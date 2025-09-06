use criterion::{black_box, criterion_group, criterion_main, Criterion};
use bevy_ai_game_dev::{generate_bevy_project, GameSpec, GameType, ComplexityLevel};

fn bench_2d_game_generation(c: &mut Criterion) {
    let spec = GameSpec {
        name: "BenchmarkGame2D".to_string(),
        description: "A simple 2D platformer for benchmarking".to_string(),
        game_type: GameType::TwoDimensional,
        features: vec!["physics".to_string(), "audio".to_string()],
        complexity: ComplexityLevel::Intermediate,
    };

    c.bench_function("generate_2d_bevy_project", |b| {
        b.iter(|| generate_bevy_project(black_box(&spec)))
    });
}

fn bench_3d_game_generation(c: &mut Criterion) {
    let spec = GameSpec {
        name: "BenchmarkGame3D".to_string(),
        description: "A 3D adventure game for benchmarking".to_string(),
        game_type: GameType::ThreeDimensional,
        features: vec!["physics".to_string(), "ai".to_string()],
        complexity: ComplexityLevel::Advanced,
    };

    c.bench_function("generate_3d_bevy_project", |b| {
        b.iter(|| generate_bevy_project(black_box(&spec)))
    });
}

fn bench_complex_game_generation(c: &mut Criterion) {
    let spec = GameSpec {
        name: "ComplexBenchmarkGame".to_string(),
        description: "A complex game with all features enabled".to_string(),
        game_type: GameType::ThreeDimensional,
        features: vec![
            "physics".to_string(),
            "ai".to_string(),
            "audio".to_string(),
            "networking".to_string(),
        ],
        complexity: ComplexityLevel::Advanced,
    };

    c.bench_function("generate_complex_bevy_project", |b| {
        b.iter(|| generate_bevy_project(black_box(&spec)))
    });
}

criterion_group!(
    benches,
    bench_2d_game_generation,
    bench_3d_game_generation,
    bench_complex_game_generation
);
criterion_main!(benches);