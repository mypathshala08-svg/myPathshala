import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# ---------------------------------------------------------------- 0. concept map
cmap = concept_map(
    [('1.1', 'Files, folders, paths', 'the basic words'), ('1.6', 'The prompt', 'typing commands')],
    ['one tree from / (no C: or D:)', 'what each top-level folder is for', 'everything is a file', 'real vs virtual file systems', 'where an app keeps config, logs and data'],
    [('2.2', 'pwd, cd and ls', 'move around the tree'), ('2.3', 'Paths', 'absolute vs relative'), ('15.3', 'Mounting', 'attach disks to the tree'), ('20.2', '/proc and /sys', 'the kernel as files')],
    'Every later module refers to these folders: /etc (configs), /var/log (logs), /home (users), /proc (processes), /dev (devices).')

# ---------------------------------------------------------------- 1. story
tree_nodes = [('/', 300, 20, 'acc'), ('etc', 40, 80, 'blue'), ('home', 120, 80, 'green'), ('var', 200, 80, 'amber'), ('usr', 280, 80, 'violet'), ('tmp', 360, 80, 'card'), ('dev', 440, 80, 'red'), ('proc', 520, 80, 'blue')]
sc = ''
for name, x, y, tone in tree_nodes:
    if name != '/':
        sc += f'<path d="M330 50 L{x + 30} {y}" class="s-line" style="fill:none;stroke-width:1.4"/>'
for name, x, y, tone in tree_nodes:
    sc += label_box(x, y, 60, 26, [name], tone, 9.4)
sc += (t(70, 124, 'configs', 8, 'ink2') + t(150, 124, 'users', 8, 'ink2') + t(230, 124, 'logs, data', 8, 'ink2') + t(310, 124, 'programs', 8, 'ink2')
       + t(390, 124, 'scratch', 8, 'ink2') + t(470, 124, 'devices', 8, 'ink2') + t(550, 124, 'processes', 8, 'ink2')
       + t(600, 34, 'No C:, no D:', 9, 'red', anchor='end', bold=True))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Where is the C: drive?”</h2>
  <div class="story">
''' + puzzle('On Linux you can <code>cat</code> a text file, but also your CPU’s details, your disk and even the program that is reading. How can a running program or a piece of hardware be “a file”?') + '''
    <p class="narration">Neha asks Riya to “check the nginx config and the error log on app-01”. Riya logs in and types <code>cd C:</code>. Nothing. She lists the top of the system and sees short, strange names: etc, var, usr, proc, dev. No drives, no “Program Files”, no “My Documents”.</p>
''' + scene('The Linux tree: one root / with folders etc, home, var, usr, tmp, dev and proc, each labelled with its job.', sc,
            'Linux has <tspan font-weight="700" class="s-acc">one tree</tspan>, starting at /. Every disk, device and setting lives somewhere inside it.') + '''
