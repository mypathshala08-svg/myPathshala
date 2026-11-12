import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='06-text-processing', lesson='01-grep-searching-inside-files', n='6.1',
    module_label='Module 6 · Filters, text processing and regex',
    title='grep: searching inside files',
    desc='grep explained, then used in every field: -i -n -c -v -w -x -o -m, recursive search with -r -l -L --include --exclude-dir, context with -A -B -C, several patterns with -e -E -f -F -P, quiet mode -q and exit codes, grep in pipelines, binary files, ripgrep. Real outputs from Ubuntu, with corrections to common notes (-c counts lines, not occurrences).',
    og_desc='Search logs, code and configs with grep: every useful option, real outputs and the mistakes to avoid.',
    minutes=40, level='Beginner → Advanced',
    lead='grep shows you the lines of a file that contain what you are looking for. This lesson explains every option you will really use, then shows how admins, developers, DBAs, data engineers, DevOps, security and testers use grep every day.',
    chips=['grep by field', 'Real terminal screens', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A tiny log, then the grep options you use most
printf 'INFO start\\nERROR db down\\nINFO retry\\nerror disk full\\nFATAL crash\\n' > app.log
grep ERROR app.log              # exact case
grep -i -n error app.log        # any case + line numbers
grep -c -i error app.log        # how many lines
grep -v INFO app.log            # everything except INFO
grep -E 'ERROR|FATAL' app.log   # either word
grep -q FATAL app.log && echo 'alert: FATAL found'
"""

RUN = dict(
    heading='Six grep searches on one small log',
    intro='<p>Exact case, any case with line numbers, a count, an inverted search, two words at once and a quiet check.</p>',
    code=MAIN,
    anno=[
        ('grep -i -n error app.log        # any case + line numbers', 'Lines 2 and 4.'),
        ('grep -c -i error app.log        # how many lines', '2'),
        ('grep -v INFO app.log            # everything except INFO', 'Three lines.'),
        ("grep -q FATAL app.log && echo 'alert: FATAL found'", 'Exit code 0.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which lines does -v INFO print?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the two counts print? Then run.',
             code="echo 'ERROR ERROR' > t.log\ngrep -c ERROR t.log\ngrep -o ERROR t.log | wc -l\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should find lines with ERROR or FATAL but finds none. Fix it.',
             code="printf 'ERROR a\\nFATAL b\\n' > a.log\ngrep 'ERROR|FATAL' a.log\necho \"exit $?\"\n"),
        dict(label='4 · Your turn', hint='Print the line numbers of lines in /etc/passwd that end with bash.',
             code="grep -n 'bash$' /etc/passwd\n"),
        dict(label='5 · Challenge', hint='Show only the 4-digit numbers that appear in the text.',
             code="echo 'order 7781 paid, pin 12, year 2026' | grep -oE '\\b[0-9]{4}\\b'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real logs and big folders',
    intro='<p>These need system logs, sudo or a bigger project. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Errors in the system journal today', cmd="journalctl --since today | grep -i -E 'error|fail' | tail -n 5", output='Nov 06 10:12:01 laptop kernel: usb 1-2: device descriptor read/64, error -71\nNov 06 10:14:22 laptop systemd[1]: Failed to start Snap Daemon.', note='Typical. journalctl itself also has -g PATTERN.'),
        dict(title='2 · Failed SSH logins by IP', cmd="sudo grep 'Failed password' /var/log/auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -rn | head -3", output='     41 from 185.220.101.4\n      7 from 45.9.20.1\n      2 from 10.0.0.9', note='Typical on a public server.'),
        dict(title='3 · Search a big project, skipping junk', cmd="grep -rn --exclude-dir={.git,node_modules,venv} 'TODO' .", output='./src/api/orders.py:88:    # TODO: handle refunds\n./web/app.js:12:// TODO remove debug', note='Typical.'),
        dict(title='4 · ripgrep for comparison', cmd='sudo apt install ripgrep; rg -n TODO', output='src/api/orders.py\n88:    # TODO: handle refunds', note='Typical. rg skips .gitignore files automatically.'),
        dict(title='5 · grep version on our build machine', cmd='grep --version | head -1', output=pc('grep --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='grep results in variables',
    intro='<p>Step through a script that stores grep answers in variables.</p>',
    code='''printf 'INFO a\\nERROR b\\nERROR c\\n' > s.log
n=$(grep -c ERROR s.log)
first=$(grep -n -m 1 ERROR s.log)
grep -q FATAL s.log; rc=$?
echo "errors=$n first=[$first] fatal_rc=$rc"
''',
    notes={1: 'Sample :: Three lines.', 2: 'Count :: 2 lines.', 3: 'First :: Line 2.', 4: 'Quiet :: Not found → 1.', 5: 'Report :: All answers together.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an admin’s config audit, a developer’s code search, and a security check of an access log.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='Show only the active settings',
         problem='<p>Print the lines of a config file that are not comments and not empty, with line numbers.</p>',
         inp='a config with comments and blank lines',
         approach=['-v removes matching lines.', 'Two patterns: ^# and ^$.'],
         code='''printf '# server\\nport=8080\\n\\n# logging\\nlevel=info\\n#debug=true\\n' > app.conf
grep -n -v -e '^#' -e '^$' app.conf
''',
         notes={2: 'Filter :: Only port and level remain.'},
         tryit='Add a line with spaces before # and see what happens.'),
    dict(level='i', tag='Developer', title='Where is a function used?',
         problem='<p>List every Python file and line that calls <code>connect(</code>, but not files under tests/.</p>',
         inp='a small project',
         approach=['-rn for file:line.', '--include and --exclude-dir to focus.', '-F because ( is special.'],
         code='''mkdir -p proj/app proj/tests
printf 'db.connect(host)\\n' > proj/app/db.py
printf 'x = connect(1)\\n' > proj/app/api.py
printf 'mock.connect(2)\\n' > proj/tests/test_db.py
grep -rnF --include='*.py' --exclude-dir=tests 'connect(' proj
''',
         notes={5: 'Search :: Two app files; tests skipped.'},
         tryit='Remove --exclude-dir and compare.'),
    dict(level='a', tag='Security', title='Who is attacking /admin?',
         problem='<p>From a web log, list each IP that got 401 on /admin with its count, biggest first.</p>',
         inp='access log lines',
         approach=['grep twice to filter.', '-o to extract the IP.', 'sort | uniq -c | sort -rn.'],
         code='''printf '%s\\n' '185.220.101.4 "GET /admin" 401' '49.36.12.8 "GET /" 200' '185.220.101.4 "GET /admin" 401' '45.9.20.1 "GET /admin" 401' > access.log
grep '/admin' access.log | grep ' 401' | grep -oE '^[0-9.]+' | sort | uniq -c | sort -rn
''',
         notes={2: 'Pipeline :: Two attempts from 185.220.101.4.'},
         tryit='Count all 401s with grep -c.'),
]

QUIZ = mix([
    dict(q='What does grep -c ERROR file print?', options=['the number of ERROR occurrences', 'the number of lines containing ERROR', 'the line numbers', 'the first match'], answer=1,
         why='Lines. Use grep -o | wc -l for occurrences.'),
    dict(q='Which option shows lines that do NOT match?', options=['-n', '-v', '-x', '-c'], answer=1,
         why='-v inverts.'),
    dict(q="grep 'ERROR|FATAL' file (no -E) finds…", options=['ERROR or FATAL', 'the literal text ERROR|FATAL', 'an error', 'nothing ever'], answer=1,
         why='In basic regex | is literal; use -E or \\|.'),
    dict(q='Which shows only file names that contain a match?', options=['-o', '-l', '-h', '-n'], answer=1,
         why='-l = list files.'),
    dict(q='grep -w main matches which line?', options=['mainPage()', 'call main now', 'domain', 'remain'], answer=1,
         why='Whole word only.'),
    dict(q='What is grep’s exit code when nothing matches?', options=['0', '1', '2', '127'], answer=1,
         why='0 found, 1 not found, 2 error.'),
    dict(q='Which shows 2 lines before each match?', options=['-A 2', '-B 2', '-C 2', '-n 2'], answer=1,
         why='B = before.'),
    dict(q='You search for the IP 10.0.0.5 and also get 10x0y0z5. Which option fixes it?', options=['-i', '-F', '-v', '-r'], answer=1,
         why='-F: dots are literal.'),
])

REVISION = [
    "<code>grep 'pattern' file</code> or <code>cmd | grep</code>: prints matching lines; never changes files.",
    '<code>-i</code> case, <code>-n</code> numbers, <code>-c</code> count <b>lines</b>, <code>-v</code> invert, <code>-w</code> word, <code>-x</code> line, <code>-o</code> only match, <code>-m N</code> stop.',
    '<code>-r</code>/<code>-R</code> folders; <code>-l</code>/<code>-L</code> file names; <code>--include</code>, <code>--exclude-dir</code>; <code>-h</code>/<code>-H</code>.',
    '<code>-A</code>/<code>-B</code>/<code>-C N</code>: context lines.',
    "Several patterns: <code>-e a -e b</code>, <code>-E 'a|b'</code>, <code>-f list</code>; <code>-F</code> literal text; <code>-P</code> Perl regex.",
    '<code>-q</code> + exit code: 0 found, 1 not found, 2 error.',
    'Quote patterns; count occurrences with <code>grep -o | wc -l</code>; pgrep instead of ps | grep.',
    '“binary file matches” → <code>-a</code> or strings; speed → <code>LC_ALL=C</code>, rg.',
]

FAQ = [
    ('What does grep stand for?', 'g/re/p: global / regular expression / print, a command of the ed editor.'),
    ('How do I search for a word in all files of a folder?', 'grep -rn word folder/ (add -i for any case, --include="*.ext" to limit files, -l for names only).'),
    ('How do I count how many times a word appears?', 'grep -o word file | wc -l. grep -c counts matching lines, not occurrences.'),
    ('How do I search for two words at once?', "grep -E 'word1|word2' file, or grep -e word1 -e word2 file."),
    ('How do I show lines that do not contain a word?', 'grep -v word file.'),
    ('How do I see lines around a match?', 'grep -C 2 word file (or -A for after, -B for before).'),
    ('Why does grep say “binary file matches”?', 'The file contains NUL bytes. Use grep -a to treat it as text, or strings file | grep word.'),
]

PRACTICE_INTRO = 'Small grep tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Find root', stmt='Print the line for the user root in /etc/passwd.', inp='/etc/passwd',
         code="grep '^root:' /etc/passwd\n", explain='^ anchors at the start; the colon ends the name.'),
    dict(level='easy', title='Any case', stmt='Count lines containing “linux” in any case.', inp='three lines',
         code="printf 'Linux\\nLINUX rocks\\nwindows\\n' > os.txt\ngrep -ci linux os.txt\n", explain='-c and -i together.'),
    dict(level='easy', title='Without comments', stmt='Print lines of a file that do not start with #.', inp='a small config',
         code="printf '#a\\nx=1\\n#b\\ny=2\\n' > c.conf\ngrep -v '^#' c.conf\n", explain='-v inverts.'),
    dict(level='medium', title='Whole word', stmt='Print lines with the word “cat” but not “catalog”.', inp='three lines',
         code="printf 'my cat\\ncatalog\\na cat sat\\n' > w.txt\ngrep -w cat w.txt\n", explain='-w needs word boundaries.'),
    dict(level='medium', title='Extract numbers', stmt='Print every number in the text, one per line.', inp='a sentence',
         code="echo 'room 12, floor 3, pin 4401' | grep -oE '[0-9]+'\n", explain='-o prints each match.'),
    dict(level='medium', title='Context', stmt='Show the line with FAIL and the line after it.', inp='a test log',
         code="printf 'test1 ok\\ntest2 FAIL\\n  expected 3 got 4\\ntest3 ok\\n' > t.log\ngrep -A 1 FAIL t.log\n", explain='-A 1 = one line after.'),
    dict(level='business', title='Files to fix', stmt='List the files under conf/ that still contain http:// (not https).', inp='three files',
         code="mkdir -p conf; echo 'url=http://a' > conf/a.cfg; echo 'url=https://b' > conf/b.cfg; echo 'x=http://c' > conf/c.cfg\ngrep -rl 'http://' conf | sort\n", explain='-l lists file names.'),
    dict(level='business', title='Status counts', stmt='Count lines with 5xx status codes in a mini web log.', inp='four lines',
         code="printf '%s\\n' 'GET / 200' 'GET /a 500' 'GET /b 503' 'GET /c 404' > w.log\ngrep -cE ' 5[0-9]{2}$' w.log\n", explain='Anchored 3-digit code starting with 5.'),
]

SCN_INTRO = 'Interview questions about grep, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Find all lines with ERROR in a log, with line numbers, ignoring case.”',
        'Asked in almost every Linux round.',
        'do you know the everyday options?',
        '''<ul>
          <li><code>grep -in error app.log</code>.</li>
          <li>Count: <code>grep -ic error app.log</code> (lines); occurrences: <code>grep -oi error app.log | wc -l</code>.</li>
          <li>Whole folder: <code>grep -rin error /var/log/app/</code>.</li>
        </ul>''', 'opening the log in vi and searching by hand.') +
    scn('Operations · on-call', 'Junior', 'What happened before the crash?',
        'A service crashed at 03:12. You have SSH and a 5 GB log.',
        'can you find context quickly?',
        '''<ol>
          <li><code>grep -n '03:1[0-2]' app.log | grep -iE 'error|fatal|killed'</code> to narrow to the time.</li>
          <li><code>grep -n -B 20 -m 1 FATAL app.log</code> for the lead-up.</li>
          <li>Check the kernel: <code>dmesg | grep -i oom</code> (out-of-memory killer).</li>
        </ol>''', 'less + scrolling through gigabytes.') +
    scn('Product team · developer', 'Mid-level', 'Rename a deprecated function safely',
        '<code>getUserData()</code> must be replaced everywhere, but <code>getUserDataV2()</code> must stay.',
        'do you search precisely before changing?',
        '''<ul>
          <li><code>grep -rnw --include='*.java' 'getUserData' src/</code>: whole word, so V2 is not listed.</li>
          <li><code>grep -rlw …</code> gives the file list for the change (sed -i in Lesson 6.4, or the IDE).</li>
          <li>Afterwards the same grep must return nothing (exit code 1) in CI.</li>
        </ul>''', 'a plain search that also hits getUserDataV2.') +
    scn('Security team', 'Senior', 'Secrets were pushed to a repository',
        'A key was committed months ago. You must find all secrets in the code and its history.',
        'do you know grep’s place and its limits?',
        '''<ul>
          <li>Current files: <code>grep -rnE -i '(api[_-]?key|secret|password)\\s*[=:]' --exclude-dir=.git .</code></li>
          <li>History: <code>git grep -E pattern $(git rev-list --all)</code> or a dedicated scanner (gitleaks).</li>
          <li>Rotate every key found; deleting the line does not remove it from history.</li>
        </ul>''', 'only grepping the latest version.')
) + interview([
    ('What does grep -v do?', 'Prints lines that do NOT match.'),
    ('Difference between grep -c and grep -o | wc -l?', 'Lines vs occurrences.'),
    ('How do you search recursively?', 'grep -r (or -R to follow symlinks), often with -n, -l, --include.'),
    ('What is the difference between grep, grep -E and grep -F?', 'Basic regex, extended regex (| + ? () {} special), fixed strings (nothing special).'),
    ('How do you show lines before and after a match?', '-B N, -A N, -C N.'),
    ('What does grep return when nothing matches?', 'Exit status 1 (0 found, 2 error).'),
    ('How do you avoid ps aux | grep matching itself?', "pgrep, or grep '[p]attern'."),
], [
    ('RHCSA (EX200)', '“Use grep and regular expressions to analyze text”: an explicit exam objective.'),
    ('LFCS', 'Essential commands: search for files and text, use grep with regex.'),
    ('CompTIA Linux+', 'Text search with grep, egrep, fgrep and regular expressions.'),
]) + distro('grep is everywhere; options differ between GNU and BSD.', [
    ('-r -i -n -c -v -w -o -A -B -C', 'GNU grep', 'GNU grep', 'BSD grep: same', 'WSL GNU; Git Bash GNU'),
    ('-P (Perl regex)', 'yes', 'yes', 'no (use -E or brew grep)', 'WSL yes; Git Bash yes'),
    ('egrep / fgrep', 'warn: use grep -E / -F', 'same', 'still work', 'warn'),
    ('--include / --exclude-dir', 'yes', 'yes', 'yes', 'yes'),
    ('Colour by default', 'alias in ~/.bashrc', 'alias', 'export GREP_OPTIONS no; use --color', 'yes'),
    ('ripgrep (rg)', 'apt install ripgrep', 'dnf install ripgrep', 'brew install ripgrep', 'WSL apt; Windows: winget'),
]) + teaser('6.2', 'Riya’s manager wants, from employees.csv: the departments sorted by total headcount, the 3 highest salaries, and the city column in capital letters. No spreadsheet allowed. Which five small commands from the next lesson do it?')

CHEATSHEET = cheatsheet('grep', [
    ('Basics', [("grep 'x' f", 'matching lines'), ('-i', 'ignore case'), ('-n', 'line numbers'), ('-c', 'count lines'), ('-v', 'invert')]),
    ('Precision', [('-w', 'whole word'), ('-x', 'whole line'), ('-o', 'only the match'), ('-m N', 'stop after N'), ('-F', 'literal text')]),
    ('Folders', [('-rn x dir/', 'recursive'), ('-l / -L', 'files with / without'), ("--include='*.py'", 'only these'), ('--exclude-dir=.git', 'skip'), ('-h / -s', 'no names / no errors')]),
    ('Context', [('-A N', 'after'), ('-B N', 'before'), ('-C N', 'around'), ('-n with context', ': match, - context'), ('--', 'group separator')]),
    ('Patterns & scripts', [('-e a -e b', 'several'), ("-E 'a|b'", 'extended'), ('-f list', 'from a file'), ('-q', 'exit code only'), ('0 / 1 / 2', 'found / not / error')]),
])

MINDMAP = mindmap('grep', [
    ('Match', 'blue', ['-i case', '-w word, -x line', '-v invert']),
    ('Show', 'green', ['-n numbers', '-c count lines', '-o only match']),
    ('Where', 'amber', ['files, | input', '-r, --include', '-l / -L names']),
    ('Context', 'violet', ['-A after', '-B before', '-C around']),
    ('Patterns', 'red', ["-E 'a|b'", '-F literal', '-f list, -P']),
    ('Scripts', 'acc', ['-q exit code', '0 / 1 / 2', 'pgrep not ps|grep']),
])

LAB = lab('investigate an outage with grep', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab61 && cd ~/lab61 && rm -rf *
printf '09:00 INFO start\\n09:02 ERROR db refused\\n09:03 INFO retry\\n09:04 error timeout\\n09:05 FATAL oom\\n' > app.log
mkdir -p src; echo '# TODO fix' > src/a.py; echo 'print(1)' > src/b.py; echo '// TODO test' > src/c.js''',
    tasks=['Write the number of lines containing “error” in any case into <code>errors.txt</code>.',
           'Write every line that is NOT an INFO line into <code>problems.txt</code>.',
           'Write the names of the files under <code>src/</code> that contain TODO (one per line, sorted) into <code>todo_files.txt</code>.',
           'Write the line just before the FATAL line into <code>before.txt</code> (only that line).'],
    solution='''grep -ci error app.log > errors.txt
grep -v INFO app.log > problems.txt
grep -rl TODO src | sort > todo_files.txt
grep -B 1 FATAL app.log | head -n 1 > before.txt''',
    check='''cd ~/lab61
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 error count"     '[ "$(cat errors.txt 2>/dev/null)" = 2 ]'
ok "2 non-INFO lines"  '[ "$(wc -l < problems.txt 2>/dev/null)" = 3 ] && ! grep -q INFO problems.txt'
ok "3 TODO files"      '[ "$(cat todo_files.txt 2>/dev/null)" = "$(printf "src/a.py\\nsrc/c.js")" ]'
ok "4 line before"     '[ "$(cat before.txt 2>/dev/null)" = "09:04 error timeout" ]' ''')
