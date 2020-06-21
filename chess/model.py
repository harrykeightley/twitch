# Models used in the chess game
from pprint import pprint

GRID_SIZE = 8
WHITE = 0
BLACK = 1

EMPTY_BOARD = (None,) * GRID_SIZE ** 2


class Board(object):
    
    def __init__(self, board=EMPTY_BOARD):
        self._board = board

    def get_board(self):
        return self._board

    @staticmethod
    def load(file):
        raw_lines = []
        with open(file) as board_file:
            for line in board_file:
                raw_lines.append(line.split(';'))
        raw_pieces = [[Piece.load(x) for x in y] for y in raw_lines]
        raw_pieces.reverse()

        result = []
        for x in raw_pieces:
            result.extend(x)
        return Board(board=tuple(result))
        

    @staticmethod
    def position_to_index(position):
        x, y = position
        return y * GRID_SIZE + x # might have to think about this

    @staticmethod
    def notation_to_position(notation):
        pass

    def set_position(self, position, piece):
        index = Board.position_to_index(position)
        return self._board[:index] + (piece,) + self._board[index + 1:]

    def get_piece(self, position):
        """ (Tuple<Piece, Player>) Gets information about the supplied position """
        return self._board[Board.position_to_index(position)]

    def move(self, from_position, to_position):
        """ (Board) Return the resultant board from moving the given position into the other """
        piece = self.get_piece(from_position)

        # promote pawns to queens on 8th rank
        if self.is_promoting(from_position, to_position):
            piece = Queen(piece.get_side())

        intermediate = Board(board=self.set_position(to_position, piece))
        result = intermediate.set_position(from_position, None)

        piece.set_moved(True)
        return Board(board=result)

    def castle(self, side, long):
        is_white = True if side == WHITE else False
        rank = {True: 0, False: 7}
        y = rank.get(is_white, 0)

        king_position = (4, y)
        rook_position = (rank[long], y)

        king_delta = (-2, 0) if long else (2, 0)
        rook_delta = (1, 0) if long else (-1, 0)
        next_king_position = Board.add_position(king_position, king_delta)
        next_rook_position = Board.add_position(next_king_position, rook_delta)

        intermediate = self.move(king_position, next_king_position)
        return intermediate.move(rook_position, next_rook_position)

    def is_castling(self, from_position, to_position):
        # Really stupid implementation
        piece = self.get_piece(from_position)
        if not isinstance(piece, King):
            return False, None

        dx, dy = Board.subtract_position(to_position, from_position)
        if dx == 2:
            return True, piece.get_side(), False
        elif dx == -2:
            return True, piece.get_side(), True

        return False, None

    def can_castle(self, side, long):
        is_white = True if side == WHITE else False
        rank = {True: 0, False: 7}
        y = rank.get(is_white, 0)

        king_position = (4, y)
        rook_position = (rank[long], y)

        king = self.get_piece(king_position)
        if not isinstance(king, King) or king.has_moved():
            return False

        rook = self.get_piece(rook_position)
        if not isinstance(rook, Rook) or rook.has_moved():
            return False

        # check king in check
        side = WHITE if is_white else BLACK
        if self.is_in_check(side):
            return False
        
        # get squares between them
        if long:
            xs = list(range(1, 4))
        else:
            xs = list(range(5, 7))
        squares = [(x, y) for x in xs]

        # check nothing between them
        for square in squares:
            if self.get_piece(square) is not None:
                return False

        # check no move of king would be in check
        for square in squares:
            
            # move king there
            if square[0] == 1: # ignore this square
                continue

            intermediate = self.move(king_position, square)
            king.set_moved(False)
            # check if in check
            if intermediate.is_in_check(side):
                return False

        return True
    
    def is_promoting(self, from_position, to_position):
        piece = self.get_piece(from_position)
        if piece is None or not isinstance(piece, Pawn):
            return False

        side = piece.get_side()
        return to_position[1] == 7 - side * 7

    
        


    def is_in_check(self, side):
        king_position = None
        for index, piece in enumerate(self._board):
            if isinstance(piece, King) and piece.get_side() == side: 
                king_position = index % GRID_SIZE, index // GRID_SIZE
                king = piece

        if king_position is None:
            return False

        # check for danger squares
        danger_squares = []
        for delta in king.get_deltas(king_position):
            # goes out in line of sight from the king in each direction
            danger_squares.extend(king.follow_delta(king_position, delta, self))

        # check king line of sight
        for square in danger_squares:
            piece = self.get_piece(square)
            if piece is None or piece.get_side() == side:
                continue
            
            # if the piece is attacking our king
            if king_position in piece.possible_moves(square, self):
                return True


        # imagine there is a knight on the king and see if any in possible moves are an enemy knight
        knight = Knight(side)
        for square in knight.possible_moves(king_position, self):
            piece = self.get_piece(square)
            if piece is None:
                continue
            if isinstance(piece, Knight) and piece.get_side() != side:
                return True

        return False

    @staticmethod
    def is_valid_position(position):
        x, y = position
        return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

    @staticmethod
    def add_position(position, delta):
        x, y = position
        dx, dy = delta
        return x + dx, y + dy

    @staticmethod
    def subtract_position(position, other):
        x, y = position
        dx, dy = other
        return x - dx, y - dy

    def display(self):
        result = []
        for row in range(GRID_SIZE):
            start = row * GRID_SIZE
            end = (row + 1) * GRID_SIZE
            result.append([str(x) for x in self._board[start:end]])
        result.reverse()
        pprint(result)


