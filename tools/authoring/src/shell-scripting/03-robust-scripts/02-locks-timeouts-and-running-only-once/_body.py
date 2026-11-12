import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# A job that appends to a shared report; run twice at once it corrupts it. Locks live in ~/ops/run.
SS = r'''rm -rf ~/ops; mkdir -p ~/ops/bin ~/ops/run ~/ops/out; cd ~/ops
cat > bin/append.sh <<'EOF'
#!/usr/bin/env bash
# append.sh NAME: read the counter, think, write counter+1 (a classic read-modify-write)
n=$(cat ~/ops/out/counter 2>/dev/null || echo 0)
sleep 0.2
echo $(( n + 1 )) > ~/ops/out/counter
echo "$1 wrote $(( n + 1 ))"
EOF
cat > bin/job.sh <<'EOF'
#!/usr/bin/env bash
# job.sh NAME: the same work, protected by flock; only one copy at a time
set -euo pipefail
exec 9> ~/ops/run/job.lock
if ! flock -n 9; then echo "$1: another copy is running, skipping" >&2; exit 0; fi
~/ops/bin/append.sh "$1"
EOF
chmod +x bin/*.sh
echo 0 > out/counter'''

HOOK = hook('Riya’s report job runs every 5 minutes from cron. One day the database is slow, a run takes 7 minutes, the next run starts while the first is still working, and both write the same file: the report ends up with half of each. Another night a network copy simply hangs, and the job never finishes. Two failures that <code>set -e</code> and retries cannot fix: <b>two copies at once</b> and <b>steps that never end</b>. This lesson adds a <b>lock</b> with <code>flock</code> so only one copy runs, <code>timeout</code> so nothing runs forever, and the patterns behind them: lock files, PID files, stale locks and idempotent steps.',
    ['show how two copies of a job corrupt shared data (a race condition) and prevent it with flock',
     'use flock -n (skip), flock -w (wait with a limit) and the exec 9>file pattern, and know why mkdir also works as a lock',
     'limit any command’s run time with timeout, -k and exit code 124, and set a deadline for a whole script',
     'avoid stale-lock and PID-file traps, and make steps idempotent so a rerun is always safe'])
