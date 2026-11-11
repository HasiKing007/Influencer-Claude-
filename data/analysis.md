# Reelbot Auswertungen

## 2026-11-11 14:45 (Wien)
- Bisher 1 Reel (ibrahimovic, 06:52 UTC, manuell gestartet): 2 Likes, 0 Kommentare nach 7 h; 3 Follower.
- Views/Reach fehlen: Insights-Abfrage scheitert mit "(#10) Application does not have permission" -> Token braucht die Berechtigung instagram_business_manage_insights (Jacob muss Token neu erzeugen).
- Der geplante Lauf um 10:17 UTC ist nicht gestartet (GitHub-Cron ausgefallen), daher kein zweites Reel.
- Zu wenig Daten fuer inhaltliche Schluesse; Inhalt bleibt unveraendert.
- Geaendert: Ersatz-Cron-Termine (:47 und +1 h) mit Slot-Sperre in post.py (max. 1 Post pro 150 min, max. 3/Tag), Workflow holt vor dem Posten den neuesten Stand.
