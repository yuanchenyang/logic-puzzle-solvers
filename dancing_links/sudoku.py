import argparse
import sys
from dancing_links import Instance
from collections import defaultdict
from functools import reduce

def box(r, c):
    return (r//3) * 3 + c//3

DIGITS = '123456789'

class Sudoku(Instance):
    def __init__(self, grid):
        self.board = [[d if d in DIGITS else '.' for d in row]
                       for row in grid]
        rs, cs, bs = set(), set(), set()
        for r in range(9):
            for c in range(9):
                if (d := self.board[r][c]):
                    rs.add((r, d))
                    cs.add((c, d))
                    bs.add((box(r, c), d))

        rows = [(f'p{r}{c}', f'r{r}{d}', f'c{c}{d}', f'b{box(r, c)}{d}')
                for r in range(9) for c in range(9)
                if self.board[r][c] not in DIGITS
                for d in DIGITS
                if not ((r, d) in rs or (c, d) in cs or (box(r, c), d) in bs)]

        cols = reduce(set.union, map(set, rows))
        Instance.__init__(self, rows, cols)

    def board_string(self):
        return '\n'.join(''.join(row) for row in self.board)

    @property
    def solutions(self):
        for links in self.dancing_links:
            for row in links:
                pos, rc, _, _ = self.rows[row]
                r, c, d = int(pos[1]), int(pos[2]), rc[2]
                self.board[r][c] = d
            yield self.board_string()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reads sudoku instance from file and prints solution(s)')
    parser.add_argument('filename')
    parser.add_argument('--limit', dest='limit', type=int, default=10)
    args = parser.parse_args()

    # Read a list of column names
    s = Sudoku([line.strip() for line in open(args.filename)])

    for sol, _ in zip(s.solutions, range(args.limit)):
        print('Solution:')
        print(sol)
