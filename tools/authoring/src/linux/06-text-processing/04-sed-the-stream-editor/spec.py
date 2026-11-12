import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='06-text-processing', lesson='04-sed-the-stream-editor', n='6.4',
    module_label='Module 6 · Filters, text processing and regex',
    title='sed: the stream editor',
    desc='sed explained, then used in every field: s/old/new/ with g, i, N, &, groups and \\1, other delimiters; addresses (line numbers, ranges, /patterns/, $, !, 0,/re/, 1~2); p, d, i, a, c, q, =, y; -n, -E, -e, -f; safe in-place editing with -i.bak; pattern and hold space. Real outputs from GNU sed, with the greedy .* trap from common notes explained.',
    og_desc='sed search and replace, line printing and deleting, and safe in-place editing, with real outputs and the greedy .* trap.',
    minutes=42, level='Beginner → Advanced',
    lead='sed applies the same edit to every line of a file, without opening an editor. This lesson explains substitution, line addresses, printing, deleting, inserting and safe in-place editing, then shows how every IT role uses sed.',
    chips=['sed by field', 'The greedy trap', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A tiny config, then the sed commands you use most
printf '# app\\nurl=http://api.cdac.in\\nlevel=debug\\n\\nport=8080\\n' > app.conf
sed 's|http://|https://|' app.conf            # replace (file unchanged)
sed -n '2,3p' app.conf                        # print lines 2-3
sed '/^#/d; /^$/d' app.conf                   # drop comments and blank lines
sed '1i\\# generated 2026-11-06' app.conf | head -2
sed -i.bak 's/debug/info/' app.conf && grep level app.conf
"""

RUN = dict(
    heading='Five everyday sed commands',
    intro='<p>Replace, print a range, delete lines, insert a header and edit the file in place with a backup.</p>',
    code=MAIN,
    anno=[
        ("sed 's|http://|https://|' app.conf            # replace (file unchanged)", 'Printed only.'),
        ("sed '/^#/d; /^$/d' app.conf                   # drop comments and blank lines", 'Real settings.'),
        ("sed -i.bak 's/debug/info/' app.conf && grep level app.conf", 'Changed; app.conf.bak kept.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which command changed the file?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the three lines print? Then run.',
             code="echo 'a a a' | sed 's/a/X/'\necho 'a a a' | sed 's/a/X/g'\necho 'a a a' | sed 's/a/X/3'\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the path has slashes. Fix the delimiter.',
             code="echo /usr/local/bin | sed 's//usr/local//opt/'\n", expect='any'),
        dict(label='4 · Your turn', hint='Print only the last line of /etc/passwd.',
             code="sed -n '$p' /etc/passwd\n"),
        dict(label='5 · Challenge', hint='Turn 2026-11-06 into 06/11/2026.',
             code="echo 2026-11-06 | sed -E 's|([0-9]{4})-([0-9]{2})-([0-9]{2})|\\3/\\2/\\1|'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real config files',
    intro='<p>These change system files and need sudo. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Preview a system config change as a diff', cmd="sed 's/^#\\?MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config | diff /etc/ssh/sshd_config -", output='< #MaxAuthTries 6\n---\n> MaxAuthTries 3', note='Typical. No sudo needed: nothing is changed yet.'),
        dict(title='2 · Apply it with a backup', cmd="sudo sed -i.bak 's/^#\\?MaxAuthTries.*/MaxAuthTries 3/' /etc/ssh/sshd_config && sudo sshd -t && echo ok", output='ok', note='Typical. sshd -t checks the syntax.'),
        dict(title='3 · Replace across a project', cmd="grep -rl 'oldapi.cdac.in' src/ | xargs sed -i.bak 's/oldapi\\.cdac\\.in/api.cdac.in/g'", output='(no output; grep -rn api.cdac.in src/ to check)', note='Typical (Lesson 13.2).'),
        dict(title='4 · macOS difference', cmd="sed -i '' 's/a/b/' file   # BSD sed on a Mac", output='(no output)', note='Typical: BSD sed needs an argument after -i.'),
        dict(title='5 · sed version on our build machine', cmd='sed --version | head -1', output=pc('sed --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='sed results in variables',
    intro='<p>Step through a script that uses sed to build values.</p>',
    code='''line='user=riya;password=Secret#42'
masked=$(echo "$line" | sed -E 's/(password=)[^;]*/\\1*****/')
d=$(echo 06/11/2026 | sed -E 's|(..)/(..)/(....)|\\3-\\2-\\1|')
n=$(printf 'a\\nb\\nc\\n' | sed -n '$=')
echo "$masked | $d | lines=$n"
''',
    notes={1: 'Input :: A line with a secret.', 2: 'Mask :: Group kept, value hidden.', 3: 'Date :: Reordered.', 4: 'Count :: 3 lines.', 5: 'Report.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an admin’s config cleanup, a data engineer’s CSV fix, and a DevOps version bump.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='The real settings of a config',
         problem='<p>Show a config without comments, blank lines or trailing spaces.</p>',
         inp='a messy config',
         approach=['d for comments and blanks.', 's for trailing spaces.'],
         code='''printf '# web\\nport=80   \\n\\n  # old\\nlevel=info\\n' > web.conf
sed -e '/^\\s*#/d' -e '/^\\s*$/d' -e 's/\\s*$//' web.conf | cat -A
''',
         notes={2: 'Clean :: Two settings, no trailing spaces.'},
         tryit='Use -i.bak to clean the file itself.'),
    dict(level='i', tag='Data engineer', title='Fix a CSV export',
         problem='<p>Remove quotes, change ; to , and turn the decimal comma into a dot.</p>',
         inp='a European-style export',
         approach=['Order matters: decimal commas first.', 'Several -e scripts.'],
         code='''printf '"id";"amount"\\n"1";"1250,50"\\n"2";"99,90"\\n' > ex.csv
sed -E -e 's/"//g' -e 's/([0-9]),([0-9])/\\1.\\2/g' -e 's/;/,/g' ex.csv
''',
         notes={2: 'Pipeline :: Quotes gone, 1250.50, commas between columns.'},
         tryit='Swap the order of the last two -e and see the damage.'),
    dict(level='a', tag='DevOps', title='Bump a version in two files',
         problem='<p>Change version 1.4.2 to 1.5.0 in a YAML and a properties file, with backups, and show the diff.</p>',
         inp='two files with the version',
         approach=['Escape the dots (\\.).', '-i.bak on both, diff each.'],
         code='''printf 'image: api:1.4.2\\n' > deploy.yaml; printf 'app.version=1.4.2\\n' > app.properties
sed -i.bak 's/1\\.4\\.2/1.5.0/' deploy.yaml app.properties
for f in deploy.yaml app.properties; do diff "$f.bak" "$f" | grep '^>'; done
''',
         notes={2: 'Edit :: Both files, each with .bak.', 3: 'Check :: The new lines.'},
         tryit='Use a variable: v=2.0.0 and double quotes.'),
]

QUIZ = mix([
    dict(q="What does sed 's/a/b/' file do to the file?", options=['changes it', 'nothing: it prints the result', 'deletes it', 'makes a backup'], answer=1,
         why='Only -i changes the file.'),
    dict(q='Which flag replaces every match on a line?', options=['a', 'g', 'p', 'e'], answer=1,
         why='g = global.'),
    dict(q="sed -n '5p' file prints…", options=['5 lines', 'line 5 only', 'all lines 5 times', 'nothing'], answer=1,
         why='-n stops auto-print; 5p prints line 5.'),
    dict(q='How do you keep a backup when editing in place?', options=['sed -b', 'sed -i.bak', 'sed -i -b', 'sed --keep'], answer=1,
         why='Suffix right after -i.'),
    dict(q="In s/(a)(b)/\\2\\1/ with -E, abc becomes…", options=['abc', 'bac', 'cba', 'ab'], answer=1,
         why='Groups swapped.'),
    dict(q="What does sed '/^#/d' do?", options=['deletes the file', 'removes lines starting with #', 'removes # characters', 'prints comments'], answer=1,
         why='Address /^#/ + d.'),
    dict(q='Why is .* dangerous before a capture group?', options=['it is slow', 'it is greedy and swallows text the group needed', 'it is not allowed', 'it matches nothing'], answer=1,
         why='192.168.1.10 → 2.168.1.10.'),
    dict(q='Which delimiter avoids escaping slashes in paths?', options=['s/a/b/', 's|a|b|', 's\\a\\b\\', 's a b'], answer=1,
         why='Any character can be the delimiter.'),
])

REVISION = [
    "<code>sed 's/old/new/' f</code>: prints; <code>g</code> all, <code>i</code> any case, <code>N</code> Nth; <code>s|a|b|</code> for paths.",
    '<code>&amp;</code> whole match; <code>-E</code> with <code>( )</code> and <code>\\1</code>; quote the script in single quotes.',
    "Addresses: <code>3</code>, <code>2,5</code>, <code>$</code>, <code>/re/</code>, <code>/a/,/b/</code>, <code>1~2</code>, <code>0,/re/</code>, <code>!</code>.",
    "<code>-n '…p'</code> print; <code>'…d'</code> delete; <code>i\\</code> <code>a\\</code> <code>c\\</code>; <code>q</code>; <code>=</code>.",
    '<code>-i.bak</code> then <code>diff f.bak f</code>; test without -i first; never -n with -i without p.',
    '-i writes a new file (new inode, links break).',
    'Greedy <code>.*</code>: extract with <code>grep -oE</code>; use <code>[^,]*</code> instead of <code>.*</code> for columns.',
    'Hold space and N for multi-line tricks; prefer paste/awk when simpler.',
]

FAQ = [
    ('How do I replace text in a file with sed?', "sed -i.bak 's/old/new/g' file (test without -i first)."),
    ('How do I replace a path containing slashes?', "Use another delimiter: sed 's|/old/path|/new/path|g'."),
    ('How do I print specific lines with sed?', "sed -n '10,20p' file, or sed -n '/start/,/end/p' file."),
    ('How do I delete empty lines with sed?', "sed '/^$/d' file (or '/^\\s*$/d' for lines with only spaces)."),
    ('What does sed -n do?', 'It stops sed from printing every line automatically; only p prints.'),
    ('How do I use a shell variable in sed?', "Use double quotes: sed \"s/old/$new/\" file (and choose a delimiter not in the value)."),
    ('Why does sed -i break my symlink?', 'sed -i writes a new file and renames it; use --follow-symlinks to edit the target.'),
]

PRACTICE_INTRO = 'Small sed tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Replace a word', stmt='Change cat to dog everywhere in “cat and cat”.', inp='a line',
         code="echo 'cat and cat' | sed 's/cat/dog/g'\n", explain='g for all.'),
    dict(level='easy', title='Line 2', stmt='Print only line 2 of a three-line text.', inp='three lines',
         code="printf 'a\\nb\\nc\\n' | sed -n '2p'\n", explain='-n + p.'),
    dict(level='easy', title='Delete blank lines', stmt='Remove empty lines.', inp='four lines',
         code="printf 'a\\n\\nb\\n\\n' | sed '/^$/d'\n", explain='/^$/ = empty line.'),
    dict(level='medium', title='Header', stmt='Insert “name,city” before the first line.', inp='two rows',
         code="printf 'Asha,Pune\\nRavi,Agra\\n' | sed '1i\\name,city'\n", explain='1i\\ inserts before line 1.'),
    dict(level='medium', title='Swap', stmt='Turn “Pune-Asha” into “Asha-Pune”.', inp='a string',
         code="echo 'Pune-Asha' | sed -E 's/(.*)-(.*)/\\2-\\1/'\n", explain='Two groups swapped.'),
    dict(level='medium', title='Path', stmt='Replace /var/www with /srv/web in a path.', inp='a path',
         code="echo /var/www/html/index.html | sed 's|/var/www|/srv/web|'\n", explain='| as delimiter.'),
    dict(level='business', title='Mask cards', stmt='Show only the last 4 digits of a 16-digit card number.', inp='a card number',
         code="echo 'card 4111222233334444' | sed -E 's/[0-9]{12}([0-9]{4})/XXXX-XXXX-XXXX-\\1/'\n", explain='Keep the last group, mask the rest.'),
    dict(level='business', title='Section', stmt='Print the lines from [db] up to the next blank line.', inp='an ini file',
         code="printf '[web]\\nport=80\\n\\n[db]\\nhost=db01\\nport=5432\\n\\n[x]\\n' > s.ini\nsed -n '/^\\[db\\]/,/^$/p' s.ini\n", explain='A range from a pattern to a pattern; \\[ makes [ literal.'),
]

SCN_INTRO = 'Interview questions about sed, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Replace a word in a file without opening it.”',
        'One of the most common practical questions.',
        'do you know sed and -i?',
        '''<ul>
          <li><code>sed 's/old/new/g' file</code> to preview; <code>sed -i.bak …</code> to change.</li>
          <li>Mention g, and the delimiter trick for paths.</li>
          <li>Check with grep or diff afterwards.</li>
        </ul>''', 'forgetting that without -i nothing changes.') +
    scn('Operations', 'Junior', 'A config change on 50 servers',
        'max_connections=100 must become 500 in /etc/app/app.conf on 50 servers.',
        'can you change configs safely at scale?',
        '''<ol>
          <li>Test on one: <code>sed 's/^max_connections=.*/max_connections=500/' app.conf | diff app.conf -</code>.</li>
          <li>Apply with <code>-i.bak</code> over ssh in a loop, or better with Ansible (lineinfile).</li>
          <li>Verify with grep on every server; keep the backups until the service restarts cleanly.</li>
        </ol>''', 'editing 50 files by hand in vi.') +
    scn('Data team', 'Mid-level', 'The cleaned file has wrong amounts',
        'A sed script converted “1.250,50” into “1,250.50” on some rows and “1.250.50” on others.',
        'do you test regex edits carefully?',
        '''<ul>
          <li>The order of substitutions matters; write each step, test on edge cases.</li>
          <li>Anchor patterns to the column, use [^;]* instead of .*.</li>
          <li>For real number parsing switch to awk or Python; keep sed for simple text.</li>
        </ul>''', 'adding another sed to fix the first one.') +
    scn('Platform', 'Senior', 'sed -i broke production',
        'After a sed -i on /etc/resolv.conf (a symlink), the system lost DNS.',
        'do you understand how -i works?',
        '''<ul>
          <li>sed -i replaced the symlink with a regular file, so the managed file was no longer updated.</li>
          <li>Use <code>--follow-symlinks</code>, or edit the real target, or the proper tool (resolvectl, netplan).</li>
          <li>Policy: preview, backup, review the diff, use config management.</li>
        </ul>''', '“sed always edits in place”.')
) + interview([
    ('How do you replace all occurrences of a word in a file?', "sed -i 's/old/new/g' file."),
    ('How do you print lines 10 to 20?', "sed -n '10,20p' file."),
    ('How do you delete lines containing a word?', "sed '/word/d' file."),
    ('What does -n do in sed?', 'Suppresses automatic printing.'),
    ('How do you use another delimiter?', "s|a|b| or s#a#b#."),
    ('What are & and \\1 in a replacement?', 'The whole match and the first captured group.'),
    ('Difference between sed and awk?', 'sed edits text line by line; awk works with fields, conditions and calculations.'),
], [
    ('RHCSA (EX200)', 'Analyse and edit text with regular expressions; sed is a common choice for scripted edits.'),
    ('LFCS', 'Essential commands: edit text files with sed and other filters.'),
    ('CompTIA Linux+', 'Stream editing with sed: substitute, delete, print, in-place edits.'),
]) + distro('GNU sed on Linux; BSD sed on macOS behaves differently in a few places.', [
    ('-i', '-i or -i.bak', 'same', "-i '' or -i .bak (argument required)", 'GNU'),
    ('-E', 'yes (-r also)', 'yes', 'yes', 'yes'),
    ('\\b, \\s, I flag, 0,/re/, 1~2', 'GNU extensions', 'GNU', 'missing', 'GNU'),
    ('a\\ / i\\ text on one line', 'yes', 'yes', 'needs a newline after \\', 'yes'),
    ('--follow-symlinks', 'yes', 'yes', 'no', 'yes'),
    ('Install GNU sed on a Mac', '-', '-', 'brew install gnu-sed (gsed)', '-'),
]) + teaser('6.5', 'Riya needs the average salary per department, only for employees in Pune or Mumbai, printed as a neat report with a header and a total line. sed can’t add numbers. Which tool reads columns, compares, adds up and prints reports?')

CHEATSHEET = cheatsheet('sed', [
    ('Substitute', [("s/a/b/", 'first'), ("s/a/b/g", 'all'), ("s/a/b/2 · gi", 'Nth · any case'), ("s|/x|/y|", 'delimiter'), ("&  ·  \\1", 'match · group')]),
    ('Addresses', [("3 · $", 'line · last'), ("2,5", 'range'), ("/re/", 'matching'), ("/a/,/b/", 'section'), ("!", 'not')]),
    ('Commands', [("-n '…p'", 'print'), ("'…d'", 'delete'), ("i\\ a\\ c\\", 'insert/append/change'), ("q · =", 'quit · line no.'), ("y/ab/xy/", 'like tr')]),
    ('Options', [('-i.bak', 'in place + backup'), ('-E', 'extended regex'), ('-e … -e …', 'several'), ('-f file', 'script file'), ('-n', 'no auto-print')]),
    ('Safety', [('preview first', 'no -i'), ('diff f.bak f', 'review'), ('grep -oE', 'to extract'), ('[^,]*', 'not .*'), ('--follow-symlinks', 'links')]),
])

MINDMAP = mindmap('sed', [
    ('s///', 'blue', ['g i N', '& \\1 -E', 's|a|b|']),
    ('Addresses', 'green', ['3, $, 2,5', '/re/, /a/,/b/', '!, 1~2']),
    ('Commands', 'amber', ['p d', 'i a c', 'q = y']),
    ('-i', 'red', ['-i.bak', 'new inode', 'never -n -i']),
    ('Advanced', 'violet', ['N, :a ba', 'hold space h G', '-f scripts']),
    ('Traps', 'acc', ['greedy .*', 'unescaped /', 'no backup']),
])

LAB = lab('migrate a config with sed', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab64 && cd ~/lab64 && rm -f *
printf '# app config\\nurl=http://api.cdac.in\\nlevel=debug\\n\\nbackup=http://files.cdac.in\\nport=8080\\n' > app.conf''',
    tasks=['Change every <code>http://</code> to <code>https://</code> in app.conf <b>in place</b>, keeping a backup <code>app.conf.bak</code>.',
           'Change <code>level=debug</code> to <code>level=info</code> in app.conf.',
           'Write app.conf without comment lines and blank lines into <code>clean.conf</code>.',
           'Write only line 2 of the original (the .bak file) into <code>line2.txt</code>.'],
    solution='''sed -i.bak 's|http://|https://|g' app.conf
sed -i 's/^level=debug/level=info/' app.conf
sed '/^#/d; /^$/d' app.conf > clean.conf
sed -n '2p' app.conf.bak > line2.txt''',
    check='''cd ~/lab64
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 https + backup"  '[ "$(grep -c https:// app.conf 2>/dev/null)" = 2 ] && grep -q http://api app.conf.bak 2>/dev/null'
ok "2 level=info"      'grep -qx level=info app.conf 2>/dev/null'
ok "3 clean copy"      '[ "$(wc -l < clean.conf 2>/dev/null)" = 4 ] && ! grep -q "^#" clean.conf'
ok "4 line 2"          '[ "$(cat line2.txt 2>/dev/null)" = url=http://api.cdac.in ]' ''')
