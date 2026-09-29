import time
from board import Board
from piece import Rook, Pawn, King
from ai import alphabeta_fast

INF = float('inf')

board = Board()
for depth in [2, 3]:
    start = time.time()
    score, (piece, move) = alphabeta_fast(board, depth, -INF, INF, True)
    print(f'depth {depth}: {piece.name} {move}  score {score:.2f}  ({time.time()-start:.1f}s)')

# back-rank mate test
board = Board()
for r in range(8):
    for c in range(8):
        board.squares[r][c].piece = None
board.squares[0][7].piece = King('black')
board.squares[1][5].piece = Pawn('black')
board.squares[1][6].piece = Pawn('black')
board.squares[1][7].piece = Pawn('black')
board.squares[7][0].piece = Rook('white')
board.squares[7][6].piece = King('white')

score, (piece, move) = alphabeta_fast(board, 2, -INF, INF, True)
print(f'mate test: {piece.name} {move}  score {score}')