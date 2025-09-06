/*!
 * Bevy Space Shooter Example
 * Demonstrates AI-powered game development with bevy_game_dev
 */

use bevy::prelude::*;
use bevy_game_dev::{AIGameDev, GameSpec, GameType, ComplexityLevel};

fn main() {
    println!("🚀 AI-Powered Bevy Space Shooter Demo");
    
    // Generate game specification using AI
    let spec = GameSpec {
        name: "AI Space Shooter".to_string(),
        description: "Fast-paced space shooter with AI-generated content".to_string(),
        game_type: GameType::TwoDimensional,
        features: vec![
            "Player spaceship with smooth movement".to_string(),
            "Enemy waves with different behaviors".to_string(),
            "Power-ups and weapon upgrades".to_string(),
            "Particle effects and explosions".to_string(),
            "Progressive difficulty scaling".to_string(),
        ],
        complexity: ComplexityLevel::Intermediate,
    };
    
    // Initialize AI game development system
    let mut game_dev = AIGameDev::new();
    
    println!("🎮 Generating space shooter with AI...");
    
    // Generate game project
    match game_dev.generate_bevy_project(&spec) {
        Ok(project) => {
            println!("✅ Game project generated successfully!");
            println!("📁 Project contains {} systems", project.systems.len());
            println!("🎨 Generated {} components", project.components.len());
            
            // Start the Bevy app with generated content
            run_space_shooter(project);
        }
        Err(e) => {
            eprintln!("❌ Failed to generate game: {}", e);
            std::process::exit(1);
        }
    }
}

fn run_space_shooter(project: bevy_game_dev::BevyProject) {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "AI Generated Space Shooter".to_string(),
                resolution: (800.0, 600.0).into(),
                ..default()
            }),
            ..default()
        }))
        .add_systems(Startup, setup)
        .add_systems(Update, (
            player_movement,
            player_shooting,
            enemy_movement,
            collision_system,
            cleanup_system,
        ))
        .run();
}

#[derive(Component)]
struct Player {
    speed: f32,
}

#[derive(Component)]
struct Enemy {
    speed: f32,
    health: i32,
}

#[derive(Component)]
struct Bullet {
    speed: f32,
    direction: Vec3,
}

#[derive(Component)]
struct Health(i32);

fn setup(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    // Camera
    commands.spawn(Camera2dBundle::default());
    
    // Player spaceship
    commands.spawn((
        MaterialMesh2dBundle {
            mesh: meshes.add(shape::RegularPolygon::new(20.0, 3).into()).into(),
            material: materials.add(ColorMaterial::from(Color::rgb(0.0, 0.8, 0.0))),
            transform: Transform::from_translation(Vec3::new(0.0, -250.0, 0.0)),
            ..default()
        },
        Player { speed: 300.0 },
        Health(100),
    ));
    
    println!("🎮 Space shooter initialized! Use WASD to move, SPACE to shoot");
}

fn player_movement(
    keyboard: Res<Input<KeyCode>>,
    time: Res<Time>,
    mut query: Query<&mut Transform, With<Player>>,
) {
    for mut transform in &mut query {
        let mut direction = Vec3::ZERO;
        
        if keyboard.pressed(KeyCode::A) || keyboard.pressed(KeyCode::Left) {
            direction.x -= 1.0;
        }
        if keyboard.pressed(KeyCode::D) || keyboard.pressed(KeyCode::Right) {
            direction.x += 1.0;
        }
        if keyboard.pressed(KeyCode::W) || keyboard.pressed(KeyCode::Up) {
            direction.y += 1.0;
        }
        if keyboard.pressed(KeyCode::S) || keyboard.pressed(KeyCode::Down) {
            direction.y -= 1.0;
        }
        
        if direction.length() > 0.0 {
            direction = direction.normalize();
            transform.translation += direction * 300.0 * time.delta_seconds();
        }
        
        // Keep player on screen
        transform.translation.x = transform.translation.x.clamp(-380.0, 380.0);
        transform.translation.y = transform.translation.y.clamp(-280.0, 280.0);
    }
}

fn player_shooting(
    mut commands: Commands,
    keyboard: Res<Input<KeyCode>>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<ColorMaterial>>,
    player_query: Query<&Transform, With<Player>>,
) {
    if keyboard.just_pressed(KeyCode::Space) {
        for player_transform in &player_query {
            // Spawn bullet
            commands.spawn((
                MaterialMesh2dBundle {
                    mesh: meshes.add(shape::Circle::new(3.0).into()).into(),
                    material: materials.add(ColorMaterial::from(Color::YELLOW)),
                    transform: Transform::from_translation(
                        player_transform.translation + Vec3::new(0.0, 30.0, 0.0)
                    ),
                    ..default()
                },
                Bullet {
                    speed: 500.0,
                    direction: Vec3::Y,
                },
            ));
        }
    }
}

fn enemy_movement(
    time: Res<Time>,
    mut query: Query<&mut Transform, With<Enemy>>,
) {
    for mut transform in &mut query {
        transform.translation.y -= 100.0 * time.delta_seconds();
        
        // Remove enemies that go off screen
        if transform.translation.y < -350.0 {
            // This would need entity cleanup in a real implementation
        }
    }
}

fn collision_system(
    mut commands: Commands,
    bullet_query: Query<(Entity, &Transform), With<Bullet>>,
    enemy_query: Query<(Entity, &Transform), With<Enemy>>,
) {
    for (bullet_entity, bullet_transform) in &bullet_query {
        for (enemy_entity, enemy_transform) in &enemy_query {
            let distance = bullet_transform.translation.distance(enemy_transform.translation);
            
            if distance < 25.0 {
                // Collision detected
                commands.entity(bullet_entity).despawn();
                commands.entity(enemy_entity).despawn();
                
                println!("💥 Enemy destroyed!");
            }
        }
    }
}

fn cleanup_system(
    mut commands: Commands,
    bullet_query: Query<(Entity, &Transform), With<Bullet>>,
) {
    for (entity, transform) in &bullet_query {
        if transform.translation.y > 350.0 {
            commands.entity(entity).despawn();
        }
    }
}