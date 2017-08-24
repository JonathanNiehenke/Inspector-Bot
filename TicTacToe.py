from collections import OrderedDict
import os

class TicTacToeGame:

    def __init__(self):
        self.currentPlayer = "X";
        self.gameBoard = OrderedDict((f"{x}, {y}", " ") for y in range(3) for x in range(3))

    def draw(self):
        os.system("cls")
        print("""
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(*self.gameBoard.values()))

    def isGood(self, Index):
        cellValue = self.gameBoard.get(Index, False)
        return cellValue if cellValue and cellValue != " " else False

    def isRowWin(self, Index):
        y = Index[-1]
        return all(self.gameBoard[f"{x}, {y}"] == self.currentPlayer for x in range(3))

    def isColWin(self, Index):
        x = Index[0]
        return all(self.gameBoard[f"{x}, {y}"] == self.currentPlayer for y in range(3))

    def isBackDiagWin(self, Index):
        if Index[0] != Index[-1]:
            return False
        return all(self.gameBoard[f"{z}, {z}"] == self.currentPlayer for z in range(3))

    def isFrontDiagWin(self, Index):
        adjust = 2;
        if int(Index[0]) != adjust - int(Index[-1]):
            return False
        return all(self.gameBoard[f"{z}, {adjust - z}"] == self.currentPlayer for z in range(3))

    def isWin(self, Index):
        return self.isRowWin(Index) or self.isColWin(Index) or self.isBackDiagWin(Index) or self.isFrontDiagWin(Index)

    # def resetBoard():
        # currentMove = 0;
        # currentPlayer = "X";
        # msgLabelJN.Text = "Player " + currentPlayer + "'s turn";
        # for (boardIdx in self.gameBoard)
            # gameBoard[boardIdx] = ""

    def playGame(self):
        self.draw()
        for currentMove in range(9):
            print(f"Player {self.currentPlayer} to move.")
            playerInput = input("Please enter the row, column coordinates.")
            while self.isGood(playerInput):
                playerInput = input("Please enter an empty row, column coordinate");
            self.gameBoard[playerInput] = self.currentPlayer
            if self.isWin(playerInput):
                self.draw()
                print(f"Player {self.currentPlayer} Won!!!")
                break
            self.currentPlayer = "X" if currentMove % 2 else "O"
            print(f"Player {self.currentPlayer} to move.")
            self.draw()
        else:
            print("Tie game")

def main():
    TicTacToe = TicTacToeGame()
    TicTacToe.playGame()

if __name__ == '__main__':
    main()
