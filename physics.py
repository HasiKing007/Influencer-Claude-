"""Kleine 2D-Physik-Engine fuer die Satisfying-Reels: Kugeln mit Schwerkraft, Stoessen untereinander,
an festen Stiften (Kreise) und Waenden (Strecken). Gleich schwere Kugeln, Impuls-Stoesse mit
Elastizitaet, Reibung entlang der Kontaktflaeche, Positionskorrektur gegen Durchdringen.
Aufprall-Ereignisse werden fuer den Ton mitgeschrieben.
"""
import numpy as np


class World:
    def __init__(self, gravity=1800.0, e_ball=0.35, e_wall=0.35, e_peg=0.4, friction=0.08, drag_x=0.0):
        self.g = gravity
        self.drag_x = drag_x          # Bremsung seitlicher Bewegung (Rollreibung/Luft)
        self.e_ball, self.e_wall, self.e_peg, self.mu = e_ball, e_wall, e_peg, friction
        self.p = np.zeros((0, 2))
        self.v = np.zeros((0, 2))
        self.r = np.zeros(0)
        self.tag = []                 # beliebige Daten je Kugel (z. B. Farbe)
        self.alive = np.zeros(0, bool)
        self.pegs = np.zeros((0, 3))  # x, y, radius
        self.segs = {}                # name -> [ax, ay, bx, by, dicke, aktiv, art]
        self.events = []              # (t, art, x, y, staerke 0..1)
        self.t = 0.0
        self._last_event = {}

    def add_ball(self, x, y, r, vx=0.0, vy=0.0, tag=None):
        self.p = np.vstack([self.p, [x, y]])
        self.v = np.vstack([self.v, [vx, vy]])
        self.r = np.append(self.r, r)
        self.alive = np.append(self.alive, True)
        self.tag.append(tag)

    def add_seg(self, name, ax, ay, bx, by, thick=6.0, kind="wall"):
        self.segs[name] = [ax, ay, bx, by, thick, True, kind]

    def _event(self, kind, x, y, speed, ref):
        # Ton-Ereignis, aber nicht oefter als alle 12 ms pro Art (sonst rauscht es nur)
        if speed < 60:
            return
        last = self._last_event.get(kind, -1)
        if self.t - last < 0.012:
            return
        self._last_event[kind] = self.t
        self.events.append((self.t, kind, float(x), float(y), float(min(1.0, speed / ref))))

    def step(self, dt, iterations=3):
        if len(self.r) == 0:
            self.t += dt
            return
        a = self.alive
        self.v[a, 1] += self.g * dt
        if self.drag_x:
            self.v[a, 0] *= 1 - self.drag_x * dt
        self.p[a] += self.v[a] * dt
        for _ in range(iterations):
            self._balls(dt)
            self._pegs()
            self._walls()
        self.t += dt

    def _balls(self, dt):
        idx = np.nonzero(self.alive)[0]
        if len(idx) < 2:
            return
        p, r = self.p[idx], self.r[idx]
        d = p[:, None, :] - p[None, :, :]
        dist = np.sqrt((d ** 2).sum(-1)) + 1e-9
        over = r[:, None] + r[None, :] - dist
        i, j = np.nonzero(np.triu(over > 0, 1))
        if len(i) == 0:
            return
        n = d[i, j] / dist[i, j][:, None]
        corr = (over[i, j] * 0.5)[:, None] * n
        gi, gj = idx[i], idx[j]
        np.add.at(self.p, gi, corr)
        np.add.at(self.p, gj, -corr)
        rv = self.v[gi] - self.v[gj]
        vn = (rv * n).sum(-1)
        hit = vn < 0
        if hit.any():
            imp = (-(1 + self.e_ball) * vn[hit] / 2)[:, None] * n[hit]
            np.add.at(self.v, gi[hit], imp)
            np.add.at(self.v, gj[hit], -imp)
            k = np.argmax(-vn[hit])
            pi = gi[hit][k]
            self._event("ball", self.p[pi, 0], self.p[pi, 1], -vn[hit][k], 600)

    def _bounce(self, sel, n, e, kind, ref):
        """Prallt Kugeln sel an einer Flaeche mit Normale n ab (mit Reibung)."""
        v = self.v[sel]
        vn = (v * n).sum(-1)
        hit = vn < 0
        if not hit.any():
            return
        vt = v - vn[:, None] * n
        vt_len = np.sqrt((vt ** 2).sum(-1)) + 1e-9
        # Coulomb-Reibung: bremst tangential hoechstens um mu * Normalimpuls
        cut = np.minimum(vt_len, self.mu * (1 + e) * np.abs(vn)) / vt_len
        new = vt * (1 - cut)[:, None] - (e * vn)[:, None] * n
        v[hit] = new[hit]
        self.v[sel] = v
        k = np.argmax(-vn * hit)
        self._event(kind, self.p[sel[k], 0], self.p[sel[k], 1], -vn[k], ref)

    def _pegs(self):
        if len(self.pegs) == 0:
            return
        idx = np.nonzero(self.alive)[0]
        d = self.p[idx, None, :] - self.pegs[None, :, :2]
        dist = np.sqrt((d ** 2).sum(-1)) + 1e-9
        over = self.r[idx, None] + self.pegs[None, :, 2] - dist
        bi, pi = np.nonzero(over > 0)
        if len(bi) == 0:
            return
        n = d[bi, pi] / dist[bi, pi][:, None]
        sel = idx[bi]
        self.p[sel] += over[bi, pi][:, None] * n
        self._bounce(sel, n, self.e_peg, "peg", 500)

    def _walls(self):
        idx = np.nonzero(self.alive)[0]
        for name, (ax, ay, bx, by, thick, active, kind) in self.segs.items():
            if not active:
                continue
            a = np.array([ax, ay])
            ab = np.array([bx - ax, by - ay])
            L2 = ab @ ab
            p = self.p[idx]
            u = np.clip(((p - a) @ ab) / L2, 0, 1)
            q = a + u[:, None] * ab
            d = p - q
            dist = np.sqrt((d ** 2).sum(-1)) + 1e-9
            over = self.r[idx] + thick / 2 - dist
            m = over > 0
            if not m.any():
                continue
            n = d[m] / dist[m][:, None]
            sel = idx[m]
            self.p[sel] += over[m][:, None] * n
            self._bounce(sel, n, self.e_wall, kind, 700)

    def cull(self, ymax):
        self.alive &= self.p[:, 1] < ymax
