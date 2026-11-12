import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

SI = r"""rm -rf ~/si; mkdir -p ~/si; cd ~/si
printf 'riya,Pune,85000\naman,Delhi,72000\nneha,Mumbai,91000\n' > staff.csv
cat > args.sh <<'EOF'
#!/bin/bash
echo "script : $0"
echo "first  : $1"
echo "second : $2"
echo "count  : $#"
echo "all    : $@"
EOF
chmod +x args.sh"""

HOOK = hook('Riya’s backup script always backs up the same folder. Her lead asks for one script that works for <b>any</b> folder: <code>./backup.sh /var/www</code>, <code>./backup.sh /etc</code>. Another script must <b>ask</b> the operator for a ticket number before deleting anything. A third must compute disk usage in GB from a number in KB. Those are the three ways a script gets input and works with numbers: <b>positional parameters</b> (<code>$1</code>, <code>$2</code>, <code>$#</code>, <code>$@</code>), the <b><code>read</code></b> command, and <b>arithmetic</b> (<code>$(( ))</code>, <code>expr</code>, <code>let</code>, and <code>bc</code> for decimals). This lesson is where scripts stop being fixed recipes and become tools.',
    ['use command-line arguments: <code>$0</code>, <code>$1</code>…<code>${10}</code>, <code>$#</code>, <code>"$@"</code>, <code>shift</code>, and check that enough were given',
     'ask the user with <code>read</code>: <code>-p</code> prompt, <code>-s</code> silent, <code>-t</code> timeout, <code>-r</code> raw, several variables, arrays, reading a file line by line',
     'do arithmetic with <code>$(( ))</code>, <code>(( ))</code>, <code>let</code> and <code>expr</code> (including its string functions), and decimals with <code>bc</code>',
     'avoid the classic traps: <code>$10</code>, <code>expr 5 * 3</code>, <code>expr 5+3</code>, integer division, <code>read</code> without <code>-r</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, 'one script, any folder'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'Script input', 5, 'simple meaning + 4 depths'),
    ('types', 'Arguments vs read; arithmetic forms', 5, 'side by side'),
    ('commands', 'By field', 16, 'real runs'),
    ('animation', 'See it happen', 4, 'arguments and shift'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a salary calculator'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Input given when the script starts', './s.sh FILE DAYS  →  $1 $2', 'arguments'),
    ('How many arguments?', '$#', 'check before using'),
    ('All arguments, unchanged', '"$@"', 'loops and forwarding'),
    ('Ask while running', "read -p 'Name: ' name", 'interactive'),
    ('Ask for a password', "read -s -p 'Password: ' pw", 'no echo'),
    ('Whole-number maths', 'echo $(( a * b ))', 'fast, built in'),
    ('Decimal maths', "echo 'scale=2; 7/2' | bc", '3.50'),
    ('Old scripts / POSIX', 'expr $a + $b', 'spaces and \\* needed'),
])

cmap = concept_map(
    [('12.4', 'Quoting', '"$@"'), ('12.5', 'First script', 'running it'), ('12.6', 'set -u', '${1:?}')],
    ['$0, $1…${10}, $#, $@, $*, shift', 'read: -p -s -t -n -r -a, IFS', '$(( )), (( )), let', 'expr (numbers and strings)', 'bc for decimals'],
    [('12.8', 'if, test, case', 'decide on input'), ('12.9', 'Loops', 'process every argument'), ('12.10', 'Functions', 'their own $1'), ('6.5', 'awk', 'maths on columns')],
    'Arguments come in at start ($1, $#, "$@"); read asks while running; $(( )) does whole-number maths and bc does decimals.')

