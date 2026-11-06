import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='05-redirection-and-pipes', lesson='04-chaining-commands-exit-codes-and-xargs', n='5.4',
    module_label='Module 5 · Redirection, pipes and chaining',
    title='Chaining commands: ;, &&, ||, exit codes, $( ) and xargs',
    desc='Exit codes and $? (0, 1, 2, 124, 126, 127, 128+N, wrap-around at 256), chaining with ;, && and ||, the a && b || c trap, grouping with { } and ( ), command substitution $( ) and backticks, and xargs with -0, -I{}, -n, -r, -P, -p and -t. Each explained, then used by admins, developers, DevOps, DBAs, data, security and QA, with real outputs and corrected exit-code notes.',
    og_desc='Exit codes, ; && ||, $( ) and xargs explained with real outputs, the a && b || c trap and safe find | xargs.',
    minutes=40, level='Beginner → Advanced',
    lead='Every Linux command ends with a number: 0 means it worked. This lesson shows how to read that number, how ; && and || decide what runs next, how $( ) puts output inside commands, and how xargs turns a list into arguments safely.',
    chips=['Operators by field', 'Real exit-code table', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Exit codes, chaining, $( ) and xargs
ls /etc > /dev/null; echo "ls /etc -> $?"
ls /nope 2> /dev/null; echo "ls /nope -> $?"
mkdir -p demo && echo "created demo"
cd /nope 2> /dev/null || echo "cd failed, staying here"
echo "Today is $(date -d 2026-11-06 +%A)"
printf 'a.txt\\nb.txt\\n' | xargs -I{} touch demo/{}
ls demo
"""

RUN = dict(
    heading='Codes, chains, substitution and xargs in eight lines',
    intro='<p>See two exit codes, an &amp;&amp; on success, an || on failure, a date inside a sentence, and xargs creating files from a list.</p>',
    code=MAIN,
    anno=[
        ('ls /nope 2> /dev/null; echo "ls /nope -> $?"', '2'),
        ('cd /nope 2> /dev/null || echo "cd failed, staying here"', 'The fallback runs.'),
        ('echo "Today is $(date -d 2026-11-06 +%A)"', 'Friday'),
        ("printf 'a.txt\\nb.txt\\n' | xargs -I{} touch demo/{}", 'One touch per name.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which code does ls /nope give?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which lines print? Then run.',
             code="true && echo A\nfalse && echo B\nfalse || echo C\ntrue && false || echo D\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the group gives a syntax error. Fix it.',
             code="{ echo one; echo two }\n", expect='any'),
        dict(label='4 · Your turn', hint='Create backup_YYYY-MM-DD.txt for 2026-11-06 using $( ), then list it.',
             code='touch "backup_$(date -d 2026-11-06 +%F).txt" && ls backup_*\n'),
        dict(label='5 · Challenge', hint='With xargs, print each of 1–6 in pairs (two per line).',
             code='seq 1 6 | xargs -n 2 echo\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: Ctrl+C codes, sudo chains and ARG_MAX',
    intro='<p>These need a keyboard, sudo or many files. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · The code of Ctrl+C', cmd='sleep 30   # press Ctrl+C\necho $?', output='^C\n130', note='Typical: 128 + 2 (SIGINT).'),
        dict(title='2 · Update, upgrade, clean only on success', cmd='sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y', output='…\n0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.', note='Typical.'),
        dict(title='3 · Repeat the last command with sudo', cmd='apt install tree\nsudo !!', output='E: Could not open lock file /var/lib/dpkg/lock-frontend - open (13: Permission denied)\nsudo apt install tree\n…', note='Typical: !! is replaced by the previous command.'),
        dict(title='4 · Argument list too long, and xargs', cmd='touch f{1..200000}; rm f*\nfind . -name "f*" -print0 | xargs -0 rm', output='bash: /usr/bin/rm: Argument list too long\n(second command: no output, all deleted)', note='Typical: xargs splits the list into many rm runs.'),
        dict(title='5 · Limits on our build machine', cmd='getconf ARG_MAX; xargs --show-limits < /dev/null 2>&1 | head -3', output=pc('getconf ARG_MAX; xargs --show-limits < /dev/null 2>&1 | head -3'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Exit codes, step by step',
    intro='<p>Step through a script and watch $? and the variables change.</p>',
    code='''mkdir -p out && echo "out ready"
ls /nope 2> /dev/null
rc=$?
[ "$rc" -eq 2 ] && echo "ls failed with $rc"
n=$(printf 'x\\ny\\n' | xargs -n 1 echo | wc -l)
echo "xargs ran echo for $n items"
''',
    notes={1: '&& :: mkdir worked, so echo runs.', 2: 'Failure :: ls returns 2.', 3: 'Save $? :: Before it changes.', 4: 'Test :: The code was 2.', 5: '$( ) :: xargs ran echo twice.', 6: 'Report.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an admin’s guarded maintenance line, a DBA’s backup with a result code, and a DevOps clean-up with find and xargs.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='Do the next step only if this one worked',
         problem='<p>Create a work folder, write a file into it and show it, stopping at the first failure; print a message if anything failed.</p>',
         inp='nothing',
         approach=['&& between steps.', '|| at the end for the message.'],
         code='''mkdir -p work && echo 'hello' > work/note.txt && cat work/note.txt || echo 'something failed'
mkdir -p /root/work 2>/dev/null && echo 'never' || echo 'second chain failed at step 1'
''',
         notes={1: 'Chain :: All three steps worked.', 2: 'Failure :: mkdir failed, the rest skipped.'},
         tryit='Change work to /proc/work.'),
    dict(level='i', tag='DBA', title='A backup step that reports its result',
         problem='<p>Write a function that “dumps” a database to a dated file and returns 0 or 1; report the result.</p>',
         inp='a fake dump (no server here)',
         approach=['$( ) for the date.', 'return codes from the function.'],
         code='''dump() { [ "$1" = shop ] && echo "-- dump of $1" > "$1_$(date -d 2026-11-06 +%F).sql"; }
for db in shop hr; do
  if dump "$db"; then echo "$db: ok ($(ls "$db"_*.sql))"; else echo "$db: FAILED (code $?)"; fi
done
''',
         notes={1: 'Function :: Succeeds only for shop.', 3: 'if :: Branch on the code, no $? needed.'},
         tryit='Make hr succeed too.'),
    dict(level='a', tag='DevOps', title='Clean up old files safely with find and xargs',
         problem='<p>Delete *.log files older than 30 days under logs/, including names with spaces, and report the count.</p>',
         inp='three logs, two old (one with a space)',
         approach=['find -mtime +30 -print0.', 'xargs -0 -r rm -v; count the lines.'],
         code='''mkdir -p logs
touch -d '2026-09-01' logs/a.log 'logs/old app.log'; touch logs/today.log
n=$(find logs -name '*.log' -mtime +30 -print0 | xargs -0 -r rm -v | wc -l)
echo "deleted $n old logs"; ls logs
''',
         notes={2: 'Setup :: Two old, one new.', 3: 'Safe :: NUL-separated names, no run if empty.', 4: 'Only today.log is left.'},
         tryit='Run it twice: the second time deletes 0.'),
]

QUIZ = mix([
    dict(q='What exit code means success?', options=['1', '0', '255', '-1'], answer=1,
         why='0 = success; 1–255 = failure.'),
    dict(q='In a && b, when does b run?', options=['always', 'only if a succeeded', 'only if a failed', 'never'], answer=1,
         why='AND list.'),
    dict(q='cd /nope ; ls  — what does ls list?', options=['/nope', 'the current folder', 'nothing', 'an error'], answer=1,
         why='; ignores the failure.'),
    dict(q='Exit code 127 means…', options=['permission denied', 'command not found', 'killed', 'timeout'], answer=1,
         why='126 = not executable, 127 = not found.'),
    dict(q='What does true && false || echo X print?', options=['nothing', 'X', 'true', 'an error'], answer=1,
         why='false failed, so || runs: the a && b || c trap.'),
    dict(q='Why use find -print0 | xargs -0?', options=['faster', 'keeps names with spaces whole', 'sorts files', 'needed for sudo'], answer=1,
         why='NUL never occurs in file names.'),
    dict(q='What does $(date +%F) do?', options=['prints $(date)', 'runs date and inserts its output', 'arithmetic', 'creates a variable named date'], answer=1,
         why='Command substitution.'),
    dict(q='bash -c "exit 300"; echo $? prints…', options=['300', '44', '255', '0'], answer=1,
         why='Codes wrap modulo 256: 300 − 256 = 44.'),
])

REVISION = [
    '<code>$?</code> = last exit code: <b>0 success</b>, 1–255 failure. Save it at once: <code>rc=$?</code>.',
    'Codes: 1 general, 2 serious/misuse (ls, grep, syntax), 124 timeout, 126 not executable, 127 not found, 128+N signal (130 Ctrl+C, 137 kill -9, 141 SIGPIPE). Values wrap at 256.',
    '<code>a ; b</code> always · <code>a &amp;&amp; b</code> on success · <code>a || b</code> on failure.',
    '<code>a &amp;&amp; b || c</code> ≠ if/else (c runs if b fails). Use <code>if a; then b; else c; fi</code>.',
    'Never <code>cd dir ; rm …</code>: use <code>&amp;&amp;</code>.',
    '<code>{ a; b; }</code> (same shell; spaces and final ;), <code>( a; b )</code> (subshell).',
    '<code>"$(cmd)"</code>: output inside a command; trailing newlines removed; <code>$(( ))</code> is arithmetic.',
    'xargs: <code>-print0 | xargs -0</code>, <code>-I{}</code>, <code>-n</code>, <code>-r</code>, <code>-P</code>, <code>-t</code>/<code>-p</code>.',
]

FAQ = [
    ('What does $? mean in Linux?', 'It holds the exit status of the last command: 0 for success, a non-zero number (1–255) for failure.'),
    ('What is the difference between ;, && and ||?', '; runs the next command always, && only if the previous succeeded, || only if it failed.'),
    ('Is a && b || c the same as if-then-else?', 'No. c also runs when b fails. Use if a; then b; else c; fi when b can fail.'),
    ('What do exit codes 126 and 127 mean?', '126: the file was found but is not executable. 127: command not found.'),
    ('What is the difference between $( ) and backticks?', 'They do the same (command substitution); $( ) nests easily and is easier to read, so it is preferred.'),
    ('Why does xargs fail on file names with spaces?', 'By default it splits at spaces and newlines. Use find … -print0 | xargs -0.'),
    ('How do I fix “Argument list too long”?', 'The list is bigger than ARG_MAX; use find … -print0 | xargs -0 cmd or find -exec cmd {} +.'),
]

PRACTICE_INTRO = 'Small tasks with exit codes and chaining. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Read a code', stmt='Run ls /etc/hostname and print its exit code.', inp='—',
         code='ls /etc/hostname\necho $?\n', explain='0 = success.'),
    dict(level='easy', title='Only on success', stmt='Create folder notes and print “ok” only if it worked.', inp='—',
         code="mkdir -p notes && echo ok\n", explain='&& waits for success.'),
    dict(level='easy', title='Only on failure', stmt='Try cd /nope (hide the error) and print “no such folder” on failure.', inp='—',
         code="cd /nope 2>/dev/null || echo 'no such folder'\n", explain='|| runs on failure.'),
    dict(level='medium', title='Output in a name', stmt='Print report_<weekday>.txt for 2026-11-06.', inp='2026-11-06',
         code='echo "report_$(date -d 2026-11-06 +%A).txt"\n', explain='$( ) inserts Friday.'),
    dict(level='medium', title='Lines to arguments', stmt='Create x1 x2 x3 from a list using xargs, then list them.', inp='a list',
         code="printf 'x1\\nx2\\nx3\\n' | xargs touch && ls x*\n", explain='xargs touch x1 x2 x3.'),
    dict(level='medium', title='Which code?', stmt='Run a missing command “hello123” and print the code.', inp='—',
         code='hello123 2>/dev/null\necho $?\n', explain='127: not found.'),
    dict(level='business', title='Guarded backup', stmt='Copy data.txt to bak/ only if bak/ can be created; report OK or FAILED.', inp='data.txt exists',
         code="echo d > data.txt\nmkdir -p bak && cp data.txt bak/ && echo OK || echo FAILED\n", explain='Each step depends on the previous one.'),
    dict(level='business', title='Rename with xargs', stmt='Give every .txt file a .bak copy using xargs -I{}.', inp='two .txt files',
         code="touch p.txt q.txt\nls *.txt | xargs -I{} cp {} {}.bak && ls *.bak\n", explain='{} appears twice.'),
]

SCN_INTRO = 'Interview questions about exit codes and chaining, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you know if the last command succeeded?”',
        'A classic shell question.',
        'do you know exit codes?',
        '''<ul>
          <li><code>echo $?</code>: 0 = success, non-zero = failure.</li>
          <li>Better: use it directly: <code>if cmd; then …</code> or <code>cmd &amp;&amp; …</code>.</li>
          <li>Common codes: 1, 2, 126, 127, 130.</li>
        </ul>''', 'saying “if there is no error message it worked” (grep -q prints nothing either way).') +
    scn('Operations · scripts', 'Junior', 'The clean-up that emptied the home folder',
        'A colleague’s script had <code>cd $LOGDIR; rm -rf *</code>. LOGDIR was empty on one server and the home folder was wiped.',
        'do you guard dangerous steps?',
        '''<ol>
          <li>With ;, rm runs even when cd fails or goes somewhere else; empty $LOGDIR means cd goes home.</li>
          <li>Fix: <code>cd "${LOGDIR:?not set}" &amp;&amp; rm -rf ./*</code>, or better <code>rm -rf "${LOGDIR:?}"/*</code> (Lesson 3.3).</li>
          <li>Add <code>set -euo pipefail</code> and test with an empty variable.</li>
        </ol>''', '“add sudo so it doesn’t fail”.') +
    scn('Data platform · ops', 'Mid-level', '200,000 files and “Argument list too long”',
        'A nightly job runs <code>gzip /data/export/*.csv</code> and started failing as the folder grew.',
        'do you know ARG_MAX and xargs?',
        '''<ul>
          <li>The glob expands to more bytes than the kernel’s argument limit (ARG_MAX).</li>
          <li><code>find /data/export -name '*.csv' -print0 | xargs -0 -r -P 4 gzip</code> or <code>find … -exec gzip {} +</code>.</li>
          <li>-P speeds it up; -r avoids errors on empty days; check the exit code.</li>
        </ul>''', 'raising limits or splitting by hand.') +
    scn('Platform · CI', 'Senior', 'The pipeline is green but the release is broken',
        'A CI step runs <code>./build.sh; ./test.sh | tee test.log</code> and always passes.',
        'do you understand how CI reads exit codes?',
        '''<ul>
          <li>The step’s code is tee’s (the last command), so test failures are hidden; ; also ignores build failures.</li>
          <li>Use <code>set -euo pipefail</code>, <code>&amp;&amp;</code> between steps, and fail with distinct exit codes.</li>
          <li>Add a deliberately failing test to prove the pipeline goes red.</li>
        </ul>''', 'reading the log by eye each time.')
) + interview([
    ('What does $? contain?', 'The exit status of the last command (0 = success).'),
    ('Difference between && and ||?', '&& runs the next only on success; || only on failure.'),
    ('What do 126, 127 and 130 mean?', 'Not executable; command not found; killed by Ctrl+C (128+2).'),
    ('What is command substitution?', '$(cmd): the command’s output is inserted into the command line.'),
    ('Why is a && b || c dangerous?', 'c also runs if b fails; it is not a real if/else.'),
    ('How do you pass find results to a command safely?', 'find … -print0 | xargs -0 cmd, or find -exec cmd {} +.'),
    ('How do you stop a script at the first error?', 'set -e (plus -u and -o pipefail), or cmd || exit 1 on each step.'),
], [
    ('RHCSA (EX200)', '“Use input-output redirection” and “conditionally execute code (use of: if, test, [], etc.)”: exit codes and && / || are the base.'),
    ('LFCS', 'Essential commands: chaining, exit codes and xargs with find.'),
    ('CompTIA Linux+', 'Command chaining (;, &&, ||), exit codes, command substitution and xargs.'),
]) + distro('These are POSIX shell features; xargs options differ between GNU and BSD.', [
    ('; && || $? $( )', 'yes', 'yes', 'yes', 'yes'),
    ('xargs -0 -I -n -P -t -p', 'GNU findutils', 'GNU findutils', 'BSD xargs: same main options', 'WSL yes; Git Bash yes'),
    ('xargs -r', 'yes (GNU runs once on empty input without it)', 'yes', 'default behaviour on BSD', 'yes'),
    ('xargs -a FILE', 'yes', 'yes', 'no (use < FILE)', 'yes'),
    ('find -print0', 'yes', 'yes', 'yes', 'yes'),
    ('Code 127 / 126', 'bash', 'bash', 'zsh: same codes', 'yes'),
]) + teaser('6.1', 'Module 5 done: streams, redirection, pipes and chaining. Next, Riya has a 2 GB log and needs every line with “ERROR” or “FATAL”, case-insensitive, with the line number and two lines of context, but not the lines from the health-check URL. One command, with the right options, does it. Which one?')

CHEATSHEET = cheatsheet('chaining, exit codes and xargs', [
    ('Exit codes', [('echo $?', 'last code'), ('rc=$?', 'save it'), ('0 / 1 / 2', 'ok / fail / serious'), ('126 / 127', 'not exec / not found'), ('130 137 141', 'Ctrl+C, kill -9, SIGPIPE')]),
    ('Chaining', [('a ; b', 'always'), ('a && b', 'on success'), ('a || b', 'on failure'), ('a || exit 1', 'stop here'), ('if a; then b; else c; fi', 'real if/else')]),
    ('Grouping', [('{ a; b; } > f', 'one redirect'), ('( cd d && make )', 'subshell'), ('a || { msg; exit 1; }', 'several on failure'), ('"$(cmd)"', 'output inside'), ('$((a+b))', 'arithmetic')]),
    ('xargs', [('… | xargs cmd', 'lines → args'), ('-print0 | xargs -0', 'safe names'), ('-I{} cp {} d/', 'one per item'), ('-n 2 / -P 4', 'batch / parallel'), ('-r · -t · -p', 'empty · show · ask')]),
    ('Safety', [('cd d && rm ./*', 'never ;'), ('"${VAR:?}"', 'stop if empty'), ('set -euo pipefail', 'strict scripts'), ('xargs -t echo rm', 'dry run'), ('exit 3', 'meaningful codes')]),
])

MINDMAP = mindmap('Chaining and xargs', [
    ('$?', 'blue', ['0 = success', '1, 2, 126, 127', '128+N signals']),
    ('; && ||', 'green', ['; always', '&& on success', '|| on failure']),
    ('Traps', 'red', ['a && b || c', 'cd ; rm', '$? overwritten']),
    ('Groups', 'amber', ['{ a; b; }', '( subshell )', '|| { …; exit 1; }']),
    ('$( )', 'violet', ['output inside', 'nests', '"quote it"']),
    ('xargs', 'acc', ['-print0 | -0', '-I{} -n -P', '-r -t -p']),
])

LAB = lab('make a safe maintenance script', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab54 && cd ~/lab54 && rm -rf out old *.txt
mkdir old; touch 'old/a.tmp' 'old/b c.tmp' old/keep.txt''',
    tasks=['Run <code>ls /nope</code> (hide the error) and write its exit code into <code>code.txt</code>.',
           'In one line: create folder <code>out</code> and, only if that worked, write <code>ready</code> into <code>out/status.txt</code>.',
           'Delete every <code>.tmp</code> file in <code>old/</code> with find and xargs, so that names with spaces work too.',
           'Write the text <code>report_2026-11-06</code> into <code>name.txt</code> using <code>$(date -d 2026-11-06 +%F)</code>.'],
    solution='''ls /nope 2>/dev/null; echo $? > code.txt
mkdir -p out && echo ready > out/status.txt
find old -name '*.tmp' -print0 | xargs -0 -r rm
echo "report_$(date -d 2026-11-06 +%F)" > name.txt''',
    check='''cd ~/lab54
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 exit code"        '[ "$(cat code.txt 2>/dev/null)" = 2 ]'
ok "2 guarded chain"    '[ "$(cat out/status.txt 2>/dev/null)" = ready ]'
ok "3 tmp files gone"   '[ -z "$(find old -name "*.tmp" 2>/dev/null)" ] && [ -e old/keep.txt ]'
ok "4 dated name"       '[ "$(cat name.txt 2>/dev/null)" = report_2026-11-06 ]' ''')
