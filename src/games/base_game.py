from abc import ABC, abstractmethod
import pygame
import time
from typing import Dict, Any, Optional

class BaseGame(ABC):
    """
    Abstract base class for all games in the suite.
    All game implementations must inherit from this class.
    """
    
    def __init__(self, engine, game_name: str):
        """
        Initialize base game properties
        
        Args:
            engine: Reference to the main game engine
            game_name: Unique identifier for the game
        """
        self.engine = engine
        self.game_name = game_name
        self.running = True
        self.paused = False
        self.score = 0
        self.stats: Dict[str, Any] = {}
        
    @abstractmethod
    def initialize(self):
        """Initialize game-specific resources and state"""
        pass
        
    @abstractmethod
    def update(self, delta_time: float):
        """
        Update game logic
        
        Args:
            delta_time: Time elapsed since last frame in seconds
        """
        pass
        
    @abstractmethod
    def render(self, surface: pygame.Surface):
        """
        Render game to the provided surface
        
        Args:
            surface: Pygame surface to render onto
        """
        pass
        
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        """
        Handle game-specific events
        
        Args:
            event: Pygame event to process
        """
        pass
        
    def cleanup(self):
        """Cleanup game resources before switching"""
        self._save_progress()
        print(f"Cleaned up game: {self.game_name}")
        
    def _save_progress(self):
        """Save game progress to persistent storage"""
        progress_data = {
            'score': self.score,
            'stats': self.stats,
            'timestamp': time.time()
        }
        # Placeholder for save system integration
        return progress_data
        
    def pause(self):
        """Pause the game"""
        self.paused = True
        
    def resume(self):
        """Resume the game"""
        self.paused = False
        
    def exit(self):
        """Exit the game and return to menu"""
        self.running = False
