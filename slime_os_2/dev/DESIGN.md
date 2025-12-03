# Slime OS 2 - Design Document

## Philosophy

**Clean, Simple, Extensible**

- No technical debt from v1
- Minimal abstraction (Pico 2040 has limited resources)
- Clean APIs that feel like a "real OS"
- Easy to understand for app developers
- Easy to extend with new devices

## Core Principles

1. **Device abstraction**: Hardware details hidden behind device profiles
2. **Clean system API**: Apps interact through `system` object, not globals
3. **Simple app model**: Easy to write new apps
4. **Minimal memory footprint**: Lazy loading, efficient data structures
5. **Extensible**: Easy to add new devices, features, and apps

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           config.py (user file)         │
│           DEVICE = "pico_calc"          │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         main.py (entry point)           │
│    Loads device, creates System,        │
│    boots Launcher                       │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│       System (OS kernel)                │
│  - Device management                    │
│  - App lifecycle                        │
│  - Graphics/Input wrappers              │
│  - Event loop                           │
└───┬─────────────────────────────────┬───┘
    │                                 │
    ▼                                 ▼
┌─────────┐                     ┌──────────┐
│ Devices │                     │   Apps   │
│ ├─ pico_calc                  │ ├─ Launcher
│ ├─ slime_deck                 │ ├─ Flashlight
│ └─ simulator                  │ └─ ...
└─────────┘                     └──────────┘
```

## Directory Structure

```
slime_os_2/
├── DESIGN.md                    # This file
├── config.py                    # User configuration (device selection)
├── main.py                      # Entry point
│
├── slime/                       # Main OS package
│   ├── __init__.py
│   ├── system.py               # System class (OS kernel)
│   ├── app.py                  # Base App class
│   │
│   ├── devices/                # Device profiles
│   │   ├── __init__.py
│   │   ├── base.py            # BaseDevice interface
│   │   ├── pico_calc.py       # Pico Calc device
│   │   └── simulator.py       # Simulator device (future)
│   │
│   └── drivers/               # Hardware drivers
│       ├── display/
│       │   ├── abstract.py   # AbstractDisplay
│       │   └── pico_calc_display.py
│       └── input/
│           ├── abstract.py   # AbstractInput
│           └── pico_calc_keyboard.py
│
├── apps/                       # Applications
│   ├── __init__.py
│   ├── launcher.py            # Built-in launcher
│   └── flashlight.py          # Example app
│
└── lib/                        # Shared utilities
    ├── __init__.py
    └── keycode.py             # Keycode constants
```

## Device Abstraction Layer

### BaseDevice Interface

```python
class BaseDevice:
    """Base device interface"""

    # Metadata
    name = "Unknown"
    display_width = 320
    display_height = 320

    # Capabilities
    has_keyboard = True
    has_display = True
    has_sd_card = False

    def create_display(self):
        """Return display driver instance"""
        raise NotImplementedError

    def create_input(self):
        """Return input driver instance"""
        raise NotImplementedError
```

### Device Example

```python
# slime/devices/pico_calc.py
class PicoCalcDevice(BaseDevice):
    name = "Pico Calc"
    display_width = 320
    display_height = 320
    has_sd_card = True

    def create_display(self):
        from slime.drivers.display.pico_calc_display import PicoCalcDisplay
        return PicoCalcDisplay(
            width=self.display_width,
            height=self.display_height,
            sck=10, mosi=11, cs=13, dc=14, reset=15, backlight=8
        )

    def create_input(self):
        from slime.drivers.input.pico_calc_keyboard import PicoCalcKeyboard
        from machine import I2C, Pin
        i2c = I2C(1, scl=Pin(7), sda=Pin(6))
        return PicoCalcKeyboard(i2c)
