"""
Log Viewer App

View recent system logs for debugging.
"""

from slime.app import App
from lib.keycode import Keycode


class LogViewerApp(App):
    """View system logs"""

    name = "Log Viewer"
    id = "log_viewer"

    def on_cleanup(self):
        """Clean up cached logs to free memory"""
        super().on_cleanup()
        if hasattr(self, 'cached_logs'):
            self.cached_logs = []

    def run(self):
        """Main app loop"""
        self.scroll_offset = 0
        self.lines_per_page = 16  # ~20 lines fit on 320px screen
        self.need_update = True
        self.last_log_count = 0
        # Cache logs - only copy when count changes
        self.cached_logs = []

        while True:
            # Only get logs if count changed (avoid copying every frame)
            current_log_count = len(self.sys.log.messages)
            if current_log_count != self.last_log_count:
                self.cached_logs = self.sys.log.get_all()
                self.need_update = True
                self.last_log_count = current_log_count

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.C,
                Keycode.M,
                Keycode.Q
            ])

            if keys[Keycode.UP_ARROW]:
                # Scroll up (show older logs)
                max_scroll = max(0, len(self.cached_logs) - self.lines_per_page)
                self.scroll_offset = min(self.scroll_offset + 3, max_scroll)
                self.need_update = True

            if keys[Keycode.DOWN_ARROW]:
                # Scroll down (show newer logs)
                self.scroll_offset = max(0, self.scroll_offset - 3)
                self.need_update = True

            if keys[Keycode.C]:
                # Clear logs
                self.sys.log.clear()
                self.sys.log.info("Logs cleared by user")
                self.cached_logs = self.sys.log.get_all()
                self.scroll_offset = 0
                self.need_update = True

            if keys[Keycode.M]:
                # Memory debug - add test lines and log memory usage
                import gc
                for i in range(10):
                    self.sys.log.debug(f"Test log line {i + 1}")

                # Log memory info
                gc.collect()
                mem = self.sys.memory_info()
                self.sys.log.info(f"MEM: {mem['free']//1024}KB free, {mem['allocated']//1024}KB used ({mem['percent_used']:.1f}%)")

                # Force cache update
                self.cached_logs = self.sys.log.get_all()
                self.last_log_count = len(self.sys.log.messages)
                self.need_update = True

            if keys[Keycode.Q]:
                # Exit
                return

            if self.need_update:
                self._draw_ui(self.cached_logs)
                self.need_update = False
            yield

    def _draw_ui(self, logs):
        # Draw UI
        self.sys.clear((0, 0, 0))

        # Title
        self.sys.draw_text("SYSTEM LOGS", 5, 5, scale=1, color=(255, 255, 0))
        self.sys.draw_text(f"{len(logs)} messages", 5, 18, scale=1, color=(200, 200, 200))

        # Draw logs (newest at bottom, scrollable)
        y = 35
        line_height = 12

        # Calculate which logs to show
        start_idx = max(0, len(logs) - self.lines_per_page - self.scroll_offset)
        end_idx = len(logs) - self.scroll_offset
        visible_logs = logs[start_idx:end_idx]

        for timestamp, level, message in visible_logs:
            # Color by level
            if level == "ERROR":
                color = (255, 0, 0)  # Red
            elif level == "WARN":
                color = (255, 255, 0)  # Yellow
            elif level == "DEBUG":
                color = (128, 128, 128)  # Gray
            else:  # INFO
                color = (255, 255, 255)  # White

            # Truncate long messages - use slice to avoid string concat
            if len(message) > 36:
                display_message = message[:33] + "..."
            else:
                display_message = message

            # Format once and draw
            line_text = f"{level[0]}: {display_message}"
            self.sys.draw_text(line_text, 5, y, scale=1, color=color)
            y += line_height

            if y > self.sys.height - 40:
                break

        # Controls at bottom
        controls_y = self.sys.height - 42
        self.sys.draw_text("[Up/Down] Scroll", 5, controls_y, scale=1, color=(200, 200, 200))
        self.sys.draw_text("[C] Clear  [M] Mem", 5, controls_y + 12, scale=1, color=(200, 200, 200))
        self.sys.draw_text("[Q] Quit", 5, controls_y + 24, scale=1, color=(200, 200, 200))

        # Scroll indicator
        if self.scroll_offset > 0:
            self.sys.draw_text(f"^ {self.scroll_offset} more", self.sys.width - 80, controls_y, scale=1, color=(255, 255, 0))

        self.sys.update()