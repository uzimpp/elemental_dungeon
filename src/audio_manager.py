import pygame
import os.path
from config import MENU_BGM_PATH, GAME_BGM_PATH

class AudioManager:
    """Handles all audio playback including background music and sound effects"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Music properties
        self.current_music = None
        self.music_volume = 0.5  # Default volume (0.0 to 1.0)
        
        # Sound effects properties
        self.sound_effects = {}
        self.sfx_volume = 0.7  # Default volume (0.0 to 1.0)
        
        # Preload background music tracks
        self.music_tracks = {
            "MENU": MENU_BGM_PATH,
            "PLAYING": GAME_BGM_PATH
        }
        
        # Status flags
        self.music_enabled = True
        self.sound_enabled = True
        
        # Check if music files exist
        self._check_music_files()
    
    def _check_music_files(self):
        """Check if music files exist and print warnings for missing files"""
        missing_files = []
        for track_name, track_path in self.music_tracks.items():
            if not os.path.exists(track_path):
                missing_files.append((track_name, track_path))
        
        if missing_files:
            print("\n===== MUSIC FILES MISSING =====")
            print("The following music files were not found:")
            for name, path in missing_files:
                print(f" - {name}: {path}")
            print("\nTo add music:")
            print("1. Download MP3 files")
            print("2. Create the directory:", os.path.dirname(MENU_BGM_PATH))
            print("3. Add the files with the configured names")
            print("============================\n")
    
    def load_music(self):
        """Pre-checks if music files exist to avoid runtime errors"""
        for track_name, track_path in self.music_tracks.items():
            if not os.path.exists(track_path):
                print(f"Warning: Music file not found: {track_path}")
                # Continue anyway - missing files will be handled gracefully
        return True
    
    def play_music(self, track_name, loop=True):
        """Play a music track by name with optional looping"""
        if not self.music_enabled:
            return
            
        # Don't restart if already playing this track
        if self.current_music == track_name:
            return
            
        # Check if track exists
        if track_name not in self.music_tracks:
            print(f"Error: Unknown music track '{track_name}'")
            return
            
        track_path = self.music_tracks[track_name]
        
        # Check if file exists
        if not os.path.exists(track_path):
            print(f"Note: Music file not found: {track_path} - continuing without music")
            return
        
        # Stop any current music
        pygame.mixer.music.stop()
        
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.music_volume)
            loop_count = -1 if loop else 0  # -1 means infinite loop
            pygame.mixer.music.play(loop_count)
            self.current_music = track_name
            print(f"Playing music track: {track_name}")
        except pygame.error as e:
            print(f"Error playing music: {e}")
            self.current_music = None  # Reset current music on error
    
    def stop_music(self):
        """Stop currently playing music"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def fade_out(self, time_ms=1000):
        """Gradually fade out the current music"""
        pygame.mixer.music.fadeout(time_ms)
        self.current_music = None
    
    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            # Resume music if it was playing before
            if self.current_music:
                self.play_music(self.current_music)
        else:
            # Stop music
            pygame.mixer.music.stop()
        return self.music_enabled
    
    def load_sound(self, name, file_path):
        """Load a sound effect"""
        if os.path.exists(file_path):
            try:
                self.sound_effects[name] = pygame.mixer.Sound(file_path)
                self.sound_effects[name].set_volume(self.sfx_volume)
            except pygame.error as e:
                print(f"Error loading sound '{name}': {e}")
        else:
            print(f"Sound file not found: {file_path}")
    
    def play_sound(self, name):
        """Play a loaded sound effect"""
        if not self.sound_enabled:
            return
            
        if name in self.sound_effects:
            self.sound_effects[name].play()
        else:
            print(f"Sound effect '{name}' not loaded")
    
    def set_sound_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sound_effects.values():
            sound.set_volume(self.sfx_volume)
    
    def toggle_sound(self):
        """Toggle sound effects on/off"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled 
