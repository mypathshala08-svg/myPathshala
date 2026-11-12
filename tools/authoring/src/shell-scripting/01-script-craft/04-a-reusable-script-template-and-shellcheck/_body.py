import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# The team template, a generator that copies it, and a script with typical bugs (all real on our build machine)
SS = r"""rm -rf ~/ops; mkdir -p ~/ops/bin ~/ops/templates ~/ops/data; cd ~/ops
printf 'id,city,amount\n1,Pune,450\n2,Mumbai,1200\n' > 'data/nov orders.csv'
cat > templates/script.sh <<'EOF'
#!/usr/bin/env bash
# __NAME__ - __DESC__
# Usage: __NAME__ [-v] [-n] [-h] ARG
# Exit codes: 0 ok, 1 error, 2 usage
set -euo pipefail
readonly PROG=${0##*/}
readonly VERSION=0.1.0

verbose=0 dry_run=0

usage() {
  cat <<USAGE
Usage: $PROG [-v] [-n] [-h] ARG
  -v   verbose
  -n   dry run: show what would be done
  -h   help
USAGE
}
log()  { echo "$(date '+%F %T') [$1] $PROG: ${*:2}" >&2; }
info() { log INFO "$@"; }
debug(){ (( verbose )) && log DEBUG "$@" || true; }
die()  { log ERROR "$*"; exit 1; }
bad()  { echo "$PROG: $*" >&2; usage >&2; exit 2; }
run()  { if (( dry_run )); then info "dry run: $*"; else "$@"; fi; }

tmp=""
cleanup() { [[ -n $tmp ]] && rm -rf -- "$tmp"; return 0; }
trap cleanup EXIT

main() {
  local opt
  while getopts ':vnh' opt; do
    case $opt in
      v) verbose=1 ;;
      n) dry_run=1 ;;
      h) usage; exit 0 ;;
      \?) bad "unknown option -$OPTARG" ;;
    esac
  done
  shift $((OPTIND - 1))
  (( $# == 1 )) || bad "expected 1 argument, got $#"

  tmp=$(mktemp -d)
  debug "temp dir $tmp"
  info "start: $1"
  # --- your work here ---
  run touch "$tmp/work"
  info "done"
}

main "$@"
EOF
cat > bin/newscript <<'EOF'
#!/usr/bin/env bash
# newscript - create a new script from the team template
set -euo pipefail
(( $# == 2 )) || { echo "Usage: newscript NAME 'one-line description'" >&2; exit 2; }
name=$1 desc=$2 dest=bin/$1
[[ -e $dest ]] && { echo "newscript: $dest already exists" >&2; exit 1; }
sed -e "s|__NAME__|$name|g" -e "s|__DESC__|$desc|g" templates/script.sh > "$dest"
chmod +x "$dest"
bash -n "$dest" && echo "created $dest ($(wc -l < "$dest") lines)"
EOF
chmod +x bin/newscript
cat > bin/buggy.sh <<'EOF'
#!/bin/bash
files=$(ls data/*.csv)
for f in $files; do
  echo Processing $f
  count=`wc -l < $f`
done
cd /tmp/work
rm -rf $OUTDIR/*
if [ $count > 1 ]; then echo "has rows"; fi
EOF
chmod +x bin/buggy.sh"""

HOOK = hook('Riya now writes a new script every week, and each time she copies the last one, deletes half of it, and forgets something: the safe mode, the usage text, the clean-up of temp files. Her team agrees on one <b>template</b>: every new script starts from the same 50 lines that already contain everything from Lessons 1.1 to 1.3, plus a dry-run switch and automatic clean-up. And before any script is merged, a <b>linter</b> called <b>ShellCheck</b> reads it and points at the bugs humans keep missing: unquoted variables, a <code>cd</code> that may fail, a <code>rm -rf $DIR/*</code> that could become <code>rm -rf /*</code>. This lesson builds the template, a generator for it, and a lint routine.',
    ['use a team script template with safe mode, logging, getopts, dry run and a trap clean-up',
     'create new scripts from it with a small generator, and fill in only the work',
     'read the typical ShellCheck warnings (SC2086, SC2164, SC2115, SC2045, SC2006 …) and fix each one',
     'build a pre-commit check: bash -n, ShellCheck, and a test run'])
