import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='13-one-liners', lesson='07-100-must-know-one-liners', n='13.7',
    module_label='Module 13 · Power one-liners and command combos',
    title='100 must-know Linux one-liners: cheat sheet and challenge',
    desc='100 everyday Linux one-liners grouped by job (files and folders, viewing and searching, transforming text, counting and statistics, processes, disk and memory, users and permissions, archives and checksums, system and network, shell tricks), every one really run with its output and a one-line explanation; the six patterns behind them, safety checks, a self-test script, a challenge quiz and a ten-task lab.',
    og_desc='100 must-know Linux one-liners, each really run with real output, grouped by job, plus the six patterns behind them and a challenge.',
    minutes=50, level='Beginner → Advanced',
    lead='The reference to bookmark: 100 one-liners by job, each tested with real output, the six patterns that generate them, and a challenge to check yourself.',
    chips=['100 tested one-liners', 'Six patterns', 'Safety checklist animated', 'Ten-task challenge lab', 'Real Bash in your browser'],
)

MAIN = """# Ten of the hundred, on a tiny sample
printf 'alpha\\nbeta\\ngamma\\nbeta\\n' > words.txt
printf 'name,dept,salary\\nRiya,IT,72000\\nAman,HR,51000\\nZoya,IT,88000\\n' > staff.csv
sort words.txt | uniq -c | sort -rn | head -1                        # 33 count and rank
awk -F, 'NR>1{s+=$3} END{print s}' staff.csv                          # 35 sum a column
awk -F, 'NR>1{t[$2]+=$3} END{for(d in t) print d, t[d]}' staff.csv    # 38 group
tail -n +2 staff.csv | sort -t, -k3 -rn | head -1 | cut -d, -f1       # 37 max
sed -n '2,3p' words.txt                                               # 12 slice
grep -c beta words.txt                                                # count matches
echo 'a    b' | tr -s ' '                                             # 25 squeeze
seq -s ' ' 1 2 9                                                      # 97 sequence
echo $((7 * 6))                                                       # 99 calculator
diff <(echo a) <(echo b) | grep '^[<>]'                               # 95 compare
"""

