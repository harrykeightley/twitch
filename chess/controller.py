from view import ImageChessView, InfoBar
from model import *
import tkinter as tk

def main():
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()

class ChessApp(object):

    def __init__(self, master):
        super().__init__()

        board = Board.load('default_board.txt')
        #board.display()

        player1 = Player("harry", 60)
        player2 = Player("chat", 60)

        self._game = ChessGame(player1, player2, board=board)
        self._view = ImageChessView(master)
        self._view.pack(side=tk.TOP)

        self._info = InfoBar(master)
        self._info.pack(side=tk.TOP)

        self._view.bind("<Button-1>", self.left_click)

        self._selected_square = None
        self._view.draw_board(board)

    def left_click(self, e):
        pixel = e.x, e.y
        position = self._view.get_position(pixel)
        board = self._game.get_board()
        piece = board.get_piece(position)

        # if this is the first time we've clicked
        if self._selected_square is None and piece is not None:
            self._selected_square = position
            self.highlight_possible_moves(piece, position, board)

        # if we've already clicked somewhere
        else:
            old_piece = board.get_piece(self._selected_square)

            if position == self._selected_square:
                self._selected_square = None
                self._view.draw_board(board)

            # if valid move
            elif position in old_piece.possible_moves(self._selected_square, board):
                side = self._game.get_turn()
                # make the move
                self._game.attempt_move(side, self._selected_square, position)
                # draw the new board
                self._view.draw_board(self._game.get_board())
                self._selected_square = None

            elif piece is not None:
                self._selected_square = position
                self.highlight_possible_moves(piece, position, board)

            else:
                self._selected_square = None
                self._view.draw_board(board)

        self.update_info(self._selected_square)
            


    def update_info(self, position):
        self._info.set_turn(self._game.get_turn())
        self._info.set_selected(self._selected_square)

    def highlight_possible_moves(self, piece, position, board):
        self._view.draw_board(board)
        possible_moves = piece.possible_moves(position, board)
        self._view.highlight_squares(possible_moves, board)





if __name__ == '__main__':
    main()