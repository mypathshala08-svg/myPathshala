import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

DC = r"""rm -rf ~/dc; mkdir -p ~/dc/logs ~/dc/backup; cd ~/dc
printf 'port=8080\n' > app.conf; : > empty.txt; printf '#!/bin/bash\necho hi\n' > run.sh; chmod +x run.sh
ln -s app.conf link.conf; printf 'GET / 200\nGET /x 500\n' > logs/web.log"""

HOOK = hook('A script that never decides anything is just a list. Real scripts check: <b>does</b> the backup folder exist, <b>is</b> the disk more than 90% full, <b>did</b> the user type a number, <b>which</b> action did they ask for (start, stop, status)? Bash decides with <code>if</code> (one or two paths, <code>elif</code> for more), with <code>case</code> (many choices by pattern), and with tests written as <code>[ … ]</code>, <code>test …</code>, <code>[[ … ]]</code> or <code>(( … ))</code>. The trickiest part is not the syntax but the details: spaces inside brackets, quotes around variables, and using the right operator for numbers (<code>-gt</code>) versus strings (<code>&gt;</code>).',
    ['write if-then-fi, if-else, elif chains and nested ifs, and know that if tests an <b>exit status</b>',
     'use the test command and its three families: file tests (-e -f -d -r -w -x -s -L -nt), string tests (= != -z -n) and number tests (-eq -ne -lt -le -gt -ge)',
     'choose between <code>[ ]</code>, <code>[[ ]]</code> and <code>(( ))</code>; use &&, ||, ! and pattern / regex matching with =~',
     'write case statements with several patterns, wildcards and a default, and avoid the classic bracket, quoting and case-sensitivity mistakes'])
