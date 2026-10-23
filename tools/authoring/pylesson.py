#!/usr/bin/env python3
"""Build one Python-based lesson page (Big Data track and other Python courses).

usage: python3 tools/authoring/pylesson.py SRC_DIR [SITE_ROOT]

SRC_DIR/spec.py defines plain Python values (see src/big-data-fundamentals/ for examples):
  COURSE   dict(id, title, track, track_anchor, color)
  META     dict(module, lesson, n, module_label, title, desc, og_desc, minutes, level, lead, chips=[...])
  BODY     html for parts 1-6 (story ... real-world use)
  RUN      dict(heading, intro, code, anno=[(code, html)], tasks=[dict(label, hint, code, expect=None|'error')])
  PCRUN    optional dict(heading, intro, items=[dict(title, cmd, output, note)])  "Run on your PC" panels
  TRACE    dict(heading, intro, code, notes={line | (line, k): "Phase :: html"})
  WORKED_INTRO, EXAMPLES = [dict(tag, title, problem, inp, approach=[...], code, notes={...}, tryit)]
  QUIZ     [dict(q, options, answer, why)]        (q and options are plain text)
  REVISION [html, ...]   FAQ [(question, answer_html), ...]
  PRACTICE_INTRO, PROBLEMS = [dict(level: easy|medium|business, title, stmt, inp, code, explain)]
  SCN_INTRO, SCENARIOS (html)

Every program is really run with python3. Expected outputs are taken from the run, never typed by hand.
Traces are recorded with sys.settrace: each step shows the line that just ran, the frames and variables
after it, containers (list/dict/tuple/set) as numbered objects, and the text it printed.
A note 'Phase :: = text' replaces the automatic description instead of adding to it.
"""
import sys, os, io, json, html, runpy, subprocess, types

E = html.escape
HERE = os.path.dirname(os.path.abspath(__file__))


def run_py(code, expect=None):
    p = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=30)
    if expect == 'error':
        if p.returncode == 0:
            raise SystemExit('expected an error but program ran fine:\n' + code)
        return p.stdout + p.stderr.strip().splitlines()[-1] + '\n'
    if p.returncode != 0:
        raise SystemExit('program failed:\n' + code + '\n' + p.stderr)
    return p.stdout


# ---------------------------------------------------------------- tracer
CONTAINERS = (list, dict, tuple, set)


def short(s, n=70):
    return s if len(s) <= n else s[:n - 1] + '…'


