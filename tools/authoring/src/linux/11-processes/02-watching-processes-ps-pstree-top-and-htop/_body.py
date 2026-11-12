import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# a busy "server": one CPU hog (yes), one memory hog (python3 holding 80 MB), and a small tree (app → 2 workers)
HOG = r"""pkill -u riya -f app.sh; pkill -u riya -x yes; pkill -u riya -x python3; pkill -u riya -x sleep; rm -rf ~/ps; mkdir -p ~/ps; cd ~/ps
printf '#!/bin/bash\nsleep 300 &\nsleep 301 &\nwait\n' > app.sh; chmod +x app.sh
(setsid timeout 120 yes > /dev/null 2>&1 &)
(setsid timeout 120 python3 -c 'a = bytearray(80*1024*1024); import time; time.sleep(120)' > /dev/null 2>&1 &)
(setsid ./app.sh > /dev/null 2>&1 &)
sleep 1.5"""
KILL = 'pkill -u riya -x yes; pkill -u riya -x python3; pkill -u riya -x sleep; pkill -u riya -f app.sh; true'
ME = "ps -u riya -o pid,ppid,%cpu,%mem,rss,stat,etime,cmd --sort=-%cpu | grep -v -E ' (ps|grep|sort|head|awk|bash --norc)' "

HOOK = hook('3 a.m.: the website is slow and the server’s fan is screaming. Riya logs in and has two minutes to answer three questions: <b>what</b> is running, <b>who</b> started it, and <b>which one</b> is eating the CPU or the memory? Linux has a few tools for exactly this: <code>ps</code> takes a snapshot, <code>pstree</code> shows the family tree, <code>top</code> and <code>htop</code> show a live, sorted view. Reading their columns correctly (%CPU, RSS, VIRT, load average, STAT) is the difference between “I restarted everything” and “I found the one runaway process”.',
    ['take snapshots with <code>ps aux</code>, <code>ps -ef</code> and <code>ps -eo</code> with your own columns and sort order',
     'see who started what with <code>pstree -p</code>, <code>ps --forest</code> and <code>pgrep -a</code>',
     'read and drive <code>top</code>: the summary lines, load average, %CPU, RES vs VIRT, and keys P, M, k, u, 1, q',
     'know what <code>htop</code> adds, and avoid the classic mistakes (ps | grep matching itself, VIRT as memory use, load average vs CPU count)'])
