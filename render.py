"""Rendert ein "Guess the player"-Reel (1080x1920, 30 fps) aus einem Quiz-Eintrag.

Aufruf:  python render.py <quiz-id> [ausgabe.mp4]
         python render.py <quiz-id> --frames   (nur Testbilder nach out/)
"""
import json
import math
import os
import struct
import subprocess
import sys
import wave

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
BG_TOP, BG_BOTTOM = (10, 18, 38), (4, 8, 18)
ACCENT = (198, 255, 61)
WHITE = (245, 247, 250)
MUTED = (140, 152, 178)
ROW_BG = (22, 32, 60)
BOLD = os.path.join(ROOT, "fonts", "DejaVuSansCondensed-Bold.ttf")
REGULAR = os.path.join(ROOT, "fonts", "DejaVuSansCondensed.ttf")

# Bereich, den die Instagram-Oberflaeche nicht verdeckt
SAFE_LEFT, SAFE_RIGHT = 70, 930
LIST_TOP, LIST_BOTTOM = 520, 1440

INTRO = 0.3   # erste Station sofort zeigen (vorher 0.9 s leerer Einstieg)
# 2026-11-12: Zuschauer blieben im Schnitt nur 4-7 s, Reel war ~15 s -> auf ~9 s gekuerzt
COUNTDOWN = 2.0
REVEAL = 2.2
STATIONS_MAX = 4.5   # alle Stationen zusammen hoechstens so lange


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, size, max_width, min_size=30):
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(path, min_size)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def timing(n):
    step = min(0.6, STATIONS_MAX / n)
    stations_end = INTRO + n * step
    countdown_end = stations_end + COUNTDOWN
    total = countdown_end + REVEAL
    return step, stations_end, countdown_end, total


