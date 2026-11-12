import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='08-users-and-groups', lesson='01-users-and-groups-uid-gid-etc-passwd-etc-shadow', n='8.1',
    module_label='Module 8 · Users, groups and sudo',
    title='Users and groups: UID, GID, /etc/passwd, /etc/shadow, id, who, w and last',
    desc='Users, groups, UID and GID explained; root, system and normal accounts; every field of /etc/passwd, /etc/shadow and /etc/group; id, whoami, groups and getent; who, w, last, lastb and lastlog; how numbers become names (NSS) and how passwords are checked, animated with real outputs.',
    og_desc='What users, groups, UIDs and GIDs are, how to read /etc/passwd, /etc/shadow and /etc/group, and who is logged in, with real outputs.',
    minutes=38, level='Beginner → Advanced',
    lead='Linux decides who can read a file or run a command from two numbers: a user ID and group IDs. This lesson explains where they live, how to read the account files, and how admins, DBAs, DevOps, security and testers use id, getent, who, w and last.',
    chips=['passwd and shadow field by field', 'Numbers become names (animated)', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Who am I, and what do the account files say?
id
whoami
groups
getent passwd root
grep '^root:' /etc/passwd | tr ':' '\\n' | nl
getent group root
ls -l /etc/passwd /etc/shadow
"""

RUN = dict(
    heading='Your identity and the account files',
    intro='<p>Print your identity, then read root’s line in /etc/passwd field by field.</p>',
    code=MAIN,
    anno=[
        ("grep '^root:' /etc/passwd | tr ':' '\\n' | nl", 'The seven fields, numbered.'),
        ('ls -l /etc/passwd /etc/shadow', 'shadow is not readable by others.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is your UID?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what UID and shell does root have? Then run.',
             code="getent passwd root | cut -d: -f3,7\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this prints whole lines, not user names. Add the delimiter.',
             code="cut -f1 /etc/passwd | head -3\n"),
        dict(label='4 · Your turn', hint='Print the names of all accounts whose shell is /usr/sbin/nologin, first 5.',
             code="awk -F: '$7==\"/usr/sbin/nologin\" {print $1}' /etc/passwd | head -5\n"),
        dict(label='5 · Challenge', hint='Count accounts per shell, most common first.',
             code="cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real login records',
    intro='<p>Your PC has real logins. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Your identity', cmd='id', output='uid=1000(vineeta) gid=1000(vineeta) groups=1000(vineeta),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev)', note='Typical Ubuntu desktop: the first user is in sudo and adm.'),
        dict(title='2 · Who is logged in', cmd='w', output=' 10:05:12 up  2:14,  1 user,  load average: 0.21, 0.30, 0.28\nUSER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\nvineeta  pts/0    -                07:51    0.00s  0.03s  0.00s w', note='Typical.'),
        dict(title='3 · Login history', cmd='last -n 5', output='vineeta  pts/0                         Wed Nov 11 07:51   still logged in\nreboot   system boot  6.8.0-45-generic Wed Nov 11 07:50   still running', note='Typical.'),
        dict(title='4 · Password status', cmd='sudo passwd -S $USER', output='vineeta P 2026-09-02 0 99999 7 -1', note='Typical: P = password set.'),
        dict(title='5 · Where names come from', cmd="grep -E '^(passwd|group|shadow):' /etc/nsswitch.conf", output=pc("grep -E '^(passwd|group|shadow):' /etc/nsswitch.conf"), note='Recorded on our build machine.'),
    ],
)

TRACE = dict(
    heading='Reading an account into variables',
    intro='<p>Step through a script that splits a passwd line into named variables.</p>',
    code='''line=$(getent passwd root)
IFS=: read -r name pw uid gid comment home shell <<< "$line"
echo "$name has UID $uid, home $home, shell $shell"
[ "$uid" -eq 0 ] && echo "$name is the superuser"
''',
    notes={1: 'One line :: the root account.', 2: 'Split :: IFS=: cuts at colons into 7 variables.', 3: 'Report.', 4: 'Check :: UID 0 = root.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a help-desk check, a security audit and a DBA question.'
EXAMPLES = [
    dict(level='b', tag='Help desk', title='What is this account?',
         problem='<p>Show the UID, home and shell of an account in a readable way.</p>',
         inp='the root account', approach=['getent passwd.', 'cut the fields.'],
         code='''getent passwd root
getent passwd root | cut -d: -f1,3,6,7 | tr ':' ' '
''', notes={1: 'Raw line.', 2: 'Readable :: name UID home shell.'}, tryit='Try daemon and nobody.'),
    dict(level='i', tag='Security', title='UID 0 and login shells',
         problem='<p>Make sure only root has UID 0, and list which accounts have a real shell.</p>',
         inp='/etc/passwd', approach=['awk $3==0.', 'grep shells.'],
         code='''awk -F: '$3==0 {print "UID 0:", $1}' /etc/passwd
grep -E '(bash|sh)$' /etc/passwd | cut -d: -f1,7
''', notes={1: 'Only root.', 2: 'Shell accounts :: these can log in.'}, tryit='Exclude root from the second list.'),
    dict(level='a', tag='Sysadmin', title='System vs human accounts',
         problem='<p>Count system accounts (UID 1–999) and human accounts (1000–60000) using the limits in /etc/login.defs.</p>',
         inp='/etc/login.defs and /etc/passwd', approach=['Read UID_MIN/UID_MAX.', 'awk with -v.'],
         code='''min=$(awk '/^UID_MIN/ {print $2}' /etc/login.defs); max=$(awk '/^UID_MAX/ {print $2}' /etc/login.defs)
echo "human UIDs: $min-$max"
awk -F: -v min="$min" -v max="$max" '$3>0 && $3<min {s++} $3>=min && $3<=max {h++} END {print "system:", s, "human:", h+0}' /etc/passwd
''', notes={1: 'Limits.', 2: 'Range.', 3: 'Count :: nobody (65534) is outside both.'}, tryit='Print the human names too.'),
]

QUIZ = mix([
    dict(q='What is the UID of root?', options=['1', '0', '1000', '65534'], answer=1, why='UID 0 bypasses permission checks.'),
    dict(q='What does the x in the second field of /etc/passwd mean?', options=['account locked', 'the password hash is in /etc/shadow', 'no password', 'executable'], answer=1, why='Shadow passwords.'),
    dict(q='Which field of /etc/passwd is the login shell?', options=['5', '6', '7', '4'], answer=2, why='name:x:UID:GID:comment:home:shell.'),
    dict(q='Who can read /etc/shadow?', options=['everyone', 'root and the shadow group', 'the user only', 'nobody'], answer=1, why='-rw-r----- root shadow.'),
    dict(q='Which command shows the UID, GID and all groups?', options=['whoami', 'id', 'who', 'last'], answer=1, why='whoami shows only the name.'),
    dict(q='You were added to docker, but id does not show it in your open terminal. Why?', options=['the command failed', 'groups are read at login', 'you need sudo id', 'docker hides it'], answer=1, why='Log in again or newgrp.'),
    dict(q='Which shows past logins and reboots?', options=['who', 'w', 'last', 'id'], answer=2, why='From /var/log/wtmp.'),
    dict(q='Typical UID range for system (service) accounts on Ubuntu?', options=['0', '1–999', '1000–60000', '65534'], answer=1, why='Humans start at 1000.'),
])

REVISION = [
    'Users have a <b>UID</b>, groups a <b>GID</b>; the kernel only uses the numbers. root = 0, services 1–999, people 1000+.',
    '<code>/etc/passwd</code>: <code>name:x:UID:GID:comment:home:shell</code>, readable by all.',
    '<code>/etc/shadow</code>: <code>name:hash:last:min:max:warn:inactive:expire</code>, root only. <code>!</code>/<code>*</code> = locked.',
    '<code>/etc/group</code>: <code>group:x:GID:members</code>. One primary group (in passwd), many supplementary.',
    '<code>id</code>, <code>id -u</code>, <code>id -Gn</code>, <code>whoami</code>, <code>groups</code>, <code>getent passwd|group NAME</code>.',
    '<code>who</code>, <code>w</code> (now), <code>last</code>, <code>sudo lastb</code>, <code>lastlog</code> (history).',
    'New groups apply at next login. Edit accounts with tools (8.2), not an editor; <code>vipw</code>, <code>pwck</code>.',
]

FAQ = [
    ('How do I list all users in Linux?', 'getent passwd (or cut -d: -f1 /etc/passwd). Humans: awk -F: \'$3>=1000 && $3<65534\' /etc/passwd.'),
    ('What is the difference between /etc/passwd and /etc/shadow?', 'passwd lists accounts and is readable by all; shadow holds password hashes and ageing and is readable only by root.'),
    ('How do I see which groups a user belongs to?', 'id USER or groups USER.'),
    ('What is a UID?', 'The number the kernel uses to identify a user; root is 0.'),
    ('How do I see who is logged in?', 'who or w (w also shows what each user is running).'),
    ('How do I see login history?', 'last (successful), sudo lastb (failed), lastlog (latest per account).'),
    ('Why does a new group not work in my terminal?', 'Groups are set at login; log out and in, or run newgrp GROUP.'),
]

PRACTICE_INTRO = 'Small identity tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='My UID', stmt='Print only your numeric UID.', inp='you', code="id -u\n", explain='-u.'),
    dict(level='easy', title='root’s home', stmt='Print root’s home folder.', inp='/etc/passwd', code="getent passwd root | cut -d: -f6\n", explain='Field 6.'),
    dict(level='easy', title='Group names', stmt='Print your group names.', inp='you', code="id -Gn\n", explain='-G -n.'),
    dict(level='medium', title='How many accounts', stmt='Count the lines in /etc/passwd.', inp='/etc/passwd', code="wc -l < /etc/passwd\n", explain='One line per account.'),
    dict(level='medium', title='Service shells', stmt='How many accounts use nologin?', inp='/etc/passwd', code="grep -c nologin /etc/passwd\n", explain='grep -c.'),
    dict(level='medium', title='GID of a group', stmt='Print the GID of the group sudo.', inp='/etc/group', code="getent group sudo | cut -d: -f3\n", explain='Field 3.'),
    dict(level='business', title='Accounts with a home in /home', stmt='List accounts whose home is under /home.', inp='/etc/passwd', code="awk -F: '$6 ~ /^\\/home\\// {print $1, $6}' /etc/passwd\n", explain='Regex on field 6.'),
    dict(level='business', title='UID 0 check', stmt='Print OK if root is the only UID 0 account.', inp='/etc/passwd', code="[ \"$(awk -F: '$3==0' /etc/passwd | wc -l)\" = 1 ] && echo OK || echo ALERT\n", explain='Count UID 0 lines.'),
]

SCN_INTRO = 'Interview questions about users and groups, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Explain /etc/passwd.”', 'Asked in almost every Linux interview.', 'do you know the fields?',
        '''<ul>
          <li>Seven fields: name, x, UID, GID, comment, home, shell.</li>
          <li>x: hash in /etc/shadow (root only).</li>
          <li>UID 0 root, 1–999 system, 1000+ users.</li>
        </ul>''', '“It stores the passwords.”') +
    scn('Help desk', 'Junior', '“I was added to the developers group but still get Permission denied”', 'The ticket says the group was added an hour ago.', 'do you know when groups apply?',
        '''<ol>
          <li><code>id NAME</code> (files) vs <code>id</code> in their session.</li>
          <li>Log out and back in, or <code>newgrp developers</code>.</li>
          <li>Then check the folder’s group and permissions (Lesson 9.1).</li>
        </ol>''', 'chmod 777 on the folder.') +
    scn('Security team', 'Mid-level', 'Audit a server you have never seen', 'You get a shell on an old server.', 'what do you check first?',
        '''<ul>
          <li>Extra UID 0: <code>awk -F: '$3==0' /etc/passwd</code>; empty passwords in shadow.</li>
          <li>Members of sudo/wheel/docker; accounts with shells; lastlog for stale accounts.</li>
          <li><code>last</code> and <code>sudo lastb</code> for unusual logins.</li>
        </ul>''', 'only checking root’s password.') +
    scn('Platform', 'Senior', 'Same UID, different names on two servers', 'Files copied over NFS appear owned by the wrong person.', 'do you understand that only numbers travel?',
        '''<ul>
          <li>Files store UIDs; aman=1005 on one host may be 1005=priya on another.</li>
          <li>Keep UIDs consistent: central directory (LDAP/SSSD/AD) or fixed UIDs in provisioning.</li>
          <li>Fix existing data with find -uid OLD -exec chown NEW.</li>
        </ul>''', '“rename the users”.')
) + interview([
    ('What is the difference between a primary and a supplementary group?', 'Primary: one, from passwd, used for new files. Supplementary: extra groups in /etc/group.'),
    ('How do you check whether a user is locked?', 'sudo passwd -S NAME (L) or ! at the start of the shadow hash.'),
    ('Why is /etc/shadow separate?', 'So hashes are not readable by everyone.'),
    ('whoami vs id?', 'whoami: name only; id: UID, GID, groups.'),
    ('How do you see failed login attempts?', 'sudo lastb, or journalctl -u ssh / /var/log/auth.log.'),
    ('What is UID 65534?', 'nobody: an account with no rights.'),
    ('What does getent do?', 'Reads passwd/group/hosts through NSS, so it also sees LDAP users.'),
], [
    ('RHCSA (EX200)', '“Create, delete, and modify local user accounts”: requires reading passwd, shadow and group.'),
    ('LFCS', 'User and group management; system accounts.'),
    ('CompTIA Linux+', 'User account files, UID/GID, who/w/last.'),
]) + distro('The files are the same everywhere; group names and ranges differ.', [
    ('Admin group', 'sudo', 'wheel', 'admin', '-'),
    ('First user UID', '1000', '1000', '501', '-'),
    ('Hash in shadow', '$y$ yescrypt', '$6$ SHA-512 (RHEL 9: yescrypt optional)', 'no shadow: dscl / Directory Services', '-'),
    ('Login records', '/var/log/wtmp, btmp', 'same', 'last works; no lastb', 'Git Bash: none'),
    ('id, who, w, last', 'yes', 'yes', 'yes', 'id and whoami only'),
]) + teaser('8.2', 'Aman joined. Riya must create his account with a home folder and the right shell, set a temporary password that he must change on first login, and lock the account of someone who left. Which commands do this safely?')

CHEATSHEET = cheatsheet('Users and groups', [
    ('Identity', [('id', 'UID GID groups'), ('id -u / -un', 'number / name'), ('id -Gn USER', 'groups'), ('whoami', 'name'), ('groups', 'group names')]),
    ('Account files', [('/etc/passwd', 'name:x:UID:GID:…:home:shell'), ('/etc/shadow', 'hashes (root)'), ('/etc/group', 'group:x:GID:members'), ('/etc/gshadow', 'group admins'), ('/etc/login.defs', 'UID ranges')]),
    ('Look up', [('getent passwd NAME', 'one account'), ('getent group NAME', 'members'), ('sudo passwd -S NAME', 'P / L / NP'), ('sudo chage -l NAME', 'ageing'), ('cut -d: -f1 /etc/passwd', 'names')]),
    ('Logins', [('who / who -b', 'now / boot'), ('w', 'who + what'), ('last -n 5', 'history'), ('sudo lastb', 'failed'), ('lastlog', 'latest per user')]),
])

MINDMAP = mindmap('Users and groups', [
    ('Identity', 'blue', ['UID / GID', 'primary + extra groups', 'id, whoami']),
    ('Accounts', 'green', ['root 0', 'system 1–999', 'people 1000+']),
    ('passwd', 'amber', ['7 fields', 'x = shadow', 'shell nologin']),
    ('shadow', 'red', ['hash $y$', 'ageing', '! locked']),
    ('group', 'violet', ['group:x:GID:members', 'getent group', 'newgrp']),
    ('Logins', 'acc', ['who, w', 'last, lastb', 'lastlog']),
])

LAB = lab('read the account files', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab81 && cd ~/lab81 && rm -f *.txt''',
    tasks=['Write your numeric UID into <code>uid.txt</code>.',
           'Write the login shell of root (field 7) into <code>rootshell.txt</code>.',
           'Write the number of accounts whose shell contains <code>nologin</code> into <code>nologin.txt</code>.',
           'Write the names of all your groups, one per line, sorted, into <code>groups.txt</code>.'],
    solution='''id -u > uid.txt
getent passwd root | cut -d: -f7 > rootshell.txt
grep -c nologin /etc/passwd > nologin.txt
id -Gn | tr ' ' '\\n' | sort > groups.txt''',
    check='''cd ~/lab81
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 uid"        '[ "$(cat uid.txt 2>/dev/null)" = "$(id -u)" ]'
ok "2 root shell" '[ "$(cat rootshell.txt 2>/dev/null)" = "$(getent passwd root | cut -d: -f7)" ]'
ok "3 nologin"    '[ "$(cat nologin.txt 2>/dev/null)" = "$(grep -c nologin /etc/passwd)" ]'
ok "4 groups"     '[ "$(cat groups.txt 2>/dev/null)" = "$(id -Gn | tr " " "\\n" | sort)" ]' ''')
