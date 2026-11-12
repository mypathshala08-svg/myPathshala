import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='10-links-and-inodes', lesson='01-inodes-how-linux-stores-a-file-behind-its-name', n='10.1',
    module_label='Module 10 · Inodes and links',
    title='Inodes: how Linux stores a file behind its name',
    desc='What an inode is and what it stores (everything except the name); directories as name → inode tables; ls -i, stat and its fields, df -i, du --inodes, find -inum and -samefile; link counts; why mv is instant and cp is not; sed -i changing the inode; sparse files; deleted-but-open files and lsof +L1; running out of inodes on a real 16-inode ext4 disk; debugfs and tune2fs, with real outputs and animations.',
    og_desc='Learn what an inode is, why a disk can be “full” with free space, and how Linux finds a file from its name, with real ext4 outputs.',
    minutes=40, level='Beginner → Advanced',
    lead='Every Linux file is an inode: a numbered record with its size, owner, permissions, times and data location. The name lives in the folder. This lesson shows both on a real disk and uses them to solve full disks, missing space and odd file names.',
    chips=['A real 16-inode disk', 'stat field by field', 'debugfs inside ext4', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Names and inodes
echo hello > a.txt
ls -i a.txt
cp a.txt b.txt
mv a.txt c.txt
ls -i b.txt c.txt
stat -c '%i %h %s %n' b.txt c.txt
"""

RUN = dict(
    heading='See inode numbers change (or not)',
    intro='<p>Make a file, copy it, rename it, and compare the inode numbers.</p>',
    code=MAIN,
    anno=[('mv a.txt c.txt', 'Rename: c.txt keeps the inode a.txt had.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which file has a.txt’s old number?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> does appending change the inode number? Then run.',
             code="echo one > f\nstat -c %i f\necho two >> f\nstat -c %i f\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is the link count of the folder. Add the missing option so ls shows the folder itself.',
             code="mkdir -p d/x d/y\nls -l d\n"),
        dict(label='4 · Your turn', hint='Print size and blocks of a sparse file.',
             code="truncate -s 10M s.img\nstat -c 'size=%s blocks=%b' s.img\n"),
        dict(label='5 · Challenge', hint='Find a file by its inode number and print its name.',
             code="mkdir -p z; echo x > z/target\nn=$(stat -c %i z/target)\nfind z -inum \"$n\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own inodes',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Inode usage of every disk', cmd='df -ih -x tmpfs -x squashfs', output='Filesystem     Inodes IUsed IFree IUse% Mounted on\n/dev/sda2         30M  412K   30M    2% /\n/dev/sda1           0     0     0     - /boot/efi', note='Typical. FAT (/boot/efi) has no inodes: “-”.'),
        dict(title='2 · Your home folder’s inode', cmd='stat -c "%i %h %A %n" ~', output=pc('stat -c "%i %h %A %n" ~'), note='Recorded.'),
        dict(title='3 · Inode settings of your root disk', cmd="sudo tune2fs -l $(findmnt -no SOURCE /) | grep -E 'Inode count|Free inodes|Inode size'", output='Inode count:              31227904\nFree inodes:              30816322\nInode size:               256', note='Typical, ext4 only.'),
        dict(title='4 · Deleted files still open', cmd='sudo lsof +L1 | head', output='COMMAND   PID USER  FD  TYPE DEVICE SIZE/OFF NLINK  NODE NAME\nfirefox  2210 vineeta 45u REG  0,1    65536     0 10240 /memfd:... (deleted)', note='Typical. NLINK 0 = deleted, still open.'),
    ],
)

TRACE = dict(
    heading='One file, three operations',
    intro='<p>Step through and watch which operations keep the inode number.</p>',
    code='''echo data > f
a=$(stat -c %i f)
mv f g; b=$(stat -c %i g)
cp g h; c=$(stat -c %i h)
[ "$a" = "$b" ] && echo "mv kept the inode"
[ "$a" != "$c" ] && echo "cp made a new inode"
''',
    notes={1: 'Create :: one inode.', 2: 'Save its number.', 3: 'Rename :: same inode.', 4: 'Copy :: new inode.', 6: 'Summary :: both lines print.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an admin’s full disk, a developer’s replaced config and a security check.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='Read the inode of a file',
         problem='<p>Print the inode number, link count, size and owner of a file in one line.</p>',
         inp='a file', approach=['stat -c with a format.'],
         code='''echo 'port=8080' > app.conf
stat -c 'inode=%i links=%h size=%s owner=%U' app.conf
''', notes={1: 'Create.', 2: 'Fields :: %i %h %s %U.'}, tryit='Add %y for the modify time.'),
    dict(level='i', tag='Developer', title='Edited in place or replaced?',
         problem='<p>A program watches a config file. Show which kind of edit keeps the same inode.</p>',
         inp='a config', approach=['Save the number.', 'Append, then sed -i.', 'Compare.'],
         code='''echo 'mode=dev' > c.conf; a=$(stat -c %i c.conf)
echo 'debug=1' >> c.conf; b=$(stat -c %i c.conf)
sed -i 's/dev/prod/' c.conf; c=$(stat -c %i c.conf)
[ "$a" = "$b" ] && echo "append: same inode"
[ "$b" != "$c" ] && echo "sed -i: new inode"
''', notes={1: 'Save.', 2: 'Append.', 3: 'sed -i :: rename over.', 4: 'Summary :: both lines print.'}, tryit='Try cat new > c.conf instead of sed -i.'),
    dict(level='a', tag='Security', title='Find files with several names',
         problem='<p>List regular files that have more than one name (link count above 1) in a folder.</p>',
         inp='a folder', approach=['find -links +1.', 'Print inode and links.'],
         code='''mkdir -p box; echo s > box/one; echo t > box/two; ln box/one box/alias
find box -type f -links +1 -printf '%i %n %p\\n' | sort
''', notes={1: 'Setup :: alias is a hard link (10.2).', 2: 'Same inode twice.'}, tryit='Remove box/alias and run the find again.'),
]

QUIZ = mix([
    dict(q='Which is NOT stored in an inode?', options=['the size', 'the owner', 'the file name', 'the permissions'], answer=2, why='Names are in directory entries.'),
    dict(q='touch says “No space left on device” but df -h shows 50% free. What do you check?', options=['free -h', 'df -i', 'du -sh', 'lsblk'], answer=1, why='Inodes may be 100%.'),
    dict(q='Which keeps the same inode number?', options=['cp a b', 'mv a b on the same filesystem', 'sed -i on a', 'mv a to another disk'], answer=1, why='Only the folder entry changes.'),
    dict(q='What shows inode numbers?', options=['ls -i', 'ls -n', 'ls -h', 'ls -s'], answer=0, why='-i = inode.'),
    dict(q='A deleted log still uses space. Which command finds it?', options=['df -i', 'lsof +L1', 'find -inum', 'stat'], answer=1, why='Link count 0, still open.'),
    dict(q='What does ctime mean in stat?', options=['creation time', 'last inode change', 'last read', 'last copy'], answer=1, why='Birth is creation.'),
    dict(q='On ext4, which inode is always the root folder?', options=['0', '1', '2', '11'], answer=2, why='11 is lost+found.'),
    dict(q='A file shows size 1G and 0 blocks. It is…', options=['corrupted', 'a sparse file', 'a link', 'compressed by ls'], answer=1, why='Holes have no blocks.'),
])

REVISION = [
    'An inode is a file’s record: type, mode, owner, size, link count, times, data location. Not the name.',
    'A directory is a table of name → inode number. <code>.</code> and <code>..</code> are entries too.',
    '<code>ls -i</code>, <code>stat</code> (<code>-c %i %h %s</code>), <code>find -inum / -samefile</code>.',
    '“No space left” = blocks OR inodes: check <code>df -h</code> and <code>df -i</code>; find culprits with <code>du --inodes</code>.',
    'Data is freed when links = 0 and no program has it open: <code>lsof +L1</code>.',
    'mv (same disk) keeps the inode; cp and sed -i make a new one. ext4 inode count is fixed at mkfs.',
]

FAQ = [
    ('What is an inode in Linux?', 'A data structure that stores a file’s metadata (type, permissions, owner, size, times, link count, data block locations), identified by a number. It does not store the name.'),
    ('How do I see a file’s inode number?', 'ls -i FILE or stat -c %i FILE.'),
    ('How do I check inode usage?', 'df -i (per filesystem) and du --inodes -x DIR (per folder).'),
    ('Why “No space left on device” when the disk has space?', 'The filesystem has run out of inodes (df -i shows 100%), usually from millions of small files.'),
    ('Can I add more inodes to ext4?', 'Not on an existing filesystem; recreate it with mkfs.ext4 -i or -N, or use XFS.'),
    ('Why is space not freed after deleting a file?', 'A program still has it open; find it with lsof +L1 and restart or reload it.'),
    ('Where is the file name stored?', 'In the directory entry of its parent folder.'),
]

PRACTICE_INTRO = 'Small inode tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Inode number', stmt='Print only the inode number of a new file (check that it is a number).', inp='a file', code="touch n.txt; stat -c %i n.txt | grep -Eq '^[0-9]+$' && echo number\n", explain='%i.'),
    dict(level='easy', title='Links of a file', stmt='Print the link count of a new file.', inp='a file', code="touch l.txt; stat -c %h l.txt\n", explain='1 name.'),
    dict(level='easy', title='Folder links', stmt='Make a folder with two subfolders and print its link count.', inp='folders', code="mkdir -p top/a top/b; stat -c %h top\n", explain='2 + 2 = 4.'),
    dict(level='medium', title='Rename keeps it', stmt='Show that mv keeps the inode number.', inp='a file', code="touch m1; a=$(stat -c %i m1); mv m1 m2; [ \"$a\" = \"$(stat -c %i m2)\" ] && echo same\n", explain='Same disk.'),
    dict(level='medium', title='Copy changes it', stmt='Show that cp makes a new inode.', inp='a file', code="touch c1; cp c1 c2; [ \"$(stat -c %i c1)\" != \"$(stat -c %i c2)\" ] && echo different\n", explain='New file.'),
    dict(level='medium', title='Sparse', stmt='Make a 5 MB sparse file and print its size and block count.', inp='nothing', code="truncate -s 5M sp; stat -c '%s %b' sp\n", explain='0 blocks.'),
    dict(level='business', title='Delete by inode', stmt='Delete a file called -x using its inode number.', inp='a bad name', code="touch -- -x; find . -maxdepth 1 -inum \"$(stat -c %i -- -x)\" -delete; ls -- -x 2>/dev/null || echo gone\n", explain='-inum -delete.'),
    dict(level='business', title='Count files', stmt='Count the inodes used inside a folder with 20 files.', inp='a folder', code="mkdir -p cnt; for i in $(seq 1 20); do : > cnt/f$i; done; du --inodes -s cnt | cut -f1\n", explain='20 files + the folder = 21.'),
]

SCN_INTRO = 'Interview questions about inodes, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is an inode?”', 'A favourite Linux interview question.', 'can you say what is (and is not) inside?',
        '''<ul>
          <li>A numbered record per file: type, permissions, owner, size, times, link count, data block pointers.</li>
          <li>Not the name: names are in directories (name → inode number).</li>
          <li>See it: <code>ls -i</code>, <code>stat</code>.</li>
        </ul>''', 'saying “the inode stores the file name”.') +
    scn('Hosting company', 'Junior', '“No space left on device” with 40% free', 'Customers cannot upload. df -h looks fine.', 'do you check inodes?',
        '''<ol>
          <li><code>df -i</code>: IUse% 100%.</li>
          <li><code>du --inodes -x / | sort -n | tail</code>: e.g. /var/lib/php/sessions.</li>
          <li>Delete old sessions with find -mtime; fix the session clean-up job.</li>
        </ol>''', 'deleting large files and restarting the server.') +
    scn('Operations', 'Mid-level', 'Deleted 30 GB of logs, df did not change', 'The disk is still 100%.', 'deleted-but-open files?',
        '''<ul>
          <li><code>sudo lsof +L1</code> shows the app holding the deleted log (NLINK 0).</li>
          <li>Reload the app (or <code>: &gt; /proc/PID/fd/N</code>) to free the space.</li>
          <li>Prevent it: logrotate with postrotate reload, or copytruncate.</li>
        </ul>''', 'rebooting a production server without knowing why.') +
    scn('Storage team', 'Senior', 'Design a disk for 200 million thumbnails', 'Average file 6 KB.', 'inode planning?',
        '''<ul>
          <li>ext4 default (1 inode per 16 KB) gives too few: use <code>mkfs.ext4 -i 4096</code> or choose XFS (dynamic inodes).</li>
          <li>Shard into folders (ab/cd/…) so directories stay small.</li>
          <li>Or use object storage for billions of objects.</li>
        </ul>''', 'using defaults and finding out at 100%.')
) + interview([
    ('What does df -i show?', 'Total, used and free inodes per filesystem.'),
    ('Is the file name in the inode?', 'No, it is in the directory entry.'),
    ('Why is mv fast and cp slow for large files?', 'mv on one filesystem only changes a folder entry; cp copies data to a new inode.'),
    ('What is the link count?', 'The number of directory entries (names) pointing to the inode.'),
    ('When is a file’s space freed?', 'When its link count is 0 and no process has it open.'),
    ('What is the difference between mtime and ctime?', 'mtime: contents changed; ctime: inode changed (incl. chmod, chown).'),
    ('How do you remove a file with an unprintable name?', 'find -inum N -delete.'),
], [
    ('RHCSA (EX200)', 'Diagnose filesystem issues; create and manage file systems.'),
    ('LFCS', 'Manage and troubleshoot file systems and storage.'),
    ('CompTIA Linux+', 'Inodes, df -i, hard and soft links.'),
]) + distro('The concept is the same everywhere; tools and limits differ.', [
    ('ls -i / stat', 'yes', 'yes', 'yes (BSD stat -f)', 'Git Bash: fake numbers'),
    ('df -i', 'yes', 'yes', 'df -i', '-'),
    ('Default filesystem', 'ext4', 'XFS (dynamic inodes)', 'APFS', 'NTFS (MFT records)'),
    ('debugfs / tune2fs', 'ext4', 'xfs_db for XFS', '-', '-'),
    ('lsof +L1', 'yes', 'yes', 'yes', '-'),
]) + teaser('10.2', 'The link count can be more than 1: one inode, two names. Riya also sees arrows like <code>python3 -&gt; python3.12</code> in ls -l. What is the difference between a hard link and a symbolic link, and which one breaks when you delete the original? Next: hard links vs soft links.')

CHEATSHEET = cheatsheet('Inodes', [
    ('See', [('ls -i', 'inode numbers'), ('ls -lai', 'with links, . ..'), ('stat f', 'all fields'), ('stat -c %i', 'number only'), ('stat -f', 'filesystem')]),
    ('Usage', [('df -i', 'per disk'), ('df -ih', 'human'), ('du --inodes -x', 'per folder'), ('find -links +1', 'multi-name')]),
    ('Find', [('find -inum N', 'by number'), ('find -samefile f', 'same inode'), ('-xdev', 'one disk'), ('-inum N -delete', 'odd names')]),
    ('Deep', [('sudo lsof +L1', 'deleted, open'), ('tune2fs -l', 'inode count'), ("debugfs -R 'ls -l'", 'raw entries'), ('mkfs.ext4 -i', 'set ratio')]),
])

MINDMAP = mindmap('Inode', [
    ('Holds', 'blue', ['type, mode', 'owner, size', 'times, links']),
    ('Not', 'red', ['the name', 'in the folder', 'name → number']),
    ('See', 'green', ['ls -i', 'stat', 'debugfs']),
    ('Limits', 'amber', ['df -i', 'fixed on ext4', 'XFS dynamic']),
    ('Free', 'violet', ['links 0', 'not open', 'lsof +L1']),
    ('Ops', 'acc', ['mv same', 'cp new', 'sed -i new']),
])

LAB = lab('inode detective', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab101 && cd ~/lab101 && rm -rf case answers.txt
mkdir -p case/a case/b; echo invoice > case/a/inv.txt; echo memo > case/b/memo.txt
touch -- 'case/-delete-me'; truncate -s 50M case/disk.img''',
    tasks=['Write the inode number of <code>case/a/inv.txt</code> into <code>answers.txt</code> (only the number, one line).',
           'Rename <code>case/a/inv.txt</code> to <code>case/b/invoice.txt</code> so that it keeps the same inode.',
           'Delete the file named <code>-delete-me</code> using its inode number.',
           'Append the block count (<code>%b</code>) of <code>case/disk.img</code> as a second line of <code>answers.txt</code>.'],
    solution='''stat -c %i case/a/inv.txt > answers.txt
mv case/a/inv.txt case/b/invoice.txt
find case -inum "$(stat -c %i -- 'case/-delete-me')" -delete
stat -c %b case/disk.img >> answers.txt''',
    check='''cd ~/lab101
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 number"  '[ -f answers.txt ] && [ -f case/b/invoice.txt ] && [ "$(sed -n 1p answers.txt)" = "$(stat -c %i case/b/invoice.txt)" ]'
ok "2 rename"  '[ ! -e case/a/inv.txt ] && [ -f case/b/invoice.txt ]'
ok "3 delete"  '[ ! -e "case/-delete-me" ]'
ok "4 blocks"  '[ "$(sed -n 2p answers.txt 2>/dev/null)" = "$(stat -c %b case/disk.img)" ]' ''')