RUN = dict(
    heading='Ten of the hundred',
    intro='<p>Ten one-liners from different groups on a tiny sample. Change a number or a pattern and run again.</p>',
    code=MAIN,
    anno=[("sort | uniq -c | sort -rn", 'The count-and-rank pattern.'), ("t[$2]+=$3", 'The group pattern.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which department has the larger total?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does each line print?',
             code="echo 'one two three' | wc -w\necho 'a,b,c' | cut -d, -f3\nseq 3 | tac | paste -sd' '\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> uniq -c without sort splits the counts.',
             code="printf 'x\\ny\\nx\\n' | uniq -c\n"),
        dict(label='4 · Your turn', hint='Adapt the group pattern: count staff per department.',
             code="printf 'name,dept\\nRiya,IT\\nAman,HR\\nZoya,IT\\n' > s.csv\nawk -F, 'NR>1{n[$2]++} END{for(d in n) print d, n[d]}' s.csv | sort\n"),
        dict(label='5 · Challenge', hint='Top 2 most frequent words in a sentence.',
             code="echo 'the cat and the dog and the bird' | tr ' ' '\\n' | sort | uniq -c | sort -rn | head -2\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: make them yours',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Save favourites as functions', cmd="cat >> ~/.bashrc <<'EOF'\ntopn(){ sort | uniq -c | sort -rn | head -\"${1:-10}\"; }\nbiggest(){ du -sh \"${1:-.}\"/* 2>/dev/null | sort -rh | head; }\nEOF\nsource ~/.bashrc\nawk '{print $1}' access.log | topn 5", output='   812 10.0.0.5\n   433 10.0.0.7\n…', note='Typical.'),
        dict(title='2 · Your history’s most used commands', cmd="history | awk '{print $2}' | sort | uniq -c | sort -rn | head -5", output='   212 cd\n   180 ls\n    97 git\n    64 grep\n    41 sudo', note='Typical: a one-liner about one-liners.'),
        dict(title='3 · Check tools on a new server', cmd='for t in rsync ss lsof jq tmux; do command -v $t > /dev/null || echo "missing: $t"; done', output='missing: jq', note='Typical.'),
        dict(title='4 · Versions here', cmd='bash --version | head -1; awk -W version 2>&1 | head -1', output=pc('bash --version | head -1; awk -W version 2>&1 | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='The count pattern, line by line',
    intro='<p>Step through each stage of sort | uniq -c | sort -rn | head.</p>',
    code='''words="b a b c b a"
lines=$(echo $words | tr ' ' '\\n')
sorted=$(echo "$lines" | sort)
counted=$(echo "$sorted" | uniq -c)
top=$(echo "$counted" | sort -rn | head -1)
echo "top: $top"
''',
    notes={2: 'One word per line.', 3: 'Equal words together.', 4: 'Count each.', 5: 'Biggest first, keep one.'},
)

WORKED_INTRO = 'Three tasks solved by adapting one-liners from the 100.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Which file types fill a folder?',
         problem='<p>Count files per extension in a folder, most first.</p>',
         inp='files', approach=['find -type f.', '${f##*.} via sed.', 'count pattern.'],
         code='''mkdir -p f; touch f/a.log f/b.log f/c.txt f/d.log f/e.csv
find f -type f | sed 's/.*\\.//' | sort | uniq -c | sort -rn
''', notes={2: 'Extension, then the count pattern.'}, tryit='Add the total size per extension with du.'),
    dict(level='i', tag='Data', title='Average per group with a header',
         problem='<p>Average salary per department, rounded.</p>',
         inp='a CSV', approach=['group pattern with two arrays.'],
         code='''printf 'name,dept,salary\\nRiya,IT,72000\\nAman,HR,51000\\nZoya,IT,88000\\nRavi,HR,47000\\n' > s.csv
awk -F, 'NR>1{t[$2]+=$3; n[$2]++} END{for(d in t) printf "%s %.0f\\n", d, t[d]/n[d]}' s.csv | sort
''', notes={2: 'Sum and count per key.'}, tryit='Print only departments above 60000.'),
    dict(level='a', tag='DevOps', title='Compare two environments',
         problem='<p>Show settings that differ between dev.env and prod.env.</p>',
         inp='two files', approach=['compare pattern with sort.'],
         code='''printf 'A=1\\nB=2\\nC=3\\n' > dev.env; printf 'A=1\\nB=5\\nD=4\\n' > prod.env
diff <(sort dev.env) <(sort prod.env) | grep '^[<>]'
comm -3 <(cut -d= -f1 dev.env | sort) <(cut -d= -f1 prod.env | sort)
''', notes={2: 'Values that differ.', 3: 'Keys only in one file.'}, tryit='Print the differences as KEY: dev -> prod.'),
]

QUIZ = mix([
    dict(q='Top 3 most frequent lines:', options=['sort | uniq -c | sort -rn | head -3', 'uniq -c | head -3', 'sort -u | head -3', 'wc -l'], answer=0, why='Count pattern.'),
    dict(q='Sum column 3 of a CSV with a header:', options=["awk -F, 'NR>1{s+=$3} END{print s}'", 'cut -f3 | wc', 'sort -k3', 'grep -c ,'], answer=0, why='awk sum.'),
    dict(q='Lines 5 to 10:', options=["sed -n '5,10p'", 'head -10', 'tail -5', 'grep 5-10'], answer=0, why='sed -n range.'),
    dict(q='Remove Windows line endings:', options=["tr -d '\\r'", 'dos', 'sed s/n//', 'cut -c1'], answer=0, why='Delete \\r.'),
    dict(q='Files bigger than 1 GB:', options=['find / -size +1G', 'ls -S /', 'du -1G', 'df -h'], answer=0, why='find -size.'),
    dict(q='Run a command with a time limit:', options=['timeout 10 cmd', 'sleep 10 cmd', 'limit cmd', 'nice cmd'], answer=0, why='timeout.'),
    dict(q='Check files against a list of checksums:', options=['sha256sum -c SUMS', 'diff SUMS', 'cmp SUMS', 'md5 SUMS'], answer=0, why='-c.'),
    dict(q='Make a tar.gz of src:', options=['tar czf src.tgz src', 'tar x src', 'zip src', 'gzip src'], answer=0, why='c = create, z = gzip.'),
    dict(q='Default permissions for new files are set by…', options=['umask', 'chmod', 'chown', 'stat'], answer=0, why='umask.'),
    dict(q='Last argument of the previous command:', options=['$_', '$!', '$?', '$$'], answer=0, why='$_.'),
])

REVISION = [
    'Six patterns: count (sort | uniq -c | sort -rn), group (awk arrays), bulk (find -exec), loop (for/while), compare (diff/comm <( )), chain (&& ||).',
    'Files 1–10, search 11–20, transform 21–30, count 31–40, processes 41–50, disk 51–60, users 61–70, archives 71–80, system 81–90, shell 91–100.',
    'Before running any one-liner: tool exists, read each stage, sample data, read-only first.',
    'Quote file names, use -- before names, LC_ALL=C for reproducible sorting.',
    'GNU vs BSD options differ (sed -i, find -printf, date -d).',
    'Turn the ones you repeat into aliases, functions or scripts.',
]

FAQ = [
    ('What are the most useful Linux one-liners?', 'Counting and ranking (sort | uniq -c | sort -rn), summing columns with awk, finding big or old files with find, searching with grep -rn, and checking disk with du | sort -rh.'),
    ('How do I count the most frequent words in a file?', "tr -s ' ' '\\n' < file | sort | uniq -c | sort -rn | head."),
    ('How do I find large files?', 'find / -xdev -type f -size +500M, or du -ah DIR | sort -rh | head.'),
    ('How do I sum a column?', "awk '{s+=$N} END{print s}' file (add -F, and NR>1 for CSV with a header)."),
    ('Are one-liners from the internet safe?', 'Only after reading each part, checking the tools exist and running a read-only version on sample data.'),
    ('How do I keep my favourite one-liners?', 'As aliases or functions in ~/.bashrc, or small scripts in ~/bin.'),
    ('Do these work on macOS?', 'Most do; GNU-specific options (sed -i, find -printf, date -d) differ on BSD tools.'),
]

PRACTICE_INTRO = 'Ten quick challenges. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Count words', stmt='How many words in “one two three four”?', inp='text', code="echo 'one two three four' | wc -w\n", explain='4.'),
    dict(level='easy', title='Third field', stmt='Print the third field of a:b:c:d.', inp='text', code="echo 'a:b:c:d' | cut -d: -f3\n", explain='c.'),
    dict(level='easy', title='Reverse', stmt='Print 1 2 3 in reverse order, one line.', inp='nothing', code="seq 3 | tac | paste -sd' '\n", explain='3 2 1.'),
    dict(level='medium', title='Most frequent', stmt='Most frequent letter in a b a c a.', inp='letters', code="printf 'a\\nb\\na\\nc\\na\\n' | sort | uniq -c | sort -rn | head -1\n", explain='3 a.'),
    dict(level='medium', title='Average', stmt='Average of 10, 20, 60.', inp='numbers', code="printf '10\\n20\\n60\\n' | awk '{s+=$1} END{print s/NR}'\n", explain='30.'),
    dict(level='medium', title='Upper', stmt='Upper-case “linux rocks”.', inp='text', code="echo 'linux rocks' | tr a-z A-Z\n", explain='LINUX ROCKS.'),
    dict(level='business', title='Group count', stmt='Count per key in a / b / a / a.', inp='keys', code="printf 'a\\nb\\na\\na\\n' | awk '{n[$1]++} END{for(k in n) print k, n[k]}' | sort\n", explain='a 3, b 1.'),
    dict(level='business', title='Only in A', stmt='Lines in (x y z) but not in (y).', inp='lists', code="comm -23 <(printf 'x\\ny\\nz\\n') <(echo y)\n", explain='x, z.'),
]

