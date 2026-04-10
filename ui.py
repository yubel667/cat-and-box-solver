import pygame
import sys
import math
from board import Board, PIECE_MAP, CellType, PIECES

# Constants
CELL_SIZE = 100
MARGIN = 50
BOARD_WIDTH = CELL_SIZE * 5 + 2 * MARGIN
BOARD_HEIGHT = CELL_SIZE * 5 + 2 * MARGIN
CONTROL_HEIGHT = 130
WIDTH = BOARD_WIDTH
HEIGHT = BOARD_HEIGHT + CONTROL_HEIGHT
FPS = 60
ANIM_DURATION = 0.5 # Fixed animation speed
ANIM_FRAMES = int(FPS * ANIM_DURATION)

# Colors
BOARD_COLOR = (30, 30, 150)
GRID_LINE_COLOR = (60, 60, 200)
CAT_COLOR = (160, 32, 240) # Purple
BOX_COLOR = (210, 180, 140) # Light Brown
EMPTY_CELL_COLOR = (0, 255, 255) # Cyan
CONNECTION_COLOR = EMPTY_CELL_COLOR
TEXT_COLOR = (255, 255, 255)
UI_BG_COLOR = (40, 40, 40)
BTN_COLOR = (60, 60, 60)
BTN_HOVER_COLOR = (80, 80, 80)

def draw_board(screen, board, moving_piece_data=None):
    pygame.draw.rect(screen, BOARD_COLOR, (0, 0, BOARD_WIDTH, BOARD_HEIGHT))
    
    # Draw Grid
    for i in range(6):
        pygame.draw.line(screen, GRID_LINE_COLOR, (MARGIN, MARGIN + i * CELL_SIZE), (BOARD_WIDTH - MARGIN, MARGIN + i * CELL_SIZE), 2)
        pygame.draw.line(screen, GRID_LINE_COLOR, (MARGIN + i * CELL_SIZE, MARGIN), (MARGIN + i * CELL_SIZE, BOARD_HEIGHT - MARGIN), 2)

    # Draw Cats
    for cat in board.setup.cats:
        cx = MARGIN + cat.loc.x * CELL_SIZE + CELL_SIZE // 2
        cy = MARGIN + cat.loc.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, CAT_COLOR, (cx, cy), CELL_SIZE * 0.3)

    static_pieces = []
    if moving_piece_data:
        moving_id = moving_piece_data['id']
        for p in board.pieces:
            if p.id != moving_id:
                static_pieces.append(p)
    else:
        static_pieces = board.pieces

    for p in static_pieces:
        draw_piece(screen, p.id, p.orientation, p.loc.x, p.loc.y)

    if moving_piece_data:
        draw_piece(
            screen, 
            moving_piece_data['id'], 
            0,
            moving_piece_data['x'], 
            moving_piece_data['y'],
            alpha=160,
            angle=moving_piece_data['angle']
        )
        
