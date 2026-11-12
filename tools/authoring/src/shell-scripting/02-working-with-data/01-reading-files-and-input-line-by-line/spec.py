import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)
_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index('SS = r"""') + 9
SS = _s[_i:_s.index('"""', _i)]

META = dict(
    module='02-working-with-data', lesson='01-reading-files-and-input-line-by-line', n='2.1',
    module_label='Module 2 · Working with data',
    title='Reading files and input line by line: while read, IFS and mapfile',
    desc='Read files safely in Bash: while IFS= read -r line, the last line without a newline, fields with IFS and read -r a b c, comments and blank lines, CSV-like and passwd files, mapfile/readarray, process substitution, the subshell trap of pipes and the stdin trap of ssh, Windows line endings, with every run real and 35+ examples.',
    og_desc='while IFS= read -r, IFS fields, mapfile, the pipe subshell trap and ssh -n, with real runs on messy files.',
    minutes=35, level='Beginner → Intermediate',
    lead='One loop that never loses a line, a space or a backslash, and the two traps that make loops silently do less than you think.',
    chips=['Messy real files', 'read animated four ways', 'Subshell trap explained', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """printf 'Sales Q3.xlsx\\nbuild\\\\01\\n  indented\\nlast line, no newline' > list.txt

echo '--- for over $(cat): words, not lines'
for x in $(cat list.txt); do printf '[%s] ' "$x"; done; echo

echo '--- while IFS= read -r || [[ -n $line ]]: exact lines'
while IFS= read -r line || [[ -n $line ]]; do
  printf '[%s]\\n' "$line"
done < list.txt
"""

RUN = dict(
    heading='Words vs lines in your browser',
    intro='<p>The same four-line file, read two ways.</p>',
    code=MAIN,
    anno=[('$(cat list.txt)', 'One string, split on every space.'), ('IFS= read -r', 'Exactly one raw line.'), ('|| [[ -n $line ]]', 'Keeps the last line.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Count the items each loop prints.', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what is b?',
             code="read -r a b <<< 'one two three'\necho \"a=$a b=$b\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> count stays 0 because of the pipe. Use done < <(…).',
             code="count=0\nprintf 'a\\nb\\nc\\n' | while read -r x; do count=$((count+1)); done\necho \"count=$count\"\n"),
        dict(label='4 · Your turn', hint='Split on commas.',
             code="while IFS=, read -r name city; do echo \"$name lives in $city\"; done <<< $'Asha,Pune\\nRavi,Delhi'\n"),
        dict(label='5 · Challenge', hint='Load lines into an array and print the count and the last one.',
             code="mapfile -t a < <(printf 'x\\ny\\nz\\n')\necho \"${#a[@]} items, last=${a[-1]}\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Try the loops on your own lists. Outputs below are from our build machine.</p>',
    items=[
        dict(title='1 · Count lines both ways', cmd="wc -l < hosts.txt\nmapfile -t a < hosts.txt; echo ${#a[@]}", output='6\n7', note='Real output: the last line has no newline.'),
        dict(title='2 · Fields', cmd="while read -r h ip env || [[ -n $h ]]; do [[ -z $h || $h == \\#* ]] || echo \"$h $env\"; done < hosts.txt", output='web01 prod\nweb02 prod\ndb01 prod\ntest01 test\nbuild\\01 ci', note='Real output.'),
        dict(title='3 · ssh in a loop', cmd="while read -r h _; do ssh -n \"$h\" uptime; done < prod-hosts.txt", output='web01:  02:00:01 up 41 days, load average: 0.10, 0.08, 0.05\nweb02:  02:00:02 up 41 days, load average: 0.22, 0.15, 0.10', note='Typical; without -n only web01 would answer.'),
        dict(title='4 · Windows file', cmd="file users.csv\ndos2unix users.csv", output='users.csv: CSV text, with CRLF line terminators\ndos2unix: converting file users.csv to Unix format...', note='Typical.'),
    ],
)

TRACE = dict(
    heading='The safe loop, line by line',
    intro='<p>Watch read take one line per round.</p>',
    code='''printf 'web01 prod\\nweb02 prod\\ntest01 test' > h.txt
n=0
while read -r host env || [[ -n $host ]]; do
  n=$((n + 1))
  echo "$n: $host ($env)"
done < h.txt
echo "total $n"
''',
    notes={3: 'One line per round; the third has no newline.', 7: 'n survives: no pipe.'},
)

WORKED_INTRO = 'Three real lists processed safely.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Check that every listed file exists',
         problem='<p>Report missing files from a list whose names contain spaces.</p>',
         inp='a list file', approach=['Safe loop, -e test.'],
         code='''touch 'Sales Q3.xlsx' notes.txt
printf 'Sales Q3.xlsx\\nnotes.txt\\nold report.pdf\\n' > list.txt
missing=0
while IFS= read -r f; do
  [[ -e $f ]] && echo "ok       $f" || { echo "MISSING  $f"; ((++missing)); }
done < list.txt
echo "$missing missing"
''', notes={5: '"$f" would be needed in commands; [[ ]] is safe without.'}, tryit='Exit 1 when something is missing.'),
    dict(level='i', tag='Data', title='Sum a column from a CSV',
         problem='<p>Total the amount column per city, skipping the header.</p>',
         inp='a CSV', approach=['IFS=, + associative array.'],
         code='''printf 'id,city,amount\\n1,Pune,450\\n2,Mumbai,1200\\n3,Pune,300\\n' > o.csv
declare -A sum
{ read -r _; while IFS=, read -r id city amt; do (( sum[$city] += amt )); done; } < o.csv
for c in "${!sum[@]}"; do echo "$c ${sum[$c]}"; done | sort
''', notes={3: 'Header skipped inside the same { }.'}, tryit='Add a count per city.'),
    dict(level='a', tag='SRE', title='Commands in a loop that must not eat the list',
         problem='<p>Run a command that reads stdin for each host, without losing hosts.</p>',
         inp='a host list', approach=['fd 3 for the list.'],
         code='''printf 'h1\\nh2\\nh3\\n' > hosts
eats() { cat > /dev/null; }
while read -r h; do echo "visit $h"; eats; done < hosts
echo '--- list on fd 3:'
while read -r -u 3 h; do echo "visit $h"; eats; done 3< hosts
''', notes={3: 'Only h1: eats consumed the rest.', 5: 'All three.'}, tryit='Use < /dev/null instead.'),
]

QUIZ = mix([
    dict(q='The safe way to read lines:', options=['for l in $(cat f)', 'while IFS= read -r l', 'cat f | for', 'read f'], answer=1, why='Exact lines.'),
    dict(q='-r in read keeps…', options=['spaces', 'backslashes', 'the last line', 'variables'], answer=1, why='Raw.'),
    dict(q='IFS= before read keeps…', options=['backslashes', 'leading and trailing spaces', 'commas', 'nothing'], answer=1, why='No trimming.'),
    dict(q='Why || [[ -n $line ]]?', options=['speed', 'keep a last line without newline', 'skip blanks', 'read faster'], answer=1, why='read fails at EOF.'),
    dict(q='cat f | while … count++ … ; echo $count shows 0 because…', options=['read failed', 'the loop ran in a subshell', 'count is local', 'cat is slow'], answer=1, why='Pipe = subshell.'),
    dict(q='Whole file into an array:', options=['readfile', 'mapfile -t arr < f', 'arr=$(cat f)', 'read -a'], answer=1, why='mapfile.'),
    dict(q='ssh inside a while-read loop needs…', options=['-v', '-n', 'sudo', '-t'], answer=1, why='No stdin.'),
    dict(q='read -r a b on “x y z” gives b =', options=['y', 'z', 'y z', 'empty'], answer=2, why='Last gets the rest.'),
])

REVISION = [
    'while IFS= read -r line || [[ -n $line ]]; do …; done < file: exact lines, last line kept.',
    'for over $(cat) splits words and expands globs: never for lines.',
    'read -r a b rest splits on IFS; the last variable gets the remainder; _ skips a field.',
    'IFS=, / IFS=: / IFS=$\'\\t\' for other separators; empty fields survive with non-space IFS.',
    'mapfile -t arr < file (-s skip, -n limit); done < <(cmd) keeps variables, cmd | while does not.',
    'Commands in the body share stdin: ssh -n, < /dev/null or read -u 3 … 3< file. Strip \\r from Windows files.',
]

FAQ = [
    ('How do I read a file line by line in Bash?', 'while IFS= read -r line; do …; done < file (add || [[ -n $line ]] for a last line without a newline).'),
    ('Why does my while read loop skip the last line?', 'The file does not end with a newline; read returns failure even though it filled the variable.'),
    ('Why are variables lost after a while loop?', 'The loop was on the right of a pipe and ran in a subshell; use done < file or done < <(cmd).'),
    ('What does IFS mean in Bash?', 'Internal Field Separator: the characters used to split words and read fields.'),
    ('What is mapfile?', 'A Bash built-in (alias readarray) that reads lines into an array.'),
    ('Why does my loop only process the first line when using ssh?', 'ssh reads the rest of the loop’s input; use ssh -n.'),
    ('How do I read a CSV file in Bash?', 'For simple CSV: while IFS=, read -r a b c; for quoted fields use a real parser (next lesson).'),
]

PRACTICE_INTRO = 'Small line-reading tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Lines', stmt='Print each line of a 2-line here-string in brackets.', inp='two lines', code="while IFS= read -r l; do echo \"[$l]\"; done <<< $'a b\\nc'\n", explain='[a b] [c].'),
    dict(level='easy', title='Fields', stmt='Read name and city from "Asha Pune".', inp='a line', code="read -r n c <<< 'Asha Pune'; echo \"$c\"\n", explain='Pune.'),
    dict(level='easy', title='Count', stmt='Count lines with mapfile.', inp='3 lines', code="mapfile -t a <<< $'x\\ny\\nz'; echo ${#a[@]}\n", explain='3.'),
    dict(level='medium', title='Last line', stmt='Count lines of a file without a final newline.', inp='2 lines', code="printf 'a\\nb' > f; n=0; while IFS= read -r l || [[ -n $l ]]; do ((++n)); done < f; echo $n\n", explain='2.'),
    dict(level='medium', title='Commas', stmt='Print the middle field of x,,z (it is empty).', inp='a CSV line', code="IFS=, read -r a b c <<< 'x,,z'; echo \"[$b]\"\n", explain='[].'),
    dict(level='medium', title='Skip comments', stmt='Print only non-comment lines.', inp='lines', code="while IFS= read -r l; do [[ $l == \\#* ]] || echo \"$l\"; done <<< $'#c\\nweb01'\n", explain='web01.'),
    dict(level='business', title='Keep the total', stmt='Sum numbers from seq 1 4 keeping the total after the loop.', inp='numbers', code="t=0; while read -r n; do t=$((t+n)); done < <(seq 1 4); echo $t\n", explain='10.'),
    dict(level='business', title='Strip CR', stmt='Remove a Windows \\r from web01\\r.', inp='a CRLF line', code="h=$'web01\\r'; h=${h%$'\\r'}; echo \"${#h}\"\n", explain='5.'),
]

