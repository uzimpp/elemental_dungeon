import pygame
import csv
import time
from config import Config as C
from ui import Button, ProgressBar, SkillDisplay, UIManager
from deck import Deck
from ui import UI
from font import Font
from data_collection import DataCollection

class GameStateManager:
    """Manages transitions between game states"""
    def __init__(self, game):
        self.game = game
        self.current_state = None
        self.states = {}
        self.overlay = None
    
    def add_state(self, state_id, state):
        self.states[state_id] = state
    
    def set_state(self, state_id):
        if self.current_state:
            self.current_state.exit()
        self.current_state = self.states[state_id]
        self.current_state.enter()
    
    def set_overlay(self, overlay):
        self.overlay = overlay
    
    def clear_overlay(self):
        self.overlay = None
    
    def update(self, dt):
        if self.current_state:
            result = self.current_state.update(dt)
            if result:  # Allow state to request state change
                self.set_state(result)
        if self.overlay:
            overlay_result = self.overlay.update(dt)
            if overlay_result:
                if overlay_result == "CLOSE_OVERLAY":
                    self.clear_overlay()
                else:
                    self.clear_overlay()
                    self.set_state(overlay_result)
    
    def render(self, screen):
        if self.current_state:
            self.current_state.render(screen)
        if self.overlay:
            self.overlay.render(screen)
    
    def handle_events(self, events):
        result = None
        if self.overlay:
            result = self.overlay.handle_events(events)
            if result == "CLOSE_OVERLAY":
                self.clear_overlay()
                return None
            elif result:
                self.clear_overlay()
                self.set_state(result)
                return None
        
        if not result and self.current_state:
            result = self.current_state.handle_events(events)
            if result:
                self.set_state(result)
        return None

class GameState:
    """Base class for game states"""
    def __init__(self, game):
        self.game = game
        self.ui_manager = UIManager(game.screen)
    
    def enter(self): pass
    def exit(self): pass
    def update(self, dt): return None
    def render(self, screen): pass
    def handle_events(self, events): return None

class PauseOverlay:
    """Reusable overlay for pause menu"""
    def __init__(self, game):
        self.game = game
        self.font = Font().get_font('MENU')
        
        # Centered buttons
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        
        music_status = 'On' if self.game.audio.music_enabled else 'Off'
        
        self.buttons = [
            Button(button_x, 250, button_width, button_height, "Resume", self.font),
            Button(button_x, 320, button_width, button_height, f"Music: {music_status}", self.font),
            Button(button_x, 390, button_width, button_height, "Retry", self.font),
            Button(button_x, 460, button_width, button_height, "Quit", self.font)
        ]
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
        return None
    
    def render(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # 50% transparent black
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font.render("PAUSED", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 180))
        
        # Buttons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "CLOSE_OVERLAY"
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.buttons[0].is_clicked(mouse_pos, True):  # Resume
                    return "CLOSE_OVERLAY"
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Music toggle
                    music_enabled = self.game.audio.toggle_music()
                    self.buttons[1].set_text(f"Music: {'On' if music_enabled else 'Off'}")
                elif self.buttons[2].is_clicked(mouse_pos, True):  # Retry
                    return "DECK_SELECTION"
                elif self.buttons[3].is_clicked(mouse_pos, True):  # Quit
                    return "MENU"
        return None

