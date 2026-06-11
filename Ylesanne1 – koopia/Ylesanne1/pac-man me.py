import pygame, sys, math, random

BLACK     = (  0,   0,   0)
WHITE     = (255, 255, 255)
WALL_COL  = ( 33,  33, 222)
NEON_BLUE = (100, 180, 255)
YELLOW    = (255, 220,   0)
RED       = (220,   0,   0)
PINK      = (255, 140, 210)
CYAN      = (  0, 220, 220)
ORANGE    = (255, 150,   0)
SCARED_C  = ( 20,  20, 200)
SCARED2_C = (255, 255, 255)
DOT_COL   = (255, 200, 100)
POWER_COL = (255,  60, 200)

TILE   = 28
COLS   = 21
ROWS   = 21
WIN_W  = COLS * TILE
WIN_H  = ROWS * TILE + 56
FPS    = 60
SPEED  = 2
GHOST_SPEED = 2
# Iga kummituse kiirus eraldi (tile per frame skaala)
GHOST_SPEEDS = [2, 2, 2, 2]
# Mitu frame'i oodata enne ghost-house'ist väljumist
GHOST_LEAVE_DELAY = [0, 180, 360, 540]  # Blinky kohe, teised 3/6/9 sek hiljem

POWER_TIME   = 420
SCARED_FLASH = 120

MAP_STR = [
    "111111111111111111111",
    "100000000010000000001",
    "101110111010111011101",
    "1P1110111010111011P01",
    "101110111010111011101",
    "100000000000000000001",
    "101110101111101011101",
    "100000100000001000001",
    "111110111010111011111",
    "111110100000010011111",
    "111110101GGG101011111",
    "111110100000010011111",
    "111110101111101011111",
    "100000100000001000001",
    "101110101111101011101",
    "100000000000000000001",
    "101110111010111011101",
    "1P0000000000000000P01",
    "101110111010111011101",
    "100000000010000000001",
    "111111111111111111111",
]

PAC_COL = 10
PAC_ROW = 15

def parse_map():
    wall_set, dots, powers, ghost_starts = set(), [], [], []
    for r, row in enumerate(MAP_STR):
        for c, ch in enumerate(row):
            if ch == '1':
                wall_set.add((c, r))
            elif ch == '0':
                dots.append((c, r))
            elif ch == 'P':
                dots.append((c, r))
                powers.append((c, r))
            elif ch == 'G':
                ghost_starts.append((c, r))
    return wall_set, dots, powers, ghost_starts

def is_wall(wall_set, c, r):
    return (c, r) in wall_set or c < 0 or c >= COLS or r < 0 or r >= ROWS

