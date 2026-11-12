import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='13-one-liners', lesson='05-data-one-liners-csv-with-cut-awk-sort-and-join', n='13.5',
    module_label='Module 13 · Power one-liners and command combos',
    title='Data one-liners: CSV with cut, awk, sort and join, and JSON with jq',
    desc='Command-line data work: inspecting a CSV (header, NF per row, duplicates, empty cells, \\r), cut and awk -F, for columns, filters, totals, averages, min/max and group-by arrays, sort -t, -k and uniq -c, join, paste, comm and the awk NR==FNR lookup, dedupe with !seen[$0]++, quoted fields and Windows line endings, and jq for JSON: paths, select, map, add, group_by, @csv, @tsv and CSV to JSON; real outputs and 40+ examples.',
    og_desc='CSV and JSON one-liners with real runs: awk totals and group-by, join, dedupe, data checks and jq.',
    minutes=45, level='Beginner → Advanced',
    lead='Turn a CSV export into a correct report and a JSON API answer into a table, with small tools: inspect the data first, then select, aggregate, combine and export.',
    chips=['awk group-by animated', 'join explained', 'Data-quality checks', 'jq for JSON', 'Practice lab with checker'],
)

MAIN = """# A small sales file (with a duplicate row, like real exports)
cat > sales.csv <<'EOF'
id,city,product,qty,price
1,Pune,Pen,10,10
2,Delhi,Bag,1,799
3,Pune,Notebook,3,45
4,Delhi,Pen,5,10
4,Delhi,Pen,5,10
EOF
echo "rows: $(tail -n +2 sales.csv | wc -l), unique: $(tail -n +2 sales.csv | sort -u | wc -l)"
echo "-- revenue per city (deduplicated)"
awk -F, 'NR>1 && !seen[$0]++ {t[$2]+=$4*$5} END{for(c in t) print c, t[c]}' sales.csv | sort -k2 -rn
echo "-- orders per product"
tail -n +2 sales.csv | sort -u | cut -d, -f3 | sort | uniq -c | sort -rn
"""

