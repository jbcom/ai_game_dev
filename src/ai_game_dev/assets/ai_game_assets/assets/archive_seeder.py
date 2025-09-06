"""
Internet Archive seeding for CC0 assets with PyTorch embeddings.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Optional, Any
import json
import hashlib

try:
    import torch
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class ArchiveSeeder:
    """Seed and retrieve assets from Internet Archive with semantic search."""
    
    def __init__(self):
        self.base_url = "https://archive.org"
        self.search_url = f"{self.base_url}/advancedsearch.php"
        self.session = None
        self.embedding_cache = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_cc0_collections(
        self,
        query: str,
        media_type: str = "image",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search Internet Archive for CC0 collections."""
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        # Build search parameters for Internet Archive
        params = {
            "q": f"{query} AND licenseurl:*creativecommons.org/publicdomain/zero*",
            "fl": "identifier,title,description,downloads,item_size,publicdate",
            "rows": limit,
            "output": "json",
            "mediatype": media_type
        }
        
        try:
            async with self.session.get(self.search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", {}).get("docs", [])
                else:
                    return []
        except Exception as e:
            print(f"Error searching Internet Archive: {e}")
            return []
    
    def generate_text_embedding(self, text: str) -> Optional[torch.Tensor]:
        """Generate semantic embedding for text using simple word vectors."""
        
        if not TORCH_AVAILABLE:
            return None
        
        # Simple word embedding simulation (in real implementation, use proper embeddings)
        words = text.lower().split()
        
        # Create a simple hash-based embedding
        embedding_dim = 384
        embedding = torch.zeros(embedding_dim)
        
        for word in words:
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            word_embedding = torch.randn(embedding_dim, generator=torch.Generator().manual_seed(word_hash % (2**32)))
            embedding += word_embedding
        
        if len(words) > 0:
            embedding /= len(words)
        
        return F.normalize(embedding.unsqueeze(0), p=2, dim=1).squeeze(0)
    
    async def semantic_search_assets(
        self,
        query: str,
        asset_database: List[Dict[str, Any]],
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on asset database using embeddings."""
        
        if not TORCH_AVAILABLE:
            # Fallback to keyword search
            return [asset for asset in asset_database 
                   if query.lower() in asset.get("title", "").lower() 
                   or query.lower() in asset.get("description", "").lower()]
        
        query_embedding = self.generate_text_embedding(query)
        if query_embedding is None:
            return []
        
        results = []
        
        for asset in asset_database:
            # Create text representation of asset
            asset_text = f"{asset.get('title', '')} {asset.get('description', '')}"
            asset_embedding = self.generate_text_embedding(asset_text)
            
            if asset_embedding is not None:
                # Calculate cosine similarity
                similarity = F.cosine_similarity(
                    query_embedding.unsqueeze(0),
                    asset_embedding.unsqueeze(0)
                ).item()
                
                if similarity >= similarity_threshold:
                    asset_copy = asset.copy()
                    asset_copy["similarity_score"] = similarity
                    results.append(asset_copy)
        
        # Sort by similarity score
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results
    
    async def seed_game_asset_collection(
        self,
        game_description: str,
        output_dir: Path = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Seed a collection of game assets from Internet Archive."""
        
        if output_dir is None:
            output_dir = Path("seeded_assets")
        output_dir.mkdir(exist_ok=True)
        
        # Search for different types of game assets
        search_queries = [
            f"{game_description} sprites",
            f"{game_description} textures",
            f"{game_description} sounds",
            "game assets",
            "pixel art",
            "8bit graphics"
        ]
        
        all_collections = []
        
        for query in search_queries:
            collections = await self.search_cc0_collections(query, limit=10)
            all_collections.extend(collections)
        
        # Remove duplicates based on identifier
        unique_collections = {}
        for collection in all_collections:
            identifier = collection.get("identifier")
            if identifier and identifier not in unique_collections:
                unique_collections[identifier] = collection
        
        # Perform semantic search to find most relevant
        relevant_collections = await self.semantic_search_assets(
            game_description,
            list(unique_collections.values()),
            similarity_threshold=0.5
        )
        
        # Categorize collections
        categorized_assets = {
            "graphics": [],
            "audio": [],
            "mixed": [],
            "other": []
        }
        
        for collection in relevant_collections[:20]:  # Limit to top 20
            title = collection.get("title", "").lower()
            description = collection.get("description", "").lower()
            
            if any(word in title or word in description 
                   for word in ["sprite", "graphics", "image", "pixel", "art"]):
                categorized_assets["graphics"].append(collection)
            elif any(word in title or word in description 
                     for word in ["sound", "audio", "music", "sfx"]):
                categorized_assets["audio"].append(collection)
            elif any(word in title or word in description 
                     for word in ["game", "asset", "pack"]):
                categorized_assets["mixed"].append(collection)
            else:
                categorized_assets["other"].append(collection)
        
        # Save metadata for each category
        for category, collections in categorized_assets.items():
            if collections:
                category_dir = output_dir / category
                category_dir.mkdir(exist_ok=True)
                
                metadata_file = category_dir / "collections_metadata.json"
                with open(metadata_file, 'w') as f:
                    json.dump(collections, f, indent=2)
        
        return categorized_assets
    
    async def download_collection_metadata(
        self,
        identifier: str,
        output_dir: Path = None
    ) -> Optional[Dict[str, Any]]:
        """Download metadata for a specific Internet Archive collection."""
        
        if output_dir is None:
            output_dir = Path("collection_metadata")
        output_dir.mkdir(exist_ok=True)
        
        metadata_url = f"{self.base_url}/metadata/{identifier}"
        
        if not self.session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
        
        try:
            async with self.session.get(metadata_url) as response:
                if response.status == 200:
                    metadata = await response.json()
                    
                    # Save metadata to file
                    metadata_file = output_dir / f"{identifier}_metadata.json"
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    return metadata
                else:
                    return None
        except Exception as e:
            print(f"Error downloading metadata for {identifier}: {e}")
            return None
    
    def analyze_collection_suitability(
        self,
        collection_metadata: Dict[str, Any],
        game_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze how suitable a collection is for game requirements."""
        
        title = collection_metadata.get("metadata", {}).get("title", [""])[0]
        description = collection_metadata.get("metadata", {}).get("description", [""])[0]
        
        # Analyze file types in collection
        files = collection_metadata.get("files", [])
        file_types = {}
        total_size = 0
        
        for file_info in files:
            format_type = file_info.get("format", "unknown")
            size = int(file_info.get("size", 0))
            
            if format_type not in file_types:
                file_types[format_type] = {"count": 0, "total_size": 0}
            
            file_types[format_type]["count"] += 1
            file_types[format_type]["total_size"] += size
            total_size += size
        
        # Calculate suitability score based on requirements
        suitability_score = 0.0
        
        # Check for required file formats
        required_formats = game_requirements.get("file_formats", [])
        for req_format in required_formats:
            if any(req_format.lower() in fmt.lower() for fmt in file_types.keys()):
                suitability_score += 0.3
        
        # Check for relevant keywords
        required_keywords = game_requirements.get("keywords", [])
        text_content = f"{title} {description}".lower()
        
        for keyword in required_keywords:
            if keyword.lower() in text_content:
                suitability_score += 0.2
        
        # Bonus for CC0 license
        license_info = collection_metadata.get("metadata", {}).get("licenseurl", [""])
        if any("creativecommons.org/publicdomain/zero" in url for url in license_info):
            suitability_score += 0.5
        
        return {
            "suitability_score": min(suitability_score, 1.0),
            "file_types": file_types,
            "total_size_mb": total_size / (1024 * 1024),
            "estimated_download_time": self._estimate_download_time(total_size),
            "license_compatible": any("creativecommons.org/publicdomain/zero" in url 
                                    for url in license_info),
            "recommended": suitability_score >= 0.6
        }
    
    def _estimate_download_time(self, size_bytes: int) -> str:
        """Estimate download time for a given file size."""
        
        # Assume 10 Mbps average connection
        mbps = 10
        bytes_per_second = (mbps * 1_000_000) / 8
        
        estimated_seconds = size_bytes / bytes_per_second
        
        if estimated_seconds < 60:
            return f"{int(estimated_seconds)} seconds"
        elif estimated_seconds < 3600:
            return f"{int(estimated_seconds / 60)} minutes"
        else:
            return f"{int(estimated_seconds / 3600)} hours"
    
    async def create_curated_asset_seed(
        self,
        game_description: str,
        max_collections: int = 10,
        max_size_mb: int = 500
    ) -> Dict[str, Any]:
        """Create a curated seed of assets for a specific game."""
        
        # Search and analyze collections
        all_collections = await self.seed_game_asset_collection(game_description)
        
        # Define game requirements based on description
        game_requirements = self._analyze_game_requirements(game_description)
        
        curated_seed = {
            "game_description": game_description,
            "requirements": game_requirements,
            "collections": [],
            "total_estimated_size_mb": 0,
            "recommended_download_order": []
        }
        
        # Analyze each collection for suitability
        all_collection_items = []
        for category, collections in all_collections.items():
            for collection in collections:
                collection["category"] = category
                all_collection_items.append(collection)
        
        # Sort by relevance and download top collections' metadata
        for collection in all_collection_items[:max_collections]:
            identifier = collection.get("identifier")
            if identifier:
                metadata = await self.download_collection_metadata(identifier)
                if metadata:
                    suitability = self.analyze_collection_suitability(metadata, game_requirements)
                    
                    if suitability["recommended"] and suitability["total_size_mb"] <= max_size_mb:
                        collection_info = {
                            "identifier": identifier,
                            "title": collection.get("title"),
                            "category": collection.get("category"),
                            "suitability": suitability,
                            "download_url": f"{self.base_url}/download/{identifier}"
                        }
                        
                        curated_seed["collections"].append(collection_info)
                        curated_seed["total_estimated_size_mb"] += suitability["total_size_mb"]
        
        # Create recommended download order (smallest first)
        curated_seed["collections"].sort(
            key=lambda x: x["suitability"]["total_size_mb"]
        )
        
        curated_seed["recommended_download_order"] = [
            collection["identifier"] for collection in curated_seed["collections"]
        ]
        
        return curated_seed
    
    def _analyze_game_requirements(self, game_description: str) -> Dict[str, Any]:
        """Analyze game description to determine asset requirements."""
        
        desc_lower = game_description.lower()
        
        # Determine required file formats
        file_formats = ["png", "jpg"]  # Default image formats
        
        if any(word in desc_lower for word in ["audio", "sound", "music"]):
            file_formats.extend(["wav", "mp3", "ogg"])
        
        if any(word in desc_lower for word in ["3d", "model", "mesh"]):
            file_formats.extend(["obj", "gltf", "fbx"])
        
        # Determine keywords based on game type
        keywords = []
        
        if any(word in desc_lower for word in ["fantasy", "magic", "medieval"]):
            keywords.extend(["fantasy", "medieval", "magic", "sword", "castle"])
        
        if any(word in desc_lower for word in ["sci-fi", "space", "future"]):
            keywords.extend(["sci-fi", "space", "robot", "alien", "laser"])
        
        if any(word in desc_lower for word in ["platformer", "2d", "pixel"]):
            keywords.extend(["platformer", "2d", "pixel", "sprite", "tile"])
        
        return {
            "file_formats": file_formats,
            "keywords": keywords,
            "estimated_asset_count": self._estimate_asset_needs(desc_lower),
            "priority_categories": self._determine_priority_categories(desc_lower)
        }
    
    def _estimate_asset_needs(self, description: str) -> Dict[str, int]:
        """Estimate how many assets of each type are needed."""
        
        base_needs = {"sprites": 5, "backgrounds": 3, "ui": 10, "audio": 8}
        
        # Adjust based on game complexity indicators
        if any(word in description for word in ["complex", "large", "many"]):
            base_needs = {k: v * 2 for k, v in base_needs.items()}
        elif any(word in description for word in ["simple", "small", "minimal"]):
            base_needs = {k: max(1, v // 2) for k, v in base_needs.items()}
        
        return base_needs
    
    def _determine_priority_categories(self, description: str) -> List[str]:
        """Determine which asset categories are highest priority."""
        
        priorities = []
        
        if any(word in description for word in ["character", "player", "sprite"]):
            priorities.append("sprites")
        
        if any(word in description for word in ["environment", "world", "background"]):
            priorities.append("backgrounds")
        
        if any(word in description for word in ["ui", "interface", "menu"]):
            priorities.append("ui")
        
        if any(word in description for word in ["sound", "music", "audio"]):
            priorities.append("audio")
        
        return priorities or ["sprites", "ui"]  # Default priorities