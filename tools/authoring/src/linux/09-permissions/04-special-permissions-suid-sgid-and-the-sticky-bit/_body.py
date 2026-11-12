import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

CL = 'sudo rm -rf /srv/team /srv/drop ~/sp; sudo groupdel analysts > /dev/null 2>&1'
TEAM = CL + '; sudo groupadd analysts; sudo usermod -aG analysts aman; sudo usermod -aG analysts riya; sudo mkdir /srv/team; sudo chown root:analysts /srv/team; sudo chmod 770 /srv/team'
SP = CL + '; mkdir -p ~/sp; cd ~/sp; cp /bin/id ./myid; touch data.txt'

HOOK = hook('/etc/shadow is readable only by root, yet every user can change their own password, which means writing to /etc/shadow. /tmp is writable by everyone, yet nobody can delete your files there. In a team folder, files created by Aman should belong to the team, not to Aman. Three puzzles, three special bits: <b>SUID</b>, the <b>sticky bit</b> and <b>SGID</b>. They are the 4th octal digit (<code>4755</code>, <code>1777</code>, <code>2770</code>), they show up as <code>s</code> and <code>t</code> in <code>ls -l</code>, and SUID is also a favourite target for attackers.',
    ['explain what SUID, SGID and the sticky bit do on files and on directories, and recognise <code>s S t T</code> in ls -l',
     'set and remove them with <code>chmod u+s g+s +t</code> and with 4-digit modes (4755, 2770, 1777)',
     'build a team folder where new files keep the team group (SGID) and a shared upload folder where users cannot delete each other’s files (sticky)',
     'find SUID/SGID programs for a security audit and explain why SUID shell scripts are ignored'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three puzzles'),
    ('decide', 'Which bit when?', 2, 'the quick chart'),
    ('definition', 'What the bits do', 6, 'simple meaning + 4 depths'),
    ('types', 'The three bits compared', 4, 'files vs folders, s S t T'),
    ('commands', 'Each bit, by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'passwd becoming root'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'team and drop folders'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which bit? (decide in 5 seconds)', [
    ('A program must run with its owner’s rights (passwd)', 'chmod u+s PROG  /  4755', 'rare, risky'),
    ('A program must run with a group’s rights', 'chmod g+s PROG  /  2755', 'rare'),
    ('Team folder: new files keep the folder’s group', 'chmod g+s DIR  /  2770', 'very common'),
    ('Shared writable folder, no deleting others’ files', 'chmod +t DIR  /  1777 or 1770', '/tmp, uploads'),
    ('Remove a special bit', 'chmod u-s / g-s / -t', 'hardening'),
    ('Find SUID programs (audit)', 'find / -xdev -perm -4000 -type f', 'security'),
    ('Find SGID programs', 'find / -xdev -perm -2000 -type f', 'security'),
    ('See the 4th digit', 'stat -c %a FILE', '4755, 2770, 1777'),
])

cmap = concept_map(
    [('9.1', 'Reading permissions', 'rwx, x on folders'), ('9.2', 'chmod', 'letters and digits'), ('9.3', 'chown and umask', 'group of new files')],
    ['SUID: run as the file’s owner', 'SGID on files and on folders', 'sticky bit: only owners delete', 's S t T in ls -l; 4-digit modes', 'finding and removing special bits'],
    [('8.4', 'sudo', 'an SUID program'), ('9.5', 'ACLs', 'finer sharing'), ('15.3', 'Mounting', 'nosuid'), ('13.4', 'Admin one-liners', 'audits')],
    'Three extra bits change how a program runs (SUID, SGID) and how a folder behaves (SGID, sticky). They solve real problems and must be audited.')

sc = (term(20, 14, 316, 156, ['$ ls -l /usr/bin/passwd', ('-rwsr-xr-x 1 root root … passwd', 'acc'), '$ ls -ld /tmp /srv/team', ('drwxrwxrwt 17 root root … /tmp', 'acc'), ('drwxrws--- 2 root analysts … /srv/team', 'acc'), '$ stat -c %a /tmp', ('1777', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Three special bits:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• s in owner x: SUID (4)', '• s in group x: SGID (2)', '• t in others x: sticky (1)', '• 4th digit: 4755 2770 1777', '• audit SUID often'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>How does passwd write a root-only file?</h2>
  <div class="story">
''' + puzzle('Riya writes a script <code>whoami.sh</code> containing <code>id</code>, makes it <code>chmod 4755</code> and owned by root, expecting it to print uid=0. It prints uid=1000. Meanwhile her colleague sets <code>chmod u+s report.txt</code> on a data file and sees <code>-rwSr--r--</code> with a capital S. Is SUID broken?') + '''
    <p class="narration">A security review of a shared server. Riya walks the new auditor through it.</p>
''' + scene('A terminal: passwd shows rws (SUID), /tmp shows rwt (sticky, 1777), a team folder shows rws in the group (SGID).', sc,
            '<tspan font-weight="700" class="s-acc">s</tspan> and <tspan font-weight="700" class="s-acc">t</tspan> replace x in ls -l.') + '''
K> /etc/shadow is root-only. How does a normal user’s passwd command change it?
A> Look at passwd: <code>-rwsr-xr-x root</code>. The s means SUID: whoever runs it, the program runs as its owner, root. passwd is written very carefully to change only <b>your</b> line.
R> And /tmp? Everyone can write there.
A> The t at the end is the sticky bit: in such a folder you may only delete or rename your own files. And the s in the group part of /srv/team (SGID) makes new files inherit the team group. Today: all three, how to set them, and how to audit them.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Three pictures: a bank teller’s badge that lets anyone’s request be processed with bank authority (SUID); a team room where every document placed inside gets the team stamp (SGID on a folder); a shared locker room where anyone can put a bag but only the owner can take it out (sticky).">'
       + label_box(14, 20, 190, 110, ['SUID: the teller', 'you ask, the bank', 'acts with its own', 'authority (owner)'], 'red', 8.6)
       + label_box(224, 20, 190, 110, ['SGID folder: team room', 'every paper put', 'inside gets the', 'team stamp (group)'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['sticky: lockers', 'anyone may put a bag,', 'only its owner', 'may take it out'], 'amber', 8.6)
       + t(320, 160, 'One changes who a program runs as; two change', 9.6, 'ink2')
       + t(320, 182, 'how a folder treats the files inside it.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Special bits at four depths', [
    ('v', 'No jargon: teller, team room, lockers', '      <p>Three special rules.</p>' + pic),
    ('b', 'What you will see and type', '''      <ul>
        <li><code>-rwsr-xr-x root … passwd</code>: s in the owner part = SUID.</li>
        <li><code>drwxrwsr-x … team</code>: s in the group part = SGID.</li>
        <li><code>drwxrwxrwt … /tmp</code>: t in the others part = sticky.</li>
        <li><code>chmod g+s /srv/team</code>, <code>chmod +t /srv/drop</code>, <code>chmod u+s prog</code>.</li>
      </ul>'''),
    ('i', 'What each bit does, and the 4th digit', '''      <ul>
        <li><b>SUID (4)</b> on an executable: the process runs with the file owner’s UID (effective UID). On folders: ignored on Linux.</li>
        <li><b>SGID (2)</b> on an executable: runs with the file’s group. On a folder: new files and subfolders get the <b>folder’s group</b>, and new subfolders get SGID too.</li>
        <li><b>Sticky (1)</b> on a folder: a file inside can be deleted or renamed only by its owner, the folder’s owner, or root. On files: ignored today.</li>
        <li>4-digit modes: first digit = 4 SUID + 2 SGID + 1 sticky: <code>4755</code>, <code>2770</code>, <code>1777</code>, <code>3770</code> (SGID + sticky).</li>
        <li>Capital <code>S</code>/<code>T</code> = the special bit is set but the x under it is not (usually a mistake).</li>
      </ul>'''),
    ('a', 'Behind the screen: effective UID, scripts and nosuid', '''      <ul>
        <li>On <code>execve()</code> of an SUID file the kernel sets the process’s <b>effective UID</b> to the file owner; the real UID stays yours, so the program knows who called it (<code>getuid()</code> vs <code>geteuid()</code>). sudo, su, passwd, mount and ping-like tools work this way.</li>
        <li>Linux <b>ignores SUID/SGID on interpreted scripts</b> (#! files) because of race conditions; only binaries honour them. That is the puzzle.</li>
        <li>Writing to an SUID file, or a chgrp by a normal user, clears the bits. Mounts with <code>nosuid</code> (often /tmp, USB disks) ignore them entirely.</li>
        <li>Modern systems replace many SUID programs with <b>capabilities</b> (<code>getcap /usr/bin/ping</code> → cap_net_raw), which grant one privilege instead of full root.</li>
        <li>Every SUID-root program is an attack surface: a bug in it is a root exploit. Audits list them (<code>find -perm -4000</code>) and compare with a baseline.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>SUID, SGID and the sticky bit</h2>
''' + def_block(
    '<b>SUID</b> (set user ID, 4000) on an executable makes it run with the privileges of the file’s owner. <b>SGID</b> (set group ID, 2000) on an executable makes it run with the file’s group; on a directory it makes new files inherit the directory’s group. The <b>sticky bit</b> (1000) on a directory allows only a file’s owner, the directory’s owner or root to delete or rename files inside it.',
    'Let normal users do one privileged job safely, keep team files in the team group, and protect shared folders.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Effective UID', 'The identity a process acts with (root for SUID-root).'),
    ('Real UID', 'Who actually started the process.'),
    ('Special bits', 'The 4th octal digit: 4 SUID, 2 SGID, 1 sticky.'),
    ('s / S', 'Special bit with / without x underneath.'),
    ('t / T', 'Sticky with / without x for others.'),
    ('nosuid', 'Mount option that ignores SUID/SGID.'),
    ('Capability', 'One root privilege granted alone (cap_net_raw).'),
    ('Privilege escalation', 'Becoming root through a bug or misconfiguration.'),
]) + '\n' + names('Where the names come from.', [
    ('SUID', 'set user ID', 'Patented by Dennis Ritchie (1979).'),
    ('SGID', 'set group ID', 'Same idea for groups.'),
    ('sticky', 'sticky text', 'Once: keep a program’s code in memory.'),
    ('4000/2000/1000', 'octal bits', 'The 4th digit.'),
    ('passwd', 'password', 'The classic SUID program.'),
    ('/tmp', 'temporary', 'The classic sticky folder.'),
    ('setgid dir', 'BSD semantics', 'Group inheritance.'),
    ('GTFOBins', 'list of escapes', 'Abusable SUID programs.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('SUID', '<code>chmod u+s f</code> / <b>4</b>755'),
    ('SGID folder', '<code>chmod g+s d</code> / <b>2</b>770'),
    ('Sticky', '<code>chmod +t d</code> / <b>1</b>777'),
    ('/tmp', '<b>1777</b> drwxrwxrwt'),
    ('Audit', '<code>find / -perm -4000</code>'),
    ('Scripts', 'SUID <b>ignored</b>'),
]) + '\n' + lv + didyou('The sticky bit got its name from early Unix, where it told the system to keep (“stick”) a program’s code in swap memory for faster starts. Linux ignores that meaning; only the folder meaning survives.') + '''
EXAM> “Create /shared owned by group devs so that new files get group devs and users cannot delete each other’s files.” → <code>chgrp devs /shared; chmod 3770 /shared</code> (2 SGID + 1 sticky).
''' + qc('What does <code>drwxrwxrwt</code> allow, and forbid?', 'Everyone may create files; only the owner of a file (or the folder owner or root) may delete or rename it.') + mistake('chmod u+s myscript.sh  (to make a script run as root)',
    'Use a sudo rule for that script (Lesson 8.4), or a small compiled wrapper reviewed by security.',
    'Linux ignores SUID on scripts (#!). Recorded below: a 4755 root-owned script still prints uid=1000.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The three bits compared</h2>
''' + table(['', 'SUID (4)', 'SGID (2)', 'Sticky (1)'], [
    ['On an executable file', 'runs as the file’s owner', 'runs with the file’s group', 'ignored'],
    ['On a directory', 'ignored (Linux)', 'new files get the folder’s group', 'only owners may delete/rename'],
    ['Shown in', 'owner x: <code>rws</code> / <code>rwS</code>', 'group x: <code>rws</code> / <code>rwS</code>', 'others x: <code>rwt</code> / <code>rwT</code>'],
    ['Set with', '<code>u+s</code>, 4xxx', '<code>g+s</code>, 2xxx', '<code>+t</code> / <code>o+t</code>, 1xxx'],
    ['Classic example', '/usr/bin/passwd, sudo', 'team folders; /usr/bin/chage (group shadow)', '/tmp, /var/tmp'],
    ['Risk', 'high (root bugs)', 'medium', 'low'],
], minw=620) + table(['Mode', 'ls -l', 'Meaning'], [
    ['4755', '-rwsr-xr-x', 'SUID program'],
    ['2755', '-rwxr-sr-x', 'SGID program'],
    ['2770', 'drwxrws---', 'team folder'],
    ['1777', 'drwxrwxrwt', '/tmp-style folder'],
    ['3770', 'drwxrws--T', 'team folder + no deleting others’ files'],
    ['4644', '-rwSr--r--', 'SUID without x: meaningless (capital S)'],
], minw=440) + qc('<code>ls -l</code> shows <code>-rwSr--r--</code>. What is wrong?', 'SUID is set but the owner has no x, so it cannot run anyway. Usually a mistake: chmod u-s.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each bit explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine. riya and aman share a group <code>analysts</code> where a team folder is needed.</p>
''' + cmdcard_u(['understanding passwd, sudo, su, mount', 'security audits', 'rare, reviewed programs that need one root action'],
               ['your own scripts (ignored)', 'any program that can start a shell or edit files'])(
    'suid', 'SUID (u+s, 4xxx)', 'run as the owner',
    'On an executable, the process gets the <b>file owner’s</b> effective UID while it runs. Shown as <code>s</code> in the owner’s x position.',
    'chmod u+s FILE   ·   chmod 4755 FILE   ·   chmod u-s FILE   ·   find / -xdev -perm -4000 -type f', 'danger',
    [('ls -l /usr/bin/passwd', 'rws: SUID root', 'the classic'),
     ('chmod u+s f', 'set SUID', 'rare'),
     ('chmod 4755 f', 'SUID + 755', 'same'),
     ('chmod u-s f', 'remove', 'hardening'),
     ('find / -xdev -perm -4000', 'list all SUID files', 'audit'),
     ('getcap -r /usr/bin', 'capabilities instead', 'modern way')],
    dict(cmd="ls -l /usr/bin/passwd /usr/bin/sudo /usr/bin/su\nstat -c '%a %n' /usr/bin/passwd", note='The s in rws, and 4755: these run as root for every user.'),
    [('sec', [
        dict(situation='Audit: every SUID program on the system.', cmd="find /usr /bin /sbin -xdev -perm -4000 -type f 2>/dev/null | sort",
             why='Keep this list as a baseline; a new entry (for example in /tmp or /home) is a red flag.'),
        dict(situation='SUID on a copied binary: it runs as the owner (here riya, so harmless).', setup=SP, cmd="cd ~/sp; chmod u+s myid; ls -l myid\nsudo -u aman ./myid",
             why='aman runs it, but euid=1000(riya): the effective UID comes from the file owner. Owned by root this would be a root shell risk.')]),
     ('sys', [
        dict(situation='Why can a normal user change their password?', cmd="ls -l /etc/shadow /usr/bin/passwd",
             why='shadow is root-only; passwd is SUID root and checks your old password before writing only your line.')]),
     ('dev', [
        dict(situation='SUID on a script is ignored (the puzzle).', setup=SP, cmd="cd ~/sp; printf '#!/bin/sh\\nid -u\\n' > whoami.sh; sudo chown root: whoami.sh; sudo chmod 4755 whoami.sh\nls -l whoami.sh; ./whoami.sh; sudo rm whoami.sh",
             why='Root-owned, 4755, and still prints 1000. Use a sudo rule instead (Lesson 8.4).')]),
    ]
) + cmdcard_u(['team folders where all files must belong to the team', 'programs that need a group’s rights (rare)'],
               ['relying on it for permissions: it only sets the group, not g+w'])(
    'sgid', 'SGID (g+s, 2xxx)', 'inherit the group',
    'On a <b>folder</b>: new files and subfolders get the folder’s group (subfolders also get SGID). On a program: it runs with the file’s group. Shown as <code>s</code> in the group’s x position.',
    'chmod g+s DIR   ·   chmod 2770 DIR   ·   chmod g-s DIR', 'change',
    [('chmod g+s dir', 'group inheritance', 'teams'),
     ('chmod 2770 dir', 'SGID + rwxrwx---', 'private team folder'),
     ('chmod 2775 dir', 'SGID + others read', 'shared'),
     ('ls -ld dir', 'rws in the group part', 'check'),
     ('find / -perm -2000', 'SGID files', 'audit')],
    dict(setup=TEAM, cmd="sudo -u aman touch /srv/team/before.csv\nsudo chmod g+s /srv/team\nsudo -u aman touch /srv/team/after.csv\nls -ld /srv/team; sudo ls -l /srv/team", note='Before SGID, aman’s file got his own group; after, the team group analysts.'),
    [('data', [
        dict(situation='A full team folder: SGID + group write + umask 002.', setup=TEAM, cmd="sudo chmod 2770 /srv/team\nsudo -u aman sh -c 'umask 002; echo a > /srv/team/sales.csv'\nsh -c 'umask 002; echo more >> /srv/team/sales.csv' && sudo ls -l /srv/team",
             why='The file belongs to analysts and is group-writable, so riya can append to aman’s file. This finishes the folder from Lesson 9.3.')]),
     ('devops', [
        dict(situation='Subfolders inherit SGID automatically.', setup=TEAM + '; sudo chmod 2770 /srv/team', cmd="sudo -u aman mkdir /srv/team/2026\nsudo ls -ld /srv/team/2026",
             why='rws in the group part: the whole tree keeps the team group, even folders made later.')]),
     ('sys', [
        dict(situation='An SGID program: chage runs with group shadow to read /etc/shadow.', cmd="ls -l /usr/bin/chage /etc/shadow",
             why='Group shadow may read shadow; SGID shadow gives chage exactly that, not full root.')]),
    ]
) + cmdcard_u(['shared folders where many users write', 'uploads and drop boxes', '/tmp-like scratch areas'],
               ['folders where a team must delete each other’s files'])(
    'sticky', 'Sticky bit (+t, 1xxx)', 'only owners delete',
    'On a folder that others can write to, only a file’s owner, the folder’s owner or root may delete or rename the file. Shown as <code>t</code> in the others’ x position.',
    'chmod +t DIR   ·   chmod 1777 DIR   ·   chmod 1770 DIR   ·   chmod -t DIR', 'change',
    [('ls -ld /tmp', 'drwxrwxrwt', 'the classic'),
     ('chmod +t dir', 'set', 'shared folders'),
     ('chmod 1777 dir', 'everyone writes, owners delete', 'scratch'),
     ('chmod 3770 dir', 'SGID + sticky', 'team drop box'),
     ('chmod -t dir', 'remove', 'rare')],
    dict(cmd="ls -ld /tmp /var/tmp\nsudo -u aman touch /tmp/aman_note\nrm -f /tmp/aman_note; echo \"exit $?\"\nsudo rm /tmp/aman_note", expect='any', note='riya can write to /tmp but cannot delete aman’s file there: “Operation not permitted”.'),
    [('web', [
        dict(situation='An upload folder for several apps: without and with the sticky bit.', setup=CL, cmd="sudo mkdir /srv/drop; sudo chmod 777 /srv/drop\nsudo -u aman touch /srv/drop/aman.pdf; rm /srv/drop/aman.pdf && echo 'deleted aman.pdf (777: bad)'\nsudo chmod 1777 /srv/drop; sudo -u aman touch /srv/drop/aman2.pdf\nrm -f /srv/drop/aman2.pdf; echo \"with sticky: exit $?\"", expect='any',
             why='In a plain 777 folder anyone deletes anything (w on the folder is enough). The sticky bit stops that.')]),
     ('sec', [
        dict(situation='Find world-writable folders without the sticky bit (risky).', setup=CL + '; sudo mkdir /srv/drop; sudo chmod 777 /srv/drop', cmd="sudo find /srv -xdev -type d -perm -0002 ! -perm -1000",
             why='Every hit lets users delete each other’s files. On a real server search / (with -xdev). Fix with chmod +t (or remove o+w).')]),
    ]
) + mistake('chmod 777 /shared   (for a folder many users write to)', 'chmod 1777 /shared   (or better: a group + 3770)',
            'Without the sticky bit, write permission on a folder lets every user delete or replace every file in it.') + undo('Special bits are removed like any other bit.', [
    ('Unwanted SUID/SGID on a file:', '<code>chmod u-s,g-s FILE</code> (or a 3-digit mode, which clears them for files).'),
    ('A folder lost SGID:', '<code>chmod g+s DIR</code>, then fix existing files: <code>chgrp -R TEAM DIR</code>.'),
    ('Capital S or T:', 'add the x (chmod u+x / o+x) or remove the special bit.'),
    ('Unknown SUID file found:', 'do not run it; check <code>dpkg -S FILE</code> (package?), remove the bit, investigate.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="sudo -u aman touch /tmp/aman_x; rm /tmp/aman_x", meaning='Sticky folder: only the owner may delete (EPERM).', fix='Ask the owner, or root.'),
    dict(cmd="chmod u+s /usr/bin/passwd", meaning='Not your file (EPERM).', fix='Only root changes special bits on system files (and should not).'),
    dict(cmd="sudo -u aman touch /srv/team/x", setup=TEAM + '; sudo chmod 2750 /srv/team', meaning='SGID does not give write permission: the group has no w.', fix='chmod g+w (2770).'),
]) + qc('Which mode makes a team folder where files keep the team group and nobody deletes another’s file?', '3770 (or 3775): SGID + sticky + rwxrwx---.') + '''
'''

SCREENS = screens_block('Real terminal screens: the sticky bit in /tmp', 'aman creates a file in /tmp; riya tries to delete it.',
    "sudo rm -f /tmp/report_aman; sudo -u aman touch /tmp/report_aman; printf '%s\\n' 'PS1=\"riya@web01:~$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'ls -ld /tmp; ls -l /tmp/report_aman' Enter", ' after listing: /tmp is drwxrwxrwt, the file belongs to aman.'),
    ('Enter', "'rm -f /tmp/report_aman' Enter", ' after rm -f: refused even with -f.'),
], 74, 9, hid='screens', what='bash')

cards = cards + SCREENS + '</section>\n'

def run(k, note, tone):
    o = label_box(14, 14, 100, 44, ['riya runs', 'passwd'], 'blue', 8)
    o += arrow(116, 36, 132, 36)
    o += label_box(134, 14, 96, 44, ['file is', 'rws root'], 'amber' if k >= 1 else 'card', 8)
    o += arrow(232, 36, 248, 36)
    o += label_box(250, 14, 96, 44, ['euid = 0', 'ruid = 1000'] if k >= 2 else ['euid = 1000', 'ruid = 1000'], 'red' if k >= 2 else 'card', 8)
    if k >= 3:
        o += label_box(80, 74, 200, 32, ['writes only riya’s line in /etc/shadow'], 'green', 7.6)
    return o + t(180, 130, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ passwd'] + ([('Current password:', 'dim')] if k >= 1 else []) + ([('New password:', 'dim')] if k >= 2 else []) + ([('passwd: password updated successfully', 'out')] if k == 3 else []), title='riya@web01', prompt='riya@web01:~$', size=8) + cap(c, '', 'card', y=150, h=34)
       for k, c in enumerate(['riya types passwd…', '…it asks for her password…', '…and the new one…', '…updated, although shadow is root-only.'])]
behind = [run(0, 'A normal process: euid 1000.', 'violet'), run(1, 'execve sees the SUID bit on a root file.', 'amber'),
          run(2, 'Effective UID becomes 0; real UID stays 1000.', 'red'), run(3, 'passwd uses root rights only for riya’s line.', 'green')]
two = anim_two('How SUID works', 'Behind the screen: effective vs real UID',
               'A terminal: riya runs passwd and changes her password.',
               'Boxes: riya runs passwd, the file is SUID root, the process gets effective UID 0 and real UID 1000, and writes only her line in shadow.', see, behind,
               ['Start.', 'Old password.', 'New password.', 'Done.'],
               ['1. euid 1000', '2. rws root', '3. euid 0', '4. limited write'])

def sticky(k, note, tone):
    o = label_box(14, 14, 130, 46, ['/tmp', 'drwxrwxrwt' if k >= 2 else 'drwxrwxrwx'], 'amber' if k >= 2 else 'card', 8)
    o += label_box(160, 14, 90, 46, ['aman.pdf', 'owner aman'], 'blue', 8)
    o += label_box(262, 14, 86, 46, ['riya:', 'rm aman.pdf'], 'card', 8)
    res = {0: '', 1: 'deleted! (w on folder)', 2: '', 3: 'Operation not permitted'}[k]
    if res:
        o += label_box(90, 74, 180, 30, [res], 'red' if k == 1 else 'green', 8)
    return o + t(180, 130, note, 8.6, tone, bold=True)
frames = [sticky(0, 'A 777 folder: aman’s file inside.', 'violet'), sticky(1, 'Without t: riya deletes it (only folder w counts).', 'red'),
          sticky(2, 'chmod +t: the folder becomes rwt.', 'amber'), sticky(3, 'Now only aman (or root) may delete it.', 'green')]
s1 = anim_one('Animated example', 'The sticky bit protects shared folders',
              'Deleting is about the folder, so the folder needs the protection.',
              'sticky bit', 'A world-writable folder with aman’s file: without the sticky bit riya deletes it; with it, she is refused.', frames,
              ['Shared folder.', 'Danger.', 'Sticky.', 'Protected.'], hid='scenario-sticky')

dx = dissect('Layer by layer: the 4th digit',
    'Each layer has a real command and output from our build machine.', [
    dict(key='digits', name='4th digit', sub='4 2 1', why='SUID, SGID, sticky.', how='First of four digits.', impl='Bits 04000 02000 01000.', used='4755 2770 1777.',
         cmd="touch a b; mkdir c; chmod 4755 a; chmod 2755 b; chmod 1777 c; stat -c '%a %A %n' a b c"),
    dict(key='caps', name='s vs S, t vs T', sub='x underneath?', why='Shows a missing x.', how='Capital = no x.', impl='ls rendering.', used='Spot mistakes.',
         cmd="touch d; mkdir e; chmod 4644 d; chmod 1770 e; ls -ld d e"),
    dict(key='exec', name='Exec rule', sub='binaries only', why='Scripts are ignored.', how='Kernel at execve.', impl='Race-condition safety.', used='Security.',
         cmd="printf '#!/bin/sh\\nid -u\\n' > s.sh; chmod 4755 s.sh; ls -l s.sh; ./s.sh"),
    dict(key='caps2', name='Capabilities', sub='the modern way', why='One privilege, not all of root.', how='getcap / setcap.', impl='xattrs.', used='ping, servers.',
         cmd="getcap -r /usr/bin /usr/sbin 2>/dev/null | head -3; echo \"(SUID-root files: $(find /usr/bin /usr/sbin -perm -4000 -type f | wc -l))\""),
], hint='From digits to the kernel. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How SUID works, and how the sticky bit protects</h2>
''' + two + s1 + dx + qc('Why is <code>/usr/bin/sudo</code> SUID root?', 'It must start as root to switch to UID 0 after checking the sudoers rules (Lesson 8.4).') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Special bits at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['2770', 'team dirs'], 'green', 8.6), '1. Team folders',
              'SGID folders keep every file in the team group; with umask 002 everyone can edit.', ['Team', '*chmod g+s', 'shared']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['1777', '/tmp'], 'amber', 8.6), '2. Shared scratch',
    '/tmp, /var/tmp and upload folders use the sticky bit.', ['Users', '*chmod +t', 'safe']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-perm -4000', 'audit'], 'red', 8.6), '3. Security audits',
    'SUID/SGID lists are compared with a baseline; unknown entries are investigated.', ['Scan', '*find', 'baseline']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['nosuid', 'mounts'], 'blue', 8.6), '4. Hardening',
    '/tmp, /home and USB mounts use nosuid so planted SUID files do nothing.', ['fstab', '*nosuid', 'contained']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['setcap', 'ping'], 'violet', 8.6), '5. Capabilities',
    'Programs needing one privilege (bind port 80, raw sockets) get a capability, not SUID root.', ['Need', '*setcap', 'least privilege']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Is /tmp sticky?', scenario='Check the t.', cmd="stat -c '%a %A' /tmp", explain='1777.'),
    dict(level='b', title='SUID programs count', scenario='How many?', cmd="find /usr/bin -perm -4000 -type f | wc -l", explain='-perm -4000.'),
    dict(level='i', title='SGID programs', scenario='List them.', cmd="find /usr/bin /usr/sbin -perm -2000 -type f -exec ls -l {} +", explain='-perm -2000.'),
    dict(level='i', title='Who owns each SUID file', scenario='root or not?', cmd="find /usr/bin -perm -4000 -type f -exec stat -c '%U %n' {} + | sort | head -5", explain='stat %U.'),
    dict(level='a', title='Compare with a baseline', scenario='Detect new SUID files.', setup=SP, cmd="find /usr/bin -perm -4000 -type f | sort > /tmp/base.txt\ncd ~/sp; chmod u+s myid\nfind /usr/bin ~/sp -perm -4000 -type f | sort | comm -13 /tmp/base.txt -", explain='comm -13 = only new (Lesson 6.3).'),
], extra=build_up('a team drop box', 'Riya builds a folder for analysts: files keep the group, nobody deletes another’s file.', TEAM, [
    ('sudo chmod 3770 /srv/team; ls -ld /srv/team', '1. SGID + sticky + rwxrwx---.'),
    ("sudo -u aman sh -c 'umask 002; echo a > /srv/team/aman.csv'", '2. aman adds a file.'),
    ("sudo ls -l /srv/team; sh -c 'echo b >> /srv/team/aman.csv' && echo 'riya can edit it'", '3. Group analysts, group-writable: riya may edit…'),
    ("rm -f /srv/team/aman.csv; echo \"…but not delete it: exit $?\"", '4. …but the sticky bit stops her deleting it.'),
], cumulative=True, expect='any')) + which('Choosing the right bit.', [
    ('Team files in team group', 'SGID on folder', 'Automatic.', 'chgrp by hand.'),
    ('Shared writable folder', 'sticky', 'No mutual deletes.', 'Plain 777.'),
    ('Script must run as root', 'sudo rule', 'Works, logged.', 'SUID script (ignored).'),
    ('Program needs one privilege', 'capability', 'Least privilege.', 'SUID root.'),
    ('Find risky files', 'find -perm -4000/-2000', 'Audit.', 'Hoping.'),
    ('Block planted SUID', 'mount nosuid', 'Contained.', 'Nothing.'),
]) + keys('Handy forms.', [
    ('chmod u+s / u-s', 'SUID on/off', 'programs'),
    ('chmod g+s DIR', 'group inheritance', 'teams'),
    ('chmod +t DIR', 'sticky', 'shared'),
    ('chmod 3770 DIR', 'team drop box', 'both'),
    ('find / -perm /6000', 'SUID or SGID', 'audit'),
    ("stat -c %a", 'see 4 digits', 'check'),
]) + scriptit('suid-audit.sh', 'A weekly audit: list SUID/SGID files with owner and package, and flag any that no package owns.',
'''for f in $(find /usr/bin /usr/sbin -xdev -perm /6000 -type f | sort); do
  pkg=$(dpkg -S "$f" 2>/dev/null | cut -d: -f1)
  printf '%-5s %-6s %-26s %s\\n' "$(stat -c %a "$f")" "$(stat -c %U "$f")" "$f" "${pkg:-UNKNOWN - investigate}"
done''',
'<p>dpkg -S tells which package installed a file (Lesson 14.2); a SUID file from no package is suspicious.</p>') + puzzle_answer('SUID is not broken: Linux <b>ignores SUID on scripts</b>, so the root-owned 4755 script runs as riya (uid 1000); use a sudo rule instead. The capital <b>S</b> means SUID is set but the owner has no x on report.txt, so it is meaningless: SUID only makes sense on executable programs.') + qc('Which command lists files that have SUID or SGID?', '<code>find / -xdev -perm /6000 -type f</code>') + '''
</section>
'''

_sh.run_sh(CL, 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-chmod-symbolic-and-numeric-modes-755-644-600/">Lesson 9.2</a> (chmod) and <a href="../03-ownership-and-defaults-chown-chgrp-and-umask/">9.3</a> (groups of new files).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
_sh.run_sh(CL + '; sudo gpasswd -d riya analysts > /dev/null 2>&1; true', 'any')
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
