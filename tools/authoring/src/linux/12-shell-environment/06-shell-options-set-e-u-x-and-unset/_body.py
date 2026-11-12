import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

SO = r"""rm -rf ~/so; mkdir -p ~/so/app; cd ~/so
printf 'GET /a 200\nGET /b 500\n' > access.log"""
DEPLOY = r"""printf '#!/bin/bash\necho "1. building"\ncp app/missing.jar /tmp/ 2>&1\necho "2. stopping old version"\necho "3. deploy done"\n' > ~/so/deploy.sh"""
VI = r"""rm -rf ~/vi; mkdir -p ~/vi; cd ~/vi
printf '%s\n' 'PS1="riya@web01:~$ "' 'set -o vi' > ~/vi/.rc"""

HOOK = hook('Riya’s deploy script prints an error on line 3, “cp: cannot stat app.jar”, and then cheerfully continues: it stops the old version, deploys nothing, and prints “deploy done”. The website is down and the CI pipeline is green, because the last command succeeded. Another script used <code>$BACKUP_DIR</code>, which was never set, and wrote backups into <code>/</code>. Bash’s defaults are forgiving: keep going after errors, treat unknown variables as empty, ignore failures in the middle of pipelines. A few <b>shell options</b> turn a forgiving shell into a strict one: <code>set -e</code>, <code>set -u</code>, <code>set -o pipefail</code>, and <code>set -x</code> to see every line as it runs.',
    ['make scripts stop at the first error with <code>set -e</code>, and know its exceptions and traps',
     'catch typos and missing settings with <code>set -u</code>, and failures inside pipes with <code>set -o pipefail</code>',
     'debug any script with <code>set -x</code> / <code>bash -x</code> and a better <code>PS4</code>; check syntax with <code>bash -n</code>',
     'use <code>set -o</code>, <code>set +o</code>, <code>noclobber</code>, <code>set -o vi</code>, <code>set --</code> and <code>unset</code> (variables and functions)'])
