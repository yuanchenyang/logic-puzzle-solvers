#!/usr/bin/python3

import sys
import unittest
import argparse
from functools import reduce
from itertools import groupby, product

first = lambda p: p[0]
second =  lambda p: p[1]

class Cell:
    '''2D doubly linked list'''
    def __init__(self):
        self.N = self.E = self.S = self.W = self

    def insert_E(self, other):
        other.W, other.E = self, self.E
        self.E.W = self.E = other

    def insert_S(self, other):
        other.N, other.S = self, self.S
        self.S.N = self.S = other

    def iter_dir(self, direction):
        '''Iterates in direction starting at curent cell, does not include
        current cell'''
        cur = self
        while (cur := getattr(cur, direction)) != self:
            yield cur

class Link(Cell):
    def __init__(self, C=None, row=-1):
        Cell.__init__(self)
        self.C = C
        self.row = row

def link_row(lst):
    def link(a, b):
        a.insert_E(b)
        return b
    reduce(link, lst)

class Col(Cell):
    def __init__(self, count=0):
        Cell.__init__(self)
        self.count = count

    def cover(self):
        self.E.W, self.W.E = self.W, self.E
        for row in self.iter_dir('S'):
            for cell in row.iter_dir('E'):
                cell.N.S, cell.S.N = cell.S, cell.N
                cell.C.count -= 1

    def uncover(self):
        for row in self.iter_dir('N'):
            for cell in row.iter_dir('W'):
                cell.C.count += 1
                cell.N.S = cell.S.N = cell
        self.E.W = self.W.E = self

class Instance:
    '''An instance of an exact cover problem'''
    def __init__(self, rows, cols):
        ''' Cols is a sequence of column names, rows is a sequence of tuples of
        column names
        '''
        self.rows = rows
        self.cols = cols
        self.col_index = {col: i for i, col in enumerate(cols)}
        self.entries = [(ri, self.col_index[c]) for ri, row in enumerate(rows)
                                                for c in row]
        self.initialize()

    def from_matrix(M):
        cols = range(len(M[0]))
        rows = [[ci for ci, entry in enumerate(row) if entry == 1]
                for row in M]
        return Instance(rows, cols)

    def __iter__(self):
        '''Iterates through rows of matrix, return a pair of row number and
        items in that row'''
        for k, g in groupby(self.entries, key=first):
            yield list(g)

    def initialize(self):
        # Initialize head node
        head = Col()

        # Build column headers
        cols = [Col() for i in range(len(self.cols))]
        link_row(cols)
        cols[-1].insert_E(head)

        # Build rows
        for row in self:
            cur_row = []
            for ri, ci in row:
                col_header = cols[ci].S
                col_header.count += 1
                link = Link(C=col_header, row=ri)
                cols[ci].insert_S(link)
                cols[ci] = link
                cur_row.append(link)
            link_row(cur_row)
        self.head = head

    @property
    def dancing_links(self):
        '''Given a matrix of 0s and 1s M, return a generator of exact covers of M:
        Each exact cover is a tuple of rows containing exactly one 1 per column.

        Implements Knuth's algorithm: https://arxiv.org/abs/cs/0011047
        '''
        out = []
        def search():
            if self.head.E == self.head:
                yield tuple(o.row for o in out)
            else:
                # Choose column c with least branches
                col = min(self.head.iter_dir('E'), key=lambda c: c.count)
                col.cover()
                for row in col.iter_dir('S'):
                    out.append(row)
                    for cell in row.iter_dir('E'):
                        cell.C.cover()
                    for result in search():
                        yield result
                    row = out.pop()
                    for cell in row.iter_dir('W'): # order reversed when uncovering
                        cell.C.uncover()
                col.uncover()
        return search()

class TestDancingLinks(unittest.TestCase):
    def test(self):
        M = [[0,0,1,0,1,1,0],
             [1,0,0,1,0,0,1],
             [0,1,1,0,0,1,0],
             [1,0,0,1,0,0,0],
             [0,1,0,0,0,0,1],
             [0,0,0,1,1,0,1]]
        inst = Instance.from_matrix(M)

        cur = inst.head
        ones = set((r.row, ci) for ci, col in enumerate(inst.head.iter_dir('E'))
                               for r in col.iter_dir('S'))

        for ri, row in enumerate(M):
            for ci, val in enumerate(row):
                if val == 0:
                    assert (ri, ci) not in ones
                else:
                    assert (ri, ci) in ones

        assert list(inst.dancing_links) == [(3, 0, 4)]

README = \
'''Reads in an exact cover instance, defined by one line of space-separated
column names, then lines of rows defining space-separated columns in each row'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=README)
    parser.add_argument('--limit', dest='limit', type=int, default=1000)
    args = parser.parse_args()

    # Read a list of column names
    cols = sys.stdin.readline().strip().split(' ')
    col_index = {col: i for i, col in enumerate(cols)}

    # Rest of input are rows
    rows = list(sys.stdin)
    inst = Instance([(ri, col_index[col]) for ri, row in enumerate(rows)
                                          for col in row.strip().split(' ')])

    for link, _ in zip(inst.dancing_links, range(args.limit)):
        print(''.join(rows[r] for r in link))
