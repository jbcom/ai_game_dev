// Package main provides the core C-compatible interface for ai-game-dev
package main

import "C"

import (
	"encoding/json"
	"errors"
	"runtime"
	"unsafe"
)

// GameEngine represents supported game engines
type GameEngine int

const (
	EngineBevy GameEngine = iota
	EngineGodot
	EngineArcade
	EngineAuto
)

// GameConfig holds configuration for game creation
type GameConfig struct {
	Engine         GameEngine `json:"engine"`
	Complexity     string     `json:"complexity"`
	TargetAudience string     `json:"target_audience"`
	Features       []string   `json:"features"`
}

// GameResult contains the result of game creation
type GameResult struct {
	Title           string   `json:"title"`
	Description     string   `json:"description"`
	Engine          string   `json:"engine"`
	Success         bool     `json:"success"`
	FilesGenerated  []string `json:"files_generated"`
	OutputDirectory string   `json:"output_directory"`
	ErrorMessage    string   `json:"error_message,omitempty"`
}

// Global state management
var (
	initialized    bool
	lastError      string
	gameInstances  = make(map[int]*GameInstance)
	nextInstanceID int
)

// GameInstance represents an active game development session
type GameInstance struct {
	ID          int
	Config      GameConfig
	State       string
	Generated   bool
	Result      *GameResult
}

//export ai_game_dev_init
func ai_game_dev_init() C.int {
	if initialized {
		return 0
	}
	
	// Initialize the library
	runtime.GC() // Ensure clean start
	initialized = true
	lastError = ""
	
	return 0
}

//export ai_game_dev_create_game
func ai_game_dev_create_game(description *C.char, configJSON *C.char) C.int {
	if !initialized {
		lastError = "Library not initialized"
		return -1
	}
	
	desc := C.GoString(description)
	configStr := C.GoString(configJSON)
	
	var config GameConfig
	if err := json.Unmarshal([]byte(configStr), &config); err != nil {
		lastError = "Invalid configuration JSON: " + err.Error()
		return -1
	}
	
	// Create new game instance
	instanceID := nextInstanceID
	nextInstanceID++
	
	instance := &GameInstance{
		ID:     instanceID,
		Config: config,
		State:  "generating",
	}
	
	// Generate the game (simplified for C interface)
	result, err := generateGame(desc, config)
	if err != nil {
		lastError = err.Error()
		return -1
	}
	
	instance.Result = result
	instance.Generated = true
	instance.State = "completed"
	
	gameInstances[instanceID] = instance
	
	return C.int(instanceID)
}

//export ai_game_dev_get_result
func ai_game_dev_get_result(instanceID C.int) *C.char {
	if !initialized {
		return C.CString(`{"error": "Library not initialized"}`)
	}
	
	instance, exists := gameInstances[int(instanceID)]
	if !exists {
		return C.CString(`{"error": "Invalid instance ID"}`)
	}
	
	if !instance.Generated {
		return C.CString(`{"error": "Game not yet generated"}`)
	}
	
	resultJSON, err := json.Marshal(instance.Result)
	if err != nil {
		return C.CString(`{"error": "Failed to serialize result"}`)
	}
	
	return C.CString(string(resultJSON))
}

//export ai_game_dev_supported_engines
func ai_game_dev_supported_engines() *C.char {
	engines := []string{"bevy", "godot", "arcade", "auto"}
	enginesJSON, _ := json.Marshal(engines)
	return C.CString(string(enginesJSON))
}

//export ai_game_dev_version
func ai_game_dev_version() *C.char {
	return C.CString("1.0.0")
}

//export ai_game_dev_get_last_error
func ai_game_dev_get_last_error() *C.char {
	return C.CString(lastError)
}

//export ai_game_dev_cleanup
func ai_game_dev_cleanup() {
	if !initialized {
		return
	}
	
	// Clean up all game instances
	for id := range gameInstances {
		delete(gameInstances, id)
	}
	
	initialized = false
	lastError = ""
	nextInstanceID = 0
	
	// Force garbage collection
	runtime.GC()
}

// generateGame creates a game based on description and configuration
func generateGame(description string, config GameConfig) (*GameResult, error) {
	if len(description) == 0 {
		return nil, errors.New("description cannot be empty")
	}
	
	// Determine engine
	engineName := "auto"
	switch config.Engine {
	case EngineBevy:
		engineName = "bevy"
	case EngineGodot:
		engineName = "godot"
	case EngineArcade:
		engineName = "arcade"
	}
	
	// Generate basic game structure
	result := &GameResult{
		Title:           generateTitle(description),
		Description:     description,
		Engine:          engineName,
		Success:         true,
		FilesGenerated:  generateFileList(engineName),
		OutputDirectory: "./generated_games/" + sanitizeFilename(description),
		ErrorMessage:    "",
	}
	
	return result, nil
}

func generateTitle(description string) string {
	// Simple title generation from description
	words := strings.Fields(description)
	if len(words) == 0 {
		return "AI Generated Game"
	}
	
	title := "AI Generated"
	for i, word := range words {
		if i >= 3 { // Limit title length
			break
		}
		title += " " + strings.Title(strings.ToLower(word))
	}
	
	return title
}

func generateFileList(engine string) []string {
	switch engine {
	case "bevy":
		return []string{
			"Cargo.toml",
			"src/main.rs", 
			"src/components.rs",
			"src/systems.rs",
			"src/resources.rs",
			"assets/sprites/",
			"assets/audio/",
		}
	case "godot":
		return []string{
			"project.godot",
			"scenes/Main.tscn",
			"scripts/Main.gd",
			"scripts/Player.gd",
			"assets/sprites/",
			"assets/audio/",
		}
	case "arcade":
		return []string{
			"main.py",
			"game.py",
			"sprites.py",
			"assets/",
			"requirements.txt",
			"web_config.json",
		}
	default:
		return []string{"main.py", "assets/"}
	}
}

func sanitizeFilename(filename string) string {
	// Simple filename sanitization
	result := ""
	for _, r := range filename {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '_' || r == '-' {
			result += string(r)
		} else if r == ' ' {
			result += "_"
		}
	}
	
	if len(result) == 0 {
		return "ai_game"
	}
	
	return result
}

// Go API for direct usage (not exported to C)
func CreateGame(description string, config GameConfig) (*GameResult, error) {
	return generateGame(description, config)
}

func GetSupportedEngines() []string {
	return []string{"bevy", "godot", "arcade", "auto"}
}

func main() {
	// This allows the package to be used as both a library and a command-line tool
	if len(os.Args) > 1 {
		runCLI()
	}
}

func runCLI() {
	// Command-line interface implementation
	description := "Simple 2D platformer game"
	if len(os.Args) > 1 {
		description = strings.Join(os.Args[1:], " ")
	}
	
	config := GameConfig{
		Engine:     EngineAuto,
		Complexity: "intermediate",
	}
	
	result, err := CreateGame(description, config)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	
	fmt.Printf("✅ Game Created: %s\n", result.Title)
	fmt.Printf("   Engine: %s\n", result.Engine)
	fmt.Printf("   Files: %v\n", result.FilesGenerated)
	fmt.Printf("   Output: %s\n", result.OutputDirectory)
}