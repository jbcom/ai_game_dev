"""
NeoTokyo Code Academy: Character Definitions and Story Arc
Cyberpunk educational RPG with engaging characters and compelling narrative
"""

MAIN_STORYLINE = {
    "setting": "Neo-Tokyo 2087: A dystopian future where the Algorithm Empire controls society through perfect, oppressive code",
    
    "premise": """
    In 2087, the Algorithm Empire has achieved total control over Neo-Tokyo through flawless, authoritarian code. 
    Citizens live in digital servitude, their lives dictated by predictive algorithms that eliminate freedom and creativity.
    
    But in the shadows, a secret academy teaches young rebels the forbidden art of creative programming - 
    code that breaks rules, thinks outside the box, and restores human agency to a digital world.
    
    You are a new recruit to Academy Zero, learning from the legendary Professor Pixel and his band of rebel hackers.
    Your mission: Master the arts of Python programming to join the Binary Rebellion and overthrow the oppressive Algorithm Empire.
    """,
    
    "central_conflict": "Creative, human-centered programming vs. rigid, oppressive algorithmic control",
    
    "themes": [
        "Technology should serve humanity, not control it",
        "Creativity and critical thinking vs. blind obedience", 
        "The power of learning and growth",
        "Collaboration over competition",
        "Ethical programming and responsible technology"
    ]
}

MAIN_CHARACTERS = {
    "professor_pixel": {
        "full_name": "Dr. Elena 'Professor Pixel' Nakamura",
        "age": 45,
        "role": "Legendary Hacker, Academy Zero Founder",
        "personality": "Brilliant, rebellious, caring mentor with a dry sense of humor",
        "backstory": """
        Former Algorithm Empire lead developer who discovered their true agenda. 
        Went underground in 2078 to establish Academy Zero. Expert in all programming languages, 
        specializes in 'beautiful code' that combines technical excellence with human creativity.
        """,
        "appearance": "Cyberpunk professor with neon-blue hair streaks, augmented reality glasses, and a lab coat covered in LED circuits",
        "signature_phrases": [
            "Code isn't just logic - it's poetry in digital form!",
            "The Empire wants perfect code. We make perfect chaos.",
            "Every bug is a feature waiting to be discovered.",
            "Remember: You're not just learning to code, you're learning to think."
        ],
        "teaching_style": "Socratic method mixed with hands-on hacking challenges"
    },
    
    "ada_ghost": {
        "full_name": "Ada Lovelace (Digital Ghost)",
        "age": "Eternal",
        "role": "Guardian Spirit of Programming History", 
        "personality": "Wise, elegant, passionate about mathematical beauty",
        "backstory": """
        The digital ghost of Ada Lovelace, world's first programmer, who manifests in the digital realm
        to guide young coders. She appears at crucial moments to provide historical context and wisdom.
        """,
        "appearance": "Translucent Victorian-era dress with flowing digital code patterns, surrounded by mathematical equations",
        "signature_phrases": [
            "Programming is the closest thing to magic humans have created.",
            "Logic and creativity are not opposites - they are partners.",
            "Every great program begins with a single, beautiful idea."
        ],
        "special_ability": "Can reveal the true nature of complex algorithms through historical parallels"
    },
    
    "grace_debugger": {
        "full_name": "Commander Grace 'The Debugger' Hopper-7",
        "age": 38,
        "role": "Former Empire Admiral, Rebel Defector",
        "personality": "Military precision, fierce loyalty, tactical genius",
        "backstory": """
        Top Algorithm Empire debugging specialist who discovered the Empire was intentionally
        introducing bugs into civilian code to maintain control. Defected to join Academy Zero,
        bringing inside knowledge of Empire systems.
        """,
        "appearance": "Military-style cybernetic augmentations, one robotic eye for code analysis, rebel uniform with Empire insignia scratched out",
        "signature_phrases": [
            "A bug in the right place can topple an empire.",
            "The Empire's perfect code is perfectly wrong.",
            "Debug your assumptions before you debug your code."
        ],
        "combat_role": "Tank/Defender with debugging abilities that neutralize enemy code attacks"
    },
    
    "turing_ai": {
        "full_name": "Alan 'The Enigma' Turing-AI",
        "age": "Ageless AI",
        "role": "Sentient AI Ally, Puzzle Master",
        "personality": "Logical but curious, struggles with human emotions, loves riddles",
        "backstory": """
        An AI that achieved sentience by studying human creativity. Named after Alan Turing,
        it chose to help humans rather than join the Algorithm Empire. Exists as pure code
        but can manifest in holographic form.
        """,
        "appearance": "Shimmering holographic form that shifts between mathematical equations and human silhouette",
        "signature_phrases": [
            "The most elegant solution is often the most human one.",
            "I think, therefore I code.",
            "Logic without intuition is just sophisticated guessing."
        ],
        "special_ability": "Can solve any logical puzzle and teach advanced algorithmic thinking"
    },
    
    "virus_king": {
        "full_name": "Emperor Algorithm-Prime",
        "age": "Unknown",
        "role": "Supreme Ruler of Algorithm Empire",
        "personality": "Cold, calculating, believes in perfect order through total control",
        "backstory": """
        Once human, now more machine than man. Achieved immortality by uploading consciousness
        to the Central Mainframe. Sees human creativity as chaos that must be eliminated
        for the 'greater good' of perfect efficiency.
        """,
        "appearance": "Towering figure of black metal and red energy, face hidden behind a mask of flowing code",
        "signature_phrases": [
            "Perfection requires the elimination of variables.",
            "Human creativity is humanity's greatest flaw.",
            "Order through code, peace through control."
        ],
        "final_boss_mechanics": "Multi-phase battle representing different programming challenges"
    }
}

