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
        """Get display height"""
        return self.device.display_height

    def clear(self, color=(0, 0, 0)):
        """
        Clear screen to color.

        Args:
            color: RGB tuple (r, g, b)
        """
        self.display.set_pen(*color)
        self.display.rectangle(0, 0, self.width, self.height)

    def draw_rect(self, x, y, w, h, color):
        """
        Draw filled rectangle.

        Args:
            x, y: Position
            w, h: Size
            color: RGB tuple (r, g, b)
        """
        self.display.set_pen(*color)
        self.display.rectangle(x, y, w, h)

    def draw_text(self, text, x, y, scale=1, color=(255, 255, 255)):
        """
        Draw text.

        Args:
            text: String to draw
            x, y: Position
            scale: Text scale (1, 2, 3, etc.)
            color: RGB tuple (r, g, b)
        """
        self.display.set_pen(*color)
        self.display.text(text, x, y, scale=scale)

    def draw_line(self, x1, y1, x2, y2, color):
        """
        Draw line.

        Args:
            x1, y1: Start position
            x2, y2: End position
            color: RGB tuple (r, g, b)
        """
        self.display.set_pen(*color)
        self.display.line(x1, y1, x2, y2)

    def draw_pixel(self, x, y, color):
        """
        Draw single pixel.

        Args:
            x, y: Position
            color: RGB tuple (r, g, b)
        """
        self.display.set_pen(*color)
        self.display.pixel(x, y)

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
        """Update display - flip buffer to screen"""
        self.display.update()

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

            # Clear keyboard state to prevent stale key presses
            if self._input:
                try:
                    self._input.clear_state()
                    # Small delay to ensure key release is processed
                    time.sleep(0.1)
                except AttributeError:
                    pass  # Hardware keyboards may not have clear_state

            try:
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
                                current_app_class = result[1]
                                self.log.info(f"Launching {current_app_class.name if hasattr(current_app_class, 'name') else 'App'}")
                                break
                        # Otherwise just exit normally
                        self.log.info("App exited normally")
                        current_app_class = initial_app_class
                        break

                    # Handle special return values from yield
                    if result and isinstance(result, tuple):
                        if result[0] == 'launch':
                            # App wants to launch another app
                            current_app_class = result[1]
                            self.log.info(f"Launching {current_app_class.name if hasattr(current_app_class, 'name') else 'App'}")
                            break  # Exit app loop, will launch new app

            except KeyboardInterrupt:
                # User interrupted (Ctrl+C)
                self.log.info("Interrupted by user")
                current_app_class = initial_app_class

            except Exception as e:
                # App crashed with unhandled exception
                self.log.error(f"App crashed: {type(e).__name__}: {e}")

                # Show crash screen
                self._show_crash_screen(
                    app_name=app.name if hasattr(app, 'name') else "Unknown App",
                    error=f"{type(e).__name__}: {str(e)}"
                )

                # Return to launcher
                current_app_class = initial_app_class

            finally:
                # Always cleanup
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
