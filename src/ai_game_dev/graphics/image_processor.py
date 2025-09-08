"""
Advanced Pillow-based image post-processor for AI-generated assets.

This module provides intelligent image processing capabilities including:
- Automatic transparency removal and cropping
- Frame detection and splitting for UI borders
- Size optimization and format conversion
- Integration with asset generation subgraphs
"""

import logging
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from PIL import Image, ImageFilter, ImageOps

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Advanced image processing for AI-generated game assets."""
    
    def __init__(self, quality: int = 95, optimize: bool = True):
        """
        Initialize image processor.
        
        Args:
            quality: JPEG quality for compressed outputs (1-95)
            optimize: Whether to optimize file sizes
        """
        self.quality = quality
        self.optimize = optimize
        
    def remove_excess_transparency(self, image: Image.Image, padding: int = 5) -> Image.Image:
        """
        Remove excess transparent areas from image while preserving content.
        
        Args:
            image: PIL Image with alpha channel
            padding: Pixels of padding to maintain around content
            
        Returns:
            Cropped image with minimal transparent areas
        """
        if not image.mode in ('RGBA', 'LA'):
            logger.warning("Image has no alpha channel, returning original")
            return image
            
        # Get bounding box of non-transparent content
        bbox = image.getbbox()
        if not bbox:
            logger.warning("Image is completely transparent")
            return image
            
        # Add padding while staying within image bounds
        x1, y1, x2, y2 = bbox
        x1 = max(0, x1 - padding)
        y1 = max(0, y1 - padding)
        x2 = min(image.width, x2 + padding)
        y2 = min(image.height, y2 + padding)
        
        # Crop to content + padding
        cropped = image.crop((x1, y1, x2, y2))
        
        logger.info(f"Removed excess transparency: {image.size} -> {cropped.size}")
        return cropped
        
    def detect_frame_pattern(self, image: Image.Image, threshold: float = 0.1) -> Dict[str, Any]:
        """
        Detect if image is a frame with transparent center and content on edges.
        
        Args:
            image: PIL Image to analyze
            threshold: Transparency threshold (0-1) for center detection
            
        Returns:
            Dict with frame detection results and metadata
        """
            
        if not NUMPY_AVAILABLE:
            # Simple fallback without numpy for RGB frames
            if image.mode == 'RGB':
                # Quick heuristic: check if corners have content but center is dark/empty
                width, height = image.size
                corner_brightness = []
                center_x, center_y = width // 2, height // 2
                
                # Sample corner pixels
                corners = [(50, 50), (width-50, 50), (50, height-50), (width-50, height-50)]
                for x, y in corners:
                    r, g, b = image.getpixel((x, y))
                    brightness = (r + g + b) / 3
                    corner_brightness.append(brightness)
                
                # Sample center pixels  
                center_pixels = [(center_x, center_y), (center_x-20, center_y), (center_x+20, center_y)]
                center_brightness = []
                for x, y in center_pixels:
                    r, g, b = image.getpixel((x, y))
                    brightness = (r + g + b) / 3
                    center_brightness.append(brightness)
                
                avg_corner = sum(corner_brightness) / len(corner_brightness)
                avg_center = sum(center_brightness) / len(center_brightness)
                
                # Detect both types: dark borders with light center OR light borders with dark center
                is_dark_border_frame = avg_corner < 50 and avg_center > 150 and (avg_center - avg_corner) > 100
                is_light_border_frame = avg_corner > 150 and avg_center < 50 and (avg_corner - avg_center) > 100
                is_frame = is_dark_border_frame or is_light_border_frame
                
                frame_type = "dark_border" if is_dark_border_frame else "light_border" if is_light_border_frame else "none"
                
                return {
                    "is_frame": is_frame, 
                    "reason": "Fallback detection without numpy",
                    "border_size": min(width, height) // 8,  # Default border size
                    "frame_type": frame_type,
                    "edge_opacities": {"fallback": "simple detection"},
                    "center_opacity": avg_center / 255,
                    "center_bounds": (width//4, height//4, 3*width//4, 3*height//4),
                    "analysis": f"Corner: {avg_corner:.1f}, Center: {avg_center:.1f}, Type: {frame_type}"
                }
            else:
                return {"is_frame": False, "reason": "NumPy not available for advanced frame detection"}
            
        # Handle both RGBA and RGB images
        if image.mode not in ('RGBA', 'LA', 'RGB'):
            return {"is_frame": False, "reason": "Unsupported image mode"}
            
        width, height = image.size
        
        if image.mode in ('RGBA', 'LA'):
            # For images with alpha channel
            analysis_channel = np.array(image.getchannel('A'))
        else:
            # For RGB images, convert to grayscale and look for solid backgrounds
            gray = image.convert('L')
            analysis_channel = np.array(gray)
            # Invert logic - dark areas (like black backgrounds) should be treated as "transparent"
            analysis_channel = 255 - analysis_channel
        
        # Define regions for analysis - more aggressive detection
        border_size = min(width, height) // 6  # Larger border detection
        center_margin = min(width, height) // 6  # Smaller center margin
        
        # Extract regions
        top_border = analysis_channel[:border_size, :]
        bottom_border = analysis_channel[-border_size:, :]
        left_border = analysis_channel[:, :border_size]  
        right_border = analysis_channel[:, -border_size:]
        
        center_x1 = center_margin
        center_x2 = width - center_margin
        center_y1 = center_margin  
        center_y2 = height - center_margin
        center = analysis_channel[center_y1:center_y2, center_x1:center_x2]
        
        # Calculate opacity percentages
        def calc_opacity(region):
            if region.size == 0:
                return 0
            return np.mean(region > 128) # Pixels with >50% alpha
            
        edge_opacities = {
            'top': calc_opacity(top_border),
            'bottom': calc_opacity(bottom_border), 
            'left': calc_opacity(left_border),
            'right': calc_opacity(right_border)
        }
        
        center_opacity = calc_opacity(center)
        min_edge_opacity = min(edge_opacities.values())
        
        # Frame detection logic - more sensitive
        is_frame = (
            min_edge_opacity > threshold and           # All edges have content
            center_opacity < (threshold * 3) and      # Center is mostly transparent  
            (min_edge_opacity - center_opacity) > 0.2 # Clear difference between edges and center
        )
        
        return {
            "is_frame": is_frame,
            "edge_opacities": edge_opacities,
            "center_opacity": center_opacity, 
            "border_size": border_size,
            "center_bounds": (center_x1, center_y1, center_x2, center_y2),
            "analysis": f"Edges: {min_edge_opacity:.2f}, Center: {center_opacity:.2f}, Mode: {image.mode}"
        }
        
    def split_frame_image(self, image: Image.Image, output_dir: Path) -> List[Path]:
        """
        Split frame image into corner and edge components.
        
        Args:
            image: Frame image to split
            output_dir: Directory to save split components
            
        Returns:
            List of paths to generated frame components
        """
        frame_info = self.detect_frame_pattern(image)
        if not frame_info["is_frame"]:
            logger.warning(f"Image is not detected as frame: {frame_info['analysis']}")
            return []
            
        output_dir.mkdir(parents=True, exist_ok=True)
        width, height = image.size
        border = frame_info["border_size"]
        
        # Define split regions
        regions = {
            "top-left": (0, 0, border, border),
            "top": (border, 0, width - border, border),
            "top-right": (width - border, 0, width, border),
            "left": (0, border, border, height - border),
            "center": frame_info["center_bounds"],
            "right": (width - border, border, width, height - border),
            "bottom-left": (0, height - border, border, height),
            "bottom": (border, height - border, width - border, height),
            "bottom-right": (width - border, height - border, width, height)
        }
        
        saved_files = []
        base_name = output_dir.name
        
        for region_name, (x1, y1, x2, y2) in regions.items():
            # Skip center for frames
            if region_name == "center":
                continue
                
            region_img = image.crop((x1, y1, x2, y2))
            
            # Remove excess transparency from each piece
            region_img = self.remove_excess_transparency(region_img, padding=2)
            
            # Save component
            output_path = output_dir / f"{base_name}-{region_name}.png"
            region_img.save(output_path, "PNG", optimize=self.optimize)
            saved_files.append(output_path)
            
            logger.info(f"Saved frame component: {output_path}")
            
        return saved_files
        
    def optimize_image(self, image: Image.Image, target_format: str = "PNG") -> Image.Image:
        """
        Optimize image for size and quality.
        
        Args:
            image: Image to optimize
            target_format: Target format (PNG, JPEG, WEBP)
            
        Returns:
            Optimized image
        """
        # Convert to RGB if saving as JPEG
        if target_format.upper() == "JPEG" and image.mode in ('RGBA', 'LA'):
            # Create white background for JPEG
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'RGBA':
                background.paste(image, mask=image.split()[-1])
            else:
                background.paste(image)
            image = background
            
        return image
        
    def process_asset(self, input_path: Path, output_path: Optional[Path] = None, 
                     remove_transparency: bool = True, detect_frames: bool = True) -> Dict[str, Any]:
        """
        Complete asset processing pipeline.
        
        Args:
            input_path: Path to input image
            output_path: Path for processed output (optional)
            remove_transparency: Whether to remove excess transparency
            detect_frames: Whether to detect and split frames
            
        Returns:
            Processing results and metadata
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input image not found: {input_path}")
            
        image = Image.open(input_path)
        original_size = image.size
        results = {
            "input_path": input_path,
            "original_size": original_size,
            "processed_files": []
        }
        
        # ALWAYS remove excess transparency first if present
        if image.mode in ('RGBA', 'LA'):
            original_image = image.copy()
            image = self.remove_excess_transparency(image)
            results["transparency_removed"] = True
            results["processed_size"] = image.size
            logger.info(f"Removed excess transparency: {original_size} -> {image.size}")
        else:
            original_image = image.copy()
        
        # AUTOMATIC frame detection and splitting (ALWAYS check for frames)
        frame_info = self.detect_frame_pattern(original_image)
        results["frame_analysis"] = frame_info
        
        if frame_info["is_frame"]:
            # This is a frame - automatically split the ORIGINAL into components
            split_dir = input_path.parent / f"{input_path.stem}_components"
            split_files = self.split_frame_image(original_image if 'original_image' in locals() else image, split_dir)
            results["split_files"] = split_files
            results["processing_type"] = "frame_split_and_transparency"
            logger.info(f"Detected frame - split into {len(split_files)} components")
        else:
            results["processing_type"] = "transparency_removal" if results.get("transparency_removed") else "no_processing_needed"
            
        # Save processed image
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image = self.optimize_image(image)
            image.save(output_path, optimize=self.optimize)
            results["output_path"] = output_path
            results["processed_files"].append(output_path)
            
        logger.info(f"Asset processing complete: {results}")
        return results


def process_image_cli(input_path: str, output_path: Optional[str] = None) -> None:
    """CLI wrapper for image processing."""
    processor = ImageProcessor()
    input_p = Path(input_path)
    output_p = Path(output_path) if output_path else None
    
    results = processor.process_asset(input_p, output_p)
    
    print(f"✅ Processing complete!")
    print(f"Original size: {results['original_size']}")
    print(f"Processing type: {results.get('processing_type', 'unknown')}")
    
    if 'processed_size' in results:
        print(f"Processed size: {results['processed_size']}")
    if 'split_files' in results:
        print(f"Frame components: {len(results['split_files'])}")
        for component in results['split_files']:
            print(f"  - {component}")
    if results.get('processed_files'):
        print(f"Output files: {results['processed_files']}")


def main():
    """Main entry point for command-line usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: ai-game-dev-process-image INPUT_PATH [OUTPUT_PATH]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_image_cli(input_path, output_path)


if __name__ == "__main__":
    main()