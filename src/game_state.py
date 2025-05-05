import pygame
import time

class GameState:
    """Base class for all game states"""
    def __init__(self, game):
        self.game = game  # Reference to main game object
    
    def enter(self):
        """Called when this state becomes active"""
        pass
    
    def exit(self):
        """Called when this state is no longer active"""
        pass
    
    def update(self, dt):
        """Update game logic"""
        pass
    
    def render(self, screen):
        """Render the state"""
        pass
    
    def handle_events(self, events):
        """Process input events"""
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
        return None  # No state change


class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.menu_font = pygame.font.SysFont("Arial", 32)
        self.title_font = pygame.font.SysFont("Arial", 48)
        self.options = ["Play", "Quit"]
        self.selected = 0
    
    def enter(self):
        # Setup or reset menu state
        self.selected = 0
        
    def update(self, dt):
        # Menu animations, if any
        pass
    
    def render(self, screen):
        # Clear screen with background
        screen.fill((50, 50, 100))
        
        # Draw title
        title = self.title_font.render("INCANTATO", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # Draw menu options
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.menu_font.render(option, True, color)
            pos_y = 250 + i * 60
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, pos_y))
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:  # Play
                        # Go to name entry screen instead of initializing directly
                        return "NAME_ENTRY"
                    elif self.selected == 1:  # Quit
                        return "QUIT"
        return None


