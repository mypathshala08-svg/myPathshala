import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='03-files-and-directories', lesson='03-deleting-safely-rm-rm-r-rm-i-shred-and-why-rm', n='3.3',
    module_label='Module 3 · Working with files and directories',
    title='Deleting safely: rm, rm -r, rm -i, shred and why rm -rf is dangerous',
    desc='Delete files and folders with rm (-r, -d, -i, -I, -f, -v, --), the five dangers of rm (spaces, wildcards, empty variables, wrong machine, -f), guarded delete scripts with ${var:?}, why a deleted file can still use disk space (lsof +L1, truncate), and secure deletion with shred and its limits on SSDs. Explained, then used by admins, DBAs, data engineers, DevOps, QA and security teams, with real outputs.',
    og_desc='There is no Recycle Bin in the terminal. rm, rm -r, -i, -I, -f, shred and the five dangers to check before you press Enter.',
    minutes=38, level='Beginner → Advanced',
    lead='One extra space in an rm -rf command deletes a project and its backup. This lesson explains rm and shred option by option, the five dangers to check for, how “deleted” files can still fill a disk, and how every IT team deletes safely.',
    chips=['Commands by field', 'The five dangers', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = '''# Look first, then delete
mkdir -p work/cache && touch work/a.tmp work/b.tmp work/keep.csv work/cache/x.bin
ls -R work
rm -v work/*.tmp
rm -r work/cache
rmdir work 2>&1 || echo "work is not empty"
ls work
'''

RUN = dict(
    heading='Look first, then delete',
    intro='<p>The script lists a folder, deletes the .tmp files, removes a sub-folder with its content, and shows that rmdir refuses a folder that still has a file.</p>',
    code=MAIN,
    anno=[
        ('ls -R work', 'Always look before deleting.'),
        ('rm -v work/*.tmp', 'Only the .tmp files; -v names each one.'),
        ('rm -r work/cache', 'A folder and its content need -r.'),
        ('rmdir work 2>&1 || echo "work is not empty"', 'rmdir refuses: keep.csv is still inside.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which file is left in work/?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which names will rm receive? (echo only prints.) Then run.',
             code='touch a.log b.log c.txt\necho rm * .log\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the file called <code>-v</code> is not deleted. Fix the rm line.',
             code='touch -- -v\nrm -v\nls\n', expect='any'),
        dict(label='4 · Your turn', hint='Delete the folder <code>old</code> and everything in it, showing each removal.',
             code='mkdir -p old/x && touch old/x/1.txt old/2.txt\nrm -rv old\n'),
        dict(label='5 · Challenge', hint='Protect the rm line so it stops when <code>dir</code> is empty.',
             code='dir=""\nrm -rf "${dir:?dir is empty}/"\necho "never reached"\n', expect='any'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: interactive questions, open files and a trash bin',
    intro='<p>Some behaviour appears only at a real keyboard or on a real server. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · rm asks about a write-protected file', cmd='touch ro.txt; chmod 444 ro.txt; rm ro.txt', output="rm: remove write-protected regular empty file 'ro.txt'? ",
             note='Typical: the question appears only when you type at a keyboard. In a script (no keyboard) rm deletes it silently, as our recorded runs show.'),
        dict(title='2 · Ask once for many files', cmd='alias rm="rm -I"; touch {1..5}.log; rm *.log', output='rm: remove 5 arguments? y',
             note='Typical. Put the alias in ~/.bashrc to keep it (Lesson 12.3). Bypass once with <code>\\rm</code>.'),
        dict(title='3 · Find deleted files still using space', cmd='sudo lsof +L1', output='COMMAND  PID USER  FD  TYPE DEVICE  SIZE/OFF NLINK  NODE NAME\njava     812 app   4w  REG  259,2 21474836480     0 8121 /var/log/app.log (deleted)',
             note='Typical. NLINK 0 = no name left; the 20 GB is freed when java closes it.'),
        dict(title='4 · A desktop trash from the terminal', cmd='gio trash old.pdf; gio list trash://', output='trash:///old.pdf',
             note='Typical on Ubuntu desktop (GNOME). The file appears in the Files app’s Trash and can be restored. Not available on servers.'),
        dict(title='5 · shred keeps the size rounded to a block', cmd='echo secret > s.txt; shred -n 1 s.txt; stat -c "%s bytes" s.txt', output=pc('echo secret > s.txt; shred -n 1 s.txt; stat -c "%s bytes" s.txt'),
             note='Recorded on our build machine: 7 bytes became 4096, one full block of random data.'),
    ],
)

TRACE = dict(
    heading='Watching files disappear',
    intro='<p>Step through a cleanup. Watch the <b>Files</b> box and the exit status: some deletes work, some are refused.</p>',
    code='''mkdir -p proj/logs
touch proj/a.tmp proj/logs/app.log
rm proj/a.tmp
rm proj/logs
rmdir proj/logs
rm -r proj/logs
rmdir proj
''',
    notes={1: 'Setup :: A folder with a sub-folder.', 3: 'rm :: The file is gone.', 4: 'Refused :: rm without -r does not delete folders.',
           5: 'Refused :: rmdir: logs is not empty.', 6: 'rm -r :: Folder and content gone.', 7: 'rmdir :: proj is empty now, so it goes.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a sysadmin freeing disk space, a data engineer cleaning a failed run, and a DevOps engineer writing a guarded cleanup.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='Free space without stopping the application',
         problem='<p>A log file has grown huge while the application is still writing to it. Free the space now, keep the file.</p>',
         inp='app.log (about 20 KB here, 20 GB on the server)',
         approach=['Check the size.', 'Truncate with <code>&gt;</code>, not rm.'],
         code='''printf 'log line %d\\n' $(seq 1 1500) > app.log
stat -c '%n %s bytes' app.log
> app.log
stat -c '%n %s bytes' app.log
''',
         notes={1: 'Setup :: A big log (seq: Lesson 3.6).', 3: 'Truncate :: The file stays, the content goes.'},
         tryit='Why would <code>rm app.log</code> not free the space while the program runs?'),
    dict(level='i', tag='Data engineering', title='Clean up after a failed run only',
         problem='<p>A job writes part files to <code>out/</code>. If there is no <code>_SUCCESS</code> marker, the run failed: delete the partial output so the next run starts clean.</p>',
         inp='out/part-0000.csv, out/part-0001.csv, no _SUCCESS',
         approach=['Test for the marker.', 'Delete the folder only if it is missing.'],
         code='''mkdir -p out && touch out/part-0000.csv out/part-0001.csv
if [ ! -f out/_SUCCESS ]; then
  echo "run failed: removing partial output"
  rm -rv out
fi
ls
''',
         notes={2: 'Check :: No marker = failed run.', 4: 'Delete :: Partial results would confuse the next job.'},
         tryit='Add <code>touch out/_SUCCESS</code> before the if. What changes?'),
    dict(level='a', tag='DevOps', title='A guarded cleanup of old releases',
         problem='<p>Keep only the newest 2 release folders in <code>releases/</code>, from a script that must never delete outside that folder.</p>',
         inp='releases/v1 … v5 (v5 newest)',
         approach=['List by name (version order) and skip the newest 2.', 'Guard the base folder with :?'],
         code='''base=releases
mkdir -p "$base"/v{1..5}
cd "${base:?}" || exit 1
ls -1 | sort -V | head -n -2 | while read -r r; do
  rm -rv -- "$r"
done
ls
''',
         notes={3: 'Guard :: Stop if base is empty or missing.', 4: 'Select :: sort -V = version order; head -n -2 = all but the last 2.', 5: 'Delete :: -- protects against names starting with a dash.'},
         tryit='Change <code>-2</code> to <code>-3</code> to keep three releases.'),
]

QUIZ = mix([
    dict(q='Which command deletes a folder with files inside?', options=['rm folder', 'rmdir folder', 'rm -r folder', 'rm -d folder'], answer=2,
         why='-r removes the folder and everything inside it.'),
    dict(q='What does -f do?', options=['Asks first', 'Never asks and ignores missing files', 'Deletes folders', 'Shreds'], answer=1,
         why='-f = force: no questions, no “not found” errors.'),
    dict(q='rm * .log (with a space) does what?', options=['Deletes .log files', 'Deletes every file, then complains about .log', 'Nothing', 'Asks first'], answer=1,
         why='* matches every file; “.log” is a separate missing name.'),
    dict(q='How do you delete a file named -x?', options=['rm -x', 'rm "-x"', 'rm -- -x', 'rm -f -x'], answer=2,
         why='-- ends the options; rm ./-x also works.'),
    dict(q='A 20 GB log was deleted but df still shows the disk full. Most likely?', options=['rm failed', 'A process still has it open', 'df is cached', 'The disk is broken'], answer=1,
         why='Data is freed when no name and no open handle remain; lsof +L1 shows it.'),
    dict(q='Which option asks only once before deleting many files?', options=['-i', '-I', '-v', '-d'], answer=1,
         why='-I asks once if more than three files or recursive.'),
    dict(q='Why is shred unreliable on SSDs?', options=['SSDs are read-only', 'Wear levelling writes new data elsewhere', 'shred needs root', 'SSDs encrypt'], answer=1,
         why='The SSD controller may write the overwrite to other cells, leaving the old ones.'),
    dict(q='How do you stop rm -rf "$dir/" when dir is empty?', options=['rm -i', '"${dir:?}"', 'rm --safe', 'quotes only'], answer=1,
         why=':? stops with an error when the variable is empty or unset.'),
])

REVISION = [
    '<code>rm file</code> deletes at once: no bin, no undo. Look first with <code>ls</code>.',
    'Folders: <code>rm -r dir</code> (all inside); empty only: <code>rmdir</code> / <code>rm -d</code>.',
    '<code>-i</code> ask each, <code>-I</code> ask once, <code>-v</code> show, <code>-f</code> no questions (scripts only).',
    'Five dangers: a space in a path, a stray <code>*</code>, an empty variable, the wrong machine, -f by habit.',
    'Guards: quotes, <code>"${dir:?}"</code>, <code>set -u</code>, <code>--</code>, preview with <code>echo</code>.',
    'rm removes names (unlink); data is freed when no name and no open file remain (<code>lsof +L1</code>).',
    'Free a log being written: <code>&gt; app.log</code> or <code>truncate -s 0</code>.',
    '<code>shred -u -z file</code> overwrites then deletes; not reliable on SSD, CoW or snapshotted file systems.',
]

FAQ = [
    ('How do you delete a non-empty directory in Linux?', 'rm -r directory. Check it first with ls -R. rmdir only deletes empty directories.'),
    ('What is the difference between rm -r and rm -rf?', '-f suppresses all prompts (even for write-protected files) and errors for missing files. -rf deletes everything silently.'),
    ('Is there a recycle bin for rm?', 'No. Use a trash folder (mv), gio trash on desktops, trash-cli, version control or backups for undo.'),
    ('How do you delete a file whose name starts with a dash?', 'rm -- -filename or rm ./-filename.'),
    ('Why is disk space not freed after deleting a file?', 'A process still has the file open. The space is freed when it closes the file; find such files with lsof +L1.'),
    ('How do you securely delete a file?', 'shred -u -z file on traditional hard disks. On SSDs and copy-on-write file systems use full-disk encryption and secure erase instead.'),
    ('What does --preserve-root do?', 'It is rm’s default safety: it refuses to recursively delete /.'),
]

PRACTICE_INTRO = 'Tasks for every field. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Delete one file', stmt='Create <code>junk.txt</code>, delete it with a message, then list.', inp='—',
         code='touch junk.txt\nrm -v junk.txt\nls\n', explain='-v confirms the removal.'),
    dict(level='easy', title='Delete a folder tree', stmt='Delete <code>tmp/a/b</code> and everything in it with one command.', inp='tmp/a/b/c.txt',
         code='mkdir -p tmp/a/b && touch tmp/a/b/c.txt\nrm -r tmp\nls\n', explain='-r removes all levels.'),
    dict(level='easy', title='Only the .bak files', stmt='Delete only the <code>.bak</code> files.', inp='a.bak b.bak c.txt',
         code='touch a.bak b.bak c.txt\nrm *.bak\nls\n', explain='The pattern selects only .bak names.'),
    dict(level='medium', title='A name with a dash', stmt='Delete the file called <code>-report</code>.', inp='-report',
         code='touch -- -report\nrm -- -report\nls | wc -l\n', explain='-- ends options.'),
    dict(level='medium', title='Preview first', stmt='Show which files <code>rm *.log</code> would delete, without deleting.', inp='x.log y.log z.txt',
         code='touch x.log y.log z.txt\necho rm *.log\n', explain='echo prints the expanded command.'),
    dict(level='medium', title='Empty a log', stmt='Make <code>app.log</code> 0 bytes without deleting it.', inp='app.log with 3 lines',
         code="printf 'a\\nb\\nc\\n' > app.log\n> app.log\nstat -c '%s bytes' app.log\n", explain='Truncation keeps the file.'),
    dict(level='business', title='Clean old exports securely', stmt='Destroy <code>customers.csv</code> with one overwrite pass and delete it.', inp='customers.csv',
         code="printf 'id,email\\n1,a@b.in\\n' > customers.csv\nshred -u -n 1 customers.csv\nls customers.csv 2>&1\n", explain='-u removes after overwriting.', expect='any'),
    dict(level='business', title='Guarded cleanup', stmt='Delete <code>$dir/*.tmp</code> only if <code>dir</code> is set; here dir=work.', inp='work/a.tmp work/keep.csv',
         code='dir=work\nmkdir -p work && touch work/a.tmp work/keep.csv\nrm -v "${dir:?}"/*.tmp\nls work\n', explain='${dir:?} stops if dir is empty.'),
]

