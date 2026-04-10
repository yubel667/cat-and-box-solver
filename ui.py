import pygame
import sys
import math
from board import Board, PIECE_MAP, CellType, PIECES

# Constants
CELL_SIZE = 100
MARGIN = 50
WIDTH = CELL_SIZE * 5 + 2 * MARGIN
HEIGHT = CELL_SIZE * 5 + 2 * MARGIN
FPS = 60
ANIMATION_DURATION_SEC = 0.8  # Slightly slower for better visibility
FRAMES_PER_MOVE = int(FPS * ANIMATION_DURATION_SEC)

# Colors
BOARD_COLOR = (30, 30, 150)
GRID_LINE_COLOR = (60, 60, 200)
CAT_COLOR = (255, 165, 0) # Orange
BOX_COLOR = (210, 180, 140) # Light Brown
EMPTY_CELL_COLOR = (0, 255, 255) # Cyan
CONNECTION_COLOR = (200, 200, 200) # Light Gray

def draw_board(screen, board, moving_piece_data=None):
    screen.fill(BOARD_COLOR)
    
    # Draw Grid
    for i in range(6):
        pygame.draw.line(screen, GRID_LINE_COLOR, (MARGIN, MARGIN + i * CELL_SIZE), (WIDTH - MARGIN, MARGIN + i * CELL_SIZE), 2)
        pygame.draw.line(screen, GRID_LINE_COLOR, (MARGIN + i * CELL_SIZE, MARGIN), (MARGIN + i * CELL_SIZE, HEIGHT - MARGIN), 2)

    # Draw Cats
    for cat in board.setup.cats:
        cx = MARGIN + cat.loc.x * CELL_SIZE + CELL_SIZE // 2
        cy = MARGIN + cat.loc.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, CAT_COLOR, (cx, cy), CELL_SIZE // 2.5)

    # Separate static pieces and the moving piece (if any)
    static_pieces = []
    if moving_piece_data:
        moving_id = moving_piece_data['id']
        for p in board.pieces:
            if p.id != moving_id:
                static_pieces.append(p)
    else:
        static_pieces = board.pieces

    # Draw static pieces
    for p in static_pieces:
        draw_piece(screen, p.id, p.orientation, p.loc.x, p.loc.y)

    # Draw moving piece with alpha and rotation
    if moving_piece_data:
        draw_piece(
            screen, 
            moving_piece_data['id'], 
            0, # We will handle rotation manually
            moving_piece_data['x'], 
            moving_piece_data['y'],
            alpha=160, # Transparency
            angle=moving_piece_data['angle']
        )
        
