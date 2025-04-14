# main.py
import pygame
import sys
import time
import csv
import random
from skill import SkillType, BaseSkill
from game_state import MenuState, PlayingState, PausedState, GameOverState
from wave_manager import WaveManager
from player import Player
from enemy import Enemy
from effects import EffectManager
from utils import resolve_overlap, draw_hp_bar, angle_diff
from config import (
    TITLE,
    WIDTH,
    HEIGHT,
    FPS,
    WHITE,
    BLACK,
    RED,
    BLUE,
    PURPLE,
    GREEN,
    UI_COLORS,
    LOG_FILENAME,
    SKILLS_FILENAME,
    PLAYER_RADIUS,
    PLAYER_MAX_HEALTH,
    PLAYER_SUMMON_LIMIT,
    PLAYER_COLOR,
    PLAYER_WALK_SPEED,
    PLAYER_SPRINT_SPEED,
    PLAYER_MAX_STAMINA,
    PLAYER_STAMINA_REGEN,
    PLAYER_SPRINT_DRAIN,
    PLAYER_DASH_COST,
    PLAYER_DASH_DISTANCE,
    PLAYER_STAMINA_COOLDOWN,
    ENEMY_BASE_HP,
    ENEMY_BASE_SPEED,
    WAVE_MULTIPLIER,
    ENEMY_DAMAGE,
    ATTACK_COOLDOWN)
from ui import UIManager
from map_system import MapManager
from resource_manager import ResourceManager


