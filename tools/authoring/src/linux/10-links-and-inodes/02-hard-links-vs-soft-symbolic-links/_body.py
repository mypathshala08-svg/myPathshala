import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

LN = r"""rm -rf ~/ln; mkdir -p ~/ln/docs ~/ln/releases/v1 ~/ln/releases/v2; cd ~/ln
echo 'Q3 sales: 42 lakh' > report.txt; echo 'meeting at 10' > docs/notes.txt
echo 'version 1' > releases/v1/app.txt; echo 'version 2' > releases/v2/app.txt"""
TINY = r"""export PATH=$PATH:/usr/sbin:/sbin; sudo umount /mnt/tiny 2>/dev/null; rm -f ~/tiny.img; truncate -s 8M ~/tiny.img; mkfs.ext4 -q -N 16 ~/tiny.img
sudo mkdir -p /mnt/tiny; sudo mount -o loop ~/tiny.img /mnt/tiny; sudo chown riya: /mnt/tiny"""
UNM = 'cd ~; sudo umount /mnt/tiny'

HOOK = hook('Riya runs <code>ls -l /usr/bin/python3</code> and sees an arrow: <code>python3 -&gt; python3.12</code>. A deployment tool switches a live website to a new version in one millisecond by changing where <code>current</code> points. A backup tool keeps 30 daily snapshots of 50 GB of files but uses only 52 GB of disk. And one day a colleague deletes the “original” file, and half the shortcuts break while the others keep working. All of this is <b>links</b>: two ways of giving a file another name. A <b>hard link</b> is a second name for the same inode. A <b>symbolic (soft) link</b> is a small file that contains a path.',
    ['explain hard links and symbolic links using inodes, and predict exactly what happens when the original is renamed, edited or deleted',
     'create, read and replace links with <code>ln</code>, <code>ln -s</code>, <code>ln -sfn</code>, <code>readlink -f</code> and <code>realpath</code>',
     'avoid the classic mistakes: relative symlink paths, broken links, <code>ln -sf</code> into a folder link, hard links across disks or to folders',
     'use links in real work: versioned deploys, /etc/alternatives, snapshot backups, and finding broken links with <code>find -xtype l</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the arrow in ls -l'),
    ('decide', 'Which link when?', 2, 'the quick chart'),
    ('definition', 'What a link is', 6, 'simple meaning + 4 depths'),
    ('types', 'Hard vs soft', 5, 'the big comparison'),
    ('commands', 'ln and friends by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'delete the original'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a versioned deploy'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which link? (decide in 5 seconds)', [
    ('A shortcut to a file or folder', 'ln -s TARGET LINK', 'symbolic'),
    ('Point at a folder', 'ln -s DIR LINK', 'hard links to folders are not allowed'),
    ('Point to another disk', 'ln -s', 'hard links stay on one filesystem'),
    ('Switch “current” to a new version', 'ln -sfn v2 current', '-n: replace the link itself'),
    ('Two names, the file survives deleting one', 'ln FILE NAME2', 'hard'),
    ('Save disk space in snapshots', 'cp -al / rsync --link-dest', 'hard links'),
    ('Where does a link really point?', 'readlink -f LINK', 'follows the whole chain'),
    ('Find broken links', 'find DIR -xtype l', 'target missing'),
])

cmap = concept_map(
    [('10.1', 'Inodes', 'name → inode'), ('3.2', 'cp and mv', 'copy vs rename'), ('7.1', 'find', '-type l, -samefile')],
    ['hard link = another name for the same inode', 'symbolic link = a file holding a path', 'ln, ln -s, -f, -n, -r', 'readlink, realpath, broken links', 'links in deploys, alternatives, backups'],
    [('14.1', 'Packages', '/etc/alternatives'), ('15.1', 'Disks', 'mounts and filesystems'), ('16.3', 'systemd', 'unit links in /etc'), ('17.3', 'Backups', 'rsync --link-dest')],
    'A hard link shares the inode. A soft link only knows a path, and the path can stop existing.')

