#!/usr/bin/env python3
"""Wrap a lesson source file in the standard MyPhatshala lesson shell.
usage: gen.py SRC OUT_SITE_ROOT
SRC starts with <!--META {json} META--> followed by the body (parts 1-9).
Macros:
  <part n="1" id="story" label="The story"> ... </part>
  <riya>text</riya>  <arjun>text</arjun>      comic panels
  <exam>html</exam> <tip>html</tip> <warn>html</warn>   callouts (html is inside a <p>)
  {{AD}}                                         mid ad slot
"""
import json, re, sys, os, html

RIYA = '<svg viewBox="0 0 64 64"><rect width="64" height="64" fill="#FCE6D6"/><path d="M14 64c2-12 9-18 18-18s16 6 18 18z" fill="#2E5AAC"/><circle cx="32" cy="29" r="12" fill="#C68B5E"/><path d="M19 29c0-10 6-15 13-15s13 5 13 15c-3-5-7-8-13-8s-10 3-13 8z" fill="#2A1B14"/><path d="M43 27c3 6 3 14 0 20" stroke="#2A1B14" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="27.5" cy="30" r="1.5" fill="#2A1B14"/><circle cx="36.5" cy="30" r="1.5" fill="#2A1B14"/><path d="M28 35q4 3 8 0" stroke="#2A1B14" stroke-width="1.6" fill="none" stroke-linecap="round"/><circle cx="32" cy="24" r="1.2" fill="#D64545"/></svg>'
ARJUN = '<svg viewBox="0 0 64 64"><rect width="64" height="64" fill="#DDEFE6"/><path d="M12 64c2-12 10-18 20-18s18 6 20 18z" fill="#F4F1EA"/><path d="M28 46l4 8 4-8" fill="#2F7D5B"/><circle cx="32" cy="28" r="12" fill="#B57A50"/><path d="M20 26c0-8 5-13 12-13s12 5 12 13c-2-3-6-5-12-5s-10 2-12 5z" fill="#5A5A5A"/><path d="M22 32c1 8 5 11 10 11s9-3 10-11c-2 3-6 4-10 4s-8-1-10-4z" fill="#5A5A5A"/><circle cx="27" cy="29" r="3.4" fill="none" stroke="#1B2433" stroke-width="1.4"/><circle cx="37" cy="29" r="3.4" fill="none" stroke="#1B2433" stroke-width="1.4"/><path d="M30.4 29h3.2" stroke="#1B2433" stroke-width="1.4"/><circle cx="27" cy="29" r="1.1" fill="#1B2433"/><circle cx="37" cy="29" r="1.1" fill="#1B2433"/></svg>'
ICON = {
 'exam': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19V5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2zm0 0a2 2 0 0 1 2-2h12"/></svg>',
 'tip': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>',
 'warn': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18v.5"/></svg>',
}
TOC = [("story","The story"),("definition","Definition"),("types","Types and ways to use it"),("steps","Step by step"),
       ("animation","See it happen"),("real-world","Real-world use"),("run","Run the code"),("tracer","Line by line"),("worked","Worked examples"),
       ("quiz","Quiz and revision"),("practice","Practice problems"),("scenarios","Industry scenarios")]

