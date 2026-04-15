"""
Vitae Mors
Salt
Air Fire Water Earth
Quicksilver
Lead Tin Iron Copper silveR Gold
"""
from collections import Counter
from itertools import combinations
from random import shuffle

MetalsOrder = "GRCITL"
elemental = set("AFWE")
metals = set("LTICR")
anima = set("VM")


def matches(c1, c2):
    if c1 == "G": return False
    if c1 == "Q": return c2 in metals
    if c1 == "S": return c2 in elemental or c2 == "S"
    if c1 in anima: return {c1, c2} == anima
    if c1 in metals: return c2 == "Q"
    if c1 in elemental: return c1 == c2 or c2 == "S"
    raise Exception(f"{c1} isnt a proper substance")


def flatten(board):
    for i in board:
        for j in range(len(i)):
            i[j] = yield
    yield


def row_size(i):
    # 6..10,11,10..
    return 11 - abs(i - 5)


def col_in_other_row(src_row, tgt_row):
    return (row_size(tgt_row) - row_size(src_row)) // 2


def contiguous(haystack, needle, count):
    # TODO this only works for haystack: iter[char], needle: char, count: usize
    return needle * count in haystack[-1] + "".join(haystack) + haystack[0]


class Board:
    def __init__(self, data_string: str):
        self.board = [['_'] * row_size(i) for i in range(11)]
        data_string = ''.join(data_string.upper().strip().split())
        it = flatten(self.board)
        next(it)
        for s in data_string:
            if s.isdigit():
                for _ in range(int(s)):
                    it.send('_')
            else:
                it.send(s)
        self._dirty = True
        assert not self.impossible()

    def __copy__(self):
        return type(self)(repr(self))

    def get(self, i, j):
        if 0 <= i < len(self.board):
            L = self.board[i]
            if 0 <= j < len(L):
                return L[j]
        return "_"

    def neighbors(self, i, j):
        return [self.get(i, j - 1),
                self.get(i1 := i - 1, j1 := j + col_in_other_row(i, i1)),
                self.get(i1, j1 + 1),
                self.get(i, j + 1),
                self.get(i1 := i + 1, (j1 := j + col_in_other_row(i, i1)) + 1),
                self.get(i + 1, j1)]

    def _precompute(self, force=False):
        if not (self._dirty or force):
            return  # no need to recompute the precomputed
        self.counter = Counter(j.upper() for i in self.board for j in i if j != "_")
        for i, L in enumerate(self.board):
            for j, c in enumerate(L):
                if c == '_': continue
                if contiguous(self.neighbors(i, j), "_", 3):
                    self.board[i][j] = c.upper()
                else:
                    self.board[i][j] = c.lower()

    def available(self):
        self._precompute()
        for i, L in enumerate(self.board):
            for j, c in enumerate(L):
                # isupper is the marker that precompute uses to say it has 3 contiguous neighbors
                # if it's a metal it has to be its turn in the metal order
                # if it's not a metal. it can be clicked just using isupper
                if c.isupper() and (c not in MetalsOrder or self.metal_count() == MetalsOrder.find(c)):
                    yield i, j, c

    def moves(self):
        available = list(self.available())
        for i1, j1, c1 in available:
            if c1 == "G" and self.metal_count() == 0:
                yield (i1, j1),
        for ((i1, j1, c1), (i2, j2, c2)) in combinations(available, 2):
            if matches(c1, c2):
                yield (i1, j1), (i2, j2)

    def move(self, *ijs):
        self._dirty = True
        for i, j in ijs:
            self.board[i][j] = '_'
        return self

    def metal_count(self):
        self._precompute()
        return sum(self.counter[i] for i in metals)

    def odd_elements(self):
        self._precompute()
        return sum(self.counter[i] % 2 for i in elemental)

    def impossible(self):
        assert self.metal_count() == self.counter["Q"]
        assert self.counter["V"] == self.counter["M"]
        return self.odd_elements() > self.counter["S"]

    def win(self):
        self._precompute()
        return all((j == "_" or j.isupper()) for i in self.board for j in i)

    def solve(self):
        if self.impossible(): return []
        if self.win(): return [repr(self)]
        moves = list(self.moves())
        shuffle(moves)
        for move in moves:
            s = self.__copy__().move(*move).solve()
            if s: return [(repr(self), move, ''.join(self.get(*ij) for ij in move)), *s]
        return []

    def __str__(self):
        return '\n'.join(f"{' '.join(i):^23}" for i in self.board)

    def __repr__(self):
        return ''.join(''.join(i) for i in self.board)


def solve_game(bstr):
    board = Board(bstr)
    solve_path = board.solve()
    for _, ps, _ in solve_path[:-1]:
        yield ps
    board = Board(solve_path[-1])
    while True:
        move = next(board.moves(), None)
        if move is None: break
        board.move(*move)
        yield move


def main():
    b = Board("F_S___AE_F___S_WWEQWVMSAC___EW_E_AMEFQ_W__A_EGFFWWE__F_IA_F___FVEQ_QQTM_SW_A___V_AA__VLRM__")
    s = b.solve()
    for x in s[:-1]: print(x)
    print(" ", s[-1])
    for x, *r in s[:-1]:
        print(Board(x))
        print(r)
        input()


if __name__ == '__main__':
    main()
