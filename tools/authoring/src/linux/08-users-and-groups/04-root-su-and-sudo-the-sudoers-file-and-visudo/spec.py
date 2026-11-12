import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='08-users-and-groups', lesson='04-root-su-and-sudo-the-sudoers-file-and-visudo', n='8.4',
    module_label='Module 8 · Users, groups and sudo',
    title='root, su and sudo: the sudoers file and visudo',
    desc='What root (UID 0) is and why direct root logins are avoided; su, su - and su -c; sudo, sudo -i, -s, -u, -l, -k, -n, -E and sudoedit; sudo with redirection (sudo tee); sudoers rule syntax with groups, run-as users, NOPASSWD, aliases and /etc/sudoers.d; visudo and visudo -c; SUID, PAM and sudo logs, animated with real outputs.',
    og_desc='Use sudo and su correctly, write sudoers rules that give exactly one command, and edit them safely with visudo, with real outputs.',
    minutes=42, level='Beginner → Advanced',
    lead='Servers avoid root logins: named people run single, logged commands with sudo instead. This lesson explains root, su and sudo, how to read and write sudoers rules, how visudo prevents lock-outs, and how admins, DBAs, DevOps and security teams use them.',
    chips=['su vs sudo', 'Least-privilege rules', 'How sudo decides (animated)', 'Practice lab with checker', 'Real outputs'],
)

MAIN = """# Who am I, and could I become root?
id -u; id -un
ls -l /usr/bin/sudo /usr/bin/su
getent group sudo
ls -l /etc/sudoers
cat /etc/shadow > /dev/null 2>&1 || echo "cannot read /etc/shadow as $(id -un)"
"""

