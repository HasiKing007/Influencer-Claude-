# reelbot

Postet jeden Tag automatisch ein "Guess the player"-Reel auf Instagram.

- `data/quizzes.json` – Warteschlange der Quizze (wird der Reihe nach abgearbeitet)
- `data/state.json` – was bereits gepostet wurde
- `data/stats.json` – Follower- und Reel-Kennzahlen (wird täglich aktualisiert)
- `render.py` – erzeugt das Video (Pillow + ffmpeg)
- `post.py` – rendert und veröffentlicht über die Instagram-API
- `.github/workflows/post.yml` – täglicher Lauf (17:17 UTC)
- `.github/workflows/refresh-token.yml` – erneuert das Instagram-Token zweimal im Monat

Benötigte Secrets: `IG_ACCESS_TOKEN`, `GH_PAT`. Einrichtung siehe ANLEITUNG.txt.

Lokal testen: `pip install -r requirements.txt`, dann `python render.py ibrahimovic`.
