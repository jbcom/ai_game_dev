# Node.js Integration Guide

<div align="center">
  <img src="https://nodejs.org/static/images/logo.svg" alt="Node.js Logo" width="200"/>
  
  <h2>📦 AI Game Development with Node.js</h2>
</div>

This guide shows how to integrate the AI Game Development library into Node.js applications, enabling server-side game generation and web framework integration.

## 🚀 Quick Start

### Installation

```bash
npm install ai-game-dev

# Or with yarn
yarn add ai-game-dev
```

### Basic Usage

```javascript
const { createGame, GameEngine } = require('ai-game-dev');

async function createMyGame() {
    try {
        const game = await createGame(
            'A fun 2D platformer with jumping and coin collection',
            GameEngine.ARCADE
        );
        
        console.log(`✅ Game created: ${game.title}`);
        console.log(`   Engine: ${game.engine}`);
        console.log(`   Files: ${game.filesGenerated.length}`);
        console.log(`   Output: ${game.outputDirectory}`);
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
    }
}

createMyGame();
```

## 🏗️ Architecture

The Node.js bindings use native C++ addons for optimal performance:

```
Node.js Application
     ↓ (Native Addon)
C++ Bindings (N-API/NAN)
     ↓ (C Interface)
Core Library (Go shared library)
```

## 🎮 Advanced Examples

### Express.js API Server

```javascript
const express = require('express');
const { AIGameDev, GameEngine } = require('ai-game-dev');

const app = express();
app.use(express.json());

// Initialize AI Game Dev instance pool
const gameDevPool = [];
const poolSize = 5;

async function initializePool() {
    for (let i = 0; i < poolSize; i++) {
        const dev = new AIGameDev();
        gameDevPool.push(dev);
    }
}

function getGameDev() {
    return gameDevPool.pop() || new AIGameDev();
}

function returnGameDev(dev) {
    if (gameDevPool.length < poolSize) {
        gameDevPool.push(dev);
    } else {
        dev.cleanup();
    }
}

// API endpoint for game creation
app.post('/api/create-game', async (req, res) => {
    const { description, engine, config = {} } = req.body;
    
    if (!description) {
        return res.status(400).json({ 
            error: 'Description is required' 
        });
    }
    
    const gameDev = getGameDev();
    
    try {
        const game = await gameDev.createGame(description, {
            engine: engine || GameEngine.AUTO,
            ...config
        });
        
        res.json({
            success: true,
            game: game
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    } finally {
        returnGameDev(gameDev);
    }
});

// Batch game creation
app.post('/api/create-games-batch', async (req, res) => {
    const { games } = req.body;
    
    if (!Array.isArray(games) || games.length === 0) {
        return res.status(400).json({
            error: 'Games array is required'
        });
    }
    
    try {
        const results = await Promise.all(
            games.map(async (gameReq) => {
                const gameDev = getGameDev();
                try {
                    return await gameDev.createGame(
                        gameReq.description,
                        gameReq.config
                    );
                } finally {
                    returnGameDev(gameDev);
                }
            })
        );
        
        res.json({
            success: true,
            games: results
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Server startup
async function startServer() {
    await initializePool();
    
    const port = process.env.PORT || 3000;
    app.listen(port, () => {
        console.log(`🚀 Game creation API running on port ${port}`);
    });
}

startServer().catch(console.error);

// Graceful shutdown
process.on('SIGTERM', () => {
    gameDevPool.forEach(dev => dev.cleanup());
    process.exit(0);
});
```

### Real-time Game Generation with Socket.io

```javascript
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { AIGameDev } = require('ai-game-dev');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(express.static('public'));

io.on('connection', (socket) => {
    console.log(`Client connected: ${socket.id}`);
    
    const gameDev = new AIGameDev();
    
    socket.on('create-game', async (data) => {
        const { description, config } = data;
        
        try {
            // Send progress updates
            socket.emit('game-progress', { 
                status: 'initializing',
                message: 'Starting AI game generation...' 
            });
            
            socket.emit('game-progress', { 
                status: 'generating',
                message: 'AI is creating your game...' 
            });
            
            const game = await gameDev.createGame(description, config);
            
            socket.emit('game-progress', { 
                status: 'finalizing',
                message: 'Finalizing game files...' 
            });
            
            socket.emit('game-complete', {
                success: true,
                game: game
            });
            
        } catch (error) {
            socket.emit('game-error', {
                success: false,
                error: error.message
            });
        }
    });
    
    socket.on('disconnect', () => {
        console.log(`Client disconnected: ${socket.id}`);
        gameDev.cleanup();
    });
});

const port = process.env.PORT || 3000;
server.listen(port, () => {
    console.log(`🎮 Real-time game creation server running on port ${port}`);
});
```

