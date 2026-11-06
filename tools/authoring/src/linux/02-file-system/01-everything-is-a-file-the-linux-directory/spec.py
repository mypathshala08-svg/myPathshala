import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap
BODY = body(HERE)

META = dict(
    module='02-file-system', lesson='01-everything-is-a-file-the-linux-directory', n='2.1',
    module_label='Module 2 · The Linux file system',
    title='Everything is a file: the Linux directory hierarchy',
    desc='The Linux directory tree explained: one root /, the Filesystem Hierarchy Standard (/etc, /home, /usr, /var, /tmp, /dev, /proc, /sys, /boot, /opt), merged /usr, real vs virtual file systems, mounts, and what “everything is a file” really means. Animations, a layer-by-layer dissection, real Bash and interview questions.',
    og_desc='No C: drive? The Linux tree from / explained, folder by folder, with what happens behind the screen.',
    minutes=30, level='Beginner → Advanced',
    lead='Riya logs in to a server and looks for the C: drive. There isn’t one. This lesson walks through Linux’s single directory tree, what every top-level folder is for, where any application keeps its programs, settings, logs and data, and why on Linux even devices and running programs show up as files.',
    chips=['Story-based', '4 animations', 'Layer-by-layer', 'Real Bash in your browser'],
)

MAIN = '''# A guided tour of the Linux tree
ls /
echo "--- /bin is really:"; readlink -f /bin
echo "--- config entries in /etc: $(ls /etc | wc -l)"
cat /etc/hostname
echo "--- logs live in /var/log:"; ls /var/log | head -3
echo "--- your home: $HOME"
grep -m1 "model name" /proc/cpuinfo
ls -l /proc/self/exe
'''

