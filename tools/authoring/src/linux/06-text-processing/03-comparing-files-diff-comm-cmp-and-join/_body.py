import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
from linuxkit import *
from _data import EMP

CONF = "printf 'port=8080\\nlevel=info\\nuser=app\\n' > web01.conf; printf 'port=9090\\nlevel=info\\nuser=app\\ntimeout=30\\n' > web02.conf"
USERS = "printf 'asha\\nkabir\\nmeena\\nravi\\n' > yesterday.txt; printf 'arjun\\nasha\\nmeena\\nravi\\nriya\\n' > today.txt"
JOIN = "printf '101,Asha\\n102,Ravi\\n103,Meena\\n104,Kabir\\n' > names.csv; printf '101,85000\\n102,52000\\n103,98000\\n105,61000\\n' > pay.csv"

HOOK = hook('Two web servers should be identical, but only one of them crashes at night. The ops lead asks Riya three questions: “What is different in the config? Which users were added or removed since yesterday? And which employees are missing from the payroll file?” Opening the files side by side and reading line by line would take an hour and miss things. <code>diff</code>, <code>comm</code> and <code>join</code> answer each in one line; <code>cmp</code> checks binary files.',
    ['show exactly what changed between two files or folders with <code>diff</code> (normal, <code>-u</code>, <code>-y</code>, <code>-q</code>, <code>-r</code>, <code>-w</code>), and apply it with <code>patch</code>',
     'compare two sorted lists with <code>comm</code>: only in A, only in B, in both (set operations)',
     'check whether any two files, including binaries, are identical with <code>cmp</code>',
     'combine two files on a common key like SQL with <code>join</code> (inner, left, full, anti joins)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'two servers, one crashes'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What the four tools are', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each tool, by field', 16, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'reading a diff'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('What changed between two text files?', 'diff -u old new', 'the format git uses'),
    ('Just: same or different?', 'diff -q a b  /  cmp -s a b', 'exit code 0 = same'),
    ('Two folders', 'diff -rq dir1 dir2', 'which files differ or are missing'),
    ('Side by side on screen', 'diff -y -W 80 a b', 'or vimdiff a b'),
    ('Ignore spaces or case', 'diff -w / -b / -B / -i', 'formatting changes'),
    ('Lines only in A / only in B / in both', 'comm -23 / -13 / -12 A B', 'inputs must be sorted'),
    ('Binary files (images, jars)', 'cmp a b', 'or sha256sum both'),
    ('Merge two files on an ID', 'join -t, a b', 'like SQL JOIN; sort first'),
    ('Apply someone’s changes', 'patch file < fix.patch', 'diff -u makes the patch'),
])

