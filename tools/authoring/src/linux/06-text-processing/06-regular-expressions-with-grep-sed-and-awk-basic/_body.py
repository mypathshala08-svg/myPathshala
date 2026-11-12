import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
from linuxkit import *
from _data import APPLOG, ACCESS

FORM = "printf '%s\\n' 'Asha,9876543210,411001,ABCDE1234F,asha@cdac.in' 'Ravi,5876543210,40001,abcde1234f,ravi@cdac' 'Meena,98765 43210,560001,PQRSX5678Z,meena.k@gmail.com' 'Kabir,9123456780,110001,KLMNO9012P,kabir@@x.in' > signup.csv"

HOOK = hook('An online form collected 40,000 sign-ups. Some mobile numbers have 9 digits, some PIN codes have 5, PAN numbers are in lowercase and emails are missing their domain. Before the data goes into the bank’s system, Riya must find every bad row. She needs one language that can say “exactly 10 digits, starting with 6 to 9” or “five capital letters, four digits, one capital letter”. That language is the <b>regular expression</b>, and grep, sed, awk, vim, Python, Java and SQL all speak it, each with its own small dialect.',
    ['read and write patterns with anchors (<code>^ $ \\b</code>), the dot, character classes (<code>[0-9]</code>, <code>[^,]</code>, <code>[[:digit:]]</code>) and quantifiers (<code>* + ? {n,m}</code>)',
     'group with <code>( )</code>, choose with <code>|</code>, reuse with <code>\\1</code>, and avoid greedy surprises',
     'know the three dialects: basic (grep, sed), extended (grep -E, sed -E, awk) and Perl-style (grep -P, rename, Python), and which one understands <code>+ ? | ( ) {} \\d</code>',
     'validate real Indian data (mobile, PIN, PAN, email, IP, dates) and extract matches with grep -o'])
