from collections import OrderedDict
import os

def twoDimIter(width, height):
    for y in range(height):
        for x in range(width):
            yield (x, y)

class TicTacToeEngine:

    def __init__(self):
        self.currentMove = 0;
        self.recentMove = "0, 1";
        self.currentPlayer = "X";
        self.gameBoard = OrderedDict(
            (f"{x}, {y}", " ") for x, y in twoDimIter(3, 3))

    def isPlayerIndex(self, Index):
        return self.gameBoard[Index] == self.currentPlayer 

    def isRowWin(self, y):
        return all(self.isPlayerIndex(f"{x}, {y}") for x in range(3))

    def isColWin(self, x):
        return all(self.isPlayerIndex(f"{x}, {y}") for y in range(3))

    def isBackDiagWin(self, x, y):
        return (all(self.isPlayerIndex(f"{z}, {z}") for z in range(3))
                if x == y else False)

    def isFrontDiagWin(self, x, y):
        adjust = 2;  # The maximium of range(3) is 2
        return (all(self.isPlayerIndex(f"{z}, {adjust - z}") for z in range(3))
                if int(x) == adjust - int(y) else False)

    def isWin(self):
        x, y = self.recentMove[0], self.recentMove[-1]
        return (self.isRowWin(y) or self.isColWin(x) or
                self.isBackDiagWin(x, y) or self.isFrontDiagWin(x, y))

    def isEnd(self):
        return self.isWin() or self.currentMove == 9

    def makeMove(self, Index):
        if (self.gameBoard.get(Index, "") == " "):  # Is a valid move
            self.gameBoard[Index] = self.currentPlayer = self.getNextPlayer()
            self.currentMove += 1
            self.recentMove = Index
            return True
        return False

    def getPlayer(self):
        return self.currentPlayer

    def getNextPlayer(self):
        return "O" if self.currentMove % 2 else "X"
