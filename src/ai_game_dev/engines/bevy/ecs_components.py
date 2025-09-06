"""Bevy ECS component library with common patterns and optimizations."""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ComponentTemplate:
    """Template for generating Bevy components."""
    name: str
    category: str
    rust_code: str
    description: str
    usage_example: str


class ECSlibrary:
    """Library of common Bevy ECS patterns and components."""
    
    def __init__(self):
        self.components = self._initialize_component_library()
        self.systems = self._initialize_system_patterns()
        
    def _initialize_component_library(self) -> Dict[str, ComponentTemplate]:
        """Initialize library of common Bevy components."""
        
        return {
            "transform": ComponentTemplate(
                name="Transform",
                category="spatial",
                rust_code="""// Transform is built into Bevy
// Use: #[derive(Component, Default)]
// pub struct CustomTransform {
//     pub position: Vec3,
//     pub rotation: Quat,
//     pub scale: Vec3,
// }""",
                description="3D transformation component",
                usage_example="Transform::from_translation(Vec3::new(0.0, 0.0, 0.0))"
            ),
            
            "velocity": ComponentTemplate(
                name="Velocity", 
                category="physics",
                rust_code="""#[derive(Component, Default, Debug)]
pub struct Velocity {
    pub linear: Vec3,
    pub angular: Vec3,
}""",
                description="Linear and angular velocity",
                usage_example="Velocity { linear: Vec3::new(1.0, 0.0, 0.0), angular: Vec3::ZERO }"
            ),
            
            "health": ComponentTemplate(
                name="Health",
                category="gameplay", 
                rust_code="""#[derive(Component, Debug)]
pub struct Health {
    pub current: f32,
    pub maximum: f32,
}

impl Health {
    pub fn new(max_health: f32) -> Self {
        Self {
            current: max_health,
            maximum: max_health,
        }
    }
    
    pub fn take_damage(&mut self, damage: f32) {
        self.current = (self.current - damage).max(0.0);
    }
    
    pub fn heal(&mut self, amount: f32) {
        self.current = (self.current + amount).min(self.maximum);
    }
    
    pub fn is_dead(&self) -> bool {
        self.current <= 0.0
    }
    
    pub fn health_percentage(&self) -> f32 {
        self.current / self.maximum
    }
}""",
                description="Health component with damage/healing logic",
                usage_example="Health::new(100.0)"
            ),
            
            "player": ComponentTemplate(
                name="Player",
                category="identity",
                rust_code="""#[derive(Component, Default, Debug)]
pub struct Player {
    pub player_id: u32,
    pub name: String,
}""",
                description="Marks an entity as a player",
                usage_example="Player { player_id: 1, name: \"Player1\".to_string() }"
            ),
            
            "animation": ComponentTemplate(
                name="AnimationState",
                category="rendering",
                rust_code="""#[derive(Component, Debug)]
pub struct AnimationState {
    pub current_animation: String,
    pub timer: Timer,
    pub looping: bool,
    pub frame_index: usize,
}

impl Default for AnimationState {
    fn default() -> Self {
        Self {
            current_animation: "idle".to_string(),
            timer: Timer::from_seconds(0.1, TimerMode::Repeating),
            looping: true,
            frame_index: 0,
        }
    }
}""",
                description="Animation state management",
                usage_example="AnimationState::default()"
            ),
            
            "inventory": ComponentTemplate(
                name="Inventory",
                category="gameplay",
                rust_code="""#[derive(Component, Debug)]
pub struct Inventory {
    pub items: Vec<Entity>,
    pub capacity: usize,
}

impl Inventory {
    pub fn new(capacity: usize) -> Self {
        Self {
            items: Vec::new(),
            capacity,
        }
    }
    
    pub fn add_item(&mut self, item: Entity) -> bool {
        if self.items.len() < self.capacity {
            self.items.push(item);
            true
        } else {
            false
        }
    }
    
    pub fn remove_item(&mut self, item: Entity) -> bool {
        if let Some(pos) = self.items.iter().position(|&x| x == item) {
            self.items.remove(pos);
            true
        } else {
            false
        }
    }
    
    pub fn is_full(&self) -> bool {
        self.items.len() >= self.capacity
    }
}""",
                description="Inventory system for holding items",
                usage_example="Inventory::new(10)"
            ),
            
            "ai_behavior": ComponentTemplate(
                name="AIBehavior",
                category="ai",
                rust_code="""#[derive(Component, Debug)]
pub enum AIBehavior {
    Idle,
    Patrol { waypoints: Vec<Vec3>, current_target: usize },
    Chase { target: Entity },
    Attack { target: Entity, cooldown: Timer },
    Flee { from: Entity },
}

impl Default for AIBehavior {
    fn default() -> Self {
        AIBehavior::Idle
    }
}""",
                description="AI behavior state machine",
                usage_example="AIBehavior::Patrol { waypoints: vec![Vec3::ZERO], current_target: 0 }"
            ),
        }
    
    def _initialize_system_patterns(self) -> Dict[str, str]:
        """Initialize library of common Bevy system patterns."""
        
        return {
            "movement": """pub fn movement_system(
    mut query: Query<(&mut Transform, &Velocity)>,
    time: Res<Time>,
) {
    for (mut transform, velocity) in query.iter_mut() {
        transform.translation += velocity.linear * time.delta_seconds();
        transform.rotate(Quat::from_scaled_axis(velocity.angular * time.delta_seconds()));
    }
}""",
            
            "collision": """pub fn collision_system(
    query: Query<(Entity, &Transform, &Collider)>,
    mut collision_events: EventWriter<CollisionEvent>,
) {
    let entities: Vec<_> = query.iter().collect();
    
    for (i, (entity_a, transform_a, collider_a)) in entities.iter().enumerate() {
        for (entity_b, transform_b, collider_b) in entities.iter().skip(i + 1) {
            if check_collision(transform_a, collider_a, transform_b, collider_b) {
                collision_events.send(CollisionEvent {
                    entity_a: *entity_a,
                    entity_b: *entity_b,
                });
            }
        }
    }
}""",
            
            "health": """pub fn health_system(
    mut commands: Commands,
    mut query: Query<(Entity, &mut Health)>,
    mut death_events: EventWriter<DeathEvent>,
) {
    for (entity, mut health) in query.iter_mut() {
        if health.is_dead() {
            death_events.send(DeathEvent { entity });
            commands.entity(entity).despawn();
        }
    }
}""",
            
            "animation": """pub fn animation_system(
    mut query: Query<(&mut AnimationState, &mut TextureAtlasSprite)>,
    time: Res<Time>,
) {
    for (mut animation, mut sprite) in query.iter_mut() {
        animation.timer.tick(time.delta());
        
        if animation.timer.just_finished() {
            animation.frame_index += 1;
            if animation.looping && animation.frame_index >= sprite.index {
                animation.frame_index = 0;
            }
            sprite.index = animation.frame_index;
        }
    }
}""",
        }
    
    def get_component_by_category(self, category: str) -> List[ComponentTemplate]:
        """Get all components in a specific category."""
        return [comp for comp in self.components.values() if comp.category == category]
    
    def get_component_rust_code(self, component_name: str) -> str:
        """Get Rust code for a specific component."""
        comp = self.components.get(component_name.lower())
        return comp.rust_code if comp else ""
    
    def get_system_pattern(self, pattern_name: str) -> str:
        """Get code for a specific system pattern."""
        return self.systems.get(pattern_name, "")
    
    def get_all_categories(self) -> List[str]:
        """Get all available component categories."""
        return list(set(comp.category for comp in self.components.values()))