### Integration with Game Development Frameworks

#### Phaser.js Integration

```javascript
const { generateAssets, createGame } = require('ai-game-dev');
const fs = require('fs').promises;
const path = require('path');

class PhaserGameBuilder {
    constructor() {
        this.outputDir = './generated-games';
    }
    
    async createPhaserGame(description, config = {}) {
        // Generate game assets
        const assets = await generateAssets({
            descriptions: [
                'Player character sprite sheet',
                'Enemy sprites',
                'Background tiles',
                'UI elements',
                'Sound effects'
            ],
            style: config.artStyle || 'pixel_art'
        });
        
        // Generate base game structure
        const gameData = await createGame(description, {
            engine: 'web',
            framework: 'phaser',
            ...config
        });
        
        // Create Phaser-specific game files
        await this.generatePhaserProject(gameData, assets);
        
        return {
            ...gameData,
            framework: 'phaser',
            playUrl: `${this.outputDir}/${gameData.title}/index.html`
        };
    }
    
    async generatePhaserProject(gameData, assets) {
        const projectDir = path.join(this.outputDir, gameData.title);
        
        // Create project structure
        await fs.mkdir(projectDir, { recursive: true });
        await fs.mkdir(path.join(projectDir, 'assets'), { recursive: true });
        await fs.mkdir(path.join(projectDir, 'src'), { recursive: true });
        
        // Generate HTML file
        const htmlContent = this.generateHTML(gameData);
        await fs.writeFile(
            path.join(projectDir, 'index.html'),
            htmlContent
        );
        
        // Generate main game file
        const gameScript = this.generateGameScript(gameData, assets);
        await fs.writeFile(
            path.join(projectDir, 'src', 'game.js'),
            gameScript
        );
        
        // Copy assets
        for (const asset of assets) {
            if (asset.path) {
                const assetName = path.basename(asset.path);
                await fs.copyFile(
                    asset.path,
                    path.join(projectDir, 'assets', assetName)
                );
            }
        }
        
        // Generate package.json
        const packageJson = {
            name: gameData.title.toLowerCase().replace(/\s+/g, '-'),
            version: '1.0.0',
            description: gameData.description,
            main: 'src/game.js',
            dependencies: {
                'phaser': '^3.70.0'
            }
        };
        
        await fs.writeFile(
            path.join(projectDir, 'package.json'),
            JSON.stringify(packageJson, null, 2)
        );
    }
    
    generateHTML(gameData) {
        return `<!DOCTYPE html>
<html>
<head>
    <title>${gameData.title}</title>
    <style>
        body { margin: 0; padding: 20px; background: #2c3e50; }
        #game-container { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 80vh; 
        }
    </style>
</head>
<body>
    <h1 style="color: white; text-align: center;">${gameData.title}</h1>
    <div id="game-container">
        <div id="game"></div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js"></script>
    <script src="src/game.js"></script>
</body>
</html>`;
    }
    
    generateGameScript(gameData, assets) {
        return `// ${gameData.title} - Generated by AI Game Dev
class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }
    
    preload() {
        // Load AI-generated assets
        ${assets.map(asset => 
            `this.load.image('${asset.name}', 'assets/${path.basename(asset.path)}');`
        ).join('\n        ')}
    }
    
    create() {
        // Add background
        this.add.image(400, 300, 'background');
        
        // Add player
        this.player = this.add.sprite(100, 450, 'player');
        
        // Add game logic based on AI-generated description
        this.setupGameplay();
    }
    
    update() {
        // Game update loop
        this.handleInput();
        this.updateGameplay();
    }
    
    setupGameplay() {
        // AI-generated gameplay setup
        console.log('Setting up: ${gameData.description}');
    }
    
    handleInput() {
        const cursors = this.input.keyboard.createCursorKeys();
        
        if (cursors.left.isDown) {
            this.player.x -= 5;
        }
        if (cursors.right.isDown) {
            this.player.x += 5;
        }
        if (cursors.up.isDown) {
            this.player.y -= 5;
        }
        if (cursors.down.isDown) {
            this.player.y += 5;
        }
    }
    
    updateGameplay() {
        // AI-generated game logic updates
    }
}

