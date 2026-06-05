import pygame
import sys

# --- Initsialiseerimine ---
pygame.init()
W, H = 640, 480
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("ul5")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 22, bold=True)

# --- Pildid (ball.png ja pad.png peavad olema samas kaustas!) ---
ball_img = pygame.transform.scale(pygame.image.load("ball.png"), (20, 20))
pad_img  = pygame.transform.scale(pygame.image.load("pad.png"),  (120, 20))

# --- Mängu olek ---
score = 0
BALL_SIZE = 20
ball_x, ball_y = float(W // 2), float(H // 4)
ball_sx, ball_sy = 3.5, 3.5

PAD_W, PAD_H = 120, 20
pad_x = float(W // 2 - PAD_W // 2)
pad_y = H / 1.5
PAD_SPEED = 6

# --- Põhisilmus ---
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

    # Aluse juhtimine
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  pad_x -= PAD_SPEED
    if keys[pygame.K_RIGHT]: pad_x += PAD_SPEED
    pad_x = max(0, min(pad_x, W - PAD_W))

    # Palli liikumine
    ball_x += ball_sx
    ball_y += ball_sy

    # Põrge seintelt
    if ball_x - BALL_SIZE/2 <= 0:
        ball_x = BALL_SIZE/2;  ball_sx = abs(ball_sx)
    if ball_x + BALL_SIZE/2 >= W:
        ball_x = W - BALL_SIZE/2; ball_sx = -abs(ball_sx)
    if ball_y - BALL_SIZE/2 <= 0:
        ball_y = BALL_SIZE/2;  ball_sy = abs(ball_sy)

    # Pall kukub alla → -1 punkt
    if ball_y + BALL_SIZE/2 >= H:
        score -= 1
        ball_x, ball_y = float(W // 2), float(H // 4)
        ball_sx = 3.5 if score % 2 == 0 else -3.5
        ball_sy = 3.5

    # Kokkupõrge alusega → +1 punkt
    if (ball_sy > 0 and
        ball_y + BALL_SIZE/2 >= pad_y and
        ball_y + BALL_SIZE/2 <= pad_y + PAD_H + 6 and
        ball_x + BALL_SIZE/2 >= pad_x and
        ball_x - BALL_SIZE/2 <= pad_x + PAD_W):
        ball_sy = -abs(ball_sy)
        hit = (ball_x - (pad_x + PAD_W / 2)) / (PAD_W / 2)
        ball_sx = hit * 5
        score += 1

    # --- Joonistamine ---
    screen.fill((168, 216, 234))

    txt = font.render(f"SKOOR: {score}", True, (26, 58, 92))
    screen.blit(txt, (12, 10))

    screen.blit(ball_img, (int(ball_x - BALL_SIZE/2), int(ball_y - BALL_SIZE/2)))
    screen.blit(pad_img,  (int(pad_x), int(pad_y)))

    pygame.display.flip()