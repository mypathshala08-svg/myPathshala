import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

FN = r"""rm -rf ~/fn; mkdir -p ~/fn/logs; cd ~/fn
printf 'GET /a 200\nGET /b 500\nGET /c 500\n' > logs/app.log
cat > lib.sh <<'EOF'
# lib.sh: shared helpers
log()  { echo "[$(date +%H:%M:%S)] $*"; }
die()  { echo "ERROR: $*" >&2; exit 1; }
is_number() { [[ $1 =~ ^[0-9]+$ ]]; }
EOF"""
T = 'TERM=xterm-256color '
BOX = r"""rm -rf ~/tp; mkdir -p ~/tp; cd ~/tp
cat > box.sh <<'EOF'
#!/bin/bash
clear
tput cup 1 4;  echo "+----------------------+"
tput cup 2 4;  echo "|  MyPhatshala backup  |"
tput cup 3 4;  echo "+----------------------+"
tput cup 5 4;  echo "screen: $(tput cols) x $(tput lines)"
tput cup 6 4;  printf 'status: '; tput bold; echo 'OK'; tput sgr0
tput cup 8 0
EOF
printf '%s\n' 'PS1="riya@web01:~/tp$ "' > ~/tp/.rc"""

HOOK = hook('Riya’s deploy script prints a timestamped log line in fourteen places, checks “is this a number?” in six places and prints the same red ERROR message in nine. When she wants to change the log format, she has to edit fourteen lines and misses two. <b>Functions</b> fix this: name a block once (<code>log()</code>, <code>die()</code>, <code>is_number()</code>), call it like a command with arguments, return a status, keep its variables <code>local</code>, and share it between scripts with <code>source</code>. Around functions sit the shell’s <b>built-ins</b> (commands inside bash itself, like cd, read, echo, printf, local, return, trap), <b>trap</b> for clean-up when a script ends or is killed, and <b>tput</b> for screen control: clear, cursor position, bold and colours.',
    ['define and call functions with arguments ($1, $#, "$@"), return a status with return, and return data with echo and $( )',
     'keep variables local, understand scope, write recursive functions, and build a small library loaded with source',
     'tell built-ins from external commands (type, enable, help, command, builtin) and know why it matters',
     'clean up with trap on EXIT, ERR, INT and TERM, and control the screen with tput: clear, cup, cols, lines, bold, setaf, sgr0'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the same lines fourteen times'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'Functions and built-ins', 5, 'simple meaning + 4 depths'),
    ('types', 'Function vs alias vs script; return vs echo', 5, 'side by side'),
    ('commands', 'By field', 16, 'real runs and screens'),
    ('animation', 'See it happen', 4, 'a call and its scope'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a helper library'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('A block used in several places', 'name() { …; }', 'function'),
    ('Pass it values', 'name a b   →  $1 $2 inside', 'arguments'),
    ('Report success / failure', 'return 0 / return 1', 'status only (0–255)'),
    ('Give back data (text, numbers)', 'echo result   →  x=$(name)', 'output'),
    ('Variable only inside the function', 'local v=…', 'no side effects'),
    ('Share functions between scripts', 'source lib.sh', 'a library'),
    ('Clean up when the script ends', "trap 'rm -f \"$tmp\"' EXIT", 'always runs'),
    ('Colours, cursor, screen size', 'tput setaf 2 / cup 5 10 / cols', 'screen control'),
])

cmap = concept_map(
    [('12.7', 'Arguments', '$1 "$@" $#'), ('12.8', 'if and case', 'decisions inside'), ('12.9', 'Loops', 'repeat inside')],
    ['name() { …; } and function name', 'arguments, return status, echo for data', 'local and global scope, recursion', 'built-ins vs external commands', 'trap and tput'],
    [('12.11', 'Expansion and eval', 'how calls are read'), ('11.3', 'Signals', 'what trap catches'), ('12.13', 'Arrays', 'passing lists'), ('17.3', 'systemd', 'stop signals')],
    'A function is a named block you call like a command. It gets $1…, returns a status, and prints data. local keeps its variables private.')

sc = (term(20, 14, 316, 156, ['$ cat deploy.sh', ('log()  { echo "[$(date +%T)] $*"; }', 'acc'), ('die()  { echo "ERROR: $*" >&2; exit 1; }', 'acc'), ('log "copying files"', 'out'), ('[ -d /srv/app ] || die "no /srv/app"', 'out'), '$ ./deploy.sh', ('[10:42:07] copying files', 'out'), ('ERROR: no /srv/app', 'err')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=15)
      + t(352, 36, 'Write once, use often:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• log, die, is_number', '• arguments: $1 $@', '• return: status', '• echo: data', '• local: private'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The same lines fourteen times</h2>
  <div class="story">
''' + puzzle('Riya writes <code>total=0; add(){ total=$(( total + $1 )); }</code> and then <code>count(){ i=0; for f in logs/*; do i=$((i+1)); done; echo $i; }</code>. A loop in her main script uses <code>i</code> as well: <code>for i in 1 2 3; do add 10; count &gt;/dev/null; echo "$i"; done</code>. She expects to see 1 2 3, but the output is different. What is printed, why, and which one word fixes it?') + '''
    <p class="narration">Riya replaces fourteen copies of the same lines with three small functions.</p>
''' + scene('A terminal: a deploy script defines log and die functions and uses them; running it prints a timestamped line and an error.', sc,
            'A function is a <tspan font-weight="700" class="s-acc">named block</tspan>, called like a command.') + '''
K> Is a function like a small script?
A> Almost: it is called like a command, takes arguments as <code>$1</code>, <code>$2</code>, <code>"$@"</code>, and ends with a status. But it runs <b>inside</b> the current shell, so it is fast and it can change the shell’s variables, which is exactly the puzzle’s trap.
R> How do I get a value back?
A> <code>return</code> only gives a status (0–255). For data, the function <b>prints</b> it and the caller captures it with <code>$( )</code>. Today: functions, local variables, built-ins, trap for clean-up, and tput for the screen.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A coffee machine: you press a named button (call the function) with options (arguments); it returns a green or red light (status) and pours the coffee (output); its internal water tank is private (local).">'
       + label_box(14, 20, 190, 110, ['call = press a button', 'make_coffee large', '$1 = large', '(arguments)'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['inside: local tank', 'local water=200', 'not visible outside', '(local variables)'], 'amber', 8.6)
       + label_box(434, 20, 192, 110, ['results', 'light: return 0/1', 'cup: echo → $( )', '(status vs data)'], 'green', 8.6)
       + t(320, 160, 'Define once with name() { … }, press the button anywhere.', 9.6, 'ink2')
       + t(320, 182, 'return = light, echo = coffee.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Functions at four depths', [
    ('v', 'No jargon: a coffee machine', '      <p>A button with options, a light and a cup.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>greet() { echo "Hello, $1!"; }</code> then <code>greet Riya</code>.</li>
        <li><code>square() { echo $(( $1 * $1 )); }</code> then <code>x=$(square 7)</code>.</li>
        <li><code>is_even() { (( $1 % 2 == 0 )); }</code> then <code>if is_even 4; then …</code>.</li>
        <li>Define before you call: bash reads the script top to bottom.</li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li>Two forms: <code>name() { …; }</code> (POSIX) and <code>function name { …; }</code> (bash). Inside braces, the last command needs <code>;</code> or a newline before <code>}</code>.</li>
        <li>Inside: <code>$1…</code>, <code>$#</code>, <code>"$@"</code> are the <b>function’s</b> arguments; <code>$0</code> stays the script name; <code>FUNCNAME</code> is the function’s name.</li>
        <li><code>return N</code> sets the status (0–255, wraps like exit); without it, the status of the last command. <code>exit</code> inside a function ends the whole script.</li>
        <li>Variables are global unless declared <code>local</code> (bash) inside the function.</li>
        <li><code>$(func)</code> runs the function in a subshell: it cannot change the caller’s variables from there.</li>
      </ul>'''),
    ('a', 'Behind the screen: built-ins, scope and signals', '''      <ul>
        <li>Lookup order: alias → keyword → <b>function</b> → <b>builtin</b> → PATH (Lesson 12.1). A function can override a command; <code>command ls</code> or <code>builtin cd</code> reach the original.</li>
        <li>Built-ins run inside bash (no fork, no exec): cd, read, export, local, trap must be built-ins because they change the shell itself. <code>enable</code> lists them, <code>help NAME</code> documents them.</li>
        <li>bash uses dynamic scope: a <code>local</code> variable is visible to functions called from that function.</li>
        <li><code>trap CMD SIGNAL</code> runs CMD when the shell receives SIGNAL (INT = Ctrl+C, TERM = kill, HUP); the pseudo-signals EXIT, ERR, DEBUG and RETURN are bash extras. SIGKILL cannot be trapped (Lesson 11.3).</li>
        <li><code>tput</code> looks up the terminal’s capabilities in the terminfo database for <code>$TERM</code> and prints the matching escape sequence; it works on any terminal type, unlike hard-coded <code>\\e[32m</code>.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Functions, built-ins, trap and tput</h2>
''' + def_block(
    'A <b>shell function</b> is a named compound command, defined with <code>name() { commands; }</code>, that is executed in the current shell when its name is used as a command; it receives arguments as positional parameters and returns an exit status with <code>return</code>. A <b>built-in</b> is a command implemented inside the shell itself. <code>trap</code> sets commands to run when the shell receives a signal or exits, and <code>tput</code> sends terminal control sequences (cursor, colours, clear) for the current terminal type.',
    'Function = your own command inside the script. Built-in = a command inside bash. trap = “when this happens, run that”. tput = control the screen.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Function', 'A named block called like a command.'),
    ('Call', 'Running it: name arg1 arg2.'),
    ('return', 'End the function with a status.'),
    ('local', 'Variable only inside the function.'),
    ('Recursion', 'A function calling itself.'),
    ('Library', 'A file of functions you source.'),
    ('trap', 'Run code on a signal or exit.'),
    ('tput', 'Terminal control by capability name.'),
]) + '\n' + names('Where the names come from.', [
    ('function', 'a named routine', 'ksh keyword, bash too.'),
    ('return', 'return from routine', 'Status only.'),
    ('local', 'local scope', 'bash, not POSIX.'),
    ('trap', 'catch a signal', 'Bourne shell.'),
    ('tput', 'terminal put', 'Uses terminfo.'),
    ('cup', 'cursor position', 'row, column.'),
    ('setaf', 'set ANSI foreground', 'Colour 0–7.'),
    ('sgr0', 'select graphic rendition 0', 'Reset styles.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Define', '<code>f() { …; }</code>'),
    ('Arguments', '<code>$1 $# "$@"</code>'),
    ('Data back', '<code>x=$(f)</code>'),
    ('Status back', '<code>return 1</code>'),
    ('Private', '<code>local v</code>'),
    ('Clean-up', "<code>trap '…' EXIT</code>"),
]) + '\n' + lv + didyou('You use functions every day without knowing it: on Ubuntu, Tab completion for git, apt and systemctl is implemented by hundreds of bash functions. Run <code>declare -F | wc -l</code> in a terminal to count them.') + '''
EXAM> “What is the difference between return and exit in a shell function?” → return ends only the function and sets its status; exit ends the whole script (or shell).
''' + qc('A function <code>f() { echo hi }</code> is all on one line. Why does bash complain?', 'The } is read as part of the echo arguments; it needs a ; (or newline) before it: f() { echo hi; }.') + mistake('result=square 4   ·   return "$total"   (to give back a big number)',
    'result=$(square 4)   ·   echo "$total"   (and capture with $( ))',
    'A function’s output is text; capture it with $( ). return only carries a status 0–255: return 300 gives 44 (checked).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Function vs alias vs script, and return vs echo</h2>
''' + table(['', 'Function', 'Alias (12.3)', 'Script (12.5)'], [
    ['Arguments', '$1, $@ anywhere', 'only appended', '$1, $@ anywhere'],
    ['Logic (if, loops)', 'yes', 'no', 'yes'],
    ['Runs in', 'current shell', 'current shell', 'new process'],
    ['Can change your variables / cd', 'yes', 'yes', 'no (unless sourced)'],
    ['Works in scripts', 'yes', 'no (default)', 'yes'],
    ['Speed', 'fast (no fork)', 'fast', 'slower (fork + exec)'],
], minw=560) + table(['', 'return N', 'echo …; x=$(f)', 'global variable'], [
    ['Carries', 'a status 0–255', 'any text or number', 'any value'],
    ['Used with', 'if f; then  ·  $?', 'x=$(f)', 'f; echo "$result"'],
    ['Side effects', 'none', 'runs in a subshell', 'changes shared state'],
    ['Best for', 'yes/no answers', 'computed values', 'large results (careful)'],
], minw=520) + table(['Kind of command', 'Example', 'Check with'], [
    ['keyword', 'if, for, [[, function', '<code>type -t</code> → keyword'],
    ['builtin', 'cd, echo, read, printf, local, trap', '<code>type -t</code> → builtin'],
    ['function', 'your log(), die()', '<code>type -t</code> → function; <code>declare -f</code>'],
    ['alias', 'll', '<code>type -t</code> → alias'],
    ['file', '/usr/bin/ls, tput', '<code>type -t</code> → file; <code>type -P</code>'],
], minw=440) + qc('Why must cd be a built-in, while ls can be a program?', 'cd changes the shell’s own current folder; a separate program would only change its own folder and then exit.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Functions, built-ins, trap and tput, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/fn</code> with <code>logs/app.log</code> and a small library <code>lib.sh</code> (log, die, is_number). tput needs a terminal type, so its examples set <code>TERM=xterm-256color</code> and show the escape codes with <code>cat -v</code>; the screen example is a real recorded terminal.</p>
''' + cmdcard_u(['any block used more than once', 'giving a name to a step (readability)', 'checks used in if'],
               ['one-line shortcuts with no logic (an alias is enough)'])(
    'func', 'name() { … } · arguments · calling', 'define and call',
    'Define with <code>name() { commands; }</code> (or <code>function name { …; }</code>), then call it like a command: <code>name arg1 arg2</code>. Inside, <code>$1</code>…, <code>$#</code> and <code>"$@"</code> are the call’s arguments. Define before use.',
    'name() { …; }   ·   name ARGS   ·   declare -f name   ·   unset -f name', 'safe',
    [('f() { …; }', 'define (POSIX)', 'always works'),
     ('function f { …; }', 'define (bash)', 'readable'),
     ('f a b', 'call with arguments', '$1=a $2=b'),
     ('"$@" inside', 'all arguments', 'pass on'),
     ('$FUNCNAME', 'own name', 'messages'),
     ('declare -f f', 'show the code', 'debug'),
     ('declare -F', 'list function names', 'inventory'),
     ('unset -f f', 'remove', 'clean up')],
    dict(cmd="greet() {\n  echo \"Hello, $1! You gave $# argument(s).\"\n}\ngreet Riya\ngreet 'Aman Kumar' extra\ndeclare -F | grep greet", note='Quoted “Aman Kumar” arrives as one argument.'),
    [('dev', [
        dict(situation='The class-notes examples, run for real.', cmd="add_numbers() { result=$(( $1 + $2 )); echo \"The sum of $1 and $2 is: $result\"; }\nsquare() { echo $(( $1 * $1 )); }\ncheck_number() { if [ \"$1\" -gt 0 ]; then echo \"$1 is positive.\"; elif [ \"$1\" -lt 0 ]; then echo \"$1 is negative.\"; else echo \"$1 is zero.\"; fi; }\nadd_numbers 5 10; echo \"square of 4: $(square 4)\"; check_number -5; echo \"result leaked out: $result\"", why='They all work; note the last line: result was not local, so it is still set outside.')]),
     ('sys', [
        dict(situation='Functions as the steps of a script.', setup=FN, cmd="cd ~/fn\ncheck_logs() { [ -s logs/app.log ]; }\ncount_errors() { grep -c ' 500$' logs/app.log; }\nreport() { echo \"$(date +%F): $1 server errors\"; }\nif check_logs; then report \"$(count_errors)\"; fi | sed 's/^[0-9-]*/DATE/'", why='Each step has a name; the main part reads like a sentence.')]),
     ('qa', [
        dict(situation='Define before use.', cmd="bash -c 'hello; hello(){ echo hi; }; hello'", expect='any', why='The first call happens before the definition is read: command not found. Put functions at the top.')]),
    ],
    anat=anatomy([('greet', 'cmd', 'name'), ('()', 'opt', 'function'), ('{', 'opt', 'body start'), ('echo "Hello, $1"', 'arg', 'commands'), ('; }', 'opt', 'end')], 'Spaces after { and ; before } are required.')
) + cmdcard_u(['yes/no checks (is_number, file_ok)', 'computed values (sizes, names, totals)'],
               ['return for data larger than 255', 'echo debug text inside a function you capture with $( )'])(
    'ret', 'return · echo + $( ) · $?', 'give results back',
    '<code>return N</code> ends the function with status N, perfect for <code>if f; then</code>. To return data, the function prints it (echo/printf) and the caller captures it: <code>x=$(f args)</code>. Messages for humans should go to stderr (<code>&gt;&amp;2</code>) so they are not captured.',
    'f(){ …; return 1; }   ·   x=$(f)   ·   if f; then …', 'safe',
    [('return 0 / 1', 'success / failure', 'checks'),
     ('return', 'status of last command', 'default'),
     ('echo VALUE', 'output = data', 'results'),
     ('x=$(f)', 'capture data', 'caller'),
     ('>&2', 'message, not data', 'logs'),
     ('return 300', 'wraps to 44', 'avoid')],
    dict(setup=FN, cmd="cd ~/fn; source lib.sh\nfor v in 42 4x2; do if is_number \"$v\"; then echo \"$v: number\"; else echo \"$v: not a number\"; fi; done\nsize_kb() { du -k \"$1\" | cut -f1; }\necho \"logs use $(size_kb logs) KB\"", note='is_number returns a status (used by if); size_kb prints data (captured with $( )).'),
    [('dev', [
        dict(situation='Status and data together.', cmd="half() { (( $1 % 2 == 0 )) || { echo \"$1 is odd\" >&2; return 1; }; echo $(( $1 / 2 )); }\nx=$(half 10) && echo \"half: $x\"\nx=$(half 7) || echo \"failed with status $?\"", why='The error message went to stderr (shown on screen, not captured); the status says it failed.')]),
     ('qa', [
        dict(situation='return only carries 0–255.', cmd="big() { return 300; }; big; echo \"status: $?\"\nbig2() { echo 300; }; echo \"output: $(big2)\"", why='Use output for numbers; keep return for success/failure.')]),
    ]
) + cmdcard_u(['every variable used only inside a function', 'recursive functions'],
               ['values that really must be shared (name them clearly)'])(
    'local', 'local · scope · recursion', 'private variables',
    'Without <code>local</code>, a variable set in a function changes (or creates) the global one. <code>local v</code> or <code>local v=value</code> makes it private to that call (and functions it calls). Recursive functions need local variables for each level.',
    'local VAR[=value]   ·   local -a arr   ·   local -i n', 'safe',
    [('local v=1', 'private copy', 'always'),
     ('local -i n', 'integer local', 'counters'),
     ('local -a a', 'local array', 'lists'),
     ('declare v', 'same as local inside f', 'alternative'),
     ('global (no local)', 'shared', 'rare, on purpose')],
    dict(cmd="name=global\nwith_local() { local name=inside; echo \"in with_local: $name\"; }\nwithout_local() { name=changed; }\nwith_local; echo \"after with_local: $name\"\nwithout_local; echo \"after without_local: $name\"", note='Only the function without local changed the global variable.'),
    [('dev', [
        dict(situation='The puzzle: a shared loop variable.', setup=FN, cmd="cd ~/fn\ncount(){ i=0; for f in logs/*; do i=$((i+1)); done; echo $i; }\nfor i in 1 2 3; do count > /dev/null; echo \"loop i=$i\"; done\ncount2(){ local i=0 f; for f in logs/*; do i=$((i+1)); done; echo $i; }\nfor i in 1 2 3; do count2 > /dev/null; echo \"loop i=$i\"; done", why='count overwrote the caller’s i with 1 (one file), so the loop printed 1 1 1. local i fixes it.')]),
     ('data', [
        dict(situation='Recursion: factorial.', cmd="fact() { local n=$1; if (( n <= 1 )); then echo 1; else echo $(( n * $(fact $((n - 1))) )); fi; }\nfor n in 1 5 10; do echo \"$n! = $(fact $n)\"; done", why='Each call has its own local n; each $( ) is a new subshell.')]),
    ]
) + mistake('Defining every helper without local', 'local for every variable that is not meant to be shared',
            'Global by default is the most common source of “impossible” bugs in long scripts, exactly as in the puzzle.') + cmdcard_u(['sharing helpers across many scripts', 'consistent logging and error handling'],
               ['libraries that print or run things when sourced'])(
    'lib', 'source lib.sh · built-ins · type · help', 'libraries and built-ins',
    'Put functions in a file and load them with <code>source lib.sh</code> (or <code>. lib.sh</code>). Built-ins are commands inside bash: <code>type NAME</code> tells you what a name is, <code>help NAME</code> shows a built-in’s help, <code>enable</code> lists built-ins, <code>command NAME</code> skips functions/aliases, <code>builtin NAME</code> forces the built-in.',
    'source lib.sh   ·   type -a NAME   ·   help NAME   ·   command NAME   ·   builtin NAME', 'safe',
    [('source lib.sh', 'load functions', 'libraries'),
     ('type -t NAME', 'keyword/builtin/function/file', 'what is it'),
     ('type -a NAME', 'all definitions', 'shadowing'),
     ('help read', 'built-in help', 'no man page'),
     ('enable', 'list built-ins', 'curious'),
     ('command ls', 'skip function/alias', 'wrappers'),
     ('builtin cd', 'force the built-in', 'overrides')],
    dict(setup=FN, cmd="cd ~/fn; source lib.sh\nlog 'backup started' | sed 's/^\\[[0-9:]*\\]/[HH:MM:SS]/'\ntype -t log cd if ls\nis_number 2026 && echo '2026 is a number'", note='Three functions from the library, and type showing four kinds of names.'),
    [('sys', [
        dict(situation='A function that wraps a command, then calls the real one.', cmd="cd() { builtin cd \"$@\" && echo \"now in $PWD\"; }\ncd /tmp; cd /etc\nls() { command ls -1 \"$@\" | head -2; }\nls /\nunset -f cd ls", why='builtin and command prevent the wrapper from calling itself forever.')]),
     ('dev', [
        dict(situation='How many built-ins, and a few of them.', cmd="enable | wc -l\nhelp -d read printf local trap | sed 's/ - /: /'", why='help -d gives one-line descriptions of built-ins.')]),
    ]
) + cmdcard_u(['removing temporary files whatever happens', 'stopping cleanly on Ctrl+C or kill', 'reporting the failing line'],
               ['trying to trap SIGKILL (impossible)'])(
    'trap', "trap 'CMD' EXIT INT TERM ERR", 'clean-up and signals',
    "<code>trap 'commands' SIGNALS</code> runs the commands when the shell gets a signal (INT = Ctrl+C, TERM = kill, HUP = terminal closed) or on the pseudo-signals EXIT (script ends, any way), ERR (a command fails) and RETURN. <code>trap - SIGNAL</code> removes it; <code>trap -p</code> lists.",
    "trap 'rm -f \"$tmp\"' EXIT   ·   trap 'echo stopped; exit 130' INT", 'safe',
    [('EXIT', 'script ends (any way)', 'clean-up'),
     ('INT', 'Ctrl+C', 'polite stop'),
     ('TERM', 'kill PID', 'services'),
     ('ERR', 'a command failed', 'error report'),
     ("trap '' INT", 'ignore Ctrl+C', 'critical section'),
     ('trap - INT', 'back to default', 'after'),
     ('trap -p', 'list traps', 'debug')],
    dict(cmd="bash -c 'tmp=$(mktemp); trap \"rm -f \\\"\\$tmp\\\"; echo cleaned up \\$tmp\" EXIT; echo working with \"$tmp\"; exit 3' | sed 's|/tmp/tmp\\.[A-Za-z0-9]*|/tmp/tmp.XXXX|'\necho \"script status: ${PIPESTATUS[0]}\"", note='The EXIT trap ran even though the script ended with exit 3.'),
    [('devops', [
        dict(situation='Catch kill (TERM) and finish politely.', cmd="bash -c 'trap \"echo caught TERM, saving state; exit 1\" TERM; echo \"running as $$\" | sed s/[0-9]*$/PID/; kill -TERM $$; sleep 5; echo never'\necho \"status $?\"", why='docker stop and systemctl stop send TERM first: a trap lets the script save its work (Lesson 11.3).')]),
     ('qa', [
        dict(situation='Report the line that failed.', cmd="bash -c 'set -e; trap \"echo FAILED at line \\$LINENO: \\$BASH_COMMAND\" ERR\necho step 1\nls /no/such/dir 2>/dev/null\necho step 3'", expect='any', why='ERR plus $LINENO and $BASH_COMMAND gives a useful message before set -e stops the script.')]),
    ]
) + cmdcard_u(['menus, dashboards, progress screens', 'bold or coloured status words'],
               ['output that goes to files or pipes (no terminal: skip colours)'])(
    'tput', 'tput clear · cup · cols · lines · bold · setaf · sgr0', 'screen control',
    '<code>tput</code> prints the control sequence for a named capability: <code>clear</code>, <code>cup ROW COL</code> (move the cursor, from 0), <code>cols</code> / <code>lines</code> (screen size), <code>bold</code>, <code>smul</code> (underline), <code>rev</code>, <code>setaf N</code> / <code>setab N</code> (colour 0–7), <code>sgr0</code> (reset), <code>civis</code>/<code>cnorm</code> (hide/show cursor).',
    'tput clear   ·   tput cup 5 10   ·   tput setaf 2; echo OK; tput sgr0', 'safe',
    [('clear', 'clear screen', 'menus'),
     ('cup R C', 'cursor to row, column', 'layouts'),
     ('cols / lines', 'screen size', 'centring'),
     ('bold / smul / rev', 'bold, underline, reverse', 'emphasis'),
     ('setaf 1 / 2 / 3', 'red / green / yellow text', 'status'),
     ('sgr0', 'reset everything', 'always after'),
     ('civis / cnorm', 'hide / show cursor', 'progress bars'),
     ('colors', 'how many colours', 'checks')],
    dict(cmd=T + "tput cols; " + T + "tput lines; " + T + "tput colors\nfor cap in bold 'setaf 2' sgr0 'cup 5 10' clear; do printf '%-9s -> ' \"$cap\"; " + T + "tput $cap | cat -v; echo; done", note='Each capability is just a short escape sequence; cat -v makes it visible (^[ is the ESC character).'),
    [('sys', [
        dict(situation='Coloured OK / FAIL only when writing to a terminal.', cmd="status() { if [ -t 1 ]; then g=$(" + T + "tput setaf 2) r=$(" + T + "tput setaf 1) n=$(" + T + "tput sgr0); fi; [ \"$1\" = ok ] && echo \"${g:-}OK${n:-}\" || echo \"${r:-}FAIL${n:-}\"; }\nstatus ok; status bad\nstatus ok | cat -v", why='[ -t 1 ] is false here (the output is recorded, not a terminal), so no escape codes end up in logs.')]),
     ('dev', [
        dict(situation='Centre a title using tput cols.', cmd="title='MyPhatshala Report'; w=$(" + T + "tput cols)\nprintf '%*s\\n' $(( (w + ${#title}) / 2 )) \"$title\" | cat -A | sed 's/ /./g' | cut -c1-60", why='printf %*s pads to a width computed from the screen size (dots show the padding).')]),
    ]
) + undo('Functions live in the shell; mistakes are easy to undo.', [
    ('A function shadows a real command:', '<code>unset -f NAME</code>; inside wrappers use <code>command</code> / <code>builtin</code>.'),
    ('Screen messed up after colours or cursor moves:', '<code>tput sgr0</code>, <code>tput cnorm</code>, or <code>reset</code>.'),
    ('trap left in place:', '<code>trap - EXIT INT TERM</code>.'),
    ('Function changed a global by accident:', 'add <code>local</code>; check with <code>declare -p NAME</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="bash -c 'f() { echo hi }'", meaning='Missing ; before } (the } is read as an argument and the function never ends).', fix='<code>f() { echo hi; }</code>.'),
    dict(cmd="bash -c 'myfunc'", meaning='Called before (or without) being defined.', fix='Define functions at the top; source the library first.'),
    dict(cmd='local x=1', meaning='local works only inside a function.', fix='Use it inside f() { … }.'),
    dict(cmd='return 1', meaning='return outside a function (or sourced file).', fix='Use exit in the main script.'),
]) + qc('Inside a function, what are $0 and $1?', '$0 is still the script (or shell) name; $1 is the function’s first argument.') + '''
'''

SCREENS = screens_block('Real terminal screen: a tput layout', 'A small script that clears the screen, places text with <code>tput cup</code> and prints a bold OK, run in a 60×10 terminal.',
    BOX, 'bash --rcfile ~/tp/.rc', [
    ('bash box.sh  Enter', "'bash box.sh' Enter", ' the screen is cleared and every line is placed at row/column positions.'),
], 60, 10, what='bash')
cards = cards + SCREENS + '</section>\n'

def call(k):
    o = label_box(14, 16, 160, 40, ['main script', 'i = 2'], 'blue', 8)
    if k >= 1:
        o += arrow(174, 36, 196, 36) + label_box(196, 16, 150, 40, ['count()', 'i=0 … i=1'], 'amber', 8)
    if k == 2:
        o = label_box(14, 16, 160, 40, ['main script', 'i = 1  (changed!)'], 'red', 8) + label_box(196, 16, 150, 40, ['count() returned', 'no local'], 'card', 8)
    if k == 3:
        o = label_box(14, 16, 160, 40, ['main script', 'i = 2  (safe)'], 'green', 8) + label_box(196, 16, 150, 40, ['count2()', 'local i: own copy'], 'green', 8)
    return o
see_cmds = [['$ for i in 1 2 3; do count; echo $i; done'], ['$ for i in 1 2 3; do count; echo $i; done'], ['$ for i in 1 2 3; do count; echo $i; done', ('1', 'err'), ('1', 'err'), ('1', 'err')], ['$ for i in 1 2 3; do count2; echo $i; done', ('1', 'out'), ('2', 'out'), ('3', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/fn', prompt='riya@web01:~/fn$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['The loop sets i.', 'It calls count…', '…which overwrote i.', 'With local: 1 2 3.'])]
behind = [call(k) + t(180, 96, n, 8.4, 'violet', bold=True) for k, n in enumerate(['i belongs to the main script.', 'count runs in the SAME shell.', 'Its i=… changed the global i.', 'local i gives count2 its own copy.'])]
two = anim_two('A call and its scope', 'Behind the screen: one shell, shared variables',
               'A terminal: a loop printing i calls a function; without local it prints 1 1 1, with local 1 2 3.',
               'The main script and the function share variables unless the function declares local.', see, behind,
               ['Loop.', 'Call.', 'Overwritten.', 'local.'],
               ['global i', 'same shell', 'i changed', 'own copy'])

def tr(k):
    o = label_box(14, 16, 332, 30, ["trap 'rm -f $tmp; echo cleaned' EXIT INT TERM"], 'blue', 7.6)
    rows = [('normal end', 'green'), ('exit 3 / error', 'amber'), ('Ctrl+C (INT)', 'violet'), ('kill -9 (KILL)', 'red')]
    for i, (n, tn) in enumerate(rows[:k + 1]):
        res = 'trap runs: cleaned' if i < 3 else 'cannot be trapped!'
        o += label_box(14, 56 + i * 32, 150, 26, [n], tn, 8) + label_box(176, 56 + i * 32, 170, 26, [res], 'card', 7.6)
    return o
frames = [tr(0) + t(180, 205, 'The script finishes: EXIT runs.', 8.6, 'green', bold=True),
          tr(1) + t(180, 205, 'exit 3 or set -e: EXIT still runs.', 8.6, 'amber', bold=True),
          tr(2) + t(180, 205, 'Ctrl+C: INT runs (then EXIT).', 8.6, 'violet', bold=True),
          tr(3) + t(180, 205, 'SIGKILL ends it at once: no trap.', 8.6, 'red', bold=True)]
s1 = anim_one('Animated example', 'When does a trap run?',
              'Four ways a script can end.',
              'trap', 'A trap on EXIT INT TERM runs for a normal end, an exit with an error and Ctrl+C, but not for kill -9.', frames,
              ['Normal.', 'Error.', 'Ctrl+C.', 'kill -9.'], hid='scenario-trap')

dx = dissect('Layer by layer: what happens when you type a name',
    'Each layer has a real command and output from our build machine.', [
    dict(key='kw', name='Keyword', sub='if for [[', why='Grammar.', how='Parsed first.', impl='bash parser.', used='Every script.',
         cmd="type -t if for '[['"),
    dict(key='fn', name='Function', sub='yours', why='Your commands.', how='Before built-ins.', impl='declare -f.', used='Libraries.',
         cmd="echo(){ builtin echo \"[fn] $*\"; }; echo hi; unset -f echo; echo hi"),
    dict(key='bi', name='Built-in', sub='inside bash', why='No new process.', how='enable.', impl='C code in bash.', used='cd read trap.',
         cmd="type -t cd read trap printf; enable -a | grep -c enable"),
    dict(key='file', name='External', sub='PATH', why='Everything else.', how='fork + exec.', impl='/usr/bin.', used='ls tput.',
         cmd="type -P ls tput; type -a printf"),
], hint='From keywords down to programs on disk. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A call and its scope, and when a trap runs</h2>
''' + two + s1 + dx + qc('Why does the EXIT trap also run when set -e stops a script?', 'Because EXIT fires whenever the shell exits, for any reason except SIGKILL.') + '''
</section>
'''

VAR = variations('Eighteen more functions, each a variation of the examples above. All were really run on our build machine.', [
    ('Small useful functions', [
        dict(title='max of any number of values', cmd="max() { local m=$1 v; shift; for v; do (( v > m )) && m=$v; done; echo $m; }\nmax 12 45 7 30", why='shift takes the first value, for v loops over the rest.'),
        dict(title='sum of arguments', cmd="sum() { local t=0 n; for n in \"$@\"; do t=$((t + n)); done; echo $t; }\nsum 10 20 30 40", why='"$@" with an accumulator.'),
        dict(title='is_even as a test', cmd="is_even() { (( $1 % 2 == 0 )); }\nfor n in 4 7; do is_even $n && echo \"$n even\" || echo \"$n odd\"; done", why='The last command’s status is the function’s status: no return needed.'),
        dict(title='to_upper with a default', cmd="to_upper() { local s=${1:-nothing}; echo \"${s^^}\"; }\nto_upper cdac; to_upper", why='${s^^} uppercases (Lesson 12.14); ${1:-} gives a default.'),
        dict(title='file_info', setup=FN, cmd="cd ~/fn\nfile_info() { [ -e \"$1\" ] || { echo \"$1: missing\"; return 1; }; echo \"$1: $(wc -l < \"$1\") lines, $(stat -c %s \"$1\") bytes\"; }\nfile_info logs/app.log; file_info nope.txt", expect='any', why='A guard, then data; status 1 for the missing file.'),
        dict(title='Confirm before acting', cmd="confirm() { local a; read -r -p \"$1 [y/N] \" a; [[ $a == [yY]* ]]; }\nconfirm 'Delete temp files?' <<< y && echo deleting\nconfirm 'Restart server?' <<< n || echo 'skipped'", why='A yes/no question as a reusable test.'),
    ]),
    ('Scope, recursion and libraries', [
        dict(title='Local vs global (notes example)', cmd="global_var='I am global'\ndemo_local() { local local_var='I am local'; local global_var='local override'; echo \"inside: $local_var / $global_var\"; }\ndemo_local; echo \"outside: ${local_var:-<unset>} / $global_var\"", why='local hides the global inside the function only.'),
        dict(title='Dynamic scope', cmd="outer() { local who=outer; inner; }\ninner() { echo \"inner sees who=$who\"; }\nwho=global; outer; inner", why='bash locals are visible to functions called from that function.'),
        dict(title='Fibonacci, recursive', cmd="fib() { local n=$1; (( n < 2 )) && { echo $n; return; }; echo $(( $(fib $((n-1))) + $(fib $((n-2))) )); }\nfor i in {0..9}; do printf '%s ' \"$(fib $i)\"; done; echo", why='Elegant but slow (many subshells); a loop is faster.'),
        dict(title='Count calls with a global on purpose', cmd="calls=0\nping_db() { calls=$((calls + 1)); }\nfor i in 1 2 3; do ping_db; done; echo \"called $calls times\"", why='Sometimes sharing is intended: name such variables clearly.'),
        dict(title='A library with a guard', cmd="printf 'echo loading lib\\n[ -n \"${LIB_LOADED:-}\" ] && return; LIB_LOADED=1\\nhi(){ echo hi from lib; }\\n' > mylib.sh\nsource mylib.sh; source mylib.sh; hi", why='return at top level of a sourced file stops it: the library loads once.'),
    ]),
    ('trap and tput variations', [
        dict(title='Temporary folder that always disappears', cmd="work() { local d; d=$(mktemp -d); saved=$d; trap 'rm -rf \"$d\"' RETURN; touch \"$d/x\"; echo \"working in a temp folder with $(ls \"$d\" | wc -l) file\"; }\nwork; [ -e \"$saved\" ] && echo 'temp folder still there' || echo 'temp folder removed when work returned'", why='RETURN runs when the function returns (bash extension).'),
        dict(title='Ignore Ctrl+C during a critical step', cmd="bash -c 'trap \"\" INT; echo \"critical step (Ctrl+C ignored)\"; trap - INT; trap -p INT | wc -l'", why="trap '' INT ignores; trap - INT restores the default."),
        dict(title='List active traps', cmd="trap 'echo bye' EXIT; trap 'echo int' INT; trap -p | cut -c1-40; trap - EXIT INT", why='trap -p prints the current traps in a form you can reuse.'),
        dict(title='A coloured log function', cmd="clog() { local c; case $1 in INFO) c=2;; WARN) c=3;; ERROR) c=1;; esac; shift; echo \"$(" + T + "tput setaf $c)$*$(" + T + "tput sgr0)\"; }\nclog INFO started | cat -v; clog ERROR 'disk full' | cat -v", why='Green, yellow, red by level; cat -v shows the codes (in a terminal you see colours).'),
        dict(title='Progress bar with \\r', cmd="bar() { local i; for i in 20 40 60 80 100; do printf '\\r[%-10s] %3d%%' \"$(printf '#%.0s' $(seq 1 $((i / 10))))\" $i; done; echo; }\nbar | tr '\\r' '\\n' | tail -2", why='\\r returns to the line start so the bar redraws in place (tr shows the last frames).'),
        dict(title='Screen size in a function', cmd="screen() { echo \"$(" + T + "tput cols) columns x $(" + T + "tput lines) lines\"; }\nscreen", why='In a real terminal this follows the window size; here the default 80×24.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Functions, trap and tput at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['lib.sh', 'log die'], 'blue', 8.6), '1. Team script libraries',
              'Teams keep a common.sh with log, die, retry and require_root, sourced by every script.', ['Write once', '*source', 'reuse']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['trap EXIT', 'clean-up'], 'green', 8.6), '2. Safe temporary files',
    'Scripts create files with mktemp and remove them in an EXIT trap, even when they fail.', ['mktemp', '*trap', 'clean']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['trap TERM', 'containers'], 'amber', 8.6), '3. Graceful shutdown',
    'Container entrypoints trap TERM to finish the current job before docker stop or Kubernetes kills them.', ['TERM', '*trap', 'exit 0']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['tput', 'menus'], 'violet', 8.6), '4. Operator menus',
    'Admin menus and installers use tput to clear the screen, highlight choices and colour statuses.', ['Draw', '*tput', 'choose']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['retry()', 'CI'], 'red', 8.6), '5. CI helpers',
    'A retry function wraps flaky network steps: retry 5 curl -f URL.', ['Flaky', '*retry', 'stable']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='One-line function', scenario='Quick helper.', cmd="hello() { echo \"Namaste, ${1:-friend}!\"; }; hello; hello Riya", explain='Define and call.'),
    dict(level='b', title='What is it?', scenario='Function, built-in or file?', cmd="f(){ :; }; type -t f cd ls if", explain='type -t.'),
    dict(level='i', title='retry helper', scenario='Flaky commands.', cmd="retry() { local n=$1 i; shift; for ((i=1;i<=n;i++)); do \"$@\" && return 0; echo \"try $i failed\"; done; return 1; }\nretry 3 false || echo 'all tries failed'", explain='"$@" runs the given command.'),
    dict(level='i', title='Show a function’s code', scenario='Debug.', cmd="square() { echo $(( $1 * $1 )); }; declare -f square", explain='declare -f.'),
    dict(level='a', title='Timer with trap RETURN', scenario='How long did it take?', cmd="timed() { local s=$SECONDS; trap 'echo \"took $((SECONDS - s)) s\"; trap - RETURN' RETURN; sleep 1; }; timed", explain='SECONDS counts seconds since the shell started.'),
], extra=build_up('a helper library', 'Riya builds lib.sh step by step and uses it from a script.', FN + "\nrm -f ~/fn/lib.sh", [
    ("cd ~/fn; printf 'log() { echo \"[log] $*\"; }\\n' > lib.sh; source lib.sh; log 'first helper'", '1. A log function.'),
    ("cd ~/fn; printf 'die() { echo \"ERROR: $*\" >&2; exit 1; }\\n' >> lib.sh; bash -c 'source lib.sh; die \"no config\"; echo never'; echo \"status $?\"", '2. die: message and exit.'),
    ("cd ~/fn; printf 'is_number() { [[ $1 =~ ^[0-9]+$ ]]; }\\n' >> lib.sh; source lib.sh; is_number 42 && log '42 ok'", '3. A test function.'),
    ("cd ~/fn; printf 'source ./lib.sh\\nlog start\\nis_number \"$1\" || die \"not a number: $1\"\\nlog \"got $1\"\\n' > use.sh; bash use.sh 7; bash use.sh x; echo \"status $?\"", '4. A script using the library.'),
], cumulative=True, expect='any')) + VAR + which('Choosing the right tool.', [
    ('Reuse a block', 'function', 'One place to change.', 'Copy-paste.'),
    ('Yes/no answer', 'return status', 'Works with if.', 'echo yes/no and compare text.'),
    ('Give back a value', 'echo + $( )', 'Any size.', 'return 300.'),
    ('Private variable', 'local', 'No side effects.', 'Globals everywhere.'),
    ('Clean up', "trap '…' EXIT", 'Always runs.', 'rm at the end only.'),
    ('Colour / cursor', 'tput', 'Any terminal.', 'Hard-coded \\e[ codes.'),
]) + keys('Handy forms.', [
    ('f() { …; }', 'define', 'POSIX'),
    ('local v=…', 'private', 'always'),
    ('x=$(f a b)', 'capture', 'data'),
    ('declare -F', 'list functions', 'inventory'),
    ("trap 'rm -f \"$t\"' EXIT", 'clean-up', 'temp files'),
    ('tput setaf 2; …; tput sgr0', 'green text', 'status'),
]) + scriptit('menu.sh', 'A small menu built from functions, case, a loop, trap and tput: the same pattern as the class notes’ menu-driven program, organised into functions.',
'''bold=$(TERM=xterm-256color tput bold) reset=$(TERM=xterm-256color tput sgr0)
trap 'echo "bye (cleaned up)"' EXIT
show_menu() { echo "${bold}1${reset} date  ${bold}2${reset} user  ${bold}3${reset} files  ${bold}4${reset} exit"; }
do_date()  { date +%F; }
do_user()  { echo "user: $USER"; }
do_files() { ls | head -3; }
while show_menu; read -r -p 'choice: ' c; do
  case $c in 1) do_date;; 2) do_user;; 3) do_files;; 4) break;; *) echo "invalid: $c";; esac
done <<< $'2\\n9\\n4' | cat -v''',
'<p>Answers 2, 9 and 4 are given through a here-string; cat -v shows the bold codes.</p>', expect='any') + puzzle_answer('count() sets <code>i=0</code> and counts files with <code>i</code> <b>without local</b>, so it changes the main script’s loop variable: after each call i is 1 (one file in logs/), and the loop prints 1, 1, 1 (and keeps running because for takes the next item from its own list). The one-word fix: <code>local</code> (<code>local i=0 f</code>) inside count. The same applies to <code>total</code> in add, which is meant to be global, so leave that one.') + qc('Which signal can a trap never catch?', 'SIGKILL (kill -9), and SIGSTOP.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/fn ~/tp ~/mylib.sh', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../09-loops-for-while-until-break-continue/">Lesson 12.9</a> (loops) and <a href="../08-decisions-if-test-and-case/">12.8</a> (if and case).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
