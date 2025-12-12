"""
Settings Manager

Handles persistent storage of system settings.
Settings are stored in a JSON file and loaded on boot.
"""

import json


class Settings:
    """
    Settings manager for persistent configuration

    Provides get/set/save methods for system configuration.
    Settings are automatically loaded on init and can be saved to disk.
    """

    DEFAULT_SETTINGS = {
        'cpu_freq_mhz': 150,  # Default CPU frequency in MHz
        'display_brightness': 255,  # Display backlight (0-255, full brightness)
        'keyboard_brightness': 80,  # Keyboard backlight (0-255, medium-high)
    }

    SETTINGS_FILE = 'settings.json'

    def __init__(self):
        """Initialize settings manager and load from file"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load()

    def get(self, key, default=None):
        """
        Get a setting value

        Args:
            key: Setting name
            default: Default value if key doesn't exist

        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set(self, key, value):
        """
        Set a setting value (in memory only, call save() to persist)

        Args:
            key: Setting name
            value: Setting value
        """
        self.settings[key] = value

    def save(self):
        """
        Save settings to disk

        Returns:
            True on success, False on error
        """
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f)
            print(f"[Settings] Saved to {self.SETTINGS_FILE}")
            return True
        except Exception as e:
            print(f"[Settings] Failed to save: {e}")
            return False

    def load(self):
        """
        Load settings from disk

        Returns:
            True on success, False on error (defaults will be used)
        """
        try:
            with open(self.SETTINGS_FILE, 'r') as f:
                loaded = json.load(f)
                # Merge loaded settings with defaults (in case new settings were added)
                self.settings.update(loaded)
            print(f"[Settings] Loaded from {self.SETTINGS_FILE}")
            return True
        except OSError:
            # File doesn't exist - use defaults
            print(f"[Settings] No settings file found, using defaults")
            return False
        except Exception as e:
            print(f"[Settings] Failed to load: {e}")
            return False

    def reset(self):
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        print("[Settings] Reset to defaults")

    def get_all(self):
        """
        Get all settings

        Returns:
            Dict of all settings
        """
        return self.settings.copy()
