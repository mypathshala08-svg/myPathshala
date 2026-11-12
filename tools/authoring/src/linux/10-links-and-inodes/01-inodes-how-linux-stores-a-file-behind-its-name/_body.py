import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# a tiny real ext4 disk with only 16 inodes, mounted at /mnt/tiny (loop device)
TINY = r"""export PATH=$PATH:/usr/sbin:/sbin; sudo umount /mnt/tiny 2>/dev/null; rm -f ~/tiny.img; truncate -s 8M ~/tiny.img; mkfs.ext4 -q -N 16 ~/tiny.img
sudo mkdir -p /mnt/tiny; sudo mount -o loop ~/tiny.img /mnt/tiny; sudo chown riya: /mnt/tiny"""
UNM = 'cd ~; sudo umount /mnt/tiny'
# the same tiny disk with three files, unmounted, for debugfs
IMG = TINY + r"""
cd /mnt/tiny; echo 'Q3 sales: 42 lakh' > report.txt; mkdir logs; echo boot > logs/app.log; cd ~; sudo umount /mnt/tiny"""
INO = r"""rm -rf ~/ino; mkdir -p ~/ino/docs; cd ~/ino
echo 'Q3 sales: 42 lakh' > report.txt; echo 'meeting at 10' > docs/notes.txt"""

HOOK = hook('The monitoring alert says “disk full”: the app cannot create a single new file. But <code>df -h</code> shows the disk is only 1% used. On another server, an admin deletes a 20 GB log and <code>df</code> shows no space was freed. Renaming a 50 GB video takes no time at all, yet copying it takes ten minutes. All three puzzles have one answer: Linux does not store a file under its name. Behind every name is an <b>inode</b>, a small numbered record that holds everything about the file except its name.',
    ['explain what an inode is, what it stores (and what it does not: the name), and how a directory maps names to inode numbers',
     'read every field of <code>stat</code>, see inode numbers with <code>ls -i</code>, and check inode usage with <code>df -i</code>',
     'diagnose “No space left on device” with free space, deleted-but-open files, and why mv is instant but cp is not',
     'look inside a real ext4 disk with <code>debugfs</code> and <code>tune2fs</code>, and find or delete files by inode number'])