def background():
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        k = y / (H - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * k) for i in range(3))
        for x in range(W):
            px[x, y] = c
    d = ImageDraw.Draw(img)
    d.ellipse((W // 2 - 260, 1500, W // 2 + 260, 2020), outline=(20, 32, 62), width=6)
    d.line((0, 1760, W, 1760), fill=(20, 32, 62), width=6)
    d.text((SAFE_LEFT, 270), "GUESS THE", font=font(BOLD, 64), fill=WHITE)
    d.text((SAFE_LEFT, 340), "PLAYER", font=font(BOLD, 112), fill=ACCENT)
    d.text((SAFE_LEFT + 470, 388), "from his\ncareer path", font=font(REGULAR, 40), fill=MUTED, spacing=6)
    return img


def draw_row(img, i, n, club, progress):
    """Zeichnet Station i; progress 0..1 steuert Einblenden und Hereingleiten."""
    row_h = min(104, (LIST_BOTTOM - LIST_TOP) / n)
    gap = max(6, row_h * 0.12)
    y0 = LIST_TOP + i * row_h
    box_h = row_h - gap
    p = ease(progress)
    dx = int((1 - p) * 90)
    layer = Image.new("RGBA", (W, int(box_h) + 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = int(box_h * 0.28)
    d.rounded_rectangle((SAFE_LEFT, 0, SAFE_RIGHT, box_h), radius=r, fill=ROW_BG + (255,))
    chip = box_h
    d.rounded_rectangle((SAFE_LEFT, 0, SAFE_LEFT + chip, box_h), radius=r, fill=ACCENT + (255,))
    num_font = font(BOLD, int(box_h * 0.5))
    d.text((SAFE_LEFT + chip / 2, box_h / 2), str(i + 1), font=num_font, fill=BG_BOTTOM, anchor="mm")
    text_x = SAFE_LEFT + chip + 28
    club_font = fit_font(d, club, BOLD, int(box_h * 0.5), SAFE_RIGHT - text_x - 24)
    d.text((text_x, box_h / 2), club, font=club_font, fill=WHITE, anchor="lm")
    if p < 1:
        alpha = layer.getchannel("A").point(lambda a: int(a * p))
        layer.putalpha(alpha)
    img.paste(layer, (dx, int(y0)), layer)


def dim(img, strength):
    overlay = Image.new("RGB", (W, H), BG_BOTTOM)
    return Image.blend(img, overlay, strength)


def draw_countdown(img, t):
    """t = Sekunden seit Beginn des Countdowns."""
    img = dim(img, 0.86 * ease(t / 0.25))
    d = ImageDraw.Draw(img)
    d.text((W / 2, 700), "WHO IS IT?", font=font(BOLD, 96), fill=WHITE, anchor="mm")
    number = int(COUNTDOWN) - int(t)
    frac = t - int(t)
    cx, cy, rad = W / 2, 1010, 190
    d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), outline=ROW_BG, width=22)
    d.arc((cx - rad, cy - rad, cx + rad, cy + rad), -90, -90 + 360 * (1 - frac), fill=ACCENT, width=22)
    size = int(230 * (1 + 0.25 * (1 - ease(frac / 0.3))))
    d.text((cx, cy), str(max(number, 1)), font=font(BOLD, size), fill=ACCENT, anchor="mm")
    d.text((W / 2, 1300), "Answer in the comments", font=font(REGULAR, 46), fill=MUTED, anchor="mm")
    return img


def draw_reveal(img, answer, t):
    img = dim(img, 0.86)
    d = ImageDraw.Draw(img)
    p = ease(t / 0.45)
    d.text((W / 2, 760), "IT'S", font=font(BOLD, 70), fill=MUTED, anchor="mm")
    words = answer.split(" ")
    lines = [answer] if len(answer) <= 12 or len(words) == 1 else [words[0], " ".join(words[1:])]
    base = 150
    f = min((fit_font(d, ln, BOLD, base, SAFE_RIGHT - SAFE_LEFT + 60) for ln in lines), key=lambda x: x.size)
    f = font(BOLD, max(30, int(f.size * (0.7 + 0.3 * p))))
    y = 930 if len(lines) == 1 else 880
    for ln in lines:
        d.text((W / 2, y), ln.upper(), font=f, fill=ACCENT, anchor="mm")
        y += int(f.size * 1.15)
    if t > 0.9:
        q = ease((t - 0.9) / 0.4)
        colour = tuple(int(BG_BOTTOM[i] + (WHITE[i] - BG_BOTTOM[i]) * q) for i in range(3))
        d.text((W / 2, 1260), "Did you get it?", font=font(BOLD, 60), fill=colour, anchor="mm")
        d.text((W / 2, 1340), "Follow for a new quiz every day", font=font(REGULAR, 44), fill=MUTED, anchor="mm")
    return img


def draw_progress(img, t, until):
    d = ImageDraw.Draw(img)
    d.rectangle((SAFE_LEFT, 478, SAFE_RIGHT, 486), fill=ROW_BG)
    k = max(0.0, min(1.0, t / until))
    d.rectangle((SAFE_LEFT, 478, SAFE_LEFT + int((SAFE_RIGHT - SAFE_LEFT) * k), 486), fill=ACCENT)


def frame_at(t, quiz, base, baked):
    """base = Hintergrund mit allen fertig eingeblendeten Stationen (wird fortgeschrieben)."""
    clubs = quiz["clubs"]
    n = len(clubs)
    step, stations_end, countdown_end, _ = timing(n)
    anim = min(0.3, step * 0.6)
    for i in range(n):
        start = INTRO + i * step
        if t >= start + anim and i not in baked:
            draw_row(base, i, n, clubs[i], 1.0)
            baked.add(i)
    img = base.copy()
    for i in range(n):
        start = INTRO + i * step
        if start <= t < start + anim:
            draw_row(img, i, n, clubs[i], (t - start) / anim)
    draw_progress(img, t, countdown_end)
    if stations_end <= t < countdown_end:
        img = draw_countdown(img, t - stations_end)
    elif t >= countdown_end:
        img = draw_reveal(img, quiz["answer"], t - countdown_end)
    return img


def tone(samples, start, freq, length, volume=0.35, rate=44100):
    s0 = int(start * rate)
    for k in range(int(length * rate)):
        if s0 + k >= len(samples):
            break
        env = math.exp(-k / (length * rate * 0.35))
        samples[s0 + k] += volume * env * math.sin(2 * math.pi * freq * k / rate)


def write_audio(path, quiz):
    rate = 44100
    n = len(quiz["clubs"])
    step, stations_end, countdown_end, total = timing(n)
    samples = [0.0] * int(total * rate)
    for i in range(n):
        tone(samples, INTRO + i * step, 520 + 28 * i, 0.16)
    for k in range(int(COUNTDOWN)):
        tone(samples, stations_end + k, 440, 0.22, 0.4)
    for freq in (523.25, 659.25, 783.99, 1046.5):
        tone(samples, countdown_end, freq, 1.4, 0.22)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, s)) * 32767)) for s in samples))


def render(quiz, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    n = len(quiz["clubs"])
    total = timing(n)[3]
    silent = out_path + ".silent.mp4"
    audio = out_path + ".wav"
    enc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", silent],
        stdin=subprocess.PIPE)
    base, baked = background(), set()
    for k in range(int(total * FPS)):
        enc.stdin.write(frame_at(k / FPS, quiz, base, baked).tobytes())
    enc.stdin.close()
    if enc.wait() != 0:
        raise RuntimeError("ffmpeg (Video) fehlgeschlagen")
    write_audio(audio, quiz)
    tmp = out_path + ".tmp.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio,
         "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-ar", "44100", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, out_path)
    os.remove(silent)
    os.remove(audio)
    return out_path


def load_quiz(quiz_id):
    with open(os.path.join(ROOT, "data", "quizzes.json"), encoding="utf-8") as f:
        for q in json.load(f):
            if q["id"] == quiz_id:
                return q
    raise SystemExit(f"Quiz '{quiz_id}' nicht gefunden")


if __name__ == "__main__":
    quiz = load_quiz(sys.argv[1])
    if "--frames" in sys.argv:
        n = len(quiz["clubs"])
        step, stations_end, countdown_end, total = timing(n)
        base, baked = background(), set()
        os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
        for name, t in (("a_intro", 0.3), ("b_list", stations_end - 0.05),
                        ("c_count", stations_end + 1.4), ("d_reveal", countdown_end + 2.0)):
            frame_at(t, quiz, base, baked).save(os.path.join(ROOT, "out", f"frame_{name}.png"))
    else:
        out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "out", "reel.mp4")
        print(render(quiz, out))
