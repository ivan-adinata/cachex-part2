from os import remove
import random
from itertools import permutations
from GreedyAgent.hex import Hex

class Player:
    FIRST_PLAYER = "Red"

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
        self.hexTaken = []
        self.possibleMoves = []

        for row in range(n):
            for column in range(n):
                # Last element represents eval function
                self.possibleMoves.append(Hex(row, column, None))
        if n % 2 != 0:
            # self.possibleMoves.remove((n // 2, n // 2))
            # self.possibleMoves.pop(((n // 2 - 1) * n) + (n // 2))
            self.possibleMoves.pop((n ** 2) // 2)

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
                if self.n % 2 != 0:
                    self.possibleMoves.append(Hex(self.n // 2, self.n // 2, None))
            else:
                if self.opponentMove.y == 0:
                    return ("STEAL",)
                else:
                    chosen = (start, 0)
        else:
            chosen = max(self.possibleMoves, key=lambda hex: hex.evalScore)
        return ("PLACE", chosen.x, chosen.y)
    
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
                self.steal(self.opponentMove)
            elif action[0] == 'PLACE':
                self.lastMove = (action[1], action[2])
                self.place(self.lastMove)
            self.numTurns += 1
        else:
            self.opponentMove = action
            if action[0] == "STEAL":
                self.remove(self.lastMove)
            elif action[0] == 'PLACE':
                self.opponentMove = (action[1], action[2])
                for hex in self.capture(self.opponentMove):
                    self.remove(hex)
        
        # Update evalScores in possibleMoves
        for hex in self.possibleMoves:
            self.evalFunction(hex)

    def place(self, coordinate):
        self.hexTaken.append(coordinate)
        # Remove hex in possibleMoves
        self.possibleMoves = [hex for hex in self.possibleMoves if (hex.x, hex.y) == coordinate]

    def steal(self, coordinate):
        new_coordinate = (coordinate[1], coordinate[0])
        self.lastMove = new_coordinate
        self.place(new_coordinate)

    def remove(self, coordinate):
        self.hexTaken.remove(coordinate)
        self.possibleMoves.append(Hex(coordinate[0], coordinate[1], None))

    def capture(self, coordinate):
        """
        Returns a list of hexes to be removed as a result of capturing
        """
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
                    if not (neighbourBDoubled in self.hexTaken or neighbourBDoubled in self.possibleMoves) and self.hexInBoard(neighbourBDoubled):
                        #print(f'REMOVE ({pos[0]}, {pos[1]}) and ({neighbourADoubled[0]}, {neighbourADoubled[1]}) from ({neighbourBDoubled[0]}, {neighbourBDoubled[1]})')
                        removeHex.add(pos)
                        removeHex.add(neighbourADoubled)
                if neighbourBDoubled in self.hexTaken:
                    captureHex = (axialCentre[0] + axialDif[0] + neighbourBDif[0], axialCentre[1] + axialDif[1] + neighbourBDif[1])
                    if not (captureHex in self.hexTaken or captureHex in self.possibleMoves) and self.hexInBoard(captureHex):
                        #print(f'REMOVE ({pos[0]}, {pos[1]}) and ({neighbourBDoubled[0]}, {neighbourBDoubled[1]}) from ({captureHex[0]}, {captureHex[1]})')
                        removeHex.add(pos)
                        removeHex.add(neighbourBDoubled)
        return removeHex

    def hexInBoard(self, hex):
        return (0 <= hex[0] < self.n and 0<= hex[1] < self.n)


    def updateEvalScore(self, hex):
        """
        Updates the evaluation score for a hex using weighted features
        """
        COL_WEIGHT = 0.33
        ROW_WEIGHT = 0.33
        CAPTURE_WEIGHT = 0.33
        return (COL_WEIGHT * self.heuristic1(hex)) + (ROW_WEIGHT * self.heuristic2(hex)) + \
            (CAPTURE_WEIGHT * self.captureHeuristic(hex))

    def heuristic1(self, hex):
        """
        Calculates the distance from a hex to the average position of tokens
        """
        total = 0
        if self.Player == Player.FIRST_PLAYER:
            for coordinate in self.hexTaken:
                total += coordinate[1]
            hex.evalScore = hex.y - (total / len(self.hexTaken))
        else:
            for coordinate in self.hexTaken:
                total += coordinate[0]
            hex.evalScore = hex.x - (total / len(self.hexTaken))

    def heuristic2(self, hex):
        """
        Calculates the value of placing a token in a row
        """
        tokens = 0
        if self.player == Player.FIRST_PLAYER:
            for coordinate in self.hexTaken:
                if coordinate[0] == hex.x:
                    tokens += 1
        else:
            for coordinate in self.hexTaken:
                if coordinate[1] == hex.y:
                    tokens += 1

        # Inverse relationship; the less tokens, the higher the value
        hex.evalScore = self.n / tokens

    def captureHeuristic(self, hex):
        """
        Calculates the number of enemy tokens that can be captured by placing a token
        """
        hex.evalScore = len(self.capture((hex.x, hex.y)))