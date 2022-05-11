from math import inf
import random
from itertools import permutations
from statistics import stdev


class Player:
    FIRST_PLAYER = 'red'
    SECOND_PLAYER = 'blue'
    CUTOFF_DEPTH = 2

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

        for row in range(n):
            for column in range(n):
                # Value represents eval function
                self.possibleMoves[(row, column)] = 0

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """

        if self.numTurns == 0:
            # Choose random position along start edge
            start = random.randint(0, self.n - 1)
            if self.player == Player.FIRST_PLAYER:
                chosen = (0, start)
            else:
                if self.opponentMove[1] == 0:
                    return ("STEAL",)
                else:
                    chosen = (start, 0)
        else:
            chosen = self.minimaxDecision()
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
                self.possibleMoves[self.opponentMove] = 0
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
                for hex in self.capture(self.lastMove, player, self.hexTaken, self.opponentTaken):
                    self.opponentTaken.remove(hex)
                    self.possibleMoves[hex] = 0
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
                for hex in self.capture(self.opponentMove, player, self.hexTaken, self.opponentTaken):
                    self.hexTaken.remove(hex)
                    self.possibleMoves[hex] = 0

    def minimaxDecision(self):
        """
        Returns the best hex to place based on Minimax
        """

        # Update evalScores in possibleMoves
        for hex in self.possibleMoves:
            # Copy the current state
            # newState = [hexTaken, opponentTaken, possibleMoves]
            state = [self.hexTaken, self.opponentTaken, self.possibleMoves]
            # State is represented as hexTaken and opponentTaken
            self.possibleMoves[hex] = self.minimaxValue(self.applyHex(state, hex, True), Player.CUTOFF_DEPTH, True,
                                                        -inf, inf)
        return max(self.possibleMoves, key=self.possibleMoves.get)

    def applyHex(self, state, hex, isMax):
        """
        Returns a state represented by copies of hexTaken, opponentTaken and possibleMoves
        """
        newState = [state[0].copy(), state[1].copy(), state[2].copy()]

        # Add changes to the state
        if self.player == Player.FIRST_PLAYER:
            player = Player.FIRST_PLAYER if isMax else Player.SECOND_PLAYER
        else:
            player = Player.SECOND_PLAYER if isMax else Player.FIRST_PLAYER

        if isMax:
            newState[0].append(hex)
            # Add capture hexes to possibleMoves
            for coordinates in self.capture(hex, player, newState[0], newState[1]):
                newState[1].remove(coordinates)
                newState[2][coordinates] = 0
        else:
            newState[1].append(hex)
            for coordinates in self.capture(hex, player, newState[0], newState[1]):
                newState[0].remove(coordinates)
                newState[2][coordinates] = 0
        newState[2].pop(hex)

        return newState

    def minimaxValue(self, state, cutoff, isMax, alpha, beta):
        if cutoff == 0:
            return self.evalFunction(state[0], state[1])
        if isMax:
            best = -inf
            if None not in state[2].values():
                state[2] = sorted(state[2].items(), key=lambda x: x[1], reverse=True)
            for hex in state[2]:
                newState = self.applyHex(state, hex, isMax)
                best = max(best, self.minimaxValue(newState, cutoff - 1, not isMax, alpha, beta))
                alpha = max(alpha, best)

                if beta <= alpha:
                    break

            return best
        else:
            best = inf
            for hex in state[2]:
                newState = self.applyHex(state, hex, isMax)
                best = min(best, self.minimaxValue(newState, cutoff - 1, not isMax, alpha, beta))
                beta = min(beta, best)

                if beta <= alpha:
                    break
            return best

    def invert(self, coordinate):
        return (coordinate[1], coordinate[0])

    def capture(self, coordinate, player, hexTaken, opponentTaken):
        """
        Returns a list of hexes to be removed as a result of capturing
        """
        removeHex = set()
        axialCentre = (coordinate[0] + 0, coordinate[1] + 0, -coordinate[0] - coordinate[1] + 0)
        for comb in permutations([-1, 0, 1], 2):
            pos = (coordinate[0] + comb[0], coordinate[1] + comb[1])

            if self.player == player:
                if pos in opponentTaken:
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

                    if neighbourADoubled in opponentTaken:
                        if neighbourBDoubled in hexTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourADoubled)
                    if neighbourBDoubled in opponentTaken:
                        captureHex = (axialCentre[0] + axialDif[0] + neighbourBDif[0],
                                      axialCentre[1] + axialDif[1] + neighbourBDif[1])
                        if captureHex in hexTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourBDoubled)
            else:
                if pos in hexTaken:
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

                    if neighbourADoubled in hexTaken:
                        if neighbourBDoubled in opponentTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourADoubled)
                    if neighbourBDoubled in hexTaken:
                        captureHex = (axialCentre[0] + axialDif[0] + neighbourBDif[0],
                                      axialCentre[1] + axialDif[1] + neighbourBDif[1])
                        if captureHex in opponentTaken:
                            removeHex.add(pos)
                            removeHex.add(neighbourBDoubled)
        return removeHex

    def hexInBoard(self, hex):
        return (0 <= hex[0] < self.n and 0 <= hex[1] < self.n)

    def inOpponentHex(self, hex):
        return not (hex in self.hexTaken) or not (hex in self.possibleMoves) and self.hexInBoard(hex)

    def evalFunction(self, hexTaken, opponentTaken):
        """
        Updates the evaluation score for a hex using weighted features
        """
        COL_WEIGHT = 0.2
        ROW_WEIGHT = 0.2
        CAPTURE_WEIGHT = 0.2
        PLACED_WEIGHT = 0.2
        BLOCKING_WEIGHT = 0.2
        return (COL_WEIGHT * self.heuristic1(hexTaken)) + (ROW_WEIGHT * self.heuristic2(hexTaken)) + \
               (CAPTURE_WEIGHT * self.captureHeuristic(opponentTaken)) + (BLOCKING_WEIGHT * self.blockingEvaluation(hexTaken,opponentTaken)) + (PLACED_WEIGHT * self.placedEvaluation(hexTaken))

    def heuristic1(self, hexTaken):
        """
        Calculates the standard deviation of hexes taken
        """
        if len(hexTaken) < 2:
            return 0

        coordinates = []
        if self.player == Player.FIRST_PLAYER:
            for coordinate in hexTaken:
                coordinates.append(coordinate[1])
        else:
            for coordinate in hexTaken:
                coordinates.append(coordinate[0])
        return 1 / (stdev(coordinates) + 1)

    def heuristic2(self, hexTaken):
        """
        Calculates the value of placing a token in a row
        """
        if len(hexTaken) < 2:
            return 0

        freq = []
        for i in range(self.n):
            freq.append(0)
        if self.player == Player.FIRST_PLAYER:
            for coordinate in hexTaken:
                freq[coordinate[0]] += 1
        else:
            for coordinate in hexTaken:
                freq[coordinate[1]] += 1
        return stdev(freq)

    def captureHeuristic(self, opponentTaken):
        """
        Calculates the number of enemy tokens in the board
        """
        return 1 / len(opponentTaken)

    def placedEvaluation(self, hexTaken):
        """
        Calculates the number of player's tokens in the board
        """
        return len(hexTaken)

    def blockingEvaluation(self, hexTaken, opponentTaken):
        if len(opponentTaken) == 0:
            return 0

        teamCount = 0
        freqTable = {}
        for i in range(self.n):
            freqTable[i] = 0

        if self.player == Player.FIRST_PLAYER:
            for hex in opponentTaken:
                freqTable[hex[0]] += 1
            mostFreq = max(freqTable, key=freqTable.get)
            for hex in hexTaken:
                if hex[0] == mostFreq:
                    teamCount += 1
        else:
            for hex in opponentTaken:
                freqTable[hex[1]] += 1
            mostFreq = max(freqTable, key=freqTable.get)
            for hex in hexTaken:
                if hex[1] == mostFreq:
                    teamCount += 1
        return teamCount / freqTable[mostFreq]