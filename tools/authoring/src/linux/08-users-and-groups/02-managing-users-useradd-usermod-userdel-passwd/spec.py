import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='08-users-and-groups', lesson='02-managing-users-useradd-usermod-userdel-passwd', n='8.2',
    module_label='Module 8 · Users, groups and sudo',
    title='Managing users: useradd, usermod, userdel, passwd and chage',
    desc='Create accounts with useradd (-m -s -c -u -g -G -d -e -r) and adduser, set and lock passwords with passwd and chpasswd, password ageing with chage, change accounts with usermod (-s -c -l -d -m -L -U -e -aG), and remove them with userdel and userdel -r. Defaults, /etc/skel, lock vs expire vs delete, and safe on- and offboarding, with real outputs.',
    og_desc='Create, change, lock and remove Linux user accounts the right way with useradd, passwd, chage, usermod and userdel.',
    minutes=42, level='Beginner → Advanced',
    lead='Every new joiner and every leaver means user management. This lesson explains useradd, passwd, chage, usermod and userdel, their defaults and traps, and how admins, DevOps, security and testers onboard and offboard safely.',
    chips=['Onboard and offboard safely', 'Lock vs expire vs delete', 'Errors decoded', 'Practice lab with checker', 'Real outputs'],
)

MAIN = """# Where do useradd's defaults come from?
cat /etc/default/useradd | grep -v '^#' | grep .
ls -A /etc/skel
grep -E '^(UID_MIN|UID_MAX|PASS_MAX_DAYS|ENCRYPT_METHOD)' /etc/login.defs
getent passwd root | cut -d: -f7
"""

