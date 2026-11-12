import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='11-processes', lesson='05-process-priority-nice-renice-and-a-look', n='11.5',
    module_label='Module 11 · Processes',
    title='Process priority: nice, renice and ionice (and a look at cgroups, chrt and taskset)',
    desc='Linux process priority from zero: nice values −20 to 19, NI vs PRI vs PR in ps and top, nice -n, renice -n -p -u -g, who may raise or lower niceness, scheduler weights (1024 vs 15) with measured CPU shares, ionice classes realtime/best-effort/idle, disk schedulers, and when to use cgroups CPUQuota, chrt or taskset; real outputs and 30+ examples.',
    og_desc='nice, renice and ionice explained with measured CPU shares: nice values, priorities, permissions and hard limits.',
    minutes=35, level='Beginner → Advanced',
    lead='Make heavy jobs polite instead of killing them: nice values, renice on running processes, ionice for disks, and the measured effect when two jobs compete for one CPU.',
    chips=['Measured CPU shares', 'Two jobs, one CPU animated', 'nice vs hard limits', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# nice values in practice
echo "my niceness: $(nice)"
nice -n 10 bash -c 'echo "inside nice -n 10: $(nice)"'
sleep 30 &
p=$!
renice -n 15 -p $p
ps -o pid,ni,comm -p $p
kill $p
"""

RUN = dict(
    heading='Start nicely, renice, check',
    intro='<p>Show your niceness, start a command with nice, renice a background job and check it with ps.</p>',
    code=MAIN,
    anno=[('renice -n 15 -p $p', 'Raise the niceness of a running process.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which column shows the nice value?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the three lines print?',
             code="nice\nnice nice\nnice -n 5 nice -n 5 nice\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> a normal user cannot lower niceness. Use a positive value.',
             code="sleep 20 &\nrenice -n -5 -p $! 2>&1\nrenice -n 5 -p $!\nkill %1\n", expect='any'),
        dict(label='4 · Your turn', hint='Start sleep with nice 19 and print its NI.',
             code="nice -n 19 sleep 10 &\nps -o ni= -p $!\nkill $!\n"),
        dict(label='5 · Challenge', hint='Show the I/O class of a command started with ionice -c3.',
             code="ionice -c3 bash -c 'ionice -p $$'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: watch it in top',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Two loops on one CPU', cmd="taskset -c 0 sh -c 'while :; do :; done' & taskset -c 0 nice -n 19 sh -c 'while :; do :; done' & top", output='  PID USER  PR  NI  %CPU COMMAND\n 5120 you   20   0  97.7 sh\n 5121 you   39  19   1.3 sh', note='Typical (our measured values: 97.3% vs 1.3%). Press q, then: kill %1 %2'),
        dict(title='2 · Renice from top', cmd='top   # press r, type the PID, Enter, type 10, Enter', output='PID to renice [default pid = 5120] 5121\nRenice PID 5121 to value 10', note='Typical.'),
        dict(title='3 · Disk scheduler', cmd='cat /sys/block/sda/queue/scheduler', output='none [mq-deadline] bfq', note='Typical; ionice works best with bfq.'),
        dict(title='4 · util-linux version', cmd='renice --version', output=pc('renice --version'), note='Recorded. Since 2.38, -n sets an absolute value.'),
    ],
)

TRACE = dict(
    heading='Niceness, line by line',
    intro='<p>Step through: read, add, inherit.</p>',
    code='''base=$(nice)
plus=$(nice -n 7 nice)
twice=$(nice -n 7 nice -n 7 nice)
capped=$(nice -n 15 nice -n 15 nice)
echo "base=$base plus=$plus twice=$twice capped=$capped"
''',
    notes={1: '0 by default.', 2: '0 + 7.', 3: '7 + 7.', 4: 'Capped at 19.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a nice audit, a polite wrapper and a guard for production.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='List my niced processes',
         problem='<p>Start two processes with different nice values and list every process of mine whose NI is not 0.</p>',
         inp='processes', approach=['ps -o ni.', 'awk filter.'],
         code='''nice -n 5 sleep 20 &
nice -n 15 sleep 21 &
sleep 0.2
ps -u "$USER" -o pid=,ni=,comm= | awk '$2 != 0 {print "NI", $2, $3}'
kill %1 %2
''', notes={4: 'Skip the normal ones.'}, tryit='Sort by NI, highest first.'),
    dict(level='i', tag='DevOps', title='A polite wrapper',
         problem='<p>Write a function polite() that runs any command at nice 19 and idle I/O, and prints the values it got.</p>',
         inp='a command', approach=['nice + ionice.', '"$@".'],
         code='''polite(){ ionice -c3 nice -n 19 "$@"; }
polite bash -c 'echo "nice=$(nice) io=$(ionice -p $$)"'
''', notes={1: 'Passes all arguments on.'}, tryit='Add a log line with the start time.'),
    dict(level='a', tag='SRE', title='Refuse to run greedy',
         problem='<p>A batch script must not run at nice below 10. If it does, renice itself.</p>',
         inp='nothing', approach=['$(nice).', 'renice $$.'],
         code='''cur=$(nice)
if (( cur < 10 )); then
  renice -n 10 -p $$ > /dev/null
  echo "was nice $cur, reniced myself to $(nice)"
fi
echo "batch work runs at nice $(nice)"
''', notes={3: '$$ = this script.'}, tryit='Also set ionice -c3 for $$.'),
]

QUIZ = mix([
    dict(q='The nice range is…', options=['0 to 100', '−20 to 19', '1 to 10', '−19 to 20'], answer=1, why='−20 … 19.'),
    dict(q='Default nice value?', options=['10', '0', '19', '−20'], answer=1, why='0.'),
    dict(q='Which gets the smallest CPU share?', options=['−20', '0', '10', '19'], answer=3, why='19.'),
    dict(q='A normal user may…', options=['set −5', 'only raise niceness', 'lower to 0 after raising', 'set any value'], answer=1, why='Only up.'),
    dict(q='nice cmd without -n adds…', options=['1', '5', '10', '19'], answer=2, why='10.'),
    dict(q='On an idle machine a nice-19 CPU job uses…', options=['~1%', '~50%', '~100%', '0%'], answer=2, why='No competition.'),
    dict(q='Disk-heavy job, polite:', options=['nice -n 19', 'ionice -c3', 'renice -20', 'taskset'], answer=1, why='ionice.'),
    dict(q='top shows PR 30. NI is…', options=['30', '10', '−10', '0'], answer=1, why='PR = 20 + NI.'),
])

REVISION = [
    'Nice −20 (greedy) … 19 (polite); default 0; children inherit; nice alone shows it.',
    'nice -n N cmd starts with +N (nice cmd = +10); renice -n N -p PID / -u user / -g group changes it.',
    'Users: only up, never back down; root: both. ps NI/PRI, top PR = 20 + NI.',
    'Nice is a share under competition (weights 1024 vs 15), not a cap.',
    'ionice -c3 idle, -c2 -n0..7 best-effort, -c1 realtime (root); combine with nice for backups.',
    'Hard caps: cgroups (systemd CPUQuota=); pin CPUs: taskset; real-time: chrt.',
]

FAQ = [
    ('What is the nice value in Linux?', 'A number from −20 to 19 that sets a process’s share of CPU time under competition; higher is more polite.'),
    ('How do I run a command with low priority?', 'nice -n 19 command; for disk, add ionice -c3.'),
    ('How do I change the priority of a running process?', 'renice -n VALUE -p PID (raising is allowed for users; lowering needs root).'),
    ('What is the difference between PR and NI in top?', 'NI is the nice value; PR is the kernel priority, 20 + NI for normal tasks.'),
    ('Why does nice not slow down my program?', 'Nice only matters when processes compete for the CPU; on an idle machine the job still gets full speed.'),
    ('What does ionice do?', 'Sets the I/O scheduling class (realtime, best-effort, idle) for disk access.'),
    ('How do I limit a process to 20% CPU?', 'Use cgroups, for example systemd-run --scope -p CPUQuota=20% command.'),
]

PRACTICE_INTRO = 'Small priority tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Current', stmt='Print your niceness.', inp='nothing', code="nice\n", explain='0.'),
    dict(level='easy', title='Add 10', stmt='Print the niceness inside nice without -n.', inp='nothing', code="nice nice\n", explain='10.'),
    dict(level='easy', title='Most polite', stmt='Print the niceness inside nice -n 19.', inp='nothing', code="nice -n 19 nice\n", explain='19.'),
    dict(level='medium', title='Cap', stmt='Print niceness after nice -n 12 twice.', inp='nothing', code="nice -n 12 nice -n 12 nice\n", explain='19 (capped).'),
    dict(level='medium', title='Renice', stmt='Start sleep 10, renice it to 7, print its NI.', inp='nothing', code="sleep 10 & renice -n 7 -p $! > /dev/null; ps -o ni= -p $! | tr -d ' '; kill $!\n", explain='7.'),
    dict(level='medium', title='PR', stmt='Compute top’s PR for nice 13.', inp='13', code="echo $((20 + 13))\n", explain='33.'),
    dict(level='business', title='I/O class', stmt='Print the I/O class inside ionice -c3.', inp='nothing', code="ionice -c3 bash -c 'ionice -p $$'\n", explain='idle.'),
    dict(level='business', title='Wrapper', stmt='Run echo ok with nice 19 and idle I/O.', inp='nothing', code="ionice -c3 nice -n 19 echo ok\n", explain='ok.'),
]

SCN_INTRO = 'Interview questions about process priority, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is nice and renice?”', 'Very common.', 'range?',
        '''<ul>
          <li>Nice −20 … 19, default 0; higher = lower priority.</li>
          <li>nice -n 19 cmd starts; renice -n 10 -p PID changes.</li>
          <li>Only root can set negative values.</li>
        </ul>''', 'mixing up which way is “higher priority”.') +
    scn('Service company', 'Junior', 'Nightly job slows the website', 'Users complain at 1 a.m.', 'fix without stopping it?',
        '''<ol>
          <li>nice -n 19 and ionice -c3 in the cron line.</li>
          <li>renice the running job now.</li>
          <li>If still too much: a systemd unit with CPUQuota.</li>
        </ol>''', 'moving it to the afternoon.') +
    scn('Product company', 'Mid-level', '“I set nice 19 but it still uses 100% CPU”', 'Idle machine.', 'is it broken?',
        '''<ul>
          <li>No: nice is a share; with no competition it gets everything.</li>
          <li>Show with taskset two loops on one CPU.</li>
          <li>For a cap use cgroups.</li>
        </ul>''', 'agreeing that nice is broken.') +
    scn('Platform', 'Senior', 'Noisy neighbour on a shared build server', 'One team’s builds starve others.', 'design?',
        '''<ul>
          <li>systemd slices per team with CPUWeight and CPUQuota.</li>
          <li>IOWeight for disks; nice inside the slices.</li>
          <li>Monitor with systemd-cgtop.</li>
        </ul>''', 'renicing by hand every day.')
) + interview([
    ('Who can lower niceness?', 'root (or users allowed by limits.conf).'),
    ('Do children inherit niceness?', 'Yes.'),
    ('What does ionice -c3 mean?', 'Idle I/O class.'),
    ('What is PR in top?', '20 + NI for normal tasks.'),
    ('Nice vs cgroups?', 'Nice is a soft share; cgroups can cap.'),
    ('What is chrt?', 'Sets real-time scheduling policies.'),
    ('What does taskset do?', 'Sets CPU affinity.'),
], [
    ('RHCSA (EX200)', 'Adjust process scheduling (nice/renice).'),
    ('LFCS', 'Manage process priorities.'),
    ('CompTIA Linux+', 'nice, renice, ionice.'),
]) + distro('nice and renice work everywhere; ionice and systemd limits are Linux-specific.', [
    ('nice / renice', 'coreutils / util-linux', 'same', 'BSD versions', '-'),
    ('ionice', 'util-linux', 'util-linux', 'no', '-'),
    ('Default I/O scheduler', 'mq-deadline / none', 'mq-deadline / bfq', '-', '-'),
    ('Hard limits', 'systemd / cgroups v2', 'same', 'no cgroups', 'Job Objects'),
    ('Windows', '-', '-', '-', 'start /low, Task Manager priority'),
]) + teaser('11.6', 'Riya’s nice-19 job runs for six hours, but her SSH session drops after one. nohup keeps it alive, but she cannot watch it or type into it. Next: tmux and screen, terminal sessions that survive logout and can be reattached.')

CHEATSHEET = cheatsheet('Priority', [
    ('nice', [('nice', 'show'), ('nice cmd', '+10'), ('nice -n 19 cmd', 'polite'), ('sudo nice -n -5 cmd', 'greedy')]),
    ('renice', [('renice -n 10 -p PID', 'process'), ('-u user', 'user'), ('-g PGID', 'group'), ('top → r', 'interactive')]),
    ('ionice', [('ionice -c3 cmd', 'idle'), ('-c2 -n7', 'low best-effort'), ('-p PID', 'show'), ('-c1', 'realtime (root)')]),
    ('Read', [('ps -o ni,pri', 'values'), ('top PR = 20+NI', 'kernel prio'), ('CPUQuota=', 'hard cap'), ('taskset -c', 'CPUs')]),
])

MINDMAP = mindmap('Priority', [
    ('Nice', 'blue', ['−20 … 19', 'default 0', 'inherited']),
    ('Commands', 'green', ['nice -n', 'renice -p', 'renice -u']),
    ('Rules', 'red', ['users: up only', 'root: both', 'limits.conf']),
    ('Effect', 'amber', ['share, not cap', 'weights', 'competition']),
    ('Disk', 'violet', ['ionice -c3', 'best-effort', 'scheduler']),
    ('Beyond', 'acc', ['cgroups', 'chrt', 'taskset']),
])

LAB = lab('make jobs polite', 'Build the lab (it starts two processes), do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab115 && cd ~/lab115 && rm -f *.txt
pkill -u "$USER" -f 'lab115-'; true
(exec -a lab115-report sleep 600 &)
(exec -a lab115-backup sleep 601 &)
sleep 0.5''',
    tasks=['Renice the process <code>lab115-report</code> to nice value 15.',
           'Put the process <code>lab115-backup</code> into the idle I/O class and nice value 19.',
           'Write the niceness you get inside <code>nice -n 4 nice -n 4</code> into <code>nested.txt</code> (use the command, do not type the number).',
           'Write the PR value top would show for nice 15 into <code>pr.txt</code>.'],
    solution='''renice -n 15 -p $(pgrep -f lab115-report)
renice -n 19 -p $(pgrep -f lab115-backup); ionice -c3 -p $(pgrep -f lab115-backup)
nice -n 4 nice -n 4 nice > ~/lab115/nested.txt
echo $((20 + 15)) > ~/lab115/pr.txt''',
    check='''cd ~/lab115
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
r=$(pgrep -f lab115-report); b=$(pgrep -f lab115-backup)
ok "1 report" '[ -n "$r" ] && [ "$(ps -o ni= -p $r | tr -d " ")" = 15 ]'
ok "2 backup" '[ -n "$b" ] && [ "$(ps -o ni= -p $b | tr -d " ")" = 19 ] && [ "$(ionice -p $b)" = idle ]'
ok "3 nested" '[ "$(cat nested.txt 2>/dev/null)" = 8 ]'
ok "4 pr"     '[ "$(cat pr.txt 2>/dev/null)" = 35 ]' ''')
