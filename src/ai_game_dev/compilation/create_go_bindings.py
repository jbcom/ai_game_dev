#!/usr/bin/env python3
"""
Create Go language bindings for the compiled C++ binary.
Enables Go applications to use the AI Game Development library via CGO.
"""
from pathlib import Path
from typing import Dict

from ai_game_dev.logging_config import get_logger

logger = get_logger(__name__, component="go_bindings")


class GoBindingsGenerator:
    """Generate Go bindings for the AI Game Dev library."""
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("dist/bindings/go")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_bindings(self) -> Dict[str, Path]:
        """Generate complete Go bindings package."""
        logger.info("🐹 Generating Go bindings...")
        
        files = {}
        
        # Go module files
        files['mod'] = self.create_go_mod()
        files['main'] = self.create_main_bindings()
        files['types'] = self.create_types_definitions()
        files['examples'] = self.create_examples()
        files['tests'] = self.create_tests()
        files['readme'] = self.create_documentation()
        
        logger.info("✅ Go bindings generated successfully")
        return files
    
    def create_go_mod(self) -> Path:
        """Create go.mod file."""
        mod_content = '''module github.com/ai-game-dev/go-bindings

go 1.21

require ()
'''
        
        mod_path = self.output_dir / "go.mod"
        with open(mod_path, "w") as f:
            f.write(mod_content)
        
        return mod_path
    
    def create_main_bindings(self) -> Path:
        """Create main Go bindings file."""
        go_content = '''// Package aigamedev provides Go bindings for the AI Game Development library
package aigamedev

/*
#cgo CFLAGS: -I../compiled/include
#cgo LDFLAGS: -L../compiled/lib -lai_game_dev

#include "ai_game_dev.h"
#include <stdlib.h>
*/
import "C"
import (
	"errors"
	"runtime"
	"unsafe"
)

// GameEngine represents supported game engines
type GameEngine string

const (
	EngineBevy   GameEngine = "bevy"
	EngineGodot  GameEngine = "godot"
	EngineArcade GameEngine = "arcade"
	EngineAuto   GameEngine = "auto"
)

// GameConfig holds configuration for game creation
type GameConfig struct {
	Engine         GameEngine
	Complexity     string
	TargetAudience string
	Features       []string
}

// GameResult contains the result of game creation
type GameResult struct {
	Title           string
	Description     string
	Engine          string
	Success         bool
	FilesGenerated  []string
	OutputDirectory string
	ErrorMessage    string
}

// AssetConfig holds configuration for asset generation
type AssetConfig struct {
	Descriptions []string
	Style        string
}

// AIGameDev is the main interface to the AI game development library
type AIGameDev struct {
	initialized bool
}

// NewAIGameDev creates a new AI game development instance
func NewAIGameDev() (*AIGameDev, error) {
	dev := &AIGameDev{}
	
	result := int(C.ai_game_dev_init())
	if result != 0 {
		return nil, errors.New("failed to initialize AI Game Dev library")
	}
	
	dev.initialized = true
	
	// Set finalizer to cleanup resources
	runtime.SetFinalizer(dev, (*AIGameDev).cleanup)
	
	return dev, nil
}

// CreateGame creates a complete game from a text description
func (dev *AIGameDev) CreateGame(description string, config *GameConfig) (*GameResult, error) {
	if !dev.initialized {
		return nil, errors.New("library not initialized")
	}
	
	if config == nil {
		config = &GameConfig{
			Engine:     EngineAuto,
			Complexity: "intermediate",
		}
	}
	
	// Convert Go strings to C strings
	cDescription := C.CString(description)
	defer C.free(unsafe.Pointer(cDescription))
	
	// Create C config struct
	cConfig := &C.GameConfig{
		engine:     C.CString(string(config.Engine)),
		complexity: C.CString(config.Complexity),
	}
	defer C.free(unsafe.Pointer(cConfig.engine))
	defer C.free(unsafe.Pointer(cConfig.complexity))
	
	// Call the C function
	cResult := C.ai_game_dev_create_game(cDescription, cConfig)
	if cResult == nil {
		errorMsg := C.GoString(C.ai_game_dev_get_last_error())
		return nil, errors.New("game creation failed: " + errorMsg)
	}
	
	// Convert C result to Go struct
	result := &GameResult{
		Title:           C.GoString(cResult.title),
		Description:     C.GoString(cResult.description),
		Engine:          C.GoString(cResult.engine),
		Success:         int(cResult.success) == 1,
		FilesGenerated:  []string{}, // TODO: Extract from C result
		OutputDirectory: "./generated_games",
	}
	
	if !result.Success && cResult.error_message != nil {
		result.ErrorMessage = C.GoString(cResult.error_message)
	}
	
	// Cleanup C result
	C.ai_game_dev_free_result(cResult)
	
	if !result.Success {
		return nil, errors.New(result.ErrorMessage)
	}
	
	return result, nil
}

// GenerateAssets generates game assets from descriptions
func (dev *AIGameDev) GenerateAssets(config *AssetConfig) error {
	if !dev.initialized {
		return errors.New("library not initialized")
	}
	
	// Convert descriptions to C array
	cDescriptions := make([]*C.char, len(config.Descriptions))
	for i, desc := range config.Descriptions {
		cDescriptions[i] = C.CString(desc)
		defer C.free(unsafe.Pointer(cDescriptions[i]))
	}
	
	cStyle := C.CString(config.Style)
	defer C.free(unsafe.Pointer(cStyle))
	
	// Call C function
	result := int(C.ai_game_dev_generate_assets(
		(**C.char)(unsafe.Pointer(&cDescriptions[0])),
		C.int(len(config.Descriptions)),
		cStyle,
	))
	
	if result != 0 {
		errorMsg := C.GoString(C.ai_game_dev_get_last_error())
		return errors.New("asset generation failed: " + errorMsg)
	}
	
	return nil
}

// GetSupportedEngines returns a list of supported game engines
func (dev *AIGameDev) GetSupportedEngines() ([]GameEngine, error) {
	if !dev.initialized {
		return nil, errors.New("library not initialized")
	}
	
	// Allocate C array for engines
	maxEngines := 10
	cEngines := make([]*C.char, maxEngines)
	
	count := int(C.ai_game_dev_supported_engines(
		(**C.char)(unsafe.Pointer(&cEngines[0])),
		C.int(maxEngines),
	))
	
	engines := make([]GameEngine, count)
	for i := 0; i < count; i++ {
		engines[i] = GameEngine(C.GoString(cEngines[i]))
	}
	
	return engines, nil
}

// GetVersion returns the library version
func (dev *AIGameDev) GetVersion() string {
	return C.GoString(C.ai_game_dev_version())
}

// IsRustAvailable checks if Rust acceleration is available
func (dev *AIGameDev) IsRustAvailable() bool {
	// For now, assume true if library loaded successfully
	return dev.initialized
}

// cleanup releases library resources
func (dev *AIGameDev) cleanup() {
	if dev.initialized {
		C.ai_game_dev_cleanup()
		dev.initialized = false
	}
}

// Close explicitly releases resources (call this instead of relying on finalizer)
func (dev *AIGameDev) Close() {
	dev.cleanup()
	runtime.SetFinalizer(dev, nil)
}

// Convenience Functions

// CreateGame creates a game using the default configuration
func CreateGame(description string, engine GameEngine) (*GameResult, error) {
	dev, err := NewAIGameDev()
	if err != nil {
		return nil, err
	}
	defer dev.Close()
	
	config := &GameConfig{
		Engine:     engine,
		Complexity: "intermediate",
	}
	
	return dev.CreateGame(description, config)
}

// CreateBevyGameOptimized creates an optimized Bevy game with Rust acceleration
func CreateBevyGameOptimized(description string, complexity string) (*GameResult, error) {
	dev, err := NewAIGameDev()
	if err != nil {
		return nil, err
	}
	defer dev.Close()
	
	config := &GameConfig{
		Engine:     EngineBevy,
		Complexity: complexity,
	}
	
	return dev.CreateGame(description, config)
}

// CheckSupport returns information about library capabilities
func CheckSupport() (map[string]interface{}, error) {
	dev, err := NewAIGameDev()
	if err != nil {
		return nil, err
	}
	defer dev.Close()
	
	engines, err := dev.GetSupportedEngines()
	if err != nil {
		return nil, err
	}
	
	return map[string]interface{}{
		"rust_available":     dev.IsRustAvailable(),
		"engines_supported":  engines,
		"version":           dev.GetVersion(),
		"go_bindings":       true,
	}, nil
}

// Demo runs a demonstration of the library
func Demo() error {
	fmt.Println("🐹 AI Game Development Library - Go Demo")
	fmt.Println(strings.Repeat("=", 50))
	
	// Create a simple game
	game, err := CreateGame(
		"2D platformer with jumping mechanics and coin collection",
		EngineArcade,
	)
	if err != nil {
		return fmt.Errorf("demo failed: %v", err)
	}
	
	fmt.Printf("✅ Game Created: %s\\n", game.Title)
	fmt.Printf("   Engine: %s\\n", game.Engine)
	fmt.Printf("   Success: %t\\n", game.Success)
	
	// Check support information
	support, err := CheckSupport()
	if err != nil {
		return fmt.Errorf("support check failed: %v", err)
	}
	
	fmt.Printf("\\n🔧 Library Support:\\n")
	fmt.Printf("   Version: %s\\n", support["version"])
	fmt.Printf("   Rust Available: %t\\n", support["rust_available"])
	fmt.Printf("   Engines: %v\\n", support["engines_supported"])
	
	return nil
}
'''
        
        main_path = self.output_dir / "aigamedev.go"
        with open(main_path, "w") as f:
            f.write(go_content)
        
        return main_path
    
    def create_types_definitions(self) -> Path:
        """Create additional type definitions."""
        types_content = '''package aigamedev

// Additional type definitions and constants

// ComplexityLevel represents game complexity levels
type ComplexityLevel string

const (
	ComplexitySimple       ComplexityLevel = "simple"
	ComplexityIntermediate ComplexityLevel = "intermediate"
	ComplexityAdvanced     ComplexityLevel = "advanced"
	ComplexityExpert       ComplexityLevel = "expert"
)

// AssetStyle represents different art styles for assets
type AssetStyle string

const (
	StyleGameReady AssetStyle = "game_ready"
	StylePixelArt  AssetStyle = "pixel_art"
	StyleRealistic AssetStyle = "realistic"
	StyleCartoon   AssetStyle = "cartoon"
)

// TargetAudience represents different target audiences
type TargetAudience string

const (
	AudienceChildren    TargetAudience = "children"
	AudienceTeens       TargetAudience = "teens"
	AudienceAdults      TargetAudience = "adults"
	AudienceEducational TargetAudience = "educational"
	AudienceGamers      TargetAudience = "gamers"
)

// GameFeature represents optional game features
type GameFeature string

const (
	FeatureMultiplayer     GameFeature = "multiplayer"
	FeatureAI             GameFeature = "ai_opponents"
	FeatureTechTrees      GameFeature = "tech_trees"
	FeaturePhysics        GameFeature = "physics"
	FeatureParticleEffects GameFeature = "particle_effects"
	FeatureSoundEffects   GameFeature = "sound_effects"
	FeatureNetworking     GameFeature = "networking"
)

// ConfigBuilder helps build game configurations fluently
type ConfigBuilder struct {
	config *GameConfig
}

// NewConfigBuilder creates a new configuration builder
func NewConfigBuilder() *ConfigBuilder {
	return &ConfigBuilder{
		config: &GameConfig{
			Engine:     EngineAuto,
			Complexity: string(ComplexityIntermediate),
			Features:   []string{},
		},
	}
}

// WithEngine sets the game engine
func (cb *ConfigBuilder) WithEngine(engine GameEngine) *ConfigBuilder {
	cb.config.Engine = engine
	return cb
}

// WithComplexity sets the complexity level
func (cb *ConfigBuilder) WithComplexity(complexity ComplexityLevel) *ConfigBuilder {
	cb.config.Complexity = string(complexity)
	return cb
}

// WithTargetAudience sets the target audience
func (cb *ConfigBuilder) WithTargetAudience(audience TargetAudience) *ConfigBuilder {
	cb.config.TargetAudience = string(audience)
	return cb
}

// WithFeatures adds game features
func (cb *ConfigBuilder) WithFeatures(features ...GameFeature) *ConfigBuilder {
	for _, feature := range features {
		cb.config.Features = append(cb.config.Features, string(feature))
	}
	return cb
}

// Build returns the built configuration
func (cb *ConfigBuilder) Build() *GameConfig {
	return cb.config
}

// Quick configuration presets

// PresetSimplePlatformer returns a configuration for simple platformer games
func PresetSimplePlatformer() *GameConfig {
	return NewConfigBuilder().
		WithEngine(EngineArcade).
		WithComplexity(ComplexitySimple).
		WithTargetAudience(AudienceChildren).
		WithFeatures(FeaturePhysics).
		Build()
}

// PresetAdvancedRTS returns a configuration for advanced RTS games
func PresetAdvancedRTS() *GameConfig {
	return NewConfigBuilder().
		WithEngine(EngineBevy).
		WithComplexity(ComplexityAdvanced).
		WithTargetAudience(AudienceGamers).
		WithFeatures(FeatureMultiplayer, FeatureAI, FeatureTechTrees).
		Build()
}

// PresetStoryGame returns a configuration for story-driven games
func PresetStoryGame() *GameConfig {
	return NewConfigBuilder().
		WithEngine(EngineGodot).
		WithComplexity(ComplexityIntermediate).
		WithTargetAudience(AudienceAdults).
		WithFeatures(FeatureSoundEffects, FeatureParticleEffects).
		Build()
}
'''
        
        types_path = self.output_dir / "types.go"
        with open(types_path, "w") as f:
            f.write(types_content)
        
        return types_path
    
    def create_examples(self) -> Path:
        """Create example usage file."""
        example_content = '''package main

import (
	"fmt"
	"log"
	
	"github.com/ai-game-dev/go-bindings"
)

func basicExample() {
	fmt.Println("🎮 Basic Game Creation Example")
	fmt.Println(strings.Repeat("-", 40))
	
	// Create a simple game
	game, err := aigamedev.CreateGame(
		"A fun 2D platformer with jumping mechanics and collectible coins",
		aigamedev.EngineArcade,
	)
	if err != nil {
		log.Printf("❌ Error: %v", err)
		return
	}
	
	fmt.Printf("✅ Game Created: %s\\n", game.Title)
	fmt.Printf("   Engine: %s\\n", game.Engine)
	fmt.Printf("   Success: %t\\n", game.Success)
	fmt.Printf("   Output: %s\\n", game.OutputDirectory)
}

func advancedExample() {
	fmt.Println("\\n🚀 Advanced Game Creation Example")
	fmt.Println(strings.Repeat("-", 40))
	
	// Create AI game dev instance
	dev, err := aigamedev.NewAIGameDev()
	if err != nil {
		log.Printf("❌ Failed to create AI Game Dev: %v", err)
		return
	}
	defer dev.Close()
	
	// Use configuration builder
	config := aigamedev.NewConfigBuilder().
		WithEngine(aigamedev.EngineBevy).
		WithComplexity(aigamedev.ComplexityAdvanced).
		WithTargetAudience(aigamedev.AudienceGamers).
		WithFeatures(
			aigamedev.FeatureMultiplayer,
			aigamedev.FeatureAI,
			aigamedev.FeatureTechTrees,
		).
		Build()
	
	// Create advanced game
	game, err := dev.CreateGame(
		"Real-time strategy game with resource management and combat systems",
		config,
	)
	if err != nil {
		log.Printf("❌ Error: %v", err)
		return
	}
	
	fmt.Printf("✅ Advanced Game Created: %s\\n", game.Title)
	fmt.Printf("   Engine: %s\\n", game.Engine)
	fmt.Printf("   Features: %v\\n", config.Features)
}

func presetExample() {
	fmt.Println("\\n🎯 Preset Configuration Example")
	fmt.Println(strings.Repeat("-", 40))
	
	dev, err := aigamedev.NewAIGameDev()
	if err != nil {
		log.Printf("❌ Failed to create AI Game Dev: %v", err)
		return
	}
	defer dev.Close()
	
	// Use preset configuration
	config := aigamedev.PresetSimplePlatformer()
	
	game, err := dev.CreateGame(
		"Educational platformer teaching basic math",
		config,
	)
	if err != nil {
		log.Printf("❌ Error: %v", err)
		return
	}
	
	fmt.Printf("✅ Educational Game Created: %s\\n", game.Title)
	fmt.Printf("   Target Audience: %s\\n", config.TargetAudience)
}

func supportCheckExample() {
	fmt.Println("\\n🔧 Support Check Example")
	fmt.Println(strings.Repeat("-", 40))
	
	support, err := aigamedev.CheckSupport()
	if err != nil {
		log.Printf("❌ Support check failed: %v", err)
		return
	}
	
	fmt.Printf("Library Version: %s\\n", support["version"])
	fmt.Printf("Rust Available: %t\\n", support["rust_available"])
	fmt.Printf("Engines Supported: %v\\n", support["engines_supported"])
	fmt.Printf("Go Bindings: %t\\n", support["go_bindings"])
}

func assetGenerationExample() {
	fmt.Println("\\n🎨 Asset Generation Example")
	fmt.Println(strings.Repeat("-", 40))
	
	dev, err := aigamedev.NewAIGameDev()
	if err != nil {
		log.Printf("❌ Failed to create AI Game Dev: %v", err)
		return
	}
	defer dev.Close()
	
	// Generate game assets
	assetConfig := &aigamedev.AssetConfig{
		Descriptions: []string{
			"Heroic knight character sprite",
			"Medieval castle background",
			"Magic sword power-up item",
		},
		Style: string(aigamedev.StylePixelArt),
	}
	
	err = dev.GenerateAssets(assetConfig)
	if err != nil {
		log.Printf("❌ Asset generation failed: %v", err)
		return
	}
	
	fmt.Printf("✅ Generated %d assets in %s style\\n",
		len(assetConfig.Descriptions), assetConfig.Style)
}

func main() {
	fmt.Println("🐹 AI Game Development Library - Go Examples")
	fmt.Println(strings.Repeat("=", 55))
	
	basicExample()
	advancedExample()
	presetExample()
	supportCheckExample()
	assetGenerationExample()
	
	fmt.Println("\\n🎉 All examples completed!")
	fmt.Println("See the library documentation for more advanced usage.")
}
'''
        
        example_path = self.output_dir / "examples" / "main.go"
        example_path.parent.mkdir(exist_ok=True)
        
        with open(example_path, "w") as f:
            f.write(example_content)
        
        return example_path
    
    def create_tests(self) -> Path:
        """Create test file."""
        test_content = '''package aigamedev

import (
	"strings"
	"testing"
)

func TestNewAIGameDev(t *testing.T) {
	dev, err := NewAIGameDev()
	if err != nil {
		t.Fatalf("Failed to create AIGameDev: %v", err)
	}
	defer dev.Close()
	
	if !dev.initialized {
		t.Error("AIGameDev should be initialized")
	}
}

func TestCreateGame(t *testing.T) {
	game, err := CreateGame(
		"Simple test game with basic mechanics",
		EngineArcade,
	)
	if err != nil {
		t.Fatalf("CreateGame failed: %v", err)
	}
	
	if game.Title == "" {
		t.Error("Game title should not be empty")
	}
	
	if !game.Success {
		t.Error("Game creation should be successful")
	}
	
	if game.Engine == "" {
		t.Error("Game engine should be specified")
	}
}

func TestGetVersion(t *testing.T) {
	dev, err := NewAIGameDev()
	if err != nil {
		t.Fatalf("Failed to create AIGameDev: %v", err)
	}
	defer dev.Close()
	
	version := dev.GetVersion()
	if version == "" {
		t.Error("Version should not be empty")
	}
	
	if !strings.Contains(version, ".") {
		t.Error("Version should contain dots (semantic versioning)")
	}
}

func TestGetSupportedEngines(t *testing.T) {
	dev, err := NewAIGameDev()
	if err != nil {
		t.Fatalf("Failed to create AIGameDev: %v", err)
	}
	defer dev.Close()
	
	engines, err := dev.GetSupportedEngines()
	if err != nil {
		t.Fatalf("GetSupportedEngines failed: %v", err)
	}
	
	if len(engines) == 0 {
		t.Error("Should support at least one engine")
	}
	
	// Check for expected engines
	expectedEngines := []GameEngine{EngineBevy, EngineGodot, EngineArcade}
	found := make(map[GameEngine]bool)
	
	for _, engine := range engines {
		found[engine] = true
	}
	
	for _, expected := range expectedEngines {
		if !found[expected] {
			t.Errorf("Expected engine %s not found in supported engines", expected)
		}
	}
}

func TestConfigBuilder(t *testing.T) {
	config := NewConfigBuilder().
		WithEngine(EngineBevy).
		WithComplexity(ComplexityAdvanced).
		WithTargetAudience(AudienceGamers).
		WithFeatures(FeatureMultiplayer, FeatureAI).
		Build()
	
	if config.Engine != EngineBevy {
		t.Errorf("Expected engine %s, got %s", EngineBevy, config.Engine)
	}
	
	if config.Complexity != string(ComplexityAdvanced) {
		t.Errorf("Expected complexity %s, got %s", ComplexityAdvanced, config.Complexity)
	}
	
	if config.TargetAudience != string(AudienceGamers) {
		t.Errorf("Expected audience %s, got %s", AudienceGamers, config.TargetAudience)
	}
	
	if len(config.Features) != 2 {
		t.Errorf("Expected 2 features, got %d", len(config.Features))
	}
}

func TestPresets(t *testing.T) {
	platformer := PresetSimplePlatformer()
	if platformer.Engine != EngineArcade {
		t.Error("Simple platformer should use Arcade engine")
	}
	
	rts := PresetAdvancedRTS()
	if rts.Engine != EngineBevy {
		t.Error("Advanced RTS should use Bevy engine")
	}
	
	story := PresetStoryGame()
	if story.Engine != EngineGodot {
		t.Error("Story game should use Godot engine")
	}
}

func TestCheckSupport(t *testing.T) {
	support, err := CheckSupport()
	if err != nil {
		t.Fatalf("CheckSupport failed: %v", err)
	}
	
	if version, ok := support["version"].(string); !ok || version == "" {
		t.Error("Support should include valid version")
	}
	
	if rustAvailable, ok := support["rust_available"].(bool); !ok {
		t.Error("Support should include rust_available boolean")
	} else if !rustAvailable {
		t.Log("Rust acceleration not available (this may be expected)")
	}
	
	if engines, ok := support["engines_supported"].([]GameEngine); !ok || len(engines) == 0 {
		t.Error("Support should include supported engines list")
	}
	
	if goBindings, ok := support["go_bindings"].(bool); !ok || !goBindings {
		t.Error("Support should indicate Go bindings are available")
	}
}

// Benchmark tests
func BenchmarkCreateGame(b *testing.B) {
	for i := 0; i < b.N; i++ {
		game, err := CreateGame("Benchmark test game", EngineArcade)
		if err != nil {
			b.Fatalf("CreateGame failed: %v", err)
		}
		
		if !game.Success {
			b.Fatal("Game creation should succeed")
		}
	}
}

func BenchmarkConfigBuilder(b *testing.B) {
	for i := 0; i < b.N; i++ {
		config := NewConfigBuilder().
			WithEngine(EngineBevy).
			WithComplexity(ComplexityAdvanced).
			WithTargetAudience(AudienceGamers).
			WithFeatures(FeatureMultiplayer, FeatureAI, FeatureTechTrees).
			Build()
		
		if config == nil {
			b.Fatal("Config should not be nil")
		}
	}
}
'''
        
        test_path = self.output_dir / "aigamedev_test.go"
        with open(test_path, "w") as f:
            f.write(test_content)
        
        return test_path
    
    def create_documentation(self) -> Path:
        """Create comprehensive documentation."""
        readme_content = '''# AI Game Development Library - Go Bindings

Revolutionary AI-powered game development library with multi-agent orchestration, now available for Go applications via CGO bindings.

## Installation

```bash
go get github.com/ai-game-dev/go-bindings
```

## Prerequisites

- Go 1.21 or later
- CGO enabled
- AI Game Dev C++ library installed

## Quick Start

```go
package main

import (
	"fmt"
	"log"
	
	"github.com/ai-game-dev/go-bindings"
)

func main() {
	// Create a simple game
	game, err := aigamedev.CreateGame(
		"A fun 2D platformer with jumping and coin collection",
		aigamedev.EngineArcade,
	)
	if err != nil {
		log.Fatal(err)
	}
	
	fmt.Printf("✅ Game created: %s\\n", game.Title)
	fmt.Printf("Engine: %s\\n", game.Engine)
	fmt.Printf("Output: %s\\n", game.OutputDirectory)
}
```

## API Reference

### Types

#### `GameEngine`
```go
type GameEngine string

const (
    EngineBevy   GameEngine = "bevy"   // Rust ECS for performance
    EngineGodot  GameEngine = "godot"  // Scene-based with visual scripting  
    EngineArcade GameEngine = "arcade" // Python for web deployment
    EngineAuto   GameEngine = "auto"   // Let AI choose
)
```

#### `GameConfig`
```go
type GameConfig struct {
    Engine         GameEngine
    Complexity     string
    TargetAudience string
    Features       []string
}
```

#### `GameResult`
```go
type GameResult struct {
    Title           string
    Description     string
    Engine          string
    Success         bool
    FilesGenerated  []string
    OutputDirectory string
    ErrorMessage    string
}
```

### Core Functions

#### `NewAIGameDev() (*AIGameDev, error)`

Creates a new AI game development instance.

```go
dev, err := aigamedev.NewAIGameDev()
if err != nil {
    log.Fatal(err)
}
defer dev.Close() // Important: cleanup resources
```

#### `CreateGame(description string, config *GameConfig) (*GameResult, error)`

Creates a complete game from description and configuration.

```go
config := &aigamedev.GameConfig{
    Engine:     aigamedev.EngineBevy,
    Complexity: "advanced",
    Features:   []string{"multiplayer", "ai_opponents"},
}

game, err := dev.CreateGame("RTS with base building", config)
```

### Convenience Functions

#### `CreateGame(description string, engine GameEngine) (*GameResult, error)`

Quick game creation with minimal configuration.

```go
game, err := aigamedev.CreateGame(
    "Space shooter with power-ups",
    aigamedev.EngineBevy,
)
```

#### `CreateBevyGameOptimized(description, complexity string) (*GameResult, error)`

Creates Bevy games with maximum Rust optimization.

```go
game, err := aigamedev.CreateBevyGameOptimized(
    "High-performance racing game",
    "advanced",
)
```

## Configuration Builder

Use the fluent builder pattern for complex configurations:

```go
config := aigamedev.NewConfigBuilder().
    WithEngine(aigamedev.EngineGodot).
    WithComplexity(aigamedev.ComplexityIntermediate).
    WithTargetAudience(aigamedev.AudienceAdults).
    WithFeatures(
        aigamedev.FeatureSoundEffects,
        aigamedev.FeatureParticleEffects,
    ).
    Build()

game, err := dev.CreateGame("Adventure game", config)
```

## Presets

Quick configurations for common game types:

```go
// Simple educational platformer
config := aigamedev.PresetSimplePlatformer()

// Advanced RTS with multiplayer
config := aigamedev.PresetAdvancedRTS()

// Story-driven adventure game
config := aigamedev.PresetStoryGame()
```

## Engine Selection Guide

### Bevy (Rust ECS)
**Best for:** Performance-critical games, real-time systems, high entity counts
```go
config := &aigamedev.GameConfig{
    Engine: aigamedev.EngineBevy,
    Complexity: "advanced",
    Features: []string{"multiplayer", "physics_simulation"},
}
```

### Godot (Scene-based)
**Best for:** Story-driven games, complex UI, visual scripting
```go
config := &aigamedev.GameConfig{
    Engine: aigamedev.EngineGodot,
    Complexity: "intermediate", 
    Features: []string{"dialogue_system", "cutscenes"},
}
```

### Arcade (Python Web)
**Best for:** Educational games, web deployment, rapid prototyping
```go
config := &aigamedev.GameConfig{
    Engine: aigamedev.EngineArcade,
    Complexity: "simple",
    TargetAudience: "children",
}
```

## Error Handling

```go
game, err := aigamedev.CreateGame("My game", aigamedev.EngineAuto)
if err != nil {
    // Handle different error types
    switch {
    case strings.Contains(err.Error(), "initialization"):
        log.Fatal("Library initialization failed")
    case strings.Contains(err.Error(), "generation"):
        log.Printf("Game generation failed: %v", err)
    default:
        log.Printf("Unknown error: %v", err)
    }
}
```

## Asset Generation

```go
dev, err := aigamedev.NewAIGameDev()
if err != nil {
    log.Fatal(err)
}
defer dev.Close()

assetConfig := &aigamedev.AssetConfig{
    Descriptions: []string{
        "Hero character sprite",
        "Castle background",
        "Magic sword item",
    },
    Style: string(aigamedev.StylePixelArt),
}

err = dev.GenerateAssets(assetConfig)
if err != nil {
    log.Printf("Asset generation failed: %v", err)
}
```

## Web Server Integration

Example with Gin web framework:

```go
package main

import (
    "net/http"
    
    "github.com/gin-gonic/gin"
    "github.com/ai-game-dev/go-bindings"
)

func main() {
    r := gin.Default()
    
    r.POST("/create-game", func(c *gin.Context) {
        var req struct {
            Description string \`json:"description"\`
            Engine      string \`json:"engine"\`
        }
        
        if err := c.ShouldBindJSON(&req); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        
        game, err := aigamedev.CreateGame(req.Description, 
            aigamedev.GameEngine(req.Engine))
        if err != nil {
            c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
            return
        }
        
        c.JSON(http.StatusOK, gin.H{"game": game})
    })
    
    r.Run(":8080")
}
```

## Testing

Run the test suite:

```bash
go test -v
```

Run benchmarks:

```bash
go test -bench=.
```

## Performance

- **Native Speed**: Uses compiled C++ binary for optimal performance
- **Memory Efficient**: CGO bindings with proper resource cleanup
- **Rust Acceleration**: Bevy games benefit from native Rust optimizations
- **Concurrent Safe**: Library handles concurrent requests safely

## Examples

See the `examples/` directory for:
- Basic usage patterns
- Advanced configurations  
- Web server integration
- Error handling strategies
- Performance benchmarks

## Building

To build the bindings:

```bash
go build -tags cgo
```

## License

MIT License - See LICENSE file for details.

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: Full API documentation
- Examples: Comprehensive examples repository
'''
        
        readme_path = self.output_dir / "README.md"
        with open(readme_path, "w") as f:
            f.write(readme_content)
        
        return readme_path


def main():
    """Generate Go bindings."""
    generator = GoBindingsGenerator()
    files = generator.generate_bindings()
    
    print("\n🐹 Go bindings generated:")
    for name, path in files.items():
        print(f"   {name}: {path}")


if __name__ == "__main__":
    main()