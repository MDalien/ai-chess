from const import ROWS, COLS
from const import ROWS, COLS
from piece import King
from board import Board
from square import Square
import copy

INF = float('inf')

def get_all_moves(board, color):
    all_moves = []
    for row in range(ROWS):
        for col in range(COLS):
            square = board.squares[row][col]
            if square.has_team_piece(color):
                piece = square.piece
                piece.clear_moves()
                board.calc_moves(piece, row, col, bool=True)
                for move in piece.moves:
                    all_moves.append((piece, move))
    return all_moves

from piece import King

def evaluate(board):
    score = 0
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.squares[row][col].piece
            if piece is None:
                continue
            score += piece.value
            if not isinstance(piece, King):
                dist = max(abs(row - 3.5), abs(col - 3.5))
                bonus = (3.5 - dist) * 0.05
                sign = 1 if piece.color == 'white' else -1
                score += bonus * sign
    return score

import copy

def king_in_check(board, color):
    for row in range(ROWS):
        for col in range(COLS):
            square = board.squares[row][col]
            if square.has_enemy_piece(color):
                enemy = square.piece
                enemy.clear_moves()
                board.calc_moves(enemy, row, col, bool=False)
                for m in enemy.moves:
                    target = board.squares[m.final.row][m.final.col].piece
                    if isinstance(target, King) and target.color == color:
                        return True
    return False

def minimax(board, depth, maximizing):
    color = 'white' if maximizing else 'black'
    moves = get_all_moves(board, color)

    if not moves:
        if king_in_check(board, color):
            return (-100000 if maximizing else 100000), None
        return 0, None

    if depth == 0:
        return evaluate(board), None

    best_move = None
    best_score = float('-inf') if maximizing else float('inf')

    for piece, move in moves:
        temp_board = fast_copy(board)
        temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
        temp_board.move(temp_piece, move, testing=True)
        temp_board.set_true_en_passant(temp_piece)

        score, _ = minimax(temp_board, depth - 1, not maximizing)

        if maximizing and score > best_score:
            best_score, best_move = score, (piece, move)
        elif not maximizing and score < best_score:
            best_score, best_move = score, (piece, move)

    return best_score, best_move

def alphabeta(board, depth, alpha, beta, maximizing):
    color = 'white' if maximizing else 'black'
    moves = get_all_moves(board, color)

    if not moves:
        if king_in_check(board, color):
            return (-100000 if maximizing else 100000), None
        return 0, None

    if depth == 0:
        return evaluate(board), None

    best_move = None

    if maximizing:
        best_score = float('-inf')
        for piece, move in moves:
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
            temp_board.move(temp_piece, move, testing=True)
            temp_board.set_true_en_passant(temp_piece)

            score, _ = alphabeta(temp_board, depth - 1, alpha, beta, False)

            if score > best_score:
                best_score, best_move = score, (piece, move)
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
    else:
        best_score = float('inf')
        for piece, move in moves:
            temp_board = copy.deepcopy(board)
            temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
            temp_board.move(temp_piece, move, testing=True)
            temp_board.set_true_en_passant(temp_piece)

            score, _ = alphabeta(temp_board, depth - 1, alpha, beta, True)

            if score < best_score:
                best_score, best_move = score, (piece, move)
            beta = min(beta, best_score)
            if alpha >= beta:
                break

    return best_score, best_move

def get_pseudo_moves(board, color):
    moves = []
    for row in range(ROWS):
        for col in range(COLS):
            square = board.squares[row][col]
            if square.has_team_piece(color):
                piece = square.piece
                piece.clear_moves()
                board.calc_moves(piece, row, col, bool=False)
                for move in piece.moves:
                    moves.append((piece, move))
    return moves

def capture_value(board, move):
    target = board.squares[move.final.row][move.final.col].piece
    return abs(target.value) if target else 0

def alphabeta_fast(board, depth, alpha, beta, maximizing):
    if depth == 0:
        return evaluate(board), None

    color = 'white' if maximizing else 'black'
    moves = get_pseudo_moves(board, color)
    moves.sort(key=lambda pm: capture_value(board, pm[1]), reverse=True)

    best_move = None
    best_score = float('-inf') if maximizing else float('inf')

    for piece, move in moves:
        temp_board = copy.deepcopy(board)
        temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
        temp_board.move(temp_piece, move, testing=True)
        temp_board.set_true_en_passant(temp_piece)

        if king_in_check(temp_board, color):
            continue

        score, _ = alphabeta_fast(temp_board, depth - 1, alpha, beta, not maximizing)

        if maximizing:
            if score > best_score:
                best_score, best_move = score, (piece, move)
            alpha = max(alpha, best_score)
        else:
            if score < best_score:
                best_score, best_move = score, (piece, move)
            beta = min(beta, best_score)

        if alpha >= beta:
            break

    if best_move is None:
        if king_in_check(board, color):
            return (-100000 if maximizing else 100000), None
        return 0, None

    return best_score, best_move


from board import Board
from square import Square

def fast_copy(board):
    new_board = Board.__new__(Board)
    new_board.last_move = board.last_move
    new_board.squares = [[Square(row, col) for col in range(COLS)] for row in range(ROWS)]

    copies = {}
    for row in range(ROWS):
        for col in range(COLS):
            piece = board.squares[row][col].piece
            if piece is not None:
                new_piece = copy.copy(piece)
                new_piece.moves = []
                copies[id(piece)] = new_piece
                new_board.squares[row][col].piece = new_piece

    for new_piece in copies.values():
        if isinstance(new_piece, King):
            if new_piece.left_rook is not None:
                new_piece.left_rook = copies.get(id(new_piece.left_rook))
            if new_piece.right_rook is not None:
                new_piece.right_rook = copies.get(id(new_piece.right_rook))

    return new_board

    INF = float('inf')

def find_best_move(board, color, depth):
    maximizing = (color == 'white')
    score, best = alphabeta_fast(board, depth, -INF, INF, maximizing)
    return best

def game_status(board, color):
    for piece, move in get_pseudo_moves(board, color):
        temp_board = fast_copy(board)
        temp_piece = temp_board.squares[move.initial.row][move.initial.col].piece
        temp_board.move(temp_piece, move, testing=True)
        if not king_in_check(temp_board, color):
            return 'playing'
    return 'checkmate' if king_in_check(board, color) else 'stalemate'