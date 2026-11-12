import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# A flaky "API" (fails the first N calls, counted in a file) and a sync job that must handle it
SS = r'''rm -rf ~/ops; mkdir -p ~/ops/bin ~/ops/data ~/ops/state; cd ~/ops
cat > bin/flaky <<'EOF'
#!/usr/bin/env bash
# flaky NAME FAILS: fails the first FAILS calls for NAME (exit 75 = try again later), then succeeds
n=$(( $(cat ~/ops/state/"$1" 2>/dev/null || echo 0) + 1 )); echo "$n" > ~/ops/state/"$1"
if (( n <= ${2:-2} )); then echo "flaky: $1 attempt $n: service unavailable" >&2; exit 75; fi
echo "flaky: $1 attempt $n: ok"
EOF
chmod +x bin/flaky
printf 'id,amount\n1,450\n2,800\n' > data/orders.csv'''

HOOK = hook('Riya’s nightly sync calls a partner API, copies files and loads a database. Some failures are permanent (a wrong password, a missing file) and the job should stop at once with a clear error. Others are temporary (the API answers “service unavailable”, the network blinks) and the right reaction is to wait and try again. In Lesson 1.1 she learned <code>set -euo pipefail</code>; this lesson shows where it silently does <i>not</i> stop a script, how an <b>ERR trap</b> reports exactly which line failed, and how a small <b>retry</b> function with back-off turns a flaky step into a reliable one.',
    ['know exactly when set -e stops a script and the cases where it does not (if, &&, ||, !, local x=$(…), subshells)',
     'report failures with an ERR trap: line number, command and exit code, with set -E for functions',
     'handle errors explicitly with || die, if ! cmd, and fallbacks with ||',
     'write a retry function with a limit and exponential back-off, retrying only temporary errors'])
