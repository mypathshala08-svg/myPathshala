import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# A deterministic 1,320-line web access log (combined format + response time), an app log and an auth log.
LG = r"""rm -rf ~/lg; mkdir -p ~/lg; cd ~/lg
python3 - <<'PY'
import random
r = random.Random(7)
ips = "10.0.0.5 10.0.0.7 10.0.0.9 192.168.1.20 203.0.113.50 198.51.100.7 10.0.0.11".split()
urls = "/ /index.html /login /api/orders /api/cart /static/app.js /static/logo.png /admin /search".split()
ags = "Mozilla/5.0 curl/8.5.0 Googlebot/2.1 python-requests/2.31".split()
L = []
for i in range(1200):
    h = 8 + i // 150; m = r.randrange(60); s = r.randrange(60)
    a = r.choice(ips); p = r.choice(urls); x = r.random(); st = 200
    if x < 0.06: st = 404
    elif x < 0.09: st = 500
    elif x < 0.11: st = 302
    elif p == "/admin": st = 403
    meth = "POST" if p == "/login" and r.random() < 0.5 else "GET"
    b = r.randrange(200, 5200); t = 1 + r.random() * 2 if st == 500 else 0.01 + r.random() * 0.4
    L.append((h, m, s, f'{a} - - [11/Nov/2026:{h:02d}:{m:02d}:{s:02d} +0530] "{meth} {p} HTTP/1.1" {st} {b} "-" "{r.choice(ags)}" {t:.3f}'))
for j in range(120):
    m = 2 + j // 20; s = r.randrange(60)
    L.append((10, m, s, f'203.0.113.50 - - [11/Nov/2026:10:{m:02d}:{s:02d} +0530] "POST /login HTTP/1.1" 401 88 "-" "python-requests/2.31" 0.020'))
L.sort(key=lambda z: z[:3])
open("access.log", "w").write("\n".join(z[3] for z in L) + "\n")
PY
cat > app.log <<'EOF'
2026-11-11 09:58:01 INFO  orders: started worker 1
2026-11-11 10:01:12 WARN  db: slow query 1.8s (orders.list)
2026-11-11 10:02:40 ERROR db: connection timeout after 5s
2026-11-11 10:02:41 ERROR orders: failed to load cart id=8812
2026-11-11 10:03:05 ERROR db: connection timeout after 5s
2026-11-11 10:04:30 WARN  auth: 50 failed logins from 203.0.113.50
2026-11-11 10:05:02 ERROR db: connection timeout after 5s
2026-11-11 10:07:15 INFO  db: pool resized to 40
2026-11-11 10:09:44 ERROR payment: gateway returned 502
2026-11-11 10:12:00 INFO  orders: backlog cleared
EOF
cat > auth.log <<'EOF'
Nov 11 10:02:01 web01 sshd[2101]: Failed password for root from 203.0.113.50 port 51012 ssh2
Nov 11 10:02:03 web01 sshd[2101]: Failed password for root from 203.0.113.50 port 51012 ssh2
Nov 11 10:02:09 web01 sshd[2104]: Failed password for invalid user admin from 203.0.113.50 port 51020 ssh2
Nov 11 10:03:15 web01 sshd[2110]: Failed password for invalid user test from 198.51.100.7 port 40022 ssh2
Nov 11 10:05:40 web01 sshd[2122]: Accepted publickey for riya from 10.0.0.5 port 50110 ssh2
Nov 11 10:06:02 web01 sshd[2130]: Failed password for root from 203.0.113.50 port 51101 ssh2
Nov 11 11:15:20 web01 sshd[2201]: Accepted publickey for aman from 10.0.0.7 port 50222 ssh2
EOF"""

HOOK = hook('10:15 a.m.: customers report that the shop’s login page is broken and the website feels slow. The on-call dashboard is down, but Riya can SSH into the web server. She has an access log with 1,320 requests, an application log and the SSH auth log. In ten minutes she must answer: <b>how bad is it</b> (status codes), <b>since when</b> (requests per minute), <b>who</b> (top IPs), <b>where</b> (failing URLs), <b>how slow</b> (response times) and <b>is it an attack</b>? Every answer is a one-liner built from grep, cut, awk, sort, uniq and a few friends. This lesson builds each one on a realistic log and shows the real output.',
    ['read a web access log line by line and pick out fields with awk and cut',
     'count and rank anything with sort | uniq -c | sort -rn (status codes, IPs, URLs, user agents)',
     'slice logs by time, compute totals, averages and slow requests with awk, and follow live logs with tail -f',
     'spot brute-force attacks in auth logs and turn the one-liners into a reusable incident report'])
