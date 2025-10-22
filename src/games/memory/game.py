import pygame
import random
import time
import os
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class MemoryGame(BaseGame):
    """Professional Memory Card Game with Multiple Themes"""
    
    def __init__(self, engine):
        super().__init__(engine, "memory")
        self.grid_size = 4  # 4x4 grid (8 pairs)
        self.card_size = 100
        self.cards: List[Dict] = []
        self.selected_cards: List[int] = []
        self.matched_pairs = 0
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.last_selection_time = 0
        self.checking_match = False
        
        # Theme management
        self.available_themes = self._discover_themes()
        self.current_theme_index = 0 if self.available_themes else -1
        self.card_images = {}
        
        if self.available_themes:
            self._load_assets()
            self.initialize()
        else:
            print("❌ No themes found with images!")
        
    def _discover_themes(self):
        """Discover available themes from assets folder"""
        themes_path = "assets/images/memory"
        themes = []
        
        if os.path.exists(themes_path):
            for item in os.listdir(themes_path):
                item_path = os.path.join(themes_path, item)
                if os.path.isdir(item_path):
                    # Check if directory has PNG files
                    png_files = [f for f in os.listdir(item_path) if f.lower().endswith('.png')]
                    if png_files:
                        themes.append(item)
                        print(f"🎨 Discovered theme: {item} ({len(png_files)} images)")
        
        return sorted(themes)  # Return sorted for consistent order
        
    def _load_assets(self):
        """Load images for current theme"""
        if not self.available_themes or self.current_theme_index == -1:
            return
            
        current_theme = self.available_themes[self.current_theme_index]
        self.card_images = self._load_theme_images(current_theme)
        
        if self.card_images:
            print(f"✅ Loaded {len(self.card_images)} images from '{current_theme}' theme")
        else:
            print(f"⚠️  No images loaded for theme '{current_theme}'")
            
    def _load_theme_images(self, theme_name: str):
        """Load and process images for a specific theme"""
        images = {}
        theme_path = f"assets/images/memory/{theme_name}"
        
        if not os.path.exists(theme_path):
            return images
            
        # Get all PNG files and sort them
        image_files = [f for f in os.listdir(theme_path) if f.lower().endswith('.png')]
        image_files.sort()
        
        for i, filename in enumerate(image_files):
            try:
                image_path = os.path.join(theme_path, filename)
                
                # Load and convert image
                original_image = pygame.image.load(image_path)
                if original_image.get_alpha():
                    image = original_image.convert_alpha()
                else:
                    image = original_image.convert()
                
                # Calculate optimal size maintaining aspect ratio
                target_size = self.card_size - 24  # 12px padding on each side
                original_width, original_height = image.get_size()
                
                scale = min(target_size / original_width, target_size / original_height)
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                
                # Scale smoothly
                image = pygame.transform.smoothscale(image, (new_width, new_height))
                
                # Store image data
                images[str(i)] = {
                    'surface': image,
                    'width': new_width,
                    'height': new_height,
                    'name': os.path.splitext(filename)[0]
                }
                
            except Exception as e:
                print(f"❌ Error loading {filename}: {e}")
                
        return images
        
    def initialize(self):
        """Initialize game state with current theme"""
        if not self.card_images:
            return
            
        # Determine how many image pairs we need
        num_pairs_needed = (self.grid_size * self.grid_size) // 2
        available_images = list(self.card_images.keys())
        
        if len(available_images) < num_pairs_needed:
            # Duplicate images if we don't have enough unique ones
            available_pairs = available_images * ((num_pairs_needed // len(available_images)) + 1)
            available_pairs = available_pairs[:num_pairs_needed]
        else:
            available_pairs = available_images[:num_pairs_needed]
        
        # Create card pairs
        card_values = available_pairs + available_pairs  # Duplicate for pairs
        random.shuffle(card_values)
        
        # Initialize cards
        self.cards = []
        for i, image_key in enumerate(card_values):
            self.cards.append({
                'image_key': image_key,
                'revealed': False,
                'matched': False,
                'position': (i % self.grid_size, i // self.grid_size)
            })
            
        # Reset game state
        self.selected_cards = []
        self.matched_pairs = 0
        self.moves = 0
        self.game_started = False
        self.game_complete = False
        self.last_selection_time = 0
        self.checking_match = False
        
    def update(self, delta_time: float):
        """Update game logic"""
        if not self.card_images:
            return
            
        # Process card matches after delay
        if self.checking_match and len(self.selected_cards) == 2:
            current_time = time.time()
            if current_time - self.last_selection_time > 1.0:
                self._process_match()
                self.checking_match = False
                
    def _process_match(self):
        """Process the current card match attempt"""
        card1 = self.cards[self.selected_cards[0]]
        card2 = self.cards[self.selected_cards[1]]
        
        if card1['image_key'] == card2['image_key']:
            # Successful match
            card1['matched'] = True
            card2['matched'] = True
            self.matched_pairs += 1
            self.moves += 1
            
            # Check for game completion
            if self.matched_pairs == (self.grid_size * self.grid_size) // 2:
                self.game_complete = True
        else:
            # Failed match - hide cards
            card1['revealed'] = False
            card2['revealed'] = False
            self.moves += 1
            
        self.selected_cards = []
        
    def render(self, surface: pygame.Surface):
        """Render the game"""
        if not self.card_images:
            self._draw_error_state(surface)
            return
            
        self._draw_background(surface)
        self._draw_game_board(surface)
        self._draw_ui(surface)
        self._draw_developer_credit(surface)
        
    def _draw_error_state(self, surface: pygame.Surface):
        """Display error state when no images are available"""
        surface.fill((25, 25, 40))
        
        title_font = pygame.font.Font(None, 48)
        message_font = pygame.font.Font(None, 28)
        
        title_text = title_font.render("No Images Available", True, (255, 100, 100))
        message_text = message_font.render("Add PNG images to assets/images/memory/", True, (200, 200, 200))
        instruction_text = message_font.render("Press ESC to return to menu", True, (150, 150, 150))
        
        surface.blit(title_text, (surface.get_width() // 2 - title_text.get_width() // 2, 200))
        surface.blit(message_text, (surface.get_width() // 2 - message_text.get_width() // 2, 270))
        surface.blit(instruction_text, (surface.get_width() // 2 - instruction_text.get_width() // 2, 320))
        
    def _draw_background(self, surface: pygame.Surface):
        """Draw professional gradient background"""
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(30 + (10 * ratio))
            g = int(35 + (10 * ratio))
            b = int(45 + (10 * ratio))
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))
        
    def _draw_game_board(self, surface: pygame.Surface):
        """Draw the card grid"""
        board_x, board_y = self._get_board_position()
        
        for card in self.cards:
            x, y = card['position']
            card_rect = pygame.Rect(
                board_x + x * self.card_size + 2,
                board_y + y * self.card_size + 2,
                self.card_size - 4,
                self.card_size - 4
            )
            
            self._draw_card(surface, card_rect, card)
        
    def _draw_card(self, surface: pygame.Surface, rect: pygame.Rect, card: Dict):
        """Draw an individual card with professional styling"""
        # Card shadow for depth
        shadow_rect = rect.move(3, 3)
        pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect, border_radius=8)
        
        if card['matched']:
            # Matched state - success green
            self._draw_card_background(surface, rect, (120, 220, 120), (100, 200, 100))
            self._draw_card_image(surface, rect, card['image_key'])
            
        elif card['revealed']:
            # Revealed state - clean white
            self._draw_card_background(surface, rect, (250, 250, 250), (240, 240, 240))
            self._draw_card_image(surface, rect, card['image_key'])
            
        else:
            # Hidden state - professional blue
            self._draw_card_background(surface, rect, (80, 110, 160), (70, 100, 150))
            self._draw_card_back_design(surface, rect)
                    
    def _draw_card_background(self, surface: pygame.Surface, rect: pygame.Rect, 
                            color1: Tuple[int, int, int], color2: Tuple[int, int, int]):
        """Draw card background with smooth gradient"""
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), (rect.left, rect.top + y), (rect.right, rect.top + y))
        
        # Professional border
        border_color = (min(255, color1[0] + 20), min(255, color1[1] + 20), min(255, color1[2] + 20))
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)
        
    def _draw_card_image(self, surface: pygame.Surface, rect: pygame.Rect, image_key: str):
        """Draw the card's image centered properly"""
        if image_key in self.card_images:
            image_data = self.card_images[image_key]
            image_surface = image_data['surface']
            image_rect = image_surface.get_rect(center=rect.center)
            surface.blit(image_surface, image_rect)
        
    def _draw_card_back_design(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw professional back design for hidden cards"""
        accent_color = (100, 130, 180)
        
        # Center geometric element
        center_size = 32
        center_rect = pygame.Rect(
            rect.centerx - center_size // 2,
            rect.centery - center_size // 2,
            center_size,
            center_size
        )
        pygame.draw.rect(surface, accent_color, center_rect, 2, border_radius=6)
        
        # Corner accents
        corner_size = 10
        corners = [
            (rect.left + 8, rect.top + 8),
            (rect.right - 18, rect.top + 8),
            (rect.left + 8, rect.bottom - 18),
            (rect.right - 18, rect.bottom - 18)
        ]
        
        for corner in corners:
            pygame.draw.rect(surface, accent_color, 
                           (corner[0], corner[1], corner_size, corner_size), border_radius=3)
        
    def _draw_ui(self, surface: pygame.Surface):
        """Draw professional user interface"""
        self._draw_info_panel(surface)
        
        if self.game_complete:
            self._draw_victory_overlay(surface)
        else:
            self._draw_instructions(surface)
        
    def _draw_info_panel(self, surface: pygame.Surface):
        """Draw game information panel"""
        panel_rect = pygame.Rect(20, 20, 240, 120)
        self._draw_glass_panel(surface, panel_rect)
        
        # Theme information
        theme_font = pygame.font.Font(None, 24)
        current_theme = self.available_themes[self.current_theme_index]
        theme_text = theme_font.render(f"Theme: {current_theme.title()}", True, (200, 220, 255))
        surface.blit(theme_text, (35, 30))
        
        # Game statistics
        stats_font = pygame.font.Font(None, 28)
        pairs_text = stats_font.render(f"Pairs: {self.matched_pairs}/8", True, (255, 255, 255))
        moves_text = stats_font.render(f"Moves: {self.moves}", True, (255, 255, 255))
        
        surface.blit(pairs_text, (35, 60))
        surface.blit(moves_text, (35, 90))
        
        # Theme switching hint
        if len(self.available_themes) > 1:
            hint_font = pygame.font.Font(None, 20)
            hint_text = hint_font.render("T - Change Theme", True, (150, 200, 150))
            surface.blit(hint_text, (35, 120))
        
    def _draw_glass_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw glass-morphism style panel"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill((40, 50, 70, 180))  # Semi-transparent dark blue
        surface.blit(panel_surface, rect)
        
        # Subtle border
        pygame.draw.rect(surface, (80, 100, 140, 200), rect, 1, border_radius=8)
        
    def _draw_victory_overlay(self, surface: pygame.Surface):
        """Draw victory screen overlay"""
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Dark overlay
        surface.blit(overlay, (0, 0))
        
        # Victory message
        victory_font = pygame.font.Font(None, 52)
        victory_text = victory_font.render("Perfect Match!", True, (100, 255, 100))
        surface.blit(victory_text, 
                    (surface.get_width() // 2 - victory_text.get_width() // 2, 
                     surface.get_height() // 2 - 80))
        
        # Statistics
        stats_font = pygame.font.Font(None, 32)
        efficiency = ((self.grid_size * self.grid_size) // 2) / self.moves * 100 if self.moves > 0 else 0
        stats_text = stats_font.render(f"Completed in {self.moves} moves", True, (220, 220, 220))
        surface.blit(stats_text,
                    (surface.get_width() // 2 - stats_text.get_width() // 2,
                     surface.get_height() // 2 - 20))
        
        # Instructions
        instruction_font = pygame.font.Font(None, 24)
        instructions = [
            "R - Play Again",
            "ESC - Main Menu"
        ]
        
        if len(self.available_themes) > 1:
            instructions.insert(1, "T - Change Theme")
            
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (180, 180, 180))
            surface.blit(text,
                        (surface.get_width() // 2 - text.get_width() // 2,
                         surface.get_height() // 2 + 30 + i * 28))
        
    def _draw_instructions(self, surface: pygame.Surface):
        """Draw game instructions"""
        instruction_font = pygame.font.Font(None, 20)
        instructions = [
            "Click cards to find matching pairs",
            "ESC - Return to Menu"
        ]
        
        if len(self.available_themes) > 1:
            instructions.insert(1, "T - Change Theme")
            
        for i, instruction in enumerate(instructions):
            text = instruction_font.render(instruction, True, (180, 180, 180))
            surface.blit(text, (25, surface.get_height() - 70 + i * 22))
                
    def _draw_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit"""
        credit_font = pygame.font.Font(None, 16)
        credit_text = "Developed by Gustavo Viana"
        
        text_surface = credit_font.render(credit_text, True, (150, 150, 150))
        text_surface.set_alpha(160)  # Subtle but readable
        
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 15, surface.get_height() - 15)
        
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event: pygame.event.Event):
        """Handle game events"""
        if not self.card_images:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()
            return
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.game_complete and len(self.selected_cards) < 2 and not self.checking_match:
                self._handle_card_click(pygame.mouse.get_pos())
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.game_complete:
                self.initialize()  # Restart game
            elif event.key == pygame.K_t and len(self.available_themes) > 1:
                self._switch_theme()
            elif event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()
                
    def _switch_theme(self):
        """Switch to the next available theme"""
        self.current_theme_index = (self.current_theme_index + 1) % len(self.available_themes)
        new_theme = self.available_themes[self.current_theme_index]
        print(f"🔄 Switching to theme: {new_theme}")
        
        self._load_assets()
        self.initialize()
                
    def _handle_card_click(self, mouse_pos: Tuple[int, int]):
        """Handle player card selection"""
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
                
                # Start match checking when two cards are selected
                if len(self.selected_cards) == 2:
                    self.last_selection_time = time.time()
                    self.checking_match = True
                    self.game_started = True
                break
        
    def _get_board_position(self) -> Tuple[int, int]:
        """Calculate centered board position"""
        board_width = self.grid_size * self.card_size
        board_height = self.grid_size * self.card_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2
        
        return board_x, board_y
