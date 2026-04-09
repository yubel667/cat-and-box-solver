import unittest
from board import Board
from board_parser import parse_board_string

class TestBoardParser(unittest.TestCase):
    def test_parse_question_1(self):
        with open("questions/1.txt", "r") as f:
            board_str = f.read()
            
        board = parse_board_string(board_str)
        
        # Round-trip verification
        # The debug_string() output might have different header if it's solved, but question 1 is not solved.
        self.assertEqual(board.debug_string().strip(), board_str.strip())
        
        # Verify component counts
        self.assertEqual(len(board.setup.cats), 5)
        self.assertEqual(len(board.pieces), 4)
        
        # Verify piece IDs are unique 0, 1, 2, 3
        ids = sorted([p.id for p in board.pieces])
        self.assertEqual(ids, [0, 1, 2, 3])

if __name__ == "__main__":
    unittest.main()
