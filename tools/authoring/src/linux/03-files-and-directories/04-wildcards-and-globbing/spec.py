import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='03-files-and-directories', lesson='04-wildcards-and-globbing', n='3.4',
    module_label='Module 3 · Working with files and directories',
    title='Wildcards and globbing: *, ?, [ ] and brace expansion',
    desc='Select files by pattern with *, ? and [ ] (ranges, [!…], [[:digit:]]), generate names with brace expansion ({a,b}, {01..12}, steps), and handle no-match, hidden files, quotes and spaces. Advanced: bash expansion order, nullglob, failglob, dotglob, nocaseglob, globstar ** and extglob !(…). Each pattern explained, then used by data engineers, admins, developers, QA, security and DevOps, with real outputs.',
    og_desc='500 files, three needed: one pattern picks exactly the right ones. *, ?, [ ], braces, ** and !(…) with real outputs.',
    minutes=36, level='Beginner → Advanced',
    lead='Riya must copy exactly the January–March 2026 reports out of 500 files. This lesson explains every wildcard and brace pattern, who expands them (bash, not the command), the surprises (no match, hidden files, quotes), and how each IT role uses patterns every day.',
    chips=['Patterns by field', 'Which pattern when?', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = '''# Test patterns with echo first
touch report_2025_{01..12}.csv report_2026_{01..06}.csv notes.txt data1.log data10.log
echo report_2026_0[1-3].csv
echo data?.log
echo *.txt
echo report_2025_1?.csv
echo *.xyz
mkdir -p q1 && cp report_2026_0[1-3].csv q1/ && ls q1
'''

RUN = dict(
    heading='Test patterns, then use them',
    intro='<p>The script creates sample files with braces, tests five patterns with echo, then copies the first quarter. Change the patterns and run again.</p>',
    code=MAIN,
    anno=[
        ('touch report_2025_{01..12}.csv report_2026_{01..06}.csv notes.txt data1.log data10.log', 'Braces create 18 report names.'),
        ('echo report_2026_0[1-3].csv', 'One digit from 1 to 3.'),
        ('echo data?.log', 'Exactly one character: data10.log does not fit.'),
        ('echo *.xyz', 'No match: printed as it is.'),
        ('mkdir -p q1 && cp report_2026_0[1-3].csv q1/ && ls q1', 'The tested pattern, now with cp.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which pattern printed itself unchanged? Why?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many names does this print? Then run.',
             code='echo {a,b,c}{1,2}\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the quotes stop the pattern from working. Fix it.',
             code='touch a.txt b.txt\nls "*.txt"\n', expect='any'),
        dict(label='4 · Your turn', hint='Print all 2025 reports from April to June.',
             code='touch report_2025_{01..12}.csv\necho report_2025_0[4-6].csv\n'),
        dict(label='5 · Challenge', hint='List every .py file in every sub-folder with one pattern.',
             code='mkdir -p app/core/db && touch app/main.py app/core/db/models.py\nshopt -s globstar\necho **/*.py\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: interactive helpers and other shells',
    intro='<p>Some pattern features are keyboard shortcuts or differ between shells. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Expand a pattern on the command line before running', cmd='rm *.tmp    then press Ctrl+x and *', output='rm a.tmp b.tmp c.tmp',
             note='Typical. The line is rewritten in place so you can read it; press Enter only if it is right.'),
        dict(title='2 · Your bash version and glob options', cmd="echo $BASH_VERSION; shopt | grep glob", output=pc("echo $BASH_VERSION; shopt | grep glob"),
             note='Recorded on our build machine (bash 5.2). globskipdots is new in 5.2.'),
        dict(title='3 · zsh (macOS default) reports no match itself', cmd='ls *.xyz', output='zsh: no matches found: *.xyz',
             note='Typical in zsh: like bash’s failglob, the command is not run.'),
        dict(title='4 · Too many files for one command', cmd='rm /data/tmp/*', output='bash: /usr/bin/rm: Argument list too long',
             note='Typical with hundreds of thousands of files. Use <code>find /data/tmp -type f -delete</code> or xargs (Lesson 13.2).'),
    ],
)

TRACE = dict(
    heading='Watching patterns turn into names',
    intro='<p>Step through. Each echo shows what a pattern became; the last lines use patterns with real commands.</p>',
    code='''touch jan.csv feb.csv mar.csv notes.txt
echo *.csv
echo ???.csv
echo [jf]*.csv
mkdir old
mv [jf]*.csv old/
echo *.csv
''',
    notes={2: 'Star :: All three CSV names.', 3: 'Three ? :: Names with exactly 3 letters before .csv.', 4: 'Brackets :: Starts with j or f.',
           6: 'Use it :: mv receives jan.csv and feb.csv.', 7: 'Check :: Only mar.csv is left here.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an analyst picking a period, an admin cleaning rotated logs, and a developer listing source files at any depth.'
EXAMPLES = [
    dict(level='b', tag='Data analysis', title='Pick a quarter of reports',
         problem='<p>From monthly reports of 2025 and 2026, copy Q4 2025 (October–December) into <code>q4/</code>.</p>',
         inp='report_2025_01…12.csv, report_2026_01…06.csv',
         approach=['Fixed text <code>report_2025_1</code> + one digit 0–2.', 'Test with echo, then cp.'],
         code='''touch report_2025_{01..12}.csv report_2026_{01..06}.csv
echo report_2025_1[0-2].csv
mkdir -p q4 && cp report_2025_1[0-2].csv q4/
ls q4
''',
         notes={2: 'Test :: Exactly three names.', 3: 'Use :: Same pattern with cp.'},
         tryit='Write the pattern for Q2 2026 (April–June).'),
    dict(level='i', tag='System admin', title='Delete old rotated logs, keep the current one',
         problem='<p>A folder has <code>app.log</code> and rotated copies <code>app.log.1</code> … <code>app.log.12</code>. Delete the rotated copies 4 and above, keep app.log and 1–3.</p>',
         inp='app.log app.log.1 … app.log.12',
         approach=['One digit 4–9: <code>app.log.[4-9]</code>.', 'Two digits: <code>app.log.1?</code>.'],
         code='''touch app.log app.log.{1..12}
echo rm app.log.[4-9] app.log.1?
rm app.log.[4-9] app.log.1?
ls
''',
         notes={2: 'Preview :: Always before rm.', 3: 'Delete :: Exactly those 9 files.'},
         tryit='What would <code>app.log.*</code> have matched?'),
    dict(level='a', tag='Development', title='Source files at any depth, without tests',
         problem='<p>List all <code>.py</code> files in the project at any depth, except files whose name starts with <code>test_</code>.</p>',
         inp='app/main.py, app/core/db.py, app/tests/test_db.py, setup.py',
         approach=['globstar for any depth.', 'extglob <code>!(test_*)</code> for “not starting with test_”.'],
         code='''mkdir -p app/core app/tests
touch setup.py app/main.py app/core/db.py app/tests/test_db.py
shopt -s globstar extglob
echo **/!(test_*).py
''',
         notes={3: 'Options :: Both enabled before use.', 4: 'Pattern :: Any folder depth, then any name that is not test_*.'},
         tryit='Change it to list only the test files.'),
]

QUIZ = mix([
    dict(q='Which files does report_2026_0[1-3].csv match?', options=['All 2026 reports', 'January to March 2026', 'Report 0, 1, 2, 3', 'Only report_2026_0.csv'], answer=1,
         why='[1-3] is one character: 1, 2 or 3.'),
    dict(q='Who expands * in ls *.txt?', options=['ls', 'The kernel', 'The shell (bash)', 'The file system'], answer=2,
         why='Bash replaces the pattern with names before ls starts.'),
    dict(q='What does echo *.xyz print when no file matches?', options=['Nothing', '*.xyz', 'An error from echo', 'All files'], answer=1,
         why='By default an unmatched pattern is left unchanged.'),
    dict(q='Does * match .bashrc?', options=['Yes', 'No, hidden files need .* or dotglob', 'Only for root', 'Only with ls -a'], answer=1,
         why='Names starting with a dot are skipped by * unless dotglob is on.'),
    dict(q='{1..3}.txt in an empty folder gives…', options=['nothing', '1.txt 2.txt 3.txt', '{1..3}.txt', 'an error'], answer=1,
         why='Braces generate text without checking the folder.'),
    dict(q='How do you make ** match any depth of folders?', options=['shopt -s extglob', 'shopt -s globstar', 'set -f', 'shopt -s dotglob'], answer=1,
         why='globstar enables ** recursion.'),
    dict(q='Which loop is safe for names with spaces?', options=['for f in $(ls *.txt)', 'for f in *.txt; do cat "$f"; done', 'for f in "*.txt"', 'for f in `ls`'], answer=1,
         why='A glob gives each name as one item; quote the variable.'),
    dict(q='data?.log matches…', options=['data1.log and data10.log', 'data1.log, not data10.log', 'only data.log', 'nothing'], answer=1,
         why='? is exactly one character.'),
])

REVISION = [
    '<code>*</code> any text · <code>?</code> one character · <code>[abc]</code> <code>[1-3]</code> one from a set · <code>[!a]</code> not.',
    'Bash expands patterns before the command starts; the command only sees names.',
    'Test every pattern with <code>echo pattern</code>; count with <code>| wc -w</code>.',
    'No match → the pattern stays as text (nullglob: disappears, failglob: error).',
    '<code>*</code> skips hidden files: use <code>.[!.]*</code> or <code>shopt -s dotglob</code>.',
    'Quotes switch globbing off: quote variables (<code>"$f"</code>), not patterns.',
    'Braces <code>{a,b}</code> <code>{01..12}</code> <code>{1..9..2}</code> write names (create); wildcards find names (select).',
    '<code>shopt -s globstar</code> → <code>**/*.py</code>; <code>shopt -s extglob</code> → <code>!(…)</code>, <code>@(a|b)</code>.',
]

FAQ = [
    ('What are wildcards in Linux?', 'Special characters in file name patterns: * (any characters), ? (one character), [ ] (one character from a set). The shell expands them into matching file names.'),
    ('What is the difference between * and ?', '* matches any number of characters including none; ? matches exactly one.'),
    ('What is globbing?', 'Pathname expansion: the shell replacing a pattern with the sorted list of matching file names.'),
    ('What is the difference between brace expansion and wildcards?', 'Brace expansion generates text whether or not files exist; wildcards match existing file names only.'),
    ('Why does ls *.txt not show hidden files?', 'Wildcards do not match names that start with a dot unless the pattern starts with a dot or dotglob is enabled.'),
    ('How do you match files in all sub-directories?', 'Enable globstar (shopt -s globstar) and use **/pattern, or use find -name.'),
    ('Are glob patterns the same as regular expressions?', 'No. In globs * means any text; in regex * means “repeat the previous item”. Regex is covered in Lesson 6.6 and rename in Lesson 3.7.'),
]

PRACTICE_INTRO = 'Pattern tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='All text files', stmt='Print all <code>.txt</code> names.', inp='a.txt b.txt c.csv',
         code='touch a.txt b.txt c.csv\necho *.txt\n', explain='* + fixed ending.'),
    dict(level='easy', title='One character', stmt='Print the names <code>v1.log</code> … <code>v9.log</code> but not <code>v10.log</code>.', inp='v1.log v2.log v10.log',
         code='touch v1.log v2.log v10.log\necho v?.log\n', explain='? = exactly one character.'),
    dict(level='easy', title='Create with braces', stmt='Create <code>mon.txt</code> to <code>fri.txt</code> with one command.', inp='—',
         code='touch {mon,tue,wed,thu,fri}.txt\nls\n', explain='A comma list in braces.'),
    dict(level='medium', title='A range of months', stmt='Print reports 04, 05 and 06.', inp='report_01 … report_12 .csv',
         code='touch report_{01..12}.csv\necho report_0[4-6].csv\n', explain='One digit from 4 to 6.'),
    dict(level='medium', title='Hidden files', stmt='Print only the hidden file names (not . and ..).', inp='.env .gitignore main.py',
         code='touch .env .gitignore main.py\necho .[!.]*\n', explain='A dot, then a character that is not a dot.'),
    dict(level='medium', title='Count matches', stmt='How many files start with <code>img_</code>?', inp='img_1.png … img_7.png, logo.png',
         code='touch img_{1..7}.png logo.png\nls img_* | wc -l\n', explain='Pattern + count.'),
    dict(level='business', title='Archive one year', stmt='Archive all 2025 CSV reports into <code>2025.tgz</code> and list the archive.', inp='report_2025_01…03.csv, report_2026_01.csv',
         code='touch report_2025_{01..03}.csv report_2026_01.csv\ntar -czf 2025.tgz report_2025_*.csv\ntar -tzf 2025.tgz\n', explain='tar receives only the 2025 names.'),
    dict(level='business', title='Safe loop', stmt='Print the size of every .txt file, including one with a space in its name.', inp='a.txt, "my notes.txt"',
         code='echo hi > a.txt; echo hello > "my notes.txt"\nfor f in *.txt; do echo "$f: $(wc -c < "$f") bytes"; done\n', explain='Glob loop + quoted variable.'),
]

SCN_INTRO = 'Interview questions about wildcards and globbing, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“List all log files whose name has exactly one digit.”',
        'The folder has app1.log, app2.log and app10.log.',
        'do you know * vs ?',
        '''<ul>
          <li><code>ls app?.log</code>: ? is exactly one character.</li>
          <li>For digits only: <code>ls app[0-9].log</code>.</li>
          <li><code>app*.log</code> would also match app10.log.</li>
        </ul>''', 'not knowing that the shell expands the pattern.') +
    scn('Operations · scripts', 'Junior', 'The loop that processed “*.csv”',
        'A nightly script logs “cannot open *.csv” on days when no files arrive.',
        'do you know unmatched globs?',
        '''<ol>
          <li>With no match, bash leaves <code>*.csv</code> as text, so the loop runs once with that name.</li>
          <li>Fix: <code>shopt -s nullglob</code>, or <code>[ -e "$f" ] || continue</code> in the loop.</li>
          <li>Optionally count first and exit cleanly when there are no files.</li>
        </ol>''', 'hiding the error with 2>/dev/null.') +
    scn('DevOps · CI', 'Mid-level', 'The build artefact that was not uploaded',
        'A CI step runs <code>cp build/*.jar out/</code>; one day the jar is called <code>.app.jar</code> by mistake and nothing is copied, yet the step passes.',
        'do you understand hidden files and exit codes?',
        '''<ul>
          <li>* skips dotfiles, so the pattern matched nothing and cp received the literal text (it should fail; check that the step really checks exit codes).</li>
          <li>Use <code>shopt -s failglob</code> (or <code>set -e</code> with a count check) so an empty match fails the build.</li>
          <li>Fix the naming upstream; list artefacts explicitly.</li>
        </ul>''', '“it works on my machine”.') +
    scn('Platform team · scale', 'Senior', '“Argument list too long”',
        '<code>rm /data/spool/*</code> fails on a folder with 2 million files.',
        'do you know the limits of globbing?',
        '''<ul>
          <li>The glob expands to millions of names, exceeding the kernel’s ARG_MAX for one exec.</li>
          <li>Use <code>find /data/spool -type f -delete</code>, or <code>find … -print0 | xargs -0 rm</code> (batches).</li>
          <li>Also: globbing a huge folder is slow (one getdents64 pass, then a sort); design spool folders with sub-directories.</li>
        </ul>''', 'raising limits instead of changing the approach.')
) + interview([
    ('Explain *, ? and [ ] with examples.', '*.txt = any name ending in .txt; file?.log = one character; [a-c]* = names starting with a, b or c; [!0-9]* = not starting with a digit.'),
    ('Who expands wildcards?', 'The shell, before the command runs. The command receives the list of names.'),
    ('What happens when a glob matches nothing?', 'By default the pattern is passed unchanged; nullglob makes it disappear, failglob makes it an error.'),
    ('Difference between {1..3} and [1-3]?', 'Braces generate 1 2 3 regardless of files; [1-3] matches existing names with one of those characters.'),
    ('How do you include hidden files in *?', 'shopt -s dotglob, or add .[!.]* to the pattern.'),
    ('Glob vs regex?', 'Globs match file names with * ? [ ]; regex is a richer language for text (., *, +, groups) used by grep, sed, rename.'),
    ('How do you match any depth of sub-folders?', 'shopt -s globstar and **/pattern, or find -name pattern.'),
], [
    ('RHCSA (EX200)', 'Essential tools: “Create, delete, copy, and move files and directories”; wildcards are used throughout these tasks.'),
    ('LFCS', 'Essential Commands: use shell features such as wildcards to work with files efficiently.'),
    ('CompTIA Linux+', 'Shell globbing and brace expansion in file management and scripting objectives.'),
]) + distro('Globs are a shell feature, so they depend on the shell more than on the distribution.', [
    ('Default shell', 'bash 5.2 (Ubuntu 24.04)', 'bash 5.1 (RHEL 9)', 'zsh (bash 3.2 also present)', 'WSL: bash; Git Bash: bash 5'),
    ('No match', 'pattern kept (nullglob/failglob options)', 'same', 'zsh: error “no matches found”', 'same as bash'),
    ('.* matches . and ..', 'no (globskipdots, bash 5.2)', 'yes in bash 5.1', 'zsh: no', 'depends on bash version'),
    ('{01..12} padding', 'yes', 'yes', 'bash 3.2: no padding; zsh: yes', 'yes'),
    ('** recursion', 'needs shopt -s globstar', 'same', 'zsh: on by default', 'same as bash'),
    ('Case', 'case-sensitive', 'case-sensitive', 'file system usually case-insensitive', '/mnt/c case-insensitive'),
]) + teaser('3.5', 'A 2 GB log file: Riya needs the last 50 lines, then to watch new lines arrive live, then the lines 1000–1010. Which three commands, without ever opening the whole file?')

