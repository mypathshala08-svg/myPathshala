import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

PR = r"""rm -rf ~/pr; mkdir -p ~/pr; cd ~/pr
printf '#!/bin/bash\necho "report: my PID is $$, my parent is $PPID"\nsleep 1\n' > report.sh; chmod +x report.sh"""

HOOK = hook('Riya double-clicks nothing, types one word, <code>ls</code>, and a program starts, runs and disappears in 3 milliseconds. Behind that word, Linux made a copy of her shell, turned the copy into <code>ls</code>, waited for it, and collected its exit status. Every running program, from your shell to a web server with 200 workers, is a <b>process</b>: a program in memory with a number (PID), a parent (PPID), an owner, a state and its own resources. Understanding this one idea explains “zombie processes”, why <code>cd</code> cannot be a separate program, why a server keeps running after you close the terminal (or does not), and what you are really killing with <code>kill</code>.',
    ['explain program vs process vs thread, and read PID, PPID, UID, state and command for any process',
     'describe how every command starts: <b>fork</b> (copy the parent) then <b>exec</b> (load a new program), then <b>wait</b> and the exit status',
     'recognise process states R, S, D, T, Z and I, and what zombies and orphans really are',
     'find information about your own shell: <code>$$</code>, <code>$PPID</code>, <code>$!</code>, <code>/proc/PID</code>, and see fork/exec happen with strace'])
