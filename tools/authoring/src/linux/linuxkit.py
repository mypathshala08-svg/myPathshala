"""Drawing and block helpers for Linux lessons (authoring time only). Used by each lesson's _body.py."""
import os, sys, re, html as _html
_HERE = os.path.dirname(os.path.abspath(__file__))
AUTH = os.path.abspath(os.path.join(_HERE, '..', '..'))
sys.path.insert(0, AUTH)
from svgkit import *            # noqa: F401,F403  (t, box, fill, label_box, arrow, cap, anim_one, anim_two, scene, table, ...)
import shlesson                 # real Bash runs for one-liners

E = _html.escape
SITE = os.path.abspath(os.path.join(AUTH, '..', '..'))

# ---------------------------------------------------------------- glossary links
_GL = None
def gl(term_id, text=None):
    """Link to a glossary card: gl('inode') -> <a href="../../glossary/#inode">inode</a>. Fails if the id does not exist."""
    global _GL
    if _GL is None:
        p = os.path.join(SITE, 'courses', 'linux', 'glossary', 'index.html')
        _GL = set(re.findall(r'<article class="gt" id="([^"]+)"', open(p, encoding='utf-8').read()))
    if term_id not in _GL:
        raise SystemExit(f'glossary id not found: {term_id}')
    return f'<a class="gl-term" href="../../glossary/#{term_id}" title="Open in the Linux glossary">{text or term_id}</a>'


# ---------------------------------------------------------------- terminal drawing (SVG)
def term(x, y, w, h, lines, title='riya@laptop: ~', size=8.6, step=13.5, cursor=False, prompt='riya@laptop:~$'):
    """A terminal window. lines: list of str or (str, cls) where cls in prompt|out|err|dim|acc."""
    col = {'prompt': '#9FD3B8', 'out': '#EDEBE3', 'err': '#F59E8B', 'dim': '#8A94A0', 'acc': '#F5C77E'}
    o = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" style="fill:#1F2B26;stroke:#2C3A33"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="16" rx="8" style="fill:#2C3A33"/><rect x="{x}" y="{y+8}" width="{w}" height="8" style="fill:#2C3A33"/>'
         + ''.join(f'<circle cx="{x+10+k*9}" cy="{y+8}" r="2.6" style="fill:{c}"/>' for k, c in enumerate(['#D64545', '#E0A100', '#2F7D5B']))
         + f'<text x="{x+w/2}" y="{y+11.5}" text-anchor="middle" font-size="7.4" style="fill:#B7BFCC">{E(title)}</text>')
    yy = y + 16 + step
    for ln in lines:
        s, c = (ln, None) if isinstance(ln, str) else ln
        if c is None:
            c = 'prompt' if s.startswith('$ ') else 'out'
        if c == 'prompt' and s.startswith('$ '):
            o += (f'<text x="{x+8}" y="{yy}" font-size="{size}" class="mono"><tspan style="fill:#9FD3B8">{E(prompt)}</tspan>'
                  f'<tspan style="fill:#EDEBE3"> {E(s[2:])}</tspan></text>')
        else:
            o += f'<text x="{x+8}" y="{yy}" font-size="{size}" class="mono" style="fill:{col[c]}">{E(s)}</text>'
        yy += step
    if cursor:
        o += f'<rect x="{x+8}" y="{yy-size}" width="5" height="{size+1}" style="fill:#9FD3B8"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>'
    return o


def server(x, y, w=46, h=56, label='server', tone='blue', leds=3):
    """A rack server drawn as stacked units."""
    o = box(x, y, w, h, tone, rx=5)
    for k in range(leds):
        yy = y + 8 + k * ((h - 12) / leds)
        o += f'<rect x="{x+5}" y="{round(yy,1)}" width="{w-10}" height="{round((h-12)/leds-4,1)}" rx="2" class="s-card2"/>'
        o += f'<circle cx="{x+w-10}" cy="{round(yy+((h-12)/leds-4)/2,1)}" r="1.8" style="fill:#2F7D5B"/>'
    if label:
        o += t(x + w / 2, y + h + 11, label, 8, 'ink2')
    return o


def laptop(x, y, w=70, label=None, screen=None):
    h = w * 0.58
    o = (f'<rect x="{x}" y="{y}" width="{w}" height="{round(h,1)}" rx="4" class="s-board"/>'
         f'<rect x="{x+4}" y="{y+4}" width="{w-8}" height="{round(h-8,1)}" rx="2" style="fill:#2C3A33"/>'
         f'<path d="M{x-8} {round(y+h+6,1)}h{w+16}l-6 -6h-{w+4}z" class="s-card" style="stroke:var(--line)"/>')
    if screen:
        o += screen
    if label:
        o += t(x + w / 2, round(y + h + 18, 1), label, 8, 'ink2')
    return o


