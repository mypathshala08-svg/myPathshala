import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, '..'))
from linuxkit import *
from _data import APPLOG, ACCESS, EMP

HOOK = hook('The CFO wants, by tonight: the average salary per department, only for staff in Pune or Mumbai, as a neat report with a header and a total. cut can take columns, sort can order them, but none of them can <b>compare</b> a value or <b>add</b> numbers per group. awk can: <code>awk -F, \'$4=="Pune" || $4=="Mumbai" {s[$3]+=$5; n[$3]++} END {for (d in s) print d, s[d]/n[d]}\' employees.csv</code>. awk is a small programming language built for columns.',
    ['print and reorder columns with <code>awk \'{print $2, $5}\'</code>, using any separator (<code>-F,</code> <code>-F:</code>) and the built-in variables <code>NR NF $0 $NF FS OFS</code>',
     'select lines with patterns and conditions: <code>/ERROR/</code>, <code>$5 &gt; 70000</code>, <code>NR &gt; 1</code>, <code>&amp;&amp; ||</code>, ranges',
     'calculate totals, averages, counts and per-group sums with variables, arrays and <code>BEGIN</code>/<code>END</code>',
     'format reports with <code>printf</code>, and use string functions (<code>length</code>, <code>substr</code>, <code>toupper</code>, <code>gsub</code>, <code>split</code>)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the CFO’s report'),
    ('decide', 'Which awk form when?', 2, 'the quick chart'),
    ('definition', 'What awk is', 5, 'simple meaning + 4 depths'),
    ('commands', 'awk, by field', 18, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'fields and the awk cycle'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which awk form? (decide in 5 seconds)', [
    ('Print some columns (space-separated)', "awk '{print $1, $3}' f", 'any number of spaces'),
    ('Columns of a CSV / passwd', "awk -F, '{print $2}'  ·  awk -F:", '-F sets the separator'),
    ('Lines matching a pattern', "awk '/ERROR/' f", 'like grep'),
    ('Rows where a column meets a condition', "awk -F, '$5 > 70000' f", '== != < > ~ !~'),
    ('Skip the header', "awk 'NR > 1' f", 'NR = line number'),
    ('Total / average of a column', "awk '{s+=$5} END {print s, s/NR}'", 'END runs after the last line'),
    ('Sum or count per group', "awk '{s[$3]+=$5} END {for (k in s) print k, s[k]}'", 'arrays'),
    ('Last column', "awk '{print $NF}'", 'NF = number of fields'),
    ('Neat aligned report', "awk '{printf \"%-10s %8.2f\\n\", $1, $2}'", 'printf'),
    ('Remove duplicates, keep order', "awk '!seen[$0]++'", 'a famous one-liner'),
])

