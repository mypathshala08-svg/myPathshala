import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
from linuxkit import *
from _data import APPLOG, EMP

CONF = "printf '# web config\\nserver=http://api.cdac.in\\nport=8080\\n\\n# logging\\nlevel=debug\\nbackup_url=http://files.cdac.in\\n' > app.conf"
F4 = "printf 'one\\ntwo\\nthree\\nfour\\n' > f.txt"

HOOK = hook('The company is moving to HTTPS. Riya must change <code>http://</code> to <code>https://</code> in 300 config files, switch <code>level=debug</code> to <code>level=info</code>, and add a header line to each file. Opening 300 files in an editor would take a day and she would miss some. <code>sed -i.bak \'s|http://|https://|g\' *.conf</code> does the first part in one second, with a backup of every file. sed is an editor you control with commands instead of keys.',
    ['replace text with <code>s/old/new/</code> and its flags <code>g</code>, <code>i</code>, <code>2</code>, and use any delimiter (<code>s|a|b|</code>)',
     'choose lines by number, range or pattern (<code>3</code>, <code>2,5</code>, <code>/ERROR/</code>, <code>/start/,/end/</code>, <code>$</code>) and print (<code>-n …p</code>), delete (<code>d</code>), insert, append or change lines',
     'edit files in place safely with <code>-i.bak</code>, and capture parts with <code>-E</code>, <code>( )</code>, <code>\\1</code> and <code>&amp;</code>',
     'fix the classic mistakes: greedy <code>.*</code>, unescaped slashes, editing without a backup'])