def phone(x, y, w=34, h=60, label=None, text=None):
    o = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" class="s-board"/>'
         f'<rect x="{x+3}" y="{y+7}" width="{w-6}" height="{h-14}" rx="2" style="fill:#F4F1EA"/>')
    if text:
        o += t(x + w / 2, y + h / 2 + 3, text, 7.6, 'green', bold=True)
    if label:
        o += t(x + w / 2, y + h + 11, label, 8, 'ink2')
    return o


# ---------------------------------------------------------------- blocks
LV = {'v': ('v', 'Very basic'), 'b': ('b', 'Beginner'), 'i': ('i', 'Intermediate'), 'a': ('a', 'Advanced')}


def oneliners(intro, items, extra=''):
    """One-liner corner. items: dict(level b|i|a, title, scenario, cmd, setup='', explain, expect=None).
    `setup` (hidden) creates sample files; the shown command is really run after it and its output recorded."""
    out = [f'  <h3 id="oneliners">One-liner corner</h3>', f'  <p class="ol-intro">{intro}</p>', '  <div class="ol-list">']
    for it in items:
        k, name = LV[it['level']]
        script = (it.get('setup', '').rstrip('\n') + '\n' if it.get('setup') else '') + it['cmd']
        if it.get('setup') and shlesson.run_sh(it['setup'], 'any').strip():
            raise SystemExit('one-liner setup must print nothing: ' + it['title'])
        res = shlesson.run_sh(script, it.get('expect')).rstrip('\n')
        o = f'<div class="output">{E(res)}</div>' if res else ''
        setup_note = f'<p class="ol-setup">Sample files used: {it["files_note"]}</p>' if it.get('files_note') else ''
        out.append(f'''    <article class="ol">
      <div class="ol__head"><span class="lvl lvl--{k}">{name}</span><h4>{it['title']}</h4></div>
      <p class="ol__scn"><b>Scenario:</b> {it['scenario']}</p>
      {setup_note}
      <div class="code" data-lang="bash" data-file="Terminal"><pre><code>{E(it['cmd'])}</code></pre>{o}</div>
      <p class="ol__how">{it['explain']}</p>
    </article>''')
    if extra:
        out.append(extra)
    out.append('  </div>')
    return '\n'.join(out)


