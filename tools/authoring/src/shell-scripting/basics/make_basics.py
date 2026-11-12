#!/usr/bin/env python3
"""Builds courses/shell-scripting/basics-by-example/index.html: 110 Bash basics examples, every output really run.
Run as root from the site root: python3 tools/authoring/src/shell-scripting/basics/make_basics.py"""
import os, sys, html, json
HERE = os.path.dirname(os.path.abspath(__file__))
AUTH = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, AUTH)
import shlesson
ROOT = os.path.abspath(os.path.join(AUTH, '..', '..'))
E = lambda s: html.escape(s, quote=True)
_g = {}; exec(open(os.path.join(HERE, 'examples.py'), encoding='utf-8').read(), _g); EX = _g['EX']

TOPICS = [('var', 'Variables'), ('type', 'Data types'), ('op', 'Operators'), ('io', 'Input and output'), ('if', 'Conditions (if)'),
          ('case', 'case'), ('loop', 'Loops'), ('fn', 'Functions'), ('str', 'Strings'), ('prog', 'Small programs')]
LEVEL = {'v': 'Very basic', 'b': 'Basic', 'i': 'Intermediate'}
LINUX = {'var': '12-shell-environment/01-shell-variables-and-environment-variables-env', 'type': '12-shell-environment/13-arrays-indexed-and-associative',
         'op': '12-shell-environment/07-script-input-positional-parameters-read-and-arithmetic', 'io': '12-shell-environment/07-script-input-positional-parameters-read-and-arithmetic',
         'if': '12-shell-environment/08-decisions-if-test-and-case', 'case': '12-shell-environment/08-decisions-if-test-and-case',
         'loop': '12-shell-environment/09-loops-for-while-until-break-continue', 'fn': '12-shell-environment/10-functions-built-ins-and-tput',
         'str': '12-shell-environment/14-string-manipulation-and-printf', 'prog': '12-shell-environment/05-your-first-shell-script'}

cards = {}
for i, x in enumerate(EX, 1):
    out = shlesson.run_sh(x['code'], 'any').rstrip('\n')
    out = '\n'.join(l for l in out.split('\n') if not l.startswith('exit status:'))
    import re as _re; out = _re.sub(r'^line [0-9]+: ', 'bash: ', out.replace('/home/riya/script.sh: ', '').replace('/home/riya/lab', '~'), flags=_re.M)
    x['out'] = out
    q = ' '.join([x['title'], x['code'], x['why'], dict(TOPICS)[x['t']], LEVEL[x['l']]]).lower()
    cards.setdefault(x['t'], []).append(
        f'<article class="bx" id="ex{i}" data-t="{x["t"]}" data-l="{x["l"]}" data-q="{E(q)}">'
        f'<header><span class="bx-n">#{i}</span><h3>{E(x["title"])}</h3><span class="bx-l bx-l--{x["l"]}">{LEVEL[x["l"]]}</span></header>'
        f'<div class="code" data-lang="bash" data-file="script.sh"><pre><code>{E(x["code"])}</code></pre></div>'
        f'<p class="bx-ol">Output (really run)</p><pre class="bx-out">{E(out) if out else "(no output)"}</pre>'
        f'<p class="bx-why">{E(x["why"])}</p>'
        f'<button type="button" class="bx-copy" data-i="{i}">Copy code</button></article>')
    print(f'{i:3d} {x["title"][:40]:40s} -> {out[:60]!r}')

secs = '\n'.join(
    f'<section class="bx-sec" id="{t}" data-t="{t}"><h2>{E(n)} <small>({len(cards[t])})</small></h2>'
    f'<p class="muted">Full lesson: <a href="../../linux/{LINUX[t]}/">Linux Module 12</a>.</p><div class="bx-grid">' + ''.join(cards[t]) + '</div></section>'
    for t, n in TOPICS)
chips = '<button type="button" data-t="all" aria-pressed="true">All</button>' + ''.join(f'<button type="button" data-t="{t}" aria-pressed="false">{E(n)} <small>({len(cards[t])})</small></button>' for t, n in TOPICS)
lchips = '<button type="button" data-l="all" aria-pressed="true">All levels</button>' + ''.join(f'<button type="button" data-l="{k}" aria-pressed="false">{v} <small>({sum(1 for x in EX if x["l"] == k)})</small></button>' for k, v in LEVEL.items())
codes = json.dumps([x['code'] for x in EX], ensure_ascii=False).replace('</', '<\\/')

