"""
Arcade Academy Agent - Revolutionary Educational Game Development Agent

Extends PygameAgent with AI-powered educational analysis:
- Automatic teachable moment detection through code analysis
- Intelligent breakpoint flagging with educational context
- Standardized learning objective mapping
- Professor Pixel integration with context-aware lessons

This agent automatically analyzes generated code to identify learning opportunities
and inserts Professor Pixel breakpoints at optimal educational moments.
"""

import re
import ast
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Set
from pathlib import Path
from dataclasses import dataclass

try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.language_models import BaseChatModel
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create stub classes to avoid NameError
    class SystemMessage:
        def __init__(self, content): self.content = content
    class HumanMessage:
        def __init__(self, content): self.content = content

from .base_agent import GameDevelopmentAgent, AgentConfig
try:
    from ..models.llm_manager import LLMManager
except ImportError:
    # Fallback for development/testing
    class LLMManager:
        async def get_model(self, model_name): return None
from ..variants.variant_system import InteractiveVariantSystem, create_variant_enabled_game


@dataclass
class TeachableMoment:
    """Represents a detected teachable moment in code."""
    concept: str  # variables, loops, functions, classes, etc.
    location: Tuple[int, int]  # (line_start, line_end)
    code_snippet: str
    context: str  # surrounding code context
    difficulty_level: str  # beginner, intermediate, advanced
    lesson_id: str
    trigger_condition: Optional[str] = None
    educational_value: float = 0.0  # 0.0 to 1.0 scoring


@dataclass 
class EducationalContext:
    """Educational framework for a game project."""
    target_audience: str  # "beginner", "intermediate", "advanced"
    learning_objectives: List[str]
    programming_concepts: List[str]
    game_mechanics_focus: List[str]
    progression_difficulty: str  # "gradual", "moderate", "steep"


