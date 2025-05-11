# main.py
import pygame
import sys
import time
import random
from player import Player
from enemy import Enemy
from utils import resolve_overlap
from game_state import GameStateManager, MenuState, NameEntryState, DeckSelectionState, PlayingState
from audio import Audio
from config import Config as C


class Game:
    def __init__(self):
        """Initialize game state and assets."""
        pygame.init()
        self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
        pygame.display.set_caption(C.GAME_NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.audio = Audio()
        self.audio.load_music()
        
        # Game state tracking
        self.wave_number = 1
        self.skills_filename = C.SKILLS_FILENAME
        self.player_name = None
        self.last_player_name = None

        # Sprite groups for collision detection
        self.enemy_group = pygame.sprite.Group()
        
        # Initialize state manager and states
        self.state_manager = GameStateManager(self)
        self.state_manager.add_state("MENU", MenuState(self))
        self.state_manager.add_state("NAME_ENTRY", NameEntryState(self))
        self.state_manager.add_state("DECK_SELECTION", DeckSelectionState(self))
        self.state_manager.add_state("PLAYING", PlayingState(self))
        
        # Start with menu state and play menu music
        self.state_manager.set_state("MENU")
        self.audio.play_music("MENU")

    def initialize_player(self):
        """Initialize the player with an empty deck"""
        self.player = Player(self.player_name)
        self.game_start_time = time.time()

    def prepare_game(self):
        """Setup game for playing after deck is created"""
        self.wave_number = 1
        self.spawn_wave()
        self.audio.fade_out(800)
        self.audio.fade_in("PLAYING", 1000)

    def spawn_wave(self):
        # Clear enemy group
        self.enemy_group.empty()
        
        # spawn enemies based on wave number
        n_enemies = 5 + self.wave_number
        for _ in range(n_enemies):
            x = random.randint(20, C.WIDTH - 20)
            y = random.randint(20, C.HEIGHT - 20)
            enemy = Enemy(
                x, y, 
                self.wave_number,
                C.ENEMY_BASE_SPEED,
                C.ENEMY_BASE_HP
            )
            self.enemy_group.add(enemy)
    
    @property
    def enemies(self):
        """Property to maintain backward compatibility"""
        return list(self.enemy_group.sprites())

    def check_collisions(self):
        """Use sprite collide for efficient collision detection"""
        # Player projectiles vs enemies
        for projectile in self.player.deck.projectiles:
            collided_enemies = pygame.sprite.spritecollide(
                projectile, self.enemy_group, False, pygame.sprite.collide_circle
            )
            if collided_enemies:
                enemy = collided_enemies[0]
                enemy.take_damage(projectile.damage)
                projectile.explode(self.enemies)
                break

        # Player summons vs enemies handled in the summon update
        
        # Player vs enemies (push back enemies)
        collided_enemies = pygame.sprite.spritecollide(
            self.player, self.enemy_group, False, pygame.sprite.collide_circle
        )
        for enemy in collided_enemies:
            resolve_overlap(self.player, enemy)

    def run(self):
        while self.running:
            # Get delta time in seconds
            dt = self.clock.tick(C.FPS) / 1000.0
            
            # Get all events
            events = pygame.event.get()
            
            # Handle events through state manager
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                    break
            
            if not self.running:
                break
                
            # Update and handle state events
            self.state_manager.handle_events(events)
            self.state_manager.update(dt)
            self.state_manager.render(self.screen)
            
            pygame.display.flip()

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
