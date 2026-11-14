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

## 2026-11-12 22:50 (Wien)
- Frische Insights (21:48 UTC): Satisfying-Reel "fill" steht nach 3,5 h weiter bei 139 Views/106 Reach -> auch der schnellere Start ist bei ~110 Reach eingefroren. Alle 7 Reels: 113-139 Views, 0 Shares, 0 Saves, 0 Kommentare, 3 Follower.
- Wiedergabe: fill 6,7 s von ~12 s (~55 %), Quiz-Reels 4,1-7,3 s von ~15 s (~27-48 %). Satisfying haelt besser, aber ohne Interaktion (Kommentare/Shares) gibt Instagram keinen zweiten Schub.
- Schluss: Uns fehlt ein Grund zum Kommentieren und Zuendeschauen. Top-Reels im Physik-Nischenbereich sind "Ball-Battles" (zwei Farben/Teams, wer gewinnt?): Zuschauer waehlen eine Seite, kommentieren und schauen bis zum Ende.
- MUTIGES EXPERIMENT (Markierung scene=duel): neue Szene "duel" = zwei Laender-Baelle (z. B. BRAZIL vs ARGENTINA, nur Namen/Farben, keine Logos) in rotierenden Ringen, echte Physik inkl. Ball-gegen-Ball-Stoss; Hook "X vs Y / Who escapes first?", Caption ruft zum Tippen in den Kommentaren auf, am Ende "X WINS!". Verbindet Fussball-Nische mit Satisfying-Physik.
- Geaendert: duel steht in formats.json als naechste Satisfying-Szene (morgen frueh). Messen: Kommentare + Views nach 24 h gegen fill (139) und Quiz (113-138). Quiz-Kuerzung (9 s) laeuft parallel, erstes kurzes Quiz morgen.

## 2026-11-13 15:45 (Wien)
- 9 Reels: alle 113-139 Views / 93-117 Reach, 0 Shares, 0 Saves, 0 Kommentare, 0-2 Likes, weiter 3 Follower. Duel (Experiment, 00:54 Wien gepostet): 133 Views, 6,7 s Wiedergabe = gleich wie fill (139). Kaka (erstes 9-s-Quiz, 10:39 UTC) noch ohne Insights.
- Format, Spieler, Caption und Laenge aendern nichts: jedes Reel friert bei ~110 Reach ein. Instagram testet es an einer kleinen Gruppe und bekommt null Interaktion zurueck -> kein zweiter Schub. Engpass ist Interaktion, nicht Optik.
- 14:17-UTC-Slot ist heute ausgefallen (weder Cron noch Waechter) -> manuell nachgestartet.
- MUTIGES EXPERIMENT (Markierung reveal=false): Quiz-Reels zeigen die Loesung NICHT mehr im Video, sondern enden mit "WHO IS IT? COMMENT YOUR ANSWER" (7,5 s statt 9 s). stats.py postet >=2 h spaeter die Antwort als Kommentar. Wer die Loesung wissen will, muss in die Kommentare -> Kommentare + Rueckkehr-Besuche + Loops.
- Messen: Kommentare und Views nach 24 h der reveal=false-Quizze gegen kaka (9 s mit Aufloesung) und die alten Quizze (113-138). Rotation bleibt 2x satisfying : 1x quiz.
- Nachtrag 15:50: Kaka (9-s-Quiz) nach 4 h 165 Views (bisher bestes Reel), 113 Reach, Wiedergabe 5,5 s von 9 s = 61 % (alte 15-s-Quizze 27-48 %) -> Kuerzung wirkt, Reach-Deckel bleibt. Erstes reveal=false-Quiz (torres) um 14:45 UTC gepostet.

## 2026-11-13 22:45 (Wien)
- 11 Reels, 4 Follower (+1 heute). Frische Insights 21:44 UTC: torres (erstes Quiz ohne Aufloesung) 176 Views/110 Reach, 3 Likes, 2 Kommentare (einer davon unsere Antwort) = bestes Reel bisher und erstes mit Kommentar. kaka (9-s-Quiz) 168, escape 165 (7,7 s Wiedergabe, beste Haltezeit), duel 134, fill 140, alte 15-s-Quizze 114-140.
- Reach-Deckel ~110 bleibt bei allen Formaten, 0 Shares/Saves. Aber: die kurzen Quizze (kaka, torres) holen die meisten Views, und nur das Quiz ohne Aufloesung erzeugt Interaktion. Duel brachte keine Kommentare.
- Geaendert: Rotation von 2x Satisfying : 1x Quiz auf 1x Satisfying : 2x Quiz (naechste Posts: Quiz anelka, dann Satisfying, dann 2 Quizze). Szene duel pausiert, Satisfying rotiert ueber escape/grow/slice/stack/fill.
- Messen: Kommentare/Likes je reveal=false-Quiz nach 24 h; wenn sie konstant >=1 echten Kommentar holen und ueber 170 Views liegen, Quiz als Hauptformat festlegen. Naechstes mutiges Experiment danach: staerkerer Hook in Sekunde 1 (Challenge-Text).

## 2026-11-14 14:45 (Wien)
- 13 Reels, 4 Follower (unveraendert). Frische Insights 13:50 UTC: torres 184 Views (2 Kommentare, davon 1 echter), anelka (2. Quiz ohne Aufloesung) 165 Views/109 Reach, 2 Likes, 0 echte Kommentare (nur unsere Antwort), grow 153 Views/123 Reach nach 3 h (hoechster Reach bisher), escape 166.
- Alle Reels weiter bei 110-125 Reach, 0 Shares/Saves. Quiz ohne Aufloesung haelt mit 7,3 s Wiedergabe von 7,5 s (anelka, ~97 %) sehr gut, aber nur 1 von 2 holte einen echten Kommentar -> Hook reicht nicht, um zum Mitmachen zu provozieren.
- MUTIGES EXPERIMENT (Markierung hook in state.json, quiz_hook=true): Quiz-Titel ist jetzt ein Challenge-Hook statt "GUESS THE PLAYER": rotierend "ONLY 1% CAN / NAME HIM", "TRUE FANS / GET THIS", "BET YOU CAN'T / GUESS HIM". Ziel: Ego-Reiz in Sekunde 1 -> mehr Kommentare/Shares. Video sonst unveraendert (7,5 s, reveal=false).
- Messen: echte Kommentare + Views nach 24 h je Hook-Variante gegen torres/anelka (165-184 Views, 0-1 echter Kommentar).
