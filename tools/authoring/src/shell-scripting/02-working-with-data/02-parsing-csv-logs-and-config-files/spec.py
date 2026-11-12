import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)
_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index("SS = r'''") + 9
SS = _s[_i:_s.index("'''", _i)]

META = dict(
    module='02-working-with-data', lesson='02-parsing-csv-logs-and-config-files', n='2.2',
    module_label='Module 2 · Working with data',
    title='Parsing CSV, logs and config files in Bash',
    desc='Parse real data formats in Bash: CSV with quoted commas and doubled quotes (a quote-aware parser and python3 csv), Excel BOMs, log lines with [[ =~ ]] and BASH_REMATCH, awk summaries of nginx access logs, key=value configs read safely without source, and INI sections, with validation and every run real.',
    og_desc='Quote-aware CSV, BASH_REMATCH for logs, safe config parsing without source, and INI sections in Bash.',
    minutes=40, level='Intermediate',
    lead='Every format has a trap: quoted commas in CSV, spaces inside log fields, code hidden in configs. Parse the format, not just the separator.',
    chips=['Quote-aware CSV parser', 'Regex groups animated', 'Why source is dangerous', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """line='2,"Kumar, Ravi","New Delhi, India"'

echo '--- IFS=, (wrong)'
IFS=, read -r id name city <<< "$line"
echo "name=[$name] city=[$city]"

echo '--- regex groups on a log line'
log='10.0.0.9 - - [12/Nov/2026:09:15:03 +0530] "POST /login HTTP/1.1" 401 310'
re='^([0-9.]+) .*"([A-Z]+) ([^ ]+) [^"]*" ([0-9]{3})'
if [[ $log =~ $re ]]; then
  echo "ip=${BASH_REMATCH[1]} method=${BASH_REMATCH[2]} path=${BASH_REMATCH[3]} status=${BASH_REMATCH[4]}"
fi
"""

RUN = dict(
    heading='Split vs parse in your browser',
    intro='<p>IFS cuts the quoted name; a regex pulls exact fields from a log line.</p>',
    code=MAIN,
    anno=[('IFS=,', 'Knows nothing about quotes.'), ('[[ $log =~ $re ]]', 'Unquoted $re = regex.'), ('BASH_REMATCH', 'One slot per ( ) group.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Where did “Kumar, Ravi” go?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> match or not?',
             code="re='[0-9]+'\n[[ abc123 =~ \"$re\" ]] && echo match || echo 'no match'\n[[ abc123 =~ $re ]] && echo \"match: ${BASH_REMATCH[0]}\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> \\d is not POSIX. Use [0-9].',
             code="[[ 'port=5432' =~ =(\\d+) ]] && echo \"${BASH_REMATCH[1]}\" || echo 'no match'\n"),
        dict(label='4 · Your turn', hint='Read key=value lines without running them.',
             code="while IFS='=' read -r k v; do echo \"key=[$k] value=[$v]\"; done <<< $'host=db01\\ncmd=x; rm -rf /tmp/x'\n"),
        dict(label='5 · Challenge', hint='Get the month from a URL query.',
             code="url='/reports?month=11&year=2026'\n[[ $url =~ month=([0-9]+) ]] && echo \"${BASH_REMATCH[1]}\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Try the parsers on your own files. Outputs below are from our build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Status codes of your web server', cmd="sudo awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c", output='      3 200\n      2 401\n      1 500', note='Real output on our sample log.'),
        dict(title='2 · Quoted CSV with Python', cmd="python3 -c 'import csv,sys\nfor r in csv.reader(sys.stdin): print(r)' < customers.csv", output="['id', 'name', 'city', 'note']\n['1', 'Asha Rao', 'Pune', 'regular']\n['2', 'Kumar, Ravi', 'New Delhi, India', 'said \"call after 6\"']\n…", note='Real output (shortened).'),
        dict(title='3 · Miller for CSV', cmd="mlr --icsv --opprint cut -f name,city customers.csv", output='name        city\nAsha Rao    Pune\nKumar, Ravi New Delhi, India\n…', note='Typical; install the miller package.'),
        dict(title='4 · crudini for INI', cmd="crudini --get site.ini cache port", output='6379', note='Typical; install crudini.'),
    ],
)

TRACE = dict(
    heading='Safe config reading, line by line',
    intro='<p>The config is only read, never run.</p>',
    code='''printf 'port = 5432\\n# comment\\nmode=fast\\n' > c.conf
declare -A cfg
while IFS='=' read -r k v; do
  [[ $k == \\#* || -z $k ]] && continue
  k=${k// /}; v=${v# }
  cfg[$k]=$v
done < c.conf
echo "port=${cfg[port]} mode=${cfg[mode]}"
''',
    notes={3: 'Split at the first =.', 4: 'Skip comments.', 6: 'Store, do not run.'},
)

WORKED_INTRO = 'Three real files parsed properly.'
EXAMPLES = [
    dict(level='b', tag='Data', title='Total per city from a quoted CSV',
         problem='<p>Sum amounts per city when city names contain commas.</p>',
         inp='a quoted CSV', approach=['Normalise with python csv, then awk.'],
         code='''printf 'city,amount\\n"Delhi, NCR",500\\nPune,300\\n"Delhi, NCR",200\\n' > s.csv
python3 -c 'import csv,sys; w=csv.writer(sys.stdout, delimiter="\\t", lineterminator="\\n"); [w.writerow(r) for r in csv.reader(sys.stdin)]' < s.csv |
  awk -F'\\t' 'NR>1 {t[$1]+=$2} END {for (c in t) print c": "t[c]}' | sort
''', notes={2: 'CSV → TSV once.', 3: 'Then simple tab splitting.'}, tryit='Add a count per city.'),
    dict(level='i', tag='Ops', title='Response times from an app log',
         problem='<p>Find requests slower than 500 ms in lines like “GET /x took=812ms”.</p>',
         inp='log lines', approach=['Regex with a numeric group.'],
         code='''printf 'GET /a took=120ms\\nGET /b took=812ms\\nPOST /c took=640ms\\n' > app.log
re='^([A-Z]+) ([^ ]+) took=([0-9]+)ms$'
while IFS= read -r l; do
  [[ $l =~ $re ]] && (( BASH_REMATCH[3] > 500 )) && echo "SLOW ${BASH_REMATCH[1]} ${BASH_REMATCH[2]} ${BASH_REMATCH[3]}ms"
done < app.log
''', notes={4: 'Groups used as numbers.'}, tryit='Print the average time.'),
    dict(level='a', tag='Security', title='Reject a config with unknown keys',
         problem='<p>Fail (exit 2) when a config has a key outside the allowed list.</p>',
         inp='a config', approach=['Whitelist regex.'],
         code='''printf 'host=db01\\nport=5432\\npasword=x\\n' > c.conf
check() { local k v bad=0
  while IFS== read -r k v; do [[ $k =~ ^(host|port|password)$ ]] || { echo "unknown key: $k" >&2; bad=1; }; done < "$1"
  return $(( bad * 2 )); }
check c.conf; echo "exit $?"
''', notes={3: 'Typos like pasword are caught.'}, tryit='Also require host.', expect='any'),
]

QUIZ = mix([
    dict(q='Why does IFS=, break "Kumar, Ravi"?', options=['IFS ignores quotes', 'Bash bug', 'read -r', 'UTF-8'], answer=0, why='No quote rules.'),
    dict(q='In CSV a quote inside a quoted field is written as…', options=['\\"', '""', "''", '&quot;'], answer=1, why='Doubled.'),
    dict(q='After [[ $s =~ $re ]], group 1 is in…', options=['$1', 'BASH_REMATCH[1]', 'MATCH[1]', '$REPLY'], answer=1, why='BASH_REMATCH.'),
    dict(q='[[ $s =~ "$re" ]] treats re as…', options=['a regex', 'a literal string', 'a glob', 'an error'], answer=1, why='Quoted = literal.'),
    dict(q='Bash regex digit class:', options=['\\d', '[0-9]', '%d', '#'], answer=1, why='POSIX ERE.'),
    dict(q='source app.conf is risky because…', options=['slow', 'it executes the file', 'it needs root', 'it trims spaces'], answer=1, why='Runs code.'),
    dict(q='Status code in combined log, awk space-split:', options=['$7', '$8', '$9', '$10'], answer=2, why='$9.'),
    dict(q='Same key in two INI sections: store as…', options=['key', 'section.key', 'key.section', 'one wins'], answer=1, why='Unique.'),
])

REVISION = [
    'Plain IFS=, only works for CSV without quotes; quoted CSV needs a parser (csv_split, python3 csv, mlr).',
    'CSV rules: quote fields with commas/quotes/newlines; "" inside quotes is one quote; strip an Excel BOM.',
    "Logs: re='…' then [[ $l =~ $re ]] (unquoted); groups in BASH_REMATCH; POSIX ERE ([0-9], [^\"]*).",
    'Big logs: awk ($1 IP, $7 path, $9 status, $10 bytes; -F\'"\' for request and agent).',
    'Config: IFS== read -r k v, skip comments/blanks, trim, whitelist keys, validate values; never source.',
    'INI: track [section], store cfg[section.key]; git config -f or configparser also work.',
]

FAQ = [
    ('How do I parse a CSV file with quoted fields in Bash?', 'Use a quote-aware parser: a regex loop like csv_split, or python3 -c with the csv module, or Miller (mlr).'),
    ('What is BASH_REMATCH?', 'An array filled by [[ string =~ regex ]]: index 0 is the whole match, 1.. the groups.'),
    ('Why does my Bash regex not match \\d?', 'Bash uses POSIX extended regex; write [0-9] or [[:digit:]].'),
    ('Is it safe to source a config file?', 'Only if you fully trust its content: source executes it. Read key=value lines instead.'),
    ('How do I parse an nginx access log?', 'awk for counts ($9 status, $1 IP), or a full regex with BASH_REMATCH per line.'),
    ('How do I read an INI file in Bash?', 'Track the current [section] in a loop and store section.key; or use git config -f / crudini.'),
    ('How do I remove the BOM from a CSV?', "sed -i '1s/^\\xEF\\xBB\\xBF//' file.csv."),
]

PRACTICE_INTRO = 'Small parsing tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Regex group', stmt='Print 5432 from port=5432.', inp='a string', code="[[ port=5432 =~ =([0-9]+) ]] && echo ${BASH_REMATCH[1]}\n", explain='Group 1.'),
    dict(level='easy', title='Status field', stmt='Print the status from a combined-log line.', inp='a log line', code="echo '1.2.3.4 - - [x] \"GET / HTTP/1.1\" 404 9 \"-\" \"ua\"' | awk '{print $9}'\n", explain='404.'),
    dict(level='easy', title='Key and value', stmt='Split host=db01 at =.', inp='a line', code="IFS== read -r k v <<< host=db01; echo \"$k -> $v\"\n", explain='host -> db01.'),
    dict(level='medium', title='Value with =', stmt='Keep the whole value of TOKEN=a=b.', inp='a line', code="IFS== read -r k v <<< TOKEN=a=b; echo $v\n", explain='a=b.'),
    dict(level='medium', title='Quoted CSV', stmt='Print the second field of 1,"a, b",c with python csv.', inp='a CSV line', code="echo '1,\"a, b\",c' | python3 -c 'import csv,sys; print(next(csv.reader(sys.stdin))[1])'\n", explain='a, b.'),
    dict(level='medium', title='Section', stmt='Extract cache from [cache].', inp='a line', code="[[ '[cache]' =~ ^\\[(.+)\\]$ ]] && echo ${BASH_REMATCH[1]}\n", explain='cache.'),
    dict(level='business', title='Count 5xx', stmt='Count lines whose status starts with 5.', inp='statuses', code="printf '200\\n500\\n503\\n404\\n' | grep -c '^5'\n", explain='2.'),
    dict(level='business', title='Valid port', stmt='Check 70000 is not a valid port.', inp='a number', code="p=70000; [[ $p =~ ^[0-9]+$ ]] && (( p <= 65535 )) && echo ok || echo invalid\n", explain='invalid.'),
]

SCN_INTRO = 'Interview questions about parsing data in shell scripts.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Count status codes in an access log”', 'Common.', 'one line',
        '''<ul>
          <li>awk '{print $9}' access.log | sort | uniq -c</li>
          <li>$9 in the combined format.</li>
          <li>sort -rn for the biggest first.</li>
        </ul>''', 'grep for each code.') +
    scn('Service company', 'Junior', 'CSV import shifts columns', 'Excel export.', 'why?',
        '''<ol>
          <li>Quoted fields with commas split by IFS/cut.</li>
          <li>Use a CSV parser (python csv, mlr).</li>
          <li>Also strip the BOM and CRLF.</li>
        </ol>''', 'asking users to remove commas.') +
    scn('Product company', 'Mid-level', 'Config read with source', 'Security review.', 'risk + fix?',
        '''<ul>
          <li>source executes any code in the file.</li>
          <li>Parse key=value, whitelist keys, validate.</li>
          <li>Restrict file permissions.</li>
        </ul>''', 'adding a comment “do not edit”.') +
    scn('Data company', 'Senior', '200 GB of logs per day to summarise', 'Daily job.', 'approach?',
        '''<ul>
          <li>Not Bash loops: awk/grep in parallel, or Spark.</li>
          <li>Ship structured logs (JSON) to a log platform.</li>
          <li>Bash only orchestrates.</li>
        </ul>''', 'a bigger server for the Bash loop.')
) + interview([
    ('What does =~ do?', 'Regex match in [[ ]].'),
    ('BASH_REMATCH[0]?', 'Whole match.'),
    ('Why quote-aware CSV?', 'Commas inside quotes.'),
    ('awk -F\'"\' for logs?', 'Split on quotes to get request and agent.'),
    ('Why not source configs?', 'Executes code.'),
    ('BOM?', 'Invisible bytes from Excel at file start.'),
    ('Tool for CSV on the CLI?', 'mlr, csvkit, python csv.'),
], [
    ('LFCS', 'Text processing for files.'),
    ('RHCSA', 'Use regular expressions with grep and in scripts.'),
    ('CompTIA Linux+', 'Regex, awk, text parsing.'),
]) + distro('Helpful parsing tools per distribution.', [
    ('awk', 'mawk default', 'gawk', 'gawk', 'gawk'),
    ('Miller (mlr)', 'apt install miller', 'dnf install miller', 'zypper', 'pacman'),
    ('crudini', 'apt', 'dnf (EPEL)', 'pip', 'pip'),
    ('python3 csv', 'built in', 'built in', 'built in', 'built in'),
    ('Note', 'mawk: no FPAT', 'gawk FPAT for CSV', '-', '-'),
]) + teaser('2.3', 'Parsing creates intermediate files: TSV copies, filtered logs. Next: temporary files done right with mktemp, and trap so they are always cleaned up.')

