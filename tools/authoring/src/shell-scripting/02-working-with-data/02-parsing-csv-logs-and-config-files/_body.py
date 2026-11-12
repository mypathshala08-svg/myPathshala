import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# Real-world formats: quoted CSV, an nginx-style access log, a key=value config and an INI file
SS = r'''rm -rf ~/ops; mkdir -p ~/ops/data ~/ops/bin; cd ~/ops
cat > data/customers.csv <<'EOF'
id,name,city,note
1,Asha Rao,Pune,regular
2,"Kumar, Ravi","New Delhi, India","said ""call after 6"""
3,Meera Iyer,Mumbai,
4,"Das, Anil",Kolkata,"VIP"
EOF
cat > data/access.log <<'EOF'
10.0.0.5 - - [12/Nov/2026:09:15:01 +0530] "GET /orders HTTP/1.1" 200 5120 "-" "curl/8.5"
10.0.0.9 - - [12/Nov/2026:09:15:03 +0530] "POST /login HTTP/1.1" 401 310 "-" "Mozilla/5.0 (X11; Linux)"
10.0.0.5 - - [12/Nov/2026:09:16:10 +0530] "GET /orders/17 HTTP/1.1" 200 980 "-" "curl/8.5"
10.0.0.7 - - [12/Nov/2026:09:17:44 +0530] "GET /reports?month=11 HTTP/1.1" 500 120 "-" "python-requests/2.31"
10.0.0.9 - - [12/Nov/2026:09:18:02 +0530] "POST /login HTTP/1.1" 401 310 "-" "Mozilla/5.0 (X11; Linux)"
10.0.0.9 - - [12/Nov/2026:09:18:05 +0530] "POST /login HTTP/1.1" 200 742 "-" "Mozilla/5.0 (X11; Linux)"
EOF
cat > data/app.conf <<'EOF'
# app.conf - key = value, comments allowed
db_host = db01.internal
db_port=5432
   log_level = INFO   
backup_dir = /srv/backups/orders data
retries = 3
EOF
cat > data/evil.conf <<'EOF'
db_host=db01; touch HACKED
EOF
cat > data/site.ini <<'EOF'
[database]
host = db01
port = 5432

[cache]
host = redis01
port = 6379
EOF'''

