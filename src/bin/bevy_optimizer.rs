//! Standalone Bevy game optimizer
//! 
//! This binary provides command-line optimization for Bevy games generated
//! by the AI Game Development library.

use ai_game_dev::{RustGameDevBridge, bevy_optimization::*};
use std::env;
use std::fs;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        println!("Usage: bevy_optimizer <game_data.json>");
        return Ok(());
    }
    
    let input_file = &args[1];
    
    if !Path::new(input_file).exists() {
        eprintln!("Error: File '{}' not found", input_file);
        return Ok(());
    }
    
    println!("🦀 Bevy Game Optimizer");
    println!("======================");
    println!("Optimizing: {}", input_file);
    
    // Read game data
    let game_json = fs::read_to_string(input_file)?;
    
    // Create optimization bridge
    let mut bridge = RustGameDevBridge::new();
    
    // Apply optimizations
    match bridge.optimize_bevy_game(&game_json) {
        Ok(optimizations) => {
            println!("✅ Optimizations applied:");
            println!("{}", optimizations);
            
            // Save optimized version
            let output_file = format!("{}.optimized.json", input_file);
            fs::write(&output_file, optimizations)?;
            println!("💾 Saved to: {}", output_file);
        }
        Err(e) => {
            eprintln!("❌ Optimization failed: {}", e);
        }
    }
    
    // Generate performance analysis
    let analysis = bridge.analyze_performance();
    println!("📊 Performance Analysis:");
    println!("{}", analysis);
    
    Ok(())
}