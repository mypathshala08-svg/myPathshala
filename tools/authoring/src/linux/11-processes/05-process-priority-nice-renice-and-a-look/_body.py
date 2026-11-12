import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

CLEAN = "pkill -u riya -f 'while :'; pkill -u riya -x sleep; pkill -u riya -x yes; rm -rf ~/nc; mkdir -p ~/nc; cd ~/nc"
LOOP = '"while :; do :; done"'
RACE = ("taskset -c 0 timeout 4 sh -c " + LOOP + " & taskset -c 0 nice -n {n} timeout 4 sh -c " + LOOP + " & sleep 3\n"
        "ps -o ni=,%cpu=,args= -u riya | grep '[w]hile' | grep -v timeout | awk '{{printf \"  nice %3s  CPU %5s%%\\n\", $1, $2}}'; wait")

HOOK = hook('Every night at 1 a.m. Riya’s report job compresses gigabytes of logs and uses all the CPU. Customers in other time zones complain that the website is slow at that hour. She does not want to kill the job, only make it <b>polite</b>: run at full speed when the machine is idle, and step aside when the web server needs the CPU. Linux lets every process have a <b>nice value</b> from −20 (greedy) to 19 (very polite). <code>nice</code> starts a command with a value, <code>renice</code> changes it for a running process, and <code>ionice</code> does the same for disk access. This lesson shows the real effect with measured numbers.',
    ['explain nice values (−20 to 19), priority (PRI/PR) and who may raise or lower them',
     'start commands with nice -n, change running processes with renice -n -p / -u / -g',
     'read NI and PR in ps and top, and measure the effect when two processes compete for one CPU',
     'use ionice classes for disk-heavy jobs and know when to use cgroups, chrt or taskset instead'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the polite report job'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What niceness is', 6, 'simple meaning + 4 depths'),
    ('types', 'Values and classes', 5, 'nice, PRI, ionice'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'two jobs, one CPU'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'make jobs polite'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Start a heavy job politely', 'nice -n 19 ./job.sh', 'nice'),
    ('A running job is too greedy', 'renice -n 15 -p PID', 'renice'),
    ('All processes of a user', 'sudo renice -n 10 -u aman', 'renice -u'),
    ('Make something MORE important', 'sudo renice -n -5 -p PID', 'root only'),
    ('Disk-heavy backup', 'ionice -c3 nice -n 19 tar …', 'ionice idle'),
    ('See the values', 'ps -o pid,ni,pri,cmd   ·   top (NI, PR)', 'check'),
    ('Hard CPU limit (not just polite)', 'systemd-run -p CPUQuota=20% …', 'cgroups'),
    ('Pin to one CPU', 'taskset -c 0 cmd', 'affinity'),
])

cmap = concept_map(
    [('11.2', 'ps and top', 'NI and PR columns'), ('11.3', 'Signals', 'STOP/CONT, the other way'), ('11.4', 'Jobs', 'background jobs')],
    ['nice values −20 … 19', 'PRI / PR vs NI', 'nice, renice -p -u -g', 'who may change what', 'ionice classes', 'measured CPU shares'],
    [('11.6', 'tmux', 'long nice jobs in a session'), ('17.3', 'systemd units', 'Nice=, CPUWeight='), ('18.3', 'Performance', 'load average'), ('20.3', 'cgroups', 'hard limits')],
    'Niceness is how polite a process is about the CPU: higher nice, smaller share when others want the CPU. With no competition it changes nothing.')

