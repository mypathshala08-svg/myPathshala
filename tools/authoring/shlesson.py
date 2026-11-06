#!/usr/bin/env python3
"""Build one Bash/Linux lesson page (Linux and Shell Scripting courses).

usage: sudo python3 tools/authoring/shlesson.py SRC_DIR [SITE_ROOT]

Same spec.py format as pylesson.py (COURSE, META, BODY, RUN, PCRUN, TRACE, EXAMPLES, QUIZ, REVISION,
FAQ, PROBLEMS, SCENARIOS ...), but every program is a **Bash script**:

  * Each script is really run by bash as a normal Linux user `riya` (HOME=/home/riya) inside a fresh,
    empty folder /home/riya/lab, so outputs such as `pwd` and `whoami` look like a student's machine.
    Scripts must create any files they need (heredocs), exactly like in the browser runner.
  * Expected outputs are taken from the run (stdout + stderr, as a terminal shows them), never typed.
  * Traces ("Line by line") are recorded with bash's DEBUG trap: for each line the tracer shows the
    shell's variables, the current folder, the last exit status ($?), the files in ~/lab and the
    text printed.  Consecutive events on the same line (a pipeline) are merged into one step.
  * notes = {line | (line, k): "Phase :: html"}; a note "Phase :: = text" replaces the automatic text.
  * RUN tasks / EXAMPLES / PROBLEMS may set expect='error' (script must fail) or expect='any'.
  * Optional per-script `stdin` text.

Must be run as root (it creates the user riya and runs scripts as riya with runuser).
The page layout is pylesson.page(); this module only swaps the runner, tracer and labels.
"""
import os, sys, json, html, subprocess, shutil, pwd, re, runpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pylesson  # noqa: E402

E = html.escape
USER, HOME = 'riya', '/home/riya'
LAB = HOME + '/lab'
WORK = '/tmp/mp-shlesson'
ENV = {'HOME': HOME, 'USER': USER, 'LOGNAME': USER, 'SHELL': '/bin/bash', 'LANG': 'C.UTF-8',
       'PATH': '/usr/local/bin:/usr/bin:/bin', 'TERM': 'dumb', 'TZ': 'Asia/Kolkata'}

DRIVER = r'''__mp_base=" $(compgen -v | tr '\n' ' ') "
exec 9>"$MP_TRACE"
__mp_dump() {
  local __st=$1 __n
  printf 'E\t%s\t%s\t%s\n' "$2" "$__st" "$(stat -c %s "$MP_OUT")" >&9
  printf 'P\t%s\n' "$PWD" >&9
  for __n in $(compgen -v); do
    case "$__mp_base" in *" $__n "*) continue;; esac
    case $__n in __*|BASH_*|FUNCNAME|PIPESTATUS|OLDPWD|_) continue;; esac
    printf 'V\t%s\t%s\n' "$__n" "${!__n}" >&9
  done
  find "$MP_LAB" -mindepth 1 -maxdepth 3 -printf 'F\t%P\t%y\t%s\t%M\n' 2>/dev/null | LC_ALL=C sort >&9
}
set -T
trap '__mp_s=$?; [[ ${BASH_SOURCE[0]} == "$MP_SCRIPT" ]] && __mp_dump $__mp_s "$LINENO"' DEBUG
trap '__mp_dump $? END' EXIT
source "$MP_SCRIPT"
'''


def ensure_user():
    try:
        pwd.getpwnam(USER)
    except KeyError:
        subprocess.run(['useradd', '-m', '-s', '/bin/bash', USER], check=True)


def fresh_lab():
    ensure_user()
    shutil.rmtree(LAB, ignore_errors=True)
    os.makedirs(LAB)
    pw = pwd.getpwnam(USER)
    os.chown(LAB, pw.pw_uid, pw.pw_gid)
    os.makedirs(WORK, exist_ok=True)
    os.chmod(WORK, 0o777)


