import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='05-redirection-and-pipes', lesson='02-redirection-dev-null-and-here-documents', n='5.2',
    module_label='Module 5 · Redirection, pipes and chaining',
    title='Redirection: >, >>, <, 2>, 2>&1, /dev/null and here-documents',
    desc='Every redirection operator: > and >> (overwrite and append), noclobber and >|, < for input, 2> and 2>>, 2>&1, &> and &>>, why the order of 2>&1 matters, /dev/null, here-documents (<< EOF, quoted EOF, <<-), here-strings (<<<), process substitution, and sudo tee. Each operator explained, then used by admins, DBAs, developers, data engineers, DevOps, security and QA, with real outputs.',
    og_desc='> vs >>, 2>&1 and why its order matters, /dev/null, here-documents and here-strings, with real outputs from Ubuntu.',
    minutes=40, level='Beginner → Advanced',
    lead='One wrong character, > instead of >>, empties a whole log. This lesson explains every redirection operator: saving, appending, feeding files, capturing errors, combining streams, throwing output away and writing multi-line input inside scripts.',
    chips=['Operators by field', 'Why 2>&1 order matters', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Save, append, feed, combine, discard, here-doc
echo 'Mon ok' > week.log           # new file
echo 'Tue ok' >> week.log          # add a line
wc -l < week.log                   # feed it as input
ls week.log /nope > all.txt 2>&1   # results + errors
cat all.txt
ls /nope 2>/dev/null || echo 'error hidden'
cat << EOF
Report for $(date -d 2026-11-06 +%F)
Lines in log: $(wc -l < week.log)
EOF
"""

RUN = dict(
    heading='Every operator in one short script',
    intro='<p>Create and grow a log, count it through stdin, capture results and errors together, hide one error and print a here-document report. Change the operators and run again.</p>',
    code=MAIN, expect='any',
    anno=[
        ("echo 'Tue ok' >> week.log          # add a line", 'Append: 2 lines now.'),
        ('wc -l < week.log                   # feed it as input', 'Just the number.'),
        ('ls week.log /nope > all.txt 2>&1   # results + errors', 'Both in all.txt.'),
        ("ls /nope 2>/dev/null || echo 'error hidden'", 'Error discarded.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is in all.txt?', code=MAIN, expect='any'),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many lines does a.txt have at the end? Then run.',
             code="echo one > a.txt\necho two >> a.txt\necho three > a.txt\nwc -l < a.txt\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the error should go into all.txt too, but it is printed. Fix the order.',
             code="ls /nope 2>&1 > all.txt\necho '--- all.txt:'; cat all.txt\n", expect='any'),
        dict(label='4 · Your turn', hint='Write a 3-line file hello.txt with a here-document, then show it.',
             code="cat > hello.txt << EOF\nline 1\nline 2\nline 3\nEOF\ncat hello.txt\n"),
        dict(label='5 · Challenge', hint="Print $HOME literally (not expanded) with a here-document.",
             code="cat << 'EOF'\nmy home is $HOME\nEOF\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: root-owned files, noclobber and a real database',
    intro='<p>These need sudo or a database server, which our recorder does not have. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · The sudo trap, and the fix', cmd='sudo echo "test" > /etc/mp_test.conf\necho "test" | sudo tee /etc/mp_test.conf', output='bash: /etc/mp_test.conf: Permission denied\n[sudo] password for riya:\ntest', note='Typical. Remove it afterwards: <code>sudo rm /etc/mp_test.conf</code>.'),
        dict(title='2 · Turn on noclobber for good', cmd="echo 'set -o noclobber' >> ~/.bashrc; source ~/.bashrc\necho x > ~/.bashrc", output='bash: /home/riya/.bashrc: cannot overwrite existing file', note='Typical. Use >| when you really mean to overwrite.'),
        dict(title='3 · Dump and restore MySQL', cmd='mysqldump -u root -p shop > shop.sql\nmysql -u root -p shop_copy < shop.sql', output='Enter password:\nEnter password:', note='Typical (needs MySQL; see the Advanced Java JDBC module). gzip version: <code>mysqldump shop | gzip &gt; shop.sql.gz</code>.'),
        dict(title='4 · PostgreSQL with a here-document', cmd="psql -d shop << 'SQL'\nSELECT count(*) FROM orders;\nSQL", output=' count\n-------\n  1520\n(1 row)', note='Typical. The psql client is on our build machine but no server.'),
        dict(title='5 · Bash and dash on our build machine', cmd="bash --version | head -1; ls -l /bin/sh | sed 's/.* //'", output=pc("bash --version | head -1; ls -l /bin/sh | sed 's/.* //'"), note='Recorded. /bin/sh is dash: &amp;&gt; and &lt;&lt;&lt; do not work in #!/bin/sh scripts.'),
    ],
)

TRACE = dict(
    heading='A log file, line by line',
    intro='<p>Step through a script that creates, grows and reads a log. Watch the file change.</p>',
    code='''echo "start" > run.log
echo "step 1" >> run.log
ls /missing >> run.log 2>&1
n=$(wc -l < run.log)
echo "log has $n lines"
''',
    notes={1: 'Create :: > makes a fresh file.', 2: 'Append :: >> adds a line.', 3: 'Both :: The error is appended too.', 4: 'Input :: < feeds the file to wc.', 5: 'Result :: 3 lines.'},
    expect='any',
)

WORKED_INTRO = 'Three tasks from real jobs: a DBA’s SQL report with no temp file, an admin’s cron-ready log, and a developer’s generated config.'
EXAMPLES = [
    dict(level='b', tag='System admin', title='A job that logs properly',
         problem='<p>Run a check twice so that both runs, results and errors, end up in check.log.</p>',
         inp='a check that prints one result and one error',
         approach=['>> keeps old runs.', '2>&1 after it adds errors.'],
         code='''check() { echo "disk ok"; ls /data_missing; }
check >> check.log 2>&1
check >> check.log 2>&1
cat check.log
''',
         notes={2: 'Run 1 :: Appended, errors included.', 3: 'Run 2 :: Added below.', 4: 'Four lines: two runs.'},
         tryit='Replace the first >> with > and run twice.', expect='any'),
    dict(level='i', tag='DBA', title='SQL report with a here-document',
         problem='<p>Create a table, insert three orders and print the total per city, all from the script.</p>',
         inp='SQL inside the script (SQLite through minisql.py)',
         approach=['Write minisql.py once (it reads SQL on stdin).', 'Feed the SQL with << SQL.'],
         code='''cat > minisql.py << 'PY'
import sqlite3, sys
db = sqlite3.connect(sys.argv[1])
for s in sys.stdin.read().split(';'):
    if s.strip():
        for r in db.execute(s): print(*r, sep=' | ')
PY
python3 minisql.py :memory: << SQL
CREATE TABLE o(city TEXT, amt INT);
INSERT INTO o VALUES ('Pune',500),('Agra',300),('Pune',250);
SELECT city, sum(amt) FROM o GROUP BY city;
SQL
''',
         notes={1: 'Helper :: Quoted PY: written exactly.', 8: 'SQL :: The here-doc becomes stdin.'},
         tryit='Add ORDER BY 2 DESC.'),
    dict(level='a', tag='Developer / DevOps', title='Generate a config, safely',
         problem='<p>Write nginx-style config from variables, without overwriting an existing file by accident.</p>',
         inp='app name and port in variables',
         approach=['noclobber protects existing files.', 'Here-doc fills in the variables.'],
         code='''set -o noclobber
app=shop; port=8080
cat > "$app.conf" << EOF
server {
    listen $port;
    server_name $app.example.in;
}
EOF
cat > "$app.conf" << EOF || echo "refused: $app.conf exists"
overwrite attempt
EOF
cat "$app.conf"
''',
         notes={1: 'Safety :: > will not overwrite.', 3: 'Template :: Variables expanded.', 9: 'Second write refused.'},
         tryit='Use >| for the second write.'),
]

QUIZ = mix([
    dict(q='What does > do if the file already exists?', options=['Appends', 'Empties it, then writes', 'Fails', 'Asks first'], answer=1,
         why='> truncates. >> appends.'),
    dict(q='Which line puts results and errors into all.log?', options=['cmd 2>&1 > all.log', 'cmd > all.log 2>&1', 'cmd > all.log 2> 1', 'cmd 1>&2 all.log'], answer=1,
         why='Left to right: first 1 → file, then 2 → where 1 points.'),
    dict(q='What is /dev/null?', options=['An empty folder', 'A device that discards everything written to it', 'A deleted file', 'The trash'], answer=1,
         why='Writes vanish; reads give EOF.'),
    dict(q="In cat << 'EOF' … EOF, what happens to $HOME?", options=['Expanded', 'Printed literally', 'Error', 'Removed'], answer=1,
         why='A quoted delimiter turns off expansion.'),
    dict(q='sort data.txt > data.txt leaves data.txt…', options=['sorted', 'empty', 'unchanged', 'doubled'], answer=1,
         why='The shell empties it before sort reads.'),
    dict(q='Why does sudo echo x > /etc/f fail?', options=['echo is not allowed', 'The redirection is done by your non-root shell', 'sudo has no echo', '/etc is read-only'], answer=1,
         why='Use | sudo tee /etc/f.'),
    dict(q='Which bash operator sends both streams to a file?', options=['&>', '2>1', '>>2', '|>'], answer=0,
         why='&> file = > file 2>&1 (bash only).'),
    dict(q='What does <<- do?', options=['Appends', 'Removes leading tabs in a here-doc', 'Reads backwards', 'Nothing'], answer=1,
         why='Tabs only, not spaces.'),
])

REVISION = [
    '<code>&gt;</code> overwrite (empties first), <code>&gt;&gt;</code> append; <code>set -o noclobber</code> + <code>&gt;|</code>.',
    '<code>&lt; file</code>: file as stdin (no file name in the output); <code>while read -r l; do …; done &lt; file</code>.',
    '<code>2&gt;</code> / <code>2&gt;&gt;</code>: errors; <code>&gt; out 2&gt; err</code>: two files.',
    '<code>&gt; f 2&gt;&amp;1</code> (or <code>&amp;&gt; f</code>): both. <b>Order matters</b>: <code>2&gt;&amp;1 &gt; f</code> leaves errors on screen.',
    '<code>/dev/null</code>: <code>&gt; /dev/null 2&gt;&amp;1</code> silence; <code>2&gt;/dev/null</code> hide errors; <code>&lt; /dev/null</code> no input.',
    "Here-doc <code>&lt;&lt; EOF</code> (expanded), <code>&lt;&lt; 'EOF'</code> (literal), <code>&lt;&lt;-</code> (tabs); EOF alone on its line.",
    'Here-string <code>&lt;&lt;&lt; "$var"</code>; process substitution <code>&lt;(cmd)</code>.',
    'Never <code>cmd f &gt; f</code>. Root files: <code>| sudo tee [-a]</code>.',
]

FAQ = [
    ('What is the difference between > and >> in Linux?', '> overwrites the file (it is emptied first); >> appends to the end. Both create the file if it does not exist.'),
    ('How do I redirect both stdout and stderr to a file?', 'command > file 2>&1 (any shell), or command &> file in bash. To append: >> file 2>&1 or &>> file.'),
    ('Why does the order of 2>&1 matter?', 'Redirections are applied left to right, and 2>&1 copies where stdout points at that moment. Put it after > file.'),
    ('What does 2>/dev/null mean?', 'Send error messages (stream 2) to /dev/null, which throws them away.'),
    ('What is a here-document?', 'A way to give several lines from the script as a command’s input: command << EOF … EOF. Quote EOF to stop variable expansion.'),
    ('How do I write to a file that needs root?', 'echo "text" | sudo tee /path/file (or sudo tee -a to append). sudo echo text > file does not work.'),
    ('How do I avoid overwriting files by accident?', 'set -o noclobber; then > refuses to overwrite existing files and >| forces it.'),
]

PRACTICE_INTRO = 'Small tasks with redirection. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Create and add', stmt='Create todo.txt with “buy milk”, then add “pay bill”. Show it.', inp='—',
         code="echo 'buy milk' > todo.txt\necho 'pay bill' >> todo.txt\ncat todo.txt\n", explain='> then >>.'),
    dict(level='easy', title='Just the number', stmt='Print only the number of lines of /etc/hostname.', inp='/etc/hostname',
         code='wc -l < /etc/hostname\n', explain='< hides the file name.'),
    dict(level='easy', title='Hide the error', stmt='List /nope without any message on screen.', inp='—',
         code="ls /nope 2>/dev/null\necho \"exit status $?\"\n", explain='The error is discarded; the exit status still says it failed.'),
    dict(level='medium', title='Both into one file', stmt='Put the result and the error of ls /etc/hostname /nope into both.txt and show it.', inp='—',
         code="ls /etc/hostname /nope > both.txt 2>&1\ncat both.txt\n", explain='> first, then 2>&1.', expect='any'),
    dict(level='medium', title='Here-doc file', stmt='Create servers.txt with web01, web02, db01 using a here-document and count the lines.', inp='—',
         code="cat > servers.txt << EOF\nweb01\nweb02\ndb01\nEOF\nwc -l < servers.txt\n", explain='cat > file << EOF writes the lines.'),
    dict(level='medium', title='Literal dollar', stmt='Print the line “price: $5” exactly, with a here-document.', inp='—',
         code="cat << 'EOF'\nprice: $5\nEOF\n", explain="Quoted 'EOF': $5 is not expanded."),
    dict(level='business', title='Only errors counted', stmt='Count how many of a.txt b.txt c.txt are missing (only a.txt exists), without printing the results.', inp='a.txt exists',
         code='echo x > a.txt\nls a.txt b.txt c.txt 2>&1 > /dev/null | wc -l\n', explain='Errors to the pipe, results discarded.'),
    dict(level='business', title='Split a CSV line', stmt='From “INV-77,4999,Pune” print “Pune: Rs 4999”.', inp='a CSV line',
         code="IFS=, read -r id amt city <<< 'INV-77,4999,Pune'\necho \"$city: Rs $amt\"\n", explain='Here-string into read with IFS=,.'),
]

SCN_INTRO = 'Interview questions about redirection, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is the difference between > and >>?”',
        'A very common first-round question.',
        'do you know overwrite vs append, and the risk?',
        '''<ul>
          <li>&gt; empties the file first, then writes; &gt;&gt; adds at the end. Both create the file.</li>
          <li>Example: <code>date &gt;&gt; log.txt</code> for logs, <code>ls &gt; list.txt</code> for a fresh list.</li>
          <li>Safety: <code>set -o noclobber</code>, then <code>&gt;|</code> to force.</li>
        </ul>''', 'saying they are the same.') +
    scn('Operations · cron', 'Junior', 'The log has results but never errors',
        'A crontab line is <code>./sync.sh 2&gt;&amp;1 &gt;&gt; /var/log/sync.log</code>. Failures never appear in the log.',
        'do you know that redirection order matters?',
        '''<ol>
          <li>Left to right: 2&gt;&amp;1 copied stdout while it still pointed to cron’s capture, not the log.</li>
          <li>Fix: <code>&gt;&gt; /var/log/sync.log 2&gt;&amp;1</code>.</li>
          <li>Test by forcing an error and checking the log.</li>
        </ol>''', 'adding 2&gt;&gt; to a second file without understanding why.') +
    scn('Data team · DBA', 'Mid-level', 'The report that came out empty',
        'A script runs <code>grep -v test users.csv &gt; users.csv</code> to remove test accounts. Now users.csv is empty and the CRM import failed.',
        'do you understand when the shell opens files?',
        '''<ul>
          <li>The shell truncates users.csv before grep starts, so grep reads nothing.</li>
          <li>Restore from backup; then write to a temp file and <code>mv</code> it into place (atomic, Lesson 3.2), or use <code>sed -i</code> / <code>sponge</code>.</li>
          <li>Add a check: abort if the new file is empty or much smaller.</li>
        </ul>''', '“run it again”, which keeps the file empty.') +
    scn('Platform · automation', 'Senior', 'Provisioning script edits system files',
        'A setup script must add a line to /etc/hosts and write /etc/app/app.conf with variables, as a non-root CI user with sudo.',
        'can you write system files safely from scripts?',
        '''<ul>
          <li><code>echo "10.0.0.5 db01" | sudo tee -a /etc/hosts &gt; /dev/null</code> (tee prints too; silence it).</li>
          <li><code>sudo tee /etc/app/app.conf &gt; /dev/null &lt;&lt; EOF</code> with the template; quote EOF where $ must stay literal.</li>
          <li>Make it idempotent: <code>grep -q db01 /etc/hosts || …</code>; prefer configuration tools (Ansible) at scale.</li>
        </ul>''', 'sudo echo … &gt; /etc/hosts, or running the whole script as root.')
) + interview([
    ('What is the difference between > and >>?', '> overwrites (truncates), >> appends.'),
    ('How do you redirect stderr to stdout?', '2>&1; put it after the stdout redirection: > file 2>&1.'),
    ('What is /dev/null?', 'A device that discards writes and returns EOF on read.'),
    ('How do you suppress all output of a command?', 'cmd > /dev/null 2>&1 (or &> /dev/null in bash).'),
    ('What is a here-document?', 'Inline multi-line stdin: cmd << EOF … EOF; quoted EOF disables expansion.'),
    ('Why does sudo echo x > /etc/file fail?', 'The redirection is done by the calling shell, not by sudo. Use tee.'),
    ('What happens with sort file > file?', 'The file is emptied before sort reads it; the result is an empty file.'),
], [
    ('RHCSA (EX200)', '“Use input-output redirection (&gt;, &gt;&gt;, |, 2&gt;, etc.)”: this lesson covers it fully.'),
    ('LFCS', 'Essential commands: redirect input and output, use here-documents in scripts.'),
    ('CompTIA Linux+', 'Redirection operators (&gt;, &gt;&gt;, &lt;, 2&gt;, &amp;&gt;, &lt;&lt;, &lt;&lt;&lt;) and /dev/null.'),
]) + distro('The basic operators are POSIX and work everywhere; a few are bash extensions.', [
    ('> >> < 2> 2>&1 <<', 'yes', 'yes', 'yes', 'yes'),
    ('&> &>> <<< |&', 'bash yes; /bin/sh (dash) no', 'bash; /bin/sh is bash there', 'bash/zsh yes', 'WSL bash; Git Bash yes'),
    ('<(cmd)', 'bash', 'bash', 'bash/zsh', 'WSL yes; Git Bash yes'),
    ('/dev/null', 'yes', 'yes', 'yes', 'Git Bash yes; PowerShell uses $null'),
    ('noclobber', 'set -o noclobber', 'same', 'same (zsh: setopt noclobber)', 'same'),
    ('sudo tee', 'yes', 'yes', 'yes', 'WSL yes; Git Bash: no sudo'),
]) + teaser('5.3', 'Riya wants the 5 IP addresses that hit her web server most often, from a 50 MB access log, without creating any temporary files. And she wants to see the result on screen and save it at the same time. Which two tools join commands together like that?')

CHEATSHEET = cheatsheet('redirection', [
    ('Output', [('cmd > f', 'overwrite'), ('cmd >> f', 'append'), ('> f  ·  : > f', 'empty a file'), ('set -o noclobber', 'protect'), ('cmd >| f', 'force overwrite')]),
    ('Input', [('cmd < f', 'file as stdin'), ('done < f', 'loop over lines'), ('cmd < /dev/null', 'no input'), ("cmd <<< 'text'", 'here-string'), ('diff <(a) <(b)', 'process substitution')]),
    ('Errors', [('cmd 2> err', 'errors to file'), ('cmd 2>> err', 'append errors'), ('cmd 2>/dev/null', 'hide errors'), ('> out 2> err', 'split'), ('echo x >&2', 'write to stderr')]),
    ('Both', [('> f 2>&1', 'both (POSIX)'), ('&> f  ·  &>> f', 'both (bash)'), ('2>&1 | cmd', 'both into a pipe'), ('&> /dev/null', 'silence'), ('2>&1 > f', 'WRONG order')]),
    ('Here-documents', [('cat << EOF', 'expanded'), ("cat << 'EOF'", 'literal'), ('cat <<- EOF', 'strip tabs'), ('cat > f << EOF', 'write a file'), ('| sudo tee f', 'root files')]),
])

MINDMAP = mindmap('Redirection', [
    ('> and >>', 'red', ['> empties first', '>> appends', 'noclobber, >|']),
    ('<', 'blue', ['file as stdin', 'while read … < f', '< /dev/null']),
    ('2> 2>>', 'amber', ['errors only', '2>/dev/null', '> out 2> err']),
    ('Both', 'green', ['> f 2>&1', '&> &>> (bash)', 'order: left → right']),
    ('Here', 'violet', ["<< EOF / << 'EOF'", '<<- tabs', '<<< "$var"']),
    ('Traps', 'acc', ['cmd f > f empties f', 'sudo … > f fails', 'indented EOF']),
])

LAB = lab('build a proper job log', 'Build the lab, do the five tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab52 && cd ~/lab52 && rm -f *.txt *.log *.conf
printf 'Pune\\nAgra\\nGoa\\n' > cities.txt''',
    tasks=['Run <code>ls cities.txt nofile.txt</code> <b>twice</b> so that both runs, results and errors, are appended to <code>job.log</code>.',
           'Write the number of lines of cities.txt (just the number) into <code>count.txt</code>.',
           'Create <code>app.conf</code> with a here-document containing the two lines <code>port=8080</code> and <code>env=prod</code>.',
           'Create <code>literal.txt</code> containing exactly <code>$HOME</code> (not your home path).',
           'Run <code>ls cities.txt nofile.txt</code> so that the error is thrown away and only the result is saved in <code>quiet.txt</code>.'],
    solution='''ls cities.txt nofile.txt >> job.log 2>&1
ls cities.txt nofile.txt >> job.log 2>&1
wc -l < cities.txt > count.txt
cat > app.conf << EOF
port=8080
env=prod
EOF
cat > literal.txt << 'EOF'
$HOME
EOF
ls cities.txt nofile.txt > quiet.txt 2>/dev/null''',
    check='''cd ~/lab52
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 two runs logged"   '[ "$(grep -c cities.txt job.log 2>/dev/null)" = 2 ] && [ "$(grep -c nofile job.log 2>/dev/null)" = 2 ]'
ok "2 count only"        '[ "$(cat count.txt 2>/dev/null)" = 3 ]'
ok "3 here-doc config"   '[ "$(cat app.conf 2>/dev/null)" = "$(printf "port=8080\\nenv=prod")" ]'
ok "4 literal \\$HOME"    '[ "$(cat literal.txt 2>/dev/null)" = "\\$HOME" ]'
ok "5 errors discarded"  '[ "$(cat quiet.txt 2>/dev/null)" = cities.txt ]' ''')