RUN = dict(
    heading='Check, deduplicate, total and count',
    intro='<p>Count rows and unique rows, total revenue per city without the duplicate, and count orders per product. (jq is not available in the browser; its examples above are real runs.)</p>',
    code=MAIN,
    anno=[("!seen[$0]++", 'True only the first time a line is seen.'), ("t[$2]+=$4*$5", 'Group by city: qty × price.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. How much is Delhi?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does each line print?',
             code="printf 'a,1\\nb,2\\na,3\\n' > d.csv\ncut -d, -f1 d.csv | sort | uniq -c\nawk -F, '{s+=$2} END{print s}' d.csv\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the header is counted as a city. Add NR&gt;1.',
             code="printf 'city,n\\nPune,1\\nDelhi,2\\n' > c.csv\nawk -F, '{print $1}' c.csv\n"),
        dict(label='4 · Your turn', hint='Join names to scores on the id column.',
             code="printf '1,Riya\\n2,Aman\\n' > names.csv\nprintf '1,91\\n2,78\\n' > scores.csv\njoin -t, names.csv scores.csv\n"),
        dict(label='5 · Challenge', hint='Average price per product.',
             code="printf 'Pen,10\\nPen,12\\nBag,800\\n' > p.csv\nawk -F, '{s[$1]+=$2; n[$1]++} END{for(k in s) printf \"%s %.1f\\n\", k, s[k]/n[k]}' p.csv | sort\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: bigger tools',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · jq version', cmd='jq --version', output=pc('jq --version'), note='Recorded. Install: sudo apt install jq.'),
        dict(title='2 · A real API', cmd="curl -s https://api.github.com/repos/torvalds/linux | jq '{name, stargazers_count, language}'", output='{\n  "name": "linux",\n  "stargazers_count": 190000,\n  "language": "C"\n}', note='Typical (numbers change).'),
        dict(title='3 · Quoted CSV done right (Miller)', cmd='sudo apt install miller\nmlr --icsv --opprint cut -f name customers.csv', output='name\nSharma, Riya\nAman Verma', note='Typical.'),
        dict(title='4 · SQL on a CSV (sqlite3)', cmd='sqlite3 :memory: ".import --csv sales.csv s" "select city, sum(qty*price) from s group by city order by 2 desc"', output='Pune|2732.0\nDelhi|1878.0\n…', note='Typical: when one-liners get complex.'),
    ],
)

TRACE = dict(
    heading='An awk group-by, line by line',
    intro='<p>Step through: read rows, build totals, read them back.</p>',
    code='''printf 'Pune,135\\nDelhi,100\\nPune,799\\n' > t.csv
totals=$(awk -F, '{t[$1]+=$2} END{for(c in t) print c, t[c]}' t.csv | sort)
first=${totals%%$'\\n'*}
count=$(printf '%s\\n' "$totals" | wc -l)
echo "$count cities; first: $first"
''',
    notes={2: 'One pass: a total per city.', 3: 'The first line (Delhi 100 after sort).', 4: 'Two cities.'},
)

WORKED_INTRO = 'Three data tasks from real jobs: a quality gate, a reconciliation and a JSON summary.'
EXAMPLES = [
    dict(level='b', tag='Data', title='A quality gate before loading',
         problem='<p>Stop with an error if any row has the wrong number of columns or a duplicate ID.</p>',
         inp='a CSV', approach=['NF check.', 'uniq -d on IDs.'],
         code='''printf 'id,name,score\\n1,Riya,91\\n2,Aman\\n3,Zoya,88\\n3,Zoya,88\\n' > in.csv
bad=$(awk -F, 'NF!=3' in.csv | wc -l)
dup=$(tail -n +2 in.csv | cut -d, -f1 | sort | uniq -d | wc -l)
echo "bad rows: $bad, duplicate ids: $dup"
[ "$bad" -eq 0 ] && [ "$dup" -eq 0 ] && echo LOAD || echo "STOP: fix the file first"
''', notes={2: 'Rows with a different column count.', 5: 'Gate.'}, tryit='Print the bad rows with their line numbers.'),
    dict(level='i', tag='Finance', title='Reconcile payments with orders',
         problem='<p>List order IDs that have no payment, and payments that have no order.</p>',
         inp='two ID lists', approach=['comm -23 and -13.'],
         code='''printf '1001\\n1002\\n1003\\n1004\\n' > orders.txt
printf '1001\\n1003\\n1005\\n' > payments.txt
echo "unpaid orders: $(comm -23 <(sort orders.txt) <(sort payments.txt) | paste -sd' ')"
echo "unknown payments: $(comm -13 <(sort orders.txt) <(sort payments.txt) | paste -sd' ')"
''', notes={3: 'Only in orders.', 4: 'Only in payments.'}, tryit='Add a count of matched IDs with comm -12.'),
    dict(level='a', tag='Analytics', title='Monthly summary per category',
         problem='<p>From sales (date, product, amount) and a product list, total amount per month and category.</p>',
         inp='two CSVs', approach=['NR==FNR lookup.', 'composite key.'],
         code='''printf 'Pen,Stationery\\nBag,Luggage\\n' > cat.csv
printf '2026-10-30,Pen,50\\n2026-11-02,Bag,799\\n2026-11-05,Pen,20\\n' > s.csv
awk -F, 'NR==FNR{c[$1]=$2; next} {k=substr($1,1,7)","c[$2]; t[k]+=$3} END{for(k in t) print k","t[k]}' cat.csv s.csv | sort
''', notes={3: 'Key = month + category.'}, tryit='Add a grand total line.'),
]

QUIZ = mix([
    dict(q='Skip the header in awk:', options=['NR>1', 'NF>1', 'FNR==1', '$1!=""'], answer=0, why='Record number > 1.'),
    dict(q='cut defaults to which delimiter?', options=['comma', 'space', 'tab', 'semicolon'], answer=2, why='Tab.'),
    dict(q='Total per city in awk:', options=['t[$3]+=$5', 'sum($3)', 'group $3', 'uniq -c $3'], answer=0, why='Array.'),
    dict(q='Remove duplicate lines but keep order:', options=['sort -u', "awk '!seen[$0]++'", 'uniq', 'cut -u'], answer=1, why='sort -u changes order.'),
    dict(q='join requires…', options=['tabs', 'both files sorted on the key', 'a header', 'JSON'], answer=1, why='Merge-style.'),
    dict(q='Why can cut break customer names?', options=['too long', 'commas inside quotes', 'Unicode', 'spaces'], answer=1, why='Not CSV-aware.'),
    dict(q='jq: each order’s city:', options=['.orders.city', '.orders[].city', '.city[]', 'orders->city'], answer=1, why='[] walks the list.'),
    dict(q='jq: print strings without quotes:', options=['-c', '-r', '-s', '-n'], answer=1, why='Raw.'),
])

REVISION = [
    'Inspect first: head, wc -l, awk -F, \'{print NF}\' | uniq -c, sort | uniq -d, empty cells, cat -A for \\r.',
    'cut -d, -fN for columns; awk -F, for filters ($3=="Pune"), sums (s+=$5*$6), groups (t[$3]+=…), NR>1 for headers.',
    'sort -t, -kN,N[n][r]; sort | uniq -c | sort -rn to count; awk \'!seen[$0]++\' to dedupe in order.',
    'join -t, -1 N -2 M on sorted inputs (-a 1 left join); paste by line; comm -12/-23/-13; awk NR==FNR lookup without sorting.',
    'Quoted CSV: use a CSV-aware tool; money: printf %.2f or integers; never write output to the input file.',
    'jq: .a[].b, select(), map(), add, group_by, length, keys, @csv/@tsv, -r, -c; -R for raw lines.',
]

FAQ = [
    ('How do I sum a column in a CSV with awk?', "awk -F, 'NR>1{s+=$N} END{print s}' file.csv."),
    ('How do I group by a column in awk?', "awk -F, 'NR>1{t[$3]+=$5} END{for(k in t) print k, t[k]}' file.csv."),
    ('How do I join two CSV files in Linux?', 'join -t, -1 COL1 -2 COL2 <(sort -t, -kCOL1,COL1 a) <(sort -t, -kCOL2,COL2 b), or an awk NR==FNR lookup.'),
    ('How do I remove duplicate lines but keep the order?', "awk '!seen[$0]++' file."),
    ('Why does cut split names with commas wrongly?', 'cut is not CSV-aware; use Python csv, Miller, csvkit or gawk FPAT.'),
    ('How do I read JSON on the command line?', "jq, e.g. jq -r '.orders[] | .id' file.json."),
    ('How do I convert JSON to CSV?', "jq -r '.items[] | [.a, .b] | @csv'."),
]

PRACTICE_INTRO = 'Small data tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Second column', stmt='Print the second column of “a,b,c”.', inp='a line', code="echo 'a,b,c' | cut -d, -f2\n", explain='b.'),
    dict(level='easy', title='Sum', stmt='Sum 3, 4 and 5 given as CSV rows x,3 / y,4 / z,5.', inp='rows', code="printf 'x,3\\ny,4\\nz,5\\n' | awk -F, '{s+=$2} END{print s}'\n", explain='12.'),
    dict(level='easy', title='Header skip', stmt='Count data rows in a file with a header and 2 rows.', inp='a CSV', code="printf 'h\\n1\\n2\\n' | tail -n +2 | wc -l\n", explain='2.'),
    dict(level='medium', title='Group', stmt='Total per key for a,1 / b,2 / a,3.', inp='rows', code="printf 'a,1\\nb,2\\na,3\\n' | awk -F, '{t[$1]+=$2} END{for(k in t) print k, t[k]}' | sort\n", explain='a 4, b 2.'),
    dict(level='medium', title='Dedupe', stmt='Remove the repeated line from x / y / x, keeping order.', inp='lines', code="printf 'x\\ny\\nx\\n' | awk '!seen[$0]++'\n", explain='x, y.'),
    dict(level='medium', title='Sort by number', stmt='Sort b,20 / a,3 / c,100 by the number, biggest first.', inp='rows', code="printf 'b,20\\na,3\\nc,100\\n' | sort -t, -k2,2rn\n", explain='c, b, a.'),
    dict(level='business', title='Join', stmt='Join 1,Riya / 2,Aman with 1,Pune / 2,Delhi on the id.', inp='two files', code="join -t, <(printf '1,Riya\\n2,Aman\\n') <(printf '1,Pune\\n2,Delhi\\n')\n", explain='1,Riya,Pune …'),
    dict(level='business', title='Semicolons', stmt='A European export uses ; and decimal commas: print the total of 1,50 and 2,25 from x;1,50 / y;2,25.', inp='rows', code="printf 'x;1,50\\ny;2,25\\n' | awk -F';' '{gsub(\",\", \".\", $2); s+=$2} END{printf \"%.2f\\n\", s}'\n", explain='3.75: change the delimiter and the decimal comma first.'),
]