SCN_INTRO = 'Interview questions about reading files in Bash.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Read a file line by line”', 'Very common.', 'write it',
        '''<ul>
          <li>while IFS= read -r line; do echo "$line"; done < file</li>
          <li>-r keeps backslashes, IFS= keeps spaces.</li>
          <li>Not for line in $(cat file).</li>
        </ul>''', 'using for and cat.') +
    scn('Service company', 'Junior', 'Loop over servers stops after one', 'ssh inside.', 'why?',
        '''<ol>
          <li>ssh reads the loop’s stdin.</li>
          <li>ssh -n or < /dev/null.</li>
          <li>Or read the list on fd 3.</li>
        </ol>''', 'adding sleep.') +
    scn('Product company', 'Mid-level', 'Counter is 0 after the loop', 'grep | while.', 'fix?',
        '''<ul>
          <li>Pipe runs the loop in a subshell.</li>
          <li>done < <(grep …).</li>
          <li>Or shopt -s lastpipe in scripts.</li>
        </ul>''', 'export the variable.') +
    scn('Data company', 'Senior', 'A 50 GB file processed in a Bash loop takes hours', 'Nightly job.', 'what now?',
        '''<ul>
          <li>Bash read is slow (byte reads on pipes, per-line forks).</li>
          <li>awk, sort, or Python/Spark for that size.</li>
          <li>Keep Bash for orchestration.</li>
        </ul>''', 'adding more CPUs.')
) + interview([
    ('What does read -r do?', 'Disables backslash escapes.'),
    ('What is IFS?', 'Field separator characters.'),
    ('mapfile vs while read?', 'All at once into an array vs one at a time.'),
    ('What is < <(cmd)?', 'Process substitution as input.'),
    ('Why ssh -n?', 'Stop ssh reading stdin.'),
    ('How to skip a CSV header?', 'read -r _ before the loop, or tail -n +2, or mapfile -s 1.'),
    ('Last line without newline?', '|| [[ -n $line ]].'),
], [
    ('LFCS', 'Process text files in scripts.'),
    ('RHCSA', 'Loops over input in scripts.'),
    ('CompTIA Linux+', 'while/read loops, IFS.'),
]) + distro('read and mapfile availability.', [
    ('read -r', 'yes', 'yes', 'yes', 'yes (POSIX)'),
    ('mapfile', 'bash 4+', 'bash 4+', 'bash 4+', 'macOS bash 3.2: no'),
    ('read -u', 'bash', 'bash', 'bash', 'bash'),
    ('dos2unix', 'install', 'install', 'install', 'brew'),
    ('In dash (sh)', 'read -r only', '-', '-', '-'),
]) + teaser('2.2', 'IFS=, breaks on "New Delhi, India" and on log lines with brackets. Next: parsing real CSV, log and config files properly.')

