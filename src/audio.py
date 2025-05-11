"""
Audio management module for Incantato game.

Handles background music and sound effects using the Pygame mixer,
implementing a singleton pattern to ensure centralized audio control.
"""
import os.path
import time

import pygame

from config import Config as C


class Audio:
    """
    Audio management system using singleton pattern to ensure
    only one instance controls all game audio.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        """
        Create or return the singleton instance.

        Returns:
            Audio: The singleton Audio instance
        """
        if cls._instance is None:
            cls._instance = super(Audio, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the audio system if not already initialized."""
        # Skip initialization if already done
        if self._initialized:
            return

        self._initialized = True
        self._font_path = None

        pygame.mixer.init()

        # Music properties
        self.current_music = None
        self.music_volume = 0.5  # Default volume (0.0 to 1.0)

        # Sound effects dictionary (name -> Sound object)
        self.sound_effects = {}
        self.sfx_volume = 0.7  # Default volume (0.0 to 1.0)

        # Preload background music tracks
        self.music_tracks = {
            "MENU": C.MENU_BGM_PATH,
            "PLAYING": C.GAME_BGM_PATH,
        }

        # Status flags
        self.music_enabled = True
        self.sound_enabled = True

        # Preload music files
        self.load_music()

    def load_music(self):
        """
        Pre-check if music files exist to avoid runtime errors.

        Returns:
            bool: True if verification completed (even if files are missing)
        """
        for track_key, track_path in self.music_tracks.items():
            if not os.path.exists(track_path):
                print(f"Warning: Music file not found: {track_path}")
        return True

    def play_music(self, music_key):
        """
        Play a music track by key.

        Args:
            music_key: Key identifying the music track ("MENU" or "PLAYING")
        """
        if not self.music_enabled:
            return

        if music_key == "MENU":
            pygame.mixer.music.load(C.MENU_BGM_PATH)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_music = music_key
        elif music_key == "PLAYING":
            pygame.mixer.music.load(C.GAME_BGM_PATH)
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.current_music = music_key

        pygame.mixer.music.set_volume(self.music_volume)

    def stop_music(self):
        """Stop the currently playing music."""
        pygame.mixer.music.stop()
        self.current_music = None

    def fade_out(self, fade_ms=500):
        """
        Fade out the current music.

        Args:
            fade_ms: Fade duration in milliseconds
        """
        pygame.mixer.music.fadeout(fade_ms)

    def fade_in(self, music_key, fade_ms=500):
        """
        Fade in a new music track.

        Args:
            music_key: Key identifying the music track
            fade_ms: Fade duration in milliseconds

        Returns:
            function: A callback function to handle the fade effect,
            or None if music is disabled
        """
        if not self.music_enabled:
            return None

        # Set volume to 0 and then start fading in
        orig_volume = self.music_volume
        pygame.mixer.music.set_volume(0.0)

        # Start playing the new track
        self.play_music(music_key)

        # Create a fade-in effect using a timer
        start_time = time.time()

        def fade_step():
            elapsed = time.time() - start_time
            progress = min(elapsed / (fade_ms / 1000), 1.0)
            pygame.mixer.music.set_volume(progress * orig_volume)

            if progress < 1.0:
                # Continue fading
                # Check again in 50ms
                pygame.time.set_timer(pygame.USEREVENT, 50)
            else:
                # Done fading, clear the timer
                pygame.time.set_timer(pygame.USEREVENT, 0)

        # Set up the timer for the first step
        pygame.time.set_timer(pygame.USEREVENT, 50)

        # The event will be handled in the main game loop
        return fade_step

    def set_music_volume(self, volume):
        """
        Set music volume.

        Args:
            volume: Volume level from 0.0 to 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_enabled:
            pygame.mixer.music.set_volume(self.music_volume)

    def toggle_music(self):
        """
        Toggle music on/off.

        Returns:
            bool: Current music enabled state
        """
        self.music_enabled = not self.music_enabled

        if self.music_enabled:
            # Resume music if we have a current track
            if self.current_music:
                self.play_music(self.current_music)
        else:
            # Stop music
            self.stop_music()

        return self.music_enabled

    def load_sound(self, name, file_path):
        """
        Load a sound effect.

        Args:
            name: Identifier for the sound effect
            file_path: Path to the sound file
        """
        if os.path.exists(file_path):
            try:
                self.sound_effects[name] = pygame.mixer.Sound(file_path)
                self.sound_effects[name].set_volume(self.sfx_volume)
            except pygame.error as e:
                print(f"Error loading sound '{name}': {e}")
        else:
            print(f"Sound file not found: {file_path}")

    def play_sound(self, sound_key):
        """
        Play a sound effect by key.

        Args:
            sound_key: Key identifying the sound effect
        """
        if not self.sound_enabled or sound_key not in self.sound_effects:
            return

        self.sound_effects[sound_key].set_volume(self.sfx_volume)
        self.sound_effects[sound_key].play()

    def set_sound_volume(self, volume):
        """
        Set sound effects volume.

        Args:
            volume: Volume level from 0.0 to 1.0
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sound_effects.values():
            sound.set_volume(self.sfx_volume)

    def toggle_sound(self):
        """
        Toggle sound effects on/off.

        Returns:
            bool: Current sound enabled state
        """
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled
