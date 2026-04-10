import pygame
import sys
import os
from board import (
    Board, BoardSetup, PiecePlace, Cat, Location, 
    PIECES, PIECE_MAP, CellType, FullBoardState
)
from board_parser import parse_board_string

# Improved Constants
CELL_SIZE = 100
MARGIN = 100 # Larger margin to prevent pieces from rendering outside
BOARD_WIDTH = CELL_SIZE * 5 + 2 * MARGIN
BOARD_HEIGHT = CELL_SIZE * 5 + 2 * MARGIN
PALETTE_HEIGHT = 160
WIDTH = BOARD_WIDTH + 250 # Extra side space
HEIGHT = BOARD_HEIGHT + PALETTE_HEIGHT

# Colors (matching ui.py)
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
VALID_COLOR = (100, 255, 100)
INVALID_COLOR = (255, 100, 100)

FPS=60

class Editor:
    def __init__(self, question_num):
        self.question_num = question_num
        self.file_path = f"questions/{question_num}.txt"
        self.cats = []
        self.pieces = [] # List of PiecePlace
        self.selected_type = None # 'cat' or 'piece'
        self.selected_id = None # piece id if selected_type == 'piece'
        self.selected_orientation = 0
        
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    board = parse_board_string(f.read())
                    self.cats = board.setup.cats
                    self.pieces = board.pieces
            except Exception as e:
                print(f"Error loading existing file: {e}")

    def save(self):
        valid, msg = self.validate()
        if not valid:
            print(f"Cannot save: {msg}")
            return False
            
        setup = BoardSetup(self.cats)
        board = Board(setup, self.pieces)
        ascii_str = board.debug_string()
        
        os.makedirs("questions", exist_ok=True)
        with open(self.file_path, "w") as f:
            f.write(ascii_str)
        print(f"Saved to {self.file_path}")
        return True

    def validate(self):
        if len(self.cats) != 5:
            return False, f"Need 5 cats ({len(self.cats)}/5)"
        if len(self.pieces) != 4:
            return False, f"Need 4 pieces ({len(self.pieces)}/4)"
        
        try:
            setup = BoardSetup(self.cats)
            board = Board(setup, self.pieces)
            if board.board_state == FullBoardState.INVALID:
                return False, "Invalid: Overlap or bad placement"
        except Exception:
            return False, "Invalid board configuration"
            
        return True, "Valid setup"

    def rotate_selection(self):
        self.selected_orientation = (self.selected_orientation + 1) % 4
        # If selected piece is on board, update it immediately
        if self.selected_type == 'piece':
            for i, p in enumerate(self.pieces):
                if p.id == self.selected_id:
                    self.pieces[i] = PiecePlace(p.id, p.loc, self.selected_orientation)
                    break

    def handle_click(self, pos, button):
        x, y = pos
        
        # Check Grid
        grid_x = (x - MARGIN) // CELL_SIZE
        grid_y = (y - MARGIN) // CELL_SIZE
        
        if 0 <= grid_x < 5 and 0 <= grid_y < 5:
            if button == 1: # Left click place/select
                self.on_grid_click(grid_x, grid_y)
            elif button == 3: # Right click rotate
                # First select what's there
                self.on_grid_click(grid_x, grid_y, select_only=True)
                self.rotate_selection()
            return

        if button != 1: return

        # Check Palette (Cats)
        cat_pal_rect = pygame.Rect(MARGIN, BOARD_HEIGHT + 20, CELL_SIZE, CELL_SIZE)
        if cat_pal_rect.collidepoint(pos):
            self.selected_type = 'cat'
            self.selected_id = None
            return

        # Check Palette (Pieces)
        for i in range(4):
            p_rect = pygame.Rect(MARGIN + (i+1) * (CELL_SIZE + 40), BOARD_HEIGHT + 20, CELL_SIZE, CELL_SIZE)
            if p_rect.collidepoint(pos):
                self.selected_type = 'piece'
                self.selected_id = i
                # Default to current orientation if already on board
                existing = next((p for p in self.pieces if p.id == i), None)
                if existing:
                    self.selected_orientation = existing.orientation
                else:
                    self.selected_orientation = 0
                return

        # Check Save Button
        save_btn_rect = pygame.Rect(WIDTH - 200, HEIGHT - 80, 150, 50)
        if save_btn_rect.collidepoint(pos):
            self.save()

    def on_grid_click(self, gx, gy, select_only=False):
        # 1. Check for pieces first (flexible selection)
        clicked_piece = None
        for p in self.pieces:
            actual = PIECE_MAP[p.id, p.orientation]
            for cell in actual.cells:
                if p.loc.x + cell.location.x == gx and p.loc.y + cell.location.y == gy:
                    clicked_piece = p
                    break
            if clicked_piece: break

        if clicked_piece:
            self.selected_type = 'piece'
            self.selected_id = clicked_piece.id
            self.selected_orientation = clicked_piece.orientation
            if select_only: return
            # If we were already selected and click again, we might want to move it?
            # Handled by logic below.
        
        # 2. Check for cats
        clicked_cat = next((c for c in self.cats if c.loc.x == gx and c.loc.y == gy), None)
        if clicked_cat:
            self.selected_type = 'cat'
            if select_only: return
            self.cats.remove(clicked_cat)
            return

        if select_only:
            self.selected_type = None
            return

        # 3. Placement logic
        if self.selected_type == 'cat':
            if len(self.cats) < 5:
                # Remove anything currently at this cell
                self.cats = [c for c in self.cats if not (c.loc.x == gx and c.loc.y == gy)]
                self.cats.append(Cat(Location(gy, gx)))
        elif self.selected_type == 'piece' and self.selected_id is not None:
            # Move existing piece
            self.pieces = [p for p in self.pieces if p.id != self.selected_id]
            self.pieces.append(PiecePlace(self.selected_id, Location(gy, gx), self.selected_orientation))

