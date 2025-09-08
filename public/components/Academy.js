// Academy Component for Chainlit
class Academy {
    constructor(sendMessage, element) {
        this.sendMessage = sendMessage;
        this.element = element;
        this.currentLesson = null;
        this.progress = { level: 1, xp: 0, lessons: [] };
        this.init();
    }

    init() {
        this.render();
        this.attachEventListeners();
    }

    render() {
        this.element.innerHTML = `
            <div class="academy-content">
                <!-- Header with Professor Pixel -->
                <div class="glass-panel p-6 mb-6 relative overflow-hidden">
                    <div class="flex items-center gap-4">
                        <img src="/public/static/assets/characters/professor-pixel.png" 
                             class="w-24 h-24 rounded-full border-4 border-purple-500 glow">
                        <div>
                            <h1 class="text-3xl font-bold mb-2 text-purple-300">🎓 Arcade Academy</h1>
                            <p class="text-gray-300">Learn programming through adventure with Professor Pixel!</p>
                        </div>
                    </div>
                    <div class="absolute top-0 right-0 w-32 h-32 bg-purple-500/20 rounded-full blur-3xl"></div>
                </div>

                <!-- Progress Dashboard -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div class="glass-panel p-4 text-center">
                        <div class="text-3xl font-bold text-cyan-300">${this.progress.level}</div>
                        <div class="text-sm text-gray-400">Level</div>
                    </div>
                    <div class="glass-panel p-4 text-center">
                        <div class="text-3xl font-bold text-purple-300">${this.progress.xp}</div>
                        <div class="text-sm text-gray-400">Experience</div>
                    </div>
                    <div class="glass-panel p-4 text-center">
                        <div class="text-3xl font-bold text-green-300">${this.progress.lessons.length}</div>
                        <div class="text-sm text-gray-400">Lessons</div>
                    </div>
                </div>

                <!-- Main Game Area -->
                <div class="glass-panel p-6 mb-6">
                    <div id="gameScreen" class="relative h-96 bg-gray-900 rounded-lg overflow-hidden">
                        <!-- Welcome Screen -->
                        <div id="welcomeScreen" class="h-full flex flex-col items-center justify-center text-center p-8">
                            <h2 class="text-2xl font-bold mb-4 text-cyan-300">
                                Welcome to NeoTokyo Code Academy
                            </h2>
                            <p class="mb-6 text-gray-300">
                                Join the Binary Rebellion and learn to code through an epic adventure!
                            </p>
                            <button id="startLessonBtn" class="custom-button px-8 py-4 text-lg rounded-lg">
                                Start Your Journey
                            </button>
                        </div>

                        <!-- Game View (hidden initially) -->
                        <div id="gameView" class="hidden h-full">
                            <canvas id="gameCanvas" class="w-full h-full"></canvas>
                        </div>
                    </div>

                    <!-- Dialogue Box -->
                    <div id="dialogueBox" class="hidden mt-4 glass-panel p-4">
                        <div class="flex items-start gap-3">
                            <img id="speakerAvatar" src="" class="w-12 h-12 rounded-full">
                            <div class="flex-1">
                                <div id="speakerName" class="font-bold text-cyan-300 mb-1"></div>
                                <div id="dialogueText" class="text-gray-200"></div>
                            </div>
                        </div>
                        <div id="dialogueChoices" class="mt-4 space-y-2"></div>
                    </div>

                    <!-- Code Editor -->
                    <div id="codeEditor" class="hidden mt-4">
                        <div class="bg-gray-900 rounded-lg p-4 font-mono text-sm">
                            <div class="mb-2 text-gray-400"># Your Code:</div>
                            <textarea 
                                id="codeInput"
                                class="w-full h-32 bg-gray-800 text-green-400 p-2 rounded border border-gray-700 focus:border-cyan-500 focus:outline-none"
                                spellcheck="false"
                            ></textarea>
                            <div class="mt-2 flex gap-2">
                                <button id="runCodeBtn" class="btn btn-sm btn-success">Run Code</button>
                                <button id="hintBtn" class="btn btn-sm btn-info">Get Hint</button>
                            </div>
                        </div>
                        <div id="codeOutput" class="mt-2 hidden bg-gray-900 rounded p-3 text-sm">
                            <div class="text-gray-400 mb-1">Output:</div>
                            <div id="outputText" class="text-cyan-300 font-mono"></div>
                        </div>
                    </div>
                </div>

                <!-- Lesson Navigation -->
                <div class="glass-panel p-4">
                    <h3 class="font-bold mb-3 text-purple-300">Available Lessons</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <button class="lesson-btn" data-lesson="variables">
                            <div class="text-left">
                                <div class="font-semibold">Variables & Data Types</div>
                                <div class="text-sm text-gray-400">Learn the basics of storing data</div>
                            </div>
                        </button>
                        <button class="lesson-btn" data-lesson="loops">
                            <div class="text-left">
                                <div class="font-semibold">Loops & Iteration</div>
                                <div class="text-sm text-gray-400">Master repetitive tasks</div>
                            </div>
                        </button>
                        <button class="lesson-btn" data-lesson="conditions">
                            <div class="text-left">
                                <div class="font-semibold">Conditionals</div>
                                <div class="text-sm text-gray-400">Make decisions in your code</div>
                            </div>
                        </button>
                        <button class="lesson-btn" data-lesson="functions">
                            <div class="text-left">
                                <div class="font-semibold">Functions</div>
                                <div class="text-sm text-gray-400">Create reusable code blocks</div>
                            </div>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        // Start lesson button
        const startBtn = this.element.querySelector('#startLessonBtn');
        startBtn?.addEventListener('click', () => {
            this.sendMessage('start lesson');
            this.showGameView();
        });

        // Lesson selection buttons
        this.element.querySelectorAll('.lesson-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const lesson = btn.dataset.lesson;
                this.sendMessage(`start lesson ${lesson}`);
                this.showGameView();
            });
        });

        // Code editor buttons
        const runCodeBtn = this.element.querySelector('#runCodeBtn');
        runCodeBtn?.addEventListener('click', () => this.runCode());

        const hintBtn = this.element.querySelector('#hintBtn');
        hintBtn?.addEventListener('click', () => this.sendMessage('hint'));
    }

    showGameView() {
        const welcomeScreen = this.element.querySelector('#welcomeScreen');
        const gameView = this.element.querySelector('#gameView');
        welcomeScreen.classList.add('hidden');
        gameView.classList.remove('hidden');
        this.initializeGame();
    }

    initializeGame() {
        // Initialize the game canvas
        const canvas = this.element.querySelector('#gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        
        // Draw initial game state
        ctx.fillStyle = '#1a1a2e';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Add cyberpunk grid effect
        ctx.strokeStyle = 'rgba(100, 255, 218, 0.1)';
        ctx.lineWidth = 1;
        
        for (let x = 0; x < canvas.width; x += 30) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        
        for (let y = 0; y < canvas.height; y += 30) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }
        
        // Show Professor Pixel dialogue
        this.showDialogue(
            'Professor Pixel',
            '/public/static/assets/characters/professor-pixel.png',
            'Welcome to the Academy! Ready to begin your coding journey?'
        );
    }

    showDialogue(speaker, avatar, text, choices = []) {
        const dialogueBox = this.element.querySelector('#dialogueBox');
        const speakerAvatar = this.element.querySelector('#speakerAvatar');
        const speakerName = this.element.querySelector('#speakerName');
        const dialogueText = this.element.querySelector('#dialogueText');
        const dialogueChoices = this.element.querySelector('#dialogueChoices');
        
        dialogueBox.classList.remove('hidden');
        speakerAvatar.src = avatar;
        speakerName.textContent = speaker;
        dialogueText.textContent = text;
        
        // Clear and add choices
        dialogueChoices.innerHTML = '';
        choices.forEach(choice => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-sm btn-outline btn-cyan w-full';
            btn.textContent = choice.text;
            btn.addEventListener('click', () => {
                this.sendMessage(choice.action);
            });
            dialogueChoices.appendChild(btn);
        });
    }

    showCodeEditor() {
        const codeEditor = this.element.querySelector('#codeEditor');
        codeEditor.classList.remove('hidden');
    }

    runCode() {
        const codeInput = this.element.querySelector('#codeInput');
        const code = codeInput.value;
        this.sendMessage(`run_code: ${code}`);
    }

    updateState(state) {
        // Handle UI state updates from backend
        switch (state.type) {
            case 'academy_start':
                // Academy flow started
                this.showWelcome();
                break;
            case 'academy_update':
                if (state.stage === 'skill_assessment') {
                    // Show skill assessment
                    this.showSkillAssessment(state.question);
                }
                break;
            case 'academy_lesson':
                // Lesson started
                this.currentLesson = state.lesson;
                this.updateProgressDisplay(state.progress);
                break;
            case 'academy_progress':
                // Progress update
                this.progress = state.progress;
                this.updateProgressDisplay(state.progress);
                if (state.stage === 'lesson_complete') {
                    this.showLessonComplete();
                }
                break;
        }
    }
    
    handleMessage(message) {
        // Handle incoming messages from Chainlit
        if (message.type === 'dialogue') {
            this.showDialogue(
                message.speaker,
                message.avatar,
                message.text,
                message.choices
            );
        } else if (message.type === 'show_code_editor') {
            this.showCodeEditor();
        } else if (message.type === 'code_output') {
            this.showCodeOutput(message.output, message.success);
        } else if (message.type === 'progress_update') {
            this.updateProgress(message.progress);
        }
    }
    
    showWelcome() {
        // Show welcome screen with start button
        const gameScreen = this.element.querySelector('#gameScreen');
        gameScreen.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full">
                <h2 class="text-2xl font-bold mb-4">Welcome to Arcade Academy!</h2>
                <p class="mb-6">Ready to learn programming through game creation?</p>
                <button class="custom-button px-6 py-3" onclick="app.academy.sendMessage('start')">
                    Start Learning!
                </button>
            </div>
        `;
    }
    