R> Sir, there is no C: drive! Where are the programs? Where did nginx put its settings?
A> Linux has a single tree that starts at <code>/</code>, called root. There are no drive letters: a second disk is simply attached to some folder of the tree. And the folder names are a standard: settings are always in <code>/etc</code>, logs in <code>/var/log</code>, users in <code>/home</code>.
K> That’s the best part. Once you know the map, every Linux server feels familiar. nginx’s config is in <code>/etc/nginx</code>, its log in <code>/var/log/nginx</code>, on almost any distro.
R> And what are proc and dev? They don’t sound like folders.
A> They are the strangest and most powerful part: windows into the kernel and the hardware, shown as files. Linux follows one big idea from Unix: <b>everything is a file</b>. Let’s walk through the whole map, and you will see why that idea is so useful.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
school = ('<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="The Linux tree drawn as a school building: one main gate is /, the staff room is /etc, the classrooms or lockers are /home, the store room is /var, the library is /usr, the rough notice board is /tmp, and the electricity room is /dev.">'
          + label_box(250, 10, 140, 34, ['Main gate = /', 'everything is inside'], 'acc', 9)
          + ''.join(label_box(10 + k * 125, 74, 115, 54, [a, b, c], tone, 8.6) for k, (a, b, c, tone) in enumerate([
              ('Staff room', '/etc', 'rules & settings', 'blue'), ('Lockers', '/home', 'each student’s own', 'green'),
              ('Store room', '/var', 'registers, records', 'amber'), ('Library', '/usr', 'books = programs', 'violet'), ('Notice board', '/tmp', 'wiped regularly', 'card')]))
          + ''.join(f'<path d="M320 44 L{67 + k * 125} 74" class="s-line" style="fill:none"/>' for k in range(5))
          + label_box(130, 150, 170, 44, ['Electricity room = /dev', 'switches for every device'], 'red', 8.6)
          + label_box(340, 150, 170, 44, ['Principal’s live board = /proc', 'what is happening right now'], 'blue', 8.6)
          + '<text x="632" y="214" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('The Linux tree at four depths', [
    ('v', 'No jargon: a school building with one gate', '''      <p>Picture the whole Linux system as one school building. There is only one main gate, and every room has a fixed job, the same in every school.</p>''' + school + '''
      <ul>
        <li>The main gate is <code>/</code> (“root”). Everything is somewhere inside it. There is no second building called D:.</li>
        <li>Settings live in the staff room (<code>/etc</code>); each person’s own things in their locker (<code>/home/riya</code>); records and logs in the store room (<code>/var</code>); programs in the library (<code>/usr</code>).</li>
        <li>Because every Linux “school” uses the same rooms, you can walk into any Linux server and find things.</li>
      </ul>'''),
    ('b', 'The main folders and their jobs', '''      <ul>
        <li><code>/etc</code>: configuration files, as plain text. <code>/etc/hostname</code>, <code>/etc/passwd</code>, <code>/etc/nginx/nginx.conf</code>.</li>
        <li><code>/home</code>: one folder per user (<code>/home/riya</code>); <code>/root</code> is the administrator’s home.</li>
        <li><code>/var</code>: data that grows: <code>/var/log</code> (logs), <code>/var/lib</code> (databases, package lists), <code>/var/cache</code>.</li>
        <li><code>/usr</code>: installed programs and libraries: <code>/usr/bin</code> (commands), <code>/usr/lib</code>, <code>/usr/share</code> (docs, icons).</li>
        <li><code>/tmp</code>: temporary files for everyone, may be cleared at reboot.</li>
        <li><code>/dev</code>: devices (disks, terminals); <code>/proc</code> and <code>/sys</code>: live information from the kernel; <code>/boot</code>: the kernel itself.</li>
      </ul>'''),
    ('i', 'The FHS, merged /usr and why /var fills up', '''      <ul>
        <li>The layout follows the <b>Filesystem Hierarchy Standard (FHS)</b>, so tools, packages and admins agree where things go.</li>
        <li><b>Merged /usr</b>: on current Ubuntu, Debian, Fedora and RHEL, <code>/bin</code>, <code>/sbin</code> and <code>/lib</code> are links to <code>/usr/bin</code>, <code>/usr/sbin</code> and <code>/usr/lib</code>. Old scripts using <code>/bin/bash</code> still work.</li>
        <li>Rule of thumb: <code>/usr</code> is changed only by the package manager; <code>/etc</code> by admins; <code>/var</code> by running programs; <code>/home</code> by users. <code>/usr/local</code> and <code>/opt</code> hold software installed by hand.</li>
        <li>“Disk full” on a server is usually <code>/var</code>: logs (<code>/var/log</code>), Docker images (<code>/var/lib/docker</code>) or package caches.</li>
        <li><code>/tmp</code> is writable by everyone but has the <b>sticky bit</b>: you can delete only your own files there (Lesson 9.4).</li>
      </ul>'''),
    ('a', 'One tree, many file systems, all through the VFS', '''      <ul>
        <li>The tree is assembled from <b>mounts</b>: the root file system (ext4 or xfs on disk) plus others attached on folders: <code>/proc</code> (procfs), <code>/sys</code> (sysfs), <code>/dev</code> (devtmpfs), <code>/run</code> and often <code>/tmp</code> (tmpfs, in RAM), USB sticks (vfat), network shares (nfs). <code>findmnt</code> shows the mount tree.</li>
        <li>The kernel’s <b>virtual file system</b> (VFS, Lesson 1.2) gives all of them the same operations, so <code>cat</code> works the same on a disk file, a kernel statistic or a device.</li>
        <li><b>Everything is a file</b> means: one interface (open, read, write, close, permissions) for documents, directories, devices (<code>/dev/sda</code>, <code>/dev/null</code>), pipes, sockets and kernel data. What is behind each name is decided by its inode type and the file system it lives on.</li>
        <li><code>/proc/self</code> always points to the process that is reading it: <code>ls -l /proc/self/exe</code> shows the program running that very command.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>The Linux directory hierarchy and “everything is a file”</h2>
''' + def_block(
    'The <b>Linux directory hierarchy</b> is a single tree of directories rooted at <code>/</code>, whose top-level layout is defined by the <b>Filesystem Hierarchy Standard (FHS)</b>: for example <code>/etc</code> for host configuration, <code>/home</code> for user data, <code>/usr</code> for installed software, <code>/var</code> for variable data and <code>/tmp</code> for temporary files. Additional storage devices and virtual file systems are <b>mounted</b> onto directories of this tree. <b>“Everything is a file”</b> is the Unix design principle that files, directories, devices, pipes, sockets and kernel interfaces are all accessed through the same file operations and permission model.',
    'Linux keeps everything in one tree that starts at <code>/</code>. Each top-level folder has a standard job. And almost everything, even devices and running programs, shows up as a file you can read with ordinary commands.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('/ (root directory)', f'Top of the one tree. {gl("root-directory", "Glossary →")}'),
    ('FHS', f'The standard map of folders. {gl("file-system-hierarchy-fhs", "Glossary →")}'),
    ('/etc', f'Configuration files, as text. {gl("etc", "Glossary →")}'),
    ('/var', f'Logs and data that grow. {gl("var", "Glossary →")}'),
    ('/usr', f'Installed programs and libraries. {gl("usr-bin-and-sbin", "Glossary →")}'),
    ('/home and ~', f'Users’ own folders. {gl("home-and", "Glossary →")}'),
    ('/tmp', f'Shared scratch space. {gl("tmp", "Glossary →")}'),
    ('/dev', f'Device files. {gl("dev", "Glossary →")}'),
    ('/proc and /sys', f'Kernel information as files. {gl("proc", "Glossary →")}'),
    ('Mount point', f'A folder where another file system is attached. {gl("mount-and-mount-point", "Glossary →")}'),
]) + '\n' + names('The top-level names are short and old. Here is what they meant, and a hook to remember each.', [
    ('etc', '“et cetera”', 'Originally “everything else”; today it means configuration.'),
    ('usr', 'user → Unix system resources', 'Once held users’ files; now programs. “Unix System Resources” is a later backronym.'),
    ('var', 'variable', 'Data that varies (grows) while the system runs.'),
    ('tmp', 'temporary', 'Scratch space, may vanish at reboot.'),
    ('bin / sbin', 'binaries / system binaries', 'Programs for everyone / for the administrator.'),
    ('dev', 'devices', 'One file per device.'),
    ('proc', 'processes', 'One folder per running process, plus kernel data.'),
    ('opt', 'optional', 'Add-on software from vendors.'),
    ('srv', 'served', 'Data this machine serves, e.g. a website.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('How many trees?', 'One, starting at <code>/</code>; no drive letters'),
    ('Standard', 'Filesystem Hierarchy Standard (FHS), maintained by the Linux Foundation'),
    ('Config files', 'Plain text in <code>/etc</code>; about 150–250 entries on a typical Ubuntu system'),
    ('Merged /usr', '<code>/bin → /usr/bin</code>, <code>/lib → /usr/lib</code>, <code>/sbin → /usr/sbin</code> on modern distros'),
    ('Virtual file systems', '<code>/proc</code> (procfs), <code>/sys</code> (sysfs), <code>/dev</code> (devtmpfs), <code>/run</code> (tmpfs)'),
    ('root vs /root', '<code>/</code> is the root <i>directory</i>; <code>/root</code> is the root <i>user’s</i> home'),
]) + '\n' + lv + didyou('<code>/proc/self</code> is a link that points to whichever process is reading it. Run <code>ls -l /proc/self/exe</code> and it shows <code>/usr/bin/ls</code>, because ls is the process that asked. Run <code>cat /proc/self/status | head -1</code> and it says <code>Name: cat</code>.') + '''
EXAM> “Explain the Linux file system hierarchy” → draw the tree from / with at least 10 directories and one line each (/bin, /boot, /dev, /etc, /home, /lib, /media, /mnt, /opt, /proc, /root, /tmp, /usr, /var); mention the FHS, that there are no drive letters (devices are mounted), and the meaning of “everything is a file”.
''' + qc('Your colleague says “I put the file in root.” Which two places could that mean?', '<code>/</code>, the root <b>directory</b> at the top of the tree, or <code>/root</code>, the home folder of the root <b>user</b>. Always ask, and say “slash” for <code>/</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The top-level folders, one by one</h2>
''' + table(['Folder', 'What lives there', 'Examples', 'Who changes it'], [
    ['<code>/</code>', 'The root of the tree', 'everything', '—'],
    ['<code>/etc</code>', 'Configuration (text files)', '<code>hostname</code>, <code>passwd</code>, <code>ssh/sshd_config</code>, <code>nginx/</code>', 'Admins, packages'],
    ['<code>/home</code>', 'Users’ personal folders', '<code>/home/riya/projects</code>', 'Each user'],
    ['<code>/root</code>', 'Home of the root user', '<code>/root/.bashrc</code>', 'root'],
    ['<code>/usr</code>', 'Installed programs, libraries, docs', '<code>/usr/bin/ls</code>, <code>/usr/lib</code>, <code>/usr/share/doc</code>', 'Package manager'],
    ['<code>/usr/local</code>, <code>/opt</code>', 'Software installed by hand or by vendors', '<code>/opt/google/chrome</code>', 'Admins'],
    ['<code>/bin</code>, <code>/sbin</code>, <code>/lib</code>', 'Links into <code>/usr</code> (merged /usr)', '<code>/bin/bash</code>', 'Package manager'],
    ['<code>/var</code>', 'Data that grows: logs, databases, caches, mail', '<code>/var/log/syslog</code>, <code>/var/lib/mysql</code>', 'Running programs'],
    ['<code>/tmp</code>', 'Temporary files for everyone', 'downloads in progress, build files', 'Everyone (own files only)'],
    ['<code>/boot</code>', 'Kernel and boot loader files', '<code>vmlinuz-…</code>, <code>grub/</code>', 'Package manager'],
    ['<code>/dev</code>', 'Device files', '<code>/dev/sda</code>, <code>/dev/null</code>, <code>/dev/tty</code>', 'The kernel (udev)'],
    ['<code>/proc</code>, <code>/sys</code>', 'Live kernel and process information', '<code>/proc/cpuinfo</code>, <code>/sys/class/net</code>', 'The kernel'],
    ['<code>/run</code>', 'Runtime data since this boot (PIDs, sockets)', '<code>/run/sshd.pid</code>', 'Running programs'],
    ['<code>/mnt</code>, <code>/media</code>', 'Mount points for extra disks and USB sticks', '<code>/media/riya/USB</code>', 'Admins, desktop'],
    ['<code>/srv</code>', 'Data served by this machine', '<code>/srv/www</code>', 'Admins'],
    ['<code>/lost+found</code>', 'Pieces recovered by fsck after a crash', '(normally empty)', 'fsck'],
], minw=700) + '''

  <h3>Real files and virtual files</h3>
''' + cards([
    ('Files on disk', 'Your documents, configs in /etc, programs in /usr. Stored in blocks on an SSD, kept after power-off.', 'ext4, xfs'),
    ('Kernel windows', 'Files in /proc and /sys are generated by the kernel the moment you read them. They take no disk space.', 'procfs, sysfs'),
    ('Device files', 'Names in /dev that lead to drivers: reading /dev/sda reads the disk; writing to /dev/null throws data away.', 'devtmpfs'),
    ('RAM-only folders', '/run (and on many systems /tmp) live in memory and start empty at every boot.', 'tmpfs'),
]) + didyou('The Linux tree is one tree, but its branches can live on very different things: an SSD, RAM, the kernel itself, a USB stick or a server in another city. You cannot tell from the path; <code>findmnt</code> or <code>df -T</code> tells you.') + qc('A teammate filled the disk with logs. Which top-level folder will you check first?', '<code>/var</code>, especially <code>/var/log</code> (and <code>/var/lib/docker</code> if Docker is used). <code>sudo du -sh /var/*</code> shows which part is big.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Find where an application keeps everything</h2>
  <p>A routine you will use on every server: map one application (here nginx) onto the tree.</p>
''' + stepper([
    ('1. Where is the program?', '<p><code>command -v nginx</code> → <code>/usr/sbin/nginx</code>.</p>', 'Behind the screen: the shell searches the folders in PATH; package-managed programs live under /usr.'),
    ('2. Where is its configuration?', '<p><code>ls /etc/nginx</code> → <code>nginx.conf</code>, <code>sites-available/</code>…</p>', 'Behind the screen: by FHS rules, host-specific settings go to /etc, as plain text you can read and back up.'),
    ('3. Where are its logs?', '<p><code>ls /var/log/nginx</code> → <code>access.log</code>, <code>error.log</code>.</p>', 'Behind the screen: logs grow, so they belong in /var; logrotate keeps them small (Lesson 18.2).'),
    ('4. Where is its data?', '<p>Web pages in <code>/var/www/html</code> (or <code>/srv</code>); a database such as MySQL keeps data in <code>/var/lib/mysql</code>.</p>', 'Behind the screen: /var/lib holds the state programs need to keep between restarts.'),
    ('5. Where is it at run time?', '<p>Its process ID file in <code>/run/nginx.pid</code>; the process itself under <code>/proc/&lt;PID&gt;</code>.</p>', 'Behind the screen: /run is a RAM file system emptied at each boot; /proc is generated by the kernel.'),
    ('6. Which package put it there?', '<p><code>dpkg -S /usr/sbin/nginx</code> (Ubuntu) or <code>rpm -qf</code> (RHEL).</p>', 'Behind the screen: the package database records every file each package installed (Lesson 14.2).'),
]) + qc('Riya edited <code>/usr/share/nginx/html/index.html</code> by hand, and the next package update overwrote her changes. Which folder rule did she break?', '<code>/usr</code> belongs to the package manager. Her own content should go in <code>/var/www</code> or <code>/srv</code>, and her settings in <code>/etc</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
see = [term(20, 18, 320, 130, ['$ cat /etc/hostname', ('app-01', 'out')]) + t(180, 172, 'One file looks like any text file.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ cat /etc/hostname', ('app-01', 'out'), '$ grep -m1 "model name" /proc/cpuinfo', ('model name : Intel(R) Xeon(R) ...', 'out')]) + t(180, 172, 'So does this one.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ ls -l /etc/hostname /proc/cpuinfo', ('-rw-r--r-- 1 root root 7 ... /etc/hostname', 'out'), ('-r--r--r-- 1 root root 0 ... /proc/cpuinfo', 'acc')]) + t(180, 172, 'But cpuinfo has size 0!', 9, 'red', bold=True),
       term(20, 18, 320, 130, ['$ df -T /etc /proc | cut -c1-30', ('Filesystem Type', 'out'), ('/dev/vda   ext4', 'out'), ('proc       proc', 'acc')]) + t(180, 172, 'They live on different file systems.', 9, 'ink2'),
       term(20, 18, 320, 130, ['$ ls -l /proc/self/exe', ('/proc/self/exe -> /usr/bin/ls', 'acc')]) + t(180, 172, 'And /proc even knows who is asking.', 9, 'green', bold=True)]
def vfs(hl, right):
    o = label_box(130, 12, 100, 30, ['cat (program)'], 'card', 8.8) + arrow(180, 44, 180, 58, 'ink3', 1.4)
    o += label_box(100, 60, 160, 30, ['VFS (kernel)'], 'blue' if 'vfs' in hl else 'card', 9)
    o += arrow(150, 92, 70, 112, 'ink3', 1.4) + arrow(210, 92, 290, 112, 'ink3', 1.4)
    o += label_box(10, 114, 120, 34, ['ext4 driver', '→ SSD blocks'], 'green' if 'ext4' in hl else 'card', 8.6)
    o += label_box(230, 114, 120, 34, ['procfs', '→ made in RAM now'], 'acc' if 'proc' in hl else 'card', 8.6)
    return o + right
behind = [vfs(['vfs', 'ext4'], t(180, 176, '/etc/hostname: VFS asks ext4, which reads 7 bytes from disk.', 8.6, 'ink2')),
          vfs(['vfs', 'proc'], t(180, 176, '/proc/cpuinfo: VFS asks procfs, which writes the text now.', 8.6, 'ink2')),
          vfs(['proc'], t(180, 176, 'Nothing is stored, so its size is 0 until you read it.', 8.6, 'red', bold=True)),
          vfs(['ext4', 'proc'], t(180, 176, 'Two file systems mounted in one tree: / and /proc.', 8.6, 'ink2')),
          vfs(['vfs', 'proc'], t(180, 176, 'procfs builds /proc/self for the process asking: ls.', 8.6, 'green', bold=True))]
two = anim_two('cat a real and a virtual file', 'Same command, two very different files', 'A terminal reading /etc/hostname and /proc/cpuinfo, showing size 0 for cpuinfo and /proc/self/exe pointing to ls.',
               'cat goes through the kernel VFS to the ext4 driver for /etc/hostname and to procfs for /proc/cpuinfo.', see, behind,
               ['<code>cat /etc/hostname</code> prints the machine name. An ordinary text file.',
                '<code>/proc/cpuinfo</code> is read the same way and prints CPU details.',
                'But <code>ls -l</code> says <code>/proc/cpuinfo</code> has <b>size 0</b>. How can a file with nothing in it print so much?',
                '<code>df -T</code> shows why: <code>/etc</code> is on the disk (ext4), <code>/proc</code> is a different file system called proc.',
                '<code>/proc/self</code> points to whichever process reads it, here ls. (Outputs shortened; host name is an example.)'],
               ['cat asks the kernel to open and read <code>/etc/hostname</code>. The VFS sees it lives on ext4 and lets the ext4 driver read 7 bytes from the SSD.',
                'For <code>/proc/cpuinfo</code> the VFS hands the request to <b>procfs</b>, which asks the kernel for CPU information and writes it as text, right now.',
                'Nothing is stored anywhere, so the file’s size is reported as 0. The content exists only while you read it.',
                'The tree is built from several mounted file systems. Programs never need to know which one they are using: “everything is a file”.',
                'Because procfs generates content per reader, <code>/proc/self</code> can be different for every process. ps, top and free are built on these files.'])

# scenario 1: disk full -> /var
def dbar(rows, cap1, cap2, tone):
    return bars(rows, y=30) + cap(cap1, cap2, tone, y=150, h=44)
d1 = dbar([('/  (whole disk)', 97, 'red', '97% full')], 'An alert: app-01’s disk is 97% full.', 'Payments may start failing when it hits 100%.', 'red')
d2 = dbar([('/usr', 18, 'green', '4.1G'), ('/home', 6, 'green', '1.2G'), ('/var', 90, 'red', '61G'), ('/opt', 4, 'green', '0.8G')], 'sudo du -sh /*  (sizes are an example)', '/var is the giant.', 'blue')
d3 = dbar([('/var/lib', 10, 'green', '3.0G'), ('/var/cache', 5, 'green', '1.1G'), ('/var/log', 88, 'red', '56G')], 'Inside /var: the logs.', '', 'blue')
d4 = dbar([('app/debug.log', 85, 'red', '52G'), ('syslog', 6, 'green', '1.9G')], 'One debug log left switched on for a week.', '', 'amber')
d5 = (t(180, 30, 'The fix and the habit', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Compress or truncate the log, turn debug off.', '• Set up logrotate for the app (Lesson 18.2).', '• Know the map: disk full → look in /var first.'])) + cap('The tree told them exactly where to look.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Disk 97% full: the map tells you where to look',
              'Because every Linux server uses the same layout, finding what filled a disk takes minutes. Sizes are illustrative.',
              'Following the tree to the problem', 'Bars showing disk usage per top-level folder, then inside /var, then a single huge log file.', [d1, d2, d3, d4, d5],
              ['The monitoring system warns that app-01’s disk is 97% full.',
               '<code>sudo du -sh /*</code> sizes each top-level folder. <code>/var</code> is far bigger than anything else.',
               'Inside <code>/var</code>, <code>/var/log</code> holds almost everything.',
               'One application log, left in debug mode, has grown to 52 GB.',
               'The team turns debug off, compresses the log and adds log rotation. Knowing the tree made the search fast.'],
              hid='scenario-diskfull')

# scenario 2: one app across the tree
appmap = [('/usr/sbin/nginx', 'program', 'violet'), ('/etc/nginx/', 'configuration', 'blue'), ('/var/log/nginx/', 'logs', 'amber'), ('/var/www/html/', 'web pages', 'green'), ('/run/nginx.pid', 'running PID', 'acc')]
def amap(n, c1, c2):
    o = label_box(130, 10, 100, 30, ['nginx'], 'red', 10)
    for k in range(n):
        p_, w, tone = appmap[k]
        y = 52 + k * 19
        o += t(30, y + 4, p_, 8.4, 'ink', anchor='start', mono=True) + t(250, y + 4, w, 8.4, tone, anchor='start', bold=True)
    return o + cap(c1, c2, 'blue', y=154, h=44)
a1 = amap(1, 'The program: /usr/sbin/nginx (installed by the package).', '')
a2 = amap(2, 'Its settings: /etc/nginx/ (text you edit).', '')
a3 = amap(3, 'Its logs: /var/log/nginx/ (grow over time).', '')
a4 = amap(4, 'Its content: /var/www/html/ (your website).', '')
a5 = amap(5, 'While running: /run/nginx.pid, and /proc/<PID>/.', 'The same pattern fits MySQL, SSH, Docker…')
s2 = anim_one('Real-time scenario 2', 'One application, five places in the tree',
              'Neha’s request was “check nginx’s config and error log”. The FHS says exactly where each part of an application goes, on almost every distro.',
              'An application mapped onto the tree', 'The nginx program, configuration, logs, web content and PID file at their standard paths.', [a1, a2, a3, a4, a5],
              ['The program file sits in <code>/usr/sbin</code>, put there by the package manager.',
               'Its configuration is in <code>/etc/nginx</code>: plain text files the admin edits.',
               'Its logs go to <code>/var/log/nginx</code>: access.log and error.log.',
               'The website itself is in <code>/var/www/html</code> by default on Ubuntu.',
               'While it runs, its process ID is in <code>/run/nginx.pid</code> and the kernel shows the process under <code>/proc</code>. MySQL, SSH and Docker follow the same pattern.'],
              hid='scenario-appmap')

# scenario 3: a new disk becomes a folder
m1 = label_box(14, 20, 150, 50, ['/ (root disk)', '/dev/vda, 50 GB'], 'green', 9) + label_box(196, 20, 150, 50, ['new cloud disk', '/dev/vdb, 500 GB'], 'card', 9) + cap('A 500 GB disk is added to the server for data.', 'Windows would call it D:. Linux has no letters.', 'card', y=150, h=44)
m2 = label_box(14, 20, 150, 50, ['/ (root disk)', '/dev/vda, 50 GB'], 'green', 9) + label_box(196, 20, 150, 50, ['/dev/vdb', 'formatted ext4'], 'blue', 9) + cap('The admin creates a file system on it (Lesson 15.2).', '', 'blue', y=150, h=34)
m3 = label_box(14, 20, 150, 50, ['/ (root disk)', '… /data (empty folder)'], 'green', 9) + label_box(196, 20, 150, 50, ['/dev/vdb', 'ext4'], 'blue', 9) + arrow(196, 45, 166, 45, 'acc', 2.2) + t(180, 96, 'sudo mount /dev/vdb /data', 9, 'acc', mono=True, bold=True) + cap('mount attaches it to the folder /data.', '', 'blue', y=150, h=34)
m4 = term(14, 14, 332, 100, ['$ df -h /data', ('Filesystem  Size  Used Avail  Mounted on', 'out'), ('/dev/vdb    492G   28K  467G  /data', 'out')], title='riya@app-01', size=7.8) + cap('Now /data is the new disk. Paths stay the same for apps.', '(Sizes are an example.)', 'green', y=150, h=44)
m5 = (t(180, 30, 'Why one tree is powerful', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Apps just use paths; storage can change underneath.', '• Move /var/lib/mysql to a bigger disk: same path.', '• /etc/fstab makes the mount permanent (Lesson 15.3).'])) + cap('Disks are branches of the tree, not letters.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'A new disk becomes a folder, not a drive letter',
              'The database needs more space. Watch how Linux adds a whole disk to the tree. Device names and sizes are examples; Module 15 does it hands-on.',
              'Mounting a disk into the tree', 'A new disk /dev/vdb is formatted and mounted on /data, then df shows it.', [m1, m2, m3, m4, m5],
              ['A new 500 GB cloud disk appears as the device <code>/dev/vdb</code>.',
               'The admin creates an ext4 file system on it.',
               '<code>mount /dev/vdb /data</code> attaches it to the empty folder <code>/data</code>.',
               '<code>df -h /data</code> confirms: everything under <code>/data</code> is now stored on the new disk.',
               'Applications only see paths, so storage can be added or moved without changing them. An entry in <code>/etc/fstab</code> keeps the mount after reboot.'],
              hid='scenario-mount')

dx = dissect('Layer by layer: one tree, many file systems',
    'The tree looks like one thing, but each branch can be a different file system. Click each one: why it exists, how it works, where it is, where you meet it, and a real check of which file system the folder really is (recorded on our build machine).', [
    dict(key='root', name='/ on disk', sub='ext4 or xfs',
         why='Programs, configs and your files must survive a reboot.',
         how='A disk partition (or cloud disk) formatted with ext4 or xfs is mounted as <code>/</code> during boot.',
         impl='A block device such as <code>/dev/vda</code> or <code>/dev/nvme0n1p2</code>.',
         used='Everything that is not one of the special folders below.',
         cmd='findmnt -n -o SOURCE,FSTYPE /'),
    dict(key='proc', name='/proc', sub='procfs: processes and kernel',
         why='Tools like ps, top and free need live information from the kernel without special system calls.',
         how='procfs creates files when they are read; one numbered folder per process.',
         impl='The kernel’s procfs (<code>fs/proc/</code> in the kernel source); takes no disk space.',
         used='ps, top, free, uptime and your own scripts (Lesson 20.2).',
         cmd='findmnt -n -o FSTYPE /proc; ls -l /proc/self/exe'),
    dict(key='sys', name='/sys', sub='sysfs: devices and drivers',
         why='The kernel’s view of devices and drivers should be browsable and, in places, changeable.',
         how='sysfs mirrors the kernel’s device model as folders: buses, classes, devices.',
         impl='The kernel’s sysfs; cgroup v2 is mounted inside it at <code>/sys/fs/cgroup</code>.',
         used='udev, systemd, container runtimes, hardware tools.',
         cmd='findmnt -n -o FSTYPE /sys; ls /sys/class | head -4'),
    dict(key='dev', name='/dev', sub='devtmpfs: device files',
         why='Programs need names for hardware: disks, terminals, random numbers.',
         how='The kernel creates device files as hardware appears; udev adds friendly names and permissions.',
         impl='devtmpfs, a RAM file system managed by the kernel and udev.',
         used='<code>/dev/null</code> in scripts, <code>/dev/sda</code> for disks, <code>/dev/pts/0</code> for terminals.',
         cmd='findmnt -n -o FSTYPE /dev; ls -l /dev/null'),
    dict(key='shm', name='/run and /dev/shm', sub='tmpfs: files in RAM',
         why='Some files are only needed while the system is running and must be fast.',
         how='tmpfs keeps files in memory (and swap); they disappear at reboot.',
         impl='tmpfs mounts; on many distros <code>/tmp</code> is tmpfs too (not on this build machine).',
         used='PID files, sockets, shared memory between processes.',
         cmd='findmnt -n -o FSTYPE /dev/shm | head -1'),
    dict(key='media', name='/media and /mnt', sub='whatever you attach',
         why='USB sticks, extra disks and network shares must appear somewhere in the one tree.',
         how='mount attaches their file system (vfat, ntfs, ext4, nfs) to a folder.',
         impl='Mount points: ordinary empty folders until something is mounted.',
         used='Data disks on servers, USB sticks on laptops, Windows drives on WSL (/mnt/c).',
         cmd='ls -ld /mnt /media'),
], hint='Each branch of the tree can be a different file system. Click one.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A real file and a virtual file, side by side</h2>
  <p>Left: what Riya sees. Right: how the kernel’s VFS sends each request to a different file system.</p>
''' + two + '''
  <p>Three real-time scenarios: a full disk, one application spread over the tree, and a new disk joining the tree.</p>
''' + s1 + s2 + s3 + dx + qc('<code>ls -l /proc/meminfo</code> shows size 0, yet <code>cat /proc/meminfo</code> prints many lines. Why?', 'Files in /proc are generated by the kernel when read; nothing is stored, so the size shown is 0.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>The tree in a working day</h2>
''' + usecase(term(8, 14, 104, 62, [('$ sudo du -sh /var/*', 'prompt'), ('56G /var/log', 'err')], title='ops', size=6.4, step=12),
              '1. Disk-full alerts', 'Operations teams follow the tree from <code>/</code> to the folder that grew, almost always under <code>/var</code>.', ['Alert', '*du on the tree', 'culprit found']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['/etc in Git', 'config backup'], 'blue', 8.6), '2. Backing up configuration',
    'Because all settings are text in <code>/etc</code>, teams back it up or keep it in Git (tools such as etckeeper) to see exactly what changed.', ['/etc', '*Git history', 'easy rollback']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-v /data', 'into container'], 'green', 8.6), '3. Containers and volumes',
    'Docker containers have their own tree; data folders from the host are mounted into it (for example <code>-v /srv/data:/data</code>).', ['Host folder', '*mount into container', 'data survives']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ cat /proc/loadavg', 'prompt'), ('0.42 0.38 0.30', 'out')], title='monitor', size=6.4, step=12),
    '4. Monitoring agents', 'Monitoring tools read <code>/proc</code> and <code>/sys</code> every few seconds to report CPU, memory, disk and network usage.', ['/proc, /sys', '*agent', 'dashboard']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['/var/lib/mysql', 'on big disk'], 'amber', 8.6), '5. Moving data to a bigger disk',
    'DBAs mount a new disk and move a database’s folder onto it; applications keep using the same path.', ['New disk', '*mount at /var/lib/mysql', 'same path']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Short explorations of the tree. All were really run on our Ubuntu 24.04 build machine (as a normal user, so some folders are not readable).', [
    dict(level='b', title='See the merged /usr for yourself', scenario='A tutorial says /bin/bash, another says /usr/bin/bash. Are they the same?',
         cmd='ls -ld /bin /sbin /lib', explain='The <code>l</code> at the start and the arrow show these are symbolic links into /usr (Lesson 10.2).'),
    dict(level='b', title='How many configuration entries are there?', scenario='Kabir wonders how much there is to configure on a fresh server.',
         cmd='ls /etc | wc -l', explain='Every name in /etc is a config file or folder. Plain text means you can read, search and back them up with normal tools.'),
    dict(level='i', title='Which file system is each folder on?', scenario='You want to know which folders are on the disk and which live in RAM or the kernel.',
         cmd='for d in / /proc /sys /dev /dev/shm; do printf "%-9s %s\\n" "$d" "$(findmnt -n -o FSTYPE --target $d | head -1)"; done',
         explain='<code>findmnt --target</code> finds the mount that contains a path; <code>-o FSTYPE</code> prints just its type.'),
    dict(level='a', title='Who is reading /proc/self?', scenario='Prove that /proc/self is different for every process.',
         cmd='ls -l /proc/self/exe; cat /proc/self/status | head -1',
         explain='The first command is run by ls, the second by cat: each sees itself. Tools such as ps read exactly these per-process files.'),
], extra=build_up('which part of /usr is the biggest?', 'Before building a slim server image, find what takes the space inside /usr.', '', [
    ('ls /usr', 'Look at the branches first.'),
    ('du -sh /usr/* 2>/dev/null', '<code>du -sh</code> = disk usage, summary, human units. <code>2>/dev/null</code> hides “permission denied” noise.'),
    ('du -sh /usr/* 2>/dev/null | sort -h', '<code>sort -h</code> understands sizes like 671M and 2.4G.'),
    ('du -sh /usr/* 2>/dev/null | sort -h | tail -2', 'Keep the two biggest: the answer.'),
], level='i')) + which('Questions about the tree, and the command that answers each.', [
    ('See the top of the tree', 'ls /', 'Lists the top-level folders.', 'Looking for C: or D:.'),
    ('Find a program’s location', 'command -v nginx', 'Shows the path the shell would run.', 'Searching the whole disk with find.'),
    ('Find what filled the disk', 'sudo du -sh /var/*', 'Sizes per folder; start at /var.', 'Deleting random files in /usr.'),
    ('See which disk a folder is on', 'df -h /data', 'Shows the file system holding that path.', 'Assuming everything is on one disk.'),
    ('See the whole mount tree', 'findmnt', 'Every mounted file system and where.', 'Reading /etc/fstab only (it lists planned, not current, mounts).'),
    ('Read live kernel information', 'cat /proc/meminfo', 'Generated on read.', 'Trying to edit files in /proc with an editor.'),
    ('Read the standard itself', 'man hier', 'The manual page describing the hierarchy.', 'Guessing what an unfamiliar folder is for.'),
]) + puzzle_answer('Because of <b>“everything is a file”</b> and the kernel’s <b>virtual file system</b>. A file name is just a door; what is behind it depends on the file system it lives on. Behind <code>/home/riya/notes.txt</code> is ext4 on the disk. Behind <code>/proc/cpuinfo</code> is procfs, which writes the CPU details the moment you read. Behind <code>/dev/sda</code> is the disk driver. And <code>/proc/self</code> is generated for whichever process is reading, so a running program really can look at itself as files.') + qc('Where would you look for SSH’s configuration and for its log of logins on Ubuntu?', 'Configuration in <code>/etc/ssh/sshd_config</code>; login records in <code>/var/log/auth.log</code> (on RHEL: <code>/var/log/secure</code>).') + '''
</section>
'''

body = (cmap + story.replace('  <div class="story">', before('<a href="../../01-start-here/06-terminal-console-shell-and-prompt-your-first/">Lesson 1.6</a>: you can type a command and read its output.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
