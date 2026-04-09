from board import (
    Board, BoardSetup, PiecePlace, Cat, Location, 
    PIECE_MAP, CellType, PIECES
)

def parse_board_string(s: str) -> Board:
    lines = s.strip().split("\n")
    if len(lines) != 11:
        raise ValueError(f"Invalid board string: must have 11 lines, got {len(lines)}")
    
    # Extract the 9x9 buffer
    buffer = []
    for line in lines[1:10]:
        # Each line should be |xxxxxxxxx|
        content = line[1:10]
        if len(content) < 9:
            content = content.ljust(9)
        buffer.append(content)
        
    cats = []
    piece_cells = set()
    for y in range(5):
        for x in range(5):
            char = buffer[y*2][x*2]
            if char == 'c':
                cats.append(Cat(Location(y, x)))
            elif char in ('B', '*'):
                piece_cells.add((y, x))
            elif char == 'C':
                # User said cats are not in boxes initially, but handle for completeness
                cats.append(Cat(Location(y, x)))
                piece_cells.add((y, x))
    
    setup = BoardSetup(cats)
    processed_cells = set()
    piece_places = []
    
    # Sort cells for deterministic processing
    for y, x in sorted(list(piece_cells)):
        if (y, x) in processed_cells:
            continue
            
        # Find connected component using the connection characters in the buffer
        component = set()
        stack = [(y, x)]
        while stack:
            cy, cx = stack.pop()
            if (cy, cx) in component:
                continue
            component.add((cy, cx))
            processed_cells.add((cy, cx))
            
            # Check 4 neighbors and their connections
            # Right
            if cx < 4 and buffer[cy*2][cx*2+1] == '-' and (cy, cx+1) in piece_cells:
                stack.append((cy, cx+1))
            # Left
            if cx > 0 and buffer[cy*2][cx*2-1] == '-' and (cy, cx-1) in piece_cells:
                stack.append((cy, cx-1))
            # Down
            if cy < 4 and buffer[cy*2+1][cx*2] == '|' and (cy+1, cx) in piece_cells:
                stack.append((cy+1, cx))
            # Up
            if cy > 0 and buffer[cy*2-1][cx*2] == '|' and (cy-1, cx) in piece_cells:
                stack.append((cy-1, cx))
        
        # Match component to a piece and orientation
        match_found = False
        for (piece_id, orientation), piece in PIECE_MAP.items():
            # Try every cell in the piece as an anchor to align with the first cell of our component (y, x)
            for anchor_cell in piece.cells:
                # Potential piece center location if anchor_cell matches component cell (y, x)
                loc_y = y - anchor_cell.location.y
                loc_x = x - anchor_cell.location.x
                
                if not (0 <= loc_y < 5 and 0 <= loc_x < 5):
                    continue
                
                # Verify all cells of this piece match the component
                temp_component_matches = True
                piece_abs_locs = set()
                for pcell in piece.cells:
                    ay, ax = loc_y + pcell.location.y, loc_x + pcell.location.x
                    if (ay, ax) not in component:
                        temp_component_matches = False
                        break
                    
                    # Verify cell type
                    char = buffer[ay*2][ax*2]
                    is_box = char in ('B', 'C')
                    if is_box != (pcell.t == CellType.BOX):
                        temp_component_matches = False
                        break
                    piece_abs_locs.add((ay, ax))
                
                if temp_component_matches and len(piece_abs_locs) == len(component):
                    piece_places.append(PiecePlace(piece_id, Location(loc_y, loc_x), orientation))
                    match_found = True
                    break
            if match_found:
                break
        
        if not match_found:
            raise ValueError(f"Could not identify piece for component starting at ({y}, {x})")
            
    return Board(setup, piece_places)
