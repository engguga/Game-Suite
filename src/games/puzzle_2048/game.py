import pygame
import random
import time
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class Puzzle2048Game(BaseGame):
    """Professional 2048 Puzzle Game with Dark Mode"""
    
    def __init__(self, engine):
        super().__init__(engine, "puzzle_2048")
        self.grid_size = 4
        self.cell_size = 100
        self.grid: List[List[int]] = []
        self.score = 0
        self.best_score = 0
        self.game_over = False
        self.won = False
        self.moved = False
        self.animations: List[Dict] = []
        self.dark_mode = True  # Default to dark mode
        
        # Dark mode color scheme - professional dark theme
        self.dark_colors = {
            'background': (25, 25, 40),
            'grid_bg': (50, 50, 70),
            'empty_cell': (40, 40, 60),
            'text_light': (220, 220, 220),
            'text_dark': (80, 80, 100),
            'panel_bg': (60, 60, 80, 200),
            'panel_border': (90, 90, 120)
        }
        
        # Light mode color scheme (original 2048)
        self.light_colors = {
            'background': (250, 248, 239),
            'grid_bg': (187, 173, 160),
            'empty_cell': (205, 193, 180),
            'text_light': (249, 246, 242),
            'text_dark': (119, 110, 101),
            'panel_bg': (187, 173, 160, 220),
            'panel_border': (150, 140, 130)
        }
        
        # Tile colors - optimized for dark mode
        self.tile_colors = {
            0: self.dark_colors['empty_cell'],      # Empty cell
            2: (65, 75, 85),                        # 2 - Dark slate
            4: (75, 85, 95),                        # 4 - Dark slate blue
            8: (100, 120, 140),                     # 8 - Steel blue
            16: (120, 140, 160),                    # 16 - Cadet blue
            32: (140, 160, 180),                    # 32 - Light steel blue
            64: (160, 180, 200),                    # 64 - Powder blue
            128: (180, 160, 120),                   # 128 - Dark khaki
            256: (200, 180, 100),                   # 256 - Goldenrod
            512: (220, 200, 80),                    # 512 - Gold
            1024: (240, 220, 60),                   # 1024 - Yellow
            2048: (255, 215, 0),                    # 2048 - Gold
            4096: (60, 180, 255)                    # 4096+ - Electric blue
        }
        
        # Light mode tile colors (original)
        self.light_tile_colors = {
            0: (205, 193, 180),      # Empty cell
            2: (238, 228, 218),      # 2
            4: (237, 224, 200),      # 4
            8: (242, 177, 121),      # 8
            16: (245, 149, 99),      # 16
            32: (246, 124, 95),      # 32
            64: (246, 94, 59),       # 64
            128: (237, 207, 114),    # 128
            256: (237, 204, 97),     # 256
            512: (237, 200, 80),     # 512
            1024: (237, 197, 63),    # 1024
            2048: (237, 194, 46),    # 2048
            4096: (60, 58, 50)       # 4096+
        }
        
        # Text colors for dark mode
        self.text_colors = {
            **{i: self.dark_colors['text_light'] for i in [2, 4]},  # Dark tiles get light text
            **{i: self.dark_colors['text_dark'] for i in [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]}  # Light tiles get dark text
        }
        
        # Light mode text colors
        self.light_text_colors = {
            **{i: (119, 110, 101) for i in [2, 4]},
            **{i: (249, 246, 242) for i in [8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096]}
        }
        
        self.initialize()
        
    def initialize(self):
        """Initialize 2048 game state"""
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.score = 0
        self.game_over = False
        self.won = False
        self.moved = False
        self.animations = []
        
        # Add two initial tiles
        self._add_random_tile()
        self._add_random_tile()
        
    def _add_random_tile(self):
        """Add a random tile (90% 2, 10% 4) to empty cell"""
        empty_cells = [
            (i, j) 
            for i in range(self.grid_size) 
            for j in range(self.grid_size) 
            if self.grid[i][j] == 0
        ]
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4
            
            # Add spawn animation
            self.animations.append({
                'type': 'spawn',
                'position': (i, j),
                'value': self.grid[i][j],
                'progress': 0.0
            })
        
    def update(self, delta_time: float):
        """Update game logic and animations"""
        # Update animations
        for animation in self.animations[:]:
            animation['progress'] += delta_time * 8  # Animation speed
            
            if animation['progress'] >= 1.0:
                self.animations.remove(animation)
                
    def render(self, surface: pygame.Surface):
        """Render 2048 game"""
        self._draw_background(surface)
        self._draw_grid(surface)
        self._draw_tiles(surface)
        self._draw_ui(surface)
        self._draw_developer_credit(surface)
        
    def handle_event(self, event: pygame.event.Event):
        """Handle 2048 game events"""
        if event.type == pygame.KEYDOWN:
            if not self.game_over:
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_KP8]:
                    self._move_tiles('up')
                elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_KP2]:
                    self._move_tiles('down')
                elif event.key in [pygame.K_LEFT, pygame.K_a, pygame.K_KP4]:
                    self._move_tiles('left')
                elif event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_KP6]:
                    self._move_tiles('right')
            
            # Global controls
            if event.key == pygame.K_r:
                self.initialize()  # Restart
            elif event.key == pygame.K_m:  # Toggle dark mode
                self.dark_mode = not self.dark_mode
                print(f"🌙 Dark mode: {self.dark_mode}")
            elif event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()
                
    def _move_tiles(self, direction: str):
        """Move tiles in specified direction and handle merging"""
        old_grid = [row[:] for row in self.grid]  # Copy for comparison
        self.moved = False
        
        if direction == 'left':
            self._move_left()
        elif direction == 'right':
            self._move_right()
        elif direction == 'up':
            self._move_up()
        elif direction == 'down':
            self._move_down()
            
        # Check if movement occurred
        if self.grid != old_grid:
            self.moved = True
            self._add_random_tile()
            self._check_game_state()
            
    def _move_left(self):
        """Move and merge tiles to the left"""
        for i in range(self.grid_size):
            # Remove zeros and merge
            row = [cell for cell in self.grid[i] if cell != 0]
            merged = []
            skip = False
            
            for j in range(len(row)):
                if skip:
                    skip = False
                    continue
                    
                if j + 1 < len(row) and row[j] == row[j + 1]:
                    # Merge tiles
                    new_value = row[j] * 2
                    merged.append(new_value)
                    self.score += new_value
                    skip = True
                    
                    # Add merge animation
                    self.animations.append({
                        'type': 'merge',
                        'position': (i, len(merged) - 1),
                        'value': new_value,
                        'progress': 0.0
                    })
                else:
                    merged.append(row[j])
            
            # Fill remaining with zeros
            merged.extend([0] * (self.grid_size - len(merged)))
            self.grid[i] = merged
            
    def _move_right(self):
        """Move and merge tiles to the right"""
        for i in range(self.grid_size):
            row = [cell for cell in self.grid[i] if cell != 0]
            merged = []
            skip = False
            
            for j in range(len(row) - 1, -1, -1):
                if skip:
                    skip = False
                    continue
                    
                if j - 1 >= 0 and row[j] == row[j - 1]:
                    new_value = row[j] * 2
                    merged.insert(0, new_value)
                    self.score += new_value
                    skip = True
                    
                    self.animations.append({
                        'type': 'merge',
                        'position': (i, self.grid_size - len(merged)),
                        'value': new_value,
                        'progress': 0.0
                    })
                else:
                    merged.insert(0, row[j])
            
            merged = [0] * (self.grid_size - len(merged)) + merged
            self.grid[i] = merged
            
    def _move_up(self):
        """Move and merge tiles upward"""
        for j in range(self.grid_size):
            column = [self.grid[i][j] for i in range(self.grid_size) if self.grid[i][j] != 0]
            merged = []
            skip = False
            
            for i in range(len(column)):
                if skip:
                    skip = False
                    continue
                    
                if i + 1 < len(column) and column[i] == column[i + 1]:
                    new_value = column[i] * 2
                    merged.append(new_value)
                    self.score += new_value
                    skip = True
                    
                    self.animations.append({
                        'type': 'merge',
                        'position': (len(merged) - 1, j),
                        'value': new_value,
                        'progress': 0.0
                    })
                else:
                    merged.append(column[i])
            
            merged.extend([0] * (self.grid_size - len(merged)))
            for i in range(self.grid_size):
                self.grid[i][j] = merged[i]
                
    def _move_down(self):
        """Move and merge tiles downward"""
        for j in range(self.grid_size):
            column = [self.grid[i][j] for i in range(self.grid_size) if self.grid[i][j] != 0]
            merged = []
            skip = False
            
            for i in range(len(column) - 1, -1, -1):
                if skip:
                    skip = False
                    continue
                    
                if i - 1 >= 0 and column[i] == column[i - 1]:
                    new_value = column[i] * 2
                    merged.insert(0, new_value)
                    self.score += new_value
                    skip = True
                    
                    self.animations.append({
                        'type': 'merge',
                        'position': (self.grid_size - len(merged), j),
                        'value': new_value,
                        'progress': 0.0
                    })
                else:
                    merged.insert(0, column[i])
            
            merged = [0] * (self.grid_size - len(merged)) + merged
            for i in range(self.grid_size):
                self.grid[i][j] = merged[i]
                
    def _check_game_state(self):
        """Check if game is won or lost"""
        # Check for 2048 tile (win condition)
        if not self.won:
            for row in self.grid:
                if 2048 in row:
                    self.won = True
                    break
        
        # Check for game over (no moves left)
        if not any(0 in row for row in self.grid):
            # Check if any adjacent tiles can be merged
            game_over = True
            
            # Check horizontal merges
            for i in range(self.grid_size):
                for j in range(self.grid_size - 1):
                    if self.grid[i][j] == self.grid[i][j + 1]:
                        game_over = False
                        break
            
            # Check vertical merges
            for j in range(self.grid_size):
                for i in range(self.grid_size - 1):
                    if self.grid[i][j] == self.grid[i + 1][j]:
                        game_over = False
                        break
                        
            self.game_over = game_over
        
    def _get_colors(self):
        """Get current color scheme based on dark mode"""
        if self.dark_mode:
            return self.dark_colors, self.tile_colors, self.text_colors
        else:
            return self.light_colors, self.light_tile_colors, self.light_text_colors
        
    def _draw_background(self, surface: pygame.Surface):
        """Draw game background"""
        colors, _, _ = self._get_colors()
        surface.fill(colors['background'])
        
    def _draw_grid(self, surface: pygame.Surface):
        """Draw 2048 grid"""
        board_x, board_y = self._get_board_position()
        colors, _, _ = self._get_colors()
        
        # Draw grid background
        board_rect = pygame.Rect(
            board_x - 10, board_y - 10,
            self.grid_size * self.cell_size + 20,
            self.grid_size * self.cell_size + 20
        )
        pygame.draw.rect(surface, colors['grid_bg'], board_rect, border_radius=8)
        
        # Draw cell backgrounds
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                cell_rect = pygame.Rect(
                    board_x + j * self.cell_size + 6,
                    board_y + i * self.cell_size + 6,
                    self.cell_size - 12,
                    self.cell_size - 12
                )
                pygame.draw.rect(surface, colors['empty_cell'], cell_rect, border_radius=4)
                
    def _draw_tiles(self, surface: pygame.Surface):
        """Draw all tiles with animations"""
        board_x, board_y = self._get_board_position()
        _, tile_colors, text_colors = self._get_colors()
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = self.grid[i][j]
                if value > 0:
                    self._draw_tile(surface, board_x, board_y, i, j, value, tile_colors, text_colors)
                    
        # Draw animations
        for animation in self.animations:
            i, j = animation['position']
            value = animation['value']
            progress = animation['progress']
            
            if animation['type'] == 'spawn':
                # Scale animation
                scale = progress
                self._draw_tile(surface, board_x, board_y, i, j, value, tile_colors, text_colors, scale)
            elif animation['type'] == 'merge':
                # Pulse animation
                pulse = 1.0 + 0.1 * (1.0 - abs(progress - 0.5) * 2)
                self._draw_tile(surface, board_x, board_y, i, j, value, tile_colors, text_colors, pulse)
                    
    def _draw_tile(self, surface: pygame.Surface, board_x: int, board_y: int, 
                  i: int, j: int, value: int, tile_colors: Dict, text_colors: Dict, scale: float = 1.0):
        """Draw individual tile"""
        # Get color based on value
        color_key = min(value, 4096)  # Cap at 4096 for colors
        bg_color = tile_colors.get(color_key, tile_colors[4096])
        text_color = text_colors.get(color_key, text_colors[4096])
        
        # Calculate tile size with animation scale
        base_size = self.cell_size - 12
        animated_size = int(base_size * scale)
        size_diff = base_size - animated_size
        
        tile_rect = pygame.Rect(
            board_x + j * self.cell_size + 6 + size_diff // 2,
            board_y + i * self.cell_size + 6 + size_diff // 2,
            animated_size,
            animated_size
        )
        
        # Draw tile background
        pygame.draw.rect(surface, bg_color, tile_rect, border_radius=4)
        
        # Draw tile value
        if value > 0:
            # Choose font size based on value length
            if value < 100:
                font_size = 48
            elif value < 1000:
                font_size = 40
            else:
                font_size = 32
                
            font = pygame.font.Font(None, font_size)
            text = font.render(str(value), True, text_color)
            text_rect = text.get_rect(center=tile_rect.center)
            surface.blit(text, text_rect)
        
    def _draw_ui(self, surface: pygame.Surface):
        """Draw game UI"""
        board_x, board_y = self._get_board_position()
        colors, _, _ = self._get_colors()
        
        # Score panel
        score_panel = pygame.Rect(board_x, 30, 200, 80)
        self._draw_glass_panel(surface, score_panel, colors)
        
        # Score text
        score_font = pygame.font.Font(None, 32)
        title_font = pygame.font.Font(None, 24)
        
        title_text = title_font.render("SCORE", True, colors['text_light'])
        score_text = score_font.render(str(self.score), True, colors['text_light'])
        
        surface.blit(title_text, (board_x + 20, 45))
        surface.blit(score_text, (board_x + 20, 70))
        
        # Dark mode indicator
        mode_font = pygame.font.Font(None, 20)
        mode_text = mode_font.render(f"Mode: {'Dark' if self.dark_mode else 'Light'} (M)", True, colors['text_light'])
        surface.blit(mode_text, (board_x + 220, 50))
        
        # Game state messages
        message_font = pygame.font.Font(None, 36)
        if self.won and not self.game_over:
            message_text = message_font.render("You Win! Press R to restart", True, colors['text_light'])
            surface.blit(message_text, 
                        (surface.get_width() // 2 - message_text.get_width() // 2, 
                         board_y + self.grid_size * self.cell_size + 30))
        elif self.game_over:
            message_text = message_font.render("Game Over! Press R to restart", True, colors['text_light'])
            surface.blit(message_text,
                        (surface.get_width() // 2 - message_text.get_width() // 2,
                         board_y + self.grid_size * self.cell_size + 30))
        
        # Instructions
        instruction_font = pygame.font.Font(None, 20)
        instructions = [
            "Use ARROW KEYS or WASD to move tiles",
            "Combine tiles to reach 2048",
            "R: Restart • M: Toggle Mode • ESC: Menu"
        ]
        
        for idx, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, colors['text_light'])
            surface.blit(text, (20, surface.get_height() - 80 + idx * 22))
                
    def _draw_glass_panel(self, surface: pygame.Surface, rect: pygame.Rect, colors: Dict):
        """Draw glass effect panel"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill(colors['panel_bg'])
        surface.blit(panel_surface, rect)
        
        # Border
        pygame.draw.rect(surface, colors['panel_border'], rect, 2, border_radius=6)
                
    def _draw_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit"""
        colors, _, _ = self._get_colors()
        credit_font = pygame.font.Font(None, 16)
        credit_text = "Developed by Gustavo Viana"
        
        text_surface = credit_font.render(credit_text, True, colors['text_light'])
        text_surface.set_alpha(180)
        
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 15, surface.get_height() - 15)
        
        surface.blit(text_surface, text_rect)
        
    def _get_board_position(self) -> Tuple[int, int]:
        """Calculate board position to center it on screen"""
        board_width = self.grid_size * self.cell_size
        board_height = self.grid_size * self.cell_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2 + 20
        
        return board_x, board_y
