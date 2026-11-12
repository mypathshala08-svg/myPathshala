import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='06-text-processing', lesson='03-comparing-files-diff-comm-cmp-and-join', n='6.3',
    module_label='Module 6 · Filters, text processing and regex',
    title='Comparing files: diff, comm, cmp and join',
    desc='diff (normal, -u, -y, -q, -r, -w -b -B -i, exit codes) and patch (--dry-run, -b, -R); comm for sorted lists and set operations; cmp and checksums for binary files; join for SQL-style inner, left, full and anti joins (-t -1 -2 -a -v -e -o auto). Each explained, then used by admins, developers, DBAs, data engineers, DevOps, security and QA, with real outputs and corrections to common notes.',
    og_desc='diff, patch, comm, cmp and join explained with real outputs: config drift, user audits, binary checks and table joins.',
    minutes=38, level='Beginner → Advanced',
    lead='“It worked yesterday, what changed?” diff shows changes between files and folders, comm compares lists, cmp checks any two files byte by byte, and join combines tables on an ID. This lesson explains each and shows how every IT role uses them.',
    chips=['Tools by field', 'Reading a diff', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Two configs, two user lists, two tables
printf 'port=8080\\nlevel=info\\n' > a.conf; printf 'port=9090\\nlevel=info\\ntimeout=30\\n' > b.conf
diff -u a.conf b.conf
printf 'asha\\nkabir\\nravi\\n' > old.txt; printf 'asha\\nravi\\nriya\\n' > new.txt
echo 'new users:'; comm -13 old.txt new.txt
printf '1,Asha\\n2,Ravi\\n' > n.csv; printf '1,85000\\n2,52000\\n' > p.csv
join -t, n.csv p.csv
"""

RUN = dict(
    heading='diff, comm and join in a few lines',
    intro='<p>See a unified diff, the new users between two lists, and two CSVs joined on their ID.</p>',
    code=MAIN, expect='any',
    anno=[
        ('diff -u a.conf b.conf', '- old, + new.'),
        ("echo 'new users:'; comm -13 old.txt new.txt", 'riya'),
        ('join -t, n.csv p.csv', 'Name and pay together.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which lines start with +?', code=MAIN, expect='any'),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what are the two exit codes? Then run.',
             code="echo x > a; echo x > b; echo y > c\ndiff -q a b; echo $?\ndiff -q a c; echo $?\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> join misses row 1. Fix it by sorting.',
             code="printf '2,B\\n1,A\\n' > j1; printf '1,x\\n2,y\\n' > j2\njoin -t, j1 j2\n", expect='any'),
        dict(label='4 · Your turn', hint='Print the lines that are in both lists.',
             code="printf 'a\\nb\\nc\\n' > l1; printf 'b\\nc\\nd\\n' > l2\ncomm -12 l1 l2\n"),
        dict(label='5 · Challenge', hint='Make a patch from a.conf to b.conf and apply it to a.conf.',
             code="printf 'x=1\\n' > a.conf; printf 'x=2\\n' > b.conf\ndiff -u a.conf b.conf > p.patch; patch a.conf < p.patch; cat a.conf\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real configs and two servers',
    intro='<p>These need two machines or system files. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Compare a config with its package default', cmd='diff -u /usr/share/doc/openssh-server/examples/sshd_config /etc/ssh/sshd_config | head', output='-#PermitRootLogin prohibit-password\n+PermitRootLogin no', note='Typical (paths vary by package).'),
        dict(title='2 · Same file on two servers', cmd='diff <(ssh web01 cat /etc/nginx/nginx.conf) <(ssh web02 cat /etc/nginx/nginx.conf)', output='12c12\n<     worker_connections 1024;\n---\n>     worker_connections 768;', note='Typical: process substitution over SSH (Lesson 16.6).'),
        dict(title='3 · Checksums across servers', cmd='ssh web01 sha256sum /opt/app/app.jar; ssh web02 sha256sum /opt/app/app.jar', output='9f2c…e1  /opt/app/app.jar\n9f2c…e1  /opt/app/app.jar', note='Typical: equal hashes = identical files.'),
        dict(title='4 · Coloured diff', cmd='diff --color=always -u a.conf b.conf | less -R', output='(red - lines, green + lines)', note='Typical.'),
        dict(title='5 · Versions on our build machine', cmd='diff --version | head -1; patch --version | head -1', output=pc('diff --version | head -1; patch --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Comparisons and their exit codes',
    intro='<p>Step through a script that stores comparison results.</p>',
    code='''printf 'a\\nb\\n' > x; printf 'a\\nc\\n' > y
diff -q x y > /dev/null; d=$?
cmp -s x x; c=$?
both=$(comm -12 x y)
echo "diff=$d cmp_same=$c both=$both"
''',
    notes={1: 'Files :: Two small lists.', 2: 'diff :: 1 = different.', 3: 'cmp :: 0 = identical.', 4: 'comm :: Only a is in both.', 5: 'Report.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an admin’s config review, a data engineer’s reconciliation, and a security baseline check.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='What changed in the config?',
         problem='<p>Show the changes between yesterday’s backup of a config and today’s file, in unified format.</p>',
         inp='two versions of a config',
         approach=['diff -u old new.', 'Read - and + lines.'],
         code='''printf 'max_conn=100\\nlog=info\\n' > db.conf.bak; printf 'max_conn=500\\nlog=info\\nssl=on\\n' > db.conf
diff -u db.conf.bak db.conf | tail -n +3
''', expect='any',
         notes={2: 'Changes :: max_conn changed; ssl added.'},
         tryit='Use diff -y instead.'),
    dict(level='i', tag='Data engineer', title='Reconcile two exports',
         problem='<p>Orders in the shop export and the payment export: which are paid, which are unpaid, which payments have no order?</p>',
         inp='two ID lists',
         approach=['comm on sorted IDs.', '-12, -23, -13.'],
         code='''printf 'O1\\nO2\\nO3\\nO4\\n' > orders.txt; printf 'O2\\nO4\\nO9\\n' > paid.txt
echo "paid:    $(comm -12 orders.txt paid.txt | paste -sd,)"
echo "unpaid:  $(comm -23 orders.txt paid.txt | paste -sd,)"
echo "orphans: $(comm -13 orders.txt paid.txt | paste -sd,)"
''',
         notes={2: 'Both :: O2, O4.', 3: 'Only orders :: O1, O3.', 4: 'Only payments :: O9.'},
         tryit='Add O5 to both files.'),
    dict(level='a', tag='Security', title='New SUID files since the baseline',
         problem='<p>Compare today’s list of SUID programs with an approved baseline and report new ones.</p>',
         inp='two file lists',
         approach=['Sort both.', 'comm -13.'],
         code='''printf '/usr/bin/passwd\\n/usr/bin/sudo\\n' > baseline.txt
printf '/usr/bin/sudo\\n/tmp/.x/bash\\n/usr/bin/passwd\\n' > today.txt
comm -13 <(sort baseline.txt) <(sort today.txt)
''',
         notes={3: 'Alert :: A SUID shell in /tmp is a classic backdoor (Lesson 9.4).'},
         tryit='Real list: find / -perm -4000 -type f 2>/dev/null.'),
]

QUIZ = mix([
    dict(q='diff exits with 1. What does that mean?', options=['error', 'files differ', 'files identical', 'file missing'], answer=1,
         why='0 same, 1 different, 2 trouble.'),
    dict(q='In diff -u output, a line starting with + is…', options=['in the first file only', 'in the second file only', 'in both', 'a comment'], answer=1,
         why='+ added in the new file.'),
    dict(q='Which shows lines only in file A (both sorted)?', options=['comm -12', 'comm -23', 'comm -13', 'comm -3'], answer=1,
         why='Hide columns 2 and 3.'),
    dict(q='Which compares two jar files byte by byte?', options=['diff -u', 'cmp', 'comm', 'join'], answer=1,
         why='cmp works on any bytes.'),
    dict(q='join gives fewer rows than expected. The most likely reason?', options=['files too big', 'inputs not sorted on the key', 'wrong locale only', 'join is broken'], answer=1,
         why='join needs sorted keys.'),
    dict(q='How do you undo a patch?', options=['patch -u', 'patch -R', 'diff -R', 'unpatch'], answer=1,
         why='-R reverses.'),
    dict(q='Which lists files that differ between two folders?', options=['diff -rq a b', 'cmp -r a b', 'comm a b', 'join a b'], answer=0,
         why='-r recursive, -q names only.'),
    dict(q='join -a 1 -e NULL without -o auto…', options=['fills NULL', 'does not fill missing fields', 'errors', 'drops file 1 rows'], answer=1,
         why='-e works with -o.'),
])

REVISION = [
    '<code>diff a b</code>: 1c1 change, 3a4 add, 5d4 delete; &lt; first file, &gt; second. Exit 0 / 1 / 2.',
    '<code>diff -u</code> (- old, + new, @@ hunks), <code>-y</code> side by side, <code>-q</code> brief, <code>-r</code> folders, <code>-w -b -B -i</code> ignore.',
    '<code>patch --dry-run</code>, <code>patch -b f &lt; p</code>, <code>patch -R</code> to undo.',
    '<code>comm</code> needs sorted input: <code>-12</code> both, <code>-23</code> only A, <code>-13</code> only B, <code>-3</code> either; union = <code>sort -u A B</code>.',
    '<code>cmp -s</code> for any files; <code>sha256sum</code> across machines.',
    '<code>join -t,</code> on sorted keys; <code>-1/-2</code> key fields; <code>-a</code> outer; <code>-v</code> anti; <code>-e X -o auto</code>.',
    'Compare command outputs: <code>diff &lt;(cmd1) &lt;(cmd2)</code>.',
    'Every line changed? Check Windows line endings with <code>cat -A</code>.',
]

FAQ = [
    ('How do I compare two files in Linux?', 'diff file1 file2 for text (diff -u for the unified format), cmp for binary files.'),
    ('How do I compare two directories?', 'diff -rq dir1 dir2 lists files that differ or exist on one side only.'),
    ('What does the output of diff mean?', 'Normal format: “3a4” add, “1c1” change, “5d4” delete; < lines from the first file, > from the second. Unified: - removed, + added.'),
    ('How do I find lines common to two files?', 'comm -12 <(sort a) <(sort b).'),
    ('How do I join two CSV files on a column?', 'Sort both on that column, then join -t, (use -1/-2 for other columns, -a for outer joins).'),
    ('How do I create and apply a patch?', 'diff -u old new > fix.patch; patch old < fix.patch (patch -R to undo).'),
    ('Why does diff show every line as changed?', 'Often one file has Windows line endings (\\r\\n). Check with cat -A.'),
]

PRACTICE_INTRO = 'Small comparison tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Same?', stmt='Print same if x.txt and y.txt are identical, else different.', inp='two files',
         code="echo hi > x.txt; echo hi > y.txt\ncmp -s x.txt y.txt && echo same || echo different\n", explain='cmp -s uses only the exit code.'),
    dict(level='easy', title='Brief diff', stmt='Report whether two files differ, in one line.', inp='two files',
         code="echo a > p; echo b > q\ndiff -q p q\n", explain='-q is brief.', expect='any'),
    dict(level='easy', title='In both', stmt='Print lines in both sorted lists.', inp='two lists',
         code="printf 'a\\nb\\n' > l1; printf 'b\\nc\\n' > l2\ncomm -12 l1 l2\n", explain='-12 hides columns 1 and 2.'),
    dict(level='medium', title='Only in the first', stmt='Print lines only in l1.', inp='two lists',
         code="printf 'a\\nb\\n' > l1; printf 'b\\nc\\n' > l2\ncomm -23 l1 l2\n", explain='-23.'),
    dict(level='medium', title='Unified diff', stmt='Show the unified diff without the two header lines.', inp='two configs',
         code="printf 'x=1\\ny=2\\n' > o; printf 'x=1\\ny=3\\n' > n\ndiff -u o n | tail -n +3\n", explain='tail skips the --- and +++ lines.', expect='any'),
    dict(level='medium', title='Join', stmt='Join id,name and id,city files on id.', inp='two CSVs',
         code="printf '1,Asha\\n2,Ravi\\n' > a.csv; printf '1,Pune\\n2,Agra\\n' > b.csv\njoin -t, a.csv b.csv\n", explain='Inner join on field 1.'),
    dict(level='business', title='Left join', stmt='All names, with city or NA.', inp='two CSVs, one city missing',
         code="printf '1,Asha\\n2,Ravi\\n3,Meena\\n' > a.csv; printf '1,Pune\\n3,Goa\\n' > b.csv\njoin -t, -a 1 -e NA -o auto a.csv b.csv\n", explain='-a 1 keeps every name; -e with -o auto fills NA.'),
    dict(level='business', title='Folder check', stmt='Which files differ between two release folders?', inp='two folders',
         code="mkdir -p r1 r2; echo 1 > r1/a; echo 1 > r2/a; echo 2 > r1/b; echo 3 > r2/b\ndiff -rq r1 r2\n", explain='Only b differs.', expect='any'),
]

SCN_INTRO = 'Interview questions about comparing files, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you compare two files?”',
        'A common first-round question.',
        'do you know diff and its output?',
        '''<ul>
          <li><code>diff a b</code>; explain &lt; and &gt;, and a/c/d.</li>
          <li><code>diff -u</code> for reviews; <code>diff -rq</code> for folders.</li>
          <li>Binary: <code>cmp</code>; exit codes 0/1/2.</li>
        </ul>''', 'saying “open both in an editor”.') +
    scn('Operations', 'Junior', 'One server of a pair misbehaves',
        'Two load-balanced servers should be identical, but one returns errors.',
        'can you find configuration drift?',
        '''<ol>
          <li><code>diff &lt;(ssh a cat /etc/app.conf) &lt;(ssh b cat /etc/app.conf)</code>.</li>
          <li>Packages: <code>comm -3 &lt;(ssh a dpkg-query -W | sort) &lt;(ssh b dpkg-query -W | sort)</code>.</li>
          <li>Binaries: compare sha256sum of the deployed files.</li>
        </ol>''', 'redeploying both and hoping.') +
    scn('Data team', 'Mid-level', 'The finance export does not match the CRM',
        '50,000 customer IDs in one file, 49,980 in the other.',
        'can you do set operations quickly?',
        '''<ul>
          <li>Extract IDs, <code>sort -u</code> both, <code>comm -23</code> / <code>-13</code> for each side’s extras.</li>
          <li><code>join -v</code> keeps whole rows for the report.</li>
          <li>Watch for whitespace and case: normalise with tr/sed first.</li>
        </ul>''', 'eyeballing in a spreadsheet.') +
    scn('Platform', 'Senior', 'Patching 200 servers safely',
        'A one-line config change must go to 200 servers, and must be reversible.',
        'do you know patch and its safety options?',
        '''<ul>
          <li>Make a unified diff from a tested server; apply with <code>patch --dry-run</code> then <code>patch -b</code>.</li>
          <li>Roll back with <code>patch -R</code> or the .orig backup.</li>
          <li>At scale use configuration management (Ansible), which shows a diff before changing.</li>
        </ul>''', 'scp-ing a whole config over every server’s own changes.')
) + interview([
    ('What does diff -u do?', 'Prints a unified diff with context: - removed, + added.'),
    ('How do you compare two directories?', 'diff -r (add -q for names only).'),
    ('Difference between diff and cmp?', 'diff: line-based changes for text; cmp: first differing byte, any file.'),
    ('What does comm need?', 'Both inputs sorted; it prints only-A, only-B and both columns.'),
    ('How do you apply and reverse a patch?', 'patch file < p; patch -R file < p.'),
    ('How do you do a left join on two files?', 'join -a 1 (with -t, and sorted keys).'),
    ('What exit codes does diff return?', '0 same, 1 different, 2 trouble.'),
], [
    ('RHCSA (EX200)', 'Comparing files and analysing text are part of “understand and use essential tools”.'),
    ('LFCS', 'Essential commands: compare and manipulate file content (diff, comm, patch).'),
    ('CompTIA Linux+', 'File comparison and text utilities: diff, comm, cmp, join.'),
]) + distro('diffutils and coreutils on Linux; BSD versions on macOS.', [
    ('diff -u -y -r -q', 'GNU diffutils', 'GNU', 'BSD/Apple diff: same main options', 'GNU'),
    ('diff --color', 'yes', 'yes', 'recent macOS yes', 'yes'),
    ('patch', 'install patch on minimal', 'yes', 'yes', 'WSL yes; Git Bash yes'),
    ('comm / join', 'GNU', 'GNU', 'BSD (no -o auto)', 'GNU'),
    ('cmp', 'diffutils', 'diffutils', 'yes', 'yes'),
    ('vimdiff', 'with vim', 'with vim', 'yes', 'WSL yes'),
]) + teaser('6.4', 'Riya must change http:// to https:// in 300 config files, delete every comment line, and add a header line at the top of each, without opening any file in an editor. One command can edit files in place: which one, and how does she keep a backup?')

CHEATSHEET = cheatsheet('comparing files', [
    ('diff', [('diff a b', 'normal'), ('diff -u a b', 'unified'), ('diff -y -W 80', 'side by side'), ('diff -q / -rq', 'brief / folders'), ('-w -b -B -i', 'ignore')]),
    ('patch', [('diff -u o n > p', 'make'), ('patch --dry-run f < p', 'test'), ('patch -b f < p', 'apply + backup'), ('patch -R f < p', 'undo'), ('-p1', 'git paths')]),
    ('comm (sorted)', [('comm -12 A B', 'both'), ('comm -23 A B', 'only A'), ('comm -13 A B', 'only B'), ('comm -3 A B', 'either'), ('sort -u A B', 'union')]),
    ('cmp', [('cmp a b', 'first difference'), ('cmp -s a b', 'exit code'), ('cmp -l a b', 'all bytes'), ('sha256sum a b', 'across machines'), ('0 / 1 / 2', 'same / differ / error')]),
    ('join (sorted)', [('join -t, a b', 'inner'), ('-a 1', 'left'), ('-a 1 -a 2', 'full'), ('-v 1', 'anti'), ('-e NA -o auto', 'fill blanks')]),
])

MINDMAP = mindmap('Comparing files', [
    ('diff', 'blue', ['-u - and +', '-rq folders', 'exit 0/1/2']),
    ('patch', 'green', ['--dry-run', '-b backup', '-R undo']),
    ('comm', 'amber', ['sorted lists', '-12 -23 -13', 'set operations']),
    ('cmp', 'violet', ['any bytes', '-s scripts', 'sha256sum']),
    ('join', 'acc', ['sorted on key', '-t, -1 -2', '-a -v -e -o']),
    ('Traps', 'red', ['unsorted input', 'CRLF line ends', '-e without -o']),
])

LAB = lab('compare yesterday and today', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab63 && cd ~/lab63 && rm -f *
printf 'asha\\nkabir\\nmeena\\nravi\\n' > yesterday.txt
printf 'arjun\\nasha\\nmeena\\nravi\\nriya\\n' > today.txt
printf 'port=8080\\nlevel=info\\n' > a.conf; printf 'port=9090\\nlevel=info\\n' > b.conf
printf '1,Asha\\n2,Ravi\\n3,Meena\\n' > names.csv; printf '1,85000\\n3,98000\\n' > pay.csv''',
    tasks=['Write the new users (in today.txt but not yesterday.txt) into <code>added.txt</code>.',
           'Write the removed user into <code>removed.txt</code>.',
           'Save the unified diff from a.conf to b.conf as <code>change.patch</code>.',
           'Write the names with no pay row (just the line from names.csv) into <code>nopay.txt</code>.'],
    solution='''comm -13 yesterday.txt today.txt > added.txt
comm -23 yesterday.txt today.txt > removed.txt
diff -u a.conf b.conf > change.patch
join -t, -v 1 names.csv pay.csv > nopay.txt''',
    check='''cd ~/lab63
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 added users"     '[ "$(cat added.txt 2>/dev/null)" = "$(printf "arjun\\nriya")" ]'
ok "2 removed user"    '[ "$(cat removed.txt 2>/dev/null)" = kabir ]'
ok "3 unified patch"   'grep -qx -- "-port=8080" change.patch 2>/dev/null && grep -qx -- "+port=9090" change.patch'
ok "4 no pay"          '[ "$(cat nopay.txt 2>/dev/null)" = "2,Ravi" ]' ''')