def _bash(script_path, stdin=None, trace=False):
    """Run a script as riya in ~/lab. Returns (returncode, output_bytes)."""
    fresh_lab()
    out_path = os.path.join(WORK, 'out.txt')
    open(out_path, 'wb').close(); os.chmod(out_path, 0o666)
    env = dict(ENV, MP_LAB=LAB, MP_OUT=out_path, MP_TRACE=os.path.join(WORK, 'trace.txt'), MP_SCRIPT=script_path)
    if trace:
        drv = os.path.join(WORK, 'driver.sh')
        open(drv, 'w').write(DRIVER); os.chmod(drv, 0o644)
        cmd = ['bash', '--norc', '--noprofile', drv]
    else:
        cmd = ['bash', '--norc', '--noprofile', script_path]
    full = ['runuser', '-u', USER, '--', 'env', '-i'] + [f'{k}={v}' for k, v in env.items()] + cmd
    with open(out_path, 'wb') as fo:
        p = subprocess.run(full, cwd=LAB, stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                           input=stdin.encode() if stdin is not None else None, stdout=fo, stderr=subprocess.STDOUT, timeout=60)
    return p.returncode, open(out_path, 'rb').read()


def _script(code):
    # lives in riya's home (outside ~/lab), so error messages read like a student's machine: /home/riya/script.sh: line 3: ...
    ensure_user()
    path = os.path.join(HOME, 'script.sh')
    open(path, 'w').write(code.rstrip('\n') + '\n')
    os.chmod(path, 0o644)
    return path


EXPECT_BY_CODE = pylesson.__dict__.setdefault('SH_EXPECT', {})   # shared by every copy of this module; code -> 'error' | 'any', filled from RUN/EXAMPLES/PROBLEMS 'expect' keys (pylesson.page passes no expect)


def run_sh(code, expect=None, stdin=None):
    if expect is None:
        expect = EXPECT_BY_CODE.get(code)
    rc, out = _bash(_script(code), stdin)
    text = out.decode('utf-8', 'replace')
    if expect == 'error' and rc == 0:
        raise SystemExit('expected the script to fail, but it exited 0:\n' + code)
    if expect is None and rc != 0:
        raise SystemExit(f'script failed (exit {rc}):\n{code}\n--- output ---\n{text}')
    if expect is None:
        for bad in ('command not found', 'No such file or directory', 'cannot access', 'Permission denied', 'syntax error', 'Is a directory'):
            if bad in text:
                raise SystemExit(f'output contains an error ({bad!r}) but the script was not marked expect="error"/"any":\n{code}\n--- output ---\n{text}')
    return text


# ---------------------------------------------------------------- tracer
def _parse(raw):
    evs, cur = [], None
    for ln in raw.split('\n'):
        if not ln:
            continue
        k, *f = ln.split('\t')
        if k == 'E':
            cur = dict(line=f[0], st=f[1], pos=int(f[2]), pwd='', vars=[], files=[])
            evs.append(cur)
        elif k == 'P':
            cur['pwd'] = f[0]
        elif k == 'V':
            cur['vars'].append([f[0], f[1] if len(f) > 1 else ''])
        elif k == 'F':
            cur['files'].append(dict(path=f[0], type=f[1], size=int(f[2]), mode=f[3]))
    return evs


def _home(p):
    return '~' + p[len(HOME):] if p == HOME or p.startswith(HOME + '/') else p


def _short(s, n=60):
    s = s.replace('\n', '⏎')
    return s if len(s) <= n else s[:n - 1] + '…'


def _file_html(f, perms):
    if f['type'] == 'd':
        return f'<b>{E(f["path"])}/</b> folder' + (f' · <code>{E(f["mode"])}</code>' if perms else '')
    if f['type'] == 'l':
        return f'<b>{E(f["path"])}</b> link'
    s = f['size']
    sz = f'{s} byte' + ('' if s == 1 else 's')
    return f'<b>{E(f["path"])}</b> file · {sz}' + (f' · <code>{E(f["mode"])}</code>' if perms else '')


