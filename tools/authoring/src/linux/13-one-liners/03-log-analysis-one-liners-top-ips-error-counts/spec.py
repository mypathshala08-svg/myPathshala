import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='13-one-liners', lesson='03-log-analysis-one-liners-top-ips-error-counts', n='13.3',
    module_label='Module 13 · Power one-liners and command combos',
    title='Log analysis one-liners: top IPs, error counts, status codes and response times',
    desc='Analyse web and system logs from the command line: the combined access log format field by field, status code counts, top IPs and URLs with sort | uniq -c | sort -rn, per-minute and per-hour counts, time windows, error rates, averages, maximums and p95 response times with awk, user agents, app log errors, SSH brute force in auth.log, tail -f live filtering and a reusable incident script; real outputs on a 1,320-line log and 40+ examples.',
    og_desc='Log analysis one-liners with real runs: status codes, top IPs, failing URLs, per-minute errors, response times and SSH brute force.',
    minutes=45, level='Beginner → Advanced',
    lead='Answer “how bad, since when, who, where, how slow” from raw logs in minutes: learn the fields of an access log once, then filter, pick, count and rank.',
    chips=['1,320-line realistic log', 'Funnel animated', 'Attack per minute chart', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A tiny access log (IP, time, request, status, bytes, seconds)
cat > access.log <<'EOF'
10.0.0.5 - - [11/Nov/2026:10:01:02 +0530] "GET / HTTP/1.1" 200 512 0.040
203.0.113.50 - - [11/Nov/2026:10:02:10 +0530] "POST /login HTTP/1.1" 401 88 0.020
203.0.113.50 - - [11/Nov/2026:10:02:11 +0530] "POST /login HTTP/1.1" 401 88 0.021
10.0.0.7 - - [11/Nov/2026:10:02:30 +0530] "GET /api/orders HTTP/1.1" 500 120 1.900
203.0.113.50 - - [11/Nov/2026:10:03:05 +0530] "POST /login HTTP/1.1" 401 88 0.020
10.0.0.5 - - [11/Nov/2026:10:04:40 +0530] "GET /index.html HTTP/1.1" 200 2048 0.120
EOF
echo "status codes:"; awk '{print $9}' access.log | sort | uniq -c | sort -rn
echo "top IP:"; awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -1
echo "401s per minute:"; awk '$9==401 {print substr($4,14,5)}' access.log | uniq -c
awk '{s+=$NF; if($NF>m){m=$NF; u=$7}} END{printf "avg %.3f s, slowest %s (%.1f s)\\n", s/NR, u, m}' access.log
"""

RUN = dict(
    heading='Count, rank, slice and compute',
    intro='<p>A six-line log: status codes, the top IP, failed logins per minute, and the average and slowest response.</p>',
    code=MAIN,
    anno=[("awk '{print $9}'", 'Field 9 is the status code.'), ('substr($4,14,5)', 'Hour:minute from the time field.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which IP is suspicious?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many lines does each print?',
             code="printf 'a\\nb\\na\\n' > ips.txt\nuniq -c ips.txt | wc -l\nsort ips.txt | uniq -c | wc -l\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> grep 500 also matches the 5000 bytes. Use awk on the status field.',
             code="printf '%s\\n' '1.1.1.1 \"GET /\" 200 5000' '2.2.2.2 \"GET /x\" 500 10' > l.log\ngrep -c 500 l.log\nawk '$4==500' l.log | wc -l\n"),
        dict(label='4 · Your turn', hint='Print the error rate (status ≥ 500) as a percentage.',
             code="printf '%s\\n' 'a 200' 'b 500' 'c 200' 'd 502' > s.log\nawk '{n++; if($2>=500)e++} END{printf \"%.0f%%\\n\", 100*e/n}' s.log\n"),
        dict(label='5 · Challenge', hint='Count requests per URL with an awk array (no sort | uniq).',
             code="printf '%s\\n' '/a' '/b' '/a' '/c' '/a' > urls.txt\nawk '{n[$1]++} END{for(u in n) print n[u], u}' urls.txt | sort -rn\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your real logs',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical. Real logs often need sudo.</p>',
    items=[
        dict(title='1 · Nginx status codes today', cmd="sudo awk '{print $9}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head", output='  20112 200\n    845 304\n    210 404\n     12 502', note='Typical.'),
        dict(title='2 · SSH failures from the journal', cmd="sudo journalctl -u ssh --since today | grep -c 'Failed password'", output='1873', note='Typical on an internet-facing server.'),
        dict(title='3 · Include rotated logs', cmd="sudo zcat -f /var/log/nginx/access.log* | awk '$9>=500' | wc -l", output='77', note='Typical: zcat -f reads both plain and .gz files.'),
        dict(title='4 · Ready-made report', cmd='sudo apt install goaccess && goaccess /var/log/nginx/access.log --log-format=COMBINED', output='(interactive terminal dashboard)', note='Typical: a tool built on the same ideas.'),
    ],
)

TRACE = dict(
    heading='Counting with an awk array, line by line',
    intro='<p>Step through how a one-pass counter works.</p>',
    code='''printf '%s\\n' '1.1.1.1 401' '2.2.2.2 200' '1.1.1.1 401' > t.log
fails=$(awk '$2==401 {n[$1]++} END{for(ip in n) print n[ip], ip}' t.log)
top_ip=${fails#* }
count=${fails%% *}
echo "top failing IP: $top_ip with $count failures"
''',
    notes={2: 'One pass: a counter per IP.', 3: 'Text after the first space.', 4: 'Text before the first space.'},
)

WORKED_INTRO = 'Three log tasks from real jobs: an error-rate alert, a per-endpoint report and a brute-force list.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Alert if the error rate is too high',
         problem='<p>Print ALERT if more than 5% of requests are server errors (5xx).</p>',
         inp='an access log', approach=['awk counts.', 'compare in awk.'],
         code='''printf '%s\\n' 'a "GET /" 200' 'b "GET /x" 500' 'c "GET /" 200' 'd "GET /y" 503' 'e "GET /" 200' > a.log
awk '{n++; if($4>=500)e++} END{r=100*e/n; printf "error rate %.1f%%: %s\\n", r, (r>5?"ALERT":"ok")}' a.log
''', notes={2: 'Ternary inside printf.'}, tryit='Exit with status 1 when it is an alert.'),
    dict(level='i', tag='SRE', title='Requests and average time per endpoint',
         problem='<p>For each URL print the number of requests and the average response time, slowest first.</p>',
         inp='URL and seconds', approach=['awk arrays.', 'sort -k3 -rn.'],
         code='''printf '%s\\n' '/api 0.30' '/api 0.50' '/home 0.05' '/home 0.07' '/pay 1.20' > t.log
awk '{n[$1]++; s[$1]+=$2} END{for(u in n) printf "%-6s %3d req %6.3f s\\n", u, n[u], s[u]/n[u]}' t.log | sort -k4 -rn
''', notes={2: 'Two arrays with the same key.'}, tryit='Add the maximum time per URL.'),
    dict(level='a', tag='Security', title='IPs to block',
         problem='<p>From SSH log lines, list IPs with at least 3 failed passwords, with counts, ready for a firewall.</p>',
         inp='auth lines', approach=['grep -oE.', 'uniq -c, awk filter.'],
         code='''for i in 1 2 3; do echo "sshd: Failed password for root from 203.0.113.50 port 1"; done > auth.log
echo "sshd: Failed password for bob from 198.51.100.7 port 2" >> auth.log
grep 'Failed password' auth.log | grep -oE 'from [0-9.]+' | awk '{print $2}' | sort | uniq -c | awk '$1>=3 {print "block", $2, "("$1" failures)"}'
''', notes={3: 'Keep only repeat offenders.'}, tryit='Print ufw deny commands instead.'),
]

QUIZ = mix([
    dict(q='Status code field in the combined format:', options=['$4', '$7', '$9', '$1'], answer=2, why='$9.'),
    dict(q='Why sort before uniq -c?', options=['speed', 'uniq only merges adjacent duplicates', 'uniq needs numbers', 'to remove headers'], answer=1, why='Neighbours.'),
    dict(q='Top 5 IPs:', options=["awk '{print $1}' | sort | uniq -c | sort -rn | head -5", 'grep -c', 'wc -l', 'sort -u | head -5'], answer=0, why='Count and rank.'),
    dict(q='Best way to count status 500:', options=['grep 500', "awk '$9==500'", 'grep -c 5', 'tail'], answer=1, why='Exact field.'),
    dict(q='Average of the last field:', options=["awk '{s+=$NF} END{print s/NR}'", "awk '{print $NF}'", 'sort -n', 'wc -l'], answer=0, why='Sum / count.'),
    dict(q='5xx means…', options=['client error', 'server error', 'redirect', 'success'], answer=1, why='Our side.'),
    dict(q='Watch new errors live:', options=['cat', 'tail -f | grep --line-buffered', 'head', 'less'], answer=1, why='Follow.'),
    dict(q='Brute-force SSH evidence:', options=['Accepted publickey', 'Failed password from one IP many times', 'session opened', 'Connection closed'], answer=1, why='Repeated failures.'),
])

REVISION = [
    'Combined format: $1 IP, $4 time, $6 method, $7 URL, $9 status, $10 bytes; here $NF = response time; -F\'"\' $6 = user agent.',
    'Count and rank: awk \'{print $N}\' | sort | uniq -c | sort -rn | head.',
    'Match fields, not lines: awk \'$9>=500\' instead of grep 500.',
    'Time: substr($4,14,2) hour, substr($4,14,5) minute; windows by text comparison of $4; uniq -c per minute.',
    'Numbers: s+=$NF, n++, max; per group with arrays a[$7]+=$NF; p95 with sort -n.',
    'auth.log: Failed password / invalid user / Accepted; grep -oE "from [0-9.]+"; tail -f | grep --line-buffered for live.',
]

FAQ = [
    ('How do I find the top IP addresses in an access log?', "awk '{print $1}' access.log | sort | uniq -c | sort -rn | head."),
    ('How do I count HTTP status codes?', "awk '{print $9}' access.log | sort | uniq -c | sort -rn."),
    ('How do I see errors per minute?', "awk '$9>=500 {print substr($4,14,5)}' access.log | uniq -c."),
    ('How do I find failed SSH logins?', "grep 'Failed password' /var/log/auth.log (or journalctl -u ssh), then grep -oE 'from [0-9.]+' | sort | uniq -c."),
    ('How do I analyse rotated .gz logs?', 'zcat -f access.log* | … or zgrep.'),
    ('Why does uniq -c show the same value several times?', 'The input was not sorted; uniq only merges adjacent lines.'),
    ('How do I watch a log live and filter it?', 'tail -f file | grep --line-buffered pattern.'),
]

PRACTICE_INTRO = 'Small log tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Count lines', stmt='Count the requests in a 3-line log.', inp='a log', code="printf 'a\\nb\\nc\\n' > x.log; wc -l < x.log\n", explain='3.'),
    dict(level='easy', title='Second field', stmt='Print the second field of “10.0.0.5 200”.', inp='a line', code="echo '10.0.0.5 200' | awk '{print $2}'\n", explain='200.'),
    dict(level='easy', title='Count one value', stmt='Count lines whose second field is 404.', inp='a log', code="printf '%s\\n' 'a 404' 'b 200' 'c 404' | awk '$2==404' | wc -l\n", explain='2.'),
    dict(level='medium', title='Rank', stmt='Rank the values a b a c a b by frequency.', inp='values', code="printf '%s\\n' a b a c a b | sort | uniq -c | sort -rn\n", explain='3 a, 2 b, 1 c.'),
    dict(level='medium', title='Minute', stmt='Print the hour:minute of [11/Nov/2026:10:02:13.', inp='a time field', code="echo '[11/Nov/2026:10:02:13' | awk '{print substr($1,14,5)}'\n", explain='10:02.'),
    dict(level='medium', title='Average', stmt='Average of 0.2, 0.4 and 0.6.', inp='numbers', code="printf '0.2\\n0.4\\n0.6\\n' | awk '{s+=$1} END{print s/NR}'\n", explain='0.4.'),
    dict(level='business', title='Top failing IP', stmt='From “ip status” lines, print the IP with the most 401s.', inp='a log', code="printf '%s\\n' 'x 401' 'y 401' 'x 401' 'x 200' | awk '$2==401{print $1}' | sort | uniq -c | sort -rn | head -1\n", explain='2 x.'),
    dict(level='business', title='Error rate', stmt='Percentage of lines with status ≥ 500 in: 200 500 200 200.', inp='statuses', code="printf '200\\n500\\n200\\n200\\n' | awk '{n++; if($1>=500)e++} END{print 100*e/n \"%\"}'\n", explain='25%.'),
]

SCN_INTRO = 'Interview questions about log analysis, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Find the top 10 IPs in an Apache log”', 'Asked everywhere.', 'one-liner?',
        '''<ul>
          <li>awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10</li>
          <li>Explain each stage.</li>
          <li>Mention sort before uniq.</li>
        </ul>''', 'grep each IP by hand.') +
    scn('Service company', 'Junior', '“The site was down at 10 a.m. Prove when it started”', 'You have the access log.', 'how?',
        '''<ol>
          <li>awk '$9>=500 {print substr($4,14,5)}' | uniq -c.</li>
          <li>Find the first minute with a jump.</li>
          <li>Correlate with app.log timestamps.</li>
        </ol>''', '“it felt like 10”.') +
    scn('Security team', 'Mid-level', 'Thousands of 401s from one IP', 'Login page slow.', 'what next?',
        '''<ul>
          <li>Confirm: top IPs for 401, per-minute rate, user agents.</li>
          <li>Check auth.log for the same IP.</li>
          <li>Block (firewall), rate-limit, and add fail2ban.</li>
        </ul>''', 'blocking a whole country by reflex.') +
    scn('Platform', 'Senior', 'Logs are 40 GB per day', 'One-liners too slow.', 'scale?',
        '''<ul>
          <li>Filter first with grep/zgrep; LC_ALL=C; awk arrays instead of sort.</li>
          <li>Parallel per file (xargs -P) and combine.</li>
          <li>Long term: ship logs to ELK/Loki/ClickHouse.</li>
        </ul>''', 'opening it in an editor.')
) + interview([
    ('What is in the combined log format?', 'IP, ident, user, time, request, status, bytes, referrer, user agent.'),
    ('401 vs 403?', 'Not authenticated vs not allowed.'),
    ('How to count requests per hour?', 'substr($4,14,2) | uniq -c.'),
    ('How to include rotated logs?', 'zcat -f access.log*.'),
    ('Why grep --line-buffered with tail -f?', 'So lines are not held in a buffer.'),
    ('What is p95?', 'The value 95% of requests are faster than.'),
    ('Where are SSH logs on RHEL?', '/var/log/secure (or journalctl -u sshd).'),
], [
    ('RHCSA (EX200)', 'Locate and interpret system log files and journals.'),
    ('LFCS', 'Analyse logs with text tools.'),
    ('Security+ / SOC interviews', 'Find brute force in logs.'),
]) + distro('Log locations differ by distribution and service.', [
    ('Web (nginx)', '/var/log/nginx/access.log', 'same', '/usr/local/var/log/nginx', 'IIS logs'),
    ('Web (Apache)', '/var/log/apache2/access.log', '/var/log/httpd/access_log', '-', '-'),
    ('SSH', '/var/log/auth.log or journal', '/var/log/secure or journal', 'log show', 'Event Viewer'),
    ('All system logs', 'journalctl', 'journalctl', 'log show', 'Get-WinEvent'),
    ('Rotation', 'logrotate (.1, .gz)', 'logrotate', 'newsyslog', '-'),
]) + teaser('13.4', 'The disk is 97% full, port 8080 is “already in use” and something is eating all the memory. Next: server admin one-liners for the biggest files, who uses a port and the CPU and memory hogs.')

CHEATSHEET = cheatsheet('Log one-liners', [
    ('Fields', [('$1', 'IP'), ('$4', 'time'), ('$7', 'URL'), ('$9', 'status'), ('$NF', 'seconds')]),
    ('Count', [("{print $9} | sort | uniq -c", 'per value'), ('| sort -rn | head', 'top'), ("'$9>=500' | wc -l", 'errors'), ('sort -u | wc -l', 'unique')]),
    ('Time', [('substr($4,14,2)', 'hour'), ('substr($4,14,5)', 'minute'), ('$4>="[…:10:00"', 'window'), ('| uniq -c', 'per unit')]),
    ('Numbers / live', [('s+=$NF … s/NR', 'average'), ('a[$7]+=$NF', 'per URL'), ('sort -n … p95', 'percentile'), ('tail -f | grep --line-buffered', 'live')]),
])

MINDMAP = mindmap('Logs', [
    ('Fields', 'blue', ['$1 IP', '$9 status', '$NF time']),
    ('Count', 'green', ['sort | uniq -c', 'sort -rn', 'head']),
    ('Time', 'amber', ['per minute', 'windows', 'first/last']),
    ('Numbers', 'violet', ['sum avg', 'max p95', 'per URL']),
    ('Security', 'red', ['401 spikes', 'auth.log', 'block']),
    ('Tools', 'acc', ['tail -f', 'zcat -f', 'awk arrays']),
])

LAB = lab('an incident report', 'Build the lab, write <code>~/lab133/report.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab133 && cd ~/lab133 && rm -f report.sh *.txt
for i in $(seq 1 30); do echo "10.0.0.$((i % 3 + 1)) - - [11/Nov/2026:09:$(printf %02d $i):00 +0530] \\"GET /home HTTP/1.1\\" 200 500 0.050"; done > access.log
for i in $(seq 1 12); do echo "198.51.100.9 - - [11/Nov/2026:10:0$((i % 4)):10 +0530] \\"POST /login HTTP/1.1\\" 401 80 0.020"; done >> access.log
for i in 1 2 3; do echo "10.0.0.2 - - [11/Nov/2026:10:05:0$i +0530] \\"GET /api/pay HTTP/1.1\\" 502 90 2.500"; done >> access.log''',
    tasks=['Write the status code counts, as <code>uniq -c</code> prints them sorted by count (biggest first), into <code>status.txt</code>.',
           'Write the IP with the most 401 responses (just the IP) into <code>attacker.txt</code>.',
           'Write the URL that returned 5xx (just the URL) into <code>failing.txt</code>.',
           'Write the average response time of all requests, with 3 decimals (printf "%.3f"), into <code>avg.txt</code>.'],
    solution='''cat > report.sh <<'EOF'
cd ~/lab133
awk '{print $9}' access.log | sort | uniq -c | sort -rn > status.txt
awk '$9==401{print $1}' access.log | sort | uniq -c | sort -rn | awk 'NR==1{print $2}' > attacker.txt
awk '$9>=500{print $7}' access.log | sort -u > failing.txt
awk '{s+=$NF} END{printf "%.3f\\n", s/NR}' access.log > avg.txt
EOF''',
    check='''cd ~/lab133; rm -f status.txt attacker.txt failing.txt avg.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f report.sh ] && bash report.sh 2>/dev/null
ok "1 status"   '[ "$(awk "{print \\$1, \\$2}" status.txt 2>/dev/null | tr "\\n" " ")" = "30 200 12 401 3 502 " ]'
ok "2 attacker" '[ "$(cat attacker.txt 2>/dev/null)" = 198.51.100.9 ]'
ok "3 failing"  '[ "$(cat failing.txt 2>/dev/null)" = /api/pay ]'
ok "4 avg"      '[ "$(cat avg.txt 2>/dev/null)" = "$(awk "{s+=\\$NF} END{printf \\"%.3f\\", s/NR}" access.log)" ]' ''')
