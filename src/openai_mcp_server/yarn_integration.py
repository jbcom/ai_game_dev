"""Advanced Python YarnSpinner integration system with multiple backend support."""

import asyncio
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

import aiofiles
from openai import AsyncOpenAI

from .config import settings
from .logging_config import get_logger
from .utils import ensure_directory_exists

logger = get_logger(__name__, component="yarn_integration")


class YarnBackend(str, Enum):
    """Supported YarnSpinner backends."""
    YARN_PYGAME = "yarn_pygame"  # Python implementation
    YARN_JSON_EXPORT = "json_export"  # JSON-based custom parser
    YARN_CONSOLE = "console_tool"  # External ysc compiler
    

class YarnNodeType(str, Enum):
    """Types of Yarn dialogue nodes."""
    DIALOGUE = "dialogue"
    CHOICE = "choice"
    COMMAND = "command"
    CONDITIONAL = "conditional"
    JUMP = "jump"


@dataclass
class YarnDialogueNode:
    """Enhanced Yarn dialogue node with Python integration."""
    node_id: str
    title: str
    tags: List[str]
    body: List[str]  # Lines of dialogue content
    choices: List[Dict[str, Any]]
    conditions: List[str]
    commands: List[str]
    variables: Dict[str, Any]
    
    def to_yarn_format(self) -> str:
        """Convert to standard Yarn format."""
        content = []
        
        # Header
        content.append(f"title: {self.title}")
        if self.tags:
            content.append(f"tags: {' '.join(self.tags)}")
        content.append("---")
        
        # Body content
        for line in self.body:
            content.append(line)
        
        # Choices
        for choice in self.choices:
            choice_text = f"-> {choice['text']}"
            if choice.get('condition'):
                choice_text += f" <<if {choice['condition']}>>"
            content.append(choice_text)
            
            if choice.get('destination'):
                content.append(f"    <<jump {choice['destination']}>>")
            elif choice.get('body'):
                for body_line in choice['body']:
                    content.append(f"    {body_line}")
        
        # Footer
        content.append("===")
        return "\n".join(content)
    
    def to_json_format(self) -> Dict[str, Any]:
        """Convert to JSON format for custom parser."""
        return {
            "id": self.node_id,
            "title": self.title,
            "tags": self.tags,
            "body": self.body,
            "choices": self.choices,
            "conditions": self.conditions,
            "commands": self.commands,
            "variables": self.variables
        }


