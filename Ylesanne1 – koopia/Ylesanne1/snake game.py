"""
Snake Kombaineeritud – PyCharm / pygame versioon
Klassikaline Snake + Slither.io + Worms

Juhtnupud:
  Nooleklahvid / WASD  – liikumine
  SPACE                – kiirenda (kulutab energiat)
  F                    – tulista valitud relv
  1 / 2 / 3 / 4        – vali relv
  ENTER                – alusta / restart
  ESC                  – välju
"""

import pygame
import random
import math
import sys

pygame.init()

# ── konstanded ──────────────────────────────────────────────────────────────
CELL = 22
COLS = 36
ROWS = 24
INFO_H = 90
W = COLS * CELL
H = ROWS * CELL
FPS = 60

# värvid
BG       = (10,  22,  40)
GRID     = (255, 255, 255,  8)
HEAD_COL = (74,  222, 128)
FOOD_COL = (34,  197,  94)
FOOD_HI  = (134, 239, 172)
ENERGY_C = (250, 204,  21)
WEAPON_C = (168,  85, 247)
TRAP_C   = ( 59, 130, 246)
UI_BG    = ( 20,  36,  60)
TEXT_C   = (200, 210, 230)
TEXT_DIM = (100, 120, 150)
WHITE    = (255, 255, 255)
RED      = (220,  50,  50)
ORANGE   = (251, 146,  60)
YELLOW   = (250, 204,  21)
PURPLE   = (168,  85, 247)
CYAN     = ( 34, 211, 238)

ENEMY_COLORS = [
    (239,  68,  68), (234, 179,   8), ( 16, 185, 129),
    ( 99, 102, 241), (236,  72, 153), ( 20, 184, 166),
]

# relvanimed + kirjeldused
WEAPONS = [
    {"name": "Tavalõks",  "color": TRAP_C,   "key": "1"},
    {"name": "Pomm",      "color": RED,       "key": "2"},
    {"name": "Välk",      "color": YELLOW,    "key": "3"},
    {"name": "Magnet",    "color": PURPLE,    "key": "4"},
]
INIT_AMMO = [999, 3, 2, 1]

# ── abifunktsioonid ──────────────────────────────────────────────────────────
def rnd(n): return random.randint(0, n - 1)

def glow(surf, x, y, r, col, alpha=80):
    s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*col[:3], alpha), (r, r), r)
    surf.blit(s, (x - r, y - r))

def draw_rounded_rect(surf, rect, col, radius=6, border=0, border_col=None):
    pygame.draw.rect(surf, col, rect, border_radius=radius)
    if border and border_col:
        pygame.draw.rect(surf, border_col, rect, border, border_radius=radius)

# ── fontid ───────────────────────────────────────────────────────────────────
F_LARGE  = pygame.font.SysFont("segoeui", 28, bold=True)
F_MED    = pygame.font.SysFont("segoeui", 17)
F_SMALL  = pygame.font.SysFont("segoeui", 14)
F_TINY   = pygame.font.SysFont("segoeui", 12)

