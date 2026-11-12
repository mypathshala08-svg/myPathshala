import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='06-text-processing', lesson='02-sort-uniq-wc-cut-paste-and-tr', n='6.2',
    module_label='Module 6 · Filters, text processing and regex',
    title='sort, uniq, wc, cut, paste and tr',
    desc='The six classic filters: cut (-d -f -c --complement), sort (-n -r -u -f -k -t -h -V -s -o -c and locale), uniq (-c -d -u -i -f -s -w, and why sort comes first), wc (-l -w -c -m -L), paste (-d -s) and tr (translate, -d, -s, -c). Each explained, then used by admins, data engineers, developers, DevOps, security and QA, with real outputs and corrected sample outputs from common notes.',
    og_desc='cut, sort, uniq, wc, paste and tr explained with real outputs: frequency tables, column sorts, totals and text cleaning.',
    minutes=42, level='Beginner → Advanced',
    lead='Six small commands turn a CSV or a log into a report: cut takes a column, sort orders it, uniq counts, wc measures, paste joins and tr changes characters. This lesson explains each one, then shows how every IT role combines them.',
    chips=['Tools by field', 'Why uniq needs sort', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A tiny CSV, then the six tools
printf 'name,dept,salary\\nAsha,Eng,85000\\nRavi,Sales,52000\\nMeena,Eng,98000\\n' > emp.csv
tail -n +2 emp.csv | cut -d, -f2 | sort | uniq -c        # people per dept
tail -n +2 emp.csv | sort -t, -k3,3nr | head -1          # top salary
tail -n +2 emp.csv | cut -d, -f3 | paste -sd+ | bc       # total
wc -l < emp.csv                                          # lines
cut -d, -f1 emp.csv | tr '[:lower:]' '[:upper:]'         # capitals
"""

RUN = dict(
    heading='A small HR report with six tools',
    intro='<p>Count per department, find the top salary, add up the salaries, count lines and change case.</p>',
    code=MAIN,
    anno=[
        ('tail -n +2 emp.csv | cut -d, -f2 | sort | uniq -c        # people per dept', '2 Eng, 1 Sales.'),
        ('tail -n +2 emp.csv | sort -t, -k3,3nr | head -1          # top salary', 'Meena.'),
        ('tail -n +2 emp.csv | cut -d, -f3 | paste -sd+ | bc       # total', '235000'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is the total?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which order do the two sorts give? Then run.',
             code="printf '100\\n20\\n3\\n' | sort | tr '\\n' ' '; echo\nprintf '100\\n20\\n3\\n' | sort -n | tr '\\n' ' '; echo\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> apple should be counted 3 times. Fix the pipeline.',
             code="printf 'apple\\nkiwi\\napple\\napple\\n' | uniq -c\n"),
        dict(label='4 · Your turn', hint='Print the user names from /etc/passwd, sorted, first 5.',
             code="cut -d: -f1 /etc/passwd | sort | head -5\n"),
        dict(label='5 · Challenge', hint='Turn “Hello   World” into “hello_world”.',
             code="echo 'Hello   World' | tr -s ' ' | tr ' ' '_' | tr '[:upper:]' '[:lower:]'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: locale and big files',
    intro='<p>Your desktop’s language setting changes sort order. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Same data, two locales', cmd="printf 'Bob\\nalice\\nAlice\\n' | sort; echo ---; printf 'Bob\\nalice\\nAlice\\n' | LC_ALL=C sort", output='alice\nAlice\nBob\n---\nAlice\nBob\nalice', note='Typical on Ubuntu with en_IN.UTF-8: dictionary order first, byte order with LC_ALL=C.'),
        dict(title='2 · Biggest folders in your home', cmd='du -sh ~/* 2>/dev/null | sort -rh | head -5', output='12G\t/home/riya/Videos\n4.1G\t/home/riya/Downloads\n900M\t/home/riya/Projects', note='Typical.'),
        dict(title='3 · Sort a 2 GB file faster', cmd='LC_ALL=C sort -S 1G --parallel=4 big.csv -o big_sorted.csv', output='(no output; finishes much faster than plain sort)', note='Typical.'),
        dict(title='4 · Pretty-print a CSV', cmd='column -t -s, employees.csv | head -3', output='id   name   dept         city       salary\n101  Asha   Engineering  Pune       85000\n102  Ravi   Sales        Mumbai     52000', note='Typical.'),
        dict(title='5 · Versions on our build machine', cmd='sort --version | head -1; locale | head -1', output=pc('sort --version | head -1; locale | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A report, variable by variable',
    intro='<p>Step through a script that builds numbers from a CSV.</p>',
    code='''printf 'a,10\\nb,30\\nc,20\\n' > d.csv
n=$(wc -l < d.csv)
top=$(sort -t, -k2,2nr d.csv | head -1 | cut -d, -f1)
sum=$(cut -d, -f2 d.csv | paste -sd+ | bc)
echo "rows=$n top=$top sum=$sum"
''',
    notes={1: 'Data :: Three rows.', 2: 'wc :: 3.', 3: 'sort + cut :: b has 30.', 4: 'paste + bc :: 60.', 5: 'Report :: Together.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a data profile, a disk report and a log summary.'
EXAMPLES = [
    dict(level='b', tag='Data engineer', title='Profile a CSV column',
         problem='<p>How many rows, how many distinct cities, and which city is most common?</p>',
         inp='a small CSV with a header',
         approach=['tail -n +2 skips the header.', 'cut, sort -u, uniq -c.'],
         code='''printf 'id,city\\n1,Pune\\n2,Agra\\n3,Pune\\n4,Goa\\n5,Pune\\n' > c.csv
echo "rows: $(tail -n +2 c.csv | wc -l)"
echo "distinct: $(tail -n +2 c.csv | cut -d, -f2 | sort -u | wc -l)"
tail -n +2 c.csv | cut -d, -f2 | sort | uniq -c | sort -rn | head -1
''',
         notes={2: 'Rows :: 5.', 3: 'Distinct :: 3.', 4: 'Top :: Pune, 3 times.'},
         tryit='Show the least common city.'),
    dict(level='i', tag='System admin', title='Biggest files in a folder',
         problem='<p>List the 3 biggest files in a folder with human sizes.</p>',
         inp='four files of different sizes',
         approach=['du -h per file.', 'sort -rh, head.'],
         code='''mkdir -p f; head -c 2M /dev/zero > f/a; head -c 300K /dev/zero > f/b; head -c 50K /dev/zero > f/c; head -c 1M /dev/zero > f/d
du -h f/* | sort -rh | head -3
''',
         notes={2: 'Sizes :: Largest first.'},
         tryit='Use sort -h without -r.'),
    dict(level='a', tag='DevOps', title='Requests per minute from a log',
         problem='<p>Count requests per minute and show the busiest minute.</p>',
         inp='five log lines',
         approach=['cut the HH:MM part.', 'uniq -c, sort -rn.'],
         code='''printf '%s\\n' '10:01:05 GET /' '10:01:40 GET /a' '10:02:10 GET /' '10:01:59 GET /b' '10:03:00 GET /' > req.log
cut -c1-5 req.log | sort | uniq -c | sort -rn | head -1
''',
         notes={2: 'Pipeline :: 10:01 had 3 requests.'},
         tryit='Show all minutes in time order.'),
]

QUIZ = mix([
    dict(q='What does cut -d: -f1 /etc/passwd print?', options=['passwords', 'user names', 'home folders', 'shells'], answer=1,
         why='Field 1 is the user name.'),
    dict(q='Why sort before uniq?', options=['uniq is slow', 'uniq only merges adjacent equal lines', 'uniq needs numbers', 'It is not needed'], answer=1,
         why='Equal lines must be neighbours.'),
    dict(q='Which sorts by column 3 only, numerically?', options=['sort -k3', 'sort -k3,3n', 'sort -n3', 'sort -c3'], answer=1,
         why='-k3,3 ends the key at field 3; n numeric.'),
    dict(q='Plain sort on 100, 20, 3 gives…', options=['3 20 100', '100 20 3', '20 3 100', '100 3 20'], answer=1,
         why='Text order. Use -n.'),
    dict(q='Which counts lines only?', options=['wc -w', 'wc -l', 'wc -c', 'wc -L'], answer=1,
         why='-l lines.'),
    dict(q="tr 'abc' 'xy' turns abc into…", options=['xy', 'xyy', 'xyc', 'error'], answer=1,
         why='SET2 is padded with its last character.'),
    dict(q='How do you add up a column of numbers?', options=['cut | wc', 'cut | paste -sd+ | bc', 'cut | sort -n', 'cut | uniq -c'], answer=1,
         why='paste builds a+b+c; bc calculates.'),
    dict(q='Which sort understands 2G and 500K?', options=['-n', '-h', '-V', '-g'], answer=1,
         why='human-numeric.'),
])

REVISION = [
    '<code>cut -d, -f2</code> fields; <code>-c1-4</code> characters; default delimiter is TAB; no quote handling.',
    '<code>sort</code> text by default; <code>-n -h -V -g -M</code>; <code>-r -u -f -s</code>; <code>-t, -kN,N</code> (give the end field).',
    'Locale changes text order: <code>LC_ALL=C</code> for byte order. <code>sort -o f f</code> is safe; <code>sort f &gt; f</code> is not.',
    '<code>uniq</code> works on <b>adjacent</b> lines: <code>sort | uniq -c | sort -rn</code>; <code>-d</code> repeated, <code>-u</code> once, <code>-i</code> with <code>sort -f</code>.',
    '<code>wc -l -w -c -m -L</code>; <code>wc -l &lt; f</code> for just the number.',
    '<code>paste -d, a b</code> side by side; <code>-s</code> one line; <code>paste -sd+ | bc</code> a sum.',
    "<code>tr</code> reads stdin only: <code>a-z A-Z</code>, <code>-d '\\r'</code>, <code>-s ' '</code>, <code>-cd '[:digit:]'</code>.",
    'Headers: <code>tail -n +2</code>; keep them: <code>{ head -1 f; tail -n +2 f | sort; }</code>.',
]

FAQ = [
    ('How do I sort a CSV by a column?', 'sort -t, -k3,3 file (add n for numbers, r for reverse). Skip the header with tail -n +2.'),
    ('Why does uniq not remove all duplicates?', 'uniq only removes adjacent duplicates. Sort first: sort file | uniq, or sort -u file.'),
    ('How do I count how many times each line occurs?', 'sort file | uniq -c | sort -rn.'),
    ('How do I extract a column from a file?', 'cut -d, -f2 file for delimited data, cut -c1-10 for positions, or awk for space-separated columns.'),
    ('How do I convert text to upper case in Linux?', "tr '[:lower:]' '[:upper:]' < file (or tr a-z A-Z)."),
    ('How do I remove Windows line endings?', "tr -d '\\r' < in.txt > out.txt (or dos2unix)."),
    ('Why does sort give a different order on another computer?', 'The locale (LANG/LC_ALL) differs. Use LC_ALL=C sort for a fixed byte order.'),
]

PRACTICE_INTRO = 'Small tasks with the six filters. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Sorted names', stmt='Sort the names Riya, Asha, Kabir.', inp='three names',
         code="printf 'Riya\\nAsha\\nKabir\\n' | sort\n", explain='Text order.'),
    dict(level='easy', title='Numbers high to low', stmt='Sort 5, 40, 300 from biggest to smallest.', inp='three numbers',
         code="printf '5\\n40\\n300\\n' | sort -nr\n", explain='-n numeric, -r reverse.'),
    dict(level='easy', title='Line count', stmt='Print only the number of lines in /etc/shells.', inp='/etc/shells',
         code='wc -l < /etc/shells\n', explain='< hides the file name.'),
    dict(level='medium', title='Second column', stmt='Print the second column of a:b:c and d:e:f.', inp='two lines',
         code="printf 'a:b:c\\nd:e:f\\n' | cut -d: -f2\n", explain='-d: -f2.'),
    dict(level='medium', title='Count colours', stmt='Count each colour in red, blue, red, red, green; most first.', inp='five words',
         code="printf 'red\\nblue\\nred\\nred\\ngreen\\n' | sort | uniq -c | sort -rn\n", explain='Frequency table.'),
    dict(level='medium', title='Clean spaces', stmt='Turn “a    b   c” into “a,b,c”.', inp='a string',
         code="echo 'a    b   c' | tr -s ' ' | tr ' ' ','\n", explain='Squeeze, then replace.'),
    dict(level='business', title='Total and count', stmt='Sum 1200, 800 and 2000, and count them.', inp='three amounts',
         code="printf '1200\\n800\\n2000\\n' > amt.txt\necho \"sum $(paste -sd+ amt.txt | bc), count $(wc -l < amt.txt)\"\n", explain='paste + bc, wc.'),
    dict(level='business', title='Second highest', stmt='Print the second highest unique score from 70, 90, 85, 90.', inp='four scores',
         code="printf '70\\n90\\n85\\n90\\n' | sort -nru | sed -n 2p\n", explain='-u removes the duplicate 90; sed -n 2p prints line 2.'),
]

SCN_INTRO = 'Interview questions about these filters, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Remove duplicate lines from a file.”',
        'A favourite first-round question.',
        'do you know uniq needs sorted input?',
        '''<ul>
          <li><code>sort file | uniq</code> or <code>sort -u file</code>.</li>
          <li>Keep the original order: <code>awk '!seen[$0]++' file</code>.</li>
          <li>Count them: <code>sort file | uniq -c</code>.</li>
        </ul>''', 'uniq file alone (misses non-adjacent duplicates).') +
    scn('Operations', 'Junior', 'The disk is 95% full',
        'You have 10 minutes to tell the team what is using the space under /var.',
        'do you combine du and sort correctly?',
        '''<ol>
          <li><code>sudo du -xh --max-depth=1 /var | sort -rh | head</code>.</li>
          <li>Drill into the biggest folder with the same command.</li>
          <li>Check for deleted-but-open files: <code>sudo lsof +L1</code>.</li>
        </ol>''', 'sort -n on human sizes (puts 900K above 2G).') +
    scn('Data team', 'Mid-level', 'Numbers in the report do not match Excel',
        'Your shell report of “top customers” differs from the analyst’s spreadsheet.',
        'do you understand text vs numeric sort and CSV quoting?',
        '''<ul>
          <li>Check <code>-k5,5n</code> (not -k5, not text order) and the locale.</li>
          <li>Quoted fields with commas break cut/sort -t,: count fields per line with awk to find bad rows.</li>
          <li>For real CSV use Python/pandas, csvkit or Miller; keep shell for quick checks.</li>
        </ul>''', '“Excel must be wrong”.') +
    scn('Platform', 'Senior', 'Sorting a 200 GB log on a 16 GB server',
        'A one-off analysis needs the log sorted by user ID.',
        'do you know how GNU sort scales?',
        '''<ul>
          <li>GNU sort does an external merge sort: it writes temporary files to $TMPDIR; make sure that disk has space (<code>-T /bigdisk/tmp</code>).</li>
          <li><code>LC_ALL=C</code>, <code>-S 8G</code>, <code>--parallel</code>, <code>--compress-program=zstd</code> speed it up.</li>
          <li>Or split by key and sort in parallel, or load it into a columnar tool (DuckDB, Spark).</li>
        </ul>''', 'buying more RAM first.')
) + interview([
    ('Difference between sort -u and sort | uniq?', 'Same result for whole lines; -u is one process. uniq has extra options (-c -d -u).'),
    ('How do you sort numerically in reverse?', 'sort -nr.'),
    ('How do you sort by the second column of a CSV?', 'sort -t, -k2,2.'),
    ('What does uniq -c do?', 'Prefixes each group of adjacent equal lines with its count.'),
    ('How do you count words in a file?', 'wc -w file.'),
    ('Convert lowercase to uppercase?', "tr '[:lower:]' '[:upper:]'."),
    ('Extract the third field of a colon-separated file?', 'cut -d: -f3 file.'),
], [
    ('RHCSA (EX200)', 'Use text filters to analyse text (grep, sort, cut, wc, uniq, tr) in pipelines.'),
    ('LFCS', 'Essential commands: process text streams with filters.'),
    ('CompTIA Linux+', 'Text-processing commands: sort, uniq, cut, paste, tr, wc.'),
]) + distro('These are POSIX tools, but GNU versions have extra options.', [
    ('sort -h / -V / --parallel', 'GNU: yes', 'GNU: yes', 'BSD sort: -h yes, -V yes on recent macOS', 'GNU'),
    ('uniq -i -f -s -w', 'yes', 'yes', '-w missing on BSD', 'yes'),
    ('cut --complement / --output-delimiter', 'GNU', 'GNU', 'no on BSD', 'GNU'),
    ('wc -L', 'GNU', 'GNU', 'no on BSD', 'GNU'),
    ('Default sort order', 'locale (en_IN, C.UTF-8)', 'locale', 'locale', 'locale'),
    ('tr classes [:upper:]', 'yes', 'yes', 'yes', 'yes'),
]) + teaser('6.3', 'Yesterday’s user list has 412 names, today’s has 415. Which three users are new, which one was removed, and did the config file change between the two servers? Three commands compare files: which ones?')

CHEATSHEET = cheatsheet('sort, uniq, wc, cut, paste, tr', [
    ('cut', [('cut -d, -f2', 'field 2'), ('-f1,3 / -f2-', 'list / from 2'), ('-c1-4', 'characters'), ('-d: -f1 /etc/passwd', 'users'), ('--complement', 'all but')]),
    ('sort', [('sort -n / -r', 'numbers / reverse'), ('-t, -k5,5nr', 'by column'), ('-h / -V', 'sizes / versions'), ('-u / -f', 'unique / no case'), ('-o f f', 'in place')]),
    ('uniq', [('sort | uniq', 'dedupe'), ('uniq -c', 'count'), ('-d / -u', 'repeated / once'), ('sort -f | uniq -i', 'no case'), ("awk '!s[$0]++'", 'keep order')]),
    ('wc · paste', [('wc -l < f', 'lines'), ('wc -w / -m / -L', 'words / chars / longest'), ('paste -d, a b', 'side by side'), ('paste -sd,', 'one line'), ('paste -sd+ | bc', 'sum')]),
    ('tr', [('tr a-z A-Z', 'capitals'), ("tr -d '\\r'", 'Windows CR'), ("tr -s ' '", 'squeeze'), ("tr -cd '[:digit:]'", 'digits only'), ("tr ' ' '\\n'", 'one word per line')]),
])

MINDMAP = mindmap('Six filters', [
    ('cut', 'blue', ['-d -f fields', '-c positions', 'no CSV quotes']),
    ('sort', 'green', ['-n -h -V', '-t -kN,N', 'locale, -o']),
    ('uniq', 'amber', ['adjacent only', '-c -d -u', 'sort first']),
    ('wc', 'violet', ['-l -w', '-c bytes, -m chars', '-L longest']),
    ('paste', 'acc', ['side by side', '-s one line', '-sd+ | bc']),
    ('tr', 'red', ['a-z A-Z', '-d -s', '-cd classes']),
])

LAB = lab('build the HR report', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab62 && cd ~/lab62 && rm -f *
printf 'id,name,dept,salary\\n1,Asha,Eng,85000\\n2,Ravi,Sales,52000\\n3,Meena,Eng,98000\\n4,Kabir,HR,47000\\n5,Riya,Sales,61000\\n' > emp.csv''',
    tasks=['Write the headcount per department, biggest first, into <code>depts.txt</code> (format of <code>uniq -c</code>).',
           'Write the name of the highest-paid employee into <code>top.txt</code>.',
           'Write the total of all salaries into <code>total.txt</code>.',
           'Write the names in capital letters, sorted, one per line, into <code>names.txt</code>.'],
    solution='''tail -n +2 emp.csv | cut -d, -f3 | sort | uniq -c | sort -rn > depts.txt
tail -n +2 emp.csv | sort -t, -k4,4nr | head -1 | cut -d, -f2 > top.txt
tail -n +2 emp.csv | cut -d, -f4 | paste -sd+ | bc > total.txt
tail -n +2 emp.csv | cut -d, -f2 | tr '[:lower:]' '[:upper:]' | sort > names.txt''',
    check='''cd ~/lab62
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 headcount"   '[ "$(tail -1 depts.txt 2>/dev/null | tr -s " " | sed "s/^ //")" = "1 HR" ] && [ "$(wc -l < depts.txt 2>/dev/null)" = 3 ]'
ok "2 top earner"  '[ "$(cat top.txt 2>/dev/null)" = Meena ]'
ok "3 total"       '[ "$(cat total.txt 2>/dev/null)" = 343000 ]'
ok "4 names"       '[ "$(cat names.txt 2>/dev/null)" = "$(printf "ASHA\\nKABIR\\nMEENA\\nRAVI\\nRIYA")" ]' ''')
