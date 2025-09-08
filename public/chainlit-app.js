// Main Chainlit App Integration
class ChainlitApp {
    constructor() {
        this.currentView = 'home';
        this.videoOverlay = null;
        this.workshop = null;
        this.academy = null;
        this.audioManager = new AudioManager();
        this.init();
    }

    init() {
        // Wait for Chainlit to be ready
        if (window.chainlit) {
            this.setupApp();
        } else {
            // Try multiple ways to ensure we initialize
            window.addEventListener('chainlit-ready', () => this.setupApp());
            // Also try DOMContentLoaded
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => {
                    setTimeout(() => {
                        if (!window.chainlit) {
                            console.log('Chainlit not ready, initializing UI anyway');
                            this.setupApp();
                        }
                    }, 100);
                });
            } else {
                // DOM already loaded
                setTimeout(() => {
                    if (!window.chainlit) {
                        console.log('Chainlit not ready, initializing UI anyway');
                        this.setupApp();
                    }
                }, 100);
            }
        }
    }

    setupApp() {
        this.render();
        this.attachEventListeners();
        this.connectToChainlit();
    }

    render() {
        document.body.innerHTML = `
            <div class="min-h-screen game-dev-gradient">
                <!-- Tech Frame Container -->
                <div class="window-frame">
                    <div class="inner-content-frame">
                        <!-- Back Button -->
                        <a href="#" class="back-button" style="display: none;" onclick="app.goHome()">
                            ← Back to Home
                        </a>
                        
                        <!-- Dynamic Content Area -->
                        <div id="dynamic-content">
                            <!-- Content will be loaded here -->
                        </div>
                    </div>
                    
                    <!-- Video Overlay -->
                    <div id="video-overlay" class="video-overlay" style="display: none;">
                        <div class="video-container">
                            <button class="skip-video" onclick="app.skipVideo()">Skip Intro ⏭️</button>
                            <video id="intro-video" class="intro-video" autoplay muted onended="app.onVideoEnd()">
                                <source src="" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                    </div>
                </div>
                
                <!-- Audio Toggle -->
                <button id="audioToggle" 
                        class="fixed bottom-4 right-4 btn btn-circle btn-sm glass"
                        onclick="toggleAudio()"
                        title="Toggle Sound Effects">
                    🔊
                </button>
            </div>
        `;

        // Load initial view
        this.loadView('home');
    }

    loadView(view) {
        const content = document.getElementById('dynamic-content');
        const backButton = document.querySelector('.back-button');
        
        this.currentView = view;
        
        // Show/hide back button
        backButton.style.display = view === 'home' ? 'none' : 'block';
        
        switch(view) {
            case 'home':
                this.loadHomePage(content);
                break;
            case 'workshop':
                this.loadWorkshop(content);
                break;
            case 'academy':
                this.loadAcademy(content);
                break;
        }
    }

    loadHomePage(container) {
        container.innerHTML = `
            <div id="split-panel-home">
                <!-- Clean Header -->
                <div class="text-center py-2 mb-3 flex-shrink-0">
                    <h1 class="text-xl font-bold mb-1 text-white">🎮 AI Game Development Platform</h1>
                    <p class="text-sm opacity-80 text-cyan-300">Choose your path: Create games or master programming</p>
                </div>
                
                <!-- Horizontal Panel Interface -->
                <div style="display: flex; gap: 0; height: 100%; width: 100%;">
                    <!-- Game Workshop Panel -->
                    <div style="flex: 1; width: 50%; position: relative; cursor: pointer; overflow: hidden; 
                                border-top-left-radius: 12px; border-bottom-left-radius: 12px; margin: 0; padding: 0;"
                         class="workshop-panel horizontal-panel" 
                         onclick="app.playVideo('workshop')">
                        <div class="panel-overlay"></div>
                        <img src="/public/static/assets/logos/game-workshop-condensed.png" 
                             alt="Game Workshop" 
                             class="panel-logo">
                    </div>
                    
                    <!-- Arcade Academy Panel -->
                    <div style="flex: 1; width: 50%; position: relative; cursor: pointer; overflow: hidden; 
                                border-top-right-radius: 12px; border-bottom-right-radius: 12px; margin: 0; padding: 0;"
                         class="academy-panel horizontal-panel" 
                         onclick="app.playVideo('academy')">
                        <div class="panel-overlay"></div>
                        <img src="/public/static/assets/logos/arcade-academy-condensed.png" 
                             alt="Arcade Academy" 
                             class="panel-logo">
                    </div>
                </div>
            </div>
        `;
    }

    loadWorkshop(container) {
        // Load Workshop component
        this.workshop = new Workshop(this.sendMessage.bind(this), container);
    }

    loadAcademy(container) {
        // Load Academy component
        this.academy = new Academy(this.sendMessage.bind(this), container);
    }

    playVideo(type) {
        const videoSrc = type === 'workshop' 
            ? '/public/static/assets/videos/game-workshop-intro.mp4'
            : '/public/static/assets/videos/arcade-academy-intro.mp4';
        
        const video = document.getElementById('intro-video');
        const videoOverlay = document.getElementById('video-overlay');
        
        video.src = videoSrc;
        videoOverlay.style.display = 'flex';
        
        this.audioManager.play('success');
        
        // Store which view to load after video
        this.pendingView = type;
    }

    onVideoEnd() {
        document.getElementById('video-overlay').style.display = 'none';
        this.audioManager.play('notification');
        
        if (this.pendingView) {
            this.loadView(this.pendingView);
            this.pendingView = null;
        }
    }

    skipVideo() {
        const video = document.getElementById('intro-video');
        video.pause();
        this.onVideoEnd();
        this.audioManager.play('click');
    }

    goHome() {
        this.loadView('home');
        this.audioManager.play('click');
    }

    connectToChainlit() {
        // Connect to Chainlit WebSocket
        if (window.chainlit) {
            window.chainlit.on('message', (message) => {
                this.handleChainlitMessage(message);
            });
            
            // Send initial connection message
            this.sendMessage('connected');
        }
    }

    sendMessage(message) {
        if (window.chainlit && window.chainlit.sendMessage) {
            window.chainlit.sendMessage(message);
        } else {
            console.error('Chainlit not available');
        }
    }

    handleChainlitMessage(message) {
        // Route messages to appropriate component
        if (this.currentView === 'workshop' && this.workshop) {
            this.workshop.handleMessage(message);
        } else if (this.currentView === 'academy' && this.academy) {
            this.academy.handleMessage(message);
        }
    }

    attachEventListeners() {
        // Global keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentView !== 'home') {
                this.goHome();
            }
        });
    }
}

