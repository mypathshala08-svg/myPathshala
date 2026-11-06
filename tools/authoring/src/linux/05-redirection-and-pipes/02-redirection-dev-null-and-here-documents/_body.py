import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# Our build machine has no database server. A 6-line Python program reads SQL from stdin and runs it on SQLite,
# so the DBA examples show real redirections with real results. The file name says what it is.
MINI = r"""cat > minisql.py << 'PY'
import sqlite3, sys
db = sqlite3.connect(sys.argv[1])
for stmt in sys.stdin.read().split(';'):
    if stmt.strip():
        for row in db.execute(stmt): print(*row, sep=' | ')
db.commit()
PY"""

HOOK = hook('Riya’s nightly job writes 2,000 lines of output, a few of which are errors. She wants all of it saved in one log, kept from night to night, with yesterday’s lines not overwritten. She also needs to feed a 15-line SQL script to the database without creating a temporary file, and to silence one harmless warning. Three small operators do all of that: <code>&gt;&gt;</code>, <code>2&gt;&amp;1</code> and <code>&lt;&lt; EOF</code>. One wrong character (<code>&gt;</code> instead of <code>&gt;&gt;</code>) deletes the whole log.',
    ['save command output to files with <code>&gt;</code> (overwrite) and <code>&gt;&gt;</code> (append), and protect files with <code>noclobber</code>',
     'feed files to commands with <code>&lt;</code>, and capture errors with <code>2&gt;</code> and <code>2&gt;&gt;</code>',
     'combine both streams with <code>2&gt;&amp;1</code> or <code>&amp;&gt;</code>, and explain why the order matters',
     'throw output away with <code>/dev/null</code>, and write multi-line input with here-documents (<code>&lt;&lt; EOF</code>) and here-strings (<code>&lt;&lt;&lt;</code>)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the log that vanished'),
    ('decide', 'Which operator when?', 2, 'the quick chart'),
    ('definition', 'What redirection is', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each operator, by field', 18, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'why 2>&1 order matters'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which operator? (decide in 5 seconds)', [
    ('Save output, replace the file', 'cmd > file', 'creates or empties the file first'),
    ('Add output to the end of a file', 'cmd >> file', 'logs, reports that grow'),
    ('Give a file to a command as input', 'cmd < file', 'mysql db < dump.sql'),
    ('Save only the errors', 'cmd 2> errors.txt', '2>> to append'),
    ('Results and errors in one file', 'cmd > all.log 2>&1', 'or cmd &> all.log (bash); order matters'),
    ('Throw output away', 'cmd > /dev/null', 'errors too: > /dev/null 2>&1'),
    ('Several lines of input, typed in the script', 'cmd << EOF … EOF', "<< 'EOF' = no $variables expanded"),
    ('One line or one variable as input', "cmd <<< \"$text\"", 'here-string (bash)'),
    ('Write a root-owned file', 'echo x | sudo tee /etc/file', 'sudo echo x > file does NOT work'),
    ('Never overwrite by accident', 'set -o noclobber', 'then >| to force'),
])

cmap = concept_map(
    [('5.1', 'Standard streams', 'stdin 0, stdout 1, stderr 2'), ('3.1', 'Creating files', 'echo > and cat > file'), ('3.5', 'Viewing files', 'cat, head, tail on the results')],
    ['> and >>: save or append stdout; noclobber and >|', '<: a file as stdin', '2> and 2>>: errors to a file', '2>&1, &> and &>>: both streams together, and why the order matters', '/dev/null; here-documents << EOF, <<- and quoted EOF; here-strings <<<'],
    [('5.3', 'Pipes and tee', 'send output to a command instead of a file'), ('5.4', 'Chaining and exit codes', 'react to success and failure'), ('17.4', 'cron', 'jobs that log with >> … 2>&1'), ('12.5', 'Shell scripts', 'here-docs for config and SQL')],
    'Redirection is how scripts save results, keep logs and feed data. Every admin, developer and DBA types these operators daily.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ['$ ./nightly.sh > nightly.log', ('# Monday: 2000 lines', 'dim'), '$ ./nightly.sh > nightly.log', ('# Tuesday: Monday is GONE', 'err'), '$ ./nightly.sh >> nightly.log 2>&1', ('# appended, errors included', 'acc'), '$ wc -l nightly.log', ('4000 nightly.log', 'acc')], title='riya@server: ~', size=7.2, step=15)
      + t(352, 36, 'One character decides:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• > replaces the file', '• >> adds to the end', '• 2>&1 brings errors along', '• /dev/null throws away', '• << EOF types input inline'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The log that vanished every night</h2>
  <div class="story">
''' + puzzle('Which of these two lines puts <b>both</b> the result and the error into all.txt?<br><code>ls notes.txt /nope 2&gt;&amp;1 &gt; all.txt</code><br><code>ls notes.txt /nope &gt; all.txt 2&gt;&amp;1</code><br>They contain the same words in a different order. Do they do the same thing?') + '''
    <p class="narration">On Wednesday the manager asks for Monday’s log. Riya opens nightly.log: only last night is there. The crontab says <code>./nightly.sh &gt; nightly.log</code>.</p>
''' + scene('A terminal: each night > nightly.log replaces the file and Monday’s lines are gone; with >> nightly.log 2>&1 the log grows to 4000 lines with errors included.', sc,
            'One <tspan font-weight="700" class="s-acc">&gt;</tspan> empties the file before the command even starts.') + '''
A> <code>&gt;</code> means “replace”. The shell empties nightly.log first, then the job writes into it. Every night starts from zero.
R> And <code>&gt;&gt;</code>?
K> Append: new lines go at the end. Add <code>2&gt;&amp;1</code> and the errors from Lesson 5.1 go into the same log, in order.
A> Today: every redirection operator: <code>&gt;</code>, <code>&gt;&gt;</code>, <code>&lt;</code>, <code>2&gt;</code>, <code>2&gt;&amp;1</code>, <code>&amp;&gt;</code>, <code>/dev/null</code>, here-documents and here-strings, each explained and then used by admins, DBAs, developers, DevOps, security and QA.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="A water tank with taps: one tap fills a new bucket (overwrite), one tops up a bucket (append), a drain (dev null), and a funnel pouring into the tank (input).">'
       + label_box(250, 30, 140, 100, ['the command', '(a water tank)', 'with 3 taps'], 'card', 9)
       + label_box(20, 30, 160, 44, ['< file', 'funnel: pour a file in'], 'blue', 8.6)
       + label_box(460, 14, 165, 40, ['> file', 'empty bucket, then fill'], 'red', 8.4)
       + label_box(460, 62, 165, 40, ['>> file', 'top up the bucket'], 'green', 8.4)
       + label_box(460, 110, 165, 40, ['> /dev/null', 'straight down the drain'], 'card', 8.4)
       + arrow(182, 52, 248, 70) + arrow(392, 60, 458, 34) + arrow(392, 80, 458, 82) + arrow(392, 110, 458, 130)
       + t(320, 182, 'You choose the bucket before opening the tap:', 9.6, 'ink2')
       + t(320, 204, '> throws away what was in it; >> keeps it.', 9.6, 'acc', bold=True)
       + '<text x="632" y="214" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Redirection at four depths', [
    ('v', 'No jargon: buckets and taps', '      <p>Think of a command as a water tank with taps.</p>' + pic + '''
      <ul>
        <li><code>&gt;</code> puts an <b>empty</b> bucket under the tap: whatever was in it before is poured away.</li>
        <li><code>&gt;&gt;</code> puts the same bucket back and <b>tops it up</b>.</li>
        <li><code>&lt;</code> is a funnel: you pour a file into the tank.</li>
        <li><code>/dev/null</code> is the drain: water disappears and nothing fills up.</li>
      </ul>'''),
    ('b', 'The operators you will type every day', '''      <ul>
        <li><code>date &gt; today.txt</code> saves the output (replacing the file); <code>date &gt;&gt; log.txt</code> adds a line.</li>
        <li><code>wc -l &lt; names.txt</code> feeds a file as input.</li>
        <li><code>ls /nope 2&gt; err.txt</code> saves only the error; <code>2&gt;&gt;</code> appends errors.</li>
        <li><code>cmd &gt; all.log 2&gt;&amp;1</code> saves results <b>and</b> errors (bash also has <code>cmd &amp;&gt; all.log</code>).</li>
        <li><code>cmd &gt; /dev/null 2&gt;&amp;1</code> runs quietly; <code>2&gt;/dev/null</code> hides only errors.</li>
      </ul>'''),
    ('i', 'Order, quoting and here-documents', '''      <ul>
        <li>Redirections are read <b>left to right</b>. <code>2&gt;&amp;1</code> means “make 2 point where 1 points <b>now</b>”. So <code>&gt; f 2&gt;&amp;1</code> sends both to f, but <code>2&gt;&amp;1 &gt; f</code> sends errors to the screen (where 1 pointed at that moment).</li>
        <li>The shell creates or empties the target file <b>before</b> the command runs, even if the command then fails. So <code>sort data.txt &gt; data.txt</code> empties data.txt before sort reads it.</li>
        <li>A here-document <code>&lt;&lt; EOF</code> feeds the following lines until a line with only <code>EOF</code>. <code>$variables</code> and <code>$(commands)</code> are expanded; with <code>&lt;&lt; 'EOF'</code> they are kept literally; <code>&lt;&lt;-</code> removes leading tabs.</li>
        <li><code>set -o noclobber</code> makes <code>&gt;</code> refuse to overwrite existing files; <code>&gt;|</code> overrides it on purpose.</li>
        <li><code>sudo cmd &gt; /etc/file</code> fails: the redirection is done by <b>your</b> shell, not by sudo. Use <code>cmd | sudo tee /etc/file</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: open(), dup2() and more descriptors', '''      <ul>
        <li><code>&gt; f</code> = <code>open("f", O_WRONLY|O_CREAT|O_TRUNC)</code> + <code>dup2(fd, 1)</code>; <code>&gt;&gt;</code> uses <code>O_APPEND</code> instead of <code>O_TRUNC</code>, so every write goes to the end, even with several writers.</li>
        <li><code>2&gt;&amp;1</code> is <code>dup2(1, 2)</code>: copy descriptor 1 into 2. General form <code>N&gt;&amp;M</code>; <code>N&lt;&gt;file</code> opens for reading and writing; <code>N&gt;&amp;-</code> closes.</li>
        <li>Here-documents are stored by bash in a temporary file or a pipe, then given to the command as stdin.</li>
        <li><b>Process substitution</b> <code>&lt;(cmd)</code> turns a command’s output into a file name (<code>/dev/fd/63</code>): <code>diff &lt;(sort a) &lt;(sort b)</code>. Glossary: {ps}.</li>
        <li><code>&amp;&gt;</code>, <code>&amp;&gt;&gt;</code>, <code>&lt;&lt;&lt;</code> and <code>|&amp;</code> are bash extensions; in POSIX <code>sh</code> (dash on Ubuntu, used by <code>/bin/sh</code> scripts) write <code>&gt; f 2&gt;&amp;1</code> instead.</li>
      </ul>'''.replace('{ps}', gl('process-substitution', 'process substitution'))),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Redirection, /dev/null and here-documents</h2>
''' + def_block(
    '<b>Redirection</b> is a shell feature that changes where a command’s standard streams point before the command runs: to a file, from a file, or to another file descriptor. <code>/dev/null</code> is a special device file that discards everything written to it and returns end-of-file when read. A <b>here-document</b> supplies several lines written inside the script as a command’s standard input; a <b>here-string</b> supplies a single string.',
    'Tell the shell where input comes from and where output and errors go, before the command starts.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Redirection', f'Changing where stdin, stdout or stderr point. {gl("redirection-2", "Glossary →")}'),
    ('Overwrite / truncate', '<code>&gt;</code> empties the file to 0 bytes, then writes.'),
    ('Append', '<code>&gt;&gt;</code> writes at the end, keeping old content.'),
    ('/dev/null', f'The “black hole” device. {gl("dev-null", "Glossary →")}'),
    ('Here-document', f'<code>&lt;&lt; EOF</code> … <code>EOF</code>: lines inside the script as input. {gl("here-document-eof", "Glossary →")}'),
    ('Here-string', '<code>&lt;&lt;&lt; "text"</code>: one string as input (bash).'),
    ('noclobber', 'A shell option that stops <code>&gt;</code> overwriting files.'),
    ('Process substitution', f'<code>&lt;(cmd)</code>: output as a file name. {gl("process-substitution", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('>  >>', 'arrow into a file', 'The data flows the way the arrow points.'),
    ('<', 'arrow out of a file', 'The file flows into the command.'),
    ('2>&1', '“2 to wherever 1 goes”', 'The &amp; means “a descriptor, not a file named 1”.'),
    ('/dev/null', 'null device', 'From early Unix; nicknamed “the bit bucket”.'),
    ('<< EOF', 'here-document', 'The input is “here”, in the script. EOF is just a habit: any word works.'),
    ('<<<', 'here-string', 'Borrowed by bash from rc and zsh.'),
    ('clobber', 'to hit hard, destroy', 'noclobber = “don’t destroy my files”.'),
    ('tee', 'a T-shaped pipe fitting', 'One input, two outputs (Lesson 5.3).'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Replace', '<code>cmd &gt; file</code>'),
    ('Add', '<code>cmd &gt;&gt; file</code>'),
    ('Input from file', '<code>cmd &lt; file</code>'),
    ('Both streams', '<code>cmd &gt; file 2&gt;&amp;1</code>  ·  <code>cmd &amp;&gt; file</code>'),
    ('Silence', '<code>cmd &gt; /dev/null 2&gt;&amp;1</code>'),
    ('Empty a file', '<code>&gt; file</code>  ·  <code>truncate -s 0 file</code>'),
]) + '\n' + lv + didyou('<code>&gt; file</code> with no command at all is a complete command: it creates an empty file, or empties an existing one. Admins use <code>: &gt; app.log</code> to empty a big log that a program still has open, because deleting it with rm would not free the disk space until the program closes it (Lesson 3.3).') + '''
EXAM> “What is the difference between &gt; and &gt;&gt;, and how do you redirect both stdout and stderr to a file?” → &gt; truncates (overwrites), &gt;&gt; appends; cmd &gt; file 2&gt;&amp;1 (or &amp;&gt; file in bash); 2&gt;&amp;1 must come after &gt; file.
''' + qc('What does <code>echo hi &gt; a.txt</code> do if a.txt already has 100 lines?', 'It empties a.txt first, so afterwards a.txt contains only “hi”. Use <code>&gt;&gt;</code> to keep the 100 lines.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Every redirection operator in one table</h2>
''' + table(['Operator', 'Stream', 'What it does', 'File exists?', 'Example'], [
    ['<code>&gt; f</code> (= <code>1&gt; f</code>)', 'stdout', 'write to f', '<b>emptied</b> first', '<code>ls &gt; list.txt</code>'],
    ['<code>&gt;&gt; f</code>', 'stdout', 'append to f', 'kept', '<code>date &gt;&gt; log.txt</code>'],
    ['<code>&gt;| f</code>', 'stdout', 'overwrite even with noclobber', 'emptied', '<code>ls &gt;| list.txt</code>'],
    ['<code>&lt; f</code>', 'stdin', 'read from f', 'must exist', '<code>wc -l &lt; list.txt</code>'],
    ['<code>2&gt; f</code> / <code>2&gt;&gt; f</code>', 'stderr', 'errors to f / appended', 'emptied / kept', '<code>find / 2&gt; err.txt</code>'],
    ['<code>2&gt;&amp;1</code>', 'stderr', 'errors to wherever stdout points now', '-', '<code>cmd &gt; all.log 2&gt;&amp;1</code>'],
    ['<code>1&gt;&amp;2</code> / <code>&gt;&amp;2</code>', 'stdout', 'output to stderr', '-', '<code>echo "err" &gt;&amp;2</code>'],
    ['<code>&amp;&gt; f</code> / <code>&amp;&gt;&gt; f</code>', 'both', 'both streams to f / appended (bash)', 'emptied / kept', '<code>cmd &amp;&gt;&gt; all.log</code>'],
    ['<code>&gt; /dev/null</code>', 'stdout', 'discard', '-', '<code>cmd &gt; /dev/null 2&gt;&amp;1</code>'],
    ['<code>&lt;&lt; EOF</code>', 'stdin', 'lines until EOF, $vars expanded', '-', '<code>cat &lt;&lt; EOF</code>'],
    ["<code>&lt;&lt; 'EOF'</code>", 'stdin', 'lines kept literally', '-', 'scripts that write scripts'],
    ['<code>&lt;&lt;- EOF</code>', 'stdin', 'leading <b>tabs</b> removed', '-', 'indented code'],
    ['<code>&lt;&lt;&lt; "s"</code>', 'stdin', 'one string (bash)', '-', '<code>bc &lt;&lt;&lt; "2^10"</code>'],
    ['<code>&lt;(cmd)</code>', '-', 'command output as a file name (bash)', '-', '<code>diff &lt;(ls a) &lt;(ls b)</code>'],
], minw=720) + mistake('sort data.txt > data.txt', 'sort data.txt > sorted.txt && mv sorted.txt data.txt   ·   or  sort -o data.txt data.txt',
                       'The shell empties data.txt <b>before</b> sort starts, so sort reads an empty file and data.txt ends up empty (a real run gave 0 bytes). The same happens with grep, sed, cut and any command reading and writing the same file.') + qc('Which operator would you use for a log that must keep growing?', '<code>&gt;&gt;</code> (append), usually with <code>2&gt;&amp;1</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each operator explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on Ubuntu 24.04 as a normal user (riya, no sudo rights). Our build machine has no database server, so DBA examples use <code>minisql.py</code>, a 6-line Python program that reads SQL on stdin and runs it on SQLite: the redirections are exactly the ones you use with <code>mysql</code> or <code>psql</code>.</p>
''' + cmdcard_u(['saving a command’s output as a new file or a fresh copy', 'reports regenerated every run', 'creating or emptying a file (<code>&gt; file</code>)'],
               ['logs and anything you must keep (use <code>&gt;&gt;</code>)', 'the same file the command is reading', 'files owned by root (use <code>sudo tee</code>)'])(
    'gt', '>', 'redirect stdout, overwriting',
    'Sends stdout into a file. If the file exists it is <b>emptied first</b>; if not, it is created. <code>&gt;</code> is short for <code>1&gt;</code>.',
    'command > file   ·   command 1> file   ·   > file (empty it)   ·   command >| file', 'danger',
    [('cmd > file', 'create or overwrite file with the output', 'reports, fresh copies'),
     ('cmd 1> file', 'the same, with the stream number written', 'next to 2> for clarity'),
     ('> file  /  : > file', 'empty (or create) a file', 'reset a log in place'),
     ('set -o noclobber', 'make > refuse to overwrite', 'interactive safety'),
     ('cmd >| file', 'overwrite even with noclobber', 'when you really mean it'),
     ('cmd > "$dir/$name"', 'quoted target path', 'names with spaces'),
     ('{ cmd1; cmd2; } > file', 'one redirection for a group', 'several commands, one file')],
    dict(cmd="echo 'first' > notes.txt\necho 'second' > notes.txt\ncat notes.txt", note='The second <code>&gt;</code> replaced the file: only “second” is left.'),
    [('sys', [
        dict(situation='Save the list of installed shells as a fresh report.', cmd='cat /etc/shells > shells_report.txt\nwc -l shells_report.txt',
             why='> gives a clean file every time the report runs.'),
        dict(situation='Empty a huge log file that a service still writes to, without deleting it.', cmd="seq 1 100000 > app.log; ls -l app.log | awk '{print $5, $9}'\n: > app.log\nls -l app.log | awk '{print $5, $9}'",
             why='rm would remove the name but the service keeps the old file open, so the disk space stays used. Emptying keeps the same file.')]),
     ('dev', [
        dict(situation='Generate a config file from a template in one go.', cmd="{ echo 'APP_ENV=prod'; echo \"BUILD=$(date -d 2026-11-06 +%Y%m%d)\"; } > .env\ncat .env",
             why='Braces group commands so one redirection captures all their output.')]),
     ('data', [
        dict(situation='Save the filtered rows of a CSV as a new file.', cmd="printf 'city,temp\\nPune,31\\nLeh,4\\nGoa,33\\n' > temps.csv\ngrep -v ',4$' temps.csv > warm.csv\ncat warm.csv",
             why='Never write to the input file (see the common mistake above); write a new one.')]),
     ('qa', [
        dict(situation='Protect an expected-results file from being overwritten by accident.', cmd="echo 'expected: 42' > expected.txt\nset -o noclobber\necho 'oops' > expected.txt\necho \"exit status $?\"\ncat expected.txt",
             why='With noclobber, > refuses to replace an existing file. Use <code>&gt;|</code> to overwrite on purpose.', expect='any')]),
     ('sec', [
        dict(situation='Create a file that is private from the start.', cmd="(umask 077; echo 'token=abc123' > secret.env)\nstat -c '%A %n' secret.env",
             why='> creates files with the umask permissions. Setting umask 077 in a subshell first means no one else can ever read it, not even for a moment (Lesson 9.3).')]),
    ],
    anat=anatomy([('ls', 'cmd', 'command'), ('>', 'opt', 'stdout to … (overwrite)'), ('list.txt', 'arg', 'target file')], 'Spaces around <code>&gt;</code> are optional: <code>ls&gt;list.txt</code> works too.')
) + mistake('sudo echo "nameserver 1.1.1.1" > /etc/resolv.conf     →  Permission denied', 'echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf    (append: sudo tee -a)',
            'Your own shell opens /etc/resolv.conf before sudo even starts, and you are not root. tee runs as root and opens the file itself.') + cmdcard_u(['logs: every run adds to the end', 'collecting results from many commands or loops into one file', 'audit trails'],
               ['files that must start fresh each run (use <code>&gt;</code>)', 'logs that grow forever without rotation (use logrotate, Lesson 13)'])(
    'gtgt', '>>', 'redirect stdout, appending',
    'Sends stdout to the end of a file, keeping what is already there. Creates the file if needed. Every write goes to the end, even when several programs append at once.',
    'command >> file   ·   command >> file 2>&1   ·   command &>> file', 'change',
    [('cmd >> file', 'append the output', 'logs'),
     ('cmd 2>> file', 'append the errors', 'error logs'),
     ('cmd >> file 2>&1', 'append both streams', 'cron jobs'),
     ('cmd &>> file', 'the same in bash', 'short form'),
     ('for … done >> file', 'append a whole loop', 'collect results'),
     ('echo "$(date +%F_%T) msg" >> log', 'timestamped log line', 'simple logging')],
    dict(cmd="echo 'Mon: ok' > week.log\necho 'Tue: ok' >> week.log\necho 'Wed: disk 91%' >> week.log\ncat week.log", note='Each <code>&gt;&gt;</code> adds a line; nothing is lost.'),
    [('sys', [
        dict(situation='A tiny log function for scripts, with timestamps.', cmd="log() { echo \"$(date -d '2026-11-06 02:00' '+%F %T') $*\" >> backup.log; }\nlog 'backup started'\nlog 'backup finished'\ncat backup.log",
             why='>> keeps every run. (The time is fixed here so the output stays stable; in real use: date \'+%F %T\'.)')]),
     ('devops', [
        dict(situation='The crontab line every admin should know.', cmd='0 2 * * * /opt/scripts/nightly.sh >> /var/log/nightly.log 2>&1',
             typical='(added with crontab -e: runs at 02:00 every night, results and errors appended to one log)',
             why='Append, both streams, absolute paths. This one line fixes the “log that vanished” and the “errors that went nowhere”.')]),
     ('data', [
        dict(situation='Collect results of a loop into one CSV.', cmd="echo 'n,square' > squares.csv\nfor n in 1 2 3; do echo \"$n,$((n*n))\" >> squares.csv; done\ncat squares.csv",
             why='Header once with >, rows with >>. (Faster for big loops: redirect the whole loop once: <code>done &gt;&gt; file</code>.)')]),
     ('sec', [
        dict(situation='An append-only audit line for each login attempt (demo).', cmd="for u in riya kabir; do echo \"2026-11-06 login $u\" >> audit.log; done\nwc -l audit.log",
             why='Audit files are only ever appended to. Admins can enforce it with <code>chattr +a</code> (root): then even > fails.')]),
     ('qa', [
        dict(situation='Append each test result, then count failures.', cmd="for t in t1 t2 t3; do\n  if [ \"$t\" = t2 ]; then echo \"$t FAIL\" >> results.txt; else echo \"$t PASS\" >> results.txt; fi\ndone\ngrep -c FAIL results.txt",
             why='One results file across all tests.')]),
    ]
) + cmdcard_u(['a command reads only stdin, or you do not want the file name in the output', 'loading SQL or data files into a database client', 'reading a file line by line in a loop (<code>while read … done &lt; file</code>)'],
               ['the command takes the file name itself (just give the name)', 'very large binary files to programs that expect text'])(
    'lt', '<', 'redirect stdin from a file',
    'Connects a file to the command’s standard input. The shell opens the file; the command just reads stdin and never sees the file name.',
    'command < file   ·   while read -r line; do …; done < file', 'safe',
    [('cmd < file', 'file as stdin', 'tools reading stdin'),
     ('wc -l < file', 'count without printing the name', 'clean numbers in scripts'),
     ('mysql db < dump.sql', 'run a SQL file', 'restores, migrations'),
     ('while read -r l; do …; done < file', 'loop over lines', 'process records'),
     ('cmd < in > out', 'input and output together', 'filters'),
     ('cmd < /dev/null', 'no input at all', 'cron, ssh in loops')],
    dict(cmd="printf 'Asha\\nRavi\\nMeena\\n' > team.txt\nwc -l team.txt\nwc -l < team.txt", note='With &lt; wc does not know the file name, so it prints just the number: perfect for <code>n=$(wc -l &lt; team.txt)</code>.'),
    [('dba', [
        dict(situation='Create tables and data from a SQL file (with mysql: <code>mysql shop &lt; schema.sql</code>).', setup=MINI,
             cmd="printf 'CREATE TABLE emp(id INT, name TEXT);\\nINSERT INTO emp VALUES (1,\"Asha\"),(2,\"Ravi\");\\nSELECT count(*) FROM emp;\\n' > schema.sql\npython3 minisql.py shop.db < schema.sql",
             why='The database client reads SQL from stdin, so &lt; runs a whole script: schema files, migrations and restores all work this way.'),
        dict(situation='Restore a MySQL dump (the real command).', cmd='mysql -u root -p shop < shop_2026-11-05.sql',
             typical='Enter password:\n(the dump is replayed; no output on success)',
             why='Dumps made with <code>mysqldump shop &gt; file.sql</code> are restored with &lt;. Check the exit status (Lesson 5.4).')]),
     ('sys', [
        dict(situation='Read a list of users line by line.', cmd="printf 'asha\\nravi\\n' > users.txt\nwhile read -r u; do echo \"would create user: $u\"; done < users.txt",
             why='The redirection is at the end of the loop, so the whole loop reads the file. -r keeps backslashes.')]),
     ('data', [
        dict(situation='Feed numbers to a calculator program.', cmd="echo '1250*18/100' > calc.txt\nbc < calc.txt",
             why='Any program that reads stdin can read a file this way.')]),
     ('devops', [
        dict(situation='Run a remote command in a loop without ssh eating the list (typical bug).', cmd='while read -r host; do ssh "$host" uptime < /dev/null; done < hosts.txt',
             typical='web01  10:30:01 up 12 days,  load average: 0.20, 0.15, 0.10\nweb02  10:30:02 up 30 days,  load average: 0.05, 0.08, 0.07',
             why='ssh reads stdin too, so without &lt; /dev/null it swallows the rest of hosts.txt and the loop ends after the first host (or use <code>ssh -n</code>).')]),
    ]
) + cmdcard_u(['keeping a record of errors from long jobs', 'separating errors from results for different people', 'hiding expected errors (2>/dev/null)'],
               ['when you need errors and results in their real order (use 2>&1 into one file)', 'hiding errors you do not understand'])(
    'err', '2>  ·  2>>', 'redirect stderr',
    'Sends standard error to a file (<code>2&gt;</code> overwrites, <code>2&gt;&gt;</code> appends). Results on stdout are not affected.',
    'command 2> errors.txt   ·   command 2>> errors.log   ·   command 2>/dev/null', 'change',
    [('2> file', 'errors to a file (overwrite)', 'one run’s errors'),
     ('2>> file', 'errors appended', 'long-term error log'),
     ('2>/dev/null', 'discard errors', 'expected errors only'),
     ('> out 2> err', 'two files', 'results and errors apart'),
     ('2> >(cmd)', 'errors into a command (bash)', 'colour or filter errors')],
    dict(cmd="echo x > a.txt\nls a.txt /nope 2> errors.txt\necho '--- errors.txt:'\ncat errors.txt", note='The result stays on screen; the error is in the file.', expect='any'),
    [('sys', [
        dict(situation='Search the whole file system as a normal user: results on screen, errors logged.', cmd="find /etc -name 'host*' 2> find_errors.txt | head -n 3\necho \"errors logged: $(wc -l < find_errors.txt)\"",
             why='Keep the error list instead of throwing it away: it tells you which folders you could not search.')]),
     ('dev', [
        dict(situation='Compiler warnings into a file to review later.', cmd="printf 'x = 1\\nprint(undefined_name)\\n' > app.py\npython3 app.py 2> run_errors.txt\necho \"exit $?\"; tail -n 1 run_errors.txt",
             why='Tracebacks go to stderr. Saving them keeps the screen clean in CI and gives you the full error to read.', expect='any')]),
     ('devops', [
        dict(situation='Append each night’s errors to their own log, results elsewhere.', cmd="for night in 1 2; do ls a.txt /missing_$night >> results.log 2>> errors.log; done\nwc -l results.log errors.log",
             why='Two logs for two audiences: results for reports, errors for the on-call engineer.', setup='echo x > a.txt')]),
     ('qa', [
        dict(situation='Assert that a command prints no errors.', cmd="ls a.txt 2> err.txt > /dev/null\nif [ -s err.txt ]; then echo 'FAIL: errors printed'; else echo 'PASS: no errors'; fi", setup='echo x > a.txt',
             why='<code>[ -s file ]</code> is true when the file is not empty.')]),
    ]
) + cmdcard_u(['one complete log with results and errors in order', 'cron jobs, CI steps, background services', 'piping errors into grep too (<code>2&gt;&amp;1 |</code>)'],
               ['when other programs need clean stdout data (keep errors separate)', 'POSIX sh scripts with &> (write > file 2>&1)'])(
    'both', '2>&1  ·  &>', 'both streams together',
    '<code>2&gt;&amp;1</code> makes stderr point to wherever stdout points <b>at that moment</b>. Written after <code>&gt; file</code>, both go into the file. Bash shortcuts: <code>&amp;&gt; file</code>, <code>&amp;&gt;&gt; file</code>, and <code>|&amp;</code> for pipes.',
    'command > file 2>&1   ·   command >> file 2>&1   ·   command &> file   ·   command 2>&1 | grep …', 'change',
    [('> file 2>&1', 'both into file (overwrite)', 'standard, works in every shell'),
     ('>> file 2>&1', 'both appended', 'cron and service logs'),
     ('&> file  /  &>> file', 'the same in bash', 'short, interactive use'),
     ('2>&1 | cmd', 'both into a pipe', 'grep through errors'),
     ('|& cmd', 'the same in bash', 'short form'),
     ('2>&1 > file', '<b>wrong order</b>: errors to screen, results to file', 'only to keep errors visible on purpose'),
     ('> /dev/null 2>&1', 'silence everything', 'quiet checks')],
    dict(cmd="echo x > a.txt\nls a.txt /nope > all.txt 2>&1\necho '--- all.txt:'; cat all.txt", note='Both lines are in all.txt and nothing reached the screen. This is the second line of the puzzle.', expect='any'),
    [('devops', [
        dict(situation='A CI step whose full output (warnings included) goes into the build log.', cmd="python3 -c 'import sys; print(\"building\"); print(\"warning: old API\", file=sys.stderr); print(\"done\")' >> build.log 2>&1\ncat build.log",
             why='One log in time order. (Order inside the file can still differ by buffering; see 5.1. Use python3 -u to keep it exact.)')]),
     ('sys', [
        dict(situation='Search through a command’s errors: errors must go into the pipe too.', cmd="ls a.txt /nope1 /nope2 2>&1 | grep -c 'No such file'", setup='echo x > a.txt',
             why='A pipe only carries stdout; 2&gt;&amp;1 first joins errors to it. Bash: <code>ls … |&amp; grep …</code>.')]),
     ('dev', [
        dict(situation='Keep only the errors and throw away the results: here the order is the trick.', cmd="ls a.txt /nope 2>&1 > /dev/null | wc -l", setup='echo x > a.txt',
             why='2&gt;&amp;1 first copies stderr to the pipe; then &gt; /dev/null moves only stdout away. Exactly the “wrong” order, used on purpose.')]),
     ('qa', [
        dict(situation='Prove the order rule with a real run.', cmd="echo x > a.txt\nls a.txt /nope 2>&1 > wrong.txt\necho '--- wrong.txt:'; cat wrong.txt",
             why='The error appeared on screen: when 2&gt;&amp;1 ran, 1 still pointed to the screen. Then 1 moved to the file, alone.', expect='any')]),
     ('web', [
        dict(situation='Start a dev web server in the background with its log in a file.', cmd="python3 -m http.server 8099 > server.log 2>&1 &\nsleep 1; curl -s -o /dev/null http://localhost:8099/; kill $!\ngrep -c 'GET /' server.log",
             why='The request log goes to stderr for this server; 2&gt;&amp;1 puts it into server.log with everything else.')]),
    ]
) + cmdcard_u(['output you truly do not need (progress, noise)', 'quiet checks where only the exit status matters (Lesson 5.4)', 'empty input for commands that would wait (< /dev/null)'],
               ['errors you have not read even once', 'debugging: remove the redirection first'])(
    'null', '/dev/null', 'the black hole',
    'A device file that accepts any amount of data and throws it away; reading from it gives immediate end-of-file. Everyone can write to it.',
    'command > /dev/null   ·   command 2>/dev/null   ·   command > /dev/null 2>&1   ·   command < /dev/null', 'safe',
    [('> /dev/null', 'discard results', 'only errors matter'),
     ('2>/dev/null', 'discard errors', 'expected Permission denied'),
     ('> /dev/null 2>&1  ·  &>/dev/null', 'discard everything', 'only the exit status matters'),
     ('< /dev/null', 'empty input', 'never wait for a keyboard'),
     ('cp /dev/null file', 'empty a file', 'like : > file')],
    dict(cmd='ls -l /dev/null\necho "gone" > /dev/null\ncat /dev/null | wc -c', note='A character device (c), writable by everyone (rw-rw-rw-), always empty.'),
    [('sys', [
        dict(situation='Does a user exist? Only the yes/no matters.', cmd="if id riya > /dev/null 2>&1; then echo 'user riya exists'; fi\nif ! id ghost > /dev/null 2>&1; then echo 'no user ghost'; fi",
             why='The output of id is not needed, only its exit status (Lesson 5.4).')]),
     ('devops', [
        dict(situation='Is a website up? Throw away the page, keep the HTTP code.', cmd='curl -s -o /dev/null -w "%{http_code}\\n" https://example.com',
             typical='200',
             why='-o /dev/null discards the body; -w prints only the status code. Classic health check.')]),
     ('dev', [
        dict(situation='Is a program installed? Check without printing its path.', cmd="for p in python3 git java; do if command -v \"$p\" > /dev/null; then echo \"$p: yes\"; else echo \"$p: no\"; fi; done",
             why='command -v prints the path on success; we only need yes or no.')]),
     ('sec', [
        dict(situation='Why attackers love 2>/dev/null, and why defenders log errors.', cmd="cat /etc/shadow 2>/dev/null; echo \"exit $? (error hidden)\"\ncat /etc/shadow 2>> denied.log; echo \"exit $? (error logged)\"; cat denied.log",
             why='Hidden errors leave no trace. Scripts you run as root should log, not discard.', expect='any')]),
    ]
) + cmdcard_u(['several lines of input written inside a script: SQL, config files, emails, help text', 'generating files from a template with $variables', 'feeding commands to interactive tools (ftp, mysql, ssh)'],
               ['large data (keep it in a separate file)', 'secrets inside the script file (they end up in git)'])(
    'heredoc', '<< EOF', 'here-document',
    'Gives the lines that follow, up to a line containing only the delimiter, to the command as stdin. Variables and $( ) are expanded unless the delimiter is quoted. <code>&lt;&lt;-</code> strips leading tabs.',
    "command << EOF … EOF   ·   command << 'EOF' … EOF   ·   command <<- EOF   ·   cat > file << EOF", 'safe',
    [('<< EOF', 'lines until EOF; $var and $( ) expanded', 'templates'),
     ("<< 'EOF'  or  << \\EOF", 'nothing expanded: text kept exactly', 'scripts, code with $'),
     ('<<- EOF', 'leading tabs removed (not spaces)', 'indented in if/for'),
     ('cat > file << EOF', 'write a file', 'config files'),
     ('cat >> file << EOF', 'append lines', 'add a block'),
     ('cmd << EOF > out', 'here-doc in, output to a file', 'SQL report'),
     ('any word: << END, << SQL', 'the delimiter is your choice', 'readability')],
    dict(cmd='name=Riya\ncat << EOF\nHello $name,\nyour report for $(date -d 2026-11-06 +%d-%m-%Y) is ready.\nEOF', note='$name and $( ) were filled in. The final EOF must be alone on its line, with nothing before or after it.'),
    [('sys', [
        dict(situation='Write a small config file from a script.', cmd="port=8080\ncat > app.conf << EOF\n[server]\nport=$port\nlog=/var/log/app.log\nEOF\ncat app.conf",
             why='cat &gt; file with a here-doc is the standard way to create multi-line files in scripts and Dockerfiles.')]),
     ('dba', [
        dict(situation='Run a SQL report from a script with no extra file (mysql: <code>mysql shop &lt;&lt; SQL</code>).', setup=MINI,
             cmd="python3 minisql.py shop.db << SQL\nCREATE TABLE IF NOT EXISTS sales(city TEXT, amt INT);\nINSERT INTO sales VALUES ('Pune',500),('Agra',300),('Pune',200);\nSELECT city, sum(amt) FROM sales GROUP BY city ORDER BY 2 DESC;\nSQL",
             why='The SQL lives next to the shell logic, with no temp file to clean up.')]),
     ('dev', [
        dict(situation='A script that writes another script: $ must NOT be expanded.', cmd="cat > greet.sh << 'EOF'\n#!/bin/bash\necho \"Hello, $USER from $HOSTNAME\"\nEOF\ncat greet.sh",
             why="With the quoted 'EOF' the text is kept exactly, so $USER is expanded later, when greet.sh runs."),
        dict(situation='Indented here-doc inside an if block (tabs).', cmd="if true; then\n\tcat <<- EOF\n\tindented with tabs in the script,\n\tprinted without them\n\tEOF\nfi",
             why='&lt;&lt;- removes leading tab characters (not spaces), so you can indent code neatly.')]),
     ('devops', [
        dict(situation='Run several commands on a remote server in one ssh call.', cmd="ssh web01 << 'EOF'\ndf -h / | tail -1\nuptime\nEOF",
             typical='/dev/sda1        50G   21G   27G  44% /\n 10:30:01 up 12 days,  2:14,  0 users,  load average: 0.20, 0.15, 0.10',
             why='The remote shell reads the commands from stdin. Quote EOF so that $variables are expanded on the server, not locally.')]),
     ('qa', [
        dict(situation='Give a program fixed answers to its questions.', cmd="python3 -c 'n=input(\"name? \"); a=input(\"age? \"); print(); print(n, \"is\", a)' << EOF\nAsha\n21\nEOF",
             why='Each line answers one input(). Repeatable tests for interactive programs.')]),
    ]
) + mistake('cat << EOF\n  text\n  EOF          ← indented with spaces', 'cat << EOF\ntext\nEOF           ← the delimiter alone, at the start of the line (or use <<- with tabs)',
            'bash looks for a line that is exactly <code>EOF</code>. With spaces in front it never finds it, keeps reading to the end of the script and warns: “here-document delimited by end-of-file”.') + cmdcard_u(['one line or one variable as input', 'quick calculations and tests: <code>bc &lt;&lt;&lt; "2^10"</code>', 'reading a value into several variables'],
               ['portable /bin/sh scripts (bash, zsh and ksh only)', 'many lines (use a here-document)'])(
    'herestr', '<<<', 'here-string',
    'Gives one string (with a newline added) to the command as stdin. Variables are expanded; quote the string to keep spaces.',
    'command <<< "text"   ·   command <<< "$variable"', 'safe',
    [('cmd <<< "text"', 'one string as stdin', 'quick input'),
     ('cmd <<< "$var"', 'a variable as stdin', 'no echo | needed'),
     ('read a b <<< "x y"', 'split into variables', 'parse one line'),
     ('bc <<< "scale=2; 10/3"', 'calculator', 'one-off sums'),
     ('grep -q pat <<< "$s"', 'test a string', 'validation')],
    dict(cmd='wc -c <<< "hello"\ntr a-z A-Z <<< "linux"\nbc <<< "2^10"', note='wc counts 6 bytes: here-strings add a newline.'),
    [('data', [
        dict(situation='Split a CSV line into variables.', cmd="line='EMP042,Asha,Pune'\nIFS=, read -r id name city <<< \"$line\"\necho \"$name works in $city ($id)\"",
             why='IFS=, splits on commas; the here-string feeds the line to read without a pipe.')]),
     ('dev', [
        dict(situation='Validate an input format.', cmd="for v in 2026-11-06 06/11/2026; do if grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' <<< \"$v\"; then echo \"$v valid\"; else echo \"$v invalid\"; fi; done",
             why='grep -q on a here-string tests a variable against a pattern.')]),
     ('sys', [
        dict(situation='Why not echo "$x" | read? (a real trap)', cmd="echo 'Asha' | read who; echo \"pipe: [$who]\"\nread who <<< 'Asha'; echo \"here-string: [$who]\"",
             why='Each part of a pipe runs in a subshell, so the variable set by read disappears (Lesson 5.3). The here-string runs read in the current shell.')]),
    ]
) + undo('Redirection can destroy data in one keystroke. Protect yourself.', [
    ('Overwrote a file with >:', 'there is no undo in the shell. Restore from backup or git (<code>git checkout -- file</code>). Prevent it: <code>set -o noclobber</code> in ~/.bashrc, then use <code>&gt;|</code> when you mean it.'),
    ('Emptied the input file (sort f > f):', 'same as above. Write to a new file and mv it, or use <code>sort -o f f</code>, <code>sed -i</code>, or <code>sponge</code> (moreutils).'),
    ('A here-doc swallowed the rest of the script:', 'the closing EOF was indented or misspelled. Fix that line; bash warns “delimited by end-of-file”.'),
    ('2>/dev/null hid the real problem:', 'run again without it, or log with 2>> instead.'),
    ('A log file grows forever with >>:', 'set up logrotate (Lesson 18.2); empty safely with <code>: &gt; file</code>.'),
]) + errors('Redirection errors students see most. Each was really produced on our build machine as a normal user, with its exit status.', [
    dict(cmd='echo hi > /root/test.txt', meaning='Your shell cannot create a file in /root: you are not root.', fix='Write somewhere you own, or <code>echo hi | sudo tee /root/test.txt</code>.'),
    dict(cmd='wc -l < no_such_file.txt', meaning='The input file does not exist; the command never ran.', fix='Check the name and path (Tab completion helps).'),
    dict(cmd='echo hi > /nodir/out.txt', meaning='The folder /nodir does not exist; > creates files, not folders.', fix='<code>mkdir -p</code> the folder first.'),
    dict(cmd='set -o noclobber; echo x > a.txt; echo y > a.txt', setup='rm -f a.txt', meaning='noclobber is on and a.txt exists.', fix='Use <code>&gt;|</code> to overwrite on purpose, or <code>&gt;&gt;</code> to append.'),
    dict(cmd='f=""; echo hi > $f', meaning='The variable is empty, so bash has no file name: “ambiguous redirect”.', fix='Check the variable, and quote it: <code>&gt; "$f"</code> gives the clearer “No such file or directory”.'),
    dict(cmd="printf 'cat << EOF\\nline\\n  EOF\\n' > t.sh; bash t.sh", meaning='The closing EOF had spaces before it, so bash read to the end of the file.', fix='Put EOF alone at the start of the line.'),
]) + qc('Write one command that appends both the output and the errors of <code>./job.sh</code> to job.log.', '<code>./job.sh &gt;&gt; job.log 2&gt;&amp;1</code> (bash: <code>./job.sh &amp;&gt;&gt; job.log</code>)') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def fds(one, two, note, tone='blue', hl=()):
    o = label_box(14, 20, 110, 96, ['ls', 'a.txt /nope'], 'card', 9)
    o += label_box(150, 26, 90, 30, ['fd 1', one], 'green' if 1 in hl else 'card', 8)
    o += label_box(150, 76, 90, 30, ['fd 2', two], 'red' if 2 in hl else 'card', 8)
    return o + arrow(126, 41, 148, 41) + arrow(126, 91, 148, 91) + t(180, 168, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ ls a.txt /nope > all.txt 2>&1', '$ cat all.txt', ("ls: cannot access '/nope'…", 'out'), ('a.txt', 'out')], title='riya@laptop', size=7.8) + cap('Right order: both lines in the file.', '', 'green', y=150, h=34),
       term(14, 16, 332, 116, ['$ ls a.txt /nope 2>&1 > all.txt', ("ls: cannot access '/nope'…", 'err'), '$ cat all.txt', ('a.txt', 'out')], title='riya@laptop', size=7.8) + cap('Swapped: the error still reaches the screen.', '', 'amber', y=150, h=34)]
behind = [fds('screen', 'screen', 'Start: 1 and 2 both point to the screen.', 'violet'),
          fds('all.txt', 'screen', '> all.txt: fd 1 now points to the file.', 'green', (1,)),
          fds('all.txt', 'all.txt', '2>&1: fd 2 copies fd 1 → the file. Both in.', 'green', (1, 2)),
          fds('screen', 'screen', 'Swapped order, start again: both on screen.', 'violet'),
          fds('screen', 'screen', '2>&1 first: 2 copies 1 = the screen (no change).', 'amber', (2,)),
          fds('all.txt', 'screen', 'Then > all.txt moves only fd 1. Error on screen.', 'red', (1,))]
see = [see[0], see[0], see[0], see[1], see[1], see[1]]
two = anim_two('Why the order of 2>&1 matters', 'Read left to right, like the shell',
               'Two terminals: with > all.txt 2>&1 both lines are in the file; with 2>&1 > all.txt the error shows on screen.',
               'Boxes for fd 1 and fd 2 changing target step by step for both orders.', see, behind,
               ['<code>ls a.txt /nope &gt; all.txt 2&gt;&amp;1</code>', 'The shell reads the redirections from left to right.', 'Result: all.txt has the result and the error.',
                '<code>ls a.txt /nope 2&gt;&amp;1 &gt; all.txt</code>', 'Same words, different order.', 'Result: the error is on the screen, only a.txt in the file.'],
               ['Both descriptors start at the terminal.', '&gt; all.txt re-points fd 1.', '2&gt;&amp;1 copies where fd 1 points <b>now</b>: the file.',
                'Second try, fresh start.', '2&gt;&amp;1 copies fd 1, which is still the screen.', '&gt; all.txt then changes only fd 1.'])

n1 = term(14, 14, 332, 100, ['$ cat week.log', ('Mon ok', 'out'), ('Tue ok', 'out'), ('Wed disk 91%', 'out')], title='riya@server', size=7.8) + cap('A log with three nights.', '', 'card', y=150, h=34)
n2 = term(14, 14, 332, 100, ['$ echo "Thu ok" > week.log', '$ cat week.log', ('Thu ok', 'err')], title='riya@server', size=7.8) + cap('One > : Mon to Wed are gone.', '', 'red', y=150, h=34)
n3 = term(14, 14, 332, 100, ['$ set -o noclobber', '$ echo "Thu ok" > week.log', ('bash: week.log: cannot overwrite existing file', 'err')], title='riya@server', size=7.2) + cap('noclobber refuses to overwrite.', '', 'amber', y=150, h=34)
n4 = term(14, 14, 332, 100, ['$ echo "Thu ok" >> week.log', '$ wc -l week.log', ('4 week.log', 'acc')], title='riya@server', size=7.8) + cap('>> appends: four nights kept.', '', 'green', y=150, h=34)
s1 = anim_one('Real-time scenario', 'One character between a log and nothing',
              'Riya’s week log, a slip of the finger, and the safety net.',
              '> versus >>', 'A log with three lines; > replaces it with one line; noclobber refuses; >> appends a fourth line.', [n1, n2, n3, n4],
              ['The log has Monday to Wednesday.', 'Typing <code>&gt;</code> instead of <code>&gt;&gt;</code> empties the file first.', 'With <code>set -o noclobber</code>, bash refuses to overwrite.', 'With <code>&gt;&gt;</code> the new night is simply added.'], hid='scenario-log')

dx = dissect('Layer by layer: ./job.sh >> job.log 2>&1',
    'What the shell does with the most common redirection line. Each layer has a real command and output from our build machine.', [
    dict(key='parse', name='Parse', sub='left to right',
         why='Redirections are instructions for the shell, not arguments.',
         how='bash removes them from the command line and remembers them in order.',
         impl='The command sees only its own arguments.', used='Every line.',
         cmd="printf '#!/bin/bash\\necho \"args: $#\"\\n' > job.sh; chmod +x job.sh\n./job.sh >> job.log 2>&1; cat job.log"),
    dict(key='open', name='open(O_APPEND)', sub='>> job.log',
         why='Append mode keeps old lines.',
         how='The file is created if missing, never emptied.',
         impl='open(..., O_WRONLY|O_CREAT|O_APPEND); dup2 to fd 1.', used='Logs.',
         cmd='echo one >> j.log; echo two >> j.log; cat j.log'),
    dict(key='dup', name='dup2(1, 2)', sub='2>&1',
         why='Errors should go where results go.',
         how='fd 2 becomes a copy of fd 1 (the log).',
         impl='Same open file, same position.', used='cron, CI.',
         cmd='echo x > a.txt; ls a.txt /nope >> j2.log 2>&1; cat j2.log', expect='any'),
    dict(key='run', name='Run the job', sub='inherits 1 and 2',
         why='The job writes normally.',
         how='Children of the job inherit the same descriptors.',
         impl='fork + exec.', used='Every child process.',
         cmd="bash -c 'echo out; echo err >&2; ls /nope' >> j3.log 2>&1; cat j3.log", expect='any'),
    dict(key='file', name='The log', sub='grows each run',
         why='History for later checks.',
         how='Each run appends at the end.',
         impl='ext4 file; rotate with logrotate.', used='/var/log.',
         cmd='for i in 1 2 3; do echo "run $i" >> j4.log 2>&1; done; wc -l < j4.log'),
], hint='From the command line to the log file. Click a layer.')

HOOD = hood('Under the hood: > versus >>', 'The difference is one flag in the <code>openat()</code> system call: <code>O_TRUNC</code> (empty it) or <code>O_APPEND</code> (add to the end). Here bash runs <code>echo x &gt; a.txt; echo y &gt;&gt; a.txt</code>.',
    "bash -c 'echo x > a.txt; echo y >> a.txt'", show='openat.*a\\.txt|dup2|^write\\(1')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Why the order of 2&gt;&amp;1 matters, and the log that was saved</h2>
  <p>Left: what Riya sees. Right: where fd 1 and fd 2 point after each redirection.</p>
''' + two + s1 + dx + HOOD + qc('In <code>cmd 2&gt;&amp;1 &gt; out.txt</code>, where do the errors go?', 'To the screen. When 2&gt;&amp;1 was applied, fd 1 still pointed to the terminal; the later &gt; out.txt moved only fd 1.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Redirection at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ job >> log', 'prompt'), ('2>&1', 'acc')], title='cron', size=6.4, step=12),
              '1. Scheduled jobs and logs', 'Every cron job and many systemd scripts end in >> logfile 2>&1 so results and errors are kept in order.', ['Job', '*>> 2>&1', 'log']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['mysqldump >', 'mysql <'], 'blue', 8.6), '2. Database backups and restores',
    'DBAs dump with > (often gzip-compressed through a pipe) and restore with < every night.', ['DB', '*> dump.sql', 'restore <']) + '\n' + usecase(
    term(8, 14, 104, 62, [("$ cat > f << 'EOF'", 'prompt'), ('config…', 'acc')], title='docker', size=6.2, step=12),
    '3. Config and provisioning', 'Dockerfiles, cloud-init and setup scripts write config files with cat > file << EOF.', ['Script', '*here-doc', 'config file']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['&>/dev/null', 'exit code'], 'green', 8.6), '4. Health checks',
    'Monitoring checks throw away output and react only to success or failure (Lesson 5.4).', ['Check', '*/dev/null', 'OK / alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['tee', 'sudo'], 'violet', 8.6), '5. Editing system files from scripts',
    'Admins use | sudo tee (or tee -a) because sudo does not apply to the shell’s redirection.', ['Line', '*sudo tee', '/etc/file']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine as a normal user.', [
    dict(level='b', title='Save and add', scenario='Start a shopping list, then add an item.',
         cmd="echo 'milk' > list.txt; echo 'bread' >> list.txt; cat list.txt", explain='> once, >> after.'),
    dict(level='b', title='Count without the name', scenario='Just the number of lines, for a variable.',
         cmd="printf 'a\\nb\\nc\\n' > f.txt; n=$(wc -l < f.txt); echo \"lines=$n\"", explain='< hides the file name.'),
    dict(level='i', title='Quiet check', scenario='Is port-80 config present? Only yes/no.',
         cmd="echo 'Listen 80' > web.conf; grep -q 'Listen 80' web.conf > /dev/null 2>&1 && echo yes", explain='Output discarded, exit status used.'),
    dict(level='i', title='Only the errors', scenario='Count how many paths are missing, ignore the rest.',
         cmd='touch a b; ls a b c d 2>&1 > /dev/null | wc -l', explain='Order trick: errors to the pipe, results to /dev/null.'),
    dict(level='a', title='Compare two command outputs', scenario='Which files are in one folder but not the other?',
         cmd='mkdir -p d1 d2; touch d1/{a,b,c} d2/{a,c}; diff <(ls d1) <(ls d2)', explain='Process substitution: each ls becomes a file for diff.', expect='any'),
], extra=build_up('a nightly job with a proper log', 'Riya turns a noisy job into a well-behaved one, one redirection at a time.',
    "printf '#!/bin/bash\\necho \"backup ok: $1\"\\nls /data_missing\\n' > job.sh; chmod +x job.sh", [
    ('./job.sh mon', '1. Run it: result and error both on screen.'),
    ('./job.sh mon > job.log; cat job.log', '2. > saves the result; the error still shows.'),
    ('./job.sh mon > job.log 2>&1; ./job.sh tue > job.log 2>&1; cat job.log', '3. Both streams saved, but each run replaces the last.'),
    ('./job.sh mon >> job.log 2>&1; ./job.sh tue >> job.log 2>&1; cat job.log', '4. >> 2>&1: every night kept, errors included.'),
], expect='any')) + which('Choosing the right operator.', [
    ('New or fresh file', 'cmd > file', 'Clean result.', '> on logs.'),
    ('Growing log', 'cmd >> file 2>&1', 'History kept.', '> (empties it).'),
    ('Feed a file', 'cmd < file', 'Clean numbers.', 'cat file | cmd (extra process).'),
    ('Errors apart', '> out 2> err', 'Two audiences.', 'Mixing data and errors.'),
    ('Both together', '> f 2>&1 (or &> f)', 'Time order.', '2>&1 > f.'),
    ('Silence', '&> /dev/null', 'Only exit status.', 'Hiding unknown errors.'),
    ('Many lines inline', '<< EOF / << \'EOF\'', 'No temp files.', 'echo line by line.'),
    ('Root-owned file', '| sudo tee [-a]', 'Works.', 'sudo cmd > file.'),
]) + keys('Shortcuts and handy forms.', [
    ('set -o noclobber', 'protect files from >', 'add to ~/.bashrc'),
    ('>|', 'overwrite anyway', 'ls >| list.txt'),
    (': > file', 'empty a file (keep it open for services)', ': > app.log'),
    ('&>  &>>', 'bash: both streams', 'cmd &>> all.log'),
    ('|&', 'bash: pipe both streams', 'make |& grep error'),
    ('Ctrl + R', 'search history for that long redirection line', 'Ctrl+R 2>&1'),
    ('<<- EOF', 'here-doc with tab indentation', 'inside if/for'),
    ('<(cmd)', 'output as a file (bash)', 'diff <(ls a) <(ls b)'),
]) + scriptit('report.sh', 'A nightly report script that uses every operator from this lesson: a here-doc template, &gt; for the fresh report, &gt;&gt; 2&gt;&amp;1 for the log, &lt; for input and /dev/null for a quiet check.',
'''#!/bin/bash
printf 'Pune,500\\nAgra,300\\nGoa,200\\n' > sales.csv   # demo input
day=2026-11-06; log=report.log
total=$(cut -d, -f2 < sales.csv | paste -sd+ | bc)
cat > report.txt << EOF
Sales report for $day
Cities: $(wc -l < sales.csv)
Total:  Rs $total
EOF
if grep -q Goa sales.csv > /dev/null 2>&1; then
  echo "$day report ok (total $total)" >> "$log" 2>&1
fi
cat report.txt; echo "--- $log:"; cat "$log"''') + puzzle_answer('No. <code>ls notes.txt /nope &gt; all.txt 2&gt;&amp;1</code> puts <b>both</b> lines in all.txt. <code>ls notes.txt /nope 2&gt;&amp;1 &gt; all.txt</code> prints the error on the screen and puts only the result in the file. The shell applies redirections from left to right, and <code>2&gt;&amp;1</code> copies where stdout points <b>at that moment</b>.') + qc('Why does <code>sudo echo x &gt; /etc/test</code> fail with Permission denied?', 'The redirection is done by your own (non-root) shell before sudo runs. Use <code>echo x | sudo tee /etc/test</code>.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-standard-streams-stdin-stdout-stderr-and-file/">Lesson 5.1</a>: stdin 0, stdout 1, stderr 2.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
