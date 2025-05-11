import pygame
import time
from config import Config as C
from font import Font

class UIElement(pygame.sprite.Sprite):
    """Base class for all UI elements"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.is_hovered = False
        self.is_active = False
        
    def update(self, mouse_pos=None, dt=0):
        """Update element state based on mouse position"""
        if mouse_pos:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        
    def draw(self, screen):
        """Draw the UI element"""
        screen.blit(self.image, self.rect)
        
    def is_clicked(self, mouse_pos, mouse_click):
        """Check if element was clicked"""
        return self.rect.collidepoint(mouse_pos) and mouse_click
        
    def set_active(self, active):
        """Set whether this element is active"""
        self.is_active = active


class Button(UIElement):
    """Button UI element with text"""
    def __init__(self, x, y, width, height, text, font, 
                 color=(255, 255, 255), hover_color=(255, 255, 0),
                 bg_color=(30, 30, 60), border_color=(100, 100, 150)):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.on_click = None  # Callback function to be called when button is clicked
        self._render()
        
    def _render(self):
        """Render the button to its image surface"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw button background
        pygame.draw.rect(self.image, self.bg_color, (0, 0, self.rect.width, self.rect.height))
        pygame.draw.rect(self.image, self.border_color, (0, 0, self.rect.width, self.rect.height), 2)
        
        # Render text
        text_color = self.hover_color if self.is_hovered else self.color
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.rect.width//2, self.rect.height//2))
        self.image.blit(text_surf, text_rect)
        
    def update(self, mouse_pos=None, dt=0):
        """Update button state and appearance"""
        was_hovered = self.is_hovered
        super().update(mouse_pos, dt)
        
        # Only re-render if hover state changed
        if was_hovered != self.is_hovered:
            self._render()
    
    def set_text(self, text):
        """Change the button text"""
        self.text = text
        self._render()


