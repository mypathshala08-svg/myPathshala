import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
from linuxkit import *
from _data import APPLOG, ACCESS, CODE, EMP

HOOK = hook('At 9:07 the payment site goes down. The application log has 40,000 lines, the source code has 600 files, and the manager is asking “what happened?”. Scrolling is hopeless. <code>grep -n -i -C 2 "error\\|fatal" app.log</code> shows every problem line, its line number and the two lines around it in one second. grep is the command Linux people type more than almost any other.',
    ['search one file, many files or a whole folder tree for a word or pattern with <code>grep</code>',
     'choose the right option: <code>-i -n -c -v -w -x -o -l -L -r -A -B -C -m -q -h</code>',
     'search for several patterns at once (<code>-e</code>, <code>-E \'a|b\'</code>, <code>-f</code>) and for text with special characters (<code>-F</code>)',
     'use grep in pipelines and scripts, and avoid the mistakes in common notes (<code>-c</code> counts lines, not matches)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the outage at 9:07'),
    ('decide', 'Which option when?', 2, 'the quick chart'),
    ('definition', 'What grep is', 5, 'simple meaning + 4 depths'),
    ('commands', 'grep, by field', 16, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'grep reading line by line'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which grep option? (decide in 5 seconds)', [
    ('Lines containing a word', 'grep word file', 'case-sensitive'),
    ('Ignore upper/lower case', 'grep -i word file', 'Error, ERROR, error'),
    ('Where is it? (line numbers)', 'grep -n word file', 'open it at that line'),
    ('How many lines match?', 'grep -c word file', 'lines, not occurrences'),
    ('Lines WITHOUT the word', 'grep -v word file', 'drop comments, noise'),
    ('The whole word only', 'grep -w main file', 'not mainPage'),
    ('Only the matching text', 'grep -o pattern file', 'extract IPs, emails'),
    ('Search a whole folder', 'grep -rn word dir/', '--include="*.py" to limit'),
    ('Which files contain it?', 'grep -rl word dir/', '-L = files without it'),
    ('Lines around the match', 'grep -C 2 word file', '-A after, -B before'),
    ('Several words at once', "grep -E 'ERROR|FATAL' file", 'or -e ERROR -e FATAL'),
    ('Just yes / no in a script', 'grep -q word file && …', 'exit code 0 / 1 / 2'),
])

