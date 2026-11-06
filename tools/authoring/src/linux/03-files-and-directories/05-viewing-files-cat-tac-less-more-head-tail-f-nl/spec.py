import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='03-files-and-directories', lesson='05-viewing-files-cat-tac-less-more-head-tail-f-nl', n='3.5',
    module_label='Module 3 · Working with files and directories',
    title='Viewing files: cat, tac, less, more, head, tail -f, nl and wc',
    desc='Read files without an editor: cat and tac (-n, -b, -s, -A, joining files), head and tail (-n, -n +N, -c, line ranges, skipping CSV headers), tail -f, -F and --pid for live logs and log rotation, less and more (search, G, F, -S, -N), nl (-ba, -bp, -nrz, -w, -s) and wc (-l, -w, -c, -m). Each command explained, then used by admins, data engineers, developers, DBAs, QA, security and ML teams, with real outputs.',
    og_desc='A 2 GB log and no editor: tail, tail -F, less, head, cat -A, nl and wc explained with real outputs, for every IT role.',
    minutes=40, level='Beginner → Advanced',
    lead='A production log is 2 GB and the server has no screen. This lesson shows how to read only the part you need: the start, the end, a range, live new lines, or just counts, and how every IT role uses these commands.',
    chips=['Commands by field', 'Which command when?', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = r"""# Read a log and a CSV without an editor
printf '2026-11-06 10:00:01 INFO start\n2026-11-06 10:00:05 ERROR db timeout\n2026-11-06 10:00:07 WARN slow query\n2026-11-06 10:00:09 ERROR disk full\n' > app.log
printf 'id,name,marks\n1,Asha,91\n2,Ravi,78\n3,Meena,85\n' > marks.csv
head -n 2 app.log
tail -n 1 app.log
cat -n marks.csv
tail -n +2 marks.csv | wc -l
tac app.log | head -n 1
wc app.log
"""

RUN = dict(
    heading='Read a log and a CSV',
    intro='<p>The script creates a small log and a CSV, then reads them six different ways. Change the numbers and run again.</p>',
    code=MAIN,
    anno=[
        ('head -n 2 app.log', 'The two oldest entries.'),
        ('tail -n 1 app.log', 'The newest entry.'),
        ('cat -n marks.csv', 'The whole small file, numbered.'),
        ('tail -n +2 marks.csv | wc -l', 'Data rows without the header: 3.'),
        ('tac app.log | head -n 1', 'Reverse, then first = the newest line again.'),
        ('wc app.log', 'Lines, words, bytes.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. How many students are in marks.csv?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which numbers are printed? Then run.',
             code='seq 1 20 > n.txt\nhead -n 5 n.txt | tail -n 2\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this prints the last 2 lines instead of skipping the header. Fix it.',
             code="printf 'id,name\\n1,A\\n2,B\\n3,C\\n' > d.csv\ntail -n 2 d.csv\n"),
        dict(label='4 · Your turn', hint='Show the file with tabs and line ends visible.',
             code="printf 'a\\tb\\n' > t.txt\ncat -A t.txt\n"),
        dict(label='5 · Challenge', hint='Print lines 8 to 10 of a 20-line file.',
             code='seq 1 20 > n.txt\nhead -n 10 n.txt | tail -n 3\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: pagers and live logs',
    intro='<p>less, more and long-running tail -f need a real terminal. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Page through a long file', cmd='less /etc/services', output='# Network services, Internet style\n#\ntcpmux          1/tcp\necho            7/tcp\n...\n/etc/services', note='Typical. Space, b, /http, n, G, q. Try <code>-N</code> for numbers.'),
        dict(title='2 · Follow the system log (Ubuntu)', cmd='sudo tail -f /var/log/syslog', output='Nov  6 10:52:01 laptop CRON[2211]: (root) CMD (command -v debian-sa1 > /dev/null && debian-sa1 1 1)\n(new lines keep appearing; Ctrl+C to stop)', note='Typical. On systems that only use journald: <code>journalctl -f</code>.'),
        dict(title='3 · Follow two logs at once', cmd='tail -F app.log error.log', output='==> app.log <==\n10:52:03 INFO request 200\n\n==> error.log <==\n10:52:04 ERROR timeout', note='Typical. Each block shows which file the lines came from.'),
        dict(title='4 · Characters vs bytes', cmd="printf 'नमस्ते\\n' | wc -m -c", output=pc("printf 'नमस्ते\\n' | wc -m -c"), note='Recorded on our build machine: 7 characters, 19 bytes.'),
        dict(title='5 · Fix a garbled terminal after cat on a binary', cmd='reset', output='(the screen clears and the prompt works normally again)', note='Typical. Type it even if your typing is invisible, then press Enter.'),
    ],
)

TRACE = dict(
    heading='Reading parts of a file',
    intro='<p>Step through and compare what each command prints from the same 10-line file.</p>',
    code='''seq 1 10 > n.txt
head -n 3 n.txt
tail -n 2 n.txt
tail -n +9 n.txt
head -n 6 n.txt | tail -n 2
wc -l n.txt
''',
    notes={1: 'Setup :: Ten numbered lines (seq, Lesson 3.6).', 2: 'head :: The first 3.', 3: 'tail :: The last 2.', 4: 'From line 9 :: 9 and 10.',
           5: 'Range :: Lines 5 and 6.', 6: 'Count :: 10 lines.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a data engineer validating a file, an admin finding the latest errors, and a DBA checking that a dump completed.'
EXAMPLES = [
    dict(level='b', tag='Data engineering', title='Validate a CSV before loading',
         problem='<p>Before loading <code>sales.csv</code>, print its header, the first data row and the number of data rows.</p>',
         inp='sales.csv: header + 3 rows',
         approach=['head -n 1 for the header; sed/head for row 1.', 'tail -n +2 | wc -l for the count.'],
         code='''printf 'date,region,amount\\n2026-11-01,North,1200\\n2026-11-01,South,950\\n2026-11-02,North,1310\\n' > sales.csv
echo "header: $(head -n 1 sales.csv)"
echo "first:  $(head -n 2 sales.csv | tail -n 1)"
echo "rows:   $(tail -n +2 sales.csv | wc -l)"
''',
         notes={2: 'Header :: Check column names.', 3: 'Row 1 :: Check the format of the data.', 4: 'Count :: Compare with the source system.'},
         tryit='Add a row without a final newline (printf without \\n). What does the count say?'),
    dict(level='i', tag='System admin', title='The latest errors, newest first',
         problem='<p>From a log, show the 2 most recent ERROR lines, newest first, with their line numbers in the file.</p>',
         inp='app.log with mixed INFO / ERROR lines',
         approach=['Number the lines first (cat -n), so the numbers refer to the original file.', 'Filter ERROR, then tac and head.'],
         code='''printf 'INFO a\\nERROR one\\nINFO b\\nERROR two\\nINFO c\\nERROR three\\n' > app.log
cat -n app.log | grep ERROR | tac | head -n 2
''',
         notes={2: 'Pipeline :: number → keep errors → newest first → take 2.'},
         tryit='Use <code>grep -n</code> instead of cat -n. Is the result the same?'),
    dict(level='a', tag='DBA', title='Did every dump finish?',
         problem='<p>Several dump files should each end with “-- Dump completed”. Print OK or BROKEN for each.</p>',
         inp='a.sql (complete), b.sql (cut off)',
         approach=['tail -n 1 on each file.', 'Compare in a loop.'],
         code='''printf 'INSERT ...;\\n-- Dump completed on 2026-11-06\\n' > a.sql
printf 'INSERT ...;\\nINSERT INTO big VAL' > b.sql
for f in *.sql; do
  if tail -n 1 "$f" | grep -q '^-- Dump completed'; then echo "OK      $f"; else echo "BROKEN  $f"; fi
done
''',
         notes={4: 'Check :: Only the last line matters; tail reads it instantly even on 50 GB.'},
         tryit='Also print the size of each file with <code>wc -c</code>.'),
]

QUIZ = mix([
    dict(q='Which command shows the last 20 lines of a log?', options=['head -n 20 log', 'tail -n 20 log', 'cat -20 log', 'less -20 log'], answer=1,
         why='tail shows the end.'),
    dict(q='How do you skip the first (header) line of a CSV?', options=['tail -n 2 f.csv', 'tail -n +2 f.csv', 'head -n -1 f.csv', 'cat -s f.csv'], answer=1,
         why='+2 = start at line 2.'),
    dict(q='A log is rotated every night. Which follows it reliably?', options=['tail -f', 'tail -F', 'less -f', 'cat -f'], answer=1,
         why='-F follows the name and reopens the new file.'),
    dict(q='What does ^M at the end of lines in cat -A mean?', options=['A tab', 'Windows line ending (CR)', 'An empty line', 'A binary file'], answer=1,
         why='\\r shown as ^M; CRLF files come from Windows.'),
    dict(q='In less, how do you search for ERROR?', options=['Ctrl+F ERROR', '/ERROR', ':find ERROR', 's ERROR'], answer=1,
         why='/ searches forward, n for the next match.'),
    dict(q='Why is tail -n 5 bigfile instant, but cat bigfile | tail -n 5 slow?', options=['cat is broken', 'tail can seek to the end only when it has the file', 'pipes compress data', 'it is not slower'], answer=1,
         why='A pipe is not seekable; all data must flow through it.'),
    dict(q='wc -l counts…', options=['words', 'newline characters', 'bytes', 'non-empty lines'], answer=1,
         why='A last line without a newline is not counted.'),
    dict(q='nl numbers which lines by default?', options=['all', 'non-empty lines', 'odd lines', 'none'], answer=1,
         why='Default -bt; use -ba for all lines.'),
])

REVISION = [
    '<code>cat</code> short files and joining; <code>-n</code> number, <code>-b</code> non-empty, <code>-s</code> squeeze, <code>-A</code> show ^I ^M $.',
    '<code>tac</code> reverses lines: newest log lines first.',
    '<code>head -n N</code> first lines, <code>-n -N</code> all but last N, <code>-c</code> bytes.',
    '<code>tail -n N</code> last lines, <code>-n +N</code> from line N (skip header), range: <code>head -n 210 | tail -n 11</code>.',
    '<code>tail -f</code> follow; <code>-F</code> survive rotation; <code>--pid</code> stop with a process; Ctrl+C stops.',
    '<code>less</code>: Space/b, /word, n, g/G, F (follow), -S, -N, q. <code>more</code> is the older pager.',
    '<code>nl</code>: -ba all, -bp pattern, -nrz zeros, -w width, -s separator.',
    '<code>wc</code>: -l lines (newlines), -w words, -c bytes, -m characters; <code>wc -l &lt; f</code> = number only.',
]

FAQ = [
    ('How do you view a large file in Linux?', 'less file: it shows one screen at a time and does not load the whole file. Search with /word, quit with q.'),
    ('How do you see the last lines of a log in real time?', 'tail -f file (or tail -F for logs that get rotated). Ctrl+C stops it.'),
    ('What is the difference between less and more?', 'more mostly scrolls forward; less scrolls both ways, searches, follows (F) and opens big files quickly.'),
    ('How do you print a specific range of lines?', 'head -n END file | tail -n COUNT, or sed -n START,ENDp file.'),
    ('What is the difference between cat -n and nl?', 'cat -n numbers all lines; nl by default numbers only non-empty lines and has format options.'),
    ('How do you count lines, words and characters?', 'wc -l, wc -w, wc -m (characters) and wc -c (bytes).'),
    ('Why does wc -l report one line less than I see?', 'The last line has no newline character at the end; wc -l counts newlines.'),
]

PRACTICE_INTRO = 'Reading tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='First three lines', stmt='Print the first 3 lines of a 10-line file.', inp='seq 1 10',
         code='seq 1 10 > n.txt\nhead -n 3 n.txt\n', explain='head -n 3.'),
    dict(level='easy', title='Last line', stmt='Print only the last line.', inp='seq 1 10',
         code='seq 1 10 > n.txt\ntail -n 1 n.txt\n', explain='tail -n 1.'),
    dict(level='easy', title='Count lines', stmt='Print only the number of lines, without the file name.', inp='seq 1 25',
         code='seq 1 25 > n.txt\nwc -l < n.txt\n', explain='&lt; hides the name.'),
    dict(level='medium', title='Skip the header', stmt='Print a CSV without its header.', inp='id,city / 1,Pune / 2,Goa',
         code="printf 'id,city\\n1,Pune\\n2,Goa\\n' > c.csv\ntail -n +2 c.csv\n", explain='+2 starts at line 2.'),
    dict(level='medium', title='Lines 4 to 6', stmt='Print lines 4, 5 and 6 of a 10-line file.', inp='seq 1 10',
         code='seq 1 10 > n.txt\nhead -n 6 n.txt | tail -n 3\n', explain='First 6, then the last 3 of those.'),
    dict(level='medium', title='Join two files', stmt='Combine a.txt and b.txt into all.txt and show it.', inp='a: x / b: y',
         code='echo x > a.txt; echo y > b.txt\ncat a.txt b.txt > all.txt\ncat all.txt\n', explain='cat joins in order.'),
    dict(level='business', title='Newest errors first', stmt='From a log, print the ERROR lines newest first.', inp='ERROR a, INFO, ERROR b',
         code="printf 'ERROR a\\nINFO x\\nERROR b\\n' > l.log\ntac l.log | grep ERROR\n", explain='tac then grep.'),
    dict(level='business', title='Find Windows line endings', stmt='Show whether <code>data.csv</code> has Windows line endings.', inp='a CRLF file',
         code="printf 'id,v\\r\\n1,2\\r\\n' > data.csv\ncat -A data.csv\n", explain='^M$ = CRLF.'),
]

SCN_INTRO = 'Interview questions about reading files, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you see the last 100 lines of a log and keep watching it?”',
        'A support engineer must check a live application log.',
        'do you know tail and its options?',
        '''<ul>
          <li><code>tail -n 100 app.log</code>, then <code>tail -n 100 -f app.log</code> to keep following.</li>
          <li>Rotated logs: <code>-F</code>. Only errors: <code>| grep --line-buffered ERROR</code>.</li>
          <li>Ctrl+C to stop.</li>
        </ul>''', 'opening the file in vi on production.') +
    scn('Data team · validation', 'Junior', 'The row counts do not match',
        'The source says 10,000 rows; <code>wc -l</code> on the exported CSV says 10,000 too, but the database has 9,999.',
        'do you understand headers and newlines?',
        '''<ol>
          <li>wc -l counts the header too: 9,999 data rows + 1 header = 10,000 lines. The load is correct.</li>
          <li>Count data rows with <code>tail -n +2 file | wc -l</code>.</li>
          <li>Also check the last line ends with a newline (<code>tail -c 1 file | od -c</code>), and quoted fields with embedded newlines.</li>
        </ol>''', 'reloading the data without understanding the difference.') +
    scn('Operations · on call', 'Mid-level', '“tail -f shows nothing since midnight.”',
        'An engineer says the application stopped logging at 00:00, but users are active.',
        'do you know log rotation?',
        '''<ul>
          <li>logrotate renamed the file at midnight; tail -f still watches the old inode.</li>
          <li>Use <code>tail -F</code>, or check with <code>ls -li app.log*</code> and <code>lsof</code> which file the app writes.</li>
          <li>If the app itself still writes to the old file, logrotate needs copytruncate or a reload (Lesson 18.1).</li>
        </ul>''', 'restarting the application first.') +
    scn('Platform · performance', 'Senior', 'Reading a 50 GB file efficiently',
        'A script runs <code>cat huge.log | tail -n 100</code> every minute and loads the disk.',
        'do you know which tools seek and which stream?',
        '''<ul>
          <li>tail with a file name seeks to the end: <code>tail -n 100 huge.log</code> reads a few KB, not 50 GB.</li>
          <li>Pipes remove that ability; avoid useless cat. head also stops early.</li>
          <li>For repeated checks, follow with <code>tail -F</code> or use the journal / a log shipper instead of re-reading.</li>
        </ul>''', 'buying faster disks.')
) + interview([
    ('Difference between cat, less, head and tail?', 'cat prints the whole file; less pages through it; head prints the start; tail the end (and can follow with -f).'),
    ('How do you skip a CSV header?', 'tail -n +2 file.csv.'),
    ('tail -f vs tail -F?', '-f follows the opened file descriptor; -F follows the name and reopens after rotation.'),
    ('How do you print lines 50–60?', 'head -n 60 f | tail -n 11, or sed -n 50,60p f.'),
    ('How do you find Windows line endings?', 'cat -A shows ^M$ at line ends (or file says “with CRLF line terminators”).'),
    ('Why is tail fast on huge files?', 'It seeks to the end and reads backwards only as much as needed; it cannot do that through a pipe.'),
    ('What does wc -l count exactly?', 'Newline characters, so a final line without \\n is not counted.'),
], [
    ('RHCSA (EX200)', '“Locate and interpret system log files and journals”; tail, less and wc are the everyday tools for it.'),
    ('LFCS', 'Essential Commands and Operations: read and monitor log files from the command line.'),
    ('CompTIA Linux+', 'Text viewing utilities (cat, head, tail, less, more, wc, nl) in file management objectives.'),
]) + distro('These tools exist everywhere; the extras differ.', [
    ('tac', 'yes (GNU)', 'yes', 'no: use tail -r', 'yes'),
    ('tail -F, --pid', 'yes', 'yes', '-F yes, --pid no', 'yes'),
    ('cat -A', 'yes', 'yes', 'no: use cat -vet', 'yes'),
    ('head -n -N', 'yes (GNU)', 'yes', 'no', 'yes'),
    ('System log', '/var/log/syslog + journalctl', '/var/log/messages + journalctl', 'log show / Console app', 'WSL: often no syslog; journalctl if systemd'),
    ('Pager', 'less', 'less', 'less', 'less (Git Bash: less too)'),
]) + teaser('3.6', 'Riya needs the date 45 days from today, a quick sum like 1250×18%, the numbers 1 to 100 for test data, and to re-run a command every 2 seconds until a file appears. Which four small tools?')