sc = (term(20, 14, 316, 156, ['$ ./backup.sh /etc 7', ('backing up /etc, keeping 7 days', 'out'), '$ ./add.sh 12 30', ('12 + 30 = 42', 'out'), '$ ./ticket.sh', ('Ticket number: INC-4471', 'acc'), ('ok, deleting for INC-4471', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Three inputs:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• arguments: $1 $2', '• count: $#', '• read: ask', '• $(( )): maths', '• bc: decimals'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>One script, any folder</h2>
  <div class="story">
''' + puzzle('Riya’s script averages marks: <code>avg=$(( (m1 + m2 + m3) / 3 ))</code>. For the marks 85, 90 and 92 it prints <b>89</b>, but her calculator says 89.0. For 70, 71 and 71 it prints 70, the calculator says 70.67. And a colleague’s version with <code>expr ($m1 + $m2 + $m3) / 3</code> fails with a syntax error. What is going on in each case, and how do you print 70.67?') + '''
    <p class="narration">Riya’s scripts learn to take input three different ways.</p>
''' + scene('A terminal: backup.sh with a folder and a number of days, add.sh adding two numbers, and ticket.sh asking for a ticket number.', sc,
            'Arguments at the start, <tspan font-weight="700" class="s-acc">read</tspan> while running, <tspan font-weight="700" class="s-acc">$(( ))</tspan> for maths.') + '''
K> How does the script know what I typed after its name?
A> The shell splits your command line into words. Word 0 is the script itself (<code>$0</code>), the next ones become <code>$1</code>, <code>$2</code>… and <code>$#</code> is how many there are. <code>"$@"</code> is all of them.
R> And numbers? Everything in the shell is text.
A> Exactly, so you must ask for maths explicitly: <code>$(( ))</code> treats the text as whole numbers. That is why 89.0 became 89, and 70.67 became 70: the shell only does integers. For decimals you call <code>bc</code>. Today: arguments, <code>read</code>, and every way to calculate.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A courier form: the boxes filled before sending are arguments ($1, $2), a phone call during delivery is read, and the calculator in the van is $(( )) for whole numbers and bc for decimals.">'
       + label_box(14, 20, 190, 110, ['arguments', 'boxes filled BEFORE:', './s.sh /etc 7', '$1=/etc  $2=7'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['read', 'a question DURING:', '“Ticket number?”', 'answer → variable'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['arithmetic', '$(( 7 / 2 )) = 3', 'bc: 7/2 = 3.50', 'text → numbers'], 'amber', 8.6)
       + t(320, 160, 'Arguments suit cron and other scripts; read suits people.', 9.6, 'ink2')
       + t(320, 182, 'The shell counts in whole numbers only.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Script input at four depths', [
    ('v', 'No jargon: a courier form', '      <p>Information can arrive before the job starts, or be asked for during it.</p>' + pic),
    ('b', 'What you will type every day', '''      <ul>
        <li><code>./greet.sh Riya</code> → inside, <code>$1</code> is Riya.</li>
        <li><code>echo "You gave $# arguments: $@"</code>.</li>
        <li><code>read -p "Your city: " city</code> asks and stores the answer.</li>
        <li><code>total=$(( price * qty ))</code> multiplies.</li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li><code>$0</code> = how the script was called; <code>$1</code>–<code>$9</code>; from 10 on use braces: <code>${10}</code>. <code>$#</code> = count; <code>"$@"</code> = all, each kept whole (Lesson 12.4).</li>
        <li><code>shift</code> drops <code>$1</code> and moves the rest down; <code>shift 2</code> drops two.</li>
        <li><code>read a b c</code> splits the line at IFS: the <b>last</b> variable gets everything left. Always use <code>-r</code> (keep backslashes).</li>
        <li><code>$(( ))</code>: + - * / % ** and ( ), integers only, variables without $. Division truncates: 7/2 = 3.</li>
        <li><code>expr</code> needs spaces between every part and <code>\\*</code> for multiply; it prints the result and exits 1 when the result is 0.</li>
      </ul>'''),
    ('a', 'Behind the screen: how the numbers really work', '''      <ul>
        <li>Positional parameters come from the argv array given to execve() (Lesson 11.1); <code>set --</code> replaces them, functions get their own set (12.10).</li>
        <li>bash arithmetic is 64-bit signed: up to 9223372036854775807, then it wraps without warning. Numbers with a leading 0 are octal: <code>$((010))</code> is 8, so <code>$((08))</code> is an error (beware dates like 08, 09).</li>
        <li><code>expr</code> is an external program (/usr/bin/expr), so each call costs a fork: in a loop of 10,000 it is much slower than <code>$(( ))</code>.</li>
        <li><code>read</code> reads one byte at a time from a pipe to stop exactly at the newline; <code>cmd | read x</code> runs read in a subshell, so x is lost (use <code>&lt;&lt;&lt;</code> or <code>&lt; file</code>).</li>
        <li><code>bc</code> is an arbitrary-precision calculator language; <code>scale</code> sets digits after the point and every step is truncated, not rounded.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Positional parameters, read and shell arithmetic</h2>
''' + def_block(
    '<b>Positional parameters</b> (<code>$1</code>, <code>$2</code>, …) hold the arguments given to a script or function; <code>$0</code> is its name, <code>$#</code> their number and <code>$@</code> / <code>$*</code> all of them. The <code>read</code> builtin reads a line from standard input and assigns its words to variables. <b>Arithmetic expansion</b> <code>$(( expression ))</code> evaluates integer expressions; <code>expr</code> is an older external command for the same, and <code>bc</code> handles decimal numbers.',
    'Arguments = input before the start. read = input during the run. $(( )) = whole-number maths.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Argument', 'A word after the script name.'),
    ('Positional parameter', '$1, $2…: arguments by position.'),
    ('$#', 'Number of arguments.'),
    ('shift', 'Drop $1, move the rest down.'),
    ('read', 'Read one line into variables.'),
    ('Arithmetic expansion', '$(( )) → a number.'),
    ('Integer', 'A whole number (no decimals).'),
    ('bc', 'Calculator for decimals.'),
]) + '\n' + names('Where the names come from.', [
    ('$1', 'positional parameter 1', 'First argument.'),
    ('$#', 'count', '# = number sign.'),
    ('$0', 'argument zero', 'The command itself.'),
    ('shift', 'shift left', 'Like a queue.'),
    ('read -r', 'raw', 'Backslashes kept.'),
    ('expr', 'expression', 'Unix V7, 1979.'),
    ('let', 'let x = …', 'From BASIC.'),
    ('bc', 'basic calculator', 'Unix V6, 1975.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('First arg', '<code>$1</code>'),
    ('Count', '<code>$#</code>'),
    ('Ask', "<code>read -rp 'X: ' x</code>"),
    ('Add', '<code>$((a + b))</code>'),
    ('Decimals', "<code>bc &lt;&lt;&lt; 'scale=2; 7/2'</code>"),
    ('expr ×', '<code>expr 5 \\* 3</code>'),
]) + '\n' + lv + didyou('<code>$0</code> is not always the file name you think: run the same script as <code>./s.sh</code>, <code>bash s.sh</code> or <code>/home/riya/s.sh</code> and $0 is exactly what you typed. Use <code>basename "$0"</code> in usage messages.') + '''
EXAM> “Write a script that takes two numbers as arguments and prints their sum.” → <code>echo "$1 + $2 = $(( $1 + $2 ))"</code>, with a check <code>[ $# -eq 2 ] || { echo "usage: $0 A B"; exit 1; }</code>.
''' + qc('A script is run as <code>./s.sh a b c d e f g h i j k</code>. What do <code>$10</code> and <code>${10}</code> print?', '$10 is ${1} followed by 0: a0. ${10} is the tenth argument: j.') + mistake('letters=( "A""B""C""D""E" ); echo "${letters:1:3}"   (expecting B C D)',
    'letters=( A B C D E ); echo "${letters[@]:1:3}"',
    'Without spaces "A""B"… is ONE element, ABCDE; ${letters:1:3} cuts characters from it (BCD). An array slice needs [@]. Checked on our build machine (from the class notes’ slicing example).') + mistake('“255: exit status out of range”',
    'Exit statuses are 0–255 and wrap: exit 256 gives 0 (success!), exit 300 gives 44',
    'There is no error for out-of-range values; bash keeps only the lowest 8 bits. Checked: bash -c "exit 256"; echo $? prints 0.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Arguments vs read, and the four ways to calculate</h2>
''' + table(['', 'Arguments ($1 …)', 'read'], [
    ['When', 'given at start', 'asked while running'],
    ['Works in cron / CI', 'yes', 'no (nobody to answer)'],
    ['Scriptable by other scripts', 'yes', 'only through a pipe or file'],
    ['Good for', 'file names, options, numbers', 'confirmations, passwords, menus'],
    ['Check', '<code>$#</code>, <code>${1:?}</code>', 'empty answer, <code>-t</code> timeout'],
], minw=520) + table(['Form', 'Example', 'Decimals', 'Notes'], [
    ['<code>$(( ))</code>', 'echo $((a * b))', 'no', 'best: built in, fast'],
    ['<code>(( ))</code>', '((count++)); ((a &gt; b))', 'no', 'a command: status 0/1, used in if'],
    ['<code>let</code>', 'let "x = a + b"', 'no', 'old, quote it'],
    ['<code>expr</code>', 'expr $a \\* $b', 'no', 'external, spaces, \\*'],
    ['<code>bc</code>', "bc &lt;&lt;&lt; 'scale=2; a/b'", 'yes', 'external, for money and averages'],
    ['<code>awk</code>', "awk 'BEGIN{print 7/2}'", 'yes', 'handy inside pipelines'],
], minw=560) + table(['Variable', 'Meaning', 'For ./s.sh x "y z"'], [
    ['<code>$0</code>', 'script as called', './s.sh'],
    ['<code>$1 $2</code>', 'arguments', 'x · y z'],
    ['<code>$#</code>', 'count', '2'],
    ['<code>"$@"</code>', 'all, separate', 'x | y z'],
    ['<code>"$*"</code>', 'all, one string', 'x y z'],
    ['<code>$?</code> / <code>$$</code> / <code>$!</code>', 'status / PID / last background', '(Lesson 11.1)'],
], minw=440) + qc('Which arithmetic form can be used directly as an <code>if</code> condition?', '<code>(( ))</code>: <code>if (( a &gt; b )); then …</code>. It returns status 0 when the result is non-zero.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Script input and arithmetic, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/si</code> with <code>staff.csv</code> (three lines: name, city, salary) and <code>args.sh</code>, a script that prints <code>$0</code>, <code>$1</code>, <code>$2</code>, <code>$#</code> and <code>$@</code>. Questions asked by <code>read</code> are answered through a pipe or <code>&lt;&lt;&lt;</code>, because the recorder has no keyboard.</p>
''' + cmdcard_u(['any script that works on files, folders, users or numbers given by the caller', 'scripts run by cron and other scripts'],
               ['using $1 without checking it exists', '$10 without braces'])(
    'pos', '$0 · $1 … ${10} · $# · "$@" · shift', 'arguments',
    'Words after the script name become <code>$1</code>, <code>$2</code>…; <code>$0</code> is the script, <code>$#</code> the count, <code>"$@"</code> all of them. <code>shift [N]</code> removes the first N. Check input early: <code>[ $# -ge 1 ] || { echo "usage: …"; exit 1; }</code> or <code>${1:?message}</code>.',
    './s.sh ARG1 ARG2 …   ·   $1 $#  "$@"   ·   shift', 'safe',
    [('$0', 'script name', 'usage messages'),
     ('$1 … $9', 'arguments 1–9', 'inputs'),
     ('${10}', 'argument 10+', 'braces!'),
     ('$#', 'how many', 'checks'),
     ('"$@"', 'all, separately', 'loops, forwarding'),
     ('shift', 'drop $1', 'option loops'),
     ('${1:-default}', 'optional argument', 'defaults'),
     ('${1:?msg}', 'required argument', 'stop if missing')],
    dict(setup=SI, cmd="cd ~/si\n./args.sh report.txt 'Q3 sales'", note='$2 is “Q3 sales” (one argument, quoted); $# is 2.'),
    [('sys', [
        dict(situation='A backup tool with a folder and a number of days.', setup=SI, cmd="cd ~/si; cat > backup.sh <<'EOF'\n#!/bin/bash\ndir=${1:?usage: backup.sh FOLDER [DAYS]}\ndays=${2:-7}\necho \"backing up $dir, keeping $days days\"\nEOF\nbash backup.sh /etc 30; bash backup.sh /var/www; bash backup.sh; echo \"status $?\"", expect='any',
             why='Required first argument (${1:?}), optional second with a default (${2:-7}).')]),
     ('dev', [
        dict(situation='$10 needs braces; shift moves everything down.', cmd="set -- a b c d e f g h i j k\necho \"\\$10=$10  \\${10}=${10}  count=$#\"\nshift 3; echo \"after shift 3: \\$1=$1 count=$#\"", why='$10 is read as $1 followed by 0. shift is the classic way to walk through options.')]),
     ('qa', [
        dict(situation='Count check with a usage message.', cmd="cat > add.sh <<'EOF'\n#!/bin/bash\nif [ $# -ne 2 ]; then echo \"usage: $(basename \"$0\") A B\" >&2; exit 2; fi\necho \"$1 + $2 = $(( $1 + $2 ))\"\nEOF\nbash add.sh 12 30; bash add.sh 5; echo \"status $?\"", expect='any',
             why='Exit status 2 by convention means “wrong usage”; the message goes to stderr.')]),
    ],
    anat=anatomy([('./backup.sh', 'cmd', '$0'), ('/etc', 'arg', '$1'), ('30', 'arg', '$2')], '$# = 2 here.')
) + mistake('echo "Tenth: $10"', 'echo "Tenth: ${10}"', 'Without braces only one digit is read: $1 then the text 0.') + cmdcard_u(['confirmations, menus, passwords', 'reading a file line by line'],
               ['scripts that run unattended (cron, CI): nobody answers'])(
    'read', 'read -r -p -s -t -n -a', 'ask the user',
    '<code>read VAR</code> reads one line from stdin. <code>-p "text"</code> shows a prompt, <code>-s</code> hides typing, <code>-t N</code> gives up after N seconds, <code>-n N</code> returns after N characters, <code>-a ARR</code> stores words in an array, <code>-r</code> keeps backslashes. With several names, the last one gets the rest of the line.',
    "read -r -p 'Prompt: ' VAR   ·   read -r a b rest   ·   while read -r line; do …; done &lt; file", 'safe',
    [('-p TEXT', 'prompt', 'questions'),
     ('-s', 'silent (no echo)', 'passwords'),
     ('-t 10', 'timeout 10 s', 'default answers'),
     ('-n 1', 'one key', 'y/n'),
     ('-a arr', 'words → array', 'lists'),
     ('-r', 'raw backslashes', 'always'),
     ('IFS=, read', 'split at commas', 'CSV'),
     ('-d ""', 'until NUL', 'find -print0')],
    dict(cmd="printf 'Riya\\nPune\\n' | { read -r -p 'Name: ' name; read -r -p 'City: ' city; echo \"$name lives in $city\"; }", note='The prompt goes to the terminal only, so the recorded output shows the answer line. In a real terminal you see “Name: ” and type.'),
    [('dev', [
        dict(situation='Several variables: the last one gets the rest.', cmd="read -r first second rest <<< 'one two three four five'\necho \"[$first] [$second] [$rest]\"", why='Words are split at IFS; extra words all go to the last variable.')]),
     ('data', [
        dict(situation='Read a CSV file line by line.', setup=SI, cmd="cd ~/si\nwhile IFS=, read -r name city salary; do\n  echo \"$name ($city) earns $salary\"\ndone < staff.csv", why='IFS=, splits at commas; < staff.csv feeds the loop. Lesson 12.9 covers loops.')]),
     ('sec', [
        dict(situation='Without -r backslashes vanish.', cmd="read v <<< 'C:\\Users\\riya'; echo \"no -r: $v\"\nread -r w <<< 'C:\\Users\\riya'; echo \"with -r: $w\"", why='Always use -r unless you want backslash escapes interpreted.')]),
    ]
) + mistake('ls | read first; echo "$first"', 'read -r first < <(ls)   or   first=$(ls | head -1)',
            'Each part of a pipe runs in a subshell, so the variable set by read disappears when the pipe ends.') + cmdcard_u(['counters, sizes, percentages, dates as numbers', 'loops and conditions'],
               ['decimal values (use bc or awk)', 'numbers with leading zeros (08, 09 are invalid octal)'])(
    'arith', '$(( )) · (( )) · let', 'whole-number maths',
    '<code>$(( expr ))</code> is replaced by the result. Inside, variables need no <code>$</code>; operators: <code>+ - * / % **</code>, comparisons, <code>&amp;&amp; ||</code>, <code>++ --</code>, <code>+= -=</code>, <code>? :</code>. <code>(( ))</code> without $ is a command (status 0 if non-zero). <code>let</code> is an older form.',
    'x=$(( a + b ))   ·   (( count++ ))   ·   (( a > b )) && echo bigger', 'safe',
    [('+ - * /', 'basic', '/ truncates'),
     ('%', 'remainder', 'even/odd'),
     ('**', 'power', '2**10'),
     ('++ -- += -=', 'change in place', 'counters'),
     ('a > b, a == b', 'compare (1/0)', 'conditions'),
     ('c ? x : y', 'pick a value', 'short if'),
     ('16#ff, 8#17', 'other bases', 'hex, octal'),
     ('10#08', 'force decimal', 'dates')],
    dict(cmd="a=17; b=5\necho \"sum $((a + b))  diff $((a - b))  prod $((a * b))\"\necho \"div $((a / b))  rem $((a % b))  pow $((2 ** 10))\"\n((a++)); echo \"a is now $a\"", note='17/5 is 3: the decimal part is dropped, not rounded.'),
    [('sys', [
        dict(situation='KB to GB, and a percentage.', cmd="kb=7340032; total=10485760\necho \"used: $(( kb / 1024 / 1024 )) GB\"\necho \"percent: $(( kb * 100 / total ))%\"", why='Multiply before dividing to keep precision in integer maths.')]),
     ('dev', [
        dict(situation='Leading zeros are octal.', cmd="month=08\necho $(( month + 1 )) 2>&1 | sed 's/.*: //'\necho $(( 10#$month + 1 ))", expect='any',
             why='08 is not valid octal: error. 10# forces base 10. Watch for this with dates (date +%m gives 08, 09).')]),
     ('qa', [
        dict(situation='(( )) as a condition.', cmd="disk=91\nif (( disk > 90 )); then echo \"ALERT: disk $disk%\"; fi\n(( disk > 95 )) || echo 'not critical yet'", why='(( )) returns status 0 when true: no [ ] needed for numbers.')]),
    ]
) + cmdcard_u(['old scripts and strict POSIX sh', 'string length, substring and position (expr string functions)'],
               ['new bash scripts (use $(( )) and ${#var})', 'set -e scripts (expr exits 1 when the result is 0)'])(
    'expr', 'expr', 'the old calculator',
    '<code>expr</code> evaluates its arguments: every number and operator must be a <b>separate word</b>, and <code>*</code>, <code>(</code>, <code>)</code>, <code>&lt;</code>, <code>&gt;</code> must be escaped. It also has string functions: <code>length</code>, <code>substr</code>, <code>index</code>, <code>match</code>. It prints the result and exits 1 if the result is 0 or empty.',
    'expr A + B   ·   expr A \\* B   ·   expr length "$s"   ·   expr substr "$s" POS LEN', 'safe',
    [('expr 5 + 3', 'add (spaces!)', 'POSIX'),
     ('expr 5 \\* 3', 'multiply (escape *)', 'POSIX'),
     ('expr 7 / 2', 'integer divide', '3'),
     ('expr 7 % 2', 'remainder', '1'),
     ('expr length "$s"', 'string length', 'old scripts'),
     ('expr substr "$s" 2 3', 'substring', 'old scripts'),
     ('expr index "$s" c', 'first position of c', 'old scripts'),
     ('x=$(expr $x + 1)', 'counter', 'sh scripts')],
    dict(cmd="a=12; b=4\nexpr $a + $b\nexpr $a \\* $b\nexpr $a / $b\nexpr length 'CDAC Mumbai'\nexpr substr 'CDAC Mumbai' 6 6", note='Each result printed by expr itself; capture it with $( ).'),
    [('qa', [
        dict(situation='The three classic expr mistakes.', setup="rm -rf ~/ex; mkdir -p ~/ex; touch ~/ex/a1.png", cmd="cd ~/ex\nexpr 5+3\nexpr 5 * 3 2>&1\nexpr 5 \\* 3", expect='any',
             why='No spaces: expr just prints the text 5+3. Unescaped *: the shell turned it into file names (here a1.png): syntax error. With \\*: 15.')]),
     ('devops', [
        dict(situation='expr exits 1 when the result is 0.', cmd="expr 5 - 5; echo \"status $?\"\nbash -c 'set -e; n=$(expr 5 - 5); echo never'; echo \"script status $?\"", expect='any',
             why='Under set -e, a zero result stops the script. Another reason to prefer $(( )).')]),
    ]
) + mistake('avg=$(expr ($a + $b) / 2)', 'avg=$(( (a + b) / 2 ))   or   avg=$(expr \\( $a + $b \\) / 2)',
            'Unescaped ( ) are shell syntax: “syntax error near unexpected token”. In expr, brackets must be escaped and separated by spaces.') + cmdcard_u(['money, averages, percentages with decimals', 'big numbers'],
               ['tight loops (it starts a new process each time)'])(
    'bc', 'bc · awk', 'decimals',
    '<code>bc</code> is a calculator: send it an expression on stdin. <code>scale=N</code> sets digits after the point (truncated, not rounded); <code>-l</code> loads the maths library (scale 20, sqrt, s, c, l, e). <code>awk \'BEGIN{printf …}\'</code> is a handy alternative with printf rounding.',
    "echo 'scale=2; 7/2' | bc   ·   bc -l <<< 'sqrt(2)'   ·   awk 'BEGIN{printf \"%.2f\\n\", 7/3}'", 'safe',
    [('scale=2', '2 decimals (truncated)', 'money'),
     ('bc -l', 'maths library', 'sqrt, decimals'),
     ('<<< "expr"', 'here-string input', 'short'),
     ('x=$(bc <<< …)', 'into a variable', 'scripts'),
     ("printf '%.2f'", 'round when printing', 'reports'),
     ('awk BEGIN{…}', 'quick decimal maths', 'pipelines')],
    dict(cmd="echo 'scale=2; 7/2' | bc\nbc -l <<< 'sqrt(2)'\nm1=70; m2=71; m3=71\necho \"integer: $(( (m1+m2+m3)/3 ))   bc: $(bc <<< \"scale=2; ($m1+$m2+$m3)/3\")\"", note='The puzzle: integer maths gives 70, bc gives 70.66 (truncated). awk below rounds to 70.67.'),
    [('data', [
        dict(situation='Round instead of truncate.', cmd="awk 'BEGIN { printf \"%.2f\\n\", (70+71+71)/3 }'\nprintf '%.2f\\n' \"$(bc -l <<< '(70+71+71)/3')\"", why='printf rounds; bc’s scale truncates. For money, round when printing.')]),
     ('dba', [
        dict(situation='GST on a price.', cmd="price=1499; gst=18\ntotal=$(bc <<< \"scale=2; $price * (100 + $gst) / 100\")\necho \"₹$total incl. $gst% GST\"", why='bc keeps decimals all the way; $(( )) would lose the paise.')]),
    ]
) + undo('Input and maths do not change files; the risk is wrong numbers.', [
    ('Wrong argument used:', 'print them first: <code>printf \'[%s]\\n\' "$@"</code>.'),
    ('read waits forever in a script:', 'add <code>-t SECONDS</code>, or give the answer through a pipe / here-string.'),
    ('Integer result where decimals were needed:', 'use bc or awk; or multiply first (cents, percent × 100).'),
    ('expr error:', 'check spaces and <code>\\*</code>; better switch to <code>$(( ))</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='echo $(( 5 / 0 ))', meaning='Division by zero.', fix='Check the divisor first: <code>(( d != 0 ))</code>.'),
    dict(cmd='expr 5 + x', meaning='expr needs integers.', fix='Validate input: <code>[[ $x =~ ^[0-9]+$ ]]</code> (12.8).'),
    dict(cmd='echo $(( 09 + 1 ))', meaning='A leading 0 means octal; 9 is not an octal digit.', fix='<code>$(( 10#09 + 1 ))</code>.'),
    dict(cmd="bash -c 'echo ${1:?need a file name}'", meaning='Required argument missing.', fix='Pass it: <code>bash -c \'…\' _ file.txt</code>.'),
]) + qc('How do you read a password without showing it?', "<code>read -rs -p 'Password: ' pw; echo</code> (the echo prints the missing newline).") + '''
'''
cards = cards + '</section>\n'

def argv(k):
    words = ['./args.sh', 'report.txt', 'Q3 sales', '7'] if k < 3 else ['./args.sh', 'Q3 sales', '7']
    labels = ['$0', '$1', '$2', '$3']
    o = ''
    for i, w in enumerate(words):
        tn = 'violet' if i == 0 else ('green' if k >= 1 else 'card')
        if k == 3 and i == 0: tn = 'violet'
        o += label_box(14 + i * 86, 26, 80, 44, [w, labels[i] if k >= 1 else ''], tn, 7.8)
    if k >= 2:
        o += label_box(14, 84, 332, 28, [f'$# = {len(words) - 1}   "$@" = ' + ' | '.join(words[1:])], 'amber', 8)
    if k == 3:
        o += label_box(14, 120, 332, 28, ['after shift: report.txt is gone, everything moved down'], 'red', 7.8)
    return o
see_cmds = [["$ ./args.sh report.txt 'Q3 sales' 7"], ["$ ./args.sh report.txt 'Q3 sales' 7", ('first  : report.txt', 'out'), ('second : Q3 sales', 'out')], ["$ ./args.sh report.txt 'Q3 sales' 7", ('count  : 3', 'out')], ['(inside: shift)', ('first  : Q3 sales', 'acc'), ('count  : 2', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/si', prompt='riya@web01:~/si$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['You type a line.', 'Words become $1, $2…', '$# counts them.', 'shift moves them down.'])]
behind = [argv(k) + t(180, 175, n, 8.4, 'violet', bold=True) for k, n in enumerate(['The shell splits the line into words.', 'Word 0 is $0; the rest are numbered.', 'Quotes kept “Q3 sales” as one word.', 'shift dropped $1.'])]
two = anim_two('Arguments and shift', 'Behind the screen: from a command line to $1 $2',
               "A terminal: args.sh is run with report.txt, 'Q3 sales' and 7; it prints first, second and count; after shift the first is Q3 sales.",
               'Word boxes labelled $0 to $3; $# is 3; after shift every argument moves one place left and $# is 2.', see, behind,
               ['Line.', 'Numbered.', 'Counted.', 'Shifted.'],
               ['split', '$0 $1 $2 $3', '$# = 3', 'shift'])

def ar(k):
    rows = [('$(( 7 / 2 ))', '3', 'blue'), ("bc: scale=2; 7/2", '3.50', 'green'), ('expr 7 / 2', '3', 'amber'), ('expr 7 * 2 (no \\)', 'error: * → file names', 'red')]
    o = ''
    for i, (a, b, tn) in enumerate(rows[:k + 1]):
        o += label_box(14, 16 + i * 40, 170, 32, [a], tn, 7.8) + arrow(184, 32 + i * 40, 206, 32 + i * 40) + label_box(206, 16 + i * 40, 144, 32, [b], 'card', 7.8)
    return o
frames = [ar(0) + t(180, 190, 'Integers only: the .5 is dropped.', 8.6, 'blue', bold=True),
          ar(1) + t(180, 190, 'bc keeps decimals (scale).', 8.6, 'green', bold=True),
          ar(2) + t(180, 190, 'expr: same integer result, external program.', 8.6, 'amber', bold=True),
          ar(3) + t(180, 190, 'expr needs \\* because the shell sees * first.', 8.6, 'red', bold=True)]
s1 = anim_one('Animated example', 'Four ways to divide and multiply',
              'Same numbers, different tools, different results.',
              'arithmetic', '7 divided by 2 with $(( )), bc and expr, and expr multiplication failing without a backslash.', frames,
              ['$(( )).', 'bc.', 'expr.', 'The * trap.'], hid='scenario-arith')

dx = dissect('Layer by layer: where script input comes from',
    'Each layer has a real command and output from our build machine.', [
    dict(key='argv', name='argv', sub='the command line', why='Input at start.', how='execve() array.', impl='/proc/PID/cmdline.', used='$0 $1 …',
         cmd="sleep 30 & tr '\\0' ' ' < /proc/$!/cmdline; echo; kill $!"),
    dict(key='stdin', name='stdin', sub='for read', why='Input during the run.', how='File descriptor 0.', impl='Terminal, pipe or file.', used='read.',
         cmd="echo 'from a pipe' | { read -r x; echo \"read got: $x\"; }; read -r y <<< 'from a here-string'; echo \"$y\""),
    dict(key='ifs', name='IFS', sub='word splitting', why='How read splits.', how='Characters list.', impl='Default space tab newline.', used='CSV.',
         cmd="IFS=: read -r u x uid rest <<< 'riya:x:1000:1000::/home/riya:/bin/bash'; echo \"$u $uid\""),
    dict(key='int', name='Integers', sub='64-bit', why='Fast maths.', how='Built into bash.', impl='Signed 64-bit, wraps.', used='$(( )).',
         cmd="echo $(( 2**62 )) $(( 2**63 )) $(( 2**63 - 1 ))"),
], hint='From the command line and keyboard to numbers. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Arguments and shift, and four ways to calculate</h2>
''' + two + s1 + dx + qc('Why can a 64-bit integer show a negative number for 2**63?', 'It overflows: the largest value is 2**63 − 1; one more wraps to the most negative number. bash does not warn.') + '''
</section>
'''

VAR = variations('Twelve more scripts that each change one thing, so you see arguments, read and arithmetic from every side. All were really run on our build machine.', [
    ('Arguments', [
        dict(title='Print every argument with its number', cmd="cat > list.sh <<'EOF'\nn=1\nfor a in \"$@\"; do echo \"arg $n: $a\"; n=$((n + 1)); done\necho \"total: $#\"\nEOF\nbash list.sh alpha 'beta gamma' 42", why='"$@" in a loop; a counter with $(( )).'),
        dict(title='Required and optional arguments together', cmd="cat > greet.sh <<'EOF'\nname=${1:?usage: greet.sh NAME [GREETING]}\ngreeting=${2:-Namaste}\necho \"$greeting, $name!\"\nEOF\nbash greet.sh Riya; bash greet.sh Aman 'Good morning'", why='${1:?} stops without a name; ${2:-} gives a default.'),
        dict(title='Last argument and all but the first', cmd="set -- copy a.txt b.txt c.txt /backup\necho \"action: $1\"\necho \"last: ${!#}\"\necho \"files: ${@:2:$#-2}\"", why='${!#} is the last argument; ${@:2:N} slices the list.'),
        dict(title='Simple option handling with shift', cmd="cat > opts.sh <<'EOF'\nverbose=0\nwhile [ $# -gt 0 ]; do\n  case $1 in -v) verbose=1;; -o) out=$2; shift;; *) file=$1;; esac\n  shift\ndone\necho \"verbose=$verbose out=${out:-none} file=${file:-none}\"\nEOF\nbash opts.sh -v -o report.txt data.csv", why='The classic loop: look at $1, consume it with shift. getopts does this formally.'),
    ]),
    ('read', [
        dict(title='Yes/no confirmation with a default', cmd="ask(){ read -r -p 'Delete old logs? [y/N] ' a; [ \"${a:-n}\" = y ] && echo deleting || echo 'skipped'; }\nask <<< 'y'; ask <<< ''", why='An empty answer takes the default (N).'),
        dict(title='Timeout with a default answer', cmd="if read -r -t 1 -p 'Environment [dev]: ' env < <(sleep 2); then :; else env=dev; echo \"(no answer in 1 s, using $env)\"; fi", why='-t returns a non-zero status on timeout; then use the default.'),
        dict(title='Read words into an array', cmd="read -r -a cities <<< 'Pune Delhi Mumbai Chennai'\necho \"${#cities[@]} cities, second is ${cities[1]}, last is ${cities[-1]}\"", why='-a stores each word as an array element (index from 0).'),
        dict(title='Sum a column from a file', setup=SI, cmd="cd ~/si; total=0\nwhile IFS=, read -r name city sal; do total=$(( total + sal )); done < staff.csv\necho \"payroll: $total\"", why='read + $(( )) in a loop: a tiny report without awk.'),
    ]),
    ('Arithmetic', [
        dict(title='Even or odd, and a ternary', cmd="for n in 7 12; do echo \"$n is $(( n % 2 == 0 ? 1 : 0 ))\" | sed 's/is 1/is even/; s/is 0/is odd/'; done", why='% gives the remainder; ? : picks a value.'),
        dict(title='Seconds to h:m:s', cmd="s=7384\nprintf '%02d:%02d:%02d\\n' $(( s / 3600 )) $(( s % 3600 / 60 )) $(( s % 60 ))", why='Integer division and remainder are perfect for units.'),
        dict(title='Compound assignment', cmd="x=10; (( x += 5 )); (( x *= 2 )); (( x -= 6 )); echo \"$x\"\nlet 'y = x / 4'; echo \"$y\"", why='+= *= -= work inside (( )); let does the same.'),
        dict(title='Hex, octal and binary', cmd="echo $(( 16#ff )) $(( 8#755 )) $(( 2#1010 ))\nprintf '%x %o\\n' 255 493", why='BASE#number reads any base; printf %x %o writes hex and octal (permissions!).'),
        dict(title='Percentage with one decimal', cmd="used=37; total=128\necho \"integer: $(( used * 100 / total ))%\"\necho \"bc:      $(bc <<< \"scale=1; $used * 100 / $total\")%\"", why='Same formula; bc keeps the decimal.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Script input at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['./job.sh', 'DATE ENV'], 'blue', 8.6), '1. Scheduled jobs',
              'Cron and Airflow call scripts with arguments (date, environment, folder) instead of editing the script.', ['Schedule', '*$1 $2', 'run']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['read -p', 'runbooks'], 'green', 8.6), '2. Operator scripts',
    'Risky maintenance scripts ask for a ticket number and a “yes” before deleting or restarting.', ['Ask', '*read', 'confirm']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['$(( ))', 'monitoring'], 'amber', 8.6), '3. Monitoring checks',
    'Checks compute percentages and thresholds (disk, memory, queue size) with integer maths.', ['Measure', '*$(( ))', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['bc', 'billing'], 'violet', 8.6), '4. Reports with money',
    'Billing and sales summaries use bc or awk so paise are not lost.', ['Sum', '*bc', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['while read', 'CSV'], 'red', 8.6), '5. Data loading',
    'Small ETL steps read CSV lines, validate fields and load them, one line at a time.', ['File', '*read -r', 'load']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Add two numbers', scenario='Quick maths.', cmd="echo $(( 125 + 375 ))", explain='$(( )).'),
    dict(level='b', title='How many arguments?', scenario='Check input.', cmd="set -- a b c; echo $#", explain='$#.'),
    dict(level='i', title='Average with decimals', scenario='Marks.', cmd="echo 'scale=2; (85+90+92)/3' | bc", explain='bc.'),
    dict(level='i', title='String length three ways', scenario='Validate input.', cmd="s='CDAC Mumbai'; echo ${#s}; expr length \"$s\"; printf %s \"$s\" | wc -c", explain='${#s} is fastest.'),
    dict(level='a', title='Read and sum numbers from stdin', scenario='A quick adder.', cmd="printf '10\\n20\\n30\\n' | { t=0; while read -r n; do t=$((t + n)); done; echo \"sum $t\"; }", explain='The { } keeps t inside the same subshell as the loop.'),
], extra=build_up('a salary calculator', 'Riya builds a script that takes a salary as an argument and asks for a bonus percentage.', SI, [
    ("cd ~/si; printf '#!/bin/bash\\nsal=${1:?usage: pay.sh SALARY}\\n' > pay.sh; bash pay.sh 2>&1 | sed 's/.*: //'", '1. Require the salary argument.'),
    ("cd ~/si; printf 'read -r -p \"Bonus %%: \" b\\n' >> pay.sh; printf 'bonus=$(( sal * b / 100 ))\\n' >> pay.sh; tail -2 pay.sh", '2. Ask for the bonus and compute it.'),
    ("cd ~/si; printf 'echo \"salary $sal + bonus $bonus = $(( sal + bonus ))\"\\n' >> pay.sh; bash pay.sh 85000 <<< 12", '3. Print the total (answer 12 given through <<<).'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Input at start', '$1 $2 / "$@"', 'Works in cron.', 'Hard-coding values.'),
    ('Check input exists', '${1:?msg} / $#', 'Fails early.', 'Using an empty $1.'),
    ('Ask a person', 'read -r -p', 'Interactive.', 'read in cron jobs.'),
    ('Whole numbers', '$(( ))', 'Built in.', 'expr in new scripts.'),
    ('Decimals', 'bc / awk', 'Exact.', '$(( )) (truncates).'),
    ('Tenth argument', '${10}', 'Braces.', '$10.'),
]) + keys('Handy forms.', [
    ('${1:-default}', 'optional arg', 'defaults'),
    ('${!#}', 'last argument', 'targets'),
    ("read -rsp 'Pw: ' p", 'hidden input', 'passwords'),
    ('read -r -t 5', 'timeout', 'defaults'),
    ('(( x > 5 ))', 'numeric test', 'if'),
    ("bc <<< 'scale=2; a/b'", 'decimals', 'money'),
]) + scriptit('calc.sh', 'A tiny calculator from the syllabus topics: two numbers and an operator as arguments, input checked, integer and decimal results.',
'''[ $# -eq 0 ] && set -- 7 / 2      # demo values when run without arguments
[ $# -eq 3 ] || { echo "usage: calc.sh A OP B   (OP: + - x /)" >&2; exit 2; }
a=$1; op=$2; b=$3
case $op in
  +) r=$(( a + b ));; -) r=$(( a - b ));; x) r=$(( a * b ));;
  /) [ "$b" -ne 0 ] || { echo "cannot divide by zero" >&2; exit 1; }; r=$(bc <<< "scale=2; $a / $b");;
  *) echo "unknown operator: $op" >&2; exit 2;;
esac
echo "$a $op $b = $r"''',
'<p>Run without arguments, so it uses the demo values <code>7 / 2</code> (x is used for multiply so the shell does not expand *). case is explained in Lesson 12.8.</p>', expect='any') + puzzle_answer('$(( )) does <b>integer</b> arithmetic, so (85+90+92)/3 = 267/3 = 89 exactly, and (70+71+71)/3 = 212/3 = 70 with the .67 dropped. The expr version fails because <code>(</code> and <code>)</code> are shell syntax: they must be escaped (<code>\\( … \\)</code>) and separated by spaces. For 70.67: <code>bc &lt;&lt;&lt; "scale=2; (70+71+71)/3"</code> gives 70.66 (truncated); <code>awk \'BEGIN{printf "%.2f\\n", 212/3}\'</code> gives 70.67 (rounded).') + qc('What does <code>read a b &lt;&lt;&lt; "one two three"</code> put in b?', '“two three”: the last variable gets the rest of the line.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/si ~/ex', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../05-your-first-shell-script/">Lesson 12.5</a> (writing and running scripts) and <a href="../04-quoting-and-expansion-single-vs-double-quotes/">12.4</a> ("$@").') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