ROAD = roadmap([
    ('story', 'The story', 3, 'two copies, one file'),
    ('decide', 'Which tool?', 2, 'the quick chart'),
    ('definition', 'Locks and timeouts', 5, 'simple meaning + 4 depths'),
    ('types', 'Lock types compared', 4, 'flock, mkdir, PID file'),
    ('commands', 'Step by step', 15, 'race, flock, timeout'),
    ('animation', 'See it happen', 4, 'the race, then the lock'),
    ('run', 'Run on your PC', 3, 'cron + flock'),
    ('lab', 'Practice lab', 8, 'one copy, limited time'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('I need… → use', [
    ('only one copy, skip if busy', 'flock -n LOCKFILE CMD', 'cron jobs'),
    ('only one copy, wait my turn', 'flock -w 60 LOCKFILE CMD', 'queues'),
    ('lock inside the script', 'exec 9>f; flock -n 9 || exit', 'whole script'),
    ('a step must not hang', 'timeout 30 CMD', 'exit 124 on timeout'),
    ('it ignores TERM', 'timeout -k 5 30 CMD', 'KILL after 5 s more'),
    ('safe to run again', 'idempotent steps', 'check before doing'),
])

cmap = concept_map(
    [('3.1', 'Error handling', 'retries'), ('2.3', 'trap', 'clean-up'), ('L:11.3', 'Signals', 'TERM, KILL')],
    ['race conditions', 'flock -n / -w / -x / -s', 'exec 9>file locks', 'mkdir as an atomic lock', 'stale locks and PID files', 'timeout, -k, exit 124', 'idempotent steps'],
    [('3.3', 'Testing scripts', 'test concurrency'), ('4.1', 'Backup tool', 'one at a time'), ('4.4', 'cron and timers', 'schedules'), ('L:17.3', 'systemd service', 'built-in limits')],
    'One copy at a time, nothing runs forever, and any rerun is safe.')

sc = (term(20, 14, 316, 156, ['$ bin/job.sh A & bin/job.sh B', ('B: another copy is running, skipping', 'err'), ('A wrote 1', 'out'), '$ timeout 2 bash -c "sleep 10"; echo $?', ('124', 'acc')], title='riya@server: ~/ops', prompt='$', size=6.8, step=20)
      + t(352, 36, 'Two new guards:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['flock: one copy', 'timeout: a limit', 'exit 124 = timed out', 'idempotent steps', '= safe reruns'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Two copies, one file</h2>
  <div class="story">
''' + puzzle('Five copies of <code>append.sh</code> each read a counter, add 1 and write it back. Run one after another, the counter ends at 5. Started at the same moment, it ends at 1. Riya first “fixes” it with <code>[[ -e job.lock ]] &amp;&amp; exit; touch job.lock; …; rm job.lock</code>: it still breaks sometimes, and after one crash the job never runs again. Why does the check-then-create lock fail, and why does a crash leave the job stuck?') + '''
    <p class="narration">In <code>~/ops</code> (every run in this lesson is real). <code>bin/append.sh</code> reads <code>out/counter</code>, waits 0.2 s (the “work”), and writes counter+1. <code>bin/job.sh</code> is the same job protected by flock.</p>
''' + scene('A terminal: two copies of job.sh start; B finds the lock taken and skips, A writes 1; timeout stops a 10-second command after 2 seconds with exit 124.', sc,
            '<tspan font-weight="700" class="s-acc">flock</tspan> lets one copy in; <tspan font-weight="700" class="s-acc">timeout</tspan> ends hangs.') + '''
K> Why does the counter end at 1?
A> All five read 0 before any of them wrote. Each writes 0+1. This is a <b>race condition</b>: the result depends on timing. The check-then-create lock has the same race: two copies can both see “no lock” before either creates it.
R> So a lock must be checked and taken in one step.
A> Exactly. The kernel’s <code>flock</code> does that atomically, and it releases the lock automatically when the process ends, even after a crash or kill -9. No stale lock files.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Two jobs A and B reach a lock: A takes it and works; B finds it taken and either skips (flock -n) or waits (flock -w); when A ends, the kernel releases the lock automatically.">'
       + label_box(14, 40, 120, 40, ['job A'], 'blue', 9) + label_box(14, 120, 120, 40, ['job B'], 'amber', 9)
       + arrow(136, 60, 250, 90) + arrow(136, 140, 250, 110)
       + label_box(256, 76, 130, 48, ['flock job.lock', 'kernel lock'], 'violet', 8.6)
       + arrow(388, 90, 470, 60) + label_box(476, 40, 150, 40, ['A works'], 'green', 9)
       + arrow(388, 110, 470, 140) + label_box(476, 120, 150, 40, ['B: skip (-n) / wait (-w)'], 'red', 8.4)
       + t(320, 192, 'lock released automatically when A exits (even kill -9)', 9, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Locks and timeouts at four depths', [
    ('v', 'No jargon: a single-person changing room', '      <p>The door locks from inside. The next person either waits or comes back later. When you leave, the door unlocks by itself, even if you ran out in a hurry.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>flock -n /run/lock/report.lock ./report.sh</code> in cron</li>
        <li>inside a script: <code>exec 9&gt;/run/lock/report.lock; flock -n 9 || exit 0</code></li>
        <li><code>timeout 300 rsync -a src/ dst/</code></li>
        <li><code>timeout -k 10 300 ./step.sh</code></li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li><code>-n</code> fails at once if locked (skip this run); <code>-w N</code> waits up to N seconds; no option waits forever.</li>
        <li>flock locks belong to the <b>open file</b>: they disappear when the process (and its children holding fd 9) exit. A lock <i>file</i> left on disk is harmless; only a held lock blocks.</li>
        <li><code>timeout</code> sends TERM (exit 124 if it fired); <code>-k 5</code> sends KILL 5 s later if the command ignores TERM; <code>-s INT</code> chooses another signal.</li>
        <li>An idempotent step gives the same result if run twice: <code>mkdir -p</code>, <code>ln -sfn</code>, “create user if missing”.</li>
      </ul>'''),
    ('a', 'Behind the screen: flock(2) and atomic operations', '''      <ul>
        <li><code>flock(2)</code> is an advisory lock on an open file description, kept by the kernel: only programs that also call flock respect it. Exclusive (<code>-x</code>, default) vs shared (<code>-s</code>) locks allow one writer or many readers.</li>
        <li><code>mkdir</code> is atomic (create-or-fail in one system call), so <code>mkdir lockdir</code> is a portable lock, but it is not released on crash: you need a trap and stale-lock handling.</li>
        <li>PID files can lie: after a crash and reboot the PID may belong to another process (PID reuse). Check <code>/proc/PID/cmdline</code> or prefer flock.</li>
        <li>flock does not work reliably on some network file systems (older NFS); keep lock files on local disk, e.g. <code>/run/lock</code> or <code>/var/lock</code>.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Locks, timeouts and idempotence</h2>
''' + def_block(
    'A <b>lock</b> makes sure only one process at a time runs a critical section; <b>flock</b> takes a kernel-managed lock on a file atomically and releases it automatically when the process exits. A <b>timeout</b> limits how long a command may run; the <code>timeout</code> command stops it with a signal and exits 124. A step is <b>idempotent</b> when running it again produces the same result, so reruns and retries are safe.',
    'One copy at a time, nothing runs forever, reruns change nothing extra.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Race condition', 'Result depends on timing.'),
    ('Critical section', 'Code only one copy may run.'),
    ('flock', 'Kernel file lock.'),
    ('Exclusive / shared', 'One writer / many readers.'),
    ('Stale lock', 'Left behind by a dead process.'),
    ('timeout', 'Limit run time; exit 124.'),
    ('Idempotent', 'Same result when repeated.'),
    ('fd 9', 'A file descriptor kept for the lock.'),
]) + '\n' + names('Where the names come from.', [
    ('flock', 'file lock', 'BSD 4.2, 1983.'),
    ('race', 'processes racing', 'Who gets there first.'),
    ('mutex', 'mutual exclusion', 'Dijkstra, 1965.'),
    ('PID file', 'process ID in a file', '/run/*.pid.'),
    ('124', 'timeout’s exit code', 'GNU coreutils.'),
    ('/run/lock', 'lock folder (tmpfs)', 'Cleared at boot.'),
    ('idempotent', 'idem = same', 'Maths, 1870.'),
    ('advisory', 'only if everyone asks', 'Not enforced.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Skip if running', '<code>flock -n f cmd</code>'),
    ('Wait 60 s max', '<code>flock -w 60 f cmd</code>'),
    ('Whole script', '<code>exec 9&gt;f; flock -n 9</code>'),
    ('Time limit', '<code>timeout 30 cmd</code>'),
    ('Timed out', 'exit <b>124</b>'),
    ('Force kill', '<code>timeout -k 5 30 cmd</code>'),
]) + '\n' + lv + didyou('The flock man page has a ready-made line for the top of any script: <code>[ "${FLOCKER}" != "$0" ] &amp;&amp; exec env FLOCKER="$0" flock -en "$0" "$0" "$@" || :</code>. It re-runs the script under a lock on the script file itself, so no separate lock file is needed.') + '''
EXAM> “How do you make sure a cron job never runs twice at the same time?” → Run it under flock: flock -n /var/lock/job.lock /path/job.sh (or take the lock inside the script with exec 9>file; flock -n 9 || exit). The kernel releases it automatically when the job ends.
''' + qc('Why does [[ -e lock ]] || touch lock not work as a lock?', 'Check and create are two steps: two copies can both pass the check before either creates the file.') + mistake('[[ -e /tmp/job.lock ]] && exit; touch /tmp/job.lock; …; rm /tmp/job.lock',
    'exec 9>/run/lock/job.lock; flock -n 9 || exit 0',
    'The check-then-create has a race, and a crash leaves the file forever: the job never runs again.') + mistake('rsync -a big/ remote:/backup/   with no limit in a nightly job',
    'timeout -k 60 3600 rsync -a big/ remote:/backup/',
    'A hung network copy blocks the job, and with a lock, every later run too.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Ways to lock, compared</h2>
''' + table(['Method', 'Atomic?', 'Released on crash?', 'Notes'], [
    ['<code>[[ -e f ]] || touch f</code>', 'no (race)', 'no', 'never use'],
    ['<code>mkdir lockdir</code>', 'yes', 'no (needs trap + stale check)', 'portable, works on NFS'],
    ['PID file', 'no', 'no (PID reuse)', 'for daemons, with checks'],
    ['<code>flock</code>', 'yes', '<b>yes</b>, by the kernel', 'best on Linux, local disk'],
    ['<code>set -o noclobber; &gt; f</code>', 'yes', 'no', 'creates only if missing'],
    ['systemd unit', 'yes', 'yes', 'a service runs once by design'],
], minw=560) + table(['flock option', 'Meaning'], [
    ['<code>-n</code>', 'non-blocking: fail (exit 1) if locked'],
    ['<code>-w N</code>', 'wait at most N seconds'],
    ['<code>-x</code> / <code>-s</code>', 'exclusive (default) / shared'],
    ['<code>-u</code>', 'unlock an fd early'],
    ['<code>-E N</code>', 'exit code to use when locked (instead of 1)'],
    ['<code>-o</code>', 'do not pass the lock to the command’s children'],
], minw=420) + qc('Which lock survives a kill -9 of its owner?', 'mkdir and PID files do (stale); a flock lock is released by the kernel.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>The race, flock, mkdir locks, timeouts and safe reruns</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops</code>: <code>bin/append.sh</code> (an unprotected read-modify-write of <code>out/counter</code>) and <code>bin/job.sh</code> (the same work under flock). Locks live in <code>~/ops/run</code>.</p>
''' + cmdcard_u(['understanding why locks exist'], ['assuming jobs never overlap'])(
    'race', 'two copies at once', 'the race condition',
    'Run the read-modify-write five times in a row and the counter is 5. Start the five at the same moment with <code>&amp;</code> and <code>wait</code>, and they all read the old value before anyone writes. That lost update is a race condition.',
    'for i in 1 2 3 4 5; do bin/append.sh $i & done; wait', 'change',
    [('&', 'run in background', 'parallel'),
     ('wait', 'wait for all', 'collect'),
     ('read-modify-write', 'unsafe', 'counters, files'),
     ('lost update', 'symptom', 'wrong totals'),
     ('timing-dependent', 'flaky', 'hard to test'),
     ('fix', 'a lock', 'next card')],
    dict(setup=SS, cmd="cd ~/ops\nfor i in 1 2 3 4 5; do bin/append.sh $i > /dev/null; done; echo \"one after another: counter=$(cat out/counter)\"\necho 0 > out/counter\nfor i in 1 2 3 4 5; do bin/append.sh $i > /dev/null & done; wait; echo \"all at once:        counter=$(cat out/counter)\"", note='Five updates, one survives: four were lost.'),
    [('dev', [
        dict(situation='The check-then-create lock still races.', setup=SS, cmd="cd ~/ops; echo 0 > out/counter\nbad(){ [[ -e run/bad.lock ]] && return; touch run/bad.lock; bin/append.sh \"$1\" > /dev/null; rm -f run/bad.lock; }\nfor i in 1 2 3; do bad $i & done; wait; echo \"counter=$(cat out/counter) (3 copies got past the check)\"", why='Check and create are two steps.')]),
    ],
    anat=anatomy([('n=$(cat f)', 'cmd', 'read'), ('… work …', 'opt', 'meanwhile others read too'), ('echo $((n+1)) > f', 'arg', 'write: overwrites theirs')], 'Any gap between read and write is a race window.')
) + cmdcard_u(['cron jobs', 'any shared file or resource'], ['network file systems (old NFS)'])(
    'flock', 'flock -n FILE CMD · exec 9>FILE; flock -n 9', 'one copy with flock',
    'flock takes the lock and runs the command in one atomic step. <code>-n</code> means “if busy, give up now” (exit 1); in a script, open the lock file on fd 9 with <code>exec 9&gt;file</code> and lock that fd, so the whole script is protected and the lock ends with the process.',
    'exec 9> ~/ops/run/job.lock; flock -n 9 || { echo "already running"; exit 0; }', 'change',
    [('flock -n f cmd', 'wrap a command', 'cron line'),
     ('exec 9>f', 'open fd 9', 'whole script'),
     ('flock -n 9', 'try to lock fd 9', 'skip if busy'),
     ('flock -w 30 9', 'wait ≤ 30 s', 'take turns'),
     ('exit 0 when busy', 'not an error', 'cron stays quiet'),
     ('lock file stays', 'harmless', 'only held locks block')],
    dict(setup=SS, cmd="cd ~/ops\nfor i in A B C D E; do bin/job.sh $i & done 2>&1; wait\necho \"counter=$(cat out/counter): one copy ran, four skipped\"\necho '--- taking turns with -w (wait up to 5 s):'\necho 0 > out/counter\nfor i in A B C; do flock -w 5 run/turns.lock bin/append.sh $i & done; wait\necho \"counter=$(cat out/counter): all three ran, one at a time\"", note='-n: only one copy works, the rest skip. -w: they queue and every update survives.'),
    [('sys', [
        dict(situation='The kernel releases the lock after kill -9.', setup=SS, cmd="cd ~/ops; ( exec 9> run/k.lock; flock 9; sleep 30 ) & p=$!; sleep 0.3\nflock -n run/k.lock true || echo 'locked while the holder runs'\nkill -9 $p; wait $p 2>/dev/null; pkill -f 'sleep 30' 2>/dev/null\nflock -n run/k.lock true && echo 'free immediately after kill -9: no stale lock'", why='No clean-up code needed.', expect='any')]),
    ]
) + cmdcard_u(['NFS, portability', 'when flock is missing'], ['forgetting the trap'])(
    'mkdir', 'mkdir LOCKDIR · trap rmdir · stale check', 'mkdir as a portable lock',
    '<code>mkdir</code> creates a folder or fails if it exists, in one atomic system call, on every Unix and on NFS. Remove it with a trap on EXIT. Because a crash leaves it behind, store the owner’s PID inside and treat the lock as <b>stale</b> if that process no longer exists.',
    'mkdir run/job.lockdir 2>/dev/null || { echo busy; exit 0; }; trap \'rm -rf run/job.lockdir\' EXIT', 'change',
    [('mkdir d', 'atomic create', 'or fail'),
     ('trap rm EXIT', 'release', 'normal exits'),
     ('echo $$ > d/pid', 'owner', 'stale check'),
     ('kill -0 PID', 'still alive?', 'no signal sent'),
     ('remove stale', 'then retry', 'carefully'),
     ('noclobber', 'set -C; > f', 'file variant')],
    dict(setup=SS, cmd="cd ~/ops\ntake() { mkdir run/job.lockdir 2>/dev/null && echo $$ > run/job.lockdir/pid; }\ntake && echo 'first: got the lock'\ntake || echo 'second: busy'\necho 99999 > run/job.lockdir/pid      # pretend the owner died\nowner=$(cat run/job.lockdir/pid); kill -0 \"$owner\" 2>/dev/null || { echo \"owner $owner is gone: stale lock, removing\"; rm -rf run/job.lockdir; }\ntake && echo 'third: got the lock after stale clean-up'", note='kill -0 only checks whether a process exists.', expect='any'),
    [('sec', [
        dict(situation='noclobber as a file lock.', setup=SS, cmd="cd ~/ops; ( set -C; echo $$ > run/noclob.lock ) 2>/dev/null && echo 'created: lock taken'; ( set -C; echo $$ > run/noclob.lock ) 2>/dev/null || echo 'exists: busy'", why='> refuses to overwrite with set -C.')]),
    ]
) + cmdcard_u(['network calls', 'anything that can hang'], ['jobs without any time limit'])(
    'timeout', 'timeout N cmd · -k · -s · exit 124', 'limit run time',
    '<code>timeout 30 cmd</code> runs cmd and sends TERM after 30 s; the exit code is then <b>124</b> (otherwise the command’s own code). <code>-k 5</code> sends KILL 5 s later for programs that ignore TERM. Units: <code>30</code>, <code>2m</code>, <code>1h</code>, decimals allowed.',
    'timeout -k 10 300 rsync -a src/ dst/', 'safe',
    [('timeout 30 cmd', 'TERM after 30 s', 'basic'),
     ('124', 'timed out', 'check it'),
     ('-k 5', 'then KILL', 'stubborn'),
     ('-s INT', 'other signal', 'graceful apps'),
     ('2m · 1.5', 'units', 'm h d'),
     ('--preserve-status', 'cmd’s own code', 'rare')],
    dict(setup=SS, cmd="cd ~/ops\ntimeout 1 sleep 5; echo \"sleep 5 with timeout 1: exit $?\"\ntimeout 5 sleep 0.2; echo \"sleep 0.2 with timeout 5: exit $?\"\ntimeout 0.5 bash -c 'trap \"\" TERM; sleep 3'; echo \"ignores TERM, no -k: exit $? (ran the full 3 s)\"\ntimeout -k 0.5 0.5 bash -c 'trap \"\" TERM; sleep 3'; echo \"ignores TERM, -k 0.5: exit $? (128+9 = killed)\"", note='124 = our timeout fired; 137 = it had to use KILL.', expect='any'),
    [('devops', [
        dict(situation='Treat a timeout differently from a failure.', cmd="timeout 0.3 sleep 2; rc=$?\ncase $rc in 0) echo ok;; 124) echo 'step timed out: retry later';; *) echo \"step failed ($rc)\";; esac", why='124 is a temporary error for retry() (Lesson 3.1).')]),
    ]
) + cmdcard_u(['reruns after failures', 'retries'], ['steps that double the work'])(
    'idem', 'mkdir -p · ln -sfn · grep -q || append · check first', 'idempotent steps',
    'With locks and retries, steps will be run again. Make each one safe to repeat: create only if missing, replace instead of append, skip work already done (a marker file or a check).',
    'grep -qxF "$line" file || echo "$line" >> file', 'change',
    [('mkdir -p', 'no error if exists', 'folders'),
     ('ln -sfn', 'replace link', 'releases'),
     ('grep -q || >>', 'add once', 'config lines'),
     ('[[ -e done.flag ]]', 'skip done work', 'markers'),
     ('id user || useradd', 'create once', 'users'),
     ('cp -n', 'no overwrite', 'seed files')],
    dict(setup=SS, cmd="cd ~/ops\nsetup() {\n  mkdir -p out/reports\n  grep -qxF 'retention=30' out/settings 2>/dev/null || echo 'retention=30' >> out/settings\n  ln -sfn reports out/latest\n  [[ -e out/.migrated ]] || { echo '  migrating (once)'; touch out/.migrated; }\n}\nfor run in 1 2 3; do echo \"run $run\"; setup; done\necho \"settings lines: $(wc -l < out/settings); link: $(readlink out/latest)\"", note='Three runs, one result: one settings line, one link, one migration.'),
    [('sys', [
        dict(situation='Not idempotent: append twice, get duplicates.', setup=SS, cmd="cd ~/ops; for i in 1 2; do echo 'retention=30' >> out/bad-settings; done; wc -l < out/bad-settings", why='Every rerun adds another line.')]),
    ]
) + undo('Concurrency bugs corrupt data quietly; recover and prevent:', [
    ('Corrupted shared file:', 'restore from backup or rebuild from source data; add flock before the next run.'),
    ('Job never runs (stale lock):', 'with flock this cannot happen; with mkdir/PID locks check the owner (<code>kill -0</code>) and remove the stale lock.'),
    ('Killed by timeout mid-write:', 'write to a temp file and mv (Lesson 2.3) so a stop never leaves half a file.'),
    ('Duplicates after a rerun:', 'deduplicate, then make the step idempotent.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(setup=SS, cmd="cd ~/ops && exec 9> run/held.lock && flock -n 9 && echo 'got it' && flock -n run/held.lock true; echo \"second flock: exit $?\"", meaning='The same lock file is already held (by fd 9 of this shell): -n fails with 1.', fix='Wait (-w), skip, or find the holder: fuser run/held.lock.'),
    dict(cmd="timeout 1 sleep 3; echo \"exit $?\"", meaning='124 is not an error of sleep: it means timeout stopped it.', fix='Check for 124 separately.'),
    dict(cmd="flock -n /nonexistent/dir/x.lock true", meaning='The lock file’s folder does not exist.', fix='mkdir -p the folder (e.g. /run/lock/myapp) first.'),
]) + qc('timeout returns 124. What happened?', 'The time limit was reached and timeout stopped the command.') + '''
'''
cards = cards + '</section>\n'

def race(k):
    o = t(180, 18, 'counter = 0, two copies', 9.6, 'ink2', bold=True)
    rows = [('A reads', '0', 'blue'), ('B reads', '0 (A has not written yet)', 'amber'), ('A writes', '1', 'blue'), ('B writes', '1: A’s update is lost', 'red')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
def locked(k):
    o = t(180, 18, 'with flock', 9.6, 'ink2', bold=True)
    rows = [('A locks', 'reads 0', 'blue'), ('B tries', 'busy → waits (-w) or skips (-n)', 'amber'), ('A writes', '1, unlocks', 'blue'), ('B locks', 'reads 1, writes 2', 'green')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
see_cmds = [['A: n=$(cat counter)', ('0', 'out')], ['B: n=$(cat counter)', ('0', 'out')], ['A: echo 1 > counter', ('', 'out')], ['B: echo 1 > counter', ('counter = 1 (should be 2)', 'err')]]
see = [term(14, 16, 332, 116, c, title='riya@server: ~/ops', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['A reads.', 'B reads.', 'A writes.', 'B writes.'])]
two = anim_two('A race, step by step', 'Behind the screen: and with a lock',
               'Two copies read the same value; one update is lost.', 'With flock the second copy waits, and both updates survive.', see, [locked(k) for k in range(4)],
               ['A reads.', 'B reads.', 'A writes.', 'B writes.'], ['1', '2', '3', '4'])

def to(k):
    o = t(180, 18, 'timeout -k 5 30 ./step.sh', 9.4, 'ink2', bold=True)
    rows = [('0 s', 'step starts', 'blue'), ('30 s', 'still running → TERM', 'amber'), ('35 s', 'ignored TERM → KILL', 'red'), ('result', 'exit 124 (or 137 after KILL)', 'violet')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
s1 = anim_one('Animated example', 'How timeout ends a hang',
              'TERM first, KILL if needed.', 'timeout -k', 'Rows: start, TERM at the limit, KILL after the grace period, exit code.', [to(k) for k in range(4)],
              ['start.', 'TERM.', 'KILL.', 'code.'], hid='scenario-timeout')

dx = dissect('Layer by layer: what a flock really is',
    'Each layer has a real command from our build machine.', [
    dict(key='file', name='Lock file', sub='just a file', why='A name to agree on.', how='Any path.', impl='Local disk.', used='/run/lock.',
         setup=SS, cmd="cd ~/ops; bin/job.sh X > /dev/null 2>&1; ls -l run/job.lock | awk '{print $1, $5, $9}'"),
    dict(key='fd', name='Open file', sub='fd 9', why='Lock is on the open file.', how='exec 9>f.', impl='/proc/$$/fd.', used='Whole script.',
         setup=SS, cmd="cd ~/ops; exec 9> run/demo.lock; ls -l /proc/$$/fd/9 | sed \"s|.*-> ||; s|$HOME|~|\""),
    dict(key='kernel', name='Kernel lock', sub='flock(2)', why='Atomic, auto-release.', how='One system call.', impl='/proc/locks.', used='Everyone who asks.',
         setup=SS, cmd="cd ~/ops; exec 9> run/demo2.lock; flock 9; grep -c FLOCK /proc/locks | sed 's/^/FLOCK entries in \\/proc\\/locks: /'"),
], hint='File → open file → kernel. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A race and its fix, and timeout</h2>
''' + two + s1 + dx + qc('Two copies run without a lock and both add 1 to a counter of 0. What can the result be?', '1 or 2, depending on timing: that is the race.') + '''
</section>
'''

VAR = variations('Fifteen more lock, timeout and idempotence patterns. All were really run on our build machine.', [
    ('flock', [
        dict(title='Custom exit code when busy', setup=SS, cmd="cd ~/ops; exec 9> run/e.lock; flock 9; flock -n -E 3 run/e.lock true; echo \"exit $?\"", why='-E distinguishes “busy” from a failure.', expect='any'),
        dict(title='Wait with a limit', setup=SS, cmd="cd ~/ops; ( flock run/w.lock sleep 1 ) & sleep 0.2; flock -w 0.3 run/w.lock true; echo \"waited 0.3 s: exit $?\"; wait", why='Gives up after 0.3 s.', expect='any'),
        dict(title='Shared locks for readers', setup=SS, cmd="cd ~/ops; ( flock -s run/s.lock sleep 0.5 ) & sleep 0.1; flock -s -n run/s.lock true && echo 'second reader allowed'; flock -x -n run/s.lock true || echo 'writer must wait'; wait", why='Many readers or one writer.'),
        dict(title='Release early', setup=SS, cmd="cd ~/ops; exec 8> run/u.lock; flock 8; echo 'critical part done'; flock -u 8; flock -n run/u.lock true && echo 'others may start now'", why='-u before slow non-critical work.'),
        dict(title='Who holds a lock?', setup=SS, cmd="cd ~/ops; ( exec 9> run/who.lock; flock 9; sleep 2 ) & sleep 0.2; awk '$2==\"FLOCK\"' /proc/locks | wc -l | sed 's/^/flock entries: /'; wait", why='/proc/locks lists all locks (fuser/lsof name the PID).'),
    ]),
    ('timeout', [
        dict(title='Minutes and decimals', cmd="timeout 0.2 sleep 1; echo \"exit $?\"; timeout 1m true; echo \"exit $?\"", why='Units s m h d.', expect='any'),
        dict(title='Graceful signal first', cmd="timeout -s INT 0.3 bash -c 'trap \"echo got INT, saving work; exit 0\" INT; sleep 2 & wait'; echo \"exit $?\"", why='Let the program clean up.', expect='any'),
        dict(title='Whole-script deadline', cmd="SECONDS=0; deadline=1; for step in a b c d e; do (( SECONDS >= deadline )) && { echo \"deadline reached before step $step\"; break; }; sleep 0.3; echo \"step $step done\"; done", why='Bash SECONDS counts up.'),
        dict(title='timeout inside retry', cmd="for try in 1 2; do timeout 0.2 sleep 1 && break; echo \"try $try timed out ($?)\"; done", why='124 as a temporary error.'),
    ]),
    ('Idempotence', [
        dict(title='Create a user only if missing (dry run)', cmd="u=riya; id \"$u\" >/dev/null 2>&1 && echo \"$u exists: nothing to do\" || echo \"would run: useradd $u\"", why='Check first.'),
        dict(title='Download only if newer (pattern)', cmd="touch -d '2 days ago' old.csv; [[ old.csv -nt marker ]] || echo 'source not newer than last run: skip'", why='-nt compares times.'),
        dict(title='Done-markers per item', cmd="mkdir -p done; for f in a b c; do [[ -e done/$f ]] && continue; echo \"processing $f\"; touch done/$f; done; echo 'second run:'; for f in a b c; do [[ -e done/$f ]] && continue; echo \"processing $f\"; done; echo '(nothing)'", why='Restart where it stopped.'),
        dict(title='Replace, never append', cmd="for i in 1 2 3; do printf 'port=9090\\n' > app.port; done; wc -l < app.port", why='> instead of >>.'),
        dict(title='Symlink switch is repeatable', cmd="mkdir -p r1 r2; for i in 1 2; do ln -sfn r2 current; done; readlink current", why='-n replaces the link itself.'),
        dict(title='set -C (noclobber) as a guard', cmd="set -C; echo first > once.txt; echo second > once.txt 2>/dev/null || echo 'refused to overwrite'; set +C; cat once.txt", why='Protects existing files.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Locks and timeouts at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['cron', 'flock'], 'blue', 8.6), '1. Overlapping cron jobs',
              'Every */5 cron job that can run longer than 5 minutes is wrapped in flock -n; slow nights skip a run instead of piling up.', ['*/5', '*flock -n', 'one copy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['deploy', 'lock'], 'green', 8.6), '2. Deploys',
    'Two engineers deploying at once is a classic outage; deploy scripts hold a lock for the whole release.', ['deploy', '*lock', 'serial']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['backup', 'timeout'], 'amber', 8.6), '3. Backups over the network',
    'rsync/scp steps run under timeout -k so a dead link does not block the next night.', ['rsync', '*timeout', 'next night ok']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['apt', 'dpkg'], 'violet', 8.6), '4. Package managers',
    'apt and dpkg take locks (/var/lib/dpkg/lock-frontend): the “could not get lock” message you meet in Linux 14.2.', ['apt', '*lock', 'one at a time']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['idempotent', 'IaC'], 'red', 8.6), '5. Infrastructure as code',
    'Ansible, Terraform and Puppet are built on idempotence: run them again and only differences change.', ['rerun', '*no change', 'safe']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful forms. All really run on our build machine.', [
    dict(level='b', title='Run only one copy', scenario='Cron.', setup=SS, cmd="cd ~/ops; flock -n run/one.lock bin/append.sh cron", explain='flock -n.'),
    dict(level='b', title='Time limit', scenario='Hang protection.', cmd="timeout 0.5 sleep 2; echo \"exit $?\"", explain='124.', expect='any'),
    dict(level='i', title='Lock the whole script', scenario='Inside a script.', setup=SS, cmd="cd ~/ops; bash -c 'exec 9> run/s.lock; flock -n 9 || exit 0; echo \"working with the lock\"'", explain='exec 9>; flock -n 9.'),
    dict(level='i', title='Is the lock busy?', scenario='Monitoring.', setup=SS, cmd="cd ~/ops; flock -n run/check.lock true && echo free || echo busy", explain='Probe with true.'),
    dict(level='a', title='Queue three jobs', scenario='Serial work.', setup=SS, cmd="cd ~/ops; for j in 1 2 3; do flock -w 5 run/q.lock bin/append.sh job$j & done; wait; cat out/counter", explain='-w: all run, in turn.'),
], extra=build_up('a safe cron job', 'Riya makes her 5-minute job safe against overlaps and hangs.', SS, [
    ("cd ~/ops; for i in 1 2 3; do bin/append.sh $i > /dev/null & done; wait; echo \"unprotected: counter=$(cat out/counter)\"", '1. Unprotected: lost updates.'),
    ("cd ~/ops; echo 0 > out/counter; for i in 1 2 3; do bin/job.sh $i 2>/dev/null & done; wait; echo \"flock -n: counter=$(cat out/counter) (overlaps skipped)\"", '2. flock -n: overlaps skip.'),
    ("cd ~/ops; timeout 0.5 bash -c 'sleep 3'; echo \"hung step stopped: exit $?\"", '3. timeout: a hang ends.'),
    ("cd ~/ops; echo '*/5 * * * * flock -n /run/lock/report.lock timeout -k 30 270 /home/riya/ops/bin/report.sh >> /home/riya/ops/out/cron.log 2>&1'", '4. The final crontab line.'),
], cumulative=False, expect='any')) + VAR + which('Choosing the right guard.', [
    ('One copy (cron)', 'flock -n', 'Atomic, auto-release.', 'touch lock files.'),
    ('Take turns', 'flock -w N', 'Queue with a limit.', 'Waiting forever.'),
    ('NFS / no flock', 'mkdir + trap + stale check', 'Portable.', 'PID file alone.'),
    ('Hangs', 'timeout -k', 'Always ends.', 'No limit.'),
    ('Reruns', 'idempotent steps', 'Safe.', 'Blind appends.'),
    ('Daemons', 'systemd unit', 'Built-in.', 'Hand-made PID logic.'),
]) + keys('Handy forms.', [
    ('flock -n /run/lock/x.lock cmd', 'skip if busy', 'cron'),
    ('exec 9>f; flock -n 9 || exit 0', 'whole script', 'top'),
    ('flock -w 60 f cmd', 'wait ≤ 60 s', 'queue'),
    ('timeout -k 10 300 cmd', 'limit + kill', 'any step'),
    ('(( rc == 124 ))', 'timed out', 'retry'),
    ('grep -qxF l f || echo l >> f', 'add once', 'idempotent'),
]) + scriptit('safe-job.sh', 'A cron-safe job: a flock on the whole script (skip quietly if already running), a timeout on the slow step, and idempotent setup, so overlaps, hangs and reruns are all harmless.',
'''#!/usr/bin/env bash
set -euo pipefail
mkdir -p run out
exec 9> run/safe-job.lock
flock -n 9 || { echo "safe-job: already running, skipping" >&2; exit 0; }

mkdir -p out/reports                                   # idempotent
grep -qxF 'retention=30' out/settings 2>/dev/null || echo 'retention=30' >> out/settings

if timeout -k 1 2 bash -c 'sleep 0.3; echo "report built"'; then
  echo "safe-job: ok"
else
  rc=$?
  (( rc == 124 )) && echo "safe-job: report step timed out" >&2 || echo "safe-job: report step failed ($rc)" >&2
  exit "$rc"
fi''',
'<p>Run it twice at once and the second copy only says it is skipping.</p>', expect='any') + puzzle_answer('<b>1.</b> The check (<code>[[ -e job.lock ]]</code>) and the create (<code>touch job.lock</code>) are two separate steps: two copies can both see “no lock” before either creates it, which is the same race as the counter. <b>2.</b> The <code>rm job.lock</code> at the end never runs after a crash or kill -9, so the file stays and every later run thinks the job is still running. <code>flock</code> fixes both: checking and taking the lock is one atomic kernel operation, and the kernel releases it when the process ends, however it ends.') + qc('Where should lock files live?', 'On a local disk, e.g. /run/lock or /var/lock (or a folder of your own), not on network file systems.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-error-handling-patterns-and-retries/">Lesson 3.1</a> (retries) and <a href="../../02-working-with-data/03-temporary-files-trap-and-clean-up/">Lesson 2.3</a> (trap, atomic writes).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
