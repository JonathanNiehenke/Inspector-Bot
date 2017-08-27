from functools import partial
import tkinter as tk
import os

from TicTacToe import twoDimIter, TicTacToeEngine, TicTacToe_Intelligence

class ConsoleTicTacToe:

    def __init__(self, cpu=None):
        self.Engine = TicTacToeEngine()
        self.cpu = cpu
        self.playGame = self.playGame_HvH if cpu is None else  self.playGame_HvC

    def draw(self):
        # os.system("cls")
        print("""
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(*self.Engine.gameBoard.values()))

    def playerMove(self):
        self.draw()
        print(f"Player {self.Engine.getNextPlayer()} to move.")
        playerInput = input("Please enter the column, row coordinates: ")
        while not self.Engine.makeMove(playerInput):
            playerInput = input("Please enter something like 1, 2");
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

    def playGame_HvC(self):
        while not self.Engine.isEnd():
            self.Engine.makeMove(self.cpu.makeMove())
            if not self.Engine.isEnd():
                self.cpu.opponentMove(self.playerMove())
        else:
            self.draw()
            if self.Engine.isWin():
                print(f"Player {self.Engine.getPlayer()} Won!!!")
            else:
                print("Tie game")


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
        Welcome = OptionsFrame(self.Window)
        vsCpu, gameNum = Welcome.provideOptions()
        self.buttonPress = (
            self.buttonPress_HvC if vsCpu  else self.buttonPress_HvH)
        self.buttons = self.createButtons()
        self.msgText = tk.StringVar()
        tk.Label(self.Window, textvar=self.msgText).grid(
            row=0, column=0, columnspan=3)

    def endGame(self):
        self.msgText.set(f"Player {self.Engine.getPlayer()} Won!!!"
                         if self.Engine.isWin() else "Tie game")
        for button in self.buttons.values():
            button.configure(state="disabled")

    def buttonPress_HvH(self, x, y):
        move = f"{x}, {y}"
        if self.Engine.makeMove(move):
            self.buttons[move].configure(text=self.Engine.getPlayer())
            self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
            if (self.Engine.isEnd()):
                self.endGame()

    def cpuMove(self):
        move = self.cpu.makeMove()
        self.Engine.makeMove(move)
        self.buttons[move].configure(text=self.Engine.getPlayer())
        self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
        if (self.Engine.isEnd()):
            self.endGame()

    def buttonPress_HvC(self, x, y):
        move = f"{x}, {y}"
        if self.Engine.makeMove(move):
            self.buttons[move].configure(text=self.Engine.getPlayer())
            self.msgText.set(f"Player {self.Engine.getNextPlayer()} to move.")
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
    # ConsoleTicTacToe(TicTacToe_Intelligence()).playGame()
    GuiTicTacToe(TicTacToe_Intelligence()).playGame()

if __name__ == '__main__':
    main()