class Game:
    """Main game controller class using state pattern"""
    
    def __init__(self):
        # Initialize pygame
        pygame.init()
        
        # Make constants accessible to game states
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.PLAYER_RADIUS = PLAYER_RADIUS
        self.PLAYER_MAX_HEALTH = PLAYER_MAX_HEALTH
        self.PLAYER_SUMMON_LIMIT = PLAYER_SUMMON_LIMIT
        self.PLAYER_COLOR = PLAYER_COLOR
        self.PLAYER_WALK_SPEED = PLAYER_WALK_SPEED
        self.PLAYER_SPRINT_SPEED = PLAYER_SPRINT_SPEED
        self.PLAYER_MAX_STAMINA = PLAYER_MAX_STAMINA
        self.PLAYER_STAMINA_REGEN = PLAYER_STAMINA_REGEN
        self.PLAYER_SPRINT_DRAIN = PLAYER_SPRINT_DRAIN
        self.PLAYER_DASH_COST = PLAYER_DASH_COST
        self.PLAYER_DASH_DISTANCE = PLAYER_DASH_DISTANCE
        self.PLAYER_STAMINA_COOLDOWN = PLAYER_STAMINA_COOLDOWN
        
        # Create game window
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Create managers
        self.wave_manager = WaveManager()
        self.ui_manager = UIManager()
        # self.map_manager = MapManager(WIDTH, HEIGHT)  # Comment this out
        self.effect_manager = EffectManager()
        self.resource_manager = ResourceManager()
        
        # Generate a random map
        # self.map_manager.create_random_map()  # Comment this out
        
        # Initialize game states
        self.states = {
            "menu": MenuState(self),
            "playing": PlayingState(self),
            "paused": PausedState(self),
            "game_over": GameOverState(self)
        }
        
        # Set initial state
        self.current_state = "menu"
        
        # Player data (collected before starting game)
        self.player_name = "Unknown"
        self.deck = []
    
    def set_running(self, value):
        """Set running state"""
        self.running = value
    
    def set_state(self, state_name):
        """Change to a different game state"""
        if state_name in self.states:
            # Call exit on current state
            if hasattr(self.states[self.current_state], "exit"):
                self.states[self.current_state].exit()
            
            # Switch state
            self.current_state = state_name
            
            # Call enter on new state
            if hasattr(self.states[self.current_state], "enter"):
                self.states[self.current_state].enter()
            
            if state_name == "menu":
                self.ui_manager.create_menu_ui(
                    lambda: self.start_new_game(),
                    lambda: self.set_running(False)
                )
            elif state_name == "paused":
                self.ui_manager.create_pause_ui(
                    lambda: self.set_state("playing"),
                    lambda: self.set_running(False)
                )
            elif state_name == "game_over":
                self.ui_manager.create_game_over_ui(
                    lambda: self.set_state("menu"),
                    lambda: self.set_running(False),
                    self.wave_number
                )
    
    def get_player_info(self):
        """Get player name and build their deck"""
        self.player_name = input("Enter player name: ") or "Unknown"
        
        # Load skills
        all_skills = self.load_skills_from_csv(SKILLS_FILENAME)
        
        # Build deck
        self.deck = self.build_deck_interactively(all_skills)
    
    def load_skills_from_csv(self, filename_in_config):
        """Load skills from the data preloaded by ResourceManager."""
        skill_list = []
        # Get the pre-processed data (list of dicts) from ResourceManager
        skills_data = self.resource_manager.get_data("skills") # Use the name used in preload

        if not skills_data:
            print(f"Error: Skills data '{filename_in_config}' not loaded by ResourceManager.")
            sys.exit(1)

        try:
            for row in skills_data: # Iterate through the list of dicts
                nm = row["name"]
                elem = row["element"].upper()
                stype_str = row["skill_type"].upper()
                # ... (rest of the parsing logic remains the same) ...
                # Make sure to handle potential errors if CSV columns are missing/malformed
                try:
                    dmg = int(row["damage"])
                    spd = float(row["speed"])
                    rad = float(row["radius"])
                    dur = float(row["duration"])
                    pull = (row["pull"].strip().lower() == "true")
                    heal = int(row["heal_amount"])
                    cd = float(row["cooldown"])
                    desc = row["description"]
                except KeyError as e:
                    print(f"CSV parsing error: Missing column {e} in row: {row}")
                    continue # Skip this skill
                except ValueError as e:
                    print(f"CSV parsing error: Invalid value in row {row}. Error: {e}")
                    continue # Skip this skill

                # Convert string to SkillType enum
                try:
                    st = SkillType[stype_str]
                except KeyError:
                    print(f"Unknown skill_type: {stype_str} for skill '{nm}'")
                    continue

                skill_obj = BaseSkill(
                    nm, elem, st,
                    dmg, spd,
                    rad, dur, pull, heal,
                    cd, desc
                )
                skill_list.append(skill_obj)
        except Exception as e: # Catch broader exceptions during processing
            print(f"Error processing skills data: {e}")
            sys.exit(1)
        return skill_list
    
    def build_deck_interactively(self, skill_list):
        """Let player select skills for their deck"""
        print("=== BUILD YOUR DECK (Pick 4) ===")
        for i, sk in enumerate(skill_list):
            print(f"{i + 1}. [{sk.element}] {sk.name} - {sk.description}")

        chosen = []
        picks_needed = 4
        while len(chosen) < picks_needed:
            c = input(f"Pick skill #{len(chosen) + 1} (1-{len(skill_list)}): ")
            if not c.isdigit():
                print("Invalid input. Enter a number.")
                continue
            idx = int(c) - 1
            if idx < 0 or idx >= len(skill_list):
                print("Out of range. Try again.")
                continue
            chosen_skill = skill_list[idx]
            chosen.append(chosen_skill)
            print(f"Added {chosen_skill.name}.")

        print("=== Final Deck ===")
        for s in chosen:
            print(f"- {s.name}")
        return chosen
    
    def log_csv(self, wave):
        """Log game results to CSV file"""
        # Use the data_dir from resource manager to build the correct path
        log_path = os.path.join(self.resource_manager.data_dir, LOG_FILENAME)

        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        # Ensure game_start_time is initialized correctly in start_new_game
        if not hasattr(self, 'game_start_time') or self.game_start_time is None:
             g_time = 0 # Or some default/error value
             print("Warning: game_start_time not set before logging.")
        else:
             g_time = time.time() - self.game_start_time

        # Ensure player and deck exist before logging
        if not hasattr(self, 'player') or not self.player or not self.player.deck:
             print("Warning: Player/deck not available for logging.")
             deck_str = "N/A"
             skill_names = ["N/A"] * 4
             final_hp = "N/A"
        else:
             deck_str = "|".join([skill.name for skill in self.player.deck])
             skill_names = [self.player.deck[i].name if i < len(self.player.deck) else "N/A" for i in range(4)]
             final_hp = self.player.health


        file_exists = os.path.exists(log_path)

        try:
            with open(log_path, "a", newline="", encoding='utf-8') as f:
                w = csv.writer(f)
                # Write header only if file is new
                if not file_exists or f.tell() == 0:
                    w.writerow([
                        "timestamp", "player_name", "wave_survived",
                        "game_duration", "final_hp", "deck_composition",
                        "skill1", "skill2", "skill3", "skill4"
                    ])

                # Write data row
                w.writerow([
                    now_str,                    # timestamp
                    self.player_name,           # player_name
                    wave,                       # wave_survived
                    f"{g_time:.2f}",            # game_duration
                    final_hp,                   # final_hp
                    deck_str,                   # deck_composition
                    skill_names[0],             # skill1
                    skill_names[1],             # skill2
                    skill_names[2],             # skill3
                    skill_names[3],             # skill4
                ])
        except IOError as e:
             print(f"Error writing to log file '{log_path}': {e}")
        except Exception as e:
             print(f"An unexpected error occurred during logging: {e}")
    
    def run(self):
        """Main game loop"""
        # Get player info MUST happen AFTER resource manager is ready
        # and AFTER pygame.init is called (which ResourceManager ensures)
        # ResourceManager init should happen first in Game.__init__ if it does pygame.init

        # Preload resources
        self.resource_manager.preload_resources() # Now includes loading skills data

        # Get player info (which uses skills data)
        self.get_player_info()

        # Inject managers into the playing state
        self.states["playing"].wave_manager = self.wave_manager
        # self.states["playing"].map_manager = self.map_manager  # Comment this out
        self.states["playing"].effect_manager = self.effect_manager
        
        # Start with menu state
        self.set_state("menu")
        
        # Main game loop
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0
            
            # Get all events
            events = pygame.event.get()
            
            # Check for quit event
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            # Let current state handle events
            self.states[self.current_state].handle_events(events)
            
            # Update current state
            self.states[self.current_state].update(dt)
            
            # Update UI
            self.ui_manager.update(dt)
            
            # Draw current state
            self.states[self.current_state].draw(self.screen)
            
            # Draw UI
            self.ui_manager.draw(self.screen)
            
            # Flip display
            pygame.display.flip()
        
        # Clean up
        pygame.quit()
        sys.exit()

    def start_new_game(self):
        """Initialize a new game"""
        # ... (map stuff commented out) ...

        # Reset wave number
        self.wave_number = 1
        self.game_start_time = time.time() # Initialize game_start_time here

        # ... (Create player - deck is already built in get_player_info) ...
        # Make sure self.deck is available here
        if not self.deck:
             print("Error: Deck is empty. Cannot start game.")
             # Maybe go back to menu or exit?
             self.set_state("menu") # Example: return to menu
             return

        self.player = Player(
            self.player_name,
            WIDTH // 2,
            HEIGHT // 2,
            self.deck, # Use the deck built earlier
            PLAYER_RADIUS,
            PLAYER_MAX_HEALTH,
            PLAYER_SUMMON_LIMIT,
            PLAYER_COLOR,
            PLAYER_WALK_SPEED,
            PLAYER_SPRINT_SPEED,
            PLAYER_MAX_STAMINA,
            PLAYER_STAMINA_REGEN,
            PLAYER_SPRINT_DRAIN,
            PLAYER_DASH_COST,
            PLAYER_DASH_DISTANCE,
            PLAYER_STAMINA_COOLDOWN
        )
        
        # Create initial wave
        self.enemies = []
        self.wave_manager.spawn_wave(self.wave_number, self.enemies)
        
        # Create game UI
        self.ui_manager.create_gameplay_ui(self.player)
        
        # Start game music
        self.resource_manager.play_music("game_theme", volume=0.4)
        
        # Change state to playing
        self.set_state("playing")

    def draw_playing(self):
        self.screen.fill(WHITE)
        
        # Draw map first
        # self.map_manager.draw(self.screen)  # Comment this out
        
        # Draw game elements
        self.draw_game_elements()
        
        # Draw UI
        self.ui_manager.draw(self.screen)

    def handle_playing_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        now = time.time()
        
        for event in events:
            # Let UI handle events first
            if self.ui_manager.handle_event(event):
                continue
            
            # Existing event handling code...

def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
