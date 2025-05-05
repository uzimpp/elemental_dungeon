import pygame
import time
import os.path
from singleton import Singleton
from resource_manager import ResourceManager

class AudioManager(Singleton):
    """Singleton class to handle all audio playback including background music and sound effects"""
    
    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            print("\n[AudioManager] Initializing audio system...")
            try:
                # Try to initialize with different parameters
                pygame.mixer.quit()  # Reset mixer if it was previously initialized
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                # Add a small delay to ensure mixer is fully initialized
                time.sleep(0.5)
                print("[AudioManager] Pygame mixer initialized successfully")
            except pygame.error as e:
                print(f"[AudioManager] ERROR initializing pygame mixer: {e}")
            
            # Get the resource manager
            self.resource_manager = ResourceManager()
            
            # Music properties
            self.current_music = None
            self.music_volume = 0.5  # Default volume (0.0 to 1.0)
            
            # Sound effects properties
            self.sfx_volume = 0.7  # Default volume (0.0 to 1.0)
            
            # Status flags
            self.music_enabled = True
            self.sound_enabled = True
            
            self.initialized = True
            print("[AudioManager] Audio system initialization complete")
    
    def play_music(self, track_name, loop=True):
        """Play a music track by name with optional looping"""
        print(f"[AudioManager] Request to play music: {track_name} (currently enabled: {self.music_enabled})")
        if not self.music_enabled:
            print("[AudioManager] Music is disabled, not playing.")
            return

        # Don't restart if already playing this track
        if self.current_music == track_name:
            print(f"[AudioManager] Already playing {track_name}, not restarting.")
            return

        # Get the music path from the resource manager
        track_path = self.resource_manager.get_music_path(track_name)
        if not track_path:
            print(f"[AudioManager] Error: Music track '{track_name}' not found")
            return

        # Check if file exists
        if not os.path.exists(track_path):
            print(f"[AudioManager] Error: Music file not found: {track_path}")
            return

        # Stop any current music
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"[AudioManager] Warning: Could not stop previous music: {e}")

        try:
            print(f"[AudioManager] Loading music file: {track_path}")
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.music_volume)
            loop_count = -1 if loop else 0  # -1 means infinite loop
            pygame.mixer.music.play(loop_count)
            self.current_music = track_name
            print(f"[AudioManager] Successfully playing music track: {track_name}")
        except pygame.error as e:
            print(f"[AudioManager] ERROR playing music: {e}")
            print(f"[AudioManager] DEBUG: File path: {track_path}, File exists: {os.path.exists(track_path)}, File size: {os.path.getsize(track_path) if os.path.exists(track_path) else 'N/A'}")
            self.current_music = None  # Reset current music on error
        except Exception as e:
            print(f"[AudioManager] UNEXPECTED ERROR playing music: {e}")
            self.current_music = None
    
    def stop_music(self):
        """Stop currently playing music"""
        try:
            pygame.mixer.music.stop()
            self.current_music = None
            print("[AudioManager] Music stopped")
        except pygame.error as e:
            print(f"[AudioManager] Error stopping music: {e}")
    
    def fade_out(self, time_ms=1000):
        """Gradually fade out the current music"""
        if self.current_music:
            try:
                pygame.mixer.music.fadeout(time_ms)
                print(f"[AudioManager] Fading out music over {time_ms}ms")
                self.current_music = None
            except pygame.error as e:
                print(f"[AudioManager] Error fading out music: {e}")
                self.stop_music()  # Fallback to stop if fadeout fails
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
            print(f"[AudioManager] Music volume set to {self.music_volume:.1f}")
        except pygame.error as e:
            print(f"[AudioManager] Error setting music volume: {e}")
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            print("[AudioManager] Music enabled")
            # Resume music if it was playing before
            if self.current_music:
                self.play_music(self.current_music)
        else:
            print("[AudioManager] Music disabled")
            # Stop music
            pygame.mixer.music.stop()
        return self.music_enabled
    
    def play_sound(self, name):
        """Play a loaded sound effect"""
        if not self.sound_enabled:
            print(f"[AudioManager] Sound disabled, not playing '{name}'")
            return
            
        sound = self.resource_manager.get_sound(name)
        if sound:
            try:
                sound.set_volume(self.sfx_volume)  # Ensure correct volume
                sound.play()
                print(f"[AudioManager] Playing sound effect: {name}")
            except pygame.error as e:
                print(f"[AudioManager] Error playing sound '{name}': {e}")
    
    def set_sound_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        print(f"[AudioManager] Sound effect volume set to {self.sfx_volume:.1f}")
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
        print(f"[AudioManager] Sound effects {'enabled' if self.sound_enabled else 'disabled'}")
        return self.sound_enabled 
