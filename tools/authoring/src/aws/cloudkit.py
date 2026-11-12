"""Drawing + section helpers for Cloud lessons (authoring time only)."""
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


# ---- Module 4+ helpers
_CAPDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lab', 'captures') + os.sep


def capsec(name, a, b=None, drop=()):
    """Text of capture `name` from marker a up to marker b (exclusive); lines containing any of `drop` removed."""
    s = open(_CAPDIR + name).read().rstrip()
    i = s.index(a)
    j = s.index(b, i + len(a)) if b else len(s)
    out = s[i:j].rstrip()
    if drop:
        out = '\n'.join(l for l in out.split('\n') if not any(d in l for d in drop))
    return out


def opbox(x, y, label, sub='', tone='card', w=128, h=26):
    o = box(x, y, w, h, tone) + t(x + w / 2, y + (11 if sub else 16), label, 7.2, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 21, sub, 6.4, 'ink2', mono=True)
    return o


def flow(items, y=40, x0=8, w=74, gap=16, h=30):
    """A left-to-right row of boxes: items = [(label, sub, tone)]."""
    o = ''
    for k, (lab, sub, tone) in enumerate(items):
        x = x0 + k * (w + gap)
        o += opbox(x, y, lab, sub, tone, w, h)
        if k:
            o += arrow(x - gap, y + h / 2, x, y + h / 2, 'ink3', 1.1)
    return o


# ---- Kafka helpers
def figure(aria, content, h=200, caption=''):
    """A wide static figure (640 x h) for image dissection."""
    cap_ = f'<text x="320" y="{h - 10}" text-anchor="middle" font-size="10.5" class="s-ink2">{caption}</text>' if caption else ''
    return f'''    <div class="scene">
      <svg viewBox="0 0 640 {h}" role="img" aria-label="{aria}">
        {content}
        {cap_}
        <text x="632" y="{h - 2}" text-anchor="end" class="s-wm">myphatshala.in</text>
      </svg>
    </div>'''


def pin(x, y, n, color='acc'):
    """Numbered call-out circle."""
    return (f'<circle cx="{x}" cy="{y}" r="8" class="s-{color}" style="fill:var(--{"track" if color == "acc" else color})"/>'
            + t(x, y + 3, str(n), 8, bold=True, extra=' style="fill:#fff"'))


def legend(x, y, items, size=8, gap=15, w=None):
    """Numbered legend lines: [(n, bold, text)]."""
    o = ''
    for k, (n, b, txt) in enumerate(items):
        yy = y + k * gap
        o += pin(x + 8, yy - 3, n) + t(x + 22, yy, b, size, 'ink', anchor='start', bold=True) + t(x + (w or 170), yy, txt, size - 0.4, 'ink2', anchor='start')
    return o


def pcol(x, y, label, cells, tone='blue', cw=34, ch=20, hi=()):
    """A partition drawn as a row of offset cells. cells: list of short strings."""
    o = t(x - 6, y + ch / 2 + 3, label, 8, 'ink', anchor='end', bold=True)
    for k, c in enumerate(cells):
        o += box(x + k * (cw + 2), y, cw, ch, 'acc' if k in hi else tone, rx=3) + t(x + k * (cw + 2) + cw / 2, y + ch / 2 + 3, c, 7, 'ink', mono=True)
    return o


def fields(x, y, items, h=22, size=7.6, gap=4):
    """A row of field boxes [(text, tone, pin_no or None)]; width from text length (mono). Returns svg."""
    o = ''
    for txt, tone, n in items:
        w = len(txt) * size * 0.62 + 12
        o += box(x, y, w, h, tone, rx=3) + t(x + w / 2, y + h / 2 + 3, txt, size, 'ink', mono=True)
        if n:
            o += pin(x + 2, y - 2, n)
        x += w + gap
    return o


# ---- Learning-design helpers (hook, concept map, layer peel, why/how/where)
def hook(question, promise, teasers):
    """Opening hook: one curious question, what you will be able to do, 3 'you will find out' teasers."""
    lis = ''.join(f'<li>{x}</li>' for x in teasers)
    return f'''<div class="callout callout--exam" style="display:block"><p style="font-size:1.12rem;margin:0 0 6px"><b>🤔 {question}</b></p><p style="margin:0 0 6px">{promise}</p><ul style="margin:0 0 0 18px">{lis}</ul></div>
'''


def concept_map(aria, cols, edges, here, links_html, h=230):
    """Beginner/Intermediate/Advanced columns of concept nodes with dependency arrows.
    cols: [[(id, label, sub, href or None)], ...] for B, I, A. edges: [(from_id, to_id)]. here: set of ids taught in this lesson."""
    names = [('Beginner', 'green'), ('Intermediate', 'blue'), ('Advanced', 'violet')]
    pos, o = {}, ''
    for c, (nm, tone) in enumerate(names):
        x = 14 + c * 210
        o += box(x, 8, 196, h - 40, 'card', rx=8) + t(x + 98, 24, nm, 9, tone, bold=True)
        for r, (nid, lab, sub, href) in enumerate(cols[c]):
            y = 36 + r * 38
            node = opbox(x + 14, y, lab, sub, 'acc' if nid in here else tone, 168, 30)
            if href:
                node = f'<a href="{href}">{node}</a>'
            o += node; pos[nid] = (x + 14, y)
    for a, b in edges:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        if x2 > x1:
            o += arrow(x1 + 168, y1 + 15, x2, y2 + 15, 'ink3', 1)
        else:
            o += arrow(x1 + 84, y1 + 30, x2 + 84, y2, 'ink3', 1)
    return figure(aria, o + t(320, h - 18, 'Orange = this lesson · arrows = “you need this first” · click a box to jump', 8, 'ink2'), h=h) + f'  <p class="muted">{links_html}</p>\n'


def peel(title, intro, layers, notes, caps, hid):
    """Layer-by-layer dissection animation: frame k highlights layer k and shows its note."""
    fr = []
    n = len(layers)
    for k in range(n):
        o = t(180, 14, 'Peel it layer by layer', 9, bold=True)
        for i, (nm, sub) in enumerate(layers):
            y = 24 + i * 22
            tone = 'acc' if i == k else ('green' if i < k else 'card')
            o += box(16, y, 150, 19, tone, rx=3) + t(24, y + 13, f'{i + 1}. {nm}', 7.6, 'ink', anchor='start', bold=True)
        o += chip(134, 26 + k * 22, 'event', 'acc', w=30, h=14, size=6.6) + (arrow(149, 26 + k * 22 - 8, 149, 26 + k * 22, 'acc', 1) if k else '')
        o += box(176, 24, 168, n * 22 - 3, 'card', rx=6)
        for j, ln in enumerate(notes[k]):
            o += t(184, 40 + j * 13, ln, 7.4, 'ink' if j == 0 else 'ink2', anchor='start', bold=(j == 0))
        fr.append(o)
    return anim_one('Layer by layer', title, intro, 'Layers', 'Each layer of the system, from your code down to the disk', fr, caps, hid=hid)


def why_how_where(why, how, where, when):
    return cards([('Why', why, 'the problem it solves'), ('How', how, 'the mechanism'),
                  ('Where', where, 'in real systems'), ('When not', when, 'know the limits')])


# ---- Original icon set (simple line icons, 24x24 units, scaled by s)
def icon(name, x, y, s=1.0, color='ink'):
    st = f'fill="none" stroke="var(--{"ink" if color == "ink" else color})" stroke-width="{1.6 / s:.2f}" stroke-linecap="round" stroke-linejoin="round"'
    P = {
        'cart': '<path d="M2 3h3l2.5 11h11l2-8H6.2"/><circle cx="9" cy="19" r="1.6"/><circle cx="17" cy="19" r="1.6"/>',
        'card': '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
        'phone': '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4"/>',
        'sensor': '<path d="M10 14V4a2 2 0 0 1 4 0v10a4 4 0 1 1-4 0z"/><path d="M12 9v7"/>',
        'chart': '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 16v-4M12 16V8M17 16v-6"/>',
        'bell': '<path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4z"/><path d="M10 21h4"/>',
        'chef': '<path d="M7 13a4 4 0 1 1 2-7.5A4 4 0 0 1 15 5.5 4 4 0 1 1 17 13v6H7z"/><path d="M7 16h10"/>',
        'sms': '<path d="M4 4h16v12H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
        'scooter': '<circle cx="5" cy="17" r="3"/><circle cx="19" cy="17" r="3"/><path d="M8 17h8l2-7h-4M14 6h3"/>',
        'gear': '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1 7 17M17 7l2.1-2.1"/>',
        'disk': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    }
    return f'<g transform="translate({x} {y}) scale({s})" {st}>{P[name]}</g>'


def myths(rows):
    """Myth vs reality, each with proof from our lab. rows: [(myth, reality, proof)]."""
    items = ''.join(f'<li><b>Myth:</b> {m}<br><b>Reality:</b> {r}<br><span class="muted">Proof: {p}</span></li>' for m, r, p in rows)
    return f'''<div class="callout callout--warn" style="display:block"><p style="margin:0 0 6px"><b>Myth vs reality: things many websites still say</b></p><ul style="margin:0 0 0 18px">{items}</ul></div>
'''


