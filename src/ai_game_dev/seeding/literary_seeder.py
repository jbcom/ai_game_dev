"""
Literary and Narrative Seeding System
Integrates with Internet Archive and uses PyTorch embeddings for semantic enhancement
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

try:
    import torch
    import torch.nn.functional as F
    from sentence_transformers import SentenceTransformer
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False


@dataclass
class SeededContent:
    """Container for seeded narrative content."""
    source: str
    content_type: str
    text_content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding_vector: Optional[List[float]] = None
    relevance_score: float = 0.0


@dataclass 
class SeedingRequest:
    """Request for narrative seeding."""
    themes: List[str]
    genres: List[str]
    character_types: List[str]
    settings: List[str]
    tone: str = "neutral"
    target_length: int = 1000
    max_sources: int = 5


class LiterarySeeder:
    """
    Seeding system that gathers narrative elements from literary sources.
    
    Capabilities:
    - Internet Archive integration for public domain literature
    - PyTorch embedding generation for semantic similarity
    - Thematic filtering and relevance scoring
    - Grammar and style analysis
    - Cross-genre inspiration gathering
    """
    
    def __init__(self):
        self.embedding_model = None
        self.cache_dir = Path("seeding_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        if PYTORCH_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                self.embedding_model = None
                
    async def seed_from_request(self, request: SeedingRequest) -> Dict[str, Any]:
        """Generate seeded content based on request parameters."""
        
        seeded_content = []
        
        # Gather content from multiple sources
        internet_archive_content = await self._gather_from_internet_archive(request)
        seeded_content.extend(internet_archive_content)
        
        # Generate embeddings and calculate relevance
        if self.embedding_model and seeded_content:
            await self._generate_embeddings(seeded_content, request)
            
        # Filter and rank by relevance
        relevant_content = self._filter_by_relevance(seeded_content, request.max_sources)
        
        # Compile final seeding data
        return {
            "seeded_content": [content.__dict__ for content in relevant_content],
            "themes_found": list(set().union(*[self._extract_themes(c.text_content) for c in relevant_content])),
            "narrative_patterns": self._analyze_narrative_patterns(relevant_content),
            "character_inspirations": self._extract_character_concepts(relevant_content),
            "setting_inspirations": self._extract_setting_concepts(relevant_content),
            "style_analysis": self._analyze_literary_style(relevant_content),
            "embedding_summary": self._summarize_embeddings(relevant_content) if PYTORCH_AVAILABLE else None
        }
        
    async def _gather_from_internet_archive(self, request: SeedingRequest) -> List[SeededContent]:
        """Gather content from Internet Archive."""
        
        content_list = []
        
        # Simulate Internet Archive API calls (would be real in production)
        archive_sources = [
            {
                "title": "Classic Literature Collection",
                "genre": "fantasy",
                "content": "In a hole in the ground there lived a hobbit. Not a nasty, dirty, wet hole, filled with the ends of worms and an oozy smell, nor yet a dry, bare, sandy hole with nothing in it to sit down on or to eat: it was a hobbit-hole, and that means comfort.",
                "metadata": {"author": "Sample Author", "year": "1937", "genre": "fantasy"}
            },
            {
                "title": "Science Fiction Anthology",
                "genre": "sci-fi", 
                "content": "The stars wheeled overhead in their ancient dance, but humanity had learned to dance among them. Cities of light spanned the void between worlds, and consciousness itself had become the ultimate frontier.",
                "metadata": {"author": "Sample Sci-Fi Author", "year": "1950", "genre": "science fiction"}
            },
            {
                "title": "Historical Adventures",
                "genre": "adventure",
                "content": "The castle stood silhouetted against the storm-dark sky, its towers reaching like grasping fingers toward the roiling clouds. Within its walls, secrets as old as the stones themselves waited to be uncovered.",
                "metadata": {"author": "Sample Adventure Author", "year": "1920", "genre": "historical adventure"}
            }
        ]
        
        # Filter sources based on request themes and genres
        for source in archive_sources:
            if any(genre.lower() in source["genre"].lower() for genre in request.genres):
                content = SeededContent(
                    source="Internet Archive",
                    content_type="literary_excerpt",
                    text_content=source["content"],
                    metadata=source["metadata"]
                )
                content_list.append(content)
                
        return content_list
        
    async def _generate_embeddings(self, content_list: List[SeededContent], request: SeedingRequest):
        """Generate PyTorch embeddings for semantic analysis."""
        
        if not self.embedding_model:
            return
            
        # Create query embedding from request
        query_text = f"{' '.join(request.themes)} {' '.join(request.genres)} {request.tone}"
        query_embedding = self.embedding_model.encode(query_text)
        
        # Generate embeddings for each content piece
        for content in content_list:
            try:
                content_embedding = self.embedding_model.encode(content.text_content)
                content.embedding_vector = content_embedding.tolist()
                
                # Calculate semantic similarity
                similarity = F.cosine_similarity(
                    torch.tensor(query_embedding).unsqueeze(0),
                    torch.tensor(content_embedding).unsqueeze(0)
                ).item()
                
                content.relevance_score = similarity
                
            except Exception as e:
                content.relevance_score = 0.5  # Default relevance
                
    def _filter_by_relevance(self, content_list: List[SeededContent], max_sources: int) -> List[SeededContent]:
        """Filter and rank content by relevance score."""
        
        # Sort by relevance score (highest first)
        sorted_content = sorted(content_list, key=lambda x: x.relevance_score, reverse=True)
        
        # Return top N most relevant sources
        return sorted_content[:max_sources]
        
    def _extract_themes(self, text: str) -> List[str]:
        """Extract thematic elements from text."""
        
        # Simple thematic analysis (would be more sophisticated in production)
        themes = []
        
        theme_keywords = {
            "heroism": ["hero", "brave", "courage", "noble", "champion"],
            "mystery": ["secret", "hidden", "unknown", "mysterious", "enigma"],
            "adventure": ["journey", "quest", "travel", "explore", "discover"],
            "conflict": ["battle", "war", "fight", "struggle", "conflict"],
            "magic": ["magic", "spell", "wizard", "enchant", "mystical"],
            "technology": ["machine", "device", "invention", "future", "advanced"]
        }
        
        text_lower = text.lower()
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
                
        return themes
        
    def _analyze_narrative_patterns(self, content_list: List[SeededContent]) -> Dict[str, Any]:
        """Analyze narrative patterns across seeded content."""
        
        patterns = {
            "common_structures": [],
            "recurring_motifs": [],
            "character_archetypes": [],
            "setting_patterns": []
        }
        
        # Analyze patterns across all content
        all_text = " ".join([content.text_content for content in content_list])
        
        # Simple pattern detection (would be more sophisticated)
        if "castle" in all_text.lower():
            patterns["setting_patterns"].append("medieval/fantasy settings")
        if "stars" in all_text.lower() or "space" in all_text.lower():
            patterns["setting_patterns"].append("cosmic/space settings")
        if "hole" in all_text.lower() and "ground" in all_text.lower():
            patterns["setting_patterns"].append("underground/hidden locations")
            
        return patterns
        
    def _extract_character_concepts(self, content_list: List[SeededContent]) -> List[Dict[str, str]]:
        """Extract character concept inspirations."""
        
        characters = []
        
        for content in content_list:
            text = content.text_content.lower()
            
            # Simple character archetype detection
            if "hobbit" in text:
                characters.append({
                    "archetype": "unlikely_hero",
                    "description": "Small, comfort-loving being thrust into adventure",
                    "source": content.source
                })
            if "wizard" in text or "magic" in text:
                characters.append({
                    "archetype": "wise_mentor",
                    "description": "Magical guide with ancient knowledge",
                    "source": content.source
                })
                
        return characters
        
    def _extract_setting_concepts(self, content_list: List[SeededContent]) -> List[Dict[str, str]]:
        """Extract setting concept inspirations."""
        
        settings = []
        
        for content in content_list:
            text = content.text_content.lower()
            
            # Setting analysis
            if "castle" in text:
                settings.append({
                    "type": "fortress",
                    "description": "Ancient stronghold with hidden secrets",
                    "mood": "mysterious_foreboding",
                    "source": content.source
                })
            if "stars" in text or "space" in text:
                settings.append({
                    "type": "cosmic",
                    "description": "Vast space with cities of light",
                    "mood": "wonder_exploration",
                    "source": content.source
                })
                
        return settings
        
    def _analyze_literary_style(self, content_list: List[SeededContent]) -> Dict[str, Any]:
        """Analyze literary style and language patterns."""
        
        style_analysis = {
            "tone_indicators": [],
            "language_complexity": "medium",
            "narrative_voice": "third_person",
            "descriptive_density": "moderate"
        }
        
        all_text = " ".join([content.text_content for content in content_list])
        
        # Simple style analysis
        if "dark" in all_text.lower() or "storm" in all_text.lower():
            style_analysis["tone_indicators"].append("atmospheric_dark")
        if "comfort" in all_text.lower() or "light" in all_text.lower():
            style_analysis["tone_indicators"].append("warm_inviting")
            
        return style_analysis
        
    def _summarize_embeddings(self, content_list: List[SeededContent]) -> Dict[str, Any]:
        """Summarize embedding analysis results."""
        
        if not content_list or not content_list[0].embedding_vector:
            return {"status": "no_embeddings"}
            
        return {
            "total_sources": len(content_list),
            "average_relevance": sum(c.relevance_score for c in content_list) / len(content_list),
            "highest_relevance": max(c.relevance_score for c in content_list),
            "embedding_dimensions": len(content_list[0].embedding_vector) if content_list[0].embedding_vector else 0,
            "pytorch_available": PYTORCH_AVAILABLE
        }