SCN_INTRO = 'Interview questions about data on the command line, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Sum the third column of a CSV”', 'Very common.', 'one-liner?',
        '''<ul>
          <li>awk -F, 'NR&gt;1{s+=$3} END{print s}' file.csv</li>
          <li>Explain -F, and NR&gt;1.</li>
          <li>Mention empty values and duplicates.</li>
        </ul>''', 'opening Excel.') +
    scn('Analytics team', 'Junior', 'Report totals do not match finance', 'Same CSV.', 'why?',
        '''<ol>
          <li>Check duplicates (uniq -d), header, empty cells.</li>
          <li>Check \\r endings and quoted commas.</li>
          <li>Recompute after cleaning; document the rules.</li>
        </ol>''', 'blaming finance.') +
    scn('Data engineering', 'Mid-level', 'Join a 2 GB CSV with a 50 MB lookup', 'join is slow (sorting).', 'faster?',
        '''<ul>
          <li>awk NR==FNR loads the small file into memory; one pass over the big one.</li>
          <li>LC_ALL=C for speed; compress with zcat on the fly.</li>
          <li>Or DuckDB/SQLite for SQL.</li>
        </ul>''', 'Excel.') +
    scn('Platform', 'Senior', 'Extract fields from cloud CLI output', 'aws/kubectl JSON.', 'how?',
        '''<ul>
          <li>--output json | jq -r '.Items[] | [.Name, .State] | @tsv'.</li>
          <li>select() to filter; length to count.</li>
          <li>Or the CLI’s own --query/jsonpath.</li>
        </ul>''', 'grep on JSON.')
) + interview([
    ('cut vs awk?', 'cut picks columns; awk filters and computes.'),
    ('What is NR==FNR?', 'True only while reading the first file: used to load a lookup table.'),
    ('sort -u vs awk !seen?', 'sort -u sorts; awk keeps the original order.'),
    ('What does paste do?', 'Joins files side by side by line number.'),
    ('How to handle \\r\\n files?', 'tr -d \'\\r\' or dos2unix.'),
    ('What is @csv in jq?', 'Formats an array as a CSV line with quoting.'),
    ('When to leave one-liners?', 'Complex quoting, joins of many files, or millions of rows: use SQL tools or Python.'),
], [
    ('Data analyst interviews', 'Command-line CSV manipulation.'),
    ('LFCS', 'Text processing with awk, sort, join.'),
    ('DevOps interviews', 'jq on API and cloud output.'),
]) + distro('The tools are standard; versions differ.', [
    ('awk', 'mawk (default), gawk installable', 'gawk', 'BSD awk', 'Git Bash gawk'),
    ('FPAT (quoted CSV)', 'gawk only', 'gawk', 'no', '-'),
    ('jq', 'apt install jq', 'dnf install jq', 'brew install jq', 'winget install jqlang.jq'),
    ('join / paste / comm', 'coreutils', 'coreutils', 'BSD versions', '-'),
    ('Miller / csvkit', 'apt', 'dnf/pip', 'brew/pip', 'pip'),
]) + teaser('13.6', 'grep or awk? sed or awk? find or locate? scp or rsync? Riya knows the tools, but in a hurry she picks the wrong one. Next: a scenario guide for choosing the right command.')

