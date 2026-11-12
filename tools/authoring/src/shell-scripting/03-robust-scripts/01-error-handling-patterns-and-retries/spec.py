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
    module='03-robust-scripts', lesson='01-error-handling-patterns-and-retries', n='3.1',
    module_label='Module 3 · Robust scripts',
    title='Error handling patterns: set -euo pipefail, ERR trap and retries',
    desc='Robust Bash error handling: where set -e does not stop (if, &&, ||, !, local x=$(…), functions in conditions), ERR traps with $LINENO and $BASH_COMMAND, set -E, || die, fallbacks and || true, and a retry function with exponential back-off that retries only temporary exit codes, with every run real.',
    og_desc='set -e pitfalls, ERR traps with line numbers, and a retry function with back-off for Bash scripts.',
    minutes=40, level='Intermediate → Advanced',
    lead='Stop loudly on permanent errors, retry temporary ones, and always know which line failed.',
    chips=['set -e holes tested', 'Retry with back-off animated', 'ERR trap stack trace', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """set -euo pipefail

retry() {   # retry MAX CMD...: waits 1, 2, 4 ... seconds (scaled down here)
  local max=$1 n=1; shift
  until "$@"; do
    (( n >= max )) && { echo "giving up after $n attempts" >&2; return 1; }
    echo "attempt $n failed, waiting $(( 2 ** (n - 1) ))s" >&2
    sleep 0.1; (( ++n ))
  done
}

calls=0
flaky() { (( ++calls )); (( calls >= 3 )); }   # fails twice, then works

retry 5 flaky && echo "succeeded after $calls calls"
"""

RUN = dict(
    heading='A retry loop in your browser',
    intro='<p>flaky fails twice, then succeeds; retry waits a little longer each time.</p>',
    code=MAIN,
    anno=[('until "$@"', 'Run the command until it succeeds.'), ('2 ** (n - 1)', '1, 2, 4… seconds.'), ('(( ++n ))', '++n, so the status is never 0 → false.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Change 3 to 9 in flaky: what happens?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> does set -e stop at local?',
             code="set -e\nf() { local x=$(false); echo \"still here, x=[$x]\"; }\nf\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> split local and the assignment so set -e sees the failure.',
             code="f() { local x; x=$(false) || { echo 'caught the failure'; return 1; }; }\nf || echo \"f returned $?\"\n"),
        dict(label='4 · Your turn', hint='Report the failing line with an ERR trap.',
             code="trap 'echo \"failed at line $LINENO\"' ERR\ntrue\nfalse\ntrap - ERR\n"),
        dict(label='5 · Challenge', hint='Classify exit codes into temporary or permanent.',
             code="for rc in 7 28 75 77 2; do case $rc in 6|7|28|75) echo \"$rc temporary\";; *) echo \"$rc permanent\";; esac; done\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Use retry with a real network command. Outputs are typical.</p>',
    items=[
        dict(title='1 · curl exit codes', cmd="curl -fsS http://127.0.0.1:9 -o /dev/null; echo $?\ncurl -fsS https://httpbin.org/status/503 -o /dev/null; echo $?", output='curl: (7) Failed to connect to 127.0.0.1 port 9\n7\ncurl: (22) The requested URL returned error: 503\n22', note='Typical: 7 = connection refused, 22 = HTTP error with -f.'),
        dict(title='2 · Retry a real URL', cmd="source retry.sh\nRETRY_ON='6 7 22 28' retry 4 curl -fsS https://httpbin.org/status/503 -o /dev/null", output='retry: attempt 1 failed (22), waiting 1s\nretry: attempt 2 failed (22), waiting 2s\nretry: attempt 3 failed (22), waiting 4s\nretry: giving up after 4 attempts', note='Typical.'),
        dict(title='3 · curl’s own retry', cmd="curl -fsS --retry 4 --retry-delay 1 https://example.com -o page.html", output='(downloads, retrying transient errors itself)', note='Many tools have built-in retries: use them.'),
        dict(title='4 · ERR trap in a cron mail', cmd="(cron runs sync.sh, MAILTO=riya)", output='Subject: Cron <riya@server> /home/riya/ops/bin/sync.sh\nsync: failed at line 12: cp data/orders.csv /mnt/share/', note='Typical.'),
    ],
)

TRACE = dict(
    heading='The ERR trap, line by line',
    intro='<p>See which line the trap reports.</p>',
    code='''report() { echo "ERR at line $1 (status $2)"; }
trap 'report $LINENO $?' ERR
echo "step 1"
ls /nonexistent 2>/dev/null
echo "step 3 still runs (no set -e here)"
trap - ERR
''',
    notes={2: 'Single quotes: $LINENO at run time.', 4: 'Fails: the trap reports line 4, status 2.'},
)

WORKED_INTRO = 'Three robust patterns.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Required files with clear errors',
         problem='<p>Check all required files, report every missing one, then fail once.</p>',
         inp='file names', approach=['Collect, then decide.'],
         code='''touch app.conf
missing=()
for f in app.conf secrets.env schema.sql; do [[ -r $f ]] || missing+=("$f"); done
if (( ${#missing[@]} )); then echo "missing: ${missing[*]}" >&2; echo "exit 1"; else echo "all present"; fi
''', notes={3: 'No early stop: the user sees all problems at once.'}, tryit='Exit 1 for real.'),
    dict(level='i', tag='Dev', title='A step-aware ERR trap',
         problem='<p>Name the failing step, not just the line.</p>',
         inp='nothing', approach=['A step variable + ERR trap.'],
         code='''( set -eE
  step=start
  trap 'echo "FAILED in step [$step] at line $LINENO" >&2' ERR
  step=download; true
  step=unpack;  false
  step=load;    echo never ) 2>&1; true
''', notes={3: 'The trap reads $step when it runs.'}, tryit='Add a timestamp.', expect='any'),
    dict(level='a', tag='SRE', title='Retry with jitter and a deadline',
         problem='<p>Retry up to a total time budget, adding random jitter.</p>',
         inp='a command', approach=['SECONDS + RANDOM.'],
         code='''tries=0
ok() { (( ++tries >= 3 )); }
deadline=$(( SECONDS + 5 ))
until ok; do
  (( SECONDS >= deadline )) && { echo "deadline reached"; break; }
  sleep "0.0$(( RANDOM % 9 + 1 ))"
done
echo "done after $tries tries"
''', notes={5: 'Total time limit, not just attempts.', 6: 'Small random pause.'}, tryit='Make ok never succeed.'),
]

QUIZ = mix([
    dict(q='Does set -e stop on local x=$(false)?', options=['yes', 'no: local’s status is 0', 'only in functions', 'with pipefail'], answer=1, why='Split it.'),
    dict(q='Inside if f; then, set -e in f is…', options=['active', 'ignored for f’s body', 'an error', 'doubled'], answer=1, why='Condition context.'),
    dict(q='The ERR trap fires inside functions only with…', options=['set -u', 'set -E', 'set -x', 'pipefail'], answer=1, why='errtrace.'),
    dict(q='Best trap quoting:', options=['trap "echo $LINENO" ERR', "trap 'echo $LINENO' ERR", 'either', 'neither'], answer=1, why='Expand at run time.'),
    dict(q='Retry which error?', options=['401 bad password', '503 service unavailable', 'file not found', 'syntax error'], answer=1, why='Temporary.'),
    dict(q='Back-off means…', options=['retry instantly', 'wait longer each time', 'stop', 'run backwards'], answer=1, why='1,2,4,8…'),
    dict(q='false && echo x under set -e…', options=['stops', 'continues', 'syntax error', 'retries'], answer=1, why='Not the last command.'),
    dict(q='Mark a failure as harmless:', options=['set +e', 'cmd || true', '2>/dev/null', 'exit 0'], answer=1, why='Explicit.'),
])

REVISION = [
    'set -e ignores failures in conditions (if/while tests, all but the last of &&/||, after !) and in functions called from them.',
    'local/export/declare x=$(cmd) hide cmd’s status: declare first, assign on the next statement.',
    "ERR trap: trap 'on_err $LINENO \"$BASH_COMMAND\" $?' ERR, single quotes; set -E for functions.",
    'Decide per step: || die (permanent), || fallback (optional), || true (harmless, commented).',
    'retry MAX cmd: limit, exponential back-off, jitter for fleets, only temporary codes (75, curl 6/7/28, 429/503).',
    'Only retry idempotent steps; add an overall deadline for polling.',
]

FAQ = [
    ('Why does set -e not exit my script?', 'The failure was in a condition (if, while, &&, ||, !), inside a function called from one, or hidden by local x=$(…).'),
    ('How do I print the line number where a Bash script failed?', "trap 'echo \"line $LINENO: $BASH_COMMAND\"' ERR, with set -E to include functions."),
    ('How do I retry a command in Bash?', 'A loop or function that runs it up to N times with growing sleeps, only for temporary exit codes.'),
    ('What is exponential back-off?', 'Waiting 1, 2, 4, 8… seconds between attempts so a struggling service gets time to recover.'),
    ('Should I use set -e?', 'Yes, as a safety net with -u and pipefail, plus explicit || die on important steps and an ERR trap.'),
    ('What does set -E do?', 'Makes ERR traps inherited by functions, command substitutions and subshells.'),
    ('How do I ignore one error under set -e?', 'cmd || true, with a comment explaining why.'),
]

PRACTICE_INTRO = 'Small error-handling tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Allowed failure', stmt='Run false under set -e without stopping.', inp='nothing', code="set -e; false || true; echo ok\n", explain='ok.'),
    dict(level='easy', title='Fallback', stmt='Use 0 when a file cannot be read.', inp='nothing', code="v=$(cat /nonexistent 2>/dev/null || echo 0); echo $v\n", explain='0.'),
    dict(level='easy', title='Doubling', stmt='Print the first 5 back-off waits.', inp='nothing', code="for n in 1 2 3 4 5; do echo -n \"$((2**(n-1))) \"; done; echo\n", explain='1 2 4 8 16.'),
    dict(level='medium', title='Split local', stmt='Catch a failing $( ) in a function.', inp='nothing', code="f(){ local x; x=$(false) || echo caught; }; f\n", explain='caught.'),
    dict(level='medium', title='ERR line', stmt='Report the line of a failing command.', inp='nothing', code="trap 'echo line $LINENO' ERR\nfalse\ntrap - ERR\n", explain='line 2.'),
    dict(level='medium', title='Classify', stmt='Say if 28 is temporary.', inp='a code', code="rc=28; case $rc in 6|7|28|75) echo temporary;; *) echo permanent;; esac\n", explain='temporary.'),
    dict(level='business', title='Retry count', stmt='Retry a command that succeeds on the 2nd call; print the calls.', inp='nothing', code="c=0; f(){ (( ++c >= 2 )); }; until f; do :; done; echo $c\n", explain='2.'),
    dict(level='business', title='Collect errors', stmt='Count missing files among /etc/hostname and /nope.', inp='paths', code="n=0; for f in /etc/hostname /nope; do [[ -e $f ]] || ((++n)); done; echo $n\n", explain='1.'),
]

