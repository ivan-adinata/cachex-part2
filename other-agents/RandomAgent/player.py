import random
from itertools import permutations


class Player:
    FIRST_PLAYER = "red"

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
        self.numTurns = 0
        self.opponentMove = ()
        self.lastMove = ()
        self.opponentTaken = []
        self.hexTaken = []
        self.possibleMoves = []

        for row in range(n):
            for column in range(n):
                self.possibleMoves.append((row, column))
        if self.n % 2 != 0:
            self.possibleMoves.remove((n // 2, n // 2))

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        chosen = random.choice(self.possibleMoves)
        if self.numTurns == 0:
            if self.n % 2 != 0:
                self.possibleMoves.append((self.n // 2, self.n // 2))
            if self.player != Player.FIRST_PLAYER and random.randint(0, 1) == 0:
                return ("STEAL",)
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
                self.possibleMoves.append(self.opponentMove)
                self.opponentTaken.remove(self.opponentMove)
                invertedHex = self.invert(self.opponentMove)
                self.lastMove = invertedHex
                self.possibleMoves.remove(invertedHex)
                self.hexTaken.append(invertedHex)
            elif action[0] == 'PLACE':
                self.lastMove = (action[1], action[2])
                self.possibleMoves.remove(self.lastMove)
                self.hexTaken.append(self.lastMove)
                # Add capture hexes to possibleMoves
                print("PLACE CAPTURE FOR PLAYER")
                for hex in self.capture(self.lastMove, player):
                    print(f'HEX = ({hex[0]}, {hex[1]})')
                    self.opponentTaken.remove(hex)
                    self.possibleMoves.append(hex)
            self.numTurns += 1
        else:
            if action[0] == "STEAL":
                self.possibleMoves.append(self.lastMove)
                self.hexTaken.remove(self.lastMove)
                invertedHex = self.invert(self.lastMove)
                self.opponentMove = invertedHex
                self.possibleMoves.remove(invertedHex)
                self.opponentTaken.append(invertedHex)
            elif action[0] == 'PLACE':
                self.opponentMove = (action[1], action[2])
                self.possibleMoves.remove(self.opponentMove)
                self.opponentTaken.append(self.opponentMove)
                print("PLACE CAPTURE FOR OPPONENT")
                for hex in self.capture(self.opponentMove, player):
                    print(f'HEX = ({hex[0]}, {hex[1]})')
                    self.hexTaken.remove(hex)
                    self.possibleMoves.append(hex)

    def invert(self, coordinate):
        return (coordinate[1], coordinate[0])

    def capture(self, coordinate, player):
        """
        Returns a list of hexes to be removed as a result of capturing
        """
        removeHex = set()
        axialCentre = (coordinate[0], coordinate[1], -coordinate[0] - coordinate[1])
        for comb in permutations([-1, 0, 1], 2):
            pos = (coordinate[0] + comb[0], coordinate[1] + comb[1])

            if self.player == player:
                if pos in self.opponentTaken:
                    axialPos = (pos[0], pos[1], -pos[0] - pos[1])
                    axialDif = (
                        axialPos[0] - axialCentre[0], axialPos[1] - axialCentre[1], axialPos[2] - axialCentre[2])

                    neighbourADif = (axialDif[1], axialDif[2], axialDif[0])
                    neighbourA = (axialCentre[0] + neighbourADif[0], axialCentre[1] + neighbourADif[1],
                                  axialCentre[2] + neighbourADif[2])
                    neighbourADoubled = (neighbourA[0], neighbourA[1])

                    neighbourBDif = (
                        axialDif[0] + neighbourADif[0], axialDif[1] + neighbourADif[1], axialDif[2] + neighbourADif[2])
                    neighbourB = (axialCentre[0] + neighbourBDif[0], axialCentre[1] + neighbourBDif[1],
                                  axialCentre[2] + neighbourBDif[2])
                    neighbourBDoubled = (neighbourB[0], neighbourB[1])


                    if neighbourADoubled in self.opponentTaken:
                        if neighbourBDoubled in self.hexTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourADoubled)
                    if neighbourBDoubled in self.opponentTaken:
                        captureHex = (axialCentre[0] + axialDif[0] + neighbourBDif[0],
                                      axialCentre[1] + axialDif[1] + neighbourBDif[1])
                        if captureHex in self.hexTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourBDoubled)
            else:
                if pos in self.hexTaken:
                    axialPos = (pos[0], pos[1], -pos[0] - pos[1])
                    axialDif = (
                        axialPos[0] - axialCentre[0], axialPos[1] - axialCentre[1], axialPos[2] - axialCentre[2])

                    neighbourADif = (axialDif[1], axialDif[2], axialDif[0])
                    neighbourA = (axialCentre[0] + neighbourADif[0], axialCentre[1] + neighbourADif[1],
                                  axialCentre[2] + neighbourADif[2])
                    neighbourADoubled = (neighbourA[0], neighbourA[1])

                    neighbourBDif = (
                        axialDif[0] + neighbourADif[0], axialDif[1] + neighbourADif[1], axialDif[2] + neighbourADif[2])
                    neighbourB = (axialCentre[0] + neighbourBDif[0], axialCentre[1] + neighbourBDif[1],
                                  axialCentre[2] + neighbourBDif[2])
                    neighbourBDoubled = (neighbourB[0], neighbourB[1])

                    if neighbourADoubled in self.hexTaken:
                        if neighbourBDoubled in self.opponentTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourADoubled)
                    if neighbourBDoubled in self.hexTaken:
                        captureHex = (axialCentre[0] + axialDif[0] + neighbourBDif[0],
                                      axialCentre[1] + axialDif[1] + neighbourBDif[1])
                        if captureHex in self.opponentTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourBDoubled)
        return removeHex

    def hexInBoard(self, hex):
        return (0 <= hex[0] < self.n and 0<= hex[1] < self.n)

