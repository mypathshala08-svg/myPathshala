import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='11-processes', lesson='04-foreground-and-background-jobs-and-nohup', n='11.4',
    module_label='Module 11 · Processes',
    title='Foreground and background jobs: &, Ctrl+Z, jobs, fg, bg, wait, nohup, disown and setsid',
    desc='Linux job control from zero: foreground vs background, & and $!, jobs -l, Ctrl+Z (SIGTSTP), bg, fg, %1 %+ %- %name, wait and wait -n, why logout kills jobs (SIGHUP, sessions, process groups), nohup and nohup.out, disown -h, setsid, SIGTTIN; real interactive terminal screens, parallel scripts and 30+ examples.',
    og_desc='Background jobs, Ctrl+Z, fg, bg, nohup and disown explained with real terminal screens and outputs.',
    minutes=40, level='Beginner → Advanced',
    lead='Run several jobs from one terminal, pause and resume them, run tasks in parallel, and keep long jobs alive after you log out, with real recorded terminal screens.',
    chips=['Real terminal screens', 'Logout and SIGHUP animated', 'Parallel jobs with wait', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Background jobs and wait
( sleep 1; echo "job A finished" ) &
a=$!
( sleep 0.5; echo "job B finished" ) &
b=$!
echo "started A=$a and B=$b"
jobs
wait $a
echo "A exit status: $?"
wait
echo "all done"
"""

RUN = dict(
    heading='Start, list and wait for jobs',
    intro='<p>Start two background jobs, list them, and wait for each. (The browser has no keyboard job control; Ctrl+Z, bg and fg are shown on the real screens above.)</p>',
    code=MAIN,
    anno=[('a=$!', 'PID of the job just started.'), ('wait $a', 'Wait for one job and get its status.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which job finishes first?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how long does this take, 1 s or 3 s?',
             code="start=$SECONDS\nfor i in 1 2 3; do sleep 1 & done\nwait\necho \"took $((SECONDS - start)) s\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> kill 1 targets PID 1. Use %1.',
             code="sleep 30 &\nkill 1 2>&1\nkill %1 && echo 'job 1 stopped'\n", expect='any'),
        dict(label='4 · Your turn', hint='Get the exit status of a background job that fails.',
             code="( sleep 0.2; exit 7 ) &\nwait $!\necho \"status $?\"\n"),
        dict(label='5 · Challenge', hint='Run 6 tasks, never more than 2 at a time.',
             code="for i in 1 2 3 4 5 6; do\n  ( sleep 0.3; echo \"task $i\" ) &\n  (( $(jobs -rp | wc -l) >= 2 )) && wait -n\ndone\nwait\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: a real logout test',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Ctrl+Z in your terminal', cmd='sleep 300   # then press Ctrl+Z, then type: bg; jobs', output='^Z\n[1]+  Stopped                 sleep 300\n[1]+ sleep 300 &\n[1]+  Running                 sleep 300 &', note='Recorded (see the live screens above).'),
        dict(title='2 · Logout test over SSH', cmd='ssh you@server "sleep 300 & nohup sleep 301 > /dev/null 2>&1 &"; ssh you@server pgrep -a sleep', output='4811 sleep 301', note='Typical: only the nohup job is left after the first SSH session ends.'),
        dict(title='3 · Exiting with stopped jobs', cmd='sleep 300   # Ctrl+Z, then type: exit', output='exit\nThere are stopped jobs.', note='Typical. A second exit kills them.'),
        dict(title='4 · logind setting', cmd='grep -i KillUserProcesses /etc/systemd/logind.conf', output=pc('grep -i KillUserProcesses /etc/systemd/logind.conf || echo "#KillUserProcesses=no"'), note='Recorded. If yes, even nohup jobs are killed at logout (use systemd-run --user or lingering).'),
    ],
)

TRACE = dict(
    heading='Background jobs, line by line',
    intro='<p>Step through: start, remember the PID, check, wait.</p>',
    code='''( sleep 0.3; exit 4 ) &
pid=$!
running=$(jobs -rp | wc -l)
wait $pid
status=$?
echo "pid kept, $running running, status $status"
''',
    notes={1: 'Runs behind.', 2: 'Save the PID at once.', 4: 'Blocks until it ends.', 5: '4 from exit 4.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a parallel health check, a progress watcher and a fail-fast pipeline.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Check several servers in parallel',
         problem='<p>Simulate pinging four servers at the same time and print the results.</p>',
         inp='host names', approach=['One background job per host.', 'wait.'],
         code='''for h in web01 web02 db01 cache01; do
  ( sleep 0.$((RANDOM % 5 + 1)); echo "$h: reachable" ) &
done
wait
echo "checked 4 hosts"
''', notes={2: 'Random delay stands in for the network.'}, tryit='Make db01 fail and count failures.'),
    dict(level='i', tag='Developer', title='Show progress while a job runs',
         problem='<p>Start a slow job in the background and print a dot every 0.2 s until it ends.</p>',
         inp='a slow job', approach=['$! and kill -0 loop.'],
         code='''( sleep 1 ) &
p=$!
while kill -0 "$p" 2>/dev/null; do printf '.'; sleep 0.2; done
wait "$p"; echo " done (status $?)"
''', notes={3: 'Poll until the PID is gone.'}, tryit='Print the elapsed seconds instead of dots.'),
    dict(level='a', tag='DevOps', title='Fail fast: stop all parts when one fails',
         problem='<p>Run three jobs; if any fails, stop the others immediately.</p>',
         inp='jobs', approach=['wait -n in a loop.', 'kill $(jobs -p).'],
         code='''( sleep 2; echo slow ok ) &
( sleep 0.3; echo "bad part failed"; exit 1 ) &
( sleep 2; echo other ok ) &
while (( $(jobs -rp | wc -l) > 0 )); do
  if ! wait -n; then echo "a part failed: stopping the rest"; kill $(jobs -p) 2>/dev/null; break; fi
done
wait 2>/dev/null; echo "finished"
''', notes={5: 'First failure → kill the others.'}, tryit='Remove exit 1 and watch all finish.'),
]

QUIZ = mix([
    dict(q='Which runs a command in the background?', options=['cmd |', 'cmd &', 'cmd &&', 'bg cmd'], answer=1, why='&.'),
    dict(q='Ctrl+Z…', options=['ends the job', 'stops (pauses) the job', 'logs out', 'sends HUP'], answer=1, why='SIGTSTP.'),
    dict(q='Continue a stopped job in the background:', options=['fg', 'bg', 'jobs', 'wait'], answer=1, why='bg.'),
    dict(q='$! contains…', options=['last exit status', 'PID of the last background job', 'shell PID', 'job count'], answer=1, why='$!.'),
    dict(q='Why does cmd & die at logout?', options=['it runs out of memory', 'the shell passes SIGHUP to it', 'cron kills it', '& has a timeout'], answer=1, why='HUP.'),
    dict(q='nohup without a redirect writes output to…', options=['/dev/null', 'nohup.out', 'syslog', 'the screen'], answer=1, why='nohup.out.'),
    dict(q='A job is already running; make it survive logout:', options=['nohup %1', 'disown %1', 'fg %1', 'wait %1'], answer=1, why='disown.'),
    dict(q='In a script, fg says…', options=['nothing', 'no job control', 'permission denied', 'command not found'], answer=1, why='Job control is off.'),
])

REVISION = [
    'cmd & runs in the background; $! is its PID; jobs -l lists jobs; wait waits and returns status.',
    'Ctrl+Z stops (TSTP); bg continues behind, fg in front; %1 %+ %- %name select jobs; kill %1.',
    'Closing the terminal sends SIGHUP to the shell, which passes it to its jobs: plain & jobs die.',
    'nohup cmd > log 2>&1 & (ignores HUP); cmd & disown (forget the job); setsid cmd (new session).',
    'Background jobs that read the keyboard are stopped (SIGTTIN); redirect output and input.',
    'Scripts have no job control: use &, wait, wait -n, kill; for interactive long work use tmux.',
]

FAQ = [
    ('How do I run a command in the background in Linux?', 'Add & at the end: cmd &. Use jobs to list and fg to bring it back.'),
    ('What does Ctrl+Z do?', 'It stops (pauses) the foreground job with SIGTSTP; bg or fg continues it.'),
    ('What is the difference between nohup and &?', '& only runs in the background; nohup makes the command ignore SIGHUP so it survives logout.'),
    ('What is nohup.out?', 'The file nohup appends output to when output is a terminal; redirect to avoid it.'),
    ('How do I keep a running job alive after logout?', 'disown it (or disown -h), or start it with nohup/setsid, or use tmux.'),
    ('How do I wait for background jobs in a script?', 'wait (all), wait PID (one), wait -n (the next one).'),
    ('Why does fg not work in my script?', 'Scripts run without job control; use wait and kill, or set -m.'),
]

PRACTICE_INTRO = 'Small job tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Background', stmt='Start sleep 1 in the background and print “started”.', inp='nothing', code="sleep 1 & echo started\n", explain='The prompt returns at once.'),
    dict(level='easy', title='Count jobs', stmt='Start two sleeps and print how many jobs are running.', inp='nothing', code="sleep 2 & sleep 2 & jobs -r | wc -l; kill $(jobs -p)\n", explain='2.'),
    dict(level='easy', title='Wait', stmt='Start a job that prints done after 0.2 s, wait for it, print end.', inp='nothing', code="( sleep 0.2; echo done ) & wait; echo end\n", explain='done, end.'),
    dict(level='medium', title='Status', stmt='Background job exits 3; print its status.', inp='nothing', code="( exit 3 ) & wait $!; echo $?\n", explain='3.'),
    dict(level='medium', title='Parallel time', stmt='Four 1-second sleeps in parallel: print the seconds taken.', inp='nothing', code="s=$SECONDS; for i in 1 2 3 4; do sleep 1 & done; wait; echo $((SECONDS - s))\n", explain='About 1.'),
    dict(level='medium', title='Kill a job', stmt='Start sleep 30 and stop it with its job number.', inp='nothing', code="sleep 30 & kill %1; wait; echo stopped\n", explain='%1.'),
    dict(level='business', title='Failures', stmt='Run true, false, false in the background and count failures.', inp='nothing', code="f=0; for c in true false false; do $c & done; for p in $(jobs -p); do wait $p || f=$((f+1)); done; echo $f\n", explain='2.'),
    dict(level='business', title='nohup status', stmt='Run false under nohup with output discarded and print the status.', inp='nothing', code="nohup false > /dev/null 2>&1; echo $?\n", explain='1: nohup passes the status on.'),
]

SCN_INTRO = 'Interview questions about jobs and nohup, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you run a process in the background?”', 'Very common.', 'and bring it back?',
        '''<ul>
          <li>cmd &amp;; jobs; fg %1.</li>
          <li>Ctrl+Z then bg for a running command.</li>
          <li>kill %1 to stop it.</li>
        </ul>''', 'opening another terminal.') +
    scn('Service company', 'Junior', 'A script stops when the SSH session ends', 'Started with &.', 'fix?',
        '''<ol>
          <li>nohup ./job.sh &gt; job.log 2&gt;&amp;1 &amp;</li>
          <li>Or tmux, so you can reattach.</li>
          <li>For permanent jobs: a systemd service.</li>
        </ol>''', 'keeping the laptop open all night.') +
    scn('Product company', 'Mid-level', 'A cron/CI script must run 20 tasks fast', 'Serial takes 20 min.', 'how?',
        '''<ul>
          <li>Background jobs with a limit (jobs -rp + wait -n), or xargs -P.</li>
          <li>Collect statuses with wait PID; fail if any failed.</li>
          <li>Log each task separately.</li>
        </ul>''', 'starting 20 jobs at once with no limit.') +
    scn('Platform', 'Senior', 'nohup jobs still die at logout on a new server', 'Same command worked before.', 'why?',
        '''<ul>
          <li>systemd-logind KillUserProcesses=yes kills the whole user scope.</li>
          <li>Use loginctl enable-linger, systemd-run --user, or a service.</li>
          <li>Check logind.conf and the distro default.</li>
        </ul>''', 'blaming nohup.')
) + interview([
    ('What does disown do?', 'Removes a job from the shell’s job table so it is not sent HUP.'),
    ('What is %+?', 'The current job.'),
    ('What happens if a background job reads input?', 'It is stopped by SIGTTIN.'),
    ('wait vs sleep?', 'wait blocks until jobs end; sleep waits a fixed time.'),
    ('What is setsid?', 'Starts a program in a new session without a terminal.'),
    ('What does “There are stopped jobs” mean?', 'You tried to exit with stopped jobs; exit again to kill them.'),
    ('nohup vs tmux?', 'nohup survives but you cannot reattach; tmux lets you come back.'),
], [
    ('RHCSA (EX200)', 'Manage processes: background, foreground, jobs.'),
    ('LFCS', 'Use job control: &, fg, bg, jobs, nohup.'),
    ('CompTIA Linux+', 'Job control and nohup.'),
]) + distro('Job control is a shell feature; it works the same on every Linux.', [
    ('&, jobs, fg, bg', 'bash', 'bash', 'zsh/bash', 'Git Bash (partly)'),
    ('nohup', 'coreutils', 'coreutils', 'BSD nohup', '-'),
    ('setsid', 'util-linux', 'util-linux', 'not built in', '-'),
    ('KillUserProcesses', 'no', 'no (default)', '-', '-'),
    ('Windows', '-', '-', '-', 'Start-Job / start /b'),
]) + teaser('11.5', 'Riya’s nightly report uses all the CPU and the website slows down. She does not want to kill it, just make it polite. Next: process priority with nice and renice, and a look at ionice.')

CHEATSHEET = cheatsheet('Jobs', [
    ('Start / list', [('cmd &', 'background'), ('$!', 'its PID'), ('jobs -l', 'list'), ('jobs -p', 'PIDs')]),
    ('Move', [('Ctrl+Z', 'stop'), ('bg [%n]', 'behind'), ('fg [%n]', 'front'), ('%1 %+ %-', 'select'), ('kill %1', 'signal')]),
    ('Scripts', [('wait', 'all'), ('wait PID', 'one + status'), ('wait -n', 'next'), ('jobs -rp', 'running')]),
    ('Survive logout', [('nohup cmd > log 2>&1 &', 'new'), ('disown [-h] %1', 'existing'), ('setsid cmd', 'detached'), ('tmux', 'reattach')]),
])

MINDMAP = mindmap('Jobs', [
    ('Run', 'blue', ['cmd &', '$!', 'jobs']),
    ('Move', 'amber', ['Ctrl+Z', 'bg fg', '%1 %+']),
    ('Wait', 'green', ['wait', 'wait PID', 'wait -n']),
    ('Logout', 'red', ['SIGHUP', 'session', 'job dies']),
    ('Survive', 'violet', ['nohup', 'disown', 'setsid']),
    ('Traps', 'acc', ['nohup.out', 'kill 1', 'no job control']),
])

LAB = lab('jobs that survive', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab114 && cd ~/lab114 && rm -f *.txt *.log nohup.out
pkill -u "$USER" -f 'lab114-'; true''',
    tasks=['Start <code>bash -c \'exec -a lab114-keep sleep 600\'</code> with nohup, in the background, with output going to <code>keep.log</code> (no nohup.out).',
           'Run three background jobs that each sleep 1 second, wait for <b>those three</b>, and write the total seconds taken (an integer, at most 2) into <code>time.txt</code>. Careful: a plain <code>wait</code> would also wait for the 600-second job from task 1.',
           'Run <code>( exit 5 ) &amp;</code>, wait for it, and write its exit status into <code>status.txt</code>.',
           'Write the name of the signal a terminal sends to its jobs on hang-up (as kill -l prints it) into <code>hup.txt</code>.'],
    solution='''cd ~/lab114
nohup bash -c 'exec -a lab114-keep sleep 600' > keep.log 2>&1 &
s=$SECONDS; pids=(); for i in 1 2 3; do sleep 1 & pids+=($!); done; wait "${pids[@]}"; echo $((SECONDS - s)) > time.txt
( exit 5 ) & wait $!; echo $? > status.txt
kill -l 1 > hup.txt''',
    check='''cd ~/lab114; sleep 0.3
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
p=$(pgrep -f lab114-keep | head -1)
ok "1 nohup"  '[ -n "$p" ] && [ -e keep.log ] && [ ! -e nohup.out ] && (( 0x$(awk "/SigIgn/{print \\$2}" /proc/$p/status) & 1 ))'
ok "2 time"   't=$(cat time.txt 2>/dev/null); [ -n "$t" ] && [ "$t" -ge 1 ] && [ "$t" -le 2 ]'
ok "3 status" '[ "$(cat status.txt 2>/dev/null)" = 5 ]'
ok "4 hup"    '[ "$(cat hup.txt 2>/dev/null)" = HUP ]'
pkill -f lab114-keep; true''')
