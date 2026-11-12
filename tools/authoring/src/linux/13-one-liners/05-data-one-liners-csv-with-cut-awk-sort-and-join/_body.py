import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

DT = r"""rm -rf ~/dt; mkdir -p ~/dt; cd ~/dt
cat > sales.csv <<'EOF'
order_id,date,city,product,qty,price
1001,2026-11-01,Pune,Notebook,3,45.00
1002,2026-11-01,Delhi,Pen,10,10.00
1003,2026-11-02,Pune,Bag,1,799.00
1004,2026-11-02,Mumbai,Notebook,5,45.00
1005,2026-11-03,Delhi,Bag,2,799.00
1006,2026-11-03,Pune,Pen,20,10.00
1007,2026-11-04,Chennai,Notebook,2,45.00
1008,2026-11-04,Mumbai,Pen,,10.00
1009,2026-11-05,Delhi,Notebook,4,45.00
1010,2026-11-05,Pune,Bag,1,799.00
1010,2026-11-05,Pune,Bag,1,799.00
EOF
cat > products.csv <<'EOF'
product,category,supplier
Bag,Luggage,TravelCo
Notebook,Stationery,PaperWorks
Pen,Stationery,InkLine
EOF
cat > customers.csv <<'EOF'
id,name,city
7,"Sharma, Riya",Pune
8,Aman Verma,Delhi
EOF
cat > orders.json <<'EOF'
{"orders":[
 {"id":1001,"city":"Pune","items":[{"sku":"NB","qty":3,"price":45}],"status":"shipped"},
 {"id":1002,"city":"Delhi","items":[{"sku":"PEN","qty":10,"price":10}],"status":"pending"},
 {"id":1003,"city":"Pune","items":[{"sku":"BAG","qty":1,"price":799},{"sku":"PEN","qty":2,"price":10}],"status":"shipped"},
 {"id":1004,"city":"Mumbai","items":[{"sku":"NB","qty":5,"price":45}],"status":"cancelled"}
]}
EOF"""

HOOK = hook('Riya’s manager forwards a CSV export with one line: “Totals per city and top products by Friday, please. Also join it with the product list, and the web team wants the same numbers from the orders API, which returns JSON.” Riya could open Excel, but the real file has 50,000 rows, arrives every night and needs the same steps every time. On Linux, data work is a pipeline of small tools: <code>cut</code> and <code>awk</code> pick columns, <code>sort</code> and <code>uniq</code> count, <code>join</code> and <code>paste</code> combine files, and <code>jq</code> does the same for JSON. This lesson runs each one on a real sales file, including the traps: headers, empty values, duplicates and commas inside quotes.',
    ['inspect a CSV quickly (head, wc, column counts) and pick columns with cut and awk -F,',
     'filter, total, average and group rows with awk, and count and rank with sort | uniq -c',
     'combine files with join, paste and comm, handle headers, duplicates, empty and quoted fields',
     'read, filter and reshape JSON with jq and convert between JSON and CSV'])
