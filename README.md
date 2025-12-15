# Slime OS 2

A lightweight operating system for embedded MicroPython devices.

This project started from [Slime OS](https://github.com/abeisgoat/slime_os) but has been re-written to be easier to extend and modify.

## Directory Structure

```
slime_os_2/
├── main.py              # Entry point
├── config.py            # Device configuration
├── deploy_to_pico.sh    # Hardware deployment script
│
├── apps/                # User applications
│   ├── launcher.py      # App launcher (home screen)
│   ├── flashlight.py    # Example app
│   └── log_viewer.py    # System log viewer
│
├── lib/                 # Libraries
│   └── keycode.py       # Keyboard key constants
│
├── slime/               # OS core
│   ├── system.py        # System kernel
│   ├── app.py           # App base class
│   ├── logger.py        # Logging system
│   ├── devices/         # Device profiles
│   └── drivers/         # Hardware drivers
│
└── dev/                 # Development files (NOT uploaded to hardware)
    ├── *.md             # Documentation
    ├── run_simulator.py # Desktop simulator
    ├── compat/          # Desktop compatibility shims
    └── slime/           # Simulator-specific drivers
```

## Quick Start

### Deploy to Hardware (Pico Calc)

1. Edit `config.py` to select your device:
   ```python
   DEVICE = "pico_calc"
   ```

2. Run the deployment script:
   ```bash
   ./deploy_to_pico.sh
   ```

3. Reset your Pico and the launcher will appear!

### Run Simulator (Desktop)

```bash
python3 dev/run_simulator.py
```

[screenshot of home page](screenshot.png)

Requires pygame: `pip3 install pygame`

## Adding Apps

Create a new file in `apps/` directory:

```python
from slime.app import App
from lib.keycode import Keycode

class MyApp(App):
    name = "My App"
    id = "my_app"
    
    def run(self):
        while True:
            self.sys.clear((0, 0, 0))
            self.sys.draw_text("Hello!", 10, 10)
            self.sys.update()
            
            if self.sys.key_pressed(Keycode.Q):
                return  # Exit to launcher
            
            yield  # Return control to OS
```

The launcher will automatically discover and display your app!

## Hardware Support

Currently supported:
- **Pico Calc**: Raspberry Pi Pico with 320x320 ST7789 display and I2C keyboard

## Documentation

See `dev/` directory for detailed documentation:
- `dev/DESIGN.md` - Architecture and design decisions
- `dev/DEPLOY_TO_HARDWARE.md` - Hardware deployment guide
- `dev/TESTING.md` - Testing procedures
