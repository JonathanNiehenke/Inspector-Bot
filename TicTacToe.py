from collections import OrderedDict, deque

def two_dim_iter(width, height):
    for y in range(height):
        for x in range(width):
            yield (x, y)

class TicTacToeEngine:

    def __init__(self):
        self.current_move = 0;
        self.recent_move = "0, 1";
        self.current_player = "X";
        self.game_board = OrderedDict(
            (f"{x}, {y}", " ") for x, y in two_dim_iter(3, 3))
        self.vector_iters = (
            self.row_Iter, self.col_iter, self.b_diag_iter, self.f_diag_iter)

    def __getitem__(self, Index):
        return self.game_board[Index]

    def __setitem__(self, Index, Value):
        self.game_board[Index] = Value

    def is_player(self, Index):
        return self[Index] == self.current_player 

    def players_vector(self, Vector):
        return (self.is_player(Index) for Index in Vector)

    def row_Iter(self, _, y):
        return (f"{x}, {y}" for x in range(3))

    def col_iter(self, x, _):
        return (f"{x}, {y}" for y in range(3))

    def b_diag_iter(self, x, y):
        return (f"{z}, {z}" for z in range(3)) if x == y else ()

    def f_diag_iter(self, x, y):
        return ((f"{z}, {2 - z}" for z in range(3))
                if int(x) == 2 - int(y) else ())

    def is_vector_win(self, Vector):
        # Prevent returning True if empty as expected from diagonals
        return all(self.players_vector(Vector)) if Vector else False

    def is_win(self):
        x, y = self.recent_move[0], self.recent_move[-1]
        return any(self.is_vector_win(Iter(x, y)) for Iter in self.vector_iters)

    def is_end(self):
        return self.is_win() or self.current_move == 9

    def make_move(self, Index):
        if (self.game_board.get(Index, "") == " "):  # Is a valid move
            self[Index] = self.current_player = self.get_next_player()
            self.current_move += 1
            self.recent_move = Index
            return True
        return False

    def get_player(self):
        return self.current_player

    def get_next_player(self):
        return "O" if self.current_move % 2 else "X"

    def reset(self):
        for Index in self.game_board:
            self[Index] = " "
            self.current_move = 0


class TicTacToe_Intelligence:

    def __init__(self):
        self.engine = TicTacToeEngine()
        self.priority_moves = deque()

    def draw(self, values):
        print("""
{} | {} | {}
--+---+--
{} | {} | {}
--+---+--
{} | {} | {}
        """.format(*values))

    def count_along_vec(self, Vector):
        return sum(self.engine.players_vector(Vector))

    def get_empty(self, Vector):
        for Index in Vector:
            if self.engine[Index] == " ":
                return Index

    def get_next_vec_win(self, Vector):
        repeatVector = tuple(Vector)
        if self.count_along_vec(repeatVector) == 2:
            return self.get_empty(repeatVector)

    def get_winning_moves(self, move):
        x, y = move[0], move[-1]
        winAlongVecs = (self.get_next_vec_win(Iter(x, y))
                        for Iter in self.engine.vector_iters)
        return [move for move in winAlongVecs if move is not None]

    def count_focus(self, Vector, Counter):
        nextPlayer, repeatVector = self.engine.get_next_player(), tuple(Vector)
        isNextPlayerPresent = any(self.engine[Index] == nextPlayer
                                  for Index in repeatVector)
        if not isNextPlayerPresent:
            Focus = self.count_along_vec(repeatVector)
            for Index in repeatVector:
                Counter[Index] += Focus

    def apply_to_board_vectors(self, Func, *args):
        for z in range(3):
            Func(self.engine.row_Iter(None, z), *args)
            Func(self.engine.col_iter(z, None), *args)
        Func(self.engine.b_diag_iter(0, 0), *args)
        Func(self.engine.f_diag_iter(2, 0), *args)

    def count_enemy_focus(self):
        focusCount = OrderedDict(
            (f"{x}, {y}", 0) for x, y in two_dim_iter(3, 3))
        self.apply_to_board_vectors(self.count_focus, focusCount)
        # self.draw(focusCount.values())
        return focusCount

    def get_death_moves(self):
        focusCount = self.count_enemy_focus()
        enemyFocus = (Idx for Idx, Cnt in focusCount.items() if Cnt > 1)
        moves = []
        for Index in enemyFocus:
            backup = (self.engine.current_player, self.engine.game_board.copy())
            self.engine.current_player = self.engine.get_next_player()
            self.engine[Index] = self.engine.current_player
            moves.extend(self.get_winning_moves(Index))
            self.engine.current_player, self.engine.game_board = backup
        return moves

    def count_wins(self, Vector, Counter):
        repeatVector = tuple(Vector)
        if self.engine.is_vector_win(repeatVector):
            for Index in repeatVector:
                Counter[Index] += 1

    def fill_game_board(self, Player):
        for Index in self.engine.game_board:
            if self.engine[Index] == " ":
                self.engine[Index] = Player

    def count_board_wins(self, winCount, Player):
        backup = (self.engine.current_player, self.engine.game_board.copy())
        self.engine.current_player = Player
        self.fill_game_board(Player)
        self.apply_to_board_vectors(self.count_wins, winCount)
        self.engine.current_player, self.engine.game_board = backup
        # self.draw(winCount.values())
        return winCount

    def invert_count(self, countDict):
        invDict = {}
        for Index, Count in countDict.items():
            invDict.setdefault(Count, []).append(Index)
        return invDict

    def sort_count(self, countDict):
        nestedSort = sorted(self.invert_count(countDict).items(), reverse=True)
        return [v for _, l in nestedSort for v in l]

    def make_move(self):
        # print(self.priority_moves)
        while self.priority_moves:
            move = self.priority_moves.popleft()
            if self.engine.game_board.get(move, "") == " ": break
        else:
            deathMoves = self.get_death_moves()
            winCount = OrderedDict(
                (f"{x}, {y}", 0) for x, y in two_dim_iter(3, 3))
            self.count_board_wins(winCount, self.engine.current_player)
            self.count_board_wins(winCount, self.engine.get_next_player())
            for move in self.sort_count(winCount):
                if (self.engine.game_board.get(move, "") == " " and
                   move not in deathMoves):
                    break
        self.engine.make_move(move)
        self.priority_moves.extend(self.get_winning_moves(move))
        return move

    def oppenent_move(self, move):
        self.engine.make_move(move);
        self.priority_moves.extend(self.get_winning_moves(move))

    def reset(self):
        self.engine.reset()
        self.priority_moves.clear()
