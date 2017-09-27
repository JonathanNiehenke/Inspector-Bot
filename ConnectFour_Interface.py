from functools import partial
from tkinter import messagebox
import tkinter as tk

from ConnectFour import ConnectFourEngine, ConnectFour_Intelligence

class GuiConnectFour:

    def __init__(self, cpu=None):
        self.engine = ConnectFourEngine()
        self.window = tk.Tk()
        self.cpu = ConnectFour_Intelligence()
        self.buttons = self.create_buttons()
        self.board = self.create_board()
        self.msg_text = tk.StringVar()
        tk.Label(self.window, textvar=self.msg_text).grid(
                 row=0, column=0, columnspan=7)

    def reset(self):
        self.engine.reset()
        self.msg_text.set(f"Player {self.engine.get_next_player()} to move.")
        for button in self.buttons:
            button.configure(state="normal")

    def end_game(self):
        for button in self.buttons:
            button.configure(state="disabled")
        Title = f"Game!"
        Msg = (f"player {self.engine.get_player()} Won!!!"
               if self.engine.is_win() else "Tie game")
        tk.messagebox.showinfo(Title, Msg)
        self.window.destroy()

    def button_press(self, x):
        Index = self.engine.make_column_move(x)
        if Index:
            self.board[Index].configure(text=self.engine.get_player())
            if (self.engine.is_end()):
                self.end_game()
            self.msg_text.set(f"Player {self.engine.get_next_player()} to move.")
            self.cpu.oppenent_move(Index)

    def create_buttons(self):
        buttons = []
        for x in range(self.engine.width):
            thisButtonPress = partial(self.button_press, x)
            button = tk.Button(self.window, text=f"{x}", font=('Courier', 18),
                               command=thisButtonPress)
            button.grid(row=1, column=x, padx=8, pady=8)
            buttons.append(button)
        return buttons

    def create_board(self):
        board = {}
        for Index in iter(self.engine):
            x, y = int(Index[0]), int(Index[-1])
            label = tk.Label(
                self.window, text=" ", font=('Courier', 18), relief="sunken")
            label.grid(row=(y + 2), column=x, padx=2, pady=4, ipadx=8, ipady=4)
            board[Index] = label
        return board

    def play_game(self):
        self.msg_text.set(f"Player {self.engine.get_next_player()} to move.")
        self.window.mainloop()


def main():
    GuiConnectFour().play_game()

if __name__ == '__main__':
    main()
