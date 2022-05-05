import random
from itertools import permutations


class Player:
    FIRST_PLAYER = "red"
    possibleMoves = []

    def __init__(self, player, n):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "red" if your player will
        play as Red, or the string "blue" if your player will play
        as Blue.
        """
        self.player = player
        self.n = n
        self.numTurn = 0
        self.opponentMove = ()
        self.lastMove = ()
        self.hexTaken = []

        if not Player.possibleMoves:
            isOdd = (n % 2 != 0)
            for row in range(n):
                for column in range(n):
                    Player.possibleMoves.append((row, column))
            if isOdd:
                Player.possibleMoves.remove((n // 2, n // 2))

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        if self.numTurn == 0:
            chosen = random.choice(Player.possibleMoves)
            if (self.n % 2 != 0 and self.player == 'red'):
                Player.possibleMoves.append((self.n // 2, self.n // 2))
                #print('PossibleMoves are: ')
                #for i in Player.possibleMoves:
                    #print(f'({i[0]}, {i[1]})')
            if self.player != "red":
                if random.randint(0, 1) == 0:
                    return ("STEAL",)
            return ("PLACE", chosen[0], chosen[1])
        else:
            chosen = random.choice(Player.possibleMoves)
            return ("PLACE", chosen[0], chosen[1])

    def turn(self, player, action):
        """
        Called at the end of each player's turn to inform this player of
        their chosen action. Update your internal representation of the
        game state based on this. The parameter action is the chosen
        action itself.

        Note: At the end of your player's turn, the action parameter is
        the same as what your player returned from the action method
        above. However, the referee has validated it at this point.
        """

        if self.player == player:
            if action[0] == 'STEAL':
                self.steel(self.opponentMove)
            elif action[0] == 'PLACE':
                self.lastMove = (action[1], action[2])
                self.place(self.lastMove)
            self.numTurn += 1
        else:
            self.opponentMove = action
            if action[0] == "STEAL":
                self.remove(self.lastMove)
            elif action[0] == 'PLACE':
                self.opponentMove = (action[1], action[2])
                self.capture(self.opponentMove)

        #print("HEXTAKEN:")
        #for hex in self.hexTaken:
            #print(f'({hex[0]}, {hex[1]}')
        #print("HEXENDED")
    def steel(self, coordinate):
        new_coordinate = (coordinate[1], coordinate[0])
        self.lastMove = new_coordinate
        self.place(new_coordinate)

    def place(self, coordinate):
        #print("PLACEEEE")
        self.hexTaken.append(coordinate)
        if coordinate in Player.possibleMoves:
            Player.possibleMoves.remove(coordinate)

    def remove(self, coordinate):
        self.hexTaken.remove(coordinate)
        Player.possibleMoves.append(coordinate)

    def capture(self, coordinate):
        removeHex = set()
        axialCentre = (coordinate[0], coordinate[1], -coordinate[0] - coordinate[1])

        for comb in permutations([-1, 0, 1], 2):
            pos = (coordinate[0] + comb[0], coordinate[1] + comb[1])
            if pos in self.hexTaken:
                axialPos = (pos[0], pos[1], -pos[0] - pos[1])
                axialDif = (axialPos[0] - axialCentre[0], axialPos[1] - axialCentre[1], axialPos[2] - axialCentre[2])

                neighbourADif = (axialDif[1], axialDif[2], axialDif[0])
                neighbourA = (axialCentre[0] + neighbourADif[0], axialCentre[1] + neighbourADif[1], axialCentre[2] + neighbourADif[2])
                neighbourADoubled = (neighbourA[0], neighbourA[1])

                neighbourBDif = (axialDif[0] + neighbourADif[0], axialDif[1] + neighbourADif[1], axialDif[2] + neighbourADif[2])
                neighbourB = (axialCentre[0] + neighbourBDif[0], axialCentre[1] + neighbourBDif[1], axialCentre[2] + neighbourBDif[2])
                neighbourBDoubled = (neighbourB[0], neighbourB[1])

                if neighbourADoubled in self.hexTaken:
                    if not (neighbourBDoubled in self.hexTaken or neighbourBDoubled in Player.possibleMoves) and self.hexInBoard(neighbourBDoubled):
                        #print(f'REMOVE ({pos[0]}, {pos[1]}) and ({neighbourADoubled[0]}, {neighbourADoubled[1]}) from ({neighbourBDoubled[0]}, {neighbourBDoubled[1]})')
                        removeHex.add(pos)
                        removeHex.add(neighbourADoubled)
                if neighbourBDoubled in self.hexTaken:
                    captureHex = (axialCentre[0] + axialDif[0] + neighbourBDif[0], axialCentre[1] + axialDif[1] + neighbourBDif[1])
                    if not (captureHex in self.hexTaken or captureHex in Player.possibleMoves) and self.hexInBoard(captureHex):
                        #print(f'REMOVE ({pos[0]}, {pos[1]}) and ({neighbourBDoubled[0]}, {neighbourBDoubled[1]}) from ({captureHex[0]}, {captureHex[1]})')
                        removeHex.add(pos)
                        removeHex.add(neighbourBDoubled)
        for hex in removeHex:
            self.remove(hex)
            #print(f"REMOVEEEE: {hex[0]} {hex[1]}")

    def hexInBoard(self, hex):
        return (0 <= hex[0] < self.n and 0<= hex[1] < self.n)