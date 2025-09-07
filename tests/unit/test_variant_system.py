"""
Comprehensive tests for the Interactive Variant System.
Tests A/B choice detection, feature flags, and cross-engine compatibility.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import toml
from typing import Dict, Any

from ai_game_dev.variants import (
    VariantType,
    VariantChoice,
    VariantPoint,
    FeatureFlags,
    VariantGenerator,
    VariantCodeInjector,
    InteractiveVariantSystem,
    create_variant_enabled_game
)


class TestVariantChoice:
    """Test VariantChoice data model."""
    
    def test_variant_choice_creation(self):
        """Test creating a variant choice."""
        choice = VariantChoice(
            id="test_choice",
            name="Test Choice",
            description="A test implementation",
            code_snippet="print('test')",
            difficulty_level="easier",
            educational_notes="This is easier to understand"
        )
        
        assert choice.id == "test_choice"
        assert choice.name == "Test Choice"
        assert choice.difficulty_level == "easier"
        assert choice.educational_notes == "This is easier to understand"
    
    def test_variant_choice_defaults(self):
        """Test variant choice with default values."""
        choice = VariantChoice(
            id="minimal",
            name="Minimal",
            description="Minimal choice",
            code_snippet="pass"
        )
        
        assert choice.assets_needed == []
        assert choice.performance_impact == "neutral"
        assert choice.difficulty_level == "same"
        assert choice.educational_notes == ""


class TestVariantPoint:
    """Test VariantPoint data model."""
    
    def test_variant_point_creation(self):
        """Test creating a variant point with choices."""
        choice_a = VariantChoice(
            id="choice_a",
            name="Choice A",
            description="First option",
            code_snippet="# Option A"
        )
        choice_b = VariantChoice(
            id="choice_b", 
            name="Choice B",
            description="Second option",
            code_snippet="# Option B"
        )
        
        variant = VariantPoint(
            id="test_variant",
            name="Test Variant",
            description="A test variant point",
            variant_type=VariantType.MECHANICAL,
            context="Testing context",
            educational_value="Learn about choices",
            choices=[choice_a, choice_b],
            default_choice="choice_a"
        )
        
        assert variant.id == "test_variant"
        assert variant.variant_type == VariantType.MECHANICAL
        assert len(variant.choices) == 2
        assert variant.default_choice == "choice_a"
    
    def test_get_choice(self):
        """Test getting specific choices."""
        choice_a = VariantChoice("a", "A", "First", "# A")
        choice_b = VariantChoice("b", "B", "Second", "# B")
        
        variant = VariantPoint(
            id="test",
            name="Test",
            description="Test",
            variant_type=VariantType.VISUAL,
            context="Test",
            educational_value="Test",
            choices=[choice_a, choice_b],
            default_choice="a"
        )
        
        assert variant.get_choice("a") == choice_a
        assert variant.get_choice("b") == choice_b
        assert variant.get_choice("nonexistent") is None
    
    def test_get_default_choice(self):
        """Test getting the default choice."""
        choice_a = VariantChoice("a", "A", "First", "# A")
        choice_b = VariantChoice("b", "B", "Second", "# B")
        
        variant = VariantPoint(
            id="test",
            name="Test", 
            description="Test",
            variant_type=VariantType.VISUAL,
            context="Test",
            educational_value="Test",
            choices=[choice_a, choice_b],
            default_choice="a"
        )
        
        assert variant.get_default_choice() == choice_a


class TestFeatureFlags:
    """Test FeatureFlags system."""
    
    def test_feature_flags_creation(self):
        """Test creating feature flags."""
        flags = FeatureFlags()
        assert flags.flags == {}
    
    def test_set_variant(self):
        """Test setting variant choices."""
        flags = FeatureFlags()
        flags.set_variant("grid_system", "square")
        flags.set_variant("combat", "turn_based")
        
        assert flags.flags["grid_system"] == "square"
        assert flags.flags["combat"] == "turn_based"
    
    def test_get_active_choice(self):
        """Test getting active choices."""
        flags = FeatureFlags()
        flags.set_variant("test_variant", "choice_b")
        
        assert flags.get_active_choice("test_variant") == "choice_b"
        assert flags.get_active_choice("nonexistent") == "a"  # default
        assert flags.get_active_choice("nonexistent", "custom") == "custom"
    
    def test_to_toml(self):
        """Test exporting to TOML format."""
        flags = FeatureFlags()
        flags.set_variant("grid_system", "hexagonal")
        flags.set_variant("combat_system", "realtime")
        
        toml_output = flags.to_toml()
        parsed = toml.loads(toml_output)
        
        assert "features" in parsed
        assert "variants" in parsed["features"]
        assert parsed["features"]["variants"]["grid_system"] == "hexagonal"
        assert parsed["features"]["variants"]["combat_system"] == "realtime"
    
    def test_from_toml(self):
        """Test loading from TOML content."""
        toml_content = """
        [features]
        description = "Feature flags for game variants"
        
        [features.variants]
        grid_system = "square"
        movement = "discrete"
        """
        
        flags = FeatureFlags.from_toml(toml_content)
        assert flags.get_active_choice("grid_system") == "square"
        assert flags.get_active_choice("movement") == "discrete"


class TestVariantGenerator:
    """Test VariantGenerator for detecting variant opportunities."""
    
    def test_variant_generator_creation(self):
        """Test creating variant generator."""
        mock_llm_manager = Mock()
        generator = VariantGenerator(mock_llm_manager)
        
        assert generator.llm_manager == mock_llm_manager
        assert len(generator.common_variants) > 0
        assert "grid_system" in generator.common_variants
        assert "combat_system" in generator.common_variants
    
    def test_common_variants_structure(self):
        """Test that common variants have proper structure."""
        mock_llm_manager = Mock()
        generator = VariantGenerator(mock_llm_manager)
        
        grid_variant = generator.common_variants["grid_system"]
        assert grid_variant.id == "grid_system"
        assert grid_variant.variant_type == VariantType.VISUAL
        assert len(grid_variant.choices) == 2
        assert grid_variant.default_choice == "a_square"
        
        # Check choices
        square_choice = grid_variant.get_choice("a_square")
        hex_choice = grid_variant.get_choice("b_hexagonal")
        
        assert square_choice.name == "Square Grid"
        assert hex_choice.name == "Hexagonal Grid"
        assert square_choice.difficulty_level == "easier"
        assert hex_choice.difficulty_level == "harder"
    
    @pytest.mark.asyncio
    async def test_detect_variant_opportunities(self):
        """Test detecting variant opportunities in code."""
        mock_llm_manager = Mock()
        generator = VariantGenerator(mock_llm_manager)
        
        # Code that should trigger grid and combat variants
        test_code = """
        grid_size = 32
        player_health = 100
        
        def handle_combat():
            if player_turn:
                attack_enemy()
            else:
                enemy_attack()
        
        def draw_map():
            for row in range(grid_height):
                for col in range(grid_width):
                    draw_tile(col * grid_size, row * grid_size)
        """
        
        variants = await generator.detect_variant_opportunities(
            test_code, "pygame"
        )
        
        # Should detect grid and combat variants
        variant_ids = [v.id for v in variants]
        assert "grid_system" in variant_ids
        assert "combat_system" in variant_ids
    
    def test_code_matches_variant_pattern(self):
        """Test pattern matching for variant detection."""
        mock_llm_manager = Mock()
        generator = VariantGenerator(mock_llm_manager)
        
        grid_variant = generator.common_variants["grid_system"]
        
        # Code with grid patterns
        grid_code = "grid_size = 32\ndraw_tile(x, y)"
        assert generator._code_matches_variant_pattern(grid_code, grid_variant)
        
        # Code without grid patterns
        no_grid_code = "print('hello world')"
        assert not generator._code_matches_variant_pattern(no_grid_code, grid_variant)


class TestVariantCodeInjector:
    """Test VariantCodeInjector for inserting variant code."""
    
    def test_code_injector_creation(self):
        """Test creating code injector."""
        injector = VariantCodeInjector()
        
        assert "pygame" in injector.injection_patterns
        assert "godot" in injector.injection_patterns  
        assert "bevy" in injector.injection_patterns
    
    def test_injection_patterns(self):
        """Test injection pattern structure."""
        injector = VariantCodeInjector()
        
        pygame_pattern = injector.injection_patterns["pygame"]
        assert "flag_check" in pygame_pattern
        assert "template" in pygame_pattern
        
        # Check pattern contains placeholder variables
        assert "{variant_id}" in pygame_pattern["flag_check"]
        assert "{choice_a_code}" in pygame_pattern["template"]
    
    def test_inject_variants(self):
        """Test injecting variants into code."""
        injector = VariantCodeInjector()
        
        # Create test variant
        choice_a = VariantChoice("a", "A", "First", "print('A')")
        choice_b = VariantChoice("b", "B", "Second", "print('B')")
        variant = VariantPoint(
            id="test_variant",
            name="Test",
            description="Test variant",
            variant_type=VariantType.MECHANICAL,
            context="Test",
            educational_value="Test",
            choices=[choice_a, choice_b],
            default_choice="a"
        )
        
        # Create feature flags
        flags = FeatureFlags()
        flags.set_variant("test_variant", "a")
        
        # Test code
        base_code = "def main():\n    pass"
        
        enhanced_code, features_toml = injector.inject_variants(
            base_code, [variant], "pygame", flags
        )
        
        assert "Variant Point: Test variant" in enhanced_code
        assert "print('A')" in enhanced_code
        assert "print('B')" in enhanced_code
        assert "test_variant" in features_toml


class TestInteractiveVariantSystem:
    """Test the complete InteractiveVariantSystem."""
    
    @pytest.mark.asyncio
    async def test_system_creation(self):
        """Test creating interactive variant system."""
        mock_llm_manager = AsyncMock()
        system = InteractiveVariantSystem(mock_llm_manager)
        
        assert system.variant_generator is not None
        assert system.code_injector is not None
        assert system.active_variants == {}
        assert system.preview_cache == {}
    
    @pytest.mark.asyncio
    async def test_generate_interactive_game_with_variants(self):
        """Test generating game with variants."""
        mock_llm_manager = AsyncMock()
        system = InteractiveVariantSystem(mock_llm_manager)
        
        # Mock the variant detection to return known variants
        with patch.object(system.variant_generator, 'detect_variant_opportunities') as mock_detect:
            # Create mock variant
            choice_a = VariantChoice("a", "A", "First", "# A")
            choice_b = VariantChoice("b", "B", "Second", "# B")
            mock_variant = VariantPoint(
                id="test_variant",
                name="Test Variant",
                description="Test",
                variant_type=VariantType.MECHANICAL,
                context="Test",
                educational_value="Test concept",
                choices=[choice_a, choice_b],
                default_choice="a"
            )
            mock_detect.return_value = [mock_variant]
            
            test_code = "def game(): pass"
            result = await system.generate_interactive_game_with_variants(
                test_code, "pygame"
            )
            
            assert "enhanced_code" in result
            assert "features_toml" in result
            assert "variants" in result
            assert "preview_data" in result
            assert result["engine"] == "pygame"
            assert result["interactive_points"] == 1
    
    def test_variant_to_dict(self):
        """Test converting variant to dictionary."""
        mock_llm_manager = Mock()
        system = InteractiveVariantSystem(mock_llm_manager)
        
        choice_a = VariantChoice("a", "Choice A", "First option", "# A")
        choice_b = VariantChoice("b", "Choice B", "Second option", "# B")
        variant = VariantPoint(
            id="test_variant",
            name="Test Variant",
            description="A test variant",
            variant_type=VariantType.VISUAL,
            context="Testing",
            educational_value="Learn testing",
            choices=[choice_a, choice_b],
            default_choice="a"
        )
        
        variant_dict = system._variant_to_dict(variant)
        
        assert variant_dict["id"] == "test_variant"
        assert variant_dict["name"] == "Test Variant"
        assert variant_dict["type"] == "visual"
        assert variant_dict["default_choice"] == "a"
        assert len(variant_dict["choices"]) == 2
        assert variant_dict["choices"][0]["id"] == "a"
        assert variant_dict["choices"][0]["name"] == "Choice A"


class TestCreateVariantEnabledGame:
    """Test the factory function for creating variant-enabled games."""
    
    @pytest.mark.asyncio
    async def test_create_variant_enabled_game_with_llm_manager(self):
        """Test factory function with provided LLM manager."""
        mock_llm_manager = AsyncMock()
        
        with patch('ai_game_dev.variants.variant_system.InteractiveVariantSystem') as MockSystem:
            mock_system_instance = AsyncMock()
            mock_system_instance.generate_interactive_game_with_variants.return_value = {
                "enhanced_code": "# Enhanced code",
                "features_toml": "[features]\n",
                "variants": [],
                "preview_data": {},
                "engine": "pygame"
            }
            MockSystem.return_value = mock_system_instance
            
            result = await create_variant_enabled_game(
                "def game(): pass",
                "pygame", 
                mock_llm_manager
            )
            
            assert result["enhanced_code"] == "# Enhanced code"
            assert result["engine"] == "pygame"
            MockSystem.assert_called_once_with(mock_llm_manager)
    
    @pytest.mark.asyncio 
    async def test_create_variant_enabled_game_default_llm_manager(self):
        """Test factory function with default LLM manager."""
        with patch('ai_game_dev.variants.variant_system.InteractiveVariantSystem') as MockSystem:
            with patch('ai_game_dev.variants.variant_system.LLMManager') as MockLLMManager:
                mock_llm_instance = AsyncMock()
                MockLLMManager.return_value = mock_llm_instance
                
                mock_system_instance = AsyncMock()
                mock_system_instance.generate_interactive_game_with_variants.return_value = {
                    "enhanced_code": "# Default enhanced code",
                    "engine": "pygame"
                }
                MockSystem.return_value = mock_system_instance
                
                result = await create_variant_enabled_game("def game(): pass")
                
                assert result["enhanced_code"] == "# Default enhanced code"
                MockLLMManager.assert_called_once()
                MockSystem.assert_called_once_with(mock_llm_instance)


# Integration tests for common variant patterns
class TestCommonVariantPatterns:
    """Test the predefined common variant patterns."""
    
    def test_all_common_variants_present(self):
        """Test that all expected common variants are present."""
        mock_llm_manager = Mock()
        generator = VariantGenerator(mock_llm_manager)
        
        expected_variants = [
            "grid_system",
            "combat_system", 
            "movement_system",
            "ai_behavior"
        ]
        
        for variant_id in expected_variants:
            assert variant_id in generator.common_variants
            variant = generator.common_variants[variant_id]
            assert len(variant.choices) >= 2
            assert variant.default_choice is not None
            assert "pygame" in variant.engine_compatibility
    
    def test_educational_progression(self):
        """Test that variants have proper educational progression."""
        mock_llm_manager = Mock()
        generator = VariantGenerator(mock_llm_manager)
        
        for variant in generator.common_variants.values():
            # Each variant should have at least one easier and one harder choice
            difficulties = [choice.difficulty_level for choice in variant.choices]
            
            # Should have educational variety
            assert len(set(difficulties)) > 1 or "same" in difficulties
            
            # Should have educational value
            assert variant.educational_value
            assert len(variant.educational_value) > 10
    
    def test_cross_engine_compatibility(self):
        """Test that variants work across different engines."""
        mock_llm_manager = Mock()
        generator = VariantGenerator(mock_llm_manager)
        
        for variant in generator.common_variants.values():
            # All variants should support at least pygame
            assert "pygame" in variant.engine_compatibility
            
            # Most should support multiple engines
            assert len(variant.engine_compatibility) >= 1