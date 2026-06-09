import pygame
import sys
import os

# --- Initsialiseerimine ---
pygame.init()
pygame.mixer.init()
W, H = 640, 480
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("ul6")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier New", 22, bold=True)
big_font = pygame.font.SysFont("Courier New", 48, bold=True)

# --- Pildid ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ball_img = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "ball.png")), (20, 20))
pad_img  = pygame.transform.scale(pygame.image.load(os.path.join(BASE_DIR, "pad.png")),  (120, 20))

# --- Taustamuusika ---
MUSIC_FILE = os.path.join(BASE_DIR, "sounds", "847179__fonoskop__puckpuckretro_arcade_funk_120bpm.wav")
if os.path.exists(MUSIC_FILE):
    pygame.mixer.music.load(MUSIC_FILE)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

# --- Heliefektid ---
BOUNCE_FILE = os.path.join(BASE_DIR, "sounds", "328011__astrand__retro-blaster-fire (1).wav")
bounce_sound = None
if os.path.exists(BOUNCE_FILE):
    bounce_sound = pygame.mixer.Sound(BOUNCE_FILE)
    bounce_sound.set_volume(0.4)

GAMEOVER_FILE = os.path.join(BASE_DIR, "sounds", "173859__jivatma07__j1game_over_mono.wav")
gameover_sound = None
if os.path.exists(GAMEOVER_FILE):
    gameover_sound = pygame.mixer.Sound(GAMEOVER_FILE)
    gameover_sound.set_volume(1.0)

# --- Taustavärv ---
BG_COLOR = (168, 216, 234)

# --- Mängu olek ---
def reset_game():
    return {
        "score": 0,
        "ball_x": float(W // 2),
        "ball_y": float(H // 4),
        "ball_sx": 3.5,
        "ball_sy": 3.5,
        "pad_x": float(W // 2 - 60),
        "game_over": False,
        "sound_played": False,
    }

BALL_SIZE = 20
PAD_W, PAD_H = 120, 20
pad_y = H / 1.5
PAD_SPEED = 6

state = reset_game()

# --- Põhisilmus ---
while True:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if state["game_over"] and event.key == pygame.K_r:
                state = reset_game()
                if os.path.exists(MUSIC_FILE):
                    pygame.mixer.music.play(-1)

    if not state["game_over"]:
        # Aluse juhtimine klaviatuuriga (x-suunas)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:  state["pad_x"] -= PAD_SPEED
        if keys[pygame.K_RIGHT]: state["pad_x"] += PAD_SPEED
        state["pad_x"] = max(0, min(state["pad_x"], W - PAD_W))

        # Palli liikumine
        state["ball_x"] += state["ball_sx"]
        state["ball_y"] += state["ball_sy"]

        # Põrge seintelt (vasak / parem / ülemine)
        if state["ball_x"] - BALL_SIZE / 2 <= 0:
            state["ball_x"] = BALL_SIZE / 2
            state["ball_sx"] = abs(state["ball_sx"])
            if bounce_sound: bounce_sound.play()
        if state["ball_x"] + BALL_SIZE / 2 >= W:
            state["ball_x"] = W - BALL_SIZE / 2
            state["ball_sx"] = -abs(state["ball_sx"])
            if bounce_sound: bounce_sound.play()
        if state["ball_y"] - BALL_SIZE / 2 <= 0:
            state["ball_y"] = BALL_SIZE / 2
            state["ball_sy"] = abs(state["ball_sy"])
            if bounce_sound: bounce_sound.play()

        # Pall puudutab alumist äärt → mäng lõpetatakse
        if state["ball_y"] + BALL_SIZE / 2 >= H:
            state["game_over"] = True

        # Kokkupõrge alusega → +1 punkt
        if (state["ball_sy"] > 0 and
                state["ball_y"] + BALL_SIZE / 2 >= pad_y and
                state["ball_y"] + BALL_SIZE / 2 <= pad_y + PAD_H + 6 and
                state["ball_x"] + BALL_SIZE / 2 >= state["pad_x"] and
                state["ball_x"] - BALL_SIZE / 2 <= state["pad_x"] + PAD_W):
            state["ball_sy"] = -abs(state["ball_sy"])
            hit = (state["ball_x"] - (state["pad_x"] + PAD_W / 2)) / (PAD_W / 2)
            state["ball_sx"] = hit * 5
            state["score"] += 1
            if bounce_sound: bounce_sound.play()

    else:
        # Game over heli — mängitakse ainult üks kord
        if not state["sound_played"]:
            pygame.mixer.music.stop()
            if gameover_sound: gameover_sound.play()
            state["sound_played"] = True

    # --- Joonistamine ---
    screen.fill(BG_COLOR)

    if state["game_over"]:
        over_txt    = big_font.render("MÄNG LÄBI!", True, (180, 30, 30))
        score_txt   = font.render(f"Sinu skoor: {state['score']}", True, (26, 58, 92))
        restart_txt = font.render("Vajuta R uuesti alustamiseks", True, (26, 58, 92))
        screen.blit(over_txt,    (W // 2 - over_txt.get_width() // 2,    H // 2 - 80))
        screen.blit(score_txt,   (W // 2 - score_txt.get_width() // 2,   H // 2))
        screen.blit(restart_txt, (W // 2 - restart_txt.get_width() // 2, H // 2 + 50))
    else:
        txt = font.render(f"SKOOR: {state['score']}", True, (26, 58, 92))
        screen.blit(txt, (12, 10))
        screen.blit(ball_img, (int(state["ball_x"] - BALL_SIZE / 2), int(state["ball_y"] - BALL_SIZE / 2)))
        screen.blit(pad_img,  (int(state["pad_x"]), int(pad_y)))

    pygame.display.flip()