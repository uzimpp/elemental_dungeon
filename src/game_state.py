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
        self.paused = False
        self.previous_state_id = None

    def add_state(self, state_id, state):
        """Add a state to the state dictionary"""
        self.states[state_id] = state

    def set_state(self, state_id):
        """Transition to a new state"""
        if self.current_state:
            for sid, s in self.states.items():
                if s == self.current_state:
                    self.previous_state_id = sid
                    break
            self.current_state.exit()

        self.current_state = self.states[state_id]
        self.current_state.enter()

    def return_to_previous_state(self):
        """Return to the previous state if available"""
        if self.previous_state_id:
            self.set_state(self.previous_state_id)

    def set_overlay(self, overlay):
        """Set an overlay and pause the game"""
        self.overlay = overlay
        self.pause()

    def clear_overlay(self):
        """Clear the overlay and resume the game"""
        self.overlay = None
        self.resume()

    def pause(self):
        """Pause the game"""
        self.paused = True
        if self.current_state and hasattr(self.current_state, 'on_pause'):
            self.current_state.on_pause()

    def resume(self):
        """Resume the game"""
        self.paused = False
        if self.current_state and hasattr(self.current_state, 'on_resume'):
            self.current_state.on_resume()

    def toggle_pause(self):
        """Toggle between paused and resumed states"""
        if self.paused:
            self.resume()
        else:
            self.pause()

    def is_paused(self):
        """Check if the game is paused"""
        return self.paused

    def update(self, dt):
        """Update the current state and overlay"""
        if self.overlay:
            overlay_result = self.overlay.update(dt)
            if overlay_result:
                if overlay_result == "CLOSE_OVERLAY":
                    self.clear_overlay()
                else:
                    self.clear_overlay()
                    self.set_state(overlay_result)
                return

        if not self.paused and self.current_state:
            result = self.current_state.update(dt)
            if result:
                self.set_state(result)

    def render(self, screen):
        """Render the current state and overlay"""
        if self.current_state:
            self.current_state.render(screen)
        if self.overlay:
            self.overlay.render(screen)

    def handle_events(self, events):
        """Handle events for the current state and overlay"""
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"  # Prioritize global quit

        overlay_took_action = False
        if self.overlay:
            result = self.overlay.handle_events(events)
            if result == "QUIT":
                return "QUIT"  # Overlay wants to quit
            elif result == "CLOSE_OVERLAY":
                self.clear_overlay()
                overlay_took_action = True  # Overlay handled event, no state change needed from it
            elif result:  # Overlay requests a state change
                self.clear_overlay()
                self.set_state(result)
                overlay_took_action = True  # Overlay handled event and changed state
            # If result is None, overlay didn't handle the specific event type, fall through

        # Only pass events to current_state if not paused AND overlay didn't take over
        if not self.paused and not overlay_took_action and self.current_state:
            result = self.current_state.handle_events(events)
            if result == "QUIT":
                return "QUIT"  # Current state wants to quit
            elif result:  # Current state requests a state change
                self.set_state(result)
                # After current_state handles an event and requests a state change,
                # we typically don't need to return anything other than None or "QUIT"

        return None  # No action taken that requires a "QUIT" or specific state return


class GameState:
    """Base class for game states"""

    def __init__(self, game):
        self.game = game
        self.ui_manager = UIManager(game.screen)

    def enter(self):
        """Called when entering this state"""
        pass

    def exit(self):
        """Called when exiting this state"""
        pass

    def update(self, dt):
        """Update state logic"""
        return None

    def render(self, screen):
        """Render the state"""
        pass

    def handle_events(self, events):
        """Handle input events"""
        return None

    def on_pause(self):
        """Called when the game is paused"""
        pass

    def on_resume(self):
        """Called when the game is resumed"""
        pass


