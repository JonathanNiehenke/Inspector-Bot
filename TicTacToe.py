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
        self.recentMove = "1, 1";
        self.currentPlayer = "X";
        self.gameBoard = OrderedDict(
            (f"{x}, {y}", " ") for x, y in twoDimIter(3, 3))

    def isGood(self, Index):
        return self.gameBoard.get(Index, "") == " "

    def isPlayerIndex(self, Index):
        return self.gameBoard[Index] == self.currentPlayer 

    def isRowWin(self, Index):
        y = Index[-1]
        return all(self.isPlayerIndex(f"{x}, {y}") for x in range(3))

    def isColWin(self, Index):
        x = Index[0]
        return all(self.isPlayerIndex(f"{x}, {y}") for y in range(3))

    def isBackDiagWin(self, Index):
        if Index[0] != Index[-1]:
            return False
        return all(self.isPlayerIndex(f"{z}, {z}") for z in range(3))

    def isFrontDiagWin(self, Index):
        adjust = 2;
        if int(Index[0]) != adjust - int(Index[-1]):
            return False
        return all(self.isPlayerIndex(f"{z}, {adjust - z}") for z in range(3))

    def isWin(self):
        Idx = self.recentMove
        return (self.isRowWin(Idx) or self.isColWin(Idx) or
                self.isBackDiagWin(Idx) or self.isFrontDiagWin(Idx))

    def isEnd(self):
        return self.isWin() or self.currentMove == 9

    def makeMove(self, Index):
        if (self.isGood(Index)):
            self.currentPlayer = self.getNextPlayer()
            self.gameBoard[Index] = self.currentPlayer
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
        self.draw()
        while not self.Engine.isEnd():
            print(f"Player {self.Engine.getNextPlayer()} to move.")
            playerInput = input("Please enter the row, column coordinates.")
            while not self.Engine.makeMove(playerInput):
                playerInput = input("Please enter an empty row, column coordinate");
            self.draw()
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

    def disableButtons(self):
        for button in self.buttons.values():
            button.configure(state="disabled")

    def endGame(self):
        self.disableButtons()
        self.msgText.set(f"Player {self.Engine.getPlayer()} Won!!!"
            if self.Engine.isWin() else "Tie game")


    def buttonPress(self, x, y):
        if self.Engine.makeMove(f"{x}, {y}"):
            self.buttons[(x, y)].configure(text=self.Engine.getPlayer())
            self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
            if (self.Engine.isEnd()):
                self.endGame()
                

    def createButtons(self):
        buttons = {}
        for x, y in twoDimIter(3, 3):
            button = tk.Button(
                self.Window, text=" ", command=partial(self.buttonPress, x, y))
            button.grid(row=(x+1), column=y, padx=8, pady=8)
            buttons[(x, y)] = button
        return buttons

    def playGame(self):
        self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
        self.Window.mainloop()


def main():
    TicTacToe = GuiTicTacToe()
    TicTacToe.playGame()

if __name__ == '__main__':
    main()
