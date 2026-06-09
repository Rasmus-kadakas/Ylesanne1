import pygame
import random
import sys
from collections import deque

WINDOW_TITLE = "ül7"
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
BG_COLOR = (168, 208, 240)

BASE_RADIUS = 10
RADIUS_STEP = 2
MAX_RINGS = 10

RING_COLORS = [
    (34, 68, 204),   # sinine
    (204, 34, 68),   # punane
    (34, 170, 68),   # roheline
    (204, 136, 0),   # oranž
    (136, 34, 204),  # lilla
    (0, 180, 180),   # tsüaan
    (220, 100, 0),   # tume oranž
    (0, 102, 136),   # teal
    (180, 0, 100),   # magenta
    (60, 140, 220),  # helesinine
    (100, 200, 60),  # heleroheline
    (200, 60, 140),  # roosa
]


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(icon, (34, 68, 204), (16, 16), 12, 3)
    pygame.display.set_icon(icon)

    clock = pygame.time.Clock()

    # (x, y, color, radius)
    rings = deque()
    ring_number = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                color = random.choice(RING_COLORS)

                radius = BASE_RADIUS + ring_number * RADIUS_STEP

                rings.append((x, y, color, radius))

                if len(rings) > MAX_RINGS:
                    rings.popleft()

                ring_number = (ring_number + 1) % MAX_RINGS

        screen.fill(BG_COLOR)

        for x, y, color, radius in rings:
            pygame.draw.circle(screen, color, (x, y), radius, 2)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
