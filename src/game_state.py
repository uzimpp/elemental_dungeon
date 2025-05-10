import pygame
import time
from config import Config as C


class Button:
    """A clickable button class for UI elements"""
    def __init__(self, x, y, width, height, text, font, color=(255, 255, 255), hover_color=(255, 255, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        # Draw button background
        pygame.draw.rect(screen, (30, 30, 60), self.rect)
        pygame.draw.rect(screen, (100, 100, 150), self.rect, 2)
        
        # Render text
        text_color = self.hover_color if self.is_hovered else self.color
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        # Check if mouse is hovering over button
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_click):
        # Check if button was clicked
        return self.rect.collidepoint(mouse_pos) and mouse_click

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
        self.menu_font = pygame.font.Font(C.FONT_PATH, 32)
        self.title_font = pygame.font.Font(C.FONT_PATH, 48)
        self.info_font = pygame.font.Font(C.FONT_PATH, 20)
        
        # Create buttons
        screen_width = game.screen.get_width()
        screen_height = game.screen.get_height()
        button_width = 200
        button_height = 50
        
        # Position buttons in the center of the screen
        button_x = (screen_width - button_width) // 2
        
        self.buttons = [
            Button(button_x, 250, button_width, button_height, "Start", self.menu_font),
            Button(button_x, 320, button_width, button_height, "Stats", self.menu_font),
            Button(button_x, 390, button_width, button_height, "Quit", self.menu_font)
        ]
        
        # Stats panel (initially hidden)
        self.show_stats = False
        self.back_button = Button(screen_width // 2 - 100, 500, 200, 50, "Back", self.menu_font)
    
    def enter(self):
        self.show_stats = False
    
    def update(self, dt):
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
            
        if self.show_stats:
            self.back_button.update(mouse_pos)
    
    def render(self, screen):
        screen.fill((50, 50, 100))
        
        title = self.title_font.render("INCANTATO", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # If showing stats panel
        if self.show_stats:
            self._render_stats_panel(screen)
            return
            
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
            
        # Display player name if they've played before
        if self.game.player_name != "Unknown":
            player_text = self.info_font.render(f"Player: {self.game.player_name}", True, (200, 200, 200))
            screen.blit(player_text, (screen.get_width()//2 - player_text.get_width()//2, 170))
            
            # If there's a high score, show it
            if self.game.profile.high_score > 0:
                score_text = self.info_font.render(f"Best Score: {self.game.profile.high_score} waves", True, (200, 200, 200))
                screen.blit(score_text, (screen.get_width()//2 - score_text.get_width()//2, 200))
    
    def _render_stats_panel(self, screen):
        """Render the statistics panel"""
        # Stats panel background
        panel_width = 400
        panel_height = 300
        panel_x = (screen.get_width() - panel_width) // 2
        panel_y = 200
        
        pygame.draw.rect(screen, (30, 30, 60), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 150), (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Stats panel title
        stats_title = self.menu_font.render("Player Statistics", True, (255, 255, 255))
        screen.blit(stats_title, (screen.get_width()//2 - stats_title.get_width()//2, panel_y + 20))
        
        # Player name
        name_text = self.info_font.render(f"Player Name: {self.game.player_name}", True, (200, 200, 200))
        screen.blit(name_text, (panel_x + 50, panel_y + 80))
        
        # High score
        score_text = self.info_font.render(f"Best Score: {self.game.profile.high_score} waves", True, (200, 200, 200))
        screen.blit(score_text, (panel_x + 50, panel_y + 120))
        
        # Games played
        games_text = self.info_font.render(f"Games Played: {self.game.profile.games_played}", True, (200, 200, 200))
        screen.blit(games_text, (panel_x + 50, panel_y + 160))
        
        # Draw back button
        self.back_button.draw(screen)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                
                # If showing stats panel, only check the back button
                if self.show_stats:
                    if self.back_button.is_clicked(mouse_pos, True):
                        self.show_stats = False
                    return None
                
                # Check button clicks
                if self.buttons[0].is_clicked(mouse_pos, True):  # Start button
                    # If player name already exists, skip to deck selection
                    if self.game.player_name != "Unknown":
                        self.game.initialize_player()
                        return "DECK_SELECTION"
                    else:
                        return "NAME_ENTRY"
                        
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Stats button
                    self.show_stats = True
                    
                elif self.buttons[2].is_clicked(mouse_pos, True):  # Quit button
                    return "QUIT"
            
            # Keep keyboard navigation as well
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Find which button is currently hovered
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # If showing stats, check back button
                    if self.show_stats:
                        if self.back_button.is_hovered:
                            self.show_stats = False
                        return None
                    
                    for i, button in enumerate(self.buttons):
                        if button.is_hovered:
                            if i == 0:  # Start
                                if self.game.player_name != "Unknown":
                                    self.game.initialize_player()
                                    return "DECK_SELECTION"
                                else:
                                    return "NAME_ENTRY"
                            elif i == 1:  # Stats
                                self.show_stats = True
                            elif i == 2:  # Quit
                                return "QUIT"
                            break
                            
                elif event.key == pygame.K_ESCAPE and self.show_stats:
                    self.show_stats = False
        return None


class PlayerNameState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.title_font = pygame.font.Font(C.FONT_PATH, 36)
        self.input_font = pygame.font.Font(C.FONT_PATH, 28)
        self.info_font = pygame.font.Font(C.FONT_PATH, 20)
        self.name = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_rate = 0.5  # Blink every half second
        
        # Create back button
        self.back_button = Button(10, 10, 100, 40, "Back", self.info_font)
        
        # Create continue button
        screen_width = game.screen.get_width()
        self.continue_button = Button(
            (screen_width - 200) // 2,
            350,
            200,
            50,
            "Continue",
            self.input_font
        )
    
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
            
        # Update buttons
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos)
        self.continue_button.update(mouse_pos)
    
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
        
        # Draw buttons
        self.back_button.draw(screen)
        self.continue_button.draw(screen)
        
        # Default name info
        if not self.name:
            default_text = self.info_font.render("(Leave empty for 'Unknown')", True, (150, 150, 150))
            screen.blit(default_text, (screen.get_width()//2 - default_text.get_width()//2, input_y + input_height + 60))
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check back button
                if self.back_button.is_clicked(mouse_pos, True):
                    return "MENU"
                
                # Check continue button
                if self.continue_button.is_clicked(mouse_pos, True):
                    self.game.player_name = self.name if self.name else "Unknown"
                    self.game.initialize_player()
                    return "DECK_SELECTION"
            
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
        self.title_font = pygame.font.Font(C.FONT_PATH, 36)
        self.skill_font = pygame.font.Font(C.FONT_PATH, 24)
        self.desc_font = pygame.font.Font(C.FONT_PATH, 18)
        self.info_font = pygame.font.Font(C.FONT_PATH, 20)
        
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
        
        # Create buttons
        screen_width = game.screen.get_width()
        self.back_button = Button(10, 10, 100, 40, "Back", self.info_font)
        self.confirm_button = Button(
            (screen_width - 200) // 2,
            650,
            200,
            50,
            "Confirm",
            self.skill_font
        )
        
        # Create scroll buttons
        self.up_button = Button(screen_width // 2 + 180, 80, 40, 40, "▲", self.skill_font)
        self.down_button = Button(screen_width // 2 + 180, 440, 40, 40, "▼", self.skill_font)
    
    def enter(self):
        # Load skills from CSV
        if not hasattr(self, 'all_skills'):
            self.all_skills = self.game.deck.load_from_csv(self.game.skills_filename)
        
        self.scroll_offset = 0
        self.selected_skill = 0
        self.chosen_skills = []
    
    def update(self, dt):
        # Update buttons
        mouse_pos = pygame.mouse.get_pos()
        self.back_button.update(mouse_pos)
        self.confirm_button.update(mouse_pos)
        self.up_button.update(mouse_pos)
        self.down_button.update(mouse_pos)
    
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
        
        # Draw buttons
        self.back_button.draw(screen)
        self.confirm_button.draw(screen)
        self.up_button.draw(screen)
        self.down_button.draw(screen)
    
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
            
            # Create clickable area for the skill
            skill_rect = pygame.Rect(list_x + 5, skill_y - 5, list_width - 25, 70)
            
            # Highlight if this is the selected skill
            if i + self.scroll_offset == self.selected_skill:
                pygame.draw.rect(screen, (60, 60, 100), skill_rect)
            
            # Skill name with element color
            element_color = self.element_colors.get(skill.element, (255, 255, 255))
            skill_text = self.skill_font.render(f"[{skill.element}] {skill.name}", True, 
                                               (150, 150, 150) if is_chosen else element_color)
            screen.blit(skill_text, (list_x + 15, skill_y))
            
            # Display cooldown and type
            cd_text = self.desc_font.render(f"Cooldown: {skill.cooldown:.1f}s | Type: {skill.type}", True, (200, 200, 200))
            screen.blit(cd_text, (list_x + 15, skill_y + 30))
            
            # Skill description (with wrapping for longer descriptions)
            desc_words = skill.description.split()
            desc_line = ""
            desc_y = skill_y + 50
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
            slot_rect = pygame.Rect(slot_x, slot_y, 100, 80)
            pygame.draw.rect(screen, (30, 30, 60), slot_rect)
            pygame.draw.rect(screen, (100, 100, 150), slot_rect, 2)
            
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
                
                # Element and cooldown
                element_text = self.desc_font.render(skill.element, True, element_color)
                element_rect = element_text.get_rect(center=(slot_x + 50, slot_y + 50))
                screen.blit(element_text, element_rect)
                
                cooldown_text = self.desc_font.render(f"{skill.cooldown:.1f}s", True, (200, 200, 200))
                cooldown_rect = cooldown_text.get_rect(center=(slot_x + 50, slot_y + 65))
                screen.blit(cooldown_text, cooldown_rect)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check back button
                if self.back_button.is_clicked(mouse_pos, True):
                    return "MENU"
                
                # Check confirm button
                if self.confirm_button.is_clicked(mouse_pos, True):
                    if len(self.chosen_skills) == self.picks_needed:
                        self.game.deck.skills = self.chosen_skills
                        self.game.finish_initialization()
                        return "PLAYING"
                
                # Check scroll buttons
                if self.up_button.is_clicked(mouse_pos, True) and self.scroll_offset > 0:
                    self.scroll_offset -= 1
                
                if self.down_button.is_clicked(mouse_pos, True) and self.scroll_offset < len(self.all_skills) - self.skills_per_page:
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
                    skill_height = list_height // self.skills_per_page
                    clicked_index = (mouse_pos[1] - list_y) // skill_height
                    
                    if 0 <= clicked_index < min(self.skills_per_page, len(self.all_skills) - self.scroll_offset):
                        self.selected_skill = self.scroll_offset + clicked_index
                        
                        # If double-clicked (or single click for simplicity), select the skill
                        selected = self.all_skills[self.selected_skill]
                        if selected not in self.chosen_skills and len(self.chosen_skills) < self.picks_needed:
                            self.chosen_skills.append(selected)
                
                # Check if clicking on chosen skills to remove them
                chosen_y = 500
                for i in range(len(self.chosen_skills)):
                    slot_x = (self.game.screen.get_width() // 2) - ((self.picks_needed * 120) // 2) + (i * 120) + 10
                    slot_y = chosen_y
                    slot_rect = pygame.Rect(slot_x, slot_y, 100, 80)
                    
                    if slot_rect.collidepoint(mouse_pos):
                        self.chosen_skills.pop(i)
                        break
            
            # Keep keyboard navigation as well
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
        pass
        
    def exit(self):
        # Cleanup, save progress, etc.
        pass
        
    def update(self, dt):
        # 1. Update enemy positions and attacks
        self.game.enemy_group.update(self.game.player, dt)

        # 2. Handle player input (movement)
        self.game.player.handle_input(dt)

        # 3. Update deck
        self.game.player.deck.update(dt, self.game.enemies)

        # 4. Check collisions using sprite groups
        self.game.check_collisions()

        # 5. Wave logic
        if len(self.game.enemy_group) == 0:
            self.game.wave_number += 1
            self.game.spawn_wave()
        
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
        # 1. Draw enemies
        for enemy in self.game.enemy_group:
            enemy.draw(screen)

        # 2. Draw player
        self.game.player.draw(screen)

        # 3. Draw projectiles, summons, and effects via deck
        self.game.player.deck.draw(screen)
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "PAUSED"
                
                # Volume controls
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol - 0.1)
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol + 0.1)
                
                elif event.key == pygame.K_m:
                    self.game.audio.toggle_music()
                    
            # Process other gameplay events
            mouse_pos = pygame.mouse.get_pos()
            now = time.time()
            result = self.game.player.handle_event(event, mouse_pos, self.game.enemies, now)
            if result == 'exit':
                return "QUIT"
                
        return None


class PausedState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.menu_font = pygame.font.Font(C.FONT_PATH, 32)
        
        # Create buttons
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        
        self.buttons = [
            Button(button_x, 250, button_width, button_height, "Resume", self.menu_font),
            Button(button_x, 320, button_width, button_height, "Music: On", self.menu_font),
            Button(button_x, 390, button_width, button_height, "Return to Menu", self.menu_font),
            Button(button_x, 460, button_width, button_height, "Quit", self.menu_font)
        ]
        
    def enter(self):
        music_state = "On" if self.game.audio.music_enabled else "Off"
        self.buttons[1].text = f"Music: {music_state}"
        
    def update(self, dt):
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
        
    def render(self, screen):
        # First draw the game in the background
        screen.fill((255, 255, 255))
        
        self.game.draw_wave_info()
        self.game.draw_player_bars()
        self.game.draw_skill_ui()
        
        for enemy in self.game.enemies:
            enemy.draw(screen)
            
        self.game.player.draw(screen)
        self.game.player.deck.draw(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        
        # Draw pause menu title
        title = self.menu_font.render("GAME PAUSED", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
            
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check button clicks
                if self.buttons[0].is_clicked(mouse_pos, True):  # Resume
                    return "PLAYING"
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Music toggle
                    music_enabled = self.game.audio.toggle_music()
                    music_state = "On" if music_enabled else "Off"
                    self.buttons[1].text = f"Music: {music_state}"
                elif self.buttons[2].is_clicked(mouse_pos, True):  # Return to menu
                    return "MENU"
                elif self.buttons[3].is_clicked(mouse_pos, True):  # Quit
                    return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "PLAYING"
                    
                if event.key == pygame.K_UP:
                    # Find current hovered button and move up
                    for i, button in enumerate(self.buttons):
                        if button.is_hovered and i > 0:
                            button.is_hovered = False
                            self.buttons[i-1].is_hovered = True
                            break
                            
                elif event.key == pygame.K_DOWN:
                    # Find current hovered button and move down
                    for i, button in enumerate(self.buttons):
                        if button.is_hovered and i < len(self.buttons) - 1:
                            button.is_hovered = False
                            self.buttons[i+1].is_hovered = True
                            break
                            
                elif event.key == pygame.K_RETURN:
                    # Activate currently hovered button
                    for i, button in enumerate(self.buttons):
                        if button.is_hovered:
                            if i == 0:  # Resume
                                return "PLAYING"
                            elif i == 1:  # Music toggle
                                music_enabled = self.game.audio.toggle_music()
                                music_state = "On" if music_enabled else "Off"
                                self.buttons[1].text = f"Music: {music_state}"
                            elif i == 2:  # Return to menu
                                return "MENU"
                            elif i == 3:  # Quit
                                return "QUIT"
                            break
                
        return None


class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.Font(C.FONT_PATH, 32)
        self.title_font = pygame.font.Font(C.FONT_PATH, 64)
        self.stats_font = pygame.font.Font(C.FONT_PATH, 24)
        
        # Create buttons
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2
        
        self.buttons = [
            Button(button_x, 320, button_width, button_height, "Retry", self.font),
            Button(button_x, 390, button_width, button_height, "Main Menu", self.font),
            Button(button_x, 460, button_width, button_height, "Quit", self.font)
        ]
        
    def enter(self):
        self.game.log_csv(self.game.wave_number)  # Log game results
        
    def update(self, dt):
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
        
    def render(self, screen):
        # Black background
        screen.fill((0, 0, 0))
        
        # Game Over title
        title = self.title_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        
        # Stats
        wave_text = self.font.render(f"Waves Survived: {self.game.wave_number}", True, (255, 255, 255))
        screen.blit(wave_text, (screen.get_width()//2 - wave_text.get_width()//2, 180))
        
        player_text = self.font.render(f"Player: {self.game.player_name}", True, (255, 255, 255))
        screen.blit(player_text, (screen.get_width()//2 - player_text.get_width()//2, 230))
        
        # Additional stats from PlayerProfile
        high_score_text = self.stats_font.render(f"Best Score: {self.game.profile.high_score} waves", True, (200, 200, 200))
        screen.blit(high_score_text, (screen.get_width()//2 - high_score_text.get_width()//2, 270))
        
        games_text = self.stats_font.render(f"Games Played: {self.game.profile.games_played}", True, (200, 200, 200))
        screen.blit(games_text, (screen.get_width()//2 - games_text.get_width()//2, 300))
        
        # Draw buttons
        for button in self.buttons:
            button.draw(screen)
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check button clicks
                if self.buttons[0].is_clicked(mouse_pos, True):  # Retry
                    # Reinitialize player with same name
                    self.game.initialize_player()
                    return "DECK_SELECTION"
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Main Menu
                    return "MENU"
                elif self.buttons[2].is_clicked(mouse_pos, True):  # Quit
                    return "QUIT"
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "MENU"
        return None 
