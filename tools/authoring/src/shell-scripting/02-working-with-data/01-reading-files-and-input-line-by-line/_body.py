import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# Riya's server list and user list: messy on purpose (spaces, tabs, backslashes, comments, no final newline)
SS = r"""rm -rf ~/ops; mkdir -p ~/ops/data; cd ~/ops
printf '# servers to patch\nweb01  10.0.1.11   prod\nweb02  10.0.1.12   prod\n\ndb01   10.0.2.21   prod\n  test01 10.0.9.5  test\nbuild\\01 10.0.3.7 ci' > data/hosts.txt
printf 'name,dept,city\nAsha Rao,Data,Pune\nRavi K,Ops,"New Delhi"\nMeera Iyer,Data,Mumbai\n' > data/users.csv
printf 'Sales Q3.xlsx\nnotes.txt\nold report.pdf\n' > data/files.txt"""

HOOK = hook('Riya has to patch every server in <code>hosts.txt</code>, create accounts for every person in <code>users.csv</code>, and act on a list of file names that contain spaces. Each job is the same pattern: <b>read a file line by line and do something with each line</b>. It is also where shell scripts break most often: a <code>for</code> loop over <code>$(cat file)</code> splits “Sales Q3.xlsx” into two words, a backslash in a name disappears, the last line is silently skipped because the file has no final newline, and an <code>ssh</code> inside the loop swallows the rest of the file. This lesson teaches the one loop that gets all of this right, <code>while IFS= read -r line</code>, and its friends <code>mapfile</code> and field splitting with <code>IFS</code>.',
    ['read a file line by line correctly with while IFS= read -r, including the last line without a newline',
     'split lines into fields with IFS and read -r a b c, and read CSV-like data into variables',
     'load a whole file into an array with mapfile / readarray',
     'avoid the classic traps: for over $(cat), lost backslashes, trimmed spaces, subshell variables, and commands that eat stdin'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three lists'),
    ('decide', 'Which loop?', 2, 'the quick chart'),
    ('definition', 'read, IFS, mapfile', 5, 'simple meaning + 4 depths'),
    ('types', 'Ways to read', 4, 'compared'),
    ('commands', 'Step by step', 15, 'real files, real traps'),
    ('animation', 'See it happen', 4, 'read splits a line'),
    ('run', 'Run on your PC', 3, 'your own lists'),
    ('lab', 'Practice lab', 8, 'process a host list'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('I want to… → use', [
    ('do something for each line', 'while IFS= read -r line; do …; done < file', 'the safe loop'),
    ('split each line into fields', 'while read -r name ip env; do', 'IFS default: spaces/tabs'),
    ('split on commas', 'while IFS=, read -r a b c; do', 'simple CSV'),
    ('have all lines in an array', 'mapfile -t arr < file', 'random access'),
    ('read command output', 'while read -r x; do …; done < <(cmd)', 'keeps variables'),
    ('ask the user', 'read -rp "Name: " name', 'interactive'),
])

cmap = concept_map(
    [('1.4', 'Template', 'safe structure'), ('L:12.9', 'Loops', 'while, for'), ('L:12.13', 'Arrays', 'indexed')],
    ['while IFS= read -r line', 'the last line without a newline', 'IFS and field splitting', 'skipping comments and blank lines', 'mapfile / readarray', 'process substitution < <(cmd)', 'stdin traps: ssh -n, < /dev/null'],
    [('2.2', 'Parsing CSV, logs, config', 'real formats'), ('2.4', 'sed, awk, jq', 'when Bash is slow'), ('4.3', 'Provisioning', 'users from a file'), ('4.2', 'Log monitor', 'tail -f | read')],
    'The one loop that never loses a line, a space or a backslash.')

sc = (term(20, 14, 316, 156, ['$ for f in $(cat files.txt); do echo "[$f]"; done', ('[Sales] [Q3.xlsx] [notes.txt] …', 'err'), '$ while IFS= read -r f; do echo "[$f]"; done < files.txt', ('[Sales Q3.xlsx]', 'out'), ('[notes.txt]', 'out'), ('[old report.pdf]', 'acc')], title='riya@laptop: ~/ops/data', prompt='$', size=6.2, step=18)
      + t(352, 36, 'One line = one item:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['IFS=  keeps spaces', '-r   keeps \\\\', '< file  at done', '|| [[ -n $line ]]', '  last line'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three lists, four ways to lose data</h2>
  <div class="story">
''' + puzzle('Riya’s first loop, <code>for h in $(cat hosts.txt)</code>, runs once per <i>word</i>, not per line: 21 rounds for 7 lines. Her second, <code>while read line</code>, turns <code>build\\01</code> into <code>build01</code>, trims the leading spaces of <code>test01</code>, and never prints the last line at all. Her third, <code>cat hosts.txt | while read …; do count=$((count+1)); done</code>, ends with <code>count</code> still 0. Why does each of these happen?') + '''
    <p class="narration">In <code>~/ops/data</code> (every run in this lesson is real). <code>hosts.txt</code> is messy on purpose: a comment, a blank line, extra spaces, a tab-free indent, a backslash, and no newline after the last line, exactly like files people really send you.</p>
''' + scene('A terminal: a for loop over cat splits Sales Q3.xlsx into two items; a while IFS= read -r loop prints each file name whole.', sc,
            'Read <tspan font-weight="700" class="s-acc">lines</tspan>, not words.') + '''
K> Why does for split “Sales Q3.xlsx”?
A> <code>$(cat file)</code> becomes one long string, and the unquoted expansion is split on <i>any</i> space, tab or newline. <code>for</code> never knew there were lines. <code>read</code> works the other way round: it reads exactly one line each time it is called.
R> And the missing last line, the lost backslash?
A> Two small defaults of <code>read</code>. We switch both off, and the loop becomes the one you can use for the rest of your career.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A file flows into a while loop through the redirection at done; read takes one line per round and puts it into the variable line, until the end of the file.">'
       + ''.join(label_box(14, 20 + i * 34, 170, 28, [s], 'card', 8.2) for i, s in enumerate(['web01  10.0.1.11  prod', 'web02  10.0.1.12  prod', 'db01   10.0.2.21  prod', '(end of file)']))
       + arrow(190, 80, 250, 80) + label_box(256, 50, 150, 60, ['read -r line', 'one line per round'], 'blue', 9)
       + arrow(412, 80, 470, 80) + label_box(476, 50, 150, 60, ['loop body', 'uses "$line"'], 'green', 9)
       + t(330, 160, 'while IFS= read -r line; do …; done < hosts.txt', 9.2, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Reading line by line at four depths', [
    ('v', 'No jargon: a queue at a counter', '      <p>People come to the counter one at a time; the clerk serves exactly one, then calls “next”. <code>read</code> is the clerk; each line is one person.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>while IFS= read -r line; do echo "$line"; done &lt; file</code></li>
        <li><code>while read -r name ip env; do …; done &lt; hosts.txt</code> (fields)</li>
        <li><code>while IFS=, read -r a b c; do …; done &lt; file.csv</code></li>
        <li><code>mapfile -t lines &lt; file; echo "${#lines[@]}"</code></li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li><code>IFS=</code> (empty, only for this read) keeps leading and trailing spaces; <code>-r</code> keeps backslashes.</li>
        <li><code>read</code> returns non-zero at end of file <i>even if it read a last line without a newline</i>; <code>|| [[ -n $line ]]</code> handles it.</li>
        <li>With several variables, the <b>last</b> one gets the rest of the line: <code>read -r name rest</code>.</li>
        <li>A pipe <code>cmd | while …</code> runs the loop in a subshell: variables set inside are lost. Use <code>done &lt; file</code> or <code>done &lt; &lt;(cmd)</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: read() one byte at a time', '''      <ul>
        <li>On a pipe, Bash’s read builtin calls <code>read(2)</code> one byte at a time (it must not consume bytes after the newline, which belong to the next command); on a regular file it reads a block and seeks back. That is why huge files are slow in Bash loops: use awk for millions of lines.</li>
        <li>Every command inside the loop inherits the loop’s stdin (the file). <code>ssh</code>, <code>ffmpeg</code>, <code>read</code> without redirection can swallow the remaining lines: give them <code>&lt; /dev/null</code> (<code>ssh -n</code>) or read from another file descriptor (<code>read -u 3</code>).</li>
        <li>Field splitting with IFS whitespace collapses runs of spaces and tabs and trims the ends; a non-whitespace IFS like <code>,</code> does not collapse, so empty fields survive (<code>a,,c</code> → 3 fields).</li>
        <li><code>mapfile</code> (Bash 4) reads all lines into an array in one call; <code>-t</code> strips the newlines, <code>-s N</code> skips N lines, <code>-n N</code> reads at most N.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>read, IFS and mapfile</h2>
''' + def_block(
    '<b>read</b> is a Bash built-in that reads one line from standard input and assigns it to one or more variables, splitting it into fields using the characters in <b>IFS</b> (the Internal Field Separator, by default space, tab and newline). In a <code>while</code> loop with the file redirected at <code>done</code>, it processes a file line by line. <b>mapfile</b> (also called readarray) reads all lines of its input into an indexed array.',
    'read takes one line per call; IFS decides where fields split; mapfile takes them all.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('read -r', 'Keep backslashes.'),
    ('IFS=', 'Keep leading/trailing spaces.'),
    ('IFS=,', 'Split fields on commas.'),
    ('Field', 'One piece of a split line.'),
    ('mapfile -t', 'File → array, no newlines.'),
    ('< <(cmd)', 'Process substitution as input.'),
    ('EOF', 'End of file.'),
    ('Subshell', 'A child shell; its variables vanish.'),
]) + '\n' + names('Where the names come from.', [
    ('read', 'read a line', 'Bourne shell, 1979.'),
    ('IFS', 'Internal Field Separator', 'Bourne shell.'),
    ('-r', 'raw', 'No backslash escapes.'),
    ('mapfile', 'map a file to an array', 'Bash 4.0, 2009.'),
    ('readarray', 'same as mapfile', 'Synonym.'),
    ('<(…)', 'process substitution', 'ksh/bash.'),
    ('here-string <<<', 'a string as stdin', 'ksh/bash.'),
    ('/dev/null', 'empty input', 'The black hole.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Safe loop', '<code>while IFS= read -r line</code>'),
    ('Last line', '<code>|| [[ -n $line ]]</code>'),
    ('Fields', '<code>read -r a b rest</code>'),
    ('CSV-ish', '<code>IFS=, read -r a b c</code>'),
    ('All lines', '<code>mapfile -t arr &lt; f</code>'),
    ('Keep vars', '<code>done &lt; &lt;(cmd)</code>'),
]) + '\n' + lv + didyou('ShellCheck warns about almost every mistake in this lesson: SC2162 (“read without -r will mangle backslashes”), SC2013 (“to read lines rather than words, pipe/redirect to a while read loop”) and SC2031 (a variable modified in a subshell).') + '''
EXAM> “How do you read a file line by line in Bash?” → while IFS= read -r line; do … "$line" …; done < file, with || [[ -n $line ]] to keep a last line that has no newline.
''' + qc('Why put < file after done and not cat file | before while?', 'With the redirect, the loop runs in the current shell, so variables set inside survive; a pipe runs it in a subshell.') + mistake('for line in $(cat hosts.txt); do',
    'while IFS= read -r line; do …; done < hosts.txt',
    'for splits on every space and expands wildcards: one “line” becomes many words.') + mistake('ssh "$host" uptime   inside a while read loop',
    'ssh -n "$host" uptime   (or < /dev/null)',
    'ssh reads the loop’s stdin, swallowing the remaining lines: only the first host is processed.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Ways to read a file in Bash</h2>
''' + table(['Method', 'Unit', 'Spaces kept', 'Backslash kept', 'Last line w/o newline', 'Variables survive'], [
    ['<code>for x in $(cat f)</code>', 'word', 'no', 'yes', 'yes', 'yes'],
    ['<code>while read line</code>', 'line', 'trimmed', 'no', 'lost', 'yes'],
    ['<code>while IFS= read -r line</code>', 'line', 'yes', 'yes', 'lost', 'yes'],
    ['… <code>|| [[ -n $line ]]</code>', 'line', 'yes', 'yes', 'yes', 'yes'],
    ['<code>cat f | while …</code>', 'line', 'yes', 'yes', 'lost', '<b>no</b>'],
    ['<code>mapfile -t arr &lt; f</code>', 'line → array', 'yes', 'yes', 'yes', 'yes'],
], minw=640) + table(['IFS value', 'Splits on', 'Empty fields'], [
    ['default (space tab newline)', 'runs of whitespace, ends trimmed', 'impossible'],
    ['<code>IFS=,</code>', 'each comma', 'kept: <code>a,,c</code> = 3 fields'],
    ['<code>IFS=:</code>', 'each colon', '/etc/passwd'],
    ['<code>IFS=$\'\\t\'</code>', 'each tab', 'TSV files'],
    ['<code>IFS=</code> (empty)', 'nothing', 'whole line in one variable'],
], minw=420) + qc('Which method keeps everything, including a last line without a newline?', 'while IFS= read -r line || [[ -n $line ]], or mapfile -t.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>The safe loop, fields, arrays and the traps</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops/data</code>: <code>hosts.txt</code> (7 lines, messy, no final newline), <code>users.csv</code> and <code>files.txt</code> (names with spaces).</p>
''' + cmdcard_u(['every “for each line” job'], ['for over $(cat)'])(
    'loop', 'while IFS= read -r line || [[ -n $line ]]; do … done < file', 'the safe loop',
    'Three details make it safe: <code>IFS=</code> keeps spaces at the ends, <code>-r</code> keeps backslashes, and <code>|| [[ -n $line ]]</code> still processes a last line that has no newline. The file is redirected at <code>done</code>, so the loop runs in the current shell.',
    'while IFS= read -r line || [[ -n $line ]]; do printf \'%s\\n\' "$line"; done < hosts.txt', 'safe',
    [('IFS=', 'no trimming', 'spaces'),
     ('-r', 'raw', 'backslashes'),
     ('|| [[ -n $line ]]', 'last line', 'no newline'),
     ('< file at done', 'input', 'same shell'),
     ('"$line"', 'quoted', 'always'),
     ("printf '%s\\n'", 'safe print', 'not echo')],
    dict(setup=SS, cmd="cd ~/ops/data\nn=0; while read line; do n=$((n+1)); done < hosts.txt; echo \"naive loop: $n lines\"\nn=0; while IFS= read -r line || [[ -n $line ]]; do n=$((n+1)); last=$line; done < hosts.txt; echo \"safe loop: $n lines, last: [$last]\"\nwc -l < hosts.txt", note='wc -l counts newlines (6): the 7th line has none. The naive loop loses it; the safe loop keeps it, backslash included.'),
    [('dev', [
        dict(situation='Spaces and backslashes, side by side.', setup=SS, cmd="cd ~/ops/data; sed -n '6,7p' hosts.txt > two.txt; echo >> two.txt\nwhile read line; do echo \"naive: [$line]\"; done < two.txt\nwhile IFS= read -r line; do echo \"safe:  [$line]\"; done < two.txt", why='Leading spaces and \\ survive only in the safe loop.')]),
    ],
    anat=anatomy([('while', 'cmd', 'repeat while read succeeds'), ('IFS=', 'opt', 'only for this read'), ('read -r line', 'arg', 'one raw line'), ('< file', 'arg', 'after done')], 'IFS= before read applies to read only.')
) + cmdcard_u(['lists with columns'], ['awk-sized jobs on huge files'])(
    'fields', 'read -r a b c · comments · blank lines', 'fields, comments and blank lines',
    'Give <code>read</code> several variable names and it splits the line on IFS (spaces and tabs by default, runs collapsed); the last variable gets everything left. Skip comments and blank lines with a <code>case</code> or <code>[[ ]]</code> at the top of the loop.',
    'while read -r name ip env || [[ -n $name ]]; do [[ -z $name || $name == \\#* ]] && continue; …', 'safe',
    [('read -r a b c', '3 fields', 'columns'),
     ('read -r a rest', 'first + rest', 'commands'),
     ('[[ -z $a ]]', 'blank line', 'continue'),
     ('[[ $a == \\#* ]]', 'comment', 'continue'),
     ('_ (underscore)', 'ignore a field', 'read -r a _ c'),
     ('IFS=$\'\\t\'', 'tabs only', 'TSV')],
    dict(setup=SS, cmd="cd ~/ops/data\nwhile read -r name ip env || [[ -n $name ]]; do\n  [[ -z $name || $name == \\#* ]] && continue\n  printf '%-9s %-11s %s\\n' \"$name\" \"$ip\" \"$env\"\ndone < hosts.txt", note='The comment and the blank line are skipped; the extra spaces between columns do not matter; build\\01 keeps its backslash.'),
    [('sys', [
        dict(situation='Only production hosts, counted.', setup=SS, cmd="cd ~/ops/data; prod=0; while read -r name ip env || [[ -n $name ]]; do [[ $env == prod ]] && prod=$((prod+1)); done < hosts.txt; echo \"production hosts: $prod\"", why='Variables survive: no pipe.')]),
    ]
) + cmdcard_u(['simple CSV/TSV/passwd-like files'], ['CSV with quoted commas (Lesson 2.2)'])(
    'ifs', 'IFS=, read -r · IFS=: · header skip', 'other separators',
    'Set IFS just for <code>read</code>: <code>IFS=, read -r a b c</code>. With a non-space separator every comma counts, so empty fields are kept. Skip a header line with one <code>read</code> before the loop, or <code>tail -n +2</code>.',
    "{ read -r _; while IFS=, read -r name dept city; do …; done; } < users.csv", 'safe',
    [('IFS=,', 'commas', 'CSV'),
     ('IFS=:', 'colons', '/etc/passwd'),
     ('read -r _', 'skip header', 'before loop'),
     ('{ …; } < f', 'one input', 'header + loop'),
     ('a,,c', '3 fields', 'empties kept'),
     ('"New Delhi"', 'quotes stay', 'Lesson 2.2')],
    dict(setup=SS, cmd="cd ~/ops/data\n{ read -r header; while IFS=, read -r name dept city; do echo \"$dept: $name ($city)\"; done; } < users.csv\nwhile IFS=: read -r user _ uid _ _ home shell; do if [[ $user == root ]]; then echo \"root: uid=$uid home=$home shell=$shell\"; fi; done < /etc/passwd", note='The quotes around New Delhi stay: real CSV needs more care (next lesson).'),
    [('data', [
        dict(situation='Empty fields survive with IFS=,', cmd="IFS=, read -r a b c <<< 'x,,z'; echo \"a=[$a] b=[$b] c=[$c]\"; read -r a b c <<< 'x  z'; echo \"spaces: a=[$a] b=[$b] c=[$c]\"", why='Comma: b is empty. Spaces: runs collapse, so z moves to b.')]),
    ]
) + cmdcard_u(['you need all lines at once', 'counting, indexing'], ['very large files'])(
    'mapfile', 'mapfile -t arr < file · ${arr[@]} · ${#arr[@]}', 'the whole file into an array',
    '<code>mapfile -t lines &lt; file</code> reads every line into <code>lines[0]</code>, <code>lines[1]</code>…; <code>-t</code> removes the newlines. It keeps spaces, backslashes and the last line. Then loop with <code>for l in "${lines[@]}"</code>, index directly, or count with <code>${#lines[@]}</code>.',
    'mapfile -t files < files.txt; for f in "${files[@]}"; do …; done', 'safe',
    [('-t', 'strip newline', 'always'),
     ('-s 1', 'skip header', 'CSV'),
     ('-n 10', 'first 10', 'limits'),
     ('${#arr[@]}', 'count', 'size'),
     ('${arr[-1]}', 'last line', 'Bash 4.3+'),
     ('< <(cmd)', 'from a command', 'filtered input')],
    dict(setup=SS, cmd="cd ~/ops/data\nmapfile -t files < files.txt\necho \"${#files[@]} files; second: [${files[1]}]\"\nfor f in \"${files[@]}\"; do echo \"would back up: $f\"; done\nmapfile -t prod < <(grep -w prod hosts.txt)\necho \"prod lines: ${#prod[@]}; last host line: [${prod[-1]}]\"", note='No word splitting anywhere: "Sales Q3.xlsx" stays one item.'),
    [('devops', [
        dict(situation='Read a list, then loop with the index.', setup=SS, cmd="cd ~/ops/data; mapfile -t -s 1 users < users.csv; for i in \"${!users[@]}\"; do echo \"$((i+1)). ${users[i]%%,*}\"; done", why='-s 1 skips the header; ${!arr[@]} gives the indexes.')]),
    ]
) + cmdcard_u(['loops over command output', 'remote commands in loops'], ['pipes when you need the variables'])(
    'traps', 'cmd | while (subshell) · < <(cmd) · ssh -n · read -u 3', 'the two big traps',
    '<b>Trap 1:</b> <code>cmd | while …</code> runs the loop in a subshell, so variables set inside vanish; use <code>done &lt; &lt;(cmd)</code>. <b>Trap 2:</b> commands inside the loop share its stdin; <code>ssh</code> (and others) read it and swallow the rest of the file. Give them <code>&lt; /dev/null</code>, use <code>ssh -n</code>, or read the file on fd 3.',
    'while read -r h _; do ssh -n "$h" uptime; done < <(grep prod hosts.txt)', 'safe',
    [('| while', 'subshell', 'vars lost'),
     ('< <(cmd)', 'same shell', 'vars kept'),
     ('shopt -s lastpipe', 'last pipe part in shell', 'scripts only'),
     ('cmd < /dev/null', 'no stdin', 'inside loops'),
     ('ssh -n', 'same for ssh', 'remote'),
     ('read -u 3 … 3< f', 'other fd', 'interactive bodies')],
    dict(setup=SS, cmd="cd ~/ops/data\ncount=0; grep -w prod hosts.txt | while read -r h _; do count=$((count+1)); done; echo \"with a pipe: count=$count\"\ncount=0; while read -r h _; do count=$((count+1)); done < <(grep -w prod hosts.txt); echo \"with < <(...): count=$count\"\nslurp() { cat > /dev/null; }   # stands in for ssh: it reads stdin\nwhile read -r h _; do echo \"patching $h\"; slurp; done < <(grep -w prod hosts.txt)\necho '--- with < /dev/null:'\nwhile read -r h _; do echo \"patching $h\"; slurp < /dev/null; done < <(grep -w prod hosts.txt)", note='slurp reads stdin like ssh does: without < /dev/null only the first host is patched.'),
    [('sys', [
        dict(situation='Reading the file on fd 3.', setup=SS, cmd="cd ~/ops/data; while read -r -u 3 f; do echo \"file: $f\"; slurp(){ cat > /dev/null; }; slurp; done 3< files.txt", why='stdin stays free for the body; the list comes from fd 3.')]),
    ]
) + undo('Reading never changes files; mistakes are in what the loop does with the lines. Make the body safe:', [
    ('Wrong items processed:', 'print first: run the loop with <code>echo</code> in front of the real command.'),
    ('Only the first host done:', 'a command ate stdin; add <code>&lt; /dev/null</code> or <code>ssh -n</code>, rerun.'),
    ('Counter is 0:', 'the loop was in a pipe; switch to <code>done &lt; &lt;(cmd)</code>.'),
    ('Windows line endings (\\r):', 'strip with <code>line=${line%$\'\\r\'}</code> or <code>dos2unix</code> first.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(setup=SS, cmd="cd ~/ops/data && for f in $(cat files.txt); do ls -- \"$f\"; done", meaning='for splits names on spaces: “Sales”, “Q3.xlsx”… do not exist.', fix='while IFS= read -r f; do …; done < files.txt'),
    dict(setup=SS, cmd="cd ~/ops/data && while read -r line; do :; done < nosuch.txt", meaning='The redirect at done fails before the loop starts.', fix='Check [[ -r $file ]] first.'),
    dict(cmd="printf 'web01\\r\\nweb02\\r\\n' > win.txt; while IFS= read -r h; do echo \"$(printf %q \"$h\") has ${#h} chars\"; done < win.txt", meaning='Windows CRLF: each name ends in an invisible \\r (6 chars, not 5); ssh would fail with “hostname not found”.', fix="line=${line%$'\\r'} or dos2unix."),
]) + qc('Your loop over hosts processes only the first host. Most likely cause?', 'A command in the body (ssh, ffmpeg, read) consumed the loop’s stdin.') + '''
'''
cards = cards + '</section>\n'

def rd(k):
    o = t(180, 18, '"  test01 10.0.9.5  test"', 9.4, 'ink2', bold=True)
    rows = [('read line', 'test01 10.0.9.5  test (trimmed)', 'amber'), ('IFS= read -r line', '"  test01 10.0.9.5  test"', 'green'), ('read -r name ip env', 'name=test01 ip=10.0.9.5 env=test', 'blue'), ('read -r name rest', 'name=test01 rest="10.0.9.5  test"', 'violet')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 7.8)
    return o
see_cmds = [['$ read line', ('leading spaces gone', 'err')], ['$ IFS= read -r line', ('kept exactly', 'out')], ['$ read -r name ip env', ('three fields', 'out')], ['$ read -r name rest', ('rest = the remainder', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@laptop: ~/ops/data', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Default.', 'Raw.', 'Fields.', 'Rest.'])]
two = anim_two('One line, four reads', 'Behind the screen: how read assigns',
               'A terminal reads the same indented line four ways.',
               'Rows show what each read form stores.', see, [rd(k) for k in range(4)],
               ['default.', 'raw.', 'fields.', 'rest.'], ['read', 'raw', 'fields', 'rest'])

def sub(k):
    o = t(180, 18, 'grep prod | while read …', 9.6, 'ink2', bold=True)
    o += label_box(14, 36, 160, 46, ['main shell', 'count=0'], 'blue', 8.6) + label_box(186, 36, 160, 46, ['subshell (pipe)', ['count=0', 'count=3', 'count=3', 'gone'][k]], ['card', 'amber', 'red', 'card'][k], 8.6)
    o += t(180, 112, ['the loop starts in a child shell', 'it counts to 3 there', 'the child exits: its variables vanish', 'main shell still says 0'][k], 9.2, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Why the counter stays 0',
              'A pipe puts the loop in a subshell.', 'subshell variables', 'Two boxes: the main shell and the pipe’s subshell.', [sub(k) for k in range(4)],
              ['start.', 'count.', 'exit.', 'result.'], hid='scenario-subshell')

dx = dissect('Layer by layer: from file to variables',
    'Each layer has a real command from our build machine.', [
    dict(key='bytes', name='Bytes', sub='lines end in \\n', why='What read sees.', how='Newline = end of line.', impl='od.', used='Debugging.',
         setup=SS, cmd="cd ~/ops/data; tail -c 22 hosts.txt | od -c | head -2"),
    dict(key='read', name='read', sub='one line', why='Line unit.', how='Until \\n or EOF.', impl='Built-in.', used='Loops.',
         setup=SS, cmd="cd ~/ops/data; IFS= read -r first < hosts.txt; echo \"first line: [$first]\""),
    dict(key='split', name='IFS split', sub='fields', why='Columns.', how='IFS chars.', impl='Word splitting.', used='read a b c.',
         cmd="line='db01   10.0.2.21   prod'; read -r h ip env <<< \"$line\"; echo \"h=$h ip=$ip env=$env\""),
], hint='Bytes → read → fields. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How read assigns, and the subshell trap</h2>
''' + two + s1 + dx + qc('In read -r a b with the line “x y z”, what is b?', '“y z”: the last variable gets the rest.') + '''
</section>
'''

VAR = variations('Sixteen more line-by-line patterns. All were really run on our build machine.', [
    ('Loops', [
        dict(title='Number the lines', setup=SS, cmd="cd ~/ops/data; n=0; while IFS= read -r l; do printf '%2d  %s\\n' $((++n)) \"$l\"; done < files.txt", why='Like nl, in Bash.'),
        dict(title='Read from a here-string', cmd="while read -r w; do echo \"<$w>\"; done <<< $'alpha\\nbeta'", why='Quick tests without a file.'),
        dict(title='Read command output, keep a total', setup=SS, cmd="cd ~/ops/data; total=0; while read -r size _; do total=$((total+size)); done < <(wc -c *.txt *.csv | grep -v total); echo \"total bytes: $total\"", why='< <( ) keeps total.'),
        dict(title='Stop at a marker line', cmd="while IFS= read -r l; do [[ $l == END ]] && break; echo \"$l\"; done <<< $'a\\nb\\nEND\\nc'", why='break.'),
        dict(title='Two files in parallel', setup=SS, cmd="cd ~/ops/data; printf 'Pune\\nDelhi\\n' > a.txt; printf '450\\n800\\n' > b.txt; while IFS= read -r c && IFS= read -r v <&3; do echo \"$c=$v\"; done < a.txt 3< b.txt", why='fd 3 for the second file.'),
        dict(title='Strip Windows \\r', cmd="printf 'web01\\r\\n' | while IFS= read -r h; do h=${h%$'\\r'}; echo \"[$h] ${#h} chars\"; done", why='Remove the trailing CR.'),
    ]),
    ('Fields', [
        dict(title='Last field only', setup=SS, cmd="cd ~/ops/data; while read -r -a f || (( ${#f[@]} )); do [[ ${#f[@]} -gt 0 && ${f[0]} != \\#* ]] && echo \"${f[-1]}\"; done < hosts.txt | sort | uniq -c", why='read -a: fields into an array.'),
        dict(title='Tab-separated', cmd="printf 'a b\\tc d\\n' | while IFS=$'\\t' read -r x y; do echo \"x=[$x] y=[$y]\"; done", why='Spaces inside fields survive.'),
        dict(title='key=value lines', cmd="while IFS== read -r k v; do echo \"key=$k value=$v\"; done <<< $'host=db01\\nport=5432'", why='IFS== splits on =.'),
        dict(title='Ignore middle fields', setup=SS, cmd="cd ~/ops/data; grep -v '^#' hosts.txt | while read -r name _ env; do [[ -n $name ]] && echo \"$name:$env\"; done", why='_ discards a field.'),
    ]),
    ('mapfile', [
        dict(title='First two lines only', setup=SS, cmd="cd ~/ops/data; mapfile -t -n 2 a < files.txt; printf '[%s]\\n' \"${a[@]}\"", why='-n.'),
        dict(title='Skip the header', setup=SS, cmd="cd ~/ops/data; mapfile -t -s 1 rows < users.csv; echo \"${#rows[@]} data rows\"", why='-s.'),
        dict(title='Reverse order', setup=SS, cmd="cd ~/ops/data; mapfile -t a < files.txt; for (( i=${#a[@]}-1; i>=0; i-- )); do echo \"${a[i]}\"; done", why='Index access.'),
        dict(title='Array from a command', cmd="mapfile -t nums < <(seq 3 3 12); echo \"${nums[*]} (count ${#nums[@]})\"", why='Process substitution.'),
    ]),
    ('Interactive read', [
        dict(title='Prompt with a default', cmd="read -r -p 'City [Pune]: ' city <<< ''; echo \"city=${city:-Pune}\"", why='<<< "" simulates pressing Enter.'),
        dict(title='Timeout', cmd="read -r -t 1 ans < <(sleep 2); echo \"status $? (timed out), answer=[${ans:-none}]\"", why='-t seconds; status > 128 on timeout.', expect='any'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Line-by-line reading at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['hosts', 'patching'], 'blue', 8.6), '1. Fleet operations',
              'Loop over a host list and run a command on each with ssh -n; skip comments so the list doubles as documentation.', ['hosts.txt', '*while read', 'ssh -n']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['users', 'onboarding'], 'green', 8.6), '2. Bulk onboarding',
    'HR exports a CSV; a script reads each row and creates the account, home folder and group (Lesson 4.3).', ['CSV', '*IFS=,', 'useradd']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['files', 'spaces'], 'amber', 8.6), '3. File lists from users',
    'Lists of report names with spaces and brackets are processed safely with read -r and quotes.', ['list', '*read -r', '"$f"']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['logs', 'tail -f'], 'violet', 8.6), '4. Watching logs live',
    'tail -F app.log | while read -r line reacts to each new line, e.g. alerting on ERROR (Lesson 4.2).', ['tail -F', '*read', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['config', 'key=value'], 'red', 8.6), '5. Simple config files',
    'Reading key=value files with IFS== instead of sourcing them avoids running code hidden in a config.', ['file', '*IFS==', 'variables']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful loops. All really run on our build machine.', [
    dict(level='b', title='Print each line safely', scenario='Check a list.', setup=SS, cmd="cd ~/ops/data; while IFS= read -r f; do printf '[%s]\\n' \"$f\"; done < files.txt", explain='The safe loop.'),
    dict(level='b', title='Count real lines', scenario='Including the last.', setup=SS, cmd="cd ~/ops/data; mapfile -t a < hosts.txt; echo ${#a[@]}", explain='mapfile counts 7; wc -l says 6.'),
    dict(level='i', title='Host names only', scenario='Patch list.', setup=SS, cmd="cd ~/ops/data; while read -r h _ || [[ -n $h ]]; do [[ -z $h || $h == \\#* ]] || echo \"$h\"; done < hosts.txt | paste -sd' '", explain='Skip comments and blanks.'),
    dict(level='i', title='Dry-run a command per file', scenario='Before deleting.', setup=SS, cmd="cd ~/ops/data; while IFS= read -r f; do echo rm -- \"$f\"; done < files.txt", explain='echo first.'),
    dict(level='a', title='Group by environment', scenario='Report.', setup=SS, cmd="cd ~/ops/data; declare -A n; while read -r h _ env || [[ -n $h ]]; do [[ -z $h || $h == \\#* ]] && continue; n[$env]+=\"$h \"; done < hosts.txt; for e in \"${!n[@]}\"; do echo \"$e: ${n[$e]}\"; done | sort", explain='Associative array.'),
], extra=build_up('a patch list from hosts.txt', 'Riya builds the reading part of her patch script.', SS, [
    ("cd ~/ops/data; while IFS= read -r line || [[ -n $line ]]; do echo \"[$line]\"; done < hosts.txt | wc -l", '1. Every line, including the last.'),
    ("cd ~/ops/data; while read -r h ip env || [[ -n $h ]]; do [[ -z $h || $h == \\#* ]] && continue; echo \"$h $ip $env\"; done < hosts.txt", '2. Fields, no comments or blanks.'),
    ("cd ~/ops/data; while read -r h ip env || [[ -n $h ]]; do [[ $env == prod ]] || continue; echo \"would run: ssh -n $h 'sudo apt -y upgrade'\"; done < hosts.txt", '3. Only prod, dry run.'),
    ("cd ~/ops/data; n=0; while read -r h _ env || [[ -n $h ]]; do [[ $env == prod ]] && ((++n)); done < hosts.txt; echo \"$n prod hosts would be patched\"", '4. A summary that survives the loop.'),
], cumulative=False)) + VAR + which('Choosing the right way to read.', [
    ('Each line', 'while IFS= read -r', 'Exact.', 'for $(cat).'),
    ('Columns', 'read -r a b c', 'Splits.', 'cut in a loop.'),
    ('Whole file', 'mapfile -t', 'Fast, array.', 'Loop + +=.'),
    ('Command output', 'done < <(cmd)', 'Vars survive.', 'cmd | while.'),
    ('Huge files', 'awk', 'Much faster.', 'Bash loop.'),
    ('Remote commands in loop', 'ssh -n', 'No stdin theft.', 'plain ssh.'),
]) + keys('Handy forms.', [
    ('while IFS= read -r l || [[ -n $l ]]', 'safe loop', 'lines'),
    ('done < file', 'input', 'same shell'),
    ('IFS=, read -r a b c', 'CSV-ish', 'fields'),
    ('mapfile -t -s 1 arr < f', 'array, skip header', 'all'),
    ('done < <(cmd)', 'command output', 'vars kept'),
    ('ssh -n · cmd < /dev/null', 'protect stdin', 'loops'),
]) + scriptit('each-host.sh', 'Run a command for every host of a given environment in hosts.txt, skipping comments and blank lines, reading the list on fd 3 so the command can never steal it, and printing a summary.',
'''#!/usr/bin/env bash
set -euo pipefail
printf '# hosts\\nweb01 10.0.1.11 prod\\n\\ndb01 10.0.2.21 prod\\ntest01 10.0.9.5 test' > hosts.txt
env_wanted=prod
cmd=(echo "would patch")          # replace with: ssh -n "$host" sudo apt-get -y upgrade
ok=0
while read -r -u 3 host ip env || [[ -n ${host:-} ]]; do
  [[ -z ${host:-} || $host == \\#* ]] && continue
  [[ $env == "$env_wanted" ]] || continue
  "${cmd[@]}" "$host ($ip)"
  ((++ok))
done 3< hosts.txt
echo "done: $ok host(s) in $env_wanted"''',
'<p>The command is an array, so it can contain spaces safely.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>for h in $(cat hosts.txt)</code> splits on every space, tab and newline: 21 words, not 7 lines. <b>2.</b> Plain <code>read</code> treats backslashes as escapes (so <code>build\\01</code> becomes <code>build01</code>), trims leading and trailing whitespace (IFS), and returns failure at a last line without a newline, so the loop body never runs for it. <code>while IFS= read -r line || [[ -n $line ]]</code> fixes all three. <b>3.</b> <code>cat … | while</code> runs the loop in a <b>subshell</b>; <code>count</code> is incremented there and thrown away when the pipe ends. Redirect instead: <code>done &lt; hosts.txt</code> or <code>done &lt; &lt;(cmd)</code>.') + qc('Which option keeps backslashes in read?', '-r (raw).') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../01-script-craft/04-a-reusable-script-template-and-shellcheck/">Lesson 1.4</a> (the template) and <a href="../../../linux/12-shell-environment/09-loops-for-while-until-break-continue/">Linux Lesson 12.9</a> (loops).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
