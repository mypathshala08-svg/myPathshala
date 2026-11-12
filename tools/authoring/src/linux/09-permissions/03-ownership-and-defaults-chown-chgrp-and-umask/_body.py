import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

CL = 'sudo rm -rf /srv/reports /srv/www-demo ~/own; sudo groupdel analysts > /dev/null 2>&1'
OWN = CL + "; mkdir -p ~/own/sub; touch ~/own/a.txt ~/own/b.txt ~/own/sub/c.txt"
TEAM = CL + "; sudo groupadd analysts; sudo usermod -aG analysts aman; sudo usermod -aG analysts riya; sudo mkdir -p /srv/reports; sudo touch /srv/reports/q3.csv"

HOOK = hook('Aman leaves; his manager needs his 40 GB of project files, but they all belong to <code>aman</code>. A cron job running as root writes a log the web app then cannot read. A team shares a folder, yet every new file comes out <code>-rw-r--r--</code> so nobody else can edit it. These are not chmod problems: they are about <b>who owns</b> a file (<code>chown</code>, <code>chgrp</code>) and <b>what mode new files get</b> (<code>umask</code>).',
    ['explain owner and group ownership, and who is allowed to change them',
     'change owners and groups with <code>chown USER:GROUP</code>, <code>chown :GROUP</code>, <code>chgrp</code>, <code>-R</code>, <code>-h</code> and <code>--reference</code>',
     'calculate the mode of new files and folders from the umask (666/777 minus umask), and set it with <code>umask 022</code>, <code>027</code>, <code>002</code>, <code>077</code>',
     'fix the real cases: handing files over, files created by root, team folders, services that cannot read their files'])
