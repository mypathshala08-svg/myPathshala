import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='13-one-liners', lesson='04-server-admin-one-liners-biggest-files-who-uses', n='13.4',
    module_label='Module 13 · Power one-liners and command combos',
    title='Server admin one-liners: biggest files, who uses a port, CPU and memory hogs',
    desc='Everyday server admin one-liners: df -h and df -i, du drill-down with sort -h, find -size for big and old files, deleted-but-open files with lsof +L1 and truncating via /proc, who uses a port or file with ss -ltnp, lsof -i, fuser, CPU and memory hogs with ps --sort, top -b, free and load average, who/w/last, and a reusable health check; real outputs and 35+ examples.',
    og_desc='Admin one-liners with real runs: what fills the disk, deleted-but-open files, who uses a port, and CPU and memory hogs.',
    minutes=40, level='Beginner → Advanced',
    lead='Three classic tickets, answered with one-liners: the disk is full, the port is taken, something eats CPU or memory. Measure, rank biggest first, find the owner, then act.',
    chips=['Disk drill-down animated', 'Deleted-but-open trap', 'Port owner in seconds', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Make a small folder tree with big and small files
mkdir -p data/videos data/backups data/cache
head -c 3000000 /dev/zero > data/videos/talk.mp4
head -c 1500000 /dev/zero > data/backups/db.sql.gz
for i in 1 2 3 4 5; do head -c 2000 /dev/zero > data/cache/t$i.jpg; done

echo "== biggest folders =="; du -sh data/* | sort -rh
echo "== biggest files ==";   find data -type f -size +1M -exec ls -lh {} + | awk '{print $5, $NF}'
echo "== memory hogs ==";     ps -eo rss,comm --sort=-rss | head -3
"""

RUN = dict(
    heading='Biggest folders, biggest files, memory hogs',
    intro='<p>Build a small tree, rank folders and files biggest first, and rank processes by memory.</p>',
    code=MAIN,
    anno=[('du -sh data/* | sort -rh', 'Folder totals, biggest first (sort -h understands K/M/G).')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which folder is biggest?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which order does sort -rh give?',
             code="printf '%s\\n' '900K a' '1.5M b' '20K c' '2G d' | sort -rh\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> sort -rn puts 900K above 2G. Use -h.',
             code="printf '%s\\n' '900K a' '2G d' | sort -rn\n"),
        dict(label='4 · Your turn', hint='Show disk use of the current file system in percent only.',
             code="df --output=pcent . | tail -1\n"),
        dict(label='5 · Challenge', hint='Count files per folder (inode hunting).',
             code="mkdir -p x/a x/b; touch x/a/{1..20} x/b/{1..3}\nfind x -type f -printf '%h\\n' | sort | uniq -c | sort -rn\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: ports and system-wide views',
    intro='<p>Our build machine has no <code>ss</code>, so these are <b>typical</b> outputs from a normal Ubuntu machine unless marked recorded.</p>',
    items=[
        dict(title='1 · Who listens on which port', cmd='sudo ss -ltnp', output='State  Recv-Q Send-Q Local Address:Port Peer Address:Port Process\nLISTEN 0      511          0.0.0.0:80        0.0.0.0:*     users:(("nginx",pid=812,fd=6))\nLISTEN 0      128          0.0.0.0:22        0.0.0.0:*     users:(("sshd",pid=701,fd=3))', note='Typical.'),
        dict(title='2 · Port 80 only', cmd="sudo ss -ltnp 'sport = :80'", output='LISTEN 0 511 0.0.0.0:80 0.0.0.0:* users:(("nginx",pid=812,fd=6))', note='Typical: ss has its own filter language.'),
        dict(title='3 · Biggest folders of the whole system', cmd='sudo du -xh --max-depth=1 / 2>/dev/null | sort -rh | head', output='9.8G\t/\n5.1G\t/usr\n2.3G\t/var\n1.4G\t/home', note='Typical.'),
        dict(title='4 · lsof version', cmd='lsof -v 2>&1 | grep -m1 revision', output=pc("lsof -v 2>&1 | grep -m1 revision"), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A disk alert, line by line',
    intro='<p>Step through: read the percentage, compare, decide.</p>',
    code='''used=$(df --output=pcent . | tail -1 | tr -d ' %')
limit=90
state=ok
[ "$used" -ge "$limit" ] && state=ALERT
echo "disk ${used}% used: $state"
''',
    notes={1: 'Only the number.', 4: 'ALERT only at 90% or more.'},
)

WORKED_INTRO = 'Three admin tasks from real jobs: a disk report, a port check before a deploy and a memory report.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Top 3 folders and files',
         problem='<p>Print the three biggest folders and the three biggest files under a tree.</p>',
         inp='a folder tree', approach=['du -s | sort -rh.', 'find -printf %s | sort -rn.'],
         code='''mkdir -p t/a t/b t/c; head -c 300000 /dev/zero > t/a/big; head -c 50000 /dev/zero > t/b/mid; head -c 900 /dev/zero > t/c/small
echo "folders:"; du -sh t/* | sort -rh | head -3
echo "files:"; find t -type f -printf '%s %p\\n' | sort -rn | head -3
''', notes={3: 'Bytes, biggest first.'}, tryit='Show sizes in KB with awk.'),
    dict(level='i', tag='DevOps', title='Is the port free before a deploy?',
         problem='<p>Before starting an app on port 8080, check whether something already listens there and stop the deploy if so.</p>',
         inp='a port', approach=['/dev/tcp test.', 'exit code.'],
         code='''port=8080
if (exec 3<>/dev/tcp/127.0.0.1/$port) 2>/dev/null; then
  echo "port $port is busy: deploy stopped"; exit 1
else
  echo "port $port is free: starting app"
fi
''', notes={2: 'Try to connect; success means something listens.'}, tryit='Start a listener first and run it again.'),
    dict(level='a', tag='SRE', title='Memory by program, in MB',
         problem='<p>Sum resident memory per program name and show the top 3.</p>',
         inp='ps output', approach=['ps -eo rss,comm.', 'awk array.'],
         code='''ps -eo rss=,comm= | awk '{m[$2]+=$1} END{for(c in m) printf "%8.1f MB  %s\\n", m[c]/1024, c}' | sort -rn | head -3
''', notes={1: 'One pass, grouped by name.'}, tryit='Add the number of processes per program.'),
]

QUIZ = mix([
    dict(q='Which disk is full?', options=['du -sh', 'df -h', 'ls -lh', 'free'], answer=1, why='df per file system.'),
    dict(q='Biggest folders first:', options=['du -sh * | sort -rh', 'du -sh * | sort', 'ls -S', 'df -h | sort'], answer=0, why='-h understands K/M/G.'),
    dict(q='df full, du small, after rm of a log. Check:', options=['df -i', 'lsof +L1', 'free', 'ls -a'], answer=1, why='Deleted but open.'),
    dict(q='“No space left” at 40% used. Check:', options=['df -i', 'du -sh', 'top', 'lsof -i'], answer=0, why='Inodes.'),
    dict(q='Who uses port 8080?', options=['sudo ss -ltnp | grep :8080', 'df 8080', 'ps 8080', 'kill 8080'], answer=0, why='Or lsof -i :8080.'),
    dict(q='Real memory of a process:', options=['VSZ', 'RSS', '%CPU', 'STAT'], answer=1, why='Resident.'),
    dict(q='Safe way to empty a log a service writes:', options=['rm it', ': > file', 'mv it', 'chmod 000'], answer=1, why='Truncate.'),
    dict(q='Memory really available:', options=['free “free”', 'free “available”', 'VSZ', 'df'], answer=1, why='Includes reclaimable cache.'),
])

REVISION = [
    'Disk: df -h (which), du -xh -d1 | sort -rh (where), find -size / -mtime (which files); df -i for inodes.',
    'df ≠ du: deleted-but-open files (lsof +L1; reload or : > /proc/PID/fd/N) or files under a mount point.',
    'Ports: sudo ss -ltnp | grep :P, sudo lsof -i :P (-t PID only), fuser P/tcp; check what it is before stopping.',
    'Files busy: fuser -v FILE, fuser -vm MOUNT, lsof FILE / +D DIR.',
    'Hogs: ps -eo pid,%cpu,%mem,rss,cmd --sort=-%cpu or -rss | head; top -b -n1; free -h “available”; load vs nproc.',
    'People: who, w, last. Habit: look → identify → act; truncate logs instead of rm.',
]

FAQ = [
    ('How do I find what is using disk space in Linux?', 'df -h for the disk, then du -xh --max-depth=1 DIR | sort -rh | head, repeat on the biggest folder; find -size +100M for big files.'),
    ('Why is my disk still full after deleting files?', 'A process still has the deleted file open; check sudo lsof +L1 and restart or reload it.'),
    ('Why do I get "No space left on device" when df shows free space?', 'You ran out of inodes (df -i) or hit the reserved-blocks limit.'),
    ('How do I find which process uses a port?', 'sudo ss -ltnp | grep :PORT, or sudo lsof -i :PORT, or sudo fuser PORT/tcp.'),
    ('How do I find the top memory-consuming processes?', 'ps -eo pid,rss,%mem,cmd --sort=-rss | head, or top sorted by %MEM.'),
    ('What is the difference between RSS and VSZ?', 'RSS is memory actually in RAM; VSZ is the whole address space, mostly unused.'),
    ('Why is ss missing?', 'It is in the iproute2 package; install it or use lsof -i / netstat.'),
]

PRACTICE_INTRO = 'Small admin tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Percent used', stmt='Print only the used percentage of the current file system.', inp='nothing', code="df --output=pcent . | tail -1 | tr -d ' '\n", explain='e.g. 29%.'),
    dict(level='easy', title='Folder size', stmt='Create a 100 KB file in d and print the size of d.', inp='nothing', code="mkdir -p d; head -c 100000 /dev/zero > d/f; du -sh d | cut -f1\n", explain='About 100K.'),
    dict(level='easy', title='Sort sizes', stmt='Sort 3M, 20K, 1G biggest first.', inp='sizes', code="printf '%s\\n' 3M 20K 1G | sort -rh\n", explain='1G, 3M, 20K.'),
    dict(level='medium', title='Big files', stmt='Create a 2 MB and a 1 KB file; list only files over 1 MB.', inp='nothing', code="head -c 2000000 /dev/zero > big; head -c 1000 /dev/zero > small; find . -maxdepth 1 -type f -size +1M\n", explain='./big.'),
    dict(level='medium', title='Files per folder', stmt='Count files in folders a (5 files) and b (2 files).', inp='nothing', code="mkdir -p a b; touch a/{1..5} b/{1..2}; for d in a b; do echo \"$d $(ls $d | wc -l)\"; done\n", explain='a 5, b 2.'),
    dict(level='medium', title='Top process', stmt='Print the name of the process using the most memory.', inp='nothing', code="ps -eo rss=,comm= --sort=-rss | head -1 | awk '{print $2}'\n", explain='Depends on the machine.'),
    dict(level='business', title='Alert', stmt='Print ALERT if the file system is at least 1% used, else ok (a test that always alerts).', inp='nothing', code="u=$(df --output=pcent . | tail -1 | tr -d ' %'); [ \"$u\" -ge 1 ] && echo ALERT || echo ok\n", explain='ALERT.'),
    dict(level='business', title='Port free?', stmt='Report whether TCP port 1 on localhost accepts connections.', inp='nothing', code="(exec 3<>/dev/tcp/127.0.0.1/1) 2>/dev/null && echo open || echo closed\n", explain='closed.'),
]

SCN_INTRO = 'Interview questions about admin one-liners, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“The disk is full. What do you do?”', 'The classic.', 'steps?',
        '''<ul>
          <li>df -h: which file system.</li>
          <li>du -xh --max-depth=1 /var | sort -rh | head, drill down.</li>
          <li>Archive or rotate, do not blindly delete.</li>
        </ul>''', 'rm -rf /var/log/*.') +
    scn('Service company', 'Junior', '“I deleted the log but space did not come back”', 'df unchanged.', 'why?',
        '''<ol>
          <li>The service still has the file open.</li>
          <li>sudo lsof +L1 shows it.</li>
          <li>systemctl reload/restart, or truncate via /proc/PID/fd.</li>
        </ol>''', 'deleting more files.') +
    scn('Product company', 'Mid-level', '“Address already in use” on deploy', 'Port 8080.', 'how?',
        '''<ul>
          <li>sudo ss -ltnp | grep :8080 → PID.</li>
          <li>ps -fp PID / systemctl status: what is it?</li>
          <li>Stop the old instance cleanly; fix the deploy script to wait for it.</li>
        </ul>''', 'kill -9 the PID blindly.') +
    scn('Platform', 'Senior', '“No space” but df shows 40%', 'Mail server.', 'cause?',
        '''<ul>
          <li>df -i: inodes at 100%.</li>
          <li>find -printf %h | sort | uniq -c to find the folder with millions of files.</li>
          <li>Clean the queue; long term: monitor inodes too.</li>
        </ul>''', 'adding a bigger disk.')
) + interview([
    ('df vs du?', 'File system view vs file view.'),
    ('What does lsof +L1 show?', 'Open files with link count below 1: deleted but open.'),
    ('How to free space from such a file without restart?', ': > /proc/PID/fd/N.'),
    ('What is an inode?', 'The record of one file; a fixed number per file system.'),
    ('RSS vs VSZ?', 'RAM used vs address space.'),
    ('How to see what is listening?', 'ss -ltnp (or netstat -ltnp).'),
    ('What does fuser -vm /mnt do?', 'Lists processes using a mount point.'),
], [
    ('RHCSA (EX200)', 'Identify CPU/memory intensive processes; manage disks.'),
    ('LFCS', 'Monitor disk, processes and network services.'),
    ('CompTIA Linux+', 'df, du, lsof, ss, ps.'),
]) + distro('The tools are the same; packages differ slightly.', [
    ('ss / ip', 'iproute2', 'iproute', 'not available (netstat, lsof)', '-'),
    ('netstat', 'net-tools (old)', 'net-tools', 'netstat (BSD)', 'netstat -ano'),
    ('lsof / fuser', 'lsof / psmisc', 'lsof / psmisc', 'lsof built in', 'Resource Monitor'),
    ('ncdu', 'apt install ncdu', 'dnf install ncdu', 'brew', '-'),
    ('du -x / sort -h', 'GNU', 'GNU', 'du -x; gsort -h', '-'),
]) + teaser('13.5', 'Riya’s manager sends a CSV of 50,000 sales and asks for totals per city, the top products and a join with the price list, plus a JSON export from an API. Next: data one-liners with cut, awk, sort, join and jq.')

CHEATSHEET = cheatsheet('Admin one-liners', [
    ('Disk', [('df -h / df -i', 'blocks / inodes'), ('du -xh -d1 D | sort -rh', 'drill down'), ('find / -xdev -size +500M', 'big files'), ('lsof +L1', 'deleted but open')]),
    ('Ports / files', [('ss -ltnp', 'listeners'), ('lsof -i :P', 'port owner'), ('fuser P/tcp', 'PID'), ('fuser -vm /mnt', 'busy mount')]),
    ('CPU / memory', [('ps … --sort=-%cpu', 'CPU'), ('ps … --sort=-rss', 'memory'), ('top -b -n1', 'snapshot'), ('free -h', 'available')]),
    ('People / fix', [('who / w', 'logged in'), ('last -n 10', 'history'), (': > file', 'truncate'), ('systemctl reload', 'reopen logs')]),
])

MINDMAP = mindmap('Admin', [
    ('Disk', 'blue', ['df -h', 'du | sort -rh', 'find -size']),
    ('Traps', 'red', ['lsof +L1', 'df -i', 'mounts']),
    ('Ports', 'amber', ['ss -ltnp', 'lsof -i', 'fuser']),
    ('CPU', 'green', ['ps --sort', 'top', 'load']),
    ('Memory', 'violet', ['RSS', 'free', 'OOM']),
    ('Habit', 'acc', ['look', 'identify', 'act']),
])

LAB = lab('fix the tickets', 'Build the lab (it creates files and starts a process), do the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab134 && cd ~/lab134 && rm -rf srv archive *.txt .pid; pkill -u "$USER" -f lab134-; true
mkdir -p srv/{media,db,tmp}; head -c 5M /dev/zero > srv/media/intro.mp4; head -c 2M /dev/zero > srv/db/dump.sql
head -c 8M /dev/zero > srv/tmp/core.1234; touch -d '100 days ago' srv/tmp/core.1234
(setsid bash -c 'exec -a lab134-server python3 -m http.server 8134 --bind 127.0.0.1' > /dev/null 2>&1 &); sleep 1; lsof -t -i :8134 > .pid''',
    tasks=['Write the name of the biggest folder directly inside <code>srv</code> (just the name, e.g. <code>media</code>) into <code>bigdir.txt</code>.',
           'Move every file under <code>srv</code> that is bigger than 4 MB <b>and</b> older than 30 days into <code>~/lab134/archive/</code>.',
           'Write the PID of the process listening on port 8134 into <code>port.txt</code>.',
           'Stop that process with SIGTERM, so that port 8134 is free.'],
    solution='''cd ~/lab134
du -s srv/* | sort -rn | head -1 | awk '{print $2}' | xargs basename > bigdir.txt
mkdir -p archive; find srv -type f -size +4M -mtime +30 -exec mv -t archive/ {} +
lsof -t -i :8134 > port.txt
kill "$(cat port.txt)"''',
    check='''cd ~/lab134; sleep 0.5
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 bigdir"  '[ "$(cat bigdir.txt 2>/dev/null)" = tmp ]'
ok "2 archive" '[ -f archive/core.1234 ] && [ ! -e srv/tmp/core.1234 ] && [ -f srv/media/intro.mp4 ]'
ok "3 port"    '[ -s port.txt ] && [ "$(cat port.txt)" = "$(cat .pid)" ]'
ok "4 stopped" '! lsof -t -i :8134 > /dev/null 2>&1' ''')
