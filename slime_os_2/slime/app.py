"""
Slime OS 2 - App Base Class

All apps inherit from this class and implement the run() method.
The run() method should be a generator that yields control back to the OS.
"""


class App:
    """
    Base class for all Slime OS apps

    Apps inherit from this class and override the run() method.
    The run() method should be a generator that yields control back to the OS.

    Lifecycle hooks (optional overrides):
    - on_enter(): Called when app starts, before run() is called
    - on_exit(): Called when app exits normally (return/break from run())
    - on_cleanup(): Always called when app is torn down (even on crash)

    By default, the display is automatically cleared on enter, exit, and cleanup.
    Apps can override these hooks to customize behavior (call super() to keep clearing).
    """

    # App metadata (override in subclass)
    name = "Unknown App"
    id = "unknown"

    def __init__(self, system):
        """
        Initialize app.

        Args:
            system: System instance (provides display, input, etc.)
        """
        self.sys = system

    # ========================================================================
    # Lifecycle Hooks - Override these in your app as needed
    # ========================================================================

    def on_enter(self):
        """
        Called when app is about to start running.

        This is called BEFORE the run() generator is created.

        Default behavior: Resets display to clean state (clears framebuffer,
        text queue, and display itself).

        Use this to:
        - Initialize app state
        - Show loading screen
        - Set up resources

        To customize:
        - Call super().on_enter() first to keep display clearing
        - Or override completely for custom transition effects

        Note: This is called even if the app crashes during run()
        """
        # Clear display and all buffers
        self.sys.reset_display()

    def on_exit(self, reason='normal'):
        """
        Called when app exits normally.

        This is called AFTER run() returns/breaks, but BEFORE cleanup.

        Default behavior: Resets display to clean state.

        Args:
            reason: Exit reason string
                - 'normal': App returned normally
                - 'launch': App is launching another app
                - 'interrupt': User interrupted (Ctrl+C)

        Use this to:
        - Save state
        - Show transition screen
        - Release non-critical resources

        To customize:
        - Call super().on_exit(reason) first to keep display clearing
        - Or override completely for custom transition effects

        Note: NOT called if app crashes - use on_cleanup() for guaranteed cleanup
        """
        # Clear display and all buffers
        self.sys.reset_display()

    def on_cleanup(self):
        """
        Called when app is being torn down.

        This is ALWAYS called when app exits (in finally block).

        Default behavior: Resets display to clean state (failsafe).

        Use this to:
        - Release resources (files, memory, etc.)
        - Restore hardware state
        - Free memory

        To customize:
        - Call super().on_cleanup() first to keep display clearing
        - Keep this method simple and error-free

        Note: This is called even if the app crashes!
        Exceptions in this method are caught and ignored to prevent cascading failures.
        """
        try:
            # Failsafe: clear display even on crash
            self.sys.reset_display()
        except:
            pass  # Ignore errors during cleanup

    # ========================================================================
    # Main App Loop - Override this in your app
    # ========================================================================

    def run(self):
        """
        Main app loop - override this in your app.

        This should be a generator (use yield).
        Each yield returns control to the OS.
        Return or break to exit app.

        IMPORTANT:
        - ALWAYS yield regularly (at least every 100ms) to prevent watchdog timeout
        - Keep iterations fast (< 100ms per yield)
        - To exit app: `return` or `break` from run()
        - To launch another app: `return ('launch', OtherAppClass)`

        Yields:
            None (just yield) to continue app loop
            ('launch', AppClass) to launch another app

        Example:
            def run(self):
                self.count = 0
                while True:
                    # Update state
                    self.count += 1

                    # Draw UI
                    self.sys.clear()
                    self.sys.draw_text(f"Count: {self.count}", 10, 10)
                    self.sys.update()

                    # Check for exit
                    if self.sys.key_pressed(Keycode.Q):
                        return

                    # Yield control back to OS
                    yield
        """
        # Default: do nothing and exit
        yield
