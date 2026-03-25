from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, field
from model import Surface

# FONT_SIZE_H1 = 50
# FONT_SIZE_DEFAULT = 24
# FONT_SIZE_SUMMARY = 36

LINE_SPACING = 8

BLACK = 0x000000  #   00  BGR
WHITE = 0xFFFFFF  #   01
YELLOW = 0x00FFFF  #   10
RED = 0x0000FF  #   11


# DEFAULT_FONT_FILE = "fonts/Font.ttc"
# BOLD_FONT_FILE = "fonts/Font.ttc"
# FONT_SIZE_H1 = 48
# FONT_SIZE_DEFAULT = 24
# FONT_SIZE_SUMMARY = 36
# PADDING = 5


DEFAULT_FONT_FILE = "fonts/DejaVuSansCondensed.ttf"
BOLD_FONT_FILE = "fonts/DejaVuSansCondensed-Bold.ttf"
FONT_SIZE_H1 = 48
FONT_SIZE_DEFAULT = 28
FONT_SIZE_SUMMARY = 43
PADDING = 5

#DEFAULT_FONT_FILE = "fonts/RobotoCondensed-Regular.ttf"
#BOLD_FONT_FILE = "fonts/RobotoCondensed-Bold.ttf"

# DEFAULT_FONT_FILE = "fonts/LiberationSansNarrow-Regular.ttf"
# BOLD_FONT_FILE = "fonts/LiberationSansNarrow-Bold.ttf"
# FONT_SIZE_H1 = 50
# FONT_SIZE_DEFAULT = 24
# FONT_SIZE_SUMMARY = 36
# PADDING = 5


def borders(box) -> int:
    return box.margin * 2 + box.stroke * 2 + box.padding * 2


def font(file=DEFAULT_FONT_FILE, size=FONT_SIZE_DEFAULT):
    return ImageFont.truetype(file, size)

def important_font(size=FONT_SIZE_DEFAULT):
    return ImageFont.truetype(BOLD_FONT_FILE, size)

def important_font(size=FONT_SIZE_DEFAULT):
    return ImageFont.truetype(BOLD_FONT_FILE, size)    


def find_break_index(line, font, pixel_width):
    i = len(line) - 1
    while i > 0:
        length = font.getlength(line[:i])
        if length > pixel_width:
            i -= 1
            continue

        return find_nearest_separator(line, i)
    return 1


def find_nearest_separator(line, max):
    i = max
    while i > 0:
        if line[i] == " ":
            return i
        i -= 1
    return max


def split_line(lines, line, font, pixel_width):
    length = font.getlength(line)

    if length <= pixel_width:
        lines.append(line)
        return
    break_index = find_break_index(line, font, pixel_width)
    lines.append(line[:break_index].strip())
    split_line(lines, line[break_index:].strip(), font, pixel_width)


@dataclass
class Text:
    text: str
    _wrapped_text = ""
    color: int = BLACK
    font: object = font()
    padding_top: int = 0

    def render(self, draw: ImageDraw, surface: Surface):
        text = self.wrapped_text(surface.right - surface.left)

        # Debugging - make the background of the text yellow
        # bbox = draw.multiline_textbbox((surface.left, surface.top + self.padding_top), text, font=self.font)
        # draw.rectangle(bbox, fill="yellow")

        draw.text(
            (surface.left, surface.top + self.padding_top),
            text,
            font=self.font,
            fill=self.color,
        )

    """
    Sets the wrapped_text which is then cached for use in the render method. Suspect this shouldn't be cached.

    width: number
        The width allowed for the text box
    """
    def wrapped_text(self, width):
        if self._wrapped_text != "":
            return self._wrapped_text
        lines = []
        for line in self.text.split("\n"):
            split_line(lines, line, self.font, width)
        self._wrapped_text = "\n".join(lines)
        return self._wrapped_text

    def height(self, width: int, draw: ImageDraw):
        _, _, _, bbox_height = draw.multiline_textbbox((0, 0), self.wrapped_text(width), font=self.font, spacing=LINE_SPACING)
        return bbox_height


