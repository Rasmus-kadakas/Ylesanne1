
import pygame  # Mängu põhimoodul
import random  # Juhuslike arvude genereerimiseks
import sys  # Süsteemifunktsioonid
import json  # Rekordite salvestamiseks
import os  # Failisüsteemi operatsioonid

# ─── PYGAME INITSIALISEERIMINE ─────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()  # Helimootoril initsialiseerimine

# ─── AKNA SEADED ──────────────────────────────────────────────────────────────
AKNA_LAIUS = 800  # Mänguakna laius pikslites
AKNA_KORGUS = 650  # Mänguakna kõrgus pikslites
MÄNGUALA_ÜLEMINE = 60  # Infopaneeli kõrgus ülaosas

# ─── RUUDUSTIKU SEADED ────────────────────────────────────────────────────────
PLOKI_SUURUS = 20  # Ühe mänguruudu suurus pikslites
VEERUD = AKNA_LAIUS // PLOKI_SUURUS  # Ruudustiku veergude arv
READ = (AKNA_KORGUS - MÄNGUALA_ÜLEMINE) // PLOKI_SUURUS  # Ruudustiku ridade arv

# ─── VÄRVID (hele teema) ──────────────────────────────────────────────────────
HELE_TAUST = (240, 248, 240)  # Hele roheline taustavärv
HELE_RUUDUSTIK = (220, 235, 220)  # Ruudustiku joonte värv
HELE_PANEELI_TAUST = (50, 120, 50)  # Infopaneeli taustavärv
HELE_TEKST = (255, 255, 255)  # Paneeli teksti värv
HELE_SKOOR_TEKST = (30, 30, 30)  # Skoori teksti värv mänguväljal

# ─── VÄRVID (tume teema) ──────────────────────────────────────────────────────
TUME_TAUST = (15, 20, 15)  # Tume taustavärv
TUME_RUUDUSTIK = (25, 35, 25)  # Tume ruudustiku joonte värv
TUME_PANEELI_TAUST = (10, 40, 10)  # Tume infopaneeli värv
TUME_TEKST = (100, 255, 100)  # Neon-roheline tekst tumedas teemas
TUME_SKOOR_TEKST = (180, 255, 180)  # Hele skoori tekst tumedas teemas

# ─── USSI VÄRVID ──────────────────────────────────────────────────────────────
USSI_PEA_VÄRV = (34, 180, 34)  # Ussi pea värv (heleroheline)
USSI_KEHA_VÄRV = (50, 205, 50)  # Ussi keha värv
USSI_SILM_VÄRV = (255, 255, 255)  # Ussi silma valge osa
USSI_PUPILL_VÄRV = (0, 0, 0)  # Ussi pupilli värv

# ─── TOIDU VÄRVID ─────────────────────────────────────────────────────────────
PUNANE_ÕUN = (220, 50, 50)  # Tavaline punane õun (+1 punkt)
ROHELINE_ÕUN = (50, 220, 50)  # Kiiruse boonus õun (+2 punkti + kiirus)
KULDNE_ÕUN = (255, 215, 0)  # Kuldne õun (+5 punkti, haruldane)

# ─── TAKISTUSTE VÄRVID ────────────────────────────────────────────────────────
TAKISTUS_VÄRV = (100, 80, 60)  # Takistuse põhivärv (kivi/sein)
TAKISTUS_ÄÄRIS = (70, 55, 40)  # Takistuse äärise värv

# ─── MÄNGU KIIRUSED (kaadrit sekundis) ────────────────────────────────────────
ALGKIIRUS = 8  # Algne mängu kiirus
MAKSIMAALNE_KIIRUS = 20  # Maksimaalne kiirus tasemetel
BOONUS_KIIRUS = 15  # Kiiruse boonus aktiveeritud olekus
BOONUS_KESTUS = 150  # Kiiruse boonus kestus kaadrites (≈5 sek 30fps juures)

# ─── TASEMETE SEADED ──────────────────────────────────────────────────────────
PUNKTID_TASEME_KOHTA = 10  # Mitu punkti on vaja taseme tõstmiseks
TAKISTUSTE_ARV_TASEMEL = 3  # Mitu uut takistust lisandub iga tasemega

# ─── REKORDITE FAIL ───────────────────────────────────────────────────────────
REKORDITE_FAIL = "rekordid.json"  # Fail kus rekordid salvestatakse
MAX_REKORDEID = 5  # Mitu rekordit salvestatakse