def build_sh_trace(spec_trace):
    code = spec_trace['code'].rstrip('\n') + '\n'
    notes = spec_trace.get('notes', {})
    perms = spec_trace.get('perms', False)
    rc, out = _bash(_script(code), spec_trace.get('stdin'), trace=True)
    raw = open(os.path.join(WORK, 'trace.txt'), encoding='utf-8', errors='replace').read()
    evs = _parse(raw)
    if not evs or evs[-1]['line'] != 'END':
        raise SystemExit('trace did not finish:\n' + code)
    # merge consecutive events on the same line (pipelines, a; b on one line)
    merged = []
    for e in evs:
        if merged and e['line'] != 'END' and merged[-1]['line'] == e['line']:
            continue
        merged.append(e)
    src = code.split('\n')
    steps, count = [], {}
    prev_state = None
    for i, e in enumerate(merged[:-1]):
        after = merged[i + 1]
        line = int(e['line'])
        # bash reports a command that spans several lines (an open '...' quote) at its LAST line: find its first line
        first = line
        while first > 1 and sum(l.count("'") for l in src[first - 1:line]) % 2 == 1:
            first -= 1
        if first != line and first in notes and line not in notes:
            notes = dict(notes); notes[line] = notes[first]
        count[line] = count.get(line, 0) + 1
        k = count[line]
        st_vars = [['folder (PWD)', _home(after['pwd'])], ['$? exit status', after['st']]] + \
                  [[n, _short(v)] for n, v in after['vars']]
        stack = [{'frame': 'bash · your script', 'vars': st_vars}]
        files = [f for f in after['files']]
        heap = [_file_html(f, perms) for f in files][:14]
        printed = out[e['pos']:after['pos']].decode('utf-8', 'replace')
        # automatic note
        bits, newv = [], None
        if prev_state is None:
            pv, ppwd, pfiles = {}, LAB, {}
        else:
            pv, ppwd, pfiles = prev_state
        for n, v in after['vars']:
            if n not in pv:
                bits.append(f'Variable <code>{E(n)}</code> is created: <code>{E(_short(v))}</code>.'); newv = n
            elif pv[n] != v:
                bits.append(f'<code>{E(n)}</code> changes to <code>{E(_short(v))}</code>.'); newv = n
        if after['pwd'] != ppwd:
            bits.append(f'The current folder changes to <code>{E(_home(after["pwd"]))}</code>.'); newv = 'folder (PWD)'
        nf = {f['path']: f for f in files}
        for pth, f in nf.items():
            if pth not in pfiles:
                bits.append(f'New {"folder" if f["type"] == "d" else "file"} <code>{E(pth)}</code> appears in ~/lab.')
            elif f['type'] == 'f' and pfiles[pth]['size'] != f['size']:
                bits.append(f'<code>{E(pth)}</code> now has {f["size"]} bytes.')
            elif pfiles[pth]['mode'] != f['mode']:
                bits.append(f'Permissions of <code>{E(pth)}</code> change to <code>{E(f["mode"])}</code>.')
        for pth in pfiles:
            if pth not in nf:
                bits.append(f'<code>{E(pth)}</code> is gone.')
        if after['st'] != '0':
            bits.append(f'The command <b>failed</b>: exit status <b>{E(after["st"])}</b>.')
        if printed and not bits:
            bits.append('The output appears in the terminal.')
        a = ' '.join(bits)
        n = notes.get((line, k)) or (notes.get(line) if k == 1 else None)
        phase, note = 'Shell', a
        if n:
            phase, txt = n.split('::', 1) if '::' in n else ('Shell', n)
            phase, txt = phase.strip(), txt.strip()
            note = txt[1:].strip() if txt.startswith('=') else (txt + (' ' + a if a else ''))
        step = {'line': [first, line] if first != line else line, 'phase': phase, 'note': note or 'This line runs.', 'stack': stack, 'heap': heap}
        if printed:
            step['out'] = printed
        if newv:
            step['newVar'] = newv
        steps.append(step)
        prev_state = (dict((n, v) for n, v in after['vars']), after['pwd'], nf)
    if len(steps) > 70:
        raise SystemExit(f'trace too long ({len(steps)} steps)')
    used = set()
    for st in steps:
        used |= set(range(st['line'][0], st['line'][1] + 1)) if isinstance(st['line'], list) else {st['line']}
    for key in notes:
        ln = key[0] if isinstance(key, tuple) else key
        if ln not in used:
            print(f'WARNING: trace note for line {ln} never matched a traced line')
    return {'lang': 'bash', 'code': code.rstrip('\n').split('\n'), 'steps': steps,
            'labels': {'stack': ['Shell', 'variables, current folder, $?'], 'heap': ['Files', 'inside ~/lab'],
                       'emptyStack': 'the shell has not started', 'emptyHeap': '~/lab is empty'}}, out.decode('utf-8', 'replace')


