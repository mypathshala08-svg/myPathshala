import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

cmap = concept_map(
    [('2.3', 'Absolute and relative paths', 'where the new file goes'), ('2.4', 'File types and stat', 'checking what you made'), ('2.5', 'Getting help', 'touch --help, mkdir --help')],
    ['touch: empty files and timestamps', 'mkdir and mkdir -p: folders and whole trees', 'rmdir: remove empty folders only', 'echo, printf, cat and here-docs: files with content', 'brace expansion: 12 files in one command'],
    [('3.2', 'Copying and moving', 'cp, mv, rsync'), ('3.4', 'Wildcards and braces', '*, ?, {a,b}'), ('5.2', 'Redirection', '>, >>, here-documents'), ('9.3', 'Default permissions', 'umask decides rw-r--r--')],
    'Every project, log folder and data pipeline starts with an empty folder and an empty file. Here you learn to make them fast, correctly and safely.')


HOOK = hook('Your manager says: “Set up the DBDA project by lunch: data, scripts and reports folders, and one empty CSV for every month.” With the mouse that is 3 “New folder” and 12 “New file” clicks, and one typo breaks the reporting script. In Linux it is <b>two short commands</b>, and they work the same on a laptop and on a server with no screen.',
    ['create one folder or a whole tree of folders in one command (<code>mkdir</code>, <code>mkdir -p</code>)',
     'create empty files, or change a file’s date without touching its content (<code>touch</code>)',
     'create files with text in them (<code>echo</code>, <code>printf</code>, <code>cat</code>)',
     'remove empty folders safely (<code>rmdir</code>), and know which command to use in which situation'])