CHEATSHEET = cheatsheet('Reading lines', [
    ('Loop', [('while IFS= read -r l', 'safe'), ('|| [[ -n $l ]]', 'last line'), ('done < file', 'input'), ('"$l"', 'quote')]),
    ('Fields', [('read -r a b rest', 'split'), ('IFS=, read -r', 'commas'), ('read -r _', 'skip'), ('read -a arr', 'into array')]),
    ('Arrays', [('mapfile -t a < f', 'all lines'), ('-s 1', 'skip header'), ('-n 10', 'limit'), ('${#a[@]}', 'count')]),
    ('Traps', [('cmd | while', 'subshell'), ('done < <(cmd)', 'fix'), ('ssh -n', 'stdin'), ("${l%$'\\r'}", 'CRLF')]),
])

MINDMAP = mindmap('Line by line', [
    ('Loop', 'blue', ['IFS=', '-r', '|| [[ -n ]]']),
    ('Fields', 'green', ['read a b c', 'IFS=,', 'rest']),
    ('Filter', 'amber', ['comments', 'blanks', 'continue']),
    ('Arrays', 'violet', ['mapfile', '-s -n', '${arr[@]}']),
    ('Input', 'acc', ['< file', '< <(cmd)', '<<< str']),
    ('Traps', 'red', ['pipe subshell', 'ssh stdin', 'CRLF']),
])

