import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='09-permissions', lesson='01-reading-permissions-rwx-for-user-group', n='9.1',
    module_label='Module 9 · Permissions and ownership',
    title='Reading permissions: rwx for user, group and others',
    desc='Read every character of ls -l: file type, owner, group and three sets of rwx; what r, w and x mean on files and on directories; the one-class rule; x on every folder of a path; octal 644/600/755/750; ls -l, ls -ld, stat -c, namei -l and test -r -w -x; how the kernel decides (EACCES), animated with real outputs.',
    og_desc='Read Linux permissions like a sentence: rwx for owner, group and others, on files and on directories, with real outputs.',
    minutes=36, level='Beginner → Advanced',
    lead='Ten characters in ls -l decide who may read, change or run each file. This lesson teaches you to read them exactly, explains why folders behave differently, and shows how admins, web, DevOps, security and testers diagnose “Permission denied”.',
    chips=['Files vs folders', 'How the kernel decides (animated)', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Read permissions in a small folder
mkdir -p demo/private; echo hi > demo/notes.txt; echo key > demo/secret.key
printf '#!/bin/sh\\necho run\\n' > demo/run.sh
chmod 644 demo/notes.txt; chmod 600 demo/secret.key; chmod 755 demo/run.sh; chmod 700 demo/private
ls -l demo
stat -c '%A %a %n' demo/*
ls -ld demo
"""

RUN = dict(
    heading='Read a folder’s permissions',
    intro='<p>Create four items with typical modes, then read them as letters and as numbers.</p>',
    code=MAIN,
    anno=[("stat -c '%A %a %n' demo/*", 'Letters and octal side by side.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which file can only you read?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what octal number is -rwxr-x---? Then run.',
             code="touch f; chmod u=rwx,g=rx,o= f\nstat -c '%A %a' f\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should show the folder itself, not its contents.',
             code="mkdir -p box; touch box/a\nls -l box\n"),
        dict(label='4 · Your turn', hint='Show the mode of /etc/shadow and /tmp as letters and octal.',
             code="stat -c '%A %a %n' /etc/shadow /tmp\n"),
        dict(label='5 · Challenge', hint='Test whether you can read, write and run /etc/passwd.',
             code="f=/etc/passwd\nfor t in r w x; do test -$t $f && echo \"$t: yes\" || echo \"$t: no\"; done\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own files',
    intro='<p>Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Your home folder', cmd='ls -ld ~', output='drwxr-x--- 42 vineeta vineeta 4096 Nov 11 09:10 /home/vineeta', note='Typical Ubuntu 22.04+ (750).'),
        dict(title='2 · Your SSH folder and keys', cmd='ls -la ~/.ssh', output='drwx------  2 vineeta vineeta 4096 Oct  2 10:00 .\n-rw-------  1 vineeta vineeta  411 Oct  2 10:00 id_ed25519\n-rw-r--r--  1 vineeta vineeta  101 Oct  2 10:00 id_ed25519.pub', note='Typical: private key 600, public key 644.'),
        dict(title='3 · System files', cmd="stat -c '%A %a %U:%G %n' /etc/passwd /etc/shadow /tmp /usr/bin/passwd", output=pc("stat -c '%A %a %U:%G %n' /etc/passwd /etc/shadow /tmp /usr/bin/passwd"), note='Recorded. s and t are special bits (Lesson 9.4).'),
        dict(title='4 · A whole path', cmd='namei -l /var/log/syslog', output='f: /var/log/syslog\ndrwxr-xr-x root   root   /\ndrwxr-xr-x root   root   var\ndrwxrwxr-x root   syslog log\n-rw-r----- syslog adm    syslog', note='Typical: only adm members (and root) can read it.'),
    ],
)

TRACE = dict(
    heading='Reading a mode in a script',
    intro='<p>Step through a script that splits a mode string into owner, group and others.</p>',
    code='''touch f; chmod 640 f
m=$(stat -c %A f)
owner=${m:1:3}; group=${m:4:3}; others=${m:7:3}
echo "mode $m: owner=$owner group=$group others=$others"
n=$(stat -c %a f)
echo "octal $n"
''',
    notes={1: 'File :: mode 640.', 2: 'Letters :: -rw-r-----.', 3: 'Split :: three characters each.', 4: 'Report.', 6: 'Octal :: stat -c %a on line 5 gave 640.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s script, a web check and a security audit.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Why won’t my script run?',
         problem='<p>A script fails with Permission denied. Show why and run it another way.</p>',
         inp='a script without x', approach=['ls -l: no x.', 'bash script.sh needs only r.'],
         code='''printf '#!/bin/sh\\necho hello\\n' > hi.sh
ls -l hi.sh
./hi.sh 2>&1; echo "exit $?"
bash hi.sh
''', notes={2: 'No x :: -rw-r--r--.', 3: 'Denied :: exit 126.', 4: 'bash reads it :: only r needed.'}, tryit='Add x in Lesson 9.2.', expect='any'),
    dict(level='i', tag='Web', title='Can the web server reach a page?',
         problem='<p>Check every folder on the way to a page for x for others.</p>',
         inp='a site folder', approach=['namei -l.', 'Look for folders without o+x.'],
         code='''mkdir -p site/a/b; echo page > site/a/b/index.html; chmod 750 site/a
namei -m site/a/b/index.html
find site -type d ! -perm -o+x
''', notes={2: 'Modes :: a is drwxr-x---.', 3: 'Blockers :: folders others cannot enter.'}, tryit='chmod o+x site/a and repeat.'),
    dict(level='a', tag='Security', title='Find readable secrets',
         problem='<p>List key and env files that others can read.</p>',
         inp='a mixed folder', approach=['find by name.', '-perm -o+r.'],
         code='''mkdir -p app; touch app/.env app/server.key app/readme.md
chmod 644 app/.env app/readme.md; chmod 600 app/server.key
find app -type f \\( -name '*.key' -o -name '.env' \\) -perm -o+r -exec stat -c '%a %n' {} +
''', notes={1: 'Files.', 2: 'Modes.', 3: 'Found :: .env is readable by others.'}, tryit='Also check -perm -g+r.'),
]

QUIZ = mix([
    dict(q='In -rw-r----- which class can read but not write?', options=['owner', 'group', 'others', 'nobody'], answer=1, why='r-- for the group.'),
    dict(q='What is -rwxr-xr-x in octal?', options=['644', '755', '775', '711'], answer=1, why='7 5 5.'),
    dict(q='On a directory, what does x allow?', options=['run it', 'enter it and reach files inside', 'list names', 'delete it'], answer=1, why='“search”.'),
    dict(q='To delete a file you need…', options=['w on the file', 'w and x on the folder', 'x on the file', 'r on the folder'], answer=1, why='Deleting changes the folder.'),
    dict(q='You own a file with mode 0446. Can you write it?', options=['yes', 'no: owner bits r-- apply', 'only with sudo', 'yes, others has w'], answer=1, why='One class.'),
    dict(q='Which shows a folder’s own permissions?', options=['ls -l DIR', 'ls -ld DIR', 'ls -la DIR', 'stat -f DIR'], answer=1, why='-d.'),
    dict(q='Which command lists modes of every folder on a path?', options=['namei -l', 'pwd -P', 'ls -R', 'tree'], answer=0, why='namei.'),
    dict(q='Typical mode for an SSH private key?', options=['644', '600', '755', '777'], answer=1, why='Only the owner.'),
])

REVISION = [
    '<code>-rwxr-x---</code>: type, then owner, group, others; r=4 w=2 x=1 → 750.',
    'File: r read, w change, x run. Folder: r list, w create/delete (with x), x enter/reach.',
    'One class only: owner, else group, else others.',
    'Opening /a/b/f needs x on every folder and r on f. Deleting needs w+x on the folder.',
    '<code>ls -l</code>, <code>ls -ld</code>, <code>stat -c \'%A %a %U %G %n\'</code>, <code>namei -l</code>, <code>[ -r -w -x ]</code>.',
    'Common modes: 644 files, 600 secrets, 755 scripts/folders, 700 private, 750 homes/teams. Avoid 777.',
]

FAQ = [
    ('What does -rw-r--r-- mean?', 'A regular file; the owner can read and write, the group and others can only read (644).'),
    ('What do r, w and x mean on a directory?', 'r lists names, w creates and deletes entries (with x), x lets you enter it and reach files inside.'),
    ('How do I see a directory’s permissions?', 'ls -ld DIR.'),
    ('How do I see permissions as numbers?', "stat -c '%a %n' FILE."),
    ('Why do I get Permission denied although the file is 644?', 'A folder on the path is missing x for you; check with namei -l.'),
    ('What is the difference between owner, group and others?', 'Owner is one user, group is one group of users, others is everyone else; Linux uses exactly one of them for you.'),
    ('What does a + after the permissions mean?', 'The file has an ACL with extra rules (getfacl).'),
]

PRACTICE_INTRO = 'Small reading tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Octal of passwd', stmt='Print the octal mode of /etc/passwd.', inp='/etc/passwd', code="stat -c %a /etc/passwd\n", explain='644.'),
    dict(level='easy', title='Folder itself', stmt='Show /tmp’s own permissions.', inp='/tmp', code="ls -ld /tmp | cut -d' ' -f1\n", explain='-d.'),
    dict(level='easy', title='Owner and group', stmt='Print owner and group of /etc/shadow.', inp='/etc/shadow', code="stat -c '%U %G' /etc/shadow\n", explain='%U %G.'),
    dict(level='medium', title='Letters to number', stmt='Create a file with -rw-r----- and print its octal.', inp='a file', code="touch g; chmod u=rw,g=r,o= g\nstat -c %a g\n", explain='640.'),
    dict(level='medium', title='Can I write it?', stmt='Test if you can write /etc/hosts.', inp='/etc/hosts', code="test -w /etc/hosts && echo yes || echo no\n", explain='test -w.'),
    dict(level='medium', title='Others’ bits', stmt='Print only the last three characters of the mode of /etc/shadow.', inp='/etc/shadow', code="m=$(stat -c %A /etc/shadow); echo ${m:7:3}\n", explain='Substring.'),
    dict(level='business', title='Blocking folders', stmt='List folders under site that others cannot enter.', inp='a tree',
         code="mkdir -p site/a/b site/c; chmod 700 site/c\nfind site -type d ! -perm -o+x\n", explain='! -perm -o+x.'),
    dict(level='business', title='Mode report', stmt='Count files in /etc (top level) by octal mode.', inp='/etc',
         code="find /etc -maxdepth 1 -type f -exec stat -c %a {} + | sort | uniq -c | sort -rn | head -3\n", explain='stat + uniq -c.'),
]

SCN_INTRO = 'Interview questions about reading permissions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Explain -rwxr-xr--.”', 'Asked in almost every Linux interview.', 'can you read all ten characters?',
        '''<ul>
          <li>Regular file; owner rwx, group r-x, others r--: 754.</li>
          <li>r=4 w=2 x=1.</li>
        </ul>''', 'reading it as one block of letters.') +
    scn('Web team', 'Junior', 'Nginx returns 403 for a new page', 'The file is 644 and owned by the developer.', 'do you check the path?',
        '''<ol>
          <li><code>sudo -u www-data cat FILE</code> to reproduce.</li>
          <li><code>namei -l FILE</code>: which folder lacks x for others?</li>
          <li>Add only that x (or put the site under /var/www).</li>
        </ol>''', 'chmod -R 777 /home.') +
    scn('Operations', 'Mid-level', '“Permission denied” as root', 'root cannot change a file.', 'do you know what else blocks root?',
        '''<ul>
          <li>Immutable attribute (<code>lsattr</code>, Lesson 9.5).</li>
          <li>Read-only mount (Lesson 15.3), NFS root_squash.</li>
          <li>SELinux/AppArmor denials in the audit log.</li>
        </ul>''', '“root can always do everything”.') +
    scn('Security team', 'Senior', 'Least privilege on a shared server', 'Hundreds of users, many projects.', 'can you design a model?',
        '''<ul>
          <li>Private homes (700/750), one group per project, SGID team folders (9.4), umask 027 (9.3).</li>
          <li>ACLs for exceptions (9.5); no world-writable files outside /tmp.</li>
          <li>Regular audits with find -perm.</li>
        </ul>''', 'one big shared folder with 777.')
) + interview([
    ('What does x mean on a directory?', 'Permission to enter it and access entries by name.'),
    ('What permission do you need to delete a file?', 'w and x on its directory.'),
    ('How do you see permissions in octal?', 'stat -c %a FILE.'),
    ('What is the first character in ls -l?', 'The file type: - file, d directory, l link, c/b device.'),
    ('Why does a symlink always show lrwxrwxrwx?', 'Its own mode is not used; the target’s permissions apply.'),
    ('Which class applies to the owner?', 'Only the owner bits, even if group or others have more.'),
    ('What does 600 mean?', 'Owner read and write; nobody else anything.'),
], [
    ('RHCSA (EX200)', '“List, set, and change standard ugo/rwx permissions”.'),
    ('LFCS', 'Manage file permissions and ownership.'),
    ('CompTIA Linux+', 'File permissions, octal notation, special cases for directories.'),
]) + distro('The permission model is identical on all Unix-like systems.', [
    ('rwx model', 'yes', 'yes', 'yes', 'Git Bash shows approximations of NTFS ACLs'),
    ('Home folder default', '750 (22.04+)', '700', '700 (drwxr-x---+ with ACL)', '-'),
    ('namei', 'util-linux', 'util-linux', 'not installed', '-'),
    ('stat -c', 'GNU', 'GNU', 'stat -f (BSD syntax)', 'GNU'),
    ('Extra markers', '+ ACL', '+ ACL, . SELinux', '@ xattr, + ACL', '-'),
]) + teaser('9.2', 'Riya now reads every mode at a glance. But .env is still readable by everyone and deploy.sh still has no x. Next: chmod with letters (u+x, go-r) and with numbers (755, 644, 600), and why -R on a whole tree is dangerous.')

CHEATSHEET = cheatsheet('Reading permissions', [
    ('The string', [('-rwxr-x---', 'type u g o'), ('- d l c b', 'file dir link dev'), ('r w x', '4 2 1'), ('750', 'rwx r-x ---'), ('+ at end', 'ACL')]),
    ('Files', [('r', 'read contents'), ('w', 'change contents'), ('x', 'run'), ('script', 'needs r + x'), ('600', 'secrets')]),
    ('Folders', [('r', 'list names'), ('w', 'create/delete (with x)'), ('x', 'enter, reach'), ('delete file', 'w+x on folder'), ('path', 'x on every folder')]),
    ('Commands', [('ls -l / -la', 'files'), ('ls -ld DIR', 'folder itself'), ("stat -c '%a %n'", 'octal'), ('namei -l PATH', 'whole path'), ('test -r/-w/-x', 'can I?')]),
])

MINDMAP = mindmap('Permissions', [
    ('String', 'blue', ['type + 9 bits', 'u g o', 'octal 4 2 1']),
    ('Files', 'green', ['r read', 'w write', 'x run']),
    ('Folders', 'amber', ['r list', 'w add/delete', 'x enter']),
    ('Rule', 'violet', ['one class', 'owner → group → others', 'root skips']),
    ('Path', 'acc', ['x on every folder', 'namei -l', '403']),
    ('Commands', 'red', ['ls -l -ld', 'stat -c', 'test -r -w -x']),
])

LAB = lab('read and predict permissions', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab91 && cd ~/lab91 && rm -rf * .env
mkdir -p web/pages locked; echo hi > web/pages/index.html; echo x > .env; printf '#!/bin/sh\\necho ok\\n' > tool.sh
chmod 644 web/pages/index.html .env tool.sh; chmod 711 web; chmod 700 locked''',
    tasks=['Write the octal modes of <code>.env</code>, <code>tool.sh</code>, <code>web</code> and <code>locked</code> (one per line, in that order) into <code>modes.txt</code>.',
           'Write the names of folders under the lab that others cannot enter into <code>blocked.txt</code>.',
           'Write <code>yes</code> or <code>no</code>: can you run <code>./tool.sh</code> as it is? Into <code>run.txt</code>.',
           'Write the permission string of the folder <code>web</code> itself (e.g. drwx------) into <code>web.txt</code>.'],
    solution='''stat -c %a .env tool.sh web locked > modes.txt
find . -mindepth 1 -type d ! -perm -o+x > blocked.txt
[ -x tool.sh ] && echo yes > run.txt || echo no > run.txt
ls -ld web | cut -d' ' -f1 > web.txt''',
    check='''cd ~/lab91
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 modes"   '[ "$(cat modes.txt 2>/dev/null)" = "$(printf "644\\n644\\n711\\n700")" ]'
ok "2 blocked" 'grep -qx "./locked" blocked.txt 2>/dev/null && [ "$(wc -l < blocked.txt)" = 1 ]'
ok "3 run"     '[ "$(cat run.txt 2>/dev/null)" = no ]'
ok "4 web"     '[ "$(cat web.txt 2>/dev/null)" = drwx--x--x ]' ''')
