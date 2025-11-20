# Slime OS 2

A clean, simple operating system for embedded devices with displays and keyboards.

## Features

- **Clean Architecture**: Device abstraction, simple app model, no global state
- **Exception Handling**: Apps crash gracefully with error screen
- **Watchdog Support**: Optional hardware watchdog prevents system hangs
- **Memory Efficient**: Lazy loading, garbage collection, fits on Pico (264KB RAM)
- **Easy to Extend**: Add new devices by creating device profiles
- **Simple App Development**: Clear API, well-documented base class

## Quick Start

### 1. Configure Your Device

Edit `config.py`:

```python
DEVICE = "pico_calc"  # Your device name
WATCHDOG_TIMEOUT = None  # or number of seconds
```

### 2. Upload to Hardware

Upload all files to your device:
- slime_os_2/ (entire directory)

### 3. Run

```python
import main
main.main()
```

Or configure your device to run main.py on boot.

## Directory Structure

```
slime_os_2/
├── config.py              # User configuration
├── main.py                # Entry point
│
├── slime/                 # OS core
│   ├── system.py         # System class (OS kernel)
│   ├── app.py            # Base App class
│   │
│   ├── devices/          # Device profiles
│   │   ├── base.py       # BaseDevice interface
│   │   └── pico_calc.py  # Pico Calc device
│   │
│   └── drivers/          # Hardware drivers
│       ├── display/
│       └── input/
│
├── apps/                  # Applications
│   ├── launcher.py       # App selector
│   └── flashlight.py     # Example app
│
└── lib/                   # Shared libraries
    └── keycode.py        # Keycode constants
```

## Writing Apps

### Minimal App

```python
from slime.app import App
from lib.keycode import Keycode

class MyApp(App):
    name = "My App"
    id = "my_app"

    def run(self):
        while True:
            # Draw
            self.sys.clear((0, 0, 0))
            self.sys.draw_text("Hello World", 10, 10)
            self.sys.update()

            # Input
            if self.sys.key_pressed(Keycode.Q):
                return  # Exit

            yield  # Return control to OS
```

### System API

The `self.sys` object provides:

**Display:**
- `sys.width`, `sys.height` - Display dimensions
- `sys.clear(color)` - Clear screen to color
- `sys.draw_rect(x, y, w, h, color)` - Draw rectangle
- `sys.draw_text(text, x, y, scale, color)` - Draw text
- `sys.draw_line(x1, y1, x2, y2, color)` - Draw line
- `sys.draw_pixel(x, y, color)` - Draw pixel
- `sys.measure_text(text, scale)` - Get text width
- `sys.update()` - Flip buffer to screen

**Input:**
- `sys.key_pressed(keycode)` - Check single key
- `sys.keys_pressed([keycodes])` - Check multiple keys

**Utility:**
- `sys.memory_info()` - Get memory usage
- `sys.device` - Device instance

Colors are RGB tuples: `(r, g, b)` where each value is 0-255.

### App Guidelines

1. **Always yield regularly** (at least every 100ms)
2. **Keep iterations fast** (< 100ms per yield)
3. **Return to exit** app (goes back to launcher)
4. **Return ('launch', AppClass)** to launch another app
5. **Handle errors gracefully** when possible

### Example: Full App

```python
from slime.app import App
from lib.keycode import Keycode

class CounterApp(App):
    name = "Counter"
    id = "counter"

    def run(self):
        count = 0

        while True:
            # Draw UI
            self.sys.clear((0, 0, 128))  # Blue
            self.sys.draw_text("COUNTER", 10, 10, scale=2)
            self.sys.draw_text(str(count), 10, 50, scale=3)
            self.sys.draw_text("[Up] +1  [Down] -1", 10, 100)
            self.sys.draw_text("[Q] Quit", 10, 120)
            self.sys.update()

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.Q
            ])

            if keys[Keycode.UP_ARROW]:
                count += 1
            if keys[Keycode.DOWN_ARROW]:
                count -= 1
            if keys[Keycode.Q]:
                return

            yield
```