RUN = dict(
    heading='The defaults behind useradd',
    intro='<p>Creating users needs root, so here you inspect what useradd would do. The real commands are in the cards above and in the lab.</p>',
    code=MAIN,
    anno=[
        ("cat /etc/default/useradd | grep -v '^#' | grep .", 'SHELL=/bin/sh: why you pass -s /bin/bash.'),
        ('ls -A /etc/skel', 'Copied into every new home with -m.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is the default shell?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what is the first UID given to people? Then run.',
             code="awk '/^UID_MIN/ {print $2}' /etc/login.defs\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should print only the SHELL line.',
             code="grep shell /etc/default/useradd\n"),
        dict(label='4 · Your turn', hint='Print how many days a password is valid by default (PASS_MAX_DAYS).',
             code="awk '/^PASS_MAX_DAYS/ {print $2}' /etc/login.defs\n"),
        dict(label='5 · Challenge', hint='Compute the date 90 days from today (for chage -E).',
             code="date -d '+90 days' +%F\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: a full joiner and leaver',
    intro='<p>Use a test name. Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine.</p>',
    items=[
        dict(title='1 · Create', cmd='sudo useradd -m -s /bin/bash -c "Test User" testuser && getent passwd testuser', output=pc('sudo userdel -r testuser >/dev/null 2>&1; sudo useradd -m -s /bin/bash -c "Test User" testuser && getent passwd testuser'), note='Recorded (UID differs on your PC).'),
        dict(title='2 · Password, change at first login', cmd='sudo passwd testuser; sudo chage -d 0 testuser', output='New password: \nRetype new password: \npasswd: password updated successfully', note='Typical: nothing is shown while you type.'),
        dict(title='3 · Log in as the new user', cmd='su - testuser', output='Password: \nYou are required to change your password immediately (administrator enforced).\nCurrent password: \nNew password: ', note='Typical: the forced change.'),
        dict(title='4 · Disable', cmd='sudo usermod -L -e 1 testuser && sudo passwd -S testuser', output=pc('sudo usermod -L -e 1 testuser && sudo passwd -S testuser'), note='Recorded.'),
        dict(title='5 · Remove', cmd='sudo userdel -r testuser', output=pc('sudo userdel -r testuser 2>&1'), note='Recorded: the mail-spool message is a harmless warning.'),
    ],
)

TRACE = dict(
    heading='Checking an account before creating it',
    intro='<p>Step through a script that only creates the account if it does not exist.</p>',
    code='''u=root
if getent passwd "$u" > /dev/null; then msg="exists"; else msg="would create"; fi
echo "$u: $msg"
u=neha2026
if getent passwd "$u" > /dev/null; then msg="exists"; else msg="safe to create"; fi
echo "$u: $msg"
''',
    notes={1: 'Name.', 2: 'Check :: getent exits 0 if found.', 3: 'root exists.', 6: 'Not found :: getent exits 2, so it is safe to create.'},
)

WORKED_INTRO = 'Three tasks from real jobs, all recorded with sudo: onboarding, a service account and offboarding.'
EXAMPLES = [
    dict(level='b', tag='Help desk', title='Create a person properly',
         problem='<p>Create karan with home, bash, full name and a temporary password he must change.</p>',
         inp='nothing yet', approach=['useradd -m -s -c.', 'chpasswd, chage -d 0.'],
         code='''sudo userdel -r karan > /dev/null 2>&1
sudo useradd -m -s /bin/bash -c "Karan Shah" karan
echo 'karan:Tmp#4321' | sudo chpasswd
sudo chage -d 0 karan
getent passwd karan; sudo chage -l karan | head -1
''', notes={2: 'Create.', 3: 'Temporary password.', 4: 'Force change :: then check.'}, tryit='Add -e for an end date.'),
    dict(level='i', tag='DevOps', title='Service account for an app',
         problem='<p>Create a system account “reports” with no login and its own data folder.</p>',
         inp='nothing yet', approach=['useradd -r -s nologin -d.', 'mkdir + chown.'],
         code='''sudo userdel reports > /dev/null 2>&1; sudo rm -rf /srv/reports
sudo useradd -r -s /usr/sbin/nologin -d /srv/reports -c "Reports service" reports
sudo mkdir /srv/reports && sudo chown reports: /srv/reports
getent passwd reports; ls -ld /srv/reports
sudo userdel reports; sudo rm -rf /srv/reports
''', notes={2: 'System UID :: below 1000.', 3: 'Data folder owned by the service.', 4: 'Check.'}, tryit='Try sudo -u reports touch /srv/reports/x.'),
    dict(level='a', tag='Security', title='Offboard without losing data',
         problem='<p>Disable karan now, archive his home, then remove the account.</p>',
         inp='karan from example 1', approach=['usermod -L -e 1.', 'tar, then userdel -r.'],
         code='''sudo useradd -m -s /bin/bash karan 2>/dev/null; sudo -u karan touch /home/karan/handover.txt
sudo usermod -L -e 1 -s /usr/sbin/nologin karan
sudo tar czf /tmp/karan_home.tgz -C /home karan && tar tzf /tmp/karan_home.tgz
sudo userdel -r karan 2>/dev/null; id karan 2>&1 || echo 'karan removed'
''', notes={2: 'Disable everything.', 3: 'Archive :: listed.', 4: 'Removed.'}, tryit='Restore with sudo tar xzf -C /home.'),
]

QUIZ = mix([
    dict(q='Which option of useradd creates the home folder?', options=['-h', '-m', '-d', '-c'], answer=1, why='-d only sets the path.'),
    dict(q='On Ubuntu, what shell does useradd give without -s?', options=['/bin/bash', '/bin/sh', '/bin/zsh', 'nologin'], answer=1, why='useradd -D shows SHELL=/bin/sh.'),
    dict(q='Which forces a password change at next login?', options=['chage -d 0', 'passwd -l', 'usermod -L', 'chage -M 0'], answer=0, why='Last change = day 0.'),
    dict(q='usermod -G docker riya does what to riya’s other groups?', options=['keeps them', 'removes them', 'doubles them', 'nothing'], answer=1, why='Use -aG.'),
    dict(q='Which removes the account and its home folder?', options=['userdel', 'userdel -r', 'userdel -f', 'deluser -k'], answer=1, why='-r = remove home and mail.'),
    dict(q='After passwd -l, a user still logs in with an SSH key. Why?', options=['bug', 'locking only disables the password', 'keys bypass PAM', 'sudo needed'], answer=1, why='Also expire or set nologin.'),
    dict(q='Which file’s contents are copied into new homes?', options=['/etc/default/useradd', '/etc/skel', '/etc/login.defs', '/etc/profile'], answer=1, why='The skeleton.'),
    dict(q='Safest way to set passwords for many users in a script?', options=['useradd -p plain', 'chpasswd from a protected file', 'echo into /etc/shadow', 'passwd in a loop with arguments'], answer=1, why='Not on the command line.'),
])

REVISION = [
    '<code>sudo useradd -m -s /bin/bash -c "Name" NAME</code>; then <code>sudo passwd NAME</code>. Defaults: <code>useradd -D</code>, /etc/login.defs, /etc/skel.',
    'Other options: <code>-u UID</code>, <code>-g</code> primary, <code>-G a,b</code> extra (must exist), <code>-d</code> home, <code>-e DATE</code>, <code>-r</code> system.',
    '<code>adduser</code>: interactive, bash + home by default (Debian/Ubuntu).',
    '<code>passwd -S -l -u -e</code>; <code>chpasswd</code> for many; never passwords on the command line.',
    '<code>chage -l -d 0 -M -m -W -I -E</code>.',
    '<code>usermod -s -c -l -d -m -L -U -e -aG</code>. <b>-G without -a removes other groups.</b>',
    'Leavers: lock + expire + nologin, back up, hand over, then <code>userdel -r</code>. Check <code>find -nouser</code>.',
]

FAQ = [
    ('How do I create a user with a home directory?', 'sudo useradd -m -s /bin/bash NAME (or sudo adduser NAME on Ubuntu), then sudo passwd NAME.'),
    ('What is the difference between useradd and adduser?', 'useradd is the low-level tool (needs options); adduser on Debian/Ubuntu is an interactive wrapper with friendly defaults.'),
    ('How do I lock a user account?', 'sudo usermod -L NAME (password only); add -e 1 to block SSH keys too.'),
    ('How do I force a user to change password at next login?', 'sudo chage -d 0 NAME (or sudo passwd -e NAME).'),
    ('How do I delete a user and their home?', 'sudo userdel -r NAME, after backing up anything needed.'),
    ('How do I change a user’s shell?', 'sudo usermod -s /bin/bash NAME (or chsh for your own).'),
    ('How do I rename a user?', 'sudo usermod -l NEW -d /home/NEW -m OLD (and groupmod -n NEW OLD for the group).'),
]

PRACTICE_INTRO = 'Small account tasks (with sudo). Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Default shell', stmt='Print only the default shell of useradd.', inp='useradd -D', code="sudo useradd -D | grep SHELL\n", explain='SHELL=/bin/sh.'),
    dict(level='easy', title='Skeleton', stmt='List the files in /etc/skel.', inp='/etc/skel', code="ls -A /etc/skel\n", explain='Hidden files: -A.'),
    dict(level='easy', title='Password status', stmt='Show riya’s password status.', inp='riya', code="sudo passwd -S riya | cut -d' ' -f1,2\n", explain='P = set.'),
    dict(level='medium', title='Create and check', stmt='Create test1 with home and bash and show its passwd line.', inp='nothing',
         code="sudo userdel -r test1 > /dev/null 2>&1\nsudo useradd -m -s /bin/bash test1\ngetent passwd test1 | cut -d: -f1,6,7\nsudo userdel -r test1 2>/dev/null\n", explain='-m -s.'),
    dict(level='medium', title='Expiry date', stmt='Give test2 an account end date and show it.', inp='nothing',
         code="sudo userdel -r test2 > /dev/null 2>&1; sudo useradd -m test2\nsudo chage -E 2026-12-31 test2\nsudo chage -l test2 | grep 'Account expires'\nsudo userdel -r test2 2>/dev/null\n", explain='-E.'),
    dict(level='medium', title='Lock', stmt='Set a password, lock it, show the status letter.', inp='nothing',
         code="sudo userdel -r test3 > /dev/null 2>&1; sudo useradd -m test3\necho 'test3:Ab#12345' | sudo chpasswd; sudo usermod -L test3\nsudo passwd -S test3 | cut -d' ' -f2\nsudo userdel -r test3 2>/dev/null\n", explain='L.'),
    dict(level='business', title='Fix /bin/sh users', stmt='Create test4 without -s, then fix its shell.', inp='nothing',
         code="sudo userdel -r test4 > /dev/null 2>&1; sudo useradd -m test4\ngetent passwd test4 | cut -d: -f7\nsudo usermod -s /bin/bash test4; getent passwd test4 | cut -d: -f7\nsudo userdel -r test4 2>/dev/null\n", explain='usermod -s.'),
    dict(level='business', title='Rename', stmt='Rename test5 to test6 and move the home.', inp='nothing',
         code="for u in test5 test6; do sudo userdel -r $u > /dev/null 2>&1; sudo groupdel $u > /dev/null 2>&1; done; sudo useradd -m test5\nsudo usermod -l test6 -d /home/test6 -m test5\ngetent passwd test6 | cut -d: -f1,6; ls -d /home/test6\nsudo userdel -r test6 2>/dev/null\n", explain='-l -d -m.'),
]

