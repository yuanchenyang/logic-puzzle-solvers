sudoku.c: sudoku.w
	ctangle sudoku.w

sudoku: sudoku.c
	gcc sudoku.c -o sudoku

%.out: %.in sudoku dancing_links.py sudoku_decode
	cat $< | ./sudoku | ./dancing_links.py | ./sudoku_decode > $@
