class AbstractDisplay:
    def __init__(self, width:int, height:int):
        self.width = width
        self.height = height

    def get_bounds(self):
        """
        Returns the width and height of the display.
        """
        return self.width -1, self.height -1

    def set_pen(self, r, g, b):
        """
        Sets the pen color for drawing.
        """ 
        raise NotImplementedError("Subclasses should implement this method.")

    def rectangle(self, x, y, w, h):
        """
        Draws a rectangle on the display.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def pixel(self, x, y):
        """
        Draws a pixel on the display.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def line(self, x, y, x2, y2, t=1):
        """
        Draws a line on the display.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def text(self, text, x, y, scale=1, angle=0):
        """
        Draws text on the display.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def measure_text(self, text, scale=1):
        """
        Measures the size of the text.
        """
        raise NotImplementedError("Subclasses should implement this method.")

    def update(self):
        """
        Updates the display.
        """
        raise NotImplementedError("Subclasses should implement this method.")