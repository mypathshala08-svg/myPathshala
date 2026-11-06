import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='05-redirection-and-pipes', lesson='03-pipes-and-tee-building-command-pipelines', n='5.3',
    module_label='Module 5 · Redirection, pipes and chaining',
    title='Pipes and tee: building command pipelines',
    desc='The pipe | and how to build pipelines from small filters (head, tail, wc, grep, sort, uniq, cut, tr, awk) step by step; tee, tee -a and sudo tee; PIPESTATUS, set -o pipefail and SIGPIPE (141); |& and 2>&1 |; the subshell trap; named pipes with mkfifo. Explained, then used by admins, web, security, data, developers, DBAs, DevOps and QA, with real outputs and corrected classroom examples.',
    og_desc='Build Linux pipelines step by step: top IPs from an access log, tee, pipefail and PIPESTATUS, with real outputs.',
    minutes=40, level='Beginner → Advanced',
    lead='There is no command called “top IPs”, but cut | sort | uniq -c | sort -rn | head answers it in one line. This lesson shows how pipes join small tools, how to build a pipeline one stage at a time, how tee saves a copy, and how to know that every stage really worked.',
    chips=['Pipelines by field', 'Build it step by step', 'pipefail & PIPESTATUS', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A tiny log, then the classic top-N pipeline
printf '%s\\n' 10.0.0.1 10.0.0.2 10.0.0.1 10.0.0.3 10.0.0.1 10.0.0.2 > ips.txt
sort ips.txt | uniq -c | sort -rn | head -n 2
sort ips.txt | uniq | wc -l                     # unique IPs
sort -u ips.txt | tee unique.txt | wc -l        # save a copy too
false | true; echo "stages: ${PIPESTATUS[*]}"
"""

RUN = dict(
    heading='The top-N pipeline in five lines',
    intro='<p>Count IPs, find the unique ones, save a copy with tee and look at the exit status of each stage.</p>',
    code=MAIN,
    anno=[
        ('sort ips.txt | uniq -c | sort -rn | head -n 2', 'Top 2 by count.'),
        ('sort ips.txt | uniq | wc -l                     # unique IPs', '3'),
        ('sort -u ips.txt | tee unique.txt | wc -l        # save a copy too', 'tee in the middle.'),
        ('false | true; echo "stages: ${PIPESTATUS[*]}"', '1 0'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which IP is top?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does uniq -c print without sort? Then run.',
             code="printf 'a\\nb\\na\\n' | uniq -c\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should show the 3 largest files, but shows only 2. Fix it.',
             code="for i in 1 2 3 4; do head -c ${i}000 /dev/zero > f$i; done\nls -lS | head -n 3\n"),
        dict(label='4 · Your turn', hint='Print the words of “b c a b” sorted, one per line, without duplicates.',
             code="echo 'b c a b' | tr ' ' '\\n' | sort -u\n"),
        dict(label='5 · Challenge', hint='Make the pipeline below report failure using pipefail.',
             code="set -o pipefail\nfalse | true\necho \"status $?\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: live logs and root files',
    intro='<p>These need a live log, sudo or a real history. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Your most used commands', cmd="history | awk '{print $2}' | sort | uniq -c | sort -rn | head -5", output='    212 ls\n    140 cd\n     88 git\n     51 cat\n     40 sudo', note='Typical. Column 1 of history is a number, so the command is $2.'),
        dict(title='2 · Follow a log and filter it live', cmd='tail -f /var/log/syslog | grep --line-buffered -i error', output='Nov  6 10:31:02 laptop kernel: [ 812.4] usb 1-2: device descriptor read/64, error -71', note='Typical. --line-buffered makes grep pass each line on at once; Ctrl+C stops.'),
        dict(title='3 · Append a host entry as root', cmd='echo "10.0.0.5  db01" | sudo tee -a /etc/hosts > /dev/null; tail -1 /etc/hosts', output='10.0.0.5  db01', note='Typical.'),
        dict(title='4 · Is nginx running?', cmd='pgrep -c nginx; ps aux | grep nginx | wc -l', output='3\n4', note='Typical: the second count includes grep itself.'),
        dict(title='5 · Pipe buffer size on our build machine', cmd='cat /proc/sys/fs/pipe-max-size; getconf PIPE_BUF', output=pc('cat /proc/sys/fs/pipe-max-size; getconf PIPE_BUF'), note='Recorded. Max size a pipe can be grown to; PIPE_BUF = writes up to this size are never interleaved.'),
    ],
)

TRACE = dict(
    heading='A pipeline, stage by stage',
    intro='<p>Step through building the word-frequency pipeline and watch each variable.</p>',
    code='''text="to be or not to be"
n=$(wc -w <<< "$text")
top=$(tr ' ' '\\n' <<< "$text" | sort | uniq -c | sort -rn | head -n 1)
top=$(echo $top)
echo "$n words, top: $top"
''',
    notes={1: 'Input :: Six words.', 2: 'wc -w :: 6 words.', 3: 'Pipeline :: One word per line, counted, ranked.', 4: 'Tidy :: Remove the padding spaces.', 5: 'Report :: Count and the top word.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a web admin’s error report, a data engineer’s CSV profile, and a DBA’s safe compressed backup.'
EXAMPLES = [
    dict(level='b', tag='Web admin', title='Which pages return 404?',
         problem='<p>From an access log, list the pages that returned 404, with how often.</p>',
         inp='four log lines',
         approach=['grep the status.', 'cut the page, count it.'],
         code='''printf '%s\\n' '1.1.1.1 "GET /a" 404' '1.1.1.2 "GET /b" 200' '1.1.1.3 "GET /a" 404' '1.1.1.1 "GET /c" 404' > web.log
grep ' 404$' web.log | cut -d'"' -f2 | sort | uniq -c | sort -rn
''',
         notes={2: 'Filter, cut, count :: /a twice, /c once.'},
         tryit='Show 200s instead.'),
    dict(level='i', tag='Data engineer', title='Profile a CSV column',
         problem='<p>How many rows, how many distinct cities, and the most common city?</p>',
         inp='a small CSV with a header',
         approach=['tail -n +2 drops the header.', 'One pipeline per question.'],
         code='''printf 'id,city\\n1,Pune\\n2,Agra\\n3,Pune\\n4,Goa\\n5,Pune\\n' > c.csv
echo "rows: $(tail -n +2 c.csv | wc -l)"
echo "distinct: $(tail -n +2 c.csv | cut -d, -f2 | sort -u | wc -l)"
echo "top: $(tail -n +2 c.csv | cut -d, -f2 | sort | uniq -c | sort -rn | head -n 1)"
''',
         notes={2: 'Rows :: 5.', 3: 'Distinct :: 3.', 4: 'Top :: Pune.'},
         tryit='Add the least common city (sort -n | head -1).'),
    dict(level='a', tag='DBA / DevOps', title='A backup that cannot fail silently',
         problem='<p>Compress a dump through a pipe and stop if the dump stage fails.</p>',
         inp='a dump command that fails half-way (simulated)',
         approach=['set -o pipefail.', 'Check the status and remove the broken file.'],
         code='''set -o pipefail
dump() { echo 'INSERT ...'; echo 'mysqldump: Got error 2013' >&2; return 2; }
if dump | gzip > shop.sql.gz; then
  echo 'backup ok'
else
  echo "backup FAILED (stages: ${PIPESTATUS[*]})"; rm -f shop.sql.gz
fi
''', expect='any',
         notes={1: 'Strict :: Any stage failing fails the pipeline.', 6: 'Failure :: Report the stages and remove the broken file.'},
         tryit='Remove set -o pipefail and run again.'),
]

QUIZ = mix([
    dict(q='What does | connect?', options=['stdout of one command to a file', 'stdout of one command to stdin of the next', 'stderr to stdout', 'two files'], answer=1,
         why='A file would be >.'),
    dict(q='Why sort before uniq -c?', options=['uniq is slow', 'uniq merges only adjacent equal lines', 'sort adds counts', 'It is optional'], answer=1,
         why='Equal lines must be next to each other.'),
    dict(q='ls -lS | head -n 3 shows how many files?', options=['3', '2 (the first line is “total”)', '1', 'all'], answer=1,
         why='Use head -n 4 or tail -n +2 | head -n 3.'),
    dict(q='What does tee do?', options=['Splits a file in two', 'Copies its input to stdout and to files', 'Counts lines', 'Joins files'], answer=1,
         why='T-junction.'),
    dict(q='After false | true, $? is…', options=['1', '0', '141', 'empty'], answer=1,
         why='$? is the last stage; use pipefail or PIPESTATUS.'),
    dict(q='ps aux | grep java | wc -l with one java process prints…', options=['1', '2 (grep matches itself)', '0', 'an error'], answer=1,
         why='Use pgrep -c java.'),
    dict(q='How do you write to /etc/hosts from a pipe as a normal user with sudo?', options=['| sudo > /etc/hosts', '| sudo tee -a /etc/hosts', 'sudo | tee', '| tee sudo'], answer=1,
         why='tee runs as root.'),
    dict(q='Status 141 for a stage means…', options=['file not found', 'it got SIGPIPE: the reader closed early', 'out of memory', 'syntax error'], answer=1,
         why='128 + 13. Normal with head.'),
])

REVISION = [
    '<code>cmd1 | cmd2</code>: stdout → stdin; stages run at the same time; only stdout passes (<code>2&gt;&amp;1 |</code> or <code>|&amp;</code> for errors).',
    'Filters: head, tail, wc, grep, sort, uniq, cut, tr, awk, sed. Build pipelines one stage at a time.',
    'Top N: <code>sort | uniq -c | sort -rn | head</code>. uniq needs sorted input.',
    '<code>ls -l | head -n 3</code> includes the “total” line; quote grep patterns (<code>\'^\\.\'</code>); <code>pgrep -c</code> not ps|grep|wc.',
    '<code>tee file</code>, <code>tee -a</code>, several files, mid-pipeline copy; <code>| sudo tee [-a] f &gt; /dev/null</code>.',
    '<code>$?</code> = last stage; <code>${PIPESTATUS[@]}</code>; <code>set -o pipefail</code> for scripts and backups.',
    '141 = SIGPIPE (reader closed early), normal with head.',
    'Subshell trap: <code>cmd | read v</code> loses v; use <code>&lt;&lt;&lt;</code> or <code>done &lt; &lt;(cmd)</code>. Named pipes: <code>mkfifo</code>.',
]

FAQ = [
    ('What is a pipe in Linux?', 'The | operator: it sends the standard output of one command into the standard input of the next, so small commands can be combined.'),
    ('What is the difference between a pipe and redirection?', 'A pipe connects a command to another command (ls | wc -l); redirection connects a command to a file (ls > list.txt).'),
    ('What does tee do?', 'It copies its input to standard output and to one or more files, so you can see and save output at the same time. -a appends.'),
    ('How do I find the most frequent lines?', 'sort file | uniq -c | sort -rn | head.'),
    ('Why is $? 0 even though the first command in my pipeline failed?', '$? holds the status of the last command. Use set -o pipefail or ${PIPESTATUS[@]}.'),
    ('How do I pipe stderr as well?', 'cmd 2>&1 | next, or cmd |& next in bash.'),
    ('Why is the variable empty after cmd | while read …?', 'Each pipeline stage runs in a subshell. Use while … done < <(cmd), a here-string, or shopt -s lastpipe.'),
]

PRACTICE_INTRO = 'Small pipeline tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='First 3 lines', stmt='Print the first 3 lines of /etc/passwd through a pipe.', inp='/etc/passwd',
         code='cat /etc/passwd | head -n 3 | cut -d: -f1\n', explain='head keeps 3; cut shows just the names.'),
    dict(level='easy', title='How many shells', stmt='Count the lines in /etc/shells that start with /.', inp='/etc/shells',
         code="grep '^/' /etc/shells | wc -l\n", explain='Filter, then count.'),
    dict(level='easy', title='Upper case', stmt='Print “linux pipes” in capital letters.', inp='—',
         code="echo 'linux pipes' | tr a-z A-Z\n", explain='tr changes characters.'),
    dict(level='medium', title='Unique sorted', stmt='From “pune agra pune goa agra”, print the unique words sorted.', inp='a string',
         code="echo 'pune agra pune goa agra' | tr ' ' '\\n' | sort -u\n", explain='One per line, then sort -u.'),
    dict(level='medium', title='Top word', stmt='Which word appears most in “a b a c a b”?', inp='a string',
         code="echo 'a b a c a b' | tr ' ' '\\n' | sort | uniq -c | sort -rn | head -n 1\n", explain='The frequency pipeline.'),
    dict(level='medium', title='See and save', stmt='Print 1 to 3 and save them to nums.txt at the same time; then count nums.txt.', inp='—',
         code='seq 1 3 | tee nums.txt\nwc -l < nums.txt\n', explain='tee shows and saves.'),
    dict(level='business', title='Largest 3 files', stmt='Show the names of the 3 largest files (4 files given).', inp='f1..f4',
         code='for i in 1 2 3 4; do head -c ${i}000 /dev/zero > f$i; done\nls -lS f* | tail -n +1 | head -n 3 | awk \'{print $9}\'\n', explain='With a file pattern, ls -l prints no total line; without one, skip it with tail -n +2.'),
    dict(level='business', title='Catch the failing stage', stmt='Run “false | sort | true” and print which stages failed.', inp='—',
         code="false | sort | true\necho \"${PIPESTATUS[*]}\"\n", explain='1 0 0: the first stage failed.'),
]

SCN_INTRO = 'Interview questions about pipes and tee, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Count the number of files in a folder.”',
        'A very common practical question.',
        'can you combine two commands?',
        '''<ul>
          <li><code>ls | wc -l</code> (one name per line in a pipe).</li>
          <li>Hidden files too: <code>ls -A | wc -l</code>; only files: <code>find . -maxdepth 1 -type f | wc -l</code>.</li>
          <li>Explain the pipe: stdout of ls into stdin of wc.</li>
        </ul>''', 'ls -l | wc -l (counts the “total” line too).') +
    scn('Web hosting · operations', 'Junior', 'The site is slow: who is calling it?',
        'You have SSH to the web server and the nginx access log.',
        'can you build a log pipeline quickly?',
        '''<ol>
          <li><code>awk '{print $1}' access.log | sort | uniq -c | sort -rn | head</code>: top IPs.</li>
          <li>Same pattern for $7 (pages) and $9 (status codes).</li>
          <li>Check one suspicious IP with grep; block it if abusive.</li>
        </ol>''', 'opening a 2 GB log in vim.') +
    scn('Data platform · DBA', 'Mid-level', 'The backup was empty for a week',
        'Nightly <code>mysqldump shop | gzip &gt; /backup/shop.sql.gz</code> always “succeeded”, but the files are tiny.',
        'do you know how a pipeline’s exit status works?',
        '''<ul>
          <li>$? is gzip’s status; mysqldump failed (password expired), unnoticed.</li>
          <li>Fix: <code>set -o pipefail</code>, check <code>${PIPESTATUS[0]}</code>, alert on failure and on unexpected size.</li>
          <li>Test restores regularly: a backup is only proven by a restore.</li>
        </ul>''', '“the job said 0, so it worked”.') +
    scn('Platform · scripting', 'Senior', 'The counter that is always zero',
        'A script runs <code>count=0; grep ERROR app.log | while read -r l; do count=$((count+1)); done; echo $count</code> and prints 0.',
        'do you understand subshells in pipelines?',
        '''<ul>
          <li>The while loop runs in a subshell; its count vanishes when the pipeline ends.</li>
          <li>Fix: <code>while …; done &lt; &lt;(grep ERROR app.log)</code>, or <code>shopt -s lastpipe</code>, or simply <code>grep -c ERROR app.log</code>.</li>
          <li>Prefer the simplest tool; loop in bash only when you must.</li>
        </ul>''', 'adding export to count.')
) + interview([
    ('What is a pipe?', 'It sends stdout of one command into stdin of the next: cmd1 | cmd2.'),
    ('Difference between | and >?', '| feeds a command; > writes a file.'),
    ('What does tee do?', 'Writes its input to stdout and to files; -a appends.'),
    ('How do you get the top 10 most frequent lines?', 'sort | uniq -c | sort -rn | head.'),
    ('How do you make a pipeline fail if any command fails?', 'set -o pipefail; inspect ${PIPESTATUS[@]}.'),
    ('How do you pipe both stdout and stderr?', '2>&1 | or |& in bash.'),
    ('Why does ps aux | grep x show the grep line?', 'grep’s own command line contains x. Use pgrep or grep [x].'),
], [
    ('RHCSA (EX200)', '“Use input-output redirection (&gt;, &gt;&gt;, |, 2&gt;, etc.)” and “use grep and regular expressions to analyse text”.'),
    ('LFCS', 'Essential commands: use pipes and filters to process text streams.'),
    ('CompTIA Linux+', 'Pipes, tee and text filters (sort, uniq, cut, wc, head, tail).'),
]) + distro('Pipes work the same everywhere; some helpers differ.', [
    ('| tee', 'yes', 'yes', 'yes', 'yes'),
    ('|& and PIPESTATUS', 'bash', 'bash', 'bash (zsh: pipestatus)', 'WSL / Git Bash bash'),
    ('set -o pipefail', 'bash; dash (sh) since 0.5.11+', 'bash', 'bash/zsh', 'yes'),
    ('pgrep', 'procps', 'procps-ng', 'yes', 'WSL yes; Git Bash no'),
    ('sort, uniq, cut', 'GNU', 'GNU', 'BSD (few option differences)', 'GNU'),
    ('mkfifo', 'yes', 'yes', 'yes', 'WSL yes; Git Bash: limited'),
]) + teaser('5.4', 'Riya wants: create the folder, and only if that worked copy the files, and if the copy fails print an alert. And she has 300 file names coming out of find that must be passed to rm as arguments, not as stdin. Which operators and which command do that?')

CHEATSHEET = cheatsheet('pipes and tee', [
    ('Pipe basics', [('a | b', 'stdout of a → stdin of b'), ('a 2>&1 | b', 'errors too'), ('a |& b', 'same (bash)'), ('a | less', 'scroll'), ('a | head -n 5', 'first lines')]),
    ('Counting', [('a | wc -l', 'lines'), ('grep -c x f', 'matches'), ('ls | wc -l', 'files'), ('pgrep -c name', 'processes'), ('sort -u | wc -l', 'distinct')]),
    ('Top N', [('sort | uniq -c', 'count'), ('| sort -rn', 'biggest first'), ('| head -n 5', 'top 5'), ("cut -d' ' -f1", 'a column'), ("tr ' ' '\\n'", 'words to lines')]),
    ('tee', [('a | tee f', 'see + save'), ('a | tee -a f', 'append'), ('a | tee f1 f2', 'two files'), ('a | tee f | b', 'mid-pipeline copy'), ('| sudo tee f >/dev/null', 'root file')]),
    ('Status', [('$?', 'last stage'), ('${PIPESTATUS[*]}', 'every stage'), ('set -o pipefail', 'fail on any'), ('141', 'SIGPIPE: normal'), ('done < <(cmd)', 'avoid subshell')]),
])

MINDMAP = mindmap('Pipes and tee', [
    ('|', 'blue', ['stdout → stdin', 'stages run together', 'only stdout passes']),
    ('Filters', 'green', ['head tail wc', 'grep sort uniq', 'cut tr awk sed']),
    ('Top N', 'amber', ['sort | uniq -c', '| sort -rn | head', 'build stage by stage']),
    ('tee', 'red', ['see + save', '-a append', 'sudo tee']),
    ('Status', 'violet', ['$? = last', 'PIPESTATUS', 'pipefail, 141']),
    ('Traps', 'acc', ['ls -l total line', 'grep counts itself', 'subshell variables']),
])

LAB = lab('analyse a web log with pipelines', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab53 && cd ~/lab53 && rm -f *.txt
printf '%s\\n' '1.1.1.1 GET / 200' '2.2.2.2 GET /login 401' '1.1.1.1 GET /cart 200' '3.3.3.3 GET /admin 401' '2.2.2.2 GET /login 401' '1.1.1.1 GET / 500' > web.log''',
    tasks=['Write the number of lines of web.log that contain <code>401</code> into <code>count401.txt</code>.',
           'Write the IP that appears most often (just the IP) into <code>top.txt</code>.',
           'Write the sorted list of unique IPs into <code>ips.txt</code> <b>and</b> show it on screen, in one pipeline.',
           'Write the number of unique status codes into <code>codes.txt</code>.'],
    solution='''grep -c 401 web.log > count401.txt
cut -d' ' -f1 web.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}' > top.txt
cut -d' ' -f1 web.log | sort -u | tee ips.txt
cut -d' ' -f4 web.log | sort -u | wc -l > codes.txt''',
    check='''cd ~/lab53
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 count of 401"   '[ "$(cat count401.txt 2>/dev/null)" = 3 ]'
ok "2 top IP"         '[ "$(cat top.txt 2>/dev/null)" = 1.1.1.1 ]'
ok "3 unique IPs"     '[ "$(cat ips.txt 2>/dev/null)" = "$(printf "1.1.1.1\\n2.2.2.2\\n3.3.3.3")" ]'
ok "4 status codes"   '[ "$(tr -d " " < codes.txt 2>/dev/null)" = 3 ]' ''')
