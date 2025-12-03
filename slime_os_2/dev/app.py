"""
Base App class for Slime OS 2

All apps must inherit from this class.
"""


class App:
    """
    Base class for all Slime OS apps

    Apps inherit from this class and override the run() method.
    The run() method should be a generator that yields control back to the OS.

    Example:
        class MyApp(App):
            name = "My App"
            id = "my_app"

            def run(self):
                while True:
                    # Draw UI
                    self.sys.clear((0, 0, 0))
                    self.sys.draw_text("Hello World", 10, 10)
                    self.sys.update()

                    # Handle input
                    if self.sys.key_pressed(Keycode.Q):
                        return  # Exit app

                    yield  # Return control to OS

    IMPORTANT GUIDELINES:

    1. ALWAYS yield regularly (at least every 100ms)
       - Allows OS to maintain responsiveness
       - Feeds watchdog timer if enabled
       - Bad:  while True: compute()  # Never yields!
       - Good: while True: compute(); yield

    2. Keep iterations fast (< 100ms per yield)
       - OS expects regular yields
       - Break long operations into chunks

    3. To exit app, simply return or break from run()
       - return  # Exit to launcher

    4. To launch another app, return tuple:
       - return ('launch', OtherApp)  # Launch OtherApp

    5. Handle your own errors when possible
       - OS will catch unhandled exceptions
       - But better to handle gracefully in your app
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

    def run(self):
        """
        Main app loop - override this in your app.

        This should be a generator (use yield).
        Each yield returns control to the OS.
        Return or break to exit app.

        Yields:
            None (just yield) to continue
            ('launch', AppClass) to launch another app
        """
        # Default: do nothing and exit
        yield
