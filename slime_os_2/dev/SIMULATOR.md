# Slime OS 2 - Simulator Guide

## Overview

The Slime OS 2 Simulator allows you to run and test Slime OS applications on your desktop computer without hardware. This dramatically speeds up development by eliminating the upload/flash cycle.

## Features

- **Full OS Experience**: Runs complete Slime OS with launcher and apps
- **Accurate Display**: 320x320 pixel display (scaled 2x for visibility)
- **PC Keyboard Input**: Maps your keyboard to Slime OS keycodes
- **Hot Reload**: Optional auto-restart on file changes
- **Zero Hardware**: Develop without device connected
- **Same Code**: Apps run identically on hardware and simulator

## Quick Start

### 1. Install Requirements

```bash
cd slime_os_2
pip install -r requirements.txt
```

This installs:
- `pygame` (required)
- `watchdog` (optional, for hot-reload)

### 2. Run Simulator

```bash
python run_simulator.py
```

A 640x640 window will open showing the Slime OS launcher.

### 3. Use the Simulator

**Navigation:**
- Arrow keys: Navigate menus
- Enter: Select/activate
- Q: Quit apps (returns to launcher)
- Close window: Exit simulator

**Example:**
1. Window opens with launcher
2. Press Up/Down to select "Flashlight"
3. Press Enter to launch
4. Press Enter to toggle flashlight
5. Press Q to return to launcher

## Hot Reload

Enable hot-reload to automatically restart the simulator when you edit code:

```bash
python run_simulator.py --watch
```

Changes to any `.py` file will trigger a restart (with 1-second debounce).

**Great for:**
- Iterating on UI layouts
- Testing app logic
- Tweaking colors/text
- Bug fixes

## Keyboard Mapping

PC Keyboard → Slime OS Keycodes:

| PC Key | Slime OS Keycode |
|--------|------------------|
| A-Z | Keycode.A - Keycode.Z |
| 0-9 | Keycode.ZERO - Keycode.NINE |
| Enter | Keycode.ENTER |
| Space | Keycode.SPACE |
| Arrows | Keycode.UP_ARROW, etc. |
| Esc | Keycode.ESCAPE |
| Backspace | Keycode.BACKSPACE |
| Tab | Keycode.TAB |
| F1-F12 | Keycode.F1 - Keycode.F12 |

Full mapping in `slime/drivers/input/sim_keyboard.py`

## Display

**Native Resolution**: 320x320 pixels
**Window Size**: 640x640 pixels (2x scale for visibility)
**Color**: Full RGB (0-255 per channel)
**Fonts**: Pygame fonts (approximate hardware font)

### Customizing Display

Edit `slime/devices/simulator.py`:

```python
class SimulatorDevice(BaseDevice):
    # ...
    WINDOW_SCALE = 3  # 3x scale = 960x960 window
    WINDOW_TITLE = "My Custom Title"
```

## Differences from Hardware

### What Works Identically
- Display rendering (colors, shapes, text)
- Keyboard input
- App logic
- Launcher
- Exception handling
- Memory management (with fake values)

### What's Different
- **Font rendering**: Pygame font vs hardware bitmap font (slightly different appearance)
- **Performance**: Simulator runs at desktop speed (usually faster than hardware)
- **Memory**: Reports fake values (~200KB free) instead of actual Pico RAM
- **Watchdog**: Disabled (no-op) in simulator
- **Hardware peripherals**: SD card, expansion port, I2C/SPI not functional

### What's Not Supported Yet
- Expansion port communication
- SD card operations
- Hardware-specific features (ADC, PWM, etc.)

## Development Workflow

### Recommended Process

1. **Develop in simulator**:
   ```bash
   python run_simulator.py --watch
   ```

2. **Edit code**: Make changes in your editor

3. **Test immediately**: Simulator auto-restarts

4. **Iterate quickly**: No upload delays!

5. **Deploy to hardware**: When ready, upload and test on device

### Tips

**Rapid Prototyping:**
- Use simulator for UI layout
- Test color schemes
- Validate app logic
- Debug crashes safely

**Before Hardware Deploy:**
- Test all key combinations
- Verify text fits on screen
- Check edge cases
- Profile performance (if needed)

