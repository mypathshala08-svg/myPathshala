# Shared settings for every Apache Spark and PySpark lesson (read by tools/authoring/pylesson.py)
COURSE = dict(id='spark-pyspark', title='Apache Spark and PySpark', track='Big Data Engineering',
              track_anchor='big-data', color='#B45309')

ARJUN = '<svg viewBox="0 0 64 64"><rect width="64" height="64" fill="#DDEFE6"/><path d="M12 64c2-12 10-18 20-18s18 6 20 18z" fill="#F4F1EA"/><path d="M28 46l4 8 4-8" fill="#2F7D5B"/><circle cx="32" cy="28" r="12" fill="#B57A50"/><path d="M20 26c0-8 5-13 12-13s12 5 12 13c-2-3-6-5-12-5s-10 2-12 5z" fill="#5A5A5A"/><path d="M22 32c1 8 5 11 10 11s9-3 10-11c-2 3-6 4-10 4s-8-1-10-4z" fill="#5A5A5A"/><circle cx="27" cy="29" r="3.4" fill="none" stroke="#1B2433" stroke-width="1.4"/><circle cx="37" cy="29" r="3.4" fill="none" stroke="#1B2433" stroke-width="1.4"/><path d="M30.4 29h3.2" stroke="#1B2433" stroke-width="1.4"/><circle cx="27" cy="29" r="1.1" fill="#1B2433"/><circle cx="37" cy="29" r="1.1" fill="#1B2433"/></svg>'
RIYA = '<svg viewBox="0 0 64 64"><rect width="64" height="64" fill="#FCE6D6"/><path d="M14 64c2-12 9-18 18-18s16 6 18 18z" fill="#2E5AAC"/><circle cx="32" cy="29" r="12" fill="#C68B5E"/><path d="M19 29c0-10 6-15 13-15s13 5 13 15c-3-5-7-8-13-8s-10 3-13 8z" fill="#2A1B14"/><path d="M43 27c3 6 3 14 0 20" stroke="#2A1B14" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="27.5" cy="30" r="1.5" fill="#2A1B14"/><circle cx="36.5" cy="30" r="1.5" fill="#2A1B14"/><path d="M28 35q4 3 8 0" stroke="#2A1B14" stroke-width="1.6" fill="none" stroke-linecap="round"/><circle cx="32" cy="24" r="1.2" fill="#D64545"/></svg>'
EXAM_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19V5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2zm0 0a2 2 0 0 1 2-2h12"/></svg>'


KABIR = '<svg viewBox="0 0 64 64"><rect width="64" height="64" fill="#E1E9F7"/><path d="M12 64c2-12 10-18 20-18s18 6 20 18z" fill="#B45309"/><circle cx="32" cy="29" r="12" fill="#A9714A"/><path d="M19 27c0-9 6-14 13-14s13 5 13 14c-2-4-5-6-8-6-3 3-9 4-13 3-2 1-4 2-5 3z" fill="#1E1A17"/><circle cx="27.5" cy="30" r="1.5" fill="#1E1A17"/><circle cx="36.5" cy="30" r="1.5" fill="#1E1A17"/><path d="M27 35.5q5 3.5 10 0" stroke="#1E1A17" stroke-width="1.6" fill="none" stroke-linecap="round"/><rect x="41" y="40" width="10" height="7" rx="1.5" fill="#2E5AAC"/></svg>'


def say(who, text):
    """One speech bubble. Arjun Sir speaks from the right, Riya from the left."""
    if who == 'K':
        return f'<div class="panel"><div class="avatar" aria-hidden="true">{KABIR}</div><div class="bubble"><b class="who">Kabir</b><p>{text}</p></div></div>'
    if who == 'A':
        return f'<div class="panel panel--right"><div class="avatar" aria-hidden="true">{ARJUN}</div><div class="bubble"><b class="who">Arjun Sir</b><p>{text}</p></div></div>'
    return f'<div class="panel"><div class="avatar" aria-hidden="true">{RIYA}</div><div class="bubble"><b class="who">Riya</b><p>{text}</p></div></div>'


