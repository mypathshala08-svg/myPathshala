import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)
_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index("SS = r'''") + 9
SS = _s[_i:_s.index("'''", _i)]

META = dict(
    module='03-robust-scripts', lesson='02-locks-timeouts-and-running-only-once', n='3.2',
    module_label='Module 3 · Robust scripts',
    title='Locks, timeouts and running only once',
    desc='Stop overlapping runs and hangs in Bash: a real race condition with lost updates, flock -n / -w / -s / -u and the exec 9>file pattern, mkdir locks with stale-lock checks, noclobber, timeout with -k and exit code 124, whole-script deadlines, and idempotent steps for safe reruns, with every run real.',
    og_desc='flock, mkdir locks, timeout and idempotent steps for Bash and cron jobs, shown with a real race condition.',
    minutes=35, level='Intermediate → Advanced',
    lead='One copy at a time, nothing runs forever, and any rerun is safe.',
    chips=['A real race condition', 'flock released after kill -9', 'timeout and 124', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """counter=0
work() {          # read, think, write: a read-modify-write
  local n=$counter
  sleep 0.05
  counter=$(( n + 1 ))
}
for i in 1 2 3; do work; done
echo "one after another: $counter"

# a time limit for a slow step (simulated with a loop and SECONDS)
SECONDS=0; limit=1
until (( SECONDS >= limit )); do sleep 0.2; done
echo "stopped after the $limit s limit"
"""

RUN = dict(
    heading='Read-modify-write and a deadline',
    intro='<p>The browser runs one copy, so no race here; the steps show the pattern and a simple deadline. The real race and flock run in the cards below.</p>',
    code=MAIN,
    anno=[('local n=$counter', 'Read.'), ('counter=$(( n + 1 ))', 'Write: another copy could have written in between.'), ('SECONDS', 'Bash counts seconds for you.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>.', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does a mkdir lock print the second time?',
             code="mkdir lockdir && echo 'got the lock'\nmkdir lockdir 2>/dev/null || echo 'busy'\nrmdir lockdir\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> check-then-create is two steps. Use mkdir (atomic) instead.',
             code="[[ -e my.lock ]] || touch my.lock\necho 'two copies could both reach this line'\nrm -f my.lock\n"),
        dict(label='4 · Your turn', hint='Make the step idempotent: add the line only once.',
             code="for run in 1 2 3; do grep -qxF 'retention=30' s.conf 2>/dev/null || echo 'retention=30' >> s.conf; done\nwc -l < s.conf\n"),
        dict(label='5 · Challenge', hint='Use noclobber as a lock.',
             code="set -C\n( echo $$ > n.lock ) 2>/dev/null && echo 'lock taken'\n( echo $$ > n.lock ) 2>/dev/null || echo 'busy'\nset +C; rm -f n.lock\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Try flock in two terminals. Outputs below are from our build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Two terminals', cmd="# terminal 1\nflock /tmp/demo.lock -c 'echo got it; sleep 30'\n# terminal 2\nflock -n /tmp/demo.lock -c 'echo got it' || echo busy", output='got it          (terminal 1)\nbusy            (terminal 2)', note='Real behaviour.'),
        dict(title='2 · Who holds it?', cmd="fuser -v /tmp/demo.lock", output='                     USER        PID ACCESS COMMAND\n/tmp/demo.lock:      riya       4211 F.... flock', note='Typical.'),
        dict(title='3 · cron line', cmd="crontab -l", output='*/5 * * * * flock -n /run/lock/report.lock timeout -k 30 270 /home/riya/ops/bin/report.sh >> /home/riya/ops/out/cron.log 2>&1', note='Typical.'),
        dict(title='4 · apt’s lock', cmd="sudo apt install htop   # while another apt runs", output='E: Could not get lock /var/lib/dpkg/lock-frontend. It is held by process 3311 (apt)', note='Typical: the same idea inside apt.'),
    ],
)

TRACE = dict(
    heading='A mkdir lock with clean-up, line by line',
    intro='<p>Take, use and release a portable lock.</p>',
    code='''lock=job.lockdir
if mkdir "$lock" 2>/dev/null; then
  echo "lock taken"
  echo $$ > "$lock/pid"
  echo "working..."
  rm -rf "$lock"
  echo "lock released"
else
  echo "busy"
fi
''',
    notes={2: 'Atomic: create or fail.', 6: 'In a script: do this in trap … EXIT.'},
)

WORKED_INTRO = 'Three jobs made safe against overlap and hangs.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Skip when already running',
         problem='<p>Make a script exit quietly if another copy holds the lock.</p>',
         inp='nothing', approach=['exec 9> + flock -n.'],
         code='''job() { ( exec 9> job.lock; flock -n 9 || { echo "$1: busy, skipping"; exit 0; }; echo "$1: working"; sleep 0.4 ); }
job first & sleep 0.1; job second; wait
''', notes={1: 'Each call is a subshell holding fd 9.'}, tryit='Use flock -w 1 so second waits.'),
    dict(level='i', tag='Data', title='Serialise writers, allow readers',
         problem='<p>Readers share the lock; a writer needs it alone.</p>',
         inp='nothing', approach=['flock -s / -x.'],
         code='''( flock -s data.lock sleep 0.5 ) & sleep 0.1
flock -s -n data.lock true && echo "reader 2: allowed"
flock -x -n data.lock true || echo "writer: must wait"
wait; flock -x -n data.lock true && echo "writer: allowed now"
''', notes={2: 'Shared + shared = ok.', 3: 'Exclusive waits for all readers.'}, tryit='Add -w 1 to the writer.'),
    dict(level='a', tag='SRE', title='Timeout plus retry',
         problem='<p>A step sometimes hangs; give each attempt 0.3 s and retry twice.</p>',
         inp='nothing', approach=['timeout inside a loop, 124 = temporary.'],
         code='''calls=0
step() { (( ++calls )); (( calls < 3 )) && sleep 2; echo "step finished on call $calls"; }
export -f step
for try in 1 2 3; do
  timeout 0.3 bash -c "calls=$((try-1)); step" && break
  echo "try $try: timed out ($?)"
done
''', notes={5: 'Each attempt has its own limit.'}, tryit='Stop after the first success only.'),
]

QUIZ = mix([
    dict(q='Five copies add 1 to a counter of 0 at the same moment. Result?', options=['always 5', 'often less than 5', 'always 1', 'an error'], answer=1, why='Lost updates.'),
    dict(q='flock -n means…', options=['wait forever', 'fail at once if locked', 'no lock', 'new file'], answer=1, why='Non-blocking.'),
    dict(q='A flock lock after kill -9 of its holder is…', options=['stale forever', 'released by the kernel', 'converted', 'kept 1 h'], answer=1, why='Tied to the open file.'),
    dict(q='Why is mkdir a good portable lock?', options=['fast', 'atomic create-or-fail', 'hidden', 'root only'], answer=1, why='One system call.'),
    dict(q='timeout exit code when the limit is reached:', options=['1', '124', '137', '143'], answer=1, why='124.'),
    dict(q='timeout -k 5 30 cmd does…', options=['kill after 5 s', 'TERM at 30 s, KILL 5 s later', 'retry 5 times', 'wait 35 s first'], answer=1, why='Grace period.'),
    dict(q='Idempotent means…', options=['fast', 'same result when repeated', 'runs once a day', 'locked'], answer=1, why='Safe reruns.'),
    dict(q='Lock files should live…', options=['on NFS', 'on a local disk like /run/lock', 'in /etc', 'anywhere'], answer=1, why='flock is unreliable on some NFS.'),
])

REVISION = [
    'Race condition: copies read the same old value and overwrite each other’s updates; check-then-create locks race too.',
    'flock does check-and-take atomically and the kernel releases it on exit (even kill -9).',
    'flock -n (skip), -w N (wait with a limit), -s/-x (shared/exclusive), -u (unlock early); exec 9>file; flock -n 9 for a whole script.',
    'mkdir and set -C are atomic portable locks but need a trap and stale checks (kill -0 PID).',
    'timeout N cmd → 124 on timeout; -k adds KILL; SECONDS for whole-script deadlines.',
    'Make steps idempotent: mkdir -p, ln -sfn, add-once, done-markers, > not >>.',
]

FAQ = [
    ('How do I prevent a cron job from running twice?', 'Wrap it with flock: flock -n /run/lock/job.lock /path/job.sh.'),
    ('What is flock in Linux?', 'A command (and system call) that takes an advisory lock on a file; the kernel releases it when the process exits.'),
    ('How do I make a script run only one instance?', 'At the top: exec 9>/run/lock/name.lock; flock -n 9 || exit 0.'),
    ('How do I stop a command after a time limit?', 'timeout 30 cmd; it exits 124 if the limit was reached; add -k to force KILL.'),
    ('Why is my lock file not removed after a crash?', 'File-existence locks are not released automatically; use flock, or check the owner PID and remove stale locks.'),
    ('What is a race condition?', 'A bug where the result depends on timing between processes, such as two copies updating the same file.'),
    ('What does idempotent mean in scripting?', 'Running the step again gives the same result, so reruns are safe.'),
]

PRACTICE_INTRO = 'Small lock, timeout and idempotence tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Timeout code', stmt='Show the exit code when timeout fires.', inp='nothing', code="timeout 0.2 sleep 1; echo $?\n", explain='124.'),
    dict(level='easy', title='mkdir lock', stmt='Take a mkdir lock twice; print busy the second time.', inp='nothing', code="mkdir L && echo ok; mkdir L 2>/dev/null || echo busy; rmdir L\n", explain='ok, busy.'),
    dict(level='easy', title='flock probe', stmt='Show a free lock with flock -n true.', inp='nothing', code="flock -n x.lock true && echo free\n", explain='free.'),
    dict(level='medium', title='Busy', stmt='Hold a lock on fd 9 and probe it.', inp='nothing', code="exec 9> h.lock; flock 9; flock -n h.lock true || echo busy\n", explain='busy.'),
    dict(level='medium', title='Add once', stmt='Run an add-once line three times; count lines.', inp='nothing', code="for i in 1 2 3; do grep -qx a f 2>/dev/null || echo a >> f; done; wc -l < f\n", explain='1.'),
    dict(level='medium', title='Alive?', stmt='Check whether PID 1 exists with kill -0.', inp='nothing', code="kill -0 1 2>/dev/null && echo alive || echo 'exists (no permission to signal)'\n", explain='Either answer means it exists; a missing PID gives “No such process”.'),
    dict(level='business', title='Deadline', stmt='Stop a loop after 1 second using SECONDS.', inp='nothing', code="SECONDS=0; n=0; until (( SECONDS >= 1 )); do ((++n)); sleep 0.25; done; echo stopped\n", explain='stopped.'),
    dict(level='business', title='Timeout to word', stmt='Map 124 to timed out.', inp='a code', code="rc=124; (( rc == 124 )) && echo 'timed out'\n", explain='timed out.'),
]

