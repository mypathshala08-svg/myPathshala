import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='10-functions-built-ins-and-tput', n='12.10',
    module_label='Module 12 · The shell environment and shell programming',
    title='Functions, built-ins, return values and tput for screen control',
    desc='Defining and calling shell functions, arguments ($1, $#, "$@"), return status vs output captured with $( ), local and global scope, dynamic scope, recursion, libraries loaded with source; built-ins vs keywords vs external commands (type, enable, help, command, builtin); trap on EXIT, ERR, INT, TERM and RETURN; tput clear, cup, cols, lines, bold, setaf, sgr0 with a real recorded screen; class-note examples run; 30+ runnable examples and variations.',
    og_desc='Bash functions, local variables, return vs echo, built-ins, trap and tput, with real outputs and 30+ examples.',
    minutes=45, level='Beginner → Advanced',
    lead='Functions name a block of commands, take arguments, return a status and print data; local keeps their variables private. Built-ins run inside bash, trap cleans up on exit or Ctrl+C, and tput controls the screen. Many runnable examples.',
    chips=['Scope animated', 'return vs echo', 'trap and tput', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Functions: arguments, status and data
greet() { echo "Hello, $1!"; }
square() { echo $(( $1 * $1 )); }
is_even() { (( $1 % 2 == 0 )); }
greet Riya
x=$(square 7)
echo "7 squared is $x"
for n in 4 9; do
  if is_even $n; then echo "$n is even"; else echo "$n is odd"; fi
done
"""

RUN = dict(
    heading='Three small functions',
    intro='<p>One prints, one returns data through output, one returns a status used by if.</p>',
    code=MAIN,
    anno=[('x=$(square 7)', 'Capture the printed result.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which function is used in if?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does the last echo print? Then run.',
             code="v=outside\nf() { v=inside; }\nf\necho \"$v\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> make the function print hi.',
             code="f() { echo hi }\nf\n", expect='any'),
        dict(label='4 · Your turn', hint='Write add() that prints the sum of its two arguments.',
             code="add() { echo $(( $1 + $2 )); }\necho \"sum: $(add 12 30)\"\n"),
        dict(label='5 · Challenge', hint='Make a temporary file that is deleted when the script ends.',
             code="tmp=$(mktemp)\ntrap 'rm -f \"$tmp\"; echo removed' EXIT\necho data > \"$tmp\"; cat \"$tmp\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: colours and functions',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · The 8 basic colours', cmd='for c in 0 1 2 3 4 5 6 7; do tput setaf $c; echo "colour $c"; done; tput sgr0', output='colour 0 … colour 7 (black, red, green, yellow, blue, magenta, cyan, white)', note='Typical: you see each line in its colour.'),
        dict(title='2 · Your screen size', cmd='tput cols; tput lines', output='120\n32', note='Typical: changes when you resize the window.'),
        dict(title='3 · How many functions does your shell have?', cmd='declare -F | wc -l', output='123', note='Typical: mostly bash-completion functions.'),
        dict(title='4 · tput version', cmd='tput -V', output=pc('tput -V'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A function call, line by line',
    intro='<p>Step through: a global, a local, a call and a return status.</p>',
    code='''total=0
add() {
  local n=$1
  total=$(( total + n ))
  (( n > 0 ))
}
add 5
add -2
echo "total $total, last status $?"
''',
    notes={1: 'A global.', 7: 'Call :: n=5 is local; total becomes 5.', 8: 'Call :: n=-2; status 1 (not > 0).', 9: 'The echo itself runs after add, so $? is add’s status: 1.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a logging helper, a retry wrapper and a clean-up trap.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='A logging helper with levels',
         problem='<p>Write log LEVEL MESSAGE that prints “LEVEL: MESSAGE” and sends ERROR to stderr.</p>',
         inp='messages', approach=['case on $1.', 'shift.', '>&2.'],
         code='''log() { local lvl=$1; shift; if [ "$lvl" = ERROR ]; then echo "$lvl: $*" >&2; else echo "$lvl: $*"; fi; }
log INFO "backup started"
log ERROR "disk full" 2>&1
''', notes={2: 'stdout.', 3: 'stderr (shown with 2>&1).'}, tryit='Add a timestamp with date +%T.'),
    dict(level='i', tag='DevOps', title='A retry wrapper',
         problem='<p>retry N CMD… runs CMD up to N times until it succeeds; the test command succeeds on the 3rd try.</p>',
         inp='a flaky command', approach=['"$@" runs the command.', 'return 0/1.'],
         code='''n=0; flaky() { n=$((n + 1)); [ $n -ge 3 ]; }
retry() { local max=$1 i; shift; for ((i=1; i<=max; i++)); do "$@" && { echo "ok on try $i"; return 0; }; done; echo "failed $max times"; return 1; }
retry 5 flaky; retry 2 false
''', notes={3: 'Third try works; false never does.'}, expect='any', tryit='Add sleep $i between tries.'),
    dict(level='a', tag='Security', title='Clean up secrets on any exit',
         problem='<p>Write a secret to a temp file, use it, and make sure it is deleted even if the script fails.</p>',
         inp='nothing', approach=['mktemp.', 'trap EXIT.', 'set -e.'],
         code='''bash -c 'set -e
s=$(mktemp); trap "rm -f \\"\\$s\\"; echo secret file removed" EXIT
echo "token=abc123" > "$s"; chmod 600 "$s"
grep -q token "$s" && echo "using secret"
false
echo "never printed"'
''', notes={1: 'The whole script.'}, expect='any', tryit='Remove the trap and look in /tmp afterwards.'),
]

QUIZ = mix([
    dict(q='How do you call a function greet with the argument Riya?', options=['greet(Riya)', 'greet Riya', 'call greet Riya', '$greet Riya'], answer=1, why='Like a command.'),
    dict(q='Inside a function, $1 is…', options=['the script’s first argument', 'the function’s first argument', 'the function name', 'empty'], answer=1, why='Its own.'),
    dict(q='How do you return the number 500 from a function?', options=['return 500', 'echo 500 and capture with $( )', 'exit 500', 'local 500'], answer=1, why='return is 0–255.'),
    dict(q='What does local do?', options=['exports', 'makes the variable private to the function', 'makes it readonly', 'nothing in bash'], answer=1, why='Scope.'),
    dict(q='Which is a built-in?', options=['ls', 'cd', 'grep', 'tput'], answer=1, why='Changes the shell.'),
    dict(q='trap … EXIT runs…', options=['only on success', 'whenever the shell exits (except kill -9)', 'on Ctrl+Z', 'never in scripts'], answer=1, why='Clean-up.'),
    dict(q='tput setaf 2 sets…', options=['bold', 'green text', 'cursor row 2', 'two columns'], answer=1, why='ANSI foreground 2.'),
    dict(q='tput cup 5 10 moves the cursor to…', options=['column 5 row 10', 'row 5 column 10', 'line 15', 'nowhere'], answer=1, why='Row first.'),
])

REVISION = [
    'name() { cmds; } (or function name { …; }); call with name args; define before use; ; before }.',
    'Inside: $1 … $# "$@" are the function’s; $0 is still the script; FUNCNAME is its name.',
    'return N = status 0–255 (used by if); data = echo + $( ); messages to >&2.',
    'Variables are global unless local; bash locals are visible to called functions; recursion needs locals.',
    'Built-ins (cd read trap local printf) run inside bash; type -t, help, enable, command, builtin.',
    'trap \'…\' EXIT INT TERM ERR RETURN; trap - SIG; SIGKILL cannot be trapped. tput clear cup cols lines bold setaf sgr0.',
]

FAQ = [
    ('How do I create a function in bash?', 'name() { commands; } — then call it like a command: name arg1 arg2.'),
    ('How do I pass arguments to a bash function?', 'Write them after the name; inside the function use $1, $2, $# and "$@".'),
    ('How do I return a value from a bash function?', 'Print it (echo) and capture with $(function); use return only for a 0–255 status.'),
    ('What does local do in bash?', 'Declares a variable that exists only inside the function (and functions it calls).'),
    ('What is the difference between a builtin and an external command?', 'A builtin runs inside the shell without a new process; an external command is a program found in PATH.'),
    ('What is trap in bash?', 'A builtin that runs commands when the shell receives a signal or exits, e.g. trap \'rm -f $tmp\' EXIT.'),
    ('What is tput used for?', 'Terminal control: clear the screen, move the cursor, get its size, set bold and colours in a terminal-independent way.'),
]

PRACTICE_INTRO = 'Small function tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Hello function', stmt='A function hi that prints Hello CDAC; call it.', inp='nothing', code="hi() { echo 'Hello CDAC'; }; hi\n", explain='Define, call.'),
    dict(level='easy', title='Cube', stmt='cube 3 prints 27.', inp='an argument', code="cube() { echo $(( $1 ** 3 )); }; cube 3\n", explain='**.'),
    dict(level='easy', title='Status', stmt='positive N returns 0 for N > 0; test it with 5.', inp='an argument', code="positive() { (( $1 > 0 )); }; positive 5 && echo yes\n", explain='Status.'),
    dict(level='medium', title='Local', stmt='Show that a local variable does not leak.', inp='nothing', code="f() { local a=1; }; f; echo \"[${a:-}]\"\n", explain='[].'),
    dict(level='medium', title='Count args', stmt='nargs prints how many arguments it got (3).', inp='arguments', code="nargs() { echo $#; }; nargs a 'b c' d\n", explain='$# of the function.'),
    dict(level='medium', title='Average', stmt='avg prints the integer average of its arguments (10 20 30).', inp='numbers', code="avg() { local s=0 n; for n; do s=$((s+n)); done; echo $((s / $#)); }; avg 10 20 30\n", explain='20.'),
    dict(level='business', title='Trap', stmt='Print “done” on exit of a small bash -c script that exits 2.', inp='nothing', code="bash -c 'trap \"echo done\" EXIT; exit 2'; echo \"status $?\"\n", explain='EXIT trap.'),
    dict(level='business', title='Power of two', stmt='Recursive pow2 N prints 2^N (for 8).', inp='an argument', code="pow2() { (( $1 == 0 )) && { echo 1; return; }; echo $(( 2 * $(pow2 $(( $1 - 1 ))) )); }; pow2 8\n", explain='256.'),
]

SCN_INTRO = 'Interview questions about functions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Write a function that adds two numbers”', 'Very common.', 'arguments + output?',
        '''<ul>
          <li><code>add() { echo $(( $1 + $2 )); }</code></li>
          <li><code>sum=$(add 3 4)</code></li>
          <li>Explain why not return.</li>
        </ul>''', 'return $(( $1 + $2 )) for big numbers.') +
    scn('Service company', 'Junior', '“return vs exit?”', 'Follow-up.', 'scope of each?',
        '''<ol>
          <li>return ends the function, sets $?.</li>
          <li>exit ends the whole script.</li>
          <li>Both 0–255.</li>
        </ol>''', 'using exit in a library function.') +
    scn('DevOps', 'Mid-level', 'Temp files pile up in /tmp', 'A script creates files and fails before cleaning.', 'trap?',
        '''<ul>
          <li><code>tmp=$(mktemp); trap 'rm -f "$tmp"' EXIT</code></li>
          <li>Runs on success, error and Ctrl+C.</li>
          <li>Not on kill -9: also clean old temp files with a timer.</li>
        </ul>''', 'rm at the last line only.') +
    scn('Platform', 'Senior', 'Shared bash library for 30 teams', 'Inconsistent logging and errors.', 'design?',
        '''<ul>
          <li>common.sh with log/die/retry/require_cmd, all variables local, no side effects when sourced, guard against double loading.</li>
          <li>Version it in Git; shellcheck in CI.</li>
          <li>Colours only when [ -t 1 ].</li>
        </ul>''', 'copy-pasting helpers into every script.')
) + interview([
    ('How to list all functions?', 'declare -F.'),
    ('How to show a function’s code?', 'declare -f name (or type name).'),
    ('How to remove a function?', 'unset -f name.'),
    ('What is a builtin?', 'A command implemented inside the shell.'),
    ('How to call the real ls from a function named ls?', 'command ls.'),
    ('Which signal can’t be trapped?', 'SIGKILL (and SIGSTOP).'),
    ('How to reset colours after tput?', 'tput sgr0.'),
], [
    ('RHCSA (EX200)', 'Use functions and control structures in scripts.'),
    ('LFCS', 'Shell scripting: functions, trap.'),
    ('CompTIA Linux+', 'Functions, built-ins, signals and traps.'),
]) + distro('Functions are POSIX; local and some traps are bash extras.', [
    ('f() { …; }', 'yes', 'yes', 'yes', 'Git Bash'),
    ('function f', 'bash/ksh', 'bash', 'bash/zsh', '-'),
    ('local', 'bash, dash', 'bash', 'bash/zsh', '-'),
    ('trap ERR / RETURN', 'bash', 'bash', 'bash/zsh', '-'),
    ('tput', 'ncurses', 'ncurses', 'ncurses', 'Windows Terminal: ANSI codes'),
]) + teaser('12.11', 'Riya’s functions work, but a line like rm $files/*.log {a,b} ~ $(date) still surprises her: in what order does bash expand braces, tildes, variables, commands and wildcards? Plus eval, and pushd/popd to jump between folders. Next: metacharacters, expansion order and directory stacks.')

CHEATSHEET = cheatsheet('Functions, trap, tput', [
    ('Define / call', [('f() { …; }', 'define'), ('f a b', 'call'), ('$1 $# "$@"', 'args'), ('declare -f / -F', 'show / list'), ('unset -f f', 'remove')]),
    ('Results', [('return N', 'status 0–255'), ('x=$(f)', 'data'), ('>&2', 'messages'), ('local v', 'private')]),
    ('Built-ins', [('type -t', 'what is it'), ('help cmd', 'help'), ('command x', 'skip function'), ('builtin cd', 'force builtin')]),
    ('trap / tput', [("trap '…' EXIT", 'clean-up'), ('INT TERM ERR', 'signals'), ('tput clear / cup r c', 'screen'), ('tput setaf N / sgr0', 'colour / reset')]),
])

MINDMAP = mindmap('Functions', [
    ('Define', 'blue', ['f() { ; }', 'top of script', 'source lib']),
    ('Input', 'green', ['$1 $#', '"$@"', 'shift']),
    ('Output', 'amber', ['return status', 'echo data', '$( )']),
    ('Scope', 'red', ['global default', 'local', 'recursion']),
    ('Built-ins', 'violet', ['cd read trap', 'type help', 'command']),
    ('trap/tput', 'acc', ['EXIT INT TERM', 'cup clear', 'setaf sgr0']),
])

LAB = lab('a helper library', 'Build the lab, write <code>~/lab1210/lib.sh</code> with the four functions, then run the checker (it sources your file).',
    setup='''mkdir -p ~/lab1210 && cd ~/lab1210 && rm -f lib.sh''',
    tasks=['<code>is_number X</code>: returns 0 if X is a whole number (digits only), 1 otherwise.',
           '<code>sum A B …</code>: prints the sum of all its arguments.',
           '<code>max A B …</code>: prints the largest argument, using <b>local</b> variables only (no global left behind).',
           '<code>with_temp CMD</code>: creates a temp file, exports its name as TMPF, runs CMD, and removes the file when the function returns (use trap … RETURN or remove it at the end).'],
    solution='''cat > lib.sh <<'EOF'
is_number() { [[ $1 =~ ^[0-9]+$ ]]; }
sum() { local t=0 n; for n in "$@"; do t=$((t + n)); done; echo "$t"; }
max() { local m=$1 v; shift; for v in "$@"; do (( v > m )) && m=$v; done; echo "$m"; }
with_temp() { local f; f=$(mktemp); export TMPF=$f; "$@"; rm -f "$f"; }
EOF''',
    check='''cd ~/lab1210
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f lib.sh ] && source ./lib.sh
ok "1 is_number" 'declare -F is_number >/dev/null && is_number 2026 && ! is_number 20x6'
ok "2 sum"       '[ "$(sum 10 20 30 5 2>/dev/null)" = 65 ]'
unset m v
ok "3 max"       '[ "$(max 12 99 7 2>/dev/null)" = 99 ] && max 1 2 >/dev/null 2>&1 && [ -z "${m:-}${v:-}" ]'
ok "4 with_temp" 'declare -F with_temp >/dev/null && with_temp sh -c "[ -f \\"\\$TMPF\\" ] && echo inside > \\"\\$TMPF\\"" && [ ! -e "$TMPF" ]' ''')
