"""Experiment 17.11. abends: "Tap to pause" (Format pause).

Recherche 17.11. abends: Instagram hat seit Maerz 2026 Tippen-zum-Pausieren (ein Tipp pausiert,
zweiter laeuft weiter). Interaktive "Stop the video - what you land on is yours"-Reels nutzen genau
das: 12 Optionen im Raster, eine Markierung springt schnell hin und her, der Zuschauer tippt und
kommentiert, was er bekommen hat. Das erzeugt Wiederholungen (nochmal versuchen = Loops),
Kommentare ohne Vorwissen und laesst sich weiterschicken ("what did you get?").
Kein Fremdmaterial: nur Text, eigene Synth-Tonspur, KI-Stimme.

Aufruf:  python pause.py <set-id> [ausgabe.mp4] [--frame]
"""
import json
import os
import random
import sys

import reelkit as k
import render as r

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "pauses.json")
BG_TOP, BG_BOTTOM = (34, 16, 72), (8, 6, 24)
HILITE = (255, 214, 0)
CELL_BG = (44, 36, 92)
STEP = 0.1          # Markierung springt alle 0,1 s (3 Frames)
MIN_TOTAL = 6.5
COLS, ROWS = 3, 4
GRID_TOP, GRID_BOTTOM = 560, 1460
GAP = 18
CAPTIONS = [
    "Tap the screen to pause. What did you get? Comment it, then send this to a friend and compare!",
    "Pause it NOW. Comment what you landed on and send this to your best friend to see theirs.",
    "One tap only, no cheating. Comment what you got and send this to someone who needs to try.",
]


def load_sets():
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def cells():
    w = (r.SAFE_RIGHT - r.SAFE_LEFT - GAP * (COLS - 1)) / COLS
    h = (GRID_BOTTOM - GRID_TOP - GAP * (ROWS - 1)) / ROWS
    out = []
    for i in range(COLS * ROWS):
        c, row = i % COLS, i // COLS
        x0 = r.SAFE_LEFT + c * (w + GAP)
        y0 = GRID_TOP + row * (h + GAP)
        out.append((x0, y0, x0 + w, y0 + h))
    return out


def sequence(n_steps, seed):
    """Zufaellige Folge ohne direkte Wiederholung, damit jede Pause zufaellig wirkt."""
    rng = random.Random(seed)
    seq, last = [], -1
    for _ in range(n_steps):
        i = rng.randrange(COLS * ROWS - 1)
        i = i if i < last or last < 0 else i + 1
        seq.append(i)
        last = i
    return seq


def draw_cell(d, box, text, active):
    d.rounded_rectangle(box, radius=26, fill=HILITE if active else CELL_BG,
                        outline=(255, 255, 255) if active else None, width=6 if active else 0)
    x0, y0, x1, y1 = box
    f, lines = k.wrap(d, text.upper(), r.BOLD, 46, x1 - x0 - 28, max_lines=2, min_size=28)
    lh = f.size * 1.12
    y = (y0 + y1) / 2 - (len(lines) - 1) * lh / 2
    for ln in lines:
        d.text(((x0 + x1) / 2, y), ln, font=f, fill=(20, 14, 40) if active else r.WHITE, anchor="mm")
        y += lh


def base_frame(pset):
    img = k.gradient(BG_TOP, BG_BOTTOM)
    d = k.draw(img)
    width = r.SAFE_RIGHT - r.SAFE_LEFT
    k.pill(d, 250, "TAP TO PAUSE", HILITE, (20, 14, 40), size=64, h=110)
    k.center_text(d, 380, "WHAT YOU LAND ON IS", r.BOLD, 52, (200, 190, 240), width)
    k.center_text(d, 465, pset["title"].upper(), r.BOLD, 84, r.WHITE, width)
    k.pill(d, 1560, "COMMENT WHAT YOU GOT", r.WHITE, (20, 14, 40), size=54, h=100)
    return img


def render_pause(pset, out_path, seed=None):
    say = f"Tap to pause the video. Whatever you land on is {pset.get('say', pset['title'])}. Comment what you got!"
    clip = k.voice(say)
    total = max(MIN_TOTAL, k.clip_len(clip) + 1.2)
    seed = seed if seed is not None else random.randint(1, 10 ** 6)
    n_steps = int(total / STEP) + 1
    seq = sequence(n_steps, seed)
    boxes = cells()
    base = base_frame(pset)
    opts = pset["options"]
    for i, box in enumerate(boxes):
        draw_cell(k.draw(base), box, opts[i], False)

    def frame(t):
        img = base.copy()
        i = seq[min(int(t / STEP), n_steps - 1)]
        draw_cell(k.draw(img), boxes[i], opts[i], True)
        return img

    audio = k.silence(total)
    k.add_pulse(audio, bpm=128, volume=0.09)
    step = 0.0
    while step < total:
        k.add_tick(audio, step, volume=0.12)
        step += STEP
    k.add_clip(audio, 0.05, clip)
    k.encode(out_path, total, frame, audio)
    return {"path": out_path, "duration": total, "thumb_ms": 300, "voice": clip is not None, "seed": seed}


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    pset = sets[sys.argv[1]]
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    if "--frame" in sys.argv:
        img = base_frame(pset)
        for i, box in enumerate(cells()):
            draw_cell(k.draw(img), box, pset["options"][i], i == 4)
        img.save(os.path.join(ROOT, "out", "pause.png"))
    else:
        print(render_pause(pset, sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "pause.mp4")))