class Recorder:
    def __init__(self, code):
        self.code = code
        self.events = []
        self.ids = {}

    def oid(self, o):
        k = id(o)
        if k not in self.ids:
            self.ids[k] = (len(self.ids) + 1, o)
        return self.ids[k][0]

    def val(self, v, heap):
        if isinstance(v, CONTAINERS):
            n = self.oid(v)
            heap.add(n)
            return f'→ {type(v).__name__} #{n}'
        if isinstance(v, types.FunctionType):
            return f'function {v.__name__}()'
        if isinstance(v, float):
            return repr(round(v, 4))
        return short(repr(v))

    def obj_desc(self, n):
        o = self.ids[[k for k, (m, _) in self.ids.items() if m == n][0]][1]
        sub = set()
        if isinstance(o, dict):
            body = ', '.join(f'{short(repr(k), 20)}: {self.val(v, sub)}' for k, v in o.items())
            txt = '{' + body + '}'
        elif isinstance(o, (list, tuple, set)):
            items = sorted(o, key=repr) if isinstance(o, set) else o
            body = ', '.join(self.val(v, sub) for v in items)
            txt = {'list': '[%s]', 'tuple': '(%s)', 'set': '{%s}'}[type(o).__name__] % body
        else:
            txt = repr(o)
        return f'#{n} {type(o).__name__} ({len(o)})', short(txt, 90), sub

    def snap(self, frame):
        frames = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == '<lesson>' and not (f.f_code.co_name.startswith('<') and f.f_code.co_name != '<module>'):
                frames.append(f)
            f = f.f_back
        frames.reverse()
        heap, stack = set(), []
        for f in frames:
            name = 'module (global)' if f.f_code.co_name == '<module>' else f.f_code.co_name + '()'
            loc = f.f_globals if f.f_code.co_name == '<module>' else f.f_locals
            vs = []
            for k, v in list(loc.items()):
                if k.startswith('__') or k.startswith('.') or isinstance(v, types.ModuleType) or k == 'Counter_':
                    continue
                if isinstance(v, type):
                    continue
                vs.append([k, self.val(v, heap)])
            stack.append({'frame': name, 'vars': vs})
        # follow references inside containers
        seen, todo, objs = set(), sorted(heap), []
        while todo:
            n = todo.pop(0)
            if n in seen:
                continue
            seen.add(n)
            head, txt, sub = self.obj_desc(n)
            objs.append((n, f'<b>{E(head)}</b> {E(txt)}'))
            todo += sorted(sub - seen)
        objs.sort()
        return stack, [o for _, o in objs]

    def run(self):
        out = io.StringIO()
        g = {'__name__': '__main__', '__builtins__': __builtins__}
        code = compile(self.code, '<lesson>', 'exec')

        def tr(frame, ev, arg):
            if frame.f_code.co_filename != '<lesson>':
                return None
            if frame.f_code.co_name.startswith('<') and frame.f_code.co_name != '<module>':
                return tr
            if ev in ('line', 'return', 'call'):
                st, hp = self.snap(frame)
                self.events.append(dict(ev=ev, line=frame.f_lineno, fn=frame.f_code.co_name,
                                        stack=st, heap=hp, out=len(out.getvalue()),
                                        ret=self.val(arg, set()) if ev == 'return' else None,
                                        caller=(frame.f_back.f_lineno if frame.f_back is not None and frame.f_back.f_code.co_filename == '<lesson>' and frame.f_code.co_name != '<module>' else None)))
            return tr

        old = sys.stdout
        sys.stdout = out
        sys.settrace(tr)
        try:
            exec(code, g)
        finally:
            sys.settrace(None)
            sys.stdout = old
        self.text = out.getvalue()
        return self


def auto_note(prev, cur, ev):
    bits = []
    pf = prev['stack'] if prev else []
    cf = cur['stack']
    if len(cf) > len(pf) and (prev is not None or len(cf) > 1):
        top = cf[-1]
        ps = ', '.join(f'<code>{E(n)}</code> = {E(v)}' for n, v in top['vars'])
        bits.append(f'<code>{E(top["frame"])}</code> is called: a new frame is pushed' + (f' with {ps}' if ps else '') + '.')
        return ' '.join(bits), top['vars'][-1][0] if top['vars'] else None
    if len(cf) < len(pf):
        bits.append(f'<code>{E(pf[-1]["frame"])}</code> returns {E(ev.get("ret") or "")} and its frame is popped.')
    newv = None
    if cf:
        before = dict(map(tuple, pf[len(cf) - 1]['vars'])) if len(pf) >= len(cf) and pf else {}
        for n, v in cf[-1]['vars']:
            if before.get(n) != v:
                if n in before:
                    bits.append(f'<code>{E(n)}</code> changes to {E(v)}.')
                else:
                    bits.append(f'<code>{E(n)}</code> is created: {E(v)}.')
                newv = n
    if prev:
        pheap = set(prev['heap'])
        pnums = {h.replace('<b>', '').split(' ')[0] for h in prev['heap']}
        for h in cur['heap']:
            if h not in pheap:
                head, body_ = h.split('</b>')[0].replace('<b>', ''), h.split('</b>')[1].strip()
                if head.split(' ')[0] in pnums:
                    bits.append(f'Object {head.split(" (")[0]} now holds {body_}')
                else:
                    bits.append(f'A new {head.split(" ")[1]} object ({head.split(" ")[0]}) is created: {body_}')
    return ' '.join(bits), newv


