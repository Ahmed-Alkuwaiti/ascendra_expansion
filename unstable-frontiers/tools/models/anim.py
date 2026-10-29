"""Writes Bedrock/GeckoLib animation files (.animation.json), the format Blockbench's animator edits.

Keyframes are sampled from small functions of time (sines for gaits and wingbeats, eased curves for attacks), so cycles
loop seamlessly and every bone in a gait shares one clock.
"""
import json
import math


class Anim:
    def __init__(self, name, length, loop=True):
        self.name = name
        self.length = length
        self.loop = loop     # True, False or 'hold' (hold_on_last_frame)
        self.channels = {}   # bone -> {'rotation'|'position'|'scale': {time: [x, y, z]}}

    def key(self, bone, channel, t, vec):
        self.channels.setdefault(bone, {}).setdefault(channel, {})[round(t, 4)] = [round(float(v), 3) for v in vec]

    def wave(self, bone, channel, fn, steps=8):
        """fn(phase 0..1) -> [x, y, z]; sampled at steps+1 points so the loop closes."""
        for i in range(steps + 1):
            p = i / steps
            self.key(bone, channel, p * self.length, fn(p))

    def keys(self, bone, channel, pairs):
        for t, v in pairs:
            self.key(bone, channel, t, v)

    def to_json(self):
        bones = {}
        for b, chans in self.channels.items():
            bones[b] = {}
            for ch, ks in chans.items():
                bones[b][ch] = {f'{t:.4f}'.rstrip('0').rstrip('.') if t else '0.0': v for t, v in sorted(ks.items())}
        j = {'animation_length': self.length, 'bones': bones}
        if self.loop is True:
            j['loop'] = True
        elif self.loop == 'hold':
            j['loop'] = 'hold_on_last_frame'
        return j

    def sample(self, bone, channel, t):
        ks = self.channels.get(bone, {}).get(channel)
        if not ks:
            return None
        times = sorted(ks)
        if t <= times[0]:
            return ks[times[0]]
        for a, b in zip(times, times[1:]):
            if a <= t <= b:
                f = (t - a) / (b - a) if b > a else 0
                return [ks[a][i] + (ks[b][i] - ks[a][i]) * f for i in range(3)]
        return ks[times[-1]]


def save(anims, path):
    with open(path, 'w') as f:
        json.dump({'format_version': '1.8.0', 'animations': {a.name: a.to_json() for a in anims}}, f, indent=1)


def sin(p, amp, phase=0.0):
    return amp * math.sin(2 * math.pi * (p + phase))


def ease(t):
    return t * t * (3 - 2 * t)
