import pprint
import random
from random import randrange

pp = pprint.PrettyPrinter(indent=4)


class Person:
    def __init__(self, ticket_row, ticket_seat, id_=0, seating_time=None):
        self.ticketRow = ticket_row
        self.ticketSeat = ticket_seat

        self.currentRow = -1
        self.currentSeat = -1

        if seating_time is None:
            seating_time = random.choice(random.choices((2, 3, 4), weights=(2, 2, 1), k=10))

        self.seatingTime = seating_time
        self.toWait = 0
        self.idleTime = 0

        self.id = id_

    def __repr__(self):
        if self.currentRow == self.ticketRow and self.currentSeat == self.ticketSeat:
            return f"p{self.id}"

        current = "currently: "
        if self.currentRow < 0:
            current += "off plane"
        else:
            current += f"{self.currentRow}{chr(65 + self.currentSeat)}"
        current += ", "

        s_ = f"p{self.id}({current}ticket: {self.ticket()})"

        return s_

    def check_seated(self):
        return self.currentRow == self.ticketRow and self.currentSeat == self.ticketSeat

    def ticket(self):
        if self.ticketSeat < 26:
            return f"{self.ticketRow+1}{chr(65 + self.ticketSeat)}"
        else:
            return f"{self.ticketRow+1}{chr(65 + self.ticketSeat//26 - 1)}{chr(65 + self.ticketSeat - 26)}"


def getPassengers(a, b, cy, type_, opts=None):  # generate random people
    pt = None
    if opts is None:
        opts = {}
    elif "packing_time" in opts:
        pt = opts["packing_time"]

    p = []
    if type_ == "random":
        for i in range(b):
            if i != cy:
                for j in range(a):
                    p.insert(randrange(len(p) + 1), Person(j, i, str(j) + str(i), pt))
    elif type_ == "seat":
        for i in range(b):
            if i != cy:
                i_ = list(range(0, a))
                random.shuffle(i_)

                for j in range(a):
                    if i > cy:
                        p.append(Person(i_[j], b-i+cy, str(j) + str(i), pt))
                    else:
                        p.append(Person(i_[j], i, str(j) + str(i), pt))
    elif type_ == "section":
        section_width = 6
        if "section_width" in opts:
            section_width = opts["section_width"]

        def chunks(lst, n_):
            """Yield successive n-sized chunks from lst."""
            for i__ in range(0, len(lst), n_):
                yield lst[i__:i__ + n_]

        sections = list(chunks(list(range(0, a)), section_width))
        sections.reverse()

        for s in sections:
            sp = []
            for column in range(len(s)):
                for row in range(b):
                    if row != cy:
                        # print(Person(s[column], row, str(s[column]) + str(row)))
                        sp.insert(randrange(len(sp) + 1), Person(s[column], row, str(s[column]) + str(row)))  # a-i-1

            p.extend(sp)

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


def checkPlaceStatus(grid_, row, seat, corridor):
    if len(grid_[row][seat]) == 0:
        return "empty", None
    if len(grid_[row][seat]) == 1:
        if grid_[row][seat][0].check_seated():
            return "full", grid_[row][seat][0]
        elif row == grid_[row][seat][0].ticketRow and seat == corridor:
            return "packing", grid_[row][seat][0]

    return "occupied", grid_[row][seat]


def movePerson(p_, row, seat, grid_):
    if p_.toWait > 0:
        p_.toWait -= 1
        p_.idleTime += 1

        return grid_

    # deleting the person from old place
    if p_.currentRow > -1 and p_.currentSeat > -1 and p_ in grid_[p_.currentRow][p_.currentSeat]:
        grid_[p_.currentRow][p_.currentSeat].remove(p_)

    # adding the person in new place
    p_.currentRow = row
    p_.currentSeat = seat

    grid_[row][seat].append(p_)

    return grid_


