import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# A report job that needs scratch space; everything stays inside ~/ops (our own TMPDIR) so counts are exact
SS = r"""rm -rf ~/ops; mkdir -p ~/ops/data ~/ops/bin ~/ops/tmp ~/ops/out; cd ~/ops
export TMPDIR=$HOME/ops/tmp
seq 1 5000 | awk '{printf "%d,%s,%d\n", $1, ($1%3==0?"Pune":($1%3==1?"Mumbai":"Delhi")), ($1*37)%1000}' > data/orders.csv
cat > bin/report.sh <<'EOF'
#!/usr/bin/env bash
# report.sh - build a per-city report through temp files; always cleans up
set -euo pipefail
readonly PROG=${0##*/}
work=$(mktemp -d "${TMPDIR:-/tmp}/report.XXXXXX")
cleanup() {
  local rc=$?
  rm -rf -- "$work"
  echo "$PROG: cleaned $(basename "$work") (exit $rc)" >&2
}
trap cleanup EXIT
trap 'echo "$PROG: interrupted" >&2; exit 130' INT
trap 'echo "$PROG: terminated" >&2; exit 143' TERM

sort -t, -k2,2 data/orders.csv > "$work/sorted.csv"
awk -F, '{s[$2]+=$3} END {for (c in s) print c, s[c]}' "$work/sorted.csv" | sort > "$work/totals.txt"
[[ ${FAIL:-} == 1 ]] && { echo "$PROG: simulated failure" >&2; exit 1; }
sleep "${SLOW:-0}"
mv -- "$work/totals.txt" out/report.txt
echo "$PROG: report written" >&2
EOF
chmod +x bin/report.sh"""