RUN = dict(
    heading='root, SUID programs and the sudo group',
    intro='<p>Inspect the pieces sudo relies on. Real sudo commands are in the cards above and in the lab.</p>',
    code=MAIN,
    anno=[('ls -l /usr/bin/sudo /usr/bin/su', 'The s in rwsr-xr-x: SUID root.'), ('cat /etc/shadow > /dev/null 2>&1 || echo "cannot read /etc/shadow as $(id -un)"', 'Denied without root.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Who may use sudo?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what UID does root have? Then run.', code="id -u root\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this root check uses the name. Compare the UID instead.', code="[ \"$(whoami)\" = root ] && echo root || echo \"not root\"\n"),
        dict(label='4 · Your turn', hint='Print the permission string of /usr/bin/passwd (also SUID).', code="ls -l /usr/bin/passwd | cut -d' ' -f1\n"),
        dict(label='5 · Challenge', hint='List every SUID program in /usr/bin.', code="find /usr/bin -perm -4000 -type f | sort\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own sudo',
    intro='<p>Your PC asks for your password. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · What may I run?', cmd='sudo -l', output='[sudo] password for vineeta: \nMatching Defaults entries for vineeta on laptop:\n    env_reset, mail_badpass, secure_path=…, use_pty\n\nUser vineeta may run the following commands on laptop:\n    (ALL : ALL) ALL', note='Typical for the first user on Ubuntu.'),
        dict(title='2 · A root shell, then leave', cmd='sudo -i\nwhoami; pwd\nexit', output='root\n/root\nlogout', note='Typical.'),
        dict(title='3 · Is root locked?', cmd='sudo passwd -S root', output=pc('sudo passwd -S root'), note='Recorded: L = locked, so su - fails on Ubuntu.'),
        dict(title='4 · Recent sudo use', cmd='journalctl -t sudo -n 3 --no-pager', output='Nov 11 10:02:31 laptop sudo[4412]:  vineeta : TTY=pts/0 ; PWD=/home/vineeta ; USER=root ; COMMAND=/usr/bin/passwd -S root', note='Typical.'),
        dict(title='5 · Check all rules', cmd='sudo visudo -c', output=pc('sudo visudo -c'), note='Recorded on our build machine (one extra file for riya).'),
    ],
)

TRACE = dict(
    heading='A script that needs root',
    intro='<p>Step through a script that checks its UID and then runs one command with sudo.</p>',
    code='''me=$(id -un)
uid=$(id -u)
if [ "$uid" -eq 0 ]; then mode=root; else mode="user, will use sudo"; fi
echo "$me: $mode"
lines=$(sudo wc -l /etc/shadow | cut -d' ' -f1)
echo "shadow has $lines lines"
''',
    notes={1: 'Name.', 2: 'UID :: 1000, not 0.', 3: 'Decide.', 6: 'sudo :: line 5 ran only wc as root, and wc opened the file itself (a < redirect would be opened by you and fail).'},
)

WORKED_INTRO = 'Three tasks from real jobs, recorded: a read-only support rule, a DBA rule and a sudo audit.'
EXAMPLES = [
    dict(level='b', tag='Help desk', title='sudo vs redirect',
         problem='<p>Append a line to a root-owned file correctly, then remove it.</p>',
         inp='/etc/hosts', approach=['tee -a runs as root.', 'sed -i to clean up.'],
         code='''echo '10.0.0.9 build01' | sudo tee -a /etc/hosts
grep build01 /etc/hosts
sudo sed -i '/build01/d' /etc/hosts; grep build01 /etc/hosts || echo 'build01 removed'
''', notes={1: 'tee :: prints the line and appends it.', 2: 'Check.', 3: 'Clean up :: grep finds nothing.'}, tryit='Try sudo echo … >> /etc/hosts and read the error.'),
    dict(level='i', tag='Support', title='One read-only command for a group',
         problem='<p>Let finance read the package log with tail, and nothing else.</p>',
         inp='group finance', approach=['Write rule to a temp file.', 'visudo -cf, install 440.'],
         code='''printf '%s\\n' '%finance ALL=(root) /usr/bin/tail /var/log/dpkg.log' > /tmp/rule
sudo visudo -cf /tmp/rule
sudo install -m 440 /tmp/rule /etc/sudoers.d/finance
sudo -l -U aman | tail -1
sudo rm /etc/sudoers.d/finance
''', notes={1: 'Rule.', 2: 'Check :: parsed OK.', 3: 'Install read-only.', 4: 'aman’s rights.'}, tryit='Add a second command after a comma.'),
    dict(level='a', tag='Security', title='Audit sudo rights',
         problem='<p>List members of the sudo group and every non-comment rule in sudoers.d.</p>',
         inp='this server', approach=['getent group.', 'grep the files.'],
         code='''echo "sudo group: $(getent group sudo | cut -d: -f4)"
for f in /etc/sudoers.d/*; do
  sudo grep -Hv '^#' "$f" | grep -v ':$'
done
''', notes={1: 'Admins.', 2: 'Each file.', 3: 'Rules :: file name + rule.'}, tryit='Also flag NOPASSWD.'),
]

QUIZ = mix([
    dict(q='Whose password does sudo ask for?', options=['root’s', 'your own', 'the target user’s', 'none'], answer=1, why='su asks for the target’s.'),
    dict(q='Why does sudo echo x >> /etc/hosts fail?', options=['echo is not allowed', 'your shell opens the file before sudo runs', 'hosts is read-only', 'needs -E'], answer=1, why='Use sudo tee -a.'),
    dict(q='Best way to get a root shell on Ubuntu?', options=['su', 'su -', 'sudo -i', 'login root'], answer=2, why='Root is locked.'),
    dict(q='Which runs psql as the postgres user?', options=['sudo psql postgres', 'sudo -u postgres psql', 'su postgres psql', 'sudo -g postgres psql'], answer=1, why='-u = run-as user.'),
    dict(q='Which tool must be used to edit sudoers?', options=['nano', 'visudo', 'vipw', 'sudoedit /etc/sudoers'], answer=1, why='Checks syntax.'),
    dict(q='%dba ALL=(postgres) ALL lets dba members…', options=['do anything as root', 'do anything as postgres', 'only start postgres', 'nothing'], answer=1, why='Run-as limited to postgres.'),
    dict(q='Which shows the commands you may run with sudo?', options=['sudo -l', 'sudo -k', 'sudo -v', 'sudo -i'], answer=0, why='-l lists.'),
    dict(q='Why is allowing sudo less a risk?', options=['less is slow', 'less can start a shell (!bash) as root', 'less edits files', 'it is not'], answer=1, why='Shell escapes.'),
])

REVISION = [
    'root = UID 0. Log in as yourself; use <code>sudo</code> for admin work (own password, logged).',
    '<code>sudo CMD</code>, <code>-i</code> root shell, <code>-u USER</code>, <code>-l</code>, <code>-k</code>, <code>-n</code>, <code>sudoedit</code>.',
    'Redirection is not covered by sudo: <code>… | sudo tee [-a] FILE</code>. sudo cd fails (builtin).',
    '<code>su - USER</code> needs USER’s password; Ubuntu’s root is locked, so use <code>sudo -i</code>.',
    'Rules: <code>WHO HOST=(AS_USER:AS_GROUP) [NOPASSWD:] /full/path args</code>; groups with <code>%</code>; last match wins.',
    'Put rules in <code>/etc/sudoers.d/NAME</code> (440) with <code>visudo -f</code>; check with <code>visudo -c</code>; keep a root shell open.',
    'sudo/su are SUID root; passwords via PAM; logs: <code>journalctl -t sudo</code>, /var/log/auth.log.',
]

FAQ = [
    ('What is the difference between su and sudo?', 'su starts a shell as another user using that user’s password; sudo runs a command as root (or another user) with your own password, according to the sudoers rules, and logs it.'),
    ('How do I give a user sudo rights?', 'sudo usermod -aG sudo USER on Ubuntu (wheel on RHEL), then they log in again.'),
    ('How do I edit the sudoers file?', 'sudo visudo, or sudo visudo -f /etc/sudoers.d/NAME for your own rules.'),
    ('How do I allow a command without a password?', 'A rule like USER ALL=(root) NOPASSWD: /full/path/command (only for specific commands).'),
    ('Why does sudo say “is not in the sudoers file”?', 'The user has no rule; an admin must add them to the sudo group or write a rule. The attempt is logged.'),
    ('How do I get a root shell?', 'sudo -i (exit to leave).'),
    ('Where are sudo logs?', 'journalctl -t sudo, or /var/log/auth.log (Ubuntu) and /var/log/secure (RHEL).'),
]

PRACTICE_INTRO = 'Small sudo tasks. Expected outputs come from real runs on Ubuntu 24.04 (riya is in the sudo group).'
PROBLEMS = [
    dict(level='easy', title='Run as root', stmt='Print the user name sudo runs as.', inp='sudo', code="sudo whoami\n", explain='root.'),
    dict(level='easy', title='Run as another user', stmt='Print the user name when running as aman.', inp='sudo -u', code="sudo -u aman whoami\n", explain='-u.'),
    dict(level='easy', title='Root’s home', stmt='Print the folder a root login shell starts in.', inp='sudo -i', code="sudo -i pwd\n", explain='/root.'),
    dict(level='medium', title='Append safely', stmt='Append a line to a root-owned file with tee, show it, remove it.', inp='/etc/hosts',
         code="echo '10.0.0.7 qa01' | sudo tee -a /etc/hosts > /dev/null\ntail -1 /etc/hosts\nsudo sed -i '/qa01/d' /etc/hosts\n", explain='tee -a.'),
    dict(level='medium', title='Check a rule', stmt='Validate a rule file without installing it.', inp='a temp file',
         code="printf '%s\\n' 'aman ALL=(root) /usr/bin/id' > /tmp/r1\nsudo visudo -cf /tmp/r1\n", explain='-cf.'),
    dict(level='medium', title='Catch a typo', stmt='Validate a rule with a missing colon.', inp='a temp file',
         code="printf '%s\\n' 'aman ALL=(root) NOPASSWD /usr/bin/id' > /tmp/r2\nsudo visudo -cf /tmp/r2 > /dev/null 2>&1; echo \"exit $?\"\n", explain='exit 1.'),
    dict(level='business', title='aman’s rights', stmt='Show what aman may run with sudo.', inp='aman',
         code="sudo -l -U aman | tail -1\n", explain='-U (root only).'),
    dict(level='business', title='SUID helpers', stmt='Show the modes of sudo, su and passwd.', inp='/usr/bin',
         code="ls -l /usr/bin/sudo /usr/bin/su /usr/bin/passwd | cut -d' ' -f1,9\n", explain='rws.'),
]

SCN_INTRO = 'Interview questions about root and sudo, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“su vs sudo?”', 'Asked in almost every Linux interview.', 'do you know the password difference?',
        '''<ul>
          <li>su: target’s password, whole shell, little logging.</li>
          <li>sudo: own password, rules, every command logged.</li>
          <li>Ubuntu: root locked, use sudo -i.</li>
        </ul>''', '“they are the same”.') +
    scn('Help desk', 'Junior', '“sudo: unable to … parse error in /etc/sudoers”', 'Someone edited sudoers with nano and saved a typo.', 'can you recover without reinstalling?',
        '''<ol>
          <li>Use an open root shell, <code>pkexec visudo</code>, or recovery mode.</li>
          <li>Fix with visudo; check with <code>visudo -c</code>.</li>
          <li>Only ever edit with visudo.</li>
        </ol>''', 'reinstalling the OS.') +
    scn('Database team', 'Mid-level', 'Give DBAs what they need, no more', 'DBAs ask for root to restart PostgreSQL and read its logs.', 'can you write least-privilege rules?',
        '''<ul>
          <li><code>%dba ALL=(postgres) ALL</code> for database work.</li>
          <li><code>%dba ALL=(root) /usr/bin/systemctl restart postgresql, /usr/bin/journalctl -u postgresql</code>.</li>
          <li>No editors or shells as root; review logs.</li>
        </ul>''', 'adding DBAs to the sudo group.') +
    scn('Security team', 'Senior', 'A rule lets support run “sudo find”', 'An audit flags it.', 'do you know shell escapes?',
        '''<ul>
          <li><code>sudo find . -exec /bin/sh \\;</code> gives a root shell: the rule is equivalent to ALL.</li>
          <li>Replace with a fixed wrapper script owned by root (not writable), or sudoedit for files.</li>
          <li>Alert on sudo use outside the allowed set.</li>
        </ul>''', '“find only reads files”.')
) + interview([
    ('Where are sudo rules stored?', '/etc/sudoers and /etc/sudoers.d/*.'),
    ('What does NOPASSWD do?', 'No password is asked for that rule.'),
    ('How do you run a command as another user?', 'sudo -u USER CMD.'),
    ('How long does sudo remember your password?', '15 minutes per terminal by default (timestamp_timeout).'),
    ('How do you check sudoers syntax?', 'visudo -c.'),
    ('How do you disable root SSH login?', 'PermitRootLogin no in /etc/ssh/sshd_config (Lesson 16.6).'),
    ('Why is sudo SUID?', 'It must start as root to switch to UID 0 after checking the rules.'),
], [
    ('RHCSA (EX200)', 'Configure superuser access (sudo, wheel); su.'),
    ('LFCS', 'Manage sudo access and the sudoers file.'),
    ('CompTIA Linux+', 'su, sudo, visudo, sudoers, wheel.'),
]) + distro('sudo is the same everywhere; group names and logs differ.', [
    ('Admin group', '%sudo', '%wheel', '%admin', '-'),
    ('Root password', 'locked by default', 'set at install (optional)', 'disabled', '-'),
    ('Log file', '/var/log/auth.log, journal', '/var/log/secure, journal', 'log show --predicate …', '-'),
    ('su -', 'fails (root locked)', 'works with root password', 'needs root enabled', '-'),
    ('Windows equivalent', '-', '-', '-', '“Run as administrator”, runas, sudo for Windows'),
]) + teaser('9.1', 'Riya can now control who is who and who may become root. But why can Aman read report.txt and not edit it, and what do the ten characters -rw-r--r-- actually say? Next: reading permissions.')

