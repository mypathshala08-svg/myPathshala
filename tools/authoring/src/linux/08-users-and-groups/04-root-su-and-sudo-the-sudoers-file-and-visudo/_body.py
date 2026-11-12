import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

SCLEAN = 'sudo rm -f /etc/sudoers.d/finance /etc/sudoers.d/dbteam /etc/sudoers.d/90-lab; sudo groupdel dbteam > /dev/null 2>&1; sudo rm -f /tmp/rule'
subprocess.run(['bash', '-c', SCLEAN.replace('sudo ', '')])
AS_AMAN = "echo 'Welcome@1' | sudo -u aman sudo -S"   # aman types his own password
def codebox_typ(cmd, out, label):
    return f'  <div class="code" data-lang="bash" data-file="Terminal"><pre><code>{E(cmd)}</code></pre><div class="output">{E(out)}</div></div>\n  <p class="muted">{label}</p>\n'

LOGTYP = 'Typical output on Ubuntu (our build machine has no system journal).'

HOOK = hook('3 a.m., production is down. Someone logged in as <code>root</code>, ran a command, and nobody knows who it was or what they typed. That is why modern servers almost never let people log in as root. Instead, named people run single commands with <code>sudo</code>: every use is logged with their name, they need their <b>own</b> password, and the rules can give a DBA exactly “restart PostgreSQL” and nothing more. One typo in the rules file can lock every admin out, so it has its own safe editor, <code>visudo</code>.',
    ['explain what root is, why direct root logins are avoided, and how su and sudo differ',
     'use <code>sudo</code>, <code>sudo -i</code>, <code>sudo -u USER</code>, <code>sudo -l</code> and <code>sudo -k</code> correctly, and read sudo’s messages',
     'read and write sudoers rules (<code>who where=(as-whom) what</code>), with groups, NOPASSWD and command limits, in <code>/etc/sudoers.d</code>',
     'edit rules safely with <code>visudo</code>, check them with <code>visudo -c</code>, and find who ran what in the logs'])
