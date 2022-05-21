import sys
import pygame
import plane
from pygame.locals import KEYDOWN, K_q, K_RIGHT, K_SPACE, K_UP, K_DOWN, K_LEFT, K_RETURN, K_r

# CONSTANTS:
import ctypes

user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

SCREENSIZE = WIDTH, HEIGHT = screensize  # 1920, 1080  # 1024, 768
BLACK = (0, 0, 0)
GREY = (160, 160, 160)
PADDING = PADTOPBOTTOM, PADLEFTRIGHT = 60, 60
# VARS:
_VARS = {'surf': False, "auto": False, "auto_time": 1000, "end": False}

pygame.font.init()
font = pygame.font.SysFont('Sans Serif', 26)


def main():
    pygame.init()

    _VARS['surf'] = pygame.display.set_mode(SCREENSIZE)

    m, n = 33, 7
    corridor = n // 2

    _VARS["dims"] = (m, n, corridor)
    _VARS["t"] = next_((0, plane.getGrid(m, n), plane.getPassengers(m, n, corridor)))

    while True:
        # drawGrid(3, 7)
        checkEvents()
        _VARS['surf'].fill(GREY)

        # pygame.display.update()


def next_(t):
    if len(t[2]) == 0:
        _VARS['auto'] = False
        _VARS['end'] = True
        return

    m, n, corridor = _VARS["dims"]

    # print(t[0])
    drawTurnNumber(t[0])

    t = plane.next_turn(t[2], t[0], t[1], corridor)

    drawGrid(m, n)
    for i in range(m):
        drawRect(i, corridor, (m, n))

    # pygame.display.update()

    for i in range(len(t[1])):
        for j in range(len(t[1][i])):
            s = plane.checkPlaceStatus(t[1], i, j)

            if s[0] == "occupied":
                drawRect(i, j, (m, n), (255, 0, 0))
                for p in range(len(s[1])):
                    drawText(i, j + p * 0.2, (m, n), s[1][p].ticket())
            elif s[0] == 'packing':
                drawRect(i, j, (m, n), (0, 0, 255))
                drawText(i, j, (m, n), s[1].ticket() + f", {s[1].seatingTime}")
            elif s[0] == "full":
                drawRect(i, j, (m, n), (0, 255, 0))
                drawText(i, j, (m, n), s[1].ticket())

    pygame.display.update()

    return t


def drawTurnNumber(turn):
    t = font.render(str(turn), False, BLACK)
    _VARS['surf'].blit(t, (PADDING[0] / 2, PADDING[1] / 2))


def drawTextRightUp(text, color=BLACK):
    t = font.render(str(text), False, color)
    _VARS['surf'].blit(t, (WIDTH - PADDING[0] / 2, PADDING[1] / 2))


def drawText(i, j, grid, text, color=BLACK):
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
                _VARS["t"] = next_((0, plane.getGrid(_VARS["dims"][0], _VARS["dims"][1]),
                                    plane.getPassengers(_VARS["dims"][0], _VARS["dims"][1], _VARS["dims"][2])))
                _VARS["end"] = False


if __name__ == '__main__':
    # import cProfile as profile
    #
    # profile.run('main()')

    main()
