import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='11-processes', lesson='03-signals-kill-pkill-killall-sigterm-vs-sigkill', n='11.3',
    module_label='Module 11 · Processes',
    title='Signals: kill, pkill and killall, SIGTERM vs SIGKILL, and trap',
    desc='Linux signals from zero: what a signal is, HUP INT QUIT KILL TERM STOP CONT TSTP USR1 PIPE CHLD and their default actions; kill, kill -l, kill -0, pkill -x -f -u -n -o, killall -w -i; STOP/CONT; exit codes 130, 137, 143; trap with EXIT, INT, TERM, HUP; /proc SigCgt; graceful stop patterns used by systemd and Docker; real outputs and 30+ examples.',
    og_desc='Linux signals and kill, pkill, killall explained with real runs: SIGTERM vs SIGKILL, exit codes, trap and graceful shutdown.',
    minutes=40, level='Beginner → Advanced',
    lead='kill does not kill: it sends a signal. Learn the signals, why TERM comes before KILL, how to select processes by PID or name safely, and how trap lets your scripts clean up.',
    chips=['TERM vs KILL animated', 'Exit codes decoded', 'trap cleanup patterns', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Signals in a sandbox: start, signal, check
sleep 60 &
p=$!
kill -0 $p && echo "PID $p is alive"
kill -TERM $p
wait $p
echo "exit status $? = $(kill -l $?)"
trap 'echo "caught INT, cleaning up"' INT
kill -INT $$
echo "script continued"
"""

RUN = dict(
    heading='Send TERM, read the status, catch INT',
    intro='<p>Start a background sleep, check it, send TERM, decode the exit status, and catch a signal sent to this shell.</p>',
    code=MAIN,
    anno=[('kill -l $?', 'Turns 143 back into TERM.'), ("trap '…' INT", 'Our handler runs instead of stopping.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which number does TERM give?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what status after kill -9?',
             code="sleep 60 &\np=$!\nkill -9 $p\nwait $p\necho \"status $?\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> kill needs a PID. Use pkill -x sleep instead.',
             code="sleep 60 &\nkill sleep\n", expect='any'),
        dict(label='4 · Your turn', hint='Make cleanup run when the script ends.',
             code="tmp=$(mktemp)\ntrap 'rm -f \"$tmp\"; echo \"removed $tmp\"' EXIT\necho data > \"$tmp\"\necho \"working with $tmp\"\n"),
        dict(label='5 · Challenge', hint='Pause a busy loop with STOP and resume it with CONT; check the state each time.',
             code="(while :; do :; done) &\np=$!\nsleep 0.5; ps -o stat= -p $p\nkill -STOP $p; sleep 0.3; ps -o stat= -p $p\nkill -CONT $p; sleep 0.3; ps -o stat= -p $p\nkill $p\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real services',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical. Commands with sudo affect the whole system; try them on a practice VM.</p>',
    items=[
        dict(title='1 · All signals', cmd='kill -l', output=pc('kill -l | head -3'), note='Recorded (first lines).'),
        dict(title='2 · Reload nginx with HUP', cmd='sudo kill -HUP $(cat /run/nginx.pid)   # same as: sudo systemctl reload nginx', output='(no output; error.log shows: signal 1 (SIGHUP) received, reconfiguring)', note='Typical.'),
        dict(title='3 · What does a service catch?', cmd='grep SigCgt /proc/$(pgrep -o sshd)/status', output='SigCgt:\t0000000000004a03', note='Typical: bits for HUP, INT, TERM, CHLD.'),
        dict(title='4 · An OOM kill in the log', cmd='sudo dmesg | grep -i "killed process" | tail -1', output='Out of memory: Killed process 23110 (java) total-vm:8123456kB …', note='Typical. The exit status of that process was 137.'),
    ],
)

TRACE = dict(
    heading='A signal arriving, line by line',
    intro='<p>Step through: install a handler, signal ourselves, see the handler run, then restore the default.</p>',
    code='''count=0
trap 'count=$((count+1)); echo "USR1 #$count"' USR1
kill -USR1 $$
kill -USR1 $$
trap - USR1
echo "handled $count signals"
''',
    notes={2: 'Handler for USR1.', 3: 'Handler runs.', 5: 'Back to the default.'},
)

WORKED_INTRO = 'Three tasks from real jobs: decoding exit codes, a graceful stop and a service-style script.'
EXAMPLES = [
    dict(level='b', tag='Support', title='Decode job exit codes',
         problem='<p>A scheduler reports exit codes 0, 1, 130, 137 and 143. Explain each one automatically.</p>',
         inp='codes', approach=['>128 → signal.', 'kill -l.'],
         code='''for c in 0 1 130 137 143; do
  if (( c > 128 )); then echo "$c: killed by SIG$(kill -l $((c - 128)))"
  elif (( c == 0 )); then echo "$c: success"
  else echo "$c: program error"; fi
done
''', notes={2: '128 + signal number.'}, tryit='Add 124 (timeout) and 141 (PIPE).'),
    dict(level='i', tag='DevOps', title='Stop gracefully with a deadline',
         problem='<p>Stop a process with TERM, wait up to 3 seconds, then KILL, and report which one worked.</p>',
         inp='a PID', approach=['kill, poll kill -0.', 'kill -9 if needed.'],
         code='''bash -c "trap '' TERM; sleep 30" &
p=$!; sleep 0.3
kill "$p"
for i in 1 2 3; do kill -0 "$p" 2>/dev/null || break; sleep 1; done
if kill -0 "$p" 2>/dev/null; then kill -9 "$p"; echo "TERM ignored, used KILL"; else echo "stopped by TERM"; fi
''', notes={1: 'A process that ignores TERM.', 5: 'Force only if still alive.'}, tryit='Remove the trap so TERM works.'),
    dict(level='a', tag='Developer', title='A daemon-style script',
         problem='<p>Write a loop that counts work, reloads on HUP and prints a summary on TERM.</p>',
         inp='signals', approach=['trap HUP / TERM.', 'wait for sleep.'],
         code='''work=0
trap 'echo "HUP: reload config"' HUP
trap 'echo "TERM: did $work units, exiting"; exit 0' TERM
( sleep 0.5; kill -HUP $$; sleep 0.5; kill -TERM $$ ) &
while :; do work=$((work + 1)); sleep 0.1; done
''', notes={4: 'A helper sends the signals to us.', 5: 'Signals arrive between commands.'}, tryit='Add USR1 to print the current count.'),
]

QUIZ = mix([
    dict(q='kill PID sends which signal by default?', options=['KILL', 'TERM', 'HUP', 'INT'], answer=1, why='15.'),
    dict(q='Which signal cannot be caught?', options=['TERM', 'INT', 'KILL', 'HUP'], answer=2, why='Also STOP.'),
    dict(q='Ctrl+C sends…', options=['TERM', 'INT', 'QUIT', 'TSTP'], answer=1, why='SIGINT.'),
    dict(q='Exit status 137 means…', options=['not found', 'killed by KILL', 'killed by TERM', 'success'], answer=1, why='128+9.'),
    dict(q='Reload a daemon’s config is usually…', options=['KILL', 'HUP', 'STOP', 'PIPE'], answer=1, why='HUP.'),
    dict(q='kill -0 PID…', options=['kills PID 0', 'checks the PID exists', 'sends KILL', 'lists signals'], answer=1, why='No signal sent.'),
    dict(q='Safest way to stop all processes named exactly worker?', options=['kill worker', 'pkill worker', 'pkill -x worker', 'killall -9 w'], answer=2, why='-x exact.'),
    dict(q="trap '…' EXIT does NOT run after…", options=['exit 0', 'Ctrl+C', 'kill PID', 'kill -9 PID'], answer=3, why='KILL runs no code.'),
])

REVISION = [
    'A signal is a numbered message; kill sends one (TERM by default).',
    'HUP 1 reload/hang-up, INT 2 Ctrl+C, QUIT 3, KILL 9, USR1 10, PIPE 13, TERM 15, CHLD 17, CONT 18, STOP 19, TSTP 20.',
    'TERM first, wait, check with kill -0, KILL only if needed. KILL and STOP cannot be caught.',
    'pkill/pgrep: -x exact, -f full command, -u user, -n/-o newest/oldest; preview with pgrep -a. killall: exact name.',
    'Exit status 128+n: 130 INT, 137 KILL, 143 TERM; kill -l n translates.',
    "trap 'cmds' TERM INT HUP; trap … EXIT for cleanup; trap '' SIG ignores; trap - SIG restores.",
]

FAQ = [
    ('What is a signal in Linux?', 'A numbered notification sent to a process by the kernel or another process, such as SIGTERM or SIGKILL.'),
    ('What is the difference between kill -9 and kill -15?', '15 (TERM) can be caught so the program can clean up; 9 (KILL) cannot be caught and stops it immediately.'),
    ('How do I kill a process by name?', 'pkill -x name or killall name; preview with pgrep -a.'),
    ('Why does a process not die with kill -9?', 'It is in D state (waiting on I/O) or a zombie that its parent has not reaped.'),
    ('What does exit code 137 mean?', 'Killed by SIGKILL (128+9), often the OOM killer in containers.'),
    ('How do I clean up when a bash script is stopped?', "Use trap 'cleanup' EXIT (and INT/TERM)."),
    ('What does kill -HUP do?', 'Sends SIGHUP; many daemons reload their configuration.'),
]

PRACTICE_INTRO = 'Small signal tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Name of 15', stmt='Print the name of signal 15.', inp='nothing', code="kill -l 15\n", explain='TERM.'),
    dict(level='easy', title='Number of KILL', stmt='Print the number of KILL.', inp='nothing', code="kill -l KILL\n", explain='9.'),
    dict(level='easy', title='Alive?', stmt='Check whether your own shell ($$) exists with kill -0.', inp='nothing', code="kill -0 $$ && echo alive\n", explain='alive.'),
    dict(level='medium', title='Status after TERM', stmt='Start sleep 30 in the background, TERM it and print the exit status.', inp='nothing', code="sleep 30 & p=$!; kill $p; wait $p; echo $?\n", explain='143.'),
    dict(level='medium', title='Decode', stmt='Print the signal name for exit status 130.', inp='130', code="kill -l $((130 - 128))\n", explain='INT.'),
    dict(level='medium', title='Ignore', stmt='Ignore INT, send INT to yourself, print still here.', inp='nothing', code="trap '' INT; kill -INT $$; echo still here\n", explain='Ignored.'),
    dict(level='business', title='Cleanup', stmt='Create a temp file and remove it with an EXIT trap in a child bash; then show it is gone.', inp='nothing', code="f=$(bash -c 't=$(mktemp); trap \"rm -f $t\" EXIT; echo $t'); [ -e \"$f\" ] || echo removed\n", explain='EXIT ran.'),
    dict(level='business', title='Count before kill', stmt='Start two sleeps, print how many pkill -x sleep would hit, then kill them.', inp='nothing', code="sleep 30 & sleep 31 & sleep 0.2; pgrep -c -P $$ -x sleep; pkill -P $$ -x sleep\n", explain='2.'),
]

SCN_INTRO = 'Interview questions about signals, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you kill a process?”', 'Very common.', 'steps?',
        '''<ul>
          <li>Find the PID: pgrep -a name / ps aux.</li>
          <li>kill PID (TERM); check; kill -9 PID only if needed.</li>
          <li>By name: pkill -x name.</li>
        </ul>''', '“kill -9 everything”.') +
    scn('Service company', 'Junior', 'App leaves a lock file after a restart', 'Ops use kill -9.', 'fix?',
        '''<ol>
          <li>Use TERM and give it time.</li>
          <li>Add trap cleanup EXIT in scripts.</li>
          <li>On start, check if the PID in the lock is alive (kill -0) before refusing.</li>
        </ol>''', 'deleting locks by hand every morning.') +
    scn('Cloud / Kubernetes', 'Mid-level', 'Pods exit with code 137', 'Random restarts.', 'cause?',
        '''<ul>
          <li>137 = SIGKILL: OOM killer or the grace period expired.</li>
          <li>Check kubectl describe (OOMKilled) and memory limits.</li>
          <li>Handle TERM to shut down within terminationGracePeriodSeconds.</li>
        </ul>''', 'raising CPU limits.') +
    scn('Platform', 'Senior', 'kill -9 does not remove a process', 'State D in ps.', 'why?',
        '''<ul>
          <li>D = uninterruptible sleep in the kernel (often NFS or a dying disk).</li>
          <li>The signal is pending until the I/O returns.</li>
          <li>Fix the storage path; sometimes only a reboot clears it.</li>
        </ul>''', 'kill -9 harder.')
) + interview([
    ('What does SIGHUP do?', 'Hang-up; daemons often reload config.'),
    ('Which signals cannot be caught?', 'KILL and STOP.'),
    ('What is Ctrl+Z?', 'SIGTSTP: suspend.'),
    ('How to kill a process group?', 'kill -- -PGID.'),
    ('How does systemctl stop work?', 'TERM, wait TimeoutStopSec, then KILL.'),
    ('What is SIGCHLD?', 'Sent to a parent when a child ends.'),
    ('Can you kill a zombie?', 'No; reap it via its parent.'),
], [
    ('RHCSA (EX200)', 'Identify CPU/memory intensive processes and kill processes.'),
    ('LFCS', 'Manage processes and signals.'),
    ('CompTIA Linux+', 'kill, pkill, killall, signals.'),
]) + distro('Signals are the same on all Linux systems; tools differ slightly.', [
    ('kill / pkill', 'procps', 'procps-ng', 'BSD versions', '-'),
    ('killall', 'psmisc', 'psmisc', 'BSD killall', 'Solaris: kills ALL'),
    ('Signal numbers', 'x86 Linux', 'same', 'some differ (USR1=30)', '-'),
    ('Service stop', 'systemctl', 'systemctl', 'launchctl', '-'),
    ('Windows', '-', '-', '-', 'taskkill /PID'),
]) + teaser('11.4', 'Riya starts a long download, presses Ctrl+Z by accident and the progress stops. Later she closes the terminal and her job dies with it. Next: foreground and background jobs, fg, bg, jobs, disown and nohup.')

CHEATSHEET = cheatsheet('Signals', [
    ('Send', [('kill PID', 'TERM'), ('kill -9 PID', 'KILL'), ('kill -HUP PID', 'reload'), ('kill -0 PID', 'alive?'), ('kill -l', 'list')]),
    ('By name', [('pgrep -a -x n', 'preview'), ('pkill -x n', 'exact'), ('pkill -f text', 'command line'), ('pkill -u user', 'user'), ('killall -w n', 'wait')]),
    ('Numbers', [('1 HUP', 'reload'), ('2 INT', 'Ctrl+C'), ('9 KILL', 'force'), ('15 TERM', 'default'), ('19 STOP / 18 CONT', 'pause')]),
    ('trap / codes', [("trap '…' EXIT", 'cleanup'), ("trap '' INT", 'ignore'), ('trap - INT', 'default'), ('130/137/143', 'INT/KILL/TERM')]),
])

MINDMAP = mindmap('Signals', [
    ('What', 'blue', ['numbered message', 'kernel delivers', 'kill(2)']),
    ('Common', 'amber', ['HUP INT', 'TERM KILL', 'STOP CONT']),
    ('Send', 'green', ['kill PID', 'pkill -x', 'killall']),
    ('Handle', 'violet', ['trap', 'EXIT', 'ignore']),
    ('Codes', 'red', ['128+n', '137 KILL', '143 TERM']),
    ('Rules', 'acc', ['TERM first', 'kill -0', 'preview pgrep']),
])

LAB = lab('stop the right processes', 'Build the lab (it starts four processes), do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab113 && cd ~/lab113 && rm -f *.txt *.sh
pkill -u "$USER" -f 'lab113-|lab113/svc'; true
(exec -a lab113-keep sleep 600 &)
(exec -a lab113-drop sleep 601 &); (exec -a lab113-drop sleep 602 &)
cat > svc.sh <<'EOF'
trap 'echo reloaded >> ~/lab113/svc.log' HUP
while :; do sleep 0.2; done
EOF
(setsid bash ~/lab113/svc.sh > /dev/null 2>&1 &)
sleep 1''',
    tasks=['Stop both processes whose command line contains <code>lab113-drop</code> with TERM, leaving <code>lab113-keep</code> running.',
           'Send HUP to the process running <code>svc.sh</code> so it writes <code>reloaded</code> into <code>svc.log</code> (it must keep running).',
           'Write the exit status a process gets when killed by SIGTERM into <code>term.txt</code> (use a real test, not typing).',
           'Write the signal name for number 9 into <code>nine.txt</code> using kill -l.'],
    solution='''pkill -f lab113-drop
pkill -HUP -f lab113/svc.sh
sleep 30 & p=$!; kill $p; wait $p; echo $? > ~/lab113/term.txt
kill -l 9 > ~/lab113/nine.txt''',
    check='''cd ~/lab113; sleep 0.5
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 drop"  '[ "$(pgrep -c -f lab113-drop)" = 0 ] && [ "$(pgrep -c -f lab113-keep)" = 1 ]'
ok "2 hup"   'grep -q reloaded svc.log 2>/dev/null && pgrep -f lab113/svc.sh > /dev/null'
ok "3 term"  '[ "$(cat term.txt 2>/dev/null)" = 143 ]'
ok "4 nine"  '[ "$(cat nine.txt 2>/dev/null)" = KILL ]' ''')
