import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='11-processes', lesson='02-watching-processes-ps-pstree-top-and-htop', n='11.2',
    module_label='Module 11 · Processes, jobs and signals',
    title='Watching processes: ps, pstree, top and htop',
    desc='ps aux, ps -ef and ps -eo with custom columns and --sort; pgrep and pidof; pstree -p, -a, -s and ps --forest; top summary lines, load average, %CPU, RES vs VIRT, TIME+, keys P M c k u 1 q and batch mode; htop; why ps | grep matches itself; real outputs with CPU and memory hogs, real top screens and animations.',
    og_desc='Read ps, pstree, top and htop like a pro: find the CPU or memory hog, who started it, and what load average really means.',
    minutes=40, level='Beginner → Advanced',
    lead='ps takes a snapshot, pstree shows the family tree and top shows a live, sorted view. This lesson teaches the columns that matter, finds a real CPU hog and memory hog, and explains load average.',
    chips=['Find the hog in one line', 'Real top screens', 'Load average animated', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A snapshot of your own processes
sleep 60 &
sleep 61 &
ps -o pid,ppid,stat,etime,cmd --ppid $$
pgrep -a sleep
pgrep -c sleep
kill %1 %2
"""

RUN = dict(
    heading='Snapshot, find by name, count',
    intro='<p>Start two background jobs, list them with ps, find them with pgrep, then stop them.</p>',
    code=MAIN,
    anno=[('pgrep -a sleep', 'Finds by name; never matches itself.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is the PPID of both sleeps?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many lines does the grep print when no sleep runs? Then run.',
             code="ps aux | grep sleep | wc -l\npgrep -c sleep\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is to sort by CPU, highest first. Fix the sort key.',
             code="ps -eo pid,%cpu,comm --sort=%cpu | tail -3\n"),
        dict(label='4 · Your turn', hint='Show your shell’s processes as a tree with PIDs.',
             code="sleep 30 & sleep 31 &\npstree -p $$\nkill %1 %2\n"),
        dict(label='5 · Challenge', hint='Print only the PID of the newest sleep.',
             code="sleep 30 & sleep 31 &\npgrep -n sleep\nkill %1 %2\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own machine',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Your top 5 memory users', cmd='ps -eo pid,rss,comm --sort=-rss | head -6', output='    PID   RSS COMMAND\n   2210 612340 firefox\n   2491 301228 Isolated Web Co\n   1530 210044 gnome-shell\n   3001 180932 code\n   3020 150212 code', note='Typical desktop.'),
        dict(title='2 · Load and CPUs', cmd='uptime; nproc', output=' 10:12:01 up  2:31,  1 user,  load average: 0.42, 0.55, 0.61\n8', note='Typical.'),
        dict(title='3 · htop', cmd='sudo apt install htop && htop', output='(full-screen, coloured: per-CPU bars, memory bar, process list; F10 quits)', note='Typical; htop is not on our build machine.'),
        dict(title='4 · procps version', cmd='ps --version', output=pc('ps --version'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='From a name to a PID to a column',
    intro='<p>Step through finding a process and reading one field about it.</p>',
    code='''sleep 30 &
pid=$(pgrep -n sleep)
state=$(ps -o stat= -p "$pid")
parent=$(ps -o ppid= -p "$pid" | tr -d ' ')
[ "$parent" = "$$" ] && echo "sleep $pid is my child, state $state"
kill "$pid"
''',
    notes={2: 'pgrep :: newest sleep.', 3: 'ps -o :: state only.', 4: 'Parent :: our shell.', 6: 'Stop it.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a quick health check, a memory report and a family tree.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='Is the service running?',
         problem='<p>Print “up” or “down” for a process name, using its exit status.</p>',
         inp='a background job', approach=['pgrep -x.', 'if.'],
         code='''sleep 30 &
for name in sleep nginx; do
  if pgrep -x "$name" > /dev/null; then echo "$name up"; else echo "$name down"; fi
done
kill %1
''', notes={3: 'pgrep :: exit 0 or 1.'}, tryit='Add -u $USER.'),
    dict(level='i', tag='DevOps', title='Memory report in MB',
         problem='<p>List your processes with RSS converted to MB, biggest first.</p>',
         inp='your processes', approach=['ps -o rss.', 'awk divides by 1024.'],
         code='''python3 -c 'a=bytearray(30*1024*1024); import time; time.sleep(5)' &
sleep 0.5
ps -o rss=,comm= --sort=-rss --ppid $$ | awk '{printf "%5.1f MB %s\\n", $1/1024, $2}' | head -2
kill %1
''', notes={3: 'RSS :: KiB → MB.'}, tryit='Add %MEM.'),
    dict(level='a', tag='Security', title='Children of a script',
         problem='<p>Show a script and the processes it started, as a tree.</p>',
         inp='a script with workers', approach=['pstree -p PID.'],
         code='''printf 'sleep 30 &\\nsleep 31 &\\nwait\\n' > w.sh
bash w.sh & sleep 0.3
pstree -p $!
kill $(pgrep -P $!) ; wait
''', notes={3: 'Tree :: bash with two sleeps.', 4: 'pgrep -P :: children of a PID.'}, tryit='Try ps --forest -g $!.'),
]

QUIZ = mix([
    dict(q='Which shows the parent PID by default?', options=['ps aux', 'ps -ef', 'top', 'pgrep'], answer=1, why='PPID column.'),
    dict(q='Real memory in RAM is…', options=['VSZ/VIRT', 'RSS/RES', 'TIME+', '%CPU'], answer=1, why='VIRT is reserved space.'),
    dict(q='In top, which key sorts by memory?', options=['P', 'M', 'T', 'k'], answer=1, why='M = memory.'),
    dict(q='Why does ps aux | grep nginx always show a line?', options=['nginx always runs', 'grep matches itself', 'ps bug', 'it is a zombie'], answer=1, why='Use pgrep.'),
    dict(q='Load average 2.0 on 4 CPUs means…', options=['overloaded', 'about half used', 'two crashes', 'two users'], answer=1, why='Compare with nproc.'),
    dict(q='top in a script needs…', options=['-u', '-b -n 1', '-H', '-p'], answer=1, why='Batch mode.'),
    dict(q='Show ancestors of PID 4120?', options=['pstree -s -p 4120', 'ps -p 4120', 'pgrep 4120', 'top -p 4120'], answer=0, why='-s = parents.'),
    dict(q='TIME+ in top is…', options=['how long it ran', 'CPU time used', 'start time', 'time left'], answer=1, why='Not wall-clock.'),
])

REVISION = [
    '<code>ps aux</code> (user, %CPU, %MEM, RSS) and <code>ps -ef</code> (PPID); <code>ps -eo COLS --sort=-%cpu</code> for scripts.',
    '<code>pgrep -a/-x/-f/-u/-c</code> finds PIDs by name and never matches itself; <code>ps | grep</code> does.',
    '<code>pstree -p</code>, <code>-s PID</code> for ancestors; <code>ps -ef --forest</code>.',
    'top: load average, task states, us/sy/id/wa, memory; keys P M c 1 u k q; <code>top -b -n 1</code> in scripts.',
    'RSS = real RAM; VSZ = reserved; TIME = CPU time; %CPU 100 = one core.',
    'Load = running + waiting + D-state; compare with <code>nproc</code>.',
]

FAQ = [
    ('What is the difference between ps aux and ps -ef?', 'Both list all processes. aux (BSD style) shows %CPU, %MEM, VSZ, RSS and STAT; -ef (System V style) shows PPID and start time.'),
    ('How do I find the process using the most CPU?', 'ps -eo pid,%cpu,cmd --sort=-%cpu | head, or top (sorted by CPU by default).'),
    ('How do I find the process using the most memory?', 'ps -eo pid,rss,cmd --sort=-rss | head, or press M in top.'),
    ('What is load average?', 'The average number of tasks running, waiting for a CPU or in uninterruptible (disk) wait over 1, 5 and 15 minutes.'),
    ('What is the difference between VIRT and RES in top?', 'VIRT is all reserved virtual memory; RES is the part actually in RAM.'),
    ('How do I exit top?', 'Press q.'),
    ('Is htop better than top?', 'It is friendlier (scrolling, mouse, colours, tree with F5); top is always installed and scriptable with -b.'),
]

PRACTICE_INTRO = 'Small ps/pgrep tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Count jobs', stmt='Start three sleeps in the background and count them with pgrep.', inp='nothing', code="sleep 9 & sleep 9 & sleep 9 &\npgrep -c -P $$ sleep; kill %1 %2 %3\n", explain='-c.'),
    dict(level='easy', title='Header off', stmt='Print only the PID of your shell with ps, no header.', inp='nothing', code="[ \"$(ps -o pid= -p $$ | tr -d ' ')\" = \"$$\" ] && echo match\n", explain='pid=.'),
    dict(level='easy', title='State letter', stmt='Print the state of a background sleep.', inp='nothing', code="sleep 9 & sleep 0.1; ps -o stat= -p $!; kill $!\n", explain='S.'),
    dict(level='medium', title='Exact name', stmt='Start sleep and a copy called sleepy; count matches of “sleep” with and without -x (only your shell’s children).', inp='nothing', code="cp /usr/bin/sleep ./sleepy; ./sleepy 9 & sleep 9 & sleep 0.1\npgrep -c -P $$ sleep; pgrep -cx -P $$ sleep; kill %1 %2\n", explain='2 without -x (sleep and sleepy), 1 with -x.'),
    dict(level='medium', title='Children', stmt='List the children of your shell by name only.', inp='nothing', code="sleep 9 & sleep 0.1; pgrep -l -P $$; kill %1\n", explain='pgrep -P = children of a PID; -l adds the name.'),
    dict(level='medium', title='No self-match', stmt='Count lines of ps aux matching sleep using the [s] trick, with no sleep running.', inp='nothing', code="ps aux | grep '[s]leep 99' | wc -l\n", explain='0.'),
    dict(level='business', title='Batch top', stmt='Print the first summary line of top in batch mode, starting with “top -”.', inp='nothing', code="top -b -n 1 | head -1 | cut -c1-5\n", explain='-b -n 1.'),
    dict(level='business', title='Tree', stmt='Show a script with one worker as a tree with PIDs hidden.', inp='a script', code="printf 'sleep 9\\n' > one.sh; bash one.sh & sleep 0.2; pstree $!; kill $(pgrep -P $!)\n", explain='pstree PID. “Terminated” is printed by one.sh’s bash when its child sleep is killed.'),
]

SCN_INTRO = 'Interview questions about watching processes, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you see running processes?”', 'Asked in every Linux interview.', 'ps vs top?',
        '''<ul>
          <li><code>ps aux</code> / <code>ps -ef</code>: snapshot.</li>
          <li><code>top</code> / htop: live, sorted.</li>
          <li><code>pgrep -a NAME</code> to find one.</li>
        </ul>''', 'only knowing Task Manager.') +
    scn('Support team', 'Junior', 'Server is slow', 'Users complain; you have SSH.', 'a method?',
        '''<ol>
          <li><code>uptime</code> and <code>nproc</code>: load vs cores.</li>
          <li><code>top</code>: P then M; look at wa and D states.</li>
          <li>Note PID, user, command, parent before acting.</li>
        </ol>''', 'rebooting first.') +
    scn('Operations', 'Mid-level', 'Load 12 on 8 cores, CPU 90% idle', 'Graphs show high load.', 'D state?',
        '''<ul>
          <li>Linux load counts D-state tasks.</li>
          <li><code>ps -eo stat,pid,cmd | awk '$1~/^D/'</code>: processes waiting on disk/NFS.</li>
          <li>Check the storage (iostat, NFS server), not the CPU.</li>
        </ul>''', 'adding CPUs.') +
    scn('SRE team', 'Senior', 'Memory slowly grows each night', 'The OOM killer fires at 3 a.m.', 'evidence?',
        '''<ul>
          <li>Cron: <code>ps -eo pid,rss,comm --sort=-rss | head</code> every 5 minutes into a log.</li>
          <li>Compare RSS over time; PSS for shared memory.</li>
          <li>Restart policy as a stopgap; fix the leak.</li>
        </ul>''', 'reading VIRT as usage.')
) + interview([
    ('What does ps aux show?', 'All processes with user, %CPU, %MEM, VSZ, RSS, TTY, STAT, START, TIME, COMMAND.'),
    ('How do you sort ps output?', '--sort=-%cpu (or -rss, etime…).'),
    ('pgrep vs pidof?', 'pgrep matches patterns (and users, full command); pidof needs the exact name.'),
    ('What is RSS?', 'Resident set size: memory actually in RAM.'),
    ('What does wa mean in top?', 'CPU time spent waiting for I/O.'),
    ('How do you kill from top?', 'Press k, type the PID, Enter, signal (default 15).'),
    ('How do you see threads?', 'top -H or ps -eLf.'),
], [
    ('RHCSA (EX200)', '“Identify CPU/memory intensive processes and kill processes”.'),
    ('LFCS', 'Monitor processes and resources.'),
    ('CompTIA Linux+', 'ps, top, htop, pgrep, load average.'),
]) + distro('Same ideas everywhere; options differ on macOS.', [
    ('ps aux / -ef', 'yes', 'yes', 'yes (BSD ps)', '-'),
    ('ps --sort', 'yes', 'yes', 'no (use -r, -m)', '-'),
    ('top keys P/M', 'procps top', 'procps top', 'different top (o cpu)', 'Task Manager'),
    ('htop', 'apt install', 'dnf install', 'brew install', '-'),
    ('pstree', 'yes', 'yes', 'brew install', '-'),
]) + teaser('11.3', 'Riya found the hog: PID 4120, yes, 99% CPU. Now she must stop it. kill? kill -9? What is the difference between asking a process to stop and forcing it, and why can a process ignore one but not the other? Next: signals, kill, pkill, killall and trap.')

CHEATSHEET = cheatsheet('Watching processes', [
    ('ps', [('ps aux', 'all, resources'), ('ps -ef', 'all, PPID'), ('ps -u USER', 'one user'), ('ps -eo … --sort=-%cpu', 'top CPU'), ('ps -ef --forest', 'tree')]),
    ('find', [('pgrep -a NAME', 'PIDs + cmd'), ('pgrep -x', 'exact'), ('pgrep -f', 'full cmd'), ('pgrep -c', 'count'), ('pidof NAME', 'exact name')]),
    ('tree', [('pstree -p', 'with PIDs'), ('pstree -a', 'arguments'), ('pstree -s PID', 'ancestors'), ('pstree USER', 'one user')]),
    ('top', [('P / M / T', 'sort CPU/mem/time'), ('1 / c / H', 'CPUs/cmd/threads'), ('u / k / r', 'user/kill/renice'), ('top -b -n 1', 'batch'), ('q', 'quit')]),
])

MINDMAP = mindmap('Watch', [
    ('ps', 'blue', ['aux / -ef', '-eo cols', '--sort']),
    ('find', 'green', ['pgrep -a', '-x -f -u', 'not grep']),
    ('tree', 'amber', ['pstree -p', '-s ancestors', '--forest']),
    ('top', 'red', ['P M k q', '-b -n 1', 'load']),
    ('columns', 'violet', ['RSS real', 'VSZ reserved', 'TIME cpu']),
    ('load', 'acc', ['R + D', 'vs nproc', '1 5 15']),
])

LAB = lab('find the hog', 'Build the lab (it starts three processes), do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab112 && cd ~/lab112 && rm -f *.txt
pkill -u "$USER" -f lab112-worker; pkill -u "$USER" -x yes
(timeout 600 yes > /dev/null &)
(exec -a lab112-worker sleep 600 &); (exec -a lab112-worker sleep 601 &)
sleep 2''',
    tasks=['Write the PID of the process using the most CPU among your processes into <code>hog.txt</code>.',
           'Write the number of processes whose command line contains <code>lab112-worker</code> into <code>workers.txt</code> (use pgrep).',
           'Write the PPID of the hog into <code>parent.txt</code>.',
           'Write the first line of a batch-mode top run into <code>top.txt</code>.'],
    solution='''ps -u "$USER" -o pid= --sort=-%cpu | head -1 | tr -d ' ' > hog.txt
pgrep -c -f lab112-worker > workers.txt
ps -o ppid= -p "$(cat hog.txt)" | tr -d ' ' > parent.txt
top -b -n 1 | head -1 > top.txt''',
    check='''cd ~/lab112
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 hog"     '[ -s hog.txt ] && [ "$(cat hog.txt 2>/dev/null)" = "$(pgrep -u "$USER" -x yes)" ]'
ok "2 workers" '[ "$(cat workers.txt 2>/dev/null)" = 2 ]'
ok "3 parent"  '[ -s parent.txt ] && [ "$(cat parent.txt 2>/dev/null)" = "$(ps -o ppid= -p "$(pgrep -u "$USER" -x yes)" | tr -d " ")" ]'
ok "4 top"     'grep -q "^top - .*load average" top.txt 2>/dev/null'
pkill -u "$USER" -f lab112-worker; pkill -u "$USER" -x yes; true''')
