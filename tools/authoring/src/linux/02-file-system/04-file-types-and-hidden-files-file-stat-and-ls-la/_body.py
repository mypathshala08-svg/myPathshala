import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

JPEG = r"printf '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9' > photo.jpg"

cmap = concept_map(
    [('2.2', 'ls -l columns', 'the first letter of each line'), ('2.3', 'Paths', 'naming any file')],
    ['the 7 file types: - d l c b p s', 'extensions are only part of the name', 'file: what is inside, by magic bytes', 'stat: every detail of an inode, three timestamps', 'hidden dotfiles and ls -a / -A'],
    [('3.1', 'Creating files', 'touch, mkdir'), ('9.1', 'Permissions', 'the other 9 letters'), ('10.1', 'Inodes', 'where stat’s data lives'), ('5.2', 'Redirection', '/dev/null and pipes')],
    'On Linux, what a file is depends on its inode and its content, never on the end of its name.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 300, 124, ['$ mv photo.jpg photo.txt', '$ cat photo.txt', ('����JFIF���...', 'err'), '$ file photo.txt', ('photo.txt: JPEG image data, JFIF', 'acc'), ('standard 1.01', 'acc')], title='riya@laptop', size=8.2)
      + t(350, 36, 'Riya’s experiment:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(350, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• renamed a photo to .txt', '• cat prints garbage', '• file still says JPEG', '• Linux looked inside', '• the name changed nothing'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Is it a photo or a text file?</h2>
  <div class="story">
''' + puzzle('Riya renames <code>photo.jpg</code> to <code>photo.txt</code>. Windows would now show a text icon. On Linux, <code>file photo.txt</code> still says “JPEG image data”. How can a program know it is a photo without trusting the name? (Hint: open the first four bytes.)') + '''
    <p class="narration">On Windows, Riya always judged a file by its extension and its icon. On Linux she tries a small experiment: she renames a photo to <code>.txt</code>. <code>cat</code> prints strange symbols, and the <code>file</code> command calmly says it is still a JPEG.</p>
''' + scene('A terminal where a renamed photo prints garbage with cat but file still reports JPEG image data, next to Riya’s notes.', sc,
            'Linux looks at <tspan font-weight="700" class="s-acc">what is inside</tspan>, not at the end of the name.') + '''
K> On Linux the extension is just part of the name. <code>.txt</code>, <code>.jpg</code>, no extension at all: the system does not care. Half the files in <code>/etc</code> have no extension.
R> Then how does anything know what a file is?
A> Two different questions. First: what <b>kind of object</b> is it: a normal file, a folder, a link, a device, a pipe? The kernel stores that in the inode, and <code>ls -l</code> shows it as the first letter. Second: for a normal file, what <b>format</b> is the content? The <code>file</code> command reads the first bytes and recognises signatures, called “magic numbers”.
K> And the files whose names start with a dot, like <code>.bashrc</code>? They are hidden. That is where all your settings live.
A> Today: the seven file types, <code>file</code>, the full story <code>stat</code> tells about any file, including its three timestamps, and hidden files.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
labels = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Jars in a kitchen: the label on the jar can be wrong, but opening the jar shows what is really inside. The name is the label, the content is what file reads.">'
          + ''.join(label_box(30 + k * 150, 30, 120, 90, [lab, inside], tone, 9.2) for k, (lab, inside, tone) in enumerate([('label: “SUGAR”', 'inside: sugar', 'green'), ('label: “SALT”', 'inside: sugar!', 'red'), ('no label', 'inside: rice', 'amber'), ('“.hidden” jar', 'at the back', 'violet')]))
          + t(320, 150, 'The label (the file name and extension) can be wrong or missing.', 9.4, 'ink2')
          + t(320, 172, 'Opening the jar (reading the first bytes) tells you what is really inside.', 9.4, 'acc', bold=True)
          + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('File types at four depths', [
    ('v', 'No jargon: jars with labels', '''      <p>Think of jars in a kitchen.</p>''' + labels + '''
      <ul>
        <li>A file name, including <code>.txt</code> or <code>.jpg</code>, is just a <b>label</b> on the jar. Labels can be wrong or missing.</li>
        <li>The <code>file</code> command <b>opens the jar</b> and looks at the first bytes to tell you what is really inside.</li>
        <li>Some things in the kitchen are not jars at all: a cupboard (a folder), a note saying “see the other shelf” (a link), a tap (a device). Linux has those too.</li>
        <li>Jars pushed to the back of the shelf are <b>hidden files</b>: their names start with a dot.</li>
      </ul>'''),
    ('b', 'What you need every day', '''      <ul>
        <li>The first letter in <code>ls -l</code> is the type: <code>-</code> regular file, <code>d</code> directory, <code>l</code> symbolic link (plus <code>c</code>, <code>b</code>, <code>p</code>, <code>s</code> for special files).</li>
        <li><code>file name</code> tells you the format: “ASCII text”, “PNG image data”, “ELF 64-bit executable”, “gzip compressed data”.</li>
        <li>Names starting with <code>.</code> are hidden from plain <code>ls</code>; <code>ls -a</code> shows them (and <code>.</code>, <code>..</code>), <code>ls -A</code> shows them without <code>.</code> and <code>..</code>.</li>
        <li>Settings live in hidden files in your home: <code>.bashrc</code>, <code>.profile</code>, <code>.ssh/</code>, <code>.gitconfig</code>.</li>
      </ul>'''),
    ('i', 'stat and the three times', '''      <ul>
        <li><code>stat file</code> shows everything the inode stores: size, blocks, inode number, links, permissions, owner, and the times.</li>
        <li><b>atime</b> = last read (Access), <b>mtime</b> = content last changed (Modify), <b>ctime</b> = inode last changed (Change: content, permissions, owner, rename). ctime is <b>not</b> creation time.</li>
        <li>Newer file systems also record <b>Birth</b> (creation) time, shown by stat on ext4 and xfs.</li>
        <li><code>stat -c</code> prints only what you ask for: <code>stat -c '%F %s %n' file</code> = type, size, name.</li>
        <li><code>file -i</code> prints a MIME type (<code>image/jpeg</code>), as web servers use; <code>file</code> often adds “with CRLF line terminators” for Windows text files, but not for every format (recent versions just say “CSV ASCII text”), so for data files check with <code>grep -c $'\\r'</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: mode bits and magic', '''      <ul>
        <li>The type is stored in the top bits of the inode’s 16-bit <code>st_mode</code> field, next to the permission bits. <code>ls</code> and <code>stat</code> read it with the <code>statx()</code> system call.</li>
        <li>Device files (<code>c</code>, <code>b</code>) hold no data: they carry a <b>major, minor</b> number pair (shown by <code>ls -l</code> instead of a size) that tells the kernel which driver to call. <code>/dev/null</code> is 1, 3.</li>
        <li>Named pipes (<code>p</code>, created with <code>mkfifo</code>) and Unix sockets (<code>s</code>) are meeting points between processes; their data passes through kernel memory, never the disk.</li>
        <li><code>file</code> uses the <b>libmagic</b> database: it compares the first bytes (and more) against thousands of signatures, e.g. <code>FF D8 FF</code> = JPEG, <code>89 50 4E 47</code> = PNG, <code>7F 45 4C 46</code> = ELF.</li>
        <li>atime updates are expensive, so Linux mounts with <code>relatime</code> by default: atime is updated only if it is older than mtime or more than a day old.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>File types, file, stat and hidden files</h2>
''' + def_block(
    'Every file system object has a <b>file type</b> stored in its inode: regular file, directory, symbolic link, character device, block device, named pipe (FIFO) or socket. <code>ls -l</code> shows it as the first character of the mode. A file’s <b>name</b>, including any extension, carries no type information for the kernel. The <code>file</code> command classifies a file’s <b>content</b> by testing it against known signatures (magic numbers); <code>stat</code> displays the inode’s metadata. A <b>hidden file</b> is one whose name begins with a dot; listing tools omit such names unless asked.',
    'The kernel knows the kind of object; <code>file</code> guesses the format from the bytes; the extension is just a name.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('File types', f'- d l c b p s. {gl("file-types", "Glossary →")}'),
    ('Inode', f'The record that stores a file’s type and details. {gl("inode", "Glossary →")}'),
    ('Hidden file (dotfile)', f'A name starting with a dot. {gl("hidden-file-dotfile", "Glossary →")}'),
    ('Magic number', 'The first bytes that identify a format (FF D8 FF = JPEG).'),
    ('Device file', f'A file in /dev that leads to a driver. {gl("block-device", "Glossary →")}'),
    ('Named pipe', f'A FIFO file connecting two processes. {gl("pipe", "Glossary →")}'),
    ('Socket', f'A meeting point for process communication. {gl("socket-and-listening", "Glossary →")}'),
    ('atime / mtime / ctime', f'Last read / content changed / inode changed. {gl("unix-epoch-and-timestamps", "Glossary →")}'),
]) + '\n' + names('Letters and names in this lesson.', [
    ('-', 'regular file', 'Text, images, programs, archives: any normal data.'),
    ('d', 'directory', 'A folder: a list of names → inodes.'),
    ('l', 'link (symbolic)', 'A pointer to another path.'),
    ('c / b', 'character / block device', 'Byte-by-byte devices (terminals) / block devices (disks).'),
    ('p', 'pipe (named, FIFO)', 'First In, First Out: one process writes, another reads.'),
    ('s', 'socket', 'Two-way communication endpoint, e.g. /run/docker.sock.'),
    ('stat', 'status', 'Shows the full status of an inode.'),
    ('file', 'file (type)', 'Determines the type of content.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Seven types', '<code>-</code> file · <code>d</code> dir · <code>l</code> link · <code>c</code> char dev · <code>b</code> block dev · <code>p</code> pipe · <code>s</code> socket'),
    ('What is this file?', '<code>file name</code> (content) · <code>stat -c %F name</code> (kind)'),
    ('Extension', 'Only part of the name; Linux does not need one'),
    ('Hidden files', '<code>ls -a</code> (with . and ..) or <code>ls -A</code>'),
    ('ctime', 'Change time of the inode, <b>not</b> creation time'),
    ('Devices', 'Show major, minor instead of size: <code>/dev/null</code> = 1, 3'),
]) + '\n' + lv + didyou('The dot rule for hidden files started as a <b>bug</b>. In early Unix, <code>ls</code> skipped <code>.</code> and <code>..</code> by checking only whether a name began with a dot. That accidentally hid every name starting with a dot, and programmers began using it on purpose for configuration files. The “feature” has stayed for about fifty years.') + '''
EXAM> “Explain the different types of files in Linux” → list all seven with their ls -l letter and an example each (/etc/passwd, /home, /bin → usr/bin, /dev/tty, /dev/sda, a mkfifo pipe, /run/docker.sock); say that the type is stored in the inode and that extensions are not used by the kernel.
''' + qc('<code>ls -l</code> shows <code>crw-rw-rw- 1 root root 1, 3 ... /dev/null</code>. What type is it, and what is <code>1, 3</code>?', 'A character device. <code>1, 3</code> are the major and minor numbers: they select the kernel driver (major 1 = memory devices, minor 3 = null).') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The seven file types</h2>
''' + table(['Letter', 'Type', 'Example', 'Create with', 'file says'], [
    ['<code>-</code>', 'regular file', '<code>/etc/passwd</code>, photos, programs', 'touch, editors, cp', 'ASCII text, JPEG image data, ELF…'],
    ['<code>d</code>', 'directory', '<code>/home</code>, <code>~/lab</code>', 'mkdir', 'directory'],
    ['<code>l</code>', 'symbolic link', '<code>/bin → usr/bin</code>', 'ln -s', 'symbolic link to …'],
    ['<code>c</code>', 'character device', '<code>/dev/null</code>, <code>/dev/tty</code>', 'kernel / udev (mknod)', 'character special (1/3)'],
    ['<code>b</code>', 'block device', '<code>/dev/sda</code>, <code>/dev/nvme0n1</code>, <code>/dev/loop0</code>', 'kernel / udev (mknod)', 'block special'],
    ['<code>p</code>', 'named pipe (FIFO)', 'a pipe between two programs', 'mkfifo', 'fifo (named pipe)'],
    ['<code>s</code>', 'socket', '<code>/run/docker.sock</code>, <code>/run/systemd/journal/socket</code>', 'programs (bind)', 'socket'],
], minw=640) + '''
  <h3>Common content formats and their magic bytes</h3>
''' + table(['Format', 'First bytes (hex)', 'file says'], [
    ['JPEG photo', '<code>FF D8 FF</code>', 'JPEG image data'],
    ['PNG image', '<code>89 50 4E 47</code> (“.PNG”)', 'PNG image data'],
    ['PDF', '<code>25 50 44 46</code> (“%PDF”)', 'PDF document'],
    ['ZIP (also .docx, .xlsx, .jar)', '<code>50 4B 03 04</code> (“PK”)', 'Zip archive data'],
    ['gzip', '<code>1F 8B</code>', 'gzip compressed data'],
    ['Linux program', '<code>7F 45 4C 46</code> (“.ELF”)', 'ELF 64-bit LSB executable'],
    ['Script', '<code>23 21</code> (“#!”)', 'Bourne-Again shell script'],
], minw=480) + didyou('A <code>.docx</code> or <code>.xlsx</code> file is really a ZIP archive of XML files, which is why <code>file</code> may report “Microsoft Word 2007+” or “Zip archive data”, and why <code>unzip report.docx</code> works.') + qc('Which letter does <code>ls -l</code> show for a named pipe made with <code>mkfifo</code>?', '<code>p</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Investigating an unknown file</h2>
''' + stepper([
    ('1. What kind of object?', '<p><code>ls -l mystery</code>: look at the first letter.</p>', 'Behind the screen: ls calls statx() and decodes the type bits of st_mode.'),
    ('2. If it is a link, where to?', '<p><code>ls -l</code> shows <code>name -&gt; target</code>; <code>file -L</code> describes the target.</p>', 'Behind the screen: lstat() looks at the link itself, stat() follows it.'),
    ('3. What format is the content?', '<p><code>file mystery</code> (or <code>file -i</code> for a MIME type).</p>', 'Behind the screen: libmagic reads the first bytes and tests them against its signature database.'),
    ('4. Look at the bytes yourself', '<p><code>head -c 16 mystery | od -An -tx1</code></p>', 'Behind the screen: od prints the raw bytes in hexadecimal; compare with the magic-bytes table.'),
    ('5. Size, owner and times', '<p><code>stat mystery</code></p>', 'Behind the screen: every line of stat is a field of the inode.'),
    ('6. Safe to view?', '<p>Text: <code>less</code>. Binary: do not <code>cat</code> it (it can mess up your terminal; type <code>reset</code> if that happens).</p>', 'Behind the screen: binary bytes can be terminal control codes.'),
]) + qc('<code>file report</code> says “gzip compressed data”. How would you read it?', '<code>zcat report | less</code> (or <code>gunzip -c report</code>): it is compressed, whatever its name says.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def bytes_row(hl, y=120):
    bs = ['FF', 'D8', 'FF', 'E0', '00', '10', '4A', '46']
    return ''.join(label_box(14 + k * 41, y, 36, 26, [b], 'acc' if k < hl else 'card', 9) for k, b in enumerate(bs))
see = [term(20, 18, 320, 96, ['$ ls', ('photo.jpg', 'out'), '$ mv photo.jpg photo.txt'], title='riya@laptop') + t(180, 140, 'Only the name changes.', 9, 'ink2'),
       term(20, 18, 320, 96, ['$ cat photo.txt', ('����JFIF���...', 'err')], title='riya@laptop') + t(180, 140, 'cat prints the bytes: garbage on screen.', 9, 'ink2'),
       term(20, 18, 320, 96, ['$ file photo.txt', ('photo.txt: JPEG image data, JFIF', 'acc'), ('standard 1.01', 'acc')], title='riya@laptop') + t(180, 140, 'file looks inside: still a JPEG.', 9, 'green', bold=True),
       term(20, 18, 320, 96, ['$ file -i photo.txt', ('photo.txt: image/jpeg; charset=binary', 'acc')], title='riya@laptop') + t(180, 140, 'MIME type, as web servers use it.', 9, 'ink2'),
       term(20, 18, 320, 96, ['$ stat -c %F photo.txt', ('regular file', 'acc')], title='riya@laptop') + t(180, 140, 'The kernel only knows: a regular file.', 9, 'ink2')]
behind = [label_box(14, 20, 160, 46, ['directory entry', 'photo.jpg → inode 794811'], 'card', 8.6) + arrow(176, 43, 196, 43, 'acc', 2) + label_box(198, 20, 150, 46, ['directory entry', 'photo.txt → inode 794811'], 'acc', 8.6) + t(180, 100, 'mv only rewrote the name in the directory.', 8.8, 'ink2') + t(180, 118, 'Same inode, same bytes.', 8.8, 'acc', bold=True),
          bytes_row(0, 40) + t(180, 100, 'The content is bytes. cat sends them to the terminal,', 8.8, 'ink2') + t(180, 116, 'which tries to draw them as letters.', 8.8, 'ink2'),
          bytes_row(3, 40) + t(180, 100, 'libmagic reads the first bytes: FF D8 FF.', 8.8, 'ink2') + t(180, 116, 'Its database says: JPEG. JFIF in bytes 7–10 confirms it.', 8.8, 'acc', bold=True),
          bytes_row(3, 40) + label_box(60, 96, 240, 40, ['magic database', '/usr/share/misc/magic.mgc'], 'blue', 8.8) + t(180, 160, 'Thousands of signatures: JPEG, PNG, PDF, ELF…', 8.6, 'ink2'),
          label_box(14, 20, 332, 46, ['inode 794811: st_mode = 0100644', 'type bits 0100000 = regular file · 0644 = rw-r--r--'], 'violet', 8.6) + t(180, 100, 'The kernel stores the kind of object, not the format.', 8.8, 'ink2') + t(180, 118, 'Format detection is a user-space tool’s job.', 8.8, 'acc', bold=True)]
two = anim_two('Rename a photo, then ask Linux', 'Name, inode and magic bytes', 'A terminal: a photo renamed to .txt, cat prints garbage, file still reports JPEG, file -i gives image/jpeg, stat says regular file.',
               'The directory entry changing, the first bytes FF D8 FF being matched against the magic database, and the inode mode bits.', see, behind,
               ['Riya renames <code>photo.jpg</code> to <code>photo.txt</code>.',
                '<code>cat</code> prints the raw bytes, which are not text.',
                '<code>file</code> still reports a JPEG: it ignored the name.',
                '<code>file -i</code> gives the MIME type <code>image/jpeg</code>.',
                'To the kernel it is simply a regular file.'],
               ['A rename only changes the name stored in the directory. The inode and the bytes are untouched.',
                'The file’s content is a series of bytes; the first ones of a JPEG are <code>FF D8 FF E0</code>.',
                '<code>file</code> compares those bytes with known signatures, the “magic numbers”.',
                'The signatures come from the compiled magic database installed with the tool.',
                'The inode’s mode says “regular file” plus permissions. That is all the kernel needs.'])

# scenario 1: hidden files
h1 = term(14, 14, 332, 104, ['$ ls', ('lab  notes.txt', 'out'), ('# where is my .bashrc?', 'dim')], title='riya@laptop', size=7.8) + cap('Plain ls hides names starting with a dot.', '', 'card', y=150, h=34)
h2 = term(14, 14, 332, 104, ['$ ls -a', ('.  ..  .bash_logout  .bashrc  .profile', 'acc'), ('.ssh  lab  notes.txt', 'out')], title='riya@laptop', size=7.8) + cap('ls -a: everything, including . and ..', '', 'blue', y=150, h=34)
h3 = term(14, 14, 332, 104, ['$ ls -A', ('.bash_logout  .bashrc  .profile  .ssh', 'acc'), ('lab  notes.txt', 'out')], title='riya@laptop', size=7.8) + cap('ls -A: hidden files without . and ..', '', 'blue', y=150, h=34)
h4 = term(14, 14, 332, 104, ['$ ls -d .[!.]*', ('.bash_logout  .bashrc  .profile  .ssh', 'acc')], title='riya@laptop', size=7.8) + cap('Only the hidden ones.', '', 'blue', y=150, h=34)
h5 = (t(180, 30, 'Hidden ≠ secret', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• anyone with read permission can list them', '• security comes from permissions (Module 9)', '• dotfiles = settings: .bashrc, .ssh, .gitconfig', '• projects: .git, .env, .gitignore'])) + cap('The dot only reduces clutter.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', '“My settings file has disappeared!”',
              'Riya edited <code>~/.bashrc</code> yesterday and today cannot find it. Example listing of a fresh Ubuntu home folder.',
              'Finding hidden files', 'ls hides dotfiles; ls -a shows all with . and ..; ls -A without them; ls -d .[!.]* only hidden ones.', [h1, h2, h3, h4, h5],
              ['Plain <code>ls</code> shows only two names. Is .bashrc gone?',
               '<code>ls -a</code> shows everything, including <code>.</code> and <code>..</code>.',
               '<code>ls -A</code> is the cleaner version without <code>.</code> and <code>..</code>.',
               'The pattern <code>.[!.]*</code> matches names that start with one dot followed by something other than a dot.',
               'Hidden files hide clutter, not secrets. Protect secrets with permissions.'],
              hid='scenario-hidden')

# scenario 2: the three times
m = lambda a, mo, c, hl: ''.join(label_box(14 + k * 112, 26, 104, 50, [n, v], 'acc' if n[0] in hl else 'card', 8.6) for k, (n, v) in enumerate([('atime (read)', a), ('mtime (content)', mo), ('ctime (inode)', c)]))
x1 = m('10:00', '10:00', '10:00', 'amc') + t(180, 110, '$ echo hello > notes   (10:00)', 9, 'ink2', mono=True) + cap('A new file: all three times are equal.', '', 'card', y=150, h=34)
x2 = m('10:00', '10:05', '10:05', 'mc') + t(180, 110, '$ echo more >> notes   (10:05)', 9, 'ink2', mono=True) + cap('Content changed: mtime and ctime move.', '', 'blue', y=150, h=34)
x3 = m('10:00', '10:05', '10:10', 'c') + t(180, 110, '$ chmod 600 notes   (10:10)', 9, 'ink2', mono=True) + cap('Permissions changed: only ctime moves.', '', 'blue', y=150, h=34)
x4 = m('10:20', '10:05', '10:10', 'a') + t(180, 110, '$ cat notes   (10:20)', 9, 'ink2', mono=True) + cap('Reading moves atime: it was older than mtime.', '', 'blue', y=150, h=34)
x5 = (t(180, 30, 'Where the times matter', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• mtime: ls -lt, backups, make, “what changed?”', '• ctime: security checks (permission changes)', '• atime: “is anyone still reading this?”', '• Birth: creation time on ext4/xfs (stat)'])) + cap('ctime is Change time, not creation time.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Three clocks on every file: atime, mtime, ctime',
              'An auditor asks: “When was this file changed, and when were its permissions changed?” stat answers both. Times are examples.',
              'atime, mtime and ctime', 'Creating, appending to, chmod-ing and reading a file, and which of the three timestamps changes each time.', [x1, x2, x3, x4, x5],
              ['When the file is created, all three times are the same.',
               'Writing new content updates mtime; because the inode changed too (new size), ctime moves as well.',
               '<code>chmod</code> changes only the inode, so only ctime moves. mtime keeps the real content time.',
               'Reading updates atime, but with the default <code>relatime</code> only if atime was older than mtime (or a day old).',
               'Remember: ctime is change time. The creation time is “Birth”, shown by stat on modern file systems.'],
              hid='scenario-times')

# scenario 3: special files
y1 = term(14, 14, 332, 104, ['$ ls -l /dev/null /dev/loop0', ('crw-rw-rw- 1 root root 1, 3 /dev/null', 'acc'), ('brw------- 1 root root 7, 0 /dev/loop0', 'acc')], title='riya@laptop', size=7.6) + cap('c and b: devices. 1, 3 = driver numbers, not a size.', '', 'blue', y=150, h=34)
y2 = term(14, 14, 332, 104, ['$ mkfifo orders', '$ ls -l orders', ('prw-r--r-- 1 riya riya 0 Nov 5 orders', 'acc')], title='terminal 1', size=7.6) + cap('p: a named pipe. Size 0, it stores nothing.', '', 'blue', y=150, h=34)
y3 = (term(14, 14, 160, 104, ['$ cat orders', ('(waiting...)', 'dim'), ('order 1001', 'acc')], title='terminal 1: reader', size=7.4)
      + term(186, 14, 160, 104, ['$ echo "order 1001" \\', '    > orders'], title='terminal 2: writer', size=7.4) + cap('One process writes, the other reads, through the kernel.', '', 'green', y=150, h=34))
y4 = term(14, 14, 332, 104, ['$ ls -l /run/docker.sock', ('srw-rw---- 1 root docker 0 /run/docker.sock', 'acc')], title='riya@laptop', size=7.6) + cap('s: a socket. The docker command talks to its daemon here.', '', 'blue', y=150, h=34)
y5 = (t(180, 30, 'Special files', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• c, b: lead to kernel drivers (Module 15 for disks)', '• p: simple one-way link between two programs', '• s: two-way, used by Docker, databases, systemd', '• none of them keeps data on disk'])) + cap('Same tools (ls, stat, permissions) for all.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Files that are not files: devices, pipes and sockets',
              'The other four letters, as you meet them on real servers. Listings shortened; the pipe demo uses two terminals.',
              'Special files', 'Device files with major and minor numbers, a named pipe passing a message between two terminals, and the Docker socket.', [y1, y2, y3, y4, y5],
              ['Device files show two numbers where the size would be: the major (driver) and minor (which device).',
               '<code>mkfifo</code> creates a named pipe. It has size 0: data never lands on the disk.',
               'Terminal 1 waits on <code>cat orders</code>; when terminal 2 writes, the message passes straight through.',
               'Docker’s command talks to the Docker daemon through a Unix socket; its group decides who may use it.',
               'Everything is a file: the same listing and permission tools work for all seven types.'],
              hid='scenario-special')

dx = dissect('Layer by layer: dissect the output of <code>stat</code>',
    'Open each line of <code>stat notes</code>: what it means, why it exists, where it is stored, and when you will use it. Each comes with the real value for a fresh file on our build machine.', [
    dict(key='file', name='File / Size / Blocks', sub='name, bytes, space used',
         why='The size is what you see; Blocks is the disk space really used, which can differ.',
         how='Size = bytes of content (6 for “hello” + newline). Blocks counts 512-byte units allocated: 8 = 4 KiB, the smallest piece ext4 gives out.',
         impl='Size and block count fields of the inode. “IO Block” is the preferred read size.', used='Explaining why <code>du</code> and <code>ls -l</code> disagree; sparse files.',
         setup='echo hello > notes', cmd="stat -c 'File: %n  Size: %s  Blocks: %b  IO Block: %o  %F' notes"),
    dict(key='inode', name='Device / Inode / Links', sub='where the inode is',
         why='A file is really identified by (device, inode number), not by its name.',
         how='Device = which file system; Inode = the record number inside it; Links = how many names point to it.',
         impl='The inode table of the file system (Lesson 10.1).', used='Hard links, finding files by inode, “disk full but df shows space” (out of inodes).',
         setup='echo hello > notes', cmd="stat -c 'Device: %D  Inode: %i  Links: %h' notes"),
    dict(key='access', name='Access (0644/-rw-r--r--)', sub='type and permissions',
         why='Who may read, write or run the file.',
         how='The mode in octal and letters. The type bits sit in the same field (here: regular file).',
         impl='st_mode in the inode.', used='Every permission problem (Module 9).',
         setup='echo hello > notes', cmd="stat -c 'Access: (%a/%A)  type: %F' notes"),
    dict(key='uid', name='Uid / Gid', sub='owner and group',
         why='Permissions are applied to one user and one group.',
         how='Stored as numbers; stat also prints the names from /etc/passwd and /etc/group.',
         impl='uid and gid fields of the inode.', used='Files owned by a deleted user show only a number; chown fixes it.',
         setup='echo hello > notes', cmd="stat -c 'Uid: (%u/%U)  Gid: (%g/%G)' notes"),
    dict(key='times', name='Access / Modify / Change', sub='the three times',
         why='When was it read, when did its content change, when did its inode change?',
         how='atime, mtime and ctime with nanoseconds and time zone. A <code>chmod</code> one second later moves only Change.',
         impl='Three timestamp fields of the inode, in seconds since 1970 (the Unix epoch) plus nanoseconds.', used='Backups (mtime), audits (ctime), cleanup of unused files (atime).',
         setup='echo hello > notes', cmd="sleep 1; chmod 600 notes; stat --printf 'Modify: %y\\nChange: %z\\n' notes"),
    dict(key='birth', name='Birth', sub='creation time',
         why='The question everyone asks: “when was this created?”',
         how='Recorded by newer file systems (ext4, xfs, btrfs); shown as “-” when unknown.',
         impl='The crtime field of the inode, read through statx().', used='Forensics, “which file appeared first?”.',
         setup='echo hello > notes', cmd="stat -c 'Birth: %w' notes"),
], hint='Six lines of stat, six fields of one inode. Click a line.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How Linux knows what a file is</h2>
  <p>Left: Riya’s terminal. Right: the directory entry, the bytes and the inode behind each answer.</p>
''' + two + '''
  <p>Three real-time scenarios: hidden settings files, the three timestamps, and the special file types.</p>
''' + s1 + s2 + s3 + dx + qc('After <code>chmod 600 notes</code>, which of atime, mtime and ctime changes?', 'Only ctime: the inode changed, the content did not.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>File types at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ file upload', 'prompt'), ('PHP script', 'err')], title='upload', size=6.4, step=12),
              '1. Upload checks', 'Web apps should check uploads by content (as <code>file -i</code> does), not by extension: a script renamed <code>cat.jpg</code> is still a script.', ['Upload', '*check bytes', 'reject fakes']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ file -i data.csv', 'prompt'), ('utf-16le', 'acc')], title='data', size=6.4, step=12),
    '2. Data engineering: check before loading', 'Before loading a file, <code>file -i</code> reveals the real format and encoding (a “CSV” that is really a ZIP, or UTF-16 text) that would break a pipeline.', ['File arrives', '*file -i', 'clean first']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['.env  .git', 'dotfiles'], 'violet', 8.6), '3. Developers: dotfiles',
    'Project settings and secrets live in hidden files (<code>.env</code>, <code>.git</code>). <code>ls -A</code> before copying or zipping a project avoids leaking them.', ['Package', '*ls -A', 'no leaks']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ stat -c %z', 'prompt'), ('/etc/passwd', 'acc')], title='audit', size=6.4, step=12),
    '4. Security audits', 'Investigators compare mtime and ctime: a file whose ctime is recent but mtime old had its permissions or owner changed.', ['Alert', '*stat times', 'timeline']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['srw-rw----', 'docker.sock'], 'blue', 8.6), '5. Containers and services',
    'Docker, databases and systemd talk through socket files in <code>/run</code>; their permissions decide who may control them.', ['docker ps', '*socket', 'daemon']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('File-type tricks. All were really run on our Ubuntu build machine.', [
    dict(level='b', title='What is everything in this folder?', scenario='A folder of downloads with confusing names.',
         setup=JPEG + " && echo 'hello' > readme && gzip -k readme && mkdir docs", cmd='file *', files_note='a photo, a text file, its gzip copy and a folder.',
         explain='<code>file</code> accepts many names; the shell expands <code>*</code>.'),
    dict(level='b', title='Only the hidden entries', scenario='Check which dotfiles a project contains before sharing it.',
         setup="mkdir app && cd app && touch .env .gitignore main.py && mkdir .git", cmd='ls -d .[!.]*', files_note='a project with .env, .gitignore and .git.',
         explain='The pattern means: a dot, then any character except a dot, then anything.'),
    dict(level='i', title='Count objects by type', scenario='A quick inventory of a folder: how many files, folders, links?',
         setup='mkdir -p d1 d2 && touch a b c && ln -s a la && mkfifo p1', cmd='stat -c %F * | sort | uniq -c',
         files_note='3 files, 2 folders, 1 link, 1 pipe.', explain='<code>%F</code> prints the type in words (touch makes <b>empty</b> regular files); <code>sort | uniq -c</code> counts each.'),
    dict(level='a', title='Find CSV files with Windows line endings', scenario='A data load fails on some files only.',
         setup="printf 'a,b\\r\\n1,2\\r\\n' > jan.csv && printf 'a,b\\n1,2\\n' > feb.csv", cmd="file *.csv; grep -l $'\\r' *.csv",
         files_note='one Windows-style and one Linux-style CSV.', explain='Both look the same to <code>file</code> (“CSV ASCII text”). <code>grep -l $\'\\r\'</code> lists the files that contain a carriage return (\\r), the Windows line-ending byte.'),
], extra=build_up('what a mystery download really is', 'A colleague sends <code>invoice</code> with no extension. Find out what it is, step by step.',
    "echo 'JVBERi0xLjQKJcOkw7zDtsOfCjEgMCBvYmoKPDwvVHlwZS9DYXRhbG9nPj4KZW5kb2JqCnRyYWlsZXIKPDwvUm9vdCAxIDAgUj4+CiUlRU9GCg==' | base64 -d > invoice", [
    ('ls -l invoice', 'A regular file of a few bytes, no clue about the format.'),
    ('file invoice', 'libmagic recognises a PDF.'),
    ('file -i invoice', 'The MIME type, as a browser would need it.'),
    ('head -c 8 invoice | od -An -c', 'See the magic yourself: %PDF-1.4'),
])) + which('File-type situations.', [
    ('What format is this file?', 'file name', 'Reads the content.', 'Trusting the extension.'),
    ('What kind of object is it?', 'ls -l / stat -c %F', 'Inode type: - d l c b p s.', 'file on a device (needs permissions).'),
    ('See hidden files', 'ls -A', 'All but . and ..', 'ls (hides dotfiles)'),
    ('When did the content change?', 'stat -c %y', 'mtime.', 'ctime (also moves on chmod).'),
    ('When were permissions changed?', 'stat -c %z', 'ctime.', 'Thinking ctime = creation.'),
    ('When was it created?', 'stat -c %w', 'Birth on ext4/xfs.', 'ls -l (shows mtime).'),
    ('Is this CSV from Windows?', "grep -c $'\\r' data.csv", 'Counts lines with \\r.', 'Relying on file (may just say CSV text).'),
    ('Look at raw bytes', 'od -An -tx1', 'Hex dump, always installed.', 'cat on a binary file.'),
]) + puzzle_answer('By reading the content. Most formats begin with a fixed signature, a “magic number”: a JPEG starts with the bytes <code>FF D8 FF</code>, a PNG with <code>89 50 4E 47</code>, a PDF with <code>%PDF</code>. The <code>file</code> command compares the first bytes with its magic database, so the name, including the extension, does not matter. Renaming only changes the directory entry; the inode and the bytes stay the same.') + qc('What is the difference between <code>ls -a</code> and <code>ls -A</code>?', '<code>-a</code> shows all entries including <code>.</code> and <code>..</code>; <code>-A</code> shows hidden entries but leaves out those two.') + '''
</section>
'''

body = (cmap + story.replace('  <div class="story">', before('<a href="../02-moving-around-pwd-cd-and-ls/">Lesson 2.2</a>: the columns of <code>ls -l</code>.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
