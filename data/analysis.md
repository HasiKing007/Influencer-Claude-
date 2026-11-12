# Reelbot Auswertungen

> Hinweise fuer jede Auswertung (Stand 2026-11-11, von Jacob gewuenscht):
> - Ziel sind maximale Views. Bei jedem Lauf per Websuche vergleichen, was aktuell top-performende Fussball-Quiz-Reels/Shorts machen
>   (Schnitt, Tempo, Footage, Idee/Format, Sound, Effekte, Hook in der ersten Sekunde), und eins bis zwei Punkte davon uebernehmen.
> - Keine urheberrechtlich geschuetzten Spielszenen/TV-Clips (Jacob wollte sie, Claude hat abgelehnt). Erlaubt: frei lizenziertes
>   Stock-Footage (Pexels/Pixabay), sobald Jacob einen API-Key als Secret hinterlegt; eigene Animationen und eigener Sound.
> - Pruefen, ob alle Slots des Tages gepostet haben; fehlende per Workflow-Dispatch ohne Inputs nachholen (Sperre verhindert Doppelposts).

## 2026-11-11 14:45 (Wien)
- Bisher 1 Reel (ibrahimovic, 06:52 UTC, manuell gestartet): 2 Likes, 0 Kommentare nach 7 h; 3 Follower.
- Views/Reach fehlen: Insights-Abfrage scheitert mit "(#10) Application does not have permission" -> Token braucht die Berechtigung instagram_business_manage_insights (Jacob muss Token neu erzeugen).
- Der geplante Lauf um 10:17 UTC ist nicht gestartet (GitHub-Cron ausgefallen), daher kein zweites Reel.
- Zu wenig Daten fuer inhaltliche Schluesse; Inhalt bleibt unveraendert.
- Geaendert: Ersatz-Cron-Termine (:47 und +1 h) mit Slot-Sperre in post.py (max. 1 Post pro 150 min, max. 3/Tag), Workflow holt vor dem Posten den neuesten Stand.

## 2026-11-11 17:50 (Wien), Nachtrag
- GitHub-Cron hat auch 14:17/14:47/15:17 UTC nicht gestartet; zusaetzlich hing apt-get (ffmpeg) >15 min.
- Fix: ffmpeg jetzt via imageio-ffmpeg (PyPI), Sperre gilt fuer alle Ausloeser (90 min Abstand, max. 4/Tag), externer Waechter um 10:38/14:38/18:38 UTC startet den Workflow, falls ein Slot fehlt.
- Nachhol-Reel ronaldinho um 16:40 UTC gepostet (Caption-Variante 1).

## 2026-11-11 22:45 (Wien)
- Heute 4 Reels: ibrahimovic 2 Likes (15 h), ronaldinho 1 Like (5 h), henry 2 Likes (3 h), tevez 0 Likes (20 min, spaet um 22:27 Wien gepostet). 0 Kommentare, 3 Follower (unveraendert).
- Views/Reach weiterhin nicht abrufbar ((#10) fehlende Berechtigung instagram_business_manage_insights) -> neuer Token von Jacob am 12.11. noetig.
- Likes allein (0-2) sind zu wenig Signal, um Captions/Spieler zu vergleichen; Konto ist erst 1 Tag alt.
- Geaendert: nichts am Inhalt, damit die ersten Tage eine saubere Vergleichsbasis liefern. 28 Quizze noch in der Warteschlange (Ziel >=15 erfuellt).

## 2026-11-11 22:50 (Wien)
- 4 Reels heute (ibrahimovic, ronaldinho, henry, tevez); laut Jacobs Screenshot 132 bzw. 138 Views bei den aelteren Reels, 1-2 Likes, weiter 3 Follower.
- Problem: Alle Titelbilder im Profil sind identisch und leer (nur "GUESS THE PLAYER"), erster Frame 0.9 s ohne Inhalt.
- Geaendert: Titelbild jetzt = komplette Karriere-Liste (thumb_offset kurz vor Countdown); erste Station erscheint nach 0.3 s statt 0.9 s.
- Keine Spielszenen-Clips: Urheberrecht der Ligen/Sender, Gefahr von Sperren.

## 2026-11-12 14:45 (Wien)
- 5 Reels insgesamt, heute bisher 1 (beckham 10:39 UTC, Waechter-Start; der 10:17-Cron fiel wieder aus). Likes: beckham 2 (3 h), tevez 2, henry 2, ronaldinho 1, ibrahimovic 2; 0 Kommentare; weiter 3 Follower.
- Views/Reach weiterhin nicht abrufbar: Token hat noch keine Berechtigung instagram_business_manage_insights (Fehler #10).
- Likes stagnieren bei 1-2 pro Reel unabhaengig von Spieler/Caption -> Reichweite schwach, aber noch kein Unterschied messbar.
- Markt-Check: Instagram erlaubt seit Dez. 2025 nur noch 5 Hashtags; wir nutzten 7 (#careerpath, #futbol zu allgemein/schwach).
- Geaendert: Hashtags auf 5 gezielte reduziert (#footballquiz #guesstheplayer #football #soccer #footballtrivia). Video unveraendert, damit der Effekt messbar bleibt. 27 Quizze in der Warteschlange.