CSS = '''
.gt-toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:8px 0 6px}
.gl-search{display:flex;align-items:center;gap:8px;flex:1 1 280px;max-width:520px;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.gl-search svg{width:18px;height:18px;color:var(--ink-3);flex:none}
.gl-search input{border:0;outline:0;background:none;font:inherit;color:var(--ink);width:100%;min-width:0}
.gt-chips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.gt-chips button{font:inherit;font-size:.85rem;padding:5px 11px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--ink-2);cursor:pointer}
.gt-chips button[aria-pressed="true"]{background:var(--track);border-color:var(--track);color:#fff}
.bx-sec{margin:22px 0 6px}
.bx-sec h2{font-size:1.25rem;margin:0 0 2px}
.bx-sec h2 small{font-weight:400;color:var(--ink-3);font-size:.85rem}
.bx-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,420px),1fr));gap:12px;margin-top:8px}
.bx{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;min-width:0}
.bx header{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.bx h3{margin:0;font-size:1rem;flex:1 1 180px}
.bx-n{font-family:var(--font-code);font-size:.78rem;color:var(--ink-3)}
.bx-l{font-size:.7rem;padding:2px 8px;border-radius:999px;border:1px solid var(--line);white-space:nowrap}
.bx-l--v{background:var(--green-soft,#e6f4ea)}.bx-l--b{background:var(--blue-soft,#e8f0fe)}.bx-l--i{background:var(--saffron-soft,#fff3e0)}
.bx .code{margin:0}
.bx .code pre{margin:0;max-width:100%;overflow-x:auto}
.bx-ol{margin:2px 0 0;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase;color:var(--track)}
.bx-out{margin:0;background:var(--paper-2);border:1px solid var(--line);border-radius:8px;padding:7px 10px;font-family:var(--font-code);font-size:.82rem;white-space:pre-wrap;overflow-wrap:anywhere;color:var(--ink)}
.bx-why{margin:0;font-size:.92rem;color:var(--ink-2)}
.bx-copy{align-self:flex-start;font:inherit;font-size:.8rem;padding:4px 10px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--ink-2);cursor:pointer}
#bx-empty{display:none}
'''
JS = '''
(function(){
  const CODES = %s;
  const q=document.getElementById("gl-q"), cards=[...document.querySelectorAll(".bx")], secs=[...document.querySelectorAll(".bx-sec")], cnt=document.getElementById("gl-count");
  const tc=[...document.querySelectorAll("#t-chips button")], lc=[...document.querySelectorAll("#l-chips button")]; let t="all", l="all";
  function run(){ const s=q.value.trim().toLowerCase(); let n=0;
    cards.forEach(c=>{const on=(t==="all"||c.dataset.t===t)&&(l==="all"||c.dataset.l===l)&&(!s||c.dataset.q.includes(s)); c.hidden=!on; if(on)n++;});
    secs.forEach(x=>{x.hidden=!x.querySelector(".bx:not([hidden])");});
    cnt.textContent=n+" of "+cards.length+" examples"; document.getElementById("bx-empty").style.display=n?"none":"block"; }
  tc.forEach(b=>b.addEventListener("click",()=>{t=b.dataset.t; tc.forEach(x=>x.setAttribute("aria-pressed",x===b)); run();}));
  lc.forEach(b=>b.addEventListener("click",()=>{l=b.dataset.l; lc.forEach(x=>x.setAttribute("aria-pressed",x===b)); run();}));
  q.addEventListener("input",run);
  document.querySelectorAll(".bx-copy").forEach(b=>b.addEventListener("click",()=>{ try{navigator.clipboard.writeText(CODES[b.dataset.i-1]).then(()=>{b.textContent="Copied";setTimeout(()=>b.textContent="Copy code",1200);});}catch(e){} }));
  run();
})();
''' % codes