CHEATSHEET = cheatsheet('wildcards and braces', [
    ('Wildcards (find)', [('*', 'any text, even none'), ('?', 'exactly one character'), ('[abc] [a-z]', 'one from a set / range'), ('[!a] [^a]', 'one, not a'), ('[[:digit:]]', 'one digit (class)')]),
    ('Braces (write)', [('{a,b,c}', 'list'), ('{1..10}', 'sequence'), ('{01..12}', 'zero padded'), ('{1..20..5}', 'with step'), ('f{,.bak}', 'f and f.bak')]),
    ('Safety', [('echo pattern', 'preview the list'), ('echo pattern | wc -w', 'count'), ('Ctrl+x *', 'expand in place'), ('"$f"', 'quote variables'), ('for f in *.txt', 'never $(ls)')]),
    ('Options (shopt -s)', [('nullglob', 'no match → nothing'), ('failglob', 'no match → error'), ('dotglob', '* includes dotfiles'), ('nocaseglob', 'ignore case'), ('globstar / extglob', '** and !(…)')]),
    ('Useful patterns', [('*/', 'folders only'), ('.[!.]*', 'hidden files'), ('**/*.py', 'any depth'), ('!(*.csv)', 'all but CSV'), ('report_2026_0[1-3].csv', 'Q1 2026')]),
])