SCN_INTRO = 'Interview questions about concurrency and hangs in scripts.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you stop a cron job overlapping?”', 'Common.', 'command?',
        '''<ul>
          <li>flock -n /run/lock/job.lock job.sh</li>
          <li>Skips if the previous run is still going.</li>
          <li>Released automatically when it ends.</li>
        </ul>''', 'a touch/rm lock file.') +
    scn('Service company', 'Junior', 'Job stopped running after a crash', 'Lock file present.', 'why + fix?',
        '''<ol>
          <li>File-existence lock never released.</li>
          <li>Remove it after checking the owner is dead.</li>
          <li>Switch to flock.</li>
        </ol>''', 'deleting locks blindly every time.') +
    scn('Product company', 'Mid-level', 'Report totals sometimes wrong', 'Two writers.', 'diagnose?',
        '''<ul>
          <li>Race: overlapping read-modify-write.</li>
          <li>flock around the update, or one writer.</li>
          <li>Atomic replace with temp + mv.</li>
        </ul>''', 'adding sleep between steps.') +
    scn('Platform', 'Senior', 'Nightly job blocked for a week', 'Hung rsync + lock.', 'design?',
        '''<ul>
          <li>timeout -k on every network step.</li>
          <li>Alert on lock age / job duration.</li>
          <li>Idempotent, resumable steps.</li>
        </ul>''', 'rebooting the server.')
) + interview([
    ('Race condition?', 'Timing-dependent wrong result.'),
    ('flock -n vs -w?', 'Fail now vs wait with a limit.'),
    ('Why exec 9>?', 'Keep the lock for the whole script.'),
    ('mkdir as lock?', 'Atomic but needs clean-up.'),
    ('PID file problem?', 'PID reuse, stale files.'),
    ('timeout 124?', 'Limit reached.'),
    ('Idempotent?', 'Repeat-safe.'),
], [
    ('LFCS', 'Schedule and manage jobs safely.'),
    ('RHCSA', 'Schedule tasks; manage processes.'),
    ('CompTIA Linux+', 'Locks, signals, timeouts.'),
]) + distro('Tools per system.', [
    ('flock', 'util-linux', 'util-linux', 'util-linux', 'macOS: not built in'),
    ('timeout', 'coreutils', 'coreutils', 'coreutils', 'macOS: gtimeout (brew)'),
    ('/run/lock', 'yes', 'yes', 'yes', '-'),
    ('mkdir lock', 'everywhere', 'everywhere', 'everywhere', 'everywhere'),
    ('systemd', 'yes', 'yes', 'yes', 'launchd'),
]) + teaser('3.3', 'How do you know your error handling, retries and locks really work? Next: testing and debugging scripts with bash -x, PS4 and small automated tests.')

