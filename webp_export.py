import os
import sys
import pygame
from PIL import Image
from board_parser import parse_board_string
from solver import solve_prioritized_bfs
import ui # Import constants and draw functions

def export_webp(question_num):
    file_path = f"questions/{question_num}.txt"
    if not os.path.exists(file_path):
        print(f"Error: Question {question_num} not found.")
        return

    with open(file_path, "r") as f:
        board_str = f.read()
    
    start_board = parse_board_string(board_str)
    print(f"Solving level {question_num} for export...")
    solution_path, _ = solve_prioritized_bfs(start_board)
    
    if not solution_path:
        print("No solution found.")
        return

    # Export Settings
    EXPORT_FPS = 24
    EXPORT_ANIM_FRAMES = int(EXPORT_FPS * ui.ANIM_DURATION)
    frame_duration = 1000 // EXPORT_FPS 
    
    # Auto-play settings
    delay_sec = 0.5
    pause_frames = int(EXPORT_FPS * delay_sec)
    level_name = str(question_num)

    # Headless-ish pygame initialization
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    # Minimal mode: only record the board area
    screen = pygame.Surface((ui.WIDTH, ui.BOARD_HEIGHT))
    
    frames = []
    
    print("Generating frames...")
    
    # 0. Initial delay (1 second)
    initial_delay_frames = EXPORT_FPS * 1
    for _ in range(initial_delay_frames):
        ui.draw_board(screen, solution_path[0])
        ui.draw_ui(screen, 0, len(solution_path), True, (-1,-1), delay_sec, level_name=level_name, minimal=True)
        frames.append(surface_to_pil(screen))

    for step in range(len(solution_path)):
        # 1. Stationary frames at the start of the step (pause between moves)
        if step > 0:
            for _ in range(pause_frames):
                ui.draw_board(screen, solution_path[step])
                ui.draw_ui(screen, step, len(solution_path), True, (-1,-1), delay_sec, level_name=level_name, minimal=True)
                frames.append(surface_to_pil(screen))

        # 2. Animation frames
        if step < len(solution_path) - 1:
            board_start = solution_path[step]
            board_end = solution_path[step + 1]
            
            moving_p_start, moving_p_end = None, None
            for p1, p2 in zip(board_start.pieces, board_end.pieces):
                if p1.loc.x != p2.loc.x or p1.loc.y != p2.loc.y or p1.orientation != p2.orientation:
                    moving_p_start, moving_p_end = p1, p2
                    break
            
            if moving_p_start:
                for frame in range(EXPORT_ANIM_FRAMES):
                    progress = frame / EXPORT_ANIM_FRAMES
                    ease = progress * progress * (3.0 - 2.0 * progress)
                    
                    curr_x = moving_p_start.loc.x + (moving_p_end.loc.x - moving_p_start.loc.x) * ease
                    curr_y = moving_p_start.loc.y + (moving_p_end.loc.y - moving_p_start.loc.y) * ease
                    
                    angle_start = moving_p_start.orientation * 90
                    angle_end = moving_p_end.orientation * 90
                    diff = (angle_end - angle_start + 180) % 360 - 180
                    curr_angle = angle_start + diff * ease
                    
                    ui.draw_board(screen, board_end, {'id': moving_p_end.id, 'x': curr_x, 'y': curr_y, 'angle': curr_angle})
                    ui.draw_ui(screen, step, len(solution_path), True, (-1,-1), delay_sec, level_name=level_name, minimal=True)
                    frames.append(surface_to_pil(screen))
            else:
                # Instant transition if no piece moved
                ui.draw_board(screen, board_end)
                ui.draw_ui(screen, step + 1, len(solution_path), True, (-1,-1), delay_sec, level_name=level_name, minimal=True)
                frames.append(surface_to_pil(screen))
        else:
            # Final state
            ui.draw_board(screen, solution_path[-1])
            
            # Draw "SOLVED!" notification as in ui.py (will appear in top margin)
            solved_font = pygame.font.SysFont(None, 48)
            text = solved_font.render("SOLVED!", True, (100, 255, 100))
            screen.blit(text, (int((ui.WIDTH - text.get_width()) *0.7), ui.MARGIN // 2 - text.get_height() // 2))
            ui.draw_ui(screen, step, len(solution_path), False, (-1,-1), delay_sec, level_name=level_name, minimal=True)
            
            # Add some final frames to show the result (1 second)
            final_delay_frames = EXPORT_FPS * 1
            for _ in range(final_delay_frames):
                frames.append(surface_to_pil(screen))

    print(f"Exporting {len(frames)} frames to WebP at {EXPORT_FPS} FPS (Minimal Mode)...")
    os.makedirs("solution", exist_ok=True)
    out_path = f"solution/{question_num}.webp"
    
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration,
        loop=0,
        lossless=False,
        quality=80,
        method=6
    )
    print(f"SUCCESS: Saved to {out_path} ({len(frames)} frames)")
    pygame.quit()

def surface_to_pil(surface):
    # Convert pygame surface to PIL Image
    size = surface.get_size()
    data = pygame.image.tobytes(surface, 'RGB')
    return Image.frombytes('RGB', size, data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 webp_export.py <question_number>")
        sys.exit(1)
    export_webp(sys.argv[1])
