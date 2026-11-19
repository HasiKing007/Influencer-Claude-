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

## 2026-11-14 22:45 (Wien)
- 16 Reels, 4 Follower (unveraendert). Frische Insights 21:45 UTC: robben (Hook "ONLY 1% CAN NAME HIM") 176 Views/110 Reach, 3 echte Kommentare = meiste Interaktion bisher; ronaldo-nazario (Hook "TRUE FANS GET THIS") 145 Views, 1 echter Kommentar, nur 5,2 s Wiedergabe; slice 152 Views/115 Reach nach 3 h.
- Reach-Deckel bleibt bei 106-126, weiter 0 Shares/0 Saves. Aber Quiz mit Challenge-Hook holt jetzt verlaessig echte Kommentare (4 in 2 Reels), Satisfying in 6 Reels 0 Kommentare und 0-3 Likes bei gleichen Views (134-166).
- Schluss: Kommentare sind das einzige Signal, das wir bewegen; Satisfying verwaessert ausserdem die Fussball-Nische des Accounts.
- Geaendert: Rotation nur noch Quiz (["quiz","quiz","quiz"]), Satisfying pausiert. Hook-Experiment laeuft weiter, damit "BET YOU CAN'T GUESS HIM" (Hook 2) auch Daten bekommt.
- Messen: echte Kommentare und Views je Hook nach 24 h; ob 3 Quizze/Tag mit Kommentaren den 110-Reach-Deckel knacken. 21 Quizze uebrig (~7 Tage bei 3/Tag) -> naechste Laeufe Vorrat auffuellen.

## 2026-11-15 14:55 (Wien)
- 17 Reels, 5 Follower (+1). Frische Insights 13:44 UTC: pirlo (Hook "BET YOU CAN'T GUESS HIM") nach 3 h 146 Views/111 Reach, 0 Likes, 0 echte Kommentare (nur unsere Antwort), Wiedergabe 4,9 s von 7,5 s. robben (Hook "ONLY 1%") 178 Views, 3 echte Kommentare, 7,4 s; ronaldo-nazario (Hook "TRUE FANS") 147 Views, 1 echter Kommentar, 5,2 s.
- Hook-Vergleich klar: "ONLY 1% CAN NAME HIM" gewinnt bei Views, Kommentaren und Haltezeit. Reach-Deckel 106-127 bleibt, 0 Shares und 0 Saves in allen 17 Reels.
- Schluss: Weitergeleitete Reels (Sends pro Reach) sind laut Instagram das wichtigste Signal fuer Reichweite bei Nicht-Followern, und genau das fehlt komplett. Wir haben nie zum Teilen aufgefordert.
- Geaendert (1): Hook fest auf "ONLY 1% CAN NAME HIM" (quiz_hook_fixed=0).
- MUTIGES EXPERIMENT (2, Markierung share_cta=true): Schlussbild zeigt "SEND THIS TO A FRIEND who thinks he knows football", Captions rotieren 3 Share-Aufforderungen. Messen: Shares und Views nach 24 h gegen robben (178 Views, 0 Shares).
- Vorrat: 5 Quizze ergaenzt (rooney, aguero, shevchenko, batistuta, ribery) -> 25 unveroeffentlicht.

