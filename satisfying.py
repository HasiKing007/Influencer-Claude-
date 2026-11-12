"""Rendert "oddly satisfying"-Reels komplett selbst: Animation in Python, Sound synthetisiert.

Kein fremdes Material: jedes Bild und jeder Ton entsteht hier im Code.
Stil: ruhig, weiche Pastellfarben, natuerliche Bewegung (echte Pendel-/Roll-/Kipp-Physik).
Jede Szene ist ein nahtloser Endlos-Loop: das letzte Bild geht exakt in das erste ueber, der Ton auch.

Aufruf:  python satisfying.py <szene> [seed] [ausgabe.mp4]
"""
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
S = 2                      # Supersampling fuer glatte Kanten
RATE = 44100
CX, CY = W / 2, 1040
BOLD = os.path.join(ROOT, "fonts", "DejaVuSansCondensed-Bold.ttf")

PALETTES = [  # (Hintergrund oben, unten)
    ((248, 231, 226), (238, 212, 216)),
    ((226, 238, 248), (208, 222, 242)),
    ((234, 242, 226), (214, 230, 208)),
    ((241, 232, 250), (222, 211, 242)),
    ((250, 240, 222), (240, 224, 200)),
]
COLORS = [(255, 138, 128), (255, 190, 110), (120, 210, 175), (150, 160, 255),
          (255, 150, 196), (110, 195, 240), (245, 210, 95)]
