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

    def run(self):
        """Main app loop"""
        self.scroll_offset = 0
        self.lines_per_page = 16  # ~20 lines fit on 320px screen
        self.need_update = True
        self.last_log_count = 0
        while True:
            # Get recent logs
            logs = self.sys.log.get_all()

            if len(logs) != self.last_log_count:
                self.need_update = True
                self.last_log_count = len(logs)

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.C,
                Keycode.Q
            ])

            if keys[Keycode.UP_ARROW]:
                # Scroll up (show older logs)
                max_scroll = max(0, len(logs) - self.lines_per_page)
                self.scroll_offset = min(self.scroll_offset + 3, max_scroll)

            if keys[Keycode.DOWN_ARROW]:
                # Scroll down (show newer logs)
                self.scroll_offset = max(0, self.scroll_offset - 3)

            if keys[Keycode.C]:
                # Clear logs
                self.sys.log.clear()
                self.sys.log.info("Logs cleared by user")
                self.scroll_offset = 0

            if keys[Keycode.Q]:
                # Exit
                return

            # Check if any key was pressed
            if any(keys.values()):
                self.need_update = True

            if self.need_update:
                self._draw_ui(logs)
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

            # Wrap long messages
            wrapped_message = textwrap.fill(message, width=38)
            for line in wrapped_message.split("\n"):
                self.sys.draw_text(f"{level[0]}: {line}", 5, y, scale=1, color=color)
            y += line_height

            if y > self.sys.height - 40:
                break

        # Controls at bottom
        controls_y = self.sys.height - 30
        self.sys.draw_text("[Up/Down] Scroll", 5, controls_y, scale=1, color=(200, 200, 200))
        self.sys.draw_text("[C] Clear  [Q] Quit", 5, controls_y + 12, scale=1, color=(200, 200, 200))

        # Scroll indicator
        if self.scroll_offset > 0:
            self.sys.draw_text(f"^ {self.scroll_offset} more", self.sys.width - 80, controls_y, scale=1, color=(255, 255, 0))

        self.sys.update()