class PythonYarnRunner:
    """Python-based Yarn dialogue runner with multiple backend support."""
    
    def __init__(self, backend: YarnBackend = YarnBackend.YARN_JSON_EXPORT):
        self.backend = backend
        self.dialogue_dir = settings.cache_dir / "dialogue"
        self.current_node = None
        self.variables = {}
        self.dialogue_history = []
        
    async def initialize(self):
        """Initialize the Yarn runner."""
        await ensure_directory_exists(self.dialogue_dir)
        
        if self.backend == YarnBackend.YARN_PYGAME:
            await self._setup_yarn_pygame()
        elif self.backend == YarnBackend.YARN_CONSOLE:
            await self._setup_yarn_console()
    
    async def create_dialogue_tree(
        self,
        dialogue_nodes: List[YarnDialogueNode],
        filename: str,
        project_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create complete dialogue tree with Python integration."""
        
        # Create project-specific directory
        if project_context:
            project_dir = self.dialogue_dir / project_context
            await ensure_directory_exists(project_dir)
            base_path = project_dir / filename
        else:
            base_path = self.dialogue_dir / filename
        
        results = {
            "filename": filename,
            "node_count": len(dialogue_nodes),
            "backend": self.backend.value,
            "files_created": []
        }
        
        if self.backend == YarnBackend.YARN_PYGAME:
            # Create yarn-pygame compatible format
            yarn_content = []
            for node in dialogue_nodes:
                yarn_content.append(node.to_yarn_format())
            
            yarn_file = f"{base_path}.yarn"
            async with aiofiles.open(yarn_file, 'w') as f:
                await f.write("\n\n".join(yarn_content))
            
            results["files_created"].append(str(yarn_file))
            
            # Create Python runner integration
            python_runner = await self._create_python_runner(dialogue_nodes, base_path)
            results["files_created"].append(python_runner)
            
        elif self.backend == YarnBackend.YARN_JSON_EXPORT:
            # Create JSON format for custom parser
            json_data = {
                "project": filename,
                "nodes": [node.to_json_format() for node in dialogue_nodes],
                "variables": {},
                "metadata": {
                    "created_by": "OpenAI MCP Server",
                    "node_count": len(dialogue_nodes),
                    "backend": self.backend.value
                }
            }
            
            json_file = f"{base_path}.json"
            async with aiofiles.open(json_file, 'w') as f:
                await f.write(json.dumps(json_data, indent=2))
            
            results["files_created"].append(str(json_file))
            
            # Create custom Python parser
            parser_file = await self._create_json_parser(json_data, base_path)
            results["files_created"].append(parser_file)
        
        elif self.backend == YarnBackend.YARN_CONSOLE:
            # Create standard Yarn format for console tool
            yarn_content = []
            for node in dialogue_nodes:
                yarn_content.append(node.to_yarn_format())
            
            yarn_file = f"{base_path}.yarn"
            async with aiofiles.open(yarn_file, 'w') as f:
                await f.write("\n\n".join(yarn_content))
            
            results["files_created"].append(str(yarn_file))
            
            # Attempt to compile with yarn console tool
            try:
                compiled_file = await self._compile_with_ysc(yarn_file)
                if compiled_file:
                    results["files_created"].append(compiled_file)
            except Exception as e:
                logger.warning(f"YarnSpinner console compilation failed: {e}")
        
        return results
    
    async def _create_python_runner(
        self, 
        dialogue_nodes: List[YarnDialogueNode], 
        base_path: Path
    ) -> str:
        """Create Python dialogue runner for yarn-pygame."""
        
        runner_code = '''"""
Python Yarn dialogue runner generated by OpenAI MCP Server.
Compatible with yarn-pygame library.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class DialogueRunner:
    """Python dialogue runner for generated Yarn content."""
    
    def __init__(self, yarn_file: str):
        self.yarn_file = yarn_file
        self.current_node = None
        self.variables = {}
        self.dialogue_history = []
        
    def load_dialogue(self):
        """Load dialogue from Yarn file."""
        try:
            # This would integrate with yarn-pygame
            # For now, implement basic JSON-based runner
            pass
        except ImportError:
            print("yarn-pygame not available, using basic runner")
            return self._load_basic_dialogue()
    
    def _load_basic_dialogue(self):
        """Basic dialogue loader without yarn-pygame."""
        # Implementation for standalone dialogue running
        pass
    
    def get_current_text(self) -> Optional[str]:
        """Get current dialogue text."""
        if self.current_node:
            return self.current_node.get('text', '')
        return None
    
    def get_choices(self) -> List[Dict[str, str]]:
        """Get available dialogue choices."""
        if self.current_node and 'choices' in self.current_node:
            return self.current_node['choices']
        return []
    
    def select_choice(self, choice_index: int):
        """Select a dialogue choice and advance."""
        choices = self.get_choices()
        if 0 <= choice_index < len(choices):
            selected = choices[choice_index]
            # Handle choice selection logic
            self._advance_to_node(selected.get('destination'))
    
    def _advance_to_node(self, node_id: str):
        """Advance dialogue to specific node."""
        # Implementation for node traversal
        pass
    
    def is_finished(self) -> bool:
        """Check if dialogue is complete."""
        return self.current_node is None


# Example usage:
if __name__ == "__main__":
    runner = DialogueRunner("dialogue.yarn")
    runner.load_dialogue()
    
    while not runner.is_finished():
        text = runner.get_current_text()
        if text:
            print(f"Dialogue: {text}")
        
        choices = runner.get_choices()
        if choices:
            for i, choice in enumerate(choices):
                print(f"{i + 1}. {choice['text']}")
            
            try:
                selection = int(input("Choose: ")) - 1
                runner.select_choice(selection)
            except (ValueError, IndexError):
                print("Invalid choice")
        else:
            break
'''
        
        runner_file = f"{base_path}_runner.py"
        async with aiofiles.open(runner_file, 'w') as f:
            await f.write(runner_code)
        
        logger.info(f"Created Python dialogue runner: {runner_file}")
        return str(runner_file)
    
    async def _create_json_parser(
        self, 
        json_data: Dict[str, Any], 
        base_path: Path
    ) -> str:
        """Create custom JSON dialogue parser."""
        
        parser_code = f'''"""
Custom JSON dialogue parser generated by OpenAI MCP Server.
Handles dialogue trees exported from Yarn format.
"""

import json
from typing import Dict, List, Optional, Any, Callable


class JSONDialogueParser:
    """Custom parser for JSON-exported Yarn dialogue."""
    
    def __init__(self):
        self.nodes = {json.dumps(json_data['nodes'], indent=2)}
        self.current_node_id = None
        self.variables = {json.dumps(json_data.get('variables', {}), indent=2)}
        self.dialogue_history = []
        self.event_handlers = {{}}}
        
    def start_dialogue(self, starting_node: str = None):
        """Start dialogue from specified node or first available."""
        if starting_node:
            self.current_node_id = starting_node
        elif self.nodes:
            # Find a node tagged as 'start' or use first node
            for node in self.nodes:
                if 'start' in node.get('tags', []):
                    self.current_node_id = node['id']
                    break
            else:
                self.current_node_id = self.nodes[0]['id']
        
        return self.get_current_dialogue()
    
    def get_current_dialogue(self) -> Optional[Dict[str, Any]]:
        """Get current dialogue content."""
        if not self.current_node_id:
            return None
            
        current_node = self._get_node(self.current_node_id)
        if not current_node:
            return None
        
        return {{
            'id': current_node['id'],
            'title': current_node['title'],
            'text': '\\n'.join(current_node['body']),
            'choices': current_node['choices'],
            'commands': current_node['commands'],
            'tags': current_node['tags']
        }}
    
    def _get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get node by ID."""
        for node in self.nodes:
            if node['id'] == node_id:
                return node
        return None
    
    def make_choice(self, choice_index: int) -> bool:
        """Make a dialogue choice and advance."""
        current = self.get_current_dialogue()
        if not current or not current['choices']:
            return False
            
        if 0 <= choice_index < len(current['choices']):
            choice = current['choices'][choice_index]
            
            # Add to history
            self.dialogue_history.append({{
                'node_id': self.current_node_id,
                'choice': choice
            }})
            
            # Handle choice destination
            if choice.get('destination'):
                self.current_node_id = choice['destination']
                return True
            else:
                # Choice might contain inline content
                self._handle_inline_choice(choice)
                return True
        
        return False
    
    def _handle_inline_choice(self, choice: Dict[str, Any]):
        """Handle choices with inline content."""
        # Process any commands in the choice
        if choice.get('commands'):
            for command in choice['commands']:
                self._execute_command(command)
    
    def _execute_command(self, command: str):
        """Execute Yarn command."""
        # Handle basic Yarn commands
        if command.startswith('<<set '):
            # Variable setting
            var_assignment = command[6:-2]  # Remove <<set >> wrapper
            if '=' in var_assignment:
                var_name, value = var_assignment.split('=', 1)
                self.variables[var_name.strip()] = value.strip()
        
        elif command.startswith('<<jump '):
            # Node jumping
            destination = command[7:-2]  # Remove <<jump >> wrapper
            self.current_node_id = destination.strip()
        
        # Fire event for custom commands
        if command in self.event_handlers:
            self.event_handlers[command]()
    
    def register_command_handler(self, command: str, handler: Callable):
        """Register custom command handler."""
        self.event_handlers[command] = handler
    
    def is_dialogue_finished(self) -> bool:
        """Check if dialogue has ended."""
        current = self.get_current_dialogue()
        return current is None or (not current['choices'] and not current['text'])
    
    def get_variable(self, var_name: str) -> Any:
        """Get dialogue variable value."""
        return self.variables.get(var_name)
    
    def set_variable(self, var_name: str, value: Any):
        """Set dialogue variable value."""
        self.variables[var_name] = value


# Example usage:
if __name__ == "__main__":
    parser = JSONDialogueParser()
    
    # Start dialogue
    dialogue = parser.start_dialogue()
    
    while dialogue and not parser.is_dialogue_finished():
        print(f"\\n{{dialogue['text']}}")
        
        if dialogue['choices']:
            print("\\nChoices:")
            for i, choice in enumerate(dialogue['choices']):
                print(f"{{i + 1}}. {{choice['text']}}")
            
            try:
                selection = int(input("\\nChoose (1-{{len(dialogue['choices'])}}): ")) - 1
                if parser.make_choice(selection):
                    dialogue = parser.get_current_dialogue()
                else:
                    print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")
        else:
            print("\\n[Dialogue ended]")
            break
'''
        
        parser_file = f"{base_path}_parser.py"
        async with aiofiles.open(parser_file, 'w') as f:
            await f.write(parser_code)
        
        logger.info(f"Created JSON dialogue parser: {parser_file}")
        return str(parser_file)
    
    async def _setup_yarn_pygame(self):
        """Set up yarn-pygame integration."""
        # Check if yarn-pygame is available
        try:
            # This would check for yarn-pygame installation
            logger.info("yarn-pygame backend selected")
        except ImportError:
            logger.warning("yarn-pygame not available, falling back to JSON export")
            self.backend = YarnBackend.YARN_JSON_EXPORT
    
    async def _setup_yarn_console(self):
        """Set up YarnSpinner console tool integration."""
        try:
            # Check for ysc (YarnSpinner Console) availability
            result = subprocess.run(['ysc', '--version'], capture_output=True, text=True)
            logger.info(f"YarnSpinner Console available: {result.stdout}")
        except FileNotFoundError:
            logger.warning("YarnSpinner Console (ysc) not available")
            self.backend = YarnBackend.YARN_JSON_EXPORT
    
    async def _compile_with_ysc(self, yarn_file: str) -> Optional[str]:
        """Compile Yarn file with YarnSpinner Console."""
        try:
            output_file = f"{yarn_file}.yarnc"
            result = subprocess.run([
                'ysc', 'compile', yarn_file, '-o', output_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully compiled {yarn_file} to {output_file}")
                return output_file
            else:
                logger.error(f"YarnSpinner compilation failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"YarnSpinner Console compilation error: {e}")
            return None
    
    async def export_for_engine(
        self, 
        dialogue_data: Dict[str, Any], 
        target_engine: str,
        output_path: Path
    ) -> List[str]:
        """Export dialogue for specific game engine."""
        
        exported_files = []
        
        if target_engine.lower() == "bevy":
            # Export for Bevy with bevy_yarnspinner
            bevy_integration = f'''
// Bevy YarnSpinner integration code
use bevy::prelude::*;
use bevy_yarnspinner::prelude::*;

#[derive(Component)]
pub struct DialogueComponent {{
    pub dialogue_file: String,
    pub current_node: Option<String>,
}}

fn setup_dialogue_system(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
) {{
    // Load dialogue file
    let dialogue_handle = asset_server.load("{dialogue_data['filename']}.yarn");
    
    commands.spawn((
        DialogueComponent {{
            dialogue_file: "{dialogue_data['filename']}.yarn".to_string(),
            current_node: None,
        }},
        YarnSpinnerComponent::new(dialogue_handle),
    ));
}}

fn dialogue_system(
    mut dialogue_query: Query<&mut DialogueComponent>,
    mut yarn_events: EventReader<YarnSpinnerEvent>,
) {{
    for event in yarn_events.iter() {{
        match event {{
            YarnSpinnerEvent::DialogueStart {{ node }} => {{
                println!("Dialogue started at node: {{}}", node);
            }}
            YarnSpinnerEvent::DialogueComplete => {{
                println!("Dialogue completed");
            }}
            YarnSpinnerEvent::LineReceived {{ line }} => {{
                println!("Dialogue line: {{}}", line.text);
            }}
            YarnSpinnerEvent::ChoicesReceived {{ choices }} => {{
                for (i, choice) in choices.iter().enumerate() {{
                    println!("{{}}: {{}}", i, choice.text);
                }}
            }}
        }}
    }}
}}
'''
            bevy_file = output_path / f"{dialogue_data['filename']}_bevy.rs"
            async with aiofiles.open(bevy_file, 'w') as f:
                await f.write(bevy_integration)
            exported_files.append(str(bevy_file))
        
        elif target_engine.lower() == "godot":
            # Export for Godot with YarnSpinner-Godot
            godot_integration = f'''
# Godot YarnSpinner integration script
extends Node

var yarn_dialogue: YarnDialogue
var dialogue_ui: Control

func _ready():
	# Initialize YarnSpinner
	yarn_dialogue = YarnDialogue.new()
	yarn_dialogue.dialogue_file = "res://dialogue/{dialogue_data['filename']}.yarn"
	
	# Connect signals
	yarn_dialogue.connect("line_received", self, "_on_line_received")
	yarn_dialogue.connect("choices_received", self, "_on_choices_received")
	yarn_dialogue.connect("dialogue_complete", self, "_on_dialogue_complete")
	
	# Start dialogue
	yarn_dialogue.start_dialogue()

func _on_line_received(line: String, character: String):
	print("{{character}}: {{line}}")
	# Update UI with dialogue line

func _on_choices_received(choices: Array):
	print("Choices available:")
	for i in range(choices.size()):
		print("{{i + 1}}. {{choices[i]}}")
	# Show choice UI

func _on_dialogue_complete():
	print("Dialogue finished")
	# Handle dialogue end
'''
            godot_file = output_path / f"{dialogue_data['filename']}_godot.gd"
            async with aiofiles.open(godot_file, 'w') as f:
                await f.write(godot_integration)
            exported_files.append(str(godot_file))
        
        return exported_files