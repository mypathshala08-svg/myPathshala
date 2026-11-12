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
    module='01-script-craft', lesson='01-anatomy-of-a-real-script', n='1.1',
    module_label='Module 1 · Script craft',
    title='Anatomy of a real script: shebang, safe header, main and usage',
    desc='The eight parts of a production Bash script: shebang, header comment, set -euo pipefail, readonly constants, usage() and die(), small functions with local variables, main and main "$@"; exit codes 0, 1, 2, 126, 127; stderr; quoting; bash vs sh (dash); with every version really run and 30+ examples.',
    og_desc='Turn a one-line script into a real one: shebang, set -euo pipefail, usage, die, main "$@", exit codes and quoting.',
    minutes=35, level='Beginner → Intermediate',
    lead='Commands in a file are not yet a script a team can trust. Eight parts, always in the same order, make it explain itself, check its input and fail loudly.',
    chips=['Eight-part skeleton', 'pipefail animated', 'Real runs of every version', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """#!/usr/bin/env bash
set -euo pipefail
readonly PROG=report.sh

usage() { echo "Usage: $PROG FILE"; }
die()   { echo "$PROG: error: $*" >&2; exit 1; }

main() {
  [[ $# -eq 1 ]] || { usage >&2; exit 2; }
  [[ -r $1 ]] || die "cannot read '$1'"
  echo "reading $1"
}

printf 'id,city\\n1,Pune\\n' > orders.csv
( main orders.csv ) && echo "exit 0"
( main ) || echo "exit $?"
( main nosuch.csv ) || echo "exit $?"
"""

RUN = dict(
    heading='The skeleton, live',
    intro='<p>Three calls of the same main: good input, no input, a missing file. Each runs in ( ) so an exit does not end the whole demo.</p>',
    code=MAIN,
    anno=[('>&2', 'Messages to stderr.'), ('exit 2', 'Usage error.'), ('|| echo', 'Under set -e a failure must be handled, or the demo itself stops.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which exit codes appear?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what is the status of the pipeline?',
             code="false | true; echo \"without pipefail: $?\"\nset -o pipefail\nfalse | true; echo \"with pipefail: $?\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the loop breaks the spaced name in two. Quote it.',
             code="set -- 'my file.csv' b.csv\nfor f in $@; do echo \"<$f>\"; done\n"),
        dict(label='4 · Your turn', hint='Add a -h branch that prints usage and exits 0.',
             code="usage(){ echo 'Usage: demo FILE'; }\nmain(){ [[ ${1:-} == -h ]] && { usage; return 0; }; echo \"file: $1\"; }\nmain -h; main data.csv\n"),
        dict(label='5 · Challenge', hint='Print the script name without its path.',
             code="p=/opt/tools/bin/backup.sh\necho \"${p##*/}\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Create the script in your own terminal (WSL, a VM or a Linux PC). Outputs below are from our build machine.</p>',
    items=[
        dict(title='1 · Create and run', cmd="nano report.sh   # paste the script from this lesson\nchmod +x report.sh\n./report.sh orders.csv", output='Delhi       800\nMumbai     1200\nPune       1449', note='Real output on our build machine.'),
        dict(title='2 · Wrong usage', cmd="./report.sh; echo $?", output='Usage: report.sh [-h] FILE\nPrint the total amount of paid orders per city.\n  -h   show this help\n2', note='Real output.'),
        dict(title='3 · What is sh?', cmd="readlink -f /bin/sh", output='/usr/bin/dash   (Ubuntu/Debian)\n/usr/bin/bash   (Fedora/RHEL)', note='Typical.'),
        dict(title='4 · Windows line endings', cmd="file report.sh\nsed -i 's/\\r$//' report.sh", output='report.sh: Bourne-Again shell script, ASCII text executable, with CRLF line terminators', note='Typical when a script was saved on Windows.'),
    ],
)

TRACE = dict(
    heading='main and its guards, line by line',
    intro='<p>Step through main with no argument.</p>',
    code='''usage() { echo "Usage: report.sh FILE" >&2; }
main() {
  if [[ $# -ne 1 ]]; then usage; return 2; fi
  echo "would read $1"
}
main
echo "status $?"
''',
    notes={3: '$# is 0, so usage and status 2.', 7: 'The caller sees 2.'},
)

WORKED_INTRO = 'Three scripts upgraded to the real anatomy.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='A disk-check script with a guard',
         problem='<p>Warn when a given directory uses more than a limit (KB); usage error without arguments.</p>',
         inp='a directory and a limit', approach=['Guard $#, then du.'],
         code='''check() {
  [[ $# -eq 2 ]] || { echo "usage: check DIR LIMIT_KB" >&2; return 2; }
  local used; used=$(du -sk "$1" | cut -f1)
  (( used > $2 )) && echo "WARN $1 uses ${used} KB" || echo "OK $1"
}
mkdir -p d; head -c 50000 /dev/zero > d/f; check d 10; check d 100; check d; echo "exit $?"
''', notes={2: 'Usage error = 2.', 3: 'local, then assign: keeps du’s status.'}, tryit='Add -h.'),
    dict(level='i', tag='Dev', title='Safe mode catches a typo',
         problem='<p>Show how -u stops a dangerous typo before a delete.</p>',
         inp='nothing', approach=['set -u in a subshell.'],
         code='''( set -u; build_dir=/tmp/build; echo "would run: rm -rf $buld_dir/*" ) 2>&1; echo "exit $?"
( build_dir=/tmp/build; echo "without -u: rm -rf $buld_dir/*" )
''', notes={1: 'Stops with an error.', 2: 'Expands to rm -rf /* without -u!'}, tryit='Fix the typo.'),
    dict(level='a', tag='CI', title='Pipeline failure detection',
         problem='<p>Make a pipeline whose first step fails stop the job.</p>',
         inp='nothing', approach=['pipefail + -e.'],
         code='''( set -e; cat nosuch.log 2>/dev/null | wc -l; echo "default: continued" )
( set -eo pipefail; cat nosuch.log 2>/dev/null | wc -l; echo "never printed" ); echo "pipefail exit $?"
''', notes={1: 'wc succeeds, so -e does not trigger.', 2: 'Now the job stops.'}, tryit='Use grep instead of cat.'),
]

QUIZ = mix([
    dict(q='The best first line for a Bash script:', options=['#!/bin/sh', '#!/usr/bin/env bash', '# bash', 'bash:'], answer=1, why='Finds bash anywhere.'),
    dict(q='set -u makes Bash…', options=['run unsafely', 'treat unset variables as errors', 'print commands', 'update'], answer=1, why='nounset.'),
    dict(q='Without pipefail, the status of a | b | c is…', options=['a’s', 'b’s', 'c’s', 'the worst'], answer=2, why='The last.'),
    dict(q='Error messages should go to…', options=['stdout', 'stderr', '/dev/null', 'a variable'], answer=1, why='>&2.'),
    dict(q='Exit code for wrong usage by convention:', options=['0', '1', '2', '127'], answer=2, why='2.'),
    dict(q='"$@" vs $*:', options=['same', '"$@" keeps each argument separate', '$* is safer', '"$@" counts'], answer=1, why='Words preserved.'),
    dict(q='Why call main "$@" on the last line?', options=['speed', 'all functions defined first', 'required by bash', 'colour'], answer=1, why='And half-downloads do nothing.'),
    dict(q='Exit code 126 means…', options=['not found', 'not executable', 'killed', 'success'], answer=1, why='Permission.'),
])

REVISION = [
    'Eight parts: shebang, header, set -euo pipefail, readonly constants, usage/die, work functions, main, main "$@".',
    '-e stops on failures, -u on unset variables, pipefail on any failing pipeline step.',
    'Messages to stderr (>&2); exit 0 success, 1 error, 2 usage; 126 not executable, 127 not found.',
    'Quote every variable; pass arguments on with "$@"; use ${1:-} under -u.',
    '#!/usr/bin/env bash and ./script.sh; sh on Ubuntu is dash.',
    'bash -n checks syntax; ${0##*/} gives the script name.',
]

FAQ = [
    ('What is the best shebang for Bash scripts?', '#!/usr/bin/env bash finds bash on the PATH; #!/bin/bash is also fine on Linux.'),
    ('What does set -euo pipefail mean?', 'Exit on errors, error on unset variables, and fail a pipeline if any command in it fails.'),
    ('Why does my script exit 0 even after an error?', 'The exit code is that of the last command; use set -e, pipefail and explicit exit 1.'),
    ('Why use a main function in Bash?', 'One clear entry point, local variables, and nothing runs until the whole file is read.'),
    ('Why does [[ not found appear?', 'The script ran under sh (dash); use a bash shebang and run it with ./ or bash.'),
    ('How do I print errors in a shell script?', 'echo "message" >&2, then exit with a non-zero code.'),
    ('What does $@ mean in Bash?', 'All positional arguments; quoted as "$@" each stays a separate word.'),
]

PRACTICE_INTRO = 'Small tasks on script anatomy. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Script name', stmt='Print backup.sh from /opt/bin/backup.sh.', inp='a path', code="p=/opt/bin/backup.sh; echo ${p##*/}\n", explain='Remove up to the last /.'),
    dict(level='easy', title='stderr', stmt='Print an error to stderr only.', inp='nothing', code="echo 'error: no file' >&2\n", explain='>&2.'),
    dict(level='easy', title='Argument count', stmt='Count the arguments a b c.', inp='three args', code="set -- a b c; echo $#\n", explain='3.'),
    dict(level='medium', title='Default', stmt='Print level=info when LEVEL is unset, under set -u.', inp='nothing', code="set -u; echo \"level=${LEVEL:-info}\"\n", explain=':- default.'),
    dict(level='medium', title='Pipefail', stmt='Show the pipeline status of false | true with pipefail.', inp='nothing', code="set -o pipefail; false | true; echo $?\n", explain='1.'),
    dict(level='medium', title='Guard', stmt='Return 2 and print usage when no argument is given.', inp='nothing', code="f(){ [[ $# -ge 1 ]] || { echo 'usage: f ARG' >&2; return 2; }; }; f; echo $?\n", explain='2.'),
    dict(level='business', title='Quoted loop', stmt='Print each argument in <>, keeping spaces.', inp='two args', code="set -- 'q3 report.csv' x.csv; for a in \"$@\"; do echo \"<$a>\"; done\n", explain='"$@".'),
    dict(level='business', title='Exit codes', stmt='Show 127 for a missing command.', inp='nothing', code="nosuchcmd 2>/dev/null; echo $?\n", explain='127.'),
]

