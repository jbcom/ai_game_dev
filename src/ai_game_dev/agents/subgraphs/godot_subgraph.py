"""
Godot Engine Subgraph
Generates complete Godot projects with GDScript
"""
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from ai_game_dev.agents.base_agent import AgentConfig, BaseAgent


@dataclass
class GodotState:
    """State for Godot game generation."""
    game_spec: dict[str, Any] = field(default_factory=dict)
    generated_files: dict[str, str] = field(default_factory=dict)
    scene_files: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    complete: bool = False


class GodotSubgraph(BaseAgent):
    """
    Subgraph for generating Godot games.
    
    Handles:
    - Scene tree structure
    - GDScript generation
    - Node composition
    - Signal connections
    - Resource management
    """
    
    def __init__(self):
        config = AgentConfig(
            model="gpt-4o",
            temperature=0.2,
            instructions=self._get_godot_instructions()
        )
        super().__init__(config)
        self.graph = None
    
    def _get_godot_instructions(self) -> str:
        return """You are a Godot game development expert specializing in GDScript.
        
        Generate complete Godot projects with:
        1. Proper scene hierarchy and node structure
        2. GDScript with type hints and best practices
        3. Signal-based communication between nodes
        4. Resource preloading and management
        5. Responsive UI with Control nodes
        6. Educational comments explaining Godot concepts
        
        Follow Godot best practices:
        - Use scene inheritance for reusable components
        - Implement proper _ready() and _process() functions
        - Handle input with _input() and _unhandled_input()
        - Use groups for entity management
        - Export variables for inspector configuration
        """
    
    async def initialize(self):
        """Initialize the Godot subgraph."""
        await super().initialize()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the Godot generation workflow."""
        workflow = StateGraph(GodotState)
        
        # Add nodes
        workflow.add_node("analyze_spec", self._analyze_spec)
        workflow.add_node("generate_project", self._generate_project)
        workflow.add_node("generate_main_scene", self._generate_main_scene)
        workflow.add_node("generate_player", self._generate_player)
        workflow.add_node("generate_ui", self._generate_ui)
        workflow.add_node("generate_game_logic", self._generate_game_logic)
        
        # Add edges
        workflow.set_entry_point("analyze_spec")
        workflow.add_edge("analyze_spec", "generate_project")
        workflow.add_edge("generate_project", "generate_main_scene")
        workflow.add_edge("generate_main_scene", "generate_player")
        workflow.add_edge("generate_player", "generate_ui")
        workflow.add_edge("generate_ui", "generate_game_logic")
        workflow.add_edge("generate_game_logic", END)
        
        return workflow.compile()
    
    async def _analyze_spec(self, state: GodotState) -> GodotState:
        """Analyze game specification for Godot requirements."""
        spec = state.game_spec
        
        # Determine Godot-specific needs
        features = spec.get("features", [])
        is_2d = "2d" in str(spec.get("type", "2d")).lower()
        
        state.scene_files = ["Main.tscn", "Player.tscn", "UI.tscn"]
        return state
    
    async def _generate_project(self, state: GodotState) -> GodotState:
        """Generate Godot project configuration."""
        spec = state.game_spec
        
        project_godot = f'''[application]

config/name="{spec.get("title", "Godot Game")}"
config/description="{spec.get("description", "A Godot game")}"
run/main_scene="res://scenes/Main.tscn"
config/features=PackedStringArray("4.2", "GDScript")

[display]

window/size/viewport_width=1280
window/size/viewport_height=720

[input]

move_left={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":65,"key_label":0,"unicode":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194319,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}}

move_right={{
"deadzone": 0.5,
"events": [Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":68,"key_label":0,"unicode":0,"echo":false,"script":null)
, Object(InputEventKey,"resource_local_to_scene":false,"resource_name":"","device":0,"window_id":0,"alt_pressed":false,"shift_pressed":false,"ctrl_pressed":false,"meta_pressed":false,"pressed":false,"keycode":0,"physical_keycode":4194321,"key_label":0,"unicode":0,"echo":false,"script":null)
]
}}

[rendering]

renderer/rendering_method="forward_plus"
'''
        
        state.generated_files["project.godot"] = project_godot
        return state
    
    async def _generate_main_scene(self, state: GodotState) -> GodotState:
        """Generate main scene and script."""
        main_gd = '''extends Node2D
## Main game controller

signal game_started
signal game_over

@export var player_scene: PackedScene = preload("res://scenes/Player.tscn")

var score: int = 0
var game_active: bool = false

@onready var ui: Control = $UI
@onready var spawn_timer: Timer = $SpawnTimer


func _ready() -> void:
	## Initialize the game
	ui.start_game.connect(_on_start_game)
	set_process(false)


func _on_start_game() -> void:
	## Start a new game
	game_active = true
	score = 0
	set_process(true)
	emit_signal("game_started")
	
	# Spawn player
	var player = player_scene.instantiate()
	player.position = Vector2(640, 360)
	add_child(player)


func add_score(points: int) -> void:
	## Add points to score
	score += points
	ui.update_score(score)


func _on_game_over() -> void:
	## Handle game over
	game_active = false
	set_process(false)
	emit_signal("game_over")
	ui.show_game_over(score)
'''
        
        state.generated_files["scripts/Main.gd"] = main_gd
        
        # Simple scene file (normally binary, but we'll describe it)
        state.generated_files["scenes/Main.tscn"] = """[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scripts/Main.gd" id="1"]
[ext_resource type="PackedScene" path="res://scenes/UI.tscn" id="2"]

[node name="Main" type="Node2D"]
script = ExtResource("1")

[node name="UI" parent="." instance=ExtResource("2")]

[node name="SpawnTimer" type="Timer" parent="."]
wait_time = 2.0
autostart = true
"""
        
        return state
    
    async def _generate_player(self, state: GodotState) -> GodotState:
        """Generate player scene and controller."""
        player_gd = '''extends CharacterBody2D
## Player character controller

signal health_changed(new_health: int)
signal player_died

@export var speed: float = 300.0
@export var max_health: int = 100

var health: int = max_health

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D


func _ready() -> void:
	## Initialize player
	health = max_health


func _physics_process(delta: float) -> void:
	## Handle movement
	var direction := Vector2.ZERO
	
	# Get input
	if Input.is_action_pressed("move_left"):
		direction.x -= 1
	if Input.is_action_pressed("move_right"):
		direction.x += 1
	if Input.is_action_pressed("move_up"):
		direction.y -= 1
	if Input.is_action_pressed("move_down"):
		direction.y += 1
	
	# Normalize and apply movement
	if direction.length() > 0:
		direction = direction.normalized()
		velocity = direction * speed
	else:
		velocity = velocity.move_toward(Vector2.ZERO, speed * delta)
	
	move_and_slide()


func take_damage(amount: int) -> void:
	## Apply damage to player
	health -= amount
	emit_signal("health_changed", health)
	
	if health <= 0:
		die()


func die() -> void:
	## Handle player death
	emit_signal("player_died")
	queue_free()
'''
        
        state.generated_files["scripts/Player.gd"] = player_gd
        state.generated_files["scenes/Player.tscn"] = """[gd_scene load_steps=3 format=3]

[ext_resource type="Script" path="res://scripts/Player.gd" id="1"]

[sub_resource type="RectangleShape2D" id="1"]
size = Vector2(32, 32)

[node name="Player" type="CharacterBody2D"]
script = ExtResource("1")

[node name="Sprite2D" type="Sprite2D" parent="."]

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("1")
"""
        
        return state
    
    async def _generate_ui(self, state: GodotState) -> GodotState:
        """Generate UI scene and controller."""
        ui_gd = '''extends Control
## Game UI controller

signal start_game

@onready var score_label: Label = $ScoreLabel
@onready var menu_panel: Panel = $MenuPanel
@onready var game_over_panel: Panel = $GameOverPanel
@onready var start_button: Button = $MenuPanel/StartButton
@onready var final_score_label: Label = $GameOverPanel/FinalScoreLabel


func _ready() -> void:
	## Initialize UI
	start_button.pressed.connect(_on_start_button_pressed)
	game_over_panel.visible = false


func _on_start_button_pressed() -> void:
	## Start game button pressed
	menu_panel.visible = false
	emit_signal("start_game")


func update_score(score: int) -> void:
	## Update score display
	score_label.text = "Score: " + str(score)


func show_game_over(final_score: int) -> void:
	## Show game over screen
	game_over_panel.visible = true
	final_score_label.text = "Final Score: " + str(final_score)
'''
        
        state.generated_files["scripts/UI.gd"] = ui_gd
        state.complete = True
        
        return state
    
    async def _generate_game_logic(self, state: GodotState) -> GodotState:
        """Generate additional game logic scripts."""
        # Add any additional game-specific logic here
        return state
    
    async def process(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Process Godot generation request."""
        initial_state = GodotState(
            game_spec=inputs.get("game_spec", inputs)
        )
        
        # Run the graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "success": final_state.complete,
            "files": final_state.generated_files,
            "errors": final_state.errors,
            "engine": "godot"
        }