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
        self.disembarkingTimeList = []

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

    