CHEATSHEET = cheatsheet('Locks and timeouts', [
    ('flock', [('flock -n f cmd', 'skip'), ('flock -w 60 f cmd', 'wait'), ('exec 9>f; flock -n 9', 'script'), ('-s / -x / -u', 'modes')]),
    ('Portable', [('mkdir d', 'atomic'), ('trap rm -rf d EXIT', 'release'), ('kill -0 PID', 'stale?'), ('set -C; > f', 'noclobber')]),
    ('timeout', [('timeout 30 cmd', 'limit'), ('124', 'timed out'), ('-k 5', 'then KILL'), ('SECONDS', 'deadline')]),
    ('Idempotent', [('mkdir -p', 'folders'), ('ln -sfn', 'links'), ('grep -q || >>', 'add once'), ('done markers', 'resume')]),
])

MINDMAP = mindmap('Run once, run safe', [
    ('Race', 'red', ['read-modify-write', 'lost update', 'check-then-create']),
    ('flock', 'blue', ['-n / -w', 'exec 9>', 'auto release']),
    ('Portable', 'amber', ['mkdir', 'noclobber', 'stale check']),
    ('timeout', 'green', ['124', '-k KILL', 'deadline']),
    ('Idempotent', 'violet', ['mkdir -p', 'add once', 'markers']),
    ('Cron', 'acc', ['flock + timeout', 'logs', 'alerts']),
])

