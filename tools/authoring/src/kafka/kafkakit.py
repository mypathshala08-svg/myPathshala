"""Small drawing helpers shared by the Apache Kafka lessons (authoring time only)."""
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
    """Myth vs Kafka 4.4 reality, each with proof from our lab. rows: [(myth, reality, proof)]."""
    items = ''.join(f'<li><b>Myth:</b> {m}<br><b>Reality (Kafka 4.4):</b> {r}<br><span class="muted">Proof: {p}</span></li>' for m, r, p in rows)
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
