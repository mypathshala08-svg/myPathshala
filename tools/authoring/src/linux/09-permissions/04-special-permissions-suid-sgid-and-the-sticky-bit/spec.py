import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='09-permissions', lesson='04-special-permissions-suid-sgid-and-the-sticky-bit', n='9.4',
    module_label='Module 9 · Permissions and ownership',
    title='Special permissions: SUID, SGID and the sticky bit',
    desc='SUID (4), SGID (2) and the sticky bit (1): what they do on programs and on folders, s S t T in ls -l, chmod u+s g+s +t and 4-digit modes (4755, 2770, 1777, 3770), team folders with SGID, shared folders with the sticky bit, why SUID scripts are ignored, effective vs real UID, nosuid, capabilities, and SUID audits with find -perm, with real outputs and animations.',
    og_desc='Understand and use SUID, SGID and the sticky bit: passwd, team folders and /tmp explained with real outputs.',
    minutes=40, level='Beginner → Advanced',
    lead='Three special bits explain how passwd writes a root-only file, why nobody can delete your files in /tmp, and how team folders keep the team group. This lesson explains each, how to set them, and how admins, data teams, DevOps, web and security use and audit them.',
    chips=['SUID animated', 'Team folders with SGID', 'Sticky bit', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# The 4th digit
touch prog data; mkdir team shared
chmod 4755 prog; chmod 4644 data
chmod 2770 team; chmod 1777 shared
ls -ld prog data team shared
stat -c '%a %n' prog data team shared
ls -l /usr/bin/passwd; ls -ld /tmp
"""

RUN = dict(
    heading='Set and read the special bits',
    intro='<p>Set SUID, SGID and sticky with 4-digit modes, and compare with passwd and /tmp.</p>',
    code=MAIN,
    anno=[('chmod 4755 prog; chmod 4644 data', 's vs S: x or no x underneath.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Where do you see a capital S?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does ls show for chmod 3770? Then run.', code="mkdir box; chmod 3770 box; ls -ld box\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is a /tmp-like folder. Fix the mode.', code="mkdir pub; chmod 777 pub; ls -ld pub\n"),
        dict(label='4 · Your turn', hint='Count SUID files in /usr/bin.', code="find /usr/bin -perm -4000 -type f | wc -l\n"),
        dict(label='5 · Challenge', hint='Show that SUID on a script does nothing: it still prints your UID.', code="printf '#!/bin/sh\\nid -u\\n' > s.sh; chmod 4755 s.sh; ./s.sh\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: audit special bits',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · SUID programs', cmd='find / -xdev -perm -4000 -type f 2>/dev/null | sort', output=pc('find /usr /bin /sbin -xdev -perm -4000 -type f 2>/dev/null | sort'), note='Recorded (a desktop also shows pkexec, snap-confine, …).'),
        dict(title='2 · Capabilities', cmd='getcap -r /usr/bin /usr/sbin 2>/dev/null', output='/usr/bin/ping cap_net_raw=ep\n/usr/bin/mtr-packet cap_net_raw=ep', note='Typical desktop.'),
        dict(title='3 · Mounts with nosuid', cmd='findmnt -no TARGET,OPTIONS | grep nosuid | head -4', output='/dev nosuid,relatime\n/run nosuid,nodev,noexec,relatime\n/dev/shm nosuid,nodev\n/run/user/1000 nosuid,nodev,relatime', note='Typical.'),
        dict(title='4 · Sticky folders', cmd="find / -xdev -type d -perm -1000 2>/dev/null", output='/tmp\n/var/tmp', note='Typical.'),
    ],
)

TRACE = dict(
    heading='Reading the special digit',
    intro='<p>Step through a script that decodes the 4th digit of a mode.</p>',
    code='''mkdir t; chmod 3770 t
m=$(stat -c %a t)
s=${m:0:1}
out=""
for bit in "4 SUID" "2 SGID" "1 sticky"; do
  read -r v name <<< "$bit"
  if [ $((s & v)) -ne 0 ]; then out="$out $name"; fi
done
echo "mode $m:$out"
''',
    notes={1: 'Folder :: 3770.', 2: 'Mode.', 3: 'First digit :: 3 = 2 + 1.', 7: 'Test a bit :: 4 no, 2 yes, 1 yes, so the script prints “ SGID sticky”.'},
)

WORKED_INTRO = 'Three tasks from real jobs, recorded: a team folder, an upload folder and an audit.'
EXAMPLES = [
    dict(level='b', tag='Data team', title='New files keep the team group',
         problem='<p>Make /tmp/fin so files created by aman belong to group finance.</p>',
         inp='group finance', approach=['chgrp + chmod 2770.', 'Create as aman.'],
         code='''sudo rm -rf /tmp/fin; sudo mkdir /tmp/fin; sudo chgrp finance /tmp/fin; sudo chmod 2770 /tmp/fin
sudo -u aman touch /tmp/fin/q4.csv
sudo ls -l /tmp/fin; sudo rm -rf /tmp/fin
''', notes={1: 'SGID folder.', 2: 'aman’s file.', 3: 'Group finance.'}, tryit='Use 0770 and compare.'),
    dict(level='i', tag='Web', title='Shared upload folder',
         problem='<p>Everyone may upload; nobody may delete another user’s upload.</p>',
         inp='a shared folder', approach=['1777.', 'Test a delete.'],
         code='''sudo rm -rf /tmp/up; sudo mkdir /tmp/up; sudo chmod 1777 /tmp/up
sudo -u aman touch /tmp/up/a.pdf
rm -f /tmp/up/a.pdf 2>&1; ls /tmp/up
sudo rm -rf /tmp/up
''', notes={1: 'Sticky.', 2: 'aman uploads.', 3: 'riya cannot delete :: a.pdf is still there.'}, tryit='Remove the 1 and try again.'),
    dict(level='a', tag='Security', title='Baseline and diff',
         problem='<p>Save today’s SUID list and detect a new SUID file.</p>',
         inp='/usr/bin plus a test folder', approach=['sort > baseline.', 'comm -13.'],
         code='''find /usr/bin -perm -4000 -type f | sort > base.txt
mkdir -p t; cp /bin/true t/true; chmod u+s t/true
find /usr/bin t -perm -4000 -type f | sort | comm -13 base.txt -
''', notes={1: 'Baseline.', 2: 'A new SUID file.', 3: 'Only new :: t/true.'}, tryit='Add -perm /6000 for SGID too.'),
]

QUIZ = mix([
    dict(q='What does SUID on a program do?', options=['runs it as root always', 'runs it with the file owner’s rights', 'runs it with the caller’s group', 'makes it immutable'], answer=1, why='Owner, which is often root.'),
    dict(q='SGID on a folder makes new files…', options=['executable', 'get the folder’s group', 'owned by root', 'undeletable'], answer=1, why='Group inheritance.'),
    dict(q='What does the t in drwxrwxrwt mean?', options=['temporary', 'sticky: only owners delete', 'text file', 'trusted'], answer=1, why='Sticky.'),
    dict(q='What is chmod 2770 in ls -l?', options=['drwxrws---', 'drwsrwx---', 'drwxrwx--T', 'drwxrwxrwt'], answer=0, why='s in the group part.'),
    dict(q='Why does a SUID shell script still run as you?', options=['bug', 'Linux ignores SUID on scripts', 'needs 6755', 'needs sudo'], answer=1, why='Security.'),
    dict(q='What does capital S mean?', options=['SUID with x', 'SUID without x underneath', 'sticky', 'socket'], answer=1, why='Usually a mistake.'),
    dict(q='Which finds SUID files?', options=['find / -perm -4000', 'find / -suid', 'ls -s /', 'stat -s'], answer=0, why='-perm -4000.'),
    dict(q='Mount option that ignores SUID?', options=['noexec', 'nosuid', 'ro', 'nodev'], answer=1, why='nosuid.'),
])

REVISION = [
    '4th digit: <b>4</b> SUID, <b>2</b> SGID, <b>1</b> sticky (4755, 2770, 1777, 3770).',
    'SUID program: runs as the file owner (passwd, sudo). Scripts: ignored.',
    'SGID program: runs with the file’s group. SGID folder: new files get the folder’s group; subfolders inherit SGID.',
    'Sticky folder: only the file owner, folder owner or root deletes/renames (/tmp 1777).',
    '<code>s</code>/<code>t</code> = with x; <code>S</code>/<code>T</code> = without x.',
    'Audit: <code>find / -xdev -perm /6000 -type f</code>; harden with nosuid mounts and capabilities.',
]

FAQ = [
    ('What is SUID in Linux?', 'A permission bit (4000) that makes a program run with the privileges of its owner, e.g. passwd runs as root.'),
    ('What is the sticky bit?', 'A bit (1000) on a directory that lets only a file’s owner (or the directory owner or root) delete or rename it, as in /tmp.'),
    ('What does SGID do on a directory?', 'New files and folders inside get the directory’s group, which keeps team files in the team group.'),
    ('How do I find SUID files?', 'find / -xdev -perm -4000 -type f (use -perm /6000 for SUID or SGID).'),
    ('What does chmod 1777 mean?', 'rwx for everyone plus the sticky bit: drwxrwxrwt.'),
    ('Why doesn’t SUID work on my script?', 'Linux ignores SUID/SGID on interpreted scripts; use sudo rules.'),
    ('What does a capital S mean in ls -l?', 'The special bit is set but the execute bit under it is not.'),
]

PRACTICE_INTRO = 'Small special-bit tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Sticky /tmp', stmt='Print /tmp’s octal mode.', inp='/tmp', code="stat -c %a /tmp\n", explain='1777.'),
    dict(level='easy', title='passwd', stmt='Print passwd’s mode string.', inp='/usr/bin/passwd', code="stat -c %A /usr/bin/passwd\n", explain='-rwsr-xr-x.'),
    dict(level='easy', title='SGID folder', stmt='Create a folder with mode 2775 and show ls -ld.', inp='a folder', code="mkdir g; chmod 2775 g; ls -ld g | cut -d' ' -f1\n", explain='drwxrwsr-x.'),
    dict(level='medium', title='Add sticky', stmt='Add the sticky bit to a 777 folder.', inp='a folder', code="mkdir p; chmod 777 p; chmod +t p; stat -c '%a %A' p\n", explain='1777.'),
    dict(level='medium', title='Remove SUID', stmt='Remove SUID from a file with 4755.', inp='a file', code="touch f; chmod 4755 f; chmod u-s f; stat -c %a f\n", explain='755.'),
    dict(level='medium', title='Capital T', stmt='Show the mode string for 1770.', inp='a folder', code="mkdir t; chmod 1770 t; stat -c %A t\n", explain='T: no x for others.'),
    dict(level='business', title='SGID programs', stmt='List SGID programs in /usr/bin with their group.', inp='/usr/bin', code="find /usr/bin -perm -2000 -type f -exec stat -c '%G %n' {} +\n", explain='-perm -2000.'),
    dict(level='business', title='Risky folders', stmt='Find world-writable folders without sticky under a test tree.', inp='a tree', code="mkdir -p w/a w/b; chmod 777 w/a; chmod 1777 w/b\nfind w -type d -perm -0002 ! -perm -1000\n", explain='Only w/a.'),
]

SCN_INTRO = 'Interview questions about special permissions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What are SUID, SGID and sticky?”', 'Asked in most Linux interviews.', 'can you give one example each?',
        '''<ul>
          <li>SUID: passwd runs as root.</li>
          <li>SGID: team folders keep the group.</li>
          <li>Sticky: /tmp, only owners delete.</li>
        </ul>''', 'mixing up SGID and sticky.') +
    scn('Data team', 'Junior', 'Shared folder: files have the wrong group', 'Analysts cannot edit each other’s files.', 'do you know SGID + umask?',
        '''<ol>
          <li><code>chgrp -R team DIR</code>; <code>chmod 2770 DIR</code>.</li>
          <li>umask 002 (or default ACLs, 9.5) for group write.</li>
          <li>Add the sticky bit if people must not delete others’ files.</li>
        </ol>''', 'a cron job running chgrp every 5 minutes.') +
    scn('Security team', 'Mid-level', 'Unknown SUID binary in /home', 'An audit finds /home/dev/.cache/x with -rwsr-xr-x root.', 'can you respond?',
        '''<ul>
          <li>Do not run it; record hash and metadata; remove the bit / isolate.</li>
          <li>Check how a root-owned file got there (logs, sudo history).</li>
          <li>Mount /home with nosuid; schedule SUID baseline diffs.</li>
        </ul>''', 'deleting it and moving on.') +
    scn('Platform', 'Senior', 'Remove SUID from the base image', 'Reduce attack surface in containers.', 'do you know alternatives?',
        '''<ul>
          <li>Strip SUID/SGID in the image (<code>find / -perm /6000 -exec chmod a-s {} +</code>).</li>
          <li>Use capabilities (setcap) and drop the rest; run as non-root; no-new-privileges.</li>
        </ul>''', '“containers are isolated, it does not matter”.')
) + interview([
    ('How do you set SUID?', 'chmod u+s FILE or chmod 4755 FILE.'),
    ('What does 2755 mean?', 'SGID + rwxr-xr-x.'),
    ('What is the difference between s and S?', 's: special bit with x; S: without x.'),
    ('Does SUID work on directories?', 'Ignored on Linux.'),
    ('What is the effective UID?', 'The UID used for permission checks; root for SUID-root programs.'),
    ('How do you find SGID files?', 'find / -perm -2000 -type f.'),
    ('What replaces many SUID programs?', 'Linux capabilities.'),
], [
    ('RHCSA (EX200)', '“Create and configure set-GID directories for collaboration”.'),
    ('LFCS', 'Special permissions: SUID, SGID, sticky.'),
    ('CompTIA Linux+', 'Special permissions and their octal values.'),
]) + distro('The bits are the same everywhere; details differ.', [
    ('SUID on scripts', 'ignored', 'ignored', 'ignored', '-'),
    ('SGID on folders', 'group inheritance', 'same', 'BSD: always inherits the folder group', '-'),
    ('/tmp mode', '1777', '1777', '1777 (/private/tmp)', '-'),
    ('Capabilities', 'getcap/setcap', 'same', 'no (entitlements)', '-'),
    ('Typical SUID set', 'sudo passwd su mount …', 'same + pkexec', 'sudo su passwd login', '-'),
]) + teaser('9.5', 'Priya from audit needs read access to one folder, but she is not in the team group, and Riya does not want to open it to everyone. Three classes are not enough. Next: ACLs with getfacl and setfacl, and file attributes that even root cannot ignore.')

CHEATSHEET = cheatsheet('SUID, SGID, sticky', [
    ('SUID (4)', [('chmod u+s f', 'set'), ('4755', 'rwsr-xr-x'), ('runs as owner', 'passwd, sudo'), ('scripts', 'ignored'), ('chmod u-s', 'remove')]),
    ('SGID (2)', [('chmod g+s d', 'set'), ('2770', 'drwxrws---'), ('folder', 'new files get its group'), ('program', 'runs with file group'), ('chmod g-s', 'remove')]),
    ('Sticky (1)', [('chmod +t d', 'set'), ('1777', 'drwxrwxrwt'), ('effect', 'only owners delete'), ('3770', 'SGID + sticky'), ('T', 'no x for others')]),
    ('Audit', [('find / -perm -4000', 'SUID'), ('find / -perm -2000', 'SGID'), ('find / -perm /6000', 'either'), ('getcap -r /usr', 'capabilities'), ('nosuid', 'mount option')]),
])

MINDMAP = mindmap('Special bits', [
    ('SUID 4', 'red', ['run as owner', 'passwd sudo', 'not scripts']),
    ('SGID 2', 'green', ['folder → group', 'program → group', 'team dirs']),
    ('Sticky 1', 'amber', ['only owners delete', '/tmp 1777', 'uploads']),
    ('ls -l', 'blue', ['s / S', 't / T', '4-digit modes']),
    ('Audit', 'violet', ['find -perm', 'baseline + comm', 'dpkg -S']),
    ('Harden', 'acc', ['nosuid', 'capabilities', 'remove bits']),
])

LAB = lab('team and drop folders', 'Build the lab, do the four tasks in your own terminal (sudo needed for task 4), then run the checker.',
    setup='''rm -rf ~/lab94; mkdir -p ~/lab94/team ~/lab94/drop; cd ~/lab94
cp /bin/true mytool; chmod 4755 mytool; chmod 777 drop''',
    tasks=['Make <code>team</code> an SGID folder with mode <code>2770</code>.',
           'Make <code>drop</code> a sticky, world-writable folder (<code>1777</code>).',
           'Remove the SUID bit from <code>mytool</code>, keeping it 755.',
           'Write the list of SUID files in <code>/usr/bin</code>, sorted, into <code>suid.txt</code>.'],
    solution='''chmod 2770 team
chmod 1777 drop
chmod u-s mytool
find /usr/bin -perm -4000 -type f | sort > suid.txt''',
    check='''cd ~/lab94
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 team"  '[ "$(stat -c %a team)" = 2770 ]'
ok "2 drop"  '[ "$(stat -c %a drop)" = 1777 ]'
ok "3 tool"  '[ "$(stat -c %a mytool)" = 755 ]'
ok "4 list"  'grep -qx /usr/bin/passwd suid.txt 2>/dev/null && [ "$(sort -c suid.txt 2>&1)" = "" ]' ''')