class GameOverOverlay:
    """Reusable game over overlay"""
    def __init__(self, game):
        self.game = game
        self.title_font = Font().get_font('TITLE')
        self.font = Font().get_font('MENU')
        
        # Centered buttons
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        
        self.buttons = [
            Button(button_x, 350, button_width, button_height, "Try Again", self.font),
            Button(button_x, 420, button_width, button_height, "Main Menu", self.font),
            Button(button_x, 490, button_width, button_height, "Quit", self.font)
        ]
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
        return None
    
    def render(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))  # Darker overlay for game over
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))
        
        # Stats
        wave_text = self.font.render(f"Waves Survived: {self.game.wave_number}", True, (255, 255, 255))
        screen.blit(wave_text, (screen.get_width()//2 - wave_text.get_width()//2, 230))
        
        # Buttons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.buttons[0].is_clicked(mouse_pos, True):  # Try Again
                    return "DECK_SELECTION"
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Main Menu
                    return "MENU"
                elif self.buttons[2].is_clicked(mouse_pos, True):  # Quit
                    return "QUIT"
        return None

class MenuState(GameState):
    """Main menu state"""
    def __init__(self, game):
        super().__init__(game)
        self.title_font = Font().get_font('TITLE')
        self.menu_font = Font().get_font('MENU')
        self.info_font = Font().get_font('UI')
        
        # Create buttons
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        
        start_button = Button(button_x, 250, button_width, button_height, "Start", self.menu_font)
        quit_button = Button(button_x, 320, button_width, button_height, "Quit", self.menu_font)
        
        self.ui_manager.add_element(start_button, "buttons")
        self.ui_manager.add_element(quit_button, "buttons")
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)
        return None
    
    def render(self, screen):
        screen.fill((50, 50, 100))
        
        # Title
        title = self.title_font.render("INCANTATO", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # Player name if available
        if self.game.player_name:
            player_text = self.info_font.render(f"Player: {self.game.player_name}", True, (200, 200, 200))
            screen.blit(player_text, (screen.get_width()//2 - player_text.get_width()//2, 170))
        
        # Draw UI elements
        self.ui_manager.draw_all()
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            # Process UI element events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                buttons = self.ui_manager.elements.get("buttons", [])
                for i, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos, True):
                        if i == 0:  # Start
                            if self.game.player_name is None:
                                return "NAME_ENTRY"
                            else:
                                return "DECK_SELECTION"
                        elif i == 1:  # Quit
                            return "QUIT"
        return None

class NameEntryState(GameState):
    """State for entering player name"""
    def __init__(self, game):
        super().__init__(game)
        self.title_font = Font().get_font('TITLE')
        self.input_font = Font().get_font('TITLE')
        self.player_name = ""
        self.active = True
        
        # Input box properties
        self.input_rect = pygame.Rect(C.WIDTH//2 - 200, 300, 400, 60)
        self.input_color_active = pygame.Color(C.WHITE)
        self.input_color_inactive = pygame.Color(C.GREY)
        self.input_color = self.input_color_active
        
        # Submit button
        button_width, button_height = 200, 50
        button_x = C.WIDTH//2 - button_width//2
        submit_button = Button(button_x, 400, button_width, button_height, 
                              "Continue", self.title_font)
        self.ui_manager.add_element(submit_button, "buttons")
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)
        return None
    
    def render(self, screen):
        screen.fill(C.BLACK)
        
        # Title
        title_text = self.title_font.render("Enter Your Name", True, C.WHITE)
        title_rect = title_text.get_rect(center=(C.WIDTH//2, 200))
        screen.blit(title_text, title_rect)
        
        # Draw input box
        pygame.draw.rect(screen, self.input_color, self.input_rect, 2)
        text_surface = self.input_font.render(self.player_name, True, C.WHITE)
        screen.blit(text_surface, (self.input_rect.x + 10, self.input_rect.y + 10))
        
        # Draw UI elements
        self.ui_manager.draw_all()
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if input box was clicked
                if self.input_rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
                self.input_color = self.input_color_active if self.active else self.input_color_inactive
                
                # Check if submit button was clicked
                mouse_pos = pygame.mouse.get_pos()
                buttons = self.ui_manager.elements.get("buttons", [])
                for button in buttons:
                    if button.is_clicked(mouse_pos, True):
                        self.submit_name()
                        return "DECK_SELECTION"
                    
            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        self.submit_name()
                        return "DECK_SELECTION"
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        # Limit name length to 15 characters
                        if len(self.player_name) < 15:
                            self.player_name += event.unicode
        return None
    
    def submit_name(self):
        """Process the final name submission"""
        final_name = self.player_name.strip()
        if not final_name:
            final_name = "Unknown"
        self.game.player_name = final_name
        self.game.initialize_player()  # Create player object with name

class DeckSelectionState(GameState):
    """State for selecting skills for player deck"""
    SKILLS_PER_PAGE = 5

    def __init__(self, game):
        super().__init__(game)
        self.title_font = Font().get_font('TITLE')
        self.skill_font = Font().get_font('SKILL')
        self.desc_font = Font().get_font('DESC')
        
        # Skill selection data
        self.skill_data = []
        self.selected_skill_data = []
        self.scroll_offset = 0
        self.selected_index = 0
        
        # Create UI
        screen_width = game.screen.get_width()
        
        # Back button
        back_button = Button(10, 10, 100, 40, "Back", Font().get_font('DESC'))
        self.ui_manager.add_element(back_button, "navigation")
        
        # Confirm button 
        confirm_button = Button((screen_width - 200) // 2, 650, 200, 50, "Confirm", Font().get_font('SKILL'))
        self.ui_manager.add_element(confirm_button, "navigation")
        
        # Scroll buttons
        up_button = Button(screen_width // 2 + 180, 80, 40, 40, "▲", Font().get_font('SKILL'))
        down_button = Button(screen_width // 2 + 180, 440, 40, 40, "▼", Font().get_font('SKILL'))
        self.ui_manager.add_element(up_button, "scroll")
        self.ui_manager.add_element(down_button, "scroll")
        
        # Element colors for displaying skills
        self.element_colors = {k: v['primary'] for k, v in C.ELEMENT_COLORS.items()}
    
    def enter(self):
        """Load skill data when entering state"""
        self.skill_data = self.load_skill_data()
        self.selected_skill_data = []
        self.scroll_offset = 0
        self.selected_index = 0
    
    def load_skill_data(self):
        """Load raw skill data from CSV file"""
        skill_data = []
        try:
            with open(C.SKILLS_FILENAME, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill_data.append(row)
        except Exception as e:
            print(f"Error loading skills data: {e}")
        return skill_data
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)
        return None
    
    def render(self, screen):
        # Background
        screen.fill((40, 40, 80))

        # Title
        title = self.title_font.render(f"BUILD YOUR DECK (Pick {C.SKILLS_LIMIT})", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 30))

        # Draw skill list
        self.draw_skill_list(screen)
        # Draw selected skills
        UI.draw_selected_skills(screen, self.selected_skill_data)
        
        # Draw UI elements (buttons)
        self.ui_manager.draw_all()
    
    def draw_skill_list(self, screen):
        """Draw the list of available skills"""
        list_width = screen.get_width() * 0.6
        list_height = 400
        list_x = (screen.get_width() - list_width) // 2
        list_y = 80
        # Draw list background
        pygame.draw.rect(screen, (30, 30, 60), (list_x, list_y, list_width, list_height))
        pygame.draw.rect(screen, (100, 100, 150), (list_x, list_y, list_width, list_height), 2)
        
        # Draw scrollbar if needed
        if len(self.skill_data) > self.SKILLS_PER_PAGE:
            scrollbar_height = list_height * min(1.0, self.SKILLS_PER_PAGE / len(self.skill_data))
            scrollbar_pos = list_y + (list_height - scrollbar_height) * (self.scroll_offset / (len(self.skill_data) - self.SKILLS_PER_PAGE))
            pygame.draw.rect(screen, (150, 150, 180), (list_x + list_width - 15, scrollbar_pos, 10, scrollbar_height))
        
        # Draw visible skills
        visible_skills = self.skill_data[self.scroll_offset:self.scroll_offset + self.SKILLS_PER_PAGE]
        for i, skill in enumerate(visible_skills):
            # Check if this skill is already chosen
            is_chosen = skill in self.selected_skill_data
            skill_y = list_y + 10 + i * (list_height // self.SKILLS_PER_PAGE)
            
            # Create clickable area for the skill
            skill_rect = pygame.Rect(list_x + 5, skill_y - 5, list_width - 25, 70)
            
            # Highlight if this is the selected skill
            if i + self.scroll_offset == self.selected_index:
                pygame.draw.rect(screen, (60, 60, 100), skill_rect)
            
            # Skill name with element color
            element = skill["element"].upper()
            element_color = self.element_colors.get(element, (255, 255, 255))
            skill_text = self.skill_font.render(f"[{element}] {skill['name']}", True, 
                                               (150, 150, 150) if is_chosen else element_color)
            screen.blit(skill_text, (list_x + 15, skill_y))
            
            # Display cooldown and type
            cd_text = self.desc_font.render(f"Cooldown: {float(skill['cooldown']):.1f}s | Type: {skill['skill_type']}", True, (200, 200, 200))
            screen.blit(cd_text, (list_x + 15, skill_y + 30))
            
            # Skill description (truncated for space)
            desc = skill["description"]
            if len(desc) > 60:
                desc = desc[:57] + "..."
            desc_text = self.desc_font.render(desc, True, (200, 200, 200))
            screen.blit(desc_text, (list_x + 15, skill_y + 50))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Handle UI button clicks
                navigation_buttons = self.ui_manager.elements.get("navigation", [])
                for i, button in enumerate(navigation_buttons):
                    if button.is_clicked(mouse_pos, True):
                        if i == 0:  # Back button
                            return "MENU"
                        elif i == 1:  # Confirm button
                            if len(self.selected_skill_data) == C.SKILLS_LIMIT:
                                self.create_player_deck()
                                return "PLAYING"
                
                # Handle scroll buttons
                scroll_buttons = self.ui_manager.elements.get("scroll", [])
                for i, button in enumerate(scroll_buttons):
                    if button.is_clicked(mouse_pos, True):
                        if i == 0 and self.scroll_offset > 0:  # Up button
                            self.scroll_offset -= 1
                        elif i == 1 and self.scroll_offset < len(self.skill_data) - self.SKILLS_PER_PAGE:  # Down button
                            self.scroll_offset += 1
                
                # Check skill list clicks
                list_width = self.game.screen.get_width() * 0.6
                list_height = 400
                list_x = (self.game.screen.get_width() - list_width) // 2
                list_y = 80
                
                # Check if clicking in the skill list area
                if (list_x <= mouse_pos[0] <= list_x + list_width and
                    list_y <= mouse_pos[1] <= list_y + list_height):
                    
                    # Calculate which skill was clicked
                    skill_height = list_height // self.SKILLS_PER_PAGE
                    clicked_index = (mouse_pos[1] - list_y) // skill_height
                    
                    if 0 <= clicked_index < min(self.SKILLS_PER_PAGE, len(self.skill_data) - self.scroll_offset):
                        abs_index = self.scroll_offset + clicked_index
                        self.selected_index = abs_index
                        
                        # If double-clicked, select the skill
                        selected = self.skill_data[self.selected_index]
                        if selected not in self.selected_skill_data and len(self.selected_skill_data) < C.SKILLS_LIMIT:
                            self.selected_skill_data.append(selected)
                
                # Check if clicking on chosen skills to remove them
                chosen_y = 500
                for i in range(len(self.selected_skill_data)):
                    slot_x = (self.game.screen.get_width() // 2) - ((C.SKILLS_LIMIT * 120) // 2) + (i * 120) + 10
                    slot_y = chosen_y
                    slot_rect = pygame.Rect(slot_x, slot_y, 100, 80)
                    
                    if slot_rect.collidepoint(mouse_pos):
                        self.selected_skill_data.pop(i)
                        break
            
            # Keyboard navigation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    # Adjust scroll if needed
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.skill_data) - 1, self.selected_index + 1)
                    # Adjust scroll if needed
                    if self.selected_index >= self.scroll_offset + self.SKILLS_PER_PAGE:
                        self.scroll_offset = self.selected_index - self.SKILLS_PER_PAGE + 1
                
                elif event.key == pygame.K_RETURN:
                    # Add selected skill to chosen (if not already chosen and haven't reached limit)
                    if self.selected_index < len(self.skill_data):
                        selected = self.skill_data[self.selected_index]
                        if selected not in self.selected_skill_data and len(self.selected_skill_data) < C.SKILLS_LIMIT:
                            self.selected_skill_data.append(selected)
                
                elif event.key == pygame.K_BACKSPACE:
                    # Remove the last chosen skill
                    if self.selected_skill_data:
                        self.selected_skill_data.pop()
                
                elif event.key == pygame.K_SPACE:
                    # Confirm selection if we have enough skills
                    if len(self.selected_skill_data) == C.SKILLS_LIMIT:
                        self.create_player_deck()
                        self.game.prepare_game()  # Initialize gameplay
                        return "PLAYING"
                
                elif event.key == pygame.K_ESCAPE:
                    # Go back to main menu
                    return "MENU"
        
        return None
    
    def create_player_deck(self):
        """Create skill objects in the deck class based on selected skills"""
        deck = Deck()
        deck.create_skills(self.selected_skill_data)
        self.game.player.deck = deck

class PlayingState(GameState):
    """Main gameplay state"""
    def __init__(self, game):
        super().__init__(game)
        self.background = None
        self.load_background()
    
    def load_background(self):
        """Load the game background image"""
        try:
            bg_path = C.MAP_PATH
            self.background = pygame.image.load(bg_path).convert()
        except Exception as e:
            print(f"Error loading background: {e}")
            self.background = None
    
    def enter(self):
        """Initialize UI when entering state"""
        self.setup_ui()
    
    def setup_ui(self):
        """Set up UI elements for gameplay"""
        # Clear previous UI elements
        self.ui_manager.clear_group("status")
        self.ui_manager.clear_group("skills")
        
        # Add HP bar
        hp_bar = ProgressBar(
            10, 50, 200, 20, 
            self.game.player.max_health,
            bg_color=C.UI_COLORS['hp_bar_bg'],
            fill_color=C.UI_COLORS['hp_bar_fill'],
            text_color=C.UI_COLORS['hp_text'],
            font=pygame.font.Font(C.FONT_PATH, 16),
            label="HP"
        )
        self.ui_manager.add_element(hp_bar, "status")
        
        # Add stamina bar
        stamina_bar = ProgressBar(
            10, 80, 200, 20,
            self.game.player.max_stamina,
            bg_color=C.UI_COLORS['stamina_bar_bg'],
            fill_color=C.UI_COLORS['stamina_bar_fill'],
            text_color=C.UI_COLORS['stamina_text'],
            font=pygame.font.Font(C.FONT_PATH, 16),
            label="Stamina"
        )
        self.ui_manager.add_element(stamina_bar, "status")
        
        # Add skill displays
        skill_font = pygame.font.Font(C.FONT_PATH, 16)
        for i, skill in enumerate(self.game.player.deck.skills):
            skill_display = SkillDisplay(
                10 + i * 110, C.HEIGHT - 100,
                100, 80,
                skill, skill_font, 
                hotkey=str(i+1)
            )
            self.ui_manager.add_element(skill_display, "skills")
    
    def update(self, dt):
        # 1. Update enemy positions and attacks
        self.game.enemy_group.update(self.game.player, dt)
        
        # 2. Handle player input (movement)
        self.game.player.handle_input(dt)
        
        # 3. Update deck
        self.game.player.deck.update(dt, self.game.enemies)
        
        # 4. Update UI elements
        # Update HP bar
        status_elements = self.ui_manager.elements.get("status", [])
        if len(status_elements) >= 1:
            status_elements[0].set_value(self.game.player.health)
        
        # Update stamina bar
        if len(status_elements) >= 2:
            status_elements[1].set_value(self.game.player.stamina)
        
        # Update skill cooldowns
        now = time.time()
        skill_elements = self.ui_manager.elements.get("skills", [])
        for skill_display in skill_elements:
            skill_display.update_cooldown(now)
            
        # Update all UI elements
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)
        
        # 5. Check collisions
        self.game.check_collisions()
        
        # 6. Wave logic
        if len(self.game.enemy_group) == 0:
            self.game.wave_number += 1
            self.game.spawn_wave()
        
        # Check for player death
        if self.game.player.health <= 0:
            self.game.state_manager.set_overlay(GameOverOverlay(self.game))
        
        return None
    
    def render(self, screen):
        # Draw background
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((200, 220, 255))  # fallback color
        
        # Draw wave info
        ui_font = pygame.font.Font(C.FONT_PATH, 24)
        wave_text = ui_font.render(f"WAVE: {self.game.wave_number}", True, C.BLACK)
        screen.blit(wave_text, (10, 10))
        
        # Draw game objects
        for enemy in self.game.enemy_group:
            enemy.draw(screen)
            
        self.game.player.draw(screen)
        self.game.player.deck.draw(screen)
        
        # Draw UI
        self.ui_manager.draw_all()
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.state_manager.set_overlay(PauseOverlay(self.game))
                    return None
                
                # Volume controls
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol - 0.1)
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol + 0.1)
                
                elif event.key == pygame.K_m:
                    self.game.audio.toggle_music()
            
            # Process gameplay events (skill usage, etc.)
            mouse_pos = pygame.mouse.get_pos()
            now = time.time()
            result = self.game.player.handle_event(event, mouse_pos, self.game.enemies, now)
            if result == 'exit':
                return "MENU"
        return None

class PlayingState(GameState):
    """Main gameplay state"""
    def __init__(self, game):
        super().__init__(game)
        self.background = None
        self.load_background()
        self.paused = False
        self.ui_font = Font().get_font('MENU')
        
    def load_background(self):
        """Load the game background image"""
        try:
            bg_path = C.MAP_PATH
            self.background = pygame.image.load(bg_path).convert()
        except Exception as e:
            print(f"Error loading background: {e}")
            self.background = None
    
    def enter(self):
        """Initialize UI when entering state"""
        self.setup_ui()
        # Play game music if not already playing
        if self.game.audio.current_music != "PLAYING":
            self.game.audio.fade_out(500)
            self.game.audio.fade_in("PLAYING", 1000)
    
    def exit(self):
        """Clean up when leaving state"""
        pass
    
    def setup_ui(self):
        """Set up UI elements for gameplay"""
        # Clear previous UI elements
        self.ui_manager.clear_group("status")
        self.ui_manager.clear_group("skills")
        
        # Add HP bar
        hp_bar = ProgressBar(
            10, 50, 200, 20, 
            self.game.player.max_health,
            bg_color=C.UI_COLORS['hp_bar_bg'],
            fill_color=C.UI_COLORS['hp_bar_fill'],
            text_color=C.UI_COLORS['hp_text'],
            font=Font().get_font('UI'),
            label="HP"
        )
        self.ui_manager.add_element(hp_bar, "status")
        
        # Add stamina bar
        stamina_bar = ProgressBar(
            10, 80, 200, 20,
            self.game.player.max_stamina,
            bg_color=C.UI_COLORS['stamina_bar_bg'],
            fill_color=C.UI_COLORS['stamina_bar_fill'],
            text_color=C.UI_COLORS['stamina_text'],
            font=Font().get_font('UI'),
            label="Stamina"
        )
        self.ui_manager.add_element(stamina_bar, "status")
        
        # Add skill displays
        skill_font = Font().get_font('UI')
        for i, skill in enumerate(self.game.player.deck.skills):
            skill_display = SkillDisplay(
                10 + i * 110, C.HEIGHT - 100,
                100, 80,
                skill, skill_font, 
                hotkey=str(i+1)
            )
            self.ui_manager.add_element(skill_display, "skills")
    
    def update(self, dt):
        # Skip updates if game objects aren't ready
        if not hasattr(self.game, 'player') or not self.game.player:
            return None
            
        # 1. Update enemy positions and attacks
        self.game.enemy_group.update(self.game.player, dt)
        
        # 2. Handle player input (movement)
        self.game.player.handle_input(dt)
        
        # 3. Update deck
        self.game.player.deck.update(dt, self.game.enemies)
        
        # 4. Update UI elements
        # Update HP bar
        status_elements = self.ui_manager.elements.get("status", [])
        if len(status_elements) >= 1:
            status_elements[0].set_value(self.game.player.health)
        
        # Update stamina bar
        if len(status_elements) >= 2:
            status_elements[1].set_value(self.game.player.stamina)
        
        # Update skill cooldowns
        now = time.time()
        skill_elements = self.ui_manager.elements.get("skills", [])
        for skill_display in skill_elements:
            skill_display.update_cooldown(now)
            
        # Update all UI elements
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)
        
        # 5. Check collisions
        self.game.check_collisions()
        
        # 6. Wave logic
        if len(self.game.enemy_group) == 0:
            self.game.wave_number += 1
            self.game.spawn_wave()
        
        # Check for player death
        if self.game.player.health <= 0:
            # Log the game results
            DataCollection.log_csv(self.game, self.game.wave_number)
            # Show game over overlay
            self.game.state_manager.set_overlay(GameOverOverlay(self.game))
        
        return None
    
    def render(self, screen):
        # Draw background
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((200, 220, 255))  # fallback color
        
        # Draw wave info
        wave_text = self.ui_font.render(f"WAVE: {self.game.wave_number}", True, C.BLACK)
        screen.blit(wave_text, (10, 10))
        
        # Draw game objects
        for enemy in self.game.enemy_group:
            enemy.draw(screen)
            
        self.game.player.draw(screen)
        self.game.player.deck.draw(screen)
        
        # Draw UI
        self.ui_manager.draw_all()
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.state_manager.set_overlay(PauseOverlay(self.game))
                    return None
                
                # Volume controls
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol - 0.1)
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol + 0.1)
                
                elif event.key == pygame.K_m:
                    self.game.audio.toggle_music()
            
            # Process gameplay events (skill usage, etc.)
            if hasattr(self.game, 'player') and self.game.player:
                mouse_pos = pygame.mouse.get_pos()
                now = time.time()
                result = self.game.player.handle_event(event, mouse_pos, self.game.enemies, now)
                if result == 'exit':
                    return "MENU"
        
        return None
class PauseOverlay:
    """Reusable overlay for pause menu"""
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(C.FONT_PATH, 32)
        
        # Centered buttons
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        
        music_status = 'On' if self.game.audio.music_enabled else 'Off'
        
        self.buttons = [
            Button(button_x, 250, button_width, button_height, "Resume", self.font),
            Button(button_x, 320, button_width, button_height, f"Music: {music_status}", self.font),
            Button(button_x, 390, button_width, button_height, "Retry", self.font),
            Button(button_x, 460, button_width, button_height, "Quit", self.font)
        ]
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
        return None
    
    def render(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # 50% transparent black
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font.render("PAUSED", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 180))
        
        # Buttons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "CLOSE_OVERLAY"
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.buttons[0].is_clicked(mouse_pos, True):  # Resume
                    return "CLOSE_OVERLAY"
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Music toggle
                    music_enabled = self.game.audio.toggle_music()
                    self.buttons[1].text = f"Music: {'On' if music_enabled else 'Off'}"
                elif self.buttons[2].is_clicked(mouse_pos, True):  # Retry
                    return "DECK_SELECTION"
                elif self.buttons[3].is_clicked(mouse_pos, True):  # Quit
                    return "MENU"
        return None

class GameOverOverlay:
    """Reusable game over overlay"""
    def __init__(self, game):
        self.game = game
        self.title_font = Font().get_font('TITLE')
        self.font = pygame.font.Font(C.FONT_PATH, 32)
        
        # Centered buttons
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        
        self.buttons = [
            Button(button_x, 350, button_width, button_height, "Try Again", self.font),
            Button(button_x, 420, button_width, button_height, "Main Menu", self.font),
            Button(button_x, 490, button_width, button_height, "Quit", self.font)
        ]
    
    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
        return None
    
    def render(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))  # Darker overlay for game over
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))
        
        # Stats
        wave_text = self.font.render(f"Waves Survived: {self.game.wave_number}", True, (255, 255, 255))
        screen.blit(wave_text, (screen.get_width()//2 - wave_text.get_width()//2, 230))
        
        # Buttons
        for button in self.buttons:
            button.draw(screen)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.buttons[0].is_clicked(mouse_pos, True):  # Try Again
                    return "DECK_SELECTION"
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Main Menu
                    return "MENU"
                elif self.buttons[2].is_clicked(mouse_pos, True):  # Quit
                    return "QUIT"
        return None

