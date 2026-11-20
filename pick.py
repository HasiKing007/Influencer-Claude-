"""Experiment 16.11. abends: "Pick one per row"-Reel (Dream-Team bauen).
Nur Text, keine Fotos/Logos/fremde Musik. Meinungsfrage statt Wissensfrage:
jeder kann mitmachen und seine Auswahl kommentieren oder mit Freunden vergleichen.

Aufruf:  python pick.py <set-id> [ausgabe.mp4]
"""
import json
import os
import struct
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw

import render as r

ROOT = os.path.dirname(os.path.abspath(__file__))
PICKS = os.path.join(ROOT, "data", "picks.json")
ROW_IN = 0.45      # neue Reihe alle 0,45 s
INTRO = 0.2
HOLD = 2.6         # Schlussbild "COMMENT YOUR TEAM"
CAPTIONS = [
    "Pick ONE player from each row and comment your team. Then send this to a friend and compare!",
    "Your dream team, one pick per row. Comment it and send it to your football group. Who has the best XI?",
    "Only one per row. Hardest one? Comment your picks and send this to a friend to see if they agree.",
]
CODE_CAPTIONS = [
    "One per row. Comment your code (A, B or C per row, e.g. {ex}) and send this to a friend to compare!",
    "Your picks as a code: one letter per row, like {ex}. Drop yours in the comments. Who has the same?",
    "Hardest one per row. Comment your letters ({ex}?) and tag the friend who picks completely different.",
]
TAGS = "#football #soccer #dreamteam #footballfans #footballquiz"


def load_sets():
    with open(PICKS, encoding="utf-8") as f:
        return json.load(f)


def timing(n):
    rows_end = INTRO + n * ROW_IN
    return rows_end, rows_end + HOLD


def header(title):
    img = Image.new("RGB", (r.W, r.H))
    px = img.load()
    for y in range(r.H):
        k = y / (r.H - 1)
        c = tuple(int(r.BG_TOP[i] + (r.BG_BOTTOM[i] - r.BG_TOP[i]) * k) for i in range(3))
        for x in range(r.W):
            px[x, y] = c
    d = ImageDraw.Draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    d.text((r.SAFE_LEFT, 250), title, font=r.fit_font(d, title, r.BOLD, 70, width), fill=r.WHITE)
    d.text((r.SAFE_LEFT, 330), "PICK ONE", font=r.fit_font(d, "PICK ONE", r.BOLD, 120, width), fill=r.ACCENT)
    d.text((r.SAFE_LEFT, 460), "from each row", font=r.font(r.REGULAR, 46), fill=r.MUTED)
    text = "SEND THIS TO A FRIEND AND COMPARE"
    f = r.fit_font(d, text, r.BOLD, 50, width - 60)
    d.rounded_rectangle((r.SAFE_LEFT, 1462, r.SAFE_RIGHT, 1552), radius=45, fill=r.ACCENT)
    d.text(((r.SAFE_LEFT + r.SAFE_RIGHT) / 2, 1507), text, font=f, fill=r.BG_BOTTOM, anchor="mm")
    return img


