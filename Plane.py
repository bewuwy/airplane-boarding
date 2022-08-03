from Passenger import Passenger

import random


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
        reverse = False

        if options is None:
            options = {}
        if "packing_time" in options:
            packing_time = options["packing_time"]
        if "section_width" in options:
            section_width = options["section_width"]
        if "naughty_chance" in options:
            naughty_chance = options["naughty_chance"]
        if "reverse" in options:
            reverse = bool(options["reverse"])

        p = []  # passengers list
        naughtyList = []  # line cutters list
        
        if type_ == "random":  # random passengers distribution 
            for seat in range(self.m):
                if seat not in self.corridors:
                    for row in range(self.n):
                        p_ = Passenger(row, seat, {"packing_time": random.choice(packing_time)}, 
                                    self.corridors)

                        place_in_line = random.randrange(len(p) + 1)
                        if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                            p_.naughty = True
                            naughtyList.append([p_, place_in_line//2])
                        else:
                            p.insert(place_in_line, p_)

        elif type_ == "seat":  # seat-based passengers distribution
            seatsFilled = self.corridors.copy()
            displacement = 1

            while len(seatsFilled) < self.m:
                c_ = []
                for corridor in self.corridors:
                    if corridor - displacement >= 0 and corridor - displacement not in seatsFilled:
                        seatsFilled.append(corridor - displacement)

                        for row in range(self.n):
                            p_ = Passenger(row, corridor - displacement, {"packing_time": random.choice(packing_time)},
                                        self.corridors)
                            
                            place_in_line = random.randrange(len(c_) + 1)
                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append([p_, place_in_line//2])
                            else:
                                c_.insert(place_in_line, p_)

                    if corridor + displacement < self.m and corridor + displacement not in seatsFilled:
                        seatsFilled.append(corridor + displacement)

                        for row in range(self.n):
                            p_ = Passenger(row, corridor + displacement,  {"packing_time": random.choice(packing_time)}, 
                                        self.corridors,)

                            place_in_line = random.randrange(len(c_) + 1)
                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append([p_, place_in_line//2])
                            else:
                                c_.insert(place_in_line, p_)

                    p = c_ + p

                displacement += 1

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
                        if seat not in self.corridors:
                            p_ = Passenger(s[row], seat, {"packing_time": random.choice(packing_time)}, self.corridors)
                            
                            place_in_line = random.randrange(len(sp) + 1)
                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append([p_, place_in_line//2])
                            else:
                                sp.insert(place_in_line, p_)

                p.extend(sp)
                
        # this is a weird idea from class
        # # custom section passengers distribution
        # elif type_ == "custom-section":
        #     def chunks(lst, n_):
        #         """Yield successive n-sized chunks from lst."""
        #         for i__ in range(0, len(lst), n_):
        #             yield lst[i__:i__ + n_]

        #     sections = list(chunks(list(range(0, self.n)), 11))
        #     sections.reverse()
            
        #     print(sections)
            
        #     order = [
        #         [1, 1, 2],
        #         [1, 2, 3],
        #         [2, 3, 3],
        #         [],
        #         [2, 3, 3],
        #         [1, 2, 3],
        #         [1, 1, 2]
        #     ]
            
        #     n = 1
        #     for seat in range(self.m):
        #         for row in range(self.n):
        #             if row in self.corridors:
        #                 continue
                    
        #             row_s = None
                    
        #             ti = 0
        #             while not row_s:
        #                 if row in sections[ti]:
        #                     row_s = ti
        #                     break
        #                 else:
        #                     ti += 1
                    
        #             section_order = order[seat][row_s]
                    
        #             if section_order != n:
        #                 continue
            

        if reverse:
            p.reverse()
            
        for i in naughtyList:
            p.insert(i[1], i[0])

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
            elif row == self.grid[seat][row][0].ticketRow and seat in self.corridors and \
                self.grid[seat][row][0].toWait < 1:
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
        
        passenger.barged = False

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
                        
                        if (len(self.grid[toMoveY][p.currentRow]) > 0 or \
                           len(self.grid[p.currentSeat][p.currentRow]) > 1) and not p.barged:
                            p.toWait = barging_time
                            p.barged = True
                        
                        self.movePerson(p, p.currentRow, toMoveY)
                        
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