## Troubleshooting

### Simulator Won't Start

**Error: pygame not installed**
```bash
pip install pygame
```

**Error: Unknown device 'simulator'**
- Check `config.py`: `DEVICE = "simulator"`
- Check `slime/devices/__init__.py` has simulator registered

**Window opens then closes immediately**
- Check console for Python errors
- Verify all files are present
- Try running without timeout: `python run_simulator.py`

### Display Issues

**Window too small/large**
- Edit `slime/devices/simulator.py`
- Change `WINDOW_SCALE` (1-4)

**Font looks wrong**
- Expected: pygame fonts differ from hardware
- They approximate the 8x8 bitmap font

**Colors look different**
- Monitor vs LCD display
- Calibration varies

### Input Issues

**Keys not working**
- Click window to focus it
- Check key mapping in sim_keyboard.py
- Some keys may not be mapped yet

**Multiple key presses**
- Simulator handles simultaneous keys
- Works like hardware

### Hot Reload Issues

**Not restarting on changes**
```bash
pip install watchdog
```

**Restarting too often**
- 1-second debounce prevents rapid restarts
- Save all files before testing

**Can't stop it**
- Press Ctrl+C in terminal
- Close window

## Architecture

```
run_simulator.py
    ├─> Adds compat/ to sys.path
    ├─> Sets DEVICE = "simulator"
    └─> Boots System with Launcher

System
    ├─> Gets SimulatorDevice
    ├─> Creates SimDisplay (pygame window)
    ├─> Creates SimKeyboard (pygame events)
    └─> Runs apps normally

Apps
    └─> Use self.sys API (no changes needed!)
```

### Key Files

- `run_simulator.py` - Entry point, hot-reload
- `slime/devices/simulator.py` - Device profile
- `slime/drivers/display/sim_display.py` - Pygame display
- `slime/drivers/input/sim_keyboard.py` - Pygame keyboard
- `compat/` - Hardware module stubs

## Extending the Simulator

### Add New Keys

Edit `slime/drivers/input/sim_keyboard.py`:

```python
KEY_MAP = {
    # Add your key
    pygame.K_PAGEUP: Keycode.PAGE_UP,
    # ...
}
```

### Simulate Peripherals

Create new drivers:

```python
# slime/drivers/peripheral/sim_sdcard.py
class SimSDCard:
    def __init__(self):
        # Use actual filesystem
        self.root = '/tmp/slime_os_sd'
```

Register in SimulatorDevice:

```python
def create_sdcard(self):
    from slime.drivers.peripheral.sim_sdcard import SimSDCard
    return SimSDCard()
```

### Debug Mode

Add debug overlays in `sim_display.py`:

```python
def update(self):
    # ... normal rendering ...

    # Debug overlay
    if DEBUG_MODE:
        self.draw_fps()
        self.draw_memory()

    pygame.display.flip()
```

## Performance

### Simulator Performance
- **Display**: ~60 FPS (vsync limited)
- **Startup**: <1 second
- **Hot reload**: ~2 seconds

### Hardware Comparison
- Simulator usually faster (desktop CPU)
- Don't optimize for simulator performance
- Always test on hardware for real metrics

## FAQ

**Q: Do I need MicroPython installed?**
A: No! Simulator uses standard Python 3.

**Q: Can I run multiple simulators?**
A: Yes, just run the command multiple times.

**Q: Can I test on Mac/Windows?**
A: Yes! Pygame is cross-platform. Simulator works on Linux, Mac, and Windows.

**Q: Does simulator support touch input?**
A: Not yet (hardware doesn't have touch currently).

**Q: Can I record simulator output?**
A: Use screen recording software (OBS, etc.)

**Q: Can I unit test with simulator?**
A: Yes! Import apps and test methods directly.

**Q: How accurate is the simulator?**
A: Very accurate for display/input. Peripherals not implemented yet.

## Next Steps

1. **Try the examples**: Run flashlight app
2. **Make changes**: Edit colors, text, layout
3. **Create new app**: Follow app template
4. **Deploy to hardware**: When ready, test on device
5. **Report issues**: If simulator behaves differently from hardware

---

**Happy developing!** The simulator makes Slime OS development fast and fun. 🚀
