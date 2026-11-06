import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='03-files-and-directories', lesson='01-creating-files-and-folders-touch-mkdir-and-rmdir', n='3.1',
    module_label='Module 3 · Working with files and directories',
    title='Creating files and folders: touch, mkdir and rmdir',
    desc='Create folders with mkdir and mkdir -p (whole trees, idempotent scripts, -m permissions), empty files and timestamps with touch (-c, -a, -m, -d, -t, -r), remove empty folders with rmdir (-p), and create files with content using echo, printf, cat and here-documents. Every command explained, then used in development, DBA, data engineering, DevOps, security, testing and system administration, with real Bash outputs.',
    og_desc='Two commands instead of fifteen right-clicks: mkdir -p, touch with {01..12}, rmdir, echo, printf and here-docs, used in every IT field.',
    minutes=35, level='Beginner → Advanced',
    lead='Riya needs a project layout and twelve monthly report files. This lesson explains mkdir, touch and rmdir option by option, shows the four ways to create a file with content, and then shows how developers, DBAs, data engineers, DevOps, testers and security teams use each command, with real outputs.',
    chips=['Commands by field', '3 animations', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = '''# Build a project layout
mkdir -p dbda/{data,scripts,reports}
touch dbda/reports/report_{01..12}.csv
printf 'id,name,marks\\n' > dbda/data/students.csv
echo "Created on 2026-11-06" > dbda/README.md
ls dbda
ls dbda/reports | wc -l
cat dbda/data/students.csv
'''

RUN = dict(
    heading='Create a project in seven lines',
    intro='<p>The script creates folders, twelve empty files, a CSV with a header and a README, then checks the result. Run it, then try the tasks.</p>',
    code=MAIN,
    anno=[
        ('mkdir -p dbda/{data,scripts,reports}', 'Three folders inside a new dbda folder. -p creates dbda too.'),
        ('touch dbda/reports/report_{01..12}.csv', 'Bash expands the braces into twelve names; touch makes twelve empty files.'),
        ("printf 'id,name,marks\\n' > dbda/data/students.csv", 'A file with exactly one line: the CSV header.'),
        ('echo "Created on 2026-11-06" > dbda/README.md', '> creates the file (or replaces it).'),
        ('ls dbda/reports | wc -l', 'Count the report files: 12.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. How many folders and files were created?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does <code>echo</code> print here? No files are created. Then run.',
             code='echo mkdir -p app/{src,tests}/{unit,data}\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this fails. Add one option so it works.',
             code='mkdir shop/orders/2026\nls -R shop\n', expect='any'),
        dict(label='4 · Your turn', hint='Create <code>logs/</code> with one empty file per weekday: <code>mon.log</code> … <code>fri.log</code>.',
             code='mkdir -p logs\ntouch logs/{mon,tue,wed,thu,fri}.log\nls logs\n'),
        dict(label='5 · Challenge', hint='Make a file look 30 days old, then prove it with <code>stat</code>.',
             code="touch -d '2026-10-07 09:00' old.txt\ndate -r old.txt '+old.txt %F %T'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the same commands on your own Linux',
    intro='<p>Most commands in this lesson run in the browser runner above. These need your own machine (sudo or a real desktop). Outputs marked typical could not be recorded on our build machine.</p>',
    items=[
        dict(title='1 · A folder under /opt for a new app (needs sudo)', cmd='sudo mkdir -p /opt/myapp/{bin,conf,logs} && ls /opt/myapp', output='bin  conf  logs',
             note='Typical. sudo asks for your password the first time. Then fix ownership with <code>sudo chown -R $USER: /opt/myapp</code> (Lesson 9.3).'),
        dict(title='2 · See the three timestamps', cmd='touch t.txt; stat t.txt', output=pc("touch t.txt; stat t.txt | grep -E '^ *File|^Access: [0-9]|^Modify|^Change'"),
             note='Recorded on our build machine (only the name and time lines shown). Access, Modify and Change all show the same time right after touch.'),
        dict(title='3 · Create a file by typing', cmd='cat > shopping.txt', output='milk\nbread\n(press Ctrl+D on a new line to finish)',
             note='Typical. Everything you type goes into the file until Ctrl+D. Ctrl+C also stops, and keeps what was already typed.'),
        dict(title='4 · Windows users (WSL)', cmd='mkdir -p /mnt/c/Users/$USER/Desktop/linux-lab', output='(a linux-lab folder appears on your Windows desktop)',
             note='Typical. In WSL, your Windows drives are under <code>/mnt/c</code>. Your Windows user name may differ from the Linux one; check with <code>ls /mnt/c/Users</code>.'),
        dict(title='5 · Default permissions of new files', cmd='umask; touch f; mkdir d; ls -ld f d', output=pc("umask; touch f; mkdir d; stat -c '%A %n' f d"),
             note='Recorded on our build machine. umask 0022 → files rw-r--r--, folders rwxr-xr-x (Lesson 9.3).'),
    ],
)

TRACE = dict(
    heading='Watching files and folders appear',
    intro='<p>Step through a small setup script. Watch the <b>Files</b> box: new folders and files appear in <code>~/lab</code>, and the exit status shows when a command fails.</p>',
    code='''mkdir reports
mkdir -p dbda/data
touch dbda/data/a.csv dbda/data/b.csv
echo "id,name" > dbda/data/a.csv
mkdir reports
rmdir reports
rmdir dbda/data
''',
    notes={1: 'mkdir :: One new folder.', 2: 'mkdir -p :: Two levels at once.', 3: 'touch :: Two empty files (0 bytes).',
           4: 'Content :: a.csv now has 8 bytes.', 5: 'Error :: The folder exists: exit status 1, nothing changes.',
           6: 'rmdir :: Empty, so it goes.', 7: 'Refused :: data still holds two files.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s project skeleton, a DBA’s nightly backup folder, and a tester’s old files for a cleanup script.'
EXAMPLES = [
    dict(level='b', tag='Development', title='A Python project skeleton',
         problem='<p>Create <code>shop/</code> with <code>src/shop/</code>, <code>tests/</code>, an empty <code>__init__.py</code>, a README and a .gitignore with two patterns.</p>',
         inp='nothing (empty folder)',
         approach=['One <code>mkdir -p</code> with braces for the folders.', '<code>touch</code> for empty files, <code>printf</code> for the .gitignore.'],
         code='''mkdir -p shop/{src/shop,tests}
touch shop/src/shop/__init__.py shop/README.md
printf '%s\\n' '__pycache__/' '.venv/' > shop/.gitignore
find shop | sort
cat shop/.gitignore
''',
         notes={1: 'Folders :: shop, shop/src, shop/src/shop, shop/tests.', 2: 'Empty files :: 0 bytes each.', 3: 'Content :: one pattern per line.', 4: 'Check :: find lists everything, including hidden files.'},
         tryit='Add a <code>docs/</code> folder and a <code>requirements.txt</code> to the same commands.'),
    dict(level='i', tag='DBA', title='Tonight’s backup folder',
         problem='<p>A backup script must create <code>backups/&lt;year&gt;/&lt;month&gt;/&lt;day&gt;</code> for today and an empty log file inside, and must not fail if it already exists.</p>',
         inp='date = 2026-11-06 (fixed here so the output is stable)',
         approach=['Build the path from the date parts.', '<code>mkdir -p</code> twice to show it is safe to repeat.'],
         code='''today=2026-11-06
dir="backups/${today:0:4}/${today:5:2}/${today:8:2}"
mkdir -p "$dir"
mkdir -p "$dir" && echo "second run: no error"
touch "$dir/backup.log"
find backups | sort
''',
         notes={1: 'Date :: In the real script: today=$(date +%F).', 2: 'Path :: ${today:0:4} = the first 4 characters (Lesson 12.1).', 4: 'Idempotent :: -p never fails on an existing folder.'},
         tryit='Change the date and run again: a second day folder appears next to the first.'),
    dict(level='a', tag='Testing', title='Old files to test a cleanup rule',
         problem='<p>A cleanup job deletes logs older than 7 days. Create 5 logs with ages 1, 3, 8, 15 and 30 days (relative to 2026-11-06) and list them oldest first.</p>',
         inp='ages: 1 3 8 15 30',
         approach=['A loop over the ages.', '<code>touch -d</code> with a date expression; <code>ls -ltr</code> for oldest first.'],
         code='''for age in 1 3 8 15 30; do
  touch -d "2026-11-06 -$age days" "app_$age.log"
done
ls -ltr --time-style=+%F *.log | awk '{print $6, $7}'
''',
         notes={1: 'Loop :: One file per age.', 2: 'Old date :: GNU date understands “-8 days”.', 4: 'Oldest first :: -t sorts by time, -r reverses (the right option is -ltr).'},
         tryit='Which of these would <code>find . -name "*.log" -mtime +7</code> select? (Lesson 7.1.)'),
]

QUIZ = mix([
    dict(q='What does touch do to a file that already exists?', options=['Empties it', 'Updates its timestamps only', 'Deletes and recreates it', 'Gives an error'], answer=1,
         why='touch sets atime and mtime; the content and size stay the same.'),
    dict(q='Which command creates a/b/c when none of them exists?', options=['mkdir a/b/c', 'mkdir -p a/b/c', 'mkdir -r a/b/c', 'touch a/b/c'], answer=1,
         why='-p creates every missing parent folder.'),
    dict(q='rmdir logs prints “Directory not empty”, but ls logs shows nothing. Why?', options=['A bug in rmdir', 'logs contains hidden files', 'You need sudo', 'logs is a file'], answer=1,
         why='ls hides dotfiles; ls -A shows them, and they make the folder non-empty.'),
    dict(q='How many files does touch f_{1..3}_{a,b}.txt create?', options=['3', '5', '6', '2'], answer=2,
         why='3 numbers × 2 letters = 6 names, expanded by bash.'),
    dict(q='Which line adds text without deleting the existing content?', options=['echo hi > f', 'echo hi >> f', 'touch hi f', 'cat f > hi'], answer=1,
         why='>> appends; > truncates the file first.'),
    dict(q='Which touch option never creates a new file?', options=['-a', '-m', '-c', '-r'], answer=2,
         why='-c = --no-create.'),
    dict(q='Default permissions of a new folder with umask 022?', options=['rw-r--r--', 'rwxr-xr-x', 'rwxrwxrwx', 'rwx------'], answer=1,
         why='777 minus 022 = 755 = rwxr-xr-x.'),
    dict(q="In cat > f <<'EOF', what do the quotes around EOF do?", options=['Nothing', 'Stop $VARIABLES from being expanded', 'Make the file hidden', 'Append instead of overwrite'], answer=1,
         why='A quoted delimiter writes the lines exactly as typed.'),
])

REVISION = [
    '<code>mkdir dir</code> one folder; <code>mkdir a b c</code> several; <code>-v</code> reports each.',
    '<code>mkdir -p a/b/c</code>: all missing parents, no error if it exists (idempotent, use in scripts).',
    '<code>mkdir -m 700 dir</code>: set permissions at creation.',
    '<code>touch f</code>: empty file if missing, else update atime and mtime; content never changes.',
    'touch options: <code>-c</code> no create, <code>-a</code>/<code>-m</code> one time only, <code>-d "10 days ago"</code>, <code>-t 202601011200</code>, <code>-r ref</code>.',
    '<code>rmdir dir</code>: only empty folders (hidden files count); <code>-p</code> removes empty parents.',
    'Content: <code>echo "x" &gt; f</code> overwrite, <code>&gt;&gt;</code> append, <code>printf</code> for formats, <code>cat &gt; f &lt;&lt;\'EOF\'</code> for blocks.',
    'Braces <code>{a,b}</code> and <code>{01..12}</code> are expanded by bash; preview with <code>echo</code>.',
]

FAQ = [
    ('What is the difference between touch and mkdir?', 'touch creates empty files (or updates their timestamps); mkdir creates directories.'),
    ('How do you create nested directories in one command?', 'mkdir -p parent/child/grandchild. It creates all missing levels and does not fail if they exist.'),
    ('Why does rmdir fail on a directory that looks empty?', 'It probably contains hidden files (names starting with a dot). Check with ls -A. rmdir only removes truly empty directories.'),
    ('How do you create a file with content without an editor?', 'echo "text" > file, printf "format" > file, or cat > file with a here-document (<<EOF … EOF).'),
    ('What are the three timestamps of a file?', 'atime (last access), mtime (last content modification), ctime (last change of metadata such as permissions). touch updates atime and mtime; ctime changes automatically.'),
    ('How do you create 100 files at once?', 'With brace expansion: touch file_{001..100}.txt. Bash builds the 100 names.'),
    ('Is touch dangerous?', 'No: it never changes content. The danger is > redirection, which empties a file before writing.'),
]

PRACTICE_INTRO = 'Tasks for every field. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Three folders', stmt='Create <code>music</code>, <code>photos</code> and <code>videos</code> with one command and list them.', inp='—',
         code='mkdir music photos videos\nls\n', explain='Several names after mkdir.'),
    dict(level='easy', title='A deep path', stmt='Create <code>college/sem1/dbms/notes</code> in one command.', inp='—',
         code='mkdir -p college/sem1/dbms/notes\nfind college\n', explain='-p creates every level.'),
    dict(level='easy', title='Empty or not?', stmt='Create <code>a.txt</code> with touch and print its size in bytes.', inp='—',
         code="touch a.txt\nstat -c '%s bytes' a.txt\n", explain='A new file from touch has 0 bytes.'),
    dict(level='medium', title='Weekly logs', stmt='Create <code>week/</code> with files <code>day1.log</code> to <code>day7.log</code> and count them.', inp='—',
         code='mkdir week && touch week/day{1..7}.log\nls week | wc -l\n', explain='{1..7} → seven names.'),
    dict(level='medium', title='Append, do not replace', stmt='Write “start” into <code>run.log</code>, then add “end” without losing “start”.', inp='—',
         code='echo start > run.log\necho end >> run.log\ncat run.log\n', explain='> creates, >> appends.'),
    dict(level='medium', title='Clean only the empty ones', stmt='Folders <code>t1 t2 t3</code>; only <code>t2</code> has a file. Remove the empty ones with one command.', inp='t2/keep.txt',
         code='mkdir t1 t2 t3 && touch t2/keep.txt\nrmdir --ignore-fail-on-non-empty t1 t2 t3\nls\n', explain='rmdir deletes t1 and t3 and silently keeps t2.'),
    dict(level='business', title='Data lake partitions', stmt='Create <code>sales/year=2026/month=01</code> … <code>month=03</code> and list them.', inp='—',
         code='mkdir -p sales/year=2026/month={01..03}\nls sales/year=2026\n', explain='The key=value pattern used by Hive and Spark (Hive course, partitions).'),
    dict(level='business', title='Config from a here-document', stmt='Create <code>db.conf</code> with host, port and user lines, using one here-document.', inp='host=localhost, port=3306, user=report',
         code="cat > db.conf <<'EOF'\nhost=localhost\nport=3306\nuser=report\nEOF\ncat db.conf\n", explain='All lines until EOF go into the file.'),
]

SCN_INTRO = 'Interview questions about creating files and folders, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Create 50 test files quickly.”',
        'The interviewer asks you to create file1.txt to file50.txt for a test.',
        'do you know brace expansion and touch?',
        '''<ul>
          <li><code>touch file{1..50}.txt</code>: bash expands the names, touch creates them.</li>
          <li>Check with <code>ls file* | wc -l</code> → 50.</li>
          <li>For sorted names use padding: <code>{01..50}</code>.</li>
        </ul>''', 'a loop that runs touch 50 times, or saying it cannot be done without a script.') +
    scn('Operations · scripting', 'Junior', 'The script that fails on its second run',
        'A start-up script has <code>mkdir /home/app/logs</code>. It works once, then fails every restart.',
        'do you understand idempotent scripts?',
        '''<ol>
          <li>The second run fails with “File exists”, and with <code>set -e</code> the script stops.</li>
          <li>Fix: <code>mkdir -p /home/app/logs</code>: same result every time, no error.</li>
          <li>Same idea for files: <code>touch</code> is also safe to repeat.</li>
        </ol>''', 'adding <code>2&gt;/dev/null</code> to hide the error without fixing the logic.') +
    scn('Data engineering', 'Mid-level', '“How does the next job know the data is ready?”',
        'A Spark job writes many part files. A downstream job must not read half-written output.',
        'do you know marker files?',
        '''<ul>
          <li>The writer creates an empty <code>_SUCCESS</code> file (touch) only after all parts are written.</li>
          <li>The reader (or Airflow sensor) waits for <code>_SUCCESS</code> before reading.</li>
          <li>Writing to a temp folder and renaming it at the end (mv is atomic on one file system, Lesson 3.2) is another safe pattern.</li>
        </ul>''', '“wait 10 minutes and hope it is finished”.') +
    scn('Security · audit', 'Senior', '“Can we trust the file’s modification date?”',
        'During an incident review, someone says a config file was not changed because its mtime is three months old.',
        'do you know that timestamps can be set by any owner?',
        '''<ul>
          <li><code>touch -d</code> or <code>touch -r</code> lets the owner set any atime/mtime, so mtime alone proves nothing.</li>
          <li>ctime cannot be set with touch; it changes on every metadata change, but root can still change the clock.</li>
          <li>Use audit logs (auditd), file integrity tools (AIDE), checksums and backups or version control as evidence.</li>
        </ul>''', 'trusting <code>ls -l</code> dates as proof.')
) + interview([
    ('What is the difference between mkdir and mkdir -p?', 'Plain mkdir creates only the last part of the path and fails if it exists or a parent is missing. -p creates all missing parents and does not fail if the directory already exists.'),
    ('Does touch change the content of a file?', 'No. It creates an empty file if missing; otherwise it only updates the access and modification times.'),
    ('How do you remove a directory that is not empty?', 'rmdir cannot. Use rm -r dir (carefully, after checking with ls -A), covered in Lesson 3.3.'),
    ('What is the difference between > and >>?', '> truncates (empties) the file and writes; >> appends to the end. Both create the file if it does not exist.'),
    ('How do you create a file with several lines from a script?', "A here-document: cat > file <<'EOF' … EOF. Quote EOF to stop variable expansion."),
    ('Why does a new folder have a link count of 2?', 'Its name in the parent folder, plus the . entry inside itself. Each subfolder adds one more (its .. entry).'),
    ('How do you set a specific date on a file?', 'touch -d "2026-01-01 10:00" file, or touch -t 202601011000 file, or copy from another file with touch -r ref file.'),
], [
    ('RHCSA (EX200)', '“Create, delete, copy, and move files and directories”, part of the essential tools objectives.'),
    ('LFCS', 'Essential Commands domain: working with files and directories from the command line.'),
    ('CompTIA Linux+', 'File and directory management with basic commands (mkdir, touch, rmdir) and redirection.'),
]) + distro('These commands are part of POSIX and behave almost the same everywhere; the differences are in the extras.', [
    ('mkdir -p, -m', 'GNU coreutils: yes', 'GNU coreutils: yes', 'BSD mkdir: yes', 'WSL: GNU (same as Ubuntu); Git Bash: GNU'),
    ('mkdir -v output', "mkdir: created directory 'x'", 'same', 'prints just the name: x', 'same as Ubuntu'),
    ('touch -d "10 days ago"', 'yes (GNU)', 'yes (GNU)', 'no: use touch -t or -A (adjust)', 'WSL yes; Git Bash yes'),
    ('rmdir --ignore-fail-on-non-empty', 'yes', 'yes', 'no (GNU only)', 'yes'),
    ('{01..12} zero padding', 'bash 4+: yes', 'bash 4+: yes', 'macOS bash 3.2: no padding (zsh: yes)', 'yes'),
    ('echo -e', 'bash: yes; sh (dash): prints -e', 'bash: yes', 'zsh echo handles \\n without -e', 'yes'),
    ('Case of names', 'case-sensitive: A.txt ≠ a.txt', 'case-sensitive', 'case-insensitive by default (APFS)', 'files under /mnt/c are case-insensitive'),
]) + teaser('3.2', 'Riya copies a 10 GB folder to a backup disk, then needs to update it every night. Copying all 10 GB again takes an hour. Which command copies only what changed?')

CHEATSHEET = cheatsheet('creating files and folders', [
    ('Folders', [('mkdir dir', 'make one folder'), ('mkdir a b c', 'several'), ('mkdir -p a/b/c', 'with parents, no error if exists'), ('mkdir -v', 'report each folder'), ('mkdir -m 700 d', 'set permissions')]),
    ('Empty files and times', [('touch f', 'create empty / update time'), ('touch -c f', 'never create'), ('touch -d "10 days ago" f', 'set a date'), ('touch -t 202601011200 f', 'compact date'), ('touch -r ref f', 'copy the times')]),
    ('Files with content', [('echo "x" > f', 'create / overwrite'), ('echo "x" >> f', 'append'), ("printf '%s\\n' a b > f", 'formatted'), ("cat > f <<'EOF'", 'many lines, until EOF'), ('cat > f  + Ctrl+D', 'type it')]),
    ('Remove folders', [('rmdir d', 'only if empty'), ('rmdir -p a/b/c', 'and empty parents'), ('rmdir -v d', 'report'), ('ls -A d', 'check hidden files first'), ('rm -r d', 'non-empty (Lesson 3.3)')]),
    ('Shell helpers', [('{a,b,c}', 'list of names'), ('{01..12}', 'padded sequence'), ('echo cmd …', 'preview the expansion'), ('!$  /  Alt+.', 'last argument'), ('mkdir -p d && cd d', 'make and enter')]),
])

MINDMAP = mindmap('Creating files and folders', [
    ('mkdir', 'blue', ['one or many folders', '-p: whole path', '-m 700: private']),
    ('touch', 'green', ['empty file, 0 bytes', 'existing: time only', '-d -r -c']),
    ('rmdir', 'amber', ['only empty folders', 'hidden files count', '-p: parents']),
    ('Content', 'violet', ['> overwrite', '>> append', 'printf, here-doc']),
    ('Braces', 'acc', ['{a,b} list', '{01..12} sequence', 'preview with echo']),
    ('Behind it', 'red', ['openat O_CREAT', 'utimensat, mkdir()', 'umask 022 → 644/755']),
])

LAB = lab('set up the college project', 'Build the lab, do the four tasks in your own terminal, then run the checker. It says PASS or FAIL for each task.',
    setup='''mkdir -p ~/lab31 && cd ~/lab31 && rm -rf college old_empty
mkdir -p old_empty/a/b''',
    tasks=['Create <code>college/sem1/{dbms,java,linux}</code> (three subject folders).',
           'Create <code>notes_01.txt</code> to <code>notes_10.txt</code> inside <code>college/sem1/linux</code>.',
           'Create <code>college/README.md</code> whose first line is exactly <code># College</code>.',
           'Remove the empty chain <code>old_empty/a/b</code> completely with one rmdir command.'],
    solution='''mkdir -p college/sem1/{dbms,java,linux}
touch college/sem1/linux/notes_{01..10}.txt
echo "# College" > college/README.md
rmdir -p old_empty/a/b''',
    check='''cd ~/lab31
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 subject folders"  '[ -d college/sem1/dbms ] && [ -d college/sem1/java ] && [ -d college/sem1/linux ]'
ok "2 ten notes files"  '[ "$(ls college/sem1/linux 2>/dev/null | grep -c "^notes_[0-9][0-9].txt$")" -eq 10 ]'
ok "3 README heading"   '[ "$(head -1 college/README.md 2>/dev/null)" = "# College" ]'
ok "4 old_empty gone"   '[ ! -e old_empty ]' ''')