SCN_INTRO = 'Interview questions about error handling in scripts.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What does set -e do?”', 'Common.', 'and its limits?',
        '''<ul>
          <li>Exit when a command fails.</li>
          <li>Not in if/while tests, && / || lists, after !.</li>
          <li>Add -u and -o pipefail.</li>
        </ul>''', 'saying it catches everything.') +
    scn('Service company', 'Junior', 'Nightly job fails 1 night in 10', 'API 503.', 'fix?',
        '''<ol>
          <li>Retry with back-off (3–5 attempts).</li>
          <li>Only for temporary codes.</li>
          <li>Alert only after the last attempt.</li>
        </ol>''', 'running it twice from cron.') +
    scn('Product company', 'Mid-level', 'Script continued with an empty value', 'local x=$(…).', 'why?',
        '''<ul>
          <li>local’s status masked the failure.</li>
          <li>Split declaration and assignment.</li>
          <li>ShellCheck SC2155 catches it.</li>
        </ul>''', 'adding sleep.') +
    scn('Platform', 'Senior', 'Retry storm after an outage', '500 servers.', 'what went wrong?',
        '''<ul>
          <li>Same fixed waits: all retried together.</li>
          <li>Exponential back-off + jitter + a cap.</li>
          <li>Circuit breaker / deadline.</li>
        </ul>''', 'more retries.')
) + interview([
    ('What is errexit?', 'set -e.'),
    ('What is the ERR trap?', 'Code run when a command fails.'),
    ('$BASH_COMMAND?', 'The command that was executing.'),
    ('set -E?', 'ERR trap in functions/subshells.'),
    ('Why idempotent steps?', 'Safe to retry or rerun.'),
    ('Jitter?', 'Random extra wait to spread retries.'),
    ('|| true?', 'Mark a failure as acceptable.'),
], [
    ('LFCS', 'Robust scripts and exit statuses.'),
    ('RHCSA', 'Scripts with conditionals and error checks.'),
    ('CompTIA Linux+', 'Error handling in scripts.'),
]) + distro('Bash features for error handling.', [
    ('set -E / ERR trap', 'bash', 'bash', 'bash', 'bash 3.2 ok'),
    ('inherit_errexit', 'bash 4.4+', 'bash 5', 'bash 5', 'macOS bash 3.2: no'),
    ('$BASH_COMMAND', 'yes', 'yes', 'yes', 'yes'),
    ('dash (sh)', 'no ERR trap', '-', '-', '-'),
    ('curl --retry', 'yes', 'yes', 'yes', 'yes'),
]) + teaser('3.2', 'A retry loop helps when a step fails; but what if it hangs forever, or two copies run at once? Next: locks, timeouts and running only once.')