class PlayerNameState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("Arial", 36)
        self.input_font = pygame.font.SysFont("Arial", 28)
        self.info_font = pygame.font.SysFont("Arial", 20)
        self.name = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 0.5  # Blink every half second
    
    def enter(self):
        self.name = ""
        self.cursor_visible = True
        self.cursor_timer = 0
    
    def update(self, dt):
        # Blink cursor
        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_blink_rate:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def render(self, screen):
        # Background
        screen.fill((40, 40, 80))
        
        # Title
        title = self.title_font.render("Enter Your Name", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))
        
        # Input field background
        input_width = 400
        input_height = 50
        input_x = (screen.get_width() - input_width) // 2
        input_y = 250
        pygame.draw.rect(screen, (30, 30, 60), (input_x, input_y, input_width, input_height))
        pygame.draw.rect(screen, (100, 100, 150), (input_x, input_y, input_width, input_height), 2)
        
        # Display entered name
        display_name = self.name
        if self.cursor_visible:
            display_name += "|"
        
        name_text = self.input_font.render(display_name, True, (255, 255, 255))
        screen.blit(name_text, (input_x + 10, input_y + (input_height - name_text.get_height()) // 2))
        
        # Instructions
        instruction = self.info_font.render("Enter your name and press ENTER to continue", True, (200, 200, 200))
        screen.blit(instruction, (screen.get_width()//2 - instruction.get_width()//2, input_y + input_height + 30))
        
        # Default name info
        if not self.name:
            default_text = self.info_font.render("(Leave empty for 'Unknown')", True, (150, 150, 150))
            screen.blit(default_text, (screen.get_width()//2 - default_text.get_width()//2, input_y + input_height + 60))
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Set the player name and move to deck selection
                    self.game.player_name = self.name if self.name else "Unknown"
                    self.game.initialize_player()
                    return "DECK_SELECTION"
                
                elif event.key == pygame.K_ESCAPE:
                    # Go back to main menu
                    return "MENU"
                
                elif event.key == pygame.K_BACKSPACE:
                    # Remove last character
                    self.name = self.name[:-1]
                
                else:
                    # Add character (if it's a valid input)
                    if event.unicode.isprintable() and len(self.name) < 20:  # Limit name length
                        self.name += event.unicode
        
        return None


class DeckSelectionState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.SysFont("Arial", 36)
        self.skill_font = pygame.font.SysFont("Arial", 24)
        self.desc_font = pygame.font.SysFont("Arial", 18)
        self.info_font = pygame.font.SysFont("Arial", 20)
        
        # Scrolling parameters
        self.skills_per_page = 5
        self.scroll_offset = 0
        self.selected_skill = 0
        
        # Selected skills
        self.chosen_skills = []
        self.picks_needed = 4
        
        # Element colors
        self.element_colors = {
            "Fire": (255, 100, 50),
            "Water": (50, 100, 255),
            "Earth": (150, 100, 50),
            "Air": (200, 200, 255),
            "Ice": (150, 200, 255),
            "Lightning": (255, 255, 100),
            "Dark": (100, 50, 150),
            "Light": (255, 255, 200)
        }
    
    def enter(self):
        # Load skills from CSV
        if not hasattr(self, 'all_skills'):
            self.all_skills = self.game.deck.load_from_csv(self.game.skills_filename)
        
        self.scroll_offset = 0
        self.selected_skill = 0
        self.chosen_skills = []
    
    def update(self, dt):
        pass
    
    def render(self, screen):
        # Background
        screen.fill((40, 40, 80))
        
        # Title
        title = self.title_font.render("BUILD YOUR DECK (Pick 4)", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 30))
        
        # Draw skill list (with scrolling)
        self.draw_skill_list(screen)
        
        # Draw chosen skills
        self.draw_chosen_skills(screen)
        
        # Draw navigation help
        help_text = self.info_font.render("↑↓: Navigate   ENTER: Select   BACKSPACE: Remove   SPACE: Confirm", True, (200, 200, 200))
        screen.blit(help_text, (screen.get_width()//2 - help_text.get_width()//2, screen.get_height() - 40))
    
    def draw_skill_list(self, screen):
        list_width = screen.get_width() * 0.6
        list_height = 400
        list_x = (screen.get_width() - list_width) // 2
        list_y = 80
        
        # Draw list background
        pygame.draw.rect(screen, (30, 30, 60), (list_x, list_y, list_width, list_height))
        pygame.draw.rect(screen, (100, 100, 150), (list_x, list_y, list_width, list_height), 2)
        
        # Draw scrollbar if needed
        if len(self.all_skills) > self.skills_per_page:
            scrollbar_height = list_height * min(1.0, self.skills_per_page / len(self.all_skills))
            scrollbar_pos = list_y + (list_height - scrollbar_height) * (self.scroll_offset / (len(self.all_skills) - self.skills_per_page))
            pygame.draw.rect(screen, (150, 150, 180), (list_x + list_width - 15, scrollbar_pos, 10, scrollbar_height))
        
        # Draw visible skills
        visible_skills = self.all_skills[self.scroll_offset:self.scroll_offset + self.skills_per_page]
        for i, skill in enumerate(visible_skills):
            # Check if this skill is already chosen
            is_chosen = skill in self.chosen_skills
            skill_y = list_y + 10 + i * (list_height // self.skills_per_page)
            
            # Highlight if this is the selected skill
            if i + self.scroll_offset == self.selected_skill:
                pygame.draw.rect(screen, (60, 60, 100), (list_x + 5, skill_y - 5, list_width - 25, 70))
            
            # Skill name with element color
            element_color = self.element_colors.get(skill.element, (255, 255, 255))
            skill_text = self.skill_font.render(f"[{skill.element}] {skill.name}", True, 
                                               (150, 150, 150) if is_chosen else element_color)
            screen.blit(skill_text, (list_x + 15, skill_y))
            
            # Skill description (with wrapping for longer descriptions)
            desc_words = skill.description.split()
            desc_line = ""
            desc_y = skill_y + 30
            for word in desc_words:
                test_line = desc_line + " " + word if desc_line else word
                test_surf = self.desc_font.render(test_line, True, (200, 200, 200))
                if test_surf.get_width() < list_width - 40:
                    desc_line = test_line
                else:
                    text = self.desc_font.render(desc_line, True, (200, 200, 200))
                    screen.blit(text, (list_x + 20, desc_y))
                    desc_y += 20
                    desc_line = word
            
            # Draw the last line
            if desc_line:
                text = self.desc_font.render(desc_line, True, (200, 200, 200))
                screen.blit(text, (list_x + 20, desc_y))
    
    def draw_chosen_skills(self, screen):
        chosen_y = 500
        chosen_title = self.skill_font.render(f"Selected Skills ({len(self.chosen_skills)}/{self.picks_needed})", True, (255, 255, 255))
        screen.blit(chosen_title, (screen.get_width()//2 - chosen_title.get_width()//2, chosen_y - 30))
        
        # Draw slots for chosen skills
        for i in range(self.picks_needed):
            slot_x = (screen.get_width() // 2) - ((self.picks_needed * 120) // 2) + (i * 120) + 10
            slot_y = chosen_y
            
            # Draw slot background
            pygame.draw.rect(screen, (30, 30, 60), (slot_x, slot_y, 100, 80))
            pygame.draw.rect(screen, (100, 100, 150), (slot_x, slot_y, 100, 80), 2)
            
            # If there's a skill in this slot, draw it
            if i < len(self.chosen_skills):
                skill = self.chosen_skills[i]
                element_color = self.element_colors.get(skill.element, (255, 255, 255))
                
                # Draw element color indicator
                pygame.draw.rect(screen, element_color, (slot_x, slot_y, 5, 80))
                
                # Skill name (centered in slot)
                name_text = self.skill_font.render(skill.name, True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(slot_x + 50, slot_y + 30))
                screen.blit(name_text, name_rect)
                
                # Element
                element_text = self.desc_font.render(skill.element, True, element_color)
                element_rect = element_text.get_rect(center=(slot_x + 50, slot_y + 60))
                screen.blit(element_text, element_rect)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_skill = max(0, self.selected_skill - 1)
                    # Adjust scroll if needed
                    if self.selected_skill < self.scroll_offset:
                        self.scroll_offset = self.selected_skill
                
                elif event.key == pygame.K_DOWN:
                    self.selected_skill = min(len(self.all_skills) - 1, self.selected_skill + 1)
                    # Adjust scroll if needed
                    if self.selected_skill >= self.scroll_offset + self.skills_per_page:
                        self.scroll_offset = self.selected_skill - self.skills_per_page + 1
                
                elif event.key == pygame.K_RETURN:
                    # Add selected skill to chosen (if not already chosen and haven't reached limit)
                    selected = self.all_skills[self.selected_skill]
                    if selected not in self.chosen_skills and len(self.chosen_skills) < self.picks_needed:
                        self.chosen_skills.append(selected)
                
                elif event.key == pygame.K_BACKSPACE:
                    # Remove the last chosen skill
                    if self.chosen_skills:
                        self.chosen_skills.pop()
                
                elif event.key == pygame.K_SPACE:
                    # Confirm selection if we have enough skills
                    if len(self.chosen_skills) == self.picks_needed:
                        self.game.deck.skills = self.chosen_skills
                        self.game.finish_initialization()
                        return "PLAYING"
                
                elif event.key == pygame.K_ESCAPE:
                    # Go back to main menu
                    return "MENU"
        
        return None


class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        
    def enter(self):
        # Nothing special needed when entering play state
        pass
        
    def exit(self):
        # Cleanup, save progress, etc.
        pass
        
    def update(self, dt):
        # 1. Update enemy positions and attacks
        for e in self.game.enemies:
            e.update(self.game.player, dt)

        # 2. Handle player input (movement)
        self.game.player.handle_input(dt)

        # 3. Update deck
        self.game.player.deck.update(dt, self.game.enemies)

        # 4. Resolve collisions
        entities = [entity for entity in ([self.game.player] + 
                                          self.game.player.summons + 
                                          self.game.enemies) if entity.alive]
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                self.game.resolve_overlap(entities[i], entities[j])

        # 5. Clean up dead entities
        self.game.enemies = [e for e in self.game.enemies if e.alive]

        # 6. Wave logic
        if len(self.game.enemies) == 0:
            self.game.wave_number += 1
            self.game.spawn_wave()

        # 7. Update visual effects
        for eff in self.game.effects:
            eff.update(dt)
        self.game.effects = [ef for ef in self.game.effects if ef.active]
        
        # Check for player death
        if self.game.player.health <= 0:
            return "GAME_OVER"
            
    def render(self, screen):
        # Draw game background
        screen.fill((255, 255, 255))
        
        # Draw game information
        self.game.draw_wave_info()
        self.game.draw_player_bars()
        self.game.draw_skill_ui()
        
        # Draw all game objects in proper layers
        # 1. Draw entities (enemies, player)
        for enemy in self.game.enemies:
            enemy.draw(screen)

        # 2. Draw player
        self.game.player.draw(screen)

        # 3. Draw projectiles and summons via deck
        self.game.player.deck.draw(screen)

        # 4. Draw overhead effects (top layer)
        for effect in self.game.effects:
            effect.draw(screen)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "PAUSED"
                
                # Volume controls
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    # Decrease volume
                    current_vol = self.game.audio_manager.music_volume
                    self.game.audio_manager.set_music_volume(current_vol - 0.1)
                    print(f"Music volume: {self.game.audio_manager.music_volume:.1f}")
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    # Increase volume
                    current_vol = self.game.audio_manager.music_volume
                    self.game.audio_manager.set_music_volume(current_vol + 0.1)
                    print(f"Music volume: {self.game.audio_manager.music_volume:.1f}")
                
                elif event.key == pygame.K_m:
                    # Toggle music
                    music_enabled = self.game.audio_manager.toggle_music()
                    state = "on" if music_enabled else "off"
                    print(f"Music: {state}")
                    
            # Process other gameplay events
            mouse_pos = pygame.mouse.get_pos()
            now = time.time()
            result = self.game.player.handle_event(event, mouse_pos, self.game.enemies, now, self.game.effects)
            if result == 'exit':
                return "QUIT"
                
        return None


class PausedState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.menu_font = pygame.font.SysFont("Arial", 32)
        self.options = ["Resume", "Music: On", "Return to Menu", "Quit"]
        self.selected = 0
        
    def enter(self):
        self.selected = 0
        # Update the Music option text based on current state
        music_state = "On" if self.game.audio_manager.music_enabled else "Off"
        self.options[1] = f"Music: {music_state}"
        
    def update(self, dt):
        # No updates while paused
        pass
        
    def render(self, screen):
        # First draw the game in the background
        screen.fill((255, 255, 255))
        
        # Draw game information
        self.game.draw_wave_info()
        self.game.draw_player_bars()
        self.game.draw_skill_ui()
        
        # Draw game elements
        for enemy in self.game.enemies:
            enemy.draw(screen)
            
        self.game.player.draw(screen)
        self.game.player.deck.draw(screen)
        
        for effect in self.game.effects:
            effect.draw(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Black with alpha
        screen.blit(overlay, (0, 0))
        
        # Draw pause title
        title = self.menu_font.render("GAME PAUSED", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))
        
        # Draw menu options
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected else (255, 255, 255)
            text = self.menu_font.render(option, True, color)
            pos_y = 250 + i * 60
            screen.blit(text, (screen.get_width()//2 - text.get_width()//2, pos_y))
            
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "PLAYING"  # Resume game
                    
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    if self.selected == 0:  # Resume
                        return "PLAYING"
                    elif self.selected == 1:  # Toggle Music
                        # Toggle music on/off
                        music_enabled = self.game.audio_manager.toggle_music()
                        music_state = "On" if music_enabled else "Off"
                        self.options[1] = f"Music: {music_state}"
                    elif self.selected == 2:  # Return to Menu
                        return "MENU"
                    elif self.selected == 3:  # Quit
                        return "QUIT"
        return None


class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("Arial", 32)
        self.title_font = pygame.font.SysFont("Arial", 64)
        
    def enter(self):
        self.game.log_csv(self.game.wave_number)  # Log game results
        
    def update(self, dt):
        pass
        
    def render(self, screen):
        # Black background
        screen.fill((0, 0, 0))
        
        # Game Over title
        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))
        
        # Stats
        wave_text = self.font.render(f"Waves Survived: {self.game.wave_number}", True, (255, 255, 255))
        screen.blit(wave_text, (screen.get_width()//2 - wave_text.get_width()//2, 250))
        
        # Continue prompt
        prompt = self.font.render("Press ENTER to return to menu", True, (255, 255, 255))
        screen.blit(prompt, (screen.get_width()//2 - prompt.get_width()//2, 400))
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "MENU"
        return None 