SCN_INTRO = 'Interview questions about deleting files, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you delete a folder that is not empty?”',
        'rmdir reports says “Directory not empty”.',
        'do you know rm -r and its risk?',
        '''<ul>
          <li><code>rm -r reports</code> removes it with everything inside; check with <code>ls -R</code> first.</li>
          <li>Add <code>-i</code> or <code>-I</code> to be asked; avoid <code>-f</code> by habit.</li>
          <li>There is no recycle bin.</li>
        </ul>''', 'reaching for <code>rm -rf</code> without looking.') +
    scn('Operations · on call', 'Junior', 'Disk full after deleting the log',
        'You deleted a 20 GB log on a full server, but df still shows 100%.',
        'do you understand open files and inodes?',
        '''<ol>
          <li><code>sudo lsof +L1</code> shows the deleted file still open by the app.</li>
          <li>Restart or reload the app (or truncate via <code>/proc/PID/fd/N</code>) to release it.</li>
          <li>Next time: <code>&gt; app.log</code> or <code>truncate -s 0</code>, and logrotate with copytruncate or a reload (Lesson 18.1).</li>
        </ol>''', '“reboot the server” as the first step.') +
    scn('DevOps · scripting', 'Mid-level', 'The cleanup script that could delete everything',
        'A script contains <code>rm -rf $WORKDIR/*</code>. Review it.',
        'do you write defensive shell?',
        '''<ul>
          <li>If WORKDIR is empty: <code>rm -rf /*</code>. If it has a space: two paths.</li>
          <li>Fix: <code>set -euo pipefail</code>, <code>rm -rf -- "${WORKDIR:?}"/*</code>, check it is under an allowed prefix, log with -v.</li>
          <li>Prefer deleting a dedicated temp dir created by <code>mktemp -d</code>.</li>
        </ul>''', '“it worked when I tested it”.') +
    scn('Security · compliance', 'Senior', '“Delete the customer data permanently.”',
        'A client asks you to guarantee that exported personal data on a server is unrecoverable.',
        'do you know the limits of file deletion?',
        '''<ul>
          <li>rm only removes names; data remains until overwritten.</li>
          <li>shred helps on HDD files but not on SSDs, journaling/CoW file systems, snapshots or backups.</li>
          <li>Real answer: encryption at rest (delete the key = crypto-erase), secure erase of retired disks, backup retention policies, and documented disposal.</li>
        </ul>''', 'promising that shred makes data unrecoverable everywhere.')
) + interview([
    ('What is the difference between rm, rm -r, rm -f and rmdir?', 'rm deletes files; -r also folders and their content; -f removes prompts and missing-file errors; rmdir deletes only empty folders.'),
    ('How do you make rm safer at the keyboard?', 'alias rm="rm -I", Tab completion, look with ls first, preview with echo, and use a trash folder for anything you might need.'),
    ('What happens to a file’s data when you rm it?', 'The name is unlinked and the link count drops. When it reaches 0 and no process has it open, the blocks are marked free, not wiped.'),
    ('How do you find files that are deleted but still use space?', 'lsof +L1 (or ls -l /proc/*/fd | grep deleted).'),
    ('Why is rm -rf "$dir/" dangerous in scripts?', 'If dir is empty it becomes rm -rf /. Use "${dir:?}" and set -u.'),
    ('Does shred work on SSDs?', 'Not reliably, because of wear levelling and over-provisioning. Use encryption and the drive’s secure erase.'),
    ('How do you delete a file named -rf?', 'rm -- -rf or rm ./-rf.'),
], [
    ('RHCSA (EX200)', '“Create, delete, copy, and move files and directories”, part of the essential tools objectives.'),
    ('LFCS', 'Essential Commands: manage files and directories, including safe removal.'),
    ('CompTIA Linux+', 'File management (rm, rmdir) and data destruction concepts in the security domain.'),
]) + distro('rm is POSIX; the safety extras differ.', [
    ('rm -I', 'yes (GNU)', 'yes', 'no (BSD has -I since newer versions; check man rm)', 'yes'),
    ('--preserve-root default', 'yes', 'yes', 'BSD refuses rm -rf / too', 'yes'),
    ('RHEL root alias', '—', "root’s ~/.bashrc has alias rm='rm -i'", '—', '—'),
    ('shred', 'yes (coreutils)', 'yes', 'no; use rm -P (deprecated) or encryption', 'WSL yes; Git Bash yes (but NTFS)'),
    ('Desktop trash', 'gio trash', 'gio trash', 'Finder only; trash via brew', 'WSL: Windows Recycle Bin not used'),
]) + teaser('3.4', 'Riya has 500 files: report_2025_*.csv, report_2026_*.csv, notes.txt… How does she select exactly the 2026 CSV files from January to March, without typing a single file name?')