// Phaser game configuration
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game',
    backgroundColor: '#87CEEB',
    scene: GameScene,
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 300 },
            debug: false
        }
    }
};

const game = new Phaser.Game(config);`;
    }
}

// Usage
const builder = new PhaserGameBuilder();

async function createWebGame() {
    const game = await builder.createPhaserGame(
        'A space shooter with enemy waves and power-ups',
        {
            artStyle: 'pixel_art',
            difficulty: 'intermediate'
        }
    );
    
    console.log(`🎮 Phaser game created: ${game.playUrl}`);
}
```

## ⚡ Performance Optimization

### Worker Threads for CPU-Intensive Operations

```javascript
const { Worker, isMainThread, parentPort } = require('worker_threads');
const { createGame } = require('ai-game-dev');

if (isMainThread) {
    // Main thread - API server
    const express = require('express');
    const app = express();
    app.use(express.json());
    
    const workers = [];
    const workerCount = require('os').cpus().length;
    
    // Create worker pool
    for (let i = 0; i < workerCount; i++) {
        const worker = new Worker(__filename);
        workers.push(worker);
    }
    
    let currentWorker = 0;
    
    app.post('/api/create-game', (req, res) => {
        const worker = workers[currentWorker];
        currentWorker = (currentWorker + 1) % workers.length;
        
        const requestId = Date.now() + Math.random();
        
        // Send work to worker
        worker.postMessage({
            requestId,
            description: req.body.description,
            config: req.body.config
        });
        
        // Listen for response
        const responseHandler = (result) => {
            if (result.requestId === requestId) {
                worker.off('message', responseHandler);
                
                if (result.error) {
                    res.status(500).json({ error: result.error });
                } else {
                    res.json({ success: true, game: result.game });
                }
            }
        };
        
        worker.on('message', responseHandler);
        
        // Set timeout
        setTimeout(() => {
            worker.off('message', responseHandler);
            res.status(408).json({ error: 'Request timeout' });
        }, 120000); // 2 minutes
    });
    
    app.listen(3000, () => {
        console.log('🚀 Multi-threaded game creation server running');
    });
    
} else {
    // Worker thread - game generation
    parentPort.on('message', async ({ requestId, description, config }) => {
        try {
            const game = await createGame(description, config);
            
            parentPort.postMessage({
                requestId,
                game
            });
        } catch (error) {
            parentPort.postMessage({
                requestId,
                error: error.message
            });
        }
    });
}
```

### Caching with Redis

```javascript
const redis = require('redis');
const { createGame } = require('ai-game-dev');
const crypto = require('crypto');

class CachedGameCreator {
    constructor() {
        this.redis = redis.createClient();
        this.cacheTimeout = 3600; // 1 hour
    }
    
    async connect() {
        await this.redis.connect();
    }
    
    generateCacheKey(description, config) {
        const data = JSON.stringify({ description, config });
        return crypto.createHash('sha256').update(data).digest('hex');
    }
    
    async createGameCached(description, config = {}) {
        const cacheKey = this.generateCacheKey(description, config);
        
        // Try to get from cache
        const cached = await this.redis.get(cacheKey);
        if (cached) {
            console.log('📦 Returning cached game');
            return JSON.parse(cached);
        }
        
        // Create new game
        console.log('🔄 Creating new game');
        const game = await createGame(description, config);
        
        // Store in cache
        await this.redis.setEx(
            cacheKey,
            this.cacheTimeout,
            JSON.stringify(game)
        );
        
        return game;
    }
    
    async clearCache() {
        const keys = await this.redis.keys('*');
        if (keys.length > 0) {
            await this.redis.del(keys);
        }
    }
}

// Usage
const cachedCreator = new CachedGameCreator();

async function setupCaching() {
    await cachedCreator.connect();
    
    // Express route with caching
    app.post('/api/create-game-cached', async (req, res) => {
        try {
            const game = await cachedCreator.createGameCached(
                req.body.description,
                req.body.config
            );
            
            res.json({ success: true, game });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    });
}
```

