import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
from linuxkit import *
from _data import APPLOG, ACCESS, EMP

HOOK = hook('Friday, 5 pm. The HR head asks Riya: “From employees.csv, how many people per department, the three highest salaries, the total salary bill, and the cities in capital letters, please, before you leave.” There is no spreadsheet on the server. Six tiny commands answer all of it in under a minute: <code>cut</code> takes a column, <code>sort</code> orders it, <code>uniq -c</code> counts, <code>wc</code> measures, <code>paste</code> joins, <code>tr</code> changes characters.',
    ['take columns out of CSV, log and system files with <code>cut</code>, and join them back with <code>paste</code>',
     'sort text, numbers, sizes, versions and multi-column data correctly with <code>sort -n -r -k -t -h -V -u</code>',
     'remove and count duplicates with <code>uniq -c -d -u -i -f -w</code> (and know why sort must come first)',
     'count with <code>wc</code> and change characters with <code>tr</code> (case, delete, squeeze, Windows line endings)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the HR report at 5 pm'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What the six tools are', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each tool, by field', 18, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'a column becoming a report'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('One column of a CSV or : file', 'cut -d, -f3 file', '-f1,3 several, -f2- from 2 on'),
    ('Characters 1 to 4 of each line', 'cut -c1-4 file', 'fixed-width data'),
    ('Order lines', 'sort file', '-r reverse, -u unique'),
    ('Order numbers', 'sort -n', '-h for 2G 500K, -V for versions'),
    ('Order by a column', 'sort -t, -k5,5nr', 'always give the end field ,5'),
    ('Remove duplicate lines', 'sort | uniq  (or sort -u)', 'uniq needs sorted input'),
    ('Count each value', 'sort | uniq -c | sort -rn', 'the frequency table'),
    ('Lines / words / characters', 'wc -l / -w / -m', '-c bytes, -L longest line'),
    ('Put two files side by side', 'paste -d, a b', 'paste -sd+ | bc = a sum'),
    ('Change or delete characters', "tr a-z A-Z  /  tr -d '\\r'", 'tr -s squeezes repeats'),
])

