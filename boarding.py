from Passenger import Passenger
import random


def next_boarding_turn(plane, options=None):
        barging_time = 1
        if options is None:
            options = {}
        if "barging_time" in options:
            barging_time = options["barging_time"]

        toRemove = []
        
        for p in plane.passengers:  # trying to move every passenger
            p.boardingTime += 1
            if p.currentRow < 0:  # person not on plane yet
                if plane.checkIfPlaceEmpty(0, p.entranceCorridor):  # entrance empty
                    plane.movePerson(p, 0, p.entranceCorridor)
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

                    if p.currentSeat in plane.corridors and p.seatingTime > 0:
                        # if person in the corridor and still has something to pack
                        p.seatingTime -= 1
                        continue
                    elif plane.checkIfPlaceEmpty(p.currentRow, toMoveY):  # if seat left/right of current seat empty
                        
                        if (len(plane.grid[toMoveY][p.currentRow]) > 0 or \
                           len(plane.grid[p.currentSeat][p.currentRow]) > 1) and not p.barged:
                            p.toWait = barging_time
                            p.barged = True
                        
                        plane.movePerson(p, p.currentRow, toMoveY)
                        
                        continue
                    else:  # if seat left/right of current seat taken
                        p.idleTime += 1

                elif p.currentRow != p.ticketRow:  # person not in a correct row
                    if plane.checkIfPlaceEmpty(p.currentRow + 1, p.currentSeat):  # if next place in the corridor empty
                        plane.movePerson(p, p.currentRow + 1, p.currentSeat)
                        continue
                    else:  # standing idle
                        p.idleTime += 1

        for p_ in toRemove:
            plane.passengers.remove(p_)
            plane.idleList.append(p_.idleTime)
            plane.boardingTimeList.append(p_.boardingTime)
            
            # grid_[i_.currentRow][i_.currentSeat] = 0

        plane.turn += 1  # increment number of turns

        return plane.turn, plane.boardingTimeList  # t_num, grid_, people_


