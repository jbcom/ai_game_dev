# C++ Integration Guide

<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/1/18/ISO_C%2B%2B_Logo.svg" alt="C++ Logo" width="150"/>
  
  <h2>⚡ AI Game Development with C++</h2>
</div>

This guide shows how to integrate the AI Game Development library into C++ applications, providing high-performance native integration for systems programming and game engines.

## 🚀 Quick Start

### Installation

#### Using CMake FetchContent

```cmake
include(FetchContent)

FetchContent_Declare(
    ai-game-dev
    GIT_REPOSITORY https://github.com/ai-game-dev/cpp-bindings
    GIT_TAG v1.0.0
)

FetchContent_MakeAvailable(ai-game-dev)

target_link_libraries(your_target PRIVATE ai-game-dev-cpp)
```

#### Manual Installation

```bash
# Clone the repository
git clone https://github.com/ai-game-dev/cpp-bindings
cd cpp-bindings

# Build and install
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
sudo make install
```

### Basic Usage

```cpp
#include <ai_game_dev.hpp>
#include <iostream>

int main() {
    try {
        // Initialize the AI game development system
        aigamedev::AIGameDev ai_dev;
        
        // Create a simple game
        auto game = ai_dev.create_game(
            "2D platformer with jumping mechanics and collectible coins",
            aigamedev::presets::simple_platformer()
        );
        
        std::cout << "✅ Game created: " << game.title << std::endl;
        std::cout << "   Engine: " << game.engine << std::endl;
        std::cout << "   Files: " << game.files_generated.size() << std::endl;
        std::cout << "   Output: " << game.output_directory << std::endl;
        
        return 0;
    } catch (const aigamedev::AIGameDevException& e) {
        std::cerr << "❌ Error: " << e.what() << std::endl;
        return 1;
    }
}
```

## 🏗️ Architecture

The C++ bindings provide a modern C++17 interface with RAII resource management:

```
C++ Application
     ↓ (Modern C++ Interface)
C++ Wrapper Library (RAII, exceptions, futures)
     ↓ (C Interface)
Core Library (Go shared library)
```

## 🎮 Advanced Examples

### Asynchronous Game Creation

```cpp
#include <ai_game_dev.hpp>
#include <future>
#include <vector>
#include <iostream>

class GameFactory {
public:
    GameFactory() : ai_dev_() {}
    
    // Create multiple games concurrently
    std::vector<aigamedev::GameResult> create_games_batch(
        const std::vector<std::string>& descriptions
    ) {
        std::vector<std::future<aigamedev::GameResult>> futures;
        
        // Start all game creations asynchronously
        for (const auto& desc : descriptions) {
            futures.push_back(
                ai_dev_.create_game_async(desc)
            );
        }
        
        // Wait for all to complete
        std::vector<aigamedev::GameResult> results;
        results.reserve(futures.size());
        
        for (auto& future : futures) {
            results.push_back(future.get());
        }
        
        return results;
    }
    
    // Create game with timeout
    std::optional<aigamedev::GameResult> create_game_with_timeout(
        const std::string& description,
        std::chrono::seconds timeout
    ) {
        auto future = ai_dev_.create_game_async(description);
        
        if (future.wait_for(timeout) == std::future_status::ready) {
            return future.get();
        } else {
            return std::nullopt;
        }
    }

private:
    aigamedev::AIGameDev ai_dev_;
};

int main() {
    GameFactory factory;
    
    // Batch creation
    std::vector<std::string> game_descriptions = {
        "Space shooter with enemy waves",
        "Puzzle game with physics",
        "Racing game with multiple tracks"
    };
    
    auto games = factory.create_games_batch(game_descriptions);
    
    std::cout << "Created " << games.size() << " games:" << std::endl;
    for (const auto& game : games) {
        std::cout << "  - " << game.title << std::endl;
    }
    
    return 0;
}
```

### Game Engine Integration

#### Unreal Engine Integration

