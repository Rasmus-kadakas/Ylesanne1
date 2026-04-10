import pygame
import math  # Vajalik päikese kiirte arvutamiseks

# 1. Käivitame PyGame'i
pygame.init()

# 2. Seadistame akna suuruse ja nime
screen_width = 300
screen_height = 300
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Lumemees ja Valgusfoor – Sinu Nimi")

# 3. Värvide defineerimine (RGB)
VALGE = (255, 255, 255)
MUST = (0, 0, 0)
HELESININE = (135, 206, 235)  # Uus taustavärv
PUNANE = (220, 20, 60)
KOLLANE = (255, 215, 0)
ROHELINE = (34, 139, 34)
ORANZ = (255, 140, 0)
PRUUN = (139, 69, 19)
EESTI_SININE = (0, 114, 206)  # Täpne Eesti lipu sinine


# --- Funktsioon: Joonistame Lumememme ---
def joonista_lumemees(pind):
    # a. Keha pallid
    pygame.draw.circle(pind, VALGE, (100, 230), 45)  # Alumine
    pygame.draw.circle(pind, VALGE, (100, 160), 35)  # Keskmine
    pygame.draw.circle(pind, VALGE, (100, 105), 25)  # Pea

    # b. Nööbid (3tk) keskmisel pallil
    for i in range(3):
        pygame.draw.circle(pind, MUST, (100, 145 + i * 15), 3)

    # c. Silmad ja nina
    pygame.draw.circle(pind, MUST, (92, 100), 2)  # Vasak silm
    pygame.draw.circle(pind, MUST, (108, 100), 2)  # Parem silm
    pygame.draw.polygon(pind, ORANZ, [(100, 105), (100, 112), (115, 108)])  # Nina

    # d. Müts (pruun kaabu)
    # Alumine äär (ristkülik)
    pygame.draw.rect(pind, PRUUN, (75, 80, 50, 5))
    # Ülemine osa (ristkülik)
    pygame.draw.rect(pind, PRUUN, (85, 60, 30, 25))

    # e. Käed (pruunid jooned)
    pygame.draw.line(pind, PRUUN, (65, 160), (30, 140), 3)  # Vasak käsi
    pygame.draw.line(pind, PRUUN, (135, 160), (170, 140), 3)  # Parem käsi

    # f. Hari (põhi ja harjased) paremas käes
    # Varre ots
    pygame.draw.line(pind, PRUUN, (170, 140), (175, 130), 3)
    # Harjased (rida lühikesi jooni)
    harja_ots_x = 175
    harja_ots_y = 130
    for i in range(-5, 6):
        pygame.draw.line(pind, MUST, (harja_ots_x, harja_ots_y), (harja_ots_x + i * 2, harja_ots_y - 15), 1)


