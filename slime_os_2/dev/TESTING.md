# Testing Slime OS 2

## Testing the Simulator

### Quick Test
```bash
python run_simulator.py
```

**Expected behavior:**
1. Window opens (640x640)
2. Launcher appears with blue background
3. Shows "SLIME OS" at top
4. Shows "Flashlight" in list
5. Flashlight should be highlighted in yellow

### Keyboard Input Test

**In the launcher:**
1. **Press DOWN arrow** → Selection should move (if more apps)
2. **Press UP arrow** → Selection should move back
3. **Press ENTER** → Flashlight app should launch

**In flashlight app:**
1. App should show "FLASHLIGHT ON" with white screen
2. **Press ENTER** → Should toggle to "FLASHLIGHT OFF" with black screen
3. **Press ENTER again** → Should toggle back to ON
4. **Press Q** → Should return to launcher

### If Keyboard Not Working

**Symptoms:**
- Can't navigate in launcher
- Keys don't respond
- Arrow keys do nothing

**Debug steps:**

1. **Check window has focus:**
   - Click on the simulator window
   - Make sure it's the active window

2. **Test keyboard directly:**
   ```bash
   python test_keyboard.py
   ```
   - Press keys and watch console
   - Should print "Pressed: [...]"
   - Press ESC to exit

3. **Check for errors:**
   - Look at terminal output
   - Any pygame errors?
   - Any import errors?

4. **Verify pygame:**
   ```bash
   python -c "import pygame; print(pygame.version.ver)"
   ```
   Should print version (e.g., "2.6.1")

5. **Check event handling:**
   The fix ensures only the keyboard driver calls `pygame.event.get()`:
   - `sim_display.py` update() → Just flips display
   - `sim_keyboard.py` _update_state() → Processes ALL events

### Common Issues

**Issue: Keys not detected**
- Solution: Click window to focus it

**Issue: Window closes immediately**
- Solution: Check for Python errors in terminal

**Issue: Can't see cursor**
- Normal: Cursor is system cursor, not drawn by app

**Issue: Multiple key presses**
- Normal: Keyboard supports simultaneous keys

### Manual Testing Checklist

**Launcher:**
- [ ] Window opens
- [ ] Blue background shows
- [ ] Title "SLIME OS" visible
- [ ] Device name shows
- [ ] Memory info shows
- [ ] App list shows
- [ ] Arrow keys navigate
- [ ] Selection highlights in yellow
- [ ] Enter launches app

**Flashlight App:**
- [ ] App launches
- [ ] White screen shows (ON state)
- [ ] Text readable
- [ ] Enter toggles state
- [ ] Black screen shows (OFF state)
- [ ] Controls text visible
- [ ] Q returns to launcher

**Exception Handling:**
- [ ] Edit app to add crash: `x = 1/0`
- [ ] App should show crash screen
- [ ] Error message displayed
- [ ] Returns to launcher after 3s

**Hot Reload (if enabled):**
- [ ] Run with `--watch` flag
- [ ] Edit apps/flashlight.py
- [ ] Change a color value
- [ ] Save file
- [ ] Simulator restarts (~2s)
- [ ] New colors show

### Performance Checks

**FPS:**
- Should feel smooth (~60 FPS)
- No visible lag or stuttering

**Memory:**
- Launcher shows memory info
- Should show ~195KB free

**Startup:**
- Simulator starts in < 1 second
- Window appears quickly
- Launcher renders immediately

### Integration Test

Create a simple test app:

```python
# apps/test_keys.py
from slime.app import App
from lib.keycode import Keycode

class TestKeysApp(App):
    name = "Key Test"
    id = "test_keys"

    def run(self):
        while True:
            self.sys.clear((0, 0, 0))
            self.sys.draw_text("Press keys:", 10, 10, scale=2)

            keys = self.sys.keys_pressed([
                Keycode.A, Keycode.B, Keycode.C,
                Keycode.UP_ARROW, Keycode.DOWN_ARROW,
                Keycode.Q
            ])

            y = 50
            for keycode, pressed in keys.items():
                if pressed:
                    self.sys.draw_text(f"Key {hex(keycode)} pressed", 10, y)
                    y += 15

            if keys[Keycode.Q]:
                return

            self.sys.update()
            yield
```

Run simulator and test:
1. Launch "Key Test" app
2. Press A, B, C → Should see on screen
3. Press arrows → Should see codes
4. Press Q → Should exit

### Troubleshooting Commands

```bash
# Check Python version (need 3.7+)
python3 --version

# Check pygame
python3 -c "import pygame; pygame.init(); print('OK')"

# Run with debug output
python3 run_simulator.py 2>&1 | tee sim.log

# Test just keyboard
python3 test_keyboard.py

# Run specific app
# (Edit config.py DEVICE="simulator", then edit main.py to boot specific app)
```

### Known Limitations

**Simulator vs Hardware:**
- Font rendering slightly different
- Colors may appear different (monitor vs LCD)
- Performance much faster than hardware
- Memory values are fake

**Not Yet Implemented:**
- SD card access
- Expansion port
- Hardware peripherals

### Reporting Issues

If keyboard still doesn't work:

1. Note pygame version: `python3 -c "import pygame; print(pygame.version.ver)"`
2. Note Python version: `python3 --version`
3. Note OS: `uname -a` (Linux)
4. Save output: `python3 run_simulator.py 2>&1 > sim.log`
5. Test keyboard directly: `python3 test_keyboard.py`
6. Report what happens

### Success Criteria

✅ Window opens
✅ Launcher renders
✅ Arrow keys navigate
✅ Enter launches apps
✅ Apps run correctly
✅ Q returns to launcher
✅ No crashes or errors

---

**If all checks pass:** Simulator is working correctly! 🎉

**If issues persist:** Check TESTING.md for troubleshooting steps.
