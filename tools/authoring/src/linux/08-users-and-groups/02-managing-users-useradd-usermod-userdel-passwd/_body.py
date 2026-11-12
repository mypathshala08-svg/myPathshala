import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

CLEAN = 'for u in karan neha mohan cdac; do sudo userdel -r "$u" > /dev/null 2>&1; sudo groupdel "$u" > /dev/null 2>&1; done; sudo rm -rf /home/customcdac /data/home/karan /tmp/mohan_report.txt'

HOOK = hook('Monday: Neha joins the data team and needs an account by 10 a.m., with a home folder, bash, and a password she must change at first login. Friday: Mohan leaves; his account must stop working today, but his project files must be kept for his manager. Three months later an auditor asks why passwords never expire. All of this is user management, and a single wrong option (a missing <code>-m</code>, a <code>-G</code> without <code>-a</code>) causes real tickets.',
    ['create accounts properly with <code>useradd</code> (<code>-m -s -c -u -g -G -d -e</code>) and the friendlier <code>adduser</code>',
     'set, lock, unlock and expire passwords with <code>passwd</code>, and set ageing rules with <code>chage</code>',
     'change existing accounts with <code>usermod</code> (shell, comment, home, name, lock), without losing groups',
     'remove or disable leavers safely with <code>userdel</code> and <code>userdel -r</code>, and know what is left behind'])