CHEATSHEET = cheatsheet('Parsing', [
    ('CSV', [('csv_split "$line"', 'quote-aware'), ("python3 -c 'import csv'", 'robust'), ('""', 'one quote'), ("sed '1s/^\\xEF\\xBB\\xBF//'", 'BOM')]),
    ('Regex', [("re='…'", 'variable'), ('[[ $s =~ $re ]]', 'match'), ('${BASH_REMATCH[1]}', 'group'), ('[0-9] [^"]*', 'POSIX')]),
    ('Logs', [("awk '{print $9}'", 'status'), ('$1 $7 $10', 'IP path bytes'), ("-F'\"' $6", 'agent'), ('sort | uniq -c', 'count')]),
    ('Config', [('IFS== read -r k v', 'split'), ('whitelist keys', 'safe'), ('cfg[section.key]', 'INI'), ('never source', 'rule')]),
])

MINDMAP = mindmap('Parsing', [
    ('CSV', 'blue', ['quotes', '"" escape', 'BOM']),
    ('Regex', 'green', ['=~', 'BASH_REMATCH', 'POSIX ERE']),
    ('Logs', 'amber', ['combined', 'awk $9', 'agent']),
    ('Config', 'red', ['key=value', 'no source', 'validate']),
    ('INI', 'violet', ['[section]', 'section.key', 'git config']),
    ('Tools', 'acc', ['python csv', 'mlr', 'jq']),
])

