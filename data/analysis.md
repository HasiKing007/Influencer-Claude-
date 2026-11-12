# Reelbot Auswertungen

> Hinweise fuer jede Auswertung (Stand 2026-11-11, von Jacob gewuenscht):
> - Ziel sind maximale Views. Bei jedem Lauf per Websuche vergleichen, was aktuell top-performende Fussball-Quiz-Reels/Shorts machen
>   (Schnitt, Tempo, Footage, Idee/Format, Sound, Effekte, Hook in der ersten Sekunde), und eins bis zwei Punkte davon uebernehmen.
> - Keine urheberrechtlich geschuetzten Spielszenen/TV-Clips (Jacob wollte sie, Claude hat abgelehnt). Erlaubt: frei lizenziertes
>   Stock-Footage (Pexels/Pixabay), sobald Jacob einen API-Key als Secret hinterlegt; eigene Animationen und eigener Sound.
> - Seit 2026-11-12: zwei Formate. "quiz" (render.py) und "satisfying" (satisfying.py, selbst gerenderte Neon-Physik-Endlos-Loops mit
>   synthetisiertem ASMR-Sound, Szenen escape/grow/fill/slice/stack, Physik in physics.py; Jacob mag huepfende Baelle + Abwechslung, nicht zu hektisch, Physik muss realistisch wirken; Pastell-Version lehnte er ab; gern neue Szenen ergaenzen). Reihenfolge und erlaubte Szenen in data/formats.json.
>   Jacob hat die Content-Entscheidung komplett an Claude uebertragen: Views pro Format/Szene vergleichen (state.json hat format+scene
>   je Post) und formats.json selbststaendig anpassen; Ziel ist eine Nische, sobald klar ist, was besser laeuft. Account/Name bleiben.
> - Explorative Forschung ausdruecklich erwuenscht (Jacob, 2026-11-12): neben kleinen Stellschrauben auch ganz neue Formate,
>   Hooks, Laengen, Stile testen. Ziel ist >=10.000 Views pro Reel; ~130 Views gelten als Misserfolg. Pro Lauf mindestens
>   ein mutiges Experiment einplanen und klar markieren, damit der Effekt messbar bleibt (nur die Reels mit diesem Merkmal vergleichen).
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

## 2026-11-12 20:45 (Wien), erste Insights
- Insights funktionieren seit neuem Token (Recht instagram_manage_insights ueber die Login-Konfiguration).
- 7 Reels: 113-139 Views, 92-117 Reach je Reel, 0 Shares, 0 Saves, 0-2 Likes; 3 Follower.
- Alle Reels bleiben bei ~100 Reach haengen = Instagram zeigt sie nur der ersten Testgruppe, ohne Shares/Saves gibt es keinen Push.
- Erstes Satisfying-Reel (18:22 UTC): 139 Views nach 1,3 h, also schnellster Start; Quiz-Reels brauchten dafuer ~1 Tag. Noch zu frueh fuer ein Urteil.
- Geaendert: stats.py fragt zusaetzlich die durchschnittliche Wiedergabezeit ab (zeigt, ob Leute bis zur Aufloesung bleiben).
- Wiedergabezeit im Schnitt 4,1-7,3 s, das Quiz-Reel dauert aber ~15 s (Aufloesung erst ab ~12 s) -> die meisten springen vor der Aufloesung ab. Kandidat fuer die naechste Aenderung: kuerzer/schneller bis zum Countdown.

## 2026-11-12 20:50 (Wien), Sofortmassnahme
- Jacob: ~130 Views sind viel zu wenig, Ziel >=10.000 pro Reel. Hauptproblem laut Daten: Wiedergabe 4-7 s bei ~15 s Laenge.
- Geaendert: Quiz-Reel von ~15 s auf ~9 s gekuerzt (Stationen max. 4,5 s statt 9 s, Countdown 2 s statt 3 s, Aufloesung 2,2 s statt 3,6 s). Ziel: Durchschauquote und Loops rauf. Messen: ig_reels_avg_watch_time im Verhaeltnis zur Laenge, Views nach 24 h.
