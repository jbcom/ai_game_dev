"""
Player Character System for NeoTokyo Code Academy
Demonstrates Object-Oriented Programming concepts for educational purposes
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class StatType(Enum):
    """Character statistics enumeration."""
    HEALTH = "health"
    MANA = "mana" 
    ATTACK = "attack"
    DEFENSE = "defense"
    SPEED = "speed"
    LUCK = "luck"


@dataclass
class Equipment:
    """Equipment item with educational programming concepts."""
    name: str
    description: str
    stat_bonuses: Dict[StatType, int]
    required_level: int = 1
    
    def apply_bonuses(self, player_stats: Dict[StatType, int]) -> Dict[StatType, int]:
        """Apply equipment bonuses to player stats (demonstrates functions)."""
        enhanced_stats = player_stats.copy()
        
        for stat_type, bonus in self.stat_bonuses.items():
            enhanced_stats[stat_type] += bonus
            
        return enhanced_stats


class Ability:
    """Character ability demonstrating methods and encapsulation."""
    
    def __init__(self, name: str, description: str, mana_cost: int, power: int):
        self.name = name
        self.description = description
        self.mana_cost = mana_cost
        self.power = power
        self.cooldown = 0
    
    def can_use(self, current_mana: int) -> bool:
        """Check if ability can be used (demonstrates conditionals)."""
        return current_mana >= self.mana_cost and self.cooldown == 0
    
    def use(self) -> int:
        """Use the ability and return damage/effect (demonstrates return values)."""
        if self.cooldown > 0:
            return 0
            
        self.cooldown = 3  # Abilities have cooldowns
        return self.power


class CharacterClass:
    """Base character class demonstrating inheritance principles."""
    
    def __init__(self, name: str, base_stats: Dict[StatType, int]):
        self.name = name
        self.base_stats = base_stats
        self.abilities: List[Ability] = []
        self.learning_concepts: List[str] = []
    
    def add_ability(self, ability: Ability):
        """Add a new ability (demonstrates list operations)."""
        self.abilities.append(ability)
    
    def get_stat_growth(self, level: int) -> Dict[StatType, int]:
        """Calculate stat growth by level (demonstrates algorithms)."""
        growth = {}
        for stat_type, base_value in self.base_stats.items():
            # Each level adds a percentage of base stats
            growth[stat_type] = base_value + (level - 1) * (base_value // 10)
        return growth


class CodeKnight(CharacterClass):
    """Code Knight class demonstrating inheritance."""
    
    def __init__(self):
        base_stats = {
            StatType.HEALTH: 120,
            StatType.MANA: 60, 
            StatType.ATTACK: 15,
            StatType.DEFENSE: 18,
            StatType.SPEED: 8,
            StatType.LUCK: 10
        }
        
        super().__init__("Code Knight", base_stats)
        
        # Add class-specific abilities
        self.add_ability(Ability("Neural Shield", "Blocks incoming attacks", 20, 0))
        self.add_ability(Ability("Class Strike", "Object-oriented attack", 15, 25))
        self.add_ability(Ability("Inheritance Wall", "Defensive barrier", 30, 0))
        
        self.learning_concepts = ["OOP", "Classes", "Inheritance", "Polymorphism"]


class DataSage(CharacterClass):
    """Data Sage class demonstrating different inheritance path."""
    
    def __init__(self):
        base_stats = {
            StatType.HEALTH: 85,
            StatType.MANA: 180,
            StatType.ATTACK: 10,
            StatType.DEFENSE: 8,
            StatType.SPEED: 12,
            StatType.LUCK: 15
        }
        
        super().__init__("Data Sage", base_stats)
        
        # Add class-specific abilities
        self.add_ability(Ability("Neon List Storm", "Array manipulation attack", 25, 30))
        self.add_ability(Ability("Dictionary Heal", "Key-value restoration", 20, -35))  # Negative = healing
        self.add_ability(Ability("Quantum Sort", "Organize battlefield chaos", 40, 50))
        
        self.learning_concepts = ["Data Structures", "Algorithms", "Complexity", "Recursion"]


class Player:
    """Main player character demonstrating composition and state management."""
    
    def __init__(self, character_class: CharacterClass):
        self.character_class = character_class
        self.level = 1
        self.experience = 0
        
        # Current stats (demonstrates dictionaries)
        self.current_stats = character_class.get_stat_growth(self.level)
        self.health = self.current_stats[StatType.HEALTH]
        self.mana = self.current_stats[StatType.MANA]
        
        # Equipment and inventory (demonstrates lists)
        self.equipment: List[Equipment] = []
        self.inventory: List[str] = []
        
        # Position and movement
        self.x = 100
        self.y = 100
        
        # Educational progress tracking
        self.learned_concepts: List[str] = []
        self.completed_chapters: List[int] = []
    
    def gain_experience(self, amount: int):
        """Gain experience and handle level ups (demonstrates while loops)."""
        self.experience += amount
        
        # Check for level up (demonstrates conditional logic)
        exp_needed = self.calculate_exp_needed()
        while self.experience >= exp_needed:
            self.level_up()
            exp_needed = self.calculate_exp_needed()
    
    def calculate_exp_needed(self) -> int:
        """Calculate experience needed for next level (demonstrates math operations)."""
        # Exponential growth: level^1.5 * 100
        return int((self.level ** 1.5) * 100)
    
    def level_up(self):
        """Level up character and increase stats (demonstrates state changes)."""
        old_level = self.level
        self.level += 1
        
        # Reset experience for next level
        self.experience -= self.calculate_exp_needed()
        
        # Update stats based on new level
        old_stats = self.current_stats.copy()
        self.current_stats = self.character_class.get_stat_growth(self.level)
        
        # Restore health and mana proportionally
        health_percent = self.health / old_stats[StatType.HEALTH]
        mana_percent = self.mana / old_stats[StatType.MANA]
        
        self.health = int(self.current_stats[StatType.HEALTH] * health_percent)
        self.mana = int(self.current_stats[StatType.MANA] * mana_percent)
        
        print(f"🎉 Level Up! {self.character_class.name} reached level {self.level}")
        
        # Learn new concepts at certain levels
        if self.level % 5 == 0:  # Every 5 levels
            self.learn_new_concept()
    
    def learn_new_concept(self):
        """Learn a new programming concept (educational progression)."""
        available_concepts = [
            concept for concept in self.character_class.learning_concepts 
            if concept not in self.learned_concepts
        ]
        
        if available_concepts:
            new_concept = available_concepts[0]
            self.learned_concepts.append(new_concept)
            print(f"📚 New Concept Learned: {new_concept}")
    
    def equip_item(self, equipment: Equipment) -> bool:
        """Equip an item if level requirement is met (demonstrates validation)."""
        if self.level >= equipment.required_level:
            self.equipment.append(equipment)
            # Apply stat bonuses
            enhanced_stats = equipment.apply_bonuses(self.current_stats)
            self.current_stats = enhanced_stats
            return True
        else:
            print(f"Level {equipment.required_level} required to equip {equipment.name}")
            return False
    
    def use_ability(self, ability_name: str) -> Optional[int]:
        """Use a character ability (demonstrates error handling)."""
        try:
            # Find the ability
            ability = None
            for ab in self.character_class.abilities:
                if ab.name == ability_name:
                    ability = ab
                    break
            
            if ability is None:
                raise ValueError(f"Ability '{ability_name}' not found")
            
            if not ability.can_use(self.mana):
                raise ValueError(f"Cannot use {ability_name}: insufficient mana or cooldown")
            
            # Use the ability
            effect = ability.use()
            self.mana -= ability.mana_cost
            
            return effect
            
        except ValueError as e:
            print(f"❌ Error using ability: {e}")
            return None
    
    def move(self, dx: int, dy: int):
        """Move player character (demonstrates coordinate systems)."""
        # Simple boundary checking
        new_x = max(0, min(1200, self.x + dx))  # Screen boundaries
        new_y = max(0, min(680, self.y + dy))
        
        self.x = new_x
        self.y = new_y
    
    def get_status_display(self) -> Dict[str, str]:
        """Get formatted status for UI display (demonstrates string formatting)."""
        return {
            "class": self.character_class.name,
            "level": f"Level {self.level}",
            "health": f"{self.health}/{self.current_stats[StatType.HEALTH]}",
            "mana": f"{self.mana}/{self.current_stats[StatType.MANA]}",
            "experience": f"XP: {self.experience}/{self.calculate_exp_needed()}",
            "concepts": f"Learned: {len(self.learned_concepts)} concepts"
        }


# Factory function demonstrating the Factory design pattern
def create_player(class_name: str) -> Player:
    """Create a player character of the specified class."""
    class_mapping = {
        "code_knight": CodeKnight,
        "data_sage": DataSage,
        # Add other classes as they're implemented
    }
    
    if class_name.lower() not in class_mapping:
        raise ValueError(f"Unknown character class: {class_name}")
    
    character_class = class_mapping[class_name.lower()]()
    return Player(character_class)


# Example usage for educational demonstration
if __name__ == "__main__":
    print("🎓 Player Character System Demo")
    print("Creating a Code Knight character...")
    
    # Demonstrate object creation
    player = create_player("code_knight")
    print(f"Created: {player.get_status_display()}")
    
    # Demonstrate experience and leveling
    print("\nGaining experience...")
    player.gain_experience(150)
    print(f"After XP gain: {player.get_status_display()}")
    
    # Demonstrate ability usage
    print("\nUsing abilities...")
    damage = player.use_ability("Class Strike")
    if damage:
        print(f"Class Strike dealt {damage} damage!")
    
    print("\n🎮 Player system ready for game integration!")
