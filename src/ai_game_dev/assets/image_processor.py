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

import numpy as np

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
        
    def detect_frame_pattern(self, image: Image.Image, threshold: float = 0.3) -> Dict[str, Any]:
        """
        Detect if image is a frame with transparent center and content on edges.
        
        Args:
            image: PIL Image to analyze
            threshold: Transparency threshold (0-1) for center detection
            
        Returns:
            Dict with frame detection results and metadata
        """
            
        if not image.mode in ('RGBA', 'LA'):
            return {"is_frame": False, "reason": "No alpha channel"}
            
        width, height = image.size
        alpha = np.array(image.getchannel('A'))
        
        # Define regions for analysis
        border_size = min(width, height) // 8  # Dynamic border based on image size
        center_margin = min(width, height) // 4
        
        # Extract regions
        top_border = alpha[:border_size, :]
        bottom_border = alpha[-border_size:, :]
        left_border = alpha[:, :border_size]  
        right_border = alpha[:, -border_size:]
        
        center_x1 = center_margin
        center_x2 = width - center_margin
        center_y1 = center_margin  
        center_y2 = height - center_margin
        center = alpha[center_y1:center_y2, center_x1:center_x2]
        
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
        
        # Frame detection logic
        is_frame = (
            min_edge_opacity > threshold and  # All edges have content
            center_opacity < threshold        # Center is mostly transparent
        )
        
        return {
            "is_frame": is_frame,
            "edge_opacities": edge_opacities,
            "center_opacity": center_opacity, 
            "border_size": border_size,
            "center_bounds": (center_x1, center_y1, center_x2, center_y2),
            "analysis": f"Edges: {min_edge_opacity:.2f}, Center: {center_opacity:.2f}"
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
        
        # Frame detection and splitting
        if detect_frames:
            frame_info = self.detect_frame_pattern(image)
            results["frame_analysis"] = frame_info
            
            if frame_info["is_frame"]:
                split_dir = input_path.parent / f"{input_path.stem}_components"
                split_files = self.split_frame_image(image, split_dir)
                results["split_files"] = split_files
                logger.info(f"Split frame into {len(split_files)} components")
        
        # Standard processing
        if remove_transparency and image.mode in ('RGBA', 'LA'):
            image = self.remove_excess_transparency(image)
            results["transparency_removed"] = True
            results["processed_size"] = image.size
            
        # Save processed image
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            image = self.optimize_image(image)
            image.save(output_path, optimize=self.optimize)
            results["output_path"] = output_path
            results["processed_files"].append(output_path)
            
        logger.info(f"Asset processing complete: {results}")
        return results


def process_image_cli(input_path: str, output_path: Optional[str] = None, **kwargs) -> None:
    """CLI wrapper for image processing."""
    processor = ImageProcessor()
    input_p = Path(input_path)
    output_p = Path(output_path) if output_path else None
    
    results = processor.process_asset(input_p, output_p, **kwargs)
    
    print(f"✅ Processing complete!")
    print(f"Original size: {results['original_size']}")
    if 'processed_size' in results:
        print(f"Processed size: {results['processed_size']}")
    if 'split_files' in results:
        print(f"Frame components: {len(results['split_files'])}")
    if results['processed_files']:
        print(f"Output files: {results['processed_files']}")