SCN_INTRO = 'Interview questions about managing users, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Create a user with a home directory and set a password.”', 'The classic first task.', 'do you know -m and passwd?',
        '''<ul>
          <li><code>sudo useradd -m -s /bin/bash NAME</code> then <code>sudo passwd NAME</code>.</li>
          <li>Or <code>sudo adduser NAME</code> on Ubuntu.</li>
          <li>Check with <code>id NAME</code>.</li>
        </ul>''', 'useradd NAME without -m, and no password.') +
    scn('Help desk', 'Junior', '“The new user’s terminal shows ^[[A and has no tab completion”', 'The account was created with useradd on Ubuntu.', 'do you know the default shell?',
        '''<ol>
          <li><code>getent passwd NAME</code>: shell is /bin/sh.</li>
          <li><code>sudo usermod -s /bin/bash NAME</code>.</li>
          <li>Fix the default: <code>sudo useradd -D -s /bin/bash</code>.</li>
        </ol>''', 'reinstalling bash.') +
    scn('Security team', 'Mid-level', 'An employee was fired this morning', 'HR asks for access to be removed now; legal wants the files kept.', 'can you disable without destroying?',
        '''<ul>
          <li><code>usermod -L -e 1 -s /usr/sbin/nologin</code>; remove authorized_keys; kill sessions (<code>pkill -u</code>).</li>
          <li>Remove from sudo and other groups; rotate shared secrets they knew.</li>
          <li>Archive the home; delete only after approval.</li>
        </ul>''', 'userdel -r immediately.') +
    scn('Platform', 'Senior', '200 servers, consistent accounts', 'Users have different UIDs on different servers and NFS ownership is wrong.', 'do you know central identity and automation?',
        '''<ul>
          <li>Central directory (LDAP/FreeIPA/AD via SSSD), or Ansible with fixed UIDs.</li>
          <li>Never create humans by hand on servers; audit drift.</li>
          <li>Fix ownership with find -uid / chown after renumbering.</li>
        </ul>''', 'a shell script that runs useradd on each host by hand.')
) + interview([
    ('What does useradd -r do?', 'Creates a system account (UID below 1000, no home by default).'),
    ('How do you lock and unlock an account?', 'usermod -L / -U, or passwd -l / -u.'),
    ('What does chage -M 90 do?', 'Password must be changed every 90 days.'),
    ('Where are useradd defaults?', '/etc/default/useradd (useradd -D) and /etc/login.defs.'),
    ('What does userdel leave behind?', 'Files outside the home owned by the old UID; cron jobs and mail unless removed.'),
    ('How do you add a user to a group without removing others?', 'usermod -aG GROUP USER.'),
    ('How do you set a password non-interactively?', 'echo "user:pass" | chpasswd (from a protected source).'),
], [
    ('RHCSA (EX200)', '“Create, delete, and modify local user accounts”, “Change passwords and adjust password aging”.'),
    ('LFCS', 'Create and manage users, password policies.'),
    ('CompTIA Linux+', 'useradd, usermod, userdel, passwd, chage.'),
]) + distro('The tools are the same; defaults differ.', [
    ('useradd default shell', '/bin/sh', '/bin/bash', '- (sysadminctl / dscl)', '-'),
    ('useradd creates home', 'no (needs -m)', 'yes (CREATE_HOME yes)', '-', '-'),
    ('adduser', 'interactive Perl tool', 'link to useradd', '-', '-'),
    ('Admin group for -G', 'sudo', 'wheel', 'admin', '-'),
    ('Password ageing', 'chage', 'chage', 'pwpolicy', '-'),
]) + teaser('8.3', 'Neha and Aman both need to edit files in /srv/projects, but Riya must not. Making a group is easy; adding people without accidentally removing their other groups is where one missing letter (-a) causes outages. Next: groupadd, gpasswd and usermod -aG.')