LAB = lab('process a host list', 'Build the lab (it creates <code>~/lab21/hosts.txt</code>, messy on purpose), write <code>~/lab21/hosts.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab21; mkdir -p ~/lab21 && cd ~/lab21
printf '# fleet\\nweb01 10.0.1.11 prod\\n\\n  web02   10.0.1.12 prod\\ndb01 10.0.2.21 prod\\nbuild\\\\01 10.0.3.7 ci\\ntest01 10.0.9.5 test' > hosts.txt''',
    tasks=['<code>hosts.sh ENV</code> prints the names of the hosts in <code>hosts.txt</code> whose third field equals ENV, one per line, skipping comments and blank lines.',
           '<code>./hosts.sh prod</code> must print exactly <code>web01</code>, <code>web02</code>, <code>db01</code> (in that order).',
           '<code>./hosts.sh test</code> must print <code>test01</code> (the last line has no newline: do not lose it), and <code>./hosts.sh ci</code> must print <code>build\\01</code> with the backslash.',
           'After the names, print a line <code>count: N</code> to <b>stderr</b> with the number of matches (so the counter must survive the loop).'],
    solution='''cat > hosts.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
want=${1:?usage: hosts.sh ENV}
n=0
while read -r host ip env || [[ -n ${host:-} ]]; do
  [[ -z ${host:-} || $host == \\#* ]] && continue
  if [[ ${env:-} == "$want" ]]; then printf '%s\\n' "$host"; n=$((n + 1)); fi
done < ~/lab21/hosts.txt
echo "count: $n" >&2
EOF
chmod +x hosts.sh''',
    check='''cd ~/lab21
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 runs"      '[ -x hosts.sh ] && ./hosts.sh prod >/dev/null 2>&1'
ok "2 prod"      '[ "$(./hosts.sh prod 2>/dev/null | paste -sd,)" = "web01,web02,db01" ]'
ok "3 last + \\\\" '[ "$(./hosts.sh test 2>/dev/null)" = test01 ] && [ "$(./hosts.sh ci 2>/dev/null)" = "build\\\\01" ]'
ok "4 count"     '[ "$(./hosts.sh prod 2>&1 >/dev/null)" = "count: 3" ]' ''')
