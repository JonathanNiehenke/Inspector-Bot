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
        self.vectorIters = (
            self.rowIter, self.colIter, self.bDiagIter, self.fDiagIter)

    def isPlayer(self, Index):
        return self.gameBoard[Index] == self.currentPlayer 

    def playersVector(self, Vector):
        return (self.isPlayer(Index) for Index in Vector)

    def rowIter(self, _, y):
        return (f"{x}, {y}" for x in range(3))

    def colIter(self, x, _):
        return (f"{x}, {y}" for y in range(3))

    def bDiagIter(self, x, y):
        return (f"{z}, {z}" for z in range(3)) if x == y else ()

    def fDiagIter(self, x, y):
        return ((f"{z}, {2 - z}" for z in range(3))
                if int(x) == 2 - int(y) else ())

    def isVectorWin(self, Vector):
        # Prevent returning True if empty as expected from diagonals
        return all(self.playersVector(Vector)) if Vector else False

    def isWin(self):
        x, y = self.recentMove[0], self.recentMove[-1]
        return any(self.isVectorWin(Iter(x, y)) for Iter in self.vectorIters)

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

    def countAlongVec(self, vec, Iter):
        return sum(self.Engine.playersVector(Iter(vec)))

    def getEmpty(self, vec, Iter):
        for Index in Iter(vec):
            if self.Engine.gameBoard[Index] == " ":
                return Index

    def getDefensiveMove(self):
        for vec in range(3):
            if self.countAlongVec(vec, self.Engine.rowIter) == 2:
                move = self.getEmpty(vec, self.Engine.rowIter)
                if move is not None: return move
            elif self.countAlongVec(vec, self.Engine.colIter) == 2:
                move = self.getEmpty(vec, self.Engine.colIter)
                if move is not None: return move
        if sum(self.Engine.playersVector(self.Engine.bDiagIter(None))) == 2:
            move = self.getEmpty(None, self.Engine.bDiagIter)
            if move is not None: return move
        elif sum(self.Engine.playersVector(self.Engine.fDiagIter(None))) == 2:
            move = self.getEmpty(None, self.Engine.fDiagIter)
            if move is not None: return move

    def getWinningMove(self):
        currentPlayer = self.Engine.currentPlayer
        self.Engine.currentPlayer = self.Engine.getNextPlayer()
        move = self.getDefensiveMove()
        self.Engine.currentPlayer = currentPlayer
        return move

    def fillGameBoard(self, Player):
        for Index in self.Engine.gameBoard:
            if self.Engine.gameBoard[Index] == " ":
                self.Engine.gameBoard[Index] = Player 

    def countRowWins(self, y, winCount):
        if (self.Engine.isVectorWin(self.Engine.rowIter(None, y))):
            for x in range(3):
                winCount[(x, y)] += 1

    def countColWins(self, x, winCount):
        if (self.Engine.isVectorWin(self.Engine.colIter(x, None))):
            for y in range(3):
                winCount[(x, y)] += 1

    def countBDiagWins(self, winCount):
        if (self.Engine.isVectorWin(self.Engine.bDiagIter(0, 0))):
            for z in range(3):
                winCount[(z, z)] += 1

    def countFDiagWins(self, winCount):
        if (self.Engine.isVectorWin(self.Engine.fDiagIter(2, 0))):
            for z in range(3):
                winCount[(z, 2 - z)] += 1

    def foreachVec(self, func, *args):
        for vec in range(3):
            func(vec, *args)

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
        backup = self.Engine.gameBoard.copy()  # Create backup
        self.fillGameBoard(Player)
        self.foreachVec(self.countRowWins, winCount)
        self.foreachVec(self.countColWins, winCount)
        self.countBDiagWins(winCount)
        self.countFDiagWins(winCount)
        self.Engine.gameBoard = backup  # Restore backup
        # self.draw(winCount.values())
        return winCount
        # self.draw(self.Engine.gameBoard.values())
        # self.draw(self.Backup.values())

    def makeMove(self):
        # self.draw(self.Engine.gameBoard.values())
        # print(self.sortCount(self.countWinPossibilities("O")))
        # print("Internal board")
        # self.draw(self.Engine.gameBoard.values())
        move = self.getWinningMove()
        # print(f"Win move {move}")
        move = self.getDefensiveMove() if move is None else move
        # print(f"Def move {move}")
        if move is None:
            for Index in self.sortCount(self.countWinPossibilities("X")):
                move = "{}, {}".format(*Index)
                if self.Engine.gameBoard.get(move, "") == " ": break
        self.Engine.makeMove(move)
        # print(move)
        return move

    def opponentMove(self, move):
        self.Engine.makeMove(move);
