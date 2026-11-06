import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap
BODY = body(HERE)

JPEG = r"printf '\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9' > photo.jpg"

META = dict(
    module='02-file-system', lesson='04-file-types-and-hidden-files-file-stat-and-ls-la', n='2.4',
    module_label='Module 2 · The Linux file system',
    title='File types and hidden files: file, stat and ls -la',
    desc='Linux file types explained: the seven types (- d l c b p s), why extensions do not matter, the file command and magic numbers, stat and the three timestamps atime, mtime and ctime (plus Birth), device major and minor numbers, named pipes, sockets, and hidden dotfiles with ls -a and ls -A. Animations, real Bash and interview questions.',
    og_desc='Rename a photo to .txt and Linux still knows it is a photo. File types, file, stat and hidden files explained.',
    minutes=30, level='Beginner → Advanced',
    lead='Riya renames a photo to photo.txt and Linux still calls it a JPEG. This lesson explains how Linux really knows what a file is: the seven file types stored in the inode, the file command and magic bytes, everything stat tells you including the three timestamps, and the hidden dotfiles where all your settings live.',
    chips=['Story-based', '4 animations', 'Layer-by-layer', 'Real Bash in your browser'],
)

MAIN = JPEG + '''
mv photo.jpg photo.txt
echo "hello" > notes
mkdir docs
ln -s notes shortcut
touch .settings
ls
ls -A
ls -l | cut -c1-10
file photo.txt notes docs shortcut
stat -c '%n is a %F of %s bytes' notes docs
'''