CHEATSHEET = cheatsheet('Error handling', [
    ('Safety net', [('set -eEuo pipefail', 'top'), ("trap '…$LINENO…' ERR", 'where'), ('$BASH_COMMAND', 'what'), ('inherit_errexit', '$( )')]),
    ('Holes', [('if cmd', 'no stop'), ('a && b', 'only b'), ('local x=$(…)', 'hidden'), ('! cmd', 'no stop')]),
    ('Decide', [('|| die "…"', 'permanent'), ('|| fallback', 'optional'), ('|| true', 'harmless'), ('if ! cmd; then', 'block')]),
    ('Retry', [('retry 5 cmd', 'limit'), ('2**(n-1)', 'back-off'), ('RANDOM', 'jitter'), ('RETRY_ON', 'temporary only')]),
])

MINDMAP = mindmap('Error handling', [
    ('set -e', 'blue', ['-u', 'pipefail', 'holes']),
    ('Holes', 'red', ['if / &&', 'local $( )', '!']),
    ('ERR trap', 'green', ['$LINENO', '$BASH_COMMAND', 'set -E']),
    ('Decide', 'amber', ['|| die', '|| fallback', '|| true']),
    ('Retry', 'violet', ['limit', 'back-off', 'jitter']),
    ('Rules', 'acc', ['temporary only', 'idempotent', 'deadline']),
])