MINDMAP = mindmap('Wildcards', [
    ('*', 'blue', ['any text', 'not hidden files', 'not across /']),
    ('? and [ ]', 'green', ['? one char', '[1-3] range', '[!a] not']),
    ('Braces', 'amber', ['write, not find', '{a,b} {01..12}', 'create names']),
    ('Surprises', 'red', ['no match → text', 'quotes stop it', 'spaces: "$f"']),
    ('Options', 'violet', ['nullglob failglob', 'globstar **', 'extglob !(…)']),
    ('Habit', 'acc', ['echo first', 'count with wc -w', 'then cp/mv/rm']),
])

LAB = lab('sort the reports folder', 'Build the lab, do the four tasks using one pattern each, then run the checker.',
    setup='''mkdir -p ~/lab34 && cd ~/lab34 && rm -rf rep
mkdir rep && cd rep
touch report_2025_{01..12}.csv report_2026_{01..06}.csv data{1..3}.log data10.log notes.txt .env''',
    tasks=['Move the Q1 2026 reports (January–March) into a new folder <code>q1_2026</code>.',
           'Move all 2025 reports into <code>y2025</code>.',
           'Delete only the logs with a one-digit number (data1–data3), keep data10.log.',
           'Copy every hidden file into <code>hidden_backup</code>.'],
    solution='''mkdir q1_2026 y2025 hidden_backup
mv report_2026_0[1-3].csv q1_2026/
mv report_2025_*.csv y2025/
rm data?.log
cp .[!.]* hidden_backup/''',
    check='''cd ~/lab34/rep
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 Q1 2026 moved"   '[ "$(ls q1_2026 2>/dev/null | tr "\\n" " ")" = "report_2026_01.csv report_2026_02.csv report_2026_03.csv " ]'
ok "2 2025 moved"      '[ "$(ls y2025 2>/dev/null | wc -l)" -eq 12 ] && ! ls report_2025_* >/dev/null 2>&1'
ok "3 one-digit logs"  '[ ! -e data1.log ] && [ ! -e data3.log ] && [ -e data10.log ]'
ok "4 hidden copied"   '[ -f hidden_backup/.env ]' ''')