RUN = dict(
    heading='Make one of each and ask Linux',
    intro='<p>The script creates a photo (then renames it to .txt), a text file, a folder, a link and a hidden file, and asks <code>ls</code>, <code>file</code> and <code>stat</code> about them. The first line writes the first bytes of a real JPEG with <code>printf</code>. The output was recorded on our Ubuntu build machine.</p>',
    code=MAIN,
    anno=[
        ('mv photo.jpg photo.txt', 'Only the name changes.'),
        ('ln -s notes shortcut', 'A symbolic link (Lesson 10.2).'),
        ('touch .settings', 'A name starting with a dot: hidden.'),
        ('ls -A', 'Now .settings appears.'),
        ('ls -l | cut -c1-10', 'Only the type and permission letters of each line (the first line is “total”).'),
        ('file photo.txt notes docs shortcut', 'Content and kind of each name; the photo is still a JPEG.'),
        ("stat -c '%n is a %F of %s bytes' notes docs", 'Your own stat format: name, type, size.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which letter in the <code>ls -l</code> column belongs to the link?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what will <code>file</code> say about a file containing only <code>#!/bin/bash</code>? Then run.',
             code="echo '#!/bin/bash' > setup\nfile setup\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the hidden file is not listed. Add the right option.',
             code='touch .env app.py\nls\n'),
        dict(label='4 · Your turn', hint='Create a named pipe <code>jobs</code> and show its type letter and its type in words.',
             code='mkfifo jobs\nls -l jobs | cut -c1\nstat -c %F jobs\n'),
        dict(label='5 · Challenge', hint='Show that <code>chmod</code> changes ctime but not mtime.',
             code="echo data > f\nsleep 1\nchmod 600 f\nstat --printf 'mtime %y\\nctime %z\\n' f\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: types on your own Linux',
    intro='<p>Try these on your own Linux. <b>Outputs were recorded on our Ubuntu 24.04 build machine</b> unless marked typical.</p>',
    items=[
        dict(title='1 · Device files and their numbers', cmd='ls -l /dev/null /dev/zero /dev/tty /dev/loop0', output=pc('ls -l /dev/null /dev/zero /dev/tty /dev/loop0'),
             note='<code>c</code> = character device, <code>b</code> = block device. The two numbers are major, minor.'),
        dict(title='2 · Your hidden settings', cmd='ls -A ~', output=pc('ls -A ~'),
             note='A fresh Ubuntu account starts with .bash_logout, .bashrc and .profile. Yours will have many more (.cache, .ssh, .config…).'),
        dict(title='3 · Programs are files too', cmd='file /usr/bin/ls /usr/bin/zcat', output=pc('file /usr/bin/ls /usr/bin/zcat'),
             note='ls is a compiled ELF program; zcat is a shell script. Both run the same way.'),
        dict(title='4 · Real disks on a laptop', cmd='ls -l /dev/sda /dev/sda1 /dev/nvme0n1', output='ls: cannot access \'/dev/sda\': No such file or directory\nls: cannot access \'/dev/sda1\': No such file or directory\nbrw-rw---- 1 root disk 259, 0 Nov  5 09:12 /dev/nvme0n1',
             note='Typical output on a laptop with an NVMe SSD (our build container has no real disks). Older machines and VMs use <code>/dev/sda</code>.'),
        dict(title='5 · Sockets in /run', cmd='find /run -type s 2>/dev/null | head -3', output='/run/systemd/notify\n/run/systemd/journal/stdout\n/run/systemd/journal/socket',
             note='Typical output on Ubuntu with systemd (our build container does not run systemd). <code>-type s</code> finds sockets.'),
    ],
)

TRACE = dict(
    heading='Watching the three timestamps',
    intro='<p>The script creates a file, changes its content, then only its permissions, and prints mtime and ctime after each step. Watch the <b>Files</b> box and the output.</p>',
    code='''echo "v1" > report
stat -c 'mtime %Y  ctime %Z' report
sleep 1
echo "v2" >> report
stat -c 'mtime %Y  ctime %Z' report
sleep 1
chmod 600 report
stat -c 'mtime %Y  ctime %Z' report
''',
    notes={1: 'Create :: A new file: all times equal.', 2: 'Read the clocks :: %Y and %Z print mtime and ctime as seconds since 1970.',
           4: 'New content :: mtime and ctime both move.', 7: 'Permissions only :: Only ctime moves.'},
)

WORKED_INTRO = 'Three real tasks: an inventory of a folder, catching a disguised upload, and finding files whose permissions changed recently.'
EXAMPLES = [
    dict(level='b', tag='Inventory', title='Label everything in a folder',
         problem='<p>Print one line per entry in a folder: its type letter and name, with hidden entries included.</p>',
         inp='a folder with a file, a hidden file, a folder and a link',
         approach=['<code>ls -lA</code> shows all entries with details.', '<code>awk</code> prints the first character of column 1 and column 9, the name.'],
         code='''touch report.txt .config && mkdir archive && ln -s report.txt latest
ls -lA | awk 'NR>1 {print substr($1,1,1), $9}'
''',
         notes={2: 'Pick fields :: NR>1 skips the “total” line; column 9 is the name (for the link, ls adds -> target after it).'},
         tryit='Add <code>mkfifo q</code> before the listing. Which letter appears?'),
    dict(level='i', tag='Security', title='Catch a disguised upload',
         problem='<p>An upload folder should contain only images. Flag every file whose real MIME type is not <code>image/*</code>, whatever its extension.</p>',
         inp='cat.jpg (real JPEG), dog.jpg (really a shell script), note.png (really text)',
         approach=['<code>file -b --mime-type</code> prints only the MIME type.', 'A <code>case</code> pattern <code>image/*</code> accepts images.'],
         code=JPEG.replace('photo.jpg', 'cat.jpg') + '''
printf '#!/bin/sh\\necho hacked\\n' > dog.jpg
echo "just text" > note.png
for f in *; do
  type=$(file -b --mime-type "$f")
  case $type in
    image/*) echo "OK      $f ($type)" ;;
    *)       echo "REJECT  $f ($type)" ;;
  esac
done
''',
         notes={5: 'Real type :: <code>-b</code> = brief (no file name).', 7: 'Accept :: Any image MIME type.'},
         tryit='Rename cat.jpg to cat.exe and run again. Is it still accepted?'),
    dict(level='a', tag='Business problem', title='Which files had their permissions changed?',
         problem='<p>After an incident, list files in a config folder whose <b>ctime</b> is newer than their <b>mtime</b>: their content was not edited, but their permissions or owner were changed later.</p>',
         inp='three config files; one gets chmod a moment later',
         approach=['<code>stat -c \'%Y %Z %n\'</code> prints mtime, ctime (seconds) and name.', '<code>awk</code> keeps lines where ctime &gt; mtime.'],
         code='''mkdir conf && echo a > conf/app.conf && echo b > conf/db.conf && echo c > conf/cache.conf
sleep 1
chmod 777 conf/db.conf
stat -c '%Y %Z %n' conf/* | awk '$2 > $1 {print "changed later:", $3}'
''',
         notes={3: 'The suspicious change :: Only permissions change, so only ctime moves.', 4: 'Compare :: Field 2 (ctime) greater than field 1 (mtime).'},
         tryit='Append a line to conf/app.conf after the chmod. Is it listed? Why not?'),
]

QUIZ = mix([
    dict(q='What does the first letter d in ls -l mean?', options=['deleted', 'directory', 'device', 'data'], answer=1,
         why='d = directory; - = regular file; l = symbolic link.'),
    dict(q='You rename song.mp3 to song.txt. What does file song.txt report?', options=['ASCII text', 'An MP3 audio file', 'Unknown', 'An error'], answer=1,
         why='file reads the content (magic bytes), not the name.'),
    dict(q='Which ls option shows hidden files but not . and ..?', options=['-a', '-A', '-h', '-H'], answer=1,
         why='-A = almost all.'),
    dict(q='What is ctime?', options=['Creation time', 'Time of the last inode change', 'Time of the last read', 'Copy time'], answer=1,
         why='ctime = change time of the inode (content, permissions, owner…). Creation is “Birth”.'),
    dict(q='Which file type letter is a named pipe?', options=['n', 'p', 's', 'f'], answer=1,
         why='p (FIFO), created with mkfifo.'),
    dict(q='ls -l /dev/sda shows “8, 0” instead of a size. What are these?', options=['Size in KB', 'Major and minor device numbers', 'Partition count', 'Permissions'], answer=1,
         why='Device files show the driver (major) and device (minor) numbers.'),
    dict(q='Why are names like .bashrc hidden?', options=['They are encrypted', 'Names starting with a dot are skipped by ls by default', 'Only root can see them', 'They are in a hidden partition'], answer=1,
         why='Hidden is a listing convention, not security.'),
])

REVISION = [
    'Seven types (first letter of ls -l): <code>-</code> file, <code>d</code> dir, <code>l</code> link, <code>c</code> char device, <code>b</code> block device, <code>p</code> pipe, <code>s</code> socket.',
    'The type is in the inode; the extension is only part of the name.',
    '<code>file</code> identifies content by magic bytes (JPEG FF D8 FF, PNG 89 50 4E 47, ELF 7F 45 4C 46); <code>file -i</code> gives MIME.',
    '<code>stat</code>: size, blocks, inode, links, permissions, owner, atime, mtime, ctime, Birth.',
    'atime = read, mtime = content changed, ctime = inode changed (chmod moves only ctime). Not creation!',
    'Device files show major, minor; pipes and sockets store nothing on disk.',
    'Dotfiles are hidden: <code>ls -a</code> (with . ..), <code>ls -A</code> (without). Hidden ≠ secret.',
    'Check data files before loading: <code>file -i</code> for format, <code>grep -c $\'\\r\'</code> for Windows line endings.',
]

FAQ = [
    ('What are the file types in Linux?', 'Regular file (-), directory (d), symbolic link (l), character device (c), block device (b), named pipe or FIFO (p) and socket (s). The type is stored in the inode and shown as the first character of ls -l.'),
    ('Does Linux use file extensions?', 'The kernel does not. Extensions are just part of the name; some programs use them as hints, but the file command and most tools look at the content.'),
    ('How does the file command work?', 'It runs tests in order: file-system tests (is it a directory, device, link?), magic tests that compare the first bytes with a database of signatures, and language tests for text.'),
    ('What is the difference between mtime, ctime and atime?', 'mtime: last change of the content. ctime: last change of the inode, including permissions, owner and content. atime: last read. None of them is the creation time; modern file systems store that as Birth.'),
    ('How do you show hidden files?', 'ls -a (includes . and ..) or ls -A. Hidden files are those whose names start with a dot.'),
    ('What are /dev/null and /dev/zero?', 'Character devices: /dev/null discards everything written to it and returns end-of-file when read; /dev/zero returns an endless stream of zero bytes.'),
]

PRACTICE_INTRO = 'Tasks about file types, file, stat and hidden files. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Type letter', stmt='Create a folder <code>logs</code> and print only the first letter of its <code>ls -ld</code> line.', inp='logs/',
         code='mkdir logs\nls -ld logs | cut -c1\n', explain='<code>-d</code> lists the folder itself; the first character is its type.'),
    dict(level='easy', title='Show the hidden one', stmt='Create <code>.token</code> and <code>app.py</code>, then list both.', inp='.token, app.py',
         code='touch .token app.py\nls -A\n', explain='-A includes names starting with a dot.'),
    dict(level='easy', title='What is it?', stmt='Ask what kind of file <code>/etc/hostname</code> is.', inp='/etc/hostname',
         code='file /etc/hostname\n', explain='A small plain-text configuration file.'),
    dict(level='medium', title='Type in words', stmt='Print the type in words of <code>/dev/null</code>, <code>/tmp</code> and <code>/etc/passwd</code>.', inp='three paths',
         code="stat -c '%n: %F' /dev/null /tmp /etc/passwd\n", explain='%n = name, %F = type in words.'),
    dict(level='medium', title='Bytes vs space', stmt='Create a 1-byte file and print its size and the disk blocks it uses.', inp='one.txt containing "x" (no newline)',
         code="printf x > one.txt\nstat -c 'size %s bytes, %b blocks of %B bytes' one.txt\n", explain='1 byte of data still takes a whole 4 KiB block (8 × 512).'),
    dict(level='medium', title='Magic bytes', stmt='Print the first 4 bytes of <code>/usr/bin/ls</code> in hex.', inp='/usr/bin/ls',
         code='head -c 4 /usr/bin/ls | od -An -tx1\n', explain='7f 45 4c 46 = “\\x7fELF”, the signature of every Linux program.'),
    dict(level='business', title='Before zipping a project', stmt='Before sending a project to a client, list hidden files and folders inside it that might contain secrets.', inp='project with .env, .git, src/, README.md',
         code='mkdir -p project/src project/.git && touch project/.env project/README.md\ncd project\nls -d .[!.]*\n', explain='.env and .git should usually not be sent. Check before zipping.'),
    dict(level='business', title='Accept only PDFs', stmt='An invoice folder receives files with random names. Print the names of the real PDF files only.', inp='a.pdf (real PDF), b.pdf (text), c (real PDF, no extension)',
         code="pdf='JVBERi0xLjQKJcOkw7zDtsOfCjEgMCBvYmoKPDwvVHlwZS9DYXRhbG9nPj4KZW5kb2JqCnRyYWlsZXIKPDwvUm9vdCAxIDAgUj4+CiUlRU9GCg=='\necho \"$pdf\" | base64 -d > a.pdf\necho \"not a pdf\" > b.pdf\necho \"$pdf\" | base64 -d > c\nfor f in *; do\n  [ \"$(file -b --mime-type \"$f\")\" = application/pdf ] && echo \"$f\"\ndone\n",
         explain='The decision is based on content: c is accepted without an extension, b.pdf is rejected.'),
]

