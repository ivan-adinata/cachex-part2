import random

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
        self.turn = 0
        self.opponentMove = ()
        self.possibleMoves = []
        self.hexTaken = []
        self.state = []

        isOdd = (n % 2 != 0)
        for row in range(n):
            for column in range(n):
                if not (isOdd and (row == n//2) and (column == n//2)):
                    self.possibleMoves.append((row, column))

    def action(self):
        """
        Called at the beginning of your turn. Based on the current state
        of the game, select an action to play.
        """
        if self.turn == 0:
            if not (self.player == Player.FIRST_PLAYER):
                if random.randint(0, 1) == 0:
                    return ("STEAL",)
            chosen = random.choice(self.possibleMoves)
            return ("PLACE", chosen[0], chosen[1])
        else:
            chosen = random.choice(self.possibleMoves)
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

            if action[0] == 'PLACE':

            self.turn += 1
        else:
            self.opponentMove = action
            if action[0] == "STEAL":

            if action[0] == 'PLACE':


