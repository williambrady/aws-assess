'''
This module is responsible for loading the configuration file and providing a way to access the configuration values.
modules/config.py
'''
import os
import yaml

class ConfigLoader:
    '''
    This class is responsible for loading the configuration file and providing a way to access the configuration values.
    '''
    def __init__(self, config_file="config.yaml"):
        '''
        Initialize the ConfigLoader class with the specified config file.

        Args:
            config_file (str): The path to the configuration file.

        Returns:
            None
        '''
        # Allow overriding the config file via an environment variable
        self.config_file = os.getenv("AWS_ASSESS_CONFIG", config_file)
        self.config = self._load_config()

    def _load_config(self):
        '''
        Loads the YAML configuration file.

        Args:
            None

        Returns:
            dict: The configuration values from the file
        '''
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Warning: Config file '{self.config_file}' not found.")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config file: {e}")
            return {}

    def get(self, key, default=None):
        '''
        Get a configuration value by key.

        Args:
            key (str): The key to retrieve from the configuration.
            default (any): The default value to return if the key is not found.

        Returns:
            any: The configuration value or the default value if not found.
        '''
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def reload_config(self):
        '''
        Reloads the configuration file without creating a new instance.

        Args:
            None

        Returns:
            None
        '''
        self.config = self._load_config()
        print("Configuration reloaded.")

# Singleton instance (so you don't have to reload the config multiple times)
config = ConfigLoader()