    showSkillAssessment(question) {
        // Show skill assessment question
        const gameScreen = this.element.querySelector('#gameScreen');
        // Implementation handled by existing dialogue system
    }
    
    updateProgressDisplay(progress) {
        // Update the progress displays
        if (progress) {
            this.progress = progress;
            // Update level
            const levelDisplay = this.element.querySelector('.text-3xl.text-cyan-300');
            if (levelDisplay) levelDisplay.textContent = progress.level;
            // Update XP
            const xpDisplay = this.element.querySelector('.text-3xl.text-purple-300');
            if (xpDisplay) xpDisplay.textContent = progress.xp;
            // Update lessons
            const lessonsDisplay = this.element.querySelector('.text-3xl.text-green-300');
            if (lessonsDisplay) lessonsDisplay.textContent = progress.lessons.length;
        }
    }
    
    showLessonComplete() {
        // Show lesson complete celebration
        const gameScreen = this.element.querySelector('#gameScreen');
        gameScreen.innerHTML += `
            <div class="absolute inset-0 flex items-center justify-center bg-black/50">
                <div class="glass-panel p-8 text-center">
                    <h2 class="text-3xl font-bold mb-4 text-green-400">🎉 Lesson Complete!</h2>
                    <p class="text-xl mb-4">Great job! You've earned XP!</p>
                    <button class="custom-button" onclick="app.academy.sendMessage('continue')">
                        Next Lesson
                    </button>
                </div>
            </div>
        `;
    }

    showCodeOutput(output, success) {
        const codeOutput = this.element.querySelector('#codeOutput');
        const outputText = this.element.querySelector('#outputText');
        
        codeOutput.classList.remove('hidden');
        outputText.textContent = output;
        outputText.className = success ? 'text-green-400 font-mono' : 'text-red-400 font-mono';
    }

    updateProgress(progress) {
        this.progress = progress;
        // Re-render progress section
        this.element.querySelector('.grid').innerHTML = `
            <div class="glass-panel p-4 text-center">
                <div class="text-3xl font-bold text-cyan-300">${progress.level}</div>
                <div class="text-sm text-gray-400">Level</div>
            </div>
            <div class="glass-panel p-4 text-center">
                <div class="text-3xl font-bold text-purple-300">${progress.xp}</div>
                <div class="text-sm text-gray-400">Experience</div>
            </div>
            <div class="glass-panel p-4 text-center">
                <div class="text-3xl font-bold text-green-300">${progress.lessons.length}</div>
                <div class="text-sm text-gray-400">Lessons</div>
            </div>
        `;
    }
}

// Export for use in Chainlit
window.Academy = Academy;