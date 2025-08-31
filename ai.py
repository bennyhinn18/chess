# File: ai.py
import chess
import math

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}


def evaluate_board(board: chess.Board) -> int:
    """Simple material evaluation: positive means advantage for White."""
    score = 0
    for piece_type in PIECE_VALUES:
        score += len(board.pieces(piece_type, chess.WHITE)) * PIECE_VALUES[piece_type]
        score -= len(board.pieces(piece_type, chess.BLACK)) * PIECE_VALUES[piece_type]
    return score


def minimax(board: chess.Board, depth: int, alpha: int, beta: int, is_max: bool) -> int:
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    legal_moves = list(board.legal_moves)
    if is_max:
        max_eval = -math.inf
        for m in legal_moves:
            board.push(m)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval > max_eval:
                max_eval = eval
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for m in legal_moves:
            board.push(m)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval < min_eval:
                min_eval = eval
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


def find_best_move(board: chess.Board, depth: int) -> chess.Move | None:
    best_move = None
    best_value = -math.inf
    for move in board.legal_moves:
        board.push(move)
        value = minimax(board, depth - 1, -math.inf, math.inf, False)
        board.pop()
        if value > best_value:
            best_value = value
            best_move = move
    return best_move
