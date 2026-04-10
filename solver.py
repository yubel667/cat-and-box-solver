import sys
import os
import heapq
from board import Board, PiecePlace, Location, FullBoardState, VALID_PLACEMENTS
from board_parser import parse_board_string

def get_neighbors(current_board: Board, stats: dict, visited: dict, invalid_visited: set):
    """
    Generates all possible boards reachable by moving exactly one piece 
    to a new valid position/orientation.
    Uses precomputed VALID_PLACEMENTS and caches invalid states.
    """
    neighbors = []
    # Try moving each of the pieces currently on the board
    for i in range(len(current_board.pieces)):
        piece_to_move = current_board.pieces[i]
        # Get the other pieces that will remain stationary
        other_pieces = current_board.pieces[:i] + current_board.pieces[i+1:]
        
        for orientation in range(4):
            # Only iterate over locations where this piece/orientation actually fits in a 5x5 grid
            for y, x in VALID_PLACEMENTS[piece_to_move.id, orientation]:
                # Skip if it's the exact same position and orientation
                if (y == piece_to_move.loc.y and 
                    x == piece_to_move.loc.x and 
                    orientation == piece_to_move.orientation):
                    continue
                
                # We can construct a board identifier BEFORE creating the Board object to check caches
                new_place = PiecePlace(piece_to_move.id, Location(y, x), orientation)
                temp_pieces = sorted(other_pieces + [new_place], key=lambda p: p.id)
                ident = "".join(p.get_identifer() for p in temp_pieces)
                
                if ident in visited or ident in invalid_visited:
                    continue
                
                # Create a new board with the moved piece
                new_board = Board(current_board.setup, temp_pieces)
                
                if new_board.board_state == FullBoardState.INVALID:
                    invalid_visited.add(ident)
                    stats['invalid_count'] += 1
                else:
                    neighbors.append(new_board)
    return neighbors

def solve_prioritized_bfs(start_board: Board):
    """
    Performs a Prioritized Breadth-First Search with optimized search space.
    """
    stats = {
        'visited_count': 0,
        'invalid_count': 0
    }
    
    # Priority Queue stores (path_length, -cats_captured, tie_breaker, current_board, path)
    counter = 0
    pq = [(0, -start_board.cats_captured, counter, start_board, [start_board])]
    visited = {start_board.get_board_identifier(): 0} 
    invalid_visited = set()
    
    while pq:
        path_len, neg_cats, _, current_board, path = heapq.heappop(pq)
        stats['visited_count'] += 1
        
        if current_board.board_state == FullBoardState.SOLVED:
            return path, stats
            
        if path_len > visited.get(current_board.get_board_identifier(), float('inf')):
            continue

        for neighbor in get_neighbors(current_board, stats, visited, invalid_visited):
            ident = neighbor.get_board_identifier()
            new_path_len = path_len + 1
            
            if new_path_len < visited.get(ident, float('inf')):
                visited[ident] = new_path_len
                counter += 1
                heapq.heappush(pq, (new_path_len, -neighbor.cats_captured, counter, neighbor, path + [neighbor]))
                
    return None, stats

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 solver.py <question_number> [--gui]")
        sys.exit(1)
        
    question_num = sys.argv[1]
    
    use_gui = False
    if len(sys.argv) > 2 and sys.argv[2] == "--gui":
        use_gui = True
        
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
        
        print("Searching for the shortest solution with optimized search...")
        solution_path, stats = solve_prioritized_bfs(start_board)
        
        if solution_path:
            print(f"\nSUCCESS! Found the shortest solution in {len(solution_path) - 1} moves.")
            for i, board in enumerate(solution_path):
                print(f"Step {i} (Cats captured: {board.cats_captured}):")
                print(board.debug_string())
                
            if use_gui:
                try:
                    from ui import play_animation
                    play_animation(solution_path)
                except ImportError:
                    print("Pygame is required for the GUI. Run `pip install pygame`.")
        else:
            print("\nNo solution found.")
            
        print("-" * 30)
        print("Search Statistics:")
        print(f"  Valid states visited:   {stats['visited_count']}")
        print(f"  Unique Invalid states:  {stats['invalid_count']}")
        print("-" * 30)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
