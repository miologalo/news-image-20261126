#!/usr/bin/env python3
"""news-image-20261126: draw a newspaper front page for Thursday 26 November 2026.

Deterministic: no randomness, no wall clock, no network. Writes one PNG to
/output/entry.png (or argv[1] / $MAKEFUN_OUTPUT_DIR/entry.png for local runs).
Pillow + the DejaVu fonts shipped on the system only.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 768, 1024
MARGIN = 30
CW = W - 2 * MARGIN

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (176, 24, 24)
NAVY = (16, 34, 64)
GREY = (96, 96, 96)
LIGHT_GREY = (222, 222, 222)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


SERIF_BOLD = lambda s: load("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: load("DejaVuSerif.ttf", s)
SANS_BOLD = lambda s: load("DejaVuSans-Bold.ttf", s)
SANS = lambda s: load("DejaVuSans.ttf", s)


def wrap_text(draw, text, font, max_w):
    """Greedy word wrap measured in pixels; returns the wrapped lines."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=font) <= max_w:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_lines(draw, x, y, text, font, max_w, fill=BLACK, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(font.size * 1.3)
    for line in wrap_text(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def hrule(draw, y, thickness=2, fill=BLACK, x0=None, x1=None):
    x0 = MARGIN if x0 is None else x0
    x1 = W - MARGIN if x1 is None else x1
    draw.rectangle([x0, y, x1, y + thickness - 1], fill=fill)
    return y + thickness


def centred(draw, y, text, font, fill=BLACK):
    """Draw one line centred on the page; returns the y below it."""
    w = draw.textlength(text, font=font)
    draw.text(((W - w) / 2, y), text, font=font, fill=fill)
    return y + int(font.size * 1.3)


def headline_block(draw, y, kicker, headline, deck, head_size, head_font,
                   deck_size=19, gap=6):
    """A kicker + wrapped headline + wrapped deck; returns the y below."""
    if kicker:
        y = draw_lines(draw, MARGIN, y, kicker, SANS_BOLD(15), CW,
                       fill=RED, leading=20)
        y += 2
    y = draw_lines(draw, MARGIN, y, headline, head_font(head_size), CW,
                   leading=int(head_size * 1.18))
    y += gap
    if deck:
        y = draw_lines(draw, MARGIN, y, deck, SANS(deck_size), CW,
                       fill=(40, 40, 40), leading=int(deck_size * 1.3))
    return y


def news_item(draw, y, title, deck):
    """One short item in the round-up: bold title, one-line deck."""
    y = draw_lines(draw, MARGIN, y, title, SANS_BOLD(20), CW, leading=24)
    y = draw_lines(draw, MARGIN, y, deck, SANS(17), CW, fill=(40, 40, 40),
                   leading=21)
    return y + 5


def build():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    y = 22

    # Masthead
    y = centred(d, y, "THE WORLD TODAY", SERIF_BOLD(54), fill=NAVY)
    y += 2
    y = hrule(d, y, 3)
    y += 6
    y = hrule(d, y, 1)
    y += 10

    # Date line
    y = centred(d, y, "THURSDAY 26 NOVEMBER 2026", SANS_BOLD(25), fill=RED)
    y += 4
    y = hrule(d, y, 1)
    y += 14

    # Lead story: Cairo tanker fire
    y = headline_block(
        d, y,
        kicker="CAIRO",
        headline="Fuel tanker crash and fire kills 31, injures 21",
        deck="A fuel tanker overturns on a crowded Cairo road and bursts into "
             "flames, killing 31 people and injuring 21 as firefighters battle "
             "the blaze and hospitals take in the wounded.",
        head_size=42, head_font=SERIF_BOLD, deck_size=18, gap=7)
    y += 8
    y = hrule(d, y, 1, fill=LIGHT_GREY)
    y += 10

    # Second story: Macy's parade postponed
    y = headline_block(
        d, y,
        kicker="NEW YORK",
        headline="Macy's Thanksgiving Day Parade postponed for the first "
                 "time in 100 years",
        deck="A storm forces the parade to Saturday, November 28 - the first "
             "postponement in the event's century-long history.",
        head_size=30, head_font=SERIF_BOLD, deck_size=18, gap=6)
    y += 8
    y = hrule(d, y, 1, fill=LIGHT_GREY)
    y += 8

    # Round-up header
    y = centred(d, y, "AROUND THE WORLD", SANS_BOLD(17), fill=NAVY)
    y += 4
    y = hrule(d, y, 1)
    y += 8

    # Supporting stories
    y = news_item(d, y, "US announces tariffs of up to 20%",
                  "New duties hit China, the EU and 12 other nations.")
    y = news_item(d, y, "Bangkok oil depot explosion injures 7",
                  "Four of the injured are in a critical condition.")
    y = news_item(d, y, "Israeli strikes in Gaza kill 9",
                  "The dead include a Hamas-appointed minister.")
    y = news_item(d, y, "Kim Jong Un displays nuclear warheads",
                  "North Korea shows off its arsenal in a new inspection.")
    y = news_item(d, y, "UK net migration falls to 77,000",
                  "Lowest since 1997 outside the Covid years.")
    y = news_item(d, y, "Iran mine strikes hit tankers near Hormuz",
                  "Attacks raise fears for shipping through the strait.")
    y = news_item(d, y, "Russian missiles hit Kyiv shopping centre",
                  "Seven people wounded in a strike on the capital.")
    y += 2

    # Footer
    y = hrule(d, y, 1, fill=LIGHT_GREY)
    y += 8
    centred(d, y, "THE WORLD TODAY  -  THURSDAY 26 NOVEMBER 2026",
            SANS(14), fill=GREY)

    return img


def main():
    if len(sys.argv) > 1:
        out_dir = sys.argv[1]
    else:
        out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
