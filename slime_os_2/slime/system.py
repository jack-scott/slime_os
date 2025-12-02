"""
Slime OS 2 - System Core

The System class is the OS kernel that manages:
- Device initialization
- App lifecycle
- Graphics/input APIs
- Exception handling
- Watchdog timer
"""

import time
import gc as _gc_module
from slime.logger import Logger

# Create gc wrapper that works for both MicroPython and Python
class GC:
    """GC wrapper for MicroPython/Python compatibility"""

    def collect(self):
        return _gc_module.collect()

    def mem_free(self):
        # MicroPython has this, standard Python doesn't
        if hasattr(_gc_module, 'mem_free'):
            return _gc_module.mem_free()
        else:
            # Simulator: return fake value
            return 200_000  # ~200KB free

    def mem_alloc(self):
        # MicroPython has this, standard Python doesn't
        if hasattr(_gc_module, 'mem_alloc'):
            return _gc_module.mem_alloc()
        else:
            # Simulator: return fake value
            return 64_000  # ~64KB allocated

gc = GC()


class System:
    """
    System class - the OS kernel

    This is the main interface that apps use to interact with hardware
    and system services.
    """

    # Toolbar configuration
    TOOLBAR_HEIGHT = 16
    TOOLBAR_ENABLED = True

    def __init__(self, device, watchdog_timeout=None):
        """
        Initialize the system.

        Args:
            device: Device instance (from devices/)
            watchdog_timeout: Optional watchdog timeout in seconds (None to disable)
        """
        self.device = device

        # Lazy-loaded drivers
        self._display = None
        self._input = None

        # Toolbar state
        self._toolbar_frame = 0
        self._toolbar_update_interval = 30  # Update toolbar every 30 frames (~1 second at 30fps)
        self._last_mem_free = 0  # Will be initialized on first update

        # Logger (print to stdout for simulator)
        print_logs = (device.name == "Simulator")
        self.log = Logger(max_messages=200, print_to_stdout=print_logs)
        self.log.info(f"System initializing on {device.name}")

        # Watchdog setup
        self.wdt = None
        if watchdog_timeout:
            try:
                from machine import WDT
                self.wdt = WDT(timeout=int(watchdog_timeout * 1000))  # Convert to ms
                self.log.info(f"Watchdog enabled: {watchdog_timeout}s timeout")
            except ImportError:
                self.log.warn("Watchdog not available on this platform")

    # ========================================================================
    # Display API
    # ========================================================================

    @property
    def display(self):
        """Get display driver (lazy loaded)"""
        if self._display is None:
            self._display = self.device.create_display()
            print(f"[OS] Display initialized: {self.device.display_width}x{self.device.display_height}")
        return self._display

    @property
    def width(self):
        """Get display width"""
        return self.device.display_width

    @property
    def height(self):
        """Get display height (excluding toolbar if enabled)"""
        if self.TOOLBAR_ENABLED:
            return self.device.display_height - self.TOOLBAR_HEIGHT
        return self.device.display_height

    def clear(self, color=(0, 0, 0)):
        """
        Clear screen to color (app area only, not toolbar).

        Args:
            color: RGB tuple (r, g, b)
        """
        self.display.set_pen(*color)
        y_offset = self.TOOLBAR_HEIGHT if self.TOOLBAR_ENABLED else 0
        self.display.rectangle(0, y_offset, self.width, self.height)

    def draw_rect(self, x, y, w, h, color):
        """
        Draw filled rectangle.

        Args:
            x, y: Position (relative to app area)
            w, h: Size
            color: RGB tuple (r, g, b)
        """
        y_offset = self.TOOLBAR_HEIGHT if self.TOOLBAR_ENABLED else 0
        self.display.set_pen(*color)
        self.display.rectangle(x, y + y_offset, w, h)

    def draw_text(self, text, x, y, scale=1, color=(255, 255, 255)):
        """
        Draw text.

        Args:
            text: String to draw
            x, y: Position (relative to app area)
            scale: Text scale (1, 2, 3, etc.)
            color: RGB tuple (r, g, b)
        """
        y_offset = self.TOOLBAR_HEIGHT if self.TOOLBAR_ENABLED else 0
        self.display.set_pen(*color)
        self.display.text(text, x, y + y_offset, scale=scale)

    def draw_line(self, x1, y1, x2, y2, color):
        """
        Draw line.

        Args:
            x1, y1: Start position (relative to app area)
            x2, y2: End position (relative to app area)
            color: RGB tuple (r, g, b)
        """
        y_offset = self.TOOLBAR_HEIGHT if self.TOOLBAR_ENABLED else 0
        self.display.set_pen(*color)
        self.display.line(x1, y1 + y_offset, x2, y2 + y_offset)

    def draw_pixel(self, x, y, color):
        """
        Draw single pixel.

        Args:
            x, y: Position (relative to app area)
            color: RGB tuple (r, g, b)
        """
        y_offset = self.TOOLBAR_HEIGHT if self.TOOLBAR_ENABLED else 0
        self.display.set_pen(*color)
        self.display.pixel(x, y + y_offset)

    def measure_text(self, text, scale=1):
        """
        Measure text dimensions.

        Args:
            text: String to measure
            scale: Text scale

        Returns:
            Tuple (width, height)
        """
        return self.display.measure_text(text, scale)

    def update(self):
        """Update display - flip buffer to screen and draw toolbar"""
        # Update toolbar data periodically (not every frame)
        self._toolbar_frame += 1
        if self._toolbar_frame >= self._toolbar_update_interval:
            self._update_toolbar_data()
            self._toolbar_frame = 0

        # Always draw toolbar (uses cached data)
        self._draw_toolbar()

        # Flip display buffer to screen
        self.display.update()

    def reset_display(self):
        """
        Reset display to clean state.

        This clears:
        - The display itself (to black)
        - Framebuffers
        - Text/drawing queues
        - Any cached display state

        Called automatically during app transitions.
        Apps can also call this manually if needed.

        Note: The toolbar area is also cleared and will be redrawn on next update().
        """
        self.display.reset()

        # Clear toolbar area explicitly
        if self.TOOLBAR_ENABLED:
            self.display.set_pen(0, 0, 0)
            self.display.rectangle(0, 0, self.device.display_width, self.TOOLBAR_HEIGHT)

    # ========================================================================
    # Input API
    # ========================================================================

    @property
    def input(self):
        """Get input driver (lazy loaded)"""
        if self._input is None:
            self._input = self.device.create_input()
            print("[OS] Input initialized")
        return self._input

    def key_pressed(self, keycode):
        """
        Check if a key is currently pressed.

        Args:
            keycode: Keycode constant (from lib.keycode)

        Returns:
            True if pressed, False otherwise
        """
        return self.input.get_key(keycode)

    def keys_pressed(self, keycodes):
        """
        Check multiple keys at once.

        Args:
            keycodes: List of keycode constants

        Returns:
            Dict mapping each keycode to True/False
        """
        return self.input.get_keys(keycodes)

    # ========================================================================
    # System Utilities
    # ========================================================================

    def memory_info(self):
        """
        Get memory usage information.

        Returns:
            Dict with keys: 'free', 'allocated', 'total', 'percent_used'
        """
        gc.collect()
        free = gc.mem_free()
        allocated = gc.mem_alloc()
        total = free + allocated
        percent_used = (allocated / total * 100) if total > 0 else 0

        return {
            'free': free,
            'allocated': allocated,
            'total': total,
            'percent_used': percent_used
        }

    def print_memory(self, label=""):
        """Print memory info with a label (for debugging)"""
        mem = self.memory_info()
        print(f"[MEM {label}] Free: {mem['free']:,} | Allocated: {mem['allocated']:,} | {mem['percent_used']:.1f}% used")

    # ========================================================================
    # Toolbar
    # ========================================================================

    def _draw_toolbar(self):
        """
        Draw the system toolbar at the top of the screen.

        Shows: SLIME OS | RAM usage
        """
        if not self.TOOLBAR_ENABLED:
            return

        # Draw toolbar background (dark gray)
        self.display.set_pen(32, 32, 32)
        self.display.rectangle(0, 0, self.device.display_width, self.TOOLBAR_HEIGHT)

        # Draw "SLIME OS" on the left
        self.display.set_pen(255, 255, 0)  # Yellow
        self.display.text("SLIME OS", 2, 2, scale=1)

        # Draw RAM usage on the right
        # Update data if not initialized yet
        if self._last_mem_free == 0:
            self._update_toolbar_data()

        mem_kb = self._last_mem_free // 1024
        mem_text = f"{mem_kb}KB"
        text_width = self.display.measure_text(mem_text, scale=1)

        # Position from the right edge
        x_pos = self.device.display_width - text_width - 2

        self.display.set_pen(0, 255, 0)  # Green
        self.display.text(mem_text, x_pos, 2, scale=1)

    def _update_toolbar_data(self):
        """Update toolbar data (called periodically, not every frame)"""
        mem = self.memory_info()
        self._last_mem_free = mem['free']

    # ========================================================================
    # App Lifecycle Management
    # ========================================================================

    def boot(self, initial_app_class):
        """
        Boot the OS with an initial app.

        This is the main event loop. It:
        1. Creates app instance
        2. Runs app generator
        3. Handles app results and exceptions
        4. Manages app switching
        5. Cleans up resources

        Args:
            initial_app_class: App class to boot with (typically Launcher)
        """
        current_app_class = initial_app_class

        self.log.info(f"Booting {self.device.name}")
        self.log.info(f"Starting {current_app_class.name if hasattr(current_app_class, 'name') else 'App'}")

        # Frame rate limiting (simulate hardware speed)
        # Pico 2040 runs at ~133-200 MHz, much slower than desktop
        # Target ~30 FPS to approximate hardware responsiveness
        target_fps = 30
        frame_time = 1.0 / target_fps
        last_frame_time = time.time()

        while True:
            # Create app instance
            app = current_app_class(self)
            app_generator = None
            exit_reason = 'normal'

            # Clear keyboard state to prevent stale key presses
            if self._input:
                try:
                    self._input.clear_state()
                    # Small delay to ensure key release is processed
                    time.sleep(0.1)
                except AttributeError:
                    pass  # Hardware keyboards may not have clear_state

            try:
                # Call on_enter hook
                self.log.debug(f"Calling on_enter for {app.name if hasattr(app, 'name') else 'app'}")
                try:
                    app.on_enter()
                except Exception as e:
                    self.log.error(f"Error in on_enter: {e}")
                    # Continue anyway - don't crash just because on_enter failed

                # Start app generator
                self.log.debug(f"Creating generator for {app.name if hasattr(app, 'name') else 'app'}")
                app_generator = app.run()
                self.log.debug("Generator created, entering event loop")

                # Run app event loop
                while True:
                    # Frame rate limiting
                    current_time = time.time()
                    elapsed = current_time - last_frame_time
                    if elapsed < frame_time:
                        time.sleep(frame_time - elapsed)
                    last_frame_time = time.time()

                    # Feed watchdog if enabled
                    if self.wdt:
                        self.wdt.feed()

                    # Get next result from app
                    try:
                        result = next(app_generator)
                    except StopIteration as e:
                        # Generator returned - check if it returned a value
                        if hasattr(e, 'value') and e.value:
                            result = e.value
                            # Check if it's a launch command
                            if isinstance(result, tuple) and result[0] == 'launch':
                                exit_reason = 'launch'
                                current_app_class = result[1]
                                self.log.info(f"Launching {current_app_class.name if hasattr(current_app_class, 'name') else 'App'}")
                                break
                        # Otherwise just exit normally
                        exit_reason = 'normal'
                        self.log.info("App exited normally")
                        current_app_class = initial_app_class
                        break

                    # Handle special return values from yield
                    if result and isinstance(result, tuple):
                        if result[0] == 'launch':
                            # App wants to launch another app
                            exit_reason = 'launch'
                            current_app_class = result[1]
                            self.log.info(f"Launching {current_app_class.name if hasattr(current_app_class, 'name') else 'App'}")
                            break  # Exit app loop, will launch new app

                # Call on_exit hook (only if normal exit, not crash)
                self.log.debug(f"Calling on_exit({exit_reason})")
                try:
                    app.on_exit(reason=exit_reason)
                except Exception as e:
                    self.log.error(f"Error in on_exit: {e}")

            except KeyboardInterrupt:
                # User interrupted (Ctrl+C)
                self.log.info("Interrupted by user")
                exit_reason = 'interrupt'
                current_app_class = initial_app_class

                # Call on_exit for interrupt
                try:
                    app.on_exit(reason=exit_reason)
                except Exception as e:
                    self.log.error(f"Error in on_exit: {e}")

            except Exception as e:
                # App crashed with unhandled exception
                self.log.error(f"App crashed: {type(e).__name__}: {e}")

                # Show crash screen
                self._show_crash_screen(
                    app_name=app.name if hasattr(app, 'name') else "Unknown App",
                    error=f"{type(e).__name__}: {str(e)}"
                )

                # Return to launcher
                exit_reason = 'crash'
                current_app_class = initial_app_class
                # Note: on_exit NOT called on crash, only on_cleanup

            finally:
                # Call on_cleanup hook (ALWAYS called, even on crash)
                self.log.debug("Calling on_cleanup")
                try:
                    app.on_cleanup()
                except Exception as e:
                    self.log.error(f"Error in on_cleanup: {e}")
                    # Continue anyway - don't crash during cleanup

                # Always cleanup resources
                if app_generator:
                    try:
                        app_generator.close()
                    except:
                        pass

                del app
                del app_generator
                gc.collect()

                mem = self.memory_info()
                self.log.debug(f"Memory: {mem['free']/1024:.1f}KB free, {mem['percent_used']:.1f}% used")

    def _show_crash_screen(self, app_name, error):
        """
        Show a crash screen briefly.

        Args:
            app_name: Name of crashed app
            error: Error message
        """
        try:
            self.reset_display()
            self.clear((128, 0, 0))  # Dark red
            self.draw_text("APP CRASHED", 10, 10, scale=2, color=(255, 255, 255))
            self.draw_text(f"App: {app_name}", 10, 40, scale=1, color=(255, 255, 255))
            self.draw_text("Error:", 10, 60, scale=1, color=(255, 255, 255))

            # Word wrap error message
            error_lines = self._word_wrap(error, 38)  # ~38 chars per line at scale 1
            y = 80
            for line in error_lines[:5]:  # Max 5 lines
                self.draw_text(line, 10, y, scale=1, color=(255, 200, 200))
                y += 12

            self.draw_text("Returning to launcher...", 10, self.height - 30, scale=1, color=(255, 255, 0))
            self.update()

            time.sleep(3)  # Show for 3 seconds
        except Exception as e:
            # If we can't even show crash screen, just print and continue
            print(f"[OS] Failed to show crash screen: {e}")
            time.sleep(1)

    def _word_wrap(self, text, width):
        """
        Simple word wrap.

        Args:
            text: String to wrap
            width: Maximum characters per line

        Returns:
            List of lines
        """
        if len(text) <= width:
            return [text]

        lines = []
        while text:
            if len(text) <= width:
                lines.append(text)
                break

            # Find last space before width
            split_pos = text.rfind(' ', 0, width)
            if split_pos == -1:
                # No space found, hard break
                split_pos = width

            lines.append(text[:split_pos])
            text = text[split_pos:].lstrip()

        return lines