def exam(text):
    return f'<div class="callout callout--exam">{EXAM_ICON}<p><b>Exam tip:</b> {text}</p></div>'

TIP_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z"/></svg>'
WARN_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3 2 21h20L12 3z"/><path d="M12 10v5M12 18v.5"/></svg>'


LEVEL_NAMES = {'L1': ('b', 'Beginner'), 'L2': ('i', 'Intermediate'), 'L3': ('a', 'Advanced')}


def levels(heading, panels):
    """Beginner / Intermediate / Advanced tabs (reuses the .modlab tab script in lesson.js)."""
    bar = ''.join(f'<button type="button" data-mod="{k}">{n}</button>' for k, n in [('b', 'Beginner'), ('i', 'Intermediate'), ('a', 'Advanced')])
    out = [f'  <h3 id="levels">{heading}</h3>',
           f'  <div class="modlab levels"><div class="modlab__bar"><b>Pick your level. New to this? Start at Beginner and climb.</b>{bar}</div>']
    for tag, title, html in panels:
        k, name = LEVEL_NAMES[tag]
        out.append(f'    <div class="modlab__panel" data-mod="{k}"><h4><span class="lvl lvl--{k}">{name}</span> {title}</h4>\n{html}\n    </div>')
    out.append('  </div>')
    return '\n'.join(out)


def body(path):
    """Read body.html. Lines starting with these macros are expanded:
       A> text     Arjun Sir speech bubble        R> text    Riya speech bubble
       K> text     Kabir speech bubble (a friend of Riya, data intern)
       EXAM> text  exam-tip callout               TIP> text  tip callout       WARN> text  warning callout
       LEVELS> heading ... L1> title / L2> title / L3> title (each followed by html lines) ... /LEVELS"""
    import os
    out, lv = [], None
    for ln in open(os.path.join(path, 'body.html'), encoding='utf-8').read().split('\n'):
        s = ln.strip()
        if lv is not None:
            if s == '/LEVELS':
                out.append(levels(lv[0], lv[1])); lv = None
            elif s[:4] in ('L1> ', 'L2> ', 'L3> '):
                lv[1].append([s[:2], s[4:], ''])
            elif lv[1]:
                lv[1][-1][2] += ln + '\n'
            continue
        if s.startswith('LEVELS> '): lv = (s[8:], [])
        elif s.startswith('A> '): out.append('    ' + say('A', s[3:]))
        elif s.startswith('R> '): out.append('    ' + say('R', s[3:]))
        elif s.startswith('K> '): out.append('    ' + say('K', s[3:]))
        elif s.startswith('EXAM> '): out.append('  ' + exam(s[6:]))
        elif s.startswith('TIP> '): out.append(f'  <div class="callout callout--tip">{TIP_ICON}<p>{s[5:]}</p></div>')
        elif s.startswith('WARN> '): out.append(f'  <div class="callout callout--warn">{WARN_ICON}<p>{s[6:]}</p></div>')
        else: out.append(ln)
    return '\n'.join(out)


def playground(cfg):
    """Embed the Cluster Playground (assets/js/cluster-sim.js). cfg is a dict, see the JS header."""
    import json as _j
    return '<div class="csim"><script type="application/json">' + _j.dumps(cfg, ensure_ascii=False).replace('</', '<\\/') + '</script></div>'


def recap(text):
    """'Already know this?' box pointing to Big Data Fundamentals lessons."""
    return f'<div class="callout callout--tip">{TIP_ICON}<p><b>Coming from Big Data Fundamentals?</b> {text}</p></div>'


def mix(quiz):
    """Spread the correct answers over all positions (deterministic), so the answer is not always option B."""
    out = []
    for i, q in enumerate(quiz):
        opts, ans = list(q['options']), q['answer']
        right = opts.pop(ans)
        pos = (i * 3 + 2) % len(q['options'])
        opts.insert(pos, right)
        out.append(dict(q, options=opts, answer=pos))
    return out