SCN_INTRO = 'One-liner interview questions, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Top 5 most common words in a file”', 'Very common.', 'one-liner?',
        '''<ul>
          <li>tr -s ' ' '\\n' &lt; f | sort | uniq -c | sort -rn | head -5</li>
          <li>Explain why sort comes before uniq.</li>
          <li>Mention tr -cs for punctuation.</li>
        </ul>''', 'a 30-line script.') +
    scn('Service company', 'Junior', '“Find and delete .tmp files older than 7 days”', 'Classic.', 'safe?',
        '''<ol>
          <li>find DIR -name '*.tmp' -mtime +7 (preview).</li>
          <li>Same with -delete at the end.</li>
          <li>Or -exec rm {} +.</li>
        </ol>''', 'rm -rf *.tmp with no age test.') +
    scn('Product company', 'Mid-level', '“Average response time per endpoint from a log”', 'Live coding.', 'awk?',
        '''<ul>
          <li>awk '{t[$7]+=$NF; n[$7]++} END{for(u in t) print u, t[u]/n[u]}'</li>
          <li>Sort by the average.</li>
          <li>Discuss p95 vs average.</li>
        </ul>''', 'Excel.') +
    scn('Platform', 'Senior', '“Your one-liner fails on the new servers”', 'Minimal images.', 'how to make it robust?',
        '''<ul>
          <li>command -v checks; fallbacks (ss → lsof → /proc).</li>
          <li>LC_ALL=C, quoting, set -euo pipefail in scripts.</li>
          <li>Avoid GNU-only options or detect them.</li>
        </ul>''', 'installing tools by hand everywhere.')
) + interview([
    ('Count lines in a file?', 'wc -l < file.'),
    ('Print a column?', 'cut -dD -fN or awk.'),
    ('Unique values?', 'sort -u.'),
    ('Find text recursively?', 'grep -rn PATTERN DIR.'),
    ('Biggest folders?', 'du -sh * | sort -rh | head.'),
    ('Time limit?', 'timeout N cmd.'),
    ('Compare two outputs?', 'diff <(a) <(b).'),
], [
    ('RHCSA / LFCS', 'Text, files, processes and archives with standard tools.'),
    ('DevOps / SRE interviews', 'Log and data one-liners.'),
    ('CompTIA Linux+', 'Command-line tasks.'),
]) + distro('The 100 use standard tools; a few options are GNU-only.', [
    ('sort, uniq, cut, tr, awk', 'yes', 'yes', 'yes (BSD)', 'Git Bash'),
    ('sed -i.bak', 'yes', 'yes', "sed -i '.bak' (BSD)", '-'),
    ('find -printf', 'yes', 'yes', 'no', '-'),
    ('date -d', 'yes', 'yes', 'date -j -f (BSD)', '-'),
    ('tac', 'yes', 'yes', 'tail -r', '-'),
]) + teaser('14.1', 'Module 13 is done. Next: software. Where do programs come from on Linux, what is a package and a repository, and how do apt, dnf, snap and building from source fit together? Module 14 starts with packages and repositories.')

