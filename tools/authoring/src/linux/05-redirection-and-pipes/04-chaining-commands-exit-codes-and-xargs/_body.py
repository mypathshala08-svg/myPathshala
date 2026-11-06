import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

HOOK = hook('Riya’s deploy script has three steps: build, copy, restart. One night the build fails, but the script carries on, copies the half-built files to the server and restarts it. The website goes down. Linux had told her the build failed (every command returns an <b>exit code</b>) but her script never listened. Today: how to listen. <code>&amp;&amp;</code> runs the next step only on success, <code>||</code> runs a fallback on failure, <code>$?</code> shows the code, <code>$( )</code> puts one command’s output inside another, and <code>xargs</code> turns a list into arguments.',
    ['read exit codes with <code>$?</code> and know what 0, 1, 2, 126, 127, 130 and 137 mean',
     'chain commands with <code>;</code> (always), <code>&amp;&amp;</code> (on success) and <code>||</code> (on failure), and avoid the <code>a &amp;&amp; b || c</code> trap',
     'insert a command’s output into another command with <code>$( )</code>, and group commands with <code>{ }</code> and <code>( )</code>',
     'turn lines into arguments with <code>xargs</code>, safely (<code>-0</code>, <code>-I{}</code>, <code>-n</code>, <code>-r</code>, <code>-P</code>, <code>-p</code>)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the deploy that never stopped'),
    ('decide', 'Which operator when?', 2, 'the quick chart'),
    ('definition', 'What chaining is', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each operator, by field', 18, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each code means'),
    ('animation', 'See it happen', 4, 'success and failure paths'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which operator? (decide in 5 seconds)', [
    ('Run several commands, one after another, no matter what', 'cmd1 ; cmd2', 'also: a new line'),
    ('Run the next step only if this one worked', 'cmd1 && cmd2', 'mkdir d && cd d'),
    ('Do something only if this one failed', 'cmd1 || cmd2', 'a fallback or an error message'),
    ('Did the last command work?', 'echo $?', '0 = success, anything else = failure'),
    ('Use a command’s output inside another command', '$(cmd)', 'backup_$(date +%F).tar.gz'),
    ('Several commands, one redirection or one condition', '{ cmd1; cmd2; }', '( … ) = in a subshell'),
    ('Turn a list of lines into arguments', '… | xargs cmd', 'find … -print0 | xargs -0 rm'),
    ('One command per item, with the item in the middle', '… | xargs -I{} cmd {} …', 'xargs -I{} cp {} /backup/'),
    ('Stop a script at the first error', 'set -e  (Lesson 12.6)', 'or cmd || exit 1 per step'),
])

