from collections import OrderedDict, deque
from SeriesGame import two_dim_iter, SeriesGame

class TicTacToeEngine(SeriesGame):

    def __init__(self):
        SeriesGame.__init__(self, column=3, row=3, win=3)


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
