import random
from random import randrange


class Person:
    def __init__(self, ticket_row, ticket_seat, options=None, corridors=(), id_=None):
        packing_time = None
        if options is None:
            options = {}
        if "packing_time" in options:
            packing_time = options["packing_time"]
        
        self.ticketRow = ticket_row
        self.ticketSeat = ticket_seat

        self.currentRow = -1
        self.currentSeat = -1

        if packing_time is None:
            packing_time = random.choice(random.choices((2, 3, 4), weights=(2, 2, 1), k=10))

        self.seatingTime = packing_time
        self.toWait = 0
        
        self.idleTime = 0
        self.boardingTime = 0
        self.naughty = False

        self.entranceCorridors = []
        if self.ticketSeat > corridors[-1]:
            self.entranceCorridors.append(corridors[-1])
        elif self.ticketSeat < corridors[0]:
            self.entranceCorridors.append(corridors[0])
        else:
            for e in range(len(corridors)):
                self.entranceCorridors.append(corridors[e])
                if len(self.entranceCorridors) > 2:
                    self.entranceCorridors.pop(0)

                if corridors[e] > self.ticketSeat:
                    break

        if id_ is None:
            id_ = str(self.ticketRow) + str(self.ticketSeat)
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
    def __init__(self, m, n, corridors):
        self.grid = []
        self.corridors = corridors
        self.passengers = []

        self.m = m
        self.n = n

        self.turn = 0

        for seat in range(m):
            t_ = []
            for row in range(n):
                t_.append([])
            self.grid.append(t_)
            
        self.idleList = []
        self.boardingTimeList = []
        
    def createPassengers(self, type_, options=None):  # generate random people
        # print(type_)
        
        packing_time = [3, 3, 3, 4]
        section_width = 6
        naughty_chance = 0.1

        if options is None:
            options = {}
        if "packing_time" in options:
            packing_time = options["packing_time"]
        if "section_width" in options:
            section_width = options["section_width"]
        if "naughty_chance" in options:
            naughty_chance = options["naughty_chance"]

        p = []  # passengers list
        if type_ == "random":  # random passengers distribution 
            for seat in range(self.m):
                if seat not in self.corridors:
                    for row in range(self.n):
                        p_ = Person(row, seat, {"packing_time": random.choice(packing_time)}, 
                                    self.corridors)

                        place_in_line = randrange(len(p) + 1)
                        if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                            p_.naughty = True
                            p.insert(place_in_line//2, p_)
                        else:
                            p.insert(place_in_line, p_)

        elif type_ == "seat":  # seat-based passengers distribution
            seatsFilled = self.corridors.copy()
            displacement = 1

            naughtyList = []

            while len(seatsFilled) < self.m:
                c_ = []
                for corridor in self.corridors:
                    if corridor - displacement >= 0 and corridor - displacement not in seatsFilled:
                        seatsFilled.append(corridor - displacement)

                        for row in range(self.n):
                            p_ = Person(row, corridor - displacement, {"packing_time": random.choice(packing_time)},
                                        self.corridors)
                            
                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append(p_)
                                # p.insert(-randrange((len(p) + 2)//2), p_)
                            else:
                                c_.insert(randrange(len(c_) + 1), p_)

                    if corridor + displacement < self.m and corridor + displacement not in seatsFilled:
                        seatsFilled.append(corridor + displacement)

                        for row in range(self.n):
                            p_ = Person(row, corridor + displacement,  {"packing_time": random.choice(packing_time)}, 
                                        self.corridors,)

                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append(p_)
                                # p.insert(-randrange((len(p) + 2)//2), p_)
                            else:
                                c_.insert(randrange(len(c_) + 1), p_)

                    # random.shuffle(c_)
                    p = c_ + p

                displacement += 1

            for i in naughtyList:
                p.insert(randrange((len(p) + 2)//4), i)

        elif type_ == "section":  # section-based passengers distribution
            def chunks(lst, n_):
                """Yield successive n-sized chunks from lst."""
                for i__ in range(0, len(lst), n_):
                    yield lst[i__:i__ + n_]

            sections = list(chunks(list(range(0, self.n)), section_width))
            sections.reverse()
            
            naughtyList = []

            for s in sections:
                sp = []  # section passengers
                for row in range(len(s)):
                    for seat in range(self.m):
                        if seat not in self.corridors:
                            p_ = Person(s[row], seat, {"packing_time": random.choice(packing_time)}, self.corridors)
                            
                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append(p_)
                                # p.insert(randrange((len(p) + 2)//2), p_)
                            else:
                                sp.insert(randrange(len(sp) + 1), p_)

                p.extend(sp)

            for i in naughtyList:
                p.insert(randrange((len(p) + 2)//4), i)

        self.passengers = p

    def checkIfPlaceEmpty(self, row, seat):
        if len(self.grid[seat][row]) == 0 or \
                (len(self.grid[seat][row]) == 1 and self.grid[seat][row][0].check_seated()) or \
                (len(self.grid[seat][row]) < 2 and seat not in self.corridors):  # swapping places not in corridors

            return True
        else:
            return False

    def checkPlaceStatus(self, row, seat):
        if len(self.grid[seat][row]) == 0:
            return "empty", None
        if len(self.grid[seat][row]) == 1:
            if self.grid[seat][row][0].check_seated():
                return "boarded", self.grid[seat][row][0]
            elif row == self.grid[seat][row][0].ticketRow and seat in self.corridors:
                return "packing", self.grid[seat][row][0]

        return "standing", self.grid[seat][row]

    def checkIfAllSeated(self):
        for seat in self.grid:
            for place in seat:
                if not place[0].check_seated():
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

        toRemove = []
        
        for p in self.passengers:  # trying to move every passenger
            p.boardingTime += 1
            if p.currentRow < 0:  # person not on plane yet
                for corridor in p.entranceCorridors:
                    if self.checkIfPlaceEmpty(0, corridor):  # entrance empty
                        self.movePerson(p, 0, corridor)
                        continue
                    else:  # entrance taken
                        p.idleTime += 1
                        continue

            if p.currentRow >= 0:  # person already on plane
                if p.currentRow == p.ticketRow:  # person in a correct row
                    if p.currentSeat == p.ticketSeat:  # person in a correct seat
                        toRemove.append(p)
                        continue

                    if p.ticketSeat < p.currentSeat:
                        toMoveY = p.currentSeat - 1
                    else:
                        toMoveY = p.currentSeat + 1

                    if p.currentSeat in self.corridors and p.seatingTime > 0:
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
            self.idleList.append(p_.idleTime)
            self.boardingTimeList.append(p_.boardingTime)
            
            # grid_[i_.currentRow][i_.currentSeat] = 0

        self.turn += 1  # increment number of turns

        return self.turn, self.boardingTimeList  # t_num, grid_, people_
