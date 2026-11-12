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
    module='02-working-with-data', lesson='04-calling-sed-awk-and-jq-from-scripts', n='2.4',
    module_label='Module 2 · Working with data',
    title='Calling sed, awk and jq from scripts',
    desc='Use sed, awk and jq safely inside Bash scripts: sed -i with backups and escaped replacements, awk -v and ENVIRON instead of pasting values into code, awk programs in heredocs and files, jq filters (.[], select, map, group_by), jq --arg, --argjson, -n, -r, -e, @csv, @tsv and @sh, safe JSON edits with temp files, and verifying every change.',
    og_desc='sed -i, awk -v and jq --arg from Bash scripts: edit configs, total columns and parse JSON safely.',
    minutes=40, level='Intermediate',
    lead='Let sed edit, awk count and jq understand JSON, and hand them your variables as data, never as code.',
    chips=['Code injection demo', 'jq pipeline animated', '40+ real calls', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """city='Pune'
printf 'id,city,amount\\n1,Pune,450\\n2,Delhi,800\\n3,Pune,300\\n' > orders.csv

echo '--- awk with -v (safe):'
awk -F, -v c="$city" '$2 == c {s += $3} END {print c, s}' orders.csv

echo '--- sed with another delimiter:'
dir=/srv/logs/orders
echo 'log_dir = /var/log/app' | sed "s|^log_dir = .*|log_dir = $dir|"

echo '--- building JSON safely (no jq here, so we show the escaping idea):'
note='said "hi"'
printf '{"note": "%s"}\\n' "${note//\\"/\\\\\\"}"
"""

RUN = dict(
    heading='Values as data, in your browser',
    intro='<p>The browser has awk and sed but not jq; the last block shows the quoting jq would do for you.</p>',
    code=MAIN,
    anno=[('-v c="$city"', 'A value, not code.'), ('s|…|…|', 'Slashes in the value are fine.'), ('${note//\\"/…}', 'Escaping quotes by hand: jq --arg does this.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Change city to Delhi.', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does sed say?',
             code="dir=/srv/x\necho 'a = 1' | sed \"s/a = .*/a = $dir/\"\n", expect='any'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the value is pasted into awk code. Use -v.',
             code="min=500\nprintf '100\\n900\\n' | awk \"\\$1 > $min\"\n"),
        dict(label='4 · Your turn', hint='Sum column 2 only for rows with status paid (passed with -v).',
             code="printf 'a,10,paid\\nb,20,failed\\nc,5,paid\\n' | awk -F, -v s=paid '$3 == s {t += $2} END {print t}'\n"),
        dict(label='5 · Challenge', hint='Preview a sed change with -n …p before applying it.',
             code="printf 'port = 80\\nhost = x\\n' > c.conf\nsed -n 's|^port = .*|port = 8080|p' c.conf\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Install jq if needed. Outputs below are from our build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Install jq', cmd="sudo apt install jq      # or: sudo dnf install jq\njq --version", output='jq-1.7.1', note='Real version on our build machine.'),
        dict(title='2 · A real API', cmd="curl -s https://api.github.com/repos/jqlang/jq | jq -r '.full_name, .stargazers_count'", output='jqlang/jq\n31000', note='Typical (the number changes).'),
        dict(title='3 · Cloud CLI', cmd="aws ec2 describe-instances --output json | jq -r '.Reservations[].Instances[] | [.InstanceId, .State.Name] | @tsv'", output='i-0abc123def456\trunning\ni-0789ghi012jkl\tstopped', note='Typical.'),
        dict(title='4 · macOS sed', cmd="sed -i '' 's|^port = .*|port = 9090|' app.conf", output='(no output)', note='BSD sed needs an argument after -i.'),
    ],
)

TRACE = dict(
    heading='A safe config change, line by line',
    intro='<p>Preview, change with a backup, verify.</p>',
    code='''printf 'port = 80\\nhost = web01\\n' > app.conf
sed -n 's|^port = .*|port = 8080|p' app.conf
sed -i.bak 's|^port = .*|port = 8080|' app.conf
changed=$(diff app.conf.bak app.conf | grep -c '^>')
echo "changed lines: $changed"
cat app.conf
''',
    notes={2: 'Preview only.', 3: 'Real change, backup kept.', 4: 'Exactly one line expected.'},
)

WORKED_INTRO = 'Three jobs with the right tool and safe values.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Bump a version in a config',
         problem='<p>Set version = 1.4.3 in an env file and keep a backup.</p>',
         inp='a config', approach=['Anchored sed -i.bak.'],
         code='''printf 'name = orders\\nversion = 1.4.2\\n' > release.env
v=1.4.3
sed -i.bak "s|^version = .*|version = $v|" release.env
diff release.env.bak release.env
''', notes={3: 'Dots in a replacement are harmless; in a pattern they would need escaping.'}, tryit='Undo with mv.', expect='any'),
    dict(level='i', tag='Data', title='Top city with awk',
         problem='<p>Find the city with the highest paid total and pass the status as a variable.</p>',
         inp='orders CSV', approach=['awk -v, then sort.'],
         code='''printf 'id,city,amount,status\\n1,Pune,450,paid\\n2,Mumbai,1200,paid\\n3,Pune,999,paid\\n4,Delhi,800,failed\\n' > o.csv
st=paid
awk -F, -v s="$st" 'NR > 1 && $4 == s {t[$2] += $3} END {for (c in t) print t[c], c}' o.csv | sort -rn | head -1
''', notes={3: 'Totals per city, then the biggest.'}, tryit='Print the top 2.'),
    dict(level='a', tag='DevOps', title='JSON in, JSON out',
         problem='<p>Read a service list, keep the unhealthy ones, and build an alert body (without jq the idea is shown with awk + manual escaping).</p>',
         inp='JSON lines', approach=['Line-delimited JSON with fixed keys.'],
         code='''printf '{"svc":"api","ok":true}\\n{"svc":"db","ok":false}\\n' > status.jsonl
bad=$(awk -F'"' '/"ok":false/ {print $4}' status.jsonl)
printf '{"text": "unhealthy: %s"}\\n' "$bad"
echo '(with jq: jq -cn --arg b "$bad" '"'"'{text: "unhealthy: \\($b)"}'"'"')'
''', notes={2: 'Works only because each line has the same layout: jq is the real answer.'}, tryit='Add a second bad service.'),
]