ROAD = roadmap([
    ('story', 'The story', 3, 'ten minutes, three logs'),
    ('decide', 'Which one-liner when?', 2, 'the quick chart'),
    ('definition', 'Log formats', 6, 'fields of an access log'),
    ('types', 'Kinds of questions', 5, 'count, rank, slice, compute'),
    ('commands', 'By field', 15, 'real runs on a real-looking log'),
    ('animation', 'See it happen', 4, 'from 1,320 lines to an answer'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'an incident report'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which one-liner? (decide in 5 seconds)', [
    ('How many of each status code?', "awk '{print $9}' access.log | sort | uniq -c | sort -rn", 'count'),
    ('Who sends the most requests?', "awk '{print $1}' … | sort | uniq -c | sort -rn | head", 'top IPs'),
    ('Which URLs fail?', "awk '$9>=500{print $7}' … | sort | uniq -c | sort -rn", 'failing URLs'),
    ('When did it start?', "awk '{print substr($4,14,5)}' … | uniq -c", 'per minute'),
    ('Only a time window', "awk '$4>=\"[11/Nov/2026:10:00\" && $4<\"[11/Nov/2026:10:15\"'", 'slice'),
    ('How slow?', "awk '{s+=$NF} END{print s/NR}'", 'average'),
    ('Errors in the app log', "grep -c ERROR app.log   ·   grep ERROR | cut -d' ' -f4- | sort | uniq -c", 'app'),
    ('Brute force on SSH?', "grep 'Failed password' auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c", 'security'),
])

cmap = concept_map(
    [('13.1', 'Combining', 'pipes and $( )'), ('6.5', 'awk', 'fields and patterns'), ('6.2', 'sort and uniq', 'count and rank')],
    ['the combined log format, field by field', 'count and rank: sort | uniq -c | sort -rn', 'time slices and per-minute counts', 'awk totals, averages, maximums', 'auth.log brute force', 'tail -f live filtering'],
    [('18.1', 'System logs', 'journalctl, rsyslog'), ('18.2', 'logrotate', 'rotated .gz logs'), ('19.3', 'fail2ban', 'automatic bans'), ('13.7', '100 one-liners', 'cheat sheet')],
    'Every log question is “filter, pick a field, count or compute, sort”. Learn the fields once and the one-liners write themselves.')

sc = (term(20, 14, 316, 156, ["$ awk '{print $9}' access.log | sort | uniq -c | sort -rn", ('    948 200', 'out'), ('    123 403', 'out'), ('    120 401', 'acc'), ('     71 404', 'out'), ('     41 500', 'out')], title='riya@web01: ~/lg', prompt='riya@web01:~/lg$', size=6.6, step=17)
      + t(352, 36, 'First look:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['120 × 401 at login', '41 × 500 errors', 'who? when?', 'one-liner each', 'then report'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Ten minutes, three logs</h2>
  <div class="story">
''' + puzzle('Riya’s first attempt to find the top IPs is <code>awk \'{print $1}\' access.log | uniq -c | sort -rn | head -3</code>. It shows the same IP three times with small counts. Then she counts 500 errors with <code>grep 500 access.log | wc -l</code> and gets far more than the real number. Finally she averages response times with <code>awk \'{s+=$11} END{print s/NR}\'</code> and gets 0. What is wrong with each one-liner?') + '''
    <p class="narration">Riya starts with the status codes: the fastest way to see how bad it is.</p>
''' + scene('A terminal: counting status codes in the access log shows 948 OK, 123 forbidden, 120 unauthorised (401), 71 not found and 41 server errors.', sc,
            '120 × <tspan font-weight="700" class="s-acc">401</tspan> on a normal day would be a handful.') + '''
K> Why look at status codes first?
A> They are the quickest health check. 2xx is fine, 3xx redirects, 4xx are the visitor’s problem (wrong password, missing page), 5xx are <b>our</b> problem. 120 failed logins and 41 server errors tell me where to look next.
R> And then?
A> Then I ask the same kind of question again and again: filter some lines, pick one field, count, sort. Who sent the 401s? When did they start? Which URL gives 500? Today: the log format and the one-liners for each question.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="One access log line cut into labelled pieces: IP address, time, request with method and URL, status code, bytes, user agent and response time, with the awk field numbers underneath.">'
       + label_box(10, 30, 110, 46, ['10.0.0.5', '$1 IP'], 'blue', 8.6)
       + label_box(126, 30, 150, 46, ['[11/Nov/2026:10:02:13', '$4 time'], 'amber', 8)
       + label_box(282, 30, 120, 46, ['"POST /login', '$6 $7 method URL'], 'green', 8)
       + label_box(408, 30, 60, 46, ['401', '$9 status'], 'red', 8.4)
       + label_box(474, 30, 56, 46, ['88', '$10 bytes'], 'violet', 8.4)
       + label_box(536, 30, 94, 46, ['… 0.020', '$NF seconds'], 'blue', 8.4)
       + t(320, 116, 'awk splits at spaces: the quotes and brackets stay inside the fields.', 9.6, 'acc', bold=True)
       + t(320, 140, 'The user agent ("python-requests/2.31") is $(NF-1) here.', 9.2, 'ink2')
       + t(320, 164, 'Learn these numbers once; every one-liner uses them.', 9.2, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Log analysis at four depths', [
    ('v', 'No jargon: a log line has labelled pieces', '      <p>Each request is one line; each piece has a position.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>tail -n 20 access.log</code>: the latest requests.</li>
        <li><code>grep -c ' 500 ' access.log</code>: how many server errors.</li>
        <li><code>awk '{print $1}' access.log | sort | uniq -c | sort -rn | head</code>: top visitors.</li>
        <li><code>tail -f access.log | grep --line-buffered ' 50[0-9] '</code>: watch errors live.</li>
      </ul>'''),
    ('i', 'The patterns', '''      <ul>
        <li><b>Count and rank:</b> <code>sort | uniq -c | sort -rn</code> (sort first, uniq only merges neighbours).</li>
        <li><b>Match a field, not the line:</b> <code>awk '$9==500'</code> instead of <code>grep 500</code> (500 also appears in sizes and times).</li>
        <li><b>Time windows:</b> the time field sorts as text within one day, so <code>$4 &gt;= "[11/Nov/2026:10:00"</code> works.</li>
        <li><b>Numbers:</b> <code>awk '{s+=$NF; if($NF&gt;m)m=$NF} END{print s/NR, m}'</code> for average and maximum.</li>
        <li><b>Rotated logs:</b> <code>zcat access.log.*.gz | …</code> or <code>zgrep</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: formats, locales and speed', '''      <ul>
        <li>This is the Apache/Nginx <b>combined</b> format plus <code>$request_time</code> at the end; your server’s <code>log_format</code> may differ, so check one line first.</li>
        <li>awk splits on runs of blanks; a URL with a space (rare, encoded as %20) would shift fields. <code>awk -F'"'</code> splits at quotes instead: field 2 is the request, field 6 the user agent.</li>
        <li><code>sort</code> is locale-aware; <code>LC_ALL=C sort</code> is several times faster on big logs and sorts bytes.</li>
        <li>For gigabyte logs, filter early (grep is very fast), sort late, and prefer awk associative arrays over sort | uniq for counting (one pass, no sort of every line).</li>
        <li><code>grep --line-buffered</code> (or <code>stdbuf -oL</code>) is needed after <code>tail -f</code>, otherwise output waits in a 4 KiB buffer.</li>
        <li>Logs are evidence: copy them before experimenting, and remember they may contain personal data.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Access logs and log one-liners</h2>
''' + def_block(
    'A <b>web access log</b> records one line per request: client IP, time, request line (method, URL, protocol), status code, bytes sent, referrer, user agent and often the response time. <b>Log analysis one-liners</b> combine filters (grep, awk patterns), field extraction (awk, cut) and aggregation (sort, uniq -c, awk sums) to answer questions such as “which IPs”, “which URLs”, “how many errors” and “since when”.',
    'Filter the lines, pick the field, count or compute, sort the answer.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Access log', 'One line per web request.'),
    ('Status code', '2xx ok, 3xx redirect, 4xx client, 5xx server.'),
    ('Combined format', 'The common Apache/Nginx layout.'),
    ('Field', 'One space-separated piece ($1, $9…).'),
    ('User agent', 'Which browser or tool made the request.'),
    ('Response time', 'Seconds to answer (last field here).'),
    ('Brute force', 'Many password guesses from one source.'),
    ('Rotated log', 'access.log.1, access.log.2.gz…'),
]) + '\n' + names('Where the names come from.', [
    ('log', 'ship’s logbook', 'Speed measured with a log of wood.'),
    ('uniq -c', 'count unique', 'Adjacent duplicates.'),
    ('401', 'Unauthorized', 'Wrong or no credentials.'),
    ('403', 'Forbidden', 'Not allowed.'),
    ('404', 'Not Found', 'No such page.'),
    ('500 / 502', 'Server error / bad gateway', 'Our side.'),
    ('auth.log', 'authentication log', 'Debian/Ubuntu; RHEL: /var/log/secure.'),
    ('tail -f', 'follow', 'Live view.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Status counts', "<code>awk '{print $9}' | sort | uniq -c</code>"),
    ('Top IPs', "<code>awk '{print $1}' | sort | uniq -c | sort -rn</code>"),
    ('Only 5xx', "<code>awk '$9&gt;=500'</code>"),
    ('Per minute', "<code>substr($4,14,5)</code>"),
    ('Average time', "<code>awk '{s+=$NF} END{print s/NR}'</code>"),
    ('Live', '<code>tail -f | grep --line-buffered</code>'),
]) + '\n' + lv + didyou('The default web log format was defined by NCSA httpd in 1993 (the “common log format”); Apache added referrer and user agent as the “combined” format. Thirty years later most tools still read exactly that layout.') + '''
EXAM> “How do you find the top 10 IP addresses in an access log?” → awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -10.
''' + qc('Why is <code>grep 500</code> a bad way to count server errors?', '500 can appear anywhere in the line (byte counts, times, URLs). Match the status field: awk \'$9==500\'.') + mistake("awk '{print $1}' access.log | uniq -c",
    "awk '{print $1}' access.log | sort | uniq -c | sort -rn",
    'uniq only merges identical neighbouring lines; without sort the same IP appears many times with small counts (real run).') + mistake("awk '{s+=$11} END{print s/NR}'",
    "awk '{s+=$NF} END{print s/NR}'   (check the field numbers on one line first)",
    'Field 11 is the quoted referrer "-", which counts as 0. The response time is the last field, $NF.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The kinds of log questions, and the fields you need</h2>
''' + table(['Field', 'awk', 'Example value', 'Questions'], [
    ['Client IP', '<code>$1</code>', '203.0.113.50', 'who, attacks, top visitors'],
    ['Time', '<code>$4</code>', '[11/Nov/2026:10:02:13', 'when, per minute/hour'],
    ['Method', '<code>$6</code>', '"POST', 'logins, API writes'],
    ['URL', '<code>$7</code>', '/login', 'which pages, failing endpoints'],
    ['Status', '<code>$9</code>', '401', 'health, errors'],
    ['Bytes', '<code>$10</code>', '88', 'traffic, big downloads'],
    ['User agent', '<code>-F\'"\' $6</code>', 'python-requests/2.31', 'bots, scripts'],
    ['Response time', '<code>$NF</code>', '0.020', 'slowness'],
], minw=520) + table(['Question type', 'Pattern', 'Example'], [
    ['Count', '<code>grep -c</code> / <code>awk \'cond{n++} END{print n}\'</code>', 'how many 500s'],
    ['Count per value', '<code>… | sort | uniq -c | sort -rn</code>', 'status codes, IPs'],
    ['Top N', '<code>… | head -N</code>', 'top 5 URLs'],
    ['Per time unit', '<code>substr($4,14,5) | uniq -c</code>', 'requests per minute'],
    ['Window', '<code>$4 &gt;= "…" &amp;&amp; $4 &lt; "…"</code>', '10:00–10:15'],
    ['Sum / average / max', 'awk accumulators', 'bytes, times'],
    ['Group + compute', 'awk arrays <code>a[$7]+=$NF</code>', 'average time per URL'],
    ['Live', '<code>tail -f | grep --line-buffered</code>', 'watch errors'],
], minw=480) + table(['Status', 'Meaning', 'Who must act'], [
    ['200', 'OK', '-'],
    ['301 / 302', 'redirect', '-'],
    ['401', 'not logged in / wrong password', 'user (or an attacker guessing)'],
    ['403', 'forbidden', 'user / config'],
    ['404', 'not found', 'broken link'],
    ['429', 'too many requests', 'client is rate-limited'],
    ['500', 'server error', 'developers'],
    ['502 / 503 / 504', 'bad gateway / unavailable / timeout', 'ops: backend down or slow'],
], minw=420) + qc('Which field would you count to find the busiest page?', '$7, the URL.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Counting, ranking, slicing and computing, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/lg</code>: <code>access.log</code> (1,320 requests on 11 Nov 2026 from 08:00 to 15:59, combined format with the response time at the end, including an incident around 10:02–10:07), <code>app.log</code> (10 application lines) and <code>auth.log</code> (7 SSH lines).</p>
''' + cmdcard_u(['first look during any incident', 'daily traffic reports'],
               ['grep for numbers that can appear in many fields'])(
    'count', "awk '{print $N}' | sort | uniq -c | sort -rn · grep -c", 'count and rank',
    'Pick the field with awk, <code>sort</code> so equal values are next to each other, <code>uniq -c</code> to count them, <code>sort -rn</code> to put the biggest first, <code>head</code> to keep the top. To count lines that match a condition, use <code>grep -c</code> or <code>awk \'cond\' | wc -l</code>.',
    "awk '{print $9}' access.log | sort | uniq -c | sort -rn", 'safe',
    [('$9', 'status codes', 'health'),
     ('$1', 'IPs', 'who'),
     ('$7', 'URLs', 'what'),
     ("-F'\"' $6", 'user agents', 'bots'),
     ('| head -5', 'top 5', 'focus'),
     ("awk '$9==500' | wc -l", 'count one value', 'exact'),
     ('grep -c', 'count lines', 'simple')],
    dict(setup=LG, cmd="cd ~/lg\nwc -l < access.log\nawk '{print $9}' access.log | sort | uniq -c | sort -rn\nawk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3", note='One IP, 203.0.113.50, stands out.'),
    [('qa', [
        dict(situation='The puzzle: uniq without sort, grep for a number.', setup=LG, cmd="cd ~/lg\nawk '{print $1}' access.log | uniq -c | sort -rn | head -3\necho \"grep 500: $(grep -c 500 access.log)   status 500: $(awk '$9==500' access.log | wc -l)\"", why='Unsorted, uniq only merged neighbours. grep 500 also matched byte counts and times.')]),
     ('sys', [
        dict(situation='Errors only, ranked by URL.', setup=LG, cmd="cd ~/lg; awk '$9>=500 {print $7}' access.log | sort | uniq -c | sort -rn | head -4", why='Which endpoints fail on our side (5xx).')]),
    ],
    anat=anatomy([("awk '{print $9}'", 'cmd', 'pick a field'), ('sort', 'opt', 'group equal values'), ('uniq -c', 'opt', 'count each'), ('sort -rn | head', 'arg', 'biggest first, top N')], 'The most-used pattern in log analysis.')
) + cmdcard_u(['finding when an incident started and ended', 'traffic per hour'],
               ['comparing times across different days as text'])(
    'time', "substr($4,14,5) · uniq -c · $4 >= \"[…\" && $4 < \"[…\"", 'slicing by time',
    'The time field looks like <code>[11/Nov/2026:10:02:13</code>. Characters 14–15 are the hour, 14–18 hour:minute. Because the log is in time order, <code>uniq -c</code> on the minute gives requests per minute. For a window, compare the field as text: within one day the format sorts correctly.',
    "awk '{print substr($4,14,5)}' access.log | uniq -c", 'safe',
    [('substr($4,14,2)', 'hour', 'per hour'),
     ('substr($4,14,5)', 'hour:minute', 'per minute'),
     ('$4 >= "[…:10:00"', 'from', 'window start'),
     ('$4 < "[…:10:15"', 'until', 'window end'),
     ('sed -n "/10:00/,/10:15/p"', 'range by text', 'quick'),
     ('awk … | sort | uniq -c | sort -rn | head -1', 'busiest minute', 'peak')],
    dict(setup=LG, cmd="cd ~/lg\necho 'requests per hour:'; awk '{print substr($4,14,2)\":00\"}' access.log | uniq -c\necho '401s per minute around 10:00:'; awk '$9==401 {print substr($4,14,5)}' access.log | uniq -c | awk '$1>5'", note='Hour 10 has extra traffic; 401s jump from 10:02 to 10:07: the incident window.'),
    [('sys', [
        dict(situation='Everything in the incident window.', setup=LG, cmd="cd ~/lg\nawk '$4 >= \"[11/Nov/2026:10:00\" && $4 < \"[11/Nov/2026:10:15\"' access.log > window.log\nwc -l < window.log; awk '{print $9}' window.log | sort | uniq -c | sort -rn | head -3", why='Save the window once, then ask more questions about it.')]),
    ]
) + cmdcard_u(['slowness, traffic volume, capacity planning'],
               ['averages alone (one slow request hides in them)'])(
    'compute', "awk '{s+=$NF} END{print s/NR}' · arrays a[$7]+=$NF", 'sums, averages and maximums',
    'awk keeps numbers in variables across lines: sum with <code>s+=$NF</code>, count with <code>n++</code>, maximum with <code>if($NF&gt;m)m=$NF</code>, and print in <code>END</code>. With associative arrays you can do it per URL or per IP in one pass. Use <code>printf</code> for neat columns.',
    "awk '{s+=$NF} END{printf \"%.3f\\n\", s/NR}' access.log", 'safe',
    [('s+=$NF', 'sum', 'totals'),
     ('s/NR', 'average', 'typical'),
     ('if($NF>m)m=$NF', 'maximum', 'worst case'),
     ('a[$7]+=$NF; n[$7]++', 'per URL', 'group by'),
     ('$NF>1', 'slow requests', 'filter'),
     ('sort -k2 -rn', 'sort by a column', 'rank'),
     ('printf "%-15s %6.3f"', 'columns', 'reports')],
    dict(setup=LG, cmd="cd ~/lg\nawk '{s+=$NF; if($NF>m){m=$NF; u=$7}} END{printf \"avg %.3f s, max %.3f s (%s)\\n\", s/NR, m, u}' access.log\nawk '$NF>1' access.log | wc -l\nawk '{bytes+=$10} END{printf \"%.1f MB sent\\n\", bytes/1e6}' access.log", note='The slowest request and the number of requests over 1 second.'),
    [('data', [
        dict(situation='Average time per URL, slowest first.', setup=LG, cmd="cd ~/lg; awk '{t[$7]+=$NF; n[$7]++} END{for(u in t) printf \"%-18s %6.3f s  (%d req)\\n\", u, t[u]/n[u], n[u]}' access.log | sort -k2 -rn | head -4", why='One pass, grouped by URL; 500s make /api endpoints slow.')]),
     ('qa', [
        dict(situation='The puzzle: the wrong field gives 0.', setup=LG, cmd="cd ~/lg; head -1 access.log | awk '{print \"$11 =\", $11, \"  $NF =\", $NF}'\nawk '{s+=$11} END{print \"avg of $11:\", s/NR}' access.log", why='$11 is the quoted referrer "-": not a number. Always check field numbers on one line.')]),
    ]
) + cmdcard_u(['brute-force detection', 'who logged in, from where'],
               ['banning by hand forever (use fail2ban, Lesson 19.3)'])(
    'auth', "grep 'Failed password' · grep -oE 'from [0-9.]+' · Accepted", 'security logs',
    'SSH writes every login attempt to <code>/var/log/auth.log</code> (Debian/Ubuntu) or <code>/var/log/secure</code> (RHEL), or to the journal (<code>journalctl -u ssh</code>). Failed and accepted logins have fixed wording, so grep and <code>grep -o</code> extract IPs and users.',
    "grep 'Failed password' auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -rn", 'safe',
    [('Failed password', 'wrong password', 'attacks'),
     ('invalid user', 'user does not exist', 'scanning'),
     ('Accepted', 'successful login', 'audit'),
     ("grep -oE 'from [0-9.]+'", 'the source IP', 'who'),
     ("grep -oE 'for (invalid user )?[a-z]+'", 'the target user', 'what'),
     ('journalctl -u ssh', 'same, from the journal', 'systemd systems')],
    dict(setup=LG, cmd="cd ~/lg\ngrep 'Failed password' auth.log | grep -oE 'from [0-9.]+' | sort | uniq -c | sort -rn\ngrep 'Failed password' auth.log | grep -oE 'for (invalid user )?[a-z]+' | sed 's/for //' | sort | uniq -c | sort -rn\ngrep Accepted auth.log | awk '{print $3, $9, \"from\", $11}'", note='203.0.113.50 is guessing root and admin over SSH too: the same attacker as the web 401s.'),
    [('sec', [
        dict(situation='Same IP in both logs?', setup=LG, cmd="cd ~/lg; comm -12 <(grep 'Failed password' auth.log | grep -oE '([0-9]+\\.){3}[0-9]+' | sort -u) <(awk '$9==401{print $1}' access.log | sort -u)", why='comm -12 prints IPs present in both lists (Lesson 13.1).')]),
    ]
) + undo('Reading logs changes nothing; acting on them can.', [
    ('Analysis looks wrong:', 'check one line’s fields first: <code>head -1 access.log | awk \'{for(i=1;i&lt;=NF;i++) print i, $i}\'</code>.'),
    ('Log rotated mid-incident:', 'include <code>access.log.1</code> and <code>zcat access.log.*.gz</code>.'),
    ('Blocked the wrong IP:', 'remove the firewall rule (Lesson 19.1); check for NAT/proxy IPs before blocking.'),
    ('Big log is slow:', 'filter first, <code>LC_ALL=C</code>, count with awk arrays.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="awk '{print $9' access.log", meaning='Missing closing brace in the awk program.', fix="awk '{print $9}'"),
    dict(setup=LG, cmd="cd ~/lg; grep -c 'HTTP/2.0' access.log", meaning='grep -c prints 0 and exits 1 when nothing matches.', fix='Not an error: status 1 means no match.'),
    dict(cmd="tail -n 5 /var/log/auth.log", meaning='This machine has no auth.log: it logs SSH to the journal only (on other systems auth.log exists but is readable only by root and group adm).', fix='journalctl -u ssh, or sudo tail /var/log/auth.log.'),
    dict(setup=LG, cmd="cd ~/lg; zcat access.log > /dev/null", meaning='zcat on a file that is not gzip-compressed.', fix='Use cat, or zcat only on .gz files.'),
]) + qc('Which pattern gives requests per minute in a time-ordered log?', "awk '{print substr($4,14,5)}' access.log | uniq -c") + '''
'''
cards = cards + '</section>\n'

def funnel(k):
    labels = [('1,320 lines', 'all requests', 'blue'), ('120 lines', "awk '$9==401'", 'amber'), ('120 IPs', "{print $1}", 'amber'), ('1 value', 'sort | uniq -c', 'green'), ('1 answer', 'sort -rn | head -1', 'green')]
    o = ''
    for i in range(k + 1):
        w = 320 - i * 55
        o += label_box(180 - w / 2, 10 + i * 34, w, 30, [f'{labels[i][0]} · {labels[i][1]}'], labels[i][2], 7.6)
    return o
see_cmds = [['$ wc -l < access.log', ('1320', 'out')], ["$ awk '$9==401' access.log | wc -l", ('120', 'out')], ["$ … | awk '{print $1}' | head -2", ('203.0.113.50', 'out'), ('203.0.113.50', 'out')], ['$ … | sort | uniq -c', ('    120 203.0.113.50', 'out')], ['$ … | sort -rn | head -1', ('    120 203.0.113.50', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/lg', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['All lines.', 'Filter.', 'Pick a field.', 'Count.', 'Rank.'])]
behind = [funnel(k) for k in range(5)]
two = anim_two('From 1,320 lines to one answer', 'Behind the screen: the funnel',
               'A terminal narrowing the access log: all lines, only 401s, only their IPs, counted, ranked.',
               'A funnel of boxes getting narrower: 1,320 lines, 120 lines, 120 IPs, one counted value, one answer.', see, behind,
               ['All.', 'Filter.', 'Field.', 'Count.', 'Rank.'],
               ['all', 'filter', 'field', 'count', 'rank'])

def bars(k):
    data = [('10:00', 0), ('10:01', 0), ('10:02', 20), ('10:03', 20), ('10:04', 20), ('10:05', 20), ('10:06', 20), ('10:07', 20), ('10:08', 0)]
    o = ''
    for i, (m, v) in enumerate(data[:k * 3 + 3]):
        h = v * 4
        o += f'<rect x="{20 + i * 36}" y="{140 - h}" width="28" height="{h}" class="b-{"red" if v > 10 else "blue"}" rx="2"/>' + t(34 + i * 36, 156, m[3:], 7.6, 'ink2')
    o += t(180, 178, ['10:00–10:02: normal…', '10:02: the attack starts', '10:08: it stops (blocked)'][k], 9, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', '401s per minute',
              'uniq -c on the minute shows exactly when it started and stopped.',
              "awk '$9==401{print substr($4,14,5)}' access.log | uniq -c", 'Bar chart of failed logins per minute between 10:00 and 10:08: none, then 20 per minute from 10:02 to 10:07, then none again.', [bars(k) for k in range(3)],
              ['Before.', 'Start.', 'Stop.'], hid='scenario-minutes')

dx = dissect('Layer by layer: making log one-liners fast and correct',
    'Each layer has a real command and output from our build machine.', [
    dict(key='fields', name='Field map', sub='check first', why='Right numbers.', how='Print every field.', impl='awk loop.', used='New formats.',
         setup=LG, cmd="cd ~/lg; head -1 access.log | awk '{for(i=1;i<=NF;i++) printf \"%s=%s  \", i, $i; print \"\"}'"),
    dict(key='quote', name='Split at quotes', sub='-F\'"\'', why='Spaces inside fields.', how='Quote-separated.', impl='$2 request, $6 agent.', used='User agents.',
         setup=LG, cmd="cd ~/lg; awk -F'\"' '{print $6}' access.log | sort | uniq -c | sort -rn"),
    dict(key='speed', name='One pass with arrays', sub='no sort', why='Big logs.', how='a[$1]++.', impl='Hash table.', used='GB logs.',
         setup=LG, cmd="cd ~/lg; awk '{n[$9]++} END{for(s in n) print n[s], s}' access.log | sort -rn | head -3"),
    dict(key='live', name='Live view', sub='tail -f', why='Watch it happen.', how='--line-buffered.', impl='Follows the file.', used='Incidents.',
         setup=LG, cmd="cd ~/lg; (sleep 0.5; echo '10.0.0.9 - - [11/Nov/2026:16:00:01 +0530] \"GET /api/orders HTTP/1.1\" 500 120 \"-\" \"curl/8.5.0\" 1.900' >> access.log) &\ntimeout 1.5 tail -n 0 -f access.log | grep --line-buffered '\" 50[0-9] ' | awk '{print \"LIVE 5xx:\", $1, $7, $9}'; true"),
], hint='From field numbers to live monitoring. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>The funnel, and the attack per minute</h2>
''' + two + s1 + dx + qc('Why does counting with an awk array not need sort?', 'awk keeps a counter per value in memory in one pass; only the small final list needs sorting.') + '''
</section>
'''

VAR = variations('Twenty more log one-liners. All were really run on our build machine on the sample logs.', [
    ('Access log: who and what', [
        dict(title='Unique visitors', setup=LG, cmd="awk '{print $1}' ~/lg/access.log | sort -u | wc -l", why='sort -u then count.'),
        dict(title='Top 3 URLs', setup=LG, cmd="awk '{print $7}' ~/lg/access.log | sort | uniq -c | sort -rn | head -3", why='The busiest pages.'),
        dict(title='Top URLs without static files', setup=LG, cmd="awk '$7 !~ /^\\/static/ {print $7}' ~/lg/access.log | sort | uniq -c | sort -rn | head -3", why='!~ excludes a pattern.'),
        dict(title='Methods used', setup=LG, cmd="awk '{print $6}' ~/lg/access.log | tr -d '\"' | sort | uniq -c", why='tr removes the quote.'),
        dict(title='Bots and scripts', setup=LG, cmd="awk -F'\"' '$6 ~ /bot|curl|python/ {print $6}' ~/lg/access.log | sort | uniq -c | sort -rn", why='Non-browser traffic.'),
        dict(title='404s: broken links', setup=LG, cmd="awk '$9==404 {print $7}' ~/lg/access.log | sort | uniq -c | sort -rn | head -3", why='Pages people ask for that do not exist.'),
        dict(title='One IP’s activity', setup=LG, cmd="grep '^203.0.113.50 ' ~/lg/access.log | awk '{print $7, $9}' | sort | uniq -c | sort -rn | head -3", why='What exactly did it do?'),
        dict(title='Status per IP for the top attacker', setup=LG, cmd="awk '$1==\"203.0.113.50\"{print $9}' ~/lg/access.log | sort | uniq -c | sort -rn", why='Mostly 401: password guessing.'),
    ]),
    ('Time and numbers', [
        dict(title='Busiest minute', setup=LG, cmd="awk '{print substr($4,14,5)}' ~/lg/access.log | uniq -c | sort -rn | head -1", why='Peak load.'),
        dict(title='First and last error', setup=LG, cmd="awk '$9>=500{print substr($4,14,8)}' ~/lg/access.log | sed -n '1p;$p'", why='When 5xx started and stopped.'),
        dict(title='Error rate in percent', setup=LG, cmd="awk '{n++; if($9>=500)e++} END{printf \"%.1f%% server errors\\n\", 100*e/n}' ~/lg/access.log", why='The number managers ask for.'),
        dict(title='Slowest 3 requests', setup=LG, cmd="sort -k12 -rn ~/lg/access.log | head -3 | awk '{print $NF, $7, $9}'", why='Sort numerically by the last column.'),
        dict(title='Traffic per hour in KB', setup=LG, cmd="awk '{kb[substr($4,14,2)]+=$10/1024} END{for(h in kb) printf \"%s:00 %6.0f KB\\n\", h, kb[h]}' ~/lg/access.log | sort", why='Group bytes by hour.'),
        dict(title='95th percentile response time', setup=LG, cmd="awk '{print $NF}' ~/lg/access.log | sort -n | awk '{a[NR]=$1} END{print \"p95:\", a[int(NR*0.95)]}'", why='Better than the average for “how slow for most users”.'),
    ]),
    ('App and auth logs', [
        dict(title='Errors by component', setup=LG, cmd="grep ERROR ~/lg/app.log | awk '{print $4}' | sort | uniq -c | sort -rn", why='db: is the main problem.'),
        dict(title='Same error messages grouped', setup=LG, cmd="grep ERROR ~/lg/app.log | cut -d' ' -f4- | sort | uniq -c | sort -rn", why='Counting identical messages.'),
        dict(title='Lines around the first ERROR', setup=LG, cmd="grep -m1 -B1 -A1 ERROR ~/lg/app.log", why='Context: what happened just before.'),
        dict(title='Errors and warnings with line numbers', setup=LG, cmd="grep -nE 'ERROR|WARN' ~/lg/app.log | cut -c1-60", why='-n for jumping into the file later.'),
        dict(title='SSH users who logged in', setup=LG, cmd="grep Accepted ~/lg/auth.log | awk '{print $9}' | sort -u", why='Audit trail.'),
        dict(title='Attackers with more than 2 failures', setup=LG, cmd="grep 'Failed password' ~/lg/auth.log | grep -oE 'from [0-9.]+' | awk '{print $2}' | sort | uniq -c | awk '$1>2{print $2}'", why='Candidates for blocking (or fail2ban).'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Log one-liners at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['5xx', 'on-call'], 'red', 8.6), '1. Incident triage',
              'Before dashboards load, on-call engineers run status counts, per-minute errors and top failing URLs on the server.', ['Alert', '*one-liners', 'cause']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['401', 'security'], 'amber', 8.6), '2. Spotting attacks',
    'A spike of 401s or SSH failures from one IP is brute force; the same one-liners feed block lists and fail2ban rules.', ['Spike', '*top IPs', 'block']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['p95', 'SRE'], 'blue', 8.6), '3. Performance reviews',
    'Average and p95 response time per endpoint show which API needs work.', ['Log', '*awk arrays', 'slow endpoints']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['404', 'SEO'], 'green', 8.6), '4. Website health',
    'Top 404 URLs reveal broken links after a redesign; marketing gets the list.', ['Log', '*$9==404', 'fix links']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cron', 'reports'], 'violet', 8.6), '5. Daily reports',
    'A cron job mails yesterday’s traffic, errors and top pages, built from the same one-liners (Lesson 17.4).', ['Midnight', '*script', 'email']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company. IP addresses are from documentation ranges.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Last 3 requests', scenario='What is happening now?', setup=LG, cmd="tail -n 3 ~/lg/access.log | cut -c1-70", explain='tail.'),
    dict(level='b', title='Server errors count', scenario='How bad?', setup=LG, cmd="awk '$9>=500' ~/lg/access.log | wc -l", explain='Field test.'),
    dict(level='i', title='Status codes', scenario='Health.', setup=LG, cmd="awk '{print $9}' ~/lg/access.log | sort | uniq -c | sort -rn | head -3", explain='Count and rank.'),
    dict(level='i', title='Top attacker', scenario='Security.', setup=LG, cmd="awk '$9==401{print $1}' ~/lg/access.log | sort | uniq -c | sort -rn | head -1", explain='401 by IP.'),
    dict(level='a', title='Slowest endpoint', scenario='Performance.', setup=LG, cmd="awk '{t[$7]+=$NF;n[$7]++} END{for(u in t) print t[u]/n[u], u}' ~/lg/access.log | sort -rn | head -1 | awk '{printf \"%s %.3f s\\n\", $2, $1}'", explain='Average per URL.'),
], extra=build_up('the incident answer', 'Riya builds the final answer for her manager step by step.', LG, [
    ("cd ~/lg; awk '$9==401' access.log | wc -l", '1. How many failed logins?'),
    ("cd ~/lg; awk '$9==401{print $1}' access.log | sort | uniq -c | sort -rn | head -1", '2. From whom?'),
    ("cd ~/lg; awk '$1==\"203.0.113.50\" && $9==401{print substr($4,14,5)}' access.log | sed -n '1p;$p' | paste -sd' '", '3. From when to when?'),
    ("cd ~/lg; n=$(awk '$9==401' access.log | wc -l); top=$(awk '$9==401{print $1}' access.log | sort | uniq -c | sort -rn | head -1); w=$(awk '$1==\"203.0.113.50\" && $9==401{print substr($4,14,5)}' access.log | sed -n '1p;$p' | paste -sd-); echo \"$n failed logins; top source: ${top##* } ($(echo ${top% *}) times, $w). SSH: $(grep -c 'Failed password.*203.0.113.50' auth.log) failures from the same IP.\" | tr -s ' '", '4. One sentence for the manager.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Count lines that match', 'grep -c / awk cond', 'Fast.', 'grep | wc -l on numbers.'),
    ('Count per value', 'sort | uniq -c | sort -rn', 'Classic.', 'uniq without sort.'),
    ('Huge logs, counting', 'awk arrays', 'One pass.', 'Sorting every line.'),
    ('Numbers: sum, avg, p95', 'awk (+ sort -n)', 'Exact.', 'A spreadsheet during an incident.'),
    ('Live', 'tail -f | grep --line-buffered', 'Immediate.', 'Rerunning the whole analysis.'),
    ('Long-term dashboards', 'ELK, Loki, GoAccess', 'History, graphs.', 'One-liners as the only monitoring.'),
]) + keys('Field cheat sheet (combined format + time).', [
    ('$1', 'IP', 'who'),
    ('$4', 'time', 'when'),
    ('$6 $7', 'method, URL', 'what'),
    ('$9', 'status', 'result'),
    ('$10', 'bytes', 'size'),
    ('$NF', 'response time', 'speed'),
]) + scriptit('incident.sh', 'Produce an incident summary from an access log: totals, status codes, error rate, top IPs for 401/5xx, failing URLs, the busiest minute and the slowest endpoint, with an optional time window.',
'''log=${1:-$HOME/lg/access.log}; from=${2:-00:00}; to=${3:-23:59}
[ -r "$log" ] || { echo "cannot read $log" >&2; exit 1; }
w=$(mktemp); trap 'rm -f "$w"' EXIT
awk -v f="$from" -v t="$to" '{m=substr($4,14,5)} m>=f && m<=t' "$log" > "$w"
echo "== ${log##*/}  $from-$to  ($(wc -l < "$w") requests) =="
echo "status codes:"; awk '{print $9}' "$w" | sort | uniq -c | sort -rn | head -4 | sed 's/^ */  /'
awk '{n++; if($9>=500)e++} END{printf "server error rate: %.1f%%\\n", n?100*e/n:0}' "$w"
echo "top 401 sources:"; awk '$9==401{print $1}' "$w" | sort | uniq -c | sort -rn | head -2 | sed 's/^ */  /'
echo "failing URLs (5xx):"; awk '$9>=500{print $7}' "$w" | sort | uniq -c | sort -rn | head -2 | sed 's/^ */  /'
echo "busiest minute: $(awk '{print substr($4,14,5)}' "$w" | uniq -c | sort -rn | head -1 | awk '{print $2" ("$1" req)"}')"
awk '{t[$7]+=$NF;n[$7]++} END{for(u in t) print t[u]/n[u], u}' "$w" | sort -rn | head -1 | awk '{printf "slowest endpoint: %s (%.3f s avg)\\n", $2, $1}' ''',
'<p>Run without arguments, so it reports on the whole day of the sample log (try <code>incident.sh ~/lg/access.log 10:00 10:15</code> on your PC).</p>', expect='any') + puzzle_answer('<b>1.</b> <code>uniq -c</code> only merges <i>neighbouring</i> identical lines; the IPs were not sorted, so each run of the same IP was counted separately. Add <code>sort</code> before <code>uniq -c</code>. <b>2.</b> <code>grep 500</code> matches “500” anywhere: in byte counts, in times like 0.500 and in URLs. Test the status field: <code>awk \'$9==500\'</code>. <b>3.</b> Field 11 is the quoted referrer <code>"-"</code>, which awk treats as 0. The response time is the last field: <code>$NF</code>. Print one line’s fields first to get the numbers right.') + qc('Which command shows only new log lines as they arrive?', 'tail -f (with grep --line-buffered if you filter).') + '''
</section>
'''

_sh.run_sh('rm -rf ~/lg', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-combining-commands-pipes-subshells-substitution/">Lesson 13.1</a> (combining commands) and <a href="../../06-text-processing/05-awk-fields-patterns-and-reports/">Lesson 6.5</a> (awk).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
