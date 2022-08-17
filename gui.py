from Plane import Plane
from boarding import createPassengers, next_boarding_turn

import sys
import pygame
from pygame.locals import KEYDOWN, K_q, K_RIGHT, K_SPACE, K_UP, K_DOWN, K_LEFT, K_RETURN, K_r, K_7, K_8, K_9
import configparser


# CONSTANTS:
BLACK = (0, 0, 0)
GREY = (160, 160, 160)
PADDING = PADTOPBOTTOM, PADLEFTRIGHT = 60, 60
    

def main():
    pygame.init()

    fullscreen = config.get("window", "fullscreen")
    if fullscreen == "True":
        _VARS['surf'] = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        _VARS['surf'] = pygame.display.set_mode(SCREENSIZE)
        
    _VARS['l_opts'] = {}
    _VARS["l_opts"]["showBoardingTime"] = config.get("labels", "showBoardingTime").lower() == "true"
    _VARS["l_opts"]["showLC"] = config.get("labels", "showLC").lower() == "true"
    
    _VARS["p_opts"] = {}

    m, n = int(config.get("airplane", "seats")), int(config.get("airplane", "rows"))
    if config.get("airplane", "columnsLengths"):
        _VARS['p_opts']['columns_lengths'] = [int(i) for i in config.get("airplane", "columnsLengths").split(",")]
    else:
        _VARS['p_opts']['columns_lengths'] = None
    corridors = [int(i) for i in config.get("airplane", "corridors").split(",")]
    
    _VARS["pt"] = config.get("passengers", "type")
    # print(config.get("passengers", "type"))
    
    _VARS["p_opts"]["section_width"] = int(config.get("sections", "width"))
    _VARS["p_opts"]["packing_time"] = []
    for i in config.get("passengers", "packingTime").split(", "):
        _VARS["p_opts"]["packing_time"].append(int(i))
    _VARS["p_opts"]["naughty_chance"] = float(config.get("passengers", "naughtyChance"))
    _VARS["p_opts"]["reverse"] = config.get("passengers", "reverse").lower() == "true"

    _VARS["t_opts"] = {}
    _VARS["t_opts"]["barging_time"] = int(config.get("passengers", "bargingTime"))

    _VARS["plane"] = Plane(m, n, corridors, _VARS['p_opts']['columns_lengths'])
    createPassengers(_VARS["plane"],_VARS["pt"], _VARS["p_opts"])
    
    while True:
        _VARS['surf'].fill(GREY)
        checkEvents()
        
        # TODO: update screen every frame not every next_turn
        #! update screen every frame not every next_turn

        # pygame.display.update()


def next_():
    plane = _VARS["plane"]
    
    if len(plane.passengers) == 0:
        _VARS['auto'] = False
        _VARS['end'] = True
        return
    
    m, n, corridors = plane.m, plane.n, plane.corridors

    drawTurnNumber(plane.turn)
    
    if _VARS['auto']:
        if _VARS["auto_time"] > 0:
            t = str(round(1 / (_VARS["auto_time"] / 1000), 1)) + " turns/s"
        else:
            t = "FAST"

        drawText(t, WIDTH - 2.5 * PADDING[0], HEIGHT - (PADDING[1] / 2))
    
    typeText = "Type: " + _VARS["pt"]
    if _VARS["p_opts"]["reverse"]:
        typeText += " (r)"
    
    drawText(typeText, WIDTH - PADDING[0] - font.size(typeText)[0], (PADDING[1] / 4))

    next_boarding_turn(plane, _VARS["t_opts"])

    drawGrid(plane.grid)
    for c in corridors:
        for i in range(n):  # draw corridor in black
            # if place empty
            if plane.grid[c][i] == []:
                drawRect(c, i)

    for seat in range(len(plane.grid)):
        for row in range(len(plane.grid[seat])):
            status = plane.checkPlaceStatus(row, seat)

            if status[0] == "standing":  # drawing a standing person
                drawRect(seat, row, (69, 179, 224))  # blue
                for p in status[1]:
                    if p.naughty and _VARS['l_opts']['showLC']:
                        drawTextGrid(seat + 0.8, row, "LC")
                    
                    if p.toWait > 0 or p.barged:
                        drawRect(seat, row, (171, 209, 0))  # yellow
                        drawTextGrid(seat + 0.2, row, f"{p.toWait} left")

                        break

                for p in range(len(status[1])):
                    drawTextGrid(seat + p * 0.4, row, status[1][p].ticket())

            elif status[0] == 'packing':  # drawing a person packing
                drawRect(seat, row, (201, 29, 62))  # red
                drawTextGrid(seat, row, status[1].ticket())
                drawTextGrid(seat + 0.2, row, f"{status[1].seatingTime} left")
                
            elif status[0] == "boarded":  # drawing a person that's already booked
                drawRect(seat, row, (71, 209, 71))  # green
                drawTextGrid(seat, row, status[1].ticket())
                
                if _VARS["l_opts"]['showBoardingTime']:
                    drawTextGrid(seat + 0.2, row, status[1].boardingTime)

    pygame.display.update()