def next_turn(people_, t_num, grid_, corridor, opts=None):
    if opts is None:
        opts = {}

    barging_time = 1
    if "barging_time" in opts:
        barging_time = opts["barging_time"]

    toRemove = []
    # print(f"turn {t_num}")

    for p in people_:
        if p.currentRow < 0:  # person not on plane yet
            if checkIfPlaceEmpty(grid_, 0, corridor):  # entrance empty
                grid_ = movePerson(p, 0, corridor, grid_)
                continue
            else:  # entrance taken
                p.idleTime += 1
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
                elif checkIfPlaceEmpty(grid_, p.currentRow, toMoveY):  # if seat left/right of current seat empty
                    grid_ = movePerson(p, p.currentRow, toMoveY, grid_)

                    if len(grid_[p.currentRow][toMoveY]) > 1:
                        p.toWait = barging_time

                    continue
                else:  # if seat left/right of current seat taken
                    p.idleTime += 1

            elif p.currentRow != p.ticketRow:  # person not in a correct row
                if checkIfPlaceEmpty(grid_, p.currentRow + 1, p.currentSeat):  # if next place in the corridor empty
                    grid_ = movePerson(p, p.currentRow + 1, p.currentSeat, grid_)
                    continue
                else:  # standing idle
                    p.idleTime += 1

    for i_ in toRemove:
        people_.remove(i_)
        # grid_[i_.currentRow][i_.currentSeat] = 0

    t_num += 1  # increment number of turns
    # pp.pprint(grid_)

    return t_num, grid_, people_


if __name__ == '__main__':
    m, n = 8 + 1, 43  # +1 in m because of corridor
    corridorY = 4
    types = ["random", "seat", ["section", {"section_width": 6}], ["section", {"section_width": 3}],
             ["section", {"section_width": 12}]]

    # types = [["random", {"barging_time": 1, "packing_time": 2}], ["random", {"barging_time": 0, "packing_time": 4}]]

    s_opt = {"section_width": 6}
    tests = 100
    
    print(f"plane with {n} rows and {m} seats, corridor at {corridorY}")

    all_results = {}
    for t in types:
        print()
        results = []
        t_opts = {}
        s_opt = {}

        if isinstance(t, list):
            if "barging_time" in t[1]:
                barging_time = t[1]["barging_time"]
                t_opts = {"barging_time": barging_time}

            if t[0] == "section":
                s_opt = t[1]
            if "packing_time" in t[1]:
                packing_time = t[1]["packing_time"]
                s_opt["packing_time"] = packing_time

            t = t[0]

        for i in range(tests):
            print(f"{i+1}/{tests} {t}", end='\r')

            people = getPassengers(n, m, corridorY, t, s_opt)
            t_num = 0
            grid = getGrid(n, m)

            while people:
                t_num, grid, people = next_turn(people, t_num, grid, corridorY, t_opts)

            # print(t_num, end='\r')
            results.append(t_num)

        if t == "section":
            t += " (width " + str(s_opt["section_width"]) + ")"

        print(f"\nresults for {t} passengers distribution ({tests} tests):")
        print(f"average: {sum(results) / tests}")
        print(f"range: {min(results)}-{max(results)}")
        print(t_opts, s_opt)

        all_results[sum(results) / tests] = t

    best_results = list(all_results.keys())
    best_results.sort()

    print()
    for i in range(min(len(best_results), 5)):
        print(f"{i+1}.: {all_results[best_results[i]]} - {best_results[i]}")

    quit()

    # people = [Person(0, 0, 1), Person(2, 1, 2), Person(1, 2, 3)]  # person  - [x, y]
    people = getPassengers(n, m, corridorY, types[0])

    # print("People list:\n")
    # pp.pprint(people)
    # print(f"{len(people)} passengers")

    # print("\nTurns: \n")
    grid = getGrid(n, m)
    t = [0, grid, people]
    while people:  # 3 test turns
        t = next_turn(t[2], t[0], t[1], corridorY)

    # finished seating
    print(t[0])
