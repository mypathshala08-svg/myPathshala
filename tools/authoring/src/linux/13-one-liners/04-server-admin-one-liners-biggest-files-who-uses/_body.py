import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

KILL = "pkill -u riya -f 'http.server|hog_|holder'; pkill -u riya -x yes; true"
DISK = r"""pkill -u riya -f 'http.server|hog_|holder'; rm -rf ~/ad; mkdir -p ~/ad/data/{videos,backups,logs,cache/thumbs} ~/ad/app; cd ~/ad
head -c 30M /dev/zero > data/videos/demo.mp4; head -c 12M /dev/zero > data/backups/db-2026-11-01.sql.gz
head -c 9M /dev/zero > data/backups/db-2026-11-10.sql.gz; head -c 4M /dev/zero > data/logs/app.log
for i in $(seq 1 300); do head -c 2k /dev/zero > data/cache/thumbs/t$i.jpg; done
head -c 1M /dev/zero > app/server.bin; touch -d '200 days ago' data/backups/db-2026-11-01.sql.gz"""
PROCS = r"""pkill -u riya -f 'http.server|hog_|holder'; pkill -u riya -x yes; rm -rf ~/ad; mkdir -p ~/ad; cd ~/ad
(setsid timeout 120 python3 -m http.server 8099 --bind 127.0.0.1 > /dev/null 2>&1 &)
(setsid timeout 120 bash -c 'exec -a hog_cpu yes' > /dev/null 2>&1 &)
(setsid timeout 120 python3 -c 'import sys; sys.argv[0]="hog_mem"; a = bytearray(120*1024*1024); import time; time.sleep(120)' > /dev/null 2>&1 &)
sleep 1.5"""
ME = "grep -v -E ' (ps|grep|sort|head|awk|sed|bash --norc|timeout|tail|cut)( |$)'"