ROAD = roadmap([
    ('story', 'The story', 3, 'files nobody can use'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'Ownership and umask', 6, 'simple meaning + 4 depths'),
    ('types', 'chown vs chgrp vs chmod', 3, 'and umask values'),
    ('commands', 'Each command, by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'umask subtracting bits'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'hand over and share'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('Give a file to another user', 'sudo chown aman FILE', 'root only'),
    ('Change owner and group together', 'sudo chown aman:finance FILE', ''),
    ('Change only the group', 'chgrp finance FILE  /  chown :finance FILE', 'owner may, if member'),
    ('A whole folder tree', 'sudo chown -R aman:aman DIR', 'hand-over'),
    ('Owner and the user’s own group', 'sudo chown aman: FILE', 'trailing colon'),
    ('Same owner as another file', 'chown --reference=GOOD FILE', 'consistency'),
    ('What mode will new files get?', 'umask  /  umask -S', '022 → 644 / 755'),
    ('Make new files private (this shell)', 'umask 077', '600 / 700'),
    ('Make new files team-writable', 'umask 002', '664 / 775'),
])

cmap = concept_map(
    [('8.1', 'Users and groups', 'UID, GID'), ('9.1', 'Reading permissions', 'owner and group columns'), ('9.2', 'chmod', 'modes')],
    ['owner and group of a file; who may change them', 'chown USER:GROUP, :GROUP, USER:, -R, -h', 'chgrp and when a normal user may use it', 'umask: default modes of new files', 'cp, mv, sudo and ownership'],
    [('9.4', 'SGID', 'team folders keep the group'), ('9.5', 'ACLs', 'default ACLs'), ('12.2', 'Startup files', 'where umask is set'), ('17.3', 'systemd', 'User=, UMask=')],
    'chmod decides what each class may do; chown and chgrp decide who is in each class; umask decides how new files start.')

sc = (term(20, 14, 316, 156, ['$ ls -l /home/aman/project', ('-rw-r--r-- 1 aman aman plan.xlsx', 'out'), '$ sudo chown -R priya: /home/aman/project', ('-rw-r--r-- 1 priya priya plan.xlsx', 'acc'), '$ umask', ('0022', 'out'), ('new files: 644, folders: 755', 'dim')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Who owns it, and', 9.4, 'acc', anchor='start', bold=True)
      + t(352, 52, 'how does it start?', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 72 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• chown: owner', '• chgrp: group', '• umask: new files', '• only root gives away', '• 666/777 − umask'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Files that belong to the wrong person</h2>
  <div class="story">
''' + puzzle('Riya runs <code>umask 027</code> and creates a file and a folder. A note says umask is “subtracted from 777”, so she expects the file to be 750, executable. <code>ls -l</code> shows <code>-rw-r-----</code> (640). Then she tries <code>chown aman report.txt</code> on her own file and gets “Operation not permitted”. Is umask arithmetic wrong, and why can’t she give away her own file?') + '''
    <p class="narration">Three tickets about the same idea: ownership.</p>
''' + scene('A terminal: aman’s project files are handed to priya with chown -R; umask shows 0022, meaning new files 644 and folders 755.', sc,
            'chown changes <tspan font-weight="700" class="s-acc">who</tspan>; umask decides how new files <tspan font-weight="700" class="s-acc">start</tspan>.') + '''
K> Can’t I just chmod 777 Aman’s files so Priya can use them?
A> Then everyone can use them, and Priya still is not the owner: she cannot chmod them or clean them up. The right fix is <code>sudo chown -R priya: …</code>. Only root may give a file away.
R> And our team folder, where every new file is read-only for the others?
A> That is the umask. With 022, new files start as 644. A team needs 002 (files 664) plus a shared group on the folder. Today: chown, chgrp and umask, and how they work together.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A house: the name on the deed is the owner (chown), the family that lives there is the group (chgrp), and the builder’s standard plan for every new room is the umask.">'
       + label_box(14, 20, 190, 110, ['deed of the house', 'owner = one person', 'chown aman', 'only the registrar (root)'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['household', 'group = one family', 'chgrp finance', 'owner may pick own families'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['builder’s standard', 'new rooms start with', 'all doors open, minus', 'what umask blocks'], 'amber', 8.6)
       + t(320, 160, 'Ownership says who is who; umask sets the first lock', 9.6, 'ink2')
       + t(320, 182, 'on every new file.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Ownership and umask at four depths', [
    ('v', 'No jargon: deed, family and builder', '      <p>A file is like a house.</p>' + pic),
    ('b', 'The commands you will type', '''      <ul>
        <li><code>sudo chown aman report.txt</code>: aman owns it now.</li>
        <li><code>sudo chown aman:finance report.txt</code>: owner and group together.</li>
        <li><code>chgrp finance report.txt</code>: only the group.</li>
        <li><code>sudo chown -R priya: /home/aman/project</code>: a whole folder, owner priya, group priya.</li>
        <li><code>umask</code>: see the default (0022 or 0002).</li>
      </ul>'''),
    ('i', 'Who may change what; how umask works', '''      <ul>
        <li>Only <b>root</b> may change a file’s owner (otherwise users could give files away to dodge disk quotas or frame others).</li>
        <li>The <b>owner</b> may change the group, but only to a group they belong to. Anyone else needs root.</li>
        <li>New files start from <b>666</b> (rw for all: programs never ask for x on data), new folders from <b>777</b>; the umask bits are <b>removed</b>: umask 022 → 644 / 755, 027 → 640 / 750, 077 → 600 / 700, 002 → 664 / 775.</li>
        <li>umask is a property of each process, inherited by children. Set it in <code>~/.bashrc</code> or <code>~/.profile</code>, for services with systemd <code>UMask=</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: chown(), umask() and inheritance', '''      <ul>
        <li>chown and chgrp use <code>fchownat()</code>. When a <b>normal user</b> changes the group of an SUID/SGID program, the kernel <b>clears those bits</b> (recorded below), so ownership tricks cannot create privileged programs.</li>
        <li>umask removes bits; it is not arithmetic subtraction. 027 removes w for group and rwx for others: from 666 that gives 640 (no x appears, because 666 had none).</li>
        <li>On Ubuntu, <code>pam_umask</code> with <code>USERGROUPS_ENAB yes</code> (login.defs) gives login sessions umask <b>0002</b> when the user’s group has the same name as the user; plain shells and services default to 0022.</li>
        <li>New files get the creator’s <b>effective UID</b> and primary GID (or the folder’s group if the folder has SGID, Lesson 9.4). So <code>sudo</code> creates root-owned files, a classic source of “I cannot edit my own file”.</li>
        <li>Default ACLs on a folder (9.5) override umask for files created inside it.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>chown, chgrp and umask</h2>
''' + def_block(
    '<code>chown</code> changes the owner and/or group of files (<code>USER</code>, <code>USER:GROUP</code>, <code>:GROUP</code>, <code>USER:</code>); only root may change the owner. <code>chgrp</code> changes only the group; the owner may do it if they are a member of the new group. The <b>umask</b> is a per-process mask of permission bits that are removed from the default mode (666 for files, 777 for directories) when new files are created.',
    'Make sure the right person and team own each file, and that new files start with safe permissions.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Owner', 'The user a file belongs to (st_uid).'),
    ('Group owner', 'The group a file belongs to (st_gid).'),
    ('umask', 'Bits removed from the mode of every new file.'),
    ('Default mode', '666 for files, 777 for folders, before umask.'),
    ('Hand-over', 'Giving files to another user with chown.'),
    ('Recursive', '-R: the folder and everything inside.'),
    ('Dereference', 'Follow a symbolic link (chown does by default; -h does not).'),
    ('Effective UID', 'The identity a process acts as (root under sudo).'),
]) + '\n' + names('Where the names come from.', [
    ('chown', 'change owner', 'Also changes the group.'),
    ('chgrp', 'change group', 'Group only.'),
    ('umask', 'user (file-creation) mask', 'Unix V7.'),
    ('USER:', 'trailing colon', 'Group = user’s login group.'),
    (':GROUP', 'leading colon', 'Group only (like chgrp).'),
    ('-h', 'no dereference', 'The link itself.'),
    ('-R', 'recursive', 'Whole tree.'),
    ('UMask=', 'systemd setting', 'For services.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Owner', '<code>sudo chown aman f</code>'),
    ('Both', '<code>sudo chown aman:finance f</code>'),
    ('Group', '<code>chgrp finance f</code>'),
    ('Tree', '<code>sudo chown -R aman: d</code>'),
    ('Show umask', '<code>umask</code> / <code>umask -S</code>'),
    ('022 gives', 'files <b>644</b>, folders <b>755</b>'),
]) + '\n' + lv + didyou('Copying a file with <code>cp</code> makes <b>you</b> the owner of the copy, even with <code>cp -p</code>, unless you are root. That is how ownership “resets” when users copy files around.') + '''
EXAM> “Make the user tom and group web the owners of /var/www/site, recursively.” → <code>chown -R tom:web /var/www/site</code>.
''' + qc('Your umask is 027. What modes do a new file and a new folder get?', 'File 640 (rw-r-----), folder 750 (rwxr-x---).') + mistake('“umask is subtracted from 777”, so umask 027 gives files 750',
    'Files start from 666, folders from 777, and umask <b>removes</b> bits: 027 gives files 640 and folders 750.',
    'Checked on our build machine: with umask 027, touch gives 640 and mkdir gives 750. Files never get x from umask alone.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>chown vs chgrp vs chmod, and common umask values</h2>
''' + table(['', 'chown', 'chgrp', 'chmod'], [
    ['Changes', 'owner (and group)', 'group only', 'permission bits'],
    ['Normal user may', 'no (root only)', 'yes, own files, to own groups', 'yes, own files'],
    ['Typical use', 'hand-over, files made by root', 'share with a team', 'who may do what'],
    ['Recursive', '-R', '-R', '-R'],
    ['Copy from a file', '--reference', '--reference', '--reference'],
], minw=520) + table(['umask', 'New file', 'New folder', 'Used for'], [
    ['022', '644 rw-r--r--', '755 rwxr-xr-x', 'default for services and root'],
    ['002', '664 rw-rw-r--', '775 rwxrwxr-x', 'Ubuntu login sessions, team work'],
    ['027', '640 rw-r-----', '750 rwxr-x---', 'servers: group reads, others nothing'],
    ['007', '660 rw-rw----', '770 rwxrwx---', 'private team folders'],
    ['077', '600 rw-------', '700 rwx------', 'private: secrets, keys'],
], minw=520) + table(['chown form', 'Owner', 'Group'], [
    ['<code>chown aman f</code>', 'aman', 'unchanged'],
    ['<code>chown aman:finance f</code>', 'aman', 'finance'],
    ['<code>chown aman: f</code>', 'aman', 'aman’s login group'],
    ['<code>chown :finance f</code>', 'unchanged', 'finance'],
], minw=400) + qc('Which command could a normal user run on their own file: chown aman f, chgrp finance f (she is in finance), or chgrp sudo f (she is not)?', 'Only chgrp finance f.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine. riya (in sudo) and aman are the users; a group <code>analysts</code> is created where needed.</p>
''' + cmdcard_u(['handing files to another user', 'fixing files created by root (sudo, cron)', 'service files owned by the service account'],
               ['giving away files without sudo (impossible)', '-R on system folders (/, /usr, /etc)'])(
    'chown', 'chown', 'change owner (and group)',
    'Sets the owner, the group, or both. Only root can change the owner. With <code>-R</code> it walks a tree; <code>-h</code> changes a symbolic link itself; <code>--reference=F</code> copies F’s owner and group.',
    'sudo chown [-R] [-h] [-v|-c] USER[:GROUP] FILE…   ·   chown :GROUP FILE   ·   chown --reference=F FILE', 'change',
    [('chown aman f', 'owner only', 'hand-over'),
     ('chown aman:finance f', 'owner and group', 'both'),
     ('chown aman: f', 'group = aman’s login group', 'personal files'),
     ('chown :finance f', 'group only', 'like chgrp'),
     ('-R', 'whole tree', 'folders'),
     ('-c / -v', 'report changes / all', 'audits'),
     ('-h', 'the link, not its target', 'symlinks'),
     ('--reference=F', 'same owner/group as F', 'consistency')],
    dict(setup=OWN, cmd="cd ~/own\nchown aman a.txt; echo \"exit $?\"\nsudo chown aman a.txt; sudo chown aman:finance b.txt\nls -l a.txt b.txt", expect='any', note='riya owns a.txt but cannot give it away. With sudo it works; b.txt got both an owner and a group.'),
    [('sys', [
        dict(situation='Hand a leaver’s project to a colleague.', setup=OWN + '; sudo chown -R aman:aman ~/own', cmd="sudo chown -R -c riya: ~/own | head -3\nls -l ~/own",
             why='The trailing colon sets the group to riya’s login group. -c lists what changed.')]),
     ('devops', [
        dict(situation='A file created with sudo belongs to root, so you cannot edit it.', setup=OWN, cmd="cd ~/own; sudo touch deploy.log\necho x >> deploy.log; echo \"exit $?\"\nsudo chown riya: deploy.log; echo ok >> deploy.log && ls -l deploy.log", expect='any',
             why='Files take the creator’s effective UID: under sudo that is root. Fix with chown, or avoid running editors and tools with sudo.')]),
     ('web', [
        dict(situation='Deploy files owned by a deploy user, readable by the web server group.', setup=CL, cmd="sudo mkdir -p /srv/www-demo/uploads; sudo touch /srv/www-demo/index.html\nsudo chown -R riya:www-data /srv/www-demo; sudo chown www-data /srv/www-demo/uploads\nsudo chmod 750 /srv/www-demo\nls -la /srv/www-demo",
             why='The web server reads through the group and writes only to uploads/. It does not own the code, so a hacked app cannot rewrite it.')]),
     ('dba', [
        dict(situation='Restored database files must belong to postgres.', setup=CL, cmd="sudo mkdir -p /srv/reports/pgrestore; sudo touch /srv/reports/pgrestore/base.dat\nsudo chown -R postgres:postgres /srv/reports/pgrestore; ls -l /srv/reports/pgrestore",
             why='Files restored as root would make PostgreSQL fail with “permission denied” on start.')]),
    ],
    anat=anatomy([('sudo chown', 'cmd', 'root only'), ('-R', 'opt', 'tree'), ('aman', 'arg', 'owner'), (':finance', 'opt', 'group'), ('project/', 'arg', 'target')], 'USER:GROUP with no spaces. USER: = login group. :GROUP = group only.'),
    sudo=True
) + mistake('chown -R aman /   ·   sudo chown -R aman: /home/aman/../', 'sudo chown -R aman: /home/aman/project   (an exact path, checked with ls first)',
            'A recursive chown on / or a mistyped path changes system files (sudo, passwd, /etc) and can make the system unbootable. Check the path, never use .. in recursive commands.') + cmdcard_u(['sharing a file with a team you belong to', 'scripts that set the group only'],
               ['changing to a group you are not in (needs sudo)'])(
    'chgrp', 'chgrp', 'change the group',
    'Changes only the group owner. A normal user may do it on files they own, to groups they are a member of.',
    'chgrp [-R] [-c] GROUP FILE…', 'change',
    [('chgrp finance f', 'group only', 'share'),
     ('-R', 'whole tree', 'folders'),
     ('-c', 'report changes', 'audits'),
     ('--reference=F', 'copy F’s group', 'consistency')],
    dict(setup=TEAM + '; touch ~/plan.txt', cmd="id -Gn\nchgrp sudo ~/plan.txt; ls -l ~/plan.txt\nchgrp finance ~/plan.txt; echo \"exit $?\"\nrm ~/plan.txt", expect='any', note='riya may move her file to sudo (she is a member) but not to finance (she is not).'),
    [('data', [
        dict(situation='Share a report folder with the analysts group.', setup=TEAM, cmd="sudo chgrp -R analysts /srv/reports; sudo chmod -R g+rw,o= /srv/reports\nls -la /srv/reports\nsudo -u aman sh -c 'echo row >> /srv/reports/q3.csv' && echo 'aman can write'",
             why='Group ownership + g+rw: every analyst may edit. (Lesson 9.4 adds SGID so new files keep the group.)')]),
    ]
) + cmdcard_u(['setting how new files start', 'private sessions (077)', 'team work (002)', 'services (systemd UMask=)'],
               ['expecting umask to change existing files (it only affects new ones)'])(
    'umask', 'umask', 'default mode of new files',
    'Shows or sets the mask of bits removed from new files (base 666) and new folders (base 777). It applies to the current shell and everything it starts.',
    'umask   ·   umask -S   ·   umask 022|027|002|077   ·   umask u=rwx,g=rx,o=', 'safe',
    [('umask', 'show (octal)', 'check'),
     ('umask -S', 'show as letters', 'readable'),
     ('umask 022', 'files 644, folders 755', 'default'),
     ('umask 027', 'files 640, folders 750', 'servers'),
     ('umask 077', 'files 600, folders 700', 'secrets'),
     ('umask 002', 'files 664, folders 775', 'teams'),
     ('(umask 077; cmd)', 'only for one command', 'subshell')],
    dict(setup=OWN, cmd="cd ~/own; umask\ntouch f1; mkdir d1\numask 027; touch f2; mkdir d2\numask 077; touch f3; mkdir d3\nstat -c '%a %n' f1 d1 f2 d2 f3 d3", note='The puzzle: with 027 the file is 640, not 750, because files start from 666.'),
    [('sec', [
        dict(situation='Create a secret that is private from the first moment.', setup=OWN, cmd="cd ~/own; (umask 077; echo 'token=abc' > api.token)\nstat -c '%a %n' api.token; umask",
             why='With umask 022 the file would exist as 644 for a moment before a chmod 600; a subshell with 077 avoids that window.')]),
     ('sys', [
        dict(situation='Login sessions on Ubuntu get 0002 (user private groups); plain shells 0022.', cmd="umask\nsudo su - riya -c umask\ngrep -E '^(UMASK|USERGROUPS_ENAB)' /etc/login.defs",
             why='pam_umask relaxes group bits when your group is your own private group. Services usually run with 0022.')]),
     ('devops', [
        dict(situation='A service’s umask is set in its unit, not in .bashrc.', cmd="printf '%s\\n' '[Service]' 'User=reports' 'UMask=0027' 'ExecStart=/usr/local/bin/report'",
             why='systemd starts services without your shell files (Lesson 17.3).')]),
    ]
) + mistake('Run umask 077 and expect existing files to become private', 'umask only affects files created afterwards; fix existing ones with chmod (9.2).',
            'umask is applied by the kernel at creation time (open with O_CREAT, mkdir). It never touches files that already exist.') + undo('Ownership changes are reversible if you know the old owner.', [
    ('Before a recursive chown:', "record owners: <code>find DIR -printf '%u:%g %p\\n' &gt; owners.txt</code>."),
    ('Wrong owner on a tree:', '<code>sudo chown -R RIGHT: DIR</code>; for mixed trees replay owners.txt.'),
    ('Ran chown -R on a system folder:', 'compare with a working system, or reinstall the affected packages (14.2); restore from backup.'),
    ('Wrong umask in .bashrc:', 'fix the line, open a new shell; existing files need chmod.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='touch f; chown aman f', meaning='Only root may change the owner (EPERM).', fix='<code>sudo chown aman f</code>.'),
    dict(cmd='touch f; chgrp finance f', meaning='riya is not a member of finance.', fix='Join the group (8.3) or use sudo.'),
    dict(cmd='touch f; sudo chown nosuchuser f', meaning='No such user.', fix='Check with <code>getent passwd</code>.'),
    dict(cmd='umask 999', meaning='Not an octal number.', fix='Digits 0–7, e.g. umask 027.'),
]) + qc('A file created by a root cron job must be readable by group www-data. Two fixes?', 'chown root:www-data + chmod 640 after creating it, or set the job’s umask (027) and run it as a user in that group.') + '''
'''

SCREENS = screens_block('Real terminal screens: umask in action', 'The same touch and mkdir, before and after changing the umask.',
    OWN + "; printf '%s\\n' 'PS1=\"riya@web01:~/own$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'cd ~/own; umask; touch x1; mkdir y1; ls -ld x1 y1' Enter", ' with the default umask 0022.'),
    ('Enter', "'umask 027; touch x2; mkdir y2; ls -ld x2 y2' Enter", ' after umask 027: others get nothing.'),
], 74, 12, hid='screens', what='bash')

cards = cards + SCREENS + '</section>\n'

def mask(k, um, note, tone):
    base = '666' if k < 2 else '777'
    res = ''.join(str(int(b) & ~int(u) & 7) for b, u in zip(base, um))
    o = label_box(14, 14, 100, 44, ['start', base + (' (file)' if k < 2 else ' (folder)')], 'blue', 8)
    o += t(124, 40, '−', 12, 'ink2', bold=True)
    o += label_box(134, 14, 90, 44, ['umask', um], 'amber', 8)
    o += t(232, 40, '=', 12, 'ink2', bold=True)
    o += label_box(244, 14, 104, 44, ['new mode', res], 'green', 8)
    return o + t(180, 100, note, 8.6, tone, bold=True)
fr = [('022', 'File: 666 with 022 removed = 644.'), ('027', 'File: 666 with 027 removed = 640 (no x!).'), ('022', 'Folder: 777 with 022 removed = 755.'), ('027', 'Folder: 777 with 027 removed = 750.')]
see = [term(14, 16, 332, 116, [f'$ umask {u}', '$ touch f' if k < 2 else '$ mkdir d', ('-rw-r--r-- f' if k == 0 else '-rw-r----- f' if k == 1 else 'drwxr-xr-x d' if k == 2 else 'drwxr-x--- d', 'out')], title='riya@web01', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34) for k, (u, n) in enumerate(fr)]
behind = [mask(k, u, n, 'violet' if k % 2 == 0 else 'green') for k, (u, n) in enumerate(fr)]
two = anim_two('How umask shapes new files', 'Behind the screen: start mode minus umask',
               'A terminal creating files and folders with umask 022 and 027.',
               'Three boxes: the start mode (666 for files, 777 for folders), the umask, and the resulting mode.', see, behind,
               ['File, 022.', 'File, 027.', 'Folder, 022.', 'Folder, 027.'],
               ['666 − 022 = 644', '666 − 027 = 640', '777 − 022 = 755', '777 − 027 = 750'])

def handover(k, note, tone):
    o = label_box(14, 20, 110, 56, ['/home/aman/', 'project', 'owner: ' + ('aman' if k < 2 else 'priya')], 'card' if k < 2 else 'green', 8)
    o += label_box(140, 20, 90, 56, ['aman', 'left'], 'red' if k >= 1 else 'blue', 8)
    o += label_box(246, 20, 100, 56, ['priya', 'can edit' if k >= 2 else 'denied'], 'green' if k >= 2 else 'amber', 8)
    return o + t(180, 110, note, 8.6, tone, bold=True)
frames = [handover(0, 'aman owns his project folder.', 'violet'), handover(1, 'aman leaves; priya is denied.', 'amber'),
          handover(2, 'sudo chown -R priya: … : priya owns everything.', 'green'), handover(3, 'priya can now chmod, edit and clean up.', 'green')]
s1 = anim_one('Animated example', 'A hand-over with chown -R',
              'Changing the owner moves the whole “owner” row of permissions to a new person.',
              'hand-over', 'A project folder owned by aman; after aman leaves, chown -R makes priya the owner and she gains access.', frames,
              ['Before.', 'Leaver.', 'chown -R.', 'Done.'], hid='scenario-handover')

dx = dissect('Layer by layer: where ownership comes from',
    'Each layer has a real command and output from our build machine.', [
    dict(key='proc', name='Creator', sub='effective UID/GID', why='New files take the creator’s identity.', how='sudo = root.', impl='Process credentials.', used='touch, editors, cron.',
         cmd="touch ~/mine; sudo touch ~/roots; ls -l ~/mine ~/roots; sudo rm ~/roots ~/mine"),
    dict(key='umask', name='umask', sub='per process', why='Starting mode.', how='Inherited by children.', impl='umask() syscall.', used='Every new file.',
         cmd="umask; bash -c umask; (umask 077; bash -c umask)"),
    dict(key='inode', name='Inode', sub='uid, gid', why='Stored with the file.', how='chown changes it.', impl='fchownat().', used='Every check.',
         cmd="touch ~/z; stat -c 'uid %u gid %g mode %a' ~/z; rm ~/z"),
    dict(key='suid', name='Safety rule', sub='chgrp clears SUID/SGID', why='No ownership tricks with privileged programs.', how='Kernel clears 4000/2000 when a normal user changes ownership.', impl='In fchownat().', used='Security.',
         cmd="cp /bin/true ~/tt; chmod 6755 ~/tt; stat -c %a ~/tt; chgrp sudo ~/tt; stat -c %a ~/tt; rm ~/tt"),
], hint='From the creating process to the inode. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How umask shapes new files, and a hand-over</h2>
''' + two + s1 + dx + qc('A team wants new files to be group-writable. Which umask?', '002 (files 664, folders 775), plus a shared group on the folder (SGID, 9.4).') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Ownership and umask at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['chown -R', 'hand-over'], 'blue', 8.6), '1. Leavers and hand-overs',
              'Files of departing staff are given to a manager or a project account.', ['Leaver', '*chown -R', 'continuity']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['root:root', 'from sudo'], 'red', 8.6), '2. “Cannot edit my file”',
    'Files made with sudo or by root cron jobs are handed back with chown.', ['Ticket', '*chown', 'fixed']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['postgres', 'www-data'], 'green', 8.6), '3. Service accounts',
    'Data owned by the service; code owned by a deploy user; group for read access.', ['Deploy', '*chown u:g', 'least privilege']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['umask 002', 'teams'], 'amber', 8.6), '4. Team work',
    'Shared folders combine a group, g+w and umask 002 (or default ACLs).', ['Team', '*chgrp', 'edit together']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['UMask=027', 'services'], 'violet', 8.6), '5. Hardening',
    'Servers use umask 027 so new files are never readable by everyone.', ['Policy', '*umask', 'safe defaults']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='My umask', scenario='As letters.', cmd='umask -S', explain='-S.'),
    dict(level='b', title='Owner and group', scenario='Of one file.', cmd="stat -c '%U:%G %n' /etc/shadow", explain='%U %G.'),
    dict(level='i', title='Files not owned by me in my home', scenario='Leftovers from sudo.', setup=OWN + '; sudo touch ~/own/rootfile', cmd="find ~ -xdev ! -user riya -ls 2>/dev/null | cut -c1-90", explain='! -user.'),
    dict(level='i', title='Give them back', scenario='Fix all at once.', setup=OWN + '; sudo touch ~/own/rootfile', cmd="sudo find ~ -xdev ! -user riya -exec chown -c riya: {} +", explain='find + chown.'),
    dict(level='a', title='Save and restore owners', scenario='Before a risky chown -R.', setup=OWN, cmd="cd ~/own; find . -printf '%u:%g %p\\n' > /tmp/owners.txt; sudo chown -R aman: .; while read -r o f; do sudo chown \"$o\" \"$f\"; done < /tmp/owners.txt; ls -l a.txt", explain='A manual undo.'),
], extra=build_up('a team reports folder', 'Riya builds a folder the analysts can all edit.', TEAM, [
    ('sudo chown -R root:analysts /srv/reports', '1. Group owner: analysts.'),
    ('sudo chmod -R u=rwX,g=rwX,o= /srv/reports', '2. Group may read and write; others nothing.'),
    ("ls -la /srv/reports", '3. Check.'),
    ("sudo -u aman sh -c 'umask 002; echo x > /srv/reports/new.csv' && ls -l /srv/reports/new.csv", '4. With umask 002 aman’s new file is group-writable (its group is still aman’s: SGID fixes that in 9.4).'),
], cumulative=True)) + which('Choosing the right command.', [
    ('Give away a file', 'sudo chown', 'Only root can.', 'chmod 777.'),
    ('Share with a team', 'chgrp + chmod g+', 'Exact group.', 'Others access.'),
    ('Files made by sudo', 'chown USER:', 'Back to you.', 'sudo editing forever.'),
    ('New files private', 'umask 077', 'From creation.', 'chmod after.'),
    ('Team defaults', 'umask 002 / default ACL', 'Group write.', 'Manual chmod.'),
    ('Services', 'systemd UMask=', 'Per service.', '.bashrc.'),
]) + keys('Handy forms.', [
    ('chown u: f', 'login group too', 'hand-over'),
    ('chown :g f', 'group only', 'like chgrp'),
    ('chown -R -c', 'report', 'audits'),
    ('umask -S', 'letters', 'readable'),
    ('(umask 077; cmd)', 'one command', 'secrets'),
    ('ls -ln', 'numbers', 'orphans'),
]) + scriptit('handover.sh', 'Hand a leaver’s project to a colleague: check both users, record old owners, change, and report.',
'''from=${1:-aman}; to=${2:-riya}; dir=${3:-$HOME/own}
for u in "$from" "$to"; do id "$u" > /dev/null 2>&1 || { echo "no such user: $u" >&2; exit 1; }; done
[ -d "$dir" ] || { echo "no such folder: $dir" >&2; exit 1; }
sudo find "$dir" -printf '%u:%g %p\\n' > /tmp/owners_before.txt
sudo chown -R "$to": "$dir"
echo "changed $(wc -l < /tmp/owners_before.txt) entries; now owned by: $(stat -c %U "$dir")"''',
'<p>Run on a sample folder.</p>') + puzzle_answer('umask arithmetic is right, the note is not: files start from <b>666</b> (folders from 777), so 027 gives a <b>640</b> file and a 750 folder; umask never adds x. And only <b>root</b> may change a file’s owner, even your own file: <code>sudo chown aman report.txt</code>.') + qc('What does <code>chown aman: f</code> do?', 'Owner aman, group aman’s login group.') + '''
</section>
'''

_sh.run_sh(OWN + '; sudo mkdir -p /srv/reports; sudo touch /srv/reports/q3.csv', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-chmod-symbolic-and-numeric-modes-755-644-600/">Lesson 9.2</a> (chmod).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
_sh.run_sh(CL + '; sudo gpasswd -d riya analysts > /dev/null 2>&1; true', 'any')
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
