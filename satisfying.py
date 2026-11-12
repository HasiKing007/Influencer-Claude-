"""Rendert "oddly satisfying"-Reels komplett selbst: Physik/Animation in Python, Sound synthetisiert.
Jede Szene endet so, wie sie beginnt (Endlos-Loop); der Ton laeuft im Ringpuffer nahtlos weiter.

Kein fremdes Material: jedes Bild und jeder Ton entsteht hier im Code.
Szenen: grow, escape, galton, slice, stack, duel (siehe SCENES).

Aufruf:  python satisfying.py <szene> [seed] [ausgabe.mp4]
"""
import colorsys
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np

import physics
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
S = 2                      # Supersampling fuer glatte Kanten
RATE = 44100
CX, CY = W / 2, 1010
BOLD = os.path.join(ROOT, "fonts", "DejaVuSansCondensed-Bold.ttf")
BG_TOP, BG_BOTTOM = (16, 14, 34), (4, 4, 12)


def hsv(h, s=0.75, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def background():
    y = np.linspace(0, 1, H * S)[:, None, None]
    top, bot = np.array(BG_TOP, float), np.array(BG_BOTTOM, float)
    grad = top + (bot - top) * y
    xs = np.linspace(-1, 1, W * S)[None, :, None]
    ys = np.linspace(-1, 1, H * S)[:, None, None]
    vign = 1 - 0.35 * np.clip(xs ** 2 + (ys * 0.8) ** 2, 0, 1)
    arr = np.broadcast_to(grad * vign, (H * S, W * S, 3)).astype(np.uint8)
    return Image.fromarray(arr)


class Pen:
    """Zeichnet in 1x-Koordinaten auf eine S-fach vergroesserte Leinwand."""

    def __init__(self, img):
        self.img, self.d = img, ImageDraw.Draw(img)

    def circle(self, x, y, r, fill=None, outline=None, width=0):
        self.d.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S),
                       fill=fill, outline=outline, width=int(width * S))

    def arc(self, x, y, r, a0, a1, fill, width):
        self.d.arc(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), a0, a1, fill=fill, width=int(width * S))

    def rect(self, x0, y0, x1, y1, fill, radius=0):
        if radius:
            self.d.rounded_rectangle((x0 * S, y0 * S, x1 * S, y1 * S), radius=radius * S, fill=fill)
        else:
            self.d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill)

    def poly(self, pts, fill):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill)

    def line(self, pts, fill, width):
        self.d.line([(x * S, y * S) for x, y in pts], fill=fill, width=int(width * S), joint="curve")


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


# ---------------------------------------------------------------- Szenen

class Scene:
    name = ""
    hook = ""
    duration = 12.0
    thumb = 0.5            # Anteil der Laenge fuer das Titelbild

    def __init__(self, seed):
        self.seed = seed
        self.rng = random.Random(seed)
        self.hue = self.rng.random()
        self.events = []    # (t, art, parameter...)

    def frames(self):
        raise NotImplementedError

    def sound(self, mx):
        raise NotImplementedError


class Grow(Scene):
    """Ball springt im Kreis, waechst bei jedem Aufprall; jeder Aufprall spielt die naechste Note."""
    name, hook = "grow", "Wait for the last bounce..."
    thumb = 0.8
    R, R0 = 420, 26

    def simulate(self, grow, record=False):
        rng = random.Random(self.seed)
        c = np.array([CX, CY])
        r = self.R0
        p = c + np.array([0.0, -self.R + 2 * self.R0 + 40])
        v = np.array([rng.choice([-1, 1]) * rng.uniform(380, 520), 0.0])
        g, sub = 1500.0, 10
        dt = 1 / (FPS * sub)
        t, done, out, hits = 0.0, None, [], []
        while True:
            for _ in range(sub):
                v[1] += g * dt
                p += v * dt
                d = p - c
                dist = np.linalg.norm(d)
                if dist + r >= self.R:
                    n = d / dist
                    vn = v @ n
                    if vn > 0:
                        v -= 2 * vn * n
                        r = min(self.R, r + grow)
                        hits.append((t, float(p[0] + n[0] * r), float(p[1] + n[1] * r), r))
                    p = c + n * (self.R - r)
                t += dt
            if record:
                out.append((p.copy(), r, len(hits)))
            if r >= self.R - 1 and done is None:
                done = t
            if done is not None and t >= done + 0.9:
                break
            if t > 24:
                return None, None, None
        return t, out, hits

    def frames(self):
        best = None
        for grow in np.linspace(4, 16, 25):
            t, _, _ = self.simulate(grow)
            if t and 10 <= t <= 14:
                best = grow
                break
        if best is None:
            best = 9.0
        _, states, hits = self.simulate(best, record=True)
        self.hits = hits
        self.duration = len(states) / FPS + 0.6
        n_loop = int(0.6 * FPS)
        start_p, start_r = states[0][0], states[0][1]
        trail = []
        for k in range(len(states) + n_loop):
            img = BASE.copy()
            pen = Pen(img)
            t = k / FPS
            if k < len(states):
                p, r, nh = states[k]
            else:  # Loop: Ball schrumpft zurueck an die Startposition
                q = ease((k - len(states)) / n_loop)
                p = states[-1][0] * (1 - q) + start_p * q
                r = self.R * (1 - q) + start_r * q
                nh = len(hits)
            col = hsv(self.hue + nh * 0.021)
            pen.circle(CX, CY, self.R + 7, outline=(235, 235, 245), width=7)
            for (ht, hx, hy, _) in hits:   # Wellen am Aufprallpunkt
                age = t - ht
                if 0 <= age < 0.35:
                    a = age / 0.35
                    pen.circle(hx, hy, 10 + 70 * a, outline=mix(col, BG_BOTTOM, a), width=5 * (1 - a) + 1)
            trail.append((p.copy(), r, col))
            trail = trail[-9:]
            for i, (tp, tr, tc) in enumerate(trail[:-1]):
                k2 = (i + 1) / len(trail)
                pen.circle(tp[0], tp[1], tr, fill=mix(BG_BOTTOM, tc, 0.25 * k2))
            pen.circle(p[0], p[1], r, fill=col, outline=(255, 255, 255), width=5)
            yield img

    def sound(self, mx):
        last = -1
        for i, (t, x, y, r) in enumerate(self.hits):
            if t - last < 0.035:
                continue
            last = t
            mx.add(t, snd_pluck(midi(arpeggio(i))), 0.5, pan_of(x))
        end = self.hits[-1][0] if self.hits else 5
        for j, n in enumerate((72, 76, 79, 84)):
            mx.add(end + 0.05 + j * 0.05, snd_pluck(midi(n), 2.0), 0.35, (j - 1.5) / 2)