```cpp
// UnrealAIGameDev.h
#pragma once

#include "CoreMinimal.h"
#include "Engine/Engine.h"
#include "Async/AsyncWork.h"
#include <ai_game_dev.hpp>

UCLASS(BlueprintType, Blueprintable)
class YOURGAME_API UUnrealAIGameDev : public UObject {
    GENERATED_BODY()
    
public:
    UFUNCTION(BlueprintCallable, Category = "AI Game Dev")
    void CreateGameAsync(
        const FString& Description,
        const FString& Engine = TEXT("auto")
    );
    
    UFUNCTION(BlueprintImplementableEvent, Category = "AI Game Dev")
    void OnGameCreated(const FString& Title, const FString& OutputPath);
    
    UFUNCTION(BlueprintImplementableEvent, Category = "AI Game Dev") 
    void OnGameCreationFailed(const FString& Error);

private:
    class FCreateGameTask : public FNonAbandonableTask {
    public:
        FCreateGameTask(
            UUnrealAIGameDev* InOwner,
            FString InDescription,
            FString InEngine
        ) : Owner(InOwner), Description(InDescription), Engine(InEngine) {}
        
        void DoWork();
        
        FORCEINLINE TStatId GetStatId() const {
            RETURN_QUICK_DECLARE_CYCLE_STAT(FCreateGameTask, STATGROUP_ThreadPoolAsyncTasks);
        }
        
    private:
        UUnrealAIGameDev* Owner;
        FString Description;
        FString Engine;
    };
    
    friend class FCreateGameTask;
    aigamedev::AIGameDev ai_dev_;
};

// UnrealAIGameDev.cpp
#include "UnrealAIGameDev.h"

void UUnrealAIGameDev::CreateGameAsync(
    const FString& Description,
    const FString& Engine
) {
    // Start async task
    (new FAutoDeleteAsyncTask<FCreateGameTask>(
        this, Description, Engine
    ))->StartBackgroundTask();
}

void UUnrealAIGameDev::FCreateGameTask::DoWork() {
    try {
        // Convert engine string
        aigamedev::GameEngine engine = aigamedev::GameEngine::Auto;
        if (Engine == TEXT("bevy")) {
            engine = aigamedev::GameEngine::Bevy;
        } else if (Engine == TEXT("godot")) {
            engine = aigamedev::GameEngine::Godot;
        }
        
        // Create game configuration
        aigamedev::GameConfig config;
        config.with_engine(engine);
        
        // Create the game
        auto game = Owner->ai_dev_.create_game(
            TCHAR_TO_UTF8(*Description),
            config
        );
        
        // Call blueprint event on game thread
        AsyncTask(ENamedThreads::GameThread, [Owner = Owner, game]() {
            Owner->OnGameCreated(
                UTF8_TO_TCHAR(game.title.c_str()),
                UTF8_TO_TCHAR(game.output_directory.c_str())
            );
        });
        
    } catch (const aigamedev::AIGameDevException& e) {
        // Handle error on game thread
        AsyncTask(ENamedThreads::GameThread, [Owner = Owner, error = FString(UTF8_TO_TCHAR(e.what()))]() {
            Owner->OnGameCreationFailed(error);
        });
    }
}
```

#### Custom Game Engine Integration

```cpp
#include <ai_game_dev.hpp>
#include <memory>
#include <string>

class CustomGameEngine {
public:
    struct EngineConfig {
        int window_width = 800;
        int window_height = 600;
        bool fullscreen = false;
        std::string title = "AI Generated Game";
    };
    
    class AIGameIntegration {
    public:
        explicit AIGameIntegration(CustomGameEngine& engine) 
            : engine_(engine), ai_dev_() {}
        
        // Generate game and integrate into engine
        bool generate_and_load_game(const std::string& description) {
            try {
                // Generate game with custom engine configuration
                auto config = aigamedev::GameConfig{}
                    .with_engine(aigamedev::GameEngine::Auto)
                    .with_complexity("intermediate");
                
                auto game = ai_dev_.create_game(description, config);
                
                // Load generated content into engine
                load_game_content(game);
                
                return true;
            } catch (const aigamedev::AIGameDevException& e) {
                engine_.log_error("Game generation failed: " + std::string(e.what()));
                return false;
            }
        }
        
        // Generate assets for existing game
        void generate_additional_assets(const std::vector<std::string>& descriptions) {
            // Implementation for generating specific assets
        }
        
    private:
        void load_game_content(const aigamedev::GameResult& game) {
            // Parse generated files and load into engine
            engine_.set_title(game.title);
            
            // Load generated assets
            for (const auto& file : game.files_generated) {
                if (file.ends_with(".png") || file.ends_with(".jpg")) {
                    engine_.load_texture(file);
                } else if (file.ends_with(".wav") || file.ends_with(".ogg")) {
                    engine_.load_sound(file);
                } else if (file.ends_with(".json")) {
                    engine_.load_level_data(file);
                }
            }
        }
        
        CustomGameEngine& engine_;
        aigamedev::AIGameDev ai_dev_;
    };
    
    // Engine methods
    void set_title(const std::string& title) { config_.title = title; }
    void load_texture(const std::string& path) { /* Implementation */ }
    void load_sound(const std::string& path) { /* Implementation */ }
    void load_level_data(const std::string& path) { /* Implementation */ }
    void log_error(const std::string& message) { /* Implementation */ }
    
    // Get AI integration
    std::unique_ptr<AIGameIntegration> get_ai_integration() {
        return std::make_unique<AIGameIntegration>(*this);
    }
    
private:
    EngineConfig config_;
};

// Usage
int main() {
    CustomGameEngine engine;
    auto ai_integration = engine.get_ai_integration();
    
    if (ai_integration->generate_and_load_game(
        "Top-down shooter with power-ups and enemy waves"
    )) {
        // Run the generated game
        engine.run();
    }
    
    return 0;
}
```

