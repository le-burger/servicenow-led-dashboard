import importlib
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Any, Type, Optional


class PluginManager:
    """Manages dynamic loading of plugins"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.logger = logging.getLogger(__name__)
        self.plugins: Dict[str, Dict[str, Any]] = {
            'screens': {},
            'data_sources': {},
            'displays': {}
        }
        self.instances: Dict[str, Any] = {}

    def discover_plugins(self):
        """Discover all available plugins"""
        self.logger.info("Discovering plugins...")

        # Built-in plugins
        self._load_builtin_plugins()

        # External plugins
        self._load_external_plugins()

        # Log discovered plugins
        for plugin_type, plugins in self.plugins.items():
            self.logger.info(f"Found {len(plugins)} {plugin_type} plugins")

    def _load_builtin_plugins(self):
        """Load built-in plugins from src directory"""
        plugin_dirs = {
            'screens': Path('src/screens'),
            'data_sources': Path('src/data_sources'),
            'displays': Path('src/displays')
        }

        for plugin_type, directory in plugin_dirs.items():
            if directory.exists():
                for file in directory.glob('*.py'):
                    if file.name not in ['__init__.py', 'base.py']:
                        self._load_plugin_file(file, plugin_type)

    def _load_external_plugins(self):
        """Load external plugins from plugins directory"""
        plugin_dirs = {
            'screens': Path('plugins/screens'),
            'data_sources': Path('plugins/data_sources')
        }

        for plugin_type, directory in plugin_dirs.items():
            if directory.exists():
                for file in directory.glob('*.py'):
                    if file.name != '__init__.py':
                        self._load_plugin_file(file, plugin_type)

    def _load_plugin_file(self, file: Path, plugin_type: str):
        """Load a single plugin file"""
        module_name = file.stem
        module_path = str(file).replace('/', '.').replace('.py', '')

        try:
            module = importlib.import_module(module_path)

            # Find plugin classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and
                        not name.startswith('_') and
                        obj.__module__ == module.__name__):
                    self.register_plugin(plugin_type, name, obj)
                    self.logger.debug(f"Loaded plugin: {plugin_type}/{name}")

        except Exception as e:
            self.logger.error(f"Failed to load plugin {file}: {e}")

    def register_plugin(self, plugin_type: str, name: str, plugin_class: Type):
        """Register a plugin"""
        self.plugins[plugin_type][name] = {
            'class': plugin_class,
            'config': self.config.get(f'plugins.{plugin_type}.{name}', {})
        }

    def get_plugin(self, plugin_type: str, name: str) -> Any:
        """Get or create plugin instance"""
        instance_key = f"{plugin_type}.{name}"

        if instance_key not in self.instances:
            if name not in self.plugins[plugin_type]:
                raise ValueError(f"Plugin {name} not found in {plugin_type}")

            plugin_info = self.plugins[plugin_type][name]
            self.instances[instance_key] = plugin_info['class'](plugin_info['config'])
            self.logger.debug(f"Created instance: {instance_key}")

        return self.instances[instance_key]

    def get_all_plugins(self, plugin_type: str) -> List[str]:
        """Get list of available plugins of a type"""
        return list(self.plugins.get(plugin_type, {}).keys())