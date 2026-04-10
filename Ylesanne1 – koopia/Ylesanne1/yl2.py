import pygame
import sys
import urllib.request
import os

# Piltide allalaadimine internetist
def download_image(url, filename):
    if not os.path.exists(filename):
        urllib.request.urlretrieve(url, filename)

download_image("https://www.metshein.com/wp-content/uploads/2019/03/bg_shop.jpg", "bgshop.jpg")
download_image("https://www.metshein.com/wp-content/uploads/2019/03/seller.png", "seller.png")
download_image("https://www.metshein.com/wp-content/uploads/2019/03/chat.png", "chat.png")

# PyGame'i algseadistamine
pygame.init()

# Aken 640x480, pealkiri – ülesande number
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Ülesanne 2")

# Piltide laadimine
bg = pygame.image.load("bgshop.jpg")
bg = pygame.transform.scale(bg, (640, 480))  # фон на весь экран

seller = pygame.image.load("seller.png")
seller = pygame.transform.scale(seller, (225, 305))  # продавец

chat = pygame.image.load("chat.png")
chat = pygame.transform.scale(chat, (235, 195))  # пузырь

# Kirjasort ja tekst nimega (valge värv)
font = pygame.font.SysFont("Arial", 20, bold=True)
text = font.render("Tere, Rasmus kadakas", True, (255, 255, 255))

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Joonistame tausta
    screen.blit(bg, (0, 0))

    # Joonistame müüja (vasakul all)
    screen.blit(seller, (140, 493 - 330))

    # Joonistame mullikese (müüja paremal pool, ülaosas)
    chat_x, chat_y = 270, 60
    screen.blit(chat, (chat_x, chat_y))

    # Tekst mullis keskel
    text_x = chat_x + (235 - text.get_width()) // 2
    text_y = chat_y + (195 - text.get_height()) // 2 - 15
    screen.blit(text, (text_x, text_y))

    pygame.display.flip()
    clock.tick(60)