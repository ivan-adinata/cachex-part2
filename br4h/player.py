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
        self.possibleMoves = {}

        # Build possibleMoves dictionary
        for row in range(n):
            for column in range(n):
                # Key rerpresents coordinates, Value represents eval function
                self.possibleMoves[(row, column)] = None

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        if self.numTurns == 0:
            # Choose random coordinate along middle hexes
            start = random.choice([i for i in range(self.n - 1) if i != self.n // 2])
            if self.player == Player.FIRST_PLAYER:
                chosen = (self.n // 2, start)
            else:
                # Steal if the opponent places on one of our middle hexes
                if self.opponentMove[1] == self.n // 2:
                    return ("STEAL",)
                else:
                    chosen = (start, self.n // 2)
        else:
            # Choose hex with highest evaluation function
            chosen = max(self.possibleMoves, key=self.possibleMoves.get)
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

        # Update variables based on action
        if self.player == player:
            if action[0] == 'STEAL':
                self.possibleMoves[self.opponentMove] = None
                self.opponentTaken.remove(self.opponentMove)
                invertedHex = self.invert(self.opponentMove)
                self.lastMove = invertedHex
                self.possibleMoves.pop(invertedHex)
                self.hexTaken.append(invertedHex)
            elif action[0] == 'PLACE':
                self.lastMove = (action[1], action[2])
                self.possibleMoves.pop(self.lastMove)
                self.hexTaken.append(self.lastMove)
                # Add capture hexes to possibleMoves
                for hex in self.capture(self.lastMove, player):
                    self.opponentTaken.remove(hex)
                    self.possibleMoves[hex] = None
            self.numTurns += 1
        else:
            if action[0] == "STEAL":
                self.possibleMoves[self.lastMove] = None
                self.hexTaken.remove(self.lastMove)
                invertedHex = self.invert(self.lastMove)
                self.opponentMove = invertedHex
                self.possibleMoves.pop(invertedHex)
                self.opponentTaken.append(invertedHex)
            elif action[0] == 'PLACE':
                self.opponentMove = (action[1], action[2])
                self.possibleMoves.pop(self.opponentMove)
                self.opponentTaken.append(self.opponentMove)
                for hex in self.capture(self.opponentMove, player):
                    self.hexTaken.remove(hex)
                    self.possibleMoves[hex] = None

        # Update evalScores in possibleMoves
        for hex in self.possibleMoves.keys():
            self.possibleMoves[hex] = self.evalFunction(hex, player)

    def invert(self, coordinate):
        """
        Finds the inverse hex across the main line of symmetry
        """
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
        """
        Checks if given hex is in the board
        """
        return (0 <= hex[0] < self.n and 0 <= hex[1] < self.n)

    def inOpponentHex(self, hex):
        """
        Checks if given hex is taken by opponent
        """
        return not (hex in self.hexTaken) or not (hex in self.possibleMoves) and self.hexInBoard(hex)

    def evalFunction(self, hex, player):
        """
        Updates the evaluation score for a hex using weighted features
        """
        # Weights add up to 1
        DISTANCE_WEIGHT = 0.17
        PATH_WEIGHT = 0.17
        CAPTURE_WEIGHT = 0.5
        BLOCKING_WEIGHT = 0.17
        
        return (DISTANCE_WEIGHT * (1 / (self.distanceHeuristic(hex) + 1))) + \
                (PATH_WEIGHT * self.pathHeuristic(hex)) + \
                (CAPTURE_WEIGHT * self.captureHeuristic(hex, player)) + \
                (BLOCKING_WEIGHT * self.blockingHeuristic(hex))

    def distanceHeuristic(self, hex):
        """
        Calculates the distance from a hex to the average column position of tokens
        """
        if len(self.hexTaken) == 0:
            return 0

        total = 0
        if self.player == Player.FIRST_PLAYER:
            for coordinate in self.hexTaken:
                total += coordinate[1]
            return abs(hex[1] - (total / len(self.hexTaken)))
        else:
            for coordinate in self.hexTaken:
                total += coordinate[0]
            return abs(hex[0] - (total / len(self.hexTaken)))

    def pathHeuristic(self, hex):
        """
        Calculates the value of placing a token in a row
        """
        tokens = 0
        if self.player == Player.FIRST_PLAYER:
            for coordinate in self.hexTaken:
                if coordinate[0] == hex[0]:
                    tokens += 1
        else:
            for coordinate in self.hexTaken:
                if coordinate[1] == hex[1]:
                    tokens += 1

        # Inverse relationship; the less tokens, the higher the value
        return self.n / (tokens + 1)

    def captureHeuristic(self, hex, player):
        """
        Calculates the number of enemy tokens that can be captured by placing a token
        """
        return len(self.capture(hex, player))

    def blockingHeuristic(self, hex):
        """
        Finds the relative row distance of the hex to all enemy hexes and the number of
        enemy tokens in the most frequent row
        """
        freq = 0
        total_distance = 0
        if self.player == Player.FIRST_PLAYER:
            for opponent in self.opponentTaken:
                distance = hex[0] - opponent[0]
                total_distance += abs(distance)
                if hex[0] == opponent[0]:
                    freq += 1
        else:
            for opponent in self.opponentTaken:
                distance = hex[1] - opponent[1]
                total_distance += abs(distance)
                if hex[1] == opponent[1]:
                    freq += 1

        return freq / (total_distance + 1)