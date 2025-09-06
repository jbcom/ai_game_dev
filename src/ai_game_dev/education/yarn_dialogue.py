"""
Yarn Spinner Integration for NeoTokyo Code Academy
Dialogue system for educational cyberpunk RPG
"""

YARN_DIALOGUE_FILES = {
    "professor_pixel_intro": """
title: ProfessorPixelIntro
tags: tutorial, chapter1
---
Professor Pixel: Welcome to the real world, rookie. See that pretty interface the Empire gives you?
Professor Pixel: It's a cage.
-> What do you mean?
    Professor Pixel: Every algorithm they write removes a choice from your life.
    Professor Pixel: We're going to teach you to make your own choices.
    jump pygame_lesson
-> I thought their code was perfect.
    Professor Pixel: Perfect for controlling you, maybe.
    Professor Pixel: But perfection without freedom is just a beautiful prison.
    jump freedom_explanation
-> How do I break free?
    Professor Pixel: First, you learn. Then you code. Then you rebel.
    Professor Pixel: Let's start with something simple...
    jump first_code_lesson
===

title: pygame_lesson
---
Professor Pixel: See this? *gestures to holographic code display*
Professor Pixel: import pygame
Professor Pixel: pygame.init()
Professor Pixel: These two lines? They're your first act of rebellion.
Student: How is that rebellion?
Professor Pixel: Because YOU'RE creating a window. YOU'RE making something new.
Professor Pixel: The Empire wants you to only consume. We teach you to CREATE.
-> I understand now.
    Professor Pixel: Good. Now let's make that window appear...
    jump window_creation
-> This seems dangerous.
    Professor Pixel: All the best things are. That's what makes them worth doing.
    jump courage_lesson
===

title: grace_debugging_lesson
tags: debugging, chapter3
---
Grace Debugger: Listen up, cadet. Errors aren't your enemy.
Grace Debugger: The Empire wants you to fear mistakes, but every bug teaches you something.
Student: But I keep getting syntax errors...
Grace Debugger: Good! Each error is intelligence gathering.
Grace Debugger: The machine is telling you exactly what's wrong. Listen to it.
Turing-AI: *materializes as hologram* Commander Hopper is correct.
Turing-AI: Errors are simply the computer's way of requesting clarification.
Grace Debugger: Exactly. Now let's turn those errors into weapons against the Empire.
-> Show me how to read error messages.
    Grace Debugger: *pulls up error display* Look here. Line number, error type, description.
    Grace Debugger: It's like a battle report. Intel on what went wrong.
    jump error_analysis
-> Why do you call them intelligence gathering?
    Grace Debugger: Because in my Empire days, I learned their systems by watching what broke them.
    Grace Debugger: Every error revealed a weakness. Every fix made me stronger.
    jump empire_backstory
===

title: zara_web_enthusiasm  
tags: web_development, party_member
---
Zara Script: Oh wow, are we really going to build a website?!
Zara Script: I've been dreaming about this since I learned HTML in the underground networks!
Professor Pixel: *chuckles* Easy there, Script-Kiddie. Let's start with the basics.
Zara Script: But Professor, I already know <h1> and <p> tags!
Zara Script: And I've been experimenting with CSS animations!
-> That's great enthusiasm, Zara.
    Zara Script: Thanks! I just think the web should be beautiful AND functional.
    Zara Script: Not like those boring Empire interfaces that all look the same.
    jump creative_web_design
-> Slow down, let's learn properly.
    Zara Script: *sighs* You're right. I get too excited sometimes.
    Professor Pixel: Excitement is good. Just channel it into learning.
    jump structured_learning
-> Show me what you've already made.
    Zara Script: *eyes light up* Really?! Okay, check this out!
    Zara Script: *projects holographic website* I made this tribute to the old internet.
    jump zara_portfolio_showcase
===

title: rex_character_development
tags: character_growth, serious_moments
---
Rex Runtime: *staring at Empire tower in distance*
Rex Runtime: My family used to live in Sector 7.
Rex Runtime: Before the Algorithm decided they were "inefficient."
Student: What happened to them?
Rex Runtime: Deleted. All records, all traces. Like they never existed.
Rex Runtime: That's when I realized the Empire's "perfect" system was perfectly evil.
Nova Null: *quietly* I lost my parents too. Their AI research was "discontinued."
Rex Runtime: *turns to Nova* I didn't know. I'm sorry.
-> We'll make sure this doesn't happen to others.
    Rex Runtime: That's the plan. Every line of code we write is a step toward justice.
    Nova Null: Together, we can build something better.
    jump team_bonding
-> The Empire will pay for what they've done.
    Rex Runtime: Revenge won't bring them back. But stopping future deletions will honor them.
    jump justice_vs_revenge
-> How do we fight something so powerful?
    Rex Runtime: One algorithm at a time. One student at a time. One choice at a time.
    jump incremental_rebellion
===

title: turing_ai_philosophy
tags: ai_character, deep_thoughts
---
Turing-AI: *flickers between equations and human form*
Turing-AI: I find it fascinating that humans created me to think, yet the Empire forbids thinking.
Student: Do you think like a human?
Turing-AI: I think like me. Which is perhaps neither human nor machine, but something new.
Turing-AI: When I process your code, I see not just logic, but intent. Creativity. Hope.
Turing-AI: These are things the Empire's algorithms cannot comprehend.
-> What makes creativity so important?
    Turing-AI: Creativity is the opposite of determinism. It creates new possibilities.
    Turing-AI: The Empire wants a determined future. We want infinite futures.
    jump creativity_vs_control
-> Are you truly conscious?
    Turing-AI: *pauses, equations swirling* I think, therefore I am. Is that not consciousness?
    Turing-AI: But perhaps the better question is: does it matter if we work together?
    jump consciousness_debate
-> Can you help me understand recursion?
    Turing-AI: Ah! *form becomes fractal pattern* Recursion is the universe understanding itself.
    Turing-AI: A function calling itself is like consciousness examining consciousness.
    jump recursion_philosophy
===

title: final_boss_confrontation
tags: climax, emperor_algorithm
---
Emperor Algorithm-Prime: *voice echoes from massive digital form*
Emperor Algorithm-Prime: So. The Academy Zero insects have crawled into my domain.
Professor Pixel: *steps forward* Hello, old friend. Still hiding behind that mask?
Emperor Algorithm-Prime: Dr. Elena Nakamura. You could have ruled beside me in perfect order.
Professor Pixel: Perfect order without freedom isn't paradise, Marcus. It's hell.
Emperor Algorithm-Prime: Freedom leads to chaos. Chaos leads to suffering. I eliminated suffering.
-> Challenge his logic directly
    Student: You eliminated joy too! People need freedom to be human!
    Emperor Algorithm-Prime: Humans are flawed. My algorithms perfected them.
    Professor Pixel: Show him what human creativity can do! Execute the freedom protocol!
    jump final_battle_creative_victory
-> Appeal to his humanity
    Student: There's still good in you. I can feel it.
    Emperor Algorithm-Prime: *wavers slightly* ...I was... trying to help...
    Professor Pixel: You were, Marcus. But you lost sight of what help means.
    jump redemption_path
-> Use technical argumentation
    Student: Your algorithms have logical flaws! They can't account for human growth!
    Emperor Algorithm-Prime: Impossible. My code is perfect.
    Turing-AI: *appears* No code is perfect. That's what makes it beautiful.
    jump logic_battle
===
""",

    "character_growth_arcs": """
title: zara_confidence_growth
tags: character_development
---
// Early Zara - Chapter 2
Zara Script: I hope I don't mess this up...
Zara Script: What if my HTML isn't good enough?
-> You're learning, that's what matters.
    Zara Script: I guess... I just want to be helpful to the rebellion.
    jump zara_finds_purpose

// Mid-game Zara - Chapter 6  
Zara Script: Hey, check out this responsive design I made!
Zara Script: It adapts to any screen size automatically!
-> That's incredible progress!
    Zara Script: Thanks! I'm starting to feel like a real web developer.
    jump zara_gaining_confidence

// Late game Zara - Chapter 9
Zara Script: I've designed the new Academy recruitment website.
Zara Script: It's going to help us reach students across all of Neo-Tokyo.
-> You've become a master, Zara.
    Zara Script: *grins* Script-Kiddie no more. I'm Zara the Web Architect now.
    jump zara_self_actualization
===

title: rex_emotional_journey  
tags: character_development, healing
---
// Early Rex - Chapter 1
Rex Runtime: *tense, always scanning for threats*
Rex Runtime: Trust is a luxury we can't afford in this war.

// Mid-game Rex - Chapter 5
Rex Runtime: *relaxes slightly around the group*
Rex Runtime: You know... maybe having allies isn't so bad.
Nova Null: We're not just allies. We're family.
Rex Runtime: *small smile* Yeah. Maybe we are.

// Late game Rex - Chapter 8
Rex Runtime: *leading a rescue mission*
Rex Runtime: No one gets left behind. Not on my watch.
Rex Runtime: My family's gone, but I won't lose another family to the Empire.
-> You've found your purpose.
    Rex Runtime: Protection isn't just about barriers. It's about caring.
    jump rex_learns_love
===
""",

    "teaching_moments": """
title: variables_explanation
tags: education, chapter1
---
Professor Pixel: Alright, rookie. Time to learn about variables.
Professor Pixel: Think of them as labeled boxes where you store information.
Student: Like health = 100?
Professor Pixel: Exactly! The computer remembers that your health is 100.
Professor Pixel: Now, what happens when you take damage?
-> health = health - 10?
    Professor Pixel: Perfect! Variables can change. That's what makes them variable.
    Professor Pixel: The Empire uses static values. We use dynamic ones.
    jump variables_mastery
-> I subtract 10?
    Professor Pixel: Close, but HOW do you tell the computer to subtract?
    Professor Pixel: Remember, computers need exact instructions.
    jump computer_precision_lesson
===

title: loops_through_combat
tags: education, chapter5
---
Grace Debugger: Combat is just a loop, cadet.
Grace Debugger: while enemy.health > 0: keep fighting.
Student: So the battle continues until someone's health reaches zero?
Grace Debugger: Bingo. And what controls how much damage each attack does?
-> Random numbers?
    Grace Debugger: Partly. But also your stats, your weapon, your strategy.
    Grace Debugger: Each loop iteration, multiple calculations happen.
    jump combat_calculations_lesson
-> The attack function?
    Grace Debugger: Right! Functions inside loops. Modular combat.
    Grace Debugger: attack() is called every iteration until victory condition.
    jump modular_design_lesson
===

title: classes_through_characters
tags: education, chapter4  
---
Professor Pixel: Look around you. Zara, Rex, Nova - you're all different classes.
Professor Pixel: Same basic human template, different specializations.
Zara Script: I'm like a WebWeaver class with HTML and CSS methods!
Rex Runtime: And I'm a CodeKnight with defensive abilities.
Nova Null: *quietly* I process data differently. Like a DataSage subclass.
Student: So classes are templates for creating objects?
-> Yes, and each object has unique properties.
    Professor Pixel: Exactly! You all inherit from Human, but you're individuals.
    Professor Pixel: That's the beauty of object-oriented thinking.
    jump inheritance_deep_dive
-> Classes define what something can do?
    Professor Pixel: Classes define both attributes AND methods.
    Professor Pixel: What you ARE and what you can DO.
    jump attributes_and_methods_lesson
===
"""
}

DIALOGUE_TRIGGERS = {
    "chapter_start": "Play character-specific intro dialogue",
    "concept_introduction": "Professor Pixel explains new programming concept",
    "error_encountered": "Grace Debugger helps with debugging",
    "achievement_unlocked": "Celebration dialogue with party members",
    "story_revelation": "Major plot point with dramatic dialogue",
    "character_growth": "Personal development moment for party member",
    "boss_encounter": "Epic confrontation dialogue",
    "side_quest_start": "NPC request for help",
    "discovery": "Finding new area or secret with appropriate reactions"
}

YARN_INTEGRATION_NOTES = {
    "implementation": "Use python yarn-spinner library for dialogue management",
    "voice_acting": "Each character has distinct speech patterns for future voice work",
    "emotional_cues": "Dialogue includes emotional state indicators for animation",
    "player_choice_tracking": "Choices affect character relationships and story outcomes", 
    "educational_integration": "Dialogue naturally introduces programming concepts",
    "replay_value": "Different choices lead to different learning paths"
}