import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

RC = "printf '%s\\n' 'PS1=\"riya@laptop:~/lab\\$ \"' > ~/.mprc; echo 'hello' > notes.txt"
SH = 'bash --rcfile ~/.mprc'

HOOK = hook('Riya runs her backup script with <code>./backup.sh &gt; backup.log</code> so that nothing appears on the screen. But one red line still prints: <code>tar: /data/old: Cannot open: No such file or directory</code>. And when she opens backup.log, that line is not in it. Where did the error go, and why did it ignore her <code>&gt;</code>? The answer is the single most useful idea in the Linux shell: every program has <b>three separate streams</b>.',
    ['name the three standard streams and their numbers (stdin 0, stdout 1, stderr 2) and say where each one goes by default',
     'predict which text a command sends to stdout and which to stderr, and see it for yourself',
     'feed a command from the keyboard, a file, a pipe or a here-string, and end keyboard input with Ctrl+D',
     'look at any process’s file descriptors in <code>/proc/PID/fd</code>, and write your own messages to stderr in scripts'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the error that ignored >'),
    ('decide', 'Which stream when?', 2, 'the quick chart'),
    ('definition', 'What streams are', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each stream, by field', 14, 'options, real runs, your field'),
    ('screens', 'Real terminal screens', 4, 'see /dev/pts and Ctrl+D'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'three pipes out of one program'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which stream? (decide in 5 seconds)', [
    ('Normal results of a command', 'stdout (1)', 'goes to the screen, or to > file, or into | the next command'),
    ('Error and warning messages', 'stderr (2)', 'stays on the screen even with > file; catch it with 2>'),
    ('Input a command reads when you give it no file', 'stdin (0)', 'the keyboard, < file, a pipe, or <<< "text"'),
    ('A command “hangs” with no prompt', 'it is reading stdin', 'type the input and press Ctrl+D (end), or Ctrl+C to cancel'),
    ('Your script must report an error', 'echo "error: …" >&2', 'so it is not mixed into the real output'),
    ('Is my output going to a screen or a file?', '[ -t 1 ]', 'true only when stdout is a terminal'),
    ('Which files does a running process have open?', 'ls -l /proc/PID/fd', 'or lsof -p PID'),
    ('A program wants a file name but you have a pipe', '- or /dev/stdin', 'echo hi | cat header.txt -'),
])

cmap = concept_map(
    [('3.1', 'Creating files', 'echo "text" > file (a first redirection)'), ('3.5', 'Viewing files', 'cat, wc and less read stdin too'), ('1.6', 'Terminal and shell', 'the program that connects the streams')],
    ['stdin, stdout and stderr: the three standard streams', 'file descriptors 0, 1, 2 and the fd table', 'where they point: the terminal /dev/pts/N', 'commands that read stdin when no file is given; Ctrl+D', 'writing to stderr from scripts (>&2), [ -t 1 ], /proc/PID/fd'],
    [('5.2', 'Redirection', 'point the streams at files: > >> < 2> 2>&1'), ('5.3', 'Pipes and tee', 'connect stdout to stdin'), ('5.4', 'Chaining and exit codes', 'the fourth signal: the exit status'), ('12.5', 'Shell scripts', 'clean output and errors')],
    'Everything in Module 5 (redirection, pipes, tee, xargs) is about moving these three streams around. Learn them once and the rest is easy.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ ./backup.sh > backup.log', ('tar: /data/old: Cannot open: No such', 'err'), ('file or directory', 'err'), '$ grep Cannot backup.log', ('(nothing)', 'dim'), '$ ./backup.sh > backup.log 2> errors.log', '$ cat errors.log', ('tar: /data/old: Cannot open: …', 'acc')], title='riya@server: ~', size=7.0, step=15)
      + t(352, 36, 'One program, two outputs:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• stdout (1): the results', '• stderr (2): the errors', '• > moves only stdout', '• 2> moves stderr', '• and stdin (0) is the input'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The error that ignored the arrow</h2>
  <div class="story">
''' + puzzle('Riya runs <code>ls notes.txt /nope &gt; out.txt</code>. One line appears on the screen. Which line is it, and what is inside out.txt afterwards? (notes.txt exists, /nope does not.)') + '''
    <p class="narration">Riya’s nightly backup script should be silent and write everything into backup.log. Yet one error keeps appearing on the screen, and it never reaches the log.</p>
''' + scene('A terminal: ./backup.sh > backup.log still prints a tar error on screen; grep finds nothing in backup.log; with 2> errors.log the error lands in errors.log.', sc,
            'Results and errors travel on <tspan font-weight="700" class="s-acc">two different streams</tspan>.') + '''
A> Your script did nothing wrong. Every program has two ways to write: <b>standard output</b> for results and <b>standard error</b> for problems. <code>&gt;</code> only moves the first one.
R> So the error went straight to my screen, past the log?
K> Exactly. That is deliberate: if errors went into the results file, you would never see them, and the file would contain garbage.
A> Today: the three standard streams, their numbers 0, 1 and 2, how to see them, and how every IT role relies on keeping them apart. Lesson 5.2 then shows every way to redirect them.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
def _pipe(x, y, w, label, sub, tone):
    return label_box(x, y, w, 34, [label, sub], tone, 8.6)
pic = ('<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="A kitchen counter: orders come in through one window (stdin), finished plates go out through the serving hatch (stdout), and complaints go to the manager’s phone (stderr).">'
       + _pipe(20, 40, 150, 'Order window', 'stdin · 0 · input', 'blue')
       + label_box(240, 22, 160, 112, ['The cook', '(the program)', 'reads orders,', 'cooks, reports'], 'card', 9)
       + _pipe(470, 22, 150, 'Serving hatch', 'stdout · 1 · results', 'green')
       + _pipe(470, 100, 150, 'Manager’s phone', 'stderr · 2 · problems', 'red')
       + arrow(172, 57, 236, 57) + arrow(402, 40, 466, 40) + arrow(402, 117, 466, 117)
       + t(320, 168, 'Plates and complaints never use the same door,', 9.6, 'ink2')
       + t(320, 190, 'so a bad order never ends up on a customer’s plate.', 9.6, 'acc', bold=True)
       + '<text x="632" y="214" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Standard streams at four depths', [
    ('v', 'No jargon: the restaurant kitchen', '      <p>Think of a cook in a restaurant kitchen.</p>' + pic + '''
      <ul>
        <li>Orders come in through one window: that is <b>stdin</b>, the input.</li>
        <li>Finished plates go out through the serving hatch: that is <b>stdout</b>, the results.</li>
        <li>Problems (“we are out of paneer”) go to the manager’s phone: that is <b>stderr</b>, the errors.</li>
        <li>The cook never decides where the hatch leads. The restaurant (the shell) does, and it can move the hatch to a delivery van (a file) or to the next cook (a pipe).</li>
      </ul>'''),
    ('b', 'The three streams every command has', '''      <ul>
        <li><b>stdin</b>, number <b>0</b>: where a command reads input. Default: the keyboard.</li>
        <li><b>stdout</b>, number <b>1</b>: where it writes normal results. Default: the screen.</li>
        <li><b>stderr</b>, number <b>2</b>: where it writes errors and warnings. Default: also the screen.</li>
        <li>Because stdout and stderr both go to the screen, they look like one stream. They are not: <code>ls notes.txt /nope &gt; out.txt</code> moves only stdout, so the error still appears.</li>
        <li>Commands such as <code>cat</code>, <code>wc</code>, <code>sort</code>, <code>grep</code> read stdin when you give them no file. If one seems to “hang”, it is waiting for you: type, then press <kbd>Ctrl+D</kbd>.</li>
      </ul>'''),
    ('i', 'File descriptors and the terminal', '''      <ul>
        <li>The numbers 0, 1, 2 are <b>file descriptors</b> (fd): small numbers a process uses to refer to its open files. A process can open more (3, 4, …).</li>
        <li>In a terminal, all three point to the same device, the <b>pseudo-terminal</b> <code>/dev/pts/0</code>. See it with <code>ls -l /proc/$$/fd</code> (<code>$$</code> = your shell’s process ID).</li>
        <li>Programs behave differently when stdout is not a terminal: <code>ls</code> prints one name per line, <code>grep --color=auto</code> stops colouring. Test it yourself with <code>[ -t 1 ]</code>.</li>
        <li>In scripts, send your own error messages to stderr with <code>echo "error: …" &gt;&amp;2</code>, so callers can separate them.</li>
        <li><kbd>Ctrl+D</kbd> at the start of a line means “end of input” (EOF); <kbd>Ctrl+C</kbd> stops the program instead.</li>
      </ul>'''),
    ('a', 'Behind the screen: the fd table, inheritance and buffering', '''      <ul>
        <li>The kernel keeps a <b>file descriptor table</b> for every process. A child process (every command you run) <b>inherits</b> a copy of its parent’s table, which is why commands start with the shell’s 0, 1 and 2.</li>
        <li>Redirection is done by the shell <b>before</b> the command starts: it opens the file and copies the descriptor into position 1 (the <code>dup2()</code> system call). The program never knows: it just writes to fd 1.</li>
        <li><b>Buffering:</b> the C library sends stdout to a terminal line by line, but to a file or pipe in blocks (often 4–64 KB); stderr is unbuffered. That is why, in a file, errors can appear <i>before</i> output that was printed earlier (see “Under the hood”). Python: <code>python3 -u</code> or <code>flush=True</code>; other programs: <code>stdbuf -oL</code>.</li>
        <li><code>/dev/stdin</code>, <code>/dev/stdout</code>, <code>/dev/stderr</code> are links to <code>/proc/self/fd/0</code>, <code>1</code> and <code>2</code>: a way to give a stream to programs that only accept file names.</li>
        <li>The convention is POSIX: fd 0, 1, 2 (<code>STDIN_FILENO</code>, <code>STDOUT_FILENO</code>, <code>STDERR_FILENO</code> in C), used by every Unix-like system since the 1970s.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>stdin, stdout, stderr and file descriptors</h2>
''' + def_block(
    'The <b>standard streams</b> are three communication channels that every process starts with: <b>standard input</b> (stdin, file descriptor 0) for reading input, <b>standard output</b> (stdout, fd 1) for normal output, and <b>standard error</b> (stderr, fd 2) for error and diagnostic messages. A <b>file descriptor</b> is a small non-negative integer that a process uses to refer to an open file, device, pipe or socket.',
    'One way in, two ways out: input on 0, results on 1, problems on 2.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Standard streams', f'stdin, stdout, stderr. {gl("standard-streams-stdin-stdout-stderr", "Glossary →")}'),
    ('File descriptor (fd)', f'The number of an open file inside a process: 0, 1, 2, 3 … {gl("file-descriptor-fd", "Glossary →")}'),
    ('Terminal / pts', 'The device your keyboard and screen are connected through, e.g. <code>/dev/pts/0</code>.'),
    ('EOF', 'End of file: “no more input”. Ctrl+D sends it from the keyboard.'),
    ('Redirection', f'Pointing a stream at a file instead of the terminal (Lesson 5.2). {gl("redirection-2", "Glossary →")}'),
    ('Pipe', f'Connects one command’s stdout to the next command’s stdin (Lesson 5.3). {gl("pipe", "Glossary →")}'),
    ('/proc', f'A virtual folder with live information about processes. {gl("proc", "Glossary →")}'),
    ('Buffering', 'Collecting output in memory and writing it in larger pieces.'),
]) + '\n' + names('Where the names come from.', [
    ('stdin', 'standard input', 'From the C library name <code>stdin</code>.'),
    ('stdout', 'standard output', 'The “normal” channel.'),
    ('stderr', 'standard error', 'Added in Unix V6 (1975) so that errors would not end up inside pipelines.'),
    ('fd', 'file descriptor', 'It “describes” which open file you mean.'),
    ('tty', 'teletypewriter', 'The printing terminals of early Unix; the name stuck.'),
    ('pts', 'pseudo-terminal slave', 'The software terminal behind each terminal window or SSH session.'),
    ('$$', 'this shell’s PID', 'Used in <code>/proc/$$/fd</code>.'),
    ('EOF', 'end of file', 'Ctrl+D at the start of a line.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('stdin', '<b>0</b> · keyboard · read by cat, wc, sort, grep, read'),
    ('stdout', '<b>1</b> · screen · moved by <code>&gt;</code> and <code>|</code>'),
    ('stderr', '<b>2</b> · screen · moved only by <code>2&gt;</code>'),
    ('End keyboard input', '<kbd>Ctrl+D</kbd> (Ctrl+C cancels)'),
    ('See the fds', '<code>ls -l /proc/$$/fd</code>'),
    ('Error from a script', '<code>echo "error: …" &gt;&amp;2</code>'),
]) + '\n' + lv + didyou('Standard error was not in the first Unix versions. Errors went to stdout, so when Bell Labs started sending command output straight to the phototypesetter, error messages came out typeset on expensive photographic paper. stderr was added (around 1975) so that errors always reach a person instead of the next program or file.') + '''
EXAM> “What are stdin, stdout and stderr, and what are their file descriptor numbers?” → 0 = standard input (keyboard), 1 = standard output (screen), 2 = standard error (screen); every process inherits them from its parent; &gt; moves 1, 2&gt; moves 2, &lt; feeds 0.
''' + qc('Name the three streams with their numbers, and say which one <code>&gt;</code> moves.', 'stdin 0, stdout 1, stderr 2. A plain <code>&gt;</code> means <code>1&gt;</code>: only stdout. Errors (2) still reach the screen.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The three streams side by side</h2>
''' + table(['', 'stdin', 'stdout', 'stderr'], [
    ['Number (fd)', '<b>0</b>', '<b>1</b>', '<b>2</b>'],
    ['Direction', 'into the program', 'out of the program', 'out of the program'],
    ['Default', 'keyboard', 'screen', 'screen'],
    ['Carries', 'data to process', 'results', 'errors, warnings, progress'],
    ['Buffered?', 'yes', 'by line (terminal) / by block (file, pipe)', '<b>no</b>: appears immediately'],
    ['Redirect with', '<code>&lt; file</code>, <code>&lt;&lt;&lt;</code>, <code>&lt;&lt;</code>', '<code>&gt;</code> <code>&gt;&gt;</code> <code>1&gt;</code>', '<code>2&gt;</code> <code>2&gt;&gt;</code>'],
    ['Goes through a pipe <code>|</code>?', 'it is the receiving end', '<b>yes</b>', '<b>no</b> (unless <code>2&gt;&amp;1</code> or <code>|&amp;</code>)'],
    ['Device file', '<code>/dev/stdin</code>', '<code>/dev/stdout</code>', '<code>/dev/stderr</code>'],
], minw=600) + '''
  <h3>Where can stdin come from?</h3>
''' + table(['Source', 'Example', 'When to use it'], [
    ['the keyboard (default)', '<code>wc -l</code> then type, <kbd>Ctrl+D</kbd>', 'quick tests, interactive tools'],
    ['a file', '<code>wc -l &lt; notes.txt</code>', 'a program that only reads stdin; scripts'],
    ['another command (pipe)', '<code>ls | wc -l</code>', 'building pipelines (Lesson 5.3)'],
    ['a string (here-string)', '<code>wc -w &lt;&lt;&lt; "one two three"</code>', 'one value from a variable'],
    ['several lines (here-document)', '<code>cat &lt;&lt; EOF … EOF</code>', 'templates, SQL, config (Lesson 5.2)'],
    ['nothing at all', '<code>cmd &lt; /dev/null</code>', 'stop a program from waiting for input (cron, ssh loops)'],
], minw=560) + mistake('wc -l     (then the terminal “hangs”, so you close the window)', 'wc -l notes.txt   ·   or type the lines and press Ctrl+D',
                       'The command is not stuck. With no file name it reads stdin, which is your keyboard. Ctrl+D ends the input and wc prints the count; Ctrl+C cancels.') + qc('Why does <code>sort</code> with no file name seem to freeze?', 'It is reading stdin from the keyboard. Type lines and press Ctrl+D, or give it a file.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each stream explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04. Our recorder collects stdout and stderr into one window, exactly as your terminal shows them; the examples move one stream to a file and then <code>cat</code> it, so you can see which line travelled where.</p>
''' + cmdcard_u(['a command should read data you type, paste, pipe or redirect', 'a script asks a question (<code>read</code>)', 'passing secrets without putting them on the command line'],
               ['the program already takes a file name (just give it the file)', 'cron jobs and background jobs: nobody is at the keyboard (use <code>&lt; /dev/null</code> or a file)'])(
    'stdin', 'stdin  (fd 0)', 'standard input',
    'The stream a command reads from. Many commands read stdin whenever you give them no file: <code>cat</code>, <code>wc</code>, <code>sort</code>, <code>grep</code>, <code>tr</code>, <code>read</code>, <code>python3</code>, <code>mysql</code>.',
    'command            (reads the keyboard)   ·   command < file   ·   cmd1 | command   ·   command <<< "text"', 'safe',
    [('(no file)', 'read the keyboard; Ctrl+D ends', 'quick tests'),
     ('< file', 'read a file through stdin', 'tools that only read stdin'),
     ('cmd |', 'read another command’s output', 'pipelines'),
     ('<<< "text"', 'read one string (here-string)', 'a value from a variable'),
     ('-  (a dash as file name)', '“read stdin here”, between real files', 'cat header.txt - footer.txt'),
     ('/dev/stdin', 'stdin as a file name', 'programs that insist on a path'),
     ('read VAR', 'bash reads one line into a variable', 'questions in scripts'),
     ('< /dev/null', 'empty input: no waiting', 'cron, ssh in loops')],
    dict(cmd="printf 'chai\\ncoffee\\nlassi\\n' > drinks.txt\nwc -l drinks.txt\nwc -l < drinks.txt\nprintf 'a\\nb\\n' | wc -l\nwc -w <<< 'one two three'", note='The same <code>wc</code>, four ways of getting input. With a file name wc prints the name; with stdin it does not know any name.'),
    [('sys', [
        dict(situation='A script asks for a value; here the answer comes from a here-string so it can run unattended.', cmd='read -r name <<< "Riya"\necho "Hello, $name"',
             why='<code>read</code> reads one line from stdin. Interactively it waits for the keyboard; in automation you feed it.'),
        dict(situation='Stop a command from waiting for keyboard input in a cron job.', cmd='cat < /dev/null; echo "cat finished at once, exit $?"',
             why='/dev/null as stdin gives immediate end-of-file, so nothing can hang waiting for a person.')]),
     ('data', [
        dict(situation='Sort numbers that arrive from another command, not from a file.', cmd="printf '30\\n4\\n100\\n' | sort -n",
             why='sort reads stdin when given no file; -n sorts numerically.'),
        dict(situation='Add a header line in front of a CSV that streams in.', cmd="echo 'id,city' > header.csv\nprintf '1,Pune\\n2,Agra\\n' | cat header.csv -",
             why='The dash means “stdin goes here”: header first, then the piped rows.')]),
     ('dev', [
        dict(situation='A Python program that reads its input from stdin (like coding-test websites do).', cmd="printf '12\\n30\\n8\\n' | python3 -c 'import sys; print(sum(int(x) for x in sys.stdin))'",
             why='Reading stdin means the same program works with typed input, files (<code>&lt; data.txt</code>) and pipes.')]),
     ('dba', [
        dict(situation='Load a SQL file into MySQL (Lesson: Advanced Java, JDBC module).', cmd='mysql -u riya -p shop < schema.sql',
             typical='Enter password:\n(no output: the statements ran)',
             why='mysql reads SQL statements from stdin, so <code>&lt; file</code> runs a whole script. The password prompt itself is written to the terminal, not read from the file.')]),
     ('sec', [
        dict(situation='Hash a secret without putting it on the command line, where <code>ps</code> and the history would show it.', cmd="secret='MyP@ss2026'\nprintf '%s' \"$secret\" | sha256sum",
             why='Arguments are visible to every user in <code>ps</code> and in /proc/PID/cmdline; stdin is not. Many tools (docker login --password-stdin, kubectl) accept secrets on stdin for this reason.')]),
     ('qa', [
        dict(situation='Test a program with fixed input every time.', cmd="printf '2\\n3\\n' > input.txt\npython3 -c 'a=int(input()); b=int(input()); print(a*b)' < input.txt",
             why='The same input file gives the same result in every run: repeatable tests.')]),
    ],
    anat=anatomy([('wc -l', 'cmd', 'command, no file name'), ('<', 'opt', 'feed stdin from …'), ('drinks.txt', 'arg', 'the file')], 'The shell opens drinks.txt and connects it to fd 0 before wc starts.')
) + cmdcard_u(['every normal result: lists, reports, data for the next command', 'output you want to save (> file) or process (| next)', 'checking whether output goes to a person or to a program'],
               ['error messages and warnings (use stderr)', 'progress bars and prompts (stderr, so they do not end up in files)'])(
    'stdout', 'stdout  (fd 1)', 'standard output',
    'The stream for normal results. It goes to the screen by default and is what <code>&gt;</code>, <code>&gt;&gt;</code> and <code>|</code> move. Programs can check whether it is a terminal and adjust their format.',
    'command            (results on screen)   ·   command > file   ·   command | next', 'safe',
    [('(default)', 'results on the terminal', 'reading them'),
     ('> file / >> file', 'into a file (overwrite / append)', 'saving (Lesson 5.2)'),
     ('| next', 'into the next command’s stdin', 'pipelines (5.3)'),
     ('1>', 'same as >, with the number written out', 'clarity next to 2>'),
     ('[ -t 1 ]', 'true if stdout is a terminal', 'colours only for people'),
     ('stdbuf -oL cmd', 'line-buffered stdout', 'live output into a pipe'),
     ('python3 -u', 'unbuffered Python output', 'logs that appear at once')],
    dict(cmd="echo 'Namaste'\nprintf '%s scored %d\\n' Riya 91\nls drinks.txt", setup="printf 'chai\\n' > drinks.txt", note='echo, printf and ls all write their results to fd 1.'),
    [('sys', [
        dict(situation='ls looks different when its output goes into a pipe.', cmd='touch a.txt b.txt c.txt\nls | cat',
             why='On a terminal ls prints columns; when stdout is a pipe or file it prints one name per line, which is easier for programs. (Our recorder is not a terminal, so plain <code>ls</code> would look the same here; the screens below show the real terminal.)')]),
     ('dev', [
        dict(situation='A script that colours its output only for people.', cmd="if [ -t 1 ]; then echo 'stdout is a terminal: use colours'; else echo 'stdout is a file or pipe: plain text'; fi",
             why='Here it prints “plain text” because the recorder captures the output. In your terminal it prints the first message. grep --color=auto and ls --color=auto use the same test.')]),
     ('data', [
        dict(situation='Save a report and also count its lines: stdout can be reused.', cmd="printf 'Pune 41\\nAgra 39\\n' > report.txt\ncat report.txt\nwc -l < report.txt",
             why='Results on stdout can go anywhere: screen, file, next command.')]),
     ('devops', [
        dict(situation='Live logs from Python inside a container appear late.', cmd="python3 -c 'import time\nfor i in range(2): print(\"tick\", i, flush=True)' | cat",
             why='When stdout is a pipe, Python buffers in blocks. <code>flush=True</code>, <code>python3 -u</code> or <code>PYTHONUNBUFFERED=1</code> (common in Dockerfiles) make lines appear immediately.')]),
     ('qa', [
        dict(situation='Capture a command’s output in a variable and compare it with the expected value.', cmd='got=$(echo "OK")\n[ "$got" = "OK" ] && echo "PASS: got $got"',
             why='<code>$( )</code> captures stdout (only stdout: errors are not captured). Lesson 5.4 covers it.')]),
    ]
) + mistake('ls notes.txt /nope > out.txt        (expecting “everything” in out.txt)', 'ls notes.txt /nope > out.txt 2> err.txt   ·   or  > all.txt 2>&1   (Lesson 5.2)',
            '<code>&gt;</code> is short for <code>1&gt;</code>. The error is on stream 2 and still goes to the screen.') + cmdcard_u(['every error and warning your own scripts print', 'progress, prompts and debug messages', 'keeping results clean so the next program can use them'],
               ['real results (they belong on stdout)', 'very important events only in stderr: also log them to a file (Lesson 18.1)'])(
    'stderr', 'stderr  (fd 2)', 'standard error',
    'The stream for error messages, warnings and diagnostics. It also goes to the screen, but it is <b>not</b> moved by <code>&gt;</code> or <code>|</code>, and it is unbuffered, so errors appear immediately.',
    "command 2> errors.txt   ·   echo 'message' >&2   ·   command 2>/dev/null", 'safe',
    [('(default)', 'errors on the terminal', 'you see them at once'),
     ('2> file', 'errors into a file', 'error logs (5.2)'),
     ('2>> file', 'errors appended', 'long-running error logs'),
     ('2>/dev/null', 'throw errors away', 'expected, harmless errors only'),
     ('2>&1', 'errors to wherever stdout goes', 'one combined log'),
     ('>&2', 'write your message to stderr', 'errors in scripts'),
     ('|&', 'pipe stdout and stderr together (bash)', 'grep through errors too')],
    dict(cmd='echo hello > notes.txt\nls notes.txt /nope > out.txt\necho "--- out.txt contains:"\ncat out.txt', note='The error reached the screen; out.txt has only the result. That answers the puzzle.', expect='any'),
    [('dev', [
        dict(situation='Your script reports a problem the right way.', cmd='f=config.yml\nif [ ! -e "$f" ]; then echo "error: $f not found" >&2; fi\necho "result line" > result.txt\ncat result.txt',
             why='<code>&gt;&amp;2</code> sends the message to stderr. Anyone running <code>./script &gt; result.txt</code> still sees the error, and the result file stays clean.'),
        dict(situation='Python: print a warning on stderr and a result on stdout.', cmd="python3 -c 'import sys; print(\"42\"); print(\"warning: slow disk\", file=sys.stderr)' > answer.txt\ncat answer.txt",
             why='Every language has both: Java System.err, Python sys.stderr, C fprintf(stderr, …).')]),
     ('sys', [
        dict(situation='Search the whole system without “Permission denied” flooding the screen.', cmd="find /etc -name 'host*' 2>/dev/null | head -n 3",
             why='Normal users cannot read some folders. The errors are expected, so 2&gt;/dev/null hides them while results still flow.')]),
     ('devops', [
        dict(situation='curl prints the download on stdout and the progress meter on stderr.', cmd='curl -o page.html https://example.com',
             typical='  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n100  1256  100  1256    0     0   4310      0 --:--:-- --:--:-- --:--:--  4316',
             why='Progress goes to stderr so that <code>curl URL &gt; file</code> or <code>curl URL | jq</code> get only the data. <code>-s</code> silences the meter; <code>-sS</code> keeps real errors.')]),
     ('qa', [
        dict(situation='Check that a test failure message really goes to stderr.', cmd='ls /nope 2> err.txt > out.txt\necho "stdout bytes: $(wc -c < out.txt), stderr: $(cat err.txt)"',
             why='Good command-line programs keep errors off stdout. Testing it prevents broken pipelines later.', expect='any')]),
     ('sec', [
        dict(situation='Audit scripts: keep error output for review instead of throwing it away.', cmd='ls /root 2> audit_errors.log; echo "exit $?"; cat audit_errors.log',
             why='Hiding errors with /dev/null can hide attacks or misconfiguration. Log them, then decide.', expect='any')]),
    ]
) + cmdcard_u(['seeing which files, pipes and sockets a process has open', 'debugging “where is this program writing?”', 'opening extra descriptors (3, 4 …) in advanced scripts'],
               ['normal day-to-day work (you rarely need fd numbers above 2)', 'other users’ processes without sudo (you will get Permission denied)'])(
    'procfd', '/proc/PID/fd', 'the file descriptor table',
    'Linux shows every process’s open file descriptors as links in <code>/proc/PID/fd</code>. <code>$$</code> is your shell, <code>$!</code> the last background job. <code>exec</code> can open or close descriptors in the current shell.',
    'ls -l /proc/PID/fd   ·   lsof -p PID   ·   exec 3> file … exec 3>&-', 'safe',
    [('ls -l /proc/$$/fd', 'your shell’s descriptors', 'where do 0 1 2 point?'),
     ('ls -l /proc/$!/fd', 'the last background job’s', 'debug a job'),
     ('lsof -p PID', 'the same with more detail', 'servers, sockets'),
     ('ls -l /dev/std*', 'the stdin/stdout/stderr links', 'understand /dev/stdout'),
     ('exec 3> file', 'open fd 3 for writing in this shell', 'a separate log channel'),
     ('cmd >&3', 'write to fd 3', 'log lines'),
     ('exec 3>&-', 'close fd 3', 'always clean up')],
    dict(cmd='ls -l /dev/stdin /dev/stdout /dev/stderr | sed -E "s/.*(\\/dev)/\\1/"', note='Three links into <code>/proc/self/fd</code>: “self” is whichever process looks.'),
    [('sys', [
        dict(situation='Where is a background job writing?', cmd='sleep 30 > job.log 2> job.err &\nls -l /proc/$!/fd | sed -E "s/.* ([0-9]+ ->)/\\1/" | grep -E "^[012] "\nkill $!',
             why='fd 1 and 2 point to the files the shell opened. Very useful when a service “writes logs somewhere”.')]),
     ('dev', [
        dict(situation='Write a separate log channel on fd 3 while stdout stays for results.', cmd='exec 3> debug.log\necho "result: 42"\necho "debug: step 1 done" >&3\nexec 3>&-\necho "--- debug.log:"; cat debug.log',
             why='Advanced scripts use extra descriptors for logs or locks (flock). Always close them with <code>3&gt;&amp;-</code>.')]),
     ('sec', [
        dict(situation='Which network connections and files does a process hold open?', cmd='sleep 30 &\nlsof -p $! 2>/dev/null | awk \'NR==1 || $4 ~ /^[0-9]/\' | awk \'{print $4, $5, $NF}\'\nkill $!',
             why='lsof shows descriptors (FD column 0u, 1w …), their type and target. Incident responders use it to find unexpected sockets or deleted files a process still holds.')]),
    ]
) + undo('Streams cannot be “broken”, but a few things surprise beginners.', [
    ('A command waits and nothing happens:', 'it is reading stdin. Press <kbd>Ctrl+D</kbd> to end the input or <kbd>Ctrl+C</kbd> to cancel.'),
    ('You closed stdout or stderr by mistake (exec 1>&- or exec 2>&-):', 'the shell can no longer print. Type <code>exec 1&gt;/dev/tty 2&gt;/dev/tty</code>, or just close the terminal and open a new one.'),
    ('The terminal shows garbage after cat on a binary file:', 'type <code>reset</code> (blind if needed) and press Enter.'),
    ('2>/dev/null hid an important error:', 'run the command again without it. Hide only errors you understand.'),
]) + errors('Stream-related errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='wc -l < missing.txt', meaning='The shell could not open the file for stdin, so wc never even started.', fix='Check the name with <code>ls</code>. The message comes from bash, not from wc.'),
    dict(cmd='echo hi >&4', meaning='There is no file descriptor 4 open in this shell.', fix='Open it first (<code>exec 4&gt; file</code>) or use 1 or 2.'),
    dict(cmd='echo hi > /dev/full', meaning='/dev/full is a test device that is always “full”: writing to stdout failed. Real disks give the same error when they fill up.', fix='Free disk space (<code>df -h</code>, Lesson 15.4). Good scripts check the exit status of writes.'),
    dict(cmd='ls /nope', meaning='A normal error message, printed on stderr; exit status 2 means a serious problem for ls.', fix='Check the path. Use 2&gt; to log such errors.'),
]) + qc('In a script, how do you print “error: disk full” so that it is not mixed into the results?', '<code>echo "error: disk full" &gt;&amp;2</code>') + '''
</section>
'''

# real terminal screens
SCREENS = screens_block('Real terminal screens: where 0, 1 and 2 point, and Ctrl+D', 'Riya opens a real terminal, looks at her shell’s descriptors, repeats the puzzle, and types input for <code>wc -l</code>.',
    RC, SH, [
    ('ls -l /proc/$$/fd  Enter', "'ls -l /proc/$$/fd' Enter", ': 0, 1 and 2 all point to the terminal device <code>/dev/pts/0</code> (255 is bash’s own copy). Ctrl+L clears the screen before each next command.'),
    ('ls notes.txt /nope > out.txt  Enter', "C-l 'ls notes.txt /nope > out.txt' Enter", ': only the error reaches the screen.'),
    ('cat out.txt  Enter', "'cat out.txt' Enter", ': the result went into the file.'),
    ('wc -l  Enter', "C-l 'wc -l' Enter", ': no prompt comes back. wc is reading the keyboard.'),
    ('chai  Enter  coffee  Enter', "'chai' Enter 'coffee' Enter", ': each line you type goes to wc’s stdin.'),
    ('Ctrl+D', 'C-d', ': end of input. wc prints 2 and the prompt returns.'),
], 72, 16, hid='screens', what='bash')

# ---------------------------------------------------------------- 5. animations
def fdbox(hl, note, tone='blue', targets=('/dev/pts/0', '/dev/pts/0', '/dev/pts/0')):
    o = label_box(120, 14, 120, 120, ['process', 'ls', 'fd table'], 'card', 9)
    for k, (nm, tn) in enumerate([('0 stdin', 'blue'), ('1 stdout', 'green'), ('2 stderr', 'red')]):
        y = 22 + k * 38
        o += label_box(250, y, 96, 28, [nm, targets[k]], tn if k in hl else 'card', 7.6)
    return o + t(180, 168, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ ls notes.txt /nope', ("ls: cannot access '/nope': No such", 'err'), ('notes.txt', 'acc')], title='riya@laptop', size=7.8) + cap('Both streams appear on the screen.', '', 'card', y=150, h=34),
       term(14, 16, 332, 116, ['$ ls notes.txt /nope > out.txt', ("ls: cannot access '/nope': No such", 'err')], title='riya@laptop', size=7.8) + cap('> moves stdout: only the error is left.', '', 'blue', y=150, h=34),
       term(14, 16, 332, 116, ['$ ls notes.txt /nope 2> err.txt', ('notes.txt', 'acc')], title='riya@laptop', size=7.8) + cap('2> moves stderr: only the result is left.', '', 'blue', y=150, h=34),
       term(14, 16, 332, 116, ['$ wc -l', 'chai', 'coffee', ('^D', 'dim'), ('2', 'acc')], title='riya@laptop', size=7.8) + cap('stdin: the keyboard until Ctrl+D.', '', 'green', y=150, h=34)]
behind = [fdbox([1, 2], 'fd 1 and fd 2 both lead to the terminal.', 'violet'),
          fdbox([1], 'The shell points fd 1 at out.txt before ls starts.', 'green', ('/dev/pts/0', 'out.txt', '/dev/pts/0')),
          fdbox([2], 'With 2> only fd 2 is changed.', 'red', ('/dev/pts/0', '/dev/pts/0', 'err.txt')),
          fdbox([0], 'wc reads fd 0 (the terminal) until end-of-file.', 'blue')]
two = anim_two('One program, three pipes', 'The fd table behind the screen',
               'A terminal: ls with a good and a bad path prints a result and an error; with > only the error shows; with 2> only the result; wc -l reads two typed lines.',
               'A process box with fd 0, 1 and 2 pointing to /dev/pts/0, then fd 1 to out.txt, then fd 2 to err.txt.', see, behind,
               ['ls writes the result to stdout and the error to stderr; both show on screen.',
                'With <code>&gt; out.txt</code> the result disappears into the file.',
                'With <code>2&gt; err.txt</code> the error disappears into its file.',
                'wc with no file reads the keyboard until Ctrl+D.'],
               ['Every process starts with descriptors 0, 1, 2, copied from the shell.',
                'Redirection only changes where a descriptor points; ls does not know.',
                'Each stream is moved separately.',
                'Ctrl+D tells the terminal driver to deliver end-of-file to fd 0.'])

c1 = term(14, 14, 332, 100, ['$ ./nightly.sh > nightly.log', ("rsync: link_stat '/data/old' failed", 'err')], title='cron@server', size=7.6) + cap('In cron there is no screen at all.', '', 'card', y=150, h=34)
c2 = (label_box(20, 20, 140, 60, ['cron', 'collects stderr'], 'amber', 9) + label_box(200, 20, 140, 60, ['email to root', 'from: Cron daemon'], 'red', 8.6) + arrow(162, 50, 196, 50) + cap('Unredirected output is mailed (or lost).', '', 'amber', y=150, h=34))
c3 = term(14, 14, 332, 100, ['0 2 * * * ./nightly.sh >> /var/log/nightly.log 2>&1'], title='crontab -e', size=7.2) + cap('Fix: send both streams to a log (Lesson 5.2).', '', 'green', y=150, h=34)
c4 = term(14, 14, 332, 100, ['$ grep -c failed /var/log/nightly.log', ('1', 'acc')], title='riya@server', size=7.6) + cap('Now the morning check finds the error.', '', 'green', y=150, h=34)
s1 = anim_one('Real-time scenario', 'The cron job whose errors vanished',
              'A nightly job runs with no terminal. Where does its stderr go? Screens are typical.',
              'stderr without a terminal', 'A cron job prints an rsync error; cron mails it to root; the fix appends both streams to a log; grep finds the failure in the morning.', [c1, c2, c3, c4],
              ['The job redirects stdout, but the error is on stderr.',
               'With no terminal, cron collects anything left on the streams and emails it, often to a mailbox nobody reads.',
               'Redirect both streams into a log file.',
               'Now errors are where people look.'], hid='scenario-cron')

dx = dissect('Layer by layer: ls notes.txt /nope > out.txt',
    'What happens from your key press to the bytes on screen and in the file. Each layer has a real command and output from our build machine.', [
    dict(key='shell', name='The shell', sub='reads the line',
         why='The shell, not ls, understands > out.txt.',
         how='It removes “> out.txt” from the arguments and opens the file.',
         impl='bash parses redirections before running the command.', used='Every command line.',
         cmd="echo 'ls gets only these arguments:'; set -- notes.txt /nope; printf '[%s] ' \"$@\"; echo"),
    dict(key='fork', name='Child process', sub='inherits fd 0 1 2',
         why='Each command runs as a new process.',
         how='fork() copies the shell’s fd table.',
         impl='The child is a copy of bash until exec.', used='All programs.',
         cmd='echo "shell PID $$"; bash -c \'echo "child PID $$, parent $PPID"\''),
    dict(key='dup', name='dup2()', sub='fd 1 → out.txt',
         why='Point stdout at the file.',
         how='open("out.txt") then dup2(fd, 1) in the child.',
         impl='Happens before exec, so ls never knows.', used='>, >>, 2>, <.',
         cmd='sleep 2 > out.txt &\nls -l /proc/$!/fd/1 | sed -E "s/.*-> //"; kill $!'),
    dict(key='prog', name='ls runs', sub='write(1) and write(2)',
         why='ls writes results to 1 and errors to 2.',
         how='It never opens the terminal itself.',
         impl='C: fputs to stdout / stderr.', used='Every Unix program.',
         cmd='echo hello > notes.txt; ls notes.txt /nope 2>/dev/null; echo "(only stdout shown)"'),
    dict(key='dev', name='Devices and files', sub='/dev/pts/0 · out.txt',
         why='Bytes reach the terminal or the file.',
         how='The kernel delivers write() to the right driver or file system.',
         impl='tty driver; ext4.', used='Screen, files, pipes.',
         cmd='echo hello > notes.txt; ls notes.txt /nope > out.txt 2>/dev/null; cat out.txt'),
], hint='From the shell to the device. Click a layer.')

HOOD = hood('Under the hood: two streams, two numbers', 'Run <code>ls</code> with one good and one bad file under <code>strace</code>, which shows every <code>write()</code> with its file descriptor as the first number.',
    'ls notes.txt /nope > out.txt', setup='echo hello > notes.txt', show='^write',
    explain='<p>The error goes to <b>write(2, …)</b> in four small pieces, immediately; the result goes to <b>write(1, …)</b> at the very end, because stdout to a file is buffered and only flushed when ls exits. That is why in a combined log file errors can appear before output that was produced earlier.</p>')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Three pipes out of one program</h2>
  <p>Left: what Riya sees. Right: where each file descriptor points.</p>
''' + two + s1 + dx + HOOD + qc('A program writes “progress 50%” to stderr and the data to stdout. You run <code>prog &gt; data.txt</code>. What do you see on screen?', 'Only “progress 50%”. The data is in data.txt; the progress message was on stream 2.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Standard streams at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ cron job', 'prompt'), ('stderr → mail', 'err')], title='ops', size=6.4, step=12),
              '1. Scheduled jobs', 'With no terminal, unredirected output of cron jobs is mailed or lost; admins always redirect both streams to logs.', ['Job', '*stdout + stderr', 'log file']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['docker logs', '1 + 2'], 'blue', 8.6), '2. Containers and services',
    'Docker and systemd collect a service’s stdout and stderr as its log (docker logs, journalctl). The 12-factor rule: apps write logs to stdout.', ['App', '*stdout/stderr', 'log system']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ curl | jq', 'prompt'), ('data only', 'acc')], title='dev', size=6.4, step=12),
    '3. Clean pipelines', 'Tools print progress on stderr so that their stdout can be piped into the next program without garbage.', ['curl', '*stdout = data', 'jq']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['CI test', 'stderr'], 'red', 8.6), '4. CI and test reports',
    'CI systems show stderr in red and keep stdout as the build output; test runners compare stdout with expected results.', ['Test', '*1 vs 2', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ps / argv', 'stdin'], 'violet', 8.6), '5. Secrets',
    'Passwords and tokens are passed on stdin (--password-stdin) because command-line arguments are visible to other users.', ['Secret', '*stdin', 'tool']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Count lines you paste', scenario='How many names are in this list? (piped here; in your terminal: type and Ctrl+D)',
         cmd="printf 'Asha\\nRavi\\nMeena\\n' | wc -l", explain='wc reads stdin.'),
    dict(level='b', title='Keep only the errors', scenario='Run a command, throw away results, see only problems.',
         cmd='echo hi > a.txt; ls a.txt /nope /tmp/zz > /dev/null', explain='stdout to /dev/null; stderr still shows. (/tmp/zz is missing too.)', expect='any'),
    dict(level='i', title='Error message from a function', scenario='A reusable die() helper for scripts.',
         cmd='die() { echo "error: $*" >&2; return 1; }\ndie "config missing"; echo "exit status $?"', explain='Message on stderr, status 1 for the caller.'),
    dict(level='i', title='Header + stream + footer', scenario='Wrap piped rows with a header and a footer file.',
         cmd="echo 'BEGIN' > h.txt; echo 'END' > f.txt\nprintf 'row1\\nrow2\\n' | cat h.txt - f.txt", explain='- puts stdin between the files.'),
    dict(level='a', title='Which streams are terminals?', scenario='Debug a script that behaves differently in cron.',
         cmd='for fd in 0 1 2; do if [ -t $fd ]; then echo "fd $fd: terminal"; else echo "fd $fd: not a terminal"; fi; done',
         explain='In our recorder none is a terminal; in your terminal all three are; in cron none are.'),
], extra=build_up('a script with clean output and clean errors', 'Riya writes a tiny checker that prints results on stdout and problems on stderr, then proves it.',
    'echo ok > app.conf', [
    ('for f in app.conf db.conf; do if [ -e "$f" ]; then echo "$f ok"; fi; done', '1. Results only for files that exist.'),
    ('for f in app.conf db.conf; do if [ -e "$f" ]; then echo "$f ok"; else echo "missing: $f" >&2; fi; done', '2. Missing files reported on stderr.'),
    ('for f in app.conf db.conf; do if [ -e "$f" ]; then echo "$f ok"; else echo "missing: $f" >&2; fi; done > results.txt; echo "--- results.txt:"; cat results.txt', '3. Results into a file: the error still shows.'),
    ('for f in app.conf db.conf; do if [ -e "$f" ]; then echo "$f ok"; else echo "missing: $f" >&2; fi; done > results.txt 2> problems.txt; echo "results: $(cat results.txt) | problems: $(cat problems.txt)"', '4. Each stream in its own file.'),
])) + which('Choosing the right stream.', [
    ('Normal results', 'stdout (echo, printf)', 'Can be saved and piped.', 'Errors mixed into results.'),
    ('Errors, warnings', 'stderr (>&2)', 'Always visible.', 'echo "error" on stdout.'),
    ('Input for a tool', 'a file name, < file, |', 'No waiting.', 'Typing when a file exists.'),
    ('One value', '<<< "$var"', 'Short.', 'echo "$var" | … in loops (slower).'),
    ('No input wanted', '< /dev/null', 'Never hangs.', 'Jobs that wait for a keyboard.'),
    ('Secrets', 'stdin', 'Not in ps.', 'Passwords as arguments.'),
    ('Live output in a pipe', 'stdbuf -oL / python3 -u', 'Lines appear at once.', 'Waiting for the buffer.'),
]) + keys('Shortcuts and handy forms.', [
    ('Ctrl + D', 'end of input (EOF) at the start of a line', 'wc -l → lines → Ctrl+D'),
    ('Ctrl + C', 'cancel the running command', 'a cat that waits'),
    ('$$', 'your shell’s PID', 'ls -l /proc/$$/fd'),
    ('$!', 'PID of the last background job', 'ls -l /proc/$!/fd'),
    ('>&2', 'send this echo to stderr', 'echo "error" >&2'),
    ('-', 'stdin as a file name', 'cat head.txt - tail.txt'),
    ('tty', 'which terminal am I on?', 'tty → /dev/pts/0'),
    ('reset', 'repair a garbled terminal', 'after cat on a binary'),
]) + scriptit('check-files.sh', 'Riya’s checker as a script: results on stdout, problems on stderr, and a non-zero exit status if anything was missing (Lesson 5.4).',
'''#!/bin/bash
# usage: check-files.sh FILE...
echo ok > app.conf                        # demo file
set -- app.conf db.conf                   # demo arguments
missing=0
for f in "$@"; do
  if [ -e "$f" ]; then
    echo "OK      $f"
  else
    echo "MISSING $f" >&2
    missing=$((missing + 1))
  fi
done
echo "$missing missing" >&2
[ "$missing" -eq 0 ]''',
'<p>Try <code>./check-files.sh *.conf &gt; ok.txt</code>: ok.txt gets the OK lines, the screen shows the problems, and <code>echo $?</code> prints 1.</p>', expect='any') + puzzle_answer('The <b>error</b> line appears on the screen: <code>ls: cannot access \'/nope\': No such file or directory</code>. out.txt contains only <code>notes.txt</code>. <code>&gt;</code> moves stream 1 (stdout); the error travels on stream 2 (stderr), which still points to the terminal.') + qc('Why is it a good idea for tools to print progress bars on stderr?', 'So that stdout contains only data, which can be redirected to a file or piped into another program without the progress text mixed in.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../03-files-and-directories/01-creating-files-and-folders-touch-mkdir-and-rmdir/">Lesson 3.1</a> (echo &gt; file) and <a href="../../03-files-and-directories/05-viewing-files-cat-tac-less-more-head-tail-f-nl/">3.5</a> (cat, wc).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards[:cards.rfind('</section>')] + SCREENS + '</section>\n' + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
