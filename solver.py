import sys
import os
import heapq
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
                    new_board = Board(current_board.setup, other_pieces + [new_place])
                    
                    if new_board.board_state != FullBoardState.INVALID:
                        neighbors.append(new_board)
    return neighbors

def solve_prioritized_bfs(start_board: Board):
    """
    Performs a Prioritized Breadth-First Search to find the shortest path.
    Prioritizes states where more cats are captured first.
    """
    # Priority Queue stores (path_length, -cats_captured, tie_breaker, current_board, path)
    # tie_breaker is used to avoid comparing Board objects if priorities are equal
    counter = 0
    pq = [(0, -start_board.cats_captured, counter, start_board, [start_board])]
    visited = {start_board.get_board_identifier(): 0} # map ident to shortest path found
    
    while pq:
        path_len, neg_cats, _, current_board, path = heapq.heappop(pq)
        
        if current_board.board_state == FullBoardState.SOLVED:
            return path
            
        if path_len > visited.get(current_board.get_board_identifier(), float('inf')):
            continue

        for neighbor in get_neighbors(current_board):
            ident = neighbor.get_board_identifier()
            new_path_len = path_len + 1
            
            if new_path_len < visited.get(ident, float('inf')):
                visited[ident] = new_path_len
                counter += 1
                heapq.heappush(pq, (new_path_len, -neighbor.cats_captured, counter, neighbor, path + [neighbor]))
                
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
        
        print("Searching for the shortest solution with cat-capture priority...")
        solution_path = solve_prioritized_bfs(start_board)
        
        if solution_path:
            print(f"\nSUCCESS! Found the shortest solution in {len(solution_path) - 1} moves.")
            for i, board in enumerate(solution_path):
                print(f"Step {i} (Cats captured: {board.cats_captured}):")
                print(board.debug_string())
        else:
            print("\nNo solution found.")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
