import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='09-loops-for-while-until-break-continue', n='12.9',
    module_label='Module 12 · The shell environment and shell programming',
    title='Loops: for, while, until, break and continue',
    desc='for over words, ranges ({1..10}, steps, seq), globs, "$@" and arrays; C-style for (( )); while with counters and conditions; while IFS= read -r for files and CSV; process substitution vs the pipe subshell trap; until for retries; break, continue, break 2, continue 2; select menus, while true + case menus and getopts option parsing; class-note syntax errors checked; 30+ runnable examples and variations.',
    og_desc='Bash loops explained: for, while, until, break, continue, select and getopts, with real outputs and 30+ examples.',
    minutes=45, level='Beginner → Advanced',
    lead='for walks through a list, while repeats while a command succeeds, until repeats until it succeeds; break and continue change the flow; select and getopts handle menus and options. This lesson covers them all with many runnable examples.',
    chips=['for, while, until', 'The pipe trap animated', 'select and getopts', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# for, while and until
for city in Pune Delhi Mumbai; do
  echo "office: $city"
done
i=1
while [ $i -le 3 ]; do
  echo "round $i"
  i=$((i + 1))
done
n=0
until [ $n -ge 2 ]; do
  echo "until: n=$n"
  n=$((n + 1))
done
"""

RUN = dict(
    heading='Three kinds of loops',
    intro='<p>A for over words, a while with a counter and an until that stops when the test succeeds.</p>',
    code=MAIN,
    anno=[('i=$((i + 1))', 'Without this line the while loop never ends.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. How many lines does each loop print?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which numbers are printed? Then run.',
             code="for i in 1 2 3 4 5 6; do\n  [ $i -eq 3 ] && continue\n  [ $i -eq 5 ] && break\n  echo $i\ndone\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the loop should print 1 to 3. Add what is missing.',
             code="for i in 1 2 3 do\n  echo $i\ndone\n", expect='any'),
        dict(label='4 · Your turn', hint='Print the multiplication table of 9 (1 to 5).',
             code="n=9\nfor i in {1..5}; do echo \"$n x $i = $((n * i))\"; done\n"),
        dict(label='5 · Challenge', hint='Count lines of a file into a variable and print it after the loop.',
             code="printf 'a\\nb\\nc\\n' > f.txt\nc=0; while IFS= read -r l; do c=$((c + 1)); done < f.txt\necho \"lines: $c\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: interactive loops',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · A select menu', cmd="PS3='Your choice: '; select c in date whoami quit; do [ \"$c\" = quit ] && break; $c; done", output='1) date\n2) whoami\n3) quit\nYour choice: 2\nriya\nYour choice: 3', note='Typical: you type 2, then 3.'),
        dict(title='2 · Live clock for 3 seconds', cmd='for i in 1 2 3; do date +%T; sleep 1; done', output='10:15:01\n10:15:02\n10:15:03', note='Typical.'),
        dict(title='3 · Stop an endless loop', cmd='while true; do echo working; sleep 1; done   # press Ctrl+C', output='working\nworking\n^C', note='Typical.'),
        dict(title='4 · bash version', cmd='bash --version | head -1', output=pc('bash --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A loop with continue and break',
    intro='<p>Step through: watch the variable, the skipped round and the early exit.</p>',
    code='''total=0
for n in 4 0 7 99 2; do
  [ $n -eq 0 ] && continue
  [ $n -eq 99 ] && break
  total=$((total + n))
done
echo "total $total"
''',
    notes={1: 'Start.', 2: 'Each round :: n takes the next value.', 3: '0 :: skipped.', 4: '99 :: stop.', 5: 'Add.', 7: '4 + 7 = 11; 2 was never reached.'},
)

WORKED_INTRO = 'Three tasks from real jobs: bulk users, a health retry and a CSV report.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='Bulk user commands from a list',
         problem='<p>Print the useradd command for each name in a file, skipping blank lines (dry run).</p>',
         inp='a names file', approach=['while read.', 'continue on empty.'],
         code='''printf 'riya\\n\\naman\\nneha\\n' > names.txt
while IFS= read -r u; do
  [ -z "$u" ] && continue
  echo "sudo useradd -m -s /bin/bash $u"
done < names.txt
''', notes={3: 'Skip blanks.', 4: 'Dry run.'}, tryit='Add a check that the user does not exist already (id).'),
    dict(level='i', tag='DevOps', title='Health check with retries',
         problem='<p>Retry a check up to 4 times; it succeeds on the third try (simulated).</p>',
         inp='nothing', approach=['until + counter.'],
         code='''tries=0
check(){ [ $tries -ge 3 ]; }
until check; do
  tries=$((tries + 1)); echo "try $tries: not ready"
  [ $tries -ge 4 ] && { echo 'giving up'; break; }
done
echo "finished after $tries tries"
''', notes={3: 'until the check succeeds.', 7: 'Result.'}, tryit='Make check always fail.'),
    dict(level='a', tag='Data', title='Per-city salary totals',
         problem='<p>From a CSV of name,city,salary, print the total per city using an associative array.</p>',
         inp='a CSV', approach=['while read.', 'declare -A (Lesson 12.13).'],
         code='''printf 'riya,Pune,85000\\naman,Delhi,72000\\nneha,Pune,91000\\n' > s.csv
declare -A tot
while IFS=, read -r n c s; do tot[$c]=$(( ${tot[$c]:-0} + s )); done < s.csv
for c in "${!tot[@]}"; do echo "$c ${tot[$c]}"; done | sort
''', notes={3: 'Add per city.', 4: 'Print sorted.'}, tryit='Also count people per city.'),
]

QUIZ = mix([
    dict(q='Which loop is best for each line of a file?', options=['for l in $(cat f)', 'while IFS= read -r l; do …; done < f', 'until read', 'select'], answer=1, why='One line per round.'),
    dict(q='until repeats…', options=['while the condition is true', 'until the condition succeeds', 'forever', 'once'], answer=1, why='Opposite of while.'),
    dict(q='continue does…', options=['stops the loop', 'skips to the next round', 'exits the script', 'restarts the script'], answer=1, why='Next iteration.'),
    dict(q='for i in {1..$n} with n=3 gives…', options=['1 2 3', '{1..3}', 'error', 'nothing'], answer=1, why='Braces before variables.'),
    dict(q='Why does cmd | while read …; count++ lose count?', options=['bash bug', 'the loop runs in a subshell', 'read clears it', 'pipes are slow'], answer=1, why='Child shell.'),
    dict(q='Leave two nested loops at once?', options=['break', 'break 2', 'exit 2', 'continue 2'], answer=1, why='break N.'),
    dict(q='In getopts "o:", the colon means…', options=['optional', 'o takes a value', 'o is long', 'ignore o'], answer=1, why='$OPTARG.'),
    dict(q='Missing in: for x in a b ___ echo $x; done', options=['do', '; do', 'then', 'in'], answer=1, why='; before do on one line.'),
])

REVISION = [
    'for x in LIST; do …; done — words, {1..10}, {0..20..5}, *.log, "$@", "${arr[@]}"; C-style for ((i=0;i<n;i++)).',
    'while COND repeats while 0; until COND repeats until 0; change something each round.',
    'Lines: while IFS= read -r l; do …; done < file (|| [ -n "$l" ] for a last line without \\n); CSV with IFS=,.',
    'cmd | while … runs in a subshell: use done < <(cmd) to keep variables.',
    'break / continue (N for nested); select menus with PS3 and REPLY; getopts "vo:" with OPTARG and shift $((OPTIND-1)).',
    'Never for f in $(ls) or for l in $(cat f); {1..$n} does not work.',
]

FAQ = [
    ('How do I write a for loop in bash?', 'for item in list; do commands; done — e.g. for f in *.txt; do echo "$f"; done.'),
    ('How do I loop over numbers in bash?', 'for i in {1..10} for fixed ranges; for ((i=1; i<=n; i++)) or seq 1 "$n" when the end is a variable.'),
    ('How do I read a file line by line in bash?', 'while IFS= read -r line; do …; done < file.'),
    ('What is the difference between while and until?', 'while repeats while the condition is true; until repeats until it becomes true.'),
    ('What do break and continue do?', 'break exits the loop; continue skips to the next iteration.'),
    ('Why are my variables empty after a while loop?', 'The loop was at the end of a pipe and ran in a subshell; use done < <(command) instead.'),
    ('How do I make a menu in bash?', 'select item in a b c; do …; done, or while true with read and case.'),
]

PRACTICE_INTRO = 'Small loop tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='1 to 5', stmt='Print 1 to 5 on one line.', inp='nothing', code="for i in {1..5}; do printf '%s ' $i; done; echo\n", explain='{1..5}.'),
    dict(level='easy', title='Countdown', stmt='Print 3 2 1 with a while loop.', inp='nothing', code="i=3; while [ $i -gt 0 ]; do printf '%s ' $i; i=$((i-1)); done; echo\n", explain='Counter down.'),
    dict(level='easy', title='Sum 1..10', stmt='Print the sum of 1 to 10.', inp='nothing', code="s=0; for i in {1..10}; do s=$((s+i)); done; echo $s\n", explain='55.'),
    dict(level='medium', title='Squares', stmt='Print the squares of 1 to 5.', inp='nothing', code="for ((i=1;i<=5;i++)); do printf '%s ' $((i*i)); done; echo\n", explain='C-style.'),
    dict(level='medium', title='Skip 3', stmt='Print 1 to 5 except 3.', inp='nothing', code="for i in {1..5}; do [ $i -eq 3 ] && continue; printf '%s ' $i; done; echo\n", explain='continue.'),
    dict(level='medium', title='Count lines', stmt='Count lines of a 4-line file with while read.', inp='a file', code="printf 'a\\nb\\nc\\nd\\n' > f; n=0; while read -r l; do n=$((n+1)); done < f; echo $n\n", explain='4.'),
    dict(level='business', title='Factorial of 5', stmt='Print 5! with a loop.', inp='nothing', code="f=1; for i in {2..5}; do f=$((f*i)); done; echo $f\n", explain='120.'),
    dict(level='business', title='First multiple of 7 above 50', stmt='Find it with until.', inp='nothing', code="n=51; until (( n % 7 == 0 )); do n=$((n+1)); done; echo $n\n", explain='56.'),
]

SCN_INTRO = 'Interview questions about loops, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Print numbers 1 to 10 using a loop”', 'Warm-up question.', 'two forms?',
        '''<ul>
          <li><code>for i in {1..10}; do echo $i; done</code></li>
          <li><code>i=1; while [ $i -le 10 ]; do echo $i; i=$((i+1)); done</code></li>
          <li>Mention seq and C-style for.</li>
        </ul>''', 'forgetting to increment.') +
    scn('Service company', 'Junior', '“Read a file line by line”', 'Follow-up after for loops.', 'correct idiom?',
        '''<ol>
          <li><code>while IFS= read -r line; do …; done &lt; file</code></li>
          <li>Why not <code>for line in $(cat file)</code>: splits at spaces.</li>
          <li>-r keeps backslashes; IFS= keeps leading spaces.</li>
        </ol>''', 'cat file | while … and then using the variables.') +
    scn('Operations', 'Mid-level', 'Retry a flaky service check', 'Health URL fails for the first 20 s after start.', 'bounded retry?',
        '''<ul>
          <li><code>for i in {1..10}; do curl -fs URL &amp;&amp; break; sleep 3; done</code></li>
          <li>Check the result after the loop; exit 1 if still failing.</li>
          <li>Back-off: sleep $((i*2)).</li>
        </ul>''', 'an endless while true without a limit.') +
    scn('Data team', 'Senior', 'Loop over 2 million lines is too slow', 'A while read loop with grep and cut inside.', 'performance?',
        '''<ul>
          <li>Each external command inside the loop costs a fork per line.</li>
          <li>Use one awk/sed/grep over the whole file, or bash built-ins only.</li>
          <li>Redirect once after done.</li>
        </ul>''', 'adding more servers.')
) + interview([
    ('for vs while?', 'for for known lists; while for conditions and reading lines.'),
    ('What does until do?', 'Repeats until the command succeeds.'),
    ('How to stop an infinite loop?', 'break inside, or Ctrl+C / a signal.'),
    ('What is $REPLY in select?', 'The number the user typed.'),
    ('What does getopts return at the end?', 'Non-zero, ending the while loop.'),
    ('How to loop over array items?', 'for x in "${arr[@]}".'),
    ('Why is {1..$n} wrong?', 'Brace expansion happens before variable expansion.'),
], [
    ('RHCSA (EX200)', 'Use looping constructs (for, etc.) to process file and command-line input.'),
    ('LFCS', 'Shell scripting: loops.'),
    ('CompTIA Linux+', 'for, while, until loops.'),
]) + distro('Loops are POSIX; a few forms are bash-only.', [
    ('for / while / until', 'yes', 'yes', 'yes', 'Git Bash'),
    ('for (( ))', 'bash', 'bash', 'bash/zsh', '-'),
    ('{1..10}', 'bash', 'bash', 'bash/zsh', '-'),
    ('select', 'bash/ksh', 'bash', 'bash/zsh', '-'),
    ('getopts', 'POSIX', 'POSIX', 'POSIX', '-'),
]) + teaser('12.10', 'Riya’s scripts now repeat the same block in three places. Functions let her name a block, give it arguments and a return status, keep variables local, and clean up with trap. Plus built-ins and tput for colours and screen control. Next: functions, built-ins and tput.')

CHEATSHEET = cheatsheet('Loops', [
    ('for', [('for x in a b', 'words'), ('in {1..10}', 'range'), ('in *.log', 'files'), ('in "$@"', 'args'), ('((i=0;i<n;i++))', 'C-style')]),
    ('while / until', [('while COND', 'while 0'), ('until COND', 'until 0'), ('while true', 'forever'), ('read -r l … < f', 'lines'), ('done < <(cmd)', 'keep vars')]),
    ('Control', [('break', 'leave'), ('continue', 'skip'), ('break 2', 'outer'), ('done > f', 'one redirect')]),
    ('Menus / options', [('select x in …', 'menu'), ('PS3 / REPLY', 'prompt / number'), ('getopts "vo:"', 'options'), ('OPTARG / OPTIND', 'value / index')]),
])

MINDMAP = mindmap('Loops', [
    ('for', 'blue', ['words, ranges', 'globs, "$@"', '(( )) C-style']),
    ('while', 'green', ['counter', 'read -r lines', 'while true']),
    ('until', 'amber', ['retries', 'wait for', '+ counter']),
    ('control', 'red', ['break', 'continue', 'N levels']),
    ('menus', 'violet', ['select', 'case', 'getopts']),
    ('traps', 'acc', ['; do', '$(ls)', 'pipe subshell']),
])

LAB = lab('a log report', 'Build the lab, write <code>~/lab129/report.sh</code> doing the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab129/logs && cd ~/lab129 && rm -f report.sh summary.txt
printf 'GET /a 200\\nGET /b 500\\n' > logs/mon.log; printf 'GET /c 200\\n' > logs/tue.log
printf 'GET /d 500\\nGET /e 500\\nGET /f 404\\n' > logs/wed.log; printf '# web servers\\nweb01\\n\\nweb02\\n' > hosts.txt''',
    tasks=['Loop over <code>logs/*.log</code> and write one line per file into <code>summary.txt</code>: <code>NAME COUNT</code> (NAME without .log, COUNT = lines ending in 500).',
           'Skip days with 0 errors (use continue).',
           'After the loop, append <code>total N</code> with the sum of all counts.',
           'Read <code>hosts.txt</code> line by line, skipping comments and blank lines, and append <code>host NAME</code> for each host.'],
    solution='''cat > report.sh <<'EOF'
#!/bin/bash
total=0
for f in logs/*.log; do
  n=$(grep -c ' 500$' "$f")
  total=$((total + n))
  [ "$n" -eq 0 ] && continue
  echo "$(basename "$f" .log) $n"
done > summary.txt
echo "total $total" >> summary.txt
while IFS= read -r h; do
  [[ -z $h || $h == \\#* ]] && continue
  echo "host $h"
done < hosts.txt >> summary.txt
EOF''',
    check='''cd ~/lab129; rm -f summary.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f report.sh ] && bash report.sh
ok "1 per file" 'grep -qx "mon 1" summary.txt && grep -qx "wed 2" summary.txt'
ok "2 skip 0"   '[ -f summary.txt ] && ! grep -q "^tue" summary.txt'
ok "3 total"    'grep -qx "total 3" summary.txt'
ok "4 hosts"    '[ "$(grep -c "^host " summary.txt)" = 2 ] && grep -qx "host web02" summary.txt' ''')
