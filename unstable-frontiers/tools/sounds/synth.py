"""Synthesises the creatures' sounds from scratch (noise, oscillators, filters, envelopes): no samples, no third-party audio.

    python3 tools/sounds/synth.py [out_dir] [--sheet sheet.png]

Writes mono 44.1 kHz Ogg Vorbis files (ffmpeg with libvorbis) to assets/unstable_frontiers/sounds/<creature>/<name>.ogg, and
optionally a spectrogram sheet of all of them for inspection. Every sound is deterministic (seeded), so re-running reproduces
the same files. Edit a recipe below and re-run to change one.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers', 'sounds')


# ------------------------------------------------------------------------------------------------------- building blocks
def t_(dur):
    return np.arange(int(dur * SR)) / SR


def noise(dur, rng):
    return rng.standard_normal(int(dur * SR))


def brown(dur, rng):
    x = np.cumsum(rng.standard_normal(int(dur * SR)))
    x -= np.convolve(x, np.ones(2001) / 2001, mode='same')   # remove the drift
    return x / (np.abs(x).max() + 1e-9)


def band(x, lo, hi, soft=0.15):
    """Band-pass by masking the spectrum (with soft edges)."""
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    w = np.clip((f - lo * (1 - soft)) / (lo * soft * 2 + 1e-9), 0, 1) if lo > 0 else np.ones_like(f)
    w *= np.clip((hi * (1 + soft) - f) / (hi * soft * 2 + 1e-9), 0, 1)
    return np.fft.irfft(X * w, len(x))


def lowpass(x, hi):
    return band(x, 0, hi)


def sweep_band(x, lo0, hi0, lo1, hi1, chunks=24):
    """A band-pass whose band moves over the sound (overlap-added chunks)."""
    n = len(x)
    out = np.zeros(n)
    size = n // chunks * 2
    win = np.hanning(size)
    for i in range(chunks * 2 - 1):
        a = i * size // 2
        seg = x[a:a + size]
        if len(seg) < size:
            seg = np.pad(seg, (0, size - len(seg)))
        p = i / (chunks * 2 - 2)
        y = band(seg * win, lo0 + (lo1 - lo0) * p, hi0 + (hi1 - hi0) * p)
        m = min(size, n - a)
        if m > 0:
            out[a:a + m] += y[:m]
    return out


def env(dur, attack=0.01, release=0.2, hold=None, curve=2.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    e = np.ones(n)
    a = t < attack
    e[a] = (t[a] / attack)
    hold = dur - release if hold is None else hold
    r = t > hold
    e[r] = np.clip(1 - (t[r] - hold) / max(1e-6, dur - hold), 0, 1) ** curve
    return e


def decay(dur, tau):
    return np.exp(-t_(dur) / tau)


def osc(freq, dur, shape='sine', vib=0.0, vib_rate=6.0, rng=None, jitter=0.0):
    """freq may be a number or an array (a glide). shape: sine, saw, square, tri."""
    n = int(dur * SR)
    f = np.full(n, float(freq)) if np.isscalar(freq) else np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(freq)), freq)
    if vib:
        f = f * (1 + vib * np.sin(2 * np.pi * vib_rate * t_(dur)))
    if jitter and rng is not None:
        j = lowpass(rng.standard_normal(n), 30)
        f = f * (1 + jitter * j / (np.abs(j).max() + 1e-9))
    ph = 2 * np.pi * np.cumsum(f) / SR
    if shape == 'sine':
        return np.sin(ph)
    if shape == 'saw':
        return 2 * ((ph / (2 * np.pi)) % 1) - 1
    if shape == 'square':
        return np.sign(np.sin(ph))
    if shape == 'tri':
        return 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1
    raise ValueError(shape)


def glide(a, b, n=64, power=1.0):
    return a + (b - a) * np.linspace(0, 1, n) ** power


def place(dst, src, at):
    i = int(at * SR)
    m = min(len(src), len(dst) - i)
    if m > 0:
        dst[i:i + m] += src[:m]
    return dst


def click(freq, rng, dur=0.03, q=0.004):
    """A chitinous click: a noise burst through a resonant ring."""
    n = noise(dur, rng) * decay(dur, q)
    ring = osc(freq, dur) * decay(dur, q * 2.5)
    return band(n, freq * 0.6, freq * 1.6) + 0.6 * ring


def formant(x, centres, width=0.25):
    out = np.zeros_like(x)
    for c, g in centres:
        out += g * band(x, c * (1 - width), c * (1 + width))
    return out


def drive(x, k):
    return np.tanh(k * x) / np.tanh(k)


def norm(x, peak=0.89):
    x = x - np.mean(x)
    return x / (np.abs(x).max() + 1e-9) * peak


def fade(x, ms=8):
    n = int(ms / 1000 * SR)
    x[:n] *= np.linspace(0, 1, n)
    x[-n:] *= np.linspace(1, 0, n)
    return x


# ----------------------------------------------------------------------------------------------------------- recipes
def gnashback_ambient(rng):
    d = 1.6
    x = np.zeros(int(d * SR))
    at = 0.05
    while at < d - 0.1:   # a bout of mandible chitter, slowing down
        x = place(x, click(rng.uniform(1800, 3200), rng) * rng.uniform(0.5, 1.0), at)
        at += rng.uniform(0.04, 0.09) * (1 + at)
    purr = osc(58, d, 'saw', rng=rng, jitter=0.05) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t_(d)))
    x += 0.35 * lowpass(purr, 400) * env(d, 0.2, 0.6)
    return x


def gnashback_hurt(rng):
    d = 0.45
    crack = band(noise(d, rng), 900, 5000) * decay(d, 0.03)
    rasp = drive(osc(glide(320, 140, power=0.7), d, 'square', rng=rng, jitter=0.08), 2) * env(d, 0.005, 0.3)
    return crack + 0.5 * formant(rasp, [(700, 1.0), (1600, 0.6)])


def gnashback_death(rng):
    d = 1.8
    rasp = osc(glide(260, 60, power=0.6), d, 'saw', rng=rng, jitter=0.1) * env(d, 0.01, 1.2)
    x = formant(drive(rasp, 3), [(500, 1.0), (1200, 0.5)])
    at = 0.1
    while at < d - 0.2:
        x = place(x, click(rng.uniform(1500, 2500), rng) * 0.8 * (1 - at / d), at)
        at += 0.05 + at * 0.12
    x = place(x, lowpass(noise(0.5, rng), 500) * decay(0.5, 0.08) * 1.5, 1.2)   # the shell hits the ground
    return x


def gnashback_bite(rng):
    d = 0.3
    x = np.zeros(int(d * SR))
    x = place(x, click(2600, rng, 0.06, 0.006), 0.0)
    x = place(x, click(2100, rng, 0.08, 0.008) * 1.2, 0.09)
    x += 0.3 * lowpass(noise(d, rng), 300) * decay(d, 0.05)
    return x


def gnashback_scrape(rng):
    d = 1.3
    x = brown(d, rng) + 0.3 * noise(d, rng)
    x = sweep_band(x, 300, 1400, 200, 900)
    stroke = np.zeros(int(d * SR))
    for at in (0.05, 0.6):   # two scrapes of the foreleg
        stroke = place(stroke, env(0.45, 0.06, 0.25), at)
    grit = (rng.random(len(x)) < 0.002) * rng.standard_normal(len(x))
    return x * stroke + 0.5 * band(grit, 2000, 6000) * stroke


def gnashback_charge(rng):
    d = 1.1
    growl = drive(osc(glide(70, 115, power=0.5), d, 'saw', rng=rng, jitter=0.06), 2.5)
    growl = formant(growl, [(250, 1.0), (700, 0.6), (1500, 0.3)])
    buzz = band(noise(d, rng), 150, 1200) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 120 * t_(d))))   # the elytra
    return (growl + 0.5 * buzz) * env(d, 0.15, 0.3)


def gnashback_impact(rng):
    d = 0.7
    thud = osc(glide(80, 40), d) * decay(d, 0.12)
    crunch = lowpass(noise(d, rng), 900) * decay(d, 0.05)
    cr2 = band(noise(d, rng), 1500, 4500) * decay(d, 0.02)
    return 1.4 * thud + crunch + 0.4 * cr2


def shrike_cry(rng, d, f0, f1, rough=0.3, power=1.0, vib=0.03):
    car = glide(f0, f1, power=power)
    mod = osc(np.array(car) * 1.5, d, rng=rng, jitter=0.02)
    n = int(d * SR)
    f = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(car)), car) * (1 + vib * np.sin(2 * np.pi * 7 * t_(d)))
    ph = 2 * np.pi * np.cumsum(f) / SR + 2.2 * mod
    tone = np.sin(ph)
    tone = drive(tone, 2.0)
    hiss = band(noise(d, rng), 2500, 7000) * rough
    return formant(tone, [(f0 * 1.0, 1.0), (f0 * 2.1, 0.6), (3200, 0.4)], 0.4) + hiss


def shrikewing_ambient(rng):
    d = 0.9
    return shrike_cry(rng, d, 1350, 900, 0.15, 0.8) * env(d, 0.03, 0.5)


def shrikewing_ambient2(rng):
    d = 1.1
    x = np.zeros(int(d * SR))
    x = place(x, shrike_cry(rng, 0.35, 1500, 1200, 0.15) * env(0.35, 0.02, 0.2), 0.0)
    x = place(x, shrike_cry(rng, 0.6, 1400, 850, 0.15, 0.7) * env(0.6, 0.02, 0.4), 0.42)
    return x


def shrikewing_hurt(rng):
    d = 0.32
    return shrike_cry(rng, d, 1900, 1100, 0.5, 0.5, 0.08) * env(d, 0.005, 0.2)


def shrikewing_death(rng):
    d = 1.5
    x = shrike_cry(rng, d, 1700, 380, 0.4, 0.6, 0.06) * env(d, 0.01, 1.0)
    return x + place(np.zeros(len(x)), lowpass(noise(0.4, rng), 600) * decay(0.4, 0.06), 1.1)


def shrikewing_screech(rng):
    d = 1.1
    a = shrike_cry(rng, d, 2100, 3000, 0.6, 1.5, 0.05)
    b = shrike_cry(rng, d, 2180, 3120, 0.3, 1.5, 0.05)   # a slightly detuned second voice: harsh beating
    return drive(a + 0.8 * b, 1.5) * env(d, 0.08, 0.35)


def shrikewing_flap(rng):
    d = 0.4
    x = lowpass(noise(d, rng), 700) + 0.6 * brown(d, rng)
    return x * env(d, 0.06, 0.3, curve=3) * (1 + 0.3 * np.sin(2 * np.pi * 18 * t_(d)))


def matriarch_voice(rng, d, f0, f1, power=1.0, grit=0.4):
    """A huge insect voice: a rough low saw through chitinous formants, with clicking undertone."""
    v = drive(osc(glide(f0, f1, power=power), d, 'saw', rng=rng, jitter=0.07), 3)
    v = formant(v, [(180, 1.0), (450, 0.8), (1100, 0.45), (2600, 0.2)], 0.3)
    clicks = (rng.random(int(d * SR)) < 0.0015) * rng.standard_normal(int(d * SR))
    return v + grit * band(clicks, 1500, 4000)


def matriarch_ambient(rng):
    d = 2.2
    x = matriarch_voice(rng, d, 48, 42, grit=0.8) * env(d, 0.4, 1.0) * (0.7 + 0.3 * np.sin(2 * np.pi * 1.6 * t_(d)))
    return x


def matriarch_ambient2(rng):
    d = 1.8
    x = np.zeros(int(d * SR))
    at = 0.05
    while at < d - 0.1:
        x = place(x, click(rng.uniform(900, 1600), rng, 0.06, 0.01) * rng.uniform(0.5, 1.0), at)
        at += rng.uniform(0.07, 0.14)
    return x + 0.6 * matriarch_voice(rng, d, 40, 52, grit=0.2) * env(d, 0.3, 0.8)


def matriarch_hurt(rng):
    d = 0.7
    return matriarch_voice(rng, d, 120, 70, 0.6, 0.6) * env(d, 0.01, 0.45) + band(noise(d, rng), 1000, 4000) * decay(d, 0.05)


def matriarch_hurt2(rng):
    d = 0.6
    return matriarch_voice(rng, d, 100, 80, 1.0, 0.8) * env(d, 0.01, 0.4) + band(noise(d, rng), 800, 3000) * decay(d, 0.04)


def matriarch_death(rng):
    d = 3.0
    x = matriarch_voice(rng, d, 140, 28, 0.5, 0.6) * env(d, 0.02, 2.2)
    for at in (1.6, 2.1, 2.35):   # the body hits the floor, the chains rattle down
        x = place(x, (1.2 * osc(glide(60, 35), 0.6) + lowpass(noise(0.6, rng), 700)) * decay(0.6, 0.12), at)
    for i in range(14):
        at = 1.7 + i * 0.07 + rng.uniform(0, 0.03)
        x = place(x, click(rng.uniform(3000, 5000), rng, 0.05, 0.01) * 0.6 * (1 - i / 14), at)
    return x


def matriarch_roar(rng):
    d = 2.0
    v = matriarch_voice(rng, d, 55, 75, 0.4, 0.3) + 0.6 * matriarch_voice(rng, d, 82, 110, 0.4, 0.0)
    breath = sweep_band(noise(d, rng), 300, 1500, 600, 3000) * 0.5
    return drive((v + breath) * env(d, 0.25, 0.8), 1.5)


def matriarch_brood(rng):
    d = 2.4
    x = 0.8 * lowpass(brown(d, rng), 250) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.0 * t_(d))) ** 2
    at = 0.0
    while at < d - 0.1:   # wet bubbles: short rising chirps
        dur = rng.uniform(0.03, 0.08)
        f = rng.uniform(250, 700)
        x = place(x, osc(glide(f, f * 2.2), dur) * env(dur, 0.002, dur * 0.7) * rng.uniform(0.2, 0.6), at)
        at += rng.uniform(0.02, 0.07)
    return x * env(d, 0.2, 0.6)


def matriarch_sweep_tell(rng):
    d = 1.0
    x = np.zeros(int(d * SR))
    for f, g in ((1180, 1.0), (2730, 0.6), (4120, 0.4), (5960, 0.25)):   # inharmonic, metallic partials
        x += g * osc(glide(f * 0.9, f * 1.05), d) * env(d, 0.4, 0.2)
    scrape = sweep_band(noise(d, rng), 2000, 5000, 3500, 8000) * env(d, 0.5, 0.2)
    return x + 0.6 * scrape


def matriarch_sweep(rng):
    d = 0.6
    return sweep_band(noise(d, rng), 300, 900, 1500, 5000) * env(d, 0.12, 0.35, hold=0.2)


def matriarch_spit(rng):
    d = 0.55
    gurgle = lowpass(brown(d, rng), 600) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t_(d)))
    hiss = band(noise(d, rng), 1500, 6000) * env(d, 0.15, 0.3)
    return (gurgle + 0.7 * hiss) * env(d, 0.05, 0.25)


def matriarch_slam(rng):
    d = 1.4
    thud = 1.5 * osc(glide(70, 30), d) * decay(d, 0.25)
    crack = lowpass(noise(d, rng), 1200) * decay(d, 0.08)
    rumble = lowpass(brown(d, rng), 150) * decay(d, 0.5)
    return thud + crack + rumble


def matriarch_acid(rng):
    d = 0.9
    sizzle = band(noise(d, rng), 3000, 9000) * env(d, 0.01, 0.7)
    pops = (rng.random(int(d * SR)) < 0.004) * rng.standard_normal(int(d * SR))
    splat = lowpass(noise(d, rng), 900) * decay(d, 0.04)
    return 0.6 * sizzle + band(pops, 1500, 6000) * env(d, 0.01, 0.6) + splat



# ------------------------------------------------------------------------------------------------ the Astral Abyss
def bell(f, d, rng, partials=((1, 1.0), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)), tau=0.6, detune=0.002):
    """A glassy struck tone: inharmonic partials, each decaying faster the higher it is."""
    x = np.zeros(int(d * SR))
    for k, g in partials:
        x += g * osc(f * k * (1 + rng.uniform(-detune, detune)), d) * decay(d, tau / k ** 0.5)
    return x


def shimmer(d, rng, lo=3000, hi=9000, density=0.004):
    """Sparkle: sparse high pings."""
    x = np.zeros(int(d * SR))
    hits = np.nonzero(rng.random(int(d * SR)) < density / 40)[0]
    for i in hits:
        f = rng.uniform(lo, hi)
        x = place(x, osc(f, 0.08) * decay(0.08, 0.015) * rng.uniform(0.2, 0.6), i / SR)
    return x


def hum(f, d, rng, beat=0.7):
    """A low drone of two slightly detuned tones (a slow beating), softly driven."""
    return drive(osc(f, d, 'tri', rng=rng, jitter=0.01) + osc(f * 1.007 + beat, d) + 0.4 * osc(f * 2.01, d), 1.4)


def mite_ambient(rng):
    d = 1.4
    wings = band(noise(d, rng), 180, 520) * (0.6 + 0.4 * np.sin(2 * np.pi * 34 * t_(d)))
    return 0.5 * wings * env(d, 0.2, 0.5) + 0.7 * osc(glide(880, 990), d, vib=0.02, vib_rate=5) * env(d, 0.3, 0.6) * 0.4 + shimmer(d, rng)


def mite_hurt(rng):
    d = 0.35
    return bell(1320, d, rng, tau=0.12) + osc(glide(1500, 700), d, 'tri') * env(d, 0.005, 0.25) * 0.6


def mite_death(rng):
    d = 0.9
    x = osc(glide(1400, 220, power=0.6), d, 'tri') * env(d, 0.005, 0.7) * 0.6
    for i in range(6):   # the lantern shatters
        x = place(x, bell(rng.uniform(2000, 4000), 0.4, rng, tau=0.08) * (1 - i / 7), 0.1 + i * 0.05)
    return x


def mite_tell(rng):
    d = 0.75
    swell = osc(glide(500, 1600, power=2.0), d, 'sine', vib=0.03, vib_rate=14) * env(d, 0.4, 0.1)
    return swell + 0.4 * band(noise(d, rng), 2000, 6000) * env(d, 0.6, 0.1) ** 2


def mite_spit(rng):
    d = 0.45
    x = osc(glide(1800, 400, power=0.5), d, 'tri') * decay(d, 0.08)
    return x + 0.6 * sweep_band(noise(d, rng), 3000, 6000, 600, 1500, 8) * decay(d, 0.1)


def warden_ambient(rng):
    d = 2.0
    x = 0.6 * hum(55, d, rng) * env(d, 0.4, 0.6)
    at = 0.1
    while at < d - 0.1:   # gears: regular ticks
        x = place(x, click(rng.uniform(2500, 3200), rng, 0.04, 0.004) * 0.5, at)
        at += 0.25
    return x


def warden_hurt(rng):
    d = 0.6
    return bell(310, d, rng, ((1, 1.0), (2.41, 0.7), (3.9, 0.5), (6.2, 0.3)), tau=0.25) + band(noise(d, rng), 1500, 5000) * decay(d, 0.03)


def warden_death(rng):
    d = 2.6
    x = hum(70, d, rng) * env(d, 0.01, 2.0) * np.interp(t_(d), [0, d], [1, 0.2])
    x = place(x, 0.9 * bell(180, 1.8, rng, tau=0.8), 0.0)
    for at in (0.9, 1.3, 1.5):   # the rings drop
        x = place(x, bell(rng.uniform(250, 420), 1.0, rng, tau=0.4) * 0.7, at)
    return x


def warden_tell(rng):
    d = 1.0
    rising = osc(glide(220, 880, power=1.5), d, 'saw') * env(d, 0.6, 0.05)
    return 0.5 * lowpass(rising, 3000) + 0.5 * hum(110, d, rng) * env(d, 0.1, 0.1)


def warden_beam(rng):
    d = 1.5
    core = osc(440, d, 'saw', vib=0.01, vib_rate=30) + osc(660, d, 'square') * 0.3
    return lowpass(drive(core, 2), 4000) * env(d, 0.02, 0.3) * 0.7 + 0.4 * band(noise(d, rng), 4000, 9000) * env(d, 0.02, 0.3)


def warden_stall(rng):
    d = 1.1
    return place(osc(glide(440, 60, power=0.5), d, 'saw') * env(d, 0.005, 0.8) * 0.6, click(1800, rng, 0.08, 0.02), 0.0)


def warden_recover(rng):
    d = 0.7
    return place(osc(glide(80, 330, power=0.7), d, 'tri') * env(d, 0.05, 0.2), 0.5 * click(2600, rng, 0.05, 0.006), 0.6)


def warden_pulse(rng):
    d = 1.0
    boom = osc(glide(120, 40), d) * decay(d, 0.25)
    return boom + 0.6 * sweep_band(noise(d, rng), 200, 800, 1500, 5000, 10) * decay(d, 0.2)


def leviathan_voice(rng, d, f0, f1, power=1.0):
    """A whale-like song through a crystalline resonance: slow sine glides, a hollow octave, glassy formants."""
    v = osc(glide(f0, f1, power=power), d, 'sine', vib=0.015, vib_rate=3.5, rng=rng, jitter=0.02)
    v += 0.5 * osc(glide(f0 * 2.02, f1 * 2.02, power=power), d, 'tri')
    v += 0.25 * osc(glide(f0 * 3.01, f1 * 3.01, power=power), d, 'saw')
    return formant(drive(v, 1.6), [(400, 1.0), (900, 0.6), (2400, 0.35)], 0.35) + 0.3 * v


def leviathan_ambient(rng):
    d = 3.2
    return leviathan_voice(rng, d, 110, 165, 0.5) * env(d, 0.6, 1.4) + 0.3 * shimmer(d, rng, 2000, 6000)


def leviathan_hurt(rng):
    d = 0.9
    return leviathan_voice(rng, d, 260, 150, 0.7) * env(d, 0.01, 0.6) + 0.5 * bell(900, d, rng, tau=0.15)


def leviathan_death(rng):
    d = 4.5
    x = leviathan_voice(rng, d, 220, 45, 0.6) * env(d, 0.05, 3.2)
    for i in range(18):   # the scales fall like glass
        x = place(x, bell(rng.uniform(1200, 3600), 0.6, rng, tau=0.15) * 0.4 * (1 - i / 20), 1.5 + i * 0.12 + rng.uniform(0, 0.05))
    return x + 0.5 * hum(40, d, rng) * env(d, 1.0, 2.0)


def leviathan_roar(rng):
    d = 2.6
    v = leviathan_voice(rng, d, 90, 140, 0.4) + 0.7 * leviathan_voice(rng, d, 134, 210, 0.4)
    breath = sweep_band(noise(d, rng), 200, 1200, 800, 4000) * 0.5
    return drive((v + breath) * env(d, 0.3, 0.9), 1.8)


def leviathan_beam_tell(rng):
    d = 1.6
    rising = sum(osc(glide(f, f * 3, power=2.0), d, 'sine') * (0.6 ** i) for i, f in enumerate((220, 331, 440)))
    return rising * env(d, 1.2, 0.05) + 0.5 * shimmer(d, rng, 4000, 10000, 0.02) * env(d, 1.0, 0.1)


def leviathan_beam(rng):
    d = 2.8
    core = drive(osc(150, d, 'saw', vib=0.02, vib_rate=8) + osc(301, d, 'saw') * 0.6, 2.5)
    return lowpass(core, 2500) * env(d, 0.03, 0.4) * 0.6 + 0.5 * band(noise(d, rng), 2000, 7000) * env(d, 0.03, 0.4)


def leviathan_well(rng):
    d = 1.8
    suck = osc(glide(60, 25, power=0.6), d) * env(d, 0.2, 0.4) * 1.2
    return suck + 0.6 * sweep_band(noise(d, rng), 2000, 6000, 100, 400, 16) * env(d, 0.1, 0.4)


def leviathan_pass(rng):
    d = 1.6
    whoosh = sweep_band(noise(d, rng), 200, 600, 1200, 3000, 16) * np.hanning(int(d * SR))
    return whoosh + 0.4 * leviathan_voice(rng, d, 180, 120) * np.hanning(int(d * SR))


def leviathan_summon(rng):
    d = 1.8
    x = leviathan_voice(rng, d, 300, 420, 0.5) * env(d, 0.1, 0.8) * 0.7
    for i in range(5):
        x = place(x, bell(660 * (1.25 ** i), 0.8, rng, tau=0.3) * 0.5, 0.2 + i * 0.18)
    return x


def leviathan_slam(rng):
    d = 1.6
    boom = 1.4 * osc(glide(70, 28), d) * decay(d, 0.35) + lowpass(noise(d, rng), 600) * decay(d, 0.2)
    return drive(boom, 1.5) + 0.5 * bell(420, d, rng, tau=0.5)


def rift_open(rng):
    d = 4.0
    tones = sum(osc(f, d, 'sine', vib=0.004, vib_rate=0.5 + i) * g for i, (f, g) in enumerate(((110, 1.0), (165, 0.7), (220, 0.6), (330, 0.4), (440, 0.3))))
    swell = tones * env(d, 1.8, 1.6)
    rush = sweep_band(noise(d, rng), 100, 400, 2000, 8000, 20) * env(d, 2.5, 1.0) * 0.6
    return swell + rush + 0.4 * shimmer(d, rng, 3000, 9000, 0.02) * env(d, 2.0, 1.0)


def abyss_ambient(rng):
    d = 8.0
    x = 0.8 * hum(41, d, rng, 0.3) + 0.4 * hum(61.5, d, rng, 0.2)
    x = lowpass(x, 400) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.125 * t_(d)))
    wind = sweep_band(noise(d, rng), 300, 900, 600, 1600, 32) * 0.3
    return (x + wind) * env(d, 1.5, 1.5) + 0.25 * shimmer(d, rng, 2500, 7000, 0.006)


ABYSS = ['mite_ambient', 'mite_hurt', 'mite_death', 'mite_tell', 'mite_spit', 'warden_ambient', 'warden_hurt', 'warden_death',
         'warden_tell', 'warden_beam', 'warden_stall', 'warden_recover', 'warden_pulse', 'leviathan_ambient', 'leviathan_hurt',
         'leviathan_death', 'leviathan_roar', 'leviathan_beam_tell', 'leviathan_beam', 'leviathan_well', 'leviathan_pass',
         'leviathan_summon', 'leviathan_slam', 'rift_open', 'abyss_ambient']


RECIPES = {
    'gnashback/ambient': gnashback_ambient,
    'gnashback/hurt': gnashback_hurt,
    'gnashback/death': gnashback_death,
    'gnashback/bite': gnashback_bite,
    'gnashback/scrape': gnashback_scrape,
    'gnashback/charge': gnashback_charge,
    'gnashback/impact': gnashback_impact,
    'shrikewing/ambient1': shrikewing_ambient,
    'shrikewing/ambient2': shrikewing_ambient2,
    'shrikewing/hurt': shrikewing_hurt,
    'shrikewing/death': shrikewing_death,
    'shrikewing/screech': shrikewing_screech,
    'shrikewing/flap': shrikewing_flap,
    'matriarch/ambient1': matriarch_ambient,
    'matriarch/ambient2': matriarch_ambient2,
    'matriarch/hurt1': matriarch_hurt,
    'matriarch/hurt2': matriarch_hurt2,
    'matriarch/death': matriarch_death,
    'matriarch/roar': matriarch_roar,
    'matriarch/brood': matriarch_brood,
    'matriarch/sweep_tell': matriarch_sweep_tell,
    'matriarch/sweep': matriarch_sweep,
    'matriarch/spit': matriarch_spit,
    'matriarch/slam': matriarch_slam,
    'matriarch/acid': matriarch_acid,
}
RECIPES.update({'abyss/' + n: globals()[n] for n in ABYSS})


def render(name):
    rng = np.random.default_rng(sum(map(ord, name)) * 7919)
    return fade(norm(RECIPES[name](rng)))


def write_ogg(x, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        tmp = f.name
    with wave.open(tmp, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libvorbis', '-q:a', '4', path], check=True)
    os.unlink(tmp)


def sheet(sounds, path):
    from PIL import Image, ImageDraw
    rows = []
    for name, x in sounds:
        n = 1024
        hop = 256
        frames = [np.abs(np.fft.rfft(x[i:i + n] * np.hanning(n)))[:n // 2] for i in range(0, max(1, len(x) - n), hop)]
        s = 20 * np.log10(np.array(frames).T + 1e-6)
        s = np.clip((s - s.max() + 70) / 70, 0, 1)[::-1]
        img = Image.fromarray((s * 255).astype('uint8')).resize((min(900, len(frames) * 3), 160))
        rows.append((name, img, len(x) / SR))
    W, H = 1100, 180 * len(rows)
    out = Image.new('RGB', (W, H), (12, 12, 16))
    dr = ImageDraw.Draw(out)
    for i, (name, img, dur) in enumerate(rows):
        out.paste(Image.merge('RGB', (img, img.point(lambda v: v * 0.6), img.point(lambda v: 255 - v if v else 0))), (190, i * 180 + 10))
        dr.text((8, i * 180 + 70), f'{name}\n{dur:.2f}s  0-22kHz', fill=(230, 230, 230))
    out.save(path)


def main():
    args = sys.argv[1:]
    sheet_path = None
    if '--sheet' in args:
        sheet_path = args[args.index('--sheet') + 1]
        del args[args.index('--sheet'):args.index('--sheet') + 2]
    out = args[0] if args else OUT
    done = []
    only = os.environ.get('ONLY', '')
    for name in RECIPES:
        if not name.startswith(only):
            continue
        x = render(name)
        write_ogg(x, os.path.join(out, name + '.ogg'))
        done.append((name, x))
        print(f'{name}: {len(x) / SR:.2f}s')
    if sheet_path:
        sheet(done, sheet_path)


if __name__ == '__main__':
    main()
