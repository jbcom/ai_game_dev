/**
 * @file ai_game_dev.hpp
 * @brief C++ bindings for AI Game Development library
 * 
 * Provides a modern C++ interface to the AI game development system
 * with RAII resource management and exception safety.
 */

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <future>
#include <optional>
#include <functional>

extern "C" {
    // C interface functions from Go library
    int ai_game_dev_init();
    int ai_game_dev_create_game(const char* description, const char* config);
    const char* ai_game_dev_get_result(int instance_id);
    const char* ai_game_dev_supported_engines();
    const char* ai_game_dev_version();
    const char* ai_game_dev_get_last_error();
    void ai_game_dev_cleanup();
}

namespace aigamedev {

// Forward declarations
class GameResult;
class GameConfig;

/**
 * @brief Game engine enumeration
 */
enum class GameEngine {
    Bevy,
    Godot,
    Arcade,
    Auto
};

/**
 * @brief Exception thrown by AI Game Dev operations
 */
class AIGameDevException : public std::runtime_error {
public:
    explicit AIGameDevException(const std::string& message)
        : std::runtime_error("AI Game Dev Error: " + message) {}
};

/**
 * @brief Game configuration structure
 */
struct GameConfig {
    GameEngine engine = GameEngine::Auto;
    std::string complexity = "intermediate";
    std::string target_audience;
    std::vector<std::string> features;
    
    // Convert to JSON string for C interface
    std::string to_json() const;
    
    // Builder pattern methods
    GameConfig& with_engine(GameEngine eng) { engine = eng; return *this; }
    GameConfig& with_complexity(const std::string& comp) { complexity = comp; return *this; }
    GameConfig& with_target_audience(const std::string& audience) { target_audience = audience; return *this; }
    GameConfig& with_features(const std::vector<std::string>& feat) { features = feat; return *this; }
    GameConfig& add_feature(const std::string& feature) { features.push_back(feature); return *this; }
};

/**
 * @brief Game generation result
 */
struct GameResult {
    std::string title;
    std::string description;
    std::string engine;
    bool success = false;
    std::vector<std::string> files_generated;
    std::string output_directory;
    std::string error_message;
    
    // Parse from JSON string
    static GameResult from_json(const std::string& json);
};

/**
 * @brief Main AI Game Development class with RAII resource management
 */
class AIGameDev {
public:
    /**
     * @brief Constructor - initializes the AI game development system
     * @throws AIGameDevException if initialization fails
     */
    AIGameDev();
    
    /**
     * @brief Destructor - automatically cleans up resources
     */
    ~AIGameDev();
    
    // Non-copyable but moveable
    AIGameDev(const AIGameDev&) = delete;
    AIGameDev& operator=(const AIGameDev&) = delete;
    AIGameDev(AIGameDev&&) = default;
    AIGameDev& operator=(AIGameDev&&) = default;
    
    /**
     * @brief Create a game synchronously
     * @param description Natural language description of the game
     * @param config Game configuration options
     * @return GameResult containing the generated game information
     * @throws AIGameDevException if game creation fails
     */
    GameResult create_game(const std::string& description, const GameConfig& config = {});
    
    /**
     * @brief Create a game asynchronously
     * @param description Natural language description of the game
     * @param config Game configuration options
     * @return Future containing the GameResult
     */
    std::future<GameResult> create_game_async(const std::string& description, const GameConfig& config = {});
    
    /**
     * @brief Get supported game engines
     * @return Vector of supported engine names
     */
    std::vector<std::string> get_supported_engines() const;
    
    /**
     * @brief Get library version
     * @return Version string
     */
    std::string get_version() const;
    
    /**
     * @brief Get last error message
     * @return Error message string
     */
    std::string get_last_error() const;
    
    /**
     * @brief Check if the system is properly initialized
     * @return True if initialized successfully
     */
    bool is_initialized() const { return initialized_; }

private:
    bool initialized_;
    
    // Internal helper methods
    void ensure_initialized() const;
    GameResult create_game_internal(const std::string& description, const GameConfig& config);
};

/**
 * @brief Specialized Bevy game generator with C++ integration
 */
class BevyGameGenerator {
public:
    explicit BevyGameGenerator(AIGameDev& ai_dev) : ai_dev_(ai_dev) {}
    
    /**
     * @brief Generate high-performance Bevy game with Rust optimizations
     */
    GameResult create_optimized_game(const std::string& description, const GameConfig& config = {});
    
    /**
     * @brief Generate Bevy ECS components from description
     */
    std::vector<std::string> generate_ecs_components(const std::string& description);
    
    /**
     * @brief Generate Bevy systems from game requirements
     */
    std::vector<std::string> generate_systems(const std::string& requirements);

private:
    AIGameDev& ai_dev_;
};

/**
 * @brief Specialized Godot game generator
 */
class GodotGameGenerator {
public:
    explicit GodotGameGenerator(AIGameDev& ai_dev) : ai_dev_(ai_dev) {}
    
    /**
     * @brief Generate Godot game with scene-based architecture
     */
    GameResult create_scene_based_game(const std::string& description, const GameConfig& config = {});
    
    /**
     * @brief Generate GDScript files from description
     */
    std::vector<std::string> generate_gdscript_files(const std::string& description);

private:
    AIGameDev& ai_dev_;
};

// Utility functions

/**
 * @brief Convert GameEngine enum to string
 */
std::string engine_to_string(GameEngine engine);

/**
 * @brief Convert string to GameEngine enum
 */
std::optional<GameEngine> string_to_engine(const std::string& engine_str);

/**
 * @brief Configuration builder for common game types
 */
namespace presets {
    GameConfig simple_platformer();
    GameConfig advanced_rts();
    GameConfig story_driven_adventure();
    GameConfig educational_game();
    GameConfig web_casual_game();
}

/**
 * @brief Convenience functions for quick game creation
 */
GameResult create_game(const std::string& description, GameEngine engine = GameEngine::Auto);
GameResult create_bevy_game(const std::string& description, const std::string& complexity = "intermediate");
GameResult create_godot_game(const std::string& description, const std::string& complexity = "intermediate");
GameResult create_arcade_game(const std::string& description, const std::string& complexity = "simple");

} // namespace aigamedev