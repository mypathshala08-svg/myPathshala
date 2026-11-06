import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='03-files-and-directories', lesson='02-copying-moving-and-syncing-cp-mv-and-rsync', n='3.2',
    module_label='Module 3 · Working with files and directories',
    title='Copying, moving and syncing: cp, mv and rsync',
    desc='Copy files and folders with cp (-r, -a, -p, -i, --update=none, -u, --backup), move and rename with mv (-i, -n, -v) and why mv is instant on the same disk, and keep backups up to date with rsync (-av, --delete, --dry-run, --exclude, trailing slash, -z over SSH). Every command explained, then used in DBA, DevOps, data, security, testing and development work, with real outputs.',
    og_desc='The one-hour backup that became three seconds: cp, mv and rsync explained, with real outputs, for every IT field.',
    minutes=40, level='Beginner → Advanced',
    lead='Riya copies her whole project to a backup disk every evening and it takes an hour. Kabir moved a folder and cannot find it. This lesson explains cp, mv and rsync option by option, shows what really happens on the disk, and how each IT role uses them.',
    chips=['Commands by field', 'Which command when?', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = '''# Copy, back up, move
mkdir -p project/data backup archive
echo "id,name" > project/data/students.csv
cp project/data/students.csv students_copy.csv
cp -a project backup/
mv students_copy.csv archive/students_2026.csv
ls
find backup archive | sort
'''

RUN = dict(
    heading='Copy, back up and move in seven lines',
    intro='<p>The script copies one file, backs up a whole folder with its attributes, then moves and renames the copy. Run it, then try the tasks.</p>',
    code=MAIN,
    anno=[
        ('cp project/data/students.csv students_copy.csv', 'A copy with a new name; the original stays.'),
        ('cp -a project backup/', 'The whole folder, inside backup/, with dates and permissions.'),
        ('mv students_copy.csv archive/students_2026.csv', 'Moved and renamed in one step.'),
        ('find backup archive | sort', 'Check what ended up where.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Is students_copy.csv still in the current folder?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> backup/ already exists. Where will the copy go? Then run.',
             code='mkdir -p reports backup\ntouch reports/q1.csv\ncp -r reports backup\nfind backup\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the folder is not copied. Fix it.',
             code='mkdir -p logs && touch logs/app.log\ncp logs logs_backup\nls\n', expect='any'),
        dict(label='4 · Your turn', hint='Rename <code>draft.txt</code> to <code>final.txt</code> and show the folder.',
             code='touch draft.txt\nmv draft.txt final.txt\nls\n'),
        dict(label='5 · Challenge', hint='Copy a file so that the old target is kept as a numbered backup.',
             code='echo v1 > notes.txt; echo v2 > new.txt\ncp --backup=numbered new.txt notes.txt\nls; cat notes.txt notes.txt.~1~\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: rsync and copies between computers',
    intro='<p>rsync is not installed on our browser build machine. These outputs were <b>recorded on Ubuntu 22.04 with rsync 3.2.7</b> unless marked typical.</p>',
    items=[
        dict(title='1 · Install rsync if it is missing', cmd='rsync --version | head -1 || sudo apt install rsync', output='rsync  version 3.2.7  protocol version 31',
             note='Recorded. Most Ubuntu installs already have it; minimal and WSL images may not.'),
        dict(title='2 · First backup, then the second (nothing changed)', cmd='rsync -av db_backup/ backup/ ; rsync -av db_backup/ backup/', output='sending incremental file list\ncreated directory backup\n./\napp.log\nschema.sql\ndumps/\ndumps/day1.sql\n\nsent 347 bytes  received 113 bytes  920.00 bytes/sec\ntotal size is 6  speedup is 0.01\nsending incremental file list\n\nsent 198 bytes  received 13 bytes  422.00 bytes/sec\ntotal size is 6  speedup is 0.03',
             note='Recorded. The second run lists no files.'),
        dict(title='3 · Statistics: how much was really sent?', cmd="rsync -a --stats db_backup/ backup/ | grep -E 'Number of (files|regular files transferred)|Total transferred'", output='Number of files: 5 (reg: 3, dir: 2)\nNumber of regular files transferred: 0\nTotal transferred file size: 0 bytes',
             note='Recorded. 0 files transferred = the backup is already identical.'),
        dict(title='4 · To another computer over SSH', cmd='rsync -avz ~/project/ riya@192.168.1.20:/home/riya/project/', output="riya@192.168.1.20's password:\nsending incremental file list\n./\nREADME.md\n...\nsent 12,804 bytes  received 412 bytes  2,403.27 bytes/sec",
             note='Typical. Needs SSH on the other machine (Lesson 16.5). With SSH keys there is no password prompt.'),
        dict(title='5 · Windows (WSL) to a USB disk', cmd='rsync -av --progress ~/project/ /mnt/e/backup/project/', output='sending incremental file list\nproject/report.pdf\n      2,097,152 100%   45.20MB/s    0:00:00 (xfr#1, to-chk=3/5)',
             note='Typical. In WSL, drive E: is /mnt/e. NTFS cannot store Linux permissions, so you may see harmless “failed to set permissions” warnings; use -rt instead of -a there.'),
    ],
)

TRACE = dict(
    heading='Watching copies and moves',
    intro='<p>Step through a script. Watch the <b>Files</b> box: cp adds files, mv makes a name disappear and another appear.</p>',
    code='''mkdir data
echo "id,name" > data/a.csv
cp data/a.csv b.csv
cp data data2
cp -r data data2
mv b.csv data2/b.csv
mv data2 backup
''',
    notes={1: 'mkdir :: A folder for the demo.', 3: 'cp :: A second file appears; a.csv stays.', 4: 'Error :: Folders need -r: exit status 1.',
           5: 'cp -r :: The whole folder is copied.', 6: 'mv :: b.csv disappears here and appears inside data2.', 7: 'Rename :: data2 is now called backup.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a DBA’s backup that keeps dates, a data engineer’s incoming/processed folders, and a DevOps atomic deploy.'
EXAMPLES = [
    dict(level='b', tag='DBA', title='Back up dumps and keep their dates',
         problem='<p>Copy every <code>.sql</code> dump into <code>backup/</code> so that the copies keep the original dates (a cleanup job deletes backups older than 7 days by date).</p>',
         inp='mon.sql (Nov 3), tue.sql (Nov 4)',
         approach=['<code>cp -p</code> keeps modification times.', 'Check with <code>date -r</code>.'],
         code='''touch -d '2026-11-03 23:00' mon.sql
touch -d '2026-11-04 23:00' tue.sql
mkdir -p backup
cp -pv *.sql backup/
for f in backup/*.sql; do echo "$f $(date -r "$f" '+%F %H:%M')"; done
''',
         notes={4: 'Copy :: -p = preserve, -v = show.', 5: 'Verify :: Dates match the originals.'},
         tryit='Run the same with plain <code>cp</code> (no -p). What date do the copies get?'),
    dict(level='i', tag='Data engineering', title='incoming → processing → done',
         problem='<p>A pipeline takes files from <code>incoming/</code>, “processes” them (here: counts lines) and moves each to <code>done/</code>, so nothing is processed twice.</p>',
         inp='incoming/a.csv (3 lines), incoming/b.csv (2 lines)',
         approach=['A loop over incoming files.', 'mv to done/ after each file.'],
         code='''mkdir -p incoming done
printf '1\\n2\\n3\\n' > incoming/a.csv
printf '1\\n2\\n' > incoming/b.csv
for f in incoming/*.csv; do
  echo "$(basename "$f"): $(wc -l < "$f") rows"
  mv "$f" done/
done
ls incoming done
''',
         notes={4: 'Loop :: One file at a time.', 5: 'Process :: Here just a count.', 6: 'Move :: Done files leave incoming/.'},
         tryit='Add <code>failed/</code> and move a file there if it has 0 rows.'),
    dict(level='a', tag='DevOps', title='An atomic config deploy with rollback',
         problem='<p>Replace <code>app.conf</code> with a new version so that the app never sees a half-written file, and keep the old version for rollback.</p>',
         inp='app.conf with port=80; new port 8080',
         approach=['Write the new file under a temp name.', '<code>cp</code> the old one to .bak, then <code>mv</code> the temp file into place.'],
         code='''echo "port=80" > app.conf
echo "port=8080" > app.conf.tmp
cp -p app.conf app.conf.bak
mv app.conf.tmp app.conf
cat app.conf
cat app.conf.bak
''',
         notes={2: 'Temp :: Written completely before anyone uses it.', 3: 'Backup :: Rollback = mv app.conf.bak app.conf.', 4: 'Switch :: rename() is atomic.'},
         tryit='Write the rollback command and run it.'),
]

QUIZ = mix([
    dict(q='cp logs backup/ prints “-r not specified; omitting directory”. Why?', options=['backup/ does not exist', 'logs is a folder and cp needs -r', 'You need sudo', 'logs is empty'], answer=1,
         why='cp copies folders only with -r (or -a).'),
    dict(q='Which cp option keeps dates, permissions and links when copying a folder?', options=['-r', '-a', '-i', '-v'], answer=1,
         why='-a = archive: recursive and preserves everything.'),
    dict(q='mv notes reports, where reports is an existing folder. Result?', options=['notes renamed to reports', 'notes moved into reports/', 'Error', 'reports deleted'], answer=1,
         why='An existing folder as the last argument means “move inside”.'),
    dict(q='Why is mv of a big file on the same disk instant?', options=['It compresses', 'It only renames the directory entry', 'It copies in the background', 'It uses RAM'], answer=1,
         why='rename() moves the name; the data and inode stay.'),
    dict(q='rsync -a src dest/ (no slash after src) creates…', options=['dest/ with src’s contents', 'dest/src/ with the contents', 'An error', 'A link'], answer=1,
         why='No trailing slash = copy the folder itself.'),
    dict(q='What should you run before rsync --delete?', options=['--progress', '--dry-run', '--compress', '--stats'], answer=1,
         why='-n / --dry-run shows what would be deleted without doing it.'),
    dict(q='Which cp option never overwrites existing files (the modern form)?', options=['--update=none', '-f', '-u', '--force'], answer=0,
         why='--update=none; the older -n now prints a portability warning.'),
    dict(q='The second rsync -av run lists no file names. What does it mean?', options=['It failed', 'Nothing changed, nothing was sent', 'Files were deleted', 'It needs -r'], answer=1,
         why='rsync only lists files it transfers.'),
])

REVISION = [
    '<code>cp a b</code>, <code>cp a dir/</code>; folders: <code>-r</code>; backups: <code>-a</code> (keeps dates, permissions, links).',
    'cp and mv overwrite silently: <code>-i</code> ask, <code>--update=none</code> skip (old <code>-n</code>), <code>-u</code> newer only, <code>--backup=numbered</code>.',
    '<code>mv old new</code> renames; <code>mv f dir/</code> moves; existing folder as target = move inside.',
    'Same disk: mv = rename() = instant, atomic, same inode. Other disk: copy + delete.',
    '<code>rsync -av src/ dest/</code>: first run copies all, later runs only changes.',
    'Trailing slash: <code>src/</code> = contents, <code>src</code> = the folder itself.',
    '<code>--delete</code> makes an exact mirror; always <code>-n</code> (<code>--dry-run</code>) first. <code>--exclude</code>, <code>-z</code>, <code>-P</code>, <code>-e ssh</code>.',
    'Safe updates: cp to .bak → write .tmp → mv .tmp into place.',
]

FAQ = [
    ('What is the difference between cp and mv?', 'cp creates a copy and keeps the original; mv moves or renames, so the original name disappears. cp needs -r for folders; mv does not.'),
    ('How do you copy a directory in Linux?', 'cp -r dir dest/ (or cp -a to keep timestamps, permissions and links).'),
    ('How do you rename a file?', 'mv oldname newname. For many files at once by a pattern, use rename (Lesson 3.7).'),
    ('What is the difference between rsync and cp?', 'rsync compares source and destination and transfers only new or changed files; it can delete extras (--delete), exclude patterns, preview (--dry-run) and copy over SSH. cp copies everything every time, locally only.'),
    ('Why does rsync care about the trailing slash?', 'src/ means the contents of src; src means the folder itself, so it is created inside the destination.'),
    ('How do you avoid overwriting files with cp?', 'cp -i to be asked, cp --update=none to skip existing files, or --backup=numbered to keep the old ones.'),
    ('Is mv safe for big files?', 'On the same file system it is instant and atomic. Across file systems it copies then deletes; if interrupted, the original is still there.'),
]

PRACTICE_INTRO = 'Tasks for every field. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='A copy with a new name', stmt='Copy <code>notes.txt</code> to <code>notes_copy.txt</code> and list both.', inp='notes.txt',
         code='echo hi > notes.txt\ncp notes.txt notes_copy.txt\nls\n', explain='Source first, new name second.'),
    dict(level='easy', title='Rename', stmt='Rename <code>report.txt</code> to <code>report_final.txt</code>.', inp='report.txt',
         code='touch report.txt\nmv report.txt report_final.txt\nls\n', explain='mv with a new name = rename.'),
    dict(level='easy', title='Copy a folder', stmt='Copy the folder <code>src</code> (with a file inside) to <code>src_backup</code>.', inp='src/main.py',
         code='mkdir src && touch src/main.py\ncp -r src src_backup\nfind src_backup\n', explain='-r for folders.'),
    dict(level='medium', title='Several files into a folder', stmt='Copy <code>a.csv</code>, <code>b.csv</code>, <code>c.csv</code> into <code>input/</code> in one command.', inp='three CSV files',
         code='touch a.csv b.csv c.csv && mkdir input\ncp a.csv b.csv c.csv input/\nls input\n', explain='Many sources, folder last.'),
    dict(level='medium', title='Keep the date', stmt='Copy <code>old.log</code> (dated 2026-10-01) so the copy keeps that date.', inp='old.log',
         code="touch -d 2026-10-01 old.log\ncp -p old.log copy.log\ndate -r copy.log +%F\n", explain='-p preserves the time.'),
    dict(level='medium', title='Do not overwrite', stmt='Copy <code>new.txt</code> to <code>keep.txt</code> only if keep.txt does not exist. It does, so it must stay unchanged.', inp='keep.txt = "keep"',
         code='echo keep > keep.txt; echo new > new.txt\ncp --update=none new.txt keep.txt\ncat keep.txt\n', explain='--update=none skips existing files.'),
    dict(level='business', title='Archive last month', stmt='Move all <code>sales_2026-10-*.csv</code> files into <code>archive/2026-10/</code>, leaving November files.', inp='sales_2026-10-01.csv, sales_2026-10-02.csv, sales_2026-11-01.csv',
         code='touch sales_2026-10-01.csv sales_2026-10-02.csv sales_2026-11-01.csv\nmkdir -p archive/2026-10\nmv sales_2026-10-*.csv archive/2026-10/\nls; ls archive/2026-10\n', explain='The wildcard selects only October (Lesson 3.4).'),
    dict(level='business', title='Rollback a config', stmt='app.conf was changed to a broken version. Restore it from <code>app.conf.bak</code> and show it.', inp='app.conf.bak = port=80',
         code='echo port=80 > app.conf.bak; echo "port=" > app.conf\ncp app.conf.bak app.conf\ncat app.conf\n', explain='The .bak copy made before editing is the undo.'),
]

SCN_INTRO = 'Interview questions about copying, moving and syncing, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“cp says omitting directory.”',
        'You run <code>cp project backup/</code> and nothing is copied.',
        'do you know cp’s recursive option?',
        '''<ul>
          <li>cp copies only files by default; folders need <code>-r</code>.</li>
          <li>For backups use <code>cp -a</code>: recursive and keeps dates and permissions.</li>
          <li>Check with <code>ls -R backup</code>.</li>
        </ul>''', 'saying “Linux cannot copy folders”.') +
    scn('Operations · backups', 'Junior', 'The backup that takes all night',
        'A nightly <code>cp -r</code> of 200 GB no longer finishes before morning.',
        'do you know incremental copies?',
        '''<ol>
          <li>Replace with <code>rsync -a --delete /data/ /backup/data/</code>: only changes are copied.</li>
          <li>Preview the first run with <code>--dry-run</code>; watch with <code>--stats</code>.</li>
          <li>For history, rotate dated folders or use <code>--link-dest</code> snapshots (unchanged files become hard links).</li>
        </ol>''', '“buy a faster disk” as the only answer.') +
    scn('DevOps · deployments', 'Mid-level', 'Users saw a broken page during deploy',
        'A deploy script writes the new <code>index.html</code> directly into the web folder; for a second, users get half a page.',
        'do you understand atomic replacement?',
        '''<ul>
          <li>Write the new file to a temp name in the <b>same file system</b>, then <code>mv tmp index.html</code>: rename() is atomic.</li>
          <li>For whole releases: upload to <code>releases/v42/</code>, then switch a symlink (<code>ln -sfn</code>, Lesson 10.2).</li>
          <li>rsync already does this per file: it writes a temporary file and renames it.</li>
        </ul>''', 'adding sleep or “deploy at night”.') +
    scn('Data platform · incident', 'Senior', 'rsync --delete wiped the backup',
        'A nightly <code>rsync -a --delete /mnt/data/ /backup/</code> ran while the data disk was not mounted. The backup is now empty.',
        'do you design safe automation?',
        '''<ul>
          <li>An unmounted /mnt/data is an empty folder, so --delete mirrored “empty”.</li>
          <li>Guards: check <code>mountpoint -q /mnt/data</code> or a marker file before syncing; use <code>--max-delete=N</code>; keep deleted files with <code>--backup --backup-dir</code>.</li>
          <li>Keep several generations (snapshots), not one mirror; alert on unusual delete counts.</li>
        </ul>''', 'blaming rsync instead of the missing checks.')
) + interview([
    ('Difference between cp and mv?', 'cp makes a copy (original stays, new inode, needs -r for folders); mv moves or renames (original name gone, same inode on the same file system, works on folders directly).'),
    ('How do you copy a folder and keep permissions and timestamps?', 'cp -a src dest/ (archive), or rsync -a src/ dest/.'),
    ('Why is mv fast on the same disk but slow to a USB disk?', 'Same file system: rename() only changes directory entries. Different file system: mv must copy the data and then delete the original.'),
    ('What does the trailing slash mean in rsync?', 'src/ copies the contents of src; src copies the folder itself into the destination.'),
    ('How does rsync know what changed?', 'By default it compares size and modification time; with -c it compares checksums. Over a network it sends only changed blocks of a file (delta transfer).'),
    ('How do you prevent cp from overwriting?', 'cp -i (ask), cp --update=none (skip; older -n), or --backup=numbered (keep the old file).'),
    ('What is an atomic file replacement?', 'Writing to a temp file and mv-ing it over the target, so readers see the old or new file, never a partial one.'),
], [
    ('RHCSA (EX200)', '“Create, delete, copy, and move files and directories”, part of the essential tools objectives.'),
    ('LFCS', 'Essential Commands: copy, move and archive files; rsync for backups appears in operations tasks.'),
    ('CompTIA Linux+', 'File management commands (cp, mv) and copying files between systems (rsync, scp).'),
]) + distro('cp and mv are POSIX; the options beyond that differ.', [
    ('cp -a', 'yes (GNU)', 'yes (GNU)', 'yes (BSD cp has -a since macOS 10.x)', 'WSL yes; Git Bash yes'),
    ('cp --update=none / -n warning', 'coreutils 9.x: -n warns, use --update=none', 'RHEL 9 (coreutils 8.32): no warning, --update=none not available', 'BSD: -n works, no --update', 'depends on coreutils version'),
    ('cp --backup=numbered', 'yes', 'yes', 'no', 'yes'),
    ('mv -v output', "renamed 'a' -> 'b'", 'same', 'a -> b', 'same as Ubuntu'),
    ('rsync installed', 'usually (not on minimal images)', 'install with dnf', 'old 2.6.9 (Apple) or openrsync; brew install rsync', 'WSL: apt install rsync; Git Bash: not included'),
    ('mv across disks', 'copy + delete', 'same', 'same', 'WSL: /mnt/c is another file system'),
]) + teaser('3.3', 'Riya types <code>rm -rf /home/riya/project /backup</code> with one extra space before /backup. What exactly gets deleted, and how could she have been protected?')

CHEATSHEET = cheatsheet('cp, mv and rsync', [
    ('cp: copy', [('cp a b', 'copy to new name'), ('cp a b c dir/', 'into a folder'), ('cp -r dir dest/', 'a folder'), ('cp -a dir dest/', 'keep everything (backup)'), ('cp -p f g', 'keep date, mode')]),
    ('cp: safety', [('cp -i a b', 'ask before overwrite'), ('cp --update=none a b', 'never overwrite'), ('cp -u src/* dst/', 'only newer'), ('cp --backup=numbered a b', 'keep b.~1~'), ('cp f{,.bak}', 'quick backup')]),
    ('mv: move / rename', [('mv old new', 'rename'), ('mv f dir/', 'move into folder'), ('mv -i a b', 'ask before overwrite'), ('mv -n a b', 'never overwrite'), ('mv -v a b', 'show what happened')]),
    ('rsync: sync', [('rsync -av src/ dest/', 'copy / update'), ('rsync -av src dest/', 'creates dest/src'), ('rsync -avn --delete src/ dest/', 'preview mirror'), ('rsync -av --delete src/ dest/', 'exact mirror'), ("rsync -av --exclude='*.log' …", 'skip files')]),
    ('rsync: remote', [('rsync -avz src/ user@host:dir/', 'to a server'), ('rsync -avz user@host:dir/ ./', 'from a server'), ('rsync -avP …', 'progress + resume'), ('rsync -ai …', 'why each file is sent'), ('rsync --stats …', 'totals')]),
])

MINDMAP = mindmap('cp, mv, rsync', [
    ('cp', 'blue', ['original stays', '-r folders, -a backups', 'new inode']),
    ('Safety', 'red', ['-i ask', '--update=none skip', '--backup=numbered']),
    ('mv', 'green', ['move or rename', 'same disk: instant', 'atomic rename()']),
    ('rsync', 'violet', ['only changes', 'src/ vs src', '-z -e ssh remote']),
    ('Mirror', 'amber', ['--delete', '--dry-run first', '--exclude']),
    ('Patterns', 'acc', ['cp f f.bak first', 'tmp + mv deploy', 'incoming → done']),
])

LAB = lab('organise the DBDA folder', 'Build the lab, do the five tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab32 && cd ~/lab32 && rm -rf work
mkdir -p work/incoming && cd work
printf 'id,name\\n1,Asha\\n' > incoming/students.csv
printf 'port=80\\n' > app.conf
touch -d '2026-10-01' incoming/old.log''',
    tasks=['Copy <code>incoming/students.csv</code> to <code>students_copy.csv</code> in the <code>work</code> folder.',
           'Make a backup <code>app.conf.bak</code> of <code>app.conf</code>.',
           'Copy the whole <code>incoming</code> folder to <code>backup/incoming</code> keeping dates (old.log must still be dated 2026-10-01).',
           'Move <code>incoming/old.log</code> into a new folder <code>archive/</code>.',
           'Rename <code>students_copy.csv</code> to <code>students_2026.csv</code>.'],
    solution='''cp incoming/students.csv students_copy.csv
cp app.conf app.conf.bak
mkdir -p backup && cp -a incoming backup/
mkdir -p archive && mv incoming/old.log archive/
mv students_copy.csv students_2026.csv''',
    check='''cd ~/lab32/work
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1+5 copy renamed"    '[ -f students_2026.csv ] && [ ! -e students_copy.csv ] && cmp -s students_2026.csv incoming/students.csv'
ok "2 config backup"     'cmp -s app.conf app.conf.bak 2>/dev/null'
ok "3 backup keeps date" '[ "$(date -r backup/incoming/old.log +%F 2>/dev/null)" = 2026-10-01 ]'
ok "4 old.log archived"  '[ -f archive/old.log ] && [ ! -e incoming/old.log ]' ''')
