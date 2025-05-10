import pygame
import os
from resources import Resources

class Audio:
    """Manages all audio playback including background music and sound effects."""

    def __init__(self):
        self.resources = Resources()  # Composition: use the singleton resource manager
        self.current_music = None
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.sound_enabled = True
        self.music_enabled = True
        print("[AudioManager] Audio system initialization complete")

    def play_music(self, track_name, loop=True):
        if not self.music_enabled or self.current_music == track_name:
            return
        track_path = self.resources.get_file(track_name)
        if not track_path or not os.path.exists(track_path):
            print(f"[AudioManager] Error: Music file not found: {track_path}")
            return
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.music_volume)
            loop_count = -1 if loop else 0
            pygame.mixer.music.play(loop_count)
            self.current_music = track_name
        except Exception as e:
            print(f"[AudioManager] ERROR playing music: {e}")
            self.current_music = None

    def stop_music(self):
        try:
            pygame.mixer.music.stop()
            self.current_music = None
        except pygame.error as e:
            print(f"[AudioManager] ERROR stopping music: {e}")

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled and self.current_music:
            self.play_music(self.current_music)
        else:
            pygame.mixer.music.stop()
        return self.music_enabled

    def play_sound(self, sound_name):
        if not self.sound_enabled:
            return
        sound = self.resources.get_file(sound_name)
        if sound:
            try:
                sound.set_volume(self.sfx_volume)
                sound.play()
            except pygame.error as e:
                print(f"[AudioManager] ERROR playing sound {sound_name}: {e}")

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        print(f"[AudioManager] Sound effects {'enabled' if self.sound_enabled else 'disabled'}")
        return self.sound_enabled