ROAD = roadmap([
    ('story', 'The story', 3, '300 configs to HTTPS'),
    ('decide', 'Which sed command when?', 2, 'the quick chart'),
    ('definition', 'What sed is', 5, 'simple meaning + 4 depths'),
    ('commands', 'sed, by field', 18, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'the pattern space cycle'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which sed command? (decide in 5 seconds)', [
    ('Replace the first match on each line', "sed 's/old/new/' f", 'prints the result; file unchanged'),
    ('Replace every match', "sed 's/old/new/g' f", 'i = ignore case: s/x/y/gi'),
    ('Text contains slashes (paths, URLs)', "sed 's|/old/path|/new/path|g'", 'any delimiter works'),
    ('Change the file itself, keep a backup', "sed -i.bak 's/a/b/g' f", 'f.bak is the original'),
    ('Print only lines 10–20', "sed -n '10,20p' f", 'like head + tail'),
    ('Delete lines', "sed '/^#/d; /^$/d' f", 'comments and blank lines'),
    ('Only on lines that match', "sed '/ERROR/s/db01/db02/' f", 'an address before s'),
    ('Insert / append / change a line', "sed '1i\\Header' f  ·  '$a\\Footer'  ·  '3c\\New'", 'i before, a after, c replace'),
    ('Reorder parts of a line', "sed -E 's/(.*)-(.*)/\\2-\\1/'", '\\1 \\2 = captured groups'),
    ('Extract IPs, emails', "grep -oE '…'  (easier than sed)", 'sed with .* is greedy'),
])

cmap = concept_map(
    [('6.1', 'grep', 'find the lines first'), ('6.2', 'tr', 'characters, not words'), ('4.3', 'vim :%s', 'the same s command, interactively')],
    ['sed s/old/new/flags: g i N, & and \\1', 'addresses: line numbers, ranges, /patterns/, $, !', 'commands: p d i a c q = y', '-n -i[.bak] -E -e -f', 'pattern space and hold space (N, G, h)'],
    [('6.5', 'awk', 'when you need columns and logic'), ('6.6', 'Regular expressions', 'the pattern language in depth'), ('13.2', 'find + xargs + sed', 'replace across many files'), ('12.5', 'Shell scripts', 'sed in automation')],
    'sed is the “search and replace” of the command line. It runs the same small program on every line, so it works on one file or a thousand.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ["$ sed -i.bak 's|http://|https://|g' *.conf", "$ grep -c 'https://' app.conf", ('2', 'acc'), "$ sed -n '/level/p' app.conf", ('level=debug', 'out'), "$ sed -i 's/level=debug/level=info/' app.conf", "$ ls app.conf*", ('app.conf  app.conf.bak', 'acc')], title='riya@ops: ~', size=7.0, step=15)
      + t(352, 36, 'One command, many files:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• s/old/new/g replace', '• -i edit in place', '• .bak keeps a backup', '• /pattern/ picks lines', '• d p i a c: line commands'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>300 configs to HTTPS</h2>
  <div class="story">
''' + puzzle('A note says this extracts IP addresses: <code>sed -n \'s/.*\\([0-9]\\{1,3\\}\\.[0-9]\\{1,3\\}\\.[0-9]\\{1,3\\}\\.[0-9]\\{1,3\\}\\).*/\\1/p\'</code>. On the line <code>from 192.168.1.10</code> it prints <code>2.168.1.10</code>. Where did “19” go?') + '''
    <p class="narration">Security says: every internal URL must use HTTPS by Monday. There are 300 config files on the server.</p>
''' + scene('A terminal: sed -i.bak replaces http with https in every .conf file; grep counts 2 https lines; another sed changes level=debug to info; ls shows app.conf and its .bak backup.', sc,
            'sed edits text <tspan font-weight="700" class="s-acc">without opening an editor</tspan>.') + '''
A> sed reads each line, runs your little command on it, and prints the result. <code>s|http://|https://|g</code> means: substitute, using | as the separator because the text has slashes, on every match.
R> And it changes the files?
K> Only with <code>-i</code>. Always add a suffix, <code>-i.bak</code>, so every file keeps a backup. Test without -i first.
A> Today: substitution, line addresses, printing, deleting, inserting, in-place editing and groups, each explained, then used by admins, developers, DBAs, data engineers, DevOps, security and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A proofreader with a red pen working through a stack of pages on a conveyor: each page passes under the pen, gets the same corrections, and continues to the out tray.">'
       + label_box(14, 50, 130, 70, ['pages in', '(lines)'], 'card', 9)
       + label_box(220, 30, 200, 110, ['proofreader', 'same rules', 'on every page:', 's/http/https/'], 'amber', 9)
       + label_box(496, 50, 130, 70, ['pages out', '(stdout or -i)'], 'green', 9)
       + arrow(146, 85, 216, 85) + arrow(422, 85, 492, 85)
       + t(320, 172, 'sed = a proofreader that applies your corrections to every line,', 9.6, 'ink2')
       + t(320, 194, 'one line at a time, very fast.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('sed at four depths', [
    ('v', 'No jargon: a proofreader', '      <p>Think of a proofreader with a red pen.</p>' + pic + '''
      <ul>
        <li>Pages (lines) come in one at a time.</li>
        <li>The proofreader applies the same corrections to every page, without asking.</li>
        <li>Corrected pages go out; with <code>-i</code> they replace the original pages.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>sed 's/cat/dog/' f</code>: first cat on each line → dog (printed, file unchanged).</li>
        <li><code>sed 's/cat/dog/g' f</code>: every cat. <code>gi</code>: any case.</li>
        <li><code>sed -n '5,10p' f</code>: print lines 5–10 only.</li>
        <li><code>sed '/^#/d' f</code>: delete comment lines.</li>
        <li><code>sed -i.bak 's/a/b/g' f</code>: change the file, keep f.bak.</li>
      </ul>'''),
    ('i', 'Addresses, groups and the -n trick', '''      <ul>
        <li>A command can have an <b>address</b>: <code>3</code>, <code>2,5</code>, <code>$</code> (last line), <code>/re/</code>, <code>/start/,/end/</code>, <code>1~2</code> (every 2nd), and <code>!</code> for “not”.</li>
        <li>sed prints every line automatically; <code>-n</code> turns that off so only <code>p</code> prints.</li>
        <li>In the replacement, <code>&amp;</code> is the whole match and <code>\\1</code>…<code>\\9</code> are groups. With <code>-E</code> write groups as <code>( )</code>; without it <code>\\( \\)</code>.</li>
        <li><code>.*</code> is <b>greedy</b>: it takes as much as possible, which is why the IP puzzle lost digits.</li>
        <li>Use another delimiter when the text has slashes: <code>s|/usr/local|/opt|</code>, <code>s#a#b#</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: pattern space, hold space, in-place', '''      <ul>
        <li>sed reads a line into the <b>pattern space</b>, runs the whole script on it, prints it (unless -n), and repeats. The <b>hold space</b> is a second buffer: <code>h</code>/<code>H</code> copy to it, <code>g</code>/<code>G</code> copy back, <code>x</code> swaps.</li>
        <li><code>N</code> appends the next line, so a script can work across lines; <code>:a … ba</code> are labels and branches: sed is a small programming language.</li>
        <li><code>-i</code> does not edit in place: it writes a new temporary file and renames it over the original. The file gets a new inode, so hard links break and the owner/permissions are copied from the original.</li>
        <li>GNU sed extensions: <code>-i</code>, <code>-E</code>, <code>\\b</code>, <code>I</code> flag, <code>0,/re/</code>, <code>1~2</code>. macOS (BSD) sed needs <code>-i ''</code> and lacks some of them.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>sed: the stream editor</h2>
''' + def_block(
    '<code>sed</code> (stream editor) reads input line by line, applies a script of editing commands (substitute, delete, print, insert, append, change, and more) to each line that matches the command’s address, and writes the result to standard output, or back to the file with <code>-i</code>. It is non-interactive, so it is ideal for scripts and for editing many files the same way.',
    'Apply the same edit to every line, automatically.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Script', 'The sed commands, e.g. s/a/b/g; several separated by ; or -e.'),
    ('Address', 'Which lines a command applies to: 3, 2,5, /re/, $.'),
    ('Substitute (s)', 's/regex/replacement/flags.'),
    ('Flag', 'g all, i ignore case, N the Nth match, p print, w file write.'),
    ('In place (-i)', 'Write the result back to the file (with -i.bak a backup).'),
    ('Pattern space', 'The buffer holding the current line.'),
    ('Backreference', '\\1 … \\9: text captured by ( ).'),
    ('sed', f'{gl("sed", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('sed', 'stream editor', 'Lee McMahon, Bell Labs, 1974, based on the ed editor’s commands.'),
    ('s', 'substitute', 'The same command as in ed and vim (:s).'),
    ('p / d', 'print / delete', ''),
    ('i / a / c', 'insert / append / change', 'Before, after, instead of the line.'),
    ('q', 'quit', 'Stop reading.'),
    ('y', 'transliterate', 'Like tr.'),
    ('-n', 'no auto-print', 'Only explicit p prints.'),
    ('-E', 'extended regex', 'Same as grep -E.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Replace all', "<code>sed 's/a/b/g' f</code>"),
    ('In place + backup', "<code>sed -i.bak 's/a/b/g' f</code>"),
    ('Lines 5–10', "<code>sed -n '5,10p' f</code>"),
    ('Delete comments/blank', "<code>sed '/^#/d;/^$/d' f</code>"),
    ('Header line', "<code>sed '1i\\Title' f</code>"),
    ('Paths', "<code>sed 's|/a/b|/c/d|g'</code>"),
]) + '\n' + lv + didyou('sed and vim share their roots: both come from the 1970s editor <code>ed</code>. That is why <code>:%s/old/new/g</code> in vim (Lesson 4.3) and <code>sed \'s/old/new/g\'</code> look the same, and why <code>grep</code>’s name comes from ed’s <code>g/re/p</code>.') + '''
EXAM> “How do you replace a word in a file in place, keeping a backup?” → sed -i.bak 's/old/new/g' file. Show -n 'Np' to print a line, '/re/d' to delete, and mention testing without -i first.
''' + qc('What does <code>sed \'s/cat/dog/\'</code> do with the line <code>cat cat cat</code>?', 'Only the first: <code>dog cat cat</code>. Add g for all, or a number for the Nth: s/cat/dog/2.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Addresses and commands</h2>
''' + table(['Address', 'Means', 'Example'], [
    ['(none)', 'every line', "<code>sed 's/a/b/'</code>"],
    ['<code>3</code> / <code>$</code>', 'line 3 / the last line', "<code>sed '3d'</code>, <code>sed '$a\\END'</code>"],
    ['<code>2,5</code> / <code>2,$</code>', 'a range of lines', "<code>sed -n '2,5p'</code>"],
    ['<code>1~2</code>', 'every 2nd line from 1 (GNU)', "<code>sed -n '1~2p'</code>"],
    ['<code>/re/</code>', 'lines matching re', "<code>sed '/ERROR/d'</code>"],
    ['<code>/start/,/end/</code>', 'from a match to the next match', "<code>sed -n '/BEGIN/,/END/p'</code>"],
    ['<code>0,/re/</code>', 'up to the first match only (GNU)', "<code>sed '0,/x/s/x/y/'</code>"],
    ['<code>addr!</code>', 'lines NOT matching', "<code>sed '/^#/!s/a/b/'</code>"],
], minw=560) + table(['Command', 'Does', 'Example'], [
    ['<code>s/re/rep/flags</code>', 'substitute (g, i, N, p, w)', "<code>s/http:/https:/g</code>"],
    ['<code>p</code> / <code>d</code>', 'print / delete the line', "<code>-n '/x/p'</code> · <code>'/x/d'</code>"],
    ['<code>i\\text</code> / <code>a\\text</code> / <code>c\\text</code>', 'insert before / append after / change', "<code>'1i\\# header'</code>"],
    ['<code>q</code>', 'quit (stop reading)', "<code>sed 10q</code> = head -10"],
    ['<code>=</code>', 'print the line number', "<code>sed -n '$='</code> = wc -l"],
    ['<code>y/abc/xyz/</code>', 'translate characters', 'like tr'],
    ['<code>N G h x</code>, <code>:a</code> <code>ba</code>', 'multi-line, hold space, labels', 'advanced'],
], minw=560) + qc('Which sed command prints only the last line of a file?', "<code>sed -n '$p' file</code> (or <code>sed '$!d'</code>).") + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>sed explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 (GNU sed 4.9) with small sample files: a config <code>app.conf</code>, a 4-line <code>f.txt</code> (one … four), <code>app.log</code> and <code>employees.csv</code>.</p>
''' + cmdcard_u(['replacing words, values, URLs, paths', 'the same change in many files (-i)', 'cleaning data: spaces, quotes, separators'],
               ['changes that need column logic or arithmetic (use awk)', 'structured formats like JSON/YAML/XML (use jq, yq, xmlstarlet)', 'editing without testing first'])(
    's', "sed 's///'", 'substitute',
    'Replaces text matching a regular expression. Without <code>-i</code> the result is printed and the file is unchanged.',
    "sed [-E] [-i[.bak]] 's/REGEX/REPLACEMENT/[g][i][N][p]' FILE", 'change',
    [('s/a/b/', 'first match on each line', 'one change per line'),
     ('s/a/b/g', 'every match', 'global replace'),
     ('s/a/b/2', 'only the 2nd match', 'precise edits'),
     ('s/a/b/gi', 'any case', 'Error/ERROR'),
     ('s|/x|/y|g', 'another delimiter', 'paths, URLs'),
     ('&', 'the whole match in the replacement', 'wrap: s/[0-9]+/[&]/'),
     ('-E + ( ) \\1', 'groups and backreferences', 'reorder parts'),
     ('-i.bak', 'edit the file, keep a backup', 'real changes')],
    dict(setup=CONF, cmd="sed 's|http://|https://|' app.conf | grep url\necho 'a a a' | sed 's/a/X/'\necho 'a a a' | sed 's/a/X/g'\necho 'a a a' | sed 's/a/X/2'", note='Without g only the first match changes; with a number only that match. The file app.conf itself is still unchanged.'),
    [('sys', [
        dict(situation='HTTPS everywhere, in place, with a backup (the story).', setup=CONF, cmd="sed -i.bak 's|http://|https://|g' app.conf\ngrep -n 'https' app.conf\nls app.conf*",
             why='| as the delimiter avoids escaping every slash. app.conf.bak holds the original.'),
        dict(situation='Change one setting value whatever it was before.', setup=CONF, cmd="sed -E 's/^level=.*/level=info/' app.conf | grep level",
             why='^ anchors at the line start, so only the real setting changes, not comments mentioning level.')]),
     ('data', [
        dict(situation='Convert a CSV to tab-separated and remove quotes (from your notes).', cmd="printf '\"id\",\"city\"\\n\"1\",\"Pune\"\\n' > q.csv\nsed -e 's/\"//g' -e 's/,/\\t/g' q.csv | cat -A",
             why='Two expressions with -e; cat -A shows ^I for each TAB. (Only safe when no field contains a comma.)'),
        dict(situation='Indian date 06/11/2026 → ISO 2026-11-06.', cmd="echo 'paid on 06/11/2026' | sed -E 's|([0-9]{2})/([0-9]{2})/([0-9]{4})|\\3-\\2-\\1|'",
             why='Three groups captured, written back in a new order.')]),
     ('dev', [
        dict(situation='Rename a function everywhere in a project (whole word only).', cmd="mkdir -p src; printf 'getUser()\\ngetUserById()\\nx = getUser()\\n' > src/a.py\nsed -i 's/\\bgetUser\\b/fetchUser/g' src/a.py; cat src/a.py",
             why='\\b is a word boundary (GNU), so getUserById is untouched. Check with grep -rnw first (Lesson 6.1).')]),
     ('devops', [
        dict(situation='Set the image version in a deployment file.', cmd="printf 'image: shop/api:1.4.2\\nreplicas: 2\\n' > deploy.yaml\nv=1.5.0\nsed -i \"s|\\(image: shop/api:\\).*|\\1$v|\" deploy.yaml; cat deploy.yaml",
             why='Double quotes let $v expand; the group keeps the image name and replaces only the tag. CI pipelines do this before every deploy.')]),
     ('sec', [
        dict(situation='Mask passwords before sharing a log or config.', cmd="printf 'user=riya\\npassword=Secret#42\\ndb_password = x9\\n' > s.conf\nsed -E 's/(password *= *).*/\\1*****/' s.conf",
             why='Keep the key, hide the value. Never paste real secrets into tickets or chat.')]),
    ],
    anat=anatomy([('sed', 'cmd', 'command'), ('-i.bak', 'opt', 'edit file, keep backup'), ("'s|http://|https://|g'", 'arg', 'script: s, delimiter |, flag g'), ('*.conf', 'arg', 'files')], 'Always single-quote the script, so the shell does not touch $ * \\ or spaces. Use double quotes only when you need a shell variable inside.')
) + mistake("sed -n 's/.*\\([0-9]\\{1,3\\}\\.…\\).*/\\1/p'   (extract IPs)", "grep -oE '([0-9]{1,3}\\.){3}[0-9]{1,3}' file",
            'The leading <code>.*</code> is greedy: it swallows as much as it can and leaves only the shortest possible match for the group, so 192.168.1.10 becomes 2.168.1.10 (real run). The same happens to the email example in many notes (riya.sharma@cdac.in → a@cdac.in). grep -o finds whole matches.') + cmdcard_u(['showing only some lines: a range, a section, matches', 'removing lines: comments, blanks, headers, debug lines', 'quick head/tail/grep replacements in one tool'],
               ['huge files where you only need the first lines (sed 10q is fine; head is clearer)'])(
    'pd', "sed -n '…p' · sed '…d'", 'print and delete lines',
    '<code>p</code> prints the addressed lines (use with <code>-n</code>, otherwise every line is printed and the addressed ones twice). <code>d</code> deletes them from the output.',
    "sed -n 'ADDRp' FILE   ·   sed 'ADDRd' FILE", 'safe',
    [("-n '5p'", 'line 5 only', 'look at one line'),
     ("-n '10,20p'", 'a range', 'middle of a file'),
     ("-n '/re/p'", 'matching lines (like grep)', 'one tool'),
     ("-n '/BEGIN/,/END/p'", 'a section', 'config blocks, dates'),
     ("'1d' / '$d'", 'first / last line', 'headers, footers'),
     ("'/^#/d;/^$/d'", 'comments and blank lines', 'clean config'),
     ("'/^\\s*$/d'", 'lines with only spaces too', 'messy files')],
    dict(setup=F4, cmd="sed -n '2,3p' f.txt\necho ---\nsed '2d' f.txt\necho ---\nsed -n '$=' f.txt", note='-n stops the automatic printing. $= prints the number of the last line: 4.'),
    [('sys', [
        dict(situation='Show the real settings of a config (no comments, no blank lines).', setup=CONF, cmd="sed '/^#/d; /^$/d' app.conf",
             why='Two delete commands separated by ; in one script.')]),
     ('devops', [
        dict(situation='The log lines between two times (from your notes).', setup=APPLOG, cmd="sed -n '/09:02:30/,/09:04:12/p' app.log",
             why='A range from the first line matching the start to the next line matching the end.')]),
     ('data', [
        dict(situation='Remove the header row of a CSV before loading it.', setup=EMP, cmd="sed '1d' employees.csv | head -2",
             why='Same as tail -n +2. Many loaders choke on a header.')]),
     ('qa', [
        dict(situation='Line 42 of a big test report (the failing assertion).', cmd="seq -f 'line %g' 1 100 > report.txt\nsed -n '42p' report.txt\nsed '42q;d' report.txt",
             why='The second form stops reading after line 42: faster on huge files.')]),
    ]
) + cmdcard_u(['adding headers, footers, lines after a match', 'replacing a whole line by a new one', 'scripts that edit configs'],
               ['multi-line blocks in YAML/JSON (use a proper tool)'])(
    'iac', "sed 'i\\' · 'a\\' · 'c\\'", 'insert, append, change',
    '<code>i\\TEXT</code> inserts TEXT before the addressed line, <code>a\\TEXT</code> appends after it, <code>c\\TEXT</code> replaces it.',
    "sed 'ADDRi\\TEXT'   ·   sed 'ADDRa\\TEXT'   ·   sed 'ADDRc\\TEXT'", 'change',
    [("'1i\\# header'", 'line at the top', 'headers, shebangs'),
     ("'$a\\# end'", 'line at the bottom', 'footers'),
     ("'/^port/a\\timeout=30'", 'after a matching line', 'add a setting'),
     ("'3c\\new line'", 'replace line 3', 'fixed positions'),
     ("'/^level=/c\\level=info'", 'replace matching lines', 'whole setting')],
    dict(setup=F4, cmd="sed '1i\\# numbers' f.txt | head -2\nsed '/two/a\\two and a half' f.txt | sed -n '2,3p'\nsed '3c\\THREE' f.txt | paste -sd,", note='i before, a after, c instead.'),
    [('sys', [
        dict(situation='Add a timeout setting right after the port line.', setup=CONF, cmd="sed '/^port=/a\\timeout=30' app.conf | sed -n '2,4p'",
             why='The address finds the line, so this works wherever port= is.')]),
     ('dev', [
        dict(situation='Add a licence header to every source file.', cmd="mkdir -p src; echo 'print(1)' > src/a.py; echo 'print(2)' > src/b.py\nsed -i '1i\\# Copyright 2026 MyPhatshala' src/*.py\nhead -1 src/a.py src/b.py",
             why='-i with several files edits each one separately.')]),
    ]
) + cmdcard_u(['many files, the same change', 'repeatable changes in scripts and pipelines'],
               ['files you have not backed up or committed', 'symlinked or hard-linked files you want to keep linked (-i replaces the file)'])(
    'inplace', 'sed -i', 'edit files in place',
    'Writes the result back to the file instead of the screen. <code>-i.bak</code> (no space) keeps the original as FILE.bak. Without a suffix there is no backup.',
    "sed -i[SUFFIX] 'SCRIPT' FILE...   ·   always test without -i first", 'danger',
    [('-i.bak', 'edit, keep FILE.bak', 'safe default'),
     ('-i', 'edit, no backup', 'only with git or backups'),
     ("-i -e '…' -e '…'", 'several edits', 'one pass'),
     ('-n … -i', 'dangerous: -n without p empties the file', 'avoid'),
     ('--follow-symlinks', 'edit the target, keep the link', 'symlinked configs'),
     ("-i '' (macOS)", 'BSD sed needs an argument', 'Mac users')],
    dict(setup=CONF, cmd="sed -n '/level/p' app.conf\nsed -i.bak 's/level=debug/level=info/' app.conf\ndiff app.conf.bak app.conf", note='diff shows exactly what -i changed (Lesson 6.3). Always check like this.', expect='any'),
    [('devops', [
        dict(situation='Change many files, check, then remove the backups.', cmd="mkdir -p conf; for s in a b c; do echo 'url=http://x' > conf/$s.conf; done\nsed -i.bak 's|http://|https://|' conf/*.conf\ngrep -h url conf/*.conf | sort -u\nrm conf/*.bak",
             why='Change, verify with grep, then clean up. find … -exec sed -i … + does the same over a whole tree (Lesson 13.2).')]),
     ('sec', [
        dict(situation='Disable root SSH login (the real command; needs sudo).', cmd="sudo sed -i.bak 's/^#\\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config\nsudo sshd -t && sudo systemctl reload ssh",
             typical='(no output: the line now reads PermitRootLogin no; sshd -t checked the syntax before reload)',
             why='Test the config (sshd -t) before reloading, or you can lock yourself out (Lesson 19.3).')]),
    ]
) + mistake("sed -n 's/x/y/' -i file   (meant: print and change)", "sed -i.bak 's/x/y/' file",
            'With -n nothing is printed unless you say p, and -i writes that nothing back: the file becomes empty. Never combine -n and -i without a p.') + undo('sed -i rewrites files. Protect yourself.', [
    ('Wrong change with -i.bak:', '<code>mv file.bak file</code> restores it.'),
    ('Wrong change without backup:', '<code>git checkout -- file</code>, your backups, or undo the edit with the reverse s command if it was a simple one-to-one change.'),
    ('Before every -i:', 'run the same command without -i and look (<code>| diff file -</code> shows the change).'),
    ('Hard links broken by -i:', 'expected: -i creates a new file. Use an editor or <code>sed … file | tee file.new</code> and copy back if links matter.'),
]) + errors('sed errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="echo x | sed 's/x/y'", meaning='The s command is missing its final delimiter.', fix="<code>s/x/y/</code>."),
    dict(cmd="echo /usr/bin | sed 's//usr/bin//opt/bin/'", meaning='The slashes in the path end the s command too early.', fix="Use another delimiter: <code>s|/usr/bin|/opt/bin|</code>."),
    dict(cmd="echo abc | sed -E 's/(a/X/'", meaning='An unclosed ( in an extended regex.', fix='Close it, or escape it as \\( for a literal bracket.'),
    dict(cmd="sed -i 's/a/b/' /etc/hostname", meaning='-i needs to create a new file in /etc: permission denied for a normal user.', fix='sudo, and check first without -i.'),
    dict(cmd="echo abc | sed 's/\\(b\\)/\\2/'", meaning='There is only one group, so \\2 does not exist.', fix='Count the groups; use \\1.'),
]) + qc('Write a sed command that prints lines 3 to 5 of a file and nothing else.', "<code>sed -n '3,5p' file</code>") + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def cyc(k, note, tone):
    steps = ['read line', 'pattern space', "s/http/https/", 'print', 'next line']
    o = ''.join(label_box(8 + i * 70, 20, 64, 40, [s], ('amber' if i == k else ('green' if i < k else 'card')), 7.4) for i, s in enumerate(steps))
    o += ''.join(arrow(72 + i * 70, 40, 78 + i * 70, 40) for i in range(4))
    ps = ['', 'url=http://api', 'url=https://api', 'url=https://api', '']
    o += label_box(90, 80, 180, 36, ['pattern space', ps[k] or '(empty)'], 'blue', 8.2)
    return o + t(180, 150, note, 8.6, tone, bold=True)
frames = [cyc(0, 'sed reads one line.', 'violet'), cyc(1, 'It sits in the pattern space.', 'blue'),
          cyc(2, 'Every command runs on it, in order.', 'amber'), cyc(3, 'The result is printed (unless -n).', 'green'), cyc(4, 'The space is cleared; the next line comes in.', 'violet')]
s1 = anim_one('Animated example', 'The sed cycle',
              'How sed processes each line. The same five steps repeat for every line of the input.',
              'read → edit → print', 'Five boxes read, pattern space, command, print, next; a line moves through them and is changed by the s command.', frames,
              ['Read the next line.', 'Put it in the pattern space.', 'Run the script on it.', 'Print it.', 'Repeat until the end.'], hid='scenario-sed')

def greedy(k, note, tone):
    txt = 'from 192.168.1.10'
    parts = [('from 19', '2.168.1.10'), ('from ', '192.168.1.10')][k]
    o = label_box(14, 20, 332, 30, [txt], 'card', 9)
    o += label_box(14, 64, 180, 30, ['.* took: “%s”' % parts[0]], 'red' if k == 0 else 'green', 8.2)
    o += label_box(200, 64, 146, 30, ['group: %s' % parts[1]], 'red' if k == 0 else 'green', 8.2)
    return o + t(180, 130, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ["$ echo 'from 192.168.1.10' |", "  sed -n 's/.*\\(…IP…\\).*/\\1/p'", ('2.168.1.10', 'err')], title='riya@laptop', size=7.6) + cap('Greedy .* ate “19”.', '', 'red', y=150, h=34),
       term(14, 16, 332, 116, ["$ echo 'from 192.168.1.10' |", "  grep -oE '([0-9]{1,3}\\.){3}[0-9]{1,3}'", ('192.168.1.10', 'acc')], title='riya@laptop', size=7.6) + cap('grep -o finds the whole IP.', '', 'green', y=150, h=34)]
behind = [greedy(0, '.* grabs as much as possible; the group keeps the minimum (1 digit).', 'red'),
          greedy(1, 'Matching only the IP itself avoids the problem.', 'green')]
two = anim_two('Why .* is greedy', 'How the regex engine splits the line',
               'Two terminals: the sed extraction prints 2.168.1.10; grep -oE prints 192.168.1.10.',
               'The line from 192.168.1.10 split into what .* consumed and what the group captured.', see, behind,
               ['The note’s sed command loses digits.', 'grep -o prints the full address.'],
               ['.* takes “from 19”, leaving “2.168.1.10” (still a valid 1–3 digit group).', 'No leading .*: nothing is swallowed.'])

dx = dissect("Layer by layer: sed -i.bak 's|http://|https://|g' app.conf",
    'What happens when sed edits a file. Each layer has a real command and output from our build machine.', [
    dict(key='parse', name='Parse the script', sub='s, delimiter, flags',
         why='Understand what to do.',
         how='The first character after s is the delimiter; g is a flag.',
         impl='Compiled once, used for every line.', used='Every sed run.',
         cmd="echo 'url=http://a http://b' | sed 's|http://|https://|g'"),
    dict(key='tmp', name='Temporary file', sub='sedXXXXXX',
         why='Write safely.',
         how='-i writes the new text to a temp file in the same folder.',
         impl='Then rename() over the original.', used='-i.',
         setup=CONF, cmd="ls -i app.conf | cut -d' ' -f1 > before.txt\nsed -i 's/x/x/' app.conf\n[ \"$(ls -i app.conf | cut -d' ' -f1)\" != \"$(cat before.txt)\" ] && echo 'new inode: -i replaced the file'"),
    dict(key='bak', name='Backup', sub='.bak',
         why='Undo.',
         how='The original is renamed to app.conf.bak first.',
         impl='Suffix after -i, no space.', used='Safety.',
         setup=CONF, cmd="sed -i.bak 's|http://|https://|g' app.conf; ls app.conf*"),
    dict(key='check', name='Check', sub='diff',
         why='Know what changed.',
         how='Compare backup and new file.',
         impl='Lesson 6.3.', used='Reviews.',
         setup=CONF, cmd="sed -i.bak 's|http://|https://|g' app.conf; diff app.conf.bak app.conf | grep '^>'", expect='any'),
], hint='From the script to a safely edited file. Click a layer.')

HOOD = hood('Under the hood: -i writes a new file and renames it', 'strace shows sed reading app.conf, writing a temporary file and renaming it over the original: “in place” really means “replace”.',
    "sed -i 's/debug/info/' app.conf", setup=CONF, show='openat.*(app|sed)|rename|^write\\(4', start='openat.*app\\.conf')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>The sed cycle, and the greedy trap</h2>
''' + s1 + two + dx + HOOD + qc('Why does <code>sed -i</code> give the file a new inode number?', 'sed writes the result to a temporary file and renames it over the original. The name is the same, the file is new.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>sed at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ sed -i.bak', 'prompt'), ("'s|a|b|g'", 'acc')], title='ops', size=6.4, step=12),
              '1. Configuration changes', 'Admins change settings across many servers and files with sed -i in scripts and Ansible tasks.', ['Change', '*sed -i.bak', 'config']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['s|:1.4|:1.5|', 'deploy.yaml'], 'blue', 8.6), '2. CI/CD',
    'Pipelines set version numbers, image tags and URLs in files before building and deploying.', ['Build', '*sed', 'versioned file']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ["s/,/\\t/g", 'csv'], 'green', 8.6), '3. Data cleaning',
    'Remove quotes, change separators, fix dates and trim spaces before loading data.', ['Raw file', '*sed', 'clean file']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['s/pass=.*/…/', 'mask'], 'red', 8.6), '4. Masking secrets',
    'Logs and configs are masked before they are shared or shipped to log systems.', ['Log', '*sed', 'safe log']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ["-n '/a/,/b/p'", 'logs'], 'violet', 8.6), '5. Log sections',
    'Extract a time window or one request’s lines from a big log.', ['Log', '*sed -n', 'window']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands from your notes and practice. All really run on our build machine.', [
    dict(level='b', title='Trim spaces', scenario='Remove leading and trailing spaces.',
         cmd="echo '   hello world   ' | sed 's/^ *//; s/ *$//' | cat -A", explain='Two substitutions; cat -A shows the line end $.'),
    dict(level='b', title='Prefix every line', scenario='Add a label in front of each line.', setup=F4,
         cmd="sed 's/^/LOG: /' f.txt | head -2", explain='^ matches the start of the line.'),
    dict(level='i', title='Commas in numbers', scenario='1234567 → 1,234,567 (from your notes).',
         cmd="echo 1234567 | sed ':a;s/\\([0-9]\\)\\([0-9]\\{3\\}\\)\\($\\|,\\)/\\1,\\2\\3/;ta'", explain='A loop: label a, substitute, branch back while it changes. (Indian 12,34,567 grouping needs a different rule.)'),
    dict(level='i', title='Swap two columns', scenario='name,city → city,name.',
         cmd="echo 'Asha,Pune' | sed -E 's/([^,]*),([^,]*)/\\2,\\1/'", explain='[^,]* = “anything except a comma”: not greedy across columns.'),
    dict(level='a', title='Join all lines', scenario='Turn a list into one comma line (from your notes).', setup=F4,
         cmd="sed ':a;N;$!ba;s/\\n/,/g' f.txt", explain='N appends lines into one pattern space; paste -sd, is simpler.'),
], extra=build_up('the HTTPS migration', 'Riya moves a config to HTTPS safely, one step at a time.', CONF, [
    ("grep -n 'http://' app.conf", '1. See what will change.'),
    ("sed 's|http://|https://|g' app.conf | grep -n 'https'", '2. Preview the change without -i.'),
    ("sed -i.bak 's|http://|https://|g' app.conf && diff app.conf.bak app.conf", '3. Apply with a backup and review the diff.'),
    ("sed -i.bak 's|http://|https://|g' app.conf; sed -i 's/^level=debug/level=info/' app.conf; sed -n '/^level/p;/url/p;/^server/p' app.conf", '4. Second change, then show the final values.'),
], expect='any')) + which('Choosing the right tool.', [
    ('Replace text', "sed 's/a/b/g'", 'Fast, scriptable.', 'Opening 300 files.'),
    ('Paths, URLs', "sed 's|a|b|g'", 'No escaping.', "Many \\/."),
    ('Edit files', 'sed -i.bak, then diff', 'Undo possible.', '-i without backup.'),
    ('Extract matches', 'grep -oE', 'Whole matches.', 'sed with greedy .*'),
    ('Column logic', 'awk (6.5)', 'Fields, maths.', 'Complex sed.'),
    ('Characters', 'tr', 'Simpler.', 'sed y/// for big sets.'),
    ('Join lines', 'paste -sd,', 'Readable.', 'sed N loops.'),
    ('JSON / YAML', 'jq / yq', 'Correct.', 'sed on structured data.'),
]) + keys('Shortcuts and handy forms.', [
    ("sed -n '$='", 'count lines', "sed -n '$=' f"),
    ("sed 10q", 'first 10 lines and stop', 'sed 10q big.log'),
    ("sed -n 'Np'", 'one line', "sed -n '42p' f"),
    ('-e … -e …', 'several scripts', "sed -e 's/a/b/' -e '/x/d'"),
    ('-f script.sed', 'commands from a file', 'long scripts'),
    ('sed … f | diff f -', 'preview a change as a diff', "sed 's/a/b/' f | diff f -"),
]) + scriptit('mask-and-clean.sh', 'A small data-cleaning script: remove comments and blank lines, trim spaces, mask passwords, convert dates, and save a cleaned copy.',
'''printf '# export\\n  user=riya  \\n\\npassword=Secret#42\\njoined=06/11/2026\\n' > raw.conf
sed -E -e '/^#/d' -e '/^\\s*$/d' \\
       -e 's/^\\s+//; s/\\s+$//' \\
       -e 's/(password=).*/\\1*****/' \\
       -e 's|([0-9]{2})/([0-9]{2})/([0-9]{4})|\\3-\\2-\\1|' raw.conf > clean.conf
cat clean.conf''') + puzzle_answer('The leading <code>.*</code> is <b>greedy</b>: it takes as many characters as it can while the rest of the pattern can still match. The group needs only 1–3 digits for the first part, so <code>.*</code> keeps “from 19” and the group gets <code>2.168.1.10</code>. Use <code>grep -oE \'([0-9]{1,3}\\.){3}[0-9]{1,3}\'</code>, or in sed make the left side unable to end in a digit: <code>s/.*[^0-9]\\(…\\)…/</code>.') + qc('How do you change “debug” to “info” only on lines that start with level=?', "<code>sed '/^level=/s/debug/info/' file</code>") + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-grep-searching-inside-files/">Lesson 6.1</a> (grep and patterns) and <a href="../../04-text-editors/03-vim-power-use-search-and-replace-blocks/">4.3</a> (vim :s).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
