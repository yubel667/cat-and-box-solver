from enum import Enum
from typing import List

class Location:
    def __init__(self, y, x):
        self.y=y
        self.x=x

    # rotate the location.
    def rotate(self) -> "Location":
        return Location(-self.x, self.y)

class CellType(Enum):
    EMPTY = 1
    BOX = 2

class Cell:
    def __init__(self, loc: Location, t: CellType):
       self.location = loc
       self.t = t

    # rotation relative axis.
    def rotate(self) -> "Cell":
       return Cell(self.location.rotate(), self.t)

class Piece:
    def __init__(self, id: int, cells: List[Cell]):
        self.id = id
        self.cells = cells

    # rotate each cell by 90 degree and return a new Piece with its new orientation.
    def rotate(self) -> "Piece":
        new_cells = [
            cell.rotate() for cell in self.cells
        ]
        return Piece(self.id, new_cells)

# all pieces ranges are within -1~1 so we could easily ensure after rotation they are still within the range.
# this makes testing them much easier.
PIECES = [
    Piece(0, 
        [Cell(Location(-1,-1), CellType.BOX),
        Cell(Location(-1,0), CellType.EMPTY),
        Cell(Location(0,0), CellType.EMPTY),
        Cell(Location(1,0), CellType.EMPTY),
        Cell(Location(0,1), CellType.BOX)]
    ),
    Piece(1,
        [Cell(Location(0,-1), CellType.BOX),
        Cell(Location(0,0), CellType.EMPTY),
        Cell(Location(0,1), CellType.EMPTY),
        Cell(Location(1,-1), CellType.EMPTY)]
    ),
    Piece(2,
       [Cell(Location(0,0), CellType.BOX),
        Cell(Location(0,1), CellType.EMPTY),
        Cell(Location(0,-1), CellType.EMPTY),
        Cell(Location(1,0), CellType.EMPTY)]
    ),
    Piece(3,
        [Cell(Location(0,0), CellType.BOX),
        Cell(Location(0,1), CellType.EMPTY),
        Cell(Location(0,-1), CellType.EMPTY),
        Cell(Location(1,1), CellType.EMPTY)]
    )
]

# build all id & 4 orientation variant of the piece.
def build_piece_map():
    piece_map = {}
    for piece in PIECES:
        current = piece
        for orientation in range(4):
            piece_map[piece.id, orientation] = current
            current = current.rotate()
    return piece_map

PIECE_MAP = build_piece_map()
def get_piece(id: int, orientation: int) -> Piece:
    return PIECE_MAP[id, orientation]

# cat only cares about location
class Cat:
    def __init__(self, loc: Location):
        self.loc = loc

# a shorthand for the piece where we find its place. all pieces is relative to the loc and has orientation.
class PiecePlace:
    def __init__(self, id: int, loc: Location, orientation: int):
        self.id = id
        self.loc = loc
        self.orientation = orientation

    # Unique identifier representing the piece place
    def get_identifer(self):
        # This works because all the numbers are within range 0~9 (given a valid piece)
        # note that the loc can only be 0~4 because we always use the central piece.
        # oriential can only be 0 to 4
        return f"{self.id}{self.loc.y}{self.loc.x}{self.orientation}"

# representing the current board setup. it should be immutable.
class BoardSetup:
    def __init__(self, cats: List[Cat]):
        self.cats = cats

class BoardState(Enum):
    CAT = 1
    CAT_IN_BOX = 2
    BOX = 3
    EMPTY = 4 # still occupied by a piece
    NULL = 5 # truly nothing.

# Overall state for the whole board.
class FullBoardState(Enum):
    VALID = 1
    INVALID = 2
    SOLVED = 3

