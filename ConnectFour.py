from SeriesGame import SeriesGame

class ConnectFourEngine(SeriesGame):

    def __init__(self):
        SeriesGame.__init__(self, height=6, width=7, win=4)

    def make_column_move(self, x):
        for Index in self.col_iter(x, None, reverse=True):
            if self.make_move(Index):
                return Index
        return None
