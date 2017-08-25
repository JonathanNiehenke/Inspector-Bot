from functools import partial
import tkinter as tk

from TicTacToe import twoDimIter, TicTacToeEngine

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
            playerInput = input("Please enter the column, row coordinates ")
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

