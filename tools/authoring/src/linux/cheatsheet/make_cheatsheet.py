#!/usr/bin/env python3
"""Builds courses/linux/cheat-sheet/index.html: every Linux command in the course with a one-line explanation.
Run from the site root:  python3 tools/authoring/src/linux/cheatsheet/make_cheatsheet.py
Commands live in commands.py; lesson links are resolved from courses/linux/course.json and shown only for live lessons."""
import json, html, re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
E = lambda s: html.escape(s, quote=True)
exec(open(os.path.join(HERE, "commands.py"), encoding="utf-8").read())

GROUPS = [
    ("nav", "Basics, help and moving around"), ("files", "Files and folders"), ("text", "Text processing"),
    ("shell", "Shell, redirection and variables"), ("script", "Shell scripting syntax"), ("users", "Users, groups and sudo"), ("perms", "Permissions"),
    ("proc", "Processes and jobs"), ("pkg", "Packages and archives"), ("storage", "Disks and storage"),
    ("net", "Networking and SSH"), ("services", "Services, logs and monitoring"), ("sec", "Security and kernel"),
]
SHORT = {"nav": "Basics", "files": "Files", "text": "Text", "shell": "Shell", "script": "Scripting", "users": "Users", "perms": "Permissions",
         "proc": "Processes", "pkg": "Packages", "storage": "Storage", "net": "Network", "services": "Services", "sec": "Security"}
course = json.load(open(os.path.join(ROOT, "courses/linux/course.json")))
mods = course["modules"]
def lesson(ref):
    m, l = (int(x) for x in ref.split("."))
    mo = mods[m - 1]; le = mo["lessons"][l - 1]
    return f"{mo['slug']}/{le['slug']}", le["title"]
counts = {g: sum(1 for c in CMDS if c["g"] == g) for g, _ in GROUPS}
assert all(counts.values()) and sum(counts.values()) == len(CMDS), counts

def row(c):
    path, title = lesson(c["ref"])
    q = " ".join([c["cmd"], c["what"], c["ex"]]).lower()
    return (f'<div class="cs-row" data-g="{c["g"]}" data-q="{E(q)}">'
            f'<code class="cs-cmd">{E(c["cmd"])}</code>'
            f'<span class="cs-what">{E(c["what"])}</span>'
            f'<button type="button" class="cs-ex" title="Copy this example" aria-label="Copy example: {E(c["ex"])}"><span aria-hidden="true">$ </span><code>{E(c["ex"])}</code></button>'
            f'<a class="cs-lesson" data-path="{path}/" href="../{path}/" title="{E(title)}">Lesson {c["ref"]}</a>'
            f'</div>')

sections = "\n".join(
    f'<section class="cs-sec" id="{g}" data-g="{g}"><h2>{E(n)} <small>({counts[g]})</small></h2><div class="cs-list">'
    + "".join(row(c) for c in CMDS if c["g"] == g) + '</div></section>' for g, n in GROUPS)
chips = '<button type="button" data-g="all" aria-pressed="true">All</button>' + "".join(
    f'<button type="button" data-g="{g}" aria-pressed="false">{SHORT[g]} <small>({counts[g]})</small></button>' for g, _ in GROUPS)