SCN_INTRO = 'Interview and review questions about script structure.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is a shebang?”', 'Very common.', 'and why env?',
        '''<ul>
          <li>First line #! naming the interpreter.</li>
          <li>/usr/bin/env bash finds bash on the PATH.</li>
          <li>Without it the caller’s shell runs the file.</li>
        </ul>''', 'saying it is a comment.') +
    scn('Service company', 'Junior', 'Cron job “succeeds” but did nothing', 'Logs empty.', 'why?',
        '''<ol>
          <li>Exit code of the last command was 0.</li>
          <li>Add set -euo pipefail and die/exit 1.</li>
          <li>Send errors to stderr so cron mails them.</li>
        </ol>''', 'adding more echo.') +
    scn('Product company', 'Mid-level', 'Review a teammate’s 200-line script', 'Top-level code everywhere.', 'what do you ask for?',
        '''<ul>
          <li>Header, safe mode, usage.</li>
          <li>Functions with local, main "$@".</li>
          <li>Quoting; consider Python if logic is heavy.</li>
        </ul>''', 'rewriting it yourself silently.') +
    scn('Platform', 'Senior', 'A script deleted /', 'Post-mortem.', 'root cause and guard?',
        '''<ul>
          <li>rm -rf "$DIR/"* with DIR unset or misspelled.</li>
          <li>set -u, ${DIR:?} and checks before deletes.</li>
          <li>Code review and ShellCheck in CI.</li>
        </ul>''', 'blaming the junior.')
) + interview([
    ('What is $0?', 'The script’s name/path.'),
    ('What is $?', 'Exit status of the last command.'),
    ('Difference between "$@" and "$*"?', 'Separate words vs one string.'),
    ('How do you check syntax only?', 'bash -n script.sh.'),
    ('When does set -e not stop?', 'In if, while, && / || lists and after !.'),
    ('Exit code 127?', 'Command not found.'),
    ('Why not #!/bin/sh with [[ ]]?', 'sh may be dash, without [[ ]].'),
], [
    ('LFCS', 'Write and run simple shell scripts.'),
    ('RHCSA', 'Create simple shell scripts (conditionals, loops, arguments).'),
    ('CompTIA Linux+', 'Shell script elements, exit codes.'),
]) + distro('What sh is, per distribution.', [
    ('/bin/sh', 'dash', 'bash', 'bash', 'bash'),
    ('Default login shell', 'bash', 'bash', 'bash', 'bash'),
    ('bash path', '/usr/bin/bash', '/usr/bin/bash', '/usr/bin/bash', '/usr/bin/bash'),
    ('macOS note', '-', '-', '-', 'zsh default; bash 3.2'),
    ('Shebang to use', '#!/usr/bin/env bash', 'same', 'same', 'same'),
]) + teaser('1.2', 'report.sh takes one file. Real tools take options: -v, -o FILE, --city Pune. Next: getopts, long options, defaults and validation.')

