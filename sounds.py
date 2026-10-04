import pygame
from resource_path import resource_path


class SoundManager:
    def __init__(self, sfx_volume=0.7, music_volume=0.5):
        if not pygame.mixer.get_init():
            pygame.mixer.init(
                frequency=44100, size=-16, channels=2, buffer=512
            )
        pygame.mixer.set_num_channels(32)
        self.sfx_volume = sfx_volume
        self.music_volume = music_volume
        self.current_music = None
        self.sounds = {}

    def load_sound(self, name, filepath):
        """Resolve, load, and cache a one-shot sound effect."""
        path = resource_path(filepath)

        if not path.is_file():
            print(f"[SoundManager] Sound file not found: {path}")
            return

        sound = pygame.mixer.Sound(str(path))
        sound.set_volume(self.sfx_volume)
        self.sounds[name] = sound

    def play_sound(self, name):
        """Play a cached effect; no filesystem lookup is needed here."""
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def play_music(self, filepath, loops=-1, fade_ms=1000):
        """Resolve and stream music, without restarting the same track."""
        path = resource_path(filepath)
        music_path = str(path)

        if self.current_music == music_path:
            return

        if not path.is_file():
            print(f"[SoundManager] Music file not found: {path}")
            return

        try:
            pygame.mixer.music.fadeout(fade_ms)
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
        except pygame.error as error:
            self.current_music = None
            print(f"[SoundManager] Music error: {error}")
        else:
            self.current_music = music_path

    def stop_music(self, fade_ms=500):
        pygame.mixer.music.fadeout(fade_ms)
        self.current_music = None

    def pause_music(self):
        pygame.mixer.music.pause()

    def unpause_music(self):
        pygame.mixer.music.unpause()

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)