cmap = concept_map(
    [('5.1', 'Standard streams', 'the three streams'), ('5.2', 'Redirection', '> /dev/null 2>&1 for quiet checks'), ('5.3', 'Pipes', 'PIPESTATUS and pipefail')],
    ['exit codes: $?, 0 vs non-zero, the common codes', '; && || and how they combine; the a && b || c trap', 'grouping: { } and ( ), if cmd; then', 'command substitution $( ) (and old `backticks`)', 'xargs: -0, -I{}, -n, -r, -P, -p, -t'],
    [('7.1', 'find', 'find … -print0 | xargs -0'), ('12.5', 'Shell scripts', 'exit codes in your own scripts'), ('12.6', 'Safer scripts', 'set -e, set -u, pipefail'), ('13.2', 'find + xargs + -exec', 'bulk changes across files')],
    'Exit codes are how Linux commands say “it worked” or “it failed”. Chaining is how you make the next step depend on that answer.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ ./build.sh ; ./copy.sh ; ./restart.sh', ('build: ERROR missing module', 'err'), ('copied 212 files', 'out'), ('service restarted', 'out'), ('# site is DOWN', 'err'), '$ ./build.sh && ./copy.sh && ./restart.sh', ('build: ERROR missing module', 'err'), ('# stopped: site still up', 'acc')], title='riya@deploy: ~', size=7.0, step=15)
      + t(352, 36, 'Every command answers:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• exit code 0 = it worked', '• 1–255 = it failed', '• ; ignores the answer', '• && continues only on 0', '• || acts on failure'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The deploy that never stopped</h2>
  <div class="story">
''' + puzzle('Riya writes <code>mkdir /root/x &amp;&amp; echo "created" || echo "failed"</code> as a normal user. Then she writes <code>true &amp;&amp; false || echo "failed"</code>. Which lines print “failed”, and is <code>a &amp;&amp; b || c</code> really the same as if-then-else?') + '''
    <p class="narration">Friday night. Riya’s deploy script ran build, copy and restart, separated by semicolons. The build failed, the rest ran anyway, and the site went down.</p>
''' + scene('A terminal: build ; copy ; restart runs every step even after the build error and the site goes down; build && copy && restart stops after the error and the site stays up.', sc,
            'The semicolon ignores failures; <tspan font-weight="700" class="s-acc">&amp;&amp;</tspan> listens to them.') + '''
A> Every command ends with a number, its <b>exit code</b>. 0 means success; anything else means failure. You can see it with <code>echo $?</code>.
R> And my semicolons ignored it?
K> Exactly. <code>;</code> means “then run the next one, whatever happened”. <code>&amp;&amp;</code> means “only if that worked”. One character would have saved the site.
A> Today: exit codes, <code>;</code> <code>&amp;&amp;</code> <code>||</code>, <code>$( )</code> to use output inside commands, and <code>xargs</code> to turn lists into arguments: the glue of every Linux script.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="A railway junction: a train reaches a signal; green (exit 0) sends it on the && track, red (non-zero) sends it on the || track; a semicolon track ignores the signal.">'
       + label_box(20, 70, 120, 56, ['a command', 'finishes'], 'card', 9)
       + label_box(190, 70, 110, 56, ['signal', 'exit code'], 'amber', 9)
       + label_box(360, 14, 260, 46, ['0 (green) → && track', 'run the next step'], 'green', 8.8)
       + label_box(360, 76, 260, 46, ['1–255 (red) → || track', 'run the fallback'], 'red', 8.8)
       + label_box(360, 138, 260, 46, ['; track', 'ignores the signal, always goes on'], 'card', 8.8)
       + arrow(142, 98, 188, 98) + arrow(302, 90, 358, 40) + arrow(302, 98, 358, 99) + arrow(302, 108, 358, 160)
       + t(320, 206, 'The exit code is the signal; the operator decides which track to take.', 9.6, 'acc', bold=True)
       + '<text x="632" y="216" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Chaining at four depths', [
    ('v', 'No jargon: a railway signal', '      <p>Think of trains and signals.</p>' + pic + '''
      <ul>
        <li>When a command finishes, it shows a signal: green (0, worked) or red (any other number, failed).</li>
        <li><code>&amp;&amp;</code> is a track that is only used on green; <code>||</code> only on red.</li>
        <li><code>;</code> is a track that ignores the signal completely.</li>
        <li><code>xargs</code> is a loading crane: it takes a list of items and loads them onto a command as arguments.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>echo $?</code> right after a command: 0 = success.</li>
        <li><code>sudo apt update &amp;&amp; sudo apt upgrade -y</code>: upgrade only if the update worked.</li>
        <li><code>mkdir -p logs &amp;&amp; cd logs</code>: enter the folder only if it was created.</li>
        <li><code>ping -c1 server || echo "server down"</code>: a message only on failure.</li>
        <li><code>echo "Today is $(date +%A)"</code>: a command’s output inside text.</li>
      </ul>'''),
    ('i', 'Codes, combinations and traps', '''      <ul>
        <li>Common codes: 0 success; 1 general failure (also grep “no match”); 2 misuse or serious trouble (bash syntax error, ls/grep cannot access a file); 126 not executable; 127 command not found; 128+N killed by signal N: 130 = Ctrl+C, 137 = kill -9, 141 = SIGPIPE; 124 = timeout.</li>
        <li><code>&amp;&amp;</code> and <code>||</code> have <b>equal</b> priority and are read left to right. <code>a &amp;&amp; b || c</code> runs c if a fails <b>or</b> if b fails, so it is not a true if-then-else.</li>
        <li><code>{ a; b; }</code> groups in the current shell (spaces and the final ; are required); <code>( a; b )</code> runs in a subshell, so <code>cd</code> and variables inside do not leak out.</li>
        <li><code>$(cmd)</code> runs cmd and replaces itself with the output, minus trailing newlines. Quote it: <code>"$(cmd)"</code>. Backticks <code>`cmd`</code> are the old form: hard to nest and read.</li>
        <li><code>xargs</code> reads words from stdin and runs the command with them as arguments. Names with spaces break it unless you use <code>-print0 | xargs -0</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: wait(), status bytes and ARG_MAX', '''      <ul>
        <li>A process ends with <code>exit(n)</code>; the parent collects it with <code>wait()</code>. Only the low 8 bits are kept, so codes are 0–255: <code>exit 256</code> gives 0 and <code>exit 300</code> gives 44 (real runs).</li>
        <li>If a signal kills the process, bash reports 128 + the signal number. <code>kill -l 9</code> shows the name (KILL).</li>
        <li><code>$( )</code> forks a subshell with its stdout connected to a pipe, reads everything, waits, and strips trailing newlines. Its exit status becomes <code>$?</code> in <code>x=$(cmd)</code>.</li>
        <li>The kernel limits the total size of arguments (<code>getconf ARG_MAX</code>, about 2 MB): <code>rm $(find …)</code> fails with “Argument list too long” on huge lists. <code>xargs</code> splits the list into several command runs automatically.</li>
        <li><code>xargs -P N</code> runs N commands in parallel; <code>find -exec … {} +</code> is the built-in alternative to xargs.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Exit codes, chaining, $( ) and xargs</h2>
''' + def_block(
    'Every command returns an <b>exit status</b> (exit code), an integer 0–255, when it ends: 0 means success, any other value means failure. The shell stores it in <code>$?</code>. <b>Command lists</b> join commands: <code>;</code> runs them in sequence, <code>&amp;&amp;</code> runs the next only if the previous succeeded (AND list), <code>||</code> only if it failed (OR list). <b>Command substitution</b> <code>$(cmd)</code> replaces itself with cmd’s output. <code>xargs</code> builds and runs command lines from items read on standard input.',
    'Each command answers “worked” (0) or “failed” (not 0); ; && || decide what runs next; $( ) pastes output; xargs turns lines into arguments.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Exit status / code', f'The number a command returns: 0 = success. {gl("exit-status", "Glossary →")}'),
    ('$?', 'The exit status of the last command.'),
    ('AND list / OR list', '<code>a &amp;&amp; b</code> / <code>a || b</code>.'),
    ('Command substitution', f'<code>$(cmd)</code>: the output becomes part of the command line. {gl("command-substitution", "Glossary →")}'),
    ('Subshell', f'<code>( … )</code>: a child copy of the shell. {gl("subshell", "Glossary →")}'),
    ('xargs', f'Builds arguments from stdin. {gl("xargs", "Glossary →")}'),
    ('Argument', 'A word given to a command after its name: <code>rm a.txt</code>.'),
    ('Signal', f'A message to a process, e.g. SIGINT (Ctrl+C). {gl("signal", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('&&', 'logical AND', 'From C: true only if both sides are true.'),
    ('||', 'logical OR', 'From C: the second side runs only if the first is false.'),
    ('$?', '“what was the result?”', 'Shell special parameter.'),
    ('$( )', 'command substitution', 'POSIX form; replaces the older backticks.'),
    ('xargs', 'extended arguments', 'It extends a command with arguments from stdin.'),
    ('true / false', 'commands that only return 0 / 1', 'Handy for tests.'),
    ('exit', 'leave the script', '<code>exit 3</code> returns 3 to the caller.'),
    ('-I{}', 'insert here', 'Replace {} with each item.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Last result', '<code>echo $?</code> (0 = OK)'),
    ('Next only on success', '<code>a &amp;&amp; b</code>'),
    ('Fallback on failure', '<code>a || b</code>'),
    ('Always', '<code>a ; b</code>'),
    ('Output inside a command', '<code>"$(cmd)"</code>'),
    ('Safe xargs', '<code>find … -print0 | xargs -0 cmd</code>'),
]) + '\n' + lv + didyou('In the shell, 0 means <b>true</b> (success) and non-zero means false, the opposite of most programming languages, where 0 is false. The reason: there is only one way to succeed but many ways to fail, so the non-zero numbers are free to say <i>which</i> failure happened.') + '''
EXAM> “What does $? contain, and what is the difference between ;, &amp;&amp; and ||?” → $? = exit status of the last command (0 success). ; runs the next always; &amp;&amp; only if the previous returned 0; || only if it returned non-zero. Example: mkdir d &amp;&amp; cd d; ping -c1 h || echo down.
''' + qc('<code>grep -q root /etc/passwd</code> prints nothing. How do you know if it found root?', 'Check its exit code: <code>echo $?</code> prints 0 if it found a match, 1 if not, 2 on error. Or use it directly: <code>grep -q root /etc/passwd &amp;&amp; echo found</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Exit codes you will meet (all recorded on our build machine)</h2>
''' + table(['Code', 'Meaning', 'Real example that produced it'], [
    ['<b>0</b>', 'success', '<code>ls /etc</code>, <code>test 5 -gt 3</code>, <code>grep</code> found a match'],
    ['<b>1</b>', 'general failure', '<code>cd /nope</code>, <code>grep -q zz file</code> (no match), <code>false</code>'],
    ['<b>2</b>', 'misuse / serious trouble', '<code>ls /nope</code>, <code>grep x /nofile</code>, a bash syntax error'],
    ['<b>124</b>', 'timeout stopped the command', '<code>timeout 1 sleep 3</code>'],
    ['<b>126</b>', 'found but not executable', '<code>./s.sh</code> without chmod +x'],
    ['<b>127</b>', 'command not found', 'a typo: <code>nosuch</code>'],
    ['<b>128+N</b>', 'killed by signal N', '130 = Ctrl+C (2), 137 = kill -9 (9), 141 = SIGPIPE (13), 143 = kill (15)'],
    ['<b>0–255 only</b>', 'values wrap around (modulo 256)', '<code>exit 256</code> → 0, <code>exit 300</code> → 44, <code>exit -1</code> → 255'],
], minw=620) + mistake('“Most commands return 1 if they fail.”   ·   “2 = misuse of builtins, e.g. cd to a non-existent directory.”   ·   “255 = exit status out of range.”',
                       'Failures can be any of 1–255 (ls and grep use 2 for errors; 126, 127, 128+N have fixed meanings) · cd to a missing directory returns 1 · out-of-range values wrap: exit 300 gives 44; 255 is what exit -1 gives',
                       'These three lines are common in class notes and online. Real runs on bash 5.2 give the values in the table above. Check codes with <code>echo $?</code>, and read each command’s man page (section EXIT STATUS).') + '''
  <h3>The three operators side by side</h3>
''' + table(['', '<code>a ; b</code>', '<code>a &amp;&amp; b</code>', '<code>a || b</code>'], [
    ['a succeeds (0)', 'b runs', 'b runs', 'b is skipped'],
    ['a fails (≠0)', 'b runs', 'b is skipped', 'b runs'],
    ['$? afterwards', 'b’s status', 'a’s (if failed) or b’s', 'a’s (if 0) or b’s'],
    ['Use for', 'independent steps', 'dependent steps', 'fallbacks, error messages'],
], minw=520) + qc('What does <code>cd /nope ; ls</code> list, and what does <code>cd /nope &amp;&amp; ls</code> list?', 'With ; the cd fails but ls still runs and lists the <b>current</b> folder (dangerous with rm!). With &amp;&amp; nothing is listed.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each operator explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 (bash 5.2, GNU findutils 4.9 xargs) as a normal user without sudo.</p>
''' + cmdcard_u(['any time you need to know whether a command worked', 'scripts that must react to failure', 'commands that print nothing (grep -q, test, cmp -s)'],
               ['reading $? after another command ran (it is overwritten at once: save it first)', 'guessing: read the man page EXIT STATUS section'])(
    'status', '$?', 'exit status of the last command',
    'A special variable holding the exit code of the most recent command: 0 = success, 1–255 = failure. Every command, including <code>echo</code> and <code>[ … ]</code>, changes it.',
    'command; echo $?   ·   rc=$?   ·   exit N  (in your scripts)', 'safe',
    [('echo $?', 'show the last code', 'quick check'),
     ('rc=$?', 'save it before it changes', 'scripts'),
     ('exit N', 'end your script with code N', 'tell the caller'),
     ('return N', 'end a function with code N', 'functions'),
     ('true / false', 'commands that return 0 / 1', 'tests, loops'),
     ('if cmd; then', 'branch on the code (no $? needed)', 'clean scripts'),
     ('kill -l 137', 'name of a signal code', 'what killed it?')],
    dict(cmd='ls /etc > /dev/null; echo "ls /etc: $?"\nls /nope 2> /dev/null; echo "ls /nope: $?"\ncd /nope 2> /dev/null; echo "cd /nope: $?"\nnosuchcmd 2> /dev/null; echo "typo: $?"', note='Four commands, four codes: 0, 2, 1, 127.'),
    [('sys', [
        dict(situation='Is a user in the system? grep prints nothing with -q; only the code answers.', cmd="grep -q '^riya:' /etc/passwd; echo \"riya: $?\"\ngrep -q '^ghost:' /etc/passwd; echo \"ghost: $?\"",
             why='0 = found, 1 = not found, 2 = error (e.g. file missing). Scripts branch on this.'),
        dict(situation='What killed my process?', cmd="sleep 30 & pid=$!; kill -9 $pid; wait $pid; rc=$?\necho \"exit code $rc = signal $((rc-128)) = $(kill -l $((rc-128)))\"",
             why='128 + 9 = 137: killed with SIGKILL, often the OOM killer when memory runs out (Lesson 18.4).')]),
     ('dev', [
        dict(situation='Your script returns a meaningful code to whoever runs it (CI, cron, another script).', cmd="printf '#!/bin/bash\\n[ -f \"$1\" ] || { echo \"missing: $1\" >&2; exit 3; }\\necho ok\\n' > check.sh; chmod +x check.sh\n./check.sh /etc/hostname; echo \"code $?\"\n./check.sh /nope; echo \"code $?\"",
             why='Pick codes and document them (3 = missing input). CI marks a job red on any non-zero code.')]),
     ('devops', [
        dict(situation='timeout tells you whether a command hung.', cmd="timeout 1 sleep 3; rc=$?\n[ $rc -eq 124 ] && echo 'timed out after 1 s'",
             why='124 is timeout’s own code. Save $? into a variable first; the [ ] test would overwrite it.')]),
     ('qa', [
        dict(situation='Are two output files identical? cmp -s prints nothing.', cmd="echo 42 > expected.txt; echo 42 > got.txt; echo 41 > bad.txt\ncmp -s expected.txt got.txt; echo \"same: $?\"\ncmp -s expected.txt bad.txt; echo \"different: $?\"",
             why='Test frameworks use exit codes the same way: 0 pass, non-zero fail.')]),
    ],
    anat=anatomy([('ls /nope', 'cmd', 'any command'), (';', 'opt', 'then'), ('echo $?', 'arg', 'show its exit code')], 'Read $? immediately: the next command replaces it.')
) + cmdcard_u(['steps that depend on each other: build && deploy', 'creating then entering: mkdir d && cd d', 'one-line conditions: test && action, test || message'],
               ['independent steps that should all run (use ; or new lines)', 'real if/else logic with two branches (use if … then … else)'])(
    'andor', '&&  ·  ||  ·  ;', 'AND, OR and sequence',
    '<code>a &amp;&amp; b</code> runs b only if a returned 0. <code>a || b</code> runs b only if a failed. <code>a ; b</code> runs both, always. They can be chained: <code>a &amp;&amp; b &amp;&amp; c</code> stops at the first failure.',
    'cmd1 && cmd2   ·   cmd1 || cmd2   ·   cmd1 ; cmd2   ·   cmd1 && cmd2 || cmd3', 'safe',
    [('a && b', 'b only if a succeeded', 'dependent steps'),
     ('a && b && c', 'stop at the first failure', 'build pipelines'),
     ('a || b', 'b only if a failed', 'fallbacks, messages'),
     ('a || exit 1', 'stop the script on failure', 'guard a step'),
     ('a ; b', 'always both', 'independent steps'),
     ('[ -f f ] && cat f', 'test, then act', 'one-line if'),
     ('a && b || c', '<b>not</b> if/else: c also runs if b fails', 'only when b cannot fail')],
    dict(cmd="mkdir -p reports && echo 'created reports'\nmkdir /root/x 2> /dev/null && echo 'created x' || echo 'could not create x'\ncd /nope 2> /dev/null ; echo 'the ; ran anyway'", note='The second line is the first part of the puzzle: mkdir failed (no permission), so the || branch ran.'),
    [('sys', [
        dict(situation='Update the package list and upgrade only if the update worked (the real command).', cmd='sudo apt update && sudo apt upgrade -y',
             typical='Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease\nReading package lists... Done\n…\n0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.',
             why='If apt update fails (no network), upgrading from an old list makes no sense, so && stops there.'),
        dict(situation='Change ownership, then permissions, as one unit (from your notes).', cmd="touch file.txt\nchown riya:riya file.txt && chmod 740 file.txt && stat -c '%U:%G %a' file.txt",
             why='chmod runs only if chown worked. (Changing to another user would need sudo, Lesson 9.3.)')]),
     ('devops', [
        dict(situation='The deploy chain: each step only after the previous one succeeded.', cmd="build()   { echo 'build ok'; }\ntest_()   { echo 'tests FAILED'; return 1; }\ndeploy()  { echo 'deployed!'; }\nbuild && test_ && deploy || echo 'pipeline stopped, nothing deployed'",
             why='Like a CI pipeline: the first failure stops the chain. The final || reports it.'),
        dict(situation='Check that a server answers, with a message on failure.', cmd="curl -s -o /dev/null --max-time 3 http://localhost:9 || echo 'ALERT: service on port 9 is down'",
             why='Port 9 has no service here, so curl fails and the alert prints.')]),
     ('dev', [
        dict(situation='Create a folder and work inside it, but never in the wrong place.', cmd="mkdir -p build/out && cd build/out && pwd",
             why='If mkdir fails, cd is skipped; if cd fails, nothing runs in the wrong folder.')]),
     ('sec', [
        dict(situation='Why ; is dangerous with cd and rm (demo with echo instead of rm).', cmd="cd /no/such/dir 2> /dev/null ; echo \"rm -rf * would now run in: $(pwd)\"\ncd /no/such/dir 2> /dev/null && echo 'never printed'",
             why='With ; the delete runs in whatever folder you happen to be in. Always: <code>cd dir &amp;&amp; rm -rf ./*</code>, or better <code>rm -rf dir/*</code>.', expect='any')]),
     ('qa', [
        dict(situation='The a && b || c trap, shown for real.', cmd="true && false || echo 'c ran even though a succeeded (b failed)'\nif true; then false; else echo 'never printed'; fi; echo \"if/else: else did not run\"",
             why='In a &amp;&amp; b || c, c runs when a fails <b>or</b> b fails. Use a real if/then/else when b can fail.')]),
    ]
) + mistake('cd /var/app/tmp ; rm -rf *', 'cd /var/app/tmp && rm -rf ./*    ·   or simply   rm -rf /var/app/tmp/*',
            'If the cd fails (typo, folder missing), ; still runs rm in the <b>current</b> folder, possibly your home or /. This has deleted real servers.') + cmdcard_u(['putting a command’s output into a variable, a file name or a message', 'dates, counts and paths inside other commands', 'nested calls (each $( ) inside another)'],
               ['huge outputs (the whole output is held in memory)', 'lists of file names with spaces into for loops (use while read or find -print0)'])(
    'subst', '$( )', 'command substitution',
    'Runs the command inside and replaces itself with its standard output, with trailing newlines removed. Quote it (<code>"$(cmd)"</code>) to keep spaces. Backticks <code>`cmd`</code> do the same but cannot nest easily.',
    'var=$(command)   ·   "text $(command) text"   ·   cmd "$(other)"', 'safe',
    [('x=$(cmd)', 'output into a variable', 'store results'),
     ('"…$(cmd)…"', 'output inside a string', 'messages, names'),
     ('$(cmd1 $(cmd2))', 'nest', 'compose'),
     ('$(< file)', 'file contents (bash, no cat)', 'read a small file'),
     ('$((1 + 2))', '<b>arithmetic</b>, not a command', 'calculations'),
     ('`cmd`', 'old form of $(cmd)', 'reading old scripts'),
     ('x=$(cmd) || …', '$? is the command’s status', 'check it')],
    dict(cmd='echo "Today is $(date -d 2026-11-06 +%A)"\nn=$(ls /etc | wc -l); echo "/etc has $n entries"\necho "nested: $(basename $(dirname /var/log/syslog))"', note='$( ) runs first; its output is pasted into the command line.'),
    [('dba', [
        dict(situation='A dated backup file name.', cmd='touch "shop_$(date -d 2026-11-06 +%F).sql.gz" && ls shop_*',
             why='The standard naming pattern for dumps: sortable and unique per day.')]),
     ('sys', [
        dict(situation='Kernel version and uptime in a one-line report.', cmd='echo "$(hostname): kernel $(uname -r | cut -d- -f1), $(nproc) CPUs"',
             why='Three commands inside one message. Monitoring scripts are full of this.')]),
     ('data', [
        dict(situation='Count rows and compute a percentage.', cmd="printf 'ok\\nok\\nfail\\nok\\n' > runs.txt\ntotal=$(wc -l < runs.txt); fails=$(grep -c fail runs.txt)\necho \"failure rate: $(( fails * 100 / total ))%\"",
             why='$( ) for commands, $(( )) for arithmetic: two different things that look alike.')]),
     ('dev', [
        dict(situation='$( ) removes trailing newlines (a common surprise).', cmd="x=$(printf 'abc\\n\\n\\n'); echo \"[$x]\"\necho \"[$(printf '  padded  ')]\"",
             why='Newlines at the end are stripped; spaces are kept when you quote.'),
        dict(situation='Capture output and check the status in one line.', cmd="if out=$(grep -c root /etc/passwd); then echo \"found $out line(s)\"; fi",
             why='The assignment’s status is the command’s status, so if works directly.')]),
    ]
) + cmdcard_u(['one redirection or one && for several commands', 'trying something in another folder without moving yourself (( ))', 'a block that runs only on failure: || { echo …; exit 1; }'],
               ['big logic: write a function or a script instead'])(
    'group', '{ }  ·  ( )', 'grouping commands',
    '<code>{ a; b; }</code> runs the commands in the current shell as one unit. <code>( a; b )</code> runs them in a subshell: <code>cd</code>, variables and <code>exit</code> inside do not affect your shell.',
    '{ cmd1; cmd2; }   ·   ( cmd1; cmd2 )   ·   cmd || { echo "failed" >&2; exit 1; }', 'safe',
    [('{ a; b; } > f', 'one redirection for both', 'reports'),
     ('a || { msg; exit 1; }', 'several actions on failure', 'guards in scripts'),
     ('( cd dir && cmd )', 'run elsewhere, come back automatically', 'builds'),
     ('( set -e; … )', 'strict mode for a block only', 'risky steps'),
     ('{ and } need spaces; last ; required', 'syntax rule', 'avoid errors')],
    dict(cmd="{ echo 'header'; date -d 2026-11-06 +%F; } > report.txt; cat report.txt\n( cd /tmp && echo \"inside: $(pwd)\" ); echo \"outside: $(pwd)\"", note='The subshell’s cd did not move us.'),
    [('devops', [
        dict(situation='Stop the script with a clear message if a required file is missing.', cmd="cfg=app.conf\n[ -f \"$cfg\" ] || { echo \"error: $cfg missing\" >&2; echo 'would exit 1 here'; }",
             why='The braces let one || run two commands. (A real script would end with exit 1.)')]),
     ('dev', [
        dict(situation='Build in a sub-folder without changing your own location.', cmd="mkdir -p proj/src && echo 'print(1)' > proj/src/main.py\n( cd proj/src && python3 main.py ) && echo \"still in $(basename \"$PWD\")\"",
             why='The subshell keeps your terminal where it was, even if the build fails half-way.')]),
    ]
) + cmdcard_u(['many items from a pipe must become arguments (rm, cp, grep, chmod)', 'very long lists (xargs splits them to avoid “Argument list too long”)', 'parallel work (-P)'],
               ['names that may contain spaces or newlines, unless you use -print0 | xargs -0', 'commands that read stdin themselves (just pipe into them)'])(
    'xargs', 'xargs', 'build command lines from stdin',
    'Reads items (words or lines) from stdin and runs a command with them as arguments, as many as fit per run. <code>-0</code> reads NUL-separated items (from <code>find -print0</code>), <code>-I{}</code> places each item where {} is, <code>-n N</code> gives N per run, <code>-r</code> skips the run if there is no input, <code>-P N</code> runs N at once, <code>-p</code> asks first, <code>-t</code> prints each command.',
    "… | xargs [-0] [-r] [-n N] [-P N] [-I{}] [-t|-p] command [args]", 'change',
    [('| xargs cmd', 'all items as arguments to cmd', 'rm, grep, wc'),
     ('-print0 | xargs -0', 'NUL-separated: safe for any file name', 'always with find'),
     ('-I{}', 'one run per item, {} = the item', 'cp {} dest/, mv {} {}.bak'),
     ('-n N', 'N items per run', 'batching'),
     ('-r', 'do not run if input is empty', 'avoid “rm: missing operand”'),
     ('-P N', 'N runs in parallel', 'compress, download'),
     ('-t / -p', 'print / confirm each command', 'check before deleting'),
     ('-d \'\\n\'', 'one item per line (spaces kept)', 'line lists')],
    dict(cmd="printf 'a.txt\\nb.txt\\nc.txt\\n' > list.txt\ntouch $(cat list.txt)\ncat list.txt | xargs -t wc -c", note='-t printed the command xargs built: one wc with three arguments.'),
    [('sys', [
        dict(situation='Delete old .tmp files found by find, safely (names may contain spaces).', cmd="touch 'old report.tmp' a.tmp keep.txt\nfind . -name '*.tmp' -print0 | xargs -0 -r rm -v",
             why='-print0 / -0 keep “old report.tmp” as one name; -r does nothing if find found nothing. (find -delete or -exec rm {} + also work, Lesson 13.2.)'),
        dict(situation='Why plain xargs breaks on spaces (real failure).', cmd="touch 'my file.txt'\nls *.txt | xargs rm",
             why='xargs split “my file.txt” into “my” and “file.txt”. Use find -print0 | xargs -0.', expect='any')]),
     ('devops', [
        dict(situation='Back up each config file with a .bak copy.', cmd="touch nginx.conf app.conf\nls *.conf | xargs -I{} cp {} {}.bak\nls *.bak",
             why='-I{} runs one cp per file with the name in two places.'),
        dict(situation='Compress logs in parallel, 2 at a time.', cmd="for d in 1 2 3 4; do seq 1 20000 > app$d.log; done\nls app*.log | xargs -P 2 -n 1 gzip\nls app*.log.gz | wc -l",
             why='-P 2 uses two CPU cores; -n 1 gives each gzip one file.')]),
     ('dev', [
        dict(situation='Search for TODO in all Python files listed by find.', cmd="mkdir -p pkg; printf 'x=1  # TODO fix\\n' > pkg/a.py; printf 'y=2\\n' > pkg/b.py\nfind pkg -name '*.py' -print0 | xargs -0 grep -n TODO",
             why='grep gets all file names as arguments and prints file:line for each match.')]),
     ('data', [
        dict(situation='Count lines of many CSV files, in batches of 2.', cmd="seq 1 4 > jan.csv; seq 1 6 > feb.csv; seq 1 3 > mar.csv\nls *.csv | xargs -n 2 wc -l",
             why='-n 2 shows how xargs splits a list into several runs (each with its own total).')]),
     ('sec', [
        dict(situation='Ask before each risky action (-p), here answering “n” automatically.', cmd="ls *.key | xargs -p -n 1 rm",
             typical='rm s1.key ?...n\nrm s2.key ?...y\n(only s2.key was deleted)',
             why='-p prints each command and waits for y. With no answer nothing is deleted. Use it when deleting by pattern.')]),
    ]
) + undo('Chaining decides what runs; a wrong operator can run the wrong thing.', [
    ('; ran a step after a failure:', 'use &amp;&amp; between dependent steps, or <code>set -e</code> in scripts (Lesson 12.6).'),
    ('xargs deleted the wrong files:', 'there is no undo for rm. Always run the list first without the command, or with <code>xargs -t echo</code> / <code>-p</code>.'),
    ('xargs split names with spaces:', 'use <code>find … -print0 | xargs -0</code>, or <code>-d \'\\n\'</code>.'),
    ('$? was overwritten:', 'save it immediately: <code>cmd; rc=$?</code>.'),
    ('a && b || c ran c unexpectedly:', 'b failed. Use if/then/else.'),
]) + errors('Errors and codes students see most. Each was really produced on our build machine.', [
    dict(cmd='mkdir reports; mkdir reports', meaning='The second mkdir fails because the folder exists (code 1). With ; the script carries on anyway.', fix='<code>mkdir -p</code> (no error if it exists), or <code>&amp;&amp;</code> to stop.'),
    dict(cmd="echo '' | xargs rm", meaning='Empty input, but GNU xargs still ran rm once, with no file: “missing operand”. 123 is xargs’ code for “a command it ran failed”.', fix='<code>xargs -r</code> skips the run when there is no input.'),
    dict(cmd='touch s.sh; ./s.sh', meaning='The file exists but is not executable: 126.', fix='<code>chmod +x s.sh</code> (Lesson 12.5) or <code>bash s.sh</code>.'),
    dict(cmd='lss', meaning='Command not found: 127. A typo, or the program is not installed / not in PATH.', fix='Check the spelling; <code>type cmd</code>; install it (Lesson 14).'),
    dict(cmd='{ echo a; echo b }', meaning='The closing } is read as an argument of echo, so bash waits for the real end and hits end of input: syntax error, code 2.', fix='A ; (or newline) before }: <code>{ echo a; echo b; }</code>.'),
    dict(cmd='timeout 1 sleep 5', meaning='timeout stopped the command after 1 s: 124.', fix='Not a bug in your code; handle 124 in scripts.'),
]) + qc('Write one line: create the folder <code>backup</code>, copy <code>db.sql</code> into it, and print “backup failed” if either step fails.', '<code>mkdir -p backup &amp;&amp; cp db.sql backup/ || echo "backup failed"</code> (here the || is fine: echo cannot fail).') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def rail(k, ok, note, tone):
    names_ = ['build', 'test', 'deploy']
    o = ''
    for i, nm in enumerate(names_):
        tone_i = 'card'
        if i < k:
            tone_i = 'green'
        elif i == k:
            tone_i = 'green' if ok else 'red'
        o += label_box(14 + i * 118, 24, 96, 46, [nm, ('exit 0' if (i < k or (i == k and ok)) else ('exit 1' if i == k else 'not run'))], tone_i, 8.6)
    o += arrow(112, 47, 130, 47) + arrow(230, 47, 248, 47)
    o += t(64, 90, '&&', 10, 'acc', bold=True) + t(182, 90, '&&', 10, 'acc', bold=True)
    return o + t(180, 130, note, 8.8, tone, bold=True)
frames = [rail(0, True, 'build succeeds: exit 0, so && lets test run.', 'green'),
          rail(1, False, 'test fails: exit 1.', 'red'),
          rail(1, False, '&& sees the failure: deploy is skipped.', 'red'),
          rail(1, False, '|| echo "stopped" prints the alert.', 'amber')]
s1 = anim_one('Animated chain', 'build && test && deploy || echo "stopped"',
              'Follow the exit codes along a deploy chain where the tests fail.',
              'Success and failure paths', 'Three boxes build, test, deploy; build turns green, test turns red, deploy stays grey, then the fallback message appears.', frames,
              ['build returns 0.', 'test returns 1.', 'The second && skips deploy.', 'The final || runs the alert.'], hid='scenario-chain')

def xbox(items, cmd, note, tone):
    o = label_box(14, 18, 110, 96, ['stdin'] + items, 'card', 8)
    o += label_box(150, 46, 60, 36, ['xargs'], 'amber', 9) + arrow(126, 64, 148, 64) + arrow(212, 64, 228, 64)
    o += label_box(230, 30, 120, 68, ['runs:'] + cmd, 'green', 7.6)
    return o + t(180, 140, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ["$ find . -name '*.tmp'", ('./a.tmp', 'out'), ('./old report.tmp', 'out')], title='riya@laptop', size=7.8) + cap('Two files; one name has a space.', '', 'card', y=150, h=34),
       term(14, 16, 332, 116, ["$ find . -name '*.tmp' | xargs rm", ("rm: cannot remove './old': No such…", 'err'), ("rm: cannot remove 'report.tmp': …", 'err')], title='riya@laptop', size=7.4) + cap('Plain xargs splits at the space.', '', 'red', y=150, h=34),
       term(14, 16, 332, 116, ["$ find . -name '*.tmp' -print0 |", '  xargs -0 rm -v', ("removed './a.tmp'", 'acc'), ("removed './old report.tmp'", 'acc')], title='riya@laptop', size=7.4) + cap('-print0 | xargs -0: names stay whole.', '', 'green', y=150, h=34)]
behind = [xbox(['./a.tmp', './old report.tmp'], ['(nothing yet)'], 'find writes one name per line.', 'violet'),
          xbox(['./a.tmp', './old', 'report.tmp'], ['rm ./a.tmp ./old', '   report.tmp'], 'Split at spaces: 3 “names”, 2 wrong.', 'red'),
          xbox(['./a.tmp\\0', './old report.tmp\\0'], ['rm -v ./a.tmp', '  "./old report.tmp"'], 'Split at NUL bytes: exactly 2 names.', 'green')]
two = anim_two('Why find needs -print0 with xargs', 'How xargs splits its input',
               'Three terminals: find lists two tmp files, one with a space; plain xargs rm fails on the split name; -print0 with xargs -0 removes both.',
               'A box showing stdin items, xargs, and the command it builds, first split at spaces (wrong), then at NUL bytes (right).', see, behind,
               ['find lists the files.', 'Plain xargs: errors.', 'NUL-separated: both removed.'],
               ['Items arrive on stdin.', 'By default xargs splits at spaces and newlines.', 'With -0 it splits only at NUL, which never occurs in file names.'])

dx = dissect('Layer by layer: backup_$(date +%F).tar.gz && echo done || echo failed',
    'How the shell evaluates one real line. Each layer has a real command and output from our build machine.', [
    dict(key='subst', name='$( ) first', sub='date runs',
         why='The name must exist before tar starts.',
         how='bash runs date in a subshell and reads its output.',
         impl='fork + pipe + wait; trailing newline removed.', used='Every dated name.',
         cmd='echo "backup_$(date -d 2026-11-06 +%F).tar.gz"'),
    dict(key='run', name='Run the command', sub='tar returns a code',
         why='The work itself.',
         how='The code arrives through wait().',
         impl='0–255, low 8 bits of exit().', used='$?.',
         cmd='mkdir -p data && echo hi > data/a.txt\ntar -czf "backup_$(date -d 2026-11-06 +%F).tar.gz" data; echo "tar: $?"'),
    dict(key='and', name='&&', sub='only on 0',
         why='Report success only if it succeeded.',
         how='bash checks the code; 0 → run the right side.',
         impl='Left to right, equal priority with ||.', used='Dependent steps.',
         cmd='true && echo "ran after success"'),
    dict(key='or', name='||', sub='only on failure',
         why='Report failures.',
         how='Runs if everything before it ended non-zero.',
         impl='Also runs if the && part failed.', used='Alerts.',
         cmd='tar -czf x.tar.gz /no/such/dir 2>/dev/null && echo done || echo "failed (tar code was 2)"'),
    dict(key='rc', name='$? at the end', sub='the last command run',
         why='Callers see one final code.',
         how='Here: the status of echo, so 0 even after a failure.',
         impl='Use exit 1 in the || branch in scripts.', used='CI, cron.',
         cmd='false || echo "handled"; echo "final \\$? = $?"'),
], hint='From substitution to the final code. Click a layer.')

HOOD = hood('Under the hood: where $? comes from', 'strace follows bash and its child: the child ends with <code>exit_group(2)</code>, bash collects it with <code>wait4()</code>, and that number becomes <code>$?</code>.',
    "bash -c 'ls /nope; echo $?'", show='exit_group|wait4|^write\\(1', trace='%process,write')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Success and failure paths, and xargs splitting</h2>
''' + s1 + two + dx + HOOD + qc('Why is the final $? 0 in <code>false || echo handled</code>?', '$? is the status of the last command that ran, echo, which succeeded. To report failure to a caller, end the || branch with <code>exit 1</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Chaining at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ build &&', 'prompt'), ('deploy', 'acc')], title='ci', size=6.4, step=12),
              '1. CI/CD pipelines', 'Every CI step is judged by its exit code: 0 = green, anything else = red and the pipeline stops.', ['Step', '*exit code', 'green / red']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['apt update', '&& upgrade'], 'blue', 8.6), '2. Server maintenance',
    'Admins chain update && upgrade && reboot so that nothing runs after a failure.', ['Update', '*&&', 'upgrade']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ check ||', 'prompt'), ('alert', 'err')], title='monitor', size=6.4, step=12),
    '3. Monitoring and alerts', 'Health checks (curl, ping, pg_isready) are followed by || send_alert.', ['Check', '*||', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['find -print0', '| xargs -0'], 'green', 8.6), '4. Bulk file work',
    'Cleaning old files, compressing logs, changing permissions on thousands of files: find + xargs (or -exec +).', ['List', '*xargs', 'action']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['$(date +%F)', 'names'], 'violet', 8.6), '5. Dated artefacts',
    'Backups, reports and releases are named with $(date +%F), versions with $(git describe).', ['Run', '*$( )', 'name']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Make and enter', scenario='Create a project folder and go into it.',
         cmd='mkdir -p myproj && cd myproj && pwd', explain='cd only if mkdir worked.'),
    dict(level='b', title='Message on failure', scenario='Tell the user if a config file is missing.',
         cmd="[ -f app.conf ] || echo 'app.conf not found'", explain='The test fails, so || runs.'),
    dict(level='i', title='Count with $( )', scenario='How many users have a login shell?',
         cmd="echo \"login users: $(grep -c -E '(bash|zsh)$' /etc/passwd)\"", explain='grep -c inside a message.'),
    dict(level='i', title='Copy a list of files', scenario='Copy every file listed in files.txt to backup/.',
         cmd="touch r1.txt r2.txt; printf 'r1.txt\\nr2.txt\\n' > files.txt; mkdir -p backup\nxargs -a files.txt -I{} cp {} backup/ && ls backup", explain='-a reads items from a file; -I{} places each one.'),
    dict(level='a', title='Parallel checksums', scenario='Checksum 4 files using 4 processes.',
         cmd="for i in 1 2 3 4; do seq 1 $((i*1000)) > part$i.dat; done\nls part*.dat | xargs -P 4 -n 1 sha256sum | sort -k2 | cut -c1-12,65-", explain='-P 4 runs 4 at once; sort restores the order.'),
], extra=build_up('a safe clean-up command', 'Riya must delete .tmp files older than a week under logs/, and never delete the wrong thing. She builds it step by step.',
    "mkdir -p logs/a; touch -d '2026-10-01' logs/old.tmp 'logs/a/old copy.tmp'; touch logs/new.tmp logs/keep.log", [
    ("find logs -name '*.tmp'", '1. List all .tmp files.'),
    ("find logs -name '*.tmp' -mtime +7", '2. Only those older than 7 days.'),
    ("find logs -name '*.tmp' -mtime +7 -print0 | xargs -0 -r echo rm", '3. Dry run: print the rm command xargs would build.'),
    ("find logs -name '*.tmp' -mtime +7 -print0 | xargs -0 -r rm -v && echo 'clean-up done' || echo 'clean-up FAILED'", '4. Run it for real, with a result message.'),
])) + which('Choosing the right construct.', [
    ('Independent steps', 'a ; b', 'Both run.', 'When b needs a.'),
    ('Dependent steps', 'a && b && c', 'Stops at failure.', '; between them.'),
    ('Fallback / alert', 'a || b', 'Runs on failure.', 'Ignoring errors.'),
    ('Two real branches', 'if a; then b; else c; fi', 'Correct.', 'a && b || c when b can fail.'),
    ('Output in a command', '"$(cmd)"', 'Readable, nests.', '`backticks`, unquoted.'),
    ('Lines → arguments', 'find -print0 | xargs -0', 'Safe names.', 'ls | xargs.'),
    ('One run per item', 'xargs -I{} cmd {}', 'Flexible.', 'for f in $(ls).'),
    ('Stop scripts on errors', 'set -e  /  || exit 1', 'Fail fast.', 'Hoping.'),
]) + keys('Shortcuts and handy forms.', [
    ('$?', 'exit code of the last command', 'echo $?'),
    ('!!', 'repeat the last command (often: sudo !!)', 'sudo !!'),
    ('true / false', 'always 0 / always 1', 'false || echo ran'),
    ('|| exit 1', 'stop the script here on failure', 'cd "$d" || exit 1'),
    ('xargs -t', 'print each command before running', '… | xargs -t rm'),
    ('xargs -p', 'ask y/n before each command', '… | xargs -p rm'),
    ('$((…))', 'arithmetic (not a command)', 'echo $((7*6))'),
    ('kill -l N', 'signal name for a code 128+N', 'kill -l 9 → KILL'),
]) + scriptit('deploy.sh', 'Riya’s fixed deploy script: every step guarded, a clear message and a non-zero exit code on failure, a dated release name with $( ), and xargs to copy the built files.',
'''#!/bin/bash
release="release_$(date -d 2026-11-06 +%F)"
build()  { mkdir -p dist && printf 'a\\nb\\n' | xargs -I{} touch dist/{}.html; }
tests()  { [ -f dist/a.html ] && [ -f dist/b.html ]; }
deploy() { mkdir -p "$release" && ls dist/*.html | xargs -I{} cp {} "$release"/; }

build  || { echo "build failed" >&2; exit 1; }
tests  || { echo "tests failed" >&2; exit 2; }
deploy || { echo "deploy failed" >&2; exit 3; }
echo "deployed $(ls "$release" | wc -l) files to $release"''',
'<p>Each failure exits with its own code (1, 2, 3), so whoever runs the script (cron, CI) knows exactly which step failed.</p>') + puzzle_answer('Both print “failed”. The first because mkdir really failed (no permission for /root). The second although <code>true</code> succeeded: <code>false</code> (the middle command) failed, and <code>||</code> reacts to <b>any</b> failure before it. So <code>a &amp;&amp; b || c</code> is not if-then-else: c runs when a fails <b>or</b> when b fails. Use <code>if a; then b; else c; fi</code> when b can fail.') + qc('Why is <code>find … -print0 | xargs -0 rm</code> safer than <code>ls | xargs rm</code>?', 'Plain xargs splits items at spaces and newlines, so “my file.txt” becomes two wrong names. NUL bytes cannot occur in file names, so -print0/-0 keeps every name whole.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../03-pipes-and-tee-building-command-pipelines/">Lesson 5.3</a> (PIPESTATUS) and <a href="../02-redirection-dev-null-and-here-documents/">5.2</a> (&gt; /dev/null 2&gt;&amp;1).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
