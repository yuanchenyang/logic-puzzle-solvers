from z3 import *
from collections import defaultdict

class Sudoku():
    def __init__(self):
        # 9x9 matrix of integer variables
        self.X = [[Int("x_%s_%s" % (i+1, j+1)) for j in range(9)]
                  for i in range(9)]

        # each cell contains a value in {1, ..., 9}
        cells_c  = [And(1 <= self.X[i][j], self.X[i][j] <= 9)
                    for i in range(9) for j in range(9)]

        # each row contains a digit at most once
        rows_c   = [Distinct(self.X[i]) for i in range(9)]

        # each column contains a digit at most once
        cols_c   = [Distinct([ self.X[i][j] for i in range(9)])
                    for j in range(9)]

        # each 3x3 square contains a digit at most once
        sq_c     = [Distinct([self.X[3*i0 + i][3*j0 + j]
                              for i in range(3) for j in range(3)])
                    for i0 in range(3) for j0 in range(3)]

        self.constraints = cells_c + rows_c + cols_c + sq_c
        self.instance_constraints = []

    def get_groups(self, instance):
        cell_groups = defaultdict(list)
        for i, row in enumerate(instance):
            for j, c in enumerate(row):
                cell_groups[c].append(self.X[i][j])
        return cell_groups

    def add_filled_numbers(self, instance):
        instance_c = [self.X[i][j] == int(instance[i][j])
                      for i in range(9) for j in range(9)
                      if instance[i][j] != '0']
        self.instance_constraints += instance_c

    def add_killer_sudoku(self, instance, sums=None, equals=None, gts=None,
                          distinct=True):
        sums = sums or {}
        equals = equals or []
        gts = gts or []
        groups = self.get_groups(instance)
        symbols = set(tuple(sums.keys()) + sum(equals + gts, tuple()))
        distinct_c = [Distinct(groups[s]) for s in symbols] if distinct else []
        sums_c =   [sum(groups[c]) == val            for c, val in sums.items()]
        equals_c = [sum(groups[a]) == sum(groups[b]) for a,b in equals]
        gt_c =     [sum(groups[a]) >  sum(groups[b]) for a,b in gts]
        self.instance_constraints += sums_c + distinct_c + equals_c + gt_c

    def add_miracle_rules(self):
        ortho_move  = [(-1, 0), (1, 0), (0,-1), (0, 1)]
        king_move   = ortho_move + [(-1,-1), (-1,1), (1,-1), (1, 1)]
        knight_move = [(-2,-1), (-2, 1), ( 2,-1), ( 2, 1),
                       ( 1,-2), ( 1, 2), (-1, 2), (-1,-2)]
        valid_cells = set([(i,j) for i in range(9) for j in range(9)])
        add = lambda a,b: (a[0]+b[0], a[1]+b[1])
        get = lambda c: self.X[c[0]][c[1]]
        gen_pairs = lambda deltas: ((get(c), get(add(c, delta)))
                                    for c in list(valid_cells)
                                    for delta in deltas
                                    if add(c, delta) in valid_cells)
        move_c = [c1 != c2 for c1, c2 in gen_pairs(king_move + knight_move)]
        ortho_c = [And(c1 - c2 != 1, c2 - c1 != 1) for c1, c2 in gen_pairs(ortho_move)]
        self.instance_constraints += move_c + ortho_c

    def solve(self,
              additional_constraints=None,
              verbose=True,
              debug=False,
              check_uniqueness=False):
        # Quantifier-free finite domain theory
        s = SolverFor("QF_FD")
        additional_constraints = additional_constraints or []
        s.add(self.constraints + self.instance_constraints + additional_constraints)
        if debug:
            print('Sudoku Constraints', self.constraints)
            print('Instance Constraints', self.instance_constraints)
        if s.check() == sat:
            m = s.model()
            r = '\n'.join(''.join(str(m.evaluate(self.X[i][j])) for j in range(9))
                          for i in range(9))
            if verbose:
                print('Solution:')
                print(r)
            if check_uniqueness:
                s.add(Or(*[Xi != m.evaluate(Xi) for row in self.X for Xi in row]))
                unique = not (s.check() == sat)
                if verbose: print(f'Solution {"" if unique else "Not "}Unique!')
                return unique
        else:
            if verbose: print("failed to solve")

