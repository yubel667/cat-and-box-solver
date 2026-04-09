
import unittest
from board import Board, BoardSetup, PiecePlace, Cat,Location

class BoardTest(unittest.TestCase):

    def test_board_debug_string(self):
        # start with an empty board
        setup = BoardSetup(
            [
                Cat(Location(0,0)),
                Cat(Location(0,4)),
                Cat(Location(1,2)),
                Cat(Location(3,0)),
                Cat(Location(4,3))
            ]
        )
        board = Board(setup, [
            PiecePlace(0, Location(1,1), 2),
            PiecePlace(1, Location(1,3), 3),
            PiecePlace(2, Location(4,1), 2),
            PiecePlace(3, Location(3,3), 0)
        ])

        self.assertEqual(board.get_board_identifier(), "0112113324123330")

        debug_string = board.debug_string()
        print("debug board state:\n"+debug_string)

        with open("questions/1.txt", "r") as f:
            expected = f.read()

        actual_lines = debug_string.strip().split("\n")
        expected_lines = expected.strip().split("\n")
        self.assertEqual(len(actual_lines), len(expected_lines))
        for actual_line, expected_line in zip(actual_lines, expected_lines):
            self.assertEqual(actual_line, expected_line)

    def test_all_pieces(self):
        return # disable this manual test.
        empty_setup = BoardSetup([])
        for piece_id in range(4): 
            for orientation in range(4):          
                board = Board(empty_setup, [PiecePlace(piece_id, Location(2,2), orientation)])
                print(f"p={piece_id},o={orientation}\n"+board.debug_string()+"\n\n")



if __name__ == "__main__":
    unittest.main()
