"""Pillow drawing primitives for the 1200×630 summary cards, so every layout shares one look."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTS = Path(__file__).parent / "fonts"

# Coordinates are in design pixels; the file is drawn at SCALE times that for crisp text.
SCALE = 2
WIDTH, HEIGHT = 1200, 630
PADDING = 56
ROW_TOP = PADDING + 96 + 28
ROW_HEIGHT = 394
CONTENT_WIDTH = WIDTH - 2 * PADDING

GROUND = "#F7F6F2"
INK = "#16181D"
BODY = "#2E323B"
MUTED = "#5A5F6B"
QUOTE_MARK = "#C9C4B8"
WHITE = "#FFFFFF"

Box = tuple[int, int, int, int]


@lru_cache
def font(name: str, size: int, weight: int | None = None) -> ImageFont.FreeTypeFont:
    """Loads a bundled font at a design size; weight sets the axis of the Instrument Sans variable font."""
    loaded = ImageFont.truetype(str(FONTS / name), size * SCALE)
    if weight is not None:
        loaded.set_variation_by_axes([100, weight])
    return loaded


def display(size: int) -> ImageFont.FreeTypeFont:
    """Bricolage Grotesque ExtraBold, whose default instance is the heavy display cut of the design."""
    return font("BricolageGrotesque.ttf", size)


def sans(size: int, weight: int = 600) -> ImageFont.FreeTypeFont:
    """Instrument Sans for labels and captions."""
    return font("InstrumentSans.ttf", size, weight)


class Card:
    """One card being drawn: ground and header on creation, then panels placed on the content row."""

    def __init__(self, tag: str, title: str):
        self._image = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE), GROUND)
        self._draw = ImageDraw.Draw(self._image)
        header_bottom = ROW_TOP - 28
        self._draw.text(self._at(PADDING, header_bottom), title, INK, display(54), anchor="ld")
        self._draw.text(
            self._at(PADDING, header_bottom - 54 - 10), tag, MUTED, font("IBMPlexMono-Medium.ttf", 18), anchor="ld"
        )

    def photo(self, path: Path, box: Box, radius: int = 20) -> None:
        """Pastes the photo cropped to fill the box, as CSS object-fit cover, with rounded corners."""
        x, y, w, h = box
        with Image.open(path) as source:
            fitted = ImageOps.fit(ImageOps.exif_transpose(source).convert("RGB"), (w * SCALE, h * SCALE))
        mask = Image.new("L", fitted.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, *fitted.size), radius * SCALE, fill=255)
        self._image.paste(fitted, self._at(x, y), mask)

    def tile(self, box: Box, color: str, lines: list[tuple[str, ImageFont.FreeTypeFont]], gap: int = 12) -> None:
        """Rounded colour block with white lines of text stacked and centred inside it."""
        x, y, w, h = box
        self._draw.rounded_rectangle(self._rect(box), 28 * SCALE, fill=color)
        fitted = [(text, _fit(text, face, (w - 48) * SCALE)) for text, face in lines]
        heights = [face.getbbox(text)[3] - face.getbbox(text)[1] for text, face in fitted]
        top = (y + h / 2) * SCALE - (sum(heights) + gap * SCALE * (len(fitted) - 1)) / 2
        for (text, face), height in zip(fitted, heights):
            left, ink_top, right, _ = face.getbbox(text)
            origin = ((x + w / 2) * SCALE - (left + right) / 2, top - ink_top)
            self._draw.text(origin, text, WHITE, face)
            top += height + gap * SCALE

    def quote(self, text: str, box: Box) -> None:
        """Opening quote mark and the text in italic serif, shrunk and then cut to fit the box."""
        x, y, w, h = box
        mark_w = 44
        self._quote_mark(x, y + 10)
        text_x, text_w = x + mark_w + 20, w - mark_w - 20
        for size in (40, 36, 32, 28, 24):
            face = font("InstrumentSerif-Italic.ttf", size)
            lines = _wrap(text, face, text_w * SCALE)
            line_height = round(size * 1.25)
            if len(lines) * line_height <= h:
                break
        else:
            lines = _truncate(lines[: h // line_height], face, text_w * SCALE)
        for index, line in enumerate(lines):
            self._draw.text(self._at(text_x, y + index * line_height), line, BODY, face)

    def missing(self, box: Box) -> None:
        """Pale red panel with a red X, shown where a crop could not be made."""
        x, y, w, h = box
        self._draw.rounded_rectangle(self._rect(box), 20 * SCALE, fill="#FBE9E9", outline="#C0262D", width=3 * SCALE)
        reach, stroke = 50, 18
        centre_x, centre_y = x + w / 2, y + h / 2
        for dx in (reach, -reach):
            start = ((centre_x - dx) * SCALE, (centre_y - reach) * SCALE)
            end = ((centre_x + dx) * SCALE, (centre_y + reach) * SCALE)
            self._draw.line((start, end), "#C0262D", stroke * SCALE)
            for cx, cy in (start, end):
                r = stroke * SCALE / 2
                self._draw.ellipse((cx - r, cy - r, cx + r, cy + r), "#C0262D")

    def caption(self, text: str, x: int, y: int, color: str = BODY) -> None:
        """One line of caption text whose top sits at the given design coordinates."""
        self._draw.text(self._at(x, y), text, color, sans(22))

    def save(self, destination: Path) -> Path:
        """Writes the card as PNG, creating the destination folder, and returns its path."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        self._image.save(destination, format="PNG", optimize=True)
        return destination

    def _quote_mark(self, x: int, y: int) -> None:
        """A large opening quote glyph from the same serif, in a soft tone, beside the quote."""
        self._draw.text(self._at(x, y - 10), "\u201c", QUOTE_MARK, font("InstrumentSerif-Italic.ttf", 120))

    def _at(self, x: float, y: float) -> tuple[float, float]:
        """Design coordinates to file pixels."""
        return x * SCALE, y * SCALE

    def _rect(self, box: Box) -> tuple[float, float, float, float]:
        """A design (x, y, w, h) box as the file-pixel corners Pillow expects."""
        x, y, w, h = box
        return x * SCALE, y * SCALE, (x + w) * SCALE, (y + h) * SCALE


def _fit(text: str, face: ImageFont.FreeTypeFont, width: float) -> ImageFont.FreeTypeFont:
    """Shrinks the font in steps until the text fits the width, so 100% never spills out of a tile."""
    while face.getlength(text) > width and face.size > 12 * SCALE:
        face = face.font_variant(size=face.size - 4 * SCALE)
    return face


def _wrap(text: str, face: ImageFont.FreeTypeFont, width: float) -> list[str]:
    """Greedy word wrap of the text to lines no wider than width."""
    lines: list[str] = []
    for word in text.split():
        candidate = f"{lines[-1]} {word}" if lines else word
        if lines and face.getlength(candidate) <= width:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines


def _truncate(lines: list[str], face: ImageFont.FreeTypeFont, width: float) -> list[str]:
    """Ends the last line with an ellipsis, dropping words until it fits the width."""
    last = lines[-1]
    while last and face.getlength(f"{last}…") > width:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    return [*lines[:-1], f"{last}…"]
