import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# A small, realistic web access log (generated, fixed, so every output is stable).
LOG = r"""python3 - << 'PY'
import random
random.seed(7)
ips = ['49.36.12.8']*9 + ['103.21.44.7']*6 + ['157.48.1.20']*4 + ['10.0.0.5']*3 + ['185.220.101.4']*7 + ['117.99.3.3']*2
pages = ['/', '/login', '/cart', '/api/orders', '/admin', '/products?id=7']
codes = [200]*7 + [404, 500, 302]
random.shuffle(ips)
with open('access.log', 'w') as f:
    for k, ip in enumerate(ips):
        p = '/admin' if ip == '185.220.101.4' else random.choice(pages)
        c = 401 if p == '/admin' else random.choice(codes)
        f.write(f'{ip} - - [06/Nov/2026:10:{k:02d}:00 +0530] "GET {p} HTTP/1.1" {c} {random.randint(200, 9000)}\n')
PY"""

HOOK = hook('The manager wants to know, in five minutes, which IP addresses hit the website most often today. The access log has 50,000 lines. Opening it in an editor is hopeless, and there is no single command called “top IPs”. But there are small commands that each do one thing: cut a column, sort, count duplicates, show the top. The pipe <code>|</code> joins them: <code>cut -d" " -f1 access.log | sort | uniq -c | sort -rn | head -5</code>. That one line is how Linux people solve most data problems.',
    ['connect commands with <code>|</code> so that one command’s output becomes the next one’s input',
     'build a pipeline step by step from your notes’ examples (head, wc, grep, sort, uniq) and fix the common mistakes',
     'save and see output at the same time with <code>tee</code>, append with <code>tee -a</code>, and write root files with <code>sudo tee</code>',
     'check every stage of a pipeline with <code>PIPESTATUS</code> and <code>set -o pipefail</code>, and avoid the subshell trap'])