def createPassengers(plane, type_, options=None):
        # default options
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
            for seat in range(plane.m):
                if seat not in plane.corridors:
                    for row in range(len(plane.grid[seat])):
                        p_ = Passenger(row, seat, {"packing_time": random.choice(packing_time)}, 
                                    plane.corridors)

                        place_in_line = random.randrange(len(p) + 1)
                        if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                            p_.naughty = True
                            naughtyList.append([p_, place_in_line//2])
                        else:
                            p.insert(place_in_line, p_)

        elif type_ == "seat":  # seat-based passengers distribution
            seatsFilled = plane.corridors.copy()
            displacement = 1

            while len(seatsFilled) < plane.m:
                c_ = []
                for corridor in plane.corridors:
                    if corridor - displacement >= 0 and corridor - displacement not in seatsFilled:
                        seatsFilled.append(corridor - displacement)

                        for row in range(len(plane.grid[corridor - displacement])):
                            p_ = Passenger(row, corridor - displacement, {"packing_time": random.choice(packing_time)},
                                        plane.corridors)
                            
                            place_in_line = random.randrange(len(c_) + 1)
                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append([p_, place_in_line//2])
                            else:
                                c_.insert(place_in_line, p_)

                    if corridor + displacement < plane.m and corridor + displacement not in seatsFilled:
                        seatsFilled.append(corridor + displacement)

                        for row in range(len(plane.grid[corridor + displacement])):
                            p_ = Passenger(row, corridor + displacement,  {"packing_time": random.choice(packing_time)}, 
                                        plane.corridors,)

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
                for i__ in range(0, len(lst), n_):
                    yield lst[i__:i__ + n_]

            sections = list(chunks(list(range(0, plane.n)), section_width))
            sections.reverse()

            for s in sections:
                sp = []  # section passengers
                for row in range(len(s)):
                    for seat in range(plane.m):
                        if seat not in plane.corridors:
                            if s[row] >= len(plane.grid[seat]):
                                # if the place is out of bounds, then it's not a valid place
                                continue
                            
                            p_ = Passenger(s[row], seat, {"packing_time": random.choice(packing_time)}, plane.corridors)
                            
                            place_in_line = random.randrange(len(sp) + 1)
                            if random.random() < naughty_chance:  # if a person is naughty, then they cut half of their line
                                p_.naughty = True
                                naughtyList.append([p_, place_in_line//2])
                            else:
                                sp.insert(place_in_line, p_)

                p.extend(sp)
                
        elif type_ == "alternating":
            corridors = plane.corridors.copy()
            corridors.insert(0, -1)
            corridors.append(plane.m)
            for corridor_index in range(len(corridors)-1):
                sc = []
                for row in range(plane.n)[::2]:
                    p_= []
                    for seat in range(0, corridors[corridor_index + 1] - corridors[corridor_index] - 1):
                        if row < len(plane.grid[seat+corridors[corridor_index]+1]):
                            p_.append(Passenger(row, seat+corridors[corridor_index]+1, {"packing_time": random.choice(packing_time)}, plane.corridors))
                    sc.extend(p_)
                random.shuffle(sc)
                p.extend(sc)
                sc = []
                for row in range(plane.n)[1::2]:
                    p_= []
                    for seat in range(0, corridors[corridor_index + 1] - corridors[corridor_index] - 1):
                        if row < len(plane.grid[seat+corridors[corridor_index]+1]):
                            p_.append(Passenger(row, seat+corridors[corridor_index]+1, {"packing_time": random.choice(packing_time)}, plane.corridors))
                    sc.extend(p_)
                random.shuffle(sc)
                p.extend(sc)

        elif type_ == "alternating-wma":
            corridors = plane.corridors.copy()
            corridors.insert(0, -corridors[0]-2)
            corridors.append(2*plane.m - corridors[-1]-1)
            for corridor_index in range(1,len(corridors)-1):
                sc = []
                j = []
                #for seat in plane.grid[corridors[corridor_index]+1:corridors[corridor_index+1]-1]:
                for i in range(int((corridors[corridor_index-1]+corridors[corridor_index])/2)+1,corridors[corridor_index]):
                    seat = plane.grid[i]
                    for row in range(len(seat))[::2]:
                        p_ = Passenger(row, i, {"packing_time": random.choice(packing_time)}, plane.corridors)
                        sc.append(p_)
                    random.shuffle(sc)
                    j.append(sc)
                    sc = []
                    for row in range(len(seat))[1::2]:
                        p_ = Passenger(row, i, {"packing_time": random.choice(packing_time)}, plane.corridors)
                        sc.append(p_)
                    random.shuffle(sc)
                    j.append(sc)
                    sc = []
                for i in range(int((corridors[corridor_index+1]+corridors[corridor_index])/2),corridors[corridor_index],-1):
                    seat = plane.grid[i]
                    for row in range (len(seat))[::2]:
                        p_ = Passenger(row, i, {"packing_time": random.choice(packing_time)}, plane.corridors)
                        sc.append(p_)
                    random.shuffle(sc)
                    j.append(sc)
                    sc = []
                    for row in range(len(seat))[1::2]:
                        p_ = Passenger(row, i, {"packing_time": random.choice(packing_time)}, plane.corridors)
                        sc.append(p_)
                    random.shuffle(sc)
                    j.append(sc)
                    sc = []
                for g in range(int(len(j)/2)):
                    j[g].extend(j[int(len(j)/2)+g])
                    random.shuffle(j[g])
                    p.extend(j[g])

        # this is a weird idea from class
        # # custom section passengers distribution
        # elif type_ == "custom-section":
        #     def chunks(lst, n_):
        #         """Yield successive n-sized chunks from lst."""
        #         for i__ in range(0, len(lst), n_):
        #             yield lst[i__:i__ + n_]

        #     sections = list(chunks(list(range(0, plane.n)), 11))
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
        #     for seat in range(plane.m):
        #         for row in range(plane.n):
        #             if row in plane.corridors:
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

        plane.passengers = p
