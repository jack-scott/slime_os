# Keyboard Input Fix

## Issue
Keyboard input wasn't working in the simulator.

## Root Cause
Both `sim_display.py` and `sim_keyboard.py` were calling `pygame.event.get()`, which removes events from the queue. The display's `update()` method was consuming all events (including keyboard events) before the keyboard driver could see them.

## Solution
Removed event processing from `sim_display.py`'s `update()` method. Now only `sim_keyboard.py` calls `pygame.event.get()`, ensuring keyboard events are properly captured.

## Changes Made

**File: `slime/drivers/display/sim_display.py`**

**Before:**
```python
def update(self):
    # ... flip display ...

    # Process pygame events to keep window responsive
    for event in pygame.event.get():  # ❌ Consuming events!
        if event.type == pygame.QUIT:
            raise SystemExit("Window closed")
```

**After:**
```python
def update(self):
    # ... flip display ...

    # Note: Events are processed by SimKeyboard driver to avoid consuming them here
    # ✅ No longer consuming events
```

**File: `slime/drivers/input/sim_keyboard.py`** (unchanged)
```python
def _update_state(self):
    # Process all pending events
    for event in pygame.event.get():  # ✅ Only place events are consumed
        if event.type == pygame.KEYDOWN:
            # Handle key press
        elif event.type == pygame.KEYUP:
            # Handle key release
        elif event.type == pygame.QUIT:
            # Handle window close
            raise SystemExit("Window closed")
```

## Event Flow (Fixed)

```
User presses key
    ↓
pygame event queue: [KEYDOWN event]
    ↓
App calls sys.update()
    ↓
display.update() called → Just flips display (no event processing)
    ↓
pygame event queue: [KEYDOWN event] (still there!)
    ↓
App calls sys.key_pressed(Keycode.A)
    ↓
keyboard._update_state() called
    ↓
pygame.event.get() retrieves KEYDOWN event ✅
    ↓
Key detected!
```

## Testing

**Quick test:**
```bash
python run_simulator.py
```

1. Window opens with launcher
2. Press UP/DOWN arrows → Selection should change
3. Press ENTER → App launches
4. Press keys in app → Should respond

**Detailed test:**
```bash
python test_keyboard.py
```

Press keys and watch console output.

## Why This Works

**pygame.event.get()** removes events from the queue. If multiple parts of code call it:
- First call: Gets all events ✅
- Second call: Gets nothing (queue is empty) ❌

**Solution:** Only call it once per frame, in one place (keyboard driver).

## Alternative Approaches Considered

1. **Shared event queue:** Store events in a list, share between drivers
   - More complex
   - Not necessary for our use case

2. **pygame.event.peek():** Look at events without removing
   - Not as reliable
   - Still have to remove them eventually

3. **Centralized event manager:** Single class handles all events
   - Over-engineered for this simple case
   - Current solution is cleaner

## Verification

After fix:
- ✅ Keyboard input works
- ✅ Window close still works (handled by keyboard driver)
- ✅ No duplicate event processing
- ✅ Simple, clean code

## Status

**FIXED** ✅

Keyboard input now works correctly in simulator.