## 🧪 Testing

### Unit Tests with Jest

```javascript
const { AIGameDev, createGame, GameEngine } = require('ai-game-dev');

describe('AI Game Development', () => {
    let gameDev;
    
    beforeEach(async () => {
        gameDev = new AIGameDev();
    });
    
    afterEach(() => {
        if (gameDev) {
            gameDev.cleanup();
        }
    });
    
    test('should create AI game dev instance', () => {
        expect(gameDev).toBeDefined();
        expect(gameDev.isInitialized()).toBe(true);
    });
    
    test('should create simple game', async () => {
        const game = await gameDev.createGame(
            'Simple test game',
            { engine: GameEngine.ARCADE }
        );
        
        expect(game).toBeDefined();
        expect(game.title).toBeTruthy();
        expect(game.success).toBe(true);
        expect(game.engine).toBe('arcade');
    });
    
    test('should handle invalid input', async () => {
        await expect(
            gameDev.createGame('', {})
        ).rejects.toThrow();
    });
    
    test('should get supported engines', () => {
        const engines = gameDev.getSupportedEngines();
        
        expect(Array.isArray(engines)).toBe(true);
        expect(engines.length).toBeGreaterThan(0);
        expect(engines).toContain('bevy');
        expect(engines).toContain('godot');
        expect(engines).toContain('arcade');
    });
    
    test('should get version', () => {
        const version = gameDev.getVersion();
        expect(typeof version).toBe('string');
        expect(version).toMatch(/^\d+\.\d+\.\d+$/);
    });
});

describe('Convenience functions', () => {
    test('should create game with convenience function', async () => {
        const game = await createGame(
            'Test platformer',
            GameEngine.ARCADE
        );
        
        expect(game).toBeDefined();
        expect(game.success).toBe(true);
    });
});
```

### Integration Tests

```javascript
const request = require('supertest');
const express = require('express');

// Setup test server
const app = express();
app.use(express.json());

// Add your routes here
app.post('/api/create-game', async (req, res) => {
    // Your game creation endpoint
});

describe('Game Creation API', () => {
    test('POST /api/create-game should create game', async () => {
        const response = await request(app)
            .post('/api/create-game')
            .send({
                description: 'Test game for integration test',
                engine: 'arcade'
            })
            .expect(200);
        
        expect(response.body.success).toBe(true);
        expect(response.body.game).toBeDefined();
        expect(response.body.game.title).toBeTruthy();
    });
    
    test('POST /api/create-game should validate input', async () => {
        await request(app)
            .post('/api/create-game')
            .send({})
            .expect(400);
    });
});
```

## 🚀 Production Deployment

### PM2 Configuration

```javascript
// ecosystem.config.js
module.exports = {
    apps: [{
        name: 'ai-game-dev-api',
        script: 'server.js',
        instances: 'max',
        exec_mode: 'cluster',
        
        // Environment variables
        env: {
            NODE_ENV: 'production',
            PORT: 3000,
        },
        
        // Resource limits
        max_memory_restart: '1G',
        
        // Logging
        log_file: 'logs/combined.log',
        out_file: 'logs/out.log',
        error_file: 'logs/error.log',
        log_date_format: 'YYYY-MM-DD HH:mm Z',
        
        // Auto-restart
        autorestart: true,
        watch: false,
        max_restarts: 10,
        min_uptime: '10s',
        
        // Advanced features
        kill_timeout: 5000,
        listen_timeout: 3000,
        
        // Health monitoring
        health_check_grace_period: 10000
    }]
};
```

### Docker Configuration

```dockerfile
FROM node:18-alpine

# Install build dependencies for native modules
RUN apk add --no-cache make gcc g++ python3

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app
USER nodejs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["node", "server.js"]
```

## 📚 Additional Resources

- [Node.js Package Documentation](https://npmjs.com/package/ai-game-dev)
- [Native Addon Development](https://nodejs.org/api/addons.html)
- [Performance Best Practices](https://nodejs.org/en/docs/guides/simple-profiling/)
- [Example Applications](https://github.com/ai-game-dev/nodejs-examples)

---

<div align="center">
  <strong>📦 Server-side AI game development with Node.js</strong>
</div>