# --- Funktsioon: Joonistame Valgusfoori ---
def joonista_valgusfoor(pind):
    # g. Valgusfoori korpus (must ristkülik)
    pygame.draw.rect(pind, MUST, (220, 50, 40, 100))

    # h. Tuled (punane, kollane, roheline ringid)
    pygame.draw.circle(pind, PUNANE, (240, 70), 12)
    pygame.draw.circle(pind, KOLLANE, (240, 100), 12)
    pygame.draw.circle(pind, ROHELINE, (240, 130), 12)

    # i. Post (must kitsas ristkülik)
    pygame.draw.rect(pind, MUST, (235, 150, 10, 100))

    # j. Postialus (trapets /_\)
    # Defineerime trapetsi neli nurka
    alus_top_y = 250
    alus_bottom_y = 280
    alus_laius_top = 10
    alus_laius_bottom = 50
    post_kesk_x = 240

    trapetsi_punktid = [
        (post_kesk_x - alus_laius_top // 2, alus_top_y),  # Ülemine vasak
        (post_kesk_x + alus_laius_top // 2, alus_top_y),  # Ülemine parem
        (post_kesk_x + alus_laius_bottom // 2, alus_bottom_y),  # Alumine parem
        (post_kesk_x - alus_laius_bottom // 2, alus_bottom_y)  # Alumine vasak
    ]

    # Joonistame trapetsi *seest tühjana*, ainult piirjoone
    pygame.draw.polygon(pind, MUST, trapetsi_punktid, 2)

    # k. Täidame postialuse Eesti lipu värvidega (sini-must-valge)
    # Jagame trapetsi kõrguse kolmeks
    riba_korgus = (alus_bottom_y - alus_top_y) // 3
    # Joonistame kolm horisontaalset täidetud ristkülikut trapetsi *sees*
    # (Kuna trapetsi küljed on diagonaalsed, peame igat riba veidi laiemaks tegema)
    # See lahendus on lihtsuse mõttes ristkülikutega, mis on "lõigatud" trapetsi kuju sisse.
    # PyGame'is keerukamate kujundite täitmine mustriga on keeruline,
    # seega joonistame värvilised ribad esimesena ja trapetsi *peale*.
    # (Selleks tõstame trapetsi joonistamise *peale* värvimist)

    # Joonistame täidetud ribad (täiesti trapetsi *taha*)
    for i, värv in enumerate([EESTI_SININE, MUST, VALGE]):
        y_algus = alus_top_y + i * riba_korgus
        # Arvutame riba laiuse trapetsi valemi põhjal (lihtsustatud)
        # See on veidi keerulisem matemaatika, lihtsustame:
        laius = alus_laius_top + (i + 0.5) * (alus_laius_bottom - alus_laius_top) / 3

        # Joonistame täidetud ristküliku, mis on trapetsi sees
        pygame.draw.rect(pind, värv, (post_kesk_x - laius // 2, y_algus, laius, riba_korgus))

    # Joonistame trapetsi piirjoone *uuesti üle* värvide, et diagonaalid oleksid näha
    pygame.draw.polygon(pind, MUST, trapetsi_punktid, 3)  # Paksem piirjoon


# --- Funktsioon: Joonistame Tausta (Päike ja Pilved) ---
def joonista_taust(pind):
    # l. Päike (kollane ring ja kiired)
    paike_x, paike_y = 50, 50
    paike_raadius = 20
    pygame.draw.circle(pind, KOLLANE, (paike_x, paike_y), paike_raadius)

    # Päikese kiired (jooned ringist välja)
    kiirte_arv = 12
    kiire_pikkus = 35
    for i in range(kiirte_arv):
        nurk = i * (2 * math.pi / kiirte_arv)
        alg_x = paike_x + math.cos(nurk) * paike_raadius
        alg_y = paike_y + math.sin(nurk) * paike_raadius
        lopp_x = paike_x + math.cos(nurk) * kiire_pikkus
        lopp_y = paike_y + math.sin(nurk) * kiire_pikkus
        pygame.draw.line(pind, ORANZ, (alg_x, alg_y), (lopp_x, lopp_y), 2)

    # m. 3 pilve (valged ringid)
    def joonista_pilv(x, y):
        pygame.draw.circle(pind, VALGE, (x, y), 15)
        pygame.draw.circle(pind, VALGE, (x + 10, y - 5), 18)
        pygame.draw.circle(pind, VALGE, (x + 20, y), 15)

    joonista_pilv(150, 40)
    joonista_pilv(220, 60)
    joonista_pilv(100, 30)


# Programmi põhitsükkel
running = True
clock = pygame.time.Clock()  # Lisame kella, et piirata kaadrisagedust

while running:
    # Kontrollime sündmusi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 4. Joonistamine
    screen.fill(HELESININE)  # d. Taust helesiniseks

    joonista_taust(screen)
    joonista_lumemees(screen)
    joonista_valgusfoor(screen)

    # 5. Uuendame ekraani
    pygame.display.flip()

    # Piirame kaadrisagedust (FPS)
    clock.tick(60)

# Lõpetame töö
pygame.quit()