class Escape(Scene):
    """Ball in rotierenden Ringen mit Luecke; jeder entkommene Ring zerplatzt."""
    name, hook = "escape", "Can the ball escape?"
    thumb = 0.3

    def setup(self, rng):
        self.rings = []
        n = 6
        for i in range(n):
            rad = 150 + i * 55
            self.rings.append({"r": rad, "w": rng.uniform(0.7, 1.2) * (1 if i % 2 else -1),
                               "ph": rng.uniform(0, 2 * math.pi), "gap": math.radians(rng.uniform(42, 52))})

    def simulate(self, seed, record=False):
        rng = random.Random(seed)
        self.setup(rng)
        p = np.array([CX, CY])
        ang = rng.uniform(-2.4, -0.7)
        v = np.array([math.cos(ang), math.sin(ang)]) * 700
        r, g, sub = 16, 1100.0, 10
        dt = 1 / (FPS * sub)
        cur, t, hits, pops, out = 0, 0.0, [], [], []
        while t < 15:
            for _ in range(sub):
                v[1] += g * dt
                p += v * dt
                t += dt
                if cur >= len(self.rings):
                    continue
                ring = self.rings[cur]
                d = p - np.array([CX, CY])
                dist = np.linalg.norm(d)
                if dist + r >= ring["r"] - 4:
                    th = math.atan2(d[1], d[0])
                    rel = (th - ring["ph"] - ring["w"] * t + math.pi) % (2 * math.pi) - math.pi
                    if abs(rel) < ring["gap"] / 2 - r / ring["r"]:
                        pops.append((t, cur, float(p[0]), float(p[1])))
                        cur += 1
                        continue
                    n = d / dist
                    vn = v @ n
                    if vn > 0:
                        v -= 2 * vn * n
                        hits.append((t, cur, float(p[0]), float(p[1])))
                    p = np.array([CX, CY]) + n * (ring["r"] - 4 - r)
            if record:
                out.append((p.copy(), cur))
            if cur >= len(self.rings) and (abs(p[0] - CX) > 700 or abs(p[1] - CY) > 1100):
                break
        return t, cur, hits, pops, out

    def frames(self):
        seed = self.seed
        for k in range(200):
            t, cur, hits, pops, _ = self.simulate(seed)
            if cur == len(self.rings) and 8 <= t <= 14 and pops[-1][0] < t - 0.4:
                break
            seed = self.seed * 1000 + k + 1
        t, cur, hits, pops, states = self.simulate(seed, record=True)
        self.hits, self.pops = hits, pops
        n_loop = int(0.7 * FPS)
        self.duration = (len(states) + n_loop) / FPS
        rng = random.Random(seed)
        shards = []
        for (pt, idx, _, _) in pops:
            ring = self.rings[idx]
            for j in range(48):
                a = j / 48 * 2 * math.pi
                sp = rng.uniform(150, 520)
                shards.append((pt, idx, CX + ring["r"] * math.cos(a), CY + ring["r"] * math.sin(a),
                               math.cos(a) * sp, math.sin(a) * sp - 200))
        for k in range(len(states) + n_loop):
            t = k / FPS
            img = BASE.copy()
            pen = Pen(img)
            if k < len(states):
                p, cur = states[k]
                fade = 1.0
            else:  # Loop: Ringe blenden wieder ein, Ball zurueck in die Mitte
                q = ease((k - len(states)) / n_loop)
                cur, fade = 0, q
                p = np.array([CX, CY])
            for i, ring in enumerate(self.rings):
                if i < cur:
                    continue
                col = mix(BG_BOTTOM, hsv(self.hue + i * 0.09), fade)
                ph = ring["ph"] + ring["w"] * (t if k < len(states) else 0)
                g = ring["gap"] / 2
                pen.arc(CX, CY, ring["r"], math.degrees(ph + g), math.degrees(ph + 2 * math.pi - g), col, 9)
            for (pt, idx, x0, y0, vx, vy) in shards:
                age = t - pt
                if 0 <= age < 1.1 and k < len(states):
                    x, y = x0 + vx * age, y0 + vy * age + 900 * age * age
                    pen.circle(x, y, 7 * (1 - age / 1.1) + 1, fill=mix(hsv(self.hue + idx * 0.09), BG_BOTTOM, age / 1.1))
            if k >= len(states) or fade:
                pen.circle(p[0], p[1], 16 * (fade if k >= len(states) else 1), fill=(255, 255, 255))
            yield img

    def sound(self, mx):
        last = -1
        for i, (t, ring, x, y) in enumerate(self.hits):
            if t - last < 0.04:
                continue
            last = t
            mx.add(t, snd_pluck(midi(arpeggio(i) + ring * 2)), 0.42, pan_of(x))
        for (t, ring, x, y) in self.pops:
            mx.add(t, snd_pop(mx.rng), 0.6, pan_of(x))
            for j, n in enumerate((84, 88, 91)):
                mx.add(t + 0.03 * j, snd_pluck(midi(n + ring), 0.8, 1.4), 0.18, pan_of(x))