QUIZ = mix([
    dict(q='Pass a shell variable to awk safely:', options=['awk "…$v…"', 'awk -v v="$v" …', 'export only', 'awk $v'], answer=1, why='-v.'),
    dict(q='sed "s/x/$dir/" fails for dir=/srv/a because…', options=['sed has no variables', 'the slashes end the s command', 'quotes', 'sed -i missing'], answer=1, why='Delimiter clash.'),
    dict(q='Keep a backup when editing in place:', options=['sed -b', 'sed -i.bak', 'sed --keep', 'cp after'], answer=1, why='-i.bak.'),
    dict(q='jq option for strings without quotes:', options=['-c', '-r', '-n', '-s'], answer=1, why='Raw.'),
    dict(q='A number into jq:', options=['--arg', '--argjson', '-v', '$n'], answer=1, why='--argjson.'),
    dict(q='jq … f > f does what?', options=['edits in place', 'empties the file first', 'fails safely', 'backs up'], answer=1, why='Shell truncates.'),
    dict(q='Build JSON from variables:', options=['echo "{\\"a\\":\\"$v\\"}"', "jq -n --arg a \"$v\" '{a: $a}'", 'printf', 'sed'], answer=1, why='Escaping done.'),
    dict(q='Why not grep JSON?', options=['slow', 'depends on layout and escaping', 'not allowed', 'case'], answer=1, why='Not a parser.'),
])

REVISION = [
    'sed edits, awk computes over columns, jq parses JSON; Bash loops only for small data or complex logic.',
    'sed: anchor (^key = .*), use | as delimiter, escape \\ | & in replacements, -i.bak, preview with -n …p.',
    'awk: -F, -v name="$v" (or ENVIRON["v"]); never paste $v into the program; long programs via -f or heredoc.',
    'jq: .key, .[], select(), map(), group_by(), length, add; -r raw, -c compact, -e exit status.',
    'jq values: --arg (string), --argjson (number/JSON), -n to build JSON; @csv @tsv @sh to hand results on.',
    'Verify changes (diff, grep -c, cmp, jq empty); never jq … f > f: temp file + mv.',
]

FAQ = [
    ('How do I use a shell variable in sed?', 'Use double quotes and a delimiter the value cannot contain, and escape \\, the delimiter and & in the value: sed "s|^key = .*|key = $v|".'),
    ('How do I pass a variable to awk?', "awk -v name=\"$var\" '… name …' file."),
    ('How do I parse JSON in a shell script?', "Use jq: jq -r '.field' file.json; pass variables with --arg."),
    ('How do I edit a file in place with sed and keep a backup?', "sed -i.bak 's/old/new/' file (macOS: sed -i '' …)."),
    ('Why is my file empty after jq … file > file?', 'The shell truncated it before jq read it; write to a temp file and mv.'),
    ('How do I create JSON with variables in Bash?', 'jq -n --arg name "$v" \'{name: $name}\' handles all escaping.'),
    ('What does jq -e do?', 'Sets the exit status from the last output: false or null gives 1.'),
]