def pc(cmd, as_root=False, shell_cmd=None):
    """Run a 'Run on your PC' command for real and return its output (for spec.py PCRUN items)."""
    if as_root:
        p = subprocess.run(['bash', '-c', shell_cmd or cmd], capture_output=True, text=True, timeout=120, env=dict(os.environ, LANG='C.UTF-8'))
    else:
        fresh_lab()
        p = subprocess.run(['runuser', '-u', USER, '--', 'env', '-i'] + [f'{k}={v}' for k, v in ENV.items()] + ['bash', '-c', shell_cmd or cmd],
                           cwd=LAB, capture_output=True, text=True, timeout=120)
    return (p.stdout + p.stderr).rstrip('\n')


def codebox(code, out=None, lang='bash', file='script.sh'):
    o = f'<div class="output">{E(out.rstrip())}</div>' if out else ''
    return f'<div class="code" data-lang="{lang}" data-file="{E(file)}"><pre><code>{E(code.rstrip())}</code></pre>{o}</div>'


# patch the shared page builder
pylesson.run_py = run_sh
pylesson.build_trace = build_sh_trace
pylesson.codebox = codebox


def post(h, S):
    h = h.replace('"lang": "python"', '"lang": "bash"').replace('"file": "main.py"', '"file": "script.sh"')
    h = h.replace('Recorded from a real Python run: press <b>Next</b> to execute one line at a time. Watch variables change in each frame, and lists and dictionaries (numbered #1, #2 …) fill up as objects.',
                  'Recorded from a real Bash run on Linux: press <b>Next</b> to run one line at a time. Watch the shell’s variables, the current folder, the exit status <code>$?</code> and the files in <code>~/lab</code> change.')
    if 'id="map"' in S['BODY']:
        h = h.replace('<li><a href="#story">The story</a></li>', '<li><a href="#map">Where this fits</a></li>\n      <li><a href="#story">The story</a></li>')
    if 'id="names"' in S['BODY']:
        h = h.replace('<li><a href="#types">', '<li><a href="#names">Why is it called that?</a></li>\n      <li><a href="#types">')
    if S.get('MINDMAP'):
        h = h.replace('  <h3>Quick revision</h3>', S['MINDMAP'] + '\n  <h3>Quick revision</h3>', 1)
        h = h.replace('<li><a href="#quiz">Quiz and revision</a></li>', '<li><a href="#quiz">Quiz and revision</a></li>\n      <li><a href="#mindmap">Mind map</a></li>', 1)
    if 'id="kernel-map"' in S['BODY']:
        h = h.replace('<li><a href="#steps">', '<li><a href="#kernel-map">Inside the kernel</a></li>\n      <li><a href="#steps">', 1)
    if 'id="dissect"' in S['BODY']:
        h = h.replace('<li><a href="#real-world">Real-world use</a></li>', '<li><a href="#dissect">Layer by layer</a></li>\n      <li><a href="#real-world">Real-world use</a></li>')
    h = h.replace('<li><a href="#levels">Beginner → Advanced</a></li>', '<li><a href="#levels">Very basic → Advanced</a></li>') if 'levels4' in S['BODY'] else h
    if S.get('CHEATSHEET'):
        h = h.replace('  <h3>Quick revision</h3>', S['CHEATSHEET'] + '\n  <h3>Quick revision</h3>', 1)
        h = h.replace('<li><a href="#quiz">Quiz and revision</a></li>', '<li><a href="#quiz">Quiz and revision</a></li>\n      <li><a href="#cheatsheet">Cheat sheet</a></li>', 1)
    if S.get('LAB'):
        h = re.sub(r'(<p class="prob-intro">.*?</p>)', lambda m: m.group(1) + '\n' + S['LAB'], h, count=1, flags=re.S)
        h = h.replace('<li><a href="#practice">Practice problems</a></li>', '<li><a href="#lab">Practice lab</a></li>\n      <li><a href="#practice">Practice problems</a></li>', 1)
    if 'class="cc"' in S['BODY']:
        h = h.replace('<li><a href="#steps">Step by step</a></li>', '<li><a href="#commands">Commands by field</a></li>\n      <li><a href="#steps">Step by step</a></li>', 1)
    for hid, lab_ in (('errors', 'Error messages decoded'), ('hood', 'Under the hood')):
        if f'id="{hid}"' in S['BODY']:
            h = h.replace('<li><a href="#animation">See it happen</a></li>', f'<li><a href="#animation">See it happen</a></li>\n      <li><a href="#{hid}">{lab_}</a></li>', 1)
    extra = ''
    if 'id="oneliners"' in S['BODY']:
        extra += '\n      <li><a href="#oneliners">One-liner corner</a></li>'
    if 'id="which"' in S['BODY']:
        extra += '\n      <li><a href="#which">Which command when?</a></li>'
    h = h.replace('<li><a href="#real-world">Real-world use</a></li>', '<li><a href="#real-world">Real-world use</a></li>' + extra)
    # in-article ad slots between parts (filled by ads.js from MP_CONFIG.adSlots.inarticle)
    ad = '<div class="ad-slot ad-slot--inarticle" data-slot="inarticle"></div>\n'
    for anchor in ['<section class="part" id="types">', '<section class="part" id="real-world">', '<section class="part" id="tracer">', '  <h3 id="practice">']:
        if anchor in h:
            h = h.replace(anchor, ad + anchor, 1)
    assert '"lang": "python"' not in h
    return h


def main():
    if os.geteuid() != 0:
        raise SystemExit('run shlesson.py as root (it runs every script as the user riya)')
    src = os.path.abspath(sys.argv[1])
    root = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath(os.path.join(HERE, '..', '..'))
    shared = os.path.join(os.path.dirname(os.path.dirname(src)), 'course.py')
    S = runpy.run_path(shared) if os.path.exists(shared) else {}
    S.update(runpy.run_path(os.path.join(src, 'spec.py'), init_globals=S))
    M = S['META']
    for blk in [S.get('RUN', {})] + list(S.get('EXAMPLES', [])) + list(S.get('PROBLEMS', [])):
        if blk.get('expect') and blk.get('code'):
            EXPECT_BY_CODE[blk['code']] = blk['expect']
    out = os.path.join(root, 'courses', S['COURSE']['id'], M['module'], M['lesson'], 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    h = post(pylesson.page(S, root), S)
    open(out, 'w', encoding='utf-8').write(h)
    print('wrote', os.path.relpath(out, root), f'({len(h)//1024} KB)')


if __name__ == '__main__':
    main()
