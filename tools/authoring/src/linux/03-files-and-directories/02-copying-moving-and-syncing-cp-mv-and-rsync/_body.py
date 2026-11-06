import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# rsync is not installed on our build machine: these outputs were recorded on Ubuntu 22.04 with rsync 3.2.7 (6 Nov 2026).
RS = 'Recorded on Ubuntu 22.04 · rsync 3.2.7'
R1 = '''sending incremental file list
created directory backup
./
app.log
schema.sql
dumps/
dumps/day1.sql

sent 347 bytes  received 113 bytes  920.00 bytes/sec
total size is 6  speedup is 0.01'''
R2 = '''sending incremental file list

sent 198 bytes  received 13 bytes  422.00 bytes/sec
total size is 6  speedup is 0.03'''
R3 = '''sending incremental file list
schema.sql
dumps/day2.sql

sent 315 bytes  received 59 bytes  748.00 bytes/sec
total size is 10  speedup is 0.03'''
R4 = '''backup2
backup2/db_backup
backup2/db_backup/app.log
backup2/db_backup/dumps
backup2/db_backup/dumps/day1.sql
backup2/db_backup/dumps/day2.sql
backup2/db_backup/schema.sql'''
R5 = '''backup3
backup3/app.log
backup3/dumps
backup3/dumps/day1.sql
backup3/dumps/day2.sql
backup3/schema.sql'''
R6 = '''sending incremental file list
deleting app.log

sent 197 bytes  received 31 bytes  456.00 bytes/sec
total size is 8  speedup is 0.04 (DRY RUN)'''
R8 = '''sending incremental file list
created directory clean
./
schema.sql

sent 180 bytes  received 66 bytes  492.00 bytes/sec
total size is 4  speedup is 0.02'''
R10 = '''sending incremental file list
created directory backup5
cd+++++++++ ./
>f+++++++++ schema.sql
cd+++++++++ dumps/'''

