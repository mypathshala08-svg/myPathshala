import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='06-text-processing', lesson='05-awk-fields-patterns-and-reports', n='6.5',
    module_label='Module 6 · Filters, text processing and regex',
    title='awk: fields, patterns and reports',
    desc='awk explained, then used in every field: fields ($1…$NF, -F, OFS), built-in variables (NR, NF, FNR, FILENAME), patterns (regex, comparisons, ranges, && ||), BEGIN and END, variables and associative arrays for totals and GROUP BY, printf reports, string functions (length, substr, toupper, gsub, split), joins with NR==FNR, and awk script files. Real outputs from Ubuntu’s mawk, with the passwd -F: mistake from common notes explained.',
    og_desc='awk for columns, conditions, totals, GROUP BY and formatted reports, with real outputs.',
    minutes=44, level='Beginner → Advanced',
    lead='awk turns the command line into a small spreadsheet: it splits lines into columns, selects rows by conditions, adds up and groups numbers, and prints formatted reports. This lesson explains awk step by step and shows how every IT role uses it.',
    chips=['awk by field', 'GROUP BY in one line', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A tiny CSV, then awk from simple to report
printf 'name,dept,salary\\nAsha,Eng,85000\\nRavi,Sales,52000\\nMeena,Eng,98000\\n' > emp.csv
awk -F, 'NR>1 {print $1, $3}' emp.csv                  # two columns
awk -F, 'NR>1 && $3>60000 {print $1}' emp.csv          # condition
awk -F, 'NR>1 {t+=$3} END {print "total", t}' emp.csv  # total
awk -F, 'NR>1 {s[$2]+=$3} END {for (d in s) print d, s[d]}' emp.csv | sort
"""

RUN = dict(
    heading='From columns to a GROUP BY',
    intro='<p>Print columns, filter by a condition, add a total and sum per department.</p>',
    code=MAIN,
    anno=[
        ("awk -F, 'NR>1 && $3>60000 {print $1}' emp.csv          # condition", 'Asha, Meena.'),
        ("awk -F, 'NR>1 {t+=$3} END {print \"total\", t}' emp.csv  # total", '235000'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is the Eng total?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the two lines print? Then run.',
             code="echo 'a   b    c' | awk '{print $2}'\necho 'a   b    c' | cut -d' ' -f2\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should print user names. Add the separator.',
             code="awk '{print $1}' /etc/passwd | head -3\n"),
        dict(label='4 · Your turn', hint='Print the last field of each line of /etc/passwd (the shell), first 3.',
             code="awk -F: '{print $NF}' /etc/passwd | head -3\n"),
        dict(label='5 · Challenge', hint='Print the average of 4, 8 and 6 with two decimals.',
             code="printf '4\\n8\\n6\\n' | awk '{s+=$1} END {printf \"%.2f\\n\", s/NR}'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real system output',
    intro='<p>These read live system data. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Memory per process name (top 5)', cmd="ps -eo comm,rss --no-headers | awk '{m[$1]+=$2} END {for (p in m) printf \"%-20s %8.1f MB\\n\", p, m[p]/1024}' | sort -k2 -nr | head -5", output='firefox                1810.4 MB\ncode                    950.2 MB\ngnome-shell             420.7 MB', note='Typical.'),
        dict(title='2 · Open TCP ports by process', cmd="sudo ss -ltnp | awk 'NR>1 {print $4, $6}'", output='0.0.0.0:22 users:(("sshd",pid=812,fd=3))\n127.0.0.1:5432 users:(("postgres",pid=990,fd=6))', note='Typical (Lesson 16.4).'),
        dict(title='3 · Install gawk for extra features', cmd="sudo apt install gawk; gawk --version | head -1", output='GNU Awk 5.2.1, API 3.2, PMA Avon 8-g1, (GNU MPFR 4.2.1, GNU MP 6.3.0)', note='Typical. After installing, awk usually points to gawk.'),
        dict(title='4 · Quoted CSV with gawk', cmd="echo '7,\"Sharma, Riya\",Pune' | gawk --csv '{print $2}'", output='Sharma, Riya', note='Typical (gawk 5.3+).'),
        dict(title='5 · Which awk on our build machine', cmd='readlink -f $(which awk); awk -W version 2>&1 | head -1', output=pc('readlink -f $(which awk); awk -W version 2>&1 | head -1'), note='Recorded: mawk.'),
    ],
)

TRACE = dict(
    heading='awk results in shell variables',
    intro='<p>Step through a script that uses awk to compute values.</p>',
    code='''printf 'a 10\\nb 30\\nc 20\\n' > d.txt
total=$(awk '{s+=$2} END {print s}' d.txt)
max=$(awk '$2>m {m=$2; k=$1} END {print k}' d.txt)
big=$(awk '$2>15' d.txt | wc -l)
echo "total=$total max=$max big=$big"
''',
    notes={1: 'Data :: Three rows.', 2: 'Total :: 60.', 3: 'Max :: b.', 4: 'Count :: 2 rows above 15.', 5: 'Report.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an admin’s disk check, a data engineer’s summary and a web log report.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='Warn about full disks',
         problem='<p>Print every filesystem above a threshold, with its usage.</p>',
         inp='saved df output (real: df -P)',
         approach=['NR>1 skips the header.', '$5+0 turns 63% into 63.', '-v passes the threshold.'],
         code='''printf 'Filesystem Size Used Avail Use%% Mounted\\n/dev/sda1 50G 33G 15G 69%% /\\n/dev/sdb1 500G 474G 26G 95%% /data\\n' > df.txt
limit=80
awk -v lim=$limit 'NR>1 && $5+0 > lim {print $6, $5}' df.txt
''',
         notes={3: 'Check :: Only /data is above 80%.'},
         tryit='On your PC: df -P | awk … with limit=50.'),
    dict(level='i', tag='Data engineer', title='Count and average per city',
         problem='<p>For each city: number of employees and average salary, sorted by city.</p>',
         inp='employees CSV',
         approach=['Two arrays: count and sum.', 'printf in END; sort.'],
         code='''printf 'name,city,salary\\nAsha,Pune,85000\\nRavi,Mumbai,52000\\nKabir,Pune,47000\\n' > e.csv
awk -F, 'NR>1 {n[$2]++; s[$2]+=$3} END {for (c in n) printf "%-8s %d %.0f\\n", c, n[c], s[c]/n[c]}' e.csv | sort
''',
         notes={2: 'GROUP BY :: Mumbai 1 52000, Pune 2 66000.'},
         tryit='Add a maximum per city.'),
    dict(level='a', tag='Web / DevOps', title='Error rate per page',
         problem='<p>For each URL: total requests, errors (status ≥ 500) and the error percentage.</p>',
         inp='a mini access log',
         approach=['Group by $7.', 'Count errors with a condition.'],
         code='''printf '%s\\n' '1 - - [t] "GET /a HTTP/1.1" 200 10' '2 - - [t] "GET /a HTTP/1.1" 500 10' '3 - - [t] "GET /b HTTP/1.1" 200 10' '4 - - [t] "GET /a HTTP/1.1" 503 10' > a.log
awk '{t[$7]++} $9>=500 {e[$7]++} END {for (u in t) printf "%-4s %d req %d err %.0f%%\\n", u, t[u], e[u], 100*e[u]/t[u]}' a.log | sort
''',
         notes={2: 'Report :: /a 3 requests, 2 errors, 67%.'},
         tryit='Only show pages with errors.'),
]

QUIZ = mix([
    dict(q="awk '{print $1}' on a line with several spaces between words prints…", options=['an empty field', 'the first word', 'the whole line', 'an error'], answer=1,
         why='Default FS treats runs of blanks as one separator.'),
    dict(q='What is NR?', options=['number of fields', 'current line (record) number', 'number of files', 'next record'], answer=1,
         why='NR = record number; NF = fields.'),
    dict(q='Which prints user names from /etc/passwd?', options=["awk '{print $1}'", "awk -F: '{print $1}'", "awk -F, '{print $1}'", "awk '{print $NF}'"], answer=1,
         why='/etc/passwd uses :.'),
    dict(q='When does the END block run?', options=['before the first line', 'after the last line', 'on every line', 'only on errors'], answer=1,
         why='END = after all input.'),
    dict(q="What does awk '!seen[$0]++' do?", options=['counts lines', 'prints each line only the first time it appears', 'deletes the file', 'sorts lines'], answer=1,
         why='Dedupe, keeping order.'),
    dict(q='How do you pass a shell variable into awk?', options=['awk $var', 'awk -v x="$var"', 'awk --var', 'export only'], answer=1,
         why='-v name=value.'),
    dict(q='for (k in arr) prints keys in…', options=['sorted order', 'no guaranteed order', 'insertion order', 'reverse order'], answer=1,
         why='Pipe to sort.'),
    dict(q="What does printf \"%-10s\" do?", options=['right-align in 10', 'left-align in 10 characters', 'print 10 times', 'truncate to 10'], answer=1,
         why='- = left-align.'),
])

REVISION = [
    "<code>awk 'pattern {action}' file</code>; no pattern = all lines, no action = print.",
    'Fields <code>$1…$NF</code>, <code>$0</code>; <code>-F,</code> <code>-F:</code>; default FS = runs of blanks; <code>-v OFS=,</code>.',
    '<code>NR</code> line, <code>NF</code> fields, <code>FNR</code> per file, <code>FILENAME</code>.',
    "Patterns: <code>/re/</code>, <code>$5&gt;70000</code>, <code>$4~/^P/</code>, <code>NR&gt;1</code>, <code>&amp;&amp; ||</code>, ranges.",
    "<code>BEGIN</code> before, <code>END</code> after; <code>s+=$5</code> totals; <code>a[$3]+=$5</code> GROUP BY; <code>for (k in a)</code> + sort.",
    '<code>printf "%-10s %8.2f\\n"</code>; <code>length substr toupper gsub split</code>.',
    "<code>!seen[$0]++</code> dedupe; <code>NR==FNR {…; next}</code> join two files.",
    'Ubuntu’s awk is mawk; gawk adds --csv, -i inplace, more functions. Single-quote programs.',
]

FAQ = [
    ('How do I print a specific column with awk?', "awk '{print $3}' file (add -F, for CSV, -F: for /etc/passwd)."),
    ('How do I sum a column with awk?', "awk '{s+=$2} END {print s}' file."),
    ('How do I filter rows by a column value?', "awk -F, '$3 == \"HR\"' file or awk '$5 > 100' file."),
    ('What is the difference between awk, sed and grep?', 'grep finds lines, sed edits lines, awk works with columns, conditions and calculations.'),
    ('How do I group by a column in awk?', "awk '{s[$1]+=$2} END {for (k in s) print k, s[k]}' file | sort."),
    ('How do I use a shell variable in awk?', "awk -v lim=\"$limit\" '$2 > lim' file."),
    ('Why does awk print whole lines instead of a column?', 'The separator is wrong: set -F to the real delimiter (for example -F: for /etc/passwd).'),
]

PRACTICE_INTRO = 'Small awk tasks. Expected outputs come from real runs on Ubuntu 24.04 (mawk).'
PROBLEMS = [
    dict(level='easy', title='Second column', stmt='Print the second word of each line.', inp='two lines',
         code="printf 'a b c\\nd e f\\n' | awk '{print $2}'\n", explain='$2.'),
    dict(level='easy', title='Shells', stmt='Print the shell (last field) of root in /etc/passwd.', inp='/etc/passwd',
         code="awk -F: '$1==\"root\" {print $NF}' /etc/passwd\n", explain='Condition + $NF.'),
    dict(level='easy', title='Sum', stmt='Add up 10, 20 and 30.', inp='three numbers',
         code="printf '10\\n20\\n30\\n' | awk '{s+=$1} END {print s}'\n", explain='END prints the total.'),
    dict(level='medium', title='Filter', stmt='Print names with marks above 80.', inp='name marks',
         code="printf 'Asha 91\\nRavi 78\\nMeena 85\\n' | awk '$2 > 80 {print $1}'\n", explain='Numeric condition.'),
    dict(level='medium', title='Count per value', stmt='Count each city in Pune, Agra, Pune.', inp='three cities',
         code="printf 'Pune\\nAgra\\nPune\\n' | awk '{c[$1]++} END {for (k in c) print k, c[k]}' | sort\n", explain='Array counts.'),
    dict(level='medium', title='Reformat', stmt='Print “Asha scored 91” from “Asha,91”.', inp='a CSV line',
         code="echo 'Asha,91' | awk -F, '{print $1, \"scored\", $2}'\n", explain='Mix fields and text.'),
    dict(level='business', title='Average with decimals', stmt='Average salary of 85000, 52000, 98000 with 2 decimals.', inp='three salaries',
         code="printf '85000\\n52000\\n98000\\n' | awk '{s+=$1} END {printf \"%.2f\\n\", s/NR}'\n", explain='printf %.2f.'),
    dict(level='business', title='Top earner', stmt='Name of the highest salary from name,salary rows.', inp='three rows',
         code="printf 'Asha,85000\\nRavi,52000\\nMeena,98000\\n' | awk -F, '$2>m {m=$2; n=$1} END {print n}'\n", explain='Track the maximum.'),
]

SCN_INTRO = 'Interview questions about awk, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Print the first and third columns of a file.”',
        'A classic first-round question.',
        'do you know awk fields and separators?',
        '''<ul>
          <li><code>awk '{print $1, $3}' file</code>; CSV: <code>awk -F, …</code>.</li>
          <li>Compare with <code>cut -d' ' -f1,3</code>, which breaks on multiple spaces.</li>
          <li>Last column: <code>$NF</code>.</li>
        </ul>''', 'forgetting -F for non-space separators.') +
    scn('Operations', 'Junior', 'Which process uses the most memory?',
        'The server is swapping; you have 5 minutes.',
        'can you summarise command output?',
        '''<ol>
          <li><code>ps -eo comm,rss --no-headers | awk '{m[$1]+=$2} END {for (p in m) print m[p], p}' | sort -nr | head</code>.</li>
          <li>Group by command name, sum RSS (KB).</li>
          <li>Confirm with top/htop (Lesson 11.2).</li>
        </ol>''', 'reading ps aux by eye.') +
    scn('Data team', 'Mid-level', 'A daily summary before loading',
        'A 2 GB CSV arrives daily; you must report rows, bad rows and totals per region before the load.',
        'can you validate and summarise in one pass?',
        '''<ul>
          <li><code>awk -F, 'NF!=8 {bad++; next} {rows++; s[$3]+=$7} END {…}'</code>: one pass, little memory.</li>
          <li>Watch for quoted fields: gawk --csv or Python.</li>
          <li>Exit non-zero if bad rows exceed a limit so the pipeline stops.</li>
        </ul>''', 'opening it in Excel.') +
    scn('Platform', 'Senior', 'awk report gives different numbers on two servers',
        'The same script prints different totals on Ubuntu and on another distro.',
        'do you know the awk implementations and locales?',
        '''<ul>
          <li>Ubuntu: mawk; RHEL: gawk; macOS: BWK awk. Functions and number formatting can differ.</li>
          <li>Locale decimal separators (LC_NUMERIC) can change parsing; set LC_ALL=C.</li>
          <li>Pin the tool (gawk explicitly) in production scripts.</li>
        </ul>''', '“awk is awk”.')
) + interview([
    ('What do NR and NF mean?', 'Record (line) number and number of fields.'),
    ('How do you set the field separator?', '-F (or FS in BEGIN).'),
    ('What are BEGIN and END for?', 'Code before the first line and after the last.'),
    ('How do you sum a column?', "awk '{s+=$N} END {print s}'."),
    ('How do you remove duplicate lines keeping order?', "awk '!seen[$0]++'."),
    ('Difference between awk and sed?', 'awk: fields, logic, arithmetic; sed: line-based editing.'),
    ('How do you pass a shell variable into awk?', '-v name="$value".'),
], [
    ('RHCSA (EX200)', 'Text analysis with standard tools; awk is a common choice for column work.'),
    ('LFCS', 'Essential commands: process text with awk, sed and other filters.'),
    ('CompTIA Linux+', 'awk fields, patterns and basic programs for text processing.'),
]) + distro('Different distros ship different awk implementations.', [
    ('Default awk', 'mawk', 'gawk', 'BWK awk', 'WSL: mawk; Git Bash: gawk'),
    ('gawk available', 'apt install gawk', 'default', 'brew install gawk', 'yes'),
    ('--csv', 'gawk 5.3+ / BWK 2023', 'gawk 5.3+', 'recent macOS awk', 'gawk'),
    ('-i inplace, asort', 'gawk only', 'yes', 'no', 'gawk'),
    ('strftime', 'mawk 1.3.4 and gawk', 'yes', 'no', 'yes'),
    ('IGNORECASE', 'gawk only (use tolower)', 'yes', 'no', 'gawk'),
]) + teaser('6.6', 'Riya’s patterns keep failing: <code>grep \'a+b\'</code> finds nothing, <code>sed \'s/\\d/X/\'</code> does nothing, and a phone-number check accepts “12-34”. What are the rules of the pattern language behind grep, sed and awk, and why does each tool speak a slightly different dialect?')

CHEATSHEET = cheatsheet('awk', [
    ('Fields', [("'{print $1, $3}'", 'columns'), ('$NF · $0', 'last · whole'), ('-F, / -F:', 'separator'), ('-v OFS=,', 'output sep'), ("'{$1=$1}1'", 'rebuild')]),
    ('Patterns', [("'/re/'", 'regex'), ("'$5>70000'", 'numeric'), ("'$4~/^P/'", 'field regex'), ("'NR>1'", 'skip header'), ("'NF!=5'", 'bad rows')]),
    ('Totals', [("{s+=$5} END{print s}", 'sum'), ('s/NR', 'average'), ("$5>m{m=$5}", 'max'), ('{a[$3]+=$5}', 'group'), ('for (k in a)', 'loop + sort')]),
    ('Format', [('printf "%-10s %8.2f\\n"', 'aligned'), ('length substr', 'strings'), ('toupper tolower', 'case'), ('gsub(/a/,"b")', 'replace'), ('split(s,a,"-")', 'split')]),
    ('Tricks', [("'!seen[$0]++'", 'dedupe'), ('NR==FNR{…;next}', 'join files'), ('-v x="$y"', 'shell var'), ('-f prog.awk', 'script file'), ('$5+0', 'to number')]),
])

MINDMAP = mindmap('awk', [
    ('Fields', 'blue', ['$1…$NF, $0', '-F, -F:', 'OFS']),
    ('Patterns', 'green', ['/re/, $5>x', 'NR>1, ranges', '&& || !']),
    ('Blocks', 'amber', ['BEGIN', 'main', 'END']),
    ('Data', 'violet', ['variables', 'arrays a[$3]', 'for (k in a)']),
    ('Output', 'acc', ['print', 'printf %-10s', 'functions']),
    ('Know', 'red', ['mawk vs gawk', 'single quotes', 'no -i (mawk)']),
])

LAB = lab('build a salary report with awk', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab65 && cd ~/lab65 && rm -f *
printf 'name,dept,city,salary\\nAsha,Eng,Pune,85000\\nRavi,Sales,Mumbai,52000\\nMeena,Eng,Delhi,98000\\nKabir,HR,Pune,47000\\nRiya,Sales,Pune,61000\\n' > emp.csv''',
    tasks=['Write the names of employees in Pune (one per line, file order) into <code>pune.txt</code>.',
           'Write the total of all salaries into <code>total.txt</code>.',
           'Write “DEPT TOTAL” lines (e.g. <code>Eng 183000</code>), sorted by department, into <code>by_dept.txt</code>.',
           'Write the name of the highest-paid employee into <code>top.txt</code>.'],
    solution='''awk -F, '$3=="Pune" {print $1}' emp.csv > pune.txt
awk -F, 'NR>1 {t+=$4} END {print t}' emp.csv > total.txt
awk -F, 'NR>1 {s[$2]+=$4} END {for (d in s) print d, s[d]}' emp.csv | sort > by_dept.txt
awk -F, 'NR>1 && $4>m {m=$4; n=$1} END {print n}' emp.csv > top.txt''',
    check='''cd ~/lab65
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 Pune names"   '[ "$(cat pune.txt 2>/dev/null)" = "$(printf "Asha\\nKabir\\nRiya")" ]'
ok "2 total"        '[ "$(cat total.txt 2>/dev/null)" = 343000 ]'
ok "3 by department" '[ "$(cat by_dept.txt 2>/dev/null)" = "$(printf "Eng 183000\\nHR 47000\\nSales 113000")" ]'
ok "4 top earner"   '[ "$(cat top.txt 2>/dev/null)" = Meena ]' ''')
