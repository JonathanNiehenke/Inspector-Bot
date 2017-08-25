from collections import OrderedDict

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


class TicTacToe_Intelligence:

    def __init__(self):
        self.Engine = TicTacToeEngine()

    def draw(self, values):
        print("""
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(*values))

    def fillGameBoard(self, Player):
        for Index in self.Engine.gameBoard:
            if self.Engine.gameBoard[Index] == " ":
                self.Engine.gameBoard[Index] = Player 

    def invertCount(self, countDict):
        invDict = {}
        for Index, Count in countDict.items():
            invDict.setdefault(Count, []).append(Index)
        return invDict

    def sortCount(self, countDict):
        nestedSort = sorted(self.invertCount(countDict).items(), reverse=True)
        return [v for _, l in nestedSort for v in l]

    def countWinPossibilities(self, Player):
        winCount = OrderedDict((Index, 0) for Index in twoDimIter(3, 3))
        self.Engine.currentPlayer = Player
        backup = self.Engine.gameBoard.copy()
        self.fillGameBoard(Player)
        for row in range(3):
            if (self.Engine.isRowWin(row)):
                for col in range(3):
                    winCount[(col, row)] += 1
        for col in range(3):
            if (self.Engine.isColWin(col)):
                for row in range(3):
                    winCount[(col, row)] += 1
        if (self.Engine.isBackDiagWin(0, 0)):
            for z in range(3):
                winCount[(z, z)] += 1
        if (self.Engine.isFrontDiagWin(2, 0)):
            for z in range(3):
                winCount[(z, 2 - z)] += 1
        self.Engine.gameBoard = backup
        # self.draw(winCount.values())
        return winCount
        # self.draw(self.Engine.gameBoard.values())
        # self.draw(self.Backup.values())

    def makeMove(self):
        # self.draw(self.Engine.gameBoard.values())
        # print(self.sortCount(self.countWinPossibilities("O")))
        # print("Internal board")
        # self.draw(self.Engine.gameBoard.values())
        for index in self.sortCount(self.countWinPossibilities("X")):
            move = "{}, {}".format(*index)
            if self.Engine.makeMove(move):
                break
        return move

    def opponentMove(self, move):
        self.Engine.makeMove(move);
