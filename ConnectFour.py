from collections import OrderedDict
from SeriesGame import SeriesGame

class ConnectFourEngine(SeriesGame):

    def __init__(self):
        SeriesGame.__init__(self, height=6, width=7, win=4)
        self.available_moves = [f"{x}, {self.height-1}" for x in range(self.width)]

    def make_column_move(self, x):
        Index = self.available_moves[x]
        if self.make_move(Index):
            y = int(Index[-1]) - 1
            self.available_moves[x] = f"{x}, {y}"
            return Index
        return None

class ConnectFour_Intelligence:

    def __init__(self):
        self.engine = ConnectFourEngine()

    def draw(self, values):
        print("""
+--+--+--+--+--+--+--+
|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|
+--+--+--+--+--+--+--+
|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|
+--+--+--+--+--+--+--+
|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|
+--+--+--+--+--+--+--+
|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|
+--+--+--+--+--+--+--+
|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|
+--+--+--+--+--+--+--+
|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|{:>2}|
+--+--+--+--+--+--+--+
        """.format(*values))

    def fill_game_board(self, Player):
        for Index in self.engine.game_board:
            if self.engine[Index] == " ":
                self.engine[Index] = Player

    def by_four(self, Vector):
        Idx1, Idx2, Idx3 = next(Vector), next(Vector), next(Vector)
        for Idx4 in Vector:
            yield (Idx1, Idx2, Idx3, Idx4)
            Idx1, Idx2, Idx3 = Idx2, Idx3, Idx4

    def count_wins(self, Vector, Counter):
        Player = self.engine.get_player()
        for fourSeries in self.by_four(Vector):
            if all(self.engine[Index] == Player for Index in fourSeries):
                for Index in fourSeries:
                    Counter[Index] += 1

    def apply_to_board_vectors(self, Func, *args):
        for z in range(self.engine.height):
            Func(self.engine.row_iter(None, z), *args)
        for z in range(self.engine.width):
            Func(self.engine.col_iter(z, None), *args)
        for d in range(self.engine.diags):
            Func(self.engine.b_diag_iter(d), *args)
            Func(self.engine.f_diag_iter(d), *args)

    def count_board_wins(self):
        winCount = OrderedDict((Index, 0) for Index in iter(self.engine))
        backupBoard = self.engine.game_board.copy()
        self.fill_game_board(self.engine.get_player())
        self.apply_to_board_vectors(self.count_wins, winCount)
        self.engine.game_board = backupBoard
        self.draw(winCount.values())

    def oppenent_move(self, move):
        self.engine.make_move(move);
        self.count_board_wins()
