import sys
import pygame
import plane
from pygame.locals import KEYDOWN, K_q, K_RIGHT, K_SPACE, K_UP, K_DOWN, K_LEFT, K_RETURN, K_r, K_7, K_8, K_9
import os
import configparser

if os.name == 'nt':
    import ctypes

    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
else:
    screensize = (1024, 768)

# CONSTANTS:
SCREENSIZE = WIDTH, HEIGHT = screensize  # 1920, 1080  # 1024, 768
BLACK = (0, 0, 0)
GREY = (160, 160, 160)
PADDING = PADTOPBOTTOM, PADLEFTRIGHT = 60, 60
# VARS:
_VARS = {'surf': False, "auto": False, "auto_time": 1000, "end": False}
turns = {}

pygame.font.init()
font = pygame.font.SysFont('Sans Serif', 26)


def main():
    pygame.init()

    _VARS['surf'] = pygame.display.set_mode(SCREENSIZE)

    # load config
    config = configparser.RawConfigParser()
    configFilePath = r'config.txt'
    config.read(configFilePath)

    print(config.get("passengers", "type"))

    m, n = int(config.get("aeroplane", "width")), int(config.get("aeroplane", "height"))  # 40, 13
    corridor = config.get("aeroplane", "corridor") or n // 2
    corridor = int(corridor)
    _VARS["pt"] = passengersType = config.get("passengers", "type") or "random"
    _VARS["p_opts"] = {}
    _VARS["p_opts"]["section_width"] = int(config.get("sections", "width"))
    _VARS["p_opts"]["packing_time"] = int(config.get("passengers", "packingTime"))

    _VARS["t_opts"] = {}
    _VARS["t_opts"]["barging_time"] = int(config.get("passengers", "bargingTime"))

    _VARS["dims"] = (m, n, corridor)
    _VARS["t"] = next_((0, plane.getGrid(m, n), plane.getPassengers(m, n, corridor, passengersType, _VARS["p_opts"])))

    while True:
        # drawGrid(3, 7)
        checkEvents()
        _VARS['surf'].fill(GREY)

        if _VARS['auto'] and _VARS["auto_time"] > 0:
            drawText(str(round(1 / (_VARS["auto_time"] / 1000), 1)) + " turns/s", WIDTH - 2.5 * PADDING[0],
                     HEIGHT - (PADDING[1] / 2))

        # pygame.display.update()


def prev_():
    if len(turns) < 3 or _VARS["t"][0] < 2:
        return

    _VARS["auto"] = False

    print("prev to", turns[1][0])
    if not _VARS["end"] and 1 in turns:
        print(turns[1])
        next_(turns[1])  # _VARS['t'][0]-2

    return


def next_(t):
    if len(t[2]) == 0:
        _VARS['auto'] = False
        _VARS['end'] = True
        return

    m, n, corridor = _VARS["dims"]

    drawTurnNumber(t[0])
    drawText("Type: " + _VARS["pt"], WIDTH - 3 * PADDING[0], (PADDING[1] / 4))

    t = plane.next_turn(t[2], t[0], t[1], corridor, _VARS["t_opts"])

    drawGrid(m, n)
    for i in range(m):
        drawRect(i, corridor, (m, n))

    for i in range(len(t[1])):
        for j in range(len(t[1][i])):
            s = plane.checkPlaceStatus(t[1], i, j, corridor)

            if s[0] == "occupied":
                drawRect(i, j, (m, n), (69, 179, 224))  # blue
                for p in s[1]:
                    if p.toWait > 0:
                        drawRect(i, j, (m, n), (171, 209, 0))  # yellow
                        drawTextGrid(i, j + 0.2, (m, n), f"{p.toWait} left")

                        break

                for p in range(len(s[1])):
                    drawTextGrid(i, j + p * 0.4, (m, n), s[1][p].ticket())
            elif s[0] == 'packing':
                drawRect(i, j, (m, n), (201, 29, 62))  # red
                drawTextGrid(i, j, (m, n), s[1].ticket())
                drawTextGrid(i, j + 0.2, (m, n), f"{s[1].seatingTime} left")
            elif s[0] == "full":
                drawRect(i, j, (m, n), (71, 209, 71))  # green
                drawTextGrid(i, j, (m, n), s[1].ticket())
                drawTextGrid(i, j + 0.2, (m, n), s[1].idleTime)

    pygame.display.update()

    if t[0] not in turns:
        turns[t[0]] = t
    return t


def reset():
    _VARS["t"] = next_((0, plane.getGrid(_VARS["dims"][0], _VARS["dims"][1]), plane.getPassengers(_VARS["dims"][0],
                        _VARS["dims"][1], _VARS["dims"][2], _VARS["pt"], _VARS["p_opts"])))
    _VARS["end"] = False


def drawTurnNumber(turn):
    t = font.render("Turn: " + str(turn), False, BLACK)
    _VARS['surf'].blit(t, (PADDING[0] / 3, PADDING[1] / 4))


def drawText(text, x, y, color=BLACK):
    t = font.render(str(text), False, color)
    _VARS['surf'].blit(t, (x, y))


