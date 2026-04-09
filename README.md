# Cats and Boxes Solver

This is an automated solver for the **"Cats and Boxes"** sequential movement puzzle by **SmartGames**.

## The Game
The goal of the puzzle is to move the four movable puzzle pieces until every cat on the board is tucked inside a box.

### Core Rules:
1. **Static Cats**: The cats are placed according to the challenge and cannot be moved during gameplay.
2. **Sequential Moves**: You move the puzzle pieces one by one. Each move consists of picking up a piece, optionally rotating it, and placing it in a new valid position.
3. **Valid Placement**: Pieces cannot overlap each other or the cats. Only the "Box" part of a piece can sit on top of a cat; the "Flat" parts cannot.
4. **Goal**: All cats must be covered by boxes in the fewest moves possible.

## Input Format
Challenges are stored as ASCII text files in the `questions/` directory.

### Example (`questions/1.txt`):
- `c`: Represents an uncovered cat.
- `B`: Represents a "Box" part of a piece.
- `*`: Represents a "Flat" part of a piece.
- `-` and `|`: Represent connections between cells of the same piece.
- `C`: Represents a cat covered by a box.

```text
+---------+
|c * *-B c|
|  |   |  |
|B-* c *  |
|  |   |  |
|  *-B *  |
|         |
|c * *-B-*|
|  |     ||
|*-B-* c *|
+---------+
```

## Usage


### Solve a Challenge
To find the shortest path to the solution using the optimized BFS solver:
```bash
python3 solver.py 1
```

### Sample Solver Output (Level 1)
```text
Starting puzzle from question 1...
+---------+
|c * *-B c|
|  |   |  |
|B-* c *  |
|  |   |  |
|  *-B *  |
|         |
|c * *-B-*|
|  |     ||
|*-B-* c *|
+---------+

Searching for the shortest solution with optimized search...

SUCCESS! Found the shortest solution in 4 moves.
Step 0 (Cats captured: 0):
+---------+
|c * *-B c|
|  |   |  |
|B-* c *  |
|  |   |  |
|  *-B *  |
|         |
|c * *-B-*|
|  |     ||
|*-B-* c *|
+---------+

Step 1 (Cats captured: 2):
+---------+
|C-* *-B c|
|  |   |  |
|  *-C *  |
|  |   |  |
|  *   *  |
|         |
|c * *-B-*|
|  |     ||
|*-B-* c *|
+---------+

Step 2 (Cats captured: 3):
+---------+
|C-*   *-C|
|  |     ||
|  *-C   *|
|  |     ||
|  *     *|
|         |
|c * *-B-*|
|  |     ||
|*-B-* c *|
+---------+

Step 3 (Cats captured: 4):
+---------+
|C-*   *-C|
|  |     ||
|  *-C   *|
|  |     ||
|* *     *|
||        |
|C-* *-B-*|
||       ||
|*     c *|
+---------+

Step 4 (Cats captured: 5):
+<Solved>-+
|C-*   *-C|
|  |     ||
|  *-C   *|
|  |     ||
|* *     *|
||        |
|C-* *    |
||   |    |
|*   *-C-*|
+---------+

------------------------------
Search Statistics:
  Valid states visited:   45
  Unique Invalid states:  4404
------------------------------
```

## Implementation Details
- **Shortest Path**: Uses Breadth-First Search (BFS) to guarantee the minimum number of moves.
- **Priority Search**: Prioritizes states that capture more cats at each step.
- **Optimized Performance**: 
    - Uses **NumPy** for fast grid-state computations.
    - **Precomputed Placements**: Only evaluates positions where pieces actually fit.
    - **State Caching**: Maintains a cache of both visited valid states and unique invalid states.
