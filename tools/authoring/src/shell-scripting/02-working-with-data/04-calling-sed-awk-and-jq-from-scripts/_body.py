import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# Riya's ops data: a config to edit, orders to summarise, and an API response in JSON
SS = r'''rm -rf ~/ops; mkdir -p ~/ops/data ~/ops/bin; cd ~/ops
cat > data/app.conf <<'EOF'
# app.conf
listen_port = 8080
db_host = db01.internal
log_dir = /var/log/orders
feature_x = off
EOF
cat > data/orders.csv <<'EOF'
id,city,amount,status
1001,Pune,450,paid
1002,Mumbai,1200,paid
1003,Pune,300,failed
1004,Delhi,800,paid
1005,Mumbai,150,refunded
1006,Pune,999,paid
EOF
cat > data/servers.json <<'EOF'
{
  "region": "ap-south-1",
  "servers": [
    {"name": "web01", "ip": "10.0.1.11", "env": "prod", "cpu": 72, "tags": ["web", "nginx"]},
    {"name": "web02", "ip": "10.0.1.12", "env": "prod", "cpu": 91, "tags": ["web"]},
    {"name": "db01",  "ip": "10.0.2.21", "env": "prod", "cpu": 45, "tags": ["db", "postgres"]},
    {"name": "test01","ip": "10.0.9.5",  "env": "test", "cpu": 12, "tags": []}
  ]
}
EOF'''