def drawTextGrid(i, j, grid, text, color=BLACK):
    horizontal_cellsize = (WIDTH - (PADLEFTRIGHT * 2)) / grid[0]
    vertical_cellsize = (HEIGHT - (PADTOPBOTTOM * 2)) / grid[1]

    t = font.render(str(text), False, color)
    _VARS['surf'].blit(t, (PADDING[0] + i * horizontal_cellsize, PADDING[0] + j * vertical_cellsize))


def drawRect(i, j, grid, color=BLACK):
    horizontal_cellsize = (WIDTH - (PADLEFTRIGHT * 2)) / grid[0]
    vertical_cellsize = (HEIGHT - (PADTOPBOTTOM * 2)) / grid[1]

    pygame.draw.rect(
        _VARS['surf'], color,
        (PADDING[0] + i * horizontal_cellsize, PADDING[0] + j * vertical_cellsize, horizontal_cellsize,
         vertical_cellsize)
    )


def drawGrid(m, n):
    # DRAW Rectangle
    # TOP lEFT TO RIGHT
    pygame.draw.line(
        _VARS['surf'], BLACK,
        (0 + PADLEFTRIGHT, 0 + PADTOPBOTTOM),
        (WIDTH - PADLEFTRIGHT, 0 + PADTOPBOTTOM), 2)
    # BOTTOM lEFT TO RIGHT
    pygame.draw.line(
        _VARS['surf'], BLACK,
        (0 + PADLEFTRIGHT, HEIGHT - PADTOPBOTTOM),
        (WIDTH - PADLEFTRIGHT, HEIGHT - PADTOPBOTTOM), 2)
    # LEFT TOP TO BOTTOM
    pygame.draw.line(
        _VARS['surf'], BLACK,
        (0 + PADLEFTRIGHT, 0 + PADTOPBOTTOM),
        (0 + PADLEFTRIGHT, HEIGHT - PADTOPBOTTOM), 2)
    # RIGHT TOP TO BOTTOM
    pygame.draw.line(
        _VARS['surf'], BLACK,
        (WIDTH - PADLEFTRIGHT, 0 + PADTOPBOTTOM),
        (WIDTH - PADLEFTRIGHT, HEIGHT - PADTOPBOTTOM), 2)

    # Get cell size
    horizontal_cellsize = (WIDTH - (PADLEFTRIGHT * 2)) / m
    vertical_cellsize = (HEIGHT - (PADTOPBOTTOM * 2)) / n

    # VERTICAL DIVISIONS: (0,1,2) for grid(3) for example
    for x in range(max(m, n)):
        pygame.draw.line(
            _VARS['surf'], BLACK,
            (0 + PADLEFTRIGHT + (horizontal_cellsize * x), 0 + PADTOPBOTTOM),
            (0 + PADLEFTRIGHT + horizontal_cellsize * x, HEIGHT - PADTOPBOTTOM), 2)
        # HORITZONTAL DIVISION
        pygame.draw.line(
            _VARS['surf'], BLACK,
            (0 + PADLEFTRIGHT, 0 + PADTOPBOTTOM + (vertical_cellsize * x)),
            (WIDTH - PADLEFTRIGHT, 0 + PADTOPBOTTOM + (vertical_cellsize * x)), 2)

    # add labels
    for i in range(m):
        drawText(i + 1, PADDING[0] + i * horizontal_cellsize, PADDING[1] - 20)
    for j in range(n):
        drawText(chr(65 + j), PADDING[0] - 20, PADDING[1] + j * vertical_cellsize)


def checkEvents():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if not _VARS["end"] and _VARS["auto"] and pygame.time.get_ticks() - _VARS["last_auto"] > _VARS["auto_time"]:
                _VARS["t"] = next_(_VARS["t"])
                _VARS["last_auto"] = pygame.time.get_ticks()

        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == KEYDOWN:
            if event.key == K_q:
                pygame.quit()
                sys.exit()
            elif event.key == K_LEFT:
                # prev_()
                print("l")

            elif event.key == K_RIGHT:
                if not _VARS["end"]:
                    _VARS["t"] = next_(_VARS["t"])
            elif event.key == K_SPACE:
                print("SPACE")

                _VARS["last_auto"] = pygame.time.get_ticks()
                pygame.time.set_timer(pygame.event.Event(pygame.USEREVENT, id='next'), 50)
                _VARS["auto"] = not _VARS["auto"]
            elif event.key == K_UP:
                if _VARS["auto_time"] > 50:
                    _VARS["auto_time"] -= 50
                # drawTextRightUp(_VARS["auto_time"])
            elif event.key == K_DOWN:
                _VARS["auto_time"] += 50
                # drawTextRightUp(_VARS["auto_time"])
            elif event.key == K_RETURN:
                _VARS["auto"] = True
                _VARS["auto_time"] = 0
                _VARS["last_auto"] = pygame.time.get_ticks()

                pygame.time.set_timer(pygame.event.Event(pygame.USEREVENT, id='next'), 5)

            elif event.key == K_r:
                reset()
            elif event.key == K_7:
                _VARS["pt"] = "random"
                reset()
            elif event.key == K_8:
                _VARS["pt"] = "seat"
                reset()
            elif event.key == K_9:
                _VARS["pt"] = "section"
                reset()


if __name__ == '__main__':
    # import cProfile as profile
    #
    # profile.run('main()')

    main()
