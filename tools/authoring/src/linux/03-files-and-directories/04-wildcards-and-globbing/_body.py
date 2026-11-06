import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

SETUP = 'touch report_2025_{01..12}.csv report_2026_{01..06}.csv notes.txt Notes.md data1.log data2.log data10.log a.txt b.txt c.txt'

HOOK = hook('Riya’s folder has 500 files: monthly reports for two years, logs, notes. Her manager wants “the 2026 reports for January to March” copied to a USB stick. Clicking through 500 names, she will miss one or pick a 2025 file by mistake. With one pattern, <code>report_2026_0[1-3].csv</code>, the shell picks exactly the right three, every time.',
    ['select files by pattern with <code>*</code>, <code>?</code> and <code>[ ]</code>, and test any pattern safely with <code>echo</code>',
     'generate names with braces <code>{a,b}</code> and <code>{01..12}</code>, and know how braces differ from wildcards',
     'handle the tricky cases: no match, hidden files, spaces in names, quotes that switch patterns off',
     'use the advanced options <code>**</code> (globstar), <code>!(…)</code> (extglob) and <code>nullglob</code> in scripts'])
ROAD = roadmap([
    ('story', 'The story', 3, '500 files, three needed'),
    ('decide', 'Which pattern when?', 2, 'the quick chart'),
    ('definition', 'What globbing is', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each pattern, by field', 12, 'real runs, your field'),
    ('errors', 'Errors decoded', 3, 'no match, quotes, spaces'),
    ('animation', 'See it happen', 4, 'who expands the *?'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which pattern do I need? (decide in 5 seconds)', [
    ('Any name ending in .csv', '*.csv', '* = any text, even none'),
    ('Exactly one unknown character', 'data?.log', 'data1.log, not data10.log'),
    ('One character from a set or range', 'report_2026_0[1-3].csv', 'Jan, Feb, Mar'),
    ('Anything except some characters', '[!a]*.txt', '! (or ^) = not'),
    ('A list of names, existing or not', '{jan,feb,mar}.csv', 'braces always generate'),
    ('A numbered sequence', 'day_{01..31}.log', 'with zero padding'),
    ('In every sub-folder too', '**/*.py', 'needs shopt -s globstar'),
    ('Everything except a pattern', '!(*.log)', 'needs shopt -s extglob'),
    ('Check a pattern before using it', 'echo pattern', 'shows the exact list'),
    ('The * as a real character', '"*.txt" or \\*', 'quotes switch globbing off'),
])

cmap = concept_map(
    [('3.1', 'Creating files', 'braces met first'), ('3.2', 'cp and mv', 'act on many files'), ('3.3', 'Deleting safely', 'rm *.log needs a checked pattern')],
    ['* any text, ? one character, [ ] one from a set', 'braces {a,b} {1..9} generate names', 'no match, hidden files, quotes and spaces', 'globstar **, extglob !(…), nullglob', 'echo: test every pattern first'],
    [('3.7', 'Bulk renaming', 'regex is different from globs'), ('6.1', 'grep', 'patterns inside files'), ('7.1', 'find -name', 'globs in every sub-folder'), ('12.4', 'Quoting and expansion', 'the full expansion order')],
    'Wildcards turn “all these files” into one short word. They are used with every command: ls, cp, mv, rm, tar, grep.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 140, ['$ ls | wc -l', ('500', 'out'), '$ echo report_2026_0[1-3].csv', ('report_2026_01.csv report_2026_02.csv', 'acc'), ('report_2026_03.csv', 'acc'), '$ cp report_2026_0[1-3].csv /media/usb/'], title='riya@laptop: ~/reports', size=7.6, step=15)
      + t(352, 36, 'The shell picks the files:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• * = any text', '• ? = one character', '• [1-3] = 1, 2 or 3', '• echo first: see the list', '• then cp, mv, rm, tar…'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>500 files, three needed</h2>
  <div class="story">
''' + puzzle('Riya runs <code>ls *.xyz</code> in a folder with no .xyz files and gets “cannot access ’*.xyz’”. Why does the error message show the star itself, and not an empty list?') + '''
    <p class="narration">Riya’s reports folder has two years of monthly CSV files plus logs and notes. She needs the first quarter of 2026 on a USB stick before a meeting.</p>
''' + scene('A terminal: a folder with 500 files; echo report_2026_0[1-3].csv shows the three matching names; cp copies them to the USB stick.', sc,
            'One pattern instead of 500 clicks: <tspan font-weight="700" class="s-acc">the shell expands it</tspan>.') + '''
R> Is <code>[1-3]</code> something special in cp?
A> No. cp never sees the pattern. Bash looks at the files in the folder, finds the names that fit, and gives cp the list. That is called <b>globbing</b>; the special characters are <b>wildcards</b>.
K> So it works with every command?
A> Every one: ls, cp, mv, rm, tar, grep. Which is why you always test it with <code>echo</code> first: echo prints exactly the list the real command would get. Today: <code>*</code>, <code>?</code>, <code>[ ]</code>, braces, and the advanced options, with how each IT role uses them.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Wildcards are like a fill-in-the-blank search: star means any number of letters, question mark one letter, brackets one letter from a list. Braces are like a photocopied form with blanks filled in from a list.">'
       + ''.join(label_box(16 + k * 156, 22, 144, 110, [a, b, c, d], tone, 9) for k, (a, b, c, d, tone) in enumerate([
           ('*', 'any letters', 'or none', 'r*t: rat, root, rt', 'blue'),
           ('?', 'exactly one', 'letter', 'r?t: rat, rot', 'green'),
           ('[abc]', 'one letter', 'from the list', 'r[ao]t: rat, rot', 'violet'),
           ('{a,b}', 'write each', 'from the list', 'r{a,o}t: rat rot', 'amber')]))
       + t(320, 160, 'The first three SEARCH the folder for names that already exist.', 9.4, 'ink2')
       + t(320, 182, 'Braces do not search: they simply WRITE every combination.', 9.4, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Wildcards at four depths', [
    ('v', 'No jargon: fill in the blanks', '      <p>Like a crossword clue with blanks.</p>' + pic + '''
      <ul>
        <li><code>*</code> means “any letters here”. <code>*.csv</code> = every name that ends with .csv.</li>
        <li><code>?</code> means “one letter here”.</li>
        <li><code>[ ]</code> means “one of these letters”.</li>
      </ul>'''),
    ('b', 'The patterns you will use every day', '''      <ul>
        <li><code>ls *.csv</code>, <code>cp *.jpg photos/</code>, <code>rm *.tmp</code>.</li>
        <li><code>data?.log</code> matches data1.log but not data10.log (two characters).</li>
        <li><code>[0-9]</code> one digit, <code>[a-z]</code> one lowercase letter, <code>[!0-9]</code> anything but a digit.</li>
        <li>Braces make lists: <code>mkdir {jan,feb,mar}</code>, <code>touch day{1..7}.log</code>.</li>
        <li>Before a risky command, run <code>echo</code> with the same pattern.</li>
      </ul>'''),
    ('i', 'The rules that surprise people', '''      <ul>
        <li><b>No match</b>: bash leaves the pattern as it is (<code>*.xyz</code>), so the command gets a literal star. Hence “cannot access ’*.xyz’”.</li>
        <li><b>Hidden files</b> (starting with <code>.</code>) are not matched by <code>*</code>; use <code>.*</code> or <code>shopt -s dotglob</code>. Since bash 5.2, <code>.*</code> no longer matches <code>.</code> and <code>..</code> (option globskipdots).</li>
        <li><b>Quotes</b> switch globbing off: <code>"*.txt"</code> is just the text *.txt. Variables should be quoted (<code>"$f"</code>) but patterns not.</li>
        <li><b>Braces vs wildcards</b>: <code>{07..09}</code> writes names even if the files do not exist; <code>0[7-9]</code> only matches existing files.</li>
        <li>Names with spaces are safe in <code>for f in *.txt</code> as long as you write <code>"$f"</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: expansion order and options', '''      <ul>
        <li>Bash expands in a fixed order: <b>brace</b> → tilde → parameter/variable → command substitution → arithmetic → word splitting → <b>pathname (glob)</b> → quote removal (Lesson 12.4).</li>
        <li>Globbing reads the folder (<code>opendir/getdents64</code>), matches each name, and <b>sorts</b> the result by the locale’s collation order.</li>
        <li>Shell options: <code>nullglob</code> (no match → nothing), <code>failglob</code> (no match → error), <code>dotglob</code>, <code>nocaseglob</code>, <code>globstar</code> (<code>**</code> = any depth), <code>extglob</code> (<code>?(…) *(…) +(…) @(…) !(…)</code>).</li>
        <li>Range brackets like <code>[a-z]</code> depend on the locale; <code>[[:lower:]]</code>, <code>[[:digit:]]</code> are exact everywhere.</li>
        <li>Very large expansions can exceed the kernel’s argument limit: “Argument list too long”. Then use <code>find … -exec</code> or <code>xargs</code> (Lesson 13.2).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Wildcards, globbing and brace expansion</h2>
''' + def_block(
    '<b>Globbing</b> (pathname expansion) is the shell replacing a word that contains wildcards with the sorted list of existing file names that match it. The wildcards are <code>*</code> (any string, including empty), <code>?</code> (any single character) and <code>[…]</code> (one character from a set or range; <code>[!…]</code> or <code>[^…]</code> negates). <b>Brace expansion</b> (<code>{a,b}</code>, <code>{1..9}</code>) is a different feature that generates strings whether or not files exist.',
    'Wildcards <b>find</b> existing names; braces <b>write</b> names. The shell does both before the command starts.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Wildcard', f'A special character in a pattern: * ? [ ]. {gl("globbing-wildcards", "Glossary →")}'),
    ('Glob / globbing', 'The pattern, and the shell turning it into names.'),
    ('Brace expansion', f'{{a,b}} and {{1..9}}: generated text. {gl("brace-expansion", "Glossary →")}'),
    ('Character class', '[[:digit:]], [[:upper:]]: named sets.'),
    ('Hidden file', f'A name starting with a dot. {gl("hidden-file-dotfile", "Glossary →")}'),
    ('Quoting', f'Quotes stop expansion. {gl("quoting-single-vs-double-quotes", "Glossary →")}'),
    ('Expansion order', f'The steps bash runs. {gl("expansion-order", "Glossary →")}'),
    ('Regex', f'A different, more powerful pattern language. {gl("regular-expression-regex", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('glob', 'global', 'Early Unix had a separate program /etc/glob that expanded patterns.'),
    ('wildcard', 'card game', 'A wild card can stand for any card.'),
    ('*', 'star / asterisk', 'Any number of characters.'),
    ('?', 'question mark', 'One unknown character.'),
    ('globstar', 'glob + star', '** goes into every folder.'),
    ('extglob', 'extended glob', 'Extra patterns borrowed from ksh.'),
    ('nullglob', 'null + glob', 'No match → nothing (null).'),
    ('dotglob', 'dot + glob', '* also matches dotfiles.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('All CSV files', '<code>*.csv</code>'),
    ('One character', '<code>data?.log</code>'),
    ('A range', '<code>report_2026_0[1-3].csv</code>'),
    ('Not these', '<code>[!a]*</code>'),
    ('Generate names', '<code>{jan,feb}</code>, <code>{01..12}</code>'),
    ('Test a pattern', '<code>echo pattern</code>'),
]) + '\n' + lv + didyou('In the very first versions of Unix, the shell did not expand wildcards itself: it called a separate program, <code>/etc/glob</code>, short for “global”. The program is long gone, but the name “glob” stayed, and it is used today in Python (<code>glob</code> module), Node.js, .gitignore files and Docker.') + '''
EXAM> “Explain wildcards in Linux with examples” → * any characters, ? one character, [ ] one character from a set or range, [!…] negation; give ls *.txt, ls file?.log, ls [a-c]*; mention that the shell expands them before running the command, and that braces generate strings instead of matching files.
''' + qc('Which files does <code>data?.log</code> match among data1.log, data2.log and data10.log?', 'data1.log and data2.log. <code>?</code> is exactly one character; data10.log has two.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>All the pattern characters</h2>
''' + table(['Pattern', 'Matches', 'Example', 'Matches here'], [
    ['<code>*</code>', 'any text, also empty', '<code>data*.log</code>', 'data1.log, data10.log, data2.log'],
    ['<code>?</code>', 'exactly one character', '<code>data?.log</code>', 'data1.log, data2.log'],
    ['<code>[abc]</code>', 'one of a, b, c', '<code>[ab].txt</code>', 'a.txt, b.txt'],
    ['<code>[a-c]</code>', 'one in the range', '<code>[a-c].txt</code>', 'a.txt, b.txt, c.txt'],
    ['<code>[!a]</code> / <code>[^a]</code>', 'one character, not a', '<code>[!a].txt</code>', 'b.txt, c.txt'],
    ['<code>[[:digit:]]</code>', 'one digit (also :alpha: :upper: :lower: :space:)', '<code>data[[:digit:]].log</code>', 'data1.log, data2.log'],
    ['<code>{a,b}</code>', 'writes a and b (no search)', '<code>{x,y}.txt</code>', 'x.txt y.txt even if missing'],
    ['<code>{1..9}</code>, <code>{01..12}</code>, <code>{a..e}</code>, <code>{1..10..3}</code>', 'writes a sequence (with step)', '<code>file{1..10..3}</code>', 'file1 file4 file7 file10'],
    ['<code>**</code>', 'any depth of folders (globstar)', '<code>**/*.py</code>', 'src/top.py, src/a/b/deep.py'],
    ['<code>!(p)</code> <code>@(p|q)</code> <code>+(p)</code>', 'not / one of / one or more (extglob)', '<code>!(*.csv|*.log)</code>', 'everything else'],
], minw=640) + mistake('ls report_2026_0{7..9}.csv     (to see which of these exist)', 'ls report_2026_0[7-9].csv',
                       'Braces always write all three names, so ls complains about each missing one. A bracket pattern only lists files that really exist.') + qc('What is the difference between <code>{1..3}.txt</code> and <code>[1-3].txt</code> in an empty folder?', '<code>{1..3}.txt</code> writes 1.txt 2.txt 3.txt anyway; <code>[1-3].txt</code> matches nothing and stays as the text “[1-3].txt”.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands by field
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each pattern explained, then used in every field</h2>
  <p id="commands">Every example below was really run on Ubuntu 24.04 in a folder with these files: <code>report_2025_01…12.csv</code>, <code>report_2026_01…06.csv</code>, <code>notes.txt</code>, <code>Notes.md</code>, <code>data1.log</code>, <code>data2.log</code>, <code>data10.log</code>, <code>a.txt</code>, <code>b.txt</code>, <code>c.txt</code> (plus a few extra per example). Most use <code>echo</code>, so you see exactly the list the shell would hand to a command.</p>
''' + cmdcard_u(['you mean “every name that starts / ends / contains …”', 'selecting files for cp, mv, rm, tar, grep', 'a quick count: <code>ls *.csv | wc -l</code>'],
               ['you need one exact character count (use ?)', 'the files are in many sub-folders (use ** or find)', 'you need it as plain text (quote it)'])(
    'star', '*', 'star: any text',
    'Matches any sequence of characters in a name, including nothing at all. It does not cross a <code>/</code> and does not match hidden files.',
    '…*…   e.g. *.csv, report_*, *2026*', 'safe',
    [('*.csv', 'every name ending in .csv', 'one file type'),
     ('report_*', 'every name starting with report_', 'one family of files'),
     ('*2026*', 'every name containing 2026', 'by year, by keyword'),
     ('dir/*', 'everything inside dir (not hidden)', 'act on a folder’s content'),
     ('*/', 'only folders', '<code>ls -d */</code>'),
     ('.*', 'hidden names (bash 5.2: not . and ..)', 'dotfiles')],
    dict(cmd='echo *.csv | wc -w\necho *2026*', setup=SETUP, note='18 CSV files in total; six of them contain 2026.'),
    [('data', [
        dict(situation='Count and size all CSV files before loading them.', setup=SETUP, cmd='ls *.csv | wc -l\ncat *.csv | wc -c',
             why='The same pattern feeds ls and cat; here the files are empty, so 0 bytes.'),
        dict(situation='Archive last year’s reports in one go.', setup=SETUP, cmd='tar -czf reports_2025.tgz report_2025_*.csv && tar -tzf reports_2025.tgz | wc -l',
             why='tar receives the 12 expanded names (Lesson 14.5).')]),
     ('sys', [
        dict(situation='List only the folders in /etc that end in .d (config drop-in folders).', cmd='ls -d /etc/*.d/ | head -5',
             why='<code>*.d/</code> with a trailing slash matches only folders; <code>-d</code> stops ls from listing their content.')]),
     ('dev', [
        dict(situation='Search for TODO in every Python file of the folder.', setup='printf "x=1\\n# TODO fix\\n" > app.py; printf "# TODO tests\\n" > test_app.py; echo hi > README.md', cmd='grep -n TODO *.py',
             why='grep gets the list of .py files; with several files it prints the file name before each match (Lesson 6.1).')]),
     ('sec', [
        dict(situation='Check permissions of every hidden config file in a home folder.', setup='touch .bashrc .profile .ssh_config_backup && chmod 600 .ssh_config_backup', cmd="stat -c '%A %n' .[!.]*",
             why='<code>*</code> skips dotfiles; <code>.[!.]*</code> selects names that start with one dot (and works in every shell, unlike relying on globskipdots). Files with secrets should be rw------- (600).'),
        dict(situation='Danger check: what would <code>rm *</code> delete here?', setup=SETUP, cmd='echo rm * | wc -w',
             why='Always count first. 25 names: everything in the folder.')]),
    ]
) + cmdcard_u(['you know exactly how many characters are unknown', 'versions or numbers with a fixed width: v1.?, 202?', 'excluding longer names (data?.log skips data10.log)'],
               ['the unknown part has a variable length (use *)', 'you need a specific set of characters (use [ ])'])(
    'qmark', '?', 'question mark: exactly one character',
    'Matches exactly one character, whatever it is. Two question marks = exactly two characters.',
    '…?…   e.g. data?.log, report_2026_0?.csv', 'safe',
    [('?', 'any one character', 'single-digit numbers'),
     ('??', 'any two characters', 'two-digit months'),
     ('file?.txt', 'file1.txt … fileZ.txt, not file10.txt', 'fixed width names')],
    dict(cmd='echo data?.log\necho data??.log', setup=SETUP, note='One ? matched data1 and data2; two ?? matched only data10.'),
    [('sys', [
        dict(situation='Rotated logs are named syslog.1 … syslog.9 and syslog.10 …; list only the first nine.', setup='touch syslog syslog.{1..12}', cmd='echo syslog.?',
             why='One character after the dot: 1 to 9, not 10, 11, 12.')]),
     ('data', [
        dict(situation='Select monthly files of 2026 whatever the month.', setup=SETUP, cmd='echo report_2026_??.csv',
             why='Two characters for the month: robust even if the folder has report_2026_summary.csv.')]),
     ('dev', [
        dict(situation='List Python 3 minor versions installed under /usr/bin.', cmd='ls /usr/bin/python3.?? /usr/bin/python3.? 2>/dev/null',
             why='python3.12 has two characters after the dot, python3.9 one: two patterns cover both.', expect='any')]),
    ]
) + cmdcard_u(['one position may be one of a few characters', 'ranges of digits or letters: [0-9], [a-f]', 'excluding something: [!…]'],
               ['you need several characters in a row (brackets match ONE)', 'you want a list of whole words (use braces or extglob @(…))'])(
    'brackets', '[ ]', 'brackets: one character from a set',
    'Matches exactly one character that is in the set or range. With <code>!</code> or <code>^</code> first, one character that is <b>not</b> in it.',
    '[abc]  [a-z]  [0-9]  [!0-9]  [[:digit:]]', 'safe',
    [('[abc]', 'a, b or c', 'small sets'),
     ('[1-3]', '1, 2 or 3', 'ranges of numbers'),
     ('[!a] or [^a]', 'any one character except a', 'exclusions'),
     ('[nN]', 'n or N', 'upper or lower case'),
     ('[[:digit:]] [[:upper:]] [[:space:]]', 'named classes', 'locale-safe ranges'),
     ('[]a]', '] or a (] first = literal)', 'rare: special characters')],
    dict(cmd='echo report_2026_0[1-3].csv\necho [!a].txt', setup=SETUP, note='The first quarter of 2026, and every one-letter .txt file except a.txt.'),
    [('data', [
        dict(situation='The second half of 2025 (July to December).', setup=SETUP, cmd='echo report_2025_0[7-9].csv report_2025_1[0-2].csv',
             why='Two patterns, because the month has two digits: 07–09 and 10–12.'),
        dict(situation='Q4 of both years.', setup=SETUP, cmd='echo report_202[56]_1?.csv',
             why='[56] = 2025 or 2026; 1? = 10 to 19 (here 10, 11, 12 exist).')]),
     ('dev', [
        dict(situation='notes.txt and Notes.md: match both cases.', setup=SETUP, cmd='echo [nN]otes*',
             why='Linux names are case-sensitive; brackets cover both. Or <code>shopt -s nocaseglob</code>.')]),
     ('qa', [
        dict(situation='Find test files that do NOT start with test_.', setup='touch test_a.py test_b.py helper.py conftest.py', cmd='echo [!t]*.py',
             why='One character that is not t, then anything. (conftest.py starts with c, so it is listed.)')]),
     ('sec', [
        dict(situation='Find files whose name contains a space (they break careless scripts).', setup='touch "my report.txt" ok.txt "q1 data.csv"', cmd='for f in *[[:space:]]*; do echo "[$f]"; done',
             why='[[:space:]] matches the space; brackets in the output show where names begin and end.')]),
    ]
) + cmdcard_u(['creating many names: folders, files, backups', 'sequences with padding: {01..12}', 'two names that share a part: app.conf{,.bak}'],
               ['selecting files that already exist (use wildcards)', 'the list comes from a variable: {1..$n} does not work (use seq, Lesson 3.6)'])(
    'braces', '{ }', 'brace expansion: write every combination',
    'Writes out every item of a comma list or sequence, combined with the text around it. It never looks at the disk, so the names may or may not exist.',
    '{a,b,c}  {1..10}  {01..12}  {a..e}  {1..20..5}  pre{a,b}post', 'safe',
    [('{a,b,c}', 'a list', 'named items: months, environments'),
     ('{1..10}', 'a number sequence', 'numbered files'),
     ('{01..12}', 'zero-padded sequence', 'sortable names'),
     ('{1..20..5}', 'with a step: 1 6 11 16', 'every n-th'),
     ('{z..a}', 'backwards / letters', 'reverse order'),
     ('x{,.bak}', 'empty item: x and x.bak', 'backup copies'),
     ('{a,b}{1,2}', 'combinations: a1 a2 b1 b2', 'grids of names')],
    dict(cmd='echo {jan,feb,mar}_report.csv\necho file{1..10..3}\necho app.conf{,.bak}', note='Braces need no files: they only write text, which echo prints.'),
    [('devops', [
        dict(situation='Create the same folders for three environments.', cmd='mkdir -p {dev,test,prod}/{config,logs} && ls -d */*',
             why='Two brace groups multiply: 3 × 2 = 6 folders in one command.')]),
     ('sys', [
        dict(situation='Back up a config before editing it.', cmd='echo port=80 > app.conf && cp -v app.conf{,.bak}',
             why='<code>app.conf{,.bak}</code> expands to <code>app.conf app.conf.bak</code>: source and destination in one word.')]),
     ('data', [
        dict(situation='Partition folders for every hour of a day.', cmd='mkdir -p events/hour={00..23} && ls events | head -3; ls events | wc -l',
             why='Zero padding keeps the folders in time order: hour=00 … hour=23.')]),
     ('qa', [
        dict(situation='Test data for every combination of browser and language.', cmd='touch result_{chrome,firefox}_{en,hi}.json && ls result_*',
             why='All combinations generated, so no case is forgotten.')]),
    ]
) + cmdcard_u(['scripts: what happens when nothing matches (<code>nullglob</code>)', 'recursive patterns without find (<code>globstar</code>)', '“everything except” (<code>extglob</code>)'],
               ['interactive habits you forget to switch off (they change how every pattern behaves)', 'scripts that must also run in sh (these are bash-only)'])(
    'shopt', 'shopt', 'shell options for globbing',
    'Bash options that change how patterns behave. Switch on with <code>shopt -s name</code>, off with <code>shopt -u name</code>; they last for the current shell or script.',
    'shopt -s nullglob | failglob | dotglob | nocaseglob | globstar | extglob', 'safe',
    [('nullglob', 'no match → the pattern disappears', 'loops in scripts'),
     ('failglob', 'no match → error, command not run', 'strict scripts'),
     ('dotglob', '* also matches hidden files', 'copy a whole folder’s content'),
     ('nocaseglob', 'ignore upper/lower case', 'mixed-case names'),
     ('globstar', '** matches any number of folders', 'recursive selections'),
     ('extglob', '!(p) ?(p) *(p) +(p) @(p) patterns', 'everything except')],
    dict(cmd='shopt -s globstar\nmkdir -p src/a/b && touch src/top.py src/a/b/deep.py\necho **/*.py', note='Without globstar, <code>**</code> acts like <code>*</code> and finds only src/top.py.'),
    [('dev', [
        dict(situation='Count lines of all Python files in the project, any depth.', cmd='shopt -s globstar\nmkdir -p app/core && printf "a\\nb\\n" > app/main.py && printf "c\\n" > app/core/db.py\nwc -l **/*.py',
             why='** walks every folder; for very big trees prefer find (Lesson 7.1).')]),
     ('sys', [
        dict(situation='A loop over log files must do nothing when there are none.', cmd='shopt -s nullglob\nfor f in *.log; do echo "processing $f"; done\necho "done"',
             why='Without nullglob the loop would run once with f="*.log" and try to open a file called *.log.')]),
     ('data', [
        dict(situation='Move everything except CSV and log files into misc/.', setup=SETUP, cmd='shopt -s extglob\nmkdir misc && mv !(*.csv|*.log|misc) misc/ && ls misc',
             why='<code>!(a|b)</code> = not a and not b. extglob must be on its own line before the line that uses it.')]),
     ('devops', [
        dict(situation='Copy a folder’s content including hidden files like .env and .gitignore.', cmd='mkdir -p app2 && touch app2/{main.py,.env,.gitignore} && mkdir -p deploy\nshopt -s dotglob\ncp -v app2/* deploy/',
             why='Without dotglob, .env and .gitignore would be silently left behind.')]),
    ]
) + mistake('for f in $(ls *.txt); do cat $f; done', 'for f in *.txt; do cat "$f"; done',
            'Parsing ls output breaks on names with spaces (my report.txt becomes two words). A glob gives each name as one item; quote the variable.') + undo('If a pattern selects the wrong files…', [
    ('Before:', 'run the same line with <code>echo</code> in front, or <code>ls -d pattern</code>; count with <code>| wc -w</code>.'),
    ('During:', 'use <code>-i</code> with cp, mv and rm, or <code>-v</code> to see each file.'),
    ('After cp:', 'nothing is lost; delete the extra copies.'),
    ('After mv:', 'move them back with the same pattern from the target folder.'),
    ('After rm:', 'no undo (Lesson 3.3). That is why the echo habit matters most here.'),
]) + errors('The errors students see most with patterns. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='ls *.xyz', meaning='Nothing matched, so bash passed the text “*.xyz” unchanged, and ls looked for a file with that exact name.', fix='Check the pattern with <code>ls</code> on the folder; in scripts use <code>nullglob</code> or test with <code>[ -e "$f" ]</code>.'),
    dict(cmd='touch report_2026_01.csv\nls report_2026_0{1..3}.csv', meaning='Braces wrote all three names; only one exists.', fix='Use a wildcard to see what exists: <code>ls report_2026_0[1-3].csv</code>.'),
    dict(cmd='touch a.txt\nls "*.txt"', meaning='The quotes switched globbing off, so ls looked for a file named *.txt.', fix='Do not quote patterns: <code>ls *.txt</code>. Quote variables instead.'),
    dict(cmd='touch "my report.txt"\nf="my report.txt"\nls $f', meaning='Without quotes, the variable was split at the space into “my” and “report.txt”.', fix='<code>ls "$f"</code>.'),
    dict(cmd='shopt -s failglob\necho *.xyz', meaning='With failglob, a pattern that matches nothing stops the command with an error.', fix='That is the point of failglob: make the pattern match, or switch it off with <code>shopt -u failglob</code>.'),
]) + stepper([
    ('1. Describe the files in words', '<p>“2026 reports, January to March.”</p>', 'Behind the screen: nothing yet; you choose the fixed and variable parts.'),
    ('2. Write the pattern', '<p><code>report_2026_0[1-3].csv</code></p>', 'Behind the screen: fixed text + one bracket for the changing digit.'),
    ('3. Test it with echo', '<p><code>echo report_2026_0[1-3].csv</code></p>', 'Behind the screen: bash reads the folder and sorts the matching names.'),
    ('4. Count it', '<p><code>echo report_2026_0[1-3].csv | wc -w</code> → 3</p>', 'Behind the screen: wc counts the words echo printed.'),
    ('5. Use it', '<p><code>cp -v report_2026_0[1-3].csv /media/usb/</code></p>', 'Behind the screen: cp receives three names; it never sees the brackets.'),
]) + qc('You type <code>echo *.log</code> and get <code>*.log</code> back. What does that tell you?', 'No file in the current folder ends in .log, so bash left the pattern unchanged.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def fl(names, hl, note, tone='blue', title='folder: ~/reports'):
    o = label_box(196, 12, 150, 22, [title], 'card', 8.6)
    for k, n in enumerate(names):
        o += label_box(196, 38 + k * 21, 150, 18, [n], 'green' if k in hl else 'card', 8)
    return o + (t(98, 172, note, 8.6, tone, bold=True) if note else '')
NAMES = ['notes.txt', 'report_2025_12.csv', 'report_2026_01.csv', 'report_2026_02.csv', 'report_2026_03.csv', 'report_2026_04.csv']
see = [term(14, 16, 172, 110, ['$ cp report_2026', ('_0[1-3].csv usb/', 'prompt')], title='riya@laptop', size=7.6) + fl(NAMES, [], '') + cap('Riya types a pattern.', '', 'card', y=150, h=34, w=170),
       term(14, 16, 172, 110, ['bash reads', ('the folder…', 'dim')], title='bash', size=7.6) + fl(NAMES, [], '') + cap('Bash reads the folder.', '', 'blue', y=150, h=34, w=170),
       term(14, 16, 172, 110, ['bash checks', ('each name', 'dim')], title='bash', size=7.6) + fl(NAMES, [2, 3, 4], '') + cap('Three names fit the pattern.', '', 'green', y=150, h=34, w=170),
       term(14, 16, 172, 110, ['cp gets:', ('report_2026_01.csv', 'acc'), ('report_2026_02.csv', 'acc'), ('report_2026_03.csv', 'acc'), ('usb/', 'acc')], title='cp', size=7.2) + fl(NAMES, [2, 3, 4], '') + cap('cp receives 4 plain words.', '', 'blue', y=150, h=34, w=170),
       term(14, 16, 172, 110, ['$ ls *.xyz', ('cannot access', 'err'), ("'*.xyz'", 'err')], title='riya@laptop', size=7.6) + fl(NAMES, [], '') + cap('No match: kept as text.', '', 'red', y=150, h=34, w=170)]
def pipe(hl, note, tone='blue'):
    items = [('1 brace  {a,b} {1..3}', 'amber'), ('2 tilde ~  ·  3 $variables  ·  4 $(cmd)', 'card'), ('5 word splitting (spaces)', 'card'), ('6 GLOB  * ? [ ]  (reads the folder)', 'green'), ('7 quote removal → the command starts', 'blue')]
    o = ''.join(label_box(14, 12 + k * 30, 332, 25, [s], tn if k in hl else 'card', 8.4) for k, (s, tn) in enumerate(items))
    return o + t(180, 175, note, 8.8, tone, bold=True)
behind = [pipe([], 'The line goes through bash’s expansion steps.'),
          pipe([3], 'Step 6: glob reads the folder (getdents64).', 'green'),
          pipe([3], 'Each name is compared with the pattern.', 'green'),
          pipe([4], 'Then the command starts with the final list.', 'blue'),
          pipe([3], 'No match: by default the word is left as it is.', 'red')]
two = anim_two('Who expands the pattern?', 'Bash’s expansion steps',
               'A terminal and a folder: bash reads the folder, marks the three names that match report_2026_0[1-3].csv and passes them to cp; with no match the pattern stays as text.',
               'Bash expansion order: braces, tilde, variables, command substitution, word splitting, globbing, quote removal; then the command starts.', see, behind,
               ['Riya types cp with a pattern.',
                'Before cp starts, bash reads the folder.',
                'Three names fit; the others are ignored.',
                'cp gets an ordinary list of names. It cannot tell you used a pattern.',
                'If nothing fits, the pattern itself is passed on, which is why the error shows the star.'],
               ['Bash expands a command line in a fixed order of steps.',
                'Pathname expansion (globbing) is step 6, after variables and splitting.',
                'Matching names are sorted alphabetically.',
                'Quotes are removed last, and the program is started.',
                'Options nullglob and failglob change what happens with no match.'])

b1 = term(14, 14, 332, 100, ['$ ls', ('report_2026_01.csv', 'out')], title='riya@laptop: ~/q3', size=7.6) + cap('Only January exists in this folder.', '', 'card', y=150, h=34)
b2 = term(14, 14, 332, 100, ['$ echo report_2026_0{1..3}.csv', ('report_2026_01.csv report_2026_02.csv', 'acc'), ('report_2026_03.csv', 'acc')], title='riya@laptop: ~/q3', size=7.6) + cap('Braces WRITE all three names anyway.', '', 'amber', y=150, h=34)
b3 = term(14, 14, 332, 100, ['$ echo report_2026_0[1-3].csv', ('report_2026_01.csv', 'acc')], title='riya@laptop: ~/q3', size=7.6) + cap('Brackets FIND only the one that exists.', '', 'green', y=150, h=34)
b4 = term(14, 14, 332, 100, ['$ touch report_2026_0{1..3}.csv', '$ ls', ('report_2026_01.csv report_2026_02.csv', 'out'), ('report_2026_03.csv', 'out')], title='riya@laptop: ~/q3', size=7.6) + cap('So braces are perfect for CREATING names.', '', 'blue', y=150, h=34)
b5 = (t(180, 30, 'Remember', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• {…} writes: use it to create', '• * ? [ ] find: use them to select', '• braces run first, globs later', '• echo shows both'])) + cap('Create with braces, select with wildcards.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario', 'Braces write, wildcards find',
              'Riya’s Q3 folder has only one report so far. The outputs match real runs.',
              'Braces vs brackets', 'In a folder with one file, braces print three names, brackets print only the existing one, and touch with braces creates all three.', [b1, b2, b3, b4, b5],
              ['Only report_2026_01.csv exists.',
               '<code>{1..3}</code> writes three names without looking at the folder.',
               '<code>[1-3]</code> looks at the folder and finds just one.',
               'That is why braces are used with touch and mkdir to create names.',
               'Rule: create with braces, select with wildcards.'],
              hid='scenario-braces')

dx = dissect('Layer by layer: one command line, every expansion',
    'Take <code>cp ~/q/report_{2025,2026}_0[1-3].csv "$DEST"</code>. Open each step to see what bash does to it, with a real output from our build machine.', [
    dict(key='brace', name='1 · Braces', sub='write combinations',
         why='Generate names without typing each.',
         how='{2025,2026} becomes two words.',
         impl='First step of bash’s expansion.', used='mkdir, touch, cp backups.',
         cmd='echo report_{2025,2026}_X'),
    dict(key='tilde', name='2 · Tilde', sub='~ → home',
         why='Short way to write your home folder.',
         how='~ becomes /home/riya.',
         impl='Tilde expansion.', used='Every path to your files.',
         cmd='echo ~/q'),
    dict(key='var', name='3 · Variables', sub='$DEST → its value',
         why='Scripts reuse values.',
         how='"$DEST" is replaced by its value; quotes keep spaces.',
         impl='Parameter expansion.', used='Scripts.',
         cmd='DEST="/media/usb stick"; echo "$DEST"'),
    dict(key='glob', name='6 · Globbing', sub='match existing names',
         why='Select files without typing names.',
         how='Each word with * ? [ ] is matched against the folder.',
         impl='Pathname expansion; reads the folder.', used='Every command.',
         cmd='touch report_2026_0{1..4}.csv; echo report_2026_0[1-3].csv'),
    dict(key='quote', name='7 · Quote removal', sub='then the command',
         why='Quotes were instructions for bash, not part of the data.',
         how='Bash removes the quotes it used and starts the program.',
         impl='Last step before exec.', used='Always.',
         cmd="printf '[%s]\\n' \"a b\" '*.txt'"),
], hint='Bash runs these steps in this order. Click a step.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Who turns the pattern into names?</h2>
  <p>Left: what Riya types and what cp receives. Right: bash’s expansion steps.</p>
''' + two + s1 + dx + hood('Under the hood: globbing reads the folder', 'The real file-related system calls of <code>echo *.txt</code> on our build machine (echo is built into bash, so these are bash’s own calls).',
          "bash -c 'echo *.txt'", 'touch a.txt b.txt', 'openat\\(AT_FDCWD, "\\.",|getdents64',
          '<p>Bash opens the current folder (<code>"."</code>) and reads all its entries with <code>getdents64</code> (get directory entries), then compares each name with the pattern in memory. That is all: the files themselves are never opened.</p>') + qc('In which order does bash do brace expansion and globbing?', 'Braces first (step 1), globbing late (step 6). So <code>{a,b}*.txt</code> first becomes <code>a*.txt b*.txt</code>, then each is matched.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Patterns at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ tar czf q1.tgz', 'prompt'), ('*_0[1-3].csv', 'acc')], title='data', size=6.4, step=12),
              '1. Selecting data files', 'Data engineers pick partitions and periods by name: one month, one quarter, one region.', ['Period', '*pattern', 'exact files']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['*.log *.gz', 'logrotate'], 'amber', 8.6), '2. Log management',
    'Log tools and cleanup jobs select files by patterns such as <code>/var/log/app/*.log</code> (Lesson 18.1).', ['Logs', '*glob', 'rotate']) + '\n' + usecase(
    term(8, 14, 104, 62, [('.gitignore', 'prompt'), ('*.pyc  build/', 'acc')], title='dev', size=6.4, step=12),
    '3. .gitignore and Docker', 'Git, Docker (.dockerignore) and many tools use glob patterns, including <code>**</code>, to choose files.', ['Repo', '*patterns', 'clean commits']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['{dev,prod}', 'configs'], 'blue', 8.6), '4. Environments',
    'DevOps scripts generate folders and files for each environment with braces.', ['Envs', '*braces', 'same layout']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['echo first', 'count'], 'green', 8.6), '5. Safe operations',
    'Before rm, mv or chmod on many files, professionals preview the pattern with echo or ls.', ['Pattern', '*echo', 'then act']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Short pattern tricks. All really run on our build machine.', [
    dict(level='b', title='How many of each type?', scenario='Count CSV and log files in the folder.', setup=SETUP,
         cmd='echo "csv: $(ls *.csv | wc -l)  log: $(ls *.log | wc -l)"',
         explain='Two patterns, two counts, one line.'),
    dict(level='b', title='Only folders', scenario='List the sub-folders, not the files.',
         cmd='mkdir -p a b c && touch f1 f2 && ls -d */',
         explain='A trailing slash in the pattern matches only folders.'),
    dict(level='i', title='Newest of a family', scenario='The latest 2026 report.', setup=SETUP,
         cmd='ls report_2026_*.csv | tail -1',
         explain='Glob results are sorted; with zero-padded months the last one is the newest.'),
    dict(level='i', title='Back up all configs', scenario='Copy every .conf file to .conf.bak.',
         cmd='touch a.conf b.conf && for f in *.conf; do cp "$f" "$f.bak"; done && ls',
         explain='A loop over a glob; quotes keep odd names safe.'),
    dict(level='a', title='Everything except', scenario='List all files except CSV files.', setup=SETUP,
         cmd='shopt -s extglob\necho !(*.csv)',
         explain='extglob’s !( ) inverts a pattern.'),
], extra=build_up('the right pattern for Q1 2026', 'Riya narrows a pattern step by step, testing with echo each time.',
    SETUP, [
    ('echo *.csv | wc -w', 'All CSV files: 18, too many.'),
    ('echo report_2026_*.csv | wc -w', 'Only 2026: 6.'),
    ('echo report_2026_0[1-3].csv', 'Only January to March: exactly the three needed.'),
    ('mkdir -p usb && cp -v report_2026_0[1-3].csv usb/', 'Now use it.'),
])) + which('Choosing the right pattern.', [
    ('Every file of a type', '*.csv', 'Any name, fixed ending.', 'ls * .csv (space).'),
    ('Exactly one character', 'data?.log', 'Fixed width.', 'data*.log also matches data10.'),
    ('A set or range', '0[1-3]', 'One character.', '[01-03] (that is 0,1,2,3).'),
    ('Create many names', '{01..12}', 'No files needed.', 'Using braces to select.'),
    ('Every sub-folder', '**/*.py + globstar', 'Recursive.', 'Forgetting shopt -s globstar.'),
    ('Everything except', '!(*.csv) + extglob', 'Inverts.', 'extglob on the same line.'),
    ('A literal *', '"*" or \\*', 'No expansion.', 'Unquoted * in a message.'),
    ('Loop over files', 'for f in *.txt', 'Safe with spaces.', 'for f in $(ls).'),
]) + keys('Shortcuts for patterns.', [
    ('Tab Tab', 'show all completions for what you typed', 'ls rep⇥⇥'),
    ('Ctrl + x  *', 'expand the glob on the command line before running it', 'rm *.tmp → Ctrl+x * → rm a.tmp b.tmp'),
    ('Alt + *', 'insert all matches of the word before the cursor', 'ls *.csv Alt+*'),
    ('echo pattern', 'preview the list', 'echo *.log'),
    ('| wc -w', 'count matches', 'echo *.log | wc -w'),
    ('shopt', 'show all glob options', 'shopt | grep glob'),
]) + scriptit('archive-quarter.sh', 'Archive one quarter’s reports, with every safety from this lesson: nullglob, a count, and a clear message when nothing matches.',
'''#!/bin/bash
year=${1:-2026}; q=${2:-1}
touch report_2026_{01..06}.csv                      # demo files
case $q in 1) m='0[1-3]';; 2) m='0[4-6]';; 3) m='0[7-9]';; 4) m='1[0-2]';; *) echo "quarter 1-4" >&2; exit 1;; esac
shopt -s nullglob
files=( report_${year}_$m.csv )
if [ ${#files[@]} -eq 0 ]; then echo "no reports for $year Q$q"; exit 0; fi
tar -czf "reports_${year}_Q$q.tgz" "${files[@]}"
echo "archived ${#files[@]} file(s):"; tar -tzf "reports_${year}_Q$q.tgz"''',
'<p>The pattern is built from variables (<code>report_${year}_$m.csv</code>); globbing happens after variable expansion, so it still works. Try quarter 3: “no reports”.</p>') + puzzle_answer('Nothing matched <code>*.xyz</code>. In that case bash, by default, does not remove the word: it passes the text <code>*.xyz</code> unchanged to ls. ls then looks for a file whose name really is “*.xyz”, does not find it, and prints the name it was given. With <code>shopt -s nullglob</code> the word would vanish (ls would list the whole folder); with <code>failglob</code> bash itself would report “no match”.') + qc('Write one pattern for the reports of October to December 2025.', '<code>report_2025_1[0-2].csv</code>') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../03-deleting-safely-rm-rm-r-rm-i-shred-and-why-rm/">Lesson 3.3</a>: why checking a pattern before rm matters.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
