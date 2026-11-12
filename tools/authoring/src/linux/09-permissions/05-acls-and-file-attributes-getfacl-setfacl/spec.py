import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='09-permissions', lesson='05-acls-and-file-attributes-getfacl-setfacl', n='9.5',
    module_label='Module 9 · Permissions and ownership',
    title='ACLs and file attributes: getfacl, setfacl and chattr',
    desc='Why owner/group/others is not always enough; POSIX ACLs with getfacl and setfacl (-m -x -b -R -d -k, named users and groups, X), the mask and #effective rights, default ACLs for new files, keeping ACLs with cp -a, tar --acls and rsync -A; file attributes with chattr +i (immutable) and +a (append-only) and lsattr, with recorded chattr outputs and animations.',
    og_desc='Give one extra user access with setfacl, understand the ACL mask and default ACLs, and lock files with chattr +i and +a.',
    minutes=38, level='Beginner → Advanced',
    lead='ACLs add named exceptions to the three permission classes; file attributes lock files even against root. This lesson explains getfacl, setfacl, the mask, default ACLs and chattr, and how admins, web, DevOps and security teams use them.',
    chips=['The ACL mask animated', 'Default ACLs', 'chattr +i and +a', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Attributes and extended attributes
touch a.txt
lsattr a.txt
ls -l a.txt
python3 -c "import os; os.setxattr('a.txt','user.owner_note',b'audit 2026'); print(os.getxattr('a.txt','user.owner_note').decode())"
lsattr -d /tmp
"""

RUN = dict(
    heading='Look at attributes',
    intro='<p>chattr and setfacl need root and the acl package, so the browser shows lsattr and extended attributes; the real commands are in the cards and the lab.</p>',
    code=MAIN,
    anno=[('lsattr a.txt', 'e = extents (normal on ext4); no i or a.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which flags does a normal file have?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> does /etc/passwd have the i flag? Then run.', code="lsattr /etc/passwd\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should list the folder’s own flags, not its contents.', code="mkdir -p box; touch box/x\nlsattr box\n"),
        dict(label='4 · Your turn', hint='Store a note in an extended attribute and list all names.', code="touch n; python3 -c \"import os; os.setxattr('n','user.tag',b'x'); print(os.listxattr('n'))\"\n"),
        dict(label='5 · Challenge', hint='Find files with a + (ACL) in /etc.', code="ls -l /etc | awk '$1 ~ /\\+$/' | wc -l\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real ACLs',
    intro='<p>Install the tools first: <code>sudo apt install acl</code>. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · A file with an ACL', cmd='touch acl.txt; setfacl -m u:root:r acl.txt; ls -l acl.txt; getfacl acl.txt', output='-rw-rw-r--+ 1 vineeta vineeta 0 Nov 11 10:20 acl.txt\n# file: acl.txt\n# owner: vineeta\n# group: vineeta\nuser::rw-\nuser:root:r--\ngroup::rw-\nmask::rw-\nother::r--', note='Typical.'),
        dict(title='2 · The mask after chmod', cmd='setfacl -m u:root:rw acl.txt; chmod 640 acl.txt; getfacl --omit-header acl.txt', output='user::rw-\nuser:root:rw-\t\t#effective:r--\ngroup::rw-\t\t\t#effective:r--\nmask::r--\nother::---', note='Typical: the puzzle.'),
        dict(title='3 · Remove it', cmd='setfacl -b acl.txt; ls -l acl.txt', output='-rw-r----- 1 vineeta vineeta 0 Nov 11 10:20 acl.txt', note='Typical.'),
        dict(title='4 · Immutable', cmd="touch lock.txt; sudo chattr +i lock.txt; lsattr lock.txt; sudo rm lock.txt", output=pc("touch lock.txt; sudo chattr +i lock.txt; lsattr lock.txt; sudo rm lock.txt 2>&1; sudo chattr -i lock.txt; rm lock.txt"), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Finding locked files in a script',
    intro='<p>Step through a script that reads lsattr flags.</p>',
    code='''touch a b
f=$(lsattr a | cut -d' ' -f1)
case $f in *i*) s=immutable;; *a*) s=append-only;; *) s=normal;; esac
echo "a: $s"
''',
    notes={1: 'Two files.', 2: 'Flags :: the first column.', 3: 'Decide.', 4: 'Result :: normal.'},
)

WORKED_INTRO = 'Three tasks from real jobs, recorded with sudo: a locked config, an append-only log and a stuck file.'
EXAMPLES = [
    dict(level='b', tag='Sysadmin', title='Protect a config file',
         problem='<p>Make a config immutable, prove that even sudo cannot change it, then unlock.</p>',
         inp='a config file', approach=['chattr +i.', 'Try to write.', 'chattr -i.'],
         code='''echo 'port=8080' > app.conf; sudo chattr +i app.conf
echo 'port=1' | sudo tee app.conf > /dev/null 2>&1 || echo 'write refused'
cat app.conf; sudo chattr -i app.conf
''', notes={1: 'Locked.', 2: 'Refused :: even with sudo.', 3: 'Unchanged.'}, tryit='Try sudo mv app.conf x.conf while locked.'),
    dict(level='i', tag='Security', title='Append-only log',
         problem='<p>A log may grow but never be wiped.</p>',
         inp='a log', approach=['chattr +a.', 'Test >> and >.'],
         code='''echo start > app.log; sudo chattr +a app.log
echo event1 >> app.log
sudo sh -c 'echo wipe > app.log' 2>/dev/null || echo 'overwrite refused'
cat app.log; sudo chattr -a app.log
''', notes={2: 'Append ok.', 3: 'Refused.', 4: 'Both lines kept.'}, tryit='Try truncate -s 0.'),
    dict(level='a', tag='Incident', title='The file root cannot delete',
         problem='<p>A file resists sudo rm. Find out why and remove it.</p>',
         inp='a mystery file', approach=['rm fails.', 'lsattr.', 'chattr -i, rm.'],
         code='''touch evil.bin; sudo chattr +i evil.bin
sudo rm -f evil.bin 2>&1 | cut -c1-60
lsattr evil.bin
sudo chattr -i evil.bin && rm evil.bin && echo removed
''', notes={2: 'Refused.', 3: 'i flag.', 4: 'Gone.'}, tryit='Check lsattr -R on a folder.'),
]

QUIZ = mix([
    dict(q='What does a + after the mode in ls -l mean?', options=['SUID', 'the file has an ACL', 'hidden file', 'immutable'], answer=1, why='Run getfacl.'),
    dict(q='Which gives user priya read access with an ACL?', options=['chmod u+priya', 'setfacl -m u:priya:r f', 'chown priya f', 'chattr +r f'], answer=1, why='-m modifies.'),
    dict(q='What does the ACL mask do?', options=['hides the file', 'limits named entries and the owning group', 'sets the owner', 'nothing'], answer=1, why='Upper limit.'),
    dict(q='How do new files in a folder get an ACL automatically?', options=['setfacl -R', 'a default ACL (setfacl -d)', 'umask', 'SUID'], answer=1, why='Inherited.'),
    dict(q='Which removes all ACL entries?', options=['setfacl -x', 'setfacl -b', 'setfacl -k', 'chmod 000'], answer=1, why='-k removes only the default ACL.'),
    dict(q='What does chattr +i do?', options=['makes a file invisible', 'makes it immutable, even for root', 'sets SUID', 'compresses'], answer=1, why='Until chattr -i.'),
    dict(q='Which attribute lets a log only grow?', options=['+i', '+a', '+s', '+e'], answer=1, why='Append-only.'),
    dict(q='Which copy keeps ACLs?', options=['cp', 'cp -a', 'mv between file systems without -a', 'cat > copy'], answer=1, why='Also tar --acls, rsync -A.'),
])

REVISION = [
    'ACL = named user/group entries + mask on top of u/g/o; ls -l shows <code>+</code>.',
    '<code>getfacl f</code>; <code>setfacl -m u:N:rX f</code>, <code>-m g:N:r</code>, <code>-x u:N</code>, <code>-b</code>, <code>-R</code>.',
    'Mask limits named entries and the owning group; chmod’s group digit sets it (watch #effective).',
    'Default ACLs: <code>setfacl -d -m …</code> on folders; <code>-k</code> removes them.',
    'Keep ACLs: cp -a, tar --acls, rsync -A; backup with getfacl -R / restore with setfacl --restore.',
    '<code>chattr +i</code> immutable, <code>+a</code> append-only (root needed, applies to root); <code>lsattr</code> to check.',
]

FAQ = [
    ('What is an ACL in Linux?', 'An access control list: extra permission entries for specific users and groups beyond owner, group and others.'),
    ('How do I give one user access to a file?', 'setfacl -m u:USER:rw FILE (install the acl package if setfacl is missing).'),
    ('How do I see ACLs?', 'getfacl FILE; ls -l shows a + when a file has an ACL.'),
    ('What is the ACL mask?', 'The maximum permissions for named users, named groups and the owning group.'),
    ('How do I make new files inherit an ACL?', 'Set a default ACL on the folder: setfacl -d -m u:USER:rX DIR.'),
    ('How do I make a file undeletable even by root?', 'sudo chattr +i FILE (remove with chattr -i).'),
    ('Why can’t root delete a file?', 'Check lsattr for the i or a attribute, a read-only mount, or SELinux/AppArmor.'),
]

PRACTICE_INTRO = 'Small attribute tasks (with sudo). Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Flags of a file', stmt='Show the attributes of a new file.', inp='a file', code="touch x; lsattr x\n", explain='e only.'),
    dict(level='easy', title='Lock', stmt='Make a file immutable and show the flags.', inp='a file', code="touch y; sudo chattr +i y; lsattr y; sudo chattr -i y\n", explain='i.'),
    dict(level='easy', title='Folder flags', stmt='Show the flags of a folder itself.', inp='a folder', code="mkdir z; lsattr -d z\n", explain='-d.'),
    dict(level='medium', title='Append works', stmt='Append to an append-only file and count lines.', inp='a file', code="echo 1 > l; sudo chattr +a l; echo 2 >> l; wc -l < l; sudo chattr -a l\n", explain='>> allowed.'),
    dict(level='medium', title='Overwrite fails', stmt='Try to overwrite an append-only file.', inp='a file', code="echo 1 > m; sudo chattr +a m\n(echo 2 > m) 2>/dev/null || echo refused\nsudo chattr -a m\n", explain='> refused.'),
    dict(level='medium', title='Rename fails', stmt='Try to rename an immutable file.', inp='a file', code="touch n; sudo chattr +i n\nsudo mv n n2 2>/dev/null || echo 'rename refused'\nsudo chattr -i n\n", explain='Even root.'),
    dict(level='business', title='Find locked files', stmt='List files with the i flag in a folder.', inp='a folder', code="mkdir -p f; touch f/a f/b; sudo chattr +i f/b\nlsattr f | awk '$1 ~ /i/ {print $2}'\nsudo chattr -i f/b\n", explain='awk on column 1.'),
    dict(level='business', title='User xattr', stmt='Store and read a user extended attribute.', inp='a file', code="touch g; python3 -c \"import os; os.setxattr('g','user.ticket',b'INC-42'); print(os.getxattr('g','user.ticket').decode())\"\n", explain='Same storage as ACLs.'),
]

SCN_INTRO = 'Interview questions about ACLs and attributes, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you give one user access without changing the group?”', 'A common question.', 'do you know ACLs?',
        '''<ul>
          <li><code>setfacl -m u:NAME:r FILE</code>, check with getfacl.</li>
          <li>The + in ls -l.</li>
        </ul>''', 'chmod o+r (gives everyone access).') +
    scn('Help desk', 'Junior', '“My ACL stopped working”', 'An admin ran chmod after setfacl.', 'do you know the mask?',
        '''<ol>
          <li><code>getfacl</code>: #effective shows the mask cut rights.</li>
          <li><code>setfacl -m m::rw FILE</code> or chmod with the right group digit.</li>
        </ol>''', 'deleting and re-adding the ACL every day.') +
    scn('Operations', 'Mid-level', 'Access lost after a migration', 'Files were copied with cp -r to a new server; auditors lost access.', 'do you know what drops ACLs?',
        '''<ul>
          <li>cp without -a, tar without --acls, rsync without -A drop ACLs.</li>
          <li>Restore from <code>getfacl -R</code> backup or re-apply; copy again with rsync -aAX.</li>
        </ul>''', 'giving everyone access to stop complaints.') +
    scn('Security team', 'Senior', 'Malware keeps coming back', 'A file in /usr/local/bin cannot be removed and reappears.', 'incident handling?',
        '''<ul>
          <li><code>lsattr</code>: immutable flag; cron/systemd timers that restore it.</li>
          <li>chattr -i, remove, find persistence, check other +i files: <code>lsattr -R / 2>/dev/null | awk '$1~/i/'</code>.</li>
          <li>Rebuild if root was compromised.</li>
        </ul>''', '“root can always delete, it must be a disk error”.')
) + interview([
    ('What package provides setfacl?', 'acl.'),
    ('What does setfacl -x do?', 'Removes one ACL entry.'),
    ('What does setfacl -k do?', 'Removes the default ACL.'),
    ('What is #effective in getfacl?', 'Rights after applying the mask.'),
    ('Can a normal user use chattr +i?', 'No, it needs root (CAP_LINUX_IMMUTABLE).'),
    ('Where are ACLs stored?', 'In extended attributes (system.posix_acl_access/default).'),
    ('How do you back up ACLs?', 'getfacl -R DIR > file; restore with setfacl --restore=file.'),
], [
    ('RHCSA (EX200)', 'ACLs appear in collaboration and permission tasks.'),
    ('LFCS', 'Manage ACLs and file attributes.'),
    ('CompTIA Linux+', 'getfacl/setfacl, chattr/lsattr.'),
]) + distro('POSIX ACLs on Linux; other systems differ.', [
    ('getfacl / setfacl', 'acl package', 'installed', 'no: chmod +a (NFSv4-style ACLs)', '-'),
    ('chattr / lsattr', 'e2fsprogs', 'e2fsprogs', 'chflags (uchg, sappnd)', '-'),
    ('ACL on by default', 'ext4, xfs, btrfs', 'xfs, ext4', 'APFS', 'NTFS'),
    ('Copy with ACLs', 'cp -a, rsync -A', 'same', 'cp -p', 'robocopy /COPYALL'),
    ('Windows', '-', '-', '-', 'icacls, attrib +r'),
]) + teaser('10.1', 'Behind every file name in this module was an inode holding the owner, the mode, the ACL and the flags. What exactly is an inode, why can a disk be “full” with free space, and how can one file have two names? Next: inodes.')

CHEATSHEET = cheatsheet('ACLs and attributes', [
    ('getfacl', [('getfacl f', 'show'), ('-R', 'tree'), ('--omit-header', 'no #'), ('+ in ls -l', 'has ACL'), ('#effective', 'after mask')]),
    ('setfacl', [('-m u:N:rX', 'add user'), ('-m g:N:r', 'add group'), ('-x u:N', 'remove one'), ('-b', 'remove all'), ('-m m::r', 'mask')]),
    ('Defaults', [('-d -m u:N:rX d', 'inherit'), ('-k d', 'remove default'), ('-R', 'existing files'), ('cp -a / rsync -A', 'keep ACLs'), ('tar --acls', 'backups')]),
    ('Attributes', [('chattr +i', 'immutable'), ('chattr +a', 'append-only'), ('chattr -i / -a', 'remove'), ('lsattr f / -d', 'show'), ('root needed', 'applies to root')]),
])

MINDMAP = mindmap('ACLs and attributes', [
    ('Why', 'blue', ['3 classes not enough', 'named exceptions', 'locks']),
    ('getfacl', 'green', ['entries', 'mask', '#effective']),
    ('setfacl', 'amber', ['-m -x -b', '-R, X', '-d -k defaults']),
    ('Keep them', 'violet', ['cp -a', 'tar --acls', 'rsync -A']),
    ('chattr', 'red', ['+i immutable', '+a append', 'root only']),
    ('Diagnose', 'acc', ['ls -l +', 'lsattr', 'root denied?']),
])

LAB = lab('attributes and ACL commands', 'Build the lab, do the four tasks in your own terminal (sudo needed), then run the checker. Tasks 1–2 use chattr; tasks 3–4 write the ACL commands you would run (install the acl package to try them).',
    setup='''sudo chattr -i -a ~/lab95/* > /dev/null 2>&1; rm -rf ~/lab95; mkdir -p ~/lab95; cd ~/lab95
echo 'nameserver 10.0.0.2' > dns.conf; echo start > audit.log''',
    tasks=['Make <code>dns.conf</code> immutable.',
           'Make <code>audit.log</code> append-only, then append the line <code>login riya</code> to it.',
           'Write into <code>acl1.txt</code> the setfacl command that gives user <code>priya</code> read access to <code>/srv/finance/q3.xlsx</code>.',
           'Write into <code>acl2.txt</code> the setfacl command that makes new files in <code>/srv/finance</code> readable by priya (default ACL, X for folders).'],
    solution='''sudo chattr +i dns.conf
sudo chattr +a audit.log; echo 'login riya' >> audit.log
echo 'setfacl -m u:priya:r /srv/finance/q3.xlsx' > acl1.txt
echo 'setfacl -d -m u:priya:rX /srv/finance' > acl2.txt''',
    check='''cd ~/lab95
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 immutable" 'lsattr dns.conf | cut -d" " -f1 | grep -q i'
ok "2 append"    'lsattr audit.log | cut -d" " -f1 | grep -q a && tail -1 audit.log | grep -qx "login riya"'
ok "3 acl1"      'grep -Eq "setfacl +-m +u:priya:r +/srv/finance/q3.xlsx" acl1.txt 2>/dev/null'
ok "4 acl2"      'grep -Eq "setfacl +(-d +-m|-dm|-m +-d) +(d:)?u:priya:rX +/srv/finance" acl2.txt 2>/dev/null'
sudo chattr -i dns.conf; sudo chattr -a audit.log''')
