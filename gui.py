# File: gui.py
import tkinter as tk
from tkinter import messagebox, simpledialog
import chess
import threading
import time
from ai import find_best_move

# Unicode pieces to mimic classic look
UNICODE_PIECES = {
    chess.PAWN:   {chess.WHITE: '♙', chess.BLACK: '♟'},
    chess.ROOK:   {chess.WHITE: '♖', chess.BLACK: '♜'},
    chess.KNIGHT: {chess.WHITE: '♘', chess.BLACK: '♞'},
    chess.BISHOP: {chess.WHITE: '♗', chess.BLACK: '♝'},
    chess.QUEEN:  {chess.WHITE: '♕', chess.BLACK: '♛'},
    chess.KING:   {chess.WHITE: '♔', chess.BLACK: '♚'},
}

class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Win7-style Chess')
        self.board = chess.Board()
        self.square_size = 64
        self.canvas_size = self.square_size * 8
        self.canvas = tk.Canvas(self.root, width=self.canvas_size, height=self.canvas_size)
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

        # right panel
        self.panel = tk.Frame(self.root)
        self.panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.status_var = tk.StringVar()
        self.status_var.set('White to move')
        tk.Label(self.panel, textvariable=self.status_var, font=('Segoe UI', 12, 'bold')).pack(pady=6)

        btn_frame = tk.Frame(self.panel)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text='New Game', command=self.new_game).grid(row=0, column=0, padx=4)
        tk.Button(btn_frame, text='Undo', command=self.undo).grid(row=0, column=1, padx=4)
        tk.Button(btn_frame, text='Flip Board', command=self.flip_board).grid(row=0, column=2, padx=4)

        self.mode_var = tk.StringVar(value='local')
        tk.Radiobutton(self.panel, text='2 Players (Local)', variable=self.mode_var, value='local').pack(anchor='w')
        tk.Radiobutton(self.panel, text='Play vs AI (Black)', variable=self.mode_var, value='ai').pack(anchor='w')

        tk.Label(self.panel, text='AI Depth (2-4)').pack(pady=(10,0))
        self.depth_var = tk.IntVar(value=2)
        tk.Spinbox(self.panel, from_=1, to=4, textvariable=self.depth_var, width=5).pack()

        self.move_list = tk.Text(self.panel, width=30, height=20, state=tk.DISABLED)
        self.move_list.pack(pady=8)

        self.selected_square = None
        self.flipped = False
        self.draw_board()
        self.canvas.bind('<Button-1>', self.on_click)

        self.ai_thread = None
        self.update_status()

    def run(self):
        self.root.mainloop()

    def draw_board(self):
        self.canvas.delete('all')
        for r in range(8):
            for c in range(8):
                x1 = c * self.square_size
                y1 = r * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                color = '#f0d9b5' if (r + c) % 2 == 0 else '#b58863'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')

        # pieces
        squares = list(chess.SQUARES)
        if self.flipped:
            squares = list(reversed(squares))

        for idx, sq in enumerate(squares):
            piece = self.board.piece_at(sq)
            if piece:
                r = idx // 8
                c = idx % 8
                x = c * self.square_size + self.square_size/2
                y = r * self.square_size + self.square_size/2
                text = UNICODE_PIECES[piece.piece_type][piece.color]
                self.canvas.create_text(x, y, text=text, font=('Segoe UI Symbol', 28))

        # labels (a-h, 1-8) small corner labels like Win7
        files = 'abcdefgh'
        ranks = '87654321' if not self.flipped else '12345678'
        for c in range(8):
            x = c * self.square_size + 4
            y = 4
            self.canvas.create_text(x, y, anchor='nw', text=files[c], font=('Segoe UI', 9), fill='#222')
        for r in range(8):
            x = 4
            y = r * self.square_size + 4
            self.canvas.create_text(x, y, anchor='nw', text=ranks[r], font=('Segoe UI', 9), fill='#222')

        # highlight selected
        if self.selected_square is not None:
            idx = ch_sq_index(self.selected_square, self.flipped)
            r = idx // 8
            c = idx % 8
            x1 = c * self.square_size
            y1 = r * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='yellow', width=3)

    def on_click(self, event):
        c = event.x // self.square_size
        r = event.y // self.square_size
        idx = r * 8 + c
        if self.flipped:
            idx = 63 - idx
        square = chess.SQUARES[idx]

        piece = self.board.piece_at(square)
        if self.selected_square is None:
            # select if piece of current color
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            # attempt move
            move = chess.Move(self.selected_square, square)
            # handle promotions for pawns reaching last rank
            if self.board.piece_at(self.selected_square).piece_type == chess.PAWN and (chess.square_rank(square) in (0,7)):
                # prompt for promotion piece
                promo = simpledialog.askstring('Promotion', 'Promote to (q,r,b,n):', parent=self.root)
                if promo:
                    mapping = {'q': chess.QUEEN, 'r': chess.ROOK, 'b': chess.BISHOP, 'n': chess.KNIGHT}
                    pt = mapping.get(promo.lower(), chess.QUEEN)
                    move = chess.Move(self.selected_square, square, promotion=pt)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.draw_board()
                self.log_moves()
                self.update_status()
                # if AI mode and black to move start AI
                if self.mode_var.get() == 'ai' and not self.board.is_game_over() and self.board.turn == chess.BLACK:
                    self.start_ai_move()
            else:
                # if clicked own piece, reselect
                if piece and piece.color == self.board.turn:
                    self.selected_square = square
                else:
                    self.selected_square = None
            self.draw_board()

    def start_ai_move(self):
        if self.ai_thread and self.ai_thread.is_alive():
            return
        def target():
            depth = max(1, min(4, self.depth_var.get()))
            # small delay to show move
            time.sleep(0.2)
            move = find_best_move(self.board, depth)
            if move:
                self.board.push(move)
                self.draw_board()
                self.log_moves()
                self.update_status()
        self.ai_thread = threading.Thread(target=target, daemon=True)
        self.ai_thread.start()

    def log_moves(self):
        self.move_list.config(state=tk.NORMAL)
        self.move_list.delete('1.0', tk.END)
        moves = list(self.board.move_stack)
        san_moves = []
        temp = chess.Board()
        for m in moves:
            san = temp.san(m)
            san_moves.append(san)
            temp.push(m)
        # format: 1. e4 e5 2. Nf3 Nc6 ...
        lines = []
        for i in range(0, len(san_moves), 2):
            num = i//2 + 1
            white = san_moves[i]
            black = san_moves[i+1] if i+1 < len(san_moves) else ''
            lines.append(f"{num}. {white} {black}")
        self.move_list.insert(tk.END, '\n'.join(lines))
        self.move_list.config(state=tk.DISABLED)

    def update_status(self):
        if self.board.is_checkmate():
            winner = 'Black' if self.board.turn == chess.WHITE else 'White'
            self.status_var.set(f'Checkmate — {winner} wins')
            messagebox.showinfo('Game Over', f'{winner} wins by checkmate')
        elif self.board.is_stalemate():
            self.status_var.set('Stalemate — Draw')
            messagebox.showinfo('Game Over', 'Stalemate — Draw')
        elif self.board.is_insufficient_material():
            self.status_var.set('Draw — insufficient material')
            messagebox.showinfo('Game Over', 'Draw — insufficient material')
        elif self.board.is_check():
            self.status_var.set('Check')
        else:
            self.status_var.set('White to move' if self.board.turn == chess.WHITE else 'Black to move')

    def new_game(self):
        self.board.reset()
        self.selected_square = None
        self.draw_board()
        self.log_moves()
        self.update_status()

    def undo(self):
        if len(self.board.move_stack) > 0:
            self.board.pop()
            self.draw_board()
            self.log_moves()
            self.update_status()

    def flip_board(self):
        self.flipped = not self.flipped
        self.draw_board()


def ch_sq_index(square: int, flipped: bool) -> int:
    idx = list(chess.SQUARES).index(square)
    if flipped:
        return 63 - idx
    return idx
