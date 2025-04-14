# ui.py
import pygame
from config import WIDTH, HEIGHT, UI_COLORS

class UIComponent:
    """Base class for all UI components"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.active = True  # For input handling
    
    def update(self, dt):
        """Update component state"""
        pass
    
    def draw(self, surface):
        """Draw the component"""
        pass
    
    def handle_event(self, event):
        """Handle pygame events"""
        return False  # Return True if event was handled
    
    def contains_point(self, point):
        """Check if the point is within this component"""
        x, y = point
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)


class Button(UIComponent):
    """Interactive button component"""
    def __init__(self, x, y, width, height, text, callback, 
                 text_color=(255, 255, 255), 
                 bg_color=(80, 80, 80),
                 hover_color=(100, 100, 100),
                 font_size=24):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.current_color = bg_color
        self.font = pygame.font.SysFont("Arial", font_size)
        self.hovered = False
        
        # Pre-render text
        self.text_surface = self.font.render(text, True, text_color)
        self.text_x = self.x + (self.width - self.text_surface.get_width()) // 2
        self.text_y = self.y + (self.height - self.text_surface.get_height()) // 2
    
    def update(self, dt):
        # Update hover state
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.hovered = self.contains_point((mouse_x, mouse_y))
        self.current_color = self.hover_color if self.hovered else self.bg_color
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw button background
        pygame.draw.rect(surface, self.current_color, 
                         (self.x, self.y, self.width, self.height))
        
        # Draw button border
        pygame.draw.rect(surface, (200, 200, 200), 
                         (self.x, self.y, self.width, self.height), 2)
        
        # Draw text
        surface.blit(self.text_surface, (self.text_x, self.text_y))
    
    def handle_event(self, event):
        if not self.active or not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.contains_point(event.pos):
                    self.callback()
                    return True
        return False


class Panel(UIComponent):
    """Container for other UI components"""
    def __init__(self, x, y, width, height, bg_color=(50, 50, 50, 180)):
        super().__init__(x, y, width, height)
        self.bg_color = bg_color
        self.components = []
    
    def add_component(self, component):
        """Add a UI component to this panel"""
        self.components.append(component)
    
    def update(self, dt):
        for component in self.components:
            component.update(dt)
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Create semi-transparent surface for panel background
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_surface.fill(self.bg_color)
        surface.blit(panel_surface, (self.x, self.y))
        
        # Draw child components
        for component in self.components:
            component.draw(surface)
    
    def handle_event(self, event):
        if not self.active or not self.visible:
            return False
            
        # Pass event to child components
        handled = False
        for component in self.components:
            if component.handle_event(event):
                handled = True
                break
        return handled


class SkillSlot(UIComponent):
    """UI element for displaying a skill and its cooldown"""
    def __init__(self, x, y, size, skill, index, hotkey=None):
        super().__init__(x, y, size, size)
        self.skill = skill
        self.size = size
        self.index = index
        self.hotkey = hotkey
        self.font = pygame.font.SysFont("Arial", 14)
        
        # Pre-render hotkey text
        if hotkey:
            self.hotkey_text = self.font.render(hotkey, True, (255, 255, 255))
    
    def update(self, dt, current_time):
        # Nothing to update
        pass
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw skill box background
        pygame.draw.rect(surface, UI_COLORS['skill_box_bg'], 
                         (self.x, self.y, self.size, self.size))
        
        # Draw skill border
        pygame.draw.rect(surface, self.skill.color, 
                         (self.x, self.y, self.size, self.size), 2)
        
        # Draw skill name
        name_text = self.font.render(self.skill.name[:8], True, UI_COLORS['skill_text'])
        surface.blit(name_text, (self.x + 5, self.y + 5))
        
        # Draw hotkey
        if hasattr(self, 'hotkey_text'):
            surface.blit(self.hotkey_text, 
                         (self.x + self.size - 15, self.y + self.size - 20))
        
        # Draw cooldown overlay
        current_time = pygame.time.get_ticks() / 1000.0
        time_since_use = current_time - self.skill.last_use_time
        if time_since_use < self.skill.cooldown:
            # Calculate cooldown percentage
            cooldown_pct = time_since_use / self.skill.cooldown
            remaining_height = int(self.size * (1 - cooldown_pct))
            
            # Draw semi-transparent overlay
            cooldown_overlay = pygame.Surface((self.size, remaining_height), pygame.SRCALPHA)
            cooldown_overlay.fill(UI_COLORS['cooldown_overlay'])
            surface.blit(cooldown_overlay, (self.x, self.y))
            
            # Draw cooldown text
            time_left = max(0, self.skill.cooldown - time_since_use)
            cooldown_text = self.font.render(f"{time_left:.1f}", True, (255, 255, 255))
            surface.blit(cooldown_text, 
                         (self.x + (self.size - cooldown_text.get_width()) // 2, 
                          self.y + (self.size - cooldown_text.get_height()) // 2))


class HealthBar(UIComponent):
    """UI component for displaying health"""
    def __init__(self, x, y, width, height, entity, label="HP"):
        super().__init__(x, y, width, height)
        self.entity = entity
        self.label = label
        self.font = pygame.font.SysFont("Arial", 16)
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, UI_COLORS['hp_bar_bg'], 
                         (self.x, self.y, self.width, self.height))
        
        # Calculate fill width based on health percentage
        fill_width = int(self.width * (self.entity.health / self.entity.max_health))
        
        # Draw fill
        pygame.draw.rect(surface, UI_COLORS['hp_bar_fill'], 
                         (self.x, self.y, fill_width, self.height))
        
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), 
                         (self.x, self.y, self.width, self.height), 1)
        
        # Draw text
        text = f"{self.label}: {int(self.entity.health)}/{int(self.entity.max_health)}"
        text_surface = self.font.render(text, True, UI_COLORS['hp_text'])
        surface.blit(text_surface, 
                    (self.x + 5, self.y + (self.height - text_surface.get_height()) // 2))


class StaminaBar(UIComponent):
    """UI component for displaying stamina"""
    def __init__(self, x, y, width, height, player):
        super().__init__(x, y, width, height)
        self.player = player
        self.font = pygame.font.SysFont("Arial", 16)
    
    def draw(self, surface):
        if not self.visible:
            return
            
        # Draw background
        pygame.draw.rect(surface, UI_COLORS['stamina_bar_bg'], 
                         (self.x, self.y, self.width, self.height))
        
        # Calculate fill width based on stamina percentage
        fill_width = int(self.width * (self.player.stamina / self.player.max_stamina))
        
        # Draw fill
        pygame.draw.rect(surface, UI_COLORS['stamina_bar_fill'], 
                         (self.x, self.y, fill_width, self.height))
        
        # Draw border
        pygame.draw.rect(surface, (200, 200, 200), 
                         (self.x, self.y, self.width, self.height), 1)
        
        # Draw text
        text = f"SP: {int(self.player.stamina)}/{int(self.player.max_stamina)}"
        text_surface = self.font.render(text, True, UI_COLORS['stamina_text'])
        surface.blit(text_surface, 
                    (self.x + 5, self.y + (self.height - text_surface.get_height()) // 2))


class BarGraph(UIComponent):
    """Bar graph for data visualization"""
    def __init__(self, x, y, width, height, data, title="", max_value=None):
        super().__init__(x, y, width, height)
        self.data = data  # List of (label, value) tuples
        self.title = title
        self.max_value = max_value
        self.font = pygame.font.SysFont("Arial", 14)
        self.title_font = pygame.font.SysFont("Arial", 20)
    
    def draw(self, surface):
        if not self.visible:
            return
        
        # Draw background and border
        pygame.draw.rect(surface, (240, 240, 240), 
                         (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (0, 0, 0), 
                         (self.x, self.y, self.width, self.height), 2)
        
        # Draw title
        if self.title:
            title_surf = self.title_font.render(self.title, True, (0, 0, 0))
            surface.blit(title_surf, 
                        (self.x + (self.width - title_surf.get_width()) // 2, 
                         self.y + 10))
        
        # Calculate bar dimensions
        if not self.data:
            return
            
        # Find maximum value if not provided
        max_val = self.max_value if self.max_value is not None else max(v for _, v in self.data)
        if max_val == 0:
            max_val = 1  # Avoid division by zero
        
        margin = 40
        bar_area_height = self.height - margin * 2
        bar_width = min(50, (self.width - margin * 2) // len(self.data))
        bar_spacing = (self.width - margin * 2 - bar_width * len(self.data)) // max(1, len(self.data) - 1)
        
        # Draw bars
        for i, (label, value) in enumerate(self.data):
            # Calculate bar height based on value
            bar_height = (value / max_val) * bar_area_height
            
            # Calculate bar position
            bar_x = self.x + margin + i * (bar_width + bar_spacing)
            bar_y = self.y + self.height - margin - bar_height
            
            # Draw bar
            pygame.draw.rect(surface, (50, 150, 200), 
                             (bar_x, bar_y, bar_width, bar_height))
            
            # Draw label
            label_surf = self.font.render(label, True, (0, 0, 0))
            label_x = bar_x + (bar_width - label_surf.get_width()) // 2
            label_y = self.y + self.height - margin + 5
            surface.blit(label_surf, (label_x, label_y))
            
            # Draw value
            value_surf = self.font.render(str(value), True, (0, 0, 0))
            value_x = bar_x + (bar_width - value_surf.get_width()) // 2
            value_y = bar_y - value_surf.get_height() - 5
            surface.blit(value_surf, (value_x, value_y))


class UIManager:
    """Manages all UI elements"""
    def __init__(self):
        self.components = []
    
    def add_component(self, component):
        """Add a UI component"""
        self.components.append(component)
    
    def update(self, dt):
        """Update all UI components"""
        for component in self.components:
            component.update(dt)
    
    def draw(self, surface):
        """Draw all UI components"""
        for component in self.components:
            component.draw(surface)
    
    def handle_event(self, event):
        """Handle events for all UI components"""
        for component in self.components:
            if component.handle_event(event):
                return True
        return False
    
    def clear(self):
        """Remove all UI components"""
        self.components.clear()
    
    def create_gameplay_ui(self, player):
        """Create UI for gameplay screen"""
        self.clear()
        
        # Add health bar
        health_bar = HealthBar(10, HEIGHT - 80, 200, 30, player)
        self.add_component(health_bar)
        
        # Add stamina bar
        stamina_bar = StaminaBar(10, HEIGHT - 40, 200, 30, player)
        self.add_component(stamina_bar)
        
        # Add skill slots
        skill_size = 60
        skill_spacing = 10
        skills_x = WIDTH - (skill_size * 4 + skill_spacing * 3) - 20
        skills_y = HEIGHT - skill_size - 20
        
        for i, skill in enumerate(player.deck):
            hotkey = str(i + 1)
            skill_slot = SkillSlot(
                skills_x + i * (skill_size + skill_spacing),
                skills_y,
                skill_size,
                skill,
                i,
                hotkey
            )
            self.add_component(skill_slot)
        
        return self
    
    def create_menu_ui(self, start_game_callback, exit_game_callback):
        """Create UI for menu screen"""
        self.clear()
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_x = (WIDTH - button_width) // 2
        
        start_button = Button(
            button_x,
            300,
            button_width,
            button_height,
            "New Game",
            start_game_callback
        )
        
        exit_button = Button(
            button_x,
            360,
            button_width,
            button_height,
            "Exit",
            exit_game_callback
        )
        
        self.add_component(start_button)
        self.add_component(exit_button)
        
        return self
    
    def create_pause_ui(self, resume_callback, exit_callback):
        """Create UI for pause screen"""
        self.clear()
        
        # Create semi-transparent panel
        panel = Panel(
            WIDTH // 4,
            HEIGHT // 4,
            WIDTH // 2,
            HEIGHT // 2
        )
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_x = (WIDTH - button_width) // 2
        
        resume_button = Button(
            button_x,
            HEIGHT // 2 - 30,
            button_width,
            button_height,
            "Resume",
            resume_callback
        )
        
        exit_button = Button(
            button_x,
            HEIGHT // 2 + 30,
            button_width,
            button_height,
            "Exit",
            exit_callback
        )
        
        panel.add_component(resume_button)
        panel.add_component(exit_button)
        self.add_component(panel)
        
        return self
    
    def create_game_over_ui(self, restart_callback, exit_callback, wave_number):
        """Create UI for game over screen"""
        self.clear()
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_x = (WIDTH - button_width) // 2
        
        restart_button = Button(
            button_x,
            HEIGHT // 2 + 50,
            button_width,
            button_height,
            "Main Menu",
            restart_callback
        )
        
        exit_button = Button(
            button_x,
            HEIGHT // 2 + 110,
            button_width,
            button_height,
            "Exit",
            exit_callback
        )
        
        self.add_component(restart_button)
        self.add_component(exit_button)
        
        return self
    
    def create_statistics_ui(self, wave_data, skill_data, callback_to_menu):
        """Create UI for statistics screen"""
        self.clear()
        
        # Create skill usage graph
        skill_graph = BarGraph(
            50, 100, WIDTH - 100, 200,
            skill_data,
            "Skill Usage"
        )
        
        # Create wave statistics graph
        wave_graph = BarGraph(
            50, 350, WIDTH - 100, 200,
            wave_data,
            "Waves Survived"
        )
        
        # Create back button
        back_button = Button(
            WIDTH // 2 - 100, 
            HEIGHT - 70,
            200, 50,
            "Back to Menu",
            callback_to_menu
        )
        
        self.add_component(skill_graph)
        self.add_component(wave_graph)
        self.add_component(back_button)
        
        return self