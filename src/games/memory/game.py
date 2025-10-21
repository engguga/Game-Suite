import pygame
import random
import time
import os
from typing import List, Tuple, Optional, Dict
from ..base_game import BaseGame

class MemoryGame(BaseGame):
    """Professional Memory Card matching game with fruit images"""
    
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
        self.card_images = {}
        
        self._load_assets()
        self.initialize()
        
    def _load_assets(self):
        """Load fruit images from assets folder"""
        self.card_images = self._load_card_images()
        
        if not self.card_images:
            print("❌ No images found! Please add PNG images to assets/images/memory/fruits/")
        else:
            print(f"✅ Loaded {len(self.card_images)} fruit images")
            
    def _load_card_images(self):
        """Load card images from fruits folder"""
        images = {}
        theme_path = "assets/images/memory/fruits"
        
        print(f"🖼️  Loading fruit images from: {theme_path}")
        
        if os.path.exists(theme_path):
            # Get all PNG files
            image_files = [f for f in os.listdir(theme_path) 
                          if f.lower().endswith('.png')]
            
            # Sort files to maintain consistent order
            image_files.sort()
            
            print(f"📁 Found {len(image_files)} PNG files")
            
            for i, filename in enumerate(image_files):
                try:
                    image_path = os.path.join(theme_path, filename)
                    print(f"🔄 Loading: {filename}")
                    
                    # Load image
                    original_image = pygame.image.load(image_path)
                    
                    # Convert for better performance with alpha
                    if original_image.get_alpha():
                        image = original_image.convert_alpha()
                    else:
                        image = original_image.convert()
                    
                    # Calculate size to maintain aspect ratio
                    target_size = self.card_size - 20  # 10px padding on each side
                    
                    # Get original dimensions
                    original_width, original_height = image.get_size()
                    
                    # Calculate scale while maintaining aspect ratio
                    scale = min(target_size / original_width, target_size / original_height)
                    new_width = int(original_width * scale)
                    new_height = int(original_height * scale)
                    
                    # Scale image smoothly
                    image = pygame.transform.smoothscale(image, (new_width, new_height))
                    
                    # Store with index as key
                    images[str(i)] = {
                        'surface': image,
                        'width': new_width,
                        'height': new_height,
                        'name': os.path.splitext(filename)[0]
                    }
                    
                    print(f"✅ Success: {filename} -> {new_width}x{new_height}")
                    
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        else:
            print(f"⚠️  Directory not found: {theme_path}")
            
        return images
        
    def initialize(self):
        """Initialize memory game state"""
        if not self.card_images:
            print("🚨 Cannot initialize - no images loaded!")
            return
            
        # Calculate how many pairs we can make
        num_pairs_needed = (self.grid_size * self.grid_size) // 2
        available_images = list(self.card_images.keys())
        
        if len(available_images) < num_pairs_needed:
            print(f"⚠️  Not enough images! Need {num_pairs_needed}, have {len(available_images)}")
            # Use available images and duplicate if needed
            available_pairs = available_images * ((num_pairs_needed // len(available_images)) + 1)
            available_pairs = available_pairs[:num_pairs_needed]
        else:
            available_pairs = available_images[:num_pairs_needed]
        
        print(f"�� Using {len(available_pairs)} fruit pairs")
        
        # Create pairs of cards
        card_values = available_pairs + available_pairs  # Duplicate for pairs
        random.shuffle(card_values)
        
        self.cards = []
        for i, image_key in enumerate(card_values):
            self.cards.append({
                'image_key': image_key,
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
        if not self.card_images:
            return
            
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
        
        # Compare image keys for match
        if card1['image_key'] == card2['image_key']:
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
        if not self.card_images:
            self._draw_error_message(surface)
            return
            
        self._draw_background(surface)
        self._draw_cards(surface)
        self._draw_ui(surface)
        self._draw_developer_credit(surface)
        
    def _draw_error_message(self, surface: pygame.Surface):
        """Show error message if no images"""
        surface.fill((30, 30, 50))
        
        error_font = pygame.font.Font(None, 36)
        error_text = error_font.render("No fruit images found!", True, (255, 100, 100))
        instruction_font = pygame.font.Font(None, 24)
        instruction_text = instruction_font.render("Add PNG images to: assets/images/memory/fruits/", True, (200, 200, 200))
        
        surface.blit(error_text, (surface.get_width() // 2 - error_text.get_width() // 2, 200))
        surface.blit(instruction_text, (surface.get_width() // 2 - instruction_text.get_width() // 2, 250))
        
    def handle_event(self, event: pygame.event.Event):
        """Handle memory game events"""
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
            elif event.key == pygame.K_ESCAPE:
                self.engine._return_to_menu()
                
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
        """Draw professional background"""
        # Clean, subtle gradient
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(35 + (10 * ratio))
            g = int(40 + (15 * ratio))
            b = int(50 + (10 * ratio))
            pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))
        
    def _draw_cards(self, surface: pygame.Surface):
        """Draw all cards with professional styling"""
        board_x, board_y = self._get_board_position()
        
        for card in self.cards:
            x, y = card['position']
            card_rect = pygame.Rect(
                board_x + x * self.card_size + 2,
                board_y + y * self.card_size + 2,
                self.card_size - 4,
                self.card_size - 4
            )
            
            # Professional shadow effect
            shadow_rect = card_rect.move(3, 3)
            pygame.draw.rect(surface, (0, 0, 0, 80), shadow_rect, border_radius=8)
            
            if card['matched']:
                # Success state - subtle green
                self._draw_professional_card(surface, card_rect, (100, 200, 100), (80, 180, 80))
                self._draw_card_image(surface, card_rect, card['image_key'])
                
            elif card['revealed']:
                # Active state - clean white
                self._draw_professional_card(surface, card_rect, (250, 250, 250), (240, 240, 240))
                self._draw_card_image(surface, card_rect, card['image_key'])
                
            else:
                # Hidden state - professional blue
                self._draw_professional_card(surface, card_rect, (70, 100, 150), (60, 90, 140))
                self._draw_card_back(surface, card_rect)
                    
    def _draw_professional_card(self, surface: pygame.Surface, rect: pygame.Rect, 
                              color1: Tuple[int, int, int], color2: Tuple[int, int, int]):
        """Draw a professional-looking card"""
        # Smooth gradient fill
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] + (color2[0] - color1[0]) * ratio)
            g = int(color1[1] + (color2[1] - color1[1]) * ratio)
            b = int(color1[2] + (color2[2] - color1[2]) * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.left, rect.top + y), 
                           (rect.right, rect.top + y))
        
        # Clean border
        border_color = (min(255, color1[0] + 30), min(255, color1[1] + 30), min(255, color1[2] + 30))
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)
        
    def _draw_card_image(self, surface: pygame.Surface, rect: pygame.Rect, image_key: str):
        """Draw the fruit image centered on card"""
        if image_key in self.card_images:
            image_data = self.card_images[image_key]
            image_surface = image_data['surface']
            
            # Center the image on the card
            image_rect = image_surface.get_rect(center=rect.center)
            surface.blit(image_surface, image_rect)
        
    def _draw_card_back(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw professional card back design"""
        # Subtle pattern
        pattern_color = (90, 120, 170)
        
        # Center icon
        center_size = 30
        center_rect = pygame.Rect(
            rect.centerx - center_size // 2,
            rect.centery - center_size // 2,
            center_size,
            center_size
        )
        pygame.draw.rect(surface, pattern_color, center_rect, 2, border_radius=6)
        
        # Corner accents
        accent_size = 8
        accents = [
            (rect.left + 10, rect.top + 10),
            (rect.right - 18, rect.top + 10),
            (rect.left + 10, rect.bottom - 18),
            (rect.right - 18, rect.bottom - 18)
        ]
        
        for accent in accents:
            pygame.draw.rect(surface, pattern_color, 
                           (accent[0], accent[1], accent_size, accent_size), border_radius=2)
        
    def _draw_ui(self, surface: pygame.Surface):
        """Draw professional UI"""
        # Clean stats panel
        stats_bg = pygame.Rect(20, 20, 200, 80)
        self._draw_glass_panel(surface, stats_bg)
        
        stats_font = pygame.font.Font(None, 28)
        
        # Game stats
        pairs_text = stats_font.render(f"Pairs: {self.matched_pairs}/8", True, (255, 255, 255))
        moves_text = stats_font.render(f"Moves: {self.moves}", True, (255, 255, 255))
        
        surface.blit(pairs_text, (35, 35))
        surface.blit(moves_text, (35, 65))
        
        # Game complete overlay
        if self.game_complete:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))
            
            complete_font = pygame.font.Font(None, 48)
            complete_text = complete_font.render("Perfect!", True, (100, 255, 100))
            surface.blit(complete_text, 
                        (surface.get_width() // 2 - complete_text.get_width() // 2, 
                         surface.get_height() // 2 - 60))
            
            score_font = pygame.font.Font(None, 32)
            score_text = score_font.render(f"Completed in {self.moves} moves", True, (200, 200, 200))
            surface.blit(score_text,
                        (surface.get_width() // 2 - score_text.get_width() // 2,
                         surface.get_height() // 2))
            
            restart_font = pygame.font.Font(None, 24)
            restart_text = restart_font.render("Press R to play again • ESC for menu", True, (150, 150, 150))
            surface.blit(restart_text,
                        (surface.get_width() // 2 - restart_text.get_width() // 2,
                         surface.get_height() // 2 + 50))
        else:
            # Minimal instructions
            instruction_font = pygame.font.Font(None, 20)
            instructions = [
                "Click cards to find matching fruits",
                "ESC: Menu"
            ]
            
            for i, instruction in enumerate(instructions):
                text = instruction_font.render(instruction, True, (180, 180, 180))
                surface.blit(text, (25, surface.get_height() - 50 + i * 22))
                
    def _draw_glass_panel(self, surface: pygame.Surface, rect: pygame.Rect):
        """Draw glass effect panel"""
        # Semi-transparent background
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill((40, 50, 70, 200))
        surface.blit(panel_surface, rect)
        
        # Clean border
        pygame.draw.rect(surface, (80, 100, 140), rect, 1, border_radius=6)
                
    def _draw_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit"""
        credit_font = pygame.font.Font(None, 16)
        credit_text = "Developed by Gustavo Viana"
        
        text_surface = credit_font.render(credit_text, True, (150, 150, 150))
        text_surface.set_alpha(150)
        
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 15, surface.get_height() - 15)
        
        surface.blit(text_surface, text_rect)
        
    def _get_board_position(self) -> Tuple[int, int]:
        """Calculate board position to center it on screen"""
        board_width = self.grid_size * self.card_size
        board_height = self.grid_size * self.card_size
        board_x = (self.engine.screen.get_width() - board_width) // 2
        board_y = (self.engine.screen.get_height() - board_height) // 2
        
        return board_x, board_y