def draw_piece(screen, p_id, orientation, loc_x, loc_y, alpha=255, angle=None):
    if angle is not None:
        piece = next(p for p in PIECES if p.id == p_id)
        rotation_angle = angle
    else:
        piece = PIECE_MAP[p_id, orientation]
        rotation_angle = 0

    surf_size = CELL_SIZE * 5 
    piece_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    center = surf_size // 2

    # Connections
    cells = []
    for cell in piece.cells:
        gx, gy = cell.location.x, cell.location.y
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
                pygame.draw.line(piece_surf, CONNECTION_COLOR, (px1, py1), (px2, py2), 80)

    # Cells
    for cell in piece.cells:
        gx, gy = cell.location.x, cell.location.y
        px = center + gx * CELL_SIZE - CELL_SIZE // 2
        py = center + gy * CELL_SIZE - CELL_SIZE // 2
        rect = pygame.Rect(px + 2, py + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        
        if cell.t == CellType.BOX:
            pygame.draw.rect(piece_surf, BOX_COLOR, rect, border_radius=8)
            pygame.draw.rect(piece_surf, (0,0,0), rect, 2, border_radius=8)
            hole_radius = CELL_SIZE // 3
            pygame.draw.circle(piece_surf, (0, 0, 0, 0), (px + CELL_SIZE // 2, py + CELL_SIZE // 2), hole_radius)
        else:
            pygame.draw.rect(piece_surf, EMPTY_CELL_COLOR, rect, border_radius=4)
            pygame.draw.rect(piece_surf, (0,0,0), rect, 2, border_radius=4)

    if rotation_angle != 0:
        piece_surf = pygame.transform.rotate(piece_surf, rotation_angle)
    
    if alpha < 255:
        temp_surf = pygame.Surface(piece_surf.get_size(), pygame.SRCALPHA)
        temp_surf.blit(piece_surf, (0,0))
        temp_surf.set_alpha(alpha)
        piece_surf = temp_surf

    final_rect = piece_surf.get_rect(center=(
        MARGIN + loc_x * CELL_SIZE + CELL_SIZE // 2,
        MARGIN + loc_y * CELL_SIZE + CELL_SIZE // 2
    ))
    screen.blit(piece_surf, final_rect)

def get_button_rects():
    btn_w, btn_h = 70, 40
    spacing = 10
    total_w = 5 * btn_w + 4 * spacing
    start_x = (WIDTH - total_w) // 2
    y = BOARD_HEIGHT + 40
    
    rects = []
    for i in range(5):
        rects.append(pygame.Rect(start_x + i * (btn_w + spacing), y, btn_w, btn_h))
    return rects

def get_slider_rect():
    return pygame.Rect(WIDTH // 2 - 100, BOARD_HEIGHT + 100, 200, 10)

def draw_ui(screen, current_step, total_steps, is_auto_playing, mouse_pos, delay_sec):
    ui_rect = pygame.Rect(0, BOARD_HEIGHT, WIDTH, CONTROL_HEIGHT)
    pygame.draw.rect(screen, UI_BG_COLOR, ui_rect)
    pygame.draw.line(screen, (100, 100, 100), (0, BOARD_HEIGHT), (WIDTH, BOARD_HEIGHT), 2)

    font = pygame.font.SysFont(None, 24)
    btn_rects = get_button_rects()
    labels = ["|<", "<", "Pause" if is_auto_playing else "Auto", ">", ">|"]

    for rect, label in zip(btn_rects, labels):
        color = BTN_HOVER_COLOR if rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), rect, 1, border_radius=5)
        
        text = font.render(label, True, TEXT_COLOR)
        screen.blit(text, text.get_rect(center=rect.center))

    # Slider
    slider_rect = get_slider_rect()
    pygame.draw.line(screen, (100, 100, 100), (slider_rect.left, slider_rect.centery), (slider_rect.right, slider_rect.centery), 4)
    knob_x = slider_rect.left + int((delay_sec / 2.0) * slider_rect.width)
    pygame.draw.circle(screen, (200, 200, 200), (knob_x, slider_rect.centery), 8)
    
    delay_text = font.render(f"Auto Delay: {delay_sec:.1f}s", True, TEXT_COLOR)
    screen.blit(delay_text, (slider_rect.left - 130, slider_rect.top - 5))

    # Step Info
    step_font = pygame.font.SysFont(None, 32)
    step_text = step_font.render(f"Step {current_step} / {total_steps-1}", True, TEXT_COLOR)
    screen.blit(step_text, (20, BOARD_HEIGHT + 10))
    
    # Key hint
    hint_font = pygame.font.SysFont(None, 20)
    hint = "SPACE: Next | ENTER: Auto Play"
    hint_text = hint_font.render(hint, True, (150, 150, 150))
    screen.blit(hint_text, (WIDTH - hint_text.get_width() - 20, BOARD_HEIGHT + 15))

    return btn_rects, slider_rect

def play_animation(solution_path):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cats and Boxes Solver")
    clock = pygame.time.Clock()

    current_step = 0
    frame = 0
    is_animating = False
    is_auto_playing = False
    auto_pause_timer = 0 # Timer for delay between moves in auto-play
    delay_sec = 0.3 # Default for best result.
    dragging_slider = False
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        btn_rects, slider_rect = draw_ui(screen, current_step, len(solution_path), is_auto_playing, mouse_pos, delay_sec)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if slider_rect.inflate(0, 20).collidepoint(mouse_pos):
                    dragging_slider = True
                else:
                    if btn_rects[0].collidepoint(mouse_pos): # Begin
                        current_step, frame, is_animating, is_auto_playing, auto_pause_timer = 0, 0, False, False, 0
                    elif btn_rects[1].collidepoint(mouse_pos): # Prev
                        is_animating, is_auto_playing, auto_pause_timer = False, False, 0
                        if current_step > 0: current_step -= 1
                        frame = 0
                    elif btn_rects[2].collidepoint(mouse_pos): # Auto/Pause
                        is_auto_playing = not is_auto_playing
                        if is_auto_playing:
                            if not is_animating and current_step < len(solution_path)-1:
                                is_animating = True
                                frame = 0
                        else:
                            auto_pause_timer = 0
                    elif btn_rects[3].collidepoint(mouse_pos): # Next
                        if not is_animating and current_step < len(solution_path)-1:
                            is_animating, is_auto_playing, frame, auto_pause_timer = True, False, 0, 0
                    elif btn_rects[4].collidepoint(mouse_pos): # End
                        current_step, frame, is_animating, is_auto_playing, auto_pause_timer = len(solution_path)-1, 0, False, False, 0

            if event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False

            if dragging_slider:
                rel_x = max(0, min(mouse_pos[0] - slider_rect.left, slider_rect.width))
                delay_sec = round((rel_x / slider_rect.width) * 2.0, 1)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not is_animating and current_step < len(solution_path)-1:
                        is_animating, is_auto_playing, frame, auto_pause_timer = True, False, 0, 0
                elif event.key == pygame.K_RETURN:
                    if current_step == len(solution_path) - 1:
                        running = False
                    else:
                        is_auto_playing = not is_auto_playing
                        if is_auto_playing:
                            if not is_animating and current_step < len(solution_path)-1:
                                is_animating = True
                                frame = 0
                        else:
                            auto_pause_timer = 0

        if is_animating:
            board_start = solution_path[current_step]
            board_end = solution_path[current_step + 1]
            moving_p_start, moving_p_end = None, None
            for p1, p2 in zip(board_start.pieces, board_end.pieces):
                if p1.loc.x != p2.loc.x or p1.loc.y != p2.loc.y or p1.orientation != p2.orientation:
                    moving_p_start, moving_p_end = p1, p2
                    break
            
            if moving_p_start:
                progress = frame / ANIM_FRAMES
                ease = progress * progress * (3.0 - 2.0 * progress)
                curr_x = moving_p_start.loc.x + (moving_p_end.loc.x - moving_p_start.loc.x) * ease
                curr_y = moving_p_start.loc.y + (moving_p_end.loc.y - moving_p_start.loc.y) * ease
                angle_start, angle_end = moving_p_start.orientation * 90, moving_p_end.orientation * 90
                diff = (angle_end - angle_start + 180) % 360 - 180
                curr_angle = angle_start + diff * ease
                draw_board(screen, board_end, {'id': moving_p_end.id, 'x': curr_x, 'y': curr_y, 'angle': curr_angle})
                frame += 1
                if frame >= ANIM_FRAMES:
                    frame, current_step, is_animating = 0, current_step + 1, False
                    if is_auto_playing and current_step < len(solution_path)-1:
                        auto_pause_timer = int(delay_sec * FPS)
            else:
                current_step += 1
                is_animating = False
                if is_auto_playing and current_step < len(solution_path)-1:
                    auto_pause_timer = int(delay_sec * FPS)
        else:
            draw_board(screen, solution_path[current_step])
            if current_step == len(solution_path) - 1:
                font = pygame.font.SysFont(None, 64)
                text = font.render("SOLVED!", True, (0, 150, 0))
                text_rect = text.get_rect(center=(BOARD_WIDTH/2, BOARD_HEIGHT/2 - 10))
                
                exit_font = pygame.font.SysFont(None, 24)
                exit_text = exit_font.render("(Enter to exit)", True, (100, 100, 100))
                exit_rect = exit_text.get_rect(center=(BOARD_WIDTH/2, BOARD_HEIGHT/2 + 30))
                
                bg_rect = text_rect.union(exit_rect).inflate(30, 30)
                pygame.draw.rect(screen, (255, 255, 255), bg_rect)
                pygame.draw.rect(screen, (0, 0, 0), bg_rect, 2)
                screen.blit(text, text_rect)
                screen.blit(exit_text, exit_rect)
            elif is_auto_playing and auto_pause_timer > 0:
                auto_pause_timer -= 1
                if auto_pause_timer <= 0:
                    is_animating = True
                    frame = 0

        draw_ui(screen, current_step, len(solution_path), is_auto_playing, mouse_pos, delay_sec)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