def solve_sudoku():
    # Normal sudoku instance, we use '0' for empty cells
    instance = \
    ('530070000',
     '600195000',
     '098000060',
     '800060003',
     '400803001',
     '700020006',
     '060000280',
     '000419005',
     '000080079')
    s = Sudoku()
    s.add_filled_numbers(instance)
    s.solve()

def solve_killer_sudoku():
    # Killer sudoku instance with additional sum constraints
    instance = \
      ('aabcceegg',
       'llbddfjhi',
       'lmnoffjhi',
       'mmnooAjkk',
       'ttpozABBC',
       'rqpzzyBCC',
       'rqsszyDEE',
       'uvvwwyDFF',
       'uuuwxxDGG')
    sums = {'b':6, 'e':16, 'f':17, 'h':12, 'i':9, 'j':9, 'l':14, 'm':20, 'n':13,
            'o':29, 'p':8, 'q':14, 'r':8, 's':17, 'u':11, 'w':11, 'z':12, 'A':4, 'F':8}
    equals = [('c', 'd')]
    gts = [('h','g'), ('g','i'), ('q','v'), ('v','u'), ('x','w'), ('y','x')]

    s = Sudoku()
    s.add_killer_sudoku(instance, sums, equals, gts)
    s.solve()

def solve_hard_killer_sudoku():
    instance = \
      ('aaabbbccc',
       'adddeffgc',
       'ammleifgh',
       'amllkiiih',
       'onllkjjih',
       'onnnkjjwt',
       'oprnujwwt',
       'qprruvvvt',
       'qqqsssttt')

    sums = \
    {'a':28,'b':12,'c':22,'d':16,'e':10,'f':10,'g':13,'h':14,'i':23,'j':31,
     'k':13,'l':33,'m':12,'n':31,'o':10,'p':12,'q':20,'r':11,'s':17,'t':23,
     'u':10,'v':15,'w':19}
    s = Sudoku()
    s.add_killer_sudoku(instance, sums)
    s.solve()

def solve_arrow_sudoku():
    instance = \
      ('000000050',
       '000506090',
       '960000000',
       '000000000',
       '500070009',
       '000000000',
       '000000048',
       '090605000',
       '070000000')
    arrow_instance = \
      (' aa bbB  ',
       '  A F   d',
       '    f edc',
       '   fGeDCc',
       ' hgg E   ',
       'Hh  J  mM',
       'I  j  m  ',
       'i j   ll ',
       'i  Kkk  L')
    s = Sudoku()
    s.add_filled_numbers(instance)
    s.add_killer_sudoku(arrow_instance,
                    equals=list(zip('abcdefghijklm', 'ABCDEFGHIJKLM')),
                    distinct=False)
    s.solve()

def solve_miracle_sudoku():
    instance = \
      ('000000000',
       '000000000',
       '000000000',
       '000000000',
       '001000000',
       '000000200',
       '000000000',
       '000000000',
       '000000000')
    instance = \
      ('000000000',
       '000000000',
       '000020000',
       '001000000',
       '000000000',
       '000000000',
       '000000000',
       '000000000',
       '000000000')
    s = Sudoku()
    s.add_filled_numbers(instance)
    s.add_miracle_rules()
    s.solve(check_uniqueness=True)

def generate_miracle_sudoku():
    s = Sudoku()
    s.add_miracle_rules()
    return [(i, j) for i in range(9) for j in range(9)
            if not (i == j == 0) and
               s.solve(additional_constraints=[s.X[0][0] == 1, s.X[i][j] == 2],
                       check_uniqueness=True,
                       verbose=False)]

if __name__=='__main__':
    #solve_sudoku()
    #solve_killer_sudoku()
    #solve_hard_killer_sudoku()
    #solve_arrow_sudoku()
    solve_miracle_sudoku()
    #generate_miracle_sudoku()