HOOK = hook('Monday, 9:05 a.m. Three tickets land at once. “Disk 97% full on web01.” “The app won’t start: port 8080 already in use.” “Server feels slow, something is eating memory.” Riya has no fancy dashboards on this box, just SSH. Each ticket is answered by one or two classic admin one-liners: <code>du</code> and <code>find</code> for the biggest files, <code>lsof</code>, <code>fuser</code> and <code>ss</code> for who holds a port, <code>ps --sort</code> and <code>top</code> for CPU and memory hogs, <code>df -i</code> and <code>lsof +L1</code> for the two disk-full traps that fool beginners. This lesson collects them, runs each on a real machine and explains every column.',
    ['find what fills a disk with df, du -sh | sort -h and find -size, including inode exhaustion and deleted-but-open files',
     'find which process uses a port or a file with lsof, fuser and ss, and stop it safely',
     'rank processes by CPU and memory with ps --sort, top -b and /proc, and read RSS, %MEM and load correctly',
     'check who is logged in and what changed recently, and combine everything into a quick health check'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three tickets at 9:05'),
    ('decide', 'Which one-liner when?', 2, 'the quick chart'),
    ('definition', 'The admin toolkit', 6, 'simple meaning + 4 depths'),
    ('types', 'Problems and tools', 5, 'disk, ports, CPU, memory'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'drilling down a full disk'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'fix the tickets'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which one-liner? (decide in 5 seconds)', [
    ('Which disk is full?', 'df -h   (and df -i for inodes)', 'overview'),
    ('Which folder is big?', 'du -xh --max-depth=1 /var | sort -rh | head', 'drill down'),
    ('Which files are big?', "find / -xdev -type f -size +100M -exec ls -lh {} +", 'files'),
    ('Space used but no file to see', 'sudo lsof +L1', 'deleted but open'),
    ('Who uses port 8080?', 'sudo ss -ltnp | grep 8080   ·   sudo lsof -i :8080', 'ports'),
    ('Who uses this file / folder?', 'fuser -v FILE   ·   lsof FILE', 'busy files'),
    ('CPU hog', 'ps -eo pid,%cpu,cmd --sort=-%cpu | head', 'CPU'),
    ('Memory hog', 'ps -eo pid,rss,%mem,cmd --sort=-rss | head', 'memory'),
])

cmap = concept_map(
    [('11.2', 'ps and top', 'process columns'), ('13.2', 'find + xargs', 'big files'), ('11.3', 'Signals', 'stopping a process')],
    ['df -h and df -i', 'du drill-down, sort -h', 'deleted-but-open files (lsof +L1)', 'ports: ss, lsof -i, fuser', 'CPU/memory hogs: ps --sort, top -b', 'who, w, last: people'],
    [('15.4', 'df, du, free, swap', 'storage in depth'), ('16.4', 'ss and lsof', 'sockets in depth'), ('18.3', 'Performance', 'vmstat, iostat'), ('18.4', 'Troubleshooting playbook', 'step by step')],
    'Every admin ticket is “find the biggest, find the owner, then act”: biggest folder or file, the process on the port, the process using the CPU or memory.')

sc = (term(20, 14, 316, 156, ['$ du -sh ~/ad/data/* | sort -rh', ('30M  data/videos', 'acc'), ('21M  data/backups', 'out'), ('4.0M data/logs', 'out'), ('1.2M data/cache', 'out'), '$ lsof -i :8099 -t', ('4120', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=17)
      + t(352, 36, 'Admin pattern:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['1 overview (df)', '2 drill down (du)', '3 biggest first', '4 find the owner', '5 then act'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three tickets at 9:05</h2>
  <div class="story">
''' + puzzle('Riya deletes a 20 GB log file, but <code>df -h</code> still shows the disk 97% full. On another server <code>df -h</code> shows 40% used, yet every new file fails with “No space left on device”. And on the third, <code>du -sh /</code> says 8 GB while <code>df</code> says 30 GB are used. Each server is telling the truth. What is going on?') + '''
    <p class="narration">Riya starts with the disk ticket: overview first, then drill down.</p>
''' + scene('A terminal: du shows the size of each data folder sorted biggest first (videos 30M, backups 21M, logs, cache), and lsof finds the PID listening on port 8099.', sc,
            'Always <tspan font-weight="700" class="s-acc">biggest first</tspan>: sort -rh does it.') + '''
K> Why not just look around with ls?
A> ls shows one folder at a time and does not add up sub-folders. <code>du</code> totals every folder, <code>sort -rh</code> puts the biggest on top, and I go one level deeper each time. Five commands and I know which file is the problem.
R> And the port ticket?
A> A port belongs to exactly one process. <code>lsof -i :PORT</code>, <code>fuser PORT/tcp</code> or <code>ss -ltnp</code> name it. Then I decide: is it an old copy of the app (stop it) or something else (change the port)? Today: all three tickets, and the traps from the puzzle.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A building manager handling complaints: for a full storage room she checks each floor (du), then each room, then each box. For a blocked parking slot (port) she looks up whose car it is (lsof). For a noisy tenant (CPU hog) she checks the meter readings (ps).">'
       + label_box(14, 24, 190, 120, ['STORAGE FULL', 'df: which building', 'du: which floor/room', 'find: which box'], 'blue', 9)
       + label_box(224, 24, 190, 120, ['PARKING SLOT TAKEN', 'port 8080', 'lsof / ss / fuser:', 'whose car?'], 'amber', 9)
       + label_box(434, 24, 190, 120, ['NOISY TENANT', 'ps --sort=-%cpu', 'ps --sort=-rss', 'top -b'], 'red', 9)
       + t(320, 172, 'Find the biggest, find the owner, then decide.', 10, 'acc', bold=True)
       + t(320, 194, 'Never delete or kill before you know what it is.', 9.4, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Admin one-liners at four depths', [
    ('v', 'No jargon: a building manager', '      <p>Each complaint has a meter to read and an owner to find.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>df -h</code>: how full each disk is.</li>
        <li><code>du -sh * | sort -rh | head</code>: biggest folders here.</li>
        <li><code>sudo lsof -i :8080</code>: who uses port 8080.</li>
        <li><code>ps aux --sort=-%mem | head</code>: memory hogs.</li>
      </ul>'''),
    ('i', 'Reading the numbers right', '''      <ul>
        <li><code>df</code> asks the file system how many blocks are used; <code>du</code> adds up the files it can see. They differ when files are deleted but still open, or hidden under a mount point.</li>
        <li><code>df -i</code>: inodes. Millions of tiny files can fill the inode table while blocks are free (“No space left on device” at 40%).</li>
        <li><code>du -x</code> stays on one file system (does not count /proc or other disks).</li>
        <li>RSS = memory really in RAM; VSZ = address space (much bigger, mostly not used). %CPU in ps is an average over the process lifetime; top shows the current rate.</li>
        <li>Ports below 1024 and other users’ processes need <code>sudo</code> to see the PID.</li>
      </ul>'''),
    ('a', 'Behind the screen: inodes, open files and sockets', '''      <ul>
        <li>Deleting a file removes its <b>name</b>; the blocks are freed only when the last name is gone <b>and</b> no process has it open (link count 0 + open count 0). A log still written by a running program keeps its space: <code>lsof +L1</code> lists such files; restart the program or truncate via <code>/proc/PID/fd/N</code>.</li>
        <li>ext4 reserves 5% of blocks for root (<code>tune2fs -m</code>), so users see “full” before df says 100%.</li>
        <li>lsof and fuser read <code>/proc/*/fd</code>; ss reads sockets from the kernel via netlink (<code>/proc/net/tcp</code> is the older text view).</li>
        <li>A socket in TIME_WAIT after a restart is not a process; <code>SO_REUSEADDR</code> lets the server bind again.</li>
        <li>Memory: the kernel uses free RAM as page cache; <code>free</code>’s “available” column is the real headroom. The OOM killer picks by <code>oom_score</code> (Lesson 11.3: exit 137).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>The admin one-liner toolkit</h2>
''' + def_block(
    '<b>Server admin one-liners</b> are short command combinations for the most frequent operations questions: what fills a disk (<code>df</code>, <code>du</code>, <code>find</code>), which process holds a port or file (<code>ss</code>, <code>lsof</code>, <code>fuser</code>), which processes use the most CPU or memory (<code>ps --sort</code>, <code>top -b</code>), and who is logged in (<code>who</code>, <code>w</code>, <code>last</code>).',
    'Measure, rank biggest first, find the owner, then act.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('df', 'Space per file system.'),
    ('du', 'Space used by files and folders.'),
    ('Inode', 'One per file; can run out (df -i).'),
    ('Deleted but open', 'Space held by a removed file still in use.'),
    ('Port', 'Number a server listens on (80, 443, 8080).'),
    ('lsof / fuser', 'Who has a file or socket open.'),
    ('RSS', 'Memory actually in RAM.'),
    ('Load average', 'Runnable tasks over 1, 5, 15 min.'),
]) + '\n' + names('Where the names come from.', [
    ('df', 'disk free', 'Unix V1.'),
    ('du', 'disk usage', 'Unix V1.'),
    ('lsof', 'list open files', 'Vic Abell, 1994.'),
    ('fuser', 'file user', 'System V.'),
    ('ss', 'socket statistics', 'Replaces netstat.'),
    ('RSS', 'resident set size', 'Pages in RAM.'),
    ('VSZ', 'virtual size', 'Address space.'),
    ('ncdu', 'NCurses du', 'Interactive du.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Disks', '<code>df -h</code> · <code>df -i</code>'),
    ('Folders', '<code>du -sh * | sort -rh</code>'),
    ('Big files', '<code>find -size +100M</code>'),
    ('Port owner', '<code>sudo ss -ltnp</code>'),
    ('CPU hogs', '<code>ps --sort=-%cpu</code>'),
    ('Memory hogs', '<code>ps --sort=-rss</code>'),
]) + '\n' + lv + didyou('The most common cause of “I deleted the log but the disk is still full” is a log file deleted by hand while the web server still writes to it. The fix is not deleting more files: it is <code>systemctl reload nginx</code> (so it reopens a new log) or emptying the file with <code>: &gt; access.log</code> instead of deleting it.') + '''
EXAM> “How do you find which process is using port 80?” → sudo ss -ltnp | grep ':80 ' (or sudo lsof -i :80, sudo fuser 80/tcp, netstat -ltnp on old systems).
''' + qc('df says 95% used, du of everything says much less. Name one likely cause.', 'Files deleted while still open by a process (check sudo lsof +L1); or files hidden under a mount point.') + mistake('rm a huge log that a service is writing',
    ': > /var/log/app/huge.log   (truncate)   ·   or rotate with logrotate and reload the service',
    'rm only removes the name; the process keeps the space until it closes the file (real run: df unchanged, lsof +L1 shows it).') + mistake('kill -9 whatever ss shows on the port',
    'check what it is (ps -fp PID, systemctl status), stop it properly (systemctl stop / kill), or change your app’s port',
    'The “stray” process may be the real production service.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Problems, tools and what each shows</h2>
''' + table(['Ticket', 'First command', 'Then', 'Typical cause'], [
    ['Disk full', '<code>df -h</code>', '<code>du -xh --max-depth=1 / | sort -rh</code>', 'logs, backups, caches, core dumps'],
    ['Full but nothing to delete', '<code>sudo lsof +L1</code>', 'restart / truncate', 'deleted log still open'],
    ['No space at 40%', '<code>df -i</code>', '<code>find / -xdev -type d -size +1M</code>', 'millions of tiny files'],
    ['Port in use', '<code>sudo ss -ltnp</code>', '<code>ps -fp PID</code>', 'old copy still running'],
    ['File busy / cannot unmount', '<code>fuser -vm /mnt</code>', '<code>lsof +D /mnt</code>', 'a shell cd’d into it'],
    ['CPU 100%', '<code>top</code> / <code>ps --sort=-%cpu</code>', '<code>ps -fp PID</code>, logs', 'loop, runaway job'],
    ['Out of memory', '<code>free -h</code>', '<code>ps --sort=-rss</code>', 'leak, too many workers'],
    ['Who is on the box?', '<code>w</code>', '<code>last -n 10</code>', '-'],
], minw=560) + table(['', 'df', 'du'], [
    ['Asks', 'the file system (superblock)', 'every file it can see'],
    ['Counts deleted-but-open', 'yes', 'no'],
    ['Counts files under a mount point', 'no (hidden)', 'no (it sees the mount)'],
    ['Speed', 'instant', 'slow on big trees'],
    ['Use', 'which disk', 'which folder'],
], minw=420) + table(['Tool', 'Ports', 'Files', 'Needs sudo for others', 'Package'], [
    ['<code>ss -ltnp</code>', 'yes (fast)', 'no', 'yes (for -p)', 'iproute2'],
    ['<code>netstat -ltnp</code>', 'yes (old)', 'no', 'yes', 'net-tools'],
    ['<code>lsof -i :P</code>', 'yes', 'yes', 'yes', 'lsof'],
    ['<code>fuser P/tcp</code>', 'yes (PID only)', 'yes', 'yes', 'psmisc'],
], minw=480) + table(['ps column', 'Means', 'Watch out'], [
    ['%CPU', 'CPU time / lifetime', 'average, not now (top is now)'],
    ['RSS', 'KiB in RAM', 'shared libraries counted in each process'],
    ['VSZ', 'KiB of address space', 'not real usage'],
    ['%MEM', 'RSS / total RAM', '-'],
    ['STAT', 'R running, S sleeping, D disk wait, Z zombie', 'D cannot be killed (11.3)'],
], minw=420) + qc('Which command shows inode usage?', 'df -i.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Disk, ports and processes, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya. Disk examples use <code>~/ad/data</code> (a 30 MB video, two backups of 12 and 9 MB, a 4 MB log, 300 small thumbnails). Process examples start a web server on port 8099 (<code>python3 -m http.server</code>), a CPU hog (<code>yes</code>, renamed <code>hog_cpu</code>) and a memory hog (Python holding 120 MB). The build machine has no <code>ss</code> installed, so ports are shown with <code>lsof</code> and <code>fuser</code>; <code>ss</code> output is in Run on your PC.</p>
''' + cmdcard_u(['disk-full tickets', 'cleaning before backups', 'capacity checks'],
               ['du on / without -x (it walks /proc and other disks)', 'deleting before you know what it is'])(
    'disk', 'df -h · du -sh * | sort -rh · du -xh --max-depth=1 · find -size', 'what fills the disk',
    'Start with <code>df -h</code> to see which file system is full. Then drill down: <code>du -xh --max-depth=1 DIR | sort -rh | head</code>, and repeat on the biggest folder. Finally list big files with <code>find DIR -xdev -type f -size +100M</code>. <code>sort -h</code> understands K, M, G.',
    'df -h   ·   du -xh --max-depth=1 /var | sort -rh | head   ·   find / -xdev -size +500M', 'safe',
    [('df -h', 'which disk', 'overview'),
     ('df -h /var', 'one path', 'focus'),
     ('du -sh *', 'each item here', 'quick'),
     ('du -xh -d1 DIR | sort -rh', 'drill down', 'levels'),
     ('find -size +100M', 'big files', 'files'),
     ('find -mtime +180 -size +1M', 'old and big', 'archives'),
     ('du -sh --apparent-size', 'logical size', 'sparse files')],
    dict(setup=DISK, cmd="cd ~/ad\ndf -h ~ | awk 'NR==1 || /\\//{print $2, $3, $4, $5}'\ndu -xh --max-depth=1 data | sort -rh | head -5\ndu -ah data/backups | sort -rh\nfind data -xdev -type f -size +5M -exec ls -lh {} + | awk '{print $5, $NF}'", note='Overview → biggest folder → inside it → the big files.'),
    [('sys', [
        dict(situation='Old big files are the safest to archive.', setup=DISK, cmd="cd ~/ad; find data -type f -size +5M -mtime +90 -printf '%TY-%Tm-%Td  %10s  %p\\n'", why='The 200-day-old backup is the obvious candidate.')]),
     ('qa', [
        dict(situation='Many small files: count them, not just size.', setup=DISK, cmd="cd ~/ad; for d in data/*/; do printf '%-18s %6s files %6s\\n' \"$d\" \"$(find \"$d\" -type f | wc -l)\" \"$(du -sh \"$d\" | cut -f1)\"; done", why='cache has 300 files: tiny in size, large in inode count.')]),
    ],
    anat=anatomy([('du -xh', 'cmd', 'human sizes, one file system'), ('--max-depth=1 data', 'opt', 'one level'), ('| sort -rh', 'arg', 'biggest first, understands K/M/G'), ('| head', 'arg', 'top 10')], 'Repeat on the biggest folder until you reach files.')
) + cmdcard_u(['disk still full after rm', 'df and du disagree', '“No space” with free blocks'],
               ['rm on logs a service is writing'])(
    'traps', 'lsof +L1 · df -i · : > file', 'the two disk-full traps',
    'If a deleted file is still open, its space is not freed: <code>lsof +L1</code> lists open files with link count 0. Fix: restart/reload the process, or truncate it through <code>/proc/PID/fd/N</code>. If <code>df -i</code> shows 100% inodes, the problem is the <b>number</b> of files; find folders with huge counts.',
    'sudo lsof +L1   ·   df -i   ·   : > /proc/PID/fd/N', 'change',
    [('lsof +L1', 'deleted but open', 'df > du'),
     ('ls -l /proc/PID/fd', 'a process’s files', 'which fd'),
     (': > /proc/PID/fd/N', 'free it now', 'no restart'),
     ('df -i', 'inode use', '“No space” at 40%'),
     ('find DIR -xdev -printf "%h\\n" | sort | uniq -c | sort -rn', 'files per folder', 'inode hunt'),
     (': > file', 'truncate instead of rm', 'safe habit')],
    dict(setup=DISK, cmd="cd ~/ad; (setsid python3 -c 'import sys,time; sys.argv[0]=\"holder\"; f=open(\"data/logs/app.log\",\"a\"); time.sleep(60)' &) ; sleep 0.5\nbefore=$(du -sk data | cut -f1); rm data/logs/app.log; after=$(du -sk data | cut -f1)\necho \"du: ${before}K -> ${after}K (the file is gone from du)\"\nlsof +L1 -u riya 2>/dev/null | awk 'NR==1 || /app.log/{print $1, $4, $7, $9, $10}'\npid=$(pgrep -f holder); fd=$(ls -l /proc/$pid/fd | awk '/app.log/{print $9}')\n: > /proc/$pid/fd/$fd; lsof +L1 -u riya 2>/dev/null | awk '/app.log/{print \"after truncate, size:\", $7}'\npkill -f holder", note='The puzzle: rm removed the name, but the open file kept its 4 MB until we truncated it through /proc.'),
    [('sys', [
        dict(situation='Inodes: count, not size.', setup=DISK, cmd="df -i ~ | awk 'NR==1 || /\\//{print $2, $3, $4, $5}'\ncd ~/ad; find data -xdev -printf '%h\\n' | sort | uniq -c | sort -rn | head -2", why='The folder with the most entries is where inodes go.')]),
    ]
) + cmdcard_u(['“address already in use”', 'which service listens where', 'cannot unmount: device busy'],
               ['killing the PID without checking what it is'])(
    'ports', 'ss -ltnp · lsof -i :PORT · fuser PORT/tcp · fuser -vm', 'who uses a port or file',
    '<code>ss -ltnp</code> lists listening TCP sockets with the owning process (sudo for other users’). <code>lsof -i :PORT</code> shows the process and connection; <code>-t</code> prints only PIDs. <code>fuser PORT/tcp</code> prints the PID; <code>fuser -v FILE</code> or <code>-vm MOUNT</code> shows who uses files.',
    'sudo ss -ltnp | grep :8080   ·   sudo lsof -i :8080   ·   sudo fuser 8080/tcp', 'safe',
    [('ss -ltnp', 'listening TCP + process', 'modern'),
     ('ss -lunp', 'UDP', 'DNS, syslog'),
     ('lsof -i :PORT', 'process on a port', 'detail'),
     ('lsof -i -P -n', 'all network files, numeric', 'overview'),
     ('lsof -t -i :PORT', 'PID only', 'scripts'),
     ('fuser -v PORT/tcp', 'PID and user', 'quick'),
     ('fuser -vm /mnt', 'who blocks unmount', 'busy mounts')],
    dict(setup=PROCS, cmd="lsof -i :8099 -P -n | awk '{print $1, $2, $3, $5, $8, $9, $10}'\nfuser 8099/tcp 2>&1 | sed -E 's/[0-9]{3,}/PID/'\npid=$(lsof -t -i :8099); ps -o pid=,etime=,cmd= -p $pid | sed -E 's/^ *[0-9]+/PID/'\npython3 -m http.server 8099 --bind 127.0.0.1 2>&1 | tail -1", expect='any', note='The ticket: a second server on the same port fails with “Address already in use”; lsof and fuser named the owner.'),
    [('sys', [
        dict(situation='Stop the old copy properly, then start again.', setup=PROCS, cmd="pid=$(lsof -t -i :8099); kill $pid; sleep 0.5\nlsof -i :8099 > /dev/null || echo 'port 8099 is free'\n(setsid timeout 5 python3 -m http.server 8099 --bind 127.0.0.1 > /dev/null 2>&1 &); sleep 1; lsof -t -i :8099 > /dev/null && echo 'new server listening'", why='TERM first (Lesson 11.3); confirm the port is free; start the new one.')]),
     ('dev', [
        dict(situation='Who has this file open?', setup=PROCS, cmd="cd ~/ad; (setsid python3 -c 'import sys,time; sys.argv[0]=\"holder\"; f=open(\"report.csv\",\"w\"); time.sleep(30)' &); sleep 0.5\nfuser -v report.csv 2>&1 | sed -E 's/[0-9]{3,}/PID/'\nlsof report.csv | awk '{print $1, $3, $4, $NF}'; pkill -f holder", why='Before deleting or moving a file another program writes.')]),
    ]
) + cmdcard_u(['slow server', 'out-of-memory incidents', 'capacity planning'],
               ['VSZ as memory use', 'ps %CPU as the current rate'])(
    'hogs', 'ps -eo … --sort=-%cpu / -rss · top -b -n1 · free -h', 'CPU and memory hogs',
    '<code>ps -eo pid,user,%cpu,%mem,rss,cmd --sort=-%cpu | head</code> ranks by CPU (lifetime average); <code>--sort=-rss</code> by real memory. <code>top -b -n1 -o %CPU</code> gives the current view in batch mode for scripts. <code>free -h</code>’s <b>available</b> column is the real free memory.',
    'ps -eo pid,%cpu,%mem,rss,cmd --sort=-%cpu | head   ·   free -h', 'safe',
    [('--sort=-%cpu', 'CPU first', 'slow box'),
     ('--sort=-rss', 'memory first', 'OOM'),
     ('-o pid,ppid,etime,cmd', 'who started it, how long', 'context'),
     ('top -b -n1 -o %MEM', 'snapshot sorted', 'scripts'),
     ('free -h', 'RAM and swap', 'headroom'),
     ('uptime / nproc', 'load vs CPUs', 'is it busy?'),
     ('ps -eLf | wc -l', 'threads', 'thread leaks')],
    dict(setup=PROCS, cmd="ps -u riya -o pid=,%cpu=,%mem=,rss=,comm= --sort=-%cpu | head -3 | awk '{printf \"%5s%% CPU %4s%% MEM %7.1f MB  %s\\n\", $2, $3, $4/1024, $5}'\nps -u riya -o rss=,args= --sort=-rss | head -2 | awk '{printf \"%7.1f MB  %s %s\\n\", $1/1024, $2, $3}'\nfree -h | awk 'NR==1{print \"      \", $1, $2, $6} NR==2{print $1, $2, $3, $7}'", note='yes (hog_cpu) uses a full CPU; the Python hog holds 120 MB in RAM.'),
    [('data', [
        dict(situation='Memory per program (all processes of a name).', setup=PROCS, cmd="ps -u riya -o rss=,comm= | awk '{m[$2]+=$1} END{for(c in m) printf \"%8.1f MB  %s\\n\", m[c]/1024, c}' | sort -rn | head -3", why='Several workers of the same program add up.')]),
     ('sys', [
        dict(situation='Load versus CPUs.', cmd="read l1 l5 l15 rest < /proc/loadavg; echo \"CPUs: $(nproc); load: $l1 $l5 $l15\" | sed -E 's/load: [0-9. ]+/load: N N N/'; echo 'rule of thumb: load above the CPU count for long = overloaded'", why='Load 4 on a 2-CPU box means work is waiting (Lesson 18.3).')]),
    ]
) + undo('Looking is harmless; deleting files and killing processes is not.', [
    ('Deleted the wrong big file:', 'restore from backup; next time move it to a holding folder first.'),
    ('Killed the wrong process on a port:', '<code>systemctl start SERVICE</code>; check <code>systemctl status</code>.'),
    ('Truncated a log by mistake:', 'the old lines are gone; rotated copies (access.log.1, .gz) may still have them.'),
    ('Habit:', 'look (df/du/ss/ps) → identify (ps -fp, systemctl status) → act (rotate, stop, archive).'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='du -sh /root', meaning='No permission to read another user’s folder.', fix='sudo du -sh /root.'),
    dict(cmd='lsof -i :1', meaning='Nothing listens on port 1 (lsof exits 1).', fix='Check the port number.'),
    dict(setup=PROCS, cmd='python3 -m http.server 8099 --bind 127.0.0.1 2>&1 | tail -1; exit ${PIPESTATUS[0]}', meaning='The port is taken.', fix='Find the owner with lsof -i :8099.'),
    dict(cmd='ss -ltnp', meaning='ss is not installed on this machine (package iproute2).', fix='sudo apt install iproute2, or use lsof -i.'),
    dict(cmd='kill 1', meaning='PID 1 is systemd, not yours.', fix='Use the PID from lsof/ss.'),
]) + qc('Which ps option sorts by memory, biggest first?', '--sort=-rss.') + '''
'''
cards = cards + '</section>\n'

LEVELS = [('/', '40G used of 50G (80%)'), ('~/ad/data', 'videos 30M · backups 21M · logs 4M · cache 1.2M'), ('data/videos', 'demo.mp4 30M'), ('decision', 'archive demo.mp4, delete 200-day-old backup')]
def drill(k):
    o = ''
    for i in range(k + 1):
        o += label_box(10 + i * 10, 10 + i * 40, 330 - i * 20, 34, [f'{LEVELS[i][0]}: {LEVELS[i][1]}'], ['blue', 'amber', 'red', 'green'][i], 7.6)
    return o
see_cmds = [['$ df -h /', ('/dev/vda  50G  40G  80%  /', 'out')], ['$ du -xh -d1 ~/ad/data | sort -rh', ('30M data/videos', 'acc'), ('21M data/backups', 'out')], ['$ find data/videos -size +5M -ls', ('… 30M … demo.mp4', 'out')], ['$ mv demo.mp4 /archive/', ('(space back)', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Overview.', 'Drill down.', 'The file.', 'Decide.'])]
behind = [drill(k) for k in range(4)]
two = anim_two('Drilling down a full disk', 'Behind the screen: one level at a time',
               'A terminal: df shows the disk, du ranks folders, find shows the big file, then it is archived.',
               'Boxes stacked like a staircase: disk, data folder with sizes, videos folder, decision.', see, behind,
               ['df.', 'du.', 'find.', 'act.'],
               ['df', 'du', 'find', 'act'])

def deleted(k):
    o = label_box(20, 20, 140, 40, ['name: app.log'], 'blue' if k == 0 else 'card', 8.6)
    o += label_box(200, 20, 140, 40, ['process (fd 3)'], 'amber', 8.6)
    o += label_box(110, 100, 140, 40, ['inode: 4 MB blocks'], 'red' if k < 3 else 'green', 8.6)
    if k == 0:
        o += arrow(90, 60, 160, 100)
    o += arrow(270, 60, 200, 100) if k < 3 else ''
    o += t(180, 170, ['A name and an open file point to the data.', 'rm removes only the name…', '…the process still holds the blocks: df stays full.', 'Truncate or restart: space freed.'][k], 8.6, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Deleted but still open',
              'Why df does not change after rm.',
              'rm app.log  →  lsof +L1', 'A file name and a process both point to the data blocks; after rm only the process points to them, so the space stays used until it is truncated or the process closes it.', [deleted(k) for k in range(4)],
              ['Before.', 'rm.', 'Still used.', 'Freed.'], hid='scenario-deleted')

dx = dissect('Layer by layer: where the answers come from',
    'Each layer has a real command and output from our build machine.', [
    dict(key='statfs', name='df', sub='statfs()', why='Whole file system.', how='Superblock counts.', impl='Instant.', used='Overview.',
         cmd="stat -f -c 'blocks of %S bytes: total %b, free %f, inodes total %c, free %d' ~ | sed -E 's/[0-9]{4,}/N/g'"),
    dict(key='fd', name='Open files', sub='/proc/PID/fd', why='lsof’s source.', how='Symlinks per fd.', impl='Per process.', used='Who holds what.',
         cmd="sleep 30 > ~/fdtest.txt & sleep 0.2; ls -l /proc/$!/fd | awk 'NR>1{print $9, $10, $11}' | sed 's|/home/riya|~|'; kill $!; rm -f ~/fdtest.txt"),
    dict(key='net', name='Sockets', sub='/proc/net/tcp', why='ss/netstat’s source.', how='Hex addresses.', impl='Kernel table.', used='No tools installed.',
         setup=PROCS, cmd="awk 'NR>1 && $4==\"0A\"{split($2,a,\":\"); printf \"listening on port %d\\n\", strtonum(\"0x\" a[2])}' /proc/net/tcp 2>/dev/null | grep 8099 || awk 'NR>1 && $4==\"0A\"{print $2}' /proc/net/tcp | grep -ci ':1FA3' | sed 's/^/sockets listening on 8099 (hex 1FA3): /'"),
    dict(key='mem', name='Memory', sub='/proc/meminfo', why='free’s source.', how='kB counters.', impl='MemAvailable.', used='Real headroom.',
         cmd="awk '/^(MemTotal|MemAvailable|Cached):/{printf \"%-13s %6.0f MB\\n\", $1, $2/1024}' /proc/meminfo | sed -E 's/[0-9]+ MB/N MB/'"),
], hint='From system calls to /proc. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Drilling down a disk, and deleted-but-open files</h2>
''' + two + s1 + dx + qc('Why does du not see the space held by a deleted-but-open file?', 'du walks file names; the file has no name any more. df asks the file system, which still counts the blocks.') + '''
</section>
'''

VAR = variations('Twenty more admin one-liners. All were really run on our build machine.', [
    ('Disk', [
        dict(title='Top 5 biggest files under a folder', setup=DISK, cmd="find ~/ad -type f -printf '%s %p\\n' | sort -rn | head -5 | awk '{printf \"%6.1f MB  %s\\n\", $1/1048576, $2}' | sed 's|/home/riya|~|'", why='-printf %s prints bytes; sort numerically.'),
        dict(title='Folder sizes in MB, sorted', setup=DISK, cmd="du -sm ~/ad/data/* | sort -rn | sed 's|/home/riya|~|'", why='-m gives whole MB, easy to sort with -n.'),
        dict(title='Total size of all .gz backups', setup=DISK, cmd="find ~/ad -name '*.gz' -print0 | du -ch --files0-from=- | tail -1", why='du sums a list of files.'),
        dict(title='How full in percent (for alerts)', cmd="df --output=pcent ~ | tail -1 | tr -d ' %' | sed 's/^/used: /; s/$/%/'", why='--output picks one column.'),
        dict(title='Alert above a threshold', cmd="u=$(df --output=pcent ~ | tail -1 | tr -d ' %'); [ \"$u\" -gt 90 ] && echo \"ALERT: $u%\" || echo \"ok: below 90%\"", why='A cron-ready check.'),
        dict(title='Files changed in the last 10 minutes', setup=DISK, cmd="find ~/ad -type f -mmin -10 | wc -l", why='What just grew?'),
        dict(title='Empty the cache safely', setup=DISK, cmd="cd ~/ad; before=$(du -sk data/cache | cut -f1); find data/cache -type f -name '*.jpg' -delete; echo \"cache: ${before}K -> $(du -sk data/cache | cut -f1)K\"", why='Caches are rebuildable: safe to clear.'),
    ]),
    ('Ports and files', [
        dict(title='Everything listening (lsof)', setup=PROCS, cmd="lsof -a -i -P -n -sTCP:LISTEN -u riya | awk 'NR>1{print $1, $9}' | sort -u", why='-sTCP:LISTEN only listeners.'),
        dict(title='Is a port free? (for scripts)', setup=PROCS, cmd="for p in 8099 8100; do lsof -t -i :$p > /dev/null && echo \"$p busy\" || echo \"$p free\"; done", why='lsof -t exits 0 if something uses it.'),
        dict(title='Test a port from the client side', setup=PROCS, cmd="for p in 8099 8100; do (exec 3<>/dev/tcp/127.0.0.1/$p) 2>/dev/null && echo \"$p: open\" || echo \"$p: closed\"; done", why='bash /dev/tcp tries a real connection (Lesson 16.4).'),
        dict(title='Open files of one process', setup=PROCS, cmd="lsof -p $(lsof -t -i :8099) | awk 'NR>1{print $4, $5}' | sort | uniq -c | sort -rn | head -3", why='Types of descriptors the server holds.'),
        dict(title='Count open files per process', setup=PROCS, cmd="for p in $(pgrep -u riya -x python3) $(pgrep -u riya -x yes); do printf '%-12s %3d fds\\n' \"$(ps -o comm= -p $p)\" \"$(ls /proc/$p/fd | wc -l)\"; done", why='File-descriptor leaks show up here.'),
    ]),
    ('Processes and people', [
        dict(title='Top 3 CPU (current view from top)', setup=PROCS, cmd="top -b -n1 -o %CPU -u riya | awk 'NR>7 && NR<=10{print $9\"%\", $12}'", why='top -b is scriptable.'),
        dict(title='Processes running longer than a day', cmd="ps -eo etimes=,pid=,comm= | awk '$1>86400' | wc -l | sed 's/^/processes older than 1 day: /'", why='etimes = seconds since start.'),
        dict(title='Zombies?', cmd="ps -eo stat=,pid=,comm= | awk '$1 ~ /^Z/' | wc -l | sed 's/^/zombies: /'", why='Z state: parent did not reap them (Lesson 11.3).'),
        dict(title='Stop the CPU hog politely', setup=PROCS, cmd="pkill -u riya -f hog_cpu; sleep 0.3; pgrep -f hog_cpu > /dev/null || echo 'hog_cpu stopped'", why='TERM by name; check it is gone.'),
        dict(title='Who is logged in and from where', cmd="who | wc -l | sed 's/^/sessions: /'; w -h | awk '{print $1}' | sort | uniq -c | head -3", why='who / w (often empty on servers reached by scripts).'),
        dict(title='Last logins and reboots', cmd="last -n 3 2>&1 | head -4", why='last reads /var/log/wtmp.'),
        dict(title='A 5-line health check', setup=PROCS, cmd="echo \"disk:  $(df --output=pcent ~ | tail -1 | tr -d ' ') used\"; echo \"mem:   $(free -m | awk 'NR==2{print $7}') MB available\" | sed -E 's/[0-9]+ MB/N MB/'; echo \"load:  $(cut -d' ' -f1 /proc/loadavg | sed 's/.*/N/') on $(nproc) CPUs\"; echo \"top:   $(ps -u riya -o comm= --sort=-%cpu | head -1)\"; echo \"port:  8099 $(lsof -t -i :8099 > /dev/null && echo busy || echo free)\"", why='Five questions, five lines.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Admin one-liners at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['du | sort', 'disk'], 'blue', 8.6), '1. Disk-full incidents',
              'The classic: /var full at night because of logs, core dumps or forgotten backups; du drill-down finds it in minutes.', ['Alert', '*df → du → find', 'archive/rotate']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['lsof +L1', 'logs'], 'red', 8.6), '2. “Deleted but still full”',
    'A log removed by hand while nginx writes it; lsof +L1 shows it, a reload frees the space.', ['rm', '*lsof +L1', 'reload']) + '\n' + usecase(
    label_box(14, 22, 92, 46, [':8080', 'deploys'], 'amber', 8.6), '3. Failed deployments',
    'A new release cannot start because the old one still holds the port; ss/lsof shows the old PID.', ['Deploy fails', '*ss -ltnp', 'stop old']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['--sort', 'perf'], 'green', 8.6), '4. Slow servers',
    'ps --sort finds the runaway report or the leaking worker; nice or restart fixes it (Lesson 11.5).', ['Slow', '*ps --sort', 'fix']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['df -i', 'mail'], 'violet', 8.6), '5. Inode exhaustion',
    'Mail queues, PHP sessions and caches create millions of tiny files; df -i reveals it.', ['No space?', '*df -i', 'clean']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Disk overview', scenario='First look.', cmd="df -h ~ | tail -1 | awk '{print $5, \"used on\", $6}'", explain='df -h.'),
    dict(level='b', title='Biggest folders here', scenario='Where is it?', setup=DISK, cmd="cd ~/ad/data; du -sh * | sort -rh | head -3", explain='du | sort -rh.'),
    dict(level='i', title='Who has the port?', scenario='Deploy failed.', setup=PROCS, cmd="lsof -i :8099 -t | xargs -r ps -o comm=,args= -p | cut -c1-50", explain='lsof -t | ps.'),
    dict(level='i', title='Memory hog', scenario='OOM.', setup=PROCS, cmd="ps -u riya -o rss=,comm= --sort=-rss | head -1 | awk '{printf \"%.0f MB %s\\n\", $1/1024, $2}'", explain='--sort=-rss.'),
    dict(level='a', title='Deleted but open, in MB', scenario='df ≠ du.', setup=DISK, cmd="cd ~/ad; (setsid python3 -c 'import sys,time; sys.argv[0]=\"holder\"; f=open(\"data/videos/demo.mp4\"); time.sleep(20)' &); sleep 0.5; rm data/videos/demo.mp4; lsof +L1 -u riya 2>/dev/null | awk '/demo.mp4/{s+=$7} END{printf \"%.0f MB held by deleted files\\n\", s/1048576}'; pkill -f holder", explain='Sum the SIZE column.'),
], extra=build_up('the disk ticket', 'Riya answers “disk 97% full” step by step.', DISK, [
    ("df -h ~ | awk 'NR==2{print \"used:\", $5}'", '1. Is it really full? Which file system?'),
    ("cd ~/ad; du -xh --max-depth=1 data | sort -rh | head -3", '2. Which folder?'),
    ("cd ~/ad; find data -xdev -type f -size +5M -printf '%TY-%Tm-%Td %s %p\\n' | sort | awk '{printf \"%s %5.1f MB %s\\n\", $1, $2/1048576, $3}'", '3. Which files, how old?'),
    ("cd ~/ad; mkdir -p archive; mv data/backups/db-2026-11-01.sql.gz archive/; du -sh data/backups | cut -f1 | sed 's/^/backups now: /'", '4. Act on the oldest backup (move, do not delete), and check.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Which disk is full', 'df -h', 'Instant.', 'du on /.'),
    ('Which folder', 'du -xh -d1 | sort -rh', 'Drill down.', 'ls -l everywhere.'),
    ('Space not freed after rm', 'lsof +L1', 'Finds open deleted files.', 'Deleting more.'),
    ('Port owner', 'ss -ltnp / lsof -i', 'Exact PID.', 'Guessing and kill -9.'),
    ('Live CPU view', 'top / htop', 'Current rate.', 'ps %CPU (lifetime average).'),
    ('Interactive disk browser', 'ncdu', 'Fast navigation.', 'Not installed by default.'),
]) + keys('Handy forms.', [
    ('du -sh * | sort -rh', 'biggest here', 'disk'),
    ('df -i', 'inodes', 'tiny files'),
    ('lsof +L1', 'deleted but open', 'df ≠ du'),
    ('lsof -t -i :P', 'PID on port', 'scripts'),
    ('ps --sort=-rss', 'memory hogs', 'RAM'),
    (': > file', 'truncate safely', 'logs'),
]) + scriptit('healthcheck.sh', 'A quick server health check: disk and inode use with a warning threshold, memory available, load versus CPUs, the top CPU and memory processes, and whether given ports are in use.',
'''warn=${WARN:-85}; ports=("${@:-8099 22}")
read -r -a ports <<< "${ports[*]}"
printf '%-8s %s\\n' DISK "$(df -h --output=pcent,avail ~ | tail -1 | awk '{print $1" used, "$2" free"}')"
d=$(df --output=pcent ~ | tail -1 | tr -d ' %'); i=$(df --output=ipcent ~ | tail -1 | tr -d ' %')
[ "$d" -ge "$warn" ] && echo "  WARNING: disk above $warn%"; [ "$i" -ge "$warn" ] && echo "  WARNING: inodes above $warn%"
printf '%-8s %s MB available\\n' MEMORY "$(free -m | awk 'NR==2{print $7}')"
printf '%-8s %s (CPUs: %s)\\n' LOAD "$(cut -d' ' -f1-3 /proc/loadavg)" "$(nproc)"
printf '%-8s %s\\n' TOP_CPU "$(ps -u "$USER" -o comm= --sort=-%cpu | head -1)"
printf '%-8s %s\\n' TOP_MEM "$(ps -u "$USER" -o comm= --sort=-rss | head -1)"
for p in "${ports[@]}"; do printf '%-8s %s\\n' "PORT $p" "$(lsof -t -i :"$p" > /dev/null 2>&1 && echo "in use by $(ps -o comm= -p "$(lsof -t -i :"$p" | head -1)")" || echo free)"; done''',
'<p>Run with the default ports 8099 and 22.</p>', expect='any') + puzzle_answer('<b>1.</b> The 20 GB log was deleted while a process still had it open: the name is gone, the blocks are not. <code>sudo lsof +L1</code> shows it; reload or restart that service (or truncate it via /proc/PID/fd/N). <b>2.</b> The file system ran out of <b>inodes</b>, not blocks: <code>df -i</code> shows 100%. Millions of tiny files (cache, sessions, mail queue) are the usual cause. <b>3.</b> df counts blocks of deleted-but-open files and of files hidden under a mount point; du only counts files it can reach by name. Check <code>lsof +L1</code>, and look under mount points (mount the parent elsewhere with <code>mount --bind / /mnt/root</code>).') + qc('Which command lists processes holding deleted files?', 'lsof +L1 (with sudo for all users).') + '''
</section>
'''

_sh.run_sh(KILL + '; rm -rf ~/ad ~/fdtest.txt', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../11-processes/02-watching-processes-ps-pstree-top-and-htop/">Lesson 11.2</a> (ps and top) and <a href="../02-find-xargs-and-exec-one-liners/">Lesson 13.2</a> (find).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
