import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='05-your-first-shell-script', n='12.5',
    module_label='Module 12 · The shell environment and shell programming',
    title='Your first shell script: shebang, chmod +x and running it',
    desc='What a shell script is; the shebang (#!/bin/bash, #!/usr/bin/env bash, #!/bin/sh = dash on Ubuntu), comments, variables and multiple commands; chmod +x; four ways to run (./script, bash script, source, by name from ~/bin); exit and exit status; first-script errors decoded with real outputs: Permission denied, command not found, CRLF “required file not found”, wrong shebang; the syllabus dbda/file1..file100 one-liner; animations.',
    og_desc='Write and run your first Bash script: #!/bin/bash, chmod +x, ./script, exit codes and the Windows CRLF error, with real outputs.',
    minutes=35, level='Beginner → Advanced',
    lead='A shell script is your commands saved in a file, with a #! first line and execute permission. This lesson writes one from scratch, runs it four ways, returns exit codes, and decodes every first-day error.',
    chips=['#! animated', 'CRLF trap solved', 'Four ways to run', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Write a script, make it executable, run it
cat > hello.sh <<'EOF'
#!/bin/bash
# hello.sh: my first script
name="Riya"
echo "Hello, $name!"
echo "You are in $PWD"
EOF
chmod +x hello.sh
./hello.sh
echo "exit status: $?"
"""

RUN = dict(
    heading='Your first script',
    intro='<p>Create hello.sh with a here-document, make it executable and run it.</p>',
    code=MAIN,
    anno=[('chmod +x hello.sh', 'Without this: Permission denied.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is the exit status?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what status does this script return? Then run.',
             code="printf '#!/bin/bash\\necho a\\nfalse\\n' > s.sh\nbash s.sh; echo \"status $?\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the script should run with ./. Add the missing step.',
             code="printf '#!/bin/bash\\necho ok\\n' > t.sh\n./t.sh\n", expect='any'),
        dict(label='4 · Your turn', hint='Make a script that ends with exit 3 and print the status.',
             code="printf '#!/bin/bash\\necho bye\\nexit 3\\n' > x.sh\nbash x.sh; echo \"status $?\"\n"),
        dict(label='5 · Challenge', hint='The syllabus task: folder test with file1 … file100 in one command.',
             code="mkdir -p dbda/test && touch dbda/test/file{1..100}\nls dbda/test | wc -l\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your first script for real',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Make ~/bin and a tool in it', cmd="mkdir -p ~/bin && printf '#!/bin/bash\\necho \"tool runs\"\\n' > ~/bin/mytool && chmod +x ~/bin/mytool && source ~/.profile && mytool", output='tool runs', note='Typical (Ubuntu’s .profile adds ~/bin when it exists).'),
        dict(title='2 · Where is bash?', cmd='command -v bash; ls -l /bin/sh', output='/usr/bin/bash\nlrwxrwxrwx 1 root root 4 Mar 31  2024 /bin/sh -> dash', note='Typical Ubuntu.'),
        dict(title='3 · Fix a Windows script', cmd="sudo apt install dos2unix && dos2unix report.sh", output='dos2unix: converting file report.sh to Unix format...', note='Typical.'),
        dict(title='4 · Scripts among your commands', cmd="file /usr/bin/* | grep -c 'shell script'", output=pc("file /usr/bin/* 2>/dev/null | grep -c 'shell script'"), note='Recorded on our build machine.'),
    ],
)

TRACE = dict(
    heading='A script line by line',
    intro='<p>Step through a tiny report script: settings, two commands, a summary.</p>',
    code='''log=web.log
printf 'GET 200\\nGET 500\\nGET 200\\n' > "$log"
total=$(wc -l < "$log")
errors=$(grep -c ' 500$' "$log")
echo "requests $total, errors $errors"
''',
    notes={1: 'Setting at the top.', 2: 'Sample data.', 3: 'Count lines.', 4: 'Count 500s.', 5: 'Summary.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a setup script, a check script and the syllabus lab.'
EXAMPLES = [
    dict(level='b', tag='Syllabus', title='dbda and 100 files in one command',
         problem='<p>Create a folder dbda, inside it test, and 100 files file1 … file100, all in one command (the course lab does it as root under /).</p>',
         inp='nothing', approach=['mkdir -p.', 'touch with {1..100}.'],
         code='''mkdir -p dbda/test && touch dbda/test/file{1..100}
ls dbda/test | wc -l
ls dbda/test | sort -V | head -3
''', notes={1: 'One command line.', 2: '100.', 3: 'sort -V: natural order.'}, tryit='As root: sudo mkdir -p /dbda/test && sudo touch /dbda/test/file{1..100}'),
    dict(level='i', tag='Admin', title='A check script with an exit status',
         problem='<p>Exit 0 if a log exists and is not empty, 1 otherwise.</p>',
         inp='a log', approach=['[ -s file ].', 'exit 1 on failure.'],
         code='''printf 'line\\n' > app.log
cat > check.sh <<'EOF'
#!/bin/bash
[ -s app.log ] || { echo "log missing or empty"; exit 1; }
echo "log ok"
EOF
bash check.sh; echo "status $?"
: > app.log; bash check.sh; echo "status $?"
''', notes={7: 'OK :: 0.', 8: 'Empty :: 1.'}, tryit='Use the script in && and ||.'),
    dict(level='a', tag='DevOps', title='A setup script you can run twice',
         problem='<p>Write a setup script that creates folders and a config only if missing, so running it again changes nothing.</p>',
         inp='nothing', approach=['mkdir -p.', '[ -f ] || create.'],
         code='''cat > setup.sh <<'EOF'
#!/bin/bash
mkdir -p app/logs app/data
[ -f app/app.conf ] || echo 'port=8080' > app/app.conf
echo "setup done: $(ls app | tr '\\n' ' ')"
EOF
bash setup.sh; bash setup.sh
''', notes={7: 'Second run :: same result.'}, tryit='Change port in app.conf and run again.'),
]

QUIZ = mix([
    dict(q='What must the first line of a bash script be?', options=['#bash', '#!/bin/bash', '//bash', 'bash:'], answer=1, why='Shebang.'),
    dict(q='./s.sh says Permission denied. Fix?', options=['sudo ./s.sh', 'chmod +x s.sh', 'rename to s.bash', 'source it'], answer=1, why='Execute bit.'),
    dict(q='Which runs a script without execute permission?', options=['./s.sh', 'bash s.sh', 's.sh', 'exec s.sh'], answer=1, why='bash reads it.'),
    dict(q='Which keeps a cd from the script in your shell?', options=['./s.sh', 'bash s.sh', 'source s.sh', 'sh s.sh'], answer=2, why='Same shell.'),
    dict(q='“cannot execute: required file not found” on a file that exists usually means…', options=['disk full', 'wrong interpreter on line 1 or Windows line endings', 'no x', 'wrong owner'], answer=1, why='#! line.'),
    dict(q='Is the .sh extension required?', options=['yes', 'no', 'only for bash', 'only for root'], answer=1, why='Convention.'),
    dict(q='Exit status of a script with no exit line?', options=['always 0', 'that of the last command', '1', '255'], answer=1, why='Last command.'),
    dict(q='Why ./ before the name?', options=['it is required syntax', 'the current folder is not in PATH', 'it makes it faster', 'it runs as root'], answer=1, why='Safety.'),
])

REVISION = [
    'A script: text file of commands; line 1 <code>#!/bin/bash</code>; <code>#</code> comments; settings at the top.',
    '<code>chmod +x</code> then <code>./s.sh</code>; <code>bash s.sh</code> needs no x; <code>source</code> runs in your shell; tools in ~/bin run by name.',
    '<code>exit N</code>: 0 success, 1–255 failure; default = last command’s status; scripts continue after errors unless set -e.',
    '126 = not executable, 127 = not found (or bad #!), 2 = syntax; <code>bash -n</code> checks.',
    'Windows CRLF → “required file not found”: <code>sed -i \'s/\\r$//\'</code> or dos2unix.',
    '.sh is optional; #!/bin/sh is dash on Ubuntu.',
]

FAQ = [
    ('How do I create and run a shell script in Linux?', 'Write commands in a file starting with #!/bin/bash, run chmod +x file.sh, then ./file.sh.'),
    ('What is a shebang?', 'The #! first line that tells the kernel which interpreter runs the file, e.g. #!/bin/bash.'),
    ('Why do I get Permission denied running my script?', 'It lacks execute permission: chmod +x script.sh, or run bash script.sh.'),
    ('What is the difference between ./script.sh and bash script.sh?', './ uses the shebang and needs execute permission; bash script.sh runs it with bash regardless.'),
    ('What does “required file not found” mean for a script that exists?', 'The interpreter in the shebang cannot be found, usually because of Windows CRLF line endings or a typo.'),
    ('How do I return an error from a script?', 'exit 1 (any non-zero number up to 255).'),
    ('Do shell scripts need the .sh extension?', 'No; it is only a naming convention.'),
]

PRACTICE_INTRO = 'Small script tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Hello', stmt='Write and run a script that prints Hello CDAC.', inp='nothing', code="printf '#!/bin/bash\\necho \"Hello CDAC\"\\n' > h.sh; bash h.sh\n", explain='bash h.sh.'),
    dict(level='easy', title='Executable', stmt='Make a script executable and run it with ./', inp='nothing', code="printf '#!/bin/bash\\necho ran\\n' > r.sh; chmod +x r.sh; ./r.sh\n", explain='chmod +x.'),
    dict(level='easy', title='Status', stmt='A script that exits 5: print its status.', inp='nothing', code="printf 'exit 5\\n' > e.sh; bash e.sh; echo $?\n", explain='exit 5.'),
    dict(level='medium', title='Variables', stmt='A script with name=CDAC and city=Mumbai printing “CDAC Mumbai”.', inp='nothing', code="printf 'name=CDAC\\ncity=Mumbai\\necho \"$name $city\"\\n' > v.sh; bash v.sh\n", explain='Variables.'),
    dict(level='medium', title='Multiple commands', stmt='A script that prints the date year and the number of files in /etc (just “ok” if more than 10).', inp='nothing', code="printf 'date +%%Y\\n[ $(ls /etc | wc -l) -gt 10 ] && echo ok\\n' > m.sh; bash m.sh\n", explain='Several commands.'),
    dict(level='medium', title='Syntax check', stmt='Check a script with an unclosed quote without running it.', inp='a file', code="printf 'echo \"oops\\n' > bad.sh; bash -n bad.sh 2>&1 | grep -c 'unexpected EOF'\n", explain='bash -n.'),
    dict(level='business', title='CRLF fix', stmt='Fix a CRLF script and run it.', inp='a CRLF file', code="printf '#!/bin/bash\\r\\necho fixed\\r\\n' > c.sh; chmod +x c.sh\nsed -i 's/\\r$//' c.sh; ./c.sh\n", explain='sed.'),
    dict(level='business', title='Source', stmt='Load DEPT=analytics from a file into this shell.', inp='a file', code="echo 'DEPT=analytics' > d.env; source d.env; echo $DEPT\n", explain='source.'),
]

SCN_INTRO = 'Interview questions about first scripts, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Write a Hello World script and run it”', 'Often on paper.', 'every step?',
        '''<ul>
          <li><code>#!/bin/bash</code> / <code>echo "Hello World"</code>.</li>
          <li><code>chmod +x hello.sh</code>.</li>
          <li><code>./hello.sh</code> (or <code>bash hello.sh</code>).</li>
        </ul>''', 'forgetting the shebang or chmod.') +
    scn('Support', 'Junior', 'Script from a customer fails: required file not found', 'The file exists.', 'CRLF?',
        '''<ol>
          <li><code>file script.sh</code>: “with CRLF line terminators”.</li>
          <li><code>sed -i 's/\\r$//' script.sh</code>.</li>
          <li>Ask them to save with LF (Git: core.autocrlf).</li>
        </ol>''', 'reinstalling bash.') +
    scn('DevOps', 'Mid-level', 'CI step passes although the script failed halfway', 'A deploy script printed errors but CI is green.', 'exit codes?',
        '''<ul>
          <li>Scripts continue after errors and return the last command’s status.</li>
          <li>Add <code>set -euo pipefail</code> (Lesson 12.6) and explicit <code>exit 1</code> checks.</li>
          <li>CI reads only the exit status.</li>
        </ul>''', 'grepping the log for “error”.') +
    scn('Platform', 'Senior', 'A script works on Linux but not on Mac', '#!/bin/bash and bash 5 features.', 'portability?',
        '''<ul>
          <li>macOS ships bash 3.2 at /bin/bash; use <code>#!/usr/bin/env bash</code> with a newer bash, or write POSIX sh.</li>
          <li>Avoid GNU-only options (sed -i differences).</li>
          <li>Test in CI on both.</li>
        </ul>''', 'assuming every Unix is Ubuntu.')
) + interview([
    ('What is a shebang?', '#! plus the interpreter path on line 1.'),
    ('How to make a script executable?', 'chmod +x script.'),
    ('./script vs source script?', 'New process vs current shell.'),
    ('What does exit 0 mean?', 'Success.'),
    ('How to check syntax?', 'bash -n script.'),
    ('Why ./?', 'The current folder is not in PATH.'),
    ('What is #!/usr/bin/env bash?', 'Runs the first bash found in PATH.'),
], [
    ('RHCSA (EX200)', '“Create simple shell scripts”.'),
    ('LFCS', 'Write and run basic shell scripts.'),
    ('CompTIA Linux+', 'Shell script basics: shebang, permissions, exit codes.'),
]) + distro('The same everywhere, except the default shells.', [
    ('#!/bin/bash', 'bash 5', 'bash 5', 'bash 3.2 (old)', 'Git Bash / WSL'),
    ('/bin/sh', 'dash', 'bash', 'bash 3.2 (sh mode)', '-'),
    ('chmod +x', 'yes', 'yes', 'yes', 'WSL: yes'),
    ('Line endings', 'LF', 'LF', 'LF', 'CRLF (Windows)!'),
    ('Script type', '.sh', '.sh', '.sh / .command', '.bat / .ps1'),
]) + teaser('12.6', 'Riya’s script printed an error on line 3 and happily carried on to “deploy done”. Can a script stop at the first error, refuse to use empty variables, and show every line as it runs? Next: set -e, set -u, set -x and other shell options.')

CHEATSHEET = cheatsheet('First script', [
    ('Write', [('#!/bin/bash', 'line 1'), ('# comment', 'explain'), ('name=value', 'settings'), ('exit 0', 'status')]),
    ('Run', [('chmod +x s.sh', 'once'), ('./s.sh', 'normal'), ('bash s.sh', 'no x'), ('source s.sh', 'same shell'), ('~/bin/s', 'by name')]),
    ('Check', [('bash -n', 'syntax'), ('bash -x', 'trace'), ('echo $?', 'status'), ('file s.sh', 'CRLF?')]),
    ('Errors', [('126', 'no x'), ('127', 'not found / bad #!'), ('2', 'syntax'), ("sed -i 's/\\r$//'", 'fix CRLF')]),
])

MINDMAP = mindmap('Script', [
    ('File', 'blue', ['#!/bin/bash', '# comments', 'commands']),
    ('Allow', 'green', ['chmod +x', 'umask', 'u+x']),
    ('Run', 'amber', ['./s.sh', 'bash s.sh', 'source']),
    ('Status', 'red', ['exit 0', 'exit 1', '$?']),
    ('Errors', 'violet', ['126 127', 'CRLF', 'bash -n']),
    ('Grow', 'acc', ['~/bin', 'cron', 'Git']),
])

LAB = lab('a daily report script', 'Build the lab, write <code>~/lab125/report.sh</code> doing the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab125 && cd ~/lab125 && rm -f report.sh summary.txt
printf 'GET /a 200\\nGET /b 500\\nGET /c 200\\nGET /d 500\\nGET /e 404\\n' > web.log''',
    tasks=['Start the script with the bash shebang and make it executable.',
           'Make it write a line <code>requests: N</code> (N = lines in web.log) into <code>summary.txt</code>.',
           'Make it append a line <code>errors: N</code> (N = lines ending in 500).',
           'Make it exit with status 1 when there are any 500 errors, 0 otherwise.'],
    solution='''cat > report.sh <<'EOF'
#!/bin/bash
total=$(wc -l < web.log)
errors=$(grep -c ' 500$' web.log)
echo "requests: $total" > summary.txt
echo "errors: $errors" >> summary.txt
[ "$errors" -gt 0 ] && exit 1
exit 0
EOF
chmod +x report.sh''',
    check='''cd ~/lab125; rm -f summary.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -x report.sh ] && ./report.sh; st=$?
ok "1 shebang" '[ -x report.sh ] && [ "$(head -1 report.sh)" = "#!/bin/bash" ]'
ok "2 total"   'grep -qx "requests: 5" summary.txt 2>/dev/null'
ok "3 errors"  'grep -qx "errors: 2" summary.txt 2>/dev/null'
ok "4 status"  '[ "$st" = 1 ]' ''')
