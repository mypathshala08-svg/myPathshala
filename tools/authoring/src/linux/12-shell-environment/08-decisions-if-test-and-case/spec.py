import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='08-decisions-if-test-and-case', n='12.8',
    module_label='Module 12 · The shell environment and shell programming',
    title='Taking decisions: if-then-else, the test command, nested if and case',
    desc='if-then-fi, if-then-else-fi, elif and nested if; if tests an exit status; the test command and [ ]: file tests (-e -f -d -r -w -x -s -L -nt), string tests (= != -z -n) and integer tests (-eq -ne -lt -le -gt -ge); [[ ]] with patterns and =~ regex and BASH_REMATCH; (( )) comparisons; && || !; case with |, wildcards, character classes and *); class-note mistakes checked; 30+ runnable examples and variations.',
    og_desc='Bash if, elif, else, test [ ], [[ ]], (( )) and case explained with real outputs and 30+ examples.',
    minutes=45, level='Beginner → Advanced',
    lead='if runs a command and branches on its exit status; test and [ ] answer questions about files, strings and numbers; [[ ]] adds patterns and regex; case picks one branch out of many. This lesson covers all of them with many runnable examples.',
    chips=['if reads $? (animated)', 'File, string, number tests', 'case for menus', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A number check and a menu
n=-4
if [ "$n" -gt 0 ]; then
  echo "$n is positive"
elif [ "$n" -lt 0 ]; then
  echo "$n is negative"
else
  echo "$n is zero"
fi
action=status
case $action in
  start) echo "starting" ;;
  stop) echo "stopping" ;;
  status) echo "running" ;;
  *) echo "usage: start|stop|status" ;;
