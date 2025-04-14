# game_state.py
import pygame
import time
import sys

class GameState:
    """Abstract base class for all game states"""
    def __init__(self, game):
        self.game = game
    
    def handle_events(self, events):
        """Handle pygame events"""
        pass
    
    def update(self, dt):
        """Update state logic"""
        pass
    
    def draw(self, screen):
        """Draw the state"""
        pass
    
    def enter(self):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when exiting this state"""
        pass

class MenuState(GameState):
    """Main menu state"""
    def __init__(self, game):
        super().__init__(game)
        self.menu_items = ["New Game", "Exit"]
        self.selected_item = 0
        self.font = pygame.font.SysFont("Arial", 36)
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                elif event.key == pygame.K_RETURN:
                    if self.selected_item == 0:  # New Game
                        self.game.set_state("playing")
                    elif self.selected_item == 1:  # Exit
                        self.game.running = False
    
    def draw(self, screen):
        screen.fill((0, 0, 0))
        # Draw title
        title = self.font.render("INCANTATO", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 100))
        
        # Draw menu items
        for i, item in enumerate(self.menu_items):
            color = (255, 255, 0) if i == self.selected_item else (255, 255, 255)
            text = self.font.render(item, True, color)
            screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 300 + i * 50))

class PlayingState(GameState):
    """Main gameplay state"""
    def __init__(self, game):
        super().__init__(game)
        self.player = None
        self.enemies = []
        self.effect_manager = None
        self.wave_number = 1
        self.game_start_time = None
        
    def enter(self):
        # Initialize gameplay elements
        from player import Player  # Import here to avoid circular imports
        
        self.game_start_time = time.time()
        
        # Create player using deck from game
        self.player = Player(
            self.game.player_name,
            self.game.WIDTH // 2,
            self.game.HEIGHT // 2,
            self.game.deck,
            self.game.PLAYER_RADIUS,
            self.game.PLAYER_MAX_HEALTH,
            self.game.PLAYER_SUMMON_LIMIT,
            self.game.PLAYER_COLOR,
            self.game.PLAYER_WALK_SPEED,
            self.game.PLAYER_SPRINT_SPEED,
            self.game.PLAYER_MAX_STAMINA,
            self.game.PLAYER_STAMINA_REGEN,
            self.game.PLAYER_SPRINT_DRAIN,
            self.game.PLAYER_DASH_COST,
            self.game.PLAYER_DASH_DISTANCE,
            self.game.PLAYER_STAMINA_COOLDOWN
        )
        
        # Create initial wave
        self.enemies = []
        self.wave_manager.spawn_wave(self.wave_number, self.enemies)
    
    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        now = time.time()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.game.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.set_state("paused")
            else:
                result = self.player.handle_event(
                    event, mouse_pos, self.enemies, now, self.effect_manager)
                if result == 'exit':
                    self.game.log_csv(self.wave_number)
                    self.game.running = False
    
    def update(self, dt):
        # Update enemies
        for e in self.enemies:
            e.update(self.player, dt)
        
        # Check projectiles for each enemy that has them
        if hasattr(e, 'projectiles'):
            for p in e.projectiles:
                if p.check_collision(self.player):
                    # Collision already handled in check_collision
                    pass
        
        # Update player
        self.player.handle_input(dt)
        
        # Update projectiles and summons
        for p in self.player.projectiles:
            p.update(dt, self.enemies)
        self.player.projectiles = [p for p in self.player.projectiles if p.active]
        
        for s in self.player.summons:
            s.update(self.enemies)
        self.player.summons = [s for s in self.player.summons if s.alive]
        
        # Resolve collisions
        from utils import resolve_overlap
        entities = [entity for entity in ([self.player] + self.player.summons + self.enemies) if entity.alive]
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                resolve_overlap(entities[i], entities[j])
        
        # Clean up dead entities
        self.enemies = [e for e in self.enemies if e.alive]
        
        # Check for wave completion
        if len(self.enemies) == 0:
            self.wave_number += 1
            self.wave_manager.spawn_wave(self.wave_number, self.enemies)
        
        # Update effects
        if self.effect_manager:
            self.effect_manager.update(dt)
        
        # Check player death
        if self.player.health <= 0:
            self.game.log_csv(self.wave_number)
            self.game.set_state("game_over")
    
    def draw(self, screen):
        screen.fill((255, 255, 255))
        
        # Draw wave info
        self.draw_wave_info(screen)
        
        # Draw player UI
        self.draw_player_bars(screen)
        self.draw_skill_ui(screen)
        
        # Draw game elements
        self.draw_game_elements(screen)
    
    # Include the existing UI drawing methods from game.py
    def draw_wave_info(self, screen):
        ui_font = pygame.font.SysFont("Arial", 24)
        wave_text = ui_font.render(f"WAVE: {self.wave_number}", True, (0, 0, 0))
        screen.blit(wave_text, (10, 10))
    
    def draw_player_bars(self, screen):
        # Copy existing draw_player_bars method from Game class
        pass
    
    def draw_skill_ui(self, screen):
        # Copy existing draw_skill_ui method from Game class
        pass
    
    def draw_game_elements(self, screen):
        # Copy existing draw_game_elements method from Game class
        pass

class PausedState(GameState):
    """Paused game state"""
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 36)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.set_state("playing")
                elif event.key == pygame.K_q:
                    self.game.running = False
    
    def draw(self, screen):
        # Draw the underlying game state first (dimmed)
        self.game.states["playing"].draw(screen)
        
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw pause text
        paused_text = self.font.render("PAUSED", True, (255, 255, 255))
        screen.blit(paused_text, (screen.get_width() // 2 - paused_text.get_width() // 2, 200))
        
        # Draw instructions
        instructions = self.font.render("Press ESC to resume, Q to quit", True, (255, 255, 255))
        screen.blit(instructions, (screen.get_width() // 2 - instructions.get_width() // 2, 250))

class GameOverState(GameState):
    """Game over state"""
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 36)
        self.small_font = pygame.font.SysFont("Arial", 24)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.game.set_state("menu")
                elif event.key == pygame.K_q:
                    self.game.running = False
    
    def draw(self, screen):
        screen.fill((0, 0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, 150))
        
        # Get wave info from the playing state
        wave_text = self.small_font.render(f"Waves survived: {self.game.states['playing'].wave_number}", True, (255, 255, 255))
        screen.blit(wave_text, (screen.get_width() // 2 - wave_text.get_width() // 2, 220))
        
        # Draw instructions
        instructions = self.small_font.render("Press R to return to menu, Q to quit", True, (255, 255, 255))
        screen.blit(instructions, (screen.get_width() // 2 - instructions.get_width() // 2, 300))