class Galton(Scene):
    """Echtes Nagelbrett: jede Kugel wird physikalisch simuliert (Stifte, Waende, Kugeln untereinander)."""
    name, hook = "galton", "Will they make a bell curve?"
    thumb = 0.7
    ROWS, DX, DY, TOP = 12, 66, 52, 470
    BIN_TOP, FLOOR = 1150, 1580
    BALL = 13.0
    N = 110

    def build(self):
        rows, DX = self.ROWS, self.DX
        w = physics.World(gravity=1300, e_ball=0.1, e_wall=0.1, e_peg=0.25, friction=0.1, drag_x=2.0)
        w.pegs = np.array([(CX + (i - j / 2) * DX, self.TOP + j * self.DY + self.DY * 0.5, 8)
                           for j in range(rows) for i in range(j + 1)])
        xb = (rows + 1) / 2 * DX
        bottom = self.TOP + rows * self.DY
        w.add_seg("wl", CX - 34, self.TOP - 30, CX - xb, bottom, 16)
        w.add_seg("wr", CX + 34, self.TOP - 30, CX + xb, bottom, 16)
        w.add_seg("wl2", CX - xb, bottom, CX - xb, self.FLOOR, 16)
        w.add_seg("wr2", CX + xb, bottom, CX + xb, self.FLOOR, 16)
        for b in range(1, rows + 1):
            x = CX + (b - (rows + 1) / 2) * DX
            w.add_seg(f"bin{b}", x, self.BIN_TOP, x, self.FLOOR, 10)
        w.add_seg("floor", CX - xb, self.FLOOR, CX + xb, self.FLOOR, 8, kind="floor")
        return w

    def frames(self):
        rng = self.rng
        w = self.build()
        base = BASE.copy()
        bp = Pen(base)
        for (x, y, r) in w.pegs:
            bp.circle(x, y, r, fill=(150, 150, 175))
        for name, (ax, ay, bx, by, th, _, _) in w.segs.items():
            if name != "floor":
                bp.line([(ax, ay), (bx, by)], (80, 80, 110), th)
        spawns, ts = [], 0.0
        for i in range(self.N):      # Strom aus dem Rohr, wird langsam dichter
            spawns.append(ts)
            ts += 0.09
        drain_at = None
        self.drain_t = 0
        bp.rect(CX - 16, self.TOP - 190, CX + 16, self.TOP - 30, fill=(60, 62, 90), radius=6)   # Rohr
        sub = 12
        dt = 1 / (FPS * sub)
        k, si = 0, 0
        while True:
            t = k / FPS
            while si < self.N and spawns[si] <= t:
                w.add_ball(CX + rng.uniform(-2, 2), self.TOP - 45, self.BALL, rng.uniform(-8, 8), 260,
                           tag=hsv(self.hue + si / self.N * 0.8, 0.7))
                si += 1
            settled = si == self.N and (w.p[w.alive, 1] > self.BIN_TOP).all() and \
                (np.abs(w.v[w.alive]) < 40).all()
            if drain_at is None and (settled or t >= spawns[-1] + 5):
                drain_at = t + 0.6
                self.drain_t = drain_at
            if drain_at is not None and t >= drain_at and w.segs["floor"][5]:
                w.segs["floor"][5] = False          # Boden oeffnet sich -> Loop beginnt leer von vorn
                for seg in w.segs.values():
                    if seg[3] >= self.FLOOR - 1:
                        seg[3] = self.FLOOR + 60
            for _ in range(sub):
                w.step(dt)
            w.cull(H + 40)
            img = base.copy()
            pen = Pen(img)
            if w.segs["floor"][5]:
                ax, ay, bx, by, th, _, _ = w.segs["floor"]
                pen.line([(ax, ay), (bx, by)], (90, 90, 120), th)
            for i in np.nonzero(w.alive)[0]:
                pen.circle(w.p[i, 0], w.p[i, 1], self.BALL, fill=w.tag[i])
            yield img
            k += 1
            if (drain_at is not None and t > drain_at and not w.alive.any()) or t > 18:
                break
        self.events = w.events

    def sound(self, mx):
        rng = mx.rng
        for (t, kind, x, y, s) in self.events:
            if kind == "peg":
                mx.add(t, snd_tick(rng.uniform(2600, 4200), rng), 0.10 * (0.3 + s), pan_of(x))
            elif kind == "ball":
                mx.add(t, snd_tick(rng.uniform(1500, 2400), rng), 0.07 * (0.3 + s), pan_of(x))
            else:
                mx.add(t, snd_tok(rng.uniform(700, 1000)), 0.12 * (0.3 + s), pan_of(x))
        mx.add(self.drain_t, snd_whoosh(0.7, rng), 0.45)