def draw_piece(screen, p_id, orientation, loc_x, loc_y, alpha=255, scale=1.0):
    piece = PIECE_MAP[p_id, orientation]
    s_cell = int(CELL_SIZE * scale)
    surf_size = s_cell * 5
    piece_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    center = surf_size // 2

    # Connections
    cells = []
    for cell in piece.cells:
        cells.append((cell.location.x, cell.location.y))
        
    for i in range(len(cells)):
        for j in range(i + 1, len(cells)):
            gx1, gy1 = cells[i]
            gx2, gy2 = cells[j]
            if (gx1 == gx2 and abs(gy1 - gy2) == 1) or (gy1 == gy2 and abs(gx1 - gx2) == 1):
                px1 = center + gx1 * s_cell
                py1 = center + gy1 * s_cell
                px2 = center + gx2 * s_cell
                py2 = center + gy2 * s_cell
                pygame.draw.line(piece_surf, CONNECTION_COLOR, (px1, py1), (px2, py2), int(80 * scale))

    # Cells
    for cell in piece.cells:
        gx, gy = cell.location.x, cell.location.y
        px = center + gx * s_cell - s_cell // 2
        py = center + gy * s_cell - s_cell // 2
        rect = pygame.Rect(px + 2, py + 2, s_cell - 4, s_cell - 4)
        
        if cell.t == CellType.BOX:
            pygame.draw.rect(piece_surf, BOX_COLOR, rect, border_radius=int(8*scale))
            pygame.draw.rect(piece_surf, (0,0,0), rect, 2, border_radius=int(8*scale))
            pygame.draw.circle(piece_surf, (0, 0, 0, 0), (px + s_cell // 2, py + s_cell // 2), s_cell // 3)
        else:
            pygame.draw.rect(piece_surf, EMPTY_CELL_COLOR, rect, border_radius=int(4*scale))
            pygame.draw.rect(piece_surf, (0,0,0), rect, 2, border_radius=int(4*scale))

    if alpha < 255:
        piece_surf.set_alpha(alpha)

    final_rect = piece_surf.get_rect(center=(
        MARGIN + loc_x * CELL_SIZE + CELL_SIZE // 2,
        MARGIN + loc_y * CELL_SIZE + CELL_SIZE // 2
    ))
    screen.blit(piece_surf, final_rect)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 editor.py <question_number>")
        sys.exit(1)
        
    question_num = sys.argv[1]
    editor = Editor(question_num)
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Cats and Boxes Editor - Level {question_num}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                editor.handle_click(mouse_pos, event.button)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    editor.rotate_selection()
                elif event.key == pygame.K_s:
                    editor.save()
                elif event.key == pygame.K_ESCAPE:
                    editor.selected_type = None

        screen.fill(UI_BG_COLOR)
        
        # 1. Draw Board Area
        pygame.draw.rect(screen, BOARD_COLOR, (0, 0, BOARD_WIDTH, BOARD_HEIGHT))
        for i in range(6):
            pygame.draw.line(screen, GRID_LINE_COLOR, (MARGIN, MARGIN + i * CELL_SIZE), (BOARD_WIDTH - MARGIN, MARGIN + i * CELL_SIZE), 2)
            pygame.draw.line(screen, GRID_LINE_COLOR, (MARGIN + i * CELL_SIZE, MARGIN), (MARGIN + i * CELL_SIZE, BOARD_HEIGHT - MARGIN), 2)

        # 2. Draw Cats
        for cat in editor.cats:
            cx = MARGIN + cat.loc.x * CELL_SIZE + CELL_SIZE // 2
            cy = MARGIN + cat.loc.y * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.circle(screen, CAT_COLOR, (cx, cy), CELL_SIZE * 0.3)

        # 3. Draw Pieces
        for p in editor.pieces:
            draw_piece(screen, p.id, p.orientation, p.loc.x, p.loc.y)

        # 4. Draw Palette
        pygame.draw.rect(screen, (30, 30, 30), (0, BOARD_HEIGHT, WIDTH, PALETTE_HEIGHT))
        
        # Cat Palette
        cat_rect = pygame.Rect(MARGIN, BOARD_HEIGHT + 30, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (60, 60, 60), cat_rect, border_radius=10)
        if editor.selected_type == 'cat':
            pygame.draw.rect(screen, (255, 255, 255), cat_rect, 3, border_radius=10)
        pygame.draw.circle(screen, CAT_COLOR, cat_rect.center, CELL_SIZE * 0.3)
        ctxt = font.render(f"{len(editor.cats)}/5", True, TEXT_COLOR)
        screen.blit(ctxt, (cat_rect.centerx - ctxt.get_width()//2, cat_rect.bottom + 5))

        # Piece Palette
        for i in range(4):
            p_rect = pygame.Rect(MARGIN + (i+1) * (CELL_SIZE + 40), BOARD_HEIGHT + 30, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (60, 60, 60), p_rect, border_radius=10)
            
            is_on_board = any(p.id == i for p in editor.pieces)
            if editor.selected_type == 'piece' and editor.selected_id == i:
                pygame.draw.rect(screen, (255, 255, 255), p_rect, 3, border_radius=10)
            elif is_on_board:
                pygame.draw.rect(screen, (100, 100, 100), p_rect, 1, border_radius=10)
                
            # Palette preview (scaled down)
            draw_piece(screen, i, 0, (p_rect.centerx - MARGIN - CELL_SIZE//2) / CELL_SIZE, (p_rect.centery - MARGIN - CELL_SIZE//2) / CELL_SIZE, alpha=150 if is_on_board else 255, scale=0.3)

        # 5. Ghost Preview
        gx = (mouse_pos[0] - MARGIN) // CELL_SIZE
        gy = (mouse_pos[1] - MARGIN) // CELL_SIZE
        if 0 <= gx < 5 and 0 <= gy < 5:
            if editor.selected_type == 'cat':
                pygame.draw.circle(screen, (*CAT_COLOR, 100), (MARGIN + gx * CELL_SIZE + CELL_SIZE // 2, MARGIN + gy * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE * 0.3)
            elif editor.selected_type == 'piece':
                draw_piece(screen, editor.selected_id, editor.selected_orientation, gx, gy, alpha=100)

        # 6. UI Panel
        valid, msg = editor.validate()
        status_color = VALID_COLOR if valid else INVALID_COLOR
        status_surf = font.render(msg, True, status_color)
        screen.blit(status_surf, (BOARD_WIDTH + 20, 50))
        
        instructions = [
            "LEFT CLICK:",
            "  - Palette to select",
            "  - Grid to place/move",
            "RIGHT CLICK / 'R':",
            "  - Rotate selection",
            "ESC: Deselect",
            "S: Save to File"
        ]
        for idx, line in enumerate(instructions):
            isurf = font.render(line, True, (180, 180, 180))
            screen.blit(isurf, (BOARD_WIDTH + 20, 120 + idx * 30))

        # Save Button
        save_btn_rect = pygame.Rect(WIDTH - 200, HEIGHT - 80, 150, 50)
        btn_col = BTN_HOVER_COLOR if save_btn_rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, btn_col, save_btn_rect, border_radius=8)
        stxt = font.render("SAVE", True, TEXT_COLOR if valid else (120, 120, 120))
        screen.blit(stxt, stxt.get_rect(center=save_btn_rect.center))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
