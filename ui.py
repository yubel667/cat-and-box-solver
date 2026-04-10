import pygame
import sys
from board import Board, PIECE_MAP, CellType

# Constants
CELL_SIZE = 100
MARGIN = 50
WIDTH = CELL_SIZE * 5 + 2 * MARGIN
HEIGHT = CELL_SIZE * 5 + 2 * MARGIN
FPS = 60
ANIMATION_DURATION_SEC = 0.5
FRAMES_PER_MOVE = int(FPS * ANIMATION_DURATION_SEC)

# Colors
BG_COLOR = (240, 240, 240)
GRID_COLOR = (200, 200, 200)
CAT_COLOR = (255, 100, 100)
BOX_OUTLINE = (50, 50, 200)

PIECE_COLORS = [
    (150, 200, 250), # 0
    (250, 150, 200), # 1
    (200, 250, 150), # 2
    (250, 200, 150), # 3
]

def draw_board(screen, board, moving_piece_data=None):
    screen.fill(BG_COLOR)
    
    # Draw Grid
    for i in range(6):
        pygame.draw.line(screen, GRID_COLOR, (MARGIN, MARGIN + i * CELL_SIZE), (WIDTH - MARGIN, MARGIN + i * CELL_SIZE), 2)
        pygame.draw.line(screen, GRID_COLOR, (MARGIN + i * CELL_SIZE, MARGIN), (MARGIN + i * CELL_SIZE, HEIGHT - MARGIN), 2)

    # Draw Cats
    for cat in board.setup.cats:
        cx = MARGIN + cat.loc.x * CELL_SIZE + CELL_SIZE // 2
        cy = MARGIN + cat.loc.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, CAT_COLOR, (cx, cy), CELL_SIZE // 3)

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

    # Draw moving piece
    if moving_piece_data:
        draw_piece(
            screen, 
            moving_piece_data['id'], 
            moving_piece_data['orientation'], 
            moving_piece_data['x'], 
            moving_piece_data['y']
        )
        
def draw_piece(screen, p_id, orientation, loc_x, loc_y):
    piece = PIECE_MAP[p_id, orientation]
    color = PIECE_COLORS[p_id % len(PIECE_COLORS)]
    
    # Draw connections
    cells = []
    for cell in piece.cells:
        gx = loc_x + cell.location.x
        gy = loc_y + cell.location.y
        cells.append((gx, gy))
        
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            gx1, gy1 = cells[i]
            gx2, gy2 = cells[j]
            if (gx1 == gx2 and abs(gy1 - gy2) == 1) or (gy1 == gy2 and abs(gx1 - gx2) == 1):
                px1 = MARGIN + gx1 * CELL_SIZE + CELL_SIZE // 2
                py1 = MARGIN + gy1 * CELL_SIZE + CELL_SIZE // 2
                px2 = MARGIN + gx2 * CELL_SIZE + CELL_SIZE // 2
                py2 = MARGIN + gy2 * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.line(screen, color, (px1, py1), (px2, py2), 15)

    # Draw cells
    for cell in piece.cells:
        gx = loc_x + cell.location.x
        gy = loc_y + cell.location.y
        
        px = MARGIN + gx * CELL_SIZE
        py = MARGIN + gy * CELL_SIZE
        
        rect = pygame.Rect(px + 10, py + 10, CELL_SIZE - 20, CELL_SIZE - 20)
        
        if cell.t == CellType.BOX:
            # Draw Box (hollow with thick border)
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, BOX_OUTLINE, rect, 5, border_radius=10)
            # Add a hole in the middle to see the cat
            hole_rect = pygame.Rect(px + 30, py + 30, CELL_SIZE - 60, CELL_SIZE - 60)
            pygame.draw.rect(screen, BG_COLOR, hole_rect, border_radius=5)
        else:
            # Draw Flat
            flat_rect = pygame.Rect(px + 30, py + 30, CELL_SIZE - 60, CELL_SIZE - 60)
            pygame.draw.rect(screen, color, flat_rect, border_radius=5)

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
            
            moving_data = {
                'id': moving_p_end.id,
                'orientation': moving_p_end.orientation if progress > 0.5 else moving_p_start.orientation,
                'x': curr_x,
                'y': curr_y
            }
            
            draw_board(screen, board_end, moving_data)
            
            frame += 1
            if frame >= FRAMES_PER_MOVE:
                frame = 0
                current_step += 1
                pygame.display.flip()
                pygame.time.wait(300)
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