```

**Benefits:**
- Each device is self-contained
- No pin definitions in shared code
- Easy to add new devices (just add new file)
- Lazy imports save memory

## System API

The `System` object is the core OS interface that apps interact with.

```python
class System:
    def __init__(self, device):
        self.device = device
        self._display = None
        self._input = None

    # Display API
    @property
    def display(self):
        """Get display driver (lazy loaded)"""
        if self._display is None:
            self._display = self.device.create_display()
        return self._display

    # Convenience graphics methods
    def draw_rect(self, x, y, w, h, color):
        """Draw filled rectangle"""
        self.display.set_pen(*color)
        self.display.rectangle(x, y, w, h)

    def draw_text(self, text, x, y, scale=1, color=(255,255,255)):
        """Draw text"""
        self.display.set_pen(*color)
        self.display.text(text, x, y, scale=scale)

    def clear(self, color=(0,0,0)):
        """Clear screen to color"""
        w, h = self.display.get_bounds()
        self.draw_rect(0, 0, w, h, color)

    def update(self):
        """Update display"""
        self.display.update()

    # Input API
    @property
    def input(self):
        """Get input driver (lazy loaded)"""
        if self._input is None:
            self._input = self.device.create_input()
        return self._input

    def key_pressed(self, keycode):
        """Check if key is pressed"""
        return self.input.get_key(keycode)

    def keys_pressed(self, keycodes):
        """Check multiple keys, return dict"""
        return self.input.get_keys(keycodes)

    # App management
    def launch_app(self, app_class):
        """Launch an app"""
        # Called by OS, not by apps
        pass

    def exit_app(self):
        """Exit current app"""
        # Apps call this or just return from run()
        pass

    # Utility
    @property
    def width(self):
        return self.device.display_width

    @property
    def height(self):
        return self.device.display_height
```

**Benefits:**
- Clean, documented API
- No global state
- Familiar method names (draw_text, clear, etc.)
- Easy to mock for testing

## App Model

### Simple Generator Pattern

Apps are classes with a `run()` generator method. The OS calls `run()` and iterates it.

```python
# slime/app.py
class App:
    """Base class for all apps"""

    # App metadata (override these)
    name = "Unknown App"
    id = "unknown"

    def __init__(self, system):
        """Initialize app with system reference"""
        self.sys = system

    def run(self):
        """
        Main app loop - override this

        This is a generator. Each yield returns control to OS.
        Return or break to exit app.

        Example:
            def run(self):
                while True:
                    # Do work
                    self.sys.clear()
                    self.sys.draw_text("Hello", 10, 10)
                    self.sys.update()

                    if self.sys.key_pressed(Keycode.Q):
                        return  # Exit app

                    yield  # Return control to OS
        """
        yield  # Default: do nothing
```

### Example App (Flashlight)

```python
# apps/flashlight.py
from slime.app import App
from lib.keycode import Keycode

class FlashlightApp(App):
    name = "Flashlight"
    id = "flashlight"

    def run(self):
        led_on = True

        while True:
            # Draw UI
            if led_on:
                self.sys.clear((255, 255, 255))  # White
                self.sys.draw_text("FLASHLIGHT ON", 20, 20, scale=3, color=(0,0,0))
            else:
                self.sys.clear((0, 0, 0))  # Black
                self.sys.draw_text("FLASHLIGHT OFF", 20, 20, scale=3)

            self.sys.draw_text("[Enter] Toggle  [Q] Quit", 20, 50, scale=1)
            self.sys.update()

            # Handle input
            keys = self.sys.keys_pressed([Keycode.ENTER, Keycode.Q])

            if keys[Keycode.ENTER]:
                led_on = not led_on

            if keys[Keycode.Q]:
                return  # Exit app

            yield  # Return control to OS
```

**Benefits:**
- Very simple to understand
- No confusing intent system
- Clean system API
- Self-documenting
- No global imports needed

## Launcher

The launcher is just another app, but it's built-in and special.

```python
# apps/launcher.py
from slime.app import App
from lib.keycode import Keycode