def draw_piece(screen, p_id, orientation, loc_x, loc_y, alpha=255, angle=None):
    # If angle is provided, we ignore orientation and use PIECES[p_id] (base orientation)
    if angle is not None:
        piece = next(p for p in PIECES if p.id == p_id)
        rotation_angle = angle
    else:
        piece = PIECE_MAP[p_id, orientation]
        rotation_angle = 0

    # Create a temporary surface for the piece to handle alpha and rotation
    surf_size = CELL_SIZE * 5 
    piece_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    center = surf_size // 2

    # Draw connections
    cells = []
    for cell in piece.cells:
        gx = cell.location.x
        gy = cell.location.y
        cells.append((gx, gy))
        
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            gx1, gy1 = cells[i]
            gx2, gy2 = cells[j]
            if (gx1 == gx2 and abs(gy1 - gy2) == 1) or (gy1 == gy2 and abs(gx1 - gx2) == 1):
                px1 = center + gx1 * CELL_SIZE
                py1 = center + gy1 * CELL_SIZE
                px2 = center + gx2 * CELL_SIZE
                py2 = center + gy2 * CELL_SIZE
                pygame.draw.line(piece_surf, CONNECTION_COLOR, (px1, py1), (px2, py2), 20)

    # Draw cells
    for cell in piece.cells:
        gx = cell.location.x
        gy = cell.location.y
        
        px = center + gx * CELL_SIZE - CELL_SIZE // 2
        py = center + gy * CELL_SIZE - CELL_SIZE // 2
        
        # Large size: leave only a small 2px gap
        rect = pygame.Rect(px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        
        if cell.t == CellType.BOX:
            # Box cell: Light brown with a central transparent hole
            pygame.draw.rect(piece_surf, BOX_COLOR, rect, border_radius=8)
            pygame.draw.rect(piece_surf, (0,0,0), rect, 2, border_radius=8) # Outline
            
            # Central hole (to see the cat)
            hole_radius = CELL_SIZE // 3
            pygame.draw.circle(piece_surf, (0, 0, 0, 0), (px + CELL_SIZE // 2, py + CELL_SIZE // 2), hole_radius)
        else:
            # Empty cell: Cyan
            pygame.draw.rect(piece_surf, EMPTY_CELL_COLOR, rect, border_radius=4)
            pygame.draw.rect(piece_surf, (0,0,0), rect, 2, border_radius=4) # Outline

    # Apply rotation
    if rotation_angle != 0:
        piece_surf = pygame.transform.rotate(piece_surf, rotation_angle)
    
    # Apply alpha
    if alpha < 255:
        # Create a copy with alpha
        temp_surf = pygame.Surface(piece_surf.get_size(), pygame.SRCALPHA)
        temp_surf.blit(piece_surf, (0,0))
        temp_surf.set_alpha(alpha)
        piece_surf = temp_surf

    # Blit to screen
    final_rect = piece_surf.get_rect(center=(
        MARGIN + loc_x * CELL_SIZE + CELL_SIZE // 2,
        MARGIN + loc_y * CELL_SIZE + CELL_SIZE // 2
    ))
    screen.blit(piece_surf, final_rect)

def play_animation(solution_path):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cats and Boxes Solver")
    clock = pygame.time.Clock()

    if not solution_path:
        print("No solution to animate.")
        return

    current_step = 0
    frame = 0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Reset animation
                    current_step = 0
                    frame = 0
                
        if current_step < len(solution_path) - 1:
            board_start = solution_path[current_step]
            board_end = solution_path[current_step + 1]
            
            # Find the moving piece
            moving_p_start = None
            moving_p_end = None
            
            for p1, p2 in zip(board_start.pieces, board_end.pieces):
                if p1.loc.x != p2.loc.x or p1.loc.y != p2.loc.y or p1.orientation != p2.orientation:
                    moving_p_start = p1
                    moving_p_end = p2
                    break
                    
            if not moving_p_start:
                current_step += 1
                frame = 0
                continue
                
            progress = frame / FRAMES_PER_MOVE
            # Easing
            t = progress
            ease = t * t * (3.0 - 2.0 * t) # smoothstep
            
            curr_x = moving_p_start.loc.x + (moving_p_end.loc.x - moving_p_start.loc.x) * ease
            curr_y = moving_p_start.loc.y + (moving_p_end.loc.y - moving_p_start.loc.y) * ease
            
            # Handle rotation angle (CCW)
            angle_start = moving_p_start.orientation * 90
            angle_end = moving_p_end.orientation * 90
            
            # Shortest rotation path
            diff = (angle_end - angle_start + 180) % 360 - 180
            curr_angle = angle_start + diff * ease
            
            moving_data = {
                'id': moving_p_end.id,
                'x': curr_x,
                'y': curr_y,
                'angle': curr_angle
            }
            
            draw_board(screen, board_end, moving_data)
            
            frame += 1
            if frame >= FRAMES_PER_MOVE:
                frame = 0
                current_step += 1
                pygame.display.flip()
                pygame.time.wait(200)
        else:
            # Final state
            draw_board(screen, solution_path[-1])
            
            # Display SOLVED text
            font = pygame.font.SysFont(None, 64)
            text = font.render("SOLVED!", True, (0, 150, 0))
            text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
            bg_rect = text_rect.inflate(20, 20)
            pygame.draw.rect(screen, (255, 255, 255), bg_rect)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, 2)
            screen.blit(text, text_rect)
            
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