ROAD = roadmap([
    ('story', 'The story', 3, 'copy, delete, forget'),
    ('decide', 'Checklist', 2, 'what the template gives'),
    ('definition', 'Template and linter', 5, 'simple meaning + 4 depths'),
    ('types', 'ShellCheck warnings', 5, 'the ten you will see'),
    ('commands', 'Step by step', 15, 'template, generator, fixes'),
    ('animation', 'See it happen', 4, 'lint → fix → clean'),
    ('run', 'Run on your PC', 3, 'install ShellCheck'),
    ('lab', 'Practice lab', 8, 'fix a buggy script'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('The template already has → so you never forget', [
    ('shebang, header, exit codes', 'what it is and how to call it', 'Lesson 1.1'),
    ('set -euo pipefail', 'stop on errors', 'Lesson 1.1'),
    ('getopts -v -n -h', 'options and help', 'Lesson 1.2'),
    ('log / info / debug / die', 'timestamped messages on stderr', 'Lesson 1.3'),
    ('run() with -n', 'dry runs for anything risky', 'new'),
    ('mktemp + trap cleanup EXIT', 'no temp files left behind', 'new'),
    ('main "$@"', 'one entry point', 'Lesson 1.1'),
    ('ShellCheck before commit', 'bugs found by a machine', 'new'),
])

cmap = concept_map(
    [('1.1', 'Anatomy', 'eight parts'), ('1.2', 'getopts', 'options'), ('1.3', 'Logging', 'exit codes')],
    ['a team script template', 'run() and dry runs', 'mktemp and trap EXIT', 'a generator for new scripts', 'ShellCheck warnings and fixes', 'bash -n and a lint routine', 'pre-commit checks'],
    [('2.3', 'Temp files and trap', 'in depth'), ('3.1', 'Error handling', 'ERR trap'), ('3.3', 'Testing scripts', 'tests'), ('4.1', 'Backup tool', 'from the template')],
    'Every new script starts complete, and a machine reviews it before people do.')

sc = (term(20, 14, 316, 156, ['$ bin/newscript sync.sh "sync reports"', ('created bin/sync.sh (54 lines)', 'out'), '$ shellcheck bin/buggy.sh', ('SC2086: Double quote to prevent globbing', 'err'), ('SC2164: Use cd ... || exit', 'err'), ('SC2115: Use "${var:?}" so rm', 'err'), ('       never runs on /*', 'err')], title='riya@laptop: ~/ops', prompt='$', size=6.4, step=17)
      + t(352, 36, 'Start right, check always:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['template: 50 lines', 'generator: 1 command', 'ShellCheck: bugs', 'bash -n: syntax', 'test run: behaviour'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Copy, delete, forget</h2>
  <div class="story">
''' + puzzle('A colleague’s script <code>buggy.sh</code> “works on his laptop”. On the server it stops with “No such file or directory” for a file called <code>nov orders.csv</code>; then <code>cd /tmp/work</code> fails but the script carries on in the wrong folder; and one line, <code>rm -rf $OUTDIR/*</code>, would delete everything under <code>/</code> if <code>OUTDIR</code> were empty. All three bugs are the kind a linter finds in a second. Which line causes which problem?') + '''
    <p class="narration">In Riya’s <code>~/ops</code> folder (the template, generator and fixes are all really run; ShellCheck’s own output is typical, because it is not installed on our build machine).</p>
''' + scene('A terminal: newscript creates sync.sh from the template, then shellcheck lists three warnings for buggy.sh: missing quotes, cd without a check, and an unsafe rm.', sc,
            'Start from a template, let <tspan font-weight="700" class="s-acc">ShellCheck</tspan> review.') + '''
K> A template, for a shell script? Isn’t that overkill?
A> The boring parts (safe mode, usage, logging, clean-up) are the parts people forget, and forgetting them causes the 2 a.m. failures. With a template you start with them done and only write the interesting part.
R> And ShellCheck?
A> It is a free static analyser for shell scripts. It reads the code without running it and explains each problem with a code like SC2086 and a link. Teams run it in their editor and in CI.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="The workflow: newscript copies the template, you write the work, then bash -n, ShellCheck and a test run check it before commit.">'
       + ''.join(label_box(14 + i * 125, 60, 115, 60, [a, b], c, 8.6) + (arrow(129 + i * 125, 90, 139 + i * 125, 90) if i < 4 else '')
                 for i, (a, b, c) in enumerate([('newscript', 'from template', 'blue'), ('your work', 'in main()', 'green'), ('bash -n', 'syntax', 'amber'), ('ShellCheck', 'bugs', 'red'), ('test run', '-n then real', 'violet')]))
       + t(320, 150, 'every script, every time', 9.4, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Templates and linting at four depths', [
    ('v', 'No jargon: a form and a proof-reader', '      <p>A printed form makes sure nobody forgets a field; a proof-reader catches the typos you no longer see. The template is the form, ShellCheck the proof-reader.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>bin/newscript sync.sh "sync reports to the share"</code></li>
        <li>write the work inside <code>main()</code>, wrap risky commands in <code>run</code></li>
        <li><code>bash -n bin/sync.sh &amp;&amp; shellcheck bin/sync.sh</code></li>
        <li><code>bin/sync.sh -n ARG</code> (dry run) before the real run</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li><code>run cmd args</code> executes <code>cmd</code>, or with <code>-n</code> only logs it: one switch makes every risky step previewable.</li>
        <li><code>trap cleanup EXIT</code> runs on <i>every</i> exit (success, die, set -e, Ctrl+C), so temp files never pile up.</li>
        <li>ShellCheck severities: error, warning, info, style; <code>-S warning</code> hides the rest; <code># shellcheck disable=SC2086</code> on the line before silences one rule on purpose.</li>
        <li><code>bash -n</code> only checks syntax; ShellCheck checks meaning; only a test run checks behaviour. You need all three.</li>
      </ul>'''),
    ('a', 'Behind the screen: static analysis', '''      <ul>
        <li>ShellCheck (written in Haskell) parses the script into a syntax tree and runs over 300 checks on it, without executing anything; it knows how word splitting, globbing and quoting really work in sh, bash, dash and ksh.</li>
        <li>It reads the shebang (or <code># shellcheck shell=bash</code>) to choose the dialect, so <code>[[ ]]</code> in a <code>#!/bin/sh</code> script is flagged (SC3010).</li>
        <li><code>-f gcc</code> and <code>-f json</code> outputs feed editors (VS Code extension) and CI annotations; <code>-x</code> follows <code>source</code>d files.</li>
        <li><code>shfmt</code> is the matching formatter (indentation, spacing), often run next to ShellCheck in pre-commit hooks.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A script template and ShellCheck</h2>
''' + def_block(
    'A <b>script template</b> is a ready-made starting file that contains a team’s standard structure (header, safe mode, option parsing, logging, clean-up, main) so every new script begins complete and consistent. <b>ShellCheck</b> is a static analysis tool (a <b>linter</b>) for shell scripts: it reads a script without running it and reports likely bugs and bad practices, each with a code such as SC2086 and an explanation.',
    'Start from the same skeleton; let a tool proof-read it.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Template', 'Standard starting file.'),
    ('Generator', 'Copies the template, fills names.'),
    ('Linter', 'Finds bugs without running.'),
    ('SCxxxx', 'A ShellCheck rule code.'),
    ('Dry run', 'Show actions, change nothing.'),
    ('trap EXIT', 'Run code whenever the script ends.'),
    ('mktemp', 'Safe unique temp file/folder.'),
    ('Pre-commit', 'Checks before code is saved to git.'),
]) + '\n' + names('Where the names come from.', [
    ('lint', 'fluff on clothes', 'Unix lint for C, 1978.'),
    ('ShellCheck', 'checks shell', 'Vidar Holen, 2012.'),
    ('SC', 'ShellCheck code', 'SC1xxx parse, SC2xxx logic.'),
    ('shfmt', 'shell formatter', 'Daniel Martí.'),
    ('mktemp', 'make temporary', '1996.'),
    ('trap', 'catch a signal', 'Bourne shell.'),
    ('dry run', 'practice without water', 'Fire brigades.'),
    ('boilerplate', 'printing plates reused', 'Newspapers.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('New script', '<code>bin/newscript NAME "desc"</code>'),
    ('Syntax only', '<code>bash -n f.sh</code>'),
    ('Lint', '<code>shellcheck f.sh</code>'),
    ('Only important', '<code>shellcheck -S warning</code>'),
    ('Silence one rule', '<code># shellcheck disable=SC2086</code>'),
    ('Install', '<code>apt/dnf install shellcheck</code>'),
]) + '\n' + lv + didyou('ShellCheck’s wiki has a page for every rule (for example SC2086) explaining the problem, the fix, and rare exceptions. Reading the page for each warning you meet is one of the fastest ways to really understand quoting and word splitting.') + '''
EXAM> “What is the most common ShellCheck warning?” → SC2086, “Double quote to prevent globbing and word splitting”: an unquoted $variable that would break on spaces or wildcards.
''' + qc('Why does the template use trap cleanup EXIT instead of rm at the end of main?', 'EXIT runs on every exit, including errors, die and Ctrl+C; a line at the end of main runs only on success.') + mistake('# shellcheck disable=all at the top of the file',
    'fix the warnings; disable one rule on one line, with a comment why',
    'Silencing everything hides exactly the bugs ShellCheck exists to find.') + mistake('copying the last script and deleting what you do not need',
    'bin/newscript NAME "desc" from the agreed template',
    'Copies carry old bugs and lose the parts you forget to keep, like safe mode or clean-up.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The ShellCheck warnings you will meet most</h2>
''' + table(['Code', 'Problem', 'Example', 'Fix'], [
    ['SC2086', 'unquoted variable: splits and globs', '<code>wc -l &lt; $f</code>', '<code>"$f"</code>'],
    ['SC2045', 'looping over ls output', '<code>for f in $(ls *.csv)</code>', '<code>for f in *.csv</code>'],
    ['SC2164', 'cd may fail, script continues', '<code>cd /tmp/work</code>', '<code>cd /tmp/work || exit 1</code>'],
    ['SC2115', 'rm on an empty variable could hit /', '<code>rm -rf $DIR/*</code>', '<code>rm -rf "${DIR:?}"/*</code>'],
    ['SC2006', 'old backticks', '<code>`wc -l`</code>', '<code>$(wc -l)</code>'],
    ['SC2071', '&gt; in [ ] is a redirection / string compare', '<code>[ $n &gt; 1 ]</code>', '<code>[ "$n" -gt 1 ]</code>'],
    ['SC2154', 'variable used but never set', '<code>$OUTDIR</code>', 'set it or use <code>${OUTDIR:?}</code>'],
    ['SC2034', 'variable set but never used', '<code>count=…</code>', 'use it or remove it'],
    ['SC2155', 'local and $( ) on one line hide the status', '<code>local x=$(cmd)</code>', '<code>local x; x=$(cmd)</code>'],
    ['SC2181', 'checking $? instead of the command', '<code>cmd; if [ $? -ne 0 ]</code>', '<code>if ! cmd; then</code>'],
], minw=620) + table(['Check', 'Finds', 'Misses'], [
    ['<code>bash -n</code>', 'syntax errors (missing fi, done)', 'everything else'],
    ['ShellCheck', 'quoting, logic, portability, risky patterns', 'wrong business logic'],
    ['test run with <code>-n</code>', 'what would happen', 'real side effects'],
    ['real test run', 'actual behaviour', 'untested inputs'],
], minw=440) + qc('Which warning is about rm -rf $DIR/*?', 'SC2115: use "${DIR:?}" so an empty DIR stops the script instead of deleting /*.') + '''
</section>
'''

B = SS + "\ncd ~/ops && bin/newscript sync.sh 'sync reports to the share' > /dev/null"
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Template, generator, and fixing what ShellCheck finds</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops</code>: the team template <code>templates/script.sh</code>, the generator <code>bin/newscript</code>, and the colleague’s <code>bin/buggy.sh</code>. ShellCheck itself is not installed there, so its messages appear in tables and in Run on your PC; every fix is really run.</p>
''' + cmdcard_u(['every new script'], ['copying an old script'])(
    'template', 'templates/script.sh', 'the team template',
    'Fifty lines with everything from Lessons 1.1 to 1.3: header with exit codes, safe mode, <code>log/info/debug/die/bad</code>, <code>run</code> for dry runs, a temp folder removed by <code>trap cleanup EXIT</code>, getopts for <code>-v -n -h</code>, and <code>main "$@"</code>. Placeholders <code>__NAME__</code> and <code>__DESC__</code> are filled by the generator.',
    'templates/script.sh  (copied, never edited for one script)', 'safe',
    [('__NAME__ / __DESC__', 'placeholders', 'generator fills'),
     ('run CMD', 'do or just log', '-n dry run'),
     ('tmp=$(mktemp -d)', 'temp folder', 'unique'),
     ('trap cleanup EXIT', 'always removed', 'any exit'),
     ('debug', 'only with -v', 'noise control'),
     ('VERSION', 'semver', '--version later')],
    dict(setup=SS, cmd="cd ~/ops\nwc -l < templates/script.sh\ngrep -nE '^(set|trap|main|readonly)' templates/script.sh\ngrep -cE '^[a-z]+\\(\\) *\\{|^[a-z]+\\(\\)' templates/script.sh | sed 's/^/functions: /'", note='One file holds the standard; change it once, every new script benefits.'),
    [('dev', [
        dict(situation='Read the run() and cleanup lines.', setup=SS, cmd="cd ~/ops; grep -nE '^(run|tmp|cleanup)' templates/script.sh", why='Three lines that prevent two whole classes of incidents.')]),
    ]
) + cmdcard_u(['starting any script'], ['hand-editing placeholders'])(
    'generator', 'bin/newscript NAME "desc"', 'create from the template',
    'The generator refuses to overwrite, replaces the placeholders with <code>sed</code>, makes the file executable and checks it with <code>bash -n</code>. The new script runs immediately: help, verbose, dry run and errors all work before you write a line.',
    "bin/newscript sync.sh 'sync reports to the share'", 'change',
    [('NAME', 'file in bin/', 'kebab or .sh'),
     ('"desc"', 'header line', 'one line'),
     ('exists → exit 1', 'no overwrite', 'safety'),
     ('chmod +x', 'executable', 'ready'),
     ('bash -n', 'syntax check', 'guard'),
     ('sed s|…|…|g', 'fill placeholders', '| as delimiter')],
    dict(setup=SS, cmd="cd ~/ops\nbin/newscript sync.sh 'sync reports to the share'\nsed -n '2,4p' bin/sync.sh\nbin/sync.sh -h | head -2\nbin/sync.sh -v 'data/nov orders.csv' 2>&1 | sed -E 's/^[0-9-]+ [0-9:]+ //; s|/tmp/tmp\\.[A-Za-z0-9]+|/tmp/tmp.XXXX|'", note='Timestamps and the random temp name are shortened so the output repeats.'),
    [('sys', [
        dict(situation='The generator will not overwrite.', setup=B, cmd="cd ~/ops; bin/newscript sync.sh 'again'; echo \"exit $?\"", why='Losing a finished script to a typo is a real incident.', expect='any'),
        dict(situation='Dry run and usage errors work at once.', setup=B, cmd="cd ~/ops; bin/sync.sh -n x 2>&1 | grep -o 'dry run: .*' | sed -E 's|/tmp/tmp\\.[A-Za-z0-9]+|/tmp/tmp.XXXX|'; bin/sync.sh 2>&1 | head -1; bin/sync.sh -z x 2>&1 | head -1", why='Features from the template, not new code.', expect='any')]),
    ]
) + cmdcard_u(['every review'], ['merging warnings unread'])(
    'quotes', 'SC2086 · SC2045 · SC2006', 'fix: quoting, ls loops, backticks',
    '<code>files=$(ls data/*.csv); for f in $files</code> splits <code>nov orders.csv</code> into two words (SC2045, SC2086). Loop over the glob directly and quote every <code>"$f"</code>; replace backticks with <code>$( )</code> (SC2006).',
    'for f in data/*.csv; do count=$(wc -l < "$f"); done', 'safe',
    [('for f in *.csv', 'glob, not ls', 'SC2045'),
     ('"$f"', 'quote', 'SC2086'),
     ('$( )', 'not backticks', 'SC2006'),
     ('[[ -e $f ]] || continue', 'no match', 'nullglob'),
     ('"${arr[@]}"', 'arrays quoted', 'SC2068'),
     ('printf %s', 'safe output', 'SC2059')],
    dict(setup=SS, cmd="cd ~/ops\necho '--- buggy (ls + unquoted):'\nfiles=$(ls data/*.csv); for f in $files; do wc -l < $f; done 2>&1 | sed 's/^/  /'\necho '--- fixed (glob + quotes):'\nfor f in data/*.csv; do echo \"  $f: $(wc -l < \"$f\") lines\"; done", note='The file name with a space breaks the buggy loop into data/nov and orders.csv.', expect='any'),
    [('dev', [
        dict(situation='Why quotes: count the words.', cmd="f='nov orders.csv'; printf '[%s] ' $f; echo; printf '[%s] ' \"$f\"; echo", why='Unquoted = 2 words; quoted = 1.')]),
    ]
) + cmdcard_u(['any cd or rm in a script'], ['cd without a check'])(
    'danger', 'SC2164 · SC2115 · SC2154', 'fix: cd and rm',
    'If <code>cd /tmp/work</code> fails, the script continues in the <i>current</i> folder (SC2164): add <code>|| exit 1</code> (or rely on <code>set -e</code>). <code>rm -rf $OUTDIR/*</code> with an unset OUTDIR becomes <code>rm -rf /*</code> (SC2115, SC2154): write <code>"${OUTDIR:?}"</code>, which stops the script when it is empty.',
    'cd /tmp/work || exit 1;  rm -rf -- "${OUTDIR:?OUTDIR not set}"/*', 'danger',
    [('cd DIR || exit', 'stop on failure', 'SC2164'),
     ('${VAR:?msg}', 'stop if empty', 'SC2115'),
     ('rm -- "…"', 'end of options', 'odd names'),
     ('set -u', 'unset = error', 'safety net'),
     ('pushd/popd', 'return reliably', 'subdirs'),
     ('( cd dir && … )', 'subshell', 'no cd leak')],
    dict(cmd="unset OUTDIR\necho \"the buggy line would run: rm -rf $OUTDIR/*\"\nbash -c 'rm -rf -- \"${OUTDIR:?OUTDIR not set}\"/*'; echo \"guarded: exit $?\"\nbash -c 'cd /tmp/nosuchdir; pwd' 2>&1\nbash -c 'cd /tmp/nosuchdir || exit 1; pwd'; echo \"checked cd: exit $?\"", note='We only echo the dangerous command. ${OUTDIR:?} stops it; the unchecked cd carries on in the old folder.', expect='any'),
    [('sec', [
        dict(situation='Comparison bug: > in [ ] (SC2071).', cmd="count=9; [ $count > 10 ] && echo 'bug: says 9 > 10'; ls -1 10 2>/dev/null && echo '(and it created a file called 10)'; rm -f 10; [ \"$count\" -gt 10 ] || echo 'fixed: 9 is not > 10'", why='> inside [ ] is a redirection.', expect='any')]),
    ]
) + cmdcard_u(['before every commit', 'in CI'], ['only testing by hand'])(
    'lint', 'bash -n · shellcheck · test run', 'a lint routine',
    'Three checks in order: <code>bash -n</code> (does it parse?), <code>shellcheck</code> (is it likely correct?), a dry and a real test run (does it behave?). Our build machine has no ShellCheck, so the routine below uses a small grep-based check for the three worst patterns; on your PC use the real tool.',
    'bash -n f.sh && shellcheck f.sh && ./f.sh -n test', 'safe',
    [('bash -n', 'syntax', 'fast'),
     ('shellcheck -S warning', 'bugs', 'CI'),
     ('shellcheck -x', 'follow source', 'libraries'),
     ('-f gcc', 'editor format', 'VS Code'),
     ('shfmt -d', 'format diff', 'style'),
     ('./f.sh -n', 'dry run', 'behaviour')],
    dict(setup=B, cmd="cd ~/ops\nmini_lint() { local f=$1 n=0\n  grep -nE '\\$\\(ls' \"$f\" && ((++n))\n  grep -nE '^\\s*cd [^|&]+$' \"$f\" && ((++n))\n  grep -nE 'rm -rf \\$[A-Za-z_]+/' \"$f\" && ((++n))\n  return $n; }\nfor f in bin/buggy.sh bin/sync.sh; do bash -n \"$f\" && echo \"$f: syntax ok\"; mini_lint \"$f\" | sed 's/^/   /'; echo \"$f: ${PIPESTATUS[0]} risky patterns\"; done", note='Not a replacement for ShellCheck, just the idea: a machine reads every script before a human merges it.', expect='any'),
    [('devops', [
        dict(situation='A git pre-commit hook (written, not installed here).', cmd="cat <<'EOF'\n#!/usr/bin/env bash\n# .git/hooks/pre-commit: lint staged shell scripts\nset -euo pipefail\nfor f in $(git diff --cached --name-only -- '*.sh'); do\n  bash -n \"$f\" && shellcheck -S warning \"$f\"\ndone\nEOF", why='Commits with warnings are refused.')]),
    ]
) + undo('Template and linter mistakes are easy to undo; the bugs they prevent are not.', [
    ('Generated the wrong name:', '<code>mv bin/old.sh bin/new.sh</code> and fix the header line.'),
    ('Template changed badly:', 'it is in git: <code>git checkout -- templates/script.sh</code>.'),
    ('False positive:', '<code># shellcheck disable=SC2086 # reason</code> on the line before, never for the whole file.'),
    ('A risky script already ran:', 'that is why <code>-n</code> exists: always dry-run first next time.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(setup=SS, cmd="cd ~/ops && sed 's|^rm \\(.*\\)$|echo \"would run: rm \\1\"|' bin/buggy.sh | bash", meaning='The buggy script (we replace its rm line with an echo: never run it for real). ls splits the spaced name, wc fails on the pieces, cd fails but the script goes on, rm would get /*, and the last test is a redirection.', fix='Apply the fixes from the cards (and run ShellCheck).'),
    dict(setup=SS, cmd="cd ~/ops && bin/newscript", meaning='Usage error from the generator.', fix="bin/newscript NAME 'description'"),
    dict(cmd="bash -c 'x=$(false) && echo set; local_demo(){ local y=$(false); echo \"status after local: $?\"; }; local_demo'", meaning='SC2155: local swallows the status of $( ).', fix='local y; y=$(cmd).'),
]) + qc('cd /data fails inside a script without set -e. What happens next?', 'The script keeps running in the previous folder; every later relative path is wrong.') + '''
'''
cards = cards + '</section>\n'

LN = [('SC2045', 'for f in $(ls …)', 'red'), ('SC2086', 'wc -l < $f', 'red'), ('SC2164', 'cd /tmp/work', 'amber'), ('SC2115', 'rm -rf $OUTDIR/*', 'red')]
def lstep(k):
    o = ''
    for i, (a, b, c) in enumerate(LN):
        o += label_box(14, 12 + i * 40, 330, 32, [f'{a}: {b}' if i > k else f'fixed: {["for f in data/*.csv", "wc -l < \"$f\"", "cd /tmp/work || exit 1", "rm -rf -- \"${OUTDIR:?}\"/*"][i]}'], c if i > k else 'green', 8)
    return o
see_cmds = [['$ shellcheck buggy.sh', ('4 warnings', 'err')], ['fix the loop', ('3 warnings', 'err')], ['fix the cd', ('… 1 warning', 'err')], ['fix the rm', ('no warnings', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@laptop: ~/ops', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Lint.', 'Loop.', 'cd.', 'rm.'])]
two = anim_two('Lint, fix, lint again', 'Behind the screen: four warnings turn green',
               'A terminal reruns ShellCheck after each fix until no warnings remain.',
               'Four warning boxes change to green fixed lines one by one.', see, [lstep(k) for k in range(4)],
               ['lint.', 'loop + quotes.', 'cd.', 'rm.'], ['lint', 'loop', 'cd', 'rm'])

def tr(k):
    o = t(180, 18, 'trap cleanup EXIT', 9.6, 'ink2', bold=True)
    rows = [('mktemp -d', '/tmp/tmp.Ab12 created', 'blue'), ('work … then', 'success, die, set -e or Ctrl+C', 'amber'), ('EXIT trap fires', 'cleanup runs', 'green'), ('result', 'temp folder gone', 'violet')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
s1 = anim_one('Animated example', 'Why trap EXIT in the template',
              'Clean-up that runs however the script ends.', 'trap cleanup EXIT', 'Rows: temp created, any exit, trap fires, folder gone.', [tr(k) for k in range(4)],
              ['create.', 'end.', 'trap.', 'clean.'], hid='scenario-trap')

dx = dissect('Layer by layer: three kinds of checking',
    'Each layer has a real command from our build machine.', [
    dict(key='syntax', name='Syntax', sub='bash -n', why='Does it parse?', how='Parser only.', impl='No execution.', used='Every save.',
         cmd="printf 'for i in 1 2; do\\n echo $i\\n' > s.sh; bash -n s.sh; echo \"exit $?\"", expect='any'),
    dict(key='lint', name='Meaning', sub='ShellCheck', why='Likely bugs.', how='Syntax tree + rules.', impl='Static.', used='CI.',
         cmd="f='a b'; set -- $f; echo \"unquoted gives $# words (SC2086 would warn)\""),
    dict(key='run', name='Behaviour', sub='-n, then real', why='Does it do the job?', how='Run it.', impl='Real effects.', used='Tests.',
         setup=B, cmd="cd ~/ops; bin/sync.sh -n x 2>&1 | grep -c 'dry run' | sed 's/^/dry-run lines: /'; ls /tmp | grep -c '^tmp\\.' | sed 's/^/temp folders left: /'"),
], hint='Syntax → meaning → behaviour. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Lint and fix, and the clean-up trap</h2>
''' + two + s1 + dx + qc('Which check would catch a missing done?', 'bash -n (a syntax error); ShellCheck too.') + '''
</section>
'''

VAR = variations('Fifteen more template and lint patterns. All were really run on our build machine.', [
    ('Template features', [
        dict(title='Verbose shows debug lines', setup=B, cmd="cd ~/ops; bin/sync.sh -v x 2>&1 | grep -c DEBUG", why='-v turns debug on.'),
        dict(title='Exit code of a usage error', setup=B, cmd="cd ~/ops; bin/sync.sh 2>/dev/null; echo $?", why='2.', expect='any'),
        dict(title='No temp folder left after a run', setup=B, cmd="cd ~/ops; before=$(ls /tmp | grep -c '^tmp\\.'); bin/sync.sh x 2>/dev/null; after=$(ls /tmp | grep -c '^tmp\\.'); echo \"before $before, after $after\"", why='trap EXIT cleaned up.'),
        dict(title='Clean-up even on die', cmd="t=$(mktemp -d); bash -c \"trap 'rm -rf $t' EXIT; exit 1\"; [[ -d $t ]] && echo still there || echo 'removed on failure'", why='EXIT runs on every exit.'),
        dict(title='Version string', setup=B, cmd="cd ~/ops; grep -o 'VERSION=.*' bin/sync.sh", why='Bump it when behaviour changes.'),
    ]),
    ('Generator', [
        dict(title='Two scripts, same structure', setup=B, cmd="cd ~/ops; bin/newscript clean.sh 'remove old reports' > /dev/null; diff <(sed 2d bin/sync.sh) <(sed 2d bin/clean.sh | sed 's/clean.sh/sync.sh/g') && echo 'identical apart from name and description'", why='Consistency for the whole team.'),
        dict(title='Placeholders all replaced?', setup=B, cmd="cd ~/ops; grep -c '__[A-Z]*__' bin/sync.sh || echo 'none left'", why='A check the generator could add.', expect='any'),
    ]),
    ('Fixes ShellCheck asks for', [
        dict(title='SC2181: test the command, not $?', cmd="if ! grep -q zzz /etc/hostname; then echo 'not found (no $? needed)'; fi", why='Cleaner and safe with set -e.'),
        dict(title='SC2155: split local and assignment', cmd="f(){ local x; x=$(false) || echo \"caught status $?\"; }; f", why='Status preserved.'),
        dict(title='SC2068: quote array expansions', cmd="a=('x y' z); printf '[%s] ' ${a[@]}; echo; printf '[%s] ' \"${a[@]}\"; echo", why='3 vs 2 elements.'),
        dict(title='SC2059: printf format from a variable', cmd="msg='100% done'; printf '%s\\n' \"$msg\"", why='Never printf \"$msg\".'),
        dict(title='SC2002: useless cat', cmd="printf 'a\\nb\\n' > f.txt; wc -l < f.txt", why='Redirect instead of cat f | wc.'),
        dict(title='SC2046: quote $( ) in arguments', cmd="touch 'my file'; ls -1 \"$(printf 'my file')\"", why='Unquoted $( ) splits too.'),
    ]),
    ('Lint routine', [
        dict(title='Syntax-check every script', setup=B, cmd="cd ~/ops; for f in bin/*; do bash -n \"$f\" && echo \"ok   $f\" || echo \"FAIL $f\"; done", why='Fast first gate.'),
        dict(title='Find scripts without safe mode', setup=B, cmd="cd ~/ops; grep -L 'set -euo pipefail' bin/*", why='buggy.sh is listed.', expect='any'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Templates and linting at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['template', 'repo'], 'blue', 8.6), '1. Team script repositories',
              'Ops teams keep a scripts repo with a template and a generator; every script has the same options and logs.', ['new', '*template', 'same shape']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['CI', 'lint'], 'green', 8.6), '2. CI lint jobs',
    'GitHub Actions and GitLab run ShellCheck on every pull request; warnings block the merge.', ['PR', '*shellcheck', 'merge']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['editor', 'VS Code'], 'amber', 8.6), '3. In the editor',
    'The ShellCheck extension underlines problems while typing, long before review.', ['type', '*underline', 'fix']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-n', 'safety'], 'violet', 8.6), '4. Dry runs for risky jobs',
    'Cleanup and migration scripts are always run with -n first; reviewers ask for the dry-run output.', ['-n', '*review', 'real run']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['hooks', 'pre-commit'], 'red', 8.6), '5. Pre-commit hooks',
    'The pre-commit framework runs shellcheck and shfmt before every git commit.', ['commit', '*hook', 'clean']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='New script', scenario='Start work.', setup=SS, cmd="cd ~/ops; bin/newscript report.sh 'daily report'", explain='From the template.'),
    dict(level='b', title='Syntax check', scenario='Before running.', setup=B, cmd="cd ~/ops; bash -n bin/sync.sh && echo ok", explain='bash -n.'),
    dict(level='i', title='Dry run', scenario='Preview.', setup=B, cmd="cd ~/ops; bin/sync.sh -n x 2>&1 | grep -c 'dry run'", explain='-n.'),
    dict(level='i', title='Scripts missing a shebang', scenario='Audit.', setup=B, cmd="cd ~/ops; for f in bin/*; do head -1 \"$f\" | grep -q '^#!' || echo \"$f\"; done; echo '(none)'", explain='First line.'),
    dict(level='a', title='Unquoted variables (rough)', scenario='Quick review.', setup=SS, cmd="cd ~/ops; grep -nE '[^\"]\\$[a-zA-Z_]+[^\"a-zA-Z_]' bin/buggy.sh | head -3", explain='ShellCheck does this properly.'),
], extra=build_up('fix buggy.sh', 'Riya applies the ShellCheck fixes one by one, running the result each time.', SS, [
    ("cd ~/ops; sed 's|^rm \\(.*\\)$|echo \"would run: rm \\1\"|' bin/buggy.sh | bash 2>&1 | head -4", '1. The original (rm line only echoed): broken on the spaced name, rm would hit /*.'),
    ("cd ~/ops; for f in data/*.csv; do echo \"Processing $f\"; count=$(wc -l < \"$f\"); done; echo \"count=$count\"", '2. Glob + quotes + $( ).'),
    ("cd ~/ops; mkdir -p /tmp/work-$$; cd /tmp/work-$$ || exit 1; pwd | sed 's/[0-9]*$/N/'", '3. Checked cd.'),
    ("cd ~/ops; OUTDIR=$(mktemp -d); touch \"$OUTDIR\"/x; rm -rf -- \"${OUTDIR:?}\"/*; ls -A \"$OUTDIR\" | wc -l; count=3; [ \"$count\" -gt 1 ] && echo 'has rows'", '4. Guarded rm, numeric test.'),
], cumulative=False, expect='any')) + VAR + which('Choosing the right check.', [
    ('Start a script', 'newscript from template', 'Complete.', 'Copy-paste.'),
    ('Syntax', 'bash -n', 'Instant.', 'Running it.'),
    ('Likely bugs', 'ShellCheck', 'Explains each.', 'Eyes only.'),
    ('Formatting', 'shfmt', 'Consistent.', 'Arguments in review.'),
    ('Risky actions', 'run() + -n', 'Preview.', 'Hope.'),
    ('Temp files', 'mktemp + trap EXIT', 'Always cleaned.', 'rm at the end.'),
]) + keys('Handy forms.', [
    ("bin/newscript NAME 'desc'", 'new script', 'generator'),
    ('bash -n f.sh', 'syntax', 'fast'),
    ('shellcheck -S warning f.sh', 'lint', 'CI'),
    ('# shellcheck disable=SC2086', 'one exception', 'with reason'),
    ('run rm -rf -- "${d:?}"', 'safe, previewable', 'template'),
    ('trap cleanup EXIT', 'temp files', 'always'),
]) + scriptit('lint-all.sh', 'Check every script in bin/: syntax with bash -n, ShellCheck if it is installed, and a warning for scripts without safe mode. Exit 1 if anything fails.',
'''#!/usr/bin/env bash
set -uo pipefail
mkdir -p demo/bin && cd demo        # two sample scripts to check
printf '#!/usr/bin/env bash\nset -euo pipefail\necho ok\n' > bin/good.sh
printf '#!/bin/bash\nfor f in $(ls); do echo $f\n' > bin/broken.sh
fails=0
have_sc=0; command -v shellcheck >/dev/null && have_sc=1
for f in bin/*; do
  if ! bash -n "$f" 2>/dev/null; then echo "FAIL syntax   $f"; ((++fails)); continue; fi
  if (( have_sc )) && ! shellcheck -S warning "$f" >/dev/null; then echo "FAIL lint     $f"; ((++fails)); continue; fi
  grep -q 'set -euo pipefail' "$f" || { echo "WARN no safe mode  $f"; ((++fails)); continue; }
  echo "ok            $f"
done
(( have_sc )) || echo "(shellcheck not installed: syntax and safe-mode checks only)"
echo "problems: $fails"
exit $(( fails > 0 ))''',
'<p>On our build machine ShellCheck is missing, so the script says so and still checks the rest.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>files=$(ls data/*.csv); for f in $files</code> splits <code>nov orders.csv</code> into two words (SC2045/SC2086), so <code>wc</code> gets “data/nov” and “orders.csv”: “No such file or directory”. <b>2.</b> <code>cd /tmp/work</code> without a check (SC2164) fails and the script continues in the old folder. <b>3.</b> <code>rm -rf $OUTDIR/*</code> with OUTDIR unset (SC2154/SC2115) expands to <code>rm -rf /*</code>; <code>"${OUTDIR:?}"</code> stops the script instead. A bonus fourth bug: <code>[ $count &gt; 1 ]</code> is a redirection that creates a file called <code>1</code> (SC2071).') + qc('What does ${OUTDIR:?} do when OUTDIR is empty?', 'Prints an error and stops the script (or the command) instead of expanding to nothing.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-anatomy-of-a-real-script/">Lessons 1.1</a>, <a href="../02-arguments-done-right-getopts-and-validation/">1.2</a> and <a href="../03-exit-codes-logging-and-stderr/">1.3</a>: this lesson puts them into one template.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