CHEATSHEET = cheatsheet('Managing users', [
    ('Create', [('useradd -m -s /bin/bash -c "N" u', 'person'), ('useradd -r -s /usr/sbin/nologin u', 'service'), ('-u -g -G -d -e', 'UID, groups, home, end'), ('adduser u', 'friendly (Ubuntu)'), ('useradd -D', 'defaults')]),
    ('Passwords', [('passwd u', 'set'), ("echo 'u:p' | chpasswd", 'bulk'), ('passwd -S u', 'status'), ('passwd -l / -u', 'lock / unlock'), ('chage -d 0 u', 'change at login')]),
    ('Ageing', [('chage -l u', 'show'), ('chage -M 90', 'max days'), ('chage -W 7', 'warning'), ('chage -I 14', 'inactive'), ('chage -E DATE / -1', 'account end')]),
    ('Change & remove', [('usermod -s / -c', 'shell / comment'), ('usermod -l new -d /home/new -m old', 'rename'), ('usermod -L -e 1', 'disable'), ('usermod -aG g u', 'add group'), ('userdel -r u', 'remove + home')]),
])

MINDMAP = mindmap('Managing users', [
    ('useradd', 'blue', ['-m -s -c', '-u -G -d -e', '-r service']),
    ('Defaults', 'green', ['useradd -D', 'login.defs', '/etc/skel']),
    ('passwd', 'amber', ['set / chpasswd', '-S -l -u', '-e expire']),
    ('chage', 'violet', ['-d 0', '-M -W -I', '-E end date']),
    ('usermod', 'acc', ['-s -c -l', '-L -U -e', '-aG (not -G)']),
    ('userdel', 'red', ['-r home', 'orphan files', 'lock first']),
])

