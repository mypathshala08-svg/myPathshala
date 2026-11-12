import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='11-processes', lesson='01-what-is-a-process-pid-ppid-fork-exec', n='11.1',
    module_label='Module 11 · Processes, jobs and signals',
    title='What is a process? PID, PPID, fork, exec and process states',
    desc='Program vs process vs thread; PID, PPID, UID and state; how every command starts with fork (clone), exec (execve), wait and exit status; process states R, S, D, T, Z, I and ps STAT letters; zombies and orphans demonstrated for real; $$, $PPID, $!, $BASHPID; exec and source; /proc/PID; strace of a command starting, with animations.',
    og_desc='What a Linux process really is: PID and PPID, fork and exec, states, zombies and orphans, with real outputs and animations.',
    minutes=40, level='Beginner → Advanced',
    lead='Every command you run becomes a process: a program in memory with a number, a parent, an owner and a state. This lesson shows how fork, exec and wait start every command, what the state letters mean, and where zombies and orphans come from.',
    chips=['fork → exec → wait animated', 'A real zombie', 'strace of a command', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Who am I, who started me?
echo "my shell: $$"
bash -c 'echo "child: $$, parent: $PPID"'
sleep 30 &
echo "background job: $!"
ps -o pid,ppid,stat,cmd -p $$,$!
kill $!
"""

RUN = dict(
    heading='See PIDs, parents and states',
    intro='<p>Print your shell’s PID, start a child and a background job, and look at them with ps.</p>',
    code=MAIN,
    anno=[("bash -c 'echo \"child: $$, parent: $PPID\"'", 'A child: its parent is your shell.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which PID is the parent of the child?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> will $$ print the same number inside ( )? And $BASHPID? Then run.',
             code="echo \"$$ $BASHPID\"\n( echo \"$$ $BASHPID\" )\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is to change the folder of THIS shell. Fix the last two lines.',
             code="printf 'cd /tmp\\n' > go.sh\nbash go.sh\npwd\n"),
        dict(label='4 · Your turn', hint='Pause a background sleep and show its state letter.',
             code="sleep 30 & p=$!; sleep 0.1\nkill -STOP $p; ps -o stat= -p $p\nkill -CONT $p; kill $p\n"),
        dict(label='5 · Challenge', hint='Print the parent PID of a background job, without a header.',
             code="sleep 30 & p=$!; sleep 0.1\nps -o ppid= -p $p | tr -d ' '\necho \"(shell is $$)\"; kill $p\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own processes',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Who is PID 1?', cmd='ps -o pid,comm -p 1', output='    PID COMMAND\n      1 systemd', note='Typical on any systemd distribution.'),
        dict(title='2 · Your shell’s ancestry', cmd='pstree -s -p $$', output='systemd(1)───systemd(1203)───gnome-terminal-(2511)───bash(2530)───pstree(2601)', note='Typical: the chain differs for SSH, VS Code, WSL.'),
        dict(title='3 · Max PID', cmd='cat /proc/sys/kernel/pid_max', output=pc('cat /proc/sys/kernel/pid_max'), note='Recorded.'),
        dict(title='4 · Any zombies?', cmd="ps -eo pid,ppid,stat,cmd | awk '$3 ~ /^Z/'", output='', note='Typical: nothing.'),
    ],
)

TRACE = dict(
    heading='A child and its exit status',
    intro='<p>Step through: a child process runs, exits with a status, and the parent collects it.</p>',
    code='''echo "parent $$"
bash -c 'exit 3'
code=$?
echo "child exited with $code"
bash -c 'echo "child $$, my parent is $PPID"'
echo "back in the parent, last status $?"
''',
    notes={1: 'Parent :: our shell.', 2: 'Child :: fork + exec bash, exits 3.', 3: 'wait :: the status arrives in $?.', 5: 'Another child :: its PPID is our shell.', 6: 'Back :: the child exited 0.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s wrapper, an admin’s ancestry check and a container zombie.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Run a script in the current shell',
         problem='<p>A script sets a variable. Show that running it does not keep the variable, but sourcing it does.</p>',
         inp='a small script', approach=['bash = child.', 'source = current shell.'],
         code='''printf 'APP_ENV=prod\\n' > env.sh
bash env.sh; echo "after bash: [$APP_ENV]"
source env.sh; echo "after source: [$APP_ENV]"
''', notes={2: 'Child :: variable lost.', 3: 'Same shell :: kept.'}, tryit='Try . env.sh (dot) instead of source.'),
    dict(level='i', tag='Admin', title='Who started this process?',
         problem='<p>Print a background process’s PID, its parent’s PID and the parent’s command.</p>',
         inp='a background job', approach=['ps -o ppid=.', 'ps -o comm= of the parent.'],
         code='''sleep 30 & p=$!; sleep 0.1
pp=$(ps -o ppid= -p $p | tr -d ' ')
echo "child sleep, parent is: $(ps -o comm= -p $pp)"
kill $p
''', notes={2: 'Parent PID.', 3: 'Parent name :: bash.'}, tryit='Walk one more level up.'),
    dict(level='a', tag='DevOps', title='Make and spot a zombie',
         problem='<p>Create a parent that never reaps its child and find the zombie by its state.</p>',
         inp='nothing', approach=['exec replaces the parent with a program that never waits.', 'awk on STAT.'],
         code='''bash -c 'sleep 0.1 & exec sleep 2' &
sleep 0.5
ps -o stat,cmd --ppid $! | awk 'NR==1 || $1 ~ /^Z/'
''', notes={1: 'Parent :: becomes sleep 2.', 3: 'Zombie :: Z defunct.'}, tryit='Wait 2 seconds and run the ps again.'),
]

QUIZ = mix([
    dict(q='What is the difference between a program and a process?', options=['none', 'a process is a running instance of a program', 'a program is in memory, a process on disk', 'a process is always a service'], answer=1, why='File vs running instance.'),
    dict(q='Which system call loads a new program into the current process?', options=['fork', 'exec (execve)', 'wait', 'kill'], answer=1, why='Same PID, new program.'),
    dict(q='What does $! hold?', options=['last exit status', 'PID of the last background job', 'shell PID', 'parent PID'], answer=1, why='After cmd &.'),
    dict(q='STAT Z means…', options=['sleeping', 'stopped', 'zombie: exited, not reaped', 'running'], answer=2, why='<defunct>.'),
    dict(q='How do you get rid of a zombie?', options=['kill -9 it', 'fix or end its parent', 'reboot only', 'rm /proc/PID'], answer=1, why='Only the parent can wait.'),
    dict(q='An orphan is adopted by…', options=['the shell', 'PID 1 (or a subreaper)', 'root’s shell', 'nobody'], answer=1, why='init/systemd.'),
    dict(q='Why does ./go.sh with cd /tmp not change your folder?', options=['cd is broken in scripts', 'the script runs in a child process', 'needs sudo', 'needs chmod'], answer=1, why='source it.'),
    dict(q='Which state means waiting for disk, ignoring signals?', options=['S', 'D', 'T', 'R'], answer=1, why='Uninterruptible.'),
])

REVISION = [
    'Program = file; process = running instance with PID, PPID, UID, state and resources.',
    'Every command: <b>fork</b> (copy) → <b>exec</b> (new program, same PID) → <b>exit</b> (status) → parent <b>wait</b> → <code>$?</code>.',
    'States: R running, S sleeping, D disk wait, T stopped, Z zombie, I idle kernel thread; s leader, + foreground.',
    'Zombie = exited, not reaped: fix the parent. Orphan = parent gone: adopted by PID 1.',
    '<code>$$</code> shell, <code>$PPID</code> parent, <code>$!</code> last &amp;, <code>$BASHPID</code> real subshell PID.',
    'Scripts run in a child: use <code>source</code> for cd/export; <code>exec</code> replaces the shell.',
]

FAQ = [
    ('What is a process in Linux?', 'A running instance of a program with its own PID, parent (PPID), owner, memory, open files and state.'),
    ('What is the difference between fork and exec?', 'fork creates a copy of the current process with a new PID; exec replaces the program running in a process, keeping its PID.'),
    ('What is a zombie process?', 'A process that has exited but whose parent has not yet collected its exit status with wait. It shows as Z / <defunct>.'),
    ('How do I kill a zombie process?', 'You cannot; fix or restart its parent, or end the parent so PID 1 adopts and reaps it.'),
    ('What is an orphan process?', 'A running process whose parent has exited; it is adopted by PID 1 (systemd) or a subreaper.'),
    ('How do I find my shell’s PID?', 'echo $$ (and $PPID for its parent).'),
    ('What does STAT S mean in ps?', 'Interruptible sleep: the process is waiting for an event such as input or a timer.'),
]

PRACTICE_INTRO = 'Small process tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Exit status', stmt='Run a child that exits 4 and print its status.', inp='nothing', code="bash -c 'exit 4'; echo $?\n", explain='wait → $?.'),
    dict(level='easy', title='Child’s parent', stmt='Print “ok” if a child’s $PPID equals your $$.', inp='nothing', code="[ \"$(bash -c 'echo $PPID')\" = \"$$\" ] && echo ok\n", explain='The shell is the parent.'),
    dict(level='easy', title='Builtin or program?', stmt='Show that cd is a builtin and ls a program.', inp='nothing', code="type cd; type -P ls\n", explain='type.'),
    dict(level='medium', title='Stopped state', stmt='Stop a background sleep and print its state letter.', inp='nothing', code="sleep 20 & p=$!; sleep 0.1; kill -STOP $p; ps -o stat= -p $p; kill -9 $p\n", explain='T.'),
    dict(level='medium', title='Same PID after exec', stmt='Show exec keeps the PID.', inp='nothing', code="bash -c 'a=$$; exec bash -c \"[ \\$\\$ = $a ] && echo same PID\"'\n", explain='exec.'),
    dict(level='medium', title='Source vs run', stmt='Show a sourced script keeps a variable.', inp='a script', code="echo 'X=1' > s.sh; bash s.sh; echo \"[$X]\"; . s.sh; echo \"[$X]\"\n", explain='[] then [1].'),
    dict(level='business', title='Wait for jobs', stmt='Start two background jobs and wait for both; print “all done”.', inp='nothing', code="sleep 0.2 & sleep 0.3 & wait; echo all done\n", explain='wait.'),
    dict(level='business', title='Zombie count', stmt='Make one zombie and count zombies among your shell’s grandchildren.', inp='nothing', code="bash -c 'sleep 0.1 & exec sleep 2' & sleep 0.5; ps -o stat= --ppid $! | grep -c '^Z'\n", explain='1.'),
]

SCN_INTRO = 'Interview questions about processes, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is the difference between a process and a program?”', 'A classic opener.', 'clear definitions?',
        '''<ul>
          <li>Program: a file (passive). Process: a running instance (active) with PID, memory, state.</li>
          <li>One program, many processes (e.g. many bash shells).</li>
          <li>Created by fork + exec.</li>
        </ul>''', 'saying “they are the same”.') +
    scn('Product company', 'Junior', '“Explain fork and exec”', 'Often followed by “what does the shell do when you type ls?”.', 'can you walk through it?',
        '''<ol>
          <li>Shell forks: child is a copy with a new PID.</li>
          <li>Child execs /usr/bin/ls: same PID, new program.</li>
          <li>Shell waits; ls exits; status goes into $?.</li>
        </ol>''', 'mixing up which one creates a PID.') +
    scn('Operations', 'Mid-level', 'Hundreds of &lt;defunct&gt; processes', 'Monitoring alerts on process count.', 'zombies and parents?',
        '''<ul>
          <li><code>ps -eo pid,ppid,stat,cmd | awk '$3~/Z/'</code>; group by PPID.</li>
          <li>The parent has a bug (no wait / no SIGCHLD handler); restart it.</li>
          <li>Report the bug; zombies only cost PIDs, but can exhaust pid_max.</li>
        </ul>''', 'running kill -9 on the zombies.') +
    scn('Platform team', 'Senior', 'Container ignores docker stop and leaves zombies', 'The entrypoint is a bash script that starts the app.', 'PID 1 behaviour?',
        '''<ul>
          <li>bash is PID 1: it does not forward SIGTERM and may not reap.</li>
          <li>End the script with <code>exec app</code>, or use <code>--init</code>/tini as PID 1.</li>
          <li>docker stop then delivers SIGTERM to the app (Lesson 11.3).</li>
        </ul>''', 'raising the stop timeout.')
) + interview([
    ('What is a PID?', 'A number identifying a running process.'),
    ('What is PPID?', 'The PID of the parent process.'),
    ('What happens to an orphan?', 'PID 1 adopts it.'),
    ('Can you kill a zombie?', 'No; it is already dead. Fix the parent.'),
    ('What is a daemon?', 'A background service without a terminal, usually child of PID 1.'),
    ('Process vs thread?', 'Threads share the process’s memory; processes have their own.'),
    ('What is $$ in bash?', 'The shell’s own PID.'),
], [
    ('RHCSA (EX200)', '“Identify CPU/memory intensive processes and kill processes”.'),
    ('LFCS', 'Manage processes and services.'),
    ('CompTIA Linux+', 'Process concepts, states, ps and signals.'),
]) + distro('The process model is the same on every Unix-like system.', [
    ('fork/exec model', 'yes', 'yes', 'yes', 'CreateProcess (no fork)'),
    ('PID 1', 'systemd', 'systemd', 'launchd', 'System (PID 4)'),
    ('/proc/PID', 'yes', 'yes', 'no (use ps, lsof)', 'WSL only'),
    ('$$ $! $PPID', 'bash', 'bash', 'zsh/bash', 'Git Bash'),
    ('Zombie letter', 'Z', 'Z', 'Z', '-'),
]) + teaser('11.2', 'Riya now knows what a process is, but her server has 312 of them. Which one is eating the CPU? Who started that strange python3? Next: ps, pstree, top and htop, and how to read every column.')

CHEATSHEET = cheatsheet('Processes', [
    ('IDs', [('$$', 'my shell'), ('$PPID', 'its parent'), ('$!', 'last &'), ('$BASHPID', 'real subshell PID')]),
    ('Look', [('ps -o pid,ppid,stat,cmd -p N', 'one'), ('ps --ppid N', 'children'), ('ps -o ppid= -p N', 'parent'), ('/proc/N/status', 'kernel view')]),
    ('States', [('R S', 'run, sleep'), ('D', 'disk wait'), ('T', 'stopped'), ('Z', 'zombie'), ('s +', 'leader, foreground')]),
    ('Run', [('source f', 'current shell'), ('bash f', 'child'), ('exec cmd', 'replace shell'), ('wait', 'reap jobs')]),
])

MINDMAP = mindmap('Process', [
    ('Identity', 'blue', ['PID', 'PPID', 'UID']),
    ('Birth', 'green', ['fork', 'exec', 'same PID']),
    ('Death', 'red', ['exit status', 'wait', '$?']),
    ('States', 'amber', ['R S D', 'T Z', 'I']),
    ('Odd ones', 'violet', ['zombie', 'orphan', 'daemon']),
    ('Shell', 'acc', ['$$ $!', 'source', 'exec']),
])

LAB = lab('process detective', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab111 && cd ~/lab111 && rm -f *.txt setenv.sh
printf 'export LAB_MODE=ready\\n' > setenv.sh''',
    tasks=['Write your shell’s PID into <code>shell.txt</code> (only the number).',
           'Run <code>bash -c \'exit 7\'</code> and write its exit status into <code>status.txt</code>.',
           'Start <code>sleep 300</code> in the background and write its PID into <code>job.txt</code> (leave it running).',
           'Load <code>setenv.sh</code> so that <code>LAB_MODE</code> is set in your shell, then write <code>$LAB_MODE</code> into <code>mode.txt</code>.'],
    solution='''echo $$ > shell.txt
bash -c 'exit 7'; echo $? > status.txt
sleep 300 & echo $! > job.txt
source setenv.sh; echo "$LAB_MODE" > mode.txt''',
    check='''cd ~/lab111
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 shell"   '[ -s shell.txt ] && ps -p "$(cat shell.txt)" -o comm= 2>/dev/null | grep -q bash'
ok "2 status"  '[ "$(cat status.txt 2>/dev/null)" = 7 ]'
ok "3 job"     '[ -s job.txt ] && [ "$(ps -o comm= -p "$(cat job.txt)" 2>/dev/null)" = sleep ]'
ok "4 source"  '[ "$(cat mode.txt 2>/dev/null)" = ready ]'
kill "$(cat job.txt 2>/dev/null)" 2>/dev/null; true''')
