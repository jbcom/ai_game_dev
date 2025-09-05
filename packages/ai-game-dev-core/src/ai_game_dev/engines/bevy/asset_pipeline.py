"""Bevy asset pipeline integration."""

class BevyAssetPipeline:
    """Asset pipeline for Bevy games."""
    
    def __init__(self):
        pass
        
    def get_asset_formats(self):
        return {
            "images": ["png", "jpg", "webp"],
            "audio": ["ogg", "wav", "mp3"],
            "models": ["gltf", "glb"]
        }