CHEATSHEET = cheatsheet('deleting safely', [
    ('Delete', [('rm file', 'delete a file'), ('rm a b c', 'several'), ('rm -r dir', 'folder + content'), ('rm -d dir', 'empty folder'), ('rmdir dir', 'empty folder')]),
    ('Questions', [('rm -i f…', 'ask each time'), ('rm -I f…', 'ask once (>3 / -r)'), ('rm -v f…', 'show removals'), ('rm -f f', 'never ask / no error'), ('alias rm="rm -I"', 'everyday safety')]),
    ('Strange names', [('rm -- -x', 'name starts with -'), ('rm ./-x', 'same'), ('rm "my file"', 'name with space'), ('rm -i *', 'pick one by one'), ('ls -b', 'show odd characters')]),
    ('Scripts', [('"${dir:?}"', 'stop if empty'), ('set -u', 'unset = error'), ('rm -rf -- "$d"', 'quoted, ended'), ('echo rm …', 'preview'), ('mktemp -d', 'own temp folder')]),
    ('Space and secrets', [('> app.log', 'empty an open log'), ('truncate -s 0 f', 'same'), ('lsof +L1', 'deleted but open'), ('shred -u -z f', 'overwrite + delete'), ('mv f ~/.trash/', 'soft delete')]),
])

