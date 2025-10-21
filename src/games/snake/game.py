import pygame
import random
from typing import List, Tuple, Optional
from ..base_game import BaseGame

class SnakeGame(BaseGame):
    """Professional Snake game implementation"""
    
    def __init__(self, engine):
        super().__init__(engine, "snake")
        self.grid_sizes = {
            "small": 15,
            "medium": 20, 
            "large": 25
        }
        self.speeds = {
            "slow": 6,
            "medium": 8,
            "fast": 12
        }
        self.current_grid_size = "medium"
        self.current_speed = "medium"
        self.grid_size = self.grid_sizes[self.current_grid_size]
        self.speed = self.speeds[self.current_speed]
        self.cell_size = 30
        self.snake: List[Tuple[int, int]] = []
        self.direction = (1, 0)  # Start moving right
        self.next_direction = (1, 0)
        self.food: Optional[Tuple[int, int]] = None
        self.game_over = False
        self.score = 0
        self.move_timer = 0.0
        self.in_menu = False
        self.size_buttons = {}
        self.speed_buttons = {}
        
        self.initialize()
        
    def initialize(self):
        """Initialize snake game state"""
        self.grid_size = self.grid_sizes[self.current_grid_size]
        self.speed = self.speeds[self.current_speed]
        
        # Adjust cell size based on grid size to fit screen
        max_grid_size = max(self.grid_sizes.values())
        self.cell_size = min(35, 600 // max_grid_size)
        
        # Start snake in the middle
        start_x = self.grid_size // 2
        start_y = self.grid_size // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.game_over = False
        self.score = 0
        self.move_timer = 0.0
        self.in_menu = False
        self._create_menu_buttons()
        self._spawn_food()
        
    def _create_menu_buttons(self):
        """Create menu selection buttons"""
        screen_width = self.engine.screen.get_width()
        screen_height = self.engine.screen.get_height()
        
        # Grid size buttons - properly centered
        button_width = 140
        button_height = 45
        start_x = screen_width // 2 - (button_width * 3 + 40) // 2
        
        self.size_buttons = {
            "small": pygame.Rect(start_x, 200, button_width, button_height),
            "medium": pygame.Rect(start_x + button_width + 20, 200, button_width, button_height),
            "large": pygame.Rect(start_x + (button_width + 20) * 2, 200, button_width, button_height)
        }
        
        # Speed buttons - properly centered below size buttons
        self.speed_buttons = {
            "slow": pygame.Rect(start_x, 280, button_width, button_height),
            "medium": pygame.Rect(start_x + button_width + 20, 280, button_width, button_height),
            "fast": pygame.Rect(start_x + (button_width + 20) * 2, 280, button_width, button_height)
        }
        
    def update(self, delta_time: float):
        """Update snake game logic"""
        if self.in_menu or self.game_over:
            return
            
        self.move_timer += delta_time
        move_interval = 1.0 / self.speed
        
        if self.move_timer >= move_interval:
            self.direction = self.next_direction
            self._move_snake()
            self.move_timer = 0.0
            
    def render(self, surface: pygame.Surface):
        """Render snake game"""
        self._draw_background(surface)
        
        if self.in_menu:
            self._draw_settings_menu(surface)
        else:
            self._draw_grid(surface)
            self._draw_snake(surface)
            self._draw_food(surface)
            self._draw_ui(surface)
            
        self._draw_developer_credit(surface)
        
    def handle_event(self, event: pygame.event.Event):
        """Handle snake game events"""
        if event.type == pygame.KEYDOWN:
            if self.in_menu:
                if event.key == pygame.K_RETURN:
                    self.in_menu = False
                elif event.key == pygame.K_ESCAPE:
                    self.engine._return_to_menu()
            elif self.game_over:
                if event.key == pygame.K_r:
                    self.initialize()
                elif event.key == pygame.K_m:
                    self.in_menu = True
                elif event.key == pygame.K_ESCAPE:
                    self.engine._return_to_menu()
            else:
                # Movement controls - Arrow keys, WASD, and Numpad
                if event.key in [pygame.K_UP, pygame.K_w, pygame.K_KP8] and self.direction != (0, 1):
                    self.next_direction = (0, -1)
                elif event.key in [pygame.K_DOWN, pygame.K_s, pygame.K_KP2] and self.direction != (0, -1):
                    self.next_direction = (0, 1)
                elif event.key in [pygame.K_LEFT, pygame.K_a, pygame.K_KP4] and self.direction != (1, 0):
                    self.next_direction = (-1, 0)
                elif event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_KP6] and self.direction != (-1, 0):
                    self.next_direction = (1, 0)
                elif event.key == pygame.K_m:
                    self.in_menu = True
                    
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.in_menu:
                self._handle_menu_selection(pygame.mouse.get_pos())
                
    def _handle_menu_selection(self, mouse_pos):
        """Handle menu selections"""
        # Check grid size buttons
        for size_name, button_rect in self.size_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                self.current_grid_size = size_name
                self.initialize()
                break
                
        # Check speed buttons
        for speed_name, button_rect in self.speed_buttons.items():
            if button_rect.collidepoint(mouse_pos):
                self.current_speed = speed_name
                self.initialize()
                break
                
    def _move_snake(self):
        """Move the snake forward"""
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # Check collision with walls
        if (new_head[0] < 0 or new_head[0] >= self.grid_size or 
            new_head[1] < 0 or new_head[1] >= self.grid_size):
            self.game_over = True
            return
            
        # Check collision with self
        if new_head in self.snake:
            self.game_over = True
            return
            
        # Move snake
        self.snake.insert(0, new_head)
        
        # Check if food eaten
        if new_head == self.food:
            self.score += 10
            self._spawn_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()
            
    def _spawn_food(self):
        """Spawn food at random position"""
        while True:
            food_pos = (random.randint(0, self.grid_size - 1), 
                       random.randint(0, self.grid_size - 1))
            if food_pos not in self.snake:
                self.food = food_pos
                break
                
    def _draw_background(self, surface: pygame.Surface):
        """Draw game background"""
        surface.fill((15, 15, 30))
        
    def _draw_grid(self, surface: pygame.Surface):
        """Draw grid lines"""
        grid_color = (40, 40, 60)
        board_x, board_y = self._get_board_position()
        
        # Draw vertical lines
        for x in range(self.grid_size + 1):
            pygame.draw.line(
                surface, grid_color,
                (board_x + x * self.cell_size, board_y),
                (board_x + x * self.cell_size, board_y + self.grid_size * self.cell_size),
                1
            )
            
        # Draw horizontal lines
        for y in range(self.grid_size + 1):
            pygame.draw.line(
                surface, grid_color,
                (board_x, board_y + y * self.cell_size),
                (board_x + self.grid_size * self.cell_size, board_y + y * self.cell_size),
                1
            )
            
    def _draw_snake(self, surface: pygame.Surface):
        """Draw the snake"""
        board_x, board_y = self._get_board_position()
        
        # Draw snake body
        for i, (x, y) in enumerate(self.snake):
            # Gradient color from head to tail
            color_value = max(80, 200 - i * 5)
            color = (100, color_value, 100) if i == 0 else (80, color_value - 20, 80)
            
            rect = pygame.Rect(
                board_x + x * self.cell_size + 1,
                board_y + y * self.cell_size + 1,
                self.cell_size - 2,
                self.cell_size - 2
            )
            pygame.draw.rect(surface, color, rect, border_radius=4)
            
            # Draw eyes on head
            if i == 0:
                eye_size = max(2, self.cell_size // 10)
                # Left eye
                left_eye_x = board_x + x * self.cell_size + self.cell_size // 3
                right_eye_x = board_x + x * self.cell_size + 2 * self.cell_size // 3
                eye_y = board_y + y * self.cell_size + self.cell_size // 3
                
                pygame.draw.circle(surface, (0, 0, 0), (left_eye_x, eye_y), eye_size)
                pygame.draw.circle(surface, (0, 0, 0), (right_eye_x, eye_y), eye_size)
                
    def _draw_food(self, surface: pygame.Surface):
        """Draw the food"""
        if not self.food:
            return
            
        board_x, board_y = self._get_board_position()
        x, y = self.food
        
        # Draw apple-like food
        food_rect = pygame.Rect(
            board_x + x * self.cell_size + 4,
            board_y + y * self.cell_size + 4,
            self.cell_size - 8,
            self.cell_size - 8
        )
        
        # Red apple with green stem
        pygame.draw.circle(surface, (255, 50, 50), food_rect.center, food_rect.width // 2 - 2)
        
        # Green stem
        stem_rect = pygame.Rect(
            food_rect.centerx - 2,
            food_rect.top - 4,
            4, 8
        )
        pygame.draw.rect(surface, (50, 180, 50), stem_rect, border_radius=2)
        
    def _draw_ui(self, surface: pygame.Surface):
        """Draw game UI"""
        # Score display
        score_font = pygame.font.Font(None, 36)
        score_text = score_font.render(f"Score: {self.score}", True, (255, 255, 255))
        surface.blit(score_text, (20, 20))
        
        # Settings display
        settings_font = pygame.font.Font(None, 28)
        size_text = settings_font.render(f"Grid: {self.current_grid_size.title()}", True, (100, 200, 255))
        speed_text = settings_font.render(f"Speed: {self.current_speed.title()}", True, (200, 200, 100))
        
        surface.blit(size_text, (20, 65))
        surface.blit(speed_text, (20, 95))
        
        # Game over message
        if self.game_over:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 64)
            game_over_text = game_over_font.render("GAME OVER", True, (255, 50, 50))
            surface.blit(game_over_text, 
                        (surface.get_width() // 2 - game_over_text.get_width() // 2, 
                         surface.get_height() // 2 - 80))
            
            score_font = pygame.font.Font(None, 36)
            final_score_text = score_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            surface.blit(final_score_text,
                        (surface.get_width() // 2 - final_score_text.get_width() // 2,
                         surface.get_height() // 2 - 20))
            
            restart_font = pygame.font.Font(None, 24)
            instructions = [
                "R: Restart game",
                "M: Change settings", 
                "ESC: Return to menu"
            ]
            
            for i, instruction in enumerate(instructions):
                text = restart_font.render(instruction, True, (200, 200, 200))
                surface.blit(text,
                            (surface.get_width() // 2 - text.get_width() // 2,
                             surface.get_height() // 2 + 30 + i * 25))
        else:
            # Instructions
            instruction_font = pygame.font.Font(None, 20)
            controls = [
                "CONTROLS:",
                "Movement: ARROWS, WASD, or NUMPAD (2,4,6,8)",
                "M: Change settings",
                "ESC: Return to menu"
            ]
            
            for i, control in enumerate(controls):
                color = (150, 200, 255) if i == 0 else (150, 150, 150)
                text = instruction_font.render(control, True, color)
                surface.blit(text, (20, surface.get_height() - 100 + i * 22))
                
    def _draw_settings_menu(self, surface: pygame.Surface):
        """Draw settings menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Game Settings", True, (255, 255, 255))
        surface.blit(title_text, (surface.get_width() // 2 - title_text.get_width() // 2, 100))
        
        # Grid Size Section
        size_font = pygame.font.Font(None, 32)
        size_title = size_font.render("Grid Size", True, (100, 200, 255))
        surface.blit(size_title, (surface.get_width() // 2 - size_title.get_width() // 2, 160))
        
        # Draw grid size buttons
        for size_name, button_rect in self.size_buttons.items():
            is_selected = size_name == self.current_grid_size
            color = (100, 200, 100) if is_selected else (70, 70, 120)
            border_color = (150, 255, 150) if is_selected else (100, 100, 150)
            
            pygame.draw.rect(surface, color, button_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, button_rect, 2, border_radius=8)
            
            # Button text - properly fitted
            button_font = pygame.font.Font(None, 22)  # Smaller font to fit
            size_display = size_name.title()
            text_surface = button_font.render(size_display, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            surface.blit(text_surface, text_rect)
            
        # Speed Section
        speed_title = size_font.render("Game Speed", True, (200, 200, 100))
        surface.blit(speed_title, (surface.get_width() // 2 - speed_title.get_width() // 2, 240))
        
        # Draw speed buttons
        for speed_name, button_rect in self.speed_buttons.items():
            is_selected = speed_name == self.current_speed
            color = (100, 200, 100) if is_selected else (70, 70, 120)
            border_color = (150, 255, 150) if is_selected else (100, 100, 150)
            
            pygame.draw.rect(surface, color, button_rect, border_radius=8)
            pygame.draw.rect(surface, border_color, button_rect, 2, border_radius=8)
            
            # Button text - properly fitted
            button_font = pygame.font.Font(None, 22)
            speed_display = speed_name.title()
            text_surface = button_font.render(speed_display, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            surface.blit(text_surface, text_rect)
            
        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "Click settings to change",
            "ENTER: Start game",
            "ESC: Return to main menu"
        ]
        
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (200, 200, 200))
            surface.blit(text, 
                        (surface.get_width() // 2 - text.get_width() // 2,
                         surface.get_height() - 150 + i * 30))
                
    def _draw_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit"""
        credit_font = pygame.font.Font(None, 18)
        credit_text = "Developed by Gustavo Viana"
        
        text_surface = credit_font.render(credit_text, True, (200, 200, 200))
        text_surface.set_alpha(128)
        
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 20, surface.get_height() - 20)
        
        surface.blit(text_surface, text_rect)
        
    def _get_board_position(self) -> Tuple[int, int]:
        """Calculate board position to center it on screen"""
        board_width = self.grid_size * self.cell_size
        board_height = self.grid_size * self.cell_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2
        
        return board_x, board_y
