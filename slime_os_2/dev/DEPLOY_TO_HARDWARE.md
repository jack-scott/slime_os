# Deploying Slime OS 2 to Pico Calc Hardware

## Prerequisites

1. **MicroPython firmware** must be installed on your Pico
2. **mpremote** tool for uploading files

### Install mpremote

```bash
pip3 install mpremote
```

## Files to Upload

Upload ONLY these files/directories to your Pico:

```
✅ UPLOAD THESE:
├── main.py              # Entry point
├── config.py            # Device configuration
├── lib/                 # Keycode definitions
│   └── keycode.py
├── slime/               # Core OS
│   ├── __init__.py
│   ├── system.py
│   ├── app.py
│   ├── logger.py
│   ├── devices/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── pico_calc.py
│   └── drivers/
│       ├── __init__.py
│       ├── display/
│       │   ├── __init__.py
│       │   ├── abstract.py
│       │   └── pico_calc_display.py
│       └── input/
│           ├── __init__.py
│           ├── abstract.py
│           └── pico_calc_keyboard.py
└── apps/                # Applications
    ├── __init__.py
    ├── launcher.py
    ├── flashlight.py
    └── log_viewer.py

❌ DO NOT UPLOAD:
├── compat/              # Only for simulator
├── run_simulator.py     # Only for simulator
├── requirements.txt     # Only for simulator
├── slime/devices/simulator.py
├── slime/drivers/display/sim_display.py
└── slime/drivers/input/sim_keyboard.py
```

## Upload Methods

### Method 1: Using mpremote (Recommended)

```bash
# 1. Connect your Pico via USB

# 2. Verify connection
mpremote connect list

# 3. Upload files (run from slime_os_2 directory)
mpremote cp main.py :
mpremote cp config.py :
mpremote mkdir lib
mpremote cp lib/keycode.py :lib/
mpremote mkdir apps
mpremote cp apps/__init__.py :apps/
mpremote cp apps/launcher.py :apps/
mpremote cp apps/flashlight.py :apps/
mpremote cp apps/log_viewer.py :apps/
mpremote mkdir slime
mpremote cp -r slime/* :slime/

# 4. Run main.py
mpremote run main.py
```

### Method 2: Using a deployment script

I'll create a script to automate this:

```bash
./deploy_to_pico.sh
```

### Method 3: Using Thonny IDE

1. Open Thonny IDE
2. Select "MicroPython (Raspberry Pi Pico)" interpreter
3. Use File Manager to upload files manually
4. Keep the same directory structure

## After Upload

1. The Pico will run `main.py` automatically on boot
2. You should see the launcher with your apps
3. If something goes wrong, connect via serial to see error messages:

```bash
mpremote connect /dev/ttyACM0 repl
```

## Troubleshooting

### "No MicroPython device found"
- Check USB connection
- Try different USB cable
- Check device appears: `ls /dev/tty*` (look for ttyACM0 or ttyUSB0)

### "Import error" on device
- Make sure all files uploaded correctly
- Check directory structure matches exactly
- Verify config.py has DEVICE = "pico_calc"

### Display not working
- Check your hardware connections
- Verify Pico Calc device definition matches your hardware pins
- Check slime/devices/pico_calc.py pins match your setup

### Keyboard not working
- Check keyboard matrix pin definitions
- Verify keyboard is properly connected

## Testing Checklist

Once uploaded:
- [ ] Pico boots without errors
- [ ] Launcher screen appears
- [ ] Can navigate with arrow keys
- [ ] Can launch flashlight app
- [ ] Can launch log viewer
- [ ] Can return to launcher with Q

## Performance Notes

On actual hardware:
- Frame rate is controlled by 30 FPS limit
- Memory usage shown in launcher should be accurate
- Logging is silent (no stdout) but stored in memory
- Use Log Viewer app to see system logs
