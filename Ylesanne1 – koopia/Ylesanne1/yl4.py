
import pygame
import random
import sys

# --- Seadistused ---
LAIUS = 640
KORGUS = 480
FPS = 60

TEE_VASAK = 150
TEE_PAREM = 490
RAJAD = [195, 320, 445]

AUTO_LAIUS = 45
AUTO_KORGUS = 90
MIN_VAHE = AUTO_KORGUS + 30  # minimaalne vahemaa sama raja autode vahel

# --- Initsialiseerimine ---
pygame.init()
aken = pygame.display.set_mode((LAIUS, KORGUS))
pygame.display.set_caption("ul4")
kell = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 26, bold=True)

# --- Piltide laadimine ---
taust_pilt = pygame.image.load("bg_rally.jpg").convert()
taust_pilt = pygame.transform.scale(taust_pilt, (LAIUS, KORGUS))

punane_pilt = pygame.image.load("f1_red.png").convert_alpha()
punane_pilt = pygame.transform.scale(punane_pilt, (AUTO_LAIUS, AUTO_KORGUS))

sinine_pilt = pygame.image.load("f1_blue.png").convert_alpha()
sinine_pilt = pygame.transform.scale(sinine_pilt, (AUTO_LAIUS, AUTO_KORGUS))

# --- Mängija punane auto ---
mang_raja_nr = 1  # 0=vasak, 1=kesk, 2=parem
mang_x = float(RAJAD[mang_raja_nr] - AUTO_LAIUS // 2)
mang_siht_x = mang_x
mang_y = KORGUS - AUTO_KORGUS - 20
LIBISEMIS_KIIRUS = 8

# --- Sinised autod ---
class SinineAuto:
    def __init__(self, raja_nr, algus_y):
        self.raja_nr = raja_nr
        self.x = RAJAD[raja_nr] - AUTO_LAIUS // 2
        self.y = float(algus_y)
        self.kiirus = random.uniform(2.0, 4.0)

    def uuenda(self):
        self.y += self.kiirus

    def on_alla_joudnud(self):
        return self.y > KORGUS

    def reset(self, teised_autod):
        # Proovi kuni leiad turvalise koha
        for _ in range(50):
            raja = random.randint(0, 2)
            uus_y = float(random.randint(-400, -AUTO_KORGUS - 20))
            turvaline = True
            for teine in teised_autod:
                if teine is self:
                    continue
                if teine.raja_nr == raja:
                    if abs(teine.y - uus_y) < MIN_VAHE:
                        turvaline = False
                        break
            if turvaline:
                self.raja_nr = raja
                self.x = RAJAD[raja] - AUTO_LAIUS // 2
                self.y = uus_y
                self.kiirus = random.uniform(2.0, 4.0)
                return
        # Varuvariant: pane kaugele üles
        self.raja_nr = random.randint(0, 2)
        self.x = RAJAD[self.raja_nr] - AUTO_LAIUS // 2
        self.y = float(-600)
        self.kiirus = random.uniform(2.0, 4.0)

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), AUTO_LAIUS, AUTO_KORGUS)


def taga_vahemaad(autod):
    """Lükka sama raja autod lahku kui liiga lähedal."""
    for i in range(len(autod)):
        for j in range(len(autod)):
            if i == j:
                continue
            a = autod[i]
            b = autod[j]
            if a.raja_nr != b.raja_nr:
                continue
            if 0 < b.y - a.y < MIN_VAHE:
                a.y = b.y - MIN_VAHE


# Loo 4 sinist autot — igaüks erineval rajal ja kõrgusel
sinised_autod = []
for i in range(4):
    raja = i % 3
    algus_y = -AUTO_KORGUS - i * 160
    sinised_autod.append(SinineAuto(raja, algus_y))

# --- Skoor ---
skoor = 0

# --- Tausta kerimine ---
taust_nihe = 0

# --- Mäng töötab ---
mangib = True

# --- Peaahel ---
while True:
    kell.tick(FPS)

    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if sundmus.type == pygame.KEYDOWN and mangib:
            if sundmus.key == pygame.K_LEFT:
                if mang_raja_nr > 0:
                    mang_raja_nr -= 1
                    mang_siht_x = float(RAJAD[mang_raja_nr] - AUTO_LAIUS // 2)
            if sundmus.key == pygame.K_RIGHT:
                if mang_raja_nr < 2:
                    mang_raja_nr += 1
                    mang_siht_x = float(RAJAD[mang_raja_nr] - AUTO_LAIUS // 2)
        if sundmus.type == pygame.KEYDOWN and not mangib:
            if sundmus.key == pygame.K_r:
                skoor = 0
                mang_raja_nr = 1
                mang_x = float(RAJAD[mang_raja_nr] - AUTO_LAIUS // 2)
                mang_siht_x = mang_x
                for i, auto in enumerate(sinised_autod):
                    auto.raja_nr = i % 3
                    auto.x = RAJAD[auto.raja_nr] - AUTO_LAIUS // 2
                    auto.y = float(-AUTO_KORGUS - i * 160)
                    auto.kiirus = random.uniform(2.0, 4.0)
                taust_nihe = 0
                mangib = True

    if mangib:
        # Libista punane auto sihtkohta
        if mang_x < mang_siht_x:
            mang_x = min(mang_x + LIBISEMIS_KIIRUS, mang_siht_x)
        elif mang_x > mang_siht_x:
            mang_x = max(mang_x - LIBISEMIS_KIIRUS, mang_siht_x)

        taust_nihe = (taust_nihe + 4) % KORGUS

        mang_rect = pygame.Rect(int(mang_x), mang_y, AUTO_LAIUS, AUTO_KORGUS)

        for auto in sinised_autod:
            auto.uuenda()
            if auto.on_alla_joudnud():
                auto.reset(sinised_autod)
                skoor += 10
            if mang_rect.colliderect(auto.rect()):
                mangib = False

        # Taga et autod ei kattu üksteisega
        taga_vahemaad(sinised_autod)

    # --- Joonistamine ---
    aken.blit(taust_pilt, (0, taust_nihe - KORGUS))
    aken.blit(taust_pilt, (0, taust_nihe))

    for auto in sinised_autod:
        aken.blit(sinine_pilt, (int(auto.x), int(auto.y)))

    aken.blit(punane_pilt, (int(mang_x), mang_y))

    skoor_tekst = font.render("Skoor: " + str(skoor), True, (255, 255, 255))
    aken.blit(skoor_tekst, (10, 10))

    if not mangib:
        labi_pind = pygame.Surface((400, 160), pygame.SRCALPHA)
        labi_pind.fill((0, 0, 0, 180))
        aken.blit(labi_pind, (120, 150))
        labi_tekst = font.render("MÄNG LÄBI!", True, (255, 60, 60))
        skoor_l = font.render("Skoor: " + str(skoor), True, (255, 255, 255))
        restart_tekst = font.render("Vajuta R - uuesti", True, (200, 200, 200))
        aken.blit(labi_tekst,    (LAIUS//2 - labi_tekst.get_width()//2,    165))
        aken.blit(skoor_l,       (LAIUS//2 - skoor_l.get_width()//2,       205))
        aken.blit(restart_tekst, (LAIUS//2 - restart_tekst.get_width()//2, 245))

    pygame.display.flip()
