import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)
_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index('SS = r"""') + 9
SS = _s[_i:_s.index('"""', _i)]

META = dict(
    module='01-script-craft', lesson='04-a-reusable-script-template-and-shellcheck', n='1.4',
    module_label='Module 1 · Script craft',
    title='A reusable script template and ShellCheck',
    desc='A team Bash script template with safe mode, logging, getopts, dry run and trap clean-up, a generator that creates new scripts from it, the ShellCheck warnings you meet most (SC2086, SC2045, SC2164, SC2115, SC2006, SC2071, SC2155, SC2181) with real fixes, and a lint routine with bash -n, ShellCheck and test runs.',
    og_desc='A reusable Bash template, a script generator and fixes for the most common ShellCheck warnings.',
    minutes=35, level='Beginner → Intermediate',
    lead='Every new script starts complete from one template, and a linter reads it before any human does.',
    chips=['50-line team template', 'ShellCheck fixes animated', 'Generator + lint routine', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# The template's run() and cleanup ideas, in miniature
dry_run=1
run() { if (( dry_run )); then echo "dry run: $*"; else "$@"; fi; }

tmp=$(mktemp -d)
cleanup() { rm -rf -- "$tmp"; echo "cleaned $tmp"; }
trap cleanup EXIT

run rm -rf -- "${tmp:?}/old-reports"
dry_run=0
run touch "$tmp/new-report"
ls "$tmp"
"""

RUN = dict(
    heading='run() and trap in your browser',
    intro='<p>The same command is first only shown, then really done; the trap removes the temp folder when the script ends.</p>',
    code=MAIN,
    anno=[('dry_run=1', 'run only prints.'), ('trap cleanup EXIT', 'Runs when the script ends.'), ('${tmp:?}', 'Never empty in an rm.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. When does “cleaned” appear?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many words does each printf see?',
             code="f='nov orders.csv'\nprintf '[%s]' $f; echo\nprintf '[%s]' \"$f\"; echo\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error (SC2164):</b> cd can fail and the script carries on. Add || exit 1.',
             code="cd /nonexistent-dir\necho \"still running in: $PWD\"\n", expect='any'),
        dict(label='4 · Your turn', hint='Guard an rm with ${VAR:?}.',
             code="unset OUT\n( rm -rf -- \"${OUT:?OUT is not set}\"/* ) 2>&1\necho \"stopped safely\"\n", expect='any'),
        dict(label='5 · Challenge', hint='Fix SC2071: compare numbers correctly.',
             code="n=9\n[ \"$n\" -gt 10 ] && echo big || echo small\n"),
    ],
)

PCRUN = dict(
    heading='Run ShellCheck on your PC',
    intro='<p>ShellCheck is not installed on our build machine; outputs below are typical.</p>',
    items=[
        dict(title='1 · Install', cmd="sudo apt install shellcheck     # Ubuntu/Debian\nsudo dnf install ShellCheck     # Fedora (EPEL on RHEL)", output='shellcheck --version\nversion: 0.9.0', note='Typical.'),
        dict(title='2 · Lint buggy.sh', cmd="shellcheck bin/buggy.sh", output='''In bin/buggy.sh line 3:
for f in $files; do
         ^----^ SC2086 (info): Double quote to prevent globbing and word splitting.

In bin/buggy.sh line 7:
cd /tmp/work
^----------^ SC2164 (warning): Use 'cd ... || exit' or 'cd ... || return' in case cd fails.

In bin/buggy.sh line 8:
rm -rf $OUTDIR/*
       ^-------^ SC2115 (warning): Use "${var:?}" to ensure this never expands to /* .
       ^-----^ SC2154 (warning): OUTDIR is referenced but not assigned.''', note='Typical (shortened).'),
        dict(title='3 · Only warnings and errors', cmd="shellcheck -S warning bin/*.sh; echo $?", output='… (warnings) …\n1', note='Exit 1 when anything is reported: perfect for CI.'),
        dict(title='4 · In GitHub Actions', cmd="# .github/workflows/lint.yml (step)\n- run: shellcheck -S warning bin/*.sh", output='Error: bin/buggy.sh:7:1: warning: Use cd ... || exit … [SC2164]', note='Typical annotation.'),
    ],
)

TRACE = dict(
    heading='run() and dry runs, line by line',
    intro='<p>The same call, first previewed, then done.</p>',
    code='''dry_run=1
run() { if (( dry_run )); then echo "would: $*"; else "$@"; fi; }
run mkdir -p reports/old
dry_run=0
run mkdir -p reports/old
[[ -d reports/old ]] && echo "folder exists now"
''',
    notes={3: 'Only printed.', 5: 'Really executed.'},
)

WORKED_INTRO = 'Three scripts started from the template idea.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='A cleanup job with a dry run',
         problem='<p>Delete .tmp files older than nothing (all of them) in a folder, but only show them with -n.</p>',
         inp='a folder', approach=['run() wrapper.'],
         code='''dry=0; [[ ${1:-} == -n ]] && dry=1
run(){ if (( dry )); then echo "would: $*"; else "$@"; fi; }
mkdir -p w; touch w/a.tmp w/b.tmp
for f in w/*.tmp; do run rm -- "$f"; done
ls w | wc -l
''', notes={2: 'One switch for every risky step.'}, tryit='Run it with dry=1.'),
    dict(level='i', tag='Dev', title='Fixing four ShellCheck warnings',
         problem='<p>Rewrite a loop that uses ls, backticks and unquoted names.</p>',
         inp='files with spaces', approach=['Glob, $( ), quotes.'],
         code='''mkdir -p in; printf 'a\\nb\\n' > 'in/q3 sales.txt'; printf 'c\\n' > in/q4.txt
for f in in/*.txt; do
  n=$(wc -l < "$f")
  printf '%-16s %s lines\\n' "${f#in/}" "$n"
done
''', notes={2: 'SC2045 fixed.', 3: 'SC2006 and SC2086 fixed.'}, tryit='Skip empty files.'),
    dict(level='a', tag='SRE', title='Temp files that never leak',
         problem='<p>Prove that the EXIT trap cleans up even when the script fails.</p>',
         inp='nothing', approach=['Subshell with a failing step.'],
         code='''before=$(ls /tmp | wc -l)
( set -e; t=$(mktemp -d); trap 'rm -rf -- "$t"' EXIT; touch "$t/x"; false; echo never )
echo "exit $?, temp entries before/after: $before/$(ls /tmp | wc -l)"
''', notes={2: 'false ends the subshell; the trap still runs.'}, tryit='Remove the trap and compare.', expect='any'),
]

QUIZ = mix([
    dict(q='What is ShellCheck?', options=['a shell', 'a linter for shell scripts', 'a test framework', 'a formatter'], answer=1, why='Static analysis.'),
    dict(q='SC2086 means…', options=['missing done', 'unquoted variable', 'useless cat', 'cd may fail'], answer=1, why='Quote it.'),
    dict(q='The fix for SC2164 (cd) is…', options=['sudo cd', 'cd DIR || exit 1', 'pushd', 'set +e'], answer=1, why='Stop on failure.'),
    dict(q='rm -rf "${DIR:?}"/* protects against…', options=['spaces', 'an empty DIR becoming /*', 'symlinks', 'nothing'], answer=1, why='SC2115.'),
    dict(q='trap cleanup EXIT runs…', options=['only on success', 'on every exit', 'only on Ctrl+C', 'at the start'], answer=1, why='Every exit.'),
    dict(q='bash -n checks…', options=['syntax only', 'logic', 'performance', 'permissions'], answer=0, why='Parser only.'),
    dict(q='for f in $(ls *.csv) is flagged because…', options=['slow', 'names with spaces break', 'ls is deprecated', 'it is fine'], answer=1, why='SC2045.'),
    dict(q='Silence one ShellCheck rule:', options=['# shellcheck disable=SC2086 on the line before', 'disable=all', 'set +x', 'rename the file'], answer=0, why='Narrowly.'),
])

REVISION = [
    'Start every script from one template: header, safe mode, logging, getopts -v -n -h, run(), mktemp + trap EXIT, main "$@".',
    'A generator copies the template, fills placeholders, refuses to overwrite, chmod +x and bash -n.',
    'run CMD executes or (with -n) only logs: dry runs for every risky step.',
    'ShellCheck top warnings: SC2086 quote, SC2045 no ls loops, SC2164 cd || exit, SC2115 ${VAR:?}, SC2006 $( ), SC2071 -gt not >.',
    'Check in three layers: bash -n (syntax), ShellCheck (meaning), test run with -n then real (behaviour).',
    'Silence a rule only on one line, with a reason; run ShellCheck in the editor, pre-commit and CI.',
]

FAQ = [
    ('What is ShellCheck?', 'A free static analysis tool that finds bugs and bad practices in shell scripts and explains each with an SC code.'),
    ('How do I install ShellCheck?', 'sudo apt install shellcheck on Ubuntu/Debian, sudo dnf install ShellCheck on Fedora (EPEL on RHEL), or use the online version at shellcheck.net.'),
    ('What does SC2086 mean?', 'An unquoted variable may be split into several words or expanded as a wildcard; put it in double quotes.'),
    ('How do I ignore a ShellCheck warning?', 'Add # shellcheck disable=SCxxxx on the line before, with a comment explaining why.'),
    ('What should a Bash script template contain?', 'Shebang, header, set -euo pipefail, usage, logging, option parsing, clean-up trap and main "$@".'),
    ('What is a dry run in a script?', 'A mode (often -n) that shows what would be done without changing anything.'),
    ('Difference between bash -n and ShellCheck?', 'bash -n only checks syntax; ShellCheck finds logic and quoting bugs too.'),
]

PRACTICE_INTRO = 'Small template and lint tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Syntax check', stmt='Check a correct one-line script with bash -n.', inp='nothing', code="echo 'echo hi' > a.sh; bash -n a.sh && echo ok\n", explain='ok.'),
    dict(level='easy', title='Quote', stmt='Count words in "a b" quoted.', inp='a value', code="v='a b'; set -- \"$v\"; echo $#\n", explain='1.'),
    dict(level='easy', title='Checked cd', stmt='Print failed when cd to a missing folder fails.', inp='nothing', code="cd /no/such 2>/dev/null || echo failed\n", explain='|| runs.'),
    dict(level='medium', title='Guarded rm', stmt='Show the error from ${D:?} when D is unset.', inp='nothing', code="unset D; ( : \"${D:?D not set}\" ) 2>&1 | sed 's/.*: //'\n", explain='D not set.'),
    dict(level='medium', title='Dry run', stmt='Print would: rm x instead of deleting.', inp='nothing', code="dry=1; run(){ (( dry )) && echo \"would: $*\" || \"$@\"; }; run rm x\n", explain='would: rm x.'),
    dict(level='medium', title='Numeric test', stmt='Compare 9 and 10 correctly.', inp='two numbers', code="[ 9 -gt 10 ] && echo bigger || echo smaller\n", explain='smaller.'),
    dict(level='business', title='Trap', stmt='Print bye when a subshell exits.', inp='nothing', code="( trap 'echo bye' EXIT; echo work )\n", explain='work, bye.'),
    dict(level='business', title='Placeholders', stmt='Replace __NAME__ with sync.sh.', inp='a line', code="echo '# __NAME__ - tool' | sed 's|__NAME__|sync.sh|'\n", explain='sed.'),
]

SCN_INTRO = 'Interview questions about script quality.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you check a shell script for errors?”', 'Common.', 'tools?',
        '''<ul>
          <li>bash -n for syntax.</li>
          <li>ShellCheck for bugs.</li>
          <li>bash -x and a test run for behaviour.</li>
        </ul>''', 'only “I run it”.') +
    scn('Service company', 'Junior', 'Script fails on files with spaces', 'Customer files.', 'fix?',
        '''<ol>
          <li>Quote every variable (SC2086).</li>
          <li>Loop over globs, not ls (SC2045).</li>
          <li>Use "${arr[@]}" for lists.</li>
        </ol>''', 'renaming the files.') +
    scn('Product company', 'Mid-level', 'Every script looks different', '20 scripts, 6 authors.', 'proposal?',
        '''<ul>
          <li>One template + generator.</li>
          <li>ShellCheck + shfmt in CI.</li>
          <li>Migrate old scripts when touched.</li>
        </ul>''', 'a style document nobody reads.') +
    scn('Platform', 'Senior', 'rm -rf with an empty variable hit production', 'Post-mortem.', 'prevention?',
        '''<ul>
          <li>${VAR:?} on every rm path; set -u.</li>
          <li>ShellCheck SC2115 as a blocking rule.</li>
          <li>Dry-run mode and review of its output.</li>
        </ul>''', 'banning rm.')
) + interview([
    ('What is a linter?', 'A tool that finds likely bugs without running code.'),
    ('SC2086?', 'Unquoted variable.'),
    ('SC2164?', 'cd without a check.'),
    ('Why trap EXIT?', 'Clean-up on every exit.'),
    ('What is mktemp for?', 'Unique, safe temp files.'),
    ('bash -n vs ShellCheck?', 'Syntax vs meaning.'),
    ('What is shfmt?', 'A shell formatter.'),
], [
    ('LFCS', 'Write and debug scripts.'),
    ('RHCSA', 'Simple scripts that work reliably.'),
    ('CompTIA Linux+', 'Script troubleshooting.'),
]) + distro('Installing ShellCheck.', [
    ('Package', 'shellcheck', 'ShellCheck (EPEL)', 'ShellCheck', 'shellcheck'),
    ('Command', 'apt install', 'dnf install', 'zypper install', 'pacman -S'),
    ('macOS', '-', '-', '-', 'brew install shellcheck'),
    ('Online', 'shellcheck.net', 'same', 'same', 'same'),
    ('Formatter', 'shfmt (snap/go)', 'shfmt', 'shfmt', 'shfmt'),
]) + teaser('2.1', 'Module 1 is complete: your scripts have structure, options, logging and a template. Module 2 starts working with data: reading files line by line safely, with while read, IFS and mapfile.')

CHEATSHEET = cheatsheet('Template + ShellCheck', [
    ('Template', [('set -euo pipefail', 'safe'), ('log / die / bad', 'messages'), ('run CMD', 'dry run'), ('trap cleanup EXIT', 'temp files')]),
    ('Generator', [("newscript NAME 'desc'", 'create'), ('sed __NAME__', 'fill'), ('chmod +x', 'ready'), ('bash -n', 'check')]),
    ('Top fixes', [('"$var"', 'SC2086'), ('for f in *.csv', 'SC2045'), ('cd d || exit', 'SC2164'), ('"${d:?}"', 'SC2115')]),
    ('Checks', [('bash -n', 'syntax'), ('shellcheck -S warning', 'lint'), ('./s.sh -n', 'dry run'), ('shfmt -d', 'format')]),
])

MINDMAP = mindmap('Template + lint', [
    ('Template', 'blue', ['safe mode', 'logging', 'getopts']),
    ('Safety', 'red', ['run() -n', 'trap EXIT', '${VAR:?}']),
    ('Generator', 'green', ['placeholders', 'no overwrite', 'bash -n']),
    ('ShellCheck', 'amber', ['SC2086', 'SC2164', 'SC2115']),
    ('Layers', 'violet', ['syntax', 'meaning', 'behaviour']),
    ('Team', 'acc', ['editor', 'pre-commit', 'CI']),
])

LAB = lab('fix a buggy script', 'Build the lab (it creates <code>~/lab14/count.sh</code> with four classic bugs and some data), fix it, then run the checker.',
    setup='''rm -rf ~/lab14; mkdir -p ~/lab14/in ~/lab14/out && cd ~/lab14
printf 'a\\nb\\n' > 'in/nov sales.txt'; printf 'c\\n' > in/dec.txt
cat > count.sh <<'EOF'
#!/bin/bash
for f in $(ls in/*.txt); do
  echo $f `wc -l < $f`
done > out/report.txt
cd $WORK
rm -rf $WORK/*
EOF''',
    tasks=['Rewrite <code>count.sh</code> with <code>#!/usr/bin/env bash</code> and <code>set -euo pipefail</code>; make it executable.',
           'Loop with a glob and quotes (no <code>ls</code>, no backticks) so <code>out/report.txt</code> has exactly two lines, including <code>in/nov sales.txt 2</code>.',
           'Make the <code>cd</code> and <code>rm</code> safe: when <code>WORK</code> is not set the script must stop with a non-zero exit and must not delete anything.',
           'When <code>WORK</code> points to a folder, the script must empty that folder and exit 0.'],
    solution='''cat > count.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
for f in in/*.txt; do
  echo "$f $(wc -l < "$f")"
done > out/report.txt
cd "${WORK:?WORK not set}" || exit 1
rm -rf -- "${WORK:?}"/*
EOF
chmod +x count.sh''',
    check='''cd ~/lab14; rm -f out/report.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 header"  'head -1 count.sh | grep -q "^#!/usr/bin/env bash" && grep -q "set -euo pipefail" count.sh && [ -x count.sh ]'
ok "2 loop"    'unset WORK; ./count.sh 2>/dev/null; [ "$(wc -l < out/report.txt)" -eq 2 ] && grep -qx "in/nov sales.txt 2" out/report.txt && ! grep -q "\\$(ls" count.sh && ! grep -q "\\`" count.sh'
ok "3 guarded" 'unset WORK; mkdir -p keep && touch keep/x; ( cd keep && ../count.sh ) >/dev/null 2>&1; r=$?; [ $r -ne 0 ] && [ -e keep/x ]'
ok "4 work"    'w=$(mktemp -d); touch "$w/a" "$w/b"; WORK=$w ./count.sh 2>/dev/null; r=$?; [ $r -eq 0 ] && [ -z "$(ls -A "$w")" ]' ''')