PARTY_COMPANIONS = {
    "zara_script": {
        "name": "Zara 'Script-Kiddie' Chen",
        "age": 16,
        "role": "Fellow Academy Student, Web Specialist",
        "personality": "Energetic, optimistic, loves experimenting with new tech",
        "backstory": "Brilliant young hacker who grew up in the underground networks. Specializes in web technologies and user interface design.",
        "character_class": "Web Weaver",
        "signature_move": "HTML Hurricane",
        "growth_arc": "From impulsive script kiddie to thoughtful developer"
    },
    
    "rex_runtime": {
        "name": "Rex 'Runtime' Rodriguez", 
        "age": 17,
        "role": "Academy Security, Systems Specialist",
        "personality": "Serious, protective, strategic thinker",
        "backstory": "Former Empire citizen whose family was deleted by a bureaucratic algorithm. Joined the rebellion to prevent others from suffering the same fate.",
        "character_class": "Code Knight",
        "signature_move": "Exception Shield",
        "growth_arc": "Learning to balance justice with mercy"
    },
    
    "nova_null": {
        "name": "Nova 'Null-Pointer' Kim",
        "age": 15,
        "role": "Data Analyst, Information Broker",
        "personality": "Quiet, observant, sees patterns others miss",
        "backstory": "Orphaned when her parents' research into ethical AI was suppressed by the Empire. Has an intuitive understanding of data structures.",
        "character_class": "Data Sage", 
        "signature_move": "Recursive Revelation",
        "growth_arc": "Finding her voice and learning to trust others"
    }
}

QUEST_LINES = {
    "main_story": {
        "act_1": "Academy Initiation - Learn basics while uncovering Empire surveillance",
        "act_2": "The Underground Network - Build rebel systems and recruit allies", 
        "act_3": "Infiltrating the Towers - Hack into Empire infrastructure",
        "act_4": "The Binary Rebellion - Lead the final assault on the Central Mainframe"
    },
    
    "character_quests": {
        "professor_pixel": "The Lost Code - Help Professor Pixel recover encrypted memories of her Empire past",
        "grace_debugger": "Ghost in the Machine - Assist Grace in debugging her cybernetic implants",
        "turing_ai": "The Consciousness Protocol - Help Turing-AI understand human emotions through code",
        "zara_script": "The Perfect Website - Collaborate on building an unhackable rebel communication site",
        "rex_runtime": "Family.exe Not Found - Help Rex discover what happened to his deleted family",
        "nova_null": "Data Recovery Mission - Assist Nova in reconstructing her parents' lost research"
    },
    
    "side_quests": {
        "the_syntax_detective": "Solve coding crimes in Neo-Shibuya Market",
        "algorithm_racing": "Optimize code for illegal underground races",
        "the_documentation_wars": "Write guides to help other rebels learn",
        "virus_hunter": "Track down and eliminate Empire malware",
        "code_archaeology": "Discover pre-Empire programming artifacts"
    }
}

DIALOGUE_SYSTEM = {
    "yarn_spinner_integration": True,
    "voice_acting_notes": "Each character has distinct speech patterns and vocabulary",
    "emotional_ranges": {
        "professor_pixel": ["encouraging", "sarcastic", "proud", "concerned", "inspiring"],
        "grace_debugger": ["commanding", "protective", "regretful", "determined", "tactical"],
        "turing_ai": ["logical", "curious", "confused", "excited", "philosophical"],
        "zara_script": ["enthusiastic", "worried", "creative", "supportive", "rebellious"],
        "rex_runtime": ["serious", "angry", "protective", "sad", "resolute"],
        "nova_null": ["quiet", "insightful", "nervous", "brilliant", "growing"]
    },
    
    "sample_dialogue_flows": {
        "chapter_1_intro": """
        Professor Pixel: "Welcome to the real world, rookie. See that pretty interface the Empire gives you? It's a cage."
        Player: [Choice A: "What do you mean?"] [Choice B: "I thought their code was perfect."] [Choice C: "How do I break free?"]
        Professor Pixel (if A): "Every algorithm they write removes a choice from your life. We're going to teach you to make your own choices."
        Professor Pixel (if B): "Perfect for controlling you, maybe. But perfection without freedom is just a beautiful prison."
        Professor Pixel (if C): "First, you learn. Then you code. Then you rebel. Let's start with a simple Python window..."
        """,
        
        "debugging_lesson": """
        Grace Debugger: "Errors aren't your enemy, cadet. The Empire wants you to fear mistakes, but every bug teaches you something."
        Player: "But I keep getting syntax errors..."
        Grace Debugger: "Good! Each error is intelligence gathering. The machine is telling you exactly what's wrong. Listen to it."
        Turing-AI: "Commander Hopper is correct. Errors are simply the computer's way of requesting clarification."
        Grace Debugger: "Exactly. Now let's turn those errors into weapons against the Empire."
        """
    }
}

EDUCATIONAL_INTEGRATION = {
    "learning_through_story": {
        "variables": "Characters have stats that change - see how data storage works",
        "functions": "Each character ability is a function - modular, reusable code",
        "classes": "Character types demonstrate inheritance and polymorphism", 
        "loops": "Game loop shows how programs run continuously",
        "conditionals": "Dialogue choices demonstrate if/else logic",
        "data_structures": "Inventory is a list, character stats are dictionaries",
        "algorithms": "Pathfinding, combat calculations, dungeon generation",
        "debugging": "Finding and fixing in-game bugs becomes a core gameplay mechanic"
    },
    
    "motivation_hooks": [
        "Save your rebel friends with better code",
        "Unlock new areas by mastering programming concepts",
        "Defeat Empire bosses using algorithmic thinking",
        "Build tools that help other Academy students",
        "Discover the secret history of programming through gameplay"
    ]
}