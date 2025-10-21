import pygame
import random
import time
import os
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class MemoryGame(BaseGame):
    """Professional Memory Card matching game with image support"""
    
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
        self.current_theme = "animals"
        self.card_images = {}
        self.card_back = None
        self.themes = {
            "animals": "🐶🐱🐭🐹🐰🦊🐻🐼🐨🐯🦁🐮🐷🐸🐵🐔",
            "fruits": "🍎🍌🍒🍇🍓🍊🍋🍉🍑🍍🥭🍏🍐🥝🫐🍅",
            "symbols": "⭐🌟🔶🔷🔺🔻💠🔳🔲🔴🟢🔵🟡🟣🟤⚫"
        }
        
        self._load_assets()
        self.initialize()
        
    def _load_assets(self):
        """Load game assets"""
        # Placeholder for image loading - for now we use emojis
        # In the future, replace with actual image loading:
        # self.card_images = self._load_card_images()
        # self.card_back = self._load_card_back()
        
        # For now, we'll use enhanced emoji rendering
        try:
            self.emoji_font = pygame.font.SysFont("segoeuiemoji", 48)
        except:
            self.emoji_font = pygame.font.Font(None, 48)
            
    def _load_card_images(self):
        """Load card images from assets folder"""
        images = {}
        theme_path = f"assets/images/memory/{self.current_theme}"
        
        if os.path.exists(theme_path):
            for filename in os.listdir(theme_path):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    # Remove extension and get image number
                    name = os.path.splitext(filename)[0]
                    try:
                        image_path = os.path.join(theme_path, filename)
                        image = pygame.image.load(image_path)
                        # Scale image to fit card
                        image = pygame.transform.smoothscale(image, (self.card_size - 20, self.card_size - 20))
                        images[name] = image
                    except Exception as e:
                        print(f"Error loading image {filename}: {e}")
        
        return images
        
    def initialize(self):
        """Initialize memory game state"""
        # Get symbols for current theme
        theme_symbols = list(self.themes[self.current_theme])
        num_pairs = (self.grid_size * self.grid_size) // 2
        
        if len(theme_symbols) < num_pairs:
            # Duplicate symbols if not enough unique ones
            theme_symbols = theme_symbols * ((num_pairs // len(theme_symbols)) + 1)
            
        available_symbols = theme_symbols[:num_pairs]
        
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
            elif event.key == pygame.K_t:
                self._switch_theme()
            elif event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()
                
    def _switch_theme(self):
        """Switch to next theme"""
        themes = list(self.themes.keys())
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        self.current_theme = themes[next_index]
        self.initialize()
                
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
        # Gradient background
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(25 + (15 * ratio))
            g = int(25 + (10 * ratio))
            b = int(40 + (20 * ratio))
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))
        
    def _draw_cards(self, surface: pygame.Surface):
        """Draw all cards with enhanced visuals"""
        board_x, board_y = self._get_board_position()
        
        for card in self.cards:
            x, y = card['position']
            card_rect = pygame.Rect(
                board_x + x * self.card_size + 2,
                board_y + y * self.card_size + 2,
                self.card_size - 4,
                self.card_size - 4
            )
            
            # Card shadow
            shadow_rect = card_rect.move(4, 4)
            pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=10)
            
            if card['matched']:
                # Golden matched card with shine effect
                self._draw_gradient_rect(surface, card_rect, (255, 225, 100), (255, 165, 0))
                pygame.draw.rect(surface, (255, 195, 0), card_rect, 3, border_radius=10)
                
                # Add shine effect
                shine_rect = pygame.Rect(
                    card_rect.left + 5,
                    card_rect.top + 5,
                    card_rect.width // 3,
                    card_rect.height // 3
                )
                pygame.draw.ellipse(surface, (255, 255, 255, 100), shine_rect)
                
                self._draw_card_content(surface, card_rect, card['value'], is_matched=True)
                
            elif card['revealed']:
                # Blue revealed card
                self._draw_gradient_rect(surface, card_rect, (120, 120, 220), (80, 80, 180))
                pygame.draw.rect(surface, (150, 150, 240), card_rect, 3, border_radius=10)
                self._draw_card_content(surface, card_rect, card['value'], is_matched=False)
                
            else:
                # Hidden card with intricate pattern
                self._draw_gradient_rect(surface, card_rect, (70, 70, 120), (50, 50, 90))
                pygame.draw.rect(surface, (90, 90, 140), card_rect, 3, border_radius=10)
                
                # Draw decorative pattern
                self._draw_card_pattern(surface, card_rect)
                
                # Draw theme indicator
                theme_indicator = self.current_theme[0].upper()
                indicator_font = pygame.font.Font(None, 16)
                indicator_text = indicator_font.render(theme_indicator, True, (120, 120, 160))
                indicator_rect = indicator_text.get_rect(center=(card_rect.centerx, card_rect.centery + 20))
                surface.blit(indicator_text, indicator_rect)
                    
    def _draw_gradient_rect(self, surface: pygame.Surface, rect: pygame.Rect, 
                          color1: Tuple[int, int, int], color2: Tuple[int, int, int]):
        """Draw a gradient filled rectangle"""
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.left, rect.top + y), 
                           (rect.right, rect.top + y))
                    
    def _draw_card_pattern(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw decorative pattern on hidden cards"""
        pattern_color = (80, 80, 120)
        
        # Corner accents
        corner_size = 15
        corners = [
            (rect.left + 5, rect.top + 5),
            (rect.right - 20, rect.top + 5),
            (rect.left + 5, rect.bottom - 20),
            (rect.right - 20, rect.bottom - 20)
        ]
        
        for corner in corners:
            pygame.draw.rect(surface, pattern_color, 
                           (corner[0], corner[1], corner_size, corner_size), 2, border_radius=3)
        
        # Center design
        center_rect = pygame.Rect(
            rect.centerx - 10,
            rect.centery - 10,
            20, 20
        )
        pygame.draw.rect(surface, pattern_color, center_rect, 2, border_radius=5)
        
    def _draw_card_content(self, surface: pygame.Surface, rect: pygame.Rect, symbol: str, is_matched: bool):
        """Draw card content (symbol or image)"""
        if is_matched:
            color = (255, 255, 255)
            glow_color = (255, 255, 200, 100)
        else:
            color = (255, 255, 255)
            glow_color = (200, 200, 255, 80)
            
        # Draw symbol with glow effect
        symbol_surface = self.emoji_font.render(symbol, True, color)
        symbol_rect = symbol_surface.get_rect(center=rect.center)
        
        # Glow effect
        for offset in [3, 2, 1]:
            glow_rect = symbol_rect.move(offset, offset)
            glow_surface = self.emoji_font.render(symbol, True, glow_color[:3])
            glow_surface.set_alpha(glow_color[3] // (offset + 1))
            surface.blit(glow_surface, glow_rect)
        
        surface.blit(symbol_surface, symbol_rect)
        
    def _draw_ui(self, surface: pygame.Surface):
        """Draw game UI with enhanced styling"""
        # Stats panel with glass effect
        stats_bg = pygame.Rect(20, 20, 220, 100)
        self._draw_glass_panel(surface, stats_bg)
        
        stats_font = pygame.font.Font(None, 28)
        title_font = pygame.font.Font(None, 20)
        
        # Theme info
        theme_text = title_font.render(f"Theme: {self.current_theme.title()}", True, (200, 200, 255))
        surface.blit(theme_text, (35, 30))
        
        # Stats
        pairs_text = stats_font.render(f"Pairs: {self.matched_pairs}/{(self.grid_size * self.grid_size) // 2}", True, (255, 255, 255))
        moves_text = stats_font.render(f"Moves: {self.moves}", True, (255, 255, 255))
        
        surface.blit(pairs_text, (35, 55))
        surface.blit(moves_text, (35, 85))
        
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
            
            score_font = pygame.font.Font(None, 32)
            efficiency = ((self.grid_size * self.grid_size) // 2) / self.moves * 100 if self.moves > 0 else 0
            score_text = score_font.render(f"Completed in {self.moves} moves ({efficiency:.1f}% efficiency)", True, (200, 200, 200))
            surface.blit(score_text,
                        (surface.get_width() // 2 - score_text.get_width() // 2,
                         surface.get_height() // 2 - 20))
            
            restart_font = pygame.font.Font(None, 24)
            instructions = [
                "R: Play again",
                "T: Change theme",
                "ESC: Return to menu"
            ]
            
            for i, instruction in enumerate(instructions):
                text = restart_font.render(instruction, True, (150, 150, 150))
                surface.blit(text,
                            (surface.get_width() // 2 - text.get_width() // 2,
                             surface.get_height() // 2 + 30 + i * 25))
        else:
            # Instructions panel
            instructions_bg = pygame.Rect(20, surface.get_height() - 90, 280, 70)
            self._draw_glass_panel(surface, instructions_bg)
            
            instruction_font = pygame.font.Font(None, 18)
            instructions = [
                "Click cards to find matching pairs",
                "T: Change theme • ESC: Menu"
            ]
            
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, (180, 180, 180))
                surface.blit(text, (35, surface.get_height() - 75 + i * 20))
                
    def _draw_glass_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw a glass-like panel effect"""
        # Base with gradient
        self._draw_gradient_rect(surface, rect, (40, 40, 60, 180), (60, 60, 80, 180))
        
        # Border
        pygame.draw.rect(surface, (80, 80, 100, 200), rect, 2, border_radius=8)
        
        # Glass highlight
        highlight = pygame.Rect(rect.left + 2, rect.top + 2, rect.width - 4, 15)
        highlight_surface = pygame.Surface((highlight.width, highlight.height), pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 255, 30))
        surface.blit(highlight_surface, highlight)
                
    def _draw_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit"""
        credit_font = pygame.font.Font(None, 16)
        credit_text = "Developed by Gustavo Viana"
        
        text_surface = credit_font.render(credit_text, True, (200, 200, 200))
        text_surface.set_alpha(128)
        
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 15, surface.get_height() - 15)
        
        surface.blit(text_surface, text_rect)
        
    def _get_board_position(self) -> Tuple[int, int]:
        """Calculate board position to center it on screen"""
        board_width = self.grid_size * self.card_size
        board_height = self.grid_size * self.card_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2 - 20
        
        return board_x, board_y
