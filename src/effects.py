# effects.py
import pygame
import math
import random
import time
from config import WIDTH, HEIGHT
from resource_manager import ResourceManager

class Effect:
    """Base class for all game effects"""
    def __init__(self, x, y, duration=1.0, loop=False):
        self.x = x
        self.y = y
        self.duration = duration
        self.start_time = time.time()
        self.active = True
        self.loop = loop
    
    def update(self, dt):
        """Update the effect state"""
        # Check if effect has expired
        elapsed = time.time() - self.start_time
        if elapsed >= self.duration and not self.loop:
            self.active = False
    
    def draw(self, surface):
        """Draw the effect"""
        pass
    
    def reset(self):
        """Reset the effect's timer"""
        self.start_time = time.time()
        self.active = True
    
    def get_progress(self):
        """Get the effect's progress (0.0 to 1.0)"""
        elapsed = time.time() - self.start_time
        progress = elapsed / self.duration if self.duration > 0 else 1.0
        
        if self.loop:
            return progress % 1.0
        else:
            return min(1.0, progress)


class VisualEffect(Effect):
    """Base class for visual effects"""
    def __init__(self, x, y, color=(255, 255, 255), duration=1.0, loop=False):
        super().__init__(x, y, duration, loop)
        self.color = color
        
        # Allow alpha component in color
        if len(self.color) == 3:
            self.color = (*self.color, 255)
    
    def get_color_with_alpha(self, alpha_multiplier=1.0):
        """Get color with adjusted alpha"""
        r, g, b, a = self.color
        return (r, g, b, int(a * alpha_multiplier))


class ParticleEffect(VisualEffect):
    """Effect composed of multiple particles"""
    def __init__(self, x, y, color=(255, 255, 255), 
                 particle_count=20, duration=1.0, 
                 min_speed=20, max_speed=100,
                 min_size=2, max_size=8,
                 gravity=0):
        super().__init__(x, y, color, duration)
        self.particles = []
        self.gravity = gravity
        
        # Create particles
        for _ in range(particle_count):
            angle = random.random() * math.pi * 2
            speed = random.uniform(min_speed, max_speed)
            size = random.uniform(min_size, max_size)
            lifetime = random.uniform(duration * 0.5, duration)
            
            particle = {
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'lifetime': lifetime,
                'creation_time': time.time()
            }
            
            self.particles.append(particle)
    
    def update(self, dt):
        """Update all particles"""
        super().update(dt)
        
        current_time = time.time()
        for p in self.particles:
            # Apply gravity
            p['vy'] += self.gravity * dt
            
            # Update position
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            
            # Check lifetime
            age = current_time - p['creation_time']
            if age > p['lifetime']:
                p['active'] = False
            else:
                p['active'] = True
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p['active']]
        
        # If all particles are gone, mark effect as inactive
        if not self.particles and not self.loop:
            self.active = False
    
    def draw(self, surface):
        """Draw all particles"""
        if not self.active:
            return
        
        current_time = time.time()
        for p in self.particles:
            # Skip inactive particles
            if not p.get('active', True):
                continue
            
            # Calculate alpha based on lifetime
            age = current_time - p['creation_time']
            life_fraction = 1.0 - (age / p['lifetime'])
            alpha = int(255 * life_fraction)
            
            # Draw particle
            pygame.draw.circle(
                surface,
                (*self.color[:3], alpha),
                (int(p['x']), int(p['y'])),
                int(p['size'] * life_fraction)
            )


class ExplosionEffect(ParticleEffect):
    """Explosion-style particle effect"""
    def __init__(self, x, y, color=(255, 100, 20), radius=30, duration=0.5):
        super().__init__(
            x, y, color,
            particle_count=int(radius * 1.5),
            duration=duration,
            min_speed=radius * 1.5,
            max_speed=radius * 3,
            min_size=2,
            max_size=8
        )
        self.radius = radius
        
        # Add an expanding ring
        self.ring_growth_rate = radius * 2 / duration
        self.ring_width = radius / 5
    
    def draw(self, surface):
        """Draw particles and expanding ring"""
        if not self.active:
            return
        
        # Draw particles
        super().draw(surface)
        
        # Draw expanding ring
        progress = self.get_progress()
        current_radius = self.radius * progress * 2
        
        # Fade out as ring expands
        alpha = int(255 * (1.0 - progress))
        pygame.draw.circle(
            surface,
            (*self.color[:3], alpha),
            (int(self.x), int(self.y)),
            int(current_radius),
            max(1, int(self.ring_width * (1.0 - progress * 0.5)))
        )