MINDMAP = mindmap('Deleting safely', [
    ('rm', 'red', ['no bin, no undo', '-r folders', '-d / rmdir empty']),
    ('Questions', 'amber', ['-i each', '-I once', '-f none']),
    ('Five dangers', 'red', ['space in path', 'stray * , empty $var', 'wrong host, -f habit']),
    ('Guards', 'green', ['quotes, --', '${dir:?}, set -u', 'echo preview']),
    ('Inside', 'violet', ['unlink a name', 'open file keeps data', 'lsof +L1, truncate']),
    ('shred', 'blue', ['overwrite then -u', 'HDD yes', 'SSD: encrypt']),
])

LAB = lab('clean up the server folder', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab33 && cd ~/lab33 && rm -rf srv
mkdir -p srv/cache/img srv/logs && cd srv
touch cache/img/{1..3}.png a.tmp b.tmp keep.conf -- -oops
printf 'line\\n' > logs/app.log''',
    tasks=['Delete both <code>.tmp</code> files (and nothing else).',
           'Delete the whole <code>cache</code> folder with its content.',
           'Delete the file called <code>-oops</code>.',
           'Empty <code>logs/app.log</code> to 0 bytes without deleting it.'],
    solution='''rm -v *.tmp
rm -r cache
rm -- -oops
> logs/app.log''',
    check='''cd ~/lab33/srv
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 tmp files gone"   '[ ! -e a.tmp ] && [ ! -e b.tmp ] && [ -f keep.conf ]'
ok "2 cache gone"       '[ ! -e cache ]'
ok "3 -oops gone"       '[ ! -e ./-oops ]'
ok "4 log emptied"      '[ -f logs/app.log ] && [ ! -s logs/app.log ]' ''')
