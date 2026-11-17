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


def draw_row(img, i, n, row, progress):
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
    for name in opts:
        d.rounded_rectangle((x, 0, x + w, box_h), radius=24, fill=r.ROW_BG + (255,))
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


def render_pick(pset, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    n = len(pset["rows"])
    rows_end, total = timing(n)
    silent, audio = out_path + ".silent.mp4", out_path + ".wav"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{r.W}x{r.H}", "-r", str(r.FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", silent], stdin=subprocess.PIPE)
    base, baked = header(pset["title"]), set()
    for k in range(int(total * r.FPS)):
        enc.stdin.write(frame_at(k / r.FPS, pset, base, baked).tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg (Video) fehlgeschlagen")
    write_audio(audio, n)
    tmp = out_path + ".tmp.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-ar", "44100", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_path)
    os.remove(silent)
    os.remove(audio)
    # Titelbild: alle Reihen sichtbar
    return {"path": out_path, "duration": total, "thumb_ms": int((rows_end + 0.2) * 1000)}


if __name__ == "__main__":
    sets = {s["id"]: s for s in load_sets()}
    pset = sets[sys.argv[1]]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "pick.mp4")
    if "--frame" in sys.argv:
        base, baked = header(pset["title"]), set()
        os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
        frame_at(timing(len(pset["rows"]))[0] + 1.0, pset, base, baked).save(os.path.join(ROOT, "out", "pick.png"))
    else:
        print(render_pick(pset, out))