LAB = lab('onboard and offboard', 'Build the lab, do the four tasks in your own terminal (sudo needed), then run the checker.',
    setup='''sudo userdel -r labuser > /dev/null 2>&1; sudo userdel -r labold > /dev/null 2>&1
sudo useradd -m -s /bin/bash labold; echo 'labold:Old#2026x' | sudo chpasswd''',
    tasks=['Create <code>labuser</code> with a home folder, the shell <code>/bin/bash</code> and the comment <code>Lab User</code>.',
           'Give labuser the password <code>Lab#2026x</code> and force a change at first login.',
           'Make labuser’s account expire on <code>2026-12-31</code>.',
           'Disable <code>labold</code> completely (lock and expire) without deleting it.'],
    solution='''sudo useradd -m -s /bin/bash -c "Lab User" labuser
echo 'labuser:Lab#2026x' | sudo chpasswd; sudo chage -d 0 labuser
sudo chage -E 2026-12-31 labuser
sudo usermod -L -e 1 labold''',
    check='''ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 account"  '[ "$(getent passwd labuser | cut -d: -f5,7)" = "Lab User:/bin/bash" ] && [ -d /home/labuser ]'
ok "2 password" '[ "$(sudo passwd -S labuser | cut -d" " -f2)" = P ] && sudo chage -l labuser | grep -q "must be changed"'
ok "3 expiry"   'sudo chage -l labuser | grep -q "Account expires.*Dec 31, 2026"'
ok "4 disabled" '[ "$(sudo passwd -S labold | cut -d" " -f2)" = L ] && ! sudo chage -l labold | grep -q "Account expires.*never"' ''')