class Piece(object):

    def __init__(self, move_deltas, side, jumps=False):
        self._deltas = move_deltas
        self._side = side
        self._jumps = jumps
        self._has_moved = False

    def get_deltas(self, position):
        return self._deltas

    def has_moved(self):
        return self._has_moved

    def set_moved(self, moved):
        self._has_moved = moved

    def get_side(self):
        return self._side
    
    def possible_moves(self, position, board):
        result = []
        deltas = self.get_deltas(position)
        #TODO REMOVE print('deltas:', deltas)
        for delta in deltas:
            if self._jumps:
                next_position = Board.add_position(position, delta)
                if not Board.is_valid_position(next_position):
                    continue
                piece = board.get_piece(next_position)
                if piece is None or piece.get_side() != self._side:
                    result.append(next_position)

            else:
                result.extend(self.follow_delta(position, delta, board))
        return result
    
    def follow_delta(self, position, delta, board):
        result = []
        next_position = Board.add_position(position, delta)

        if not Board.is_valid_position(next_position):
            return result

        piece = board.get_piece(next_position)
        # keep extending tell we reach a piece
        if piece is None:
            result.append(next_position)
            result.extend(self.follow_delta(next_position, delta, board))
        # add the piece that could be taken if it's on the enemy side
        elif piece.get_side() != self._side:
            result.append(next_position)

        return result

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return str(self)

    @staticmethod
    def load(x):
        CLASS_MAP = {
            'K': King,
            'N': Knight,
            'p': Pawn,
            'R': Rook,
            'Q': Queen,
            'B': Bishop,
        }
        try:
            identifier, side = x.split(':')
            side = int(side)
        except ValueError:
            return None

        return CLASS_MAP[identifier](side)


class Player(object):

    def __init__(self, name, time):
        self._name = name
        self._starting_time = time
        self._time = time

    def get_name(self):
        return self._name

    def get_time(self):
        return self._time

    def change_time(self, delta):
        self._time += delta
        self._time = max(0, min(self._time, self._starting_time))

    def has_lost_on_time(self):
        return self._time == 0


class ChessGame(object):
    
    def __init__(self, white, black, board=None):
        self._white = white
        self._black = black
        self._turn = WHITE
        self._board = board
        if board is None:
            self._board = Board(board=EMPTY_BOARD)

    def get_turn(self):
        return self._turn

    def get_board(self):
        return self._board

    def toggle_turn(self):
        self._turn = (self._turn + 1) % len([WHITE, BLACK])

    def can_move(self, side, from_position, to_position):
        # check if proper turn
        if side != self._turn:
            return False

        piece = self._board.get_piece(from_position)
        if piece is None:
            return False

        # check if own piece at that position
        if piece.get_side() != side:
            return False
        
        # check if valid move
        #print('sex', piece.possible_moves(from_position, self._board))
        if to_position not in piece.possible_moves(from_position, self._board):
            return False

        next_state = self._board.move(from_position, to_position)
        # check if in check
        if next_state.is_in_check(side):
            return False

        return True

    def attempt_move(self, side, from_position, to_position):
        if not self.can_move(side, from_position, to_position):
            print("Invalid move")
            return 
        
        # TODO change to keep track of all past states

        castling, *args = self._board.is_castling(from_position, to_position)
        if castling:
            self._board = self._board.castle(*args)
        else:
            self._board = self._board.move(from_position, to_position)
        self.toggle_turn()