sc = (term(20, 14, 316, 156, ['$ nice -n 19 ./report.sh &', ('[1] 4120', 'out'), '$ ps -o pid,ni,%cpu,comm -p 4120', ('  PID  NI %CPU COMMAND', 'out'), (' 4120  19  2.1 report.sh', 'acc'), '$ renice -n 10 -p 4120', ('4120 … old priority 19 …', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.6, step=16)
      + t(352, 36, 'Nice scale:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['−20 greedy (root)', '0 normal (default)', '19 very polite', 'user: only up', 'root: up and down'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The polite report job</h2>
  <div class="story">
''' + puzzle('Riya runs <code>nice -n 19 ./report.sh</code> on an idle server and it still shows 99% CPU in top: “nice does not work!” Then she tries <code>renice -n 19 -p PID</code> and later <code>renice -n 5 -p PID</code> to make it a bit faster again, and gets “Permission denied”. Finally <code>nice -n 19 tar czf …</code> still makes the disk so busy that the database slows down. Explain all three.') + '''
    <p class="narration">Riya starts the report with the highest nice value and checks it.</p>
''' + scene('A terminal: the report starts with nice 19, ps shows NI 19, and renice changes it to 10.', sc,
            'High nice = <tspan font-weight="700" class="s-acc">small share</tspan> when others need the CPU.') + '''
K> Why is it called “nice”?
A> Because a process with a high value is being nice to the others: it lets them go first. The default is 0. Users can only make their processes nicer (higher); only root can make them greedier (lower, down to −20).
R> And the speed?
A> Nice is a <b>share</b>, not a limit. If nobody else wants the CPU, a nice-19 process still gets 100%. The difference only shows when processes compete; we will measure it. Today: nice, renice, ionice, and what to use for hard limits.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A queue at a single ticket counter. A person with nice 0 walks up normally; one with nice 19 keeps letting others go first; one with nice −20 (only allowed for staff, root) goes straight to the front. When nobody else is waiting, even the polite person is served immediately.">'
       + label_box(20, 24, 180, 110, ['nice −20', 'staff badge (root):', 'goes first', 'big share'], 'red', 9)
       + label_box(230, 24, 180, 110, ['nice 0', 'normal visitor', '(default)', 'fair share'], 'blue', 9)
       + label_box(440, 24, 180, 110, ['nice 19', '“after you”', 'lets others go', 'small share'], 'green', 9)
       + t(320, 162, 'Empty queue? Even the polite one is served at once.', 10, 'acc', bold=True)
       + t(320, 184, 'nice changes the share when there is competition, not the speed alone.', 9.2, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Priority at four depths', [
    ('v', 'No jargon: a queue at one counter', '      <p>How polite you are only matters when others are waiting.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>nice -n 19 ./backup.sh</code>: start politely.</li>
        <li><code>renice -n 15 -p 4120</code>: change a running process.</li>
        <li><code>ps -o pid,ni,cmd -p 4120</code>: check the NI column.</li>
        <li>In <code>top</code>, press <kbd>r</kbd> to renice.</li>
      </ul>'''),
    ('i', 'Rules and numbers', '''      <ul>
        <li>Range −20 … 19; default 0; children inherit the parent’s value.</li>
        <li><code>nice cmd</code> without -n adds 10.</li>
        <li>Normal users may only <b>increase</b> niceness, and cannot decrease it again (even back to the old value). Root may do both. Limits can be relaxed in <code>/etc/security/limits.conf</code> (<code>nice</code> item).</li>
        <li>ps shows NI and PRI (PRI = 19 − NI with -o pri); top shows PR = 20 + NI.</li>
        <li>ionice classes: 1 realtime (root), 2 best-effort with levels 0–7 (default derived from nice), 3 idle (only when the disk is free).</li>
      </ul>'''),
    ('a', 'Behind the screen: weights in the scheduler', '''      <ul>
        <li>The Linux scheduler (CFS, and EEVDF since kernel 6.6) gives each runnable task a <b>weight</b> from its nice value: nice 0 = 1024, each step is about ×1.25. Nice 19 = 15, nice −20 = 88761.</li>
        <li>CPU time is shared in proportion to weights: nice 0 vs nice 19 on one CPU ≈ 1024 : 15, about 98.5% vs 1.5%. That is what we measure below.</li>
        <li>With autogroup (desktop kernels), nice works only between processes of the same session/group; across groups, groups are shared fairly.</li>
        <li>Real-time policies (SCHED_FIFO, SCHED_RR via <code>chrt</code>) run before all normal tasks; nice does not apply to them.</li>
        <li>For hard limits use cgroups v2: <code>cpu.max</code> (quota) and <code>cpu.weight</code>; systemd exposes them as CPUQuota= and CPUWeight=.</li>
        <li>ionice only has an effect with I/O schedulers that support classes (BFQ; partly mq-deadline). On many NVMe disks with “none” it does little.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Nice values, nice, renice and ionice</h2>
''' + def_block(
    'The <b>nice value</b> (niceness) of a process, from −20 to 19, tells the CPU scheduler how large a share of CPU time the process should get when processes compete; higher values mean a smaller share. <code>nice</code> runs a command with a given niceness, <code>renice</code> changes the niceness of running processes, users or groups, and <code>ionice</code> sets the I/O scheduling class and priority for disk access.',
    'A politeness number for the CPU (nice) and the disk (ionice).') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Nice value (NI)', '−20 … 19; default 0.'),
    ('Priority (PRI / PR)', 'The kernel’s number derived from NI.'),
    ('Scheduler', 'Kernel part that decides who runs.'),
    ('Weight', 'Share of CPU from the nice value.'),
    ('renice', 'Change niceness of running processes.'),
    ('ionice', 'Priority for disk I/O.'),
    ('Idle class', 'ionice -c3: only when the disk is free.'),
    ('cgroup limit', 'A hard cap, unlike nice.'),
]) + '\n' + names('Where the names come from.', [
    ('nice', 'be nice to others', 'Unix V4, 1973.'),
    ('renice', 're-nice', '4.2BSD, 1983.'),
    ('ionice', 'I/O nice', 'util-linux, 2005.'),
    ('NI', 'nice', 'ps/top column.'),
    ('PRI / PR', 'priority', 'ps / top column.'),
    ('CFS', 'Completely Fair Scheduler', 'Linux 2.6.23, 2007.'),
    ('EEVDF', 'earliest eligible virtual deadline first', 'Linux 6.6, 2023.'),
    ('chrt', 'change real-time', 'util-linux.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Start nicely', '<code>nice -n 19 cmd</code>'),
    ('Change', '<code>renice -n 10 -p PID</code>'),
    ('Check', '<code>ps -o ni -p PID</code>'),
    ('Disk', '<code>ionice -c3 cmd</code>'),
    ('User range', '0 … 19, only upwards'),
    ('Root range', '−20 … 19'),
]) + '\n' + lv + didyou('A nice-19 process competing with a nice-0 process on one CPU gets about 1.5% of the time, not 50% less: the weights are 15 vs 1024. We measured 1.3% vs 97.3% on our build machine.') + '''
EXAM> “What is the range of nice values and the default?” → −20 (highest priority) to 19 (lowest); default 0. Only root can set negative values.
''' + qc('A user ran <code>renice -n 19</code> on her job. Can she set it back to 0?', 'No. Unprivileged users may only increase niceness; going back down needs root (or a limits.conf rule).') + mistake('expecting nice to make a job slower on an idle machine',
    'nice only changes the share when others compete; for a hard cap use systemd-run -p CPUQuota=20% or cgroups',
    'On an idle server a nice-19 job still uses ~100% CPU (the puzzle). That is correct: unused CPU is not wasted.') + mistake('nice for disk-heavy jobs only',
    'ionice -c3 nice -n 19 cmd   (both CPU and disk)',
    'nice affects the CPU scheduler; disk I/O needs ionice (and a scheduler that supports it).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Nice values, priorities and I/O classes</h2>
''' + table(['NI', 'Meaning', 'Weight', 'Who may set it', 'Typical use'], [
    ['−20', 'greediest', '88761', 'root', 'rarely: critical daemons'],
    ['−5', 'more important', '3121', 'root', 'database, audio'],
    ['0', 'normal (default)', '1024', 'everyone', 'most programs'],
    ['5', 'a bit polite', '335', 'everyone', 'builds while you work'],
    ['10', 'polite (nice default)', '110', 'everyone', '<code>nice cmd</code>'],
    ['19', 'most polite', '15', 'everyone', 'backups, reports, indexing'],
], minw=520) + table(['Tool', 'Shows', 'For NI 0', 'For NI 19'], [
    ['<code>ps -o ni</code>', 'nice value', '0', '19'],
    ['<code>ps -o pri</code>', '19 − NI (BSD style, higher = more important)', '19', '0'],
    ['<code>top</code> PR', '20 + NI (kernel style, lower = more important)', '20', '39'],
    ['<code>ps -l</code> PRI', '80 + NI', '80', '99'],
], minw=480) + table(['ionice class', 'Name', 'Levels', 'Who', 'Meaning'], [
    ['1', 'realtime', '0–7', 'root', 'served before everyone (dangerous)'],
    ['2', 'best-effort', '0–7 (0 = highest)', 'everyone', 'default; level follows nice'],
    ['3', 'idle', '-', 'everyone', 'only when no one else uses the disk'],
    ['0', 'none', '-', '-', 'not set: best-effort from nice'],
], minw=480) + table(['Want', 'Tool', 'Effect'], [
    ['Polite CPU share', 'nice / renice', 'soft: only under competition'],
    ['Polite disk', 'ionice', 'soft, scheduler-dependent'],
    ['Hard CPU cap', 'cgroups (CPUQuota)', 'never more than X%'],
    ['Pause entirely', 'kill -STOP / -CONT', '0% until continued (11.3)'],
    ['Specific CPUs', 'taskset -c', 'affinity'],
    ['Real-time', 'chrt', 'before all normal tasks (root)'],
], minw=420) + qc('top shows PR 39 for a process. What is its nice value?', '19 (PR = 20 + NI).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>nice, renice, ionice, and measuring the effect, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine (2 CPUs) as riya, a normal user. To make processes compete we pin them to CPU 0 with <code>taskset -c 0</code>; otherwise each would get its own CPU and nice would show no effect.</p>
''' + cmdcard_u(['backups, compression, reports, indexing, batch jobs', 'builds while you keep working'],
               ['interactive programs you are using', 'expecting a hard limit'])(
    'nice', 'nice [-n N] cmd · nice (show)', 'start with a nice value',
    '<code>nice -n N cmd</code> runs cmd with niceness = current + N (a normal user may only add). <code>nice cmd</code> without -n adds 10. <code>nice</code> alone prints the current value. Children inherit the value, so a niced script makes all its commands nice.',
    'nice -n 19 ./job.sh   ·   nice ./build.sh   ·   nice', 'safe',
    [('nice', 'show my niceness', 'check'),
     ('nice cmd', '+10', 'quick'),
     ('nice -n 19 cmd', 'most polite', 'batch'),
     ('nice -n 5 cmd', 'slightly polite', 'builds'),
     ('sudo nice -n -5 cmd', 'more important', 'root only'),
     ('nice -n 19 bash script', 'whole script', 'inheritance')],
    dict(setup=CLEAN, cmd="nice\nnice nice\nnice -n 19 nice\nnice -n 5 bash -c 'echo \"inside: $(nice); child: $(nice -n 3 nice)\"'\nnice -n -1 nice 2>&1", expect='any', note='The values add up; children inherit them; a user cannot go below the current value.'),
    [('sys', [
        dict(situation='The real effect: two jobs, one CPU.', setup=CLEAN, cmd=RACE.format(n=19), why='Both want 100% of CPU 0. Weights 1024 : 15, so the nice-19 loop gets only ~1–2%.')]),
     ('data', [
        dict(situation='A smaller difference: nice 5.', setup=CLEAN, cmd=RACE.format(n=5), why='Weights 1024 : 335 ≈ 75% : 25%.')]),
    ],
    anat=anatomy([('nice', 'cmd', 'run politely'), ('-n 19', 'opt', 'add 19'), ('./report.sh', 'arg', 'the command')], 'nice wraps the command; everything it starts inherits the value.')
) + cmdcard_u(['a running job that slows others down', 'all processes of one user'],
               ['lowering values without root', 'renicing system daemons blindly'])(
    'renice', 'renice -n N -p PID · -u user · -g pgrp', 'change a running process',
    '<code>renice -n N -p PID</code> sets the niceness of a running process (in util-linux 2.38+, -n sets the value; older versions treated it as an increment). <code>-u user</code> changes every process of a user, <code>-g</code> a process group. renice prints the old and new value. In top, press <kbd>r</kbd>, the PID and the value.',
    'renice -n 15 -p PID   ·   sudo renice -n 10 -u aman', 'change',
    [('renice -n 15 -p PID', 'one process', 'daily'),
     ('renice -n 19 -p P1 P2', 'several', 'batch'),
     ('sudo renice -n 10 -u aman', 'whole user', 'shared servers'),
     ('renice -n 10 -g PGID', 'a process group (job)', 'pipelines'),
     ('top → r', 'interactive', 'quick'),
     ('sudo renice -n 0 -p PID', 'undo (root)', 'back to normal')],
    dict(setup=CLEAN, cmd="sleep 60 & p=$!\nrenice -n 5 -p $p | sed \"s/$p/PID/\"\nrenice -n 12 -p $p | sed \"s/$p/PID/\"\nps -o ni= -p $p\nrenice -n 3 -p $p 2>&1 | sed \"s/$p/PID/\"; kill $p", expect='any', note='Up is allowed; going back down (12 → 3) is “Permission denied” for a normal user: the puzzle.'),
    [('sys', [
        dict(situation='Renice a running hog while it competes.', setup=CLEAN, cmd="taskset -c 0 timeout 6 sh -c " + LOOP + " & taskset -c 0 timeout 6 sh -c " + LOOP + " & sleep 2\nps -o ni=,%cpu= -u riya -o args= | grep '[w]hile' | grep -v timeout | awk 'NR==1{print \"  before: both loops at nice\", $1}'\nrenice -n 19 -p $(pgrep -n -f '^sh -c while') > /dev/null; sleep 3\nps -o ni=,%cpu=,args= -u riya | grep '[w]hile' | grep -v timeout | awk '{printf \"  after: nice %3s  CPU %5s%% (average since start)\\n\", $1, $2}'; wait", why='Before: 50/50. After renice the reniced loop falls behind (ps %CPU is an average over its lifetime, so it shows the mix).')]),
    ]
) + cmdcard_u(['backups, rsync, tar, database dumps, file indexing'],
               ['expecting effect on every disk scheduler', 'realtime class as a user'])(
    'ionice', 'ionice [-c class] [-n level] cmd · ionice -p PID', 'disk priority',
    '<code>ionice -c3 cmd</code> runs cmd in the idle class: it uses the disk only when nobody else does. <code>-c2 -n7</code> is best-effort, lowest level. <code>ionice -p PID</code> shows a process’s class. Combine with nice for jobs that use both CPU and disk. Check the scheduler with <code>cat /sys/block/DISK/queue/scheduler</code>.',
    'ionice -c3 nice -n 19 tar czf …   ·   ionice -c2 -n7 -p PID', 'safe',
    [('ionice -c3 cmd', 'idle class', 'backups'),
     ('ionice -c2 -n7 cmd', 'lowest best-effort', 'polite'),
     ('ionice -p PID', 'show', 'check'),
     ('ionice -c3 -p PID', 'change running', 'renice for disk'),
     ('ionice -c1', 'realtime (root)', 'rare'),
     ('/sys/block/*/queue/scheduler', 'which scheduler', 'does it apply?')],
    dict(setup=CLEAN, cmd="ionice -p $$\nionice -c3 ionice\nionice -c2 -n7 bash -c 'ionice'\nsleep 30 & p=$!; ionice -c3 -p $p; ionice -p $p; kill $p\nfor d in /sys/block/*/queue/scheduler; do echo \"${d%/queue*}: $(cat $d)\" | sed 's|/sys/block/||'; done | head -3", note='[brackets] mark the active disk scheduler.'),
    [('dba', [
        dict(situation='A polite database dump (simulated with tar).', setup=CLEAN + "; head -c 3000000 /dev/urandom > big.bin", cmd="cd ~/nc; ionice -c3 nice -n 19 tar czf dump.tgz big.bin && [ -s dump.tgz ] && echo 'dump created at nice 19 with idle I/O'", why='Same result, but the job yields CPU and disk to everyone else.')]),
    ]
) + cmdcard_u(['checking priorities when something is slow', 'finding niced or greedy processes'],
               ['reading PRI from different tools as the same number'])(
    'see', 'ps -o pid,ni,pri,cmd · top (NI, PR) · ps -l', 'reading priorities',
    'ps can show NI and several kinds of priority; top shows PR = 20 + NI and NI. Sort by niceness to find processes someone has niced (or made greedy).',
    'ps -eo pid,ni,pri,comm --sort=-ni | head   ·   top -b -n1 | head', 'safe',
    [('ps -o ni,pri', 'nice and priority', 'one process'),
     ('ps -eo ni,comm --sort=ni', 'greediest first', 'audit'),
     ('ps -l', 'PRI NI columns', 'long format'),
     ('top', 'PR NI columns', 'live'),
     ('chrt -p PID', 'scheduling policy', 'real-time?'),
     ('taskset -p PID', 'CPU affinity', 'pinned?')],
    dict(setup=CLEAN, cmd="nice -n 7 sleep 30 & p=$!; sleep 0.2\nps -o pid=,ni=,pri=,comm= -p $p | sed 's/^ *[0-9]*/PID/'\ntop -b -n1 -p $p | tail -1 | awk '{print \"top: PR\", $3, \"NI\", $4}'\nps -eo ni=,comm= --sort=ni | head -3 | sed 's/^ */  /'\nkill $p", note='The same process: ps PRI 12 (19−7), top PR 27 (20+7). Kernel threads with −20 are the greediest.'),
    []
) + undo('Niceness can always be raised; lowering it needs root.', [
    ('Made my job too slow:', 'ask root: <code>sudo renice -n 0 -p PID</code>, or restart it without nice.'),
    ('A user’s jobs hurt the server:', '<code>sudo renice -n 15 -u user</code>; long term: cgroups / systemd slices.'),
    ('Disk still busy:', 'add <code>ionice -c3</code>; check the scheduler.'),
    ('Need a hard limit:', '<code>systemd-run --scope -p CPUQuota=20% cmd</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='renice -n -5 -p $$', meaning='Lower values need root.', fix='sudo, or a limits.conf rule.'),
    dict(cmd='nice -n -5 true', meaning='Warning only: the command still runs at the current value.', fix='sudo nice -n -5 cmd.'),
    dict(cmd='renice -n 5 -p 999999', meaning='No such process.', fix='Find the PID with pgrep.'),
    dict(cmd='ionice -c1 true', meaning='Realtime I/O class needs root.', fix='Use -c2 or -c3.'),
]) + qc('What does <code>nice ./job.sh</code> (without -n) do?', 'Runs it with niceness +10.') + '''
'''
cards = cards + '</section>\n'

def bars(k):
    data = [(50, 50, '0', '0'), (50, 50, '0', '0'), (75, 25, '0', '5'), (98.5, 1.5, '0', '19')][k]
    o = ''
    for i, (pct, ni) in enumerate([(data[0], data[2]), (data[1], data[3])]):
        w = 300 * pct / 100
        o += label_box(20, 30 + i * 60, max(w, 18), 40, [f'{pct:g}%' if w > 40 else ''], 'blue' if i == 0 else 'green', 9)
        o += t(20, 26 + i * 60, f'job {"AB"[i]}  nice {ni}', 8.6, 'ink2', anchor='start')
    return o
see_cmds = [['$ taskset -c 0 ./A &', '$ taskset -c 0 ./B &'], ['$ ps -o ni,%cpu …', ('  0 50.0  A', 'out'), ('  0 50.0  B', 'out')], ['$ renice -n 5 -p B', ('  0 75 · 5 25', 'out')], ['$ renice -n 19 -p B', ('  0 98.5 · 19 1.5', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Two loops, one CPU.', 'Equal nice: equal share.', 'B at nice 5.', 'B at nice 19.'])]
behind = [bars(k) + t(180, 180, n, 8.4, 'violet', bold=True) for k, n in enumerate(['Both runnable on CPU 0.', 'Weights 1024 : 1024.', 'Weights 1024 : 335.', 'Weights 1024 : 15.'])]
two = anim_two('Two jobs, one CPU', 'Behind the screen: CPU shares from weights',
               'A terminal starting two loops on CPU 0 and renicing the second one to 5 and then 19.',
               'Two bars for jobs A and B: 50/50 at equal nice, 75/25 with B at nice 5, about 98.5/1.5 with B at nice 19.', see, behind,
               ['Start.', 'Equal.', 'nice 5.', 'nice 19.'],
               ['start', 'equal', '5', '19'])

def idle(k):
    o = label_box(20, 40, 300 if k == 0 else (300 if k == 2 else 20), 40, ['job B (nice 19): 100%' if k != 1 else ''], 'green', 9)
    if k == 1:
        o += label_box(44, 40, 276, 40, ['web server (nice 0) takes the CPU'], 'blue', 9)
    o += t(180, 130, ['Idle machine: B uses everything.', 'Web traffic arrives: B steps aside.', 'Traffic gone: B is back at 100%.'][k], 9.4, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Nice is a share, not a limit',
              'The same nice-19 job on an idle and on a busy machine.',
              'nice -n 19 ./report.sh', 'One bar: the nice-19 job uses 100% when idle, almost nothing while the web server is busy, and 100% again afterwards.', [idle(k) for k in range(3)],
              ['Idle.', 'Busy.', 'Idle again.'], hid='scenario-share')

dx = dissect('Layer by layer: where the nice value lives',
    'Each layer has a real command and output from our build machine.', [
    dict(key='proc', name='/proc/PID/stat', sub='field 19', why='Kernel’s copy.', how='Read it.', impl='task_struct.', used='ps reads it.',
         cmd="nice -n 6 sleep 5 & sleep 0.1; awk '{print \"nice field:\", $19}' /proc/$!/stat; kill $!"),
    dict(key='sched', name='/proc/PID/sched', sub='weight', why='Shares.', how='se.load.weight.', impl='Shown ×1024 on 64-bit kernels.', used='Debugging.',
         cmd="for n in 0 5 19; do nice -n $n sleep 5 & sleep 0.1; printf 'nice %2s -> weight %s\\n' $n \"$(awk '/se.load.weight/{print $3}' /proc/$!/sched)\"; kill $!; done"),
    dict(key='lim', name='Limits', sub='RLIMIT_NICE', why='Who may lower.', how='ulimit -e.', impl='limits.conf.', used='Audio, DB users.',
         cmd="echo \"ulimit -e (max priority a user may set): $(ulimit -e)\"; echo \"active nice rules in limits.conf: $(grep -v '^#' /etc/security/limits.conf | grep -c nice)\""),
    dict(key='cg', name='cgroups', sub='hard caps', why='Real limits.', how='cpu.max.', impl='cgroup v2.', used='systemd, Docker.',
         cmd="echo \"cgroup file system mounted at /sys/fs/cgroup: $(stat -fc %T /sys/fs/cgroup)\"; echo 'a normal Ubuntu 24.04 machine shows cgroup2fs (v2, with files like cpu.max); our build container shows tmpfs, the older v1 layout'"),
], hint='From the nice field to hard limits. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Two jobs on one CPU, and nice as a share</h2>
''' + two + s1 + dx + qc('Why does the weight table matter more than the nice number?', 'Shares are proportional to weights (1024 for 0, 15 for 19), so one step of nice changes the share by about 25%, and 19 vs 0 is about 68:1.') + '''
</section>
'''

VAR = variations('Fifteen more experiments with nice, renice and ionice. All were really run on our build machine.', [
    ('nice', [
        dict(title='nice values add up to 19 at most', cmd="nice -n 15 nice -n 15 nice", why='The result is capped at 19.'),
        dict(title='A whole script runs nice', setup="cd ~; printf 'echo \"script nice: $(nice)\"\\nsleep 0.1 & echo \"child nice: $(ps -o ni= -p $!)\"\\n' > nscript.sh", cmd="nice -n 9 bash ~/nscript.sh", why='Everything the script starts inherits 9.'),
        dict(title='Nice in a cron line (shown)', cmd="echo '0 1 * * * nice -n 19 ionice -c3 /opt/report/run.sh'", why='The common pattern for nightly jobs (Lesson 17.4).'),
        dict(title='No effect without competition', setup=CLEAN, cmd="timeout 3 nice -n 19 sh -c " + LOOP + " & sleep 2; ps -o ni=,%cpu=,args= -u riya | grep '[w]hile' | grep -v timeout | awk '{print \"  nice\", $1, \"alone: CPU\", $2\"%\"}'; wait", why='Alone on a free CPU, nice 19 still gets ~100%: the first puzzle.'),
        dict(title='Measured shares for 0, 10, 19', setup=CLEAN, cmd="for n in 10 19; do taskset -c 0 timeout 3 sh -c " + LOOP + " & taskset -c 0 nice -n $n timeout 3 sh -c " + LOOP + " & sleep 2.5; ps -o ni=,%cpu=,args= -u riya | grep '[w]hile' | grep -v timeout | awk '{printf \"  nice %2s: %5s%%\\n\", $1, $2}'; wait; done", why='Each extra step of nice shrinks the share by about 1.25×.'),
    ]),
    ('renice', [
        dict(title='Renice several PIDs at once', cmd="sleep 30 & a=$!; sleep 31 & b=$!; renice -n 8 -p $a $b | sed -E 's/[0-9]{3,}/PID/'; kill $a $b", why='One command, several processes.'),
        dict(title='Renice your own user', cmd="sleep 30 & p=$!; renice -n 4 -u riya > /dev/null 2>&1; ps -o ni= -p $p; kill $p", expect='any', why='-u riya changes all of riya’s processes (including this shell).'),
        dict(title='Renice a process group (a whole pipeline)', cmd="set -m; sleep 30 | sleep 31 & sleep 0.2; g=$(ps -o pgid= -p $! | tr -d ' '); renice -n 6 -g $g > /dev/null; ps -o ni= -g $g | sort -u | tr -d ' '; kill %1", why='-g: every process in the job.'),
        dict(title='top’s renice key (batch view)', cmd="nice -n 3 sleep 20 & sleep 0.2; top -b -n1 -p $! | awk 'NR==7{print \"header:\", $3, $4} NR==8{print \"value: \", $3, $4}'; kill $!", why='In interactive top, press r to change it.'),
    ]),
    ('ionice and friends', [
        dict(title='Default I/O class follows nice', cmd="for n in 0 19; do nice -n $n bash -c 'ionice -p $$' | sed \"s/^/nice $n: /\"; done", why='ionice -p shows only a class that was set explicitly (none here); the kernel then derives a best-effort level from the nice value.'),
        dict(title='Idle I/O for a copy', setup=CLEAN + "; head -c 2000000 /dev/urandom > big.bin", cmd="cd ~/nc; ionice -c3 cp big.bin copy.bin && cmp -s big.bin copy.bin && echo 'copied at idle I/O priority'", why='Same result, lower priority.'),
        dict(title='Pin a process to one CPU', cmd="taskset -c 0 sleep 5 & sleep 0.1; taskset -cp $! | sed -E 's/[0-9]{3,}/PID/'; kill $!", why='Affinity: which CPUs it may use.'),
        dict(title='Scheduling policy', cmd="chrt -p $$ | sed -E 's/[0-9]{3,}/PID/'", why='SCHED_OTHER = normal; nice applies only here.'),
        dict(title='A hard limit needs cgroups (shown)', cmd="echo 'systemd-run --user --scope -p CPUQuota=20% ./report.sh   # never more than 20% of one CPU'", why='Nice is soft; CPUQuota is a cap (Lesson 20.3).'),
        dict(title='How many CPUs compete?', cmd="echo \"$(nproc) CPUs; load average: $(cut -d' ' -f1-3 /proc/loadavg | sed 's/[0-9.]*/N/g')\"", why='Competition only starts when runnable tasks > CPUs (Lesson 18.3).'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Priority at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['nice 19', 'backups'], 'blue', 8.6), '1. Nightly backups and reports',
              'Cron lines start with nice -n 19 ionice -c3 so batch work never slows the website.', ['1 a.m.', '*nice + ionice', 'site stays fast']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['renice', 'support'], 'green', 8.6), '2. Firefighting a slow server',
    'A runaway job is reniced to 19 instead of being killed, so the work is not lost.', ['Slow site', '*renice', 'recovered']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-u', 'shared'], 'amber', 8.6), '3. Shared servers and labs',
    'On a teaching or research server, admins renice heavy users’ processes (or use limits.conf).', ['Many users', '*renice -u', 'fair']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['make -j', 'builds'], 'violet', 8.6), '4. Developer builds',
    'nice make -j$(nproc) keeps the desktop responsive during long compiles.', ['Compile', '*nice', 'usable desktop']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Nice=', 'systemd'], 'red', 8.6), '5. Services',
    'systemd units set Nice=, IOSchedulingClass= and CPUWeight= for background services.', ['Unit file', '*Nice=', 'always polite']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='My current niceness', scenario='Check.', cmd="nice", explain='0 by default.'),
    dict(level='b', title='Start politely', scenario='Big job.', cmd="nice -n 19 bash -c 'echo running at nice $(nice)'", explain='nice -n 19.'),
    dict(level='i', title='Show NI for my processes', scenario='Audit.', cmd="nice -n 4 sleep 5 & sleep 0.1; ps -o ni=,comm= -p $!; kill $!", explain='ps -o ni.'),
    dict(level='i', title='Polite CPU and disk', scenario='Backup.', setup=CLEAN, cmd="cd ~/nc; ionice -c3 nice -n 19 tar czf home.tgz -C ~ nc 2>/dev/null; ls home.tgz", explain='Both priorities lowered.'),
    dict(level='a', title='Find greedy processes', scenario='Who has negative nice?', cmd="ps -eo ni=,comm= | awk '$1<0' | sort -n | uniq -c | head -3 | sed -E 's/^ +//'", explain='Kernel threads and some daemons.'),
], extra=build_up('a polite nightly job', 'Riya makes her report job polite step by step.', CLEAN + "; head -c 2000000 /dev/urandom > logs.bin", [
    ("cd ~/nc; tar czf r1.tgz logs.bin && echo 'plain run done'", '1. The plain job.'),
    ("cd ~/nc; nice -n 19 tar czf r2.tgz logs.bin && echo \"CPU-polite run done (nice $(nice -n 19 nice))\"", '2. nice for the CPU.'),
    ("cd ~/nc; ionice -c3 nice -n 19 tar czf r3.tgz logs.bin && echo 'CPU- and disk-polite run done'", '3. ionice for the disk.'),
    ("cd ~/nc; printf '#!/bin/bash\\nexec ionice -c3 nice -n 19 tar czf ~/nc/r4.tgz -C ~/nc logs.bin\\n' > nightly.sh; bash nightly.sh && echo \"cron line: 0 1 * * * $HOME/nc/nightly.sh\" | sed 's|/home/riya|~|'", '4. A wrapper script for cron.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Batch job, polite', 'nice -n 19', 'Free when idle.', 'Running at 0.'),
    ('Running job too greedy', 'renice', 'Work not lost.', 'kill -9.'),
    ('Disk-heavy', 'ionice -c3', 'Disk for others first.', 'nice alone.'),
    ('Hard cap', 'cgroups / systemd CPUQuota', 'Real limit.', 'Hoping nice limits it.'),
    ('Pause completely', 'kill -STOP / -CONT', '0% while paused.', 'Killing.'),
    ('Low latency', 'chrt (root, careful)', 'Real-time.', 'nice −20 everywhere.'),
]) + keys('Handy forms.', [
    ('nice -n 19 cmd', 'start polite', 'batch'),
    ('renice -n 10 -p PID', 'change', 'running'),
    ('ionice -c3 cmd', 'idle disk', 'backups'),
    ('ps -o pid,ni,pri,cmd', 'see values', 'check'),
    ('top → r', 'renice in top', 'interactive'),
    ('taskset -c 0 cmd', 'pin CPU', 'tests'),
]) + scriptit('politeness.sh', 'Report every process of the current user with a non-zero nice value or non-default I/O class, then make all running sleep processes of the user polite (nice 15, idle I/O).',
'''pkill -u "$USER" -x sleep; nice -n 6 sleep 20 & ionice -c3 sleep 21 & sleep 0.2      # demo processes
printf '%4s  %-14s %s\\n' NI IO COMMAND
for p in $(pgrep -u "$USER"); do
  ni=$(ps -o ni= -p "$p" 2>/dev/null | tr -d ' ') || continue
  io=$(ionice -p "$p" 2>/dev/null | cut -d: -f1)
  [ "$ni" != 0 ] || [ "$io" != none ] && [ -n "$ni" ]  && printf '%4s  %-14s %s\\n' "$ni" "$io" "$(ps -o comm= -p "$p")"
done
for p in $(pgrep -u "$USER" -x sleep); do renice -n 15 -p "$p" > /dev/null 2>&1; ionice -c3 -p "$p"; done
echo "sleep processes now: $(ps -o ni= -p "$(pgrep -d, -u "$USER" -x sleep)" | sort -u | tr -d ' \\n' | sed 's/^/nice /')"
pkill -u "$USER" -x sleep''',
'<p>It starts two demo sleep processes first.</p>', expect='any') + puzzle_answer('<b>1.</b> Nice is a share under competition, not a speed limit: on an idle server nothing else wants the CPU, so the nice-19 job correctly gets almost 100% (we measured it). When the web server is busy, the job gets ~1.5%. <b>2.</b> Normal users may only raise niceness; going from 19 back to 5 is lowering it, which needs root (or a <code>nice</code> limit in limits.conf). <b>3.</b> nice is for the CPU scheduler; the tar job was limited by the disk. Use <code>ionice -c3 nice -n 19 tar …</code>, and for real caps use cgroups (systemd IOWeight=, CPUQuota=).') + qc('Which nice value gives a process the smallest CPU share?', '19.') + '''
</section>
'''

_sh.run_sh(CLEAN + '; rm -rf ~/nc ~/nscript.sh', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-watching-processes-ps-pstree-top-and-htop/">Lesson 11.2</a> (ps and top columns) and <a href="../04-foreground-and-background-jobs-and-nohup/">Lesson 11.4</a> (background jobs).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
