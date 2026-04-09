import sys
import os
from board_parser import parse_board_string

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <question_number>")
        sys.exit(1)
        
    question_num = sys.argv[1]
    file_path = f"questions/{question_num}.txt"
    
    if not os.path.exists(file_path):
        print(f"Error: Question file '{file_path}' not found.")
        sys.exit(1)
        
    try:
        with open(file_path, "r") as f:
            board_str = f.read()
            
        board = parse_board_string(board_str)
        print(f"Board representation for question {question_num}:")
        print(board.debug_string())
        
    except ValueError as e:
        print(f"Error parsing board: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
