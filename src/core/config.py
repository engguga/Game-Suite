import yaml
import os
from typing import Any, Dict, Optional

class Config:
    """
    Configuration manager for Game Suite
    Handles loading and accessing configuration settings
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.data: Dict[str, Any] = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file with fallback to defaults
        
        Returns:
            Dictionary containing configuration data
        """
        default_config = {
            'game': {
                'title': 'Game Suite',
                'version': '1.0.0',
                'resolution': {
                    'width': 1280,
                    'height': 720, 
                    'fullscreen': False
                }
            },
            'audio': {
                'master_volume': 0.8,
                'music_volume': 0.6,
                'sfx_volume': 0.8,
                'enabled': True
            },
            'graphics': {
                'vsync': True,
                'fps_limit': 60,
                'show_fps': True,
                'particles': True
            },
            'controls': {
                'key_repeat_delay': 200,
                'key_repeat_interval': 50
            },
            'debug': {
                'show_collisions': False,
                'log_performance': False,
                'developer_mode': False
            }
        }
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                loaded_config = yaml.safe_load(file) or {}
                return self._merge_dicts(default_config, loaded_config)
        except FileNotFoundError:
            print(f"Configuration file not found at {self.config_path}, using defaults")
            return default_config
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}, using defaults")
            return default_config
            
    def _merge_dicts(self, base: Dict, update: Dict) -> Dict:
        """
        Recursively merge two dictionaries
        
        Args:
            base: Base dictionary
            update: Dictionary with updates
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in update.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
        
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path
        
        Args:
            key_path: Dot-separated path to configuration value
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set configuration value by dot-separated path
        
        Args:
            key_path: Dot-separated path to configuration value
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        keys = key_path.split('.')
        config_dict = self.data
        
        try:
            for key in keys[:-1]:
                if key not in config_dict:
                    config_dict[key] = {}
                config_dict = config_dict[key]
                
            config_dict[keys[-1]] = value
            return True
        except (KeyError, TypeError):
            return False
            
    def save(self) -> bool:
        """
        Save current configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self.data, file, default_flow_style=False)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