ROAD = roadmap([
    ('story', 'The story', 3, 'a joiner and a leaver'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'What the tools are', 5, 'simple meaning + 4 depths'),
    ('types', 'useradd vs adduser', 3, 'and lock vs delete'),
    ('commands', 'Each command, by field', 18, 'options, real runs'),
    ('animation', 'See it happen', 4, 'what useradd writes'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'onboard and offboard'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('New person, normal account', 'sudo useradd -m -s /bin/bash -c "Full Name" NAME', 'then set a password'),
    ('…interactive and friendly (Debian/Ubuntu)', 'sudo adduser NAME', 'asks questions'),
    ('Service account (no login)', 'sudo useradd -r -s /usr/sbin/nologin NAME', 'apps and daemons'),
    ('Set or reset a password', 'sudo passwd NAME', 'or chpasswd for many'),
    ('Force change at first login', 'sudo chage -d 0 NAME', 'temporary passwords'),
    ('Block login now, keep everything', 'sudo usermod -L -e 1 NAME', 'leavers, incidents'),
    ('Change shell / comment / name', 'sudo usermod -s / -c / -l', 'existing accounts'),
    ('Password must expire every 90 days', 'sudo chage -M 90 NAME', 'policy'),
    ('Remove account and home', 'sudo userdel -r NAME', 'back up first!'),
])

cmap = concept_map(
    [('8.1', 'Users and groups', 'passwd, shadow, UID'), ('3.1', 'Creating files', 'mkdir, home folders'), ('7.1', 'find', '-user, -nouser')],
    ['useradd and adduser: options and defaults', 'passwd: set, lock, unlock, expire', 'chage: password ageing', 'usermod: change accounts safely', 'userdel: remove, and what remains'],
    [('8.3', 'Managing groups', 'groupadd, usermod -aG'), ('8.4', 'root and sudo', 'who may run useradd'), ('9.3', 'chown', 'hand files to a manager'), ('16.6', 'SSH keys', 'login without passwords')],
    'Onboarding and offboarding are daily admin work. Doing them with the right options keeps accounts consistent and auditable.')

sc = (term(20, 14, 316, 156, ['$ sudo useradd -m -s /bin/bash neha', '$ sudo passwd neha', ('passwd: password updated successfully', 'out'), '$ sudo chage -d 0 neha', '$ sudo usermod -L -e 1 mohan', ('mohan: login disabled, files kept', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Account life cycle:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• create: useradd -m', '• password: passwd', '• rules: chage', '• change: usermod', '• leave: lock, then userdel'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A joiner on Monday, a leaver on Friday</h2>
  <div class="story">
''' + puzzle('A note says: <code>sudo useradd -m cdac</code> “creates a home directory at /home/john”, and the new user can log in with bash. Riya runs exactly that, then logs in as cdac and gets a bare <code>$</code> prompt where arrow keys print <code>^[[A</code>. Two things in the note are wrong. Which?') + '''
    <p class="narration">The ticket queue at a small company. Riya handles accounts.</p>
''' + scene('A terminal: useradd creates neha with a home and bash, passwd sets a password, chage forces a change at first login, and usermod locks mohan.', sc,
            'Create, change, <tspan font-weight="700" class="s-acc">lock</tspan>, and only then delete.') + '''
K> Can I just run <code>useradd neha</code>?
A> Without <code>-m</code> there is no home folder, and without <code>-s /bin/bash</code> Ubuntu gives her <code>/bin/sh</code>. Always say what you want: <code>useradd -m -s /bin/bash -c "Neha Rao" neha</code>.
R> And Mohan? Delete him?
A> Not yet. Lock first (<code>usermod -L -e 1</code>), hand his files over, then delete with <code>userdel -r</code> when his manager agrees. Deleting is the one step you cannot undo.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="An employee life cycle: hire (useradd), give a key (passwd), set rules for the key (chage), change the job (usermod), and finally return the badge (userdel).">'
       + ''.join(label_box(14 + i * 126, 30, 116, 92, ls, tn, 8.6) for i, (ls, tn) in enumerate([
           (['hire', 'useradd -m', 'desk + locker', '(home folder)'], 'blue'), (['give a key', 'passwd', 'set password'], 'green'),
           (['key rules', 'chage', 'expires every', '90 days'], 'amber'), (['new role', 'usermod', 'shell, name,', 'lock'], 'violet'),
           (['leave', 'lock first,', 'userdel -r', 'later'], 'red')]))
       + t(320, 160, 'Five steps of an account’s life,', 9.6, 'ink2')
       + t(320, 182, 'each with its own command.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('User management at four depths', [
    ('v', 'No jargon: hiring and leaving a company', '      <p>An account is like an employee record.</p>' + pic),
    ('b', 'The commands you will type', '''      <ul>
        <li><code>sudo useradd -m -s /bin/bash -c "Neha Rao" neha</code>: create.</li>
        <li><code>sudo passwd neha</code>: set her password (type it twice, nothing is shown).</li>
        <li><code>sudo usermod -s /bin/zsh neha</code>: change something later.</li>
        <li><code>sudo userdel -r neha</code>: remove the account and her home.</li>
      </ul>'''),
    ('i', 'Defaults, skeleton and ageing', '''      <ul>
        <li>useradd’s defaults come from <code>/etc/default/useradd</code> (<code>useradd -D</code>) and <code>/etc/login.defs</code> (UID range, home creation, password ageing defaults).</li>
        <li><code>-m</code> copies the files from <code>/etc/skel</code> (.bashrc, .profile) into the new home.</li>
        <li><code>chage</code> sets password ageing in /etc/shadow: <code>-M</code> max days, <code>-m</code> min, <code>-W</code> warning, <code>-I</code> inactive, <code>-E</code> account expiry, <code>-d 0</code> force change.</li>
        <li>Locking: <code>passwd -l</code>/<code>usermod -L</code> put <code>!</code> before the hash, so the password stops working. SSH keys still work: also expire the account (<code>-e 1</code> or <code>chage -E 0</code>) or set shell nologin.</li>
      </ul>'''),
    ('a', 'Behind the screen: what useradd changes', '''      <ul>
        <li>useradd locks the account database (<code>/etc/passwd.lock</code> etc.), writes one line each to <code>/etc/passwd</code>, <code>/etc/shadow</code>, <code>/etc/group</code> and <code>/etc/gshadow</code> (the user private group), adds ranges to <code>/etc/subuid</code>/<code>/etc/subgid</code> for containers, then creates the home and copies /etc/skel.</li>
        <li>userdel removes those lines; <code>-r</code> also removes the home and mail spool. Files elsewhere (/srv, /tmp, crontabs in /var/spool/cron) keep the old UID: find them with <code>find / -uid N</code>. A new user can later get the same UID and inherit them.</li>
        <li><code>adduser</code> (Debian/Ubuntu) is a Perl front-end that calls useradd with friendly defaults (bash, home, prompts) and enforces lowercase names (NAME_REGEX). On RHEL, adduser is just a link to useradd.</li>
        <li>Never pass a password with <code>useradd -p</code> or on the command line: it must be a hash and it appears in process lists and history. Use <code>passwd</code> or <code>chpasswd</code> from a file/stdin.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>useradd, usermod, userdel, passwd and chage</h2>
''' + def_block(
    '<code>useradd</code> creates a user account (and optionally its home folder) from defaults plus the options you give. <code>usermod</code> changes an existing account. <code>userdel</code> removes an account. <code>passwd</code> sets, locks, unlocks or expires a password. <code>chage</code> changes password-ageing and account-expiry information. All of them edit /etc/passwd, /etc/shadow and /etc/group safely and need root.',
    'Create, change, disable and remove accounts without editing the account files by hand.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Home directory', 'The user’s own folder, /home/NAME.'),
    ('/etc/skel', 'Template files copied into every new home.'),
    ('Login shell', 'Program started at login: /bin/bash, nologin.'),
    ('Lock', 'Disable the password (! before the hash).'),
    ('Expire', 'Disable the whole account from a date.'),
    ('Ageing', 'Rules for how long a password is valid.'),
    ('User private group', 'A group with the same name, created per user.'),
    ('Orphan files', 'Files whose owner UID no longer exists.'),
]) + '\n' + names('Where the names come from.', [
    ('useradd', 'user add', 'Low-level, all distributions.'),
    ('adduser', 'add user', 'Friendly wrapper (Debian).'),
    ('usermod', 'user modify', 'Change an account.'),
    ('userdel', 'user delete', 'Remove an account.'),
    ('passwd', 'password', 'Set or change passwords.'),
    ('chage', 'change age', 'Password ageing.'),
    ('chpasswd', 'change passwords', 'Many at once from stdin.'),
    ('skel', 'skeleton', 'Starting files for a home.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Create', '<code>sudo useradd -m -s /bin/bash NAME</code>'),
    ('Password', '<code>sudo passwd NAME</code>'),
    ('Change at login', '<code>sudo chage -d 0 NAME</code>'),
    ('Lock', '<code>sudo usermod -L -e 1 NAME</code>'),
    ('Delete', '<code>sudo userdel -r NAME</code>'),
    ('Defaults', '<code>useradd -D</code>'),
]) + '\n' + lv + didyou('On Ubuntu, <code>useradd</code> without <code>-s</code> gives new users <code>/bin/sh</code> (dash): no arrow-key history, no tab completion. That is the most common “my new user’s terminal is broken” ticket.') + '''
EXAM> “Create user tom with UID 2000, home, bash, member of wheel, password expiring in 60 days.” → <code>useradd -m -u 2000 -s /bin/bash -G wheel tom; passwd tom; chage -M 60 tom</code>.
''' + qc('What do you lose if you forget <code>-m</code>?', 'No home folder is created (and nothing from /etc/skel), so login lands in / and many programs fail to save settings.') + mistake('“useradd -m cdac creates a home directory at /home/john”  ·  “useradd -m -G developers Mohan”',
    'It creates <code>/home/cdac</code> (the account name). Use lowercase names (<code>mohan</code>): useradd on Ubuntu 24.04 accepts “Mohan”, but adduser refuses it and many tools assume lowercase. <code>-G developers</code> fails if the group does not exist yet: create it first (Lesson 8.3).',
    'Checked on Ubuntu 24.04: useradd -m Mohan succeeds; adduser Mohan is refused (NAME_REGEX); useradd -G developers x gives “group ‘developers’ does not exist” (exit 6).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>useradd vs adduser, and lock vs expire vs delete</h2>
''' + table(['', 'useradd', 'adduser (Debian/Ubuntu)'], [
    ['Style', 'options only, scriptable', 'interactive questions'],
    ['Home folder', 'only with <code>-m</code>', 'always'],
    ['Default shell (Ubuntu)', '/bin/sh', '/bin/bash'],
    ['Password', 'not set (account locked)', 'asked immediately'],
    ['Name check', 'permissive', 'lowercase only (NAME_REGEX)'],
    ['Available on', 'every distribution', 'Debian family; on RHEL adduser = useradd'],
    ['Use in', 'scripts, Ansible, cloud-init', 'one-off accounts by hand'],
], minw=520) + table(['Action', 'Command', 'Password', 'SSH keys', 'Files', 'Undo'], [
    ['Lock password', '<code>passwd -l</code> / <code>usermod -L</code>', 'stops', '<b>still work</b>', 'kept', '<code>-u</code> / <code>-U</code>'],
    ['Expire account', '<code>usermod -e 1</code> / <code>chage -E 0</code>', 'stops', 'stop', 'kept', '<code>chage -E -1</code>'],
    ['No shell', '<code>usermod -s /usr/sbin/nologin</code>', 'no shell', 'no shell', 'kept', 'set bash again'],
    ['Delete account', '<code>userdel</code>', 'gone', 'gone', 'home kept, orphaned', 'recreate (same UID!)'],
    ['Delete with home', '<code>userdel -r</code>', 'gone', 'gone', 'home and mail deleted', 'only from backup'],
], minw=620) + qc('A leaver logs in with an SSH key after you ran <code>passwd -l</code>. Why, and what do you add?', 'Locking only disables the password. Also expire the account (<code>usermod -e 1</code>) or set the shell to nologin, and remove ~/.ssh/authorized_keys.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine, where riya may use sudo. Each example starts from a clean state (test accounts removed first).</p>
''' + cmdcard_u(['every new person or service account', 'scripts and provisioning (Ansible, cloud-init)', 'exact control: UID, groups, home, expiry'],
               ['forgetting -m and -s on Ubuntu', 'passing passwords with -p'])(
    'useradd', 'useradd · adduser', 'create an account',
    'Creates the account from the defaults (<code>useradd -D</code>, <code>/etc/login.defs</code>) plus your options. The account has no usable password until you run passwd.',
    'sudo useradd [-m] [-s SHELL] [-c COMMENT] [-u UID] [-g GROUP] [-G G1,G2] [-d HOME] [-e YYYY-MM-DD] [-r] NAME', 'change',
    [('-m', 'create the home and copy /etc/skel', 'people'),
     ('-s /bin/bash', 'login shell', 'Ubuntu default is /bin/sh'),
     ('-c "Neha Rao"', 'comment (full name)', 'readable lists'),
     ('-u 1090', 'fixed UID', 'same UID on all servers'),
     ('-g GROUP', 'primary group', 'instead of a private group'),
     ('-G a,b', 'supplementary groups (must exist)', 'access'),
     ('-d /data/home/x', 'home elsewhere', 'big disks'),
     ('-e 2026-12-31', 'account expires', 'contractors, interns'),
     ('-r', 'system account (UID < 1000, no home)', 'services'),
     ('useradd -D', 'show defaults', 'before creating')],
    dict(setup=CLEAN, cmd='sudo useradd -m -s /bin/bash -c "Neha Rao" neha\ngetent passwd neha\nsudo ls -lA /home/neha\nsudo passwd -S neha', note='The home got the files from /etc/skel; it is private to Neha (owner neha, mode 750 on Ubuntu 24.04), so riya needs sudo to look inside. Status L: no password yet, so nobody can log in with one.'),
    [('sys', [
        dict(situation='The defaults: why a bare useradd surprises people.', setup=CLEAN, cmd='sudo useradd -D | grep -E "SHELL|HOME|SKEL"\nsudo useradd cdac\ngetent passwd cdac\nls -d /home/cdac 2>&1',
             expect='any', why='No -m: no home. No -s: /bin/sh. Both are the puzzle’s answer.'),
        dict(situation='Fixed UID, custom home and comment (consistent across servers).', setup=CLEAN, cmd='sudo mkdir -p /data/home\nsudo useradd -m -u 1090 -d /data/home/karan -s /bin/bash -c "Karan (DBA)" karan\nid karan; getent passwd karan',
             why='A fixed UID keeps file ownership correct on NFS and in backups (Lesson 8.1).')]),
     ('devops', [
        dict(situation='A service account for an app: no login, no home, system UID.', setup='sudo userdel myapp > /dev/null 2>&1', cmd='sudo useradd -r -s /usr/sbin/nologin -c "MyApp service" myapp\ngetent passwd myapp\nsudo -u myapp id; sudo userdel myapp',
             why='The service runs as myapp (systemd User=myapp, Lesson 17.3). If it is hacked, the attacker is not root.')]),
     ('sec', [
        dict(situation='Contractor account that stops working on its own.', setup=CLEAN, cmd='sudo useradd -m -s /bin/bash -e 2026-12-31 mohan\nsudo chage -l mohan | grep "Account expires"',
             why='No one has to remember to remove it in January.')]),
     ('dev', [
        dict(situation='The friendly way on Ubuntu (asks questions; here non-interactive).', setup=CLEAN, cmd='sudo adduser --disabled-password --gecos "Neha Rao" neha | tail -3\ngetent passwd neha',
             why='adduser picks bash and creates the home. It also adds the user to the users group.')]),
    ],
    anat=anatomy([('sudo useradd', 'cmd', 'create'), ('-m', 'opt', 'home'), ('-s /bin/bash', 'opt', 'shell'), ('-c "Neha Rao"', 'opt', 'comment'), ('neha', 'arg', 'login name')], 'Options before the name. The name: lowercase letters, digits, - and _.'),
    sudo=True
) + mistake('sudo useradd neha   (and nothing else)', 'sudo useradd -m -s /bin/bash -c "Neha Rao" neha && sudo passwd neha',
            'Without -m there is no home; without -s Ubuntu uses /bin/sh; without passwd the account is locked.') + cmdcard_u(['setting a first password or resetting a forgotten one', 'locking an account quickly', 'forcing a change at next login'],
               ['passwords on the command line or in scripts in plain text'])(
    'passwd', 'passwd · chpasswd', 'set, lock and expire passwords',
    '<code>passwd</code> changes your own password, or (as root) anyone’s. It also locks (<code>-l</code>), unlocks (<code>-u</code>), expires (<code>-e</code>) and shows status (<code>-S</code>). <code>chpasswd</code> sets many passwords from <code>name:password</code> lines on stdin.',
    'passwd   ·   sudo passwd [-l|-u|-e|-S|-d] NAME   ·   … | sudo chpasswd', 'change',
    [('passwd', 'change my own (asks old one)', 'every user'),
     ('sudo passwd NAME', 'set/reset another', 'help desk'),
     ('-S', 'status: P, L, NP + ageing', 'check'),
     ('-l / -u', 'lock / unlock the password', 'incidents'),
     ('-e', 'expire: must change at next login', 'temporary passwords'),
     ('-d', 'delete password (passwordless: dangerous)', 'almost never'),
     ("echo 'neha:Temp#2026' | sudo chpasswd", 'non-interactive', 'bulk onboarding')],
    dict(setup=CLEAN + '; sudo useradd -m -s /bin/bash neha', cmd="echo 'neha:Temp#2026' | sudo chpasswd\nsudo passwd -S neha\nsudo passwd -e neha\nsudo passwd -S neha", note='P = password set. After -e the change date is 1970 (day 0), so she must choose a new password at the next login.'),
    [('sys', [
        dict(situation='Lock and unlock (see the ! in shadow).', setup=CLEAN + "; sudo useradd -m neha; echo 'neha:Temp#2026' | sudo chpasswd", cmd="sudo passwd -l neha\nsudo grep '^neha:' /etc/shadow | cut -c1-12\nsudo passwd -u neha\nsudo grep '^neha:' /etc/shadow | cut -c1-12",
             why='Locking just puts ! in front of the hash; unlocking removes it. Nothing is lost.'),
        dict(situation='Unlocking an account that never had a password is refused.', setup=CLEAN + '; sudo useradd -m mohan', cmd='sudo passwd -l mohan; sudo passwd -u mohan; echo "exit $?"', expect='any',
             why='passwd protects you from creating a passwordless account. Set a password first.')]),
     ('devops', [
        dict(situation='Onboard several people from a file (passwords never typed on the command line).', setup=CLEAN + '; for u in neha mohan; do sudo useradd -m -s /bin/bash $u; done', cmd="printf 'neha:N3ha#Tmp\\nmohan:M0han#Tmp\\n' > new.txt\nsudo chpasswd < new.txt && shred -u new.txt\nfor u in neha mohan; do sudo passwd -e $u > /dev/null; sudo passwd -S $u; done",
             why='chpasswd reads stdin; shred removes the file afterwards. Each person must change the temporary password.')]),
    ],
    sudo=True
) + cmdcard_u(['password expiry policies', 'forcing a change at first login', 'account end dates'],
               ['very short max ages (people write passwords down)'])(
    'chage', 'chage', 'password ageing',
    'Shows and changes the ageing fields of /etc/shadow: last change, minimum and maximum days, warning, inactive days and account expiry.',
    'sudo chage [-l] [-d DAYS|0] [-m MIN] [-M MAX] [-W WARN] [-I INACTIVE] [-E DATE|-1] NAME', 'change',
    [('-l', 'list in plain English', 'check'),
     ('-d 0', 'must change at next login', 'first login'),
     ('-M 90', 'valid for 90 days', 'policy'),
     ('-m 1', 'no change again within 1 day', 'stop cycling back'),
     ('-W 7', 'warn 7 days before', 'friendly'),
     ('-I 14', 'lock 14 days after expiry', 'stale accounts'),
     ('-E 2026-12-31 / -E -1', 'account end date / never', 'contracts')],
    dict(setup=CLEAN + '; sudo useradd -m -s /bin/bash neha', cmd='sudo chage -M 90 -m 1 -W 7 -E 2026-12-31 neha\nsudo chage -l neha', note='Password valid 90 days from today’s change date, account ends on 31 December.'),
    [('sec', [
        dict(situation='Force a new password at first login.', setup=CLEAN + "; sudo useradd -m neha; echo 'neha:Temp#2026' | sudo chpasswd", cmd='sudo chage -d 0 neha\nsudo chage -l neha | head -2',
             why='The help desk knows the temporary password; only Neha knows the real one.')]),
     ('qa', [
        dict(situation='Test accounts that disappear by themselves.', setup=CLEAN + '; sudo useradd -m karan', cmd="sudo chage -E \"$(date -d '+7 days' +%F)\" karan\nsudo chage -l karan | grep 'Account expires'",
             why='date -d computes a date a week from now (Lesson 3.6).')]),
    ],
    sudo=True
) + cmdcard_u(['changing shell, comment, home, name or expiry', 'locking (-L) and unlocking (-U)', 'adding groups (with -a!)'],
               ['-G without -a (removes all other groups)', 'renaming while the user is logged in'])(
    'usermod', 'usermod', 'change an account',
    'Changes fields of an existing account. With <code>-G</code> it <b>replaces</b> the supplementary group list unless you add <code>-a</code> (append).',
    'sudo usermod [-s SHELL] [-c COMMENT] [-d HOME -m] [-l NEWNAME] [-L|-U] [-e DATE] [-aG GROUPS] NAME', 'change',
    [('-s /bin/bash', 'change shell', 'fix /bin/sh users'),
     ('-c "text"', 'change comment', 'names, teams'),
     ('-d /new -m', 'move the home', 'disk moves'),
     ('-l new old', 'rename the login', 'name changes'),
     ('-L / -U', 'lock / unlock password', 'like passwd -l/-u'),
     ('-e 1 / -e ""', 'expire now / never', 'leavers'),
     ('-aG docker', 'add to a group (keep others)', 'access'),
     ('-u 2000', 'change UID (home files follow)', 'rare, careful')],
    dict(setup=CLEAN + '; sudo useradd cdac', cmd='getent passwd cdac\nsudo usermod -s /bin/bash -c "CDAC Mumbai" cdac\ngetent passwd cdac', note='The /bin/sh user from the puzzle, fixed.'),
    [('sys', [
        dict(situation='Rename a login after a name change (home renamed too).', setup=CLEAN + '; sudo useradd -m -s /bin/bash mohan', cmd='sudo usermod -l karan -d /home/karan -m mohan\nid karan; ls -d /home/karan',
             why='-l renames the login; -d -m moves the home. The UID stays the same, so all files still belong to them. The private group is still called mohan (rename with groupmod -n).')]),
     ('sec', [
        dict(situation='Leaver: block password, keys and shell in one go, keep files.', setup=CLEAN + "; sudo useradd -m -s /bin/bash mohan; echo 'mohan:x1Y2z3!!' | sudo chpasswd", cmd='sudo usermod -L -e 1 -s /usr/sbin/nologin mohan\nsudo passwd -S mohan\nsudo chage -l mohan | grep "Account expires"\ngetent passwd mohan | cut -d: -f7',
             why='-e 1 = expired on 2 January 1970, so even SSH keys are refused. Reversible: usermod -U -e "" -s /bin/bash.')]),
    ],
    sudo=True
) + mistake('sudo usermod -G docker riya', 'sudo usermod -aG docker riya',
            'Without -a, -G replaces every supplementary group: riya silently loses sudo and every other group. More in Lesson 8.3.') + cmdcard_u(['removing accounts after offboarding is complete', 'cleaning up test accounts'],
               ['the first step for a leaver (lock first)', '-f on a logged-in user without stopping their processes'])(
    'userdel', 'userdel', 'remove an account',
    'Removes the account’s lines from the account files. <code>-r</code> also deletes the home folder and mail spool. Files elsewhere stay, owned by a bare number.',
    'sudo userdel [-r] [-f] NAME', 'danger',
    [('userdel NAME', 'account only, home kept', 'keep data'),
     ('-r', 'also home + mail spool', 'full removal'),
     ('-f', 'force, even if logged in', 'emergencies only'),
     ('pkill -u NAME', 'stop their processes first', 'clean removal'),
     ('find / -xdev -uid N', 'files left elsewhere', 'after deleting')],
    dict(setup=CLEAN + "; sudo useradd -m -s /bin/bash mohan; sudo -u mohan touch /home/mohan/notes.txt /tmp/mohan_report.txt", cmd='id -u mohan\nsudo userdel -r mohan\nls -d /home/mohan 2>&1; ls -ln /tmp/mohan_report.txt', expect='any', note='The home is gone (the “mail spool not found” message is a harmless warning), but /tmp/mohan_report.txt is now owned by the bare UID.'),
    [('sys', [
        dict(situation='Keep the files for the manager, then remove the account.', setup=CLEAN + "; sudo useradd -m -s /bin/bash mohan; sudo -u mohan mkdir /home/mohan/project; sudo -u mohan touch /home/mohan/project/plan.txt", cmd='sudo tar czf /tmp/mohan_home.tgz -C /home mohan\nsudo userdel mohan\nsudo ls -ln /home/mohan/project\nsudo chown -R riya: /home/mohan; ls -l /home/mohan/project; sudo rm -rf /home/mohan',
             why='Back up, delete the account without -r, hand the files to someone (chown, Lesson 9.3).')]),
     ('sec', [
        dict(situation='Find files left by a deleted account anywhere.', setup="sudo rm -rf /srv/shared; sudo mkdir -p /srv/shared; sudo useradd -m -u 1095 ghost > /dev/null 2>&1; sudo touch /srv/shared/ghost.log; sudo chown ghost: /srv/shared/ghost.log; sudo userdel -r ghost > /dev/null 2>&1", cmd='sudo find /srv -xdev -nouser -ls 2>/dev/null\nsudo rm -rf /srv/shared',
             why='On a real server search everything: <code>sudo find / -xdev -nouser</code>. A future user that gets UID 1095 would inherit these files. Delete or reassign them.')]),
    ],
    sudo=True
) + undo('Account changes are reversible, except deleting data.', [
    ('Locked the wrong user:', '<code>sudo usermod -U -e "" NAME</code> (and set the shell back).'),
    ('Removed a user but not -r:', 'recreate with the <b>same UID</b> (<code>useradd -u N</code>) and the old home works again.'),
    ('Ran userdel -r by mistake:', 'only a backup brings the home back. Take one first: <code>tar czf</code>.'),
    ('Lost all groups with usermod -G:', 'add them back with <code>usermod -aG</code>; check old memberships in <code>/etc/group-</code> (backup copy).'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='/usr/sbin/useradd neha', meaning='Only root may create accounts: it cannot lock /etc/passwd.', fix='<code>sudo useradd …</code>'),
    dict(cmd='sudo useradd riya', meaning='The account already exists (exit 9).', fix='Choose another name, or change it with usermod.'),
    dict(cmd='sudo useradd -G developers neha', meaning='-G names a group that does not exist (exit 6).', fix='<code>sudo groupadd developers</code> first (Lesson 8.3).'),
    dict(cmd='useradd -D', meaning='As a normal user, /usr/sbin (where admin tools live) is not in PATH.', fix='Use <code>sudo useradd …</code>; sudo’s secure_path includes /usr/sbin (Lesson 8.4).'),
    dict(cmd='sudo userdel nosuchuser', meaning='No such account (exit 6).', fix='Check with <code>getent passwd NAME</code>.'),
]) + qc('Order the offboarding steps: userdel -r, lock + expire, back up the home, hand files over.', 'Lock + expire → back up → hand files over → userdel -r (only when the manager agrees).') + '''
'''

SCREENS = screens_block('Real terminal screens: setting a password', 'passwd asks twice and shows nothing while you type. Here sudo sets Neha’s first password.',
    CLEAN + "; sudo useradd -m -s /bin/bash neha; printf '%s\\n' 'PS1=\"riya@web01:~$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'sudo passwd neha' Enter", ' after <code>sudo passwd neha</code>: it asks for the new password.'),
    ('Enter', "'Temp#2026' Enter 'Temp#2026' Enter", ' after typing the password twice (nothing appears on screen).'),
], 72, 9, hid='screens', what='bash')

cards = cards + SCREENS + '</section>\n'

def write(k, note, tone):
    files = ['/etc/passwd', '/etc/shadow', '/etc/group', '/home/neha']
    lines = ['neha:x:1002:1002::…:/bin/bash', 'neha:!:20768:0:99999:7:::', 'neha:x:1002:', '.bashrc .profile (from /etc/skel)']
    o = ''
    for i, f in enumerate(files):
        tn = 'green' if i < k else ('amber' if i == k else 'card')
        o += label_box(14, 8 + i * 32, 110, 26, [f], tn, 7.8)
        if i < k or i == k:
            o += t(134, 25 + i * 32, lines[i], 7.6, 'ink2', anchor='start')
    return o + t(180, 146, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ sudo useradd -m -s /bin/bash neha'] + ([('$', 'prompt')] if k == 3 else []), title='riya@web01', prompt='riya@web01:~$', size=8) + cap(c, '', 'card', y=150, h=34)
       for k, c in enumerate(['You press Enter…', '…no output…', '…still nothing…', '…done: silence means success.'])]
behind = [write(0, 'A line in /etc/passwd (UID picked from login.defs).', 'violet'), write(1, 'A locked line in /etc/shadow (no password yet).', 'violet'),
          write(2, 'A private group neha in /etc/group.', 'violet'), write(3, '-m: home created, /etc/skel copied in.', 'green')]
two = anim_two('What useradd really does', 'Behind the screen: four places change',
               'A terminal running sudo useradd -m -s /bin/bash neha with no output.',
               'Four boxes fill in turn: a passwd line, a locked shadow line, a group line and a home folder with skeleton files.', see, behind,
               ['Enter.', 'Unix tools are silent on success.', 'Check with getent and ls.', 'Next: passwd neha.'],
               ['1. /etc/passwd', '2. /etc/shadow (locked)', '3. /etc/group', '4. home + /etc/skel'])

def life(k, note, tone):
    st = [('created', 'L'), ('password', 'P'), ('locked', 'L'), ('expired', 'L + expiry'), ('deleted', '—')]
    o = ''
    for i, (a, b) in enumerate(st):
        tn = 'card'
        if i == k:
            tn = ['blue', 'green', 'amber', 'red', 'red'][i]
        o += label_box(8 + i * 70, 30, 64, 56, [a, b], tn, 7.8)
    return o + t(180, 126, note, 8.6, tone, bold=True)
frames = [life(0, 'useradd: account exists, password locked.', 'violet'), life(1, 'passwd: can log in.', 'green'), life(2, 'passwd -l: password refused, keys still work.', 'amber'),
          life(3, 'usermod -e 1: nothing works, files kept.', 'red'), life(4, 'userdel -r: gone; files elsewhere orphaned.', 'red')]
s1 = anim_one('Animated example', 'An account’s life, as passwd -S sees it',
              'Each step changes what passwd -S reports and what still works.',
              'account states', 'Five state boxes: created, password set, locked, expired and deleted, highlighted in turn.', frames,
              ['New: no password.', 'Usable.', 'Password blocked.', 'Fully disabled, reversible.', 'Irreversible.'], hid='scenario-life')

dx = dissect('Layer by layer: where useradd gets its defaults',
    'Each layer has a real command and output from our build machine.', [
    dict(key='opts', name='Your options', sub='-m -s -c -G', why='Win over everything.', how='Command line.', impl='useradd parses them.', used='Every account.',
         cmd="echo 'sudo useradd -m -s /bin/bash -c \"Neha\" neha'"),
    dict(key='default', name='/etc/default/useradd', sub='useradd -D', why='Shell, home base, skel.', how='Edit or useradd -D -s.', impl='Read by useradd.', used='Ubuntu sets SHELL=/bin/sh.',
         cmd='sudo useradd -D'),
    dict(key='logindefs', name='/etc/login.defs', sub='ranges and ageing', why='UID ranges, PASS_MAX_DAYS, CREATE_HOME.', how='System policy.', impl='Shadow utilities.', used='Policy.',
         cmd="grep -E '^(UID_MIN|UID_MAX|PASS_MAX_DAYS|PASS_MIN_DAYS|ENCRYPT_METHOD)' /etc/login.defs"),
    dict(key='skel', name='/etc/skel', sub='home template', why='Start-up files for every home.', how='Copied with -m.', impl='Plain files.', used='Company .bashrc.',
         cmd='ls -A /etc/skel'),
], hint='From your command to the system defaults. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What useradd writes, and an account’s life</h2>
''' + two + s1 + dx + qc('Your company wants every new home to contain a README. Where do you put it?', 'In /etc/skel: useradd -m copies it into each new home (existing homes are not changed).') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>User management at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['useradd -m', 'chage -d 0'], 'blue', 8.6), '1. Onboarding',
              'Help desks create accounts with a temporary password that must be changed at first login.', ['Ticket', '*useradd', 'welcome']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['usermod -L', '-e 1'], 'red', 8.6), '2. Offboarding',
    'On the last day, access is locked immediately; data is handed over and the account removed later.', ['Leaver', '*lock', 'userdel']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['useradd -r', 'nologin'], 'green', 8.6), '3. Service accounts',
    'Databases, web apps and agents run as system accounts with no login.', ['Install', '*useradd -r', 'run safely']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['chage -M', 'policy'], 'amber', 8.6), '4. Compliance',
    'Audits check password ageing and expiry dates for contractors.', ['Audit', '*chage -l', 'fix']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Ansible', 'user:'], 'violet', 8.6), '5. Automation',
    'Configuration tools run useradd/usermod for you, with the same options, on hundreds of servers.', ['YAML', '*useradd', 'fleet']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Defaults', scenario='What would useradd do?', cmd='sudo useradd -D', explain='/etc/default/useradd.'),
    dict(level='b', title='Skeleton files', scenario='What every new home gets.', cmd='ls -A /etc/skel', explain='Copied by -m.'),
    dict(level='i', title='Password status of all humans', scenario='Who has no password or is locked?', cmd="for u in $(awk -F: '$3>=1000 && $3<65534 {print $1}' /etc/passwd); do sudo passwd -S \"$u\"; done", explain='passwd -S per user.'),
    dict(level='i', title='Accounts with /bin/sh', scenario='Users created without -s.', cmd="awk -F: '$3>=1000 && $7==\"/bin/sh\" {print $1}' /etc/passwd; echo checked", explain='Fix with usermod -s.'),
    dict(level='a', title='Days until each password expires', scenario='Report for the auditor.', cmd="for u in riya aman; do printf '%-6s %s\\n' \"$u\" \"$(sudo chage -l \"$u\" | awk -F': ' '/^Password expires/ {print $2}')\"; done", explain='awk on chage -l.'),
], extra=build_up('onboarding Neha, start to finish', 'Riya creates Neha’s account the right way.', CLEAN, [
    ('sudo useradd -m -s /bin/bash -c "Neha Rao" neha', '1. Create with home, bash and a comment.'),
    ("echo 'neha:Temp#2026' | sudo chpasswd", '2. Temporary password.'),
    ('sudo chage -d 0 neha', '3. Must change it at first login.'),
    ('id neha; sudo passwd -S neha; sudo chage -l neha | head -1', '4. Check everything.'),
], cumulative=True)) + which('Choosing the right command.', [
    ('New person', 'useradd -m -s /bin/bash -c', 'Explicit.', 'Bare useradd.'),
    ('By hand on Ubuntu', 'adduser', 'Friendly.', 'Scripts (interactive).'),
    ('Service', 'useradd -r -s nologin', 'No login.', 'Running as root.'),
    ('First password', 'passwd / chpasswd + chage -d 0', 'User picks real one.', 'Emailing passwords.'),
    ('Leaver', 'usermod -L -e 1', 'Reversible.', 'userdel -r on day one.'),
    ('Add a group', 'usermod -aG', 'Keeps others.', 'usermod -G.'),
    ('Remove', 'userdel -r (after backup)', 'Clean.', 'Editing /etc/passwd.'),
]) + keys('Handy forms.', [
    ('useradd -D', 'defaults', 'check first'),
    ('passwd -S NAME', 'status', 'P L NP'),
    ('chage -l NAME', 'ageing', 'expiry'),
    ('usermod -L -e 1', 'disable fully', 'leavers'),
    ('find / -xdev -nouser', 'orphan files', 'after userdel'),
    ('pkill -u NAME', 'end their processes', 'before userdel'),
]) + scriptit('offboard.sh', 'A safe offboarding script: lock and expire, stop processes, archive the home, and only print the delete command for later.',
'''u=${1:-karan}
sudo useradd -m -s /bin/bash "$u" 2>/dev/null   # a test account, for this demo only
id "$u" > /dev/null 2>&1 || { echo "no such user: $u" >&2; exit 1; }
sudo usermod -L -e 1 -s /usr/sbin/nologin "$u"
sudo pkill -u "$u" 2>/dev/null || true
sudo tar czf "/tmp/${u}_home_$(date +%F).tgz" -C /home "$u"
echo "locked: $(sudo passwd -S "$u" | cut -d' ' -f2)  archive: $(ls /tmp/${u}_home_*.tgz)"
echo "when approved: sudo userdel -r $u"''',
'<p>Run with a test account; it never deletes anything by itself.</p>', expect='any') + puzzle_answer('The home is <code>/home/cdac</code> (the account name), not /home/john. And on Ubuntu useradd’s default shell is <code>/bin/sh</code>, which is why arrow keys printed <code>^[[A</code>: create with <code>-s /bin/bash</code>, or fix it with <code>sudo usermod -s /bin/bash cdac</code>.') + qc('Which option of useradd creates the home folder, and which file supplies its contents?', '<code>-m</code>; /etc/skel.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-users-and-groups-uid-gid-etc-passwd-etc-shadow/">Lesson 8.1</a> (passwd and shadow).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
