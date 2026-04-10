import pygame
import sys
import math

# PyGame'i algseadistamine
pygame.init()

# Aken 640x480
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Ülesanne 2 - Täiendatud")

# --- PILTIDE LAADIMINE ---
# Veendu, et failinimed klapiksid sinu kaustas olevatega
bg = pygame.image.load("bgshop.jpg")
bg = pygame.transform.scale(bg, (640, 480))

seller = pygame.image.load("seller.png")
seller = pygame.transform.scale(seller, (225, 345))

chat = pygame.image.load("chat.png")
chat = pygame.transform.scale(chat, (235, 195))

# 1. VIKK Logo (vajab töötlemist/skaleerimist)
vikk_logo = pygame.image.load("VIKK logo.png")
vikk_logo = pygame.transform.scale(vikk_logo, (324, 43))  # Skaleerime väiksemaks

# 2. Tort (PNG - läbipaistev)
cake = pygame.image.load("tort.png")
cake = pygame.transform.scale(cake, (120, 100))

# 3. Mõõk
sword = pygame.image.load("Mõõk.png")
sword = pygame.transform.scale(sword, (180, 180))
sword = pygame.transform.rotate(sword, -45)  # Keerame seinale sobivaks

# --- KIRJASÕRMED JA TEKSTID ---
font_chat = pygame.font.SysFont("Arial", 20, bold=True)
text_chat = font_chat.render("Tere, Rasmus kadakas", True, (255, 255, 255))

# Kaarega teksti seadistus
font_arc = pygame.font.SysFont("Arial", 14, bold=True)
arc_text = "TULEVIK 2050"

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 1. Taust
    screen.blit(bg, (0, 0))

    # 2. Mõõk seinale (müüja selja taha paremale)
    screen.blit(sword, (420, 80))

    # 3. Müüja
    screen.blit(seller, (140, 163))

    # 4. Tort lauale (müüja ette paremale poole letti)
    screen.blit(cake, (380, 310))

    # 5. Jutumull ja tervitus
    chat_x, chat_y = 270, 60
    screen.blit(chat, (chat_x, chat_y))

    text_x = chat_x + (235 - text_chat.get_width()) // 2
    text_y = chat_y + (195 - text_chat.get_height()) // 2 - 15
    screen.blit(text_chat, (text_x, text_y))

    # 6. VIKK Logo vasakusse ülanurka
    logo_pos = (14, 15)
    screen.blit(vikk_logo, logo_pos)

    # 7. Kaarega tekst "TULEVIK 2050" ümber logo
    center_x, center_y = logo_pos[0] + 50, logo_pos[1] + 50
    radius = 65
    # Paigutame tähed kaares logo kohale
    for i, char in enumerate(arc_text):
        # Arvutame nurga iga tähe jaoks (kaar üleval pool)
        angle = math.radians(-160 + (i * 14))
        char_surf = font_arc.render(char, True, (0, 0, 0))

        # Tähe asukoht ringjoonel
        char_x = center_x + radius * math.cos(angle) - char_surf.get_width() // 2
        char_y = center_y + radius * math.sin(angle) - char_surf.get_height() // 2
        screen.blit(char_surf, (char_x, char_y))

    pygame.display.flip()
    clock.tick(60)