PRACTICE_INTRO = 'Small sed, awk and jq tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='sed delimiter', stmt='Replace a path value using | as the delimiter.', inp='a line', code="echo 'dir = /a' | sed 's|^dir = .*|dir = /srv/b|'\n", explain='dir = /srv/b.'),
    dict(level='easy', title='awk -v', stmt='Print lines whose first field equals a variable.', inp='lines', code="printf 'x 1\\ny 2\\n' | awk -v k=y '$1 == k'\n", explain='y 2.'),
    dict(level='easy', title='jq field', stmt='Get the name from a small JSON object.', inp='JSON', code="echo '{\"name\":\"web01\"}' | jq -r .name\n", explain='web01.'),
    dict(level='medium', title='jq filter', stmt='Names with cpu > 50.', inp='JSON array', code="echo '[{\"n\":\"a\",\"cpu\":70},{\"n\":\"b\",\"cpu\":10}]' | jq -r '.[] | select(.cpu > 50) | .n'\n", explain='a.'),
    dict(level='medium', title='jq --arg', stmt='Build {\"host\": \"web 01\"} from a variable.', inp='a variable', code="h='web 01'; jq -cn --arg h \"$h\" '{host: $h}'\n", explain='Escaped by jq.'),
    dict(level='medium', title='awk sum', stmt='Sum the 2nd CSV column.', inp='CSV', code="printf 'a,3\\nb,4\\n' | awk -F, '{s+=$2} END{print s}'\n", explain='7.'),
    dict(level='business', title='Escape &', stmt='Put R&D into a sed replacement correctly.', inp='a value', code="v='R&D'; echo 'team = x' | sed \"s|^team = .*|team = ${v//&/\\\\&}|\"\n", explain='team = R&D.'),
    dict(level='business', title='jq count', stmt='Count elements whose env is prod.', inp='JSON array', code="echo '[{\"env\":\"prod\"},{\"env\":\"test\"},{\"env\":\"prod\"}]' | jq '[.[] | select(.env==\"prod\")] | length'\n", explain='2.'),
]

SCN_INTRO = 'Interview questions about sed, awk and jq in scripts.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Replace a word in a file from the command line”', 'Very common.', 'and keep a backup?',
        '''<ul>
          <li>sed -i.bak 's/old/new/g' file</li>
          <li>Anchor with ^ for config keys.</li>
          <li>Check with diff file.bak file.</li>
        </ul>''', 'opening vim in a script.') +
    scn('Service company', 'Junior', 'awk program breaks on some input', 'Values pasted in.', 'fix?',
        '''<ol>
          <li>Pass values with -v.</li>
          <li>Reference them without $.</li>
          <li>Quote the program in single quotes.</li>
        </ol>''', 'more backslashes.') +
    scn('Product company', 'Mid-level', 'Script reads API JSON with grep', 'Broke after an API change.', 'fix?',
        '''<ul>
          <li>jq -r with explicit paths.</li>
          <li>-e to fail on missing values.</li>
          <li>--arg for filters; tests with saved responses.</li>
        </ul>''', 'a more complex grep.') +
    scn('Platform', 'Senior', 'Config edits across 300 servers', 'Ansible not available.', 'safe approach?',
        '''<ul>
          <li>Idempotent set_key (grep, then sed or append).</li>
          <li>-i.bak, diff count check, rollback on mismatch.</li>
          <li>Prefer config templates / tools long term.</li>
        </ul>''', 'blind sed -i on all hosts.')
) + interview([
    ('sed -i vs -i.bak?', 'Backup or not.'),
    ('Why | as sed delimiter?', 'Values with slashes.'),
    ('awk -v vs ENVIRON?', 'Escape processing vs raw.'),
    ('jq -r?', 'Raw strings.'),
    ('--arg vs --argjson?', 'String vs JSON value.'),
    ('jq -n?', 'No input; build JSON.'),
    ('Why not jq … f > f?', 'Truncation.'),
], [
    ('LFCS', 'sed and awk in scripts.'),
    ('RHCSA', 'Text editing from the command line.'),
    ('CompTIA Linux+', 'sed, awk, JSON tools.'),
]) + distro('Versions per distribution.', [
    ('sed', 'GNU', 'GNU', 'GNU', 'macOS: BSD (-i "")'),
    ('awk', 'mawk', 'gawk', 'gawk', 'macOS: BWK awk'),
    ('jq', 'apt install jq', 'dnf install jq', 'zypper', 'brew install jq'),
    ('yq (YAML)', 'snap/apt', 'dnf', 'zypper', 'brew'),
    ('Default -i', 'yes', 'yes', 'yes', 'needs suffix arg'),
]) + teaser('3.1', 'Module 2 is complete: you can read, parse and transform data safely. Module 3 makes scripts robust: error handling patterns, set -e pitfalls, ERR traps and retries.')

