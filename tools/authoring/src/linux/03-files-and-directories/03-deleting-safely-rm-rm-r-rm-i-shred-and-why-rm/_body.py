import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

HOOK = hook('There is no Recycle Bin in the terminal. One extra space in <code>rm -rf /home/riya/project /backup</code> deletes the project <b>and</b> the whole backup, in under a second, without a question. Real companies have lost production databases this way. This lesson teaches you to delete exactly what you mean, and nothing else.',
    ['delete files and folders with <code>rm</code>, <code>rm -r</code> and <code>rm -d</code>, and know when each is needed',
     'make rm ask first (<code>-i</code>, <code>-I</code>) and understand what <code>-f</code> really switches off',
     'read every rm command for the five classic dangers before pressing Enter',
     'destroy sensitive data with <code>shred</code>, and know when even shred is not enough'])
ROAD = roadmap([
    ('story', 'The story', 3, 'one space, two folders gone'),
    ('decide', 'Which command when?', 2, 'rm, rmdir, rm -r or shred?'),
    ('definition', 'What the commands are', 5, 'simple meaning + 4 depths'),
    ('commands', 'rm and shred by field', 12, 'options, real runs, your field'),
    ('danger', 'The five dangers', 4, 'read before Enter'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'what “deleted” really means'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'danger', 'lab'])
DECIDE = decide('Which delete command? (decide in 5 seconds)', [
    ('Delete one file', 'rm file', 'gone at once, no bin'),
    ('Delete several files, but check each', 'rm -i *.tmp', 'asks for every file'),
    ('Delete many files, one safety question', 'rm -I *.log', 'asks once if more than 3'),
    ('Delete an empty folder', 'rmdir dir  (or rm -d dir)', 'refuses if not empty'),
    ('Delete a folder and everything inside', 'rm -r dir', 'check with ls -R first'),
    ('Delete without any questions (scripts)', 'rm -rf "${dir:?}"', 'only with a checked path'),
    ('A file whose name starts with -', 'rm -- -name  (or rm ./-name)', 'otherwise read as an option'),
    ('Destroy a secret so it cannot be recovered', 'shred -u -z file', 'HDD only; not reliable on SSD'),
    ('Delete but be able to undo', 'mv file ~/trash/  or gio trash', 'a bin of your own'),
    ('Empty a file but keep it', '> file  or truncate -s 0 file', 'logs still being written'),
])

cmap = concept_map(
    [('3.1', 'Creating files and folders', 'and rmdir for empty ones'), ('3.2', 'Copying and moving', 'back up before you delete'), ('2.3', 'Absolute and relative paths', 'know exactly where you are')],
    ['rm, rm -r, rm -d: files and folders', '-i, -I, -f, -v: questions and silence', 'the five dangers: spaces, *, empty variables, root, -f', 'names that start with a dash: --', 'shred: overwrite before deleting'],
    [('3.4', 'Wildcards', 'rm *.log: what * matches'), ('7.1', 'find -delete', 'delete by age and size'), ('10.1', 'Inodes', 'why deleted-but-open files keep space'), ('12.6', 'set -u and set -e', 'safer delete scripts')],
    'Deleting is the only file operation with no undo. Ten seconds of checking saves days of recovery.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 150, ['$ ls', ('project  backup', 'out'), '$ rm -rf /home/riya/project /backup', ('(no message at all)', 'dim'), '$ ls /backup', ("ls: cannot access '/backup': No such", 'err'), ('file or directory', 'err')], title='server-01', prompt='$', size=7.6, step=15)
      + t(352, 36, 'What went wrong?', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• a space split one path in two', '• -r: everything inside', '• -f: no questions, no errors', '• no bin, no undo', '(illustration)'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>One space, two folders gone</h2>
  <div class="story">
''' + puzzle('A server’s disk is 100% full. Riya deletes a 20 GB log file with <code>rm</code>. The file is gone from <code>ls</code>, but <code>df</code> still says the disk is full. Did rm fail? Where are the 20 GB?') + '''
    <p class="narration">On a test server, Riya wanted to remove the folder <code>/home/riya/project/backup</code>. She typed it fast and an extra space slipped in before <code>/backup</code>.</p>
''' + scene('A terminal: rm -rf with an accidental space deletes both the project folder and the /backup folder without any message.', sc,
            'rm with <tspan font-weight="700" class="s-acc">-rf</tspan> never asks and never warns.') + '''
R> I typed one path! Why are two folders gone?
A> The shell splits words at spaces. <code>/home/riya/project</code> and <code>/backup</code> became two arguments, and <code>-r</code> deleted each one completely. <code>-f</code> made sure nothing stopped it or printed a message.
K> Can we get them back from the Recycle Bin?
A> There is no bin. rm removes the names immediately. Today you learn rm properly: the options, the five dangers to check for, how to make rm ask, and <code>shred</code> for secrets. And how each team deletes safely: admins, DBAs, data engineers, DevOps and security.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Windows Delete moves a file to the Recycle Bin, where it can be restored. rm in Linux removes the name immediately; the space is reused later. shred scribbles over the pages before throwing the book away.">'
       + ''.join(label_box(16 + k * 208, 22, 192, 110, [a, b, c, d], tone, 9.4) for k, (a, b, c, d, tone) in enumerate([
           ('Windows Delete', 'goes to the Recycle Bin', 'you can restore it', 'until the bin is emptied', 'green'),
           ('Linux rm', 'the name is removed now', 'no bin, no question', 'space reused later', 'red'),
           ('shred', 'scribble over every page', 'then throw away', 'for secrets (on HDDs)', 'violet')]))
       + t(320, 160, 'rm = tearing the label off a box in a huge warehouse.', 9.6, 'ink2')
       + t(320, 182, 'Nobody can find the box any more, and soon something else is stored there.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Deleting at four depths', [
    ('v', 'No jargon: no Recycle Bin', '      <p>Deleting in the terminal is not like pressing Delete in Windows.</p>' + pic + '''
      <ul>
        <li><code>rm</code> (remove) deletes at once. There is no bin and no “Undo”.</li>
        <li>Folders need <code>-r</code>, which means “and everything inside”.</li>
        <li>So the habit is: <b>look first</b> (<code>ls</code>), <b>then delete</b>.</li>
      </ul>'''),
    ('b', 'The commands you will type every day', '''      <ul>
        <li><code>rm file.txt</code> deletes a file; <code>rm a.txt b.txt</code> several.</li>
        <li><code>rm -r folder</code> deletes a folder and all its content. <code>rmdir</code> or <code>rm -d</code> delete only empty folders.</li>
        <li><code>rm -i</code> asks “remove …?” for each file; answer <code>y</code> or <code>n</code>.</li>
        <li><code>rm -v</code> prints what it removed.</li>
        <li><code>rm -f</code> (force) never asks and does not complain about missing files. Use it only when you are sure.</li>
      </ul>'''),
    ('i', 'Questions, silence and strange names', '''      <ul>
        <li><code>-I</code> asks <b>once</b> if you delete more than three files or delete recursively: a good everyday safety net (<code>alias rm='rm -I'</code>).</li>
        <li>rm asks before deleting a <b>write-protected</b> file only when you type at a keyboard; in scripts it just deletes it. <code>-f</code> also removes that question.</li>
        <li>You need write permission on the <b>folder</b>, not on the file, to delete a file (Lesson 9.1).</li>
        <li>A name starting with <code>-</code> looks like an option: use <code>rm -- -name</code> or <code>rm ./-name</code>.</li>
        <li><code>--preserve-root</code> (default) refuses <code>rm -rf /</code>; rm also refuses <code>.</code> and <code>..</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: what “deleted” means', '''      <ul>
        <li>rm calls <code>unlinkat()</code>: it removes the <b>name</b> from the folder and lowers the inode’s link count (Lesson 10.1).</li>
        <li>The data blocks are freed only when the link count is 0 <b>and no process has the file open</b>. A deleted log still held open by a program keeps using disk space (<code>lsof +L1</code> finds them).</li>
        <li>Freed blocks are not wiped; until they are reused, recovery tools may find the data. That is why <code>shred</code> overwrites first.</li>
        <li>shred is unreliable on SSDs (wear levelling), on journaling or copy-on-write file systems (Btrfs, ZFS) and on files with backups or snapshots. Use full-disk encryption, <code>blkdiscard</code> or secure erase for real secrets.</li>
        <li><code>rm -r</code> walks the tree depth-first: files first, then each folder once it is empty.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>rm, rm -r and shred</h2>
''' + def_block(
    '<code>rm</code> (remove) deletes directory entries for files. With <code>-r</code> (recursive) it deletes directories and their entire contents; with <code>-d</code> it deletes empty directories. The data is released when no name and no open file refer to it any more; there is no recycle bin. <code>shred</code> overwrites a file’s contents several times with random data (and optionally zeros) and can then remove it, to make recovery harder.',
    '<code>rm</code> deletes for good, <code>rm -r</code> also folders, <code>shred</code> scribbles over the data first.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Unlink', 'Remove a name of a file; rm’s real job.'),
    ('Recursive', 'The folder and everything inside it, all levels.'),
    ('Force (-f)', 'No questions, no “not found” errors.'),
    ('Write-protected', f'A file without w permission. {gl("permission-bits-rwx", "Glossary →")}'),
    ('Inode, link count', f'The file record and how many names it has. {gl("inode", "Glossary →")}'),
    ('Deleted but open', f'A file with no name still used by a program. {gl("deleted-but-still-open-file", "Glossary →")}'),
    ('Root directory', f'<code>/</code>, the top of everything. {gl("root-directory", "Glossary →")}'),
    ('Exit status', f'0 = it worked. {gl("exit-status", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('rm', 'remove', 'Removes names (links) of files.'),
    ('-r', 'recursive', 'Down into every folder.'),
    ('-f', 'force', 'Never ask, never complain.'),
    ('-i / -I', 'interactive', 'Ask every time / ask once.'),
    ('-d', 'directory', 'Empty folders, like rmdir.'),
    ('--', 'end of options', 'Everything after it is a name.'),
    ('shred', 'to shred paper', 'Cut secrets into pieces.'),
    ('unlink', 'remove a link', 'The system call (and a command) behind rm.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Delete a file / several', '<code>rm a.txt</code> · <code>rm a.txt b.txt</code>'),
    ('Delete a folder with content', '<code>rm -r dir</code> (look first: <code>ls -R dir</code>)'),
    ('Ask first', '<code>rm -i</code> each · <code>rm -I</code> once'),
    ('Show what was removed', '<code>rm -v</code>'),
    ('Name starting with -', '<code>rm -- -file</code> or <code>rm ./-file</code>'),
    ('Overwrite then delete', '<code>shred -u -z secret.txt</code>'),
]) + '\n' + lv + didyou('In 2017 an engineer at GitLab, tired after a long night of fixing replication, ran a recursive delete on the <b>wrong</b> database server and removed about 300 GB of production data. Five backup methods turned out not to be working. GitLab published the whole story openly; it is now a classic lesson: check the hostname, and test your backups.') + '''
EXAM> “How do you delete a non-empty directory? What is the difference between rm -r, rm -rf and rmdir?” → rmdir only deletes empty directories; rm -r deletes a directory and its contents recursively; -f suppresses prompts and errors for missing files; there is no recycle bin, so use -i/-I or check with ls first.
''' + qc('Why does <code>rm folder</code> fail, while <code>rm -r folder</code> works?', 'Without <code>-r</code>, rm only removes files and says “Is a directory”. <code>-r</code> removes the folder and everything inside it.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Every way to delete, from safest to most dangerous</h2>
''' + table(['Command', 'Deletes', 'Asks?', 'Risk'], [
    ['<code>rmdir dir</code>', 'empty folders only', 'no (refuses if not empty)', '🟢 cannot lose data'],
    ['<code>rm -d dir</code>', 'empty folders only', 'no', '🟢'],
    ['<code>rm -i file…</code>', 'files, after a yes for each', 'every file', '🟡'],
    ['<code>rm file…</code>', 'files', 'only write-protected ones', '🟡'],
    ['<code>rm -I *.log</code>', 'many files', 'once (if more than 3)', '🟡'],
    ['<code>rm -r dir</code>', 'folder and all inside', 'only write-protected ones', '🔴'],
    ['<code>rm -rf dir</code>', 'folder and all inside', 'never', '🔴 check the path twice'],
    ['<code>find . -name "*.tmp" -delete</code>', 'files matching a test', 'never', '🔴 test without -delete first (Lesson 7.1)'],
    ['<code>shred -u file</code>', 'overwrites, then deletes', 'no', '🔴 no recovery at all'],
], minw=600) + mistake('rm -rf /home/riya/project /backup', 'rm -rf "/home/riya/project/backup"',
                       'A space splits a path into two arguments. Put paths in quotes, type them with Tab completion, and read the line before Enter.') + qc('Which is safer for a cleanup script: <code>rmdir</code> or <code>rm -r</code>? Why?', '<code>rmdir</code>: it can only remove empty folders, so a wrong path cannot destroy data.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
danger = '''  <h3 id="danger">The five dangers: read every rm line for these</h3>
  <ol class="fvs">
    <li class="fv"><p class="fv__sit"><b>1 · A space in a path.</b> <code>rm -rf /home/riya/project /backup</code> = two folders. Quote paths: <code>"…"</code>.</p></li>
    <li class="fv"><p class="fv__sit"><b>2 · A wildcard in the wrong place.</b> <code>rm * .log</code> (space!) deletes <b>every</b> file, then complains that “.log” does not exist. Check with <code>echo rm * .log</code> or <code>ls *.log</code> first.</p></li>
    <li class="fv"><p class="fv__sit"><b>3 · An empty variable.</b> If <code>$dir</code> is empty, <code>rm -rf "$dir/"</code> becomes <code>rm -rf /</code>. Use <code>"${dir:?}"</code>, which stops the script when dir is empty (see below).</p></li>
    <li class="fv"><p class="fv__sit"><b>4 · The wrong machine or folder.</b> Check <code>hostname</code> and <code>pwd</code> before a big delete, especially with several terminals open (the GitLab story).</p></li>
    <li class="fv"><p class="fv__sit"><b>5 · -f out of habit.</b> <code>-f</code> hides the warning that would have saved you. Use it in scripts with checked paths, not by default at the keyboard.</p></li>
  </ol>
''' + (lambda r: f'''  <p class="wx__label">Danger 3, seen safely (real run: echo shows what rm would get)</p>
  <div class="code" data-lang="bash" data-file="Terminal"><pre><code>dir=""
echo rm -rf "$dir/"
rm -rf "${{dir:?dir is empty, stopping}}/"</code></pre><div class="output">{E(r)}</div></div>
''')(shlesson.run_sh('dir=""\necho rm -rf "$dir/"\nrm -rf "${dir:?dir is empty, stopping}/"', 'any').rstrip())

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">For every command: when to use it, every important option, one real run, and how it is used in different jobs. Outputs were recorded on Ubuntu 24.04 as the user riya, inside a practice folder.</p>
''' + cmdcard_u(['you are sure what you delete (you looked with ls first)', 'cleaning temporary files, old logs, build output', 'removing a folder tree you created yourself (<code>-r</code>)'],
               ['you are not sure: move it to a trash folder instead', 'the path comes from a variable you have not checked', 'you only want to empty a log a program is writing (use <code>&gt; file</code>)'])(
    'rm', 'rm', 'remove',
    'Deletes files immediately. With <code>-r</code> it deletes folders and everything in them. There is no Recycle Bin.',
    'rm [OPTION]... FILE...', 'danger',
    [('(none)', 'delete files (not folders)', 'everyday single files'),
     ('-r, -R', 'delete folders and their content, all levels', 'removing a whole folder'),
     ('-d', 'delete empty folders (like rmdir)', 'clean up empty folders'),
     ('-i', 'ask before every removal', 'deleting by hand, unsure'),
     ('-I', 'ask once if more than 3 files or recursive', 'everyday safety net (alias)'),
     ('-f', 'never ask, ignore missing files', 'scripts with checked paths'),
     ('-v', 'print every removed file', 'see and log what went'),
     ('--', 'end of options: names may start with -', 'files called -rf, -x'),
     ('--preserve-root (default)', 'refuse to work on /', 'leave it on; never --no-preserve-root')],
    dict(cmd='touch old1.tmp old2.tmp keep.txt\nrm -v old1.tmp old2.tmp\nls', note='Two files removed, one kept. Without <code>-v</code> rm prints nothing when it works.'),
    [('sys', [
        dict(situation='Before deleting a folder, look at what is inside and how big it is.', cmd='mkdir -p oldapp/logs && touch oldapp/app.jar oldapp/logs/a.log\nls -R oldapp\nrm -r oldapp && echo "removed"',
             why='ls -R (or <code>du -sh</code>, Lesson 15.3) first, then delete. Two seconds of looking is the best safety feature.'),
        dict(situation='A full disk: a big log is still being written. Empty it instead of deleting it.', cmd='printf "line\\n%.0s" {1..1000} > app.log\n> app.log\nstat -c "%n %s bytes" app.log',
             why='<code>&gt; app.log</code> truncates to 0 bytes but keeps the file, so the program keeps writing and the space is freed at once. rm on an open file would not free the space (see Advanced).')]),
     ('dev', [
        dict(situation='Clean build output and caches before a fresh build.', cmd='mkdir -p build/obj __pycache__ && touch build/obj/a.o __pycache__/m.pyc\nrm -rv build __pycache__',
             why='Generated folders are safe to delete: they are rebuilt. -v lists everything removed (real projects: <code>make clean</code>, <code>git clean -n</code> first).')]),
     ('data', [
        dict(situation='Remove yesterday’s temporary part files after the job succeeded.', cmd='mkdir -p out && touch out/part-0000{0..3}.tmp out/_SUCCESS\n[ -f out/_SUCCESS ] && rm -v out/*.tmp\nls out',
             why='Delete temp files only after checking the success marker; a failed job keeps its files for debugging.')]),
     ('dba', [
        dict(situation='Delete old dumps, but be asked once because there are many.', cmd='touch dump_{01..05}.sql\necho y | rm -I dump_*.sql; echo\nls dump_* 2>/dev/null | wc -l',
             why='<code>-I</code> asks one question (“remove 5 arguments?”) instead of five. Here the answer y comes from echo; at the keyboard you type it.', expect='any')]),
     ('devops', [
        dict(situation='A cleanup script deletes a release folder from a variable. Protect against an empty variable.', cmd='release=""\nrm -rf "/home/riya/lab/releases/${release:?release not set}" 2>&1; echo "exit status: $?"',
             why='<code>${var:?message}</code> stops with an error if var is empty, so the path can never shrink to <code>/home/riya/lab/releases/</code> (all releases).', expect='any')]),
     ('sec', [
        dict(situation='A file with a strange name created by an attacker or a typo: <code>-rf</code>.', cmd='touch -- -rf\nls\nrm -- -rf\nls | wc -l',
             why='Without <code>--</code>, <code>rm -rf</code> would read it as options. <code>--</code> means “no more options”; <code>rm ./-rf</code> also works.')]),
     ('qa', [
        dict(situation='Reset the test workspace between runs, but never outside it.', cmd='ws=/home/riya/lab/testws\nmkdir -p "$ws/out" && touch "$ws/out/r.txt"\ncase "$ws" in /home/riya/lab/*) rm -rf "$ws" && echo "reset";; *) echo "refusing: $ws";; esac',
             why='A guard checks that the path is inside the expected folder before rm -rf runs.')]),
    ],
    anat=anatomy([('rm', 'cmd', 'command'), ('-rI', 'opt', 'recursive + ask once'), ('--', 'sep', 'end of options'), ('"$dir"', 'arg', 'quoted path')], 'Quotes keep a path with spaces in one piece; <code>--</code> protects against names that start with a dash.')
) + mistake('rm -rf $dir/*', 'rm -rf -- "${dir:?}"/*',
            'Unquoted and unchecked, an empty or space-containing <code>$dir</code> changes what is deleted. Quote it and use <code>:?</code>.') + cmdcard_u(['a file held passwords, keys or personal data on a normal hard disk', 'you are retiring a USB stick or disk (whole device)', 'policy requires overwriting before deletion'],
               ['the disk is an SSD or the file system is copy-on-write (use encryption / secure erase)', 'copies exist elsewhere (backups, git, editor swap files)', 'a normal file you just want gone (plain rm)'])(
    'shred', 'shred', 'overwrite a file to hide its contents',
    'Overwrites the data of a file with random bytes several times, so that it is much harder to recover, and with <code>-u</code> deletes it afterwards.',
    'shred [OPTION]... FILE...', 'danger',
    [('(none)', 'overwrite 3 times with random data, keep the file', 'wiping before reuse'),
     ('-n N', 'number of passes (default 3)', '-n 1 is enough on modern disks'),
     ('-z', 'a final pass of zeros, to hide the shredding', 'less suspicious result'),
     ('-u', 'remove the file after overwriting', 'the usual way to “delete securely”'),
     ('-v', 'show progress', 'big files'),
     ('-s SIZE', 'shred only this many bytes', 'devices')],
    dict(cmd='echo "password=Secret123" > creds.txt\nshred -v -n 1 creds.txt\nstat -c "%n %s bytes" creds.txt\nhead -c 20 creds.txt | od -An -c | head -1', note='After one pass the file is 4096 bytes of random data: shred rounds up to a full disk block, and the text is gone.'),
    [('sec', [
        dict(situation='Remove a leaked API key file from a laptop disk (HDD) securely.', cmd='echo "API_KEY=abc123" > key.txt\nshred -u -z -n 1 key.txt\nls key.txt 2>&1',
             why='-u deletes after overwriting, -z ends with zeros. Then rotate the key anyway: assume a leaked secret is known.', expect='any')]),
     ('sys', [
        dict(situation='Wipe a whole old USB disk before giving it away (needs root).', cmd='sudo shred -v -n 1 -z /dev/sdb',
             typical='shred: /dev/sdb: pass 1/2 (random)...1.2GiB/14GiB 8%\n...\nshred: /dev/sdb: pass 2/2 (000000)...14GiB/14GiB 100%',
             why='Triple-check the device name with <code>lsblk</code> (Lesson 15.1): sdb vs sda is the difference between a USB stick and your system disk.')]),
     ('dba', [
        dict(situation='Destroy a plain-text export of customer data after loading it.', cmd="printf 'id,email\\n1,a@x.in\\n' > export.csv\nshred -u export.csv && echo 'export destroyed'",
             why='Exports often contain personal data; data-protection rules (such as India’s DPDP Act) expect you to dispose of it safely when it is no longer needed.')]),
    ]
) + danger + undo('What if you deleted the wrong thing?', [
    ('Stop writing to that disk:', 'every new file may overwrite the freed blocks. On a server, stop the services writing there.'),
    ('Restore from backup or git:', 'this is the real undo. <code>git checkout -- file</code> or <code>git restore file</code> for tracked files; your rsync backup (Lesson 3.2) for the rest.'),
    ('A program still has it open:', 'the data still exists. Find it with <code>lsof +L1</code> and copy it back from <code>/proc/PID/fd/N</code>.'),
    ('Recovery tools:', '<code>extundelete</code>, <code>photorec</code> or <code>testdisk</code> may find data on ext4, but there is no guarantee. Snapshots (LVM, Btrfs, ZFS, cloud disks) are much better.'),
    ('Prevent it next time:', '<code>alias rm="rm -I"</code>, a trash folder (<code>mv x ~/.trash/</code>, or <code>gio trash x</code> on desktops, or the trash-cli package), and <code>echo</code> in front of risky commands.'),
]) + errors('The errors students see most with rm. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='mkdir reports\nrm reports', meaning='rm deletes only files unless told otherwise.', fix='Empty folder: <code>rmdir reports</code> or <code>rm -d</code>. With content: <code>rm -r reports</code> after <code>ls -R reports</code>.'),
    dict(cmd='rm nofile.txt', meaning='There is no such file (typo, wrong folder, already deleted).', fix='Check with <code>ls</code> and Tab completion. In scripts, <code>-f</code> silences this.'),
    dict(cmd='rm /etc/hostname', meaning='You may not change the folder /etc.', fix='System files need sudo, and you should be very sure before deleting one.'),
    dict(cmd='rm -r .', meaning='rm refuses to delete . or .. (the current or parent folder).', fix='Go up and name the folder: <code>cd ..</code> then <code>rm -r foldername</code>.'),
    dict(cmd='rm -rf /', meaning='The built-in failsafe --preserve-root refused to delete the whole system.', fix='Never override it. (As root, without the failsafe, this would destroy the system.)'),
    dict(cmd='touch -- -x\nrm -x', meaning='rm read “-x” as an option, not a file name.', fix='<code>rm -- -x</code> or <code>rm ./-x</code>.'),
]) + stepper([
    ('1. Where am I?', '<p><code>hostname; pwd</code>: the right machine and folder?</p>', 'Behind the screen: nothing changes; you just read.'),
    ('2. What will go?', '<p><code>ls -l *.tmp</code> or <code>ls -R dir</code>, and for big trees <code>du -sh dir</code>.</p>', 'Behind the screen: the same names rm will receive.'),
    ('3. Is there a copy?', '<p>Important? <code>cp -a</code> or <code>mv</code> it to a backup or trash folder first.</p>', 'Behind the screen: a second name or copy means rm cannot lose the data.'),
    ('4. Preview the command', '<p><code>echo rm -r "$dir"/*.tmp</code> shows the expanded line.</p>', 'Behind the screen: bash expands wildcards and variables exactly as it will for rm.'),
    ('5. Delete with -v (and -I)', '<p><code>rm -vI *.tmp</code></p>', 'Behind the screen: unlinkat() for each name; one question if there are many.'),
    ('6. Check', '<p><code>ls</code> again; on servers, <code>df -h</code> to see the space come back.</p>', 'Behind the screen: blocks freed only if no process still holds the file open.'),
]) + qc('You want to delete all <code>.tmp</code> files but are not sure the pattern is right. What do you run first?', '<code>ls *.tmp</code> or <code>echo rm *.tmp</code>: both show exactly which names rm would receive.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def node(hl, note, tone='blue', count='links: 1'):
    o = label_box(14, 14, 150, 30, ['folder: logs/'], 'card', 8.8)
    o += label_box(14, 52, 150, 30, ['name: app.log'], 'acc' if 0 in hl else 'card', 8.8)
    o += label_box(196, 34, 150, 44, ['inode 8121', count], 'violet' if 1 in hl else 'card', 8.8)
    o += label_box(196, 92, 150, 30, ['data: 20 GB of blocks'], 'blue' if 2 in hl else 'card', 8.8)
    o += label_box(14, 92, 150, 30, ['process: java (open)'], 'green' if 3 in hl else 'card', 8.8)
    return o + t(180, 150, note, 8.8, tone, bold=True)
see = [term(14, 16, 332, 120, ['$ df -h /var', ('/dev/sda2  50G  50G  0  100% /var', 'err')], title='server-01', size=7.8) + cap('The disk is full.', '', 'red', y=150, h=34),
       term(14, 16, 332, 120, ['$ ls -lh /var/log/app.log', ('-rw-r--r-- 1 java java 20G app.log', 'out'), '$ rm /var/log/app.log'], title='server-01', size=7.8) + cap('Riya deletes the 20 GB log.', '', 'blue', y=150, h=34),
       term(14, 16, 332, 120, ['$ df -h /var', ('/dev/sda2  50G  50G  0  100% /var', 'err')], title='server-01', size=7.8) + cap('Still 100%! Where did the space go?', '', 'red', y=150, h=34),
       term(14, 16, 332, 120, ['$ sudo lsof +L1', ('java 812 … 20G 0 /var/log/app.log (deleted)', 'acc')], title='server-01', size=7.4) + cap('The java process still has it open.', '', 'violet', y=150, h=34),
       term(14, 16, 332, 120, ['$ sudo systemctl restart myapp', '$ df -h /var', ('/dev/sda2  50G  30G  20G  60% /var', 'acc')], title='server-01', size=7.6) + cap('Restart (or truncate) → the 20 GB comes back.', '', 'green', y=150, h=34)]
behind = [node([0, 1, 2, 3], 'Name → inode → data. A process also holds it open.'),
          node([1, 2, 3], 'rm removed the NAME. Link count is now 0…', 'blue', 'links: 0'),
          node([1, 2, 3], '…but an open file keeps its inode and data alive.', 'red', 'links: 0, open: 1'),
          node([3], 'lsof +L1 lists open files with 0 links.', 'violet', 'links: 0, open: 1'),
          node([], 'Process closed it: now the blocks are freed.', 'green', 'freed')]
two = anim_two('“Deleted” but the disk is still full', 'What rm really removes',
               'A terminal: the disk is full, a 20 GB log is deleted with rm, df still shows 100%, lsof finds the deleted file still open by java, a restart frees the space.',
               'The file’s name, inode, data and an open process: rm removes the name; the inode and data stay while the process holds the file open; closing it frees the blocks.', see, behind,
               ['A full /var on a server: typical output (shortened).',
                'The biggest file is a 20 GB log; rm deletes it.',
                'df still shows the disk full.',
                '<code>lsof +L1</code> shows a file marked “(deleted)” still open by java.',
                'When the program closes it (restart, or log reopen), the space is free.'],
               ['A file = a name in a folder → an inode → data blocks.',
                'rm (unlink) removes only the name and lowers the link count.',
                'The kernel keeps the inode and data while any process has it open.',
                'Those files are invisible to ls but visible to lsof.',
                'Lesson: to free a log that is being written, truncate it: <code>&gt; app.log</code>.'])

i1 = term(14, 14, 332, 100, ['$ ls', ('report.pdf  notes.txt  a.log  b.log', 'out'), '$ rm * .log', ("rm: cannot remove '.log': No such file or directory", 'err')], title='riya@laptop: ~/lab', size=7.4) + cap('One space between * and .log', '', 'red', y=150, h=34)
i2 = term(14, 14, 332, 100, ['$ ls', ('(empty)', 'dim')], title='riya@laptop: ~/lab', size=7.6) + cap('* alone matched EVERY file: all gone.', '', 'red', y=150, h=34)
i3 = term(14, 14, 332, 100, ['$ echo rm *.log', ('rm a.log b.log', 'acc')], title='riya@laptop: ~/lab', size=7.6) + cap('Preview with echo: exactly the names rm gets.', '', 'blue', y=150, h=34)
i4 = term(14, 14, 332, 100, ['$ rm -I * .log', ('rm: remove 5 arguments? n', 'acc')], title='riya@laptop: ~/lab', size=7.6) + cap('-I asks once when many files are involved.', '', 'green', y=150, h=34)
i5 = (t(180, 30, 'Before every rm with *', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• no space inside the pattern', '• echo rm … or ls … first', '• alias rm="rm -I"', '• quote variables, use ${dir:?}'])) + cap('Wildcards are expanded before rm runs.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario', 'The space that deleted everything',
              'Riya wants to delete the two .log files. The error message matches a real run.',
              'rm and wildcards', 'rm * .log deletes every file because of a space; echo previews the expansion; rm -I asks once.', [i1, i2, i3, i4, i5],
              ['With a space, the shell sees two words: <code>*</code> and <code>.log</code>.',
               '<code>*</code> is every file in the folder; rm deleted them all, then complained about “.log”.',
               '<code>echo rm *.log</code> shows the names first: only a.log and b.log.',
               '<code>rm -I</code> asks a single question when more than three files are involved.',
               'Wildcards are expanded by bash before rm runs (Lesson 3.4).'],
              hid='scenario-star')

dx = dissect('Layer by layer: what happens when you run rm -r project',
    'From what you type down to the disk. Each layer has a real command and its output from our build machine.', [
    dict(key='shell', name='Bash', sub='expands and splits',
         why='rm gets a list of names, not your intentions.',
         how='Bash splits at spaces and expands * and variables first.',
         impl='bash parser.', used='Every command line.',
         cmd='touch a.log b.log; echo rm * .log'),
    dict(key='rm', name='rm', sub='checks options',
         why='One program to delete names.',
         how='Without -r it refuses folders; it refuses / (preserve-root), . and ..',
         impl='/usr/bin/rm, GNU coreutils.', used='Everywhere.',
         cmd='mkdir -p d; rm d 2>&1; echo "exit status: $?"', expect='any'),
    dict(key='walk', name='Tree walk', sub='depth first',
         why='A folder can be removed only when it is empty.',
         how='rm -r deletes files first, then each folder from the bottom up.',
         impl='fts library inside coreutils.', used='rm -r, find -delete.',
         cmd='mkdir -p p/a/b && touch p/a/b/f p/x; rm -rv p'),
    dict(key='unlink', name='unlinkat()', sub='remove a name',
         why='Names and data are separate (inode).',
         how='The kernel removes the folder entry and lowers the link count.',
         impl='Kernel system call; folder needs w permission.', used='rm, mv across disks.',
         cmd='echo x > f; ln f f2; stat -c "links=%h" f; rm f; stat -c "links=%h" f2'),
    dict(key='free', name='Free blocks', sub='not wiped',
         why='Wiping every delete would be slow.',
         how='Blocks are marked free when no name and no open file remain; old data stays until reused.',
         impl='File system block bitmap.', used='Why recovery tools sometimes work, and why shred exists.',
         cmd='echo hi > open.log; exec 3<open.log; rm open.log; cat <&3; echo "(read after rm: still open)"'),
], hint='Top = what you type · bottom = the disk. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What “deleted” really means</h2>
  <p>Left: a real kind of server incident (typical output). Right: what rm changes in the file system.</p>
''' + two + s1 + dx + hood('Under the hood: rm is one system call per name', 'The real file-related system calls of <code>rm notes.txt</code> on our build machine.',
          'rm notes.txt', 'echo hi > notes.txt', 'unlinkat|newfstatat\\(AT_FDCWD, "notes',
          '<p><code>newfstatat</code> checks what the name is; <code>unlinkat(AT_FDCWD, "notes.txt", 0)</code> removes the name. That is all: no data is touched, which is why rm is instant even for huge files.</p>') + qc('A program still writes to a log you deleted with rm. Is the disk space free?', 'No. The inode and data stay until the program closes the file. Truncate logs with <code>&gt; file</code> instead, or restart the program.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Deleting safely at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ find -mtime', 'prompt'), ('+30 -delete', 'acc')], title='admin', size=6.4, step=12),
              '1. Log and temp cleanup', 'Servers delete old logs and temp files by age on a schedule (Lesson 7.1 and cron, Lesson 17.4), after testing the find without -delete.', ['Old files', '*find -delete', 'free disk']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['${dir:?}', 'guards'], 'red', 8.6), '2. Guarded scripts',
    'Production scripts quote every path, stop on empty variables (<code>set -u</code>, <code>:?</code>) and refuse paths outside an allowed folder.', ['Variable', '*check', 'rm -rf']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ > app.log', 'prompt'), ('(truncate)', 'acc')], title='ops', size=6.4, step=12),
    '3. Full disk incidents', 'On-call engineers truncate logs that are still open and look for deleted-but-open files with <code>lsof +L1</code>.', ['Disk 100%', '*truncate', 'space back']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['shred / wipe', 'encryption'], 'violet', 8.6), '4. Data disposal',
    'Security teams destroy exports and retired disks according to policy: shred for HDD files, secure erase or crypto-erase for SSDs.', ['Retire', '*wipe', 'compliant']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['trash/ then', 'delete later'], 'green', 8.6), '5. Soft delete',
    'Many teams move files to a trash or quarantine folder first and empty it after a few days: a cheap undo.', ['mv', '*wait', 'rm']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, safe delete commands. All really run on our build machine.', [
    dict(level='b', title='Delete all .tmp files, see what went', scenario='Clean temporary files in the current folder.',
         cmd='touch a.tmp b.tmp keep.txt && rm -v *.tmp && ls',
         explain='-v lists every removed file; keep.txt stays.'),
    dict(level='b', title='Delete everything except one file', scenario='Keep only README.md in a folder.',
         cmd='touch a b c README.md && shopt -s extglob\nrm -v !(README.md) && ls',
         explain='extglob’s <code>!(…)</code> = everything except (Lesson 3.4).'),
    dict(level='i', title='Your own trash bin', scenario='Delete with an undo for one week.',
         cmd='mkdir -p ~/.trash && touch old.csv && mv -v old.csv ~/.trash/ && ls ~/.trash',
         explain='A move instead of a delete. Later: <code>find ~/.trash -mtime +7 -delete</code>.'),
    dict(level='i', title='Delete empty folders only', scenario='A tree has many empty folders after cleanup.',
         cmd='mkdir -p t/{a,b/c,d} && touch t/d/x && find t -type d -empty -delete && find t',
         explain='find -empty selects empty folders; -delete removes them bottom up (Lesson 7.1).'),
    dict(level='a', title='Free space from an open log', scenario='A program writes to a huge log; free the space without stopping it.',
         cmd='printf "%.0sx" {1..5000} > live.log && stat -c "%s bytes" live.log && truncate -s 0 live.log && stat -c "%s bytes" live.log',
         explain='truncate (or <code>&gt; live.log</code>) empties the file in place; the program keeps its handle.'),
], extra=build_up('a safe cleanup script', 'Riya must delete old .tmp files in a work folder from a script.',
    'mkdir -p work && touch work/a.tmp work/b.tmp work/keep.csv', [
    ('dir=work; ls "$dir"/*.tmp', '1. Look: which files match?'),
    ('dir=work; echo rm -v "$dir"/*.tmp', '2. Preview the exact command.'),
    ('dir=work; [ -d "${dir:?}" ] && rm -v "$dir"/*.tmp', '3. Guard: dir must be set and be a folder.'),
    ('dir=work; [ -d "${dir:?}" ] && rm -v "$dir"/*.tmp && ls "$dir"', '4. Check what is left.'),
])) + which('Choosing the right delete.', [
    ('One file', 'rm file', 'Simple.', 'rm -rf file out of habit.'),
    ('A folder with content', 'rm -r dir', 'Recursive.', 'Not looking inside first.'),
    ('An empty folder', 'rmdir dir', 'Cannot lose data.', 'rm -rf for an “empty” folder.'),
    ('Many files by hand', 'rm -I *.log', 'One question.', 'rm * .log (space).'),
    ('From a script', 'rm -rf -- "${d:?}"', 'Quoted, guarded.', 'rm -rf $d/ with empty d.'),
    ('A log a program writes', '> app.log', 'Frees space now.', 'rm (space stays used).'),
    ('A secret on an HDD', 'shred -u -z file', 'Overwrites first.', 'Trusting shred on SSD.'),
    ('Maybe needed later', 'mv x ~/.trash/', 'Undo possible.', 'rm “just to tidy up”.'),
]) + keys('Shortcuts that make deleting safer.', [
    ('alias rm="rm -I"', 'one safety question for big deletes (~/.bashrc)', 'rm *.log → asks once'),
    ('Tab', 'complete names: no typos, no stray spaces', 'rm rep⇥'),
    ('echo first', 'preview what bash will pass to rm', 'echo rm *.tmp'),
    ('Ctrl + C', 'stop a running rm (what is gone stays gone)', 'rm -rv big/ … Ctrl+C'),
    ('!$', 'reuse a checked path', 'ls -R old/ && rm -r !$'),
    ('set -u', 'scripts stop on empty variables', 'set -u; rm -rf "$dir"'),
]) + scriptit('cleanup.sh', 'A cleanup script with every safety net from this lesson: strict mode, a guarded folder, a preview, and a log of what was removed. (You will learn set -euo pipefail in Lesson 12.6.)',
'''#!/bin/bash
set -euo pipefail
dir=${1:-/home/riya/lab/tmpwork}
mkdir -p "$dir" && touch "$dir"/{a,b}.tmp "$dir"/keep.csv     # demo files
case "$dir" in
  /home/riya/lab/*) ;;                       # allowed area only
  *) echo "refusing to clean $dir" >&2; exit 1 ;;
esac
shopt -s nullglob
files=("$dir"/*.tmp)
echo "will delete ${#files[@]} file(s)"
[ ${#files[@]} -gt 0 ] && rm -v -- "${files[@]}"
ls "$dir"''',
'<p><code>nullglob</code> makes <code>*.tmp</code> expand to nothing when there are no matches, instead of the literal text “*.tmp”.</p>') + puzzle_answer('rm did work: it removed the <b>name</b>. But a program (here the application writing the log) still had the file open. The kernel keeps the inode and its 20 GB of data until the last open handle is closed. <code>lsof +L1</code> shows such “(deleted)” files. Restart or reload the program, or next time empty the log with <code>&gt; app.log</code> (truncate) instead of deleting it.') + qc('Your script has <code>rm -rf "$BUILD_DIR"/*</code>. What happens if BUILD_DIR is empty, and how do you prevent it?', 'It becomes <code>rm -rf /*</code>. Use <code>"${BUILD_DIR:?}"</code> or <code>set -u</code>, and check the path is inside the expected folder.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-copying-moving-and-syncing-cp-mv-and-rsync/">Lesson 3.2</a>: copying and backups, so you have a copy before you delete.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