CHEATSHEET = cheatsheet('viewing files', [
    ('cat · tac', [('cat f', 'whole file'), ('cat a b > all', 'join files'), ('cat -n / -b', 'number all / non-empty'), ('cat -s', 'squeeze blank lines'), ('cat -A', 'show ^I ^M $'), ('tac f', 'reverse lines')]),
    ('head · tail', [('head -n 20 f', 'first 20'), ('head -n -1 f', 'all but last'), ('tail -n 50 f', 'last 50'), ('tail -n +2 f', 'skip header'), ('head -n 210 f | tail -n 11', 'lines 200–210')]),
    ('Live logs', [('tail -f f', 'follow'), ('tail -F f', 'follow + rotation'), ('tail -n 0 -f f', 'only new lines'), ('tail -f --pid=P f', 'stop with process'), ('… | grep --line-buffered X', 'filter live')]),
    ('less', [('Space / b', 'page down / up'), ('/word ?word', 'search'), ('n / N', 'next / previous'), ('g / G', 'top / bottom'), ('F', 'follow'), ('-S -N', 'chop / numbers')]),
    ('nl · wc', [('nl -ba f', 'number all lines'), ("nl -bp'ERR' f", 'number matches'), ('nl -nrz -w3', '001 format'), ('wc -l < f', 'line count only'), ('wc -w / -c / -m', 'words / bytes / chars')]),
])

