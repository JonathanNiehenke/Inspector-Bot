from functools import partial
from tkinter import messagebox
from sys import argv
import tkinter as tk
import os


from TicTacToe import TicTacToeEngine, TicTacToe_Intelligence

class ConsoleTicTacToe:

    def __init__(self, cpu=None):
        self.engine = TicTacToeEngine()
        self.cpu = cpu if cpu else TicTacToe_Intelligence()
        vs_cpu, self.game_amount = self.provide_options()
        self.game_count = 0
        self.play_game = self.play_game_hvc if vs_cpu else  self.play_game_hvh

    def provide_options(self):
        vsCPU = input("1. Player or 2. CPU: ") == "2"
        gamesAmount = int(input("How many games? (Even number): "))
        return vsCPU, gamesAmount

    def draw(self):
        gridValues = (self.engine[Index] for Index in iter(self.engine))
        os.system("cls")
        print("""
Game {}:
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(self.game_count + 1, *gridValues))
        print()

    def player_move(self):
        self.draw()
        playerInput = input("Please enter the column, row coordinates: ")
        while not self.engine.make_move(playerInput):
            playerInput = input("Please enter something like 1, 2: ");
        return playerInput

    def play_game_hvh(self):
        while not self.engine.is_end():
            self.player_move()
        else:
            self.draw()
            if self.engine.is_win():
                print(f"Player {self.engine.get_player()} Won!!!")
            else:
                print("Tie game")
            input("Press Enter...")

    def play_game_hvc(self):
        while not self.engine.is_end():
            self.cpu.oppenent_move(self.player_move())
            if not self.engine.is_end():
                self.engine.make_move(self.cpu.make_move())
        else:
            self.draw()
            if self.engine.is_win():
                print(f"Player {self.engine.get_player()} Won!!!")
            else:
                print("Tie game")
            input("Press Enter...")

    def play_gameSet(self):
        for self.game_count in range(self.game_amount):
            self.play_game()
            self.engine.reset()
            if self.play_game == self.play_game_hvc:
                self.cpu.reset()
                if self.game_count % 2 == 0:
                    self.engine.make_move(self.cpu.make_move())


class OptionsFrame(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.game_num = 2
        self.vs_cpu = tk.BooleanVar()
        self.play_msg = tk.StringVar()
        # tk widgets
        self.player_radio = tk.Radiobutton(
            self,
            text="Player",
            variable=self.vs_cpu,
            value=False,
            indicatoron=0)
        self.cpu_radio = tk.Radiobutton(
            self,
            text="CPU",
            variable=self.vs_cpu,
            value=True,
            indicatoron=0)
        self.increase_btn = tk.Button(
            self, text="+2", command=partial(self.increase_games, 2))
        self.decrease_btn = tk.Button(
            self, text="-2",command=partial(self.increase_games, -2))
        tk.Button(self, textvar=self.play_msg, command=self.play_game).grid(
            row=2, column=0, columnspan=2, sticky="nsew")

    def provide_options(self):
        self.play_msg.set(f"Play {self.game_num} games")
        self.player_radio.grid(row=0, column=0, sticky="nsew")
        self.cpu_radio.grid(row=0, column=1, sticky="nsew")
        self.increase_btn.grid(row=1, column=0, sticky="nsew")
        self.decrease_btn.grid(row=1, column=1, sticky="nsew")
        self.grid(row=0, column=0)
        self.parent.wait_window(self)
        return self.vs_cpu.get(), self.game_num

    def increase_games(self, value):
        self.game_num += value
        self.play_msg.set(f"Play {self.game_num} games")

    def play_game(self):
        self.destroy()


class GuiTicTacToe:

    def __init__(self, cpu=None):
        self.window = tk.Tk()
        self.engine = TicTacToeEngine()
        self.cpu = cpu if cpu else TicTacToe_Intelligence()
        vs_cpu, self.game_amount = OptionsFrame(self.window).provide_options()
        self.game_count = 1
        self.button_press = (
            self.button_press_hvc if vs_cpu  else self.button_press_hvh)
        self.buttons = self.create_buttons()
        self.msg_text = tk.StringVar()
        tk.Label(self.window, textvar=self.msg_text).grid(
            row=0, column=0, columnspan=3)

    def reset(self):
        self.engine.reset()
        self.msg_text.set(f"Player {self.engine.get_next_player()} to move.")
        for button in self.buttons.values():
            button.configure(text=" ", state="normal")

    def end_game(self):
        for button in self.buttons.values():
            button.configure(state="disabled")
        Title = f"Game {self.game_count}"
        Msg = (f"player {self.engine.get_player()} Won!!!"
               if self.engine.is_win() else "Tie game")
        tk.messagebox.showinfo(Title, Msg)
        if self.game_count < self.game_amount:
            self.game_count += 1
            self.reset()
            if self.button_press == self.button_press_hvc:
                self.cpu.reset()
                if self.game_count % 2 == 0:
                    self.cpu_move()
        else:
            self.window.destroy()

    def button_press_hvh(self, Index):
        if self.engine.make_Index(Index):
            self.buttons[Index].configure(text=self.engine.get_player())
            if (self.engine.is_end()):
                self.end_game()
            self.msg_text.set(f"Player {self.engine.get_next_player()} to move.")

    def cpu_move(self):
        move = self.cpu.make_move()
        self.engine.make_move(move)
        self.buttons[move].configure(text=self.engine.get_player())
        if (self.engine.is_end()):
            self.end_game()
        self.msg_text.set(f"Player {self.engine.get_next_player()} to move.")

    def button_press_hvc(self, Index):
        if self.engine.make_move(Index):
            self.buttons[Index].configure(text=self.engine.get_player())
            if (self.engine.is_end()):
                self.end_game()
            else:
                self.cpu.oppenent_move(Index)
                self.cpu_move()

    def create_buttons(self):
        buttons = {}
        for Index in iter(self.engine):
            x, y = int(Index[0]), int(Index[-1])
            thisButtonPress = partial(self.button_press, Index)
            button = tk.Button(self.window, text=" ", font=('Courier', 18),
                               command=thisButtonPress)
            button.grid(row=(y+1), column=x, padx=8, pady=8)
            buttons[f"{x}, {y}"] = button
        return buttons

    def play_game(self):
        self.msg_text.set(f"Player {self.engine.get_next_player()} to move.")
        self.window.mainloop()


def main():
    try:
        Interface = GuiTicTacToe() if argv[1] == "GUI" else ConsoleTicTacToe()
    except:
        Interface = ConsoleTicTacToe()
    Interface.play_game()

if __name__ == '__main__':
    main()
