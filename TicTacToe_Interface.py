from functools import partial
from tkinter import messagebox
import tkinter as tk
import os

from TicTacToe import twoDimIter, TicTacToeEngine, TicTacToe_Intelligence

class ConsoleTicTacToe:

    def __init__(self, cpu=None):
        self.Engine = TicTacToeEngine()
        self.cpu = cpu
        vsCpu, self.gameAmount = self.provideOptions()
        self.gameCount = 0
        self.playGame = self.playGame_HvC if vsCpu else  self.playGame_HvH

    def provideOptions(self):
        vsCPU = input("1. Player or 2. CPU: ") == "2"
        gamesAmount = int(input("How many games? (Even number): "))
        return vsCPU, gamesAmount

    def draw(self):
        os.system("cls")
        print("""
Game {}:
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(self.gameCount + 1, *self.Engine.gameBoard.values()))
        print()

    def playerMove(self):
        self.draw()
        playerInput = input("Please enter the column, row coordinates: ")
        while not self.Engine.makeMove(playerInput):
            playerInput = input("Please enter something like 1, 2: ");
        return playerInput

    def playGame_HvH(self):
        while not self.Engine.isEnd():
            self.playerMove()
        else:
            self.draw()
            if self.Engine.isWin():
                print(f"Player {self.Engine.getPlayer()} Won!!!")
            else:
                print("Tie game")
            input("Press Enter...")

    def playGame_HvC(self):
        while not self.Engine.isEnd():
            self.cpu.opponentMove(self.playerMove())
            if not self.Engine.isEnd():
                self.Engine.makeMove(self.cpu.makeMove())
        else:
            self.draw()
            if self.Engine.isWin():
                print(f"Player {self.Engine.getPlayer()} Won!!!")
            else:
                print("Tie game")
            input("Press Enter...")

    def playGameSet(self):
        for self.gameCount in range(self.gameAmount):
            self.playGame()
            self.Engine.reset()
            if self.playGame == self.playGame_HvC:
                self.cpu.reset()
                if self.gameCount % 2 == 0:
                    self.Engine.makeMove(self.cpu.makeMove())


class OptionsFrame(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.gameNum = 2
        self.vsCpu = tk.BooleanVar()
        self.playMsg = tk.StringVar()
        # tk widgets
        self.playerRadio = tk.Radiobutton(
            self,
            text="Player",
            variable=self.vsCpu,
            value=False,
            indicatoron=0)
        self.cpuRadio = tk.Radiobutton(
            self,
            text="CPU",
            variable=self.vsCpu,
            value=True,
            indicatoron=0)
        self.increaseBtn = tk.Button(
            self, text="+2", command=partial(self.increaseGames, 2))
        self.decreaseBtn = tk.Button(
            self, text="-2",command=partial(self.increaseGames, -2))
        tk.Button(self, textvar=self.playMsg, command=self.playGame).grid(
            row=2, column=0, columnspan=2, sticky="nsew")

    def provideOptions(self):
        self.playMsg.set(f"Play {self.gameNum} games")
        self.playerRadio.grid(row=0, column=0, sticky="nsew")
        self.cpuRadio.grid(row=0, column=1, sticky="nsew")
        self.increaseBtn.grid(row=1, column=0, sticky="nsew")
        self.decreaseBtn.grid(row=1, column=1, sticky="nsew")
        self.grid(row=0, column=0)
        self.parent.wait_window(self)
        return self.vsCpu.get(), self.gameNum

    def increaseGames(self, value):
        self.gameNum += value
        self.playMsg.set(f"Play {self.gameNum} games")

    def playGame(self):
        self.destroy()


class GuiTicTacToe:

    def __init__(self, cpu=None):
        self.Window = tk.Tk()
        self.Engine = TicTacToeEngine()
        self.cpu = cpu
        vsCpu, self.gameAmount = OptionsFrame(self.Window).provideOptions()
        self.gameCount = 1
        self.buttonPress = (
            self.buttonPress_HvC if vsCpu  else self.buttonPress_HvH)
        self.buttons = self.createButtons()
        self.msgText = tk.StringVar()
        tk.Label(self.Window, textvar=self.msgText).grid(
            row=0, column=0, columnspan=3)

    def reset(self):
        self.Engine.reset()
        self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
        for button in self.buttons.values():
            button.configure(text=" ", state="normal")

    def endGame(self):
        for button in self.buttons.values():
            button.configure(state="disabled")
        Title = f"Game {self.gameCount}"
        Msg = (f"player {self.Engine.getPlayer()} Won!!!"
               if self.Engine.isWin() else "Tie game")
        tk.messagebox.showinfo(Title, Msg)
        if self.gameCount < self.gameAmount:
            self.gameCount += 1
            self.reset()
            if self.buttonPress == self.buttonPress_HvC:
                self.cpu.reset()
                if self.gameCount % 2 == 0:
                    self.cpuMove()
        else:
            self.Window.destroy()

    def buttonPress_HvH(self, x, y):
        move = f"{x}, {y}"
        if self.Engine.makeMove(move):
            self.buttons[move].configure(text=self.Engine.getPlayer())
            if (self.Engine.isEnd()):
                self.endGame()
            self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")

    def cpuMove(self):
        move = self.cpu.makeMove()
        self.Engine.makeMove(move)
        self.buttons[move].configure(text=self.Engine.getPlayer())
        if (self.Engine.isEnd()):
            self.endGame()
        self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")

    def buttonPress_HvC(self, x, y):
        move = f"{x}, {y}"
        if self.Engine.makeMove(move):
            self.buttons[move].configure(text=self.Engine.getPlayer())
            if (self.Engine.isEnd()):
                self.endGame()
            else:
                self.cpu.opponentMove(move)
                self.cpuMove()

    def createButtons(self):
        buttons = {}
        for x, y in twoDimIter(3, 3):
            thisButtonPress = partial(self.buttonPress, x, y)
            button = tk.Button(self.Window, text=" ", font=('Courier', 18),
                               command=thisButtonPress)
            button.grid(row=(y+1), column=x, padx=8, pady=8)
            buttons[f"{x}, {y}"] = button
        return buttons

    def playGame(self):
        self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
        self.Window.mainloop()


def main():
    ConsoleTicTacToe(TicTacToe_Intelligence()).playGameSet()
    # GuiTicTacToe(TicTacToe_Intelligence()).playGame()

if __name__ == '__main__':
    main()