ROAD = roadmap([
    ('story', 'The story', 3, 'a backup that checks first'),
    ('decide', 'Which test when?', 2, 'the quick chart'),
    ('definition', 'Decisions', 5, 'simple meaning + 4 depths'),
    ('types', '[ ] vs [[ ]] vs (( )); test families', 6, 'side by side'),
    ('commands', 'By field', 16, 'real runs'),
    ('animation', 'See it happen', 4, 'if reads $?'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a service control script'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which test? (decide in 5 seconds)', [
    ('Does a file / folder exist?', '[ -f "$f" ]   [ -d "$d" ]', 'file tests'),
    ('Is a string empty?', '[ -z "$s" ]   (not empty: -n)', 'quote it'),
    ('Are two strings equal?', '[ "$a" = "$b" ]', 'one = is POSIX'),
    ('Compare numbers', '[ "$n" -gt 10 ]   or   (( n > 10 ))', 'not > inside [ ]'),
    ('Pattern / wildcard match', '[[ $f == *.log ]]', 'bash'),
    ('Regex match', '[[ $x =~ ^[0-9]+$ ]]', 'bash'),
    ('Many choices on one value', 'case "$x" in a|b) … ;; *) … ;; esac', 'menus, actions'),
    ('Did the command work?', 'if grep -q x f; then …', 'if tests the exit status'),
])

cmap = concept_map(
    [('5.4', 'Exit status', '$? and &&'), ('12.7', 'Script input', '$1 and read'), ('9.1', 'Permissions', '-r -w -x')],
    ['if, then, elif, else, fi; nested if', 'test and [ ]: file, string, number tests', '[[ ]]: patterns, =~ regex, && ||', '(( )) for numbers', 'case … in … esac'],
    [('12.9', 'Loops', 'while and until use the same tests'), ('12.10', 'Functions', 'return a status'), ('12.14', 'Strings', 'patterns and case'), ('18.4', 'Troubleshooting', 'check scripts')],
    'if runs a command and looks at its exit status: 0 = true. [ ], [[ ]] and (( )) are just commands that return 0 or 1.')

sc = (term(20, 14, 316, 156, ['$ ./backup.sh /srv/data', ('ERROR: /srv/data does not exist', 'err'), '$ ./backup.sh ~/dc', ('disk 47% used: ok', 'out'), ('backup written', 'acc'), '$ ./svc.sh restart', ('restarting app…', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Scripts that decide:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• if [ -d ]: exists?', '• (( )): numbers', '• [[ =~ ]]: input ok?', '• case: which action', '• else: plan B'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A backup that checks first</h2>
  <div class="story">
''' + puzzle('Riya’s check reads <code>if [ $count &gt; 10 ]; then echo "too many"; fi</code>. With count=5 it prints “too many”, and afterwards there is a new file called <code>10</code> in her folder. With count=50 it also prints “too many”. What did the shell actually do, and what are two correct ways to write it?') + '''
    <p class="narration">Riya’s backup script learns to look before it leaps.</p>
''' + scene('A terminal: backup.sh refuses a missing folder, checks the disk, and a service script handles a restart action.', sc,
            'if, test and case turn a list of commands into a <tspan font-weight="700" class="s-acc">program that decides</tspan>.') + '''
K> Is <code>[</code> part of the if syntax?
A> No, and that is the key idea. <code>if</code> runs <b>any command</b> and looks at its exit status: 0 means true. <code>[</code> is just a command (another name for <code>test</code>) that returns 0 or 1. That is why it needs spaces around it, like any command, and why <code>if grep -q error log</code> works without brackets.
R> And the puzzle?
A> Inside <code>[ ]</code>, <code>&gt;</code> is still a redirection. Today you will learn the right operators for files, strings and numbers, the safer <code>[[ ]]</code>, arithmetic <code>(( ))</code>, and case for menus.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A railway junction: the test is a signal (green = exit status 0, red = non-zero); if sends the train left or right; case is a junction with many tracks chosen by the train’s label.">'
       + label_box(14, 20, 190, 110, ['the test = a signal', '[ -f file ]', 'green: status 0', 'red: status 1'], 'green', 8.6)
       + label_box(224, 20, 190, 110, ['if = two tracks', 'then: green track', 'else: red track', 'elif: another signal'], 'blue', 8.6)
       + label_box(434, 20, 192, 110, ['case = a junction', 'start) → track 1', 'stop) → track 2', '*) → default'], 'amber', 8.6)
       + t(320, 160, 'if never looks at text, only at the exit status.', 9.6, 'ink2')
       + t(320, 182, '0 = true, anything else = false.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Decisions at four depths', [
    ('v', 'No jargon: signals and junctions', '      <p>The test is a signal; if and case choose the track.</p>' + pic),
    ('b', 'The shapes you will type', '''      <ul>
        <li><code>if [ -f report.txt ]; then echo found; fi</code></li>
        <li><code>if [ "$n" -gt 10 ]; then …; else …; fi</code></li>
        <li><code>if …; then …; elif …; then …; else …; fi</code></li>
        <li><code>case "$1" in start) … ;; stop) … ;; *) echo usage ;; esac</code></li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li><code>[</code> needs spaces: <code>[ "$a" = "$b" ]</code>, never <code>["$a"="$b"]</code>. The last argument must be <code>]</code>.</li>
        <li>Strings: <code>=</code>, <code>!=</code>, <code>-z</code>, <code>-n</code>. Numbers: <code>-eq -ne -lt -le -gt -ge</code>. Inside <code>[ ]</code>, <code>&gt;</code> and <code>&lt;</code> are redirections unless escaped (and then they compare text, not numbers).</li>
        <li>Quote variables inside <code>[ ]</code>: an empty unquoted variable disappears and breaks the test.</li>
        <li><code>[[ ]]</code> (bash): no word splitting, <code>==</code> with patterns (<code>*.log</code>), <code>=~</code> regex, <code>&amp;&amp;</code> and <code>||</code> inside. <code>(( ))</code>: arithmetic with &gt; &lt; ==.</li>
        <li>case compares one value against glob patterns (<code>*</code> <code>?</code> <code>[ ]</code> <code>|</code>), top to bottom, and runs only the first match; <code>;;</code> ends a branch.</li>
      </ul>'''),
    ('a', 'Behind the screen: commands and statuses', '''      <ul>
        <li><code>[</code> and <code>test</code> are shell builtins (there is also a /usr/bin/[ program); <code>[[</code> is a <b>keyword</b>, parsed before expansion, which is why it can treat <code>&amp;&amp;</code>, <code>&lt;</code> and unquoted variables safely.</li>
        <li><code>if</code> takes a whole list: <code>if cd /x &amp;&amp; ls; then</code> uses the status of the last command.</li>
        <li><code>-a</code> / <code>-o</code> inside <code>[ ]</code> are obsolete and ambiguous; use <code>[ … ] &amp;&amp; [ … ]</code> or <code>[[ … &amp;&amp; … ]]</code>.</li>
        <li><code>=~</code> uses POSIX extended regex; quote nothing on the right (quoted parts become literal); captures go to <code>BASH_REMATCH</code>.</li>
        <li>case terminators: <code>;;</code> stop, <code>;&amp;</code> run the next branch too, <code>;;&amp;</code> test the next patterns too (bash 4).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>if, test and case</h2>
''' + def_block(
    '<code>if</code> runs a command list and executes the <code>then</code> part when its exit status is 0, otherwise the <code>elif</code>/<code>else</code> parts. <code>test</code> (also written <code>[ … ]</code>) evaluates file, string and integer expressions and returns 0 (true) or 1 (false); bash adds <code>[[ … ]]</code> with pattern and regex matching and <code>(( … ))</code> for arithmetic. <code>case</code> compares a word against patterns and runs the commands of the first matching pattern.',
    'if = do this if the command succeeded. test = a command that answers yes (0) or no (1). case = pick a branch by pattern.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Condition', 'A command whose exit status decides.'),
    ('test / [ ]', 'Evaluates an expression, returns 0 or 1.'),
    ('[[ ]]', 'bash test: patterns, regex, safer.'),
    ('(( ))', 'Arithmetic test.'),
    ('elif', 'else if: another condition.'),
    ('Nested if', 'An if inside another if.'),
    ('case / esac', 'Choose by pattern.'),
    ('Pattern', 'Glob: * ? [ ] and |.'),
]) + '\n' + names('Where the names come from.', [
    ('fi', 'if backwards', 'Algol 68 tradition.'),
    ('esac', 'case backwards', 'Same idea.'),
    ('[', 'test', 'Another name for test.'),
    ('-eq -lt -gt', 'equal, less than, greater than', 'Fortran style.'),
    ('-z / -n', 'zero / non-zero length', 'Strings.'),
    ('-nt / -ot', 'newer / older than', 'Files.'),
    ('=~', 'matches regex', 'From Perl.'),
    (';;', 'end of a branch', 'case only.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('File exists', '<code>[ -e f ]</code>'),
    ('Empty string', '<code>[ -z "$s" ]</code>'),
    ('Numbers', '<code>[ "$a" -lt "$b" ]</code>'),
    ('Pattern', '<code>[[ $f == *.csv ]]</code>'),
    ('Regex', '<code>[[ $x =~ ^[0-9]+$ ]]</code>'),
    ('Status test', '<code>if grep -q x f</code>'),
]) + '\n' + lv + didyou('<code>true</code> and <code>false</code> are tiny commands that only return 0 and 1. That is why <code>while true; do … done</code> loops forever and <code>if false; then</code> never runs: the shell has no boolean type, only exit statuses.') + '''
EXAM> “Write a script to check whether a number is positive, negative or zero.” → <code>if [ "$n" -gt 0 ]; then echo positive; elif [ "$n" -lt 0 ]; then echo negative; else echo zero; fi</code>.
''' + qc('Why does <code>[ "$a"="$b" ]</code> always say true?', 'Without spaces it is ONE word, "x=y", and a single non-empty string is true. Write [ "$a" = "$b" ].') + mistake('if [[ $num -gt 0]] ; then',
    'if [[ $num -gt 0 ]]; then',
    ']] must be a separate word: without the space bash reports “syntax error in conditional expression”. Checked (from the class notes’ positive/negative example).') + mistake('Vowel check:  [ "$char" == "a" ] || … || [ "$char" == "u" ]   then   [[ $char =~ [a-zA-Z] ]] → consonant',
    'case $char in [aeiouAEIOU]) echo vowel;; [a-zA-Z]) echo consonant;; *) echo "not a letter";; esac',
    'The notes’ version reports A, E, I, O, U as consonants (only lowercase vowels are listed), and [[ =~ [a-zA-Z] ]] also accepts “ab”. Real run: a → vowel, A → consonant.') + mistake('Days example: prompt says “Monday”, patterns are monday) tuesday) …',
    'case ${day,,} in monday) …   (convert to lowercase first)   or   [Mm]onday)',
    'case is case-sensitive: typing Monday as the prompt suggests goes to the default branch. ${day,,} lowercases (Lesson 12.14).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>[ ] vs [[ ]] vs (( )), and the three families of tests</h2>
''' + table(['', '<code>[ ]</code> / test', '<code>[[ ]]</code>', '<code>(( ))</code>'], [
    ['Kind', 'builtin command (POSIX)', 'bash keyword', 'bash arithmetic'],
    ['Quote variables?', 'yes, always', 'not needed (still fine)', 'no $ needed'],
    ['Numbers', '-eq -lt -gt …', '-eq -lt -gt …', '== &lt; &gt; &lt;= &gt;='],
    ['Strings', '= != -z -n', '== != &lt; &gt; patterns', '—'],
    ['Patterns / regex', 'no', '== *.log, =~ regex', '—'],
    ['AND / OR', '[ ] &amp;&amp; [ ]', '&amp;&amp; || inside', '&amp;&amp; || inside'],
    ['Works in sh (dash)', 'yes', 'no', 'no'],
], minw=560) + table(['File test', 'True when', 'String / number test', 'True when'], [
    ['<code>-e f</code>', 'exists (anything)', '<code>-z "$s"</code>', 'empty'],
    ['<code>-f f</code>', 'regular file', '<code>-n "$s"</code>', 'not empty'],
    ['<code>-d d</code>', 'directory', '<code>"$a" = "$b"</code>', 'same text'],
    ['<code>-L f</code>', 'symbolic link', '<code>"$a" != "$b"</code>', 'different'],
    ['<code>-r -w -x f</code>', 'readable / writable / executable by you', '<code>a -eq b</code>', 'numbers equal'],
    ['<code>-s f</code>', 'exists and not empty', '<code>a -ne b</code>', 'not equal'],
    ['<code>a -nt b</code>', 'a newer than b', '<code>a -lt / -le b</code>', 'less / less or equal'],
    ['<code>-u -g -k f</code>', 'SUID / SGID / sticky (9.4)', '<code>a -gt / -ge b</code>', 'greater / greater or equal'],
], minw=560) + table(['', 'if / elif', 'case'], [
    ['Best for', 'different kinds of conditions', 'one value, many possible matches'],
    ['Compares with', 'any test or command', 'glob patterns'],
    ['Several values', 'cond1 || cond2', 'a|b|c)'],
    ['Default', 'else', '*)'],
    ['Readability with 5+ choices', 'long chain', 'clear table'],
], minw=440) + qc('Which test is true for a symbolic link that points to a missing file: <code>-e</code> or <code>-L</code>?', '-L only. -e follows the link to the target, which does not exist.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>if, test and case, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/dc</code>: <code>app.conf</code>, an empty <code>empty.txt</code>, an executable <code>run.sh</code>, a symlink <code>link.conf</code>, and <code>logs/web.log</code>. Answers that a person would type are given with <code>&lt;&lt;&lt;</code>.</p>
''' + cmdcard_u(['any decision: exists?, empty?, bigger?, did it work?', 'guarding risky commands'],
               ['testing a command’s output text when its exit status already says it (grep -q)'])(
    'if', 'if · elif · else · fi', 'two or more paths',
    '<code>if LIST; then …; [elif LIST; then …;] [else …;] fi</code>. The LIST is any command; its exit status decides. Write <code>then</code> on the same line after <code>;</code> or on the next line. Ifs can be nested inside then/else parts.',
    'if COND; then CMDS; elif COND; then CMDS; else CMDS; fi', 'safe',
    [('if COND; then', 'start', 'always'),
     ('elif COND; then', 'another condition', 'ranges'),
     ('else', 'none matched', 'default'),
     ('fi', 'end', 'always'),
     ('if ! COND', 'negate', 'not exists'),
     ('if cmd1 && cmd2', 'both must succeed', 'chains'),
     ('nested if', 'if inside then/else', 'two-level checks')],
    dict(cmd="for n in 15 -4 0; do\n  if [ \"$n\" -gt 0 ]; then echo \"$n is positive\"\n  elif [ \"$n\" -lt 0 ]; then echo \"$n is negative\"\n  else echo \"$n is zero\"; fi\ndone", note='The classic syllabus exercise; the for loop just runs it for three values (Lesson 12.9).'),
    [('sys', [
        dict(situation='if on a command, not on brackets.', setup=DC, cmd="cd ~/dc\nif grep -q ' 500$' logs/web.log; then echo 'server errors found'; fi\nif ! ping -c1 -W1 10.255.255.1 > /dev/null 2>&1; then echo 'host unreachable'; fi", why='grep -q and ping already return 0/1: no [ ] needed.')]),
     ('dev', [
        dict(situation='Nested if: two levels of checks.', setup=DC, cmd="cd ~/dc; f=app.conf\nif [ -e \"$f\" ]; then\n  if [ -r \"$f\" ]; then echo \"$f exists and is readable\"\n  else echo \"$f exists but is not readable\"; fi\nelse\n  echo \"$f is missing\"\nfi", why='The inner test runs only when the outer one was true.')]),
     ('qa', [
        dict(situation='The puzzle: > inside [ ] is a redirection.', setup=DC, cmd="cd ~/dc; count=5\nif [ $count > 10 ]; then echo 'too many?!'; fi\nls 10 && rm 10\nif [ \"$count\" -gt 10 ]; then echo 'too many'; else echo 'ok with -gt'; fi\nif (( count > 10 )); then echo 'too many'; else echo 'ok with (( ))'; fi", why='[ $count > 10 ] means: run [ 5 ] with output to a file called 10. [ 5 ] is true (non-empty). Use -gt or (( )).')]),
    ],
    anat=anatomy([('if', 'cmd', 'keyword'), ('[', 'cmd', 'test command'), ('"$n" -gt 0', 'arg', 'expression'), (']', 'arg', 'last argument'), ('; then', 'opt', 'keyword')], 'Spaces around [ and ] because they are words.')
) + mistake('if [ $count > 10 ]   ·   if ["$a"="$b"]', 'if [ "$count" -gt 10 ]   ·   if [ "$a" = "$b" ]',
            '> redirects, and words must be separated by spaces. Real run in the puzzle card: count=5 printed “too many” and created a file called 10.') + cmdcard_u(['checking files and folders before using them', 'permissions checks', 'is this newer than that?'],
               ['checking with ls and grep the output'])(
    'filetests', 'test -e -f -d -r -w -x -s -L -nt', 'file tests',
    'Ask the filesystem a yes/no question about a path. <code>-e</code> exists, <code>-f</code> regular file, <code>-d</code> folder, <code>-L</code> symlink, <code>-r/-w/-x</code> permissions for <b>you</b>, <code>-s</code> not empty, <code>-nt/-ot</code> newer/older. Combine with <code>!</code>.',
    '[ -f FILE ]   ·   [ ! -d DIR ]   ·   [ A -nt B ]', 'safe',
    [('-e', 'exists', 'anything'),
     ('-f', 'regular file', 'configs, data'),
     ('-d', 'directory', 'targets'),
     ('-s', 'not empty', 'outputs'),
     ('-r -w -x', 'your permissions', 'before use'),
     ('-L', 'symbolic link', 'deploy links'),
     ('-nt / -ot', 'newer / older', 'rebuild?'),
     ('!', 'not', 'missing')],
    dict(setup=DC, cmd="cd ~/dc\nfor f in app.conf empty.txt run.sh link.conf logs nothing; do\n  printf '%-10s' \"$f\"\n  [ -e \"$f\" ] && printf ' exists' || printf ' MISSING'\n  [ -f \"$f\" ] && printf ' file'; [ -d \"$f\" ] && printf ' dir'; [ -L \"$f\" ] && printf ' link'\n  [ -s \"$f\" ] && printf ' non-empty'; [ -x \"$f\" ] && printf ' executable'\n  echo\ndone", note='-f is also true for link.conf because tests follow links; -L tells you it is a link. A folder counts as non-empty (-s) and “executable” (x = enter).'),
    [('sys', [
        dict(situation='Create a folder only if it does not exist.', setup=DC, cmd="cd ~/dc\nfor d in backup reports; do\n  if [ ! -d \"$d\" ]; then mkdir \"$d\"; echo \"created $d\"; else echo \"$d already there\"; fi\ndone", why='! negates. (mkdir -p does the same silently.)')]),
     ('devops', [
        dict(situation='Rebuild only when the source is newer.', setup=DC, cmd="cd ~/dc; touch -d '1 hour ago' app.conf.bak\nif [ app.conf -nt app.conf.bak ]; then cp app.conf app.conf.bak; echo 'backup refreshed'; else echo 'backup is current'; fi", why='-nt compares modification times: the idea behind make (Lesson 12.12).')]),
     ('sec', [
        dict(situation='Refuse to run with a world-writable config.', setup=DC, cmd="cd ~/dc; chmod 666 app.conf\nif [ -n \"$(find app.conf -perm -o+w)\" ]; then echo 'refusing: app.conf is world-writable'; fi\nchmod 644 app.conf", why='No direct test for “others can write”; find -perm answers it (Lesson 9.1).')]),
    ]
) + cmdcard_u(['comparing user input, names and modes', 'checking that a value was given'],
               ['numbers (use -eq or (( )))', 'unquoted variables in [ ]'])(
    'strtests', '= != -z -n · [[ == pattern ]] · =~', 'string tests',
    'In <code>[ ]</code>: <code>=</code> (or <code>==</code> in bash), <code>!=</code>, <code>-z</code> empty, <code>-n</code> not empty; always quote. In <code>[[ ]]</code>: <code>==</code> with an unquoted pattern on the right (<code>*.log</code>), and <code>=~</code> with a regular expression; captured groups land in <code>BASH_REMATCH</code>.',
    '[ "$a" = "$b" ]   ·   [ -z "$s" ]   ·   [[ $f == *.log ]]   ·   [[ $x =~ ^[0-9]+$ ]]', 'safe',
    [('"$a" = "$b"', 'equal text', 'POSIX'),
     ('"$a" != "$b"', 'different', 'POSIX'),
     ('-z "$s" / -n "$s"', 'empty / not empty', 'required values'),
     ('[[ $f == *.csv ]]', 'glob pattern', 'file types'),
     ('[[ $x =~ RE ]]', 'regex', 'validate input'),
     ('${BASH_REMATCH[1]}', 'captured group', 'extract parts'),
     ('[[ $a < $b ]]', 'text order', 'sorting names')],
    dict(cmd="user=riya; empty=''\n[ \"$user\" = riya ] && echo 'user is riya'\n[ -z \"$empty\" ] && echo 'empty is empty'\n[ -n \"$user\" ] && echo 'user is not empty'\nf=sales_2026.csv; [[ $f == *.csv ]] && echo \"$f is a CSV\"", note='All four print, because each test returned 0.'),
    [('qa', [
        dict(situation='Validate a number with a regex.', cmd="for v in 42 4x2 '' -7; do\n  if [[ $v =~ ^-?[0-9]+$ ]]; then echo \"'$v' is a whole number\"; else echo \"'$v' is NOT a number\"; fi\ndone", why='The calculator from 12.7 should check its input like this before doing maths.')]),
     ('data', [
        dict(situation='Extract parts with BASH_REMATCH.', cmd="d='2026-11-11'\nif [[ $d =~ ^([0-9]{4})-([0-9]{2})-([0-9]{2})$ ]]; then\n  echo \"year ${BASH_REMATCH[1]}, month ${BASH_REMATCH[2]}, day ${BASH_REMATCH[3]}\"\nfi", why='Each ( ) group is captured in order.')]),
     ('dev', [
        dict(situation='Quoted vs unquoted pattern.', cmd="s=hello\n[[ $s == h* ]] && echo 'pattern h* matches'\n[[ $s == \"h*\" ]] || echo 'quoted \"h*\" is literal text: no match'", why='Quote the right side to compare literally; leave it unquoted to use it as a pattern.')]),
    ]
) + cmdcard_u(['sizes, counts, percentages, exit codes', 'ranges (between 1 and 10)'],
               ['decimal numbers (test only does integers)', 'string operators < > for numbers'])(
    'numtests', '-eq -ne -lt -le -gt -ge · (( ))', 'number tests',
    'In <code>[ ]</code> / <code>[[ ]]</code>: <code>-eq</code> equal, <code>-ne</code> not equal, <code>-lt</code> &lt;, <code>-le</code> ≤, <code>-gt</code> &gt;, <code>-ge</code> ≥. In <code>(( ))</code>: normal symbols <code>== != &lt; &lt;= &gt; &gt;=</code>. Integers only; an empty or non-numeric value is an error in [ ].',
    '[ "$a" -gt "$b" ]   ·   (( a > b ))   ·   [ "$n" -ge 1 ] && [ "$n" -le 10 ]', 'safe',
    [('-eq / ==', 'equal', 'counts'),
     ('-ne / !=', 'not equal', 'status checks'),
     ('-lt -le', '< ≤', 'limits'),
     ('-gt -ge', '> ≥', 'thresholds'),
     ('(( a > b ))', 'readable form', 'bash'),
     ('&& / ||', 'ranges, either', 'between')],
    dict(cmd="a=10; b=20\n[ \"$a\" -lt \"$b\" ] && echo \"$a -lt $b\"\n[ \"$a\" -ne \"$b\" ] && echo \"$a -ne $b\"\n(( b >= 20 )) && echo \"b >= 20\"\nn=7; [ \"$n\" -ge 1 ] && [ \"$n\" -le 10 ] && echo \"$n is between 1 and 10\"", note='Your notes’ six relational operators, run for real.'),
    [('sys', [
        dict(situation='A disk threshold check.', cmd="used=$(df --output=pcent / | tail -1 | tr -dc 0-9)\nif (( used >= 90 )); then echo 'CRITICAL'; elif (( used >= 75 )); then echo 'WARNING'; else echo 'disk ok'; fi", why='elif from the highest threshold down; tr -dc keeps only the digits of “ 47%”.')]),
     ('qa', [
        dict(situation='String vs number comparison.', cmd="[[ 10 > 9 ]] && echo 'as text 10 > 9' || echo 'as TEXT, 10 is NOT > 9'\n[[ 10 -gt 9 ]] && echo 'as numbers 10 -gt 9'", why='Text compares character by character: “1” sorts before “9”. Use -gt or (( )) for numbers.')]),
    ]
) + mistake('[ $name = riya ]   with name empty', '[ "$name" = riya ]',
            'Unquoted and empty, the test becomes [ = riya ]: “unary operator expected”. Quotes keep an empty value as an empty string.') + cmdcard_u(['menus and actions (start/stop/status)', 'file types by extension', 'yes/no answers in many spellings'],
               ['conditions that are not about one value (use if)'])(
    'case', 'case … in … ) … ;; esac', 'many choices',
    '<code>case WORD in PATTERN) CMDS ;; … esac</code>. Patterns are globs: <code>*</code>, <code>?</code>, <code>[abc]</code>, and <code>a|b</code> for alternatives. The first match wins; <code>*)</code> at the end catches everything else. Quoting the word is optional but harmless.',
    'case "$x" in a|b) …;; *.log) …;; [0-9]) …;; *) …;; esac', 'safe',
    [('word)', 'exact', 'actions'),
     ('a|b)', 'either', 'synonyms'),
     ('*.csv)', 'wildcard', 'file types'),
     ('[yY]*)', 'character class', 'yes / Yes / y'),
     ('*)', 'default', 'usage message'),
     (';;', 'end branch', 'always'),
     (';&  ;;&', 'fall through / keep testing', 'rare')],
    dict(cmd="for action in start stop status reload foo; do\n  case $action in\n    start)         echo \"$action: starting app\" ;;\n    stop)          echo \"$action: stopping app\" ;;\n    status|state)  echo \"$action: app is running\" ;;\n    reload|restart) echo \"$action: restarting app\" ;;\n    *)             echo \"$action: usage: start|stop|status|reload\" ;;\n  esac\ndone", note='The shape of almost every service script in /etc/init.d.'),
    [('data', [
        dict(situation='Choose a tool by file extension.', cmd="for f in sales.csv notes.txt photo.JPG data.json backup.tar.gz; do\n  case ${f,,} in\n    *.csv)     echo \"$f -> load with awk\" ;;\n    *.json)    echo \"$f -> parse with jq\" ;;\n    *.jpg|*.png) echo \"$f -> image, skip\" ;;\n    *.tar.gz)  echo \"$f -> extract with tar\" ;;\n    *)         echo \"$f -> unknown type\" ;;\n  esac\ndone", why='${f,,} lowercases first, so .JPG matches *.jpg.')]),
     ('sys', [
        dict(situation='Yes/no answers in any spelling.', cmd="for a in y Yes YES n No maybe; do\n  case $a in [yY]|[yY][eE][sS]) echo \"$a -> yes\";; [nN]|[nN][oO]) echo \"$a -> no\";; *) echo \"$a -> please answer yes or no\";; esac\ndone", why='Character classes handle upper and lower case without converting.')]),
    ]
) + undo('Decisions do not change anything by themselves; check them before the commands they guard.', [
    ('Not sure which branch will run:', 'run with <code>bash -x</code> (12.6): you see each test and its values.'),
    ('A stray file appeared (named 10, 5…):', 'a &gt; or &lt; inside [ ] created it: delete it and use -gt/-lt.'),
    ('Script works in bash, fails with sh:', '[[ ]] and (( )) are bash-only; use #!/bin/bash or [ ].'),
    ('case never matches:', 'check upper/lower case and spaces in the value: <code>printf \'[%s]\\n\' "$x"</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='x=""; [ $x = yes ]', meaning='Empty unquoted variable: [ = yes ].', fix='<code>[ "$x" = yes ]</code>.'),
    dict(cmd='[ abc -gt 5 ]', meaning='-gt needs numbers.', fix='Validate with [[ =~ ]] first.'),
    dict(cmd='["a" = "a"]', meaning='No space after [: the command is called ["a".', fix='<code>[ "a" = "a" ]</code>.'),
    dict(cmd="bash -c 'if [ 1 -eq 1 ]; then echo x'", meaning='if without fi.', fix='Close every if with fi, case with esac.'),
]) + qc('What does <code>if [ "abc" ]; then echo yes; fi</code> print, and why?', 'yes: a test with one non-empty string is true.') + '''
'''
cards = cards + '</section>\n'

def flow(k):
    o = label_box(14, 16, 332, 30, ['if [ -d "$dir" ]; then backup; else echo missing; fi'], 'blue', 7.6)
    if k >= 1:
        o += label_box(14, 56, 160, 34, ['[ -d /srv/data ]', 'runs: status 1'], 'amber', 8)
    if k >= 2:
        o += label_box(186, 56, 160, 34, ['$? = 1 → false', 'skip then'], 'red', 8)
    if k == 3:
        o += label_box(14, 100, 332, 34, ['else branch: echo missing'], 'green', 8)
    return o
see_cmds = [['$ ./backup.sh /srv/data'], ['$ ./backup.sh /srv/data'], ['$ ./backup.sh /srv/data'], ['$ ./backup.sh /srv/data', ('ERROR: /srv/data does not exist', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Run with a folder.', 'The test runs…', '…and returns 1.', 'else runs.'])]
behind = [flow(k) + t(180, 175, n, 8.4, 'violet', bold=True) for k, n in enumerate(['if is followed by a command.', '[ is that command: it checks the folder.', 'if reads its exit status.', 'Non-zero: the else branch.'])]
two = anim_two('if reads $?', 'Behind the screen: a test is just a command',
               'A terminal: backup.sh with a missing folder prints an error.',
               'The if line runs the [ command, which returns status 1; if therefore skips then and runs else.', see, behind,
               ['Run.', 'Test.', 'Status.', 'Branch.'],
               ['if', '[ -d ]', '1 = false', 'else'])

def cs(k):
    pats = ['start)', 'stop)', 'status|state)', '*)']
    o = label_box(14, 14, 332, 26, ['case "$1" in   ($1 = status)'], 'blue', 8)
    for i, p in enumerate(pats):
        tn = 'card'
        if k >= 1 and i < min(k, 2): tn = 'red'
        if k >= 3 and i == 2: tn = 'green'
        o += label_box(14, 48 + i * 30, 160, 24, [p], tn, 8)
    if k == 3:
        o += label_box(190, 108, 156, 24, ['echo running; ;;'], 'green', 8)
    return o
frames = [cs(0) + t(180, 190, 'One value, a list of patterns.', 8.6, 'violet', bold=True),
          cs(1) + t(180, 190, 'start) does not match.', 8.6, 'red', bold=True),
          cs(2) + t(180, 190, 'stop) does not match.', 8.6, 'red', bold=True),
          cs(3) + t(180, 190, 'status matches: run it, then esac.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'How case picks a branch',
              'Top to bottom; the first match wins.',
              'case', 'The value status is compared with start, stop, status|state and *; the third pattern matches and only its commands run.', frames,
              ['Value.', 'No.', 'No.', 'Match.'], hid='scenario-case')

dx = dissect('Layer by layer: what a test really is',
    'Each layer has a real command and output from our build machine.', [
    dict(key='status', name='Exit status', sub='0 or not', why='The only thing if sees.', how='$?.', impl='Every command.', used='if, while, &&.',
         cmd="true; echo \"true: $?\"; false; echo \"false: $?\"; [ 1 -eq 2 ]; echo \"[ 1 -eq 2 ]: $?\""),
    dict(key='test', name='[ and test', sub='builtins', why='Answer a question.', how='Arguments.', impl='Also /usr/bin/[.', used='POSIX scripts.',
         cmd="type [ test; ls -l /usr/bin/[ | awk '{print $1, $NF}'"),
    dict(key='dbl', name='[[ ]]', sub='keyword', why='Safer, patterns, regex.', how='Parsed specially.', impl='bash only.', used='bash scripts.',
         cmd="type [[; x='a b'; [[ $x == 'a b' ]] && echo 'no quotes needed in [[ ]]'"),
    dict(key='arith', name='(( ))', sub='arithmetic', why='Numbers naturally.', how='Status 0 if non-zero.', impl='bash.', used='Counters.',
         cmd="(( 3 > 2 )); echo $?; (( 0 )); echo $?"),
], hint='From exit status up to the bash keywords. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>if reads an exit status, and case picks a branch</h2>
''' + two + s1 + dx + qc('Why can <code>if cd /data; then</code> be better than <code>if [ -d /data ]; then cd /data</code>?', 'It tests what you really need (that cd works: exists AND you may enter it) in one step.') + '''
</section>
'''

VAR = variations('Fifteen more decision scripts, each a variation of the examples above. All were really run on our build machine.', [
    ('if variations', [
        dict(title='Even or odd', cmd="for n in 4 7; do if (( n % 2 == 0 )); then echo \"$n even\"; else echo \"$n odd\"; fi; done", why='% gives the remainder; (( )) tests it.'),
        dict(title='Largest of three numbers', cmd="a=12; b=45; c=27\nif (( a >= b && a >= c )); then max=$a\nelif (( b >= c )); then max=$b\nelse max=$c; fi\necho \"largest: $max\"", why='&& inside (( )); elif narrows the choice.'),
        dict(title='Leap year (nested logic)', cmd="for y in 2024 1900 2000 2026; do\n  if (( y % 400 == 0 )) || { (( y % 4 == 0 )) && (( y % 100 != 0 )); }; then echo \"$y leap\"; else echo \"$y not leap\"; fi\ndone", why='A classic exam question; { } groups the && part.'),
        dict(title='Grade from marks (elif ladder)', cmd="for m in 92 78 55 30; do\n  if (( m >= 90 )); then g=A; elif (( m >= 75 )); then g=B; elif (( m >= 50 )); then g=C; else g=F; fi\n  echo \"$m -> $g\"\ndone", why='Check the highest range first.'),
        dict(title='One-line if with && and ||', cmd="f=/etc/hostname\n[ -r \"$f\" ] && echo \"can read $f\" || echo \"cannot read $f\"", why='Short form; but if the && part fails, the || part also runs, so use a full if when the then-part can fail.'),
    ]),
    ('test variations', [
        dict(title='Check several required files at once', setup=DC, cmd="cd ~/dc; missing=0\nfor f in app.conf run.sh secrets.env; do [ -f \"$f\" ] || { echo \"missing: $f\"; missing=1; }; done\n[ $missing -eq 0 ] && echo 'all present' || echo 'cannot start'", why='Collect problems first, decide at the end.'),
        dict(title='Is the script run as root?', cmd="if [ \"$(id -u)\" -eq 0 ]; then echo 'root'; else echo \"normal user $(whoami)\"; fi", why='UID 0 = root (Lesson 8.1).'),
        dict(title='Empty or missing argument', cmd="check(){ if [ -z \"${1:-}\" ]; then echo 'no argument given'; else echo \"argument: $1\"; fi; }\ncheck; check report.txt", why='${1:-} avoids a set -u error; -z tests empty.'),
        dict(title='Compare two files', setup=DC, cmd="cd ~/dc; cp app.conf copy.conf\nif cmp -s app.conf copy.conf; then echo 'identical'; fi\necho 'port=9090' > copy.conf\ncmp -s app.conf copy.conf || echo 'they differ now'", why='cmp -s is silent; its exit status is the answer.'),
        dict(title='Does a user exist?', cmd="for u in riya ghost; do if id \"$u\" > /dev/null 2>&1; then echo \"$u exists\"; else echo \"$u does not exist\"; fi; done", why='Any command can be a test.'),
    ]),
    ('[[ ]] and case variations', [
        dict(title='Email-like format check', cmd="for e in riya@cdac.in riya@ bad.mail; do [[ $e =~ ^[^@]+@[^@]+\\.[a-z]+$ ]] && echo \"$e looks valid\" || echo \"$e is invalid\"; done", why='A simple regex; real email validation is much harder.'),
        dict(title='Vowel or consonant, all cases', cmd="for c in a E k 7 ab; do\n  case $c in [aeiouAEIOU]) echo \"$c vowel\";; [a-zA-Z]) echo \"$c consonant\";; *) echo \"$c not a single letter\";; esac\ndone", why='The corrected version of the class-notes example: upper-case vowels and “ab” are handled.'),
        dict(title='Day of the week, any capitals', cmd="for day in Monday SATURDAY friday holiday; do\n  case ${day,,} in\n    saturday|sunday) echo \"$day: weekend\";;\n    monday|tuesday|wednesday|thursday|friday) echo \"$day: working day\";;\n    *) echo \"$day: not a day\";;\n  esac\ndone", why='${day,,} lowercases, so Monday and SATURDAY match.'),
        dict(title='Car brand to country (notes example, fixed)', cmd="for car in Tesla bmw Toyota Tata; do\n  case ${car,,} in\n    tesla) c=USA;; bmw|mercedes|audi|porsche) c=Germany;; toyota|mazda|subaru) c=Japan;; *) c=unknown;;\n  esac\n  echo \"$car: $c\"\ndone", why='Same idea as the notes; lowercase first so bmw and BMW both match.'),
        dict(title='Menu with numbers and words', cmd="choose(){ case $1 in 1|start) echo start;; 2|stop) echo stop;; [3-9]) echo \"option $1 not used yet\";; *) echo 'invalid';; esac; }\nfor x in 1 stop 7 x; do choose \"$x\"; done", why='Several spellings per branch with |; [3-9] is a range.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Decisions at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['case $1', 'services'], 'blue', 8.6), '1. Service scripts',
              'Init and helper scripts use case "$1" in start|stop|restart|status — the most common shell pattern in Linux.', ['Action', '*case', 'run']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-d -w', 'backups'], 'green', 8.6), '2. Backups and clean-ups',
    'Check that the source exists, the target is writable and the disk has space before copying or deleting.', ['Check', '*[ -d ]', 'copy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['(( >= 90 ))', 'monitoring'], 'red', 8.6), '3. Monitoring',
    'Threshold checks (disk, load, queue length) with elif ladders send OK / WARNING / CRITICAL.', ['Measure', '*elif', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['=~', 'validation'], 'amber', 8.6), '4. Input validation',
    'Scripts check that arguments are numbers, dates or IDs before using them in SQL or commands.', ['Input', '*[[ =~ ]]', 'safe']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['if grep -q', 'CI gates'], 'violet', 8.6), '5. CI quality gates',
    'Pipelines fail a build if grep finds TODO in release code or a test report contains failures.', ['Scan', '*if grep', 'pass/fail']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='File or not', scenario='Quick check.', cmd="[ -f /etc/hostname ] && echo yes || echo no", explain='-f.'),
    dict(level='b', title='Is it a number?', scenario='Validate input.', cmd="x=123; [[ $x =~ ^[0-9]+$ ]] && echo number", explain='=~.'),
    dict(level='i', title='Exit if not root', scenario='Admin scripts.', cmd="[ \"$(id -u)\" -eq 0 ] || echo 'please run with sudo'", explain='id -u.'),
    dict(level='i', title='Newest of two files', scenario='Which changed last?', cmd="touch -d '1 day ago' old.txt; touch new.txt; [ new.txt -nt old.txt ] && echo 'new.txt is newer'", explain='-nt.'),
    dict(level='a', title='Action dispatcher', scenario='Many actions.', cmd="for a in start oops; do case $a in start|stop|status) echo \"doing $a\";; *) echo \"unknown: $a\" >&2;; esac; done 2>&1", explain='case with a default.'),
], extra=build_up('a service control script', 'Riya writes svc.sh step by step: argument check, case, and a status test.', DC, [
    ("cd ~/dc; printf '#!/bin/bash\\naction=${1:-}\\n[ -n \"$action\" ] || { echo \"usage: svc.sh start|stop|status\"; exit 2; }\\n' > svc.sh; bash svc.sh; echo \"status $?\"", '1. Require an action.'),
    ("cd ~/dc; printf 'case $action in\\n  start) touch app.pid; echo started;;\\n  stop) rm -f app.pid; echo stopped;;\\n  status) if [ -f app.pid ]; then echo running; else echo stopped; fi;;\\n  *) echo \"unknown action: $action\"; exit 2;;\\nesac\\n' >> svc.sh; bash svc.sh status", '2. Add case with a status test.'),
    ('cd ~/dc; bash svc.sh start; bash svc.sh status; bash svc.sh stop; bash svc.sh status; bash svc.sh dance; echo "status $?"', '3. Try every action.'),
], cumulative=True, expect='any')) + VAR + which('Choosing the right construct.', [
    ('Different kinds of checks', 'if / elif', 'Any command.', 'Long case for unrelated tests.'),
    ('One value, many choices', 'case', 'Readable.', 'Long elif chains.'),
    ('Files', '[ -f ] [ -d ] [ -s ]', 'Built in.', 'Parsing ls.'),
    ('Numbers', '-gt or (( ))', 'Correct.', '> < inside [ ].'),
    ('Patterns / regex', '[[ == *.x ]] / =~', 'Powerful.', '[ ] (no patterns).'),
    ('Command success', 'if cmd', 'Direct.', 'Testing its output text.'),
]) + keys('Handy forms.', [
    ('[ -n "${1:-}" ]', 'argument given?', 'scripts'),
    ('[[ $x =~ ^[0-9]+$ ]]', 'is integer', 'validation'),
    ('(( n >= 1 && n <= 10 ))', 'range', 'numbers'),
    ('case ${x,,} in', 'case-insensitive', 'input'),
    ('if ! cmd; then', 'on failure', 'errors'),
    ('[ -t 0 ]', 'stdin is a terminal?', 'interactive'),
]) + scriptit('check-env.sh', 'A start-up check that uses every kind of test from this lesson: arguments, files, permissions, numbers, regex and case.',
'''env=${1:-dev}
case $env in dev|test|prod) ;; *) echo "unknown environment: $env" >&2; exit 2;; esac
conf=$HOME/dc/app.conf
[ -f "$conf" ] || { echo "missing $conf" >&2; exit 1; }
[ -r "$conf" ] || { echo "cannot read $conf" >&2; exit 1; }
port=$(grep -oP '(?<=port=)[0-9]+' "$conf")
if [[ ! $port =~ ^[0-9]+$ ]]; then echo "bad port"; exit 1
elif (( port < 1024 )) && [ "$(id -u)" -ne 0 ]; then echo "port $port needs root"; exit 1
fi
echo "env=$env port=$port: all checks passed"''',
'<p>Run with the default environment on the lesson’s sample folder.</p>', expect='any') + puzzle_answer('Inside <code>[ ]</code>, <code>&gt; 10</code> is a <b>redirection</b>: the shell ran <code>[ 5 ]</code> with its output sent to a new file called <code>10</code>. <code>[ 5 ]</code> (one non-empty word) is always true, so “too many” is printed for any value. Correct: <code>[ "$count" -gt 10 ]</code> or <code>(( count &gt; 10 ))</code>, then delete the stray file 10.') + qc('Which ends a case branch, and which ends the case?', '<code>;;</code> ends a branch, <code>esac</code> ends the case.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/dc', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../07-script-input-positional-parameters-read-and-arithmetic/">Lesson 12.7</a> ($1, read, $(( ))) and <a href="../../05-redirection-and-pipes/04-chaining-commands-exit-codes-and-xargs/">Lesson 5.4</a> (exit status).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
