import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='13-one-liners', lesson='01-combining-commands-pipes-subshells-substitution', n='13.1',
    module_label='Module 13 · Power one-liners and command combos',
    title='Combining commands: pipes, &&, ||, ;, subshells, $( ) and <( )',
    desc='How to combine Linux commands: ; && || and exit status, pipelines | and |&, tee, PIPESTATUS and set -o pipefail, subshells ( ) vs groups { }, command substitution $( ), process substitution <( ) and >( ), the piped-while subshell trap, SIGPIPE, and building one-liners stage by stage; real outputs on a web log and 35+ examples.',
    og_desc='Pipes, &&, ||, subshells, $( ) and <( ) explained with real runs: exit status, pipefail and building one-liners step by step.',
    minutes=40, level='Beginner → Advanced',
    lead='Small tools become powerful when you join them. Every operator that combines commands, what decides when each part runs, and the habit of building a one-liner one stage at a time.',
    chips=['Pipeline animated stage by stage', '; vs && after a typo', 'pipefail and PIPESTATUS', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A small web log
printf '%s\\n' '10.0.0.5 "GET /" 200' '10.0.0.7 "GET /login" 401' '10.0.0.5 "GET /admin" 403' '10.0.0.9 "GET /" 200' > access.log

# Pipe: which IPs got errors, most first?
grep -E '" [45][0-9]{2}$' access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn

# && and ||
mkdir -p backup && cp access.log backup/ && echo "backup done"
cd /nope 2>/dev/null || echo "cd failed, staying here"

# $( ) and <( )
echo "lines: $(wc -l < access.log)"
diff <(cut -d' ' -f1 access.log | sort -u) <(echo 10.0.0.5) || true
"""

RUN = dict(
    heading='Pipes, && || and substitutions',
    intro='<p>Answer a question with a pipeline, chain safe steps, and plug outputs into other commands.</p>',
    code=MAIN,
    anno=[('| sort | uniq -c | sort -rn', 'The classic “count and rank” pattern.'), ('diff <(…) <(…)', 'Two command outputs compared as files.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which IP got the most errors?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which lines are printed?',
             code="true && echo A\nfalse && echo B\nfalse || echo C\ntrue || echo D\nfalse ; echo E\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the count should be 3. Use done &lt; file instead of a pipe.',
             code="printf 'a\\nb\\nc\\n' > f.txt\nn=0; cat f.txt | while read -r x; do n=$((n+1)); done; echo \"n=$n\"\n"),
        dict(label='4 · Your turn', hint='Make the pipeline report the grep failure with pipefail.',
             code="set -o pipefail\ngrep x /nope 2>/dev/null | wc -l\necho \"status: $?\"\n"),
        dict(label='5 · Challenge', hint='Use a { } group to write three lines into one file with one redirect.',
             code="{ echo \"user: $USER\"; echo \"date: $(date +%F)\"; echo \"files: $(ls | wc -l)\"; } > info.txt\ncat info.txt\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own logs',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Who logged in most (needs sudo)', cmd="sudo journalctl -u ssh --since today | grep 'Accepted' | awk '{print $9}' | sort | uniq -c | sort -rn | head -3", output='     12 vineeta\n      3 deploy', note='Typical.'),
        dict(title='2 · Biggest folders in your home', cmd='du -sh ~/* 2>/dev/null | sort -rh | head -5', output='4.1G\t/home/you/Videos\n1.2G\t/home/you/Downloads\n…', note='Typical (Lesson 13.4).'),
        dict(title='3 · Compare installed packages on two machines', cmd="diff <(ssh pc1 'dpkg -l | awk \"/^ii/{print \\$2}\"') <(ssh pc2 'dpkg -l | awk \"/^ii/{print \\$2}\"')", output='< htop\n> tmux', note='Typical.'),
        dict(title='4 · bash version', cmd='bash --version | head -1', output=pc('bash --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Exit status deciding, line by line',
    intro='<p>Step through: each operator looks at the status before it.</p>',
    code='''ok=0; skipped=0
true && ok=$((ok+1))
false && ok=$((ok+1))
false || skipped=$((skipped+1))
false | true
last=$?
echo "ok=$ok skipped=$skipped pipeline=$last"
''',
    notes={2: 'Runs: true succeeded.', 3: 'Skipped: false failed.', 4: 'Runs: false failed.', 5: 'Status is true’s: 0.'},
)

WORKED_INTRO = 'Three combined commands from real jobs: a safe deploy, a config drift check and a status summary.'
EXAMPLES = [
    dict(level='b', tag='DevOps', title='A safe deploy chain',
         problem='<p>Simulate build, test and restart so that restart never happens after a failed test.</p>',
         inp='three steps', approach=['&& chain.', '|| for the alert.'],
         code='''build(){ echo "building"; }
test_(){ echo "testing"; return ${FAIL:-0}; }
restart(){ echo "restarting app"; }
build && test_ && restart || echo "DEPLOY STOPPED"
FAIL=1; build && test_ && restart || echo "DEPLOY STOPPED"
''', notes={4: 'All pass.', 5: 'Test fails: no restart.'}, tryit='Make build fail instead.'),
    dict(level='i', tag='SRE', title='Config drift between two servers',
         problem='<p>Two servers should have the same settings. Show only the keys whose values differ.</p>',
         inp='two configs', approach=['join on key.', 'awk to compare.'],
         code='''printf 'port=80\\nworkers=4\\nlog=info\\n' > a.conf
printf 'port=80\\nworkers=8\\nlog=debug\\n' > b.conf
join -t= <(sort a.conf) <(sort b.conf) | awk -F= '$2 != $3 {print $1": "$2" vs "$3}'
''', notes={3: 'join by key; awk keeps differences.'}, tryit='Add a key that exists only in b.conf (look at join -a).'),
    dict(level='a', tag='Ops', title='A one-file status summary',
         problem='<p>Write the date, logged-in user count, disk use of / and the 3 largest files in /etc into one report.</p>',
         inp='the system', approach=['{ } group.', '$( ) for numbers.'],
         code='''{
  echo "report $(date +%F)"
  echo "users: $(who | wc -l)"
  echo "root disk: $(df -h / | awk 'NR==2{print $5}')"
  echo "largest in /etc:"; ls -S /etc 2>/dev/null | head -3 | sed 's/^/  /'
} > status.txt
cat status.txt
''', notes={1: 'One redirect for the whole group.'}, tryit='Add the load average from /proc/loadavg.'),
]

QUIZ = mix([
    dict(q='A ; B — B runs…', options=['only if A worked', 'always', 'only if A failed', 'never'], answer=1, why='; ignores status.'),
    dict(q='A && B — B runs…', options=['always', 'if A succeeded', 'if A failed', 'in parallel'], answer=1, why='Status 0.'),
    dict(q='The status of A | B is…', options=['A’s', 'B’s (last)', 'the sum', 'always 0'], answer=1, why='Unless pipefail.'),
    dict(q='Which keeps a cd only inside?', options=['{ cd x; }', '( cd x )', 'cd x &&', 'cd x;'], answer=1, why='Subshell.'),
    dict(q='diff needs files; you have two commands. Use…', options=['$( )', '<( )', '|', '&&'], answer=1, why='Process substitution.'),
    dict(q='Why is n empty after cmd | while read …; do n=…; done?', options=['read failed', 'the loop ran in a subshell', 'n is reserved', 'pipes clear variables'], answer=1, why='Each part is a subshell.'),
    dict(q='Save a copy in the middle of a pipeline:', options=['cp', 'tee', 'cat', 'save'], answer=1, why='tee.'),
    dict(q='Send stderr into a pipe too:', options=['|2', '|&', '||', '&|'], answer=1, why='|& = 2>&1 |.'),
])

REVISION = [
    '; always · && after success · || after failure · $? last status; A && B || C is not if/else.',
    'A | B streams stdout to stdin, all parts in parallel; |& includes stderr; tee saves a copy.',
    'Pipeline status = last part; ${PIPESTATUS[@]} all parts; set -o pipefail for honest status.',
    '( ) subshell: cd/vars/exit stay inside; { …; } current shell: one redirect for many commands.',
    '"$( )" output as text; <( ) output as a file (diff, comm, join, paste); >( ) write into a command.',
    'Build one-liners stage by stage; cmd | while loses variables, use done < <(cmd).',
]

FAQ = [
    ('What is the difference between ; && and || in Linux?', '; runs the next command always, && only if the previous succeeded, || only if it failed.'),
    ('What does a pipe | do?', 'Sends the standard output of one command to the standard input of the next; both run at the same time.'),
    ('What is set -o pipefail?', 'It makes a pipeline return failure if any part fails, not just the last command.'),
    ('What is the difference between ( ) and { } in bash?', '( ) runs commands in a subshell, so changes are lost; { ; } runs them in the current shell.'),
    ('What is process substitution <( )?', 'It runs a command and passes its output as a file name, e.g. diff <(cmd1) <(cmd2).'),
    ('Why is my variable empty after a while loop in a pipe?', 'The loop ran in a subshell; use while … done < <(cmd).'),
    ('What does tee do?', 'Copies its input to a file and to standard output, so a pipeline can continue.'),
]

PRACTICE_INTRO = 'Small combining tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='AND', stmt='Print “ok” only if /etc exists.', inp='nothing', code="[ -d /etc ] && echo ok\n", explain='&&.'),
    dict(level='easy', title='OR', stmt='Print “missing” if /nope does not exist.', inp='nothing', code="[ -e /nope ] || echo missing\n", explain='||.'),
    dict(level='easy', title='Pipe', stmt='Count the lines of /etc/hostname with a pipe.', inp='a file', code="cat /etc/hostname | wc -l\n", explain='1.'),
    dict(level='medium', title='Statuses', stmt='Print the statuses of false | true | false.', inp='nothing', code="false | true | false; echo \"${PIPESTATUS[*]}\"\n", explain='1 0 1.'),
    dict(level='medium', title='Subshell', stmt='cd to /tmp in a subshell and show you are still where you were.', inp='nothing', code="here=$PWD; (cd /tmp); [ \"$PWD\" = \"$here\" ] && echo unchanged\n", explain='unchanged.'),
    dict(level='medium', title='Group redirect', stmt='Write a and b into g.txt with one redirect and count its lines.', inp='nothing', code="{ echo a; echo b; } > g.txt; wc -l < g.txt\n", explain='2.'),
    dict(level='business', title='Count and rank', stmt='Count words in “b a b c b a” and print the most frequent.', inp='words', code="echo 'b a b c b a' | tr ' ' '\\n' | sort | uniq -c | sort -rn | head -1\n", explain='3 b.'),
    dict(level='business', title='Common lines', stmt='Print lines common to (x y z) and (y z w) with comm and <( ).', inp='two lists', code="comm -12 <(printf 'x\\ny\\nz\\n') <(printf 'w\\ny\\nz\\n' | sort)\n", explain='y, z.'),
]

SCN_INTRO = 'Interview questions about combining commands, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is a pipe?”', 'Very common.', 'example?',
        '''<ul>
          <li>| connects stdout of one command to stdin of the next.</li>
          <li>ps aux | grep nginx; cat f | sort | uniq -c.</li>
          <li>Both run at the same time.</li>
        </ul>''', '“it saves output to a file”.') +
    scn('Service company', 'Junior', '“How do you find the top 5 IPs in an access log?”', 'Classic.', 'one-liner?',
        '''<ol>
          <li>awk '{print $1}' access.log</li>
          <li>| sort | uniq -c | sort -rn | head -5</li>
          <li>Explain why sort comes before uniq.</li>
        </ol>''', 'opening it in Excel.') +
    scn('Product company', 'Mid-level', 'CI passes although a step failed', 'Step was … | tee log.', 'why?',
        '''<ul>
          <li>tee succeeded, so the pipeline status was 0.</li>
          <li>set -o pipefail (and -e).</li>
          <li>Check PIPESTATUS when needed.</li>
        </ul>''', 'removing tee.') +
    scn('Platform', 'Senior', 'Detect config drift across a fleet', 'No config management yet.', 'quick approach?',
        '''<ul>
          <li>diff &lt;(ssh a cat f) &lt;(ssh b cat f) per host pair.</li>
          <li>Or checksums: ssh h sha256sum f | sort | uniq -c.</li>
          <li>Then move to Ansible.</li>
        </ul>''', 'copying files by hand.')
) + interview([
    ('What does |& do?', 'Pipes stderr as well.'),
    ('What is $?', 'Exit status of the last command.'),
    ('What is PIPESTATUS?', 'Array of statuses of the last pipeline.'),
    ('$( ) vs <( )?', 'Text vs file name.'),
    ('Why sort before uniq?', 'uniq only merges adjacent duplicates.'),
    ('What is SIGPIPE?', 'Sent when writing to a pipe nobody reads; status 141.'),
    ('How to keep variables from a loop over output?', 'done < <(cmd) or lastpipe.'),
], [
    ('RHCSA (EX200)', 'Use input-output redirection and pipes.'),
    ('LFCS', 'Pipes, redirection, command chaining.'),
    ('CompTIA Linux+', 'Command chaining and substitution.'),
]) + distro('Operators are shell features: the same in bash on every distribution.', [
    ('| ; && ||', 'all shells', 'all shells', 'all shells', 'PowerShell: | ; && || (7+)'),
    ('$( )', 'all POSIX', 'all', 'all', '$( ) in PowerShell means something else'),
    ('<( ) >( )', 'bash, zsh', 'bash, zsh', 'bash, zsh', '-'),
    ('|& PIPESTATUS', 'bash', 'bash', 'bash (zsh: pipestatus)', '-'),
    ('/bin/sh (dash)', 'no <( ), no pipefail (dash 0.5.12+: yes)', '-', '-', '-'),
]) + teaser('13.2', 'Riya must rename 2,000 photos, delete logs older than 30 days and replace an old server name in 400 config files. Doing it by hand would take a day. Next: find with -exec and xargs, the bulk-action one-liners.')

CHEATSHEET = cheatsheet('Combining', [
    ('Lists', [('A ; B', 'always'), ('A && B', 'after success'), ('A || B', 'after failure'), ('$?', 'status')]),
    ('Pipes', [('A | B', 'stdout'), ('A |& B', '+stderr'), ('| tee f |', 'copy'), ('PIPESTATUS', 'all'), ('set -o pipefail', 'strict')]),
    ('Groups', [('( … )', 'subshell'), ('{ …; }', 'this shell'), ('(cd d && x)', 'safe cd'), ('{ … } > f', 'one redirect')]),
    ('Substitution', [('"$(cmd)"', 'as text'), ('<(cmd)', 'as file'), ('>(cmd)', 'write into'), ('done < <(cmd)', 'loop')]),
])

MINDMAP = mindmap('Combining', [
    ('Status', 'blue', ['0 = ok', '$?', 'PIPESTATUS']),
    ('Lists', 'green', [';', '&&', '||']),
    ('Pipes', 'amber', ['|', '|&', 'tee']),
    ('Groups', 'violet', ['( )', '{ ; }', 'scope']),
    ('Substitute', 'acc', ['$( )', '<( )', '>( )']),
    ('Traps', 'red', ['; after cd', 'pipe status', 'while subshell']),
])

LAB = lab('answer with one-liners', 'Build the lab, write <code>~/lab131/answers.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab131 && cd ~/lab131 && rm -f answers.sh *.txt
printf '%s\\n' 'riya,pune,OK' 'aman,delhi,FAIL' 'zoya,pune,OK' 'neha,delhi,FAIL' 'ravi,mumbai,FAIL' > results.csv
printf 'pune\\nmumbai\\nchennai\\n' > cities.txt''',
    tasks=['Write the number of lines with <code>FAIL</code> into <code>fails.txt</code> using a pipeline (grep | wc -l or grep -c).',
           'Write the city with the most FAIL lines (just the name) into <code>topcity.txt</code>.',
           'Write the cities that appear in <code>cities.txt</code> but never in <code>results.csv</code> into <code>unused.txt</code>, using comm and process substitution.',
           'Create a folder <code>out</code> and copy <code>results.csv</code> into it in one line, so that the copy only happens if mkdir succeeded, and then write <code>done</code> into <code>status.txt</code>.'],
    solution='''cat > answers.sh <<'EOF'
grep -c FAIL results.csv > fails.txt
grep FAIL results.csv | cut -d, -f2 | sort | uniq -c | sort -rn | awk 'NR==1{print $2}' > topcity.txt
comm -23 <(sort cities.txt) <(cut -d, -f2 results.csv | sort -u) > unused.txt
mkdir -p out && cp results.csv out/ && echo done > status.txt
EOF''',
    check='''cd ~/lab131; rm -rf out *.txt.bak; rm -f fails.txt topcity.txt unused.txt status.txt
printf 'pune\\nmumbai\\nchennai\\n' > cities.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f answers.sh ] && bash answers.sh 2>/dev/null
ok "1 fails"   '[ "$(cat fails.txt 2>/dev/null)" = 3 ]'
ok "2 top"     '[ "$(cat topcity.txt 2>/dev/null)" = delhi ]'
ok "3 unused"  '[ "$(cat unused.txt 2>/dev/null)" = chennai ] && grep -q "<(" answers.sh'
ok "4 chain"   '[ -f out/results.csv ] && [ "$(cat status.txt 2>/dev/null)" = done ] && grep -q "&&" answers.sh' ''')
