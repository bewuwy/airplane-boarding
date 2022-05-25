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
            return f"{self.ticketRow + 1}{chr(65 + self.ticketSeat)}"
        else:
            return f"{self.ticketRow + 1}{chr(65 + self.ticketSeat // 26 - 1)}{chr(65 + self.ticketSeat - 26)}"


class Plane:
    def __init__(self, m, n, corridor_y):
        self.grid = []
        self.corridorSeat = corridor_y
        self.passengers = []

        self.m = m
        self.n = n

        self.turn = 0

        for seat in range(m):
            t_ = []
            for row in range(n):
                t_.append([])
            self.grid.append(t_)

    def createPassengers(self, type_, options=None):  # generate random people
        packing_time = None
        section_width = 6

        if options is None:
            options = {}
        if "packing_time" in options:
            packing_time = options["packing_time"]
        if "section_width" in options:
            section_width = options["section_width"]

        p = []  # passengers list
        if type_ == "random":  # random passengers distribution 
            for seat in range(self.m):
                if seat != self.corridorSeat:
                    for row in range(self.n):
                        p.insert(randrange(len(p) + 1),
                                 Person(row, seat, str(row) + str(seat), packing_time))

        elif type_ == "seat":  # seat-based passengers distribution
            for seat in range(self.m):
                if seat != self.corridorSeat:
                    i_ = list(range(0, self.n))
                    random.shuffle(i_)

                    for row in range(self.n):
                        if seat > self.corridorSeat:
                            p.append(
                                Person(i_[row], self.m - seat + self.corridorSeat, str(row) + str(seat), packing_time))
                        else:
                            p.append(Person(i_[row], seat, str(row) + str(seat), packing_time))

        elif type_ == "section":  # section-based passengers distribution
            def chunks(lst, n_):
                """Yield successive n-sized chunks from lst."""
                for i__ in range(0, len(lst), n_):
                    yield lst[i__:i__ + n_]

            sections = list(chunks(list(range(0, self.n)), section_width))
            sections.reverse()

            for s in sections:
                sp = []  # section passengers
                for row in range(len(s)):
                    for seat in range(self.m):
                        if seat != self.corridorSeat:
                            # print(Person(s[column], row, str(s[column]) + str(row)))
                            sp.insert(randrange(len(sp) + 1), Person(s[row], seat, str(s[row]) + str(seat)))  # a-i-1

                p.extend(sp)

        self.passengers = p

    def checkIfPlaceEmpty(self, row, seat):
        if len(self.grid[seat][row]) == 0 or \
                (len(self.grid[seat][row]) == 1 and self.grid[seat][row][0].check_seated()):

            return True
        else:
            return False

    def checkPlaceStatus(self, row, seat):
        if len(self.grid[seat][row]) == 0:
            return "empty", None
        if len(self.grid[seat][row]) == 1:
            if self.grid[seat][row][0].check_seated():
                return "boarded", self.grid[seat][row][0]
            elif row == self.grid[seat][row][0].ticketRow and seat == self.corridorSeat:
                return "packing", self.grid[seat][row][0]

        return "standing", self.grid[seat][row]

    def checkIfAllSeated(self):
        for seat in self.grid:
            for place in seat:
                if place[0].check_seated() == False:
                    return False
        return True

    def movePerson(self, passenger, row, seat):
        if passenger.toWait > 0:
            passenger.toWait -= 1
            passenger.idleTime += 1

            return False

        # deleting the person from old place
        if passenger.currentRow > -1 and passenger.currentSeat > -1 \
                and passenger in self.grid[passenger.currentSeat][passenger.currentRow]:
            self.grid[passenger.currentSeat][passenger.currentRow].remove(passenger)

        # adding the person in new place
        passenger.currentSeat = seat
        passenger.currentRow = row

        self.grid[seat][row].append(passenger)

        return True

    def next_turn(self, options=None):
        barging_time = 1

        if options is None:
            options = {}
        if "barging_time" in options:
            barging_time = options["barging_time"]

        # print(f"turn {t_num}")

        toRemove = []
        for p in self.passengers:  # trying to move every passenger
            if p.currentRow < 0:  # person not on plane yet
                if self.checkIfPlaceEmpty(0, self.corridorSeat):  # entrance empty
                    self.movePerson(p, 0, self.corridorSeat)
                    continue
                else:  # entrance taken
                    p.idleTime += 1
                    continue

            if p.currentRow >= 0:  # person already on plane
                if p.currentRow == p.ticketRow:  # person in a correct row
                    if p.currentSeat == p.ticketSeat:  # person in a correct seat
                        toRemove.append(p)
                        continue

                    if p.ticketSeat < self.corridorSeat:
                        toMoveY = p.currentSeat - 1
                    else:
                        toMoveY = p.currentSeat + 1

                    if p.currentSeat == self.corridorSeat and p.seatingTime > 0:
                        # if person in the corridor and still has something to pack
                        p.seatingTime -= 1
                        continue
                    elif self.checkIfPlaceEmpty(p.currentRow, toMoveY):  # if seat left/right of current seat empty
                        self.movePerson(p, p.currentRow, toMoveY)

                        if len(self.grid[toMoveY][p.currentRow]) > 1:
                            p.toWait = barging_time

                        continue
                    else:  # if seat left/right of current seat taken
                        p.idleTime += 1

                elif p.currentRow != p.ticketRow:  # person not in a correct row
                    if self.checkIfPlaceEmpty(p.currentRow + 1, p.currentSeat):  # if next place in the corridor empty
                        self.movePerson(p, p.currentRow + 1, p.currentSeat)
                        continue
                    else:  # standing idle
                        p.idleTime += 1

        for p_ in toRemove:
            self.passengers.remove(p_)
            # grid_[i_.currentRow][i_.currentSeat] = 0

        self.turn += 1  # increment number of turns
        # pp.pprint(grid_)

        return self.turn  # t_num, grid_, people_


if __name__ == '__main__':
    m, n, cy = 6 + 1, 33, 3  # +1 in m because of corridor

    # test_types = ["random"]
    test_types = ["random", "seat", ["section", {"section_width": 6}], ["section", {"section_width": 3}],
                  ["section", {"section_width": 12}]]
    # test_types = [["random", {"barging_time": 1, "packing_time": 2}], ["random", {"barging_time": 0,
    # "packing_time": 4}]]

    tests = 10

    print(f"plane with {n} rows and {m} seats, corridor at {cy}")

    all_results = {}
    for t in test_types:
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
            print(f"{i + 1}/{tests} {t}", end='\r')

            # people = getPassengers(n, m, corridorY, t, s_opt)
            # t_num = 0
            # grid = getGrid(n, m)
            plane = Plane(m, n, cy)
            plane.createPassengers(t, s_opt)

            t_num = 0
            while plane.passengers:
                t_num = plane.next_turn(t_opts)

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
        print(f"{i + 1}.: {all_results[best_results[i]]} - {best_results[i]}")
