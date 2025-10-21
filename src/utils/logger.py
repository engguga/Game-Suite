import logging
import os
from datetime import datetime
from typing import Optional

class GameLogger:
    """
    Professional logging system for Game Suite
    """
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        Initialize game logger
        
        Args:
            log_dir: Directory to store log files
            log_level: Logging level
        """
        self.log_dir = log_dir
        self._setup_logging(log_level)
        
    def _setup_logging(self, log_level: int):
        """Setup logging configuration"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        log_filename = datetime.now().strftime("game_suite_%Y%m%d_%H%M%S.log")
        log_path = os.path.join(self.log_dir, log_filename)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('GameSuite')
        
    def info(self, message: str):
        """Log informational message"""
        self.logger.info(message)
        
    def warning(self, message: str):
        """Log warning message"""
        self.logger.warning(message)
        
    def error(self, message: str):
        """Log error message"""
        self.logger.error(message)
        
    def debug(self, message: str):
        """Log debug message"""
        self.logger.debug(message)
        
    def critical(self, message: str):
        """Log critical message"""
        self.logger.critical(message)

# Global logger instance
logger = GameLogger()
