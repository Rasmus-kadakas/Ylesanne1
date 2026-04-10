import pygame
import sys

# 1. Käivitame PyGame mooduli
pygame.init()

# 2. Ekraani seaded (640x480 nagu palutud)
screen = pygame.display.set_mode([640, 480])
pygame.display.set_caption("Ülesanne 3 - Rasmus Kadakas")

# 3. Piltide laadimine
# Kasutame try-except plokki, et programm ei jookseks kokku, kui pilti pole
try:
    bg = pygame.image.load("bgshop.jpg")
    seller = pygame.image.load("seller.png")
    chat = pygame.image.load("chat.png")

    # Muudame pildid õigesse suurusesse
    bg = pygame.transform.scale(bg, [640, 480])
    seller = pygame.transform.scale(seller, [250, 305])
    chat = pygame.transform.scale(chat, [260, 200])
except:
    print("VIGA: Pilte ei leitud! Pane pildid koodiga samasse kausta.")
    pygame.quit()
    sys.exit()

# 4. Teksti seadistamine (Sinu nimi valgega)
font = pygame.font.SysFont("Verdana", 20, bold=True)
tekst = font.render("Tere, olen Rasmus Kadakas", True, [255, 255, 255])

# 5. Mängu põhitsükkel
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- JOONISTAMINE ---
    # Alati joonista kihid selles järjekorras:

    # 1. Taust (kogu ekraan)
    screen.blit(bg, [0, 0])

    # 2. Müüja (asukoht vasakul all)
    screen.blit(seller, [50, 175])

    # 3. Jutumull (müüja pea kohal)
    screen.blit(chat, [245, 50])

    # 4. Sinu nimi jutumulli peale
    screen.blit(tekst, [280, 110])

    # Uuenda ekraani
    pygame.display.flip()

# Suleb akna korrektselt
pygame.quit()