ROAD = roadmap([
    ('story', 'The story', 3, 'why this matters'),
    ('decide', 'Which command when?', 2, 'the quick decision chart'),
    ('definition', 'What the commands are', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each command, by field', 12, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'animations, under the hood'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command do I use? (decide in 5 seconds)', [
    ('I need one new folder', 'mkdir name', 'fails if it already exists'),
    ('I need a folder inside folders (a/b/c)', 'mkdir -p a/b/c', 'makes all levels, never fails if it exists'),
    ('I need an empty file', 'touch file', '0 bytes; safe on existing files'),
    ('I need a file with one line of text', 'echo "text" > file', '> replaces old content!'),
    ('I need to add a line to a file', 'echo "text" >> file', '>> keeps old content'),
    ('I need a formatted file (CSV, report)', "printf '%s,%s\\n' …", 'exact format, \\n works'),
    ('I need a file with many lines', "cat > file <<'EOF'", 'type lines, end with EOF'),
    ('I need to change only a file’s date', 'touch -d "date" file', 'content never changes'),
    ('I need to delete an empty folder', 'rmdir name', 'refuses if anything is inside'),
    ('I need to delete a folder with files', 'rm -r name', 'Lesson 3.3: careful, no undo'),
])

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 136, ['$ mkdir -p dbda/{data,scripts,reports}', '$ touch dbda/reports/report_{01..12}.csv', '$ ls dbda/reports | wc -l', ('12', 'acc'), '$ rmdir dbda/data', ('(empty folder removed)', 'dim'), '$ rmdir dbda/reports', ('rmdir: failed to remove ... Directory not empty', 'err')], title='riya@laptop: ~/lab', size=7.6, step=14)
      + t(352, 36, 'Two lines, 3 folders, 12 files:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• mkdir -p: a whole tree', '• {01..12}: the shell counts', '• touch: empty files', '• rmdir: only empty folders', '• it protects your files'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Thirteen right-clicks, or two commands</h2>
  <div class="story">
''' + puzzle('Riya runs <code>touch notes.txt</code> on a file that <b>already has 40 lines</b> of her notes. Are the notes lost? What does change? (Hint: think about what “touch” means in English.)') + '''
    <p class="narration">Riya’s DBDA project needs a folder layout (data, scripts, reports) and one empty CSV for each month, so the reporting script has somewhere to write. On Windows she would right-click “New folder” three times and “New file” twelve times.</p>
''' + scene('A terminal: mkdir -p with braces creates three folders, touch with {01..12} creates twelve report files, rmdir removes an empty folder but refuses a full one.', sc,
            'On Linux the <tspan font-weight="700" class="s-acc">shell does the repetitive work</tspan> for you.') + '''
A> Two commands. <code>mkdir -p dbda/{data,scripts,reports}</code> makes the folders, <code>touch dbda/reports/report_{01..12}.csv</code> makes the twelve files.
R> Twelve files from one line? Who wrote the numbers?
A> The shell. It expands <code>{01..12}</code> into twelve words before touch even starts. touch just sees twelve names.
K> And to clean up, <code>rmdir</code>. It deletes a folder only if it is empty, so you can never lose files with it by accident.
A> Today: <code>touch</code>, <code>mkdir</code>, <code>rmdir</code>, and the ways to create a file <b>with</b> content: <code>echo</code>, <code>printf</code>, <code>cat</code> and here-documents. For each one you will see how it is used by developers, DBAs, data engineers, DevOps, testers and security teams.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
cupboard = ('<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="A school cupboard: mkdir adds a new shelf, mkdir -p adds a shelf with boxes inside, touch puts an empty labelled notebook on a shelf or stamps today’s date on an old one, rmdir removes a shelf only when it is empty.">'
            + ''.join(label_box(14 + k * 156, 22, 144, 104, [a, b, c, d], tone, 9) for k, (a, b, c, d, tone) in enumerate([
                ('New shelf', 'mkdir reports', 'one folder', 'in the cupboard', 'blue'),
                ('Shelf with boxes', 'mkdir -p a/b/c', 'all levels at once', 'no error if it exists', 'violet'),
                ('Empty notebook', 'touch notes.txt', 'new and empty, or', 'stamp today’s date', 'green'),
                ('Remove a shelf', 'rmdir old', 'only if it is', 'completely empty', 'amber')]))
            + t(320, 160, 'Writing inside the notebook = echo, printf, cat > file (or an editor).', 9.4, 'ink2')
            + t(320, 182, 'touch never writes words into it; it only creates it or updates its date.', 9.4, 'acc', bold=True)
            + '<text x="632" y="214" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Creating files and folders at four depths', [
    ('v', 'No jargon: shelves and notebooks', '      <p>Think of your home folder as a school cupboard.</p>' + cupboard + '''
      <ul>
        <li>A <b>folder</b> (directory) is a shelf. <code>mkdir</code> = “make a new shelf”.</li>
        <li>A <b>file</b> is a notebook. <code>touch</code> = “put a new, empty notebook here” (or, if it is already there, write today’s date on the cover).</li>
        <li><code>rmdir</code> takes a shelf away, but only an empty one, so no notebook is ever thrown away by mistake.</li>
      </ul>'''),
    ('b', 'The commands you will type every day', '''      <ul>
        <li><code>mkdir reports</code> creates one folder; <code>mkdir a b c</code> creates three.</li>
        <li><code>mkdir -p project/src/utils</code> creates every missing level, and gives <b>no error</b> if it already exists.</li>
        <li><code>touch file.txt</code> creates an empty file (0 bytes). On an existing file it changes nothing inside, only the time.</li>
        <li><code>rmdir old</code> removes an empty folder; for a folder with files you need <code>rm -r</code> (Lesson 3.3).</li>
        <li>Files with text: <code>echo "Hello" &gt; file.txt</code> (overwrite), <code>echo "more" &gt;&gt; file.txt</code> (add at the end).</li>
      </ul>'''),
    ('i', 'Timestamps, braces and content', '''      <ul>
        <li>Each file has three times: <b>access</b> (atime, last read), <b>modify</b> (mtime, content changed) and <b>change</b> (ctime, details changed). <code>touch</code> sets atime and mtime to now; <code>-a</code> or <code>-m</code> sets only one; <code>-d</code> or <code>-t</code> sets any date; <code>-r ref</code> copies another file’s times.</li>
        <li><code>touch -c</code> (no-create) updates only files that already exist.</li>
        <li>Brace expansion is done by bash, not by mkdir or touch: <code>{a,b}</code> = a list, <code>{01..12}</code> = a sequence with zero padding.</li>
        <li><code>printf</code> understands <code>\\n</code>, <code>\\t</code>, <code>%s</code>, <code>%d</code> everywhere; bash’s <code>echo</code> needs <code>-e</code> for escapes. Use printf in scripts.</li>
        <li><code>cat &gt; file &lt;&lt;'EOF'</code> … <code>EOF</code> (a here-document) writes many lines at once: perfect for config files in scripts.</li>
      </ul>'''),
    ('a', 'Behind the screen: what really happens', '''      <ul>
        <li><code>touch</code> calls <code>openat(…, O_CREAT)</code> to create the file if needed, then <code>utimensat()</code> to set the times. A new file gets a new <b>inode</b> (Lesson 10.1) and a name in the folder.</li>
        <li><code>mkdir</code> is one system call, <code>mkdir()</code>. A new folder already contains two entries, <code>.</code> and <code>..</code>, so its link count starts at 2.</li>
        <li><code>rmdir</code> calls <code>rmdir()</code>, which the <b>kernel</b> refuses with ENOTEMPTY if anything except . and .. is inside. The safety check is in the kernel, not in the command.</li>
        <li>New permissions = default (666 for files, 777 for folders) minus the <b>umask</b> (usually 022) → <code>rw-r--r--</code> and <code>rwxr-xr-x</code>. <code>mkdir -m 700</code> sets the mode directly (Lesson 9.3).</li>
        <li>An empty file uses 0 data blocks: only its inode and the name in the folder exist.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>touch, mkdir and rmdir</h2>
''' + def_block(
    '<code>mkdir</code> (make directory) creates one or more directories; with <code>-p</code> it also creates missing parent directories and does not fail if the directory exists. <code>rmdir</code> (remove directory) deletes directories only when they are empty. <code>touch</code> sets the access and modification timestamps of files to the current time (or a given time), and creates any file that does not exist as an empty file. Files with content are created by redirecting the output of <code>echo</code>, <code>printf</code> or <code>cat</code> into a file.',
    '<code>mkdir</code> makes folders, <code>touch</code> makes empty files (or updates their time), <code>rmdir</code> removes empty folders.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Directory', 'A folder: a list of names that point to files.'),
    ('Parent directory', f'The folder one level up: <code>..</code> {gl("path-absolute-and-relative", "Glossary →")}'),
    ('Timestamp', f'Access, modify and change time of a file. {gl("unix-epoch-and-timestamps", "Glossary →")}'),
    ('Inode', f'The record that stores a file’s details. {gl("inode", "Glossary →")}'),
    ('Brace expansion', f'<code>{{a,b}}</code> and <code>{{1..5}}</code>, done by bash. {gl("brace-expansion", "Glossary →")}'),
    ('Redirection', f'<code>&gt;</code> and <code>&gt;&gt;</code> send output into a file. {gl("redirection-2", "Glossary →")}'),
    ('Here-document', f'Many lines fed into a command until EOF. {gl("here-document-eof", "Glossary →")}'),
    ('umask', f'Decides default permissions of new files. {gl("umask", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('mkdir', 'make directory', 'Make a new folder.'),
    ('rmdir', 'remove directory', 'Remove an (empty) folder.'),
    ('touch', 'to touch a file', 'Like touching a book: you leave a fresh fingerprint (time), not new pages.'),
    ('-p', 'parents', 'Create parent folders too.'),
    ('-v', 'verbose', 'Tell me what you did.'),
    ('-c', 'no-create', 'touch: do not create missing files.'),
    ('printf', 'print formatted', 'From the C function printf.'),
    ('EOF', 'end of file', 'The usual end marker of a here-document.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('One folder / several', '<code>mkdir logs</code> · <code>mkdir logs tmp backup</code>'),
    ('Folder tree in one go', '<code>mkdir -p app/src/utils</code>'),
    ('Empty file', '<code>touch notes.txt</code> (0 bytes)'),
    ('Many files', '<code>touch day_{01..31}.log</code>'),
    ('File with text', '<code>echo "text" &gt; f.txt</code> · append: <code>&gt;&gt;</code>'),
    ('Remove empty folder', '<code>rmdir old</code> · whole empty chain: <code>rmdir -p a/b/c</code>'),
]) + '\n' + lv + didyou('Brace expansion like <code>{01..12}</code> is done by <b>bash</b>, not by touch. That is why it also works with mkdir, cp and echo. Try <code>echo report_{01..12}.csv</code>: echo just prints what the shell built.') + '''
EXAM> “Difference between touch and mkdir; how do you create a directory tree?” → touch creates empty files or updates timestamps, mkdir creates directories; <code>mkdir -p a/b/c</code> creates all missing parents and does not fail if the tree exists; rmdir removes only empty directories.
''' + qc('You run <code>mkdir -p project/src</code> twice. What happens the second time?', 'Nothing, and no error: <code>-p</code> means “make sure it exists”. Without <code>-p</code>, the second run fails with “File exists”.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Every way to create a file or a folder</h2>
''' + table(['Way', 'Creates', 'Content', 'Best for'], [
    ['<code>touch f.txt</code>', 'empty file', 'none (0 bytes)', 'placeholders, marker files, timestamps'],
    ['<code>echo "hi" &gt; f.txt</code>', 'file with one line', 'overwrites!', 'quick one-line files'],
    ['<code>echo "hi" &gt;&gt; f.txt</code>', 'file, or adds to it', 'appends', 'logs, adding lines'],
    ['<code>printf "%s\\n" a b &gt; f.txt</code>', 'formatted file', 'exact format', 'CSV rows, scripts'],
    ['<code>cat &gt; f.txt</code> then Ctrl+D', 'file you type', 'typed lines', 'quick notes at the terminal'],
    ['<code>cat &gt; f.txt &lt;&lt;\'EOF\'</code> … <code>EOF</code>', 'many-line file', 'block of text', 'config files in scripts'],
    ['<code>nano f.txt</code> / <code>vim f.txt</code>', 'file in an editor', 'anything', 'editing by hand (Module 4)'],
    ['<code>truncate -s 1M f.bin</code>', 'file of a given size', 'zeros (sparse)', 'testing disk-full or upload limits'],
    ['<code>mktemp</code> / <code>mktemp -d</code>', 'unique temp file / folder', 'none', 'scripts that need a safe temp name'],
    ['<code>mkdir dir</code>', 'one folder', '. and .. only', 'one folder'],
    ['<code>mkdir -p a/b/c</code>', 'whole path', '—', 'project trees, scripts (idempotent)'],
    ['<code>mkdir -p p/{src,test}</code>', 'several branches', '—', 'project skeletons'],
], minw=640) + mistake('echo -e is not needed; echo cannot use \\n anyway', 'printf "line1\\nline2\\n" > f.txt   (or echo -e "line1\\nline2")',
                       'A common classroom note says “echo cannot use escape characters”. In bash, <code>echo -e</code> does understand <code>\\n</code> and <code>\\t</code>; plain <code>echo</code> prints them literally. <code>printf</code> always understands them and behaves the same in every shell, which is why scripts prefer it.') + qc('Which one overwrites an existing file: <code>&gt;</code> or <code>&gt;&gt;</code>?', '<code>&gt;</code> empties the file first, then writes. <code>&gt;&gt;</code> adds to the end and keeps what was there.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands by field + steps
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">For every command: what it does, every important option and when to use it, one real run, and then how it is used in different jobs. All outputs were recorded on a real Ubuntu machine as the user riya.</p>
''' + cmdcard_u(['you need a new folder, or a whole path of folders', 'a script must make sure a folder exists (<code>-p</code>)', 'you want private folders from the start (<code>-m 700</code>)'], ['the name already exists as a file', 'you only want to check if a folder exists (use <code>[ -d dir ]</code>)'])('mkdir', 'mkdir', 'make directory',
    'Creates one or more folders. With <code>-p</code> it creates a whole path, including every missing parent, and is happy if the folder already exists.',
    'mkdir [OPTION]... DIRECTORY...', 'change',
    [('(none)', 'create the folder(s) named', 'one or a few folders in the current place'),
     ('-p, --parents', 'create missing parent folders; no error if it exists', 'nested paths, scripts that may run twice'),
     ('-v, --verbose', 'print a line for each folder created', 'seeing exactly what was made; logs'),
     ('-m, --mode=MODE', 'set the permissions of the new folder', 'private folders: <code>-m 700</code>'),
     ('a b c', 'several folders in one command', 'project folders'),
     ('{x,y,z}', 'brace expansion (bash) builds the list', 'many similar folders')],
    dict(cmd='mkdir reports\nmkdir -pv dbda/data/raw\nls -F', note='<code>-v</code> shows that -p made all three levels. <code>ls -F</code> marks folders with a trailing <code>/</code>.'),
    [('dev', [
        dict(situation='Start a new Python project with source, tests and docs folders.', cmd='mkdir -p myapp/{src/myapp,tests,docs}\nls -R myapp',
             why='One command, any depth. The braces give three branches; -p makes the parent <code>myapp</code> and <code>src</code> automatically.'),
        dict(situation='A build script must create its output folder, whether or not it already exists.', cmd='mkdir -p build/dist && echo "ready"\nmkdir -p build/dist && echo "still ready"',
             why='<code>-p</code> makes the script <b>idempotent</b>: safe to run again and again. Plain mkdir would fail on the second run.')]),
     ('dba', [
        dict(situation='Create a dated folder for tonight’s MySQL backup.', cmd='mkdir -p backups/mysql/2026-11-06\nls backups/mysql',
             why='A date in the path (often <code>$(date +%F)</code> in the real script) keeps every night’s dump separate and easy to clean up later.'),
        dict(situation='Archive logs go in one folder per month of the year.', cmd='mkdir -p archive/2026/{01..12}\nls archive/2026 | tr "\\n" " "; echo',
             why='<code>{01..12}</code> pads with zeros, so the folders sort correctly (01, 02 … 10, 11, 12).')]),
     ('data', [
        dict(situation='A data-lake style layout: raw, cleaned and curated zones, partitioned by date.', cmd='mkdir -pv lake/{raw,clean,curated}/sales/dt=2026-11-06 | head -4',
             why='Hive, Spark and many data lakes use <code>key=value</code> folder names for partitions. One mkdir -p builds the whole pattern.')]),
     ('devops', [
        dict(situation='Prepare folders for a Docker app: config, data volume and logs.', cmd='mkdir -p /home/riya/lab/srv/shop/{config,data,logs}\nls /home/riya/lab/srv/shop',
             why='An absolute path works from any current folder; in real servers this is often <code>/srv/app</code> or <code>/opt/app</code> (with sudo).')]),
     ('sec', [
        dict(situation='A folder for private keys that only you may open.', cmd='mkdir -m 700 secrets\nls -ld secrets | cut -c1-10',
             why='<code>-m 700</code> sets <code>rwx------</code> at creation time, so there is no moment when others could read it (Lesson 9.2).')]),
     ('sys', [
        dict(situation='An admin creates folders for a service under /var/log, which needs root.', cmd='sudo mkdir -p /var/log/myapp', typical='(no output: the folder is created as root)',
             why='System folders belong to root. Without sudo you get “Permission denied” (see Error messages below).')]),
     ('qa', [
        dict(situation='Fresh test fixtures folder for every test run.', cmd='mkdir -p fixtures/{input,expected,actual}\nls fixtures',
             why='Tests compare <code>actual</code> with <code>expected</code>; keeping them in fixed folders makes the comparison easy (Lesson 6.3: diff).')]),
     ('design', [
        dict(situation='Design a standard layout every team must follow (like the Linux FHS, Lesson 2.1).', cmd='mkdir -p app/{bin,conf,lib,logs,run,tmp}\nls app | tr "\\n" " "; echo',
             why='A fixed layout means scripts, monitoring and backups know where to look, on every server. bin = programs, conf = settings, run = PID files.')]),
    ],
    anat=anatomy([('mkdir', 'cmd', 'command'), ('-pv', 'opt', 'options -p -v'), ('app/{src,tests}', 'arg', 'argument (expanded by bash)')], 'Options start with a dash; you can combine short options (<code>-p -v</code> = <code>-pv</code>). Everything after the options are folder names.')
) + mistake('mkdir dbda/data/raw     (when dbda/ does not exist yet)', 'mkdir -p dbda/data/raw',
            'Without <code>-p</code>, mkdir only creates the <b>last</b> part and fails with “No such file or directory” if a parent is missing.') + cmdcard_u(['you need an empty file or a placeholder (marker file)', 'you want to change a file’s date for testing or a build tool', 'you want many empty files at once with braces'], ['you want text in the file (use echo, printf or cat)', 'you want to empty a file (touch never does that; use <code>&gt; file</code>)'])('touch', 'touch', 'touch a file (update its time)',
    'Creates an empty file if it does not exist. If it does exist, touch leaves the content alone and only sets its access and modification time to now (or to the time you give).',
    'touch [OPTION]... FILE...', 'change',
    [('(none)', 'create empty file(s), or update their time to now', 'placeholders; “refresh” a file'),
     ('-c, --no-create', 'do not create missing files', 'update times only where files exist'),
     ('-a', 'change only the access time', 'rare: testing tools that read atime'),
     ('-m', 'change only the modification time', 'make a build tool think a file changed'),
     ('-d, --date=STRING', 'use this date instead of now', '“10 days ago”, “2026-01-01 09:00”'),
     ('-t [[CC]YY]MMDDhhmm[.ss]', 'date in compact digits', 'scripts, old Unix style'),
     ('-r, --reference=FILE', 'copy the times of another file', 'keep the original date after editing')],
    dict(cmd='echo "40 lines of notes" > notes.txt\ntouch notes.txt new.txt\nstat -c "%A %s bytes  %n" notes.txt new.txt', note='notes.txt keeps its 18 bytes (content untouched); new.txt is a new, empty file of 0 bytes.'),
    [('dev', [
        dict(situation='Create the usual empty starter files of a project.', cmd='touch README.md .gitignore requirements.txt\nls -A',
             why='Several names in one command. <code>ls -A</code> also shows the hidden <code>.gitignore</code> (Lesson 2.4).'),
        dict(situation='Force <code>make</code> to rebuild by marking a source file as changed.', cmd='touch -m main.c && date -r main.c "+main.c modified %F %T"',
             why='Build tools compare modification times; touch -m makes the file look newer than its output.')]),
     ('data', [
        dict(situation='A Spark or Hadoop job writes an empty <code>_SUCCESS</code> file when it finishes; the next job waits for it.', cmd='mkdir -p output/sales && touch output/sales/_SUCCESS\n[ -f output/sales/_SUCCESS ] && echo "upstream done, start the next job"',
             why='An empty “marker file” is a cheap signal between programs. Airflow and other schedulers check for it.'),
        dict(situation='Twelve empty monthly CSV files for a report.', cmd='touch report_{01..12}.csv\nls report_* | head -3; ls report_* | wc -l',
             why='Bash expands the braces into twelve names before touch runs.')]),
     ('qa', [
        dict(situation='Test a “delete logs older than 7 days” script, without waiting a week.', cmd='touch -d "10 days ago" old.log\ntouch new.log\nfor f in $(ls -t *.log); do echo "$f $(date -r $f +%F)"; done',
             why='<code>-d</code> sets any date, so you can create old-looking test files in seconds. (Your dates will be relative to today.)'),
        dict(situation='Check that a script does not create files that should already exist.', cmd='touch -c missing.txt\nls missing.txt 2>&1',
             why='<code>-c</code> never creates: a quick way to update times only on files that really exist.', expect='any')]),
     ('dba', [
        dict(situation='Create an empty log file before starting a database import, so a monitor can follow it.', cmd='touch import_2026-11-06.log && stat -c "%A %s bytes  %n" import_2026-11-06.log',
             why='<code>tail -f</code> (Lesson 3.5) needs the file to exist; touch creates it first.')]),
     ('sec', [
        dict(situation='After fixing a config file, keep its original timestamp (for example, for a change audit you compare later).', cmd='touch -d "2026-01-15 10:00" app.conf\ncp app.conf edited.conf && echo "port=8080" >> edited.conf\ntouch -r app.conf edited.conf\nfor f in app.conf edited.conf; do echo "$f $(date -r $f +%F_%T)"; done',
             why='<code>-r</code> copies the time of a reference file. Security note: because anyone can do this, a file’s timestamp alone is <b>not proof</b> of when it changed. Investigators also use logs and checksums.')]),
     ('sys', [
        dict(situation='Is this folder writable for me? Try to create a file.', cmd='touch /etc/test.txt 2>&1; touch ~/lab/test.txt && echo "lab is writable"',
             why='A quick, harmless write test. /etc belongs to root, so it is refused; your home folder is yours.', expect='any')]),
     ('devops', [
        dict(situation='A deployment creates a “maintenance mode” flag; the web app shows a maintenance page while it exists.', cmd='touch maintenance.flag && [ -e maintenance.flag ] && echo "site in maintenance"\nrm maintenance.flag && echo "site live"',
             why='Many apps and load balancers check for a flag file like this (Laravel, health checks). Creating and deleting it is instant and atomic.')]),
    ],
    anat=anatomy([('touch', 'cmd', 'command'), ('-d "10 days ago"', 'opt', 'option with a value'), ('old.log', 'arg', 'file name')], 'An option that takes a value (<code>-d</code>) is followed by that value; quote it if it has spaces.')
) + cmdcard_u(['a folder is empty and you want it gone', 'cleanup scripts that must never delete data', 'removing a chain of empty folders (<code>-p</code>)'], ['the folder has files you also want to delete (use <code>rm -r</code>, Lesson 3.3)', 'you want to delete a file (use <code>rm</code>)'])('rmdir', 'rmdir', 'remove directory',
    'Deletes folders, but only empty ones. If anything is inside, it refuses, so it can never delete your files.',
    'rmdir [OPTION]... DIRECTORY...', 'change',
    [('(none)', 'remove the empty folder(s)', 'clean up after moving files out'),
     ('-p, --parents', 'also remove the parents, if they become empty', 'remove a whole empty chain: <code>a/b/c</code>'),
     ('-v, --verbose', 'print each folder removed', 'see exactly what went'),
     ('--ignore-fail-on-non-empty', 'do not report folders that are not empty', 'cleanup scripts over many folders')],
    dict(cmd='mkdir -p old/empty full\ntouch full/data.csv\nrmdir old/empty && echo "empty folder removed"\nrmdir full', note='The second rmdir fails on purpose: <code>full</code> contains data.csv. For non-empty folders use <code>rm -r</code> (Lesson 3.3), carefully.', expect='any'),
    [('sys', [
        dict(situation='Remove a whole chain of empty folders left by an uninstall.', cmd='mkdir -p tmp/a/b/c\nrmdir -pv tmp/a/b/c',
             why='<code>-p</code> walks up the path and removes each parent once it is empty.')]),
     ('data', [
        dict(situation='After a pipeline run, remove only the empty partition folders and keep the ones with data.', cmd='mkdir -p out/dt=01 out/dt=02 out/dt=03\ntouch out/dt=02/part-0000.csv\nrmdir --ignore-fail-on-non-empty out/*\nls out',
             why='rmdir is a safe filter: it deletes the empty ones and silently keeps any folder that holds data.')]),
     ('sec', [
        dict(situation='Why prefer rmdir to rm -r in cleanup scripts?', cmd='mkdir -p logs && touch logs/app.log\nrmdir logs 2>&1; ls logs',
             why='The kernel itself refuses to remove a non-empty folder with rmdir, so a typo in a path cannot wipe data. rm -r would delete everything without asking.', expect='any')]),
     ('devops', [
        dict(situation='Remove the per-release folders that are empty after a rollback.', cmd='mkdir -p releases/v1 releases/v2 releases/v3\ntouch releases/v3/app.jar\nrmdir -v --ignore-fail-on-non-empty releases/*\nls releases',
             why='Empty releases go, the release with an app stays. -v logs what was removed.')]),
    ]
) + cmdcard_u(['echo: one quick line', 'printf: exact format, CSV rows, scripts', 'cat with a here-document: a whole config file from a script'], ['the file must keep its old content and you typed <code>&gt;</code> (use <code>&gt;&gt;</code>)', 'long files you will edit by hand (use nano or vim, Module 4)'])('content', 'echo · printf · cat', 'files with content',
    'Three ways to create a file <b>with text</b> in it. They all print text; the <code>&gt;</code> or <code>&gt;&gt;</code> redirection sends that text into a file instead of the screen (Lesson 5.2).',
    'echo [TEXT] > FILE · printf FORMAT [ARGS] > FILE · cat > FILE <<\'EOF\' … EOF', 'change',
    [('echo "text" > f', 'write one line; <b>overwrites</b> the file', 'quick one-line files'),
     ('echo "text" >> f', 'add a line at the end', 'logs, lists'),
     ('echo -e "a\\tb\\n"', 'bash echo: understand escapes', 'quick tests (use printf in scripts)'),
     ('echo -n "text"', 'no newline at the end', 'prompts, joining output'),
     ('printf "%s,%d\\n" name 42', 'formatted text: %s text, %d number, \\n newline', 'CSV rows, aligned reports'),
     ('cat > f', 'type lines, finish with Ctrl+D', 'quick notes by hand'),
     ("cat > f <<'EOF'", 'here-document: all lines until EOF', 'config files and scripts from a script')],
    dict(cmd='''echo "DBDA Test Report" > test_info.txt
echo "Test executed on: 2026-11-06" >> test_info.txt
printf "Test ID: %d\\nStatus: %s\\n" 101 "Passed" >> test_info.txt
cat test_info.txt''', note='<code>&gt;</code> created the file, <code>&gt;&gt;</code> added lines. In a real script the date would be <code>$(date +%F)</code>.'),
    [('data', [
        dict(situation='Create a small CSV with a header row to test a pipeline.', cmd="printf '%s,%s,%s\\n' id name marks 1 Asha 91 2 Ravi 78 > marks.csv\ncat marks.csv",
             why='printf reuses its format for every 3 arguments, so one command writes the header and all rows.')]),
     ('devops', [
        dict(situation='A deployment script writes a config file.', cmd="cat > app.env <<'EOF'\nAPP_PORT=8080\nDB_HOST=db.internal\nLOG_LEVEL=info\nEOF\ncat app.env",
             why="Quoting <code>'EOF'</code> keeps <code>$</code> and backticks exactly as written. Without quotes, bash would expand variables inside."),
        dict(situation='The same, but with values filled in from variables.', cmd='PORT=9090\ncat > app.env <<EOF\nAPP_PORT=$PORT\nEOF\ncat app.env',
             why='Unquoted EOF: bash replaces <code>$PORT</code> before writing.')]),
     ('dev', [
        dict(situation='Add entries to .gitignore without opening an editor.', cmd="printf '%s\\n' '__pycache__/' '*.log' '.env' >> .gitignore\ncat .gitignore",
             why='<code>&gt;&gt;</code> keeps anything already in the file; printf writes one pattern per line.')]),
     ('sys', [
        dict(situation='Log a line with a timestamp from a cron job.', cmd='echo "$(date +%F) backup finished" >> cron.log\ncut -d" " -f2- cron.log',
             why='Each run appends one line; nothing is lost. (The date part is cut off here because it changes every day.)')]),
     ('sec', [
        dict(situation='Create a file that will hold a secret, with safe permissions from the start.', cmd='(umask 077; echo "API_KEY=changeme" > token.txt)\nls -l token.txt | cut -c1-10',
             why='Setting <code>umask 077</code> in a subshell makes the new file <code>rw-------</code>: nobody else can read it, not even for a moment.')]),
     ('qa', [
        dict(situation='Create an input file with tricky content: a tab, an empty line and spaces at the end.', cmd="printf 'a\\tb\\n\\nend  \\n' > tricky.txt\ncat -A tricky.txt",
             why='<code>cat -A</code> shows tabs as <code>^I</code> and line ends as <code>$</code>: you can see exactly what is in the test file.')]),
    ]
) + mistake('echo "Test executed on: $(date)" > test.txt     (to add one more line)', 'echo "Test executed on: $(date)" >> test.txt',
            'One <code>&gt;</code> replaces the whole file. Double-check <code>&gt;</code> vs <code>&gt;&gt;</code> before pressing Enter; with <code>set -o noclobber</code> bash refuses to overwrite with <code>&gt;</code>.') + undo('What if you created something by mistake?', [
    ('A folder you just made:', '<code>rmdir name</code> removes it while it is still empty. Safe.'),
    ('Files made with a wrong brace pattern:', 'repeat the <b>same</b> pattern with <code>echo</code> first to see the names, then remove them: <code>echo report_{01..12}.csv</code> → <code>rm report_{01..12}.csv</code>.'),
    ('Overwritten a file with &gt;:', 'there is <b>no undo</b> in the shell. Only a backup, version control (git) or a file-system snapshot can bring the old content back. Prevent it with <code>set -o noclobber</code>.'),
    ('touch changed a file’s date:', 'only the time changed; restore it with <code>touch -r backup_copy file</code> or <code>touch -d "old date" file</code>.'),
    ('Preview before running:', 'put <code>echo</code> in front: <code>echo mkdir -p app/{a,b}</code> prints what would run, without running it.'),
]) + errors('The errors students see most with these commands. Each was really produced on our build machine, with the exit status the shell got (0 = success).', [
    dict(cmd='mkdir reports\nmkdir reports', meaning='The folder (or a file with that name) already exists.', fix='Use <code>mkdir -p</code> if you only want to be sure it exists.'),
    dict(cmd='mkdir dbda/data/raw', meaning='A parent folder in the path (dbda or data) is missing.', fix='<code>mkdir -p dbda/data/raw</code> creates all missing parents.'),
    dict(cmd='mkdir /var/log/myapp', meaning='You are not allowed to write in that folder; it belongs to root.', fix='Work in your home folder, or use <code>sudo</code> if it is your server and the folder really belongs there.'),
    dict(cmd='mkdir full && touch full/a.txt\nrmdir full', meaning='rmdir only removes empty folders.', fix='Move or delete what is inside first, or use <code>rm -r full</code> after checking it with <code>ls full</code> (Lesson 3.3).'),
    dict(cmd='rmdir notes.txt 2>/dev/null; touch notes.txt\nrmdir notes.txt', meaning='The name is a file, not a folder.', fix='Use <code>rm notes.txt</code> for files.'),
    dict(cmd='touch a.txt\nmkdir a.txt', meaning='A file called a.txt already exists, so a folder with the same name cannot be made.', fix='Choose another name; names in one folder must be unique.'),
]) + stepper([
    ('1. Plan the layout', '<p>Write it down: <code>project/{data,scripts,reports}</code>.</p>', 'Behind the screen: nothing happens yet; planning avoids messy renames later.'),
    ('2. Preview with echo', '<p><code>echo mkdir -p project/{data,scripts,reports}</code> shows the three paths.</p>', 'Behind the screen: bash expands the braces, echo prints the result.'),
    ('3. Create the folders', '<p><code>mkdir -pv project/{data,scripts,reports}</code></p>', 'Behind the screen: one mkdir() system call per folder; -p skips folders that exist.'),
    ('4. Create the files', '<p><code>touch project/reports/report_{01..12}.csv</code></p>', 'Behind the screen: openat(O_CREAT) makes 12 inodes, each 0 bytes.'),
    ('5. Add content', '<p><code>printf "id,name\\n" &gt; project/data/students.csv</code></p>', 'Behind the screen: the shell opens the file for writing; printf writes into it.'),
    ('6. Check', '<p><code>ls -R project</code> or <code>find project</code> (Lesson 7.1).</p>', 'Behind the screen: reading the folder entries back.'),
]) + qc('Which command shows the paths <code>mkdir -p app/{a,b}/logs</code> would create, without creating them?', '<code>echo mkdir -p app/{a,b}/logs</code> prints <code>mkdir -p app/a/logs app/b/logs</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def tbl(rows, hl=None, title='notes.txt'):
    o = label_box(196, 16, 152, 22, [title], 'acc', 9)
    for k, (a, b) in enumerate(rows):
        o += label_box(196, 42 + k * 24, 152, 20, [f'{a}: {b}'], 'green' if hl == k else 'card', 8.4)
    return o
see = [term(14, 16, 172, 120, ['$ ls -l notes.txt', ('18 bytes, 09:15', 'out')], title='riya@laptop', size=7.6) + tbl([('size', '18 bytes'), ('content', '40 lines…'), ('mtime', '09:15'), ('atime', '09:15')]) + cap('Before: a file with notes, last changed at 09:15.', '', 'card', y=150, h=34),
       term(14, 16, 172, 120, ['$ touch notes.txt'], title='riya@laptop', size=7.6) + tbl([('size', '18 bytes'), ('content', '40 lines…'), ('mtime', '10:41'), ('atime', '10:41')], 2) + cap('touch on an existing file: only the times change.', '', 'blue', y=150, h=34),
       term(14, 16, 172, 120, ['$ touch notes.txt', '$ cat notes.txt', ('40 lines of notes', 'acc')], title='riya@laptop', size=7.6) + tbl([('size', '18 bytes'), ('content', '40 lines…'), ('mtime', '10:41'), ('atime', '10:41')], 1) + cap('The content is untouched.', '', 'green', y=150, h=34),
       term(14, 16, 172, 120, ['$ touch new.txt'], title='riya@laptop', size=7.6) + tbl([('size', '0 bytes'), ('content', '(empty)'), ('mtime', '10:42'), ('atime', '10:42')], 0, 'new.txt') + cap('A missing file: touch creates it, 0 bytes.', '', 'blue', y=150, h=34),
       term(14, 16, 172, 120, ['$ echo hi > notes.txt'], title='riya@laptop', size=7.6) + tbl([('size', '3 bytes'), ('content', 'hi'), ('mtime', '10:43'), ('atime', '10:41')], 1) + cap('Danger is &gt;, not touch: it replaces the content.', '', 'red', y=150, h=34)]
def calls(hl, note, tone='blue'):
    items = [('bash: expand braces, find the program /usr/bin/touch', 'acc'), ('openat(“notes.txt”, O_CREAT): open, or create if missing', 'violet'),
             ('utimensat(): set atime and mtime to now', 'green'), ('kernel: update the inode on disk', 'blue')]
    o = ''.join(label_box(14, 14 + k * 34, 332, 28, [s], tn if k in hl else 'card', 8.4) for k, (s, tn) in enumerate(items))
    return o + t(180, 172, note, 8.8, tone, bold=True)
behind = [calls([0], 'The inode stores size, owner, times; no change yet.'),
          calls([1, 2, 3], 'File exists: opened, times set. Content not written.', 'green'),
          calls([3], 'Size is still 18 bytes: no write() call happened.', 'green'),
          calls([1, 3], 'O_CREAT made a new inode and a new name.', 'violet'),
          calls([3], '&gt; opens with O_TRUNC: old content is cut to 0.', 'red')]
two = anim_two('touch on an existing file vs a new one', 'What changes in the file’s record (inode)?',
               'A terminal and a file record: touch on an existing file changes only mtime and atime, the content stays; touch on a missing file creates a 0-byte file; echo with > replaces the content.',
               'The system calls behind touch: openat with O_CREAT, utimensat to set the times, and the inode on disk being updated; > opens with O_TRUNC.', see, behind,
               ['Riya’s notes: 18 bytes, last modified at 09:15.',
                '<code>touch notes.txt</code> sets the modification and access times to now.',
                'The content is exactly the same. Nothing was lost.',
                'On a missing name, touch creates an empty file.',
                'What really erases content is <code>&gt;</code>: <code>echo hi &gt; notes.txt</code> replaces it.'],
               ['Every file has an inode: a record with size, owner, permissions and three times.',
                'touch opens the file (creating it only if missing) and calls utimensat().',
                'touch never calls write(), so the size and the data blocks are unchanged.',
                'O_CREAT tells the kernel: create the file if it is not there.',
                'The shell opens the target of &gt; with O_TRUNC, which empties it before echo writes.'])

f1 = term(14, 14, 332, 100, ['$ mkdir dbda/data/raw', ('mkdir: cannot create directory ‘dbda/data/raw’:', 'err'), ('No such file or directory', 'err')], title='riya@laptop: ~/lab', size=7.6) + cap('dbda/ does not exist yet, so its child cannot be made.', '', 'red', y=150, h=34)
f2 = term(14, 14, 332, 100, ['$ mkdir -pv dbda/data/raw', ("mkdir: created directory 'dbda'", 'out'), ("mkdir: created directory 'dbda/data'", 'out'), ("mkdir: created directory 'dbda/data/raw'", 'acc')], title='riya@laptop: ~/lab', size=7.6) + cap('-p creates each missing level, top to bottom.', '', 'blue', y=150, h=34)
f3 = term(14, 14, 332, 100, ['$ mkdir -pv dbda/data/raw', ('(no output: everything exists)', 'dim'), '$ echo $?', ('0', 'acc')], title='riya@laptop: ~/lab', size=7.6) + cap('Run it again: no error, exit status 0.', '', 'green', y=150, h=34)
f4 = term(14, 14, 332, 100, ['$ mkdir -p dbda/{scripts,reports/{daily,monthly}}', '$ ls dbda dbda/reports', ('dbda: data reports scripts', 'out'), ('dbda/reports: daily monthly', 'acc')], title='riya@laptop: ~/lab', size=7.4) + cap('Nested braces: a whole tree in one command.', '', 'blue', y=150, h=34)
f5 = (t(180, 30, 'mkdir -p in one sentence', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• creates every missing parent', '• no error if the folder exists', '• safe to run again: idempotent', '• add -v to see what it made'])) + cap('Use -p in every script.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Building a project tree with mkdir -p',
              'Riya sets up the DBDA project. Outputs match real runs on our build machine.',
              'mkdir and mkdir -p', 'mkdir without -p fails on a missing parent; mkdir -pv creates three levels; running it again gives no error; nested braces build a tree.', [f1, f2, f3, f4, f5],
              ['Plain mkdir only creates the last part of the path.',
               '<code>-p</code> creates dbda, then dbda/data, then dbda/data/raw. <code>-v</code> reports each one.',
               'Second run: nothing to do, no error. Scripts can run it every time.',
               'Braces can be nested: <code>{scripts,reports/{daily,monthly}}</code>.',
               'Rule: in scripts, always <code>mkdir -p</code>.'],
              hid='scenario-mkdir')

g1 = term(14, 14, 332, 100, ['$ ls -A logs', ('app.log', 'out'), '$ rmdir logs', ('rmdir: failed to remove ‘logs’: Directory not empty', 'err')], title='riya@app-01', size=7.4) + cap('A folder with one file inside: rmdir refuses.', '', 'red', y=150, h=34)
g2 = label_box(30, 22, 300, 80, ['kernel: rmdir(“logs”)', 'entries inside: . .. app.log', '→ ENOTEMPTY (error 39)'], 'violet', 9) + cap('The refusal comes from the kernel itself.', '', 'violet', y=150, h=34)
g3 = term(14, 14, 332, 100, ['$ mv logs/app.log archive/', '$ rmdir -v logs', ("rmdir: removing directory, 'logs'", 'acc')], title='riya@app-01', size=7.4) + cap('Move the file out, then rmdir works.', '', 'green', y=150, h=34)
g4 = term(14, 14, 332, 100, ['$ ls -A cache', ('.lock', 'acc'), ('(hidden file!)', 'dim'), '$ rmdir cache', ('… Directory not empty', 'err')], title='riya@app-01', size=7.4) + cap('“Looks empty” with ls? Use ls -A: hidden files count.', '', 'red', y=150, h=34)
g5 = (t(180, 30, 'rmdir is your safety catch', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• deletes only empty folders', '• hidden files count: ls -A', '• -p: remove empty parents too', '• full folders: rm -r (Lesson 3.3)'])) + cap('It cannot lose your data.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Why won’t rmdir delete this folder?',
              'On a server, Riya cleans up old folders. The messages match real runs.',
              'rmdir and empty folders', 'rmdir fails on a folder with a file; the kernel returns ENOTEMPTY; after moving the file rmdir works; a hidden file also blocks it.', [g1, g2, g3, g4, g5],
              ['logs/ still contains app.log, so rmdir refuses.',
               'The <code>rmdir()</code> system call returns ENOTEMPTY: the kernel checks, not just the command.',
               'Move the file out; now the folder is empty and goes.',
               'Plain <code>ls</code> hides dotfiles. <code>ls -A</code> reveals the <code>.lock</code> that blocks it.',
               'That is why scripts use rmdir for cleanup: it is safe by design.'],
              hid='scenario-rmdir')

dx = dissect('Layer by layer: what happens when you type touch report_{01..03}.csv',
    'Open each layer from what you type down to the disk. Each has a real command and its output on our build machine.', [
    dict(key='shell', name='Bash', sub='expands the braces',
         why='Typing twelve names by hand is slow and error-prone.',
         how='Before running anything, bash expands <code>{01..03}</code> into three words. touch never sees the braces.',
         impl='Brace expansion in bash’s parser (it is the first expansion bash does, Lesson 12.4).', used='mkdir, touch, cp, echo: any command.',
         cmd='echo touch report_{01..03}.csv'),
    dict(key='find', name='PATH lookup', sub='which touch?',
         why='touch is a program file, not part of bash.',
         how='bash searches the folders in <code>$PATH</code> and finds <code>/usr/bin/touch</code>.',
         impl='GNU coreutils package, the same package as ls, cp, mkdir.', used='Every external command (Lesson 7.2).',
         cmd='type touch mkdir rmdir'),
    dict(key='calls', name='System calls', sub='ask the kernel',
         why='Programs may not write to the disk directly.',
         how='touch asks the kernel with <code>openat(O_CREAT)</code> and <code>utimensat()</code>; mkdir uses <code>mkdir()</code>; rmdir uses <code>rmdir()</code>.',
         impl='Linux kernel system call interface (Lesson 1.2).', used='Every file operation of every program.',
         cmd='touch a.csv; stat -c "%n  size=%s  type=%F" a.csv'),
    dict(key='vfs', name='VFS and folder entry', sub='a name in the folder',
         why='One interface for ext4, xfs, NTFS (WSL) and others.',
         how='The new name is added to the folder’s list of entries, pointing to the inode number.',
         impl='Virtual File System layer in the kernel.', used='Same commands on any file system.',
         cmd='touch a.csv; stat -c "name=%n  inode=%i" a.csv'),
    dict(key='inode', name='Inode', sub='the file’s record',
         why='Details must be stored somewhere other than the name.',
         how='Stores size, owner, permissions and the three times. An empty file has an inode but 0 data blocks.',
         impl='On disk, in the file system’s inode table (Lesson 10.1).', used='stat, ls -l, find -newer.',
         cmd='touch a.csv; stat -c "size=%s bytes  blocks=%b  links=%h" a.csv'),
    dict(key='dir', name='A new folder', sub='. and .. inside',
         why='Every folder must know itself and its parent.',
         how='mkdir creates the folder with two entries, <code>.</code> and <code>..</code>, so it starts with 2 links.',
         impl='Created by the file system during mkdir().', used='cd .., relative paths (Lesson 2.3).',
         cmd='mkdir d; stat -c "links=%h" d; ls -a d | tr "\\n" " "; echo'),
], hint='Top = what you type · bottom = what the disk stores. Click a layer.')

hd = hood('Under the hood: the system calls', 'This is the real list of file-related system calls that <code>touch notes.txt</code> made on our build machine. Look for the two lines that matter.',
          'touch notes.txt', '', 'openat\\(AT_FDCWD, "notes|utimensat|close\\(0',
          '<p><code>openat(…"notes.txt", O_WRONLY|O_CREAT…)</code> opens the file and creates it if it is missing. <code>utimensat(0, NULL, …)</code> sets both times to “now” (NULL means current time). There is no <code>write()</code>: touch never writes content. Compare <code>mkdir</code>, which is just one call, <code>mkdir("name", 0777)</code>; the umask then turns 0777 into 0755.</p>')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What touch, mkdir and rmdir really change</h2>
  <p>Left: what Riya sees. Right: what happens in the file’s record. Times are examples; sizes and behaviour match real runs.</p>
''' + two + '''
  <p>Two real-time scenarios: building a project tree, and a folder that will not go away.</p>
''' + s1 + s2 + dx + hd + qc('Why does <code>touch notes.txt</code> not lose the notes, while <code>echo hi &gt; notes.txt</code> does?', 'touch only opens the file and sets times; it never writes. The shell opens the target of <code>&gt;</code> with truncation, which empties the file before echo writes.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Creating files and folders at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ mkdir -p', 'prompt'), ('app/{src,test}', 'acc')], title='dev', size=6.4, step=12),
              '1. Project skeletons', 'Every new repository starts with the same folders. Teams keep a one-line <code>mkdir -p</code> (or a small script) so every project looks the same.', ['New repo', '*mkdir -p', 'same layout']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['_SUCCESS', '0 bytes'], 'green', 8.6), '2. Marker files in data pipelines',
    'Hadoop and Spark write an empty <code>_SUCCESS</code> file when a job completes. Schedulers wait for it before starting the next step.', ['Job ends', '*touch _SUCCESS', 'next job']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ mkdir -p', 'prompt'), ('bk/$(date +%F)', 'acc')], title='dba', size=6.4, step=12),
    '3. Dated backup folders', 'Nightly backup scripts make one folder per day. Old ones are later removed by date (Lesson 7.1, find -mtime).', ['Night', '*mkdir -p date', 'clean history']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['touch -d', '10 days ago'], 'amber', 8.6), '4. Testing clean-up jobs',
    'Testers create files with old dates to check “delete after 7 days” rules without waiting a week.', ['Test', '*touch -d', 'instant']) + '\n' + usecase(
    term(8, 14, 104, 62, [("$ cat > .env", 'prompt'), ("<<'EOF'", 'acc')], title='devops', size=6.4, step=12),
    '5. Config files from scripts', 'Deployment scripts, Dockerfiles and cloud-init write config files with here-documents, so a server is set up the same way every time.', ['Deploy', "*cat <<'EOF'", 'same config']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small commands that save a lot of clicks. All really run on our build machine.', [
    dict(level='b', title='A folder per weekday', scenario='A team keeps one folder per working day for meeting notes.',
         cmd='mkdir -p notes/{Mon,Tue,Wed,Thu,Fri} && ls notes',
         explain='A comma list inside braces; ls prints them in alphabetical order.'),
    dict(level='b', title='31 daily log files', scenario='A practice log for every day of the month.',
         cmd='touch day_{01..31}.log && ls day_* | wc -l',
         explain='<code>{01..31}</code> counts with zero padding; wc -l counts the names.'),
    dict(level='i', title='Make it and go into it', scenario='Create a folder and move into it in one line.',
         cmd='mkdir -p work/today && cd work/today && pwd',
         explain='<code>&amp;&amp;</code> runs the next command only if the previous one worked (Lesson 5.4).'),
    dict(level='i', title='Today’s folder, automatically', scenario='A folder named with today’s date, for a report.',
         cmd='mkdir -p "reports/$(date +%Y)" && ls reports',
         explain='<code>$(date +%Y)</code> is replaced by the year before mkdir runs. Quote it in case of spaces.'),
    dict(level='a', title='Empty file of exact size', scenario='Test an upload limit of 5 MB with a 6 MB file.',
         cmd='truncate -s 6M big.bin && stat -c "%n %s bytes" big.bin && du -h big.bin',
         explain='truncate makes a file of any size in an instant. <code>du</code> shows it uses almost no disk space: it is a <b>sparse</b> file of zeros.'),
    dict(level='a', title='Safe unique temp folder', scenario='A script needs a scratch folder nobody else can guess.',
         cmd='d=$(mktemp -d) && ls -ld "$d" | cut -c1-10 && rmdir "$d"',
         explain='mktemp picks a random name and creates the folder with <code>rwx------</code>. Clean up with rmdir at the end.'),
], extra=build_up('a full project skeleton', 'Riya’s DBDA project: folders, monthly report files, a CSV with a header and a README.',
    '', [
    ('mkdir -p dbda/{data,scripts,reports}', 'The three main folders.'),
    ('mkdir -p dbda/{data,scripts,reports} && touch dbda/reports/report_{01..12}.csv && ls dbda/reports | wc -l', 'Twelve report placeholders.'),
    ("mkdir -p dbda/data && printf 'id,name,marks\\n' > dbda/data/students.csv && cat dbda/data/students.csv", 'A CSV that already has its header row.'),
    ("mkdir -p dbda/{data,scripts,reports} && touch dbda/reports/report_{01..12}.csv && echo '# DBDA project' > dbda/README.md && find dbda -type d | sort", 'All together; find lists every folder (Lesson 7.1).'),
])) + which('Choosing the right command.', [
    ('One empty file', 'touch f.txt', 'Fast, no content.', 'echo > f.txt (adds an empty line, 1 byte).'),
    ('A file with one line', 'echo "text" > f.txt', 'Creates and writes.', 'Using > when you meant >>.'),
    ('Exact format, many rows', "printf '%s,%d\\n' …", 'Same in every shell.', 'echo with \\n (needs -e in bash).'),
    ('A multi-line config file', "cat > f <<'EOF'", 'Whole block at once.', 'Forgetting quotes: $VAR gets expanded.'),
    ('A nested folder path', 'mkdir -p a/b/c', 'Makes parents.', 'Plain mkdir → No such file or directory.'),
    ('Folder that may exist', 'mkdir -p dir', 'No error.', 'mkdir dir → File exists in scripts.'),
    ('Remove an empty folder', 'rmdir dir', 'Cannot lose data.', 'rm -r for a folder you think is empty.'),
    ('Only update the date', 'touch -c f', 'Never creates.', 'touch on a misspelled name makes a new file.'),
]) + keys('Shortcuts that make creating files faster.', [
    ('{a,b,c}', 'a list of names (brace expansion)', 'mkdir -p app/{src,tests}'),
    ('{01..12}', 'a padded sequence', 'touch m_{01..12}.csv'),
    ('Alt + .', 'insert the last argument of the previous command', 'mkdir -p a/b/c  then  cd Alt+.'),
    ('!$', 'the last argument of the previous command', 'mkdir reports && cd !$'),
    ('Tab', 'complete folder and file names', 'cd db⇥ → cd dbda/'),
    ('Ctrl + D', 'end the input of cat > file', 'cat > notes.txt … Ctrl+D'),
]) + scriptit('new-project.sh', 'Turn the lesson into a reusable script. It takes a project name, builds the layout and refuses to overwrite an existing project. (You will write scripts like this in Lesson 12.5.)',
'''#!/bin/bash
# new-project.sh NAME: create a standard project layout
name=${1:-demo}
if [ -e "$name" ]; then
  echo "error: $name already exists" >&2
  exit 1
fi
mkdir -p "$name"/{data/{raw,clean},scripts,reports,logs}
touch "$name"/reports/report_{01..12}.csv
printf '# %s\\nCreated on %s\\n' "$name" "2026-11-06" > "$name/README.md"
echo "created $name:"
find "$name" -type d | sort
cat "$name/README.md"''',
'<p>The real script would use <code>"$(date +%F)"</code> instead of the fixed date. Run it twice: the second time it stops with the error message instead of mixing two projects.</p>') + puzzle_answer('The notes are <b>safe</b>. On an existing file, <code>touch</code> does not write anything: it only changes the access and modification times to now (that is the “fingerprint” of touching it). The size, content and inode stay the same. What would destroy them is <code>&gt; notes.txt</code> or <code>echo … &gt; notes.txt</code>.') + qc('A script must create <code>/home/riya/app/logs</code> every time it starts, without failing if the folder is already there. What do you write?', '<code>mkdir -p /home/riya/app/logs</code>') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../02-file-system/03-absolute-and-relative-paths/">Lesson 2.3</a>: paths, <code>~</code>, <code>.</code> and <code>..</code>.') + '  <div class="story">', 1)
        + DECIDE.replace('<div class="dchart"', '<section class="part part--decide"><div class="dchart"',1) + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