CHEATSHEET = cheatsheet('root, su and sudo', [
    ('sudo', [('sudo CMD', 'as root'), ('sudo -u U CMD', 'as U'), ('sudo -i / -s', 'root shell'), ('sudo -l', 'my rules'), ('sudo -k', 'forget password')]),
    ('su', [('su - U', 'login as U'), ('su -c "cmd" U', 'one command'), ('su -', 'root (if unlocked)'), ('exit', 'leave'), ('sudo -iu U', 'su - without their password')]),
    ('Rules', [('%sudo ALL=(ALL:ALL) ALL', 'admins'), ('u ALL=(root) /path cmd', 'one command'), ('%g ALL=(postgres) ALL', 'run-as limit'), ('NOPASSWD:', 'no prompt'), ('/etc/sudoers.d/NAME', 'drop-in, 440')]),
    ('Safety', [('visudo [-f FILE]', 'edit'), ('visudo -c', 'check'), ('… | sudo tee FILE', 'write files'), ('sudoedit FILE', 'edit configs'), ('journalctl -t sudo', 'logs')]),
])

MINDMAP = mindmap('root and sudo', [
    ('root', 'red', ['UID 0', 'no SSH login', 'Ubuntu: locked']),
    ('su', 'amber', ['target password', 'su - login', 'su -c']),
    ('sudo', 'green', ['own password', '-i -u -l -k', 'logged']),
    ('Rules', 'blue', ['who host=(as) what', '%group', 'NOPASSWD']),
    ('Safety', 'violet', ['visudo -c', 'sudoers.d 440', 'no shell escapes']),
    ('Inside', 'acc', ['SUID root', 'PAM', 'secure_path']),
])