ROAD = roadmap([
    ('story', 'The story', 3, 'stop or try again?'),
    ('decide', 'Which pattern?', 2, 'the quick chart'),
    ('definition', 'Error handling', 5, 'simple meaning + 4 depths'),
    ('types', 'Kinds of failure', 4, 'permanent vs temporary'),
    ('commands', 'Step by step', 15, 'set -e traps, ERR, retry'),
    ('animation', 'See it happen', 4, 'retry with back-off'),
    ('run', 'Run on your PC', 3, 'a real flaky URL'),
    ('lab', 'Practice lab', 8, 'a reliable sync step'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('When a step fails… → do', [
    ('it must never fail (config missing)', 'cmd || die "message"', 'stop, exit 1'),
    ('it may fail, there is a fallback', 'cmd || fallback', 'continue'),
    ('it may fail, it does not matter', 'cmd || true', 'documented'),
    ('it fails sometimes (network)', 'retry 5 cmd', 'back-off'),
    ('you want to know where it failed', "trap 'on_err $LINENO' ERR", 'line + command'),
    ('a whole block needs one check', 'if ! { a && b; }; then', 'group'),
])

cmap = concept_map(
    [('1.1', 'Safe mode', 'set -euo pipefail'), ('1.3', 'Exit codes', 'contract'), ('2.3', 'trap', 'EXIT, INT, TERM')],
    ['where set -e does not stop', 'local x=$(cmd) hides failures', 'ERR trap with $LINENO and $BASH_COMMAND', 'set -E (errtrace)', '|| die, || fallback, || true', 'retry with back-off and jitter', 'which errors to retry'],
    [('3.2', 'Locks and timeouts', 'stuck steps'), ('3.3', 'Testing scripts', 'prove the error paths'), ('4.1', 'Backup tool', 'retries'), ('4.2', 'Log monitor', 'alerts')],
    'Stop loudly on permanent errors, retry temporary ones, and always know which line failed.')

sc = (term(20, 14, 316, 156, ['$ ./sync.sh', ('flaky: api attempt 1: service unavailable', 'err'), ('retry: attempt 1 failed (75), waiting 1s', 'out'), ('flaky: api attempt 2: service unavailable', 'err'), ('retry: attempt 2 failed (75), waiting 2s', 'out'), ('flaky: api attempt 3: ok', 'acc')], title='riya@server: ~/ops', prompt='$', size=6.4, step=18)
      + t(352, 36, 'Two kinds of failure:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['permanent → stop', '  || die', 'temporary → retry', '  with back-off', 'always: which line?'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Stop, or try again?</h2>
  <div class="story">
''' + puzzle('Riya’s script has <code>set -euo pipefail</code> at the top. Yet <code>local total=$(compute_total)</code> fails and the script happily continues with an empty total. A failing <code>grep</code> inside <code>if grep … ; then</code> does not stop it either (that one is fine). And the nightly API call fails roughly one night in ten with “503 service unavailable”, waking her up for nothing because it would have worked a minute later. How can a script stop on real errors, keep going on harmless ones, and retry the flaky ones?') + '''
    <p class="narration">In <code>~/ops</code> (every run in this lesson is real). <code>bin/flaky NAME N</code> is a stand-in for a flaky API: it fails the first N calls with exit 75 (“try again later”), then succeeds.</p>
''' + scene('A terminal: sync.sh calls a flaky API; the first two attempts fail with 75 and the retry function waits 1 s then 2 s; the third attempt succeeds.', sc,
            'Retry the <tspan font-weight="700" class="s-acc">temporary</tspan>, stop on the permanent.') + '''
K> Isn’t set -e enough?
A> It is a safety net with holes. Bash deliberately ignores failures in places where a failure is part of the logic: the test of an <code>if</code> or <code>while</code>, the left side of <code>&amp;&amp;</code>/<code>||</code>, after <code>!</code>. And <code>local x=$(cmd)</code> reports the status of <code>local</code>, which is always 0. Knowing the holes is half of robust scripting.
R> And retries?
A> A retry loop with a limit and growing pauses (1 s, 2 s, 4 s…). It must only retry errors that can go away; retrying a wrong password five times just locks the account.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A failing command goes one of three ways: a permanent error stops the script with a message; a temporary error goes into a retry loop with growing waits; an expected failure continues with a fallback.">'
       + label_box(250, 14, 140, 40, ['a command fails'], 'red', 9)
       + ''.join(arrow(320, 56, x + 70, 98) + label_box(x, 100, 140, 56, [a, b], c, 8.4) for x, a, b, c in [(14, 'permanent', '|| die → exit 1', 'red'), (250, 'temporary', 'retry 1s,2s,4s…', 'amber'), (486, 'expected', '|| fallback', 'green')])
       + t(320, 190, 'ERR trap: report the line and command in every case', 9, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Error handling at four depths', [
    ('v', 'No jargon: a delivery driver', '      <p>Wrong address: stop and report. Customer not home: come back later, a few times. Doorbell broken: knock instead. Three different reactions to “it did not work”.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>cp config.yml /etc/app/ || die "cannot install config"</code></li>
        <li><code>curl -fsS "$url" -o out.json || retry 5 curl -fsS "$url" -o out.json</code></li>
        <li><code>trap 'echo "line $LINENO: $BASH_COMMAND failed" &gt;&amp;2' ERR</code></li>
        <li><code>local x; x=$(cmd)</code> (two lines, never <code>local x=$(cmd)</code>)</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li>set -e ignores failures in <code>if</code>/<code>while</code>/<code>until</code> tests, in <code>a &amp;&amp; b</code> except the last command, after <code>!</code>, and inside functions called from those places.</li>
        <li>The ERR trap fires on the same failures set -e would act on; <code>set -E</code> makes it work inside functions and subshells too.</li>
        <li>Retry with a <b>limit</b>, <b>growing waits</b> (exponential back-off) and a little <b>jitter</b> so 100 servers do not retry at the same second.</li>
        <li>Decide by exit code what is temporary: curl 6/7/28 (DNS, connect, timeout), HTTP 429/503, sysexits 75 (EX_TEMPFAIL).</li>
      </ul>'''),
    ('a', 'Behind the screen: errexit’s rules', '''      <ul>
        <li>POSIX defines errexit as “exit if a simple command fails, unless it is part of a condition”; the condition context is <i>inherited</i> by everything called from it, so <code>if myfunc; then</code> disables set -e for the whole body of myfunc.</li>
        <li><code>local</code>, <code>export</code>, <code>declare</code> and <code>readonly</code> are commands with their own status (0 when the assignment works): the <code>$( )</code> status is lost. ShellCheck flags it as SC2155.</li>
        <li>Command substitution runs in a subshell that inherits set -e only with <code>shopt -s inherit_errexit</code> (Bash 4.4+).</li>
        <li><code>$LINENO</code> in an ERR trap is the line of the failing command; <code>${BASH_SOURCE[1]}</code>, <code>${FUNCNAME[1]}</code> and <code>caller</code> give a small stack trace.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Error handling in Bash</h2>
''' + def_block(
    '<b>Error handling</b> is deciding, for every command that can fail, what the script does next: stop with a message, use a fallback, ignore it on purpose, or try again. Bash offers <b>set -e</b> (exit on unhandled failures), explicit checks (<code>if</code>, <code>||</code>), the <b>ERR trap</b> (run code whenever a command fails) and loops for <b>retries</b>.',
    'Every failure gets a decision: stop, fall back, ignore on purpose, or retry.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('errexit', 'set -e.'),
    ('ERR trap', 'Runs on a failing command.'),
    ('errtrace', 'set -E: ERR inside functions.'),
    ('$LINENO', 'Current line number.'),
    ('$BASH_COMMAND', 'The command that was running.'),
    ('Retry', 'Try again after a failure.'),
    ('Back-off', 'Wait longer each time.'),
    ('Jitter', 'A little random extra wait.'),
]) + '\n' + names('Where the names come from.', [
    ('errexit', 'error → exit', 'set -o errexit = set -e.'),
    ('errtrace', 'trace errors into functions', 'set -E.'),
    ('pipefail', 'pipeline fails', 'Bash 3.'),
    ('die', 'stop with a message', 'From Perl.'),
    ('back-off', 'step back', 'Ethernet, 1970s.'),
    ('jitter', 'small random shake', 'Networking.'),
    ('EX_TEMPFAIL', 'temporary failure (75)', 'sysexits.h.'),
    ('idempotent', 'same result if repeated', 'Maths.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Stop with message', '<code>cmd || die "…"</code>'),
    ('Allowed failure', '<code>cmd || true</code>'),
    ('Where did it fail', "<code>trap '…$LINENO…' ERR</code>"),
    ('In functions too', '<code>set -E</code>'),
    ('Keep $( ) status', '<code>local x; x=$(…)</code>'),
    ('Retry', '<code>retry 5 cmd args</code>'),
]) + '\n' + lv + didyou('The Bash manual itself warns that set -e’s rules are complicated, and many experienced scripters use it only together with explicit checks. The pattern in this lesson (set -euo pipefail + ERR trap + explicit <code>|| die</code> on important steps) gives you both: a safety net and clear intent.') + '''
EXAM> “Why didn’t set -e stop my script when local x=$(false) failed?” → local is a separate command whose own status (0) replaces the substitution’s status; declare first, then assign: local x; x=$(cmd).
''' + qc('Inside if myfunc; then …, does set -e work in myfunc?', 'No: the condition context is inherited by the whole function body.') + mistake('local result=$(compute)',
    'local result; result=$(compute)',
    'The failure of compute is hidden by local’s own exit status 0.') + mistake('for i in 1 2 3 4 5; do curl … && break; done   (retry with no pause)',
    'retry 5 curl …   (limit, back-off, only for temporary errors)',
    'Five instant retries hit an overloaded server five times in a second and still fail.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Kinds of failure, and where set -e stops</h2>
''' + table(['Failure', 'Examples', 'Reaction'], [
    ['Permanent', 'missing file, wrong password, bad argument, disk full', 'stop: <code>|| die</code>, exit non-zero'],
    ['Temporary', 'timeout, 503, 429 rate limit, DNS blip, lock busy', 'retry with back-off'],
    ['Expected', 'grep finds nothing, optional file absent', 'handle: <code>if</code>, <code>|| fallback</code>'],
    ['Harmless', 'cleanup of a file that may not exist', '<code>|| true</code> (or <code>rm -f</code>)'],
], minw=520) + table(['Situation', 'set -e stops?'], [
    ['<code>false</code> on its own line', 'yes'],
    ['<code>if false; then</code> / <code>while false</code>', 'no (condition)'],
    ['<code>false &amp;&amp; echo x</code>', 'no (not the last in the list)'],
    ['<code>echo x &amp;&amp; false</code>', 'yes (last command)'],
    ['<code>false || true</code>', 'no'],
    ['<code>! false</code>', 'no'],
    ['<code>x=$(false)</code>', 'yes'],
    ['<code>local x=$(false)</code>', '<b>no</b> (local’s status)'],
    ['<code>false | true</code> without pipefail', 'no'],
    ['a function called from <code>if f; then</code>', 'no, for its whole body'],
], minw=420) + qc('Which line stops a set -e script: false && echo hi, or echo hi && false?', 'echo hi && false (false is the last command of the list).') + '''
</section>
'''

RET = r'''retry() {   # retry MAX CMD ARGS...  (exponential back-off; retries only exit codes listed in RETRY_ON)
  local max=$1 n=1 rc wait; shift
  while true; do
    "$@" && return 0
    rc=$?
    if [[ " ${RETRY_ON:-75 6 7 28} " != *" $rc "* ]]; then echo "retry: permanent error ($rc), not retrying" >&2; return "$rc"; fi
    (( n >= max )) && { echo "retry: giving up after $n attempts" >&2; return "$rc"; }
    wait=$(( 2 ** (n - 1) ))
    echo "retry: attempt $n failed ($rc), waiting ${wait}s" >&2
    sleep "${RETRY_SLEEP_SCALE:-1}e0" 2>/dev/null || true
    sleep "$(awk -v w="$wait" -v s="${RETRY_SLEEP_SCALE:-1}" 'BEGIN{print w*s}')"
    (( n++ ))
  done
}'''
RET = RET.replace('    sleep "${RETRY_SLEEP_SCALE:-1}e0" 2>/dev/null || true\n', '')
SSR = SS + "\ncat > bin/retry.sh <<'EOF'\n" + RET + "\nEOF\nexport RETRY_SLEEP_SCALE=0.1"

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>set -e’s holes, ERR traps, explicit checks and retries</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops</code>. <code>bin/flaky NAME N</code> fails its first N calls with exit 75 and then succeeds (its counter lives in <code>state/</code>). In the retry cards <code>RETRY_SLEEP_SCALE=0.1</code> shortens the waits ten times so the page builds fast; the messages still show the real schedule.</p>
''' + cmdcard_u(['every script with set -e'], ['trusting set -e blindly'])(
    'holes', 'set -e: where it does not stop', 'the holes in set -e',
    'set -e ignores a failure when it is part of a condition (if, while, &amp;&amp;, ||, !) and when <code>local</code>/<code>export</code>/<code>declare</code> wraps a <code>$( )</code>. These are the places to check explicitly.',
    'local x; x=$(cmd)   ·   cmd || die "…"', 'safe',
    [('local x=$(cmd)', 'status lost', 'split it'),
     ('if cmd; then', 'no stop', 'by design'),
     ('a && b', 'only b stops', 'lists'),
     ('f called in if', 'no stop inside f', 'inherited'),
     ('inherit_errexit', 'set -e in $( )', 'Bash 4.4+'),
     ('cmd || true', 'deliberate', 'document it')],
    dict(cmd="compute() { echo 'computing'; false; }\nbash -c 'set -e; f(){ local t=$(false); echo \"after local: continued, t=[$t]\"; }; f'\nbash -c 'set -e; f(){ local t; t=$(false); echo \"never printed\"; }; f'; echo \"split version stopped: exit $?\"\nbash -c 'set -e; g(){ false; echo \"inside g: still running\"; }; if g; then echo \"g returned success\"; fi'", note='The first form continues with an empty value; splitting it stops at once. The third shows the if-context: false inside g is ignored.', expect='any'),
    [('dev', [
        dict(situation='&& lists.', cmd="bash -c 'set -e; false && echo x; echo \"after false && …: still running\"; echo y && false; echo never'; echo \"exit $?\"", why='Only the last command of a list counts.', expect='any')]),
    ],
    anat=anatomy([('local t;', 'cmd', 'declare'), ('t=$(cmd)', 'arg', 'assign: status kept')], 'Two statements, so set -e sees the failure.')
) + cmdcard_u(['any non-trivial script'], ['silent deaths in cron'])(
    'errtrap', "trap 'on_err $LINENO' ERR · set -E · $BASH_COMMAND", 'report where it failed',
    'An ERR trap runs whenever a command fails (where set -e would act). Print the line (<code>$LINENO</code> passed in), the command (<code>$BASH_COMMAND</code>) and the status. <code>set -E</code> makes the trap work inside functions and subshells.',
    "on_err(){ echo \"ERROR line $1: '$2' exited $3\" >&2; }; trap 'on_err $LINENO \"$BASH_COMMAND\" $?' ERR", 'safe',
    [('$LINENO', 'line number', 'pass at trap time'),
     ('$BASH_COMMAND', 'failing command', 'text'),
     ('$?', 'its status', 'first thing'),
     ('set -E', 'errtrace', 'functions'),
     ('${FUNCNAME[1]}', 'which function', 'stack'),
     ('caller', 'line + file', 'stack')],
    dict(setup=SS, cmd="cd ~/ops\ncat > bin/load.sh <<'EOF'\n#!/usr/bin/env bash\nset -eEuo pipefail\non_err() { echo \"ERROR in ${3:-main} line $1: '$2' exited $4\" >&2; }\ntrap 'on_err $LINENO \"$BASH_COMMAND\" \"${FUNCNAME[0]:-}\" $?' ERR\ncheck() { grep -q ',' \"$1\"; }\nload() { check data/orders.csv; cp data/orders.csv /nonexistent/dir/ 2>/dev/null; }\nload\necho 'never reached'\nEOF\nchmod +x bin/load.sh; bin/load.sh; echo \"exit $?\"", note='The trap names the function, the line and the exact command, which is gold in a 2 a.m. cron mail.', expect='any'),
    [('sys', [
        dict(situation='Without set -E the trap is silent inside functions.', cmd="bash -c 'set -e; trap \"echo ERR trap: line \\$LINENO\" ERR; f(){ false; }; f'; echo \"exit $?\"\nbash -c 'set -eE; trap \"echo ERR trap: line \\$LINENO\" ERR; f(){ false; }; f'; echo \"exit $?\"", why='Only the -E version reports.', expect='any')]),
    ]
) + cmdcard_u(['important steps', 'clear messages'], ['relying on set -e for messages'])(
    'explicit', '|| die · if ! cmd · || fallback · || true', 'explicit checks',
    'For steps that matter, say what should happen: <code>|| die "message"</code> stops with a reason, <code>if ! cmd; then</code> handles the failure in a block, <code>|| fallback</code> continues another way, <code>|| true</code> marks a failure as harmless (with a comment).',
    'cp "$cfg" /etc/app/ || die "cannot install $cfg"', 'safe',
    [('|| die "…"', 'stop + reason', 'must work'),
     ('if ! cmd; then', 'handle block', 'several steps'),
     ('|| fallback', 'another way', 'optional source'),
     ('|| true', 'harmless', 'comment why'),
     ('${PIPESTATUS[@]}', 'pipe statuses', 'details'),
     ('rc=$?', 'save first', 'branches')],
    dict(setup=SS, cmd="cd ~/ops\ndie() { echo \"sync: error: $*\" >&2; exit 1; }\nprimary=data/orders-today.csv; backup=data/orders.csv\nsrc=$primary; [[ -r $src ]] || { echo \"sync: $primary missing, using $backup\"; src=$backup; }\nlines=$(wc -l < \"$src\") || die \"cannot count $src\"\necho \"loading $((lines - 1)) orders from $src\"\nrm -f state/old.lock || true   # may not exist: harmless\n( [[ -r data/password.txt ]] || die 'data/password.txt missing: refusing to continue' ); echo \"exit $?\"", note='Fallback, a checked step, a harmless failure, and a permanent error that stops with a clear reason.', expect='any'),
    [('devops', [
        dict(situation='if ! with a cleanup branch.', setup=SS, cmd="cd ~/ops; if ! tar -czf /nonexistent/backup.tgz data 2>/dev/null; then echo 'backup failed: removing partial file, alerting'; rm -f /nonexistent/backup.tgz; fi", why='Several reactions in one place.')]),
    ]
) + cmdcard_u(['network calls', 'APIs', 'locks'], ['permanent errors', 'non-idempotent steps'])(
    'retry', 'retry MAX cmd args · back-off · RETRY_ON', 'retry with back-off',
    'The <code>retry</code> function runs the command; on success it returns 0. On a <b>temporary</b> exit code (listed in <code>RETRY_ON</code>, default 75, 6, 7, 28) it waits 1 s, 2 s, 4 s… and tries again, up to MAX attempts. Any other code is permanent: it gives up at once and passes the code on.',
    'retry 5 curl -fsS "$url" -o data.json', 'safe',
    [('MAX', 'attempt limit', 'always'),
     ('2 ** (n-1)', '1,2,4,8 s', 'back-off'),
     ('RETRY_ON', 'temporary codes', 'only these'),
     ('+ jitter', '$((RANDOM % 1000)) ms', 'many clients'),
     ('return rc', 'last status', 'caller decides'),
     ('idempotent', 'safe to repeat', 'required')],
    dict(setup=SSR, cmd="cd ~/ops; source bin/retry.sh\nretry 5 bin/flaky api 2; echo \"exit $?\"\necho '--- a service that never recovers:'\nretry 3 bin/flaky down 99; echo \"exit $?\"", note='Two failures, waits of 1 s and 2 s (scaled), then success. The second gives up after 3 attempts with the last code.', expect='any'),
    [('sec', [
        dict(situation='Permanent errors are not retried.', setup=SSR, cmd="cd ~/ops; source bin/retry.sh; retry 5 bash -c 'echo \"auth: invalid password\" >&2; exit 77'; echo \"exit $?\"", why='Retrying a wrong password would only lock the account.', expect='any'),
        dict(situation='Read the function.', setup=SSR, cmd="cd ~/ops; cat bin/retry.sh", why='15 lines you can paste into the template.')]),
    ]
) + undo('Error handling is about recovery; plan the undo for each step:', [
    ('Half-done job:', 'make steps idempotent (safe to run again) and write results atomically (Lesson 2.3).'),
    ('Retried a step that should not repeat (a payment, an email):', 'only retry idempotent steps, or check “already done?” first.'),
    ('Script stopped too early (|| true missing):', 'decide per step; never sprinkle set +e.'),
    ('Silent failure found later:', 'add the ERR trap and the split <code>local x; x=$(…)</code>, then rerun.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(cmd="bash -c 'set -e; f(){ local x=$(false); echo \"got [$x], status hidden\"; }; f'", meaning='local hid the failure of the substitution.', fix='local x; x=$(false)'),
    dict(cmd="bash -c 'set -e; trap \"echo line $LINENO\" ERR; false'", meaning='Double quotes expanded $LINENO when the trap was set (line 1), not when it ran.', fix="Single quotes: trap 'echo line $LINENO' ERR"),
    dict(cmd="for i in 1 2 3; do curl -fsS http://127.0.0.1:9 -o /dev/null 2>/dev/null && break; echo \"try $i failed\"; done", meaning='Retries with no pause and no limit check: all three fail within milliseconds.', fix='retry with back-off; check the final status.'),
]) + qc('Which exit codes should a retry function retry?', 'Only temporary ones (timeouts, connection refused, 429/503, EX_TEMPFAIL 75), never permanent ones such as bad credentials or missing files.') + '''
'''
cards = cards + '</section>\n'

def rt(k):
    o = t(180, 18, 'retry 5 call_api', 9.6, 'ink2', bold=True)
    rows = [('attempt 1', 'exit 75 → wait 1 s', 'amber'), ('attempt 2', 'exit 75 → wait 2 s', 'amber'), ('attempt 3', 'exit 0 → return 0', 'green'), ('total', '3 calls, 3 s waited, job continues', 'blue')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
see_cmds = [['call_api', ('503 service unavailable', 'err')], ['sleep 1; call_api', ('503 service unavailable', 'err')], ['sleep 2; call_api', ('ok', 'out')], ['$ echo $?', ('0', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@server: ~/ops', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Try 1.', 'Try 2.', 'Try 3.', 'Done.'])]
two = anim_two('Retry with back-off', 'Behind the screen: waits double',
               'A terminal: two 503 answers, waits of 1 and 2 seconds, then success.', 'Rows show each attempt and the next wait.', see, [rt(k) for k in range(4)],
               ['try 1.', 'try 2.', 'try 3.', 'done.'], ['1', '2', '3', 'ok'])

def ho(k):
    o = t(180, 18, 'set -e and local x=$(false)', 9.4, 'ink2', bold=True)
    o += label_box(14, 36, 160, 50, ['$(false)', 'status 1'], 'red', 8.4) + label_box(186, 36, 160, 50, ['local x=…', ['?', 'status 0', 'status 0', 'status 0'][k]], ['card', 'green', 'green', 'green'][k], 8.4)
    o += t(180, 112, ['two commands on one line', 'local succeeds: assignment worked', '$? = 0: set -e sees nothing', 'fix: local x; x=$(false)'][k], 9.2, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Why local hides failures',
              'Two commands, one status.', 'local + $( )', 'Two boxes: the substitution fails, local succeeds.', [ho(k) for k in range(4)],
              ['line.', 'local.', 'status.', 'fix.'], hid='scenario-local')

dx = dissect('Layer by layer: from failure to decision',
    'Each layer has a real command from our build machine.', [
    dict(key='status', name='Exit status', sub='0 or not', why='The signal.', how='$?.', impl='wait().', used='Everything.',
         setup=SS, cmd="cd ~/ops; bin/flaky x 1; echo \"status $?\"; bin/flaky x 1; echo \"status $?\"", expect='any'),
    dict(key='classify', name='Classify', sub='temporary?', why='Retry or stop.', how='case on code.', impl='RETRY_ON.', used='retry().',
         cmd="for rc in 0 2 7 28 75 77; do case $rc in 0) k=ok;; 6|7|28|75) k=temporary;; *) k=permanent;; esac; echo \"$rc -> $k\"; done"),
    dict(key='report', name='Report', sub='ERR trap', why='Find it fast.', how='$LINENO, $BASH_COMMAND.', impl='trap.', used='cron mail.',
         cmd="bash -c 'set -eE; trap '\"'\"'echo \"failed at line $LINENO: $BASH_COMMAND\" >&2'\"'\"' ERR\necho step1\nls /nonexistent-dir\necho never' 2>&1 | sed 's/^ls: .*/(ls error message)/'", expect='any'),
], hint='Status → class → report. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Retry with back-off, and the local trap</h2>
''' + two + s1 + dx + qc('With waits 1, 2, 4, 8 s, how long do 5 failed attempts take?', '15 s of waiting (1+2+4+8) before the 5th attempt fails and retry gives up.') + '''
</section>
'''

VAR = variations('Sixteen more error-handling patterns. All were really run on our build machine.', [
    ('set -e cases', [
        dict(title='Pipeline without pipefail', cmd="bash -c 'set -e; false | true; echo \"continued: pipefail missing\"'", why='Add -o pipefail.'),
        dict(title='inherit_errexit', cmd="bash -c 'set -e; shopt -s inherit_errexit; x=$(false; echo after); echo \"x=[$x]\"'; echo \"exit $?\"", why='set -e inside $( ) too.', expect='any'),
        dict(title='! does not stop', cmd="bash -c 'set -e; ! true; echo \"after ! true: still running\"'", why='Negation counts as a condition.'),
        dict(title='Arithmetic zero is a failure', cmd="bash -c 'set -e; n=0; ((n++)); echo never'; echo \"exit $?: ((n++)) returned 1 because the old value was 0\"", why='Use ((++n)) or n=$((n+1)).', expect='any'),
    ]),
    ('Reporting', [
        dict(title='A tiny stack trace', cmd="bash -c 'set -eE; trace(){ local i; for ((i=1;i<${#FUNCNAME[@]};i++)); do echo \"  at ${FUNCNAME[i]} (line ${BASH_LINENO[i-1]})\" >&2; done; }; trap \"echo ERROR: \\$BASH_COMMAND >&2; trace\" ERR; a(){ b; }; b(){ false; }; a' 2>&1", why='FUNCNAME and BASH_LINENO.', expect='any'),
        dict(title='Exit code in the message', cmd="bash -c 'trap \"rc=\\$?; echo \\\"failed with \\$rc\\\" >&2\" ERR; set -e; ls /nonexistent 2>/dev/null' 2>&1; true", why='Save $? first in the trap.', expect='any'),
        dict(title='Different message per step', cmd="step='download'; bash -c \"set -e; trap 'echo \\\"step [$step] failed\\\" >&2' ERR; false\" 2>&1; true", why='Track the current step in a variable.', expect='any'),
    ]),
    ('Explicit handling', [
        dict(title='Default when a command fails', cmd="ver=$(cat /nonexistent/VERSION 2>/dev/null || echo 0.0.0); echo \"version $ver\"", why='|| inside $( ).'),
        dict(title='Try several sources', cmd="for src in /nonexistent/a.conf /etc/hostname; do [[ -r $src ]] && { echo \"using $src\"; break; }; done", why='First that works.'),
        dict(title='Check every pipe stage', cmd="printf 'a\\n' | grep -q zzz | cat; s=(\"${PIPESTATUS[@]}\"); echo \"stages: ${s[*]}\"; (( s[1] == 1 )) && echo 'grep found nothing (expected)'", why='Decide per stage.'),
        dict(title='Collect errors, fail at the end', cmd="errs=0; for f in /etc/hostname /nonexistent /etc/passwd; do [[ -r $f ]] || { echo \"missing $f\"; ((++errs)); }; done; echo \"$errs problem(s)\"; (( errs == 0 ))", why='Report all problems, not just the first.', expect='any'),
    ]),
    ('Retries', [
        dict(title='Succeeds first time: no waiting', setup=SSR, cmd="cd ~/ops; source bin/retry.sh; retry 5 bin/flaky fast 0", why='Zero overhead on success.'),
        dict(title='Custom temporary codes', setup=SSR, cmd="cd ~/ops; source bin/retry.sh; RETRY_ON='75 3' retry 3 bash -c 'exit 3'; echo \"exit $?\"", why='Choose per command.', expect='any'),
        dict(title='Jitter', cmd="for i in 1 2 3; do echo \"wait $(( 2 ** i ))s + $(( RANDOM % 1000 ))ms\"; done | sed -E 's/[0-9]+ms/NNNms/'", why='Random part avoids thundering herds.'),
        dict(title='Retry until a file appears', cmd="( sleep 0.3; touch ready.flag ) & n=0; until [[ -e ready.flag ]]; do ((++n)); sleep 0.1; done; echo \"ready after $n checks\" | sed -E 's/[0-9]+ checks/N checks/'", why='Polling with a pause.'),
        dict(title='Overall deadline', cmd="deadline=$(( SECONDS + 1 )); n=0; until (( SECONDS >= deadline )); do ((++n)); sleep 0.2; done; echo \"gave up at the deadline after some tries\"", why='Limit total time, not just attempts.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Error handling at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['APIs', 'retries'], 'blue', 8.6), '1. Partner APIs',
              'Nightly jobs retry 503/429 with back-off before paging anyone; most “incidents” disappear.', ['503', '*retry', 'success']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['CI', 'deploy'], 'green', 8.6), '2. Deploy pipelines',
    'set -euo pipefail plus an ERR trap that prints the step and line makes failed deploys readable in CI logs.', ['step fails', '*ERR trap', 'clear log']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cloud', 'eventual'], 'amber', 8.6), '3. Cloud provisioning',
    'A new VM or DNS record is not ready instantly; scripts poll with a deadline instead of failing at once.', ['create', '*poll', 'ready']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['data', 'ETL'], 'violet', 8.6), '4. Data loads',
    'Missing source files are permanent errors (stop, alert); a busy database lock is temporary (retry).', ['classify', '*stop / retry', 'load']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['K8s', 'jobs'], 'red', 8.6), '5. Containers and jobs',
    'Kubernetes restarts failed pods with back-off too; exit codes decide whether a Job is retried.', ['exit code', '*backoffLimit', 'retry']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful patterns. All really run on our build machine.', [
    dict(level='b', title='Stop with a reason', scenario='Config missing.', cmd="( [[ -r /nonexistent/app.conf ]] || { echo 'error: app.conf missing' >&2; exit 1; } ); echo \"exit $?\"", explain='|| { …; exit 1; }', expect='any'),
    dict(level='b', title='Harmless failure', scenario='Cleanup.', cmd="rm /nonexistent/old.tmp 2>/dev/null || true; echo 'continued'", explain='|| true.'),
    dict(level='i', title='Keep a $( ) failure visible', scenario='Functions.', cmd="f(){ local v; v=$(false) || { echo \"caught: $?\"; return 1; }; }; f; echo \"f returned $?\"", explain='Split local.', expect='any'),
    dict(level='i', title='Line of the failure', scenario='Debug.', cmd="bash -c 'set -eE; trap '\"'\"'echo \"line $LINENO\" >&2'\"'\"' ERR\ntrue\nfalse' 2>&1; true", explain='ERR + $LINENO.', expect='any'),
    dict(level='a', title='Retry a flaky call', scenario='Night job.', setup=SSR, cmd="cd ~/ops; source bin/retry.sh; retry 4 bin/flaky night 1 2>&1", explain='One failure, one wait, success.'),
], extra=build_up('a reliable sync step', 'Riya hardens the API step of her nightly job.', SSR, [
    ("cd ~/ops; bin/flaky api1 2; echo \"plain call: exit $?\"", '1. Plain call: fails tonight.'),
    ("cd ~/ops; source bin/retry.sh; retry 5 bin/flaky api2 2 2>&1 | sed 's/^/  /'", '2. With retry: succeeds after two waits.'),
    ("cd ~/ops; source bin/retry.sh; retry 5 bash -c 'echo \"401 unauthorized\" >&2; exit 77' 2>&1; echo \"exit $?: no retry for a permanent error\"", '3. Permanent errors stop at once.'),
    ("cd ~/ops; bash -c 'set -eE; trap '\"'\"'echo \"sync failed at line $LINENO: $BASH_COMMAND\" >&2'\"'\"' ERR; source bin/retry.sh; retry 2 bin/flaky api3 9 || { echo \"sync: error: partner API still down after retries\" >&2; exit 1; }' 2>&1 | tail -2; echo \"exit ${PIPESTATUS[0]}\"", '4. Still down: give up with a clear message and exit 1.'),
], cumulative=False, expect='any')) + VAR + which('Choosing the right reaction.', [
    ('Must work', '|| die "reason"', 'Stops, explains.', 'Hoping set -e catches it.'),
    ('Optional step', '|| fallback', 'Continues.', 'Ignoring silently.'),
    ('Harmless', '|| true (+ comment)', 'Explicit.', 'set +e.'),
    ('Flaky', 'retry with back-off', 'Recovers.', 'Instant loops.'),
    ('Where?', 'ERR trap + set -E', 'Line, command.', 'echo after each line.'),
    ('$( ) in a function', 'local x; x=$(…)', 'Status kept.', 'local x=$(…).'),
]) + keys('Handy forms.', [
    ('set -eEuo pipefail', 'safe mode + errtrace', 'top'),
    ("trap 'on_err $LINENO \"$BASH_COMMAND\" $?' ERR", 'report', 'top'),
    ('cmd || die "…"', 'must work', 'steps'),
    ('local x; x=$(cmd)', 'keep status', 'functions'),
    ('retry 5 cmd args', 'temporary errors', 'network'),
    ('RETRY_ON="75 6 7 28"', 'which codes', 'per call'),
]) + scriptit('sync.sh', 'A nightly sync step with every pattern: safe mode with errtrace, an ERR trap that names the line, a fallback, a harmless step, a permanent check and a retried flaky call.',
'''#!/usr/bin/env bash
set -eEuo pipefail
cd ~/ops
die() { echo "sync: error: $*" >&2; exit 1; }
trap 'echo "sync: failed at line $LINENO: $BASH_COMMAND" >&2' ERR
source bin/retry.sh
export RETRY_SLEEP_SCALE=0.1

[[ -r data/orders.csv ]] || die "orders.csv missing"           # permanent: stop
extra=$(cat data/extra.csv 2>/dev/null || echo "")               # optional: fallback
rm -f state/sync.lock || true                                     # harmless
retry 5 bin/flaky partner 2                                       # temporary: retry
echo "sync: done, $(( $(wc -l < data/orders.csv) - 1 )) orders, extra rows: ${#extra}"''',
'<p>Run it twice: the second time the partner call succeeds at once (the counter remembers).</p>', expect='any') + puzzle_answer('<b>1.</b> <code>local total=$(compute_total)</code> is one <code>local</code> command whose status (0, the assignment worked) replaces the status of <code>$(compute_total)</code>, so set -e sees success. Write <code>local total; total=$(compute_total)</code>. <b>2.</b> A failing command inside an <code>if</code> test is supposed not to stop the script: that failure is the “false” branch. set -e only acts on failures that are not part of a condition. <b>3.</b> Wrap the API call in a <code>retry</code> with a limit and back-off that retries only temporary exit codes (503 → curl exit 22 with -f, timeouts, exit 75); permanent errors still stop at once with <code>|| die</code>, and an ERR trap tells her the exact line.') + qc('Which option makes an ERR trap fire inside functions?', 'set -E (errtrace).') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../01-script-craft/01-anatomy-of-a-real-script/">Lesson 1.1</a> (set -euo pipefail) and <a href="../../02-working-with-data/03-temporary-files-trap-and-clean-up/">Lesson 2.3</a> (trap).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
