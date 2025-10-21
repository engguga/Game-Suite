import pygame
from typing import List, Dict, Any, Optional, Callable
from .components.buttons import Button
from .components.panels import Panel

class MenuManager:
    """Professional menu management system for Game Suite"""
    
    def __init__(self, engine):
        self.engine = engine
        self.current_menu = "main"
        self.menus: Dict[str, Any] = {}
        self.buttons: Dict[str, Button] = {}
        self.panels: Dict[str, Panel] = {}
        self.click_cooldown = 0.0
        
        self._initialize_menus()
        
    def _initialize_menus(self):
        """Initialize all menu systems"""
        self._create_main_menu()
        self._create_game_select_menu()
        self._create_settings_menu()
        
    def _create_main_menu(self):
        """Create the main menu interface"""
        screen_width, screen_height = self.engine.screen.get_size()
        
        # Main menu buttons
        self.buttons["start_game"] = Button(
            x=screen_width // 2 - 100,
            y=screen_height // 2 - 60,
            width=200,
            height=50,
            text="Start Game",
            callback=self._on_start_game
        )
        
        self.buttons["settings"] = Button(
            x=screen_width // 2 - 100,
            y=screen_height // 2,
            width=200,
            height=50,
            text="Settings",
            callback=self._on_settings
        )
        
        self.buttons["quit"] = Button(
            x=screen_width // 2 - 100,
            y=screen_height // 2 + 60,
            width=200,
            height=50,
            text="Quit Game",
            callback=self._on_quit
        )
        
    def _create_game_select_menu(self):
        """Create game selection menu with centered layout"""
        screen_width, screen_height = self.engine.screen.get_size()
        
        # Game selection buttons - centered grid layout
        games = [
            ("Tic-Tac-Toe", "tictactoe"),
            ("Memory Game", "memory"),
            ("2048 Puzzle", "puzzle_2048"),
            ("Sliding Puzzle", "sliding"),
            ("Snake", "snake"),
            ("Sudoku", "sudoku"),
            ("Domino", "domino"),
            ("Tetris", "tetris")
        ]
        
        # Calculate centered grid position
        grid_width = 400  # Width of the button grid
        grid_height = 400  # Height of the button grid
        grid_x = (screen_width - grid_width) // 2
        grid_y = 150
        
        # Create buttons in a centered 4x2 grid
        for i, (game_name, game_id) in enumerate(games):
            row = i // 2  # 0-3 rows
            col = i % 2   # 0-1 columns
            
            # Calculate position within centered grid
            x = grid_x + col * 200 + 10  # 200px per column, 10px margin
            y = grid_y + row * 70 + 10   # 70px per row, 10px margin
            
            self.buttons[f"game_{game_id}"] = Button(
                x=x, y=y, width=180, height=50,
                text=game_name,
                callback=lambda gid=game_id: self._on_game_select(gid)
            )
        
        # Back button - centered at bottom
        self.buttons["back_to_main"] = Button(
            x=screen_width // 2 - 100,
            y=screen_height - 80,
            width=200, height=50,
            text="Back to Main",
            callback=self._on_back_to_main
        )
        
    def _create_settings_menu(self):
        """Create settings menu (placeholder)"""
        screen_width, screen_height = self.engine.screen.get_size()
        
        self.buttons["settings_back"] = Button(
            x=screen_width // 2 - 100,
            y=screen_height - 80,
            width=200, height=50,
            text="Back",
            callback=self._on_back_to_main
        )
        
    def _on_start_game(self):
        """Handle start game button click"""
        if self.click_cooldown <= 0:
            self.current_menu = "game_select"
            self.click_cooldown = 0.3  # 300ms cooldown
            print("Navigating to game selection")
        
    def _on_settings(self):
        """Handle settings button click"""
        if self.click_cooldown <= 0:
            self.current_menu = "settings"
            self.click_cooldown = 0.3
            print("Navigating to settings")
        
    def _on_quit(self):
        """Handle quit button click"""
        if self.click_cooldown <= 0:
            self.engine.running = False
        
    def _on_game_select(self, game_id: str):
        """Handle game selection"""
        if self.click_cooldown > 0:
            return
            
        print(f"Selected game: {game_id}")
        self.click_cooldown = 0.5  # 500ms cooldown for game loading
        
        # Import and switch to the selected game
        try:
            if game_id == "tictactoe":
                from games.tictactoe.game import TicTacToeGame
                self.engine.switch_to_game(TicTacToeGame)
            elif game_id == "memory":
                from games.memory.game import MemoryGame
                self.engine.switch_to_game(MemoryGame)
            elif game_id == "puzzle_2048":
                # Placeholder for 2048 game
                print("2048 game selected - not yet implemented")
            elif game_id == "sliding":
                # Placeholder for sliding puzzle
                print("Sliding puzzle selected - not yet implemented")
            elif game_id == "snake":
                from games.snake.game import SnakeGame
                self.engine.switch_to_game(SnakeGame)
            elif game_id == "sudoku":
                # Placeholder for sudoku game
                print("Sudoku game selected - not yet implemented")
            elif game_id == "domino":
                # Placeholder for domino game
                print("Domino game selected - not yet implemented")
            elif game_id == "tetris":
                # Placeholder for tetris game
                print("Tetris game selected - not yet implemented")
                
        except ImportError as e:
            print(f"Error loading game {game_id}: {e}")
            
    def _on_back_to_main(self):
        """Handle back to main menu"""
        if self.click_cooldown <= 0:
            self.current_menu = "main"
            self.click_cooldown = 0.3
        
    def handle_event(self, event: pygame.event.Event):
        """Handle menu events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            self._handle_click(mouse_pos)
            
        # Update button hover states
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            self._update_hover_states(mouse_pos)
            
    def _handle_click(self, mouse_pos):
        """Handle mouse clicks on menu elements"""
        if self.click_cooldown > 0:
            return
            
        for button_id, button in self.buttons.items():
            # Only process buttons for current menu
            if self._is_button_in_current_menu(button_id):
                if button.is_clicked(mouse_pos):
                    button.click()
                    
    def _update_hover_states(self, mouse_pos):
        """Update hover states for all buttons"""
        for button_id, button in self.buttons.items():
            if self._is_button_in_current_menu(button_id):
                button.set_hovered(button.is_clicked(mouse_pos))
                    
    def _is_button_in_current_menu(self, button_id: str) -> bool:
        """Check if button belongs to current menu"""
        if self.current_menu == "main":
            return button_id in ["start_game", "settings", "quit"]
        elif self.current_menu == "game_select":
            return button_id.startswith("game_") or button_id == "back_to_main"
        elif self.current_menu == "settings":
            return button_id == "settings_back"
        return False
        
    def update(self, delta_time: float):
        """Update menu animations and state"""
        # Update click cooldown
        if self.click_cooldown > 0:
            self.click_cooldown -= delta_time
            
        # Update buttons
        for button in self.buttons.values():
            button.update(delta_time)
            
    def render(self, surface: pygame.Surface):
        """Render current menu"""
        self._render_background(surface)
        
        if self.current_menu == "main":
            self._render_main_menu(surface)
        elif self.current_menu == "game_select":
            self._render_game_select_menu(surface)
        elif self.current_menu == "settings":
            self._render_settings_menu(surface)
            
        # Always render developer credit
        self._render_developer_credit(surface)
            
    def _render_background(self, surface: pygame.Surface):
        """Render menu background"""
        surface.fill((25, 25, 40))  # Dark blue background
        
        # Add subtle grid pattern
        for x in range(0, surface.get_width(), 40):
            pygame.draw.line(surface, (35, 35, 55), (x, 0), (x, surface.get_height()), 1)
        for y in range(0, surface.get_height(), 40):
            pygame.draw.line(surface, (35, 35, 55), (0, y), (surface.get_width(), y), 1)
            
    def _render_main_menu(self, surface: pygame.Surface):
        """Render main menu"""
        # Title
        title_font = pygame.font.Font(None, 64)
        title_text = title_font.render("GAME SUITE", True, (255, 255, 255))
        surface.blit(title_text, (surface.get_width() // 2 - title_text.get_width() // 2, 100))
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 24)
        subtitle_text = subtitle_font.render("Professional Game Collection", True, (200, 200, 200))
        surface.blit(subtitle_text, (surface.get_width() // 2 - subtitle_text.get_width() // 2, 170))
        
        # Render buttons
        for button_id in ["start_game", "settings", "quit"]:
            self.buttons[button_id].render(surface)
            
    def _render_game_select_menu(self, surface: pygame.Surface):
        """Render game selection menu"""
        # Title
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Select Game", True, (255, 255, 255))
        surface.blit(title_text, (surface.get_width() // 2 - title_text.get_width() // 2, 80))
        
        # Render game buttons in centered grid
        for button_id, button in self.buttons.items():
            if button_id.startswith("game_") or button_id == "back_to_main":
                button.render(surface)
                
    def _render_settings_menu(self, surface: pygame.Surface):
        """Render settings menu"""
        title_font = pygame.font.Font(None, 48)
        title_text = title_font.render("Settings", True, (255, 255, 255))
        surface.blit(title_text, (surface.get_width() // 2 - title_text.get_width() // 2, 80))
        
        # Placeholder settings text
        settings_font = pygame.font.Font(None, 32)
        settings_text = settings_font.render("Settings Menu - Under Development", True, (200, 200, 200))
        surface.blit(settings_text, (surface.get_width() // 2 - settings_text.get_width() // 2, 200))
        
        # Back button
        self.buttons["settings_back"].render(surface)
        
    def _render_developer_credit(self, surface: pygame.Surface):
        """Render professional developer credit with low opacity"""
        credit_font = pygame.font.Font(None, 18)
        credit_text = "Developed by Gustavo Viana"
        
        # Create surface with alpha for transparency
        text_surface = credit_font.render(credit_text, True, (200, 200, 200))
        text_surface.set_alpha(128)  # 50% opacity
        
        # Position at bottom right with margin
        text_rect = text_surface.get_rect()
        text_rect.bottomright = (surface.get_width() - 20, surface.get_height() - 20)
        
        surface.blit(text_surface, text_rect)
