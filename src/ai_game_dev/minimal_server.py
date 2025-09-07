"""
Minimal AI Game Development Server
Ultra-lightweight server with split-panel design and dynamic content switching.
"""

import asyncio
import json
import sqlite3
import os
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path


class GameDevHandler(BaseHTTPRequestHandler):
    """HTTP handler for the game development platform with dynamic content switching."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.serve_main_interface()
        elif path.startswith("/static/"):
            self.serve_static_file(path)
        elif path == "/api/status":
            self.serve_api_status()
        elif path == "/api/player-data":
            self.serve_player_data()
        elif path.startswith("/api/content/"):
            content_type = path.split("/")[-1]
            self.serve_dynamic_content(content_type)
        else:
            self.serve_404()
    
    def do_POST(self):
        """Handle POST requests."""
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/api/generate-game":
            self.handle_generate_game()
        elif path == "/api/save-progress":
            self.handle_save_progress()
        elif path == "/api/chat":
            self.handle_chat()
        else:
            self.serve_404()
    
    def serve_static_file(self, path):
        """Serve static files (assets)."""
        
        # Remove /static/ prefix and get relative path
        file_path = path[8:]  # Remove '/static/'
        
        # Look for the file in the static assets directory
        static_dir = Path(__file__).parent / "server" / "static"
        full_path = static_dir / file_path
        
        try:
            if full_path.exists() and full_path.is_file():
                # Get MIME type
                mime_type, _ = mimetypes.guess_type(str(full_path))
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                # Read and serve the file
                with open(full_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-type', mime_type)
                self.send_header('Content-length', len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.serve_404()
                
        except Exception as e:
            print(f"Error serving static file {path}: {e}")
            self.serve_404()
    
    def serve_main_interface(self):
        """Serve the main split-panel interface with existing assets."""
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🎮 AI Game Development Platform</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            
            <!-- Local Fonts -->
            <style>
                @font-face {
                    font-family: 'Inter';
                    src: url('/static/assets/fonts/inter-400.woff2') format('woff2');
                    font-weight: 400;
                    font-display: swap;
                }
                @font-face {
                    font-family: 'Inter';
                    src: url('/static/assets/fonts/inter-600.woff2') format('woff2');
                    font-weight: 600;
                    font-display: swap;
                }
                @font-face {
                    font-family: 'JetBrains Mono';
                    src: url('/static/assets/fonts/jetbrains-mono-400.woff2') format('woff2');
                    font-weight: 400;
                    font-display: swap;
                }
            </style>
            
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                
                body { 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                    background: 
                        url('/static/assets/textures/circuit-pattern.png'),
                        linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 30%, #16213e 70%, #0f3460 100%);
                    background-size: 300px 300px, cover;
                    background-repeat: repeat, no-repeat;
                    background-blend-mode: soft-light, normal;
                    min-height: 100vh;
                    padding: 20px;
                    color: white;
                }
                
                .main-container {
                    max-width: 1400px;
                    margin: 0 auto;
                    min-height: calc(100vh - 40px);
                    position: relative;
                }
                
                /* Tech Frame System */
                :root {
                    --inset-top: 11%;
                    --inset-right: 10%;
                    --inset-bottom: 12%;
                    --inset-left: 13%;
                }
                
                .tech-frame {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: center / cover no-repeat url('/static/assets/frames/tech-frame.png');
                }
                
                .safe-box {
                    position: absolute;
                    top: var(--inset-top);
                    right: var(--inset-right);
                    bottom: var(--inset-bottom);
                    left: var(--inset-left);
                    display: flex;
                    flex-direction: column;
                }
                
                .header {
                    background: 
                        url('/static/assets/textures/glass-panel.png'),
                        rgba(15, 23, 42, 0.8);
                    background-size: cover, auto;
                    background-blend-mode: overlay, normal;
                    backdrop-filter: blur(15px);
                    border: 1px solid rgba(100, 255, 218, 0.3);
                    border-radius: 16px;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    margin-bottom: 20px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                
                .header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                
                .header .subtitle {
                    font-size: 1.1em;
                    opacity: 0.9;
                }
                
                .split-container {
                    display: flex;
                    min-height: 600px;
                }
                
                .panel {
                    flex: 1;
                    position: relative;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    border-right: 1px solid #e2e8f0;
                }
                
                .panel:last-child {
                    border-right: none;
                }
                
                .panel:hover {
                    transform: scale(1.02);
                    z-index: 2;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                }
                
                .panel-content {
                    padding: 40px;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    text-align: center;
                }
                
                .workshop-panel {
                    background: 
                        url('/static/assets/textures/hexagon-overlay.png'),
                        linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
                    background-size: 120px 120px, cover;
                    background-repeat: repeat, no-repeat;
                    background-blend-mode: multiply, normal;
                    color: white;
                }
                
                .academy-panel {
                    background: 
                        url('/static/assets/textures/particle-glow.png'),
                        linear-gradient(135deg, #a55eea 0%, #26de81 100%);
                    background-size: cover, cover;
                    background-repeat: no-repeat, no-repeat;
                    background-position: center, center;
                    background-blend-mode: soft-light, normal;
                    color: white;
                }
                
                .panel-icon {
                    font-size: 5em;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }
                
                .panel-title {
                    font-size: 2.5em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
                }
                
                .panel-description {
                    font-size: 1.2em;
                    line-height: 1.6;
                    margin-bottom: 25px;
                    opacity: 0.95;
                }
                
                .panel-features {
                    list-style: none;
                    font-size: 1.1em;
                    line-height: 1.8;
                }
                
                .panel-features li {
                    margin-bottom: 8px;
                }
                
                .dynamic-content {
                    display: none;
                    padding: 40px;
                    background: white;
                    min-height: 600px;
                }
                
                .back-button {
                    position: absolute;
                    top: 20px;
                    left: 20px;
                    background: url('/static/assets/buttons/back.png') center / contain no-repeat;
                    width: 60px;
                    height: 40px;
                    border: none;
                    cursor: pointer;
                    transition: all 0.3s;
                    text-indent: -9999px; /* Hide text, show only image */
                }
                
                .back-button:hover {
                    transform: scale(1.1);
                    filter: brightness(1.2);
                }
                
                .loading {
                    text-align: center;
                    padding: 40px;
                    color: #666;
                }
                
                .form-group {
                    margin-bottom: 20px;
                    text-align: left;
                }
                
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #2d3748;
                }
                
                .form-group input, .form-group select, .form-group textarea {
                    width: 100%;
                    padding: 10px;
                    border: 2px solid #e2e8f0;
                    border-radius: 5px;
                    font-size: 1em;
                }
                
                .btn {
                    background: #4a5568;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 1em;
                    margin: 5px;
                    transition: background 0.3s;
                }
                
                .btn:hover {
                    background: #2d3748;
                }
                
                .btn-primary {
                    background: #667eea;
                }
                
                .btn-primary:hover {
                    background: #5a67d8;
                }
                
                .professor-pixel {
                    width: 120px;
                    height: 120px;
                    margin: 0 auto 20px;
                    background: url('/static/assets/characters/professor_pixel.png') center / cover no-repeat;
                    border-radius: 50%;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.3);
                    animation: float 3s ease-in-out infinite;
                }
                
                @keyframes float {
                    0%, 100% { transform: translateY(0px); }
                    50% { transform: translateY(-10px); }
                }
                
                @media (max-width: 768px) {
                    .split-container {
                        flex-direction: column;
                    }
                    
                    .panel {
                        border-right: none;
                        border-bottom: 1px solid #e2e8f0;
                    }
                    
                    .panel:hover {
                        transform: none;
                    }
                }
            </style>
        </head>
        <body>
            <div class="main-container">
                <!-- Tech Frame Background -->
                <div class="tech-frame"></div>
                
                <!-- Safe Content Area -->
                <div class="safe-box">
                    <!-- Header -->
                    <div class="header">
                        <h1>🎮 AI Game Development Platform</h1>
                        <p class="subtitle">Choose your path: Create games or master programming</p>
                    </div>
                    
                    <!-- Split Panel Interface -->
                <div id="split-view" class="split-container">
                    <!-- Game Workshop Panel -->
                    <div class="panel workshop-panel" onclick="loadContent('workshop')">
                        <div class="panel-content">
                            <div class="panel-icon">🛠️</div>
                            <h2 class="panel-title">Game Workshop</h2>
                            <p class="panel-description">
                                Create revolutionary games with AI-powered tools and multi-engine support
                            </p>
                            <ul class="panel-features">
                                <li>🎯 Multi-Engine Support (Pygame, Godot, Bevy)</li>
                                <li>🤖 AI-Powered Asset Generation</li>
                                <li>⚡ Instant Game Prototyping</li>
                                <li>🎨 Dynamic Art & Audio Creation</li>
                                <li>🚀 One-Click Deployment</li>
                            </ul>
                        </div>
                    </div>
                    
                    <!-- Arcade Academy Panel -->
                    <div class="panel academy-panel" onclick="loadContent('academy')">
                        <div class="panel-content">
                            <div class="panel-icon">🎓</div>
                            <h2 class="panel-title">Arcade Academy</h2>
                            <p class="panel-description">
                                Master programming through cyberpunk adventures with Professor Pixel
                            </p>
                            <ul class="panel-features">
                                <li>🌃 Cyberpunk Learning Environment</li>
                                <li>👨‍🏫 Professor Pixel as Your Guide</li>
                                <li>🎮 Interactive Coding Challenges</li>
                                <li>🏆 Achievement & Progress System</li>
                                <li>📚 Real-World Project Building</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <!-- Dynamic Content Area -->
                <div id="dynamic-content" class="dynamic-content">
                    <button class="back-button" onclick="showSplitView()">← Back to Home</button>
                    <div id="content-area">
                        <div class="loading">Loading...</div>
                    </div>
                </div>
                </div>
            </div>
            
            <!-- Audio System -->
            <script>
                class AudioManager {
                    constructor() {
                        this.sounds = {
                            click: new Audio('/static/assets/audio/button_click_futuristic.wav'),
                            hover: new Audio('/static/assets/audio/hover_beep_cyberpunk.wav'),
                            success: new Audio('/static/assets/audio/success_ding_pleasant.wav'),
                            notification: new Audio('/static/assets/audio/notification_chime_tech.wav')
                        };
                        this.enabled = true;
                        this.volume = 0.3;
                        
                        Object.values(this.sounds).forEach(sound => {
                            sound.volume = this.volume;
                        });
                    }
                    
                    play(soundName) {
                        if (this.enabled && this.sounds[soundName]) {
                            this.sounds[soundName].currentTime = 0;
                            this.sounds[soundName].play().catch(() => {});
                        }
                    }
                }
                
                const audioManager = new AudioManager();
                
                document.addEventListener('DOMContentLoaded', function() {
                    document.addEventListener('click', function(e) {
                        if (e.target.matches('button, .btn, .panel')) {
                            audioManager.play('click');
                        }
                    });
                    
                    document.addEventListener('mouseover', function(e) {
                        if (e.target.matches('.panel, button, .btn')) {
                            audioManager.play('hover');
                        }
                    });
                });
            </script>
            </div>
            
            <script>
                let currentUser = null;
                
                // Initialize user data
                async function initializeUser() {
                    try {
                        const response = await fetch('/api/player-data');
                        const data = await response.json();
                        currentUser = data;
                        console.log('User initialized:', currentUser);
                    } catch (error) {
                        console.error('Failed to initialize user:', error);
                    }
                }
                
                // Load dynamic content
                async function loadContent(type) {
                    document.getElementById('split-view').style.display = 'none';
                    document.getElementById('dynamic-content').style.display = 'block';
                    
                    try {
                        const response = await fetch(`/api/content/${type}`);
                        const html = await response.text();
                        document.getElementById('content-area').innerHTML = html;
                    } catch (error) {
                        document.getElementById('content-area').innerHTML = 
                            '<div class="loading">Error loading content. Please try again.</div>';
                    }
                }
                
                // Show split view
                function showSplitView() {
                    document.getElementById('dynamic-content').style.display = 'none';
                    document.getElementById('split-view').style.display = 'flex';
                }
                
                // Save user progress
                async function saveProgress(data) {
                    try {
                        await fetch('/api/save-progress', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify(data)
                        });
                    } catch (error) {
                        console.error('Failed to save progress:', error);
                    }
                }
                
                // Initialize on page load
                window.addEventListener('load', initializeUser);
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_dynamic_content(self, content_type):
        """Serve dynamic content based on type."""
        
        if content_type == "workshop":
            html = self.get_workshop_content()
        elif content_type == "academy":
            html = self.get_academy_content()
        else:
            html = "<div class='loading'>Content not found</div>"
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def get_workshop_content(self):
        """Get Game Workshop content."""
        
        return """
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="color: #ff6b6b; text-align: center; margin-bottom: 30px;">
                🛠️ Game Workshop
            </h1>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
                <h2 style="color: #2d3748; margin-bottom: 20px;">Create Your Game</h2>
                
                <form onsubmit="generateGame(event)">
                    <div class="form-group">
                        <label for="game-title">Game Title</label>
                        <input type="text" id="game-title" placeholder="My Awesome Game" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="game-engine">Game Engine</label>
                        <select id="game-engine" required>
                            <option value="">Select Engine</option>
                            <option value="pygame">Pygame - Python 2D Games</option>
                            <option value="godot">Godot - Versatile Game Engine</option>
                            <option value="bevy">Bevy - Rust ECS Engine</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="game-description">Game Description</label>
                        <textarea id="game-description" rows="4" 
                                placeholder="Describe your game idea..." required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="art-style">Art Style</label>
                        <select id="art-style">
                            <option value="modern">Modern</option>
                            <option value="pixel">Pixel Art</option>
                            <option value="cyberpunk">Cyberpunk</option>
                            <option value="cartoon">Cartoon</option>
                            <option value="minimalist">Minimalist</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="complexity">Complexity Level</label>
                        <select id="complexity">
                            <option value="simple">Simple - Basic gameplay</option>
                            <option value="intermediate">Intermediate - Moderate features</option>
                            <option value="complex">Complex - Advanced systems</option>
                        </select>
                    </div>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <button type="submit" class="btn btn-primary" style="font-size: 1.2em; padding: 15px 30px;">
                            🚀 Generate Game
                        </button>
                    </div>
                </form>
            </div>
            
            <div style="background: #e8f4fd; padding: 20px; border-radius: 10px;">
                <h3 style="color: #2d3748; margin-bottom: 15px;">🎯 Workshop Features</h3>
                <ul style="color: #4a5568; line-height: 1.8;">
                    <li>🤖 AI-powered game generation</li>
                    <li>🎨 Automatic asset creation</li>
                    <li>🔧 Multi-engine support</li>
                    <li>⚡ Instant prototyping</li>
                    <li>📦 Ready-to-deploy packages</li>
                </ul>
            </div>
        </div>
        
        <script>
            async function generateGame(event) {
                event.preventDefault();
                
                const formData = {
                    title: document.getElementById('game-title').value,
                    engine: document.getElementById('game-engine').value,
                    description: document.getElementById('game-description').value,
                    art_style: document.getElementById('art-style').value,
                    complexity: document.getElementById('complexity').value
                };
                
                // Show loading state
                const button = event.target.querySelector('button[type="submit"]');
                const originalText = button.innerHTML;
                button.innerHTML = '🔄 Generating...';
                button.disabled = true;
                
                try {
                    const response = await fetch('/api/generate-game', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        alert('🎉 Game generated successfully!\\n\\nCheck your projects for the generated game.');
                        saveProgress({ type: 'game_created', data: formData });
                    } else {
                        alert('❌ Generation failed: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    alert('❌ Network error: ' + error.message);
                } finally {
                    button.innerHTML = originalText;
                    button.disabled = false;
                }
            }
        </script>
        """
    
    def get_academy_content(self):
        """Get Arcade Academy content."""
        
        return """
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="color: #a55eea; text-align: center; margin-bottom: 30px;">
                🎓 Arcade Academy
            </h1>
            
            <!-- Professor Pixel Introduction -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 30px; border-radius: 15px; margin-bottom: 30px; text-align: center;">
                <div class="professor-pixel">👨‍💻</div>
                <h2 style="margin-bottom: 15px;">Meet Professor Pixel</h2>
                <p style="font-size: 1.1em; line-height: 1.6; opacity: 0.95;">
                    Welcome to 2087, where corporations control all information. I'm Professor Pixel, 
                    and I need your help to teach coding to the digital resistance!
                </p>
            </div>
            
            <!-- Learning Path -->
            <div style="background: #f8f9fa; padding: 30px; border-radius: 10px; margin-bottom: 30px;">
                <h2 style="color: #2d3748; margin-bottom: 20px;">🚀 Your Learning Journey</h2>
                
                <div id="learning-modules" style="space-y: 15px;">
                    <div class="module" onclick="startModule('variables')" 
                         style="background: white; padding: 20px; border-radius: 8px; cursor: pointer; 
                                border-left: 4px solid #ff6b6b; margin-bottom: 15px;
                                transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                         onmouseover="this.style.transform='translateX(5px)'" 
                         onmouseout="this.style.transform='translateX(0)'">
                        <h3 style="color: #2d3748; margin-bottom: 10px;">🔥 Chapter 1: Variables & Data</h3>
                        <p style="color: #666; margin-bottom: 10px;">Learn to store and manipulate information in the digital world.</p>
                        <div style="background: #e2e8f0; height: 8px; border-radius: 4px;">
                            <div style="background: #4ecdc4; height: 8px; border-radius: 4px; width: 0%;"></div>
                        </div>
                    </div>
                    
                    <div class="module" onclick="startModule('loops')" 
                         style="background: white; padding: 20px; border-radius: 8px; cursor: pointer; 
                                border-left: 4px solid #4ecdc4; margin-bottom: 15px;
                                transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                         onmouseover="this.style.transform='translateX(5px)'" 
                         onmouseout="this.style.transform='translateX(0)'">
                        <h3 style="color: #2d3748; margin-bottom: 10px;">🔄 Chapter 2: Loops & Logic</h3>
                        <p style="color: #666; margin-bottom: 10px;">Master the power of repetition and decision-making.</p>
                        <div style="background: #e2e8f0; height: 8px; border-radius: 4px;">
                            <div style="background: #ff6b6b; height: 8px; border-radius: 4px; width: 0%;"></div>
                        </div>
                    </div>
                    
                    <div class="module" onclick="startModule('functions')" 
                         style="background: white; padding: 20px; border-radius: 8px; cursor: pointer; 
                                border-left: 4px solid #a55eea; margin-bottom: 15px;
                                transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                         onmouseover="this.style.transform='translateX(5px)'" 
                         onmouseout="this.style.transform='translateX(0)'">
                        <h3 style="color: #2d3748; margin-bottom: 10px;">🎯 Chapter 3: Functions & Classes</h3>
                        <p style="color: #666; margin-bottom: 10px;">Organize your code like a true cyber-architect.</p>
                        <div style="background: #e2e8f0; height: 8px; border-radius: 4px;">
                            <div style="background: #a55eea; height: 8px; border-radius: 4px; width: 0%;"></div>
                        </div>
                    </div>
                    
                    <div class="module" onclick="startModule('data-structures')" 
                         style="background: white; padding: 20px; border-radius: 8px; cursor: pointer; 
                                border-left: 4px solid #ffa726; margin-bottom: 15px;
                                transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                         onmouseover="this.style.transform='translateX(5px)'" 
                         onmouseout="this.style.transform='translateX(0)'">
                        <h3 style="color: #2d3748; margin-bottom: 10px;">📊 Chapter 4: Data Structures</h3>
                        <p style="color: #666; margin-bottom: 10px;">Handle complex information like a data-hacker.</p>
                        <div style="background: #e2e8f0; height: 8px; border-radius: 4px;">
                            <div style="background: #ffa726; height: 8px; border-radius: 4px; width: 0%;"></div>
                        </div>
                    </div>
                    
                    <div class="module" onclick="startModule('game-dev')" 
                         style="background: white; padding: 20px; border-radius: 8px; cursor: pointer; 
                                border-left: 4px solid #26de81; margin-bottom: 15px;
                                transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                         onmouseover="this.style.transform='translateX(5px)'" 
                         onmouseout="this.style.transform='translateX(0)'">
                        <h3 style="color: #2d3748; margin-bottom: 10px;">🎮 Chapter 5: Game Programming</h3>
                        <p style="color: #666; margin-bottom: 10px;">Build games that liberate minds from corporate control.</p>
                        <div style="background: #e2e8f0; height: 8px; border-radius: 4px;">
                            <div style="background: #26de81; height: 8px; border-radius: 4px; width: 0%;"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Student Progress -->
            <div style="background: linear-gradient(135deg, #a55eea 0%, #26de81 100%); 
                        color: white; padding: 25px; border-radius: 10px;">
                <h3 style="margin-bottom: 20px; text-align: center;">🏆 Your Progress</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; text-align: center;">
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">📚</div>
                        <div style="font-size: 1.5em; font-weight: bold;">0/5</div>
                        <div style="opacity: 0.9;">Chapters</div>
                    </div>
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">⭐</div>
                        <div style="font-size: 1.5em; font-weight: bold;">0</div>
                        <div style="opacity: 0.9;">Stars Earned</div>
                    </div>
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">🎮</div>
                        <div style="font-size: 1.5em; font-weight: bold;">0</div>
                        <div style="opacity: 0.9;">Games Built</div>
                    </div>
                    <div>
                        <div style="font-size: 2em; margin-bottom: 5px;">🏆</div>
                        <div style="font-size: 1.5em; font-weight: bold;">0/20</div>
                        <div style="opacity: 0.9;">Achievements</div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            function startModule(moduleId) {
                alert(`🎓 Starting ${moduleId} module!\\n\\nProfessor Pixel: "Let's hack the system together, young coder!"`);
                
                // Save progress
                saveProgress({ 
                    type: 'module_started', 
                    module: moduleId, 
                    timestamp: new Date().toISOString() 
                });
                
                // Simulate progress update
                updateModuleProgress(moduleId, 10);
            }
            
            function updateModuleProgress(moduleId, percentage) {
                // This would update the progress bar for the specific module
                console.log(`Module ${moduleId} progress: ${percentage}%`);
            }
        </script>
        """
    
    def serve_player_data(self):
        """Serve player data from SQLite."""
        
        player_data = self.get_or_create_player()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(player_data).encode())
    
    def handle_save_progress(self):
        """Handle saving player progress."""
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Save to SQLite
            self.save_player_progress(data)
            
            response = {"success": True, "message": "Progress saved"}
            
        except Exception as e:
            response = {"success": False, "error": str(e)}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def get_or_create_player(self):
        """Get or create player data in SQLite."""
        
        db_path = self.get_db_path()
        self.ensure_db_schema(db_path)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Try to get existing player (for now, just use ID 1)
            cursor.execute("SELECT * FROM players WHERE id = 1")
            player = cursor.fetchone()
            
            if player:
                player_data = {
                    "id": player[0],
                    "name": player[1],
                    "level": player[2],
                    "xp": player[3],
                    "games_created": player[4],
                    "modules_completed": player[5],
                    "created_at": player[6]
                }
            else:
                # Create new player
                cursor.execute("""
                    INSERT INTO players (name, level, xp, games_created, modules_completed) 
                    VALUES (?, ?, ?, ?, ?)
                """, ("Developer", 1, 0, 0, 0))
                
                player_id = cursor.lastrowid
                player_data = {
                    "id": player_id,
                    "name": "Developer",
                    "level": 1,
                    "xp": 0,
                    "games_created": 0,
                    "modules_completed": 0,
                    "created_at": "now"
                }
            
            conn.commit()
            conn.close()
            
            return player_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def save_player_progress(self, progress_data):
        """Save player progress to SQLite."""
        
        db_path = self.get_db_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Insert progress record
            cursor.execute("""
                INSERT INTO progress (player_id, type, data, timestamp) 
                VALUES (?, ?, ?, ?)
            """, (1, progress_data.get("type", "unknown"), 
                  json.dumps(progress_data), progress_data.get("timestamp", "now")))
            
            # Update player stats based on progress type
            progress_type = progress_data.get("type")
            if progress_type == "game_created":
                cursor.execute("UPDATE players SET games_created = games_created + 1, xp = xp + 100 WHERE id = 1")
            elif progress_type == "module_started":
                cursor.execute("UPDATE players SET xp = xp + 50 WHERE id = 1")
            elif progress_type == "module_completed":
                cursor.execute("UPDATE players SET modules_completed = modules_completed + 1, xp = xp + 200 WHERE id = 1")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error saving progress: {e}")
    
    def get_db_path(self):
        """Get database path."""
        
        # Create data directory if it doesn't exist
        data_dir = Path.home() / ".local" / "share" / "ai-game-dev"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        return data_dir / "player_data.db"
    
    def ensure_db_schema(self, db_path):
        """Ensure database schema exists."""
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    level INTEGER DEFAULT 1,
                    xp INTEGER DEFAULT 0,
                    games_created INTEGER DEFAULT 0,
                    modules_completed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create progress table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER,
                    type TEXT NOT NULL,
                    data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (player_id) REFERENCES players (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error creating database schema: {e}")
    
    def serve_api_status(self):
        """Serve API status."""
        
        status = {
            "status": "running",
            "platform": "AI Game Development Platform", 
            "version": "2.0.0",
            "features": {
                "split_panel_interface": True,
                "dynamic_content_switching": True,
                "sqlite_persistence": True,
                "game_workshop": True,
                "arcade_academy": True,
                "professor_pixel": True
            },
            "engines": ["pygame", "godot", "bevy"],
            "academy": {
                "name": "Arcade Academy",
                "instructor": "Professor Pixel",
                "modules": 5,
                "theme": "Cyberpunk 2087"
            }
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def handle_generate_game(self):
        """Handle game generation request."""
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            game_data = json.loads(post_data.decode('utf-8'))
            
            # Simulate game generation
            response = {
                "success": True,
                "message": f"Game '{game_data.get('title', 'Untitled')}' generation started!",
                "game_id": f"game_{hash(game_data.get('title', 'untitled'))}", 
                "engine": game_data.get("engine", "pygame"),
                "status": "generating",
                "estimated_time": "2-3 minutes",
                "features": ["AI-generated assets", "Dynamic gameplay", "Auto-deployment ready"]
            }
            
        except Exception as e:
            response = {"success": False, "error": str(e)}
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_chat(self):
        """Handle chat request."""
        
        response = {
            "response": "🤖 AI Assistant: The new split-panel interface is ready! Choose Game Workshop to create games or Arcade Academy to learn with Professor Pixel!",
            "status": "active",
            "suggestions": [
                "Tell me about the Game Workshop",
                "How does Arcade Academy work?", 
                "What can Professor Pixel teach me?",
                "Show me the available game engines"
            ]
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def serve_404(self):
        """Serve 404 page."""
        
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>404 - Page Not Found</h1><a href='/'>Go Home</a>")
    
    def log_message(self, format, *args):
        """Custom logging."""
        print(f"🌐 {self.address_string()} - {format % args}")


def run_minimal_server():
    """Run the minimal HTTP server."""
    
    print("🚀 Starting AI Game Development Platform with split-panel interface...")
    
    server = HTTPServer(("0.0.0.0", 5000), GameDevHandler)
    
    print("✅ Server ready at http://0.0.0.0:5000")
    print("🎮 Game Workshop | 🎓 Arcade Academy")
    print("📊 SQLite persistence enabled")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()


if __name__ == "__main__":
    run_minimal_server()