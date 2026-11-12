import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

LP = r"""rm -rf ~/lp; mkdir -p ~/lp/logs ~/lp/in; cd ~/lp
printf 'GET /a 200\nGET /b 500\n' > logs/mon.log; printf 'GET /c 200\n' > logs/tue.log; printf 'GET /d 404\nGET /e 500\nGET /f 500\n' > logs/wed.log
printf 'riya,Pune,85000\naman,Delhi,72000\nneha,Mumbai,91000\n' > staff.csv
touch 'in/Q3 report.txt' in/a.txt in/b.csv
printf 'web01\nweb02\ndb01\n' > hosts.txt"""

HOOK = hook('Riya has 365 daily log files and must count the errors in each. A colleague needs every user in a CSV created on the server. A download must be retried until it succeeds, but not more than five times. A menu must keep asking until the operator chooses “exit”. All of these are <b>loops</b>: <code>for</code> walks through a list (words, files, numbers, array items), <code>while</code> repeats as long as a command succeeds, <code>until</code> repeats until it succeeds, and <code>break</code> / <code>continue</code> leave or skip early. With <code>select</code> you get a numbered menu for free, and <code>getopts</code> loops over options like <code>-v -o file</code>.',
    ['write for loops over lists, ranges ({1..10}, seq), files (globs), command output and arrays, plus the C-style for ((i=0; i<n; i++))',
     'write while and until loops with counters and conditions, and read files or command output line by line safely',
     'control loops with break, continue, break N / continue N, and build menus with select and while true',
     'parse options with getopts, and avoid the classic traps: missing ; before do, pipes that lose variables, last lines without a newline, looping over ls'])