SCN_INTRO = 'Interview questions about file types and metadata, as asked for support, DevOps and security roles.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How many types of files are there in Linux?”',
        'A classic first-round question.',
        'can you name all seven with examples?',
        '''<ul>
          <li>Regular (<code>-</code>), directory (<code>d</code>), symbolic link (<code>l</code>), character device (<code>c</code>, /dev/tty), block device (<code>b</code>, /dev/sda), named pipe (<code>p</code>, mkfifo), socket (<code>s</code>, /run/docker.sock).</li>
          <li>Shown as the first character of <code>ls -l</code>; stored in the inode’s mode.</li>
          <li>Add: extensions do not define the type; <code>file</code> checks content.</li>
        </ul>''', 'listing “text, image, video” as Linux file types.') +
    scn('Operations · audit', 'Junior', '“When was this file created?”',
        'A manager asks when <code>/etc/app.conf</code> was created and when it was last edited.',
        'do you know which timestamp means what?',
        '''<ol>
          <li><code>stat /etc/app.conf</code>: <b>Modify</b> = last content edit; <b>Birth</b> = creation, if the file system records it.</li>
          <li>Explain that <b>Change</b> (ctime) is not creation: it also moves on chmod, chown or rename.</li>
          <li>If Birth shows “-”, check package logs (<code>/var/log/dpkg.log</code>) or backups for the history.</li>
        </ol>''', 'quoting ctime as the creation time.') +
    scn('Security · uploads', 'Mid-level', 'A “.jpg” that runs code',
        'A web app accepted <code>avatar.jpg</code> which turned out to be a PHP script. How do you prevent this?',
        'do you validate by content?',
        '''<ul>
          <li>Check the real type (<code>file --mime-type</code> or the libmagic library in code), allow-list image types, and re-encode images.</li>
          <li>Store uploads outside the web root and never execute them; rename to random names.</li>
          <li>The extension and the browser’s Content-Type header can both be faked.</li>
        </ul>''', 'checking only the extension.') +
    scn('Platform team · internals', 'Senior', '“What is a device file really?”',
        'Explain what happens when a program writes to <code>/dev/null</code>.',
        'do you understand major and minor numbers and the VFS?',
        '''<ul>
          <li>A device file is an inode with type <code>c</code> or <code>b</code> and a major, minor pair; it has no data blocks.</li>
          <li>On open, the VFS uses the major number to find the driver (1 = memory devices) and the minor to pick the device (3 = null); its write function simply returns success.</li>
          <li>udev creates these nodes in <code>/dev</code> (a devtmpfs) when the kernel detects devices.</li>
        </ul>''', 'thinking /dev/null is a big empty file on disk.')
) + teaser('2.5', 'Riya wants to know every option of <code>ls</code>, but there is no internet on the server. Where is the complete manual already waiting for her?')

MINDMAP = mindmap('File types', [
    ('7 types', 'acc', ['- file, d dir, l link', 'c, b devices', 'p pipe, s socket']),
    ('Name ≠ type', 'blue', ['extension = just name', 'type in the inode', 'mv changes only name']),
    ('file', 'green', ['reads magic bytes', 'file -i = MIME', 'FF D8 FF = JPEG']),
    ('stat', 'violet', ['size, blocks, inode', 'perms, owner', 'stat -c custom']),
    ('Three times', 'amber', ['atime = read', 'mtime = content', 'ctime = inode (not birth)']),
    ('Hidden', 'red', ['name starts with .', 'ls -a / ls -A', 'hidden ≠ secret']),
])
