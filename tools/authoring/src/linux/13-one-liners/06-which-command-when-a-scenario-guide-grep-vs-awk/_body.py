import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

WC = r"""rm -rf ~/wc; mkdir -p ~/wc/src ~/wc/backup; cd ~/wc
cat > users.txt <<'EOF'
riya:1001:/home/riya:/bin/bash
aman:1002:/home/aman:/bin/zsh
zoya:1003:/home/zoya:/bin/bash
backup:34:/var/backups:/usr/sbin/nologin
EOF
printf 'port=8080\nhost=0.0.0.0\ndebug=false\n' > app.conf
printf 'port=8080\nhost=127.0.0.1\ndebug=false\n' > app.conf.new
for f in a b c; do echo "file $f" > src/$f.txt; done; head -c 200000 /dev/urandom > src/data.bin"""

HOOK = hook('Riya knows forty commands. In a hurry she still loses minutes: she writes an awk program when grep was enough, uses sed to pull out a column, copies a 50 GB folder again with <code>cp -r</code> after one file changed, and searches the whole disk with find when locate would answer in a millisecond. Knowing a command is half the skill; the other half is <b>choosing</b> it. This lesson is a scenario guide: for each common job it compares the candidates side by side on the same input, with real output, and gives a one-line rule you can remember.',
    ['choose between grep, awk, sed and cut for searching, extracting and changing text',
     'choose between find and locate, cp and rsync, scp, rsync and sftp, tar and zip, curl and wget',
     'choose between kill, pkill and systemctl; diff, cmp and comm; which, type and whereis; cron and systemd timers',
     'use a decision habit (what do I need: find, extract, change, compare, copy, run later?) instead of guessing'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the right tool, faster'),
    ('decide', 'The master chart', 3, 'job → command'),
    ('definition', 'How to choose', 5, 'four questions'),
    ('types', 'The big comparison', 6, 'pairs and trios'),
    ('commands', 'By field', 15, 'side-by-side real runs'),
    ('animation', 'See it happen', 4, 'the decision tree'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'pick the tool'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? The master chart', [
    ('Is this text in the file? Which lines?', 'grep', 'search'),
    ('Take column 1 of a simple file', 'cut (fixed delimiter) · awk (spaces, conditions)', 'extract'),
    ('Change text in a stream or file', 'sed (s/a/b/) · awk if it depends on columns', 'change'),
    ('Compute: sums, groups, reports', 'awk', 'compute'),
    ('Find files by name, size, age', 'find (live) · locate (index, instant)', 'files'),
    ('Copy a folder again after small changes', 'rsync -a (only differences)', 'sync'),
    ('Copy to another server', 'rsync -a over ssh (resume, delta) · scp (simple, one-off)', 'remote'),
    ('Stop a program / service', 'systemctl stop (service) · pkill -x (by name) · kill (PID)', 'stop'),
    ('Compare files', 'diff (text lines) · cmp (bytes) · comm (sorted lists)', 'compare'),
    ('Run later / regularly', 'at (once) · cron / systemd timer (repeat)', 'schedule'),
])

cmap = concept_map(
    [('6.1', 'grep', 'search'), ('6.4', 'sed', 'stream editor'), ('6.5', 'awk', 'fields and reports')],
    ['grep vs awk vs sed vs cut', 'find vs locate', 'cp vs rsync, scp vs rsync vs sftp', 'tar vs zip, gzip vs xz', 'curl vs wget', 'kill vs pkill vs systemctl', 'diff vs cmp vs comm', 'which vs type vs whereis', 'cron vs timers vs at'],
    [('13.7', '100 one-liners', 'cheat sheet'), ('16.6', 'SSH, scp, rsync', 'remote copies'), ('14.5', 'tar and compression', 'archives'), ('17.4', 'cron and at', 'scheduling')],
    'Ask what the job is (search, extract, change, compute, find, copy, compare, run later) before you ask which command you know best.')

sc = (term(20, 14, 316, 156, ['$ grep bash users.txt', ('riya:1001:/home/riya:/bin/bash', 'out'), "$ cut -d: -f1 users.txt | head -2", ('riya', 'out'), ('aman', 'out'), "$ awk -F: '$2>=1000{print $1}' users.txt", ('riya aman zoya', 'acc')], title='riya@web01: ~/wc', prompt='riya@web01:~/wc$', size=6.8, step=16)
      + t(352, 36, 'Same file:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['grep: find lines', 'cut: one column', 'awk: + condition', 'sed: change text', 'pick the smallest'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The right tool, faster</h2>
  <div class="story">
''' + puzzle('Riya needs (1) the users whose UID is at least 1000, (2) every config line where <code>port=8080</code> becomes <code>port=9090</code>, (3) a nightly copy of a 50 GB folder to another server where only a few files change each day, and (4) to stop the nginx service that keeps coming back after <code>kill</code>. She uses grep for (1), awk for (2), <code>cp -r</code> for (3) and <code>kill -9</code> for (4). Which of the four choices are wrong, and what should each one be?') + '''
    <p class="narration">Riya asks the same file three different questions.</p>
''' + scene('A terminal: grep finds lines containing bash, cut takes the first column, and awk prints user names with a UID of 1000 or more.', sc,
            'Each tool answers a different <tspan font-weight="700" class="s-acc">kind</tspan> of question.') + '''
K> So which one is the best?
A> None is “best”. grep is fastest at <b>finding lines</b>. cut is simplest for <b>one column with a fixed separator</b>. awk is the one that can <b>decide by a column’s value and compute</b>. sed is for <b>changing</b> text. I choose by the question, then pick the smallest tool that answers it.
R> And the other three in the puzzle?
A> The same idea for files, copies and processes: find vs locate, cp vs rsync, kill vs systemctl. Today: a guide for each choice, with side-by-side runs.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A toolbox drawn as four drawers: SEARCH (grep, find, locate), EXTRACT and COMPUTE (cut, awk), CHANGE (sed, tr), MOVE and COPY (cp, rsync, scp, tar). A question mark points to the drawer to open first.">'
       + label_box(14, 24, 146, 110, ['SEARCH', 'grep (text)', 'find / locate', '(files)'], 'blue', 9)
       + label_box(170, 24, 146, 110, ['EXTRACT', 'cut (column)', 'awk (condition,', 'compute)'], 'green', 9)
       + label_box(326, 24, 146, 110, ['CHANGE', 'sed (text)', 'tr (characters)', 'awk (by column)'], 'amber', 9)
       + label_box(482, 24, 146, 110, ['MOVE / COPY', 'cp (local, once)', 'rsync (again, remote)', 'tar (bundle)'], 'violet', 9)
       + t(320, 162, 'First decide which drawer, then pick the smallest tool in it.', 10, 'acc', bold=True)
       + t(320, 184, 'A bigger tool is slower to write and easier to get wrong.', 9.4, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Choosing at four depths', [
    ('v', 'No jargon: a toolbox with drawers', '      <p>Open the right drawer first.</p>' + pic),
    ('b', 'Four questions', '''      <ol>
        <li><b>What is the job?</b> Search, extract, change, compute, find files, copy, compare, stop, schedule.</li>
        <li><b>On what?</b> Lines of text, columns, whole files, folders, processes, remote machines.</li>
        <li><b>Once or again?</b> A one-off job or something repeated (then rsync, cron, a script).</li>
        <li><b>How safe?</b> Read-only first; tools that change things get a preview (echo, -n, --dry-run).</li>
      </ol>'''),
    ('i', 'Rules of thumb', '''      <ul>
        <li>grep to <b>select lines</b>, cut for <b>a fixed column</b>, awk when a <b>condition on a column</b> or <b>maths</b> is involved, sed to <b>replace</b>.</li>
        <li>find when you need <b>live</b> results or tests (size, age, -exec); locate when you only know part of a <b>name</b> and speed matters (index updated daily).</li>
        <li>cp for one-time local copies; rsync when you copy <b>again</b>, over the <b>network</b>, or need to <b>resume</b>.</li>
        <li>systemctl for <b>services</b> (they restart), pkill for programs by name, kill for a known PID.</li>
        <li>diff for text, cmp for binary, comm for sorted lists, sha256sum to compare files on different machines.</li>
      </ul>'''),
    ('a', 'Behind the screen: why the difference matters', '''      <ul>
        <li>grep uses highly optimised string search (Boyer–Moore-style skipping), often 10× faster than awk on large logs for pure searching.</li>
        <li>locate reads a prebuilt database (<code>/var/lib/plocate/plocate.db</code>, rebuilt by a daily timer): instant but can be stale and only knows names.</li>
        <li>rsync compares size and modification time (or checksums with -c) and sends only changed parts using a rolling checksum; cp always copies everything.</li>
        <li>A service killed with kill is restarted by systemd if <code>Restart=</code> is set: the puzzle’s nginx that “keeps coming back”.</li>
        <li>cron runs with a tiny environment and no logs by default; systemd timers log to the journal, can catch up missed runs (<code>Persistent=true</code>) and have dependencies.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A scenario guide for choosing commands</h2>
''' + def_block(
    'A <b>scenario guide</b> maps a job to the command that does it best. Many Linux tools overlap (grep, awk and sed can all print matching lines; cp and rsync can both copy), but each is <b>designed</b> for one kind of job and is simplest, fastest and safest there. Choosing well means naming the job first, then picking the smallest tool designed for it.',
    'Name the job, then pick the smallest tool built for it.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Select', 'Keep some lines (grep).'),
    ('Extract', 'Keep some columns (cut, awk).'),
    ('Transform', 'Change text (sed, tr).'),
    ('Aggregate', 'Count, sum, group (awk, sort | uniq).'),
    ('Index', 'A prebuilt list (locate’s database).'),
    ('Delta transfer', 'Sending only changes (rsync).'),
    ('Service', 'A program managed by systemd.'),
    ('Timer', 'systemd’s scheduler, like cron.'),
]) + '\n' + names('Where the names come from.', [
    ('grep', 'g/re/p', 'Global regular expression print (ed).'),
    ('sed', 'stream editor', 'Lee McMahon, 1974.'),
    ('awk', 'Aho Weinberger Kernighan', '1977.'),
    ('locate', 'locate files', 'From BSD; now plocate.'),
    ('rsync', 'remote sync', 'Andrew Tridgell, 1996.'),
    ('scp', 'secure copy', 'Part of OpenSSH.'),
    ('curl', 'client URL', 'Daniel Stenberg, 1998.'),
    ('wget', 'web get', 'GNU, 1996.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Find lines', '<code>grep</code>'),
    ('Column', '<code>cut</code> / <code>awk</code>'),
    ('Replace', '<code>sed</code>'),
    ('Copy again', '<code>rsync -a</code>'),
    ('Stop a service', '<code>systemctl stop</code>'),
    ('Compare binaries', '<code>cmp</code> / <code>sha256sum</code>'),
]) + '\n' + lv + didyou('The grep vs awk vs sed overlap is deliberate: they were written at Bell Labs in the same decade, each for one job, and designed to be piped together. Using all three in one pipeline is normal: <code>grep</code> to select, <code>sed</code> to clean, <code>awk</code> to compute.') + '''
EXAM> “When would you use awk instead of grep?” → When you need a condition on a specific column, or computation (sums, counts, formatting); grep only selects lines by pattern.
''' + qc('You need lines where column 3 is greater than 100. grep or awk?', 'awk (\'$3&gt;100\'): grep cannot compare numbers in a column.') + mistake('kill -9 the nginx process',
    'sudo systemctl stop nginx   (and disable it if it must not start at boot)',
    'systemd sees the service die and starts it again (Restart=on-failure): it “keeps coming back”.') + mistake('cp -r big/ backup/ every night',
    'rsync -a --delete big/ backup/   (only changes are copied)',
    'cp copies all 50 GB every time; rsync copies only new and changed files (real run: second rsync-style copy moved 0 files).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The big comparison</h2>
''' + table(['Job', 'grep', 'cut', 'awk', 'sed'], [
    ['Lines containing X', '<b>best</b>: <code>grep X</code>', '-', '<code>awk \'/X/\'</code>', '<code>sed -n \'/X/p\'</code>'],
    ['Column N, fixed delimiter', '-', '<b>best</b>: <code>cut -d: -fN</code>', '<code>awk -F: \'{print $N}\'</code>', 'awkward'],
    ['Columns split by spaces', '-', 'breaks on runs of spaces', '<b>best</b>', '-'],
    ['Condition on a column', '-', '-', '<b>best</b>: <code>$3&gt;100</code>', '-'],
    ['Sum / count / group', '<code>grep -c</code> only counts', '-', '<b>best</b>', '-'],
    ['Replace text', '-', '-', '<code>gsub()</code>', '<b>best</b>: <code>s/a/b/g</code>'],
    ['Edit a file in place', '-', '-', 'gawk -i inplace', '<b>best</b>: <code>sed -i</code>'],
    ['Delete lines', '<code>grep -v</code>', '-', '<code>awk \'!/X/\'</code>', '<code>sed \'/X/d\'</code>'],
], minw=560) + table(['Pair', 'Use the first when…', 'Use the second when…'], [
    ['find / locate', 'you need live results, size/age tests, -exec', 'you know part of a name and want it instantly'],
    ['cp / rsync', 'one local copy', 'copying again, big trees, network, resume, --dry-run'],
    ['scp / rsync', 'one file, one time', 'folders, repeat syncs, slow links (delta)'],
    ['scp / sftp', 'you know the path', 'you want to browse interactively'],
    ['tar / zip', 'Linux to Linux, permissions, streams', 'sharing with Windows users'],
    ['gzip / xz', 'speed', 'smallest size (slower)'],
    ['curl / wget', 'APIs, headers, methods, any protocol', 'downloading files or whole sites, resuming'],
    ['kill / pkill', 'you have the PID', 'you know the name'],
    ['pkill / systemctl', 'a program you started', 'a service (restarts, logs)'],
    ['diff / cmp', 'text, line by line', 'binary files, first differing byte'],
    ['diff / comm', 'two versions of a file', 'two sorted lists: in A, in B, in both'],
    ['which / type', 'a program in PATH', 'aliases, functions, built-ins too'],
    ['cron / systemd timer', 'simple, everywhere', 'logs, catch-up, dependencies'],
    ['at / cron', 'once, later', 'again and again'],
    ['head / tail / less', 'start / end / browse', 'tail -f to follow'],
    ['sort -u / uniq', 'unique values', 'counts (-c) or duplicates (-d) of sorted input'],
    ['-exec + / xargs', 'from find', 'from any list, parallel -P'],
], minw=560) + qc('Which tool would you use to copy a folder to a server every night?', 'rsync -a (over SSH), probably from cron or a systemd timer.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Side-by-side comparisons on the same input, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/wc</code>: <code>users.txt</code> (name:uid:home:shell for 4 accounts), <code>app.conf</code> and a changed <code>app.conf.new</code>, and <code>src/</code> (three text files and a 200 KB binary). The build machine has no rsync, scp or locate installed; their outputs are in <b>Run on your PC</b>, and here we show the idea with the tools that are installed.</p>
''' + cmdcard_u(['every text question', 'choosing the simplest correct tool'],
               ['awk where grep is enough', 'sed to extract columns'])(
    'text', 'grep · cut · awk · sed on the same file', 'grep vs cut vs awk vs sed',
    'Ask the same file four questions. Lines with “bash”: grep. The first column: cut. Users with UID ≥ 1000: awk (a numeric condition on column 2). Change /bin/zsh to /bin/bash: sed. Each tool can do more than its job, but the job it was built for is shortest and clearest.',
    "grep PAT f   ·   cut -d: -f1 f   ·   awk -F: '$2>=1000' f   ·   sed 's/a/b/' f", 'safe',
    [('grep', 'select lines', 'search'),
     ('grep -c / -v / -o', 'count / invert / only match', 'variants'),
     ('cut -d: -f1', 'fixed column', 'simple'),
     ("awk -F: '$2>=1000'", 'condition on a column', 'filters'),
     ("awk '{s+=$2} END…'", 'compute', 'reports'),
     ("sed 's/a/b/g'", 'replace', 'edits'),
     ("sed -n '5,10p'", 'line ranges', 'slices')],
    dict(setup=WC, cmd="cd ~/wc\necho '--- grep: lines with bash'; grep bash users.txt\necho '--- cut: first column'; cut -d: -f1 users.txt | paste -sd' '\necho '--- awk: UID >= 1000'; awk -F: '$2>=1000{print $1}' users.txt | paste -sd' '\necho '--- sed: zsh -> bash'; sed 's#/bin/zsh#/bin/bash#' users.txt | grep aman", note='Four questions, four tools, one line each.'),
    [('qa', [
        dict(situation='The puzzle (1): grep cannot compare numbers.', setup=WC, cmd="cd ~/wc\ngrep ':10' users.txt | cut -d: -f1 | paste -sd' '\nprintf 'old:999:/home/old:/bin/sh\\nbig:10050:/home/big:/bin/sh\\n' >> users.txt\ngrep ':10' users.txt | cut -d: -f1 | paste -sd' '\nawk -F: '$2>=1000{print $1}' users.txt | paste -sd' '", why='The grep trick worked by luck; with UID 999 and 10050 only awk is right.')]),
     ('sys', [
        dict(situation='The puzzle (2): sed for replacing, awk when it depends on a column.', setup=WC, cmd="cd ~/wc\nsed 's/^port=8080$/port=9090/' app.conf | head -1\nawk -F: -v OFS=: '$2>=1000 && $4==\"/bin/zsh\" {$4=\"/bin/bash\"} 1' users.txt | grep aman", why='sed for a text replacement; awk when the change depends on another column.')]),
    ],
    anat=anatomy([('grep', 'cmd', 'lines'), ('cut', 'opt', 'columns'), ('awk', 'arg', 'columns + logic'), ('sed', 'arg', 'changes')], 'Smallest tool that answers the question.')
) + cmdcard_u(['finding files', 'copying and syncing', 'archives to share'],
               ['find / every time you look for a name', 'cp -r for repeated copies'])(
    'files', 'find vs locate · cp vs rsync · tar vs zip', 'files: find, copy, bundle',
    'find walks the disk now and can test size, age and permissions; locate only searches names in a daily index, instantly. cp copies everything every time; rsync copies only what changed (and works over SSH, resumes, has --dry-run). tar keeps Linux permissions and streams well; zip is what Windows users can open.',
    'find / -name x   ·   locate x   ·   rsync -a src/ dst/   ·   tar czf a.tgz d   ·   zip -r a.zip d', 'change',
    [('find -name -size -mtime', 'live, with tests', 'precise'),
     ('locate name', 'index, instant', 'quick lookups'),
     ('cp -a', 'full copy, keeps attributes', 'once'),
     ('rsync -a --delete', 'mirror, only changes', 'again'),
     ('rsync -n', 'dry run', 'preview'),
     ('tar czf', 'Linux archive', 'permissions'),
     ('zip -r', 'Windows-friendly', 'sharing')],
    dict(setup=WC, cmd="cd ~/wc\ncp -a src/. backup/; echo \"cp copied: $(ls backup | wc -l) files\"\nchanged=$(find src -newer backup/a.txt -type f | wc -l); echo \"files changed since the copy: $changed (rsync would copy only these)\"\ntar czf src.tgz src; zip -qr src.zip src\nls -l src.tgz src.zip | awk '{print $5, $NF}'\ntar tzvf src.tgz | head -1 | awk '{print $1, $2}'; unzip -Z1 src.zip | head -1", note='tar records owner and permissions (drwxr-xr-x riya/riya); both archives are about the size of the random binary, which does not compress.'),
    [('sys', [
        dict(situation='find answers what locate cannot.', setup=WC, cmd="cd ~/wc; find . -type f -size +100k -mmin -60 | sed 's|^\\./||'\necho 'locate would need: locate data.bin (name only, from yesterday’s index)'", why='Tests on size and age need find.')]),
    ]
) + cmdcard_u(['stopping things', 'downloading and APIs'],
               ['kill on systemd services', 'wget for API calls with headers'])(
    'procnet', 'kill vs pkill vs systemctl · curl vs wget', 'processes and downloads',
    'kill needs a PID; pkill finds by name; systemctl manages services (stop, restart, logs, and it knows the service should not be restarted). For web: curl is the Swiss army knife for APIs (methods, headers, JSON, many protocols); wget is the downloader (recursive, resume, retries).',
    'kill PID · pkill -x name · sudo systemctl stop svc · curl -s URL · wget -c URL', 'change',
    [('kill PID', 'one process', 'known PID'),
     ('pkill -x name', 'by name', 'your programs'),
     ('systemctl stop', 'a service', 'nginx, mysql'),
     ('systemctl disable', 'not at boot', 'permanent'),
     ('curl -s -H … -d …', 'APIs', 'REST'),
     ('wget -c URL', 'resume a download', 'big files'),
     ('wget -r -np', 'mirror a folder', 'sites')],
    dict(setup=WC, cmd="cd ~/wc\nsleep 30 & p=$!; kill $p; wait $p 2>/dev/null; echo \"kill by PID: status $?\"\nsleep 31 & pkill -x -P $$ sleep; wait 2>/dev/null; echo \"pkill by name: $(pgrep -c -P $$ -x sleep) left\"\ncurl -s file://$HOME/wc/app.conf | head -1\ncurl -s -o /dev/null -w 'curl wrote %{size_download} bytes\\n' file://$HOME/wc/app.conf\nwget -q -O - file://$HOME/wc/app.conf; echo \"wget file:// status: $?\"", expect='any', note='curl speaks many protocols (here file://); wget is for HTTP/HTTPS/FTP downloads and refuses file://.'),
    [('dev', [
        dict(situation='Why systemctl and not kill for services (shown).', cmd="printf '%s\\n' '$ sudo kill 812        # nginx master' '(a second later) systemd: nginx.service: Main process exited; Scheduled restart' '$ sudo systemctl stop nginx    # stays stopped' '$ sudo systemctl disable nginx # does not start at boot'", why='The puzzle (4): systemd restarts a killed service; tell systemd instead.')]),
    ]
) + cmdcard_u(['what changed between two files', 'is this the same file?', 'where does this command come from?'],
               ['diff on binaries', 'which for aliases'])(
    'compare', 'diff vs cmp vs comm vs sha256sum · which vs type vs whereis', 'comparing and identifying',
    'diff shows changed lines of text files; cmp says whether two files are identical byte by byte (and where they first differ); comm splits two sorted lists into “only A, only B, both”; sha256sum compares files on different machines. For commands: type tells you if it is an alias, function, built-in or file; which only searches PATH; whereis also finds man pages.',
    'diff a b · cmp a b · comm a b · sha256sum f · type cmd', 'safe',
    [('diff -u a b', 'text changes', 'reviews'),
     ('cmp a b', 'same bytes?', 'binaries'),
     ('comm -3 a b', 'list differences', 'sorted lists'),
     ('sha256sum f', 'fingerprint', 'remote compare'),
     ('type -a cmd', 'what runs', 'aliases too'),
     ('which cmd', 'path only', 'scripts'),
     ('whereis cmd', 'binary + man page', 'docs')],
    dict(setup=WC, cmd="cd ~/wc\ndiff app.conf app.conf.new\ncmp app.conf app.conf.new; cmp src/data.bin src/data.bin && echo 'data.bin identical'\ncomm -3 <(sort app.conf) <(sort app.conf.new)\nshopt -s expand_aliases; alias ll='ls -l'; type ll; type cd; type -a ls | head -1; which ls", expect='any', note='diff explained the change; cmp only located it; comm listed each side; type knew about the alias and the built-in.'),
    [('sec', [
        dict(situation='Same file on two machines? Compare fingerprints.', setup=WC, cmd="cd ~/wc; cp src/data.bin /tmp/copy-$$.bin; sha256sum src/data.bin /tmp/copy-$$.bin | awk '{print substr($1,1,16)}' | uniq -c; rm /tmp/copy-$$.bin", why='One hash value for both: identical (Lesson 19.4).')]),
    ]
) + undo('Choosing the wrong tool rarely breaks things; the wrong action does.', [
    ('Replaced in the wrong file:', 'restore from backup or git; next time sed without -i first.'),
    ('cp overwrote newer files:', 'use rsync -a --update or cp -n; check with --dry-run.'),
    ('Killed a service that came back:', 'that is systemd working; use systemctl stop/disable.'),
    ('Habit:', 'name the job, choose the tool, preview, then act.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(setup=WC, cmd="cd ~/wc; cut -d' ' -f2 app.conf | head -1", meaning='No space in the line: cut prints the whole line.', fix='Use the right delimiter: cut -d= -f2.'),
    dict(setup=WC, cmd="cd ~/wc; diff src/data.bin users.txt", meaning='diff refuses binary detail.', fix='cmp for binaries.'),
    dict(cmd='locate passwd', meaning='locate is not installed here.', fix='sudo apt install plocate, or find / -name passwd.'),
    dict(cmd='rsync -a a b', meaning='rsync is not installed here.', fix='sudo apt install rsync.'),
    dict(cmd='wget -q -O - file:///etc/hostname', meaning='wget does not support file://.', fix='curl file:///… or cat.'),
]) + qc('Which tells you that ll is an alias: which ll or type ll?', 'type ll (which only searches files in PATH).') + '''
'''
cards = cards + '</section>\n'

Q = [('find text lines?', 'grep', 'blue'), ('a column?', 'cut / awk', 'green'), ('change text?', 'sed', 'amber'), ('compute?', 'awk', 'green'), ('files?', 'find / locate', 'violet'), ('copy again?', 'rsync', 'red')]
def tree(k):
    o = label_box(120, 6, 120, 26, ['What is the job?'], 'card', 8)
    for i in range(k + 1):
        q, a, col = Q[i]
        x = 10 + (i % 3) * 116; y = 44 + (i // 3) * 64
        o += label_box(x, y, 108, 26, [q], 'card', 7.4) + label_box(x, y + 30, 108, 24, [a], col, 7.8)
    return o
see_cmds = [['$ grep ERROR app.log'], ['$ cut -d: -f1 /etc/passwd'], ["$ sed -i 's/8080/9090/' app.conf"], ["$ awk '{s+=$3} END{print s}'"], ['$ find /var -size +1G'], ['$ rsync -a src/ server:dst/']]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Search.', 'Column.', 'Change.', 'Compute.', 'Files.', 'Sync.'])]
behind = [tree(k) for k in range(6)]
two = anim_two('Choosing by the job', 'Behind the screen: the decision tree',
               'Six terminals, each with the tool for one job: grep, cut, sed, awk, find and rsync.',
               'A decision tree: the question “what is the job?” branches into six boxes, each with its tool.', see, behind,
               ['Search.', 'Column.', 'Change.', 'Compute.', 'Files.', 'Sync.'],
               ['grep', 'cut', 'sed', 'awk', 'find', 'rsync'])

def copy(k):
    o = label_box(10, 20, 150, 120, ['src/ (50 GB)', '1 file changed'], 'blue', 8.6)
    o += label_box(200, 20, 150, 120, ['backup/'], 'green', 8.6)
    if k == 0:
        o += arrow(160, 80, 200, 80) + t(180, 160, 'cp -r: all 50 GB, every night', 9, 'red', bold=True)
    else:
        o += arrow(160, 80, 200, 80) + t(180, 160, 'rsync -a: only the changed file', 9, 'green', bold=True)
    return o
s1 = anim_one('Animated example', 'cp versus rsync for repeated copies',
              'The same nightly job with two tools.',
              'cp -r  vs  rsync -a', 'A 50 GB source with one changed file: cp copies everything; rsync copies one file.', [copy(0), copy(1)],
              ['cp', 'rsync'], hid='scenario-copy')

dx = dissect('Layer by layer: why the “right” tool is faster',
    'Each layer has a real command and output from our build machine.', [
    dict(key='speed', name='grep vs awk', sub='pure search', why='Speed.', how='Same search, big file.', impl='grep skips bytes.', used='Big logs.',
         cmd="seq 1 400000 | sed 's/$/ line/' > /tmp/big-$$.txt; s=$(date +%s%N); grep -c '^3999' /tmp/big-$$.txt > /dev/null; g=$(date +%s%N); awk '/^3999/{n++} END{print n}' /tmp/big-$$.txt > /dev/null; a=$(date +%s%N); echo \"grep $(( (g-s)/1000000 )) ms, awk $(( (a-g)/1000000 )) ms\" | sed -E 's/[0-9]+ ms/N ms/g'; (( (a-g) > (g-s) )) && echo 'grep was faster for a pure search'; rm /tmp/big-$$.txt"),
    dict(key='delta', name='Only changes', sub='rsync idea', why='Time and bandwidth.', how='Compare size+mtime.', impl='Rolling checksum.', used='Backups.',
         setup=WC, cmd="cd ~/wc; cp -a src/. backup/; sleep 1; echo changed >> src/b.txt; for f in src/*; do b=backup/${f#src/}; if [ \"$f\" -nt \"$b\" ]; then echo \"would copy: ${f#src/}\"; fi; done"),
    dict(key='svc', name='Services', sub='systemd', why='Restart policy.', how='Restart=.', impl='The service manager.', used='Production.',
         cmd="echo 'Restart=on-failure  -> killed processes come back'; echo 'systemctl stop      -> stopped on purpose, stays stopped'"),
    dict(key='type', name='What runs?', sub='type -a', why='Aliases hide programs.', how='Lookup order.', impl='alias > function > builtin > PATH.', used='Debugging.',
         cmd="shopt -s expand_aliases; alias grep='grep --color=auto'; type -a grep | head -2; type -t echo; type -t ls"),
], hint='From speed to lookup order. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>The decision tree, and cp versus rsync</h2>
''' + two + s1 + dx + qc('Why does an alias change which grep runs?', 'The shell checks aliases before functions, built-ins and PATH; type -a shows the order.') + '''
</section>
'''

VAR = variations('Twenty more side-by-side choices. All were really run on our build machine.', [
    ('Text', [
        dict(title='Count matching lines: grep -c vs awk', setup=WC, cmd="cd ~/wc; grep -c bash users.txt; awk '/bash/{n++} END{print n}' users.txt", why='Same answer; grep -c is shorter.'),
        dict(title='Only the matching part: grep -o', setup=WC, cmd="cd ~/wc; grep -oE '[0-9]{4}' users.txt | paste -sd' '", why='grep -o extracts patterns, no awk needed.'),
        dict(title='Delete lines: grep -v vs sed d', setup=WC, cmd="cd ~/wc; grep -v nologin users.txt | wc -l; sed '/nologin/d' users.txt | wc -l", why='Equivalent; grep -v reads more naturally.'),
        dict(title='Lines 2–3: sed vs head|tail', setup=WC, cmd="cd ~/wc; sed -n '2,3p' users.txt | cut -d: -f1; head -3 users.txt | tail -2 | cut -d: -f1", why='sed -n is one tool.'),
        dict(title='Characters: tr vs sed', setup=WC, cmd="cd ~/wc; tr ':' ' ' < users.txt | head -1; sed 's/:/ /g' users.txt | head -1", why='tr for single characters, sed for words.'),
        dict(title='Upper case: tr vs ${,^^}', cmd="echo linux | tr a-z A-Z; s=linux; echo \"${s^^}\"", why='Inside scripts, parameter expansion avoids a process (Lesson 12.14).'),
        dict(title='Columns with spaces: cut vs awk', cmd="echo 'a   b  c' | cut -d' ' -f2; echo 'a   b  c' | awk '{print $2}'", why='cut sees empty fields between spaces; awk treats runs as one.'),
    ]),
    ('Files', [
        dict(title='Sizes: ls -l vs du vs stat', setup=WC, cmd="cd ~/wc; ls -l src/data.bin | awk '{print $5}'; du -k src/data.bin | cut -f1; stat -c %s src/data.bin", why='Bytes, KB on disk, bytes: choose by what you need.'),
        dict(title='Unique values: sort -u vs uniq', cmd="printf 'b\\na\\nb\\n' | sort -u | paste -sd' '; printf 'b\\na\\nb\\n' | uniq | paste -sd' '", why='uniq without sort missed the second b.'),
        dict(title='Is it text or binary? file', setup=WC, cmd="cd ~/wc; file src/a.txt src/data.bin | sed 's|src/||'", why='Before choosing diff or cmp.'),
        dict(title='Full path of a file: realpath vs readlink', setup=WC, cmd="cd ~/wc/src; realpath a.txt | sed 's|/home/riya|~|'; ln -sf a.txt link.txt; readlink link.txt; readlink -f link.txt | sed 's|/home/riya|~|'", why='readlink shows the link target; -f resolves fully.'),
        dict(title='Compress: gzip vs xz', setup=WC, cmd="cd ~/wc; seq 1 50000 > n.txt; gzip -k n.txt; xz -k n.txt; ls -l n.txt n.txt.gz n.txt.xz | awk '{print $5, $NF}'", why='xz is smaller, gzip is faster (Lesson 14.5).'),
        dict(title='Archive listing: tar t vs unzip -l', setup=WC, cmd="cd ~/wc; tar czf s.tgz src; zip -qr s.zip src; tar tzf s.tgz | wc -l; unzip -l s.zip | tail -1 | awk '{print $2}'", why='Look inside before extracting.'),
        dict(title='Preview a copy: cp -n vs cp -u', setup=WC, cmd="cd ~/wc; cp -a src/. backup/; echo new > src/a.txt; cp -nv src/* backup/ 2>&1 | wc -l; cp -uv src/* backup/ | sed \"s/'//g; s|/home/riya|~|g\"", why='-n never overwrites; -u only newer files (a poor man’s rsync).'),
    ]),
    ('Processes and time', [
        dict(title='Find a process: pgrep vs ps | grep', cmd="sleep 30 & pgrep -c -x sleep -P $$; ps aux | grep -c '[s]leep 30'; kill %1", why='pgrep never matches itself.'),
        dict(title='Wait: sleep vs timeout', cmd="timeout 1 sleep 5; echo \"timeout stopped it: $?\"", why='timeout limits a command; sleep only waits.'),
        dict(title='Once later: at (shown) vs sleep', cmd="echo 'echo backup | at 23:00     # once, survives logout'; echo 'sleep 3600 && backup.sh     # dies with the terminal'", why='at is for one-off scheduled jobs (Lesson 17.4).'),
        dict(title='Repeat: cron line vs timer (shown)', cmd="echo '0 2 * * * /opt/backup.sh            # cron: simple'; echo 'OnCalendar=*-*-* 02:00:00, Persistent=true  # timer: logs, catch-up'", why='Choose timers when you need logs and missed-run catch-up.'),
        dict(title='Watch a command: watch vs a loop', cmd="for i in 1 2 3; do date +%S | sed 's/.*/tick/'; sleep 0.3; done", why='watch -n 2 cmd does this with a full-screen view.'),
        dict(title='How long did it take? time', cmd="TIMEFORMAT='%R s'; time (sleep 0.3) 2>&1 | sed -E 's/[0-9.]+ s/N s/'", why='time for one run; hyperfine for benchmarks.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Choosing well at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['rsync', 'backups'], 'blue', 8.6), '1. Backups and deployments',
              'Nightly rsync -a --delete to a backup server copies minutes of changes instead of hours of data.', ['Nightly', '*rsync', 'fast backup']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['grep | awk', 'logs'], 'green', 8.6), '2. Log investigations',
    'grep narrows gigabytes to the relevant lines first; awk then computes on the much smaller stream.', ['Huge log', '*grep then awk', 'answer']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['systemctl', 'ops'], 'red', 8.6), '3. Service operations',
    'On-call runbooks say systemctl restart/stop, never kill -9, so systemd and logs stay consistent.', ['Incident', '*systemctl', 'clean state']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['curl', 'APIs'], 'amber', 8.6), '4. API checks and automation',
    'curl -sf health endpoints in scripts; wget -c for big ISO downloads.', ['Check', '*curl / wget', 'result']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['zip', 'sharing'], 'violet', 8.6), '5. Sharing with other teams',
    'tar.gz for Linux servers, zip for colleagues on Windows, sha256sum to prove the copy is intact.', ['Package', '*tar / zip', 'verified']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Lines with a word', scenario='Search.', setup=WC, cmd="grep -c bash ~/wc/users.txt", explain='grep.'),
    dict(level='b', title='One column', scenario='Extract.', setup=WC, cmd="cut -d: -f1 ~/wc/users.txt | head -2", explain='cut.'),
    dict(level='i', title='Condition on a column', scenario='Filter.', setup=WC, cmd="awk -F: '$2<1000{print $1}' ~/wc/users.txt", explain='awk.'),
    dict(level='i', title='Replace safely (preview)', scenario='Change.', setup=WC, cmd="sed 's/8080/9090/' ~/wc/app.conf | diff ~/wc/app.conf - | grep '^[<>]'", explain='sed + diff preview.'),
    dict(level='a', title='What will run?', scenario='Debug.', cmd="type -a echo | head -2", explain='type -a.'),
], extra=build_up('the puzzle, done right', 'Riya redoes the four tasks with the right tools.', WC, [
    ("cd ~/wc; awk -F: '$2>=1000{print $1}' users.txt | paste -sd' '", '1. UID ≥ 1000: awk (numeric condition on a column).'),
    ("cd ~/wc; sed 's/^port=8080$/port=9090/' app.conf | head -1", '2. Replace in config: sed (preview first, then -i).'),
    ("echo 'rsync -a --delete /data/ backup01:/data/   # nightly, only changes'", '3. Nightly copy: rsync (shown: not installed here).'),
    ("echo 'sudo systemctl stop nginx && sudo systemctl disable nginx'", '4. Stop a service: systemctl (shown).'),
], cumulative=False)) + VAR + which('Choosing the right tool (summary).', [
    ('Lines with X', 'grep', 'Fast, simple.', 'awk / sed for plain search.'),
    ('Column with fixed separator', 'cut', 'Shortest.', 'sed regex gymnastics.'),
    ('Condition or maths on columns', 'awk', 'Built for it.', 'grep tricks.'),
    ('Replace text', 'sed', 'One s///.', 'awk gsub for simple cases.'),
    ('Copy again / remote', 'rsync', 'Only changes, resume.', 'cp -r / scp -r every time.'),
    ('Stop a service', 'systemctl', 'Stays stopped, logged.', 'kill -9.'),
]) + keys('One-line rules.', [
    ('grep', 'find lines', 'search'),
    ('cut / awk', 'columns / logic', 'extract'),
    ('sed / tr', 'words / characters', 'change'),
    ('find / locate', 'live / instant', 'files'),
    ('cp / rsync', 'once / again', 'copy'),
    ('kill / pkill / systemctl', 'PID / name / service', 'stop'),
]) + scriptit('whichtool.sh', 'A tiny interactive helper: given a job keyword (search, column, filter, replace, files, copy, compare, stop, schedule), print the recommended command and an example.',
'''job=${1:-copy}
case $job in
  search)   echo "grep PATTERN FILE           e.g. grep -i error app.log" ;;
  column)   echo "cut -d: -fN FILE            e.g. cut -d: -f1 /etc/passwd" ;;
  filter)   echo "awk 'COND' FILE             e.g. awk -F: '\\$3>=1000' /etc/passwd" ;;
  replace)  echo "sed 's/OLD/NEW/g' FILE      e.g. sed -i.bak 's/8080/9090/' app.conf" ;;
  files)    echo "find DIR TESTS | locate NAME e.g. find /var -size +1G" ;;
  copy)     echo "rsync -a SRC/ DST/          e.g. rsync -a --delete data/ backup01:/data/" ;;
  compare)  echo "diff (text) | cmp (binary) | comm (sorted lists)" ;;
  stop)     echo "systemctl stop SVC | pkill -x NAME | kill PID" ;;
  schedule) echo "at (once) | cron or systemd timer (repeat)" ;;
  *)        echo "unknown job: $job (try: search column filter replace files copy compare stop schedule)"; exit 1 ;;
esac''',
'<p>Run without an argument, so it answers “copy”.</p>', expect='any') + puzzle_answer('<b>(1)</b> grep is wrong: “UID at least 1000” is a numeric condition on column 2, so awk: <code>awk -F: \'$2&gt;=1000{print $1}\'</code>. <b>(2)</b> awk works but sed is the tool built for replacing text: <code>sed -i.bak \'s/^port=8080$/port=9090/\' app.conf</code>. <b>(3)</b> <code>cp -r</code> copies all 50 GB every night; <code>rsync -a --delete src/ server:dst/</code> sends only the changes and can resume. <b>(4)</b> nginx is a systemd service with a restart policy: kill makes systemd start it again. Use <code>sudo systemctl stop nginx</code> (and <code>disable</code> if it must stay off).') + qc('One-line rule for cp vs rsync?', 'cp for a one-time local copy; rsync whenever you copy again or over the network.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/wc', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../06-text-processing/">Module 6</a> (grep, sed, awk) and the previous lessons of this module.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