cmap = concept_map(
    [('6.2', 'sort and uniq', 'comm and join need sorted input'), ('6.1', 'grep', 'search inside one file'), ('5.4', 'Exit codes', 'diff and cmp: 0 same, 1 different')],
    ['diff: normal, unified (-u), side by side (-y), brief (-q), folders (-r), ignore options', 'patch: apply a diff', 'comm: three columns for sorted lists, set operations', 'cmp: byte-by-byte, binary files', 'join: inner, left, full and anti joins on a key'],
    [('19.4', 'Checksums', 'sha256sum to compare files across machines'), ('16.6', 'rsync', 'sync only what differs'), ('13.5', 'Data one-liners', 'joins and set operations on CSV'), ('12.5', 'Shell scripts', 'diff -q in checks')],
    'Comparing is half of troubleshooting: “it worked yesterday, what changed?”. These four tools answer that for text, lists, binaries and tables.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ diff -u web01.conf web02.conf', ('-port=8080', 'err'), ('+port=9090', 'acc'), ('+timeout=30', 'acc'), '$ comm -13 yesterday.txt today.txt', ('arjun', 'acc'), ('riya', 'acc'), '$ cmp app_v1.jar app_v2.jar', ('… differ: byte 4113', 'out')], title='riya@ops: ~', size=7.2, step=15)
      + t(352, 36, 'Four ways to compare:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• diff: what changed', '• comm: list sets', '• cmp: any bytes', '• join: tables on a key', '• patch: apply changes'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Two servers, one crashes</h2>
  <div class="story">
''' + puzzle('Riya runs <code>join -t, a.csv b.csv</code> on two files that both contain IDs 1 and 2, but a.csv lists 2 before 1. join prints only the row for 2. Where did row 1 go?') + '''
    <p class="narration">web01 is fine; web02 crashes every night. They were built “the same way”.</p>
''' + scene('A terminal: diff -u shows port 8080 changed to 9090 and a new timeout line; comm -13 lists the new users arjun and riya; cmp reports two jar files differ at byte 4113.', sc,
            'Don’t read two files side by side: <tspan font-weight="700" class="s-acc">ask the computer what differs</tspan>.') + '''
A> <code>diff -u web01.conf web02.conf</code>: minus is only in the first file, plus only in the second. The port differs and web02 has an extra timeout.
R> And the users?
K> Sort both lists, then <code>comm</code>: column one only yesterday, column two only today, column three both.
A> Today: diff (and patch), comm, cmp and join, each explained, then used by admins, developers, DBAs, data engineers, DevOps, security and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Spot the difference: two almost identical pictures side by side with the differences circled (diff); two guest lists with names ticked in one, the other, or both (comm); two locked boxes weighed on a scale (cmp); two registers joined by roll number (join).">'
       + ''.join(label_box(10 + k * 158, 26, 146, 96, [a, b, c], tone, 8.8) for k, (a, b, c, tone) in enumerate([
           ('diff', 'spot the difference', 'between two pictures', 'blue'), ('comm', 'two guest lists', 'only A · only B · both', 'green'),
           ('cmp', 'weigh two boxes', 'same or not?', 'amber'), ('join', 'two registers', 'matched by roll no.', 'violet')]))
       + t(320, 158, 'Four everyday ways of comparing things,', 9.6, 'ink2')
       + t(320, 180, 'done by the computer in a fraction of a second.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Comparing files at four depths', [
    ('v', 'No jargon: spot the difference', '      <p>Think of everyday comparisons.</p>' + pic + '''
      <ul>
        <li><code>diff</code> is the “spot the difference” game: it circles what changed.</li>
        <li><code>comm</code> compares two guest lists: only on list A, only on list B, on both.</li>
        <li><code>cmp</code> just says whether two boxes are exactly the same, and where they first differ.</li>
        <li><code>join</code> puts two registers together using the roll number they share.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>diff old.conf new.conf</code>: what changed (exit 0 = same, 1 = different).</li>
        <li><code>diff -u old new</code>: the “unified” format with - and +, like git.</li>
        <li><code>diff -rq dir1 dir2</code>: which files differ between two folders.</li>
        <li><code>comm -12 a b</code>: lines in both sorted files.</li>
        <li><code>cmp file1 file2</code>: are they byte-for-byte identical?</li>
      </ul>'''),
    ('i', 'Reading diffs, sorted inputs, keys', '''      <ul>
        <li>Normal diff: <code>3a4</code> = after line 3 add line 4, <code>1c1</code> = change, <code>5d4</code> = delete; <code>&lt;</code> is from the first file, <code>&gt;</code> from the second.</li>
        <li>Unified diff: <code>@@ -1,3 +1,4 @@</code> = lines 1–3 of the old, 1–4 of the new; <code>-</code> removed, <code>+</code> added, space = unchanged context.</li>
        <li><code>comm</code> and <code>join</code> need input sorted the same way (same locale). They warn “not in sorted order”, and join may silently drop rows.</li>
        <li><code>join</code> uses field 1 and whitespace by default; <code>-t,</code> for CSV, <code>-1 N -2 M</code> other key columns, <code>-a 1</code> left join, <code>-v 1</code> anti-join, <code>-e NULL -o auto</code> to fill blanks.</li>
        <li>Exit codes: diff and cmp return 0 same, 1 different, 2 trouble; perfect for scripts.</li>
      </ul>'''),
    ('a', 'Behind the screen: the LCS algorithm and patches', '''      <ul>
        <li>diff finds the <b>longest common subsequence</b> (LCS) of lines, using Myers’ O(ND) algorithm: everything not in the common part is an insertion or deletion. <code>--minimal</code>, <code>--patience</code> and <code>--histogram</code> (in git) give different, sometimes clearer, results.</li>
        <li><code>patch</code> applies a unified diff using the context lines to find the right place even if line numbers moved (“Hunk #1 succeeded at 12 (offset 3 lines)”). <code>patch -R</code> undoes it.</li>
        <li><code>cmp</code> stops at the first different byte; to compare files on two machines, compare <b>checksums</b> (<code>sha256sum</code>) instead of copying them.</li>
        <li><code>comm</code> and <code>join</code> stream through both files once, like a database <b>merge join</b>: fast and with little memory, which is why they need sorted input.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>diff, comm, cmp and join</h2>
''' + def_block(
    '<code>diff</code> compares two files (or folders) line by line and prints the changes needed to turn the first into the second. <code>patch</code> applies such a diff. <code>comm</code> compares two <b>sorted</b> files and prints three columns: lines only in file 1, only in file 2, and in both. <code>cmp</code> compares two files byte by byte and reports the first difference. <code>join</code> combines lines of two <b>sorted</b> files that share a common field value.',
    'What changed? Which lines are shared? Are they identical? Combine them on an ID.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Hunk', 'One block of changes in a diff (starts with @@).'),
    ('Unified diff', 'The -u format with - and + lines; used by git and patch.'),
    ('Context lines', 'Unchanged lines shown around a change.'),
    ('Patch', 'A diff saved to a file, to apply elsewhere.'),
    ('Set operations', 'Union, intersection, difference of two lists.'),
    ('Join key', 'The column both files share (an ID).'),
    ('diff', f'{gl("diff", "Glossary →")}'),
    ('Field / delimiter', f'{gl("field-and-delimiter", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('diff', 'difference', 'Written for Unix in 1974 by Douglas McIlroy and James Hunt.'),
    ('patch', 'a patch on cloth', 'Larry Wall (who later created Perl), 1985.'),
    ('comm', 'common', 'Lines in common.'),
    ('cmp', 'compare', 'Byte by byte.'),
    ('join', 'relational join', 'Like SQL JOIN on one column.'),
    ('-u / -c / -y', 'unified / context / side by side', 'Output formats.'),
    ('vimdiff', 'diff inside vim', 'Colours both files (Lesson 4.3).'),
    ('sdiff', 'side-by-side diff', 'Interactive merge.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('What changed', '<code>diff -u old new</code>'),
    ('Same or not', '<code>cmp -s a b &amp;&amp; echo same</code>'),
    ('Folders', '<code>diff -rq dir1 dir2</code>'),
    ('Only in A', '<code>comm -23 &lt;(sort A) &lt;(sort B)</code>'),
    ('Join CSVs', '<code>join -t, a.csv b.csv</code>'),
    ('Apply / undo patch', '<code>patch f &lt; p</code> · <code>patch -R f &lt; p</code>'),
]) + '\n' + lv + didyou('Every <code>git diff</code>, every GitHub pull request and every Linux kernel patch email uses the unified diff format that GNU diff introduced around 1990. The Linux kernel is still developed by emailing patches made with <code>diff -u</code>.') + '''
EXAM> “How do you find what changed between two config files, and how do you check two folders?” → diff -u old new (explain - and +), diff -rq dir1 dir2; exit codes 0 same / 1 different; comm for sorted lists, cmp for binaries.
''' + qc('In unified diff output, what do lines starting with - and + mean?', '- = only in the first (old) file, removed; + = only in the second (new) file, added. Lines starting with a space are unchanged context.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which tool compares what</h2>
''' + table(['Tool', 'Compares', 'Needs sorted input?', 'Output', 'Exit code'], [
    ['<code>diff</code>', 'text files, folders, line by line', 'no', 'changes (normal, -u, -y)', '0 same · 1 differ · 2 error'],
    ['<code>comm</code>', 'two lists', '<b>yes</b>', '3 columns: only A · only B · both', '0 (1 with unsorted warnings)'],
    ['<code>cmp</code>', 'any files, byte by byte', 'no', 'first differing byte and line', '0 same · 1 differ · 2 error'],
    ['<code>join</code>', 'two tables on a key', '<b>yes</b> (on the key)', 'combined rows', '0 (1 if unsorted)'],
    ['<code>sha256sum</code>', 'files on different machines', 'no', 'a fingerprint per file', 'compare the hashes'],
], minw=640) + '''
  <h3>Set operations with comm (A and B sorted)</h3>
''' + table(['You want', 'Command', 'SQL idea'], [
    ['in both (intersection)', '<code>comm -12 A B</code>', 'INNER JOIN / INTERSECT'],
    ['only in A (A minus B)', '<code>comm -23 A B</code>', 'EXCEPT'],
    ['only in B', '<code>comm -13 A B</code>', 'EXCEPT the other way'],
    ['in one but not both', '<code>comm -3 A B</code>', 'symmetric difference'],
    ['all, each once (union)', '<code>sort -u A B</code>', 'UNION'],
], minw=520) + qc('Which comm option lists users who are in today.txt but not in yesterday.txt?', '<code>comm -13 yesterday.txt today.txt</code> (hide columns 1 and 3).') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each tool explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 (GNU diffutils, coreutils 9.4) with small sample files: two server configs, two user lists and two CSV tables.</p>
''' + cmdcard_u(['what changed between two versions of a file or folder', 'reviewing config changes before a restart', 'making patches for others'],
               ['binary files (use cmp or checksums)', 'huge data files where you need set logic (use comm or sort | uniq)'])(
    'diff', 'diff', 'difference',
    'Prints the changes that turn FILE1 into FILE2. Exit status 0 = identical, 1 = different, 2 = trouble.',
    'diff [-u|-c|-y|-q] [-r] [-w|-b|-B|-i] FILE1 FILE2', 'safe',
    [('(none)', 'normal format: 1c1, 3a4, < >', 'quick look'),
     ('-u', 'unified format with - and +', 'reviews, patches, git'),
     ('-y [-W 80]', 'side by side', 'reading on screen'),
     ('-q', 'only say whether they differ', 'scripts, folders'),
     ('-r', 'recursive: whole folders', 'deploy checks'),
     ('-w / -b / -B', 'ignore all / changes in / blank-line whitespace', 'formatting noise'),
     ('-i', 'ignore case', 'config keys'),
     ('--exclude=PAT', 'skip files when -r', '.git, *.log'),
     ('--color', 'colour the output', 'terminal')],
    dict(setup=CONF, cmd="diff web01.conf web02.conf\necho \"exit status $?\"", note='1c1: line 1 changed. 3a4: after line 3, add line 4 of the second file. The status is 1: different.', expect='any'),
    [('sys', [
        dict(situation='Review a config change in the unified format before restarting a service.', setup=CONF, cmd="diff -u web01.conf web02.conf",
             why='- lines are only in the first file, + lines only in the second. The header shows both file names and times.', expect='any'),
        dict(situation='Are two deploy folders identical?', cmd="mkdir -p rel1 rel2; echo v1 > rel1/app.py; echo v2 > rel2/app.py; echo x > rel1/old.cfg; echo y > rel1/same.txt; echo y > rel2/same.txt\ndiff -rq rel1 rel2",
             why='-r walks both folders; -q reports only names: changed files and files present on one side only.', expect='any')]),
     ('dev', [
        dict(situation='Side by side view while reviewing.', setup=CONF, cmd="diff -y -W 50 web01.conf web02.conf",
             why='| marks changed lines, &gt; added, &lt; removed. In a terminal, vimdiff gives the same view with colours.', expect='any')]),
     ('devops', [
        dict(situation='A check that fails a pipeline if the generated config differs from the approved one.', setup=CONF, cmd="if diff -q web01.conf web02.conf > /dev/null; then echo 'config approved'; else echo 'config DRIFT detected'; fi",
             why='diff’s exit code drives the if. Configuration-drift checks in CI work like this.')]),
     ('qa', [
        dict(situation='Compare actual test output with the expected output, ignoring trailing spaces.', cmd="printf 'total: 42  \\nstatus: ok\\n' > got.txt; printf 'total: 42\\nstatus: ok\\n' > expected.txt\ndiff expected.txt got.txt > /dev/null; echo \"strict: $?\"\ndiff -b expected.txt got.txt > /dev/null; echo \"ignoring spaces: $?\"",
             why='“Golden file” tests: -b ignores changes in the amount of white space.')]),
    ],
    anat=anatomy([('diff', 'cmd', 'command'), ('-u', 'opt', 'unified format'), ('web01.conf', 'arg', 'old / reference'), ('web02.conf', 'arg', 'new / to check')], 'Order matters: diff a b shows how to turn a into b. Swap them and every - becomes +.')
) + cmdcard_u(['sending or applying a fix as a file', 'applying a change to many servers', 'undoing a change exactly (-R)'],
               ['when you can use git (git diff / git apply do the same with history)'])(
    'patch', 'patch', 'apply a diff',
    'Reads a diff (best: unified) and changes the target file to match. <code>--dry-run</code> tests first; <code>-R</code> reverses; <code>-b</code> keeps a backup.',
    'diff -u old new > fix.patch   ·   patch [--dry-run] [-b] [-R] FILE < fix.patch', 'change',
    [('patch f < p', 'apply to f', 'fixes'),
     ('--dry-run', 'test without changing', 'always first'),
     ('-b', 'keep f.orig backup', 'safety'),
     ('-R', 'reverse (undo)', 'roll back'),
     ('-p1', 'strip one folder level from paths', 'patches from git')],
    dict(setup=CONF, cmd="diff -u web01.conf web02.conf > fix.patch\npatch --dry-run web01.conf < fix.patch\npatch -b web01.conf < fix.patch\ndiff -q web01.conf web02.conf && echo 'web01 now matches web02'", note='The dry run checked the patch; the real run changed web01.conf and kept web01.conf.orig.'),
    [('sys', [
        dict(situation='Roll the change back.', setup=CONF + "\ndiff -u web01.conf web02.conf > fix.patch; patch -s web01.conf < fix.patch", cmd="patch -R web01.conf < fix.patch\nhead -1 web01.conf",
             why='-R applies the patch in reverse: the port is back to 8080.')]),
    ]
) + cmdcard_u(['two lists: users, packages, IPs, IDs', 'what was added, removed, kept', 'fast set operations on big sorted files'],
               ['unsorted files (sort them first, same locale)', 'files where order or line numbers matter (use diff)'])(
    'comm', 'comm', 'common lines',
    'Reads two <b>sorted</b> files and prints three TAB-indented columns: lines only in file 1, only in file 2, and in both. <code>-1 -2 -3</code> hide columns.',
    'comm [-1] [-2] [-3] SORTED1 SORTED2   ·   comm -23 <(sort A) <(sort B)', 'safe',
    [('comm A B', 'three columns', 'overview'),
     ('-12', 'only lines in both', 'intersection'),
     ('-23', 'only in A', 'removed / missing'),
     ('-13', 'only in B', 'added / new'),
     ('-3', 'in one but not both', 'differences'),
     ('<(sort f)', 'sort on the fly (bash)', 'unsorted inputs'),
     ('--check-order', 'stop with an error if not sorted', 'scripts')],
    dict(setup=USERS, cmd="comm yesterday.txt today.txt | cat -A | sed 's/\\$$//'", note='cat -A shows the TABs as ^I: no TAB = only yesterday (kabir), one TAB = only today (arjun, riya), two TABs = both.'),
    [('sys', [
        dict(situation='Which users were added and which removed since yesterday?', setup=USERS, cmd="echo 'added:';   comm -13 yesterday.txt today.txt\necho 'removed:'; comm -23 yesterday.txt today.txt",
             why='Hide the columns you do not need. Audits of /etc/passwd snapshots work this way.')]),
     ('devops', [
        dict(situation='Packages on server A but missing on server B (from two package lists).', cmd="printf 'curl\\ngit\\nnginx\\nvim\\n' > srvA.txt; printf 'git\\nvim\\nnginx\\n' > srvB.txt\ncomm -23 <(sort srvA.txt) <(sort srvB.txt)",
             why='<(sort …) sorts on the fly. Real lists: <code>dpkg-query -W -f=\'${Package}\\n\'</code> on each server.')]),
     ('data', [
        dict(situation='Customers who ordered both in October and November.', cmd="printf 'C1\\nC2\\nC3\\nC5\\n' > oct.txt; printf 'C2\\nC3\\nC4\\n' > nov.txt\ncomm -12 oct.txt nov.txt",
             why='-12 = intersection: repeat customers.')]),
     ('sec', [
        dict(situation='Which listening ports are new compared with the approved baseline?', cmd="printf '22\\n443\\n80\\n' | sort > baseline.txt; printf '22\\n80\\n443\\n4444\\n' | sort > now.txt\ncomm -13 baseline.txt now.txt",
             why='A new port (4444) that is not in the baseline deserves a look (Lesson 16.4: ss -ltn).')]),
    ]
) + mistake('comm fruits1.txt fruits2.txt   (sample output with apple indented and banana at the left edge)', 'apple and date at the left edge (only in file 1), elderberry and fig after one TAB (only in file 2), banana and cherry after two TABs (both)',
            'The indentation is the whole meaning of comm’s output. Check it with <code>comm a b | cat -A</code>: ^I is one TAB.') + cmdcard_u(['binary files: images, archives, jars, database files', 'a fast “identical or not” check in scripts', 'finding the first changed byte'],
               ['readable text changes (use diff)', 'files on different machines (compare sha256sum)'])(
    'cmp', 'cmp', 'compare bytes',
    'Compares two files byte by byte. Prints the first difference (byte and line number), or nothing if identical. <code>-s</code> prints nothing at all; <code>-l</code> lists every differing byte.',
    'cmp [-s] [-l] FILE1 FILE2', 'safe',
    [('cmp a b', 'first difference', 'quick check'),
     ('-s', 'silent; exit code only', 'scripts'),
     ('-l', 'every differing byte (octal values)', 'small binary diffs'),
     ('-n N', 'compare only the first N bytes', 'headers')],
    dict(cmd="printf 'abc' > v1.bin; printf 'abd' > v2.bin; cp v1.bin v1_copy.bin\ncmp v1.bin v2.bin\ncmp v1.bin v1_copy.bin && echo identical", note='The files differ at byte 3. The copy is identical: cmp prints nothing and returns 0.', expect='any'),
    [('sys', [
        dict(situation='Did the backup copy of a binary come out exactly the same?', cmd="head -c 50000 /dev/urandom > app.jar; cp app.jar backup.jar\ncmp -s app.jar backup.jar && echo 'backup verified'",
             why='-s gives only the exit code. For copies on another machine compare sha256sum outputs instead.')]),
     ('sec', [
        dict(situation='Is a system binary still the original? Compare checksums.', cmd="cp /bin/ls ./ls_copy\nsha256sum /bin/ls ls_copy | awk '{print substr($1,1,16), $2}'",
             why='Equal hashes = identical files, even on different servers. Package tools (debsums, rpm -V) check installed files this way (Lesson 19.4).')]),
    ]
) + cmdcard_u(['combining two tables that share an ID (like SQL JOIN)', 'finding rows without a partner (anti-join)', 'large sorted exports'],
               ['unsorted files (sort on the key first)', 'complex joins with many keys or quoted CSV (use a database, Python or awk)'])(
    'join', 'join', 'relational join',
    'For each pair of lines whose key fields are equal, prints the key followed by the other fields of both lines. Both files must be sorted on the key. Default key: field 1; default separator: blanks.',
    'join [-t SEP] [-1 F] [-2 F] [-a 1|2] [-v 1|2] [-e TXT -o auto] FILE1 FILE2', 'safe',
    [('join -t, a b', 'inner join on field 1', 'matching rows'),
     ('-1 2 -2 1', 'key = field 2 of file 1, field 1 of file 2', 'different key columns'),
     ('-a 1', 'also unmatched rows of file 1', 'left join'),
     ('-a 1 -a 2', 'unmatched from both', 'full outer join'),
     ('-v 1', 'only unmatched rows of file 1', 'anti-join: missing'),
     ('-e NULL -o auto', 'fill missing fields', 'tidy outer joins'),
     ('-o 1.2,2.2', 'choose output fields', 'just name and pay')],
    dict(setup=JOIN, cmd="join -t, names.csv pay.csv", note='Inner join: only IDs present in both files (101, 102, 103).'),
    [('data', [
        dict(situation='Left join: every employee, with pay where known.', setup=JOIN, cmd="join -t, -a 1 -e NULL -o auto names.csv pay.csv",
             why='-a 1 keeps Kabir (no pay row); -e NULL -o auto fills the empty column. Without -o auto, -e has no effect (verified).'),
        dict(situation='Anti-join: payroll rows for unknown employees.', setup=JOIN, cmd="join -t, -v 2 names.csv pay.csv",
             why='-v 2 prints rows of file 2 that have no partner: ID 105 is paid but not in the names file.')]),
     ('dba', [
        dict(situation='Join on a column that is not the first one.', setup=EMP, cmd="printf 'Engineering,Floor 3\\nHR,Floor 1\\nSales,Floor 2\\n' > floors.csv\ntail -n +2 employees.csv | sort -t, -k3,3 | join -t, -1 3 -2 1 -o 1.2,0,2.2 - floors.csv",
             why='-1 3 uses field 3 of the first input (stdin, -); 0 in -o means the key. Both inputs are sorted on the key.')]),
     ('sys', [
        dict(situation='Users with their UID and primary GID (from your notes, corrected).', cmd="cut -d: -f1,3 /etc/passwd | sort -t: -k1,1 > u_uid.txt; cut -d: -f1,4 /etc/passwd | sort -t: -k1,1 > u_gid.txt\njoin -t: u_uid.txt u_gid.txt | head -3",
             why='These files use : so -t: is required; without it join treats the whole line as the key and joins almost nothing.')]),
    ]
) + mistake('join users_uids.txt users_gids.txt   ·   join -t, -a 1 -e \'0\' a.csv b.csv', 'join -t: users_uids.txt users_gids.txt   ·   join -t, -a 1 -e 0 -o auto a.csv b.csv',
            'Without -t: join splits on blanks, so “root:0” is one field and lines only match when UID = GID (verified: wrong rows). And -e only fills fields that -o asks for: add -o auto.') + undo('Only patch changes files; the others just print.', [
    ('patch changed the wrong file:', '<code>patch -R file &lt; fix.patch</code>, or restore <code>file.orig</code> if you used -b.'),
    ('comm/join gave odd results:', 'sort both inputs the same way (<code>LC_ALL=C sort</code>) and on the key column.'),
    ('diff output too long:', 'use <code>-q</code> first, then <code>-u</code> on one file; or <code>| less</code>.'),
    ('diff shows every line changed:', 'Windows line endings in one file: check with <code>cat -A</code>, fix with <code>tr -d \'\\r\'</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='diff /nope /etc/hostname', meaning='A file is missing. Exit 2 = trouble, not “different”.', fix='Check the paths.'),
    dict(cmd="printf 'b\\na\\n' > x.txt; printf 'a\\nb\\n' > y.txt; comm x.txt y.txt", meaning='x.txt is not sorted; the result is unreliable.', fix='<code>comm &lt;(sort x.txt) &lt;(sort y.txt)</code>.'),
    dict(cmd="printf '2,B\\n1,A\\n' > j1.csv; printf '1,x\\n2,y\\n' > j2.csv; join -t, j1.csv j2.csv", meaning='j1.csv is not sorted, so join missed ID 1 (only 2,B,y is printed). This is the puzzle.', fix='Sort both on the key: <code>join -t, &lt;(sort j1.csv) &lt;(sort j2.csv)</code>.'),
    dict(cmd="printf 'x\\n' > a.txt; printf '%s\\n' '--- a' '+++ b' '@@ -1 +1 @@' '-y' '+z' > bad.patch; patch a.txt < bad.patch", meaning='The patch expects a line “y” that is not in a.txt: the hunk fails and is saved to a.txt.rej.', fix='Make sure the patch was made from the same version of the file; check with --dry-run first.'),
]) + qc('Two folders should be identical after a deploy. Which one command lists only what differs?', '<code>diff -rq releaseA/ releaseB/</code>') + '''
'''

SCREENS = screens_block('Real terminal screens: vimdiff shows both files side by side', 'For reading changes, many admins open both files in vimdiff (Lesson 4.3). Differences are highlighted; :qa quits.',
    "printf '%s\\n' 'PS1=\"riya@laptop:~/lab\\$ \"' > ~/.mprc\n" + CONF, 'bash --rcfile ~/.mprc', [
    ('vimdiff web01.conf web02.conf  Enter', "'vimdiff web01.conf web02.conf' Enter", ': both files open side by side; the changed and added lines are marked.'),
    (':qa  Enter', "':qa' Enter", ': quit all windows.'),
], 72, 10, hid='screens', what='bash and vimdiff')

cards = cards + SCREENS + '</section>\n'

# ---------------------------------------------------------------- 5. animations
def dl(k, note, tone):
    left = ['port=8080', 'level=info', 'user=app', '']
    right = ['port=9090', 'level=info', 'user=app', 'timeout=30']
    o = label_box(14, 8, 150, 18, ['web01.conf'], 'card', 7.6) + label_box(196, 8, 150, 18, ['web02.conf'], 'card', 7.6)
    for i in range(4):
        hl = (k == 1 and i == 0) or (k == 2 and i in (1, 2)) or (k == 3 and i == 3)
        tl = 'red' if (hl and i == 0) else ('green' if hl and i == 3 else ('blue' if hl else 'card'))
        tr_ = 'green' if (hl and i in (0, 3)) else ('blue' if hl else 'card')
        if left[i]:
            o += label_box(14, 32 + i * 24, 150, 20, [left[i]], tl, 7.6)
        o += label_box(196, 32 + i * 24, 150, 20, [right[i]], tr_, 7.6)
    return o + t(180, 150, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ diff -u web01.conf web02.conf', '@@ -1,3 +1,4 @@', ('-port=8080', 'err'), ('+port=9090', 'acc'), ' level=info', ' user=app', ('+timeout=30', 'acc')], title='riya@ops', size=7.6)] * 4
see = [s + cap(c, '', tone, y=150, h=34) for s, (c, tone) in zip(see, [('The unified diff.', 'card'), ('- old line, + new line.', 'red'), ('Space = unchanged context.', 'blue'), ('+ only = an added line.', 'green')])]
behind = [dl(0, 'diff looks for the longest common part.', 'violet'), dl(1, 'Line 1 differs: shown as - and +.', 'red'),
          dl(2, 'Lines 2–3 are common: context.', 'blue'), dl(3, 'Line 4 exists only in web02.', 'green')]
two = anim_two('Reading a unified diff', 'How diff matched the lines',
               'A terminal showing diff -u output: port changed from 8080 to 9090, level and user unchanged, timeout added.',
               'Two columns of lines for web01.conf and web02.conf; the changed, common and added lines light up in turn.', see, behind,
               ['The @@ line: old lines 1–3, new lines 1–4.', 'A change is a - line followed by a + line.', 'Lines with a space are the same in both.', 'A + without a - is new.'],
               ['diff first finds what both files share.', 'port=… is not shared.', 'level and user are shared, in order.', 'timeout has no partner on the left.'])

dx = dissect('Layer by layer: comm -13 <(sort yesterday) <(sort today)',
    'How the new users are found. Each layer has a real command and output from our build machine.', [
    dict(key='sort', name='Sort both', sub='same order',
         why='comm walks both files once.',
         how='sort puts lines in the same order.',
         impl='Same locale for both!', used='comm, join.',
         setup=USERS, cmd='sort today.txt | head -3'),
    dict(key='ps', name='<( )', sub='a file name for a command',
         why='comm wants two files.',
         how='bash gives each sort a /dev/fd/N name.',
         impl='Process substitution.', used='diff, comm, join.',
         cmd='echo <(true)'),
    dict(key='walk', name='Merge walk', sub='two pointers',
         why='Fast, little memory.',
         how='Compare the current lines; advance the smaller one.',
         impl='Like a database merge join.', used='Big files.',
         setup=USERS, cmd='comm yesterday.txt today.txt | head -3 | cat -A'),
    dict(key='hide', name='Hide columns', sub='-1 -3',
         why='Keep only what you asked for.',
         how='Columns 1 and 3 are not printed.',
         impl='Column 2 then needs no TAB.', used='Set operations.',
         setup=USERS, cmd='comm -13 yesterday.txt today.txt'),
], hint='From two lists to the answer. Click a layer.')

HOOD = hood('Under the hood: cmp stops at the first difference', 'strace shows cmp opening both files, and reading one 4 KB block from each. The difference is at byte 11, so it stops: the other 196 KB are never read.',
    'cmp big1.bin big2.bin', setup="head -c 200000 /dev/zero > big1.bin; cp big1.bin big2.bin; printf 'X' | dd of=big2.bin bs=1 seek=10 conv=notrunc 2>/dev/null", show='openat.*big|^read\\([34]|^write\\(1', start='openat.*big1')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Reading a diff, and set operations</h2>
''' + two + dx + HOOD + qc('Why do comm and join need sorted input, but diff does not?', 'comm and join walk both files once, comparing the current lines (a merge). diff computes the longest common subsequence and can match lines anywhere.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Comparing files at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ diff -u', 'prompt'), ('old new', 'acc')], title='ops', size=6.4, step=12),
              '1. Change review and drift', 'Before a restart, admins diff the new config against the running one; CI fails on unexpected drift.', ['Change', '*diff -u', 'approve']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['diff -rq', 'rel1 rel2'], 'blue', 8.6), '2. Deploy verification',
    'After copying a release, diff -rq or checksums prove both servers have the same files.', ['Deploy', '*diff -rq', 'same?']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['comm -13', 'users'], 'red', 8.6), '3. Audits',
    'Users, packages, open ports and cron jobs are compared with yesterday’s snapshot.', ['Snapshot', '*comm', 'changes']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['join -t,', 'a b'], 'green', 8.6), '4. Data reconciliation',
    'Finance and data teams match two exports on an ID and list unmatched rows (anti-joins).', ['Two exports', '*join -v', 'mismatches']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['diff exp got', 'tests'], 'violet', 8.6), '5. Golden-file tests',
    'Test suites compare program output with stored expected output; any diff fails the test.', ['Run', '*diff', 'pass / fail']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Same or different?', scenario='A yes/no for two files.', setup=CONF,
         cmd="diff -q web01.conf web02.conf > /dev/null && echo same || echo different", explain='Exit code only.'),
    dict(level='b', title='New log lines (from your notes)', scenario='Lines that are in today’s log but not yesterday’s.',
         cmd="printf 'a\\nb\\n' > y.log; printf 'a\\nb\\nc\\nd\\n' > t.log; diff y.log t.log | grep '^>'", explain='> marks lines from the second file.'),
    dict(level='i', title='Union of two lists', scenario='Everyone in either list, once.', setup=USERS,
         cmd='sort -u yesterday.txt today.txt | paste -sd,', explain='sort -u is the simplest union.'),
    dict(level='i', title='Ignore comments and blanks', scenario='Do two configs differ in real settings?',
         cmd="printf '# v1\\nport=80\\n' > a.cf; printf '# v2 edited\\n\\nport=80\\n' > b.cf; diff <(grep -v -e '^#' -e '^$' a.cf) <(grep -v -e '^#' -e '^$' b.cf) && echo 'same settings'", explain='Compare filtered versions.'),
    dict(level='a', title='Missing from payroll', scenario='Employees with no pay row.', setup=JOIN,
         cmd='join -t, -v 1 names.csv pay.csv', explain='Anti-join on file 1.'),
], extra=build_up('the two-server investigation', 'Riya answers the ops lead step by step.', CONF + '\n' + USERS, [
    ('diff -q web01.conf web02.conf', '1. Do the configs differ at all?'),
    ('diff -u web01.conf web02.conf', '2. Exactly how?'),
    ('comm -13 yesterday.txt today.txt', '3. Which users are new?'),
    ('comm -23 yesterday.txt today.txt', '4. Which user was removed?'),
], expect='any')) + which('Choosing the right tool.', [
    ('Text changes', 'diff -u', 'Readable, patchable.', 'Reading side by side by eye.'),
    ('Folders', 'diff -rq', 'Names only.', 'ls both and compare.'),
    ('Binary / exact', 'cmp -s / sha256sum', 'Byte-exact.', 'diff on binaries.'),
    ('List sets', 'comm (sorted)', 'Three columns.', 'diff on lists.'),
    ('Union', 'sort -u A B', 'One step.', 'comm + tr.'),
    ('Tables on a key', 'join -t, (sorted)', 'Like SQL.', 'Unsorted inputs.'),
    ('Missing partners', 'join -v 1 / -v 2', 'Anti-join.', 'Manual search.'),
    ('Apply changes', 'patch --dry-run then patch', 'Safe.', 'Copying whole files.'),
]) + keys('Shortcuts and handy forms.', [
    ('diff --color=auto -u', 'coloured unified diff', 'diff --color -u a b'),
    ('vimdiff a b', 'side by side in vim; ]c next change', 'vimdiff old new'),
    ('git diff --no-index a b', 'git’s diff on any two files', 'git diff --no-index a b'),
    ('<(cmd)', 'compare command outputs', 'diff <(ls d1) <(ls d2)'),
    ('LC_ALL=C sort', 'consistent order for comm/join', 'comm <(LC_ALL=C sort a) …'),
    ('patch -R', 'undo a patch', 'patch -R f < p'),
]) + scriptit('drift-check.sh', 'A config-drift check for two servers: report changed settings, new and removed keys, and exit 1 if anything differs.',
CONF + '''
a=web01.conf; b=web02.conf
if diff -q "$a" "$b" > /dev/null; then echo "no drift"; exit 0; fi
echo "== changed or added in $b";   comm -13 <(sort "$a") <(sort "$b")
echo "== only in $a";               comm -23 <(sort "$a") <(sort "$b")
keys_a=$(cut -d= -f1 "$a" | sort); keys_b=$(cut -d= -f1 "$b" | sort)
echo "== new keys: $(comm -13 <(echo "$keys_a") <(echo "$keys_b") | paste -sd,)"
exit 1''',
'<p>The first line only creates the two sample configs. In real use, fetch the files with scp or ssh first (Lesson 16.6).</p>', expect='any') + puzzle_answer('join assumes both files are sorted on the key and walks them together. In a.csv the first line was 2; when join then saw 1 it was already past it, so the pair for 1 was never compared. GNU join warns “is not sorted” and “input is not in sorted order”. Always sort both inputs on the key first.') + qc('Which command lists IDs that are in orders.csv but not in customers.csv (both sorted on the ID)?', '<code>join -t, -v 1 orders.csv customers.csv</code> (or <code>comm -23</code> on the ID columns).') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-sort-uniq-wc-cut-paste-and-tr/">Lesson 6.2</a> (sort) and <a href="../../05-redirection-and-pipes/02-redirection-dev-null-and-here-documents/">5.2</a> (&lt;( ) process substitution).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