// Audio Manager from original implementation
class AudioManager {
    constructor() {
        this.sounds = {
            click: new Audio('/public/static/assets/audio/button_click_futuristic.wav'),
            hover: new Audio('/public/static/assets/audio/hover_beep_cyberpunk.wav'),
            success: new Audio('/public/static/assets/audio/success_ding_pleasant.wav'),
            error: new Audio('/public/static/assets/audio/error_buzz_warning.wav'),
            notification: new Audio('/public/static/assets/audio/notification_chime_tech.wav'),
            typing: new Audio('/public/static/assets/audio/typing_mechanical_keyboard.wav')
        };
        this.enabled = true;
        this.volume = 0.3;
        
        // Set volume for all sounds
        Object.values(this.sounds).forEach(sound => {
            sound.volume = this.volume;
        });
        
        this.attachGlobalListeners();
    }
    
    play(soundName) {
        if (this.enabled && this.sounds[soundName]) {
            this.sounds[soundName].currentTime = 0;
            this.sounds[soundName].play().catch(() => {
                // Ignore autoplay policy errors
            });
        }
    }
    
    toggle() {
        this.enabled = !this.enabled;
        const toggle = document.getElementById('audioToggle');
        if (toggle) {
            toggle.textContent = this.enabled ? '🔊' : '🔇';
            toggle.title = this.enabled ? 'Disable Sound Effects' : 'Enable Sound Effects';
        }
        return this.enabled;
    }
    
    attachGlobalListeners() {
        // Button clicks
        document.addEventListener('click', (e) => {
            if (e.target.matches('button, .btn, a[href]')) {
                this.play('click');
            }
        });
        
        // Hover effects
        document.addEventListener('mouseover', (e) => {
            if (e.target.matches('button, .btn, .tab, .engine-card')) {
                this.play('hover');
            }
        });
        
        // Typing
        document.addEventListener('input', (e) => {
            if (e.target.matches('textarea, input[type="text"]')) {
                this.play('typing');
            }
        });
    }
}

// Global functions
window.toggleAudio = function() {
    if (window.app && window.app.audioManager) {
        window.app.audioManager.toggle();
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new ChainlitApp();
});