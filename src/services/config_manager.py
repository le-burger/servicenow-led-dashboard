import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigManager:
    """Manages hierarchical configuration with environment overrides"""

    def __init__(self, env: Optional[str] = None):
        self.env = env or os.getenv('DASHBOARD_ENV', 'development')
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration with environment overrides"""
        config_dir = Path('config')

        # Load base config
        base_config = self._load_yaml(config_dir / 'base.yaml')
        self.config = base_config

        # Load environment-specific config
        env_config_file = config_dir / f'{self.env}.yaml'
        if env_config_file.exists():
            env_config = self._load_yaml(env_config_file)
            self.config = self._deep_merge(self.config, env_config)

        # Load user config if exists
        user_config_file = config_dir / 'user.yaml'
        if user_config_file.exists():
            user_config = self._load_yaml(user_config_file)
            self.config = self._deep_merge(self.config, user_config)

        # Apply environment variables
        self._apply_env_vars()

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file"""
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_vars(self):
        """Override config with environment variables"""
        # Format: DASHBOARD_SECTION_KEY=value
        prefix = 'DASHBOARD_'
        for key, value in os.environ.items():
            if key.startswith(prefix):
                path = key[len(prefix):].lower().split('_')
                self._set_nested(self.config, path, value)

    def _set_nested(self, d: Dict, path: List[str], value: Any):
        """Set nested dictionary value"""
        for key in path[:-1]:
            d = d.setdefault(key, {})
        d[path[-1]] = value

    def get(self, path: str, default: Any = None) -> Any:
        """Get config value by dot notation path"""
        keys = path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
        return value if value is not None else default