ROAD = roadmap([
    ('story', 'The story', 3, '3 a.m., slow server'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What these tools show', 6, 'simple meaning + 4 depths'),
    ('types', 'ps styles, top vs htop', 4, 'and columns'),
    ('commands', 'Watching by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'top refreshing'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'find the hog'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Everything, one snapshot', 'ps aux', 'BSD style, %CPU %MEM'),
    ('Everything with PPID', 'ps -ef', 'System V style'),
    ('Top CPU users now', 'ps -eo pid,%cpu,cmd --sort=-%cpu | head', 'or top, press P'),
    ('Top memory users', 'ps -eo pid,rss,cmd --sort=-rss | head', 'or top, press M'),
    ('Find PIDs by name', 'pgrep -a NAME', 'not ps | grep'),
    ('Who started what', 'pstree -p   /   ps -ef --forest', 'the family tree'),
    ('Live, sorted, interactive', 'top   (htop if installed)', 'q to quit'),
    ('Into a log or script', 'top -b -n 1   /   ps -eo …', 'batch mode'),
])

cmap = concept_map(
    [('11.1', 'Processes', 'PID, PPID, states'), ('6.5', 'awk', 'columns'), ('5.3', 'Pipes', 'sort, head')],
    ['ps: snapshots (aux, -ef, -eo, --sort)', 'pgrep / pidof: PIDs by name', 'pstree and --forest: families', 'top: live view, load average, keys', 'htop and the columns that matter'],
    [('11.3', 'Signals and kill', 'stop the hog'), ('11.5', 'nice and /proc', 'priority and details'), ('15.4', 'Memory and swap', 'free, vmstat'), ('16.5', 'Monitoring', 'logs and alerts')],
    'ps answers “what is running”; top answers “what is busy right now”. Both read the same kernel data in /proc.')

sc = (term(20, 14, 316, 156, ['$ ps -u riya -o pid,%cpu,%mem,cmd --sort=-%cpu', ('  PID %CPU %MEM CMD', 'out'), (' 4120 99.1  0.0 yes', 'err'), (' 4121  2.6  1.1 python3 -c …', 'out'), (' 4122  0.0  0.0 /bin/bash ./app.sh', 'out'), ('$ pgrep -a yes', None), (' 4120 yes', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=15)
      + t(352, 36, 'Three questions:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• what runs? ps', '• who started it?', '  pstree', '• who is busy?', '  top / --sort'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A slow server at 3 a.m.</h2>
  <div class="story">
''' + puzzle('Riya’s 2-CPU server shows a load average of <code>4.00 3.90 3.20</code>. A colleague says “load 4 on a 2-core box, it’s twice overloaded!”. <code>top</code> shows the CPUs 95% idle and one process in state <b>D</b>. Is the CPU really the problem? What is load average actually counting?') + '''
    <p class="narration">Riya sorts the processes by CPU and finds the culprit in one line.</p>
''' + scene('A terminal: ps sorted by CPU shows a process called yes at 99% CPU at the top; pgrep finds its PID.', sc,
            'Sort by <tspan font-weight="700" class="s-acc">%CPU</tspan> or <tspan font-weight="700" class="s-acc">RSS</tspan>: the culprit is on top.') + '''
K> Why not just open top every time?
A> top is great for a live look. But ps is what you put in scripts, alerts and tickets: it prints once, with exactly the columns you choose, sorted the way you want. And <code>pstree</code> answers the third question: <b>who</b> started this process?
R> And the columns? There are so many.
A> Five matter almost every time: PID, USER, %CPU, RSS (real memory) and STAT. Today you will learn those well, and when VIRT, load average and TIME+ mislead you.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Three ways to watch processes: ps is a photo, pstree a family tree, top a live video sorted by who is busiest.">'
       + label_box(14, 20, 190, 110, ['ps = a photo', 'one snapshot', 'any columns', 'for scripts'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['pstree = family', 'parent → children', 'who started what', 'with -p: PIDs'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['top = live video', 'refresh every 3 s', 'sorted by %CPU', 'keys: P M k q'], 'amber', 8.6)
       + t(320, 160, 'All three read the same data from /proc.', 9.6, 'ink2')
       + t(320, 182, 'Photo for tickets, video for firefighting.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Watching processes at four depths', [
    ('v', 'No jargon: photo, family tree, video', '      <p>Three tools, three questions.</p>' + pic),
    ('b', 'What you will type every day', '''      <ul>
        <li><code>ps aux</code>: every process with user, %CPU, %MEM and command.</li>
        <li><code>ps -ef</code>: every process with PPID (the parent).</li>
        <li><code>pgrep -a nginx</code>: PIDs and commands whose name matches.</li>
        <li><code>top</code>: live list, busiest first. Press <kbd>M</kbd> for memory, <kbd>P</kbd> for CPU, <kbd>q</kbd> to quit.</li>
      </ul>'''),
    ('i', 'Columns that matter', '''      <ul>
        <li><b>%CPU</b> in ps = CPU time ÷ lifetime (an average); in top = share of the last interval. 100% = one full core; 4 cores can show 400%.</li>
        <li><b>RSS/RES</b> = real memory in RAM (KiB). <b>VSZ/VIRT</b> = all address space reserved, often huge and harmless. <b>SHR</b> = shared part (libraries).</li>
        <li><b>TIME / TIME+</b> = total CPU time used, not wall-clock time; <b>ELAPSED</b>/<b>etime</b> = how long it has run.</li>
        <li><b>Load average</b> (1, 5, 15 min) = average number of tasks running <b>or waiting</b> (R) plus those in disk wait (D). Compare it with <code>nproc</code>.</li>
        <li><b>PR/NI</b> = priority and nice value (Lesson 11.5); <b>TTY</b> <code>?</code> = no terminal (a daemon).</li>
      </ul>'''),
    ('a', 'Behind the screen: /proc and sampling', '''      <ul>
        <li>ps and top have no special access: they read <code>/proc/PID/stat</code>, <code>status</code>, <code>cmdline</code> and <code>/proc/loadavg</code>, <code>/proc/meminfo</code>. The kernel generates these files on demand.</li>
        <li>top computes %CPU by reading each process’s CPU ticks twice and dividing by the interval; that is why the first frame of <code>top -b -n 1</code> can differ from a later one.</li>
        <li>Linux load average includes D-state tasks (waiting for disk/NFS), so high load with idle CPUs points to storage, not CPU.</li>
        <li>Memory: RSS counts shared pages in every process that maps them, so adding RSS over processes over-counts. <code>PSS</code> (in <code>/proc/PID/smaps_rollup</code>) shares them fairly.</li>
        <li>Threads: <code>ps -eLf</code> and <code>top -H</code> show each thread; Java and browsers have hundreds.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>ps, pstree, top and htop</h2>
''' + def_block(
    '<code>ps</code> (process status) prints a one-time snapshot of selected processes with selected columns. <code>pstree</code> displays running processes as a tree of parents and children. <code>top</code> is an interactive, continuously updating view of processes sorted by resource use, with system summary lines (uptime, load average, tasks, CPU and memory). <code>htop</code> is a friendlier, colourful alternative to top with mouse support and scrolling.',
    'ps = a photo. pstree = a family tree. top/htop = a live video.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('%CPU', 'Share of one CPU core used.'),
    ('RSS / RES', 'Real memory in RAM.'),
    ('VSZ / VIRT', 'Reserved address space (not real use).'),
    ('TIME+', 'Total CPU time used so far.'),
    ('Load average', 'Tasks running or waiting, averaged.'),
    ('TTY', 'The terminal; ? = none (daemon).'),
    ('Batch mode', 'top -b: print, do not draw a screen.'),
    ('Snapshot', 'The state at one moment.'),
]) + '\n' + names('Where the names come from.', [
    ('ps', 'process status', 'Unix V4, 1973.'),
    ('aux', 'all, user-format, no-tty too', 'BSD options, no dash.'),
    ('-ef', 'every, full', 'System V options.'),
    ('top', 'top consumers', '1984.'),
    ('htop', 'Hisham’s top', 'Hisham Muhammad, 2004.'),
    ('pgrep', 'process grep', 'Solaris 7.'),
    ('RSS', 'resident set size', 'Pages in RAM.'),
    ('VSZ', 'virtual size', 'All mapped memory.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('All processes', '<code>ps aux</code> / <code>ps -ef</code>'),
    ('Sorted by CPU', '<code>ps … --sort=-%cpu</code>'),
    ('By name', '<code>pgrep -a NAME</code>'),
    ('Tree', '<code>pstree -p</code>'),
    ('Live', '<code>top</code>, <kbd>q</kbd> quits'),
    ('CPU count', '<code>nproc</code>'),
]) + '\n' + lv + didyou('<code>ps aux | grep nginx</code> always finds at least one process, even when nginx is not running: the <code>grep nginx</code> itself. That is why people write <code>grep [n]ginx</code>, or better, use <code>pgrep -a nginx</code>, which never matches itself.') + '''
EXAM> “Which command shows a dynamic real-time view of running processes?” → <code>top</code> (or htop). “A static snapshot?” → <code>ps</code>.
''' + qc('A 4-core server has load average 3.5. Is it overloaded?', 'No: up to about 4 the cores can keep up. Compare load with nproc; also check whether the load is D-state (disk) or real CPU.') + mistake('“VIRT 5.6 GB, this program uses 5.6 GB of RAM!”',
    'Look at RES/RSS (real RAM), and %MEM',
    'VIRT counts all reserved address space: mapped files, libraries, memory reserved but never touched. RES is what is really in RAM.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>ps styles, and top vs htop</h2>
''' + table(['', '<code>ps aux</code> (BSD)', '<code>ps -ef</code> (System V)', '<code>ps -eo …</code> (custom)'], [
    ['Dash', 'no dash', 'dash', 'dash'],
    ['Shows', 'USER PID %CPU %MEM VSZ RSS TTY STAT START TIME CMD', 'UID PID PPID C STIME TTY TIME CMD', 'exactly what you list'],
    ['Best for', 'resource use at a glance', 'parents (PPID)', 'scripts, sorting'],
    ['Tree', '<code>ps auxf</code>', '<code>ps -ef --forest</code>', '<code>--forest</code>'],
], minw=560) + table(['', 'top', 'htop'], [
    ['Installed', 'always (procps)', 'usually <code>apt install htop</code>'],
    ['Scrolling, mouse', 'limited / no', 'yes'],
    ['Kill, renice', '<kbd>k</kbd>, <kbd>r</kbd>', '<kbd>F9</kbd>, <kbd>F7</kbd>/<kbd>F8</kbd>'],
    ['Tree view', '<kbd>V</kbd>', '<kbd>F5</kbd>'],
    ['Search / filter', '<kbd>o</kbd> filter, <kbd>L</kbd> locate', '<kbd>F3</kbd> / <kbd>F4</kbd>'],
    ['Per-CPU bars', '<kbd>1</kbd>', 'at the top by default'],
    ['Scripts / logs', '<code>top -b -n 1</code>', 'not meant for it'],
], minw=440) + table(['Column (ps / top)', 'Meaning', 'Trap'], [
    ['%CPU', 'CPU share', 'ps: lifetime average; can exceed 100 with threads'],
    ['%MEM', 'RSS ÷ total RAM', '—'],
    ['RSS / RES', 'real RAM (KiB)', 'shared pages counted in each process'],
    ['VSZ / VIRT', 'address space', 'not real memory'],
    ['STAT / S', 'state (11.1)', 'D = disk wait, raises load'],
    ['TIME / TIME+', 'CPU time used', 'not how long it ran'],
    ['NI / PR', 'nice / priority', 'Lesson 11.5'],
], minw=480) + qc('Which ps style shows the parent PID by default?', '<code>ps -ef</code> (the PPID column). For ps aux you must add it with -o.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Watching processes, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as user riya, with three sample “problem” processes running: <code>yes</code> (a CPU hog), a <code>python3</code> holding 80 MB (a memory hog) and <code>app.sh</code> with two <code>sleep</code> workers. We show only riya’s processes (<code>-u riya</code>); the build machine’s own system processes are left out.</p>
''' + cmdcard_u(['a quick look at everything', 'tickets and reports', 'finding the user and %CPU of a process'],
               ['parsing ps aux in scripts (use -o)', 'ps aux | grep NAME (matches grep itself)'])(
    'aux', 'ps aux · ps -ef', 'snapshot of all processes',
    '<code>ps aux</code> lists every process (a), with user-oriented columns (u), including those without a terminal (x). <code>ps -ef</code> lists every process (-e) in full format (-f) with PPID. Add <code>f</code>/<code>--forest</code> for a tree.',
    'ps aux   ·   ps -ef   ·   ps -u USER', 'safe',
    [('aux', 'all, user columns', 'resources'),
     ('-ef', 'all, with PPID', 'families'),
     ('-u USER', 'one user', 'focus'),
     ('-p PID', 'chosen PIDs', 'details'),
     ('auxf / --forest', 'ASCII tree', 'who started'),
     ('ww', 'do not cut long lines', 'full cmd')],
    dict(setup=HOG, cmd="ps u -u riya | grep -v -E ' (ps|grep|bash --norc)'", note='ps u = user columns. yes has %CPU ≈ 99 (one core); python3 has RSS ≈ 92 MB. TTY ? = no terminal.'),
    [('sys', [
        dict(situation='ps -ef: who is the parent?', setup=HOG, cmd="ps -f -u riya | grep -E 'UID|app.sh|sleep 30' | grep -v grep",
             why='PPID column: the two sleep workers have app.sh’s PID as their parent.')]),
     ('qa', [
        dict(situation='The grep that finds itself.', setup=HOG, cmd="ps aux | grep yes | grep -v -E 'grep -v'\nps aux | grep '[y]es' | grep -v -E 'grep'\npgrep -a yes",
             why='The first line includes the grep process itself. [y]es does not match its own text. pgrep never matches itself.')]),
    ],
    anat=anatomy([('ps', 'cmd', 'process status'), ('a', 'opt', 'all users'), ('u', 'opt', 'user format'), ('x', 'opt', 'no tty too')], 'BSD options have no dash; ps -aux works but warns on some systems.')
) + cmdcard_u(['scripts, alerts and reports', 'finding the top CPU or memory users', 'exact columns'],
               ['default ps output in scripts (columns differ by system)'])(
    'eo', 'ps -eo … --sort', 'your own columns',
    '<code>-o</code> picks columns (pid, ppid, user, %cpu, %mem, rss, vsz, stat, etime, time, ni, comm, cmd…), <code>--sort</code> sorts (minus = descending). Pipe to <code>head</code> for the top N.',
    'ps -eo COLS --sort=-%cpu | head -N', 'safe',
    [('--sort=-%cpu', 'busiest CPU first', 'firefighting'),
     ('--sort=-rss', 'biggest RAM first', 'memory'),
     ('etime', 'running for', 'old processes'),
     ('time', 'CPU time used', 'heavy jobs'),
     ('comm / cmd', 'name / full command', 'readability'),
     ('-o pid=', 'no header', 'scripts')],
    dict(setup=HOG, cmd=ME + "| head -5", note='Sorted by %CPU: the culprit is the first line.'),
    [('sys', [
        dict(situation='Top memory users.', setup=HOG, cmd="ps -u riya -o pid,rss,vsz,%mem,comm --sort=-rss | head -3",
             why='RSS (real) 92 MB vs VSZ (reserved) bigger. Sort by RSS, not VSZ.')]),
     ('devops', [
        dict(situation='Processes running longer than an hour (stuck jobs).', setup=HOG, cmd="ps -u riya -o etimes=,pid=,comm= | awk '$1 > 3600 {print}' | wc -l\nps -u riya -o etimes=,pid=,comm= | awk '$1 > 1 {print $3}' | sort -u",
             why='etimes = elapsed seconds (a number, easy to compare). Here nothing is older than an hour; the second line lists those older than 1 s.')]),
    ]
) + cmdcard_u(['finding PIDs by name in scripts', 'checking whether a service is running'],
               ['ps | grep in scripts', 'pgrep -f with a short pattern (matches too much)'])(
    'pgrep', 'pgrep · pidof', 'PIDs by name',
    '<code>pgrep PATTERN</code> prints PIDs whose process name matches (a regex); <code>-a</code> adds the command line, <code>-l</code> the name, <code>-u</code> a user, <code>-x</code> exact name, <code>-f</code> matches the full command line, <code>-c</code> counts, <code>-n/-o</code> newest/oldest. <code>pidof NAME</code> needs the exact program name.',
    'pgrep [-a] [-u USER] [-x] [-f] PATTERN   ·   pidof NAME', 'safe',
    [('-a', 'show command line', 'readable'),
     ('-x', 'exact name', 'precise'),
     ('-f', 'match full command', 'scripts by name'),
     ('-u USER', 'only that user', 'focus'),
     ('-c', 'count', 'checks'),
     ('-n / -o', 'newest / oldest', 'one PID')],
    dict(setup=HOG, cmd="pgrep -a -u riya sleep\npgrep -c -u riya sleep\npgrep -a -f app.sh", note='-f matched app.sh in the command line /bin/bash ./app.sh (its process name is bash).'),
    [('devops', [
        dict(situation='Health check: is it running?', setup=HOG, cmd="if pgrep -x -u riya yes > /dev/null; then echo 'yes is running'; else echo 'yes is NOT running'; fi\npgrep -x nginx > /dev/null || echo 'nginx is NOT running'",
             why='pgrep exits 0 if something matched, 1 if not: perfect for if.')]),
    ]
) + cmdcard_u(['understanding who started what', 'finding the parent of a strange process', 'service and container trees'],
               ['huge trees without -p or a PID (too long)'])(
    'pstree', 'pstree · ps --forest', 'the family tree',
    '<code>pstree</code> draws processes as a tree. <code>-p</code> adds PIDs, <code>-a</code> arguments, <code>-u</code> user changes, <code>-s PID</code> the parents of PID. Give a PID or user to show only that branch. <code>ps -ef --forest</code> gives a similar tree with all ps columns.',
    'pstree [-p] [-a] [-s] [PID|USER]   ·   ps -ef --forest', 'safe',
    [('-p', 'show PIDs', 'kill the right one'),
     ('-a', 'show arguments', 'which script'),
     ('-s PID', 'ancestors of PID', 'who started it'),
     ('-u', 'show user changes', 'sudo, services'),
     ('USER', 'only that user’s trees', 'focus'),
     ('--forest', 'tree inside ps', 'with columns')],
    dict(setup=HOG, cmd="pstree -pa $(pgrep -n -f -u riya app.sh)", note='app.sh (a bash process) has two sleep children.'),
    [('sec', [
        dict(situation='Who started this sleep? Walk up the tree.', setup=HOG, cmd="pstree -s -p $(pgrep -u riya -n -x sleep) | sed -E 's/^.*(bash\\()/…\\1/'",
             why='-s shows the ancestors. In incident response, a shell whose ancestor is a web server is a red flag.')]),
     ('sys', [
        dict(situation='The same with ps.', setup=HOG, cmd="ps -o pid,ppid,cmd --forest -g $(pgrep -n -f -u riya app.sh)",
             why='-g = process group (the script and its children); --forest draws the branches.')]),
    ]
) + mistake('ps aux | grep nginx | wc -l   (to count nginx processes)', 'pgrep -c nginx',
            'The grep line itself is counted, so the answer is always one too many, and 1 when nginx is not running at all.') + cmdcard_u(['live firefighting', 'watching a process over time', 'batch logs (top -b)'],
               ['reading %CPU from the very first top -b frame', 'leaving top running in scripts without -n'])(
    'top', 'top', 'live view',
    '<code>top</code> refreshes every 3 seconds. Summary: uptime and load average, task counts by state, CPU split (us user, sy system, ni nice, id idle, wa I/O wait, st steal), memory and swap. Keys: <kbd>P</kbd> CPU sort, <kbd>M</kbd> memory, <kbd>T</kbd> time, <kbd>1</kbd> per CPU, <kbd>c</kbd> full command, <kbd>u</kbd> user, <kbd>k</kbd> kill, <kbd>r</kbd> renice, <kbd>H</kbd> threads, <kbd>q</kbd> quit.',
    'top [-u USER] [-p PID] [-o FIELD] [-d SEC] [-b -n N]', 'safe',
    [('-u USER', 'one user', 'focus'),
     ('-p PID,…', 'chosen PIDs', 'watch one'),
     ('-o %MEM', 'sort field', 'memory'),
     ('-d 1', 'refresh every 1 s', 'fast'),
     ('-b -n 1', 'print once', 'logs, scripts'),
     ('-H', 'threads', 'Java, browsers')],
    dict(setup=HOG, cmd="top -b -n 2 -d 1 -u riya | awk '/^top -/{n++} n==2' | sed -n '1p;7,10p'", note='Second frame (accurate %CPU): yes at ≈100% of one core in state R. First line: uptime, users, load average.'),
    [('sys', [
        dict(situation='Read the summary lines.', setup=HOG, cmd="top -b -n 2 -d 1 | awk '/^top -/{n++} n==2' | sed -n '1,5p' | cut -c1-74\nnproc",
             why='Load ≈ 1 with 2 CPUs: fine. %Cpu id = idle; wa = waiting for disk. avail Mem is what new programs can still get.')]),
     ('devops', [
        dict(situation='Log the top 3 every minute (cron-friendly).', setup=HOG, cmd="top -b -n 1 -o %MEM -u riya | sed -n '7,9p'",
             why='Batch mode, sorted by memory, only the table lines: append to a file from cron to see what grew overnight.')]),
    ]
) + undo('Watching never changes anything; only quitting matters.', [
    ('Stuck inside top:', 'press <kbd>q</kbd> (or <kbd>Ctrl</kbd>+<kbd>C</kbd>).'),
    ('Pressed k in top by accident:', 'press <kbd>Esc</kbd> or Enter on an empty PID to cancel.'),
    ('Changed top’s layout and saved it (W):', 'delete <code>~/.config/procps/toprc</code>.'),
    ('htop not installed:', '<code>sudo apt install htop</code> (Lesson 14.1), or use top.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='ps -o pid,cpu', meaning='Wrong column name (it is %cpu, pcpu).', fix='<code>ps L</code> lists all column names.'),
    dict(cmd='ps --sort=cpu% -e', meaning='Unknown sort key.', fix='<code>--sort=-%cpu</code> or <code>-pcpu</code>.'),
    dict(cmd='top -n 1', meaning='Not a terminal: top needs -b in pipes and scripts.', fix='<code>top -b -n 1</code>.'),
    dict(cmd='htop', meaning='htop is not installed (exit 127).', fix='<code>sudo apt install htop</code>, or top.'),
]) + qc('top shows <code>wa 60.0</code>. What is slow?', 'The disk (or network storage): CPUs are idle waiting for I/O. Look for D-state processes and use iostat/iotop (Lesson 15.4).') + '''
'''
_sh.run_sh(KILL, 'any')

SCREENS = screens_block('Real terminal screens: driving top', 'top running in a 90×16 terminal as riya, showing only riya’s processes, while the sample hogs run.',
    HOG, 'top -u riya -d 1', [
    ('M', 'M', ' sort by memory: python3 (80 MB) jumps to the top. (Press P to go back to CPU order.)'),
    ('q', 'q', ' quit: back to the shell.'),
], 90, 16, hid='screens', what='top')
_sh.run_sh(KILL, 'any')
cards = cards + SCREENS + '</section>\n'

def topf(k):
    rows = [[('yes', '99.7', '0.0'), ('python3', '0.0', '1.1'), ('app.sh', '0.0', '0.0')],
            [('python3', '0.0', '1.1'), ('yes', '99.7', '0.0'), ('app.sh', '0.0', '0.0')],
            [('yes', '99.7', '0.0'), ('python3', '0.0', '1.1'), ('app.sh', '0.0', '0.0')],
            [('python3', '0.0', '1.1'), ('app.sh', '0.0', '0.0'), ('', '', '')]][k]
    o = t(20, 22, 'CMD', 8, 'ink2', anchor='start', bold=True) + t(170, 22, '%CPU', 8, 'ink2', anchor='start', bold=True) + t(240, 22, '%MEM', 8, 'ink2', anchor='start', bold=True)
    for i, (n, c, m) in enumerate(rows):
        if not n:
            continue
        tn = 'red' if (k in (0, 2) and i == 0) or (k == 1 and i == 0) else 'card'
        o += label_box(14, 30 + i * 36, 300, 30, [f'{n}'], tn, 8) + t(185, 49 + i * 36, c, 8, 'ink', anchor='middle') + t(255, 49 + i * 36, m, 8, 'ink', anchor='middle')
    return o
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip([['$ top -u riya', ('…sorted by %CPU', 'out')], ['(press M)', ('…sorted by %MEM', 'out')], ['(press P)', ('…back to %CPU', 'out')], ['(press k, PID, Enter)', ('yes is gone', 'acc')]],
                       ['Start: busiest CPU first.', 'M: memory order.', 'P: CPU order.', 'k: kill the hog (11.3).'])]
behind = [topf(k) + t(180, 150, n, 8.6, 'violet', bold=True) for k, n in enumerate(['Every 3 s top re-reads /proc and sorts.', 'Same data, sorted by RES.', 'Same data, sorted by %CPU.', 'Next refresh: the process is no longer in /proc.'])]
two = anim_two('top refreshing', 'Behind the screen: re-read, sort, draw',
               'A terminal running top: sorted by CPU, then memory, then CPU, then the hog is killed.',
               'A table of three processes with %CPU and %MEM, re-sorted as keys are pressed; after kill the yes row disappears.', see, behind,
               ['P (default).', 'M.', 'P.', 'k.'],
               ['read /proc', 'sort by RES', 'sort by %CPU', 'process gone'])

def load(k):
    cpus = ''.join(label_box(14 + i * 74, 26, 66, 40, [f'CPU {i}', ['busy', 'busy', 'idle', 'idle'][i] if k else 'idle'], 'green' if k and i < 2 else 'card', 8) for i in range(2))
    q = ''
    if k >= 2:
        q += ''.join(label_box(14 + i * 50, 90, 44, 30, ['R'], 'amber', 8) for i in range(2))
    if k == 3:
        cpus = ''.join(label_box(14 + i * 74, 26, 66, 40, [f'CPU {i}', 'idle'], 'card', 8) for i in range(2))
        q = ''.join(label_box(14 + i * 50, 90, 44, 30, ['D'], 'red', 8) for i in range(4))
    return cpus + q
frames = [load(0) + t(180, 150, 'Nothing to do: load 0.', 8.6, 'violet', bold=True),
          load(1) + t(180, 150, '2 running on 2 CPUs: load 2 = fully used.', 8.6, 'green', bold=True),
          load(2) + t(180, 150, '2 more waiting (R): load 4 = overloaded.', 8.6, 'amber', bold=True),
          load(3) + t(180, 150, '4 in disk wait (D), CPUs idle: load 4 too!', 8.6, 'red', bold=True)]
s1 = anim_one('Animated example', 'What load average really counts',
              'Tasks running, waiting for a CPU, or waiting for the disk.',
              'load average', 'Two CPU boxes and queues: load counts running tasks plus those waiting for a CPU (R) plus those in disk wait (D), so load 4 can mean busy CPUs or a slow disk.', frames,
              ['Load 0.', 'Load 2.', 'Load 4 (CPU).', 'Load 4 (disk).'], hid='scenario-load')

dx = dissect('Layer by layer: where ps and top get their numbers',
    'Each layer has a real command and output from our build machine.', [
    dict(key='tool', name='ps / top', sub='the display', why='Readable columns.', how='Reads /proc.', impl='procps-ng.', used='Every admin.',
         setup=HOG, cmd="ps -o pid,stat,rss,comm -p $(pgrep -u riya -x yes)"),
    dict(key='stat', name='/proc/PID/stat', sub='raw numbers', why='CPU ticks, state.', how='One line.', impl='Kernel text.', used='%CPU, TIME.',
         setup=HOG, cmd="cut -d' ' -f1-3,14,15 /proc/$(pgrep -u riya -x yes)/stat"),
    dict(key='status', name='/proc/PID/status', sub='readable', why='Memory, threads.', how='Key: value.', impl='VmRSS = RSS.', used='Debugging.',
         setup=HOG, cmd="grep -E '^(Name|State|VmSize|VmRSS|Threads)' /proc/$(pgrep -u riya -x python3)/status"),
    dict(key='load', name='/proc/loadavg', sub='system', why='Load numbers.', how='1, 5, 15 min.', impl='Running/total, last PID.', used='uptime, top.',
         setup=HOG, cmd="cat /proc/loadavg | awk '{print \"load:\", $1, $2, $3, \" running/total:\", $4}'; uptime | sed 's/.*load/load/'"),
], hint='From the table you read to the kernel’s numbers. Click a layer.')

hd = hood('Under the hood: ps reads /proc, file by file', 'The real file system calls of <code>ps -p PID -o pid,comm</code> on our build machine: it opens the process’s files in /proc.',
          'ps -p $$ -o pid,comm', show='/proc/[0-9]', trace='openat', start='/proc/[0-9]')
_sh.run_sh(KILL, 'any')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>top refreshing, and what load average means</h2>
''' + two + s1 + dx + hd + qc('ps says a process has %CPU 50, top says 0. Who is right?', 'Both: ps shows the average over its whole life, top the last interval. It was busy earlier and is idle now.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Watching processes at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['--sort', '-%cpu'], 'red', 8.6), '1. Incidents',
              'The first minute of a slowness incident: top or ps sorted by CPU and memory, load vs nproc.', ['Alert', '*ps --sort', 'act']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['pgrep -x', 'health'], 'green', 8.6), '2. Health checks',
    'Scripts and monitoring check that a process exists with pgrep and restart or alert if not.', ['Check', '*pgrep', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['pstree -s', 'forensics'], 'amber', 8.6), '3. Security',
    'Investigators trace an odd process to its parent: a shell under a web server or cron points to compromise.', ['Odd PID', '*pstree -s', 'contain']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['top -b', 'logs'], 'blue', 8.6), '4. Capacity',
    'Batch snapshots in cron show which process grew overnight (memory leaks).', ['Cron', '*top -b', 'trend']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-H / -L', 'threads'], 'violet', 8.6), '5. Java and DB tuning',
    'top -H shows the thread using the CPU; its TID in hex finds it in a Java thread dump.', ['Hot thread', '*top -H', 'fix']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Top 3 CPU', scenario='Who is busy?', setup=HOG, cmd=ME + "| head -4 | awk '{print $1, $3, $8}'", explain='--sort=-%cpu.'),
    dict(level='b', title='Is it running?', scenario='Quick check.', setup=HOG, cmd="pgrep -x yes -u riya > /dev/null && echo running", explain='pgrep exit status.'),
    dict(level='i', title='Count by name', scenario='How many workers?', setup=HOG, cmd="ps -u riya -o comm= | sort | uniq -c | sort -rn | head -3", explain='uniq -c.'),
    dict(level='i', title='RAM of one program', scenario='Total RSS of riya’s python3 processes.', setup=HOG, cmd="ps -o rss= -p $(pgrep -d, -u riya -x python3) | awk '{s+=$1} END {printf \"%.0f MB\\n\", s/1024}'", explain='pgrep -d, gives a PID list for ps -p. (ps -C NAME -u USER would OR the two, not AND.)'),
    dict(level='a', title='Parent of the hog', scenario='Who started it?', setup=HOG, cmd="ps -o ppid= -p $(pgrep -u riya -x yes) | xargs -I{} ps -o pid,comm -p {}", explain='Two ps calls.'),
], extra=build_up('finding the hog', 'Riya answers the three 3 a.m. questions in order.', HOG, [
    ('uptime | sed "s/.*load/load/"; nproc', '1. How loaded, and how many CPUs?'),
    (ME + "| head -3", '2. Who uses the CPU?'),
    ("ps -u riya -o pid,rss,comm --sort=-rss | head -2", '3. Who uses the memory?'),
    ("pstree -sp $(pgrep -u riya -x yes) | sed -E 's/^.*(timeout)/…\\1/'", '4. Who started the hog?'),
])) + which('Choosing the right tool.', [
    ('Everything, now', 'ps aux', 'One snapshot.', 'Parsing it in scripts.'),
    ('Parents', 'ps -ef / pstree -p', 'PPID / tree.', 'Guessing from names.'),
    ('Top consumers', 'ps -eo … --sort=-%cpu', 'Exact columns.', 'Sorting by VSZ.'),
    ('PID by name', 'pgrep -a', 'Never matches itself.', 'ps | grep.'),
    ('Live', 'top / htop', 'Updates, keys.', 'top in a script without -b.'),
    ('Log a snapshot', 'top -b -n 1', 'Text output.', 'Screen output in a file.'),
]) + keys('Handy forms.', [
    ('ps aux --sort=-%mem | head', 'memory hogs', 'RAM'),
    ('ps -ef --forest', 'tree with columns', 'families'),
    ('pgrep -af PATTERN', 'match full command', 'scripts'),
    ('pstree -p USER', 'one user’s trees', 'focus'),
    ('top -u USER -d 1', 'live, one user', 'watch'),
    ('watch -n 2 "ps …"', 'repeat any ps', 'DIY top'),
]) + scriptit('hogs.sh', 'A one-screen report for a ticket: load vs CPUs, the top 3 CPU and memory users of a user, and their parents.',
'''u=${1:-$USER}
read l1 l5 l15 rest < /proc/loadavg
echo "load $l1 $l5 $l15 on $(nproc) CPUs"
echo "--- top CPU"
ps -u "$u" -o pid=,ppid=,%cpu=,comm= --sort=-%cpu | grep -v -E ' (ps|grep|bash)$' | head -3
echo "--- top RAM (MB)"
ps -u "$u" -o pid=,rss=,comm= --sort=-rss | head -3 | awk '{printf "%6s %6.0f %s\\n", $1, $2/1024, $3}' ''',
'<p>Run for riya while the sample hogs run.</p>', expect='any') + puzzle_answer('Load average counts tasks that are running <b>or waiting</b>, and on Linux also tasks in <b>D</b> state (uninterruptible disk/NFS wait). With CPUs 95% idle and a D-state process, the load comes from waiting for storage, not from the CPU. Check <code>wa</code> in top, D processes (<code>ps -eo stat,pid,cmd | grep ^D</code>) and the disk or NFS server.') + qc('Which column shows the parent in <code>ps -ef</code>?', 'PPID.') + '''
</section>
'''

_sh.run_sh(KILL + '; rm -rf ~/ps', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-what-is-a-process-pid-ppid-fork-exec/">Lesson 11.1</a> (PID, PPID, states).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
