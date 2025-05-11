import pygame
import time
import math
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
                 bg_color=(30, 30, 60), border_color=(100, 100, 150),
                 draw_background=True):
        super().__init__(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.draw_background = draw_background
        self.on_click = None  # Callback function to be called when button is clicked
        self._render()

    def _render(self):
        """Render the button to its image surface"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        if self.draw_background:
            # Draw button background
            pygame.draw.rect(self.image, self.bg_color,
                             (0, 0, self.rect.width, self.rect.height))
            pygame.draw.rect(self.image, self.border_color,
                             (0, 0, self.rect.width, self.rect.height), 2)

        # Render text
        text_color = self.hover_color if self.is_hovered else self.color
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(
            center=(self.rect.width//2, self.rect.height//2))
        self.image.blit(text_surf, text_rect)

    def update(self, mouse_pos=None, dt=0):
        """Update button state and appearance"""
        was_hovered = self.is_hovered
        super().update(mouse_pos, dt)
        if was_hovered != self.is_hovered:
            self._render()

    def set_text(self, text):
        """Change the button text"""
        self.text = text
        self._render()

    def is_clicked(self, mouse_pos, mouse_click):
        """Check if element was clicked"""
        # Ensure mouse_click is True and mouse_pos is within the button's rect
        return self.rect.collidepoint(mouse_pos) and mouse_click

    def draw(self, screen):
        """Draw the button by blitting its pre-rendered image."""
        screen.blit(self.image, self.rect)


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
        pygame.draw.rect(self.image, self.bg_color,
                         (0, 0, self.rect.width, self.rect.height))

        # Draw fill based on current value
        if self.max_value > 0:
            fill_width = int(
                (self.current_value / self.max_value) * self.rect.width)
            if fill_width > 0:
                pygame.draw.rect(self.image, self.fill_color,
                                 (0, 0, fill_width, self.rect.height))

        # Draw border
        pygame.draw.rect(self.image, self.border_color,
                         (0, 0, self.rect.width, self.rect.height), 2)

        # Draw text if enabled
        if self.show_text and self.font:
            if self.label:
                text = f"{self.label}: {int(self.current_value)}/{self.max_value}"
            else:
                text = f"{int(self.current_value)}/{self.max_value}"

            text_surf = self.font.render(text, True, self.text_color)
            text_rect = text_surf.get_rect(
                center=(self.rect.width//2, self.rect.height//2))
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
        # Ensure width and height are treated as diameter for a circle
        self.diameter = min(width, height)
        self.radius = self.diameter // 2
        self.center_x = width // 2
        self.center_y = height // 2
        self._render()

    def _render(self):
        """Render the skill display - base state (no cooldown shown)"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency

        # Circle Background
        pygame.draw.circle(
            self.image, C.UI_COLORS['skill_box_bg'], (self.center_x, self.center_y), self.radius)
        # Element color as border
        pygame.draw.circle(self.image, self.skill.color, (self.center_x,
                           self.center_y), self.radius, 3)  # Border width 3

        # Skill name
        if self.skill and hasattr(self.skill, 'name'):
            name_text_render = self.font.render(
                self.skill.name, True, C.UI_COLORS['skill_text'])
            name_rect = name_text_render.get_rect(
                center=(self.center_x, self.center_y - self.radius // 3))
            self.image.blit(name_text_render, name_rect)

        # Hotkey display
        if self.hotkey:
            key_text_render = self.font.render(
                f"[{self.hotkey}]", True, C.UI_COLORS['skill_hotkey'])
            key_rect = key_text_render.get_rect(
                center=(self.center_x, self.center_y + self.radius // 2))
            self.image.blit(key_text_render, key_rect)

    def update_cooldown(self, current_time):
        """Update cooldown display. Calls _render() to refresh base and then draws cooldown if active."""
        # CRUCIAL FIX: Redraw the base skill display first to clear previous cooldown renderings
        self._render()

        if not self.skill.is_off_cooldown(current_time):
            cd_remaining = self.skill.cooldown - \
                (current_time - self.skill.last_use_time)

            # Cooldown Arc
            if cd_remaining > 0 and self.skill.cooldown > 0:
                arc_angle_fraction = cd_remaining / self.skill.cooldown
                # Sweep from top (-PI/2) clockwise
                start_angle_rad = -math.pi / 2
                # pygame.draw.arc sweeps counter-clockwise, so adjust stop_angle calculation or angles
                # To draw remaining cooldown (e.g. full arc when cd_remaining is high):
                # We want the arc to represent the *elapsed* time to "clear" the circle, or *remaining* part.
                # Let's draw the part that is *still on cooldown*.
                stop_angle_rad = start_angle_rad + \
                    (arc_angle_fraction * 2 * math.pi)

                arc_rect = pygame.Rect(
                    self.center_x - self.radius, self.center_y - self.radius, self.diameter, self.diameter)

                # Ensure arc is drawn within the circle border. Inset the rect slightly.
                # Slightly smaller than main radius to fit inside border
                arc_draw_radius = self.radius - 2
                arc_draw_diameter = arc_draw_radius * 2
                arc_draw_rect = pygame.Rect(
                    self.center_x - arc_draw_radius, self.center_y - arc_draw_radius, arc_draw_diameter, arc_draw_diameter)

                try:
                    pygame.draw.arc(self.image, C.UI_COLORS['cooldown_overlay'], arc_draw_rect,
                                    start_angle_rad, stop_angle_rad, width=6)  # Arc width 6
                except TypeError as e:  # Pygame issue if start_angle == stop_angle
                    if start_angle_rad != stop_angle_rad:  # Only print if it's an unexpected error
                        print(
                            f"Error drawing arc: {e}, start: {start_angle_rad}, stop: {stop_angle_rad}")

            # Draw cooldown text (numerical)
            cd_text_render = self.font.render(
                f"{cd_remaining:.1f}s", True, C.UI_COLORS['skill_text'])
            cd_rect = cd_text_render.get_rect(
                center=(self.center_x, self.center_y))
            self.image.blit(cd_text_render, cd_rect)


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
        skill_font = Font().get_font('SKILL')  # Smaller font for skill name in slot
        desc_font = Font().get_font('DESC')  # Font for details like CD, Type, Dmg
        ui_font = Font().get_font('UI')  # For the 'X' mark and slot title
        chosen_y = 500
        chosen_title_text = f"Selected Skills ({len(selected_skills)}/{C.SKILLS_LIMIT})"
        chosen_title = ui_font.render(chosen_title_text, True, C.WHITE)
        screen.blit(chosen_title, (screen.get_width()//2 -
                    chosen_title.get_width()//2, chosen_y - 25))  # Adjusted y for title

        slot_width = 100
        slot_height = 90  # Increased height slightly for more text
        total_slots_width = C.SKILLS_LIMIT * \
            (slot_width + 20)  # 20 for spacing
        start_x = (screen.get_width() - total_slots_width) // 2 + 10

        for i in range(C.SKILLS_LIMIT):
            slot_x = start_x + i * (slot_width + 20)
            slot_y = chosen_y
            slot_rect = pygame.Rect(slot_x, slot_y, slot_width, slot_height)
            pygame.draw.rect(screen, (30, 30, 60), slot_rect)
            pygame.draw.rect(screen, (100, 100, 150), slot_rect, 2)

            if i < len(selected_skills):
                skill = selected_skills[i]
                element = skill.get("element", "N/A").upper()
                element_color = C.ELEMENT_COLORS.get(
                    element, {}).get('primary', C.WHITE)

                pygame.draw.rect(screen, element_color,
                                 (slot_x, slot_y, 5, slot_height))

                text_x_offset = 10  # Start text rendering further from the element bar
                current_y = slot_y + 5

                name_text = skill_font.render(
                    skill.get("name", "Unknown"), True, C.WHITE)
                screen.blit(name_text, (slot_x + text_x_offset, current_y))
                current_y += name_text.get_height() + 2

                type_text_str = f"Type: {skill.get('skill_type', 'N/A')}"
                # Assuming LIGHT_GREY will be fixed or use GREY
                type_text = desc_font.render(type_text_str, True, C.LIGHT_GREY)
                screen.blit(type_text, (slot_x + text_x_offset, current_y))
                current_y += type_text.get_height() + 2

                # Placeholder for damage - replace skill.get('damage', 'N/A') with actual field
                damage_val = skill.get(
                    'damage', skill.get('description_short', 'N/A'))
                damage_text_str = f"Dmg: {damage_val}"
                damage_text = desc_font.render(
                    damage_text_str, True, C.LIGHT_GREY)
                screen.blit(damage_text, (slot_x + text_x_offset, current_y))
                current_y += damage_text.get_height() + 2

                cd_text_str = f"CD: {float(skill.get('cooldown', 0)):.1f}s"
                cd_text = desc_font.render(cd_text_str, True, C.LIGHT_GREY)
                screen.blit(cd_text, (slot_x + text_x_offset, current_y))

                x_mark_text = ui_font.render("X", True, C.RED)
                x_rect = x_mark_text.get_rect(
                    top=slot_y + 3, right=slot_x + slot_width - 3)
                screen.blit(x_mark_text, x_rect)

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
