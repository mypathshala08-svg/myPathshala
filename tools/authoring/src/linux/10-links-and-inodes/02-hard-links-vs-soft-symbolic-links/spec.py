import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='10-links-and-inodes', lesson='02-hard-links-vs-soft-symbolic-links', n='10.2',
    module_label='Module 10 · Inodes and links',
    title='Hard links vs soft (symbolic) links',
    desc='Hard links (same inode, link count, survive deleting the other name, no folders, no cross-disk) vs symbolic links (a file holding a path, dangling links, relative targets resolved from the link’s folder); ln, ln -s, -f, -n, -r, -T; readlink -f, realpath; ln -sf into a folder link; atomic release switch with mv -T; find -type l, -xtype l, -samefile; how cp, find, chmod, tar treat links; sed -i breaking hard links; real outputs and animations.',
    og_desc='Hard links vs symbolic links in Linux: what each really is, what breaks when the original is deleted, and how to use ln -s safely.',
    minutes=40, level='Beginner → Advanced',
    lead='A hard link is a second name for the same inode; a symbolic link is a small file that holds a path. This lesson shows the difference on real files, the mistakes that break links, and how deploys, package tools and backups use them.',
    chips=['Hard vs soft, side by side', 'ln -sfn and atomic deploys', 'Broken links found', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A hard link and a soft link
echo 'Q3 sales: 42 lakh' > report.txt
ln report.txt backup.txt
ln -s report.txt latest
ls -li
rm report.txt
cat backup.txt
cat latest || echo "(latest is broken)"
"""

RUN = dict(
    heading='Delete the original and see what survives',
    intro='<p>Make one hard link and one symbolic link, delete the original, and read both.</p>',
    code=MAIN, expect='any',
    anno=[('ln -s report.txt latest', 'latest only stores the text “report.txt”.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which cat fails, and why?', code=MAIN, expect='any'),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what is the link count after the second ln? Then run.',
             code="echo x > f\nln f g\nln f h\nstat -c %h f\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the link inside d/ should show f’s text. Fix the target path.',
             code="echo hello > f\nmkdir -p d\nln -s f d/link\ncat d/link || echo \"(broken link)\"\n", expect='any'),
        dict(label='4 · Your turn', hint='Point current at v2 instead of v1 without creating v1/v2.',
             code="mkdir -p v1 v2; echo one > v1/a; echo two > v2/a\nln -s v1 current\nln -sfn v2 current\ncat current/a\n"),
        dict(label='5 · Challenge', hint='List only the broken links.',
             code="echo ok > real\nln -s real good; ln -s missing bad\nfind . -xtype l\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: links you already have',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · The merged /usr links', cmd='ls -ld /bin /sbin /lib', output=pc("ls -ld /bin /sbin /lib | awk '{print $1, $(NF-2), $(NF-1), $NF}'"), note='Recorded (columns trimmed).'),
        dict(title='2 · Your editor via alternatives', cmd='readlink -f /usr/bin/editor', output='/usr/bin/nano', note='Typical: the chain goes through /etc/alternatives/editor.'),
        dict(title='3 · Broken links in /etc', cmd='sudo find /etc -xtype l 2>/dev/null | head', output='', note='Typical: usually nothing.'),
        dict(title='4 · ln version', cmd='ln --version | head -1', output=pc('ln --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Link count step by step',
    intro='<p>Watch the link count go up with each hard link and down with each rm.</p>',
    code='''echo data > a
ln a b; n1=$(stat -c %h a)
ln a c; n2=$(stat -c %h a)
rm a; n3=$(stat -c %h b)
ln -s b s; n4=$(stat -c %h b)
echo "$n1 $n2 $n3 $n4"
''',
    notes={1: 'One name.', 2: 'Hard link :: 2.', 3: 'Another :: 3.', 4: 'rm :: 2.', 6: 'Summary :: a symlink does not change the count.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s shortcut, an admin’s release switch and a security clean-up.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='A shortcut to a deep folder',
         problem='<p>Make a short name for a deep project folder and use it.</p>',
         inp='a deep folder', approach=['ln -s.', 'cd through the link.'],
         code='''mkdir -p work/clients/acme/2026/reports
echo 'draft' > work/clients/acme/2026/reports/q3.txt
ln -s work/clients/acme/2026/reports acme
cat acme/q3.txt
''', notes={3: 'Short name.', 4: 'Works like the folder.'}, tryit='Run readlink -f acme.'),
    dict(level='i', tag='DevOps', title='Switch and roll back a release',
         problem='<p>Point current at v1, switch to v2 atomically, then roll back.</p>',
         inp='two release folders', approach=['ln -s + mv -T.', 'ln -sfn to roll back.'],
         code='''mkdir -p r/v1 r/v2; echo one > r/v1/app; echo two > r/v2/app
ln -sfn r/v1 current; cat current/app
ln -s r/v2 tmp && mv -T tmp current; cat current/app
ln -sfn r/v1 current; cat current/app
''', notes={2: 'v1.', 3: 'Atomic switch.', 4: 'Rollback.'}, tryit='Try ln -sf r/v2 current and look inside r/v1.'),
    dict(level='a', tag='Security', title='Remove broken links, keep good ones',
         problem='<p>A folder has good and broken links. Report the broken ones and delete them.</p>',
         inp='mixed links', approach=['find -xtype l.', '-print -delete.'],
         code='''mkdir -p L; echo ok > L/real
ln -s real L/good; ln -s gone1 L/bad1; ln -s gone2 L/bad2
find L -xtype l -print -delete | sort
ls L
''', notes={2: 'Setup.', 3: 'Only broken links.', 4: 'good and real stay.'}, tryit='Add -lname to delete only links pointing to gone*.'),
]

QUIZ = mix([
    dict(q='After rm original, which still shows the data?', options=['the symbolic link', 'the hard link', 'both', 'neither'], answer=1, why='Same inode.'),
    dict(q='Which can point to a folder?', options=['hard link', 'symbolic link', 'both', 'neither'], answer=1, why='Hard links to folders are forbidden.'),
    dict(q='ln report.txt /mnt/usb/r.txt fails with…', options=['Permission denied', 'Invalid cross-device link', 'File exists', 'Too many links'], answer=1, why='Hard links stay on one filesystem.'),
    dict(q='Correct order in ln -s?', options=['LINK TARGET', 'TARGET LINK', 'either', 'TARGET only'], answer=1, why='Like cp.'),
    dict(q='Replace a link that points to a folder?', options=['ln -sf', 'ln -sfn', 'ln -s', 'mv'], answer=1, why='-n treats the link as a file.'),
    dict(q='Find broken symlinks?', options=['find -type l', 'find -xtype l', 'find -links 0', 'ls -L'], answer=1, why='-xtype checks the target.'),
    dict(q='Size of a symlink to “report.txt”?', options=['0', '10', 'the size of report.txt', '4096'], answer=1, why='Length of the path.'),
    dict(q='Final target of a chain of links?', options=['readlink L', 'readlink -f L', 'ls L', 'stat L'], answer=1, why='-f follows all.'),
])

REVISION = [
    'Hard link: <code>ln F N</code>, same inode, link count +1, survives deleting the other name. Not for folders, not across disks.',
    'Soft link: <code>ln -s TARGET LINK</code>, own inode holding a path; breaks if the path disappears; works for folders and other disks.',
    'A relative target is resolved from the link’s folder: use <code>-r</code> or an absolute path.',
    'Replace a folder link with <code>ln -sfn</code>; switch live with <code>ln -s new tmp &amp;&amp; mv -T tmp current</code>.',
    '<code>readlink -f</code> / <code>realpath</code> show the final path; <code>find -xtype l</code> finds broken links; <code>-samefile</code> finds hard links.',
    '<code>rm link</code> removes the link only; never <code>rm -r link/</code>.',
]

FAQ = [
    ('What is the difference between a hard link and a soft link?', 'A hard link is another name for the same inode and keeps working if the other name is deleted. A soft link is a separate file holding a path and breaks if that path disappears.'),
    ('How do I create a symbolic link?', 'ln -s TARGET LINK_NAME.'),
    ('How do I update an existing symlink?', 'ln -sfn NEW_TARGET LINK_NAME.'),
    ('Why can’t I hard link a directory?', 'It could create loops in the tree and confuse tools; only the kernel makes . and .. links.'),
    ('How do I find broken symlinks?', 'find DIR -xtype l.'),
    ('Does deleting a symlink delete the file?', 'No, rm on a link removes only the link.'),
    ('Why is my symlink broken right after creating it?', 'A relative target is resolved from the link’s folder. Use ln -sr or an absolute path.'),
]

PRACTICE_INTRO = 'Small link tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Symlink', stmt='Make link → data.txt and print its target text.', inp='a file', code="echo hi > data.txt; ln -s data.txt link; readlink link\n", explain='readlink.'),
    dict(level='easy', title='Hard link count', stmt='Make one hard link and print the link count.', inp='a file', code="echo hi > h1; ln h1 h2; stat -c %h h1\n", explain='2.'),
    dict(level='easy', title='Same inode?', stmt='Print “same” if h1 and h2 share an inode.', inp='a hard link', code="echo hi > h1; ln h1 h2; [ $(stat -c %i h1) = $(stat -c %i h2) ] && echo same\n", explain='stat %i.'),
    dict(level='medium', title='Survives', stmt='Delete the first name and read the hard link.', inp='a hard link', code="echo kept > k1; ln k1 k2; rm k1; cat k2\n", explain='Data stays.'),
    dict(level='medium', title='Dangling', stmt='Make a link to a missing file and test it with [ -e ].', inp='nothing', code="ln -s nowhere dl; [ -L dl ] && echo link; [ -e dl ] || echo broken\n", explain='-L vs -e.'),
    dict(level='medium', title='Relative', stmt='From the current folder, make sub/l pointing to top.txt here.', inp='a file', code="echo top > top.txt; mkdir -p sub; ln -sr top.txt sub/l; readlink sub/l; cat sub/l\n", explain='-r.'),
    dict(level='business', title='Version switch', stmt='Point cur at b2 instead of b1 and print the content.', inp='two folders', code="mkdir -p b1 b2; echo 1 > b1/x; echo 2 > b2/x; ln -s b1 cur; ln -sfn b2 cur; cat cur/x\n", explain='-sfn.'),
    dict(level='business', title='Count broken', stmt='Count the broken links among three.', inp='links', code="echo r > r; ln -s r g; ln -s m1 b1l; ln -s m2 b2l; find . -maxdepth 1 -xtype l | wc -l\n", explain='-xtype l.'),
]

SCN_INTRO = 'Interview questions about links, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Hard link vs soft link?”', 'Asked in almost every Linux interview.', 'inode-level answer?',
        '''<ul>
          <li>Hard: same inode, survives deleting the original, no folders, same filesystem.</li>
          <li>Soft: own inode holding a path, can dangle, folders and other disks OK.</li>
          <li>Show with <code>ls -li</code>.</li>
        </ul>''', 'saying “a soft link is a copy”.') +
    scn('Web hosting', 'Junior', 'After a deploy the site shows the OLD version', 'The script ran ln -sf releases/v2 current.', 'do you know -n?',
        '''<ol>
          <li><code>ls releases/v1</code>: a stray <code>v2</code> link inside it.</li>
          <li><code>rm releases/v1/v2; ln -sfn releases/v2 current</code>.</li>
          <li>Better: <code>ln -s … tmp &amp;&amp; mv -T tmp current</code>.</li>
        </ol>''', 'rm -r current/ (deletes the release).') +
    scn('Operations', 'Mid-level', 'A config change does not take effect', 'The service reads /etc/app.conf, a hard link to /opt/app/app.conf, edited with vim.', 'sed -i / editors and hard links?',
        '''<ul>
          <li><code>ls -li</code>: the two names now have different inodes.</li>
          <li>The editor saved a new file; the hard link kept the old one.</li>
          <li>Use a symlink for config, or configure the editor to write in place.</li>
        </ul>''', 'restarting the service again and again.') +
    scn('Backup team', 'Senior', '30 daily snapshots of 2 TB in 2.3 TB', 'How?', 'hard-link snapshots?',
        '''<ul>
          <li><code>rsync -a --link-dest=../yesterday src/ today/</code>: unchanged files are hard links.</li>
          <li>Each snapshot looks complete; deleting old ones is safe.</li>
          <li>Limit: a changed file is stored again whole; modern options use filesystem snapshots (Btrfs, ZFS, LVM).</li>
        </ul>''', 'thinking it is compression.')
) + interview([
    ('Can a hard link cross filesystems?', 'No; inode numbers are per filesystem.'),
    ('What does the l in lrwxrwxrwx mean?', 'Symbolic link.'),
    ('What happens to a symlink when the target is renamed?', 'It breaks (dangling).'),
    ('How do you see where a symlink points?', 'ls -l or readlink (-f for the final path).'),
    ('How is space freed with hard links?', 'When the last name is removed and no process has the file open.'),
    ('How do you find all hard links of a file?', 'find / -xdev -samefile FILE (or -inum).'),
    ('Why ln -sfn and not ln -sf?', 'Without -n, an existing link to a folder is followed and the new link is created inside the folder.'),
], [
    ('RHCSA (EX200)', '“Create hard and soft links”.'),
    ('LFCS', 'Create and manage hard and soft links.'),
    ('CompTIA Linux+', 'ln, ln -s, inodes and link counts.'),
]) + distro('Links work the same everywhere; a few option differences.', [
    ('ln / ln -s', 'yes', 'yes', 'yes', 'Git Bash: copies unless enabled'),
    ('ln -r, -T', 'GNU', 'GNU', 'no (use -h / -F)', 'GNU'),
    ('readlink -f / realpath', 'yes', 'yes', 'macOS 13+', 'yes'),
    ('find -xtype', 'GNU', 'GNU', 'no (find -L -type l)', 'GNU'),
    ('Windows equivalent', '-', '-', '-', 'mklink, mklink /H, /J'),
]) + teaser('11.1', 'Files are done: names, inodes, permissions and links. But who is reading and writing them? Every command you run becomes a process with its own number. Next module: what a process is, PID and PPID, and how fork and exec start every program.')

CHEATSHEET = cheatsheet('Links', [
    ('Make', [('ln -s T L', 'symlink'), ('ln -sr T L', 'relative'), ('ln F N', 'hard link'), ('cp -al D S', 'hard-link tree')]),
    ('Change', [('ln -sfn T L', 'replace link'), ('mv -T tmp L', 'atomic'), ('rm L', 'link only'), ('chown -h', 'the link itself')]),
    ('Read', [('ls -li', 'inode, count'), ('readlink L', 'stored text'), ('readlink -f L', 'final path'), ('ls -lL', 'target details')]),
    ('Find', [('find -type l', 'symlinks'), ('find -xtype l', 'broken'), ('-samefile F', 'hard links'), ('-links +1', 'many names')]),
])

MINDMAP = mindmap('Links', [
    ('Hard', 'green', ['same inode', 'count +1', 'survives rm']),
    ('Soft', 'blue', ['holds a path', 'own inode', 'can dangle']),
    ('Limits', 'red', ['hard: no dirs', 'hard: one disk', 'soft: relative!']),
    ('ln', 'amber', ['-s -r', '-sfn', 'mv -T']),
    ('Read', 'violet', ['ls -l', 'readlink -f', 'realpath']),
    ('Uses', 'acc', ['deploys', 'alternatives', 'snapshots']),
])

LAB = lab('a versioned deploy', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab102 && cd ~/lab102 && rm -rf site shared
mkdir -p site/releases/v1 site/releases/v2 shared; echo 'version 1' > site/releases/v1/index.html; echo 'version 2' > site/releases/v2/index.html
echo 'DB=prod' > shared/app.env; ln -s releases/v1 site/current; ln -s gone.html site/old-link''',
    tasks=['Switch <code>site/current</code> to <code>releases/v2</code> without creating anything inside <code>releases/v1</code>.',
           'Make <code>site/releases/v2/app.env</code> a <b>symbolic</b> link to <code>shared/app.env</code> that works (use -r or an absolute path).',
           'Make <code>shared/app.env.bak</code> a <b>hard</b> link to <code>shared/app.env</code>.',
           'Delete every broken symbolic link under <code>site</code>.'],
    solution='''ln -sfn releases/v2 site/current
ln -sr shared/app.env site/releases/v2/app.env
ln shared/app.env shared/app.env.bak
find site -xtype l -delete''',
    check='''cd ~/lab102
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 switch"  '[ "$(readlink site/current)" = releases/v2 ] && [ ! -e site/releases/v1/v2 ]'
ok "2 symlink" '[ -L site/releases/v2/app.env ] && [ "$(cat site/releases/v2/app.env 2>/dev/null)" = DB=prod ]'
ok "3 hard"    '[ -f shared/app.env.bak ] && [ ! -L shared/app.env.bak ] && [ "$(stat -c %i shared/app.env)" = "$(stat -c %i shared/app.env.bak)" ]'
ok "4 broken"  '[ -z "$(find site -xtype l)" ] && [ -L site/current ]' ''')
