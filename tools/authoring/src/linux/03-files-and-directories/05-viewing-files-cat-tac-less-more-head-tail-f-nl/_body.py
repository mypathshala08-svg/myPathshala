import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

LOG = r"""printf '2026-11-06 10:00:01 INFO start\n2026-11-06 10:00:02 INFO user login\n\n\n2026-11-06 10:00:05 ERROR db timeout\n2026-11-06 10:00:07\tWARN slow query\n2026-11-06 10:00:09 ERROR disk full\n' > app.log"""
CSV = r"""printf 'id,name,city,marks\n1,Asha,Pune,91\n2,Ravi,Delhi,78\n3,Meena,Chennai,85\n4,Imran,Mumbai,66\n' > students.csv"""

HOOK = hook('A production server writes a 2 GB log. Double-clicking it would freeze an editor, and the server has no screen anyway. Riya needs the <b>last 50 lines</b>, then to <b>watch new errors as they happen</b>, then to know <b>how many lines</b> the file has. Each of these is one short command that never loads the whole file.',
    ['print, join and number files (<code>cat</code>, <code>tac</code>, <code>nl</code>)',
     'read only the beginning or the end of any file, however big (<code>head</code>, <code>tail</code>)',
     'follow a log live as it grows, and survive log rotation (<code>tail -f</code>, <code>tail -F</code>)',
     'scroll and search long files (<code>less</code>, <code>more</code>) and count lines, words and bytes (<code>wc</code>)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'a 2 GB log, no editor'),
    ('decide', 'Which command when?', 2, 'cat, less, head, tail…'),
    ('definition', 'What the commands are', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each command, by field', 15, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'tail -f vs tail -F'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which viewing command? (decide in 5 seconds)', [
    ('Show a short file', 'cat file', 'whole file at once'),
    ('Read a long file, scroll and search', 'less file', 'q to quit, /word to search'),
    ('The first lines (headers, samples)', 'head -n 20 file', 'default 10'),
    ('The last lines (latest log entries)', 'tail -n 50 file', 'default 10'),
    ('Watch a log live', 'tail -f file', 'Ctrl+C to stop'),
    ('Watch a log that gets rotated', 'tail -F file', 'reopens the new file'),
    ('Newest entries first', 'tac file', 'reverse line order'),
    ('Lines 1000 to 1010', 'head -n 1010 f | tail -n 11', 'or sed -n 1000,1010p'),
    ('Skip the CSV header', 'tail -n +2 file.csv', 'from line 2 to the end'),
    ('How many lines?', 'wc -l file', '-w words, -c bytes'),
    ('Numbers in front of lines', 'nl -ba file  or  cat -n', 'for references'),
    ('See hidden characters (tabs, Windows line ends)', 'cat -A file', '^I tab, ^M carriage return'),
])

cmap = concept_map(
    [('3.1', 'Creating files', 'something to view'), ('3.4', 'Wildcards', 'head -n 3 *.csv'), ('2.5', 'Getting help', 'man uses less')],
    ['cat, tac: print, join, reverse; -n -b -s -A', 'head and tail: first / last lines, -n +N, -c', 'tail -f, -F, --pid: follow logs live', 'less and more: scroll, search, follow', 'nl and wc: number and count'],
    [('5.3', 'Pipes', 'tail -f | grep ERROR'), ('6.1', 'grep', 'search inside files'), ('6.4', 'sed', 'print line ranges'), ('18.2', 'Log analysis', 'journalctl, /var/log')],
    'Reading files without an editor is the most used skill on servers: logs, configs, CSV samples.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 150, ['$ ls -lh /var/log/app.log', ('… 2.0G … app.log', 'out'), '$ tail -n 3 /var/log/app.log', ('10:41:02 ERROR db timeout', 'err'), ('10:41:05 WARN retry 1', 'out'), ('10:41:07 ERROR db timeout', 'err'), '$ tail -f /var/log/app.log | grep ERROR'], title='server-01', prompt='$', size=7.4, step=15)
      + t(352, 36, 'Never open the whole file:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• tail: only the end', '• tail -f: live', '• head: only the start', '• less: scroll + search', '• wc -l: count lines'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A 2 GB log and no editor</h2>
  <div class="story">
''' + puzzle('Every night at midnight the server renames <code>app.log</code> to <code>app.log.1</code> and starts a new empty app.log. Riya left <code>tail -f app.log</code> running overnight. In the morning she sees no new lines at all, even though the application is busy. Why, and what one-letter change fixes it?') + '''
    <p class="narration">Users report errors on the shop website. Riya logs in to the server: the application log is 2 GB. Opening it in an editor would take minutes and lots of memory.</p>
''' + scene('A terminal on a server: a 2 GB log; tail shows the last lines with errors; tail -f piped to grep follows only new ERROR lines live.', sc,
            'Read only the part you need: <tspan font-weight="700" class="s-acc">head, tail, less</tspan>.') + '''
A> You never need the whole file. <code>tail</code> reads only the end: the newest entries. <code>tail -f</code> keeps the file open and prints new lines as they are written.
R> And to read from the beginning, page by page?
K> <code>less</code>. Space for the next page, <code>/ERROR</code> to search, <code>G</code> to jump to the end, <code>q</code> to quit. It does not load the whole file into memory either.
A> Today: <code>cat</code>, <code>tac</code>, <code>head</code>, <code>tail</code>, <code>less</code>, <code>more</code>, <code>nl</code> and <code>wc</code>. For each one, the options you need, and how admins, data engineers, developers, DBAs, testers and security analysts use them.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 220" role="img" aria-label="A long scroll of paper: cat unrolls all of it, head cuts the top, tail cuts the bottom, less is a window you slide up and down, wc counts the lines, tail -f watches the bottom as new lines are written.">'
       + ''.join(label_box(14 + k * 104, 22, 96, 110, [a, b, c], tone, 8.8) for k, (a, b, c, tone) in enumerate([
           ('cat', 'unroll all', 'of it', 'blue'), ('head', 'cut the top', 'part', 'green'), ('tail', 'cut the bottom', 'part', 'amber'),
           ('less', 'a sliding', 'window', 'violet'), ('tail -f', 'watch the end', 'grow', 'red'), ('wc', 'count lines,', 'words, bytes', 'card')]))
       + t(320, 162, 'A file is a long paper scroll of lines.', 9.6, 'ink2')
       + t(320, 184, 'Pick the tool that shows only the piece you need.', 9.6, 'acc', bold=True)
       + '<text x="632" y="214" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Viewing files at four depths', [
    ('v', 'No jargon: a long paper scroll', '      <p>Imagine a file as a very long paper scroll.</p>' + pic + '''
      <ul>
        <li><code>cat</code> unrolls the whole scroll onto the screen: fine for short notes.</li>
        <li><code>head</code> shows the top, <code>tail</code> the bottom: the newest lines of a log are at the bottom.</li>
        <li><code>less</code> is a window you slide up and down, with a search.</li>
      </ul>'''),
    ('b', 'The commands you will type every day', '''      <ul>
        <li><code>cat notes.txt</code> prints a file; <code>cat a.txt b.txt</code> prints both, one after the other.</li>
        <li><code>head file</code> = first 10 lines; <code>head -n 3 file</code> = first 3. <code>tail</code> the same for the last lines.</li>
        <li><code>less file</code>: Space / b = page down / up, <code>/word</code> search, <code>n</code> next match, <code>g</code> / <code>G</code> top / bottom, <code>q</code> quit.</li>
        <li><code>wc -l file</code> counts lines; <code>nl file</code> or <code>cat -n file</code> numbers them.</li>
        <li><code>tail -f app.log</code> follows a log live; <code>Ctrl+C</code> stops it.</li>
      </ul>'''),
    ('i', 'The options that solve real problems', '''      <ul>
        <li><code>tail -n +2 data.csv</code> = from line 2 to the end (skip the header); <code>head -n -1</code> = all but the last line.</li>
        <li>A range: <code>head -n 1010 f | tail -n 11</code> = lines 1000–1010.</li>
        <li><code>cat -A</code> shows tabs as <code>^I</code>, line ends as <code>$</code>, Windows carriage returns as <code>^M</code>: the cause of many “invisible” bugs.</li>
        <li><code>cat -s</code> squeezes repeated blank lines; <code>cat -b</code> numbers only non-empty lines; <code>nl</code> does the same by default and has formats (<code>-nrz</code>, <code>-w</code>, <code>-s</code>, <code>-bp</code>).</li>
        <li><code>tail -F</code> = follow by <b>name</b> and retry: survives log rotation. <code>--pid=PID</code> stops when a process ends.</li>
      </ul>'''),
    ('a', 'Behind the screen: why tail is fast', '''      <ul>
        <li><code>tail</code> on a regular file does not read from the start: it <code>lseek()</code>s near the end and reads backwards until it has enough newlines. That is why tail on 2 GB is instant, while <code>cat | tail</code> reads all 2 GB.</li>
        <li><code>head</code> stops reading as soon as it has N lines, so it is instant too.</li>
        <li><code>tail -f</code> keeps the file descriptor open and uses <b>inotify</b> (or polling once per second) to notice growth. After rotation the old descriptor points to app.log.1; <code>-F</code> checks the <b>name</b> and reopens.</li>
        <li><code>less</code> reads only what it shows and builds a line index as you move; <code>less +F</code> follows like tail -f, Ctrl+C returns to normal scrolling.</li>
        <li><code>wc -l</code> counts newline characters: a last line without <code>\\n</code> is not counted. <code>-m</code> counts characters (UTF-8 aware), <code>-c</code> bytes: different for Hindi or emoji.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>cat, tac, head, tail, less, more, nl and wc</h2>
''' + def_block(
    '<code>cat</code> (concatenate) writes files to standard output, one after another; <code>tac</code> does the same with the line order reversed. <code>head</code> and <code>tail</code> output the first or last part of files (by lines or bytes); <code>tail -f</code> keeps printing data appended to a file. <code>less</code> and <code>more</code> are pagers that display text one screen at a time. <code>nl</code> numbers lines and <code>wc</code> (word count) counts lines, words, characters and bytes.',
    'Small files: <code>cat</code>. Big files: <code>less</code>. Just the start or end: <code>head</code> / <code>tail</code>. Live logs: <code>tail -f</code>. Counting: <code>wc</code>.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Pager', 'A program that shows text one screen at a time: less, more.'),
    ('Standard output', f'Where a command prints: the screen, a file or a pipe. {gl("standard-streams-stdin-stdout-stderr", "Glossary →")}'),
    ('Pipe |', f'Send one command’s output to another. {gl("pipe", "Glossary →")}'),
    ('Log rotation', f'Renaming old logs and starting new ones. {gl("logrotate", "Glossary →")}'),
    ('Line ending', 'Linux \\n (LF); Windows \\r\\n (CRLF).'),
    ('Concatenate', 'Join one after another.'),
    ('Filter', f'A command that reads text and prints changed text. {gl("filter", "Glossary →")}'),
    ('Counting tools', f'wc, cut and tr. {gl("cut-tr-and-wc", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('cat', 'concatenate', 'Join files; printing one file is the simplest case.'),
    ('tac', 'cat backwards', 'Reverses line order.'),
    ('head / tail', 'head and tail of a file', 'Top and bottom.'),
    ('less', '“less is more”', 'An improved more: it can scroll back.'),
    ('more', 'more…', 'Showed “--More--” at the bottom of each page.'),
    ('nl', 'number lines', 'Line numbers with formats.'),
    ('wc', 'word count', 'Also lines, characters and bytes.'),
    ('-f', 'follow', 'Keep reading as the file grows.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Whole small file', '<code>cat file</code> · numbered: <code>cat -n</code>'),
    ('Long file', '<code>less file</code> · <code>/word</code> · <code>q</code>'),
    ('First / last lines', '<code>head -n 20</code> · <code>tail -n 50</code>'),
    ('Live log', '<code>tail -f app.log</code> · rotated: <code>-F</code>'),
    ('Skip header', '<code>tail -n +2 data.csv</code>'),
    ('Count', '<code>wc -l</code> lines · <code>-w</code> words · <code>-c</code> bytes'),
]) + '\n' + lv + didyou('<code>less</code> was written in 1983–85 by Mark Nudelman because <code>more</code> could not scroll backwards. The joke name, “less is more”, stuck. It is still maintained by the same author forty years later, and <code>man</code> uses it to show every manual page.') + '''
EXAM> “How do you view the last 100 lines of a log and keep watching it?” → tail -n 100 file, then tail -f file (or tail -n 100 -f); mention tail -F for rotated logs, Ctrl+C to stop, and less +F as an alternative.
''' + qc('Which command shows a CSV file without its header line?', '<code>tail -n +2 file.csv</code>: from line 2 to the end.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Which part of the file does each command read?</h2>
''' + table(['Command', 'Reads', 'Big files', 'Typical use'], [
    ['<code>cat</code>', 'everything, in order', 'floods the screen', 'short files, joining files'],
    ['<code>tac</code>', 'everything, last line first', 'reads all', 'newest log lines first'],
    ['<code>head</code>', 'first N lines / bytes', 'instant', 'headers, samples'],
    ['<code>tail</code>', 'last N lines / bytes', 'instant (seeks to the end)', 'latest log entries'],
    ['<code>tail -f / -F</code>', 'the end, and every new line', 'instant, runs until Ctrl+C', 'live monitoring'],
    ['<code>less</code>', 'one screen at a time, any direction', 'fast, low memory', 'reading and searching'],
    ['<code>more</code>', 'one screen at a time, mostly forward', 'fast', 'very old or minimal systems'],
    ['<code>nl</code>', 'everything, with numbers', 'reads all', 'line references, reports'],
    ['<code>wc</code>', 'everything, only counts', 'reads all (fast)', 'sizes, checks, monitoring'],
], minw=600) + mistake('cat 2GB.log | tail -n 50', 'tail -n 50 2GB.log',
                       'Through a pipe, tail cannot jump to the end: cat must push all 2 GB through it. Give the file name directly so tail can seek. (Same for “useless use of cat”: <code>cat f | grep x</code> → <code>grep x f</code>.)') + qc('Which two commands are instant on a 2 GB file, and why?', '<code>head</code> (stops after N lines) and <code>tail</code> on a file name (jumps to the end). cat, tac, nl and wc must read everything.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">The examples use a small sample log <code>app.log</code> (7 lines: INFO, two empty lines, a tab, two ERROR lines) and <code>students.csv</code> (a header and 4 rows). Every output was recorded on Ubuntu 24.04; less and more are interactive, so their screens are shown as typical output.</p>
''' + cmdcard_u(['the file is short (fits on one screen)', 'joining files into one: <code>cat a b &gt; all</code>', 'checking hidden characters: <code>cat -A</code>'],
               ['the file is long (use less, head or tail)', 'feeding one file into another command (give the file name to that command)', 'binary files (use <code>file</code>, <code>strings</code>, <code>xxd</code>)'])(
    'cat', 'cat · tac', 'concatenate · reverse',
    '<code>cat</code> prints files in order, one after another; <code>tac</code> prints them with the last line first.',
    'cat [OPTION]... [FILE]...   ·   tac [FILE]...', 'safe',
    [('cat f', 'print the file', 'short files'),
     ('cat a b > all', 'join files into one', 'merging parts, CSV exports'),
     ('-n', 'number all lines', 'refer to line numbers'),
     ('-b', 'number non-empty lines only', 'code, logs with gaps'),
     ('-s', 'squeeze repeated empty lines into one', 'messy files'),
     ('-A', 'show tabs ^I, line ends $, other hidden characters', 'debugging “invisible” problems'),
     ('-E / -T', 'only line ends / only tabs', 'checking trailing spaces / tabs'),
     ('tac f', 'last line first', 'newest log lines first')],
    dict(cmd='cat -n app.log', setup=LOG, note='7 lines: two are empty, and line 6 contains a tab (it looks like spaces).'),
    [('dev', [
        dict(situation='A script fails with “bad interpreter”: the file was saved on Windows.', cmd="printf '#!/bin/bash\\r\\necho hi\\r\\n' > run.sh\ncat -A run.sh",
             why='<code>^M$</code> at each line end = Windows CRLF. Fix with <code>sed -i "s/\\r$//" run.sh</code> or dos2unix.'),
        dict(situation='Check for trailing spaces in a config file.', cmd="printf 'port=80  \\nhost=db\\n' > app.conf\ncat -E app.conf",
             why='The <code>$</code> marks the real line end: the spaces before it are visible now.')]),
     ('data', [
        dict(situation='Merge monthly CSV exports into one file, keeping only the first header.', cmd="printf 'id,amt\\n1,10\\n' > jan.csv; printf 'id,amt\\n2,20\\n' > feb.csv\n{ cat jan.csv; tail -n +2 feb.csv; } > q1.csv\ncat q1.csv",
             why='cat for the first file, tail -n +2 for the rest skips their headers. <code>{ …; }</code> sends both into one file.')]),
     ('sys', [
        dict(situation='Read the newest errors first from a log.', setup=LOG, cmd='tac app.log | grep -m 2 ERROR',
             why='tac reverses the order; grep -m 2 stops after the two newest errors.')]),
     ('sec', [
        dict(situation='Look inside an unknown file safely, without running it.', cmd='file /bin/ls | cut -c1-36\ncat -v /bin/true | head -c 40; echo',
             why='Binary files print garbage and can mess up the terminal; <code>file</code> tells you the type, and <code>cat -v</code> shows unprintable bytes as ^ and M- codes.')]),
     ('qa', [
        dict(situation='Compare expected and actual output by eye, with line numbers.', cmd="printf 'a\\nb\\nc\\n' > expected.txt; printf 'a\\nB\\nc\\n' > actual.txt\ncat -n expected.txt actual.txt",
             why='Numbers make it easy to point to a line. For real comparisons use <code>diff</code> (Lesson 6.3).')]),
    ],
    anat=anatomy([('cat', 'cmd', 'command'), ('-n', 'opt', 'number lines'), ('jan.csv feb.csv', 'arg', 'files, in order'), ('&gt; all.csv', 'sep', 'redirect to a file')], 'Without a file name, cat reads the keyboard (stdin) until Ctrl+D, which is why <code>cat &gt; file</code> creates a file (Lesson 3.1).')
) + cmdcard_u(['you need only the start (head) or the end (tail) of a file', 'huge files: both are instant on a file name', 'skipping headers, cutting a line range, sampling data'],
               ['you need lines in the middle by pattern (use grep, Lesson 6.1)', 'you want to scroll interactively (use less)'])(
    'headtail', 'head · tail', 'first lines · last lines',
    '<code>head</code> prints the first 10 lines, <code>tail</code> the last 10. Both accept other counts, bytes, and several files; tail can also start <b>from</b> a line number.',
    'head [-n N | -c N] [FILE]...   ·   tail [-n N | -n +N | -c N] [FILE]...', 'safe',
    [('head -n N / -N', 'first N lines', 'samples, headers'),
     ('head -n -N', 'all but the last N lines', 'remove a footer'),
     ('head -c N', 'first N bytes', 'file signatures, binary headers'),
     ('tail -n N', 'last N lines', 'latest log entries'),
     ('tail -n +N', 'from line N to the end', 'skip a header'),
     ('tail -c N', 'last N bytes', 'checking file endings'),
     ('-q / -v', 'hide / show “==> name &lt;==” headers', 'several files')],
    dict(cmd='head -n 2 app.log\ntail -n 2 app.log', setup=LOG, note='The two oldest and the two newest entries.'),
    [('data', [
        dict(situation='See the header and two rows of a CSV before loading it.', setup=CSV, cmd='head -n 3 students.csv',
             why='Always look at a sample first: separator, header names, quoting.'),
        dict(situation='Data rows only, without the header.', setup=CSV, cmd='tail -n +2 students.csv',
             why='<code>+2</code> = start at line 2. Used before sort or awk so the header is not sorted with the data.'),
        dict(situation='Lines 1000 to 1010 of a big file.', cmd='seq 1 2000 > big.txt\nhead -n 1010 big.txt | tail -n 11 | tr "\\n" " "; echo',
             why='head stops at 1010, tail keeps the last 11 of those. (seq: Lesson 3.6.)')]),
     ('sys', [
        dict(situation='The first line of every config file in a folder.', cmd="mkdir -p conf && echo 'port=80' > conf/web.conf && echo 'port=5432' > conf/db.conf\nhead -n 1 conf/*.conf",
             why='With several files head prints a “==&gt; name &lt;==” header for each; <code>-q</code> hides them.')]),
     ('sec', [
        dict(situation='Identify a file by its first bytes (“magic number”), whatever its extension.', cmd='head -c 4 /bin/ls | od -c | head -1',
             why='Executables start with \\177 E L F. A “photo.jpg” that starts with ELF is a disguised program.')]),
     ('dba', [
        dict(situation='Check that a big SQL dump finished completely: look at its last lines.', cmd="printf -- '-- MySQL dump\\nINSERT INTO t VALUES (1);\\n-- Dump completed on 2026-11-06\\n' > night.sql\ntail -n 1 night.sql",
             why='mysqldump writes “Dump completed” as the last line. If it is missing, the dump was cut off.')]),
     ('ml', [
        dict(situation='Make a small sample of a dataset for quick experiments.', cmd='seq 1 100000 > data.txt\nhead -n 1000 data.txt > sample.txt && wc -l sample.txt',
             why='A 1000-line sample loads in milliseconds; test the code on it, then run on the full data.')]),
    ]
) + cmdcard_u(['watching a log while you reproduce a problem', 'waiting for a job to finish (“Dump completed”)', 'logs that are rotated: <code>-F</code>'],
               ['the log is in systemd’s journal (use <code>journalctl -f</code>, Lesson 18.2)', 'you need history, not live lines (use tail -n or less)'])(
    'tailf', 'tail -f', 'follow a growing file',
    'Prints the end of the file, then keeps running and prints every new line as soon as it is written. Stop with Ctrl+C.',
    'tail -f FILE   ·   tail -F FILE   ·   tail -f --pid=PID FILE', 'safe',
    [('-f', 'follow the open file (descriptor)', 'most logs'),
     ('-F', 'follow by name, retry if it disappears or is replaced', 'rotated logs (safer default)'),
     ('-n N -f', 'show N old lines, then follow', 'context first'),
     ('--pid=PID', 'stop when that process ends', 'watching one job'),
     ('-s N', 'check every N seconds (when polling)', 'slow network file systems'),
     ('several files', 'follow all, with name headers', 'web + app logs together')],
    dict(cmd='touch live.log\n(for i in 1 2 3; do sleep 0.3; echo "order $i placed" >> live.log; done) &\ntimeout 1.5 tail -f live.log', note='A background job writes three lines; tail -f prints each as it arrives. Here <code>timeout</code> stops it after 1.5 s; at the keyboard you press Ctrl+C.', expect='any'),
    [('sys', [
        dict(situation='Watch only errors, live, from a busy log.', cmd='touch app.log\n(sleep 0.3; echo "INFO ok" >> app.log; echo "ERROR db down" >> app.log; echo "INFO ok" >> app.log) &\ntimeout 1 tail -f app.log | grep --line-buffered ERROR',
             why='The pipe filters the stream; <code>--line-buffered</code> makes grep print each match at once instead of waiting for a full buffer.', expect='any')]),
     ('devops', [
        dict(situation='Follow both the web server and the application log during a deploy.', cmd='sudo tail -F /var/log/nginx/error.log /var/log/myapp/app.log',
             typical='==> /var/log/nginx/error.log <==\n2026/11/06 10:12:01 [error] 812#812: *41 connect() failed ...\n\n==> /var/log/myapp/app.log <==\n2026-11-06 10:12:01 ERROR db pool exhausted',
             why='Several files in one window; -F keeps working when logrotate replaces them during the night.')]),
     ('dba', [
        dict(situation='Wait for a long restore and stop watching automatically when it ends.', cmd='tail -f --pid=$(pgrep -n mysql) restore.log',
             typical='… table 41 of 42 restored\n… table 42 of 42 restored\n(tail exits by itself when the mysql restore process ends)',
             why='--pid ends tail when the process is gone, so a script can continue.')]),
     ('qa', [
        dict(situation='Reproduce a bug while watching the log in a second terminal.', cmd='tail -n 0 -f app.log',
             typical='(empty: only lines written from now on appear)\n2026-11-06 10:20:13 ERROR NullPointer at CartService:88',
             why='<code>-n 0</code> hides old lines, so everything you see belongs to your test.')]),
    ]
) + mistake('tail -f /var/log/app.log     (left running across log rotation)', 'tail -F /var/log/app.log',
            '-f follows the open file; after rotation that is app.log.1, which no longer grows. -F follows the name and reopens the new app.log.') + cmdcard_u(['reading any file longer than one screen', 'searching inside a file interactively', 'viewing command output page by page: <code>… | less</code>'],
               ['in scripts (pagers are interactive)', 'you only need the end (tail is quicker)'])(
    'less', 'less · more', 'pagers: one screen at a time',
    'Show a file (or command output) one screen at a time. <code>less</code> can move forward and back, search, follow and open huge files quickly; <code>more</code> is the older, simpler pager.',
    'less [OPTION]... FILE   ·   more FILE', 'safe',
    [('Space / b', 'next page / previous page', 'reading'),
     ('/word, ?word', 'search forward / backward; n, N = next / previous match', 'finding errors'),
     ('g / G', 'go to the first / last line', 'jump to newest entries'),
     ('50g, 50%', 'go to line 50 / to the middle', 'references'),
     ('F', 'follow like tail -f (Ctrl+C to stop following)', 'live logs in a pager'),
     ('-N', 'show line numbers', 'code, configs'),
     ('-S', 'do not wrap long lines (scroll sideways)', 'wide CSV and logs'),
     ('q', 'quit', 'always')],
    dict(cmd='less --version | head -1\nmore -V 2>&1 | head -1', note='Recorded: both pagers are installed by default on Ubuntu. Their screens are interactive, so the examples below show typical screens.'),
    [('sys', [
        dict(situation='Open a big log at the end and search backwards for the last error.', cmd='less +G /var/log/syslog    then type ?error and Enter',
             typical='Nov  6 10:41:07 server-01 myapp[812]: error: db timeout\nNov  6 10:41:09 server-01 systemd[1]: Started Daily apt download activities.\n/var/log/syslog lines 48211-48250/48250 (END)',
             why='<code>+G</code> starts at the end (newest), <code>?</code> searches upwards: the most recent error first.')]),
     ('data', [
        dict(situation='Browse a wide CSV without wrapped, unreadable lines.', cmd='less -S -N students.csv',
             typical='      1 id,name,city,marks\n      2 1,Asha,Pune,91\n      3 2,Ravi,Delhi,78\n      4 3,Meena,Chennai,85\nstudents.csv (END)',
             why='-S chops long lines (→ scrolls sideways), -N numbers them.')]),
     ('dev', [
        dict(situation='Read long command output page by page.', cmd='git log --stat | less',
             typical='commit 1b341e5…\nAuthor: …\n    Update Hadoop course content\n …\n:',
             why='Any output can be piped into less. git, man and systemctl use less automatically.')]),
     ('devops', [
        dict(situation='Follow a log, then stop to scroll back and search.', cmd='less +F app.log    (Ctrl+C to stop following, F to follow again)',
             typical='2026-11-06 10:44:01 INFO request /cart 200\n2026-11-06 10:44:02 ERROR payment timeout\nWaiting for data... (interrupt to abort)',
             why='Better than tail -f when you also need to look back: one Ctrl+C and you are in normal less with search.')]),
    ]
) + cmdcard_u(['you refer to line numbers in reports or code reviews', 'only some lines should be numbered (pattern)', 'you need a fixed format: 001, 002'],
               ['you need to count lines (use wc -l)', 'a quick look (cat -n is enough)'])(
    'nl', 'nl', 'number lines',
    'Prints a file with line numbers. By default it numbers only non-empty lines; options choose which lines, the number format, width and separator.',
    'nl [OPTION]... [FILE]...', 'safe',
    [('(none) = -bt', 'number non-empty lines', 'code, text'),
     ('-ba', 'number all lines', 'same as cat -n'),
     ('-bn', 'number no lines', 'with -v for a start number in sections'),
     ('-bp REGEX', 'number only lines matching a pattern', 'count ERRORs in place'),
     ('-nln / -nrn / -nrz', 'left / right / right with zeros', '001, 002 …'),
     ('-w N', 'width of the number', 'alignment'),
     ('-s STR', 'separator after the number', '“1: line”'),
     ('-v N / -i N', 'start value / increment', 'continue numbering')],
    dict(cmd='nl app.log', setup=LOG, note='The two empty lines get no number (default -bt), so the ERROR line is number 3, not 5.'),
    [('dev', [
        dict(situation='Numbered code for a review comment, with a clear separator.', cmd="printf 'def f():\\n    return 1\\n' > f.py\nnl -ba -w3 -s': ' f.py",
             why='Width 3 and “: ” make a compact, readable listing.')]),
     ('sys', [
        dict(situation='Number only the ERROR lines of a log, keep the others visible.', setup=LOG, cmd="nl -bp'ERROR' app.log",
             why='Errors get 1, 2…: a quick count while still seeing the context.')]),
     ('data', [
        dict(situation='Zero-padded row numbers for an export.', setup=CSV, cmd='tail -n +2 students.csv | nl -nrz -w3 -s,',
             why='001,1,Asha… : padded numbers sort correctly as text.')]),
    ]
) + cmdcard_u(['checking sizes: lines in a log, rows in a CSV, words in a text', 'monitoring and scripts: “how many errors?”', 'validating a transfer: same line count on both sides'],
               ['the last line has no newline (wc -l counts newlines; it will be one less)', 'you need the length of one line (use awk or ${#var})'])(
    'wc', 'wc', 'word count',
    'Counts lines, words and bytes (and characters with <code>-m</code>) of files or of its input.',
    'wc [-l | -w | -c | -m | -L] [FILE]...', 'safe',
    [('(none)', 'lines, words, bytes, name', 'overview'),
     ('-l', 'lines (newline characters)', 'rows, log entries'),
     ('-w', 'words (separated by spaces)', 'text length'),
     ('-c', 'bytes', 'file size'),
     ('-m', 'characters (UTF-8 aware)', 'Hindi, emoji'),
     ('-L', 'length of the longest line', 'wide lines'),
     ('wc -l < file', 'only the number, no name', 'scripts')],
    dict(cmd='wc app.log\nwc -l app.log\nwc -l < app.log', setup=LOG, note='7 lines, 24 words, 178 bytes. With &lt; the file name is not printed: handy in scripts.'),
    [('data', [
        dict(situation='How many data rows does the CSV have (without the header)?', setup=CSV, cmd='tail -n +2 students.csv | wc -l',
             why='4 students. Compare with the source system after every load.')]),
     ('sys', [
        dict(situation='How many errors are in the log?', setup=LOG, cmd='grep -c ERROR app.log\ngrep ERROR app.log | wc -l',
             why='Both give 2; <code>grep -c</code> is the shorter way (Lesson 6.1).')]),
     ('qa', [
        dict(situation='Text in Hindi: bytes and characters are different.', cmd="printf 'नमस्ते\\n' > hi.txt\nwc -c -m hi.txt",
             why='6 Devanagari characters + newline = 7 characters, but 19 bytes in UTF-8. Database column limits may count either.')]),
     ('devops', [
        dict(situation='Fail a CI step if the build produced no artefacts.', cmd="mkdir -p dist && touch dist/app.whl\nn=$(ls dist | wc -l); [ \"$n\" -gt 0 ] && echo \"ok: $n artefact(s)\" || echo 'FAIL: nothing built'",
             why='A count turns into a yes/no test for scripts.')]),
    ]
) + undo('These commands only read, but two traps exist.', [
    ('A pager or tail -f seems stuck:', 'press <code>q</code> in less/more, <code>Ctrl+C</code> in tail -f. Nothing is changed.'),
    ('cat on a binary file garbled the terminal:', 'type <code>reset</code> (or <code>stty sane</code>) and press Enter, even if you cannot see what you type.'),
    ('cat a b &gt; a:', 'this empties a before cat reads it. Write to a new file: <code>cat a b &gt; all</code>.'),
    ('Typed cat with no file name:', 'cat is waiting for keyboard input. Press <code>Ctrl+D</code> (or Ctrl+C).'),
]) + errors('The errors students see most with these commands. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='cat nofile.txt', meaning='The file does not exist here.', fix='Check the name and folder with <code>ls</code>; use Tab completion.'),
    dict(cmd='mkdir logs\ncat logs', meaning='logs is a folder; cat prints files only.', fix='<code>ls logs</code> to see its content, then <code>cat logs/app.log</code>.'),
    dict(cmd='head -n abc app.log', meaning='-n needs a number.', fix='<code>head -n 20 app.log</code>.'),
    dict(cmd='tail /etc/shadow', meaning='Only root may read the password hash file.', fix='Use <code>sudo</code> only if you really need it, on your own system.'),
    dict(cmd='echo hi > a.txt\ncat a.txt b.txt > a.txt\ncat a.txt', meaning='bash emptied a.txt for &gt; before cat read it; cat also complains about the missing b.txt.', fix='Never redirect into one of the input files; write to a new name.'),
]) + stepper([
    ('1. How big is it?', '<p><code>ls -lh file</code> and <code>wc -l file</code>.</p>', 'Behind the screen: ls reads the inode size; wc reads the data.'),
    ('2. Small? cat it', '<p>Under ~50 lines: <code>cat file</code> (or <code>cat -n</code>).</p>', 'Behind the screen: read() the whole file, write() it to the terminal.'),
    ('3. Big? Look at the edges', '<p><code>head -n 20</code> for the structure, <code>tail -n 50</code> for the latest.</p>', 'Behind the screen: head stops early; tail seeks to the end.'),
    ('4. Need to explore? less', '<p><code>less file</code>, then <code>/ERROR</code>, <code>n</code>, <code>G</code>, <code>q</code>.</p>', 'Behind the screen: less reads only what it displays.'),
    ('5. Need it live? tail -F', '<p><code>tail -F app.log | grep --line-buffered ERROR</code></p>', 'Behind the screen: inotify wakes tail on each write.'),
]) + qc('You need lines 200 to 210 of a file. Which pipeline?', '<code>head -n 210 file | tail -n 11</code> (or <code>sed -n 200,210p file</code>, Lesson 6.4).') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def files(fd_to, note, tone='blue', newfile=False):
    o = label_box(14, 14, 150, 30, ['tail -f', 'holds fd 3'], 'violet', 8.6)
    o += label_box(196, 14, 150, 30, ['name app.log', '→ inode A' if not newfile else '→ inode B (new)'], 'card', 8.6)
    o += label_box(196, 54, 150, 30, ['inode A', 'renamed app.log.1' if newfile else 'growing'], 'green' if fd_to == 'A' else 'card', 8.6)
    if newfile:
        o += label_box(196, 94, 150, 30, ['inode B', 'new app.log, growing'], 'green' if fd_to == 'B' else 'card', 8.6)
    o += arrow(164, 30, 196, 69 if fd_to == 'A' else 109, 'ink3')
    return o + t(180, 150, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ tail -f app.log', ('23:59:58 INFO order 9912', 'out'), ('23:59:59 INFO order 9913', 'out')], title='riya@app-01', size=7.8) + cap('Before midnight: tail -f shows new lines.', '', 'card', y=150, h=34),
       term(14, 16, 332, 116, ['(logrotate at 00:00)', ('mv app.log app.log.1', 'dim'), ('new empty app.log', 'dim')], title='cron', size=7.8) + cap('Midnight: the log is rotated.', '', 'blue', y=150, h=34),
       term(14, 16, 332, 116, ['$ tail -f app.log', ('23:59:59 INFO order 9913', 'out'), ('(nothing more…)', 'err')], title='riya@app-01', size=7.8) + cap('tail -f goes silent.', '', 'red', y=150, h=34),
       term(14, 16, 332, 116, ['$ tail -F app.log', ("tail: 'app.log' has been replaced;", 'acc'), ('following new file', 'acc'), ('00:00:01 INFO order 9914', 'out')], title='riya@app-01', size=7.6) + cap('tail -F notices and reopens.', '', 'green', y=150, h=34),
       (t(180, 30, 'Rule for logs', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• -f follows the FILE it opened', '• -F follows the NAME', '• rotated logs: always -F', '• journald: journalctl -f'])) + cap('One capital letter fixes it.', '', 'green', y=150, h=34))]
behind = [files('A', 'fd 3 points to inode A, the file named app.log.'),
          files('A', 'Rotation: inode A gets the name app.log.1; a new inode B gets app.log.', 'blue', True),
          files('A', 'tail -f still reads inode A, which nobody writes to now.', 'red', True),
          files('B', 'tail -F checks the name, sees inode B, reopens it.', 'green', True),
          files('B', 'Names and inodes are different things (Lesson 10.1).', 'green', True)]
two = anim_two('tail -f vs tail -F at log rotation', 'File descriptor, name and inode',
               'A terminal: before midnight tail -f prints lines; logrotate renames app.log; tail -f stops showing lines; tail -F reports the file was replaced and follows the new one.',
               'tail -f holds a descriptor to inode A; rotation renames A to app.log.1 and creates inode B as app.log; -f keeps reading A, -F reopens the name and reads B.', see, behind,
               ['tail -f prints each new order line.',
                'At midnight logrotate renames app.log and the application starts a new one.',
                'tail -f prints nothing more: it is watching the old, renamed file.',
                'tail -F reports “has been replaced; following new file” and continues.',
                'For logs that rotate, use -F.'],
               ['tail -f keeps the file descriptor of the file it opened (inode A).',
                'Rotation is a rename (Lesson 3.2): inode A keeps its data under a new name.',
                'The application writes to a new inode B now called app.log.',
                '-F re-checks the name regularly and reopens it when the inode changes.',
                'Messages shown are the typical GNU tail messages.'])

h1 = term(14, 14, 332, 100, ['$ wc -l students.csv', ('5 students.csv', 'out')], title='riya@laptop', size=7.8) + cap('5 lines… but how many students?', '', 'card', y=150, h=34)
h2 = term(14, 14, 332, 100, ['$ head -n 1 students.csv', ('id,name,city,marks', 'acc')], title='riya@laptop', size=7.8) + cap('Line 1 is the header.', '', 'blue', y=150, h=34)
h3 = term(14, 14, 332, 100, ['$ tail -n +2 students.csv | wc -l', ('4', 'acc')], title='riya@laptop', size=7.8) + cap('Data rows only: 4 students.', '', 'green', y=150, h=34)
h4 = term(14, 14, 332, 100, ["$ printf 'a\\nb' | wc -l", ('1', 'err')], title='riya@laptop', size=7.8) + cap('No newline after the last line: wc counts 1!', '', 'red', y=150, h=34)
h5 = (t(180, 30, 'Counting rows correctly', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• look at the header: head -n 1', '• skip it: tail -n +2', '• count: wc -l', '• check the last newline: tail -c 1'])) + cap('wc -l counts newline characters.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario', 'How many rows did we load?',
              'Riya must report the number of students in an export. Outputs match real runs.',
              'head, tail and wc on a CSV', 'wc -l counts 5 lines; head shows the header; tail -n +2 piped to wc -l gives 4 rows; a file without a final newline is counted one short.', [h1, h2, h3, h4, h5],
              ['wc -l says 5 lines.',
               'But line 1 is the header, not a student.',
               '<code>tail -n +2</code> skips it: 4 students.',
               'Files from Excel or other tools may lack a newline at the end: wc -l is then one short.',
               'A good habit: look, skip the header, count, check the ending.'],
              hid='scenario-count')

dx = dissect('Layer by layer: why tail is instant on a 2 GB file',
    'Open each layer. The commands below were really run on our build machine on a 2000-line file.', [
    dict(key='cmd', name='tail -n 3 file', sub='what you type',
         why='You want the end only.',
         how='tail gets the file name, so it can open the file itself.',
         impl='GNU coreutils tail.', used='Logs, dumps.',
         cmd='seq 1 2000 > big.txt; tail -n 3 big.txt'),
    dict(key='seek', name='lseek to the end', sub='skip the start',
         why='Reading 2 GB to show 3 lines would be wasteful.',
         how='tail asks for the size and jumps near the end.',
         impl='lseek() system call.', used='tail, less G.',
         cmd="seq 1 2000 > big.txt; stat -c 'size=%s bytes' big.txt"),
    dict(key='back', name='Read backwards', sub='count newlines',
         why='Lines have different lengths.',
         how='It reads blocks from the end until it has found N newlines.',
         impl='Inside tail’s file_lines() function.', used='Every tail -n.',
         cmd='seq 1 2000 > big.txt; tail -c 15 big.txt | od -c | head -2'),
    dict(key='pipe', name='Through a pipe', sub='no seeking',
         why='A pipe has no “end” to jump to.',
         how='cat f | tail must stream all data; tail keeps only the last N lines in memory.',
         impl='Pipes are not seekable.', used='Avoid cat f | tail.',
         cmd='seq 1 2000 | tail -n 2'),
    dict(key='follow', name='-f: keep watching', sub='inotify',
         why='Logs keep growing.',
         how='After printing, tail waits for the kernel to report a change, then reads the new bytes.',
         impl='inotify (or 1-second polling).', used='tail -f, less +F.',
         cmd='touch g.log; (sleep 0.2; echo new >> g.log) & timeout 0.8 tail -n 0 -f g.log', expect='any'),
], hint='From your command down to the disk. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Following a log through rotation, and counting rows correctly</h2>
  <p>Left: what Riya sees (typical messages). Right: names, inodes and the file descriptor tail holds.</p>
''' + two + s1 + dx + hood('Under the hood: tail jumps to the end', 'The real file-related system calls of <code>tail -n 3 big.txt</code> on a 2000-line file (8893 bytes).',
          'tail -n 3 big.txt', 'seq 1 2000 > big.txt', 'openat\\(AT_FDCWD, "big|lseek|read\\(3',
          '<p>tail opens the file, asks where the end is (<code>lseek … SEEK_END</code> = 8893 bytes), jumps to 8192 and reads only the last 701 bytes, where it finds the last three newlines. The first 8 KB are never read. On 2 GB the work is the same: one seek, one small read.</p>', start='openat.*"big.txt"') + qc('Why does <code>tail -f</code> stop showing lines after a log rotation, while <code>tail -F</code> keeps working?', '-f follows the file it opened (now renamed app.log.1); -F follows the name app.log and reopens the new file.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Reading files at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ tail -F', 'prompt'), ('| grep ERROR', 'acc')], title='on-call', size=6.4, step=12),
              '1. Incident response', 'On-call engineers watch logs live while they reproduce or fix a problem.', ['Alert', '*tail -F', 'root cause']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['head -n 5', 'sample'], 'green', 8.6), '2. Data checks',
    'Before loading a file, data engineers look at the header and a few rows, and count rows after loading.', ['File', '*head / wc', 'safe load']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ tail -1', 'prompt'), ('dump.sql', 'acc')], title='dba', size=6.4, step=12),
    '3. Verifying dumps and jobs', 'DBAs check the last line of dumps and job logs for “completed” markers.', ['Backup', '*tail -1', 'verified']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cat -A', '^M ^I $'], 'amber', 8.6), '4. Debugging invisible characters',
    'Windows line endings, tabs and trailing spaces break scripts and CSV loads; cat -A shows them.', ['Weird bug', '*cat -A', 'found']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['less', '/search'], 'violet', 8.6), '5. Reading configs and manuals',
    'Admins read long configs and man pages in less, searching for the setting they need.', ['Config', '*less /word', 'answer']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Quick reading tricks. All really run on our build machine.', [
    dict(level='b', title='Latest 3 entries', scenario='The newest lines of a log.', setup=LOG,
         cmd='tail -n 3 app.log',
         explain='The end of a log = the newest entries.'),
    dict(level='b', title='Rows in a CSV', scenario='Count data rows, not the header.', setup=CSV,
         cmd='tail -n +2 students.csv | wc -l',
         explain='Skip line 1, then count.'),
    dict(level='i', title='Top scorer from a CSV', scenario='Who has the highest marks?', setup=CSV,
         cmd='tail -n +2 students.csv | sort -t, -k4 -nr | head -n 1',
         explain='Skip header, sort by column 4 as numbers (descending), take the first (sort: Lesson 6.2).'),
    dict(level='i', title='Empty lines in a file', scenario='How many blank lines does the log have?', setup=LOG,
         cmd="grep -c '^$' app.log",
         explain='<code>^$</code> = a line with nothing between start and end (Lesson 6.6).'),
    dict(level='a', title='Last line of every file', scenario='Check that every dump ends with “completed”.',
         cmd="for d in a b; do printf 'x\\n-- completed\\n' > $d.sql; done\ntail -q -n 1 *.sql",
         explain='-q hides the file name headers.'),
], extra=build_up('a quick log report', 'Riya builds a one-line report from app.log, one stage at a time.',
    LOG, [
    ('wc -l < app.log', '1. How many lines?'),
    ('grep -c ERROR app.log', '2. How many errors?'),
    ('grep ERROR app.log | tail -n 1', '3. The latest error.'),
    ('echo "lines=$(wc -l < app.log) errors=$(grep -c ERROR app.log) last=\\"$(grep ERROR app.log | tail -n 1 | cut -c12-)\\""', '4. All in one line for a chat message.'),
])) + which('Choosing the right command.', [
    ('Short file', 'cat file', 'All at once.', 'cat on a 2 GB log.'),
    ('Long file', 'less file', 'Scroll and search.', 'Opening it in an editor on a server.'),
    ('Latest log lines', 'tail -n 50 file', 'Instant.', 'cat file | tail.'),
    ('Live log', 'tail -F file', 'Survives rotation.', 'tail -f overnight.'),
    ('CSV without header', 'tail -n +2 f.csv', 'From line 2.', 'tail -n 2 (last two lines).'),
    ('Line range', 'head -n 210 | tail -n 11', 'Fast.', 'Scrolling by hand.'),
    ('Count rows', 'wc -l < file', 'Just the number.', 'Forgetting the header.'),
    ('Hidden characters', 'cat -A file', 'Shows ^M ^I $.', 'Guessing.'),
]) + keys('Keys inside less (and man).', [
    ('Space / b', 'page down / up', 'less big.log'),
    ('/word  ?word', 'search forward / backward', '/ERROR'),
    ('n / N', 'next / previous match', 'n'),
    ('g / G', 'first / last line', 'G'),
    ('F', 'follow (like tail -f); Ctrl+C to stop', 'F'),
    ('-S  -N', 'chop long lines / line numbers (type inside less too)', '-S'),
    ('h', 'help screen with all keys', 'h'),
    ('q', 'quit', 'q'),
]) + scriptit('log-summary.sh', 'A small report on any log file: size, lines, errors, warnings and the last error. (Lesson 12.5 explains scripts; grep is Lesson 6.1.)',
'''#!/bin/bash
log=${1:-app.log}
printf '2026-11-06 10:00:01 INFO start\\n2026-11-06 10:00:05 ERROR db timeout\\n2026-11-06 10:00:07 WARN slow\\n2026-11-06 10:00:09 ERROR disk full\\n' > "$log"   # demo data
[ -r "$log" ] || { echo "cannot read $log" >&2; exit 1; }
echo "file:     $log ($(wc -c < "$log") bytes)"
echo "lines:    $(wc -l < "$log")"
echo "errors:   $(grep -c ERROR "$log")"
echo "warnings: $(grep -c WARN "$log")"
echo "last error:"
grep ERROR "$log" | tail -n 1''',
'<p><code>[ -r "$log" ]</code> checks that the file exists and is readable before anything else.</p>') + puzzle_answer('<code>tail -f</code> follows the <b>file it opened</b> (its inode). At midnight logrotate renamed that file to app.log.1 and the application started writing to a <b>new</b> app.log. tail -f kept watching the renamed file, which no longer grows, so it showed nothing. <code>tail -F</code> (capital F) follows the <b>name</b>: it notices that app.log is now a different file and reopens it.') + qc('Your script must stop following a log when the backup process (PID 812) ends. Which tail option?', '<code>tail -f --pid=812 backup.log</code>') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../04-wildcards-and-globbing/">Lesson 3.4</a>: wildcards, used in <code>head -n 1 *.csv</code>.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
