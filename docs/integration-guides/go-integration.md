# Go Integration Guide

<div align="center">
  <img src="https://golang.org/lib/godoc/images/go-logo-blue.svg" alt="Go Logo" width="200"/>
  
  <h2>🐹 AI Game Development with Go</h2>
</div>

This guide shows how to integrate the AI Game Development library into Go applications, providing native Go APIs with C-compatible performance.

## 🚀 Quick Start

### Installation

```bash
go get github.com/ai-game-dev/go-bindings
```

### Basic Usage

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
        "2D platformer with jumping mechanics",
        aigamedev.EngineArcade,
    )
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("✅ Game created: %s\n", game.Title)
    fmt.Printf("   Engine: %s\n", game.Engine)
    fmt.Printf("   Output: %s\n", game.OutputDirectory)
}
```

## 🏗️ Architecture

The Go bindings use CGO to interface with the core library:

```
Go Application
     ↓ (CGO)
Go Bindings (native Go API)
     ↓ (C Interface)  
Core Library (Compiled from Python/Rust)
```

## 🎮 Advanced Examples

### Configuration Builder

```go
import "github.com/ai-game-dev/go-bindings"

func createAdvancedGame() {
    // Use fluent configuration
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
    
    dev, err := aigamedev.NewAIGameDev()
    if err != nil {
        log.Fatal(err)
    }
    defer dev.Close()
    
    game, err := dev.CreateGame(
        "Real-time strategy with base building and combat",
        config,
    )
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("🎮 Advanced game: %s\n", game.Title)
}
```

### Web Server Integration

```go
package main

import (
    "encoding/json"
    "net/http"
    "github.com/gorilla/mux"
    "github.com/ai-game-dev/go-bindings"
)

type GameRequest struct {
    Description string `json:"description"`
    Engine      string `json:"engine"`
    Complexity  string `json:"complexity"`
}

func createGameHandler(w http.ResponseWriter, r *http.Request) {
    var req GameRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    
    // Convert engine string to enum
    var engine aigamedev.GameEngine
    switch req.Engine {
    case "bevy":
        engine = aigamedev.EngineBevy
    case "godot":
        engine = aigamedev.EngineGodot
    case "arcade":
        engine = aigamedev.EngineArcade
    default:
        engine = aigamedev.EngineAuto
    }
    
    config := &aigamedev.GameConfig{
        Engine:     engine,
        Complexity: req.Complexity,
    }
    
    dev, err := aigamedev.NewAIGameDev()
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    defer dev.Close()
    
    game, err := dev.CreateGame(req.Description, config)
    if err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(game)
}

func main() {
    r := mux.NewRouter()
    r.HandleFunc("/api/create-game", createGameHandler).Methods("POST")
    
    fmt.Println("🚀 Game creation API running on :8080")
    log.Fatal(http.ListenAndServe(":8080", r))
}
```

## ⚡ Performance Tips

### Connection Pooling

```go
type GameDevPool struct {
    instances chan *aigamedev.AIGameDev
}

func NewGameDevPool(size int) *GameDevPool {
    pool := &GameDevPool{
        instances: make(chan *aigamedev.AIGameDev, size),
    }
    
    // Pre-create instances
    for i := 0; i < size; i++ {
        dev, err := aigamedev.NewAIGameDev()
        if err != nil {
            panic(err)
        }
        pool.instances <- dev
    }
    
    return pool
}

func (p *GameDevPool) Get() *aigamedev.AIGameDev {
    return <-p.instances
}

func (p *GameDevPool) Put(dev *aigamedev.AIGameDev) {
    select {
    case p.instances <- dev:
    default:
        // Pool full, cleanup instance
        dev.Close()
    }
}

// Usage
var gameDevPool = NewGameDevPool(10)

func handleGameCreation(description string) (*aigamedev.GameResult, error) {
    dev := gameDevPool.Get()
    defer gameDevPool.Put(dev)
    
    return dev.CreateGame(description, nil)
}
```

### Concurrent Game Generation

```go
import (
    "context"
    "sync"
)

type GameGenerator struct {
    dev *aigamedev.AIGameDev
    mu  sync.RWMutex
}

func (g *GameGenerator) CreateGames(
    ctx context.Context,
    descriptions []string,
) ([]*aigamedev.GameResult, error) {
    results := make([]*aigamedev.GameResult, len(descriptions))
    errs := make([]error, len(descriptions))
    
    var wg sync.WaitGroup
    sem := make(chan struct{}, 5) // Limit concurrent operations
    
    for i, desc := range descriptions {
        wg.Add(1)
        go func(i int, desc string) {
            defer wg.Done()
            
            select {
            case sem <- struct{}{}:
                defer func() { <-sem }()
                
                dev, err := aigamedev.NewAIGameDev()
                if err != nil {
                    errs[i] = err
                    return
                }
                defer dev.Close()
                
                game, err := dev.CreateGame(desc, nil)
                if err != nil {
                    errs[i] = err
                    return
                }
                
                results[i] = game
                
            case <-ctx.Done():
                errs[i] = ctx.Err()
            }
        }(i, desc)
    }
    
    wg.Wait()
    
    // Check for errors
    for _, err := range errs {
        if err != nil {
            return nil, err
        }
    }
    
    return results, nil
}
```

## 🧪 Testing

### Unit Tests

```go
package main