def build_trace(spec_trace):
    code = spec_trace['code'].rstrip('\n') + '\n'
    notes = spec_trace.get('notes', {})
    rec = Recorder(code).run()
    ev = rec.events
    steps, count, prev = [], {}, None
    for i, e in enumerate(ev):
        is_ret = e['ev'] == 'return' and e['fn'] != '<module>' and e['caller']
        if e['ev'] != 'line' and not is_ret:
            continue
        after = ev[i + 1] if i + 1 < len(ev) else e
        line = e['caller'] if is_ret else e['line']
        snap = {'stack': after['stack'], 'heap': after['heap']}
        if is_ret:
            a = f'<code>{E(e["fn"])}()</code> returns <b>{E(e["ret"])}</b> and its frame is popped. The caller continues on this line with that value.'
            newv = None
            n = None
        else:
            count[line] = count.get(line, 0) + 1
            k = count[line]
            a, newv = auto_note(prev, snap, after)
            src = code.split('\n')[line - 1].strip()
            if src.startswith(('if ', 'elif ', 'while ')):
                nxt = next((x for x in ev[i + 1:] if x['ev'] == 'line' and x['fn'] == e['fn']), None)
                ok = nxt is not None and nxt['line'] == line + 1
                a = ('The condition is <b>True</b>, so the indented block runs.' if ok else 'The condition is <b>False</b>, so the indented block is skipped.') + (' ' + a if a else '')
            if not a:
                if src.startswith(('for ', 'while ')):
                    nxt = next((x for x in ev[i + 1:] if x['ev'] == 'line' and x['fn'] == e['fn']), None)
                    if nxt is not None and nxt['line'] == line + 1:
                        a = 'The loop takes the next item (it has the same value as the previous one).'
                    else:
                        a = 'Nothing is left to loop over, so the loop ends and Python moves on.'
                elif src.startswith(('if ', 'elif ')):
                    a = 'The condition is checked.'
                elif src.startswith('return'):
                    a = 'The return value is worked out and handed back to the caller.'
                elif src.startswith('print('):
                    a = 'The text is printed to the console.'
                elif src == 'continue':
                    a = '<code>continue</code> skips the rest of this round and jumps back to the loop for the next item.'
                elif src == 'break':
                    a = '<code>break</code> leaves the loop immediately.'
                elif src.startswith('def '):
                    a = 'The function is defined (not run yet).'
            n = notes.get((line, k)) or (notes.get(line) if k == 1 else None)
        phase, note = ('Return' if is_ret else 'Python'), a
        if n:
            phase, txt = n.split('::', 1) if '::' in n else ('Python', n)
            phase, txt = phase.strip(), txt.strip()
            note = txt[1:].strip() if txt.startswith('=') else (txt + (' ' + a if a else ''))
        o0, o1 = e['out'], after['out']
        step = {'line': line, 'phase': phase, 'note': note or 'This line runs.', 'stack': snap['stack'], 'heap': snap['heap']}
        if o1 > o0:
            step['out'] = rec.text[o0:o1]
        if newv:
            step['newVar'] = newv
        steps.append(step)
        prev = dict(snap, ev=after)
    if len(steps) > 70:
        raise SystemExit(f'trace too long ({len(steps)} steps); shorten the program:\n' + spec_trace['code'][:300])
    return {'lang': 'python', 'code': code.rstrip('\n').split('\n'), 'steps': steps}, rec.text


def jscript(obj):
    return '<script type="application/json">' + json.dumps(obj, ensure_ascii=False, indent=1).replace('</', '<\\/') + '</script>'


def codebox(code, out=None, lang='python', file='main.py'):
    o = f'<div class="output">{E(out.rstrip())}</div>' if out else ''
    return f'<div class="code" data-lang="{lang}" data-file="{E(file)}"><pre><code>{E(code.rstrip())}</code></pre>{o}</div>'