ROAD = roadmap([
    ('story', 'The story', 3, 'top IPs in one line'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What a pipe is', 5, 'simple meaning + 4 depths'),
    ('commands', 'Pipes and tee, by field', 16, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'data flowing through 5 stages'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Use one command’s output as the next one’s input', 'cmd1 | cmd2', 'no temp file'),
    ('Only the first lines of long output', 'cmd | head -n 5', 'or | less to scroll'),
    ('Count results', 'cmd | wc -l', 'grep -c for matches in a file'),
    ('Top N by frequency', 'sort | uniq -c | sort -rn | head', 'the classic pipeline'),
    ('See the output AND save it', 'cmd | tee out.txt', 'tee -a appends'),
    ('Write a root-owned file from a pipe', 'cmd | sudo tee /etc/file > /dev/null', 'sudo cmd > file fails'),
    ('Errors into the pipe too', 'cmd 2>&1 | grep …', 'bash: cmd |& grep …'),
    ('Did every stage succeed?', 'set -o pipefail  /  ${PIPESTATUS[@]}', '$? is only the last stage'),
    ('Is a process running? (count)', 'pgrep -c name', 'ps aux | grep name counts grep too'),
])

cmap = concept_map(
    [('5.1', 'Standard streams', 'a pipe connects stdout to stdin'), ('5.2', 'Redirection', '> and < to files; | to commands'), ('3.5', 'Viewing files', 'head, tail, less, wc')],
    ['the pipe |: stdout of one command into stdin of the next', 'pipelines from small tools: head, tail, wc, grep, sort, uniq, cut', 'tee, tee -a, sudo tee, several files', 'exit status of pipelines: PIPESTATUS, pipefail, SIGPIPE', 'subshells, |&, named pipes (mkfifo)'],
    [('5.4', 'Chaining and xargs', 'pipe into arguments with xargs'), ('6.2', 'sort, uniq, wc, cut', 'the filters in depth'), ('13.3', 'Log analysis', 'pipelines on real logs'), ('11.2', 'Processes', 'ps, pgrep, top')],
    'The pipe is the reason Linux has small tools instead of big ones: you build the tool you need, every time, in one line.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ cut -d" " -f1 access.log | sort |', '  uniq -c | sort -rn | head -3', ('      9 49.36.12.8', 'acc'), ('      7 185.220.101.4', 'acc'), ('      6 103.21.44.7', 'acc'), '$ grep 185.220 access.log | head -1', ('… "GET /admin HTTP/1.1" 401', 'err')], title='riya@web01: ~', size=7.2, step=15)
      + t(352, 36, 'Five small tools, one answer:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• cut: take column 1 (the IP)', '• sort: group equal IPs', '• uniq -c: count each group', '• sort -rn: biggest first', '• head: keep the top'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Five minutes to find the top visitors</h2>
  <div class="story">
''' + puzzle('Riya’s notes say: “Sort files by size and show the largest 3: <code>ls -lhS | head -n 3</code>”. She runs it in a folder with 4 files. How many file names does she see, and why?') + '''
    <p class="narration">The website is slow. The manager asks Riya which IP addresses are hitting it most. The log is far too long to read.</p>
''' + scene('A terminal: cut, sort, uniq -c, sort -rn and head joined by pipes print the top three IPs; one IP keeps requesting /admin and getting 401.', sc,
            'Each <tspan font-weight="700" class="s-acc">|</tspan> hands the output of one tool to the next.') + '''
A> No single command answers that, but five small ones do, joined with the pipe <code>|</code>. Each one’s output flows straight into the next one’s input.
R> And no temporary files in between?
K> None. The data streams through memory, so it works on a 50 MB log as easily as on 30 lines. And look: one IP is hammering /admin and getting 401. That is a security question now.
A> Today: the pipe, how to build a pipeline one stage at a time, <code>tee</code> to see and save at once, and how to know whether every stage really worked.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A factory assembly line: raw material passes through four stations, cutting, sorting, counting and packing, connected by conveyor belts; a T-junction (tee) sends a copy to a storage box.">'
       + ''.join(label_box(14 + k * 128, 40, 104, 60, [a, b], tone, 8.8) for k, (a, b, tone) in enumerate([('raw log', 'cat / input', 'card'), ('cut', 'one column', 'blue'), ('sort', 'group', 'green'), ('uniq -c', 'count', 'amber'), ('head', 'top 5', 'violet')]))
       + ''.join(arrow(120 + k * 128, 70, 140 + k * 128, 70) for k in range(4))
       + label_box(400, 124, 120, 40, ['tee', 'copy to a file'], 'red', 8.6) + arrow(450, 102, 450, 122)
       + t(320, 186, 'An assembly line: each station does one job and passes the work on.', 9.6, 'ink2')
       + t(320, 204, 'The belts between stations are the pipes |.', 9.6, 'acc', bold=True)
       + '<text x="632" y="206" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Pipes at four depths', [
    ('v', 'No jargon: an assembly line', '      <p>Think of a factory assembly line.</p>' + pic + '''
      <ul>
        <li>Each station does one small job: cut, sort, count, pack.</li>
        <li>A conveyor belt carries the work from one station to the next: that belt is the <b>pipe</b> <code>|</code>.</li>
        <li>Stations work at the same time: the cutter is already cutting the next piece while the sorter sorts.</li>
        <li><code>tee</code> is a T-junction in the belt that sends a copy into a storage box (a file) while the line keeps moving.</li>
      </ul>'''),
    ('b', 'The pipes you will type every day', '''      <ul>
        <li><code>ls -l | head -n 5</code>: only the first lines of a long listing.</li>
        <li><code>ls | wc -l</code>: how many files; <code>who | wc -l</code>: how many users logged in.</li>
        <li><code>cat data.txt | grep failed | sort | uniq</code>: filter, sort, remove duplicates.</li>
        <li><code>ps aux | less</code>: scroll through long output (q quits).</li>
        <li><code>command | tee out.txt</code>: see the output and save it.</li>
      </ul>'''),
    ('i', 'Stages, filters and exit status', '''      <ul>
        <li>A command that reads stdin and writes stdout is a <b>filter</b>: grep, sort, uniq, cut, tr, head, tail, wc, sed, awk. Filters are the stations of a pipeline.</li>
        <li>A pipe carries <b>only stdout</b>. Errors still reach the screen; use <code>2&gt;&amp;1 |</code> (or <code>|&amp;</code>) to send them too.</li>
        <li><code>$?</code> after a pipeline is the status of the <b>last</b> command. <code>${PIPESTATUS[@]}</code> has all of them; <code>set -o pipefail</code> makes the pipeline fail if any stage fails.</li>
        <li><code>uniq</code> only merges <b>adjacent</b> equal lines, so always <code>sort</code> first.</li>
        <li>Prefer the command’s own file argument over <code>cat file |</code>: <code>grep x file</code>, <code>wc -l &lt; file</code>. Both work; the second saves a process.</li>
      </ul>'''),
    ('a', 'Behind the screen: pipe(), buffers, SIGPIPE and subshells', '''      <ul>
        <li>The shell calls <code>pipe()</code>, which returns two descriptors (a read end and a write end), forks one process per stage, and connects stage 1’s fd 1 and stage 2’s fd 0 to the pipe with <code>dup2()</code>. All stages run <b>at the same time</b>.</li>
        <li>The kernel pipe buffer holds 64 KB by default on Linux: a fast writer waits when it is full, a reader waits when it is empty. That is how a pipeline handles any amount of data with little memory.</li>
        <li>When a reader exits early (<code>head</code>), the writer gets <b>SIGPIPE</b> and stops: <code>seq 1 100000000 | head -2</code> finishes instantly. Its status is 141 (128 + 13).</li>
        <li>Each stage runs in a <b>subshell</b>: <code>echo x | read v</code> sets v in a child that disappears. Use a here-string, process substitution or <code>shopt -s lastpipe</code>.</li>
        <li><b>Named pipes</b> (<code>mkfifo</code>) are pipes with a name in the file system, so unrelated processes can connect.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Pipes, pipelines and tee</h2>
''' + def_block(
    'A <b>pipe</b> (<code>|</code>) connects the standard output of one command to the standard input of the next. A <b>pipeline</b> is a sequence of commands joined by pipes; all of them run at the same time and data flows through them as a stream. <code>tee</code> reads standard input and writes it both to standard output and to one or more files.',
    'Output of one command = input of the next. tee = a T-junction that also saves a copy.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Pipe', f'The <code>|</code> connection between two commands. {gl("pipe", "Glossary →")}'),
    ('Pipeline', 'Several commands joined by pipes.'),
    ('Filter', 'A command that reads stdin, transforms it and writes stdout.'),
    ('tee', f'Copies its input to the screen and to files. {gl("tee", "Glossary →")}'),
    ('PIPESTATUS', 'A bash array with the exit status of every stage.'),
    ('pipefail', 'Option: the pipeline fails if any stage fails.'),
    ('SIGPIPE', f'The signal a writer gets when the reader has gone. {gl("signal", "Glossary →")}'),
    ('Subshell', f'A child copy of the shell; each pipeline stage runs in one. {gl("subshell", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('| (pipe)', 'a water pipe', 'Doug McIlroy proposed “coupling programs like garden hoses” in 1964; Ken Thompson added pipes to Unix in 1973.'),
    ('tee', 'a T-shaped pipe fitting', 'One way in, two ways out.'),
    ('uniq', 'unique', 'Merges repeated adjacent lines.'),
    ('wc', 'word count', 'Also lines (-l) and bytes (-c).'),
    ('head / tail', 'the start / the end', 'Of the stream.'),
    ('less', '“less is more”', 'A better version of the pager more.'),
    ('pgrep', 'process grep', 'grep for running processes, without matching itself.'),
    ('FIFO', 'first in, first out', 'Another name for a (named) pipe.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Join two commands', '<code>cmd1 | cmd2</code>'),
    ('Top 5 by count', '<code>sort | uniq -c | sort -rn | head -5</code>'),
    ('See and save', '<code>cmd | tee file</code> (<code>-a</code> append)'),
    ('Errors too', '<code>cmd 2&gt;&amp;1 | …</code>  ·  <code>cmd |&amp; …</code>'),
    ('All statuses', '<code>echo ${PIPESTATUS[@]}</code>'),
    ('Fail on any stage', '<code>set -o pipefail</code>'),
]) + '\n' + lv + didyou('The pipe was the idea of Doug McIlroy, head of the Bell Labs department where Unix was born. He pushed for it for years; when Ken Thompson finally added it in one night in 1973, the team rewrote many programs overnight to read stdin and write stdout. The “do one thing well” Unix philosophy comes directly from that night.') + '''
EXAM> “What is a pipe and how is it different from redirection?” → | connects one command’s stdout to another command’s stdin; &gt; connects stdout to a file. Example: ls | wc -l vs ls &gt; list.txt. Mention that only stdout passes (2&gt;&amp;1 for errors) and that $? is the last stage (PIPESTATUS / pipefail).
''' + qc('What is the difference between <code>ls &gt; wc</code> and <code>ls | wc</code>?', '<code>ls &gt; wc</code> creates a <b>file</b> named wc containing the listing. <code>ls | wc</code> runs the <b>command</b> wc on the listing and prints the count.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The filters that make pipelines</h2>
  <p>Any command that reads stdin and writes stdout can be a stage. These are the ones you will chain most (each has its own lesson in Module 6).</p>
''' + table(['Filter', 'What it does in a pipe', 'Example'], [
    ['<code>head -n N</code> / <code>tail -n N</code>', 'first / last N lines', '<code>ls -lt | head -n 5</code>'],
    ['<code>wc -l</code>', 'count lines', '<code>ls | wc -l</code>'],
    ['<code>grep PAT</code> / <code>grep -v</code> / <code>-c</code>', 'keep / drop / count matching lines', '<code>ps aux | grep nginx</code>'],
    ['<code>sort</code> / <code>-n</code> / <code>-r</code> / <code>-k</code>', 'sort text, numbers, reverse, by column', '<code>du -s * | sort -rn</code>'],
    ['<code>uniq</code> / <code>-c</code> / <code>-d</code>', 'merge adjacent duplicates / count / only repeated', '<code>sort | uniq -c</code>'],
    ['<code>cut -d, -f2</code>', 'take columns', '<code>cut -d: -f1 /etc/passwd</code>'],
    ['<code>tr a-z A-Z</code>', 'change characters', '<code>echo hi | tr a-z A-Z</code>'],
    ['<code>awk \'{print $1}\'</code>', 'columns and calculations', '<code>ls -l | awk \'{s+=$5} END{print s}\'</code>'],
    ['<code>sed \'s/a/b/\'</code>', 'edit the stream', '<code>cat f | sed \'s/http:/https:/\'</code>'],
    ['<code>tee FILE</code>', 'copy to a file, pass it on', '<code>cmd | tee log | grep ERR</code>'],
    ['<code>less</code>', 'scroll (the end of a pipeline)', '<code>journalctl | less</code>'],
    ['<code>xargs</code>', 'turn lines into arguments (Lesson 5.4)', '<code>find . -name "*.tmp" | xargs rm</code>'],
], minw=620) + mistake('ls -lhS | head -n 3       “shows the largest 3 files”', 'ls -lhS | head -n 4   ·   or   ls -lhS | tail -n +2 | head -n 3   ·   or   ls -S | head -n 3',
                       'The first line of <code>ls -l</code> is <code>total 16K</code>, so head -n 3 shows that line plus only <b>two</b> files (checked with a real run). This is the answer to the puzzle.') + qc('Why must you <code>sort</code> before <code>uniq -c</code>?', 'uniq only merges <b>adjacent</b> equal lines. Without sort, the same IP appearing in different places is counted several times separately.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Pipes and tee explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04. The web examples use a small generated access log (35 lines, fixed so the numbers never change); real logs look exactly the same, only longer.</p>
''' + cmdcard_u(['joining small tools into the exact command you need', 'filtering, counting, sorting and summarising any output', 'processing huge data without temporary files'],
               ['when the next program needs a file name, not stdin (use <code>&lt;(…)</code> or xargs)', 'when you need the variable set inside the pipe afterwards (subshell trap)'])(
    'pipe', '|', 'pipe',
    'Connects the stdout of the command on the left to the stdin of the command on the right. Both run at the same time. Chain as many as you like.',
    'command1 | command2 | command3 …', 'safe',
    [('cmd | head -n 5', 'first lines only', 'long output'),
     ('cmd | wc -l', 'count', 'how many?'),
     ('cmd | grep PAT', 'filter', 'find lines'),
     ('cmd | sort | uniq -c | sort -rn', 'frequency table', 'top N'),
     ('cmd | less', 'scroll', 'read long output'),
     ('cmd 2>&1 | …  ·  cmd |& …', 'include errors', 'search errors'),
     ('cmd | while read -r l; do …; done', 'loop over output lines', 'process each line')],
    dict(cmd="printf 'chai\\ncoffee\\nchai\\nlassi\\nchai\\n' > orders.txt\ncat orders.txt | wc -l\nsort orders.txt | uniq -c | sort -rn", note='The second line is the classic “what is most popular?” pipeline.'),
    [('sys', [
        dict(situation='How many users are logged in, and how many accounts have bash as their shell?', cmd="who | wc -l\ngrep -c '/bin/bash$' /etc/passwd",
             why='who prints one line per session, so wc -l counts them (0 on our build machine, nobody is logged in). grep -c counts matches directly, no pipe needed.'),
        dict(situation='The 3 largest files in /etc (readable ones), biggest first.', cmd="find /etc -maxdepth 1 -type f -readable -printf '%s %f\\n' | sort -rn | head -n 3",
             why='find prints “size name”; sort -rn sorts numerically, biggest first; head keeps 3. No “total” line to worry about.')]),
     ('web', [
        dict(situation='The top 5 IP addresses in an access log.', setup=LOG, cmd="cut -d' ' -f1 access.log | sort | uniq -c | sort -rn | head -n 5",
             why='Column 1 is the IP. sort groups equal IPs, uniq -c counts each group, sort -rn puts the biggest counts first.'),
        dict(situation='How many requests failed with a 5xx server error?', setup=LOG, cmd="awk '{print $9}' access.log | grep -c '^5'",
             why='Field 9 is the status code. Start with the whole pipeline in your head: extract, filter, count.')]),
     ('sec', [
        dict(situation='Who is trying /admin and getting 401 Unauthorized? (brute force)', setup=LOG, cmd="grep '\"GET /admin' access.log | grep ' 401 ' | cut -d' ' -f1 | sort | uniq -c | sort -rn",
             why='Filter twice, then count per IP: one address with many 401s on /admin is worth blocking (Lesson 19.3).')]),
     ('data', [
        dict(situation='Unique cities in a CSV, sorted, without the header.', cmd="printf 'name,city\\nAsha,Pune\\nRavi,Agra\\nMeena,Pune\\nJoy,Goa\\n' > people.csv\ntail -n +2 people.csv | cut -d, -f2 | sort -u",
             why='tail -n +2 skips the header; cut takes column 2; sort -u sorts and removes duplicates in one step.'),
        dict(situation='Word frequency in a text (the classic pipeline).', cmd="echo 'the cat and the dog and the bird' | tr ' ' '\\n' | sort | uniq -c | sort -rn | head -n 3",
             why='tr puts one word per line, then the frequency table. Search engines and NLP courses start with exactly this.')]),
     ('dev', [
        dict(situation='Which Python files have the most lines?', cmd="mkdir -p src; seq 1 40 > src/app.py; seq 1 12 > src/util.py; seq 1 90 > src/models.py\nwc -l src/*.py | sort -rn | head -n 3",
             why='wc -l prints a total line, which sorts to the top; head -n 4 would show the top 3 files after it.'),
        dict(situation='Your most used shell commands (from your notes).', cmd="printf 'ls\\ncd src\\nls -l\\ngit status\\nls\\ngit status\\nls\\n' > hist.txt\nawk '{print $1}' hist.txt | sort | uniq -c | sort -rn | head -n 3",
             why='In your terminal: <code>history | awk \'{print $2}\' | sort | uniq -c | sort -rn | head</code> ($2 because history adds a number in column 1). Here a saved history file is used.')]),
     ('devops', [
        dict(situation='Is a process running? Count it correctly.', cmd="sleep 123 &\nps aux | grep 'sleep 123' | wc -l\npgrep -fc 'sleep 123'\nkill $!",
             why='ps aux | grep counts the grep command itself (2 instead of 1). pgrep never matches itself. See the common mistake below.')]),
    ],
    anat=anatomy([('sort orders.txt', 'cmd', 'stage 1 writes stdout'), ('|', 'opt', 'pipe'), ('uniq -c', 'cmd', 'stage 2 reads stdin'), ('| sort -rn', 'arg', 'stage 3 …')], 'Spaces around | are optional. A line can end with | and continue on the next line.')
) + mistake('ps aux | grep java | wc -l      (counts one too many)', "pgrep -c java   ·   or   ps aux | grep '[j]ava' | wc -l",
            'The grep process itself has “java” in its command line, so it matches too (a real run counted 2 for 1 process). pgrep skips itself; the <code>[j]ava</code> trick works because the pattern text no longer matches itself.') + mistake("ls -a ~ | grep ^\\.         (meant: only hidden files)", "ls -a ~ | grep '^\\.'",
            'Without quotes bash removes the backslash, grep receives <code>^.</code> (“any first character”) and prints <b>every</b> file (verified). Always quote grep patterns.') + cmdcard_u(['seeing output on screen and saving it at the same time', 'saving an intermediate stage of a pipeline for later', 'writing root-owned files from a pipe (<code>sudo tee</code>)'],
               ['when you only need the file (use <code>&gt;</code>)', 'huge binary streams to many files (it works, but doubles the I/O)'])(
    'tee', 'tee', 'T-junction',
    'Reads stdin, writes it to stdout <b>and</b> to every file you name. <code>-a</code> appends instead of overwriting. Because it is a separate program, <code>sudo tee</code> can write where your shell cannot.',
    'command | tee [-a] FILE… [| next]', 'change',
    [('| tee file', 'show and save (overwrite)', 'record a session'),
     ('| tee -a file', 'show and append', 'logs'),
     ('| tee f1 f2', 'several files at once', 'copies'),
     ('| tee file | next', 'save a stage, keep piping', 'debug a pipeline'),
     ('| tee file > /dev/null', 'save only, quietly', 'sudo tee'),
     ('| sudo tee /etc/f', 'write a root file', 'config edits'),
     ('| tee >(cmd) > out', 'feed two commands at once (bash)', 'checksum while copying')],
    dict(cmd="echo 'deploy v2.4 started' | tee deploy.log\necho 'deploy v2.4 done' | tee -a deploy.log\necho '--- deploy.log:'; cat deploy.log", note='Each line appeared on screen <b>and</b> went into the file.'),
    [('devops', [
        dict(situation='Watch a build and keep its full log, errors included.', cmd="bash -c 'echo compiling; echo \"warning: deprecated\" >&2; echo ok' 2>&1 | tee build.log\necho \"--- saved $(wc -l < build.log) lines\"",
             why='2&gt;&amp;1 joins errors to the pipe, tee shows them live and keeps a copy for the CI artifacts.')]),
     ('sys', [
        dict(situation='Add a line to a root-owned file (the real command).', cmd='echo "10.0.0.5  db01" | sudo tee -a /etc/hosts > /dev/null',
             typical='[sudo] password for riya:\n(no output: the line was appended)',
             why='tee runs as root and opens /etc/hosts itself; &gt; /dev/null hides tee’s copy on screen. Never use <code>sudo echo … &gt;&gt; /etc/hosts</code>.'),
        dict(situation='Without sudo rights, tee reports the problem clearly.', cmd="echo test | tee /etc/mp_test.conf; echo \"exit ${PIPESTATUS[1]}\"",
             why='Our recorder user has no sudo, so tee itself cannot open the file. The line still reached stdout.', expect='any')]),
     ('data', [
        dict(situation='Debug a pipeline: save what a middle stage produced.', setup=LOG, cmd="cut -d' ' -f1 access.log | sort | tee sorted_ips.txt | uniq | wc -l\nhead -n 3 sorted_ips.txt",
             why='tee in the middle saves the sorted list while the pipeline continues: 6 unique IPs, and you can inspect the intermediate file.')]),
     ('qa', [
        dict(situation='Run tests, see progress, and count failures from the saved copy.', cmd="printf 'test_login PASS\\ntest_cart FAIL\\ntest_pay PASS\\n' | tee test_run.log | grep -c FAIL",
             why='The screen shows the count; test_run.log keeps every line for the report.')]),
     ('sec', [
        dict(situation='Record a checksum while making a copy (two outputs at once).', cmd="seq 1 1000 > data.txt\ncat data.txt | tee copy.txt | sha256sum | cut -c1-16\nsha256sum copy.txt | cut -c1-16",
             why='The copy and the checksum come from the same stream, so they match. The same pattern verifies downloads and backups.')]),
    ]
) + cmdcard_u(['scripts where a failed stage must not be ignored', 'debugging which stage of a pipeline failed', 'CI and backup pipelines (<code>mysqldump | gzip &gt; file</code>)'],
               ['interactive quick checks (no need)', 'pipelines where an early stage normally “fails” on purpose (grep finding nothing, head closing the pipe)'])(
    'status', 'PIPESTATUS · pipefail', 'exit status of a pipeline',
    'After a pipeline, <code>$?</code> is the status of the <b>last</b> command only. <code>${PIPESTATUS[@]}</code> lists every stage. With <code>set -o pipefail</code>, the pipeline’s status is the last non-zero one.',
    'echo "${PIPESTATUS[@]}"   ·   set -o pipefail   ·   set -euo pipefail', 'safe',
    [('$?', 'status of the last stage', 'usual check'),
     ('${PIPESTATUS[@]}', 'status of every stage (read it immediately)', 'debugging'),
     ('${PIPESTATUS[0]}', 'the first stage', 'did the producer work?'),
     ('set -o pipefail', 'fail if any stage fails', 'scripts'),
     ('set -euo pipefail', 'strict mode (Lesson 12.6)', 'production scripts'),
     ('141', '128 + SIGPIPE: the reader closed early', 'normal with head')],
    dict(cmd="false | true\necho \"\\$? = $?\"\nfalse | true; echo \"PIPESTATUS = ${PIPESTATUS[*]}\"\nset -o pipefail\nfalse | true\necho \"with pipefail \\$? = $?\"", note='Without pipefail the failure of the first stage is invisible.'),
    [('dba', [
        dict(situation='A compressed backup that silently fails: the dump stage failed, but gzip succeeded.', cmd="fake_dump() { echo '-- partial dump'; echo 'ERROR: lost connection' >&2; return 2; }\nfake_dump | gzip > backup.sql.gz; echo \"without pipefail: $?\"\nset -o pipefail\nfake_dump | gzip > backup.sql.gz; echo \"with pipefail: $?\"",
             why='Real case: <code>mysqldump shop | gzip &gt; shop.sql.gz</code> returns 0 even when mysqldump fails, so a broken backup looks fine. Always use pipefail for backups.')]),
     ('devops', [
        dict(situation='Find which stage of a deploy pipeline failed.', cmd="printf 'a\\nb\\n' | grep zzz | sort; echo \"stages: ${PIPESTATUS[*]}\"",
             why='0 1 0: grep (stage 2) found nothing. Read PIPESTATUS right away: the next command overwrites it.')]),
     ('dev', [
        dict(situation='Why does seq … | head end with status 141?', cmd="seq 1 1000000 | head -n 2; echo \"stages: ${PIPESTATUS[*]}\"",
             why='head exits after 2 lines; seq gets SIGPIPE (13) and stops: 128 + 13 = 141. Normal, and the reason big pipelines with head finish instantly.')]),
    ]
) + cmdcard_u(['two unrelated programs or scripts must exchange a stream', 'a slow producer and a consumer started at different times', 'learning how pipes really work'],
               ['ordinary pipelines (| is simpler)', 'network communication (use sockets)'])(
    'fifo', 'mkfifo', 'named pipe (FIFO)',
    'Creates a pipe that has a name in the file system (type <code>p</code> in <code>ls -l</code>). One process writes to it, another reads from it; data never touches the disk.',
    'mkfifo NAME   ·   writer > NAME &   ·   reader < NAME', 'change',
    [('mkfifo q', 'create a named pipe', 'once'),
     ('ls -l q', 'type p = pipe', 'check'),
     ('cmd > q &', 'writer (waits for a reader)', 'producer'),
     ('cmd < q', 'reader', 'consumer'),
     ('rm q', 'remove it', 'clean up')],
    dict(cmd="mkfifo jobs.pipe\nls -l jobs.pipe | cut -c1-10\n( echo 'job 1'; echo 'job 2' ) > jobs.pipe &\nwhile read -r j; do echo \"worker got: $j\"; done < jobs.pipe\nrm jobs.pipe", note='The writer blocks until the reader opens the pipe; then the lines flow through memory.'),
    [('sys', [
        dict(situation='Feed log lines from one script to another without a temp file.', cmd="mkfifo log.pipe\n( printf 'INFO start\\nERROR disk\\nINFO end\\n' ) > log.pipe &\ngrep ERROR < log.pipe\nrm log.pipe",
             why='The two sides can be completely separate scripts; the FIFO is their meeting point.')]),
     ('data', [
        dict(situation='Compress a stream while a program writes it, without a temporary uncompressed file.', cmd="mkfifo export.pipe\ngzip -c < export.pipe > export.csv.gz &\nseq 1 50000 > export.pipe\nwait; ls -l export.csv.gz | awk '{print $5, $9}'; rm export.pipe",
             why='Useful when a tool insists on writing to a “file”: give it the FIFO and compress on the other side.')]),
    ]
) + undo('Pipes do not change files, but the commands inside them can.', [
    ('A pipeline ends with > file:', 'the same rules as Lesson 5.2: the file is emptied first. Never redirect into a file that an earlier stage reads.'),
    ('tee overwrote a file:', 'tee without -a replaces the file, like &gt;. Use <code>tee -a</code> for logs.'),
    ('| xargs rm or | sh at the end:', 'look at the list first by removing the last stage (Lesson 5.4).'),
    ('A pipeline never finishes:', 'a stage is waiting (a FIFO with no reader, or a command reading the keyboard). Ctrl+C stops all stages.'),
    ('The variable set inside a pipe is empty afterwards:', 'the subshell trap. Use <code>done &lt; &lt;(cmd)</code> or a here-string.'),
]) + errors('Pipeline errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='ls | grepp txt', meaning='A typo in a later stage: “command not found” (127). The first stage still ran.', fix='Check the spelling; use Tab completion.'),
    dict(cmd='ls /nope | wc -l', meaning='The error went to the screen (not into the pipe) and wc counted 0 lines; the status is wc’s: 0.', fix='Use 2&gt;&amp;1 | to count errors; use pipefail in scripts.'),
    dict(cmd='echo hello | tee /proc/version', meaning='tee could not open the file for writing (here a read-only system file). The text still went to stdout.', fix='Check the path and permissions; use sudo tee for root files.'),
    dict(cmd="set -o pipefail; printf 'a\\nb\\n' | grep zzz | wc -l", meaning='grep found nothing (status 1); with pipefail the whole pipeline returns 1 even though wc printed 0.', fix='Expected for “nothing found”. Use <code>grep … || true</code> where no match is fine.'),
]) + qc('After <code>mysqldump shop | gzip &gt; shop.sql.gz</code>, <code>$?</code> is 0. Does that prove the backup worked?', 'No. $? is gzip’s status. Use <code>set -o pipefail</code> or check <code>${PIPESTATUS[0]}</code> for mysqldump.') + '''
'''

SCREENS = screens_block('Real terminal screens: a pipe into less', 'Long output is easier to read in a pager. Riya pipes 200 numbered lines into <code>less</code>, moves through them and quits.',
    "printf '%s\\n' 'PS1=\"riya@laptop:~/lab\\$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ("seq -f 'line %g' 1 200 | less  Enter", "\"seq -f 'line %g' 1 200 | less\" Enter", ': less shows the first screen and waits.'),
    ('Space', 'Space', ': one screen further.'),
    ('/150  Enter', "'/150' Enter", ': search forward for 150: the screen jumps there.'),
    ('G', 'G', ': jump to the end; (END) means there is no more.'),
    ('q', 'q', ': quit; the prompt comes back and the whole pipeline is finished.'),
], 60, 10, hid='screens', what='bash and less')

cards = cards + SCREENS + '</section>\n'

# ---------------------------------------------------------------- 5. animations
STAGES = ['access.log', 'cut -f1', 'sort', 'uniq -c', 'sort -rn | head']
DATA = [['49.36.12.8 - - [06/Nov…', '103.21.44.7 - - …', '49.36.12.8 - - …'], ['49.36.12.8', '103.21.44.7', '49.36.12.8'], ['103.21.44.7', '49.36.12.8', '49.36.12.8'], ['1 103.21.44.7', '2 49.36.12.8', ''], ['2 49.36.12.8', '1 103.21.44.7', '']]
def stage(k, note, tone):
    o = ''.join(label_box(6 + i * 70, 14, 64, 26, [s], ('blue' if i == k else ('green' if i < k else 'card')), 7.4) for i, s in enumerate(STAGES))
    o += ''.join(arrow(70 + i * 70, 27, 76 + i * 70, 27) for i in range(4))
    o += label_box(40, 54, 280, 74, ['output of stage %d' % (k + 1)] + [d for d in DATA[k] if d], 'card', 8.2)
    return o + t(180, 160, note, 8.6, tone, bold=True)
frames = [stage(0, 'The raw log: one request per line.', 'violet'), stage(1, 'cut keeps only field 1: the IP.', 'blue'),
          stage(2, 'sort puts equal IPs next to each other.', 'green'), stage(3, 'uniq -c merges neighbours and counts them.', 'amber'),
          stage(4, 'sort -rn | head: the biggest count first.', 'green')]
s1 = anim_one('Animated pipeline', 'Watch the data change at every stage',
              'Three log lines flowing through the top-IP pipeline. The real outputs are in part 4.',
              'cut | sort | uniq -c | sort -rn | head', 'Five stage boxes; under them the output of the current stage changes from raw log lines to IPs, sorted IPs, counts and the ranked result.', frames,
              ['Stage 1 produces the raw lines.', '<code>cut -d" " -f1</code> keeps the IP.', '<code>sort</code> groups equal IPs.', '<code>uniq -c</code> counts each group.', '<code>sort -rn | head</code> ranks them.'], hid='scenario-pipeline')

def proc(hl, note, tone):
    o = label_box(14, 30, 90, 50, ['seq', 'writer'], 'blue' if 'w' in hl else 'card', 9)
    o += label_box(135, 30, 90, 50, ['pipe', '64 KB buffer'], 'amber' if 'p' in hl else 'card', 9)
    o += label_box(256, 30, 90, 50, ['head -2', 'reader'], 'green' if 'r' in hl else ('red' if 'x' in hl else 'card'), 9)
    return o + arrow(106, 55, 133, 55) + arrow(227, 55, 254, 55) + t(180, 120, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ seq 1 1000000 | head -n 2'], title='riya@laptop', size=8) + cap('Ask for 2 lines out of a million.', '', 'card', y=150, h=34),
       term(14, 16, 332, 116, ['$ seq 1 1000000 | head -n 2', ('1', 'acc'), ('2', 'acc')], title='riya@laptop', size=8) + cap('Two lines appear at once.', '', 'blue', y=150, h=34),
       term(14, 16, 332, 116, ['$ seq 1 1000000 | head -n 2', ('1', 'acc'), ('2', 'acc'), '$ echo ${PIPESTATUS[*]}', ('141 0', 'acc')], title='riya@laptop', size=8) + cap('seq ended with 141: SIGPIPE.', '', 'green', y=150, h=34)]
behind = [proc('wp', 'The shell creates a pipe and starts both at once.', 'violet'),
          proc('wpr', 'seq writes; head reads 2 lines and exits.', 'blue'),
          proc('wpx', 'The next write gets SIGPIPE: seq stops at once.', 'red')]
two = anim_two('Two programs, one pipe, at the same time', 'Behind the screen: pipe() and SIGPIPE',
               'A terminal: seq 1 1000000 | head -n 2 prints 1 and 2 immediately; PIPESTATUS shows 141 0.',
               'Three boxes: the writer seq, the pipe buffer and the reader head; when head exits, seq receives SIGPIPE.', see, behind,
               ['A million numbers, but we only want two.', 'The answer appears instantly.', 'PIPESTATUS shows seq was stopped by a signal.'],
               ['Both processes start together, joined by a kernel pipe.', 'head reads what it needs and exits.', 'Writing to a pipe with no reader sends SIGPIPE: 128 + 13 = 141.'])

dx = dissect('Layer by layer: cut … | sort | uniq -c',
    'What the shell and the kernel do for a three-stage pipeline. Each layer has a real command and output from our build machine.', [
    dict(key='parse', name='The shell', sub='splits at |',
         why='Each part is a separate command.',
         how='bash finds the | characters outside quotes.',
         impl='One process per stage.', used='Every pipeline.',
         cmd="echo 'a|b' | cut -d'|' -f2   # the | inside quotes is just text"),
    dict(key='pipe', name='pipe()', sub='read end + write end',
         why='A one-way channel in the kernel.',
         how='Two descriptors; data written on one is read on the other.',
         impl='A 64 KB ring buffer by default.', used='Every |.',
         cmd="sleep 2 | sleep 2 &\nsleep 0.2; ls -l /proc/$(pgrep -n -x sleep)/fd/0 | sed -E 's/.*-> //'"),
    dict(key='fork', name='Processes', sub='all at the same time',
         why='Stages run in parallel.',
         how='fork() per stage; dup2 connects 1 → pipe → 0.',
         impl='Each stage is a subshell first.', used='Multi-core speed.',
         cmd="bash -c 'echo $BASHPID' | cat; echo \"main shell: $$\""),
    dict(key='flow', name='Streaming', sub='no temp files',
         why='Works on any size.',
         how='The reader processes data as soon as it arrives.',
         impl='Writers block when the buffer is full.', used='GB-size logs.',
         cmd='seq 1 2000000 | sort -n | tail -n 1'),
    dict(key='status', name='Exit status', sub='$? and PIPESTATUS',
         why='Did it work?',
         how='$? = last stage; PIPESTATUS = every stage.',
         impl='bash collects each child’s status.', used='Scripts.',
         cmd='true | false | true; echo "${PIPESTATUS[*]}"'),
], hint='From | to the kernel and back. Click a layer.')

HOOD = hood('Under the hood: one pipe, two programs', 'strace follows both processes (<code>-f</code>): the shell creates the pipe with <code>pipe2()</code>, each child moves its end to fd 0 or 1 with <code>dup2()</code>, then echo writes and wc reads.',
    "bash -c 'echo hello | wc -c'", show='pipe2|dup2\\(.*, [01]\\)|^write\\(1|^read\\(0')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Data flowing through five stages</h2>
''' + s1 + two + dx + HOOD + qc('Why does <code>seq 1 100000000 | head -n 2</code> finish instantly instead of generating 100 million numbers?', 'head exits after two lines; seq’s next write gets SIGPIPE and seq stops. Stages run at the same time, so seq never got far.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Pipelines at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ … | sort |', 'prompt'), ('uniq -c', 'acc')], title='web01', size=6.4, step=12),
              '1. Log analysis', 'Top IPs, slowest pages, error counts: on-call engineers answer them with pipelines before any dashboard exists.', ['Log', '*cut|sort|uniq', 'answer']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['dump | gzip', '> file'], 'blue', 8.6), '2. Backups',
    'mysqldump | gzip, tar | ssh, pg_dump | aws s3 cp - : streaming means no huge temporary files. pipefail makes failures visible.', ['DB', '*| gzip', 'backup']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ make 2>&1 |', 'prompt'), ('tee build.log', 'acc')], title='ci', size=6.2, step=12),
    '3. CI/CD output', 'Build logs are shown live and archived with tee; failing stages are caught with pipefail.', ['Build', '*| tee', 'artifact']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['grep 401', '| uniq -c'], 'red', 8.6), '4. Security triage',
    'Brute-force attempts, unknown users, odd processes: grep | sort | uniq -c gives the first answer in seconds.', ['Alert', '*pipeline', 'block IP']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['csv | cut', '| sort -u'], 'green', 8.6), '5. Quick data work',
    'Data engineers profile files (row counts, distinct values, top categories) with pipelines before loading them.', ['File', '*cut|sort', 'profile']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful pipelines. All really run on our build machine.', [
    dict(level='b', title='Count files', scenario='How many .conf files are directly in /etc?',
         cmd="ls /etc/*.conf | wc -l", explain='One name per line in a pipe, so wc -l counts files.'),
    dict(level='b', title='Only directories', scenario='List only the folders (from your notes).',
         cmd="mkdir -p dd/a dd/b; touch dd/x.txt; ls -l dd | grep '^d'", explain='Directory lines start with d. Quote the pattern.'),
    dict(level='i', title='Total size of .log files', scenario='How many bytes do all .log files use? (from your notes)',
         cmd="seq 1 1000 > a.log; seq 1 500 > b.log; ls -l *.log | awk '{sum += $5} END {print sum}'", explain='Column 5 of ls -l is the size. More robust: <code>du -cb *.log | tail -1</code>.'),
    dict(level='i', title='Last errors', scenario='The last 2 ERROR lines of an app log (from your notes: tail -n 10).',
         cmd="printf 'INFO a\\nERROR db\\nINFO b\\nERROR disk\\nERROR net\\n' > app.log; grep ERROR app.log | tail -n 2", explain='Filter first, then take the end.'),
    dict(level='a', title='Status code report', scenario='How many requests per HTTP status code, most common first?',
         setup=LOG, cmd="awk '{print $9}' access.log | sort | uniq -c | sort -rn", explain='The frequency pipeline works on any column.'),
], extra=build_up('the top-IP report', 'Riya builds the manager’s answer one stage at a time, checking the output after each step (the CloudxLab way).',
    LOG, [
    ("head -n 2 access.log", '1. Look at the data first.'),
    ("cut -d' ' -f1 access.log | head -n 3", '2. Cut out the IP column.'),
    ("cut -d' ' -f1 access.log | sort | uniq -c | head -n 3", '3. Sort and count (still in IP order).'),
    ("cut -d' ' -f1 access.log | sort | uniq -c | sort -rn | head -n 3", '4. Rank by count and keep the top 3.'),
    ("cut -d' ' -f1 access.log | sort | uniq -c | sort -rn | head -n 3 | tee top_ips.txt > /dev/null; cat top_ips.txt", '5. Save the report with tee for the email.'),
])) + which('Choosing the right construct.', [
    ('Output into a command', 'cmd | next', 'Streams, no temp file.', 'cmd > tmp; next < tmp.'),
    ('Count', 'cmd | wc -l  ·  grep -c', 'Fast.', 'Counting by eye.'),
    ('Top N', 'sort | uniq -c | sort -rn | head', 'Classic.', 'uniq without sort.'),
    ('See + save', 'cmd | tee [-a] file', 'Both.', 'Running twice.'),
    ('Root file', '| sudo tee [-a] f > /dev/null', 'Works.', 'sudo … > f.'),
    ('Process running?', 'pgrep -c name', 'Exact.', 'ps | grep | wc (counts grep).'),
    ('Pipeline in a script', 'set -o pipefail', 'Failures seen.', 'Trusting $? alone.'),
    ('Loop over output', 'while read … done < <(cmd)', 'Variables survive.', 'cmd | while … (subshell).'),
]) + keys('Shortcuts and handy forms.', [
    ('|&', 'pipe stdout and stderr (bash)', 'make |& tee build.log'),
    ('Ctrl + C', 'stop every stage of the pipeline', 'a pipeline that waits'),
    ('${PIPESTATUS[*]}', 'status of each stage', 'echo ${PIPESTATUS[*]}'),
    ('line ending in |', 'continue the pipeline on the next line', 'cut … |⏎ sort'),
    ('less: q / G / /text', 'quit / end / search', 'cmd | less'),
    ('tee -a', 'append, do not overwrite', 'cmd | tee -a run.log'),
    ('<(cmd)', 'pipe output as a file name', 'diff <(sort a) <(sort b)'),
    ('Alt + .', 'insert the last argument of the previous command', 'reuse the log file name'),
]) + scriptit('top-ips.sh', 'The manager’s report as a reusable script: strict pipefail, a parameter for N, and a saved copy with tee.',
'''#!/bin/bash
set -o pipefail
''' + LOG.split('\n', 1)[0] + '\n' + LOG.split('\n', 1)[1] + '''
log=access.log; n=${1:-3}
echo "Top $n IPs in $log:"
cut -d' ' -f1 "$log" | sort | uniq -c | sort -rn | head -n "$n" | tee top_ips.txt
echo "401 on /admin: $(grep '"GET /admin' "$log" | grep -c ' 401 ')"''',
'<p>The python block only creates the demo log; on a server you would point <code>log=</code> at <code>/var/log/nginx/access.log</code>.</p>') + puzzle_answer('She sees <b>two</b> file names. The first line of <code>ls -l</code> output is <code>total 16K</code>, so <code>head -n 3</code> shows that line plus two files. Use <code>ls -lhS | head -n 4</code>, <code>ls -lhS | tail -n +2 | head -n 3</code>, or simply <code>ls -S | head -n 3</code> for names only.') + qc('In <code>echo "Asha" | read name; echo $name</code>, why is name empty?', 'Each stage of a pipeline runs in a subshell; read set the variable there, and it vanished with the subshell. Use <code>read name &lt;&lt;&lt; "Asha"</code>.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-standard-streams-stdin-stdout-stderr-and-file/">Lesson 5.1</a> (streams) and <a href="../02-redirection-dev-null-and-here-documents/">5.2</a> (redirection).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