LAB = lab('a log report', 'Build the lab (it creates <code>~/lab22/access.log</code> and <code>~/lab22/report.conf</code>), write <code>~/lab22/report.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab22; mkdir -p ~/lab22 && cd ~/lab22
cat > access.log <<'EOF'
10.0.0.5 - - [12/Nov/2026:09:15:01 +0530] "GET /orders HTTP/1.1" 200 5120 "-" "curl/8.5"
10.0.0.9 - - [12/Nov/2026:09:15:03 +0530] "POST /login HTTP/1.1" 401 310 "-" "Mozilla/5.0 (X11; Linux)"
10.0.0.9 - - [12/Nov/2026:09:15:05 +0530] "POST /login HTTP/1.1" 401 310 "-" "Mozilla/5.0 (X11; Linux)"
10.0.0.7 - - [12/Nov/2026:09:17:44 +0530] "GET /reports HTTP/1.1" 500 120 "-" "python-requests/2.31"
10.0.0.9 - - [12/Nov/2026:09:18:02 +0530] "POST /login HTTP/1.1" 401 310 "-" "Mozilla/5.0 (X11; Linux)"
EOF
printf '# report settings\\nthreshold = 3\\nlog_file=access.log ; touch PWNED\\n' > report.conf''',
    tasks=['<code>report.sh</code> reads <code>report.conf</code> <b>without source</b> (no file called PWNED may ever appear) and takes <code>threshold</code> from it.',
           'It prints one line per HTTP status in the form <code>STATUS COUNT</code>, sorted by status: <code>200 1</code>, <code>401 3</code>, <code>500 1</code>.',
           'It prints <code>ALERT IP N</code> for every IP with at least <code>threshold</code> failed logins (status 401): here <code>ALERT 10.0.0.9 3</code>.',
           'If <code>threshold</code> is not a whole number, it exits <b>2</b> with a message on stderr.'],
    solution='''cat > report.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd ~/lab22
threshold=""
while IFS='=' read -r k v || [[ -n $k ]]; do
  k=${k//[[:space:]]/}
  [[ $k == threshold ]] && { v=${v//[[:space:]]/}; threshold=$v; }
done < report.conf
[[ $threshold =~ ^[0-9]+$ ]] || { echo "bad threshold: $threshold" >&2; exit 2; }
awk '{print $9}' access.log | sort | uniq -c | awk '{print $2, $1}'
awk -v t="$threshold" '$9 == 401 {f[$1]++} END {for (ip in f) if (f[ip] >= t) print "ALERT", ip, f[ip]}' access.log
EOF
chmod +x report.sh''',
    check='''cd ~/lab22; rm -f PWNED; cp report.conf report.conf.bak
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
out=$(./report.sh 2>/dev/null)
ok "1 no source" '[ -x report.sh ] && [ ! -e PWNED ] && ! grep -Eq "^[[:space:]]*(source|\\.)[[:space:]]" report.sh'
ok "2 statuses"  'printf "%s\\n" "$out" | grep -E "^[0-9]{3} [0-9]+$" | paste -sd, | grep -qx "200 1,401 3,500 1"'
ok "3 alert"     'printf "%s\\n" "$out" | grep -qx "ALERT 10.0.0.9 3"'
ok "4 validate"  'sed -i "s/^threshold.*/threshold = lots/" report.conf; ./report.sh >/dev/null 2>e; r=$?; cp report.conf.bak report.conf; [ $r -eq 2 ] && [ -s e ]' ''')