CSS = '''
.gt-toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:8px 0 6px}
.gl-search{display:flex;align-items:center;gap:8px;flex:1 1 280px;max-width:520px;padding:10px 14px;border:1px solid var(--line);border-radius:12px;background:var(--card)}
.gl-search svg{width:18px;height:18px;color:var(--ink-3);flex:none}
.gl-search input{border:0;outline:0;background:none;font:inherit;color:var(--ink);width:100%;min-width:0}
.gt-chips{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 14px}
.gt-chips button,.cs-print{font:inherit;font-size:.85rem;padding:5px 11px;border-radius:999px;border:1px solid var(--line);background:var(--card);color:var(--ink-2);cursor:pointer}
.gt-chips button[aria-pressed="true"]{background:var(--track);border-color:var(--track);color:#fff}
.cs-sec{margin:18px 0 6px}
.cs-sec h2{font-size:1.2rem;margin:0 0 8px}
.cs-sec h2 small{font-weight:400;color:var(--ink-3);font-size:.85rem}
.cs-list{border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--card)}
.cs-row{display:grid;grid-template-columns:minmax(150px,1.1fr) 2.2fr minmax(200px,1.7fr) auto;gap:6px 14px;align-items:center;padding:9px 14px;border-top:1px solid var(--line);min-width:0}
.cs-row:first-child{border-top:0}
.cs-row:nth-child(even){background:var(--paper-2)}
.cs-cmd{font-family:var(--font-code);font-weight:600;color:var(--track);background:none!important;border:0!important;padding:0!important;overflow-wrap:anywhere}
.cs-what{color:var(--ink);font-size:.95rem;min-width:0}
.cs-ex{all:unset;cursor:pointer;display:block;background:var(--board);color:var(--chalk);border-radius:8px;padding:5px 9px;font-family:var(--font-code);font-size:.8rem;overflow-wrap:anywhere;min-width:0}
.cs-ex span{color:var(--saffron)}
.cs-ex code{background:none!important;color:inherit!important;padding:0!important;border:0!important;font:inherit}
.cs-ex.copied::after{content:"  copied";color:var(--saffron)}
.cs-ex:focus-visible{outline:2px solid var(--track)}
.cs-lesson{font-size:.8rem;font-weight:700;white-space:nowrap}
.cs-lesson.soon{color:var(--ink-3);font-weight:400;pointer-events:none}
@media (max-width:760px){.cs-row{grid-template-columns:1fr auto}.cs-what,.cs-ex{grid-column:1/-1}.cs-cmd{grid-column:1}.cs-lesson{grid-column:2;grid-row:1}}
#gt-empty{display:none}
@media print{.site-header,.site-footer,.gt-toolbar,.gt-chips,.ad-slot,.cs-lesson,.lesson-hero .lead{display:none!important}.cs-row{break-inside:avoid;padding:4px 8px}.cs-ex{background:none;color:#000;border:1px solid #ccc}}
'''
JS = '''
(function () {
  const q = document.getElementById("gl-q"), rows = Array.from(document.querySelectorAll(".cs-row")), secs = Array.from(document.querySelectorAll(".cs-sec")), cnt = document.getElementById("gl-count");
  const chips = Array.from(document.querySelectorAll(".gt-chips button")); let g = "all";
  const live = new Set();
  try { (window.MP_COURSE.modules || []).forEach(m => m.lessons.forEach(l => { if (l.live) live.add(m.slug + "/" + l.slug + "/"); })); } catch (e) {}
  document.querySelectorAll(".cs-lesson").forEach(a => { if (!live.has(a.dataset.path)) { a.classList.add("soon"); a.removeAttribute("href"); a.textContent += " · soon"; } });
  function run() {
    const s = q.value.trim().toLowerCase(); let n = 0;
    rows.forEach(r => { const on = (g === "all" || r.dataset.g === g) && (!s || r.dataset.q.includes(s)); r.hidden = !on; if (on) n++; });
    secs.forEach(x => { x.hidden = !x.querySelector(".cs-row:not([hidden])"); });
    cnt.textContent = (s || g !== "all") ? n + " of " + rows.length + " commands" : rows.length + " commands";
    document.getElementById("gt-empty").style.display = n ? "none" : "block";
  }
  chips.forEach(b => b.addEventListener("click", () => { g = b.dataset.g; chips.forEach(x => x.setAttribute("aria-pressed", x === b)); run(); }));
  q.addEventListener("input", run);
  document.querySelectorAll(".cs-ex").forEach(b => b.addEventListener("click", () => {
    const t = b.querySelector("code").textContent;
    try { navigator.clipboard.writeText(t).then(() => { b.classList.add("copied"); setTimeout(() => b.classList.remove("copied"), 1200); }); } catch (e) {}
  }));
  document.getElementById("cs-print").addEventListener("click", () => window.print());
  run();
})();
'''
N = len(CMDS)
TITLE = "Linux commands cheat sheet: every command in one line"
DESC = f"Linux command cheat sheet: {N} commands from ls, cd and grep to chmod, systemctl, ssh and tar, each with what it does in one line, a ready-to-copy example and the lesson that teaches it."
page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(TITLE)} | MyPhatshala</title>
<meta name="description" content="{E(DESC)}">
<link rel="canonical" href="https://myphatshala.in/courses/linux/cheat-sheet/">
<meta property="og:title" content="Linux commands cheat sheet · MyPhatshala">
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
<body style="--track:{course.get('color') or '#0F766E'}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="../../../" aria-label="MyPhatshala home"><img src="../../../assets/img/logo.svg" width="34" height="34" alt=""><span>My<b>Phatshala</b></span></a>
    <nav class="nav" aria-label="Main">
      <a href="../../../#tracks">All courses</a>
      <a href="../">Linux syllabus</a>
      <button class="theme-btn" id="theme-btn" aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    </nav>
  </div>