CHEATSHEET = cheatsheet('Script anatomy', [
    ('Top', [('#!/usr/bin/env bash', 'line 1'), ('# what · usage', 'header'), ('set -euo pipefail', 'safe'), ('readonly PROG=${0##*/}', 'name')]),
    ('Helpers', [('usage()', 'help'), ('die() … >&2; exit 1', 'errors'), ('local var', 'in functions'), ('"$@"', 'pass args')]),
    ('Guards', [('[[ $# -eq 1 ]]', 'count'), ('[[ -r $f ]]', 'readable'), ('${1:-}', 'safe under -u'), ('exit 2', 'usage')]),
    ('Checks', [('bash -n f.sh', 'syntax'), ('chmod +x', '126'), ('readlink -f /bin/sh', 'dash?'), ("sed -i 's/\\r$//'", 'CRLF')]),
])

MINDMAP = mindmap('Real script', [
    ('Start', 'blue', ['shebang', 'header', 'safe mode']),
    ('Config', 'amber', ['readonly', 'defaults', '${0##*/}']),
    ('Messages', 'violet', ['usage', 'die', 'stderr']),
    ('Logic', 'green', ['functions', 'local', 'main "$@"']),
    ('Exit', 'red', ['0 / 1 / 2', '126 / 127', 'pipefail']),
    ('Quoting', 'acc', ['"$var"', '"$@"', 'spaces']),
])