class ProgressBar(UIElement):
    """Progress bar UI element (for HP, stamina, etc.)"""
    def __init__(self, x, y, width, height, max_value, 
                 bg_color=(60, 60, 60), fill_color=(50, 200, 50), 
                 border_color=(100, 100, 150), show_text=True, 
                 text_color=(255, 255, 255), label=None, font=None):
        super().__init__(x, y, width, height)
        self.max_value = max_value
        self.current_value = max_value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.show_text = show_text
        self.text_color = text_color
        self.label = label
        self.font = font
        self._render()
        
    def _render(self):
        """Render the progress bar to its image surface"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw background
        pygame.draw.rect(self.image, self.bg_color, (0, 0, self.rect.width, self.rect.height))
        
        # Draw fill based on current value
        if self.max_value > 0:
            fill_width = int((self.current_value / self.max_value) * self.rect.width)
            if fill_width > 0:
                pygame.draw.rect(self.image, self.fill_color, (0, 0, fill_width, self.rect.height))
        
        # Draw border
        pygame.draw.rect(self.image, self.border_color, (0, 0, self.rect.width, self.rect.height), 2)
        
        # Draw text if enabled
        if self.show_text and self.font:
            if self.label:
                text = f"{self.label}: {int(self.current_value)}/{self.max_value}"
            else:
                text = f"{int(self.current_value)}/{self.max_value}"
            
            text_surf = self.font.render(text, True, self.text_color)
            text_rect = text_surf.get_rect(center=(self.rect.width//2, self.rect.height//2))
            self.image.blit(text_surf, text_rect)
    
    def set_value(self, value):
        """Update the current value and re-render"""
        self.current_value = max(0, min(value, self.max_value))
        self._render()


class SkillDisplay(UIElement):
    """Display for a player skill with icon, name, and cooldown"""
    def __init__(self, x, y, width, height, skill, font, hotkey=None):
        super().__init__(x, y, width, height)
        self.skill = skill
        self.font = font
        self.hotkey = hotkey
        self._render()
        
    def _render(self):
        """Render the skill display"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Background
        pygame.draw.rect(self.image, C.UI_COLORS['skill_box_bg'], (0, 0, self.rect.width, self.rect.height))
        
        # Element color indicator
        pygame.draw.rect(self.image, self.skill.color, (0, 0, 5, self.rect.height))
        
        # Skill name
        name_text = self.font.render(self.skill.name, True, C.WHITE)
        name_rect = name_text.get_rect(centerx=self.rect.width//2, top=5)
        self.image.blit(name_text, name_rect)
        
        # Element and type
        element_text = self.font.render(self.skill.element, True, self.skill.color)
        element_rect = element_text.get_rect(centerx=self.rect.width//2, top=25)
        self.image.blit(element_text, element_rect)
        
        # Render skill type text (using skill_type property)
        type_text = self.font.render(self.skill.skill_type.name, True, C.WHITE)
        type_rect = type_text.get_rect(centerx=self.rect.width//2, top=40)
        self.image.blit(type_text, type_rect)
        
        # Hotkey display
        if self.hotkey:
            key_text = self.font.render(f"[{self.hotkey}]", True, C.WHITE)
            key_rect = key_text.get_rect(centerx=self.rect.width//2, bottom=self.rect.height-5)
            self.image.blit(key_text, key_rect)
            
    def update_cooldown(self, current_time):
        """Update cooldown display"""
        if not self.skill.is_off_cooldown(current_time):
            cd_remaining = self.skill.cooldown - (current_time - self.skill.last_use_time)
            cd_height = int((cd_remaining / self.skill.cooldown) * self.rect.height)
            
            # Draw cooldown overlay
            overlay = pygame.Surface((self.rect.width, cd_height), pygame.SRCALPHA)
            overlay.fill(C.UI_COLORS['cooldown_overlay'])
            self.image.blit(overlay, (0, self.rect.height - cd_height))
            
            # Draw cooldown text
            cd_text = self.font.render(f"{cd_remaining:.1f}s", True, C.WHITE)
            cd_rect = cd_text.get_rect(center=(self.rect.width//2, self.rect.height//2))
            self.image.blit(cd_text, cd_rect)


class UIManager:
    """Manager class for handling all UI elements"""
    def __init__(self, screen):
        self.screen = screen
        self.elements = {}  # Dictionary of UI elements by group
        
    def add_element(self, element, group="default"):
        """Add a UI element to a specific group"""
        if group not in self.elements:
            self.elements[group] = []
        self.elements[group].append(element)
        
    def remove_element(self, element, group="default"):
        """Remove a UI element from a specific group"""
        if group in self.elements and element in self.elements[group]:
            self.elements[group].remove(element)
            
    def clear_group(self, group="default"):
        """Remove all elements from a group"""
        if group in self.elements:
            self.elements[group] = []
            
    def update(self, mouse_pos=None, dt=0, group="default"):
        """Update all UI elements in a group"""
        if group in self.elements:
            for element in self.elements[group]:
                element.update(mouse_pos, dt)
                
    def update_all(self, mouse_pos=None, dt=0):
        """Update all UI elements in all groups"""
        for group in self.elements:
            self.update(mouse_pos, dt, group)
                
    def draw(self, group="default"):
        """Draw all UI elements in a group"""
        if group in self.elements:
            for element in self.elements[group]:
                element.draw(self.screen)
                
    def draw_all(self):
        """Draw all UI elements in all groups"""
        for group in self.elements:
            self.draw(group)
            
    def handle_event(self, event, group="default"):
        """Handle pygame events for UI elements in a group"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if group in self.elements:
                for element in self.elements[group]:
                    if hasattr(element, 'is_clicked') and element.is_clicked(mouse_pos, True):
                        # Call the element's on_click method if it exists
                        if hasattr(element, 'on_click') and callable(element.on_click):
                            element.on_click()
                        return element  # Return the clicked element
        return None

class UI:
    """UI class for handling all UI elements"""
    @staticmethod
    def draw_selected_skills(screen, selected_skills):
        """Draw the selected skills area"""
        skill_font = Font().get_font('SKILL')
        desc_font = Font().get_font('DESC')
        chosen_y = 500
        chosen_title = skill_font.render(f"Selected Skills ({len(selected_skills)}/{C.SKILLS_LIMIT})", True, (255, 255, 255))
        screen.blit(chosen_title, (screen.get_width()//2 - chosen_title.get_width()//2, chosen_y - 30))
        # Draw slots for chosen skills
        for i in range(C.SKILLS_LIMIT):
            slot_x = (screen.get_width() // 2) - ((C.SKILLS_LIMIT * 120) // 2) + (i * 120) + 10
            slot_y = chosen_y
            # Draw slot background
            slot_rect = pygame.Rect(slot_x, slot_y, 100, 80)
            pygame.draw.rect(screen, (30, 30, 60), slot_rect)
            pygame.draw.rect(screen, (100, 100, 150), slot_rect, 2)

            # If there's a skill in this slot, draw it
            if i < len(selected_skills):
                skill = selected_skills[i]
                element = skill["element"].upper()
                # Get the primary color from the element color dictionary, with fallback to white
                if element in C.ELEMENT_COLORS:
                    element_color = C.ELEMENT_COLORS[element]['primary']
                else:
                    element_color = (255, 255, 255)  # Default to white if element not found

                # Draw element color indicator
                pygame.draw.rect(screen, element_color, (slot_x, slot_y, 5, 80))
                # Skill name (centered in slot)
                name_text = skill_font.render(skill["name"], True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(slot_x + 50, slot_y + 30))
                screen.blit(name_text, name_rect)

                # Element and cooldown
                element_text = desc_font.render(element, True, element_color)
                element_rect = element_text.get_rect(center=(slot_x + 50, slot_y + 50))
                screen.blit(element_text, element_rect)

                cooldown_text = desc_font.render(f"{float(skill['cooldown']):.1f}s", True, (200, 200, 200))
                cooldown_rect = cooldown_text.get_rect(center=(slot_x + 50, slot_y + 65))
                screen.blit(cooldown_text, cooldown_rect)
    
    @staticmethod
    def draw_hp_bar(
            surface,
            x,
            y,
            current_hp,
            max_hp,
            bar_color,
            bar_width=50,
            bar_height=6):
        """
        Draw a simple HP bar at (x, y) with the given color and size.
        Bar fill depends on current_hp / max_hp.
        """
        if current_hp < 0:
            current_hp = 0
        pygame.draw.rect(surface, (60, 60, 60), (x, y, bar_width, bar_height))
        hp_frac = current_hp / max_hp if max_hp > 0 else 0
        if hp_frac < 0:
            hp_frac = 0
        fill_width = int(bar_width * hp_frac)
        pygame.draw.rect(surface, bar_color, (x, y, fill_width, bar_height))
