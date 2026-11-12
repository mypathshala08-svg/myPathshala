import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# a small shared project: riya owns files, aman is "others" (he is not in group riya)
PROJ = r"""rm -rf ~/proj; mkdir -p ~/proj/docs ~/proj/private ~/proj/bin
echo 'quarterly numbers' > ~/proj/report.txt; echo 'db_pass=s3cret' > ~/proj/.env
printf '#!/bin/sh\necho deploying\n' > ~/proj/bin/deploy.sh; echo notes > ~/proj/docs/notes.md
chmod 644 ~/proj/report.txt; chmod 600 ~/proj/.env; chmod 755 ~/proj/bin/deploy.sh; chmod 700 ~/proj/private; chmod 755 ~/proj ~/proj/docs ~/proj/bin
chmod 711 ~; touch -d '2026-11-10 09:30' ~/proj/report.txt ~/proj/.env ~/proj/bin/deploy.sh ~/proj/docs/notes.md ~/proj/docs ~/proj/private ~/proj/bin"""
RESET = 'chmod 750 ~'

HOOK = hook('A deploy fails with “Permission denied” on a script the developer just wrote. A password file can be read by every user on the server. A web page returns 403 although the file is clearly there. All three are answered by ten characters you have seen a hundred times in <code>ls -l</code>: <code>-rw-r--r--</code>. Today you learn to read them like a sentence: <b>who</b> may do <b>what</b>, for files and, differently, for folders.',
    ['read every character of a permission string (<code>-rwxr-x---</code>) and the owner and group columns',
     'explain what r, w and x mean for a <b>file</b> and what they mean for a <b>directory</b> (they are different)',
     'work out, step by step, whether a given user can read, change or run a given file',
     'see permissions with <code>ls -l</code>, <code>ls -ld</code>, <code>stat</code> and <code>namei -l</code>, and decode “Permission denied”'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three Permission denied tickets'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'Permissions explained', 6, 'simple meaning + 4 depths'),
    ('types', 'Files vs directories', 4, 'r w x mean different things'),
    ('commands', 'Each command, by field', 14, 'ls -l, stat, namei'),
    ('animation', 'See it happen', 4, 'how the kernel decides'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'read and predict'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('Permissions of files in a folder', 'ls -l', 'the usual view'),
    ('Permissions of the folder itself', 'ls -ld DIR', 'not its contents'),
    ('Exact numbers (644) and owner', "stat -c '%A %a %U %G %n' FILE", 'scripts, audits'),
    ('Every folder on the way to a file', 'namei -l /path/to/file', '“why denied?”'),
    ('Can I read / write / run it?', '[ -r f ] / [ -w f ] / [ -x f ]', 'tests in scripts'),
    ('Who am I for this check?', 'id', 'owner? group? others?'),
    ('Change permissions', 'chmod (Lesson 9.2)', 'next lesson'),
    ('Change owner or group', 'chown / chgrp (9.3)', ''),
])

cmap = concept_map(
    [('8.1', 'Users and groups', 'UID, GID, id'), ('2.4', 'File types', 'ls -la, stat'), ('8.3', 'Groups', 'team access')],
    ['the 10-character mode: type + 3 × rwx', 'owner, group, others: who is who', 'r w x on files vs on directories', 'how the kernel checks: one class only', 'ls -l, ls -ld, stat, namei -l, test -r -w -x'],
    [('9.2', 'chmod', 'change rwx, 755, 644'), ('9.3', 'chown and umask', 'owners and defaults'), ('9.4', 'SUID, SGID, sticky', 's and t'), ('9.5', 'ACLs', 'more than three classes')],
    'Every file has one owner, one group and three sets of rwx. Reading them correctly answers most “Permission denied” questions without guessing.')

sc = (term(20, 14, 316, 156, ['$ ls -l', ('-rw-r--r-- 1 riya riya  18 report.txt', 'out'), ('-rw------- 1 riya riya  15 .env', 'out'), ('-rwxr-xr-x 1 riya riya  30 deploy.sh', 'out'), ('drwx------ 2 riya riya 4096 private', 'out'), ('$ sudo -u aman cat .env', 'prompt'), ('Permission denied', 'err')], title='riya@web01: ~/proj', prompt='riya@web01:~/proj$', size=7.0, step=15)
      + t(352, 36, 'Read it as a sentence:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• 1 char: file type', '• 3: owner can…', '• 3: group can…', '• 3: everyone else…', '• r read, w write, x run'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three “Permission denied” tickets before lunch</h2>
  <div class="story">
''' + puzzle('Riya’s folder <code>docs</code> has mode <code>drwxr--r--</code> (744). Aman is “others”, so he has <code>r</code>. He runs <code>ls docs</code> and sees the file name <code>notes.md</code>, but <code>cat docs/notes.md</code> says “Permission denied”, although notes.md itself is <code>-rw-r--r--</code>. How can he see the name and not open the file?') + '''
    <p class="narration">A project folder on a shared server. Riya owns it; Aman is a colleague in a different group.</p>
''' + scene('A terminal: ls -l shows report.txt readable by all, .env only by riya, deploy.sh executable, and a private folder; aman is denied reading .env.', sc,
            'Ten characters: <tspan font-weight="700" class="s-acc">type, owner, group, others</tspan>.') + '''
K> Aman can read report.txt but not .env. Same folder, same server. Why?
A> Read the first column: report.txt is <code>-rw-r--r--</code>, so everyone may read it. .env is <code>-rw-------</code>: only the owner, Riya. Aman is not the owner and not in group riya, so he gets the last three characters: <code>---</code>.
R> And folders? <code>private</code> also has rwx letters.
A> For folders the same letters mean something different: r = list names, w = create and delete names, x = go inside. Mixing those up is the classic mistake, and the puzzle above. Today: read permissions perfectly; changing them is next lesson.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A notice board on a room door with three rows: owner, team, visitors, each with three boxes read, write, enter; the guard checks which row you belong to and only that row.">'
       + label_box(14, 20, 190, 110, ['notice on the door', 'owner:  r w x', 'team:   r - x', 'others: - - -'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['the guard asks:', '1. are you the owner?', '2. else, in the team?', '3. else: visitor row'], 'amber', 8.6)
       + label_box(434, 20, 192, 110, ['only ONE row', 'applies to you,', 'even if another', 'row has more'], 'green', 8.6)
       + t(320, 160, 'r = read, w = write, x = run (file) or enter (folder).', 9.6, 'ink2')
       + t(320, 182, 'The guard checks your row, then your letter.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Permissions at four depths', [
    ('v', 'No jargon: a notice on a door', '      <p>Every file has a notice with three rows.</p>' + pic),
    ('b', 'Reading a line of ls -l', '''      <ul>
        <li><code>-rw-r--r-- 1 riya riya 18 report.txt</code></li>
        <li>1st character: type (<code>-</code> file, <code>d</code> directory, <code>l</code> link).</li>
        <li>Next 3: owner (riya) may <b>r</b>ead and <b>w</b>rite. Next 3: group riya may read. Last 3: everyone else may read.</li>
        <li>A <code>-</code> in a position means “not allowed”.</li>
      </ul>'''),
    ('i', 'Files vs folders, and the one-class rule', '''      <ul>
        <li>File: r = read contents, w = change contents, x = run it as a program.</li>
        <li>Folder: r = list the names, w = create, rename and delete entries (with x), x = enter it and reach things inside (“search”).</li>
        <li>Deleting a file needs <b>w on the folder</b>, not on the file.</li>
        <li>Linux picks <b>one</b> class: if you are the owner, only the owner bits count (even if “others” has more); else if you are in the group, the group bits; else others.</li>
        <li>To open <code>/a/b/c.txt</code> you need x on <code>/</code>, <code>/a</code> and <code>/a/b</code>, plus r on c.txt.</li>
      </ul>'''),
    ('a', 'Behind the screen: the mode word', '''      <ul>
        <li>The inode stores a 16-bit <b>mode</b>: 4 bits file type, 3 special bits (SUID, SGID, sticky: Lesson 9.4) and 9 permission bits. <code>stat -c %a</code> prints the permission part in octal (r=4, w=2, x=1).</li>
        <li>On every <code>open()</code>, <code>execve()</code> and path lookup the kernel compares the process’s effective UID/GIDs with the inode’s owner and group (<code>generic_permission()</code>). root (UID 0) skips the r/w checks, and needs at least one x bit to run a file.</li>
        <li>Permission is checked when a file is <b>opened</b>. A program that already has a file open keeps access after a chmod.</li>
        <li>A <code>+</code> after the mode (<code>-rw-r--r--+</code>) means an ACL adds more rules (9.5); a <code>.</code> means an SELinux context.</li>
        <li>x on a script is not enough: the interpreter must also read it, so a script needs r and x.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>File permissions: rwx for user, group and others</h2>
''' + def_block(
    'Every file and directory has an <b>owner</b> (a user), a <b>group</b>, and a <b>mode</b>: three sets of permission bits, read (r), write (w) and execute (x), for the owner (u), the group (g) and all others (o). When a process accesses the file, the kernel uses exactly one set (owner, else group, else others) and allows the action only if the needed bit is set.',
    'Decide who may read, change or run each file, and who may list, change or enter each folder.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Mode', 'The type + permission bits of a file.'),
    ('Owner (u)', 'The user who owns the file.'),
    ('Group (g)', 'The group the file belongs to.'),
    ('Others (o)', 'Everyone who is neither the owner nor in the group.'),
    ('r / w / x', 'Read, write, execute (files) or list, change, enter (folders).'),
    ('Octal', 'Writing rwx as a number: r=4, w=2, x=1, so rw- = 6.'),
    ('Permission denied', 'EACCES: the kernel refused the action.'),
    ('Path traversal', 'Needing x on every folder on the way to a file.'),
]) + '\n' + names('Where the names come from.', [
    ('rwx', 'read, write, execute', 'Unix, 1971.'),
    ('ugo', 'user, group, other', 'Used by chmod.'),
    ('mode', 'file mode', 'st_mode in stat.'),
    ('stat', 'status', 'Shows the inode.'),
    ('namei', 'name to inode', 'Follows a path.'),
    ('EACCES', 'error: access', '“Permission denied”.'),
    ('EPERM', 'error: permission', '“Operation not permitted”.'),
    ('octal', 'base 8', 'One digit per class.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('See files', '<code>ls -l</code>'),
    ('See the folder', '<code>ls -ld DIR</code>'),
    ('Numbers', "<code>stat -c '%a' FILE</code>"),
    ('Whole path', '<code>namei -l PATH</code>'),
    ('r w x', '<b>4 2 1</b>'),
    ('Delete a file', 'needs <b>w + x on the folder</b>'),
]) + '\n' + lv + didyou('On Ubuntu 24.04 new home folders are <code>drwxr-x---</code> (750): other users cannot even look inside your home. Older Ubuntu releases used 755, so everyone could read your files by default.') + '''
EXAM> “What does -rwxr-x--- mean?” → regular file; owner read, write, execute; group read and execute; others nothing. Octal 750.
''' + qc('A file is <code>-rw-r--r--</code> owned by riya. Can aman (not in group riya) change it?', 'No. Aman falls into “others”, which has only r.') + mistake('“The owner of a file can always do what others can”: -r--r--rw- lets the owner write',
    'Only one class is used. If you own a file with mode 0446 you get <code>r--</code> and cannot write, even though others have rw.',
    'Linux checks owner first and stops there. Strange modes like this are rare but appear in exam questions.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The same letters on files and on directories</h2>
''' + table(['Bit', 'On a file', 'On a directory', 'Without it (directory)'], [
    ['r', 'read the contents (cat, cp)', 'list names (ls)', 'ls fails, but known names can still be opened with x'],
    ['w', 'change the contents (edit, >)', 'create, rename, delete entries (needs x too)', 'cannot add or delete files'],
    ['x', 'run as a program', 'enter (cd) and reach anything inside', 'nothing inside is reachable at all'],
], minw=600) + table(['Character 1', 'Type', 'Example'], [
    ['<code>-</code>', 'regular file', 'report.txt'],
    ['<code>d</code>', 'directory', '/home/riya'],
    ['<code>l</code>', 'symbolic link (always shows rwxrwxrwx)', '/bin → usr/bin'],
    ['<code>c</code> / <code>b</code>', 'character / block device', '/dev/null, /dev/sda'],
    ['<code>s</code> / <code>p</code>', 'socket / named pipe', '/run/…sock, mkfifo'],
], minw=440) + table(['Mode', 'Octal', 'Typical for'], [
    ['<code>-rw-r--r--</code>', '644', 'normal files, web pages, configs'],
    ['<code>-rw-------</code>', '600', 'secrets: .env, SSH private keys'],
    ['<code>-rwxr-xr-x</code>', '755', 'scripts and programs; normal folders'],
    ['<code>drwx------</code>', '700', 'private folders: ~/.ssh'],
    ['<code>drwxr-x---</code>', '750', 'home folders (Ubuntu 24.04), team folders'],
    ['<code>-rw-rw-rw-</code> / <code>777</code>', '666 / 777', 'almost never: anyone can change it'],
], minw=480) + qc('Which bit on a directory lets you delete a file inside it?', 'w (together with x). The file’s own permissions do not matter for deleting (unless the sticky bit is set, Lesson 9.4).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine. riya owns <code>~/proj</code>; aman is a different user (not in group riya), so for him every file is “others”. Commands as aman use <code>sudo -u aman</code>.</p>
''' + cmdcard_u(['seeing who may do what in a folder', 'checking a file after creating or copying it', 'spotting secrets readable by everyone'],
               ['seeing a directory’s own permissions (use -d)'])(
    'ls-l', 'ls -l · ls -ld', 'see permissions',
    'The long listing: mode, link count, owner, group, size, time and name. <code>-d</code> shows the directory itself instead of its contents; <code>-a</code> includes hidden files; <code>-n</code> shows numeric UID/GID.',
    'ls -l [-a] [-d] [-n] [PATH…]', 'safe',
    [('ls -l', 'files in this folder', 'every day'),
     ('ls -la', 'including hidden (.env)', 'secrets'),
     ('ls -ld DIR', 'the folder itself', 'folder rights'),
     ('ls -ln', 'numbers instead of names', 'orphans, NFS'),
     ('ls -l /path/file', 'one file', 'quick check')],
    dict(setup=PROJ, cmd='cd ~/proj; ls -la\nls -ld ~ ~/proj/private', note='Mode, links, owner, group, size, date, name. The home folder is 711 here so aman can reach ~/proj.'),
    [('sec', [
        dict(situation='Secrets that others can read.', setup=PROJ + "; chmod 644 ~/proj/.env", cmd='cd ~/proj; ls -la .env\nsudo -u aman cat .env',
             why='Others has r, so any account (even the web server) can read the database password. Fix in Lesson 9.2: chmod 600.')]),
     ('web', [
        dict(situation='The web server (www-data) needs r on files and x on every folder.', setup=PROJ, cmd='ls -ld ~ ~/proj ~/proj/docs ~/proj/docs/notes.md\nsudo -u www-data cat ~/proj/docs/notes.md',
             why='www-data is “others” here: x on each folder plus r on the file. A 403 in Nginx is often a missing x on one folder.')]),
     ('dev', [
        dict(situation='Is my script executable?', setup=PROJ + '; chmod 644 ~/proj/bin/deploy.sh', cmd='cd ~/proj; ls -l bin/deploy.sh\n./bin/deploy.sh; echo "exit $?"', expect='any',
             why='No x, so the shell refuses (exit 126). chmod +x (Lesson 9.2) or run bash bin/deploy.sh.')]),
    ],
    anat=anatomy([('-', 'cmd', 'type'), ('rw-', 'arg', 'owner'), ('r--', 'opt', 'group'), ('r--', 'opt', 'others'), ('riya riya', 'arg', 'owner, group')], '-rw-r--r-- 1 riya riya 18 report.txt')
) + cmdcard_u(['exact octal modes for scripts and audits', 'owner and group as names or numbers', 'times and inode details'],
               ['quick looks (ls -l is shorter)'])(
    'stat', 'stat', 'the inode in detail',
    'Prints the inode’s information: size, inode number, links, mode in octal and letters, owner and group with numbers, and times. <code>-c FORMAT</code> prints only what you ask for.',
    "stat FILE   ·   stat -c '%A %a %U %G %n' FILE…", 'safe',
    [('stat FILE', 'everything', 'details'),
     ('%A / %a', 'mode as letters / octal', '-rw-r--r-- / 644'),
     ('%U %G', 'owner / group names', ''),
     ('%u %g', 'owner / group numbers', 'orphans'),
     ('%F', 'type in words', 'regular file'),
     ('%n', 'name', 'lists')],
    dict(setup=PROJ, cmd="cd ~/proj; stat report.txt | sed -n '1,4p'\nstat -c '%A %a %U %G %n' report.txt .env bin/deploy.sh private", note='Access: (0644/-rw-r--r--): the same permissions as letters and as a number. The leading 0 is the special-bits digit (Lesson 9.4).'),
    [('sec', [
        dict(situation='Audit: files in a folder that are not 600 or 644.', setup=PROJ, cmd="cd ~/proj; find . -type f -exec stat -c '%a %n' {} + | grep -Ev '^(600|644) '",
             why='Only the executable script is listed. Anything else unusual deserves a look.')]),
     ('devops', [
        dict(situation='A deployment check: the SSH key must be 600.', setup=PROJ, cmd="mkdir -p ~/.ssh; touch ~/.ssh/id_test; chmod 644 ~/.ssh/id_test\n[ \"$(stat -c %a ~/.ssh/id_test)\" = 600 ] && echo ok || echo \"bad mode $(stat -c %a ~/.ssh/id_test): ssh will refuse this key\"\nrm ~/.ssh/id_test",
             why='ssh refuses private keys that others can read (“UNPROTECTED PRIVATE KEY FILE”).')]),
    ]
) + cmdcard_u(['finding which folder on the way blocks access', 'web 403 and “Permission denied” on deep paths'],
               ['only one file (use ls -l)'])(
    'namei', 'namei -l · test -r -w -x', 'check the whole path',
    '<code>namei -l</code> lists every component of a path with its mode and owner, so you can see which folder is missing x. <code>[ -r FILE ]</code>, <code>-w</code> and <code>-x</code> test what <b>you</b> can do right now.',
    'namei -l PATH   ·   [ -r F ] && …   ·   test -w F', 'safe',
    [('namei -l PATH', 'every folder on the way', 'find the block'),
     ('namei -m PATH', 'modes only', 'short'),
     ('[ -r f ]', 'can I read it?', 'scripts'),
     ('[ -w f ]', 'can I write it?', 'before saving'),
     ('[ -x f ]', 'can I run it / enter it?', 'before calling')],
    dict(setup=PROJ, cmd='namei -l ~/proj/docs/notes.md', note='Each line is one step of the path. Others need x on every d line and r on the last line.'),
    [('web', [
        dict(situation='Why does aman get Permission denied? Find the folder.', setup=PROJ + '; chmod 700 ~/proj/docs', cmd="sudo -u aman cat ~/proj/docs/notes.md\nnamei -l ~/proj/docs/notes.md | grep -E '^d.......-'",
             expect='any', why='The only folder with no x for others is docs (drwx------): that is the block, not the file.')]),
     ('qa', [
        dict(situation='Test what each user can do, before shipping.', setup=PROJ, cmd="cd ~/proj; for u in riya aman; do printf '%-5s' $u; for f in report.txt .env bin/deploy.sh; do sudo -u $u test -r $f && printf ' r:%s' $f || printf ' -:%s' $f; done; echo; done",
             why='sudo -u USER test -r: an automated check of read access per user.')]),
    ]
) + mistake('chmod 777 to “fix” Permission denied', 'Find the real block with <code>namei -l</code> and <code>id</code>, then give the smallest right (often x on one folder or g+w for a team).',
            '777 lets every account, including a hacked web app, change the file. It hides the real cause and fails audits.') + undo('Reading permissions changes nothing; the risk is misreading them.', [
    ('Not sure which class you are:', 'compare <code>id</code> with the owner and group in <code>ls -l</code>.'),
    ('Folder looks fine but access fails:', '<code>namei -l</code> the full path; check x on every folder.'),
    ('A + at the end of the mode:', 'an ACL adds rules: <code>getfacl FILE</code> (Lesson 9.5).'),
    ('Permission denied as root:', 'check <code>lsattr</code> (immutable files, 9.5), read-only mounts, or SELinux/AppArmor.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="sudo -u aman cat /home/riya/proj/.env", setup=PROJ, meaning='aman is “others” and others have no r on .env (mode 600).', fix='Only if he should: give him group access (9.3) or an ACL (9.5).'),
    dict(cmd="sudo -u aman ls /home/riya/proj/private", setup=PROJ, meaning='No r (and no x) for others on the folder (700): cannot list it.', fix='chmod o+rx on the folder, if that is intended.'),
    dict(cmd="sudo -u aman touch /home/riya/proj/new.txt", setup=PROJ, meaning='No w on the folder for others: cannot create files there.', fix='Use a team folder with g+w (9.2, 9.4).'),
    dict(cmd="cd ~/proj && chmod 644 bin/deploy.sh && ./bin/deploy.sh", setup=PROJ, meaning='The file has no x: the shell will not run it (exit 126).', fix='<code>chmod +x bin/deploy.sh</code> (9.2).'),
]) + qc('Aman can <code>ls</code> a folder but cannot <code>cd</code> into it. Which bit is missing?', 'x on the folder for his class (he has r).') + '''
'''

SCREENS = screens_block('Real terminal screens: the folder puzzle', 'aman (others) on a folder with r but no x: he sees the names, but cannot reach the file.',
    PROJ + "; chmod 744 ~/proj/docs; printf '%s\\n' 'PS1=\"aman@web01:~$ \"' > /tmp/amanrc; chmod 644 /tmp/amanrc", 'sudo -u aman bash --rcfile /tmp/amanrc', [
    ('Enter', "'ls /home/riya/proj/docs' Enter", ' after <code>ls</code>: the name is listed, because others have r on docs.'),
    ('Enter', "'cat /home/riya/proj/docs/notes.md' Enter", ' after <code>cat</code>: denied, because there is no x on docs.'),
], 76, 9, hid='screens', what='bash')

import shlesson as _sh
_hood_out = _sh.run_sh(PROJ + "\nsudo -u aman strace -e trace=openat cat /home/riya/proj/.env 2>&1 | grep -E 'proj|^cat'", 'any').rstrip()
HOOD = f'''  <h3 id="hood">Under the hood: the kernel says EACCES</h3>
  <p>strace (run as aman) shows <code>cat</code> asking the kernel to open .env, and the kernel refusing with EACCES, the error code behind “Permission denied”.</p>
  <div class="code" data-lang="bash" data-file="Terminal"><pre><code>{E("strace -e trace=openat cat /home/riya/proj/.env")}</code></pre><div class="output">{E(_hood_out)}</div></div>
  <p class="muted">Recorded with <code>strace</code> on our Ubuntu build machine as aman; library loading lines are hidden.</p>
  <p>cat never sees the contents: the check happens inside <code>openat()</code>, before any data is read. The same check runs for every program, so no tool can “get around” it except by running as root or as the owner.</p>
'''

cards = cards + SCREENS + HOOD + '</section>\n' + f'<!-- reset -->'

def check(k, note, tone):
    rows = [('owner riya', 'rw-'), ('group riya', 'r--'), ('others', 'r--')]
    o = label_box(14, 10, 120, 36, ['aman wants', 'to WRITE report.txt'], 'blue', 7.8)
    for i, (who, bits) in enumerate(rows):
        tn = 'card'
        if i < k and k <= 3:
            tn = 'red'
        if i == k - 1 and k == 3:
            tn = 'amber'
        o += label_box(150, 6 + i * 36, 110, 30, [f'{who}: {bits}'], tn, 7.8)
    if k >= 4:
        o += label_box(270, 78, 80, 30, ['w? no → denied'], 'red', 7.8)
    return o + t(180, 140, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ echo hi >> report.txt'] + ([('Permission denied', 'err')] if k == 3 else []), title='aman@web01', prompt='aman@web01:~$', size=8) + cap(c, '', 'card', y=150, h=34)
       for k, c in enumerate(['Aman tries to append…', '…the kernel checks…', '…one class only…', '…and refuses.'])]
behind = [check(1, 'Is aman the owner (UID 1000)? No.', 'violet'), check(2, 'Is aman in group riya? No.', 'violet'),
          check(3, 'So the others row applies: r--.', 'amber'), check(4, 'Needed w, row has no w: EACCES.', 'red')]
two = anim_two('How the kernel decides', 'Behind the screen: owner, group or others?',
               'A terminal where aman appends to report.txt and gets Permission denied.',
               'Three rows owner, group, others; aman matches neither owner nor group, so the others row r-- is used and w is refused.', see, behind,
               ['Write attempt.', 'Check.', 'Check.', 'Denied.'],
               ['1. owner? no', '2. group? no', '3. others: r--', '4. no w → denied'])

def walk(k, note, tone):
    parts = [('/', 'r-x'), ('home', 'r-x'), ('riya', '--x'), ('proj', 'r-x'), ('docs', 'r--'), ('notes.md', 'r--')]
    o = ''
    for i, (n, b) in enumerate(parts):
        tn = 'card'
        if i < k:
            tn = 'green'
        if i == k:
            tn = 'red' if k == 4 else 'amber'
        o += label_box(4 + i * 59, 30, 55, 46, [n, b], tn, 7.6)
    return o + t(180, 120, note, 8.6, tone, bold=True)
frames = [walk(0, 'x on / for others: yes.', 'violet'), walk(2, '/home: x yes. /home/riya: --x: enough to pass.', 'green'),
          walk(3, 'proj: x yes.', 'green'), walk(4, 'docs: r-- (no x): stop. notes.md is never reached.', 'red')]
s1 = anim_one('Animated example', 'Walking a path: x on every folder',
              'To open a file, the kernel walks the path one folder at a time.',
              'path check', 'Six boxes for /, home, riya, proj, docs and notes.md with others’ bits; the walk stops at docs, which has r but no x.', frames,
              ['Start at /.', 'Folders need x, not r.', 'Still going.', 'Blocked: the puzzle.'], hid='scenario-walk')

dx = dissect('Layer by layer: where permissions live',
    'Each layer has a real command and output from our build machine.', [
    dict(key='name', name='Directory entry', sub='name → inode', why='Folders map names to inode numbers.', how='Changing names needs w on the folder.', impl='ls -i shows the numbers.', used='rm, mv.',
         cmd='cd; ls -i ~/proj | head -3' if False else "ls -id ~/proj ~/proj/report.txt", setup=PROJ),
    dict(key='inode', name='Inode', sub='owner, group, mode', why='One place per file.', how='stat reads it.', impl='16-bit mode.', used='Every check.',
         cmd="stat -c 'inode %i  uid %u  gid %g  mode %a (%A)' ~/proj/report.txt", setup=PROJ),
    dict(key='proc', name='Process', sub='who is asking', why='Effective UID and groups.', how='Set at login.', impl='/proc/self/status.', used='Compared with the inode.',
         cmd="grep -E '^(Uid|Gid|Groups)' /proc/self/status"),
    dict(key='kernel', name='Kernel check', sub='EACCES', why='One class, one bit.', how='On open, exec, lookup.', impl='generic_permission().', used='All programs.',
         cmd="sudo -u aman cat ~/proj/.env 2>&1; echo \"exit $?\"", setup=PROJ, expect='any'),
], hint='From the name to the kernel decision. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How the kernel decides, and why every folder needs x</h2>
''' + two + s1 + dx + qc('To read <code>/srv/app/conf/app.ini</code>, which bits does “others” need on each part?', 'x on /, /srv, /srv/app and /srv/app/conf, and r on app.ini.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Reading permissions at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['403', 'namei -l'], 'blue', 8.6), '1. Web 403 errors',
              'Admins trace which folder lacks x for www-data.', ['403', '*namei', 'fix one bit']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['.env 644?', 'stat'], 'red', 8.6), '2. Secret audits',
    'Security scans flag keys and .env files readable by others.', ['Scan', '*stat -c %a', '600']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['exit 126', 'no x'], 'green', 8.6), '3. Deploy failures',
    'CI jobs fail when a script lost its x bit in a zip or copy.', ['Fail', '*ls -l', 'chmod +x']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['postgres', '700 data'], 'amber', 8.6), '4. Databases',
    'Database servers refuse to start if their data folder is readable by others.', ['Start', '*ls -ld', '700']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ssh key', '600'], 'violet', 8.6), '5. SSH',
    'ssh refuses keys and configs that others can read or write.', ['Login', '*stat', 'fix']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Mode of one file', scenario='Octal.', cmd="stat -c %a /etc/passwd", explain='%a.'),
    dict(level='b', title='Folder itself', scenario='Not its contents.', cmd='ls -ld /tmp', explain='-d.'),
    dict(level='i', title='World-writable files here', scenario='Risky files.', setup=PROJ + '; chmod 666 ~/proj/report.txt', cmd="find ~/proj -type f -perm -o+w -exec ls -l {} +", explain='find -perm (Lesson 7.1).'),
    dict(level='i', title='Count by mode', scenario='What modes exist in /etc?', cmd="find /etc -maxdepth 1 -type f -exec stat -c %a {} + | sort | uniq -c | sort -rn | head -4", explain='stat + uniq -c.'),
    dict(level='a', title='Who can read it?', scenario='Every human account vs one file.', setup=PROJ, cmd="for u in riya aman www-data; do sudo -u $u test -r ~/proj/.env && echo \"$u: yes\" || echo \"$u: no\"; done", explain='test -r as each user.'),
], extra=build_up('diagnosing a 403', 'The web server cannot read a page. Riya finds the cause step by step.', PROJ + '; chmod 750 ~/proj/docs', [
    ('sudo -u www-data cat ~/proj/docs/notes.md', '1. Reproduce as the web user.'),
    ('ls -l ~/proj/docs/notes.md', '2. The file itself is fine (644).'),
    ('namei -l ~/proj/docs/notes.md', '3. Walk the path: docs is drwxr-x---.'),
    ('chmod o+x ~/proj/docs; sudo -u www-data cat ~/proj/docs/notes.md', '4. Give others x on that folder only.'),
], cumulative=True, expect='any')) + which('Choosing the right command.', [
    ('Files in a folder', 'ls -l', 'Short.', 'Guessing.'),
    ('The folder itself', 'ls -ld', 'Its own mode.', 'ls -l (shows contents).'),
    ('Exact octal', 'stat -c %a', 'Scripts.', 'Counting letters.'),
    ('Deep path denied', 'namei -l', 'Every folder.', 'chmod 777.'),
    ('Can user X read it?', 'sudo -u X test -r', 'Real answer.', 'Theory.'),
    ('Extra rules?', 'getfacl (9.5)', 'ACLs.', 'Ignoring the +.'),
]) + keys('Handy forms.', [
    ('ls -la', 'with hidden files', '.env'),
    ('ls -ld .', 'this folder', 'quick'),
    ('ls -ln', 'numeric owner', 'orphans'),
    ("stat -c '%A %a %n' *", 'modes of all', 'audits'),
    ('namei -l PATH', 'path check', '403'),
    ('id', 'my class', 'which row?'),
]) + scriptit('perm-explain.sh', 'Explain a mode in plain English: who may do what with a file.',
'''f=/etc/passwd
m=$(stat -c %A "$f")
echo "$f: $m (owner $(stat -c %U "$f"), group $(stat -c %G "$f"))"
for i in 0 1 2; do
  who=$(echo owner group others | cut -d' ' -f$((i+1)))
  bits=${m:$((1+i*3)):3}
  can=""
  [ "${bits:0:1}" = r ] && can="$can read"
  [ "${bits:1:1}" = w ] && can="$can write"
  [ "${bits:2:1}" = x ] && can="$can execute"
  echo "  $who:${can:- nothing}"
done''',
'<p>${m:1:3} takes three characters of the mode string (bash substring).</p>') + puzzle_answer('On a folder, r only lets you <b>list names</b>; reaching anything inside needs <b>x</b>. With <code>drwxr--r--</code> Aman (others) has r but no x, so <code>ls</code> shows “notes.md” (<code>ls -l</code> would add “cannot access” warnings for the details), but opening the file is denied before its own 644 mode is even checked.') + qc('A file shows <code>-rwxr-x---</code>. Write it in octal.', '750.') + '''
</section>
'''

import subprocess, shlesson
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../08-users-and-groups/01-users-and-groups-uid-gid-etc-passwd-etc-shadow/">Lesson 8.1</a> (UIDs and groups).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
shlesson.run_sh(RESET, 'any')
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
