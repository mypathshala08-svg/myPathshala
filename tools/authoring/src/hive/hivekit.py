"""Small drawing helpers shared by the Apache Hive lessons (authoring time only)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from svgkit import *


def keep(spec, inner):
    """Show `inner` on the frames in spec, e.g. keep('2-', ...) or keep('2-4,6', ...)."""
    return f'<g data-on="{spec}">{inner}</g>'


def chip(x, y, label, color='acc', w=30, h=14, size=7.6, txt='#fff'):
    return fill(x, y, w, h, color, rx=3) + t(x + w / 2, y + h / 2 + 2.8, label, size, bold=True, extra=f' style="fill:{txt}"')


def tall(x, y, w, h, title, lines, tone='card', size=7.6, mono=True):
    """Box with a bold title and a few left-aligned lines."""
    o = box(x, y, w, h, tone) + t(x + w / 2, y + 11, title, 8.2, bold=True)
    for k, ln in enumerate(lines):
        o += t(x + 6, y + 24 + k * 11, ln, size, 'ink2', anchor='start', mono=mono)
    return o


def cyl(x, y, w, h, label, tone='card', size=8.4):
    """A small database drum."""
    cls, st = TONES[tone]
    return (f'<path d="M{x} {y+6}v{h-12}a{w/2} 6 0 0 0 {w} 0v-{h-12}" class="{cls}" style="stroke:{st}"/>'
            f'<ellipse cx="{x+w/2}" cy="{y+6}" rx="{w/2}" ry="6" class="{cls}" style="stroke:{st}"/>'
            + t(x + w / 2, y + h / 2 + 5, label, size, bold=True))


def dn(x, y, w, h, label, tone='card'):
    return box(x, y, w, h, tone) + t(x + w / 2, y + 11, label, 8, bold=True)


def tag(x, y, text, color='acc', size=8):
    return t(x, y, text, size, color, anchor='start', bold=True)


G, W, Y, RD = '#9FD3B8', '#EDEBE3', '#F5C77E', '#FF8A80'


def term(lines, label='terminal · real output', size=8, step=14, x=26, y0=50):
    """Dark terminal panel (360x250 view). lines: [(text, colour)]; text is escaped."""
    import html as _h
    o = f'<rect x="14" y="14" width="332" height="196" rx="8" class="s-board"/><text x="26" y="30" font-size="9" class="mono" style="fill:#7F8C86">{_h.escape(label)}</text>'
    for k, (txt, col) in enumerate(lines):
        o += f'<text x="{x}" y="{y0 + k * step}" font-size="{size}" class="mono" style="fill:{col};white-space:pre" xml:space="preserve">{_h.escape(txt)}</text>'
    return o


def node(x, y, w, h, title, sub='', tone='card', on=True, size=8.4):
    """A component box; dimmed when on is False."""
    op = '' if on else ' opacity=".35"'
    o = f'<g{op}>' + box(x, y, w, h, tone) + t(x + w / 2, y + (h / 2 + 3 if not sub else h / 2 - 2), title, size, bold=True)
    if sub:
        o += t(x + w / 2, y + h / 2 + 10, sub, 7.2, 'ink2')
    return o + '</g>'


def tables(text):
    """Split concatenated Beeline table outputs into a list of tables."""
    import re as _re
    return [p.strip('\n') for p in _re.split(r'\n(?=\+[-+]+\+\n\|[^\n]*\|\n\+[-+]+\+)', text.strip('\n')) if p.strip()]