################## PIECES ###################

class King(Piece):
    _DELTAS = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
    
    def __init__(self, side):
        super().__init__(move_deltas=self._DELTAS, side=side, jumps=True)

    def possible_moves(self, position, board):
        result = super().possible_moves(position, board)
        
        if board.can_castle(self._side, long=True):
            result.append(Board.add_position(position, (-2, 0)))

        if board.can_castle(self._side, long=False):
            result.append(Board.add_position(position, (2, 0)))
        
        return result

    def __str__(self):
        return f'K:{self._side}'
    

class Knight(Piece):
    _DELTAS = [(1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1)]
    
    def __init__(self, side):
        super().__init__(move_deltas=self._DELTAS, side=side, jumps=True)

    def __str__(self):
        return f'N:{self._side}'

class Queen(Piece):

    _DELTAS = [(1, 1), (1, 0), (1, -1), (0, 1), (0, -1), (-1, 1), (-1, 0), (-1, -1)]
    
    def __init__(self, side):
        super().__init__(move_deltas=self._DELTAS, side=side, jumps=False)

    def __str__(self):
        return f'Q:{self._side}'


class Rook(Piece):

    _DELTAS = [(1, 0), (0, 1), (0, -1), (-1, 0)]
    
    def __init__(self, side):
        super().__init__(move_deltas=self._DELTAS, side=side, jumps=False)

    def __str__(self):
        return f'R:{self._side}'

class Bishop(Piece):

    _DELTAS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    
    def __init__(self, side):
        super().__init__(move_deltas=self._DELTAS, side=side, jumps=False)

    def __str__(self):
        return f'B:{self._side}'


class Pawn(Piece):
    _DELTAS = [(0, 1)]

    def __init__(self, side):
        super().__init__(move_deltas=self._DELTAS, side=side, jumps=True)

    def get_deltas(self, position):
        result = self._deltas[:]
        # add extra move at start
        if self._side == WHITE and position[1] == 1:
            result.append((0, 2))
        if self._side == BLACK and position[1] == 6:
            result.append((0, 2))

        result.extend([(1, 1), (-1, 1)])
        
        if self._side == BLACK:
            result = [(x, -y) for (x, y) in result]

        return result

    def possible_moves(self, position, board):
        result = []
        deltas = self.get_deltas(position)
        #TODO REMOVE print('deltas:', deltas)
        for delta in deltas:
            next_position = Board.add_position(position, delta)
            if not Board.is_valid_position(next_position):
                continue

            piece = board.get_piece(next_position)

            # if diagonal make sure enemy piece there
            if next_position[0] != position[0]:
                if piece is None:
                    continue
                if piece.get_side() != self._side:
                    result.append(next_position)

            if piece is not None:
                continue
            
            # if double jump make sure no piece in the way
            if abs(delta[1]) == 2:
                partial_delta = delta[0], round(delta[1] / 2)
                middle_position = Board.add_position(position, partial_delta)
                if board.get_piece(middle_position) is not None:
                    continue

            
            result.append(next_position)
           
        return result

    def __str__(self):
        return f'p:{self._side}'


if __name__ == "__main__":
    board = Board.load('default_board.txt')
    board.display()

    player1 = Player("harry", 60)
    player2 = Player("chat", 60)

    game = ChessGame(player1, player2, board=board)
    game.attempt_move(WHITE, (0, 1), (0, 3))
    game.attempt_move(WHITE, (0, 1), (0, 3))
    game.attempt_move(WHITE, (0, 3), (0, 2))

    game.attempt_move(BLACK, (3, 6), (3, 5))

    game.get_board().display()