## 🔧 Advanced Configuration

### Custom Configuration Builder

```cpp
#include <ai_game_dev.hpp>

class AdvancedConfigBuilder {
public:
    AdvancedConfigBuilder() = default;
    
    // Game type presets
    AdvancedConfigBuilder& for_real_time_strategy() {
        config_.with_engine(aigamedev::GameEngine::Bevy)
               .with_complexity("advanced")
               .add_feature("multiplayer")
               .add_feature("ai_opponents")
               .add_feature("tech_trees")
               .add_feature("resource_management");
        return *this;
    }
    
    AdvancedConfigBuilder& for_story_driven_game() {
        config_.with_engine(aigamedev::GameEngine::Godot)
               .with_complexity("intermediate")
               .add_feature("dialogue_system")
               .add_feature("quest_system")
               .add_feature("save_system")
               .add_feature("inventory_system");
        return *this;
    }
    
    AdvancedConfigBuilder& for_educational_game() {
        config_.with_engine(aigamedev::GameEngine::Arcade)
               .with_complexity("simple")
               .with_target_audience("children")
               .add_feature("progress_tracking")
               .add_feature("accessibility")
               .add_feature("web_deployment");
        return *this;
    }
    
    // Performance optimizations
    AdvancedConfigBuilder& with_performance_optimization() {
        config_.add_feature("entity_batching")
               .add_feature("spatial_partitioning")
               .add_feature("memory_pooling")
               .add_feature("multi_threading");
        return *this;
    }
    
    // Platform-specific configurations
    AdvancedConfigBuilder& for_mobile_platform() {
        config_.add_feature("touch_controls")
               .add_feature("battery_optimization")
               .add_feature("low_memory_mode");
        return *this;
    }
    
    AdvancedConfigBuilder& for_web_platform() {
        config_.add_feature("web_assembly")
               .add_feature("progressive_loading")
               .add_feature("offline_mode");
        return *this;
    }
    
    aigamedev::GameConfig build() const {
        return config_;
    }
    
private:
    aigamedev::GameConfig config_;
};

// Usage
auto rts_config = AdvancedConfigBuilder()
    .for_real_time_strategy()
    .with_performance_optimization()
    .build();

auto mobile_story_config = AdvancedConfigBuilder()
    .for_story_driven_game()
    .for_mobile_platform()
    .build();
```

### Resource Management