@dataclass
class StackChildrenBox:
    padding: int = PADDING
    margin: int = 0
    stroke: int = 1
    outline: int = None
    horizontal: bool = True
    fill: int = None
    children: list = field(default_factory=list)

    def render(self, draw: ImageDraw, surface: Surface):
        t = surface.top
        b = surface.bottom
        l = surface.left
        r = surface.right

        m = self.margin
        p = self.padding

        if self.stroke > 0:
            border = (l + m, t + m, r - m, b - m)
            draw.rectangle(
                border, fill=self.fill, outline=self.outline, width=self.stroke
            )

        t = t + m + p
        for child in self.children:
            cl = l + m + p
            cr = r - m - p
            cw = cr - cl
            ch = child.height(cw, draw)
            cb = t + ch
            if cb > b:
                cb = b
            cs = Surface(top=t, left=cl, right=cr, bottom=cb)
            child.render(draw, cs)
            t = t + ch
            if cb == b:
                return


@dataclass
class RightStretchBox:
    padding: int = PADDING
    margin: int = 0
    stroke: int = 1
    outline: int = None
    horizontal: bool = True
    fill: int = None
    left: object = None
    left_width: int = 0
    right: object = None

    # I think this is not quite right because there's always a bit of extra padding at the bottom of the boxes.
    def height(self, width, draw):
        return max(
            self.left.height(self.left_width - borders(self) / 2, draw),
            self.right.height(width - self.left_width - borders(self) / 2, draw),
        ) + borders(self)

    def render(self, draw: ImageDraw, surface: Surface):
        t = surface.top
        b = surface.bottom
        l = surface.left
        r = surface.right
        w = r - l

        m = self.margin
        p = self.padding

        if self.stroke > 0:
            border = (l + m, t + m, r - m, b - m)
            draw.rectangle(
                border, fill=self.fill, outline=self.outline, width=self.stroke
            )

        cl = l + m + p
        cr = cl + self.left_width
        ct = t + m + p
        cb = self.height(w, draw)
        cs = Surface(top=ct, left=cl, right=cr, bottom=cb)
        self.left.render(draw, cs)
        cl = cr
        cr = r - m - p
        cs = Surface(top=ct, left=cl, right=cr, bottom=cb)
        self.right.render(draw, cs)


@dataclass
class EqualChildrenBox:
    padding: int = PADDING
    margin: int = 0
    stroke: int = 1
    outline: int = None
    horizontal: bool = True
    fill: int = None
    children: list = field(default_factory=list)

    def render(self, draw: ImageDraw, surface: Surface):
        t = surface.top
        b = surface.bottom
        h = b - t
        l = surface.left
        r = surface.right
        w = r - l

        m = self.margin
        p = self.padding

        if self.stroke > 0:
            border = (l + m, t + m, r - m, b - m)
            draw.rectangle(
                border, fill=self.fill, outline=self.outline, width=self.stroke
            )

        nc = len(self.children)
        for i, child in enumerate(self.children):
            cl = l + m + p
            cr = r - m - p
            ct = t + m + p
            cb = b - m - p
            if self.horizontal:
                step = (w - (m + p) * 2) / nc
                cl = l + m + p + int(step * i)
                cr = l + m + p + int(step * (i + 1))
            else:
                step = (h - (m + p) * 2) / nc
                ct = t + m + p + int(step * i)
                cb = t + m + p + int(step * (i + 1))
            cs = Surface(top=ct, left=cl, right=cr, bottom=cb)
            child.render(draw, cs)


@dataclass
class SingleChildBox:
    padding: int = PADDING
    margin: int = 0
    stroke: int = 1
    outline: int = None
    horizontal: bool = True
    fill: int = None
    child: object = None

    def render(self, draw: ImageDraw, surface: Surface):
        t = surface.top
        b = surface.bottom
        l = surface.left
        r = surface.right

        m = self.margin
        p = self.padding
        s = self.stroke

        if self.stroke > 0:
            border = (l + m, t + m, r - m, b - m)
            draw.rectangle(
                border, fill=self.fill, outline=self.outline, width=self.stroke
            )

        child = self.child
        cl = l + m + p + s
        cr = r - m - p - s
        ct = t + m + p + s
        cb = b - m - p - s
        cs = Surface(top=ct, left=cl, right=cr, bottom=cb)
        child.render(draw, cs)

    def height(self, width: int, draw: ImageDraw):
        return (
            self.child.height(
                width - (self.margin * 2) - (self.padding * 2) - (self.stroke * 2),
                draw
            )
            + self.margin * 2
            + self.padding * 2
            + self.stroke * 2
        )
