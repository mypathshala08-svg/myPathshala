import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='07-finding-files', lesson='01-find-search-by-name-type-size-time-and-run-exec', n='7.1',
    module_label='Module 7 · Finding files and commands',
    title='find: search by name, type, size, time and run -exec',
    desc='find explained, then used in every field: -name -iname -path -regex, -type, -size (and its rounding), -empty, -mtime -mmin -atime -ctime -newer -newermt, -perm (exact, -, /), -user -group -nouser, ! -o \\( \\), -maxdepth, -prune, -xdev, and actions -print -ls -printf -exec {} \\; and +, -ok, -delete, -print0 with xargs. Real outputs, with the unquoted-pattern, -size -1k and -perm mistakes from common notes explained.',
    og_desc='Find files by name, size, age, permission and owner, and act on them safely with -exec and -delete, with real outputs.',
    minutes=42, level='Beginner → Advanced',
    lead='find walks a folder tree and finds files by name, size, age, permission or owner, then acts on them. This lesson explains every test and action you will use, and how admins, developers, DBAs, DevOps, security and testers use find every day.',
    chips=['find by field', 'Safe -exec and -delete', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A tiny tree, then find from simple to action
mkdir -p demo/logs demo/src; echo x > demo/src/a.py; echo y > demo/src/B.PY
head -c 2M /dev/zero > demo/logs/big.log; echo ok > demo/logs/small.log
touch -d '40 days ago' demo/logs/small.log
find demo -name '*.py'                 # by name
find demo -iname '*.py'                # any case
find demo -type f -size +1M            # big files
find demo -type f -mtime +30           # old files
find demo -name '*.log' -exec ls -s {} +
"""

RUN = dict(
    heading='Name, size, age and an action',
    intro='<p>Search a small tree by name, case-insensitive name, size and age, then list the logs with their sizes.</p>',
    code=MAIN,
    anno=[
        ("find demo -iname '*.py'                # any case", 'Both a.py and B.PY.'),
        ('find demo -type f -size +1M            # big files', 'big.log'),
        ('find demo -type f -mtime +30           # old files', 'small.log'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which file is old?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which files does each command list? Then run.',
             code="mkdir -p t; echo ab > t/two; : > t/zero\nfind t -size -1k\necho ---\nfind t -size -1024c\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this finds only one file. Quote the pattern.',
             code="mkdir -p q/s; touch q/a.py q/s/b.py; cd q\nfind . -name *.py\n"),
        dict(label='4 · Your turn', hint='List only the folders under /etc/apt, at most 1 level deep.',
             code="find /etc/apt -maxdepth 1 -type d\n"),
        dict(label='5 · Challenge', hint='Delete .tmp files older than 7 days (list first, then delete, then check).',
             code="mkdir -p c; touch c/new.tmp; touch -d '9 days ago' c/old.tmp\nfind c -name '*.tmp' -mtime +7\nfind c -name '*.tmp' -mtime +7 -delete\nls c\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the whole system',
    intro='<p>These search system folders and need sudo. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · The 5 biggest files on the root file system', cmd="sudo find / -xdev -type f -printf '%s %p\\n' 2>/dev/null | sort -rn | head -5 | numfmt --to=iec --field=1", output='2.1G /var/lib/snapd/cache/abc\n1.3G /swapfile\n812M /var/backups/db.sql.gz', note='Typical.'),
        dict(title='2 · Files changed in /etc in the last day', cmd='sudo find /etc -type f -mtime -1', output='/etc/ssh/sshd_config\n/etc/hosts', note='Typical: what did that update change?'),
        dict(title='3 · SUID programs', cmd='sudo find / -xdev -perm -4000 -type f 2>/dev/null', output='/usr/bin/passwd\n/usr/bin/sudo\n/usr/bin/mount\n/usr/bin/su', note='Typical (Lesson 9.4).'),
        dict(title='4 · Files left by a deleted user', cmd='sudo find / -xdev -nouser 2>/dev/null | head', output='/home/olduser/notes.txt', note='Typical.'),
        dict(title='5 · find version on our build machine', cmd='find --version | head -1', output=pc('find --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='find results in variables',
    intro='<p>Step through a script that counts and measures files with find.</p>',
    code='''mkdir -p w; head -c 5000 /dev/zero > w/a.log; head -c 300 /dev/zero > w/b.log; echo x > w/c.txt
n=$(find w -name '*.log' | wc -l)
big=$(find w -size +4k)
bytes=$(find w -name '*.log' -printf '%s\\n' | paste -sd+ | bc)
echo "logs=$n big=$big bytes=$bytes"
''',
    notes={1: 'Files :: Two logs, one text file.', 2: 'Count :: 2 logs.', 3: 'Size :: Only a.log is above 4k.', 4: 'Total :: 5300 bytes.', 5: 'Report.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a DBA’s retention, a security audit and a developer’s clean-up.'
EXAMPLES = [
    dict(level='b', tag='DBA', title='Keep 7 days of dumps',
         problem='<p>List and then delete database dumps older than 7 days.</p>',
         inp='four dumps with different dates',
         approach=['-name for dumps, -mtime +7.', 'List, then -delete.'],
         code='''mkdir -p dumps; for d in 1 3 10 20; do touch -d "$d days ago" dumps/db_$d.sql.gz; done
find dumps -name 'db_*.sql.gz' -mtime +7
find dumps -name 'db_*.sql.gz' -mtime +7 -delete
ls dumps
''',
         notes={2: 'List :: 10 and 20 days old.', 3: 'Delete.', 4: 'Two recent dumps remain.'},
         tryit='Change the rule to 2 days.'),
    dict(level='i', tag='Security', title='Risky permissions in a web folder',
         problem='<p>Find world-writable files and fix them in one command.</p>',
         inp='a web folder with mixed permissions',
         approach=['-perm /o+w', '-exec chmod o-w {} +'],
         code='''mkdir -p www; touch www/index.html www/upload.php www/config.php; chmod 666 www/upload.php www/config.php
find www -type f -perm /o+w
find www -type f -perm /o+w -exec chmod o-w {} +
find www -type f -perm /o+w | wc -l
''',
         notes={2: 'Found :: Two writable by everyone.', 3: 'Fix.', 4: 'Check :: 0 left.'},
         tryit='Also list SUID files with -perm -4000.'),
    dict(level='a', tag='Developer', title='Clean build output, keep sources',
         problem='<p>Delete *.class and *.pyc files and empty folders, but never touch .git.</p>',
         inp='a small project',
         approach=['Prune .git.', 'OR in brackets, -delete.', 'Then empty dirs.'],
         code='''mkdir -p app/.git app/build/x app/src; touch app/.git/HEAD.pyc app/build/x/A.class app/src/m.py app/src/m.pyc
find app -path app/.git -prune -o -type f \\( -name '*.class' -o -name '*.pyc' \\) -print -delete
find app -path app/.git -prune -o -type d -empty -print -delete
find app -type f | sort
''',
         notes={2: 'Delete :: build files only; .git untouched.', 3: 'Empty folders removed.', 4: 'What is left.'},
         tryit='Remove -prune and see .git/HEAD.pyc deleted too.'),
]

QUIZ = mix([
    dict(q="Why quote '*.log' in find -name?", options=['for speed', 'so the shell does not expand it before find runs', 'find needs quotes', 'to ignore case'], answer=1,
         why='Unquoted globs are expanded by the shell in the current folder.'),
    dict(q='find . -mtime +30 finds files…', options=['changed in the last 30 days', 'not changed for more than 30 days', 'exactly 30 days old', 'created 30 days ago'], answer=1,
         why='+ = more than.'),
    dict(q='Which finds files bigger than 100 MB?', options=['-size 100M', '-size +100M', '-size -100M', '-big 100M'], answer=1,
         why='+ bigger, - smaller.'),
    dict(q='find . -size -1k lists a 2-byte file?', options=['yes', 'no: sizes are rounded up to 1k', 'only with -type f', 'error'], answer=1,
         why='Use -size -1024c.'),
    dict(q="What does {} mean in -exec?", options=['all files', 'the current path', 'the folder', 'nothing'], answer=1,
         why='Replaced by each match.'),
    dict(q='Difference between -exec cmd {} \\; and -exec cmd {} +?', options=['none', '\\; runs once per file, + runs once with many files', '+ asks first', '\\; is faster'], answer=1,
         why='+ batches like xargs.'),
    dict(q='Which skips the .git folder?', options=['-name .git -delete', "-path ./.git -prune -o … -print", '-not .git', '-maxdepth .git'], answer=1,
         why='-prune stops descending.'),
    dict(q='Which finds files whose owner no longer exists?', options=['-user none', '-nouser', '-orphan', '-perm 000'], answer=1,
         why='-nouser.'),
])

REVISION = [
    "<code>find PATH TESTS ACTIONS</code>; default action -print. Quote patterns: <code>-name '*.log'</code>.",
    '<code>-name -iname -path -regex</code>; <code>-type f d l</code>; <code>-maxdepth N</code>.',
    '<code>-size +100M / -10k</code> (rounded up: use <code>c</code> for bytes); <code>-empty</code>.',
    '<code>-mtime -1 / +30</code>, <code>-mmin -15</code>, <code>-newer f</code>, <code>-newermt DATE</code>; m = modified, c = inode changed, a = accessed.',
    '<code>-perm 0777</code> exact, <code>-perm -4000</code> all bits, <code>/o+w</code> any; <code>-user -group -nouser</code>.',
    '<code>! -o \\( \\)</code>; AND is implicit; <code>-path X -prune -o … -print</code>; <code>-xdev</code>.',
    '<code>-exec cmd {} \\;</code> / <code>+</code>, <code>-ok</code>, <code>-delete</code> (last!), <code>-print0 | xargs -0</code>, <code>-printf</code>, <code>-ls</code>.',
    'List first, act second. 2&gt;/dev/null hides Permission denied.',
]

FAQ = [
    ('How do I find a file by name in Linux?', "find /start/path -name 'file.txt' (use -iname to ignore case, quote wildcards)."),
    ('How do I find large files?', 'find / -xdev -type f -size +100M (add -exec ls -lh {} + to see sizes).'),
    ('How do I find files modified in the last 24 hours?', 'find . -mtime -1 (or -mmin -60 for the last hour).'),
    ('How do I delete files older than 30 days?', 'List with find DIR -type f -mtime +30, then run the same command with -delete.'),
    ('What is the difference between -exec \\; and -exec +?', '\\; runs the command once per file; + passes many files to one command, which is much faster.'),
    ('How do I exclude a directory from find?', "find . -path ./node_modules -prune -o -type f -print."),
    ('Why do I get Permission denied with find?', 'You cannot read some folders as a normal user; use sudo or hide errors with 2>/dev/null.'),
]

PRACTICE_INTRO = 'Small find tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='By name', stmt='Find hosts under /etc (only at the first level).', inp='/etc',
         code="find /etc -maxdepth 1 -name hosts\n", explain='-maxdepth 1 + -name.'),
    dict(level='easy', title='Only folders', stmt='List the folders in a small tree.', inp='a tree',
         code="mkdir -p p/a/b p/c; touch p/f\nfind p -type d | sort\n", explain='-type d.'),
    dict(level='easy', title='Any case', stmt='Find report.pdf in any case.', inp='two files',
         code="mkdir -p r; touch r/Report.PDF r/report.pdf\nfind r -iname 'report.pdf' | sort\n", explain='-iname.'),
    dict(level='medium', title='Big files', stmt='Files bigger than 1 MiB.', inp='three files',
         code="mkdir -p s; head -c 2M /dev/zero > s/a; head -c 10K /dev/zero > s/b; head -c 1M /dev/zero > s/c\nfind s -type f -size +1M\n", explain='Exactly 1M is not more than 1M.'),
    dict(level='medium', title='Old files', stmt='Files not changed for 30+ days.', inp='three files',
         code="mkdir -p o; touch o/new; touch -d '40 days ago' o/old1 o/old2\nfind o -type f -mtime +30 | sort\n", explain='+30.'),
    dict(level='medium', title='Two extensions', stmt='Find .jpg or .png files.', inp='four files',
         code="mkdir -p i; touch i/a.jpg i/b.png i/c.gif i/d.JPG\nfind i \\( -name '*.jpg' -o -name '*.png' \\) | sort\n", explain='OR in brackets (case matters: d.JPG is not found; use -iname).'),
    dict(level='business', title='Count by type', stmt='Count files and folders separately.', inp='a tree',
         code="mkdir -p k/x/y; touch k/1 k/x/2 k/x/y/3\necho \"files $(find k -type f | wc -l), dirs $(find k -type d | wc -l)\"\n", explain='Two finds.'),
    dict(level='business', title='Fix permissions', stmt='Make every .sh file executable and show the result.', inp='two scripts',
         code="mkdir -p sh; touch sh/a.sh sh/b.sh\nfind sh -name '*.sh' -exec chmod +x {} +\nfind sh -name '*.sh' -perm /u+x | sort\n", explain='-exec … + then a check.'),
]

SCN_INTRO = 'Interview questions about find, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Find all .log files under /var/log.”',
        'Asked in almost every Linux interview.',
        'do you know the syntax and quoting?',
        '''<ul>
          <li><code>find /var/log -type f -name '*.log'</code>.</li>
          <li>Explain why the pattern is quoted.</li>
          <li>Bigger than 100 MB: add <code>-size +100M</code>.</li>
        </ul>''', 'find *.log /var/log (wrong order, unquoted).') +
    scn('Operations', 'Junior', 'Disk full at 2 a.m.',
        'The root file system is 99% full and a service has stopped.',
        'can you find space quickly and safely?',
        '''<ol>
          <li><code>df -h</code>, then <code>du -xh --max-depth=1 / | sort -rh | head</code> (Lesson 15.4).</li>
          <li><code>find /var -xdev -type f -size +500M -exec ls -lh {} +</code>.</li>
          <li>Old rotated logs or dumps: list with -mtime, then -delete; check deleted-but-open files with lsof +L1.</li>
        </ol>''', 'rm -rf on a guess.') +
    scn('Security team', 'Mid-level', 'After an intrusion',
        'A server was compromised yesterday around 14:00.',
        'can you find what changed?',
        '''<ul>
          <li><code>sudo find / -xdev -newermt '2026-11-05 13:30' ! -newermt '2026-11-05 16:00' -type f</code>.</li>
          <li>SUID: <code>-perm -4000</code>; world-writable in /etc, /usr; files in /tmp and /dev/shm.</li>
          <li>Compare with package checksums (debsums) and a known baseline (comm, Lesson 6.3).</li>
        </ul>''', 'trusting ls on a compromised system without checking.') +
    scn('Platform', 'Senior', 'A clean-up job deleted production data',
        'A cron job <code>find /data -name *.tmp -o -name *.bak -mtime +7 -delete</code> removed recent backups.',
        'do you understand find’s operator precedence and quoting?',
        '''<ul>
          <li>Unquoted globs may expand; without \\( \\) the -mtime and -delete apply only to the second test.</li>
          <li>Correct: <code>find /data \\( -name '*.tmp' -o -name '*.bak' \\) -mtime +7 -delete</code>.</li>
          <li>Process: dry run in CI, log the list, limit with -maxdepth/-xdev, alert on unusual counts.</li>
        </ul>''', '“find is dangerous, never use -delete” (the fix is discipline, not avoidance).')
) + interview([
    ('How do you find files by name ignoring case?', "find . -iname 'name*'."),
    ('How do you find files larger than 1 GB?', 'find / -xdev -size +1G.'),
    ('What do -mtime +7 and -mtime -7 mean?', 'Modified more than 7 days ago; less than 7 days ago.'),
    ('How do you run a command on every file found?', '-exec cmd {} \\; (or + to batch), or -print0 | xargs -0.'),
    ('How do you exclude a directory?', '-path DIR -prune -o … -print.'),
    ('How do you find SUID files?', 'find / -perm -4000 -type f.'),
    ('What is the difference between find and locate?', 'find walks the file system live; locate searches a prebuilt index (fast, may be stale).'),
], [
    ('RHCSA (EX200)', '“Locate, read, and use system documentation” and “Use … find” for files by criteria; find is used in many tasks.'),
    ('LFCS', 'Essential commands: search for files with find.'),
    ('CompTIA Linux+', 'File search: find with -name, -type, -size, -mtime, -perm, -exec.'),
]) + distro('GNU find on Linux; BSD find on macOS.', [
    ('-name -type -size -mtime -exec', 'GNU findutils', 'GNU', 'BSD: same', 'GNU'),
    ('-printf, -newermt, -iname', 'GNU', 'GNU', 'no -printf; -newermt yes', 'GNU'),
    ('-delete', 'yes', 'yes', 'yes', 'yes'),
    ('find without a path', 'uses .', 'uses .', 'path required', 'uses .'),
    ('-regextype', 'GNU', 'GNU', '-E for ERE', 'GNU'),
    ('Windows names', '-', '-', '-', 'Git Bash: find is GNU find; cmd.exe has a different find'),
]) + teaser('7.2', 'find / -name nginx.conf takes 40 seconds on a big server. Riya’s colleague finds it in 0.1 seconds. And when Riya types python, which python actually runs: /usr/bin/python3, a virtualenv, or an alias? Which four commands answer those questions?')

CHEATSHEET = cheatsheet('find', [
    ('Name & type', [("-name '*.log'", 'glob, quoted'), ("-iname '*.py'", 'any case'), ("-path '*/tests/*'", 'whole path'), ('-type f / d / l', 'kind'), ('-maxdepth 1', 'depth')]),
    ('Size', [('-size +100M', 'bigger'), ('-size -10k', 'smaller (rounded)'), ('-size -1024c', 'bytes'), ('-empty', 'empty'), ("-printf '%s %p\\n'", 'size + path')]),
    ('Time', [('-mtime -1 / +30', 'days'), ('-mmin -15', 'minutes'), ('-newer f', 'than a file'), ('-newermt DATE', 'than a date'), ('-atime / -ctime', 'read / inode')]),
    ('Owner & perms', [('-user riya', 'owner'), ('-nouser', 'orphans'), ('-perm 0777', 'exact'), ('-perm -4000', 'SUID'), ('-perm /o+w', 'world-writable')]),
    ('Logic & actions', [("\\( A -o B \\)", 'or'), ('! A', 'not'), ('-path X -prune -o … -print', 'skip'), ('-exec cmd {} +', 'run'), ('-delete (last)', 'remove')]),
])

MINDMAP = mindmap('find', [
    ('Name', 'blue', ["-name '*.x'", '-iname, -path', '-type f d l']),
    ('Size', 'green', ['+100M -10k', 'rounded up', '-empty']),
    ('Time', 'amber', ['-mtime -mmin', '-newer', 'm c a times']),
    ('Owner', 'violet', ['-user -group', '-nouser', '-perm - /']),
    ('Logic', 'acc', ['! -o \\( \\)', '-prune', '-maxdepth -xdev']),
    ('Act', 'red', ['-exec {} \\; +', '-ok -delete', '-print0 | xargs']),
])

LAB = lab('clean up a project with find', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab71 && cd ~/lab71 && rm -rf proj *.txt
mkdir -p proj/src proj/logs proj/tmp proj/empty
echo 'print(1)' > proj/src/a.py; echo 'x=1' > proj/src/B.PY; head -c 2M /dev/zero > proj/logs/big.log; echo ok > proj/logs/small.log
touch proj/tmp/new.tmp; touch -d '20 days ago' proj/tmp/old1.tmp proj/tmp/old2.tmp; chmod 777 proj/src/a.py''',
    tasks=['Write the paths of all Python files (any case of .py), sorted, into <code>py.txt</code>.',
           'Write the path of every file bigger than 1 MiB into <code>big.txt</code>.',
           'Delete every .tmp file older than 7 days (keep new.tmp).',
           'Remove write permission for “others” from every world-writable file under proj.'],
    solution='''find proj -iname '*.py' | sort > py.txt
find proj -type f -size +1M > big.txt
find proj -name '*.tmp' -mtime +7 -delete
find proj -type f -perm /o+w -exec chmod o-w {} +''',
    check='''cd ~/lab71
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 python files"  '[ "$(cat py.txt 2>/dev/null)" = "$(printf "proj/src/B.PY\\nproj/src/a.py")" ]'
ok "2 big files"     '[ "$(cat big.txt 2>/dev/null)" = proj/logs/big.log ]'
ok "3 old tmp gone"  '[ "$(find proj -name "*.tmp" | wc -l)" = 1 ] && [ -e proj/tmp/new.tmp ]'
ok "4 no o+w"        '[ -z "$(find proj -type f -perm /o+w)" ] && [ -e proj/src/a.py ]' ''')
