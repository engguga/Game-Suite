import pygame
import random
import time
import os
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class SlidingPuzzleGame(BaseGame):
    """Professional Sliding Puzzle Game"""
    
    def __init__(self, engine):
        super().__init__(engine, "sliding")
        self.grid_size = 3  # 3x3 grid to start
        self.cell_size = 120
        self.grid: List[List[int]] = []
        self.solved_grid: List[List[int]] = []
        self.empty_pos: Tuple[int, int] = (0, 0)
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.start_time = 0
        self.elapsed_time = 0
        self.animations: List[Dict] = []
        self.current_image = None
        self.image_loaded = False
        
        # Available grid sizes
        self.available_sizes = [3, 4, 5]
        self.current_size_index = 0
        
        # Load default puzzle image or create geometric pattern
        self._load_default_image()
        self.initialize()
        
    def _load_default_image(self):
        """Load or create a default puzzle image"""
        try:
            # Try to load an image from assets
            image_path = "assets/images/sliding/default.png"
            if os.path.exists(image_path):
                self.current_image = pygame.image.load(image_path)
                # Scale image to fit puzzle
                target_size = 800  # Large enough for all grid sizes
                self.current_image = pygame.transform.smoothscale(self.current_image, (target_size, target_size))
                self.image_loaded = True
                print("✅ Loaded sliding puzzle image")
            else:
                self._create_geometric_image()
        except:
            self._create_geometric_image()
            
    def _create_geometric_image(self):
        """Create a geometric pattern as fallback"""
        size = 800
        self.current_image = pygame.Surface((size, size))
        
        # Create an interesting geometric pattern
        colors = [
            (70, 130, 180),   # Steel blue
            (100, 150, 200),  # Light steel blue  
            (130, 170, 220),  # Lighter blue
            (160, 190, 240),  # Very light blue
        ]
        
        # Draw concentric circles
        for i in range(4):
            radius = size // 2 - i * 80
            color = colors[i]
            pygame.draw.circle(self.current_image, color, (size // 2, size // 2), radius)
            
            # Add some geometric lines
            if i < 3:
                start_angle = i * 45
                end_angle = start_angle + 180
                pygame.draw.arc(self.current_image, (255, 255, 255), 
                              (size // 4, size // 4, size // 2, size // 2),
                              start_angle * 3.14159 / 180, end_angle * 3.14159 / 180, 3)
        
        self.image_loaded = True
        print("🎨 Created geometric pattern for sliding puzzle")
        
    def initialize(self):
        """Initialize sliding puzzle game"""
        self.grid_size = self.available_sizes[self.current_size_index]
        self.cell_size = 500 // self.grid_size  # Adjust cell size based on grid
        
        # Create solved grid
        self.solved_grid = []
        value = 1
        for i in range(self.grid_size):
            row = []
            for j in range(self.grid_size):
                if i == self.grid_size - 1 and j == self.grid_size - 1:
                    row.append(0)  # Empty space
                else:
                    row.append(value)
                    value += 1
            self.solved_grid.append(row)
        
        # Start with solved grid and shuffle
        self.grid = [row[:] for row in self.solved_grid]
        self.empty_pos = (self.grid_size - 1, self.grid_size - 1)
        
        # Shuffle the puzzle (make solvable)
        self._shuffle_puzzle()
        
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.animations = []
        
    def _shuffle_puzzle(self):
        """Shuffle the puzzle with valid moves"""
        # Perform many random valid moves to shuffle
        for _ in range(100 * self.grid_size * self.grid_size):
            possible_moves = self._get_possible_moves()
            if possible_moves:
                move = random.choice(possible_moves)
                self._slide_tile(move)
                
    def _get_possible_moves(self) -> List[Tuple[int, int]]:
        """Get all possible tile positions that can slide"""
        empty_i, empty_j = self.empty_pos
        moves = []
        
        # Check all four directions
        for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_i, new_j = empty_i + di, empty_j + dj
            if 0 <= new_i < self.grid_size and 0 <= new_j < self.grid_size:
                moves.append((new_i, new_j))
                
        return moves
        
    def _slide_tile(self, tile_pos: Tuple[int, int]):
        """Slide a tile into the empty space"""
        tile_i, tile_j = tile_pos
        empty_i, empty_j = self.empty_pos
        
        # Swap tile with empty space
        self.grid[empty_i][empty_j] = self.grid[tile_i][tile_j]
        self.grid[tile_i][tile_j] = 0
        self.empty_pos = (tile_i, tile_j)
        
    def update(self, delta_time: float):
        """Update game logic"""
        if self.game_started and not self.game_complete:
            self.elapsed_time = time.time() - self.start_time
            
        # Update animations
        for animation in self.animations[:]:
            animation['progress'] += delta_time * 6  # Animation speed
            if animation['progress'] >= 1.0:
                self.animations.remove(animation)
                
        # Check for completion
        if not self.game_complete and self.grid == self.solved_grid:
            self.game_complete = True
            
    def render(self, surface: pygame.Surface):
        """Render sliding puzzle game"""
        self._draw_background(surface)
        self._draw_puzzle(surface)
        self._draw_ui(surface)
        self._draw_developer_credit(surface)
        
    def handle_event(self, event: pygame.event.Event):
        """Handle sliding puzzle events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_complete:
                self._handle_click(pygame.mouse.get_pos())
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.initialize()  # Restart
            elif event.key == pygame.K_s:
                self._switch_grid_size()
            elif event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()
                
    def _switch_grid_size(self):
        """Switch to next grid size"""
        self.current_size_index = (self.current_size_index + 1) % len(self.available_sizes)
        print(f"🔀 Switching to {self.available_sizes[self.current_size_index]}x{self.available_sizes[self.current_size_index]} grid")
        self.initialize()
                
    def _handle_click(self, mouse_pos: Tuple[int, int]):
        """Handle tile click"""
        board_x, board_y = self._get_board_position()
        
        # Convert mouse position to grid coordinates
        mouse_x, mouse_y = mouse_pos
        grid_x = (mouse_x - board_x) // self.cell_size
        grid_y = (mouse_y - board_y) // self.cell_size
        
        if 0 <= grid_x < self.grid_size and 0 <= grid_y < self.grid_size:
            clicked_pos = (grid_y, grid_x)  # Note: grid uses (row, col)
            
            # Check if clicked tile can slide
            if clicked_pos in self._get_possible_moves():
                if not self.game_started:
                    self.game_started = True
                    self.start_time = time.time()
                    
                # Add slide animation
                empty_i, empty_j = self.empty_pos
                self.animations.append({
                    'type': 'slide',
                    'from_pos': clicked_pos,
                    'to_pos': self.empty_pos,
                    'progress': 0.0
                })
                
                # Perform the move
                self._slide_tile(clicked_pos)
                self.moves += 1
                
    def _draw_background(self, surface: pygame.Surface):
        """Draw game background"""
        surface.fill((25, 25, 40))  # Dark blue background
        
    def _draw_puzzle(self, surface: pygame.Surface):
        """Draw the sliding puzzle"""
        board_x, board_y = self._get_board_position()
        
        # Draw puzzle background
        board_rect = pygame.Rect(
            board_x - 10, board_y - 10,
            self.grid_size * self.cell_size + 20,
            self.grid_size * self.cell_size + 20
        )
        pygame.draw.rect(surface, (50, 50, 70), board_rect, border_radius=8)
        
        # Draw tiles
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                value = self.grid[i][j]
                if value != 0:  # Don't draw empty space
                    self._draw_tile(surface, board_x, board_y, i, j, value)
                    
        # Draw animations
        for animation in self.animations:
            if animation['type'] == 'slide':
                self._draw_sliding_tile(surface, board_x, board_y, animation)
        
    def _draw_tile(self, surface: pygame.Surface, board_x: int, board_y: int, 
                  i: int, j: int, value: int):
        """Draw a puzzle tile"""
        tile_rect = pygame.Rect(
            board_x + j * self.cell_size + 2,
            board_y + i * self.cell_size + 2,
            self.cell_size - 4,
            self.cell_size - 4
        )
        
        # Draw tile background
        pygame.draw.rect(surface, (70, 70, 90), tile_rect, border_radius=6)
        
        if self.image_loaded and self.current_image:
            # Calculate source rectangle for image segment
            img_cell_size = self.current_image.get_width() // self.grid_size
            src_rect = pygame.Rect(
                j * img_cell_size,
                i * img_cell_size, 
                img_cell_size,
                img_cell_size
            )
            
            # Draw image segment
            segment = self.current_image.subsurface(src_rect)
            segment = pygame.transform.smoothscale(segment, (self.cell_size - 4, self.cell_size - 4))
            surface.blit(segment, tile_rect)
        else:
            # Fallback: draw numbered tile
            pygame.draw.rect(surface, (100, 100, 140), tile_rect, border_radius=6)
            
            # Draw tile number
            font = pygame.font.Font(None, 36)
            text = font.render(str(value), True, (255, 255, 255))
            text_rect = text.get_rect(center=tile_rect.center)
            surface.blit(text, text_rect)
            
        # Draw tile border
        pygame.draw.rect(surface, (90, 90, 120), tile_rect, 2, border_radius=6)
        
    def _draw_sliding_tile(self, surface: pygame.Surface, board_x: int, board_y: int, animation: Dict):
        """Draw a sliding tile animation"""
        from_i, from_j = animation['from_pos']
        to_i, to_j = animation['to_pos']
        progress = animation['progress']
        
        # Calculate current position (lerp between start and end)
        current_x = from_j + (to_j - from_j) * progress
        current_y = from_i + (to_i - from_i) * progress
        
        tile_rect = pygame.Rect(
            board_x + current_x * self.cell_size + 2,
            board_y + current_y * self.cell_size + 2,
            self.cell_size - 4,
            self.cell_size - 4
        )
        
        # Draw sliding tile (slightly highlighted)
        pygame.draw.rect(surface, (80, 80, 110), tile_rect, border_radius=6)
        
        if self.image_loaded and self.current_image:
            # Draw image segment for sliding tile
            img_cell_size = self.current_image.get_width() // self.grid_size
            src_rect = pygame.Rect(
                from_j * img_cell_size,
                from_i * img_cell_size,
                img_cell_size,
                img_cell_size
            )
            segment = self.current_image.subsurface(src_rect)
            segment = pygame.transform.smoothscale(segment, (self.cell_size - 4, self.cell_size - 4))
            surface.blit(segment, tile_rect)
        else:
            # Fallback numbered tile
            value = self.grid[to_i][to_j]  # Value is now at destination
            font = pygame.font.Font(None, 36)
            text = font.render(str(value), True, (255, 255, 255))
            text_rect = text.get_rect(center=tile_rect.center)
            surface.blit(text, text_rect)
            
        pygame.draw.rect(surface, (120, 120, 160), tile_rect, 2, border_radius=6)
        
    def _draw_ui(self, surface: pygame.Surface):
        """Draw game UI"""
        board_x, board_y = self._get_board_position()
        
        # Stats panel
        stats_panel = pygame.Rect(20, 20, 250, 120)
        self._draw_glass_panel(surface, stats_panel)
        
        # Game information
        title_font = pygame.font.Font(None, 24)
        stats_font = pygame.font.Font(None, 28)
        
        # Grid size
        size_text = title_font.render(f"Grid: {self.grid_size}x{self.grid_size}", True, (200, 200, 255))
        surface.blit(size_text, (35, 30))
        
        # Moves
        moves_text = stats_font.render(f"Moves: {self.moves}", True, (255, 255, 255))
        surface.blit(moves_text, (35, 60))
        
        # Time
        time_text = stats_font.render(f"Time: {int(self.elapsed_time)}s", True, (255, 255, 255))
        surface.blit(time_text, (35, 90))
        
        # Controls hint
        controls_font = pygame.font.Font(None, 20)
        controls_text = controls_font.render("S: Change Size • R: Restart", True, (150, 200, 150))
        surface.blit(controls_text, (35, 125))
        
        # Game complete message
        if self.game_complete:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            complete_font = pygame.font.Font(None, 48)
            complete_text = complete_font.render("Puzzle Solved!", True, (100, 255, 100))
            surface.blit(complete_text, 
                        (surface.get_width() // 2 - complete_text.get_width() // 2, 
                         surface.get_height() // 2 - 60))
            
            stats_font = pygame.font.Font(None, 32)
            stats_text = stats_font.render(f"Solved in {self.moves} moves, {int(self.elapsed_time)} seconds", True, (200, 200, 200))
            surface.blit(stats_text,
                        (surface.get_width() // 2 - stats_text.get_width() // 2,
                         surface.get_height() // 2))
            
            restart_font = pygame.font.Font(None, 24)
            restart_text = restart_font.render("Press R to play again or ESC for menu", True, (150, 150, 150))
            surface.blit(restart_text,
                        (surface.get_width() // 2 - restart_text.get_width() // 2,
                         surface.get_height() // 2 + 50))
        else:
            # Instructions
            instruction_font = pygame.font.Font(None, 20)
            instructions = [
                "Click tiles to slide them into empty space",
                "Arrange tiles in numerical order to solve",
                "ESC: Return to menu"
            ]
            
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, (180, 180, 180))
                surface.blit(text, (25, surface.get_height() - 80 + i * 22))
                
    def _draw_glass_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw glass effect panel"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill((60, 60, 80, 200))
        surface.blit(panel_surface, rect)
        
        # Border
        pygame.draw.rect(surface, (90, 90, 120), rect, 2, border_radius=6)
                
    def _draw_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit"""
        credit_font = pygame.font.Font(None, 16)
        credit_text = "Developed by Gustavo Viana"
        
        text_surface = credit_font.render(credit_text, True, (200, 200, 200))
        text_surface.set_alpha(150)
        
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 15, surface.get_height() - 15)
        
        surface.blit(text_surface, text_rect)
        
    def _get_board_position(self) -> Tuple[int, int]:
        """Calculate board position to center it on screen"""
        board_width = self.grid_size * self.cell_size
        board_height = self.grid_size * self.cell_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2
        
        return board_x, board_y