def offset_ruler(aria, n_total=10, log_start=0, committed=6, label='partition 0 of orders'):
    cw, x0, y = 50, 40, 70
    o = t(20, 22, label, 8.6, 'ink', anchor='start', bold=True)
    for k in range(n_total):
        tone = 'green' if k < committed else 'amber'
        o += box(x0 + k * (cw + 2), y, cw, 28, tone, rx=3) + t(x0 + k * (cw + 2) + cw / 2, y + 18, str(k), 9, 'ink', bold=True, mono=True)
    o += box(x0 + n_total * (cw + 2), y, cw, 28, 'card', rx=3) + t(x0 + n_total * (cw + 2) + cw / 2, y + 18, '…', 9, 'ink2')
    def mark(k, txt, sub, color, up=True):
        xx = x0 + k * (cw + 2) - 1
        yy1, yy2 = (y - 26, y - 2) if up else (y + 30, y + 54)
        return (arrow(xx, yy1, xx, yy2, color, 1.4) if up else arrow(xx, yy2, xx, yy1, color, 1.4)) + \
               t(xx, yy1 - 12 if up else yy2 + 12, txt, 8, color, bold=True) + t(xx, yy1 - 2 if up else yy2 + 22, sub, 7.2, 'ink2')
    o += mark(log_start, 'log start', 'oldest kept', 'blue') + mark(committed, 'committed', 'group’s bookmark', 'green') + mark(n_total, 'log end', 'next write', 'red')
    o += box(x0 + committed * (cw + 2), y + 34, (n_total - committed) * (cw + 2) - 2, 14, 'amber', rx=3) + t(x0 + committed * (cw + 2) + (n_total - committed) * (cw + 2) / 2, y + 44, f'LAG = {n_total} − {committed} = {n_total - committed}', 7.6, 'ink', bold=True)
    o += arrow(40, 150, 600, 150, 'ink3', 2) + t(40, 166, 'old', 8, 'ink2', anchor='start') + t(600, 166, 'new → producers append here', 8, 'ink2', anchor='end')
    o += t(320, 190, 'Retention deletes from the left (log start moves right); producers add on the right; each group keeps its own committed offset.', 8, 'ink2')
    return figure(aria, o, h=214)