# ─── FONT ─────────────────────────────────────────────────────────────────────
PEAFONT = pygame.font.SysFont("monospace", 22, bold=True)  # Põhifont
VÄIKEFONT = pygame.font.SysFont("monospace", 16)  # Väiksem font
SUUREFONT = pygame.font.SysFont("monospace", 40, bold=True)  # Suur pealkiri font
REKORDIFONT = pygame.font.SysFont("monospace", 18, bold=True)  # Rekordite font


def laadi_rekordid():
    """
    Laadib salvestatud rekordid JSON failist.
    Kui faili pole, tagastab tühja nimekirja.
    Tagastab: list rekordite sõnastikega {'nimi': str, 'skoor': int, 'tase': int}
    """
    if os.path.exists(REKORDITE_FAIL):
        try:
            with open(REKORDITE_FAIL, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Kui fail on rikutud, alusta tühjalt
            return []
    return []


def salvesta_rekord(nimi, skoor, tase):
    """
    Salvestab uue rekordi JSON faili.
    Hoiab ainult TOP-5 tulemust, sorteeritult skoori järgi.

    Parameetrid:
        nimi (str): Mängija nimi
        skoor (int): Lõplik punktisumma
        tase (int): Lõplik tase kus mäng lõppes
    """
    rekordid = laadi_rekordid()
    rekordid.append({"nimi": nimi, "skoor": skoor, "tase": tase})
    # Sorteeri kahanevas järjekorras skoori alusel
    rekordid.sort(key=lambda x: x["skoor"], reverse=True)
    # Hoia ainult MAX_REKORDEID parimat tulemust
    rekordid = rekordid[:MAX_REKORDEID]
    try:
        with open(REKORDITE_FAIL, "w", encoding="utf-8") as f:
            json.dump(rekordid, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Rekordite salvestamine ebaõnnestus: {e}")


def genereeri_takistused(tase, uss_positsioonid, toit_positsioon):
    """
    Genereerib juhuslikud takistuste positsioonid vastavalt tasemele.
    Takistused ei asetata ussi või toidu peale.

    Parameetrid:
        tase (int): Praegune mängutase
        uss_positsioonid (list): Ussi positsioonide nimekiri
        toit_positsioon (tuple): Toidu praegune positsioon

    Tagastab: set - takistuste positsioonide hulk
    """
    takistused = set()
    # Takistuste arv kasvab tasemega
    arv = tase * TAKISTUSTE_ARV_TASEMEL

    keelatud = set(uss_positsioonid)  # Ussi ruudud on keelatud
    keelatud.add(toit_positsioon)  # Toidu ruut on keelatud

    katseid = 0
    while len(takistused) < arv and katseid < 1000:
        katseid += 1
        # Genereeri juhusliku positsiooni
        x = random.randrange(0, VEERUD) * PLOKI_SUURUS
        y = random.randrange(0, READ) * PLOKI_SUURUS + MÄNGUALA_ÜLEMINE
        pos = (x, y)

        if pos not in keelatud and pos not in takistused:
            takistused.add(pos)

    return takistused


def juhuslik_toit_positsioon(uss, takistused):
    """
    Leiab juhusliku vaba positsiooni toidu paigutamiseks.
    Tagab et toit ei ilmu ussi ega takistuste peale.

    Parameetrid:
        uss (list): Ussi praegused ruudud
        takistused (set): Takistuste positsioonide hulk

    Tagastab: tuple (x, y) - toidu uus positsioon
    """
    keelatud = set(tuple(s) for s in uss) | takistused

    katseid = 0
    while katseid < 10000:
        katseid += 1
        x = random.randrange(0, VEERUD) * PLOKI_SUURUS
        y = random.randrange(0, READ) * PLOKI_SUURUS + MÄNGUALA_ÜLEMINE
        pos = (x, y)
        if pos not in keelatud:
            return pos

    # Äärmuslik juhtum: kõik ruudud täis (mäng peaks juba lõppenud olema)
    return (PLOKI_SUURUS, MÄNGUALA_ÜLEMINE + PLOKI_SUURUS)


def joonista_uss(ekraan, uss):
    """
    Joonistab ussi ekraanile koos peaga (silmadega) ja kehaga.
    Pea on eraldi värviga ja sellel on silmad.

    Parameetrid:
        ekraan: pygame.Surface - mänguaken
        uss (list): Ussi segmentide positsioonide nimekiri [[x,y], ...]
    """
    for i, segment in enumerate(uss):
        ruut = pygame.Rect(segment[0], segment[1], PLOKI_SUURUS, PLOKI_SUURUS)

        if i == 0:
            # ── Joonista pea ──
            pygame.draw.rect(ekraan, USSI_PEA_VÄRV, ruut, border_radius=5)
            pygame.draw.rect(ekraan, (20, 140, 20), ruut, 2, border_radius=5)

            # Joonista silmad (positsioon sõltub liikumissuunast)
            silm_r = 3  # Silma raadius
            # Vasak silm
            pygame.draw.circle(ekraan, USSI_SILM_VÄRV,
                               (segment[0] + 5, segment[1] + 6), silm_r)
            pygame.draw.circle(ekraan, USSI_PUPILL_VÄRV,
                               (segment[0] + 5, segment[1] + 6), 1)
            # Parem silm
            pygame.draw.circle(ekraan, USSI_SILM_VÄRV,
                               (segment[0] + 15, segment[1] + 6), silm_r)
            pygame.draw.circle(ekraan, USSI_PUPILL_VÄRV,
                               (segment[0] + 15, segment[1] + 6), 1)
        else:
            # ── Joonista kehasegment ──
            # Keha muutub järjest tumedamaks saba poole liikudes
            heledus = max(80, 205 - i * 3)
            keha_värv = (30, heledus, 30)
            pygame.draw.rect(ekraan, keha_värv, ruut, border_radius=4)
            pygame.draw.rect(ekraan, (20, heledus - 30, 20), ruut, 1, border_radius=4)


def joonista_toit(ekraan, toit_pos, toit_liik, animatsiooni_loendur):
    """
    Joonistab toidu animeeritud kujul.
    Tavaline õun on punane, boonus roheline, kuldne kollane.
    Toit "põrkab" kerge animatsiooniga.

    Parameetrid:
        ekraan: mänguaken
        toit_pos (tuple): Toidu (x, y) positsioon
        toit_liik (str): "tavaline", "boonus" või "kuldne"
        animatsiooni_loendur (int): Animatsiooni kaadri loendur
    """
    # Vali värv tüübi järgi
    if toit_liik == "boonus":
        värv = ROHELINE_ÕUN
        ääris_värv = (20, 180, 20)
    elif toit_liik == "kuldne":
        värv = KULDNE_ÕUN
        ääris_värv = (200, 160, 0)
    else:
        värv = PUNANE_ÕUN
        ääris_värv = (160, 30, 30)

    # Kerge üles-alla põrkamise animatsioon
    nihe = int(2 * abs(pygame.math.Vector2(1, 0).rotate(animatsiooni_loendur * 4).y))

    ruut = pygame.Rect(toit_pos[0] + 2, toit_pos[1] + 2 - nihe,
                       PLOKI_SUURUS - 4, PLOKI_SUURUS - 4)
    pygame.draw.ellipse(ekraan, värv, ruut)
    pygame.draw.ellipse(ekraan, ääris_värv, ruut, 2)

    # Väike "läige" efekt õuna peal
    pygame.draw.circle(ekraan, (255, 255, 200),
                       (toit_pos[0] + 6, toit_pos[1] + 5 - nihe), 2)


def joonista_takistused(ekraan, takistused):
    """
    Joonistab kõik takistused kivide kujul.
    Iga takistus saab kerge 3D-efekti ääristega.

    Parameetrid:
        ekraan: mänguaken
        takistused (set): Takistuste positsioonide hulk
    """
    for pos in takistused:
        ruut = pygame.Rect(pos[0], pos[1], PLOKI_SUURUS, PLOKI_SUURUS)
        pygame.draw.rect(ekraan, TAKISTUS_VÄRV, ruut, border_radius=3)
        # Hele ülaserv (3D efekt)
        pygame.draw.line(ekraan, (140, 120, 100),
                         (pos[0], pos[1]), (pos[0] + PLOKI_SUURUS - 1, pos[1]), 2)
        pygame.draw.line(ekraan, (140, 120, 100),
                         (pos[0], pos[1]), (pos[0], pos[1] + PLOKI_SUURUS - 1), 2)
        # Tume alakülg (3D efekt)
        pygame.draw.line(ekraan, TAKISTUS_ÄÄRIS,
                         (pos[0], pos[1] + PLOKI_SUURUS - 1),
                         (pos[0] + PLOKI_SUURUS - 1, pos[1] + PLOKI_SUURUS - 1), 2)
        pygame.draw.rect(ekraan, TAKISTUS_ÄÄRIS, ruut, 1, border_radius=3)


def joonista_infopaneel(ekraan, skoor, tase, uss_pikkus, boonus_loendur, tume_teema):
    """
    Joonistab ülaosa infopaneeli skoori, taseme ja muude andmetega.
    Kui kiiruse boonus on aktiivne, kuvatakse selle aeg.

    Parameetrid:
        ekraan: mänguaken
        skoor (int): Praegune punktisumma
        tase (int): Praegune tase
        uss_pikkus (int): Ussi praegune pikkus
        boonus_loendur (int): Mitu kaadrit on kiiruse boonus veel aktiivne
        tume_teema (bool): Kas tume teema on sisse lülitatud
    """
    # Paneeli taustavärv sõltub teemast
    paneeli_värv = TUME_PANEELI_TAUST if tume_teema else HELE_PANEELI_TAUST
    teksti_värv = TUME_TEKST if tume_teema else HELE_TEKST

    pygame.draw.rect(ekraan, paneeli_värv,
                     (0, 0, AKNA_LAIUS, MÄNGUALA_ÜLEMINE))

    # Skoor, tase, pikkus
    skoor_tekst = PEAFONT.render(f"SKOOR: {skoor}", True, teksti_värv)
    tase_tekst = PEAFONT.render(f"TASE: {tase}", True, teksti_värv)
    pikkus_tekst = VÄIKEFONT.render(f"Pikkus: {uss_pikkus}", True, teksti_värv)

    ekraan.blit(skoor_tekst, (10, 18))
    ekraan.blit(tase_tekst, (AKNA_LAIUS // 2 - 50, 18))
    ekraan.blit(pikkus_tekst, (AKNA_LAIUS - 130, 20))

    # Kiiruse boonus indikaator
    if boonus_loendur > 0:
        boonus_tekst = VÄIKEFONT.render(
            f"⚡ KIIRUS: {boonus_loendur // 30 + 1}s", True, KULDNE_ÕUN
        )
        ekraan.blit(boonus_tekst, (AKNA_LAIUS - 160, 38))

    # Eraldajoon paneeli ja mänguvälja vahel
    pygame.draw.line(ekraan, teksti_värv,
                     (0, MÄNGUALA_ÜLEMINE - 1), (AKNA_LAIUS, MÄNGUALA_ÜLEMINE - 1), 2)


def joonista_ruudustik(ekraan, tume_teema):
    """
    Joonistab mänguvälja tausta ruudustikuga.

    Parameetrid:
        ekraan: mänguaken
        tume_teema (bool): Kas tume teema on aktiivne
    """
    taust_värv = TUME_TAUST if tume_teema else HELE_TAUST
    ruudustiku_värv = TUME_RUUDUSTIK if tume_teema else HELE_RUUDUSTIK

    # Täida mänguväli taustavärviga
    ekraan.fill(taust_värv, (0, MÄNGUALA_ÜLEMINE, AKNA_LAIUS,
                             AKNA_KORGUS - MÄNGUALA_ÜLEMINE))

    # Joonista vertikaalsed jooned
    for x in range(0, AKNA_LAIUS, PLOKI_SUURUS):
        pygame.draw.line(ekraan, ruudustiku_värv,
                         (x, MÄNGUALA_ÜLEMINE), (x, AKNA_KORGUS))

    # Joonista horisontaalsed jooned
    for y in range(MÄNGUALA_ÜLEMINE, AKNA_KORGUS, PLOKI_SUURUS):
        pygame.draw.line(ekraan, ruudustiku_värv, (0, y), (AKNA_LAIUS, y))


def kuva_mang_labi_ekraan(ekraan, skoor, tase, tume_teema):
    """
    Kuvab mäng läbi ekraani koos punktisumma ja tasemega.
    Küsib mängijalt nime rekordite jaoks.
    Ootab klahvivajutust uuesti mängimiseks või väljumiseks.

    Parameetrid:
        ekraan: mänguaken
        skoor (int): Lõplik punktisumma
        tase (int): Tase kus mäng lõppes
        tume_teema (bool): Praegune teema

    Tagastab:
        str: "uuesti" kui mängitakse uuesti, "välja" kui väljutakse
    """
    taust_värv = TUME_TAUST if tume_teema else HELE_TAUST
    teksti_värv = TUME_TEKST if tume_teema else (50, 50, 50)

    ekraan.fill(taust_värv)

    # ── Pealkiri ──
    pealkiri = SUUREFONT.render("MÄNG LÄBI!", True, (220, 50, 50))
    ekraan.blit(pealkiri, (AKNA_LAIUS // 2 - pealkiri.get_width() // 2, 80))

    # ── Tulemus ──
    skoor_tekst = PEAFONT.render(f"Sinu skoor: {skoor}", True, teksti_värv)
    tase_tekst = PEAFONT.render(f"Saavutatud tase: {tase}", True, teksti_värv)
    ekraan.blit(skoor_tekst, (AKNA_LAIUS // 2 - skoor_tekst.get_width() // 2, 170))
    ekraan.blit(tase_tekst, (AKNA_LAIUS // 2 - tase_tekst.get_width() // 2, 205))

    # ── Rekordite tabel ──
    rekordid = laadi_rekordid()
    rekord_pealkiri = PEAFONT.render("🏆 REKORDITE TABEL:", True, KULDNE_ÕUN)
    ekraan.blit(rekord_pealkiri,
                (AKNA_LAIUS // 2 - rekord_pealkiri.get_width() // 2, 260))

    for i, r in enumerate(rekordid):
        medal = ["🥇", "🥈", "🥉", "4.", "5."][i] if i < 5 else f"{i + 1}."
        rida = REKORDIFONT.render(
            f"{medal} {r['nimi'][:12]:<12} {r['skoor']:>5} pts  (Tase {r['tase']})",
            True, teksti_värv
        )
        ekraan.blit(rida, (AKNA_LAIUS // 2 - rida.get_width() // 2, 295 + i * 28))

    # ── Juhised ──
    juhis1 = VÄIKEFONT.render("Vajuta ENTER - mängi uuesti", True, teksti_värv)
    juhis2 = VÄIKEFONT.render("Vajuta ESC - välju", True, teksti_värv)
    ekraan.blit(juhis1, (AKNA_LAIUS // 2 - juhis1.get_width() // 2, 510))
    ekraan.blit(juhis2, (AKNA_LAIUS // 2 - juhis2.get_width() // 2, 538))

    pygame.display.flip()

    # Oota klahvivajutust
    while True:
        for sündmus in pygame.event.get():
            if sündmus.type == pygame.QUIT:
                return "välja"
            if sündmus.type == pygame.KEYDOWN:
                if sündmus.key == pygame.K_RETURN:
                    return "uuesti"
                if sündmus.key == pygame.K_ESCAPE:
                    return "välja"


def kuva_aloekraan(ekraan, tume_teema):
    """
    Kuvab mängu algusekraani koos juhistega.

    Parameetrid:
        ekraan: mänguaken
        tume_teema (bool): Praegune teema

    Tagastab:
        bool: True kui mäng alustatakse, False kui väljutakse
    """
    taust_värv = TUME_TAUST if tume_teema else HELE_TAUST
    teksti_värv = TUME_TEKST if tume_teema else (30, 80, 30)

    ekraan.fill(taust_värv)

    # ── Pealkiri ──
    tiitel = SUUREFONT.render("🐍 SINU-MOOD USSIMÄNG", True, (34, 180, 34))
    ekraan.blit(tiitel, (AKNA_LAIUS // 2 - tiitel.get_width() // 2, 60))

    alatiitel = PEAFONT.render("PyGame Snake - Täiustatud versioon", True, teksti_värv)
    ekraan.blit(alatiitel, (AKNA_LAIUS // 2 - alatiitel.get_width() // 2, 115))

    # ── Juhised ──
    juhised = [
        ("JUHISED:", KULDNE_ÕUN),
        ("  Nooleklahvid / WASD - liikumine", teksti_värv),
        ("  P - paus / jätka", teksti_värv),
        ("  T - vaheta teema (hele/tume)", teksti_värv),
        ("  ESC - välju mängust", teksti_värv),
        ("", teksti_värv),
        ("TOIT:", KULDNE_ÕUN),
        ("  🔴 Punane õun = +1 punkt", (220, 80, 80)),
        ("  🟢 Roheline õun = +2 punkti + kiirusboonus", (80, 200, 80)),
        ("  🟡 Kuldne õun = +5 punkti (haruldane!)", KULDNE_ÕUN),
        ("", teksti_värv),
        ("  Koguda punkte → tase tõuseb → kiirem + rohkem takistusi!", teksti_värv),
    ]

    y_pos = 175
    for tekst, värv in juhised:
        if tekst:
            rida = VÄIKEFONT.render(tekst, True, värv)
            ekraan.blit(rida, (AKNA_LAIUS // 2 - 200, y_pos))
        y_pos += 26

    # ── Alusta nupp ──
    alusta = PEAFONT.render("Vajuta ENTER - alusta mängu", True, (34, 180, 34))
    ekraan.blit(alusta, (AKNA_LAIUS // 2 - alusta.get_width() // 2, 530))

    pygame.display.flip()

    while True:
        for sündmus in pygame.event.get():
            if sündmus.type == pygame.QUIT:
                return False
            if sündmus.type == pygame.KEYDOWN:
                if sündmus.key == pygame.K_RETURN:
                    return True
                if sündmus.key == pygame.K_ESCAPE:
                    return False


def küsi_mängija_nimi(ekraan, tume_teema):
    """
    Kuvab sisestusvälja mängija nime küsimiseks enne rekordite salvestamist.

    Parameetrid:
        ekraan: mänguaken
        tume_teema (bool): Praegune teema

    Tagastab:
        str: Mängija sisestatud nimi (maksimaalselt 12 tähemärki)
    """
    taust_värv = TUME_TAUST if tume_teema else HELE_TAUST
    teksti_värv = TUME_TEKST if tume_teema else (30, 80, 30)

    nimi = ""

    while True:
        ekraan.fill(taust_värv)

        küsimus = PEAFONT.render("Sisesta oma nimi rekordite jaoks:", True, teksti_värv)
        ekraan.blit(küsimus, (AKNA_LAIUS // 2 - küsimus.get_width() // 2, 260))

        # Sisestusväli
        väli_ruut = pygame.Rect(AKNA_LAIUS // 2 - 150, 310, 300, 45)
        pygame.draw.rect(ekraan, (200, 230, 200) if not tume_teema else (30, 60, 30),
                         väli_ruut, border_radius=5)
        pygame.draw.rect(ekraan, (34, 180, 34), väli_ruut, 2, border_radius=5)

        nimi_tekst = PEAFONT.render(nimi + "|", True, (30, 30, 30) if not tume_teema else (200, 255, 200))
        ekraan.blit(nimi_tekst, (väli_ruut.x + 10, väli_ruut.y + 10))

        juhis = VÄIKEFONT.render("ENTER - kinnita  |  ESC - jäta vahele", True, teksti_värv)
        ekraan.blit(juhis, (AKNA_LAIUS // 2 - juhis.get_width() // 2, 370))

        pygame.display.flip()

        for sündmus in pygame.event.get():
            if sündmus.type == pygame.QUIT:
                return "Anonüümne"
            if sündmus.type == pygame.KEYDOWN:
                if sündmus.key == pygame.K_RETURN:
                    return nimi if nimi.strip() else "Anonüümne"
                elif sündmus.key == pygame.K_ESCAPE:
                    return "Anonüümne"
                elif sündmus.key == pygame.K_BACKSPACE:
                    nimi = nimi[:-1]  # Kustuta viimane täht
                elif len(nimi) < 12:  # Maksimaalselt 12 tähemärki
                    nimi += sündmus.unicode


def põhimäng():
    """
    Põhimängu tsükkel.
    Käivitab mängu, haldab kõiki mänguelemente:
    - Ussi liikumine ja kasvamine
    - Toidu söömine
    - Tasemete tõstmine
    - Takistuste lisamine
    - Kiiruse boonus
    - Teema vahetus
    - Kokkupõrke tuvastamine

    Tagastab: None
    """
    # ── Ekraani initsialiseerimine ──
    ekraan = pygame.display.set_mode((AKNA_LAIUS, AKNA_KORGUS))
    pygame.display.set_caption("🐍 Sinu-Mood Ussimäng - PyGame")
    kell = pygame.time.Clock()

    # ── Teema olek ──
    tume_teema = False  # Alustame hele teemaga

    # ── Aloekraani kuvamine ──
    if not kuva_aloekraan(ekraan, tume_teema):
        pygame.quit()
        sys.exit()

    # ── Peamine mängu tsükkel (uuesti mängimine) ──
    while True:
        # ─── MÄNGU SEISUNDI LÄHTESTAMINE ───────────────────────────────────────

        # Uss algab ekraani keskel, 3 segmendiga
        algx = (VEERUD // 2) * PLOKI_SUURUS
        algy = (READ // 2) * PLOKI_SUURUS + MÄNGUALA_ÜLEMINE
        uss = [
            [algx, algy],
            [algx - PLOKI_SUURUS, algy],
            [algx - PLOKI_SUURUS * 2, algy]
        ]

        suund = [PLOKI_SUURUS, 0]  # Algsuund: paremale

        skoor = 0  # Algne punktisumma
        tase = 1  # Algne tase
        mäng_käib = True  # Mängu olek
        paus = False  # Pausirežiim
        animatsiooni_loendur = 0  # Animatsiooni kaader

        # Kiiruse boonus seaded
        boonus_aktiivne = False  # Kas boonus on praegu aktiivne
        boonus_loendur = 0  # Mitu kaadrit boonus kestab

        # Takistused (1. tasemel pole takistusi)
        takistused = set()

        # Genereeri esimene toit
        toit_pos = juhuslik_toit_positsioon(uss, takistused)
        toit_liik = "tavaline"  # Esimene toit on alati tavaline

        # Kiiruse boonus toidu positsioon (ilmub vahepeal)
        boonus_toit_pos = None  # None = pole ekraanil
        boonus_toit_loendur = 0  # Mitu kaadrit on boonus toit olnud ekraanil
        BOONUS_TOIDU_KESTUS = 200  # Mitu kaadrit boonus toit ekraanil on
        BOONUS_TOIDU_ILMUMINE = 150  # Iga mitu kaadrit võib ilmuda

        praegune_kiirus = ALGKIIRUS  # Praegune mängu kiirus

        # ─── MÄNGU PÕHITSÜKKEL ─────────────────────────────────────────────────
        while mäng_käib:

            # ── Sündmuste töötlemine ──
            for sündmus in pygame.event.get():
                if sündmus.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if sündmus.type == pygame.KEYDOWN:
                    # Liikumisklahvid (nooleklahvid ja WASD)
                    if sündmus.key in (pygame.K_UP, pygame.K_w):
                        if suund[1] != PLOKI_SUURUS:  # Ei saa tagurpidi minna
                            suund = [0, -PLOKI_SUURUS]
                    elif sündmus.key in (pygame.K_DOWN, pygame.K_s):
                        if suund[1] != -PLOKI_SUURUS:
                            suund = [0, PLOKI_SUURUS]
                    elif sündmus.key in (pygame.K_LEFT, pygame.K_a):
                        if suund[0] != PLOKI_SUURUS:
                            suund = [-PLOKI_SUURUS, 0]
                    elif sündmus.key in (pygame.K_RIGHT, pygame.K_d):
                        if suund[0] != -PLOKI_SUURUS:
                            suund = [PLOKI_SUURUS, 0]

                    # Paus (P-klahv)
                    elif sündmus.key == pygame.K_p:
                        paus = not paus

                    # ── TÄIUSTUS 5: Teema vahetus (T-klahv) ──
                    elif sündmus.key == pygame.K_t:
                        tume_teema = not tume_teema

                    # Välju mängust
                    elif sündmus.key == pygame.K_ESCAPE:
                        mäng_käib = False

            # Kui paus on sisse lülitatud, ära uuenda mängu
            if paus:
                paus_tekst = SUUREFONT.render("⏸ PAUS", True, KULDNE_ÕUN)
                juhis_tekst = VÄIKEFONT.render("Vajuta P - jätka", True, KULDNE_ÕUN)
                ekraan.blit(paus_tekst,
                            (AKNA_LAIUS // 2 - paus_tekst.get_width() // 2,
                             AKNA_KORGUS // 2 - 30))
                ekraan.blit(juhis_tekst,
                            (AKNA_LAIUS // 2 - juhis_tekst.get_width() // 2,
                             AKNA_KORGUS // 2 + 30))
                pygame.display.flip()
                kell.tick(10)
                continue

            # ── Ussi liikumine ──
            uus_pea = [uss[0][0] + suund[0], uss[0][1] + suund[1]]

            # ── Seina läbimine (uss ilmub teisest servast) ──
            if uus_pea[0] < 0:
                uus_pea[0] = (VEERUD - 1) * PLOKI_SUURUS
            elif uus_pea[0] >= AKNA_LAIUS:
                uus_pea[0] = 0
            if uus_pea[1] < MÄNGUALA_ÜLEMINE:
                uus_pea[1] = (READ - 1) * PLOKI_SUURUS + MÄNGUALA_ÜLEMINE
            elif uus_pea[1] >= AKNA_KORGUS:
                uus_pea[1] = MÄNGUALA_ÜLEMINE

            uss.insert(0, uus_pea)  # Lisa uus pea ussi algusse

            # ── Kokkupõrke tuvastamine ──

            # Kas uss põrkas iseendasse?
            if uus_pea in uss[1:]:
                mäng_käib = False
                break

            # Kas uss põrkas takistusesse?
            if tuple(uus_pea) in takistused:
                mäng_käib = False
                break

            # ── TÄIUSTUS 1: Tasemesüsteem ──
            # Kontrolli kas tase tõuseb
            uus_tase = (skoor // PUNKTID_TASEME_KOHTA) + 1
            if uus_tase > tase:
                tase = uus_tase
                # Suurenda kiirust tasemega (kuid mitte üle maksimumi)
                praegune_kiirus = min(ALGKIIRUS + tase * 2, MAKSIMAALNE_KIIRUS)
                # ── TÄIUSTUS 2: Lisa uued takistused uue tasemega ──
                takistused = genereeri_takistused(
                    tase - 1, [tuple(s) for s in uss], tuple(toit_pos)
                )

            # ── Toidu söömine ──
            sõi = False

            # Kontrolli kas uss sõi tavalise toidu
            if uus_pea == list(toit_pos):
                sõi = True
                if toit_liik == "tavaline":
                    skoor += 1  # +1 punkt tavaline
                elif toit_liik == "kuldne":
                    skoor += 5  # +5 punkti kuldne
                elif toit_liik == "boonus":
                    skoor += 2  # +2 punkti boonus
                    # ── TÄIUSTUS 3: Kiiruse boonus aktiveerimine ──
                    boonus_aktiivne = True
                    boonus_loendur = BOONUS_KESTUS

                # Genereeri uus toit
                # 10% võimalus kuldse õuna saamiseks
                juhuslik = random.random()
                if juhuslik < 0.10:
                    toit_liik = "kuldne"
                else:
                    toit_liik = "tavaline"
                toit_pos = juhuslik_toit_positsioon(uss, takistused)
                boonus_toit_pos = None  # Peitke boonus toit pärast söömist
                boonus_toit_loendur = 0

            # Kontrolli kas uss sõi boonus toidu
            if boonus_toit_pos and uus_pea == list(boonus_toit_pos):
                sõi = True
                skoor += 2
                boonus_aktiivne = True
                boonus_loendur = BOONUS_KESTUS
                boonus_toit_pos = None
                boonus_toit_loendur = 0

            if not sõi:
                uss.pop()  # Eemalda saba kui ei söönud (uss ei kasva)

            # ── Kiiruse boonus haldamine ──
            if boonus_aktiivne:
                boonus_loendur -= 1
                if boonus_loendur <= 0:
                    boonus_aktiivne = False  # Boonus lõppes

            # ── Boonus toidu haldamine ──
            # Kas on aeg kuvada boonus toit?
            if boonus_toit_pos is None:
                boonus_toit_loendur += 1
                if boonus_toit_loendur >= BOONUS_TOIDU_ILMUMINE:
                    # Ilmuta roheline boonus toit
                    boonus_toit_pos = juhuslik_toit_positsioon(uss, takistused)
                    boonus_toit_loendur = 0
            else:
                # Boonus toit on ekraanil, loenda kestust
                boonus_toit_loendur += 1
                if boonus_toit_loendur >= BOONUS_TOIDU_KESTUS:
                    # Boonus toit kadus (ei söönud)
                    boonus_toit_pos = None
                    boonus_toit_loendur = 0

            animatsiooni_loendur += 1  # Suurenda animatsiooniloendut

            # ── Joonistamine ──
            joonista_ruudustik(ekraan, tume_teema)
            joonista_takistused(ekraan, takistused)
            joonista_toit(ekraan, toit_pos, toit_liik, animatsiooni_loendur)

            # Joonista boonus toit kui ekraanil
            if boonus_toit_pos:
                joonista_toit(ekraan, boonus_toit_pos, "boonus", animatsiooni_loendur)

            joonista_uss(ekraan, uss)
            joonista_infopaneel(ekraan, skoor, tase, len(uss),
                                boonus_loendur if boonus_aktiivne else 0, tume_teema)

            pygame.display.flip()

            # Kiirus sõltub kiiruse boonus olekust
            aktiivselt_kiirus = BOONUS_KIIRUS if boonus_aktiivne else praegune_kiirus
            kell.tick(aktiivselt_kiirus)

        # ── Mäng lõppes - küsi nimi ja salvesta rekord ──
        mängija_nimi = küsi_mängija_nimi(ekraan, tume_teema)
        salvesta_rekord(mängija_nimi, skoor, tase)

        # Kuva mäng läbi ekraan
        tulemus = kuva_mang_labi_ekraan(ekraan, skoor, tase, tume_teema)

        if tulemus == "välja":
            break  # Välju mängu põhitsüklist
        # Muul juhul: "uuesti" → tsükkel jätkub ja mäng alustatakse uuesti


def main():
    """
    Programmi sisendpunkt.
    Käivitab pygame ja põhimängu, lõpetab korrektselt.
    """
    try:
        põhimäng()
    except KeyboardInterrupt:
        print("\nMäng katkestati Ctrl+C-ga.")
    finally:
        pygame.quit()
        sys.exit()


# ── Programmi käivitamine ──────────────────────────────────────────────────────
if __name__ == "__main__":
    main()