HOOK = hook('Real data never arrives as neat space-separated columns. The sales team’s CSV has <code>"Kumar, Ravi"</code> with a comma inside quotes; the web server log has brackets, quotes and spaces inside fields; and the app’s config file has <code>key = value</code> with spaces, comments and a path containing a space. Riya’s <code>IFS=,</code> loop from Lesson 2.1 cuts “Kumar, Ravi” in two. This lesson parses each format properly: CSV with a real quote-aware parser, logs with <code>[[ =~ ]]</code> and <code>BASH_REMATCH</code>, config files <b>without</b> the dangerous <code>source</code>, and INI sections, and shows when to hand the job to awk, Python or jq.',
    ['parse CSV with quoted fields, commas and doubled quotes correctly, in Bash and with python3 -c csv',
     'pull fields out of log lines with [[ =~ ]] and BASH_REMATCH, and summarise them with awk',
     'read key=value and INI config files safely into variables or associative arrays, without source',
     'validate parsed values and choose the right tool for each format and size'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three formats, one broken loop'),
    ('decide', 'Which tool?', 2, 'the quick chart'),
    ('definition', 'Parsing', 5, 'simple meaning + 4 depths'),
    ('types', 'Formats compared', 4, 'CSV, logs, config'),
    ('commands', 'Step by step', 15, 'CSV, regex, config, INI'),
    ('animation', 'See it happen', 4, 'a CSV line parsed'),
    ('run', 'Run on your PC', 3, 'real files'),
    ('lab', 'Practice lab', 8, 'a log report'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('The data is… → parse it with', [
    ('simple CSV, no quotes', 'IFS=, read -r', 'Lesson 2.1'),
    ('CSV with quotes and commas', "a quote-aware parser · python3 -c 'import csv'", 'never plain IFS'),
    ('log lines', '[[ $line =~ regex ]] + BASH_REMATCH', 'or awk'),
    ('millions of log lines', 'awk / grep -c / sort | uniq -c', 'speed'),
    ('key=value config', 'while IFS== read -r k v (never source)', 'safe'),
    ('INI with [sections]', 'loop with a current-section variable', 'or crudini'),
    ('JSON', 'jq (Lesson 2.4)', 'never grep'),
])

cmap = concept_map(
    [('2.1', 'Reading line by line', 'while read'), ('L:6.6', 'Regular expressions', 'patterns'), ('L:12.13', 'Associative arrays', 'key → value')],
    ['why IFS=, breaks real CSV', 'a quote-aware CSV parser', 'python3 csv as a helper', '[[ =~ ]] and BASH_REMATCH', 'log summaries with awk', 'safe key=value config (no source)', 'INI sections'],
    [('2.4', 'sed, awk, jq', 'the heavy tools'), ('2.3', 'Temp files', 'intermediate results'), ('4.2', 'Log monitor', 'parse live logs'), ('3.1', 'Error handling', 'bad input')],
    'Each format has its trap; parse it properly or let a real parser do it.')

sc = (term(20, 14, 316, 156, ['$ IFS=, read -r id name city <<< \'2,"Kumar, Ravi",…\'', ('name=["Kumar]  city=[ Ravi"]', 'err'), '$ csv_split \'2,"Kumar, Ravi","New Delhi, India"\'', ('[2] [Kumar, Ravi] [New Delhi, India]', 'out'), '$ [[ $l =~ \\"([A-Z]+)\\ ([^ ]+) ]]', ('method=POST path=/login status=401', 'acc')], title='riya@laptop: ~/ops', prompt='$', size=6.0, step=19)
      + t(352, 36, 'Each format, its trap:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['CSV: quoted commas', 'logs: spaces in fields', 'config: never source', 'INI: sections', 'JSON: use jq'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three formats, one broken loop</h2>
  <div class="story">
''' + puzzle('<code>customers.csv</code> has 4 customers, but Riya’s <code>IFS=,</code> loop reports Ravi’s city as <code> Ravi"</code>. Her log script splits on spaces and thinks the browser of a login attempt is <code>(X11;</code>. And the team’s old deploy script reads its config with <code>source app.conf</code>: someone puts <code>db_host=db01; touch HACKED</code> in a config file, and a file called HACKED appears on the server. Three formats, three ways to misread them. What is the right reader for each?') + '''
    <p class="narration">In <code>~/ops</code> (every run in this lesson is real).</p>
''' + scene('A terminal: IFS=, splits "Kumar, Ravi" wrongly; a quote-aware csv_split gives the right fields; a regex pulls method, path and status from a log line.', sc,
            'Parse the <tspan font-weight="700" class="s-acc">format</tspan>, not just the separator.') + '''
K> So CSV is not “values separated by commas”?
A> It is, until a value contains a comma, a quote or a newline. Then the value is wrapped in double quotes, and a quote inside is written twice. A parser has to know those rules (RFC 4180). <code>IFS=,</code> does not.
R> And configs: why is source dangerous? It is so convenient.
A> <code>source</code> does not read a config, it <b>runs</b> it as Bash code. Anything in the file executes with the script’s permissions. Reading it line by line and accepting only <code>key=value</code> is just as easy and safe.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="The CSV line 2,&quot;Kumar, Ravi&quot;,&quot;New Delhi, India&quot; split wrongly by IFS into five pieces and correctly by a quote-aware parser into three fields.">'
       + t(320, 20, '2,"Kumar, Ravi","New Delhi, India"', 10, 'ink2', bold=True)
       + t(110, 50, 'IFS=,  (wrong)', 9, 'red', bold=True)
       + ''.join(label_box(14 + i * 62, 60, 56, 30, [s], 'red', 7.6) for i, s in enumerate(['2', '"Kumar', ' Ravi"', '"New Delhi', ' India"']))
       + t(110, 120, 'quote-aware parser', 9, 'green', bold=True)
       + ''.join(label_box(14 + x, 130, w, 30, [s], 'green', 8) for x, w, s in [(0, 50, '2'), (56, 110, 'Kumar, Ravi'), (172, 140, 'New Delhi, India')])
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Parsing at four depths', [
    ('v', 'No jargon: addresses on envelopes', '      <p>“Kumar, Ravi” is one name even though it has a comma. Humans know because of the quotes; a parser must know the same rule.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>csv_split "$line"</code> (our 10-line function) or <code>python3 -c 'import csv,sys; …'</code></li>
        <li><code>[[ $line =~ $re ]] &amp;&amp; echo "${BASH_REMATCH[1]}"</code></li>
        <li><code>while IFS='=' read -r key value; do …; done &lt; app.conf</code></li>
        <li><code>awk '{print $9}' access.log | sort | uniq -c</code></li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li>CSV (RFC 4180): fields with commas, quotes or newlines are quoted; a quote inside is doubled (<code>""</code>). Excel files often add a BOM and CRLF.</li>
        <li>Put a regex in a variable (<code>re='…'</code>) and write <code>[[ $s =~ $re ]]</code> unquoted: quoting the right side makes it a plain string.</li>
        <li>Config: trim spaces, skip comments and blanks, accept only known keys or <code>^[a-z_]+$</code> names, store in an associative array.</li>
        <li>Validate after parsing: ports are numbers, paths exist, levels are in a list.</li>
      </ul>'''),
    ('a', 'Behind the screen: formats and grammars', '''      <ul>
        <li>A format is a small grammar. Regular expressions handle “regular” formats (one log line); CSV with quotes needs a tiny state machine (inside/outside quotes), which is why a single regex or IFS split fails.</li>
        <li><code>BASH_REMATCH[0]</code> is the whole match, <code>[1]</code>… the groups; Bash uses POSIX ERE (no <code>\\d</code>, no lazy <code>*?</code>, no lookahead): write <code>[0-9]</code> and <code>[^"]*</code>.</li>
        <li>For big files, the cost is per line in Bash (built-ins, no fork) vs per file in awk; awk is typically 10–100× faster on large logs.</li>
        <li><code>source</code>/<code>.</code> parses the file as shell grammar: <code>;</code>, <code>$( )</code> and backticks all run. Even <code>declare "$line"</code> can be abused; a strict <code>key=value</code> pattern plus assigning into an array is the safe design.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Parsing data files</h2>
''' + def_block(
    '<b>Parsing</b> means reading text in a known format and turning it into separate, meaningful values according to that format’s rules. In shell scripts the common formats are <b>CSV</b> (comma-separated values with quoting rules), <b>log lines</b> (a fixed layout of fields that may themselves contain spaces), and <b>configuration files</b> (<code>key=value</code> lines or INI files with <code>[sections]</code>).',
    'Know the format’s rules, then extract the values; never guess with a plain split.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('RFC 4180', 'The CSV rules.'),
    ('Quoted field', '"Kumar, Ravi".'),
    ('Escaped quote', '"" inside quotes.'),
    ('=~', 'Bash regex match.'),
    ('BASH_REMATCH', 'Captured groups.'),
    ('Combined log', 'nginx/Apache line format.'),
    ('INI', '[section] key = value.'),
    ('source', 'Runs a file as Bash code.'),
]) + '\n' + names('Where the names come from.', [
    ('CSV', 'comma-separated values', 'Used since the 1970s; RFC 4180 in 2005.'),
    ('TSV', 'tab-separated values', 'No quoting needed usually.'),
    ('INI', 'initialization file', 'Windows 3.x .ini files.'),
    ('regex', 'regular expression', 'Kleene, 1951.'),
    ('BASH_REMATCH', 'regex match array', 'Bash 3.0.'),
    ('combined log', 'common log + referer + agent', 'Apache.'),
    ('BOM', 'byte order mark', 'EF BB BF from Excel.'),
    ('parse', 'from Latin pars, part', 'Split into parts.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Quoted CSV', 'parser, not <code>IFS=,</code>'),
    ('Regex test', '<code>[[ $s =~ $re ]]</code>'),
    ('Groups', '<code>${BASH_REMATCH[1]}</code>'),
    ('Config', '<code>IFS== read -r k v</code>'),
    ('Never', '<code>source untrusted.conf</code>'),
    ('Big logs', '<code>awk</code>'),
]) + '\n' + lv + didyou('Excel saves “CSV UTF-8” with three invisible bytes at the very start (the BOM, <code>EF BB BF</code>). Your first column header then is not <code>id</code> but <code>\\ufeffid</code>, and <code>[[ $h == id ]]</code> fails for no visible reason. <code>sed \'1s/^\\xEF\\xBB\\xBF//\'</code> removes it.') + '''
EXAM> “Why is source config.conf dangerous?” → source executes the file as shell code, so any command in it (after ;, in $( ) or backticks) runs with the script’s permissions; read key=value lines and validate them instead.
''' + qc('Why does [[ $s =~ "$re" ]] not work as a regex?', 'Quoting the right-hand side makes Bash match it as a literal string.') + mistake('while IFS=, read -r id name city; do … done < customers.csv',
    'csv_split "$line" (quote-aware) or python3 csv for anything with quotes',
    'A quoted comma becomes a field separator: every later column shifts.') + mistake('source /etc/myapp/app.conf',
    'while IFS== read -r k v; do … validate k and v … done < app.conf',
    'Any command in the config file runs, with the script’s permissions (often root).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Formats and the right reader</h2>
''' + table(['Format', 'Example', 'Trap', 'Reader in Bash', 'Better tool'], [
    ['Simple CSV', '<code>1,Pune,450</code>', 'none', '<code>IFS=, read -r</code>', 'awk -F,'],
    ['Quoted CSV', '<code>2,"Kumar, Ravi"</code>', 'commas, "" in quotes', 'quote-aware loop', 'python3 csv, mlr, csvkit'],
    ['TSV', '<code>a b⇥c</code>', 'spaces in fields', "<code>IFS=$'\\t' read -r</code>", 'awk -F\'\\t\''],
    ['Log line', '<code>… "GET /x HTTP/1.1" 200 …</code>', 'spaces in quoted parts', '<code>[[ =~ ]]</code> + BASH_REMATCH', 'awk, goaccess'],
    ['key=value', '<code>port = 5432</code>', 'spaces, comments, code', '<code>IFS== read -r k v</code>', '—'],
    ['INI', '<code>[cache] host = r1</code>', 'same key in many sections', 'section variable', 'crudini, python configparser'],
    ['JSON', '<code>{"port": 5432}</code>', 'nesting, escaping', 'do not', 'jq (Lesson 2.4)'],
], minw=700) + qc('Which format can you safely split with IFS=, ?', 'Only CSV that never contains quotes, commas or newlines inside fields.') + '''
</section>
'''

CSVF = r'''csv_split() {   # print each field of one CSV line on its own line (RFC 4180, no embedded newlines)
  local line=$1 field re='^("(([^"]|"")*)"|([^,]*))(,|$)'
  while [[ -n $line ]]; do
    [[ $line =~ $re ]] || return 1
    if [[ -n ${BASH_REMATCH[1]} && ${BASH_REMATCH[1]:0:1} == '"' ]]; then field=${BASH_REMATCH[2]//\"\"/\"}; else field=${BASH_REMATCH[4]}; fi
    printf '%s\n' "$field"
    line=${line:${#BASH_REMATCH[0]}}
    [[ ${BASH_REMATCH[5]} == , && -z $line ]] && printf '\n'
  done
}'''
SSF = SS + "\ncat > bin/csv.sh <<'EOF'\n" + CSVF + "\nEOF"

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>CSV, logs, key=value and INI, really parsed</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops/data</code>: <code>customers.csv</code> (quoted fields, an embedded comma and doubled quotes, an empty last field), <code>access.log</code> (6 lines in nginx “combined” format), <code>app.conf</code>, <code>evil.conf</code> and <code>site.ini</code>. The Bash CSV parser is in <code>bin/csv.sh</code>.</p>
''' + cmdcard_u(['CSV from Excel, CRMs, exports'], ['IFS=, on quoted data'])(
    'csv', 'csv_split (regex state machine) · python3 csv', 'CSV with quotes',
    'A quote-aware parser reads one field at a time: either a quoted field <code>"…"</code> (where <code>""</code> means one quote) or an unquoted one up to the next comma. Our <code>csv_split</code> does this with one regex in a loop and prints each field on its own line, so <code>mapfile</code> can collect them. For big or messy files, call Python’s csv module.',
    'mapfile -t f < <(csv_split "$line"); echo "${f[1]}"', 'safe',
    [('"…"', 'quoted field', 'commas inside'),
     ('""', 'one quote', 'inside quotes'),
     ('empty field', 'a,,c', 'kept'),
     ('mapfile -t f < <(…)', 'fields → array', 'per line'),
     ('python3 -c csv', 'robust', 'newlines in fields'),
     ("sed '1s/^\\xEF\\xBB\\xBF//'", 'strip BOM', 'Excel')],
    dict(setup=SSF, cmd="cd ~/ops/data; source ../bin/csv.sh\necho '--- IFS=, (wrong):'\nsed -n 3p customers.csv | { IFS=, read -r id name city note; echo \"name=[$name] city=[$city]\"; }\necho '--- csv_split (right):'\n{ read -r _; while IFS= read -r line; do mapfile -t f < <(csv_split \"$line\"); printf '%s | %-12s | %-17s | %s\\n' \"${f[@]}\"; done; } < customers.csv", note='Row 2 keeps its comma and its quotes; row 3’s empty note stays an empty field.'),
    [('data', [
        dict(situation='The same with Python’s csv module (one line).', setup=SSF, cmd="cd ~/ops/data; python3 -c 'import csv,sys\nfor r in list(csv.reader(sys.stdin))[1:]: print(\" | \".join(r))' < customers.csv", why='Handles every RFC 4180 case, including newlines inside quotes.'),
        dict(situation='Convert quoted CSV to TSV, then use plain read.', setup=SSF, cmd="cd ~/ops/data; python3 -c 'import csv,sys; w=csv.writer(sys.stdout, delimiter=\"\\t\", lineterminator=\"\\n\"); [w.writerow(r) for r in csv.reader(sys.stdin)]' < customers.csv > customers.tsv\nwhile IFS=$'\\t' read -r id name city note; do echo \"$id: $city\"; done < <(tail -n +2 customers.tsv)", why='Normalise once, then Lesson 2.1’s loop works.')]),
    ],
    anat=anatomy([('csv_split', 'cmd', 'our function'), ('"$line"', 'arg', 'one CSV line'), ('→ one field per line', 'opt', 'for mapfile')], 'Quote-aware: commas inside quotes are not separators.')
) + cmdcard_u(['log lines with a fixed layout'], ['splitting log lines on spaces'])(
    'regex', '[[ $line =~ $re ]] · BASH_REMATCH', 'log lines with a regex',
    'A regex with groups describes the whole line; <code>[[ $line =~ $re ]]</code> fills <code>BASH_REMATCH</code> with each group. Keep the regex in a variable and leave it unquoted in <code>[[ ]]</code>. Bash uses POSIX extended regex: <code>[0-9]</code> not <code>\\d</code>, <code>[^"]*</code> for “anything up to a quote”.',
    're=\'^([0-9.]+) .* \\[([^]]+)\\] "([A-Z]+) ([^ ]+) [^"]*" ([0-9]{3}) ([0-9]+)\'', 'safe',
    [('( … )', 'group → BASH_REMATCH[n]', 'capture'),
     ('[^"]*', 'up to a quote', 'quoted parts'),
     ('[^]]+', 'up to ]', 'timestamp'),
     ('[0-9]{3}', 'status', 'exactly 3'),
     ('re=… unquoted', 'in [[ =~ $re ]]', 'regex, not string'),
     ('${BASH_REMATCH[0]}', 'whole match', 'debug')],
    dict(setup=SS, cmd="cd ~/ops/data\nre='^([0-9.]+) [^ ]+ [^ ]+ \\[([^]]+)\\] \"([A-Z]+) ([^ ]+) [^\"]*\" ([0-9]{3}) ([0-9]+) \"[^\"]*\" \"([^\"]*)\"'\nwhile IFS= read -r l; do\n  [[ $l =~ $re ]] || { echo \"unparsed: $l\"; continue; }\n  printf '%-9s %-4s %-17s %s  %-22s\\n' \"${BASH_REMATCH[1]}\" \"${BASH_REMATCH[3]}\" \"${BASH_REMATCH[4]}\" \"${BASH_REMATCH[5]}\" \"${BASH_REMATCH[7]}\"\ndone < access.log", note='The user agent “Mozilla/5.0 (X11; Linux)” stays whole, spaces and all.'),
    [('sec', [
        dict(situation='Failed logins per IP (the 401s).', setup=SS, cmd="cd ~/ops/data; re='^([0-9.]+) .*\"POST /login [^\"]*\" 401 '; declare -A bad; while IFS= read -r l; do [[ $l =~ $re ]] && (( ++bad[${BASH_REMATCH[1]}] )); done < access.log; for ip in \"${!bad[@]}\"; do echo \"$ip: ${bad[$ip]} failed logins\"; done", why='A brute-force check in a few lines.')]),
    ]
) + cmdcard_u(['big logs, quick summaries'], ['complex quoting (use the regex)'])(
    'awk', "awk '{print $9}' · -F'\"' · sort | uniq -c", 'summaries with awk',
    'For counting and summing over many lines, awk is faster and shorter. In the combined format, field 9 is the status and field 10 the bytes when splitting on spaces; splitting on the quote character (<code>-F\'"\'</code>) gives the request as field 2 and the user agent as field 6.',
    "awk '{c[$9]++} END{for (s in c) print s, c[s]}' access.log", 'safe',
    [('$1', 'client IP', 'spaces'),
     ('$9', 'status', 'spaces'),
     ('$10', 'bytes', 'spaces'),
     ("-F'\"' $2", 'request', 'quotes'),
     ("-F'\"' $6", 'user agent', 'quotes'),
     ('sort | uniq -c', 'count', 'classic')],
    dict(setup=SS, cmd="cd ~/ops/data\nawk '{print $9}' access.log | sort | uniq -c\nawk '{bytes += $10} END {print \"total bytes:\", bytes}' access.log\nawk -F'\"' '{print $6}' access.log | sort | uniq -c | sort -rn", note='Same answers as the Bash regex, one line each.'),
    [('sys', [
        dict(situation='5xx errors with their paths.', setup=SS, cmd="cd ~/ops/data; awk '$9 ~ /^5/ {print $9, $7}' access.log", why='Server errors to investigate.')]),
    ]
) + cmdcard_u(['app configs, .env-style files'], ['source on files you do not fully control'])(
    'config', 'IFS== read -r k v · trim · validate · declare -A', 'key=value config, safely',
    'Read each line, skip comments and blanks, split at the <b>first</b> <code>=</code> (<code>IFS== read -r k v</code> puts everything after it in <code>v</code>), trim spaces, accept only keys matching <code>^[a-z_]+$</code>, and store in an associative array. Nothing in the file is ever executed.',
    'declare -A cfg; while IFS== read -r k v; do …; cfg[$k]=$v; done < app.conf', 'safe',
    [('IFS== read -r k v', 'split at first =', 'v keeps later ='),
     ('${k//[[:space:]]/}', 'trim key', 'spaces'),
     ('trim value', 'leading/trailing', 'see code'),
     ('^[a-z_]+$', 'allowed keys', 'reject junk'),
     ('cfg[$k]=$v', 'store', 'associative'),
     ('${cfg[port]:-5432}', 'default', 'missing key')],
    dict(setup=SS, cmd="cd ~/ops/data\ndeclare -A cfg\nwhile IFS='=' read -r k v || [[ -n $k ]]; do\n  [[ $k =~ ^[[:space:]]*(#|$) ]] && continue\n  k=${k//[[:space:]]/}; v=${v#\"${v%%[![:space:]]*}\"}; v=${v%\"${v##*[![:space:]]}\"}\n  [[ $k =~ ^[a-z_]+$ ]] || { echo \"skip bad key [$k]\" >&2; continue; }\n  cfg[$k]=$v\ndone < app.conf\nfor k in db_host db_port log_level backup_dir retries; do printf '%-10s = [%s]\\n' \"$k\" \"${cfg[$k]}\"; done\n[[ ${cfg[db_port]} =~ ^[0-9]+$ ]] && echo 'db_port is a number: ok'", note='Spaces around = and at line ends are trimmed; the path with a space is kept whole.'),
    [('sec', [
        dict(situation='Why not source: the evil config.', setup=SS, cmd="cd ~/ops/data; ( source evil.conf ); ls HACKED 2>/dev/null && echo 'source RAN the command: HACKED exists'; rm -f HACKED\nwhile IFS== read -r k v; do echo \"safe read: key=[$k] value=[$v] (nothing executed)\"; done < evil.conf; ls HACKED 2>/dev/null || echo 'no HACKED file'", why='The same file: source executes touch; read just stores text.')]),
    ]
) + cmdcard_u(['INI files', 'php.ini, my.cnf, git config style'], ['one flat dictionary for sectioned data'])(
    'ini', '[section] · current section · cfg[section.key]', 'INI files with sections',
    'Keep a <code>section</code> variable: when a line matches <code>^\\[(.+)\\]$</code>, update it; for <code>key = value</code> lines store <code>cfg[$section.$key]</code>. Then <code>cfg[cache.host]</code> and <code>cfg[database.host]</code> no longer clash.',
    'cfg[$section.$key]=$value', 'safe',
    [('^\\[(.+)\\]$', 'section line', 'BASH_REMATCH[1]'),
     ('section.key', 'unique key', 'no clash'),
     ('; or #', 'comments', 'skip'),
     ('crudini --get f s k', 'ready-made tool', 'if installed'),
     ('git config -f f s.k', 'reads INI too', 'handy'),
     ('python configparser', 'robust', 'complex files')],
    dict(setup=SS, cmd="cd ~/ops/data\ndeclare -A ini; section=''\nwhile IFS= read -r line || [[ -n $line ]]; do\n  line=${line%%[;#]*}\n  if [[ $line =~ ^[[:space:]]*\\[([^]]+)\\] ]]; then section=${BASH_REMATCH[1]}; continue; fi\n  [[ $line =~ ^[[:space:]]*([A-Za-z_]+)[[:space:]]*=[[:space:]]*(.*[^[:space:]])[[:space:]]*$ ]] || continue\n  ini[$section.${BASH_REMATCH[1]}]=${BASH_REMATCH[2]}\ndone < site.ini\nfor k in $(printf '%s\\n' \"${!ini[@]}\" | sort); do echo \"$k = ${ini[$k]}\"; done", note='Two hosts, two ports, no clash.'),
    [('devops', [
        dict(situation='git can read INI files too.', setup=SS, cmd="cd ~/ops/data; git config -f site.ini --get cache.port; git config -f site.ini --get-regexp '.*host'", why='A parser you already have installed.')]),
    ]
) + undo('Parsing only reads; the risk is acting on wrongly parsed values. Protect the actions:', [
    ('Columns shifted:', 'you split quoted CSV with IFS: switch to a parser, rerun.'),
    ('A config executed code:', 'remove <code>source</code>; check what ran (logs, new files), rotate any exposed secrets.'),
    ('Garbage values used:', 'validate after parsing (numbers, lists, paths) and <code>die</code> before acting.'),
    ('Unparsed lines ignored silently:', 'count them and log a warning, as the regex card does.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(cmd="re='[0-9]+'; [[ 'abc123' =~ \"$re\" ]] && echo match || echo 'no match: quoted pattern is a literal string'", meaning='The right side was quoted, so Bash looked for the text [0-9]+.', fix='[[ $s =~ $re ]] without quotes.'),
    dict(cmd="[[ 'port=5432' =~ \\d+ ]] && echo match || echo 'no match: \\d is not POSIX ERE'", meaning='Bash regex has no \\d.', fix='[0-9]+ or [[:digit:]]+'),
    dict(setup=SS, cmd="cd ~/ops/data && printf '\\xEF\\xBB\\xBFid,name\\n1,x\\n' > bom.csv && IFS=, read -r h _ < bom.csv && [[ $h == id ]] && echo ok || echo \"first header is not 'id' (${#h} chars): BOM\"", meaning='Excel’s invisible BOM is glued to the first header.', fix="sed -i '1s/^\\xEF\\xBB\\xBF//' bom.csv"),
]) + qc('What does ${BASH_REMATCH[1]} hold after a successful [[ =~ ]]?', 'The text matched by the first ( ) group.') + '''
'''
cards = cards + '</section>\n'

def cs(k):
    o = t(180, 18, '2,"Kumar, Ravi","New Delhi, India"', 9.2, 'ink2', bold=True)
    rows = [('field 1', 'unquoted up to , → 2', 'blue'), ('field 2', 'quoted: "Kumar, Ravi" → Kumar, Ravi', 'green'), ('field 3', 'quoted: comma inside kept', 'green'), ('end', 'line empty → stop', 'violet')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 7.8)
    return o
see_cmds = [['regex: "…" or [^,]*', ('2', 'out')], ['quoted branch', ('Kumar, Ravi', 'out')], ['quoted branch', ('New Delhi, India', 'out')], ['line empty', ('3 fields', 'acc')]]
see = [term(14, 16, 332, 116, c, title='csv_split', prompt='>', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['1.', '2.', '3.', 'done.'])]
two = anim_two('A CSV line, field by field', 'Behind the screen: quoted or not?',
               'csv_split takes one field per regex match.', 'Rows show each field and which branch matched.', see, [cs(k) for k in range(4)],
               ['1.', '2.', '3.', 'done.'], ['f1', 'f2', 'f3', 'end'])

def lg(k):
    o = t(180, 18, '"POST /login HTTP/1.1" 401', 9.6, 'ink2', bold=True)
    parts = [('IP', '10.0.0.9', 'blue'), ('method', 'POST', 'green'), ('path', '/login', 'amber'), ('status', '401', 'red')]
    for i in range(k + 1):
        a, b, c = parts[i]
        o += label_box(14 + i * 84, 40, 78, 46, [a, b], c, 8.2)
    o += t(180, 112, f'BASH_REMATCH[{[1, 3, 4, 5][k]}]', 9.4, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Groups become BASH_REMATCH',
              'Each ( ) in the regex fills one slot.', 'regex groups', 'Boxes for IP, method, path, status.', [lg(k) for k in range(4)],
              ['IP.', 'method.', 'path.', 'status.'], hid='scenario-regex')

dx = dissect('Layer by layer: from text to trusted values',
    'Each layer has a real command from our build machine.', [
    dict(key='raw', name='Raw text', sub='bytes', why='What arrives.', how='Encoding, CRLF, BOM.', impl='od / file.', used='First check.',
         setup=SS, cmd="cd ~/ops/data; file customers.csv access.log app.conf | sed 's/, with very long lines//'"),
    dict(key='parse', name='Parse', sub='format rules', why='Correct fields.', how='Parser / regex.', impl='csv_split, =~.', used='Every script.',
         setup=SSF, cmd="cd ~/ops/data; source ../bin/csv.sh; csv_split '2,\"Kumar, Ravi\",\"New Delhi, India\",\"said \"\"call after 6\"\"\"' | nl"),
    dict(key='check', name='Validate', sub='before use', why='Trust.', how='Patterns, lists.', impl='[[ ]].', used='Before acting.',
         cmd="for p in 5432 54x2 99999; do if [[ $p =~ ^[0-9]+$ ]] && (( p <= 65535 )); then echo \"$p: valid port\"; else echo \"$p: rejected\"; fi; done"),
], hint='Raw → parsed → validated. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A CSV line parsed, and regex groups</h2>
''' + two + s1 + dx + qc('How is a quote written inside a quoted CSV field?', 'Doubled: "" stands for one ".') + '''
</section>
'''

VAR = variations('Sixteen more parsing patterns. All were really run on our build machine.', [
    ('CSV', [
        dict(title='Only one column, quote-aware', setup=SSF, cmd="cd ~/ops/data; source ../bin/csv.sh; tail -n +2 customers.csv | while IFS= read -r l; do mapfile -t f < <(csv_split \"$l\"); echo \"${f[2]}\"; done", why='City column, commas intact.'),
        dict(title='Count fields per line (sanity check)', setup=SSF, cmd="cd ~/ops/data; source ../bin/csv.sh; while IFS= read -r l; do csv_split \"$l\" | wc -l; done < customers.csv | sort | uniq -c", why='Every row should have 4.'),
        dict(title='Write a CSV field safely', cmd="csv_q(){ local s=${1//\\\"/\\\"\\\"}; [[ $s == *[,\\\"]* ]] && s=\\\"$s\\\"; printf '%s' \"$s\"; }; printf '%s,%s\\n' \"$(csv_q 3)\" \"$(csv_q 'Rao, Asha \"AR\"')\"", why='Quote and double the quotes when writing.'),
        dict(title='Python: column by name', setup=SS, cmd="cd ~/ops/data; python3 -c 'import csv,sys\nfor r in csv.DictReader(sys.stdin): print(r[\"name\"], \"->\", r[\"city\"])' < customers.csv", why='DictReader uses the header.'),
    ]),
    ('Logs', [
        dict(title='Requests per minute', setup=SS, cmd="cd ~/ops/data; awk -F'[][]' '{print substr($2,1,17)}' access.log | uniq -c", why='Timestamp to the minute.'),
        dict(title='Top paths', setup=SS, cmd="cd ~/ops/data; awk '{print $7}' access.log | sed 's/?.*//' | sort | uniq -c | sort -rn", why='Drop the query string.'),
        dict(title='Only lines with status ≥ 400', setup=SS, cmd="cd ~/ops/data; awk '$9 >= 400 {print $1, $9, $7}' access.log", why='Numeric compare in awk.'),
        dict(title='Query parameter from a URL', cmd="url='/reports?month=11&year=2026'; [[ $url =~ [?\\&]month=([0-9]+) ]] && echo \"month=${BASH_REMATCH[1]}\"", why='Regex on one value.'),
        dict(title='Parse the timestamp with date', cmd="ts='12/Nov/2026:09:15:01 +0530'; date -d \"$(sed 's|/| |g; s|:| |' <<< \"$ts\")\" '+%F %T'", why='Turn log time into a sortable one.'),
    ]),
    ('Config', [
        dict(title='Default for a missing key', setup=SS, cmd="cd ~/ops/data; declare -A c; while IFS== read -r k v; do k=${k//[[:space:]]/}; [[ $k == timeout ]] && c[timeout]=$v; done < app.conf; echo \"timeout=${c[timeout]:-30}\"", why=':- default.'),
        dict(title='Required keys check', setup=SS, cmd="cd ~/ops/data; keys=$(sed -n 's/^[[:space:]]*\\([a-z_]*\\)[[:space:]]*=.*/\\1/p' app.conf); for r in db_host db_port api_key; do grep -qx \"$r\" <<< \"$keys\" || echo \"missing required key: $r\"; done", why='Fail early.'),
        dict(title='Allowed values', setup=SS, cmd="cd ~/ops/data; lvl=$(sed -n 's/^[[:space:]]*log_level[[:space:]]*=[[:space:]]*\\([A-Z]*\\).*/\\1/p' app.conf); case $lvl in DEBUG|INFO|WARN|ERROR) echo \"log_level $lvl ok\";; *) echo \"bad log_level $lvl\";; esac", why='Whitelist.'),
        dict(title='.env file with export-free read', cmd="printf 'API_URL=https://api.example.com/v1?x=1\\nTOKEN=abc=def\\n' > .env; while IFS== read -r k v; do printf '%s -> %s\\n' \"$k\" \"$v\"; done < .env", why='Only the first = splits: values may contain =.'),
    ]),
    ('INI', [
        dict(title='One value with git config', setup=SS, cmd="cd ~/ops/data; git config -f site.ini database.host", why='No custom code.'),
        dict(title='List sections', setup=SS, cmd="cd ~/ops/data; sed -n 's/^\\[\\(.*\\)\\]$/\\1/p' site.ini", why='sed for a quick look.'),
        dict(title='Python configparser', setup=SS, cmd="cd ~/ops/data; python3 -c 'import configparser as c; p=c.ConfigParser(); p.read(\"site.ini\"); print(p[\"cache\"][\"port\"])'", why='Robust for complex INI.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Parsing at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['CSV', 'imports'], 'blue', 8.6), '1. Business data imports',
              'Exports from CRMs and Excel always contain quoted commas; a quote-aware step (or Python) prevents shifted columns in the database.', ['export', '*parse', 'load']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['logs', 'security'], 'red', 8.6), '2. Security checks',
    'Counting 401s per IP in access logs finds brute-force attempts; fail2ban works the same way with regexes.', ['access.log', '*regex', 'ban']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['config', 'deploy'], 'green', 8.6), '3. Deploy configuration',
    'Deploy scripts read per-environment key=value files and validate every value before touching servers.', ['app.conf', '*validate', 'deploy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['INI', 'MySQL'], 'amber', 8.6), '4. Server configs',
    'my.cnf, php.ini and systemd units are INI-like; scripts read a section key before changing anything.', ['my.cnf', '*section.key', 'check']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['reports', 'daily'], 'violet', 8.6), '5. Daily reports',
    'awk summaries of access logs (status codes, top paths, bytes) are mailed every morning.', ['log', '*awk', 'mail']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful parsers. All really run on our build machine.', [
    dict(level='b', title='Status code counts', scenario='Is the site OK?', setup=SS, cmd="cd ~/ops/data; awk '{print $9}' access.log | sort | uniq -c", explain='Field 9.'),
    dict(level='b', title='Second CSV column, quote-aware', scenario='Names.', setup=SS, cmd="cd ~/ops/data; python3 -c 'import csv,sys; [print(r[1]) for r in list(csv.reader(sys.stdin))[1:]]' < customers.csv", explain='csv module.'),
    dict(level='i', title='One config value', scenario='Which DB?', setup=SS, cmd="cd ~/ops/data; sed -n 's/^[[:space:]]*db_host[[:space:]]*=[[:space:]]*//p' app.conf", explain='sed with a capture-free strip.'),
    dict(level='i', title='IPs with failed logins', scenario='Security.', setup=SS, cmd="cd ~/ops/data; awk '$9 == 401 {print $1}' access.log | sort | uniq -c", explain='Numeric field test.'),
    dict(level='a', title='Biggest responses', scenario='Bandwidth.', setup=SS, cmd="cd ~/ops/data; awk '{print $10, $7}' access.log | sort -rn | head -2", explain='Bytes are field 10.'),
], extra=build_up('a login report from access.log', 'Riya builds a security summary step by step.', SS, [
    ("cd ~/ops/data; grep -c 'POST /login' access.log", '1. How many login attempts?'),
    ("cd ~/ops/data; re='^([0-9.]+) .*\"POST /login [^\"]*\" ([0-9]{3}) '; while IFS= read -r l; do [[ $l =~ $re ]] && echo \"${BASH_REMATCH[1]} ${BASH_REMATCH[2]}\"; done < access.log", '2. IP and status for each.'),
    ("cd ~/ops/data; re='^([0-9.]+) .*\"POST /login [^\"]*\" 401 '; declare -A f; while IFS= read -r l; do [[ $l =~ $re ]] && (( ++f[${BASH_REMATCH[1]}] )); done < access.log; for ip in \"${!f[@]}\"; do echo \"$ip ${f[$ip]}\"; done", '3. Failures per IP.'),
    ("cd ~/ops/data; awk '$7 == \"/login\" && $9 == 401 {f[$1]++} END {for (ip in f) if (f[ip] >= 2) print \"ALERT\", ip, f[ip], \"failed logins\"}' access.log", '4. The same in awk, with an alert threshold.'),
], cumulative=False)) + VAR + which('Choosing the right parser.', [
    ('Simple CSV', 'IFS=, read -r', 'Built-in.', 'Quoted data.'),
    ('Quoted CSV', 'csv_split / python3 csv', 'Correct.', 'IFS=,.'),
    ('Log lines', '[[ =~ ]] or awk', 'Fields with spaces.', 'cut -d" ".'),
    ('Big logs', 'awk', 'Fast.', 'Bash loops.'),
    ('Config', 'IFS== read + validate', 'Safe.', 'source.'),
    ('JSON', 'jq', 'Real parser.', 'grep/sed.'),
]) + keys('Handy forms.', [
    ("re='…'; [[ $s =~ $re ]]", 'regex', 'unquoted'),
    ('${BASH_REMATCH[1]}', 'group 1', 'after match'),
    ("python3 -c 'import csv,sys …'", 'CSV', 'robust'),
    ("awk -F'\"' '{print $2}'", 'log request', 'quotes'),
    ('IFS== read -r k v', 'config', 'safe'),
    ('git config -f f.ini s.k', 'INI', 'ready-made'),
]) + scriptit('parse-config.sh', 'Load a key=value config into an associative array safely, with comment and blank-line handling, trimming, a key whitelist, defaults and validation, and stop with exit 2 on any bad value.',
'''#!/usr/bin/env bash
set -euo pipefail
printf '# demo\\nhost = db01\\nport= 5432\\nmode = fast\\nrm -rf / ; oops\\n' > demo.conf
declare -A cfg=([host]=localhost [port]=5432 [mode]=safe)       # defaults
allowed='^(host|port|mode)$'

while IFS='=' read -r k v || [[ -n $k ]]; do
  [[ $k =~ ^[[:space:]]*(#|$) ]] && continue
  k=${k//[[:space:]]/}
  v=${v#"${v%%[![:space:]]*}"}; v=${v%"${v##*[![:space:]]}"}
  if [[ ! $k =~ $allowed ]]; then echo "ignored unknown line: [$k]" >&2; continue; fi
  cfg[$k]=$v
done < demo.conf

[[ ${cfg[port]} =~ ^[0-9]+$ ]] || { echo "bad port: ${cfg[port]}" >&2; exit 2; }
case ${cfg[mode]} in safe|fast) ;; *) echo "bad mode: ${cfg[mode]}" >&2; exit 2 ;; esac
for k in host port mode; do echo "$k=${cfg[$k]}"; done''',
'<p>The “rm -rf / ; oops” line is just ignored text: nothing in the file ever runs.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>IFS=,</code> does not know CSV quoting, so the comma inside <code>"Kumar, Ravi"</code> splits the field and every later column shifts. Use a quote-aware parser (our <code>csv_split</code>) or <code>python3 -c \'import csv …\'</code>. <b>2.</b> In the combined log format the user agent is a quoted field that contains spaces; splitting on spaces cuts it into pieces. Match the whole line with a regex (<code>"([^"]*)"</code>) or split on quotes in awk (<code>-F\'"\'</code>, field 6). <b>3.</b> <code>source</code> runs the config as Bash code, so <code>; touch HACKED</code> executed. Read <code>key=value</code> lines with <code>IFS== read -r k v</code>, whitelist the keys and validate the values.') + qc('Which awk field is the HTTP status in the combined log format (space-split)?', '$9.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-reading-files-and-input-line-by-line/">Lesson 2.1</a> (while read, IFS) and <a href="../../../linux/06-text-processing/06-regular-expressions-with-grep-sed-and-awk-basic/">Linux Lesson 6.6</a> (regular expressions).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