LAB = lab('upgrade a script', 'Build the lab (it creates <code>~/lab11/count.sh</code>, a careless one-liner, and some data), make it a real script, then run the checker.',
    setup='''rm -rf ~/lab11; mkdir -p ~/lab11 && cd ~/lab11
printf 'id,city,amount,status\\n1,Pune,450,paid\\n2,Mumbai,1200,paid\\n3,Pune,300,failed\\n' > 'nov orders.csv'
echo 'grep -c paid $1' > count.sh''',
    tasks=['Rewrite <code>~/lab11/count.sh</code> with a bash shebang, <code>set -euo pipefail</code>, and a <code>main "$@"</code> call on its last line; make it executable.',
           'With no argument it must print a line starting with <code>Usage:</code> to <b>stderr</b> and exit <b>2</b>.',
           'With a missing file it must print an error to stderr and exit <b>1</b>.',
           'With <code>\'nov orders.csv\'</code> (a name with a space) it must print <code>2</code> (the number of paid orders) and exit 0.'],
    solution='''cat > count.sh <<'EOF'
#!/usr/bin/env bash
# count.sh - count paid orders in a CSV
set -euo pipefail
readonly PROG=${0##*/}
die() { echo "$PROG: error: $*" >&2; exit 1; }
main() {
  [[ $# -eq 1 ]] || { echo "Usage: $PROG FILE" >&2; exit 2; }
  [[ -r $1 ]] || die "cannot read '$1'"
  grep -c ',paid$' "$1"
}
main "$@"
EOF
chmod +x count.sh''',
    check='''cd ~/lab11
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 structure" 'head -1 count.sh | grep -q "^#!.*bash" && grep -q "set -euo pipefail" count.sh && tail -1 count.sh | grep -q "^main \\"\\$@\\"" && [ -x count.sh ]'
ok "2 usage"     './count.sh 2>e >o; [ $? -eq 2 ] && grep -q "^Usage:" e && [ ! -s o ]'
ok "3 missing"   './count.sh nosuch.csv 2>e >o; [ $? -eq 1 ] && [ -s e ] && [ ! -s o ]'
ok "4 spaces"    '[ "$(./count.sh "nov orders.csv" 2>/dev/null)" = 2 ]' ''')
