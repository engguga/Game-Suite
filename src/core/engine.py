import pygame
import time
from typing import Optional, Dict, Any

class GameEngine:
    """Main game engine for Game Suite"""
    
    def __init__(self):
        self._initialize_pygame()
        self.running = True
        self.current_game = None
        self.game_state = "MENU"
        self.config = self._load_config()
        
        # Initialize systems
        self._initialize_systems()
        
    def _initialize_pygame(self):
        """Initialize Pygame systems"""
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Game Suite - Professional Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def _initialize_systems(self):
        """Initialize game systems"""
        from ui.menu_manager import MenuManager
        self.menu_manager = MenuManager(self)
        
    def _load_config(self):
        """Load engine configuration"""
        return {
            'fps_target': 60,
            'show_fps': True,
            'debug_mode': False
        }
        
    def run(self):
        """Main game loop"""
        print("Engine started - Main loop running")
        
        while self.running:
            delta_time = self.clock.tick(self.config['fps_target']) / 1000.0
            self._handle_events()
            self._update(delta_time)
            self._render()
            
        self._cleanup()
        
    def _handle_events(self):
        """Process system events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
                
            # Delegate events to current system
            if self.game_state == "MENU":
                self.menu_manager.handle_event(event)
            elif self.game_state == "GAMEPLAY" and self.current_game:
                self.current_game.handle_event(event)
                
    def _handle_keydown(self, event):
        """Handle keyboard input"""
        if event.key == pygame.K_ESCAPE:
            if self.game_state == "GAMEPLAY":
                self._return_to_menu()
            else:
                self.running = False
        elif event.key == pygame.K_F1:
            self.config['show_fps'] = not self.config['show_fps']
        elif event.key == pygame.K_F3:
            self.config['debug_mode'] = not self.config['debug_mode']
            
    def _update(self, delta_time: float):
        """Update game logic"""
        if self.game_state == "MENU":
            self.menu_manager.update(delta_time)
        elif self.game_state == "GAMEPLAY" and self.current_game:
            self.current_game.update(delta_time)
            
    def _render(self):
        """Render current frame"""
        # Clear screen with professional dark blue
        self.screen.fill((25, 25, 40))
        
        # Render current state
        if self.game_state == "MENU":
            self.menu_manager.render(self.screen)
        elif self.game_state == "GAMEPLAY" and self.current_game:
            self.current_game.render(self.screen)
            
        # Render debug information
        if self.config['show_fps']:
            self._render_debug_info()
            
        pygame.display.flip()
        
    def _render_debug_info(self):
        """Render debug information overlay"""
        fps = self.clock.get_fps()
        fps_text = self.small_font.render(f"FPS: {fps:.1f}", True, (0, 255, 0))
        self.screen.blit(fps_text, (10, 10))
        
        if self.config['debug_mode']:
            debug_info = [
                f"Game State: {self.game_state}",
                f"Active Game: {self.current_game.__class__.__name__ if self.current_game else 'None'}",
                f"Screen: 1280x720"
            ]
            
            for i, info in enumerate(debug_info):
                text = self.small_font.render(info, True, (255, 255, 0))
                self.screen.blit(text, (10, 40 + i * 20))
        
    def _cleanup(self):
        """Cleanup resources before exit"""
        if self.current_game:
            self.current_game.cleanup()
        pygame.quit()
        print("Game Suite shutdown complete")
        
    def switch_to_game(self, game_class):
        """Switch to a different game"""
        if self.current_game:
            self.current_game.cleanup()
            
        self.current_game = game_class(self)
        self.game_state = "GAMEPLAY"
        print(f"Switched to game: {game_class.__name__}")
        
    def _return_to_menu(self):
        """Return to main menu from game"""
        if self.current_game:
            self.current_game.cleanup()
            self.current_game = None
            
        self.game_state = "MENU"
        print("Returned to main menu")