</header>
<main id="main">
<section class="lesson-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="../../../">Home</a><span>›</span><a href="../../../#track-devops">DevOps and Tools</a><span>›</span><a href="../">Linux</a><span>›</span><b>Cheat sheet</b></nav>
    <h1>Linux commands cheat sheet</h1>
    <p class="lead">Every command in the Linux course on one page: <b>what it does in one line</b>, an example you can copy with one click, and the lesson that explains it fully. Search it, filter by topic, or print it. {N} commands in {len(GROUPS)} topics.</p>
    <div class="lesson-meta"><span>Linux</span><span>Reference</span><span>Beginner to Advanced</span><span>Free · no sign-up</span></div>
  </div>
</section>
<div class="wrap" style="padding-top:8px;padding-bottom:40px">
<div class="ad-slot" data-slot="top"></div>
<section class="part">
  <div class="gt-toolbar">
    <label class="search gl-search">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
      <input id="gl-q" type="search" placeholder="Search: copy, disk space, port, loop, array, grep…" aria-label="Search the cheat sheet">
    </label>
    <span class="muted" id="gl-count"></span>
    <button type="button" class="cs-print" id="cs-print">Print / save as PDF</button>
  </div>
  <div class="gt-chips" role="group" aria-label="Filter by topic">{chips}</div>
  <p class="muted">Tip: click an example to copy it. Need the meaning of a word? See the <a href="../glossary/">Linux glossary</a>.</p>
{sections}
  <p id="gt-empty" class="muted">No command matches. Try a shorter word, or clear the topic filter.</p>
</section>
<div class="ad-slot" data-slot="bottom"></div>
</div>
</main>
<footer class="site-footer">
  <div class="wrap">
    <div><h4>MyPhatshala</h4><p>Free programming and IT lessons that show what happens behind the screen.</p></div>
    <div><h4>Learn</h4><a href="../../../#tracks">All courses</a><a href="../">Linux syllabus</a><a href="../glossary/">Linux glossary</a></div>
    <div><h4>Site</h4><a href="../../../about.html">About</a><a href="../../../contact.html">Contact</a><a href="../../../privacy.html">Privacy policy</a><a href="../../../disclaimer.html">Disclaimer</a></div>
    <div class="copyright">© MyPhatshala. All lesson content, diagrams and animations are original. Please do not copy without permission.</div>
  </div>
</footer>
<script src="../../../data/courses/linux.js"></script>
<script>{JS}</script>
<script src="../../../assets/js/ads.js"></script>
<script src="../../../assets/js/site.js"></script>
</body>
</html>
'''
out = os.path.join(ROOT, "courses/linux/cheat-sheet/index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w", encoding="utf-8").write(page)
print(f"wrote {out}: {N} commands")
