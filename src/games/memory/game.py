import pygame
import random
import time
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class MemoryGame(BaseGame):
    """Professional Memory Card matching game with enhanced visuals"""
    
    def __init__(self, engine):
        super().__init__(engine, "memory")
        self.grid_size = 4  # 4x4 grid
        self.card_size = 100
        self.cards: List[Dict] = []
        self.selected_cards: List[int] = []
        self.matched_pairs = 0
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.last_selection_time = 0
        self.checking_match = False
        
        # Enhanced symbols with better visual variety
        self.symbols = [
            "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼",
            "🐨", "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🐔"
        ]
        
        self.initialize()
        
    def initialize(self):
        """Initialize memory game state"""
        # Use first N symbols based on grid size
        num_pairs = (self.grid_size * self.grid_size) // 2
        available_symbols = self.symbols[:num_pairs]
        
        # Create pairs of cards
        card_values = available_symbols + available_symbols
        random.shuffle(card_values)
        
        self.cards = []
        for i, value in enumerate(card_values):
            self.cards.append({
                'value': value,
                'revealed': False,
                'matched': False,
                'position': (i % self.grid_size, i // self.grid_size)
            })
            
        self.selected_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.last_selection_time = 0
        self.checking_match = False
        
    def update(self, delta_time: float):
        """Update memory game logic"""
        # Check if we need to process a match
        if self.checking_match and len(self.selected_cards) == 2:
            current_time = time.time()
            if current_time - self.last_selection_time > 1.0:  # 1 second delay
                self._process_match()
                self.checking_match = False
                
    def _process_match(self):
        """Process the current card match attempt"""
        card1 = self.cards[self.selected_cards[0]]
        card2 = self.cards[self.selected_cards[1]]
        
        if card1['value'] == card2['value']:
            # Match found
            card1['matched'] = True
            card2['matched'] = True
            self.matched_pairs += 1
            self.moves += 1
            
            # Check for game completion
            if self.matched_pairs == (self.grid_size * self.grid_size) // 2:
                self.game_complete = True
        else:
            # No match - hide cards
            card1['revealed'] = False
            card2['revealed'] = False
            self.moves += 1
            
        self.selected_cards = []
        
    def render(self, surface: pygame.Surface):
        """Render memory game"""
        self._draw_background(surface)
        self._draw_cards(surface)
        self._draw_ui(surface)
        self._draw_developer_credit(surface)
        
    def handle_event(self, event: pygame.event.Event):
        """Handle memory game events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_complete and len(self.selected_cards) < 2 and not self.checking_match:
                self._handle_card_click(pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.game_complete:
                self.initialize()  # Restart game
                
    def _handle_card_click(self, mouse_pos: Tuple[int, int]):
        """Handle card click"""
        board_x, board_y = self._get_board_position()
        
        for i, card in enumerate(self.cards):
            if card['matched'] or card['revealed'] or i in self.selected_cards:
                continue
                
            card_rect = pygame.Rect(
                board_x + card['position'][0] * self.card_size,
                board_y + card['position'][1] * self.card_size,
                self.card_size,
                self.card_size
            )
            
            if card_rect.collidepoint(mouse_pos):
                card['revealed'] = True
                self.selected_cards.append(i)
                
                # Start match checking if two cards are selected
                if len(self.selected_cards) == 2:
                    self.last_selection_time = time.time()
                    self.checking_match = True
                    self.game_started = True
                    
                break
                
    def _draw_background(self, surface: pygame.Surface):
        """Draw game background"""
        surface.fill((25, 25, 40))
        
    def _draw_cards(self, surface: pygame.Surface):
        """Draw all cards"""
        board_x, board_y = self._get_board_position()
        
        for card in self.cards:
            x, y = card['position']
            card_rect = pygame.Rect(
                board_x + x * self.card_size + 2,
                board_y + y * self.card_size + 2,
                self.card_size - 4,
                self.card_size - 4
            )
            
            if card['matched']:
                # Draw matched card (gold gradient)
                self._draw_gradient_rect(surface, card_rect, (255, 215, 0), (255, 165, 0))
                pygame.draw.rect(surface, (255, 195, 0), card_rect, 2, border_radius=8)
                self._draw_card_symbol(surface, card_rect, card['value'], (255, 255, 255))
            elif card['revealed']:
                # Draw revealed card (blue gradient)
                self._draw_gradient_rect(surface, card_rect, (100, 100, 200), (70, 70, 150))
                pygame.draw.rect(surface, (120, 120, 220), card_rect, 2, border_radius=8)
                self._draw_card_symbol(surface, card_rect, card['value'], (255, 255, 255))
            else:
                # Draw hidden card (dark gradient)
                self._draw_gradient_rect(surface, card_rect, (60, 60, 100), (40, 40, 80))
                pygame.draw.rect(surface, (80, 80, 120), card_rect, 2, border_radius=8)
                
                # Draw subtle card pattern
                pattern_color = (70, 70, 110)
                for i in range(0, self.card_size, 12):
                    pygame.draw.line(
                        surface, pattern_color,
                        (card_rect.left + i, card_rect.top),
                        (card_rect.left, card_rect.top + i),
                        1
                    )
                    
    def _draw_gradient_rect(self, surface: pygame.Surface, rect: pygame.Rect, 
                          color1: Tuple[int, int, int], color2: Tuple[int, int, int]):
        """Draw a gradient filled rectangle"""
        for y in range(rect.height):
            # Interpolate color
            ratio = y / rect.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.left, rect.top + y), 
                           (rect.right, rect.top + y))
                    
    def _draw_card_symbol(self, surface: pygame.Surface, rect: pygame.Rect, symbol: str, color: Tuple[int, int, int]):
        """Draw symbol on card with enhanced styling"""
        # Use a font that supports emojis better
        try:
            symbol_font = pygame.font.SysFont("segoeuiemoji", 48)
        except:
            symbol_font = pygame.font.Font(None, 48)
        
        symbol_surface = symbol_font.render(symbol, True, color)
        symbol_rect = symbol_surface.get_rect(center=rect.center)
        
        # Add subtle text shadow for better visibility
        shadow_surface = symbol_font.render(symbol, True, (0, 0, 0))
        shadow_rect = symbol_rect.move(2, 2)
        shadow_surface.set_alpha(100)
        surface.blit(shadow_surface, shadow_rect)
        
        surface.blit(symbol_surface, symbol_rect)
        
    def _draw_ui(self, surface: pygame.Surface):
        """Draw game UI"""
        # Stats with better styling
        stats_font = pygame.font.Font(None, 32)
        
        pairs_text = stats_font.render(f"Pairs: {self.matched_pairs}/{(self.grid_size * self.grid_size) // 2}", True, (255, 255, 255))
        moves_text = stats_font.render(f"Moves: {self.moves}", True, (255, 255, 255))
        
        # Add background to stats
        stats_bg = pygame.Rect(15, 15, 200, 80)
        pygame.draw.rect(surface, (40, 40, 60, 180), stats_bg, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 100), stats_bg, 2, border_radius=8)
        
        surface.blit(pairs_text, (25, 25))
        surface.blit(moves_text, (25, 60))
        
        # Game complete message
        if self.game_complete:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            
            complete_font = pygame.font.Font(None, 64)
            complete_text = complete_font.render("Congratulations!", True, (255, 215, 0))
            surface.blit(complete_text, 
                        (surface.get_width() // 2 - complete_text.get_width() // 2, 
                         surface.get_height() // 2 - 80))
            
            score_font = pygame.font.Font(None, 36)
            efficiency = (self.moves / ((self.grid_size * self.grid_size) // 2)) * 100
            score_text = score_font.render(f"Completed in {self.moves} moves ({efficiency:.1f}% efficiency)", True, (200, 200, 200))
            surface.blit(score_text,
                        (surface.get_width() // 2 - score_text.get_width() // 2,
                         surface.get_height() // 2 - 20))
            
            restart_font = pygame.font.Font(None, 24)
            restart_text = restart_font.render("Press R to play again or ESC for menu", True, (150, 150, 150))
            surface.blit(restart_text,
                        (surface.get_width() // 2 - restart_text.get_width() // 2,
                         surface.get_height() // 2 + 30))
        else:
            # Instructions with better styling
            instruction_font = pygame.font.Font(None, 20)
            instructions = [
                "Click cards to find matching pairs",
                "ESC: Return to menu"
            ]
            
            instructions_bg = pygame.Rect(15, surface.get_height() - 70, 250, 50)
            pygame.draw.rect(surface, (40, 40, 60, 180), instructions_bg, border_radius=8)
            pygame.draw.rect(surface, (80, 80, 100), instructions_bg, 2, border_radius=8)
            
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, (180, 180, 180))
                surface.blit(text, (25, surface.get_height() - 60 + i * 22))
                
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
        board_width = self.grid_size * self.card_size
        board_height = self.grid_size * self.card_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2 - 30
        
        return board_x, board_y