```cpp
#include <ai_game_dev.hpp>
#include <memory>
#include <unordered_map>
#include <mutex>

class AIGameDevManager {
public:
    static AIGameDevManager& instance() {
        static AIGameDevManager instance_;
        return instance_;
    }
    
    // Get or create AI game dev instance
    std::shared_ptr<aigamedev::AIGameDev> get_instance(const std::string& id = "default") {
        std::lock_guard<std::mutex> lock(mutex_);
        
        auto it = instances_.find(id);
        if (it != instances_.end()) {
            if (auto shared = it->second.lock()) {
                return shared;
            }
        }
        
        // Create new instance
        auto instance = std::make_shared<aigamedev::AIGameDev>();
        instances_[id] = instance;
        
        return instance;
    }
    
    // Clean up expired instances
    void cleanup() {
        std::lock_guard<std::mutex> lock(mutex_);
        
        for (auto it = instances_.begin(); it != instances_.end();) {
            if (it->second.expired()) {
                it = instances_.erase(it);
            } else {
                ++it;
            }
        }
    }
    
    // Get statistics
    struct Stats {
        size_t active_instances;
        size_t total_instances;
    };
    
    Stats get_stats() const {
        std::lock_guard<std::mutex> lock(mutex_);
        
        Stats stats{};
        stats.total_instances = instances_.size();
        
        for (const auto& [id, weak_ptr] : instances_) {
            if (!weak_ptr.expired()) {
                stats.active_instances++;
            }
        }
        
        return stats;
    }
    
private:
    AIGameDevManager() = default;
    
    mutable std::mutex mutex_;
    std::unordered_map<std::string, std::weak_ptr<aigamedev::AIGameDev>> instances_;
};

// RAII wrapper for automatic cleanup
class ScopedAIGameDev {
public:
    explicit ScopedAIGameDev(const std::string& id = "default")
        : ai_dev_(AIGameDevManager::instance().get_instance(id)) {}
    
    aigamedev::AIGameDev& operator*() { return *ai_dev_; }
    aigamedev::AIGameDev* operator->() { return ai_dev_.get(); }
    
    bool is_valid() const { return ai_dev_ != nullptr; }
    
private:
    std::shared_ptr<aigamedev::AIGameDev> ai_dev_;
};

// Usage
void create_multiple_games() {
    // Each thread gets its own instance
    ScopedAIGameDev ai_dev("thread_1");
    
    auto game = ai_dev->create_game(
        "Platformer game with unique mechanics",
        aigamedev::presets::simple_platformer()
    );
    
    // Instance is automatically cleaned up when scope ends
}
```

## 🧪 Testing Framework Integration

### Google Test Integration

```cpp
#include <gtest/gtest.h>
#include <ai_game_dev.hpp>

class AIGameDevTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Setup before each test
        ai_dev_ = std::make_unique<aigamedev::AIGameDev>();
    }
    
    void TearDown() override {
        // Cleanup after each test
        ai_dev_.reset();
    }
    
    std::unique_ptr<aigamedev::AIGameDev> ai_dev_;
};

TEST_F(AIGameDevTest, BasicGameCreation) {
    ASSERT_TRUE(ai_dev_->is_initialized());
    
    auto game = ai_dev_->create_game(
        "Simple test game",
        aigamedev::GameConfig{}.with_engine(aigamedev::GameEngine::Arcade)
    );
    
    EXPECT_FALSE(game.title.empty());
    EXPECT_TRUE(game.success);
    EXPECT_EQ(game.engine, "arcade");
    EXPECT_FALSE(game.output_directory.empty());
}

TEST_F(AIGameDevTest, SupportedEngines) {
    auto engines = ai_dev_->get_supported_engines();
    
    EXPECT_FALSE(engines.empty());
    EXPECT_TRUE(std::find(engines.begin(), engines.end(), "bevy") != engines.end());
    EXPECT_TRUE(std::find(engines.begin(), engines.end(), "godot") != engines.end());
    EXPECT_TRUE(std::find(engines.begin(), engines.end(), "arcade") != engines.end());
}

TEST_F(AIGameDevTest, AsyncGameCreation) {
    auto future = ai_dev_->create_game_async(
        "Async test game",
        aigamedev::GameConfig{}
    );
    
    // Wait with timeout
    ASSERT_EQ(future.wait_for(std::chrono::seconds(30)), std::future_status::ready);
    
    auto game = future.get();
    EXPECT_TRUE(game.success);
}

TEST_F(AIGameDevTest, ErrorHandling) {
    EXPECT_THROW(
        ai_dev_->create_game("", aigamedev::GameConfig{}),
        aigamedev::AIGameDevException
    );
}

// Performance tests
TEST_F(AIGameDevTest, PerformanceBenchmark) {
    const int num_games = 5;
    auto start_time = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < num_games; ++i) {
        auto game = ai_dev_->create_game(
            "Performance test game " + std::to_string(i),
            aigamedev::presets::simple_platformer()
        );
        
        ASSERT_TRUE(game.success);
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(
        end_time - start_time
    ).count();
    
    std::cout << "Created " << num_games << " games in " << duration << " seconds" << std::endl;
    
    // Performance expectation (adjust based on your requirements)
    EXPECT_LT(duration, 60); // Should complete within 60 seconds
}
```

### Catch2 Integration

