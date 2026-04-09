import sys
import os
from board import Board, PiecePlace, Location, FullBoardState
from board_parser import parse_board_string

def get_neighbors(current_board: Board):
    """
    Generates all possible boards reachable by moving exactly one piece 
    to a new valid position/orientation.
    """
    neighbors = []
    # Try moving each of the pieces currently on the board
    for i in range(len(current_board.pieces)):
        piece_to_move = current_board.pieces[i]
        # Get the other pieces that will remain stationary
        other_pieces = current_board.pieces[:i] + current_board.pieces[i+1:]
        
        for y in range(5):
            for x in range(5):
                for orientation in range(4):
                    # Skip if it's the exact same position and orientation
                    if (y == piece_to_move.loc.y and 
                        x == piece_to_move.loc.x and 
                        orientation == piece_to_move.orientation):
                        continue
                        
                    new_place = PiecePlace(piece_to_move.id, Location(y, x), orientation)
                    
                    # Create a new board with the moved piece
                    # The constructor handles validity checking and state computation
                    new_board = Board(current_board.setup, other_pieces + [new_place])
                    
                    if new_board.board_state != FullBoardState.INVALID:
                        neighbors.append(new_board)
    return neighbors

def solve_dfs(start_board: Board):
    """
    Performs an iterative Depth-First Search to find a solution.
    Returns the sequence of boards from start to solution, or None if not found.
    """
    # stack stores (current_board, path_to_current_board)
    stack = [(start_board, [start_board])]
    visited = {start_board.get_board_identifier()}
    
    while stack:
        current_board, path = stack.pop()
        
        if current_board.board_state == FullBoardState.SOLVED:
            return path
            
        for neighbor in get_neighbors(current_board):
            ident = neighbor.get_board_identifier()
            if ident not in visited:
                visited.add(ident)
                stack.append((neighbor, path + [neighbor]))
                
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 solver.py <question_number>")
        sys.exit(1)
        
    question_num = sys.argv[1]
    file_path = f"questions/{question_num}.txt"
    
    if not os.path.exists(file_path):
        print(f"Error: Question file '{file_path}' not found.")
        sys.exit(1)
        
    try:
        with open(file_path, "r") as f:
            board_str = f.read()
            
        start_board = parse_board_string(board_str)
        print(f"Starting puzzle from question {question_num}...")
        print(start_board.debug_string())
        
        print("Searching for a solution (this may take a moment)...")
        solution_path = solve_dfs(start_board)
        
        if solution_path:
            print(f"\nSUCCESS! Found a solution in {len(solution_path) - 1} moves.")
            for i, board in enumerate(solution_path):
                print(f"Step {i}:")
                print(board.debug_string())
        else:
            print("\nNo solution found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