class Fill(Scene):
    """Kugeln prasseln in ein Glas, bis es genau bis zum Rand voll ist; dann geht der Boden auf."""
    name, hook = "fill", "Will it fill up perfectly?"
    thumb = 0.72
    GL, GR, GT, GB = CX - 190, CX + 190, 1000, 1560
    R = 22

    def frames(self):
        rng = self.rng
        w = physics.World(gravity=1700, e_ball=0.2, e_wall=0.3, friction=0.3)
        w.add_seg("left", self.GL, self.GT, self.GL, self.GB, 10, kind="glass")
        w.add_seg("right", self.GR, self.GT, self.GR, self.GB, 10, kind="glass")
        w.add_seg("floor", self.GL, self.GB, self.GR, self.GB, 10, kind="glass")
        colors = [hsv(self.hue + k * 0.11, 0.65) for k in range(8)]
        base = BASE.copy()
        bp = Pen(base)
        glass = mix(BG_BOTTOM, (120, 150, 220), 0.12)
        bp.rect(self.GL, self.GT, self.GR, self.GB, fill=glass)
        bp.rect(CX - 30, 360, CX + 30, 560, fill=(60, 62, 90), radius=8)       # Rohr
        bp.rect(CX - 36, 548, CX + 36, 566, fill=(90, 92, 125), radius=6)
        line_y = self.GT + 4
        sub = 8
        dt = 1 / (FPS * sub)
        k, n, stop, drain = 0, 0, None, None
        next_spawn = 0.0
        while True:
            t = k / FPS
            if stop is None and t >= next_spawn and n >= 136:
                stop = t                                   # so viele passen genau bis zum Rand
            if stop is None and t >= next_spawn:
                w.add_ball(CX + rng.uniform(-4, 4), 540, self.R, rng.uniform(-30, 30), 700,
                           tag=colors[(n // 22) % len(colors)])
                n += 1
                next_spawn = t + 0.06
            if stop is not None and drain is None and t >= stop + 1.4:
                drain = t
                w.segs["floor"][5] = False
                w.segs["left"][3] = w.segs["right"][3] = self.GB + 80
            for _ in range(sub):
                w.step(dt)
            w.cull(H + 60)
            img = base.copy()
            pen = Pen(img)
            for i in np.nonzero(w.alive)[0]:
                x, y = w.p[i]
                pen.circle(x, y, self.R, fill=w.tag[i])
                pen.circle(x - self.R * 0.32, y - self.R * 0.35, self.R * 0.28, fill=mix(w.tag[i], (255, 255, 255), 0.55))
            edge = (200, 215, 255)
            pen.line([(self.GL, self.GT - 10), (self.GL, self.GB)], edge, 8)
            pen.line([(self.GR, self.GT - 10), (self.GR, self.GB)], edge, 8)
            if w.segs["floor"][5]:
                pen.line([(self.GL, self.GB), (self.GR, self.GB)], edge, 8)
            for x in range(int(self.GL + 10), int(self.GR - 10), 34):     # Markierung "voll"
                pen.line([(x, line_y), (x + 18, line_y)], (255, 255, 255), 3)
            yield img
            k += 1
            if (drain is not None and not w.alive.any()) or t > 22:
                break
        self.events, self.drain_t = w.events, drain or 0

    def sound(self, mx):
        rng = mx.rng
        for (t, kind, x, y, s) in self.events:
            if kind == "glass":
                mx.add(t, snd_pluck(rng.uniform(1900, 2600), 0.35, 1.3), 0.10 * (0.25 + s), pan_of(x))
            else:
                mx.add(t, snd_tick(rng.uniform(1200, 2200), rng), 0.12 * (0.3 + s), pan_of(x))
        mx.add(self.drain_t, snd_whoosh(0.8, rng), 0.5)


class Slice(Scene):
    """Ein Block aus bunten Schichten wird Scheibe fuer Scheibe zerschnitten (perfekter Loop)."""
    name, hook = "slice", "Sound on. Trust me."
    thumb = 0.4
    KX = 430            # Messerposition
    TOP, BOTTOM = 840, 1240
    SW = 64             # Scheibendicke
    PERIOD = 1.15

    def make_texture(self, length):
        rng = np.random.default_rng(self.seed)
        h = int((self.BOTTOM - self.TOP) * S)
        L = int(length * S)
        tex = np.zeros((h, L, 3))
        y = 0
        layers = []
        palette = [hsv(self.hue + k * 0.13, 0.45 + 0.1 * (k % 2), 0.95) for k in range(8)]
        while y < h:
            th = int(rng.uniform(0.07, 0.18) * h)
            layers.append((y, min(h, y + th), palette[len(layers) % len(palette)]))
            y += th
        xs = np.arange(L)
        for (y0, y1, c) in layers:
            wav = (np.sin(xs / L * 2 * np.pi * 3) * 6 * S).astype(int)   # periodisch -> Loop
            for x in range(0, L, 4):
                a, b = max(0, y0 + wav[x]), min(h, y1 + wav[x])
                tex[a:b, x:x + 4] = c
        grain = rng.standard_normal((h // 2 + 1, L // 2 + 1))
        grain = np.repeat(np.repeat(grain, 2, 0), 2, 1)[:h, :L]
        tex *= (1 + 0.07 * grain)[:, :, None]
        return Image.fromarray(np.clip(tex, 0, 255).astype(np.uint8))

    def simulate_fall(self):
        """Scheibe kippt als starrer Koerper ueber die Plattformkante, loest sich und faellt frei."""
        w, h, g = self.SW, self.BOTTOM - self.TOP, 2600.0
        px, py = self.KX - 6, self.BOTTOM                 # Drehpunkt: Plattformkante
        rx, ry = self.KX - w / 2 - px, -h / 2             # Schwerpunkt relativ zum Drehpunkt
        I = (w * w + h * h) / 12 + rx * rx + ry * ry
        th, om, dt, t, out = 0.0, 0.0, 1 / 600, 0.0, []
        while th < 0.9:
            off_x = rx * math.cos(th) + ry * math.sin(th)
            om += -g * off_x / I * dt
            th += om * dt
            t += dt
            out.append((t, px + rx * math.cos(th) + ry * math.sin(th), py - rx * math.sin(th) + ry * math.cos(th), th))
        vx = om * (-rx * math.sin(th) + ry * math.cos(th))
        vy = om * (-rx * math.cos(th) - ry * math.sin(th))
        cx, cy = out[-1][1], out[-1][2]
        while cy < H + 500:
            vy += g * dt
            cx += vx * dt
            cy += vy * dt
            th += om * dt
            t += dt
            out.append((t, cx, cy, th))
        return np.array(out)

    def frames(self):
        self.fall = self.simulate_fall()
        n_vis = int((W - self.KX) / self.SW) + 3
        cycles = 10
        L = (cycles) * self.SW
        tex = self.make_texture(L)
        tex = Image.fromarray(np.tile(np.asarray(tex), (1, (n_vis // cycles) + 3, 1)))
        self.duration = cycles * self.PERIOD
        P = self.PERIOD
        self.cuts = []
        crumbs = []
        warm = 3
        for c in range(-warm, cycles + 2):
            self.cuts.append(c * P + 0.48 * P)
            rng = random.Random(self.seed * 100 + c % cycles)   # gleiche Kruemel je Loop-Runde
            for _ in range(26):
                crumbs.append((c * P + 0.48 * P + rng.uniform(0, 0.18 * P), rng.uniform(self.TOP, self.BOTTOM),
                               rng.uniform(-260, -60), rng.uniform(-200, 50), rng.uniform(3, 7)))
        hgt = self.BOTTOM - self.TOP
        total = int(self.duration * FPS)
        for k in range(total):
            t = k / FPS
            img = BASE.copy()
            pen = Pen(img)
            pen.rect(self.KX - 6, self.BOTTOM, W + 10, self.BOTTOM + 34, fill=(60, 62, 84), radius=0)
            pen.rect(self.KX - 6, self.BOTTOM, W + 10, self.BOTTOM + 8, fill=(110, 112, 140))
            c = math.floor(t / P)
            ph = t / P - c
            push = ease(ph / 0.38)                 # Block schiebt sich um eine Scheibe vor
            stick = self.SW * push if ph < 0.62 else 0
            cut_x0 = (c % cycles) * self.SW        # Texturposition der Schnittkante
            src0 = cut_x0 + self.SW - stick if ph < 0.62 else cut_x0 + self.SW
            if ph >= 0.62:
                stick = 0
            vis = W - self.KX + stick + 10
            crop = tex.crop((int(src0 * S), 0, int((src0 + vis) * S), int(hgt * S)))
            img.paste(crop, (int((self.KX - stick) * S), int(self.TOP * S)))
            for cc in range(c - 3, c + 1):          # fallende Scheiben
                rel = t - (cc * P + 0.62 * P)
                if rel < 0:
                    continue
                off = ((cc % cycles) * self.SW + self.SW) % L
                sl = tex.crop((int(off * S), 0, int((off + self.SW) * S), int(hgt * S))).convert("RGBA")
                if rel > self.fall[-1, 0]:
                    continue
                fi = min(int(np.searchsorted(self.fall[:, 0], rel)), len(self.fall) - 1)
                _, cx, cy, th = self.fall[fi]
                rot = sl.rotate(math.degrees(th), resample=Image.BICUBIC, expand=True)
                img.paste(rot, (int(cx * S - rot.width / 2), int(cy * S - rot.height / 2)), rot)
            for (ct, cy0, vx, vy, sz) in crumbs:
                age = t - ct
                if 0 <= age < 1.2:
                    x, y = self.KX + vx * age, cy0 + vy * age + 1400 * age * age
                    if y < H:
                        lay = int((cy0 - self.TOP) / hgt * 7)
                        pen.rect(x - sz / 2, y - sz / 2, x + sz / 2, y + sz / 2,
                                 fill=hsv(self.hue + (lay % 8) * 0.13, 0.5, 0.95))
            # Messer
            if ph < 0.42:
                ky = self.TOP - 330
            elif ph < 0.6:
                ky = self.TOP - 330 + (hgt + 330) * ease((ph - 0.42) / 0.18) ** 0.6
            else:
                ky = self.BOTTOM - (hgt + 330) * ease((ph - 0.6) / 0.4)
            bx = self.KX
            pen.poly([(bx - 4, ky - 620), (bx + 4, ky - 620), (bx + 4, ky), (bx - 4, ky - 40)], (215, 220, 232))
            pen.poly([(bx - 1, ky - 620), (bx + 4, ky - 620), (bx + 4, ky)], (250, 252, 255))
            pen.rect(bx - 16, ky - 820, bx + 16, ky - 620, fill=(40, 36, 46), radius=8)
            yield img

    def sound(self, mx):
        P = self.PERIOD
        for c in range(-2, int(self.duration / P) + 1):
            t = c * P + 0.48 * P
            mx.add(t, snd_crunch(0.18 * P / 0.9 + 0.05, mx.rng), 0.55, pan_of(self.KX))
            mx.add(c * P + 0.05, snd_whoosh(0.3, mx.rng), 0.08, 0.3)
            mx.add(c * P + 0.62 * P + 0.25, snd_thud(), 0.15, -0.6)


class Stack(Scene):
    """Bloecke gleiten herein und landen perfekt uebereinander."""
    name, hook = "stack", "Perfectly stacked. Every time."
    thumb = 0.85
    BH, BW, GROUND = 64, 430, 1560

    def frames(self):
        n = 16
        times, t = [], 0.15
        for i in range(n):
            times.append(t)
            t += max(0.55, 0.95 - i * 0.03)
        self.lands = []
        slide, drop = 0.32, 0.22
        for i, t0 in enumerate(times):
            self.lands.append(t0 + slide + drop)
        zoom_t = self.lands[-1] + 0.4
        sink_t = zoom_t + 1.1
        self.duration = sink_t + 0.7
        self.sink_t = sink_t
        total = int(self.duration * FPS)
        cam = 0.0
        for k in range(total):
            t = k / FPS
            img = BASE.copy()
            pen = Pen(img)
            landed = sum(1 for lt in self.lands if lt <= t)
            top_h = landed * self.BH
            target = max(0.0, top_h - 520)
            cam += (target - cam) * 0.18
            z = 1.0
            if t >= zoom_t:
                fit = min(1.0, (self.GROUND - 520) / (n * self.BH + 40))
                q = ease((t - zoom_t) / 0.7)
                z = 1 + (fit - 1) * q
                cam_z = cam * (1 - q)
            else:
                cam_z = cam
            sink = 0.0
            if t >= sink_t:
                sink = 0.5 * 5000 * (t - sink_t) ** 2
            ground = self.GROUND + cam_z
            floor = ground + sink

            def blk(i, x, h_bottom, alpha=1.0):
                y1 = floor - h_bottom * z
                y0 = y1 - self.BH * z
                x0 = CX + (x - self.BW / 2 - CX) * z
                x1 = CX + (x + self.BW / 2 - CX) * z
                col = hsv(self.hue + i * 0.025, 0.62)
                pen.rect(x0, y0, x1, y1 - 1, fill=mix(BG_BOTTOM, col, alpha), radius=6 * z)
                pen.rect(x0 + 6 * z, y0 + 5 * z, x1 - 6 * z, y0 + 13 * z, fill=mix(BG_BOTTOM, mix(col, (255, 255, 255), 0.45), alpha))
            pen.rect(0, ground, W, ground + 18, fill=(70, 72, 98))
            for i, t0 in enumerate(times):
                if t < t0:
                    break
                hb = i * self.BH
                if t >= self.lands[i]:
                    sq = t - self.lands[i]
                    blk(i, CX, hb)
                    if sq < 0.3:
                        a = sq / 0.3
                        y = ground - hb * z
                        pen.line([(CX - self.BW / 2 * z - 30 * a * 3, y), (CX - self.BW / 2 * z - 5, y)],
                                 mix((255, 255, 255), BG_BOTTOM, a), 4)
                        pen.line([(CX + self.BW / 2 * z + 5, y), (CX + self.BW / 2 * z + 30 * a * 3, y)],
                                 mix((255, 255, 255), BG_BOTTOM, a), 4)
                    continue
                side = -1 if i % 2 else 1
                u = (t - t0)
                if u < slide:
                    x = CX + side * 700 * (1 - ease(u / slide))
                    blk(i, x, hb + 200)
                else:
                    d = (u - slide) / drop
                    blk(i, CX, hb + 200 * (1 - d * d))
            if sink:   # Loop: Turm versinkt im Boden, danach ist alles wie am Anfang
                gy = int(ground * S)
                img.paste(BASE.crop((0, gy, W * S, H * S)), (0, gy))
                pen.rect(0, ground, W, ground + 18, fill=(70, 72, 98))
            yield img

    def sound(self, mx):
        scale = [0, 2, 4, 7, 9]
        for i, t in enumerate(self.lands):
            note = 60 + 12 * (i // 5) % 24 + scale[i % 5]
            mx.add(t, snd_tok(midi(note + 12)), 0.30, 0.0)
            mx.add(t, snd_pluck(midi(note), 0.9), 0.32, (i % 2) * 0.6 - 0.3)
            mx.add(t - 0.4, snd_whoosh(0.3, mx.rng), 0.06, -0.7 if i % 2 else 0.7)
        mx.add(self.sink_t, snd_whoosh(0.6, mx.rng), 0.4)


MATCHUPS = [  # (Name, Kuerzel, Farbe) - nur Laendernamen/-farben, keine Logos
    (("BRAZIL", "BRA", (250, 215, 30)), ("ARGENTINA", "ARG", (110, 190, 255))),
    (("ENGLAND", "ENG", (245, 245, 245)), ("GERMANY", "GER", (230, 40, 50))),
    (("SPAIN", "ESP", (235, 30, 45)), ("PORTUGAL", "POR", (20, 170, 80))),
    (("FRANCE", "FRA", (40, 90, 230)), ("ITALY", "ITA", (30, 200, 120))),
    (("NETHERLANDS", "NED", (255, 130, 20)), ("BELGIUM", "BEL", (220, 30, 40))),
    (("MESSI", "M10", (110, 190, 255)), ("RONALDO", "CR7", (235, 30, 45))),
]


class Duel(Scene):
    """Zwei Baelle (zwei Teams) in denselben rotierenden Ringen: wer zuerst ganz draussen ist, gewinnt.
    Ein Ring zerplatzt, sobald irgendein Ball durch seine Luecke kommt. Baelle stossen elastisch aneinander."""
    name = "duel"
    thumb = 0.15
    R = 30

    def __init__(self, seed):
        super().__init__(seed)
        self.teams = MATCHUPS[seed % len(MATCHUPS)]
        a, b = self.teams[0][0], self.teams[1][0]
        self.hook = f"{a} vs {b}\nWho escapes first?"
        self.caption = f"{a.title()} or {b.title()}? Pick your side in the comments BEFORE it ends"

    def setup(self, rng):
        self.rings = []
        for i in range(5):
            self.rings.append({"r": 170 + i * 62, "w": rng.uniform(0.7, 1.15) * (1 if i % 2 else -1),
                               "ph": rng.uniform(0, 2 * math.pi), "gap": math.radians(rng.uniform(40, 48))})

    def simulate(self, seed, record=False):
        rng = random.Random(seed)
        self.setup(rng)
        c = np.array([CX, CY])
        ps = [c + np.array([-45.0, 0.0]), c + np.array([45.0, 0.0])]
        vs = []
        for _ in range(2):
            a = rng.uniform(0, 2 * math.pi)
            vs.append(np.array([math.cos(a), math.sin(a)]) * rng.uniform(600, 800))
        r, g, sub = self.R, 1000.0, 10
        dt = 1 / (FPS * sub)
        cur, t, hits, pops, out, winner, t_win = 0, 0.0, [], [], [], None, None
        while t < 16:
            for _ in range(sub):
                t += dt
                for i in range(2):
                    vs[i][1] += g * dt
                    ps[i] = ps[i] + vs[i] * dt
                d = ps[1] - ps[0]
                dist = np.linalg.norm(d)
                if 0 < dist < 2 * r:
                    n = d / dist
                    rel = (vs[0] - vs[1]) @ n
                    if rel > 0:
                        vs[0] = vs[0] - rel * n
                        vs[1] = vs[1] + rel * n
                        hits.append((t, -1, float(ps[0][0] + d[0] / 2), 0.0))
                    over = 2 * r - dist
                    ps[0] = ps[0] - n * over / 2
                    ps[1] = ps[1] + n * over / 2
                for i in range(2):
                    if cur >= len(self.rings):
                        continue
                    ring = self.rings[cur]
                    dd = ps[i] - c
                    dl = np.linalg.norm(dd)
                    if dl + r >= ring["r"] - 4:
                        th = math.atan2(dd[1], dd[0])
                        rel = (th - ring["ph"] - ring["w"] * t + math.pi) % (2 * math.pi) - math.pi
                        if abs(rel) < ring["gap"] / 2 - r / ring["r"]:
                            pops.append((t, cur, float(ps[i][0]), i))
                            cur += 1
                            if cur == len(self.rings):
                                winner, t_win = i, t
                            continue
                        n = dd / dl
                        vn = vs[i] @ n
                        if vn > 0:
                            vs[i] = vs[i] - 2 * vn * n
                            hits.append((t, cur, float(ps[i][0]), 0.0))
                        ps[i] = c + n * (ring["r"] - 4 - r)
            if record:
                out.append(([p.copy() for p in ps], cur))
            if winner is not None and t > t_win + 1.6:
                break
        return t, cur, hits, pops, out, winner, t_win

    def frames(self):
        seed = self.seed
        for k in range(300):
            res = self.simulate(seed)
            t, cur, hits, pops, _, winner, t_win = res
            if winner is not None and 7 <= t_win <= 12.5:
                by = [sum(1 for p in pops if p[3] == i) for i in range(2)]
                if min(by) >= 2:   # knappes Rennen: beide Teams sprengen mindestens 2 Ringe
                    break
            seed = self.seed * 1000 + k + 1
        t, cur, hits, pops, states, winner, t_win = self.simulate(seed, record=True)
        self.hits, self.pops, self.winner, self.t_win = hits, pops, winner, t_win
        n_loop = int(0.6 * FPS)
        self.duration = (len(states) + n_loop) / FPS
        rng = random.Random(seed)
        shards = []
        for (pt, idx, _, who) in pops:
            ring = self.rings[idx]
            col = self.teams[who][2]
            for j in range(48):
                a = j / 48 * 2 * math.pi
                sp = rng.uniform(150, 520)
                shards.append((pt, col, CX + ring["r"] * math.cos(a), CY + ring["r"] * math.sin(a),
                               math.cos(a) * sp, math.sin(a) * sp - 200))
        f_lab = ImageFont.truetype(BOLD, 19 * S)
        f_win = ImageFont.truetype(BOLD, 88 * S)
        start = [np.array([CX - 45.0, CY]), np.array([CX + 45.0, CY])]
        for k in range(len(states) + n_loop):
            t = k / FPS
            img = BASE.copy()
            pen = Pen(img)
            if k < len(states):
                ps, cur = states[k]
                fade = 1.0
            else:
                q = ease((k - len(states)) / n_loop)
                cur, fade, ps = 0, q, start
            for i, ring in enumerate(self.rings):
                if i < cur:
                    continue
                col = mix(BG_BOTTOM, hsv(0.55 + i * 0.07, 0.35, 0.95), fade)
                ph = ring["ph"] + ring["w"] * (t if k < len(states) else 0)
                gg = ring["gap"] / 2
                pen.arc(CX, CY, ring["r"], math.degrees(ph + gg), math.degrees(ph + 2 * math.pi - gg), col, 9)
            for (pt, col, x0, y0, vx, vy) in shards:
                age = t - pt
                if 0 <= age < 1.1 and k < len(states):
                    x, y = x0 + vx * age, y0 + vy * age + 900 * age * age
                    pen.circle(x, y, 7 * (1 - age / 1.1) + 1, fill=mix(col, BG_BOTTOM, age / 1.1))
            for i in range(2):
                x, y = ps[i]
                col = self.teams[i][2]
                pen.circle(x, y, self.R, fill=col, outline=(255, 255, 255), width=3)
                pen.d.text((x * S, y * S), self.teams[i][1], font=f_lab, fill=(10, 10, 20), anchor="mm")
            if k < len(states) and t >= self.t_win:
                a = ease((t - self.t_win) / 0.25)
                txt = self.teams[self.winner][0] + " WINS!"
                col = mix(BG_BOTTOM, self.teams[self.winner][2], a)
                pen.d.text((CX * S, 1620 * S), txt, font=f_win, fill=col, anchor="mm",
                           stroke_width=6 * S, stroke_fill=(0, 0, 0))
            yield img

    def sound(self, mx):
        last = -1
        for i, (t, ring, x, _) in enumerate(self.hits):
            if t - last < 0.04:
                continue
            last = t
            note = arpeggio(i) + (ring * 2 if ring >= 0 else 7)
            mx.add(t, snd_pluck(midi(note)), 0.4, pan_of(x))
        for (t, ring, x, _) in self.pops:
            mx.add(t, snd_pop(mx.rng), 0.6, pan_of(x))
            for j, n in enumerate((84, 88, 91)):
                mx.add(t + 0.03 * j, snd_pluck(midi(n + ring), 0.8, 1.4), 0.18, pan_of(x))
        for j, n in enumerate((72, 76, 79, 84, 88)):
            mx.add(self.t_win + 0.08 * j, snd_pluck(midi(n), 2.0), 0.35, (j - 2) / 2)


SCENES = {c.name: c for c in (Grow, Escape, Fill, Slice, Stack, Duel)}   # Galton: Physik-Version bildet noch keine saubere Glocke
CAPTIONS = {
    "grow": "Each bounce makes it bigger... wait for the last one",
    "escape": "Did you think it would make it out?",
    "galton": "200 balls, all bouncing randomly. Did they make the curve?",
    "fill": "Kept watching to see if it fits. Sound on",
    "slice": "Turn the sound on and watch it loop",
    "stack": "Not a single block off. Watch it again.",
}
TAGS = "#oddlysatisfying #satisfying #asmr #satisfyingvideo #relaxing"

BASE = None


def hook_layer(text):
    img = Image.new("RGBA", (W, 420), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = 78
    f = ImageFont.truetype(BOLD, size)
    lines = text.split("\n")
    while max(d.textlength(l, font=f) for l in lines) > 900 and size > 44:
        size -= 4
        f = ImageFont.truetype(BOLD, size)
    y0 = 300 - (len(lines) - 1) * size * 0.6
    for i, line in enumerate(lines):
        d.text((W / 2, y0 + i * size * 1.2), line, font=f, fill=(255, 255, 255), anchor="mm",
               stroke_width=6, stroke_fill=(0, 0, 0))
    return img


def finish(img_s, hook):
    img = img_s.reduce(S)
    small = img.resize((W // 6, H // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5))
    glow = small.resize((W, H), Image.BILINEAR).point(lambda v: int(v * 0.85))
    img = ImageChops.screen(img, glow)
    img.paste(hook, (0, 0), hook)
    return img


def render(scene_name, seed, out_path):
    global BASE
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    BASE = background()
    scene = SCENES[scene_name](seed)
    hook = hook_layer(scene.hook)
    silent, audio = out_path + ".silent.mp4", out_path + ".wav"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", silent], stdin=subprocess.PIPE)
    count = 0
    for img in scene.frames():
        enc.stdin.write(finish(img, hook).tobytes())
        count += 1
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg (Video) fehlgeschlagen")
    scene.duration = count / FPS
    mx = Mixer(scene.duration, seed)
    scene.sound(mx)
    write_wav(audio, mx.master())
    tmp = out_path + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_path)
    os.remove(silent)
    os.remove(audio)
    return {"path": out_path, "duration": scene.duration, "thumb_ms": int(scene.duration * scene.thumb * 1000),
            "caption": getattr(scene, "caption", None) or CAPTIONS[scene_name], "tags": TAGS}


if __name__ == "__main__":
    name = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(ROOT, "out", f"sat_{name}.mp4")
    print(render(name, seed, out))
