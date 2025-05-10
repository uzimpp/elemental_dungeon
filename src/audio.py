"""
Audio management module for Incantato.
Handles background music playback and sound effects.
"""
import pygame
from resources import Resources


class Audio:
    """
    Manages background music playback and sound effects.
    Provides play, stop, and toggle functionality for game audio.
    """

    def __init__(self):
        """Initialize the audio manager."""
        self.resources = Resources.get_instance()
        self.current_music = None
        self.music_enabled = True
        self.music_volume = 1.0
        print("[AudioManager] Audio system initialization complete")

    def play_music(self, track_name):
        """
        Play background music if enabled.

        Args:
            track_name (str): Name of the music track to play
        """
        if not self.music_enabled or self.current_music == track_name:
            return

        track_path = self.resources.get_data(track_name)
        if not track_path:
            print(f"[AudioManager] Error: Music file not found for: {track_name}")
            return

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_music = track_name
        except pygame.error as e:
            print(f"[AudioManager] ERROR playing music: {e}")
            self.current_music = None

    def stop_music(self):
        """Stop current music."""
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except pygame.error as e:
            print(f"[AudioManager] ERROR stopping music: {e}")

    def toggle_music(self):
        """
        Toggle music on/off.

        Returns:
            bool: Current music enabled state
        """
        self.music_enabled = not self.music_enabled
        if self.music_enabled and self.current_music:
            self.play_music(self.current_music)
        else:
            self.stop_music()
        return self.music_enabled
        
    def set_music_volume(self, volume):
        """
        Set the music volume.
        
        Args:
            volume (float): Volume level from 0.0 to 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        try:
            pygame.mixer.music.set_volume(self.music_volume)
        except pygame.error as e:
            print(f"[AudioManager] ERROR setting volume: {e}")
            
    def fade_out(self, ms):
        """
        Fade out the music over the specified milliseconds.
        
        Args:
            ms (int): Milliseconds to fade out over
        """
        try:
            pygame.mixer.music.fadeout(ms)
            self.current_music = None
        except pygame.error as e:
            print(f"[AudioManager] ERROR fading out music: {e}")
