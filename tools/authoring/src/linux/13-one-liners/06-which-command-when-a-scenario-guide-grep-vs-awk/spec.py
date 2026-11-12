import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='13-one-liners', lesson='06-which-command-when-a-scenario-guide-grep-vs-awk', n='13.6',
    module_label='Module 13 · Power one-liners and command combos',
    title='Which command when? A scenario guide: grep vs awk vs sed, find vs locate, cp vs rsync and more',
    desc='A scenario guide for choosing Linux commands: grep vs cut vs awk vs sed vs tr, find vs locate, cp vs rsync, scp vs rsync vs sftp, tar vs zip, gzip vs xz, curl vs wget, kill vs pkill vs systemctl, diff vs cmp vs comm vs sha256sum, which vs type vs whereis, sort -u vs uniq, at vs cron vs systemd timers; side-by-side real runs on the same input and one-line rules; 30+ examples.',
    og_desc='Which Linux command when? Side-by-side real runs: grep vs awk vs sed, find vs locate, cp vs rsync, kill vs systemctl and more.',
    minutes=35, level='Beginner → Advanced',
    lead='Knowing commands is half the skill; choosing is the other half. Name the job, then pick the smallest tool built for it: side-by-side comparisons on the same input, with real output.',
    chips=['Master decision chart', 'Side-by-side runs', 'Decision tree animated', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# One file, four questions, four tools
cat > users.txt <<'EOF'
riya:1001:/home/riya:/bin/bash
aman:1002:/home/aman:/bin/zsh
backup:34:/var/backups:/usr/sbin/nologin
EOF
echo "grep (lines with bash):";   grep bash users.txt
echo "cut (first column):";       cut -d: -f1 users.txt
echo "awk (UID >= 1000):";        awk -F: '$2>=1000 {print $1}' users.txt
echo "sed (zsh -> bash):";        sed 's#/bin/zsh#/bin/bash#' users.txt | grep aman
"""

RUN = dict(
    heading='The same file, the right tool for each question',
    intro='<p>Search, extract, filter by a number and replace: one tool each.</p>',
    code=MAIN,
    anno=[("awk -F: '$2>=1000'", 'A numeric condition on a column: awk’s job.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which question could grep not answer?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do cut and awk print for this line?',
             code="echo 'a   b  c' | cut -d' ' -f2\necho 'a   b  c' | awk '{print $2}'\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> uniq misses a duplicate. Sort first.',
             code="printf 'b\\na\\nb\\n' | uniq\n"),
        dict(label='4 · Your turn', hint='Find whether two files are identical with cmp.',
             code="echo hello > a; echo hello > b; echo world > c\ncmp a b && echo 'a = b'\ncmp a c || echo 'a ≠ c'\n"),
        dict(label='5 · Challenge', hint='Use type to find out what kind of command each is.',
             code="for c in cd echo ls type; do printf '%-5s %s\\n' $c \"$(type -t $c)\"; done\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the tools missing from our build machine',
    intro='<p>rsync, scp and locate are not installed on our build machine, so these are <b>typical</b> outputs from a normal Ubuntu machine.</p>',
    items=[
        dict(title='1 · locate (instant name search)', cmd='sudo apt install plocate && sudo updatedb\nlocate -i nginx.conf', output='/etc/nginx/nginx.conf\n/usr/share/doc/nginx/examples/nginx.conf', note='Typical.'),
        dict(title='2 · rsync dry run, then real', cmd='rsync -avn --delete ~/project/ /backup/project/\nrsync -av --delete ~/project/ /backup/project/', output='sending incremental file list\nsrc/app.py\n\nsent 1,204 bytes  received 35 bytes\ntotal size is 52,428,800  speedup is 42,315.17', note='Typical: only the changed file was sent.'),
        dict(title='3 · Copy to a server', cmd='scp report.pdf you@server:/tmp/\nrsync -avz --progress bigdir/ you@server:/data/bigdir/', output='report.pdf     100%  812KB   2.1MB/s   00:00', note='Typical.'),
        dict(title='4 · Tools here', cmd='type grep sed awk cut', output=pc('type grep sed awk cut'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Choosing in a script, line by line',
    intro='<p>Step through a tiny chooser.</p>',
    code='''job=filter
case $job in
  search) tool=grep ;;
  column) tool=cut ;;
  filter) tool=awk ;;
  replace) tool=sed ;;
esac
echo "for $job use $tool"
''',
    notes={2: 'case picks one branch.', 5: 'filter → awk.'},
)

WORKED_INTRO = 'Three choices from real jobs, each solved with the right tool.'
EXAMPLES = [
    dict(level='b', tag='Support', title='Search, then count',
         problem='<p>How many log lines mention “timeout”, and which services wrote them?</p>',
         inp='a log', approach=['grep -c to count.', 'grep then awk for the field.'],
         code='''printf '%s\\n' 'db timeout 5s' 'web ok' 'db timeout 3s' 'cache timeout 1s' > app.log
grep -c timeout app.log
grep timeout app.log | awk '{print $1}' | sort | uniq -c
''', notes={2: 'grep alone counts.', 3: 'awk only for the field.'}, tryit='Show only services with more than one timeout.'),
    dict(level='i', tag='Ops', title='Replace a value only for some rows',
         problem='<p>Change the shell to /bin/bash only for users with UID ≥ 1000.</p>',
         inp='passwd-like file', approach=['A condition on a column: awk.'],
         code='''printf 'root:0:/bin/sh\\nriya:1001:/bin/sh\\naman:1002:/bin/zsh\\n' > u.txt
awk -F: -v OFS=: '$2>=1000 {$3="/bin/bash"} 1' u.txt
''', notes={2: 'sed cannot test column 2 easily.'}, tryit='Leave aman’s zsh unchanged.'),
    dict(level='a', tag='DevOps', title='Did anything change? Cheap checks first',
         problem='<p>Decide whether a deployment folder changed, without copying it: compare a manifest of checksums.</p>',
         inp='two folders', approach=['sha256sum manifest.', 'diff the manifests.'],
         code='''mkdir -p v1 v2; echo a > v1/x; echo b > v1/y; cp v1/* v2/; echo c > v2/y
( cd v1 && sha256sum * ) > m1; ( cd v2 && sha256sum * ) > m2
diff m1 m2 > /dev/null && echo "no change" || echo "changed: $(diff m1 m2 | awk '/^>/{print $3}')"
''', notes={2: 'Fingerprints of every file.', 3: 'Only the file names that differ.'}, tryit='Add a file only in v2.'),
]

QUIZ = mix([
    dict(q='Lines that contain “error”:', options=['awk', 'grep', 'sed', 'cut'], answer=1, why='Search: grep.'),
    dict(q='Users with UID > 1000:', options=['grep', 'cut', 'awk', 'tr'], answer=2, why='Numeric condition on a column.'),
    dict(q='Replace foo with bar in a file:', options=['sed', 'grep', 'cut', 'sort'], answer=0, why='s/foo/bar/.'),
    dict(q='Copy a big folder again every night:', options=['cp -r', 'rsync -a', 'mv', 'tar'], answer=1, why='Only changes.'),
    dict(q='Find files by name instantly (index):', options=['find', 'locate', 'grep -r', 'ls -R'], answer=1, why='Database.'),
    dict(q='Stop a systemd service that restarts when killed:', options=['kill -9', 'systemctl stop', 'pkill', 'exit'], answer=1, why='Tell systemd.'),
    dict(q='Are two binaries identical?', options=['diff', 'cmp', 'comm', 'grep'], answer=1, why='Byte comparison.'),
    dict(q='Is ll an alias?', options=['which ll', 'type ll', 'whereis ll', 'locate ll'], answer=1, why='type knows aliases.'),
])

REVISION = [
    'Name the job first: search, extract, filter, compute, change, find files, copy, compare, stop, schedule.',
    'Text: grep (lines), cut (fixed column), awk (column conditions, maths), sed (replace), tr (characters).',
    'Files: find (live, tests) vs locate (index, instant); cp (once) vs rsync (again, remote); tar (Linux) vs zip (Windows); gzip (fast) vs xz (small).',
    'Network: scp (one file) vs rsync (folders, resume) vs sftp (browse); curl (APIs) vs wget (downloads).',
    'Processes: kill (PID) vs pkill (name) vs systemctl (services). Compare: diff (text) vs cmp (binary) vs comm (lists) vs sha256sum (remote).',
    'Identify: type (aliases, built-ins) vs which (PATH) vs whereis (with man pages). Schedule: at (once) vs cron/timers (repeat).',
]

FAQ = [
    ('When should I use awk instead of grep?', 'When you need a condition on a specific column or computation; grep only selects lines.'),
    ('What is the difference between sed and awk?', 'sed edits text (replace, delete lines); awk processes columns and computes.'),
    ('find or locate?', 'find searches live with tests (size, age); locate searches a daily name index instantly.'),
    ('cp or rsync?', 'cp for one local copy; rsync for repeated, large or remote copies (only changes, resume, dry run).'),
    ('scp or rsync?', 'scp for a quick single file; rsync for folders and repeated syncs.'),
    ('curl or wget?', 'curl for APIs and many protocols; wget for downloading files and sites.'),
    ('kill or systemctl stop?', 'systemctl stop for services (otherwise systemd may restart them); kill/pkill for ordinary processes.'),
]

PRACTICE_INTRO = 'Pick-the-tool tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Search', stmt='Count lines containing “ok” in ok / fail / ok.', inp='lines', code="printf 'ok\\nfail\\nok\\n' | grep -c ok\n", explain='2, grep -c.'),
    dict(level='easy', title='Column', stmt='Print the second column of a:b:c.', inp='a line', code="echo 'a:b:c' | cut -d: -f2\n", explain='b, cut.'),
    dict(level='easy', title='Replace', stmt='Replace cat with dog in “cat and cat”.', inp='a line', code="echo 'cat and cat' | sed 's/cat/dog/g'\n", explain='dog and dog, sed.'),
    dict(level='medium', title='Condition', stmt='Print names whose score is above 50 in a 40 / b 70.', inp='lines', code="printf 'a 40\\nb 70\\n' | awk '$2>50{print $1}'\n", explain='b, awk.'),
    dict(level='medium', title='Characters', stmt='Turn commas into newlines in a,b,c.', inp='a line', code="echo 'a,b,c' | tr ',' '\\n'\n", explain='tr.'),
    dict(level='medium', title='Binary compare', stmt='Check whether two copies of the same text are identical with cmp.', inp='files', code="echo x > f1; cp f1 f2; cmp f1 f2 && echo same\n", explain='same.'),
    dict(level='business', title='Unique', stmt='Print the unique values of b a b c a, sorted.', inp='values', code="printf 'b\\na\\nb\\nc\\na\\n' | sort -u | paste -sd' '\n", explain='a b c.'),
    dict(level='business', title='What is it?', stmt='Print what kind of command cd and ls are.', inp='nothing', code="type -t cd; type -t ls\n", explain='builtin, file.'),
]

SCN_INTRO = 'Interview questions about choosing commands, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“grep vs awk vs sed?”', 'The classic.', 'one line each?',
        '''<ul>
          <li>grep: find lines matching a pattern.</li>
          <li>sed: edit text (substitute, delete).</li>
          <li>awk: work with columns, conditions and maths.</li>
        </ul>''', '“they are all the same”.') +
    scn('Service company', 'Junior', 'Nightly copy takes 3 hours', 'cp -r of 200 GB.', 'fix?',
        '''<ol>
          <li>rsync -a --delete: only changes are copied.</li>
          <li>Run from cron/timer; log the output.</li>
          <li>Test with rsync -n first.</li>
        </ol>''', 'a faster disk.') +
    scn('Product company', 'Mid-level', 'A killed service keeps coming back', 'kill -9 used.', 'why?',
        '''<ul>
          <li>systemd Restart=on-failure restarts it.</li>
          <li>systemctl stop (and disable/mask if needed).</li>
          <li>Check systemctl status and the journal.</li>
        </ul>''', 'a cron job that keeps killing it.') +
    scn('Platform', 'Senior', 'Choose a backup strategy for 2 TB', 'Daily, off-site.', 'tools?',
        '''<ul>
          <li>rsync or restic/borg (dedupe, encryption).</li>
          <li>Verify with checksums; test restores.</li>
          <li>Schedule with systemd timers (logs, Persistent=true).</li>
        </ul>''', 'tar the whole disk every night.')
) + interview([
    ('cut vs awk on spaces?', 'cut breaks on runs of spaces; awk handles them.'),
    ('sort -u vs uniq?', 'uniq needs sorted input; sort -u sorts and dedupes.'),
    ('tar vs zip?', 'tar keeps Linux metadata; zip is Windows-friendly.'),
    ('gzip vs xz?', 'gzip faster, xz smaller.'),
    ('which vs type?', 'type also knows aliases, functions and built-ins.'),
    ('cron vs systemd timer?', 'Timers log to the journal, catch up missed runs, have dependencies.'),
    ('diff vs comm?', 'diff compares versions; comm compares sorted lists.'),
], [
    ('RHCSA / LFCS', 'Use the right tool for text, files, archives, scheduling.'),
    ('DevOps interviews', 'rsync, systemctl, curl choices.'),
    ('CompTIA Linux+', 'Command selection scenarios.'),
]) + distro('Most tools exist everywhere; some need installing.', [
    ('locate', 'plocate', 'mlocate/plocate', 'locate (BSD, needs db)', 'Everything (3rd party)'),
    ('rsync', 'apt install rsync', 'dnf install rsync', 'built in (old)', 'WSL / cwRsync'),
    ('scp / sftp', 'openssh-client', 'openssh-clients', 'built in', 'built in (OpenSSH)'),
    ('curl / wget', 'curl usually, wget often', 'curl, wget', 'curl only', 'curl.exe'),
    ('systemctl', 'yes', 'yes', 'launchctl', 'sc / services.msc'),
]) + teaser('13.7', 'Module 13 ends with a cheat sheet and a challenge: 100 must-know one-liners, grouped by job, every one tested, plus a timed quiz. Next: 100 must-know one-liners.')

CHEATSHEET = cheatsheet('Which command', [
    ('Text', [('grep', 'find lines'), ('cut', 'fixed column'), ('awk', 'columns + logic'), ('sed', 'replace'), ('tr', 'characters')]),
    ('Files', [('find / locate', 'live / instant'), ('cp / rsync', 'once / again'), ('tar / zip', 'Linux / Windows'), ('gzip / xz', 'fast / small')]),
    ('Network / processes', [('scp / rsync / sftp', 'copy'), ('curl / wget', 'API / download'), ('kill / pkill', 'PID / name'), ('systemctl', 'services')]),
    ('Compare / identify', [('diff / cmp', 'text / binary'), ('comm', 'sorted lists'), ('sha256sum', 'remote compare'), ('type / which', 'what runs')]),
])

MINDMAP = mindmap('Choose', [
    ('Text', 'blue', ['grep', 'cut awk', 'sed tr']),
    ('Files', 'green', ['find locate', 'cp rsync', 'tar zip']),
    ('Network', 'amber', ['scp rsync', 'sftp', 'curl wget']),
    ('Processes', 'red', ['kill pkill', 'systemctl', 'timeout']),
    ('Compare', 'violet', ['diff cmp', 'comm', 'sha256sum']),
    ('Time', 'acc', ['at', 'cron', 'timers']),
])

LAB = lab('pick the tool', 'Build the lab, write <code>~/lab136/answers.sh</code> using the right tool for each task, then run the checker.',
    setup='''mkdir -p ~/lab136 && cd ~/lab136 && rm -rf answers.sh *.txt out mirror
printf 'web01 10.0.0.1 up 23\\nweb02 10.0.0.2 down 0\\ndb01 10.0.0.9 up 57\\n' > hosts.txt
printf 'mode=dev\\nlog=debug\\n' > app.conf
mkdir -p out; echo one > out/a.txt; echo two > out/b.txt''',
    tasks=['Using grep, write the number of lines with <code>down</code> in hosts.txt into <code>down.txt</code>.',
           'Using awk, write the names of hosts whose last column (load) is greater than 20, one per line, into <code>busy.txt</code>.',
           'Using sed, write a copy of app.conf with <code>mode=dev</code> changed to <code>mode=prod</code> into <code>prod.conf</code> (do not change app.conf).',
           'Using cmp, write <code>same</code> into <code>cmp.txt</code> if <code>out/a.txt</code> and a fresh copy <code>a.copy</code> are identical.'],
    solution='''cat > answers.sh <<'EOF'
cd ~/lab136
grep -c down hosts.txt > down.txt
awk '$4>20{print $1}' hosts.txt > busy.txt
sed 's/^mode=dev$/mode=prod/' app.conf > prod.conf
cp out/a.txt a.copy; cmp -s out/a.txt a.copy && echo same > cmp.txt
EOF''',
    check='''cd ~/lab136; rm -f down.txt busy.txt prod.conf cmp.txt a.copy
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f answers.sh ] && bash answers.sh 2>/dev/null
ok "1 grep" '[ "$(cat down.txt 2>/dev/null)" = 1 ] && grep -q grep answers.sh'
ok "2 awk"  '[ "$(cat busy.txt 2>/dev/null | tr "\\n" " ")" = "web01 db01 " ] && grep -q awk answers.sh'
ok "3 sed"  'grep -qx mode=prod prod.conf 2>/dev/null && grep -qx mode=dev app.conf && grep -q sed answers.sh'
ok "4 cmp"  '[ "$(cat cmp.txt 2>/dev/null)" = same ] && grep -q cmp answers.sh' ''')