ROAD = roadmap([
    ('story', 'The story', 3, '365 log files'),
    ('decide', 'Which loop when?', 2, 'the quick chart'),
    ('definition', 'Loops', 5, 'simple meaning + 4 depths'),
    ('types', 'for vs while vs until', 5, 'side by side'),
    ('commands', 'Loops by field', 16, 'real runs'),
    ('animation', 'See it happen', 4, 'a loop step by step'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a log report'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which loop? (decide in 5 seconds)', [
    ('Every item of a known list', 'for x in a b c; do …; done', 'for'),
    ('Every file matching a pattern', 'for f in *.log; do …; done', 'never $(ls)'),
    ('Numbers 1 to N', 'for i in {1..10}  /  for ((i=1;i<=n;i++))', 'ranges'),
    ('Every line of a file', 'while IFS= read -r line; do …; done < file', 'not for'),
    ('As long as something is true', 'while COND; do …; done', 'counters, polling'),
    ('Until something becomes true', 'until COND; do …; done', 'retries'),
    ('Stop early / skip one', 'break  /  continue', 'inside any loop'),
    ('Numbered menu', 'select x in a b c; do …; done', 'interactive'),
])

cmap = concept_map(
    [('12.8', 'if and test', 'conditions'), ('12.7', 'Arguments', '"$@" and read'), ('3.4', 'Globs and braces', '*.log, {1..10}')],
    ['for in lists, ranges, globs, arrays, $( )', 'C-style for (( ))', 'while and until, counters', 'while read: files and output line by line', 'break, continue, select, getopts'],
    [('12.10', 'Functions', 'loops inside functions'), ('12.13', 'Arrays', 'loop over items'), ('13.2', 'find + xargs', 'loops at scale'), ('17.4', 'cron', 'run the loop daily')],
    'for walks a list, while repeats while a command succeeds, until repeats until it succeeds. break and continue change the flow.')

sc = (term(20, 14, 316, 156, ['$ for f in logs/*.log; do', '>   echo "$f: $(grep -c 500 "$f")"', '> done', ('logs/mon.log: 1', 'out'), ('logs/tue.log: 0', 'out'), ('logs/wed.log: 2', 'out'), '$ until ping -c1 db01; do sleep 5; done', ('(retries until db01 answers)', 'acc')], title='riya@web01: ~/lp', prompt='riya@web01:~/lp$', size=6.8, step=15)
      + t(352, 36, 'Repeat for…', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• each file: for', '• each line: while read', '• while true: while', '• until it works: until', '• stop: break'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>365 log files</h2>
  <div class="story">
''' + puzzle('Riya counts error lines with <code>count=0; grep 500 app.log | while read -r line; do count=$((count+1)); done; echo "$count errors"</code>. The log has 3 errors; the script prints “0 errors”. The loop runs three times (an echo inside proves it). Where did the count go, and how do you fix it in two different ways?') + '''
    <p class="narration">Three days of logs, one loop, one line per file.</p>
''' + scene('A terminal: a for loop over logs/*.log prints the number of 500 errors in each file; an until loop retries a ping.', sc,
            'Write the work once; the loop does it <tspan font-weight="700" class="s-acc">for every item</tspan>.') + '''
K> Could I not just copy the command 365 times?
A> You could, and you would make a mistake in one of them. A loop writes the work once and applies it to every item: files, lines, users, numbers. The body is between <code>do</code> and <code>done</code>; the variable takes each value in turn.
R> And the puzzle?
A> It is about <b>where</b> the loop runs: a pipe puts it in a child shell. Today you will see each kind of loop, how to stop and skip, menus, option parsing, and the traps that make loops lose data.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A conveyor belt: for takes each box from a known pile; while keeps the belt running while the switch is on; until runs it until a light turns green; break stops the belt, continue skips one box.">'
       + label_box(14, 20, 190, 110, ['for = a known pile', 'take each box', 'in turn, then stop', 'files, users, 1..10'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['while / until', 'keep going while', 'the switch is ON /', 'until the light is GREEN'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['break / continue', 'break: stop belt', 'continue: skip', 'this box only'], 'amber', 8.6)
       + t(320, 160, 'do … done = the work done for each box.', 9.6, 'ink2')
       + t(320, 182, 'A loop must be able to end: change something each time.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Loops at four depths', [
    ('v', 'No jargon: a conveyor belt', '      <p>Three ways to keep the belt moving, two ways to interrupt it.</p>' + pic),
    ('b', 'The shapes you will type', '''      <ul>
        <li><code>for city in Pune Delhi Mumbai; do echo "$city"; done</code></li>
        <li><code>for f in *.txt; do wc -l "$f"; done</code></li>
        <li><code>n=1; while [ $n -le 5 ]; do echo $n; n=$((n+1)); done</code></li>
        <li><code>until ping -c1 server; do sleep 5; done</code></li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li><code>do</code> is a separate word: on the next line, or after <code>;</code> on the same line: <code>for x in a b; do</code>.</li>
        <li><code>for x in LIST</code>: LIST is expanded once at the start (words, <code>{1..5}</code>, <code>*.log</code>, <code>"$@"</code>, <code>"${arr[@]}"</code>, <code>$(cmd)</code>). Without <code>in LIST</code>, it loops over <code>"$@"</code>.</li>
        <li><code>while CMD</code> runs the body while CMD returns 0; <code>until CMD</code> while it returns non-zero. Something in the body must change the condition.</li>
        <li><code>break</code> leaves the loop, <code>continue</code> jumps to the next round; <code>break 2</code> / <code>continue 2</code> act on the outer loop of two nested ones.</li>
        <li>To read lines use <code>while IFS= read -r line; do …; done &lt; file</code>, not <code>for line in $(cat file)</code> (that splits at every space).</li>
      </ul>'''),
    ('a', 'Behind the screen: subshells and expansion', '''      <ul>
        <li>Every part of a pipe runs in its own subshell, so <code>cmd | while read …</code> changes variables in a child that disappears (unless <code>shopt -s lastpipe</code> in a script). Use <code>done &lt; file</code> or <code>done &lt; &lt;(cmd)</code>.</li>
        <li><code>{1..N}</code> is brace expansion: N must be a literal number, not a variable (<code>{1..$n}</code> does not work); use <code>seq 1 "$n"</code> or <code>for ((i=1;i&lt;=n;i++))</code>.</li>
        <li>A glob that matches nothing stays literal (<code>*.log</code>), so loops over globs should check <code>[ -e "$f" ] || continue</code> or use <code>shopt -s nullglob</code>.</li>
        <li><code>read</code> returns non-zero at end of file even if it read a last line without a newline: use <code>while read -r l || [ -n "$l" ]</code>.</li>
        <li>A loop’s exit status is that of the last body command run; redirections after <code>done</code> apply to the whole loop (one open, faster than <code>&gt;&gt;</code> inside).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>for, while, until, break and continue</h2>
''' + def_block(
    'A <b>for</b> loop runs its body once for each word of a list, assigning the word to a variable (bash also has an arithmetic form <code>for ((init; test; step))</code>). A <b>while</b> loop runs its body as long as a command list returns 0; an <b>until</b> loop runs it as long as the list returns non-zero. <b>break</b> exits the loop and <b>continue</b> starts the next iteration. <b>select</b> shows a numbered menu, and <b>getopts</b> parses command-line options one at a time.',
    'for = each item. while = as long as. until = until. break = stop. continue = skip.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Iteration', 'One round of the loop.'),
    ('Loop variable', 'Takes each value in turn.'),
    ('Body', 'The commands between do and done.'),
    ('Counter', 'A number changed every round.'),
    ('Infinite loop', 'while true; needs a break.'),
    ('Nested loop', 'A loop inside a loop.'),
    ('select', 'A numbered menu loop.'),
    ('getopts', 'Parses -a -b value options.'),
]) + '\n' + names('Where the names come from.', [
    ('for', 'for each', 'Algol, 1958.'),
    ('do / done', 'start / end of body', 'Bourne shell.'),
    ('while', 'while true', 'Repeat while.'),
    ('until', 'until true', 'Opposite of while.'),
    ('break', 'break out', 'Leave the loop.'),
    ('continue', 'continue with next', 'Skip the rest.'),
    ('select', 'select from a menu', 'ksh, then bash.'),
    ('getopts', 'get options', 'POSIX.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('List', '<code>for x in a b c</code>'),
    ('Range', '<code>for i in {1..10}</code>'),
    ('C-style', '<code>for ((i=0;i&lt;5;i++))</code>'),
    ('Lines', '<code>while read -r l; do …; done &lt; f</code>'),
    ('Retry', '<code>until cmd; do sleep 5; done</code>'),
    ('Leave / skip', '<code>break</code> / <code>continue</code>'),
]) + '\n' + lv + didyou('<code>while true; do …; done</code> is how many Linux services and monitoring scripts are built: an endless loop with a <code>sleep</code> inside, stopped by a signal or a <code>break</code> (Lesson 11.3).') + '''
EXAM> “Write a script that prints the multiplication table of a number.” → <code>for i in {1..10}; do echo "$n x $i = $((n * i))"; done</code>.
''' + qc('How many times does <code>for x in "a b" c; do echo $x; done</code> run?', 'Twice: "a b" (one quoted word) and c.') + mistake('for var in ${list}  do   (do on the same line, no ;)',
    'for var in $list; do   …   or put do on the next line',
    'do is a separate command word: without ; it is just another list item, and bash later fails with “syntax error near unexpected token”. Checked (class-notes for-loop syntax).') + mistake('while [[ $counter -le 10 ]]; do echo $counter  ((counter++))  done',
    'echo "$counter"; ((counter++))   (separate commands: new line or ;)',
    'On one line without ;, ((counter++)) becomes part of echo’s arguments: “syntax error near unexpected token (”. Checked (class-notes while-loop example).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>for vs while vs until, and what to loop over</h2>
''' + table(['', 'for', 'while', 'until'], [
    ['Repeats', 'once per list item', 'while command is true (0)', 'while command is false'],
    ['Knows the count in advance', 'yes', 'no', 'no'],
    ['Typical use', 'files, users, numbers', 'counters, reading lines, polling', 'retries, waiting for a service'],
    ['Stops by itself', 'after the last item', 'when the condition fails', 'when the condition succeeds'],
    ['Infinite form', '—', '<code>while true</code>', '<code>until false</code>'],
], minw=560) + table(['Loop over…', 'Write', 'Avoid'], [
    ['words', '<code>for c in Pune Delhi</code>', '—'],
    ['a range', '<code>{1..10}</code>, <code>{0..100..5}</code>, <code>seq 1 "$n"</code>', '<code>{1..$n}</code> (no variables)'],
    ['files', '<code>for f in *.log</code>', '<code>for f in $(ls)</code>'],
    ['lines of a file', '<code>while IFS= read -r l; do …; done &lt; f</code>', '<code>for l in $(cat f)</code>'],
    ['command output lines', '<code>done &lt; &lt;(cmd)</code>', '<code>cmd | while …</code> (if you need variables after)'],
    ['arguments', '<code>for a in "$@"</code> (or just <code>for a</code>)', '<code>for a in $*</code>'],
    ['array items', '<code>for x in "${arr[@]}"</code>', '<code>${arr[*]}</code> unquoted'],
], minw=520) + table(['Control', 'Effect'], [
    ['<code>break</code>', 'leave the loop now'],
    ['<code>continue</code>', 'skip to the next round'],
    ['<code>break 2</code> / <code>continue 2</code>', 'act on the outer of two loops'],
    ['<code>exit</code>', 'leave the whole script'],
    ['<code>done &gt; file</code>', 'redirect all output of the loop once'],
], minw=360) + qc('Why is <code>for f in $(ls)</code> a bad way to loop over files?', 'Names with spaces are split into several words, and ls output is meant for people. for f in * gives each name intact.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Loops explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/lp</code>: three daily logs <code>logs/mon.log</code> (one 500), <code>tue.log</code> (none) and <code>wed.log</code> (two), <code>staff.csv</code>, <code>hosts.txt</code> and a folder <code>in/</code> with a file name containing a space.</p>
''' + cmdcard_u(['every file, user, host, number or argument in a known list'],
               ['lines of a file (use while read)', 'output of ls'])(
    'for', 'for … in … ; do … ; done', 'each item',
    '<code>for VAR in LIST; do CMDS; done</code>. LIST can be words, brace ranges, globs, <code>"$@"</code>, <code>"${array[@]}"</code> or <code>$(command)</code>. The variable keeps the last value after the loop.',
    'for x in LIST; do …; done   ·   for ((i=0; i<N; i++)); do …; done', 'safe',
    [('in a b c', 'fixed words', 'small lists'),
     ('in {1..10}', 'range', 'numbers'),
     ('in {0..20..5}', 'range with step', '0 5 10 …'),
     ('in *.log', 'files (glob)', 'files'),
     ('in "$@"', 'script arguments', 'tools'),
     ('in "${arr[@]}"', 'array items', 'lists'),
     ('in $(seq 1 "$n")', 'range from a variable', 'dynamic'),
     ('((i=0;i<n;i++))', 'C-style', 'counters')],
    dict(setup=LP, cmd="cd ~/lp\nfor f in logs/*.log; do\n  echo \"$f: $(grep -c ' 500$' \"$f\") errors\"\ndone", note='The story, for real: one line of work, applied to every log.'),
    [('dev', [
        dict(situation='Ranges: brace, step, seq and C-style.', cmd="for i in {1..5}; do printf '%s ' $i; done; echo\nfor i in {0..20..5}; do printf '%s ' $i; done; echo\nn=4; for i in $(seq 1 \"$n\"); do printf '%s ' $i; done; echo\nfor ((i=10; i>0; i-=3)); do printf '%s ' $i; done; echo", why='{1..$n} would NOT work with a variable; seq or (( )) do.')]),
     ('sys', [
        dict(situation='Files with spaces: glob, not ls.', setup=LP, cmd="cd ~/lp/in\nfor f in $(ls); do echo \"ls gave: [$f]\"; done\nfor f in *; do echo \"glob gave: [$f]\"; done", why='$(ls) splits “Q3 report.txt” into two words; the glob keeps names intact.')]),
     ('devops', [
        dict(situation='Run the same check on several hosts.', setup=LP, cmd="cd ~/lp\nfor h in $(cat hosts.txt); do\n  if [ \"$h\" = db01 ]; then echo \"$h: skipped (database)\"; continue; fi\n  echo \"$h: would run: ssh $h uptime\"\ndone", why='Host names have no spaces, so $(cat) is acceptable here; continue skips one host.')]),
    ],
    anat=anatomy([('for', 'cmd', 'keyword'), ('f', 'arg', 'loop variable'), ('in logs/*.log', 'arg', 'the list'), ('; do … ; done', 'opt', 'the body')], 'do and done are separate words.')
) + mistake('for line in $(cat staff.csv)', 'while IFS= read -r line; do …; done < staff.csv',
            'for splits the file at every space and tab, not at line ends, and expands * in the text. while read reads exactly one line per round.') + cmdcard_u(['counters and conditions', 'reading files and command output line by line', 'polling until something changes'],
               ['cmd | while read when you need the variables afterwards'])(
    'while', 'while … do … done · while read', 'as long as',
    '<code>while CMD; do …; done</code> repeats while CMD returns 0. The most important use: <code>while IFS= read -r line; do …; done &lt; FILE</code> reads a file one line at a time; <code>IFS=,</code> splits CSV fields; <code>&lt; &lt;(cmd)</code> reads command output without losing variables.',
    'while COND; do …; done   ·   while IFS= read -r l; do …; done < file', 'safe',
    [('while [ $i -le 5 ]', 'counter', 'repeat N'),
     ('while true', 'forever (use break)', 'menus, daemons'),
     ('while read -r l', 'line by line', 'files'),
     ('IFS=, read -r a b c', 'fields', 'CSV'),
     ('done < file', 'feed a file', 'input'),
     ('done < <(cmd)', 'feed output, keep vars', 'counters'),
     ('|| [ -n "$l" ]', 'last line without \\n', 'robust')],
    dict(setup=LP, cmd="cd ~/lp\nwhile IFS=, read -r name city salary; do\n  echo \"$name works in $city and earns $salary\"\ndone < staff.csv", note='One round per line; IFS=, splits the fields.'),
    [('data', [
        dict(situation='The puzzle: a pipe loses the count.', setup=LP, cmd="cd ~/lp; cat logs/*.log > all.log\ncount=0; grep ' 500$' all.log | while read -r l; do count=$((count+1)); done; echo \"pipe: $count\"\ncount=0; while read -r l; do count=$((count+1)); done < <(grep ' 500$' all.log); echo \"process substitution: $count\"", why='The pipe ran the loop in a child shell. Feeding it with < <(…) keeps it in this shell.')]),
     ('sys', [
        dict(situation='Counter loop with a condition.', cmd="i=1\nwhile [ \"$i\" -le 5 ]; do\n  echo \"attempt $i\"\n  i=$((i + 1))\ndone", why='Forget the i=$((i+1)) and the loop never ends.')]),
     ('qa', [
        dict(situation='A last line without a newline.', cmd="printf 'line1\\nline2' > nonl.txt\nwhile read -r l; do echo \"plain: $l\"; done < nonl.txt\nwhile read -r l || [ -n \"$l\" ]; do echo \"robust: $l\"; done < nonl.txt", why='Files written by Windows tools or Excel often lack the final newline; the robust form still reads it.')]),
    ]
) + cmdcard_u(['retrying until something works', 'waiting for a service or a file'],
               ['retries without a limit (add a counter)'])(
    'until', 'until … do … done', 'until it works',
    '<code>until CMD; do …; done</code> repeats while CMD fails and stops as soon as it succeeds. Pair it with a counter and <code>sleep</code> to retry a few times.',
    'until CMD; do sleep N; done   ·   until CMD || (( tries >= 5 )); do …; done', 'safe',
    [('until test', 'until true', 'opposite of while'),
     ('sleep 5', 'pause between tries', 'polling'),
     ('counter', 'give up after N', 'safety'),
     ('until false', 'forever', 'rare')],
    dict(setup=LP, cmd="cd ~/lp; rm -f ready.flag\n( sleep 2; touch ready.flag ) &\ntries=0\nuntil [ -f ready.flag ]; do tries=$((tries + 1)); echo \"waiting… ($tries)\"; sleep 1; done\necho \"ready after $tries checks\"", note='A background job creates the file after 2 s; until stops as soon as it exists.'),
    [('devops', [
        dict(situation='Retry with a limit.', cmd="attempt=0\nuntil false; do\n  attempt=$((attempt + 1)); echo \"try $attempt failed\"\n  [ $attempt -ge 3 ] && { echo 'giving up after 3 tries'; break; }\ndone", why='In real life replace false by the command (curl, ping, mysqladmin ping) and add sleep.')]),
    ]
) + cmdcard_u(['leaving early when you found what you need', 'skipping items you do not want'],
               ['deep nesting where a function with return is clearer'])(
    'break', 'break · continue · break N', 'change the flow',
    '<code>break</code> leaves the innermost loop immediately; <code>continue</code> skips the rest of the body and starts the next round. With a number they act on outer loops: <code>break 2</code> leaves two levels, <code>continue 2</code> continues the outer loop.',
    'break [N]   ·   continue [N]', 'safe',
    [('break', 'leave loop', 'found it'),
     ('continue', 'next round', 'skip item'),
     ('break 2', 'leave 2 levels', 'nested search'),
     ('continue 2', 'next outer round', 'nested skip')],
    dict(cmd="for i in 1 2 3 4 5 6; do\n  [ $i -eq 2 ] && continue\n  [ $i -eq 5 ] && break\n  echo \"i=$i\"\ndone", note='2 is skipped, the loop stops at 5: prints 1, 3, 4.'),
    [('data', [
        dict(situation='Nested loops: continue 2 and break 2.', cmd="for team in A B; do\n  for p in 1 2 3; do\n    [ $p -eq 2 ] && continue 2\n    echo \"$team$p\"\n  done\ndone\nfor r in 1 2; do for c in 1 2 3; do [ $c -eq 2 ] && break 2; echo \"r$r c$c\"; done; done", why='continue 2 skipped to the next team; break 2 left both loops at once.')]),
     ('sec', [
        dict(situation='Stop at the first match.', setup=LP, cmd="cd ~/lp\nfor f in logs/*.log; do\n  if grep -q ' 404$' \"$f\"; then echo \"first 404 found in $f\"; break; fi\ndone", why='No need to scan the rest once you know the answer.')]),
    ]
) + cmdcard_u(['simple interactive menus', 'scripts with -v -o FILE style options'],
               ['menus in unattended scripts', 'long options like --verbose (getopts only does short ones)'])(
    'menu', 'select · while true + case · getopts', 'menus and options',
    '<code>select x in A B C; do …; done</code> prints a numbered menu (prompt <code>PS3</code>), reads a number into <code>$REPLY</code> and sets x to the item. <code>while true; do … case … break; done</code> is the hand-made menu. <code>getopts "vo:" opt</code> reads options one by one; a colon means the option takes a value in <code>$OPTARG</code>.',
    'select x in LIST; do …; done   ·   while getopts "ab:" opt; do case $opt in …; esac; done', 'safe',
    [('select', 'numbered menu', 'interactive'),
     ('PS3', 'select prompt', 'nicer text'),
     ('$REPLY', 'number typed', 'validation'),
     ('getopts "vo:"', 'options -v and -o VALUE', 'tools'),
     ('$OPTARG', 'option value', '-o file'),
     ('shift $((OPTIND-1))', 'drop parsed options', 'then files'),
     ('?)', 'unknown option', 'usage')],
    dict(cmd="printf '2\\n' | { PS3='Choose an action: '; select a in start stop status; do echo \"you chose $a (number $REPLY)\"; break; done; } 2>&1", note='select writes the menu and prompt to stderr; here the answer 2 comes through a pipe.'),
    [('sys', [
        dict(situation='Hand-made menu with while true and case (as in the class notes).', cmd="printf '3\\n9\\n4\\n' | while true; do\n  read -r -p 'Choice [1-4]: ' c || break\n  case $c in\n    1) date +%F ;; 2) ls | head -2 ;; 3) echo \"user: $USER\" ;;\n    4) echo 'Goodbye!'; break ;;\n    *) echo \"invalid option: $c\" ;;\n  esac\ndone", why='The loop keeps asking until 4 (break). || break also stops at end of input.')]),
     ('dev', [
        dict(situation='getopts: options with and without values.', cmd="parse(){ local OPTIND opt v=0 out=-\n  while getopts 'vo:' opt; do case $opt in v) v=1;; o) out=$OPTARG;; ?) echo 'usage: [-v] [-o FILE] FILE…'; return 2;; esac; done\n  shift $((OPTIND - 1)); echo \"verbose=$v output=$out files=$*\"; }\nparse -v -o report.txt a.log b.log\nparse -x 2>&1", expect='any', why='getopts prints its own “illegal option” message and returns ?; shift removes the parsed options so $@ holds the files.')]),
    ]
) + undo('Loops repeat mistakes as fast as they repeat work; test first.', [
    ('Endless loop:', 'press <kbd>Ctrl</kbd>+<kbd>C</kbd>; check that the condition can change.'),
    ('Loop changed many files wrongly:', 'restore from backup; next time put <code>echo</code> before the real command and check the list first.'),
    ('Variables empty after the loop:', 'the loop ran in a pipe: use <code>done &lt; file</code> or <code>&lt; &lt;(cmd)</code>.'),
    ('Loop ran once with “*.log”:', 'no file matched: add <code>[ -e "$f" ] || continue</code> or <code>shopt -s nullglob</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="bash -c 'for x in a b do echo $x; done'", meaning='Missing ; before do.', fix='<code>for x in a b; do</code>.'),
    dict(cmd="bash -c 'while true; do break'", meaning='Missing done.', fix='Every do needs a done.'),
    dict(cmd='n=3; for i in {1..$n}; do echo $i; done', meaning='Brace ranges do not take variables: one round with the text {1..3}.', fix='<code>seq 1 "$n"</code> or <code>for ((i=1;i&lt;=n;i++))</code>.'),
    dict(cmd='break', meaning='break outside a loop does nothing useful.', fix='Only inside for/while/until/select.'),
]) + qc('What does <code>for i in {1..$n}</code> print with n=3?', 'The text {1..3} once: brace expansion happens before variables are filled in.') + '''
'''
cards = cards + '</section>\n'

def it(k):
    files = ['mon.log', 'tue.log', 'wed.log']
    counts = ['1', '0', '2']
    o = ''
    for i, f in enumerate(files):
        tn = 'green' if i < k else ('amber' if i == k else 'card')
        o += label_box(14 + i * 112, 30, 104, 44, [f, f'errors: {counts[i]}' if i < k else ''], tn, 8)
    if k == 3:
        o += label_box(14, 90, 328, 30, ['list finished → done → next command'], 'violet', 8)
    return o
see_cmds = [['$ for f in logs/*.log; do …'], ['$ for f in logs/*.log; do …', ('logs/mon.log: 1', 'out')], ['$ for f in logs/*.log; do …', ('logs/mon.log: 1', 'out'), ('logs/tue.log: 0', 'out')], ['$ for f in logs/*.log; do …', ('logs/mon.log: 1', 'out'), ('logs/tue.log: 0', 'out'), ('logs/wed.log: 2', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/lp', prompt='riya@web01:~/lp$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['The glob becomes 3 names.', 'Round 1.', 'Round 2.', 'Round 3: done.'])]
behind = [it(k) + t(180, 150, n, 8.4, 'violet', bold=True) for k, n in enumerate(['f = mon.log: run the body.', 'f = tue.log.', 'f = wed.log.', 'No items left: the loop ends.'])]
two = anim_two('A for loop step by step', 'Behind the screen: one round per item',
               'A terminal: the for loop prints the error count for each of three logs.',
               'Three file boxes are processed one after another; after the last, the loop ends.', see, behind,
               ['Start.', 'Round 1.', 'Round 2.', 'Round 3.'],
               ['expand list', 'f=mon.log', 'f=tue.log', 'done'])

def wl(k):
    o = label_box(14, 18, 150, 36, ['main shell', f'count = 0'], 'blue', 8)
    if k >= 1:
        o += label_box(196, 18, 150, 36, ['pipe: child shell', 'count = 3' if k >= 2 else 'count = 0'], 'amber', 8)
    if k >= 2:
        o += label_box(196, 64, 150, 30, ['child exits: lost'], 'red', 8)
    if k == 3:
        o = label_box(14, 18, 332, 36, ['done < <(grep …): loop in the main shell, count = 3'], 'green', 8)
    return o
frames = [wl(0) + t(180, 160, 'count=0 in the script.', 8.6, 'violet', bold=True),
          wl(1) + t(180, 160, 'grep … | while: the loop is a child.', 8.6, 'amber', bold=True),
          wl(2) + t(180, 160, 'The child counts 3, then exits.', 8.6, 'red', bold=True),
          wl(3) + t(180, 160, 'Process substitution keeps it here.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'Why a piped loop forgets its variables',
              'The puzzle, drawn.',
              'pipe subshell', 'The main shell has count 0; the piped while loop runs in a child that counts to 3 and exits; with done < <(…) the loop runs in the main shell.', frames,
              ['Start.', 'Pipe.', 'Lost.', 'Fix.'], hid='scenario-pipe')

dx = dissect('Layer by layer: what a loop really iterates over',
    'Each layer has a real command and output from our build machine.', [
    dict(key='list', name='The list', sub='expanded once', why='Decides the rounds.', how='Expansion first.', impl='Words.', used='for.',
         setup=LP, cmd="cd ~/lp; set -- logs/*.log; echo \"$# items: $*\""),
    dict(key='brace', name='Brace ranges', sub='{1..N}', why='Quick numbers.', how='Before variables.', impl='Literal only.', used='Counters.',
         cmd="n=3; echo {1..3}; echo {1..$n}; echo $(seq 1 $n)"),
    dict(key='status', name='Condition status', sub='while/until', why='When to stop.', how='0 or not.', impl='Any command.', used='Polling.',
         cmd="i=0; while (( i < 3 )); do ((i++)); done; echo \"i=$i, (( i < 3 )) now returns: $( (( i < 3 )); echo $? )\""),
    dict(key='sub', name='Subshells', sub='pipes', why='Where it runs.', how='fork per pipe part.', impl='$BASHPID differs.', used='The puzzle.',
         cmd="echo \"main $BASHPID\"; echo x | while read -r l; do echo \"loop in $BASHPID\"; done | sed 's/[0-9]\\+/N/'"),
], hint='From the list to where the loop runs. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A loop step by step, and the pipe trap</h2>
''' + two + s1 + dx + qc('A loop writes 1000 lines with <code>echo … &gt;&gt; out.txt</code> inside. What is faster?', 'Redirect once after done: done > out.txt. The file is opened once instead of 1000 times.') + '''
</section>
'''

VAR = variations('Eighteen more loops, each a variation of the examples above. All were really run on our build machine.', [
    ('for variations', [
        dict(title='Multiplication table', cmd="n=7; for i in {1..10}; do echo \"$n x $i = $((n * i))\"; done | head -4", why='The classic exam program (first 4 lines shown).'),
        dict(title='Sum of 1 to 100', cmd="sum=0; for ((i=1; i<=100; i++)); do sum=$((sum + i)); done; echo \"sum: $sum\"", why='C-style for with an accumulator.'),
        dict(title='Factorial', cmd="n=6; f=1; for ((i=2; i<=n; i++)); do f=$((f * i)); done; echo \"$n! = $f\"", why='Multiply instead of add.'),
        dict(title='Even numbers only', cmd="for i in {2..20..2}; do printf '%s ' $i; done; echo", why='A step of 2 in the brace range.'),
        dict(title='Reverse countdown', cmd="for i in $(seq 5 -1 1); do printf '%s… ' $i; done; echo 'go!'", why='seq with a negative step.'),
        dict(title='Rename all .txt to .bak (dry run)', setup=LP, cmd="cd ~/lp/in; for f in *.txt; do echo mv -- \"$f\" \"${f%.txt}.bak\"; done", why='${f%.txt} removes the extension (12.14); echo first = a safe dry run.'),
        dict(title='Loop over arguments without in', cmd="show(){ for a; do echo \"<$a>\"; done; }; show one 'two words' three", why='for a with no list means for a in "$@".'),
    ]),
    ('while and until variations', [
        dict(title='Sum the digits of a number', cmd="n=4721; s=0; while (( n > 0 )); do s=$((s + n % 10)); n=$((n / 10)); done; echo \"digit sum: $s\"", why='% 10 takes the last digit, / 10 removes it.'),
        dict(title='Reverse a number', cmd="n=12345; r=0; while (( n > 0 )); do r=$((r * 10 + n % 10)); n=$((n / 10)); done; echo \"$r\"", why='Another classic exam program.'),
        dict(title='Fibonacci series', cmd="a=0; b=1; for i in {1..10}; do printf '%s ' $a; t=$((a + b)); a=$b; b=$t; done; echo", why='Two variables shifted each round.'),
        dict(title='Prime check', cmd="for n in 17 21; do p=1; for ((d=2; d*d<=n; d++)); do (( n % d == 0 )) && { p=0; break; }; done; (( p )) && echo \"$n is prime\" || echo \"$n is not prime\"; done", why='break as soon as a divisor is found.'),
        dict(title='Read a file with line numbers', setup=LP, cmd="cd ~/lp; n=0; while IFS= read -r l; do n=$((n + 1)); printf '%2d: %s\\n' $n \"$l\"; done < hosts.txt", why='Same as cat -n, but you can add logic per line.'),
        dict(title='Total salary from CSV', setup=LP, cmd="cd ~/lp; t=0; while IFS=, read -r name city sal; do t=$((t + sal)); done < staff.csv; echo \"total: $t\"", why='Fields with IFS=, and an accumulator.'),
        dict(title='Wait for a process to finish', cmd="sleep 2 & pid=$!; secs=0\nwhile kill -0 $pid 2>/dev/null; do secs=$((secs + 1)); sleep 1; done; echo \"process ended after ~$secs s\"", why='kill -0 only checks that the process exists (Lesson 11.3).'),
    ]),
    ('break, continue, menus and options', [
        dict(title='Skip comments and blank lines', cmd="printf '# config\\nport=80\\n\\nhost=web01\\n' > c.conf\nwhile IFS= read -r l; do [[ -z $l || $l == \\#* ]] && continue; echo \"setting: $l\"; done < c.conf", why='continue skips lines you do not want.'),
        dict(title='Find the first free file name', cmd="touch report1.txt report2.txt; i=1; while [ -e \"report$i.txt\" ]; do i=$((i + 1)); done; echo \"next free: report$i.txt\"", why='Loop until a name does not exist.'),
        dict(title='select with validation', cmd="printf '9\\n1\\n' | { PS3='Pick: '; select o in yes no; do [ -n \"$o\" ] && { echo \"picked $o\"; break; }; echo \"$REPLY is not on the menu\"; done; } 2>/dev/null", why='An invalid number leaves o empty; the loop asks again.'),
        dict(title='getopts with a required value', cmd="opts(){ local OPTIND o n=1; while getopts 'n:' o; do [ $o = n ] && n=$OPTARG; done; echo \"n=$n\"; }; opts -n 5; opts", why='Default when the option is not given.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Loops at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['for f in', '*.log'], 'blue', 8.6), '1. Log processing',
              'Daily reports loop over log files, count errors and append a summary line per file.', ['Logs', '*for', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['while read', 'CSV'], 'green', 8.6), '2. Bulk user creation',
    'Admins read a CSV of new joiners and run useradd for each line (Lesson 8.2).', ['CSV', '*while read', 'users']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['until', 'retries'], 'amber', 8.6), '3. Deployments',
    'Deploy scripts wait until the database answers or the health check passes, with a retry limit.', ['Start', '*until', 'healthy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['for h in', 'hosts'], 'violet', 8.6), '4. Fleet tasks',
    'Run the same command over a list of servers (before tools like Ansible take over).', ['Hosts', '*for + ssh', 'done']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['while true', 'monitors'], 'red', 8.6), '5. Simple monitors',
    'A while true loop with sleep checks disk or a URL every minute and alerts on change.', ['Check', '*sleep', 'alert']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Count lines of every file', scenario='Quick sizes.', setup=LP, cmd="cd ~/lp; for f in logs/*.log; do echo \"$(wc -l < \"$f\") $f\"; done", explain='for over a glob.'),
    dict(level='b', title='1 to 5 in one line', scenario='Quick range.', cmd="for i in {1..5}; do printf '%s ' $i; done; echo", explain='{1..5}.'),
    dict(level='i', title='Create 5 users (dry run)', scenario='Bulk accounts.', cmd="for u in dev{1..5}; do echo sudo useradd -m \"$u\"; done", explain='Brace expansion builds the names.'),
    dict(level='i', title='Lines longer than 15 chars', scenario='Filter while reading.', setup=LP, cmd="cd ~/lp; while IFS= read -r l; do (( ${#l} > 15 )) && echo \"$l\"; done < staff.csv", explain='${#l} = length.'),
    dict(level='a', title='Parallel-ish with wait', scenario='Run three jobs at once.', cmd="for s in 1 2 3; do (sleep $s; echo \"job $s done\") & done; wait; echo 'all done'", explain='& starts each in the background; wait waits for all.'),
], extra=build_up('a log report', 'Riya builds a report that loops over the logs and totals the errors.', LP, [
    ("cd ~/lp; for f in logs/*.log; do echo \"$f\"; done", '1. Loop over the files.'),
    ("cd ~/lp; for f in logs/*.log; do n=$(grep -c ' 500$' \"$f\"); echo \"$(basename \"$f\" .log): $n\"; done", '2. Count errors per file.'),
    ("cd ~/lp; total=0; for f in logs/*.log; do n=$(grep -c ' 500$' \"$f\"); total=$((total + n)); done; echo \"total errors: $total\"", '3. Add a total.'),
    ("cd ~/lp; for f in logs/*.log; do n=$(grep -c ' 500$' \"$f\"); (( n == 0 )) && continue; echo \"$(basename \"$f\" .log) $n\"; done > errors.txt; cat errors.txt", '4. Skip clean days, write a file once.'),
], expect='any')) + VAR + which('Choosing the right loop.', [
    ('Known list / files', 'for', 'Simple, safe with globs.', 'for f in $(ls).'),
    ('Numbers 1..N with a variable', 'for ((i=1;i<=n;i++))', 'Works with $n.', '{1..$n}.'),
    ('Lines of a file', 'while IFS= read -r', 'One line per round.', 'for l in $(cat f).'),
    ('Output, keep variables', 'done < <(cmd)', 'Same shell.', 'cmd | while.'),
    ('Retry', 'until … with a counter', 'Stops on success.', 'Endless retries.'),
    ('Menu', 'select / while true + case', 'Interactive.', 'Menus in cron jobs.'),
]) + keys('Handy forms.', [
    ('for f in *.log; do …; done', 'every file', 'files'),
    ('for ((i=0;i<n;i++))', 'counter', 'numbers'),
    ('while IFS=, read -r a b', 'CSV fields', 'data'),
    ('done < <(cmd)', 'keep variables', 'counts'),
    ('break 2 / continue 2', 'outer loop', 'nested'),
    ('done > out.txt', 'one redirect', 'speed'),
]) + scriptit('bulk-check.sh', 'A loop-heavy tool: for every host in a file, retry a check up to 3 times (until), skip comment lines (continue), and stop everything if a STOP file appears (break). The “check” is simulated so it runs anywhere.',
'''hosts=${1:-$HOME/lp/hosts.txt}
check(){ [ "$1" != db01 ]; }        # simulated: db01 always fails
while IFS= read -r h; do
  [[ -z $h || $h == \\#* ]] && continue
  [ -e "$HOME/lp/STOP" ] && { echo "STOP file found, ending"; break; }
  tries=0
  until check "$h"; do
    tries=$((tries + 1)); [ $tries -ge 3 ] && break
  done
  if [ $tries -ge 3 ]; then echo "$h: FAILED after 3 tries"; else echo "$h: ok"; fi
done < "$hosts"''',
'<p>Run on the sample hosts.txt (web01, web02, db01).</p>', expect='any') + puzzle_answer('Because of the pipe, the <code>while</code> loop runs in a <b>child shell</b>: it counts to 3 there, and the child exits at the end of the pipe, so the main shell still has count=0. Fix 1: feed the loop without a pipe, <code>while …; done &lt; &lt;(grep 500 app.log)</code>. Fix 2: do not loop at all, <code>count=$(grep -c 500 app.log)</code>. (In a script, <code>shopt -s lastpipe</code> also works.)') + qc('How do you make a loop that asks a menu question until the user chooses Exit?', 'while true; do read -r -p … c; case $c in …) …;; exit) break;; esac; done (or select … with break).') + '''
</section>
'''

_sh.run_sh('rm -rf ~/lp', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../08-decisions-if-test-and-case/">Lesson 12.8</a> (if, test and case) and <a href="../07-script-input-positional-parameters-read-and-arithmetic/">12.7</a> (read and $(( ))).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
