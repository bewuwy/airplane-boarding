import random


class Passenger:
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
        self.barged = False
        
        self.idleTime = 0
        self.boardingTime = 0
        self.naughty = False

        self.entranceCorridors = []
        if self.ticketSeat > corridors[-1]:
            self.entranceCorridors.append(corridors[-1])
        elif self.ticketSeat < corridors[0]:
            self.entranceCorridors.append(corridors[0])
        else:
            min = 1000000000
            for e in range(len(corridors)):
                if abs(corridors[e] - self.ticketSeat) < min:
                    min = abs(corridors[e] - self.ticketSeat)
                    self.entranceCorridors=[corridors[e]]

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