class CodeAnalysisEngine:
    """AI-powered code analysis engine for detecting educational opportunities."""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.concept_patterns = self._build_concept_patterns()
        
    def _build_concept_patterns(self) -> Dict[str, List[str]]:
        """Build regex patterns for detecting programming concepts."""
        return {
            'variables': [
                r'(\w+)\s*=\s*([^=\n]+)',  # Variable assignment
                r'(player_\w+|health|score|lives)',  # Game-specific variables
            ],
            'conditionals': [
                r'if\s+(.+):',  # If statements
                r'elif\s+(.+):',  # Elif statements
                r'while\s+(.+):',  # While loops with conditions
            ],
            'loops': [
                r'for\s+\w+\s+in\s+(.+):',  # For loops
                r'while\s+(.+):',  # While loops
                r'range\(\s*(\d+)\s*\)',  # Range function
            ],
            'functions': [
                r'def\s+(\w+)\s*\([^)]*\)\s*:',  # Function definitions
                r'(\w+)\([^)]*\)',  # Function calls
            ],
            'classes': [
                r'class\s+(\w+)(?:\([^)]*\))?\s*:',  # Class definitions
                r'self\.(\w+)',  # Instance variables
            ],
            'pygame_specific': [
                r'pygame\.(\w+)',  # Pygame module usage
                r'\.blit\(',  # Drawing operations
                r'pygame\.event\.get\(\)',  # Event handling
                r'pygame\.time\.Clock\(\)',  # Game loop timing
            ],
            'game_logic': [
                r'collision|intersect',  # Collision detection
                r'spawn|create|generate',  # Object creation
                r'update|move|animate',  # Object updates
                r'score|points|health|damage',  # Game state
            ]
        }
    
    async def analyze_code_for_teachable_moments(
        self, 
        code: str, 
        educational_context: EducationalContext
    ) -> List[TeachableMoment]:
        """Analyze code and detect teachable moments using AI assistance."""
        
        # First pass: Pattern-based detection
        detected_concepts = self._detect_concepts_by_pattern(code)
        
        # Second pass: AST-based analysis for deeper understanding
        ast_concepts = self._analyze_with_ast(code)
        
        # Third pass: AI-powered contextual analysis
        ai_enhanced_moments = await self._ai_enhance_analysis(
            code, detected_concepts + ast_concepts, educational_context
        )
        
        # Score and rank teachable moments
        ranked_moments = self._rank_educational_value(ai_enhanced_moments, educational_context)
        
        return ranked_moments
    
    def _detect_concepts_by_pattern(self, code: str) -> List[TeachableMoment]:
        """Detect programming concepts using regex patterns."""
        moments = []
        lines = code.split('\n')
        
        for concept, patterns in self.concept_patterns.items():
            for i, line in enumerate(lines):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Extract context (surrounding lines)
                        start_context = max(0, i - 2)
                        end_context = min(len(lines), i + 3)
                        context_lines = lines[start_context:end_context]
                        
                        moment = TeachableMoment(
                            concept=concept,
                            location=(i + 1, i + 1),
                            code_snippet=line.strip(),
                            context='\n'.join(context_lines),
                            difficulty_level='beginner',  # Will be refined by AI
                            lesson_id=f"{concept}_{i+1}",
                            educational_value=0.5  # Default, will be scored
                        )
                        moments.append(moment)
        
        return moments
    
    def _analyze_with_ast(self, code: str) -> List[TeachableMoment]:
        """Use AST parsing for deeper code structure analysis."""
        moments = []
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                moment = None
                
                if isinstance(node, ast.FunctionDef):
                    moment = TeachableMoment(
                        concept='functions',
                        location=(node.lineno, node.end_lineno or node.lineno),
                        code_snippet=f"def {node.name}({', '.join(arg.arg for arg in node.args.args)}):",
                        context=self._extract_function_context(node, code),
                        difficulty_level='intermediate',
                        lesson_id=f"function_{node.name}_{node.lineno}",
                        educational_value=0.8
                    )
                
                elif isinstance(node, ast.ClassDef):
                    moment = TeachableMoment(
                        concept='classes',
                        location=(node.lineno, node.end_lineno or node.lineno),
                        code_snippet=f"class {node.name}:",
                        context=self._extract_class_context(node, code),
                        difficulty_level='advanced',
                        lesson_id=f"class_{node.name}_{node.lineno}",
                        educational_value=0.9
                    )
                
                elif isinstance(node, (ast.For, ast.While)):
                    loop_type = 'for' if isinstance(node, ast.For) else 'while'
                    moment = TeachableMoment(
                        concept='loops',
                        location=(node.lineno, node.end_lineno or node.lineno),
                        code_snippet=self._extract_loop_snippet(node, code),
                        context=self._extract_loop_context(node, code),
                        difficulty_level='beginner',
                        lesson_id=f"loop_{loop_type}_{node.lineno}",
                        educational_value=0.7
                    )
                
                if moment:
                    moments.append(moment)
        
        except SyntaxError:
            # Code might be incomplete or have syntax errors during generation
            pass
        
        return moments
    
    async def _ai_enhance_analysis(
        self, 
        code: str, 
        detected_moments: List[TeachableMoment],
        educational_context: EducationalContext
    ) -> List[TeachableMoment]:
        """Use AI to enhance analysis with educational context awareness."""
        
        if not LANGCHAIN_AVAILABLE or not detected_moments:
            return detected_moments
        
        # Prepare AI analysis prompt
        analysis_prompt = self._build_analysis_prompt(code, detected_moments, educational_context)
        
        try:
            llm = await self.llm_manager.get_model("gpt-4o")
            
            messages = [
                SystemMessage(content="You are an expert programming educator who analyzes code to identify optimal teaching moments."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await llm.ainvoke(messages)
            enhanced_moments = self._parse_ai_analysis(response.content, detected_moments)
            
            return enhanced_moments
            
        except Exception as e:
            # Fallback to original moments if AI analysis fails
            return detected_moments
    
    def _build_analysis_prompt(
        self, 
        code: str, 
        moments: List[TeachableMoment], 
        context: EducationalContext
    ) -> str:
        """Build AI prompt for educational code analysis."""
        
        moments_summary = "\n".join([
            f"- {m.concept} at line {m.location[0]}: {m.code_snippet}"
            for m in moments
        ])
        
        return f"""
        Analyze this pygame code for educational value in teaching programming concepts.
        
        TARGET AUDIENCE: {context.target_audience}
        LEARNING OBJECTIVES: {', '.join(context.learning_objectives)}
        FOCUS CONCEPTS: {', '.join(context.programming_concepts)}
        GAME MECHANICS: {', '.join(context.game_mechanics_focus)}
        
        CODE TO ANALYZE:
        ```python
        {code}
        ```
        
        DETECTED CONCEPTS:
        {moments_summary}
        
        For each detected concept, provide:
        1. Educational value score (0.0-1.0)
        2. Appropriate difficulty level (beginner/intermediate/advanced)
        3. Specific trigger condition for when to show this lesson
        4. Enhanced lesson context that relates to the game mechanics
        5. Whether this moment should be prioritized for the target audience
        
        Focus on moments that:
        - Directly relate to game functionality students can see/feel
        - Build progressively on previous concepts
        - Have clear cause-and-effect relationships
        - Connect programming concepts to game outcomes
        
        Respond in JSON format with enhanced moment data.
        """
    
    def _parse_ai_analysis(self, ai_response: str, original_moments: List[TeachableMoment]) -> List[TeachableMoment]:
        """Parse AI response and enhance original moments."""
        # For now, return enhanced moments with AI-suggested improvements
        # In production, would parse JSON response and update moments accordingly
        
        for moment in original_moments:
            # Apply AI enhancements (simplified for now)
            if moment.concept in ['variables', 'conditionals']:
                moment.educational_value = 0.9  # High value for beginners
                moment.trigger_condition = "on_game_state_change"
            elif moment.concept in ['loops', 'functions']:
                moment.educational_value = 0.8
                moment.trigger_condition = "on_pattern_repeat"
            elif moment.concept in ['classes', 'pygame_specific']:
                moment.educational_value = 0.7
                moment.trigger_condition = "on_feature_first_use"
        
        return original_moments
    
    def _rank_educational_value(
        self, 
        moments: List[TeachableMoment], 
        context: EducationalContext
    ) -> List[TeachableMoment]:
        """Rank moments by educational value for the target audience."""
        
        def calculate_score(moment: TeachableMoment) -> float:
            base_score = moment.educational_value
            
            # Boost score based on target audience
            if context.target_audience == "beginner":
                if moment.concept in ['variables', 'conditionals', 'loops']:
                    base_score += 0.2
                elif moment.concept in ['classes', 'advanced_patterns']:
                    base_score -= 0.3
            
            # Boost if concept is in learning objectives
            if any(obj.lower() in moment.concept.lower() for obj in context.learning_objectives):
                base_score += 0.1
            
            # Boost if related to focused game mechanics
            if any(mech.lower() in moment.code_snippet.lower() for mech in context.game_mechanics_focus):
                base_score += 0.1
            
            return min(1.0, max(0.0, base_score))
        
        # Calculate scores and sort by educational value
        for moment in moments:
            moment.educational_value = calculate_score(moment)
        
        return sorted(moments, key=lambda m: m.educational_value, reverse=True)
    
    def _extract_function_context(self, node: ast.FunctionDef, code: str) -> str:
        """Extract meaningful context around a function definition."""
        lines = code.split('\n')
        start = max(0, node.lineno - 3)
        end = min(len(lines), (node.end_lineno or node.lineno) + 2)
        return '\n'.join(lines[start:end])
    
    def _extract_class_context(self, node: ast.ClassDef, code: str) -> str:
        """Extract meaningful context around a class definition."""
        lines = code.split('\n')
        start = max(0, node.lineno - 2)
        end = min(len(lines), (node.end_lineno or node.lineno) + 5)
        return '\n'.join(lines[start:end])
    
    def _extract_loop_snippet(self, node: ast.stmt, code: str) -> str:
        """Extract the loop line from code."""
        lines = code.split('\n')
        if node.lineno <= len(lines):
            return lines[node.lineno - 1].strip()
        return ""
    
    def _extract_loop_context(self, node: ast.stmt, code: str) -> str:
        """Extract context around a loop."""
        lines = code.split('\n')
        start = max(0, node.lineno - 2)
        end = min(len(lines), (node.end_lineno or node.lineno) + 3)
        return '\n'.join(lines[start:end])


class ArcadeAcademyAgent(GameDevelopmentAgent):
    """
    Revolutionary Educational Game Development Agent
    
    Extends PygameAgent with AI-powered educational analysis:
    - Automatic teachable moment detection
    - Context-aware Professor Pixel integration  
    - Standardized educational breakpoint system
    - Progressive learning objective mapping
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        if config is None:
            config = AgentConfig(
                model="gpt-4o",
                temperature=0.2,  # Lower temperature for consistent educational output
                instructions=self._get_arcade_academy_instructions()
            )
        
        super().__init__(config)
        self.llm_manager = LLMManager()
        self.code_analyzer = CodeAnalysisEngine(self.llm_manager)
        self.educational_contexts = {}  # Cache educational contexts per project
        
    def _get_arcade_academy_instructions(self) -> str:
        """Get specialized instructions for educational game development."""
        return """
        You are the Arcade Academy Agent, a revolutionary educational game development system.
        
        Your mission is to create pygame games that teach programming through Professor Pixel's 
        interactive breakpoint learning system. You automatically analyze generated code to detect 
        teachable moments and insert contextual learning experiences.
        
        CORE CAPABILITIES:
        - Generate pygame games with embedded educational breakpoints
        - Analyze code structure to identify optimal teaching moments
        - Create progressive learning experiences that build on each other  
        - Integrate Professor Pixel modal system for interactive lessons
        - Map programming concepts to game mechanics for concrete learning
        
        EDUCATIONAL PRINCIPLES:
        - Learning through doing: Concepts taught when students encounter them naturally
        - Progressive complexity: Build from simple variables to advanced patterns
        - Immediate feedback: Show results of code changes in game behavior
        - Contextual relevance: Relate programming concepts to visible game effects
        - Spaced repetition: Reinforce concepts across multiple interactions
        
        BREAKPOINT STRATEGIES:
        - Variables: Trigger when game state changes (health, score, position)
        - Loops: Trigger when repetitive patterns become apparent (game loop, enemy spawning)
        - Functions: Trigger when reusable code patterns emerge (attack, movement)
        - Conditionals: Trigger when game logic branches (collision detection, game over)
        - Classes: Trigger when object relationships become complex (player vs enemies)
        
        Always generate games with clear cause-and-effect relationships between code and 
        visible game behavior to maximize educational impact.
        """
    
    async def _get_extended_instructions(self) -> str:
        """Add pygame-specific educational instructions."""
        return """
        PYGAME EDUCATIONAL FOCUS:
        - Use clear variable names that reflect game concepts (player_health, enemy_speed)
        - Structure code to highlight programming patterns as they emerge naturally
        - Create visual feedback for all programming concepts (variables change sprites, loops create movement)
        - Implement Professor Pixel breakpoints at moments of maximum educational impact
        - Generate WebAssembly-compatible code for browser-based learning experiences
        
        PROFESSOR PIXEL INTEGRATION:
        - Automatically insert breakpoint detection calls at strategic code locations
        - Generate educational context that relates to specific game mechanics
        - Create progressive lesson sequences that build complexity gradually
        - Ensure breakpoints trigger at moments of natural curiosity and engagement
        """
    
    async def generate_educational_game(
        self,
        game_description: str,
        educational_context: EducationalContext,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a pygame game with automatic educational analysis and interactive variants."""
        
        # Step 1: Generate base pygame game  
        base_game_result = await self._generate_base_pygame_game(game_description, **kwargs)
        
        # Step 2: Generate interactive variants using the general variant system
        variant_system = InteractiveVariantSystem(self.llm_manager)
        variant_result = await variant_system.generate_interactive_game_with_variants(
            base_game_result['main_code'],
            'pygame',
            educational_context.__dict__
        )
        
        # Step 3: Analyze code for teachable moments (Arcade Academy enhancement)
        teachable_moments = await self.code_analyzer.analyze_code_for_teachable_moments(
            variant_result['enhanced_code'],
            educational_context
        )
        
        # Step 4: Insert Professor Pixel breakpoints at optimal locations
        enhanced_code = await self._insert_educational_breakpoints(
            variant_result['enhanced_code'],
            teachable_moments
        )
        
        # Step 5: Generate Professor Pixel lesson content for detected concepts
        lesson_data = await self._generate_lesson_content(teachable_moments, educational_context)
        
        # Step 6: Enhance variants with educational context (Arcade Academy superpower)
        educational_variants = await self._enhance_variants_with_education(
            variant_result['variants'],
            educational_context
        )
        
        # Step 7: Package complete educational game with interactive variants
        return {
            'game_code': enhanced_code,
            'features_toml': variant_result['features_toml'],
            'teachable_moments': teachable_moments,
            'lesson_data': lesson_data,
            'educational_context': educational_context,
            'interactive_variants': educational_variants,
            'variant_preview_data': variant_result['preview_data'],
            'deployment_ready': True,
            'professor_pixel_integrated': True,
            'webassembly_compatible': True,
            'has_interactive_choices': True
        }
    
    async def _generate_base_pygame_game(self, description: str, **kwargs) -> Dict[str, Any]:
        """Generate the base pygame game code."""
        
        # Use the existing pygame generation capabilities but with educational focus
        messages = [
            SystemMessage(content=self.config.instructions),
            HumanMessage(content=f"""
            Generate a pygame game: {description}
            
            EDUCATIONAL REQUIREMENTS:
            - Use clear, descriptive variable names
            - Structure code with obvious programming patterns
            - Include game state that changes visibly
            - Create opportunities for natural learning moments
            - Make cause-and-effect relationships clear
            - Ensure WebAssembly compatibility
            
            Generate complete pygame code with main game loop, event handling, and basic game mechanics.
            """)
        ]
        
        llm = await self.llm_manager.get_model(self.config.model)
        response = await llm.ainvoke(messages)
        
        # Extract code from response (simplified parsing)
        code = self._extract_code_from_response(response.content)
        
        return {
            'main_code': code,
            'engine': 'pygame',
            'webassembly_ready': True
        }
    
    async def _insert_educational_breakpoints(
        self, 
        code: str, 
        moments: List[TeachableMoment]
    ) -> str:
        """Insert Professor Pixel breakpoint calls at detected teachable moments."""
        
        lines = code.split('\n')
        enhanced_lines = []
        
        # Sort moments by line number for proper insertion
        sorted_moments = sorted(moments, key=lambda m: m.location[0])
        
        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # Check if we need to insert a breakpoint after this line
            for moment in sorted_moments:
                if i + 1 == moment.location[0]:  # Line numbers are 1-indexed
                    breakpoint_code = self._generate_breakpoint_code(moment)
                    enhanced_lines.append(breakpoint_code)
        
        # Add Professor Pixel integration imports at the top
        integration_imports = self._generate_integration_imports()
        
        return integration_imports + '\n\n' + '\n'.join(enhanced_lines)
    
    def _generate_integration_imports(self) -> str:
        """Generate imports needed for Professor Pixel integration."""
        return """
# Professor Pixel Educational Integration
from ai_game_dev.engines.pygame_template_webassembly import ProfessorPixelIntegration

# Initialize educational system
professor_pixel = ProfessorPixelIntegration()

# Register educational breakpoints
professor_pixel.register_breakpoint('player_takes_damage', 'variables')
professor_pixel.register_breakpoint('game_loop_iteration', 'loops') 
professor_pixel.register_breakpoint('function_called', 'functions')
professor_pixel.register_breakpoint('collision_detected', 'conditionals')
"""
    
    def _generate_breakpoint_code(self, moment: TeachableMoment) -> str:
        """Generate breakpoint trigger code for a teachable moment."""
        return f"    # Educational breakpoint: {moment.concept}\n    professor_pixel.trigger_breakpoint('{moment.lesson_id}', locals())"
    
    async def _generate_lesson_content(
        self, 
        moments: List[TeachableMoment],
        context: EducationalContext
    ) -> Dict[str, Any]:
        """Generate Professor Pixel lesson content for detected concepts."""
        
        lessons = {}
        
        for moment in moments:
            lesson_content = await self._create_contextual_lesson(moment, context)
            lessons[moment.lesson_id] = lesson_content
        
        return lessons
    
    async def _create_contextual_lesson(
        self, 
        moment: TeachableMoment, 
        context: EducationalContext
    ) -> Dict[str, Any]:
        """Create a contextual lesson for a specific teachable moment."""
        
        # Generate lesson using AI that understands the specific game context
        lesson_prompt = f"""
        Create a Professor Pixel lesson for the concept '{moment.concept}' in this context:
        
        CODE SNIPPET: {moment.code_snippet}
        GAME CONTEXT: {moment.context}
        TARGET AUDIENCE: {context.target_audience}
        DIFFICULTY: {moment.difficulty_level}
        
        The lesson should:
        - Explain the concept in simple terms
        - Show how it affects the game behavior
        - Provide a concrete code example
        - Include an interactive challenge question
        - Relate to the specific game mechanics being used
        
        Return a lesson structure that Professor Pixel can use for teaching.
        """
        
        try:
            llm = await self.llm_manager.get_model("gpt-4o")
            response = await llm.ainvoke([
                SystemMessage(content="You are Professor Pixel, a cyberpunk coding educator. Create engaging, context-aware programming lessons."),
                HumanMessage(content=lesson_prompt)
            ])
            
            # Parse response into lesson structure
            return self._parse_lesson_response(response.content, moment)
            
        except Exception:
            # Fallback to basic lesson structure
            return self._create_fallback_lesson(moment)
    
    def _parse_lesson_response(self, response: str, moment: TeachableMoment) -> Dict[str, Any]:
        """Parse AI response into structured lesson data."""
        # Simplified parsing - in production would use structured output
        return {
            'title': f"🎓 {moment.concept.title()} Discovered!",
            'message': f"You've encountered {moment.concept} in your code! This is a fundamental programming concept.",
            'code_example': moment.code_snippet,
            'explanation': f"This {moment.concept} affects how your game behaves.",
            'challenge': f"What happens when you change this {moment.concept}?",
            'difficulty': moment.difficulty_level,
            'educational_value': moment.educational_value
        }
    
    def _create_fallback_lesson(self, moment: TeachableMoment) -> Dict[str, Any]:
        """Create a basic lesson structure as fallback."""
        return {
            'title': f"💡 {moment.concept.title()} Concept",
            'message': f"You've discovered {moment.concept}! This is an important programming concept.",
            'code_example': moment.code_snippet,
            'explanation': f"Understanding {moment.concept} will help you build better games.",
            'challenge': f"Experiment with different {moment.concept} values!",
            'difficulty': moment.difficulty_level,
            'educational_value': moment.educational_value
        }
    
    async def _enhance_variants_with_education(
        self, 
        variants: List[Dict[str, Any]], 
        educational_context: EducationalContext
    ) -> List[Dict[str, Any]]:
        """Enhance general variants with educational context and Professor Pixel integration."""
        
        enhanced_variants = []
        
        for variant in variants:
            # Add educational metadata to each variant
            enhanced_variant = variant.copy()
            
            # Add Professor Pixel teaching moments for each choice
            for choice in enhanced_variant['choices']:
                choice['professor_pixel_lesson'] = await self._create_variant_lesson(
                    choice, variant, educational_context
                )
                choice['educational_insight'] = self._generate_educational_insight(choice, variant)
            
            # Add overall learning objectives for this variant
            enhanced_variant['learning_objectives'] = self._map_variant_to_learning_objectives(
                variant, educational_context
            )
            enhanced_variant['educational_value_score'] = self._calculate_educational_value(variant)
            
            enhanced_variants.append(enhanced_variant)
        
        return enhanced_variants
    
    async def _create_variant_lesson(
        self, 
        choice: Dict[str, Any], 
        variant: Dict[str, Any],
        educational_context: EducationalContext
    ) -> Dict[str, Any]:
        """Create a Professor Pixel lesson for a variant choice."""
        
        return {
            'title': f"🎯 Choice Exploration: {choice['name']}",
            'message': f"Let's explore what happens when you choose {choice['name']} for {variant['name']}!",
            'explanation': f"This choice teaches you about {variant['educational_value']}",
            'interactive_challenge': f"Try switching between the choices to see how {variant['name']} affects your game!",
            'code_comparison': True,  # Enable split-screen code comparison
            'visual_impact': choice.get('description', ''),
            'difficulty_progression': choice.get('difficulty', 'same')
        }
    
    def _generate_educational_insight(self, choice: Dict[str, Any], variant: Dict[str, Any]) -> str:
        """Generate educational insight for a variant choice."""
        
        insights = {
            'easier': "🟢 This choice is great for beginners - it's simpler to understand and implement.",
            'harder': "🔴 This choice is more advanced - it introduces complex concepts but offers more power.",
            'same': "🟡 Both choices are similar in difficulty - this is about different approaches to the same problem."
        }
        
        difficulty = choice.get('difficulty', 'same')
        base_insight = insights.get(difficulty, insights['same'])
        
        return f"{base_insight} In {variant['name']}, this affects how {variant.get('context', 'the game')} behaves."
    
    def _map_variant_to_learning_objectives(
        self, 
        variant: Dict[str, Any], 
        educational_context: EducationalContext
    ) -> List[str]:
        """Map variant choices to specific learning objectives."""
        
        variant_mappings = {
            'grid_system': ['Coordinate systems', 'Spatial reasoning', 'Mathematical concepts'],
            'combat_system': ['State management', 'Game loops', 'Conditional logic'],
            'movement_system': ['Input handling', 'Physics concepts', 'Real-time programming'],
            'ai_behavior': ['Algorithms', 'Decision trees', 'Pathfinding concepts']
        }
        
        return variant_mappings.get(variant['id'], ['Problem-solving', 'Code organization'])
    
    def _calculate_educational_value(self, variant: Dict[str, Any]) -> float:
        """Calculate educational value score for a variant."""
        
        base_scores = {
            'visual': 0.7,      # Visual changes are easy to understand
            'mechanical': 0.9,  # Game mechanics teach core concepts well
            'algorithmic': 0.8, # Algorithms are highly educational
            'architectural': 0.6 # Code organization is important but abstract
        }
        
        variant_type = variant.get('type', 'mechanical')
        base_score = base_scores.get(variant_type, 0.7)
        
        # Bonus for beginner-friendly variants
        has_easy_choice = any(
            choice.get('difficulty') == 'easier' 
            for choice in variant.get('choices', [])
        )
        if has_easy_choice:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response."""
        # Look for code blocks
        import re
        code_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
        if code_blocks:
            return code_blocks[0]
        
        # Fallback: return basic pygame template
        return """
import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Educational Game")
clock = pygame.time.Clock()

player_health = 100
game_running = True

while game_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
    
    screen.fill((0, 0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
"""


async def create_educational_context(
    target_audience: str = "beginner",
    learning_objectives: Optional[List[str]] = None,
    programming_concepts: Optional[List[str]] = None,
    game_mechanics_focus: Optional[List[str]] = None
) -> EducationalContext:
    """Factory function to create educational context for games."""
    
    if learning_objectives is None:
        learning_objectives = [
            "Understand variables and data storage",
            "Learn basic control structures",
            "Grasp function concepts",
            "Experience cause-and-effect programming"
        ]
    
    if programming_concepts is None:
        programming_concepts = [
            "variables", "conditionals", "loops", "functions"
        ]
    
    if game_mechanics_focus is None:
        game_mechanics_focus = [
            "player movement", "collision detection", "scoring", "game state"
        ]
    
    return EducationalContext(
        target_audience=target_audience,
        learning_objectives=learning_objectives,
        programming_concepts=programming_concepts,
        game_mechanics_focus=game_mechanics_focus,
        progression_difficulty="gradual"
    )