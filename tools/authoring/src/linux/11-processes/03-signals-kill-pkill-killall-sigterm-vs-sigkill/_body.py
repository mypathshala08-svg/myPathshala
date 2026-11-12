import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

KILL = 'pkill -9 -u riya -f "lab11[0-9]|svc.sh"; pkill -u riya -x sleep; pkill -9 -u riya -f worker.sh; pkill -u riya -x nap; pkill -u riya -x yes; true'
SG = r"""pkill -9 -u riya -f 'lab11[0-9]|svc.sh'; pkill -u riya -x sleep; pkill -9 -u riya -f worker.sh; pkill -u riya -x nap; pkill -u riya -x yes; rm -rf ~/sg; mkdir -p ~/sg; cd ~/sg
cat > worker.sh <<'EOF'
#!/bin/bash
trap 'echo "worker: got TERM, saving and exiting" >> ~/sg/worker.log; exit 0' TERM
trap 'echo "worker: got HUP, reloading config" >> ~/sg/worker.log' HUP
echo $$ > ~/sg/worker.pid; echo "worker: started as $$" >> ~/sg/worker.log
while true; do ~/sg/nap 0.2; done
EOF
chmod +x worker.sh; cp /bin/sleep nap
(setsid ./worker.sh > /dev/null 2>&1 &)
(setsid timeout 120 sleep 500 > /dev/null 2>&1 &)
(setsid timeout 120 sleep 501 > /dev/null 2>&1 &)
sleep 1"""

HOOK = hook('A report job has hung for an hour. Riya runs <code>kill -9</code> on it, as she saw online. It disappears, but it leaves a half-written file, a lock file and a database connection that stay until morning. Her senior sighs: “Always ask nicely first.” Linux processes are stopped, paused, reloaded and told about events with <b>signals</b>: small numbered messages from the kernel or another process. <b>SIGTERM</b> (15) asks a program to finish cleanly; <b>SIGKILL</b> (9) removes it without warning; <b>SIGHUP</b> (1) often means “reload your config”; <b>Ctrl+C</b> sends SIGINT. This lesson shows each signal, the commands that send them (<code>kill</code>, <code>pkill</code>, <code>killall</code>), and <code>trap</code>, which lets your own scripts react.',
    ['explain what a signal is and name the common ones: HUP, INT, QUIT, KILL, TERM, STOP, CONT, TSTP, USR1, CHLD',
     'send signals by PID with kill, and by name or pattern with pkill and killall, safely',
     'use the correct order: TERM first, wait, KILL only if needed, and read exit codes 130, 137, 143',
     'handle signals in your own scripts with trap, including cleanup on EXIT'])
