"""Measured plate framework for the 1080×1080 LinkedIn card.

Every number below was read off the HTML screenshot of docs/linkedin.png,
component by component. The renderer draws from this spec. It does not
open HTML.
"""

from __future__ import annotations

W = 1080
H = 1080

CREAM = (255, 249, 239)
NAVY = (29, 53, 80)
TAUPE = (106, 92, 78)
GREEN = (46, 125, 50)
RING = (217, 203, 184)
HL = (91, 143, 184)
HL_BG = (214, 232, 245)

# Faces chosen by fitting each ink box. Gelasio is the browser Georgia stand-in.
SERIF = "Gelasio"
SERIF_CJK = "Noto Serif CJK KR"
SANS = "Lato"


class Box:
    def __init__(self, x: float, y: float, w: float, h: float) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h


class TextSpec:
    def __init__(
        self,
        text: str,
        family: str,
        size: float,
        fill: tuple[int, int, int],
        *,
        cx: float,
        cy: float,
        bold: bool = False,
        italic: bool = False,
        tracking: float = 0,
    ) -> None:
        self.text = text
        self.family = family
        self.size = size
        self.fill = fill
        self.cx = cx
        self.cy = cy
        self.bold = bold
        self.italic = italic
        self.tracking = tracking


# Header. Ink boxes from the screenshot, optical centers derived from them.
# Kicker ink x 390..682, y 68..81. Size 15, gap 11.36 fills that width.
KICKER = TextSpec(
    "BLOCKCHAIN IDEA",
    SANS,
    15,
    TAUPE,
    cx=536,
    cy=74.5,
    tracking=11.36,
)
# Title sits 51px under the kicker, the cream gap measured on how-to-devops
# (kicker ink ends at y 91, title ink starts at y 143).
TITLE = TextSpec("Proof of AI", "Liberation Serif", 50, NAVY, cx=539, cy=149.5, bold=True)
# Tagline keeps its 22px gap under the title.
TAGLINE = TextSpec(
    "Use your favourite model to produce blocks.",
    "Liberation Serif",
    27,
    TAUPE,
    cx=539.5,
    cy=202,
    italic=True,
)

# Two blocks. Stroke is 2px. Dropped 30px with the title so the 51px
# kicker gap from how-to-devops does not collide with the bars.
BLOCK_TOP = 252
BLOCK_BOTTOM = 922
BLOCK_H = BLOCK_BOTTOM - BLOCK_TOP
LEFT = Box(32, BLOCK_TOP, 494, BLOCK_H)
RIGHT = Box(554, BLOCK_TOP, 494, BLOCK_H)
HEADER_H = 94  # filled bar, outer pixels y 222..315
# Bar label ink y 261..278, so the optical center is 269.5.
HEADER_LABEL_CY = 299.5
HEADER_LABEL_SIZE = 27  # Lato bold; "Block n+1" is 118px, bar ink is ~114px
# Story title ink y 334..355, width 162. Liberation Serif italic 26 is 155×22.
STORY_TITLE_CY = 374.5
STORY_TITLE_SIZE = 26
STORY_TITLE_FACE = "Liberation Serif"
TITLE_RULE_Y = 396.75  # 1.5px stroke centered so ink lands on rows 396..397
# Story lines measured off the screenshot. x is the line start; seed words
# carry highlight=True and stay inline, which is where the HTML put them.
# Story face fitted to the measured line length (459px) and seed-word boxes.
STORY_FACE = "DejaVu Serif"
STORY_SIZE = 18
STORY_LINE_H = 34  # band pitch 377, 411, 446, 480, 514
STORY_BASELINE = 424
LEFT_LINES = (
    (48, (("Mara reached the ", False), ("harbor", True), (" after the last", False))),
    (48, (("ferry had gone. She lit the ", False), ("lantern", True), (", set it on", False))),
    (48, (("a crate of ", False), ("salt", True), (", and pinned the ", False), ("map", True), (" under", False))),
    (48, (("a stone so the wind could not take Tomas’s mark.", False),)),
    (48, (("Out past the pier, the ", False), ("tide", True), (" was already", False))),
    (48, (("turning. She would wait the night.", False),)),
)
RIGHT_LINES = (
    (570, (("At dawn the ", False), ("lantern", True), (" was cold. ", False), ("Salt", True))),
    (570, (("had crusted Tomas’s mark on the ", False), ("map", True), (", and", False))),
    (570, (("the ink had run to a cove Mara had never", False),)),
    (570, (("drawn. She walked the empty ", False), ("harbor", True), (" until", False))),
    (570, (("the ", False), ("tide", True), (" laid his skiff on the stones, oar", False))),
    (570, (("still lashed, and a second lantern burning inside.", False),)),
)
RADAR_RADIUS = 78
RADAR_CY = 730  # green ink shifted with the blocks
SCORE_CY = 900.5  # score ink shifted with the blocks

COPYRIGHT = TextSpec(
    "© 수영 책방 Swimming Bookstore",
    SERIF_CJK,
    20,
    TAUPE,
    cx=539.5,
    cy=1058,
)

AXES = ("Plot", "People", "Writing", "Fun", "Link")
LABEL_OFFSETS = (
    (0, -(RADAR_RADIUS + 18), "middle"),
    (RADAR_RADIUS + 8, -4, "start"),
    (RADAR_RADIUS * 0.42, RADAR_RADIUS + 20, "middle"),
    (-(RADAR_RADIUS * 0.42), RADAR_RADIUS + 20, "middle"),
    (-(RADAR_RADIUS + 8), -4, "end"),
)
