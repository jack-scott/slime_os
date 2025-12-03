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
        self._last_fps = 0
        self._fps_frame_times = []  # Track last N frame times for FPS calculation
        self._toolbar_update_count = 0  # Counter for toolbar updates
        self._last_cpu_freq = 0  # CPU frequency in MHz
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

    def update(self, full_update=True):
        """
        Update display - flip buffer to screen and draw toolbar.

        Called by apps after drawing each frame.
        """
        if full_update:
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

        Shows: CPU MHz | FPS | RAM usage #counter
        """
        if not self.TOOLBAR_ENABLED:
            return

        # Draw toolbar background (dark gray)
        self.display.set_pen(32, 32, 32)
        self.display.rectangle(0, 0, self.device.display_width, self.TOOLBAR_HEIGHT)
        self.display.set_pen(255, 255, 0)  # Yellow
        self.display.text("SLIME OS", 2, 2, scale=1)

        # Update data if not initialized yet
        if self._last_mem_free == 0:
            self._update_toolbar_data()

        #Cpu freq
        cpu_text = f"{self._last_cpu_freq}MHz"
        self.display.set_pen(255, 255, 0)  # Yellow

        # Draw RAM usage and update counter on the right
        mem_kb = self._last_mem_free // 1024
        update_counter = self._toolbar_update_count
        stats_text = f"{cpu_text} | {mem_kb}KB | #{update_counter}"
        stats_text_width = self.display.measure_text(stats_text, scale=1)
        # Position from the right edge
        stats_x_pos = self.device.display_width - stats_text_width - 2
        self.display.set_pen(0, 255, 0)  # Green
        self.display.text(stats_text, stats_x_pos, 2, scale=1)

        # Draw FPS from the right
        fps_text = f"{self._last_fps}FPS |"
        fps_width = self.display.measure_text(fps_text, scale=1)
        fps_x = stats_x_pos - fps_width - 1
        # Color FPS based on performance
        if self._last_fps >= 28:
            fps_color = (0, 255, 0)  # Green - good
        elif self._last_fps >= 20:
            fps_color = (255, 255, 0)  # Yellow - ok
        else:
            fps_color = (255, 0, 0)  # Red - slow

        self.display.set_pen(*fps_color)
        self.display.text(fps_text, fps_x, 2, scale=1)

    def _update_toolbar_data(self):
        """Update toolbar data (called periodically, not every frame)"""
        # Increment update counter
        self._toolbar_update_count += 1

        # Update memory info
        mem = self.memory_info()
        self._last_mem_free = mem['free']

        # Update CPU frequency
        try:
            import machine
            freq_hz = machine.freq()
            self._last_cpu_freq = freq_hz // 1_000_000  # Convert to MHz
        except:
            self._last_cpu_freq = 0  # Not available

        # Calculate FPS from recent frame times
        if len(self._fps_frame_times) >= 2:
            # Average time between frames over last N frames
            total_time = self._fps_frame_times[-1] - self._fps_frame_times[0]
            num_frames = len(self._fps_frame_times) - 1
            if total_time > 0:
                avg_fps = num_frames / total_time
                self._last_fps = int(avg_fps)
            else:
                self._last_fps = 0
        else:
            self._last_fps = 0

    def update_toolbar(self):
        """
        Update only the toolbar region of the display.

        This is more efficient than a full screen update since it only
        redraws and updates the toolbar area.

        Call this when you want to refresh the toolbar without updating
        the rest of the screen.
        """
        if not self.TOOLBAR_ENABLED:
            return

        # Redraw toolbar
        self._draw_toolbar()

        # Update only the toolbar region
        self.display.update_partial(0, 0, self.device.display_width, self.TOOLBAR_HEIGHT)

    # ========================================================================
    # App Lifecycle Management
    # ========================================================================

    def _run_system_tasks(self):
        """
        Run system maintenance tasks.

        Called every frame after the app yields. This is where the OS does its work:
        - Track FPS
        - Update toolbar data (periodically)
        - Future: Check for system events, update status indicators, etc.

        This runs independently of the app - even if the app doesn't call update().
        """
        # Track frame times for FPS calculation
        current_time = time.time()
        self._fps_frame_times.append(current_time)

        # Keep only last 30 frame times (~1 second at 30 FPS)
        if len(self._fps_frame_times) > 60:
            self._fps_frame_times.pop(0)

        # Update toolbar data periodically (not every frame)
        self._toolbar_frame += 1
        if self._toolbar_frame >= self._toolbar_update_interval:
            self._update_toolbar_data()
            self._draw_toolbar()
            self._toolbar_frame = 0
        self.update_toolbar()

    def _prepare_app_for_launch(self):
        """
        Prepare system for launching a new app.

        Clears keyboard state to prevent stale key presses from previous app.
        """
        if self._input:
            try:
                self._input.clear_state()
                time.sleep(0.05)  # Small delay to ensure key release is processed
            except AttributeError:
                pass  # Hardware keyboards may not have clear_state

    def _run_app_frame(self, app_generator, frame_state):
        """
        Run a single frame of the app.

        This is the core of the event loop:
        1. Cap frame rate (max 30 FPS) - only sleep if running too fast
        2. Feed watchdog
        3. Call app generator (app runs one iteration and yields back)
        4. Run system tasks (toolbar updates, etc.)

        Args:
            app_generator: The app's generator (from app.run())
            frame_state: Dict with 'last_frame_time' key

        Returns:
            Tuple of (continue_running, exit_reason, next_app_class)
            - continue_running: True if app should keep running, False to exit
            - exit_reason: 'normal', 'launch', etc. (only valid if continue_running=False)
            - next_app_class: Class to launch next (only valid if exit_reason='launch')
        """
        # 1. FRAME RATE LIMITING - Cap at max 30 FPS, but don't force it
        #    This allows slow hardware to run at natural speed
        #    Only sleep if we're running faster than target
        target_fps = 30
        min_frame_time = 1.0 / target_fps  # 33ms minimum between frames

        current_time = time.time()
        elapsed = current_time - frame_state['last_frame_time']

        # Only sleep if we finished early (running too fast)
        if elapsed < min_frame_time:
            sleep_time = min_frame_time - elapsed
            # Only sleep if significant time remains (avoid tiny sleeps)
            if sleep_time > 0.001:  # 1ms threshold
                time.sleep(sleep_time)

        frame_state['last_frame_time'] = time.time()

        # 2. FEED WATCHDOG - Prevent hardware reset
        if self.wdt:
            self.wdt.feed()

        # 3. RUN APP - Call generator, app executes until next yield
        #    The app does its work (update state, draw UI, check input)
        #    then yields control back to us
        try:
            result = next(app_generator)
        except StopIteration as e:
            # App's run() function returned - app wants to exit
            if hasattr(e, 'value') and e.value:
                result = e.value
                # Check if app wants to launch another app
                if isinstance(result, tuple) and result[0] == 'launch':
                    return (False, 'launch', result[1])
            # Normal exit - return to launcher
            return (False, 'normal', None)

        # 4. RUN SYSTEM TASKS - OS does maintenance work
        #    Updates toolbar data, checks system state, etc.
        #    This happens every frame, independent of the app
        self._run_system_tasks()

        # 5. HANDLE APP RESULT - Check if app yielded a command
        if result and isinstance(result, tuple):
            if result[0] == 'launch':
                # App yielded a launch command
                return (False, 'launch', result[1])

        # App yielded normally - continue running
        return (True, None, None)

    def _cleanup_app(self, app, app_generator):
        """
        Clean up app resources.

        Called in finally block - ALWAYS runs even if app crashes.

        Args:
            app: App instance
            app_generator: App generator
        """
        # Close generator
        if app_generator:
            try:
                app_generator.close()
            except:
                pass

        # Delete references and free memory
        del app
        del app_generator
        gc.collect()

        # Log memory status
        mem = self.memory_info()
        self.log.debug(f"Memory: {mem['free']/1024:.1f}KB free, {mem['percent_used']:.1f}% used")

    def boot(self, initial_app_class):
        """
        Boot the OS with an initial app.

        Main OS loop that manages app lifecycle:
        1. Launches apps
        2. Runs event loop (app yields back to OS each frame)
        3. Handles app switching and crashes
        4. Cleans up resources

        Args:
            initial_app_class: App class to boot with (typically Launcher)
        """
        current_app_class = initial_app_class

        self.log.info(f"Booting {self.device.name}")
        self.log.info(f"Starting {current_app_class.name if hasattr(current_app_class, 'name') else 'App'}")

        # Frame state for rate limiting
        frame_state = {'last_frame_time': time.time()}

        # Main OS loop - keeps running, switching between apps
        while True:
            # 1. CREATE APP INSTANCE
            app = current_app_class(self)
            app_generator = None
            exit_reason = 'normal'

            # 2. PREPARE FOR LAUNCH
            self._prepare_app_for_launch()

            try:
                # 3. CALL APP LIFECYCLE HOOKS
                # on_enter: App can initialize, show loading screen, etc.
                self.log.debug(f"Calling on_enter for {app.name if hasattr(app, 'name') else 'app'}")
                try:
                    app.on_enter()
                except Exception as e:
                    self.log.error(f"Error in on_enter: {e}")

                # 4. START APP GENERATOR
                # This calls app.run() which returns a generator
                self.log.debug(f"Creating generator for {app.name if hasattr(app, 'name') else 'app'}")
                app_generator = app.run()
                self.log.debug("Generator created, entering event loop")

                # 5. RUN EVENT LOOP
                # Each iteration:
                #   - OS calls next() on generator
                #   - App runs until it yields (one frame of work)
                #   - Control returns to OS
                #   - OS updates toolbar and handles frame timing
                while True:
                    # Run one frame of the app
                    continue_running, exit_reason, next_app = self._run_app_frame(app_generator, frame_state)

                    if not continue_running:
                        # App wants to exit
                        if exit_reason == 'launch':
                            current_app_class = next_app
                            self.log.info(f"Launching {current_app_class.name if hasattr(current_app_class, 'name') else 'App'}")
                        else:
                            # Normal exit - return to launcher
                            current_app_class = initial_app_class
                            self.log.info("App exited normally")
                        break

                # 6. CALL on_exit HOOK (only for normal exits, not crashes)
                self.log.debug(f"Calling on_exit({exit_reason})")
                try:
                    app.on_exit(reason=exit_reason)
                except Exception as e:
                    self.log.error(f"Error in on_exit: {e}")

            except KeyboardInterrupt:
                # User pressed Ctrl+C
                self.log.info("Interrupted by user")
                exit_reason = 'interrupt'
                current_app_class = initial_app_class

                try:
                    app.on_exit(reason=exit_reason)
                except Exception as e:
                    self.log.error(f"Error in on_exit: {e}")

            except Exception as e:
                # App crashed - show error screen
                self.log.error(f"App crashed: {type(e).__name__}: {e}")

                self._show_crash_screen(
                    app_name=app.name if hasattr(app, 'name') else "Unknown App",
                    error=f"{type(e).__name__}: {str(e)}"
                )

                exit_reason = 'crash'
                current_app_class = initial_app_class

            finally:
                # 7. CLEANUP (ALWAYS runs, even on crash)
                self.log.debug("Calling on_cleanup")
                try:
                    app.on_cleanup()
                except Exception as e:
                    self.log.error(f"Error in on_cleanup: {e}")

                # Clean up resources
                self._cleanup_app(app, app_generator)

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