MINDMAP = mindmap('Viewing files', [
    ('cat / tac', 'blue', ['short files, join', '-n -b -s -A', 'tac: newest first']),
    ('head / tail', 'green', ['start / end', '-n +2 skip header', 'instant on big files']),
    ('Live', 'red', ['tail -f', '-F after rotation', '--pid, | grep']),
    ('less', 'violet', ['scroll both ways', '/search n G', 'F follow, -S -N']),
    ('Count', 'amber', ['wc -l lines', '-w -c -m', 'last newline!']),
    ('nl', 'acc', ['non-empty by default', '-ba all, -bp pattern', '-nrz -w -s']),
])

LAB = lab('investigate the shop log', 'Build the lab, answer each task by writing the result into a file, then run the checker.',
    setup='''mkdir -p ~/lab35 && cd ~/lab35 && rm -f *.txt *.log *.csv
for i in $(seq 1 200); do
  if [ $((i % 40)) -eq 0 ]; then echo "2026-11-06 line $i ERROR payment failed"; else echo "2026-11-06 line $i INFO ok"; fi
done > shop.log
printf 'id,item,qty\\n1,pen,3\\n2,book,1\\n3,bag,2\\n' > orders.csv''',
    tasks=['Save the last 5 lines of <code>shop.log</code> into <code>last5.txt</code>.',
           'Save lines 100 to 105 of shop.log into <code>range.txt</code>.',
           'Save the number of ERROR lines (just the number) into <code>errors.txt</code>.',
           'Save <code>orders.csv</code> without its header into <code>orders_data.csv</code>.'],
    solution='''tail -n 5 shop.log > last5.txt
head -n 105 shop.log | tail -n 6 > range.txt
grep -c ERROR shop.log > errors.txt
tail -n +2 orders.csv > orders_data.csv''',
    check='''cd ~/lab35
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 last 5 lines"    '[ "$(wc -l < last5.txt 2>/dev/null)" = 5 ] && grep -q "line 200 " last5.txt'
ok "2 lines 100-105"   '[ "$(head -n 1 range.txt 2>/dev/null | cut -d" " -f3)" = 100 ] && [ "$(wc -l < range.txt)" = 6 ]'
ok "3 error count"     '[ "$(cat errors.txt 2>/dev/null)" = 5 ]'
ok "4 no header"       '[ "$(head -n 1 orders_data.csv 2>/dev/null)" = "1,pen,3" ]' ''')