CHEATSHEET = cheatsheet('Data one-liners', [
    ('Inspect', [('head -3', 'header'), ("awk -F, '{print NF}' | uniq -c", 'columns'), ('sort | uniq -d', 'duplicates'), ('cat -A', '\\r tabs')]),
    ('Select / compute', [('cut -d, -f2,3', 'columns'), ("awk -F, '$3==\"x\"'", 'filter'), ('s+=$5*$6', 'total'), ('t[$3]+=…', 'group by')]),
    ('Combine / clean', [('join -t, -1 N -2 M', 'join'), ('paste -d, a b', 'side by side'), ('comm -12', 'common'), ("awk '!seen[$0]++'", 'dedupe')]),
    ('jq', [('jq .', 'pretty'), ('.a[].b', 'path'), ('select(.x=="y")', 'filter'), ('[…] | @csv', 'CSV'), ('-r / -c', 'raw / compact')]),
])

MINDMAP = mindmap('Data', [
    ('Inspect', 'red', ['header', 'NF', 'duplicates']),
    ('Select', 'blue', ['cut', 'awk -F,', 'filters']),
    ('Compute', 'green', ['sum avg', 'group by', 'printf']),
    ('Combine', 'amber', ['join', 'paste comm', 'NR==FNR']),
    ('Clean', 'violet', ['dedupe', 'empty', '\\r quotes']),
    ('JSON', 'acc', ['jq paths', 'select map', '@csv']),
])

