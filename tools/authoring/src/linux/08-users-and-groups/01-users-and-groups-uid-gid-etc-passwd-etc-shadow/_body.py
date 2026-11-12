import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

TYP = 'Typical output on an Ubuntu server with SSH logins (our build machine has no login records).'

HOOK = hook('A new developer joins and can read the payroll folder. A database stops after an update because the <code>postgres</code> account was locked. An auditor asks “who logged in at 3 a.m.?”. Every one of these is a question about <b>users and groups</b>. Linux decides everything (who can read a file, who can run a command, who owns a process) from two small numbers: a user ID and group IDs. Today you learn where they live and how to read them.',
    ['explain what a user, a group, a UID and a GID are, and the three kinds of accounts (root, system, normal)',
     'read every field of <code>/etc/passwd</code>, <code>/etc/shadow</code> and <code>/etc/group</code>, and know why shadow is separate',
     'find out who you are and what you can do with <code>id</code>, <code>whoami</code>, <code>groups</code> and <code>getent</code>',
     'see who is logged in and who logged in before with <code>who</code>, <code>w</code>, <code>last</code> and <code>lastlog</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, 'a new joiner, a locked DB'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'Users, groups, UIDs', 6, 'simple meaning + 4 depths'),
    ('types', 'Kinds of accounts', 3, 'root, system, normal'),
    ('commands', 'Each command, by field', 16, 'files and commands, real runs'),
    ('animation', 'See it happen', 4, 'numbers become names'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('Who am I?', 'whoami', 'just the name'),
    ('My UID, GID and all groups', 'id', 'the full identity'),
    ('Another user’s details', 'id NAME  /  getent passwd NAME', 'home, shell, UID'),
    ('Which groups am I in?', 'groups  /  id -Gn', 'access to shared folders'),
    ('Members of a group', 'getent group NAME', 'who is in sudo?'),
    ('All human accounts', "awk -F: '$3>=1000' /etc/passwd", 'UID 1000 and up'),
    ('Password status / expiry', 'sudo passwd -S NAME  /  sudo chage -l NAME', 'locked? expired?'),
    ('Who is logged in now?', 'who  /  w', 'w also shows what they run'),
    ('Who logged in before?', 'last  /  lastlog', 'audits'),
])

cmap = concept_map(
    [('1.6', 'Shell and prompt', 'riya@web01'), ('3.5', 'Viewing files', 'cat, head, grep'), ('6.2', 'cut and sort', 'fields with -d:')],
    ['users, groups, UID and GID', 'root, system and normal accounts', '/etc/passwd, /etc/shadow, /etc/group, /etc/gshadow', 'id, whoami, groups, getent', 'who, w, last, lastlog'],
    [('8.2', 'Managing users', 'useradd, usermod, passwd'), ('8.3', 'Managing groups', 'groupadd, gpasswd'), ('8.4', 'root and sudo', 'sudoers'), ('9.1', 'Permissions', 'rwx for user, group, others')],
    'Every permission check in Linux compares numbers: the UID and GIDs of a process against the owner and group of a file. This lesson shows where those numbers come from.')

# ---------------------------------------------------------------- story
sc = (term(20, 14, 316, 156, ['$ id', ('uid=1000(riya) gid=1000(riya)', 'out'), ('groups=1000(riya),27(sudo)', 'out'), '$ ls -l /srv/payroll', ('Permission denied', 'err'), '$ id aman', ('… groups=…,1005(finance)', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Identity in Linux:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• UID: who you are', '• GID: your main group', '• groups: extra access', '• /etc/passwd: the list', '• /etc/shadow: passwords'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Why can Aman read the payroll folder?</h2>
  <div class="story">
''' + puzzle('Run <code>ls -l /etc/shadow</code> and you see it is readable only by root and the <code>shadow</code> group. But <code>/etc/passwd</code> is readable by everyone, and it is called “passwd”. Are everyone’s passwords public? And if the kernel only stores numbers, how does <code>ls -l</code> print the name <code>riya</code>?') + '''
    <p class="narration">Monday morning at a small company. Riya is the Linux admin; Aman joined last week.</p>
''' + scene('A terminal: id shows riya with UID 1000 and the sudo group; ls on /srv/payroll is denied; id aman shows he is in the finance group.', sc,
            'Access is decided by <tspan font-weight="700" class="s-acc">UID and groups</tspan>.') + '''
K> Aman is in the payroll channel but I am not, and he can open <code>/srv/payroll</code>. Why him?
A> Ask Linux who he is: <code>id aman</code>. He is in the <code>finance</code> group, and the folder belongs to that group. Linux never looks at job titles, only at user and group numbers.
R> Where are those numbers kept?
A> In three plain text files: <code>/etc/passwd</code> (accounts), <code>/etc/shadow</code> (password hashes) and <code>/etc/group</code> (groups). Today: what each line means, how to read them safely, and the commands every admin uses daily.
  </div>
</section>
'''

# ---------------------------------------------------------------- definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="An office building: each person has an employee ID card (UID), belongs to one main department (primary group) and can have extra access badges (supplementary groups); the security desk keeps the list of names (passwd) and a locked safe with password hashes (shadow).">'
       + label_box(14, 20, 140, 110, ['ID card', 'employee no. 1000', '= UID', 'riya'], 'blue', 8.6)
       + label_box(166, 20, 140, 110, ['department', 'main team', '= primary group', 'riya (GID 1000)'], 'green', 8.6)
       + label_box(318, 20, 140, 110, ['extra badges', 'server room,', 'finance floor', '= extra groups'], 'violet', 8.6)
       + label_box(470, 20, 156, 110, ['security desk', 'name list: passwd', 'locked safe:', 'shadow (hashes)'], 'amber', 8.6)
       + t(320, 160, 'Doors (files) check the card number and the badges,', 9.6, 'ink2')
       + t(320, 182, 'never the name printed on it.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Users and groups at four depths', [
    ('v', 'No jargon: an office with ID cards and badges', '      <p>Think of a company building.</p>' + pic + '''
      <ul>
        <li>Each person (user) has an employee number on their ID card: the <b>UID</b>.</li>
        <li>Everyone belongs to one main department (<b>primary group</b>) and may carry extra badges (<b>supplementary groups</b>).</li>
        <li>Doors (files and folders) only check numbers and badges.</li>
      </ul>'''),
    ('b', 'What you will type every day', '''      <ul>
        <li><code>whoami</code>: your user name. <code>id</code>: your UID, GID and every group.</li>
        <li><code>groups</code>: just the group names.</li>
        <li><code>getent passwd riya</code>: one account’s line (works with LDAP too).</li>
        <li><code>who</code> / <code>w</code>: who is logged in now; <code>last</code>: login history.</li>
      </ul>'''),
    ('i', 'The account files and their fields', '''      <ul>
        <li><code>/etc/passwd</code>: <code>name:x:UID:GID:comment:home:shell</code>. The <code>x</code> means “password is in shadow”. Readable by everyone because programs like <code>ls</code> need names.</li>
        <li><code>/etc/shadow</code>: <code>name:hash:lastchange:min:max:warn:inactive:expire:</code>. Readable only by root and the <code>shadow</code> group. <code>!</code> or <code>*</code> instead of a hash means locked or no password.</li>
        <li><code>/etc/group</code>: <code>group:x:GID:members</code>. A user’s primary group is in passwd; extra groups list the user here.</li>
        <li>UID 0 is root; 1–999 are system accounts (services such as www-data, postgres) with shell <code>nologin</code>; 1000+ are people (from <code>/etc/login.defs</code>).</li>
      </ul>'''),
    ('a', 'Behind the screen: the kernel only knows numbers', '''      <ul>
        <li>Every process carries a real and effective UID and GID plus a list of supplementary GIDs (see <code>/proc/self/status</code>). Every inode stores one owner UID and one GID.</li>
        <li>Names are a user-space convenience: <code>ls</code>, <code>id</code> and <code>ps</code> ask the C library, which follows <code>/etc/nsswitch.conf</code> (“files”, then maybe LDAP, SSSD or systemd-userdb) to turn numbers into names. <code>getent</code> uses the same path; <code>cat /etc/passwd</code> does not.</li>
        <li>Group changes take effect at the next login: a running shell keeps the groups it started with (<code>newgrp</code> or log out and back in).</li>
        <li>Hashes in shadow start with an algorithm id: <code>$y$</code> yescrypt (Ubuntu 22.04+), <code>$6$</code> SHA-512. They are salted and one-way; Linux checks a password by hashing what you type and comparing.</li>
        <li>Login records are binary files: <code>/var/run/utmp</code> (now: who, w), <code>/var/log/wtmp</code> (history: last), <code>/var/log/btmp</code> (failed logins: <code>sudo lastb</code>), <code>/var/log/lastlog</code>.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Users, groups, UID and GID</h2>
''' + def_block(
    'A <b>user</b> is an account that can own files and run processes; the kernel identifies it by a number, the <b>UID</b>. A <b>group</b> is a named set of users with its own number, the <b>GID</b>; every user has one primary group and may belong to supplementary groups. Accounts are stored in <code>/etc/passwd</code>, password hashes and ageing rules in <code>/etc/shadow</code>, and groups in <code>/etc/group</code>.',
    'Linux decides who may do what by comparing the UID and GIDs of a process with the owner and group of a file.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('UID', 'User ID: the number the kernel uses for a user. root = 0.'),
    ('GID', 'Group ID: the number of a group.'),
    ('Primary group', 'The group in your passwd line; new files get it.'),
    ('Supplementary group', 'Extra groups listed in /etc/group (sudo, docker…).'),
    ('System account', 'An account for a service (UID 1–999), usually no login.'),
    ('Hash', 'A one-way scrambled form of a password.'),
    ('Shell', 'The program started when the user logs in (/bin/bash, nologin).'),
    ('NSS', 'Name Service Switch: where names are looked up (/etc/nsswitch.conf).'),
]) + '\n' + names('Where the names come from.', [
    ('passwd', 'password', 'Originally held the hashes too (1970s Unix).'),
    ('shadow', 'shadow passwords', 'Hashes moved to a hidden file (1987).'),
    ('id', 'identity', 'Prints UID, GID and groups.'),
    ('whoami', '“who am I?”', 'Your effective user name.'),
    ('getent', 'get entries', 'Reads databases through NSS.'),
    ('w', 'who + what', 'Who is on and what they run.'),
    ('last', 'last logins', 'Reads /var/log/wtmp.'),
    ('gecos', 'GE Comprehensive OS', 'Old name for the comment field.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Me', '<code>id</code>'),
    ('One account', '<code>getent passwd riya</code>'),
    ('Group members', '<code>getent group sudo</code>'),
    ('root', 'UID <b>0</b>'),
    ('People start at', 'UID <b>1000</b>'),
    ('Who is on', '<code>w</code>'),
]) + '\n' + lv + didyou('The account called <code>nobody</code> (UID 65534) owns nothing on purpose. Services that must run with no rights at all, such as some NFS requests, are mapped to it.') + '''
EXAM> “What are the 7 fields of /etc/passwd?” → username : x (password in shadow) : UID : GID : comment (GECOS) : home directory : login shell.
''' + qc('Why is <code>/etc/passwd</code> readable by everyone?', 'Programs such as ls, ps and id must turn UIDs into names. The password hashes are not there: they are in /etc/shadow, readable only by root.') + mistake('“whoami displays the current user ID and username”',
    'whoami prints only the user name (riya). Use <code>id</code> or <code>id -u</code> for the number (1000).',
    'Checked on Ubuntu 24.04: whoami prints the effective user name only, the same as id -un.') + '''
</section>
'''

# ---------------------------------------------------------------- types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Kinds of accounts</span>
  <h2>root, system and normal users; primary and supplementary groups</h2>
''' + table(['', 'root', 'System account', 'Normal (human) user'], [
    ['UID', '0', '1–999 (Ubuntu: 100–999 dynamic)', '1000 and up'],
    ['Example', 'root', 'www-data, postgres, sshd, _apt', 'riya, aman'],
    ['Home', '/root', '/var/www, /var/lib/postgresql, /nonexistent', '/home/NAME'],
    ['Shell', '/bin/bash', 'usually /usr/sbin/nologin', '/bin/bash'],
    ['Can log in?', 'yes (often blocked over SSH)', 'no: runs one service', 'yes'],
    ['Limits', 'none: bypasses permission checks', 'only its own files', 'own files + groups + sudo'],
], minw=560) + table(['', 'Primary group', 'Supplementary groups'], [
    ['How many', 'exactly one', 'zero or more (up to 65536)'],
    ['Stored in', '4th field of /etc/passwd (GID)', 'last field of /etc/group'],
    ['Used for', 'group owner of new files', 'access to shared files, devices, sudo, docker'],
    ['Change with', '<code>usermod -g</code> (Lesson 8.2)', '<code>usermod -aG</code>, <code>gpasswd</code> (Lesson 8.3)'],
], minw=520) + qc('Why does <code>www-data</code> have the shell <code>/usr/sbin/nologin</code>?', 'It only runs the web server. If someone broke the web app, they still could not log in as www-data and get a shell.') + '''
</section>
'''

PASSWD_FIELDS = "grep '^riya:' /etc/passwd | tr ':' '\\n' | nl"

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each file and command explained, then used in every field</h2>
  <p id="commands">Every output below was recorded on our Ubuntu 24.04 build machine (host <code>web01</code>, user <code>riya</code>, UID 1000). Login-history outputs are marked <b>typical</b> because a build machine has no real logins.</p>
''' + cmdcard_u(['seeing every account, its UID, home and shell', 'scripts that list or check users', 'finding service accounts'],
               ['editing by hand (use useradd/usermod or vipw)', 'networked users (LDAP/AD): use getent'])(
    'passwd-file', '/etc/passwd', 'the list of accounts',
    'One line per account, seven fields separated by colons: <code>name:x:UID:GID:comment:home:shell</code>. Readable by everyone.',
    'cat /etc/passwd   ·   getent passwd [NAME]   ·   cut -d: -f1,3,7 /etc/passwd', 'safe',
    [('getent passwd riya', 'one account (files + LDAP)', 'details'),
     ('cut -d: -f1 /etc/passwd', 'all user names', 'lists'),
     ("awk -F: '$3>=1000 && $3<65534' /etc/passwd", 'human accounts only', 'audits'),
     ("awk -F: '$3==0' /etc/passwd", 'every UID 0 account', 'security'),
     ('grep -v nologin /etc/passwd', 'accounts that can log in', 'review'),
     ('wc -l < /etc/passwd', 'how many accounts', 'quick count')],
    dict(cmd="head -3 /etc/passwd\n" + PASSWD_FIELDS, note='The seven fields of riya’s line, numbered: name, x, UID, GID, comment, home, shell.'),
    [('sys', [
        dict(situation='List the people (not services) on a server.', cmd="awk -F: '$3>=1000 && $3<65534 {print $1, $3, $6}' /etc/passwd",
             why='UID 1000+ are human accounts (from /etc/login.defs). 65534 is nobody.'),
        dict(situation='Count accounts by login shell.', cmd="cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn",
             why='Most accounts are nologin services; only a few can log in. (Lesson 6.2.)')]),
     ('sec', [
        dict(situation='Any extra account with UID 0 is a backdoor.', cmd="awk -F: '$3==0 {print \"UID 0:\", $1}' /etc/passwd",
             why='Only root should appear. A second UID 0 account has full power under another name.')]),
     ('dba', [
        dict(situation='Where does the postgres service account live?', cmd='getent passwd postgres',
             why='Home /var/lib/postgresql holds the data; the DBA switches to it with sudo -iu postgres (Lesson 8.4).')]),
     ('web', [
        dict(situation='Which user runs the web server?', cmd="getent passwd www-data | cut -d: -f1,3,6,7",
             why='Web files must be readable by www-data, but never writable unless needed (Lesson 9.1).')]),
    ],
    anat=anatomy([('riya', 'cmd', '1 name'), ('x', 'opt', '2 password in shadow'), ('1000', 'arg', '3 UID'), ('1000', 'arg', '4 GID'), ('Riya Sharma', 'opt', '5 comment'), ('/home/riya', 'arg', '6 home'), ('/bin/bash', 'cmd', '7 shell')], 'riya:x:1000:1000:Riya Sharma:/home/riya:/bin/bash')
) + cmdcard_u(['checking whether a password is set, locked or expired', 'security audits of password ageing'],
               ['viewing it with a normal account (permission denied)', 'copying hashes anywhere'])(
    'shadow', '/etc/shadow', 'password hashes and ageing',
    'One line per account: <code>name:hash:lastchange:min:max:warn:inactive:expire:</code>. Dates are days since 1 January 1970. Only root and the <code>shadow</code> group can read it.',
    'sudo cat /etc/shadow   ·   sudo passwd -S NAME   ·   sudo chage -l NAME', 'safe',
    [('ls -l /etc/shadow', 'who may read it', 'see the protection'),
     ('sudo grep riya /etc/shadow', 'one line (needs root)', 'inspect'),
     ('sudo passwd -S riya', 'status: P set, L locked, NP none', 'quick check'),
     ('sudo chage -l riya', 'ageing in plain English', 'expiry'),
     ('$y$ / $6$', 'yescrypt / SHA-512 hash', 'algorithm'),
     ('! or * in field 2', 'locked / no password login', 'service accounts')],
    dict(cmd="ls -l /etc/passwd /etc/shadow\ncat /etc/shadow; echo \"exit $?\"\nsudo grep '^riya:' /etc/shadow | cut -c1-40", expect='any', note='A normal user cannot read shadow; with sudo you see the start of a yescrypt hash ($y$).'),
    [('sec', [
        dict(situation='Accounts with an empty password field can log in without a password.', cmd="sudo awk -F: '$2==\"\" {print \"NO PASSWORD:\", $1}' /etc/shadow; echo checked",
             why='Should print nothing. Lock such accounts with sudo passwd -l (Lesson 8.2).'),
        dict(situation='Password status of an account.', cmd='sudo passwd -S riya\nsudo passwd -S www-data',
             why='P = usable password, L = locked. Service accounts are locked: nobody can log in as them with a password.')]),
     ('sys', [
        dict(situation='When does riya’s password expire?', cmd='sudo chage -l riya',
             why='99999 days max = never. Companies often set 90 days (Lesson 8.2).')]),
    ]
) + mistake('“/etc/passwd contains the passwords”', 'Since shadow passwords (decades ago) the second field is just <code>x</code>; hashes are in /etc/shadow (root only).',
            'If you ever see a hash in /etc/passwd, that system is badly misconfigured: anyone could copy it and try to crack it offline.') + cmdcard_u(['seeing groups and their members', 'checking who has sudo or docker rights'],
               ['editing by hand (use groupadd/gpasswd, Lesson 8.3)'])(
    'group-file', '/etc/group', 'the list of groups',
    'One line per group: <code>name:x:GID:member1,member2</code>. A user’s primary group usually lists no members: the link is the GID in /etc/passwd.',
    'getent group [NAME]   ·   grep NAME /etc/group', 'safe',
    [('getent group sudo', 'members of sudo', 'who is admin'),
     ('getent group riya', 'riya’s own group', 'primary group'),
     ('grep -w riya /etc/group', 'every group mentioning riya', 'memberships'),
     ('/etc/gshadow', 'group passwords and admins (root only)', 'rare')],
    dict(cmd="getent group sudo riya\ngrep -w riya /etc/group", note='riya’s primary group lists no members; sudo lists her as a supplementary member.'),
    [('sec', [
        dict(situation='Who are the administrators?', cmd="getent group sudo | cut -d: -f4",
             why='Members of sudo (Ubuntu) or wheel (RHEL) can become root. Review this list regularly.')]),
     ('devops', [
        dict(situation='Membership of the docker group is root-equivalent.', cmd="getent group docker || echo 'no docker group on this host'",
             why='Anyone in docker can start a container that mounts / and becomes root. Treat it like sudo.')]),
    ]
) + cmdcard_u(['finding out who you are and which groups you have', 'checking another user before giving access', 'scripts that must (not) run as root'],
               ['parsing ls -l to learn identity'])(
    'id', 'id · whoami · groups · getent', 'who am I?',
    '<code>id</code> prints the UID, primary GID and all groups of a user (you, by default). <code>whoami</code> prints only the effective user name, <code>groups</code> only the group names. <code>getent</code> reads accounts and groups the same way programs do.',
    'id [-u|-g|-G] [-n] [USER]   ·   whoami   ·   groups [USER]   ·   getent passwd|group NAME', 'safe',
    [('id', 'everything about me', 'first check'),
     ('id -u / id -un', 'UID / user name', 'scripts'),
     ('id -Gn', 'all group names', 'memberships'),
     ('id aman', 'another user', 'before granting access'),
     ('whoami', 'effective user name', 'after sudo/su'),
     ('groups', 'group names only', 'quick')],
    dict(cmd="id\nwhoami\nid -u; id -un\ngroups\nid root", note='uid=1000 is riya; groups shows her primary group riya and the extra group sudo. root is UID 0.'),
    [('devops', [
        dict(situation='A setup script must run as root.', cmd="if [ \"$(id -u)\" -ne 0 ]; then echo 'please run with sudo' >&2; exit 1; fi; echo 'running as root'", expect='any',
             why='Compare the number, not the name (the root account could be renamed). Here riya runs it, so it stops.'),
        dict(situation='With sudo the same check passes.', cmd="sudo bash -c 'if [ \"$(id -u)\" -ne 0 ]; then echo no; else echo \"running as $(whoami)\"; fi'",
             why='sudo runs the command with UID 0.')]),
     ('sys', [
        dict(situation='Does the user have access to the group before a ticket is closed?', cmd="id -Gn riya | tr ' ' '\\n' | grep -qx sudo && echo 'riya is in sudo'",
             why='grep -x matches the whole word, so “sudoers” would not count.')]),
     ('qa', [
        dict(situation='Tests that must not run as root (they would hide permission bugs).', cmd="[ \"$(id -u)\" = 0 ] && echo 'refusing to test as root' || echo \"testing as $(id -un)\"",
             why='Running tests as root passes checks real users would fail.')]),
    ]
) + mistake('Added to a group, but <code>id</code> in the open terminal does not show it', 'Log out and back in (or run <code>newgrp GROUP</code> / <code>su - $USER</code>); <code>id NAME</code> reads the files and already shows it.',
            'A process gets its groups when it starts. Your old shell keeps the old list until a new login.') + cmdcard_u(['seeing who is logged in right now and what they run', 'audits: who logged in when, from where', 'checking reboots'],
               ['exact security forensics alone (records can be cleared by root; also check journalctl)'])(
    'who', 'who · w · last · lastlog', 'logins now and before',
    '<code>who</code> lists current sessions; <code>w</code> adds load average, idle time and the command each user runs. <code>last</code> lists past logins and reboots from <code>/var/log/wtmp</code>; <code>sudo lastb</code> lists failed logins; <code>lastlog</code> shows each account’s latest login.',
    'who [-b -q -H -u]   ·   w [USER]   ·   last [-n N] [USER|reboot]   ·   lastlog [-u USER]', 'safe',
    [('who -H', 'sessions with headers', 'who is on'),
     ('who -b', 'last boot time', 'after an outage'),
     ('w', 'who + idle + what', 'before maintenance'),
     ('last -n 5', 'last 5 logins', 'audit'),
     ('last reboot', 'reboot history', 'stability'),
     ('sudo lastb', 'failed logins', 'brute force'),
     ('lastlog', 'latest login per account', 'stale accounts')],
    dict(cmd='who -H\nw -h', rec=(TYP, 'NAME     LINE         TIME             COMMENT\nriya     pts/0        2026-11-11 09:12 (10.0.0.25)\naman     pts/1        2026-11-11 09:40 (10.0.0.31)\nriya     pts/0     10.0.0.25        09:12    0.00s  0.05s  0.00s w -h\naman     pts/1     10.0.0.31        09:40    2:10   0.20s  0.20s vim report.txt'), note='Two SSH sessions; w shows Aman has been idle for 2 minutes inside vim.'),
    [('sys', [
        dict(situation='Before a reboot: is anyone working?', cmd='w', rec=(TYP, ' 09:42:31 up 12 days,  3:04,  2 users,  load average: 0.08, 0.05, 0.01\nUSER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT\nriya     pts/0    10.0.0.25        09:12    0.00s  0.05s  0.00s w\naman     pts/1    10.0.0.31        09:40    2:10   0.20s  0.20s vim report.txt'),
             why='Warn Aman (wall “reboot in 10 min”) before you restart (Lesson 17.5).')]),
     ('sec', [
        dict(situation='Who logged in at night?', cmd='last -n 4', rec=(TYP, 'aman     pts/1        10.0.0.31        Wed Nov 11 09:40   still logged in\nriya     pts/0        10.0.0.25        Wed Nov 11 09:12   still logged in\ndeploy   pts/0        203.0.113.9      Tue Nov 10 03:02 - 03:05  (00:02)\nreboot   system boot  6.8.0-45-generic Thu Oct 29 06:38   still running\n\nwtmp begins Thu Oct  1 00:00:01 2026'),
             why='A 03:02 login from an outside address (203.0.113.9) for the deploy account deserves a look: was it a scheduled job?'),
        dict(situation='Failed login attempts (password guessing).', cmd='sudo lastb -n 3', rec=(TYP, 'admin    ssh:notty    198.51.100.7     Wed Nov 11 04:11 - 04:11  (00:00)\nadmin    ssh:notty    198.51.100.7     Wed Nov 11 04:11 - 04:11  (00:00)\noracle   ssh:notty    198.51.100.7     Wed Nov 11 04:10 - 04:10  (00:00)'),
             why='Many attempts from one IP with guessed names: block it (fail2ban) and disable password SSH (Lesson 16.6).')]),
     ('devops', [
        dict(situation='When was this host last booted?', cmd='who -b', rec=(TYP, '         system boot  2026-10-29 06:38'),
             why='Quick check after an alert: did the server restart?')]),
    ]
) + undo('These commands only read. The danger is editing the account files by hand.', [
    ('Broke /etc/passwd with an editor:', 'Ubuntu keeps backups: <code>/etc/passwd-</code>, <code>/etc/shadow-</code>, <code>/etc/group-</code>. Check with <code>sudo pwck</code> and <code>sudo grpck</code>.'),
    ('Need to edit safely:', '<code>sudo vipw</code> / <code>sudo vigr</code> lock the file and check it; better, use useradd/usermod (Lesson 8.2).'),
    ('Removed yourself from sudo:', 'Use another admin, or recovery mode (Lesson 17.1), then <code>usermod -aG sudo NAME</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='cat /etc/shadow', meaning='A normal user may not read password hashes.', fix='Use <code>sudo</code>, or <code>sudo passwd -S NAME</code> to see only the status.'),
    dict(cmd='id priya', meaning='No such account in passwd (or LDAP).', fix='Check the spelling with <code>getent passwd | cut -d: -f1</code>.'),
    dict(cmd='getent group hr', meaning='Prints nothing, exit 2: the group does not exist.', fix='Create it with <code>sudo groupadd hr</code> (Lesson 8.3).'),
]) + qc('Which file would you check to see whether an account is locked, and which command shows it without printing the hash?', '/etc/shadow; <code>sudo passwd -S NAME</code> (L = locked).') + '''
'''

SCREENS = screens_block('Real terminal screens: the same name, two identities', 'whoami and id change when you use sudo: the command runs as root.',
    "printf '%s\\n' 'PS1=\"riya@web01:~$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'whoami; id -u' Enter", ' after <code>whoami; id -u</code>: riya, 1000.'),
    ('Enter', "'sudo whoami; sudo id -u' Enter", ' after <code>sudo whoami; sudo id -u</code>: root, 0.'),
], 72, 8, hid='screens', what='bash')

HOOD = hood('Under the hood: id reads the account files', 'strace shows that id gets your numbers from the kernel, then opens <code>/etc/nsswitch.conf</code>, <code>/etc/passwd</code> and <code>/etc/group</code> only to print names.',
    'id', show='nsswitch|passwd|group', trace='openat', explain='<p>The numbers come from the process itself; the files only supply names. If you deleted riya’s line from /etc/passwd, <code>id</code> would still print <code>uid=1000</code>, just without “(riya)”.</p>')

cards = cards + SCREENS + HOOD + '</section>\n'

# ---------------------------------------------------------------- animations
def lookup(k, note, tone):
    o = label_box(14, 14, 100, 60, ['inode', 'report.txt', 'owner 1000'], 'blue' if k >= 0 else 'card', 8)
    o += arrow(116, 44, 132, 44)
    o += label_box(134, 14, 100, 60, ['C library', 'nsswitch.conf', '“files”'], 'amber' if k >= 1 else 'card', 8)
    o += arrow(236, 44, 252, 44)
    o += label_box(254, 14, 92, 60, ['/etc/passwd', '…:1000:…', '→ riya'], 'green' if k >= 2 else 'card', 8)
    if k >= 3:
        o += label_box(80, 88, 200, 34, ['-rw-r--r-- 1 riya riya … report.txt'], 'green', 7.6)
    return o + t(180, 140, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ ls -l report.txt'] + ([('-rw-r--r-- 1 riya riya 12 report.txt', 'out')] if k == 3 else []), title='riya@web01', prompt='riya@web01:~$', size=8) + cap(c, '', 'card', y=150, h=34)
       for k, c in enumerate(['You ask ls for details…', '…ls asks the C library for a name…', '…which reads passwd…', '…and prints riya.'])]
behind = [lookup(0, 'The disk only stores the number 1000.', 'violet'), lookup(1, 'nsswitch.conf says: look in files.', 'violet'),
          lookup(2, 'Line with UID 1000 → name riya.', 'violet'), lookup(3, 'Name printed. Permission checks still use 1000.', 'green')]
two = anim_two('Numbers become names', 'Behind the screen: from UID to name',
               'A terminal running ls -l report.txt.',
               'An inode storing owner 1000, the C library reading nsswitch.conf, then /etc/passwd turning 1000 into riya.', see, behind,
               ['ls needs the owner.', 'Names are not on the disk.', 'Lookup.', 'Done.'],
               ['1. inode: owner UID 1000', '2. NSS decides where to look', '3. /etc/passwd maps 1000 → riya', '4. Output shows the name'])

def login(k, note, tone):
    boxes = [('you type', 'password'), ('hash it', 'with salt'), ('shadow', 'stored hash'), ('match?', 'start shell')]
    o = ''
    for i, (a, b) in enumerate(boxes):
        tn = 'card'
        if i <= k:
            tn = 'green' if i == 3 and k == 3 else 'amber'
        o += label_box(14 + i * 86, 30, 78, 56, [a, b], tn, 8)
        if i < 3:
            o += arrow(92 + i * 86, 58, 100 + i * 86, 58)
    return o + t(180, 130, note, 8.6, tone, bold=True)
frames = [login(0, 'You type Lab@2026; it is never stored.', 'violet'), login(1, 'Linux hashes it with the salt from shadow.', 'amber'),
          login(2, 'It reads the stored $y$… hash for riya.', 'amber'), login(3, 'Same hash → shell /bin/bash starts as UID 1000.', 'green')]
s1 = anim_one('Animated example', 'How a password is checked',
              'Linux never stores your password, only a salted hash.',
              'login check', 'Four boxes: typed password, hashing with salt, stored hash from shadow, comparison then shell start.', frames,
              ['The password stays in memory only.', 'Same password + same salt = same hash.', 'shadow is read as root by the login program.', 'Then the shell from passwd starts.'], hid='scenario-login')

dx = dissect('Layer by layer: where an identity comes from',
    'From the account files to a running process. Each layer has a real command and output from our build machine.', [
    dict(key='passwd', name='/etc/passwd', sub='accounts',
         why='Names, UIDs, homes, shells.', how='Read by everyone.', impl='7 colon fields.', used='ls, id, login.',
         cmd="getent passwd riya"),
    dict(key='group', name='/etc/group', sub='groups',
         why='Extra access.', how='Members listed per group.', impl='4 colon fields.', used='id, newgrp.',
         cmd="grep -w riya /etc/group"),
    dict(key='nss', name='NSS', sub='/etc/nsswitch.conf',
         why='Lets LDAP/AD users work like local ones.', how='files, systemd, sss…', impl='glibc.', used='getent, every program.',
         cmd="grep -E '^(passwd|group|shadow):' /etc/nsswitch.conf"),
    dict(key='proc', name='Process identity', sub='/proc/self/status',
         why='What the kernel checks.', how='Real/effective UID, GID, groups.', impl='Set at login, inherited by children.', used='Every permission check.',
         cmd="grep -E '^(Uid|Gid|Groups):' /proc/self/status"),
], hint='From files to the kernel. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How numbers become names, and how a password is checked</h2>
''' + two + s1 + dx + qc('You delete user aman but his files remain. What will <code>ls -l</code> show as their owner?', 'The bare number (e.g. 1005), because no passwd line maps it to a name any more. find -nouser finds such files (Lesson 7.1).') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Users and groups at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['id aman', 'groups'], 'blue', 8.6),
              '1. Access tickets', 'Help desks check a user’s groups before granting or removing access to shared folders.', ['Ticket', '*id', 'grant']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['UID 0?', 'empty pw?'], 'red', 8.6), '2. Security audits',
    'Auditors look for extra UID 0 accounts, empty passwords and stale accounts.', ['Audit', '*awk passwd', 'fix']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['postgres', 'nologin'], 'green', 8.6), '3. Service accounts',
    'Databases and web servers run as their own locked accounts, so a break-in stays contained.', ['Service', '*own user', 'contained']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['last', 'lastb'], 'amber', 8.6), '4. Incident response',
    'After an alert, admins check who logged in, from where and whether logins failed.', ['Alert', '*last', 'timeline']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['id -u = 0?', 'scripts'], 'violet', 8.6), '5. Safe scripts',
    'Installers check they run as root; tests check they do not.', ['Start', '*id -u', 'go / stop']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Just my UID', scenario='For a script.', cmd='id -u', explain='1000.'),
    dict(level='b', title='User names only', scenario='First 5 accounts.', cmd='cut -d: -f1 /etc/passwd | head -5', explain='Field 1 (Lesson 6.2).'),
    dict(level='i', title='Accounts that can log in', scenario='Shells that are not nologin or false.', cmd="grep -Ev 'nologin|false|sync$' /etc/passwd | cut -d: -f1", explain='grep -v.'),
    dict(level='i', title='Home folders that exist', scenario='Check every human account’s home.', cmd="awk -F: '$3>=1000 && $3<65534 {print $6}' /etc/passwd | xargs ls -ld", explain='awk + xargs.'),
    dict(level='a', title='Group count per user', scenario='How many groups each human is in.', cmd="for u in $(awk -F: '$3>=1000 && $3<65534 {print $1}' /etc/passwd); do echo \"$u $(id -G \"$u\" | wc -w)\"; done", explain='id -G + wc -w.'),
], extra=build_up('the payroll access check', 'Riya checks why Aman can open the payroll folder (built with a finance group).', "sudo groupadd -f finance; id aman >/dev/null 2>&1 || sudo useradd -m -G finance aman; sudo mkdir -p /srv/payroll; sudo chgrp finance /srv/payroll; sudo chmod 770 /srv/payroll", [
    ("ls -ld /srv/payroll", '1. The folder belongs to the finance group.'),
    ("id aman", '2. Aman is in finance.'),
    ("id -Gn riya", '3. Riya is not.'),
    ("getent group finance", '4. The group’s member list.'),
])) + which('Choosing the right command.', [
    ('Who am I', 'id', 'All numbers and groups.', 'whoami (name only).'),
    ('One account', 'getent passwd NAME', 'Works with LDAP.', 'grep (files only).'),
    ('Group members', 'getent group NAME', 'Real list.', 'Guessing.'),
    ('Password state', 'sudo passwd -S', 'No hash shown.', 'cat /etc/shadow.'),
    ('Who is on now', 'w', 'Includes activity.', 'ps alone.'),
    ('Login history', 'last / lastb', 'wtmp/btmp.', 'Memory.'),
    ('Edit accounts', 'useradd / usermod (8.2)', 'Checked, locked.', 'nano /etc/passwd.'),
]) + keys('Handy forms.', [
    ('id -un', 'user name (like whoami)', 'id -un'),
    ('id -Gn USER', 'group names', 'id -Gn aman'),
    ('getent passwd | wc -l', 'number of accounts', 'audits'),
    ('who -b', 'boot time', 'after outages'),
    ('last -n 5', 'recent logins', 'audits'),
    ('sudo lastb -n 5', 'failed logins', 'security'),
]) + scriptit('user-report.sh', 'A small audit report: human accounts with their UID, groups and shell, plus a warning for any extra UID 0 account.',
'''echo "USER      UID   SHELL       GROUPS"
awk -F: '$3>=1000 && $3<65534 {print $1, $3, $7}' /etc/passwd | while read -r u uid sh; do
  printf '%-9s %-5s %-11s %s\\n' "$u" "$uid" "$sh" "$(id -Gn "$u" | tr ' ' ',')"
done
extra=$(awk -F: '$3==0 && $1!="root" {print $1}' /etc/passwd)
[ -n "$extra" ] && echo "WARNING: extra UID 0 accounts: $extra" || echo "OK: only root has UID 0"''',
'<p>On a real server this lists every person and flags backdoor accounts.</p>') + puzzle_answer('No: the second field of /etc/passwd is just <code>x</code>; the hashes are in /etc/shadow, which only root can read. And <code>ls -l</code> prints names because it looks the owner UID (1000) up in /etc/passwd through NSS: the disk only stores the number.') + qc('Which field of /etc/passwd tells you whether an account can log in?', 'Field 7, the shell: /usr/sbin/nologin or /bin/false means no interactive login.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../06-text-processing/02-sort-uniq-wc-cut-paste-and-tr/">Lesson 6.2</a> (cut, sort, uniq) and <a href="../../01-start-here/06-terminal-console-shell-and-prompt-your-first/">1.6</a> (the prompt).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