HOOK = hook('Some jobs are too big or too fiddly for pure Bash: changing one value in a config file in place, totalling a column over a million lines, reading a JSON answer from a cloud API. Three tools do these jobs better than any loop: <b>sed</b> (edit text streams and files), <b>awk</b> (columns, sums, reports) and <b>jq</b> (JSON). Calling them from a script brings one new danger: getting a shell variable <i>into</i> their programs safely. Riya’s script puts a city name with a slash into a sed command and breaks it; another puts a user-supplied value into an awk program and lets it run code. This lesson shows the right way for each tool: <code>awk -v</code>, escaped sed replacements, <code>jq --arg</code>.',
    ['edit files in place with sed -i (with a backup), using a variable safely in the pattern and the replacement',
     'pass shell variables into awk with -v and ENVIRON, and keep longer awk programs readable in a heredoc or .awk file',
     'read, filter and reshape JSON with jq (.field, .[], select, map, -r, @csv, --arg, --argjson) and build JSON safely',
     'choose between a Bash loop, sed, awk and jq for a job, and check results before replacing files'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three tools, one danger'),
    ('decide', 'Which tool?', 2, 'the quick chart'),
    ('definition', 'sed, awk, jq', 5, 'simple meaning + 4 depths'),
    ('types', 'Compared', 4, 'jobs and tools'),
    ('commands', 'Step by step', 15, 'in-place edits, -v, jq'),
    ('animation', 'See it happen', 4, 'jq walks the JSON'),
    ('run', 'Run on your PC', 3, 'a real API'),
    ('lab', 'Practice lab', 8, 'config + JSON report'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('The job is… → use', [
    ('change a value in a config file', 'sed -i.bak "s|^key = .*|key = $v|" file', 'escape $v'),
    ('sum/group a column, big files', 'awk -F, -v city="$c" \'…\'', '-v, never "$c" in the code'),
    ('anything with JSON', 'jq --arg name "$n" \'…\'', 'never grep/sed JSON'),
    ('build JSON from variables', 'jq -n --arg … \'{…}\'', 'quoting done for you'),
    ('a few lines, simple logic', 'Bash while read', 'Lesson 2.1'),
    ('a long awk program', 'awk -f report.awk', 'readable, testable'),
])

cmap = concept_map(
    [('2.2', 'Parsing formats', 'CSV, logs'), ('L:6.4', 'sed basics', 's///, addresses'), ('L:6.5', 'awk basics', 'fields, patterns')],
    ['sed -i with a backup', 'escaping a variable for sed', 'awk -v and ENVIRON', 'awk programs in files', 'jq filters: . [] select map', 'jq --arg / --argjson and -n', 'check before replace'],
    [('3.1', 'Error handling', 'failed edits'), ('4.2', 'Log monitor', 'awk in a pipeline'), ('4.5', 'Deploy capstone', 'JSON + config'), ('L:13.5', 'Data one-liners', 'more jq')],
    'Let sed, awk and jq do the heavy work, and hand them your variables the safe way.')

sc = (term(20, 14, 316, 156, ['$ sed -i.bak "s|^listen_port = .*|listen_port = $port|" app.conf', ('listen_port = 9090', 'out'), '$ awk -F, -v c="$city" \'$2==c {s+=$3} END{print s}\' orders.csv', ('1749', 'out'), '$ jq -r --arg e prod \'.servers[] | select(.env==$e) | .name\'', ('web01 web02 db01', 'acc')], title='riya@laptop: ~/ops/data', prompt='$', size=6.0, step=19)
      + t(352, 36, 'Variables in, safely:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['sed: escape it', 'awk: -v name=', 'jq: --arg name', 'never paste into', '  the program text'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three tools, one danger</h2>
  <div class="story">
''' + puzzle('Riya sets a new log folder with <code>sed -i "s/^log_dir = .*/log_dir = $dir/" app.conf</code>, where <code>dir=/srv/logs/orders</code>, and gets “unknown option to `s’”. Her city report builds the awk program as <code>"\\$2 == \\"$city\\" {…}"</code>; a colleague passes the city <code>x" || system("touch HACKED") || "</code> and a file called HACKED appears. And her script that reads the server list with <code>grep \'"name"\' servers.json | cut -d\'"\' -f4</code> breaks the day the API returns the JSON on one line. Three different tools, the same root cause. What is it?') + '''
    <p class="narration">In <code>~/ops/data</code> (every run in this lesson is real; jq 1.7 is installed on our build machine).</p>
''' + scene('A terminal: sed changes listen_port in place, awk sums Pune orders with -v, jq lists production server names with --arg.', sc,
            'Pass values <tspan font-weight="700" class="s-acc">as data, not as code</tspan>.') + '''
K> What do the three bugs have in common?
A> In each one a value was pasted into another program’s source text: a sed command, an awk program, a fake JSON parser. When the value contains that language’s special characters (<code>/</code> for sed, quotes for awk, a missing newline for grep), it changes the program. Each tool has a way to receive values as data instead.
R> And JSON should never be grepped?
A> JSON can be on one line or many, keys can be in any order, strings can contain escaped quotes. jq actually parses it, so the answer does not depend on how the JSON happens to be formatted today.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A shell variable passed three ways: into sed after escaping, into awk with -v, into jq with --arg; pasting it into the program text is marked unsafe.">'
       + label_box(250, 14, 140, 40, ['$value (shell)'], 'blue', 9)
       + ''.join(arrow(320, 56, x + 70, 100) + label_box(x, 102, 140, 50, [a, b], 'green', 8.4) for x, a, b in [(14, 'sed', 'escape / | & \\'), (250, 'awk -v v="$value"', 'data, not code'), (486, 'jq --arg v "$value"', '$v inside jq')])
       + t(320, 182, 'unsafe: "…$value…" inside the program text', 9.2, 'red', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('sed, awk and jq from scripts at four depths', [
    ('v', 'No jargon: filling in a form', '      <p>You write your name in the box on the form; you do not rewrite the form’s questions. -v and --arg are the boxes.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>sed -i.bak 's/^feature_x = .*/feature_x = on/' app.conf</code></li>
        <li><code>awk -F, -v c="$city" '$2 == c {s += $3} END {print s}' orders.csv</code></li>
        <li><code>jq -r '.servers[].name' servers.json</code></li>
        <li><code>jq -r --arg e "$env" '.servers[] | select(.env == $e) | .ip' servers.json</code></li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li>sed has no variables: the value becomes part of the command, so escape <code>\\</code>, the delimiter and <code>&amp;</code> in the replacement (and regex characters in the pattern), or pick a delimiter like <code>|</code> that the value cannot contain.</li>
        <li><code>sed -i.bak</code> keeps a backup; GNU sed accepts <code>-i</code> alone, macOS/BSD sed needs <code>-i ''</code>.</li>
        <li><code>awk -v</code> processes backslash escapes in the value; <code>ENVIRON["NAME"]</code> passes it raw.</li>
        <li>jq: <code>-r</code> raw strings (no quotes), <code>--arg</code> always a string, <code>--argjson</code> a number/array/object, <code>-n</code> build from nothing, <code>-e</code> exit status from the result.</li>
      </ul>'''),
    ('a', 'Behind the screen: three small languages', '''      <ul>
        <li>Each tool parses its own program string: sed’s grammar is <code>address command</code>, awk is a full C-like language with <code>system()</code> and pipes, jq is a functional language over JSON values. Shell quoting only builds that string; it does not protect it.</li>
        <li><code>sed -i</code> never edits in place literally: it writes a new temp file in the same folder and renames it over the original (Lesson 2.3’s atomic pattern), so the inode changes and hard links are broken.</li>
        <li>awk reads input in one pass with buffered I/O and compiled patterns, which is why it beats a Bash <code>while read</code> loop by orders of magnitude on large files.</li>
        <li>jq streams tokens and builds values; <code>--stream</code> handles files bigger than memory. Its <code>@csv</code>, <code>@tsv</code>, <code>@sh</code> and <code>@base64</code> formatters escape output for the next tool.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>sed, awk and jq in scripts</h2>
''' + def_block(
    '<b>sed</b> (stream editor) applies editing commands such as substitutions and deletions to each line of text, optionally rewriting a file in place. <b>awk</b> is a pattern-action language for field-based text: it splits lines into fields and is ideal for filtering, summing and reporting. <b>jq</b> is a command-line JSON processor that parses JSON and applies filters to select, transform and format it. Scripts pass values to them as data with <code>awk -v</code> and <code>jq --arg</code>; sed needs escaping.',
    'sed edits, awk counts, jq understands JSON; give them values as data.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('sed -i', 'Edit a file in place.'),
    ('-i.bak', 'Keep a backup copy.'),
    ('awk -v', 'Pass a variable to awk.'),
    ('ENVIRON', 'awk’s view of the environment.'),
    ('jq filter', '.servers[] | .name'),
    ('--arg', 'A string into jq.'),
    ('--argjson', 'A number/JSON into jq.'),
    ('-r', 'jq raw output, no quotes.'),
]) + '\n' + names('Where the names come from.', [
    ('sed', 'stream editor', 'Lee McMahon, 1974.'),
    ('awk', 'Aho, Weinberger, Kernighan', '1977.'),
    ('jq', 'JSON query', 'Stephen Dolan, 2012.'),
    ('JSON', 'JavaScript Object Notation', 'Douglas Crockford.'),
    ('-i', 'in place', 'GNU sed extension.'),
    ('-v', 'variable', 'awk option.'),
    ('@csv', 'jq formatter', 'Escapes for CSV.'),
    ('select', 'keep matching values', 'jq built-in.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Edit + backup', '<code>sed -i.bak \'…\' f</code>'),
    ('Var into awk', '<code>awk -v x="$x"</code>'),
    ('JSON field', '<code>jq -r .name</code>'),
    ('Var into jq', '<code>jq --arg x "$x"</code>'),
    ('Build JSON', '<code>jq -n --arg …</code>'),
    ('Check result', '<code>diff f.bak f</code>'),
]) + '\n' + lv + didyou('jq can also <i>edit</i> JSON: <code>jq \'.servers[1].cpu = 50\' servers.json</code> prints the whole document with one value changed. Combined with Lesson 2.3’s temp-file-and-mv pattern it becomes a safe in-place JSON editor.') + '''
EXAM> “How do you pass a shell variable to awk?” → awk -v name="$var" '… name …' (or ENVIRON["var"] for an exported variable); never by putting "$var" inside the awk program text.
''' + qc('Why does sed "s/x/$dir/" fail when dir=/srv/logs?', 'The slashes in the value end the s command early; escape them or use another delimiter such as |.') + mistake("awk \"\\$2 == \\\"$city\\\" {s+=\\$3}\" orders.csv",
    "awk -v c=\"$city\" '$2 == c {s += $3}' orders.csv",
    'The value becomes awk code: quotes in it break the program or run commands (system()).') + mistake("grep '\"ip\"' servers.json | cut -d'\"' -f4",
    "jq -r '.servers[].ip' servers.json",
    'grep/cut depend on line breaks and key order; jq parses the real structure.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Which tool for which job</h2>
''' + table(['Job', 'Bash loop', 'sed', 'awk', 'jq'], [
    ['Replace text in a file', 'awkward', '<b>best</b>', 'possible', '—'],
    ['Delete / insert lines', 'awkward', '<b>best</b>', 'possible', '—'],
    ['Sum / group columns', 'slow', 'no', '<b>best</b>', 'for JSON'],
    ['Reports with printf', 'ok, small data', 'no', '<b>best</b>', 'ok'],
    ['JSON', 'no', 'no', 'no', '<b>only choice</b>'],
    ['Complex logic per line', '<b>good</b>', 'no', 'good', 'good (JSON)'],
    ['Million-line files', 'too slow', 'fast', 'fast', 'fast'],
], minw=560) + table(['Passing a value', 'How', 'Unsafe form'], [
    ['into sed', 'escape <code>\\ / &amp;</code> (and regex chars in patterns), or <code>|</code> delimiter', '<code>"s/x/$v/"</code> with raw $v'],
    ['into awk', '<code>-v v="$v"</code> or <code>ENVIRON["v"]</code>', '<code>"…$v…"</code> in the program'],
    ['into jq (string)', '<code>--arg v "$v"</code> → <code>$v</code>', '<code>".name == \\"$v\\""</code>'],
    ['into jq (number/JSON)', '<code>--argjson n 5</code>', 'string concatenation'],
    ['out of jq to shell', '<code>-r</code>, <code>@sh</code>, <code>@tsv</code>', 'parsing printed JSON'],
], minw=520) + qc('Which tool for “total amount per city” on a 2 GB CSV?', 'awk (one pass, fast); a Bash loop would take very long.') + '''
</section>
'''

ESC = r'''sed_escape() {   # make any text safe as a sed replacement (delimiter |)
  printf '%s' "$1" | sed -e 's/[\\|&]/\\&/g'
}'''
SSE = SS + "\ncat > bin/sedesc.sh <<'EOF'\n" + ESC + "\nEOF"

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>sed in place, awk with -v, jq with --arg</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops/data</code>: <code>app.conf</code> (key = value), <code>orders.csv</code> (6 orders) and <code>servers.json</code> (4 servers). jq 1.7.1 is installed; the sed is GNU sed.</p>
''' + cmdcard_u(['changing configs from scripts', 'deploy steps'], ['editing JSON or YAML with sed'])(
    'sed', "sed -i.bak 's|^key = .*|key = new|' file · diff", 'edit a file in place',
    'An anchored substitution changes exactly one setting: <code>^listen_port = .*</code> matches the whole line. <code>-i.bak</code> rewrites the file and keeps the original as <code>app.conf.bak</code>; <code>diff</code> shows what changed. Using <code>|</code> as the delimiter means slashes in paths need no escaping.',
    "sed -i.bak \"s|^log_dir = .*|log_dir = $dir|\" app.conf", 'change',
    [('-i.bak', 'in place + backup', 'safe'),
     ("s|a|b|", 'other delimiter', 'paths'),
     ('^key = .*', 'whole line', 'anchored'),
     ('-n …p', 'print matches', 'check first'),
     ('/^#/d', 'delete comments', 'cleanup'),
     ("-i ''", 'macOS form', 'portability')],
    dict(setup=SS, cmd="cd ~/ops/data\nport=9090; dir=/srv/logs/orders\nsed -i.bak -e \"s|^listen_port = .*|listen_port = $port|\" -e \"s|^log_dir = .*|log_dir = $dir|\" app.conf\ndiff app.conf.bak app.conf\necho \"exit of diff: $? (1 = files differ)\"", note='Two settings changed in one pass; the backup is the old file.', expect='any'),
    [('devops', [
        dict(situation='The puzzle: / in the value breaks s/…/…/.', setup=SS, cmd="cd ~/ops/data; dir=/srv/logs/orders; sed \"s/^log_dir = .*/log_dir = $dir/\" app.conf; echo \"exit $?\"", why='The value’s slashes end the command. Use | or escape.', expect='any'),
        dict(situation='Escape any value for a replacement.', setup=SSE, cmd="cd ~/ops/data; source ../bin/sedesc.sh\nv='R&D | team\\\\a'; sed \"s|^db_host = .*|db_host = $(sed_escape \"$v\")|\" app.conf | grep db_host", why='\\, | and & are escaped; the value lands exactly as written.')]),
    ],
    anat=anatomy([('sed', 'cmd', 'stream editor'), ('-i.bak', 'opt', 'in place, backup'), ("'s|^port = .*|port = 9090|'", 'arg', 's|pattern|replacement|'), ('app.conf', 'arg', 'file')], 'Anchor with ^ so only the right line changes.')
) + cmdcard_u(['sums, counts, reports'], ['putting $var inside the awk program'])(
    'awk', "awk -F, -v c=\"$city\" '…c…' · ENVIRON · -f file.awk", 'pass variables into awk',
    '<code>-v name="$value"</code> creates an awk variable before the program runs; inside, use <code>name</code> without <code>$</code>. The value is data, so quotes or <code>system()</code> in it do nothing. Longer programs go into a heredoc or a <code>.awk</code> file run with <code>-f</code>.',
    "awk -F, -v c=\"$city\" -v min=\"$min\" 'NR > 1 && $2 == c && $3 >= min {n++; s += $3} END {print n, s}' orders.csv", 'safe',
    [('-v name=val', 'variable', 'before BEGIN'),
     ('-F,', 'field separator', 'CSV'),
     ('ENVIRON["X"]', 'raw env value', 'no escapes'),
     ('BEGIN / END', 'before / after input', 'set-up, totals'),
     ('-f prog.awk', 'program file', 'long logic'),
     ('printf', 'formatted output', 'reports')],
    dict(setup=SS, cmd="cd ~/ops/data\nfor city in Pune Mumbai; do\n  awk -F, -v c=\"$city\" 'NR > 1 && $2 == c && $4 == \"paid\" {n++; s += $3} END {printf \"%-7s %d paid orders, total %d\\n\", c, n, s}' orders.csv\ndone", note='The same program for every city: only the -v value changes.'),
    [('sec', [
        dict(situation='The puzzle: a value pasted into awk code runs commands.', setup=SS, cmd="cd ~/ops/data; city='x\" || system(\"touch HACKED\") || \"'\nawk -F, \"\\$2 == \\\"$city\\\" {s+=\\$3} END {print s+0}\" orders.csv; ls HACKED 2>/dev/null && echo 'pasted value RAN code: HACKED exists'; rm -f HACKED\nawk -F, -v c=\"$city\" '$2 == c {s+=$3} END {print s+0}' orders.csv; ls HACKED 2>/dev/null || echo 'with -v: just an unknown city, nothing ran'", why='-v keeps the value as data.')]),
     ('data', [
        dict(situation='A longer program in a heredoc.', setup=SS, cmd="cd ~/ops/data; awk -F, -f /dev/stdin orders.csv <<'AWK'\nNR == 1 { next }\n{ total[$2] += $3; count[$4]++ }\nEND {\n  for (c in total) printf \"%-7s %5d\\n\", c, total[c] | \"sort\"\n  close(\"sort\")\n  for (s in count) printf \"status %-9s %d\\n\", s, count[s] | \"sort\"\n}\nAWK", why='Readable, multi-line, still one command.')]),
    ]
) + cmdcard_u(['API answers, cloud CLIs, k8s output'], ['grep, sed or cut on JSON'])(
    'jq', "jq '.field' · '.[]' · select · map · -r · length", 'read JSON with jq',
    'A jq filter walks the JSON: <code>.region</code> picks a field, <code>.servers[]</code> iterates an array, <code>|</code> pipes values on, <code>select(cond)</code> keeps matches, <code>map(f)</code> transforms arrays, <code>length</code> counts. <code>-r</code> prints strings without quotes, ready for the shell.',
    "jq -r '.servers[] | select(.cpu > 80) | .name' servers.json", 'safe',
    [('.key', 'field', 'object'),
     ('.[] / .arr[]', 'each element', 'arrays'),
     ('select(.x > 1)', 'filter', 'conditions'),
     ('map(.name)', 'transform array', 'lists'),
     ('-r', 'raw strings', 'for shell'),
     ('length · keys', 'count · keys', 'inspect')],
    dict(setup=SS, cmd="cd ~/ops/data\njq -r '.region' servers.json\njq -r '.servers[].name' servers.json | paste -sd' '\njq -r '.servers[] | select(.cpu > 80) | \"\\(.name) is at \\(.cpu)% CPU\"' servers.json\njq '[.servers[] | select(.env == \"prod\")] | length' servers.json\njq -c '.servers | map({name, tags})' servers.json", note='String interpolation \\( ) builds messages; -c prints compact JSON on one line.'),
    [('sys', [
        dict(situation='The puzzle: grep breaks on one-line JSON.', setup=SS, cmd="cd ~/ops/data; jq -c . servers.json > one-line.json\necho \"grep finds: $(grep '\"name\"' one-line.json | cut -d'\"' -f4)\"\necho \"jq finds:   $(jq -r '.servers[].name' one-line.json | paste -sd' ')\"", why='Same data, different layout: grep/cut returns garbage, jq does not care.')]),
    ]
) + cmdcard_u(['filters with values from the script', 'building API requests'], ['building jq programs with string concatenation'])(
    'jqargs', "--arg · --argjson · -n · @csv · @tsv · -e", 'variables in and out of jq',
    '<code>--arg name "$v"</code> makes <code>$name</code> a string inside jq; <code>--argjson n 80</code> a number or JSON value. <code>jq -n</code> builds new JSON from arguments with correct escaping. On the way out, <code>@tsv</code>/<code>@csv</code> format rows for <code>read</code> or a spreadsheet, and <code>-e</code> sets the exit status from the result.',
    "jq -r --arg e \"$env\" --argjson max 80 '.servers[] | select(.env == $e and .cpu < $max) | .name' servers.json", 'safe',
    [('--arg x "$v"', 'string $x', 'filters'),
     ('--argjson n 5', 'number $n', 'comparisons'),
     ('-n', 'no input', 'build JSON'),
     ('@tsv / @csv', 'row output', 'read / Excel'),
     ('-e', 'false/null → exit 1', 'if jq -e …'),
     ('--slurpfile', 'file as $var', 'joins')],
    dict(setup=SS, cmd="cd ~/ops/data\nenv=prod; max=80\njq -r --arg e \"$env\" --argjson max \"$max\" '.servers[] | select(.env == $e and .cpu < $max) | .name' servers.json\necho '--- rows for a while-read loop:'\njq -r '.servers[] | [.name, .ip, .cpu] | @tsv' servers.json | while IFS=$'\\t' read -r n ip cpu; do echo \"$n ($ip): ${cpu}%\"; done\necho '--- build a request body safely:'\nnote='said \"call after 6\"'; jq -n --arg host web02 --arg note \"$note\" --argjson cpu 91 '{host: $host, cpu: $cpu, note: $note}'", note='The note’s quotes are escaped by jq; building that JSON with echo would have produced invalid JSON.'),
    [('devops', [
        dict(situation='jq -e in an if: is any server over 90%?', setup=SS, cmd="cd ~/ops/data; if jq -e 'any(.servers[]; .cpu > 90)' servers.json > /dev/null; then echo 'ALERT: a server is above 90% CPU'; fi", why='-e turns true/false into an exit status.'),
        dict(situation='Edit JSON safely (jq + temp + mv).', setup=SS, cmd="cd ~/ops/data; t=$(mktemp ./.json.XXXXXX); jq --arg n web02 '(.servers[] | select(.name == $n) | .cpu) = 50' servers.json > \"$t\" && mv -- \"$t\" servers.json; jq -r '.servers[] | \"\\(.name) \\(.cpu)\"' servers.json | grep web02", why='Lesson 2.3’s atomic pattern around jq.')]),
    ]
) + cmdcard_u(['any automated edit'], ['trusting an edit you did not check'])(
    'verify', 'diff · grep -c · jq empty · cmp', 'check before you replace',
    'After an automated change, prove it did what you meant: <code>diff</code> against the backup, count the changed lines, validate JSON with <code>jq empty</code>, and refuse to continue if the count is not what you expected.',
    "n=$(diff app.conf.bak app.conf | grep -c '^>'); (( n == 1 )) || die \"expected 1 change, got $n\"", 'safe',
    [('diff a.bak a', 'what changed', 'review'),
     ("grep -c '^>'", 'count new lines', 'expected?'),
     ('jq empty f.json', 'valid JSON?', 'exit 0/5'),
     ('sed -n …p', 'preview a match', 'before -i'),
     ('cmp -s', 'identical?', 'no-op edits'),
     ('mv .bak back', 'undo', 'restore')],
    dict(setup=SS, cmd="cd ~/ops/data\nsed -n 's|^feature_x = .*|feature_x = on|p' app.conf\nsed -i.bak 's|^feature_x = .*|feature_x = on|' app.conf\nn=$(diff app.conf.bak app.conf | grep -c '^>'); echo \"changed lines: $n\"\nsed -i.bak 's|^no_such_key = .*|x|' app.conf; cmp -s app.conf.bak app.conf && echo 'second edit changed nothing: key missing, stop the deploy'\njq empty servers.json && echo 'servers.json is valid JSON'\nprintf '{\"a\": 1,}' > bad.json; jq empty bad.json 2>&1 | head -1; echo \"jq exit: ${PIPESTATUS[0]}\"", note='sed -n …p previews; cmp catches an edit that silently matched nothing.', expect='any'),
    [('sys', [
        dict(situation='Undo an edit with the backup.', setup=SS, cmd="cd ~/ops/data; sed -i.bak 's|^db_host = .*|db_host = WRONG|' app.conf; mv -- app.conf.bak app.conf; grep db_host app.conf", why='The .bak is your undo.')]),
    ]
) + undo('Edits by tools are fast; so are mistakes. Keep the way back:', [
    ('sed changed the wrong lines:', '<code>mv app.conf.bak app.conf</code>; next time anchor the pattern and preview with <code>sed -n …p</code>.'),
    ('No backup:', 'restore from git or backups; always use <code>-i.bak</code> on files that matter.'),
    ('jq wrote empty output over the file:', 'never redirect jq into the same file; write to a temp file and mv only if jq succeeded.'),
    ('A value ran as code:', 'switch to <code>-v</code>/<code>--arg</code>; check what ran.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(setup=SS, cmd="cd ~/ops/data && jq '.servers[] | .name' servers.json > servers.json; wc -c servers.json", meaning='The shell empties servers.json (the > redirect) before jq reads it: the data is gone.', fix='jq … f > tmp && mv tmp f.'),
    dict(setup=SS, cmd="cd ~/ops/data && jq '.servers[].nmae' servers.json", meaning='A misspelled key gives null, not an error.', fix='Check spelling; use -e or // "default" (.nmae // "missing").'),
    dict(cmd="awk -v city 'BEGIN{print city}'", meaning='-v needs name=value; a bare name is an “improper assignment”.', fix='awk -v city="$city" …'),
]) + qc('Why must jq output never be redirected straight back into its input file?', 'The shell truncates the file before jq reads it; the data is lost.') + '''
'''
cards = cards + '</section>\n'

def jqw(k):
    o = t(180, 18, ".servers[] | select(.cpu > 80) | .name", 9.0, 'ink2', bold=True)
    rows = [('.servers', 'the array of 4 objects', 'blue'), ('[]', 'one object at a time', 'green'), ('select(.cpu > 80)', 'only web02 (91) passes', 'amber'), ('.name', '"web02" → -r → web02', 'violet')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
see_cmds = [["$ jq '.servers' …", ('[ {web01…}, {web02…}, … ]', 'out')], ["$ jq '.servers[]' …", ('{web01…} {web02…} …', 'out')], ['| select(.cpu > 80)', ('{"name": "web02", "cpu": 91 …}', 'out')], ['| .name  (-r)', ('web02', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@laptop: ~/ops/data', prompt='$', size=7.0) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['field.', 'iterate.', 'filter.', 'pick.'])]
two = anim_two('jq, one step at a time', 'Behind the screen: a pipeline of values',
               'A terminal grows a jq filter step by step until only web02 remains.', 'Rows show what each part of the filter produces.', see, [jqw(k) for k in range(4)],
               ['field.', 'iterate.', 'select.', 'name.'], ['.servers', '[]', 'select', '.name'])

def inj(k):
    o = t(180, 18, 'city = x" || system("touch HACKED") || "', 8.6, 'ink2', bold=True)
    o += label_box(14, 36, 160, 50, ['pasted into code', ['"…$city…"', 'program changed', 'system() runs', 'HACKED created'][k]], ['amber', 'red', 'red', 'red'][k], 8)
    o += label_box(186, 36, 160, 50, ['awk -v c="$city"', ['value only', 'program unchanged', '$2 == c is false', 'nothing runs'][k]], 'green', 8)
    o += t(180, 112, ['same value, two ways', 'left: the quotes end the string', 'left: awk executes the command', 'right: data stays data'][k], 9.2, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Code injection vs -v',
              'Why values must be passed as data.', 'injection', 'Two boxes: pasted into the program vs passed with -v.', [inj(k) for k in range(4)],
              ['value.', 'quotes.', 'runs.', 'safe.'], hid='scenario-inject')

dx = dissect('Layer by layer: a value’s trip into another tool',
    'Each layer has a real command from our build machine.', [
    dict(key='shell', name='Shell variable', sub='$city', why='Your data.', how='Quoted "$city".', impl='One word.', used='Arguments.',
         cmd="city='New Delhi'; printf '[%s]\\n' \"$city\""),
    dict(key='arg', name='As an argument', sub='-v / --arg', why='Separate from code.', how='argv element.', impl='Tool-defined.', used='awk, jq.',
         cmd="city='New Delhi'; awk -v c=\"$city\" 'BEGIN{print \"awk got [\" c \"]\"}'; jq -rn --arg c \"$city\" '\"jq got [\\($c)]\"'"),
    dict(key='code', name='Inside the program', sub='only escaped', why='sed has no variables.', how='Escape special chars.', impl='sed_escape.', used='sed.',
         setup=SSE, cmd="cd ~/ops/data; source ../bin/sedesc.sh; printf '%s\\n' 'a/b & c|d' | while IFS= read -r v; do echo \"escaped for sed: $(sed_escape \"$v\")\"; done"),
], hint='Variable → argument → program text. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A jq pipeline, and why -v matters</h2>
''' + two + s1 + dx + qc('Inside jq, how do you refer to a value passed with --arg name "$v"?', 'As $name.') + '''
</section>
'''

VAR = variations('Eighteen more sed, awk and jq calls from scripts. All were really run on our build machine.', [
    ('sed', [
        dict(title='Toggle a feature flag', setup=SS, cmd="cd ~/ops/data; sed -i 's|^feature_x = off|feature_x = on|' app.conf; grep feature_x app.conf", why='Anchored, exact.'),
        dict(title='Add a line after a match', setup=SS, cmd="cd ~/ops/data; sed -i '/^db_host/a db_port = 5432' app.conf; sed -n '/^db_/p' app.conf", why='a = append.'),
        dict(title='Delete comment and blank lines (to stdout)', setup=SS, cmd="cd ~/ops/data; sed -e '/^#/d' -e '/^$/d' app.conf", why='Clean view.'),
        dict(title='Only lines 2–3', setup=SS, cmd="cd ~/ops/data; sed -n '2,3p' app.conf", why='Address ranges.'),
        dict(title='Set or add a key (idempotent)', setup=SS, cmd="cd ~/ops/data; set_key(){ grep -q \"^$1 = \" app.conf && sed -i \"s|^$1 = .*|$1 = $2|\" app.conf || echo \"$1 = $2\" >> app.conf; }; set_key timeout 30; set_key timeout 45; grep timeout app.conf", why='Runs twice, one line.'),
    ]),
    ('awk', [
        dict(title='Several -v values', setup=SS, cmd="cd ~/ops/data; awk -F, -v s=paid -v min=500 'NR>1 && $4==s && $3>=min {print $1, $2, $3}' orders.csv", why='Numbers and strings.'),
        dict(title='ENVIRON for raw values', cmd="export PATTERN='C:\\temp'; awk 'BEGIN{print \"-v would turn \\\\t into a tab; ENVIRON keeps:\", ENVIRON[\"PATTERN\"]}'", why='No escape processing.'),
        dict(title='awk to shell variables', setup=SS, cmd="cd ~/ops/data; read -r n total < <(awk -F, 'NR>1 && $4==\"paid\" {n++; s+=$3} END{print n, s}' orders.csv); echo \"n=$n total=$total\"", why='read the awk result.'),
        dict(title='Percent of total', setup=SS, cmd="cd ~/ops/data; awk -F, 'NR>1 {t+=$3; c[$2]+=$3} END {for (k in c) printf \"%-7s %5.1f%%\\n\", k, 100*c[k]/t}' orders.csv | sort", why='Two passes in one: totals in END.'),
        dict(title='awk program in a file', setup=SS, cmd="cd ~/ops/data; printf 'BEGIN{FS=\",\"} NR>1 {s[$4]++} END{for (k in s) print k, s[k]}\\n' > status.awk; awk -f status.awk orders.csv | sort", why='-f for reusable programs.'),
    ]),
    ('jq', [
        dict(title='Count by environment', setup=SS, cmd="cd ~/ops/data; jq -r '.servers | group_by(.env)[] | \"\\(.[0].env) \\(length)\"' servers.json", why='group_by.'),
        dict(title='Average CPU', setup=SS, cmd="cd ~/ops/data; jq '[.servers[].cpu] | add / length' servers.json", why='add / length.'),
        dict(title='Servers with a tag', setup=SS, cmd="cd ~/ops/data; jq -r --arg t web '.servers[] | select(.tags | index($t)) | .name' servers.json", why='index on an array.'),
        dict(title='Default for a missing key', setup=SS, cmd="cd ~/ops/data; jq -r '.servers[] | \"\\(.name) owner=\\(.owner // \"unknown\")\"' servers.json | head -2", why='// default.'),
        dict(title='CSV for Excel', setup=SS, cmd="cd ~/ops/data; jq -r '[\"name\",\"ip\",\"cpu\"], (.servers[] | [.name, .ip, .cpu]) | @csv' servers.json", why='@csv quotes strings.'),
        dict(title='Shell-safe values with @sh', setup=SS, cmd="cd ~/ops/data; eval \"names=($(jq -r '[.servers[].name] | @sh' servers.json))\"; echo \"${#names[@]} names, first ${names[0]}\"", why='@sh quotes for eval into an array.'),
        dict(title='Keys of an object', setup=SS, cmd="cd ~/ops/data; jq -c '.servers[0] | keys' servers.json", why='Explore unknown JSON.'),
        dict(title='Merge two JSON values', cmd="jq -n --argjson a '{\"x\":1}' --argjson b '{\"y\":2}' '$a + $b' -c", why='Object +.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>sed, awk and jq at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['deploy', 'config'], 'blue', 8.6), '1. Deploy scripts',
              'sed -i.bak sets ports, hosts and versions in config files per environment, with a diff check before restarting services.', ['template', '*sed -i', 'diff']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cloud', 'CLI'], 'green', 8.6), '2. Cloud automation',
    'aws, az, gcloud and kubectl print JSON; jq picks instance IDs, IPs and states for the next command.', ['aws … --output json', '*jq -r', 'next step']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['reports', 'awk'], 'amber', 8.6), '3. Daily reports',
    'awk totals sales per city or errors per service from large files in seconds.', ['CSV/logs', '*awk -v', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['APIs', 'webhooks'], 'violet', 8.6), '4. Calling APIs',
    'jq -n --arg builds request bodies for Slack, Jira or internal APIs; curl sends them.', ['variables', '*jq -n', 'curl -d']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['k8s', 'kubectl'], 'red', 8.6), '5. Kubernetes checks',
    'kubectl get pods -o json | jq selects pods that are not Running or have restarts.', ['kubectl -o json', '*select', 'alert']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful calls. All really run on our build machine.', [
    dict(level='b', title='Change one setting', scenario='Deploy.', setup=SS, cmd="cd ~/ops/data; sed -i.bak 's|^listen_port = .*|listen_port = 9090|' app.conf; grep listen_port app.conf", explain='Anchored s|||.'),
    dict(level='b', title='All server IPs', scenario='Inventory.', setup=SS, cmd="cd ~/ops/data; jq -r '.servers[].ip' servers.json", explain='.[] + -r.'),
    dict(level='i', title='Total for a city', scenario='Sales.', setup=SS, cmd="cd ~/ops/data; city=Pune; awk -F, -v c=\"$city\" '$2==c && $4==\"paid\" {s+=$3} END{print s}' orders.csv", explain='-v.'),
    dict(level='i', title='Busy servers', scenario='Monitoring.', setup=SS, cmd="cd ~/ops/data; jq -r --argjson m 70 '.servers[] | select(.cpu > $m) | .name' servers.json", explain='--argjson for numbers.'),
    dict(level='a', title='JSON payload from variables', scenario='Alert API.', cmd="host=web02; msg='CPU \"high\" (91%)'; jq -cn --arg h \"$host\" --arg m \"$msg\" '{text: \"\\($h): \\($m)\"}'", explain='Escaping done by jq.'),
], extra=build_up('a deploy step with all three tools', 'Riya prepares a release: config change, a check of the data, and a JSON note for the team chat.', SS, [
    ("cd ~/ops/data; port=9090; sed -i.bak \"s|^listen_port = .*|listen_port = $port|\" app.conf; diff app.conf.bak app.conf | grep '^>'", '1. sed: set the port, show the change.'),
    ("cd ~/ops/data; awk -F, -v s=failed 'NR>1 && $4==s {n++} END{print n+0, \"failed orders\"}' orders.csv", '2. awk: a sanity number.'),
    ("cd ~/ops/data; jq -r --arg e prod '[.servers[] | select(.env==$e) | .name] | join(\" \")' servers.json", '3. jq: which servers get the release.'),
    ("cd ~/ops/data; hosts=$(jq -r --arg e prod '[.servers[] | select(.env==$e) | .name] | join(\",\")' servers.json); jq -cn --arg h \"$hosts\" --argjson p 9090 '{event: \"release\", port: $p, hosts: ($h | split(\",\"))}'", '4. jq -n: the chat message, valid JSON.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Edit a config line', 'sed -i.bak', 'In place, backup.', 'Rewriting with echo.'),
    ('Column maths', 'awk', 'Fast, one pass.', 'Bash loops on big files.'),
    ('JSON', 'jq', 'Real parser.', 'grep/sed/cut.'),
    ('Value into awk', '-v', 'Data, not code.', '"…$v…" in program.'),
    ('Value into jq', '--arg / --argjson', 'Escaped.', 'String building.'),
    ('Value into sed', 'escape + | delimiter', 'Correct.', 'Raw $v.'),
]) + keys('Handy forms.', [
    ("sed -i.bak 's|^k = .*|k = v|' f", 'set a key', 'backup'),
    ("sed -n 's|…|…|p' f", 'preview', 'before -i'),
    ("awk -F, -v c=\"$c\" '$2==c'", 'filter', 'safe'),
    ("jq -r '.a[] | select(.x > 1) | .n'", 'filter JSON', 'raw'),
    ("jq -r --arg v \"$v\" '…$v…'", 'string in', 'safe'),
    ('jq … f > t && mv t f', 'edit JSON', 'atomic'),
]) + scriptit('release-check.sh', 'Set a config value safely, verify exactly one line changed, summarise orders with awk, and build a JSON status message with jq: all values passed as data.',
'''#!/usr/bin/env bash
set -euo pipefail
printf 'listen_port = 8080\\nlog_dir = /var/log/app\\n' > app.conf
printf 'id,city,amount\\n1,Pune,450\\n2,Delhi,800\\n' > orders.csv
die() { echo "release-check: $*" >&2; exit 1; }

new_dir='/srv/logs/R&D app'                     # slashes, & and a space
esc=$(printf '%s' "$new_dir" | sed 's/[\\\\|&]/\\\\&/g')
sed -i.bak "s|^log_dir = .*|log_dir = $esc|" app.conf
n=$(diff app.conf.bak app.conf | grep -c '^>' || true)
(( n == 1 )) || die "expected 1 changed line, got $n"
grep '^log_dir' app.conf

total=$(awk -F, 'NR > 1 {s += $3} END {print s}' orders.csv)
jq -cn --arg dir "$new_dir" --argjson total "$total" '{status: "ok", log_dir: $dir, orders_total: $total}' ''',
'<p>The & and slashes reach the file exactly; the JSON is valid even with special characters.</p>', expect='any') + puzzle_answer('All three bugs pasted a value into another program’s source text. <b>1.</b> sed: the slashes in <code>/srv/logs/orders</code> end the <code>s/…/…/</code> command early (“unknown option to `s’”). Use <code>s|…|…|</code> and escape <code>\\</code>, <code>|</code> and <code>&amp;</code>. <b>2.</b> awk: the quotes in the “city” closed the awk string and <code>system("touch HACKED")</code> became code. Pass it with <code>awk -v c="$city"</code>. <b>3.</b> JSON: grep and cut depend on the layout (one key per line); the same data on one line breaks them. Parse it with jq: <code>jq -r \'.servers[].name\'</code>.') + qc('Which jq option turns a true/false result into an exit status?', '-e.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-parsing-csv-logs-and-config-files/">Lesson 2.2</a> (formats) and Linux Lessons <a href="../../../linux/06-text-processing/04-sed-the-stream-editor/">6.4</a> (sed) and <a href="../../../linux/06-text-processing/05-awk-fields-patterns-and-reports/">6.5</a> (awk).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