ROAD = roadmap([
    ('story', 'The story', 3, 'full disk at 1%'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'What an inode is', 6, 'simple meaning + 4 depths'),
    ('types', 'Name, inode, data', 4, 'three separate things'),
    ('commands', 'Inode tools by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'a path lookup'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'inode detective'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('See a file’s inode number', 'ls -i FILE', 'number before the name'),
    ('See everything in the inode', 'stat FILE', 'size, blocks, links, owner, times'),
    ('Just one field (for scripts)', "stat -c '%i %h %s' FILE", 'inode, links, size'),
    ('“No space left” but df -h has space', 'df -i', 'IUse% 100% = out of inodes'),
    ('Find which folder eats inodes', 'du --inodes -x / | sort -n | tail', 'many tiny files'),
    ('Deleted file still uses space', 'sudo lsof +L1', 'still open by a program'),
    ('Find or delete a file by number', 'find . -inum N [-delete]', 'odd file names'),
    ('Inode size and count of a disk', 'sudo tune2fs -l /dev/sdX', 'ext4 only'),
])

cmap = concept_map(
    [('2.2', 'Paths', 'absolute, relative'), ('3.3', 'rm', 'deletes a name'), ('9.1', 'Permissions', 'stored in the inode')],
    ['inode = the file’s record (everything but the name)', 'directory = a table of name → inode number', 'ls -i, stat, df -i, find -inum', 'link count, deleted-but-open files', 'debugfs and tune2fs: inside ext4'],
    [('10.2', 'Hard and soft links', 'two names, one inode'), ('11.5', '/proc', 'open files of a process'), ('15.1', 'Disks and filesystems', 'mkfs, mount, df'), ('16.4', 'Logs', 'rotation and inodes')],
    'A file is an inode plus data blocks. Names live in directories and only point at inodes.')

sc = (term(20, 14, 316, 156, ['$ touch new.txt', ('touch: cannot touch \'new.txt\':', 'err'), ('  No space left on device', 'err'), '$ df -h . | tail -1', ('/dev/loop0  4.0M  24K  3.5M  1%', 'out'), '$ df -i . | tail -1', ('/dev/loop0  16  16  0  100%', 'acc')], title='riya@web01: /mnt/tiny', prompt='riya@web01:/mnt/tiny$', size=7.0, step=15)
      + t(352, 36, 'Space left, but full?', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• blocks: 1% used', '• inodes: 100% used', '• every file needs', '  one inode', '• no inode = no file'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A full disk that is 99% empty</h2>
  <div class="story">
''' + puzzle('A mail server stores every email as a separate tiny file. One morning it cannot save new mail: “No space left on device”. Riya runs <code>df -h</code> and sees 60% free. She deletes a 2 GB backup to make room. The error does not go away. Why not, and which single command would have shown the real problem?') + '''
    <p class="narration">Riya reproduces the problem on a tiny 8 MB test disk that has room for only 16 files.</p>
''' + scene('A terminal: touch fails with No space left on device; df -h shows 1% used; df -i shows 100% of inodes used.', sc,
            'Every file needs <tspan font-weight="700" class="s-acc">one inode</tspan>. Run out of inodes and the disk is full.') + '''
K> But the disk has 3.5 MB free!
A> Free <b>blocks</b>, yes. A filesystem has two separate stocks: data blocks for contents, and a fixed number of <b>inodes</b>, one per file. Millions of tiny files can use up the inodes long before the blocks.
R> So what is an inode?
A> The file’s identity card: its number, type, size, owner, permissions, times, link count and where its data is on disk. Everything except the name. The name lives in the folder. Today you will see both, on a real disk.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A library: the catalogue card shows a title and a shelf number; the register under that number describes the book; the shelf holds the pages. Folder entry, inode, data blocks.">'
       + label_box(14, 20, 190, 110, ['folder = catalogue', 'report.txt → 12', 'notes.txt  → 13', '(name → number)'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['inode 12 = register', 'size 18 B, owner riya', 'rw-r--r--, 1 link', 'data at block 1036'], 'amber', 8.6)
       + label_box(434, 20, 192, 110, ['data blocks = shelf', 'block 1036:', '“Q3 sales: 42 lakh”', '(the contents)'], 'green', 8.6)
       + t(320, 160, 'The name is in the folder. Everything else is in the inode.', 9.6, 'ink2')
       + t(320, 182, 'Rename = change the catalogue card. The book does not move.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Inodes at four depths', [
    ('v', 'No jargon: a library catalogue', '      <p>A file is stored in three parts, like a book in a library.</p>' + pic),
    ('b', 'What you will see every day', '''      <ul>
        <li><code>ls -i</code> shows the inode number in front of each name.</li>
        <li><code>stat file</code> shows what the inode holds: size, blocks, links, permissions, owner, times.</li>
        <li><code>df -i</code> shows how many inodes the disk has and how many are used.</li>
        <li>Rename (<code>mv</code>) in the same filesystem keeps the inode: instant. <code>cp</code> makes a new inode and copies the data.</li>
      </ul>'''),
    ('i', 'What the inode stores, and what a folder is', '''      <ul>
        <li>An inode holds: type (file, folder, link, device…), permission bits and special bits, owner UID and group GID, size, number of blocks, link count, timestamps (atime, mtime, ctime, birth) and pointers to the data (on ext4: <b>extents</b>, “1 block starting at 1035”).</li>
        <li>A directory is a special file whose data is a list of entries: <b>name → inode number</b>. Every folder contains <code>.</code> (its own inode) and <code>..</code> (the parent’s).</li>
        <li>The <b>link count</b> is how many names point to the inode. <code>rm</code> removes a name; the data is freed only when the count reaches 0 <b>and</b> no program still has the file open.</li>
        <li>Inode numbers are unique only inside one filesystem: the pair (device, inode) identifies a file.</li>
      </ul>'''),
    ('a', 'Behind the screen: ext4 internals', '''      <ul>
        <li><code>mkfs.ext4</code> creates a fixed <b>inode table</b>: by default one inode per 16 KB of disk, 256 bytes each. The count cannot grow later (<code>-N</code> or <code>-i</code> at mkfs time). XFS and Btrfs allocate inodes dynamically, so they rarely run out.</li>
        <li>Inodes 1–10 are reserved: 2 is the root folder of every ext4 filesystem, 8 the journal, 11 <code>lost+found</code>.</li>
        <li>Opening <code>/srv/a/b.txt</code> is a <b>path walk</b>: inode 2 → read its entries → find <code>srv</code> → its inode → … The kernel caches results in the <b>dentry cache</b>.</li>
        <li>Tiny files (≈60 bytes) can live <b>inside</b> the inode (ext4 inline_data); a <b>sparse</b> file has a large size but few blocks, because holes have no blocks at all.</li>
        <li>Each process’s open files point to the inode, not the name: that is why a deleted log keeps using space until the program closes it or restarts.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Inode: index node</h2>
''' + def_block(
    'An <b>inode</b> (index node) is a numbered on-disk record that describes one file system object: its type, permissions, owner, group, size, timestamps, link count and the location of its data blocks. It does <b>not</b> contain the file’s name. A <b>directory</b> is a list of entries mapping names to inode numbers, so one inode can have several names (hard links, Lesson 10.2).',
    'The name is a label in a folder. The inode is the file.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Inode', 'The file’s record: everything except the name.'),
    ('Inode number', 'Its ID inside one filesystem (ls -i).'),
    ('Directory entry (dentry)', 'One line in a folder: name → inode number.'),
    ('Data blocks', 'Where the contents are stored (4 KB each, usually).'),
    ('Extent', 'A run of blocks: “8 blocks from block 1036”.'),
    ('Link count', 'How many names point to this inode.'),
    ('Inode table', 'The fixed array of inodes made by mkfs.'),
    ('Sparse file', 'Size larger than the blocks it uses.'),
]) + '\n' + names('Where the names come from.', [
    ('inode', 'index node', 'Unix, early 1970s.'),
    ('stat', 'status', 'The stat() system call.'),
    ('df -i', 'disk free, inodes', 'Counts inodes, not bytes.'),
    ('dentry', 'directory entry', 'Kernel term.'),
    ('debugfs', 'debug filesystem', 'ext2/3/4 inspector.'),
    ('tune2fs', 'tune ext2 fs', 'Reads/changes ext settings.'),
    ('ctime', 'change time', 'Inode changed, not “created”.'),
    ('lost+found', 'inode 11', 'fsck puts orphans here.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Inode number', '<code>ls -i f</code>'),
    ('All fields', '<code>stat f</code>'),
    ('Inode usage', '<code>df -i</code>'),
    ('By number', '<code>find . -inum N</code>'),
    ('Root folder inode', '2 (ext4)'),
    ('ext4 inode size', '256 bytes'),
]) + '\n' + lv + didyou('Your file names are not stored with your files at all. That is why one file can have two names (10.2), why a file can exist with no name (deleted but still open), and why <code>mv</code> of a 50 GB file inside one disk takes milliseconds: only one line in a folder changes.') + '''
EXAM> “What information is not stored in an inode?” → The file name (and the file’s contents). Names are stored in directory entries.
''' + qc('A folder has 3 subfolders. What is its link count, and why?', '5: its name in the parent, its own <code>.</code>, and the <code>..</code> of each of the 3 subfolders.') + mistake('“ctime is the creation time”',
    'ctime = last inode change (chmod, chown, rename, write). Creation time is Birth (stat %w).',
    'stat shows Access, Modify, Change and Birth. chmod changes ctime but not mtime; many scripts that “find files created today” with -ctime are wrong.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Name, inode and data: three separate things</h2>
''' + table(['', 'Directory entry', 'Inode', 'Data blocks'], [
    ['Holds', 'name + inode number', 'type, mode, owner, size, times, links, block map', 'the contents'],
    ['Size', 'a few bytes per name', '256 bytes (ext4)', '4 KB blocks'],
    ['Changed by', 'mv, rm, ln, touch new', 'chmod, chown, write, touch', 'write, append'],
    ['Count limited?', 'no', 'yes: fixed at mkfs (ext4)', 'yes: disk size'],
    ['See it with', 'ls -i, debugfs ls', 'stat, debugfs stat', 'cat, debugfs blocks'],
], minw=560) + table(['Operation', 'Inode', 'Why'], [
    ['<code>mv a b</code> (same filesystem)', 'same', 'only the folder entry changes'],
    ['<code>mv a /other-disk/</code>', 'new', 'copy + delete across filesystems'],
    ['<code>cp a b</code>', 'new', 'new file, data copied'],
    ['<code>echo x &gt;&gt; a</code>, <code>&gt; a</code>', 'same', 'same file written'],
    ['<code>sed -i</code>, many editors', 'new', 'write a temp file, rename over'],
    ['<code>chmod</code>, <code>chown</code>', 'same', 'only inode fields change'],
], minw=420) + table(['Filesystem', 'Inodes'], [
    ['ext4', 'fixed at mkfs: can run out'],
    ['XFS', 'allocated on demand (up to a % of space)'],
    ['Btrfs', 'dynamic: practically no limit'],
    ['tmpfs', 'limited by memory (nr_inodes)'],
    ['FAT / exFAT', 'no real inodes (Linux fakes numbers)'],
], minw=360) + qc('Why does <code>sed -i</code> change a file’s inode number but <code>echo &gt;&gt;</code> does not?', 'sed -i writes a new temporary file and renames it over the old name, so the name points to a new inode. &gt;&gt; opens the existing inode and appends.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Inode tools explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine: in a sample folder <code>~/ino</code>, and on a real 8 MB ext4 test disk with only 16 inodes, mounted at <code>/mnt/tiny</code>.</p>
''' + cmdcard_u(['seeing whether two names are the same file', 'checking whether a file was replaced', 'finding odd names'],
               ['comparing inode numbers from two different disks'])(
    'lsi', 'ls -i', 'show inode numbers',
    '<code>ls -i</code> prints each name’s inode number in front of it. Add <code>-l</code> for the full listing (the 2nd column is the link count), <code>-a</code> to see <code>.</code> and <code>..</code>, <code>-d</code> for a folder itself.',
    'ls -i[l][a][d] [FILE…]', 'safe',
    [('-i', 'inode numbers', 'identity'),
     ('-li', 'with long listing', 'links, size'),
     ('-ia', 'include . and ..', 'folder links'),
     ('-id DIR', 'the folder itself', 'not its contents'),
     ('stat -c %i', 'number only', 'scripts')],
    dict(setup=INO, cmd="cd ~/ino\nls -i\nls -ia docs\nls -id . docs", note='docs/. has the same number as docs: “.” is just another name for the folder.'),
    [('dev', [
        dict(situation='Was my config replaced or edited in place?', setup=INO, cmd="cd ~/ino; ls -i report.txt\necho 'Q4: 50 lakh' >> report.txt; ls -i report.txt\nsed -i 's/lakh/L/' report.txt; ls -i report.txt",
             why='Append keeps the inode; sed -i creates a new file under the same name. Programs watching the old inode (tail -f, inotify, hard links) lose it.')]),
     ('sys', [
        dict(situation='Same name, same file? Compare the numbers.', setup=INO, cmd="cd ~/ino; cp report.txt copy.txt; mv docs/notes.txt moved.txt\nls -i report.txt copy.txt moved.txt",
             why='cp gave a new inode; mv kept the old one: moved.txt has the number notes.txt had.')]),
    ],
    anat=anatomy([('ls', 'cmd', 'list'), ('-i', 'opt', 'inode'), ('-a', 'opt', 'dot files'), ('docs', 'arg', 'folder')], 'The first column is the inode number.')
) + cmdcard_u(['reading everything Linux knows about a file', 'scripts that need size, owner or times', 'debugging time and permission problems'],
               ['expecting a creation time on every filesystem'])(
    'stat', 'stat', 'show the whole inode',
    '<code>stat</code> prints the inode’s fields: size, blocks, IO block, device, inode number, links, mode, UID, GID and four times (Access, Modify, Change, Birth). <code>-c FORMAT</code> prints chosen fields; <code>-f</code> describes the filesystem instead.',
    "stat [-c FORMAT] [-f] FILE…", 'safe',
    [('%i', 'inode number', 'identity'),
     ('%h', 'hard links', 'link count'),
     ('%s / %b', 'size / 512 B blocks', 'real usage'),
     ('%A %a', 'mode', 'letters / octal'),
     ('%U %G', 'owner, group', 'names'),
     ('%y %z %w', 'mtime ctime birth', 'times'),
     ('-f', 'filesystem info', 'inodes total/free')],
    dict(setup=INO, cmd="cd ~/ino; stat report.txt", note='Size 18 bytes but Blocks 8 (8 × 512 B = one 4 KB block). Links 1: one name. Birth is the creation time on ext4.'),
    [('qa', [
        dict(situation='Size is not space: a sparse file.', setup=INO, cmd="cd ~/ino; truncate -s 1G sparse.img\nstat -c 'size=%s blocks=%b' sparse.img; du -h sparse.img; ls -lh sparse.img",
             why='1 GB size, 0 blocks: the inode records a size, but holes have no data blocks. VM disks and databases use this.')]),
     ('sec', [
        dict(situation='Which times change when? (forensics)', setup=INO, cmd="cd ~/ino; f=report.txt; stat -c 'm=%y c=%z' $f | cut -c1-70\nsleep 1; chmod 600 $f; stat -c 'm=%y c=%z' $f | cut -c1-70",
             why='chmod updated ctime only. Attackers can fake mtime with touch -d, but not ctime (without changing the clock).')]),
     ('sys', [
        dict(situation='How many inodes are free on this filesystem?', setup=INO, cmd="stat -f -c 'inodes total=%c free=%d  type=%T' ~/ino",
             why='stat -f reports the filesystem; the same numbers as df -i.')]),
    ]
) + cmdcard_u(['“No space left on device” with free space', 'servers with millions of small files (mail, cache, sessions)', 'capacity planning'],
               ['reading only df -h'])(
    'dfi', 'df -i · du --inodes', 'inode usage',
    '<code>df -i</code> shows each filesystem’s total, used and free inodes and IUse%. At 100%, no new file, folder or link can be created, even with gigabytes free. <code>du --inodes</code> counts inodes per folder to find the culprit.',
    'df -i [PATH]   ·   du --inodes -x DIR | sort -n | tail', 'safe',
    [('df -i', 'inodes per filesystem', 'check'),
     ('df -ih', 'human numbers (K, M)', 'readable'),
     ('du --inodes -x', 'inodes per folder', 'find culprit'),
     ('-x', 'stay on one filesystem', 'skip /proc')],
    dict(setup=TINY, cmd="cd /mnt/tiny; for i in 1 2 3 4 5 6; do touch f$i || echo \"stopped at f$i\"; done\ndf -h . | tail -1; df -i . | tail -1\necho more >> f1 && echo 'append to an existing file: OK'\n" + UNM, expect='any',
         note='Real: 16 inodes, 11 already used (1–10 reserved, 11 = lost+found). Five files fit; the sixth fails while 3.5 MB are free. Appending works: no new inode needed.'),
    [('sys', [
        dict(situation='The puzzle: deleting a big file does not help.', setup=TINY + '; cd /mnt/tiny; for i in 1 2 3 4; do touch s$i; done; fallocate -l 2M big.bak', cmd="cd /mnt/tiny; df -i . | tail -1\nrm big.bak; touch new.txt && echo created; df -i . | tail -1\n" + UNM, expect='any',
             why='rm big.bak freed one inode, so exactly one new file fits. With millions of mails, you must delete many small files, not one big one.')]),
     ('devops', [
        dict(situation='Which folder holds the most files?', setup=INO + "; mkdir -p ~/ino/cache; cd ~/ino/cache; for i in $(seq 1 300); do : > s$i; done", cmd="du --inodes -x ~/ino | sort -n | tail -3",
             why='Typical culprits: PHP session folders, mail queues, cache folders, node_modules, forgotten tmp files.')]),
    ]
) + mistake('“df -h shows 40% free, so the disk cannot be full”', 'df -h   and   df -i',
            'Blocks and inodes run out separately. Always check both when you see “No space left on device”.') + cmdcard_u(['files with names you cannot type (newlines, leading -)', 'checking that two paths are one file'],
               ['-inum across several filesystems (numbers repeat)'])(
    'findinum', 'find -inum · -samefile', 'files by inode',
    '<code>find -inum N</code> finds every name whose inode is N; <code>-samefile F</code> finds all names of the same inode as F. Add <code>-delete</code> or <code>-exec</code> to act on it. Use <code>-xdev</code> so it stays on one filesystem.',
    'find DIR -xdev -inum N [-delete]   ·   find DIR -samefile FILE', 'change',
    [('-inum N', 'inode number N', 'identify'),
     ('-samefile F', 'same inode as F', 'all names'),
     ('-xdev', 'one filesystem', 'numbers are per disk'),
     ('-delete', 'remove that name', 'odd names'),
     ("-links +1", 'files with several names', 'hard links')],
    dict(setup=INO + "; cd ~/ino; touch -- '-rf' $'bad\\nname'", cmd="cd ~/ino; ls -i\nn=$(ls -i | awk '/-rf/{print $1}')\nfind . -inum \"$n\" -delete; ls", note='A file named -rf is hard to remove (rm -rf!). By inode number there is no quoting problem. The name with a newline prints on two lines here; in a terminal ls shows it as bad?name.'),
    [('sec', [
        dict(situation='Delete the file with a newline in its name, safely.', setup=INO + "; cd ~/ino; touch $'bad\\nname'", cmd="cd ~/ino; ls -i | head -3\nfind . -maxdepth 1 -name 'bad*' -printf '%i %p\\n'\nfind . -maxdepth 1 -inum \"$(find . -maxdepth 1 -name 'bad*' -printf '%i')\" -delete; ls",
             why='Check the number first (-printf %i), then delete exactly that inode.')]),
    ]
) + cmdcard_u(['learning how ext4 really stores files', 'recovery and forensics on a disk image', 'checking inode count and size'],
               ['writing with debugfs -w on a mounted disk (corruption)'], )(
    'debugfs', 'debugfs · tune2fs -l', 'look inside ext4',
    '<code>debugfs</code> opens an ext2/3/4 filesystem (read-only unless <code>-w</code>): <code>ls -l</code> shows the raw folder entries, <code>stat &lt;N&gt;</code> an inode, <code>blocks &lt;N&gt;</code> its data blocks. <code>tune2fs -l</code> lists the superblock: inode count, size, free inodes. Real disks need sudo; image files do not.',
    "debugfs -R 'CMD' DEVICE   ·   tune2fs -l DEVICE", 'change',
    [("-R 'ls -l /'", 'folder entries', 'name → inode'),
     ("-R 'stat <12>'", 'inode 12', 'raw fields'),
     ("-R 'blocks <12>'", 'data blocks', 'where data is'),
     ("-R 'ncheck 12'", 'inode → name', 'reverse lookup'),
     ('tune2fs -l', 'superblock', 'Inode count/size'),
     ('-w', 'writable', 'experts only')],
    dict(setup=IMG, cmd="debugfs -R 'ls -l /' ~/tiny.img 2>/dev/null", note='The real directory on disk: inode number, mode, links, UID, GID, size, date, name. 2 is the root folder (both . and ..), 11 is lost+found.'),
    [('sys', [
        dict(situation='The inode of report.txt, as stored on disk.', setup=IMG, cmd="debugfs -R 'stat <12>' ~/tiny.img 2>/dev/null | grep -v -E 'time:|^Size of|^Generation|^Fragment|^File ACL|Inode checksum'\ndebugfs -R 'cat <12>' ~/tiny.img 2>/dev/null",
             why='No name anywhere in the inode. EXTENTS says where the data is; cat &lt;12&gt; reads it by number.')]),
     ('dba', [
        dict(situation='How many inodes did mkfs create, and how big is each?', setup=IMG, cmd="tune2fs -l ~/tiny.img | grep -E '^Inode count|^Free inodes|^Inode size|^Block count|^Free blocks'",
             why='Plan before mkfs: a disk for millions of small files needs mkfs.ext4 -i 4096 (or -N), or XFS.')]),
    ], sudo=True
) + undo('Inode problems are fixed by removing files or changing the filesystem; there is no “add inodes” command on ext4.', [
    ('Inodes at 100%:', 'find the folder with <code>du --inodes -x /</code>, delete old small files (sessions, cache, mail queue), then fix the program that makes them.'),
    ('Space not freed after rm:', '<code>sudo lsof +L1</code> lists deleted-but-open files; restart or reload that program, or empty the file with <code>: &gt; /proc/PID/fd/N</code>.'),
    ('Need more inodes permanently:', 'back up, re-create with <code>mkfs.ext4 -i 4096</code> or <code>-N</code>, restore; or use XFS. (Destroys data on that disk!)'),
    ('Deleted a file by mistake:', 'stop writing to that disk at once; tools such as extundelete may recover it from a copy of the disk. Better: backups.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='touch /mnt/tiny/f6', setup=TINY + '; cd /mnt/tiny; touch f1 f2 f3 f4 f5', meaning='No free inode (also printed when blocks are full).', fix='<code>df -i</code> and <code>df -h</code>; delete small files.'),
    dict(cmd='find ~/ino -inum abc', setup=INO, meaning='-inum needs a number.', fix='Take it from <code>ls -i</code> or <code>stat -c %i</code>.'),
    dict(cmd='debugfs -R stat /dev/vda', meaning='A real disk needs root (and a command argument).', fix="<code>sudo debugfs -R 'stat &lt;2&gt;' /dev/sda1</code>."),
    dict(cmd='stat nothing.txt', meaning='No such name in this folder.', fix='Check the path; names are looked up folder by folder.'),
]) + mistake('“The inode is a unique number for each file” (on the whole system)', 'Unique only inside one filesystem: the pair (device, inode) identifies a file',
            'Every disk numbers its inodes from 1, so /home/a and /mnt/usb/b can both be inode 12. find -inum should be used with -xdev, and backup tools compare device and inode together.') + qc('Two names show the same inode number with <code>ls -i</code>. When are they the same file?', 'Only when they are on the same filesystem (same Device in stat). Inode numbers repeat on every disk.') + '''
'''
_sh.run_sh(UNM, 'any')

cards = cards + '</section>\n'

_IN = _sh.run_sh(INO + '; stat -c %i / /home ~ ~/ino/report.txt', 'any').split()
def walk(k):
    steps = [('/', 'inode ' + _IN[0]), ('home', 'inode ' + _IN[1]), ('riya', 'inode ' + _IN[2]), ('…/report.txt', 'inode ' + _IN[3])]
    o = ''
    for i, (n, ino) in enumerate(steps):
        tn = 'amber' if i == k else ('green' if i < k else 'card')
        o += label_box(10 + i * 86, 30, 80, 46, [n, ino], tn, 8)
    return o
see_lines = ['cat ~/ino/report.txt'] * 4
see = [term(14, 16, 332, 116, ['$ ' + c] + ([('Q3 sales: 42 lakh', 'out')] if i == 3 else []), title='riya@web01', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for i, (c, n) in enumerate(zip(see_lines, ['You type one path.', 'The kernel reads folder after folder…', '…each time: name → inode number…', '…then the inode gives the data blocks.']))]
behind = [walk(k) + t(180, 120, n, 8.6, 'violet', bold=True) for k, n in enumerate(['Start at the root: inode ' + _IN[0] + '.', 'In /: “home” → inode ' + _IN[1] + '.', 'In home: “riya” → inode ' + _IN[2] + '.', 'Then ino, then report.txt → inode ' + _IN[3] + ' → blocks.'])]
two = anim_two('A path lookup', 'Behind the screen: the path walk',
               'A terminal running cat on a full path and printing the file.',
               'Four boxes /, home, riya and report.txt with their inode numbers; each step reads one folder, finds the next name and moves to its inode.', see, behind,
               ['One command.', 'Folder 1.', 'Folder 2.', 'The data.'],
               ['/ = inode ' + _IN[0], 'home → ' + _IN[1], 'riya → ' + _IN[2], 'report.txt → ' + _IN[3]], )
two = two.replace('(real numbers)', '')

def openrm(k):
    name = label_box(14, 26, 110, 46, ['big.log', '(folder entry)'], 'blue' if k < 1 else 'red', 8)
    ino = label_box(150, 26, 110, 46, ['inode 13', f'links {1 if k < 1 else 0}'], 'amber', 8)
    app = label_box(150, 92, 110, 34, ['app has it open'] if k < 3 else ['app closed'], 'violet' if k < 3 else 'card', 8)
    data = label_box(286, 26, 70, 46, ['2 MB', 'data'], 'green' if k < 3 else 'card', 8)
    return (name if k < 1 else label_box(14, 26, 110, 46, ['(name gone)', 'rm big.log'], 'red', 8)) + ino + app + data
frames = [openrm(0) + t(180, 150, 'A program writes to big.log.', 8.6, 'violet', bold=True),
          openrm(1) + t(180, 150, 'rm removes the name: links 0.', 8.6, 'red', bold=True),
          openrm(2) + t(180, 150, 'Data stays: the program still has it open.', 8.6, 'red', bold=True),
          openrm(3) + t(180, 150, 'Program closes or restarts: space freed.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'Why rm did not free the space',
              'A deleted file that a program still has open.',
              'deleted but open', 'Boxes for the name, the inode, the program and the data: rm removes the name, but the data is freed only when the program closes the file.', frames,
              ['Open.', 'rm.', 'Still used.', 'Freed.'], hid='scenario-open')

OPEN = TINY + "; cd /mnt/tiny; fallocate -l 2M big.log"
dx = dissect('Layer by layer: from a name to the bytes',
    'Each layer has a real command and output from our build machine, on the 16-inode test disk.', [
    dict(key='name', name='The name you type', sub='a path', why='Humans use names.', how='Looked up folder by folder.', impl='Path walk.', used='Every open().',
         setup=IMG, cmd="debugfs -R 'ncheck 12 13' ~/tiny.img 2>/dev/null"),
    dict(key='dentry', name='Folder entry', sub='name → number', why='Folders are tables.', how='One line per name.', impl='ext4 dir blocks.', used='ls, mv, rm.',
         setup=IMG, cmd="debugfs -R 'ls -l /logs' ~/tiny.img 2>/dev/null"),
    dict(key='inode', name='Inode', sub='256-byte record', why='Everything but the name.', how='Fixed table.', impl='Inode table.', used='stat, permission checks.',
         setup=IMG, cmd="debugfs -R 'stat <12>' ~/tiny.img 2>/dev/null | head -4"),
    dict(key='blocks', name='Data blocks', sub='4 KB each', why='The contents.', how='Extents.', impl='Block bitmap.', used='read, write.',
         setup=IMG, cmd="debugfs -R 'blocks <12>' ~/tiny.img 2>/dev/null; debugfs -R 'cat <12>' ~/tiny.img 2>/dev/null"),
    dict(key='sb', name='Superblock', sub='the totals', why='How many inodes exist.', how='Written at mkfs.', impl='Block 0/1.', used='df -i.',
         setup=IMG, cmd="tune2fs -l ~/tiny.img | grep -E '^Inode count|^Free inodes'"),
], hint='From the name down to the disk. Click a layer.')

hd = hood('Under the hood: stat only asks for the inode', 'The real system calls of <code>stat report.txt</code> on our build machine. One call, <code>statx</code>, fetches the whole inode by name; the file is never opened and no data is read.',
          'stat report.txt', setup=INO + '; cd ~/ino', show='statx', trace='statx')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A path lookup, and a file without a name</h2>
''' + two + s1 + dx + hd + qc('A 2 GB log was deleted but df shows no change. What do you run?', '<code>sudo lsof +L1</code>: it lists files with link count 0 that are still open, with the program’s PID. Restart that program (or truncate via /proc/PID/fd).') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Inodes at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['df -i', '100%'], 'red', 8.6), '1. Mail and session servers',
              'Millions of tiny files (mails, PHP sessions, cache) exhaust inodes while blocks are free.', ['Alert', '*df -i', 'clean up']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['lsof +L1', 'deleted logs'], 'amber', 8.6), '2. Log rotation',
    'A log deleted while the app writes to it keeps using space until the app reopens it (logrotate copytruncate / reload).', ['Disk full', '*lsof +L1', 'reload']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['mkfs -i', 'planning'], 'blue', 8.6), '3. Storage design',
    'Admins choose the inode ratio (or XFS) when building disks for build caches, Git servers and image thumbnails.', ['Plan', '*mkfs.ext4 -i', 'deploy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['stat', 'ctime'], 'violet', 8.6), '4. Forensics and audits',
    'Investigators read inode times and numbers to see what changed and whether a file was replaced.', ['Incident', '*stat', 'timeline']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['same inode?', 'backups'], 'green', 8.6), '5. Backup and sync tools',
    'rsync, tar and backup tools use (device, inode) to spot hard links and avoid copying the same file twice.', ['Scan', '*inode', 'dedupe']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Inode number', scenario='Which inode is this?', setup=INO, cmd="stat -c '%i %n' ~/ino/report.txt", explain='%i.'),
    dict(level='b', title='Inode usage', scenario='Am I running out?', cmd="df -i ~ | tail -1", explain='IUse%.'),
    dict(level='i', title='Biggest file count', scenario='Who uses the inodes?', setup=INO + "; mkdir -p ~/ino/tmp; for i in $(seq 1 50); do : > ~/ino/tmp/t$i; done", cmd="du --inodes -x ~/ino | sort -n | tail -2", explain='du --inodes.'),
    dict(level='i', title='Size vs space', scenario='Sparse or real?', setup=INO, cmd="cd ~/ino; truncate -s 100M hole.img; du -h --apparent-size hole.img; du -h hole.img", explain='Holes use no blocks.'),
    dict(level='a', title='Deleted but open', scenario='Space not freed.', setup=OPEN, cmd="cd /mnt/tiny; exec 3< big.log; rm big.log; df -h . | tail -1; ls -l /proc/$$/fd/3 | sed 's/.*3 ->/fd 3 ->/'; exec 3<&-; df -h . | tail -1; " + UNM, explain='Freed only after close.'),
], extra=build_up('the inode detective', 'Riya follows one file through name, inode and data on the test disk.', IMG, [
    ("debugfs -R 'ls /' ~/tiny.img 2>/dev/null | tr -s ' ' '\\n' | grep -v '^$' | paste - - - | head -6", '1. The root folder: (inode) name pairs.'),
    ("debugfs -R 'stat <12>' ~/tiny.img 2>/dev/null | sed -n '/^Inode:/p;/^User/p;/^Links/p;/^EXTENTS/,+1p'", '2. Inode 12: type, owner, links.'),
    ("debugfs -R 'blocks <12>' ~/tiny.img 2>/dev/null", '3. Its data block number.'),
    ("debugfs -R 'cat <12>' ~/tiny.img 2>/dev/null", '4. The contents, read by number.'),
])) + which('Choosing the right tool.', [
    ('See the inode number', 'ls -i / stat -c %i', 'Identity.', 'Comparing across disks.'),
    ('All inode fields', 'stat', 'Size, links, times.', 'Trusting ls -l times.'),
    ('No space left', 'df -h and df -i', 'Two limits.', 'Only df -h.'),
    ('Who uses inodes', 'du --inodes -x', 'Finds the folder.', 'du -sh (bytes).'),
    ('Space not freed', 'lsof +L1', 'Deleted but open.', 'Deleting more files.'),
    ('Weird file name', 'find -inum N -delete', 'No quoting.', 'rm with wildcards.'),
]) + keys('Handy forms.', [
    ("stat -c '%i %h %n' *", 'inode, links, name', 'compare'),
    ('ls -lai', 'everything incl. . ..', 'folders'),
    ('df -ih', 'inodes, human', 'check'),
    ('find / -xdev -inum N', 'all names of N', 'one disk'),
    ('sudo lsof +L1', 'deleted, open', 'space'),
    ('stat -f -c %d .', 'free inodes', 'scripts'),
]) + scriptit('inode-check.sh', 'An alert script for cron: warn when any real filesystem is above a threshold of inodes, and show the busiest folder.',
'''limit=${1:-90}
df -i -x tmpfs -x devtmpfs -x squashfs -x overlay --output=ipcent,target | tail -n +2 |
while read -r pct mnt; do
  p=${pct%\\%}; [ "$p" = "-" ] && continue
  if [ "$p" -ge "$limit" ]; then echo "ALERT $mnt inodes $pct"; else echo "ok    $mnt inodes $pct"; fi
done''',
'<p>Run with a limit of 1% so the alert fires on our machine.</p>', expect='any') + puzzle_answer('The disk ran out of <b>inodes</b>, not space: every email is a file and needs one inode. Deleting one 2 GB backup freed only one inode. <code>df -i</code> would have shown IUse% 100%. Fix: delete or archive many old small files (find the folder with <code>du --inodes</code>), and for the future use a filesystem with more inodes (<code>mkfs.ext4 -i</code>) or XFS.') + qc('Does <code>mv</code> inside one filesystem change the inode number?', 'No. Only the folder entries change; the inode and the data stay where they are.') + '''
</section>
'''

_sh.run_sh('cd ~; sudo umount /mnt/tiny 2>/dev/null; rm -rf ~/ino ~/tiny.img', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../03-files-and-directories/03-deleting-safely-rm-rm-r-rm-i-shred-and-why-rm/">Lesson 3.3</a> (what rm really deletes) and <a href="../../09-permissions/01-reading-permissions-rwx-for-user-group/">Lesson 9.1</a> (ls -l columns).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
