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
        scroll_offset = 0
        lines_per_page = 16  # ~20 lines fit on 320px screen

        while True:
            # Get recent logs
            logs = self.sys.log.get_all()

            # Draw UI
            self.sys.clear((0, 0, 0))

            # Title
            self.sys.draw_text("SYSTEM LOGS", 5, 5, scale=1, color=(255, 255, 0))
            self.sys.draw_text(f"{len(logs)} messages", 5, 18, scale=1, color=(200, 200, 200))

            # Draw logs (newest at bottom, scrollable)
            y = 35
            line_height = 12

            # Calculate which logs to show
            start_idx = max(0, len(logs) - lines_per_page - scroll_offset)
            end_idx = len(logs) - scroll_offset
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

                # Truncate long messages
                if len(message) > 38:
                    message = message[:35] + "..."

                self.sys.draw_text(f"{level[0]}: {message}", 5, y, scale=1, color=color)
                y += line_height

                if y > self.sys.height - 40:
                    break

            # Controls at bottom
            controls_y = self.sys.height - 30
            self.sys.draw_text("[Up/Down] Scroll", 5, controls_y, scale=1, color=(200, 200, 200))
            self.sys.draw_text("[C] Clear  [Q] Quit", 5, controls_y + 12, scale=1, color=(200, 200, 200))

            # Scroll indicator
            if scroll_offset > 0:
                self.sys.draw_text(f"^ {scroll_offset} more", self.sys.width - 80, controls_y, scale=1, color=(255, 255, 0))

            self.sys.update()

            # Handle input
            keys = self.sys.keys_pressed([
                Keycode.UP_ARROW,
                Keycode.DOWN_ARROW,
                Keycode.C,
                Keycode.Q
            ])

            if keys[Keycode.UP_ARROW]:
                # Scroll up (show older logs)
                max_scroll = max(0, len(logs) - lines_per_page)
                scroll_offset = min(scroll_offset + 3, max_scroll)

            if keys[Keycode.DOWN_ARROW]:
                # Scroll down (show newer logs)
                scroll_offset = max(0, scroll_offset - 3)

            if keys[Keycode.C]:
                # Clear logs
                self.sys.log.clear()
                self.sys.log.info("Logs cleared by user")
                scroll_offset = 0

            if keys[Keycode.Q]:
                # Exit
                return

            yield
