import pygame

# 1. Algatamine
pygame.init()

# 2. Ekraani seaded
laius, korgus = 800, 600
ekraan = pygame.display.set_mode((laius, korgus))
pygame.display.set_caption("Liikuv ruut")

# 3. Värvid ja muutujad
valge = (255, 255, 255)
sinine = (0, 100, 255)

ruudu_suurus = 50
x = laius // 2 - ruudu_suurus // 2
y = korgus // 2 - ruudu_suurus // 2
kiirus = 5

# KELL - see on kriitiline, et liikumine toimuks ühtlaselt!
kell = pygame.time.Clock()

# 4. Põhitsükkel
too_kaib = True
while too_kaib:
    # Kontrollime sündmusi (et aken ei läheks "Not Responding" olekusse)
    for sundmus in pygame.event.get():
        if sundmus.type == pygame.QUIT:
            too_kaib = False

    # KLAHVIDE LUGEMINE
    klahvid = pygame.key.get_pressed()

    if klahvid[pygame.K_LEFT]:
        x -= kiirus
    if klahvid[pygame.K_RIGHT]:
        x += kiirus
    if klahvid[pygame.K_UP]:
        y -= kiirus
    if klahvid[pygame.K_DOWN]:
        y += kiirus

    # 5. JOONISTAMINE
    ekraan.fill(valge)  # Puhastame ekraani vanast ruudust
    pygame.draw.rect(ekraan, sinine, (x, y, ruudu_suurus, ruudu_suurus))

    # Uuendame pilti
    pygame.display.flip()

    # PIIRAME KIIRUST (60 kaadrit sekundis)
    kell.tick(60)

pygame.quit()