ROAD = roadmap([
    ('story', 'The story', 3, 'ask nicely first'),
    ('decide', 'Which signal when?', 2, 'the quick chart'),
    ('definition', 'What a signal is', 6, 'simple meaning + 4 depths'),
    ('types', 'The signals', 5, 'numbers, defaults, keys'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'TERM vs KILL'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'stop the right processes'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which signal? (decide in 5 seconds)', [
    ('Stop a program cleanly', 'kill PID   (= kill -TERM, 15)', 'default'),
    ('It ignores TERM after 10 s', 'kill -KILL PID   (-9)', 'last resort'),
    ('Interrupt what is in front of you', 'Ctrl+C   (INT, 2)', 'keyboard'),
    ('Reload config without restart', 'kill -HUP PID   (1)', 'nginx, sshd'),
    ('Pause and resume', 'kill -STOP / -CONT PID', 'freeze'),
    ('Every process with a name', 'pkill -x name   ·   killall name', 'by name'),
    ('Is the PID alive (no harm)?', 'kill -0 PID', 'check'),
    ('Clean up when my script stops', "trap 'rm -f $tmp' EXIT", 'trap'),
])

cmap = concept_map(
    [('11.1', 'Processes', 'PID, PPID, fork'), ('11.2', 'ps, pgrep, top', 'find the PID'), ('12.10', 'Functions and trap', 'first look at trap')],
    ['signals: numbers and names', 'TERM vs KILL vs INT vs HUP', 'kill, pkill, killall, kill -0', 'STOP / CONT and Ctrl+Z', 'trap, EXIT cleanup, exit codes 128+n'],
    [('11.4', 'Jobs and nohup', 'Ctrl+Z, bg, SIGHUP on logout'), ('11.5', 'nice and renice', 'slow down instead of kill'), ('17.2', 'systemctl', 'stop = TERM, then KILL'), ('20.3', 'Containers', 'docker stop sends TERM')],
    'A signal is a tap on the shoulder. Most can be caught and handled politely; KILL and STOP cannot.')

sc = (term(20, 14, 316, 156, ['$ pgrep -a sleep', ('4120 sleep 500', 'out'), '$ kill 4120; sleep 0.2', '$ kill -0 4120', ('kill: (4120) - No such process', 'acc'), '$ kill -l 9 15', ('KILL TERM', 'out')], title='riya@web01: ~/sg', prompt='riya@web01:~/sg$', size=6.8, step=17)
      + t(352, 36, 'kill sends', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['TERM (15) by default', 'program may clean up', 'KILL (9): no warning', 'kernel removes it', '-0: just check'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Ask nicely first</h2>
  <div class="story">
''' + puzzle('Riya’s script ends with <code>trap \'rm -f /tmp/report.lock\' EXIT</code>. When she presses Ctrl+C, the lock file is removed. When she runs <code>kill PID</code>, it is removed too. But after <code>kill -9 PID</code> the lock file is still there and the next run refuses to start. Also, <code>kill nginx</code> answers “arguments must be process or job IDs”. Why the difference, and what is the right way?') + '''
    <p class="narration">Riya stops a sleeping process and checks that it is gone.</p>
''' + scene('A terminal: pgrep finds a sleep process, kill sends it TERM, kill -0 confirms it is gone, and kill -l translates 9 and 15.', sc,
            'The name <tspan font-weight="700" class="s-acc">kill</tspan> is misleading: it just sends a signal.') + '''
K> So kill does not always kill?
A> kill sends a signal, TERM by default. A well-written program catches TERM, finishes writing, closes files and exits. A program can also ignore it. KILL cannot be caught: the kernel removes the process at once, with no chance to clean up.
R> So that’s why the lock stayed.
A> Exactly. Today: the signals you will meet, how to send them by PID or name, and how to make your own scripts handle them.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Three ways to end a meeting: a polite note (TERM) lets people pack up, a fire alarm (INT, Ctrl+C) interrupts, and security guards (KILL) carry everyone out at once.">'
       + label_box(20, 24, 190, 120, ['TERM (15)', 'a polite note:', '“please finish', 'and leave”'], 'green', 9)
       + label_box(225, 24, 190, 120, ['INT (2) Ctrl+C', 'someone shouts', '“stop!”', 'you may react'], 'amber', 9)
       + label_box(430, 24, 190, 120, ['KILL (9)', 'guards carry you', 'out at once,', 'bags left behind'], 'red', 9)
       + t(320, 170, 'TERM and INT can be caught (trap). KILL cannot.', 10, 'acc', bold=True)
       + t(320, 192, 'That is why KILL leaves lock files and half-written data.', 9.4, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Signals at four depths', [
    ('v', 'No jargon: ending a meeting', '      <p>Ask, interrupt, or remove by force.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>Ctrl+C</code>: stop the command in front of you (SIGINT).</li>
        <li><code>kill 4120</code>: ask process 4120 to stop (SIGTERM).</li>
        <li><code>kill -9 4120</code>: force it (SIGKILL), only if TERM did not work.</li>
        <li><code>pkill -x firefox</code>: by name.</li>
      </ul>'''),
    ('i', 'Catch, ignore or default', '''      <ul>
        <li>For each signal a process can: run the <b>default action</b> (terminate, core dump, stop, continue, ignore), <b>ignore</b> it, or <b>catch</b> it with a handler.</li>
        <li>KILL (9) and STOP (19) can never be caught or ignored.</li>
        <li>A process killed by signal n has exit status <b>128 + n</b>: 130 for INT, 137 for KILL, 143 for TERM.</li>
        <li>You may signal only your own processes; root can signal any.</li>
        <li><code>trap 'commands' SIGNAL</code> catches signals in bash; <code>trap … EXIT</code> runs when the script ends for any reason except KILL.</li>
      </ul>'''),
    ('a', 'Behind the screen: the kernel’s pending set', '''      <ul>
        <li><code>kill</code> is the <code>kill(2)</code> system call: the kernel sets a bit in the target’s <b>pending</b> signal set (see <code>SigPnd</code>, <code>SigBlk</code>, <code>SigIgn</code>, <code>SigCgt</code> in /proc/PID/status).</li>
        <li>When the process next returns from the kernel, the signal is <b>delivered</b>: its handler runs, or the default action happens.</li>
        <li>A process in <b>D</b> state (uninterruptible disk/NFS wait) does not die even from KILL until the I/O returns.</li>
        <li>A <b>zombie</b> (Z) is already dead; killing it does nothing. Its parent must wait() for it, or the parent must die so init adopts and reaps it.</li>
        <li>The terminal driver turns keys into signals: Ctrl+C → INT, Ctrl+\\ → QUIT, Ctrl+Z → TSTP, closing the terminal → HUP to the session.</li>
        <li>systemd and Docker stop services with TERM, wait (90 s / 10 s), then KILL.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Signals and the kill commands</h2>
''' + def_block(
    'A <b>signal</b> is a short, numbered notification the kernel delivers to a process to report an event or request an action (stop, reload, interrupt, continue). <code>kill</code> sends a signal to processes by PID, <code>pkill</code> by name or pattern, and <code>killall</code> by exact name. A process may handle, ignore or accept the default action of most signals; SIGKILL and SIGSTOP cannot be caught.',
    'A tap on the shoulder with a number. kill is the tap, not the killing.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Signal', 'A numbered message to a process.'),
    ('SIGTERM (15)', 'Please terminate (default of kill).'),
    ('SIGKILL (9)', 'Terminate now; cannot be caught.'),
    ('SIGINT (2)', 'Interrupt: Ctrl+C.'),
    ('SIGHUP (1)', 'Hang-up; often “reload config”.'),
    ('Handler', 'Code that runs when a signal arrives.'),
    ('trap', 'bash command to set handlers.'),
    ('Exit 128+n', 'Status of a process killed by signal n.'),
]) + '\n' + names('Where the names come from.', [
    ('kill', 'its first use', 'Unix V1, 1971: only killing.'),
    ('SIGHUP', 'hang up', 'The modem line dropped.'),
    ('SIGINT', 'interrupt', 'The DEL / Ctrl+C key.'),
    ('SIGQUIT', 'quit with core', 'Ctrl+\\.'),
    ('SIGTSTP', 'terminal stop', 'Ctrl+Z.'),
    ('SIGCHLD', 'child changed', 'Sent to the parent.'),
    ('pkill', 'pattern kill', 'Solaris 7, 1998.'),
    ('killall', 'kill all by name', 'On Solaris it kills ALL processes!'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('List signals', '<code>kill -l</code>'),
    ('Default', '<code>kill PID</code> = TERM'),
    ('Force', '<code>kill -9 PID</code>'),
    ('By name', '<code>pkill -x name</code>'),
    ('Check alive', '<code>kill -0 PID</code>'),
    ('Exit codes', '130 INT · 137 KILL · 143 TERM'),
]) + '\n' + lv + didyou('On Solaris and some older Unix systems, <code>killall</code> really kills <i>all</i> processes (it is used at shutdown). Typing the Linux habit <code>killall java</code> as root there can take the whole machine down. On any unfamiliar system, prefer <code>pkill</code>.') + '''
EXAM> “What is the difference between kill -9 and kill -15?” → 15 (TERM) asks the process to exit and can be caught, allowing cleanup; 9 (KILL) is handled by the kernel, cannot be caught, and gives no chance to clean up.
''' + qc('A process exited with status 143. What happened?', '143 − 128 = 15: it was terminated by SIGTERM.') + mistake('kill -9 as the first try',
    'kill PID; wait a few seconds; check with kill -0 PID; only then kill -9 PID',
    'KILL skips the program’s cleanup: lock files, temp files and half-written output stay behind (the puzzle).') + mistake('kill nginx',
    'pkill -x nginx   ·   killall nginx   ·   kill $(pgrep -x nginx)',
    'kill takes PIDs or %jobs only: “arguments must be process or job IDs” (real run).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The signals you will meet</h2>
''' + table(['No.', 'Name', 'Default action', 'Sent by / used for', 'Catch?'], [
    ['1', 'HUP', 'terminate', 'terminal closed; daemons: reload config', 'yes'],
    ['2', 'INT', 'terminate', 'Ctrl+C', 'yes'],
    ['3', 'QUIT', 'core dump', 'Ctrl+\\', 'yes'],
    ['6', 'ABRT', 'core dump', 'abort(); crashes', 'yes'],
    ['9', 'KILL', 'terminate', 'last resort; OOM killer', '<b>no</b>'],
    ['10 / 12', 'USR1 / USR2', 'terminate', 'program-defined (dd prints progress, nginx reopens logs)', 'yes'],
    ['11', 'SEGV', 'core dump', 'invalid memory access (a bug)', 'yes'],
    ['13', 'PIPE', 'terminate', 'writing to a closed pipe (head quit)', 'yes'],
    ['14', 'ALRM', 'terminate', 'timer (alarm, timeout)', 'yes'],
    ['15', 'TERM', 'terminate', '<code>kill</code> default; systemd, docker stop', 'yes'],
    ['17', 'CHLD', 'ignore', 'a child ended or stopped', 'yes'],
    ['18', 'CONT', 'continue', 'resume a stopped process; fg/bg', 'yes'],
    ['19', 'STOP', 'stop', 'pause', '<b>no</b>'],
    ['20', 'TSTP', 'stop', 'Ctrl+Z', 'yes'],
], minw=560) + table(['', 'kill', 'pkill', 'killall'], [
    ['Selects by', 'PID or %job', 'pattern (regex) on name, -f full command, -u user…', 'exact process name'],
    ['Example', '<code>kill 4120</code>', '<code>pkill -u riya -x sleep</code>', '<code>killall sleep</code>'],
    ['Risk', 'wrong PID', 'pattern too broad (pkill sh hits bash, ssh…)', 'on Solaris: all processes'],
    ['Preview', '<code>ps -p PID</code>', '<code>pgrep -a …</code> with the same options', '<code>killall -i</code> asks'],
    ['Package', 'built-in + procps', 'procps', 'psmisc'],
], minw=520) + table(['Exit status', 'Means'], [
    ['0', 'finished normally'],
    ['1–125', 'the program’s own error code'],
    ['126 / 127', 'not executable / not found'],
    ['130', 'killed by INT (128+2): Ctrl+C'],
    ['137', 'killed by KILL (128+9): kill -9 or the OOM killer'],
    ['143', 'killed by TERM (128+15)'],
], minw=380) + qc('Which two signals can no process catch or ignore?', 'SIGKILL (9) and SIGSTOP (19).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>kill, pkill, killall, STOP/CONT and trap, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/sg</code>. The setup starts <code>worker.sh</code> (a loop that traps TERM and HUP and writes to <code>worker.log</code>) and two <code>sleep</code> processes. Output from other users’ processes is filtered out.</p>
''' + cmdcard_u(['stopping a hung program by PID', 'checking whether a PID exists', 'sending a specific signal'],
               ['guessing PIDs', 'kill -9 as the first step'])(
    'kill', 'kill [-SIGNAL] PID… · kill -l · kill -0 PID', 'kill',
    '<code>kill PID</code> sends TERM. Choose another signal by name or number: <code>-HUP</code>, <code>-s HUP</code>, <code>-1</code>. <code>kill -l</code> lists signals and converts numbers to names. <code>kill -0</code> sends nothing but tells you whether the PID exists and you may signal it. Several PIDs can be given at once.',
    'kill PID   ·   kill -TERM PID   ·   kill -9 PID   ·   kill -0 PID', 'danger',
    [('kill PID', 'TERM: please stop', 'normal'),
     ('kill -HUP PID', 'reload / hang-up', 'daemons'),
     ('kill -INT PID', 'like Ctrl+C', 'scripts'),
     ('kill -9 PID', 'force', 'last resort'),
     ('kill -0 PID', 'exists?', 'checks'),
     ('kill -l [n]', 'list / translate', 'reference'),
     ('kill %1', 'a shell job', 'Lesson 11.4')],
    dict(setup=SG, cmd="cd ~/sg; pid=$(cat ~/sg/worker.pid)\nkill -HUP \"$pid\"; sleep 0.5\nkill \"$pid\"; sleep 0.5\ncat worker.log | sed 's/as [0-9]*/as PID/'\nkill -0 \"$pid\" 2>&1 | sed 's/([0-9]*)/(PID)/'", expect='any', note='HUP ran the reload handler and the worker kept going; TERM ran the save-and-exit handler; kill -0 confirms it is gone.'),
    [('sys', [
        dict(situation='TERM vs KILL exit codes.', cmd="sleep 100 & p=$!; kill $p; wait $p; echo \"after TERM: $?\"\nsleep 100 & p=$!; kill -9 $p; wait $p 2>/dev/null; echo \"after KILL: $?\"\nkill -l 143 137 130", why='128+15, 128+9; kill -l turns a status back into a signal name.')]),
     ('qa', [
        dict(situation='Permission: you may only signal your own processes.', cmd="kill -0 1 2>&1; echo \"status $?\"\nkill -0 $$ && echo 'my own shell: allowed'", why='PID 1 belongs to root: Operation not permitted.')]),
    ],
    anat=anatomy([('kill', 'cmd', 'send a signal'), ('-TERM', 'opt', 'which signal (default TERM)'), ('4120', 'arg', 'PID(s)')], 'Signal by name (-TERM, -HUP) is clearer than number (-15, -1).')
) + cmdcard_u(['all processes of a program or user', 'scripts that stop their helpers'],
               ['short patterns like pkill sh', 'running without previewing as root'])(
    'pkill', 'pgrep/pkill [-x] [-f] [-u user] [-SIGNAL] pattern · killall name', 'pkill and killall',
    '<code>pkill</code> takes the same selectors as <code>pgrep</code> (Lesson 11.2) and sends a signal to every match: <code>-x</code> exact name, <code>-f</code> match the whole command line, <code>-u</code> user, <code>-n/-o</code> newest/oldest, <code>-e</code> echo what was killed. Preview with pgrep first. <code>killall</code> uses exact names; <code>-i</code> asks, <code>-u</code> limits to a user, <code>-w</code> waits until they are gone.',
    'pgrep -a -x name   →   pkill -x name   ·   killall -w name', 'danger',
    [('pkill -x name', 'exact name', 'safe default'),
     ('pkill -f text', 'full command line', 'scripts, java -jar'),
     ('pkill -u riya', 'every process of riya', 'log a user out'),
     ('pkill -e …', 'print what was killed', 'logs'),
     ('pkill -HUP -x nginx', 'signal by name', 'reload'),
     ('killall -i name', 'ask for each', 'careful'),
     ('killall -w name', 'wait until gone', 'scripts')],
    dict(setup=SG, cmd="cd ~/sg\npgrep -a -u riya -x sleep | sed 's/^[0-9]*/PID/'\npkill -e -u riya -x sleep | sed 's/(pid [0-9]*)/(pid N)/'\npgrep -c -u riya -x sleep", expect='any', note='Preview, kill, verify: none left.'),
    [('sys', [
        dict(situation='Why -x matters.', setup=SG, cmd="cd ~/sg; cp /bin/sleep ./sleepy; (setsid ./sleepy 300 >/dev/null 2>&1 &); sleep 0.3\necho \"no -x: $(pgrep -u riya sleep | wc -l)   with -x: $(pgrep -u riya -x sleep | wc -l)\"\npkill -u riya -x sleepy", why='Without -x, “sleep” also matched sleepy.')]),
     ('dev', [
        dict(situation='killall with -w waits for the end.', setup=SG, cmd="cd ~/sg; killall -u riya -w sleep && echo \"all sleep processes are gone: $(pgrep -c -u riya -x sleep)\"", expect='any', why='-w is useful before restarting a program.')]),
    ]
) + cmdcard_u(['pausing a heavy job for a while', 'freezing a process to inspect it'],
               ['stopping a process that holds a lock others need'])(
    'stop', 'kill -STOP PID · kill -CONT PID · Ctrl+Z', 'pause and resume',
    'STOP freezes a process (state <b>T</b> in ps); it uses no CPU but keeps its memory and open files. CONT lets it run again. Ctrl+Z sends TSTP, the catchable version, to the program in front of you; <code>fg</code> and <code>bg</code> continue it (Lesson 11.4).',
    'kill -STOP PID   ·   ps -o stat= -p PID   ·   kill -CONT PID', 'change',
    [('kill -STOP', 'freeze', 'pause'),
     ('kill -CONT', 'resume', 'continue'),
     ('Ctrl+Z', 'TSTP from the keyboard', 'jobs'),
     ('ps stat T', 'stopped', 'check'),
     ('kill -TSTP', 'polite stop', 'catchable')],
    dict(cmd="timeout 30 yes > /dev/null & p=$!; sleep 1\necho \"running: $(ps -o stat=,%cpu= -p $p)\"\nkill -STOP $p; sleep 1; echo \"stopped: $(ps -o stat= -p $p)\"\nkill -CONT $p; sleep 0.5; echo \"continued: $(ps -o stat= -p $p)\"\nkill $p", note='R = running, T = stopped. The CPU use drops to zero while stopped.'),
    [('data', [
        dict(situation='Pause a big job during office hours.', cmd="timeout 30 yes > /dev/null & p=$!\nkill -STOP $p; echo \"paused job $(ps -o stat= -p $p | tr -d ' ') at $(date +%H):xx\" | sed 's/[0-9][0-9]:xx/HH:xx/'\nkill -CONT $p; kill $p", why='A cron job could STOP at 9:00 and CONT at 18:00 (or use nice, Lesson 11.5).')]),
    ]
) + cmdcard_u(['cleanup of temp and lock files', 'graceful shutdown of your own scripts', 'reload on HUP'],
               ['complex logic inside a handler', 'expecting EXIT to run after kill -9'])(
    'trap', "trap 'cmds' SIGNAL… · trap … EXIT · trap - SIG · trap '' SIG", 'trap in your scripts',
    "<code>trap 'commands' TERM INT</code> runs the commands when a signal arrives. <code>EXIT</code> is a bash pseudo-signal that runs when the script ends, normally or by a catchable signal. <code>trap '' INT</code> ignores a signal; <code>trap - INT</code> restores the default; <code>trap -p</code> shows the traps.",
    "trap 'rm -f \"$tmp\"' EXIT   ·   trap 'echo reload' HUP   ·   trap '' INT", 'safe',
    [("trap '…' EXIT", 'always clean up', 'temp files'),
     ("trap '…' INT TERM", 'graceful stop', 'services'),
     ("trap '…' HUP", 'reload config', 'daemons'),
     ("trap '' INT", 'ignore Ctrl+C', 'critical section'),
     ('trap - INT', 'default again', 'after the section'),
     ('trap -p', 'list traps', 'debug')],
    dict(setup="cd ~; cat > job.sh <<'EOF'\ntmp=$(mktemp); lock=~/job.lock; touch \"$lock\"\ntrap 'rm -f \"$tmp\" \"$lock\"; echo \"cleanup done\"' EXIT\ntrap 'echo \"caught TERM\"; exit 143' TERM\necho working > \"$tmp\"; sleep 30 & wait $!\nEOF", cmd="cd ~\nbash job.sh & p=$!; sleep 0.5\nkill $p; wait $p; echo \"status $?\"; ls job.lock 2>&1\nbash job.sh & p=$!; sleep 0.5\nkill -9 $p; wait $p 2>/dev/null; echo \"status $?\"; ls job.lock; rm -f job.lock; pkill -u riya -x sleep", expect='any', note='The puzzle: with TERM both traps ran and the lock was removed; with KILL nothing ran and job.lock stayed.'),
    [('dev', [
        dict(situation='Ignore Ctrl+C during a critical step.', setup="cd ~; cat > crit.sh <<'EOF'\ntrap '' INT\necho 'updating (Ctrl+C ignored)'; kill -INT $$; echo 'still running after INT'\ntrap - INT\necho 'default restored'\nEOF", cmd="bash ~/crit.sh", why='kill -INT $$ simulates Ctrl+C on itself; it was ignored.')]),
    ]
) + undo('A killed process cannot be brought back; its unsaved work is lost.', [
    ('Killed the wrong process:', 'restart it (systemctl restart, or the command); check its logs.'),
    ('Lock or PID file left after kill -9:', 'check nothing is running (pgrep), then remove the stale file.'),
    ('Stopped (T) and forgotten:', '<code>kill -CONT PID</code> or <code>fg</code>.'),
    ('Next time:', 'preview with <code>pgrep -a</code>, send TERM, wait, check with <code>kill -0</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='kill nginx', meaning='kill needs PIDs or %jobs, not names.', fix='pkill -x nginx.'),
    dict(cmd='kill 999999', meaning='No process with that PID.', fix='Find it with pgrep -a.'),
    dict(cmd='kill -0 1', meaning='Not your process.', fix='Use sudo (and be sure).'),
    dict(cmd='kill -FOO 1', meaning='Unknown signal name.', fix='kill -l.'),
    dict(cmd='killall nosuchprog', meaning='No process with that name.', fix='pgrep -a part-of-name.'),
]) + qc('Which signal does Ctrl+C send?', 'SIGINT (2).') + '''
'''
cards = cards + '</section>\n'

def proc(k, sig):
    st = {'TERM': [('running', 'blue'), ('TERM arrives', 'amber'), ('handler: save, close', 'green'), ('exit 143 (clean)', 'green')],
          'KILL': [('running', 'blue'), ('KILL arrives', 'red'), ('kernel removes it', 'red'), ('exit 137, files left', 'red')]}[sig]
    o = ''
    for i in range(k + 1):
        o += label_box(20, 14 + i * 38, 320, 30, [st[i][0]], st[i][1], 9)
    return o
see_cmds = [['$ ./report.sh &', ('[1] 4120', 'out')], ['$ kill 4120'], ['$ kill 4120', ('saving report… removing lock', 'out')], ['$ ls report.lock', ('ls: cannot access…', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['A job runs.', 'TERM sent.', 'Its trap runs.', 'Clean exit.'])]
behind = [proc(k, 'TERM') + t(180, 190, n, 8.4, 'violet', bold=True) for k, n in enumerate(['Process running.', 'Kernel marks TERM pending.', 'Handler runs (trap).', 'Exits by itself.'])]
two = anim_two('kill with TERM', 'Behind the screen: delivery and the handler',
               'A terminal starting a job, sending kill, seeing the cleanup message and confirming the lock file is gone.',
               'Four boxes: running, TERM pending, handler runs and saves, process exits with status 143.', see, behind,
               ['Run.', 'TERM.', 'Handler.', 'Exit.'],
               ['run', 'TERM', 'trap', 'exit'])

frames = [proc(k, 'KILL') + t(180, 190, n, 8.6, 'red' if k else 'violet', bold=True) for k, n in enumerate(['Same job.', 'kill -9: no handler can run.', 'Removed at once.', 'Lock file and temp data stay.'])]
s1 = anim_one('Animated example', 'kill -9 (SIGKILL)',
              'The kernel does not ask the process anything.',
              'kill -9 PID', 'Four boxes in red: running, KILL arrives, the kernel removes the process, exit 137 with files left behind.', frames,
              ['Run.', 'KILL.', 'Removed.', 'Left behind.'], hid='scenario-kill9')

dx = dissect('Layer by layer: where signals live',
    'Each layer has a real command and output from our build machine.', [
    dict(key='list', name='Signal table', sub='numbers', why='Names ↔ numbers.', how='kill -l.', impl='signal(7).', used='Reference.',
         cmd="kill -l | head -4"),
    dict(key='mask', name='Per-process masks', sub='/proc', why='Who catches what.', how='Bit masks in hex.', impl='SigCgt = caught.', used='Debugging.',
         setup=SG, cmd="grep -E '^Sig(Blk|Ign|Cgt)' /proc/$(cat ~/sg/worker.pid)/status"),
    dict(key='keys', name='Keyboard signals', sub='stty', why='Ctrl+C → INT.', how='Terminal driver.', impl='stty -a.', used='Remap keys.',
         cmd="{ stty -a < /dev/tty; } 2>/dev/null | grep -o 'intr = [^;]*; quit = [^;]*' || echo 'intr = ^C; quit = ^\\\\ (typical: no terminal here)'"),
    dict(key='code', name='Exit status', sub='128+n', why='Diagnose.', how='$? or wait.', impl='WTERMSIG.', used='CI logs.',
         cmd="bash -c 'kill -TERM $$'; echo \"$? = 128 + $(( $? - 128 )) = $(kill -l $?)\""),
], hint='From the signal table to exit codes. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>TERM vs KILL</h2>
''' + two + s1 + dx + qc('Why does the worker’s SigCgt line show bits set?', 'Because worker.sh trapped TERM and HUP: those signals are “caught” by a handler.') + '''
</section>
'''

VAR = variations('Sixteen more signal experiments. All were really run on our build machine.', [
    ('Sending signals', [
        dict(title='Name, number and -s are the same', cmd="for f in '-TERM' '-15' '-s TERM'; do sleep 50 & p=$!; kill $f $p; wait $p; echo \"kill $f -> $?\"; done", why='Three spellings of TERM.'),
        dict(title='Several PIDs at once', cmd="sleep 50 & a=$!; sleep 51 & b=$!; kill $a $b; wait; echo \"left: $(jobs -r | wc -l)\"", why='kill accepts a list.'),
        dict(title='Polite stop with a timeout, then force', cmd="sleep 50 & p=$!\nkill $p; for i in 1 2 3 4 5; do kill -0 $p 2>/dev/null || { echo \"stopped after TERM\"; break; }; sleep 1; done\nkill -0 $p 2>/dev/null && { kill -9 $p; echo forced; }; true", why='The pattern systemd and Docker use.'),
        dict(title='A process that ignores TERM', cmd="bash -c \"trap '' TERM; sleep 2\" & p=$!; sleep 0.3\nkill $p; sleep 0.3; kill -0 $p 2>/dev/null && echo 'TERM ignored: still alive'\nkill -9 $p; wait $p 2>/dev/null; echo \"KILL: status $?\"", why='Only KILL works against a program that ignores TERM.'),
        dict(title='Kill a whole process group', cmd="setsid bash -c 'sleep 60 & sleep 61 & wait' & sleep 0.3; pg=$(pgrep -n -x bash -u riya); kill -TERM -- -$(ps -o pgid= -p $pg | tr -d ' '); sleep 0.3; echo \"sleeps left: $(pgrep -c -f '^sleep 6[01]$')\"", why='A negative PID means the whole group: parent and children.'),
        dict(title='timeout sends TERM for you', cmd="timeout 1 sleep 10; echo \"timeout status: $?\"\ntimeout -s KILL 1 sleep 10; echo \"with -s KILL: $?\"", why='timeout exits 124 after TERM; with KILL the status is 137.'),
    ]),
    ('pkill / pgrep selectors', [
        dict(title='Oldest and newest only', cmd="for n in 1 2 3; do sleep 6$n & done; sleep 0.2; pkill -o -P $$ -x sleep; pkill -n -P $$ -x sleep; pgrep -a -P $$ -x sleep | awk '{print $2, $3}'; pkill -P $$ -x sleep", why='-o oldest, -n newest: the middle one survived.'),
        dict(title='Match the full command line', cmd="(exec -a report-builder sleep 60 &); sleep 0.2; pgrep -a -f report-builder | awk '{print $2}'; pkill -f report-builder; sleep 0.2; pgrep -c -f report-builder", expect='any', why='-f matched the command line; exec -a set a custom name.'),
        dict(title='Count instead of killing', cmd="sleep 30 & sleep 31 & sleep 0.2; echo \"would kill $(pgrep -c -P $$ -x sleep) processes\"; pkill -P $$ -x sleep", why='Preview the count before pkill.'),
        dict(title='Signal by terminal or parent', cmd="sleep 40 & sleep 41 & sleep 0.2; pgrep -P $$ | wc -l; pkill -P $$ -x sleep; sleep 0.2; pgrep -c -P $$ -x sleep", expect='any', why='-P PID: only children of this shell.'),
    ]),
    ('trap patterns', [
        dict(title='Reload on HUP, quit on TERM', setup="cd ~; cat > svc.sh <<'EOF'\nn=0\ntrap 'n=$((n+1)); echo \"reload #$n\"' HUP\ntrap 'echo \"stopping after $n reloads\"; exit 0' TERM\nwhile :; do sleep 0.1; done\nEOF", cmd="bash ~/svc.sh & p=$!; sleep 0.3; kill -HUP $p; sleep 0.3; kill -HUP $p; sleep 0.3; kill $p; wait $p; echo \"exit $?\"", why='The classic daemon pattern.'),
        dict(title='EXIT runs on errors with set -e', setup="cd ~; printf 'set -e\\ntrap \"echo cleanup ran\" EXIT\\nfalse\\necho never\\n' > e.sh", cmd="bash ~/e.sh; echo \"status $?\"", expect='any', why='The script stopped at false, but EXIT still ran.'),
        dict(title='Show active traps', cmd="trap 'echo bye' EXIT; trap 'echo int' INT; trap -p | sed 's/^/  /'; trap - EXIT INT", why='trap -p prints them in reusable form.'),
        dict(title='Ctrl+C status 130', cmd="bash -c 'kill -INT $$'; echo \"status $? = $(kill -l $?)\"", why='The same status you get after pressing Ctrl+C.'),
        dict(title='dd progress with USR1', cmd="dd if=/dev/zero of=/dev/null bs=1M count=3000 2>&1 & p=$!; sleep 0.2; kill -USR1 $p 2>/dev/null; wait $p; true", expect='any', why='dd prints its progress when it gets USR1 (output order may vary).'),
        dict(title='SIGPIPE: why head stops yes', cmd="yes | head -2; echo \"statuses: ${PIPESTATUS[*]}\"", why='When head exits, yes gets PIPE (141 = 128+13).'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Signals at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['HUP', 'reload'], 'blue', 8.6), '1. Reloading servers without downtime',
              'nginx -s reload, systemctl reload sshd and kill -HUP make daemons re-read their config while connections continue.', ['Edit config', '*HUP', 'new config live']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['TERM', 'deploys'], 'green', 8.6), '2. Graceful shutdown in deployments',
    'Kubernetes, Docker and systemd send TERM, wait a grace period, then KILL. Apps that trap TERM finish requests first.', ['Deploy', '*TERM → wait → KILL', 'no lost requests']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['137', 'OOM'], 'red', 8.6), '3. Diagnosing crashes',
    'Exit 137 in a container usually means the OOM killer (SIGKILL); 139 is SIGSEGV; 143 a normal stop.', ['Exit code', '*128+n', 'cause']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['USR1', 'logs'], 'amber', 8.6), '4. Log rotation',
    'logrotate sends USR1 or HUP so programs reopen their log files (Lesson 18.2).', ['Rotate', '*USR1', 'new log']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['trap', 'scripts'], 'violet', 8.6), '5. Safe scripts',
    'Backup and ETL scripts trap EXIT to remove temp files and locks, and INT/TERM to stop cleanly.', ['Start', '*trap', 'clean end']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Translate a number', scenario='What is signal 9?', cmd="kill -l 9; kill -l 1 2 15", explain='kill -l n.'),
    dict(level='b', title='Is it still running?', scenario='Before a restart.', cmd="sleep 5 & p=$!; kill -0 $p && echo alive; kill $p", explain='kill -0.'),
    dict(level='i', title='Stop all my sleeps', scenario='Clean up tests.', setup=SG, cmd="pkill -u riya -x sleep; sleep 0.2; pgrep -c -u riya -x sleep", expect='any', explain='0 left.'),
    dict(level='i', title='What signals does a process catch?', scenario='Will it handle TERM?', setup=SG, cmd="m=$(awk '/SigCgt/{print $2}' /proc/$(cat ~/sg/worker.pid)/status); for s in 1 15; do (( 0x$m >> (s-1) & 1 )) && echo \"catches $(kill -l $s)\"; done", explain='Decode the SigCgt bit mask.'),
    dict(level='a', title='Graceful stop function', scenario='Reusable.', cmd="stop(){ kill \"$1\" 2>/dev/null; for i in {1..10}; do kill -0 \"$1\" 2>/dev/null || return 0; sleep 0.3; done; kill -9 \"$1\"; }\nsleep 60 & p=$!; stop $p && echo \"stopped $(kill -0 $p 2>&1 | grep -c 'No such')\"", explain='TERM, wait, then KILL.'),
], extra=build_up('a script that stops cleanly', 'Riya grows a background job with proper signal handling.', "cd ~; rm -f lockjob.sh lockjob.lock", [
    ("cd ~; printf 'touch ~/lockjob.lock\\nsleep 30\\nrm -f ~/lockjob.lock\\n' > lockjob.sh; bash lockjob.sh & p=$!; sleep 0.3; kill $p; sleep 0.2; ls lockjob.lock", '1. No trap: TERM leaves the lock.'),
    ("cd ~; rm -f lockjob.lock; printf 'touch ~/lockjob.lock\\ntrap \"rm -f ~/lockjob.lock\" EXIT\\nsleep 30 & wait $!\\n' > lockjob.sh; bash lockjob.sh & p=$!; sleep 0.3; kill $p; sleep 0.2; ls lockjob.lock 2>&1", '2. trap EXIT + wait: the lock is removed.'),
    ("cd ~; printf 'touch ~/lockjob.lock\\ntrap \"rm -f ~/lockjob.lock; echo cleaned\" EXIT\\ntrap \"echo got TERM; exit 143\" TERM\\nsleep 30 & wait $!\\n' > lockjob.sh; bash lockjob.sh & p=$!; sleep 0.3; kill $p; wait $p; echo \"status $?\"", '3. A TERM message and the right status.'),
    ("cd ~; pkill -u riya -x sleep; ls lockjob.lock 2>&1 | grep -c 'No such'", '4. Verify: no lock, no leftover sleep.'),
], cumulative=False, expect='any')) + VAR + which('Choosing the right tool.', [
    ('Stop one process', 'kill PID', 'Exact.', 'pkill with a vague pattern.'),
    ('Stop by name', 'pkill -x name', 'Same options as pgrep.', 'killall on Solaris.'),
    ('A system service', 'systemctl stop / reload', 'Knows the unit, restarts.', 'kill on a managed service.'),
    ('A container', 'docker stop', 'TERM + grace + KILL.', 'docker kill first.'),
    ('Pause', 'kill -STOP / -CONT or nice', 'Keeps state.', 'Killing and rerunning.'),
    ('Cleanup in scripts', "trap … EXIT", 'Runs on most exits.', 'Hoping nobody presses Ctrl+C.'),
]) + keys('Keyboard signals.', [
    ('Ctrl+C', 'INT (2)', 'interrupt'),
    ('Ctrl+\\', 'QUIT (3)', 'quit + core'),
    ('Ctrl+Z', 'TSTP (20)', 'suspend'),
    ('fg / bg', 'CONT (18)', 'resume'),
    ('close terminal', 'HUP (1)', 'hang-up'),
    ('Ctrl+D', 'not a signal: end of input', 'EOF'),
]) + scriptit('graceful-stop.sh', 'Stop every process matching a name: list them, send TERM, wait up to 5 seconds, KILL any that are left, and report each step.',
'''name=${1:-demo-nap}
cp /bin/sleep ~/demo-nap; for i in 1 2; do (~/demo-nap 70 > /dev/null 2>&1 &); done; sleep 0.3   # demo targets
mapfile -t pids < <(pgrep -u "$USER" -x "$name")
[ ${#pids[@]} -eq 0 ] && { echo "no $name processes"; exit 0; }
echo "found ${#pids[@]} $name process(es)"
kill -TERM "${pids[@]}" 2>/dev/null
for t in 1 2 3 4 5; do
  left=$(pgrep -c -u "$USER" -x "$name")
  [ "$left" -eq 0 ] && { echo "all stopped after TERM (${t}s)"; exit 0; }
  sleep 1
done
pkill -KILL -u "$USER" -x "$name" && echo "forced $left with KILL"''',
'<p>Run without a name, so it starts and stops two demo processes (a copy of sleep called demo-nap).</p>', expect='any') + puzzle_answer('Ctrl+C sends INT and <code>kill</code> sends TERM; bash ends the script and runs the EXIT trap, so the lock is removed. <code>kill -9</code> sends KILL, which the kernel carries out without running any code in the process: no trap, no cleanup, the lock stays. The fix is to send TERM first and use KILL only if the process does not stop; and to make the script check whether the PID in an old lock is still alive before refusing to start. <code>kill nginx</code> fails because kill takes PIDs; use <code>pkill -x nginx</code> or, for a service, <code>systemctl reload/stop nginx</code>.') + qc('What exit status does a process have after kill -9?', '137 (128 + 9).') + '''
</section>
'''

_sh.run_sh(KILL + '; rm -rf ~/sg ~/job.sh ~/job.lock ~/crit.sh ~/svc.sh ~/e.sh ~/lockjob.*', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-what-is-a-process-pid-ppid-fork-exec/">Lesson 11.1</a> (processes) and <a href="../02-watching-processes-ps-pstree-top-and-htop/">Lesson 11.2</a> (finding PIDs with ps and pgrep).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
