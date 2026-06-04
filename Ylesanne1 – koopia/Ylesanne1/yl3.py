import pygame
import sys

# Akna suurus
LAIUS = 640
KORGUS = 480


def joonista_ruudud(ekraan, ruudu_suurus=20, joone_vari=(255, 0, 0), tausta_vari=(144, 238, 144)):
    """
    Joonistab ekraani täis ruudustiku.

    Parameetrid:
        ekraan       – pygame.Surface, millele joonistada
        ruudu_suurus – ühe ruudu küljesuurus pikslites
        joone_vari   – ruudustiku joonte RGB-värv
        tausta_vari  – tausta RGB-värv
    """
    ekraan.fill(tausta_vari)

    # Vertikaaljooned (veerud)
    veerud = LAIUS // ruudu_suurus + 1
    for veerg in range(veerud):
        x = veerg * ruudu_suurus
        pygame.draw.line(ekraan, joone_vari, (x, 0), (x, KORGUS))

    # Horisontaaljooned (read)
    read = KORGUS // ruudu_suurus + 1
    for rida in range(read):
        y = rida * ruudu_suurus
        pygame.draw.line(ekraan, joone_vari, (0, y), (LAIUS, y))


def main():
    pygame.init()
    ekraan = pygame.display.set_mode((LAIUS, KORGUS))
    pygame.display.set_caption("Harjutamine")

    # ── Muuda siia parameetreid vastavalt soovile ──────────────────────────
    joonista_ruudud(
        ekraan,
        ruudu_suurus=20,           # ruudu suurus pikslites
        joone_vari=(255, 0, 0),    # punased jooned
        tausta_vari=(144, 238, 144),  # roheline taust
    )
    # ──────────────────────────────────────────────────────────────────────

    pygame.display.flip()

    # Põhitsükkel – ristist sulgemine
    while True:
        for sundmus in pygame.event.get():
            if sundmus.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


if __name__ == "__main__":
    main()