esac
"""

RUN = dict(
    heading='if/elif/else and case',
    intro='<p>Classify a number, then pick an action with case.</p>',
    code=MAIN,
    anno=[('elif [ "$n" -lt 0 ]; then', 'Checked only when the first test was false.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Change n to 0 and run again.', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which lines print? Then run.',
             code="f=/etc/hostname\n[ -e \"$f\" ] && echo exists\n[ -d \"$f\" ] && echo directory\n[ -s \"$f\" ] && echo 'not empty'\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the test should be false for 5. Fix the operator.',
             code="count=5\nif [ \"$count\" > 10 ]; then echo 'too many'; else echo ok; fi\nrm -f 10\n"),
        dict(label='4 · Your turn', hint='Check that x is a whole number with [[ =~ ]].',
             code="x=2026\nif [[ $x =~ ^[0-9]+$ ]]; then echo \"$x is a number\"; else echo 'not a number'; fi\n"),
        dict(label='5 · Challenge', hint='Make the case match Monday, MONDAY and monday.',
             code="day=MONDAY\ncase ${day,,} in monday) echo 'start of the week';; *) echo other;; esac\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: interactive decisions',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Ask and decide', cmd="read -rp 'Enter a number: ' n; if (( n % 2 )); then echo odd; else echo even; fi", output='Enter a number: 7\nodd', note='Typical: you type 7.'),
        dict(title='2 · Password check (from the notes, prompt fixed)', cmd="read -rsp 'Password: ' p; echo; [[ $p == CDAC ]] && echo 'correct' || echo 'wrong'", output='Password: \ncorrect', note='Typical: you type CDAC (hidden). The notes ask “Enter your username?” but compare a password.'),
        dict(title='3 · Is [ a real program too?', cmd='ls -l /usr/bin/[', output=pc("ls -l /usr/bin/[ | awk '{print $1, $NF}'"), note='Recorded (trimmed).'),
        dict(title='4 · test version', cmd='/usr/bin/test --version | head -1', output=pc('/usr/bin/test --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='if, elif and else, line by line',
    intro='<p>Step through a grade calculation: watch which tests run and which are skipped.</p>',
    code='''marks=78
if (( marks >= 90 )); then grade=A
elif (( marks >= 75 )); then grade=B
elif (( marks >= 50 )); then grade=C
else grade=F
fi
echo "marks $marks -> grade $grade"
''',
    notes={1: 'Input.', 2: 'First test :: false.', 3: 'Second test :: true, grade=B.', 7: 'The rest was skipped.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a disk alert, an input validator and a file-type router.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='Disk usage alert levels',
         problem='<p>Print OK, WARNING or CRITICAL for a usage percentage.</p>',
         inp='percentages', approach=['elif from the highest threshold.'],
         code='''for used in 45 81 96; do
  if (( used >= 90 )); then echo "$used%: CRITICAL"
  elif (( used >= 75 )); then echo "$used%: WARNING"
  else echo "$used%: OK"; fi
done
''', notes={2: 'Highest first.'}, tryit='Add a level for 100%.'),
    dict(level='i', tag='Developer', title='Validate script arguments',
         problem='<p>Require two arguments: a file that exists and a positive number.</p>',
         inp='two arguments', approach=['$#.', '-f.', '=~.'],
         code='''validate(){
  [ $# -eq 2 ] || { echo "usage: FILE COUNT"; return 2; }
  [ -f "$1" ] || { echo "no such file: $1"; return 1; }
  [[ $2 =~ ^[1-9][0-9]*$ ]] || { echo "not a positive number: $2"; return 1; }
  echo "ok: $1, $2"
}
validate /etc/hostname 3; validate /etc/hostname x; validate /nope 3; validate
''', notes={7: 'Four calls, four results.'}, expect='any', tryit='Add a check that the file is readable.'),
    dict(level='a', tag='Data', title='Route files by type',
         problem='<p>For each file, say what tool to use, ignoring upper/lower case.</p>',
         inp='file names', approach=['case ${f,,}.', 'Patterns with |.'],
         code='''for f in Q3.CSV report.json scan.Png notes; do
  case ${f,,} in
    *.csv) t=awk ;; *.json) t=jq ;; *.png|*.jpg) t=image-viewer ;; *) t=unknown ;;
  esac
  echo "$f -> $t"
done
''', notes={2: 'Lower-case first.'}, tryit='Add *.gz -> gunzip.'),
]

QUIZ = mix([
    dict(q='What does if actually check?', options=['the text printed', 'the exit status of the command', 'the variable type', 'the file size'], answer=1, why='0 = true.'),
    dict(q='Which test is true for a directory?', options=['-f', '-d', '-s', '-x only'], answer=1, why='-d.'),
    dict(q='Correct numeric comparison in [ ]?', options=['[ $a > $b ]', '[ "$a" -gt "$b" ]', '[ $a gt $b ]', '[ "$a" => "$b" ]'], answer=1, why='-gt.'),
    dict(q='Test for an empty string?', options=['-n', '-z', '-e', '-s'], answer=1, why='zero length.'),
    dict(q='Which ends an if?', options=['end', 'done', 'fi', 'esac'], answer=2, why='if backwards.'),
    dict(q='Which matches a regex?', options=['[ $x == re ]', '[[ $x =~ re ]]', '(( x =~ re ))', 'case $x =~'], answer=1, why='=~ in [[ ]].'),
    dict(q='case branch terminator?', options=[';', ';;', 'break', 'fi'], answer=1, why=';;'),
    dict(q='[ "$x" = yes ] vs [ $x = yes ] when x is empty?', options=['both fine', 'quoted works, unquoted errors', 'both error', 'unquoted works'], answer=1, why='Quote.'),
])

REVISION = [
    'if COND; then …; elif COND; then …; else …; fi — COND is any command; 0 = true.',
    '[ ] / test: files -e -f -d -s -r -w -x -L -nt; strings = != -z -n; numbers -eq -ne -lt -le -gt -ge. Spaces and quotes!',
    '[[ ]]: no quoting needed, == patterns, =~ regex (BASH_REMATCH), && || inside. (( )): numeric with > < ==.',
    '> < inside [ ] are redirections; as strings 10 < 9.',
    'case "$x" in a|b) …;; *.log) …;; [yY]*) …;; *) default;; esac — first match wins; ${x,,} for case-insensitive.',
    'Use if cmd directly (grep -q, id, cmp -s) instead of testing output text.',
]

FAQ = [
    ('How do I write an if-else in bash?', 'if [ condition ]; then commands; else commands; fi — spaces inside the brackets are required.'),
    ('How do I check if a file exists in bash?', '[ -f "$file" ] for a regular file, [ -e "$file" ] for anything, [ -d "$dir" ] for a directory.'),
    ('How do I compare numbers in bash?', 'Use -eq, -ne, -lt, -le, -gt, -ge inside [ ], or (( a > b )).'),
    ('What is the difference between [ ] and [[ ]]?', '[ ] is the POSIX test command and needs careful quoting; [[ ]] is a bash keyword with pattern and regex matching and no word splitting.'),
    ('How do I check if a string is empty?', '[ -z "$s" ] (empty) or [ -n "$s" ] (not empty).'),
    ('How does case work in bash?', 'case WORD in pattern) commands ;; … *) default ;; esac — the first matching glob pattern runs.'),
    ('How do I match a regex in bash?', '[[ $var =~ regex ]]; captured groups are in ${BASH_REMATCH[1]} etc.'),
]

PRACTICE_INTRO = 'Small decision tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Positive?', stmt='Print “positive” if n=9 is greater than 0.', inp='n=9', code="n=9; if [ \"$n\" -gt 0 ]; then echo positive; fi\n", explain='-gt.'),
    dict(level='easy', title='Exists', stmt='Print “ok” if /etc/passwd is a regular file.', inp='nothing', code="[ -f /etc/passwd ] && echo ok\n", explain='-f.'),
    dict(level='easy', title='Equal strings', stmt='Print “same” if a and b are both cdac.', inp='two variables', code="a=cdac; b=cdac; [ \"$a\" = \"$b\" ] && echo same\n", explain='='),
    dict(level='medium', title='Max of two', stmt='Print the larger of 34 and 71.', inp='two numbers', code="a=34; b=71; if (( a > b )); then echo $a; else echo $b; fi\n", explain='(( )).'),
    dict(level='medium', title='Empty check', stmt='Print “empty” for an empty variable.', inp='x=""', code="x=''; [ -z \"$x\" ] && echo empty\n", explain='-z.'),
    dict(level='medium', title='Extension', stmt='Print “csv” for data.csv using [[ == ]].', inp='a name', code="f=data.csv; [[ $f == *.csv ]] && echo csv\n", explain='Pattern.'),
    dict(level='business', title='Three-way case', stmt='Map r, g, b to red, green, blue; anything else → unknown (test with g and x).', inp='letters', code="for c in g x; do case $c in r) echo red;; g) echo green;; b) echo blue;; *) echo unknown;; esac; done\n", explain='case with default.'),
    dict(level='business', title='Leap year', stmt='Print whether 2028 is a leap year.', inp='a year', code="y=2028; if (( (y % 4 == 0 && y % 100 != 0) || y % 400 == 0 )); then echo leap; else echo 'not leap'; fi\n", explain='Combined conditions.'),
]

SCN_INTRO = 'Interview questions about decisions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Check if a number is even or odd”', 'Written test classic.', 'if + arithmetic?',
        '''<ul>
          <li><code>if (( n % 2 == 0 )); then echo even; else echo odd; fi</code></li>
          <li>Or <code>[ $((n % 2)) -eq 0 ]</code>.</li>
          <li>Validate n first.</li>
        </ul>''', 'using > inside [ ].') +
    scn('Service company', 'Junior', '“[ ] vs [[ ]]?”', 'Common follow-up.', 'details?',
        '''<ol>
          <li>[ ] = test command, POSIX, quote everything.</li>
          <li>[[ ]] = bash keyword: patterns, =~, && inside, no splitting.</li>
          <li>Use [ ] for /bin/sh scripts.</li>
        </ol>''', '“they are the same”.') +
    scn('Operations', 'Mid-level', 'A health check always says OK', 'if [ $status == "OK" ] where status is sometimes empty.', 'quoting?',
        '''<ul>
          <li>Empty unquoted variable: [ == "OK" ] → error, if takes else… or worse, logic inverted.</li>
          <li>Quote: [ "$status" = OK ]; set -u to catch unset.</li>
          <li>Test with bash -x.</li>
        </ul>''', 'adding sleep and retries.') +
    scn('Platform', 'Senior', 'Write a robust init-style script', 'start, stop, restart, status for a Java app.', 'structure?',
        '''<ul>
          <li>case "$1" in start|stop|restart|status; default prints usage, exit 2.</li>
          <li>PID file checks with -f and kill -0; exit codes per LSB (0 running, 3 stopped).</li>
          <li>Today: a systemd unit instead (Lesson 17.3).</li>
        </ul>''', 'a long if-elif chain without a default.')
) + interview([
    ('How to check a directory exists?', '[ -d "$dir" ].'),
    ('-e vs -f?', '-e anything exists; -f only regular files.'),
    ('How to negate a test?', '! : if [ ! -f f ]; or if ! cmd.'),
    ('What does -s test?', 'File exists and is not empty.'),
    ('What does -nt do?', 'Left file newer than right.'),
    ('How to match multiple patterns in case?', 'pat1|pat2).'),
    ('What is BASH_REMATCH?', 'Array of regex captures from =~.'),
], [
    ('RHCSA (EX200)', 'Use conditionals (if, test, [ ]) in scripts.'),
    ('LFCS', 'Conditional statements and case.'),
    ('CompTIA Linux+', 'if, test operators, case.'),
]) + distro('[ ] and case are POSIX; [[ ]] and (( )) are bash/zsh.', [
    ('if / case', 'yes', 'yes', 'yes', 'Git Bash'),
    ('[ ] / test', 'yes', 'yes', 'yes', '-'),
    ('[[ ]] =~', 'bash', 'bash', 'zsh/bash', '-'),
    ('${x,,} lowercase', 'bash 4+', 'bash 4+', 'bash 3.2: no', '-'),
    ('dash (/bin/sh)', '[ ] only', '-', '-', '-'),
]) + teaser('12.9', 'Riya’s checks now decide, but only once. To check every file in a folder, retry a download until it works, or process each line of a CSV, she needs loops: for, while, until, break and continue, plus select menus and getopts. Next: loops.')

CHEATSHEET = cheatsheet('if, test, case', [
    ('if', [('if C; then', 'start'), ('elif C; then', 'more'), ('else', 'default'), ('fi', 'end'), ('if ! C', 'not')]),
    ('Files', [('-e -f -d', 'exists/file/dir'), ('-s', 'not empty'), ('-r -w -x', 'permissions'), ('-L', 'link'), ('a -nt b', 'newer')]),
    ('Strings / numbers', [('= != -z -n', 'strings'), ('-eq -ne', 'equal'), ('-lt -le -gt -ge', 'order'), ('(( a > b ))', 'arith'), ('[[ x =~ re ]]', 'regex')]),
    ('case', [('case "$x" in', 'start'), ('a|b)', 'either'), ('*.log)', 'pattern'), ('*)', 'default'), (';; esac', 'end')]),
])

MINDMAP = mindmap('Decide', [
    ('if', 'blue', ['then elif else', 'fi', 'nested']),
    ('Files', 'green', ['-e -f -d', '-r -w -x -s', '-L -nt']),
    ('Strings', 'amber', ['= != -z -n', '[[ == * ]]', '=~ regex']),
    ('Numbers', 'red', ['-eq -lt -gt', '(( > ))', 'not > in [ ]']),
    ('case', 'violet', ['a|b)', '*.ext)', '*) esac']),
    ('Traps', 'acc', ['spaces in [ ]', 'quote $x', 'case-sensitive']),
])

LAB = lab('a service control script', 'Build the lab, write <code>~/lab128/svc.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab128 && cd ~/lab128 && rm -f svc.sh app.pid''',
    tasks=['With no argument, print <code>usage: svc.sh start|stop|status</code> and exit 2.',
           '<code>start</code> creates <code>app.pid</code> and prints <code>started</code>; if it already exists print <code>already running</code>.',
           '<code>stop</code> removes <code>app.pid</code> and prints <code>stopped</code>; <code>status</code> prints <code>running</code> or <code>stopped</code> using a file test.',
           'Any other action prints <code>unknown action: X</code> and exits 2. Actions must work in any upper/lower case (START, Stop…).'],
    solution='''cat > svc.sh <<'EOF'
#!/bin/bash
[ -n "${1:-}" ] || { echo "usage: svc.sh start|stop|status"; exit 2; }
case ${1,,} in
  start)  if [ -f app.pid ]; then echo "already running"; else touch app.pid; echo started; fi ;;
  stop)   rm -f app.pid; echo stopped ;;
  status) if [ -f app.pid ]; then echo running; else echo stopped; fi ;;
  *)      echo "unknown action: $1"; exit 2 ;;
esac
EOF''',
    check='''cd ~/lab128; rm -f app.pid
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f svc.sh ] || touch svc.sh
u=$(bash svc.sh 2>&1); us=$?
ok "1 usage"   '[ $us = 2 ] && [ "$u" = "usage: svc.sh start|stop|status" ]'
ok "2 start"   '[ "$(bash svc.sh start)" = started ] && [ -f app.pid ] && [ "$(bash svc.sh start)" = "already running" ]'
ok "3 status"  '[ "$(bash svc.sh status)" = running ] && [ "$(bash svc.sh stop)" = stopped ] && [ "$(bash svc.sh status)" = stopped ]'
x=$(bash svc.sh dance); xs=$?
ok "4 other"   '[ $xs = 2 ] && [ "$x" = "unknown action: dance" ] && [ "$(bash svc.sh START)" = started ] && [ "$(bash svc.sh Stop)" = stopped ]' ''')