N = len(EX)
TITLE = 'Bash basics by example: variables, data types, operators, conditions, case, loops and functions'
DESC = f'{N} Bash examples from very basic to intermediate: variables, data types, arrays, operators, input and output, if, case, loops, functions, strings and small programs, each with its real output and a one-line explanation.'
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(TITLE)} | MyPhatshala</title>
<meta name="description" content="{E(DESC)}">
<link rel="canonical" href="https://myphatshala.in/courses/shell-scripting/basics-by-example/">
<meta property="og:title" content="Bash basics by example · MyPhatshala">
<meta property="og:description" content="{E(DESC)}">
<link rel="icon" href="../../../assets/img/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../../../assets/css/style.css">
<link rel="stylesheet" href="../../../assets/css/lesson.css">
<style>{CSS}</style>
<script src="../../../assets/js/config.js"></script>
<script>try {{ const t = localStorage.getItem("mp-theme"); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5906362345660187" crossorigin="anonymous"></script>
</head>
<body style="--track:#0F766E">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../../../" aria-label="MyPhatshala home"><img src="../../../assets/img/logo.svg" width="34" height="34" alt=""><span>My<b>Phatshala</b></span></a>
    <nav class="nav" aria-label="Main">
      <a href="../../../#tracks">All courses</a>
      <a href="../">Shell Scripting syllabus</a>
      <button class="theme-btn" id="theme-btn" aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    </nav>
  </div>
</header>
<main id="main">
<section class="lesson-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="../../../">Home</a><span>›</span><a href="../../../#track-devops">DevOps and Tools</a><span>›</span><a href="../">Shell Scripting (Bash)</a><span>›</span><b>Basics by example</b></nav>
    <h1>Bash basics by example</h1>
    <p class="lead">{N} small examples, from <b>very basic</b> to <b>intermediate</b>: variables, data types, operators, input and output, conditions, case, loops, functions, strings and small programs. Every output below was <b>really run</b> on our Linux machine. Filter by topic or level, search, and copy any example to try in your terminal.</p>
    <div class="lesson-meta"><span>Shell Scripting</span><span>Reference</span><span>Very basic → Intermediate</span><span>Free · no sign-up</span></div>
  </div>
</section>
<div class="wrap" style="padding-top:8px;padding-bottom:40px">
<div class="ad-slot" data-slot="top"></div>
<section class="part">
  <div class="gt-toolbar">
    <label class="search gl-search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
      <input id="gl-q" type="search" placeholder="Search: array, while, function, %, uppercase…" aria-label="Search the examples">
    </label>
    <span class="muted" id="gl-count"></span>
  </div>
  <div class="gt-chips" id="t-chips" role="group" aria-label="Filter by topic">{chips}</div>
  <div class="gt-chips" id="l-chips" role="group" aria-label="Filter by level">{lchips}</div>
  <p class="muted">New to the shell? Start with the Very basic filter. Want the full explanations? Each topic links to its Linux lesson; for real-world scripts continue with <a href="../01-script-craft/01-anatomy-of-a-real-script/">Lesson 1.1</a>.</p>
{secs}
  <p id="bx-empty" class="muted">No example matches. Clear the filters or try a shorter word.</p>
</section>
<div class="ad-slot" data-slot="bottom"></div>
</div>
</main>
<footer class="site-footer">
  <div class="wrap">
    <div><h4>MyPhatshala</h4><p>Free programming and IT lessons that show what happens behind the screen.</p></div>
    <div><h4>Learn</h4><a href="../../../#tracks">All courses</a><a href="../">Shell Scripting syllabus</a><a href="../../linux/cheat-sheet/">Linux cheat sheet</a></div>
    <div><h4>Site</h4><a href="../../../about.html">About</a><a href="../../../contact.html">Contact</a><a href="../../../privacy.html">Privacy policy</a><a href="../../../disclaimer.html">Disclaimer</a></div>
    <div class="copyright">© MyPhatshala. All lesson content, diagrams and animations are original. Please do not copy without permission.</div>
  </div>
</footer>
<script>{JS}</script>
<script src="../../../assets/js/ads.js"></script>
<script src="../../../assets/js/site.js"></script>
</body>
</html>
'''
out = os.path.join(ROOT, 'courses/shell-scripting/basics-by-example/index.html')
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, 'w', encoding='utf-8').write(page)
print('wrote', out, N, 'examples')