class PauseOverlay:
    """Reusable overlay for pause menu"""

    def __init__(self, game):
        self.game = game
        self.font = Font().get_font('MENU')

        # Centered buttons for main actions
        screen_width = game.screen.get_width()
        button_width = 200
        button_height = 50
        button_x = (screen_width - button_width) // 2

        self.resume_button = Button(button_x, 250, button_width,
                                    button_height, "Resume", self.font)
        self.retry_button = Button(button_x, 320, button_width,  # Adjusted y-pos
                                   button_height, "Retry", self.font)
        self.quit_button = Button(button_x, 390, button_width,  # Adjusted y-pos
                                  button_height, "Quit to Menu", self.font)  # Clarified text

        # Music Toggle Button (Icon-based)
        music_icon_text = "🔊" if self.game.audio.music_enabled else "🔇"
        self.music_button = Button(
            C.WIDTH - 60, C.HEIGHT - 60, 50, 50,
            music_icon_text,
            self.font,  # Re-use menu font, consider a dedicated icon font/size later
            draw_background=False  # Added for icon button
        )

        # Store buttons in a list for easier iteration in update/render
        # but handle clicks individually for clarity if actions are very different.
        self.buttons = [self.resume_button, self.retry_button,
                        self.quit_button, self.music_button]

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)  # Make sure Button.update is called
        return None

    def render(self, screen):
        overlay_surface = pygame.Surface(
            (screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay_surface.fill((0, 0, 0, 128))
        screen.blit(overlay_surface, (0, 0))

        title = self.font.render("PAUSED", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 180))

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

                if self.resume_button.is_clicked(mouse_pos, True):
                    return "CLOSE_OVERLAY"
                elif self.retry_button.is_clicked(mouse_pos, True):
                    self.game.reset_game()
                    # This should transition to Deck Selection to allow re-picking skills,
                    # or directly to PlayingState if keeping the same deck.
                    # For now, let's go to Deck Selection as per original logic.
                    return "DECK_SELECTION"
                elif self.quit_button.is_clicked(mouse_pos, True):
                    self.game.reset_game()  # Reset game state before going to menu
                    return "MENU"
                elif self.music_button.is_clicked(mouse_pos, True):
                    print(f"[DEBUG] Music button clicked in PauseOverlay.")
                    print(
                        f"[DEBUG] Before toggle - self.game.audio.music_enabled: {self.game.audio.music_enabled}")
                    music_enabled_after_toggle = self.game.audio.toggle_music()
                    print(
                        f"[DEBUG] After toggle - self.game.audio.toggle_music() returned: {music_enabled_after_toggle}")
                    print(
                        f"[DEBUG] After toggle - self.game.audio.music_enabled: {self.game.audio.music_enabled}")
                    self.music_button.set_text(
                        "🔊" if music_enabled_after_toggle else "🔇")
                    print(
                        f"[DEBUG] Music button text set to: {self.music_button.text}")
                    # Event handled, no further action for this click
                    return None
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
            Button(button_x, 350, button_width,
                   button_height, "Try Again", self.font),
            Button(button_x, 420, button_width,
                   button_height, "Main Menu", self.font),
            Button(button_x, 490, button_width,
                   button_height, "Quit", self.font)
        ]

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
        return None

    def render(self, screen):
        # Semi-transparent overlay
        overlay = pygame.Surface(
            (screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 192))  # Darker overlay for game over
        screen.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("GAME OVER", True, (255, 50, 50))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 150))

        # Stats
        wave_text = self.font.render(
            f"Waves Survived: {self.game.wave_number}", True, (255, 255, 255))
        screen.blit(wave_text, (screen.get_width() //
                    2 - wave_text.get_width()//2, 230))

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
                    self.game.reset_game()
                    return "DECK_SELECTION"
                elif self.buttons[1].is_clicked(mouse_pos, True):  # Main Menu
                    self.game.reset_game()
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

        start_button = Button(button_x, 250, button_width,
                              button_height, "Start", self.menu_font)
        # Adjust y-pos for Stats button
        stats_button = Button(button_x, 320, button_width,
                              button_height, "Stats", self.menu_font)
        quit_button = Button(button_x, 390, button_width,  # Adjusted y-pos
                             button_height, "Quit", self.menu_font)

        self.ui_manager.add_element(start_button, "buttons")
        self.ui_manager.add_element(
            stats_button, "buttons")  # Add Stats button
        self.ui_manager.add_element(quit_button, "buttons")

        # Music Toggle Button
        music_icon_text = "🔊" if self.game.audio.music_enabled else "🔇"
        # Position bottom-right
        self.music_button = Button(
            C.WIDTH - 60, C.HEIGHT - 60, 50, 50,
            music_icon_text,
            self.menu_font,  # Use a suitable font, maybe a larger one for icons
            draw_background=False  # Added for icon button
        )
        self.ui_manager.add_element(
            self.music_button, "persistent_ui")  # New group

    def enter(self):
        """Called when entering this state."""
        if self.game.audio.current_music != "MENU":
            if self.game.audio.current_music is not None:
                self.game.audio.fade_out(500)
            self.game.audio.play_music("MENU")
        self.game.audio.set_music_volume(self.game.audio.music_volume)
        # Update music button icon on entering state
        self.music_button.set_text(
            "🔊" if self.game.audio.music_enabled else "🔇")
        super().enter()  # Call base class enter if it has any logic

    def exit(self):
        """Called when exiting this state."""
        super().exit()  # Call base class exit

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)  # Updates all groups
        return None

    def render(self, screen):
        screen.fill((50, 50, 100))
        title = self.title_font.render("INCANTATO", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 100))
        if self.game.player_name:
            player_text = self.info_font.render(
                f"Player: {self.game.player_name}", True, (200, 200, 200))
            screen.blit(player_text, (screen.get_width() //
                        2 - player_text.get_width()//2, 170))
        self.ui_manager.draw_all()  # Draws all groups

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                # Handle persistent UI (music button)
                if self.music_button.is_clicked(mouse_pos, True):
                    music_enabled = self.game.audio.toggle_music()
                    self.music_button.set_text("🔊" if music_enabled else "🔇")
                    return None  # Event handled

                # Handle other menu buttons
                buttons = self.ui_manager.elements.get("buttons", [])
                for i, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos, True):
                        if button.text == "Start":  # Check by text for clarity
                            if self.game.player_name is None:
                                return "NAME_ENTRY"
                            else:
                                return "DECK_SELECTION"
                        elif button.text == "Stats":  # Stats button action
                            return "STATS_DISPLAY"  # Transition to a new stats state
                        elif button.text == "Quit":  # Quit
                            return "QUIT"
        return None


class StatsDisplayState(GameState):
    """Placeholder state for displaying stats (simulating Tkinter window)"""

    def __init__(self, game):
        super().__init__(game)
        self.title_font = Font().get_font('TITLE')
        self.info_font = Font().get_font('MENU')
        self.message_font = Font().get_font('UI')

        close_button = Button(
            C.WIDTH // 2 - 100, C.HEIGHT - 100, 200, 50,
            "Close Stats", self.info_font
        )
        self.ui_manager.add_element(close_button, "buttons")

    def enter(self):
        # Pause current game state if coming from PlayingState via an overlay chain
        # For Menu -> Stats, GameStateManager.pause() isn't strictly needed
        # as MenuState doesn't have ongoing game logic to pause.
        # However, consistent pausing behavior might be good.
        # self.game.state_manager.pause() # This would pause MenuState if called.
        # For now, this state itself being active is the 'pause'.
        pass

    def exit(self):
        # self.game.state_manager.resume() # If we paused, we should resume.
        pass

    def update(self, dt):
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)
        return None

    def render(self, screen):
        screen.fill((30, 30, 30))  # Dark background

        title_text = self.title_font.render("Game Statistics", True, C.WHITE)
        title_rect = title_text.get_rect(center=(C.WIDTH // 2, 100))
        screen.blit(title_text, title_rect)

        message_text = self.message_font.render(
            "(Stats display would appear here - simulating Tkinter window)",
            True, C.LIGHT_GREY
        )
        message_rect = message_text.get_rect(
            center=(C.WIDTH // 2, C.HEIGHT // 2 - 50))
        screen.blit(message_text, message_rect)

        # You would fetch and display actual stats here
        # e.g., from self.game.data_collection or similar

        self.ui_manager.draw_all()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "MENU"  # Return to MenuState

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                buttons = self.ui_manager.elements.get("buttons", [])
                for button in buttons:
                    if button.is_clicked(mouse_pos, True):
                        if button.text == "Close Stats":
                            return "MENU"  # Return to MenuState
        return None

# Ensure to add this new state to the GameStateManager in main.py
# game_state_manager.add_state("STATS_DISPLAY", StatsDisplayState(game))


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
        screen.blit(text_surface, (self.input_rect.x +
                    10, self.input_rect.y + 10))

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
        self.icon_font = Font().get_font('SKILL')  # Used for icons
        self.instruction_font = Font().get_font('UI')  # For instruction text

        self.skill_data = []
        self.selected_skill_data = []
        self.scroll_offset = 0
        self.selected_index = 0

        screen_width = game.screen.get_width()
        screen_height = game.screen.get_height()

        # Skill list properties (defined here for use by scroll buttons)
        self.list_width_ratio = 0.6
        self.list_width = screen_width * self.list_width_ratio
        self.list_x = (screen_width - self.list_width) // 2
        self.list_y = 80
        self.list_height = 400  # Height of the scrollable list area

        back_button = Button(10, 60, 100, 40, "Back", self.desc_font)
        self.ui_manager.add_element(back_button, "navigation")

        confirm_button = Button((screen_width - 200) //
                                2, 650, 200, 50, "Confirm", self.skill_font)
        self.ui_manager.add_element(confirm_button, "navigation")

        # Position scroll buttons to the right of the skill list
        scroll_button_x = self.list_x + self.list_width + 10
        up_button = Button(scroll_button_x, self.list_y,
                           40, 40, "▲", self.skill_font, draw_background=False)
        down_button = Button(scroll_button_x, self.list_y + self.list_height - 40,
                             40, 40, "▼", self.skill_font, draw_background=False)
        self.ui_manager.add_element(up_button, "scroll")
        self.ui_manager.add_element(down_button, "scroll")

        music_icon_text = "🔊" if self.game.audio.music_enabled else "🔇"
        self.music_button = Button(
            C.WIDTH - 60, C.HEIGHT - 60, 50, 50, music_icon_text, self.icon_font,
            draw_background=False  # Added for icon button
        )
        self.ui_manager.add_element(self.music_button, "persistent_ui")

        self.hamburger_button = Button(
            10, 10, 40, 40, "☰", self.icon_font, draw_background=False)  # Added for icon button
        self.ui_manager.add_element(self.hamburger_button, "overlay_triggers")

        self.element_colors = {k: v['primary']
                               for k, v in C.ELEMENT_COLORS.items()}

    def enter(self):
        self.skill_data = self.load_skill_data()
        self.selected_skill_data = []
        self.scroll_offset = 0
        self.selected_index = 0
        if self.music_button:
            self.music_button.set_text(
                "🔊" if self.game.audio.music_enabled else "🔇")
        super().enter()

    def load_skill_data(self):
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
        screen.fill((40, 40, 80))
        title = self.title_font.render(
            f"BUILD YOUR DECK (Pick {C.SKILLS_LIMIT})", True, (255, 255, 255))
        screen.blit(title, (screen.get_width()//2 - title.get_width()//2, 30))
        self.draw_skill_list(screen)
        UI.draw_selected_skills(
            screen, self.selected_skill_data)  # Draws at y=500
        self.ui_manager.draw_all()

        # Draw instruction text
        instructions = [
            "Controls:",
            "- Click skill in list to select.",
            "- Click selected skill at bottom to remove.",
            "- Arrow keys or ▲▼ to scroll/highlight.",
            "- Enter/Return to select highlighted skill.",
            "- Backspace to remove last selected skill.",
            f"- Confirm or Space when {C.SKILLS_LIMIT} skills chosen."
        ]
        # Below selected skills area (y=500, height=80)
        instr_y_start = 500 + 80 + 20
        for i, line in enumerate(instructions):
            instr_text = self.instruction_font.render(line, True, C.LIGHT_GREY)
            # Center instructions or align left under the list
            instr_rect = instr_text.get_rect(
                centerx=screen.get_width() // 2, y=instr_y_start + i * 22)
            # screen.blit(instr_text, (self.list_x, instr_y_start + i * 22))
            screen.blit(instr_text, instr_rect)

    def draw_skill_list(self, screen):
        # Use self.list_x, self.list_y, etc. defined in __init__
        pygame.draw.rect(screen, (30, 30, 60),
                         (self.list_x, self.list_y, self.list_width, self.list_height))
        pygame.draw.rect(screen, (100, 100, 150),
                         (self.list_x, self.list_y, self.list_width, self.list_height), 2)

        scrollbar_x = self.list_x + self.list_width - 15
        if len(self.skill_data) > self.SKILLS_PER_PAGE:
            scrollbar_height_ratio = min(
                1.0, self.SKILLS_PER_PAGE / len(self.skill_data))
            actual_scrollbar_height = self.list_height * scrollbar_height_ratio
            max_scroll_offset = len(self.skill_data) - self.SKILLS_PER_PAGE
            current_scroll_ratio = 0
            if max_scroll_offset > 0:
                current_scroll_ratio = self.scroll_offset / max_scroll_offset
            scrollbar_pos_y = self.list_y + \
                (self.list_height - actual_scrollbar_height) * current_scroll_ratio
            pygame.draw.rect(screen, (150, 150, 180), (scrollbar_x,
                             scrollbar_pos_y, 10, actual_scrollbar_height))

        visible_skills = self.skill_data[self.scroll_offset:
                                         self.scroll_offset + self.SKILLS_PER_PAGE]
        for i, skill in enumerate(visible_skills):
            is_chosen = skill in self.selected_skill_data
            # Use self.list_x for positioning skill text
            skill_y_pos = self.list_y + 10 + i * \
                (self.list_height // self.SKILLS_PER_PAGE)
            skill_rect = pygame.Rect(
                # Use self.list_width, -25 for scrollbar space
                self.list_x + 5, skill_y_pos - 5, self.list_width - 25, 70)
            if i + self.scroll_offset == self.selected_index:
                pygame.draw.rect(screen, (60, 60, 100), skill_rect)
            element = skill["element"].upper()
            element_color = self.element_colors.get(element, (255, 255, 255))
            skill_text_render = self.skill_font.render(
                f"[{element}] {skill['name']}", True, (150, 150, 150) if is_chosen else element_color)
            screen.blit(skill_text_render, (self.list_x + 15, skill_y_pos))
            cd_text = self.desc_font.render(
                f"Cooldown: {float(skill['cooldown']):.1f}s | Type: {skill['skill_type']}", True, (200, 200, 200))
            screen.blit(cd_text, (self.list_x + 15, skill_y_pos + 30))
            desc = skill["description"]
            if len(desc) > 60:
                desc = desc[:57] + "..."
            desc_text = self.desc_font.render(desc, True, (200, 200, 200))
            screen.blit(desc_text, (self.list_x + 15, skill_y_pos + 50))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if self.hamburger_button and self.hamburger_button.is_clicked(mouse_pos, True):
                    self.game.state_manager.set_overlay(
                        PauseOverlay(self.game))
                    return None

                if self.music_button and self.music_button.is_clicked(mouse_pos, True):
                    music_enabled = self.game.audio.toggle_music()
                    self.music_button.set_text("🔊" if music_enabled else "🔇")
                    return None

                navigation_buttons = self.ui_manager.elements.get(
                    "navigation", [])
                for i, button in enumerate(navigation_buttons):
                    if button.is_clicked(mouse_pos, True):
                        if i == 0:  # Back button
                            return "MENU"
                        elif i == 1:  # Confirm button
                            if len(self.selected_skill_data) == C.SKILLS_LIMIT:
                                self.create_player_deck()
                                self.game.prepare_game()
                                return "PLAYING"
                scroll_buttons = self.ui_manager.elements.get("scroll", [])
                for i, button in enumerate(scroll_buttons):
                    if button.is_clicked(mouse_pos, True):
                        if i == 0 and self.scroll_offset > 0:  # Up button
                            self.scroll_offset -= 1
                        # Down button
                        elif i == 1 and self.scroll_offset < len(self.skill_data) - self.SKILLS_PER_PAGE:
                            self.scroll_offset += 1

                # Use instance attributes for list dimensions in click detection
                if (self.list_x <= mouse_pos[0] <= self.list_x + self.list_width and
                        self.list_y <= mouse_pos[1] <= self.list_y + self.list_height):
                    skill_height_in_list = self.list_height // self.SKILLS_PER_PAGE
                    clicked_idx_in_view = (
                        mouse_pos[1] - self.list_y) // skill_height_in_list
                    if 0 <= clicked_idx_in_view < min(self.SKILLS_PER_PAGE, len(self.skill_data) - self.scroll_offset):
                        abs_index = self.scroll_offset + clicked_idx_in_view
                        self.selected_index = abs_index
                        selected = self.skill_data[self.selected_index]
                        if selected not in self.selected_skill_data and len(self.selected_skill_data) < C.SKILLS_LIMIT:
                            self.selected_skill_data.append(selected)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    if self.selected_index < self.scroll_offset:
                        self.scroll_offset = self.selected_index
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(
                        len(self.skill_data) - 1, self.selected_index + 1)
                    if self.selected_index >= self.scroll_offset + self.SKILLS_PER_PAGE:
                        self.scroll_offset = self.selected_index - self.SKILLS_PER_PAGE + 1
                elif event.key == pygame.K_RETURN:
                    if self.selected_index < len(self.skill_data):
                        selected = self.skill_data[self.selected_index]
                        if selected not in self.selected_skill_data and len(self.selected_skill_data) < C.SKILLS_LIMIT:
                            self.selected_skill_data.append(selected)
                elif event.key == pygame.K_BACKSPACE:
                    if self.selected_skill_data:
                        self.selected_skill_data.pop()
                elif event.key == pygame.K_SPACE:
                    if len(self.selected_skill_data) == C.SKILLS_LIMIT:
                        self.create_player_deck()
                        self.game.prepare_game()
                        return "PLAYING"
                elif event.key == pygame.K_ESCAPE:
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
        self.paused = False  # Internal pause flag, distinct from GameStateManager.paused
        # General font for UI text in this state
        self.ui_font = Font().get_font('MENU')
        # Potentially larger for icons like hamburger
        self.icon_font = Font().get_font('SKILL')
        self.music_button = None
        self.hamburger_button = None  # Initialize hamburger_button

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
        if self.game.audio.current_music != "PLAYING":
            if self.game.audio.current_music is not None:  # Fade out previous if any
                self.game.audio.fade_out(500)
            self.game.audio.fade_in("PLAYING", 1000)
        if self.music_button:
            self.music_button.set_text(
                "🔊" if self.game.audio.music_enabled else "🔇")
        super().enter()

    def exit(self):
        """Clean up when leaving state"""
        super().exit()

    def setup_ui(self):
        """Set up UI elements for gameplay"""
        self.ui_manager.clear_group("status")
        self.ui_manager.clear_group("skills")
        self.ui_manager.clear_group("buttons")
        self.ui_manager.clear_group("persistent_ui")
        # New group for hamburger
        self.ui_manager.clear_group("overlay_triggers")

        hp_bar = ProgressBar(10, 50, 200, 20, self.game.player.max_health,
                             bg_color=C.UI_COLORS['hp_bar_bg'],
                             fill_color=C.UI_COLORS['hp_bar_fill'],
                             text_color=C.UI_COLORS['hp_text'],
                             font=Font().get_font('UI'),
                             label="HP")
        self.ui_manager.add_element(hp_bar, "status")

        stamina_bar = ProgressBar(10, 80, 200, 20, self.game.player.max_stamina,
                                  bg_color=C.UI_COLORS['stamina_bar_bg'],
                                  fill_color=C.UI_COLORS['stamina_bar_fill'],
                                  text_color=C.UI_COLORS['stamina_text'],
                                  font=Font().get_font('UI'),
                                  label="Stamina")
        self.ui_manager.add_element(stamina_bar, "status")

        skill_font_ui = Font().get_font('UI')  # Corrected font variable name
        for i, skill in enumerate(self.game.player.deck.skills):
            skill_display = SkillDisplay(
                10 + i * 110, C.HEIGHT - 100, 100, 80, skill, skill_font_ui, hotkey=str(i+1))
            self.ui_manager.add_element(skill_display, "skills")

        music_icon_text = "🔊" if self.game.audio.music_enabled else "🔇"
        self.music_button = Button(
            C.WIDTH - 60, C.HEIGHT - 60, 50, 50, music_icon_text, self.icon_font,
            draw_background=False  # Added for icon button
        )
        self.ui_manager.add_element(self.music_button, "persistent_ui")

        # Hamburger Menu Button
        self.hamburger_button = Button(
            10, 10, 40, 40, "☰", self.icon_font, draw_background=False)  # Added for icon button
        self.ui_manager.add_element(self.hamburger_button, "overlay_triggers")

    def on_pause(self):
        """Called when game is paused by GameStateManager (e.g. overlay shown)"""
        self.paused = True

    def on_resume(self):
        """Called when game is resumed by GameStateManager"""
        self.paused = False

    def update(self, dt):
        if not hasattr(self.game, 'player') or not self.game.player:
            return None
        if not self.paused and not self.game.state_manager.is_paused():
            self.game.enemy_group.update(self.game.player, dt)
            self.game.player.handle_input(dt)
            self.game.player.deck.update(dt, self.game.enemies)
            self.game.check_collisions()
            if len(self.game.enemy_group) == 0:
                self.game.wave_number += 1
                self.game.spawn_wave()
            if self.game.player.health <= 0:
                DataCollection.log_csv(self.game, self.game.wave_number)
                self.game.state_manager.set_overlay(GameOverOverlay(self.game))
        self.update_ui(dt)
        return None

    def update_ui(self, dt):
        """Update UI elements (always happens even when paused)"""
        status_elements = self.ui_manager.elements.get("status", [])
        if len(status_elements) >= 1 and self.game.player:
            status_elements[0].set_value(self.game.player.health)
        if len(status_elements) >= 2 and self.game.player:
            status_elements[1].set_value(self.game.player.stamina)
        now = time.time()
        skill_elements = self.ui_manager.elements.get("skills", [])
        for skill_display in skill_elements:
            skill_display.update_cooldown(now)
        mouse_pos = pygame.mouse.get_pos()
        self.ui_manager.update_all(mouse_pos, dt)

    def render(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill((200, 220, 255))
        wave_text = self.ui_font.render(
            f"WAVE: {self.game.wave_number}", True, C.BLACK)
        # This will be overlapped by hamburger; adjust hamburger y or this y
        screen.blit(wave_text, (10, 10))
        for enemy in self.game.enemy_group:
            enemy.draw(screen)
        if hasattr(self.game, 'player') and self.game.player:
            self.game.player.draw(screen)
            if hasattr(self.game.player, 'deck'):
                self.game.player.deck.draw(screen)
        self.ui_manager.draw_all()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Hamburger click
                if self.hamburger_button and self.hamburger_button.is_clicked(mouse_pos, True):
                    self.game.state_manager.set_overlay(
                        PauseOverlay(self.game))
                    return None  # Event handled
                # Music button click
                if self.music_button and self.music_button.is_clicked(mouse_pos, True):
                    music_enabled = self.game.audio.toggle_music()
                    self.music_button.set_text("🔊" if music_enabled else "🔇")
                    return None  # Event handled

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Escape also opens pause menu
                    self.game.state_manager.set_overlay(
                        PauseOverlay(self.game))
                    return None
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol - 0.1)
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    current_vol = self.game.audio.music_volume
                    self.game.audio.set_music_volume(current_vol + 0.1)
                elif event.key == pygame.K_m:
                    music_enabled = self.game.audio.toggle_music()
                    if self.music_button:
                        self.music_button.set_text(
                            "🔊" if music_enabled else "🔇")
                elif event.key == pygame.K_p:
                    self.game.state_manager.toggle_pause()

            if not self.game.state_manager.is_paused() and hasattr(self.game, 'player') and self.game.player:
                mouse_pos = pygame.mouse.get_pos()
                now = time.time()
                result = self.game.player.handle_event(
                    event, mouse_pos, self.game.enemies, now)
                if result == 'exit':
                    return "MENU"
        return None