LAB = lab('one copy, limited time', 'Build the lab (it creates <code>~/lab32</code> with a slow step), write <code>~/lab32/job.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab32; mkdir -p ~/lab32 && cd ~/lab32
cat > slow.sh <<'EOF'
#!/usr/bin/env bash
sleep "${SLOW:-0.5}"
n=$(cat counter 2>/dev/null || echo 0); echo $(( n + 1 )) > counter
EOF
chmod +x slow.sh''',
    tasks=['<code>job.sh</code> runs <code>./slow.sh</code> under an exclusive <b>flock</b> on <code>~/lab32/job.lock</code>; if another copy holds the lock it prints a line containing <code>busy</code> and exits <b>0</b> without running slow.sh.',
           'Started 4 times at once (with SLOW=0.5), exactly <b>one</b> copy may run: the counter goes up by exactly 1.',
           'slow.sh must be limited to <b>1 second</b> with timeout; when <code>SLOW=3</code> the job must exit <b>124</b> after about one second.',
           'Every run also makes sure <code>~/lab32/out</code> exists and contains exactly one line <code>ready</code>, however many times the job runs (idempotent).'],
    solution='''cat > job.sh <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
cd ~/lab32
exec 9> job.lock
flock -n 9 || { echo "job: busy, skipping"; exit 0; }
mkdir -p out
grep -qx ready out/state 2>/dev/null || echo ready >> out/state
timeout 1 ./slow.sh
EOF
chmod +x job.sh''',
    check='''cd ~/lab32; echo 0 > counter; rm -rf out
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 busy"      '( exec 8> job.lock; flock 8; out=$(./job.sh); r=$?; echo "$out" | grep -q busy && [ $r -eq 0 ] ) && [ "$(cat counter)" = 0 ]'
ok "2 one copy"  'echo 0 > counter; for i in 1 2 3 4; do SLOW=0.5 ./job.sh >/dev/null & done; wait; [ "$(cat counter)" = 1 ]'
ok "3 timeout"   'SECONDS=0; SLOW=3 ./job.sh >/dev/null 2>&1; r=$?; [ $r -eq 124 ] && (( SECONDS <= 2 ))'
ok "4 idempotent" 'for i in 1 2 3; do ./job.sh >/dev/null 2>&1; done; [ -d out ] && [ "$(grep -cx ready out/*)" = 1 ] && [ "$(cat out/* | wc -l)" = 1 ]' ''')