```cpp
#include <catch2/catch_test_macros.hpp>
#include <ai_game_dev.hpp>

TEST_CASE("AI Game Development Basic Functionality", "[aigamedev]") {
    aigamedev::AIGameDev ai_dev;
    
    REQUIRE(ai_dev.is_initialized());
    
    SECTION("Create simple game") {
        auto game = ai_dev.create_game(
            "Simple platformer test",
            aigamedev::presets::simple_platformer()
        );
        
        REQUIRE(game.success);
        REQUIRE(!game.title.empty());
        REQUIRE(game.engine == "arcade");
    }
    
    SECTION("Get version information") {
        auto version = ai_dev.get_version();
        REQUIRE(!version.empty());
        REQUIRE(version.find('.') != std::string::npos); // Should contain dots
    }
    
    SECTION("Handle configuration presets") {
        auto rts_config = aigamedev::presets::advanced_rts();
        auto story_config = aigamedev::presets::story_driven_adventure();
        
        // These should not throw
        REQUIRE_NOTHROWS([&]() {
            ai_dev.create_game("RTS test", rts_config);
        }());
        
        REQUIRE_NOTHROWS([&]() {
            ai_dev.create_game("Story test", story_config);
        }());
    }
}

SCENARIO("Game creation workflow", "[aigamedev][workflow]") {
    GIVEN("An initialized AI game development system") {
        aigamedev::AIGameDev ai_dev;
        
        WHEN("Creating a complex game") {
            auto config = aigamedev::GameConfig{}
                .with_engine(aigamedev::GameEngine::Bevy)
                .with_complexity("advanced")
                .add_feature("multiplayer")
                .add_feature("physics");
            
            auto game = ai_dev.create_game(
                "Complex RTS with physics and multiplayer",
                config
            );
            
            THEN("The game should be created successfully") {
                REQUIRE(game.success);
                REQUIRE(!game.title.empty());
                REQUIRE(game.engine == "bevy");
                REQUIRE(game.files_generated.size() > 0);
            }
        }
    }
}
```

## 🚀 Production Deployment

### Static Library Distribution

```cmake
# CMakeLists.txt for static library distribution
cmake_minimum_required(VERSION 3.16)
project(ai-game-dev-static)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find dependencies
find_package(PkgConfig REQUIRED)
find_library(AI_GAME_DEV_LIB ai_game_dev REQUIRED)

# Create static library
add_library(ai-game-dev-static STATIC
    src/ai_game_dev.cpp
    src/game_generator.cpp
    src/utils.cpp
)

# Include directories
target_include_directories(ai-game-dev-static
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Link libraries
target_link_libraries(ai-game-dev-static
    PUBLIC ${AI_GAME_DEV_LIB}
    PRIVATE dl pthread
)

# Install configuration
install(TARGETS ai-game-dev-static
    EXPORT ai-game-dev-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.hpp"
)

# Export configuration
install(EXPORT ai-game-dev-targets
    FILE ai-game-dev-targets.cmake
    NAMESPACE aigamedev::
    DESTINATION lib/cmake/ai-game-dev
)

# Create config file
include(CMakePackageConfigHelpers)

configure_package_config_file(
    cmake/ai-game-dev-config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/ai-game-dev-config.cmake
    INSTALL_DESTINATION lib/cmake/ai-game-dev
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/ai-game-dev-config-version.cmake
    VERSION 1.0.0
    COMPATIBILITY SameMajorVersion
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/ai-game-dev-config.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/ai-game-dev-config-version.cmake
    DESTINATION lib/cmake/ai-game-dev
)
```

### Conan Package

```python
# conanfile.py
from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps

class AIGameDevConan(ConanFile):
    name = "ai-game-dev"
    version = "1.0.0"
    
    # Package metadata
    license = "MIT"
    author = "AI Game Dev Team"
    url = "https://github.com/ai-game-dev/cpp-bindings"
    description = "AI-powered game development with C++"
    topics = ("game-development", "ai", "cpp")
    
    # Configuration
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_examples": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_examples": False
    }
    
    # Sources
    exports_sources = "CMakeLists.txt", "src/*", "include/*", "examples/*"
    
    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
    
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = self.options.with_examples
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        cmake = CMake(self)
        cmake.install()
    
    def package_info(self):
        self.cpp_info.libs = ["ai-game-dev-cpp"]
        self.cpp_info.includedirs = ["include"]
        
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])
```

## 📚 Additional Resources

- [C++ API Reference](https://ai-game-dev.github.io/cpp-bindings/)
- [Modern C++ Best Practices](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines)
- [CMake Documentation](https://cmake.org/documentation/)
- [Example Applications](https://github.com/ai-game-dev/cpp-examples)

---

<div align="center">
  <strong>⚡ High-performance systems programming with AI game development</strong>
</div>