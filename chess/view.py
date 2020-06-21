import tkinter as tk
from model import *
import os
from PIL import Image, ImageTk

NORMAL = 0
FLIPPED = 1

class ChessView(tk.Canvas):

    GRID_SIZE = 600
    BLACK_SQUARE = '#138c9e'

    def __init__(self, master):
        super().__init__(master, height=self.GRID_SIZE, width=self.GRID_SIZE)
        self._master = master
        self._cell_size = self.GRID_SIZE // 8
        self._orientation = NORMAL

    def draw_board(self, board):
        self.delete(tk.ALL)
        for index, piece in enumerate(board.get_board()):
            x, y = self.normalise_position((index % 8, index // 8))

            # create the rectangle
            colour = 'white' if (x + y) % 2 == 0 else self.BLACK_SQUARE
            self.create_rectangle(self.bbox((x, y)), fill=colour)

            # draw the piece if needed
            self.draw_piece(piece, (x, y))

    def draw_piece(self, piece, position):
        x, y = position
        colour = 'white' if (x + y) % 2 == 0 else 'black'

        if piece is not None:
            fg = '#000' if colour == 'white' else '#fff'
            self.create_text(self.center((x, y)), text=str(piece), fill=fg)

    def normalise_position(self, position):
        # normalises the position based on the current orientation
        x, y = position
        if self._orientation == NORMAL:
            return x, 7 - y

        return x, y

    def highlight_squares(self, squares, board, fill='#77a2b5'):
        for position in squares:
            x, y = self.normalise_position(position)

            self.create_rectangle(self.bbox((x, y)), fill=fill)

            # draw piece back on
            piece = board.get_piece(position)
            self.draw_piece(piece, (x, y))
    
    def bbox(self, position):
        x, y = position
        result = x, y, x + 1, y + 1
        return [x * self._cell_size for x in result]

    def center(self, position):
        x, y = position
        return [self._cell_size * (p + 0.5) for p in (x, y)]

    def get_position(self, pixel):
        x, y = pixel
        x, y = x // self._cell_size, y // self._cell_size

        return self.normalise_position((x, y))

class ImageChessView(ChessView):

    def __init__(self, master):
        super().__init__(master)
        self._images = {}
        self.load_images()

    def load_images(self):
        folder = 'pieces'
        for filename in os.listdir(folder):
            path = os.path.join(folder, filename)
            image = Image.open(path).resize((self._cell_size, self._cell_size))
            photo = ImageTk.PhotoImage(image)
            
            name = filename.split('.')[0]
            self._images[name] = photo

    def draw_piece(self, piece, position):
        if piece is None:
            return

        if piece.get_side() == WHITE:
            identifier = 'white'
        else:
            identifier = 'black'
        
        identifier += '_' + piece.__class__.__name__.lower()
        self.create_image(self.center(position), image=self._images[identifier])

        

class InfoBar(tk.Frame):
    
    def __init__(self, master):
        super().__init__(master)
        self._turn_label = tk.Label(self, text='WHITE')
        self._turn_label.pack(side=tk.TOP)

        self._selected_label = tk.Label(self, text='?')
        self._selected_label.pack(side=tk.TOP)

    def set_turn(self, turn):
        if turn == WHITE:
            self._turn_label.config(text='WHITE')
        else:
            self._turn_label.config(text='BLACK')

    def set_selected(self, position):
        if position is None:
            self._selected_label.config(text='?')
        else:
            self._selected_label.config(text=str(position))



def main():
    root = tk.Tk()

    board = Board.load('default_board.txt')
    board.display()

    player1 = Player("harry", 60)
    player2 = Player("chat", 60)

    game = ChessGame(player1, player2, board=board)
    knight = board.get_piece((3, 0))
    moves = knight.possible_moves((3, 0), board)
    
    view = ChessView(root)
    view.pack()
    view.draw_board(board)
    view.highlight_squares(moves, board)

    root.mainloop()

if __name__ == '__main__':
    main()