# ── mänguklass ───────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((W, H + INFO_H))
        pygame.display.set_caption("Snake Kombaineeritud")
        self.clock = pygame.time.Clock()
        self.state = "idle"   # idle | running | dead
        self.snake = []; self.direction = (1,0); self.next_dir = (1,0)
        self.score = 0; self.energy = 0; self.lives = 3; self.speed = 1.0
        self.boost_t = 0; self.move_acc = 0.0; self.ammo = list(INIT_AMMO)
        self.weapon = 0; self.items = []; self.enemies = []; self.explosions = []
        self.zap_efx = []; self.mag_efx = []; self.traps = []; self.particles = []
        self.msg = ""; self.msg_t = 0; self._spawn_timer = 0.0

    # --- init -----------------------------------------------------------------
    def reset(self):
        self.snake      = [(8, ROWS//2), (7, ROWS//2), (6, ROWS//2)]
        self.direction  = (1, 0)
        self.next_dir   = (1, 0)
        self.score      = 0
        self.energy     = 0
        self.lives      = 3
        self.speed      = 1.0
        self.boost_t    = 0
        self.move_acc   = 0.0
        self.ammo       = list(INIT_AMMO)
        self.weapon     = 0
        self.items      = []
        self.enemies    = []
        self.explosions = []
        self.zap_efx    = []
        self.mag_efx    = []
        self.traps      = []
        self.particles  = []
        self.msg        = ""
        self.msg_t      = 0
        self._spawn_items(6)
        self._spawn_enemies(3)
        self.state = "running"

    # --- spawning -------------------------------------------------------------
    def _free_cell(self):
        occupied = set(self.snake)
        for _ in range(200):
            c = (rnd(COLS), rnd(ROWS))
            if c not in occupied:
                return c
        return None

    def _spawn_items(self, n):
        for _ in range(n):
            c = self._free_cell()
            if c is None: continue
            r = random.random()
            t = "food" if r < 0.50 else ("energy" if r < 0.80 else "weapon")
            self.items.append({"pos": c, "type": t, "phase": random.random() * math.pi * 2})

    def _spawn_enemies(self, n):
        for _ in range(n):
            side = rnd(4)
            if side == 0:   x, y, dx, dy = rnd(COLS), 0,        0,  1
            elif side == 1: x, y, dx, dy = COLS-1,    rnd(ROWS), -1, 0
            elif side == 2: x, y, dx, dy = rnd(COLS), ROWS-1,    0, -1
            else:           x, y, dx, dy = 0,         rnd(ROWS),  1, 0
            length = 3 + rnd(5)
            spd    = 0.30 + random.random() * 0.35
            col    = random.choice(ENEMY_COLORS)
            self.enemies.append({
                "body":  [(x, y)] * min(length, 3),
                "dir":   (dx, dy),
                "len":   length,
                "spd":   spd,
                "acc":   0.0,
                "color": col,
            })

    # --- liikumine ------------------------------------------------------------
    def _move_interval(self):
        if self.boost_t > 0:
            return 0.07
        return max(0.10, 0.22 - self.speed * 0.025)

    def _step(self):
        self.direction = self.next_dir
        hx = (self.snake[0][0] + self.direction[0]) % COLS
        hy = (self.snake[0][1] + self.direction[1]) % ROWS
        head = (hx, hy)

        if head in self.snake:
            self._die(); return

        # kontroll trap'idega
        trap_hit = next((t for t in self.traps if t["pos"] == head), None)
        if trap_hit:
            self.traps.remove(trap_hit)
            self._die(); return

        # kontroll vaenlastega
        for e in self.enemies:
            if head in e["body"]:
                self._die(); return

        self.snake.insert(0, head)
        grew = False

        # eset koristada
        hit = next((it for it in self.items if it["pos"] == head), None)
        if hit:
            self.items.remove(hit)
            if hit["type"] == "food":
                self.score += 10
                self.speed  = min(5.0, 1.0 + len(self.snake) * 0.05)
                grew = True
                self._particles(head, FOOD_COL, 12)
            elif hit["type"] == "energy":
                self.energy = min(100, self.energy + 20)
                self.score  += 5
                self._particles(head, ENERGY_C, 8)
            elif hit["type"] == "weapon":
                wi = rnd(3) + 1
                self.ammo[wi] += 1
                self.score += 5
                self._particles(head, WEAPON_C, 8)
                self._show_msg(f"+1 {WEAPONS[wi]['name']}")

        if not grew:
            self.snake.pop()

        if self.boost_t > 0:
            self.boost_t -= 1

        if len(self.items) < 5:
            self._spawn_items(2)

    def _move_enemies(self):
        for e in self.enemies:
            e["acc"] += e["spd"]
            if e["acc"] < 1.0: continue
            e["acc"] = 0.0
            if random.random() < 0.12:
                opts = [(1,0),(-1,0),(0,1),(0,-1)]
                e["dir"] = random.choice(opts)
            dx, dy = e["dir"]
            nx = (e["body"][0][0] + dx) % COLS
            ny = (e["body"][0][1] + dy) % ROWS
            e["body"].insert(0, (nx, ny))
            if len(e["body"]) > e["len"]:
                e["body"].pop()
            if e["body"][0] in self.snake:
                self._die()

    # --- surm -----------------------------------------------------------------
    def _die(self):
        self.lives -= 1
        head = self.snake[0]
        self._particles(head, RED, 20)
        if self.lives <= 0:
            self.state = "dead"
        else:
            self.snake = self.snake[:3]
            self._show_msg(f"Tabamust!  Elusid: {self.lives}")

    # --- tulistamine ----------------------------------------------------------
    def fire(self):
        w = self.weapon
        if self.ammo[w] <= 0: return
        if w != 0: self.ammo[w] -= 1
        hx, hy = self.snake[0]
        dx, dy = self.direction

        if w == 0:   # tavalõks
            tx = (hx + dx * 3) % COLS
            ty = (hy + dy * 3) % ROWS
            self.traps.append({"pos": (tx, ty), "life": 300})
            self._show_msg("Lõks asetatud!")

        elif w == 1:  # pomm
            ex = (hx + dx * 4) % COLS
            ey = (hy + dy * 4) % ROWS
            self.explosions.append({"x": ex, "y": ey, "r": 0.0, "a": 1.0})
            survivors = []
            killed = 0
            for e in self.enemies:
                if any(abs(b[0]-ex)<=2 and abs(b[1]-ey)<=2 for b in e["body"]):
                    killed += 1
                else:
                    survivors.append(e)
            self.enemies = survivors
            self.score += killed * 50
            self.items  = [it for it in self.items
                           if not (abs(it["pos"][0]-ex)<=2 and abs(it["pos"][1]-ey)<=2)]
            if killed: self._show_msg(f"Pomm! +{killed*50} punkti")

        elif w == 2:  # välk
            self.zap_efx.append({"x": hx, "y": hy, "life": 20})
            for e in self.enemies:
                e["body"] = e["body"][:max(1, len(e["body"])//2)]
                e["len"]   = len(e["body"])
            self.enemies = [e for e in self.enemies if e["len"] > 0]
            self.score  += 30
            self._show_msg("⚡ Välk!")

        elif w == 3:  # magnet
            self.mag_efx.append({"x": hx, "y": hy, "life": 50})
            for it in self.items:
                ix, iy = it["pos"]
                ddx, ddy = hx - ix, hy - iy
                if abs(ddx) < 7 and abs(ddy) < 7:
                    it["pos"] = ((ix + (1 if ddx > 0 else -1)) % COLS,
                                 (iy + (1 if ddy > 0 else -1)) % ROWS)
            self._show_msg("🧲 Magnet!")

    # --- efektid --------------------------------------------------------------
    def _particles(self, cell, col, n):
        cx = cell[0] * CELL + CELL // 2
        cy = cell[1] * CELL + CELL // 2
        for _ in range(n):
            angle = random.random() * math.pi * 2
            spd   = 1 + random.random() * 3
            self.particles.append({
                "x": cx, "y": cy,
                "vx": math.cos(angle) * spd, "vy": math.sin(angle) * spd,
                "col": col, "life": 20 + rnd(15),
            })

    def _show_msg(self, txt, duration=140):
        self.msg   = txt
        self.msg_t = duration

    # --- update ───────────────────────────────────────────────────────────────
    def update(self, dt):
        if self.state != "running": return

        self.move_acc += dt
        interval = self._move_interval()
        if self.move_acc >= interval:
            self.move_acc = 0.0
            self._step()
            self._move_enemies()

        # perioodiline lisamine
        self._spawn_timer = getattr(self, "_spawn_timer", 0) + dt
        if self._spawn_timer > 6.0:
            self._spawn_timer = 0.0
            self._spawn_enemies(1)

        # efektid
        self.explosions = [e for e in self.explosions
                           if (e.update({'r': e['r']+1.5, 'a': e['a']-0.06}) or True) and e['a'] > 0]
        # lihtsam update
        new_exp = []
        for e in self.explosions:
            e["r"] += 1.5; e["a"] -= 0.06
            if e["a"] > 0: new_exp.append(e)
        self.explosions = new_exp

        self.zap_efx = [z for z in self.zap_efx if (z.__setitem__("life", z["life"]-1) or True) and z["life"] > 0]
        self.mag_efx = [m for m in self.mag_efx if (m.__setitem__("life", m["life"]-1) or True) and m["life"] > 0]
        self.traps   = [t for t in self.traps   if (t.__setitem__("life", t["life"]-1) or True) and t["life"] > 0]

        for p in self.particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["vy"] += 0.1; p["life"] -= 1
        self.particles = [p for p in self.particles if p["life"] > 0]

        if self.msg_t > 0: self.msg_t -= 1

    # --- joonistamine ─────────────────────────────────────────────────────────
    def draw(self):
        sc = self.screen
        sc.fill(BG)

        # võre
        grid_surf = pygame.Surface((W, H), pygame.SRCALPHA)
        for x in range(COLS):
            pygame.draw.line(grid_surf, (255,255,255,6), (x*CELL,0), (x*CELL,H))
        for y in range(ROWS):
            pygame.draw.line(grid_surf, (255,255,255,6), (0,y*CELL), (W,y*CELL))
        sc.blit(grid_surf, (0, 0))

        t = pygame.time.get_ticks() / 1000.0

        # esemed
        for it in self.items:
            cx = it["pos"][0]*CELL + CELL//2
            cy = it["pos"][1]*CELL + CELL//2
            pulse = math.sin(t * 3 + it["phase"]) * 2
            r = int(5 + pulse * 0.4)
            if it["type"] == "food":
                glow(sc, cx, cy, 14, FOOD_COL, 50)
                pygame.draw.circle(sc, FOOD_COL, (cx, cy), r)
                pygame.draw.circle(sc, FOOD_HI,  (cx-1, cy-1), max(1, r-2))
            elif it["type"] == "energy":
                glow(sc, cx, cy, 14, ENERGY_C, 70)
                pygame.draw.circle(sc, ENERGY_C, (cx, cy), r)
            elif it["type"] == "weapon":
                glow(sc, cx, cy, 14, WEAPON_C, 60)
                rect = pygame.Rect(it["pos"][0]*CELL+3, it["pos"][1]*CELL+3, CELL-6, CELL-6)
                draw_rounded_rect(sc, rect, WEAPON_C, 4)
                lbl = F_TINY.render("W", True, WHITE)
                sc.blit(lbl, lbl.get_rect(center=(cx, cy)))

        # trapid
        for tr in self.traps:
            cx = tr["pos"][0]*CELL + CELL//2
            cy = tr["pos"][1]*CELL + CELL//2
            s = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
            pygame.draw.circle(s, (*TRAP_C, 120), (CELL//2, CELL//2), CELL//2-2)
            pygame.draw.circle(s, (*TRAP_C, 220), (CELL//2, CELL//2), CELL//2-2, 1)
            sc.blit(s, (tr["pos"][0]*CELL, tr["pos"][1]*CELL))

        # vaenlased
        for e in self.enemies:
            for i, (bx, by) in enumerate(e["body"]):
                alpha = int(255 * (1 - i / len(e["body"]) * 0.6))
                s = pygame.Surface((CELL-4, CELL-4), pygame.SRCALPHA)
                s.fill((*e["color"], alpha))
                sc.blit(s, (bx*CELL+2, by*CELL+2))
            if e["body"]:
                hx2, hy2 = e["body"][0]
                for ox in (5, 12):
                    pygame.draw.circle(sc, WHITE, (hx2*CELL+ox, hy2*CELL+6), 2)

        # uss
        for i, (sx, sy) in enumerate(self.snake):
            if i == 0:
                glow(sc, sx*CELL+CELL//2, sy*CELL+CELL//2, 18, HEAD_COL, 80)
                pygame.draw.rect(sc, HEAD_COL, (sx*CELL+1, sy*CELL+1, CELL-2, CELL-2), border_radius=4)
                dx2, dy2 = self.direction
                ex2 = sx*CELL + CELL//2 + dx2*5
                ey2 = sy*CELL + CELL//2 + dy2*5
                for ox2, oy2 in [( dy2*3, -dx2*3), (-dy2*3, dx2*3)]:
                    pygame.draw.circle(sc, WHITE, (ex2+ox2, ey2+oy2), 2)
            else:
                shade = max(30, 180 - i * 4)
                col   = (30, shade, 60)
                pygame.draw.rect(sc, col, (sx*CELL+2, sy*CELL+2, CELL-4, CELL-4), border_radius=3)

        # plahvatused
        for e in self.explosions:
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            a = int(e["a"] * 200)
            pygame.draw.circle(s, (239,68,68,a),   (int(e["x"]*CELL+CELL//2), int(e["y"]*CELL+CELL//2)), int(e["r"]*CELL//3))
            pygame.draw.circle(s, (251,191,36,a//2),(int(e["x"]*CELL+CELL//2), int(e["y"]*CELL+CELL//2)), int(e["r"]*CELL//5))
            sc.blit(s, (0,0))

        # välgud
        for z in self.zap_efx:
            a = int(z["life"] / 20 * 255)
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(s, (*YELLOW, a), (z["x"]*CELL+CELL//2, z["y"]*CELL+CELL//2), (W, z["y"]*CELL+CELL//2), 3)
            pygame.draw.line(s, (*YELLOW, a), (W, z["y"]*CELL+CELL//2), (W, 0), 3)
            sc.blit(s, (0,0))

        # magneti efekt
        for m in self.mag_efx:
            a  = int(m["life"] / 50 * 120)
            r2 = int((50 - m["life"]) * CELL // 8)
            if r2 > 0:
                s = pygame.Surface((W, H), pygame.SRCALPHA)
                pygame.draw.circle(s, (*PURPLE, a), (m["x"]*CELL+CELL//2, m["y"]*CELL+CELL//2), r2, 1)
                sc.blit(s, (0,0))

        # osakesed
        for p in self.particles:
            a = int(p["life"] / 35 * 220)
            pygame.draw.circle(sc, (*p["col"], min(255,a)), (int(p["x"]), int(p["y"])), 2)

        # ── HUD ──────────────────────────────────────────────────────────────
        hud_y = H
        pygame.draw.rect(sc, UI_BG, (0, hud_y, W, INFO_H))
        pygame.draw.line(sc, (40, 60, 90), (0, hud_y), (W, hud_y), 1)

        # statistika
        stats = [
            ("SKOOR",   str(self.score)),
            ("PIKKUS",  str(len(self.snake))),
            ("KIIRUS",  f"{self.speed:.1f}x"),
            ("ENERGIA", f"{self.energy}"),
            ("ELUSID",  str(self.lives)),
        ]
        col_w = W // len(stats)
        for i, (lbl, val) in enumerate(stats):
            cx2 = i * col_w + col_w // 2
            l   = F_TINY.render(lbl, True, TEXT_DIM)
            v   = F_MED.render(val, True, TEXT_C)
            sc.blit(l, l.get_rect(centerx=cx2, y=hud_y+6))
            sc.blit(v, v.get_rect(centerx=cx2, y=hud_y+22))

        # relvad
        wep_y = hud_y + 48
        wx    = 10
        for i, wp in enumerate(WEAPONS):
            active = self.weapon == i
            a_val  = self.ammo[i]
            out    = (a_val <= 0 and i != 0)
            bg     = (30, 50, 80) if active else UI_BG
            border = wp["color"] if active else (50, 70, 100)
            rect   = pygame.Rect(wx, wep_y, 140, 32)
            draw_rounded_rect(sc, rect, bg, 6, 1, border)
            icon_col = wp["color"] if not out else TEXT_DIM
            nm  = F_SMALL.render(f"[{wp['key']}] {wp['name']}", True, icon_col)
            amm = F_TINY.render("∞" if i==0 else str(a_val), True, TEXT_DIM if out else TEXT_C)
            sc.blit(nm,  nm.get_rect(x=wx+8,   centery=wep_y+16))
            sc.blit(amm, amm.get_rect(right=wx+132, centery=wep_y+16))
            wx += 150

        # sõnum
        if self.msg_t > 0:
            alpha = min(255, self.msg_t * 6)
            s     = F_MED.render(self.msg, True, YELLOW)
            sa    = pygame.Surface(s.get_size(), pygame.SRCALPHA)
            sa.blit(s, (0,0))
            sa.set_alpha(alpha)
            sc.blit(sa, sa.get_rect(centerx=W//2, y=hud_y-28))

        # energiariba
        if self.energy > 0:
            bar_w = int((W - 20) * self.energy / 100)
            pygame.draw.rect(sc, (40,60,80),  (10, hud_y-12, W-20, 6), border_radius=3)
            pygame.draw.rect(sc, ENERGY_C,    (10, hud_y-12, bar_w, 6), border_radius=3)

        # overlay ekraanid
        if self.state == "idle":
            self._draw_overlay("SNAKE KOMBAINEERITUD",
                ["Nooleklahvid / WASD – liikumine",
                 "SPACE – kiirenda (kulutab energiat)",
                 "F – tulista valitud relv   |   1-4 – vali relv",
                 "",
                 "ENTER – alusta mängu"])

        elif self.state == "dead":
            self._draw_overlay("MÄNG LÄBI",
                [f"Lõplik skoor:  {self.score}",
                 f"Pikkus:  {len(self.snake)}",
                 "",
                 "ENTER – mängi uuesti"])

        pygame.display.flip()

    def _draw_overlay(self, title, lines):
        ov = pygame.Surface((W, H), pygame.SRCALPHA)
        ov.fill((5, 12, 25, 190))
        self.screen.blit(ov, (0, 0))

        t  = F_LARGE.render(title, True, HEAD_COL)
        self.screen.blit(t, t.get_rect(centerx=W//2, centery=H//2 - 60))

        for i, ln in enumerate(lines):
            if not ln: continue
            c  = TEXT_C if i < len(lines)-1 else ENERGY_C
            s  = F_MED.render(ln, True, c)
            self.screen.blit(s, s.get_rect(centerx=W//2, centery=H//2 - 10 + i*26))

    # --- peaahela ─────────────────────────────────────────────────────────────
    def run(self):
        self.draw()   # idle ekraan kohe
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if event.type == pygame.KEYDOWN:
                    k = event.key

                    if k == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                    if k == pygame.K_RETURN:
                        if self.state != "running":
                            self.reset()

                    if self.state == "running":
                        if k in (pygame.K_UP,    pygame.K_w) and self.direction != (0,1):
                            self.next_dir = (0,-1)
                        elif k in (pygame.K_DOWN, pygame.K_s) and self.direction != (0,-1):
                            self.next_dir = (0,1)
                        elif k in (pygame.K_LEFT, pygame.K_a) and self.direction != (1,0):
                            self.next_dir = (-1,0)
                        elif k in (pygame.K_RIGHT,pygame.K_d) and self.direction != (-1,0):
                            self.next_dir = (1,0)
                        elif k == pygame.K_SPACE:
                            if self.energy >= 10:
                                self.energy  -= 10
                                self.boost_t  = 40
                                self.speed    = min(5.0, self.speed + 0.5)
                        elif k == pygame.K_f:
                            self.fire()
                        elif k == pygame.K_1: self.weapon = 0
                        elif k == pygame.K_2: self.weapon = 1 if self.ammo[1] > 0 else self.weapon
                        elif k == pygame.K_3: self.weapon = 2 if self.ammo[2] > 0 else self.weapon
                        elif k == pygame.K_4: self.weapon = 3 if self.ammo[3] > 0 else self.weapon

            self.update(dt)
            self.draw()


# ── käivitamine ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()