cmap = concept_map(
    [('3.5', 'Viewing files', 'cat, less, head, tail'), ('5.3', 'Pipes', 'cmd | grep pattern'), ('5.4', 'Exit codes', 'grep -q in if and &&')],
    ['grep pattern file: matching lines', 'everyday options: -i -n -c -v -w -x -o -m', 'many files and folders: -r -R -l -L -h -H --include --exclude', 'context: -A -B -C', 'several patterns: -e, -E, -f, -F; exit codes 0 1 2'],
    [('6.6', 'Regular expressions', 'the full pattern language'), ('6.4', 'sed', 'search and replace'), ('6.5', 'awk', 'search and calculate'), ('13.3', 'Log analysis', 'grep in real log one-liners')],
    'grep is the “find” of text: it does not change anything, it shows you where things are. Every later text tool builds on it.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ grep -n -i "error\\|fatal" app.log', ('4:… ERROR db connection refused', 'err'), ('6:… ERROR db connection refused', 'err'), ('8:… error payment timeout', 'err'), ('9:… FATAL out of memory', 'err'), '$ grep -c -i error app.log', ('3', 'acc')], title='riya@app01: ~', size=7.2, step=15)
      + t(352, 36, 'One search, every clue:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• -n line numbers', '• -i any case', '• -c how many lines', '• -C 2 lines around', '• -r a whole folder'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The outage at 9:07</h2>
  <div class="story">
''' + puzzle('A log line says <code>ERROR ERROR disk and network</code>. Riya runs <code>grep -c ERROR app.log</code> on a file where that is the only matching line. Does grep print 1 or 2? And what about <code>grep -o ERROR app.log | wc -l</code>?') + '''
    <p class="narration">The payment site is down. Riya has SSH access to the server and one file: app.log, thousands of lines long.</p>
''' + scene('A terminal: grep -n -i for error or fatal prints four numbered problem lines from app.log; grep -c -i error prints 3.', sc,
            'grep reads every line and prints <tspan font-weight="700" class="s-acc">only the ones that match</tspan>.') + '''
A> Don’t scroll. Ask the file a question: “show me every line with error or fatal, any case, with line numbers”.
R> Four lines: two database errors, a payment timeout, then out of memory. So the database failed first?
K> Use <code>-B 3</code> to see what happened just before each error. Then search the code with <code>grep -rn</code> to find where that message is printed.
A> Today: grep and every option you will really use, explained, then used by admins, developers, DBAs, data engineers, DevOps, security and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A highlighter pen moving down a printed page, marking only the lines that contain the word ERROR; the marked lines are copied onto a short sheet.">'
       + label_box(20, 14, 250, 150, ['a long printed log', 'INFO server started', 'ERROR db refused', 'INFO health 200', 'ERROR db refused', 'INFO retry'], 'card', 8.4)
       + label_box(372, 44, 250, 90, ['grep ERROR', 'ERROR db refused', 'ERROR db refused'], 'amber', 8.6)
       + arrow(272, 88, 368, 88)
       + t(320, 186, 'grep = a highlighter that copies only the marked lines.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('grep at four depths', [
    ('v', 'No jargon: a highlighter', '      <p>Think of reading a long printout with a highlighter.</p>' + pic + '''
      <ul>
        <li>You move down the page line by line and mark every line with the word you want.</li>
        <li>Then you copy only the marked lines onto a short sheet: that is grep’s output.</li>
        <li>The original page is never changed.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>grep ERROR app.log</code>: lines containing ERROR.</li>
        <li><code>grep -i error app.log</code>: any case. <code>grep -n</code> adds line numbers, <code>grep -c</code> counts lines.</li>
        <li><code>grep -v INFO app.log</code>: everything except INFO lines.</li>
        <li><code>grep -rn TODO src/</code>: search every file under a folder.</li>
        <li><code>ps aux | grep nginx</code>: search another command’s output.</li>
      </ul>'''),
    ('i', 'Patterns, files and exit codes', '''      <ul>
        <li>The pattern is a <b>regular expression</b>: <code>^</code> start of line, <code>$</code> end, <code>.</code> any character, <code>[0-9]</code> a digit (Lesson 6.6). Quote it: <code>grep '^ERROR' file</code>.</li>
        <li>Basic grep treats <code>| + ? ( ) {}</code> as normal characters; use <code>grep -E</code> (extended) for <code>'ERROR|FATAL'</code>, or <code>\\|</code> in basic mode. <code>-F</code> means “fixed string”: no special characters at all.</li>
        <li>With several files grep prefixes each line with the file name (<code>-h</code> hides it, <code>-H</code> forces it).</li>
        <li>Exit code: 0 = found, 1 = not found, 2 = error. That is what makes <code>grep -q</code> useful in scripts.</li>
        <li><code>-c</code> counts <b>matching lines</b>; to count every occurrence use <code>grep -o … | wc -l</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: fast search and encodings', '''      <ul>
        <li>GNU grep reads big blocks, not lines, and uses the Boyer-Moore algorithm to skip ahead: a fixed string search can check far fewer bytes than the file has. It only finds line boundaries around a match.</li>
        <li>Regular expressions are compiled into an automaton (DFA) before reading, so a complex pattern costs little extra per line.</li>
        <li>Files containing NUL bytes are treated as <b>binary</b>: grep prints “binary file matches” instead of the line. <code>-a</code> treats them as text.</li>
        <li><code>-i</code> and character classes depend on the <b>locale</b> (<code>LANG</code>); <code>LC_ALL=C grep</code> is byte-based and often faster.</li>
        <li><code>-P</code> uses Perl-compatible regex (<code>\\d</code>, lookaheads). Faster modern alternatives: <code>ripgrep (rg)</code> respects .gitignore and searches in parallel.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>grep: searching inside files</h2>
''' + def_block(
    '<code>grep</code> searches its input files (or standard input) for lines that match a pattern, a <b>regular expression</b>, and prints the matching lines. Options change what is matched (case, whole words, inverted), what is printed (line numbers, counts, file names, only the match, context lines) and which files are searched (recursive, include/exclude). It never modifies the files.',
    'Show me the lines that contain this.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Pattern', 'What you search for: a word, or a regular expression.'),
    ('Regular expression', f'A pattern language: ^ $ . * [ ] … {gl("regular-expression-regex", "Glossary →")}'),
    ('Match', 'A line (or part of a line) that fits the pattern.'),
    ('Basic / extended regex', f'grep vs grep -E: which characters are special. {gl("basic-vs-extended-regex-bre-ere", "Glossary →")}'),
    ('Recursive', 'Search a folder and all folders inside it (-r).'),
    ('Context', 'Lines just before or after a match (-B, -A, -C).'),
    ('Exit status', '0 found, 1 not found, 2 error.'),
    ('grep', f'The command itself. {gl("grep", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('grep', 'g/re/p', 'The ed editor command “global / regular expression / print”: Ken Thompson turned it into a program in 1973.'),
    ('egrep / fgrep', 'extended / fixed grep', 'Old names for grep -E and grep -F (now deprecated: they print a warning).'),
    ('-v', 'invert', 'From “reVerse”.'),
    ('-w / -x', 'word / line (exact)', 'Whole word / whole line must match.'),
    ('-A -B -C', 'after, before, context', 'Lines around a match.'),
    ('-o', 'only matching', 'Print just the matched part.'),
    ('-l / -L', 'files with / without matches', '“list”.'),
    ('rg', 'ripgrep', 'A modern, faster grep.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Basic', '<code>grep word file</code>'),
    ('Any case + line numbers', '<code>grep -in word file</code>'),
    ('Whole folder', '<code>grep -rn word dir/</code>'),
    ('Several words', "<code>grep -E 'a|b' file</code>"),
    ('Count lines', '<code>grep -c word file</code>'),
    ('In scripts', '<code>grep -q word file &amp;&amp; …</code>'),
]) + '\n' + lv + didyou('grep was written by Ken Thompson in one night in 1973 at Bell Labs, because Doug McIlroy wanted to search a text too large for the ed editor. The name is the ed command <code>g/re/p</code>: on every line (g), find the regular expression (re), print it (p). It is so common that “to grep” is now an English verb.') + '''
EXAM> “How do you search for a word in all files under a directory, ignoring case, showing line numbers?” → grep -rin word dir/ (add --include="*.conf" to limit the files, -l to list only file names, -w for whole words).
''' + qc('What is the difference between <code>grep -c ERROR app.log</code> and <code>grep -o ERROR app.log | wc -l</code>?', '-c counts <b>lines</b> that contain ERROR. -o prints every <b>occurrence</b> on its own line, so wc -l counts occurrences. A line with ERROR twice counts 1 for -c and 2 for the second.') + mistake('“grep stands for Global Expression Regular Print”   ·   “grep -c: how many times a pattern appears”   ·   “grep -v: displays the number of lines that didn’t match”   ·   “grep -e: matches in a case-sensitive manner”',
    'grep = global / regular expression / print · -c counts matching LINES · -v prints the non-matching LINES (-vc would count them) · -e marks a pattern (useful for several patterns or one starting with -); case is controlled by -i',
    'Four short descriptions that are common in class notes. Real runs below show each option’s actual behaviour.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Every grep option you will use, in one table</h2>
''' + table(['Option', 'What it does', 'When to use it'], [
    ['<code>-i</code>', 'ignore case', 'Error / ERROR / error, user names'],
    ['<code>-n</code>', 'show line numbers', 'jump to the line in an editor'],
    ['<code>-c</code>', 'count matching lines', 'how many errors today'],
    ['<code>-v</code>', 'invert: non-matching lines', 'remove comments, noise'],
    ['<code>-w</code> / <code>-x</code>', 'whole word / whole line', 'main not mainPage / exact values'],
    ['<code>-o</code>', 'only the matched text', 'extract IPs, IDs, emails'],
    ['<code>-m N</code>', 'stop after N matches', 'first error only; huge files'],
    ['<code>-r</code> / <code>-R</code>', 'recursive (‑R follows symlinks)', 'source code, /etc'],
    ['<code>-l</code> / <code>-L</code>', 'file names with / without a match', 'which files to edit'],
    ['<code>-h</code> / <code>-H</code>', 'hide / show file names', 'clean output / one file'],
    ['<code>--include</code> / <code>--exclude</code> / <code>--exclude-dir</code>', 'limit files searched', '*.py only; skip .git, node_modules'],
    ['<code>-A N</code> / <code>-B N</code> / <code>-C N</code>', 'N lines after / before / around', 'what led to an error'],
    ['<code>-e P</code> / <code>-f file</code>', 'one more pattern / patterns from a file', 'several words; a blocklist'],
    ['<code>-E</code> / <code>-F</code> / <code>-P</code>', 'extended / fixed string / Perl regex', 'a|b; text with ( . * ); \\d'],
    ['<code>-q</code> / <code>-s</code>', 'quiet (exit code only) / no file errors', 'scripts'],
    ['<code>--color=auto</code>', 'highlight matches', 'usually on by default (alias)'],
], minw=620) + qc('You need the names of all .conf files under /etc that mention “Listen”. Which options?', '<code>grep -rl --include="*.conf" Listen /etc 2&gt;/dev/null</code>') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>grep explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 (GNU grep 3.11) with the same small sample files: <code>app.log</code> (10 lines), <code>access.log</code> (web log), <code>employees.csv</code> and a tiny <code>src/</code> project.</p>
''' + cmdcard_u(['finding lines in one file: logs, configs, CSVs', 'filtering another command’s output (… | grep)', 'quick counts and yes/no checks'],
               ['changing text (use sed, Lesson 6.4)', 'calculations on columns (use awk, Lesson 6.5)', 'finding files by name (use find, Lesson 7.1)'])(
    'grep', 'grep', 'global / regular expression / print',
    'Prints every line of the input that matches the pattern. Combine options freely: <code>grep -inw</code>.',
    "grep [OPTIONS] 'PATTERN' [FILE...]   ·   command | grep 'PATTERN'", 'safe',
    [('grep ERROR app.log', 'lines containing ERROR', 'basic search'),
     ('-i', 'ignore case', 'error/ERROR'),
     ('-n', 'line numbers', 'locate'),
     ('-c', 'count matching lines', 'statistics'),
     ('-v', 'lines that do NOT match', 'filter out'),
     ('-w', 'whole word', 'exact names'),
     ('-o', 'only the match', 'extract'),
     ('-m 1', 'first match only', 'quick check')],
    dict(setup=APPLOG, cmd="grep ERROR app.log\ngrep -in error app.log\ngrep -c -i error app.log", note='The second command found the lowercase “error” line too, with line numbers; the count is 3 lines.'),
    [('sys', [
        dict(situation='Which users have bash as their login shell?', cmd="grep '/bin/bash$' /etc/passwd | cut -d: -f1",
             why='<code>$</code> anchors the pattern at the end of the line, so only the shell field matches.'),
        dict(situation='Show a config file without comments and blank lines.', cmd="printf '# main config\\nport=8080\\n\\n# log level\\nlevel=info\\n' > app.conf\ngrep -v -e '^#' -e '^$' app.conf",
             why='-v with two patterns removes both comment lines and empty lines: the real settings remain.')]),
     ('dev', [
        dict(situation='Is the function named exactly main used, not mainPage?', cmd="printf 'main()\\nmainPage()\\nrun main now\\n' > code.txt\ngrep -n main code.txt\necho ---\ngrep -nw main code.txt",
             why='-w requires word boundaries on both sides, so mainPage is skipped.')]),
     ('devops', [
        dict(situation='The first fatal error after a deploy, nothing more.', setup=APPLOG, cmd="grep -m 1 -n -E 'ERROR|FATAL' app.log",
             why='-m 1 stops reading at the first match: instant on multi-GB logs.')]),
     ('data', [
        dict(situation='All employees in Pune from a CSV (city is a whole field).', setup=EMP, cmd="grep ',Pune,' employees.csv",
             why='Including the commas matches the field, not “Pune” inside another word. For real column logic use awk (6.5).')]),
     ('web', [
        dict(situation='How many requests failed with 404 or 500?', setup=ACCESS, cmd="grep -c -E '\" (404|500) ' access.log",
             why='The pattern includes the quote and space around the status, so a 404 inside a URL or size does not match.')]),
     ('sec', [
        dict(situation='Failed logins in an auth log (the real command on your server).', cmd="sudo grep -i 'failed password' /var/log/auth.log | tail -n 3",
             typical='Nov  6 09:12:01 web01 sshd[2211]: Failed password for root from 185.220.101.4 port 51122 ssh2\nNov  6 09:12:04 web01 sshd[2213]: Failed password for root from 185.220.101.4 port 51130 ssh2\nNov  6 09:12:09 web01 sshd[2215]: Failed password for invalid user admin from 185.220.101.4 port 51144 ssh2',
             why='auth.log is readable only by root/adm. Many lines from one IP = a brute-force attack (Lesson 19.3).')]),
    ],
    anat=anatomy([('grep', 'cmd', 'command'), ('-in', 'opt', 'ignore case + line numbers'), ("'error'", 'arg', 'pattern (quoted)'), ('app.log', 'arg', 'file(s)')], 'Always quote the pattern: the shell must not touch * ? [ ] $ or spaces.')
) + cmdcard_u(['searching every file of a project, /etc or a log folder', 'finding which files to edit (-l)', 'code reviews: TODO, passwords, deprecated calls'],
               ['huge trees with node_modules or .git (exclude them, or use rg)', 'binary files (use strings | grep)'])(
    'grepr', 'grep -r', 'search folders',
    'Searches every file under a folder. Each line is prefixed with the file name. <code>-l</code> prints only file names; <code>--include</code>/<code>--exclude</code>/<code>--exclude-dir</code> limit what is searched.',
    "grep -rn 'PATTERN' DIR/   ·   grep -rl … · grep -r --include='*.py' …", 'safe',
    [('-r', 'recursive (does not follow symlinks)', 'projects'),
     ('-R', 'recursive, follows symlinks', '/etc with links'),
     ('-l / -L', 'only names of files with / without a match', 'what to fix'),
     ("--include='*.py'", 'only these files', 'one language'),
     ("--exclude-dir=.git", 'skip folders', 'speed, noise'),
     ('-h', 'no file names', 'clean extraction'),
     ('-s', 'no “Permission denied” messages', 'system folders')],
    dict(setup=CODE, cmd="grep -rn TODO src/\ngrep -rl --include='*.py' def src/", note='Every match shows file:line:text. The second command lists only Python files that define a function.'),
    [('dev', [
        dict(situation='Find all TODO and FIXME notes before a release.', setup=CODE, cmd="grep -rn -E 'TODO|FIXME' src/",
             why='One pass over the whole project; the file:line format is clickable in most editors.')]),
     ('sec', [
        dict(situation='Hard-coded passwords or keys in the code (hidden .env files included).', setup=CODE, cmd="grep -rn -i -E 'password|api_key|secret' src/",
             why='grep -r also reads hidden files like .env. Secret scanners in CI (gitleaks, trufflehog) work on the same idea.')]),
     ('sys', [
        dict(situation='Which config files in /etc mention a host name? (errors hidden)', cmd="grep -rls 'localhost' /etc | head -n 5",
             why='-s suppresses “Permission denied” for files a normal user cannot read; -l keeps the output short.')]),
     ('qa', [
        dict(situation='Which test files have no assert at all?', setup=CODE + "\nprintf 'def test_x():\\n    pass\\n' > src/tests/test_empty.py", cmd="grep -rL assert src/tests/",
             why='-L lists files that do NOT contain the pattern: empty tests that always pass.')]),
    ]
) + cmdcard_u(['understanding what led to an error, or what happened right after', 'reading stack traces', 'quick incident reports'],
               ['very large context (use less +/pattern or a log tool)'])(
    'context', 'grep -A · -B · -C', 'context lines',
    'Prints N lines After, Before, or around (Context) each match. Groups of lines are separated by <code>--</code>.',
    'grep -A N | -B N | -C N  PATTERN FILE', 'safe',
    [('-A 2', '2 lines after each match', 'what followed'),
     ('-B 3', '3 lines before', 'what caused it'),
     ('-C 1', '1 line before and after', 'overview'),
     ('-n with context', 'match lines use :, context lines use -', 'tell them apart'),
     ('--group-separator=…', 'change the -- line', 'reports')],
    dict(setup=APPLOG, cmd="grep -n -B 1 FATAL app.log\necho ===\ngrep -n -A 1 'connection refused' app.log", note='With -n, matching lines show <code>9:</code> and context lines show <code>8-</code>. Groups are separated by <code>--</code>.'),
    [('devops', [
        dict(situation='A Java/Python stack trace: the error and the 3 lines after it.', cmd="printf 'INFO ok\\nERROR NullPointerException\\n  at Order.pay(Order.java:42)\\n  at Api.post(Api.java:17)\\nINFO next\\n' > svc.log\ngrep -A 2 ERROR svc.log",
             why='The lines after the exception name show where in the code it happened.')]),
     ('dba', [
        dict(situation='What did the database log say right before a crash?', cmd="printf 'checkpoint complete\\nautovacuum started\\nout of shared memory\\nserver process terminated\\n' > pg.log\ngrep -B 2 terminated pg.log",
             why='-B shows the warning signs: here memory ran out just before the crash.')]),
    ]
) + cmdcard_u(['searching for any of several words at once', 'text full of special characters: IPs, prices, ( ) [ ]', 'large lists of patterns (blocklists, IDs)'],
               ['complicated logic (use awk)'])(
    'multi', 'grep -e · -E · -f · -F', 'several patterns, special text',
    '<code>-e</code> adds a pattern (repeatable). <code>-E</code> enables extended regex, so <code>|</code> means OR. <code>-f file</code> reads one pattern per line. <code>-F</code> treats patterns as plain text, so <code>.</code> or <code>(</code> are not special.',
    "grep -e A -e B file   ·   grep -E 'A|B' file   ·   grep -f patterns.txt file   ·   grep -F 'a.b(1)' file", 'safe',
    [('-e A -e B', 'A or B', 'two words'),
     ("-E 'A|B|C'", 'extended regex OR', 'several words'),
     ("'A\\|B'", 'OR in basic grep (GNU)', 'without -E'),
     ('-f list.txt', 'patterns from a file', 'blocklists'),
     ('-F', 'fixed strings, no regex', 'IPs, paths, prices'),
     ('-x', 'whole line must match', 'exact IDs'),
     ('-P', 'Perl regex: \\d, lookarounds', 'advanced')],
    dict(setup=APPLOG, cmd="grep -c -E 'ERROR|FATAL' app.log\ngrep -c 'ERROR|FATAL' app.log\ngrep -c 'ERROR\\|FATAL' app.log", note='Without -E, the | is a normal character: grep searched for the text “ERROR|FATAL” and found 0 lines.', expect='any'),
    [('sec', [
        dict(situation='Check an access log against a list of blocked IPs.', setup=ACCESS, cmd="printf '185.220.101.4\\n45.9.20.1\\n' > blocked.txt\ngrep -c -F -f blocked.txt access.log",
             why='-f reads the list; -F makes the dots literal (otherwise 185.220.101.4 would also match 185x220…).')]),
     ('data', [
        dict(situation='Rows for an exact list of employee IDs.', setup=EMP, cmd="printf '102\\n105\\n' > ids.txt\ngrep -E \"^($(paste -sd'|' ids.txt)),\" employees.csv",
             why='paste builds 102|105; ^( ), anchors it to the first column, so 1102 would not match.')]),
     ('dev', [
        dict(situation='Search for text with special characters, e.g. a method call.', cmd="printf 'total = price*qty\\ntotal = price + qty\\n' > calc.py\ngrep -F 'price*qty' calc.py\ngrep -c 'price*qty' calc.py",
             why='As a regex, * means “repeat the previous character”, so the second search looks for “pric” followed by any number of e’s and “qty”, and finds 0 lines. -F searches the text exactly.', expect='any')]),
    ]
) + cmdcard_u(['scripts that act on “found / not found”', 'monitoring checks', 'conditions in cron jobs and CI'],
               ['when you need the matching lines themselves'])(
    'gq', 'grep -q', 'quiet: answer with the exit code',
    'Prints nothing and exits with 0 as soon as a match is found, 1 if none, 2 on error. Perfect for <code>if</code> and <code>&amp;&amp;</code>/<code>||</code> (Lesson 5.4).',
    "grep -q 'PATTERN' FILE && … || …   ·   if grep -q …; then …; fi", 'safe',
    [('-q', 'quiet; exit code only', 'conditions'),
     ('-s', 'no error messages for missing files', 'optional files'),
     ('exit 0 / 1 / 2', 'found / not found / error', 'know the difference'),
     ('-qx', 'whole-line exact check', 'a value is present')],
    dict(setup=APPLOG, cmd="grep -q FATAL app.log; echo \"FATAL: $?\"\ngrep -q PANIC app.log; echo \"PANIC: $?\"\ngrep -q x /nope 2>/dev/null; echo \"missing file: $?\"", note='0, 1 and 2: found, not found, error.'),
    [('devops', [
        dict(situation='Alert only if the log contains FATAL.', setup=APPLOG, cmd="grep -q FATAL app.log && echo 'ALERT: fatal error in app.log'",
             why='No output to parse; the exit code decides.')]),
     ('sys', [
        dict(situation='Add a line to a config only if it is not there yet (idempotent).', cmd="printf 'port=8080\\n' > app.conf\nfor i in 1 2; do grep -qx 'level=info' app.conf || echo 'level=info' >> app.conf; done\ncat app.conf",
             why='Run twice, added once. Configuration scripts must be safe to re-run.')]),
    ]
) + mistake("ps aux | grep java | wc -l", "pgrep -c java   ·   or   ps aux | grep '[j]ava' | wc -l",
            'grep’s own command line contains “java”, so it matches itself (Lesson 5.3).') + undo('grep never changes files, but a few habits save time.', [
    ('Too much output:', 'add <code>-m 5</code>, <code>| head</code>, <code>-l</code> or <code>-c</code>.'),
    ('“binary file matches”:', 'the file contains NUL bytes. Use <code>-a</code> to treat it as text or <code>strings file | grep …</code>.'),
    ('Slow on a huge project:', '<code>--exclude-dir=.git --exclude-dir=node_modules</code>, <code>LC_ALL=C</code>, or ripgrep (<code>rg</code>).'),
    ('Pattern starts with -:', '<code>grep -e -v file</code> or <code>grep -- -v file</code>.'),
]) + errors('grep errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='grep root /nope/file', meaning='The file does not exist. Exit 2 = error (not “not found”).', fix='Check the path; add -s to hide such messages in scripts.'),
    dict(cmd="grep 'a[' /etc/hostname", meaning='An unclosed bracket is an invalid regular expression.', fix='Close it, escape it (<code>a\\[</code>) or use <code>-F</code>.'),
    dict(cmd='grep -r root /etc/ssl/private', meaning='Permission denied: a normal user cannot read that folder.', fix='<code>-s</code> to hide, or sudo if you really need it.'),
    dict(cmd="printf 'a\\0b' > bin.dat; grep a bin.dat", meaning='Not an error: grep found a match in a binary file and only says so.', fix='<code>grep -a</code>, or <code>strings bin.dat | grep …</code>.'),
    dict(cmd='grep -c PANIC /etc/hostname', meaning='0 matching lines; exit status 1 means “not found”, not a failure of grep.', fix='Nothing to fix; in scripts treat 1 differently from 2.'),
]) + qc('Write a command that shows, with line numbers, every line of app.log containing ERROR or FATAL in any case, plus 1 line before each.', "<code>grep -n -i -B 1 -E 'error|fatal' app.log</code>") + '''
'''

SCREENS = screens_block('Real terminal screens: grep highlights the match', 'In a real terminal grep colours the matching text (Ubuntu sets <code>--color=auto</code>). Riya searches the log and then the code.',
    "printf '%s\\n' 'PS1=\"riya@laptop:~/lab\\$ \"' 'alias grep=\"grep --color=auto\"' > ~/.mprc\n" + APPLOG, 'bash --rcfile ~/.mprc', [
    ("grep -n -i 'error' app.log  Enter", "\"grep -n -i 'error' app.log\" Enter", ': three lines; in your terminal the word “error” is shown in red.'),
    ("grep -c FATAL app.log  Enter", "C-l 'grep -c FATAL app.log' Enter", ': just the count.'),
], 72, 8, hid='screens', what='bash and grep')

cards = cards + SCREENS + '</section>\n'

# ---------------------------------------------------------------- 5. animations
LINES = ['09:00 INFO  server started', '09:01 WARN  disk 81%', '09:02 ERROR db refused', '09:02 INFO  retrying', '09:04 error payment timeout', '09:05 FATAL out of memory']
def scan(k, hits, note, tone):
    o = ''
    for i, ln in enumerate(LINES):
        tn = 'amber' if i == k else ('green' if i in hits and i < k else 'card')
        o += label_box(14, 8 + i * 22, 210, 19, [ln], tn, 7.6)
    out = [LINES[i] for i in hits if i <= k]
    o += label_box(236, 8, 114, 130, ['output'] + [s[6:20] for s in out], 'blue', 7.2)
    return o + t(180, 160, note, 8.4, tone, bold=True)
frames = [scan(0, [2, 4, 5], 'Line 1: no “error” (any case) → skip.', 'violet'),
          scan(2, [2, 4, 5], 'Line 3 matches → printed.', 'green'),
          scan(4, [2, 4, 5], 'Line 5: “error” in lowercase; -i matches it.', 'green'),
          scan(5, [2, 4, 5], 'Line 6: FATAL only if the pattern includes it.', 'amber')]
s1 = anim_one('Animated example', "grep -i -E 'error|fatal' app.log",
              'grep reads the file one line at a time and keeps only the lines that match.',
              'Line by line', 'Six log lines; a highlight moves down; matching lines are copied into an output box.', frames,
              ['Each line is tested against the pattern.', 'A match is printed at once.', '-i makes upper and lower case equal.', 'With -E, FATAL is the second alternative.'], hid='scenario-grep')

dx = dissect('Layer by layer: grep -rn TODO src/',
    'What happens when you search a folder. Each layer has a real command and output from our build machine.', [
    dict(key='walk', name='Walk the folder', sub='every file under src/',
         why='-r means “look inside folders too”.',
         how='grep opens folders and lists their entries, depth first.',
         impl='openat + getdents64.', used='Projects, /etc.',
         setup=CODE, cmd='find src -type f | sort'),
    dict(key='read', name='Read in blocks', sub='not line by line',
         why='Speed.',
         how='grep reads big chunks (e.g. 96 KB) and searches the bytes.',
         impl='read(fd, buf, 98304).', used='Huge logs.',
         cmd="seq 1 200000 > big.txt; grep -c 199999 big.txt"),
    dict(key='match', name='Match', sub='fast string search',
         why='Find the pattern without checking every byte.',
         how='Boyer-Moore skips ahead; regex runs as an automaton.',
         impl='GNU grep DFA + kwset.', used='Every search.',
         cmd="echo 'a TODO here' | grep -o TODO"),
    dict(key='line', name='Find the line', sub='only around a match',
         why='Print the whole line.',
         how='Look backwards and forwards for \\n from the match.',
         impl='Line numbers counted with -n.', used='Output.',
         setup=CODE, cmd='grep -n TODO src/app/main.py'),
    dict(key='exit', name='Exit code', sub='0 1 2',
         why='Scripts need a yes/no.',
         how='0 if anything matched, 1 if not, 2 on error.',
         impl='Even with -q.', used='if, &&, CI.',
         setup=CODE, cmd='grep -rq TODO src/; echo $?'),
], hint='From the folder to the exit code. Click a layer.')

HOOD = hood('Under the hood: grep reads big blocks', 'strace shows grep opening the file and reading it in large chunks, then writing only the matching lines.',
    'grep ERROR app.log', setup=APPLOG, show='openat.*app\\.log|^read\\(3|^write\\(1', start='openat.*app\\.log')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>grep reading line by line</h2>
''' + s1 + dx + HOOD + qc('Why is <code>grep -m 1</code> fast even on a 10 GB log?', 'It stops reading as soon as the first match is printed.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>grep at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ grep -C2 ERR', 'prompt'), ('app.log', 'acc')], title='on-call', size=6.4, step=12),
              '1. Incident response', 'The first command in most incidents: grep the logs for errors with context and timestamps.', ['Alert', '*grep -C', 'cause']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['grep -rn', 'TODO'], 'blue', 8.6), '2. Code search and review',
    'Developers find usages, TODOs and deprecated calls across a repository (git grep does the same inside git).', ['Repo', '*grep -r', 'files:lines']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['grep -i', 'password'], 'red', 8.6), '3. Security audits',
    'Secret scanning, failed logins, suspicious IPs: grep with -i, -E and -f lists.', ['Logs/code', '*grep', 'findings']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['grep -q', '&& alert'], 'green', 8.6), '4. Monitoring and scripts',
    'Health checks and cron jobs use grep -q exit codes to decide whether to alert.', ['Check', '*exit code', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['grep ,Pune,', 'csv'], 'violet', 8.6), '5. Quick data filters',
    'Data engineers filter rows of CSV and JSON lines before loading or before writing a real query.', ['File', '*grep', 'subset']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Count errors', scenario='How many lines mention error in any case?', setup=APPLOG,
         cmd="grep -ci error app.log", explain='-c counts lines, -i ignores case.'),
    dict(level='b', title='Lines starting with H (from your notes)', scenario='Headings or sections starting with H.',
         cmd="printf 'Hello\\nhi\\nHost=db01\\n' > f1.txt; grep '^H' f1.txt", explain='^ = start of line.'),
    dict(level='i', title='Unique IPs that got 401', scenario='Who is being refused?', setup=ACCESS,
         cmd="grep '\" 401 ' access.log | grep -oE '^[0-9.]+' | sort -u", explain='-o extracts just the IP at the start of the line.'),
    dict(level='i', title='Every occurrence, not every line', scenario='Count each ERROR, even two on one line (the puzzle).', setup=APPLOG,
         cmd="echo 'ERROR ERROR twice' >> app.log; grep -c ERROR app.log; grep -o ERROR app.log | wc -l", explain='3 lines, 4 occurrences.'),
    dict(level='a', title='Errors per hour', scenario='When did the problems happen?', setup=APPLOG,
         cmd="grep -iE 'error|fatal' app.log | grep -oE ' [0-9]{2}:' | sort | uniq -c", explain='Extract the hour, then count (Lesson 6.2).'),
], extra=build_up('an incident summary from a log', 'Riya builds the 9:07 summary one step at a time.', APPLOG, [
    ("grep -n -i -E 'error|fatal' app.log", '1. Every problem line with its number.'),
    ("grep -i -E 'error|fatal' app.log | grep -v -i 'payment'", '2. Hide the payment timeout (a separate issue).'),
    ("grep -c 'connection refused' app.log", '3. How often did the database refuse?'),
    ("grep -n -B 2 FATAL app.log", '4. What happened just before the crash?'),
])) + which('Choosing the right grep form.', [
    ('One file, one word', 'grep word file', 'Simple.', 'Opening the file and scrolling.'),
    ('Any case', 'grep -i', 'Catches all spellings.', 'Searching twice.'),
    ('Count lines', 'grep -c', 'Fast.', 'grep | wc -l (same, one more process).'),
    ('Count occurrences', 'grep -o | wc -l', 'Exact.', 'grep -c (counts lines).'),
    ('A folder', 'grep -rn --include', 'Targeted.', 'cat */* | grep.'),
    ('Several words', "grep -E 'a|b'", 'One pass.', "grep 'a|b' (literal |)."),
    ('Text with . * ( )', 'grep -F', 'Exact.', 'Unescaped regex.'),
    ('Scripts', 'grep -q', 'Exit code.', 'Parsing output.'),
]) + keys('Shortcuts and handy forms.', [
    ('--color=auto', 'highlight matches (often an alias already)', "alias grep='grep --color=auto'"),
    ('grep -rn … | less -R', 'scroll with colours', 'grep --color=always -rn x . | less -R'),
    ('git grep', 'search a git repository fast', 'git grep -n TODO'),
    ('rg', 'ripgrep: faster, respects .gitignore', 'rg -n TODO'),
    ('zgrep', 'grep inside .gz files', 'zgrep ERROR app.log.1.gz'),
    ('Ctrl + R', 'find a previous grep command', 'Ctrl+R grep'),
]) + scriptit('log-check.sh', 'A small monitoring script: count problems, show the first fatal line with context, and exit non-zero so cron or CI can alert.',
APPLOG + '''
log=app.log
errors=$(grep -ci 'error' "$log")
if grep -q FATAL "$log"; then
  echo "FATAL found ($errors error lines). First one:"
  grep -n -m 1 -B 1 FATAL "$log"
  exit 2
fi
echo "OK: $errors error lines, no FATAL"''',
'<p>The heredoc at the top only creates the demo log; on a server, point <code>log=</code> at your real file.</p>', expect='any') + puzzle_answer('<code>grep -c ERROR</code> prints <b>1</b>: it counts matching <b>lines</b>. <code>grep -o ERROR | wc -l</code> prints <b>2</b>: -o prints every occurrence on its own line. Many notes describe -c as “how many times the pattern appears”; real runs show it is the number of lines.') + qc('A script must check that /etc/hosts contains the exact line <code>10.0.0.5 db01</code>. Which grep options?', "<code>grep -qxF '10.0.0.5 db01' /etc/hosts</code>: quiet, whole line, fixed string (so the dots are literal).") + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../05-redirection-and-pipes/03-pipes-and-tee-building-command-pipelines/">Lesson 5.3</a> (pipes) and <a href="../../05-redirection-and-pipes/04-chaining-commands-exit-codes-and-xargs/">5.4</a> (exit codes).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