def build_wall_surface(wall_set):
    surf = pygame.Surface((WIN_W, WIN_H))
    surf.fill(BLACK)
    E = max(3, TILE // 7)
    H = max(1, E // 3)
    for (c, r) in wall_set:
        x, y = c * TILE, r * TILE
        if (c, r-1) not in wall_set:
            pygame.draw.rect(surf, WALL_COL,  (x, y, TILE, E))
            pygame.draw.rect(surf, NEON_BLUE, (x, y, TILE, H))
        if (c, r+1) not in wall_set:
            pygame.draw.rect(surf, WALL_COL,  (x, y+TILE-E, TILE, E))
            pygame.draw.rect(surf, NEON_BLUE, (x, y+TILE-H, TILE, H))
        if (c-1, r) not in wall_set:
            pygame.draw.rect(surf, WALL_COL,  (x, y, E, TILE))
            pygame.draw.rect(surf, NEON_BLUE, (x, y, H, TILE))
        if (c+1, r) not in wall_set:
            pygame.draw.rect(surf, WALL_COL,  (x+TILE-E, y, E, TILE))
            pygame.draw.rect(surf, NEON_BLUE, (x+TILE-H, y, H, TILE))
    return surf

def draw_pacman(surf, cx, cy, rad, angle_deg, mouth_frac):
    mouth = mouth_frac * 35
    sa = math.radians(angle_deg + mouth)
    ea = math.radians(angle_deg + 360 - mouth)
    pts = [(cx, cy)]
    for i in range(37):
        a = sa + (ea - sa) * i / 36
        pts.append((cx + rad*math.cos(a), cy - rad*math.sin(a)))
    if len(pts) > 2:
        pygame.draw.polygon(surf, YELLOW, pts)
    ex = int(cx + rad*0.30*math.cos(math.radians(angle_deg+68)))
    ey = int(cy - rad*0.30*math.sin(math.radians(angle_deg+68)))
    pygame.draw.circle(surf, BLACK, (ex, ey), max(2, rad//5))

def draw_ghost(surf, cx, cy, sz, color, frame):
    r = sz // 2
    pygame.draw.circle(surf, color, (cx, cy - r//4), r)
    pygame.draw.rect(surf, color, (cx-r, cy-r//4, sz, r + r//3 + 1))
    seg = sz // 3
    for i in range(3):
        bx = cx - r + i*seg
        bot = cy + r + r//3
        pygame.draw.polygon(surf, BLACK, [(bx,bot),(bx+seg//2,bot-seg//2),(bx+seg,bot)])
    if color in (SCARED_C, SCARED2_C):
        pts2 = [(cx - r//2 + i*(r//3), cy - r//8 + (4 if i%2==0 else -4)) for i in range(6)]
        pygame.draw.lines(surf, WHITE, False, pts2, 2)
        for ox in (-r//3, r//3):
            pygame.draw.circle(surf, WHITE, (cx+ox, cy-r//2), r//5)
    else:
        for ox in (-r//3, r//3):
            pygame.draw.circle(surf, WHITE, (cx+ox, cy-r//2), r//4)
            pygame.draw.circle(surf, BLACK,  (cx+ox+1, cy-r//2+1), max(1, r//8))

# ── Mängija ──────────────────────────────────────────────────
class Player:
    def __init__(self, col, row):
        self.x = col * TILE + TILE // 2
        self.y = row * TILE + TILE // 2
        self.dx = 0; self.dy = 0
        self.want_dx = 0; self.want_dy = 0
        self.angle = 0
        self.mouth = 0.0; self.mdir = 1
        self.rad = TILE // 2 - 2

    def set_dir(self, dx, dy):
        self.want_dx = dx; self.want_dy = dy

    def _snap_center(self):
        """Snap pixel-koordinaadid tile-tsentrile."""
        self.x = (self.x // TILE) * TILE + TILE // 2
        self.y = (self.y // TILE) * TILE + TILE // 2

    def _centered(self):
        return (self.x % TILE == TILE // 2) and (self.y % TILE == TILE // 2)

    def _free(self, wall_set, dx, dy):
        nx = self.x + dx * SPEED
        ny = self.y + dy * SPEED
        r = self.rad - 3
        for px, py in [(nx-r,ny-r),(nx+r,ny-r),(nx-r,ny+r),(nx+r,ny+r)]:
            if is_wall(wall_set, int(px)//TILE, int(py)//TILE):
                return False
        return True

    def update(self, wall_set):
        if self._centered():
            if (self.want_dx or self.want_dy) and self._free(wall_set, self.want_dx, self.want_dy):
                self.dx = self.want_dx; self.dy = self.want_dy
        if self._free(wall_set, self.dx, self.dy):
            self.x += self.dx * SPEED
            self.y += self.dy * SPEED
        else:
            self._snap_center()
        self.x %= COLS * TILE; self.y %= ROWS * TILE
        if   self.dx ==  1: self.angle = 0
        elif self.dx == -1: self.angle = 180
        elif self.dy == -1: self.angle = 90
        elif self.dy ==  1: self.angle = 270
        if self.dx or self.dy:
            self.mouth += 0.08 * self.mdir
            if self.mouth >= 1: self.mouth=1; self.mdir=-1
            elif self.mouth <= 0: self.mouth=0; self.mdir=1

    def draw(self, surf):
        draw_pacman(surf, self.x, self.y, self.rad, self.angle, self.mouth)

    def tile_pos(self):
        return self.x // TILE, self.y // TILE

# ── Kummitus — tile-to-tile navigatsioon ─────────────────────
#
# Kummitus liigub alati ühest tile-tsentrist teiseni.
# Ristmikel valib suuna BFS/juhuslik (sõltub tüübist).
# Nii liiguvad nad kogu mapil ega jää kunagi kinni.

class Ghost:
    DIRS = [(1,0),(-1,0),(0,1),(0,-1)]

    def __init__(self, col, row, color, scatter_target, personality, speed, leave_delay):
        self.col = col; self.row = row
        self.home_col = col; self.home_row = row
        self.x = col * TILE + TILE // 2
        self.y = row * TILE + TILE // 2
        self.dx = 0; self.dy = -1
        self.color = color
        self.scatter_target = scatter_target
        self.personality = personality
        self.speed = speed
        self.leave_timer = leave_delay
        self.frightened = False
        self.fright_timer = 0
        self.leaving = True
        self.waiting = leave_delay > 0
        self.rad = TILE // 2 - 2
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False

    def scare(self):
        self.frightened = True
        self.fright_timer = POWER_TIME

    def get_color(self, frame):
        if not self.frightened: return self.color
        if self.fright_timer < SCARED_FLASH:
            return SCARED2_C if (frame//8)%2==0 else SCARED_C
        return SCARED_C

    def _choose_dir(self, wall_set, pac_col, pac_row):
        """Vali järgmine suund tile-ristmikel."""
        opp = (-self.dx, -self.dy)   # tagasipööramine keelatud (v.a. frightened)

        if self.frightened:
            # Hirmul: täiesti juhuslik, aga mitte seinasse
            options = []
            for d in self.DIRS:
                nc, nr = self.col + d[0], self.row + d[1]
                if not is_wall(wall_set, nc, nr):
                    options.append(d)
            return random.choice(options) if options else (self.dx, self.dy)

        # Valib suuna vastavalt isiksusele
        options = []
        for d in self.DIRS:
            if d == opp: continue   # ära tagasi mine
            nc, nr = self.col + d[0], self.row + d[1]
            if not is_wall(wall_set, nc, nr):
                options.append(d)
        if not options:
            return opp   # tupik — pöördu tagasi

        if self.personality == 'chase':
            # Blinky: mine otse Pac-Mani poole
            def dist(d):
                nc, nr = self.col+d[0], self.row+d[1]
                return (nc-pac_col)**2 + (nr-pac_row)**2
            return min(options, key=dist)

        elif self.personality == 'ambush':
            # Pinky: sihi 4 tile Pac-Mani ees
            tx = pac_col + 4   # lihtsustus
            ty = pac_row
            def dist(d):
                nc, nr = self.col+d[0], self.row+d[1]
                return (nc-tx)**2 + (nr-ty)**2
            return min(options, key=dist)

        elif self.personality == 'shy':
            # Clyde: chase kui kaugel, scatter kui lähedal
            dist_pac = (self.col-pac_col)**2 + (self.row-pac_row)**2
            if dist_pac > 64:
                def dist(d):
                    nc, nr = self.col+d[0], self.row+d[1]
                    return (nc-pac_col)**2 + (nr-pac_row)**2
                return min(options, key=dist)
            else:
                tx, ty = self.scatter_target
                def dist(d):
                    nc, nr = self.col+d[0], self.row+d[1]
                    return (nc-tx)**2 + (nr-ty)**2
                return min(options, key=dist)

        else:  # 'random' — Inky
            # 70% lähim Pac-Man, 30% juhuslik
            if random.random() < 0.7:
                def dist(d):
                    nc, nr = self.col+d[0], self.row+d[1]
                    return (nc-pac_col)**2 + (nr-pac_row)**2
                return min(options, key=dist)
            return random.choice(options)

    def update(self, wall_set, pac_col, pac_row):
        if self.frightened:
            self.fright_timer -= 1
            if self.fright_timer <= 0:
                self.frightened = False

        # Oota ghost house'is enne väljumist
        if self.waiting:
            self.leave_timer -= 1
            if self.leave_timer <= 0:
                self.waiting = False
            return

        # Ghost-house'ist välja liikumine — liigu tile-tsentri pealt üles
        if self.leaving:
            self.y -= self.speed
            exit_y = 8 * TILE + TILE // 2
            if self.y <= exit_y:
                self.y = exit_y
                # Iga kummitus väljub veidi erineva x-ga et kohe laiali minna
                self.x = self.home_col * TILE + TILE // 2
                self.col = self.home_col; self.row = 8
                self.leaving = False
                # Blinky(col<10) läheb vasakule, teised paremale
                self.dx = -1 if self.home_col <= 10 else 1
                self.dy = 0
                self.target_x = self.x
                self.target_y = self.y
                self.moving = False
            return

        spd = max(1, self.speed - (1 if self.frightened else 0))

        # Tile-to-tile: liigu target-tile tsentrisse
        if not self.moving:
            self.dx, self.dy = self._choose_dir(wall_set, pac_col, pac_row)
            nc = self.col + self.dx
            nr = self.row + self.dy
            if not is_wall(wall_set, nc, nr):
                self.col, self.row = nc, nr
                self.target_x = nc * TILE + TILE // 2
                self.target_y = nr * TILE + TILE // 2
                self.moving = True

        if self.moving:
            if abs(self.x - self.target_x) > spd:
                self.x += spd if self.target_x > self.x else -spd
            else:
                self.x = self.target_x
            if abs(self.y - self.target_y) > spd:
                self.y += spd if self.target_y > self.y else -spd
            else:
                self.y = self.target_y
            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False

    def draw(self, surf, frame):
        draw_ghost(surf, self.x, self.y, TILE-2, self.get_color(frame), frame)

    def tile_pos(self):
        return self.x // TILE, self.y // TILE

    def reset(self):
        self.col = self.home_col; self.row = self.home_row
        self.x = self.col * TILE + TILE // 2
        self.y = self.row * TILE + TILE // 2
        self.frightened = False; self.fright_timer = 0
        self.leaving = True; self.waiting = False
        self.leave_timer = 0
        self.moving = False
        self.dx = 0; self.dy = -1

# ── HUD ──────────────────────────────────────────────────────
def draw_hud(surf, font, score, total, lives):
    y0 = ROWS * TILE
    pygame.draw.rect(surf, (0, 0, 15), (0, y0, WIN_W, 56))
    pygame.draw.line(surf, WALL_COL, (0, y0), (WIN_W, y0), 2)
    surf.blit(font.render(f"SKOOR: {score}  /  MAX: {total}", True, WHITE), (8, y0+4))
    surf.blit(font.render("ELUD:", True, YELLOW), (8, y0+30))
    for i in range(lives):
        draw_pacman(surf, 82+i*28, y0+40, 10, 0, 0.35)

def show_overlay(surf, fb, fs, title, score):
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill((0,0,0,160))
    surf.blit(ov, (0,0))
    cx = WIN_W // 2
    for txt, y in [
        (fb.render(title, True, YELLOW),              WIN_H//2-90),
        (fs.render(f"Skoor: {score}", True, WHITE),   WIN_H//2-30),
        (fs.render("ENTER – mängi uuesti", True, NEON_BLUE), WIN_H//2+20),
        (fs.render("ESC   – välju",        True, NEON_BLUE), WIN_H//2+50),
    ]:
        surf.blit(txt, (cx - txt.get_width()//2, y))

# ── Peamäng ──────────────────────────────────────────────────
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Pacman – Kombineeritud Versioon")
    clock  = pygame.time.Clock()
    font_b = pygame.font.SysFont("consolas", 28, bold=True)
    font_s = pygame.font.SysFont("consolas", 16)

    while True:
        screen.fill(BLACK)
        for t, y in [
            (font_b.render("PAC-MAN", True, YELLOW), WIN_H//2-90),
            (font_s.render("Nooled – liigu    ENTER – alusta    ESC – välju", True, WHITE), WIN_H//2+10),
        ]:
            screen.blit(t, (WIN_W//2 - t.get_width()//2, y))
        pygame.display.flip()
        go = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                if ev.key == pygame.K_RETURN: go = True
        if go: break

    while True:
        wall_set, dot_list, power_list, ghost_starts = parse_map()
        wall_surf = build_wall_surface(wall_set)
        pygame.draw.rect(wall_surf, WHITE, (9*TILE, 9*TILE+TILE-3, 3*TILE, 3))

        power_set = set(map(tuple, power_list))
        dot_surfs = {}
        for (c, r) in dot_list:
            power = (c, r) in power_set
            sz = 10 if power else 5
            s = pygame.Surface((sz, sz), pygame.SRCALPHA)
            pygame.draw.ellipse(s, POWER_COL if power else DOT_COL, (0,0,sz,sz))
            dot_surfs[(c, r)] = (s, power)
        remaining_dots = set(dot_list)
        total_score = len(dot_list)*10 + len(power_list)*40

        pac = Player(PAC_COL, PAC_ROW)

        # 4 kummitust erinevate isiksustega ja nurga scatter-sihtidega
        ghost_defs = [
            (RED,    (COLS-1, 0),       'chase',   2, 0),    # Blinky — kohe välja
            (PINK,   (0, 0),            'ambush',  2, 180),  # Pinky — 3s viivitus
            (CYAN,   (COLS-1, ROWS-1),  'random',  2, 360),  # Inky  — 6s viivitus
            (ORANGE, (0, ROWS-1),       'shy',     2, 540),  # Clyde — 9s viivitus
        ]
        ghosts = []
        for i, (sc, sr) in enumerate(ghost_starts[:4]):
            color, scatter, pers, spd, delay = ghost_defs[i % 4]
            ghosts.append(Ghost(sc, sr, color, scatter, pers, spd, delay))

        score = 0; lives = 3; frame = 0; done = False; end_msg = ""; freeze = 0

        while not done:
            frame += 1
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    if ev.key == pygame.K_LEFT:  pac.set_dir(-1, 0)
                    if ev.key == pygame.K_RIGHT: pac.set_dir( 1, 0)
                    if ev.key == pygame.K_UP:    pac.set_dir( 0,-1)
                    if ev.key == pygame.K_DOWN:  pac.set_dir( 0, 1)

            if freeze > 0:
                freeze -= 1
            else:
                pac.update(wall_set)
                for g in ghosts:
                    g.update(wall_set, *pac.tile_pos())

                pt = pac.tile_pos()
                if pt in remaining_dots:
                    remaining_dots.discard(pt)
                    _, is_power = dot_surfs[pt]
                    if is_power:
                        score += 50
                        for g in ghosts: g.scare()
                    else:
                        score += 10

                if score >= 10000 and lives < 6:
                    lives = min(lives+1, 6)

                pac_t = pac.tile_pos()
                for g in ghosts:
                    if g.tile_pos() == pac_t:
                        if g.frightened:
                            score += 200; g.reset()
                        else:
                            lives -= 1
                            if lives <= 0:
                                end_msg = "MÄNG LÄBI!"; done = True
                            else:
                                pac.x = PAC_COL*TILE+TILE//2
                                pac.y = PAC_ROW*TILE+TILE//2
                                pac.dx = pac.dy = 0
                                freeze = FPS * 2
                        break

                if not remaining_dots:
                    end_msg = "SA VÕITSID!"; done = True

            screen.blit(wall_surf, (0,0))
            for (c,r) in remaining_dots:
                s, _ = dot_surfs[(c,r)]
                sz = s.get_width()
                screen.blit(s, (c*TILE+TILE//2-sz//2, r*TILE+TILE//2-sz//2))
            pac.draw(screen)
            for g in ghosts: g.draw(screen, frame)
            draw_hud(screen, font_s, score, total_score, lives)
            pygame.display.flip()
            clock.tick(FPS)

        pygame.time.wait(500)
        while True:
            screen.blit(wall_surf, (0,0))
            show_overlay(screen, font_b, font_s, end_msg, score)
            pygame.display.flip()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
                    if ev.key == pygame.K_RETURN: break
            else:
                continue
            break

if __name__ == "__main__":
    run_game()