from collections import OrderedDict, deque

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

    def reset(self):
        for Index in self.gameBoard:
            self.gameBoard[Index] = " "
            self.currentMove = 0


class TicTacToe_Intelligence:

    def __init__(self):
        self.Engine = TicTacToeEngine()
        self.priorityMoves = deque()

    def draw(self, values):
        print("""
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(*values))

    def countAlongVec(self, Vector):
        return sum(self.Engine.playersVector(Vector))

    def getEmpty(self, Vector):
        for Index in Vector:
            if self.Engine.gameBoard[Index] == " ":
                return Index

    def getNextVecWin(self, Vector):
        repeatVector = tuple(Vector)
        if self.countAlongVec(repeatVector) == 2:
            return self.getEmpty(repeatVector)

    def getWinningMoves(self, move):
        x, y = move[0], move[-1]
        winAlongVecs = (self.getNextVecWin(Iter(x, y))
                        for Iter in self.Engine.vectorIters)
        return [move for move in winAlongVecs if move is not None]

    def fillGameBoard(self, Player):
        for Index in self.Engine.gameBoard:
            if self.Engine.gameBoard[Index] == " ":
                self.Engine.gameBoard[Index] = Player 

    def countVectorWins(self, Vector, winCount):
        repeatVector = tuple(Vector)
        if self.Engine.isVectorWin(repeatVector):
            for Index in repeatVector:
                winCount[Index] += 1

    def countBoardWins(self, winCount):
        for z in range(3):
            self.countVectorWins(self.Engine.rowIter(None, z), winCount)
            self.countVectorWins(self.Engine.colIter(z, None), winCount)
        self.countVectorWins(self.Engine.bDiagIter(0, 0), winCount)
        self.countVectorWins(self.Engine.fDiagIter(2, 0), winCount)

    def countWinPossibilities(self, Player):
        winCount = OrderedDict((f"{x}, {y}", 0) for x, y in twoDimIter(3, 3))
        self.Engine.currentPlayer = Player
        backup = (self.Engine.currentPlayer, self.Engine.gameBoard.copy())
        self.fillGameBoard(Player)
        self.countBoardWins(winCount)
        self.Engine.currentPlayer, self.Engine.gameBoard = backup
        # self.draw(winCount.values())
        return winCount

    def invertCount(self, countDict):
        invDict = {}
        for Index, Count in countDict.items():
            invDict.setdefault(Count, []).append(Index)
        return invDict

    def sortCount(self, countDict):
        nestedSort = sorted(self.invertCount(countDict).items(), reverse=True)
        return [v for _, l in nestedSort for v in l]

    def makeMove(self):
        # print(self.priorityMoves)
        while self.priorityMoves:
            move = self.priorityMoves.popleft()
            if self.Engine.gameBoard.get(move, "") == " ": break
        else:
            for move in self.sortCount(
                    self.countWinPossibilities(self.Engine.getNextPlayer())):
                if self.Engine.gameBoard.get(move, "") == " ": break
        self.Engine.makeMove(move)
        self.priorityMoves.extend(self.getWinningMoves(move))
        return move

    def opponentMove(self, move):
        self.Engine.makeMove(move);
        self.priorityMoves.extend(self.getWinningMoves(move))

    def reset(self):
        self.Engine.reset()
        self.priorityMoves.clear()