def main(src, root):
    s = open(src, encoding='utf-8').read()
    m = re.match(r'\s*<!--META(.*?)META-->', s, re.S)
    meta = json.loads(m.group(1)); body = s[m.end():]
    if '{{WORKED}}' in body:
        body = body.replace('{{WORKED}}', open(src.replace('.html', '.worked.html'), encoding='utf-8').read())
    if '{{PRACTICE}}' in body:
        body = body.replace('{{PRACTICE}}', open(src.replace('.html', '.practice.html'), encoding='utf-8').read())
    body = re.sub(r'<part n="(\d+)" id="([\w-]+)" label="([^"]+)">',
                  lambda g: f'<!-- ======================= PART {g[1]}: {g[3].upper()} ======================= -->\n<section class="part" id="{g[2]}">\n  <span class="part-label"><b>{g[1]}</b> {g[3]}</span>', body)
    body = body.replace('</part>', '</section>')
    for who, av, side in (('riya', RIYA, ''), ('arjun', ARJUN, ' panel--right')):
        name = 'Riya' if who == 'riya' else 'Arjun Sir'
        body = re.sub(rf'<{who}>(.*?)</{who}>', lambda g: f'<div class="panel{side}">\n      <div class="avatar" aria-hidden="true">{av}</div>\n      <div class="bubble"><b class="who">{name}</b><p>{g[1]}</p></div>\n    </div>', body, flags=re.S)
    for k in ICON:
        body = re.sub(rf'<{k}>(.*?)</{k}>', lambda g: f'<div class="callout callout--{k}">{ICON[k]}<p>{g[1]}</p></div>', body, flags=re.S)
    body = body.replace('{{AD}}', '<div class="ad-slot" data-slot="mid"></div>')
    LV = {'easy': 'Easy', 'medium': 'Medium', 'business': 'Business problem'}
    cnt = [0]
    def prob(g):
        cnt[0] += 1
        return (f'<article class="prob"><div class="prob__head"><span class="prob__num">P{cnt[0]}</span>'
                f'<span class="prob__tag prob__tag--{g[1]}">{LV[g[1]]}</span><h4>{g[2]}</h4></div>')
    body = re.sub(r'<prob level="(easy|medium|business)" title="([^"]+)">', prob, body)
    body = body.replace('</prob>', '</article>')
    body = re.sub(r'<io>\s*<in>(.*?)</in>\s*<out>(.*?)</out>\s*</io>', lambda g: f'<div class="prob__io"><div><small>Input</small><pre>{g[1]}</pre></div><div><small>Expected output</small><pre>{g[2]}</pre></div></div>', body, flags=re.S)
    body = body.replace('<sol>', '<details class="prob__sol"><summary>Show solution and explanation</summary>').replace('</sol>', '</details>')
    assert 'id="scenarios"' in body and body.count('class="part"') == 9, 'needs 9 parts + scenarios'

    course, mod, les = meta['course'], meta['module'], meta['lesson']
    url = f"https://myphatshala.in/courses/{course}/{mod}/{les}/"
    e = html.escape
    ld = json.dumps({"@context":"https://schema.org","@type":"LearningResource","name":meta['title'],"learningResourceType":"Lesson",
        "educationalLevel":meta.get('level','Beginner'),"isAccessibleForFree":True,"inLanguage":"en",
        "isPartOf":{"@type":"Course","name":meta['courseTitle'],"provider":{"@type":"Organization","name":"MyPhatshala"}}}, ensure_ascii=False)
    R = '../../../../'
    toc = '\n'.join(f'      <li><a href="#{i}">{t}</a></li>' for i, t in TOC if i not in ('practice', 'worked') or f'id="{i}"' in body)
    chips = ''.join(f'<span>{c}</span>' for c in meta['chips'])
    out = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(meta['title'])} | MyPhatshala</title>
<meta name="description" content="{e(meta['description'])}">
<meta name="mp:minutes" content="{meta['minutes']}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(meta['ogTitle'])} · MyPhatshala">
<meta property="og:description" content="{e(meta['ogDescription'])}">
<link rel="icon" href="{R}assets/img/logo.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Fraunces:ital,opsz,wght@0,9..144,600;0,9..144,700;1,9..144,600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{R}assets/css/style.css">
<link rel="stylesheet" href="{R}assets/css/lesson.css">
<script src="{R}assets/js/config.js"></script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5906362345660187" crossorigin="anonymous"></script>
<script>try {{ const t = localStorage.getItem("mp-theme"); if (t) document.documentElement.dataset.theme = t; }} catch (e) {{}}</script>
<script type="application/ld+json">{ld}</script>
</head>
<body style="--track:{meta['track']}" data-lesson="{mod}/{les}" data-course-root="../../">
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{R}" aria-label="MyPhatshala home"><img src="{R}assets/img/logo.svg" width="34" height="34" alt=""><span>My<b>Phatshala</b></span></a>
    <nav class="nav" aria-label="Main">
      <a href="{R}#tracks">All courses</a>
      <a href="../../">{meta['courseTitle']} syllabus</a>
      <button class="theme-btn" id="theme-btn" aria-label="Toggle dark mode"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
    </nav>
  </div>
</header>

<main id="main">
<section class="lesson-hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="{R}">Home</a><span>›</span><a href="{R}#track-{meta['trackId']}">{meta['trackTitle']}</a><span>›</span><a href="../../">{meta['courseTitle']}</a><span>›</span><b>Lesson {meta['number']}</b></nav>
    <h1>{meta['title']}</h1>
    <p class="lead">{meta['lead']}</p>
    <div class="lesson-meta">{chips}</div>
  </div>
</section>

<div class="wrap lesson-layout">
<article class="lesson-main">
{body.strip()}

<nav class="lesson-nav" id="lesson-nav" aria-label="Lesson navigation"></nav>
<div class="ad-slot" data-slot="bottom"></div>
</article>

<aside class="lesson-side">
  <nav class="toc" aria-label="In this lesson">
    <h4>In this lesson</h4>
    <ol>
{toc}
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
    <div><h4>Learn</h4><a href="{R}#tracks">All courses</a><a href="../../">{meta['courseTitle']} syllabus</a></div>
    <div><h4>Site</h4><a href="{R}about.html">About</a><a href="{R}contact.html">Contact</a><a href="{R}privacy.html">Privacy policy</a><a href="{R}disclaimer.html">Disclaimer</a></div>
    <div class="copyright">© MyPhatshala. All lesson content, diagrams and animations are original. Please do not copy without permission.</div>
  </div>
</footer>

<script src="{R}data/courses/{course}.js"></script>
<script src="{R}assets/js/lesson.js"></script>
<script src="{R}assets/js/ads.js"></script>
<script src="{R}assets/js/site.js"></script>
</body>
</html>
'''
    path = os.path.join(root, 'courses', course, mod, les, 'index.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(out)
    print('wrote', path, len(out), 'bytes')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