HOOK = hook('Riya copied her 10 GB project folder to the backup disk on Monday. On Tuesday she changed two files. Copying all 10 GB again takes an hour; copying by hand means remembering which two files changed. And yesterday Kabir “moved” a folder and could not find it any more. This lesson ends all three problems.',
    ['copy files and whole folders, with or without their dates and permissions (<code>cp</code>, <code>cp -r</code>, <code>cp -a</code>)',
     'never overwrite a file by accident (<code>-i</code>, <code>-n</code>, <code>--backup</code>)',
     'move and rename files and folders, and know why mv is instant (<code>mv</code>)',
     'keep a backup up to date by copying only what changed (<code>rsync -av</code>, <code>--delete</code>, <code>--dry-run</code>)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the backup problem'),
    ('decide', 'Which command when?', 2, 'cp, mv or rsync?'),
    ('definition', 'What the commands are', 5, 'simple meaning + 4 depths'),
    ('commands', 'cp, mv, rsync by field', 14, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 5, 'why mv is instant, what rsync skips'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('cp, mv or rsync? (decide in 5 seconds)', [
    ('Make a second copy of a file', 'cp file copy', 'original stays'),
    ('Copy a whole folder', 'cp -r dir dest/', 'without -r: “omitting directory”'),
    ('Copy and keep dates, permissions', 'cp -a dir dest/', 'a = archive, for backups'),
    ('Copy but never overwrite', 'cp -i / --update=none', 'asks / skips existing'),
    ('Rename a file or folder', 'mv old new', 'instant, no copy'),
    ('Move into another folder', 'mv file dir/', 'original disappears'),
    ('Update a backup (only changes)', 'rsync -av src/ dest/', 'second run copies nothing'),
    ('Make the backup an exact mirror', 'rsync -av --delete src/ dest/', 'try --dry-run first!'),
    ('Copy to another server', 'rsync -avz src/ user@host:dir/', 'or scp (Lesson 16.6)'),
    ('Rename 100 files by a pattern', 'rename', 'Lesson 3.7'),
])

cmap = concept_map(
    [('3.1', 'Creating files and folders', 'something to copy'), ('2.3', 'Paths', 'source and destination'), ('2.4', 'stat and timestamps', 'what -a preserves')],
    ['cp: files, folders (-r), with attributes (-a)', 'safe copying: -i, -n / --update=none, -u, --backup', 'mv: move and rename; why it is instant', 'rsync: copy only what changed; --delete, --dry-run, --exclude', 'trailing slash rules of rsync'],
    [('3.3', 'Deleting safely', 'rm after a copy'), ('3.7', 'Bulk renaming', 'rename many files'), ('10.2', 'Hard and soft links', 'cp -l, cp -s'), ('16.6', 'scp and rsync over SSH', 'copy between servers')],
    'Copying, moving and syncing are the three ways data travels on a Linux system. Pick the right one and you save hours, and never lose a file.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 150, ['$ rsync -av project/ /backup/project/', ('… 2,431 files copied (Monday, 58 min)', 'dim'), '$ # Tuesday: two files changed', '$ rsync -av project/ /backup/project/', ('reports/march.csv', 'acc'), ('scripts/clean.py', 'acc'), ('sent 41 KB … (3 seconds)', 'out')], title='riya@laptop: ~', size=7.6, step=15)
      + t(352, 36, 'One command, three tools:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• cp: make a copy', '• mv: move or rename', '• rsync: copy only changes', '• Tuesday: 3 s, not 58 min', '(illustration; sizes vary)'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The one-hour backup that became three seconds</h2>
  <div class="story">
''' + puzzle('Moving a 5 GB file to another folder on the <b>same disk</b> with <code>mv</code> takes less than a second. Copying it with <code>cp</code> takes about a minute. Why is mv so much faster, when the file ends up in the same place?') + '''
    <p class="narration">Riya keeps her DBDA project on her laptop and a backup on an external disk. Every evening she copies the whole folder again “to be safe”. It takes almost an hour. Kabir has the opposite problem: he dragged a folder somewhere and now cannot find it.</p>
''' + scene('A terminal: the first rsync copies all files, the second rsync on the next day copies only two changed files in seconds.', sc,
            'Copy once with <tspan font-weight="700" class="s-acc">rsync</tspan>; after that it sends only what changed.') + '''
A> Riya, <code>cp -r</code> copies everything, every time. <code>rsync -av</code> compares both sides and sends only the files that changed. The first run is the same; every run after that takes seconds.
R> And if I delete a file in my project, does it disappear from the backup too?
A> Only if you ask: <code>--delete</code>. Always try <code>--dry-run</code> first to see what it would do.
K> And my lost folder?
A> <code>mv</code> moves <b>and</b> renames. If the target name did not exist as a folder, your folder was renamed to that name. <code>mv -v</code> tells you exactly what happened. Today: <code>cp</code>, <code>mv</code> and <code>rsync</code>, each explained, then used by developers, DBAs, data engineers, DevOps and security teams.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pics = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="cp is a photocopier: the original stays. mv is changing the label on a cupboard: nothing is carried. rsync is a teacher checking which pages are new and copying only those.">'
        + ''.join(label_box(16 + k * 208, 22, 192, 110, [a, b, c, d], tone, 9.4) for k, (a, b, c, d, tone) in enumerate([
            ('cp = photocopier', 'original stays', 'a new copy is made', 'takes time for big files', 'blue'),
            ('mv = new label', 'nothing is carried', 'the name or place changes', 'instant on the same disk', 'green'),
            ('rsync = smart copier', 'compares both sides', 'copies only new pages', 'second time: seconds', 'violet')]))
        + t(320, 160, 'Copy when you need two. Move when you need it elsewhere.', 9.6, 'ink2')
        + t(320, 182, 'Sync when you copy the same folder again and again.', 9.6, 'acc', bold=True)
        + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Copying, moving and syncing at four depths', [
    ('v', 'No jargon: photocopier, label, smart copier', '      <p>Three everyday ideas.</p>' + pics + '''
      <ul>
        <li><b>cp</b> is a photocopier: after it, you have two of the same thing.</li>
        <li><b>mv</b> just changes where a thing is or what it is called. Renaming a file is “moving” it to a new name.</li>
        <li><b>rsync</b> looks at the copy you already have and only adds what is new or changed.</li>
      </ul>'''),
    ('b', 'The commands you will type every day', '''      <ul>
        <li><code>cp a.txt b.txt</code> copies a file; <code>cp a.txt backup/</code> copies it into a folder, keeping its name.</li>
        <li><code>cp -r project backup/</code>: folders need <code>-r</code> (recursive).</li>
        <li><code>mv old.txt new.txt</code> renames; <code>mv file.txt archive/</code> moves. mv works on folders without any option.</li>
        <li>Both cp and mv <b>overwrite</b> an existing target without asking. Add <code>-i</code> to be asked.</li>
        <li><code>rsync -av src/ dest/</code> copies a folder and, next time, only the changes.</li>
      </ul>'''),
    ('i', 'Attributes, safety and the trailing slash', '''      <ul>
        <li>Plain <code>cp</code> gives the copy a new date and makes you the owner. <code>-p</code> keeps date and permissions; <code>-a</code> (archive) keeps everything and copies folders, links included. Use <code>-a</code> for backups.</li>
        <li>No overwrite: <code>-i</code> asks, <code>--update=none</code> skips (older <code>-n</code>), <code>-u</code> only replaces if the source is newer, <code>--backup=numbered</code> keeps the old one as <code>file.~1~</code>.</li>
        <li>rsync’s slash rule: <code>rsync -a src/ dest/</code> copies the <b>contents</b> of src; <code>rsync -a src dest/</code> creates <code>dest/src</code>.</li>
        <li><code>--delete</code> removes files from the destination that are no longer in the source: an exact mirror. Always <code>-n</code> (<code>--dry-run</code>) first.</li>
      </ul>'''),
    ('a', 'Behind the screen: why mv is instant', '''      <ul>
        <li>A folder is a list of <b>names → inode numbers</b>. On the same file system, <code>mv</code> calls <code>rename()</code>: it moves the name to another list. The data and inode do not move at all, which is why a 5 GB mv takes milliseconds (the inode number stays the same).</li>
        <li>Across file systems (laptop → USB disk), rename() is impossible, so mv <b>copies then deletes</b>: just as slow as cp.</li>
        <li><code>cp</code> creates a new inode and copies the data block by block. Modern cp can use <code>copy_file_range()</code> or reflinks (<code>--reflink=auto</code> on Btrfs/XFS) to share blocks.</li>
        <li><code>rename()</code> is <b>atomic</b>: other programs see either the old or the new name, never half. That is why programs write <code>file.tmp</code> and then <code>mv file.tmp file</code>.</li>
        <li>rsync decides “changed?” by size and modification time (quick check). With <code>-c</code> it compares checksums. Over a network it sends only the changed <b>parts</b> of a file (delta transfer).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>cp, mv and rsync</h2>
''' + def_block(
    '<code>cp</code> (copy) copies files, and with <code>-r</code> or <code>-a</code> whole directory trees, creating new files at the destination. <code>mv</code> (move) moves or renames files and directories; on the same file system it only changes directory entries, so the data is not copied. <code>rsync</code> (remote sync) copies files locally or between computers and, on later runs, transfers only files that are new or changed; it can also delete extra files at the destination to make an exact mirror.',
    '<code>cp</code> = make a copy, <code>mv</code> = move or rename, <code>rsync</code> = copy only what changed.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Source, destination', 'Where you copy from, and to. Source first, destination last.'),
    ('Recursive (-r)', 'Into every folder and sub-folder.'),
    ('Attributes', 'Owner, permissions and timestamps of a file.'),
    ('Overwrite (clobber)', 'Replace an existing file with the same name.'),
    ('Atomic', 'Happens completely or not at all; never half.'),
    ('Inode', f'The record that holds a file’s details. {gl("inode", "Glossary →")}'),
    ('Mirror', 'A copy that is exactly the same, extra files removed.'),
    ('scp vs rsync', f'Copying to another computer. {gl("scp-vs-rsync", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('cp', 'copy', 'Two letters, like most early Unix commands.'),
    ('mv', 'move', 'Renaming is moving to a new name.'),
    ('rsync', 'remote sync', 'Written by Andrew Tridgell and Paul Mackerras in 1996.'),
    ('-r / -R', 'recursive', 'Go into every sub-folder.'),
    ('-a', 'archive', 'Keep everything, like an archive would.'),
    ('-i', 'interactive', 'Ask me before overwriting.'),
    ('-n (cp, mv)', 'no-clobber', 'Never overwrite. (In rsync, -n means dry run!)'),
    ('-u', 'update', 'Only if the source is newer.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Copy a file / into a folder', '<code>cp a.txt b.txt</code> · <code>cp a.txt dir/</code>'),
    ('Copy a folder', '<code>cp -r dir dest/</code> · backup: <code>cp -a</code>'),
    ('Ask before overwriting', '<code>cp -i</code> · <code>mv -i</code>'),
    ('Rename / move', '<code>mv old new</code> · <code>mv f dir/</code>'),
    ('Sync a backup', '<code>rsync -av src/ dest/</code>'),
    ('Preview a mirror', '<code>rsync -av --delete --dry-run src/ dest/</code>'),
]) + '\n' + lv + didyou('The rsync algorithm was the subject of Andrew Tridgell’s PhD thesis at the Australian National University. Its trick: the receiver sends checksums of blocks it already has, so the sender only transmits the blocks that differ. That is why rsync can update a huge file over a slow link by sending a few kilobytes.') + '''
EXAM> “Difference between cp and mv” → cp creates a copy and the original stays; mv moves or renames and the original name disappears; cp needs -r for directories, mv does not; on the same file system mv only changes directory entries (fast), across file systems it copies and deletes.
''' + qc('After <code>cp report.txt backup/</code>, how many report.txt files exist? After <code>mv report.txt backup/</code>?', 'cp: two (original and copy). mv: one, now inside backup/.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>cp vs mv vs rsync</h2>
''' + table(['', 'cp', 'mv', 'rsync'], [
    ['Original after it', 'stays', 'gone (moved)', 'stays'],
    ['Folders', 'needs <code>-r</code> or <code>-a</code>', 'works as is', 'needs <code>-r</code> (in <code>-a</code>)'],
    ['Second run on same data', 'copies everything again', '—', 'copies only changes'],
    ['Keeps dates and permissions', 'only with <code>-p</code> / <code>-a</code>', 'yes (same file)', 'with <code>-a</code>'],
    ['Overwrites existing files', 'yes, silently', 'yes, silently', 'yes, if different'],
    ['Deletes extra files at target', 'no', 'no', 'only with <code>--delete</code>'],
    ['To another computer', 'no', 'no', 'yes (over SSH)'],
    ['Speed on the same disk', 'reads and writes all data', 'instant (rename)', 'like cp first time'],
    ['Installed by default', 'yes (coreutils)', 'yes (coreutils)', 'usually; else <code>sudo apt install rsync</code>'],
], minw=600) + '''
  <h3>The three ways to write a copy</h3>
''' + table(['Form', 'Meaning', 'Example'], [
    ['<code>cp SOURCE DEST</code>', 'copy to a new name', '<code>cp db_schema.txt backup_db_schema.txt</code>'],
    ['<code>cp SOURCE... DIRECTORY</code>', 'copy one or more into a folder (names kept)', '<code>cp a.csv b.csv reports/</code>'],
    ['<code>cp -t DIRECTORY SOURCE...</code>', 'folder first (handy with xargs, Lesson 13.2)', '<code>cp -t reports/ a.csv b.csv</code>'],
], minw=520) + mistake('rsync -av project /backup/project/     (to copy the contents)', 'rsync -av project/ /backup/project/',
                       'Without the trailing slash, rsync creates <code>/backup/project/project/</code>. With the slash on the source, it copies what is <b>inside</b> project. cp -r has the same idea in a different form.') + qc('Which of the three keeps the file’s original modification date by default?', 'mv (it is the same file). cp only with <code>-p</code> or <code>-a</code>; rsync with <code>-a</code> (or <code>-t</code>).') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">For every command: when to use it, every important option, one real run, and how it is used in different jobs. cp and mv outputs were recorded on Ubuntu 24.04; rsync outputs on Ubuntu 22.04 (rsync 3.2.7), because our build machine has no rsync.</p>
''' + cmdcard_u(['you need a second copy and the original must stay', 'you take a quick backup before editing a file', 'you copy a whole folder once (<code>-a</code> or <code>-r</code>)'],
               ['you copy the same big folder again and again (use rsync)', 'you only want to move or rename (mv is instant)', 'you copy to another server (rsync or scp)'])(
    'cp', 'cp', 'copy',
    'Copies files. With <code>-r</code> it copies folders and everything inside; with <code>-a</code> it also keeps dates, permissions and links. The original is never changed.',
    'cp [OPTION]... SOURCE DEST  ·  cp [OPTION]... SOURCE... DIRECTORY', 'change',
    [('(none)', 'copy file(s); overwrites the target silently', 'one-off copies'),
     ('-r, -R', 'copy folders recursively', 'any folder'),
     ('-a, --archive', 'recursive + keep dates, permissions, owner (if allowed), links', 'backups, moving projects'),
     ('-p', 'keep mode, owner and timestamps (files)', 'copy a file but keep its date'),
     ('-i', 'ask before overwriting', 'interactive work, safety'),
     ('--update=none (old: -n)', 'never overwrite an existing file', 'scripts that must not replace files'),
     ('-u, --update', 'copy only when the source is newer or the target is missing', 'quick manual refresh'),
     ('-v', 'print each copy', 'see what happened'),
     ('--backup=numbered', 'keep the old target as name.~1~, ~2~ …', 'overwrite but keep history'),
     ('-l / -s', 'make a hard / symbolic link instead of copying', 'Lesson 10.2')],
    dict(cmd='mkdir -p backup\necho "id,name" > db_schema.txt\ncp db_schema.txt backup/\ncp db_schema.txt backup/backup_db_schema.txt\nls backup', note='First into the folder with the same name, then with a new name. db_schema.txt itself is untouched.'),
    [('dev', [
        dict(situation='Take a safety copy of a config file before editing it.', cmd='echo "port=80" > app.conf\ncp -v app.conf app.conf.bak',
             why='A <code>.bak</code> copy next to the file lets you undo your edit with <code>cp app.conf.bak app.conf</code>. -v confirms what was copied.'),
        dict(situation='Start a new project from a template folder.', cmd='mkdir -p template/{src,tests} && touch template/README.md\ncp -r template newapp && find newapp | sort',
             why='-r copies the folder with everything inside. The new folder name is the destination.')]),
     ('dba', [
        dict(situation='Copy a dump into the backup folder, keeping its original date (so “newest backup” stays correct).', cmd="echo 'dump' > night.sql && touch -d '2026-11-05 23:00' night.sql\ncp night.sql b1.sql; cp -p night.sql b2.sql\nfor f in night b1 b2; do echo \"$f.sql $(date -r $f.sql '+%F %H:%M')\"; done",
             why='Plain cp gives the copy the current time; <code>-p</code> keeps 23:00 of last night. Backup tools and clean-up scripts rely on these dates.')]),
     ('sys', [
        dict(situation='Copy a folder with all its permissions and dates, e.g. a home folder or website.', cmd='mkdir -p site && echo hi > site/index.html && chmod 640 site/index.html\ncp -a site site_copy && stat -c "%A %n" site/index.html site_copy/index.html',
             why='<code>-a</code> keeps rw-r----- exactly. With plain cp -r, permissions are recalculated with your umask.')]),
     ('data', [
        dict(situation='Copy today’s CSV files into the input folder of a pipeline.', cmd='touch sales_{north,south}.csv\nmkdir -p input && cp -v sales_*.csv input/',
             why='Several sources and a folder at the end. The wildcard is expanded by bash (Lesson 3.4).')]),
     ('qa', [
        dict(situation='Refresh test fixtures without destroying files a tester already changed by hand.', cmd="mkdir -p fixtures && echo 'edited' > fixtures/users.csv\necho 'fresh' > users.csv\ncp --update=none users.csv fixtures/\ncat fixtures/users.csv",
             why='<code>--update=none</code> skips files that already exist. Old guides write <code>-n</code>; on Ubuntu 24.04 cp now warns that -n is non-portable.')]),
     ('sec', [
        dict(situation='Overwrite a config but keep every previous version for audit.', cmd="echo v1 > fw.rules; echo v2 > new.rules\ncp --backup=numbered new.rules fw.rules\necho v3 > new.rules; cp --backup=numbered new.rules fw.rules\nls fw.rules*",
             why='Each overwrite saves the previous file as <code>.~1~</code>, <code>.~2~</code>: you can see and restore exactly what changed.')]),
     ('devops', [
        dict(situation='Copy a release into a numbered folder on the server.', cmd='mkdir -p build && echo jar > build/app.jar\nmkdir -p releases/v42 && cp -a build/. releases/v42/ && ls releases/v42',
             why='<code>build/.</code> means “the contents of build”, so files land directly in v42 (no extra build/ folder inside).')]),
    ],
    anat=anatomy([('cp', 'cmd', 'command'), ('-av', 'opt', 'archive + verbose'), ('db_backup/', 'arg', 'source'), ('/home/user/backup/', 'arg', 'destination (last)')], 'Source(s) first, destination <b>last</b>. If the last argument is an existing folder, the files go inside it.')
) + mistake('cp -n test_info.txt backup/     (Ubuntu 24.04 prints a warning)', 'cp --update=none test_info.txt backup/',
            'Many notes still teach <code>cp -n</code>. It works, but coreutils 9.x warns: “behavior of -n is non-portable and may change in future; use --update=none instead”.') + cmdcard_u(['you rename a file or folder', 'you move something into another folder', 'you publish a finished file atomically (<code>mv tmp final</code>)'],
               ['you still need the original (use cp)', 'you rename 100 files by a pattern (use rename, Lesson 3.7)', 'the target name exists and you have not checked (use <code>-i</code>)'])(
    'mv', 'mv', 'move',
    'Moves files and folders to another place, or gives them a new name. The original name disappears. Folders need no option.',
    'mv [OPTION]... SOURCE DEST  ·  mv [OPTION]... SOURCE... DIRECTORY', 'change',
    [('(none)', 'move or rename; overwrites the target silently', 'everyday moves'),
     ('-i', 'ask before overwriting', 'when the target may exist'),
     ('-n, --no-clobber', 'never overwrite', 'scripts'),
     ('-u', 'move only if the source is newer', 'merging folders'),
     ('-v', 'print each move', 'see what happened'),
     ('-b / --backup', 'keep the overwritten file as name~', 'safety'),
     ('-t DIR', 'target folder first', 'with xargs or find')],
    dict(cmd='mkdir -p backup\necho "schema" > db_schema.txt\nmv -v db_schema.txt backup/db_backup.txt\nls; ls backup', note='Moved and renamed in one step: db_schema.txt is gone from the current folder.'),
    [('sys', [
        dict(situation='Rename a log file before the application starts a new one (manual log rotation).', cmd='echo "old lines" > app.log\nmv app.log app.log.1 && touch app.log\nls app.log*',
             why='This is what <code>logrotate</code> does every night (Lesson 18.1). The running program keeps writing to the renamed file until it reopens.')]),
     ('devops', [
        dict(situation='Deploy a new config without any moment where the file is half-written.', cmd="printf 'port=8080\\nworkers=4\\n' > app.conf.tmp\nmv app.conf.tmp app.conf && cat app.conf",
             why='rename() is atomic: the app sees the old file or the new one, never a half-written one. Write to a temp name, then mv.')]),
     ('data', [
        dict(situation='Move processed files out of the incoming folder so they are not processed twice.', cmd='mkdir -p incoming done && touch incoming/{a,b,c}.csv\nmv incoming/*.csv done/ && ls incoming done',
             why='A classic pipeline pattern: incoming → processing → done (or failed). Moving is instant, even for big files.')]),
     ('dev', [
        dict(situation='Rename a folder in a project.', cmd='mkdir -p src/utils && touch src/utils/helpers.py\nmv src/utils src/common && find src',
             why='Folders need no option. (In a git project use <code>git mv</code> so git records it as a rename.)')]),
     ('qa', [
        dict(situation='Check what mv does when the target exists, safely.', cmd='echo a > a.txt; echo b > b.txt\nmv -n a.txt b.txt; cat b.txt; ls',
             why='<code>-n</code> refuses to overwrite; both files stay. Without it, b.txt would be replaced by a.txt silently.', expect='any')]),
     ('sec', [
        dict(situation='Quarantine a suspicious file: take it out of the web folder without deleting the evidence.', cmd='mkdir -p www quarantine && echo "<?php ... ?>" > www/shell.php\nmv -v www/shell.php quarantine/shell.php.txt && chmod 000 quarantine/shell.php.txt && stat -c "%A %n" quarantine/*',
             why='Moving keeps the original data and inode for investigation; renaming to .txt and chmod 000 stop it from running or being served.')]),
    ]
) + cmdcard_u(['you copy the same folder again and again (backups)', 'you need an exact mirror (<code>--delete</code>)', 'you copy to or from another server over SSH'],
               ['a one-time copy of a few files (cp is simpler)', 'rsync is not installed (<code>sudo apt install rsync</code>)', 'you are not sure about <code>--delete</code> and skipped <code>--dry-run</code>'])(
    'rsync', 'rsync', 'remote sync',
    'Copies files and folders like cp, but on every later run it sends only what is new or changed. It can mirror (delete extras), exclude patterns, show a preview, and work between computers.',
    'rsync [OPTION]... SRC... DEST', 'change',
    [('-a', 'archive: recursive, keep permissions, times, links, owner', 'almost always'),
     ('-v', 'list the files it sends', 'see what changed'),
     ('-z', 'compress during the transfer', 'over a network'),
     ('-n, --dry-run', 'show what would happen, change nothing', 'before --delete, always'),
     ('--delete', 'delete files in DEST that are not in SRC', 'exact mirrors'),
     ('--exclude=PATTERN', 'skip matching files or folders', 'logs, caches, node_modules'),
     ('-i, --itemize-changes', 'show why each file is sent', 'debugging'),
     ('--progress / -P', 'progress bar (and resume partial files)', 'big files'),
     ('-e ssh', 'use SSH to reach another computer', 'remote copies (default today)'),
     ('src/ vs src', 'slash = copy the contents; no slash = copy the folder itself', 'the most common mistake')],
    dict(cmd='rsync -av db_backup/ backup/', note='The first run copies everything (like cp -a) and creates the destination.', rec=(RS, R1)),
    [('dba', [
        dict(situation='Nightly: update the backup of the database dump folder. Nothing changed since yesterday.', cmd='rsync -av db_backup/ backup/', rec=(RS, R2),
             why='No file names are listed: nothing was sent. On a real 10 GB folder this run takes seconds.'),
        dict(situation='Next night: schema.sql changed and a new dump appeared.', cmd='rsync -av db_backup/ backup/', rec=(RS, R3),
             why='Only the two changed files are sent. This is the whole point of rsync.')]),
     ('sys', [
        dict(situation='Make the backup an exact mirror: app.log was deleted in the source. Preview first.', cmd='rsync -av --delete --dry-run db_backup/ backup/', rec=(RS, R6),
             why='“deleting app.log … (DRY RUN)”: nothing was deleted yet. Read the list; only then run again without --dry-run.'),
        dict(situation='The trailing slash: copy the folder itself vs its contents.', cmd='rsync -a db_backup backup2/; find backup2 | sort', rec=(RS, R4),
             why='No slash on the source → a <code>db_backup</code> folder inside backup2. Compare the next one.'),
        dict(situation='The same with a slash.', cmd='rsync -a db_backup/ backup3/; find backup3 | sort', rec=(RS, R5),
             why='With the slash, the <b>contents</b> go straight into backup3.')]),
     ('dev', [
        dict(situation='Copy a project but skip logs and generated folders.', cmd="rsync -av --exclude='*.log' --exclude='dumps/' db_backup/ clean/", rec=(RS, R8),
             why='Excludes keep backups small: typical ones are <code>node_modules/</code>, <code>.venv/</code>, <code>__pycache__/</code>, <code>*.log</code>.')]),
     ('devops', [
        dict(situation='Deploy a built website to a web server over SSH.', cmd='rsync -avz --delete public/ deploy@web01:/var/www/site/',
             typical='sending incremental file list\nindex.html\ncss/site.css\n\nsent 4,812 bytes  received 64 bytes  3,250.67 bytes/sec\ntotal size is 182,330  speedup is 37.39',
             why='-z compresses, SSH encrypts, --delete removes pages you deleted locally. Only changed pages are uploaded.')]),
     ('net', [
        dict(situation='Pull logs from a server to your laptop, resumable on a bad connection.', cmd='rsync -avzP user@app01:/var/log/myapp/ ./app01-logs/',
             typical='receiving incremental file list\napp.log\n     52,428,800 100%   11.20MB/s    0:00:04 (xfr#1, to-chk=0/2)',
             why='-P = --partial --progress: if the connection drops, the next run continues the half-transferred file.')]),
     ('qa', [
        dict(situation='Why was this file sent? Itemized changes.', cmd='rsync -avi db_backup/ backup5/ | head -5', rec=(RS, R10),
             why='<code>&gt;f+++++++++</code> = a new file sent; on updates you see letters such as <code>s</code> (size) and <code>t</code> (time) that explain the reason.')]),
    ]
) + mistake('rsync -av --delete src/ dest/     (first time, without checking)', 'rsync -av --delete --dry-run src/ dest/   then the same without --dry-run',
            'If source and destination are swapped, or the source is empty (a disk not mounted), --delete makes the destination match: it deletes your backup. Always preview.') + undo('What if a copy or move went wrong?', [
    ('Overwrote a file with cp or mv:', '<b>no undo</b>. Only a backup, git or a snapshot helps. Prevent it with <code>-i</code>, <code>--update=none</code>, or <code>--backup=numbered</code>; many people add <code>alias cp="cp -i"</code> and <code>alias mv="mv -i"</code> to ~/.bashrc.'),
    ('Moved something and cannot find it:', 'mv into an existing folder puts it <b>inside</b>; into a new name renames it. Look with <code>ls -lt</code> in the target, or <code>find ~ -name "name"</code> (Lesson 7.1). Next time use <code>mv -v</code>.'),
    ('Copied into the wrong place:', 'just delete the copy (Lesson 3.3); the original is untouched.'),
    ('rsync --delete removed files:', 'they are gone from the destination. Restore from the source or another backup. Prevent with <code>--dry-run</code>, or <code>--backup --backup-dir=../deleted</code>, which keeps deleted files.'),
    ('Preview before running:', 'cp/mv: put <code>echo</code> in front to see the expanded names; rsync: <code>-n</code>.'),
]) + errors('The errors students see most with cp and mv. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='mkdir -p test_data && touch test_data/a.csv\ncp test_data backup/', meaning='cp copies only files unless told to go into folders.', fix='Add <code>-r</code> (or <code>-a</code>): <code>cp -r test_data backup/</code>.'),
    dict(cmd='cp missing.txt backup/', meaning='The source does not exist (typo, or wrong folder).', fix='Check with <code>ls</code>; use Tab completion so names are always right.'),
    dict(cmd='touch a.txt\ncp a.txt nofolder/', meaning='The destination ends with / but the folder does not exist.', fix='Create it first: <code>mkdir -p nofolder</code>.'),
    dict(cmd='touch a.txt\ncp a.txt a.txt', meaning='Source and destination are the same file.', fix='Give a different name or folder.'),
    dict(cmd='touch f.txt\nmv f.txt /etc/', meaning='You may not write into /etc.', fix='Use your own folders, or sudo if it is your server and really needed.'),
    dict(cmd='mkdir -p d/sub\nmv d d/sub/', meaning='A folder cannot be moved inside itself.', fix='Choose a destination outside the folder.'),
]) + stepper([
    ('1. Look first', '<p><code>ls -l source/</code> and <code>ls -l dest/</code>: what exists where?</p>', 'Behind the screen: reading folder entries only.'),
    ('2. Choose the tool', '<p>Need two copies → cp. Need it elsewhere → mv. Same copy again and again → rsync.</p>', 'Behind the screen: cp writes data; mv changes names; rsync compares first.'),
    ('3. Add safety', '<p><code>-i</code> for cp and mv, <code>--dry-run</code> for rsync.</p>', 'Behind the screen: the tool checks before calling open() with truncation or unlink().'),
    ('4. Run with -v', '<p><code>cp -av</code>, <code>mv -v</code>, <code>rsync -av</code>: you see every file.</p>', 'Behind the screen: the same work, with a line printed per file.'),
    ('5. Check the result', '<p><code>ls -l dest/</code>, <code>diff -r source dest</code> (Lesson 6.3) or run rsync again: no files listed = identical.</p>', 'Behind the screen: a second rsync is a free verification.'),
]) + qc('What does <code>cp -a</code> keep that plain <code>cp -r</code> does not?', 'Timestamps, permissions, ownership (when allowed) and symbolic links as links. cp -r gives copies the current time and default permissions.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def dirs(left, right, hl=None, note='', tone='blue'):
    o = label_box(14, 14, 150, 22, ['folder: project/'], 'card', 8.8) + label_box(196, 14, 150, 22, ['folder: backup/'], 'card', 8.8)
    for k, s in enumerate(left):
        o += label_box(14, 42 + k * 26, 150, 22, [s], 'green' if hl == ('L', k) else 'card', 8.4)
    for k, s in enumerate(right):
        o += label_box(196, 42 + k * 26, 150, 22, [s], 'green' if hl == ('R', k) else 'card', 8.4)
    return o + (t(180, 170, note, 8.8, tone, bold=True) if note else '')
see = [term(14, 16, 332, 120, ['$ ls -i big.iso', ('1048602 big.iso   (5 GB)', 'out')], title='riya@laptop', size=7.8) + cap('A 5 GB file. Its inode number is 1048602.', '', 'card', y=150, h=34),
       term(14, 16, 332, 120, ['$ time cp big.iso copy.iso', ('real 0m52s', 'acc'), '$ ls -i copy.iso', ('1048777 copy.iso', 'out')], title='riya@laptop', size=7.8) + cap('cp: almost a minute, and a NEW inode number.', '', 'blue', y=150, h=34),
       term(14, 16, 332, 120, ['$ time mv big.iso archive/', ('real 0m0.003s', 'acc'), '$ ls -i archive/big.iso', ('1048602 archive/big.iso', 'out')], title='riya@laptop', size=7.8) + cap('mv: instant, and the SAME inode number.', '', 'green', y=150, h=34),
       term(14, 16, 332, 120, ['$ time mv archive/big.iso /media/usb/', ('real 0m55s', 'err')], title='riya@laptop', size=7.8) + cap('mv to a USB disk: slow again!', '', 'red', y=150, h=34),
       (t(180, 30, 'Rule of thumb', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• same disk: mv = rename = instant', '• other disk: mv = copy + delete', '• cp always reads and writes data', '• times are illustrations'])) + cap('Check the inode to see what happened.', '', 'green', y=150, h=34))]
def fs(hl, note, tone='blue'):
    items = [('folder list  “archive/” → names', 'card'), ('name big.iso → inode 1048602', 'acc'), ('inode: size, owner, times, block map', 'violet'), ('data blocks on disk (5 GB)', 'blue')]
    o = ''.join(label_box(14, 14 + k * 34, 332, 28, [s], tn if k in hl else 'card', 8.6) for k, (s, tn) in enumerate(items))
    return o + t(180, 172, note, 8.8, tone, bold=True)
behind = [fs([1, 2], 'A name points to an inode; the inode points to blocks.'),
          fs([2, 3], 'cp: new inode + read and write all 5 GB.', 'blue'),
          fs([0, 1], 'mv: rename(): only the name moves between folder lists.', 'green'),
          fs([3], 'Another file system has its own inodes: data must be copied.', 'red'),
          fs([1], 'Names are cheap; data is expensive.', 'green')]
two = anim_two('Why is mv instant and cp slow?', 'What really moves on the disk?',
               'A terminal: cp of a 5 GB file takes almost a minute and gets a new inode; mv on the same disk is instant and keeps the inode; mv to a USB disk is slow.',
               'Names point to inodes, inodes to data blocks; cp copies blocks, mv on one file system only moves the name, mv across file systems copies blocks.', see, behind,
               ['A big file has an inode number (shown by <code>ls -i</code>).',
                'cp reads and writes every byte, and the copy is a new file with a new inode.',
                'mv on the same disk finishes instantly and the inode number is unchanged.',
                'mv to a different disk is as slow as cp.',
                'Times are illustrations; the inode behaviour matches real runs.'],
               ['A folder is a list of names pointing to inode numbers.',
                'cp creates a new inode and copies all data blocks.',
                'mv calls rename(): the name is removed from one list and added to another.',
                'Inodes belong to one file system, so across disks mv must copy, then delete.',
                'That is also why mv is atomic on one disk.'])

q1 = dirs(['schema.sql', 'dumps/day1.sql', 'app.log'], [], note='Monday: backup/ is empty.')
q2 = dirs(['schema.sql', 'dumps/day1.sql', 'app.log'], ['schema.sql', 'dumps/day1.sql', 'app.log'], note='rsync -av: everything copied.', tone='blue')
q3 = dirs(['schema.sql  (changed)', 'dumps/day1.sql', 'app.log', 'dumps/day2.sql  (new)'], ['schema.sql', 'dumps/day1.sql', 'app.log'], ('L', 0), 'Tuesday: rsync compares size and time.', 'violet')
q4 = dirs(['schema.sql', 'dumps/day1.sql', 'app.log', 'dumps/day2.sql'], ['schema.sql  ← sent', 'dumps/day1.sql', 'app.log', 'dumps/day2.sql  ← sent'], ('R', 3), 'Only 2 files sent.', 'green')
q5 = dirs(['schema.sql', 'dumps/day1.sql', 'dumps/day2.sql'], ['schema.sql', 'dumps/day1.sql', 'app.log  ← --delete', 'dumps/day2.sql'], ('R', 2), 'app.log deleted in source: --delete removes it.', 'red')
s1 = anim_one('Real-time scenario 1', 'A nightly backup with rsync',
              'Riya’s DBA backup folder over three days. The file lists match the real rsync runs shown in the command card above.',
              'rsync day by day', 'Monday rsync copies all files; Tuesday only the changed schema.sql and the new day2.sql are sent; --delete removes app.log from the backup.', [q1, q2, q3, q4, q5],
              ['Monday: the backup folder is empty.',
               'First <code>rsync -av db_backup/ backup/</code>: every file is copied, like <code>cp -a</code>.',
               'Tuesday: schema.sql changed and day2.sql is new. rsync compares size and modification time of each file.',
               'Only those two files are sent; the others are skipped.',
               'Later app.log is deleted in the source. Only with <code>--delete</code> (after <code>--dry-run</code>) does it disappear from the backup.'],
              hid='scenario-rsync')

m1 = term(14, 14, 332, 100, ['$ ls', ('notes  reports', 'out'), '$ mv notes reports', '$ ls', ('reports', 'out')], title='riya@laptop: ~/lab', size=7.8) + cap('Kabir: “mv notes reports” and notes is gone!', '', 'red', y=150, h=34)
m2 = term(14, 14, 332, 100, ['$ ls reports', ('notes  q1.csv', 'acc')], title='riya@laptop: ~/lab', size=7.8) + cap('reports existed as a folder, so notes went INSIDE it.', '', 'blue', y=150, h=34)
m3 = term(14, 14, 332, 100, ['$ mv -v reports/notes notes_2026', ("renamed 'reports/notes' -> 'notes_2026'", 'acc')], title='riya@laptop: ~/lab', size=7.8) + cap('Back out, with a new name; -v says what happened.', '', 'green', y=150, h=34)
m4 = term(14, 14, 332, 100, ['$ mv -i a.txt b.txt', ("mv: overwrite 'b.txt'? n", 'acc')], title='riya@laptop: ~/lab', size=7.8) + cap('Target exists: -i asks first.', '', 'blue', y=150, h=34)
m5 = (t(180, 30, 'mv decides by the last argument', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• existing folder → move INSIDE it', '• new name → rename', '• existing file → OVERWRITE it', '• add -v to see, -i to be asked'])) + cap('Know the target before pressing Enter.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', '“mv deleted my folder!” (it did not)',
              'Kabir runs <code>mv notes reports</code> and panics. Messages match real runs.',
              'mv and the last argument', 'mv into an existing folder moves inside it; mv -v shows a rename; mv -i asks before overwriting.', [m1, m2, m3, m4, m5],
              ['notes seems to vanish.',
               'Because reports was already a folder, notes was moved inside it.',
               '<code>mv -v</code> moves it back with a clear message.',
               'If the target is an existing <b>file</b>, mv overwrites it: <code>-i</code> asks first.',
               'Three outcomes depending on the last argument.'],
              hid='scenario-mv')

dx = dissect('Layer by layer: cp vs mv inside the system',
    'Open each layer to see what cp and mv really do. Each comes with a real command and output from our build machine.', [
    dict(key='shell', name='Bash', sub='expands names',
         why='You type patterns and paths; the program needs a final list.',
         how='Wildcards and braces are expanded first; the last word is the destination.',
         impl='bash parser (Lesson 3.4).', used='cp *.csv dir/, mv {a,b}.txt old/.',
         cmd='touch a.csv b.csv; echo cp *.csv input/'),
    dict(key='cmd', name='cp / mv programs', sub='GNU coreutils',
         why='One small program per job.',
         how='They check the destination: an existing folder means “put inside”.',
         impl='/usr/bin/cp and /usr/bin/mv.', used='Every Linux system.',
         cmd='cp --version | head -1'),
    dict(key='copy', name='cp: new inode', sub='data copied',
         why='Two independent files must exist afterwards.',
         how='open() source, create target, copy data; a new inode number.',
         impl='Kernel: openat, read/write or copy_file_range.', used='Backups, templates.',
         cmd='echo data > f; cp f g; stat -c "%n inode=%i" f g'),
    dict(key='rename', name='mv: rename()', sub='same inode',
         why='Moving should not cost time on the same disk.',
         how='One rename() system call moves the name; the inode stays.',
         impl='Kernel VFS; atomic on one file system.', used='Deploys, log rotation, pipelines.',
         cmd='echo data > f; stat -c "before: inode=%i" f; mkdir -p d; mv f d/; stat -c "after:  inode=%i" d/f'),
    dict(key='attr', name='Attributes', sub='what survives',
         why='Dates and permissions matter for backups and security.',
         how='cp makes a new file (new time) unless -p/-a; mv keeps the same inode, so all stays.',
         impl='Stored in the inode.', used='Backup age checks, audits.',
         cmd="touch -d '2026-01-01' f; cp f c1; cp -p f c2; for x in f c1 c2; do echo \"$x $(date -r $x +%F)\"; done"),
], hint='Top = what you type · bottom = what is stored. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What really moves when you copy, move and sync</h2>
  <p>Left: what Riya sees (times are illustrations). Right: what happens on the disk.</p>
''' + two + '''
  <p>Two real-time scenarios: a nightly rsync backup, and a folder that “disappeared”.</p>
''' + s1 + s2 + dx + hood('Under the hood: one system call for mv', 'The real file-related system calls of <code>mv f d/</code> on our build machine. Three lines, and none of them reads or writes the data.',
          'mv f d/', 'echo data > f; mkdir -p d', 'renameat|openat\\(AT_FDCWD, "(f|d)',
          '<p>First mv tries to rename f to the name <code>d/</code> itself with <code>RENAME_NOREPLACE</code> (never overwrite); the kernel answers EEXIST because d already exists. So mv opens the folder d and renames f into it: <code>renameat2(…, "f", 3, "f")</code> = 0, done. No <code>read</code> or <code>write</code> of the data: the kernel only moves the name. Run the same with <code>cp f d/</code> and you will see the file opened, the target created and the data copied.</p>') + qc('Why is <code>mv</code> to a USB disk as slow as <code>cp</code>?', 'Inodes belong to one file system. Across file systems rename() is impossible, so mv copies the data and then deletes the original.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Copying, moving and syncing at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ rsync -a', 'prompt'), ('--delete', 'acc')], title='backup', size=6.4, step=12),
              '1. Nightly backups', 'Servers sync data folders to a backup disk or server every night; only changes travel.', ['Night', '*rsync -a', 'fresh backup']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['.tmp → mv', 'atomic'], 'green', 8.6), '2. Safe publishing',
    'Programs write a temp file and mv it into place, so readers never see half a file. Data pipelines move files from incoming/ to done/.', ['Write tmp', '*mv', 'complete file']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ rsync -avz', 'prompt'), ('public/ web:', 'acc')], title='devops', size=6.4, step=12),
    '3. Deployments', 'Static sites and app releases are pushed with rsync over SSH; a release folder is switched with a link or mv.', ['Build', '*rsync -z', 'live']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cp file', 'file.bak'], 'amber', 8.6), '4. Before every edit',
    'Admins copy a config to <code>.bak</code> before changing it, so a bad change is undone in one command.', ['Copy', '*edit', 'undo ready']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['mv evidence', 'chmod 000'], 'violet', 8.6), '5. Incident response',
    'Security teams move suspicious files to quarantine instead of deleting them, keeping evidence intact.', ['Find', '*mv', 'investigate']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small commands that save time. cp and mv lines were really run on our build machine.', [
    dict(level='b', title='Quick backup with a date', scenario='Copy a file with today’s date in the name before editing it.',
         cmd='echo x > app.conf && cp app.conf "app.conf.$(date +%Y)" && ls app.conf*',
         explain='The shell builds the name; real scripts use <code>%F</code> for the full date.'),
    dict(level='b', title='Swap two files', scenario='Exchange the contents of a.txt and b.txt.',
         cmd='echo A > a.txt; echo B > b.txt; mv a.txt tmp && mv b.txt a.txt && mv tmp b.txt; cat a.txt b.txt',
         explain='A third, temporary name is needed; && stops if a step fails.'),
    dict(level='i', title='Copy only the folder structure', scenario='Recreate the folders of a project without any files.',
         cmd='mkdir -p p/{a,b/c} && touch p/a/x p/b/c/y && (cd p && find . -type d -exec mkdir -p ../skeleton/{} \\;) && find skeleton | sort',
         explain='find lists folders; mkdir -p recreates each one (Lesson 13.2).'),
    dict(level='i', title='Move everything except one file', scenario='Archive all files but keep README.md.',
         cmd='touch a b README.md && mkdir -p old && shopt -s extglob\nmv !(README.md|old) old/ && ls; ls old',
         explain='extglob’s <code>!(…)</code> = everything except (Lesson 3.4). It must be enabled on its own line first.'),
    dict(level='a', title='Copy only newer files', scenario='Update a folder with newer versions, leave the rest.',
         cmd='mkdir -p src dst && echo old > dst/a && sleep 1 && echo new > src/a && echo x > src/b && cp -uv src/* dst/',
         explain='<code>-u</code> copies a only because src/a is newer, and b because it is missing.'),
], extra=build_up('a safe config update', 'Riya must change the port in app.conf without any risk.',
    '', [
    ("printf 'port=80\\n' > app.conf && cp -v app.conf app.conf.bak", '1. Backup first.'),
    ("printf 'port=80\\n' > app.conf && cp app.conf app.conf.bak && sed 's/80/8080/' app.conf > app.conf.tmp && cat app.conf.tmp", '2. Write the change to a temp file (sed: Lesson 6.4).'),
    ("printf 'port=80\\n' > app.conf && cp app.conf app.conf.bak && sed 's/80/8080/' app.conf > app.conf.tmp && mv app.conf.tmp app.conf && cat app.conf", '3. Atomic switch with mv.'),
    ("printf 'port=80\\n' > app.conf && cp app.conf app.conf.bak && sed 's/80/8080/' app.conf > app.conf.tmp && mv app.conf.tmp app.conf && cp app.conf.bak app.conf && cat app.conf", '4. And the undo, if needed.'),
])) + which('Choosing the right command.', [
    ('Two copies of a file', 'cp a b', 'Original stays.', 'mv (the original goes).'),
    ('Copy a folder once', 'cp -a dir dest/', 'Keeps everything.', 'cp dir dest/ → omitting directory.'),
    ('Rename', 'mv old new', 'Instant.', 'cp + rm (slow, loses inode).'),
    ('Same backup every day', 'rsync -av src/ dest/', 'Only changes.', 'cp -r every night.'),
    ('Exact mirror', 'rsync -av --delete src/ dest/', 'Removes extras.', 'Skipping --dry-run.'),
    ('Never overwrite', 'cp --update=none', 'Skips existing.', 'Plain cp (silent overwrite).'),
    ('Publish a file safely', 'mv file.tmp file', 'Atomic.', 'Writing directly into the live file.'),
    ('To another server', 'rsync -avz src/ host:dir/', 'Resumable, compressed.', 'cp to a mounted share with -r.'),
]) + keys('Shortcuts for copying and moving.', [
    ('Tab', 'complete source and destination paths', 'cp rep⇥ bac⇥'),
    ('!$', 'last argument of the previous command', 'cp a.txt backup/ && ls !$'),
    ('Alt + .', 'insert the last argument', 'mv x.csv done/ ; ls Alt+.'),
    ('{,.bak}', 'brace trick: file and file.bak', 'cp app.conf{,.bak}'),
    ('alias cp="cp -i"', 'always ask (in ~/.bashrc)', 'cp a b → asks if b exists'),
    ('\\cp', 'run the command without its alias', '\\cp -f a b'),
]) + scriptit('backup.sh', 'A small but real backup script: dated folder, rsync with a preview, and a summary. (rsync is replaced by cp -a here because our browser runner has no rsync; the rsync line is in the comment.)',
'''#!/bin/bash
# backup.sh SRC DEST: dated copy of SRC inside DEST
src=${1:-project}; dest=${2:-backups}
mkdir -p "$src/data" && echo "id,name" > "$src/data/students.csv"   # demo data
stamp=2026-11-06                     # real script: stamp=$(date +%F)
target="$dest/$stamp"
mkdir -p "$target"
cp -a "$src"/. "$target"/            # real script: rsync -a --delete "$src"/ "$target"/
echo "backed up $(find "$target" -type f | wc -l) file(s) to $target"
ls -R "$dest"''',
'<p>Copying <code>"$src"/.</code> means “the contents of src”, the same idea as rsync’s trailing slash.</p>') + puzzle_answer('On the same disk, <code>mv</code> does not move any data. A folder is just a list of names pointing to inodes; mv calls <code>rename()</code>, which removes the name from one list and adds it to another. The 5 GB of data blocks and the inode stay exactly where they are (the inode number does not change). <code>cp</code> must read and write all 5 GB to make a new file. Across different disks, mv has to copy too.') + qc('You need yesterday’s backup folder updated with today’s changes. Which command, and how do you check before deleting anything?', '<code>rsync -av --delete --dry-run src/ backup/</code> to preview, then the same without <code>--dry-run</code>.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-creating-files-and-folders-touch-mkdir-and-rmdir/">Lesson 3.1</a>: creating files and folders.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