# ---------------------------------------------------------------- page
LVL = {'b': '<span class="lvl lvl--b">Beginner</span>', 'i': '<span class="lvl lvl--i">Intermediate</span>', 'a': '<span class="lvl lvl--a">Advanced</span>'}

def page(S, root):
    C, M = S['COURSE'], S['META']
    up = '../../../../'
    chips = ''.join(f'<span>{c}</span>' for c in M['chips'])
    parts = []
    # ---- part 7
    R = S['RUN']
    main_out = run_py(R['code'])
    tasks = []
    for t in R['tasks']:
        run_py(t['code'], t.get('expect'))
        tasks.append({'label': t['label'], 'hint': t['hint'], 'code': t['code']})
    anno = ''.join(f'<li><code>{E(c)}</code><span>{h}</span></li>' for c, h in R.get('anno', []))
    p7 = f'''<section class="part" id="run">
  <span class="part-label"><b>7</b> Run the code</span>
  <h2>{R['heading']}</h2>
  {R['intro']}
  {codebox(R['code'], main_out)}
  <ul class="anno">{anno}</ul>
  <div class="runner">
    {jscript({'lang': 'python', 'file': 'main.py', 'tasks': tasks})}
  </div>
'''
    if S.get('PCRUN'):
        P = S['PCRUN']
        p7 += f'''  <h3 id="pc">{P['heading']}</h3>
  {P['intro']}
'''
        for it in P['items']:
            p7 += f'''  <div class="pcrun"><h4>{it['title']}</h4>
  {codebox(it['cmd'], it['output'], lang='bash', file=it.get('file', 'Terminal'))}
  <p class="muted">{it['note']}</p></div>
'''
    p7 += '</section>\n'
    # ---- part 8
    T = S['TRACE']
    tj, _ = build_trace(T)
    wx = ''
    for i, ex in enumerate(S['EXAMPLES'], 1):
        out = run_py(ex['code'])
        ej, _ = build_trace({'code': ex['code'], 'notes': ex.get('notes', {})})
        appr = ''.join(f'<li>{a}</li>' for a in ex['approach'])
        wx += f'''  <article class="wx">
    <div class="wx__head"><span class="wx__num">Example {i}</span>{LVL.get(ex.get('level'), '')}<span class="wx__tag">{ex['tag']}</span></div>
    <h4>{ex['title']}</h4>
    <div class="wx__problem"><p class="wx__label">Problem statement</p>{ex['problem']}</div>
    <div class="prob__io"><div><small>Input</small><pre>{E(ex['inp'])}</pre></div><div><small>Expected output</small><pre>{E(out.rstrip())}</pre></div></div>
    <div class="wx__approach"><p class="wx__label">Approach</p><ol>{appr}</ol></div>
    <p class="wx__label">Solution: run it live</p>
    <div class="runner">
    {jscript({'lang': 'python', 'file': 'main.py', 'tasks': [{'label': 'Solution', 'hint': ex['tryit'], 'code': ex['code']}]})}
    </div>
    <p class="wx__label">What happens in memory, step by step</p>
    <p class="wx__how">Recorded from a real Python run: press <b>Next</b> to execute one line at a time. Watch variables change in each frame, and lists and dictionaries (numbered #1, #2 …) fill up as objects.</p>
    <div class="tracer">
    {jscript(ej)}
    </div>
  </article>
'''
    p8 = f'''<section class="part" id="tracer">
  <span class="part-label"><b>8</b> Line by line</span>
  <h2>{T['heading']}</h2>
  {T['intro']}
  <div class="tracer">
    {jscript(tj)}
  </div>

<h3 id="worked">Worked examples: real problems, solved and traced in memory</h3>
  <p class="wx-intro">{S['WORKED_INTRO']}</p>
{wx}</section>
'''
    # ---- part 9
    rev = ''.join(f'<li>{r}</li>' for r in S['REVISION'])
    faq = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>\n    ' for q, a in S['FAQ'])
    probs = ''
    lab = {'easy': 'Easy', 'medium': 'Medium', 'advanced': 'Advanced', 'business': 'Business problem'}
    for i, p in enumerate(S['PROBLEMS'], 1):
        out = run_py(p['code'])
        probs += f'''    <article class="prob"><div class="prob__head"><span class="prob__num">P{i}</span><span class="prob__tag prob__tag--{p['level']}">{lab[p['level']]}</span><h4>{p['title']}</h4></div>
      <p>{p['stmt']}</p>
      <div class="prob__io"><div><small>Input</small><pre>{E(p['inp'])}</pre></div><div><small>Expected output</small><pre>{E(out.rstrip())}</pre></div></div>
      <details class="prob__sol"><summary>Show solution and explanation</summary>
        {codebox(p['code'], out)}
        <p><b>How it works:</b> {p['explain']}</p>
      </details>
    </article>
'''
    p9 = f'''<section class="part" id="quiz">
  <span class="part-label"><b>9</b> Quiz and revision</span>
  <h2>Check yourself</h2>
  <div class="quiz">
    {jscript(S['QUIZ'])}
  </div>

  <h3>Quick revision</h3>
  <div class="revision">
    <h3>Lesson {M['n']} in one screen</h3>
    <ul>{rev}</ul>
  </div>

  <h3>Interview and viva questions</h3>
  <div class="faq">
    {faq}
  </div>

  <h3 id="practice">Practice problems</h3>
  <p class="prob-intro">{S['PRACTICE_INTRO']}</p>
  <div class="probs">
{probs}  </div>

  <h3 id="scenarios">Real-world scenario questions (asked in company interviews)</h3>
  <p class="scn-intro">{S['SCN_INTRO']}</p>
  <div class="scenarios">
{S['SCENARIOS']}
  </div>
</section>
'''
    ld = {"@context": "https://schema.org", "@type": "LearningResource", "name": M['title'], "learningResourceType": "Lesson",
          "educationalLevel": M['level'], "isAccessibleForFree": True, "inLanguage": "en",
          "isPartOf": {"@type": "Course", "name": C['title'], "provider": {"@type": "Organization", "name": "MyPhatshala"}}}
    url = f"https://myphatshala.in/courses/{C['id']}/{M['module']}/{M['lesson']}/"
    toc_pc = '<li><a href="#pc">Run on your PC</a></li>' if S.get('PCRUN') else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(M['title'])} | MyPhatshala</title>