RUN = dict(
    heading='A guided tour of the tree',
    intro='<p>Run the tour and match each output to a folder from the table above. The output below is from our Ubuntu build machine, which is a cloud container: it has a few extra top-level folders (for example <code>nix</code>, <code>old_root</code>) that a normal Ubuntu install does not have. Yours will differ in names and numbers.</p>',
    code=MAIN,
    anno=[
        ('ls /', 'The top of the tree. Compare with the table of top-level folders.'),
        ('readlink -f /bin', 'Follows the link to its real target: <code>/usr/bin</code> (merged /usr).'),
        ('cat /etc/hostname', 'A real configuration file: the machine’s name.'),
        ('ls /var/log | head -3', 'The first few log files. <code>head -3</code> keeps three lines.'),
        ('grep -m1 "model name" /proc/cpuinfo', 'A virtual file: the kernel writes CPU details when you read it. <code>-m1</code> = first match only.'),
        ('ls -l /proc/self/exe', 'Points to the program that is reading it: here, ls itself.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which top-level folders from the table can you see? Are there extra ones on OneCompiler’s machine?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what will <code>/proc/self/exe</code> point to when <code>cat</code> reads its status? Then run.',
             code='head -1 /proc/self/status\nls -l /proc/self/exe\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> a Windows habit. Fix it to list the root of the Linux tree.',
             code='ls C:\\\\\necho "exit status: $?"\n', expect='any'),
        dict(label='4 · Your turn', hint='Print the first 3 lines of <code>/etc/os-release</code> and the number of entries in <code>/usr/bin</code> (how many commands are installed?).',
             code='head -3 /etc/os-release\necho "commands in /usr/bin: $(ls /usr/bin | wc -l)"\n'),
        dict(label='5 · Challenge', hint='List the top-level folders that are actually symbolic links (hint: <code>find / -maxdepth 1 -type l</code>).',
             code='find / -maxdepth 1 -type l 2>/dev/null | sort\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: explore your own tree',
    intro='<p>Try these on your own Linux. <b>Outputs were recorded on our Ubuntu 24.04 build machine</b> (a cloud container, so some mounts look different from a laptop).</p>',
    items=[
        dict(title='1 · The top of the tree with details', cmd='ls -l / | head -8', output=pc('ls -l / | head -8'),
             note='<code>l</code> at the start of a line = a link (bin, lib, sbin point into usr); <code>d</code> = a directory.'),
        dict(title='2 · Which file systems make up your tree?', cmd='df -hT / /dev/shm', output=pc('df -hT / /dev/shm'),
             note='The root is ext4 on a disk; /dev/shm is tmpfs in RAM. On a laptop you will also see /boot/efi (vfat) and maybe /home on its own partition.'),
        dict(title='3 · The standard, built in', cmd='man hier | head -20', output='HIER(7)                Miscellaneous Information Manual                HIER(7)\n\nNAME\n       hier - description of the filesystem hierarchy\n\nDESCRIPTION\n       A typical Linux system has, among others, the following directories:\n\n       /      This is the root directory.  This is where the whole tree starts.\n\n       /bin   This directory contains executable programs which are needed in\n              single user mode and to bring the system up or repair it.',
             note='Typical output (manual pages are removed in our minimal build image). Read the full page: it describes every standard folder.'),
        dict(title='4 · Logs need root to read', cmd='ls -l /var/log/auth.log; sudo tail -3 /var/log/auth.log', output='-rw-r----- 1 syslog adm 48213 Nov  5 10:02 /var/log/auth.log\n2026-11-05T10:01:12 app-01 sshd[1023]: Accepted publickey for riya from 203.0.113.7\n2026-11-05T10:01:12 app-01 sshd[1023]: pam_unix(sshd:session): session opened for user riya\n2026-11-05T10:02:40 app-01 sudo:     riya : TTY=pts/0 ; PWD=/home/riya ; USER=root ; COMMAND=/usr/bin/tail -3 /var/log/auth.log',
             note='Typical output on an Ubuntu server (our build container has no SSH logins to show). Notice the permissions: only root and the <code>adm</code> group may read it.'),
    ],
)

TRACE = dict(
    heading='Building a mini tree, line by line',
    intro='<p>Inside <code>~/lab</code> the script builds a small copy of the standard layout for an app and puts a config, a log and data where the FHS says they belong. Watch the <b>Files</b> box grow into a tree.</p>',
    code='''app=shop
mkdir -p etc/$app var/log/$app var/lib/$app
echo "port=8080" > etc/$app/$app.conf
echo "started" >> var/log/$app/$app.log
echo "orders=0" > var/lib/$app/state
find . -type f | sort
''',
    notes={2: 'Layout :: One mkdir creates the three standard places: config, logs and data.',
           3: 'Config :: Settings go to etc: plain text.', 4: 'Log :: <code>>></code> appends: logs only grow.', 5: 'Data :: State the program must keep goes to var/lib.',
           6: 'Check :: <code>find . -type f</code> lists every file below the current folder.'},
)

WORKED_INTRO = 'Three real tasks: mapping where an app lives, checking which folders are virtual, and finding what is filling a disk.'
EXAMPLES = [
    dict(level='b', tag='Support', title='Where does this machine keep its basic identity?',
         problem='<p>Support asks for the host name, the distribution and the time zone of a server. All three are plain text files in <code>/etc</code>. Print them with labels.</p>',
         inp='/etc/hostname, /etc/os-release, /etc/timezone',
         approach=['Each fact is a file in /etc: read it with cat or grep.', 'Use <code>cut</code> to remove the quotes from the distro name.'],
         code='''echo "Host    : $(cat /etc/hostname)"
echo "Distro  : $(grep '^PRETTY_NAME' /etc/os-release | cut -d'"' -f2)"
echo "Timezone: $(cat /etc/timezone 2>/dev/null || echo unknown)"
''',
         notes={3: 'Fallback :: <code>2>/dev/null || echo unknown</code> prints “unknown” if the file does not exist (some systems use only /etc/localtime).'},
         tryit='Add a line with the number of user accounts: <code>wc -l &lt; /etc/passwd</code>.'),
    dict(level='i', tag='Exploration', title='Real or virtual? Classify the top-level folders',
         problem='<p>Kabir wants a list of top-level folders that are <b>not</b> stored on the main disk (they are virtual or in RAM).</p>',
         inp='/proc /sys /dev /run /tmp /dev/shm /etc /usr',
         approach=['For each folder ask <code>findmnt --target</code> for its file-system type.', 'Print “disk” for ext4/xfs and “virtual/RAM” for the rest.'],
         code='''for d in /proc /sys /dev /run /tmp /dev/shm /etc /usr; do
  fs=$(findmnt -n -o FSTYPE --target "$d" | head -1)
  case $fs in
    ext4|xfs|btrfs) kind="disk" ;;
    *)              kind="virtual/RAM" ;;
  esac
  printf "%-9s %-9s %s\\n" "$d" "$fs" "$kind"
done
''',
         notes={2: 'Ask :: findmnt finds which mount holds this path.', 7: 'Print :: <code>printf</code> lines up the columns.'},
         tryit='Our build machine is a container, so /run is on its disk; on a normal Ubuntu install /run is tmpfs and /tmp may be too. Run it on your own Linux and compare.'),
    dict(level='a', tag='Business problem', title='What is filling the disk? Top folders under a tree',
         problem='<p>A sample “server” folder tree is filling up. Find the three biggest sub-folders of <code>var</code>, largest first, so the team knows where to clean.</p>',
         inp='srv-copy/var/log (5 MB), srv-copy/var/lib (2 MB), srv-copy/var/cache (1 MB), srv-copy/var/tmp (small)',
         approach=['Create sample files of known sizes with <code>head -c</code>.', '<code>du -sh</code> each folder, <code>sort -h</code> by size, <code>tail</code> the biggest, reverse with <code>sort -hr</code>.'],
         code='''mkdir -p srv-copy/var/{log,lib,cache,tmp}
head -c 5000000 /dev/zero > srv-copy/var/log/app.log
head -c 2000000 /dev/zero > srv-copy/var/lib/db.data
head -c 1000000 /dev/zero > srv-copy/var/cache/pkgs.cache
echo small > srv-copy/var/tmp/x
du -sh srv-copy/var/* | sort -hr | head -3
''',
         notes={1: 'Brace expansion :: Four folders in one command.', 6: 'Rank :: <code>sort -hr</code> = human sizes, reversed (largest first).'},
         tryit='Make the cache 9 MB and run again. Which folder is first now?'),
]

QUIZ = mix([
    dict(q='On Linux, where do system-wide configuration files live?', options=['/usr', '/etc', '/var', '/home'], answer=1,
         why='/etc holds host configuration as text files, e.g. /etc/hostname, /etc/ssh/sshd_config.'),
    dict(q='A server’s disk is full of logs. Which folder will most likely be the biggest?', options=['/etc', '/var', '/boot', '/bin'], answer=1,
         why='Logs live in /var/log; databases and Docker data also live under /var.'),
    dict(q='What is /root?', options=['The top of the tree', 'The home folder of the root user', 'A folder of root certificates', 'The kernel'], answer=1,
         why='The top of the tree is /. /root is the administrator’s home folder.'),
    dict(q='ls -l /proc/cpuinfo shows size 0, but cat prints many lines. Why?', options=['The file is corrupted', 'procfs generates the content when it is read', 'It is compressed', 'Only root sees the size'], answer=1,
         why='Files in /proc are virtual: the kernel writes their content at read time and stores nothing.'),
    dict(q='On modern Ubuntu, /bin is…', options=['a separate folder of old programs', 'a symbolic link to /usr/bin', 'empty', 'a mount point for USB sticks'], answer=1,
         why='Merged /usr: /bin, /sbin and /lib are links into /usr.'),
    dict(q='How does a second disk appear on Linux?', options=['As drive D:', 'Mounted on a folder of the single tree, e.g. /data', 'As /dev only, never as a folder', 'It replaces /'], answer=1,
         why='Linux has no drive letters; file systems are mounted on directories.'),
    dict(q='Which folder is the right place for a website’s files that you manage yourself?', options=['/usr/share', '/var/www or /srv', '/boot', '/proc'], answer=1,
         why='/usr belongs to the package manager; your own served data goes to /var/www or /srv.'),
])

REVISION = [
    'One tree from <code>/</code>; no drive letters. Extra disks are <b>mounted</b> on folders.',
    'FHS map: <code>/etc</code> config · <code>/home</code> users · <code>/root</code> root’s home · <code>/usr</code> programs · <code>/var</code> logs and data · <code>/tmp</code> scratch.',
    '<code>/boot</code> kernel · <code>/dev</code> devices · <code>/proc</code>, <code>/sys</code> kernel info · <code>/run</code> runtime · <code>/mnt</code>, <code>/media</code> mounts · <code>/opt</code> add-ons · <code>/srv</code> served data.',
    'Merged /usr: <code>/bin → /usr/bin</code>, <code>/lib → /usr/lib</code>, <code>/sbin → /usr/sbin</code>.',
    '“Everything is a file”: one interface (open/read/write, permissions) for files, devices, pipes and kernel data, thanks to the VFS.',
    'Virtual file systems: procfs, sysfs, devtmpfs, tmpfs. Check with <code>findmnt</code> or <code>df -T</code>.',
    'An app’s places: program <code>/usr/sbin</code>, config <code>/etc/app</code>, logs <code>/var/log/app</code>, data <code>/var/lib/app</code>, PID <code>/run</code>.',
    'Disk full → <code>sudo du -sh /var/*</code> first.',
]

FAQ = [
    ('Explain the Linux directory structure.', 'A single tree rooted at /. Key folders: /bin and /sbin (commands, now links into /usr), /boot (kernel), /dev (devices), /etc (configuration), /home (users), /lib (libraries), /media and /mnt (mount points), /opt (add-on software), /proc and /sys (kernel information), /root (root’s home), /run (runtime data), /srv (served data), /tmp (temporary), /usr (installed software), /var (variable data such as logs).'),
    ('What does “everything is a file” mean in Linux?', 'Files, directories, devices, pipes, sockets and kernel interfaces are all accessed with the same file operations (open, read, write, close) and permission model. The kernel’s virtual file system routes each request to the right driver or file system.'),
    ('What is the difference between / and /root?', '/ is the root directory, the top of the whole tree. /root is the home directory of the root (administrator) user.'),
    ('What is the difference between /tmp and /var/tmp?', 'Both are for temporary files. /tmp may be cleared at every reboot (and is often in RAM); /var/tmp is kept across reboots and cleaned less often.'),
    ('What is /proc?', 'A virtual file system generated by the kernel. It has one folder per process (by PID) and files with system information such as /proc/cpuinfo, /proc/meminfo and /proc/loadavg. It uses no disk space.'),
    ('Why does Linux have no drive letters?', 'Linux uses a single tree. Each storage device or partition is mounted on a directory, so applications use paths that stay the same even if the storage underneath changes.'),
]

PRACTICE_INTRO = 'Tasks that use only the tree and the commands you know. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Is it a folder or a link?', stmt='For <code>/bin</code>, <code>/usr</code> and <code>/etc</code>, print whether each is a link or a directory.', inp='/bin /usr /etc',
         code='for d in /bin /usr /etc; do\n  if [ -L "$d" ]; then echo "$d is a link"; else echo "$d is a directory"; fi\ndone\n', explain='<code>-L</code> tests for a symbolic link. On merged-/usr systems /bin is a link.'),
    dict(level='easy', title='Count installed commands', stmt='Print how many entries are in <code>/usr/bin</code>.', inp='/usr/bin',
         code='echo "Commands in /usr/bin: $(ls /usr/bin | wc -l)"\n', explain='Every command you can type lives somewhere in PATH; most are in /usr/bin. (The number depends on what is installed.)'),
    dict(level='easy', title='Read a virtual file', stmt='Print the number of CPU cores using only <code>/proc/cpuinfo</code>.', inp='/proc/cpuinfo',
         code="echo \"CPU cores: $(grep -c '^processor' /proc/cpuinfo)\"\n", explain='Each core has a block starting with “processor”; <code>grep -c</code> counts the matching lines.'),
    dict(level='medium', title='Build a standard app layout', stmt='Create the folders <code>etc/api</code>, <code>var/log/api</code> and <code>var/lib/api</code> in one command and list all directories under <code>.</code> sorted.', inp='(nothing)',
         code='mkdir -p etc/api var/log/api var/lib/api\nfind . -type d | sort\n', explain='<code>-p</code> creates parents; <code>find -type d</code> lists directories only.'),
    dict(level='medium', title='Disk or RAM?', stmt='Print the file-system type of <code>/</code> and of <code>/dev/shm</code>.', inp='/ and /dev/shm',
         code='echo "/ is $(findmnt -n -o FSTYPE /)"\necho "/dev/shm is $(findmnt -n -o FSTYPE /dev/shm | head -1)"\n', explain='ext4 means a real disk; tmpfs means files kept in memory.'),
    dict(level='medium', title='Newest log files', stmt='In a sample <code>log</code> folder with three files created one after another, print the newest file’s name.', inp='a.log, b.log, c.log (created in that order)',
         code='mkdir log\nfor f in a b c; do echo x > log/$f.log; sleep 1; done\nls -t log | head -1\n', explain='<code>ls -t</code> sorts by modification time, newest first.'),
    dict(level='business', title='Config backup list', stmt='Before an upgrade, the team wants a list of every <code>.conf</code> file directly inside <code>/etc</code> (not sub-folders), sorted, and how many there are.', inp='/etc',
         code="ls /etc/*.conf | sort | head -5\necho \"Total .conf files in /etc: $(ls /etc/*.conf | wc -l)\"\n", explain='The wildcard <code>/etc/*.conf</code> matches files ending in .conf at that level only. (First 5 shown.)'),
    dict(level='business', title='Where should each file go?', stmt='Given file types from a new app, print the standard folder for each: config → /etc, log → /var/log, data → /var/lib, program → /usr/bin, temporary → /tmp.', inp='config log data program temporary',
         code="for kind in config log data program temporary; do\n  case $kind in\n    config) dir=/etc ;; log) dir=/var/log ;; data) dir=/var/lib ;;\n    program) dir=/usr/bin ;; temporary) dir=/tmp ;;\n  esac\n  echo \"$kind -> $dir\"\ndone\n",
         explain='A small lookup with <code>case</code>. Installers and packaging tools follow exactly this FHS mapping.'),
]

