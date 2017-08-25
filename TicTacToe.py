from collections import OrderedDict
from functools import partial
import tkinter as tk
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


class ConsoleTicTacToe:

    def __init__(self):
        self.Engine = TicTacToeEngine()

    def draw(self):
        os.system("cls")
        print("""
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(*self.Engine.gameBoard.values()))

    def playGame(self):
        while not self.Engine.isEnd():
            self.draw()
            print(f"Player {self.Engine.getNextPlayer()} to move.")
            playerInput = input("Please enter the row, column coordinates ")
            while not self.Engine.makeMove(playerInput):
                playerInput = input("Please enter something like 1, 2");
        else:
            if self.Engine.isWin():
                print(f"Player {self.Engine.getPlayer()} Won!!!")
            else:
                print("Tie game")


class GuiTicTacToe:

    def __init__(self):
        self.Engine = TicTacToeEngine()
        self.Window = tk.Tk()
        self.msgText = tk.StringVar()
        self.buttons = self.createButtons()
        tk.Label(self.Window, textvar=self.msgText).grid(
            row=0, column=0, columnspan=3)

    def endGame(self):
        self.msgText.set(f"Player {self.Engine.getPlayer()} Won!!!"
                         if self.Engine.isWin() else "Tie game")
        for button in self.buttons.values():
            button.configure(state="disabled")

    def buttonPress(self, x, y):
        if self.Engine.makeMove(f"{x}, {y}"):
            self.buttons[(x, y)].configure(text=self.Engine.getPlayer())
            self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
            if (self.Engine.isEnd()):
                self.endGame()

    def createButtons(self):
        buttons = {}
        for x, y in twoDimIter(3, 3):
            thisButtonPress = partial(self.buttonPress, x, y)
            button = tk.Button(self.Window, text=" ", font=('Courier', 18),
                               command=thisButtonPress)
            button.grid(row=(x+1), column=y, padx=8, pady=8)
            buttons[(x, y)] = button
        return buttons

    def playGame(self):
        self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
        self.Window.mainloop()


def main():
    # ConsoleTicTacToe().playGame()
    GuiTicTacToe().playGame()

if __name__ == '__main__':
    main()