TEXT = (52, 46, 72)


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def smooth(t):
    """Weiches Anfahren und Abbremsen (ease-in-out)."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def background(top, bottom):
    y = np.linspace(0, 1, H * S)[:, None, None]
    top, bot = np.array(top, float), np.array(bottom, float)
    grad = top + (bot - top) * y
    xs = np.linspace(-1, 1, W * S)[None, :, None]
    ys = np.linspace(-1, 1, H * S)[:, None, None]
    vign = 1 - 0.10 * np.clip(xs ** 2 + (ys * 0.8) ** 2, 0, 1)
    arr = np.broadcast_to(grad * vign, (H * S, W * S, 3)).astype(np.uint8)
    return Image.fromarray(arr)


class Pen:
    """Zeichnet in 1x-Koordinaten auf eine S-fach vergroesserte Leinwand."""

    def __init__(self, img, shadow):
        self.img, self.d, self.shadow = img, ImageDraw.Draw(img), shadow

    def circle(self, x, y, r, fill=None, outline=None, width=0):
        self.d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S),
                       fill=fill, outline=outline, width=int(width * S))

    def rect(self, x0, y0, x1, y1, fill, radius=0):
        if radius:
            self.d.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), radius=radius * S, fill=fill)
        else:
            self.d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill)

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def line(self, pts, fill, width):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(width * S), joint="curve")

    def ball_shadow(self, x, y, r):
        self.circle(x + r * 0.28, y + r * 0.42, r * 1.02, fill=self.shadow)

    def ball(self, x, y, r, col, spin=None):
        self.circle(x, y, r, fill=col)
        self.circle(x + r * 0.08, y + r * 0.1, r * 0.86, fill=mix(col, (0, 0, 0), 0.07))
        self.circle(x - r * 0.05, y - r * 0.05, r * 0.8, fill=col)
        if spin is not None:  # kleiner Punkt zeigt das Rollen
            self.circle(x + math.cos(spin) * r * 0.55, y + math.sin(spin) * r * 0.55, r * 0.16,
                        fill=mix(col, (255, 255, 255), 0.55))
        self.circle(x - r * 0.33, y - r * 0.36, r * 0.24, fill=mix(col, (255, 255, 255), 0.6))

    def block(self, x0, y0, x1, y1, col, radius=8):
        self.rect(x0, y0, x1, y1, col, radius)
        self.rect(x0 + 6, y0 + 4, x1 - 6, y0 + 10, mix(col, (255, 255, 255), 0.4), 3)
        self.rect(x0 + 4, y1 - 9, x1 - 4, y1 - 3, mix(col, (0, 0, 0), 0.10), 3)


# ---------------------------------------------------------------- Sound

def _t(dur):
    return np.arange(int(dur * RATE)) / RATE


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def lowpass(sig, fc):
    spec = np.fft.rfft(sig)
    f = np.fft.rfftfreq(len(sig), 1 / RATE)
    spec *= 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(spec, len(sig))


def highpass(sig, fc):
    spec = np.fft.rfft(sig)
    f = np.fft.rfftfreq(len(sig), 1 / RATE)
    spec *= 1 - 1 / (1 + (f / fc) ** 4)
    return np.fft.irfft(spec, len(sig))


def snd_pluck(f, dur=1.4, bright=1.0):
    """Weiche Kalimba/Marimba-Glocke."""
    t = _t(dur)
    att = np.minimum(1, t / 0.004)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 3.2)
    s += 0.30 * bright * np.sin(2 * np.pi * 2.0 * f * t) * np.exp(-t * 7)
    s += 0.12 * bright * np.sin(2 * np.pi * 4.07 * f * t) * np.exp(-t * 14)
    s += 0.05 * np.sin(2 * np.pi * f * 1.003 * t) * np.exp(-t * 2)
    return s * att


def snd_tick(f, rng):
    t = _t(0.03)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 260)
    s += 0.5 * rng.standard_normal(len(t)) * np.exp(-t * 900)
    return highpass(s, 1500)


def snd_tok(f=900):
    """Holziges Klacken."""
    t = _t(0.12)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t * 55)
    s += 0.6 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 90)
    s += 0.8 * np.sin(2 * np.pi * 95 * t * (1 + 0.6 * np.exp(-t * 40))) * np.exp(-t * 30)
    return s


def snd_pop(rng):
    t = _t(0.18)
    f = 180 + 900 * np.exp(-t * 45)
    s = np.sin(2 * np.pi * np.cumsum(f) / RATE) * np.exp(-t * 22)
    s += 0.35 * lowpass(rng.standard_normal(len(t)), 3000) * np.exp(-t * 60)
    return s


def snd_crunch(dur, rng, density=5000):
    """ASMR-Knistern: viele winzige Koernchen-Klicks (wie kinetischer Sand / Seife)."""
    n = int(dur * RATE)
    s = np.zeros(n + 400)
    count = int(dur * density)
    pos = rng.integers(0, n, count)
    amp = rng.random(count) ** 3
    grain = np.exp(-np.arange(120) / 14) * rng.standard_normal(120)
    for p, a in zip(pos, amp):
        s[p:p + 120] += a * grain
    s = highpass(s[:n], 900)
    env = np.minimum(1, np.arange(n) / (0.01 * RATE)) * np.minimum(1, (n - np.arange(n)) / (0.04 * RATE))
    s = s * env
    return s / (np.std(s) * 3.5 + 1e-9)


def snd_whoosh(dur, rng):
    n = int(dur * RATE)
    s = lowpass(rng.standard_normal(n), 900)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return s * env


def snd_thud():
    t = _t(0.25)
    return np.sin(2 * np.pi * (55 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 18)


class Mixer:
    """Kreisfoermiger Puffer: was ueber das Ende hinausklingt, kommt am Anfang wieder -> nahtloser Loop."""

    def __init__(self, dur, seed):
        self.n = int(round(dur * RATE))
        self.buf = np.zeros((2, self.n))
        self.dur = dur
        self.rng = np.random.default_rng(seed)

    def add(self, t, sig, gain=0.5, pan=0.0):
        """pan -1 (links) .. 1 (rechts); x-Position im Bild -> Stereo, wirkt wie ASMR."""
        s0 = int(round((t % self.dur) * RATE))
        a = (pan + 1) * math.pi / 4
        idx = (s0 + np.arange(len(sig))) % self.n
        np.add.at(self.buf[0], idx, sig * gain * math.cos(a))
        np.add.at(self.buf[1], idx, sig * gain * math.sin(a))

    def master(self):
        ir_t = _t(1.4)
        out = np.zeros_like(self.buf)
        for ch in range(2):
            ir = self.rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.35)
            ir = lowpass(ir, 4000)
            ir /= np.sqrt(np.sum(ir ** 2))
            wet = np.fft.irfft(np.fft.rfft(self.buf[ch]) * np.fft.rfft(ir, self.n), self.n)  # zyklisch
            out[ch] = self.buf[ch] + 0.25 * wet
        peak = np.percentile(np.abs(out), 99.97) or 1
        return np.tanh(out / peak * 1.2) * 0.84


def write_wav(path, stereo):
    data = (np.clip(stereo.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())


def pan_of(x):
    return max(-1.0, min(1.0, (x - CX) / (W / 2) * 0.8))


# Akkordfolge I-V-vi-IV in C-Dur als Arpeggio (generisch, kein bestehendes Lied)
CHORDS = [(60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)]


def arpeggio(i, octave=12):
    chord = CHORDS[(i // 6) % 4]
    step = i % 6
    pattern = [0, 1, 2, 3, 2, 1]
    k = pattern[step]
    note = chord[k % 3] + 12 * (k // 3) + octave
    return note


PENTA = [0, 2, 4, 7, 9]


def penta(i, base=60):
    return base + 12 * (i // 5) + PENTA[i % 5]


class Scene:
    name = ""
    hook = ""
    period = 12.0          # Loop-Laenge in Sekunden
    thumb = 0.5            # Anteil der Laenge fuer das Titelbild

    def __init__(self, seed):
        self.seed = seed
        self.rng = random.Random(seed)
        top, bottom = self.rng.choice(PALETTES)
        self.bg_top, self.bg_bottom = top, bottom
        self.shadow = mix(bottom, (40, 30, 60), 0.16)
        self.colors = COLORS[:]
        self.rng.shuffle(self.colors)
        self.base = background(top, bottom)

    def pen(self):
        img = self.base.copy()
        return img, Pen(img, self.shadow)

    def frame(self, t):
        raise NotImplementedError

    def sound(self, mx):
        raise NotImplementedError


class Pendulum(Scene):
    """Pendelwelle von oben: 12 Pendel mit leicht verschiedener Laenge, alle 15 s wieder in einer Linie."""
    name, hook = "pendulum", "Watch them line up again"
    period = 15.0
    thumb = 0.5
    N, R, AMP = 12, 27, 330

    def setup(self):
        self.xs = [150 + i * (780 / (self.N - 1)) for i in range(self.N)]
        self.ns = [7 + i for i in range(self.N)]     # Schwingungen pro Loop

    def frame(self, t):
        if not hasattr(self, "xs"):
            self.setup()
        img, pen = self.pen()
        top, bot = CY - self.AMP - 50, CY + self.AMP + 50
        for x in self.xs:
            pen.rect(x - 3, top, x + 3, bot, mix(self.bg_bottom, (40, 30, 60), 0.08), 3)
        pen.rect(110, top - 30, 970, top - 14, mix(self.bg_bottom, (40, 30, 60), 0.12), 8)
        pen.rect(110, bot + 14, 970, bot + 30, mix(self.bg_bottom, (40, 30, 60), 0.12), 8)
        ys = [CY - self.AMP * math.cos(2 * math.pi * n * t / self.period) for n in self.ns]
        for x, y in zip(self.xs, ys):
            pen.ball_shadow(x, y, self.R)
        for i, (x, y) in enumerate(zip(self.xs, ys)):
            pen.ball(x, y, self.R, self.colors[i % len(self.colors)])
        return img

    def sound(self, mx):
        self.setup()
        for i, n in enumerate(self.ns):
            f = midi(penta(i, 60))
            for k in range(n):   # jedes Pendel spielt seinen Ton am oberen Umkehrpunkt
                mx.add(k * self.period / n, snd_pluck(f, 1.6, 0.6), 0.16, pan_of(self.xs[i]))


class Marbles(Scene):
    """Murmeln rollen gemaechlich ueber eine Zickzack-Bahn (echte Roll-Physik), endloser Strom."""
    name, hook = "marbles", "This could run forever"
    period = 12.5
    thumb = 0.5
    R = 22
    SPACING = 1.25        # Sekunden zwischen zwei Murmeln (period ist ein Vielfaches)
    RAMPS = 5
    TOP_Y, GAP_Y, X0, X1 = 620, 185, 205, 875
    SLOPE = math.radians(7)
    G = 2000.0

    def ramp(self, k):
        """Bahn k als (x_start, y_start, x_end, y_end) entlang der Rollrichtung."""
        y0 = self.TOP_Y + k * self.GAP_Y
        dy = (self.X1 - self.X0) * math.tan(self.SLOPE)
        if k % 2 == 0:
            return self.X0, y0, self.X1, y0 + dy
        return self.X1, y0, self.X0, y0 + dy

    def simulate(self):
        """Bahn einer einzelnen Murmel; alle anderen laufen dieselbe Bahn zeitversetzt."""
        dt = 1 / 600
        pts, events, rolls = [], [], []
        x, y = self.X0, 400.0                 # faellt aus dem Rohr auf die erste Bahn
        vy, t, k, spin = 0.0, 0.0, 0, 0.0
        acc = self.G * math.sin(self.SLOPE) * 5 / 7
        while True:
            if k >= self.RAMPS:
                break
            xs, ys, xe, ye = self.ramp(k)
            surface = ys - self.R / math.cos(self.SLOPE)
            # Fallen bis zur Bahn, mit kleinem Huepfer
            bounced = 0
            while True:
                vy += self.G * dt
                y += vy * dt
                t += dt
                if y >= surface:
                    y = surface
                    if bounced == 0 and vy > 120:
                        events.append((t, "land", k, x, vy))
                        vy = -vy * 0.28
                        bounced = 1
                    else:
                        break
                pts.append((t, x, y, spin))
            d = 1 if xe > xs else -1
            s, v = 0.0, 0.0
            L = abs(xe - xs) / math.cos(self.SLOPE)
            t_roll0 = t
            while s < L:
                v += acc * dt
                s += v * dt
                t += dt
                spin += d * v * dt / self.R
                x = xs + d * s * math.cos(self.SLOPE)
                y = surface + s * math.sin(self.SLOPE)
                pts.append((t, x, y, spin))
            rolls.append((t_roll0, t, k, d))
            # Loch am Ende: Murmel faellt senkrecht durch
            vy = v * math.sin(self.SLOPE)
            k += 1
        while y < H + 60:   # letzte Bahn: ab in das Rohr nach unten
            vy += self.G * dt
            y += vy * dt
            t += dt
            pts.append((t, x, y, spin))
        self.track = np.array(pts)
        self.events, self.rolls, self.life = events, rolls, t

    def pos(self, tau):
        i = int(np.searchsorted(self.track[:, 0], tau))
        i = min(max(i, 0), len(self.track) - 1)
        return self.track[i, 1:]

    def frame(self, t):
        if not hasattr(self, "track"):
            self.simulate()
        img, pen = self.pen()
        dark = mix(self.bg_bottom, (40, 30, 60), 0.22)
        for k in range(self.RAMPS):
            xs, ys, xe, ye = self.ramp(k)
            d = 1 if xe > xs else -1
            back = xs - d * 40
            pen.line([(back + 10, ys + 22), (xe - d * (self.R + 8) + 10, ye + 22)], self.shadow, 18)
            pen.line([(back, ys), (xe - d * (self.R + 8), ye)], dark, 16)
            pen.line([(back, ys - 3), (xe - d * (self.R + 8), ye - 3)], mix(dark, (255, 255, 255), 0.25), 5)
            pen.rect(xe + d * (self.R + 4) - 6, ye - 60, xe + d * (self.R + 4) + 6, ye + 8, dark, 4)  # Anschlag
        marbles = []
        for j in range(-int(self.life / self.SPACING) - 2, 1):
            tau = t - j * self.SPACING
            if 0 <= tau < self.life:
                marbles.append((j, self.pos(tau)))
        for j, (x, y, spin) in marbles:
            pen.ball_shadow(x, y, self.R)
        for j, (x, y, spin) in marbles:
            pen.ball(x, y, self.R, self.colors[j % 5], spin)   # 5 teilt die Murmeln pro Loop -> Loop passt
        # Rohre vor den Murmeln: oben kommen sie heraus, unten verschwinden sie
        tube = mix(dark, (255, 255, 255), 0.35)
        x0 = self.X0
        pen.rect(x0 - self.R - 12 + 12, 370 + 12, x0 + self.R + 12 + 12, 530 + 12, self.shadow, 8)
        pen.rect(x0 - self.R - 12, 370, x0 + self.R + 12, 530, tube, 8)
        pen.rect(x0 - self.R - 16, 516, x0 + self.R + 16, 534, dark, 6)
        xe, ye = self.ramp(self.RAMPS - 1)[2:]
        pen.rect(xe - self.R - 12 + 12, ye + 90 + 12, xe + self.R + 12 + 12, H + 20, self.shadow, 8)
        pen.rect(xe - self.R - 12, ye + 90, xe + self.R + 12, H + 20, tube, 8)
        pen.rect(xe - self.R - 16, ye + 86, xe + self.R + 16, ye + 104, dark, 6)
        return img

    def sound(self, mx):
        self.simulate()
        rng = mx.rng
        track = np.zeros(int((self.life + 2) * RATE))
        for (t0, t1, k, d) in self.rolls:   # leises Rollgeraeusch, lauter mit Tempo
            a, b = int(t0 * RATE), int(t1 * RATE)
            noise = lowpass(rng.standard_normal(b - a), 350)
            ramp = np.linspace(0.15, 1.0, b - a) ** 0.7
            track[a:b] += noise * ramp * 0.5
        clicks = []
        for (t, kind, k, x, vy) in self.events:
            clicks.append((t, k, x, min(1.0, vy / 900)))
        for j in range(int(round(self.period / self.SPACING))):
            t0 = j * self.SPACING
            mx.add(t0, track, 0.10, 0.0)
            for (t, k, x, strength) in clicks:
                mx.add(t0 + t, snd_tok(midi(penta(k + 2 * (j % 2), 72))), 0.22 * (0.5 + strength), pan_of(x))
                mx.add(t0 + t, snd_pluck(midi(penta(k + 2 * (j % 2), 60)), 1.2, 0.5), 0.10, pan_of(x))


class Stack(Scene):
    """Endloser Turm: jeder Block gleitet herein und landet exakt auf dem vorigen."""
    name, hook = "stack", "This tower never ends"
    P, N = 1.3, 10                   # Sekunden pro Block, Bloecke pro Loop
    period = P * N
    thumb = 0.3
    BH, BW, TOP_SCREEN = 74, 440, 1090
    LAND = 0.9                       # Landezeitpunkt innerhalb eines Blocktakts

    def land_time(self, i):
        return i * self.P + self.LAND

    def cam(self, t):
        i = math.floor((t - self.LAND) / self.P)
        q = smooth((t - self.land_time(i)) / 0.75)
        return self.BH * (i + q)

    def frame(self, t):
        t = t + 40 * self.period     # mitten im "unendlichen" Turm beginnen
        img, pen = self.pen()
        cam = self.cam(t)

        def sy(h):
            return self.TOP_SCREEN + cam - h

        last = math.floor((t - self.LAND) / self.P)    # zuletzt gelandeter Block
        boxes = []
        for i in range(last, last - 20, -1):
            y1 = sy(i * self.BH)
            if y1 - self.BH > H:
                break
            sq = 0.0
            if i == last:
                a = (t - self.land_time(i)) / 0.18
                if 0 <= a < 1:
                    sq = math.sin(math.pi * a) * 0.08
            boxes.append((i, CX, y1, sq))
        j = last + 1                 # naechster Block im Anflug
        u = t - (self.land_time(j) - 1.0)
        if u >= 0:
            side = -1 if j % 2 else 1
            if u < 0.62:
                x = CX + side * 820 * (1 - smooth(u / 0.62))
                lift = 160
            elif u < 0.75:
                x, lift = CX, 160
            else:
                x = CX
                f = min(1.0, (u - 0.75) / 0.25)
                lift = 160 * (1 - f * f)
            boxes.append((j, x, sy(j * self.BH) - lift, 0.0))
        for (i, x, y1, sq) in boxes:
            h = self.BH * (1 - sq)
            w = self.BW * (1 + sq * 0.5)
            pen.rect(x - w / 2 + 16, y1 - h + 16, x + w / 2 + 16, y1 + 16, self.shadow, 10)
        for (i, x, y1, sq) in sorted(boxes, key=lambda b: b[0]):
            h = self.BH * (1 - sq)
            w = self.BW * (1 + sq * 0.5)
            pen.block(x - w / 2, y1 - h, x + w / 2, y1 - 1, self.colors[i % 5], 10)
        return img

    def sound(self, mx):
        rng = mx.rng
        melody = [0, 2, 4, 2, 5, 4, 7, 5, 9, 7][: self.N]
        for i in range(self.N):
            t = self.land_time(i)
            mx.add(t, snd_tok(midi(penta(melody[i], 67))), 0.32, 0.0)
            mx.add(t, snd_pluck(midi(penta(melody[i], 60)), 1.4, 0.5), 0.22, 0.0)
            mx.add(t - 1.0, snd_whoosh(0.6, rng), 0.05, 0.7 if i % 2 else -0.7)


class Slice(Scene):
    """Bunter Sandblock wird in Ruhe Scheibe fuer Scheibe geschnitten; jede Scheibe kippt natuerlich ab."""
    name, hook = "slice", "That sound though..."
    KX = 470
    TOP, BOTTOM = 860, 1250
    SW = 64
    P = 1.5
    CYCLES = 8
    period = P * CYCLES
    thumb = 0.45

    def setup(self):
        rng = np.random.default_rng(self.seed)
        h = int((self.BOTTOM - self.TOP) * S)
        L = int(self.CYCLES * self.SW * S)
        tex = np.zeros((h, L, 3))
        tex[:] = self.colors[0]
        y, li = 0, 0
        xs = np.arange(L)
        while y < h:
            th = int(rng.uniform(0.08, 0.16) * h)
            c = self.colors[li % len(self.colors)]
            wav = (np.sin(xs / L * 2 * np.pi * 2 + li) * 5 * S).astype(int)   # periodisch -> Loop
            for x in range(0, L, 2):
                tex[max(0, y + wav[x]):, x:x + 2] = c      # bis unten fuellen, naechste Schicht ueberdeckt
            y += th
            li += 1
        grain = rng.standard_normal((h, L))
        tex *= (1 + 0.05 * grain)[:, :, None]
        tex = np.clip(tex, 0, 255).astype(np.uint8)
        reps = int(math.ceil((W / self.SW + 4) / self.CYCLES)) + 1
        self.tex = Image.fromarray(np.tile(tex, (1, reps, 1)))
        self.L = self.CYCLES * self.SW
        self.fall = self.simulate_fall()

    def simulate_fall(self):
        """Scheibe kippt um die Plattformkante (starrer Koerper), dann freier Fall."""
        w, h, g = self.SW, self.BOTTOM - self.TOP, 2600.0
        px, py = self.KX - w, self.BOTTOM
        I = (w * w + h * h) / 3
        th, om, dt, t = 0.0, 0.9, 1 / 600, 0.0
        out = []
        while th < math.pi / 2 - 0.25:
            rx, ry = w / 2, -h / 2
            off_x = rx * math.cos(th) + ry * math.sin(th)
            om += -g * off_x / I * dt
            th += om * dt
            t += dt
            cx = px + rx * math.cos(th) + ry * math.sin(th)
            cy = py - rx * math.sin(th) + ry * math.cos(th)
            out.append((t, cx, cy, th))
        # loesen: Schwerpunkt-Geschwindigkeit aus der Drehung
        rx, ry = w / 2, -h / 2
        vx = om * (-rx * math.sin(th) + ry * math.cos(th))
        vy = om * (-rx * math.cos(th) - ry * math.sin(th))
        cx, cy = out[-1][1], out[-1][2]
        while cy < H + 400 and t < 4:
            vy += g * dt
            cx += vx * dt
            cy += vy * dt
            th += om * dt
            t += dt
            out.append((t, cx, cy, th))
        return np.array(out)

    def frame(self, t):
        if not hasattr(self, "tex"):
            self.setup()
        img, pen = self.pen()
        P, hgt = self.P, self.BOTTOM - self.TOP
        dark = mix(self.bg_bottom, (40, 30, 60), 0.25)
        pen.rect(self.KX - self.SW + 14, self.BOTTOM + 14, W + 20, self.BOTTOM + 60, self.shadow)
        pen.rect(self.KX - self.SW, self.BOTTOM, W + 20, self.BOTTOM + 46, dark, 6)
        pen.rect(self.KX - self.SW, self.BOTTOM, W + 20, self.BOTTOM + 8, mix(dark, (255, 255, 255), 0.3), 4)
        c = math.floor(t / P)
        ph = t / P - c
        push = smooth(ph / 0.33)
        cut_done = ph >= 0.6
        stick = 0 if cut_done else self.SW * push
        edge = (c % self.CYCLES) * self.SW + self.SW      # Texturposition am Messer
        src0 = edge - stick
        vis = W - self.KX + stick + 10
        pen.rect(self.KX - stick + 14, self.TOP + 14, W + 20, self.BOTTOM, self.shadow)
        crop = self.tex.crop((int(src0 * S), 0, int((src0 + vis) * S), int(hgt * S)))
        img.paste(crop, (int((self.KX - stick) * S), int(self.TOP * S)))
        for cc in range(c - 3, c + 1):                      # abkippende Scheiben
            rel = t - (cc * P + 0.6 * P)
            if rel < 0 or rel > self.fall[-1, 0]:
                continue
            i = min(int(np.searchsorted(self.fall[:, 0], rel)), len(self.fall) - 1)
            _, cx, cy, th = self.fall[i]
            off = (cc % self.CYCLES) * self.SW
            sl = self.tex.crop((int(off * S), 0, int((off + self.SW) * S), int(hgt * S))).convert("RGBA")
            rot = sl.rotate(math.degrees(th), resample=Image.BICUBIC, expand=True)
            img.paste(rot, (int(cx * S - rot.width / 2), int(cy * S - rot.height / 2)), rot)
        for cc in range(c - 1, c + 1):                      # ein paar Kruemel an der Schnittkante
            r2 = random.Random(self.seed * 100 + cc % self.CYCLES)
            for _ in range(7):
                t0 = cc * P + 0.42 * P + r2.uniform(0, 0.25 * P)
                y0 = self.TOP + r2.uniform(0.2, 1.0) * hgt
                vx, sz = r2.uniform(-90, -20), r2.uniform(3, 6)
                age = t - t0
                if 0 <= age < 0.6:
                    x, y = self.KX - 4 + vx * age, min(self.BOTTOM - sz, y0 + 900 * age * age)
                    pen.rect(x - sz, y - sz, x + sz, y + sz, self.colors[int((y0 - self.TOP) / hgt * 6) % len(self.colors)])
        # Messer: ruhig runter, langsam durch den Block, wieder hoch
        up = self.TOP - 300
        if ph < 0.36:
            ky = up
        elif ph < 0.42:
            ky = up + 300 * smooth((ph - 0.36) / 0.06)
        elif ph < 0.6:
            ky = self.TOP + hgt * ((ph - 0.42) / 0.18)
        else:
            ky = self.BOTTOM - (self.BOTTOM - up) * smooth((ph - 0.6) / 0.4)
        bx = self.KX
        pen.poly([(bx - 5 + 10, ky - 640 + 10), (bx + 5 + 10, ky - 640 + 10), (bx + 5 + 10, ky + 10), (bx - 5 + 10, ky - 50 + 10)],
                 self.shadow)
        pen.poly([(bx - 5, ky - 640), (bx + 5, ky - 640), (bx + 5, ky), (bx - 5, ky - 50)], (205, 210, 222))
        pen.poly([(bx, ky - 640), (bx + 5, ky - 640), (bx + 5, ky)], (240, 243, 250))
        pen.rect(bx - 18, ky - 850, bx + 18, ky - 640, (70, 58, 66), 9)
        return img

    def sound(self, mx):
        P = self.P
        for c in range(self.CYCLES):
            t = c * P + 0.42 * P
            mx.add(t, snd_crunch(0.18 * P, mx.rng, 3500), 0.6, pan_of(self.KX))
            mx.add(c * P + 0.02, snd_whoosh(0.45, mx.rng), 0.05, 0.4)


SCENES = {c.name: c for c in (Pendulum, Marbles, Stack, Slice)}
CAPTIONS = {
    "pendulum": "12 pendulums, slightly different lengths. Every 15 seconds they meet again",
    "marbles": "Could watch this all day. Sound on",
    "stack": "Not one block out of place. How long did you watch?",
    "slice": "Sound on and watch it loop",
}
TAGS = "#oddlysatisfying #satisfying #asmr #satisfyingvideo #relaxing"


def hook_layer(text):
    img = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = 70
    f = ImageFont.truetype(BOLD, size)
    while d.textlength(text, font=f) > 880 and size > 44:
        size -= 4
        f = ImageFont.truetype(BOLD, size)
    d.text((W / 2, 300), text, font=f, fill=TEXT, anchor="mm")
    return img


def render(scene_name, seed, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    scene = SCENES[scene_name](seed)
    hook = hook_layer(scene.hook)
    silent, audio = out_path + ".silent.mp4", out_path + ".wav"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", silent], stdin=subprocess.PIPE)
    n = int(round(scene.period * FPS))
    for k in range(n):       # Bild n waere wieder Bild 0 -> nahtloser Loop
        img = scene.frame(k / FPS).reduce(S)
        img.paste(hook, (0, 0), hook)
        enc.stdin.write(img.tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg (Video) fehlgeschlagen")
    mx = Mixer(n / FPS, seed)
    scene.sound(mx)
    write_wav(audio, mx.master())
    tmp = out_path + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_path)
    os.remove(silent)
    os.remove(audio)
    return {"path": out_path, "duration": n / FPS, "thumb_ms": int(n / FPS * scene.thumb * 1000),
            "caption": CAPTIONS[scene_name], "tags": TAGS}


if __name__ == "__main__":
    name = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "out", f"sat_{name}.mp4")
    print(render(name, seed, out))
