import pprint
from random import randrange

pp = pprint.PrettyPrinter(indent=4)


class Person:
    def __init__(self, ticket_row, ticket_seat, id_=0):
        self.ticketRow = ticket_row
        self.ticketSeat = ticket_seat

        self.currentRow = -1
        self.currentSeat = -1

        self.seatingTime = 1

        self.id = id_

    def __repr__(self):
        if self.currentRow == self.ticketRow and self.currentSeat == self.ticketSeat:
            return f"p{self.id}"

        current = "currently: "
        if self.currentRow < 0:
            current += "off plane"
        else:
            current += f"{chr(65 + self.currentRow)}{self.currentSeat}"
        current += ", "

        s_ = f"p{self.id}({current}ticket: {chr(65 + self.ticketRow)}" \
             f"{self.ticketSeat}, until seat: {self.seatingTime})"

        return s_

    def check_seated(self):
        return self.currentRow == self.ticketRow and self.currentSeat == self.ticketSeat

    def ticket(self):
        if self.ticketRow < 26:
            return f"{chr(65 + self.ticketRow)}{self.ticketSeat}"
        else:
            return f"{chr(65 + self.ticketRow//26 - 1)}{chr(65 + self.ticketRow - 26)}{self.ticketSeat}"


def getPassengers(a, b, cy):  # generate random people
    p = []

    for i in range(b):
        if i != cy:
            for j in range(a):
                p.insert(randrange(len(p) + 1), Person(j, i, str(j) + str(i)))

    return p


def getGrid(a, b):
    g = []  # airplane a by b
    for m_ in range(a):  # populate the grid
        t_ = []
        for n_ in range(b):
            t_.append([])
        g.append(t_)

    return g


def checkIfPlaceEmpty(grid_, row, seat):
    if len(grid_[row][seat]) == 0 or (len(grid_[row][seat]) == 1 and grid_[row][seat][0].check_seated()):
        return True
    else:
        return False


def checkIfAllSeated(grid_):
    for row in grid_:
        for seat in row:
            if seat[0].check_seated() is False:
                return False
    return True


def checkPlaceStatus(grid_, row, seat):
    corridor = len(grid_[0]) // 2

    if len(grid_[row][seat]) == 0:
        return "empty", None
    if len(grid_[row][seat]) == 1:
        if grid_[row][seat][0].check_seated():
            return "full", grid_[row][seat][0]
        elif row == grid_[row][seat][0].ticketRow and seat == corridor:
            return "packing", grid_[row][seat][0]

    return "occupied", grid_[row][seat]


def movePerson(p_, row, seat, grid_):
    # deleting the person from old place
    if p_.currentRow > -1 and p_.currentSeat > -1 and p_ in grid_[p_.currentRow][p_.currentSeat]:
        grid_[p_.currentRow][p_.currentSeat].remove(p_)

    # adding the person in new place
    p_.currentRow = row
    p_.currentSeat = seat

    grid_[row][seat].append(p_)

    return grid_


def next_turn(people_, t_num, grid_, corridor):
    toRemove = []
    print(f"turn {t_num + 1}")

    for p in people_:
        if p.currentRow < 0:  # person not on plane yet
            if checkIfPlaceEmpty(grid_, 0, corridor):  # entrance empty
                grid_ = movePerson(p, 0, corridor, grid_)
                continue
            else:  # entrance taken
                continue

        if p.currentRow >= 0:  # person already on plane
            if p.currentRow == p.ticketRow:  # person in a correct row
                if p.currentSeat == p.ticketSeat:  # person in a correct seat
                    toRemove.append(p)
                    continue

                if p.ticketSeat < corridor:
                    toMoveY = p.currentSeat - 1
                else:
                    toMoveY = p.currentSeat + 1

                if p.currentSeat == corridor and p.seatingTime > 0:  # if person in the corridor and still has
                    # something to pack
                    p.seatingTime -= 1
                    continue
                if checkIfPlaceEmpty(grid_, p.currentRow, toMoveY):  # if seat left/right of current seat empty
                    grid_ = movePerson(p, p.currentRow, toMoveY, grid_)
                    continue

            if p.currentRow != p.ticketRow:  # person not in a correct row
                if checkIfPlaceEmpty(grid_, p.currentRow + 1, p.currentSeat):  # if next place in the corridor empty
                    grid_ = movePerson(p, p.currentRow + 1, p.currentSeat, grid_)
                    continue

    for i_ in toRemove:
        people_.remove(i_)
        # grid_[i_.currentRow][i_.currentSeat] = 0

    t_num += 1  # increment number of turns
    # pp.pprint(grid_)

    return t_num, grid_, people_


if __name__ == '__main__':
    m, n = 6 + 1, 3  # +1 in m because of corridor
    corridorY = 3

    grid = getGrid(n, m)
    print(grid)

    # people = [Person(0, 0, 1), Person(2, 1, 2), Person(1, 2, 3)]  # person  - [x, y]
    people = getPassengers(n, m, corridorY)

    print("People list:\n")
    pp.pprint(people)
    print(f"{len(people)} passengers")

    print("\nTurns: \n")
    t = [0, grid, people]
    while people:  # 3 test turns
        t = next_turn(t[2], t[0], t[1], corridorY)

    # finished seating
    print(t)