## 2026-11-15 22:50 (Wien)
- 19 Reels, 5 Follower (unveraendert seit Mittag). Frische Insights 21:45 UTC: sneijder (erstes Reel mit Share-CTA "SEND THIS TO A FRIEND") nach 7 h 227 Views/149 Reach, 1 Share, 1 echter Kommentar = bestes Reel bisher, erster Share ueberhaupt und erstmals ueber dem ~110-Reach-Deckel. forlan (Share-CTA) nach 4,5 h 179 Views/124 Reach, 1 echter Kommentar. Vergleich robben (gleicher Hook, ohne CTA) 178 Views/111 Reach nach 31 h.
- Schluss: Share-Aufforderung wirkt (beide CTA-Reels ueber Reach-Deckel), auch wenn 1 Share noch duenn ist. Bleibt unveraendert, damit es weiter messbar ist.
- Geaendert: Warteschlange nach Bekanntheit sortiert, die Bekanntesten zuerst (rooney, aguero, buffon, fabregas, shevchenko, raul, van-nistelrooy, etoo, figo, owen). Bekanntere Spieler = mehr Leute, die die Antwort wissen und kommentieren/weiterschicken. Messen: Reach/Shares/Kommentare dieser 10 gegen sneijder/forlan.
- Vorrat: 23 unveroeffentlicht (ca. 7 Tage). Naechster mutiger Schritt, falls Reach wieder bei ~120 stehen bleibt: Share-CTA schon in Sekunde 1 statt erst im Schlussbild.

## 2026-11-16 14:50 (Wien)
- 21 Reels, 5 Follower (unveraendert seit 15.11.). Frische Insights 13:46 UTC: rooney (Share-CTA, bekanntester Spieler, aber von verspaetetem Cron um 23:50 Wien gepostet) 151 Views/109 Reach, 0 Shares, 1 echter Kommentar. aguero (10:41 UTC) nach 3 h nur 5 Views/0 Reach: auffaellig (sonst ~140 nach 3 h), vermutlich verzoegerte Insights; abends pruefen, ob das Reel nicht ausgespielt wurde.
- Share-CTA im Schlussbild: 3 Reels, zusammen 1 Share (sneijder 228/151). Shares bleiben fast null, weil die Aufforderung erst in den letzten 1,6 s kommt, wenn viele schon weg sind (Wiedergabe 4,2-6,2 s von 7,5 s).
- Geaendert (1): Geplante Cron-Laeufe posten nur noch 08-21 UTC (post.py Nachtruhe); rooney zeigt, dass Nacht-Posts schwach sind. Waechter/manuelle Starts unveraendert, 3 Reels/Tag bleiben.
- MUTIGES EXPERIMENT (2, Markierung share_early=true): neongruener Balken "SEND THIS TO A FRIEND WHO KNOWS BALL" ab Sekunde 0 unter der Liste, Schlussbild bleibt. Messen: Shares und Reach nach 24 h gegen sneijder/forlan/rooney.
- Vorrat: 21 unveroeffentlicht.

## 2026-11-16 22:45 (Wien)
- 24 Reels, 5 Follower (seit 15.11. unveraendert). Frische Insights 21:02 UTC: buffon (erstes Reel mit Share-Balken ab Sekunde 0) nach 6,5 h 194 Views/119 Reach, 1 Share, 4 Likes, 3 echte Kommentare = zweitbestes Reel bisher. fabregas (Share-Balken) nach 2,5 h 148/108, 0 Shares, nur 3,9 s Wiedergabe. aguero bleibt nach 10 h bei 6 Views/0 Reach: Reel wurde praktisch nicht ausgespielt (Ursache unklar, kein Muster bei Caption/Video). shevchenko (20:30 UTC) noch zu frisch.
- Share-Balken ab Sekunde 0: 1 Share in 2 auswertbaren Reels, gleiches Niveau wie Share-CTA nur im Schlussbild (sneijder). Laeuft weiter, Urteil morgen.
- Schluss: Seit 24 Reels Reach-Deckel 107-151 und kaum Follower. Das Quiz ist eine Wissensfrage, bei der die meisten nichts beitragen koennen; Debatten-/Meinungsformate sind im Fussball-Nischen-Markt die klassischen Kommentar- und Weiterschick-Treiber.
- MUTIGES EXPERIMENT (Markierung format=pick): neues Format "PICK ONE from each row" (Dream-Team: GK/DEF/MID/WING/ST je 3 Legenden, 5 s, "COMMENT YOUR TEAM" + "SEND THIS TO A FRIEND AND COMPARE"). Rotation quiz, pick, quiz: morgen 14:41 Wien erstes Pick-Reel, Quiz-Einstellungen unveraendert.
- Messen: Kommentare, Shares, Reach und Wiedergabe-Quote (5-s-Video, Loops) des Pick-Reels gegen Quiz-Schnitt (~150-190 Views, 0-1 Share). Vorrat: 18 Quizze, 6 Pick-Sets.

