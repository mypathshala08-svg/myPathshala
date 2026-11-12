import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='06-text-processing', lesson='06-regular-expressions-with-grep-sed-and-awk-basic', n='6.6',
    module_label='Module 6 · Filters, text processing and regex',
    title='Regular expressions with grep, sed and awk (basic and extended)',
    desc='Regular expressions from the ground up: anchors (^ $ \\b), the dot and escaping, character classes ([0-9] [^,] [[:digit:]]), quantifiers (* + ? {n,m}) and greed, groups, alternation and backreferences, and the three dialects (BRE in grep/sed, ERE in grep -E/sed -E/awk, PCRE in grep -P/rename). Real validation patterns for Indian data (mobile, PIN, PAN, vehicle numbers, email, IP, dates), with real outputs and the \\d mistake from common notes explained.',
    og_desc='Regex for grep, sed and awk: anchors, classes, quantifiers, groups, BRE vs ERE vs PCRE, and real validation patterns.',
    minutes=42, level='Beginner → Advanced',
    lead='A regular expression describes the shape of text: “ten digits starting with 6 to 9”, “five capital letters, four digits, one capital letter”. This lesson builds the language piece by piece, explains which tool speaks which dialect, and uses it to validate and extract real data.',
    chips=['Patterns by field', 'Three dialects', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Build a pattern piece by piece
printf '9876543210\\n5876543210\\n98765\\n9123456780\\n' > mobiles.txt
grep -E '^9' mobiles.txt                  # starts with 9
grep -E '[6-9][0-9]{9}' mobiles.txt       # 10-digit shape somewhere
grep -xE '[6-9][0-9]{9}' mobiles.txt      # the whole line
grep -vxE '[6-9][0-9]{9}' mobiles.txt     # the invalid ones
echo 'pin 1234' | grep -oE '[0-9]+'       # [0-9], not \\d
"""

RUN = dict(
    heading='One pattern, refined step by step',
    intro='<p>From “starts with 9” to a full validation, then extraction with [0-9].</p>',
    code=MAIN,
    anno=[
        ("grep -xE '[6-9][0-9]{9}' mobiles.txt      # the whole line", 'Two valid numbers.'),
        ("grep -vxE '[6-9][0-9]{9}' mobiles.txt     # the invalid ones", 'The other two.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which numbers are invalid?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which lines does each grep print? Then run.',
             code="printf 'ab\\naab\\nb\\n' > t.txt\ngrep 'a+b' t.txt\necho ---\ngrep -E 'a+b' t.txt\n", expect='any'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should print 1234. Fix the digit class.',
             code="echo 'pin 1234' | grep -oE '\\d+'\n", expect='any'),
        dict(label='4 · Your turn', hint='Print only the valid 6-digit PIN codes.',
             code="printf '411001\\n40001\\n560001\\n' | grep -xE '[1-9][0-9]{5}'\n"),
        dict(label='5 · Challenge', hint='Extract every email address from the text.',
             code="echo 'mail asha@cdac.in or ravi.k@gmail.com' | grep -oE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: regex in your other tools',
    intro='<p>The same language in Python, vim and ripgrep. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Python uses PCRE-style regex', cmd="python3 -c \"import re; print(re.findall(r'\\d{4}', 'order 7781, pin 4401'))\"", output="['7781', '4401']", note='Typical: \\d works in Python.'),
        dict(title='2 · vim search with very magic', cmd='vim app.log   then type  /\\v(ERROR|FATAL)', output='(cursor jumps to the next ERROR or FATAL line)', note='Typical: \\v makes vim use ERE-like syntax (Lesson 4.3).'),
        dict(title='3 · ripgrep (Rust regex, like PCRE without backtracking)', cmd="rg -o '\\d{6}' addresses.txt", output='411001\n560001', note='Typical.'),
        dict(title='4 · Test a regex interactively', cmd="grep --color=always -E '[6-9][0-9]{9}' mobiles.txt", output='(matches shown in red)', note='Typical.'),
        dict(title='5 · Versions on our build machine', cmd="grep --version | head -1; sed --version | head -1; awk -W version 2>&1 | head -1", output=pc("grep --version | head -1; sed --version | head -1; awk -W version 2>&1 | head -1"), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Patterns and their exit codes',
    intro='<p>Step through a validation script and watch the results.</p>',
    code='''pan=ABCDE1234F
echo "$pan" | grep -qxE '[A-Z]{5}[0-9]{4}[A-Z]'; ok=$?
mob=5876543210
echo "$mob" | grep -qxE '[6-9][0-9]{9}'; bad=$?
echo "pan_ok=$ok mobile_bad=$bad"
''',
    notes={1: 'Value :: A PAN.', 2: 'Check :: 0 = valid.', 3: 'Value :: Starts with 5.', 4: 'Check :: 1 = invalid.', 5: 'Report.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a data team’s validation, a developer’s extraction and an admin’s log filter.'
EXAMPLES = [
    dict(level='b', tag='Data team', title='Find invalid PIN codes',
         problem='<p>List PIN codes that are not exactly six digits starting with 1–9.</p>',
         inp='five PIN codes',
         approach=['[1-9][0-9]{5}', '-x whole value, -v failures.'],
         code='''printf '411001\\n40001\\n011001\\n5600012\\n110001\\n' > pins.txt
grep -vxE '[1-9][0-9]{5}' pins.txt
''',
         notes={2: 'Invalid :: 5 digits, starts with 0, 7 digits.'},
         tryit='Print the valid ones instead.'),
    dict(level='i', tag='Developer', title='Extract version numbers',
         problem='<p>From a changelog, extract every version like 1.4.2 or 10.0.11.</p>',
         inp='a few changelog lines',
         approach=['([0-9]+\\.){2}[0-9]+', 'grep -o, sort -V.'],
         code='''printf 'v1.4.2 fixed login\\nrelease 10.0.11 today\\nsee 1.10.0\\n' > CHANGELOG
grep -oE '([0-9]+\\.){2}[0-9]+' CHANGELOG | sort -V
''',
         notes={2: 'Extract :: Three versions, in version order.'},
         tryit='Only versions starting with 1.'),
    dict(level='a', tag='System admin', title='Failed SSH logins by user and IP',
         problem='<p>From auth log lines, list user and IP of failed password attempts.</p>',
         inp='three log lines',
         approach=['sed -E with two groups.', '-n and p to print only matches.'],
         code='''printf '%s\\n' 'sshd[1]: Failed password for root from 185.220.101.4 port 5 ssh2' 'sshd[2]: Accepted password for riya from 10.0.0.9 port 6 ssh2' 'sshd[3]: Failed password for invalid user admin from 45.9.20.1 port 7 ssh2' > auth.log
sed -nE 's/.*Failed password for (invalid user )?([^ ]+) from ([0-9.]+).*/\\2 \\3/p' auth.log
''',
         notes={2: 'Groups :: User is group 2, IP group 3; group 1 is optional.'},
         tryit='Count attempts per IP with sort | uniq -c.'),
]

QUIZ = mix([
    dict(q='What does ^ mean at the start of a pattern?', options=['not', 'start of the line', 'any character', 'one or more'], answer=1,
         why='Inside [ ] at the start it means “not”: [^0-9].'),
    dict(q="In grep -E, what does 'colou?r' match?", options=['only colour', 'color and colour', 'colouur', 'nothing'], answer=1,
         why='? = optional u.'),
    dict(q="Which matches a real dot?", options=['.', '\\.', '*', '?'], answer=1,
         why='. is any character; \\. is a dot.'),
    dict(q="echo 'pin 1234' | grep -oE '\\d+' prints…", options=['1234', 'nothing', 'pin', 'an error'], answer=1,
         why='In ERE \\d is the letter d; there is no d in the text, so nothing. Use [0-9]+ or grep -P.'),
    dict(q="What does [^,]* match?", options=['commas only', 'everything up to the next comma', 'the whole line', 'nothing'], answer=1,
         why='Any characters except a comma.'),
    dict(q="Which grep option makes the pattern match the whole line?", options=['-w', '-x', '-o', '-v'], answer=1,
         why='-x = whole line; -w = whole word.'),
    dict(q='Which tool understands \\d as a digit?', options=['sed', 'grep -E', 'grep -P', 'mawk'], answer=2,
         why='PCRE only.'),
    dict(q="In basic grep, 'a+b' matches…", options=['ab, aab', 'the text a+b', 'b', 'nothing'], answer=1,
         why='+ is literal in BRE.'),
])

REVISION = [
    '<code>^</code> start, <code>$</code> end, <code>\\b</code> word edge (GNU), <code>.</code> any char, <code>\\.</code> a dot.',
    '<code>[abc] [0-9] [A-Za-z] [^,]</code>; POSIX <code>[[:digit:]] [[:upper:]] [[:space:]] [[:punct:]]</code>.',
    '<code>* + ? {n} {n,m}</code>; greedy: prefer <code>[^&lt;]*</code> over <code>.*</code>.',
    '<code>( )</code> group, <code>|</code> or, <code>\\1</code> reuse (grep, sed; not awk).',
    'BRE (grep, sed): <code>\\+ \\? \\| \\( \\) \\{ \\}</code>; ERE (-E, awk): without backslashes; PCRE (-P, rename, Python): <code>\\d \\w \\s .*? (?=)</code>.',
    '<code>\\d</code> is NOT a digit in grep, grep -E, sed or awk: use <code>[0-9]</code>.',
    'Validate with <code>grep -xE</code> or <code>^…$</code>; list failures with <code>-v</code>; extract with <code>-o</code>.',
    'Mobile <code>[6-9][0-9]{9}</code>, PIN <code>[1-9][0-9]{5}</code>, PAN <code>[A-Z]{5}[0-9]{4}[A-Z]</code>.',
]

FAQ = [
    ('What is the difference between basic and extended regex?', 'In basic regex (grep, sed) + ? | ( ) { } are ordinary characters unless escaped; in extended regex (grep -E, sed -E, awk) they are special without backslashes.'),
    ('Why does \\d not work in grep or sed?', '\\d is Perl syntax. POSIX tools use [0-9] or [[:digit:]]. Use grep -P if you need \\d.'),
    ('How do I match a whole line with grep?', 'grep -x pattern, or anchor it: grep "^pattern$".'),
    ('How do I match a literal dot or star?', 'Escape it: \\. and \\*, or put it in brackets: [.] [*].'),
    ('How do I validate an Indian mobile number?', "grep -xE '[6-9][0-9]{9}' (10 digits, starting with 6 to 9)."),
    ('What does greedy mean?', '.* and other quantifiers take as much text as possible; use negated classes like [^,]* or lazy .*? in PCRE.'),
    ('Can I use the same regex in Python and grep?', 'Mostly, if you stick to ERE features and [0-9]-style classes; \\d, lazy quantifiers and lookarounds need grep -P.'),
]

PRACTICE_INTRO = 'Small regex tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Starts with', stmt='Print words that start with “pre”.', inp='four words',
         code="printf 'prefix\\nexpress\\npreview\\nspree\\n' | grep '^pre'\n", explain='^ anchors.'),
    dict(level='easy', title='Ends with', stmt='Print file names ending in .csv.', inp='four names',
         code="printf 'a.csv\\nb.csv.bak\\nc.txt\\nd.csv\\n' | grep '\\.csv$'\n", explain='\\. and $.'),
    dict(level='easy', title='Digits only', stmt='Extract the numbers from “room 12, floor 3”.', inp='a sentence',
         code="echo 'room 12, floor 3' | grep -oE '[0-9]+'\n", explain='[0-9]+ one or more digits.'),
    dict(level='medium', title='Optional letter', stmt='Match both “analyse” and “analyze”.', inp='three words',
         code="printf 'analyse\\nanalyze\\nanalyst\\n' | grep -E 'analy[sz]e'\n", explain='A class for the one letter that differs.'),
    dict(level='medium', title='Exactly 4 digits', stmt='Print lines that are exactly a 4-digit year.', inp='four values',
         code="printf '2026\\n26\\n20261\\n1999\\n' | grep -xE '[0-9]{4}'\n", explain='-x + {4}.'),
    dict(level='medium', title='This or that', stmt='Print lines with WARN or ERROR.', inp='four log lines',
         code="printf 'INFO a\\nWARN b\\nERROR c\\nDEBUG d\\n' | grep -E 'WARN|ERROR'\n", explain='| needs -E.'),
    dict(level='business', title='Valid PANs', stmt='Print only valid PAN numbers.', inp='three values',
         code="printf 'ABCDE1234F\\nabcde1234f\\nPQRSX5678Z\\n' | grep -xE '[A-Z]{5}[0-9]{4}[A-Z]'\n", explain='Five capitals, four digits, one capital.'),
    dict(level='business', title='Reformat dates', stmt='Turn 2026-11-06 into 06/11/2026 with sed groups.', inp='a date',
         code="echo 2026-11-06 | sed -E 's|([0-9]{4})-([0-9]{2})-([0-9]{2})|\\3/\\2/\\1|'\n", explain='Three groups, reordered.'),
]

SCN_INTRO = 'Interview questions about regular expressions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Write a regex for a 10-digit mobile number.”',
        'Very common in data, testing and developer interviews.',
        'do you know anchors, classes and quantifiers?',
        '''<ul>
          <li><code>^[6-9][0-9]{9}$</code> for Indian numbers; <code>^[0-9]{10}$</code> for any 10 digits.</li>
          <li>Explain each piece; test with good and bad values.</li>
          <li>With grep: <code>grep -xE '[6-9][0-9]{9}'</code>.</li>
        </ul>''', 'forgetting the anchors (11 digits would pass).') +
    scn('Support · logs', 'Junior', 'Extract all order IDs from a log',
        'Order IDs look like ORD-2026-000123.',
        'can you extract with grep -o?',
        '''<ol>
          <li><code>grep -oE 'ORD-[0-9]{4}-[0-9]{6}' app.log | sort -u</code>.</li>
          <li>Count them with wc -l.</li>
          <li>Mention -P only if you need \\d.</li>
        </ol>''', 'using sed with .* and losing characters.') +
    scn('Data team', 'Mid-level', 'Why does the same regex behave differently?',
        'A pattern works in Python but finds nothing in grep.',
        'do you know the dialects?',
        '''<ul>
          <li>Python is PCRE-like; grep is BRE, grep -E is ERE: \\d, lazy quantifiers and lookarounds are missing.</li>
          <li>Rewrite with [0-9] and negated classes, or use grep -P.</li>
          <li>Document the dialect next to every regex in a pipeline.</li>
        </ul>''', '“grep is broken”.') +
    scn('Security', 'Senior', 'A regex took down the API',
        'An input-validation regex <code>^(\\w+\\s?)*$</code> made the API hang on a long input.',
        'do you know about catastrophic backtracking (ReDoS)?',
        '''<ul>
          <li>Nested quantifiers make backtracking engines try exponentially many paths.</li>
          <li>Simplify (<code>^[\\w\\s]*$</code>), limit input length, use non-backtracking engines (RE2, Rust regex).</li>
          <li>Add fuzz tests for regexes on public inputs.</li>
        </ul>''', 'adding a bigger timeout.')
) + interview([
    ('What do ^ and $ mean?', 'Start and end of the line.'),
    ('Difference between * and +?', '* = zero or more; + = one or more.'),
    ('How do you match a literal dot?', '\\. or [.].'),
    ('What is the difference between BRE and ERE?', 'In ERE + ? | ( ) { } are special without backslashes.'),
    ('What is a backreference?', '\\1: the text matched by the first group.'),
    ('Why might \\d not work in sed?', 'It is Perl syntax; use [0-9].'),
    ('What does greedy mean?', 'Quantifiers match as much as possible.'),
], [
    ('RHCSA (EX200)', '“Use grep and regular expressions to analyze text”: an explicit objective.'),
    ('LFCS', 'Essential commands: search with regular expressions in grep, sed and awk.'),
    ('CompTIA Linux+', 'Basic and extended regular expressions with grep, sed and awk.'),
]) + distro('Regex dialects differ more between tools than between distros.', [
    ('grep BRE / ERE', 'GNU grep', 'GNU grep', 'BSD grep (similar)', 'GNU'),
    ('grep -P', 'yes', 'yes', 'no (brew grep)', 'yes'),
    ('\\b \\w \\s in grep/sed', 'GNU extensions', 'GNU', 'partly', 'GNU'),
    ('awk regex', 'mawk ERE (no \\b)', 'gawk ERE (+ \\y \\< \\>)', 'BWK ERE', 'mawk / gawk'),
    ('{n,m} in awk', 'mawk 1.3.4: yes', 'gawk: yes', 'yes', 'yes'),
    ('rename (Perl regex)', 'apt install rename', 'util-linux rename (no regex)', 'brew install rename', '-'),
]) + teaser('7.1', 'Module 6 done: you can search, sort, compare, edit and validate text. Next, Riya has to find every log file bigger than 100 MB, older than 30 days, anywhere under /var, and compress them. grep looks inside files; which command finds the files themselves?')

CHEATSHEET = cheatsheet('regular expressions', [
    ('Anchors', [('^x', 'starts with'), ('x$', 'ends with'), ('^$', 'empty line'), ('\\bx\\b', 'whole word'), ('-x / -w', 'grep line / word')]),
    ('Characters', [('.', 'any one'), ('\\.', 'a dot'), ('[abc] [0-9]', 'set / range'), ('[^,]', 'not a comma'), ('[[:digit:]]', 'POSIX class')]),
    ('Quantifiers', [('*', '0 or more'), ('+', '1 or more (-E)'), ('?', '0 or 1 (-E)'), ('{6} {2,4}', 'exact / range'), ('[^<]*', 'instead of .*')]),
    ('Groups', [('(a|b)', 'or (-E)'), ('(ab)+', 'repeat'), ('\\1', 'backreference'), ('sed -E \\1', 'reuse'), ('grep -oE', 'extract')]),
    ('Dialects', [('grep / sed', 'BRE'), ('grep -E / sed -E / awk', 'ERE'), ('grep -P / Python', 'PCRE'), ('\\d', 'PCRE only'), ('[0-9]', 'everywhere')]),
])

MINDMAP = mindmap('Regular expressions', [
    ('Anchors', 'blue', ['^ $', '\\b', '-x -w']),
    ('Classes', 'green', ['. and \\.', '[0-9] [^,]', '[[:digit:]]']),
    ('Quantifiers', 'amber', ['* + ?', '{n,m}', 'greedy']),
    ('Groups', 'violet', ['( )', '|', '\\1']),
    ('Dialects', 'red', ['BRE grep sed', 'ERE -E awk', 'PCRE -P']),
    ('Use', 'acc', ['validate -x -v', 'extract -o', 'replace sed -E']),
])

LAB = lab('validate sign-up data', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab66 && cd ~/lab66 && rm -f *
printf '9876543210\\n5876543210\\n98765 43210\\n9123456780\\n' > mobiles.txt
printf 'ABCDE1234F\\nabcde1234f\\nPQRSX5678Z\\nAB1234567C\\n' > pans.txt
printf 'order 7781 paid\\norder 12 cancelled\\norder 9034 paid\\n' > orders.log''',
    tasks=['Write the <b>invalid</b> mobile numbers (rule: <code>[6-9][0-9]{9}</code>, whole line) into <code>bad_mobiles.txt</code>.',
           'Write the <b>valid</b> PAN numbers into <code>good_pans.txt</code>.',
           'Write every 4-digit order number (just the digits) into <code>order_ids.txt</code>.',
           'Write the number of lines in orders.log that end with “paid” into <code>paid.txt</code>.'],
    solution='''grep -vxE '[6-9][0-9]{9}' mobiles.txt > bad_mobiles.txt
grep -xE '[A-Z]{5}[0-9]{4}[A-Z]' pans.txt > good_pans.txt
grep -oE '\\b[0-9]{4}\\b' orders.log > order_ids.txt
grep -c 'paid$' orders.log > paid.txt''',
    check='''cd ~/lab66
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 bad mobiles"  '[ "$(cat bad_mobiles.txt 2>/dev/null)" = "$(printf "5876543210\\n98765 43210")" ]'
ok "2 good PANs"    '[ "$(cat good_pans.txt 2>/dev/null)" = "$(printf "ABCDE1234F\\nPQRSX5678Z")" ]'
ok "3 order ids"    '[ "$(cat order_ids.txt 2>/dev/null)" = "$(printf "7781\\n9034")" ]'
ok "4 paid count"   '[ "$(cat paid.txt 2>/dev/null)" = 2 ]' ''')