ROAD = roadmap([
    ('story', 'The story', 3, 'what happens when you type ls'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'What a process is', 6, 'simple meaning + 4 depths'),
    ('types', 'States and kinds', 5, 'R S D T Z, zombie, orphan'),
    ('commands', 'Process basics by field', 14, 'real runs'),
    ('animation', 'See it happen', 5, 'fork → exec → wait'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'process detective'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('My shell’s own PID', 'echo $$', 'and $PPID for its parent'),
    ('PID of the last background job', 'echo $!', 'right after cmd &'),
    ('Details of one process', 'ps -o pid,ppid,user,stat,cmd -p PID', 'choose the columns'),
    ('All processes', 'ps -ef  or  ps aux', 'Lesson 11.2'),
    ('Parent/child tree', 'pstree -p', 'Lesson 11.2'),
    ('Everything the kernel knows', 'cat /proc/PID/status', 'Lesson 11.5'),
    ('Find a PID by name', 'pgrep -a NAME', 'not ps | grep'),
    ('Is it a zombie?', "ps -o pid,ppid,stat,cmd | grep ' Z'", 'fix the parent'),
])

cmap = concept_map(
    [('5.4', 'Exit status', '$? and 0/1'), ('8.1', 'Users', 'UID owns processes'), ('9.4', 'SUID', 'effective UID')],
    ['program vs process vs thread', 'PID, PPID, UID, state', 'fork → exec → wait → exit', 'states R S D T Z I; zombies and orphans', '$$ $PPID $! and /proc/PID'],
    [('11.2', 'ps, pstree, top', 'watch them'), ('11.3', 'Signals and kill', 'stop them'), ('11.4', 'Jobs', '& fg bg nohup'), ('16.3', 'systemd', 'PID 1 and services')],
    'A process is a running program with a number, a parent and a state. Every command you type is born by fork and exec.')

sc = (term(20, 14, 316, 156, ['$ echo $$', ('2140', 'out'), '$ bash -c \'echo "me $$, parent $PPID"\'', ('me 2187, parent 2140', 'acc'), '$ ps -o pid,ppid,stat,cmd', ('  PID  PPID STAT CMD', 'out'), (' 2140  2139 Ss   -bash', 'out'), (' 2190  2140 R+   ps -o …', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=15)
      + t(352, 36, 'Every command:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• gets a new PID', '• its parent = your shell', '• fork: copy the shell', '• exec: become the program', '• exit: status to parent'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>What really happens when you type ls</h2>
  <div class="story">
''' + puzzle('Riya writes a script <code>go.sh</code> containing one line, <code>cd /var/log</code>. She runs <code>./go.sh</code> and then <code>pwd</code>. She is still in her home folder. The script ran without error. Why did the <code>cd</code> not “stick”, and what is the correct way to run it so it does?') + '''
    <p class="narration">Riya asks her shell who it is, and who started it.</p>
''' + scene('A terminal: echo $$ prints the shell PID; a child bash prints its own PID and the shell as its parent; ps shows PID, PPID, state and command.', sc,
            'Each command is a <tspan font-weight="700" class="s-acc">child</tspan> of the shell, with its own PID.') + '''
K> So my shell is a process too?
A> Yes, PID 2140 here. When you type a command, the shell <b>forks</b>: the kernel makes an almost exact copy of it (a new PID, same memory, same open files). The copy then calls <b>exec</b> to replace itself with the program, for example <code>ls</code>. The shell <b>waits</b>; when the child exits, the shell reads its exit status into <code>$?</code>.
R> And when something goes wrong?
A> Then you see the leftovers: a <b>zombie</b> (a child that finished but whose parent never collected the status), an <b>orphan</b> (whose parent died first), or a process stuck in state <b>D</b>. Today you will see each one for real.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A kitchen: the recipe book is the program, a cook following it is a process, two cooks can follow the same recipe. A head chef (parent) hires a helper (fork), the helper switches to a new recipe (exec), and reports back when done (exit status).">'
       + label_box(14, 20, 190, 110, ['program = recipe', 'a file on disk', '/usr/bin/ls', '(does nothing alone)'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['process = a cook', 'following it now', 'PID 2190, parent 2140', 'state: running'], 'amber', 8.6)
       + label_box(434, 20, 192, 110, ['fork: hire a copy', 'exec: new recipe', 'exit: report back', 'wait: chef listens'], 'green', 8.6)
       + t(320, 160, 'One program can run as many processes at once.', 9.6, 'ink2')
       + t(320, 182, 'Every process has exactly one parent.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Processes at four depths', [
    ('v', 'No jargon: recipes and cooks', '      <p>A program is a recipe; a process is someone cooking it right now.</p>' + pic),
    ('b', 'What you will see every day', '''      <ul>
        <li><b>PID</b>: the process ID, a number unique while it runs. <code>echo $$</code> shows your shell’s.</li>
        <li><b>PPID</b>: the parent’s PID. Your commands’ parent is your shell.</li>
        <li><b>USER</b>: whose permissions it has (Lesson 8.1).</li>
        <li><b>STAT</b>: R running, S sleeping (waiting), T stopped, Z zombie, D waiting for disk.</li>
        <li>When it ends, it leaves an <b>exit status</b> for its parent: <code>$?</code> (Lesson 5.4).</li>
      </ul>'''),
    ('i', 'fork, exec, wait, exit', '''      <ul>
        <li><b>fork()</b> (on Linux: <code>clone()</code>) creates a child that is a copy of the parent: same code, memory (copy-on-write), open files, current folder, environment.</li>
        <li><b>exec()</b> (<code>execve()</code>) replaces the program inside the process: same PID, new code. <code>exec cmd</code> in bash does this to the shell itself.</li>
        <li><b>exit()</b> ends the process with a status 0–255; the kernel keeps a small entry (a <b>zombie</b>) until the parent calls <b>wait()</b>.</li>
        <li>That is why <code>cd</code> must be a shell <b>builtin</b>: a child’s current folder dies with the child. Same for <code>export</code>, <code>source</code>, <code>exit</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: the kernel’s view', '''      <ul>
        <li>The kernel keeps a <code>task_struct</code> per task: PID, parent, credentials (real/effective UID), state, memory map, open file table, signal handlers, CPU time, cgroup and namespaces.</li>
        <li>Threads are tasks that share memory: each has its own TID; the PID of a process is its main thread’s ID (TGID). <code>ps -L</code> shows them.</li>
        <li>PID 1 (systemd on most distributions) is the ancestor of all user processes and adopts <b>orphans</b>; it reaps them so they do not stay zombies. Process trees can also set a “subreaper”.</li>
        <li>Kernel threads (<code>[kthreadd]</code>, <code>[kworker/…]</code>) have PPID 2 and no command line; state <b>I</b> means idle kernel thread.</li>
        <li>PIDs are reused after a process ends; the maximum is <code>/proc/sys/kernel/pid_max</code> (often 4194304). A PID alone does not prove it is the same process later.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Process: a running program</h2>
''' + def_block(
    'A <b>process</b> is an instance of a program being executed, with its own process ID (PID), parent process ID (PPID), owner (UID/GID), memory, open files, current directory, environment and state. New processes are created by <b>fork</b> (a copy of an existing process) and usually load a different program with <b>exec</b>; when a process exits, its parent collects the exit status with <b>wait</b>.',
    'A program is a file. A process is that file running, with a number and a parent.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('PID', 'Process ID: its number.'),
    ('PPID', 'Parent’s PID.'),
    ('fork', 'Make a child copy of a process.'),
    ('exec', 'Replace the program inside a process.'),
    ('wait / reap', 'Parent collects the child’s exit status.'),
    ('Zombie (Z)', 'Finished, status not yet collected.'),
    ('Orphan', 'Parent died; adopted by PID 1.'),
    ('Thread', 'A second flow inside one process, shared memory.'),
]) + '\n' + names('Where the names come from.', [
    ('PID', 'process identifier', 'Unix, 1971.'),
    ('fork', 'a fork in the road', 'One path becomes two.'),
    ('exec', 'execute', 'execve(): exec + vector + environment.'),
    ('zombie', 'the living dead', 'Dead but still in the table.'),
    ('$$', 'this shell’s PID', 'Bash special parameter.'),
    ('$!', 'last background PID', 'After cmd &.'),
    ('init', 'initial process', 'PID 1; today systemd.'),
    ('daemon', 'helpful spirit', 'Background service (sshd).'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('My PID', '<code>echo $$</code>'),
    ('My parent', '<code>echo $PPID</code>'),
    ('Last background', '<code>echo $!</code>'),
    ('One process', '<code>ps -o pid,ppid,stat,cmd -p N</code>'),
    ('PID 1', 'systemd (on your PC)'),
    ('Zombie letter', '<code>Z</code> / &lt;defunct&gt;'),
]) + '\n' + lv + didyou('You cannot kill a zombie: it is already dead. <code>kill -9</code> does nothing to it. You fix zombies by making the <b>parent</b> call wait (or by ending the parent, so PID 1 adopts and reaps them).') + '''
EXAM> “Difference between a program and a process?” → A program is a passive file on disk; a process is an active instance of it in memory with a PID, state and resources. One program can run as many processes.
''' + qc('Why is <code>cd</code> built into the shell instead of being a program like /usr/bin/ls?', 'A program runs in a child process. A child’s current folder disappears when it exits, so the shell’s folder would never change.') + mistake('kill -9 the zombie’s PID',
    'Find its parent (ps -o ppid= -p ZPID) and fix or restart the parent',
    'A zombie has already exited. Only its parent can remove it (by calling wait); if the parent ends, PID 1 adopts and reaps it.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Process states, and kinds of processes</h2>
''' + table(['STAT', 'Name', 'Meaning', 'Example'], [
    ['R', 'Running / runnable', 'on a CPU or waiting for one', 'a compression job'],
    ['S', 'Sleeping (interruptible)', 'waiting for something: input, timer, network', 'bash at the prompt, sleep'],
    ['D', 'Uninterruptible sleep', 'waiting for disk/NFS; signals wait', 'a stuck NFS read'],
    ['T', 'Stopped', 'paused by Ctrl+Z or SIGSTOP', 'a suspended vim'],
    ['t', 'Traced', 'stopped by a debugger', 'gdb, strace'],
    ['Z', 'Zombie', 'exited; parent has not called wait', '&lt;defunct&gt;'],
    ['I', 'Idle', 'idle kernel thread', '[kworker/…]'],
], minw=560) + table(['Extra letter in ps STAT', 'Meaning'], [
    ['<code>s</code>', 'session leader (e.g. your login shell)'],
    ['<code>+</code>', 'in the foreground process group of a terminal'],
    ['<code>l</code>', 'multi-threaded'],
    ['<code>&lt;</code> / <code>N</code>', 'high / low priority (Lesson 11.5)'],
], minw=360) + table(['', 'Zombie', 'Orphan', 'Daemon'], [
    ['What', 'dead, not yet reaped', 'alive, parent gone', 'background service, no terminal'],
    ['Parent', 'still alive (did not wait)', 'PID 1 (or a subreaper)', 'usually PID 1'],
    ['Uses', 'only a process-table slot', 'normal resources', 'normal resources'],
    ['Harmful?', 'a few: no; thousands: PID exhaustion', 'no (often on purpose)', 'no'],
    ['Fix', 'fix/restart the parent', '—', '—'],
], minw=480) + table(['', 'Process', 'Thread'], [
    ['Memory', 'its own', 'shared with other threads'],
    ['ID', 'PID', 'TID (same PID)'],
    ['Created by', 'fork()/clone()', 'clone() with sharing flags'],
    ['Crash', 'only itself', 'takes the whole process down'],
    ['See', '<code>ps -e</code>', '<code>ps -eLf</code>, <code>top -H</code>'],
], minw=420) + qc('A process shows STAT <code>Ss</code>. What is it likely to be?', 'A sleeping session leader, typically a login shell waiting for you to type.') + mistake('“User processes are given limited and direct access to hardware”',
    'User processes have NO direct access to hardware; they ask the kernel through system calls (open, read, clone, execve…)',
    'That is the whole point of user space vs kernel space: a bug in your program cannot write to the disk controller or another process’s memory. You can watch the requests with strace (Under the hood, below).') + '''
</section>
'''

ZOMB = PR + r"""; cd ~/pr; bash -c 'sleep 0.2 & exec sleep 3' & echo $! > parent.pid; sleep 0.8"""
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Process basics explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine, in a folder <code>~/pr</code> with a small script <code>report.sh</code> that prints its own PID and its parent’s. PID numbers on your PC will differ. On our build container PID 1 is a small helper program instead of systemd; on your PC it is systemd.</p>
''' + cmdcard_u(['knowing your shell’s identity', 'scripts that write PID files', 'killing the job you just started'],
               ['using $$ inside $( ) or a pipe and expecting the subshell’s PID (use $BASHPID)'])(
    'vars', '$$ · $PPID · $! · $BASHPID', 'PIDs from the shell',
    'Bash keeps four PID variables: <code>$$</code> the shell’s PID, <code>$PPID</code> its parent’s, <code>$!</code> the last background job, and <code>$BASHPID</code> the current (sub)shell’s real PID.',
    'echo $$ $PPID $!', 'safe',
    [('$$', 'this shell', 'PID files'),
     ('$PPID', 'its parent', 'who started me'),
     ('$!', 'last cmd &', 'wait, kill'),
     ('$BASHPID', 'real PID in subshells', 'debugging'),
     ('$?', 'last exit status', 'Lesson 5.4')],
    dict(setup=PR, cmd="cd ~/pr\necho \"shell $$ parent $PPID\"\n./report.sh\nsleep 30 & echo \"background job $!\"; kill $!", note='report.sh is a child: its parent is our shell’s PID.'),
    [('dev', [
        dict(situation='$$ lies inside a subshell; $BASHPID does not.', cmd="echo \"main $$ $BASHPID\"; ( echo \"subshell $$ $BASHPID\" ); echo x | { read; echo \"pipe $$ $BASHPID\"; }",
             why='Subshells and pipe parts are forked children: $$ still shows the main shell, $BASHPID the real one.')]),
     ('devops', [
        dict(situation='A PID file for a service started by a script.', setup=PR, cmd="cd ~/pr; sleep 60 & echo $! > app.pid\nps -o pid,stat,cmd -p \"$(cat app.pid)\"\nkill \"$(cat app.pid)\"; rm app.pid",
             why='Many older services write a PID file in /run so scripts can stop them; systemd tracks this itself.')]),
    ],
    anat=anatomy([('echo', 'cmd', 'print'), ('$$', 'arg', 'shell PID'), ('$PPID', 'arg', 'parent'), ('$!', 'arg', 'last &')], 'Only $BASHPID changes inside ( ) subshells.')
) + cmdcard_u(['seeing one process’s details', 'scripts that need one field', 'checking states'],
               ['parsing default ps output (columns change)'])(
    'pso', 'ps -o … -p', 'look at chosen processes',
    '<code>ps -o</code> chooses the columns and <code>-p</code> the PIDs (<code>--ppid</code> the children of a PID, <code>-C</code> a command name). A <code>=</code> after a column hides the header, handy in scripts.',
    'ps -o COLUMNS [-p PID | --ppid PID | -C NAME]', 'safe',
    [('pid,ppid', 'IDs', 'family'),
     ('user,uid', 'owner', 'security'),
     ('stat', 'state letters', 'R S D T Z'),
     ('etime', 'running for', 'how long'),
     ('cmd / comm', 'full / short command', 'what'),
     ('ppid=', 'value only', 'scripts')],
    dict(setup=PR, cmd="cd ~/pr; sleep 40 & s=$!; sleep 0.1\nps -o pid,ppid,user,stat,etime,cmd -p $$,$s\nkill $s", note='Our shell (S = sleeping while ps runs) and its background child sleep (S: waiting for a timer).'),
    [('sys', [
        dict(situation='Just the parent PID of a process, for a script.', setup=PR, cmd="sleep 40 & s=$!; sleep 0.1; ps -o ppid= -p $s | tr -d ' '; echo \"shell $$\"; kill $s",
             why='The = removes the header. Compare: the parent is our shell.')]),
     ('qa', [
        dict(situation='A stopped (T) process.', cmd="sleep 40 & s=$!; sleep 0.1; kill -STOP $s; ps -o pid,stat,cmd -p $s; kill -CONT $s; ps -o pid,stat,cmd -p $s; kill $s",
             why='SIGSTOP pauses (T), SIGCONT resumes (S). Ctrl+Z does the same to a foreground job (Lesson 11.4).')]),
    ]
) + cmdcard_u(['understanding how every command starts', 'debugging “command not found” vs “permission denied”', 'scripts with exec'],
               ['exec in your login shell by accident (it replaces the shell)'])(
    'forkexec', 'fork · exec · wait (strace)', 'how a command starts',
    'Watch the system calls: the shell calls <code>clone()</code> (fork), the child calls <code>execve()</code> with the program path, the shell calls <code>wait4()</code> and gets the exit status. <code>exec CMD</code> skips the fork: the shell itself becomes CMD.',
    'strace -f -e trace=clone,execve,wait4 bash -c "CMD"', 'safe',
    [('clone()', 'fork a child', 'new PID'),
     ('execve()', 'load a program', 'same PID'),
     ('wait4()', 'collect status', 'reap'),
     ('exit_group()', 'end with status', '$?'),
     ('exec CMD', 'replace the shell', 'wrappers')],
    dict(cmd="strace -f -e trace=clone,execve,wait4,exit_group bash -c 'ls / > /dev/null; echo done' 2>&1 | grep -v -E '^---|resumed|ECHILD|exited with' | sed -E 's/, 0x[0-9a-f]+ \\/\\* [0-9]+ vars \\*\\//, …/; s/child_stack=NULL, flags=//; s/, child_tidptr=0x[0-9a-f]+//'", note='bash (exec’d by strace), clone → child PID, the child execve’s /usr/bin/ls, bash waits, the child exits 0. The builtin echo needed no new process.'),
    [('dev', [
        dict(situation='exec: the same PID becomes another program.', cmd="bash -c 'echo \"bash is $$\"; exec sh -c \"echo now sh, still \\$\\$\"'",
             why='No fork: same PID, new program. Wrapper scripts end with exec so signals reach the real program (Docker entrypoints).')]),
     ('sys', [
        dict(situation='The puzzle: cd in a child does not change the parent.', setup=PR + "; printf 'cd /var/log\\npwd\\n' > ~/pr/go.sh", cmd="cd ~/pr; bash go.sh; pwd\nsource go.sh; pwd",
             why='bash go.sh runs in a child; source (or .) runs the lines in the current shell.')]),
    ]
) + mistake('./go.sh   (a script that does cd or export, expecting your shell to change)', 'source go.sh   or   . go.sh',
            'A script runs in a child process. Its cd, export and variables vanish when it exits. source runs it inside your current shell.') + cmdcard_u(['understanding zombies and orphans', 'debugging services that leave &lt;defunct&gt; entries'],
               ['kill -9 on a zombie (it is already dead)'])(
    'zombie', 'zombies and orphans', 'Z and PPID 1',
    'A <b>zombie</b> is a child that exited while its parent did not call wait: ps shows <code>Z</code> and <code>&lt;defunct&gt;</code>. An <b>orphan</b> is a running child whose parent exited: it is adopted by PID 1 (or a subreaper), so its PPID changes.',
    "ps -o pid,ppid,stat,cmd --ppid PARENT   ·   ps -eo pid,ppid,stat,cmd | awk '$3 ~ /Z/'", 'safe',
    [('STAT Z', 'zombie', 'needs a reap'),
     ('&lt;defunct&gt;', 'zombie in cmd', 'same'),
     ('PPID 1', 'adopted orphan', 'normal for daemons'),
     ('ps -o ppid= -p Z', 'zombie’s parent', 'what to fix')],
    dict(setup=ZOMB, cmd="cd ~/pr; p=$(cat parent.pid)\nps -o pid,ppid,stat,cmd --ppid $p\nps -o pid,stat,cmd -p $p", note='The parent ran sleep 0.2 in the background, then exec’d sleep 3, which never calls wait: the finished child stays Z. When the parent ends, PID 1 reaps it.'),
    [('sys', [
        dict(situation='An orphan is adopted.', setup=PR, cmd="cd ~/pr; bash -c 'sleep 30 & echo $! > child.pid'; sleep 0.2\nps -o pid,ppid,stat,cmd -p $(cat child.pid); kill $(cat child.pid)",
             why='The parent bash ended right away; its child sleep now has PPID 1. That is how daemons detach on purpose.')]),
     ('devops', [
        dict(situation='Zombies cannot be killed.', setup=ZOMB, cmd="cd ~/pr; z=$(ps -o pid= --ppid $(cat parent.pid) | tr -d ' ')\nkill -9 $z; sleep 0.2; ps -o pid,stat,cmd -p $z",
             why='Still Z after kill -9. In containers, run a tiny init (docker run --init, tini) as PID 1 so zombies get reaped.')]),
    ]
) + undo('Process mistakes are fixed by ending or restarting the right process.', [
    ('Ran exec in your login shell:', 'the terminal closes when that program ends; just open a new terminal.'),
    ('A script’s cd/export “did nothing”:', 'run it with <code>source script.sh</code>.'),
    ('Zombies piling up:', 'find the parent (<code>ps -o ppid= -p Z</code>), restart it; in containers add an init (<code>--init</code>).'),
    ('Started something in the background and lost it:', '<code>jobs -l</code> or <code>pgrep -a NAME</code>, then kill it (Lesson 11.3).'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='ps -p 999999', meaning='No process with that PID (ps prints only the header).', fix='Check the PID; it may have ended.'),
    dict(cmd='./report.sh', setup=PR + '; chmod -x ~/pr/report.sh; cd ~/pr', meaning='exec failed: the file is not executable (exit 126).', fix='<code>chmod +x</code> or <code>bash report.sh</code>.'),
    dict(cmd='repot.sh', meaning='exec could not find it in PATH (exit 127).', fix='Check the name; use <code>./</code> for the current folder.'),
    dict(cmd='kill 1', meaning='You may not signal another user’s process (here PID 1, root).', fix='Only your own processes, or sudo if appropriate.'),
]) + qc('A parent process ends while its child is still running. What is the child’s PPID now?', '1 (systemd/init) or a subreaper: the orphan is adopted.') + '''
'''
_sh.run_sh('pkill -u riya sleep 2>/dev/null; true', 'any')
cards = cards + '</section>\n'

def fe(k):
    sh = label_box(14, 26, 96, 46, ['bash', 'PID 2140'], 'blue', 8)
    o = sh
    if k >= 1:
        o += label_box(150, 26, 96, 46, ['bash (copy)' if k == 1 else 'ls', 'PID 2190'], 'amber' if k == 1 else 'green', 8) + arrow(110, 49, 150, 49)
    if k >= 3:
        o = sh + label_box(150, 26, 96, 46, ['exited', 'status 0'], 'card', 8) + arrow(150, 60, 110, 60)
    labels = ['The shell waits for a command.', 'fork(): a copy, new PID 2190.', 'exec(): the copy becomes ls.', 'exit 0 → wait() → $? = 0.']
    return o + t(180, 110, labels[k], 8.6, 'violet', bold=True)
see_cmds = [['$ '], ['$ ls'], ['$ ls', ('notes.txt  report.sh', 'out')], ['$ ls', ('notes.txt  report.sh', 'out'), '$ echo $?', ('0', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/pr', prompt='riya@web01:~/pr$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['A prompt.', 'You press Enter.', 'Output appears.', 'Back at the prompt.'])]
behind = [fe(k) for k in range(4)]
two = anim_two('fork → exec → wait', 'Behind the screen: one command, four steps',
               'A terminal: the user types ls, sees output and checks $?.',
               'A bash box creates a copy (fork), the copy becomes ls (exec), ls exits with status 0 and bash collects it (wait).', see, behind,
               ['Prompt.', 'fork.', 'exec.', 'wait.'],
               ['shell idle', 'new PID', 'same PID, new program', '$? = 0'])

def zb(k):
    par = label_box(14, 26, 110, 46, ['parent', 'never waits' if k else 'running'], 'blue', 8)
    ch = label_box(180, 26, 110, 46, [['child', 'running'], ['child', 'exited'], ['child', 'Z <defunct>'], ['reaped', 'by PID 1']][k], ['green', 'amber', 'red', 'card'][k], 8)
    init = label_box(180, 96, 110, 34, ['PID 1 adopts'], 'violet', 8) if k == 3 else ''
    if k == 3:
        par = label_box(14, 26, 110, 46, ['parent', 'ended'], 'card', 8)
    return par + arrow(124, 49, 180, 49) + ch + init
frames = [zb(0) + t(180, 156, 'A parent starts a child.', 8.6, 'violet', bold=True),
          zb(1) + t(180, 156, 'The child exits with a status.', 8.6, 'violet', bold=True),
          zb(2) + t(180, 156, 'Nobody calls wait(): zombie.', 8.6, 'red', bold=True),
          zb(3) + t(180, 156, 'Parent ends: PID 1 adopts and reaps.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'How a zombie is born and buried',
              'A child that finishes while its parent does not listen.',
              'zombie', 'A parent and a child: the child exits, the parent never waits so the child becomes a zombie; when the parent ends, PID 1 adopts and reaps it.', frames,
              ['Start.', 'Exit.', 'Zombie.', 'Reaped.'], hid='scenario-zombie')

dx = dissect('Layer by layer: what makes a process',
    'Each layer has a real command and output from our build machine.', [
    dict(key='prog', name='Program file', sub='on disk', why='The recipe.', how='ELF binary or script.', impl='execve() loads it.', used='Every command.',
         cmd="ls -l /usr/bin/sleep | awk '{print $1, $5, $NF}'; head -c 4 /usr/bin/sleep | od -c | head -1"),
    dict(key='id', name='Identity', sub='PID, PPID, UID', why='Who and whose.', how='Kernel task.', impl='task_struct.', used='ps, kill.',
         cmd="sleep 30 & s=$!; sleep 0.1; grep -E '^(Name|Pid|PPid|Uid|State)' /proc/$s/status; kill $s"),
    dict(key='res', name='Resources', sub='memory, files, cwd', why='What it holds.', how='Per-process tables.', impl='/proc/PID/fd, cwd, maps.', used='lsof.',
         cmd="cd /tmp; sleep 30 & s=$!; sleep 0.1; ls -l /proc/$s/cwd | awk '{print $(NF-2), $(NF-1), $NF}'; ls /proc/$s/fd; kill $s"),
    dict(key='threads', name='Threads', sub='tasks inside', why='Parallel work.', how='Shared memory.', impl='/proc/PID/task.', used='ps -L.',
         cmd="sleep 30 & s=$!; sleep 0.1; grep Threads /proc/$s/status; ls /proc/$s/task; kill $s"),
    dict(key='parent', name='Parent', sub='the family tree', why='Exit status goes up.', how='fork().', impl='PPID; PID 1 adopts.', used='pstree.',
         cmd="bash -c 'echo \"child $$ parent $PPID\"'; echo \"shell $$\""),
], hint='From the file on disk to the family tree. Click a layer.')

hd = hood('Under the hood: one command, three system calls', 'The real process system calls of <code>bash -c "ls; true"</code> on our build machine: clone, execve, wait4.',
          "bash -c 'ls > /dev/null; true'", show='clone|execve|wait4', trace='clone,clone3,execve,wait4')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>fork → exec → wait, and a zombie</h2>
''' + two + s1 + dx + hd + qc('Which system call gives a process its new program but keeps its PID?', '<code>execve()</code> (exec).') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Processes at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['master +', 'workers'], 'blue', 8.6), '1. Web servers',
              'nginx, Apache and Gunicorn start a master process that forks workers; the master restarts any worker that dies.', ['Start', '*fork', 'serve']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['PID 1', 'in Docker'], 'red', 8.6), '2. Containers',
    'The first process in a container is PID 1: it must reap zombies and forward signals, or use --init / tini.', ['Run', '*PID 1', 'reap']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['exec', 'wrappers'], 'green', 8.6), '3. Start scripts',
    'Entrypoint scripts prepare the environment then exec the real program, so it gets the PID and the signals.', ['Prepare', '*exec', 'run']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['PPID', 'audit'], 'amber', 8.6), '4. Security',
    'Analysts check who started a process: a shell whose parent is a web server is a classic sign of an attack.', ['Alert', '*ps -o ppid', 'investigate']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['$?', 'pipelines'], 'violet', 8.6), '5. CI pipelines',
    'Each build step is a child process; its exit status decides whether the pipeline continues.', ['Step', '*wait', 'pass/fail']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Who am I?', scenario='Your shell’s PID and parent.', cmd="echo \"$$ $PPID\" | awk '{print ($1 > 0 && $2 > 0) ? \"two numbers\" : \"?\"}'", explain='$$ and $PPID.'),
    dict(level='b', title='Background PID', scenario='Remember what you started.', cmd="sleep 20 & echo \"started $!\" | sed 's/[0-9]\\+/N/'; kill $!", explain='$!.'),
    dict(level='i', title='Children of my shell', scenario='What did I start?', cmd="sleep 20 & sleep 21 & sleep 0.1; ps -o stat,cmd --ppid $$; kill %1 %2", explain='--ppid.'),
    dict(level='i', title='Count my processes', scenario='How many am I running?', cmd="ps -u riya --no-headers | wc -l | awk '{print ($1 > 0) ? \"some\" : \"none\"}'", explain='-u USER.'),
    dict(level='a', title='Find zombies', scenario='Health check.', setup=ZOMB, cmd="ps -eo pid,ppid,stat,cmd | awk 'NR==1 || $3 ~ /^Z/'", explain='awk on STAT.'),
], extra=build_up('the process detective', 'Riya follows one background process from birth to exit.', PR, [
    ('cd ~/pr; sleep 2 & echo $! > s.pid; ps -o pid,ppid,stat,cmd -p $(cat s.pid) | sed \'s/[0-9]\\+/N/g\'', '1. Start it; note PID and parent.'),
    ('cd ~/pr; grep -E "^(Name|State|Threads)" /proc/$(cat s.pid)/status', '2. The kernel’s view.'),
    ('cd ~/pr; wait $(cat s.pid) 2>/dev/null; sleep 2.2; ps -p $(cat s.pid) >/dev/null || echo "exited and reaped"', '3. It ends; nothing is left.'),
], cumulative=True)) + which('Choosing the right tool.', [
    ('My shell’s PID', '$$', 'Built in.', 'ps | grep bash.'),
    ('PID in a subshell', '$BASHPID', 'Real PID.', '$$ (main shell).'),
    ('One process', 'ps -o … -p PID', 'Chosen columns.', 'Parsing ps aux.'),
    ('Run in current shell', 'source script', 'cd/export stick.', './script.'),
    ('Replace a wrapper', 'exec program', 'Same PID, signals.', 'Leaving bash as parent.'),
    ('Zombies', 'fix the parent', 'Only it can reap.', 'kill -9 the zombie.'),
]) + keys('Handy forms.', [
    ('echo $$ $PPID', 'me and my parent', 'identity'),
    ('ps -o pid,ppid,stat,cmd -p N', 'one process', 'details'),
    ('ps -o ppid= -p N', 'parent only', 'scripts'),
    ('ps --ppid N', 'children', 'family'),
    ('cat /proc/N/status', 'kernel view', 'deep'),
    ('exec CMD', 'become CMD', 'wrappers'),
]) + scriptit('family.sh', 'Print the chain of parents from a PID up to PID 1 (the process’s ancestry), using only ps.',
'''p=${1:-$$}
while [ "$p" -gt 0 ]; do
  ps -o pid=,stat=,comm= -p "$p" | awk '{printf "%-7s %-5s %s\\n", $1, $2, $3}'
  [ "$p" -eq 1 ] && break
  p=$(ps -o ppid= -p "$p" | tr -d ' ')
done''',
'<p>Run for the script’s own shell. On your PC the last line is <code>1 Ss systemd</code>.</p>', expect='any') + puzzle_answer('<code>./go.sh</code> runs the script in a <b>child</b> process (fork + exec of bash). The child changed <b>its own</b> folder and then exited, so Riya’s shell never moved. Run it in the current shell instead: <code>source go.sh</code> (or <code>. go.sh</code>), or make it a shell function/alias.') + qc('A process shows PPID 1. Is something wrong?', 'Not necessarily: services and orphans have PID 1 (systemd) as parent. It only matters if you expected a different parent.') + '''
</section>
'''

_sh.run_sh('pkill -u riya sleep 2>/dev/null; rm -rf ~/pr', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../05-redirection-and-pipes/04-chaining-commands-exit-codes-and-xargs/">Lesson 5.4</a> (exit status) and <a href="../../08-users-and-groups/01-users-and-groups-uid-gid-etc-passwd-etc-shadow/">Lesson 8.1</a> (UIDs).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
