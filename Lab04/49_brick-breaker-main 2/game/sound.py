"""Procedurally generated sound effects (no asset files).

Every public method is a no-op if numpy is missing or the mixer can't
initialise (no audio device, headless CI, etc.), so the game always runs.
"""
import pygame

try:
    import numpy as np
except ImportError:  # sound is optional
    np = None


class SoundBank:
    def __init__(self, volume=0.35):
        self.enabled = False
        self.sounds = {}
        try:
            if np is None:
                return
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            init = pygame.mixer.get_init()
            if not init:
                return
            self.rate, fmt, self.channels = init
            self.bits = abs(fmt)
            self.signed = fmt < 0
            self.volume = volume

            self.sounds = {
                "brick": self._tone([880, 1320], 0.07, wave="square", vol=0.5),
                "paddle": self._tone([330], 0.06, wave="square", vol=0.6),
                "wall": self._tone([220], 0.04, wave="triangle", vol=0.6),
                "win": self._sequence([523, 659, 784, 1047], 0.12, wave="square"),
                "lose": self._sequence([392, 330, 262, 196], 0.18, wave="triangle", slide=True),
            }
            self.enabled = True
        except Exception:
            self.enabled = False
            self.sounds = {}

    # ------------------------------------------------------------ public API

    def play(self, name):
        if not self.enabled:
            return
        try:
            snd = self.sounds.get(name)
            if snd:
                snd.play()
        except Exception:
            pass

    # ------------------------------------------------------------ synthesis

    def _wave(self, freqs, duration, wave, slide=False):
        """Float samples in [-1, 1]. `freqs` are played in sequence across the duration."""
        n = max(1, int(self.rate * duration))
        t = np.arange(n) / self.rate
        seg = np.array_split(np.arange(n), len(freqs))
        freq = np.empty(n)
        for idx, f in zip(seg, freqs):
            freq[idx] = f
        if slide:
            freq = freq * np.linspace(1.0, 0.85, n)  # droop downward
        phase = 2 * np.pi * np.cumsum(freq) / self.rate

        if wave == "square":
            y = np.sign(np.sin(phase)) * 0.6
        elif wave == "triangle":
            y = 2 / np.pi * np.arcsin(np.sin(phase))
        else:
            y = np.sin(phase)

        # Short attack + exponential decay envelope to avoid clicks
        attack = min(n, int(self.rate * 0.004))
        env = np.exp(-4.0 * t / duration)
        if attack:
            env[:attack] *= np.linspace(0, 1, attack)
        env[-min(n, 64):] *= np.linspace(1, 0, min(n, 64))
        return y * env

    def _tone(self, freqs, duration, wave="sine", vol=1.0, slide=False):
        return self._make(self._wave(freqs, duration, wave, slide) * vol)

    def _sequence(self, freqs, note_len, wave="sine", slide=False):
        notes = [self._wave([f], note_len, wave, slide) for f in freqs]
        # let the final note ring longer
        notes[-1] = self._wave([freqs[-1]], note_len * 2.5, wave, slide)
        return self._make(np.concatenate(notes) * 0.7)

    def _make(self, samples):
        """Convert float samples to a pygame Sound matching the mixer format."""
        samples = np.clip(samples * self.volume, -1.0, 1.0)
        if self.bits == 8:
            dtype = np.int8 if self.signed else np.uint8
            peak, offset = 127, (0 if self.signed else 128)
        elif self.bits == 32:
            dtype = np.int32 if self.signed else np.uint32
            peak, offset = 2**31 - 1, (0 if self.signed else 2**31)
        else:
            dtype = np.int16 if self.signed else np.uint16
            peak, offset = 32767, (0 if self.signed else 32768)
        data = (samples * peak + offset).astype(dtype)
        if self.channels > 1:
            data = np.repeat(data[:, None], self.channels, axis=1)
        return pygame.sndarray.make_sound(np.ascontiguousarray(data))