SCN_INTRO = 'Interview questions about the Linux tree, as asked for support, DevOps and data engineering roles.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Where would you find …?”',
        'The interviewer fires quick questions: where is the SSH server config, where are system logs, where is a user’s home, where is the kernel?',
        'do you know the FHS map by heart?',
        '''<ul>
          <li>SSH server config: <code>/etc/ssh/sshd_config</code>.</li>
          <li>System logs: <code>/var/log/</code> (syslog or messages, auth.log or secure), plus <code>journalctl</code>.</li>
          <li>User homes: <code>/home/&lt;user&gt;</code>; root’s home is <code>/root</code>.</li>
          <li>Kernel: <code>/boot/vmlinuz-&lt;version&gt;</code>; running version from <code>uname -r</code>.</li>
        </ul>''', 'guessing paths from Windows habits (“Program Files”).') +
    scn('Operations · incident', 'Junior', 'Disk full at 2 a.m.',
        'You get paged: “/ is at 100% on app-01”. Walk through what you do.',
        'is your approach systematic and safe?',
        '''<ol>
          <li>Confirm with <code>df -h</code>; find the big folders with <code>sudo du -xsh /* | sort -h</code>, then go deeper (usually <code>/var/log</code>, <code>/var/lib/docker</code>).</li>
          <li>Free space safely: compress or truncate an oversized log the app holds open (<code>truncate -s 0</code>), clean package caches; do not delete files in <code>/usr</code> or databases.</li>
          <li>Check that deleted-but-open files are released (<code>lsof +L1</code>), then fix the cause: logrotate, retention, alerts at 80%.</li>
        </ol>''', '“rm -rf the biggest folder”.') +
    scn('Platform team · concepts', 'Mid-level', '“What does everything is a file mean in practice?”',
        'The interviewer asks for practical examples, not the slogan.',
        'can you connect the principle to tools you use?',
        '''<ul>
          <li><code>cat /proc/meminfo</code> or <code>/proc/&lt;pid&gt;/status</code>: monitoring tools are just reading files.</li>
          <li><code>command 2>/dev/null</code>: writing to a device file to discard output.</li>
          <li><code>dd if=/dev/zero of=test bs=1M count=100</code>: reading a device like a file; disks are <code>/dev/sda</code>.</li>
          <li>Pipes and sockets use the same read/write calls, which is why small tools can be joined with <code>|</code>.</li>
        </ul>''', 'repeating the slogan without examples.') +
    scn('Data engineering · design', 'Mid-level', 'Where should the data go?',
        'Your team is setting up a Linux VM for a data pipeline: code, configuration, input files, logs and a local database. Propose a folder layout.',
        'do you apply the FHS sensibly?',
        '''<ul>
          <li>Code (installed release): <code>/opt/pipeline/</code> or a package; configuration: <code>/etc/pipeline/</code>; logs: <code>/var/log/pipeline/</code>; database: <code>/var/lib/pipeline/</code>.</li>
          <li>Large input data: a separate disk mounted at <code>/data</code>, so it can grow or move without touching the OS disk.</li>
          <li>Temporary working files: <code>/var/tmp</code> or a scratch folder on <code>/data</code>, not <code>/tmp</code> if they must survive reboots.</li>
        </ul>''', 'putting everything in the home folder of whoever set it up.')
) + teaser('2.2', 'Riya is deep inside <code>/var/log/nginx</code>. With just two letters and Enter, how can she jump straight back to her home folder?')

MINDMAP = mindmap('The Linux tree', [
    ('One tree', 'acc', ['starts at / (root)', 'no C: or D:', 'disks are mounted']),
    ('Config & users', 'blue', ['/etc = config (text)', '/home = users', '/root = root’s home']),
    ('Programs', 'violet', ['/usr/bin, /usr/lib', '/bin → /usr/bin', '/opt, /usr/local']),
    ('Data that grows', 'amber', ['/var/log = logs', '/var/lib = data', '/tmp = scratch']),
    ('Virtual folders', 'green', ['/proc = processes', '/sys = devices', '/dev = device files']),
    ('Everything is a file', 'red', ['same open/read/write', 'VFS routes requests', 'findmnt, df -T']),
])