<meta name="description" content="{E(M['desc'])}">
<meta name="mp:minutes" content="{M['minutes']}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{E(M['title'])} · MyPhatshala">
<meta property="og:description" content="{E(M['og_desc'])}">
<link rel="icon" href="{up}assets/img/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/css/style.css">
<link rel="stylesheet" href="{up}assets/css/lesson.css">
<script src="{up}assets/js/config.js"></script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5906362345660187" crossorigin="anonymous"></script>
<script>try {{ const t = localStorage.getItem("mp-theme"); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body style="--track:{C['color']}" data-lesson="{M['module']}/{M['lesson']}" data-course-root="../../">
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{up}" aria-label="MyPhatshala home"><img src="{up}assets/img/logo.svg" width="34" height="34" alt=""><span>My<b>Phatshala</b></span></a>
    <nav class="nav" aria-label="Main">
      <a href="{up}#tracks">All courses</a>
      <a href="../../">{E(C['title'])} syllabus</a>
      <button class="theme-btn" id="theme-btn" aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    </nav>
  </div>
</header>

<main id="main">
<section class="lesson-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{up}">Home</a><span>›</span><a href="{up}#track-{C['track_anchor']}">{E(C['track'])}</a><span>›</span><a href="../../">{E(C['title'])}</a><span>›</span><b>Lesson {M['n']}</b></nav>
    <h1>{E(M['title'])}</h1>
    <p class="lead">{M['lead']}</p>
    <div class="lesson-meta"><span>{M['module_label']}</span><span>⏱ {M['minutes']} min</span><span>{M['level']}</span>{chips}<span>{len(S['PROBLEMS'])} practice problems</span></div>
  </div>
</section>

<div class="wrap lesson-layout">
<article class="lesson-main">
{S['BODY']}

<div class="ad-slot" data-slot="mid"></div>

{p7}
{p8}
{p9}
<nav class="lesson-nav" id="lesson-nav" aria-label="Lesson navigation"></nav>
<div class="ad-slot" data-slot="bottom"></div>
</article>

<aside class="lesson-side">
  <nav class="toc" aria-label="In this lesson">
    <h4>In this lesson</h4>
    <ol>
      <li><a href="#story">The story</a></li>
      <li><a href="#definition">Definition</a></li>{'<li><a href="#levels">Beginner → Advanced</a></li>' if 'id="levels"' in S['BODY'] else ''}
      <li><a href="#types">Types and ways to use it</a></li>
      <li><a href="#steps">Step by step</a></li>
      <li><a href="#animation">See it happen</a></li>
      <li><a href="#real-world">Real-world use</a></li>
      <li><a href="#run">Run the code</a></li>{toc_pc}
      <li><a href="#tracer">Line by line</a></li>
      <li><a href="#worked">Worked examples</a></li>
      <li><a href="#quiz">Quiz and revision</a></li>
      <li><a href="#practice">Practice problems</a></li>
      <li><a href="#scenarios">Industry scenarios</a></li>
    </ol>
  </nav>
  <div class="ad-slot" data-slot="side"></div>
  <div class="outline" id="outline"></div>
</aside>
</div>
</main>

<footer class="site-footer">
  <div class="wrap">
    <div><h4>MyPhatshala</h4><p>Free programming and IT lessons that show what happens behind the screen.</p></div>
    <div><h4>Learn</h4><a href="{up}#tracks">All courses</a><a href="../../">{E(C['title'])} syllabus</a></div>
    <div><h4>Site</h4><a href="{up}about.html">About</a><a href="{up}contact.html">Contact</a><a href="{up}privacy.html">Privacy policy</a><a href="{up}disclaimer.html">Disclaimer</a></div>
    <div class="copyright">© MyPhatshala. All lesson content, diagrams and animations are original. Please do not copy without permission.</div>
  </div>
</footer>

<script src="{up}data/courses/{C['id']}.js"></script>
<script src="{up}assets/js/lesson.js"></script>
<script src="{up}assets/js/ads.js"></script>
<script src="{up}assets/js/site.js"></script>
</body>
</html>
'''


def main():
    src = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath(os.path.join(HERE, '..', '..'))
    shared = os.path.join(os.path.dirname(os.path.dirname(src)), 'course.py')
    S = runpy.run_path(shared) if os.path.exists(shared) else {}
    S.update(runpy.run_path(os.path.join(src, 'spec.py'), init_globals=S))
    M = S['META']
    out = os.path.join(root, 'courses', S['COURSE']['id'], M['module'], M['lesson'], 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    html_ = page(S, root)
    if 'class="csim"' in html_:   # Cluster Playground used on this page
        up = '../../../../'
        html_ = html_.replace(f'<link rel="stylesheet" href="{up}assets/css/lesson.css">', f'<link rel="stylesheet" href="{up}assets/css/lesson.css">\n<link rel="stylesheet" href="{up}assets/css/cluster-sim.css">')
        html_ = html_.replace(f'<script src="{up}assets/js/lesson.js"></script>', f'<script src="{up}assets/js/lesson.js"></script>\n<script src="{up}assets/js/cluster-sim.js"></script>')
    open(out, 'w', encoding='utf-8').write(html_)
    print('wrote', os.path.relpath(out, root), f'({len(html_)//1024} KB)')


if __name__ == '__main__':
    main()