def big_picture(caption='The whole of Kafka on one page (our lab cluster).'):
    """Producers (icons) → KRaft cluster (3 brokers, leaders orange) → consumer groups (icons), with benefits and practices."""
    o = t(80, 20, 'PRODUCERS', 9, 'acc', bold=True) + t(320, 20, 'KAFKA CLUSTER (KRaft, no ZooKeeper)', 9, 'acc', bold=True) + t(560, 20, 'CONSUMER GROUPS', 9, 'acc', bold=True)
    prods = [('cart', 'Order app', 'order-events'), ('card', 'UPI payments', 'payments'), ('scooter', 'Rider GPS', 'rider-location'), ('sensor', 'Kitchen sensors', 'temperature')]
    for k, (ic, nm, tp) in enumerate(prods):
        y = 34 + k * 46
        o += box(14, y, 132, 38, 'card', rx=6) + icon(ic, 22, y + 7, 1.0) + t(54, y + 17, nm, 8, 'ink', anchor='start', bold=True) + t(54, y + 30, '→ ' + tp, 7, 'ink2', anchor='start', mono=True)
        o += arrow(146, y + 19, 178, 110, 'acc', 1)
    o += box(178, 30, 284, 186, 'card', rx=10)
    o += ''.join(box(190 + k * 60, 38, 50, 16, 'violet', rx=8) + t(215 + k * 60, 49, f'ctrl {k + 1}', 6.8, 'ink', bold=True) for k in range(3)) + t(380, 49, 'controller quorum', 7, 'ink2')
    lay = {1: ['P2*', 'P0', 'P1'], 2: ['P0*', 'P1', 'P2'], 3: ['P1*', 'P0', 'P2']}
    for b in (1, 2, 3):
        x = 188 + (b - 1) * 92
        o += box(x, 62, 84, 108, 'blue', rx=8) + t(x + 42, 76, f'Broker {b}', 8, bold=True) + icon('disk', x + 6, 66, 0.55)
        for r, p in enumerate(lay[b]):
            lead = p.endswith('*')
            o += box(x + 8, 84 + r * 26, 68, 20, 'acc' if lead else 'card', rx=3) + t(x + 42, 98 + r * 26, p.rstrip('*') + (' leader' if lead else ' copy'), 7, 'ink', mono=True)
    o += t(320, 186, 'topic = P0 + P1 + P2 · each partition: 1 leader + 2 copies', 7.6, 'ink2') + t(320, 204, 'offsets 0,1,2… per partition · data kept 7 days', 7.6, 'ink2')
    cons = [('chef', 'kitchen', 'reads all orders'), ('sms', 'sms', 'reads all orders'), ('chart', 'analytics', 'replays history'), ('bell', 'fraud-check', 'reads payments')]
    for k, (ic, nm, d) in enumerate(cons):
        y = 34 + k * 46
        o += arrow(462, 110, 494, y + 19, 'green', 1) + box(494, y, 132, 38, 'card', rx=6) + icon(ic, 502, y + 7, 1.0) + t(534, y + 17, nm, 8, 'ink', anchor='start', bold=True) + t(534, y + 30, d, 7, 'ink2', anchor='start')
    o += t(160, 238, 'push (producers write) →', 7.6, 'ink2') + t(480, 238, '← pull (consumers fetch at their pace)', 7.6, 'ink2')
    o += box(14, 250, 300, 64, 'soft-green' if False else 'green', rx=8) + t(24, 266, 'KEY BENEFITS', 8.4, 'ink', anchor='start', bold=True)
    o += ''.join(t(24 + (k % 2) * 146, 282 + (k // 2) * 15, '✓ ' + s, 7.6, 'ink', anchor='start') for k, s in enumerate(['High throughput', 'Loose coupling', 'Scale by partitions', 'Replay from history']))
    o += box(326, 250, 300, 64, 'amber', rx=8) + t(336, 266, 'BEST PRACTICES (lesson)', 8.4, 'ink', anchor='start', bold=True)
    o += ''.join(t(336 + (k % 2) * 150, 282 + (k // 2) * 15, s, 7.6, 'ink', anchor='start') for k, s in enumerate(['RF 3, acks=all (2.4)', 'Good keys (1.4, 2.2)', 'Watch consumer lag (3.3)', 'Retry + DLQ (6.2)']))
    return figure('The big picture of Kafka: four producers on the left (order app, UPI payments, rider GPS, kitchen sensors) push events into a KRaft cluster of three brokers, where each partition has one leader and two copies; four consumer groups on the right (kitchen, SMS, analytics, fraud check) pull events at their own pace. Below: key benefits and best practices with lesson numbers.', o, h=340, caption=caption)


def zoom_layers():
    """Cluster → broker → partition → segment file, with real lab numbers."""
    o = ''
    lv = [('1 · Cluster', ['3 brokers + 3 controllers', 'cluster.id TiffinGoKafkaLab0001A', 'leader of metadata: node 3']),
          ('2 · Broker 1', ['/var/lib/kafka/data', '117 folders', 'one per partition copy']),
          ('3 · Partition orders-0', ['offsets 0, 1, 2', 'Pune, Delhi, Pune', 'append-only']),
          ('4 · Segment files', ['00…0.log  157 bytes', '00…0.index  (10 MB pre-sized)', '00…0.timeindex'])]
    for k, (ttl, lines) in enumerate(lv):
        x = 14 + k * 156
        o += box(x, 34, 144, 112, ['blue', 'green', 'amber', 'violet'][k], rx=8) + t(x + 72, 52, ttl, 8.6, bold=True)
        o += ''.join(t(x + 8, 72 + j * 16, s, 7.2, 'ink2', anchor='start', mono=j > 0 or k > 0) for j, s in enumerate(lines))
        if k < 3:
            o += arrow(x + 144, 90, x + 156, 90, 'acc', 1.6)
    o += t(320, 22, 'Zoom in: from the whole cluster down to one file on disk', 9, bold=True)
    o += ''.join(t(14 + k * 156 + 72, 166, s, 7.8, 'acc', bold=True) for k, s in enumerate(['why: survive failures', 'why: spread storage', 'why: order + parallelism', 'why: fast sequential IO']))
    return figure('Four zoom levels with real lab values: the cluster with three brokers and controllers; broker 1 with 117 folders; partition orders-0 holding offsets 0 to 2; and the segment files .log of 157 bytes, .index and .timeindex.', o, h=196, caption='Every number is from our lab cluster.')


# ---- Shorter lesson assembly (Module 2+)
def five(kind, title, sub, cons, lines, caps, hid):
    fr = [t(180, 22, a, 9.4, 'acc' if i == 4 else 'ink', bold=True) + t(180, 56, b, 8.4, 'ink2') + cap(c, '', tone, y=150, h=34) for i, (a, b, c, tone) in enumerate(lines)]
    return anim_one(kind, title, sub, cons[0], cons[1], fr, caps, hid=hid)


def uc_(word, sub, tone, title, desc, flow_):
    return usecase(f'<rect x="16" y="22" width="88" height="46" rx="6" class="s-soft-{tone}" style="stroke:var(--{tone if tone != "acc" else "track"})"/>' + t(60, 42, word, 11, tone, bold=True) + t(60, 58, sub, 7.4, 'ink2'), title, desc, flow_)


def tipbox(html):
    return f'<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p>{html}</p></div>\n'


def assemble(here, *, h2_story, hook_html, narration, scene_svg, dialogue, def_h2, formal, simple, term_rows, whw, cmap, extra_def, lv, myth_rows, exam,
             types_h2, types_html, warn, steps_h2, steps_intro, steps, two, peel_intro, peel_html, scen_intro, scen, uc_h2, ucs, uc_note, pre):
    story = f'''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>{h2_story}</h2>
  <div class="story">
{hook_html}
    <p class="narration">{narration}</p>

{scene_svg}

{dialogue}
  </div>
</section>
'''
    definition = f'''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>{def_h2}</h2>
''' + def_block(formal, simple) + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms(term_rows) + '''

  <h3>Why, how, where</h3>
''' + whw + '''

  <h3>Concept map: what depends on what</h3>
''' + cmap + extra_def + lv + myths(myth_rows) + f'''
EXAM> {exam}
</section>
'''
    types = f'''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>{types_h2}</h2>
''' + types_html + f'''
WARN> {warn}
</section>
'''
    st = f'''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>{steps_h2}</h2>
  <p>{steps_intro}</p>
''' + stepper(steps) + '''
</section>
'''
    anim = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Two views of the same run</h2>
  <p>Left: real lab output. Right: what happens inside.</p>
''' + two + f'''
  <p>{peel_intro}</p>
''' + peel_html + f'''
  <p>{scen_intro}</p>
''' + scen + '''
</section>
'''
    uc = f'''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>{uc_h2}</h2>
''' + '\n'.join(ucs) + f'''
  <p class="muted">{uc_note}</p>
</section>
'''
    body_ = story.replace('  <div class="story">', tipbox(pre) + '  <div class="story">', 1) + definition + types + '\n<div class="ad-slot" data-slot="mid"></div>\n\n' + st + anim + uc
    open(os.path.join(here, 'body.html'), 'w', encoding='utf-8').write(body_)
    print('body.html', len(body_) // 1024, 'KB')


# ===================================================================== cloud-course additions
WARN_I = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18v.5"/></svg>'
EXAM_I = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19V5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2zm0 0a2 2 0 0 1 2-2h12"/></svg>'
AD = '\n<div class="ad-slot" data-slot="mid"></div>\n'
TIP_ICON_ = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>'


def small(aria, content, h=240, caption=''):
    """A phone-friendly figure (360 x h)."""
    cap_ = f'<text x="180" y="{h - 8}" text-anchor="middle" font-size="8" class="s-ink2">{caption}</text>' if caption else ''
    return f'''    <div class="scene">
      <svg viewBox="0 0 360 {h}" role="img" aria-label="{aria}">
        {content}
        {cap_}
        <text x="354" y="{h - 1}" text-anchor="end" class="s-wm">myphatshala.in</text>
      </svg>
    </div>'''


def mindmap(aria, center, branches, h=270, caption=''):
    """Radial-ish mind map: center label, up to 6 branches [(label, tone, [leaf, leaf])]. Left/right columns."""
    cx, cy = 180, (h - 16) / 2
    o = box(cx - 50, cy - 16, 100, 32, 'acc', rx=16) + t(cx, cy + 4, center, 9, 'ink', bold=True)
    left, right = branches[0::2], branches[1::2]
    for side, items in ((-1, left), (1, right)):
        n = len(items); gap = (h - 30) / max(n, 1)
        for i, (lab, tone, leaves) in enumerate(items):
            by = 14 + gap * i + gap / 2
            bx = cx + side * 64 if side > 0 else cx - 64 - 104
            ex = bx if side > 0 else bx + 104
            o += f'<path d="M{cx + side * 50},{cy} C{cx + side * 58},{cy} {ex - side * 8},{by} {ex},{by}" fill="none" stroke="currentColor" class="s-ink2" stroke-width="1.2" opacity=".55"/>'
            lh = 16 + 11 * len(leaves)
            o += box(bx, by - 9, 104, lh, tone, rx=7) + t(bx + 52, by + 3, lab, 8.2, 'ink', bold=True)
            for k, lf in enumerate(leaves):
                o += t(bx + 52, by + 15 + k * 11, lf, 6.8, 'ink2')
    return small(aria, o, h, caption)


def layers(aria, items, hl=None, h=None, caption='', side_note=None):
    """Stacked layers from top to bottom: items [(label, sub, tone)]; hl = index to highlight."""
    n = len(items); hh = 30; h = h or 26 + n * (hh + 6) + (14 if caption else 0)
    o = ''
    for i, (lab, sub, tone) in enumerate(items):
        y = 10 + i * (hh + 6); w = 300 - i * 0; x = 30
        o += box(x, y, w, hh, 'amber' if hl == i else tone, rx=6, sw=2.4 if hl == i else None)
        o += t(x + 12, y + 13, lab, 8.6, 'ink', anchor='start', bold=True) + t(x + 12, y + 24, sub, 7, 'ink2', anchor='start')
    if side_note:
        o += t(348, 20, side_note, 7, 'ink2', anchor='end')
    return small(aria, o, h, caption)


def cloud3(rows, minw=520):
    """Same idea in AWS / Azure / Google Cloud. rows: [(concept, aws, azure, gcp)]."""
    return table(['Concept', 'AWS', 'Microsoft Azure', 'Google Cloud'], rows, minw=minw)


def vendor_tabs(aws, azure, gcp, heading='Same idea in AWS, Azure and Google Cloud'):
    bar = ''.join(f'<button type="button" data-mod="{k}">{n}</button>' for k, n in [('aws', 'AWS'), ('az', 'Azure'), ('gcp', 'Google Cloud')])
    pan = ''.join(f'<div class="modlab__panel" data-mod="{k}">{v}</div>' for k, v in [('aws', aws), ('az', azure), ('gcp', gcp)])
    return f'  <h3>{heading}</h3>\n  <div class="modlab"><div class="modlab__bar"><b>Pick a cloud.</b>{bar}</div>{pan}</div>\n'


def caution(html):
    return f'<div class="callout callout--warn">{WARN_I}<p><b>Caution:</b> {html}</p></div>'


def mistakes(rows):
    """rows: [(mistake/symptom, why it happens, how to fix)]"""
    return table(['Mistake or symptom', 'Why it happens', 'How to fix or avoid'], rows, minw=560)


def certbox(rows, qs=()):
    """rows: [(exam, domain/objective, what to know)]; qs: [(question, answer)] sample exam-style questions."""
    o = table(['Exam', 'Domain', 'What you must know from this lesson'], rows, minw=560)
    if qs:
        o += '\n  <h3>Try exam-style questions</h3>\n' + ''.join(f'  <details class="faq"><summary>{q}</summary><p>{a}</p></details>\n' for q, a in qs)
    return o


def practical(intro, steps, cleanup=None):
    """steps: [(title, html, behind)] → stepper; optional cleanup html."""
    o = f'  <p>{intro}</p>\n' + stepper(steps)
    if cleanup:
        o += f'\n  <h3>Clean up and cost check</h3>\n  <p>{cleanup}</p>'
    return o


def miniproject(title, goal, steps, result, combines):
    li = ''.join(f'<li>{s}</li>' for s in steps)
    return (f'  <h3>{title}</h3>\n  <p><b>Goal:</b> {goal}</p>\n  <p class="muted"><b>Combines:</b> {combines}</p>\n'
            f'  <ol class="steps-list">{li}</ol>\n  <p><b>You should see:</b> {result}</p>')


def section(sid, num, label, h2, inner):
    return f'''<section class="part" id="{sid}">
  <span class="part-label"><b>{num}</b> {label}</span>
  <h2>{h2}</h2>
{inner}
</section>
'''


def interview_box(lines):
    li = ''.join(f'<li>{x}</li>' for x in lines)
    return f'  <h3>Say it in an interview</h3>\n  <div class="callout callout--exam">{EXAM_I}<div><p><b>30-second answer you can speak:</b></p><ul>{li}</ul></div></div>\n'


def assemble_cloud(here, *, clouds_html, practical_html, mistakes_html, cert_html, project_html='', mindmap_html='', interview=(), **kw):
    """Standard assemble() parts 1-6, then 7 Cloud by cloud, 8 Hands-on, 9 Mistakes, 10 Certification, 11 Mini project."""
    assemble(here, **kw)
    p = os.path.join(here, 'body.html')
    b = open(p, encoding='utf-8').read()
    if interview:
        b = b.replace('  <h3>Words you’ll meet in this lesson</h3>', interview_box(interview) + '\n  <h3>Words you’ll meet in this lesson</h3>', 1)
    if mindmap_html:   # lesson mind map right after the definition's concept map heading block
        b = b.replace('  <h3>Concept map: what depends on what</h3>', '  <h3>Mind map of this lesson</h3>\n' + mindmap_html + '\n  <h3>Concept map: what depends on what</h3>', 1)
    extra = AD + section('clouds', 7, 'AWS · Azure · Google Cloud', 'The same idea in three clouds', clouds_html)
    extra += section('practical', 8, 'Hands-on', 'Do it yourself, step by step', practical_html)
    extra += AD + section('mistakes', 9, 'Mistakes to avoid', 'Common mistakes, why they happen, how to fix them', mistakes_html)
    extra += section('certification', 10, 'Certification corner', 'What the exams ask from this lesson', cert_html)
    if project_html:
        extra += AD + section('project', 11, 'Mini project', 'Build something small with what you learned', project_html)
    open(p, 'w', encoding='utf-8').write(b + extra)
    print('body.html +cloud parts', len(b + extra) // 1024, 'KB')


def scene(aria, content, caption, h=170):
    """Phone-friendly hero scene (360 wide) for cloud lessons (overrides svgkit.scene).
    The caption gets its own 16px band below the content, so it never overlaps the picture."""
    h = h + 16
    return f'''    <div class="scene">
      <svg viewBox="0 0 360 {h}" role="img" aria-label="{E(aria)}">
        {content}
        <text x="180" y="{h - 12}" text-anchor="middle" font-size="8.4" class="s-ink2">{caption}</text>
        <text x="354" y="{h - 2}" text-anchor="end" class="s-wm">myphatshala.in</text>
      </svg>
    </div>'''


# ===================================================================== v2: real diagrams + step flows
def ic(kind, x, y, s=1.0, tone='ink'):
    """Small line icons (24x24 box at x,y scaled by s)."""
    P = {
        'phone': '<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M10 18h4"/>',
        'laptop': '<rect x="4" y="5" width="16" height="11" rx="1"/><path d="M2 19h20"/>',
        'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-5 5-7 8-7s7 2 8 7"/>',
        'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
        'dns': '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9h10M7 13h6M7 17h8"/>',
        'lb': '<circle cx="12" cy="5" r="2.5"/><path d="M12 8v4M12 12l-7 6M12 12l7 6M12 12v6"/><circle cx="5" cy="19" r="2"/><circle cx="12" cy="19" r="2"/><circle cx="19" cy="19" r="2"/>',
        'server': '<rect x="4" y="3" width="16" height="7" rx="1.5"/><rect x="4" y="14" width="16" height="7" rx="1.5"/><path d="M8 6.5h.01M8 17.5h.01"/>',
        'db': '<ellipse cx="12" cy="5" rx="7" ry="3"/><path d="M5 5v14c0 1.7 3 3 7 3s7-1.3 7-3V5M5 12c0 1.7 3 3 7 3s7-1.3 7-3"/>',
        'disk': '<rect x="3" y="6" width="18" height="12" rx="2"/><circle cx="16" cy="12" r="2"/>',
        'meter': '<circle cx="12" cy="13" r="8"/><path d="M12 13l4-4M8 5l1 2M16 5l-1 2"/>',
        'shield': '<path d="M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z"/>',
        'gear': '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M5 19l2-2M17 7l2-2"/>',
        'cloud': '<path d="M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 9a4.5 4.5 0 0 0 1 9z"/>',
        'chip': '<rect x="6" y="6" width="12" height="12" rx="1"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
        'app': '<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>',
        'chart': '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    }
    col = {'ink': 'currentColor'}.get(tone, FILL.get(tone, tone))
    return f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{col};stroke-width:{1.8 / s:.2f};stroke-linecap:round;stroke-linejoin:round" class="s-ink">{P.get(kind) or AWS_ICONS[kind]}</g>'


def node_box(x, y, w, h, icon, label, sub='', tone='card', on=True, hot=False):
    op = '' if on else ' opacity=".28"'
    o = f'<g{op}>' + box(x, y, w, h, 'amber' if hot else tone, rx=7, sw=2.6 if hot else None)
    o += ic(icon, x + w / 2 - 9, y + 5, 0.75, 'acc' if hot else 'ink')
    o += t(x + w / 2, y + 34, label, 7.6, 'ink', bold=True)
    if sub:
        o += t(x + w / 2, y + 43, sub, 6.4, 'ink2')
    return o + '</g>'


def packet(x1, y1, x2, y2, label='', color='#E0A100', dur=1.4):
    path = f'M{x1},{y1} L{x2},{y2}'
    o = f'<path d="{path}" style="fill:none;stroke:{color};stroke-width:2.4;stroke-dasharray:5 3"/>'
    o += f'<circle r="5" style="fill:{color}"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}"/></circle>'
    if label:
        o += f'<g><rect x="{(x1 + x2) / 2 - 26}" y="{(y1 + y2) / 2 - 17}" width="52" height="12" rx="6" style="fill:{color}"/>' + t((x1 + x2) / 2, (y1 + y2) / 2 - 8, label, 6.6, extra=' style="fill:#fff"', bold=True) + '</g>'
    return o


def flow_anim(title, intro, panel, aria, nodes, steps, static='', hid=None):
    """Step-by-step working animation.
    nodes: {id: (x, y, w, h, icon, label, sub)} drawn every frame (dim unless active).
    steps: [dict(on=[ids], hot=id, move=(x1,y1,x2,y2,label) or None, head='Step 1 · …', text='what happens', svc='AWS … · Azure … · GCP …', extra=svg)]"""
    frames, caps = [], []
    for k, s in enumerate(steps):
        o = static
        for nid, (x, y, w, h, icn, lab, sub) in nodes.items():
            o += node_box(x, y, w, h, icn, lab, sub, on=(nid in s['on'] or not s['on']), hot=(nid == s.get('hot')))
        if s.get('move'):
            x1, y1, x2, y2, lab = s['move']
            o += packet(x1, y1, x2, y2, lab)
        o += s.get('extra', '')
        # caption strip (3 lines)
        o += box(6, 160, 348, 60, 'blue', rx=8)
        o += t(14, 175, s['head'], 8.6, 'ink', anchor='start', bold=True)
        o += t(14, 189, s['text'], 7.4, 'ink', anchor='start')
        if s.get('text2'):
            o += t(14, 200, s['text2'], 7.4, 'ink', anchor='start')
        o += t(14, 213, s.get('svc', ''), 6.8, 'ink2', anchor='start')
        frames.append(o); caps.append(s['head'].split('·', 1)[-1].strip() + '.')
    return anim_one('How it works', title, intro, panel, aria, frames, caps, delay=6000, hid=hid)


def bigfig(aria, content, h=320, caption=''):
    """A large explanatory diagram (640 wide), like a textbook figure."""
    f = figure(aria, content, h=h, caption=caption)
    return f.replace('<div class="scene">', '<div class="scene" style="overflow-x:auto">', 1).replace('<svg viewBox', '<svg style="min-width:600px" viewBox', 1)


def icon_cards(rows):
    """rows: [(icon, title, text, example)] → card grid with an inline SVG icon each."""
    out = '<div class="cards">'
    for icn, ti, tx, ex in rows:
        svg = f'<svg viewBox="0 0 24 24" width="30" height="30" style="display:block;margin-bottom:6px">{ic(icn, 0, 0, 1, "acc")}</svg>'
        out += f'<div class="card">{svg}<h4>{ti}</h4><p>{tx}</p><span class="tag">{ex}</span></div>'
    return out + '</div>'


def assemble_v2(here, *, story_h2, hook_html, narration, scene_svg, dialogue, def_h2, formal, simple, interview, terms_rows,
                picture_h2, picture_html, how_h2, how_intro, how_anim, how_after='', parts_h2, parts_html, lv='', myth_rows=(), exam='',
                clouds_html='', proof_h2='', proof_intro='', proof_steps=(), practical_html='', mistakes_html='', cert_html='', project_html='', pre='', extra_secs=(), can_now=(), next_html='', after_picture=()):
    """Cloud lesson v2: one clear thread — story → definition → THE picture → how it works step by step → parts → clouds → real proof → hands-on → mistakes → exam → project."""
    n = [0]
    def sec(sid, label, h2, inner):
        n[0] += 1
        return f'<section class="part" id="{sid}">\n  <span class="part-label"><b>{n[0]}</b> {label}</span>\n  <h2>{h2}</h2>\n{inner}\n</section>\n'
    story = sec('story', 'The story', story_h2, (tipbox(pre) if pre else '') + f'  <div class="story">\n{hook_html}\n    <p class="narration">{narration}</p>\n{scene_svg}\n{dialogue}\n  </div>')
    d = def_block(formal, simple) + interview_box(interview) + '\n  <h3>Words you’ll meet</h3>\n' + terms(terms_rows)
    if exam:
        d += f'\nEXAM> {exam}\n'
    out = story + sec('definition', 'Definition', def_h2, d)
    out += sec('picture', 'The big picture', picture_h2, picture_html)
    for sid, label, h2, inner in after_picture:
        out += AD + sec(sid, label, h2, inner)
    out += AD
    out += sec('working', 'How it works, step by step', how_h2, f'  <p>{how_intro}</p>\n' + how_anim + how_after)
    out += sec('parts', 'Explained part by part', parts_h2, parts_html + lv + (myths(myth_rows) if myth_rows else ''))
    for sid, label, h2, inner in extra_secs:
        out += sec(sid, label, h2, inner)
    if clouds_html:
        out += sec('clouds', 'AWS · Azure · Google Cloud', 'The same idea in three clouds', clouds_html)
    if proof_steps:
        out += AD + sec('steps', 'Real proof', proof_h2, f'  <p>{proof_intro}</p>\n' + stepper(list(proof_steps)))
    if practical_html:
        out += sec('practical', 'Hands-on', 'Do it yourself, step by step', practical_html)
    if mistakes_html:
        out += AD + sec('mistakes', 'Mistakes to avoid', 'Common mistakes, why they happen, how to fix them', mistakes_html)
    if cert_html:
        out += sec('certification', 'Certification corner', 'What the exams ask from this lesson', cert_html)
    if project_html:
        out += AD + sec('project', 'Mini project', 'Build something with what you learned', project_html)
    if can_now or next_html:
        li = ''.join(f'<li>{x}</li>' for x in can_now)
        inner = (f'  <div class="callout callout--tip">{TIP_ICON_}<div><p><b>After this lesson you can:</b></p><ul>{li}</ul></div></div>\n' if can_now else '') + (f'  <p class="next-up"><b>Next:</b> {next_html}</p>\n' if next_html else '')
        out += sec('wrapup', 'Wrap-up', 'What you can do now', inner)
    open(os.path.join(here, 'body.html'), 'w', encoding='utf-8').write(out)
    print('body.html v2', len(out) // 1024, 'KB')


def pic_cards(rows, vb='0 0 300 150'):
    """rows: [(svg_inner, title, text, example)] — each card has its own illustration."""
    out = '<div class="pic-cards" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin:14px 0 22px">'
    for svg, ti, tx, ex in rows:
        out += (f'<div class="card" style="padding:12px"><svg viewBox="{vb}" role="img" aria-label="{E(ti)}" style="width:100%;height:auto;display:block;border-radius:10px;background:var(--paper-2)">{svg}</svg>'
                f'<h4 style="margin:10px 0 4px">{ti}</h4><p style="margin:0 0 6px">{tx}</p><span class="tag">{ex}</span></div>')
    return out + '</div>'


def big_mindmap(aria, center, branches, h=360, caption=''):
    """Readable 640-wide mind map: center + up to 6 branches [(title, tone, icon, [leaves])], 3 left, 3 right."""
    cx, cy = 320, h / 2 - 8
    o = f'<ellipse cx="{cx}" cy="{cy}" rx="78" ry="30" class="s-soft-acc" style="stroke:var(--track);stroke-width:2"/>' + t(cx, cy + 5, center, 12, 'ink', bold=True)
    L, R = branches[:3], branches[3:]
    for side, items in ((-1, L), (1, R)):
        n = len(items); gap = (h - 40) / n
        for i, (ti, tn, icn, leaves) in enumerate(items):
            by = 20 + gap * i + gap / 2
            w = 190; bx = 20 if side < 0 else 640 - 20 - w
            ex = bx + w if side < 0 else bx
            o += f'<path d="M{cx + side * 78},{cy} C{cx + side * 120},{cy} {ex - side * 40},{by} {ex},{by}" style="fill:none;stroke:{FILL.get(tn, "var(--line)")};stroke-width:3;opacity:.7"/>'
            lh = 30 + 13 * len(leaves)
            o += box(bx, by - 16, w, lh, tn, rx=10) + ic(icn, bx + 8, by - 11, 0.8, tn) + t(bx + 32, by + 1, ti, 10, 'ink', anchor='start', bold=True)
            for k, lf in enumerate(leaves):
                o += t(bx + 14, by + 17 + k * 13, '• ' + lf, 8.4, 'ink2', anchor='start')
    return bigfig(aria, o, h=h, caption=caption)


def wwu(rows):
    """'What · Why · Use' cards. rows: [(title, what, why, use)]"""
    out = '<div class="wwu" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:14px;margin:14px 0 22px">'
    for ti, what, why, use in rows:
        out += ('<div class="card" style="padding:14px 16px">'
                f'<h4 style="margin:0 0 8px">{ti}</h4>'
                f'<p style="margin:0 0 6px"><b style="color:var(--blue)">What it is:</b> {what}</p>'
                f'<p style="margin:0 0 6px"><b style="color:var(--green)">Why it exists:</b> {why}</p>'
                f'<p style="margin:0"><b style="color:var(--track)">Where it is used:</b> {use}</p></div>')
    return out + '</div>'


def qx(qtext, opts, ans, why):
    """Explained exam question (details)."""
    li = ''.join(f'<li>{"<b>✔ " if i == ans else ""}{o}{"</b>" if i == ans else ""}</li>' for i, o in enumerate(opts))
    return f'  <details class="faq"><summary>{qtext}</summary><ol type="a">{li}</ol><p><b>Why:</b> {why}</p></details>\n'


def cap_frames(frames_svg, steps):
    """frames_svg: list of svg; steps: [(head, line1, line2)] → frames with caption strip."""
    return [f + box(6, 158, 348, 62, 'blue', rx=8) + t(14, 174, h, 9, 'ink', anchor='start', bold=True) + t(14, 190, a, 7.4, 'ink', anchor='start') + t(14, 206, b, 7.2, 'ink2', anchor='start') for f, (h, a, b) in zip(frames_svg, steps)]


def vtype(num, name, tone, definition, analogy, scenario, examples, fig, anim, use_when, avoid_when, deep='', how=(), diff='', where=(), realworld='', plain='', pro='', words=()):
    """One 'type' block. Order: definition → analogy → how it works internally (text steps) → figure + animation →
    how it differs from similar types → where used · real-world example · real scenario · products → use/avoid → deeper."""
    col = {'blue': 'var(--blue)', 'green': 'var(--green)', 'amber': 'var(--track)', 'violet': 'var(--blue)', 'red': 'var(--track)'}.get(tone, 'var(--blue)')
    card = lambda h, body: f'<div class="card" style="padding:12px 14px"><h4 style="margin:0 0 6px">{h}</h4>{body}</div>'
    grid = lambda inner: f'  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;margin:0 0 14px">{inner}</div>\n'
    o = f'  <h3 id="type{num}" style="margin-top:38px">Type {num} · {name}</h3>\n'
    o += (f'  <div style="border-left:5px solid {col};padding:12px 16px;margin:10px 0 12px;border-radius:6px;background:color-mix(in srgb, {col} 9%, transparent)">'
          f'<p style="margin:0"><b>Definition (say it in an interview):</b> {definition}</p></div>\n')
    if plain:
        o += f'  <div class="card" style="padding:12px 16px;margin:0 0 12px"><p style="margin:0;font-size:1.06rem;line-height:1.6"><b>In plain words (no jargon):</b> {plain}</p></div>\n'
    o += f'  <p><b>Analogy:</b> {analogy}</p>\n'
    if how:
        li = ''.join(f'<li style="margin-bottom:6px"><b>{h}.</b> {tx}</li>' for h, tx in how)
        o += f'  <h4 style="margin:16px 0 6px">How it works internally, step by step</h4>\n  <ol>{li}</ol>\n'
    if words:
        wd = ' · '.join(f'<b>{a}</b> = {b}' for a, b in words)
        o += f'  <p style="font-size:.93em;padding:8px 12px;border-radius:6px;background:color-mix(in srgb, var(--green) 8%, transparent)"><b>Words used above, in simple terms:</b> {wd}</p>\n'
    if fig and anim:
        o += '  <p style="margin:4px 0 0"><b>See it:</b> the picture puts the analogy next to the real architecture; the animation plays the steps.</p>\n'
    elif fig or anim:
        o += '  <p style="margin:4px 0 0"><b>See it:</b> ' + ('the picture puts the analogy next to the real architecture.' if fig else 'the animation plays these steps one by one.') + '</p>\n'
    o += fig + anim
    if diff:
        o += '  <h4 style="margin:16px 0 6px">How it differs from similar types</h4>\n' + diff + '\n'
    wl = ''.join(f'<li>{w}</li>' for w in where)
    o += grid((card('Where it is used', f'<ul style="margin:0;padding-left:18px">{wl}</ul>') if where else '')
              + (card('Real-world example', f'<p style="margin:0">{realworld}</p>') if realworld else '')
              + card('Real scenario (TiffinGo)', f'<p style="margin:0">{scenario}</p>')
              + card('Products and cloud services', f'<p style="margin:0">{examples}</p>'))
    if pro:
        o += f'  <div style="border:1px dashed var(--track);border-radius:8px;padding:10px 14px;margin:0 0 12px"><p style="margin:0"><b>For the experienced — did you know?</b> {pro}</p></div>\n'
    o += (f'  <p><b style="color:var(--green)">Use it when:</b> {use_when}<br><b style="color:var(--track)">Avoid / be careful when:</b> {avoid_when}'
          + (f'<br><b>Go deeper:</b> {deep}' if deep else '') + '</p>\n')
    return o


def _ui_mark(s):
    """[[Button]] → styled UI element chip."""
    import re as _re
    return _re.sub(r'\[\[(.+?)\]\]', r'<span style="display:inline-block;padding:0 6px;border:1px solid var(--blue);border-radius:4px;font-weight:600;font-size:.92em;background:color-mix(in srgb, var(--blue) 10%, transparent)">\1</span>', s)


def uicli(ui, cli, ui_label='UI way — click by click', cli_label='CLI way — the same thing with commands', ui_note=''):
    """Two ways to do the same step: numbered click path (ui list, [[Button]] marks UI elements) + CLI code html."""
    li = ''.join(f'<li style="margin-bottom:4px">{_ui_mark(x)}</li>' for x in ui)
    left = (f'<div class="card" style="padding:10px 14px"><h4 style="margin:0 0 6px">{ui_label}</h4><ol style="margin:0;padding-left:20px">{li}</ol>'
            + (f'<p style="margin:6px 0 0;font-size:.92em">{ui_note}</p>' if ui_note else '') + '</div>')
    right = f'<div style="min-width:0"><h4 style="margin:0 0 6px">{cli_label}</h4>{cli}</div>'
    return f'<div style="display:grid;grid-template-columns:minmax(0,1fr);gap:12px">{left}{right}</div>'


def apanels(aria, title, ana_title, ana_svg, ana_cap, real_title, real_svg, note='', h=266):
    """Textbook figure: analogy picture (left, x 8-214) → real architecture (right, x 230-632). Content y 28-240."""
    o = t(320, 16, title, 11, 'ink', bold=True)
    o += box(8, 28, 206, 212, 'card', rx=10) + t(111, 44, 'Analogy: ' + ana_title, 8.2, 'ink', bold=True) + ana_svg
    for i, c in enumerate(ana_cap):
        o += t(111, 216 + i * 12, c, 6.9, 'ink2')
    o += arrow(216, 134, 228, 134)
    o += box(230, 28, 402, 212, 'card', rx=10) + t(431, 44, real_title, 8.2, 'ink', bold=True) + real_svg
    if note:
        o += t(320, 256, note, 7.4, 'ink2')
    return bigfig(aria, o, h=h)


def challenge(qs, where):
    li = ''.join(f'<li>{q}</li>' for q in qs)
    return (f'  <div style="border:1px dashed var(--track);border-radius:8px;padding:10px 14px;margin:12px 0"><p style="margin:0 0 4px"><b>Already know this topic? Try these before you read:</b></p>'
            f'<ol style="margin:0">{li}</ol><p style="margin:4px 0 0">Answers are in the <b>“For the experienced”</b> boxes of {where}.</p></div>\n')


def jump(names):
    return '  <p style="margin-top:6px"><b>Jump to:</b> ' + ' · '.join(f'<a href="#type{i}">{i} {n}</a>' for i, n in enumerate(names, 1)) + '</p>\n'


# ---------------------------------------------------------------- own-account practicals (Module 6+)
MOCKQ = []   # queue of (aws_mock, az_mock, gcp_mock) consumed by the next tri() calls
CONSOLES = {'aws': 'AWS Management Console', 'az': 'Azure portal', 'gcp': 'Google Cloud console'}
def tri(aws, az, gcp, heading='Pick your cloud'):
    """Same task on AWS / Azure / Google Cloud, each tab = UI way + CLI way + what you should see.
    each arg: (ui_list, cli_src, see_html)"""
    def pane(k, v):
        ui, cli, see = v[:3]
        mk = v[3] if len(v) > 3 else ''
        o = (mk if mk else '') + uicli(ui, code('bash', {'aws': 'AWS CloudShell or terminal', 'az': 'Azure Cloud Shell (Bash) or terminal', 'gcp': 'Cloud Shell or terminal'}[k], cli), ui_label='UI way — ' + CONSOLES[k])
        return o + (f'<p style="margin:10px 0 0"><b>You should see:</b> {see}</p>' if see else '')
    if MOCKQ:
        m = MOCKQ.pop(0)
        aws, az, gcp = [tuple(v[:3]) + (mm,) for v, mm in zip((aws, az, gcp), m)]
    bar = ''.join(f'<button type="button" data-mod="{k}">{n}</button>' for k, n in [('aws', 'AWS'), ('az', 'Azure'), ('gcp', 'Google Cloud')])
    pan = ''.join(f'<div class="modlab__panel" data-mod="{k}">{pane(k, v)}</div>' for k, v in [('aws', aws), ('az', az), ('gcp', gcp)])
    return f'<div class="modlab"><div class="modlab__bar"><b>{heading}.</b>{bar}</div>{pan}</div>'


OWN_INTRO = ('<b>These labs run on <u>your own</u> cloud account</b> — we cannot run them for you. Each step has three tabs (AWS, Azure, Google Cloud); '
             'pick the cloud you have and do both the <b>UI way</b> and the <b>CLI way</b>. Stay inside free tier / credit limits, use the India Region '
             '(AWS ap-south-1 Mumbai · Azure Central India · Google asia-south1 Mumbai), and always do the <b>Clean up</b> step at the end.')

SETUP_STEP = ('0 · Get ready: account, budget, CLI', tri(
    (['Create an AWS account (aws.amazon.com → [[Create an AWS Account]]); choose the [[Free plan]] while learning.',
      'Never work as root: [[IAM Identity Center]] (or [[IAM]]) → create an admin user with MFA and sign in as that user.',
      '[[Billing and Cost Management]] → [[Budgets]] → [[Create budget]] → monthly cost budget, e.g. $5, alert by e-mail (Lesson 5.5).',
      'Top-right Region menu → [[Asia Pacific (Mumbai)]]. Open [[CloudShell]] (terminal icon) — the AWS CLI is already signed in there.'],
     'aws sts get-caller-identity          # who am I? (must NOT be the root user)\naws configure set region ap-south-1\naws configure list',
     'your account ID and an IAM user/role ARN — not “root”.'),
    (['Create a free account at azure.microsoft.com/free (credit for the first 30 days).',
      'Search [[Cost Management]] → [[Budgets]] → [[Add]] → monthly budget, e.g. ₹400, alert at 80%.',
      'Open [[Cloud Shell]] (the >_ icon in the top bar) → choose [[Bash]]. The Azure CLI is already signed in.'],
     'az account show --output table        # subscription in use\naz account list-locations --query "[?name==\'centralindia\'].displayName" -o tsv',
     'your subscription name and state “Enabled”, then “Central India”.'),
    (['Sign in at console.cloud.google.com and start the free trial (credit for 90 days).',
      'Create a project: project picker → [[New project]] → name <code>tiffingo-lab</code>.',
      '[[Billing]] → [[Budgets & alerts]] → [[Create budget]] → e.g. ₹400, alerts at 50/90/100%.',
      'Click [[Activate Cloud Shell]] (>_ icon). The gcloud CLI is already signed in.'],
     'gcloud config set project tiffingo-lab      # use your real project ID\ngcloud config set compute/region asia-south1\ngcloud config list',
     'your account e-mail, the project and region asia-south1.')),
    'Cloud Shell is the easiest CLI: free, in the browser, already logged in. On your laptop install the AWS CLI v2, Azure CLI or Google Cloud CLI and run aws configure / az login / gcloud init.')


def mock(cloud, crumbs, nav, active, fields, button, extra=''):
    """Simplified console sketch (wireframe, no logos): breadcrumb, left nav, a form with fields, the primary button highlighted.
    fields: [(label, value)] ; value starting with '[x]' renders a ticked checkbox, '( )' a radio, '▾' a dropdown."""
    name = {'aws': 'AWS Management Console', 'az': 'Azure portal', 'gcp': 'Google Cloud console'}[cloud]
    navh = ''.join(f'<li style="padding:4px 8px;border-radius:4px;{"background:color-mix(in srgb,var(--blue) 18%,transparent);font-weight:700" if n == active else ""}">{n}</li>' for n in nav)
    def fld(l, v):
        if v.startswith('[x]'):
            ctl = f'<span style="display:inline-block;width:12px;height:12px;border:1.5px solid var(--blue);background:var(--blue);border-radius:2px;margin-right:6px;vertical-align:-1px"></span>{v[3:].strip()}'
        elif v.startswith('▾'):
            ctl = f'<span class="cm-in" style="display:inline-block;min-width:60%;padding:3px 8px;border:1px solid var(--line, #9aa);border-radius:4px">{v[1:].strip()} <span style="float:right">▾</span></span>'
        else:
            ctl = f'<span class="cm-in" style="display:inline-block;min-width:60%;padding:3px 8px;border:1px solid var(--line, #9aa);border-radius:4px;font-family:var(--mono, monospace)">{v}</span>'
        return f'<div style="margin:0 0 8px"><div style="font-size:.82em;font-weight:600;margin-bottom:2px">{l}</div>{ctl}</div>'
    form = ''.join(fld(l, v) for l, v in fields)
    return (f'<figure class="console-mock" style="margin:0 0 12px;border:1px solid var(--line, #bcc);border-radius:10px;overflow:hidden;font-size:.9rem">'
            f'<div style="display:flex;justify-content:space-between;gap:8px;padding:6px 12px;background:#2b2f36;color:#fff;font-size:.8rem"><b>{name}</b><span style="opacity:.75">simplified sketch</span></div>'
            f'<div style="padding:5px 12px;font-size:.78rem;border-bottom:1px solid var(--line, #ccd);opacity:.85">{" › ".join(crumbs)}</div>'
            f'<style>.cm-grid{{display:grid;grid-template-columns:minmax(0,150px) minmax(0,1fr)}}.cm-nav{{list-style:none;margin:0;padding:8px 6px;border-right:1px solid var(--line,#ccd);font-size:.8rem}}@media(max-width:600px){{.cm-grid{{grid-template-columns:minmax(0,1fr)}}.cm-nav{{display:flex;flex-wrap:wrap;gap:2px;border-right:0;border-bottom:1px solid var(--line,#ccd)}}.cm-in{{min-width:0!important;max-width:100%;overflow-wrap:anywhere}}}}</style>'
            f'<div class="cm-grid"><ul class="cm-nav">{navh}</ul>'
            f'<div style="padding:10px 14px;min-width:0">{form}{extra}'
            f'<div style="text-align:right;margin-top:6px"><span style="display:inline-block;padding:5px 14px;border-radius:6px;background:#E0A100;color:#111;font-weight:700;outline:3px solid color-mix(in srgb,#E0A100 40%,transparent)">{button}</span></div></div></div>'
            f'<figcaption style="padding:5px 12px;font-size:.75rem;opacity:.8;border-top:1px solid var(--line, #ccd)">A simplified sketch of the screen to help you find your way — labels match the real console, layout and colours do not.</figcaption></figure>')


# ---------------------------------------------------------------- AWS course: single-cloud practicals
MOCKA = []   # queue of single AWS console mocks consumed by the next aws1() calls (one per non-setup step)
def aws1(ui, cli, see, note=''):
    """One AWS step: console sketch (from MOCKA) + UI way + CLI way + what you should see."""
    mk_ = MOCKA.pop(0) if MOCKA else ''
    o = mk_ + uicli(ui, code('bash', 'AWS CloudShell or terminal', cli), ui_label='UI way — AWS Management Console')
    o += f'<p style="margin:10px 0 0"><b>You should see:</b> {see}</p>' if see else ''
    o += f'<p style="margin:6px 0 0;font-size:.95em">{note}</p>' if note else ''
    return o

AWS_INTRO = ('<b>These labs run on <u>your own</u> AWS account</b> — we cannot run them for you. Every step shows the <b>UI way</b> (console clicks) and the <b>CLI way</b> '
             '(commands for AWS CloudShell or your terminal), plus what you should see. Work as an IAM/Identity Center user, never root; use the Mumbai Region '
             '(<code>ap-south-1</code>); stay inside Free Tier/credits; and always do the <b>Clean up</b> step at the end.')



def astep(title, ui, cli, see, behind=''):
    """Practical step tuple for practical(): (title, html, behind)."""
    return (title, aws1(ui, cli, see), behind)


AWS_SETUP = astep('0 · Get ready: signed in, budget, Region, CloudShell',
    ['Sign in as your admin <b>user</b> (not root) — Lesson 1.2 shows how to create it.',
     '[[Billing and Cost Management]] → [[Budgets]] → check a monthly cost budget with e-mail alerts exists (e.g. $5).',
     'Top-right Region menu → [[Asia Pacific (Mumbai)]].',
     'Click the [[CloudShell]] icon (>_) in the top bar — the AWS CLI is already signed in there.'],
    'aws sts get-caller-identity --query Arn --output text   # must NOT end in :root\naws configure set region ap-south-1\naws configure list | grep region',
    'an ARN ending in <code>:user/…</code> or <code>:assumed-role/…</code> and region <code>ap-south-1</code>.',
    'CloudShell is free, runs in your browser and is already signed in as the user you logged in with.')


# ---------------------------------------------------------------- AWS-style architecture diagrams + lab simulator
AWS_ICONS = {
    'bucket': '<path d="M4 6h16l-2 14H6z"/><ellipse cx="12" cy="6" rx="8" ry="2.5"/>',
    'folder': '<path d="M3 7h6l2 2h10v10H3z"/>',
    'file': '<path d="M6 2h8l4 4v16H6z"/><path d="M14 2v4h4"/>',
    'key': '<circle cx="8" cy="12" r="4"/><path d="M12 12h9M18 12v3M21 12v2"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'role': '<rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="12" cy="10" r="3"/><path d="M7 18c1-3 3-4 5-4s4 1 5 4"/>',
    'git': '<circle cx="6" cy="6" r="2"/><circle cx="6" cy="18" r="2"/><circle cx="18" cy="12" r="2"/><path d="M6 8v8M8 6c6 0 8 2 8 6"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 3"/>',
    'fw': '<rect x="3" y="4" width="18" height="16" rx="1"/><path d="M3 9h18M3 14h18M9 4v5M15 9v5M9 14v6"/>',
    'ip': '<circle cx="12" cy="10" r="6"/><path d="M12 16v6M9 10h6"/>',
    'mail': '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="M3 6l9 7 9-7"/>',
    'list': '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
}
def ai(kind, x, y, s=1.0, tone='ink'):
    if kind not in AWS_ICONS:
        return ic(kind, x, y, s, tone)
    col = {'ink': 'currentColor'}.get(tone, FILL.get(tone, tone))
    return f'<g transform="translate({x},{y}) scale({s})" style="fill:none;stroke:{col};stroke-width:{1.8 / s:.2f};stroke-linecap:round;stroke-linejoin:round" class="s-ink">{AWS_ICONS[kind]}</g>'

GROUP = {'cloud': ('#5A6B7F', '', 'AWS Cloud'), 'region': ('#147EBA', '6 4', 'Region'), 'az': ('#147EBA', '3 3', 'Availability Zone'),
         'vpc': ('#8C4FFF', '', 'VPC'), 'pub': ('#7AA116', '', 'Public subnet'), 'priv': ('#147EBA', '', 'Private subnet'),
         'sg': ('#DD344C', '4 3', 'Security group'), 'acct': ('#E7157B', '', 'Account'), 'onprem': ('#7D8998', '5 3', 'Outside AWS')}
def grp(kind, x, y, w, h, label=None, k=None):
    """AWS-diagram-convention group box (outline + label top-left). Optional data-k for the simulator."""
    col, dash, default = GROUP[kind]
    da = f' stroke-dasharray="{dash}"' if dash else ''
    tint = {'pub': 'rgba(122,161,22,.07)', 'priv': 'rgba(20,126,186,.06)'}.get(kind, 'none')
    o = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" style="fill:{tint};stroke:{col};stroke-width:1.4"{da}/>'
         f'<rect x="{x}" y="{y}" width="12" height="12" style="fill:{col}"/>'
         f'<text x="{x + 16}" y="{y + 10}" font-size="7.4" font-weight="700" style="fill:{col}">{label or default}</text>')
    return f'<g data-k="{k}">{o}</g>' if k else o
def svc(x, y, kind, label, sub='', tone='blue', k=None, w=70):
    """A service tile: icon over label (+ sub), centred on x; y = top."""
    o = box(x - w / 2, y, w, 52, tone, rx=6) + ai(kind, x - 9, y + 5, 0.75) + t(x, y + 36, label, 7.2, 'ink', bold=True) + (t(x, y + 46, sub, 6.2, 'ink2') if sub else '')
    return f'<g data-k="{k}">{o}</g>' if k else o
def link(x1, y1, x2, y2, k=None, label='', dash=False):
    o = arrow(x1, y1, x2, y2, dash=dash) + (t((x1 + x2) / 2, (y1 + y2) / 2 - 4, label, 6.4, 'ink2') if label else '')
    return f'<g data-k="{k}">{o}</g>' if k else o
def awsfig(aria, inner, w=640, h=300, caption=''):
    """Standalone AWS-style diagram (also used as the simulator's diagram)."""
    cap_ = t(w / 2, h - 8, caption, 7.4, 'ink2') if caption else ''
    return f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(aria)}">{inner}{cap_}</svg>'

_SIM_ASSETS = [False]
def simlab(cfg):
    """Embed the AWS Lab Simulator. cfg: see assets/js/aws-sim.js header. Assets are linked once per page."""
    import json as _j
    head = ''
    if not _SIM_ASSETS[0]:
        _SIM_ASSETS[0] = True
        head = '<link rel="stylesheet" href="../../../../assets/css/aws-sim.css"><script src="../../../../assets/js/aws-sim.js" defer></script>'
    cfg = dict(cfg); dia = cfg.pop('diagram', '')
    return head + '<div class="awssim">' + (f'<div class="as-diagsrc" hidden>{dia}</div>' if dia else '') + '<script type="application/json">' + _j.dumps(cfg, ensure_ascii=False).replace('</', '<\\/') + '</script></div>'


# ---------------------------------------------------------------- v3 depth sections (AWS course)
def _cell(x):
    return x
def under_hood(intro, blocks):
    """Under the hood: [(h4, html)] blocks."""
    return f'  <p>{intro}</p>\n' + ''.join(f'  <h3>{h}</h3>\n  {b}\n' for h, b in blocks)
def errors_table(rows):
    """[(error text, when you see it, cause, fix)] — real error messages."""
    body = ''.join(f'<tr><td><code style="overflow-wrap:anywhere">{E(e)}</code></td><td>{w}</td><td>{c}</td><td>{f}</td></tr>' for e, w, c, f in rows)
    return ('  <div class="table-wrap"><table class="compare" style="min-width:640px"><thead><tr><th>Error you see</th><th>When</th><th>Why</th><th>Fix</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>\n')
def cheatsheet(rows):
    """[(command, what it does)]"""
    body = ''.join(f'<tr><td><code style="overflow-wrap:anywhere">{E(c)}</code></td><td>{w}</td></tr>' for c, w in rows)
    return f'  <div class="table-wrap"><table class="compare" style="min-width:560px"><thead><tr><th>Command</th><th>What it does</th></tr></thead><tbody>{body}</tbody></table></div>\n'
def cost_calc(title, rows, total, note):
    """rows: [(item, quantity, unit price, monthly)]"""
    body = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td style="text-align:right">{d}</td></tr>' for a, b, c, d in rows)
    return (f'  <h3>{title}</h3>\n  <div class="table-wrap"><table class="compare" style="min-width:560px"><thead><tr><th>Item</th><th>Quantity</th><th>Unit price</th><th style="text-align:right">Per month</th></tr></thead>'
            f'<tbody>{body}<tr><td colspan="3"><b>Total</b></td><td style="text-align:right"><b>{total}</b></td></tr></tbody></table></div>\n  <p class="muted" style="font-size:.9em">{note}</p>\n')
def checklist(title, items):
    li = ''.join(f'<li style="list-style:none;margin:4px 0"><span aria-hidden="true">☐</span> {x}</li>' for x in items)
    return f'  <h3>{title}</h3>\n  <ul style="padding-left:4px">{li}</ul>\n'
def realcases(cases):
    """[(who, problem, aws solution, result)]"""
    return ''.join(f'  <div class="card" style="padding:12px 16px;margin:10px 0"><p style="margin:0 0 4px"><b>{w}</b></p><p style="margin:0 0 4px"><b>Problem:</b> {p}</p><p style="margin:0 0 4px"><b>On AWS:</b> {s}</p><p style="margin:0"><b>Result:</b> {r}</p></div>\n' for w, p, s, r in cases)
LVL = {'Basic': '#2F7D5B', 'Intermediate': '#2E5AAC', 'Advanced': '#B45309', 'Very basic': '#7A8496'}
def projects(items):
    """Levelled mini projects: [(level, title, scenario, steps[], deliverable, stretch)]"""
    o = '  <p>Three projects, each a little harder. Do them on your own account (or plan them on paper first). Each lists what to hand in, so a teacher can mark it.</p>\n'
    for lv, ti, sc, st, dl, sx in items:
        li = ''.join(f'<li>{s}</li>' for s in st)
        o += (f'  <details class="faq" open><summary><span style="display:inline-block;padding:1px 8px;border-radius:99px;background:{LVL[lv]};color:#fff;font-size:.8em;margin-right:6px">{lv}</span><b>{ti}</b></summary>'
              f'<p><b>Scenario:</b> {sc}</p><ol>{li}</ol><p><b>Hand in:</b> {dl}</p>' + (f'<p><b>Stretch goal:</b> {sx}</p>' if sx else '') + '</details>\n')
    return o
def refs(items):
    li = ''.join(f'<li><a href="{u}" rel="noopener" target="_blank">{n}</a></li>' for n, u in items)
    return f'  <h3>Official documentation to read next</h3>\n  <ul>{li}</ul>\n'

ROLE_TONE = {'Software developer': 'blue', 'App / mobile developer': 'violet', 'Data analyst': 'green', 'Data engineer': 'amber', 'ML / AI engineer': 'red', 'DevOps / cloud engineer': 'card', 'Security engineer': 'red'}
def by_role(intro, rows):
    """rows: [(role, what they do with it, services/tools, a real task, skill to build)]"""
    o = f'  <p>{intro}</p>\n'
    for r, what, svcs, task, skill in rows:
        o += (f'  <div class="card" style="padding:12px 16px;margin:10px 0;border-left:4px solid var(--blue)"><p style="margin:0 0 4px"><b>{r}</b></p>'
              f'<p style="margin:0 0 4px">{what}</p><p style="margin:0 0 4px"><b>Uses:</b> {svcs}</p><p style="margin:0 0 4px"><b>A real task:</b> {task}</p>'
              f'<p style="margin:0"><b>Skill to build:</b> {skill}</p></div>\n')
    return o
def by_domain(intro, rows):
    """rows: [(domain, typical workload, AWS pattern, rules / compliance to remember)]"""
    return f'  <p>{intro}</p>\n' + table(['Domain', 'Typical workload', 'AWS pattern', 'Rules to remember'], [list(r) for r in rows], minw=720)


# ---------------------------------------------------------------- illustrated scene animations (wide, AWS-style)
SA_COL = {'blue': '#2E5AAC', 'green': '#2F7D5B', 'red': '#D64545', 'amber': '#E0A100', 'violet': '#7C4DDB', 'grey': '#7A8496', 'saffron': '#E8772E'}
def sa_flow(d, col='blue', dur=2.2, n=3, r=4.2, label='', lx=None, ly=None, dash=True):
    """Continuous traffic along an SVG path d: dashed line + n dots moving forever (SMIL)."""
    c = SA_COL.get(col, col)
    o = f'<path d="{d}" style="fill:none;stroke:{c};stroke-width:2;opacity:.55"' + (' class="sa-dash"' if dash else '') + '/>'
    for i in range(n):
        o += (f'<circle r="{r}" style="fill:{c};stroke:#fff;stroke-width:1.2"><animateMotion dur="{dur}s" repeatCount="indefinite" begin="{-i * dur / n:.2f}s" path="{d}"/></circle>')
    if label and lx is not None:
        o += f'<rect x="{lx - len(label) * 2.6 - 6}" y="{ly - 9}" width="{len(label) * 5.2 + 12}" height="14" rx="7" style="fill:{c}"/><text x="{lx}" y="{ly + 1.5}" text-anchor="middle" font-size="7.6" font-weight="700" style="fill:#fff">{label}</text>'
    return o
def sa_badge(x, y, n, col='saffron'):
    return f'<g class="sa-pop"><circle cx="{x}" cy="{y}" r="10" style="fill:{SA_COL[col]}"/><text x="{x}" y="{y + 3.6}" text-anchor="middle" font-size="10" font-weight="700" style="fill:#fff">{n}</text></g>'
def sa_note(x, y, w, lines, col='saffron', anchor='mid'):
    """Callout box with 1–3 lines (first bold)."""
    h = 8 + 13 * len(lines); x0 = x - w / 2 if anchor == 'mid' else x
    o = f'<g class="sa-pop"><rect x="{x0}" y="{y}" width="{w}" height="{h}" rx="7" style="fill:var(--card);stroke:{SA_COL.get(col, col)};stroke-width:2"/>'
    for i, ln in enumerate(lines):
        o += f'<text x="{x0 + w / 2}" y="{y + 15 + 13 * i}" text-anchor="middle" font-size="{8.6 if i == 0 else 7.6}" font-weight="{700 if i == 0 else 400}" class="s-ink">{ln}</text>'
    return o + '</g>'
def sa_cross(x, y, s=14):
    return f'<g class="sa-pop"><circle cx="{x}" cy="{y}" r="{s}" style="fill:#D64545"/><path d="M{x - s / 2.4} {y - s / 2.4}L{x + s / 2.4} {y + s / 2.4}M{x + s / 2.4} {y - s / 2.4}L{x - s / 2.4} {y + s / 2.4}" style="stroke:#fff;stroke-width:3;stroke-linecap:round"/></g>'
def sa_tick(x, y, s=14):
    return f'<g class="sa-pop"><circle cx="{x}" cy="{y}" r="{s}" style="fill:#2F7D5B"/><path d="M{x - s / 2.2} {y}L{x - s / 8} {y + s / 2.6}L{x + s / 2} {y - s / 2.6}" style="fill:none;stroke:#fff;stroke-width:3;stroke-linecap:round;stroke-linejoin:round"/></g>'
def sa_bolt(x, y, s=1.0):
    return f'<path class="sa-blink" transform="translate({x},{y}) scale({s})" d="M10 0L0 18h8l-4 16L18 12h-8l4-12z" style="fill:#E0A100;stroke:#B45309;stroke-width:1"/>'
def sa_dark(x, y, w, h, rx=6):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" style="fill:#0b0f16;opacity:.55"/>'
def sa_people(x, y, n=3, col='blue'):
    c = SA_COL[col]; o = ''
    for i in range(n):
        cx = x + i * 14
        o += f'<circle cx="{cx}" cy="{y}" r="5" style="fill:{c}"/><path d="M{cx - 8} {y + 17}c1-7 4-10 8-10s7 3 8 10z" style="fill:{c}"/>'
    return o
def sa_server(x, y, w=34, h=40, col='blue', label=''):
    c = SA_COL[col]
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" style="fill:var(--card);stroke:{c};stroke-width:1.8"/>'
    for k in range(3):
        yy = y + 7 + k * 11
        o += f'<rect x="{x + 5}" y="{yy}" width="{w - 10}" height="7" rx="1.5" style="fill:{c};opacity:.18"/><circle cx="{x + w - 9}" cy="{yy + 3.5}" r="1.6" style="fill:#2F7D5B"/>'
    if label: o += f'<text x="{x + w / 2}" y="{y + h + 10}" text-anchor="middle" font-size="7" class="s-ink2">{label}</text>'
    return o
def sa_db(x, y, label='', col='blue', crown=False):
    c = SA_COL[col]
    o = (f'<ellipse cx="{x}" cy="{y}" rx="18" ry="6" style="fill:var(--card);stroke:{c};stroke-width:1.8"/>'
         f'<path d="M{x - 18} {y}v24c0 3.5 8 6 18 6s18-2.5 18-6V{y}" style="fill:var(--card);stroke:{c};stroke-width:1.8"/>'
         f'<path d="M{x - 18} {y + 12}c0 3.5 8 6 18 6s18-2.5 18-6" style="fill:none;stroke:{c};stroke-width:1.2;opacity:.6"/>')
    if crown: o += f'<path class="sa-pop" d="M{x - 9} {y - 9}l3-8 6 5 6-5 3 8z" style="fill:#E0A100"/>'
    if label: o += f'<text x="{x}" y="{y + 42}" text-anchor="middle" font-size="7.2" font-weight="700" class="s-ink">{label}</text>'
    return o
def sa_gauge(x, y, pct, label, col=None):
    col = col or ('#D64545' if pct >= 80 else '#E0A100' if pct >= 60 else '#2F7D5B')
    return (f'<rect x="{x}" y="{y}" width="12" height="44" rx="3" style="fill:var(--paper-2);stroke:var(--line)"/>'
            f'<rect class="sa-grow" x="{x}" y="{y + 44 - 44 * pct / 100}" width="12" height="{44 * pct / 100}" rx="3" style="fill:{col}"/>'
            f'<text x="{x + 6}" y="{y + 56}" text-anchor="middle" font-size="7.2" font-weight="700" class="s-ink">{pct}%</text><text x="{x + 6}" y="{y - 4}" text-anchor="middle" font-size="6.6" class="s-ink2">{label}</text>')
def sa_building(x, y, w, h, label, col='blue', sub=''):
    c = SA_COL[col]
    o = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" style="fill:{c};opacity:.08"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" style="fill:none;stroke:{c};stroke-width:1.6;stroke-dasharray:5 3"/>'
    o += f'<text x="{x + 8}" y="{y + 13}" font-size="8" font-weight="700" style="fill:{c}">{label}</text>'
    if sub: o += f'<text x="{x + w - 8}" y="{y + 13}" text-anchor="end" font-size="6.8" class="s-ink2">{sub}</text>'
    return o
def scene_anim(title, intro, panel, aria, static, frames, hid, w=640, h=330, delay=6500):
    """Wide illustrated animation. static: svg drawn always. frames: [(overlay_svg, 'Step title', 'what happens html')]."""
    body = static + ''.join(f'<g data-on="{i + 1}">{f}</g>' for i, (f, _, _) in enumerate(frames))
    lis = '\n'.join(f'          <li><b>{hd}</b> — {tx}</li>' for _, hd, tx in frames)
    return f'''
  <span class="live">Animated</span>
  <h3 id="{hid}">{title}</h3>
  <p class="anim-intro">{intro}</p>
  <div class="anim anim--one anim--wide" data-frames="{len(frames)}" data-delay="{delay}">
    <div class="anim__title">{panel} <span>{len(frames)} steps</span></div>
    <div class="anim__views">
      <div class="view view--story">
        <span class="view__tag">Watch what happens</span>
        <svg viewBox="0 0 {w} {h}" role="img" aria-label="{E(aria)}">
          {body}
          <text x="{w - 6}" y="{h - 4}" text-anchor="end" class="s-wm">myphatshala.in</text>
        </svg>
        <ol class="caps" hidden>
{lis}
        </ol>
      </div>
    </div>
  </div>
'''
def sa_screen(x, y, w, h, title, lines, dark=False):
    """A window (browser or terminal) with lines of text."""
    bg = '#0f1720' if dark else 'var(--card)'; fg = '#d6e2ee' if dark else 'currentColor'
    o = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" style="fill:{bg};stroke:#5A6B7F;stroke-width:1.4"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="13" rx="6" style="fill:#5A6B7F"/><circle cx="{x + 8}" cy="{y + 6.5}" r="2.2" style="fill:#D64545"/><circle cx="{x + 15}" cy="{y + 6.5}" r="2.2" style="fill:#E0A100"/>'
         f'<text x="{x + 24}" y="{y + 9.5}" font-size="6.6" style="fill:#fff">{title}</text>')
    for i, ln in enumerate(lines):
        o += f'<text x="{x + 7}" y="{y + 25 + i * 11}" font-size="7" font-family="var(--font-code)" style="fill:{fg}">{ln}</text>'
    return o
def sa_pill(x, y, text, col='blue', w=None):
    w = w or len(text) * 5.2 + 14
    return f'<g class="sa-pop"><rect x="{x - w / 2}" y="{y - 9}" width="{w}" height="16" rx="8" style="fill:{SA_COL.get(col, col)}"/><text x="{x}" y="{y + 3}" text-anchor="middle" font-size="7.6" font-weight="700" style="fill:#fff">{text}</text></g>'
def sa_icon(kind, x, y, s=1.4, col='blue'):
    return ai(kind, x, y, s, SA_COL.get(col, col))


# ---------------------------------------------------------------- learner levels (owner, 12 Nov)
LADDER_TONE = [('Level 0 · Curious', 'no computer background', '#7A8496'), ('Level 1 · Beginner', 'first steps on AWS', '#2F7D5B'), ('Level 2 · Intermediate', 'can do it alone', '#2E5AAC'), ('Level 3 · Advanced', 'designs for others', '#B45309'), ('Level 4 · Expert', 'architect / interviewer', '#7C4DDB')]
def ladder(rows):
    """rows: 5 tuples (understand_html, try_html, check_question, check_answer) for levels 0-4."""
    o = '  <p>Find your level, read that card, do the “Try” and answer the check. Then move one level up. Everyone starts somewhere — Level 0 needs no computer background at all.</p>\n'
    for (name, who, col), (u, tr, q, a) in zip(LADDER_TONE, rows):
        o += (f'  <div class="card" style="padding:12px 16px;margin:10px 0;border-left:6px solid {col}">'
              f'<p style="margin:0 0 6px"><span style="display:inline-block;padding:1px 10px;border-radius:99px;background:{col};color:#fff;font-weight:700;font-size:.85em">{name}</span> <span class="muted" style="font-size:.88em">{who}</span></p>'
              f'<p style="margin:0 0 4px"><b>Understand:</b> {u}</p><p style="margin:0 0 4px"><b>Try:</b> {tr}</p>'
              f'<details class="faq" style="margin:4px 0 0"><summary><b>Check yourself:</b> {q}</summary><p>{a}</p></details></div>\n')
    return o
def newbie(text, words):
    """'New to computers? Start here' callout + jargon buster. words: [(term, everyday meaning)]"""
    li = ''.join(f'<li><b>{w}</b> — {m}</li>' for w, m in words)
    return (f'<div class="callout callout--tip" style="display:block"><p style="margin:0 0 6px"><b>New to computers? Start here.</b> {text}</p>'
            f'<p style="margin:0 0 4px"><b>Jargon buster:</b></p><ul style="margin:0">{li}</ul></div>')
