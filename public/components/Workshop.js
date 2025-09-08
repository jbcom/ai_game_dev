// Workshop Component for Chainlit
class Workshop {
    constructor(sendMessage, element) {
        this.sendMessage = sendMessage;
        this.element = element;
        this.selectedEngine = '';
        this.isGenerating = false;
        this.generatedAssets = [];
        this.uploadedSpec = null;
        this.activeTab = 'describe';
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.element.innerHTML = `
            <div class="workshop-content">
                <!-- Header -->
                <div class="glass-panel p-6 mb-6">
                    <h1 class="text-3xl font-bold mb-2 text-cyan-300">🚀 Game Workshop</h1>
                    <p class="text-gray-300">Transform your ideas into playable games with AI</p>
                </div>

                <!-- Engine Selection -->
                <div class="mb-6">
                    <h2 class="text-xl font-semibold mb-4 text-white">Choose Your Engine</h2>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="engine-card" data-engine="pygame">
                            <div class="glass-panel p-4 cursor-pointer hover:border-cyan-500 transition-all">
                                <div class="engine-icon-placeholder mb-2 text-4xl">🐍</div>
                                <h3 class="font-bold">Pygame</h3>
                                <p class="text-sm text-gray-400">Perfect for 2D games</p>
                            </div>
                        </div>
                        <div class="engine-card" data-engine="godot">
                            <div class="glass-panel p-4 cursor-pointer hover:border-cyan-500 transition-all">
                                <div class="engine-icon-placeholder mb-2 text-4xl">🎮</div>
                                <h3 class="font-bold">Godot</h3>
                                <p class="text-sm text-gray-400">Professional 2D/3D</p>
                            </div>
                        </div>
                        <div class="engine-card" data-engine="bevy">
                            <div class="glass-panel p-4 cursor-pointer hover:border-cyan-500 transition-all">
                                <div class="engine-icon-placeholder mb-2 text-4xl">🦀</div>
                                <h3 class="font-bold">Bevy</h3>
                                <p class="text-sm text-gray-400">Rust-based ECS</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Game Description -->
                <div class="glass-panel p-6 mb-6">
                    <h2 class="text-xl font-semibold mb-4 text-white">Describe Your Game</h2>
                    
                    <!-- Tabs for description vs spec upload -->
                    <div class="tabs mb-4">
                        <button class="tab-btn active" data-tab="describe">Describe Game</button>
                        <button class="tab-btn" data-tab="upload">Upload Spec</button>
                    </div>
                    
                    <!-- Description Tab -->
                    <div id="describeTab" class="tab-content active">
                        <textarea
                            id="gameDescription"
                            class="w-full h-32 bg-gray-800 text-white p-4 rounded-lg border border-cyan-500/30 focus:border-cyan-500 focus:outline-none resize-none"
                            placeholder="Example: A cyberpunk platformer with hacking mechanics..."
                        ></textarea>
                    </div>
                    
                    <!-- Upload Tab -->
                    <div id="uploadTab" class="tab-content hidden">
                        <div class="upload-area border-2 border-dashed border-cyan-500/30 rounded-lg p-8 text-center">
                            <input type="file" id="specFile" accept=".toml,.json" class="hidden" />
                            <label for="specFile" class="cursor-pointer">
                                <p class="text-lg mb-2">📄 Drop game spec here or click to browse</p>
                                <p class="text-sm text-gray-400">Supports .toml and .json formats</p>
                            </label>
                            <div id="specPreview" class="mt-4 hidden">
                                <p class="text-sm text-cyan-300">Selected: <span id="specFileName"></span></p>
                            </div>
                        </div>
                    </div>
                    
                    <button
                        id="generateBtn"
                        class="custom-button mt-4 px-6 py-3 rounded-lg font-semibold"
                    >
                        Generate Game
                    </button>
                </div>

                <!-- Progress Section -->
                <div id="progressSection" class="hidden">
                    <div class="glass-panel p-6 mb-6">
                        <h3 class="text-lg font-semibold mb-2">Generation Progress</h3>
                        <div class="progress progress-primary w-full">
                            <div class="progress-bar" style="width: 0%"></div>
                        </div>
                        <p id="progressStage" class="mt-2 text-sm text-gray-400">Initializing...</p>
                    </div>
                </div>

                <!-- Results Section -->
                <div id="resultsSection" class="hidden">
                    <!-- Generated assets and code will appear here -->
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Engine selection
        this.element.querySelectorAll('.engine-card').forEach(card => {
            card.addEventListener('click', () => {
                this.selectedEngine = card.dataset.engine;
                this.updateEngineSelection();
            });
        });

        // Tab switching
        this.element.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.activeTab = btn.dataset.tab;
                this.updateTabs();
            });
        });

        // File upload
        const fileInput = this.element.querySelector('#specFile');
        fileInput.addEventListener('change', (e) => this.handleFileUpload(e));

        // Generate button
        const generateBtn = this.element.querySelector('#generateBtn');
        generateBtn.addEventListener('click', () => this.handleGenerate());
    }

    updateEngineSelection() {
        this.element.querySelectorAll('.engine-card').forEach(card => {
            const panel = card.querySelector('.glass-panel');
            if (card.dataset.engine === this.selectedEngine) {
                panel.classList.add('border-cyan-500', 'glow');
            } else {
                panel.classList.remove('border-cyan-500', 'glow');
            }
        });
    }

    updateTabs() {
        // Update tab buttons
        this.element.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.dataset.tab === this.activeTab) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update tab content
        const describeTab = this.element.querySelector('#describeTab');
        const uploadTab = this.element.querySelector('#uploadTab');
        
        if (this.activeTab === 'describe') {
            describeTab.classList.remove('hidden');
            describeTab.classList.add('active');
            uploadTab.classList.add('hidden');
            uploadTab.classList.remove('active');
        } else {
            describeTab.classList.add('hidden');
            describeTab.classList.remove('active');
            uploadTab.classList.remove('hidden');
            uploadTab.classList.add('active');
        }
    }

    async handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = async (e) => {
            this.uploadedSpec = {
                name: file.name,
                content: e.target.result
            };
            
            // Show preview
            const preview = this.element.querySelector('#specPreview');
            const fileName = this.element.querySelector('#specFileName');
            preview.classList.remove('hidden');
            fileName.textContent = file.name;
        };
        reader.readAsText(file);
    }

    handleGenerate() {
        if (this.activeTab === 'describe') {
            const description = this.element.querySelector('#gameDescription').value.trim();
            if (!description) {
                alert('Please describe your game first!');
                return;
            }
            
            if (!this.selectedEngine) {
                alert('Please select an engine first!');
                return;
            }

            this.isGenerating = true;
            this.showProgress();

            // First send the engine selection
            this.sendMessage(this.selectedEngine);
            
            // Then send the description after a short delay
            setTimeout(() => {
                this.sendMessage(description);
            }, 100);
        } else {
            // Upload mode
            if (!this.uploadedSpec) {
                alert('Please upload a game specification file!');
                return;
            }

            this.isGenerating = true;
            this.showProgress();

            // Send spec file indicator and content
            this.sendMessage('spec_upload');
            
            // Send the spec content after a short delay
            setTimeout(() => {
                this.sendMessage(JSON.stringify({
                    type: 'game_spec',
                    filename: this.uploadedSpec.name,
                    content: this.uploadedSpec.content
                }));
            }, 100);
        }
    }

    showProgress() {
        const progressSection = this.element.querySelector('#progressSection');
        progressSection.classList.remove('hidden');
        
        // Simulate progress updates
        let progress = 0;
        const progressBar = progressSection.querySelector('.progress-bar');
        const progressStage = progressSection.querySelector('#progressStage');
        
        const stages = [
            'Analyzing requirements...',
            'Generating game architecture...',
            'Creating visual assets...',
            'Composing audio...',
            'Writing game code...',
            'Finalizing project...'
        ];
        
        let stageIndex = 0;
        const interval = setInterval(() => {
            progress += 16.66;
            progressBar.style.width = `${Math.min(progress, 100)}%`;
            
            if (stageIndex < stages.length) {
                progressStage.textContent = stages[stageIndex];
                stageIndex++;
            }
            
            if (progress >= 100) {
                clearInterval(interval);
                this.isGenerating = false;
            }
        }, 1000);
    }

    handleMessage(message) {
        // Handle incoming messages from Chainlit
        if (message.type === 'generation_complete') {
            this.showResults(message.data);
        }
    }
    
    updateState(state) {
        // Handle UI state updates from backend
        switch (state.type) {
            case 'workshop_start':
                // Workshop flow started
                break;
            case 'workshop_update':
                if (state.stage === 'game_description') {
                    // Engine was accepted, ready for description
                    const engineCards = this.element.querySelectorAll('.engine-card');
                    engineCards.forEach(card => {
                        card.style.opacity = '0.5';
                        card.style.pointerEvents = 'none';
                    });
                }
                break;
            case 'workshop_complete':
                // Game generation complete
                this.isGenerating = false;
                this.showResults(state);
                break;
        }
    }

    showResults(data) {
        const resultsSection = this.element.querySelector('#resultsSection');
        resultsSection.classList.remove('hidden');
        resultsSection.innerHTML = `
            <div class="glass-panel p-6">
                <h3 class="text-xl font-bold mb-4 text-cyan-300">✅ Game Generated!</h3>
                <p class="mb-4">${data.description}</p>
                <div class="grid grid-cols-2 gap-4">
                    <button class="btn btn-primary">Download Project</button>
                    <button class="btn btn-secondary">View Code</button>
                </div>
            </div>
        `;
    }
}

// Export for use in Chainlit
window.Workshop = Workshop;