CHEATSHEET = cheatsheet('sed, awk, jq', [
    ('sed', [("-i.bak 's|^k = .*|k = v|'", 'set key'), ("-n '…p'", 'preview'), ("'/re/d'", 'delete'), ("'/re/a txt'", 'append')]),
    ('awk', [('-F, -v c="$c"', 'safe value'), ("'$2==c {s+=$3}'", 'filter+sum'), ('END{print s}', 'total'), ('-f prog.awk', 'file')]),
    ('jq read', [('.k  .a[]', 'walk'), ('select(.x>1)', 'filter'), ('map  group_by', 'reshape'), ('-r -c -e', 'output')]),
    ('jq values', [('--arg v "$v"', 'string'), ('--argjson n 5', 'number'), ("-n '{a: $v}'", 'build'), ('@csv @tsv @sh', 'export')]),
])

MINDMAP = mindmap('sed · awk · jq', [
    ('sed', 'blue', ['-i.bak', '| delimiter', 'escape']),
    ('awk', 'green', ['-v', 'ENVIRON', '-f file']),
    ('jq read', 'amber', ['.[]', 'select', 'map']),
    ('jq values', 'violet', ['--arg', '--argjson', '-n']),
    ('Safety', 'red', ['no pasting', 'no f > f', 'verify']),
    ('Choose', 'acc', ['edit', 'columns', 'JSON']),
])

LAB = lab('config + JSON report', 'Build the lab (it creates <code>~/lab24/app.conf</code> and <code>~/lab24/servers.json</code>), write <code>~/lab24/ops.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab24; mkdir -p ~/lab24 && cd ~/lab24
printf '# app\\nlisten_port = 8080\\nlog_dir = /var/log/app\\n' > app.conf
cat > servers.json <<'EOF'
{"servers": [
  {"name": "web01", "env": "prod", "cpu": 72},
  {"name": "web02", "env": "prod", "cpu": 91},
  {"name": "test01", "env": "test", "cpu": 12}
]}
EOF''',
    tasks=['<code>ops.sh DIR</code> sets <code>log_dir</code> in <code>app.conf</code> to DIR with sed (any DIR, including slashes and <code>&amp;</code>), keeping a backup <code>app.conf.bak</code>; no other line may change.',
           'If the edit did not change exactly one line, it exits <b>1</b>.',
           'It then prints the names of <b>prod</b> servers with cpu above <b>80</b>, one per line, using jq with <code>--arg</code> and <code>--argjson</code> (here: <code>web02</code>).',
           'Finally it prints one compact JSON line built with <code>jq -n</code>: <code>{"log_dir":DIR,"hot":["web02"]}</code>, valid even when DIR contains quotes.'],
    solution='''cat > ops.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
cd ~/lab24
dir=${1:?usage: ops.sh DIR}
esc=$(printf '%s' "$dir" | sed 's/[\\\\|&]/\\\\&/g')
sed -i.bak "s|^log_dir = .*|log_dir = $esc|" app.conf
n=$(diff app.conf.bak app.conf | grep -c '^>' || true)
(( n == 1 )) || { echo "expected 1 change, got $n" >&2; exit 1; }
jq -r --arg e prod --argjson m 80 '.servers[] | select(.env == $e and .cpu > $m) | .name' servers.json
hot=$(jq -c --arg e prod --argjson m 80 '[.servers[] | select(.env == $e and .cpu > $m) | .name]' servers.json)
jq -cn --arg d "$dir" --argjson h "$hot" '{log_dir: $d, hot: $h}'
EOF
chmod +x ops.sh''',
    check='''cd ~/lab24; cp app.conf app.conf.orig
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
d='/srv/R&D "logs"'
out=$(./ops.sh "$d" 2>/dev/null)
ok "1 sed"   '[ -f app.conf.bak ] && grep -qxF "log_dir = $d" app.conf && grep -qx "listen_port = 8080" app.conf'
ok "2 count" 'cp app.conf.orig app.conf; printf "x = 1\\n" > app.conf; ./ops.sh /tmp >/dev/null 2>&1; r=$?; cp app.conf.orig app.conf; [ $r -eq 1 ]'
ok "3 jq"    'printf "%s\\n" "$out" | head -1 | grep -qx web02 && grep -q -- "--argjson" ops.sh'
ok "4 json"  'printf "%s\\n" "$out" | tail -1 | jq -e --arg d "$d" ".log_dir == \\$d and .hot == [\\"web02\\"]" >/dev/null' ''')