sc = (term(20, 14, 316, 156, ['$ ls -li', ('802 -rw- 2 riya  report.txt', 'out'), ('802 -rw- 2 riya  backup.txt', 'out'), ('811 lrwx 1 riya  latest -> report.txt', 'acc'), '$ rm report.txt', '$ cat backup.txt latest', ('Q3 sales: 42 lakh', 'out'), ('cat: latest: No such file or directory', 'err')], title='riya@web01: ~/ln', prompt='riya@web01:~/ln$', size=6.8, step=15)
      + t(352, 36, 'Two kinds of link:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• hard: same inode', '  (802, links 2)', '• soft: own inode,', '  holds a path', '• delete original:', '  hard lives, soft breaks'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Two shortcuts, one survives</h2>
  <div class="story">
''' + puzzle('Riya makes a symbolic link with <code>cd ~/ln; ln -s report.txt docs/report-link</code>. <code>ls -l docs</code> shows the arrow, but <code>cat docs/report-link</code> says “No such file or directory”, even though <code>~/ln/report.txt</code> exists. What is wrong, and what are two ways to fix it?') + '''
    <p class="narration">Riya makes one hard link and one symbolic link to the same report, then deletes the original.</p>
''' + scene('A terminal: ls -li shows report.txt and backup.txt with the same inode and link count 2, and latest as an arrow to report.txt; after rm report.txt, backup.txt still prints the data and latest fails.', sc,
            'Hard link = <tspan font-weight="700" class="s-acc">same inode</tspan>. Soft link = <tspan font-weight="700" class="s-acc">a path</tspan>.') + '''
K> Both were “links”. Why did only one break?
A> <code>backup.txt</code> is a hard link: a second name for inode 802. Deleting <code>report.txt</code> removed one name; the inode still has one. <code>latest</code> is a symbolic link: its own little file containing the text “report.txt”. That name is gone, so the arrow points at nothing.
R> So which should I use?
A> Soft links for almost everything you call a “shortcut”: folders, other disks, versions, config. Hard links for special jobs like space-saving backups. Today you will see both on real files.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Hard link: two name tags tied to the same box. Soft link: a sticky note that says where the box is; if the box moves, the note points to nothing.">'
       + label_box(14, 20, 190, 110, ['hard link', 'two name tags', 'on ONE box', '(same inode)'], 'green', 8.6)
       + label_box(224, 20, 190, 110, ['soft link', 'a note saying', '“box is on shelf 3”', '(a path)'], 'blue', 8.6)
       + label_box(434, 20, 192, 110, ['remove tag 1:', 'box still has tag 2', 'move the box:', 'the note is now wrong'], 'amber', 8.6)
       + t(320, 160, 'A hard link is the file. A soft link only says where the file is.', 9.6, 'ink2')
       + t(320, 182, 'Delete the original: hard link survives, soft link breaks.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Links at four depths', [
    ('v', 'No jargon: name tags and notes', '      <p>Two ways to reach the same box.</p>' + pic),
    ('b', 'What you will type every day', '''      <ul>
        <li><code>ln -s /opt/app/bin/run ~/bin/run</code>: a shortcut (symbolic link). <code>ls -l</code> shows <code>run -&gt; /opt/app/bin/run</code>.</li>
        <li><code>ln report.txt backup.txt</code>: a second name (hard link). <code>ls -li</code> shows the same inode number and link count 2.</li>
        <li><code>readlink -f run</code>: where does it really point?</li>
        <li><code>rm run</code>: removes only the link, never the target.</li>
      </ul>'''),
    ('i', 'The rules, from inodes', '''      <ul>
        <li><b>Hard link</b> = a new directory entry with the <b>same inode number</b>. All names are equal: there is no “original”. The data is freed when the last name is removed (and nobody has it open).</li>
        <li>Hard links work only <b>inside one filesystem</b> (inode numbers are per disk) and not for folders (that could create loops).</li>
        <li><b>Symbolic link</b> = its own inode of type <code>l</code>, whose content is a path (its size is the path length). The path is resolved every time you use the link, <b>relative to the folder the link is in</b>.</li>
        <li>Symlinks can point to folders, to other disks and to things that do not exist (yet): a <b>dangling</b> link.</li>
      </ul>'''),
    ('a', 'Behind the screen: syscalls and kernel rules', '''      <ul>
        <li><code>ln</code> calls <code>linkat()</code>; <code>ln -s</code> calls <code>symlinkat()</code>; <code>readlink</code> calls <code>readlink()</code>. <code>open()</code> follows symlinks automatically, up to 40 in a chain (then “Too many levels of symbolic links”, ELOOP).</li>
        <li>Short symlink targets are stored inside the inode (“fast symlinks”), so they use no data block.</li>
        <li>Symlink permissions are always <code>lrwxrwxrwx</code> and ignored: access is checked on the target. <code>chmod</code> on a link changes the target.</li>
        <li><code>fs.protected_symlinks</code> and <code>fs.protected_hardlinks</code> (on by default) stop classic /tmp attacks: you cannot follow another user’s symlink in a sticky folder, or hard-link a file you cannot read or write.</li>
        <li>Renaming a symlink over another (<code>mv -T new current</code>) is <b>atomic</b>: zero-downtime deploys rely on it.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Hard links and symbolic links</h2>
''' + def_block(
    'A <b>hard link</b> is an additional directory entry that points to an existing inode; every hard link is an equal name for the same file, and the file’s data exists until the last link is removed. A <b>symbolic (soft) link</b> is a separate file of type link whose content is a path to another file or directory; the system follows that path each time the link is used, so the link breaks if the path no longer exists.',
    'Hard link: another name for the same file. Soft link: a pointer to a name.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Hard link', 'Another name for the same inode.'),
    ('Symbolic link (symlink)', 'A small file that contains a path.'),
    ('Target', 'What the symlink points to.'),
    ('Dangling / broken link', 'A symlink whose target does not exist.'),
    ('Link count', 'Number of hard links (names) of an inode.'),
    ('Dereference', 'Follow the link to its target.'),
    ('Relative symlink', 'Target path relative to the link’s folder.'),
    ('Atomic switch', 'Replace a link in one step, no gap.'),
]) + '\n' + names('Where the names come from.', [
    ('ln', 'link', 'Unix V1, 1971.'),
    ('-s', 'symbolic', 'Added in BSD 4.2, 1983.'),
    ('-f', 'force', 'Replace an existing name.'),
    ('-n', 'no-dereference', 'Treat a folder link as a file.'),
    ('-r', 'relative', 'Compute a relative path.'),
    ('readlink', 'read link', 'Print the stored path.'),
    ('realpath', 'real path', 'Full path, all links resolved.'),
    ('l', 'link type', 'First letter in ls -l.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Soft link', '<code>ln -s TARGET LINK</code>'),
    ('Hard link', '<code>ln FILE NAME</code>'),
    ('Where to?', '<code>readlink -f LINK</code>'),
    ('Replace a link', '<code>ln -sfn NEW LINK</code>'),
    ('Broken links', '<code>find . -xtype l</code>'),
    ('All names of a file', '<code>find / -xdev -samefile F</code>'),
]) + '\n' + lv + didyou('Every folder already uses hard links: <code>.</code> is a hard link to the folder itself and <code>..</code> to its parent. That is why a new folder has link count 2, and only the kernel may make such links to folders.') + '''
EXAM> “Order of arguments in ln?” → Like <code>cp</code>: first what exists (the target), then the new name. <code>ln -s TARGET LINK_NAME</code>.
''' + qc('A hard link and the original: which one is the “real” file?', 'Neither and both: they are two equal names for the same inode. There is no original once the link exists.') + mistake('ln -s report.txt docs/report-link   (run in ~/ln)',
    'ln -s ../report.txt docs/report-link   ·   or   ln -sr report.txt docs/report-link   ·   or an absolute path',
    'A relative target is resolved from the link’s own folder (docs/), not from where you typed the command. -r computes the right relative path for you.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Hard link vs soft link: the big comparison</h2>
''' + table(['', 'Hard link', 'Symbolic (soft) link'], [
    ['Is', 'another name for the same inode', 'a separate file containing a path'],
    ['Inode number', 'same as the target', 'its own'],
    ['ls -l shows', 'normal file, link count ≥ 2', '<code>l</code> … <code>name -&gt; target</code>'],
    ['Delete the original', 'still works (data stays)', 'breaks (dangling)'],
    ['Rename / move the original', 'still works', 'breaks (unless absolute path still valid)'],
    ['Edit the original in place', 'sees the change', 'sees the change'],
    ['Across filesystems', 'no (“Invalid cross-device link”)', 'yes'],
    ['To a folder', 'no (“hard link not allowed for directory”)', 'yes'],
    ['To something missing', 'no', 'yes (dangling)'],
    ['Size', 'size of the file', 'length of the path'],
    ['Permissions', 'shared (one inode)', 'always rwxrwxrwx; target’s apply'],
    ['Typical use', 'snapshots, dedupe', 'shortcuts, versions, alternatives, config'],
], minw=560) + table(['Tool', 'Default on symlinks', 'Change it'], [
    ['<code>cat</code>, <code>vim</code>, <code>open()</code>', 'follow', '—'],
    ['<code>ls -l</code>, <code>stat</code>', 'show the link itself', '<code>ls -lL</code>, <code>stat -L</code>'],
    ['<code>cp</code>', 'copies the target’s data', '<code>cp -P</code> / <code>-a</code>: copy the link'],
    ['<code>cp -r</code>', 'copies links as links', '<code>-L</code>: follow'],
    ['<code>find</code>', 'does not follow', '<code>-L</code> / <code>-follow</code>'],
    ['<code>rm</code>, <code>mv</code>', 'act on the link', '—'],
    ['<code>chmod</code>, <code>chown</code>', 'change the target', '<code>chown -h</code> for the link'],
    ['<code>tar</code>, <code>rsync -a</code>', 'store links as links', '<code>-h</code> / <code>-L</code>'],
], minw=420) + qc('You edit <code>report.txt</code> with <code>sed -i</code>. Does the hard link <code>backup.txt</code> see the change? Does the symlink <code>latest</code>?', 'The symlink yes (it follows the name). The hard link no: sed -i makes a new inode for report.txt (Lesson 10.1), and backup.txt keeps the old one.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>ln explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine, in a sample folder <code>~/ln</code> with <code>report.txt</code>, <code>docs/notes.txt</code> and two releases <code>releases/v1</code>, <code>releases/v2</code>, plus a separate small test disk at <code>/mnt/tiny</code>.</p>
''' + cmdcard_u(['shortcuts to files and folders', 'version switching (current → v2)', 'links to other disks'],
               ['relative targets typed from the wrong folder', 'links that must survive the target being deleted'])(
    'soft', 'ln -s', 'make a symbolic link',
    '<code>ln -s TARGET LINK</code> creates LINK containing the text TARGET. The target is not checked: it may be missing. A relative target is resolved from LINK’s folder. <code>-r</code> makes the relative path for you; <code>-f</code> replaces an existing LINK; <code>-n</code> treats an existing folder link as a file.',
    'ln -s [-f] [-n] [-r] [-v] TARGET LINK_NAME', 'change',
    [('-s', 'symbolic', 'shortcuts'),
     ('-r', 'relative path computed', 'portable trees'),
     ('-f', 'replace existing name', 'update'),
     ('-n', 'do not enter a folder link', 'with -f'),
     ('-v', 'print what it did', 'logs'),
     ('-T', 'LINK is never a folder', 'scripts')],
    dict(setup=LN, cmd="cd ~/ln\nln -s report.txt latest\nln -s releases/v1 current\nls -l latest current | awk '{print $1, $(NF-2), $(NF-1), $NF}'\ncat latest current/app.txt", note='Size of latest = 10 = the length of “report.txt”. The link stores a path, not data.'),
    [('dev', [
        dict(situation='The puzzle: a relative link made from the wrong folder.', setup=LN, cmd="cd ~/ln\nln -s report.txt docs/report-link\ncat docs/report-link\nln -sfr report.txt docs/report-link; ls -l docs/report-link | awk '{print $1, $(NF-2), $(NF-1), $NF}'; cat docs/report-link", expect='any',
             why='The stored text “report.txt” means docs/report.txt. -r stored ../report.txt instead.')]),
     ('sys', [
        dict(situation='Make a command available in PATH without copying it.', setup=LN + "; mkdir -p ~/ln/tool/bin ~/ln/bin; printf '#!/bin/sh\\necho tool v3\\n' > ~/ln/tool/bin/tool; chmod +x ~/ln/tool/bin/tool", cmd="ln -s ~/ln/tool/bin/tool ~/ln/bin/tool\nPATH=~/ln/bin:$PATH tool",
             why='This is how /usr/local/bin often works, and how Ubuntu links python3 → python3.12.')]),
    ],
    anat=anatomy([('ln', 'cmd', 'link'), ('-s', 'opt', 'symbolic'), ('releases/v1', 'arg', 'target (exists)'), ('current', 'arg', 'new name')], 'Like cp: the existing thing first, the new name second.')
) + cmdcard_u(['a name that survives deleting the other', 'space-saving snapshots and backups'],
               ['folders (not allowed)', 'another disk (not allowed)', 'files edited by tools that replace them (sed -i, many editors)'])(
    'hard', 'ln', 'make a hard link',
    '<code>ln FILE NEW</code> adds a directory entry NEW pointing to FILE’s inode; the link count goes up by one. Only for files, only on the same filesystem. <code>rm</code> of any name lowers the count; data is freed at 0.',
    'ln [-f] [-v] FILE NEW_NAME', 'change',
    [('ln F N', 'second name', 'same inode'),
     ('-f', 'replace existing N', 'update'),
     ('-v', 'verbose', 'logs'),
     ('-P / -L', 'link a symlink itself / its target', 'rare'),
     ('stat -c %h', 'link count', 'check')],
    dict(setup=LN, cmd="cd ~/ln\nln report.txt backup.txt\nls -li report.txt backup.txt | awk '{print $1, $2, $3, $NF}'\nrm report.txt\nstat -c '%i links=%h %n' backup.txt; cat backup.txt", note='Same inode, link count 2. After rm, one name remains and the data is untouched.'),
    [('sys', [
        dict(situation='Not allowed: folders and other disks.', setup=LN + '; ' + TINY, cmd="cd ~/ln\nln docs docs-hard; echo \"exit $?\"\nln report.txt /mnt/tiny/report.txt; echo \"exit $?\"\nln -s ~/ln/report.txt /mnt/tiny/report.txt && cat /mnt/tiny/report.txt\n" + UNM, expect='any',
             why='Inode numbers only mean something inside one filesystem, so hard links cannot cross disks. A symlink can.')]),
     ('devops', [
        dict(situation='Snapshot backups that cost almost nothing.', setup=LN, cmd="cd ~/ln; cp -al docs snap1\nstat -c '%i %h %n' docs/notes.txt snap1/notes.txt\ndu -sh docs snap1 | cat",
             why='cp -al makes a tree of hard links (rsync --link-dest does the same). du counts the shared data only once: snap1 shows 4.0K for the folder itself.')]),
    ]
) + mistake('Hard-link a config, then edit the original with sed -i or vim', 'Edit in place (>>, a tool that writes into the same file), or use a symlink',
            'sed -i and many editors write a new file and rename it over the name. The name gets a new inode; the hard link keeps the old content. Checked in the Run section.') + cmdcard_u(['finding where a link really leads', 'scripts that need the real path', 'debugging “No such file” on a link'],
               ['readlink without -f on chains (shows only one step)'])(
    'read', 'readlink · realpath · ls -l', 'read a link',
    '<code>readlink LINK</code> prints the stored text (one step). <code>readlink -f</code> follows every link and prints the final absolute path (<code>-e</code>: fail if it does not exist). <code>realpath</code> does the same. <code>ls -l</code> shows the arrow; <code>ls -lL</code> shows the target’s details.',
    'readlink [-f|-e] LINK   ·   realpath PATH', 'safe',
    [('readlink L', 'stored text', 'one step'),
     ('readlink -f L', 'final path', 'whole chain'),
     ('readlink -e L', 'final path, must exist', 'checks'),
     ('realpath P', 'canonical path', 'scripts'),
     ('ls -lL', 'target details', 'size, mode'),
     ('stat -L', 'target inode', 'compare')],
    dict(setup=LN + '; cd ~/ln; ln -s releases/v2 current; ln -s current/app.txt app', cmd="cd ~/ln\nreadlink app; readlink -f app\nls -l app | awk '{print $1, $5, $(NF-2), $(NF-1), $NF}'; ls -lL app | awk '{print $1, $5, $NF}'", note='A chain: app → current/app.txt → releases/v2/app.txt. readlink shows one step; -f shows the end.'),
    [('sys', [
        dict(situation='Which Python is “python3” really?', cmd="ls -l /usr/bin/python3 | sed 's/.* \\/usr/\\/usr/'; readlink -f /usr/bin/python3",
             why='On our build machine the chain even passes through /etc/alternatives (Lesson 14.1) before reaching the versioned binary.')]),
     ('qa', [
        dict(situation='A loop of links.', setup='rm -rf ~/ln; mkdir -p ~/ln; cd ~/ln; ln -s b a; ln -s a b', cmd="cd ~/ln; cat a; echo \"exit $?\"; readlink -f a; echo \"exit $?\"", expect='any',
             why='The kernel gives up after 40 steps: ELOOP. readlink -f also fails.')]),
    ]
) + cmdcard_u(['switching a “current” link to a new version', 'replacing a link in scripts'],
               ['ln -sf on a link that points to a folder (without -n)'])(
    'replace', 'ln -sfn · mv -T', 'replace a link safely',
    'Updating a link that points to a folder is a trap: <code>ln -sf v2 current</code> follows <code>current</code> into the folder and creates <code>v1/v2</code>. Add <code>-n</code> (or <code>-T</code>). For a zero-downtime switch, make a new link and rename it over the old one with <code>mv -T</code>: rename is atomic.',
    'ln -sfn NEW_TARGET LINK   ·   ln -s NEW tmp && mv -T tmp LINK', 'change',
    [('-sfn', 'replace the link itself', 'versions'),
     ('-sfT', 'same, LINK never a folder', 'scripts'),
     ('mv -T tmp current', 'atomic rename', 'live sites'),
     ('rm current', 'remove the link', 'not the folder')],
    dict(setup=LN + '; cd ~/ln; ln -s releases/v1 current', cmd="cd ~/ln\nln -sf releases/v2 current; ls releases/v1\nrm releases/v1/v2\nln -sfn releases/v2 current; readlink current; cat current/app.txt", note='Without -n the new link landed inside v1 (v1/v2). With -n, current itself was replaced.'),
    [('devops', [
        dict(situation='Zero-downtime release switch.', setup=LN + '; cd ~/ln; ln -s releases/v1 current', cmd="cd ~/ln\nln -s releases/v2 current.tmp && mv -T current.tmp current\nreadlink current; cat current/app.txt",
             why='At every moment current points to v1 or v2, never to nothing. Capistrano and many deploy scripts do exactly this; rollback is the same command with v1.')]),
    ]
) + mistake('rm current/   ·   rm -r current/', 'rm current   (no slash)',
            'With a trailing slash the path means the folder behind the link. rm refuses or, with -r, deletes the folder’s contents. Without the slash only the link goes.') + cmdcard_u(['clean-ups after moving or deleting things', 'finding every name of a file'],
               ['find -L on big trees with loops'])(
    'findl', 'find -type l · -xtype l · -samefile', 'find links',
    '<code>find -type l</code> lists symlinks; <code>-xtype l</code> lists symlinks whose target is missing (broken). <code>-samefile F</code> and <code>-inum N</code> list hard links of F; <code>-links +1</code> files with several names.',
    'find DIR -xtype l [-delete]   ·   find DIR -xdev -samefile FILE', 'change',
    [('-type l', 'all symlinks', 'inventory'),
     ('-xtype l', 'broken symlinks', 'clean-up'),
     ('-samefile F', 'hard links of F', 'all names'),
     ('-links +1', 'files with ≥2 names', 'audit'),
     ('-lname PAT', 'symlink text matches', 'moved paths')],
    dict(setup=LN + '; cd ~/ln; ln -s report.txt ok-link; ln -s gone.txt broken-link; ln report.txt docs/hard-copy', cmd="cd ~/ln\nfind . -type l | sort\nfind . -xtype l\nfind . -samefile report.txt | sort", note='Only broken-link has a missing target. The hard link is found by -samefile, not by -type l: it is a normal file.'),
    [('sec', [
        dict(situation='Links that point outside a web root are a risk.', setup=LN + '; cd ~/ln; mkdir www; ln -s /etc/passwd www/users.txt; ln -s ../report.txt www/r.txt', cmd="cd ~/ln; find www -type l -lname '/*' -printf '%p -> %l\\n'",
             why='A symlink to /etc/passwd inside a web folder can leak it. Web servers have options to refuse symlinks for this reason.')]),
    ]
) + undo('Links are cheap to remove and recreate; the danger is removing what is behind them.', [
    ('Made a link in the wrong place:', '<code>rm LINK</code> (no trailing slash) and make it again.'),
    ('Link points to the wrong target:', '<code>ln -sfn RIGHT LINK</code>.'),
    ('Deleted the target of a symlink:', 'restore the file at that path; the link works again automatically.'),
    ('Deleted one hard link:', 'the data is still there under the other names: <code>find / -xdev -inum N</code>.'),
    ('ln -sf created v1/v2:', '<code>rm releases/v1/v2</code>, then use <code>-sfn</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='ln docs docs-hard', setup=LN + '; cd ~/ln', meaning='Hard links to folders are forbidden.', fix='<code>ln -s docs docs-link</code>.'),
    dict(cmd='ln report.txt /mnt/tiny/r.txt', setup=LN + '; ' + TINY + '; cd ~/ln', meaning='Hard link across filesystems.', fix='Use <code>ln -s</code>, or copy.'),
    dict(cmd='ln -s report.txt latest; ln -s report.txt latest', setup=LN + '; cd ~/ln', meaning='The link name exists.', fix='<code>ln -sf</code> (or -sfn for folders).'),
    dict(cmd='ln -s nothing.txt dead; cat dead', setup=LN + '; cd ~/ln', meaning='Dangling link: target missing.', fix='<code>readlink dead</code>, then create the target or fix the link.'),
]) + qc('<code>ln -s</code> never complains about a missing target. Why is that a feature?', 'You can create links before the target exists (a config that will be installed later, a mount point), and links survive the target being replaced.') + '''
'''
_sh.run_sh(UNM + ' 2>/dev/null', 'any')
cards = cards + '</section>\n'

def state(k):
    rep = label_box(14, 20, 100, 40, ['report.txt', 'inode 802'], 'blue' if k < 2 else 'red', 8)
    if k >= 2:
        rep = label_box(14, 20, 100, 40, ['(deleted)', ''], 'red', 8)
    bak = label_box(14, 72, 100, 40, ['backup.txt', 'inode 802'], 'green', 8) if k >= 1 else ''
    lat = label_box(14, 124, 100, 40, ['latest → report.txt', 'inode 811'], 'amber' if k < 2 else 'red', 7.4) if k >= 1 else ''
    ino = label_box(220, 60, 120, 48, ['inode 802', f'links {[1, 2, 1, 1][k]} · 18 bytes'], 'violet', 8)
    o = rep + bak + lat + ino
    o += arrow(114, 40, 220, 76) if k < 2 else ''
    o += arrow(114, 92, 220, 88) if k >= 1 else ''
    return o
see_cmds = [['$ ls -li report.txt', ('802 … 1 report.txt', 'out')],
            ['$ ln report.txt backup.txt', '$ ln -s report.txt latest'],
            ['$ rm report.txt', '$ cat backup.txt', ('Q3 sales: 42 lakh', 'out')],
            ['$ cat latest', ('cat: latest: No such file', 'err'), ('  or directory', 'err')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/ln', prompt='riya@web01:~/ln$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['One name, one inode.', 'A hard link and a soft link.', 'Delete the first name.', 'The soft link is broken.'])]
behind = [state(k) + t(180, 186, n, 8.4, 'violet', bold=True) for k, n in enumerate(['report.txt → inode 802 (links 1).', 'backup.txt → same 802 (links 2); latest holds a path.', 'rm: links 2 → 1. Data stays.', 'latest looks up “report.txt”: gone.'])]
two = anim_two('Delete the original', 'Behind the screen: names, inode and a path',
               'A terminal: create a hard link and a symbolic link, delete report.txt, cat both.',
               'Boxes for report.txt, backup.txt and latest pointing to inode 802; after rm, backup.txt still points to the inode and latest points to a missing name.', see, behind,
               ['Start.', 'Two links.', 'rm.', 'Broken.'],
               ['one name', 'hard + soft', 'links 2 → 1', 'dangling'])

def dep(k):
    v1 = label_box(150, 20, 90, 40, ['releases/v1', 'version 1'], 'green' if k == 0 else 'card', 8)
    v2 = label_box(150, 96, 90, 40, ['releases/v2', 'version 2'], 'green' if k >= 2 else ('amber' if k == 1 else 'card'), 8)
    cur = label_box(14, 58, 90, 40, ['current', '(symlink)'], 'blue', 8)
    tmp = label_box(14, 120, 90, 34, ['current.tmp'], 'amber', 8) if k == 1 else ''
    a = arrow(104, 72, 150, 42) if k < 2 else arrow(104, 84, 150, 114)
    return cur + v1 + v2 + tmp + a + (arrow(104, 136, 150, 120) if k == 1 else '')
frames = [dep(0) + t(180, 172, 'The site serves current → v1.', 8.6, 'violet', bold=True),
          dep(1) + t(180, 172, 'Make current.tmp → v2 (site still on v1).', 8.6, 'violet', bold=True),
          dep(2) + t(180, 172, 'mv -T current.tmp current: one atomic step.', 8.6, 'green', bold=True),
          dep(3) + t(180, 172, 'Rollback = the same with v1.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'A zero-downtime deploy with one symlink',
              'How release tools switch a live site.',
              'release switch', 'A current link pointing to releases/v1; a temporary link to v2 is created and renamed over current in one atomic step.', frames,
              ['Live on v1.', 'Prepare.', 'Switch.', 'Rollback ready.'], hid='scenario-deploy')

dx = dissect('Layer by layer: what each link really is',
    'Each layer has a real command and output from our build machine.', [
    dict(key='name', name='Directory entries', sub='names', why='Every link is a name.', how='One entry each.', impl='ext4 folder blocks.', used='ls.',
         setup=LN + '; cd ~/ln; ln report.txt hard.txt; ln -s report.txt soft.txt', cmd="cd ~/ln; ls -li report.txt hard.txt soft.txt | awk '{print $1, $2, $3, $10, $11, $12}'"),
    dict(key='hard', name='Hard link', sub='same inode', why='Second name.', how='linkat().', impl='Link count +1.', used='Backups.',
         setup=LN + '; cd ~/ln; ln report.txt hard.txt', cmd="cd ~/ln; stat -c '%i %h %F %n' report.txt hard.txt"),
    dict(key='soft', name='Symlink inode', sub='type link', why='Holds a path.', how='symlinkat().', impl='Fast symlink: path inside the inode.', used='Shortcuts.',
         setup=LN + '; cd ~/ln; ln -s report.txt soft.txt', cmd="cd ~/ln; stat -c '%i %h %F size=%s blocks=%b' soft.txt; readlink soft.txt"),
    dict(key='resolve', name='Resolution', sub='at every open', why='The path is looked up each time.', how='From the link’s folder.', impl='Max 40 hops.', used='Every access.',
         setup=LN + '; cd ~/ln; ln -s report.txt soft.txt; mv report.txt moved.txt', cmd="cd ~/ln; cat soft.txt; echo \"exit $?\"; mv moved.txt report.txt; cat soft.txt", expect='any'),
], hint='From the names down to how a path is followed. Click a layer.')

hd = hood('Under the hood: one system call each', 'The real system calls of <code>ln -s report.txt latest</code> and <code>ln report.txt backup.txt</code> on our build machine.',
          "sh -c 'ln -s report.txt latest; ln report.txt backup.txt'", setup=LN + '; cd ~/ln', show='symlinkat|linkat', trace='symlinkat,linkat')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Delete the original, and switch a release</h2>
''' + two + s1 + dx + hd + qc('A symlink points to a file you may not read. Can you read it through the link?', 'No. Symlink permissions (rwxrwxrwx) are ignored; the target’s permissions decide.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Links at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['current →', 'releases/v2'], 'blue', 8.6), '1. Deployments',
              'Releases go into their own folders; a current symlink is switched atomically, and rollback is one command.', ['Upload', '*ln -s + mv -T', 'live']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['/etc/', 'alternatives'], 'green', 8.6), '2. Choosing versions',
    'Debian/Ubuntu point java, editor and python at the chosen version through chains of symlinks.', ['Install', '*update-alternatives', 'use']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['sites-enabled', '→ available'], 'amber', 8.6), '3. Config on/off',
    'nginx and Apache enable a site by linking it from sites-available into sites-enabled; systemd enables units with links.', ['Write', '*ln -s', 'reload']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['--link-dest', 'snapshots'], 'violet', 8.6), '4. Backups',
    'rsync --link-dest and Time-Machine-style tools hard-link unchanged files, so 30 snapshots cost little more than one.', ['Backup', '*hard links', 'restore']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-xtype l', 'audit'], 'red', 8.6), '5. Security and clean-up',
    'Teams search for broken links and for links pointing outside allowed folders.', ['Scan', '*find -xtype l', 'fix']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Make a shortcut', scenario='Quick access.', setup=LN, cmd="cd ~/ln; ln -s docs/notes.txt notes; cat notes", explain='ln -s.'),
    dict(level='b', title='Where does it point?', scenario='Read the arrow.', setup=LN + '; cd ~/ln; ln -s releases/v1 current', cmd="readlink -f ~/ln/current", explain='-f: final path.'),
    dict(level='i', title='List broken links', scenario='After a clean-up.', setup=LN + '; cd ~/ln; ln -s old1 a; ln -s old2 b; ln -s report.txt c', cmd="find ~/ln -xtype l -printf '%p -> %l\\n' | sort", explain='-xtype l.'),
    dict(level='i', title='All names of a file', scenario='Who else points here?', setup=LN + '; cd ~/ln; ln report.txt docs/r1; ln report.txt releases/r2', cmd="find ~/ln -xdev -samefile ~/ln/report.txt | sort", explain='-samefile.'),
    dict(level='a', title='Delete broken links', scenario='Automate the clean-up.', setup=LN + '; cd ~/ln; ln -s old1 a; ln -s report.txt c', cmd="find ~/ln -xtype l -print -delete; ls ~/ln", explain='-delete after checking.'),
], extra=build_up('a versioned release', 'Riya deploys v1, then v2, then rolls back.', LN, [
    ('cd ~/ln; ln -sfn releases/v1 current; cat current/app.txt', '1. Live on v1.'),
    ('cd ~/ln; ln -s releases/v2 current.tmp && mv -T current.tmp current; cat current/app.txt', '2. Atomic switch to v2.'),
    ('cd ~/ln; ln -sfn releases/v1 current; readlink current; cat current/app.txt', '3. Rollback.'),
], cumulative=True)) + which('Choosing the right link.', [
    ('Shortcut to file/folder', 'ln -s', 'Works for folders and other disks.', 'Relative path from the wrong folder.'),
    ('Must survive delete of other name', 'ln (hard)', 'Same inode.', 'Expecting it across disks.'),
    ('Update a folder link', 'ln -sfn', 'Replaces the link.', 'ln -sf (creates v1/v2).'),
    ('Live switch', 'ln -s + mv -T', 'Atomic.', 'rm then ln (gap).'),
    ('Real target', 'readlink -f', 'Whole chain.', 'readlink only (one step).'),
    ('Broken links', 'find -xtype l', 'Target missing.', 'find -type l (all links).'),
]) + keys('Handy forms.', [
    ('ln -s T L', 'symlink', 'shortcut'),
    ('ln -sr T L', 'relative symlink', 'portable'),
    ('ln -sfn T L', 'replace link', 'versions'),
    ('ln F N', 'hard link', 'second name'),
    ('readlink -f L', 'final path', 'debug'),
    ('find . -xtype l', 'broken links', 'clean'),
]) + scriptit('deploy.sh', 'A tiny release switcher: checks the release exists, switches current atomically, prints the result. Rollback = run it with the old version.',
'''cd ~/ln || exit 1
rel=releases/${1:-v2}
[ -d "$rel" ] || { echo "no such release: $rel" >&2; exit 1; }
ln -sfn "$rel" current.tmp && mv -T current.tmp current
echo "current -> $(readlink current)"
cat current/app.txt''',
'<p>Run with v2 on the sample folder.</p>') + puzzle_answer('The text “report.txt” is resolved from the link’s own folder, <code>docs/</code>, so the link means <code>docs/report.txt</code>, which does not exist. Fix 1: <code>ln -sfr report.txt docs/report-link</code> (stores <code>../report.txt</code>). Fix 2: an absolute target, <code>ln -sf ~/ln/report.txt docs/report-link</code>.') + qc('Does <code>rm latest</code> delete report.txt if latest is a symlink to it?', 'No. rm removes the link only.') + '''
</section>
'''

_sh.run_sh('cd ~; sudo umount /mnt/tiny 2>/dev/null; rm -rf ~/ln ~/tiny.img', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-inodes-how-linux-stores-a-file-behind-its-name/">Lesson 10.1</a> (inodes and link counts).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