class HealEffect(ParticleEffect):
    """Healing visual effect with rising particles"""
    def __init__(self, x, y, color=(20, 255, 100), duration=0.8):
        super().__init__(
            x, y, color,
            particle_count=15,
            duration=duration,
            min_speed=20,
            max_speed=60,
            min_size=3,
            max_size=8,
            gravity=-50  # Negative gravity to make particles rise
        )
        
        # Adjust particle velocities to mostly go upward
        for p in self.particles:
            # Mostly upward direction
            angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)
            speed = random.uniform(30, 70)
            p['vx'] = math.cos(angle) * speed
            p['vy'] = math.sin(angle) * speed
    
    def draw(self, surface):
        """Draw healing particles with crosses"""
        if not self.active:
            return
        
        current_time = time.time()
        for p in self.particles:
            # Skip inactive particles
            if not p.get('active', True):
                continue
            
            # Calculate alpha based on lifetime
            age = current_time - p['creation_time']
            life_fraction = 1.0 - (age / p['lifetime'])
            alpha = int(255 * life_fraction)
            
            # Position and size
            x, y = int(p['x']), int(p['y'])
            size = int(p['size'] * life_fraction * 1.5)
            
            # Draw a plus-shaped particle
            color = (*self.color[:3], alpha)
            pygame.draw.line(surface, color, (x - size, y), (x + size, y), 2)
            pygame.draw.line(surface, color, (x, y - size), (x, y + size), 2)


class SlashEffect(VisualEffect):
    """Arc-shaped slashing effect"""
    def __init__(self, x, y, color=(200, 200, 255), radius=60, duration=0.3,
                 start_angle=0, sweep_angle=math.pi/2):
        super().__init__(x, y, color, duration)
        self.radius = radius
        self.start_angle = start_angle
        self.sweep_angle = sweep_angle
        self.slash_width = 4  # Width of the slash line
        self.particles = []   # For trailing particles
    
    def update(self, dt):
        super().update(dt)
        
        # Add particles based on current slash position
        progress = self.get_progress()
        current_angle = self.start_angle + self.sweep_angle * progress
        
        # Only add particles during the first half of animation
        if progress < 0.5:
            for _ in range(2):
                # Random position along the arc
                particle_angle = self.start_angle + current_angle * random.random()
                distance = random.uniform(0.7, 1.0) * self.radius
                px = self.x + math.cos(particle_angle) * distance
                py = self.y + math.sin(particle_angle) * distance
                
                self.particles.append({
                    'x': px,
                    'y': py,
                    'alpha': 255,
                    'size': random.randint(2, 4),
                    'creation_time': time.time()
                })
        
        # Update existing particles
        for p in self.particles:
            p['alpha'] = max(0, p['alpha'] - 10)
        
        # Remove faded particles
        self.particles = [p for p in self.particles if p['alpha'] > 0]
    
    def draw(self, surface):
        if not self.active:
            return
        
        # Calculate current angle based on progress
        progress = self.get_progress()
        current_angle = self.sweep_angle * progress
        
        # Draw the main arc
        rect = pygame.Rect(
            self.x - self.radius, self.y - self.radius,
            self.radius * 2, self.radius * 2
        )
        
        # Fade out color near the end
        alpha_multiplier = 1.0 if progress < 0.7 else (1.0 - (progress - 0.7) / 0.3)
        color = self.get_color_with_alpha(alpha_multiplier)
        
        pygame.draw.arc(
            surface, color, rect,
            self.start_angle, self.start_angle + current_angle,
            self.slash_width
        )
        
        # Draw particles
        for p in self.particles:
            pygame.draw.circle(
                surface,
                (*self.color[:3], p['alpha']),
                (int(p['x']), int(p['y'])),
                p['size']
            )
        
        # Draw inner arc (for more visibility)
        inner_radius = self.radius * 0.7
        inner_rect = pygame.Rect(
            self.x - inner_radius, self.y - inner_radius,
            inner_radius * 2, inner_radius * 2
        )
        
        pygame.draw.arc(
            surface, color, inner_rect,
            self.start_angle, self.start_angle + current_angle,
            max(1, self.slash_width - 2)
        )


class DashAfterimageEffect(VisualEffect):
    """Fading afterimage effect for dash"""
    def __init__(self, x, y, sprite, duration=0.2, start_alpha=150):
        super().__init__(x, y, (255, 255, 255, start_alpha), duration)
        self.sprite = sprite.copy()  # Copy the surface
        self.start_alpha = start_alpha
        self.width = sprite.get_width()
        self.height = sprite.get_height()
    
    def update(self, dt):
        super().update(dt)
        
        # Adjust alpha based on progress
        progress = self.get_progress()
        current_alpha = int(self.start_alpha * (1.0 - progress))
        self.sprite.set_alpha(current_alpha)
    
    def draw(self, surface):
        if not self.active or not self.sprite:
            return
        
        # Calculate top-left draw position (centering the sprite)
        draw_x = self.x - self.width / 2
        draw_y = self.y - self.height / 2
        
        surface.blit(self.sprite, (int(draw_x), int(draw_y)))


