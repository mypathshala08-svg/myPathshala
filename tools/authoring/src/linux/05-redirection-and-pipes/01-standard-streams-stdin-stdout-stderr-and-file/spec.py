import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='05-redirection-and-pipes', lesson='01-standard-streams-stdin-stdout-stderr-and-file', n='5.1',
    module_label='Module 5 · Redirection, pipes and chaining',
    title='Standard streams: stdin, stdout, stderr and file descriptors',
    desc='The three standard streams every Linux process has: stdin (0), stdout (1) and stderr (2). Where they point (the terminal /dev/pts), commands that read stdin, Ctrl+D, writing errors with >&2, [ -t 1 ], buffering, /proc/PID/fd, lsof and extra descriptors with exec. Each stream explained, then used by admins, developers, DBAs, data engineers, DevOps, security and QA, with real outputs and real terminal screens.',
    og_desc='Why does an error still appear after > file? stdin, stdout, stderr and file descriptors explained with real terminal screens and strace.',
    minutes=36, level='Beginner → Advanced',
    lead='Every Linux command has one way in and two ways out: stdin (0) for input, stdout (1) for results and stderr (2) for errors. This lesson shows where they point, how to see them, and why keeping results and errors apart matters in every IT job.',
    chips=['Streams by field', 'Real terminal screens', 'Under the hood (strace)', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Results on stdout (1), errors on stderr (2)
echo hello > notes.txt
ls notes.txt /nope > out.txt      # only stdout goes into the file
echo "--- out.txt:"
cat out.txt
echo "warning: low disk" >&2      # your own message on stderr
printf 'chai\\ncoffee\\n' | wc -l   # stdin from a pipe
wc -w <<< "one two three"         # stdin from a string
"""

RUN = dict(
    heading='Watch the two output streams split',
    intro='<p>The error from <code>ls</code> and the warning you print with <code>&gt;&amp;2</code> stay on the screen; the result goes into out.txt. Then <code>wc</code> reads stdin from a pipe and from a string.</p>',
    code=MAIN, expect='any',
    anno=[
        ('ls notes.txt /nope > out.txt      # only stdout goes into the file', 'The error still prints.'),
        ('cat out.txt', 'Only notes.txt.'),
        ('echo "warning: low disk" >&2      # your own message on stderr', 'Stream 2.'),
        ("printf 'chai\\ncoffee\\n' | wc -l   # stdin from a pipe", '2'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which lines are errors?', code=MAIN, expect='any'),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what is in err.txt, and what appears on screen? Then run.',
             code="echo hi > a.txt\nls a.txt /nope 2> err.txt\necho '--- err.txt:'\ncat err.txt\n", expect='any'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the message should go to stderr, not into result.txt. Fix the echo.',
             code="echo 'error: input missing' > result.txt\ncat result.txt\n"),
        dict(label='4 · Your turn', hint='Count the words in “Linux is fun to learn” using a here-string.',
             code="wc -w <<< 'Linux is fun to learn'\n"),
        dict(label='5 · Challenge', hint='Print a header file, then the piped rows, then a footer, in one cat.',
             code="echo HEAD > h.txt; echo FOOT > f.txt\nprintf 'r1\\nr2\\n' | cat h.txt - f.txt\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: see the streams in your own terminal',
    intro='<p>The browser runner is not a real terminal, so these show the full picture. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Where do 0, 1, 2 point?', cmd='ls -l /proc/$$/fd', output='lrwx------ 1 riya riya 64 Nov  6 10:30 0 -> /dev/pts/0\nlrwx------ 1 riya riya 64 Nov  6 10:30 1 -> /dev/pts/0\nlrwx------ 1 riya riya 64 Nov  6 10:30 2 -> /dev/pts/0\nlrwx------ 1 riya riya 64 Nov  6 10:30 255 -> /dev/pts/0', note='Recorded in a real terminal on Ubuntu 24.04 (see the screens in part 4). A second terminal window shows /dev/pts/1.'),
        dict(title='2 · Type input, end with Ctrl+D', cmd='sort', output='mango\napple\nkiwi\n^D\napple\nkiwi\nmango', note='Typical. Type three lines, then Ctrl+D at the start of a line.'),
        dict(title='3 · Same command, terminal vs pipe', cmd='ls; echo ---; ls | cat', output='a.txt  b.txt  c.txt\n---\na.txt\nb.txt\nc.txt', note='Typical: columns on the terminal, one per line in a pipe.'),
        dict(title='4 · Watch the system calls', cmd='sudo apt install strace; strace -e trace=write ls notes.txt /nope', output='write(2, "ls: ", 4)                    = 4\nwrite(2, "cannot access \'/nope\'", 21) = 21\nwrite(2, ": No such file or directory", 27) = 27\nwrite(2, "\\n", 1)                      = 1\nwrite(1, "notes.txt\\n", 10)            = 10', note='Recorded on our build machine (see Under the hood).'),
        dict(title='5 · Bash version on our build machine', cmd='bash --version | head -1', output=pc('bash --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Results and errors, line by line',
    intro='<p>Step through a script that writes to both streams. Watch which line goes where.</p>',
    code='''echo "start" > log.txt
echo "processing 3 files"
echo "warning: one file is empty" >&2
n=$(wc -l < log.txt)
echo "log has $n line"
''',
    notes={1: 'File :: stdout into log.txt.', 2: 'stdout :: On the screen.', 3: 'stderr :: Also on screen, but stream 2.', 4: 'stdin :: wc reads the file through fd 0.', 5: 'Result :: 1 line.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s clean script output, an admin’s quiet search, and a DevOps check of where a service writes.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Results in a file, errors on screen',
         problem='<p>List the sizes of three config files into sizes.txt. One file does not exist; its error must stay visible.</p>',
         inp='app.conf and web.conf exist, db.conf does not',
         approach=['wc -c writes results to stdout and errors to stderr.', '&gt; sizes.txt moves only the results.'],
         code='''echo 'port=80' > app.conf; echo 'root=/var/www' > web.conf
wc -c app.conf web.conf db.conf > sizes.txt
echo "--- sizes.txt:"
cat sizes.txt
''', expect='any',
         notes={2: 'Split :: The db.conf error reaches the screen.', 4: 'File :: Only results and the total.'},
         tryit='Add 2&gt; errors.txt and run again.'),
    dict(level='i', tag='System admin', title='Search without the noise',
         problem='<p>Find files named passwd under /etc as a normal user, without dozens of “Permission denied” lines.</p>',
         inp='/etc as user riya',
         approach=['find prints errors on stderr.', '2&gt;/dev/null hides them; results stay.'],
         code='''find /etc -name passwd 2>/dev/null
echo "errors hidden: $(find /etc -name passwd 2>&1 >/dev/null | wc -l)"
''',
         notes={1: 'Results :: Clean list.', 2: 'Count :: How many errors were hidden (2>&1 >/dev/null keeps only stderr; Lesson 5.2).'},
         tryit='Remove 2&gt;/dev/null from the first line.'),
    dict(level='a', tag='DevOps', title='Where is the background job writing?',
         problem='<p>A job was started in the background with its output redirected. Find out where fd 1 and 2 point.</p>',
         inp='a running background job',
         approach=['$! is the job’s PID.', '/proc/PID/fd shows the links.'],
         code='''sleep 20 > worker.log 2> worker.err &
pid=$!
for fd in 0 1 2; do echo "fd $fd -> $(readlink /proc/$pid/fd/$fd)"; done
kill $pid
''',
         notes={1: 'Start :: Background job with redirections.', 3: 'Look :: readlink prints each target.', 4: 'Clean up.'},
         tryit='Start it without redirections and compare.'),
]

QUIZ = mix([
    dict(q='What is the file descriptor number of stderr?', options=['0', '1', '2', '3'], answer=2,
         why='0 stdin, 1 stdout, 2 stderr.'),
    dict(q='ls good.txt /nope > out.txt: what appears on the screen?', options=['good.txt', 'the error message', 'nothing', 'both'], answer=1,
         why='> moves only stdout; the error is on stderr.'),
    dict(q='wc -l with no file seems to hang. What is it doing?', options=['crashed', 'reading stdin from the keyboard', 'counting the whole disk', 'waiting for the network'], answer=1,
         why='Type lines and press Ctrl+D.'),
    dict(q='Which key ends keyboard input?', options=['Ctrl+C', 'Ctrl+D', 'Ctrl+Z', 'Esc'], answer=1,
         why='Ctrl+D = end of file. Ctrl+C cancels the command.'),
    dict(q='How does a script print an error on stderr?', options=['echo "err" > 2', 'echo "err" >&2', 'echo "err" 2>', 'stderr "err"'], answer=1,
         why='>&2 means “to file descriptor 2”. > 2 would create a file named 2.'),
    dict(q='Where can you see the open files of process 1234?', options=['/etc/1234', '/proc/1234/fd', '/dev/1234', '/var/fd/1234'], answer=1,
         why='/proc/PID/fd has one link per descriptor.'),
    dict(q='Why do tools like curl print progress on stderr?', options=['It is faster', 'So stdout carries only data for files and pipes', 'stderr is coloured', 'By accident'], answer=1,
         why='Data on 1, messages on 2.'),
    dict(q='Does an error message go through a pipe | by default?', options=['Yes', 'No, only stdout does', 'Only in bash', 'Only with sudo'], answer=1,
         why='Use 2>&1 or |& to pipe stderr too.'),
])

REVISION = [
    '<b>stdin 0</b> (keyboard), <b>stdout 1</b> (screen), <b>stderr 2</b> (screen). Every process inherits them.',
    '<code>&gt;</code> = <code>1&gt;</code>: moves only results. Errors still show; move them with <code>2&gt;</code>.',
    'With no file name, cat, wc, sort, grep, read read stdin. <kbd>Ctrl+D</kbd> ends input; <kbd>Ctrl+C</kbd> cancels.',
    'Feed stdin: <code>&lt; file</code>, <code>cmd |</code>, <code>&lt;&lt;&lt; "text"</code>, <code>-</code> as a file name, <code>&lt; /dev/null</code> for nothing.',
    'In scripts: <code>echo "error: …" &gt;&amp;2</code>. Results on 1, problems on 2.',
    '<code>[ -t 1 ]</code> tests for a terminal; ls and grep change format when piped.',
    'stdout is buffered in files and pipes, stderr is not: <code>python3 -u</code>, <code>flush=True</code>, <code>stdbuf -oL</code>.',
    '<code>ls -l /proc/$$/fd</code>, <code>lsof -p PID</code>; <code>exec 3&gt; file</code>, <code>&gt;&amp;3</code>, <code>exec 3&gt;&amp;-</code>.',
]

FAQ = [
    ('What are stdin, stdout and stderr in Linux?', 'The three standard streams every process starts with: standard input (fd 0, keyboard by default), standard output (fd 1, screen) and standard error (fd 2, screen).'),
    ('Why does an error still appear on screen when I redirect output to a file?', 'Because > only redirects stdout (fd 1). Errors are written to stderr (fd 2); redirect them with 2> or combine with 2>&1.'),
    ('What is a file descriptor?', 'A small number a process uses to refer to an open file, device, pipe or socket. 0, 1 and 2 are the standard streams; others start at 3.'),
    ('How do I end input when a command is reading from the keyboard?', 'Press Ctrl+D at the start of a line (end of file). Ctrl+C cancels the command instead.'),
    ('How do I print to stderr in a bash script?', 'echo "message" >&2 (or printf "…" >&2).'),
    ('Why is my Python output delayed when I pipe it?', 'stdout is block-buffered when it is not a terminal. Use python3 -u, print(..., flush=True) or PYTHONUNBUFFERED=1.'),
    ('How can I see which files a process has open?', 'ls -l /proc/PID/fd, or lsof -p PID.'),
]

PRACTICE_INTRO = 'Small tasks with the three streams. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Count with stdin', stmt='Count the lines of drinks.txt through stdin, so that no file name is printed.', inp="drinks.txt with 3 lines",
         code="printf 'chai\\ncoffee\\nlassi\\n' > drinks.txt\nwc -l < drinks.txt\n", explain='< feeds the file to fd 0.'),
    dict(level='easy', title='Error on stderr', stmt='Print “error: no input” on stderr.', inp='—',
         code='echo "error: no input" >&2\n', explain='>&2 = to descriptor 2.'),
    dict(level='easy', title='Words in a string', stmt='Count the words in “I love Linux” with a here-string.', inp='a string',
         code="wc -w <<< 'I love Linux'\n", explain='<<< gives one string as stdin.'),
    dict(level='medium', title='Only the result in a file', stmt='List a.txt and /nope into out.txt; then show out.txt.', inp='a.txt exists',
         code="echo x > a.txt\nls a.txt /nope > out.txt\ncat out.txt\n", explain='The error stays on screen; out.txt has a.txt.', expect='any'),
    dict(level='medium', title='Stdin in the middle', stmt='Print START, then the piped words red and blue, then END, with one cat.', inp='—',
         code="echo START > s.txt; echo END > e.txt\nprintf 'red\\nblue\\n' | cat s.txt - e.txt\n", explain='- = stdin.'),
    dict(level='medium', title='Terminal or not?', stmt='Print “tty” if stdout is a terminal, else “not a tty”.', inp='—',
         code="[ -t 1 ] && echo tty || echo 'not a tty'\n", explain='In the runner stdout is captured, so: not a tty.'),
    dict(level='business', title='Separate logs', stmt='Run ls on a.txt and /nope; put results in ok.log and errors in err.log; print both counts.', inp='a.txt exists',
         code="echo x > a.txt\nls a.txt /nope > ok.log 2> err.log\necho \"ok: $(wc -l < ok.log)  errors: $(wc -l < err.log)\"\n", explain='Each stream to its own file.'),
    dict(level='business', title='A log channel on fd 3', stmt='Open fd 3 to audit.log, write “login riya” to it, close it, show the file.', inp='—',
         code='exec 3> audit.log\necho "login riya" >&3\nexec 3>&-\ncat audit.log\n', explain='exec opens and closes descriptors in the current shell.'),
]

SCN_INTRO = 'Interview questions about standard streams, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What are 0, 1 and 2 in Linux?”',
        'A classic first-round question.',
        'do you know the standard streams?',
        '''<ul>
          <li>0 stdin (input, keyboard), 1 stdout (results, screen), 2 stderr (errors, screen).</li>
          <li>Every process inherits them from its parent, the shell.</li>
          <li>Example: <code>ls good /bad &gt; out.txt</code> still shows the error, because &gt; moves only 1.</li>
        </ul>''', 'saying “0 is false, 1 is true”: that is exit codes, a different topic (5.4).') +
    scn('Operations · cron', 'Junior', 'The nightly job that “never fails”',
        'A cron job’s log is always clean, but the backups are missing. The crontab line is <code>./backup.sh &gt; /var/log/backup.log</code>.',
        'do you know where stderr goes without a terminal?',
        '''<ol>
          <li>Errors are on stderr, which was not redirected: cron mailed them to a local mailbox nobody reads.</li>
          <li>Fix: <code>&gt;&gt; /var/log/backup.log 2&gt;&amp;1</code> (Lesson 5.2), and make the script exit non-zero on failure.</li>
          <li>Add a check that alerts when the log contains “error” or the backup file is missing.</li>
        </ol>''', '“the log is empty, so it worked”.') +
    scn('Product team · developer', 'Mid-level', 'Our CLI breaks other people’s pipelines',
        'Users pipe your tool’s JSON into <code>jq</code>, but it fails: “parse error”. Your tool prints “Connecting…” and warnings.',
        'do you design command-line tools properly?',
        '''<ul>
          <li>Data on stdout only; progress, prompts and warnings on stderr.</li>
          <li>Non-zero exit status on failure; quiet by default when stdout is not a terminal (<code>isatty(1)</code>).</li>
          <li>Offer <code>-q</code>/<code>--json</code>; add a test that stdout parses as JSON.</li>
        </ul>''', 'telling users to delete the first line with sed.') +
    scn('Platform · containers', 'Senior', 'Logs appear minutes late in the dashboard',
        'A Python service in Docker shows no logs for minutes, then many at once. After a crash the last lines are missing.',
        'do you understand buffering?',
        '''<ul>
          <li>stdout is block-buffered when it is not a terminal (a container log pipe).</li>
          <li><code>PYTHONUNBUFFERED=1</code> / <code>python -u</code>, or flush per line; other runtimes: line-buffered loggers, <code>stdbuf -oL</code>.</li>
          <li>Log to stdout/stderr and let the platform collect them (12-factor); never only to a file inside the container.</li>
        </ul>''', 'adding sleep calls so the buffer fills faster.')
) + interview([
    ('What are the file descriptor numbers of stdin, stdout and stderr?', '0, 1 and 2.'),
    ('Why does an error appear on screen after command > file?', '> redirects only stdout; errors are on stderr.'),
    ('How do you write to stderr in bash?', 'echo "msg" >&2.'),
    ('How do you end input typed on the keyboard?', 'Ctrl+D (EOF) at the start of a line.'),
    ('How can you check if a script’s output goes to a terminal?', '[ -t 1 ] (isatty on fd 1).'),
    ('Where can you see a process’s open file descriptors?', '/proc/PID/fd, or lsof -p PID.'),
    ('Why may output and errors appear in the wrong order in a log file?', 'stdout is buffered when writing to a file; stderr is not.'),
], [
    ('RHCSA (EX200)', '“Use input-output redirection (&gt;, &gt;&gt;, |, 2&gt;, etc.)”: knowing the three streams is the base of this objective.'),
    ('LFCS', 'Essential commands: use streams, pipes and redirects.'),
    ('CompTIA Linux+', 'Standard input, output and error, file descriptors and redirection operators.'),
]) + distro('The streams are the same on every Unix-like system; the tools around them differ a little.', [
    ('fd 0 1 2, >&2', 'yes', 'yes', 'yes', 'yes (WSL and Git Bash)'),
    ('/proc/PID/fd', 'yes', 'yes', 'no /proc: use lsof -p PID', 'WSL yes; Git Bash: partial'),
    ('/dev/stdin, /dev/stdout', 'yes', 'yes', 'yes', 'yes'),
    ('lsof', 'install lsof on minimal', 'install lsof on minimal', 'installed', 'WSL: install'),
    ('stdbuf', 'coreutils', 'coreutils', 'no (brew coreutils: gstdbuf)', 'WSL yes'),
    ('Terminal device', '/dev/pts/N', '/dev/pts/N', '/dev/ttys00N', 'WSL /dev/pts/N; Git Bash /dev/cons*'),
]) + teaser('5.2', 'Riya wants the nightly job’s results and errors in one log file, appended every night, and wants to feed a 20-line SQL script to a command without creating a file. Which three small operators does she need, and why does the order of 2&gt;&amp;1 matter?')

CHEATSHEET = cheatsheet('standard streams', [
    ('The three streams', [('0  stdin', 'input · keyboard'), ('1  stdout', 'results · screen'), ('2  stderr', 'errors · screen'), ('> = 1>', 'moves only results'), ('2>', 'moves errors')]),
    ('Feeding stdin', [('cmd < file', 'from a file'), ('a | cmd', 'from a command'), ("cmd <<< 'text'", 'from a string'), ('cat h - f', '- = stdin here'), ('cmd < /dev/null', 'no input')]),
    ('Keyboard', [('Ctrl+D', 'end of input'), ('Ctrl+C', 'cancel'), ('reset', 'fix the terminal'), ('tty', 'which terminal?'), ('[ -t 1 ]', 'stdout a terminal?')]),
    ('In scripts', [('echo "error" >&2', 'message to stderr'), ('exec 3> log', 'open fd 3'), ('echo x >&3', 'write fd 3'), ('exec 3>&-', 'close fd 3'), ('python3 -u', 'no buffering')]),
    ('Inspect', [('ls -l /proc/$$/fd', 'my shell'), ('ls -l /proc/PID/fd', 'any process'), ('lsof -p PID', 'details'), ('ls -l /dev/std*', 'the links'), ('strace -e trace=write', 'see writes')]),
])

MINDMAP = mindmap('Standard streams', [
    ('stdin 0', 'blue', ['keyboard, < file', 'pipe, <<<, -', 'Ctrl+D ends']),
    ('stdout 1', 'green', ['results', '> >> |', 'buffered in files']),
    ('stderr 2', 'red', ['errors, progress', '2> 2>/dev/null', 'unbuffered']),
    ('Scripts', 'amber', ['echo … >&2', '[ -t 1 ]', 'exit status (5.4)']),
    ('fd table', 'violet', ['inherited by children', '/proc/PID/fd, lsof', 'exec 3> … 3>&-']),
    ('Why', 'acc', ['clean pipelines', 'visible errors', 'secrets on stdin']),
])

LAB = lab('separate results from errors', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab51 && cd ~/lab51 && rm -f *.txt *.log
printf 'Pune\\nAgra\\nGoa\\n' > cities.txt''',
    tasks=['Write the number of lines of cities.txt into <code>count.txt</code> using stdin (so that only the number is in the file).',
           'Run <code>ls cities.txt nofile.txt</code> so that the result goes into <code>ok.log</code> and the error into <code>err.log</code>.',
           'Write the text <code>ALERT</code> to stderr and catch it in <code>alert.log</code> (hint: <code>{ echo ALERT &gt;&amp;2; } 2&gt; alert.log</code>).',
           'Using a here-string, write the number of words in “stdin stdout stderr” into <code>words.txt</code>.'],
    solution='''wc -l < cities.txt > count.txt
ls cities.txt nofile.txt > ok.log 2> err.log
{ echo ALERT >&2; } 2> alert.log
wc -w <<< 'stdin stdout stderr' > words.txt''',
    check='''cd ~/lab51
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 count via stdin"  '[ "$(cat count.txt 2>/dev/null)" = 3 ]'
ok "2 split streams"    'grep -qx cities.txt ok.log 2>/dev/null && grep -q nofile err.log 2>/dev/null && ! grep -q nofile ok.log'
ok "3 alert on stderr"  '[ "$(cat alert.log 2>/dev/null)" = ALERT ]'
ok "4 word count"       '[ "$(cat words.txt 2>/dev/null)" = 3 ]' ''')