import (
    "testing"
    "github.com/ai-game-dev/go-bindings"
)

func TestGameCreation(t *testing.T) {
    dev, err := aigamedev.NewAIGameDev()
    if err != nil {
        t.Fatalf("Failed to create AIGameDev: %v", err)
    }
    defer dev.Close()
    
    game, err := dev.CreateGame(
        "Simple test game",
        &aigamedev.GameConfig{
            Engine:     aigamedev.EngineArcade,
            Complexity: "simple",
        },
    )
    if err != nil {
        t.Fatalf("Game creation failed: %v", err)
    }
    
    if game.Title == "" {
        t.Error("Game title should not be empty")
    }
    
    if !game.Success {
        t.Error("Game creation should be successful")
    }
}

func TestSupportedEngines(t *testing.T) {
    dev, err := aigamedev.NewAIGameDev()
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
    
    expectedEngines := []aigamedev.GameEngine{
        aigamedev.EngineBevy,
        aigamedev.EngineGodot,
        aigamedev.EngineArcade,
    }
    
    engineMap := make(map[aigamedev.GameEngine]bool)
    for _, engine := range engines {
        engineMap[engine] = true
    }
    
    for _, expected := range expectedEngines {
        if !engineMap[expected] {
            t.Errorf("Expected engine %v not found", expected)
        }
    }
}
```

### Benchmarks

```go
func BenchmarkGameCreation(b *testing.B) {
    dev, err := aigamedev.NewAIGameDev()
    if err != nil {
        b.Fatalf("Failed to create AIGameDev: %v", err)
    }
    defer dev.Close()
    
    b.ResetTimer()
    
    for i := 0; i < b.N; i++ {
        _, err := dev.CreateGame("Benchmark test game", nil)
        if err != nil {
            b.Fatalf("Game creation failed: %v", err)
        }
    }
}

func BenchmarkConfigBuilder(b *testing.B) {
    for i := 0; i < b.N; i++ {
        config := aigamedev.NewConfigBuilder().
            WithEngine(aigamedev.EngineBevy).
            WithComplexity(aigamedev.ComplexityAdvanced).
            WithFeatures(
                aigamedev.FeatureMultiplayer,
                aigamedev.FeatureAI,
            ).
            Build()
        
        if config == nil {
            b.Fatal("Config should not be nil")
        }
    }
}
```

## 🔧 Building and Deployment

### Build Configuration

```bash
# Build with CGO
CGO_ENABLED=1 go build -o game-server

# Cross-compilation (requires cross-compiler)
GOOS=linux GOARCH=amd64 CGO_ENABLED=1 go build -o game-server-linux

# With static linking
CGO_ENABLED=1 go build -ldflags '-linkmode external -extldflags "-static"' -o game-server-static
```

### Docker Deployment

```dockerfile
FROM golang:1.21-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=1 go build -o game-server

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/

COPY --from=builder /app/game-server .
COPY --from=builder /app/lib ./lib

EXPOSE 8080
CMD ["./game-server"]
```

## 🚀 Production Considerations

### Error Handling

```go
import "github.com/pkg/errors"

func createGameSafely(description string) (*aigamedev.GameResult, error) {
    dev, err := aigamedev.NewAIGameDev()
    if err != nil {
        return nil, errors.Wrap(err, "failed to initialize AI Game Dev")
    }
    defer dev.Close()
    
    if !dev.IsInitialized() {
        return nil, errors.New("library not properly initialized")
    }
    
    game, err := dev.CreateGame(description, nil)
    if err != nil {
        lastError := dev.GetLastError()
        return nil, errors.Wrapf(err, "game creation failed (last error: %s)", lastError)
    }
    
    if !game.Success {
        return nil, errors.Errorf("game creation unsuccessful: %s", game.ErrorMessage)
    }
    
    return game, nil
}
```

### Monitoring and Metrics

```go
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    gamesCreated = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "games_created_total",
            Help: "Total number of games created",
        },
        []string{"engine", "complexity"},
    )
    
    gameCreationDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "game_creation_duration_seconds",
            Help:    "Time taken to create games",
            Buckets: prometheus.DefBuckets,
        },
        []string{"engine"},
    )
)

func createGameWithMetrics(description string, config *aigamedev.GameConfig) (*aigamedev.GameResult, error) {
    timer := prometheus.NewTimer(gameCreationDuration.WithLabelValues(string(config.Engine)))
    defer timer.ObserveDuration()
    
    game, err := createGameSafely(description)
    if err != nil {
        return nil, err
    }
    
    gamesCreated.WithLabelValues(string(config.Engine), config.Complexity).Inc()
    
    return game, nil
}
```

## 📚 Additional Resources

- [Go Documentation](https://pkg.go.dev/github.com/ai-game-dev/go-bindings)
- [CGO Best Practices](https://golang.org/cmd/cgo/)
- [Performance Optimization](https://golang.org/doc/diagnostics.html)
- [Example Applications](https://github.com/ai-game-dev/go-examples)

---

<div align="center">
  <strong>🐹 High-performance AI game development with Go</strong>
</div>