class Board:
    def __init__(self, setup: BoardSetup, pieces: List[PiecePlace]):
        self.setup = setup
        self.pieces = pieces
        # Only allow 0 to 4 pieces, and piece id need to be unique.
        assert len(self.pieces) <= 4
        assert len(set(p.id for p in self.pieces)) == len(self.pieces) 
        self.pieces.sort(key = lambda p: p.id)
        self.board_state, self.cats_captured = self.compute_board_state()

    # Get unique identifer for the board state for DFS purpose to avoid stepping into the same state again.
    def get_board_identifier(self):
        return "".join(p.get_identifer() for p in self.pieces)
    
    # return a new board with piece of id removed.
    def remove_piece(self, id:int):
        assert(len(self.pieces)) >= 1
        new_pieces = [p for p in self.pieces if p.id != id]
        assert len(new_pieces) +1 == len(self.pieces)
        return Board(self.setup, new_pieces)
        
    def add_piece(self, piece: PiecePlace):
        assert(len(self.pieces)) <= 3
        for p in self.pieces:
            assert p.id != piece.id
        # It would do sorting internally.
        return Board(self.setup, [*self.pieces, piece])

    # check whether the board state is legal.
    def compute_board_state(self) -> (FullBoardState, int):
        all_states = []
        for j in range(5):
            all_states.append([BoardState.NULL for i in range(5)])
        num_cats = len(self.setup.cats)
        cat_in_box = 0
        # first place all cats.
        for cat in self.setup.cats:
            all_states[cat.loc.y][cat.loc.x] = BoardState.CAT
        # put down all pieces.
        for piece in self.pieces:
            actual_piece = PIECE_MAP[piece.id, piece.orientation]
            offset = piece.loc
            for cell in actual_piece.cells:
                y = offset.y + cell.location.y
                x = offset.x + cell.location.x
                if not (0<=y<5 and 0<=x<5):
                    # piece out of boundary.
                    return FullBoardState.INVALID, 0
                t = cell.t
                current_state = all_states[y][x]
                # if it is box, can either be CAT or NULL.
                # if it is empty, must be NULL
                if t == CellType.BOX:
                    if current_state == BoardState.CAT:
                        cat_in_box += 1
                        all_states[y][x] = BoardState.CAT_IN_BOX
                    elif current_state == BoardState.NULL:
                        all_states[y][x] = BoardState.BOX               
                    else:
                        return FullBoardState.INVALID, 0
                else:
                    assert t == CellType.EMPTY
                    if current_state == BoardState.NULL:
                        all_states[y][x] = BoardState.EMPTY
                    else:
                        return FullBoardState.INVALID, 0
        # everything is placed, so it is a success.
        if cat_in_box == num_cats:
            return FullBoardState.SOLVED, cat_in_box
        else:
            return FullBoardState.VALID, cat_in_box

    # string for visualizing the board.
    def debug_string(self) -> str:
        # 9x9 buffer to update info on.
        buffer = []
        for j in range(9):
            buffer.append([' ' for i in range(9)])
        # draw cats
        for cat in self.setup.cats:
            buffer[cat.loc.y * 2][cat.loc.x * 2] = 'c'
        # draw pieces.
        for piece in self.pieces:
            actual_piece = PIECE_MAP[piece.id, piece.orientation] 
            # find locations where this pieces belong to.
            offset = piece.loc
            # draw pieces.
            piece_cells = []
            for cell in actual_piece.cells:
                y = offset.y + cell.location.y
                x = offset.x + cell.location.x
                t = cell.t
                if (not (0<=y<5 and 0<=x<5)):
                    continue # illegal placement, discard and don't draw at all.
                piece_cells.append((y, x))
                if t == CellType.BOX:
                    # there may be a cat, then we would output 'C' instead.
                    if buffer[y * 2][x * 2] == 'c':
                        buffer[y * 2][x * 2] = 'C'
                    elif buffer[y * 2][x * 2] == ' ':
                        buffer[y * 2][x * 2] = 'B'
                    else:
                        buffer[y * 2][x * 2] = '?' # error state.
                else:
                    assert t == CellType.EMPTY
                    if buffer[y * 2][x * 2] == ' ':
                        buffer[y * 2][x * 2] = '*'
                    else:
                        buffer[y * 2][x * 2] = '?' # error state.

            # draw connections.
            # check each pair, if they are connected, draw a "-" or "|".
            for p1 in piece_cells:
                for p2 in piece_cells:
                    # horizontal connection
                    if p1[0] == p2[0] and p1[1] + 1 == p2[1]:
                        buffer[p1[0] * 2][p1[1] * 2 + 1] = '-'
                    # vertical connection
                    elif p1[0] + 1 == p2[0] and p1[1] == p2[1]:
                        buffer[p1[0] * 2 + 1][p1[1] * 2] = '|'
        # assemble everything.
        if self.board_state == FullBoardState.INVALID:
            output = "+<Invalid>+\n"
        elif self.board_state == FullBoardState.SOLVED:
            output = "+<Solved>-+\n"
        else:
            output = "+---------+\n"
        for j in range(9):
            output += "|"
            output += "".join(buffer[j])
            output += "|\n"
        output += "+---------+\n"
        return output