LAB = lab('a least-privilege sudo rule', 'Build the lab, do the four tasks in your own terminal (sudo needed), then run the checker. Keep a second terminal with sudo -i open while you work.',
    setup='''sudo rm -f /etc/sudoers.d/labrule; sudo userdel -r labop > /dev/null 2>&1; sudo groupdel labops > /dev/null 2>&1
sudo groupadd labops; sudo useradd -m -s /bin/bash -G labops labop''',
    tasks=['Write the rule <code>%labops ALL=(root) /usr/bin/id</code> into <code>/tmp/labrule</code> and check it with visudo.',
           'Install it as <code>/etc/sudoers.d/labrule</code> with mode <code>440</code>.',
           'Show that <code>labop</code> may now run exactly that command (<code>sudo -l -U labop</code>).',
           'Append the line <code>10.9.9.9 labhost</code> to <code>/etc/hosts</code> the correct way.'],
    solution='''printf '%s\\n' '%labops ALL=(root) /usr/bin/id' > /tmp/labrule && sudo visudo -cf /tmp/labrule
sudo install -m 440 /tmp/labrule /etc/sudoers.d/labrule
sudo -l -U labop | tail -1
echo '10.9.9.9 labhost' | sudo tee -a /etc/hosts > /dev/null''',
    check='''ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 rule file"  'sudo visudo -cqf /tmp/labrule'
ok "2 installed"  '[ "$(sudo stat -c %a /etc/sudoers.d/labrule 2>/dev/null)" = 440 ] && sudo visudo -cq'
ok "3 labop"      'sudo -l -U labop | grep -q "(root) /usr/bin/id"'
ok "4 hosts"      'grep -q "^10.9.9.9 labhost$" /etc/hosts'
sudo sed -i "/labhost/d" /etc/hosts; sudo rm -f /etc/sudoers.d/labrule''')