## 2026-11-16 23:05 (Wien), Richtungswechsel (Jacob: mehr recherchieren, viel mehr ausprobieren, Frequenz rauf)
- Stand: 24 Reels, alle 107-227 Views, 5 Follower. Kleine Stellschrauben am Quiz haben den Reach-Deckel nicht geknackt.
- Recherche: Fallstudie eines Faceless-Accounts (79 Reels in 5 Wochen, Median 634 Views): Top-Reel 92.850 Views war eine nummerierte Liste, die sich Zeile fuer Zeile fuellt, mit Versprechen in Zeile 1; Erfolg kam aus Menge + vielen Varianten, nicht aus einem perfekten Format (https://www.ootto.ai/blog/do-faceless-instagram-accounts-work). Buffer (2,1 Mio. Posts): mehr Posts/Woche = mehr Reach pro Post (+24 % bei 10+/Woche) und schnelleres Follower-Wachstum, abnehmender Zusatznutzen (https://buffer.com/library/how-often-to-post-on-instagram/). Faceless-Guides: Voiceover, Text-Overlay, Grund bis zum Ende zu schauen, Kommentar-Mechanik (https://fluxnote.io/guides/faceless-instagram-reels-ideas-2026). Trial Reels (nur Nicht-Follower) gehen per API (trial_params), brauchen aber >=200 Follower -> spaeter.
- Uns fehlte bisher komplett: Stimme (alle Reels nur Piepton) und Abwechslung im Format.
- Geaendert (Markierung format=facts/odd/rank, voice=true/false): drei neue Formate mit KI-Stimme (edge-tts): facts (Liste #5->#1, "#1 IS INSANE", Fussball + allgemeine Themen), odd (Suchbild "find the odd one", 6-s-Countdown, breites Publikum), rank (Blind Ranking 1-5, Fussball + allgemein). Quiz und Pick laufen weiter.
- Frequenz: 3 -> 5 Reels/Tag (10:17, 12:17, 14:17, 16:17, 19:17 Wien). Mehr Frequenz loest den Reach-Deckel nicht allein, aber wir testen pro Tag 5 statt 3 Varianten. Rotation quiz, facts, odd, rank, pick, quiz (6 bei 5/Tag -> wandert durch die Slots).
- Messen: Views/Reach/Shares/Kommentare/Wiedergabe-Quote je Format nach 24 h. Nach 4-5 Posts je Format: Verlierer raus, Format mit Ausreisser bekommt mehr Slots und Varianten. Auswertung recherchiert ab jetzt jeden Lauf selbststaendig neue Formate.

## 2026-11-17 14:50 (Wien)
- Stand (Insights 13:40 UTC): 27 Reels, 5 Follower (seit 15.11. unveraendert). Slots heute alle gelaufen (raul 10:40, facts 12:41, odd 14:40 Wien), kein Ersatzlauf noetig.
- Zahlen: raul (Quiz) nach 4 h 178 Views/125 Reach, 2 Kommentare, 0 Shares. Erstes facts-Reel (KI-Stimme, ~18 s) nach 2 h 116 Views/107 Reach, 0 Kommentare, 0 Shares, aber 8,4 s Wiedergabe = laengste bisher (Quiz 4,1-7,4 s), allerdings nur ~45 % der Laenge. odd gerade erst gepostet (0). rank/pick laufen heute 16:17/19:17. Alles weiterhin weit unter 10.000, kein Ausreisser. Fuer ein Urteil zu facts/odd/rank zu frueh (je 0-1 Post).
- Recherche:
  - Sechs-Wochen-Test eines Accounts: unter 15 s lange Text-Neugier-Reels 14.700-16.900 Views/Woche gegen 2.100-2.600 bei 30-60-s-Reels; 7-15 s gilt als Loop-Bereich (https://www.lilachbullock.com/instagram-reels-types-more-views/, ein Account, nicht kontrolliert).
  - Faceless-Reels verschwenden oft die ersten 2-3 s mit Vorspann; Hook gehoert ins erste Bild. Eigene Original-Tonspur soll bei KI-Videos besser laufen als doppelt genutzte Trend-Audios; Shares zaehlen stark, Likes wenig (https://reelforgeai.io/blog/instagram-reels-reach-collapse-q1-2026, Herstellerseite, Beobachtungen, keine Meta-Zahlen). Passt zu unserer eigenen Synth-Tonspur.
  - Quiz-/Entscheidungs-Reels: Frage, ~3 s Pause, dann Aufloesung, unter 15-20 s (https://typito.com/blog/quiz-reels-trend-report-boost-engagement/, unbelegt).
- Schluss: Unsere Kommentare kommen fast nur beim Quiz (Wissensfrage, schliesst viele aus). Eine Entscheidungsfrage ohne Vorwissen, kurz, Hook ab Frame 0, ist der naheliegende naechste Test, und sie spricht ein breiteres Publikum als Fussball an.
- MUTIGES EXPERIMENT (Markierung format=wyr): neues Format "Would you rather" (wyr.py, data/wyr.json, 16 Fragen, meist Nicht-Fussball): Bild halb rot/halb blau, beide Optionen ab Frame 0, KI-Stimme liest die Frage, 3-2-1, "COMMENT RED OR BLUE", ~6-7 s fuer Loops. Keine erfundenen Abstimmungs-Prozente. 2 von 7 Rotationsplaetzen.
- Rotation neu (7 Plaetze, teilerfremd zu 5): pick, wyr, quiz, facts, odd, wyr, rank. So geordnet, dass heute 16:17 rank und 19:17 pick wie geplant laufen; erstes wyr morgen 10:17.
- Vorrat: +1 Fakten-Set "space" (Venus-Tag > Venus-Jahr, Pulsar 716/s, Mond-Fussabdruecke, Saturn-Dichte, Licht 8 min; geprueft u. a. https://www.snopes.com/fact-check/one-day-on-venus-is-longer-than-a-year-on-venus/, https://www.livescience.com/facts-about-saturn). Jetzt unveroeffentlicht: 17 Quizze, 5 facts, 8 rank, 6 pick, 16 wyr.
- Messen: wyr gegen pick/quiz bei Kommentaren je 100 Reach, Shares, Wiedergabe-Quote (Wiedergabe / Laenge, >100 % = Loops) nach 24 h. Naechster Kandidat fuer kleine Aenderung: facts auf <15 s kuerzen, falls die Quote unter 50 % bleibt.

## 2026-11-17 22:50 (Wien)
- 29 Reels, 5 Follower (unveraendert seit 15.11.). Alle 5 Slots heute gepostet. Frische Insights 21:44 UTC (Alter in Klammern):
  - pick-legends (3 h): 184 Views/112 Reach, **5 Shares** (Rekord, bisher nie mehr als 1 pro Reel), 0 Kommentare, 5,2 s Wiedergabe bei ~5 s Laenge (>100 % = Loops).
  - odd (8 h): 176/121, 2 Saves (erste Saves ueberhaupt), 5,5 s.
  - quiz raul (12 h): 181/129, 2 Kommentare, 4,4 s.
  - rank-strikers (6 h): 135/106, 0 Interaktion, 8,3 s.
  - facts (10 h): 117/108, 0 Interaktion, 8,4 s von ~18 s.
- Ehrlich: weiterhin alles bei 110-130 Reach, Faktor ~60 unter dem 10.000er-Ziel. Aber pick ist das erste Format mit einem echten Ausreisser bei dem Signal, das laut Instagram Reichweite bei Nicht-Followern treibt (Weiterleitungen). facts und rank sind bisher am schwaechsten (je 1 Post, noch kein Urteil).
- Recherche (neue Blickwinkel):
  - Instagram hat seit Maerz 2026 Tippen-zum-Pausieren (ein Tipp pausiert, Mute ist ein eigener Knopf); profitieren sollen text-lastige Reels, die man zum Lesen anhaelt (https://www.inro.social/blog/how-to-pause-instagram-reels-in-2026-tap-to-pause-is-finally-here, Herstellerblog). Darauf baut das Interaktions-Genre "Pause the video - what you land on is yours" auf.
  - Analyse von 40 viralen KI-Reels: fast alle starken Posts haben ein Kommentar-Stichwort ("Comment X"), Kommentare/Likes bis 2,9x; Text in Safe-Zones (150 px oben, 170 px unten), Schrift >= 56 px (https://dev.to/whoffagents/i-studied-40-viral-ai-reels-to-find-what-actually-works-with-real-numbers-m6e, kleine Stichprobe, Verkaeufer).
  - Faceless-Accounts posten 2-5 Reels/Tag; Setup-Spannung-Aufloesung auch in 15 s; "Facts you didn't know" als Nische genannt, aber ohne Zahlen (https://myinstantplay.com/blog/ai-reels-exploding-how-creators-get-10m-views-without-showing-face, Werbeblog, unbelegt).
- Schluss: Formate ohne Vorwissen, bei denen jeder ein persoenliches Ergebnis hat (pick: "mein Team"), werden weitergeschickt. Das naechste logische Experiment ist ein Format, bei dem jeder ein *zufaelliges* persoenliches Ergebnis bekommt und es nur durch Mitmachen erfaehrt.
- MUTIGES EXPERIMENT (Markierung format=pause): neues Format "Tap to pause" (pause.py, data/pauses.json, 8 Sets, halb Fussball, halb allgemein): 12er-Raster, gelbe Markierung springt alle 0,1 s zufaellig, "TAP TO PAUSE / WHAT YOU LAND ON IS YOUR FOOTBALL CAREER", KI-Stimme, "COMMENT WHAT YOU GOT", 6,5 s, laeuft endlos im Loop (Nochmal-Versuchen = Wiederholungen). 1 von 9 Rotationsplaetzen, erstes am 18.11. 14:17 Wien.
- Verdoppeln: pick jetzt 2 von 9 Plaetzen (vorher 1 von 7). Neues Nicht-Fussball-Set pick-dream-life (Haus/Stadt/Job/Kraft/Haustier) als naechstes pick (18.11. 12:17), dazu pick-world-cup (alle 15 Spieler sind Weltmeister, geprueft mit https://www.wikiwand.com/en/articles/List_of_FIFA_World_Cup_winning_players). pick-Sets koennen jetzt eigene caption/tags/Endtext haben.
- Rotation (9, teilerfremd zu 5): facts, odd, wyr, pick, pause, quiz, wyr, rank, pick. Morgen: 10:17 wyr, 12:17 pick, 14:17 pause, 16:17 quiz, 19:17 wyr.
- Vorrat unveroeffentlicht: 17 Quizze, 5 facts, 7 rank, 7 pick, 16 wyr, 8 pause.
- Messen nach 24 h: Shares je 100 Reach (pick-legends = 4,5) und Kommentare je 100 Reach fuer pause, wyr, pick-dream-life vs. pick-legends; Wiedergabe-Quote. Ziel: ein Format mit >= 3 Shares/100 Reach bestaetigt sich zweimal -> dann Haelfte der Rotation darauf. facts/rank: wenn die zweiten Posts wieder <140 Views und 0 Interaktion -> raus.

## 2026-11-18 14:50 (Wien)
- 32 Reels, 5 Follower (seit 15.11. unveraendert). Heutige Slots 10:40, 12:40, 14:40 Wien alle gepostet. Frische Insights 13:41 UTC.
- Zahlen (Views/Reach, Shares, Wiedergabe): pick-legends (19 h) 184/114, 5 Shares, 5,2 s von 5 s = weiter einziger Share-Ausreisser. odd 178/122, 2 Saves, 5,6 s. quiz raul 181/129. rank 135/106, 8,3 s. facts 117/108, 8,4 s. wyr-time-travel (4 h) 147/110, 0 Shares, 0 Kommentare, nur 3,7 s Wiedergabe = schwach. pick-dream-life (2 h) 36/26, 1 Save, noch zu frisch. pause (gerade gepostet) lief OHNE Stimme (edge-tts-Aussetzer im Actions-Lauf, wyr 3 h vorher hatte Stimme).
- Ehrlich: kein einziges Reel ueber 230 Views, Reach-Deckel ~110-150 haelt seit 32 Reels, egal welches Format. Weit weg von 10.000.
- Recherche (neu): (1) Instagram sagt in den Creator-Richtlinien, dass Reels, die ueberwiegend aus Text bestehen, seltener an Nicht-Follower empfohlen werden (https://creators.instagram.com/recommendations-and-Originality, zitiert in https://designerbox.ai/blog/faceless-reels/). Alle unsere Formate sind praktisch reine Text-Tafeln, das passt zum Reach-Deckel. (2) Visuelle Quiz-Kanaele (Flaggen-/Emoji-Raetsel, z. B. Guessr 11 Mio. Views, Quiz Dino 10 Mio. bei einem Emoji-Quiz) laut https://typito.com/blog/how-ai-quiz-videos-are-changing-reels-engagement-in-2026/ (Herstellerblog, Zahlen nicht selbst geprueft). (3) Kommentar-Mechanik: Accounts mit hohem Kommentar-zu-Like-Verhaeltnis nutzen eine konkrete Kommentar-Aufgabe (Zahl/Stichwort statt offener Frage), https://dev.to/whoffagents/i-studied-40-viral-ai-reels-to-find-what-actually-works-with-real-numbers-m6e (nur 5 Accounts, schwach belegt). 2026 ausserdem verschaerfte Originalitaets-Regeln gegen Repost-Inhalte (https://petapixel.com/2026-04-30/new-instagram-policies-target-reposted-content/) - wir sind mit selbst gerenderten Inhalten auf der sicheren Seite.
- MUTIGES EXPERIMENT (Markierung format=flags): neues Format "Guess the flag" (flags.py, data/flags.json, 10 Sets): grosse, selbst gezeichnete Nationalflaggen fuellen das Bild (kaum Text), 4 Flaggen EASY -> MEDIUM -> HARD -> IMPOSSIBLE je 2 s mit Timer-Balken und Ticks, dann Aufloesung im 2x2-Raster, "COMMENT YOUR SCORE /4" (konkrete Zahl als Kommentar), 10,6 s Loop, KI-Stimme nur im Hook. Weltweites Thema ohne Sprach-/Fussball-Huerde. Ersetzt den zweiten wyr-Platz. Rotation: facts, odd, wyr, pick, pause, quiz, flags, rank, pick -> heute 16:17 quiz, 19:17 erstes flags.
- Kleine Korrektur: KI-Stimme versucht es jetzt 3x mit Pause statt 2x (pause lief heute stumm).
- Vorrat: +2 Nicht-Fussball-Pick-Sets (pick-dream-day, pick-survival). Unveroeffentlicht: 17 Quizze, 5 facts, 7 rank, 8 pick, 15 wyr, 7 pause, 10 flags.
- Messen: flags gegen Text-Formate bei Views/Reach nach 24 h (Hypothese: Bild-Reel durchbricht den ~120-Reach-Deckel), Kommentare je 100 Reach, Wiedergabe-Quote (10,6 s). Wenn flags >= 300 Views oder >= 3 Kommentare: verdoppeln und weitere Bild-Formate bauen (Umriss-/Farb-Raetsel). wyr: zweiter Post entscheidet. facts/rank: zweiter Post <140 Views und 0 Interaktion -> raus.

## 2026-11-18 22:50 (Wien)
- 34 Reels, 5 Follower (seit 15.11. unveraendert). Alle 5 Slots heute gepostet (10:40, 12:40, 14:40, 16:39, 19:08 Wien). Frische Insights per Dry-Run 21:45 UTC.
- Zahlen heute (Views/Reach, Shares, Kommentare, Wiedergabe von Laenge):
  - flags-1 (erstes Bild-Format, 3,5 h): 158/116, 0 Shares, 0 Kommentare, 3 Likes, 5,6 s von 10,6 s (53 %).
  - quiz van-nistelrooy (6 h): 156/108, 1 Kommentar, 4,9 s.
  - pause (ohne Stimme, 8 h): 141/109, 1 Kommentar, 3,0 s von 6,5 s (46 %, schwaechste Quote).
  - pick-dream-life (10 h): 123/84, 1 Save, 1 Kommentar, 0 Shares, 4,0 s.
  - wyr-time-travel (12 h): 149/112, 0 Interaktion, 3,7 s von ~7 s.
- Ehrlich: Auch das erste Bild-Format bleibt im selben Deckel. Seit 34 Reels landet JEDES Reel bei 84-129 Reach, unabhaengig von Format, Thema, Stimme oder Uhrzeit. Das sieht nach dem festen Test-Publikum aus, das Instagram jedem neuen Reel gibt; keines hat genug Signal geliefert, um in die naechste Stufe zu kommen. Faktor ~60-80 unter 10.000. Bestes Format bisher weiter pick-legends (5 Shares), aber der zweite pick (dream-life) hat den Ausreisser nicht wiederholt.
- Recherche (neue Blickwinkel, alles Herstellerblogs, Zahlen nicht unabhaengig belegt):
  - Mosseri (Mai 2026, zitiert bei https://virlo.ai/blog/instagram-reels-algorithm-2026-decoded) trennt "connected" (Follower) und "unconnected" Reach (Nicht-Follower) als getrennte Wertungen; mit 5 Followern ist praktisch alles unconnected. Entscheidend sei die Abschluss-/Wiedergabe-Quote der fremden Erstseher. Unsere Quoten liegen bei 46-55 %, nur pick (5 s) ueber 100 %.
  - Illusions-/"wie geht das"-Reels: Leute schauen mehrfach, um den Effekt nochmal zu erleben; Beispiel ~4 Mio. Views, ausserdem "Loading 0-100 %"-Fortschritts-Reels als eingebauter Grund zum Dranbleiben (https://www.anijam.ai/blog/instagram-reels-trends/).
  - Loop-Technik fuer Raetsel: "Did you catch that?" (Aufloesung so kurz, dass man nochmal schaut), kein Schwarzbild/keine Pause am Ende, Loops nur unter 15 s sinnvoll (https://joyspace.ai/looping-hack-trick-algorithm-double-views). Die dort genannten Punkt-Gewichte sind ausdruecklich Spekulation, nicht verwendet.
- Schluss: Raetsel mit Wissenshuerde (Quiz, Flaggen) und Meinungsfragen bringen den fremden Erstsehern zu wenig Grund, bis zum Ende und nochmal zu schauen. Ein Wahrnehmungs-Effekt, den jeder am eigenen Auge erlebt, ist ohne Vorwissen, ohne Sprache und baut den Wiederholungs-Grund direkt ein.
- MUTIGES EXPERIMENT (Markierung format=illusion): neues Format "Stare at the dot" (illusion.py, data/illusions.json, 10 Sets): selbst gezeichnete Flagge in Komplementaerfarben, 8 s auf den schwarzen Punkt starren (Countdown, KI-Stimme), dann wird der Schirm hell und das Auge sieht die echte Flagge als Nachbild (klassischer Wahrnehmungseffekt). Die echten Farben werden nie gezeigt: "WHICH FLAG DO YOU SEE? / COMMENT THE COUNTRY", 12,6 s Loop ("Didn't work? Watch again"). Ersetzt den zweiten pick-Platz.
- Rotation (9): facts, odd, wyr, pick, pause, quiz, flags, rank, illusion -> morgen 10:17 rank, 12:17 erstes illusion, 14:17 facts, 16:17 odd, 19:17 wyr. Damit kommen auch facts, rank und wyr zu ihrem zweiten Post (Kill-Entscheid).
- Keine kleine Aenderung diesmal (bewusst, damit flags/pause/illusion sauber vergleichbar bleiben).
- Vorrat unveroeffentlicht: 16 Quizze, 5 facts, 7 rank, 8 pick, 15 wyr, 7 pause, 9 flags, 10 illusion.
- Messen nach 24 h: illusion gegen flags (gleiche Flaggen-Optik, anderer Mechanismus) bei Reach, Wiedergabe-Quote (Ziel >80 %) und Kommentaren je 100 Reach. Wenn illusion >= 250 Views oder Quote >= 80 % -> verdoppeln und weitere Wahrnehmungs-Effekte bauen (Bewegungs-Nachbild, Farb-Illusionen). flags: zweiter Post entscheidet. facts/rank/wyr: zweiter Post <140 Views und 0 Interaktion -> raus.

## 2026-11-19 14:50 (Wien) - RICHTUNGSWECHSEL: eine Nische (mit Jacob abgestimmt)
- Befund: 37 Reels in 9 Formaten, jedes Reel 84-129 Reach, Wiedergabe 3-7 s, 5 Follower. Streuung verhindert, dass Instagram eine Zielgruppe findet; 5 automatisierte Posts/Tag bei 5 Followern koennen wie Spam wirken.
- Neu: Rotation nur noch "pick" (Fussball, pick one per row), Nicht-Fussball-Sets (topic general) werden uebersprungen. 20 neue Fussball-Sets (Vereine, Nationalteams, GOATs, Ballon d'Or, aktuelle Stars, Stuermer je Jahrzehnt) -> ~8 Tage Vorrat.
- pick v2 (state v=2): komplettes Brett ab Frame 0 (vorher leeres Bild, Reihen flogen nacheinander rein), grosser Challenge-Hook oben (3 Varianten rotierend, state "hook": 0 "YOU CAN ONLY KEEP ONE", 1 "99% CAN'T PICK JUST ONE", 2 "THE HARDEST CHOICE EVER"), KI-Stimme liest den Hook, gelbe Markierung springt Reihe fuer Reihe, ~5,2 s Loop. Dry-Run auf Actions mit Stimme ok.
- 3 Posts/Tag (12:17, 16:17, 19:17 Wien), MAX_PER_DAY=3. Waechter- und Analyse-Aufgabe neu angelegt (alte deaktiviert).
- Handposts: Jacob postet 3 Abende je 1 Reel (20:30-21:30 Wien) von Hand mit Trend-Sound: manual/reel-1-goats.mp4, reel-2-man-utd.mp4, reel-3-brazil.mp4 (stumm, 6,5 s; Sets mit manual=true). In stats.json = Media-IDs, die nicht in state.json stehen.
- Messen: v2 gegen die alten 34 Reels (Reach, Wiedergabe-Quote, Shares/100 Reach), Hooks untereinander, Handposts mit Trend-Sound gegen Bot-Posts. Erstes v2-Reel 20.11. 12:17 (heute sind die 3 Posts schon gelaufen).