ROAD = roadmap([
    ('story', 'The story', 3, 'who was root at 3 a.m.?'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'root, su and sudo', 6, 'simple meaning + 4 depths'),
    ('types', 'su vs sudo', 3, 'and the ways to get a root shell'),
    ('commands', 'Each command, by field', 16, 'sudo, su, sudoers, visudo'),
    ('animation', 'See it happen', 4, 'how sudo decides'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a limited sudo rule'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('Run one command as root', 'sudo COMMAND', 'your own password, logged'),
    ('Several root commands in a row', 'sudo -i  (then exit)', 'a root login shell'),
    ('Run as another user (service account)', 'sudo -u postgres COMMAND', 'DBA, app users'),
    ('Become another user fully', 'sudo -iu USER  /  su - USER', 'su needs THEIR password'),
    ('What am I allowed to do?', 'sudo -l', 'before asking the admin'),
    ('Forget my sudo password cache', 'sudo -k', 'walking away'),
    ('Give someone sudo rights', 'sudo usermod -aG sudo USER', 'wheel on RHEL'),
    ('Allow just one command', 'sudo visudo -f /etc/sudoers.d/NAME', 'least privilege'),
    ('Check rules before logging out', 'sudo visudo -c', 'avoid lock-out'),
])

cmap = concept_map(
    [('8.1', 'UIDs', 'root is UID 0'), ('8.3', 'Groups', 'the sudo group'), ('5.2', 'Redirection', 'sudo tee')],
    ['root: UID 0 and why not to log in as root', 'su, su -, su -c', 'sudo, -i, -u, -l, -k, -E', 'sudoers syntax, aliases, NOPASSWD, sudoers.d', 'visudo, visudo -c, logs'],
    [('9.4', 'SUID', 'why sudo can become root'), ('11.3', 'Signals', 'sudo kill'), ('16.6', 'SSH', 'PermitRootLogin no'), ('17.2', 'systemctl', 'the commands you will allow')],
    'sudo is how ordinary named accounts do administrator work safely, one logged command at a time.')

sc = (term(20, 14, 316, 156, ['$ cat /etc/shadow', ('Permission denied', 'err'), '$ sudo cat /etc/shadow', ('[sudo] password for riya:', 'dim'), ('root:*:20385:0:99999:7:::', 'out'), '$ sudo -l', ('(ALL : ALL) ALL', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Becoming root, safely:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• sudo: one command', '• your own password', '• logged with your name', '• rules in sudoers', '• edit with visudo'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Who was root at 3 a.m.?</h2>
  <div class="story">
''' + puzzle('Riya runs <code>sudo echo "10.0.0.5 db01" &gt;&gt; /etc/hosts</code> and gets “Permission denied”, although sudo worked a second ago for <code>sudo cat /etc/shadow</code>. And when she types <code>su -</code> on Ubuntu with her own password, it fails. Why both?') + '''
    <p class="narration">The morning after the outage. The team lead wants to know who did what.</p>
''' + scene('A terminal: cat /etc/shadow is denied; sudo cat /etc/shadow asks for riya’s own password and works; sudo -l shows what she may run.', sc,
            'sudo: your <tspan font-weight="700" class="s-acc">own</tspan> password, every command logged.') + '''
K> Why not just share the root password with the team? It is faster.
A> Then the logs only say “root did it”. With sudo they say “riya ran systemctl restart nginx at 03:02”. And when Riya leaves, you remove her from one group instead of changing the root password everywhere.
R> Can I give the DBA only database commands?
A> Yes: that is what <code>/etc/sudoers</code> rules are for. Today: root, su and sudo, how to read and write rules, and how to edit them with visudo without locking everyone out.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A bank: the master key (root) stays in a safe; staff ask the duty manager (sudo), show their own ID, and get the vault opened for one task, written in a log book (sudoers rules decide who may ask for what).">'
       + label_box(14, 20, 140, 110, ['master key', 'root (UID 0)', 'opens everything', 'kept in a safe'], 'red', 8.6)
       + label_box(166, 20, 150, 110, ['su', 'borrow the master', 'key: needs root’s', 'password, no log'], 'amber', 8.6)
       + label_box(328, 20, 150, 110, ['sudo', 'duty manager opens', 'one door for you,', 'with YOUR ID'], 'green', 8.6)
       + label_box(490, 20, 136, 110, ['sudoers', 'rule book: who', 'may ask for', 'which doors'], 'blue', 8.6)
       + t(320, 160, 'Most companies never hand out the master key.', 9.6, 'ink2')
       + t(320, 182, 'They use the duty manager and the log book.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('root, su and sudo at four depths', [
    ('v', 'No jargon: a bank’s master key', '      <p>root is the master key of the building.</p>' + pic),
    ('b', 'The commands you will type', '''      <ul>
        <li><code>sudo apt update</code>: run one command as root, typing <b>your</b> password.</li>
        <li><code>sudo -i</code>: a root shell for several commands; <code>exit</code> when done.</li>
        <li><code>sudo -u postgres psql</code>: run as another user.</li>
        <li><code>sudo -l</code>: what you are allowed to run.</li>
        <li><code>su - aman</code>: become aman (needs <b>aman’s</b> password).</li>
      </ul>'''),
    ('i', 'Rules, groups and the password cache', '''      <ul>
        <li>Rules live in <code>/etc/sudoers</code> and files in <code>/etc/sudoers.d/</code>. Ubuntu’s key rule: <code>%sudo ALL=(ALL:ALL) ALL</code>: members of group sudo may run anything as anyone. RHEL: <code>%wheel</code>.</li>
        <li>Rule format: <code>WHO HOST=(RUNAS_USER:RUNAS_GROUP) [NOPASSWD:] COMMANDS</code>, with full paths to commands.</li>
        <li>After a correct password, sudo remembers you for 15 minutes per terminal (<code>timestamp_timeout</code>); <code>sudo -k</code> forgets.</li>
        <li><code>secure_path</code> replaces your PATH for sudo, and <code>env_reset</code> drops most environment variables (keep some with <code>-E</code> or <code>env_keep</code>).</li>
        <li>Ubuntu locks the root password (<code>passwd -S root</code> shows L), so <code>su -</code> fails; use <code>sudo -i</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: SUID, PAM and logging', '''      <ul>
        <li><code>/usr/bin/sudo</code> and <code>/usr/bin/su</code> are <b>SUID root</b> programs (<code>-rwsr-xr-x</code>, Lesson 9.4): they always start with UID 0, check who called them, and only then run your command.</li>
        <li>Password checks go through PAM (<code>/etc/pam.d/sudo</code>, <code>/etc/pam.d/su</code>), the same stack used by login and SSH (2FA modules plug in here).</li>
        <li>sudo logs every attempt to syslog/journal (<code>journalctl -t sudo</code>, <code>/var/log/auth.log</code> on Ubuntu, <code>/var/log/secure</code> on RHEL), including denied ones. <code>log_output</code> can even record whole sessions (<code>sudoreplay</code>).</li>
        <li>Rules are matched top to bottom and the <b>last</b> match wins, so specific rules go after general ones. Files in sudoers.d are read in name order; names with a dot or ending in ~ are ignored.</li>
        <li>Command limits can be escaped: allowing <code>vim</code>, <code>less</code>, <code>find</code>, <code>tar</code> or any shell-escaping program as root effectively allows everything. Prefer <code>sudoedit</code> for editing files.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>root, su, sudo, sudoers and visudo</h2>
''' + def_block(
    '<b>root</b> is the superuser, UID 0, which bypasses normal permission checks. <code>su</code> (substitute user) starts a shell as another user after you type <b>that user’s</b> password. <code>sudo</code> runs a single command as root (or another user) after you type <b>your own</b> password, if the rules in <code>/etc/sudoers</code> allow it, and logs it. <code>visudo</code> is the safe editor for those rules: it locks the file and refuses to save a rule with a syntax error.',
    'Let named people do administrator work, one controlled and logged command at a time.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('root / superuser', 'UID 0: can read, change and kill anything.'),
    ('Privilege escalation', 'Getting more rights than you started with.'),
    ('sudoers', 'The rule file that says who may run what with sudo.'),
    ('Run-as user', 'The user a command runs as: root by default, or -u USER.'),
    ('NOPASSWD', 'A rule tag: no password asked (automation).'),
    ('Least privilege', 'Give only the rights a job needs.'),
    ('Login shell', 'A shell that reads the user’s startup files (su -, sudo -i).'),
    ('PAM', 'Pluggable Authentication Modules: how passwords are checked.'),
]) + '\n' + names('Where the names come from.', [
    ('root', 'root of the tree', 'Its home was / once.'),
    ('su', 'substitute user', 'Originally “superuser”.'),
    ('sudo', 'superuser do / substitute user do', 'Written in 1980 at SUNY Buffalo.'),
    ('sudoers', 'sudo + users', 'The rule file.'),
    ('visudo', 'vi + sudo', 'Opens in your $EDITOR, checks syntax.'),
    ('sudoedit', 'sudo -e', 'Edit a copy, then install it.'),
    ('wheel', 'big wheel', 'Admin group on RHEL.'),
    ('PAM', 'Pluggable Authentication Modules', 'Since 1995.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('One command', '<code>sudo CMD</code>'),
    ('Root shell', '<code>sudo -i</code>'),
    ('As another user', '<code>sudo -u USER CMD</code>'),
    ('My rights', '<code>sudo -l</code>'),
    ('Edit rules', '<code>sudo visudo</code>'),
    ('Check rules', '<code>sudo visudo -c</code>'),
]) + '\n' + lv + didyou('<code>sudo</code> asks for <b>your</b> password, not root’s. On Ubuntu the root account has no usable password at all: the first user is simply placed in the <code>sudo</code> group by the installer.') + '''
EXAM> “Allow members of group dba to run /usr/bin/systemctl restart postgresql as root without a password.” → file <code>/etc/sudoers.d/dba</code> (via visudo -f): <code>%dba ALL=(root) NOPASSWD: /usr/bin/systemctl restart postgresql</code>.
''' + qc('Why is sudo safer than sharing the root password?', 'Each person uses their own password, every command is logged with their name, rules can limit commands, and removing one person does not require changing a shared secret.') + mistake('if [ "$(whoami)" != "root" ]; then echo "must be root"; fi   (a root check from common notes)',
    'if [ "$(id -u)" -ne 0 ]; then …   (compare the UID, not the name)',
    'The notes’ version works on most systems, but root could be renamed or another UID 0 account used. The kernel only cares about UID 0 (Lesson 8.1).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>su vs sudo, and five ways to get a root shell</h2>
''' + table(['', 'su', 'sudo'], [
    ['Password asked', 'the <b>target</b> user’s (root’s for su -)', 'your <b>own</b>'],
    ['What it gives', 'a whole shell as that user', 'one command (or a shell with -i / -s)'],
    ['Rules', 'none: knowing the password is enough', '/etc/sudoers: who, where, as whom, what'],
    ['Logging', 'only “riya became root”', 'every command with its arguments'],
    ['Works on Ubuntu for root', 'no (root is locked)', 'yes, for the sudo group'],
    ['Typical use', 'switching to a colleague’s/test account', 'all administration'],
], minw=520) + table(['Command', 'Shell', 'Environment', 'Starts in', 'Use'], [
    ['<code>sudo -i</code>', 'root’s login shell', 'root’s (clean)', '/root', 'admin session: <b>best</b>'],
    ['<code>sudo -s</code>', 'your $SHELL as root', 'mostly yours', 'current dir', 'quick, keeps your settings'],
    ['<code>sudo su -</code>', 'root login shell', 'root’s', '/root', 'old habit, same as sudo -i'],
    ['<code>su -</code>', 'root login shell', 'root’s', '/root', 'only if root has a password'],
    ['<code>su</code>', 'root shell', '<b>yours</b> (PATH, HOME)', 'current dir', 'avoid: confusing environment'],
], minw=600) + qc('A colleague types <code>su</code> (without the dash) and then a command is “not found” that works with <code>su -</code>. Why?', 'Without the dash the shell keeps the old environment (your PATH, which may not include /usr/sbin). su - runs a full login and loads root’s environment.') + '''
</section>
'''

RULE_FIN = "printf '%s\\n' '%finance ALL=(root) /usr/bin/tail /var/log/dpkg.log' > /tmp/rule && sudo visudo -cqf /tmp/rule && sudo install -m 440 /tmp/rule /etc/sudoers.d/finance"

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine. riya is in the sudo group; aman (password <code>Welcome@1</code>) is a normal user in finance. Where aman uses sudo, he types his own password (piped into <code>sudo -S</code> so the run can be recorded). Log outputs are marked <b>typical</b>.</p>
''' + cmdcard_u(['every administrative command', 'running a command as a service account', 'checking what you are allowed to do'],
               ['sudo with redirection to a protected file (use sudo tee)', 'running whole scripts as root when one line needs it'])(
    'sudo', 'sudo', 'run one command as root',
    'Checks the sudoers rules, asks for <b>your</b> password (unless cached or NOPASSWD), logs the command, and runs it as root or the user given with <code>-u</code>.',
    'sudo [-u USER] [-g GROUP] [-i|-s] [-l] [-k] [-E] [-n] COMMAND', 'change',
    [('sudo CMD', 'run as root', 'admin work'),
     ('-u postgres CMD', 'run as another user', 'service accounts'),
     ('-i', 'root login shell', 'several commands'),
     ('-iu aman', 'login shell as aman', 'test their view'),
     ('-l', 'list my rules', 'what can I do?'),
     ('-l -U aman', 'list aman’s rules (root)', 'audits'),
     ('-k', 'forget cached password', 'walking away'),
     ('-n', 'never ask; fail instead', 'scripts, cron'),
     ('-E', 'keep my environment', 'proxies, variables'),
     ('sudoedit FILE', 'edit as root, safely', 'config files')],
    dict(cmd="cat /etc/shadow 2>&1 | head -1\nsudo head -1 /etc/shadow\nsudo whoami; sudo -u aman whoami", expect='any', note='The same command, denied and then allowed. -u runs as aman instead of root.'),
    [('sys', [
        dict(situation='What may I run? (riya, in the sudo group)', cmd='sudo -l | tail -2', rec=('Typical output on Ubuntu for a member of the sudo group', 'User riya may run the following commands on web01:\n    (ALL : ALL) ALL'),
             why='(ALL : ALL) ALL = any command, as any user and group. Our build machine adds a NOPASSWD line so recordings work without typing.'),
        dict(situation='Write to a protected file: sudo applies to the command, not to the redirect.', cmd="sudo echo '10.0.0.5 db01' >> /etc/hosts; echo \"exit $?\"\necho '10.0.0.5 db01' | sudo tee -a /etc/hosts > /dev/null; tail -1 /etc/hosts\nsudo sed -i '/db01/d' /etc/hosts", expect='any',
             why='Your own shell opens /etc/hosts for >> before sudo starts. tee runs as root and opens it (Lesson 5.2). That is half the puzzle.')]),
     ('dba', [
        dict(situation='Work as the database account without knowing its password.', cmd='sudo -u postgres whoami\nsudo -u postgres bash -c "cd; pwd"',
             why='DBAs run psql, pg_dump and backups as postgres: sudo -u postgres psql. postgres has no password at all.')]),
     ('devops', [
        dict(situation='Scripts and cron must never hang waiting for a password.', cmd=f"sudo -u aman sudo -n true; echo \"exit $?\"", expect='any',
             why='-n fails immediately (exit 1) instead of prompting. Give automation a NOPASSWD rule for exactly the commands it needs.')]),
     ('sec', [
        dict(situation='A normal user tries sudo (aman types his own password).', cmd=f"{AS_AMAN} cat /etc/shadow; echo \"exit $?\"", expect='any',
             why='Denied and reported: “is not in the sudoers file. This incident will be reported.” Every attempt is logged.')]),
    ],
    anat=anatomy([('sudo', 'cmd', 'check rules, ask, log'), ('-u postgres', 'opt', 'run as'), ('psql', 'arg', 'the command'), ('-c "select 1"', 'arg', 'its options')], 'Everything after the sudo options is the command, run as the target user.'),
    sudo=True
) + mistake('sudo echo "text" >> /etc/hosts   ·   sudo cd /root', 'echo "text" | sudo tee -a /etc/hosts   ·   sudo -i, then cd /root',
            'Redirections and cd are done by your own shell, which is not root. sudo cd fails because cd is a shell builtin, not a program.') + cmdcard_u(['switching to another (test) account whose password you know', 'systems where root has a password'],
               ['getting root on Ubuntu (root is locked; use sudo -i)', 'su without the dash (keeps your environment)'])(
    'su', 'su · su - · su -c', 'become another user',
    'Starts a shell as another user (root by default) after you type <b>that user’s</b> password. <code>-</code> (or <code>-l</code>) makes it a full login: their HOME, PATH and startup files. <code>-c</code> runs one command.',
    'su [-] [USER]   ·   su -c "COMMAND" USER   ·   sudo su - USER', 'change',
    [('su - aman', 'login as aman', 'test their view'),
     ('su -c "id" aman', 'one command as aman', 'quick check'),
     ('su -', 'root login (needs root password)', 'RHEL, old systems'),
     ('su', 'keeps your environment', 'avoid'),
     ('exit', 'back to your shell', 'always'),
     ('sudo passwd -S root', 'is root locked?', 'Ubuntu: L')],
    dict(cmd="sudo passwd -S root | cut -d' ' -f1,2\nsu -c whoami aman", rec=('Recorded on our build machine; su reads the password from a terminal, so it was typed into a real terminal session (aman’s password, not shown)', 'root L\nPassword: \naman'), note='root is locked (L) on Ubuntu. su -c with aman’s password runs whoami as aman.'),
    [('qa', [
        dict(situation='See exactly what a user sees at login.', cmd='sudo -iu aman bash -c "pwd; id -Gn; echo \\$SHELL"',
             why='sudo -iu is like su - aman, but with your password instead of his.')]),
    ]
) + cmdcard_u(['giving a person or group admin rights', 'giving exactly one command to a team', 'automation that needs root for one task'],
               ['editing with a normal editor', 'allowing editors, pagers or shells as root (they escape)'])(
    'sudoers', '/etc/sudoers · /etc/sudoers.d', 'the rules',
    'Each rule says <b>who</b> (user, <code>%group</code>) may run <b>what</b> (full paths), on <b>which host</b>, <b>as whom</b>. Put your own rules in small files in <code>/etc/sudoers.d/</code> (mode 440) instead of changing the main file.',
    'WHO  HOST=(RUNAS_USER:RUNAS_GROUP)  [NOPASSWD:]  /full/path/cmd [args], …', 'danger',
    [('%sudo ALL=(ALL:ALL) ALL', 'group sudo: everything', 'Ubuntu default'),
     ('aman ALL=(root) /usr/bin/systemctl restart nginx', 'one exact command', 'least privilege'),
     ('%dba ALL=(postgres) ALL', 'anything, but only as postgres', 'DBAs'),
     ('deploy ALL=(root) NOPASSWD: /usr/local/bin/deploy.sh', 'no password', 'CI/CD'),
     ('Defaults timestamp_timeout=5', 'cache 5 minutes', 'policy'),
     ('Cmnd_Alias WEB = /usr/bin/systemctl restart nginx, …', 'named command lists', 'tidy rules'),
     ('@includedir /etc/sudoers.d', 'read the extra files', 'already there')],
    dict(cmd="sudo grep -Ev '^#|^$' /etc/sudoers\nls -l /etc/sudoers", note='Ubuntu’s whole default policy: a few Defaults, root, the admin and sudo groups, and the include line. The file is read-only (440) on purpose.'),
    [('sys', [
        dict(situation='Give the finance group one read-only log command.', setup=SCLEAN, cmd=f"{RULE_FIN}\nsudo cat /etc/sudoers.d/finance\nsudo -l -U aman | tail -2",
             why='Written to a temp file, checked with visudo -c, then installed with mode 440. A broken rule never reaches /etc/sudoers.d.'),
        dict(situation='Aman uses his one allowed command, and is denied anything else.', setup=SCLEAN + '; ' + RULE_FIN, cmd=f"{AS_AMAN} /usr/bin/tail /var/log/dpkg.log | tail -1 | cut -c1-50\n{AS_AMAN} /usr/bin/tail -n 1 /var/log/dpkg.log; echo \"exit $?\"\n{AS_AMAN} /usr/bin/tail /etc/shadow; echo \"exit $?\"", expect='any',
             why='Arguments are part of the rule: the exact command works, but adding <code>-n 1</code> or naming another file is refused. To allow any arguments, end the rule with the command alone (<code>/usr/bin/tail</code>), which here would expose /etc/shadow.')]),
     ('dba', [
        dict(situation='DBAs may do anything, but only as the postgres account.', setup=SCLEAN, cmd="sudo groupadd dbteam; sudo gpasswd -a aman dbteam > /dev/null\nprintf '%s\\n' '%dbteam ALL=(postgres) ALL' > /tmp/rule && sudo visudo -cqf /tmp/rule && sudo install -m 440 /tmp/rule /etc/sudoers.d/dbteam\n" + f"{AS_AMAN} -u postgres whoami\n{AS_AMAN} whoami; echo \"exit $?\"\nsudo rm /etc/sudoers.d/dbteam; sudo groupdel dbteam", expect='any',
             why='Aman can become postgres (backups, psql) but not root.')]),
     ('sec', [
        dict(situation='Why allowing an editor or pager as root is dangerous.', cmd="sudo -l -U aman 2>/dev/null | tail -1; echo 'rule like: aman ALL=(root) /usr/bin/less /var/log/syslog'\necho 'inside less, typing !bash gives a root shell: use sudoedit or a read-only command instead'",
             why='Programs that can start other programs (vim, less, find -exec, tar, awk) break command limits. GTFOBins lists them.')]),
    ],
    sudo=True
) + cmdcard_u(['every change to sudo rules', 'checking all rule files before you log out'],
               ['nano /etc/sudoers (no syntax check: one typo and nobody can use sudo)'])(
    'visudo', 'visudo · visudo -c', 'edit rules safely',
    'Opens the sudoers file (or <code>-f FILE</code>) in your editor, locks it, and checks the syntax before saving; on an error it asks “What now?” (e = edit again, x = discard). <code>-c</code> only checks.',
    'sudo visudo   ·   sudo visudo -f /etc/sudoers.d/NAME   ·   sudo visudo -c [-f FILE]', 'change',
    [('visudo', 'edit /etc/sudoers', 'rare'),
     ('visudo -f /etc/sudoers.d/team', 'edit a drop-in file', 'your rules'),
     ('visudo -c', 'check every file', 'after changes'),
     ('visudo -cf FILE', 'check one file', 'before installing'),
     ('EDITOR=nano visudo', 'choose the editor', 'not vi')],
    dict(cmd="printf '%s\\n' 'aman ALL=(root) NOPASSWD /usr/bin/ls' > /tmp/bad\nsudo visudo -cf /tmp/bad; echo \"exit $?\"\nsudo visudo -c", expect='any', note='The missing colon after NOPASSWD is caught, with the position marked. The installed files all parse OK.'),
    [('devops', [
        dict(situation='Automation: validate before installing (Ansible does the same with validate: visudo -cf %s).', setup=SCLEAN, cmd="printf '%s\\n' 'deploy ALL=(root) NOPASSWD: /usr/local/bin/deploy.sh' > /tmp/rule\nsudo visudo -cf /tmp/rule && sudo install -m 440 /tmp/rule /etc/sudoers.d/90-lab && echo installed\nsudo rm /etc/sudoers.d/90-lab",
             why='Never write straight into /etc/sudoers.d from a script.')]),
    ],
    sudo=True
) + mistake('sudo nano /etc/sudoers', 'sudo visudo   (or sudo visudo -f /etc/sudoers.d/NAME)',
            'If you save a syntax error with nano, sudo refuses to run for everyone (“parse error in /etc/sudoers”), and you need recovery mode or pkexec to fix it.') + undo('Mistakes with sudo rules can lock you out. Prepare before you change them.', [
    ('Before editing:', 'keep a second terminal open with <code>sudo -i</code>: it stays root even if you break the rules.'),
    ('Broke sudoers anyway:', '<code>pkexec visudo</code> (desktops), or boot into recovery mode (Lesson 17.1) and fix the file.'),
    ('Removed yourself from the sudo group:', 'another admin runs <code>usermod -aG sudo YOU</code>, or use recovery mode.'),
    ('Left a root shell open:', '<code>exit</code>; for cached passwords, <code>sudo -k</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd=f"{AS_AMAN} whoami", meaning='The user has no sudo rule at all. The attempt is logged.', fix='Ask an admin to add you to sudo, or for a specific rule.'),
    dict(cmd="sudo -u aman sudo -n true", meaning='sudo needs a password but -n forbids asking (scripts).', fix='Run interactively, or add a NOPASSWD rule for that exact command.'),
    dict(cmd='sudo cd /root', meaning='cd is a shell builtin; sudo can only run programs.', fix='<code>sudo -i</code>, then cd; or <code>sudo ls /root</code>.'),
    dict(cmd="sudo visudo -cf /tmp/bad", meaning='A syntax error in a rules file (position shown).', fix='Fix it before installing; never install a file that fails -c.'),
]) + qc('You want aman to restart nginx and nothing else. Write the rule.', '<code>aman ALL=(root) /usr/bin/systemctl restart nginx</code> in a file under /etc/sudoers.d, created with visudo -f.') + '''
'''

SCREENS = screens_block('Real terminal screens: sudo asks for YOUR password', 'aman (with a one-command rule) runs sudo: it asks for his own password, not root’s.',
    SCLEAN + '; ' + RULE_FIN + "; printf '%s\\n' 'PS1=\"aman@web01:~$ \"' > /tmp/amanrc; chmod 644 /tmp/amanrc", 'sudo -u aman bash --rcfile /tmp/amanrc', [
    ('Enter', "'sudo tail /var/log/dpkg.log | wc -l' Enter", ' after <code>sudo tail /var/log/dpkg.log | wc -l</code>: the password prompt (nothing appears while typing).'),
    ('Enter', "'Welcome@1' Enter", ' after typing his password: the allowed command ran (10 lines counted).'),
], 78, 10, hid='screens', what='bash')

LOGS = '''  <h3 id="logs">Who ran what? Reading sudo’s log</h3>
  <p>Every sudo attempt is logged with the user, the terminal, the working folder and the full command. On Ubuntu read them with <code>journalctl</code> or in <code>/var/log/auth.log</code>.</p>
''' + codebox_typ('sudo journalctl -t sudo --since today | tail -3',
    'Nov 11 03:02:14 web01 sudo[2311]:     riya : TTY=pts/0 ; PWD=/home/riya ; USER=root ; COMMAND=/usr/bin/systemctl restart nginx\nNov 11 09:41:07 web01 sudo[2840]:     aman : TTY=pts/1 ; PWD=/home/aman ; USER=root ; COMMAND=/usr/bin/tail /var/log/dpkg.log\nNov 11 09:41:20 web01 sudo[2851]:     aman : command not allowed ; TTY=pts/1 ; PWD=/home/aman ; USER=root ; COMMAND=/usr/bin/tail -n 1 /etc/shadow', LOGTYP) + '''
  <p>The 3 a.m. question from the story is answered in one line: riya restarted nginx from pts/0. Denied attempts (“command not allowed”, “user NOT in sudoers”) are worth an alert.</p>
'''

cards = cards + SCREENS + LOGS + '</section>\n'

def decide_anim(k, note, tone):
    st = [('rule for', 'riya?'), ('password', 'correct?'), ('log it', 'journal'), ('run as', 'UID 0')]
    o = ''
    for i, (a, b) in enumerate(st):
        tn = 'card'
        if i < k:
            tn = 'green'
        if i == k:
            tn = 'amber'
        o += label_box(8 + i * 88, 30, 80, 56, [a, b], tn, 8)
        if i < 3:
            o += arrow(89 + i * 88, 58, 95 + i * 88, 58)
    return o + t(180, 126, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ sudo systemctl restart nginx'] + ([('[sudo] password for riya:', 'dim')] if k >= 1 else []) + ([('$', 'prompt')] if k == 3 else []), title='riya@web01', prompt='riya@web01:~$', size=8) + cap(c, '', 'card', y=150, h=34)
       for k, c in enumerate(['You press Enter…', '…sudo asks for YOUR password…', '…a moment…', '…nginx restarted.'])]
behind = [decide_anim(0, 'sudo (SUID root) reads sudoers: %sudo ALL=(ALL:ALL) ALL.', 'violet'), decide_anim(1, 'PAM checks riya’s password against shadow.', 'violet'),
          decide_anim(2, 'The command is logged with riya’s name.', 'violet'), decide_anim(3, 'Only now: the command runs with UID 0.', 'green')]
two = anim_two('How sudo decides', 'Behind the screen: rules, password, log, run',
               'A terminal: sudo systemctl restart nginx asks for riya’s password and returns.',
               'Four boxes: sudoers rule check, PAM password check, logging, then running the command as UID 0.', see, behind,
               ['Enter.', 'Your password, not root’s.', 'Silent checks.', 'Done.'],
               ['1. sudoers: allowed?', '2. PAM: password', '3. journal: logged', '4. exec as root'])

def lock(k, note, tone):
    o = label_box(14, 14, 160, 60, ['/etc/sudoers.d/team', 'aman ALL=(root)', 'NOPASSWD /usr/bin/ls' if k < 3 else 'NOPASSWD: /usr/bin/ls'], 'red' if k in (1, 2) else ('green' if k == 3 else 'card'), 8)
    o += label_box(196, 14, 150, 60, ['sudo for everyone', 'BROKEN' if k == 1 else ('safe' if k >= 2 else 'working')], 'red' if k == 1 else 'green', 8)
    return o + t(180, 110, note, 8.6, tone, bold=True)
frames = [lock(0, 'A rule with a missing colon is about to be saved.', 'violet'), lock(1, 'Saved with nano: sudo stops working for ALL admins.', 'red'),
          lock(2, 'With visudo: “syntax error”, the file is not saved.', 'amber'), lock(3, 'Fixed and saved: sudo still works.', 'green')]
s1 = anim_one('Animated example', 'Why visudo exists',
              'One character decides whether sudo keeps working.',
              'nano vs visudo', 'A rule file with a missing colon: saved with nano it breaks sudo for everyone; visudo refuses to save it.', frames,
              ['A typo.', 'Lock-out.', 'Caught.', 'Safe.'], hid='scenario-visudo')

dx = dissect('Layer by layer: what happens when you type sudo',
    'Each layer has a real command and output from our build machine.', [
    dict(key='suid', name='SUID binary', sub='/usr/bin/sudo', why='Starts as root, whoever runs it.', how='s bit (Lesson 9.4).', impl='Owned by root, mode 4755.', used='sudo, su, passwd.',
         cmd='ls -l /usr/bin/sudo /usr/bin/su'),
    dict(key='rules', name='sudoers', sub='policy', why='Who may run what.', how='Last match wins.', impl='/etc/sudoers + sudoers.d.', used='Every call.',
         cmd="sudo grep -E '^%|^root' /etc/sudoers"),
    dict(key='pam', name='PAM', sub='/etc/pam.d/sudo', why='Password, 2FA, limits.', how='Stack of modules.', impl='pam_unix checks shadow.', used='sudo, su, login, ssh.',
         cmd="grep -v '^#' /etc/pam.d/sudo | grep ."),
    dict(key='env', name='Environment', sub='secure_path, env_reset', why='Stops PATH tricks.', how='Defaults in sudoers.', impl='Clean environment.', used='Every command.',
         cmd="sudo bash -c 'echo \"$PATH\"'"),
], hint='From the program to the policy. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How sudo decides, and why visudo exists</h2>
''' + two + s1 + dx + qc('sudo runs a command as root, yet the program is started by riya. How can it become root?', 'sudo is an SUID-root program: the kernel starts it with UID 0, and it decides from sudoers whether to run your command.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>root and sudo at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['%sudo', 'admins'], 'blue', 8.6), '1. Admin access',
              'Admins are members of sudo/wheel; root logins over SSH are disabled.', ['Admin', '*sudo', 'logged']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['%dba', '(postgres)'], 'green', 8.6), '2. Role-based rules',
    'DBAs, developers and support get only the commands their role needs.', ['Role', '*sudoers.d', 'least privilege']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['deploy', 'NOPASSWD'], 'amber', 8.6), '3. Automation',
    'CI/CD accounts get NOPASSWD for one deploy script and nothing else.', ['Pipeline', '*sudo -n', 'deploy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['journalctl', '-t sudo'], 'red', 8.6), '4. Audit',
    'Security teams alert on denied sudo attempts and review who ran what.', ['Logs', '*grep', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['visudo -c', 'validate'], 'violet', 8.6), '5. Config management',
    'Ansible, Puppet and Chef write sudoers.d files and validate them with visudo.', ['Template', '*visudo -cf', 'install']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Am I root?', scenario='In a script.', cmd='[ "$(id -u)" -eq 0 ] && echo root || echo "not root ($(id -un))"', explain='UID 0.'),
    dict(level='b', title='Who can sudo?', scenario='Members of the sudo group.', cmd='getent group sudo', explain='Field 4.'),
    dict(level='i', title='All rule files parse', scenario='After any change.', cmd='sudo visudo -c', explain='Checks every file.'),
    dict(level='i', title='Which sudoers files exist', scenario='Drop-in rules.', cmd='sudo ls -l /etc/sudoers.d', explain='Mode 440 each.'),
    dict(level='a', title='Any NOPASSWD rules?', scenario='Audit passwordless rules.', cmd="sudo grep -rh NOPASSWD /etc/sudoers /etc/sudoers.d 2>/dev/null | grep -v '^#'", explain='Our build machine has one for riya.'),
], extra=build_up('a role-based rule for the DBA', 'Riya lets the dbteam group work as postgres, and checks it.', SCLEAN, [
    ('sudo groupadd dbteam && sudo gpasswd -a aman dbteam', '1. The role group.'),
    ("printf '%s\\n' '%dbteam ALL=(postgres) ALL' > /tmp/rule && sudo visudo -cf /tmp/rule", '2. Write and validate the rule.'),
    ('sudo install -m 440 /tmp/rule /etc/sudoers.d/dbteam && sudo ls -l /etc/sudoers.d/dbteam', '3. Install read-only.'),
    ('sudo -l -U aman | tail -2', '4. What aman may run now.'),
], cumulative=True)) + which('Choosing the right command.', [
    ('One admin command', 'sudo CMD', 'Logged, own password.', 'Logging in as root.'),
    ('Root session', 'sudo -i', 'Clean env.', 'su (no dash).'),
    ('As a service user', 'sudo -u USER', 'No password needed for them.', 'Sharing their password.'),
    ('Write a root file', '… | sudo tee FILE', 'tee is root.', 'sudo echo > FILE.'),
    ('Edit a root file', 'sudoedit FILE', 'Editor not root.', 'sudo vim (escapes).'),
    ('Change rules', 'visudo -f sudoers.d/x', 'Checked.', 'nano /etc/sudoers.'),
    ('Give admin', 'usermod -aG sudo USER', 'Standard.', 'Editing the main file.'),
]) + keys('Handy forms.', [
    ('sudo !!', 'repeat the last command with sudo', 'after Permission denied'),
    ('sudo -k', 'forget the password cache', 'walking away'),
    ('sudo -l', 'my rules', 'before asking'),
    ('sudo -iu USER', 'their login view', 'testing'),
    ('sudoedit FILE', 'safe editing', 'configs'),
    ('exit / Ctrl+D', 'leave a root shell', 'always'),
]) + scriptit('need-root.sh', 'The standard start of an admin script: re-run itself with sudo if needed, then do the root work.',
'''if [ "$(id -u)" -ne 0 ]; then
  echo "not root ($(id -un)): re-running with sudo" >&2
  exec sudo bash "$0" "$@"
fi
echo "running as $(id -un) (UID $(id -u))"''',
'<p><code>exec sudo bash "$0"</code> replaces the script with a root copy of itself. Here the script is saved as a file and run by riya.</p>') + puzzle_answer('In <code>sudo echo … &gt;&gt; /etc/hosts</code> only echo runs as root; the <code>&gt;&gt;</code> is opened by riya’s own shell, which may not write /etc/hosts. Use <code>echo … | sudo tee -a /etc/hosts</code>. And <code>su -</code> wants <b>root’s</b> password, which Ubuntu locks: use <code>sudo -i</code> with your own password.') + qc('Which file would you create to give the group support permission to run <code>/usr/bin/journalctl</code>, and with which command?', '<code>sudo visudo -f /etc/sudoers.d/support</code> containing <code>%support ALL=(root) /usr/bin/journalctl</code>.') + '''
</section>
'''

subprocess.run(['bash', '-c', SCLEAN.replace('sudo ', '')])
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../03-managing-groups-groupadd-gpasswd-and-usermod-ag/">Lesson 8.3</a> (groups) and <a href="../../05-redirection-and-pipes/02-redirection-dev-null-and-here-documents/">5.2</a> (redirection and tee).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