ROAD = roadmap([
    ('story', 'The story', 3, 'totals by Friday'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'CSV and JSON', 6, 'simple meaning + 4 depths'),
    ('types', 'Tools compared', 5, 'cut, awk, sort, join, jq'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'group-by and join'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a sales report'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('One or two columns', 'cut -d, -f3,4', 'cut'),
    ('Rows where a column matches', "awk -F, '$3==\"Pune\"'", 'filter'),
    ('Total / average of a column', "awk -F, 'NR>1{s+=$5*$6} END{print s}'", 'sum'),
    ('Total per group', "awk -F, 'NR>1{t[$3]+=$5*$6} END{for(c in t) print c, t[c]}'", 'group by'),
    ('Count and rank values', 'cut -d, -f4 | sort | uniq -c | sort -rn', 'count'),
    ('Combine two files on a key', 'join -t, -1 4 -2 1 <(sort …) <(sort …)', 'join'),
    ('Remove duplicate rows', 'sort -u   ·   awk \'!seen[$0]++\'', 'dedupe'),
    ('JSON', "jq '.orders[] | .id'", 'jq'),
])

cmap = concept_map(
    [('6.2', 'sort, uniq, cut, paste', 'the basic tools'), ('6.5', 'awk', 'fields and patterns'), ('6.3', 'join and comm', 'comparing files')],
    ['inspect: head, wc, NF', 'cut and awk -F,', 'filter, sum, average, group-by', 'sort -t, -k and uniq -c', 'join, paste, comm', 'headers, empty values, duplicates, quotes', 'jq: select, map, group, CSV out'],
    [('13.6', 'Which command when', 'awk vs others'), ('13.7', '100 one-liners', 'cheat sheet'), ('16.5', 'curl', 'fetching JSON from APIs'), ('20.4', 'Big data', 'when files are too big')],
    'CSV: every line a row, every comma a column. JSON: nested objects. awk is the spreadsheet for the first, jq for the second.')

sc = (term(20, 14, 316, 156, ["$ awk -F, 'NR>1{t[$3]+=$5*$6}", ">   END{for(c in t) print c, t[c]}' sales.csv | sort -k2 -rn", ('Pune 2732', 'acc'), ('Delhi 1878', 'out'), ('Mumbai 225', 'out'), ('Chennai 90', 'out')], title='riya@web01: ~/dt', prompt='riya@web01:~/dt$', size=6.6, step=17)
      + t(352, 36, 'One line:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['-F, : commas', 'NR>1 : skip header', 't[city] += qty×price', 'END: print totals', 'sort by total'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Totals by Friday</h2>
  <div class="story">
''' + puzzle('Riya’s first total per city shows Pune 2732 rupees, but the manager’s spreadsheet says 1933. Her count of orders includes a city called <code>city</code>. And when she cuts the customer names with <code>cut -d, -f2 customers.csv</code>, she gets <code>"Sharma</code> instead of <code>Sharma, Riya</code>. What is wrong in each case, and who is right about Pune?') + '''
    <p class="narration">Riya totals the sales per city with one awk command.</p>
''' + scene('A terminal: one awk command adds quantity times price per city, skipping the header, and sorts the totals: Pune first, then Delhi, Mumbai and Chennai.', sc,
            'An awk array is a <tspan font-weight="700" class="s-acc">group-by</tspan> in one line.') + '''
K> What does t[$3] mean?
A> It is a table inside awk: the key is the city (column 3), the value is the running total. Every row adds quantity × price to its city. At the end we print the table.
R> And why do the numbers not match the spreadsheet?
A> Real data is messy: a header line, an order that appears twice, a quantity that is empty, a name with a comma inside quotes. Before trusting a total, inspect the file. Today: CSV and JSON one-liners, and the checks that make them correct.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A spreadsheet drawn as a table: each line is a row and each comma separates columns numbered 1 to 6. Next to it a JSON document drawn as nested boxes: orders contains items, each with sku, qty and price.">'
       + ''.join(label_box(14 + i * 52, 20, 50, 26, [h], 'blue', 7.4) for i, h in enumerate(['$1 id', '$2 date', '$3 city', '$4 prod', '$5 qty', '$6 price']))
       + ''.join(label_box(14 + i * 52, 50, 50, 22, [v], 'card', 7.2) for i, v in enumerate(['1001', '11-01', 'Pune', 'Notebk', '3', '45.00']))
       + ''.join(label_box(14 + i * 52, 76, 50, 22, [v], 'card', 7.2) for i, v in enumerate(['1003', '11-02', 'Pune', 'Bag', '1', '799.00']))
       + t(170, 120, 'CSV: rows and numbered columns', 9.4, 'blue', bold=True)
       + label_box(360, 20, 266, 84, ['{ "orders": [', '  { "id": 1003, "city": "Pune",', '    "items": [ {"sku":"BAG","qty":1}, … ] }', '] }'], 'green', 7.6)
       + t(493, 120, 'JSON: nested keys and lists', 9.4, 'green', bold=True)
       + t(320, 160, 'awk -F, for CSV columns · jq for JSON paths', 10, 'acc', bold=True)
       + t(320, 184, 'Always look at the first lines before computing.', 9.2, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Data one-liners at four depths', [
    ('v', 'No jargon: a table and a tree', '      <p>CSV is a table; JSON is a tree of boxes.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>head -3 sales.csv</code>: see the columns.</li>
        <li><code>cut -d, -f3 sales.csv | sort | uniq -c</code>: orders per city.</li>
        <li><code>awk -F, 'NR&gt;1{s+=$5*$6} END{print s}' sales.csv</code>: grand total.</li>
        <li><code>jq '.orders[].city' orders.json</code>: cities from JSON.</li>
      </ul>'''),
    ('i', 'The checks that make numbers right', '''      <ul>
        <li><b>Header:</b> skip it with <code>NR&gt;1</code> or <code>tail -n +2</code>.</li>
        <li><b>Duplicates:</b> compare <code>wc -l</code> with <code>sort -u | wc -l</code>; remove with <code>awk '!seen[$0]++'</code> (keeps order).</li>
        <li><b>Empty values:</b> <code>awk -F, '$5==""'</code>; decide whether to skip or treat as 0.</li>
        <li><b>Column count:</b> <code>awk -F, '{print NF}' | sort | uniq -c</code>: every row should have the same NF.</li>
        <li><b>join</b> needs both inputs sorted on the key, with the same separator (<code>-t,</code>).</li>
      </ul>'''),
    ('a', 'Behind the screen: quoting, locales and numbers', '''      <ul>
        <li>Real CSV (RFC 4180) allows commas and newlines inside double quotes. cut and plain <code>awk -F,</code> do not understand quotes; GNU awk has <code>FPAT</code>, and tools like csvkit, Miller (mlr) or Python’s csv module parse it properly.</li>
        <li>Numbers: awk uses floating point; sums of money can drift (0.1+0.2). For exact currency, work in paise/cents (integers) or round with printf.</li>
        <li><code>sort</code> and <code>join</code> depend on the locale; use the same <code>LC_ALL=C</code> for both or join complains that input is not sorted.</li>
        <li>Windows files end lines with <code>\\r\\n</code>: the last column then has an invisible <code>\\r</code> (“Pune\\r” ≠ “Pune”). <code>tr -d '\\r'</code> or <code>dos2unix</code> fixes it.</li>
        <li>jq processes a stream of JSON values; <code>-r</code> prints raw strings, <code>-c</code> compact lines, <code>@csv</code> and <code>@tsv</code> produce safe CSV/TSV output.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>CSV, JSON and data one-liners</h2>
''' + def_block(
    '<b>CSV</b> (comma-separated values) stores a table as text: one row per line, columns separated by commas, usually with a header row. <b>JSON</b> stores nested objects (<code>{"key": value}</code>) and lists (<code>[…]</code>). <b>Data one-liners</b> use cut, awk, sort, uniq, join and paste for CSV and <b>jq</b> for JSON to select, filter, aggregate and combine data without a spreadsheet or a program.',
    'Tables with awk, trees with jq; check the data before trusting the numbers.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('CSV', 'Comma-separated values.'),
    ('Header', 'The first line with column names.'),
    ('Delimiter', 'The separator: , ; tab |.'),
    ('Key', 'The column used to match rows (join).'),
    ('Group by', 'One result per value of a column.'),
    ('Deduplicate', 'Remove repeated rows.'),
    ('JSON', 'JavaScript Object Notation.'),
    ('jq filter', 'A path like .orders[].city.'),
]) + '\n' + names('Where the names come from.', [
    ('cut', 'cut columns', 'Unix System III.'),
    ('awk', 'Aho, Weinberger, Kernighan', '1977.'),
    ('join', 'database join', 'Relational idea in a tool.'),
    ('paste', 'paste side by side', 'Opposite of cut.'),
    ('NR / NF', 'number of record / fields', 'awk variables.'),
    ('jq', 'JSON query', 'Stephen Dolan, 2012.'),
    ('TSV', 'tab-separated values', 'Safer than CSV.'),
    ('RFC 4180', 'CSV standard', '2005.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Columns', '<code>cut -d, -f2,3</code>'),
    ('Skip header', '<code>NR&gt;1</code> / <code>tail -n +2</code>'),
    ('Group total', '<code>t[$3]+=$5</code>'),
    ('Sort by column', '<code>sort -t, -k5 -n</code>'),
    ('Join', '<code>join -t, -1 4 -2 1</code>'),
    ('JSON', "<code>jq -r '.a[].b'</code>"),
]) + '\n' + lv + didyou('The comma was chosen for CSV because early 1970s mainframe tools already used it for lists; but in many European countries the comma is the decimal separator, so their spreadsheets export with semicolons. Always check the delimiter in the first line.') + '''
EXAM> “How do you sum a column in a CSV file from the command line?” → awk -F, 'NR&gt;1{s+=$N} END{print s}' file.csv (NR&gt;1 skips the header).
''' + qc('Why does <code>awk -F, \'{print $3}\'</code> include the word “city” in the list of cities?', 'The header row is also a line; skip it with NR&gt;1.') + mistake("cut -d, -f2 customers.csv   (names with commas in quotes)",
    "awk -v FPAT='([^,]*)|(\"[^\"]*\")' '{print $2}'   (GNU awk) · or a CSV-aware tool (mlr, csvkit, Python csv)",
    'cut splits at every comma, even inside quotes: "Sharma, Riya" became "Sharma (real run).') + mistake('totals without checking for duplicates',
    'wc -l vs sort -u | wc -l; dedupe with awk \'!seen[$0]++\' before summing',
    'Order 1010 appears twice in the export: Pune was 799 too high (real run).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The tools, compared</h2>
''' + table(['Tool', 'Best for', 'Example', 'Limits'], [
    ['<code>cut</code>', 'pick columns fast', '<code>cut -d, -f3,5</code>', 'no conditions, no quotes'],
    ['<code>awk -F,</code>', 'filter, compute, group', '<code>awk -F, \'$5&gt;2{print $1}\'</code>', 'quotes need FPAT (gawk)'],
    ['<code>sort -t, -k</code>', 'order by a column', '<code>sort -t, -k6 -rn</code>', 'header gets sorted too'],
    ['<code>uniq -c</code>', 'count repeats', '<code>sort | uniq -c</code>', 'needs sorted input'],
    ['<code>join</code>', 'combine on a key', '<code>join -t, -1 4 -2 1 a b</code>', 'both sorted on the key'],
    ['<code>paste</code>', 'columns side by side', '<code>paste -d, a b</code>', 'by line number, not key'],
    ['<code>comm</code>', 'in A, in B, in both', '<code>comm -12 a b</code>', 'sorted single-column input'],
    ['<code>jq</code>', 'JSON', '<code>jq \'.orders[] | .id\'</code>', 'must be installed'],
    ['<code>mlr</code>, csvkit', 'real CSV with quotes', '<code>mlr --icsv --opprint stats1 …</code>', 'extra packages'],
], minw=560) + table(['Separator', 'cut', 'awk', 'sort', 'join'], [
    ['comma', '<code>-d,</code>', '<code>-F,</code>', '<code>-t,</code>', '<code>-t,</code>'],
    ['tab', '(default)', '<code>-F\'\\t\'</code>', '<code>-t$\'\\t\'</code>', '<code>-t$\'\\t\'</code>'],
    ['semicolon', '<code>-d\\;</code>', '<code>-F\\;</code>', '<code>-t\\;</code>', '<code>-t\\;</code>'],
    ['spaces', '<code>-d\' \'</code> (one)', 'default (runs of blanks)', 'default', 'default'],
], minw=480) + table(['jq filter', 'Gives', 'Example'], [
    ['<code>.</code>', 'the whole document (pretty)', '<code>jq . f.json</code>'],
    ['<code>.orders[]</code>', 'each element of a list', 'one order per output'],
    ['<code>.orders[].city</code>', 'one field of each', '"Pune" …'],
    ['<code>select(.status=="shipped")</code>', 'filter', 'only shipped'],
    ['<code>map(.qty * .price) | add</code>', 'compute a total', 'sum of a list'],
    ['<code>group_by(.city)</code>', 'groups', 'per city'],
    ['<code>[.id, .city] | @csv</code>', 'CSV line', '1001,"Pune"'],
    ['<code>length</code>, <code>keys</code>', 'size, key names', 'inspect'],
], minw=480) + qc('Which tool combines two CSV files on a shared key?', 'join (with both inputs sorted on that key and -t,).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Inspect, select, aggregate, combine and JSON, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine (mawk, GNU coreutils, jq 1.7) as riya, in <code>~/dt</code>: <code>sales.csv</code> (a header and 11 rows; order 1010 is duplicated and order 1008 has an empty qty), <code>products.csv</code> (product, category, supplier), <code>customers.csv</code> (a name with a comma inside quotes) and <code>orders.json</code> (4 orders with nested items).</p>
''' + cmdcard_u(['every new data file', 'before any total'],
               ['computing before looking'])(
    'inspect', 'head · wc -l · awk -F, \'{print NF}\' · sort -u | wc -l', 'inspect the data first',
    'Look at the first lines (header, delimiter), count rows, check that every row has the same number of fields, and look for duplicates and empty cells. Four short commands prevent most wrong reports.',
    'head -3 f.csv   ·   awk -F, \'{print NF}\' f.csv | sort | uniq -c', 'safe',
    [('head -3', 'header and format', 'first look'),
     ('wc -l', 'rows (+1 header)', 'size'),
     ("awk -F, '{print NF}' | uniq -c", 'fields per row', 'broken rows'),
     ('sort | uniq -d', 'duplicate rows', 'dedupe'),
     ("awk -F, '$5==\"\"'", 'empty values', 'gaps'),
     ('cat -A | head -2', 'hidden \\r or tabs', 'Windows files'),
     ('file f.csv', 'encoding, line endings', 'check')],
    dict(setup=DT, cmd="cd ~/dt\nhead -3 sales.csv\necho \"rows: $(($(wc -l < sales.csv) - 1))\"\nawk -F, '{print NF}' sales.csv | sort | uniq -c\necho \"duplicate rows:\"; sort sales.csv | uniq -d\necho \"rows with empty qty:\"; awk -F, 'NR>1 && $5==\"\"' sales.csv", note='Two problems found before computing anything: a duplicated order and an empty quantity.'),
    [('data', [
        dict(situation='Name the columns once.', setup=DT, cmd="cd ~/dt; head -1 sales.csv | tr ',' '\\n' | nl", why='A numbered list of columns: $3 is city, $5 qty, $6 price.')]),
    ],
    anat=anatomy([("awk -F,", 'cmd', 'comma-separated'), ("'NR>1", 'opt', 'skip header'), ("{s+=$5*$6}", 'arg', 'per row'), ("END{print s}'", 'arg', 'at the end')], 'Pattern {action}; END runs once after the last row.')
) + cmdcard_u(['reports: totals, averages, top N', 'filters for other teams'],
               ['money in floating point without rounding'])(
    'agg', "cut · awk -F, filter / sum / group · sort -t, -k · uniq -c", 'select and aggregate',
    '<code>cut -d, -f</code> picks columns. <code>awk -F,</code> filters (<code>$3=="Pune"</code>), computes (<code>$5*$6</code>), sums (<code>s+=…</code>) and groups with arrays (<code>t[$3]+=…</code>). <code>sort -t, -k6 -rn</code> orders rows by a column; <code>sort | uniq -c | sort -rn</code> counts values.',
    "awk -F, 'NR>1{t[$3]+=$5*$6} END{for(k in t) print k, t[k]}' f.csv", 'safe',
    [('cut -d, -f3,4', 'columns', 'quick views'),
     ("$3==\"Pune\"", 'filter', 'one city'),
     ('s+=$5*$6', 'total', 'revenue'),
     ('t[$3]+=…', 'per group', 'per city'),
     ('n[$4]++', 'count per group', 'orders per product'),
     ('printf "%.2f"', 'round', 'money'),
     ('sort -t, -k2,2 -k6nr', 'multi-key sort', 'reports')],
    dict(setup=DT, cmd="cd ~/dt\ncut -d, -f3 sales.csv | tail -n +2 | sort | uniq -c | sort -rn\nawk -F, 'NR>1{s+=$5*$6} END{printf \"grand total: %.2f\\n\", s}' sales.csv\nawk -F, 'NR>1{t[$3]+=$5*$6} END{for(c in t) printf \"%-8s %8.2f\\n\", c, t[c]}' sales.csv | sort -k2 -rn", note='The raw file: Pune 2732.00 includes the duplicated order 1010.'),
    [('qa', [
        dict(situation='The puzzle: clean first, then total.', setup=DT, cmd="cd ~/dt\nawk -F, 'NR==1 || !seen[$0]++' sales.csv > clean.csv\necho \"rows before: $(tail -n +2 sales.csv | wc -l), after: $(tail -n +2 clean.csv | wc -l)\"\nawk -F, 'NR>1 && $5!=\"\" {t[$3]+=$5*$6} END{for(c in t) printf \"%-8s %8.2f\\n\", c, t[c]}' clean.csv | sort -k2 -rn", why='Without the duplicate, Pune is 1933.00, the spreadsheet’s number. The empty qty is skipped explicitly.')]),
     ('data', [
        dict(situation='Top product by revenue and by quantity.', setup=DT, cmd="cd ~/dt; awk -F, 'NR>1 && !seen[$0]++ {r[$4]+=$5*$6; q[$4]+=$5} END{for(p in r) printf \"%-9s qty %3d  revenue %8.2f\\n\", p, q[p], r[p]}' sales.csv | sort -k5 -rn", why='Pens sell the most units, bags bring the most money.')]),
    ]
) + cmdcard_u(['adding names, categories or prices from another file', 'comparing two exports'],
               ['join on unsorted input', 'paste for files whose rows are in different orders'])(
    'combine', 'join -t, · paste -d, · comm · awk two-file lookup', 'combine files',
    '<code>join</code> matches rows of two files on a key column, like a database join; both inputs must be sorted on that key. <code>paste</code> glues files side by side by line number. <code>comm</code> compares two sorted lists. The awk idiom <code>NR==FNR{…; next}</code> loads a lookup table from the first file and uses it on the second, with no sorting.',
    "join -t, -1 4 -2 1 <(sort -t, -k4 a.csv) <(sort -t, -k1 b.csv)", 'safe',
    [('join -t, -1 N -2 M', 'key column in each file', 'lookups'),
     ('-a 1', 'keep unmatched rows of file 1', 'left join'),
     ('-o 1.1,2.2', 'choose output columns', 'shape'),
     ('paste -d, a b', 'side by side', 'columns'),
     ('comm -12 / -23', 'both / only A', 'diffs'),
     ("awk -F, 'NR==FNR{m[$1]=$2; next} {print $0, m[$4]}' b a", 'lookup without sort', 'big files')],
    dict(setup=DT, cmd="cd ~/dt\njoin -t, -1 4 -2 1 <(tail -n +2 sales.csv | sort -t, -k4,4) <(tail -n +2 products.csv | sort -t, -k1,1) | head -3\nawk -F, 'NR==FNR{cat[$1]=$2; next} FNR>1{print $1, $4, cat[$4]}' products.csv sales.csv | head -3", note='Both add the category to each sale; join puts the key first, the awk lookup keeps the original order.'),
    [('data', [
        dict(situation='Revenue per category.', setup=DT, cmd="cd ~/dt; awk -F, 'NR==FNR{cat[$1]=$2; next} FNR>1 && !seen[$0]++ {t[cat[$4]]+=$5*$6} END{for(c in t) printf \"%-11s %8.2f\\n\", c, t[c]}' products.csv sales.csv | sort -k2 -rn", why='Lookup + group-by in one awk program.')]),
     ('qa', [
        dict(situation='Which products in the catalogue never sold in Chennai?', setup=DT, cmd="cd ~/dt; comm -23 <(tail -n +2 products.csv | cut -d, -f1 | sort) <(awk -F, '$3==\"Chennai\"{print $4}' sales.csv | sort -u)", why='comm -23: only in the first list.')]),
    ]
) + cmdcard_u(['APIs, configs, logs in JSON', 'turning JSON into CSV for a spreadsheet'],
               ['parsing JSON with grep and sed'])(
    'jq', "jq . · .a[] · select() · map() · group_by · @csv · -r -c", 'JSON with jq',
    'jq reads JSON and applies a filter. <code>.orders[]</code> walks a list, <code>.city</code> picks a key, <code>|</code> chains steps, <code>select(cond)</code> filters, <code>map(f)</code> transforms a list, <code>add</code> sums, <code>group_by(.k)</code> groups, and <code>@csv</code> outputs CSV. <code>-r</code> prints raw text without quotes, <code>-c</code> one compact line per value.',
    "jq -r '.orders[] | select(.status==\"shipped\") | .id' orders.json", 'safe',
    [('jq .', 'pretty print', 'look'),
     ('.orders | length', 'how many', 'count'),
     ('.orders[].city', 'one field each', 'list'),
     ('select(.status=="x")', 'filter', 'subset'),
     ('[.items[] | .qty*.price] | add', 'total per order', 'compute'),
     ('group_by(.city) | map({city: .[0].city, n: length})', 'group', 'per city'),
     ('[.id,.city] | @csv', 'CSV', 'export')],
    dict(setup=DT, cmd="cd ~/dt\njq '.orders | length' orders.json\njq -r '.orders[] | select(.status==\"shipped\") | \"\\(.id) \\(.city)\"' orders.json\njq -r '.orders[] | [.id, .city, ([.items[] | .qty * .price] | add)] | @csv' orders.json", note='Count, filter and a CSV export with a computed total per order (order 1003 has two items).'),
    [('dev', [
        dict(situation='Group JSON orders by city.', setup=DT, cmd="cd ~/dt; jq -c '.orders | group_by(.city) | map({city: .[0].city, orders: length, value: (map(.items[] | .qty * .price) | add)})[]' orders.json", why='One object per city with count and value.')]),
     ('data', [
        dict(situation='CSV to JSON (for an API).', setup=DT, cmd="cd ~/dt; tail -n +2 products.csv | jq -R -c 'split(\",\") | {product: .[0], category: .[1], supplier: .[2]}'", why='-R reads raw lines; split turns each into a JSON object.')]),
    ]
) + undo('One-liners read data; writing results to the input file destroys it.', [
    ('Overwrote the input (awk … f.csv > f.csv):', 'the shell empties f.csv before awk reads it: restore from the source; write to a new file and mv.'),
    ('Totals look wrong:', 'inspect: header, duplicates, empty cells, NF per row, \\r endings.'),
    ('join prints nothing:', 'sort both on the key with the same locale and separator; check the key column numbers.'),
    ('jq error:', 'validate with <code>jq . file</code>; fix the JSON (trailing commas are not allowed).'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(setup=DT, cmd="cd ~/dt; join -t, -1 4 -2 1 <(tail -n +2 sales.csv) <(tail -n +2 products.csv) | head -1", meaning='Inputs not sorted on the key.', fix='sort -t, -kN,N both sides.'),
    dict(setup=DT, cmd="cd ~/dt; cut -f3 sales.csv | head -2", meaning='cut defaults to tabs; no tab in the line, so the whole line is printed.', fix='cut -d, -f3.'),
    dict(setup=DT, cmd="cd ~/dt; echo '{\"a\":1,}' | jq .", meaning='Invalid JSON: trailing comma.', fix='Remove it.'),
    dict(setup=DT, cmd="cd ~/dt; jq '.orders[].nosuch' orders.json | head -2", meaning='Missing keys give null, not an error.', fix='Check key names with jq keys.'),
    dict(setup=DT, cmd="cd ~/dt; awk -F, '{s+=$5} END{print s' sales.csv", meaning='Syntax error in the awk program.', fix='Close the braces.'),
]) + qc('Why must both inputs of join be sorted?', 'join walks both files once, like a merge; unsorted keys are skipped or reported.') + '''
'''
cards = cards + '</section>\n'

ROWS = [('Pune', 135), ('Delhi', 100), ('Pune', 799), ('Mumbai', 225), ('Delhi', 1598), ('Pune', 200)]
def grp(k):
    o = ''
    for i, (c, v) in enumerate(ROWS[:k + 1]):
        o += label_box(10, 10 + i * 24, 120, 20, [f'{c} +{v}'], 'green' if i == k else 'card', 7.4)
    tot = {}
    for c, v in ROWS[:k + 1]:
        tot[c] = tot.get(c, 0) + v
    for j, (c, v) in enumerate(sorted(tot.items())):
        o += label_box(200, 20 + j * 34, 150, 28, [f't[{c}] = {v}'], 'blue', 7.8)
    return o
see_cmds = [["$ awk -F, 'NR>1{t[$3]+=$5*$6}'"]] * 5 + [["$ … END{for(c in t) print c, t[c]}'", ('Delhi 1698', 'out'), ('Mumbai 225', 'out'), ('Pune 1134', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/dt', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Row 1.', 'Row 2.', 'Row 3.', 'Row 4.', 'Row 5.', 'END: print.'])]
behind = [grp(k) for k in range(6)]
two = anim_two('A group-by in awk', 'Behind the screen: the array t[ ] filling up',
               'A terminal running the awk group-by over six sales rows and printing the totals at the end.',
               'Rows on the left are read one by one; on the right one box per city keeps its running total.', see, behind,
               ['Row 1.', 'Row 2.', 'Row 3.', 'Row 4.', 'Row 5.', 'END.'],
               ['1', '2', '3', '4', '5', 'END'])

def jn(k):
    left = ['Bag,1003', 'Notebook,1001', 'Pen,1002']
    right = ['Bag,Luggage', 'Notebook,Stationery', 'Pen,Stationery']
    o = ''
    for i in range(3):
        o += label_box(10, 14 + i * 34, 110, 28, [left[i]], 'blue' if i <= k else 'card', 7.6)
        o += label_box(240, 14 + i * 34, 110, 28, [right[i]], 'green' if i <= k else 'card', 7.6)
        if i <= k:
            o += arrow(120, 28 + i * 34, 240, 28 + i * 34)
    if k >= 0:
        o += t(180, 140, ', '.join(['Bag,1003,Luggage', 'Notebook,1001,Stationery', 'Pen,1002,Stationery'][:k + 1]), 6.8, 'violet', bold=True)
    o += t(180, 170, 'Both sorted by product: one pass, like a zip.', 8.4, 'ink2')
    return o
s1 = anim_one('Animated example', 'How join matches rows',
              'join walks two sorted files at the same time.',
              'join -t, file1 file2', 'Two sorted lists side by side; arrows connect equal keys one by one and the joined row appears below.', [jn(k) for k in range(3)],
              ['Bag.', 'Notebook.', 'Pen.'], hid='scenario-join')

dx = dissect('Layer by layer: making data one-liners correct',
    'Each layer has a real command and output from our build machine.', [
    dict(key='quote', name='Quoted commas', sub='CSV is not just commas', why='Names, addresses.', how='FPAT or a CSV tool.', impl='mawk lacks FPAT.', used='Customer files.',
         setup=DT, cmd="cd ~/dt; cut -d, -f2 customers.csv | tail -n +2\npython3 -c 'import csv,sys; [print(r[1]) for r in list(csv.reader(open(\"customers.csv\")))[1:]]'"),
    dict(key='cr', name='Windows line endings', sub='\\r', why='Invisible mismatch.', how='cat -A shows ^M.', impl='tr -d \\r.', used='Excel exports.',
         setup=DT, cmd="cd ~/dt; printf 'city\\r\\nPune\\r\\n' > win.csv; cat -A win.csv; awk 'NR>1 && $1==\"Pune\"{print \"matched\"}' win.csv | grep -c matched; tr -d '\\r' < win.csv | awk 'NR>1 && $1==\"Pune\"{print \"matched after tr\"}'"),
    dict(key='float', name='Floating point', sub='money', why='Drift.', how='Integers or printf.', impl='IEEE 754.', used='Finance.',
         cmd="awk 'BEGIN{s=0; for(i=0;i<10;i++) s+=0.1; printf \"%.17f\\n%.2f\\n\", s, s}'"),
    dict(key='inplace', name='Output to input', sub='> truncates first', why='Lost data.', how='Shell opens > before running.', impl='sponge / temp file.', used='Every edit.',
         setup=DT, cmd="cd ~/dt; cp products.csv p.csv; sort p.csv > p.csv; wc -l < p.csv; cp products.csv p.csv; sort p.csv > p.tmp && mv p.tmp p.csv; wc -l < p.csv"),
], hint='From quoting to safe output. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A group-by, and how join matches</h2>
''' + two + s1 + dx + qc('Why did <code>sort p.csv &gt; p.csv</code> leave an empty file?', 'The shell truncates p.csv for the redirection before sort runs, so sort reads an empty file.') + '''
</section>
'''

VAR = variations('Twenty-two more data one-liners. All were really run on our build machine on the sample files.', [
    ('CSV with cut, awk and sort', [
        dict(title='Two columns, header kept', setup=DT, cmd="cut -d, -f3,4 ~/dt/sales.csv | head -3", why='cut keeps the header line too.'),
        dict(title='Rows for one city', setup=DT, cmd="awk -F, 'NR==1 || $3==\"Delhi\"' ~/dt/sales.csv", why='Keep the header with NR==1.'),
        dict(title='Orders above 500 rupees', setup=DT, cmd="awk -F, 'NR>1 && $5*$6>500 {print $1, $3, $5*$6}' ~/dt/sales.csv", why='Compute inside the condition.'),
        dict(title='Sort by price, then by city', setup=DT, cmd="tail -n +2 ~/dt/sales.csv | sort -t, -k6,6rn -k3,3 | cut -d, -f1,3,6 | head -4", why='-k6,6rn then -k3,3 as a tie-breaker.'),
        dict(title='Average quantity (skip empty)', setup=DT, cmd="awk -F, 'NR>1 && $5!=\"\" {s+=$5; n++} END{printf \"%.2f over %d rows\\n\", s/n, n}' ~/dt/sales.csv", why='Count only rows with a value.'),
        dict(title='Min and max price', setup=DT, cmd="awk -F, 'NR==2{mn=mx=$6} NR>1{if($6<mn)mn=$6; if($6>mx)mx=$6} END{print \"min\", mn, \"max\", mx}' ~/dt/sales.csv", why='Initialise from the first data row.'),
        dict(title='Revenue per day', setup=DT, cmd="awk -F, 'NR>1 && !s[$0]++ {d[$2]+=$5*$6} END{for(k in d) print k, d[k]}' ~/dt/sales.csv | sort", why='Date as the group key.'),
        dict(title='Distinct products', setup=DT, cmd="tail -n +2 ~/dt/sales.csv | cut -d, -f4 | sort -u | paste -sd,", why='paste -s joins lines with commas.'),
        dict(title='Add a column (line total)', setup=DT, cmd="awk -F, -v OFS=, 'NR==1{print $0, \"total\"; next} {print $0, $5*$6}' ~/dt/sales.csv | head -3", why='OFS keeps commas in the output.'),
        dict(title='Change the delimiter to tabs', setup=DT, cmd="tr ',' '\\t' < ~/dt/products.csv | cat -A | head -2", why='^I are the tabs.'),
    ]),
    ('Combining and cleaning', [
        dict(title='Remove duplicate rows, keep order', setup=DT, cmd="awk '!seen[$0]++' ~/dt/sales.csv | wc -l", why='12 → 11 lines.'),
        dict(title='Duplicate order IDs only', setup=DT, cmd="tail -n +2 ~/dt/sales.csv | cut -d, -f1 | sort | uniq -d", why='uniq -d prints repeated values.'),
        dict(title='Fill empty qty with 0', setup=DT, cmd="awk -F, -v OFS=, '$5==\"\"{$5=0} 1' ~/dt/sales.csv | grep 1008", why='Assigning a field rebuilds the line; 1 prints it.'),
        dict(title='Left join: keep sales without a product match', setup=DT, cmd="cd ~/dt; printf '1011,2026-11-06,Pune,Stapler,1,99.00\\n' >> sales.csv; join -t, -a 1 -1 4 -2 1 <(tail -n +2 sales.csv | sort -t, -k4,4) <(tail -n +2 products.csv | sort -t, -k1,1) | grep Stapler", why='-a 1 keeps the Stapler row although it has no category.'),
        dict(title='Paste two columns together', setup=DT, cmd="cd ~/dt; paste -d, <(tail -n +2 products.csv | cut -d, -f1) <(tail -n +2 products.csv | cut -d, -f3)", why='Side by side by line number.'),
        dict(title='Split a file by city', setup=DT, cmd="cd ~/dt; awk -F, 'NR>1{print > (\"city_\" $3 \".csv\")}' sales.csv; wc -l city_*.csv | tail -1", why='awk can write to many files.'),
    ]),
    ('JSON with jq', [
        dict(title='Pretty print', setup=DT, cmd="jq '.orders[0]' ~/dt/orders.json", why='Formatted with indentation.'),
        dict(title='Keys of an object', setup=DT, cmd="jq -c '.orders[0] | keys' ~/dt/orders.json", why='Find the field names.'),
        dict(title='Count by status', setup=DT, cmd="jq -r '.orders[].status' ~/dt/orders.json | sort | uniq -c", why='jq for extraction, Unix tools for counting.'),
        dict(title='Total value of shipped orders', setup=DT, cmd="jq '[.orders[] | select(.status==\"shipped\") | .items[] | .qty * .price] | add' ~/dt/orders.json", why='Filter, flatten, compute, sum.'),
        dict(title='All SKUs sold, unique', setup=DT, cmd="jq -r '[.orders[].items[].sku] | unique | join(\",\")' ~/dt/orders.json", why='unique sorts and dedupes.'),
        dict(title='TSV for a spreadsheet', setup=DT, cmd="jq -r '.orders[] | [.id, .city, .status] | @tsv' ~/dt/orders.json", why='@tsv escapes tabs safely.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Data one-liners at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['awk', 'reports'], 'blue', 8.6), '1. Nightly business reports',
              'A cron job totals the day’s CSV export per region and mails it, long before anyone opens a spreadsheet.', ['Export', '*awk group-by', 'email']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['dedupe', 'quality'], 'red', 8.6), '2. Data quality checks',
    'Before loading into a warehouse: column counts, duplicates and empty values are checked with one-liners and the load stops if they fail.', ['File', '*checks', 'load or stop']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['join', 'finance'], 'amber', 8.6), '3. Reconciliation',
    'Finance joins bank exports with internal orders on an ID; comm shows payments without orders and orders without payments.', ['Two files', '*join / comm', 'mismatches']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['jq', 'APIs'], 'green', 8.6), '4. APIs and cloud tools',
    'curl … | jq extracts fields from APIs; AWS, Azure and Kubernetes CLIs return JSON that jq filters (kubectl get pods -o json | jq).', ['API', '*jq', 'value']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['split', 'pipelines'], 'violet', 8.6), '5. Data engineering prep',
    'Split, sample and convert files before Spark or a database (Big Data track); one-liners make quick samples: head, shuf -n.', ['Raw', '*one-liners', 'ready']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='See the header as a list', scenario='New file.', setup=DT, cmd="head -1 ~/dt/sales.csv | tr ',' '\\n' | nl | head -3", explain='Columns numbered.'),
    dict(level='b', title='Rows without header', scenario='Counting.', setup=DT, cmd="tail -n +2 ~/dt/sales.csv | wc -l", explain='tail -n +2.'),
    dict(level='i', title='Orders per city', scenario='Quick count.', setup=DT, cmd="tail -n +2 ~/dt/sales.csv | cut -d, -f3 | sort | uniq -c | sort -rn | head -2", explain='Count and rank.'),
    dict(level='i', title='Clean total', scenario='Report.', setup=DT, cmd="awk -F, 'NR>1 && $5!=\"\" && !s[$0]++ {t+=$5*$6} END{printf \"%.2f\\n\", t}' ~/dt/sales.csv", explain='Skip header, empty, duplicates.'),
    dict(level='a', title='JSON to CSV with a total', scenario='Export.', setup=DT, cmd="jq -r '.orders[] | [.id, ([.items[]|.qty*.price]|add)] | @csv' ~/dt/orders.json | head -2", explain='Computed column.'),
], extra=build_up('the Friday report', 'Riya builds the manager’s report, checking the data first.', DT, [
    ("cd ~/dt; awk -F, '{print NF}' sales.csv | sort -u; sort sales.csv | uniq -d | wc -l", '1. Check: same number of columns everywhere? any duplicates?'),
    ("cd ~/dt; awk -F, 'NR==1 || !seen[$0]++' sales.csv > clean.csv; wc -l < clean.csv", '2. Remove the duplicate into a new file.'),
    ("cd ~/dt; awk -F, 'NR>1 && $5!=\"\" {t[$3]+=$5*$6} END{for(c in t) printf \"%s,%.2f\\n\", c, t[c]}' clean.csv | sort -t, -k2,2rn", '3. Totals per city.'),
    ("cd ~/dt; { echo 'city,revenue'; awk -F, 'NR>1 && $5!=\"\" {t[$3]+=$5*$6} END{for(c in t) printf \"%s,%.2f\\n\", c, t[c]}' clean.csv | sort -t, -k2,2rn; } > report.csv; cat report.csv", '4. Save it as a CSV with a header for the manager.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Pick columns', 'cut', 'Fast, simple.', 'awk for nothing.'),
    ('Filter + compute', 'awk', 'One pass.', 'Excel for 50,000 rows.'),
    ('Join on a key', 'join or awk NR==FNR', 'Exact.', 'paste (line order only).'),
    ('Quoted CSV', 'mlr / csvkit / Python csv', 'Correct parsing.', 'cut and awk -F,.'),
    ('JSON', 'jq', 'Paths, filters.', 'grep and sed on JSON.'),
    ('Millions of rows, SQL', 'sqlite3 / DuckDB', 'Real queries.', 'Nested awk scripts.'),
]) + keys('Handy forms.', [
    ("awk -F, 'NR>1'", 'skip header', 'every total'),
    ("t[$3]+=$5*$6", 'group by', 'reports'),
    ("awk '!seen[$0]++'", 'dedupe, keep order', 'cleaning'),
    ('sort -t, -k6,6rn', 'sort by column', 'top N'),
    ("join -t, -1 4 -2 1", 'join on key', 'lookups'),
    ("jq -r '… | @csv'", 'JSON to CSV', 'exports'),
]) + scriptit('salesreport.sh', 'A small, safe sales report from a CSV: validate the file (column count, duplicates, empty quantities), then print totals per city and per product category using the product list, and the top product.',
'''sales=${1:-$HOME/dt/sales.csv}; prods=${2:-$HOME/dt/products.csv}
[ -r "$sales" ] && [ -r "$prods" ] || { echo "missing input" >&2; exit 1; }
cols=$(head -1 "$sales" | awk -F, '{print NF}')
bad=$(awk -F, -v c="$cols" 'NF!=c' "$sales" | wc -l); dup=$(tail -n +2 "$sales" | sort | uniq -d | wc -l)
empty=$(awk -F, 'NR>1 && $5==""' "$sales" | wc -l)
echo "checks: $bad bad rows, $dup duplicate rows, $empty empty qty"
awk -F, 'NR>1 && $5!="" && !s[$0]++' "$sales" > /tmp/clean.$$
echo "-- revenue per city"; awk -F, '{t[$3]+=$5*$6} END{for(c in t) printf "%-9s %9.2f\\n", c, t[c]}' /tmp/clean.$$ | sort -k2 -rn
echo "-- revenue per category"; awk -F, 'NR==FNR{if(FNR>1)cat[$1]=$2; next} {t[cat[$4]]+=$5*$6} END{for(c in t) printf "%-11s %9.2f\\n", c, t[c]}' "$prods" /tmp/clean.$$ | sort -k2 -rn
echo "-- top product: $(awk -F, '{r[$4]+=$5*$6} END{for(p in r) print r[p], p}' /tmp/clean.$$ | sort -rn | head -1 | awk '{print $2}')"
rm -f /tmp/clean.$$''',
'<p>Run without arguments, so it reads the sample files.</p>', expect='any') + puzzle_answer('<b>1.</b> The export contained order 1010 twice, so Pune got 799 extra: the spreadsheet (1933) was right. Remove duplicates first (<code>awk \'!seen[$0]++\'</code>) and treat the empty quantity explicitly. <b>2.</b> The header line was counted as a row, so “city” appeared as a city. Skip it with <code>NR&gt;1</code> or <code>tail -n +2</code>. <b>3.</b> <code>cut</code> splits at every comma, even inside quotes, so <code>"Sharma, Riya"</code> was cut in two. Use a CSV-aware parser (Python csv, mlr, csvkit, or gawk FPAT).') + qc('Which jq option prints strings without quotes?', '-r (raw output).') + '''
</section>
'''

_sh.run_sh('rm -rf ~/dt', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../06-text-processing/05-awk-fields-patterns-and-reports/">Lesson 6.5</a> (awk) and <a href="../../06-text-processing/03-comparing-files-diff-comm-cmp-and-join/">Lesson 6.3</a> (join and comm).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
