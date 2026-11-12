import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='07-script-input-positional-parameters-read-and-arithmetic', n='12.7',
    module_label='Module 12 · The shell environment and shell programming',
    title='Script input: positional parameters, read, echo, expr and $(( )) arithmetic',
    desc='Command-line arguments $0, $1…${10}, $#, "$@", $*, shift, ${1:?} and ${1:-default}; read with -p -s -t -n -a -r and IFS, reading files line by line; arithmetic with $(( )), (( )), let and expr (with its string functions length, substr, index), integer division, leading-zero octal trap, 64-bit overflow; decimals with bc and awk; real outputs, class-note corrections, 15+ examples and variations.',
    og_desc='Bash script input and arithmetic: $1, $#, "$@", shift, read, expr, $(( )) and bc, with real outputs and many examples.',
    minutes=45, level='Beginner → Advanced',
    lead='Scripts get input in two ways, arguments when they start and read while they run, and the shell only does whole-number maths unless you call bc. This lesson covers $1 $# "$@" shift, read, $(( )), expr and bc with many runnable examples.',
    chips=['$1 $# "$@" shift', 'read -p -s -t -a', 'expr vs $(( )) vs bc', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Arguments, read and arithmetic in one script
cat > info.sh <<'EOF'
#!/bin/bash
echo "script: $0, you gave $# arguments: $@"
name=${1:-guest}
read -r -p "Age of $name: " age
echo "$name is $age; in 5 years: $(( age + 5 ))"
EOF
bash info.sh Riya <<< 24
"""

RUN = dict(
    heading='Arguments, read and $(( ))',
    intro='<p>A script that uses an argument, asks a question (answered here with <code>&lt;&lt;&lt;</code>) and calculates.</p>',
    code=MAIN,
    anno=[('bash info.sh Riya <<< 24', 'Riya is $1; 24 is the answer read receives.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Where does 24 come from?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the two divisions print? Then run.',
             code="echo $(( 7 / 2 ))\necho 'scale=2; 7/2' | bc\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is 5 times 3 with expr. Fix it.',
             code="expr 5 * 3 2>&1 | head -1\n"),
        dict(label='4 · Your turn', hint='Print the tenth argument correctly.',
             code="set -- a b c d e f g h i j\necho \"${10}\"\n"),
        dict(label='5 · Challenge', hint='Read three words; put the first in x and the rest in y.',
             code="read -r x y <<< 'red green blue'\necho \"x=$x y=$y\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real keyboard input',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · read with a prompt', cmd="read -rp 'Your city: ' c; echo \"Hello from $c\"", output='Your city: Pune\nHello from Pune', note='Typical: you type Pune.'),
        dict(title='2 · Hidden input', cmd="read -rsp 'PIN: ' p; echo; echo \"${#p} digits entered\"", output='PIN: \n4 digits entered', note='Typical: what you type is not shown.'),
        dict(title='3 · One key press', cmd="read -rn1 -p 'Continue? [y/n] ' k; echo; echo \"you pressed $k\"", output='Continue? [y/n] y\nyou pressed y', note='Typical: returns after one key.'),
        dict(title='4 · bc version', cmd='bc --version | head -1', output=pc('bc --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Arguments and maths, line by line',
    intro='<p>Step through: set arguments, count them, shift, and calculate.</p>',
    code='''set -- 40 15 7
total=$(( $1 + $2 + $3 ))
count=$#
shift
avg=$(( total / count ))
echo "after shift: $1 $2; total $total, avg $avg"
''',
    notes={1: 'Arguments :: $1=40 $2=15 $3=7.', 2: 'Sum :: 62.', 3: 'Count :: 3.', 4: 'shift :: $1 is now 15.', 5: 'Integer average :: 20.', 6: 'Summary.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a disk alert, a login prompt and a marks report.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='Disk usage alert with a threshold argument',
         problem='<p>Take a limit as $1 (default 80) and compare it with a usage percentage.</p>',
         inp='a number', approach=['${1:-80}.', '(( )) comparison.'],
         code='''check(){ limit=${1:-80}; used=86
  if (( used > limit )); then echo "ALERT: $used% > $limit%"; else echo "ok: $used% <= $limit%"; fi; }
check; check 90
''', notes={3: 'Default 80, then 90.'}, tryit='Call check 50.'),
    dict(level='i', tag='Security', title='Login prompt with a hidden password',
         problem='<p>Ask for a user and a password; never show the password; report its length only.</p>',
         inp='two answers', approach=['read -p and read -s.'],
         code='''printf 'riya\\nS3cret!9\\n' | {
  read -r -p 'User: ' u
  read -r -s -p 'Password: ' p
  echo "user $u, password of ${#p} characters received"
}
''', notes={4: 'Only the length is printed.'}, tryit='Add a check that the password is at least 8 characters.'),
    dict(level='a', tag='Data', title='Marks report with decimals',
         problem='<p>Given marks as arguments, print the count, total and average with two decimals.</p>',
         inp='marks as arguments', approach=['Loop over "$@".', 'bc for the average.'],
         code='''set -- 70 71 71 88
total=0; for m in "$@"; do total=$(( total + m )); done
avg=$(bc <<< "scale=2; $total / $#")
echo "count $#, total $total, average $avg"
''', notes={2: 'Sum.', 3: 'Decimal average.'}, tryit='Round with printf %.1f.'),
]

QUIZ = mix([
    dict(q='What does $# hold?', options=['the script name', 'the number of arguments', 'the last argument', 'the PID'], answer=1, why='Count.'),
    dict(q='How do you get the 10th argument?', options=['$10', '${10}', '$(10)', '$[10]'], answer=1, why='Braces.'),
    dict(q='What does shift do?', options=['adds an argument', 'drops $1 and moves the rest down', 'reverses them', 'counts them'], answer=1, why='Like a queue.'),
    dict(q='echo $(( 7 / 2 )) prints…', options=['3.5', '3', '4', 'an error'], answer=1, why='Integers only.'),
    dict(q='Correct expr multiplication?', options=['expr 5*3', 'expr 5 * 3', 'expr 5 \\* 3', 'expr(5*3)'], answer=2, why='Spaces and \\*.'),
    dict(q='Which read option hides typing?', options=['-p', '-s', '-t', '-r'], answer=1, why='Silent.'),
    dict(q='How do you get 3.50 for 7/2?', options=['$((7/2))', "echo 'scale=2; 7/2' | bc", 'expr 7 / 2', 'let 7/2'], answer=1, why='bc.'),
    dict(q='read a b <<< "x y z": b is…', options=['y', 'z', 'y z', 'empty'], answer=2, why='Last gets the rest.'),
])

REVISION = [
    '$0 script, $1…$9, ${10}+, $# count, "$@" all (separately), "$*" all (one string); shift drops $1.',
    'Check input: ${1:?usage …} (required), ${2:-default} (optional), [ $# -eq N ].',
    'read -r always; -p prompt, -s silent, -t timeout, -n chars, -a array; IFS=, read for CSV; last variable gets the rest.',
    '$(( )) integer maths (+ - * / % **, ++, +=, ?:); (( )) as a condition; let is older.',
    'expr: spaces between all parts, \\* for multiply, \\( \\); string functions length/substr/index; exits 1 when result is 0.',
    'Decimals: bc (scale truncates) or awk/printf (rounds). Leading 0 = octal: use 10#08.',
]

FAQ = [
    ('How do I pass arguments to a bash script?', 'Write them after the script name (./s.sh a b); inside, use $1, $2, $# and "$@".'),
    ('How do I access the 10th argument?', 'Use braces: ${10}. $10 means $1 followed by 0.'),
    ('How do I read user input in bash?', 'read -r -p "Prompt: " variable; add -s for hidden input and -t for a timeout.'),
    ('How do I do arithmetic in bash?', 'Use $(( expression )) for integers, e.g. $(( a + b )); use bc or awk for decimals.'),
    ('Why does expr 5 * 3 fail?', 'The shell expands * as a wildcard; write expr 5 \\* 3 with spaces.'),
    ('How do I get decimals in bash?', "echo 'scale=2; 7/2' | bc, or awk 'BEGIN{printf \"%.2f\", 7/2}'."),
    ('What is the difference between $@ and $*?', '"$@" keeps each argument separate; "$*" joins them into one string.'),
]

PRACTICE_INTRO = 'Small input and arithmetic tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Sum of two', stmt='Print the sum of the two arguments 15 and 27.', inp='set -- 15 27', code="set -- 15 27; echo $(( $1 + $2 ))\n", explain='$(( )).'),
    dict(level='easy', title='Count', stmt='Print how many arguments were given (a b c d).', inp='set --', code="set -- a b c d; echo $#\n", explain='$#.'),
    dict(level='easy', title='Remainder', stmt='Print the remainder of 29 divided by 6.', inp='nothing', code="echo $(( 29 % 6 ))\n", explain='%.'),
    dict(level='medium', title='Square and cube', stmt='Print the square and cube of 7.', inp='nothing', code="n=7; echo \"$(( n ** 2 )) $(( n ** 3 ))\"\n", explain='**.'),
    dict(level='medium', title='expr product', stmt='Multiply 12 and 4 with expr.', inp='nothing', code="expr 12 \\* 4\n", explain='\\*.'),
    dict(level='medium', title='Read two values', stmt='Read “Riya 24” into name and age and print “Riya:24”.', inp='a here-string', code="read -r name age <<< 'Riya 24'; echo \"$name:$age\"\n", explain='read.'),
    dict(level='business', title='Celsius to Fahrenheit', stmt='Convert 37 °C to °F with one decimal.', inp='nothing', code="c=37; echo \"scale=1; $c * 9 / 5 + 32\" | bc\n", explain='bc.'),
    dict(level='business', title='Simple interest', stmt='Principal 50000, rate 7.5 %, 3 years: print the interest with two decimals.', inp='nothing', code="p=50000; r=7.5; t=3; echo \"scale=2; $p * $r * $t / 100\" | bc\n", explain='Decimals need bc.'),
]

SCN_INTRO = 'Interview questions about script input and arithmetic, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Write a script that adds two numbers given as arguments”', 'Very common written test.', 'arguments + maths?',
        '''<ul>
          <li><code>[ $# -eq 2 ] || { echo "usage: $0 A B"; exit 1; }</code></li>
          <li><code>echo $(( $1 + $2 ))</code></li>
          <li>Mention bc for decimals.</li>
        </ul>''', 'using expr without spaces.') +
    scn('Service company', 'Junior', '“$@ vs $*, and $# ?”', 'Follow-up question.', 'precise?',
        '''<ol>
          <li>$# = number of arguments.</li>
          <li>"$@" = each argument separately; "$*" = one string.</li>
          <li>Show with an argument containing a space.</li>
        </ol>''', 'saying they are identical.') +
    scn('Operations', 'Mid-level', 'A script waits forever in cron', 'It asks for confirmation with read.', 'unattended input?',
        '''<ul>
          <li>No terminal in cron: read gets EOF or hangs on a pipe.</li>
          <li>Accept the answer as an argument or flag (--yes); use read -t with a default for humans.</li>
          <li>Check [ -t 0 ] to see if stdin is a terminal.</li>
        </ul>''', 'adding sleep.') +
    scn('Data team', 'Senior', 'Totals are wrong by a few rupees', 'A shell report uses $(( )) on amounts.', 'integer maths?',
        '''<ul>
          <li>$(( )) truncates decimals and divisions.</li>
          <li>Work in paise (integers) or use bc/awk; round only when printing.</li>
          <li>For real reporting, use awk/Python/SQL.</li>
        </ul>''', 'rounding at every step.')
) + interview([
    ('What is $0?', 'The name the script was called with.'),
    ('How to read input into an array?', 'read -r -a arr.'),
    ('How to do floating point maths in shell?', 'bc (scale=N) or awk.'),
    ('What does let do?', 'Evaluates an arithmetic expression (like (( ))).'),
    ('Why ${10} and not $10?', '$10 is $1 followed by 0.'),
    ('How to give read a timeout?', 'read -t SECONDS.'),
    ('What does expr length "abc" print?', '3.'),
], [
    ('RHCSA (EX200)', 'Process script inputs ($1, $2, etc.).'),
    ('LFCS', 'Shell scripting: arguments and arithmetic.'),
    ('CompTIA Linux+', 'Positional parameters, read, expr and $(( )).'),
]) + distro('Same in POSIX shells, with some bash extras.', [
    ('$1 $# "$@" shift', 'yes', 'yes', 'yes', 'Git Bash'),
    ('$(( ))', 'yes (dash too)', 'yes', 'yes', '-'),
    ('read -p -s -a', 'bash only', 'bash', 'zsh: read "x?prompt"', '-'),
    ('expr', 'coreutils', 'coreutils', 'BSD expr (no length)', '-'),
    ('bc', 'apt install bc', 'yes', 'yes', '-'),
]) + teaser('12.8', 'Riya’s calculator must refuse letters, a backup must check that the folder exists, and a menu must do different things for start, stop and status. Next: if-then-else, the test command with file and string tests, nested if, and case.')

CHEATSHEET = cheatsheet('Script input', [
    ('Arguments', [('$0', 'script'), ('$1 … ${10}', 'args'), ('$#', 'count'), ('"$@"', 'all'), ('shift', 'drop $1')]),
    ('Checks', [('${1:?msg}', 'required'), ('${1:-x}', 'default'), ('[ $# -eq 2 ]', 'exact count'), ('${!#}', 'last')]),
    ('read', [('-r', 'raw'), ('-p TEXT', 'prompt'), ('-s', 'silent'), ('-t N', 'timeout'), ('-a arr', 'array')]),
    ('Maths', [('$(( a+b ))', 'integers'), ('(( x > 5 ))', 'condition'), ('expr 5 \\* 3', 'old'), ("bc <<< 'scale=2; 7/2'", 'decimals')]),
])

MINDMAP = mindmap('Input', [
    ('Arguments', 'blue', ['$1 $2 ${10}', '$# "$@"', 'shift']),
    ('Checks', 'red', ['${1:?}', '${1:-}', 'usage + exit 2']),
    ('read', 'green', ['-r -p', '-s -t -n', '-a IFS']),
    ('$(( ))', 'amber', ['+ - * / %', '** ++ +=', 'integers']),
    ('expr', 'violet', ['spaces', '\\*', 'length substr']),
    ('Decimals', 'acc', ['bc scale', 'awk printf', 'round at end']),
])

LAB = lab('a salary calculator', 'Build the lab, write <code>~/lab127/pay.sh</code> doing the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab127 && cd ~/lab127 && rm -f pay.sh''',
    tasks=['The script takes the monthly salary as <code>$1</code> and exits with status 2 and a usage message if it is missing.',
           'It reads the bonus percentage with <code>read</code> (from standard input).',
           'It prints <code>annual: N</code> where N = salary × 12 + salary × bonus / 100 (integer maths).',
           'It prints <code>monthly with bonus: X</code> with two decimals using bc: (annual / 12).'],
    solution='''cat > pay.sh <<'EOF'
#!/bin/bash
[ $# -ge 1 ] || { echo "usage: pay.sh SALARY" >&2; exit 2; }
sal=$1
read -r bonus
annual=$(( sal * 12 + sal * bonus / 100 ))
echo "annual: $annual"
echo "monthly with bonus: $(bc <<< "scale=2; $annual / 12")"
EOF''',
    check='''cd ~/lab127
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f pay.sh ] || touch pay.sh
bash pay.sh < /dev/null > /dev/null 2>&1; st=$?
out=$(bash pay.sh 50000 <<< 10 2>/dev/null)
ok "1 usage"   '[ "$st" = 2 ]'
ok "2 read"    'grep -q "read" pay.sh'
ok "3 annual"  'echo "$out" | grep -qx "annual: 605000"'
ok "4 monthly" 'echo "$out" | grep -qx "monthly with bonus: 50416.66"' ''')
