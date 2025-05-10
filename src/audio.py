import pygame
from resources import Resources

class Audio:
    """Manages background music playback."""

    def __init__(self):
        self.resources = Resources()
        self.current_music = None
        self.music_enabled = True
        print("[Audio] Audio system initialization complete")

    def play_music(self, track_name):
        """Play background music if enabled"""
        if not self.music_enabled or self.current_music == track_name:
            return
            
        track_path = self.resources.get_file(track_name)
        if not track_path or not self.resources.exists(track_path):
            print(f"[Audio] Error: Music file not found: {track_path}")
            return
            
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_music = track_name
        except Exception as e:
            print(f"[Audio] ERROR playing music: {e}")
            self.current_music = None

    def stop_music(self):
        """Stop current music"""
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except pygame.error as e:
            print(f"[Audio] ERROR stopping music: {e}")

    def toggle_music(self):
        """Toggle music on/off"""
        self.music_enabled = not self.music_enabled
        if self.music_enabled and self.current_music:
            self.play_music(self.current_music)
        else:
            self.stop_music()
        return self.music_enabled