CHEATSHEET = cheatsheet('Top one-liners', [
    ('Count / sum', [('sort | uniq -c | sort -rn', 'rank'), ("awk '{s+=$N} END{print s}'", 'sum'), ("awk '{t[$k]+=$v}'", 'group'), ('wc -l', 'lines')]),
    ('Search / slice', [('grep -rn X .', 'search'), ("sed -n '5,10p'", 'slice'), ('grep -v ^#', 'no comments'), ('head / tail', 'ends')]),
    ('Files / disk', [('du -sh * | sort -rh', 'biggest'), ('find -size +1G', 'big files'), ('find -mtime +30', 'old'), ('df -h / df -i', 'space')]),
    ('Shell', [('cd -', 'back'), ('$_', 'last arg'), ('diff <(a) <(b)', 'compare'), ('timeout N cmd', 'limit')]),
])

MINDMAP = mindmap('100 one-liners', [
    ('Files', 'blue', ['mkdir -p', 'find', 'rename']),
    ('Text', 'green', ['grep', 'sed', 'tr cut']),
    ('Numbers', 'amber', ['uniq -c', 'awk sum', 'group']),
    ('System', 'violet', ['ps', 'df du', 'uname']),
    ('Safety', 'red', ['command -v', 'read-only', 'quotes']),
    ('Patterns', 'acc', ['count', 'bulk', 'compare']),
])

