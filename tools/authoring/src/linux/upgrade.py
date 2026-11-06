"""Insert the new-format blocks (5 Nov 2026) into an older Linux lesson's _body.py and spec.py.

usage (from a lesson folder's upgrade_spec.py):
    from upgrade import upgrade
    upgrade(HERE, U)
U is a dict of Python *source snippets* (they are pasted into _body.py, so they may call linuxkit helpers):
    PUZZLE, VERY_BASIC_TITLE, VERY_BASIC_HTML (a Python expression giving html), NAMES, DIDYOU,
    QC_DEF, QC_TYPES, QC_STEPS, DISSECT, QC_ANIM, BUILD, PUZZLE_ANSWER, QC_UC, CMAP, TEASER (spec.py).
Safe to run once: it refuses if the lesson already contains concept_map(.
"""
import os, re


def _ins_before_section_end(s, var, snippet):
    i = s.index(f"\n{var} = '''")
    j = s.index("</section>\n'''", i)
    return s[:j] + "''' + " + snippet + " + '''\n" + s[j:]


def upgrade(here, U):
    p = os.path.join(here, '_body.py')
    s = open(p, encoding='utf-8').read()
    if 'concept_map(' in s:
        print('already upgraded:', here); return
    open(p + '.pre-upgrade', 'w', encoding='utf-8').write(s)
    # 1. puzzle at the start of the story
    a = '  <div class="story">\n    <p class="narration">'
    assert s.count(a) == 1, 'story anchor'
    s = s.replace(a, "  <div class=\"story\">\n''' + " + U['PUZZLE'] + " + '''\n    <p class=\"narration\">")
    # 2. levels -> levels4 with a Very basic panel
    a = s[s.index("lv = '''"):s.index("/LEVELS\n'''") + len("/LEVELS\n'''")]
    heading = re.search(r"LEVELS> (.*)", a).group(1).replace('three levels', 'four depths')
    parts = re.split(r'\nL[123]> ', a)
    def split(x):
        t_, h = x.split('\n', 1)
        return t_.strip(), h.replace("/LEVELS\n'''", '').rstrip()
    p1, p2, p3 = (split(x) for x in parts[1:4])
    new = (f"lv = levels4({heading!r}, [\n"
           f"    ('v', {U['VERY_BASIC_TITLE']!r}, {U['VERY_BASIC_HTML']}),\n"
           f"    ('b', {p1[0]!r}, '''{p1[1]}'''),\n"
           f"    ('i', {p2[0]!r}, '''{p2[1]}'''),\n"
           f"    ('a', {p3[0]!r}, '''{p3[1]}'''),\n])\n")
    s = s.replace(a, new)
    # 3. names + did-you-know around the levels
    a = "]) + '\\n' + lv + '''"
    assert s.count(a) == 1, 'lv anchor'
    s = s.replace(a, "]) + '\\n' + " + U['NAMES'] + " + '\\n' + lv + " + U['DIDYOU'] + " + '''")
    # 4. quick checks and the dissect block at the ends of parts 2-6
    s = _ins_before_section_end(s, 'definition', U['QC_DEF'])
    s = _ins_before_section_end(s, 'types', U['QC_TYPES'])
    s = _ins_before_section_end(s, 'steps', U['QC_STEPS'])
    s = _ins_before_section_end(s, 'animation', U['DISSECT'] + ' + ' + U['QC_ANIM'])
    # 5. build-up one-liner
    a = ']) + which('
    assert s.count(a) == 1, 'which anchor'
    s = s.replace(a, '], extra=' + U['BUILD'] + ') + which(')
    # 6. puzzle answer + quick check at the end of part 6 (last section before body =)
    i = s.index('body = (story.replace(')
    j = s.rfind("</section>\n'''", 0, i)
    s = s[:j] + "''' + " + U['PUZZLE_ANSWER'] + ' + ' + U['QC_UC'] + " + '''\n" + s[j:]
    # 7. concept map on top
    s = s.replace('body = (story.replace(', 'cmap = ' + U['CMAP'] + '\nbody = cmap + (story.replace(', 1)
    open(p, 'w', encoding='utf-8').write(s)
    # 8. teaser in spec.py
    sp = os.path.join(here, 'spec.py')
    t = open(sp, encoding='utf-8').read()
    if 'teaser(' not in t:
        t = t.replace("from shlesson import pc\n", "from shlesson import pc\nsys.path.insert(0, os.path.join(HERE, '..', '..'))\nfrom linuxkit import teaser\n", 1)
        t = t.rstrip('\n')
        assert t.endswith(')'), 'spec must end with SCENARIOS = (...)'
        t = t + ' + ' + U['TEASER'] + '\n'
        open(sp, 'w', encoding='utf-8').write(t)
    print('upgraded', os.path.basename(here))