cmap = concept_map(
    [('5.3', 'Pipes', 'cmd | cmd | cmd'), ('6.1', 'grep', 'pick lines first'), ('3.5', 'Viewing files', 'head, tail, wc')],
    ['cut: columns by delimiter (-d -f) or position (-c)', 'sort: -n -r -u -f -k -t -h -V -s -o -c', 'uniq: -c -d -u -i -f -s -w', 'wc: -l -w -c -m -L', 'paste: side by side, -s, -d; tr: translate, -d, -s, -c'],
    [('6.3', 'Comparing files', 'diff, comm, join'), ('6.5', 'awk', 'when columns need logic'), ('13.5', 'Data one-liners', 'CSV and JSON work'), ('13.3', 'Log analysis', 'top IPs and counts')],
    'These six small filters are the building blocks of almost every data one-liner. Learn them well and most pipelines become easy to read and write.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ tail -n +2 employees.csv | cut -d, -f3 |', '  sort | uniq -c | sort -rn', ('      3 Engineering', 'acc'), ('      2 Sales', 'acc'), ('      1 HR', 'acc'), "$ cut -d, -f5 employees.csv | tail -n +2 |", '  paste -sd+ | bc', ('415000', 'acc')], title='riya@hr-server: ~', size=7.0, step=15)
      + t(352, 36, 'Six tiny tools:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• cut: a column', '• sort: order', '• uniq -c: count', '• wc: measure', '• paste / tr: join, change'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The HR report at 5 pm</h2>
  <div class="story">
''' + puzzle('Riya sorts the numbers 100, 20, 3, 1000 and 5 with plain <code>sort</code>. In which order do they come out, and why? Then: a file has apple twice, banana three times, cherry once and apple twice more at the end. What does <code>sort file | uniq -c</code> print for apple?') + '''
    <p class="narration">HR wants numbers from employees.csv before the weekend, and the server has no Excel.</p>
''' + scene('A terminal: cut the department column, sort, uniq -c and sort -rn give 3 Engineering, 2 Sales, 1 HR; cut the salary column, paste -sd+ and bc give 415000.', sc,
            'Each tool does one small job; <tspan font-weight="700" class="s-acc">the pipe joins them</tspan>.') + '''
A> Think of the CSV as a table. <code>cut</code> picks a column, <code>sort</code> puts it in order, <code>uniq -c</code> counts each value.
R> And the total salary?
K> Cut the salary column, glue the numbers with + using <code>paste -sd+</code>, and give that to <code>bc</code>.
A> Today: cut, sort, uniq, wc, paste and tr, each explained, then used by admins, data engineers, DBAs, developers, DevOps, security and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A kitchen: a knife cuts one column of vegetables (cut), a tray arranges them in order (sort), a counter counts each kind (uniq -c), a ruler measures (wc), tape joins two trays (paste), and paint changes colours (tr).">'
       + ''.join(label_box(10 + k * 105, 30, 96, 90, [a, b, c], tone, 8.6) for k, (a, b, c, tone) in enumerate([
           ('cut', 'knife', 'one column', 'blue'), ('sort', 'tray', 'in order', 'green'), ('uniq -c', 'tally', 'count kinds', 'amber'),
           ('wc', 'ruler', 'measure', 'violet'), ('paste', 'tape', 'join trays', 'card'), ('tr', 'paint', 'change chars', 'red')]))
       + t(320, 160, 'Six kitchen tools, each for one small job,', 9.6, 'ink2')
       + t(320, 182, 'used one after another on a moving belt (the pipe).', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('The six tools at four depths', [
    ('v', 'No jargon: a kitchen', '      <p>Think of preparing vegetables for a big order.</p>' + pic + '''
      <ul>
        <li><code>cut</code> is a knife that takes just one column of the table.</li>
        <li><code>sort</code> lays everything out in order; <code>uniq -c</code> counts how many of each kind lie next to each other.</li>
        <li><code>wc</code> is a ruler; <code>paste</code> tapes two lists side by side; <code>tr</code> repaints characters.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>cut -d, -f2 file.csv</code>: column 2 of a CSV. <code>cut -d: -f1 /etc/passwd</code>: user names.</li>
        <li><code>sort names.txt</code>, <code>sort -n numbers.txt</code>, <code>sort -r</code>, <code>sort -u</code>.</li>
        <li><code>sort file | uniq -c | sort -rn</code>: how many of each, biggest first.</li>
        <li><code>wc -l file</code>: number of lines.</li>
        <li><code>tr a-z A-Z</code>: capitals; <code>tr -d ' '</code>: delete spaces.</li>
      </ul>'''),
    ('i', 'Columns, keys and traps', '''      <ul>
        <li><code>sort -k5,5nr -t,</code>: sort by field 5 only (<code>,5</code> ends the key), numeric, reversed. Without <code>,5</code> the key runs to the end of the line.</li>
        <li>Plain sort compares <b>text</b>: 100 comes before 20. Use <code>-n</code>, <code>-h</code> (2G, 500K) or <code>-V</code> (v1.10 after v1.9).</li>
        <li><code>uniq</code> only merges <b>adjacent</b> equal lines: always sort first, or use <code>sort -u</code>.</li>
        <li><code>cut</code> knows nothing about quotes: <code>"Sharma, Riya"</code> is split at its comma. Use a real CSV tool (csvkit, Python, or awk with care) for quoted CSV.</li>
        <li><code>tr</code> reads only stdin and works on single characters, not words: <code>tr 'abc' 'xy'</code> maps a→x, b→y, c→y.</li>
      </ul>'''),
    ('a', 'Behind the screen: locale, memory and stability', '''      <ul>
        <li>sort’s order depends on the <b>locale</b>: in <code>C</code> / <code>C.UTF-8</code> capitals come before small letters (byte order); in <code>en_IN.UTF-8</code> it is dictionary order (alice before Bob). Scripts often set <code>LC_ALL=C</code> for predictable, faster results.</li>
        <li>GNU sort handles files larger than memory: it sorts chunks into temporary files (in <code>$TMPDIR</code>) and merges them; <code>-S 2G</code> sets the buffer, <code>--parallel=4</code> uses more cores.</li>
        <li>When keys are equal sort compares the whole line as a last resort; <code>-s</code> (stable) keeps the input order instead.</li>
        <li><code>wc -c</code> counts bytes, <code>-m</code> counts characters: “héllo” is 7 bytes but 6 characters in UTF-8.</li>
        <li><code>uniq -c</code> width, <code>cut</code> delimiters and <code>tr</code> classes like <code>[:upper:]</code> follow POSIX, so they behave the same on every Linux.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>sort, uniq, wc, cut, paste and tr</h2>
''' + def_block(
    '<code>cut</code> prints selected fields (by delimiter) or character positions of each line. <code>sort</code> orders lines (as text, numbers, sizes or versions, by whole line or by key fields). <code>uniq</code> removes or counts <b>adjacent</b> duplicate lines. <code>wc</code> counts lines, words, bytes and characters. <code>paste</code> merges lines of files side by side. <code>tr</code> translates, deletes or squeezes characters read from standard input.',
    'Take a column, put it in order, count the repeats, measure it, glue lists, change characters.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Field / delimiter', f'A column, and the character between columns (, : tab). {gl("field-and-delimiter", "Glossary →")}'),
    ('Key', 'The part of a line sort compares (-k).'),
    ('Numeric vs text sort', '3 &lt; 20 &lt; 100 as numbers; “100” &lt; “20” as text.'),
    ('Adjacent', 'Next to each other: what uniq looks at.'),
    ('Locale', 'Language settings that decide sort order (LANG, LC_ALL).'),
    ('sort and uniq', f'{gl("sort-and-uniq", "Glossary →")}'),
    ('cut, tr and wc', f'{gl("cut-tr-and-wc", "Glossary →")}'),
    ('CR / LF', 'Windows lines end with \\r\\n, Linux with \\n.'),
]) + '\n' + names('Where the names come from.', [
    ('cut', 'cut', 'Cuts columns out of lines.'),
    ('sort', 'sort', 'One of the oldest Unix programs (1971).'),
    ('uniq', 'unique', 'Keeps one of each run of equal lines.'),
    ('wc', 'word count', 'Also lines and bytes.'),
    ('paste', 'paste', 'The opposite of cut: puts columns together.'),
    ('tr', 'translate', 'Character by character.'),
    ('-k / -t', 'key / tab (separator)', 'sort’s column options.'),
    ('-h / -V', 'human / version', '2G &gt; 500K; v1.10 &gt; v1.9.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Column 2 of a CSV', '<code>cut -d, -f2 f.csv</code>'),
    ('Numbers in order', '<code>sort -n</code>  (biggest first: <code>-nr</code>)'),
    ('By column 5, numeric', '<code>sort -t, -k5,5n</code>'),
    ('Frequency table', '<code>sort | uniq -c | sort -rn</code>'),
    ('Sum a column', '<code>cut … | paste -sd+ | bc</code>'),
    ('To capitals', "<code>tr '[:lower:]' '[:upper:]'</code>"),
]) + '\n' + lv + didyou('<code>sort</code> can sort files much bigger than your RAM. When the data does not fit, it sorts it in pieces, writes the sorted pieces to temporary files and then merges them, the same “external merge sort” that big-data systems like Hadoop use for terabytes.') + '''
EXAM> “Find the top 5 most frequent values in column 3 of a comma-separated file.” → cut -d, -f3 file | sort | uniq -c | sort -rn | head -5 (skip a header with tail -n +2; explain why sort comes before uniq).
''' + qc('Why does <code>sort</code> put 100 before 20?', 'Without -n it compares text character by character: “1” comes before “2”. Use <code>sort -n</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>sort’s ways of comparing</h2>
''' + table(['Option', 'Compares as', 'Example input → output'], [
    ['(none)', 'text, by the locale', '100 20 3 → 100 20 3 (text)'],
    ['<code>-n</code>', 'numbers', '100 20 3 → 3 20 100'],
    ['<code>-g</code>', 'general numbers (1.5e10)', 'scientific notation'],
    ['<code>-h</code>', 'human sizes', '2G 500K 1.5M → 500K 1.5M 2G'],
    ['<code>-V</code>', 'version numbers', 'v1.10.2 v1.9.5 → v1.9.5 v1.10.2'],
    ['<code>-M</code>', 'month names', 'Mar Jan Feb → Jan Feb Mar'],
    ['<code>-f</code> / <code>-d</code> / <code>-b</code>', 'ignore case / dictionary / leading blanks', 'tidy text'],
    ['<code>-r</code> / <code>-u</code> / <code>-s</code>', 'reverse / unique / stable', 'any of the above'],
    ['<code>-t, -k3,3 -k5,5nr</code>', 'field 3, then field 5 numeric reverse', 'multi-column reports'],
], minw=560) + mistake('sort -k2 data.txt   (meant: sort by column 2 only)', 'sort -k2,2 data.txt   ·   numbers: sort -k2,2n',
                       '-k2 means “from field 2 to the end of the line”. With equal column-2 values the rest of the line decides the order, which surprises people. Give the end field.') + qc('Which sort gives 500K, 1.5M, 2G in that order?', '<code>sort -h</code>') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each tool explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 (GNU coreutils 9.4, locale C.UTF-8) with a sample <code>employees.csv</code>: id,name,dept,city,salary for six employees.</p>
''' + cmdcard_u(['one or more columns of CSV, /etc/passwd, logs', 'fixed positions: dates, codes, IDs', 'quick extraction before sort, uniq or paste'],
               ['CSV with quoted commas (use a CSV tool or Python)', 'columns separated by a varying number of spaces (use awk or tr -s first)'])(
    'cut', 'cut', 'cut columns',
    'Prints parts of each line: fields separated by one delimiter character (<code>-d</code> + <code>-f</code>), or character/byte positions (<code>-c</code>/<code>-b</code>).',
    "cut -d'DELIM' -f LIST [FILE]   ·   cut -c LIST [FILE]", 'safe',
    [('-d, -f2', 'field 2 of a CSV', 'one column'),
     ('-f1,3', 'fields 1 and 3', 'several columns'),
     ('-f2-4 / -f3- / -f-2', 'range / from 3 / up to 2', 'groups of columns'),
     ('-d: -f1', 'user names in /etc/passwd', 'system files'),
     ('-c1-4', 'characters 1 to 4', 'fixed width, dates'),
     ('--complement', 'everything except these fields', 'drop a column'),
     ('--output-delimiter=" | "', 'different separator in the output', 'readable reports'),
     ('(default -d)', 'TAB is the default delimiter', 'TSV files')],
    dict(setup=EMP, cmd="cut -d, -f2 employees.csv | head -3\ncut -d, -f2,5 employees.csv | head -3\ncut -d, -f3 --complement employees.csv | head -2", note='Each line is cut separately; the header is a line too (tail -n +2 skips it).'),
    [('sys', [
        dict(situation='User names and their shells from /etc/passwd.', cmd="cut -d: -f1,7 /etc/passwd | head -4",
             why='/etc/passwd uses : between its 7 fields.'),
        dict(situation='The 1-minute load average (from your notes, corrected).', cmd="cut -d' ' -f1 /proc/loadavg | sed 's/[0-9]/9/g'\ncut -d' ' -f1 /proc/uptime | sed 's/[0-9]/9/g'",
             why='These files are separated by spaces, so -d\' \' is needed. (Digits are masked to 9 here because they change every second.)')]),
     ('data', [
        dict(situation='The year and month from ISO dates.', cmd="printf '2026-11-06\\n2026-10-31\\n' | cut -c1-7",
             why='Fixed-width data: -c by position is simplest.'),
        dict(situation='Why cut breaks quoted CSV (a real limit).', cmd="echo '7,\"Sharma, Riya\",Pune' | cut -d, -f2",
             why='cut splits at every comma, even inside quotes. Use <code>python3 -c "import csv…"</code>, csvkit or Miller for real CSV.')]),
     ('web', [
        dict(situation='Count requests per HTTP method from an access log.', setup=ACCESS, cmd="cut -d'\"' -f2 access.log | cut -d' ' -f1 | sort | uniq -c",
             why='Field 2 between the quotes is the request line; its first word is the method.')]),
     ('devops', [
        dict(situation='Email domains of a user list.', cmd="printf 'asha@cdac.in\\nravi@gmail.com\\nmeena@cdac.in\\n' > mails.txt\ncut -d@ -f2 mails.txt | sort | uniq -c",
             why='Any single character can be the delimiter.')]),
    ],
    anat=anatomy([('cut', 'cmd', 'command'), ('-d,', 'opt', 'delimiter: comma'), ('-f2,5', 'opt', 'fields 2 and 5'), ('employees.csv', 'arg', 'file')], 'No space is needed after -d and -f; quote special delimiters: -d\' \', -d\'"\'.')
) + mistake("cut -f1 /proc/uptime   (“system uptime in seconds”)", "cut -d' ' -f1 /proc/uptime",
            'cut’s default delimiter is TAB. /proc/uptime has a space, so without -d\' \' the whole line is printed (verified).') + cmdcard_u(['ordering lines: names, numbers, sizes, versions, dates', 'reports by one or more columns', 'preparing input for uniq, comm and join'],
               ['data with quoted CSV commas in the key columns', 'when the original order matters (use sort -s, or awk)'])(
    'sort', 'sort', 'sort lines',
    'Sorts lines. By default compares the whole line as text using the locale. Options choose numeric, human, version or month comparison, keys (columns), reverse order and uniqueness.',
    'sort [-n|-h|-V|-g|-M] [-r] [-u] [-f] [-t SEP] [-k F1[,F2][n|r…]] [-o OUT] [FILE…]', 'safe',
    [('-n', 'numeric', '3 20 100'),
     ('-r', 'reverse', 'biggest first'),
     ('-u', 'unique', 'remove duplicates while sorting'),
     ('-f', 'ignore case', 'names'),
     ('-t, -k5,5n', 'by field 5, numeric', 'CSV columns'),
     ('-k3,3 -k5,5nr', 'by dept, then salary down', 'two-level report'),
     ('-h / -V', 'sizes / versions', 'du output, releases'),
     ('-o FILE', 'write to FILE (may be the input)', 'sort in place safely'),
     ('-c', 'check if sorted (exit 1 if not)', 'validate'),
     ('-s', 'stable: keep input order for ties', 'predictable reports')],
    dict(cmd="printf '100\\n20\\n3\\n1000\\n5\\n' > nums.txt\nsort nums.txt | tr '\\n' ' '; echo\nsort -n nums.txt | tr '\\n' ' '; echo\nsort -nr nums.txt | tr '\\n' ' '; echo", note='Text order puts 100 and 1000 before 20: the first part of the puzzle.'),
    [('data', [
        dict(situation='Top 3 salaries (header removed).', setup=EMP, cmd="tail -n +2 employees.csv | sort -t, -k5,5nr | head -3",
             why='-t, sets the delimiter, -k5,5 uses only column 5, n numeric, r reverse.'),
        dict(situation='By department, then by salary high to low.', setup=EMP, cmd="tail -n +2 employees.csv | sort -t, -k3,3 -k5,5nr",
             why='Several -k options: the second is used only when the first is equal.'),
        dict(situation='Keep the header on top while sorting the rest.', setup=EMP, cmd="{ head -n 1 employees.csv; tail -n +2 employees.csv | sort -t, -k5,5n; }",
             why='Braces group the two commands into one output (Lesson 5.4).')]),
     ('sys', [
        dict(situation='The biggest folders, in human sizes.', cmd="mkdir -p d1 d2 d3; head -c 3M /dev/zero > d1/f; head -c 200K /dev/zero > d2/f; head -c 40K /dev/zero > d3/f\ndu -sh d1 d2 d3 | sort -rh",
             why='du -h prints 3.1M, 204K…; only sort -h understands those suffixes.')]),
     ('devops', [
        dict(situation='The newest release tag.', cmd="printf 'v1.10.2\\nv1.2.1\\nv1.10.10\\nv2.1.0\\nv1.9.5\\n' | sort -V | tail -n 1",
             why='-V knows that 1.10 is after 1.9. Text sort would pick the wrong “latest”.')]),
     ('qa', [
        dict(situation='Check that an export is sorted before loading it.', cmd="printf '1\\n3\\n2\\n' > ids.txt\nsort -n -c ids.txt; echo \"exit $?\"",
             why='-c reports the first line out of order and exits 1: a cheap data-quality check.', expect='any')]),
    ]
) + mistake("tail -n +2 employees.csv | sort -t',' -k3n | head -1 employees.csv -", "{ head -n 1 employees.csv; tail -n +2 employees.csv | sort -t, -k5,5n; }",
            'head with two inputs prints file-name headers and only the <b>first</b> line of each (a real run showed “==&gt; employees.csv &lt;==” and one data row). Group the two commands with braces instead.') + cmdcard_u(['removing duplicates after sort', 'counting how often each value occurs', 'finding values that appear once or more than once'],
               ['unsorted input (it only sees neighbours)', 'keeping the first occurrence in the original order (use awk \'!seen[$0]++\')'])(
    'uniq', 'uniq', 'unique adjacent lines',
    'Reads lines and merges runs of identical <b>adjacent</b> lines. With options it counts them, or prints only repeated or only unique ones.',
    'uniq [-c] [-d|-u] [-i] [-f N] [-s N] [-w N] [INPUT [OUTPUT]]', 'safe',
    [('(none)', 'one of each run', 'after sort'),
     ('-c', 'count each run', 'frequency tables'),
     ('-d', 'only lines that repeat', 'duplicates'),
     ('-u', 'only lines that appear once', 'singletons'),
     ('-i', 'ignore case (input sorted with sort -f)', 'mixed case'),
     ('-f N', 'skip the first N fields', 'ignore an ID column'),
     ('-s N / -w N', 'skip / compare only N characters', 'prefixes')],
    dict(cmd="printf 'apple\\napple\\nbanana\\nbanana\\nbanana\\ncherry\\napple\\napple\\n' > fruits.txt\nuniq fruits.txt | tr '\\n' ' '; echo\nsort fruits.txt | uniq -c", note='Without sort, apple appears twice (two separate runs). With sort, apple is counted <b>4</b> times: the second part of the puzzle.'),
    [('data', [
        dict(situation='Headcount per department.', setup=EMP, cmd="tail -n +2 employees.csv | cut -d, -f3 | sort | uniq -c | sort -rn",
             why='The classic frequency table: cut, sort, count, rank.'),
        dict(situation='Keep the first of each, in the original order (no sort).', cmd="printf 'b\\na\\nb\\nc\\na\\n' | awk '!seen[$0]++'",
             why='awk remembers what it has seen (Lesson 6.5). Useful when order matters.')]),
     ('sys', [
        dict(situation='Duplicate user IDs are a security problem: find them.', cmd="printf 'root:x:0\\nasha:x:1001\\nghost:x:0\\n' > pw.txt\ncut -d: -f3 pw.txt | sort -n | uniq -d",
             why='Two accounts with UID 0 both have root power. uniq -d shows repeated values.')]),
     ('qa', [
        dict(situation='Case-insensitive duplicates (from your notes, corrected).', cmd="printf 'Apple\\napple\\nAPPLE\\nBanana\\nbanana\\nCherry\\n' > mixed.txt\nsort mixed.txt | uniq -ci\necho ---\nsort -f mixed.txt | uniq -ci",
             why='In the C locale plain sort separates APPLE, Apple … from apple, so uniq -i cannot see them as neighbours. Sort with -f first.')]),
     ('web', [
        dict(situation='IPs that made only one request.', setup=ACCESS, cmd="cut -d' ' -f1 access.log | sort | uniq -u",
             why='-u keeps values that appear exactly once.')]),
    ]
) + mistake("sort sample.txt | uniq -c  →  “3 apple”  ·  sort structured.txt | uniq -f 1  →  2 lines  ·  sort prefixes.txt | uniq -cw 6  →  “2 apple123”",
            "4 apple (two runs of 2) · 4 lines (apple red ≠ apple green) · nothing merged with -w 6 (apple1 ≠ apple4); -w 5 merges them",
            'Three sample outputs in common notes do not match real runs. Run the command and read the result before writing the expected output.') + cmdcard_u(['how big is it: lines, words, characters', 'counting results of other commands (… | wc -l)', 'checking line lengths (-L)'],
               ['counting matches in one file (grep -c is shorter)'])(
    'wc', 'wc', 'word count',
    'Prints counts of lines, words and bytes (default), or only the ones you ask for. With several files it adds a total line.',
    'wc [-l] [-w] [-c] [-m] [-L] [FILE…]', 'safe',
    [('(none)', 'lines, words, bytes', 'overview'),
     ('-l', 'lines', 'rows, log entries'),
     ('-w', 'words', 'documents'),
     ('-c / -m', 'bytes / characters', 'sizes; UTF-8 text'),
     ('-L', 'length of the longest line', 'find over-long lines'),
     ('wc -l < file', 'number only, no name', 'scripts')],
    dict(setup=EMP, cmd="wc employees.csv\nwc -l < employees.csv\nwc -L employees.csv\nprintf 'héllo\\n' | wc -c -m", note='7 lines, 7 words (no spaces in the CSV), 209 bytes. “héllo” is 7 bytes but 6 characters: é takes 2 bytes in UTF-8.'),
    [('data', [
        dict(situation='Rows in each CSV of an export, with a total.', cmd="seq 1 4 > jan.csv; seq 1 6 > feb.csv\nwc -l jan.csv feb.csv",
             why='Several files give a total line at the end.')]),
     ('dev', [
        dict(situation='Lines of code in a project.', cmd="mkdir -p src; seq 1 40 > src/a.py; seq 1 12 > src/b.py\nwc -l src/*.py | tail -n 1",
             why='The total line is the last line.')]),
    ]
) + cmdcard_u(['putting columns from different files side by side', 'joining all lines into one (-s)', 'building sums and lists: paste -sd+'],
               ['matching rows by a key (use join, Lesson 6.3)'])(
    'paste', 'paste', 'merge lines side by side',
    'Joins line 1 of each file, line 2 of each file, and so on, separated by TAB (or <code>-d</code>). <code>-s</code> joins all lines of one file into one line. <code>-</code> reads stdin.',
    'paste [-d LIST] [-s] FILE…', 'safe',
    [('paste a b', 'side by side, TAB between', 'two lists'),
     ('-d,', 'comma between', 'build a CSV'),
     ('-s', 'all lines of a file into one line', 'one row'),
     ('-sd+', 'join with +', 'a sum for bc'),
     ("paste - - ", 'two lines of stdin per row', 'reshape lists')],
    dict(setup=EMP, cmd="cut -d, -f2 employees.csv > names.txt; cut -d, -f5 employees.csv > sal.txt\npaste -d, names.txt sal.txt | head -3\ntail -n +2 sal.txt | paste -sd+\ntail -n +2 sal.txt | paste -sd+ | bc", note='paste -sd+ builds 85000+52000+…; bc adds it: 415000.'),
    [('data', [
        dict(situation='Reshape a list into two columns.', cmd="printf 'Pune\\n41\\nAgra\\n39\\n' | paste -d: - -",
             why='Each - reads one line from stdin, so two lines become one row.')]),
     ('devops', [
        dict(situation='A comma-separated host list for a config file.', cmd="printf 'web01\\nweb02\\ndb01\\n' | paste -sd,",
             why='Many tools want hosts=web01,web02,db01 on one line.')]),
    ]
) + cmdcard_u(['changing case, replacing or deleting characters', 'cleaning data: Windows line endings, punctuation, repeated spaces', 'one word per line (tr \' \' \'\\n\')'],
               ['replacing words or patterns (use sed, Lesson 6.4)', 'reading files directly: tr reads only stdin'])(
    'tr', 'tr', 'translate characters',
    'Reads stdin and replaces each character of SET1 by the matching character of SET2, or deletes (<code>-d</code>) or squeezes (<code>-s</code>) characters. <code>-c</code> uses the complement of SET1.',
    "tr SET1 SET2   ·   tr -d SET   ·   tr -s SET   ·   tr -cd SET   (input: stdin)", 'safe',
    [("tr a-z A-Z", 'to capitals', 'normalise'),
     ("'[:lower:]' '[:upper:]'", 'the same, locale-aware classes', 'portable'),
     ("tr ' ' '_'", 'spaces to underscores', 'file names'),
     ("tr -d '\\r'", 'delete Windows CR', 'files from Windows'),
     ("tr -s ' '", 'squeeze repeated spaces', 'before cut'),
     ("tr -cd '[:digit:]'", 'keep only digits', 'phone numbers'),
     ("tr ' ' '\\n'", 'one word per line', 'word counts')],
    dict(cmd="echo 'pune' | tr a-z A-Z\necho 'a  b    c' | tr -s ' '\necho 'Ph: (020) 2556-1234' | tr -cd '[:digit:]'; echo\necho 'abc' | tr 'abc' 'xy'", note='The last line shows tr works per character: SET2 is shorter, so its last character y is repeated for c.'),
    [('sys', [
        dict(situation='A script edited on Windows fails with “bad interpreter”: remove the \\r.', cmd="printf '#!/bin/bash\\r\\necho hi\\r\\n' > win.sh\ncat -A win.sh | head -1\ntr -d '\\r' < win.sh > unix.sh; cat -A unix.sh | head -1",
             why='cat -A shows ^M (the CR). After tr the line ends with $ only.')]),
     ('data', [
        dict(situation='Word frequency in a sentence (case-insensitive).', cmd="echo 'The cat and THE dog and the bird' | tr '[:upper:]' '[:lower:]' | tr ' ' '\\n' | sort | uniq -c | sort -rn | head -3",
             why='Lower-case first, one word per line, then the frequency table.')]),
     ('devops', [
        dict(situation='Make ps output cut-friendly (from your notes).', cmd="ps -eo user,pid,pcpu,comm | head -3 | tr -s ' ' | cut -d' ' -f1,2,4",
             why='ps pads columns with many spaces; tr -s squeezes them to one so cut can split.')]),
     ('sec', [
        dict(situation='Generate a random 12-character password.', cmd="tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 12 | wc -c",
             why='-dc keeps only the allowed characters from random bytes. (Only the length is shown, to keep the output stable.)')]),
    ]
) + undo('These tools only print; the risk is in where you send the output.', [
    ('sort f > f emptied the file:', 'use <code>sort -o f f</code> (safe) or write to a new file (Lesson 5.2).'),
    ('Wrong order:', 'check the locale (<code>LC_ALL=C sort</code>) and the key (<code>-k3,3</code> not <code>-k3</code>).'),
    ('uniq missed duplicates:', 'sort first, and use the same options (-f) in sort and uniq.'),
    ('cut gave strange columns:', 'look at the separators with <code>cat -A</code>; tabs (^I) vs spaces; squeeze with <code>tr -s</code>.'),
]) + errors('Errors students see most with these tools. Each was really produced on our build machine.', [
    dict(cmd='cut -f', meaning='-f needs a list of fields.', fix='<code>cut -d, -f2</code>.'),
    dict(cmd="cut -d', ' -f1 /etc/hostname", meaning='The delimiter must be a single character.', fix='Use one character, or <code>awk -F\', \'</code>.'),
    dict(cmd='tr a-z A-Z /etc/hostname', meaning='tr does not take file names; it reads only stdin.', fix='<code>tr a-z A-Z &lt; /etc/hostname</code>.'),
    dict(cmd="printf '1\\n3\\n2\\n' | sort -n -c", meaning='Not sorted: sort -c reports the first line out of order.', fix='Sort it, or fix the data.'),
    dict(cmd='sort -k0 /etc/hostname', meaning='Fields are numbered from 1.', fix='<code>-k1</code>.'),
]) + qc('Write a pipeline that prints the number of employees per city, most first.', "<code>tail -n +2 employees.csv | cut -d, -f4 | sort | uniq -c | sort -rn</code>") + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
STAGES = ['employees.csv', 'tail -n +2', 'cut -f3', 'sort', 'uniq -c', 'sort -rn']
DATA = [['id,name,dept,…', '101,Asha,Engg,…', '102,Ravi,Sales,…', '104,Kabir,HR,…'], ['101,Asha,Engg,…', '102,Ravi,Sales,…', '103,Meena,Engg,…'],
        ['Engineering', 'Sales', 'Engineering', 'HR', 'Sales', 'Engineering'], ['Engineering ×3', 'HR', 'Sales ×2'], ['3 Engineering', '1 HR', '2 Sales'], ['3 Engineering', '2 Sales', '1 HR']]
def stage(k, note, tone):
    o = ''.join(label_box(4 + i * 59, 10, 55, 26, [s], ('blue' if i == k else ('green' if i < k else 'card')), 6.6) for i, s in enumerate(STAGES))
    o += label_box(40, 48, 280, 92, ['output of “%s”' % STAGES[k]] + DATA[k][:5], 'card', 7.8)
    return o + t(180, 160, note, 8.6, tone, bold=True)
frames = [stage(0, 'The CSV with its header.', 'violet'), stage(1, 'tail -n +2 drops the header.', 'blue'), stage(2, 'cut keeps column 3: departments.', 'blue'),
          stage(3, 'sort puts equal departments together.', 'green'), stage(4, 'uniq -c counts each group.', 'amber'), stage(5, 'sort -rn: biggest first.', 'green')]
s1 = anim_one('Animated pipeline', 'Headcount per department',
              'Watch employees.csv turn into a report, one stage at a time. The real output is in part 4.',
              'tail | cut | sort | uniq -c | sort -rn', 'Six stage boxes; below them the current output changes from CSV rows to departments, grouped, counted and ranked.', frames,
              ['Start with the file.', 'Remove the header row.', 'Keep only the department.', 'Group equal values.', 'Count each group.', 'Rank by count.'], hid='scenario-pipeline')

def uq(sorted_, note, tone):
    items = ['apple', 'apple', 'banana', 'banana', 'banana', 'cherry', 'apple', 'apple']
    if sorted_:
        items = sorted(items)
    o = ''.join(label_box(14, 8 + i * 17, 100, 15, [x], ('amber' if x == 'apple' else 'card'), 7.4) for i, x in enumerate(items))
    res = ['2 apple', '3 banana', '1 cherry', '2 apple'] if not sorted_ else ['4 apple', '3 banana', '1 cherry']
    o += label_box(180, 30, 160, 90, ['uniq -c'] + res, 'green' if sorted_ else 'red', 8.2) + arrow(118, 75, 176, 75)
    return o + t(180, 160, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ uniq -c fruits.txt', ('      2 apple', 'out'), ('      3 banana', 'out'), ('      1 cherry', 'out'), ('      2 apple', 'err')], title='riya@laptop', size=8) + cap('Without sort: apple counted twice, separately.', '', 'red', y=150, h=34),
       term(14, 16, 332, 116, ['$ sort fruits.txt | uniq -c', ('      4 apple', 'acc'), ('      3 banana', 'acc'), ('      1 cherry', 'acc')], title='riya@laptop', size=8) + cap('With sort: one group per fruit.', '', 'green', y=150, h=34)]
behind = [uq(False, 'uniq compares each line only with the one before it.', 'red'), uq(True, 'After sort, equal lines are neighbours.', 'green')]
two = anim_two('Why uniq needs sort', 'uniq looks only at neighbours',
               'Two terminals: uniq -c without sort counts apple twice in two groups; after sort apple is counted 4 times.',
               'Eight fruit boxes in file order and in sorted order, with the uniq -c result beside them.', see, behind,
               ['Two runs of apple → two separate counts.', 'Sorted first → the correct count, 4.'],
               ['Neighbours only: the last two apples start a new group.', 'sort makes every apple a neighbour of the others.'])

dx = dissect('Layer by layer: sort -t, -k5,5nr employees.csv',
    'How sort decides the order. Each layer has a real command and output from our build machine.', [
    dict(key='split', name='Split into fields', sub='-t,',
         why='Find the column to compare.',
         how='Each line is split at every comma.',
         impl='Fields numbered from 1.', used='CSV, /etc/passwd.',
         setup=EMP, cmd="sed -n 2p employees.csv | tr ',' '\\n' | cat -n"),
    dict(key='key', name='Pick the key', sub='-k5,5',
         why='Compare only the salary.',
         how='From the start of field 5 to the end of field 5.',
         impl='Without ,5 the key runs to the line end.', used='Reports.',
         setup=EMP, cmd="tail -n +2 employees.csv | cut -d, -f5 | head -3"),
    dict(key='cmp', name='Compare as numbers', sub='n',
         why='98000 &gt; 85000, but “98000” vs “100000” as text is wrong.',
         how='Parse leading digits as a number.',
         impl='Locale decides the decimal point.', used='Money, counts.',
         cmd="printf '98000\\n100000\\n' | sort | head -1; printf '98000\\n100000\\n' | sort -n | head -1"),
    dict(key='rev', name='Reverse', sub='r',
         why='Biggest first.',
         how='The comparison result is negated.',
         impl='Applies to this key only.', used='Top N.',
         setup=EMP, cmd="tail -n +2 employees.csv | sort -t, -k5,5nr | head -1"),
    dict(key='tie', name='Ties', sub='last resort or -s',
         why='Equal keys still need an order.',
         how='Whole-line comparison, unless -s keeps input order.',
         impl='GNU sort default.', used='Stable reports.',
         cmd="printf 'b 1\\na 1\\n' | sort -k2,2; echo ---; printf 'b 1\\na 1\\n' | sort -s -k2,2"),
], hint='From a line of text to its place in the output. Click a layer.')

HOOD = hood('Under the hood: sort reads everything before it writes', 'Unlike grep, sort cannot print anything until it has read the last line (the last line might belong first). strace shows all reads, then the writes.',
    'sort nums.txt', setup="printf '100\\n20\\n3\\n' > nums.txt", show='openat.*nums|^read\\(3|^write\\(1', start='openat.*nums')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A column becoming a report</h2>
''' + s1 + two + dx + HOOD + qc('Why can <code>tail -f app.log | sort</code> never show anything?', 'sort must read all input before writing, and tail -f never ends. Use grep or awk for live streams.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>The six tools at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ cut|sort|', 'prompt'), ('uniq -c', 'acc')], title='data', size=6.4, step=12),
              '1. Data profiling', 'Before loading a file, data engineers count rows, distinct values and top categories with these tools.', ['CSV', '*cut sort uniq', 'profile']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['du -sh *', '| sort -rh'], 'blue', 8.6), '2. Disk clean-up',
    'Admins find the biggest folders with du | sort -rh | head when a disk fills up.', ['Disk full', '*sort -h', 'culprit']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['uniq -c', 'top IPs'], 'red', 8.6), '3. Security and traffic',
    'Top IPs, top URLs, top user agents: the frequency pipeline on access logs.', ['Log', '*uniq -c', 'top N']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ["tr -d '\\r'", 'clean'], 'green', 8.6), '4. Data cleaning',
    'Windows line endings, odd characters, repeated spaces: tr cleans files from other systems.', ['File', '*tr', 'clean file']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['paste -sd+', '| bc'], 'violet', 8.6), '5. Quick totals',
    'Sum a column or build a list for a config without opening a spreadsheet.', ['Column', '*paste', 'total']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Sorted, no duplicates', scenario='A clean word list (from your notes).',
         cmd="printf 'kiwi\\napple\\nkiwi\\nmango\\n' | sort -u", explain='sort -u = sort | uniq.'),
    dict(level='b', title='Shells in use', scenario='How many users use each shell?',
         cmd="cut -d: -f7 /etc/passwd | sort | uniq -c | sort -rn | head -3", explain='Field 7 of /etc/passwd.'),
    dict(level='i', title='Average salary', scenario='Total ÷ count.', setup=EMP,
         cmd="t=$(tail -n +2 employees.csv | cut -d, -f5 | paste -sd+ | bc); n=$(tail -n +2 employees.csv | wc -l); echo \"avg: $((t / n))\"", explain='paste + bc for the sum, wc for the count.'),
    dict(level='i', title='Top status codes', scenario='Which HTTP codes does the site return most?', setup=ACCESS,
         cmd="cut -d' ' -f9 access.log | sort | uniq -c | sort -rn", explain='Field 9 when splitting by single spaces.'),
    dict(level='a', title='Duplicate rows by key', scenario='Which IDs appear more than once in an import file?',
         cmd="printf '101,a\\n102,b\\n101,c\\n103,d\\n102,e\\n' > imp.csv; cut -d, -f1 imp.csv | sort | uniq -d", explain='-d lists repeated keys.'),
], extra=build_up('the HR report', 'Riya answers the HR head one question at a time.', EMP, [
    ("tail -n +2 employees.csv | cut -d, -f3 | sort | uniq -c | sort -rn", '1. People per department.'),
    ("tail -n +2 employees.csv | sort -t, -k5,5nr | head -3 | cut -d, -f2,5", '2. The three highest salaries.'),
    ("tail -n +2 employees.csv | cut -d, -f5 | paste -sd+ | bc", '3. Total salary bill.'),
    ("tail -n +2 employees.csv | cut -d, -f4 | sort -u | tr '[:lower:]' '[:upper:]' | paste -sd,", '4. The cities, in capitals, on one line.'),
])) + which('Choosing the right tool.', [
    ('A column', 'cut -d -f', 'Fast, simple.', 'cut on quoted CSV.'),
    ('Columns with logic', 'awk (6.5)', 'Conditions, sums.', 'Long cut | sed chains.'),
    ('Order numbers', 'sort -n / -h / -V', 'Correct.', 'Plain sort.'),
    ('By a column', 'sort -t, -kN,N', 'Exact key.', '-kN without ,N.'),
    ('Unique', 'sort -u', 'One step.', 'uniq without sort.'),
    ('Counts', 'sort | uniq -c | sort -rn', 'Frequency table.', 'Counting by eye.'),
    ('Characters', 'tr', 'Per character.', 'tr for words (use sed).'),
    ('Totals', 'paste -sd+ | bc', 'One line.', 'A loop.'),
]) + keys('Shortcuts and handy forms.', [
    ('LC_ALL=C sort', 'byte order, faster', 'LC_ALL=C sort big.txt'),
    ('sort -o f f', 'sort a file in place safely', 'sort -o names.txt names.txt'),
    ('sort -S 1G --parallel=4', 'more memory and cores', 'huge files'),
    ('tail -n +2', 'skip a header line', 'tail -n +2 data.csv'),
    ('cat -A', 'see tabs (^I) and CRs (^M)', 'before choosing a delimiter'),
    ("column -t -s,", 'show CSV as a neat table', 'column -t -s, employees.csv'),
]) + scriptit('hr-report.sh', 'The 5 pm report as a script: headcount, top 3, total and average, written to a dated file.',
EMP + '''
f=employees.csv; out="hr_$(date -d 2026-11-06 +%F).txt"
{
  echo "== Headcount by department"; tail -n +2 "$f" | cut -d, -f3 | sort | uniq -c | sort -rn
  echo "== Top 3 salaries";          tail -n +2 "$f" | sort -t, -k5,5nr | head -3 | cut -d, -f2,5
  total=$(tail -n +2 "$f" | cut -d, -f5 | paste -sd+ | bc); n=$(tail -n +2 "$f" | wc -l)
  echo "== Total $total, average $((total / n)) for $n employees"
} > "$out"
cat "$out"''',
'<p>The heredoc at the top only creates the sample CSV. Point <code>f=</code> at a real export to use it.</p>') + puzzle_answer('Plain <code>sort</code> gives <b>100 1000 20 3 5</b>: it compares text, and “1” comes before “2”. <code>sort -n</code> gives 3 5 20 100 1000. For the fruits, <code>sort | uniq -c</code> prints <b>4 apple</b>: sort brings all four apples together. Without sort, uniq -c would print “2 apple” twice, because uniq only compares neighbours. (Some notes show “3 apple” here; real runs give 4.)') + qc('How do you show employees sorted by city, and within a city by name?', '<code>tail -n +2 employees.csv | sort -t, -k4,4 -k2,2</code>') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-grep-searching-inside-files/">Lesson 6.1</a> (grep) and <a href="../../05-redirection-and-pipes/03-pipes-and-tee-building-command-pipelines/">5.3</a> (pipes).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