LAB = lab('a reliable sync step', 'Build the lab (it creates <code>~/lab31/flaky</code>, which fails its first N calls with exit 75), write <code>~/lab31/sync.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab31; mkdir -p ~/lab31/state && cd ~/lab31
cat > flaky <<'EOF'
#!/usr/bin/env bash
n=$(( $(cat ~/lab31/state/count 2>/dev/null || echo 0) + 1 )); echo "$n" > ~/lab31/state/count
(( n <= ${FAILS:-2} )) && { echo "unavailable ($n)" >&2; exit 75; }
[[ ${PERM:-} == 1 ]] && { echo "unauthorized" >&2; exit 77; }
echo "ok after $n calls"
EOF
chmod +x flaky''',
    tasks=['<code>sync.sh</code> calls <code>./flaky</code> with a retry: up to <b>4</b> attempts, retrying only exit code <b>75</b>, with growing waits (any growing waits are fine; keep them short, e.g. 0.1 s × 2^n).',
           'With the default FAILS=2 it must print <code>ok after 3 calls</code> and exit 0.',
           'With <code>FAILS=9</code> it must give up after exactly 4 calls and exit <b>75</b>.',
           'With <code>FAILS=0 PERM=1</code> (a permanent error) it must not retry: exactly 1 call, exit <b>77</b>.'],
    solution='''cat > sync.sh <<'EOF'
#!/usr/bin/env bash
set -uo pipefail
cd ~/lab31
retry() {
  local max=$1 n=1 rc; shift
  while true; do
    "$@" && return 0
    rc=$?
    (( rc == 75 )) || return "$rc"
    (( n >= max )) && return "$rc"
    sleep "$(awk -v n="$n" 'BEGIN{print 0.1 * 2^(n-1)}')"
    (( ++n ))
  done
}
retry 4 ./flaky
EOF
chmod +x sync.sh''',
    check='''cd ~/lab31
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
calls(){ cat state/count; }
ok "1 runs"      '[ -x sync.sh ] && grep -q flaky sync.sh'
ok "2 recovers"  'rm -f state/count; out=$(./sync.sh 2>/dev/null); r=$?; [ $r -eq 0 ] && [ "$out" = "ok after 3 calls" ]'
ok "3 gives up"  'rm -f state/count; FAILS=9 ./sync.sh >/dev/null 2>&1; r=$?; [ $r -eq 75 ] && [ "$(calls)" = 4 ]'
ok "4 permanent" 'rm -f state/count; FAILS=0 PERM=1 ./sync.sh >/dev/null 2>&1; r=$?; [ $r -eq 77 ] && [ "$(calls)" = 1 ]' ''')