def which(intro, rows):
    """Which command when? rows: (situation, command, why, common_mistake)."""
    tr = ''.join(f'<tr><td>{a}</td><td><code>{E(b)}</code></td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in rows)
    return f'''  <h3 id="which">Which command when?</h3>
  <p>{intro}</p>
  <div class="table-wrap">
  <table class="compare which" style="min-width:640px">
    <thead><tr><th>You want to…</th><th>Use</th><th>Why</th><th>Common mistake</th></tr></thead>
    <tbody>{tr}</tbody>
  </table>
  </div>'''


def before(text):
    return f'<div class="callout callout--tip"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg><p><b>Before you start:</b> {text}</p></div>\n'


# ================================================================ new format blocks (5 Nov 2026)
import json as _json
_COURSE = None
def _course():
    global _COURSE
    if _COURSE is None:
        _COURSE = _json.load(open(os.path.join(SITE, 'courses', 'linux', 'course.json'), encoding='utf-8'))
    return _COURSE


def lesson_link(ref):
    """'2.3' -> (href relative to a lesson page, title, live?). Other courses: ('course:shell-scripting', 'Shell Scripting')."""
    if ref.startswith('course:'):
        cid = ref.split(':', 1)[1]
        return f'../../../{cid}/', None, True
    m, l = (int(x) for x in ref.split('.'))
    mo = _course()['modules'][m - 1]; le = mo['lessons'][l - 1]
    path = f"{mo['slug']}/{le['slug']}/"
    live = os.path.exists(os.path.join(SITE, 'courses', 'linux', path, 'index.html'))
    return ('../../' + path if live else f'../../#m{m}'), le['title'], live


def concept_map(before, now, after, note=''):
    """Where this lesson fits. before/after: [(ref or None, label, why)]; now: [str] (what you learn here).
    Live lessons become links; future ones link to the syllabus and say 'coming soon'."""
    def card(ref, label, why):
        if ref:
            href, title, live = lesson_link(ref)
            tag = f'<span class="cm__ref">Lesson {ref}</span>' if not ref.startswith('course:') else '<span class="cm__ref">Course</span>'
            soon = '' if live else ' <small class="cm__soon">coming soon</small>'
            return f'<a class="cm__card" href="{href}">{tag}<b>{label}</b><span>{why}</span>{soon}</a>'
        return f'<div class="cm__card"><span class="cm__ref">Basics</span><b>{label}</b><span>{why}</span></div>'
    col = lambda title, cls, items: f'<div class="cm__col cm__col--{cls}"><h4>{title}</h4>{"".join(items)}</div>'
    arrow = '<div class="cm__arrow" aria-hidden="true"><svg viewBox="0 0 40 24"><path d="M2 12h30m-8-8 8 8-8 8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
    mid = '<div class="cm__card cm__card--now">' + ''.join(f'<span>✓ {x}</span>' for x in now) + '</div>'
    return f'''<section class="cmap" id="map" aria-label="Where this lesson fits">
  <h2 class="cmap__h">Where this lesson fits</h2>
  <div class="cm">
    {col('You need', 'before', [card(*b) for b in before])}
    {arrow}
    {col('In this lesson', 'now', [mid])}
    {arrow}
    {col('It unlocks', 'after', [card(*a) for a in after])}
  </div>
  {f'<p class="cmap__note">{note}</p>' if note else ''}
</section>
'''


LV4 = [('v', 'Very basic'), ('b', 'Basic'), ('i', 'Intermediate'), ('a', 'Advanced')]
def levels4(heading, panels):
    """Four depth tabs. panels: [(key v|b|i|a, title, html)]. Reuses the .modlab tab script in lesson.js."""
    bar = ''.join(f'<button type="button" data-mod="{k}">{n}</button>' for k, n in LV4)
    out = [f'  <h3 id="levels">{heading}</h3>',
           f'  <div class="modlab levels levels4"><div class="modlab__bar"><b>Pick your depth. Completely new? Start at Very basic and climb one step at a time.</b>{bar}</div>']
    names = dict(LV4)
    for k, title, h in panels:
        out.append(f'    <div class="modlab__panel" data-mod="{k}"><h4><span class="lvl lvl--{k}">{names[k]}</span> {title}</h4>\n{h}\n    </div>')
    out.append('  </div>')
    return '\n'.join(out)


def dissect(title, intro, layers, hid='dissect', hint='Top = what you touch · bottom = the hardware. Click a layer.'):
    """Layer-by-layer dissection. layers (top → bottom): dict(key, name, sub, why, how, impl, used, cmd=None, setup=None, expect=None).
    Click a layer to see Kyun (why) · Kaise (how) · Kahan banaya (where it is implemented) · Kahan use (where it is used).
    An optional `cmd` is really run and its output shown ("see this layer yourself")."""
    bar = ''.join(f'<button type="button" data-mod="{L["key"]}"><b>{L["name"]}</b><small>{L["sub"]}</small></button>' for L in layers)
    panels = []
    for L in layers:
        see = ''
        if L.get('cmd'):
            script = (L.get('setup', '') + '\n' if L.get('setup') else '') + L['cmd']
            res = shlesson.run_sh(script, L.get('expect')).rstrip('\n')
            see = f'''<div class="dx__see"><p class="wx__label">See this layer yourself (real output)</p>
        <div class="code" data-lang="bash" data-file="Terminal"><pre><code>{E(L['cmd'])}</code></pre>{f'<div class="output">{E(res)}</div>' if res else ''}</div></div>'''
        panels.append(f'''    <div class="modlab__panel" data-mod="{L['key']}">
      <h4>{L['name']} <small>{L['sub']}</small></h4>
      <div class="dx__grid">
        <div class="dx__q dx__q--why"><b>Why does it exist?</b><p>{L['why']}</p></div>
        <div class="dx__q dx__q--how"><b>How does it work?</b><p>{L['how']}</p></div>
        <div class="dx__q dx__q--impl"><b>Where is it, really?</b><p>{L['impl']}</p></div>
        <div class="dx__q dx__q--used"><b>Where is it used?</b><p>{L['used']}</p></div>
      </div>
      {see}
    </div>''')
    return f'''  <h3 id="{hid}">{title}</h3>
  <p>{intro}</p>
  <div class="modlab dissect"><div class="modlab__bar"><b>{hint}</b>{bar}</div>
{chr(10).join(panels)}
  </div>
'''


def names(intro, rows):
    """'Why is it called that?' rows: (command, stands for, memory hook)."""
    cards_ = ''.join(f'<div class="nm"><code>{E(c)}</code><b>{s}</b><span>{h}</span></div>' for c, s, h in rows)
    return f'''  <h3 id="names">Why is it called that?</h3>
  <p>{intro}</p>
  <div class="nms">{cards_}</div>
'''


def qc(question, answer, options=None):
    """Quick check at the end of a part. Answer revealed on click."""
    opts = ''.join(f'<li>{o}</li>' for o in options) if options else ''
    return f'''  <details class="qc"><summary><span class="qc__tag">Quick check</span> {question}</summary>
    {f'<ol type="A" class="qc__opts">{opts}</ol>' if opts else ''}<div class="qc__a"><b>Answer:</b> {answer}</div></details>
'''


def didyou(text):
    return f'<div class="callout callout--did"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v5h1"/></svg><p><b>Did you know?</b> {text}</p></div>\n'


def puzzle(text):
    return f'<div class="puzzle" id="puzzle"><span class="puzzle__tag">Think first</span><p>{text}</p><small>Keep your guess in mind. The answer is at the end of part 6.</small></div>\n'


def puzzle_answer(text):
    return f'<details class="puzzle puzzle--ans"><summary><span class="puzzle__tag">Puzzle answer</span> Remember the question from the story? Open to check your guess.</summary><p>{text}</p></details>\n'


def teaser(ref, question):
    href, title, live = lesson_link(ref)
    return f'''<aside class="teaser"><span class="teaser__tag">Next up · Lesson {ref}</span><p class="teaser__q">{question}</p><a href="{href}">{title} →</a></aside>'''


def build_up(title, scenario, setup, steps, level='b', expect=None):
    """Build a pipeline one stage at a time. steps: [(cmd, note)]; each is really run after the hidden setup."""
    if setup and shlesson.run_sh(setup, 'any').strip():
        raise SystemExit('build_up setup must print nothing: ' + title)
    k, name = LV[level]
    items = []
    for i, (cmd, note) in enumerate(steps, 1):
        res = shlesson.run_sh((setup + '\n' if setup else '') + cmd, expect).rstrip('\n')
        items.append(f'''      <li><p>{note}</p>
        <div class="code" data-lang="bash" data-file="Step {i}"><pre><code>{E(cmd)}</code></pre>{f'<div class="output">{E(res)}</div>' if res else ''}</div></li>''')
    return f'''    <article class="ol ol--build">
      <div class="ol__head"><span class="lvl lvl--{k}">{name}</span><h4>Build it step by step: {title}</h4></div>
      <p class="ol__scn"><b>Scenario:</b> {scenario}</p>
      <ol class="build">
{chr(10).join(items)}
      </ol>
    </article>'''


# ================================================================ mind map (revision)
def mindmap(center, branches, note=''):
    """Radial mind map for revision. branches: [(label, tone, [leaf, ...])], 4-6 branches, 2-4 short leaves each.
    Returned html goes into spec.py as MINDMAP; shlesson.post() places it before 'Quick revision'."""
    import math
    W, H, cx, cy = 760, 460, 380, 230
    n = len(branches)
    col = {'acc': 'var(--track)', 'blue': 'var(--blue)', 'green': 'var(--green)', 'violet': 'var(--violet)', 'amber': '#E0A100', 'red': '#D64545'}
    o = ''
    nodes = []
    for k, (lab, tone, leaves) in enumerate(branches):
        ang = -math.pi / 2 + 2 * math.pi * k / n
        bx, by = cx + 250 * math.cos(ang), cy + 150 * math.sin(ang)
        nodes.append((bx, by, lab, tone, leaves, ang))
        o += f'<path d="M{cx} {cy} Q{(cx + bx) / 2 + 30 * math.sin(ang):.0f} {(cy + by) / 2 - 30 * math.cos(ang):.0f} {bx:.0f} {by:.0f}" style="fill:none;stroke:{col.get(tone, "var(--line)")};stroke-width:3;opacity:.7"/>'
    o += f'<ellipse cx="{cx}" cy="{cy}" rx="92" ry="34" class="s-board"/>' + t(cx, cy + 5, center, 12, 's-chalk', bold=True)
    for bx, by, lab, tone, leaves, ang in nodes:
        w = max(110, 8 * len(lab) + 24)
        o += box(round(bx - w / 2), round(by - 15), w, 30, tone, rx=15) + t(round(bx), round(by + 5), lab, 10.5, bold=True)
        lw = max(len(x) for x in leaves) * 6.1 + 16
        below = math.sin(ang) >= -0.2
        ly0 = by + 24 if below else by - 24 - 15 * len(leaves)
        lx = min(max(bx - lw / 2, 6), W - lw - 6)
        o += f'<rect x="{lx:.0f}" y="{ly0:.0f}" width="{lw:.0f}" height="{15 * len(leaves) + 8}" rx="8" class="s-card2" style="stroke:{col.get(tone, "var(--line)")};stroke-width:1"/>'
        o += ''.join(t(round(lx + 8), round(ly0 + 16 + 15 * i), '• ' + leaf, 9.4, 'ink2', anchor='start') for i, leaf in enumerate(leaves))
    aria = center + ': ' + '; '.join(f'{l}: ' + ', '.join(lv) for l, _, lv in branches)
    return f'''  <h3 id="mindmap">Mind map: the whole lesson on one page</h3>
  <p>{note or 'Revise from the centre outwards. Each branch is one idea from the lesson; the boxes hold the facts to remember. Try to redraw it from memory on paper.'}</p>
  <div class="scene scene--wide mm"><svg viewBox="0 0 {W} {H}" role="img" aria-label="{E(aria)}">{o}<text x="{W - 8}" y="{H - 6}" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>
'''


# ================================================================ Linux-specific blocks (6 Nov 2026)
# Requested by Vineeta: explain every command first, then group its variations by field; plus risk badges,
# error decoder, under the hood, distro differences, undo, shortcuts, script it, interview corner, cheat sheet, lab.
RISK = {'safe': ('🟢', 'Read-only', 'only shows information'),
        'change': ('🟡', 'Changes files', 'creates or changes files; check before pressing Enter'),
        'danger': ('🔴', 'Can destroy data', 'no undo: read the command twice')}
FIELDS = {
    'sys': 'System info / admin', 'dev': 'Software development', 'dba': 'Data administration (DBA)',
    'data': 'Data analysis / engineering', 'devops': 'DevOps / cloud', 'design': 'System design',
    'net': 'Networking', 'sec': 'Security', 'qa': 'Testing / QA', 'ml': 'ML / AI', 'web': 'Web servers',
}


def badge(risk, sudo=False):
    ic, name, tip = RISK[risk]
    s = ('<span class="rb rb--sudo" title="needs administrator rights">sudo needed</span>' if sudo is True else
         f'<span class="rb rb--sudo" title="needs administrator rights">sudo: {sudo}</span>' if sudo else
         '<span class="rb rb--nosudo" title="a normal user can run it">no sudo</span>')
    return f'<span class="rb rb--{risk}" title="{tip}">{ic} {name}</span>{s}'


def _run(cmd, setup='', expect=None):
    if setup and shlesson.run_sh(setup, 'any').strip():
        raise SystemExit('setup must print nothing:\n' + setup)
    return shlesson.run_sh((setup.rstrip('\n') + '\n' if setup else '') + cmd, expect).rstrip('\n')


def _codeout(cmd, res, file='Terminal', typical=False, rec=None):
    lab = (f'<p class="typ">{rec}</p>' if rec else
           '<p class="typ">Typical output (cannot be recorded on our build machine)</p>' if typical else '')
    o = f'<div class="output">{E(res)}</div>' if res else ''
    return f'{lab}<div class="code" data-lang="bash" data-file="{E(file)}"><pre><code>{E(cmd)}</code></pre>{o}</div>'


def anatomy(parts, note=''):
    """Command anatomy. parts: [(text, kind, label)] kind in cmd|opt|arg|sep."""
    chips = ''.join(f'<span class="an an--{k}"><code>{E(x)}</code><small>{lab}</small></span>' for x, k, lab in parts)
    return f'<div class="anat" role="img" aria-label="{E(" ".join(p[0] for p in parts))}">{chips}</div>' + (f'<p class="anat__note">{note}</p>' if note else '')


def mistake(wrong, right, why):
    return (f'<div class="mist"><b class="mist__tag">Common mistake</b><div class="mist__row"><span class="mist__no">✗</span><code>{E(wrong)}</code></div>'
            f'<div class="mist__row"><span class="mist__ok">✓</span><code>{E(right)}</code></div><p>{why}</p></div>\n')


def cmdcard(cid, name, full, what, syntax, risk, options, basic, fields, sudo=False, anat=None, extra='', use=None, avoid=None):
    """One command, explained first, then its variations by field.
    options: [(option, meaning, when to use it)]
    basic:   dict(cmd, setup='', note, expect=None)  -> really run
    fields:  [(field key, [dict(situation, cmd, setup='', why, expect=None, typical=None)])]
             typical='text' = not recordable here: shown as typical output."""
    b = basic
    bres = b['rec'][1] if b.get('rec') else _run(b['cmd'], b.get('setup', ''), b.get('expect'))
    opt = ''.join(f'<tr><td><code>{E(o)}</code></td><td>{m}</td><td>{w}</td></tr>' for o, m, w in options)
    bar = ''.join(f'<button type="button" data-mod="{k}">{FIELDS[k]}</button>' for k, _ in fields)
    panels = []
    for k, items in fields:
        rows = []
        for it in items:
            if it.get('rec'):
                res, typ = it['rec'][1], False
            elif it.get('typical'):
                res, typ = it['typical'], True
            else:
                res, typ = _run(it['cmd'], it.get('setup', ''), it.get('expect')), False
            rows.append(f'''        <li class="fv"><p class="fv__sit"><b>Situation:</b> {it['situation']}</p>
          {_codeout(it['cmd'], res, typical=typ, rec=it['rec'][0] if it.get('rec') else None)}
          <p class="fv__why"><b>Why this way:</b> {it['why']}</p></li>''')
        panels.append(f'''    <div class="modlab__panel" data-mod="{k}"><h4>{name} in {FIELDS[k].lower() if k != 'dba' else 'data administration'}</h4>
      <ol class="fvs">
{chr(10).join(rows)}
      </ol>
    </div>''')
    return f'''  <article class="cc" id="cmd-{cid}">
    <header class="cc__head"><h3><code>{E(name)}</code> <span class="cc__full">{full}</span></h3><div class="cc__badges">{badge(risk, sudo)}</div></header>
    <p class="cc__what">{what}</p>
    {usewhen(use, avoid) if use else ''}
    <p class="cc__syn"><b>Syntax:</b> <code>{E(syntax)}</code></p>
    {anat or ''}
    <div class="table-wrap"><table class="compare cc__opts" style="min-width:560px"><thead><tr><th>Option</th><th>What it does</th><th>When to use it</th></tr></thead><tbody>{opt}</tbody></table></div>
    <p class="wx__label">First run (real output)</p>
    {_codeout(b['cmd'], bres, rec=b['rec'][0] if b.get('rec') else None)}
    <p class="cc__note">{b['note']}</p>
    {extra}
    <p class="cc__fieldh"><b>Now the variations, by field.</b> Pick the field you work in (or want to work in).</p>
    <div class="modlab fields"><div class="modlab__bar"><b>Same command, different jobs. Click a field.</b>{bar}</div>
{chr(10).join(panels)}
    </div>
  </article>
'''


def errors(intro, rows):
    """Error messages decoded. rows: dict(cmd, setup='', meaning, fix). The command is run for real (it must fail)
    and its exit status recorded."""
    items = []
    for r in rows:
        res = _run(r['cmd'] + '\necho "exit status: $?"', r.get('setup', ''), 'any')
        items.append(f'''    <li class="er"><div class="code" data-lang="bash" data-file="Terminal"><pre><code>{E(r['cmd'])}</code></pre><div class="output">{E(res)}</div></div>
      <p><b>What it means:</b> {r['meaning']}</p><p><b>Fix:</b> {r['fix']}</p></li>''')
    return f'''  <h3 id="errors">Error messages decoded</h3>
  <p>{intro}</p>
  <ol class="ers">
{chr(10).join(items)}
  </ol>
'''


def hood(title, intro, cmd, setup='', show=None, explain='', start=None, trace='%file,%desc'):
    """Under the hood: the system calls a command makes (strace, recorded). show = regex of calls to keep;
    start = regex of the first line to keep (drops the program's start-up noise before it)."""
    skip = f"awk 'f||/{start}/{{f=1}} f' | " if start else ''
    script = (setup.rstrip('\n') + '\n' if setup else '') + f'strace -f -e trace={trace} -o /tmp/mp-strace.txt {cmd} > /dev/null 2>&1\n' \
             f"sed -E 's/^[0-9]+ +//' /tmp/mp-strace.txt | {skip}grep -E '{show or '.'}' | grep -v -E 'ld.so|libc|locale|/etc/ld|/usr/lib|gconv|LC_' | head -12\nrm -f /tmp/mp-strace.txt"
    res = shlesson.run_sh(script, 'any').rstrip('\n')
    return f'''  <h3 id="hood">{title}</h3>
  <p>{intro}</p>
  <div class="code" data-lang="bash" data-file="Terminal"><pre><code>{E('strace -f -e trace=' + trace + ' ' + cmd)}</code></pre><div class="output">{E(res)}</div></div>
  <p class="muted">Recorded with <code>strace</code> on our Ubuntu build machine; library loading lines are hidden. You can run the same on your PC after <code>sudo apt install strace</code>.</p>
  {explain}
'''


def distro(intro, rows):
    """Distro & OS differences. rows: (topic, Ubuntu/Debian, RHEL/Rocky/Fedora, macOS (BSD tools), WSL / Git Bash)."""
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'''  <h3 id="distro">Distro and OS differences</h3>
  <p>{intro}</p>
  <div class="table-wrap"><table class="compare" style="min-width:720px"><thead><tr><th>Topic</th><th>Ubuntu / Debian</th><th>RHEL / Rocky / Fedora</th><th>macOS (BSD tools)</th><th>WSL / Git Bash</th></tr></thead><tbody>{tr}</tbody></table></div>
'''


def undo(intro, rows):
    """Undo / safety net. rows: (risk, how to prevent or undo)."""
    li = ''.join(f'<li><b>{a}</b> {b}</li>' for a, b in rows)
    return f'''  <div class="undo" id="undo"><h3>Undo and safety net</h3><p>{intro}</p><ul>{li}</ul></div>
'''


def keys(intro, rows):
    """Keyboard and shell shortcuts. rows: (keys, what it does, example)."""
    tr = ''.join(f'<tr><td><kbd>{E(k)}</kbd></td><td>{w}</td><td><code>{E(x)}</code></td></tr>' for k, w, x in rows)
    return f'''  <h3 id="keys">Keyboard and shell shortcuts</h3>
  <p>{intro}</p>
  <div class="table-wrap"><table class="compare" style="min-width:520px"><thead><tr><th>Keys / syntax</th><th>What it does</th><th>Example</th></tr></thead><tbody>{tr}</tbody></table></div>
'''


def scriptit(title, intro, code, after='', expect=None):
    """Script it: the lesson's task as a small bash script, really run."""
    res = shlesson.run_sh(code, expect).rstrip('\n')
    return f'''  <h3 id="scriptit">Script it: {title}</h3>
  <p>{intro}</p>
  <div class="code" data-lang="bash" data-file="script.sh"><pre><code>{E(code.rstrip())}</code></pre><div class="output">{E(res)}</div></div>
  {after}
'''


def interview(qas, certs):
    """Interview and certification corner. qas: [(question, answer)]; certs: [(exam, objective)]."""
    q = ''.join(f'<details class="iv"><summary>{a}</summary><div>{b}</div></details>' for a, b in qas)
    c = ''.join(f'<li><b>{a}:</b> {b}</li>' for a, b in certs)
    return f'''  <h3 id="interview">Interview and certification corner</h3>
  <div class="ivs">{q}</div>
  <div class="certs"><b>Where this appears in certification exams</b><ul>{c}</ul></div>
'''


def cheatsheet(title, groups):
    """Printable one-page cheat sheet. groups: [(heading, [(command, meaning)])]."""
    g = ''.join(f'<div class="cs__g"><h4>{h}</h4><dl>' + ''.join(f'<dt><code>{E(c)}</code></dt><dd>{m}</dd>' for c, m in rows) + '</dl></div>' for h, rows in groups)
    return f'''  <section class="cs" id="cheatsheet" aria-label="Cheat sheet">
    <div class="cs__top"><h3>Cheat sheet: {title}</h3><button type="button" class="cs__print" onclick="document.body.classList.add('print-cs');window.print();setTimeout(function(){{document.body.classList.remove('print-cs')}},500)">Print this sheet</button></div>
    <div class="cs__grid">{g}</div>
    <p class="cs__wm">myphatshala.in · Linux</p>
  </section>
'''


def lab(title, intro, setup, tasks, solution, check):
    """Practice lab with checker. setup builds the lab; the student does the tasks; check.sh verifies.
    solution is used only at build time to prove that check.sh passes (and that it fails before)."""
    before_res = shlesson.run_sh(setup + '\n' + check, 'any').rstrip('\n')
    after_res = shlesson.run_sh(setup + '\n' + solution + '\n' + check).rstrip('\n')
    if 'FAIL' not in before_res or 'FAIL' in after_res:
        raise SystemExit('lab checker does not separate unsolved from solved: ' + title)
    t_ = ''.join(f'<li>{x}</li>' for x in tasks)
    return f'''  <div class="lab" id="lab"><h3>Practice lab: {title}</h3><p>{intro}</p>
    <p class="wx__label">Step 1 · Build the lab (copy into your terminal)</p>
    <div class="code" data-lang="bash" data-file="setup.sh"><pre><code>{E(setup.rstrip())}</code></pre></div>
    <p class="wx__label">Step 2 · Your tasks</p><ol>{t_}</ol>
    <p class="wx__label">Step 3 · Check your work (save as check.sh, run <code>bash check.sh</code>)</p>
    <div class="code" data-lang="bash" data-file="check.sh"><pre><code>{E(check.rstrip())}</code></pre><div class="output">{E(after_res)}</div></div>
    <p class="muted">The output above is what you see when every task is right (recorded). Before you start, every line says FAIL.</p>
    <details class="lab__sol"><summary>Show one possible solution</summary><div class="code" data-lang="bash" data-file="solution.sh"><pre><code>{E(solution.rstrip())}</code></pre></div></details>
  </div>
'''


# ================================================================ orientation blocks (6 Nov 2026, Vineeta's feedback:
# "kab kidhar se start ho raha hai, kya kab use karna hai, hook missing")
def hook(problem, outcomes, tag='The problem'):
    """Opening hook: a real problem in 2-3 lines + what you will be able to do by the end."""
    li = ''.join(f'<li>{o}</li>' for o in outcomes)
    return f'''<section class="hook" aria-label="Why this lesson">
  <span class="hook__tag">{tag}</span>
  <p class="hook__p">{problem}</p>
  <div class="hook__out"><b>By the end of this page you will be able to:</b><ul>{li}</ul></div>
</section>
'''


def roadmap(steps, short):
    """Start-here roadmap. steps: [(anchor, title, minutes, what)]; short: [anchor, ...] = the 10-minute path."""
    total = sum(m for _, _, m, _ in steps)
    items = ''.join(f'<li class="{"rm--short" if a in short else ""}"><a href="#{a}"><span class="rm__n">{i}</span><b>{t_}</b><small>{m} min · {w}</small></a></li>'
                    for i, (a, t_, m, w) in enumerate(steps, 1))
    return f'''<nav class="rmap" aria-label="How to read this lesson">
  <h2 class="rmap__h">Start here: how to read this page <small>(about {total} min)</small></h2>
  <ol class="rm">{items}</ol>
  <p class="rmap__short"><span class="rm__dot"></span> <b>Short on time?</b> Read only the highlighted steps (about {sum(m for a, _, m, _ in steps if a in short)} min), then come back for the rest.</p>
</nav>
'''


def decide(title, rows, hid='decide'):
    """'Which command?' decision chart near the top. rows: (I want to…, command, note)."""
    r = ''.join(f'<li><span class="dc__q">{q}</span><span class="dc__arrow" aria-hidden="true">→</span><code class="dc__a">{E(c)}</code><span class="dc__n">{n}</span></li>' for q, c, n in rows)
    return f'''  <div class="dchart" id="{hid}"><h3>{title}</h3><ul class="dc">{r}</ul></div>
'''


def usewhen(use, avoid):
    u = ''.join(f'<li>{x}</li>' for x in use)
    a = ''.join(f'<li>{x}</li>' for x in avoid)
    return f'<div class="uw"><div class="uw__yes"><b>✓ Use it when</b><ul>{u}</ul></div><div class="uw__no"><b>✗ Don’t use it when</b><ul>{a}</ul></div></div>'


def cmdcard_u(use, avoid):
    """cmdcard with 'use it when / don't use it when' given first: cmdcard_u(use, avoid)(cid, name, ...)."""
    return lambda *a, **k: cmdcard(*a, use=use, avoid=avoid, **k)


# ================================================================ editors (Module 4): real screens and real keystrokes
_KEYS = {'<Esc>': '\x1b', '<CR>': '\r', '<C-v>': '\x16', '<C-r>': '\x12', '<C-a>': '\x01', '<C-x>': '\x18', '<C-n>': '\x0e', '<C-o>': '\x0f', '<C-w>': '\x17', '<Tab>': '\t', '<BS>': '\x08'}
def _vkeys(k):
    for a, b in _KEYS.items():
        k = k.replace(a, b)
    return k


def vimrun(content, keys, name='notes.txt', show='file'):
    """Really run vim with typed keys (vim -s) on a file and return the file afterwards (show='file')
    or 'both' = before + after. keys use <Esc> <CR> <C-v> <C-r> notation."""
    import base64
    k = base64.b64encode(_vkeys(keys).encode()).decode()
    c = base64.b64encode(content.encode()).decode()
    script = (f"echo {c} | base64 -d > {name}\necho {k} | base64 -d > .keys\n"
              f"TERM=xterm vim -u NONE -N -i NONE -n -s .keys {name} > /dev/null 2>&1 < /dev/null\nrm -f .keys\ncat {name}")
    return shlesson.run_sh(script, 'any').rstrip('\n')


def tmux_screens(setup, cmd, steps, w=72, h=12, post=''):
    """Run an interactive program (nano, vim, less) inside tmux, send keys step by step and capture the real
    screen after each step. steps: list of tmux send-keys argument strings, e.g. "Down x" or "-l 'text'" or "C-o Enter".
    Returns a list of screens (one per step, plus the first screen)."""
    wrapped = f"TERM=xterm-256color {cmd}; echo; echo \"[back in the shell: {cmd.split()[0]} has closed]\"; sleep 60"
    lines = ['rm -f ~/.nanorc ~/.viminfo; rm -rf ~/.vim', setup, f"tmux -f /dev/null new-session -d -s ed -x {w} -y {h} '{wrapped}'", 'sleep 0.7',
             'echo @@SCREEN; tmux capture-pane -t ed -p']
    for s_ in steps:
        lines += [f'tmux send-keys -t ed {s_}', 'sleep 0.5', 'echo @@SCREEN; tmux capture-pane -t ed -p']
    lines += ['tmux kill-server 2>/dev/null; true']
    if post:
        lines += ['echo @@SCREEN', post]
    out = shlesson.run_sh('\n'.join(l for l in lines if l), 'any')
    return [s.strip('\n').rstrip() for s in out.split('@@SCREEN\n')[1:]]


def screens_block(title, intro, setup, cmd, steps, w=72, h=12, after=None, hid=None, what='the editor'):
    """A step-by-step real screen recording: [(keys shown to the student, tmux keys, note)]."""
    shots = tmux_screens(setup, cmd, [s[1] for s in steps], w, h, post=after or '')
    post_out = shots.pop() if after else ''
    items = [f'<li class="fv"><p class="fv__sit"><b>Start:</b> <code>{E(cmd)}</code></p><div class="code scr" data-lang="text" data-file="screen"><pre><code>{E(shots[0])}</code></pre></div></li>']
    for (show, _, note), shot in zip(steps, shots[1:]):
        items.append(f'<li class="fv"><p class="fv__sit"><b>Press</b> <kbd>{E(show)}</kbd> {note}</p><div class="code scr" data-lang="text" data-file="screen"><pre><code>{E(shot)}</code></pre></div></li>')
    aft = ''
    if after:
        res = post_out
        aft = f'<p class="wx__label">Afterwards (real output)</p><div class="code" data-lang="bash" data-file="Terminal"><pre><code>{E(after)}</code></pre><div class="output">{E(res)}</div></div>'
    return f'''  <h3{f' id="{hid}"' if hid else ''}>{title}</h3>
  <p>{intro} <span class="muted">Real screens: recorded by running {what} in a terminal on Ubuntu 24.04 and capturing the screen after each key.</span></p>
  <ol class="fvs">{''.join(items)}</ol>
  {aft}
'''