## Adding New Devices

### 1. Create Device Profile

Create `slime/devices/my_device.py`:

```python
from .base import BaseDevice

class MyDevice(BaseDevice):
    name = "My Device"
    display_width = 240
    display_height = 240

    # Pin definitions
    DISPLAY_SCK = 18
    # ... etc

    def create_display(self):
        from slime.drivers.display.my_display import MyDisplay
        return MyDisplay(...)

    def create_input(self):
        from slime.drivers.input.my_keyboard import MyKeyboard
        return MyKeyboard(...)
```

### 2. Register Device

Edit `slime/devices/__init__.py`:

```python
_DEVICES = {
    "pico_calc": "slime.devices.pico_calc.PicoCalcDevice",
    "my_device": "slime.devices.my_device.MyDevice",  # Add this
}
```

### 3. Create Drivers

Implement `AbstractDisplay` and `AbstractInput` interfaces in:
- `slime/drivers/display/my_display.py`
- `slime/drivers/input/my_keyboard.py`

See existing drivers for examples.

## Exception Handling

Apps can crash without bringing down the OS:

```python
def run(self):
    x = 1 / 0  # This will crash the app
    yield
```

The OS will:
1. Catch the exception
2. Show a crash screen (3 seconds)
3. Return to launcher
4. Clean up resources

## Watchdog Timer

Enable in `config.py`:

```python
WATCHDOG_TIMEOUT = 10  # 10 seconds
```

If an app hangs (never yields), the hardware watchdog will reset the entire system after 10 seconds.

Disable during development:

```python
WATCHDOG_TIMEOUT = None
```

## Memory Management

The system automatically:
- Lazy loads drivers (only when needed)
- Garbage collects after each app exit
- Shows memory usage in launcher

Monitor memory in your app:

```python
mem = self.sys.memory_info()
print(f"Free: {mem['free']/1024:.1f}KB ({mem['percent_used']:.1f}% used)")
```

## Supported Devices

### Pico Calc
- **Hardware**: Raspberry Pi Pico, 320x320 ST7789 display, I2C keyboard
- **Device ID**: `pico_calc`
- **Status**: ✓ Fully supported

### Coming Soon
- Slime Deck
- Simulator (for desktop development)

## Troubleshooting

### App Not Appearing in Launcher

1. Check file is in `apps/` directory
2. Check filename ends in `.py`
3. Check class inherits from `App`
4. Check `name` and `id` attributes are set
5. Check for import errors in console

### Display Not Working

1. Check device configuration in `config.py`
2. Check pin definitions in device profile
3. Check SPI connections
4. Check display driver imports

### Keyboard Not Working

1. Check I2C connections
2. Check keyboard I2C address (default: 31)
3. Test with simple key press detection

### App Crashes Immediately

1. Check for syntax errors
2. Check imports (all imports must be available)
3. Check `run()` method is a generator (uses `yield`)
4. Check for exceptions in console

### System Hangs

1. Check app yields regularly
2. Enable watchdog in development to auto-recover
3. Check for infinite loops without `yield`

## Performance Tips

1. **Minimize redraws**: Only call `update()` when display changes
2. **Use framebuffer**: For partial screen updates (see display driver)
3. **Cache calculations**: Don't recalculate every frame
4. **Limit text**: Text rendering is relatively slow
5. **Profile code**: Use `time.ticks_ms()` to measure

## Future Enhancements

- Settings page in launcher
- App icons
- Categories/folders
- Search
- SD card support
- Expansion port support
- Network features
- More example apps

## License

See LICENSE file.

## Contributing

1. Follow existing code style
2. Document new features
3. Test on hardware before submitting
4. Add examples for new APIs

## Architecture

See `DESIGN.md` for detailed architecture documentation.

---

**Slime OS 2** - Clean, Simple, Extensible