LAB = lab('ten tasks, one line each', 'Build the lab, write <code>~/lab137/answers.sh</code> with one line per task (each writes its answer file), then run the checker.',
    setup='''mkdir -p ~/lab137 && cd ~/lab137 && rm -rf answers.sh a*.txt data
mkdir -p data/logs; printf 'red\\nblue\\nred\\ngreen\\nred\\nblue\\n' > data/colors.txt
printf 'item,qty\\npen,4\\nbag,1\\npen,6\\n' > data/orders.csv
printf 'INFO ok\\nERROR x\\nINFO ok\\nERROR y\\nWARN z\\n' > data/logs/app.log
head -c 1500000 /dev/zero > data/big.bin; touch data/small.txt''',
    tasks=['a1: the number of lines in colors.txt.',
           'a2: the most frequent colour (just the word).',
           'a3: the number of unique colours.',
           'a4: the total qty in orders.csv (skip the header).',
           'a5: the total qty for pen.',
           'a6: the number of ERROR lines in app.log.',
           'a7: the names (just file names) of files under data bigger than 1 MB.',
           'a8: the lines of app.log that are not INFO, in order.',
           'a9: colours sorted alphabetically and unique, on one line separated by spaces.',
           'a10: the checksum line of data/small.txt as sha256sum prints it, run from inside data.'],
    solution='''cat > answers.sh <<'EOF'
cd ~/lab137/data
wc -l < colors.txt > ../a1.txt
sort colors.txt | uniq -c | sort -rn | awk 'NR==1{print $2}' > ../a2.txt
sort -u colors.txt | wc -l > ../a3.txt
awk -F, 'NR>1{s+=$2} END{print s}' orders.csv > ../a4.txt
awk -F, '$1=="pen"{s+=$2} END{print s}' orders.csv > ../a5.txt
grep -c ERROR logs/app.log > ../a6.txt
find . -type f -size +1M -printf '%f\\n' > ../a7.txt
grep -v '^INFO' logs/app.log > ../a8.txt
sort -u colors.txt | paste -sd' ' > ../a9.txt
sha256sum small.txt > ../a10.txt
EOF''',
    check='''cd ~/lab137; rm -f a*.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f answers.sh ] && bash answers.sh 2>/dev/null
ok "a1"  '[ "$(cat a1.txt 2>/dev/null)" = 6 ]'
ok "a2"  '[ "$(cat a2.txt 2>/dev/null)" = red ]'
ok "a3"  '[ "$(cat a3.txt 2>/dev/null)" = 3 ]'
ok "a4"  '[ "$(cat a4.txt 2>/dev/null)" = 11 ]'
ok "a5"  '[ "$(cat a5.txt 2>/dev/null)" = 10 ]'
ok "a6"  '[ "$(cat a6.txt 2>/dev/null)" = 2 ]'
ok "a7"  '[ "$(cat a7.txt 2>/dev/null)" = big.bin ]'
ok "a8"  '[ "$(cat a8.txt 2>/dev/null | tr "\\n" "|")" = "ERROR x|ERROR y|WARN z|" ]'
ok "a9"  '[ "$(cat a9.txt 2>/dev/null)" = "blue green red" ]'
ok "a10" '[ "$(cat a10.txt 2>/dev/null)" = "$(cd data && sha256sum small.txt)" ]' ''')
