import tkinter as tk
from .model import *

class Chess(object):

    def __init__(self, master):
        self._master = master

        board = Board.load('default_board.txt')
        board.display()

        player1 = Player("harry", 60)
        player2 = Player("chat", 60)
        self._model = ChessGame



def main():
    root = tk.Tk()

    
    Chess(root)
    root.mainloop()

if __name__ == '__main__':
    main()