def draw_row(img, i, n, row, progress, letters=False):
    top, bottom = 560, 1430
    row_h = (bottom - top) / n
    box_h = row_h - 16
    y0 = int(top + i * row_h)
    p = r.ease(progress)
    layer = Image.new("RGBA", (r.W, int(box_h) + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    label_w = 120
    d.rounded_rectangle((r.SAFE_LEFT, 0, r.SAFE_LEFT + label_w, box_h), radius=24, fill=r.ACCENT + (255,))
    d.text((r.SAFE_LEFT + label_w / 2, box_h / 2), row["label"], font=r.fit_font(d, row["label"], r.BOLD, 46, label_w - 16),
           fill=r.BG_BOTTOM, anchor="mm")
    x = r.SAFE_LEFT + label_w + 12
    opts = row["options"]
    w = (r.SAFE_RIGHT - x - 12 * (len(opts) - 1)) / len(opts)
    for j, name in enumerate(opts):
        d.rounded_rectangle((x, 0, x + w, box_h), radius=24, fill=r.ROW_BG + (255,))
        if letters:
            # Kommentar-Code (seit 20.11. abends): A/B/C-Marke oben links, damit der Kommentar
            # nur ein kurzer Buchstaben-Code ist ("ABCAB") statt fuenf Namen.
            lf = r.font(r.BOLD, 34)
            d.rounded_rectangle((x + 10, 8, x + 54, 52), radius=12, fill=r.ACCENT + (255,))
            d.text((x + 32, 30), "ABCD"[j], font=lf, fill=r.BG_BOTTOM, anchor="mm")
        words = name.split(" ")
        lines = [name] if len(words) == 1 else [words[0], " ".join(words[1:])]
        size = min(r.fit_font(d, ln, r.BOLD, 46, w - 32).size for ln in lines)
        f = r.font(r.BOLD, size)
        cy = box_h / 2 - (len(lines) - 1) * size * 0.55
        for ln in lines:
            d.text((x + w / 2, cy), ln.upper(), font=f, fill=r.WHITE, anchor="mm")
            cy += size * 1.1
        x += w + 12
    if p < 1:
        layer.putalpha(layer.getchannel("A").point(lambda a: int(a * p)))
    img.paste(layer, (int((1 - p) * 90), y0), layer)


def draw_end(img, t, text="COMMENT YOUR TEAM"):
    d = ImageDraw.Draw(img)
    p = r.ease(t / 0.35)
    y = 1640
    f = r.fit_font(d, text, r.BOLD, int(64 + 14 * p), r.SAFE_RIGHT - r.SAFE_LEFT)
    d.text(((r.SAFE_LEFT + r.SAFE_RIGHT) / 2, y), text, font=f, fill=r.WHITE, anchor="mm")
    return img


def frame_at(t, pset, base, baked):
    rows = pset["rows"]
    n = len(rows)
    anim = 0.3
    for i in range(n):
        if t >= INTRO + i * ROW_IN + anim and i not in baked:
            draw_row(base, i, n, rows[i], 1.0)
            baked.add(i)
    img = base.copy()
    for i in range(n):
        s = INTRO + i * ROW_IN
        if s <= t < s + anim:
            draw_row(img, i, n, rows[i], (t - s) / anim)
    rows_end, _ = timing(n)
    if t >= rows_end:
        img = draw_end(img, t - rows_end, pset.get("end", "COMMENT YOUR TEAM"))
    return img


def write_audio(path, n):
    rate = 44100
    rows_end, total = timing(n)
    samples = [0.0] * int(total * rate)
    for i in range(n):
        r.tone(samples, INTRO + i * ROW_IN, 520 + 40 * i, 0.16)
    for freq in (392.0, 523.25, 659.25):
        r.tone(samples, rows_end, freq, 1.2, 0.2)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 32767)) for s in samples))


# ---------- v2 (19.11., Nischen-Fokus) ----------
# Befund nach 34 Reels: Wiedergabe nur 3-7 s, jedes Reel bleibt bei ~100 Reach. pick-legends war der
# einzige Share-Ausreisser. v2 setzt auf einen staerkeren Einstieg: das komplette Brett steht ab
# Frame 0 (kein leeres Bild), grosser Challenge-Hook oben, KI-Stimme liest den Hook, eine gelbe
# Markierung springt Reihe fuer Reihe durch die Optionen (Bewegung + "ich muss mich entscheiden").
HOOKS = [
    ("YOU CAN ONLY", "KEEP ONE"),
    ("99% CAN'T", "PICK JUST ONE"),
    ("THE HARDEST", "CHOICE EVER"),
]
HOOK_VOICE = [
    "You can only keep one from each row. Choose wisely.",
    "Ninety nine percent can't pick just one. Can you?",
    "The hardest choice ever. One per row. Go.",
]
SCAN_ROW = 0.62     # so lange springt die Markierung in jeder Reihe
SCAN_HOP = 0.1
V2_START = 0.25
V2_HOLD = 1.9


def v2_timing(n):
    scan_end = V2_START + n * SCAN_ROW
    return scan_end, scan_end + V2_HOLD


def v2_header(title, hook):
    import reelkit as k
    img = k.gradient(r.BG_TOP, r.BG_BOTTOM)
    d = ImageDraw.Draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    top, big = HOOKS[hook % len(HOOKS)]
    d.text((r.SAFE_LEFT, 236), top, font=r.fit_font(d, top, r.BOLD, 78, width), fill=r.WHITE)
    d.text((r.SAFE_LEFT, 318), big, font=r.fit_font(d, big, r.BOLD, 128, width), fill=r.ACCENT)
    d.text((r.SAFE_LEFT, 468), title + "  \u2022  ONE PER ROW", font=r.fit_font(d, title + "  \u2022  ONE PER ROW", r.BOLD, 44, width),
           fill=r.MUTED)
    text = "SEND THIS TO A FRIEND AND COMPARE"
    f = r.fit_font(d, text, r.BOLD, 50, width - 60)
    d.rounded_rectangle((r.SAFE_LEFT, 1462, r.SAFE_RIGHT, 1552), radius=45, fill=r.ACCENT)
    d.text(((r.SAFE_LEFT + r.SAFE_RIGHT) / 2, 1507), text, font=f, fill=r.BG_BOTTOM, anchor="mm")
    return img