cmap = concept_map(
    [('6.2', 'cut, sort, uniq', 'columns without logic'), ('6.4', 'sed', 'edit text line by line'), ('6.1', 'grep', 'patterns')],
    ['the awk cycle: pattern { action } for every line', 'fields $1…$NF, -F, OFS; NR, NF, FNR, FILENAME', 'conditions, BEGIN and END', 'variables, arrays and per-group totals', 'printf and string functions; awk scripts (-f)'],
    [('6.6', 'Regular expressions', 'the patterns inside /…/'), ('13.3', 'Log analysis', 'awk on real logs'), ('13.5', 'Data one-liners', 'CSV reports'), ('12.5', 'Shell scripts', 'awk inside scripts')],
    'awk is where the command line becomes a spreadsheet: columns, conditions, sums and reports in one line. Most “I need a quick report” tasks end up as an awk command.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ["$ awk -F, 'NR>1 {s[$3]+=$5; n[$3]++}", "    END {for (d in s)", "    printf \"%-12s %6d\\n\", d, s[d]/n[d]}'", '    employees.csv | sort', ('Engineering   85000', 'acc'), ('HR            47000', 'acc'), ('Sales         56500', 'acc')], title='riya@finance: ~', size=7.0, step=15)
      + t(352, 36, 'awk = columns + logic:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• $1 $2 … $NF fields', '• -F, separator', '• $5 > 70000 conditions', '• s[$3]+=$5 group sums', '• END {…} the report'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The CFO’s report</h2>
  <div class="story">
''' + puzzle('A note says <code>awk \'{print $1}\' /etc/passwd | head -5</code> prints the first five user names. Riya runs it and sees whole lines like <code>root:x:0:0:root:/root:/bin/bash</code>. Why, and what is the one-character fix?') + '''
    <p class="narration">Finance needs the average salary per department before the board meeting. Riya has employees.csv and a terminal.</p>
''' + scene('A terminal: an awk command with arrays and printf prints the average salary for Engineering 85000, HR 47000 and Sales 56500.', sc,
            'awk reads every line, splits it into <tspan font-weight="700" class="s-acc">fields</tspan>, and lets you calculate.') + '''
A> awk splits each line into fields: <code>$1</code>, <code>$2</code>… With <code>-F,</code> the comma is the separator. Then you write: “when this condition is true, do this”.
R> And the average per department?
K> Keep two arrays: the sum per department and the count. At the <code>END</code>, divide. That is a GROUP BY in one line.
A> Today: fields, patterns, BEGIN and END, variables, arrays, printf and string functions, each explained, then used by admins, data engineers, DBAs, developers, DevOps, security and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A school register with columns roll, name, class, marks; a teacher with a calculator reads it row by row, ticks rows that match a condition, adds marks per class and writes a summary at the end.">'
       + label_box(14, 20, 260, 130, ['register (the file)', '$1 roll  $2 name  $3 class  $4 marks', '1  Asha   10A  91', '2  Ravi   10B  78', '3  Meena  10A  85'], 'card', 8.4)
       + label_box(320, 20, 140, 60, ['teacher', 'reads row by row'], 'amber', 8.6)
       + label_box(320, 90, 140, 60, ['calculator', 'total per class'], 'blue', 8.6)
       + label_box(490, 50, 136, 70, ['END: summary', '10A avg 88', '10B avg 78'], 'green', 8.4)
       + arrow(276, 60, 316, 50) + arrow(462, 85, 486, 85)
       + t(320, 182, 'awk = a teacher with a calculator going through a register.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('awk at four depths', [
    ('v', 'No jargon: a register and a calculator', '      <p>Think of a teacher with a class register.</p>' + pic + '''
      <ul>
        <li>The register has columns: roll, name, class, marks. awk calls them <code>$1 $2 $3 $4</code>.</li>
        <li>The teacher reads every row, ticks the ones that match (“marks above 80”), and adds up marks per class.</li>
        <li>At the end (<code>END</code>) she writes the summary.</li>
      </ul>'''),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>awk '{print $1}' file</code>: first column (separated by spaces or tabs).</li>
        <li><code>awk -F: '{print $1}' /etc/passwd</code>: user names (separator :).</li>
        <li><code>awk '/ERROR/' app.log</code>: lines containing ERROR.</li>
        <li><code>awk -F, '$5 &gt; 70000' employees.csv</code>: rows where column 5 is above 70000.</li>
        <li><code>awk '{s += $2} END {print s}' f</code>: the total of column 2.</li>
      </ul>'''),
    ('i', 'Patterns, actions, variables', '''      <ul>
        <li>A program is <code>pattern { action }</code> pairs. No pattern = every line; no action = print the line.</li>
        <li>Built-ins: <code>NR</code> line number, <code>NF</code> number of fields, <code>$NF</code> last field, <code>$0</code> whole line, <code>FS</code>/<code>OFS</code> input/output separator, <code>FILENAME</code>, <code>FNR</code> line number in the current file.</li>
        <li>Conditions: <code>== != &lt; &gt; &lt;= &gt;=</code>, <code>~ /re/</code> (matches), <code>!~</code>, <code>&amp;&amp; || !</code>; ranges <code>/start/,/end/</code>.</li>
        <li>Variables need no declaration and start as 0 or "". Arrays are associative: <code>count[$3]++</code> uses the department name as the index.</li>
        <li><code>BEGIN { }</code> runs before the first line (headers, FS), <code>END { }</code> after the last (totals).</li>
      </ul>'''),
    ('a', 'Behind the screen: one awk, several implementations', '''      <ul>
        <li>awk = Aho, Weinberger, Kernighan (Bell Labs, 1977). Today there are several: <b>mawk</b> (Ubuntu’s default <code>awk</code>, very fast), <b>gawk</b> (GNU, more functions: <code>strftime</code> on all versions, <code>asort</code>, <code>-i inplace</code>, networking), and BWK “one true awk” on macOS.</li>
        <li><code>for (k in arr)</code> visits keys in an <b>unspecified order</b>; pipe to <code>sort</code> or use gawk’s <code>PROCINFO["sorted_in"]</code>.</li>
        <li>Numbers are floating point (double): sums of money are fine for reports, but round with printf (<code>%.2f</code>).</li>
        <li>Assigning to a field (<code>$3 = "X"</code>) rebuilds <code>$0</code> with <code>OFS</code>; assigning <code>$1 = $1</code> is the trick to change separators.</li>
        <li><code>NR==FNR</code> is true only while reading the first file: the classic way to join two files in awk.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>awk: fields, patterns and reports</h2>
''' + def_block(
    '<code>awk</code> is a pattern-scanning and text-processing language. It reads input line by line (records), splits each line into fields (<code>$1</code>, <code>$2</code>, …) using a field separator, and for every rule <code>pattern { action }</code> whose pattern is true, runs the action. It has variables, associative arrays, arithmetic, string functions, <code>printf</code>, and special <code>BEGIN</code> and <code>END</code> blocks.',
    'For every line: if this, then do that, and at the end print the summary.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Record / field', 'A line / a column in that line.'),
    ('FS / OFS', 'Input field separator (-F) / output field separator.'),
    ('NR / NF', 'Record (line) number / number of fields.'),
    ('Pattern', 'A condition or /regex/ that selects lines.'),
    ('Action', 'Code in { } run for selected lines.'),
    ('Associative array', 'arr["Pune"]: indexed by text, not numbers.'),
    ('awk', f'{gl("awk", "Glossary →")}'),
    ('Field and delimiter', f'{gl("field-and-delimiter", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('awk', 'Aho · Weinberger · Kernighan', 'The surnames of its three authors (Bell Labs, 1977).'),
    ('gawk', 'GNU awk', 'The richest version.'),
    ('mawk', 'Mike Brennan’s awk', 'Fast; Ubuntu’s default awk.'),
    ('NR / NF', 'number of records / fields', ''),
    ('FS / OFS', '(output) field separator', ''),
    ('BEGIN / END', 'before / after all input', ''),
    ('printf', 'print formatted', 'Same as C and bash printf.'),
    ('$0', 'the whole record', 'Field zero.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Columns', "<code>awk '{print $1, $3}'</code>"),
    ('CSV', "<code>awk -F, '{print $2}'</code>"),
    ('Condition', "<code>awk -F, '$5 &gt; 70000'</code>"),
    ('Total', "<code>awk '{s+=$2} END{print s}'</code>"),
    ('Per group', "<code>awk '{s[$1]+=$2} END{for(k in s) print k, s[k]}'</code>"),
    ('Dedupe in order', "<code>awk '!seen[$0]++'</code>"),
]) + '\n' + lv + didyou('The “K” in awk is Brian Kernighan, co-author of “The C Programming Language”. awk’s syntax looks like C on purpose, and its creators wrote “The AWK Programming Language” (1988; a second edition appeared in 2023, when awk gained CSV support with <code>--csv</code>).') + '''
EXAM> “Print the user names and UIDs of all users with UID ≥ 1000.” → awk -F: '$3 &gt;= 1000 &amp;&amp; $3 &lt; 65534 {print $1, $3}' /etc/passwd (explain -F, the condition, and why 65534 (nobody) is excluded).
''' + qc('What does <code>awk \'{print $NF}\'</code> print?', 'The last field of each line, whatever the number of fields: NF is the count, so $NF is the last one.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Patterns and built-in variables</h2>
''' + table(['Pattern', 'Selects', 'Example'], [
    ['(none)', 'every line', "<code>awk '{print $1}'</code>"],
    ['<code>/re/</code>', 'lines matching the regex', "<code>awk '/ERROR|FATAL/'</code>"],
    ['<code>$3 == "HR"</code>', 'a field equals a value', "<code>awk -F, '$3==\"HR\"'</code>"],
    ['<code>$5 &gt; 70000</code>', 'numeric comparison', "<code>awk -F, '$5&gt;70000'</code>"],
    ['<code>$4 ~ /^P/</code>', 'a field matches a regex', 'cities starting with P'],
    ['<code>NR &gt; 1</code> / <code>NR==5</code>', 'by line number', 'skip header / one line'],
    ['<code>A &amp;&amp; B</code>, <code>A || B</code>, <code>!A</code>', 'combined conditions', '$4=="Pune" || $4=="Mumbai"'],
    ['<code>/start/,/end/</code>', 'a range of lines', 'log sections'],
    ['<code>BEGIN</code> / <code>END</code>', 'before / after all input', 'headers / totals'],
], minw=560) + table(['Variable', 'Meaning', 'Example'], [
    ['<code>$0</code>, <code>$1</code>…<code>$NF</code>', 'whole line, fields, last field', "<code>print $NF</code>"],
    ['<code>NR</code> / <code>FNR</code>', 'line number overall / in this file', "<code>NR&gt;1</code>"],
    ['<code>NF</code>', 'number of fields on this line', "<code>NF != 5</code> = bad rows"],
    ['<code>FS</code> / <code>-F</code>', 'input separator (space by default: any run of blanks)', "<code>-F,</code> <code>-F:</code> <code>-F'\\t'</code>"],
    ['<code>OFS</code>', 'output separator for print a, b', "<code>-v OFS=,</code>"],
    ['<code>FILENAME</code>', 'current file', 'multi-file reports'],
    ['<code>-v name=value</code>', 'pass a shell value into awk', "<code>-v min=$limit</code>"],
], minw=560) + qc('Which awk pattern finds rows of a CSV that do not have exactly 5 columns?', "<code>awk -F, 'NF != 5' file</code>") + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>awk explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04, where <code>awk</code> is <b>mawk 1.3.4</b> (gawk is a separate package). The examples use features that work in both. Sample files: <code>employees.csv</code>, <code>app.log</code>, <code>access.log</code>.</p>
''' + cmdcard_u(['printing, reordering or reformatting columns', 'columns separated by a varying number of spaces (ps, ls -l, df, logs)', 'quick filters by a column value'],
               ['quoted CSV with commas inside fields (use gawk --csv, Python or csvkit)', 'simple fixed replacements (sed is shorter)'])(
    'awkprint', "awk '{print}'", 'fields and print',
    'Splits each line into fields and prints the ones you choose. The default separator is any run of spaces or tabs; <code>-F</code> sets another. A comma in <code>print $1, $2</code> inserts OFS (a space by default).',
    "awk [-F SEP] [-v OFS=SEP] '{print $N, …}' FILE", 'safe',
    [("'{print $1}'", 'first field', 'one column'),
     ("'{print $2, $1}'", 'reorder', 'swap columns'),
     ("'{print $NF}'", 'last field', 'any width'),
     ('-F, / -F: / -F\'\\t\'', 'CSV / passwd / TSV', 'separators'),
     ('-v OFS=,', 'output separator', 'make CSV'),
     ("'{print NR\": \"$0}'", 'number lines', 'like cat -n'),
     ("'{$1=$1}1' OFS=,", 'rebuild lines with OFS', 'spaces → commas')],
    dict(setup=EMP, cmd="awk -F, '{print $2, $5}' employees.csv | head -3\nawk -F, -v OFS=' | ' 'NR>1 {print $2, toupper($4)}' employees.csv | head -2\necho 'a   b    c' | awk '{print $NF, NF}'", note='With -F, the comma splits the fields. Without -F, any number of spaces counts as one separator.'),
    [('sys', [
        dict(situation='User names (the puzzle): /etc/passwd uses :, so tell awk.', cmd="awk '{print $1}' /etc/passwd | head -2\necho ---\nawk -F: '{print $1}' /etc/passwd | head -2",
             why='Without -F: the line has no spaces, so $1 is the whole line. -F: makes $1 the user name.'),
        dict(situation='Disk usage percentages from df (columns padded with spaces).', setup="printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\\n/dev/sda1 51475068 33458796 15378832 69%% /\\n/dev/sdb1 524288000 497025024 27262976 95%% /data\\ntmpfs 4013348 0 4013348 0%% /dev/shm\\n' > df.txt", cmd="awk 'NR>1 {print $6, $5}' df.txt",
             why='df.txt is saved <code>df -P</code> output (a real server would show its own disks). awk ignores how many spaces separate columns, so df, ps and ls -l output are easy to read.')]),
     ('web', [
        dict(situation='IP and status code from an access log.', setup=ACCESS, cmd="awk '{print $1, $9}' access.log | head -3",
             why='The common log format splits on spaces: $1 IP, $7 URL, $9 status, $10 bytes.')]),
     ('data', [
        dict(situation='Turn a space-separated file into CSV.', cmd="printf 'Asha 91 Pune\\nRavi 78 Agra\\n' | awk -v OFS=, '{$1=$1} 1'",
             why='$1=$1 forces awk to rebuild the line with OFS; the lone 1 is a true pattern that prints it.')]),
    ],
    anat=anatomy([('awk', 'cmd', 'command'), ('-F,', 'opt', 'field separator'), ("'NR>1 {print $2, $5}'", 'arg', 'pattern { action }'), ('employees.csv', 'arg', 'file')], 'Always single-quote the program: $1 must reach awk, not be expanded by the shell.')
) + mistake("awk '{print $1}' /etc/passwd | head -5   (“first field: usernames”)", "awk -F: '{print $1}' /etc/passwd | head -5",
            'The default separator is white space. /etc/passwd separates fields with :, so without -F: the whole line is field 1 (real run). That is the answer to the puzzle.') + cmdcard_u(['rows that meet a condition on a column', 'filtering logs by level, status or time', 'data quality checks (wrong number of fields)'],
               ['simple text search in a whole line (grep is simpler)'])(
    'awkpat', "awk 'pattern'", 'conditions',
    'A pattern without an action prints the matching lines. Patterns can be regexes, comparisons on fields, line numbers, ranges, and combinations.',
    "awk 'PATTERN' FILE   ·   awk 'PATTERN {ACTION}' FILE", 'safe',
    [("'/ERROR/'", 'regex on the whole line', 'like grep'),
     ("'$3==\"HR\"'", 'field equals text', 'exact column'),
     ("'$5>70000'", 'numeric compare', 'thresholds'),
     ("'$4 ~ /^P/'", 'field matches regex', 'starts with P'),
     ("'NR>1'", 'skip header', 'CSV'),
     ("'A && B' / 'A || B'", 'combine', 'several rules'),
     ("'/start/,/end/'", 'range of lines', 'sections'),
     ("'NF != 5'", 'wrong column count', 'bad rows')],
    dict(setup=EMP, cmd="awk -F, 'NR>1 && $5>70000 {print $2, $5}' employees.csv\nawk -F, '$4==\"Pune\" || $4==\"Mumbai\" {print $2, $4}' employees.csv", note='Conditions read like English: line number above 1 and salary above 70000.'),
    [('sys', [
        dict(situation='Real users only (UID 1000 to 65533).', cmd="awk -F: '$3>=1000 && $3<65534 {print $1, $3}' /etc/passwd | head -3",
             why='65534 is the special user nobody; system accounts are below 1000.'),
        dict(situation='Filesystems more than 50% full.', setup="printf 'Filesystem 1024-blocks Used Available Capacity Mounted on\\n/dev/sda1 51475068 33458796 15378832 69%% /\\n/dev/sdb1 524288000 497025024 27262976 95%% /data\\ntmpfs 4013348 0 4013348 0%% /dev/shm\\n' > df.txt", cmd="awk 'NR>1 && $5+0 > 50 {print $6, $5}' df.txt",
             why='$5 is like “63%”; $5+0 turns it into the number 63 for the comparison.')]),
     ('devops', [
        dict(situation='Problem lines in the log, any case (from your notes).', setup=APPLOG, cmd="awk 'tolower($0) ~ /error|fatal/ {print NR\": \"$4, $5, $6}' app.log",
             why='tolower makes the match case-insensitive in every awk (gawk also has IGNORECASE).')]),
     ('qa', [
        dict(situation='Find rows with the wrong number of columns before loading.', cmd="printf 'a,b,c\\nd,e\\nf,g,h\\ni,j,k,l\\n' > in.csv\nawk -F, 'NF != 3 {print \"line \" NR \": \" NF \" fields\"}' in.csv",
             why='A fast data-quality gate: broken rows are reported with their line numbers.')]),
     ('sec', [
        dict(situation='Requests with status 401 to /admin.', setup=ACCESS, cmd="awk '$7 == \"/admin\" && $9 == 401 {print $1}' access.log | sort | uniq -c",
             why='Two exact field conditions: more precise than grep on the whole line.')]),
    ]
) + cmdcard_u(['totals, averages, counts, minimum and maximum', 'GROUP BY style summaries per key', 'reports with headers and footers'],
               ['very large group-bys or joins on huge data (use a database or Spark)'])(
    'awkcalc', "awk '… END {}'", 'calculate and summarise',
    'Variables keep values across lines; arrays group by a key. <code>BEGIN</code> runs before reading (headers, settings), <code>END</code> after the last line (totals, averages).',
    "awk 'BEGIN {…} PATTERN {sum += $N; arr[$K] += $N} END {…}' FILE", 'safe',
    [("'{s+=$5} END {print s}'", 'total', 'sum a column'),
     ("END {print s/NR}", 'average', 'mean'),
     ("'{c++} END {print c}'", 'count lines', 'like wc -l'),
     ("'$5>m {m=$5} END {print m}'", 'maximum', 'highest value'),
     ("'{s[$3]+=$5}'", 'sum per group', 'GROUP BY'),
     ("for (k in s) print k, s[k]", 'loop over an array', 'report rows'),
     ("'!seen[$0]++'", 'first occurrence only', 'dedupe in order')],
    dict(setup=EMP, cmd="awk -F, 'NR>1 {t+=$5} END {print \"total\", t, \"avg\", t/(NR-1)}' employees.csv\nawk -F, 'NR>1 {c[$3]++} END {for (d in c) print d, c[d]}' employees.csv | sort", note='NR-1 because the header is line 1. for (d in c) visits keys in no fixed order, so the output is piped to sort.'),
    [('data', [
        dict(situation='Average salary per department (the story).', setup=EMP, cmd="awk -F, 'NR>1 {s[$3]+=$5; n[$3]++} END {for (d in s) printf \"%-12s %8.0f\\n\", d, s[d]/n[d]}' employees.csv | sort",
             why='Two arrays (sum and count) per department; divide at the end. That is SQL’s AVG … GROUP BY.')]),
     ('sys', [
        dict(situation='Total size of .log files (from your notes).', cmd="seq 1 1000 > a.log; seq 1 500 > b.log\nls -l *.log | awk '{sum += $5} END {print sum, \"bytes\"}'",
             why='Column 5 of ls -l is the size. For scripts, du -cb *.log | tail -1 avoids parsing ls.')]),
     ('web', [
        dict(situation='Bytes served per status code.', setup=ACCESS, cmd="awk '{b[$9]+=$10} END {for (s in b) print s, b[s]}' access.log | sort",
             why='Group by $9, sum $10.')]),
     ('dba', [
        dict(situation='Slowest queries from a query log (time in column 2).', cmd="printf 'q1 120\\nq2 2400\\nq3 35\\nq4 980\\n' > slow.log\nawk '$2 > m {m=$2; q=$1} END {print \"slowest:\", q, m \" ms\"}' slow.log",
             why='Keep the maximum and its query name while reading.')]),
     ('ml', [
        dict(situation='Mean and standard deviation of a numeric column.', cmd="printf '4\\n8\\n6\\n5\\n7\\n' > x.txt\nawk '{s+=$1; ss+=$1*$1} END {m=s/NR; printf \"mean %.2f sd %.2f\\n\", m, sqrt(ss/NR - m*m)}' x.txt",
             why='Quick statistics on a column before reaching for Python (population standard deviation).')]),
    ]
) + cmdcard_u(['aligned reports for people', 'changing text inside a column', 'combining files on a key (NR==FNR)'],
               ['very long programs on one line: put them in a file (awk -f report.awk)'])(
    'awkfmt', "awk printf · functions", 'formatting and string functions',
    '<code>printf</code> prints with a format (<code>%s</code> text, <code>%d</code> integer, <code>%.2f</code> decimals, <code>%-10s</code> left-aligned width 10, no automatic newline). String functions: <code>length</code>, <code>substr</code>, <code>index</code>, <code>toupper</code>/<code>tolower</code>, <code>sub</code>/<code>gsub</code>, <code>split</code>, <code>sprintf</code>.',
    "awk '{printf \"%-10s %8.2f\\n\", $1, $2}'   ·   awk '{gsub(/a/, \"b\"); print}'", 'safe',
    [('%s %d %.2f', 'text, integer, 2 decimals', 'money'),
     ('%-12s / %8d', 'left / right aligned widths', 'tables'),
     ('length($2)', 'length of a field', 'validation'),
     ('substr($2,1,3)', 'part of a string', 'codes, initials'),
     ('toupper / tolower', 'case', 'normalise'),
     ('sub / gsub(/re/, "x")', 'replace first / all in $0 or a field', 'clean values'),
     ('split($4, a, "-")', 'split a field into an array', 'dates'),
     ('NR==FNR {…; next}', 'first file vs second file', 'joins')],
    dict(setup=EMP, cmd="awk -F, 'NR==1 {printf \"%-8s %-12s %8s\\n\", \"NAME\", \"DEPT\", \"SALARY\"; next} {printf \"%-8s %-12s %8.2f\\n\", $2, $3, $5}' employees.csv | head -4", note='The header line is formatted with the same widths as the data, so the columns line up.'),
    [('data', [
        dict(situation='Clean a column: remove ₹ and commas from amounts, then add them.', cmd="printf 'a,\"₹1,250\"\\nb,\"₹980\"\\n' > amt.csv\nawk -F'\"' '{gsub(/[^0-9]/, \"\", $2); s+=$2} END {print s}' amt.csv",
             why='Splitting on the quote character keeps the amount (with its comma) in field 2; gsub keeps only the digits.')]),
     ('dev', [
        dict(situation='Join two files on an ID, all in awk.', cmd="printf '1,Asha\\n2,Ravi\\n' > names.csv; printf '1,Pune\\n3,Goa\\n' > city.csv\nawk -F, 'NR==FNR {n[$1]=$2; next} ($1 in n) {print $1, n[$1], $2}' names.csv city.csv",
             why='While reading the first file (NR==FNR) store names; for the second file print matches. No sorting needed, unlike join.')]),
     ('devops', [
        dict(situation='Split a date field into parts.', setup=APPLOG, cmd="awk 'NR==1 {split($1, d, \"-\"); print \"day\", d[3], \"month\", d[2], \"year\", d[1]}' app.log",
             why='split fills an array; the return value is the number of parts.')]),
    ]
) + undo('awk only reads and prints; mistakes are in the output, not the files.', [
    ('Wrong columns:', 'check the separator: <code>head -1 file | cat -A</code>; use -F correctly.'),
    ('Unsorted group output:', '<code>for (k in a)</code> has no order: pipe to <code>sort</code>.'),
    ('Numbers like “63%” or “1,250”:', 'convert: <code>$5+0</code>, <code>gsub(/,/, "", $2)</code>.'),
    ('Writing back to the file:', 'awk has no -i (except gawk -i inplace): write to a new file and mv it (Lesson 5.2).'),
]) + errors('awk errors students see most. Each was really produced on our build machine (mawk), with its exit status.', [
    dict(cmd="awk '{print $1' /etc/hostname", meaning='A missing closing brace: syntax error.', fix="Balance { } and quotes: <code>'{print $1}'</code>."),
    dict(cmd='echo "a b" | awk "{print $1}"', meaning='Double quotes: the shell replaced $1 with an empty string, so awk printed whole lines. No error, wrong result.', fix="Use single quotes around awk programs."),
    dict(cmd="awk -F, '{print $2}' /nope.csv", meaning='The input file does not exist.', fix='Check the path.'),
    dict(cmd="echo 5 | awk '{print $1/0}'", meaning='Not an error in mawk: it silently prints inf (gawk stops with “division by zero attempted”). Either way the report is wrong.', fix='Check the divisor: <code>n ? s/n : 0</code>.'),
]) + qc('Write an awk command that prints the names of employees whose salary is below 60000.', "<code>awk -F, 'NR&gt;1 &amp;&amp; $5 &lt; 60000 {print $2}' employees.csv</code>") + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def fields(k, note, tone):
    parts = ['101', 'Asha', 'Engineering', 'Pune', '85000']
    o = label_box(14, 10, 332, 24, ['101,Asha,Engineering,Pune,85000   ($0)'], 'card', 8)
    for i, p in enumerate(parts):
        hl = (k == 1) or (k == 2 and i in (1, 4)) or (k == 3 and i == 4)
        o += label_box(14 + i * 67, 50, 62, 40, ['$%d' % (i + 1), p], 'green' if hl else 'card', 7.6)
    out = ['', 'NF = 5', 'print $2, $5 → Asha 85000', 's += $5 → 85000'][k]
    if out:
        o += label_box(60, 104, 240, 26, [out], 'blue', 8)
    return o + t(180, 152, note, 8.6, tone, bold=True)
frames = [fields(0, 'One record: the whole line is $0.', 'violet'), fields(1, '-F, splits it into 5 fields.', 'green'),
          fields(2, 'The action uses the fields it needs.', 'blue'), fields(3, 'Variables keep values to the END.', 'amber')]
s1 = anim_one('Animated example', 'How awk sees one line',
              'One line of employees.csv, split into fields by -F,.',
              'record → fields → action', 'A CSV line, split into five boxes $1 to $5; $2 and $5 are printed; $5 is added to a running sum.', frames,
              ['The line as read.', 'Split at every comma.', 'print $2, $5 picks two fields.', 's += $5 adds to a running total.'], hid='scenario-fields')

def cyc(k, note, tone):
    boxes = ['BEGIN', 'read line', 'split fields', 'pattern?', 'action', 'END']
    o = ''.join(label_box(6 + i * 58, 20, 54, 40, [b], ('amber' if i == k else ('green' if i < k else 'card')), 7.2) for i, b in enumerate(boxes))
    return o + t(180, 100, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ["$ awk -F, 'BEGIN{print \"report\"}", "    NR>1{t+=$5} END{print t}' employees.csv", ('report', 'acc'), ('415000', 'acc')], title='riya@laptop', size=7.4)] * 6
see = [s + cap(c, '', 'card', y=150, h=34) for s, c in zip(see, ['BEGIN prints before reading.', 'Line 1 is read…', '…split into fields…', '…NR>1 is false for the header…', '…true for data: t grows.', 'END prints the total.'])]
behind = [cyc(i, n, tone) for i, (n, tone) in enumerate([('BEGIN runs once, before any input.', 'violet'), ('Read the next record.', 'blue'), ('Split it with FS.', 'blue'),
                                                         ('Test each pattern.', 'amber'), ('Run the action when true.', 'green'), ('After the last line: END.', 'violet')])]
two = anim_two('The awk program cycle', 'BEGIN, every line, END',
               'A terminal: an awk program with BEGIN, a pattern-action and END prints report then 415000.',
               'Six boxes BEGIN, read, split, pattern, action, END lighting up in turn.', see, behind,
               ['“report” appears first.', 'awk reads line 1.', 'Fields are split.', 'The header fails NR&gt;1.', 'Data lines add to t.', 'The total appears last.'],
               ['Settings and headers go in BEGIN.', 'One record at a time.', 'FS decides the fields.', 'Every rule is tested.', 'Matching rules run.', 'Totals go in END.'])

dx = dissect("Layer by layer: awk -F, 'NR>1 {s[$3]+=$5} END {…}'",
    'A GROUP BY in awk, layer by layer. Each layer has a real command and output from our build machine.', [
    dict(key='fs', name='-F,', sub='split each line',
         why='Know where columns start.',
         how='FS = “,”.',
         impl='Default FS splits on runs of blanks.', used='Every program.',
         setup=EMP, cmd="awk -F, 'NR==2 {for (i=1; i<=NF; i++) print i, $i}' employees.csv"),
    dict(key='nr', name='NR>1', sub='skip the header',
         why='The header is not data.',
         how='NR counts lines from 1.',
         impl='FNR resets per file.', used='CSV.',
         setup=EMP, cmd="awk 'NR>1' employees.csv | head -1"),
    dict(key='arr', name='s[$3]+=$5', sub='associative array',
         why='One total per department.',
         how='The department name is the index.',
         impl='A hash table.', used='GROUP BY.',
         setup=EMP, cmd="awk -F, 'NR>1 {s[$3]+=$5} END {print s[\"Engineering\"]}' employees.csv"),
    dict(key='end', name='END', sub='after all lines',
         why='Totals are only known at the end.',
         how='Loop over the array.',
         impl='Order not guaranteed.', used='Reports.',
         setup=EMP, cmd="awk -F, 'NR>1 {s[$3]+=$5} END {for (d in s) print d, s[d]}' employees.csv | sort"),
], hint='From a CSV line to a grouped total. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Fields and the awk cycle</h2>
''' + s1 + two + dx + qc('Why must totals be printed in END and not in the main block?', 'The main block runs once per line; the total is only complete after the last line, which is exactly when END runs.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>awk at work</h2>
''' + usecase(term(8, 14, 104, 62, [("$ awk '{b[$9]", 'prompt'), ('+=$10}…', 'acc')], title='web', size=6.2, step=12),
              '1. Log reports', 'Requests per IP, bytes per status, slow requests: on-call engineers write these as awk one-liners.', ['Log', '*awk arrays', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['df | awk', '$5+0>90'], 'red', 8.6), '2. Monitoring scripts',
    'Disk, memory and process checks parse command output with awk and alert on thresholds.', ['Command', '*awk test', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['AVG GROUP BY', 'in awk'], 'blue', 8.6), '3. Data summaries',
    'Analysts and data engineers summarise CSV files (sums, averages, counts per group) before loading.', ['CSV', '*awk', 'summary']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['NF != 5', 'bad rows'], 'green', 8.6), '4. Data validation',
    'Wrong column counts, empty fields and out-of-range values are caught with one awk line.', ['Import', '*awk check', 'pass / fail']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['printf', 'reports'], 'violet', 8.6), '5. Formatted reports',
    'Nightly text reports for email are often small awk programs with printf.', ['Data', '*printf', 'report']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands from your notes and practice. All really run on our build machine.', [
    dict(level='b', title='Line numbers', scenario='Number every line (from your notes).',
         cmd="printf 'a\\nb\\n' | awk '{print NR, $0}'", explain='NR is the line number.'),
    dict(level='b', title='Long lines', scenario='Lines longer than 30 characters (from your notes, 80 in real code).', setup=EMP,
         cmd="awk 'length($0) > 30 {print NR\": \"length($0)}' employees.csv", explain='length() without argument = whole line.'),
    dict(level='i', title='Most used commands', scenario='From your notes: history | awk \'{print $2}\'… (shown on a saved history).',
         cmd="printf '  1  ls\\n  2  cd x\\n  3  ls -l\\n  4  git status\\n  5  ls\\n' > h.txt; awk '{print $2}' h.txt | sort | uniq -c | sort -rn | head -2", explain='$2 because history adds a number in column 1.'),
    dict(level='i', title='Keep the first occurrence', scenario='Remove duplicates without changing the order.',
         cmd="printf 'b\\na\\nb\\nc\\na\\n' | awk '!seen[$0]++' | paste -sd,", explain='seen[$0]++ is 0 the first time, so !0 is true.'),
    dict(level='a', title='Celsius report', scenario='A function in awk (from your notes).',
         cmd="printf 'Pune 95\\nLeh 41\\n' | awk 'function c(f) {return (f-32)*5/9} {printf \"%s %.1f C\\n\", $1, c($2)}'", explain='awk has user functions.'),
], extra=build_up('the CFO report', 'Riya builds the report step by step.', EMP, [
    ("awk -F, 'NR>1 {print $3, $5}' employees.csv", '1. Department and salary.'),
    ("awk -F, 'NR>1 && ($4==\"Pune\" || $4==\"Mumbai\") {print $3, $5}' employees.csv", '2. Only Pune and Mumbai.'),
    ("awk -F, 'NR>1 && ($4==\"Pune\" || $4==\"Mumbai\") {s[$3]+=$5; n[$3]++} END {for (d in s) print d, s[d]/n[d]}' employees.csv | sort", '3. Average per department.'),
    ("awk -F, 'BEGIN {printf \"%-12s %8s\\n\", \"DEPT\", \"AVG\"} NR>1 && ($4==\"Pune\" || $4==\"Mumbai\") {s[$3]+=$5; n[$3]++; t+=$5; c++} END {for (d in s) printf \"%-12s %8.0f\\n\", d, s[d]/n[d]; printf \"%-12s %8.0f\\n\", \"ALL\", t/c}' employees.csv", '4. A formatted report with a header and an overall average.'),
])) + which('Choosing the right tool.', [
    ('One column', 'cut (single-char sep) / awk', 'cut is shortest.', 'awk for padded columns.'),
    ('Columns with spaces of any width', 'awk', 'Handles runs.', 'cut -d" ".'),
    ('Conditions on columns', 'awk', 'Readable.', 'grep tricks.'),
    ('Sums, averages, groups', 'awk', 'One pass.', 'Loops in bash.'),
    ('Replace text', 'sed', 'Shorter.', 'awk gsub for simple cases.'),
    ('Join without sorting', 'awk NR==FNR', 'Flexible.', 'join on unsorted files.'),
    ('Quoted CSV', 'gawk --csv / Python', 'Correct.', 'awk -F, on quoted data.'),
    ('Huge data', 'a database / Spark', 'Scales.', 'awk on 100 GB with big arrays.'),
]) + keys('Shortcuts and handy forms.', [
    ('-v var=$x', 'pass a shell variable in', "awk -v min=$m '$5>min'"),
    ('-f report.awk', 'program from a file', 'long programs'),
    ('next', 'skip to the next line', "NR==1 {next}"),
    ('$5+0', 'force a number', '"63%" → 63'),
    ("'1'", 'shortest “print every line”', "awk '{$1=$1}1'"),
    ('gawk -i inplace', 'edit files in place (gawk only)', 'gawk -i inplace …'),
]) + scriptit('cfo-report.awk', 'The report as an awk script file, run with <code>awk -F, -f cfo-report.awk employees.csv</code>.',
EMP + '''
cat > cfo-report.awk << 'AWK'
BEGIN { printf "%-12s %5s %10s\\n", "DEPT", "STAFF", "AVG SALARY" }
NR > 1 && ($4 == "Pune" || $4 == "Mumbai") { sum[$3] += $5; n[$3]++; total += $5; c++ }
END {
  for (d in sum) printf "%-12s %5d %10.0f\\n", d, n[d], sum[d] / n[d]
  printf "%-12s %5d %10.0f\\n", "ALL", c, total / c
}
AWK
awk -F, -f cfo-report.awk employees.csv''',
'<p>Note: the department rows come out in no fixed order (that is how awk arrays work); pipe through <code>sort</code> if you need them ordered.</p>') + puzzle_answer('awk’s default separator is white space. Lines in /etc/passwd contain no spaces (they use :), so the whole line is field 1. The fix is one option: <code>-F:</code>. Then <code>awk -F: \'{print $1}\' /etc/passwd</code> prints the user names.') + qc('How do you print the number of fields on each line of a CSV?', "<code>awk -F, '{print NF}' file</code>") + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-sort-uniq-wc-cut-paste-and-tr/">Lesson 6.2</a> (cut, sort, uniq) and <a href="../04-sed-the-stream-editor/">6.4</a> (sed).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