ROAD = roadmap([
    ('story', 'The story', 3, '40,000 sign-ups to check'),
    ('decide', 'Which pattern piece when?', 2, 'the quick chart'),
    ('definition', 'What a regex is', 5, 'simple meaning + 4 depths'),
    ('commands', 'Pattern pieces, by field', 18, 'real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'how a pattern matches'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which pattern piece? (decide in 5 seconds)', [
    ('Starts with / ends with', '^ERROR  ·  \\.log$', 'anchors'),
    ('Any one character', 'a.c', '\\. for a real dot'),
    ('One of a set / a range', '[aeiou]  ·  [0-9]  ·  [A-Za-z]', '[^0-9] = not a digit'),
    ('A digit in grep, sed, awk', '[0-9]  or  [[:digit:]]', '\\d only with grep -P'),
    ('Repeat: 0+ / 1+ / 0 or 1', '*  ·  +  ·  ?', '+ ? need -E (or \\+ in basic)'),
    ('Exactly / between n and m times', '{10}  ·  {2,4}', '-E, or \\{10\\} in basic'),
    ('Whole word only', '\\bcat\\b  or  grep -w', 'not category'),
    ('This or that', 'ERROR|FATAL', '-E (or \\| in GNU basic)'),
    ('Reuse what matched', '(abc)\\1', 'repeated words'),
    ('Whole line must match', '^…$  or  grep -x', 'validation'),
])

cmap = concept_map(
    [('6.1', 'grep', 'search with patterns'), ('6.4', 'sed', 'replace with patterns'), ('6.5', 'awk', '/re/ and ~')],
    ['literals, the dot and escaping', 'anchors ^ $ \\b and character classes [ ] [^ ] [[:class:]]', 'quantifiers * + ? {n,m}; greedy vs lazy', 'groups ( ), alternation |, backreferences \\1', 'BRE, ERE and PCRE: which tool speaks which'],
    [('3.7', 'rename', 'Perl regex on file names'), ('13.3', 'Log analysis', 'patterns on real logs'), ('13.5', 'Data one-liners', 'validation and extraction'), ('4.3', 'vim', '/search and :s with regex')],
    'Regular expressions are one language used by almost every tool. Learn it once here, and grep, sed, awk, vim, Python and SQL all become easier.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ["$ cut -d, -f2 signup.csv | grep -vxE '[6-9][0-9]{9}'", ('5876543210', 'err'), ('98765 43210', 'err'), "$ cut -d, -f4 signup.csv | grep -vxE '[A-Z]{5}[0-9]{4}[A-Z]'", ('abcde1234f', 'err'), "$ grep -cE ',[1-9][0-9]{5},' signup.csv", ('3', 'acc')], title='riya@bank-etl: ~', size=6.8, step=15)
      + t(352, 36, 'One language, many checks:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• [6-9] one of 6…9', '• [0-9]{9} nine digits', '• [A-Z]{5} five capitals', '• ^ $ / -x whole value', '• -v the bad ones'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>40,000 sign-ups to check</h2>
  <div class="story">
''' + puzzle('Class notes say “<code>\\d</code> matches any digit (equivalent to [0-9])”. Riya runs <code>echo \'pin 1234 d\' | grep -oE \'\\d+\'</code>. What does it print? And what does <code>sed \'s/\\d/X/g\'</code> do to “pin 1234”?') + '''
    <p class="narration">The bank will reject the whole file if a single PAN or mobile number is malformed. Riya has one hour.</p>
''' + scene('A terminal: grep -vxE with mobile and PAN patterns lists the invalid values; a PIN pattern counts 3 valid rows.', sc,
            'A regular expression describes <tspan font-weight="700" class="s-acc">the shape</tspan> of valid text.') + '''
A> Describe what a valid mobile number looks like: one digit from 6 to 9, then nine more digits, nothing else. In regex: <code>^[6-9][0-9]{9}$</code>.
R> And then grep -v shows everything that does NOT have that shape?
K> Exactly. With <code>-x</code> the whole value must match, so “98765 43210” with a space fails too.
A> Today: the building blocks of regular expressions, the three dialects your tools speak, and real validation patterns, each tried with grep, sed and awk.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A stencil for a vehicle number plate: slots for two letters, two digits, two letters, four digits; plates that fit the stencil pass, others are rejected.">'
       + label_box(14, 20, 300, 60, ['stencil: [A-Z]{2} [0-9]{2} [A-Z]{2} [0-9]{4}', 'MH 12 AB 1234'], 'amber', 8.6)
       + label_box(340, 14, 140, 34, ['MH12AB1234 ✓'], 'green', 8.8) + label_box(340, 54, 140, 34, ['MH1AB1234 ✗'], 'red', 8.8)
       + label_box(490, 14, 140, 34, ['KA05XY0042 ✓'], 'green', 8.8) + label_box(490, 54, 140, 34, ['mh12ab1234 ✗'], 'red', 8.8)
       + arrow(316, 50, 336, 40)
       + t(320, 128, 'A regex is a stencil: it describes the shape of valid text,', 9.6, 'ink2')
       + t(320, 150, 'and the computer checks millions of values against it.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Regular expressions at four depths', [
    ('v', 'No jargon: a stencil', '      <p>Think of the stencil used to paint vehicle number plates.</p>' + pic + '''
      <ul>
        <li>The stencil has slots: two letters, two digits, two letters, four digits.</li>
        <li>A plate that fits every slot is valid; one with a missing digit or small letters is rejected.</li>
        <li>A regex is such a stencil, written in symbols: <code>[A-Z]{2}[0-9]{2}[A-Z]{2}[0-9]{4}</code>.</li>
      </ul>'''),
    ('b', 'The symbols you will use every day', '''      <ul>
        <li>Letters and digits match themselves: <code>error</code>.</li>
        <li><code>.</code> any one character; <code>^</code> start of line; <code>$</code> end of line.</li>
        <li><code>[abc]</code> one of a, b, c; <code>[0-9]</code> a digit; <code>[^0-9]</code> anything but a digit.</li>
        <li><code>*</code> zero or more of the previous item; with grep -E also <code>+</code> one or more, <code>?</code> optional, <code>{3}</code> exactly three.</li>
        <li><code>\\.</code> a real dot (escape special characters with a backslash).</li>
      </ul>'''),
    ('i', 'Dialects, groups and classes', '''      <ul>
        <li><b>BRE</b> (basic: grep, sed): <code>+ ? | ( ) { }</code> are ordinary characters; GNU lets you use <code>\\+ \\? \\| \\( \\) \\{ \\}</code> for their special meaning.</li>
        <li><b>ERE</b> (extended: grep -E, sed -E, awk): <code>+ ? | ( ) { }</code> are special without backslashes. Use ERE: it is easier to read.</li>
        <li><b>PCRE</b> (Perl: grep -P, rename, Python, Java): adds <code>\\d \\w \\s</code>, lazy <code>*?</code>, lookarounds. In grep -E, sed and awk <code>\\d</code> does <b>not</b> mean digit.</li>
        <li>POSIX classes work everywhere: <code>[[:digit:]] [[:alpha:]] [[:upper:]] [[:space:]] [[:alnum:]] [[:punct:]]</code>.</li>
        <li><code>( )</code> groups, <code>|</code> chooses, <code>\\1</code> repeats what group 1 matched (grep, sed; not awk).</li>
      </ul>'''),
    ('a', 'Behind the screen: automata, greed and catastrophic backtracking', '''      <ul>
        <li>grep, sed and awk compile ERE/BRE into a finite automaton (DFA/NFA): matching takes time proportional to the text length, whatever the pattern. That is why grep -E is fast even with complex patterns.</li>
        <li>Backreferences (<code>\\1</code>) cannot be handled by a pure automaton, so those patterns use slower backtracking.</li>
        <li>Quantifiers are <b>greedy</b>: <code>.*</code> takes as much as possible (Lesson 6.4’s IP trap). PCRE has lazy versions (<code>.*?</code>); ERE has none, so use negated classes like <code>[^&lt;]*</code>.</li>
        <li>PCRE engines can explode on nested quantifiers like <code>(a+)+$</code> (“catastrophic backtracking”, ReDoS attacks). Keep patterns simple and anchored.</li>
        <li>Ranges like <code>[a-z]</code> follow the locale’s collation; <code>[[:lower:]]</code> or <code>LC_ALL=C</code> is safer.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Regular expressions with grep, sed and awk</h2>
''' + def_block(
    'A <b>regular expression</b> (regex) is a pattern that describes a set of strings, built from literal characters and metacharacters: anchors, the dot, bracket expressions, quantifiers, groups and alternation. POSIX defines <b>basic</b> (BRE) and <b>extended</b> (ERE) syntaxes; Perl-compatible regex (PCRE) adds shorthand classes, lazy quantifiers and lookarounds. grep and sed use BRE by default and ERE with -E; awk uses ERE.',
    'A short description of what the text must look like.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Metacharacter', 'A character with a special meaning: . ^ $ * + ? [ ] ( ) { } | \\'),
    ('Anchor', '^ $ \\b: positions, not characters.'),
    ('Character class', '[abc], [0-9], [[:digit:]]: one character from a set.'),
    ('Quantifier', '* + ? {n,m}: how many times.'),
    ('Greedy', 'Matches as much as possible.'),
    ('Backreference', '\\1: the text matched by group 1.'),
    ('Regular expression', f'{gl("regular-expression-regex", "Glossary →")}'),
    ('BRE vs ERE', f'{gl("basic-vs-extended-regex-bre-ere", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('regular expression', 'regular sets', 'From mathematician Stephen Kleene’s “regular events” (1951).'),
    ('*', 'Kleene star', 'Zero or more: named after Kleene.'),
    ('BRE / ERE', 'basic / extended RE', 'POSIX standard names.'),
    ('PCRE', 'Perl Compatible RE', 'The dialect of Perl, Python, Java, JavaScript.'),
    ('^ $', 'caret, dollar', 'Start and end of line.'),
    ('\\b', 'word boundary', 'GNU and PCRE.'),
    ('\\d \\w \\s', 'digit, word, space', 'PCRE only (grep -P, rename).'),
    ('-x / -w', 'whole line / word', 'grep options that add anchors.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Indian mobile', "<code>^[6-9][0-9]{9}$</code>"),
    ('PIN code', "<code>^[1-9][0-9]{5}$</code>"),
    ('PAN', "<code>^[A-Z]{5}[0-9]{4}[A-Z]$</code>"),
    ('IPv4 shape', "<code>([0-9]{1,3}\\.){3}[0-9]{1,3}</code>"),
    ('ISO date', "<code>^[0-9]{4}-[0-9]{2}-[0-9]{2}$</code>"),
    ('Digit everywhere', "<code>[0-9]</code> (\\d only with -P)"),
]) + '\n' + lv + didyou('Ken Thompson put regular expressions into his QED editor in 1968, compiling them into machine code on the fly: one of the first programs to generate code at runtime. From there they went into ed, grep, sed, awk, Perl, and every language you will use.') + '''
EXAM> “Write a regex for a 10-digit Indian mobile number and use it to find invalid entries in a file.” → grep -vxE '[6-9][0-9]{9}' mobiles.txt (explain [6-9], {9}, -x and -v; mention [0-9] instead of \\d in grep -E).
''' + qc('What does <code>^$</code> match?', 'An empty line: the start of the line is immediately followed by its end.') + mistake('“\\d matches any digit (equivalent to [0-9])” — used with grep, sed or awk', '[0-9] or [[:digit:]] in grep, grep -E, sed and awk · \\d only in grep -P, rename, Perl, Python, Java',
    'In GNU grep and grep -E, <code>\\d</code> silently matches the <b>letter d</b>; in sed it does nothing; mawk treats it as d (all verified). The notes’ table is correct for Perl-style regex (rename, Lesson 3.7), not for the POSIX tools.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which tool speaks which dialect</h2>
''' + table(['Feature', 'grep / sed (BRE)', 'grep -E / sed -E / awk (ERE)', 'grep -P / rename / Python (PCRE)'], [
    ['<code>. ^ $ * [ ]</code>', 'yes', 'yes', 'yes'],
    ['<code>+ ?</code>', 'literal; <code>\\+ \\?</code> (GNU)', '<b>yes</b>', 'yes'],
    ['<code>|</code> alternation', 'literal; <code>\\|</code> (GNU)', '<b>yes</b>', 'yes'],
    ['<code>( )</code> groups', '<code>\\( \\)</code>', '<b>( )</b>', '( )'],
    ['<code>{n,m}</code>', '<code>\\{n,m\\}</code>', '<b>{n,m}</b>', '{n,m}'],
    ['<code>\\1</code> backreference', 'yes', 'grep -E, sed -E yes; awk no', 'yes'],
    ['<code>\\d \\w \\s</code>', '<b>no</b> (\\w \\s GNU only; \\d = d)', '<b>no</b> (\\d = d)', 'yes'],
    ['<code>\\b</code> word boundary', 'GNU yes', 'GNU yes; mawk no', 'yes'],
    ['<code>[[:digit:]]</code> classes', 'yes', 'yes', 'yes'],
    ['lazy <code>*?</code>, lookaround', 'no', 'no', 'yes'],
], minw=720) + qc('Which grep command finds lines with one or more a followed by b, without -E?', "<code>grep 'a\\+b'</code> (GNU), or <code>grep 'aa*b'</code> (portable BRE). With -E: <code>grep -E 'a+b'</code>.") + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each building block, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 with GNU grep 3.11, GNU sed 4.9 and mawk 1.3.4. The sample <code>signup.csv</code> has name, mobile, PIN, PAN and email for four people, with deliberate mistakes.</p>
''' + cmdcard_u(['searching for text at the start or end of a line', 'any single character, or a literal dot', 'whole words and whole lines'],
               ['matching everything with .* when a class would be safer'])(
    'anchors', '^ $ . \\b', 'anchors and the dot',
    '<code>^</code> and <code>$</code> match the start and end of a line, <code>\\b</code> a word boundary (GNU). The dot <code>.</code> matches any one character; <code>\\.</code> a real dot.',
    "grep '^ERROR' · grep '\\.log$' · grep 'a.c' · grep '\\bcat\\b'", 'safe',
    [('^text', 'line starts with text', 'log levels, headings'),
     ('text$', 'line ends with text', 'extensions, shells'),
     ('^$', 'empty line', 'remove blanks'),
     ('.', 'any one character', 'a.c = abc, a-c'),
     ('\\.', 'a real dot', 'IPs, file names'),
     ('\\bword\\b / -w', 'whole word', 'cat, not category'),
     ('-x', 'whole line (adds ^ and $)', 'validation')],
    dict(cmd="printf 'ERROR db\\nlast ERROR\\nreport.log\\nreport_log\\n' > a.txt\ngrep '^ERROR' a.txt\ngrep 'report.log' a.txt\ngrep 'report\\.log' a.txt", note='The unescaped dot also matched “report_log” (the dot is any character, here _). \\. matched only the real dot.'),
    [('sys', [
        dict(situation='Accounts whose shell is nologin (line ends with it).', cmd="grep -c 'nologin$' /etc/passwd",
             why='$ anchors at the end, so a home folder containing “nologin” would not count.')]),
     ('dev', [
        dict(situation='Whole word only: the variable cat, not category or concat.', cmd="echo 'cat category concat' | grep -oE '\\bcat\\b' | wc -l\necho 'cat category concat' | grep -o 'cat' | wc -l",
             why='\\b on both sides: 1 match instead of 3.')]),
     ('devops', [
        dict(situation='Lines that are not comments or blank in a config (from your notes).', cmd="printf '# x\\nport=80\\n\\n  # y\\nhost=a\\n' > c.conf\ngrep -vE '^\\s*(#|$)' c.conf",
             why='^ then optional spaces, then # or end of line. (\\s is a GNU extension; [[:space:]] is portable.)')]),
    ],
    anat=anatomy([('^', 'opt', 'start'), ('[6-9]', 'arg', 'one of 6…9'), ('[0-9]{9}', 'arg', 'nine digits'), ('$', 'opt', 'end')], 'Read a regex left to right, one piece at a time, like this.')
) + cmdcard_u(['one character from a set: digits, letters, vowels, separators', 'everything except a set: [^,] (stays inside a CSV column)', 'portable classes that work in every tool'],
               ['\\d \\w \\s in POSIX tools (use [0-9], [[:alnum:]_], [[:space:]])'])(
    'classes', '[ ] [^ ] [[:class:]]', 'character classes',
    'A bracket expression matches one character from a set or range; <code>[^…]</code> matches one character NOT in the set. POSIX classes like <code>[[:digit:]]</code> go inside the brackets.',
    "[aeiou] · [0-9] · [A-Za-z] · [^,] · [[:digit:]] [[:upper:]] [[:space:]]", 'safe',
    [('[abc]', 'a, b or c', 'choices'),
     ('[0-9] / [A-Z] / [a-z]', 'ranges', 'digits, letters'),
     ('[^0-9]', 'not a digit', 'clean data'),
     ('[^,]*', 'everything up to the next comma', 'CSV columns (not greedy across)'),
     ('[[:digit:]] [[:alpha:]] [[:alnum:]]', 'POSIX classes', 'portable'),
     ('[[:upper:]] [[:lower:]] [[:space:]] [[:punct:]]', 'more classes', 'case, spaces'),
     ('[.] [*]', 'special characters are literal inside [ ]', 'no escaping needed')],
    dict(cmd="echo 'Room 12B, floor 3' | grep -oE '[0-9]+'\necho 'Room 12B, floor 3' | grep -oE '[[:upper:]]'\necho 'Room 12B, floor 3' | sed 's/[^0-9]//g'", note='[^0-9] with s///g deletes every non-digit.'),
    [('data', [
        dict(situation='Keep only digits of a phone number entered with spaces and brackets.', cmd="echo '+91 (98765) 43-210' | sed 's/[^0-9]//g'",
             why='One negated class removes everything else: 919876543210.')]),
     ('sec', [
        dict(situation='Password policy: at least one digit, one capital, one symbol.', cmd="for p in Riya2026 riya@2026 R1ya@2026; do\n  if echo \"$p\" | grep -q '[0-9]' && echo \"$p\" | grep -q '[[:upper:]]' && echo \"$p\" | grep -q '[[:punct:]]'; then echo \"$p strong\"; else echo \"$p weak\"; fi\ndone",
             why='Three simple patterns combined with && are clearer than one giant regex.')]),
     ('dev', [
        dict(situation='Why \\d fails in grep -E (the puzzle).', cmd="echo 'pin 1234 d' | grep -oE '\\d+'\necho 'pin 1234 d' | grep -oE '[0-9]+'\necho 'pin 1234 d' | grep -oP '\\d+'",
             why='grep -E treats \\d as the letter d. [0-9] works everywhere; \\d needs grep -P.')]),
    ]
) + cmdcard_u(['how many times: optional, at least one, exactly N, between N and M', 'lengths of codes, IDs, numbers'],
               ['.* in extraction (greedy): use classes or grep -o with exact pieces'])(
    'quant', '* + ? {n,m}', 'quantifiers',
    'Apply to the item just before them: <code>*</code> 0 or more, <code>+</code> 1 or more, <code>?</code> 0 or 1, <code>{n}</code> exactly n, <code>{n,}</code> at least n, <code>{n,m}</code> between n and m. In BRE write <code>\\+ \\? \\{n,m\\}</code>.',
    "grep -E 'a+b' · 'colou?r' · '[0-9]{6}' · '[A-Z]{2,4}'", 'safe',
    [('*', '0 or more', 'optional repeats'),
     ('+', '1 or more (ERE)', 'numbers: [0-9]+'),
     ('?', '0 or 1 (ERE)', 'colou?r, https?'),
     ('{6}', 'exactly 6', 'PIN code'),
     ('{2,4}', '2 to 4', 'short codes'),
     ('{3,}', '3 or more', 'long words'),
     ('greedy', 'as many as possible', 'beware .*')],
    dict(cmd="printf 'ab\\naab\\nb\\na+b\\n' > t.txt\ngrep 'a+b' t.txt\necho ---\ngrep -E 'a+b' t.txt\necho ---\necho 'colour color' | grep -oE 'colou?r'", note='In basic grep + is an ordinary character, so only the line “a+b” matched. With -E it means “one or more a”.'),
    [('web', [
        dict(situation='http and https URLs.', cmd="echo 'see http://a.in and https://b.in/x' | grep -oE 'https?://[^ ]+'",
             why='s? makes s optional; [^ ]+ = everything up to the next space.')]),
     ('data', [
        dict(situation='Six-digit Indian PIN codes, first digit not 0.', cmd="printf '411001\\n40001\\n011001\\n560001\\n' | grep -xE '[1-9][0-9]{5}'",
             why='{5} after the first digit; -x so 4110012 would fail.')]),
     ('devops', [
        dict(situation='Greedy vs lazy: the first HTML tag only.', cmd="echo '<b>x</b><b>y</b>' | grep -oE '<b>.*</b>'\necho '<b>x</b><b>y</b>' | grep -oE '<b>[^<]*</b>'\necho '<b>x</b><b>y</b>' | grep -oP '<b>.*?</b>'",
             why='.* swallowed both tags. A negated class or PCRE’s lazy .*? stops at the first closing tag.')]),
    ]
) + cmdcard_u(['choices: ERROR|FATAL, jpg|png', 'repeating a part: (ab)+, ([0-9]{1,3}\\.){3}', 'capturing parts to reuse in sed (\\1) or to find repeats'],
               ['awk backreferences (not supported; use match() in gawk)'])(
    'groups', '( ) | \\1', 'groups, alternation, backreferences',
    '<code>( )</code> groups items so a quantifier applies to all of them and remembers what matched. <code>|</code> means “or”. <code>\\1</code> refers to what group 1 matched: in a search it finds repeats, in sed’s replacement it reuses the text.',
    "grep -E '(ERROR|FATAL)' · '([0-9]{1,3}\\.){3}[0-9]{1,3}' · sed -E 's/(.*)-(.*)/\\2-\\1/'", 'safe',
    [('a|b', 'a or b', 'several words'),
     ('(jpg|png)$', 'group + alternation', 'extensions'),
     ('(ab)+', 'repeat a group', 'patterns'),
     ('([0-9]{1,3}\\.){3}', 'three “number dot”', 'IPv4'),
     ('\\1 in a search', 'the same text again', 'doubled words'),
     ('\\1 in sed', 'reuse captured text', 'reorder')],
    dict(setup=APPLOG, cmd="grep -cE ' (ERROR|FATAL) ' app.log\necho 'the the cat sat sat' | grep -oE '\\b([a-z]+) \\1\\b'\necho '2026-11-06' | sed -E 's/([0-9]{4})-([0-9]{2})-([0-9]{2})/\\3.\\2.\\1/'", note='Doubled words found with a backreference; a date reordered with three groups.'),
    [('web', [
        dict(situation='All IPv4 addresses in a log (the correct way, compare Lesson 6.4).', setup=ACCESS, cmd="grep -oE '([0-9]{1,3}\\.){3}[0-9]{1,3}' access.log | sort -u | head -3",
             why='The group repeats “digits and a dot” three times. (It also accepts 999.1.1.1; for strict checks add a range test in awk.)')]),
     ('dev', [
        dict(situation='Image files only.', cmd="printf 'a.jpg\\nb.PNG\\nc.txt\\nd.jpeg\\n' | grep -iE '\\.(jpe?g|png)$'",
             why='-i ignores case; e? covers jpg and jpeg.')]),
     ('qa', [
        dict(situation='Accidentally doubled words in documentation.', cmd="printf 'Install the the package.\\nRun it.\\n' > doc.txt\ngrep -nE '\\b([A-Za-z]+) \\1\\b' doc.txt",
             why='A classic proofreading check.')]),
    ]
) + cmdcard_u(['validating form data, imports and config values', 'extracting IDs, emails, IPs from text'],
               ['full email or URL validation (use a library; regex only checks the shape)'])(
    'valid', 'grep -xE / -vxE', 'real validation patterns',
    'Validation = the <b>whole</b> value must have the shape: use <code>^…$</code> or <code>grep -x</code>. <code>-v</code> lists the values that fail.',
    "grep -xE 'PATTERN' values.txt (valid)   ·   grep -vxE 'PATTERN' values.txt (invalid)", 'safe',
    [("[6-9][0-9]{9}", 'Indian mobile', '10 digits, starts 6–9'),
     ("[1-9][0-9]{5}", 'PIN code', '6 digits, not starting 0'),
     ("[A-Z]{5}[0-9]{4}[A-Z]", 'PAN', 'ABCDE1234F'),
     ("[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}", 'vehicle number', 'MH12AB1234'),
     ("[0-9]{4}-[0-9]{2}-[0-9]{2}", 'ISO date shape', '2026-11-06'),
     ("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}", 'email shape', 'basic check')],
    dict(setup=FORM, cmd="echo 'invalid mobiles:'; cut -d, -f2 signup.csv | grep -vxE '[6-9][0-9]{9}'\necho 'invalid PANs:'; cut -d, -f4 signup.csv | grep -vxE '[A-Z]{5}[0-9]{4}[A-Z]'", note='5876543210 starts with 5; “98765 43210” has a space; abcde1234f is lowercase.'),
    [('data', [
        dict(situation='Invalid PIN codes and emails.', setup=FORM, cmd="cut -d, -f3 signup.csv | grep -vxE '[1-9][0-9]{5}'\ncut -d, -f5 signup.csv | grep -vxE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}'",
             why='40001 has 5 digits; ravi@cdac has no domain ending; kabir@@x.in has two @.')]),
     ('dba', [
        dict(situation='Whole rows that are completely valid, ready to load.', setup=FORM, cmd="grep -E '^[^,]+,[6-9][0-9]{9},[1-9][0-9]{5},[A-Z]{5}[0-9]{4}[A-Z],[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' signup.csv",
             why='[^,]+ for the name keeps each piece inside its column. Only Asha’s row passes every rule.')]),
     ('sec', [
        dict(situation='Mask PAN numbers in a log before sharing it.', cmd="echo 'kyc ok PAN=ABCDE1234F user=riya' | sed -E 's/[A-Z]{5}[0-9]{4}[A-Z]/XXXXX9999X/g'",
             why='Personal identifiers must not leave the system in plain text.')]),
     ('qa', [
        dict(situation='Test the pattern itself with good and bad examples.', cmd="for m in 9876543210 5876543210 98765 98765432101; do echo \"$m\" | grep -qxE '[6-9][0-9]{9}' && echo \"$m ok\" || echo \"$m bad\"; done",
             why='Always test a regex with values that must pass and values that must fail.')]),
    ]
) + undo('Regex mistakes rarely break files, but they can silently select the wrong data.', [
    ('A pattern matches too much:', 'anchor it (^ $ -x -w), replace .* with a negated class, escape dots.'),
    ('A pattern matches nothing:', 'check the dialect: + ? | ( ) { } need -E; \\d needs -P.'),
    ('sed -i with a wrong regex changed files:', 'restore the .bak (Lesson 6.4); test with grep -o first.'),
    ('Slow or hanging regex (PCRE):', 'avoid nested quantifiers like (a+)+; anchor; prefer grep -E.'),
]) + errors('Regex errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="echo x | grep -E '('", meaning='An unclosed group.', fix='Close it, or match a real bracket with \\( (or [(]).'),
    dict(cmd="echo x | grep '[a-'", meaning='An unclosed bracket expression.', fix='Close it: [a-z].'),
    dict(cmd="echo x | grep -E '*abc'", meaning='GNU grep warns and treats a * at the start as a literal *. No match, exit 1.', fix='Put * after the item it repeats.'),
    dict(cmd="echo 'pin 1234' | sed 's/\\d/X/g'", meaning='No error and no change: \\d is not a digit class in sed.', fix="<code>sed 's/[0-9]/X/g'</code>."),
]) + qc('Write a grep command that prints only lines consisting of exactly six digits.', "<code>grep -xE '[0-9]{6}' file</code> (or <code>grep -E '^[0-9]{6}$'</code>)") + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def m(k, note, tone):
    pieces = ['^', '[6-9]', '[0-9]{9}', '$']
    val = '9876543210'
    o = ''.join(label_box(14 + i * 82, 14, 76, 30, [p], ('amber' if i == k else ('green' if i < k else 'card')), 8.6) for i, p in enumerate(pieces))
    used = ['', '9', '9 + 876543210', '9876543210 ✓'][k]
    o += label_box(40, 60, 280, 30, ['input: 9876543210'], 'card', 8.6) + label_box(40, 98, 280, 30, ['matched so far: ' + (used or '(start)')], 'blue', 8.4)
    return o + t(180, 150, note, 8.6, tone, bold=True)
frames = [m(0, '^: we are at the start of the line.', 'violet'), m(1, '[6-9]: 9 is in the set.', 'green'), m(2, '[0-9]{9}: nine more digits.', 'green'), m(3, '$: and nothing after: valid.', 'green')]
s1 = anim_one('Animated example', 'Matching ^[6-9][0-9]{9}$',
              'How the pattern for an Indian mobile number checks a value, piece by piece.',
              'piece by piece', 'Four pattern pieces light up in turn while the matched part of 9876543210 grows.', frames,
              ['Start anchor.', 'First digit 6–9.', 'Exactly nine more digits.', 'End anchor: no extra characters.'], hid='scenario-regex')

def d3(k, note, tone):
    rows = [('grep', 'BRE', 'a\\+b · \\(x\\) · \\{3\\}'), ('grep -E · sed -E · awk', 'ERE', 'a+b · (x) · {3}'), ('grep -P · rename · Python', 'PCRE', '\\d · .*? · (?=x)')]
    o = ''
    for i, (a, b, c) in enumerate(rows):
        o += label_box(14, 14 + i * 40, 332, 34, [a + '  →  ' + b, c], ('green' if i == k else 'card'), 8.2)
    return o + t(180, 150, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ["$ grep 'a+b' t.txt", ('a+b', 'out')], title='riya@laptop', size=8) + cap('Basic: + is just a plus sign.', '', 'card', y=150, h=34),
       term(14, 16, 332, 116, ["$ grep -E 'a+b' t.txt", ('ab', 'acc'), ('aab', 'acc')], title='riya@laptop', size=8) + cap('Extended: + means one or more.', '', 'green', y=150, h=34),
       term(14, 16, 332, 116, ["$ echo 'pin 1234' | grep -oP '\\d+'", ('1234', 'acc')], title='riya@laptop', size=8) + cap('Perl: \\d is a digit.', '', 'blue', y=150, h=34)]
behind = [d3(0, 'BRE: special meaning needs a backslash.', 'violet'), d3(1, 'ERE: + ? | ( ) { } are special as they are.', 'green'), d3(2, 'PCRE: shorthand classes, lazy quantifiers.', 'blue')]
two = anim_two('Three dialects of one language', 'Same idea, different spelling',
               'Three terminals: basic grep matches the literal a+b; grep -E matches ab and aab; grep -P extracts 1234 with \\d+.',
               'A table of the three dialects BRE, ERE and PCRE, lighting up in turn with an example of each.', see, behind,
               ['grep without -E.', 'grep -E.', 'grep -P.'],
               ['Oldest, most compatible.', 'Use this by default.', 'When you need \\d, lazy or lookarounds.'])

dx = dissect("Layer by layer: grep -vxE '[6-9][0-9]{9}' mobiles.txt",
    'Reading one validation command layer by layer. Each layer has a real command and output from our build machine.', [
    dict(key='e', name='-E', sub='extended regex',
         why='{9} without backslashes.',
         how='ERE syntax.',
         impl='Compiled to an automaton.', used='Most patterns.',
         cmd="echo 987 | grep -E '[0-9]{3}'; echo 987 | grep '[0-9]{3}' || echo 'basic: {3} is literal, no match'"),
    dict(key='x', name='-x', sub='whole line',
         why='No extra characters allowed.',
         how='Adds ^ and $ around the pattern.',
         impl='Same as ^…$.', used='Validation.',
         cmd="echo 98765432101 | grep -E '[6-9][0-9]{9}'; echo 98765432101 | grep -xE '[6-9][0-9]{9}' || echo '-x: 11 digits rejected'"),
    dict(key='v', name='-v', sub='the failures',
         why='List what is wrong.',
         how='Prints lines that do NOT match.',
         impl='Exit 0 if any line is invalid.', used='Data checks.',
         cmd="printf '9876543210\\n5876543210\\n' | grep -vxE '[6-9][0-9]{9}'"),
    dict(key='pat', name='[6-9][0-9]{9}', sub='the shape',
         why='Indian mobile rule.',
         how='One of 6–9, then 9 digits.',
         impl='10 characters total.', used='Forms, CRMs.',
         cmd="echo 9123456780 | grep -oE '[6-9][0-9]{9}'"),
], hint='From options to the pattern. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How a pattern matches, and the three dialects</h2>
''' + s1 + two + dx + qc('Why does <code>grep \'[0-9]{3}\'</code> (no -E) not match “987”?', 'In basic regex { } are ordinary characters, so grep looks for a digit followed by the text “{3}”. Use -E, or \\{3\\}.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Regular expressions at work</h2>
''' + usecase(term(8, 14, 104, 62, [("$ grep -vxE", 'prompt'), ("'[6-9]…'", 'acc')], title='etl', size=6.4, step=12),
              '1. Data validation', 'Banks, telecoms and e-commerce validate mobiles, PINs, PANs and emails before loading data.', ['Import', '*regex check', 'clean rows']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['grep -oE', 'IPs, IDs'], 'blue', 8.6), '2. Extraction',
    'Pull order IDs, IPs, error codes and URLs out of logs and documents.', ['Text', '*grep -o', 'values']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['sed -E', '\\1 \\2'], 'green', 8.6), '3. Transformation',
    'Reformat dates, swap columns, mask secrets with groups and backreferences.', ['Data', '*sed -E', 'new format']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ReDoS', '(a+)+'], 'red', 8.6), '4. Security',
    'WAF rules, log alerts and input filters are regexes; badly written ones can be attacked (ReDoS).', ['Input', '*regex', 'allow / block']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['IDE', 'search'], 'violet', 8.6), '5. Developer tools',
    'IDEs, vim, git grep, linters and code reviews all use the same pattern language.', ['Code', '*regex search', 'changes']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful patterns from your notes and practice. All really run on our build machine.', [
    dict(level='b', title='Vowels', scenario='Count the vowels in a word ([aeiou] from your notes).',
         cmd="echo 'education' | grep -o '[aeiou]' | wc -l", explain='A class + -o, one match per line.'),
    dict(level='b', title='Lines starting with H', scenario='Headings (from your notes).',
         cmd="printf 'Hello\\nhi\\nHost\\n' | grep '^H'", explain='^ anchors.'),
    dict(level='i', title='Order numbers', scenario='Extract 4-digit order numbers from a log.', setup=APPLOG,
         cmd="grep -oE 'order [0-9]{4}' app.log", explain='Exact count with {4}.'),
    dict(level='i', title='Hour of each error', scenario='When did problems happen?', setup=APPLOG,
         cmd="grep -E ' (ERROR|FATAL) ' app.log | grep -oE '[0-9]{2}:[0-9]{2}' | sort | uniq -c", explain='Filter, extract HH:MM, count.'),
    dict(level='a', title='Strict IPv4 check', scenario='Shape with regex, ranges with awk.',
         cmd="printf '192.168.1.10\\n999.1.1.1\\n10.0.0\\n' | grep -xE '([0-9]{1,3}\\.){3}[0-9]{1,3}' | awk -F. '$1<=255 && $2<=255 && $3<=255 && $4<=255'", explain='Regex checks the shape; awk checks each number ≤ 255.'),
], extra=build_up('the sign-up validator', 'Riya builds the bank check one rule at a time.', FORM, [
    ("cut -d, -f2 signup.csv | grep -vxE '[6-9][0-9]{9}'", '1. Bad mobile numbers.'),
    ("cut -d, -f4 signup.csv | grep -vxE '[A-Z]{5}[0-9]{4}[A-Z]'", '2. Bad PANs.'),
    ("awk -F, '$3 !~ /^[1-9][0-9][0-9][0-9][0-9][0-9]$/ {print NR\": bad PIN \"$3}' signup.csv", '3. Bad PIN codes with row numbers (awk ERE; written without {6} so it works in every awk).'),
    ("grep -nvE '^[^,]+,[6-9][0-9]{9},[1-9][0-9]{5},[A-Z]{5}[0-9]{4}[A-Z],[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$' signup.csv | cut -d: -f1 | paste -sd,", '4. Every row number that fails any rule.'),
], expect='any')) + which('Choosing the right dialect and tool.', [
    ('Search lines', 'grep -E', 'Readable ERE.', 'BRE with many backslashes.'),
    ('Digits', '[0-9] / [[:digit:]]', 'Works everywhere.', '\\d outside -P.'),
    ('\\d, lazy, lookahead', 'grep -P', 'PCRE features.', 'Expecting them in sed/awk.'),
    ('Replace with groups', 'sed -E \\1', 'Clear.', 'sed BRE \\( \\).'),
    ('Column conditions', "awk '$3 ~ /re/'", 'Per field.', 'Whole-line grep tricks.'),
    ('Validation', 'grep -x / ^…$', 'Whole value.', 'Unanchored patterns.'),
    ('Extraction', 'grep -oE', 'Exact matches.', 'sed with .*'),
    ('Real email/URL rules', 'a library', 'Correct.', 'A 300-character regex.'),
]) + keys('Shortcuts and handy forms.', [
    ('grep -E / sed -E', 'use extended regex', "grep -E 'a+|b?'"),
    ('grep -P', 'Perl regex: \\d, lazy', "grep -oP '\\d+'"),
    ('grep -o', 'show only what matched (test your regex)', "echo x | grep -o 're'"),
    ('--color', 'see what matched', "grep --color -E 'pat'"),
    ('LC_ALL=C', 'byte-based ranges, faster', 'LC_ALL=C grep -E …'),
    ('vim /pattern', 'same language in the editor (\\v very magic)', '/\\v[0-9]{4}'),
]) + scriptit('validate-signups.sh', 'The bank check as a script: count valid and invalid rows, write the bad ones to a file with their row numbers, and exit non-zero if any row is invalid.',
FORM + '''
re='^[^,]+,[6-9][0-9]{9},[1-9][0-9]{5},[A-Z]{5}[0-9]{4}[A-Z],[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'
good=$(grep -cE "$re" signup.csv)
grep -nvE "$re" signup.csv > rejected.txt
echo "valid: $good  invalid: $(wc -l < rejected.txt)"
cut -d, -f1 rejected.txt
[ -s rejected.txt ] && exit 1 || exit 0''',
'<p>The pattern is stored in a variable and used in double quotes, so the shell does not touch it. The first line only creates the sample file.</p>', expect='any') + puzzle_answer('<code>grep -oE \'\\d+\'</code> prints <b>d</b>: in grep’s basic and extended syntax <code>\\d</code> is just the letter d. <code>sed \'s/\\d/X/g\'</code> changes <b>nothing</b>. Only Perl-style engines (grep -P, rename, Perl, Python) read \\d as a digit. In grep, sed and awk use <code>[0-9]</code> or <code>[[:digit:]]</code>.') + qc('Write a regex for a vehicle number like MH12AB1234 (two letters, two digits, one or two letters, four digits).', "<code>^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$</code> with grep -E.") + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-grep-searching-inside-files/">6.1 grep</a>, <a href="../04-sed-the-stream-editor/">6.4 sed</a> and <a href="../05-awk-fields-patterns-and-reports/">6.5 awk</a>.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
