# Cats and Boxes Solver

This is an automated solver for the **"Cats and Boxes"** sequential movement puzzle by **SmartGames**.

## The Game
The goal of the puzzle is to move the four movable puzzle pieces until every cat on the board is tucked inside a box.

### Core Rules:
1. **Static Cats**: The cats are placed according to the challenge and cannot be moved during gameplay.
2. **Sequential Moves**: You move the puzzle pieces one by one. Each move consists of picking up a piece, optionally rotating it, and placing it in a new valid position.
3. **Valid Placement**: Pieces cannot overlap each other or the cats. Only the "Box" part of a piece can sit on top of a cat; the "Flat" parts cannot.
4. **Goal**: All cats must be covered by boxes in the fewest moves possible.

## Usage

### 1. Visualize a Challenge
To see the initial state of a specific challenge (e.g., Challenge 60):
```bash
python3 main.py 60
```

### 2. Solve a Challenge
To find the shortest path to the solution using the optimized BFS solver:
```bash
python3 solver.py 60
```
The solver will output the step-by-step board configurations and search statistics (states visited vs. unique invalid states ignored).

## Implementation Details
- **Shortest Path**: Uses Breadth-First Search (BFS) to guarantee the minimum number of moves.
- **Priority Search**: Prioritizes states that capture more cats at each step to prune the search space effectively.
- **Optimized Performance**: 
    - Uses **NumPy** for fast grid-state computations.
    - **Precomputed Placements**: Only evaluates positions where pieces actually fit within the 5x5 boundary.
    - **State Caching**: Maintains a cache of both visited valid states and unique invalid states to avoid redundant calculations.

## Solver Efficiency
For the most complex challenge (Level 60), the solver found the perfect **33-move solution** while only needing to visit ~230 valid states, demonstrating high search efficiency.