LAB = lab('a sales report', 'Build the lab, write <code>~/lab135/report.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab135 && cd ~/lab135 && rm -f report.sh *.txt out.csv
printf 'id,region,item,qty,price\\n1,North,Pen,10,5\\n2,South,Bag,2,500\\n3,North,Bag,1,500\\n4,East,Pen,4,5\\n2,South,Bag,2,500\\n5,South,Pen,,5\\n' > sales.csv
printf 'item,group\\nPen,Office\\nBag,Travel\\n' > items.csv''',
    tasks=['Write the number of duplicate rows (rows that appear more than once, counted once each) into <code>dups.txt</code>.',
           'Ignoring duplicate rows and rows with an empty qty, write revenue per region as <code>region,total</code> lines sorted by total (biggest first) into <code>out.csv</code>.',
           'Write the region with the highest revenue into <code>top.txt</code>.',
           'Using <code>items.csv</code>, write the total quantity sold per group (Office, Travel) as <code>group qty</code> lines sorted by group name into <code>groups.txt</code>, again without duplicates and empty qty.'],
    solution='''cat > report.sh <<'EOF'
cd ~/lab135
tail -n +2 sales.csv | sort | uniq -d | wc -l > dups.txt
awk -F, 'NR>1 && $4!="" && !s[$0]++ {t[$2]+=$4*$5} END{for(r in t) print r","t[r]}' sales.csv | sort -t, -k2,2rn > out.csv
head -1 out.csv | cut -d, -f1 > top.txt
awk -F, 'NR==FNR{if(FNR>1)g[$1]=$2; next} FNR>1 && $4!="" && !s[$0]++ {q[g[$3]]+=$4} END{for(k in q) print k, q[k]}' items.csv sales.csv | sort > groups.txt
EOF''',
    check='''cd ~/lab135; rm -f dups.txt out.csv top.txt groups.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f report.sh ] && bash report.sh 2>/dev/null
ok "1 dups"   '[ "$(cat dups.txt 2>/dev/null)" = 1 ]'
ok "2 totals" '[ "$(cat out.csv 2>/dev/null | tr "\\n" " ")" = "South,1000 North,550 East,20 " ]'
ok "3 top"    '[ "$(cat top.txt 2>/dev/null)" = South ]'
ok "4 groups" '[ "$(cat groups.txt 2>/dev/null | tr "\\n" " ")" = "Office 14 Travel 3 " ]' ''')