class AudioEffect(Effect):
    """Base class for audio effects"""
    def __init__(self, sound_name, volume=1.0, duration=None, loop=False):
        super().__init__(0, 0, duration or 0, loop)
        self.volume = volume
        self.sound_name = sound_name
        self.sound = None
        
        # Load sound using ResourceManager
        resource_manager = ResourceManager()
        self.sound = resource_manager.get_sound(sound_name)
        if self.sound is None:
            self.sound = resource_manager.load_sound(sound_name)
        
        if self.sound:
            self.sound.set_volume(volume)
            
            # Get duration if not provided
            if duration is None:
                self.duration = self.sound.get_length()
    
    def play(self):
        """Play the sound effect"""
        if self.sound:
            loops = -1 if self.loop else 0
            self.sound.play(loops=loops)
            self.reset()
    
    def stop(self):
        """Stop the sound effect"""
        if self.sound:
            self.sound.stop()
            self.active = False
    
    def update(self, dt):
        """Update effect status"""
        super().update(dt)
        
        # If not looping and duration passed, mark as inactive
        if not self.loop and self.get_progress() >= 1.0:
            self.active = False


class SoundEffect(AudioEffect):
    """One-shot sound effect"""
    def __init__(self, sound_name, volume=1.0):
        super().__init__(sound_name, volume)
    
    def play(self):
        """Play the sound once"""
        super().play()


class MusicTrack(AudioEffect):
    """Background music track"""
    def __init__(self, sound_name, volume=0.5, loop=True):
        super().__init__(sound_name, volume, None, loop)
    
    def fade_in(self, milliseconds=1000):
        """Fade in the music"""
        if self.sound:
            self.sound.set_volume(0)
            self.sound.play(loops=-1)
            
            # Fade in using pygame's music fade
            pygame.mixer.music.set_volume(0)
            pygame.mixer.music.load(sound_name)
            pygame.mixer.music.play(loops=-1, fade_ms=milliseconds)
            
            self.reset()
    
    def fade_out(self, milliseconds=1000):
        """Fade out the music"""
        if self.sound:
            pygame.mixer.music.fadeout(milliseconds)
            self.active = False


class EffectManager:
    """Manages all game effects"""
    def __init__(self):
        self.visual_effects = []
        self.audio_effects = []
        
        # Audio system setup
        pygame.mixer.init()
        
        # Sound effect cache
        self.sound_cache = {}
    
    def add_effect(self, effect):
        """Add an effect to the appropriate list"""
        if isinstance(effect, AudioEffect):
            self.audio_effects.append(effect)
            effect.play()
        elif isinstance(effect, VisualEffect):
            self.visual_effects.append(effect)
    
    def create_explosion(self, x, y, color=(255, 100, 20), radius=30, duration=0.5):
        """Create and add an explosion effect"""
        effect = ExplosionEffect(x, y, color, radius, duration)
        self.add_effect(effect)
        
        # Also play explosion sound
        self.play_sound("explosion", volume=0.3)
        
        return effect
    
    def create_heal(self, x, y, color=(20, 255, 100), duration=0.8):
        """Create and add a heal effect"""
        effect = HealEffect(x, y, color, duration)
        self.add_effect(effect)
        
        # Also play heal sound
        self.play_sound("heal", volume=0.4)
        
        return effect
    
    def create_slash(self, x, y, start_angle, sweep_angle, color=(200, 200, 255), radius=60, duration=0.3):
        """Create and add a slash effect"""
        effect = SlashEffect(x, y, color, radius, duration, start_angle, sweep_angle)
        self.add_effect(effect)
        
        # Also play slash sound
        self.play_sound("slash", volume=0.5)
        
        return effect
    
    def create_dash_afterimage(self, x, y, sprite, duration=0.2):
        """Create and add a dash afterimage effect"""
        effect = DashAfterimageEffect(x, y, sprite, duration)
        self.add_effect(effect)
        return effect
    
    def play_sound(self, sound_name, volume=1.0):
        """Play a sound by name using ResourceManager"""
        resource_manager = ResourceManager()
        sound = resource_manager.get_sound(sound_name)
        if sound is None:
            sound = resource_manager.load_sound(sound_name)
        
        if sound:
            effect = SoundEffect(sound_name, volume)
            effect.play()
            self.audio_effects.append(effect)
            return effect
        return None
    
    def play_music(self, music_name, volume=0.5, loop=True):
        """Play background music"""
        music_path = f"music/{music_name}.ogg"
        music = MusicTrack(music_name, volume, loop)
        music.play()
        self.audio_effects.append(music)
        return music
    
    def update(self, dt):
        """Update all effects"""
        # Update and filter visual effects
        for effect in self.visual_effects:
            effect.update(dt)
        self.visual_effects = [e for e in self.visual_effects if e.active]
        
        # Update and filter audio effects
        for effect in self.audio_effects:
            effect.update(dt)
        self.audio_effects = [e for e in self.audio_effects if e.active]
    
    def draw(self, surface):
        """Draw all visual effects"""
        for effect in self.visual_effects:
            effect.draw(surface)
    
    def stop_all(self):
        """Stop all effects"""
        for effect in self.audio_effects:
            effect.stop()
        
        self.visual_effects.clear()
        self.audio_effects.clear()
    
    def stop_music(self):
        """Stop just the music"""
        for effect in self.audio_effects:
            if isinstance(effect, MusicTrack):
                effect.stop()