def _option_box(i, j, n, n_opts):
    top, bottom = 560, 1430
    row_h = (bottom - top) / n
    box_h = row_h - 16
    y0 = top + i * row_h
    x = r.SAFE_LEFT + 120 + 12
    w = (r.SAFE_RIGHT - x - 12 * (n_opts - 1)) / n_opts
    x0 = x + j * (w + 12)
    return (x0, y0, x0 + w, y0 + box_h)


def v2_frame(t, pset, base, seed):
    import random
    rows = pset["rows"]
    n = len(rows)
    img = base.copy()
    d = ImageDraw.Draw(img)
    scan_end, _ = v2_timing(n)
    if V2_START <= t < scan_end:
        i = int((t - V2_START) / SCAN_ROW)
        hop = int((t - V2_START - i * SCAN_ROW) / SCAN_HOP)
        n_opts = len(rows[i]["options"])
        rng = random.Random(seed * 1000 + i * 50 + hop)
        j = rng.randrange(n_opts)
        x0, y0, x1, y1 = _option_box(i, j, n, n_opts)
        d.rounded_rectangle((x0 - 4, y0 - 4, x1 + 4, y1 + 4), radius=28, outline=r.ACCENT, width=9)
    if t >= scan_end:
        p = r.ease(min(1.0, (t - scan_end) / 0.3))
        text = pset.get("end", "COMMENT YOUR TEAM")
        pulse = 1 + 0.04 * np.sin((t - scan_end) * 9)
        f = r.fit_font(d, text, r.BOLD, int((62 + 16 * p) * pulse), r.SAFE_RIGHT - r.SAFE_LEFT)
        d.text(((r.SAFE_LEFT + r.SAFE_RIGHT) / 2, 1650), text, font=f, fill=r.WHITE, anchor="mm")
    return img


def code_example(pset, seed):
    import random
    rng = random.Random(seed)
    return "".join("ABCD"[rng.randrange(len(row["options"]))] for row in pset["rows"])


def render_pick(pset, out_path, hook=0, silent=False, seed=7, hold=None, cta=None):
    """v2. silent=True: ohne Stimme und Toene (fuer manuelles Posten mit Trend-Sound in der App).
    cta="code": Optionen tragen A/B/C, Schluss "COMMENT YOUR CODE" mit Beispiel (Experiment 20.11.)."""
    import reelkit as k
    global V2_HOLD
    if hold is not None:
        V2_HOLD = hold
    n = len(pset["rows"])
    base = v2_header(pset["title"], hook)
    letters = cta == "code"
    if letters:
        pset = dict(pset, end="COMMENT YOUR CODE: " + code_example(pset, seed))
    for i, row in enumerate(pset["rows"]):
        draw_row(base, i, n, row, 1.0, letters=letters)
    scan_end, total = v2_timing(n)
    audio = k.silence(total)
    voiced = False
    if not silent:
        clip = k.voice(HOOK_VOICE[hook % len(HOOK_VOICE)])
        if clip is not None and k.clip_len(clip) < total - 0.3:
            k.add_clip(audio, 0.05, clip, 0.9)
            voiced = True
        hops = int(n * SCAN_ROW / SCAN_HOP)
        for h in range(hops):
            k.add_tick(audio, V2_START + h * SCAN_HOP, 0.18)
        for freq in (392.0, 523.25, 659.25):
            k.add_tone(audio, scan_end, freq, 1.2, 0.18)
        k.add_pulse(audio, volume=0.08)
    k.encode(out_path, total, lambda t: v2_frame(t, pset, base, seed), audio)
    return {"path": out_path, "duration": total, "thumb_ms": 100, "voice": voiced, "hook": hook % len(HOOKS),
            "cta": cta}


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    pset = sets[sys.argv[1]]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "pick.mp4")
    print(render_pick(pset, out, hook=int(os.environ.get("HOOK", "0")), silent="--silent" in sys.argv))
