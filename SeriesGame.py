from collections import OrderedDict

class SeriesGame:

    def __init__(self, height, width, win, playerSet="XO"):
        self.height, self.width, self.win = height, width, win
        self.diags, self.tie = width + height - 1, width * height
        self.player_set, self.player = playerSet, playerSet[0]
        self.current_move, self.recent_move = 0, "0, 0"
        self.game_board = {Index: " " for Index in self.__iter__()}
        self.vector_iters = (
            self.row_iter, self.col_iter, self.f_diag_iter, self.b_diag_iter)

    def __getitem__(self, Index):
        return self.game_board[Index]

    def __setitem__(self, Index, Value):
        self.game_board[Index] = Value

    def __iter__(self):
        for y in range(self.height):
            for x in range(self.width):
                yield f"{x}, {y}"

    def is_player(self, Index):
        return self[Index] == self.player 

    def players_vector(self, Vector):
        return (self.is_player(Index) for Index in Vector)

    def row_iter(self, x, _):
        return (f"{x}, {y}" for y in range(self.height))

    def col_iter(self, _, y):
        return (f"{x}, {y}" for x in range(self.width))

    def f_diag_iter(self, x, y=None):
        d = x if y is None else int(x) + int(y)
        return (f"{d - z}, {z}" for z in range(d + 1)
                if (z < self.height and d - z < self.width))

    def b_diag_iter(self, x, y=None):
        d = x if y is None else int(x) - int(y) + self.width
        colMax = self.width - 1
        return (f"{z}, {colMax - (d - z)}" for z in range(d + 1)
                if (z < self.width and colMax - d + z >= 0))

    def is_vector_win(self, Vector):
        Series = largestSeries = 0
        for Index in Vector:
            if self.game_board[Index] == self.player:
                Series += 1
            elif Series > largestSeries:
                largestSeries = Series
        return max(Series, largestSeries) >= self.win

    def is_win(self):
        x, y = self.recent_move[0], self.recent_move[-1]
        return any(self.is_vector_win(Iter(x, y)) for Iter in self.vector_iters)

    def is_end(self):
        return self.is_win() or self.current_move == 9

    def make_move(self, Index):
        if (self.game_board.get(Index, "") == " "):  # Is a valid move
            self[Index] = self.player = self.get_next_player()
            self.current_move += 1
            self.recent_move = Index
            return True
        return False

    def get_player(self):
        return self.player

    def get_next_player(self):
        return self.player_set[self.current_move % len(self.player_set)]

    def reset(self):
        for Index in self.game_board:
            self[Index] = " "
            self.current_move = 0

    def get_grid_values(self):
        return (self[Index] for Index in iter(self))
