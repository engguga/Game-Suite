import pygame
import random
from typing import List, Tuple, Optional
from ..base_game import BaseGame

class TicTacToeGame(BaseGame):
    """Professional Tic-Tac-Toe implementation with AI"""
    
    def __init__(self, engine):
        super().__init__(engine, "tictactoe")
        self.board_size = 3
        self.cell_size = 100
        self.board_margin = 50
        self.board: List[List[Optional[str]]] = []
        self.current_player = "X"
        self.game_over = False
        self.winner: Optional[str] = None
        self.winning_line: Optional[List[Tuple[int, int]]] = None
        
        self.initialize()
        
    def initialize(self):
        """Initialize game state"""
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None
        self.winning_line = None
        
    def update(self, delta_time: float):
        """Update game logic"""
        # AI move if it's computer's turn and game isn't over
        if not self.game_over and self.current_player == "O":
            self._make_ai_move()
            
    def render(self, surface: pygame.Surface):
        """Render game to surface"""
        self._draw_board(surface)
        self._draw_status(surface)
        self._draw_developer_credit(surface)
        
    def handle_event(self, event: pygame.event.Event):
        """Handle game events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_over and self.current_player == "X":
                self._handle_click(pygame.mouse.get_pos())
                
    def _draw_board(self, surface: pygame.Surface):
        """Draw Tic-Tac-Toe board"""
        board_width = self.board_size * self.cell_size
        board_height = self.board_size * self.cell_size
        board_x = (surface.get_width() - board_width) // 2
        board_y = (surface.get_height() - board_height) // 2 - 50
        
        # Draw board background
        board_rect = pygame.Rect(board_x - 10, board_y - 10, 
                               board_width + 20, board_height + 20)
        pygame.draw.rect(surface, (50, 50, 80), board_rect, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 120), board_rect, 2, border_radius=8)
        
        # Draw grid lines
        for i in range(1, self.board_size):
            # Vertical lines
            x = board_x + i * self.cell_size
            pygame.draw.line(surface, (100, 100, 140), 
                           (x, board_y), (x, board_y + board_height), 4)
            # Horizontal lines
            y = board_y + i * self.cell_size
            pygame.draw.line(surface, (100, 100, 140),
                           (board_x, y), (board_x + board_width, y), 4)
        
        # Draw X's and O's
        for row in range(self.board_size):
            for col in range(self.board_size):
                cell_value = self.board[row][col]
                if cell_value:
                    cell_rect = pygame.Rect(
                        board_x + col * self.cell_size + 10,
                        board_y + row * self.cell_size + 10,
                        self.cell_size - 20,
                        self.cell_size - 20
                    )
                    
                    if cell_value == "X":
                        self._draw_x(surface, cell_rect)
                    else:
                        self._draw_o(surface, cell_rect)
        
        # Draw winning line
        if self.winning_line:
            self._draw_winning_line(surface, board_x, board_y)
            
    def _draw_x(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw X symbol"""
        color = (255, 100, 100)  # Red for X
        pygame.draw.line(surface, color, 
                        rect.topleft, rect.bottomright, 8)
        pygame.draw.line(surface, color,
                        rect.topright, rect.bottomleft, 8)
        
    def _draw_o(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw O symbol"""
        color = (100, 100, 255)  # Blue for O
        pygame.draw.ellipse(surface, color, rect, 8)
        
    def _draw_winning_line(self, surface: pygame.Surface, board_x: int, board_y: int):
        """Draw line through winning cells"""
        if not self.winning_line:
            return
            
        start_row, start_col = self.winning_line[0]
        end_row, end_col = self.winning_line[-1]
        
        start_x = board_x + start_col * self.cell_size + self.cell_size // 2
        start_y = board_y + start_row * self.cell_size + self.cell_size // 2
        end_x = board_x + end_col * self.cell_size + self.cell_size // 2
        end_y = board_y + end_row * self.cell_size + self.cell_size // 2
        
        pygame.draw.line(surface, (255, 255, 0), (start_x, start_y), (end_x, end_y), 6)
        
    def _draw_status(self, surface: pygame.Surface):
        """Draw game status information"""
        status_font = pygame.font.Font(None, 36)
        
        if self.game_over:
            if self.winner:
                status_text = f"Player {self.winner} Wins!"
                color = (255, 255, 0)  # Yellow for win
            else:
                status_text = "Game Draw!"
                color = (200, 200, 200)  # Gray for draw
        else:
            status_text = f"Player {self.current_player}'s Turn"
            color = (255, 255, 255)  # White for ongoing game
            
        text_surface = status_font.render(status_text, True, color)
        surface.blit(text_surface, 
                    (surface.get_width() // 2 - text_surface.get_width() // 2, 
                     surface.get_height() - 100))
        
        # Draw instructions
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = "Click to place X | ESC to return to menu"
        instruction_surface = instruction_font.render(instruction_text, True, (150, 150, 150))
        surface.blit(instruction_surface,
                    (surface.get_width() // 2 - instruction_surface.get_width() // 2,
                     surface.get_height() - 50))
        
    def _draw_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit"""
        credit_font = pygame.font.Font(None, 18)
        credit_text = "Developed by Gustavo Viana"
        
        # Create surface with alpha for transparency
        text_surface = credit_font.render(credit_text, True, (200, 200, 200))
        text_surface.set_alpha(128)  # 50% opacity
        
        # Position at bottom right with margin
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 20, surface.get_height() - 20)
        
        surface.blit(text_surface, text_rect)
        
    def _handle_click(self, mouse_pos):
        """Handle player click on board"""
        board_width = self.board_size * self.cell_size
        board_height = self.board_size * self.cell_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2 - 50
        
        # Check if click is within board bounds
        if (board_x <= mouse_pos[0] <= board_x + board_width and
            board_y <= mouse_pos[1] <= board_y + board_height):
            
            # Calculate grid position
            col = (mouse_pos[0] - board_x) // self.cell_size
            row = (mouse_pos[1] - board_y) // self.cell_size
            
            if 0 <= row < self.board_size and 0 <= col < self.board_size:
                self._make_move(row, col)
                
    def _make_move(self, row: int, col: int):
        """Make a move at specified position"""
        if self.board[row][col] is None and not self.game_over:
            self.board[row][col] = self.current_player
            self._check_game_state()
            
            if not self.game_over:
                self.current_player = "O" if self.current_player == "X" else "X"
                
    def _make_ai_move(self):
        """Make AI move with simple strategy"""
        # Simple AI: try to win, then block, then random
        move = self._find_winning_move("O") or self._find_winning_move("X") or self._find_random_move()
        
        if move:
            # Add small delay for natural feel
            pygame.time.delay(500)
            self._make_move(move[0], move[1])
            
    def _find_winning_move(self, player: str) -> Optional[Tuple[int, int]]:
        """Find a winning move for specified player"""
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is None:
                    # Test if this move would win
                    self.board[row][col] = player
                    if self._check_winner() == player:
                        self.board[row][col] = None
                        return (row, col)
                    self.board[row][col] = None
        return None
        
    def _find_random_move(self) -> Optional[Tuple[int, int]]:
        """Find a random valid move"""
        empty_cells = [(r, c) for r in range(self.board_size) for c in range(self.board_size) 
                      if self.board[r][c] is None]
        return random.choice(empty_cells) if empty_cells else None
        
    def _check_game_state(self):
        """Check if game has ended"""
        winner = self._check_winner()
        if winner:
            self.winner = winner
            self.game_over = True
        elif self._is_board_full():
            self.game_over = True
            
    def _check_winner(self) -> Optional[str]:
        """Check if there's a winner"""
        # Check rows
        for row in range(self.board_size):
            if self.board[row][0] and all(self.board[row][0] == self.board[row][col] for col in range(self.board_size)):
                self.winning_line = [(row, col) for col in range(self.board_size)]
                return self.board[row][0]
                
        # Check columns
        for col in range(self.board_size):
            if self.board[0][col] and all(self.board[0][col] == self.board[row][col] for row in range(self.board_size)):
                self.winning_line = [(row, col) for row in range(self.board_size)]
                return self.board[0][col]
                
        # Check diagonals
        if self.board[0][0] and all(self.board[0][0] == self.board[i][i] for i in range(self.board_size)):
            self.winning_line = [(i, i) for i in range(self.board_size)]
            return self.board[0][0]
            
        if self.board[0][self.board_size-1] and all(self.board[0][self.board_size-1] == self.board[i][self.board_size-1-i] for i in range(self.board_size)):
            self.winning_line = [(i, self.board_size-1-i) for i in range(self.board_size)]
            return self.board[0][self.board_size-1]
            
        return None
        
    def _is_board_full(self) -> bool:
        """Check if board is completely filled"""
        return all(self.board[row][col] is not None 
                  for row in range(self.board_size) for col in range(self.board_size))