def reset():
    _VARS["plane"] = Plane(_VARS["plane"].m, _VARS["plane"].n, _VARS["plane"].corridors, _VARS['p_opts']['columns_lengths'])
    createPassengers(_VARS["plane"], _VARS["pt"], _VARS["p_opts"])
    
    _VARS["end"] = False
    next_() # TODO: draw the first turn
    

def drawTurnNumber(turn):
    t = font.render("Turn: " + str(turn), False, BLACK)
    _VARS['surf'].blit(t, (PADDING[0] / 3, PADDING[1] / 4))


def drawText(text, x, y, color=BLACK):
    t = font.render(str(text), False, color)
    _VARS['surf'].blit(t, (x, y))


def drawTextGrid(m, n, text, color=BLACK):
    horizontal_cellsize = (WIDTH - (PADLEFTRIGHT * 2)) / _VARS["plane"].n
    vertical_cellsize = (HEIGHT - (PADTOPBOTTOM * 2)) / _VARS["plane"].m

    t = font.render(str(text), False, color)
    _VARS['surf'].blit(t, (PADDING[0] + n * horizontal_cellsize, PADDING[0] + m * vertical_cellsize))


def drawRect(m, n, color=BLACK):
    horizontal_cellsize = (WIDTH - (PADLEFTRIGHT * 2)) / _VARS["plane"].n
    vertical_cellsize = (HEIGHT - (PADTOPBOTTOM * 2)) / _VARS["plane"].m

    pygame.draw.rect(
        _VARS['surf'], color,
        (PADDING[0] + n * horizontal_cellsize, PADDING[0] + m * vertical_cellsize, horizontal_cellsize,
         vertical_cellsize)
    )


def drawGrid(grid):
    m = len(grid)
    n = max(len(row) for row in grid)
    
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
    horizontal_cellsize = (WIDTH - (PADLEFTRIGHT * 2)) / n
    vertical_cellsize = (HEIGHT - (PADTOPBOTTOM * 2)) / m

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

    # fill blank spaces
    for column in range(m):
        if len(grid[column]) < n:
            for row in range(n - len(grid[column])):
                drawRect(column, n - (row+1), GREY)

    # add labels
    for i in range(n):
        drawText(i + 1, PADDING[0] + i * horizontal_cellsize, PADDING[1] - 20)
    for j in range(m):
        drawText(chr(65 + j), PADDING[0] - 20, PADDING[1] + j * vertical_cellsize)


def checkEvents():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            if not _VARS["end"] and _VARS["auto"] and pygame.time.get_ticks() - _VARS["last_auto"] > _VARS["auto_time"]:
                next_()
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
                    next_()
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
    # load config
    config = configparser.RawConfigParser()
    configFilePath = r'config.txt'
    config.read(configFilePath)
    
    SCREENSIZE = WIDTH, HEIGHT = int(config.get("window", "width")), int(config.get("window", "height"))

    # VARS:
    _VARS = {'surf': False, "auto": False, "auto_time": 1000, "end": False}
    turns = {}

    pygame.font.init()
    font = pygame.font.SysFont('Sans Serif', 26)
    
    main()