ROAD = roadmap([
    ('story', 'The story', 3, '“deploy done”, site down'),
    ('decide', 'Which option when?', 2, 'the quick chart'),
    ('definition', 'Shell options', 5, 'simple meaning + 4 depths'),
    ('types', 'The options compared', 4, 'what each one catches'),
    ('commands', 'Options by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'set -e stops the line'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'harden a script'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which option? (decide in 5 seconds)', [
    ('Stop at the first failing command', 'set -e', 'errexit'),
    ('Stop on an unset variable (typo!)', 'set -u', 'nounset'),
    ('A pipe fails if any part fails', 'set -o pipefail', 'not just the last'),
    ('All three, top of every script', 'set -euo pipefail', 'the “strict mode” line'),
    ('See each line as it runs', 'set -x   or   bash -x s.sh', 'xtrace, debugging'),
    ('Check syntax without running', 'bash -n s.sh', 'noexec'),
    ('Do not overwrite files with >', 'set -o noclobber', '>| to force'),
    ('Remove a variable or function', 'unset VAR   ·   unset -f FUNC', 'cleanup'),
])

cmap = concept_map(
    [('12.5', 'First script', 'exit status'), ('5.4', '&& and ||', 'exit codes'), ('12.4', 'Quoting', '${var:?}')],
    ['set -e (errexit) and its exceptions', 'set -u (nounset) and ${var:-default}', 'set -o pipefail', 'set -x, PS4, bash -n', 'set -o / +o, noclobber, vi mode, set --, unset'],
    [('12.8', 'if and test', 'handling errors yourself'), ('12.10', 'Functions and trap', 'clean-up on exit'), ('13.1', 'Combining commands', 'pipes'), ('17.4', 'cron', 'unattended scripts')],
    'Strict scripts start with set -euo pipefail. set -x shows what really runs. Options are switched on with - and off with +.')

sc = (term(20, 14, 316, 156, ['$ ./deploy.sh', ('1. building', 'out'), ("cp: cannot stat 'app.jar'", 'err'), ('2. stopping old version', 'out'), ('3. deploy done', 'out'), '$ echo $?', ('0', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Bash defaults:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• errors: carry on', '• $typo: empty', '• pipe: last wins', 'set -euo pipefail', '  makes it strict'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Deploy done”, website down</h2>
  <div class="story">
''' + puzzle('Riya adds <code>set -e</code> to a script. It contains <code>count=0</code> and later <code>((count++))</code> to count processed files. The script now stops silently right after processing the very first file, with exit status 1, and no error message. Why?') + '''
    <p class="narration">A failed copy should have stopped the deploy. Bash just kept going.</p>
''' + scene('A terminal: a deploy script prints a cp error but continues to “deploy done” and exits 0.', sc,
            'By default a failed command does <tspan font-weight="700" class="s-acc">not</tspan> stop a script.') + '''
K> Why would bash ever continue after an error?
A> In an interactive shell that is what you want: a typo should not close your terminal. Scripts inherit the same forgiving behaviour. You have to <b>ask</b> for strictness, with options switched on by <code>set</code>.
R> Which ones?
A> Three for safety (<code>-e</code>, <code>-u</code>, <code>pipefail</code>), one for seeing (<code>-x</code>). They have a few surprising exceptions, and the puzzle is one of them. Today you will see each on real runs.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A factory line: without set -e a broken part travels on to the end (shipped broken); with set -e the line stops at the first broken part; set -x is a camera filming every station.">'
       + label_box(14, 20, 190, 110, ['default', 'a broken part', 'travels on…', '“shipped!” (exit 0)'], 'red', 8.6)
       + label_box(224, 20, 190, 110, ['set -e / -u / pipefail', 'line STOPS at the', 'first broken part', 'exit ≠ 0'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['set -x', 'a camera at every', 'station: shows each', 'command as it runs'], 'amber', 8.6)
       + t(320, 160, 'Strict options catch problems early; -x shows where.', 9.6, 'ink2')
       + t(320, 182, 'set -o NAME = on, set +o NAME = off.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Shell options at four depths', [
    ('v', 'No jargon: a factory line', '      <p>Stop the line at the first broken part, and film every station.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li>Line 2 of every new script: <code>set -euo pipefail</code>.</li>
        <li>Debugging: <code>bash -x script.sh</code> prints each command with <code>+</code> before running it.</li>
        <li>Syntax only: <code>bash -n script.sh</code>.</li>
        <li><code>set -o</code> lists all options; <code>set +x</code> switches one off.</li>
      </ul>'''),
    ('i', 'The rules (and exceptions)', '''      <ul>
        <li><b>-e</b> exits when a command fails, except: commands in <code>if</code>/<code>while</code> conditions, before <code>&amp;&amp;</code>/<code>||</code>, negated with <code>!</code>, and non-last parts of a pipe.</li>
        <li>Under -e, <code>((count++))</code> with count=0 “fails” (the expression is 0), and <code>var=$(false)</code> exits; <code>local var=$(false)</code> does not.</li>
        <li><b>-u</b> makes using an unset variable an error; <code>${var:-default}</code> and <code>${var-}</code> are still allowed. <code>$@</code> with no arguments is fine in bash ≥ 4.4.</li>
        <li><b>pipefail</b>: a pipeline’s status is the last non-zero status in it (default: only the last command).</li>
        <li><b>-x</b> prints each command after expansion, prefixed with <code>$PS4</code> (default <code>+ </code>), to stderr.</li>
      </ul>'''),
    ('a', 'Behind the screen: $- and SHELLOPTS', '''      <ul>
        <li>Single-letter options are in <code>$-</code> (e.g. <code>hBeux</code>); long names in <code>$SHELLOPTS</code>. <code>set -o</code> prints them; <code>shopt</code> holds bash’s other options (Lesson 12.3).</li>
        <li><code>set -e</code> is ignored inside a function called from an <code>if</code> or <code>&amp;&amp;</code> context: the whole call becomes “checked”. This is why many experts prefer explicit checks plus <code>trap … ERR</code> (Lesson 12.10).</li>
        <li><code>PS4='+ ${BASH_SOURCE}:${LINENO}: '</code> adds file and line numbers to the trace.</li>
        <li><code>set -x</code> output goes to stderr: <code>exec 2&gt;trace.log</code> or <code>BASH_XTRACEFD</code> sends it to a file.</li>
        <li><code>set --</code> replaces the positional parameters ($1, $2…); <code>set</code> with no arguments lists all variables and functions.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Shell options with set</h2>
''' + def_block(
    'The <code>set</code> builtin turns shell options on (<code>-x</code> or <code>-o NAME</code>) and off (<code>+x</code> or <code>+o NAME</code>). <b>errexit</b> (<code>-e</code>) exits on the first failing command, <b>nounset</b> (<code>-u</code>) treats expansion of unset variables as an error, <b>pipefail</b> makes a pipeline fail if any of its commands fails, and <b>xtrace</b> (<code>-x</code>) prints each command before it runs. <code>unset</code> removes variables and functions.',
    'set -e = stop on error. set -u = stop on unknown variable. pipefail = pipes fail honestly. set -x = show me.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('errexit (-e)', 'Exit on the first failure.'),
    ('nounset (-u)', 'Unknown variable = error.'),
    ('pipefail', 'Any failing part fails the pipe.'),
    ('xtrace (-x)', 'Print each command.'),
    ('noexec (-n)', 'Read but do not run.'),
    ('noclobber (-C)', '> will not overwrite.'),
    ('PS4', 'Prefix of trace lines.'),
    ('Strict mode', 'set -euo pipefail.'),
]) + '\n' + names('Where the names come from.', [
    ('-e', 'errexit', 'Exit on error.'),
    ('-u', 'nounset', 'No unset variables.'),
    ('-x', 'xtrace', 'eXecution trace.'),
    ('-n', 'noexec', 'Syntax only.'),
    ('-C', 'noclobber', 'Do not clobber files.'),
    ('pipefail', 'pipe failure', 'bash 3.0, 2004.'),
    ('-o vi', 'vi keys', 'Command-line editing.'),
    ('+', 'switch off', 'Opposite of -.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Strict line', '<code>set -euo pipefail</code>'),
    ('Debug', '<code>bash -x s.sh</code>'),
    ('Syntax', '<code>bash -n s.sh</code>'),
    ('List', '<code>set -o</code>'),
    ('Off', '<code>set +x</code>'),
    ('Remove', '<code>unset v</code> · <code>unset -f f</code>'),
]) + '\n' + lv + didyou('<code>set -o vi</code> turns your command line into a tiny vi editor: press <kbd>Esc</kbd>, then <code>b</code>, <code>w</code>, <code>dw</code>, <code>0</code>, <code>$</code> work as in vim (Lesson 4.2). <code>set -o emacs</code> brings back the default keys.') + '''
EXAM> “How do you debug a shell script?” → <code>bash -x script.sh</code> (or <code>set -x</code> inside it) to print every command as executed; <code>bash -n</code> to check syntax.
''' + qc('Your script has <code>set -e</code>. Does <code>grep -q error log.txt || echo "no errors"</code> stop the script when grep finds nothing?', 'No: a command before || is “checked”, so set -e ignores its failure.') + mistake('set -e   and then   ((count++))   with count=0',
    'count=$((count + 1))   or   ((count++)) || true   or   ((++count))',
    '((expression)) returns status 1 when the expression’s value is 0, and count++ evaluates to the OLD value (0). set -e then exits silently. This is the puzzle; checked on our build machine.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The options compared</h2>
''' + table(['Option', 'Catches', 'Default without it', 'Watch out'], [
    ['<code>set -e</code>', 'a failing command', 'script continues', 'if/&&/|| conditions are exempt; ((x++)) at 0'],
    ['<code>set -u</code>', 'unset variable used', 'treated as empty', 'use ${var:-default} for optional ones'],
    ['<code>set -o pipefail</code>', 'failure inside a pipe', 'only last command counts', 'grep with no match = failure'],
    ['<code>set -x</code>', '(shows) every command', 'silent', 'prints secrets too!'],
    ['<code>set -n</code> / <code>bash -n</code>', 'syntax errors', 'found only when reached', 'does not catch typos in names'],
    ['<code>set -C</code>', 'overwriting with &gt;', 'file overwritten', '<code>&gt;|</code> forces'],
], minw=600) + table(['Form', 'Meaning'], [
    ['<code>set -x</code> / <code>set +x</code>', 'on / off (short)'],
    ['<code>set -o xtrace</code> / <code>set +o xtrace</code>', 'on / off (long)'],
    ['<code>bash -x s.sh</code>', 'on for one run, from outside'],
    ['<code>#!/bin/bash -e</code>', 'on from the shebang (one option only)'],
    ['<code>set -o</code>', 'list all (on/off)'],
    ['<code>echo $-</code>', 'active one-letter options'],
], minw=420) + table(['unset', 'Effect'], [
    ['<code>unset VAR</code>', 'remove a variable'],
    ['<code>unset -v VAR</code>', 'only a variable'],
    ['<code>unset -f NAME</code>', 'remove a function'],
    ['<code>unset arr[2]</code>', 'remove one array element'],
    ['readonly VAR', 'cannot be unset (12.1)'],
], minw=360) + qc('Without pipefail, what is the status of <code>false | true</code>? With it?', '0 without (the last command, true, decides); 1 with pipefail.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Shell options explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/so</code> with a two-line <code>access.log</code> and a broken <code>deploy.sh</code> whose line 3 copies a file that does not exist.</p>
''' + cmdcard_u(['every script that changes something (deploy, backup, delete)', 'scripts run by cron or CI'],
               ['commands you expect to fail sometimes (use || or if)', 'interactive shells (one typo closes the terminal)'])(
    'e', 'set -e (errexit)', 'stop at the first error',
    'After <code>set -e</code>, the script exits as soon as a command returns non-zero, with that status. Failures in <code>if</code>/<code>while</code> conditions, before <code>&amp;&amp;</code> or <code>||</code>, after <code>!</code>, and in non-final pipe parts do not count.',
    'set -e   ·   cmd || true   ·   if cmd; then …; fi', 'safe',
    [('set -e', 'switch on', 'line 2'),
     ('cmd || true', 'allow this one to fail', 'optional steps'),
     ('if cmd; then', 'handle failure yourself', 'decisions'),
     ('cmd || { echo msg; exit 1; }', 'fail with a message', 'clarity'),
     ('set +e … set -e', 'relax for a block', 'rare')],
    dict(setup=SO + '; ' + DEPLOY, cmd="cd ~/so\nbash deploy.sh; echo \"without -e: status $?\"\nsed -i '1a set -e' deploy.sh\nbash deploy.sh; echo \"with -e: status $?\"", expect='any', note='With set -e the deploy stops at the failed cp, and the status says so.'),
    [('devops', [
        dict(situation='Optional steps under set -e.', setup=SO, cmd="cd ~/so; cat > opt.sh <<'EOF'\nset -e\nrm -f /tmp/nothing-here.tmp\ngrep -q error access.log || echo 'no errors found (ok)'\nif ! grep -q 500 access.log; then echo 'no 500s'; else echo 'has 500s'; fi\necho finished\nEOF\nbash opt.sh; echo \"status $?\"",
             why='|| and if make failures “expected”, so set -e lets them pass.')]),
     ('qa', [
        dict(situation='The puzzle: ((count++)) at zero.', cmd="bash -c 'set -e; count=0; ((count++)); echo \"never printed\"'; echo \"status $?\"\nbash -c 'set -e; count=0; count=$((count+1)); echo \"count=$count\"'", expect='any',
             why='((0)) is “false” (status 1), and count++ returns the old value 0. Use count=$((count+1)) or ((++count)).')]),
    ],
    anat=anatomy([('set', 'cmd', 'builtin'), ('-e', 'opt', 'errexit'), ('-u', 'opt', 'nounset'), ('-o pipefail', 'opt', 'pipes')], 'set -euo pipefail = all three in one line.')
) + cmdcard_u(['catching typos in variable names', 'required settings (paths, hosts)'],
               ['variables that are optional by design (give them a default)'])(
    'u', 'set -u (nounset)', 'unknown variable = error',
    'With <code>set -u</code>, expanding a variable that was never set stops the script with “unbound variable”. Optional values use a default: <code>${VAR:-default}</code>, or <code>${VAR-}</code> for “empty if unset”.',
    'set -u   ·   ${VAR:-default}   ·   ${VAR:?message}', 'safe',
    [('set -u', 'switch on', 'catch typos'),
     ('${V:-x}', 'x if unset or empty', 'optional'),
     ('${V-}', 'empty if unset', 'quiet check'),
     ('${V:?msg}', 'stop with msg', 'required'),
     ('[ -n "${V-}" ]', 'is it set?', 'tests')],
    dict(cmd="cat > u.sh <<'EOF'\nset -u\nbackup_dir=/srv/backup\necho \"saving to $backpu_dir\"\nEOF\nbash u.sh; echo \"status $?\"", expect='any', note='A typo (backpu) would have saved to an empty path; set -u stopped it.'),
    [('sys', [
        dict(situation='Optional settings with defaults.', cmd="bash -c 'set -u; mode=${MODE:-dev}; echo \"mode=$mode\"'\nMODE=prod bash -c 'set -u; echo \"mode=${MODE:-dev}\"'",
             why='Required values get ${V:?}, optional ones ${V:-default}: set -u stays happy.')]),
    ]
) + cmdcard_u(['pipes inside scripts', 'checking that every stage worked'],
               ['pipes where an early stage is allowed to stop early (head can cause SIGPIPE, status 141)'])(
    'pipefail', 'set -o pipefail', 'honest pipelines',
    'Normally a pipeline’s status is the last command’s. With <code>pipefail</code> it is the last non-zero status of any command in it, so <code>set -e</code> also catches failures in the middle. <code>${PIPESTATUS[@]}</code> shows every part’s status.',
    'set -o pipefail   ·   echo "${PIPESTATUS[@]}"', 'safe',
    [('set -o pipefail', 'switch on', 'scripts'),
     ('${PIPESTATUS[@]}', 'all statuses', 'debugging'),
     ('grep … | wc -l', 'no match = failure!', 'expect it'),
     ('… | head', 'may give 141 (SIGPIPE)', 'careful')],
    dict(cmd="grep x /no/such/file | wc -l; echo \"default: $?\"\nset -o pipefail\ngrep x /no/such/file | wc -l; echo \"pipefail: $?   parts: ${PIPESTATUS[*]}\"", expect='any', note='Without pipefail the missing file went unnoticed (status 0 from wc).'),
    [('devops', [
        dict(situation='Strict mode in one line.', setup=SO, cmd="cd ~/so; printf 'set -euo pipefail\\ngrep 500 access.log | wc -l\\ngrep 999 access.log | wc -l\\necho never\\n' > strict.sh\nbash strict.sh; echo \"status $?\"", expect='any',
             why='The second grep found nothing (status 1); pipefail + -e stopped the script. If “no match” is fine, write grep … || true.')]),
    ]
) + mistake('#!/bin/bash -euo pipefail   (all options in the shebang)', '#!/bin/bash   then on line 2:   set -euo pipefail',
            'Linux passes everything after the interpreter as ONE argument, so the shebang trick works for a single option at most; set on line 2 always works, and also when someone runs bash script.sh.') + cmdcard_u(['finding which line misbehaves', 'seeing variable values as they really are'],
               ['scripts that handle passwords (trace prints them)', 'leaving it on in production logs'])(
    'x', 'set -x · bash -x · PS4', 'see every line',
    '<code>bash -x s.sh</code> (or <code>set -x</code> inside) prints each command after expansion, prefixed by <code>+</code>, to stderr. Nesting adds more <code>+</code>. <code>set +x</code> stops it. <code>PS4</code> changes the prefix, for example to show line numbers.',
    "bash -x s.sh   ·   set -x … set +x   ·   PS4='+ line $LINENO: '", 'safe',
    [('bash -x s.sh', 'trace whole run', 'quick debug'),
     ('set -x / set +x', 'trace a part', 'focus'),
     ("PS4='+ $LINENO: '", 'line numbers', 'long scripts'),
     ('2> trace.log', 'trace to a file', 'keep output clean'),
     ('bash -n', 'syntax only', 'before running')],
    dict(setup=SO, cmd="cd ~/so; printf 'f=access.log\\nn=$(grep -c 500 \"$f\")\\necho \"errors: $n\"\\n' > t.sh\nbash -x t.sh", note='You see the real values: the file name, the grep inside $( ) (two +), and the final echo.'),
    [('dev', [
        dict(situation='Line numbers in the trace.', setup=SO, cmd="cd ~/so; printf 'a=1\\nb=$((a+1))\\necho $b\\n' > ln.sh\nPS4='+ line $LINENO: ' bash -x ln.sh",
             why='In a 300-line script, the line number tells you where to look.')]),
     ('sec', [
        dict(situation='Trace leaks secrets.', cmd="bash -xc 'token=s3cr3t-abc; curl_cmd=\"curl -H Authorization:$token\"' 2>&1 | head -2",
             why='set -x prints values. Turn it off around secrets (set +x) and never keep traces of production runs that use credentials.')]),
    ]
) + cmdcard_u(['checking or changing options', 'protecting files from >', 'vi keys on the command line', 'removing variables and functions'],
               ['noclobber in scripts that are meant to overwrite'])(
    'misc', 'set -o · noclobber · vi · set -- · unset', 'more options',
    '<code>set -o</code> lists options; <code>set -o noclobber</code> (<code>-C</code>) makes <code>&gt;</code> refuse to overwrite (use <code>&gt;|</code>). <code>set -o vi</code> switches line editing to vi keys. <code>set -- a b</code> sets $1 $2. <code>unset NAME</code> removes a variable, <code>unset -f NAME</code> a function.',
    'set -o   ·   set -C   ·   set -o vi   ·   set -- ARGS   ·   unset [-f] NAME', 'change',
    [('set -o', 'list on/off', 'check'),
     ('set -C / >|', 'no overwrite / force', 'protect files'),
     ('set -o vi', 'vi editing keys', 'vim users'),
     ('set -- x y', '$1=x $2=y', 'tests'),
     ('unset v', 'remove variable', 'clean up'),
     ('unset -f f', 'remove function', 'clean up')],
    dict(cmd="set -o | grep -E '^(errexit|nounset|noclobber|pipefail|xtrace|vi) '\nset -C; echo one > keep.txt; echo two > keep.txt; echo \"status $?\"; echo three >| keep.txt; cat keep.txt", expect='any', note='noclobber refused the second >, and >| forced it.'),
    [('dev', [
        dict(situation='set -- and unset.', cmd="set -- alpha 'beta gamma'; echo \"$# args: $1 | $2\"\nv=5; f(){ echo hi; }; unset v; unset -f f\necho \"[${v-}]\"; type f 2>&1 | tail -1",
             why='set -- is handy for testing argument code; unset -f removes functions (plain unset tries a variable first).')]),
    ]
) + undo('Options are per shell; a new shell starts clean.', [
    ('Typed set -e in your terminal:', 'the next failing command closes it; <code>set +e</code> now, or just open a new terminal.'),
    ('Script stops “for no reason” with -e:', 'run <code>bash -x</code> to see the last line; look for ((x++)), grep with no match, $(…) failing.'),
    ('set -u breaks on optional variables:', 'give them defaults: <code>${VAR:-}</code>.'),
    ('Trace too noisy:', 'wrap only the suspicious part in <code>set -x</code> … <code>set +x</code>.'),
    ('noclobber blocks a needed overwrite:', '<code>&gt;|</code> or <code>set +C</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="bash -c 'set -u; echo $undefined_var'", meaning='set -u: the variable was never set.', fix='Set it, fix the typo, or use ${VAR:-default}.'),
    dict(cmd="bash -c 'set -C; echo a > f.txt; echo b > f.txt'", meaning='noclobber: > will not overwrite.', fix='<code>&gt;|</code> if you really mean it.'),
    dict(cmd="set -o nosuchoption", meaning='Unknown option name.', fix='<code>set -o</code> lists valid names.'),
    dict(cmd="bash -n missing_fi.sh", setup="printf 'if true; then\\n  echo x\\n' > missing_fi.sh", meaning='Syntax: an if without fi.', fix='Close every if/fi, case/esac, do/done.'),
]) + qc('Which status does <code>bash -c \'set -e; false; echo x\'</code> return?', '1: the status of false, the command that stopped it.') + '''
'''
VISC = screens_block('Real terminal screens: set -o vi on the command line', 'An interactive bash with <code>set -o vi</code>: you type normally (insert mode), then <kbd>Esc</kbd> gives you vi commands.',
    VI, 'bash --rcfile ~/vi/.rc', [
    ('type a command', "'echo one two three four'", ' typing works as usual (insert mode).'),
    ('Esc  b  b', 'Escape b b', ' Esc = normal mode; b jumps back one word, twice: the cursor is on “three”.'),
    ('d w', 'd w', ' dw deletes the word “three ”, just like vim.'),
    ('Enter', 'Enter', ' runs the edited command.'),
], 72, 8, what='bash with set -o vi')
cards = cards + VISC + '</section>\n'

def line(k, strict):
    steps = ['1. build', '2. cp app.jar ✗', '3. stop old', '4. “done” exit 0']
    o = ''
    for i, s in enumerate(steps):
        if strict:
            tn = 'green' if i == 0 and k >= 0 else ('red' if i == 1 and k >= 1 else ('card' if i > 1 else 'card'))
            if i > 1 and k >= 2: tn = 'card'
        else:
            tn = 'green' if i == 0 else ('red' if i == 1 and k >= 1 else ('amber' if i > 1 and k >= 2 else 'card'))
        o += label_box(14 + i * 86, 30, 80, 44, [s], tn, 7.6)
    return o
see_cmds = [['$ ./deploy.sh', ('1. building', 'out')], ['$ ./deploy.sh', ("cp: cannot stat 'app.jar'", 'err')], ['$ ./deploy.sh', ('2. stopping …', 'out'), ('3. deploy done', 'out'), ('$? = 0', 'acc')], ['$ (with set -e)', ("cp: cannot stat 'app.jar'", 'err'), ('$? = 1  (stopped)', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Step 1 works.', 'Step 2 fails…', '…default: carry on!', 'set -e: stop here.'])]
behind = [line(0, False) + t(180, 110, 'Each command runs in turn.', 8.6, 'violet', bold=True),
          line(1, False) + t(180, 110, 'cp returns status 1.', 8.6, 'red', bold=True),
          line(2, False) + t(180, 110, 'Default: the next commands still run.', 8.6, 'amber', bold=True),
          line(2, True) + t(180, 110, 'errexit: the script exits with status 1.', 8.6, 'green', bold=True)]
two = anim_two('set -e stops the line', 'Behind the screen: what happens after a failure',
               'A terminal: the deploy script fails at cp and continues to done; with set -e it stops at cp.',
               'Four step boxes: without set -e the steps after the failed cp still run; with set -e the script stops at cp.', see, behind,
               ['Run.', 'Fail.', 'Default.', 'set -e.'],
               ['status 0', 'status 1', 'ignored', 'exit 1'])

def pipe(k):
    parts = [('grep x /no/file', 'red'), ('wc -l', 'green')]
    o = ''.join(label_box(14 + i * 170, 30, 160, 40, [p, f'status {2 if i == 0 else 0}' if k >= 1 else ''], tn if k >= 1 else 'card', 8) for i, (p, tn) in enumerate(parts))
    if k >= 2:
        o += label_box(14, 90, 330, 32, ['default: pipeline status = last = 0'], 'amber', 8)
    if k >= 3:
        o += label_box(14, 132, 330, 32, ['pipefail: last non-zero = 2  → set -e stops'], 'green', 8)
    return o
frames = [pipe(0) + t(180, 190, 'A two-part pipeline.', 8.6, 'violet', bold=True),
          pipe(1) + t(180, 190, 'grep fails (2), wc succeeds (0).', 8.6, 'violet', bold=True),
          pipe(2) + t(180, 190, 'Default: only the last counts.', 8.6, 'amber', bold=True),
          pipe(3) + t(180, 190, 'pipefail: the failure is reported.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'Why pipes need pipefail',
              'The middle of a pipe can fail silently.',
              'pipefail', 'A grep that fails piped into wc that succeeds: the default status is 0, with pipefail it is 2.', frames,
              ['Pipe.', 'Statuses.', 'Default.', 'pipefail.'], hid='scenario-pipefail')

dx = dissect('Layer by layer: where options live',
    'Each layer has a real command and output from our build machine.', [
    dict(key='flags', name='$-', sub='one-letter options', why='Quick check.', how='Letters.', impl='Per shell.', used='Scripts.',
         cmd="bash -c 'echo \"$-\"'; bash -euc 'echo \"$-\"'"),
    dict(key='long', name='SHELLOPTS', sub='long names', why='Readable.', how='Colon list.', impl='Read-only variable.', used='set -o.',
         cmd="bash -o pipefail -c 'echo \"$SHELLOPTS\"' | tr : '\\n' | grep -E 'pipefail|hashall'"),
    dict(key='pipes', name='PIPESTATUS', sub='each part', why='Who failed?', how='Array.', impl='Last pipeline.', used='Debugging.',
         cmd="true | false | true; echo \"${PIPESTATUS[*]}\""),
    dict(key='trace', name='xtrace + PS4', sub='the trace', why='See values.', how='stderr.', impl='PS4 prefix.', used='bash -x.',
         cmd="PS4='>> ' bash -xc 'x=2; echo $((x*3))' 2>&1"),
], hint='From the option letters to the trace. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>set -e stops the line, and pipefail</h2>
''' + two + s1 + dx + qc('Is <code>set -e</code> enough to make a script safe?', 'No: add -u and pipefail, handle expected failures with if/||, check important results explicitly, and test with bash -x.') + '''
</section>
'''

VAR = variations('Each option tried in small variations, so you know exactly when it fires and when it does not.', [
    ('set -e: fires or not?', [
        dict(title='Five commands, five results', cmd="for c in 'false' 'false || true' 'if false; then :; fi' '! false' 'false | true'; do\n  bash -c \"set -e; $c; echo survived\" > /dev/null && r=continues || r=STOPS\n  printf '%-24s %s\\n' \"$c\" \"$r\"\ndone", why='Only the plain false stops a script; conditions, || , ! and non-last pipe parts are exempt.'),
        dict(title='Command substitution', cmd="bash -c 'set -e; x=$(false); echo \"x set\"'; echo \"plain assignment: $?\"\nbash -c 'set -e; f(){ local y=$(false); echo \"local hides it\"; }; f'; echo \"local: $?\"", expect='any', why='x=$(false) stops; local y=$(false) does not (local itself succeeds): a famous trap.'),
        dict(title='Functions called in a condition', cmd="bash -c 'set -e; f(){ false; echo \"after false inside f\"; }; if f; then echo yes; fi'", why='Inside a function used as an if condition, set -e is switched off: the echo still runs.'),
    ]),
    ('set -u variations', [
        dict(title='Which forms are allowed', cmd="bash -uc 'echo \"[${A-}] [${A:-def}] [${#}]\"'\nbash -uc 'echo \"[$A]\"' 2>&1 | sed 's/.*: A/A/'", expect='any', why='${A-} and ${A:-def} are fine; plain $A is the error.'),
        dict(title='Empty is not unset', cmd="bash -uc 'A=\"\"; echo \"empty but set: [$A]\"'", why='set -u only complains about variables that were never set.'),
    ]),
    ('Tracing variations', [
        dict(title='Trace only one part', cmd="bash -c 'a=1\nset -x\nb=$((a+1))\nset +x\necho \"b=$b\"' 2>&1", why='set -x … set +x around the suspicious lines (set +x itself is also traced).'),
        dict(title='Trace into a separate file', cmd="bash -c 'exec 5> trace.txt; BASH_XTRACEFD=5; set -x; echo normal output'\necho '--- trace.txt:'; cat trace.txt", why='BASH_XTRACEFD sends the trace to another file descriptor; normal output stays clean.'),
        dict(title='Trace with time stamps', cmd="PS4='+ $(date +%S)s line $LINENO: ' bash -xc 'sleep 1\necho done' 2>&1 | sed -E 's/[0-9]{2}s/SSs/'", why='Anything in PS4 is expanded for each line: seconds, line numbers, function names.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Shell options at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['set -euo', 'pipefail'], 'green', 8.6), '1. CI/CD scripts',
              'Build and deploy scripts start in strict mode so a failed step fails the pipeline.', ['Step fails', '*exit ≠ 0', 'red build']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['bash -x', 'support'], 'amber', 8.6), '2. Troubleshooting',
    'Support engineers re-run a failing script with bash -x and attach the trace to the ticket.', ['Bug', '*bash -x', 'fix']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['set -u', 'backups'], 'blue', 8.6), '3. Backup and clean-up',
    'set -u stops scripts that would rm or write to an empty path.', ['Typo', '*unbound', 'safe']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['pipefail', 'ETL'], 'violet', 8.6), '4. Data pipelines',
    'With pipefail, a failed extract in extract | transform | load fails the whole job instead of loading nothing.', ['Extract', '*pipefail', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['set -C', 'reports'], 'red', 8.6), '5. Protecting outputs',
    'noclobber stops a report script from overwriting yesterday’s file by mistake.', ['Write', '*>|', 'keep']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Which options are on?', scenario='Quick check.', cmd="bash -euc 'echo \"$-\"'", explain='$-.'),
    dict(level='b', title='Syntax check all scripts', scenario='Before a release.', cmd="printf 'echo ok\\n' > a.sh; printf 'if x; then\\n' > b.sh\nfor f in *.sh; do bash -n \"$f\" 2>/dev/null && echo \"ok  $f\" || echo \"BAD $f\"; done", explain='bash -n.'),
    dict(level='i', title='Trace to a file', scenario='Keep output clean.', cmd="bash -x -c 'echo visible' 2> trace.log; cat trace.log", explain='Trace is stderr.'),
    dict(level='i', title='Which part of the pipe failed?', scenario='Debug a pipeline.', cmd="cat /nonexist 2>/dev/null | sort | wc -l > /dev/null; echo \"${PIPESTATUS[*]}\"", explain='PIPESTATUS.'),
    dict(level='a', title='Safe increment under -e', scenario='Counters.', cmd="bash -c 'set -e; n=0; ((++n)); ((++n)); echo \"n=$n\"'", explain='Pre-increment returns the new value.'),
], extra=build_up('hardening a script', 'Riya makes the broken deploy script strict and debuggable, step by step.', SO + '; ' + DEPLOY, [
    ("cd ~/so; bash deploy.sh; echo \"status $?\"", '1. As it was: carries on, status 0.'),
    ("cd ~/so; sed -i '1a set -euo pipefail' deploy.sh; sed -n 2p deploy.sh", '2. Strict mode on line 2.'),
    ("cd ~/so; bash deploy.sh; echo \"status $?\"", '3. Now it stops at the failure.'),
    ("cd ~/so; bash -x deploy.sh 2>&1 | grep '^+' | tail -2", '4. The trace shows the failing line.'),
], cumulative=True, expect='any')) + VAR + which('Choosing the right option.', [
    ('Stop on errors', 'set -e', 'No silent failures.', 'Relying on it alone.'),
    ('Catch typos in names', 'set -u', 'Unbound variable error.', 'Empty paths.'),
    ('Pipes', 'set -o pipefail', 'Middle failures count.', 'Assuming wc’s status.'),
    ('See what runs', 'bash -x', 'Real values.', 'echo everywhere.'),
    ('Syntax only', 'bash -n', 'Nothing runs.', 'Running to find a typo.'),
    ('Allow one failure', 'cmd || true', 'Explicit.', 'set +e for the whole script.'),
]) + keys('Handy forms.', [
    ('set -euo pipefail', 'strict mode', 'every script'),
    ('set +e', 'relax -e', 'block'),
    ("PS4='+ $LINENO: '", 'numbered trace', 'debug'),
    ('cmd || true', 'allowed failure', '-e'),
    ('${V:-}', 'optional under -u', '-u'),
    ('set -- a b', 'set $1 $2', 'testing'),
]) + scriptit('strict-template.sh', 'A starting template for every new script: strict mode, a numbered trace when DEBUG=1, required and optional settings, and a clear failure message.',
'''set -euo pipefail
[ "${DEBUG:-0}" = 1 ] && { PS4='+ line $LINENO: '; set -x; }
log=${LOG:-/var/log/syslog}
out=${OUT:?set OUT to an output file}
count=0
for f in "$log"; do [ -r "$f" ] && count=$((count + 1)); done
echo "readable logs: $count, writing summary to $out"''',
'<p>Run without OUT (it must refuse), the safe way to see the guard.</p>', expect='any') + puzzle_answer('Under <code>set -e</code>, <code>((count++))</code> with count=0 evaluates to the <b>old</b> value 0, and <code>(( ))</code> returns status 1 when its result is 0. set -e treats that as a failure and exits silently with status 1, right after the first file. Use <code>count=$((count + 1))</code> or <code>((++count))</code>.') + qc('How do you see the line number of each command in a trace?', "PS4='+ $LINENO: ' bash -x script.sh") + '''
</section>
'''

_sh.run_sh('rm -rf ~/so ~/vi', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../05-your-first-shell-script/">Lesson 12.5</a> (scripts and exit status).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