HOOK = hook('Riya’s report job needs scratch space: a sorted copy of the orders, intermediate totals, a downloaded file. Her first version wrote to <code>/tmp/report.tmp</code>. Two problems appeared within a week: when two copies of the job ran at the same time, they overwrote each other’s file; and every time the job failed or someone pressed Ctrl+C, the temp files stayed behind until <code>/tmp</code> was full. The fix is two tools that belong together: <b>mktemp</b> creates a temp file or folder with a unique, unguessable name, and <b>trap</b> runs a clean-up function whenever the script ends: success, error, <code>set -e</code> exit, Ctrl+C or <code>kill</code>.',
    ['create unique temp files and folders with mktemp (templates, -d, TMPDIR) instead of fixed names',
     'clean up reliably with a trap on EXIT, and handle INT and TERM with the right exit codes',
     'keep the original exit status in the clean-up function, and write results atomically with mv',
     'know what trap cannot catch (kill -9) and how to sweep old leftovers'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the full /tmp'),
    ('decide', 'Which tool?', 2, 'the quick chart'),
    ('definition', 'mktemp and trap', 5, 'simple meaning + 4 depths'),
    ('types', 'Signals and endings', 4, 'what trap catches'),
    ('commands', 'Step by step', 15, 'mktemp, trap, atomic writes'),
    ('animation', 'See it happen', 4, 'every ending cleans up'),
    ('run', 'Run on your PC', 3, 'Ctrl+C for real'),
    ('lab', 'Practice lab', 8, 'a job that never leaks'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('I need… → use', [
    ('one scratch file', 'tmp=$(mktemp)', 'unique name'),
    ('several scratch files', 'work=$(mktemp -d)', 'one folder'),
    ('a recognisable name', 'mktemp -t report.XXXXXX', 'X = random'),
    ('clean-up on every exit', 'trap cleanup EXIT', 'success and failure'),
    ('a message on Ctrl+C', "trap '…; exit 130' INT", 'then EXIT runs'),
    ('no half-written result', 'write to temp, then mv', 'atomic'),
])

cmap = concept_map(
    [('1.4', 'Template', 'trap cleanup EXIT'), ('L:11.3', 'Signals', 'TERM, INT, KILL'), ('1.3', 'Exit codes', '128+N')],
    ['why fixed temp names are dangerous', 'mktemp, -d, templates, TMPDIR', 'trap … EXIT', 'INT and TERM handlers', 'keeping the exit status', 'atomic writes with mv', 'what trap cannot catch'],
    [('3.1', 'Error handling', 'ERR trap'), ('3.2', 'Locks', 'only one copy'), ('2.4', 'sed, awk, jq', 'temp outputs'), ('4.1', 'Backup tool', 'scratch space')],
    'Unique scratch space, always removed, and results that appear all at once or not at all.')

sc = (term(20, 14, 316, 156, ['$ ./report.sh', ('report.sh: report written', 'out'), ('report.sh: cleaned report.Ab3x9Q (exit 0)', 'acc'), '$ FAIL=1 ./report.sh', ('report.sh: simulated failure', 'err'), ('report.sh: cleaned report.k2LmP0 (exit 1)', 'acc')], title='riya@server: ~/ops', prompt='$', size=6.6, step=18)
      + t(352, 36, 'Every ending cleans up:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['success', 'error / set -e', 'Ctrl+C (INT)', 'kill (TERM)', 'not: kill -9'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The full /tmp</h2>
  <div class="story">
''' + puzzle('Riya’s old job used <code>/tmp/report.tmp</code>. Two copies started by cron and by a colleague at the same minute produced a report with half of each other’s data. After a month, <code>ls /tmp</code> showed 400 leftover files from failed runs. Then she added <code>rm /tmp/report.tmp</code> as the last line of the script, and files <i>still</i> piled up. Why did the rm at the end not help, and what makes two copies safe?') + '''
    <p class="narration">In <code>~/ops</code> (every run in this lesson is real; <code>TMPDIR</code> points to <code>~/ops/tmp</code> so we can count leftovers exactly).</p>
''' + scene('A terminal: report.sh succeeds and cleans its temp folder; with FAIL=1 it fails and still cleans up.', sc,
            '<tspan font-weight="700" class="s-acc">trap EXIT</tspan> runs however the script ends.') + '''
K> Why not just delete the file at the end?
A> Because “the end” is only reached on success. With <code>set -e</code>, a failing command exits the script on the spot; Ctrl+C kills it in the middle; a <code>kill</code> from a monitoring tool stops it anywhere. A trap on EXIT is called by Bash in all of those cases.
R> And mktemp?
A> It makes a name nobody else is using, like <code>report.Ab3x9Q</code>, and creates the file with permissions only you can read, so two runs, two users or an attacker cannot collide with it.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Four ways a script can end, success, error, Ctrl+C and kill, all lead into the EXIT trap, which removes the temp folder; only kill -9 bypasses it.">'
       + ''.join(label_box(14, 14 + i * 40, 150, 32, [s], c, 8.6) + arrow(166, 30 + i * 40, 250, 92) for i, (s, c) in enumerate([('success', 'green'), ('error / set -e', 'red'), ('Ctrl+C (INT)', 'amber'), ('kill (TERM)', 'violet')]))
       + label_box(256, 66, 150, 52, ['trap cleanup EXIT', 'rm -rf "$work"'], 'blue', 8.8)
       + arrow(408, 92, 470, 92) + label_box(476, 70, 150, 44, ['temp folder gone'], 'green', 8.8)
       + label_box(14, 172, 150, 28, ['kill -9 (KILL)'], 'card', 8.4) + t(330, 190, 'cannot be trapped: leftovers possible', 8.6, 'red', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Temp files and trap at four depths', [
    ('v', 'No jargon: a hotel room', '      <p>mktemp is the receptionist giving you a room nobody else has; trap is the checkout rule: whenever you leave, for whatever reason, the room is cleaned.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>tmp=$(mktemp)</code> or <code>work=$(mktemp -d)</code></li>
        <li><code>cleanup() { rm -rf -- "$work"; }</code></li>
        <li><code>trap cleanup EXIT</code> right after creating it</li>
        <li><code>mv -- "$work/result" final.txt</code> at the end</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li>EXIT runs on normal end, <code>exit N</code> and <code>set -e</code> failures. For INT/TERM, add traps that <code>exit 130</code>/<code>143</code>; the EXIT trap then runs too.</li>
        <li>Save the status first in the handler: <code>local rc=$?</code>, so clean-up commands do not change the script’s exit code.</li>
        <li><code>mktemp</code> respects <code>TMPDIR</code>; templates need at least 3 trailing X’s (6 is usual).</li>
        <li>Write results to a temp file on the <b>same file system</b>, then <code>mv</code>: readers see the old file or the new one, never half of one.</li>
      </ul>'''),
    ('a', 'Behind the screen: O_EXCL, signals and rename()', '''      <ul>
        <li>mktemp opens with <code>O_CREAT|O_EXCL</code> and mode 0600 (0700 for -d): creation fails if the name exists, which defeats symlink attacks on predictable names like <code>/tmp/report.tmp</code>.</li>
        <li>Bash runs traps between commands. While a foreground child runs, a TERM sent only to bash waits until the child finishes; Ctrl+C reaches the whole process group, so both stop.</li>
        <li>SIGKILL (9) and SIGSTOP cannot be caught by any process; leftovers are then possible, which is why systemd-tmpfiles and periodic sweeps exist.</li>
        <li><code>mv</code> within one file system is the <code>rename(2)</code> system call: atomic. Across file systems it becomes copy + delete, which is not.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>mktemp and trap</h2>
''' + def_block(
    '<b>mktemp</b> creates a temporary file (or, with <code>-d</code>, a directory) with a unique random name and private permissions, and prints its path. <b>trap</b> is a Bash built-in that registers commands to run when the shell receives a signal (such as INT or TERM) or reaches a pseudo-signal such as <b>EXIT</b> (the shell is about to exit, for any reason) or ERR.',
    'mktemp gives unique scratch space; trap EXIT guarantees it is removed.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('mktemp', 'Unique temp file/folder.'),
    ('TMPDIR', 'Where temp files go.'),
    ('XXXXXX', 'Random part of a template.'),
    ('trap … EXIT', 'Run on any exit.'),
    ('SIGINT', 'Ctrl+C, exit 130.'),
    ('SIGTERM', 'Polite kill, exit 143.'),
    ('SIGKILL', 'kill -9, untrappable.'),
    ('Atomic', 'All at once or not at all.'),
]) + '\n' + names('Where the names come from.', [
    ('mktemp', 'make temporary', 'OpenBSD, 1996.'),
    ('/tmp', 'temporary', 'Often cleared at boot (tmpfs).'),
    ('trap', 'catch a signal', 'Bourne shell.'),
    ('EXIT', 'pseudo-signal 0', 'trap … 0 is the same.'),
    ('INT', 'interrupt', 'Ctrl+C.'),
    ('TERM', 'terminate', 'Default of kill.'),
    ('HUP', 'hang-up', 'Terminal closed.'),
    ('O_EXCL', 'exclusive create', 'open(2) flag.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Temp file', '<code>tmp=$(mktemp)</code>'),
    ('Temp folder', '<code>d=$(mktemp -d)</code>'),
    ('Clean-up', '<code>trap cleanup EXIT</code>'),
    ('List traps', '<code>trap -p</code>'),
    ('Remove a trap', '<code>trap - EXIT</code>'),
    ('Ctrl+C code', '130 (128+2)'),
]) + '\n' + lv + didyou('On many systems <code>/tmp</code> is a <b>tmpfs</b>: it lives in RAM and is empty after every reboot. Big temp files there use memory, not disk; for multi-gigabyte scratch data set <code>TMPDIR=/var/tmp</code> (on disk, kept across reboots) for that job.') + '''
EXAM> “How do you make sure a script’s temp files are removed even if it fails?” → Create them with mktemp and register trap 'rm -rf -- "$tmp"' EXIT right after; EXIT runs on success, exit, set -e failures and (with INT/TERM traps) on signals.
''' + qc('Why is /tmp/report.tmp a bad temp file name?', 'Two runs collide, and anyone can pre-create or symlink that predictable name.') + mistake('tmp=/tmp/myjob.tmp; …; rm $tmp   (last line)',
    'tmp=$(mktemp); trap \'rm -f -- "$tmp"\' EXIT',
    'The rm is skipped on every failure and Ctrl+C, and parallel runs share one file.') + mistake("trap 'rm -rf $work' EXIT   (before work is set, unquoted)",
    'work=$(mktemp -d); trap \'rm -rf -- "$work"\' EXIT   (single quotes, after mktemp)',
    'With double quotes or an empty variable the trap command can become rm -rf with no path, or the wrong path.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>How a script can end, and what runs</h2>
''' + table(['Ending', 'Exit code', 'EXIT trap runs?', 'Notes'], [
    ['last line reached', 'last status', 'yes', 'normal'],
    ['<code>exit N</code> / <code>die</code>', 'N', 'yes', 'clean'],
    ['<code>set -e</code> failure', 'failing status', 'yes', 'automatic'],
    ['Ctrl+C (SIGINT)', '130', 'yes, in Bash', 'add an INT trap for a message'],
    ['<code>kill PID</code> (SIGTERM)', '143', 'only with a TERM trap', 'trap TERM → exit 143'],
    ['terminal closed (SIGHUP)', '129', 'only with a HUP trap', 'nohup/tmux avoid it'],
    ['<code>kill -9</code> (SIGKILL)', '137', '<b>never</b>', 'sweep leftovers'],
    ['power loss / OOM kill', '—', 'never', 'tmpfs /tmp clears at boot'],
], minw=560) + table(['mktemp form', 'Creates'], [
    ['<code>mktemp</code>', '<code>$TMPDIR/tmp.XXXXXXXXXX</code> (file)'],
    ['<code>mktemp -d</code>', 'a private folder'],
    ['<code>mktemp -t name.XXXXXX</code>', 'recognisable name in TMPDIR'],
    ['<code>mktemp "$dir/x.XXXXXX"</code>', 'in a chosen folder'],
    ['<code>mktemp --suffix=.csv</code>', 'with an extension (GNU)'],
    ['<code>mktemp -u</code>', 'only a name, no file (unsafe, avoid)'],
], minw=420) + qc('Which ending can no trap catch?', 'SIGKILL (kill -9), and of course power loss.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>mktemp, trap, signals and atomic writes</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops</code>: <code>data/orders.csv</code> (5,000 orders) and <code>bin/report.sh</code>, which sorts and totals through a temp folder. <code>TMPDIR</code> is <code>~/ops/tmp</code>, so <code>ls tmp | wc -l</code> counts leftovers exactly.</p>
''' + cmdcard_u(['any scratch file or folder'], ['fixed names in /tmp', 'mktemp -u'])(
    'mktemp', 'mktemp · -d · -t name.XXXXXX · TMPDIR', 'unique temp files',
    'mktemp creates the file (or folder with <code>-d</code>) and prints its path; capture it with <code>$( )</code>. The name has a random part, the permissions are private (600 / 700), and <code>TMPDIR</code> decides where it goes.',
    'work=$(mktemp -d "${TMPDIR:-/tmp}/report.XXXXXX")', 'safe',
    [('mktemp', 'file', '0600'),
     ('-d', 'folder', '0700'),
     ('name.XXXXXX', 'template', 'recognisable'),
     ('TMPDIR', 'location', 'per job'),
     ('--suffix=.csv', 'extension', 'tools that care'),
     ('-u', 'name only', 'avoid: race')],
    dict(setup=SS, cmd="cd ~/ops\na=$(mktemp); b=$(mktemp)\necho \"two calls, two names: $(basename \"$a\") $(basename \"$b\")\"\nd=$(mktemp -d \"$TMPDIR/report.XXXXXX\")\nstat -c '%A %n' \"$a\" \"$d\" | sed \"s|$HOME|~|\" | sed -E 's/(tmp\\.|report\\.)[A-Za-z0-9]+/\\1XXXX/'\nrm -rf -- \"$a\" \"$b\" \"$d\"", note='Random parts are shortened to XXXX so the output repeats. rw------- and rwx------: private.'),
    [('sec', [
        dict(situation='Why fixed names are unsafe: two runs collide.', setup=SS, cmd="cd ~/ops; ( echo 'run A' > tmp/fixed.tmp; sleep 0.2; echo \"A reads back: $(cat tmp/fixed.tmp)\" ) & ( sleep 0.1; echo 'run B' > tmp/fixed.tmp ) & wait", why='A’s data was overwritten by B. With mktemp each run has its own file.')]),
    ],
    anat=anatomy([('work=', 'cmd', 'capture the path'), ('mktemp -d', 'opt', 'unique folder'), ('"$TMPDIR/report.XXXXXX"', 'arg', 'template')], 'Six X’s become random letters and digits.')
) + cmdcard_u(['every script that creates anything temporary'], ['rm as the last line'])(
    'trap', "trap cleanup EXIT · trap -p · trap - EXIT", 'clean up on every exit',
    'Register the clean-up <b>right after</b> creating the temp folder. In the handler, save <code>$?</code> first so the script still exits with its real status, then remove with <code>rm -rf -- "$work"</code> (quoted, with <code>--</code>).',
    'cleanup() { local rc=$?; rm -rf -- "$work"; exit $rc; }; trap cleanup EXIT', 'change',
    [('trap fn EXIT', 'on any exit', 'register'),
     ("single quotes", 'expand later', 'trap \'…$x…\''),
     ('local rc=$?', 'keep status', 'first line'),
     ('rm -rf -- "$work"', 'quoted, --', 'safe'),
     ('trap -p', 'show traps', 'debug'),
     ('trap - EXIT', 'unregister', 'rare')],
    dict(setup=SS, cmd="cd ~/ops\nbin/report.sh; echo \"exit $?\"; cat out/report.txt\nFAIL=1 bin/report.sh; echo \"exit $?\"\necho \"leftovers in tmp: $(ls tmp | wc -l)\"", note='Success and failure both clean up; the failure keeps exit 1 and leaves no folder behind.', expect='any'),
    [('dev', [
        dict(situation='Without the trap: one failure, one leftover.', setup=SS, cmd="cd ~/ops; bash -c 'set -e; w=$(mktemp -d); false; rm -rf \"$w\"'; echo \"exit $?, leftovers: $(ls tmp | wc -l)\"", why='The rm on the last line never ran.', expect='any'),
        dict(situation='The status survives the clean-up.', cmd="bash -c 'cleanup(){ local rc=$?; echo \"cleanup sees $rc\"; }; trap cleanup EXIT; exit 7'; echo \"caller sees $?\"", why='local rc=$? first.', expect='any')]),
    ]
) + cmdcard_u(['long jobs someone may stop'], ['ignoring signals'])(
    'signals', "trap '…; exit 130' INT · trap '…; exit 143' TERM", 'Ctrl+C and kill',
    'Bash runs the EXIT trap on Ctrl+C, but a <code>kill</code> (TERM) ends the script without it unless you trap TERM. A handler that prints a message and calls <code>exit 130</code> / <code>exit 143</code> makes both cases clean and gives the conventional codes.',
    "trap 'echo interrupted >&2; exit 130' INT; trap 'exit 143' TERM", 'safe',
    [('INT', 'Ctrl+C', 'exit 130'),
     ('TERM', 'kill PID', 'exit 143'),
     ('HUP', 'terminal closed', 'exit 129'),
     ('kill -9', 'not catchable', 'sweep'),
     ("trap '' INT", 'ignore Ctrl+C', 'critical sections'),
     ('kill -l', 'list signals', 'numbers')],
    dict(setup=SS, cmd="cd ~/ops\nSLOW=5 bin/report.sh & pid=$!; sleep 1; kill -TERM $pid; wait $pid; echo \"after TERM: exit $?\"\n( sleep 1; pkill -INT -f 'bin/report.sh' ) & SLOW=5 bin/report.sh; echo \"after INT (as Ctrl+C would send): exit $?\"\necho \"leftovers in tmp: $(ls tmp | wc -l)\"", note='Both stops print a message, clean up, and use the standard codes (128+15, 128+2). For the INT test the job runs in the foreground: Bash ignores Ctrl+C in background jobs of scripts.', expect='any'),
    [('sys', [
        dict(situation='kill -9: the trap never runs.', setup=SS, cmd="cd ~/ops; SLOW=5 bin/report.sh & pid=$!; sleep 1; kill -KILL $pid; wait $pid 2>/dev/null; echo \"exit $?, leftovers: $(ls tmp | wc -l)\"; pkill -P $$ sleep 2>/dev/null; true", why='One folder stays behind: that is what sweeps are for.', expect='any')]),
    ]
) + cmdcard_u(['output files others read', 'reports, configs, web files'], ['writing straight into the final file'])(
    'atomic', 'write to temp → mv', 'atomic results',
    'Build the result in a temp file in the <b>same folder or file system</b> as the target, then <code>mv</code> it over the old one. Readers (a web server, another job) see the complete old file or the complete new one, never a half-written file, and a failed run leaves the old result untouched.',
    'tmp=$(mktemp "out/.report.XXXXXX"); build > "$tmp"; mv -- "$tmp" out/report.txt', 'change',
    [('same file system', 'rename() atomic', 'required'),
     ('.name.XXXXXX', 'hidden temp', 'next to target'),
     ('mv -- tmp final', 'swap', 'last step'),
     ('chmod first', 'mktemp is 600', 'readers need 644'),
     ('failed run', 'old file stays', 'safe'),
     ('cp + rm', 'not atomic', 'across file systems')],
    dict(setup=SS, cmd="cd ~/ops\nbin/report.sh 2>/dev/null; echo 'old report:'; cat out/report.txt\nFAIL=1 bin/report.sh 2>/dev/null; echo \"failed run (exit $?): report unchanged?\"; cat out/report.txt", note='The failed run never touched out/report.txt: the mv is the last step.', expect='any'),
    [('devops', [
        dict(situation='Same inode trick: mv replaces, readers keep the old copy open.', setup=SS, cmd="cd ~/ops; echo v1 > out/page.html; exec 3< out/page.html; t=$(mktemp out/.page.XXXXXX); echo v2 > \"$t\"; chmod 644 \"$t\"; mv -- \"$t\" out/page.html; echo \"open reader still sees: $(cat <&3)\"; echo \"new readers see: $(cat out/page.html)\"; exec 3<&-", why='A reader in the middle of the old file is not disturbed.')]),
    ]
) + cmdcard_u(['servers with many jobs'], ['assuming traps always ran'])(
    'sweep', 'find "$TMPDIR" -name "report.*" -mmin +60 -delete', 'sweeping old leftovers',
    'kill -9, OOM kills and power cuts leave leftovers. Name temp files with a recognisable template (<code>report.XXXXXX</code>) so a sweep can remove only yours, and only old ones. systemd-tmpfiles does this for /tmp on most distributions.',
    "find \"${TMPDIR:-/tmp}\" -maxdepth 1 -name 'report.*' -mmin +60 -exec rm -rf -- {} +", 'danger',
    [('-maxdepth 1', 'only the top', 'safe'),
     ("-name 'report.*'", 'only yours', 'template'),
     ('-mmin +60', 'older than 1 h', 'not running jobs'),
     ('-print first', 'dry run', 'always'),
     ('-exec rm -rf -- {} +', 'delete', 'folders'),
     ('systemd-tmpfiles', 'OS sweep', '/tmp age rules')],
    dict(setup=SS, cmd="cd ~/ops\nmkdir tmp/report.OLD111 tmp/report.NEW222 tmp/other.keep; touch -d '3 hours ago' tmp/report.OLD111\necho 'dry run:'; find tmp -maxdepth 1 -name 'report.*' -mmin +60 -print | sed 's|^|  |'\nfind tmp -maxdepth 1 -name 'report.*' -mmin +60 -exec rm -rf -- {} +\nls tmp", note='Only the old report folder is removed; the new one (maybe a running job) and other files stay.'),
    [('sys', [
        dict(situation='How the OS cleans /tmp (typical rule file).', cmd="printf '# /usr/lib/tmpfiles.d/tmp.conf (typical)\\nq /tmp 1777 root root 10d\\nq /var/tmp 1777 root root 30d\\n'", why='Files older than 10 / 30 days are removed by systemd-tmpfiles-clean.timer.')]),
    ]
) + undo('Temp-file mistakes are usually leftovers or lost results:', [
    ('Leftovers piled up:', 'sweep by template and age (card above), then add the trap.'),
    ('Result half-written:', 'the job wrote straight to the target; restore from backup and switch to temp + mv.'),
    ('Trap deleted the wrong folder:', 'the variable was empty or unquoted; always <code>rm -rf -- "${work:?}"</code>.'),
    ('Job always exits 0 now:', 'the clean-up function changed $?; save <code>local rc=$?</code> first.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(cmd="mktemp /tmp/report.XX", meaning='Templates need at least 3 X’s.', fix='mktemp /tmp/report.XXXXXX'),
    dict(cmd="mktemp -d /nonexistent/x.XXXXXX", meaning='The parent folder does not exist (or TMPDIR points nowhere).', fix='Create it, or fix TMPDIR.'),
    dict(cmd="bash -c 'w=/tmp/demo-$$; mkdir -p \"$w\"; trap \"rm -rf $W\" EXIT; echo \"trap is: $(trap -p EXIT)\"'", meaning='Double quotes expanded the (misspelled, empty) variable when the trap was set: the trap is rm -rf with no path.', fix="Single quotes and the right name: trap 'rm -rf -- \"$w\"' EXIT"),
]) + qc('A script is stopped with kill (no -9) and has only an EXIT trap. Does it clean up?', 'Not reliably: add a TERM trap that calls exit 143, which then runs EXIT.') + '''
'''
cards = cards + '</section>\n'

def ending(k):
    o = t(180, 18, 'report.sh: four endings', 9.6, 'ink2', bold=True)
    rows = [('success', 'EXIT trap → cleaned (exit 0)', 'green'), ('FAIL=1 / set -e', 'EXIT trap → cleaned (exit 1)', 'red'), ('Ctrl+C', 'INT → exit 130 → EXIT → cleaned', 'amber'), ('kill', 'TERM → exit 143 → EXIT → cleaned', 'violet')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 7.8)
    return o
see_cmds = [['$ ./report.sh', ('cleaned (exit 0)', 'out')], ['$ FAIL=1 ./report.sh', ('cleaned (exit 1)', 'err')], ['^C', ('interrupted · cleaned (exit 130)', 'err')], ['$ kill PID', ('terminated · cleaned (exit 143)', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@server: ~/ops', prompt='$', size=7.0) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Success.', 'Error.', 'Ctrl+C.', 'kill.'])]
two = anim_two('Every ending cleans up', 'Behind the screen: signal → exit → EXIT trap',
               'A terminal ends report.sh four ways; each prints cleaned.', 'Rows show the path from each ending to the clean-up.', see, [ending(k) for k in range(4)],
               ['success.', 'error.', 'Ctrl+C.', 'kill.'], ['ok', 'error', 'INT', 'TERM'])

def at(k):
    o = t(180, 18, 'out/report.txt', 9.6, 'ink2', bold=True)
    o += label_box(14, 36, 160, 46, ['report.txt', ['old (complete)', 'old (complete)', 'new (complete)', 'new (complete)'][k]], ['green', 'green', 'blue', 'blue'][k], 8.4)
    o += label_box(186, 36, 160, 46, ['.report.Xy12', ['', 'being written…', '(renamed)', ''][k]], ['card', 'amber', 'card', 'card'][k], 8.4)
    o += t(180, 112, ['readers see the old report', 'new one built in a hidden temp file', 'mv = rename(): one instant swap', 'never a half-written report'][k], 9.2, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Atomic replace with mv',
              'Build aside, swap in one step.', 'temp + mv', 'Two boxes: the live report and the hidden temp file.', [at(k) for k in range(4)],
              ['old.', 'build.', 'swap.', 'done.'], hid='scenario-atomic')

dx = dissect('Layer by layer: what keeps temp files safe',
    'Each layer has a real command from our build machine.', [
    dict(key='name', name='Unique name', sub='random XXXXXX', why='No collisions.', how='O_EXCL create.', impl='mktemp.', used='Every run.',
         cmd="for i in 1 2 3; do mktemp -u -t demo.XXXXXX | sed 's|.*/||'; done | sort -u | wc -l | sed 's/^/distinct names: /'"),
    dict(key='perm', name='Private', sub='0600 / 0700', why='Others cannot read.', how='umask-independent.', impl='mktemp.', used='Secrets in temp.',
         cmd="f=$(mktemp); stat -c '%a' \"$f\"; d=$(mktemp -d); stat -c '%a' \"$d\"; rm -rf -- \"$f\" \"$d\""),
    dict(key='trap', name='Trap', sub='EXIT', why='Always removed.', how='Shell runs it last.', impl='Built-in.', used='Every script.',
         cmd="bash -c 'trap \"echo trap ran\" EXIT; echo working; exit 3'; echo \"exit $?\"", expect='any'),
], hint='Name → permissions → trap. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Every ending cleans up, and atomic writes</h2>
''' + two + s1 + dx + qc('Why must the temp file for mv be on the same file system?', 'Only then is mv a single rename(); across file systems it is copy + delete, not atomic.') + '''
</section>
'''

VAR = variations('Fifteen more temp-file and trap patterns. All were really run on our build machine.', [
    ('mktemp', [
        dict(title='Temp file with an extension', cmd="f=$(mktemp --suffix=.csv); echo \"${f##*.}\"; rm -f -- \"$f\"", why='Some tools need .csv.'),
        dict(title='In a chosen folder', setup=SS, cmd="cd ~/ops; f=$(mktemp out/.part.XXXXXX); dirname \"$f\"; rm -f -- \"$f\"", why='Next to the target for mv.'),
        dict(title='TMPDIR per job', cmd="mkdir -p big; TMPDIR=$PWD/big mktemp | sed \"s|$PWD|.|; s/tmp\\..*/tmp.XXXX/\"", why='For big scratch data.'),
        dict(title='Several files in one folder', cmd="w=$(mktemp -d); touch \"$w\"/{a,b,c}.txt; ls \"$w\"; rm -rf -- \"$w\"", why='One trap cleans them all.'),
    ]),
    ('trap', [
        dict(title='See registered traps', cmd="trap 'echo bye' EXIT; trap -p EXIT; trap - EXIT", why='trap -p for debugging.'),
        dict(title='Trap order: INT then EXIT', cmd="bash -c 'trap \"echo EXIT trap\" EXIT; trap \"echo INT trap; exit 130\" INT; kill -INT $$; sleep 1'; echo \"exit $?\"", why='Both run.', expect='any'),
        dict(title='Several commands in one trap', cmd="bash -c 'a=$(mktemp); b=$(mktemp); trap \"rm -f -- \\\"\\$a\\\" \\\"\\$b\\\"; echo removed 2 files\" EXIT'", why='Or call one function.'),
        dict(title='Trap in a subshell is separate', cmd="( trap 'echo subshell done' EXIT; echo in subshell ); echo 'main continues'", why='Each ( ) has its own EXIT.'),
        dict(title='Ignore Ctrl+C for a critical step', cmd="bash -c 'trap \"\" INT; kill -INT $$; echo still running after INT; trap - INT'", why='trap "" ignores a signal.'),
    ]),
    ('Clean-up details', [
        dict(title='Keep the exit status', cmd="bash -c 'c(){ local rc=$?; rm -f /dev/null/x 2>/dev/null; exit $rc; }; trap c EXIT; exit 4'; echo \"exit $?\"", why='rm failed, status still 4.', expect='any'),
        dict(title='Guard against an empty path', cmd="w=''; ( rm -rf -- \"${w:?refusing: empty path}\" ) 2>&1 | sed 's/.*: //'", why='${w:?} stops it.'),
        dict(title='Keep temp files when debugging', cmd="KEEP=1 bash -c 'w=$(mktemp -d); cleanup(){ [[ ${KEEP:-} == 1 ]] && { echo \"kept for debugging\"; return; }; rm -rf -- \"$w\"; }; trap cleanup EXIT'", why='A switch for investigations.'),
    ]),
    ('Atomic and sweep', [
        dict(title='Atomic append-free update of a counter file', cmd="echo 41 > n.txt; t=$(mktemp ./.n.XXXXXX); echo $(( $(cat n.txt) + 1 )) > \"$t\"; mv -- \"$t\" n.txt; cat n.txt", why='Read, write aside, swap.'),
        dict(title='Same file system?', setup=SS, cmd="cd ~/ops; [[ $(stat -c %d tmp) == $(stat -c %d out) ]] && echo 'tmp and out: same file system, mv is atomic'", why='stat %d = device.'),
        dict(title='Dry-run the sweep', setup=SS, cmd="cd ~/ops; mkdir tmp/report.A; touch -d '2 hours ago' tmp/report.A; find tmp -maxdepth 1 -name 'report.*' -mmin +60 -print | wc -l", why='Look before deleting.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Temp files and traps at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['ETL', 'scratch'], 'blue', 8.6), '1. Data jobs',
              'Extract, sort and join steps write intermediate files into one mktemp -d folder removed by a trap, even when Airflow kills the task.', ['extract', '*mktemp -d', 'trap']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['web', 'atomic'], 'green', 8.6), '2. Publishing files',
    'Static sites, nginx configs and price lists are written aside and mv’d into place so users never see half a file.', ['build', '*temp', 'mv']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['secrets', '0600'], 'red', 8.6), '3. Secrets in scripts',
    'Decrypted keys or tokens go into mktemp files (private by default) and are wiped by the EXIT trap.', ['decrypt', '*0600', 'trap rm']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['CI', 'runners'], 'amber', 8.6), '4. CI runners',
    'Shared build machines run many jobs at once; fixed temp names cause flaky builds that mktemp fixes.', ['parallel', '*unique', 'stable']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ops', 'sweeps'], 'violet', 8.6), '5. Housekeeping',
    'systemd-tmpfiles and cron sweeps remove old leftovers by name and age after crashes and kill -9.', ['leftovers', '*find -mmin', 'clean']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful patterns. All really run on our build machine.', [
    dict(level='b', title='A temp file', scenario='Scratch.', cmd="t=$(mktemp); echo data > \"$t\"; cat \"$t\"; rm -f -- \"$t\"", explain='Create, use, remove.'),
    dict(level='b', title='Temp folder + trap', scenario='Any script.', cmd="bash -c 'w=$(mktemp -d); trap \"rm -rf -- \\\"\\$w\\\"; echo cleaned\" EXIT; touch \"$w/x\"'", explain='Trap right after mktemp.'),
    dict(level='i', title='Run the report', scenario='Job.', setup=SS, cmd="cd ~/ops; bin/report.sh 2>&1 | sed -E 's/cleaned report\\.[A-Za-z0-9]+/cleaned report.XXXX/'; cat out/report.txt", explain='Cleaned every time.'),
    dict(level='i', title='Count leftovers', scenario='Health check.', setup=SS, cmd="cd ~/ops; FAIL=1 bin/report.sh 2>/dev/null; ls tmp | wc -l", explain='0 thanks to the trap.', expect='any'),
    dict(level='a', title='Stop it politely', scenario='Long job.', setup=SS, cmd="cd ~/ops; SLOW=3 bin/report.sh 2>&1 & p=$!; sleep 1; kill $p; wait $p; echo \"exit $?\" ", explain='TERM → 143, cleaned.', expect='any'),
], extra=build_up('from /tmp/report.tmp to a safe job', 'Riya fixes her old job step by step.', SS, [
    ("cd ~/ops; bash -c 'set -e; t=/tmp/report-old.tmp; sort data/orders.csv > $t; false; rm -f $t'; ls /tmp/report-old.tmp && rm -f /tmp/report-old.tmp", '1. Old: fixed name, rm at the end, left behind on failure.'),
    ("cd ~/ops; bash -c 'set -e; t=$(mktemp); trap \"rm -f -- \\\"\\$t\\\"\" EXIT; sort data/orders.csv > \"$t\"; false'; echo \"leftovers: $(ls tmp | wc -l)\"", '2. mktemp + trap: nothing left.'),
    ("cd ~/ops; FAIL=1 bin/report.sh 2>&1 | tail -1 | sed -E 's/cleaned report\\.[A-Za-z0-9]+/cleaned report.XXXX/'", '3. The full script: status kept in the message.'),
    ("cd ~/ops; bin/report.sh 2>/dev/null; wc -l < out/report.txt; ls tmp | wc -l", '4. Result in place, scratch gone.'),
], cumulative=False, expect='any')) + VAR + which('Choosing the right tool.', [
    ('Scratch file', 'mktemp', 'Unique, private.', '/tmp/name.tmp.'),
    ('Many scratch files', 'mktemp -d', 'One trap.', 'Many names.'),
    ('Always clean', 'trap … EXIT', 'Every ending.', 'rm at the end.'),
    ('Ctrl+C / kill', 'INT/TERM traps', 'Codes 130/143.', 'Nothing.'),
    ('Publish a result', 'temp + mv', 'Atomic.', 'Writing in place.'),
    ('Crash leftovers', 'sweep by name+age', 'Targeted.', 'rm -rf /tmp/*.'),
]) + keys('Handy forms.', [
    ('work=$(mktemp -d)', 'scratch folder', 'unique'),
    ("trap 'rm -rf -- \"$work\"' EXIT", 'clean-up', 'right after'),
    ("trap 'exit 130' INT; trap 'exit 143' TERM", 'signals', 'codes'),
    ('cleanup(){ local rc=$?; …; }', 'keep status', 'first line'),
    ('mv -- "$tmp" final', 'atomic', 'last step'),
    ("find \"$TMPDIR\" -name 'job.*' -mmin +60", 'sweep', 'by name+age'),
]) + scriptit('safe-job.sh', 'A complete pattern: a private scratch folder, a clean-up that keeps the exit status, INT/TERM handling, and an atomic publish, ready to paste into any job.',
'''#!/usr/bin/env bash
set -euo pipefail
readonly PROG=${0##*/}
work=$(mktemp -d "${TMPDIR:-/tmp}/${PROG%.sh}.XXXXXX")
cleanup() {
  local rc=$?
  rm -rf -- "${work:?}"
  (( rc == 0 )) || echo "$PROG: failed (exit $rc), scratch removed" >&2
  exit "$rc"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

seq 1 10 > "$work/numbers"
awk '{s += $1} END {print "sum", s}' "$work/numbers" > "$work/result"
mkdir -p out
tmp=$(mktemp out/.result.XXXXXX)
cp -- "$work/result" "$tmp"
chmod 644 "$tmp"
mv -- "$tmp" out/result.txt
cat out/result.txt''',
'<p>Every line from this lesson in one place; the job prints sum 55.</p>', expect='any') + puzzle_answer('<b>1.</b> The <code>rm</code> on the last line runs only when the script reaches the last line. With <code>set -e</code> any failure exits earlier, Ctrl+C stops it mid-way, and <code>kill</code> ends it anywhere, so the file stays. <code>trap cleanup EXIT</code> (plus INT/TERM traps) runs on every ending. <b>2.</b> A fixed name like <code>/tmp/report.tmp</code> is shared by every run: two runs write into the same file. <code>mktemp</code> gives each run its own unique, private name, so parallel runs (and other users) never collide.') + qc('In which order do you write mktemp and trap?', 'mktemp first, then trap immediately after, so the trap knows the path and nothing can fail in between.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../01-script-craft/04-a-reusable-script-template-and-shellcheck/">Lesson 1.4</a> (trap in the template) and <a href="../../../linux/11-processes/03-signals-kill-pkill-killall-sigterm-vs-sigkill/">Linux Lesson 11.3</a> (signals).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