class Launcher(App):
    name = "Launcher"
    id = "launcher"

    def __init__(self, system):
        super().__init__(system)
        self.apps = []  # List of available apps
        self.selected_index = 0

    def discover_apps(self):
        """Find all available apps"""
        # Import all apps from apps/ directory
        # Read metadata
        # Return list of app classes
        pass

    def run(self):
        self.apps = self.discover_apps()

        while True:
            # Draw app list
            self.sys.clear((0, 0, 128))  # Blue background

            y = 20
            for i, app in enumerate(self.apps):
                color = (255, 255, 0) if i == self.selected_index else (255, 255, 255)
                self.sys.draw_text(f"> {app.name}", 20, y, color=color)
                y += 20

            self.sys.update()

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.ENTER
            ])

            if keys[Keycode.UP_ARROW]:
                self.selected_index = max(0, self.selected_index - 1)

            if keys[Keycode.DOWN_ARROW]:
                self.selected_index = min(len(self.apps) - 1, self.selected_index + 1)

            if keys[Keycode.ENTER]:
                # Launch selected app
                selected_app = self.apps[self.selected_index]
                return ('launch', selected_app)  # Special return value

            yield
```

**Extensibility:**
- Easy to add settings page (just another item in list)
- Can add icons, categories, search, etc.
- Clean separation from OS core

## System Boot and Event Loop

```python
# slime/system.py
import gc

class System:
    # ... (API methods above)

    def boot(self, initial_app_class):
        """Boot OS with initial app"""
        current_app_class = initial_app_class

        while True:
            # Create app instance
            app = current_app_class(self)

            # Run app
            app_generator = app.run()

            try:
                while True:
                    result = next(app_generator)

                    # Handle return values
                    if result and isinstance(result, tuple):
                        if result[0] == 'launch':
                            current_app_class = result[1]
                            break  # Exit app loop, launch new app

            except StopIteration:
                # App returned (exited)
                current_app_class = initial_app_class  # Back to launcher

            # Cleanup
            del app
            del app_generator
            gc.collect()


# main.py
from config import DEVICE
from slime.devices import get_device
from slime.system import System
from apps.launcher import Launcher

def main():
    # Load device
    device = get_device(DEVICE)

    # Create system
    system = System(device)

    # Boot with launcher
    system.boot(Launcher)

if __name__ == '__main__':
    main()
```

## Memory Considerations

### Lazy Loading
- Drivers only imported when needed
- Apps loaded one at a time, previous app garbage collected
- Device modules not imported until selected

### Efficient Data Structures
- Simple classes, minimal overhead
- No complex inheritance hierarchies
- Generator pattern for apps (no state machine needed)

### Memory Footprint Estimate
- System core: ~5-10 KB
- Device profile: ~2 KB
- Display driver: ~15-20 KB
- Input driver: ~5-10 KB
- App (average): ~5-15 KB
- **Total**: ~35-65 KB (leaves ~135-165 KB free on Pico)

## What We're NOT Porting

- Expansion port system (for now)
- SD card mounting (for now)
- Multiple existing apps (just flashlight)
- Old config/theme system (simplify)
- Intent system (replaced with simple returns)

## What We're Improving

- Device abstraction (cleaner, more flexible)
- System API (documented, intuitive)
- App model (simpler to understand)
- Launcher (extensible design)
- No global state (everything through system object)
- Better separation of concerns

## Implementation Plan

1. **Phase 1: Core Structure**
   - Create directory structure
   - Implement BaseDevice
   - Implement PicoCalcDevice
   - Create config.py

2. **Phase 2: System Core**
   - Implement System class with API
   - Implement boot and event loop
   - Create main.py

3. **Phase 3: Drivers**
   - Port display driver (AbstractDisplay + PicoCalcDisplay)
   - Port keyboard driver (AbstractInput + PicoCalcKeyboard)
   - Test hardware initialization

4. **Phase 4: Apps**
   - Implement base App class
   - Port flashlight app
   - Test app lifecycle

5. **Phase 5: Launcher**
   - Implement simple launcher
   - App discovery
   - Test app switching

6. **Phase 6: Simulator**
   - Create SimulatorDevice
   - Implement virtual drivers
   - Test in simulator

## Questions for Review

1. **Generator pattern**: Keep the generator/yield approach for apps? (I think yes - it's clean)
2. **System API**: Are the convenience methods helpful or too much abstraction?
3. **Launcher extensibility**: Does this design make it easy to add settings/features?
4. **Device capabilities**: Do we need the `has_*` flags, or just let methods return None?
5. **App metadata**: Keep as class attributes, or use decorators/functions?

## Next Steps

Once approved:
1. Create directory structure
2. Implement core classes
3. Port drivers
4. Test on hardware
5. Add simulator support
