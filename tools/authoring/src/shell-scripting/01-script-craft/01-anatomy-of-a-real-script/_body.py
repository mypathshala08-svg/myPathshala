import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# Riya's data and the script she grows in this lesson (all really run on our build machine)
SS = r"""rm -rf ~/ops; mkdir -p ~/ops/data ~/ops/bin; cd ~/ops
cat > data/orders.csv <<'EOF'
id,city,amount,status
1001,Pune,450,paid
1002,Mumbai,1200,paid
1003,Pune,300,failed
1004,Delhi,800,paid
1005,Mumbai,150,refunded
1006,Pune,999,paid
EOF
cat > bin/report-v1.sh <<'EOF'
cut -d, -f2 data/orders.csv | sort | uniq -c
EOF
cat > bin/report.sh <<'EOF'
#!/usr/bin/env bash
# report.sh - total paid orders per city from an orders CSV
# Usage: report.sh [-h] FILE
set -euo pipefail

readonly PROG=${0##*/}
readonly VERSION=1.0

usage() {
  cat <<USAGE
Usage: $PROG [-h] FILE
Print the total amount of paid orders per city.
  -h   show this help
USAGE
}

die() { echo "$PROG: error: $*" >&2; exit 1; }

report() {
  local file=$1
  awk -F, 'NR > 1 && $4 == "paid" { sum[$2] += $3 }
           END { for (c in sum) printf "%-8s %6d\n", c, sum[c] }' "$file" | sort
}

main() {
  [[ ${1:-} == -h ]] && { usage; exit 0; }
  [[ $# -eq 1 ]] || { usage >&2; exit 2; }
  [[ -r $1 ]] || die "cannot read '$1'"
  report "$1"
}

main "$@"
EOF
chmod +x bin/report.sh"""

HOOK = hook('In Linux Lesson 12.5 Riya wrote her first script: three commands in a file. At work her team lead returns it in review with a list: “no shebang, no error handling, no help text, breaks when the file name has a space, and nobody can tell what it does.” A <b>real</b> script, the kind that runs in cron jobs and CI pipelines for years, has a fixed anatomy: a shebang, a header comment, a safe-mode line, constants, small functions, a <code>main</code>, and a usage message. This lesson builds that anatomy piece by piece around one real script, and runs every version.',
    ['explain each part of a professional script: shebang, header, set -euo pipefail, readonly constants, functions, main "$@"',
     'write usage() and die() helpers and send errors to stderr with the right exit code',
     'quote variables and guard arguments so the script survives spaces, missing files and wrong input',
     'turn a three-line command file into a script a team can trust'])
ROAD = roadmap([
    ('story', 'The story', 3, 'code review'),
    ('decide', 'Checklist', 2, 'the eight parts'),
    ('definition', 'What makes it “real”', 5, 'simple meaning + 4 depths'),
    ('types', 'One-off vs real', 4, 'side by side'),
    ('commands', 'Part by part', 15, 'each part, really run'),
    ('animation', 'See it happen', 4, 'how Bash reads a script'),
    ('run', 'Run on your PC', 3, 'your own terminal'),
    ('lab', 'Practice lab', 8, 'upgrade a script'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Every real script has → why', [
    ('#!/usr/bin/env bash', 'the right interpreter on any system', 'line 1'),
    ('# header: what, usage', 'the next reader (often you)', 'lines 2–3'),
    ('set -euo pipefail', 'stop on errors, unset variables, failed pipes', 'safe mode'),
    ('readonly CONSTANTS', 'names and defaults in one place', 'config'),
    ('usage() and die()', 'help text and clean errors on stderr', 'messages'),
    ('small functions', 'one job each, local variables', 'logic'),
    ('main "$@"', 'one entry point, all arguments passed on', 'last line'),
    ('"$quoted" variables', 'spaces and empty values survive', 'everywhere'),
])

cmap = concept_map(
    [('L:12.5', 'Your first script', 'shebang, chmod +x'), ('L:12.6', 'set -e -u -x', 'safe options'), ('L:12.10', 'Functions', 'local, return')],
    ['the eight parts of a real script', 'set -euo pipefail', 'readonly constants', 'usage() and die()', 'main "$@" pattern', 'quoting and argument guards', 'exit codes 0, 1, 2'],
    [('1.2', 'getopts', 'real options'), ('1.3', 'Exit codes and logging', 'messages'), ('1.4', 'Template + ShellCheck', 'reuse it'), ('3.1', 'Error handling', 'deeper')],
    'From “commands in a file” to a script a team can run, read and maintain.')

sc = (term(20, 14, 316, 156, ['$ ./report.sh', ('Usage: report.sh [-h] FILE', 'err'), '$ ./report.sh nosuch.csv', ("report.sh: error: cannot read 'nosuch.csv'", 'err'), '$ ./report.sh data/orders.csv', ('Delhi       800', 'out'), ('Mumbai     1200', 'out'), ('Pune       1449', 'acc')], title='riya@laptop: ~/ops', prompt='$', size=6.6, step=17)
      + t(352, 36, 'A real script:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['explains itself', 'fails loudly', 'never half-runs', 'survives spaces', 'one main()'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“Works on my machine” is not a review comment</h2>
  <div class="story">
''' + puzzle('Riya’s first version is one line, <code>cut -d, -f2 data/orders.csv | sort | uniq -c</code>, saved as <code>report-v1.sh</code>. It “works”. But run from another folder it prints “No such file or directory” and still <b>exits 0</b>, so the cron job reports success. Also, with <code>sh report-v1.sh</code> on the server, a later version using <code>[[ ]]</code> fails with “[[: not found”. Why exit 0 after an error, and why does the shell matter?') + '''
    <p class="narration">In Riya’s <code>~/ops</code> folder (every run in this lesson is real).</p>
''' + scene('A terminal: report.sh with no argument prints usage, with a missing file prints a clear error, and with the CSV prints paid totals per city.', sc,
            'Same job, but it <tspan font-weight="700" class="s-acc">explains, checks and fails loudly</tspan>.') + '''
K> It is only one line. Why does it need all that?
A> Because scripts outlive the moment you wrote them. Someone runs it with no argument, from the wrong folder, with <code>sh</code> instead of <code>bash</code>, from cron at 2 a.m. A real script tells them what went wrong, stops at the first error, and returns an exit code other programs can check.
R> So there is a standard shape?
A> Eight parts, always in the same order. Once you know them you can read any team’s scripts, and your own scripts look professional from the first line.
  </div>
</section>
'''

parts = [('1', '#!/usr/bin/env bash', 'blue'), ('2', '# what it does, usage', 'card'), ('3', 'set -euo pipefail', 'red'), ('4', 'readonly PROG VERSION', 'amber'),
         ('5', 'usage() die()', 'violet'), ('6', 'report() – the work', 'green'), ('7', 'main() – checks', 'green'), ('8', 'main "$@"', 'blue')]
pic = ('<div class="scene"><svg viewBox="0 0 640 230" role="img" aria-label="The eight parts of a real Bash script from top to bottom: shebang, header comment, safe mode, constants, helper functions, work function, main function and the call main with all arguments.">'
       + ''.join(label_box(20 + (i % 2) * 310, 14 + (i // 2) * 50, 290, 40, [f'{n}. {a}'], c, 9) for i, (n, a, c) in enumerate(parts))
       + '<text x="632" y="224" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('A real script at four depths', [
    ('v', 'No jargon: a recipe card', '      <p>A recipe says what it makes, what you need, what to do if an ingredient is missing, and the steps. A real script is the same, top to bottom.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li>Line 1: <code>#!/usr/bin/env bash</code>.</li>
        <li>Line 4: <code>set -euo pipefail</code>.</li>
        <li>Functions for each job, then <code>main "$@"</code> on the last line.</li>
        <li>Always <code>"$var"</code> in double quotes.</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li><code>-e</code>: stop when a command fails; <code>-u</code>: an unset variable is an error; <code>-o pipefail</code>: a pipeline fails if <i>any</i> part fails, not just the last.</li>
        <li>Errors go to <b>stderr</b> (<code>&gt;&amp;2</code>) so they do not mix with the script’s real output in pipes and files.</li>
        <li>Exit codes: 0 success, 1 general error, 2 wrong usage (the convention of most Unix tools).</li>
        <li><code>main "$@"</code> at the end means Bash has read every function before anything runs.</li>
      </ul>'''),
    ('a', 'Behind the screen: how Bash reads a script', '''      <ul>
        <li>The kernel reads <code>#!</code> on <code>execve()</code> and starts <code>/usr/bin/env bash report.sh ARGS</code>; env finds bash on the PATH (it lives in /bin, /usr/bin or /usr/local/bin depending on the system).</li>
        <li>Bash reads and runs the file <b>command by command</b>; a function definition is just a command that stores the body. Calling <code>main</code> last guarantees all are defined, and protects against a half-downloaded script running its first half.</li>
        <li><code>set -e</code> has exceptions: commands in <code>if</code>, <code>while</code>, <code>&amp;&amp;</code>/<code>||</code> lists and <code>!</code> do not trigger it. Module 3 covers them.</li>
        <li><code>${0##*/}</code> is the script’s name without its path, so messages say <code>report.sh:</code> however it was called.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What makes a script “real”</h2>
''' + def_block(
    'A <b>shell script</b> is a text file of shell commands run by an interpreter such as Bash. A <b>production-quality</b> (real) script additionally declares its interpreter (shebang), documents itself, runs in a safe mode that stops on errors, validates its input, reports problems on standard error with a non-zero exit code, and organises its work into functions called from one entry point.',
    'Commands in a file, plus checks, messages and structure.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Shebang', '#! line naming the interpreter.'),
    ('Safe mode', 'set -euo pipefail.'),
    ('stderr', 'Stream 2, for messages.'),
    ('Exit code', '0 = success, else failure.'),
    ('usage()', 'Prints how to call the script.'),
    ('die()', 'Prints an error and exits.'),
    ('main "$@"', 'Single entry point.'),
    ('readonly', 'A variable that cannot change.'),
]) + '\n' + names('Where the names come from.', [
    ('#!', '“hash-bang”, “she-bang”', 'Unix V8, 1980.'),
    ('bash', 'Bourne-Again SHell', 'Brian Fox, 1989.'),
    ('env', 'environment', 'Runs a program found on PATH.'),
    ('$@', 'all arguments, separately', '“at” = all.'),
    ('$0', 'argument zero: the script', 'C’s argv[0].'),
    ('die', 'Perl’s die()', 'Shell scripters borrowed it.'),
    ('pipefail', 'pipe + fail', 'Bash 3, 2004.'),
    ('main', 'C’s main()', 'Entry point.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Interpreter', '<code>#!/usr/bin/env bash</code>'),
    ('Safe mode', '<code>set -euo pipefail</code>'),
    ('Error message', '<code>echo "msg" &gt;&amp;2</code>'),
    ('Script name', '<code>${0##*/}</code>'),
    ('Entry point', '<code>main "$@"</code>'),
    ('Usage error', '<code>exit 2</code>'),
]) + '\n' + lv + didyou('Google’s Shell Style Guide asks for exactly this shape (header, functions, <code>main "$@"</code> at the bottom) and says that a script over 100 lines should probably be rewritten in another language. Shell is for gluing commands together, and does that brilliantly.') + '''
EXAM> “What does set -euo pipefail do?” → -e exits on a failing command, -u treats unset variables as errors, -o pipefail makes a pipeline’s status the last non-zero status of any command in it.
''' + qc('Why does main "$@" go on the last line?', 'So every function is defined before anything runs, and a partly downloaded script does nothing.') + mistake('echo "error: file missing"; exit 0',
    'echo "error: file missing" >&2; exit 1',
    'Exit 0 tells cron, CI and other scripts that everything worked; the message also pollutes the real output.') + mistake('for f in $files; do rm $f; done',
    'for f in "${files[@]}"; do rm -- "$f"; done',
    'Unquoted, a name like “my report.csv” becomes two words: rm deletes the wrong things or fails.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>One-off commands vs a real script</h2>
''' + table(['Question', 'report-v1.sh (one line)', 'report.sh (real)'], [
    ['Which shell?', 'whatever runs it', '<code>#!/usr/bin/env bash</code>'],
    ['What does it do?', 'read the code', 'header + <code>-h</code>'],
    ['No argument', 'uses a hard-coded path', 'usage, exit 2'],
    ['Missing file', 'error, but <b>exit 0</b>', 'clear error, exit 1'],
    ['A failing command', 'next line runs anyway', 'stops (<code>-e</code>)'],
    ['Typo in a variable', 'empty string', 'error (<code>-u</code>)'],
    ['Spaces in names', 'breaks', 'quoted, works'],
    ['Run from another folder', 'breaks', 'takes a path argument'],
], minw=560) + table(['Exit code', 'Meaning', 'Example'], [
    ['0', 'success', 'report printed'],
    ['1', 'general error', 'cannot read the file'],
    ['2', 'wrong usage', 'no argument'],
    ['126', 'found but not executable', 'missing chmod +x'],
    ['127', 'command not found', 'typo, wrong PATH'],
    ['128+N', 'killed by signal N', '130 = Ctrl+C'],
], minw=420) + qc('Which exit code should a script use when called with the wrong arguments?', '2, by convention (usage error).') + '''
</section>
'''

V1 = SS
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>The script, part by part</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops</code>: <code>data/orders.csv</code> (six orders), Riya’s one-line <code>bin/report-v1.sh</code> and the finished <code>bin/report.sh</code>. Each card adds one part and shows what changes.</p>
''' + cmdcard_u(['every script'], ['#!/bin/sh with bash features'])(
    'shebang', '#!/usr/bin/env bash · bash vs sh', 'part 1: the shebang',
    'The first line tells the kernel which interpreter runs the file. <code>#!/usr/bin/env bash</code> finds bash wherever it is installed. Without it, the file runs in whatever shell starts it, and <code>sh</code> on Debian/Ubuntu is <b>dash</b>, which has no <code>[[ ]]</code>, arrays or <code>${var,,}</code>.',
    '#!/usr/bin/env bash   (or #!/bin/bash)', 'safe',
    [('#!/usr/bin/env bash', 'bash from PATH', 'portable'),
     ('#!/bin/bash', 'fixed path', 'Linux only'),
     ('#!/bin/sh', 'POSIX sh (dash)', 'only POSIX code'),
     ('bash script.sh', 'ignores shebang', 'testing'),
     ('./script.sh', 'uses shebang', 'normal'),
     ('readlink -f /bin/sh', 'what sh really is', 'check')],
    dict(setup=SS, cmd="readlink -f /bin/sh\nprintf '[[ 1 -eq 1 ]] && echo bash-ok\\n' > ~/t.sh\nbash ~/t.sh\nsh ~/t.sh; echo \"sh exit: $?\"", note='The puzzle: under sh (dash) [[ is just an unknown command.', expect='any'),
    [('devops', [
        dict(situation='Which interpreter will a file use?', setup=SS, cmd="cd ~/ops; head -1 bin/report.sh; head -1 bin/report-v1.sh | grep -q '^#!' || echo 'report-v1.sh: no shebang (runs in the caller’s shell)'", why='Check scripts in reviews.')]),
    ],
    anat=anatomy([('#!', 'cmd', 'magic bytes'), ('/usr/bin/env', 'opt', 'finder'), ('bash', 'arg', 'interpreter')], 'Must be the very first line, no spaces before #!.')
) + cmdcard_u(['scripts that others run, cron, CI'], ['interactive shells (it would close them)'])(
    'safe', 'set -euo pipefail', 'part 3: safe mode',
    '<code>set -e</code> stops at the first failing command; <code>set -u</code> stops on an unset variable; <code>set -o pipefail</code> makes a pipeline fail when any part fails. Together they stop a script from carrying on after something went wrong.',
    'set -euo pipefail', 'safe',
    [('-e / errexit', 'stop on failure', 'core'),
     ('-u / nounset', 'unset = error', 'typos'),
     ('-o pipefail', 'pipe status', 'pipelines'),
     ('${var:-default}', 'allowed under -u', 'optional vars'),
     ('cmd || true', 'allow a failure', 'deliberate'),
     ('set +e', 'turn off', 'rarely')],
    dict(setup=SS, cmd="cd ~/ops\nbash bin/report-v1.sh > /dev/null; echo \"v1 from ~/ops: exit $?\"\ncd /tmp; bash ~/ops/bin/report-v1.sh; echo \"v1 from /tmp: exit $?\"\nbash -c 'set -o pipefail; cut -d, -f2 data/orders.csv | sort | uniq -c'; echo \"with pipefail: exit $?\"", note='The puzzle: without pipefail the pipeline’s status is uniq’s (0), so the error is hidden.', expect='any'),
    [('dev', [
        dict(situation='-u catches a typo in a variable name.', cmd="bash -c 'out_dir=/tmp/x; echo \"cleaning $outdir/*\"'; bash -c 'set -u; out_dir=/tmp/x; echo \"cleaning $outdir/*\"'; echo \"exit $?\"", why='Without -u, rm -rf \"$outdir/\"* would mean rm -rf /*.', expect='any')]),
    ]
) + cmdcard_u(['any message that is not the result'], ['printing errors on stdout'])(
    'helpers', 'usage() · die() · >&2 · exit 1/2', 'part 5: usage and die',
    '<code>usage</code> prints how to call the script (to stdout for <code>-h</code>, to stderr when called wrongly). <code>die</code> prints “prog: error: …” to stderr and exits 1. <code>${0##*/}</code> gives the script’s own name.',
    'die() { echo "$PROG: error: $*" >&2; exit 1; }', 'safe',
    [('>&2', 'to stderr', 'messages'),
     ('$*', 'all args as one string', 'message text'),
     ('exit 1', 'failure', 'errors'),
     ('exit 2', 'usage', 'wrong args'),
     ('cat <<EOF', 'multi-line help', 'usage'),
     ('${0##*/}', 'script name', 'messages')],
    dict(setup=SS, cmd="cd ~/ops\nbin/report.sh -h\nbin/report.sh; echo \"no argument: exit $?\"\nbin/report.sh nosuch.csv; echo \"missing file: exit $?\"", note='Help to stdout (exit 0); wrong usage and errors to stderr (2 and 1).', expect='any'),
    [('sys', [
        dict(situation='Errors stay out of the output file.', setup=SS, cmd="cd ~/ops; bin/report.sh nosuch.csv > out.txt 2> err.txt; echo \"out.txt: $(wc -c < out.txt) bytes\"; echo \"err.txt: $(cat err.txt)\"", why='stdout and stderr are separate streams.', expect='any')]),
    ]
) + cmdcard_u(['all logic'], ['code at top level between functions'])(
    'main', 'functions · local · main "$@"', 'parts 6–8: functions and main',
    'Each job is a small function with <code>local</code> variables; <code>main</code> checks the arguments and calls them; the last line, <code>main "$@"</code>, passes every argument on unchanged. <code>"$@"</code> keeps arguments with spaces intact; <code>$*</code> would glue them together.',
    'main() { …; }   main "$@"', 'safe',
    [('local var', 'function-only', 'no leaks'),
     ('"$@"', 'all args, separately', 'pass on'),
     ('$#', 'how many', 'checks'),
     ('[[ -r $f ]]', 'readable?', 'guard'),
     ('${1:-}', 'empty if missing', 'with -u'),
     ('return N', 'function status', 'helpers')],
    dict(setup=SS, cmd="cd ~/ops\nbin/report.sh data/orders.csv\ncp data/orders.csv 'data/orders nov.csv'\nbin/report.sh 'data/orders nov.csv' | tail -1", note='Paid totals per city; the quoted name with a space works too.'),
    [('dev', [
        dict(situation='"$@" vs $* with a spaced argument.', cmd="show(){ printf '[%s] ' \"$@\"; echo; }\nf1(){ show \"$@\"; }; f2(){ show $*; }\nf1 'orders nov.csv' x; f2 'orders nov.csv' x", why='Only "$@" keeps the two arguments as two.')]),
    ]
) + undo('A script that went wrong usually only printed or stopped; fix and rerun. Prevent the dangerous cases:', [
    ('Deleted the wrong files:', 'quote every variable, and use <code>rm -- "$f"</code>; test with <code>echo</code> first.'),
    ('Ran under sh:', 'run <code>bash script.sh</code> or <code>./script.sh</code> with the shebang.'),
    ('Half-finished run:', '<code>set -e</code> stops it; make steps safe to repeat (Module 3).'),
    ('Wrong output file overwritten:', '<code>set -o noclobber</code> makes <code>&gt;</code> refuse to overwrite.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(setup=SS, cmd="cd ~/ops && printf 'echo hi\\n' > bin/x.sh && ./bin/x.sh", meaning='Permission denied: the file is not executable (exit 126).', fix='chmod +x bin/x.sh'),
    dict(setup=SS, cmd="cd ~/ops && printf '#!/usr/bin/env bash\\r\\necho hi\\r\\n' > bin/w.sh && chmod +x bin/w.sh && ./bin/w.sh", meaning='Windows line endings: the shebang asks for “bash\\r”.', fix='sed -i \'s/\\r$//\' bin/w.sh (or dos2unix).'),
    dict(setup=SS, cmd="cd ~/ops && bash -c 'set -u; echo \"$1\"'", meaning='-u: $1 is unset because no argument was given.', fix='Check $# first, or use ${1:-}.'),
    dict(setup=SS, cmd="cd ~/ops && report.sh data/orders.csv", meaning='Not on the PATH: the shell does not look in the current folder.', fix='./bin/report.sh, or put bin on PATH.'),
]) + qc('Your script prints an error but cron reports success. What is missing?', 'A non-zero exit (die / exit 1), and set -e / pipefail so failures stop it.') + '''
'''
cards = cards + '</section>\n'

RS = [('read line', 'Bash reads one command', 'blue'), ('function def', 'stored, not run', 'amber'), ('main "$@"', 'now everything runs', 'green'), ('exit code', 'last status to the caller', 'violet')]
def rstep(k):
    return ''.join(label_box(14, 12 + i * 40, 330, 32, [f'{a}: {b}'], c if i <= k else 'card', 8.2) for i, (a, b, c) in enumerate(RS))
see_cmds = [['$ ./report.sh data/orders.csv', ('kernel: #! → bash', 'out')], ['bash: usage() { … }', ('(defined, nothing printed)', 'out')], ['bash: main data/orders.csv', ('Pune 1449', 'out')], ['$ echo $?', ('0', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@laptop: ~/ops', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Start.', 'Define.', 'Run.', 'Exit.'])]
two = anim_two('How Bash runs your script', 'Behind the screen: read, define, run, exit',
               'A terminal runs report.sh: the kernel starts bash, bash defines the functions, main runs, the exit code returns.',
               'Four stacked boxes: read, define, main, exit code.', see, [rstep(k) for k in range(4)],
               ['read.', 'define.', 'run.', 'exit.'], ['read', 'define', 'run', 'exit'])

def pf(k):
    o = t(180, 18, 'cut … | sort | uniq -c', 9.6, 'ink2', bold=True)
    st = [('cut', 'exit 1', 'red'), ('sort', 'exit 0', 'green'), ('uniq', 'exit 0', 'green')]
    for i, (a, b, c) in enumerate(st):
        o += label_box(14 + i * 115, 36, 105, 46, [a, b], c, 8.4)
    o += t(180, 112, ['each command has its own exit status', 'without pipefail: status = last = 0', 'with pipefail: status = 1', 'so set -e can stop the script'][k], 9, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Why pipefail matters',
              'A failing first command hides behind a successful last one.', 'pipeline status', 'Three boxes: cut failed, sort and uniq succeeded.', [pf(k) for k in range(4)],
              ['statuses.', 'default.', 'pipefail.', 'stop.'], hid='scenario-pipefail')

dx = dissect('Layer by layer: what runs when you type ./report.sh',
    'Each layer has a real command from our build machine.', [
    dict(key='file', name='The file', sub='text + x bit', why='Must be executable.', how='chmod +x.', impl='Mode bits.', used='ls -l.',
         setup=SS, cmd="cd ~/ops; ls -l bin/report.sh | cut -c1-10; head -c 2 bin/report.sh | od -An -c"),
    dict(key='interp', name='Interpreter', sub='env → bash', why='Who reads it.', how='#! line.', impl='execve.', used='which.',
         cmd="command -v env bash; bash --version | head -1"),
    dict(key='status', name='Exit status', sub='$?', why='Callers decide.', how='Last command or exit N.', impl='0–255.', used='&& || if.',
         setup=SS, cmd="cd ~/ops; bin/report.sh data/orders.csv > /dev/null && echo 'ok -> next step runs'; bin/report.sh x 2>/dev/null || echo \"failed ($?) -> alert\""),
], hint='File → interpreter → status. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How Bash reads a script, and pipefail</h2>
''' + two + s1 + dx + qc('A pipeline’s first command fails, the last succeeds. What is $? without pipefail?', '0: the status of the last command.') + '''
</section>
'''

VAR = variations('Sixteen more small checks and patterns from real scripts. All were really run on our build machine.', [
    ('Shebang and running', [
        dict(title='Run with an explicit shell', setup=SS, cmd="cd ~/ops; bash bin/report.sh data/orders.csv | head -1", why='Works without +x.'),
        dict(title='Syntax check without running', setup=SS, cmd="cd ~/ops; bash -n bin/report.sh && echo 'syntax OK'", why='-n parses only.'),
        dict(title='A syntax error found by -n', cmd="printf 'if true; then\\n echo x\\n' > /tmp/bad.sh; bash -n /tmp/bad.sh; echo \"exit $?\"", why='Missing fi.', expect='any'),
        dict(title='Script name in messages', setup=SS, cmd="cd ~/ops; bash -c 'echo \"${0##*/}\"' /long/path/to/deploy.sh", why='${0##*/} drops the path.'),
    ]),
    ('Safe mode in action', [
        dict(title='-e stops at the failure', cmd="bash -c 'set -e; echo step1; false; echo step2'; echo \"exit $?\"", why='step2 never runs.', expect='any'),
        dict(title='Allowing one failure on purpose', cmd="bash -c 'set -e; grep -q nothing /etc/hostname || true; echo continued'", why='|| true marks it intentional.'),
        dict(title='-u with a default', cmd="bash -c 'set -u; echo \"level=${LOG_LEVEL:-info}\"'", why='${var:-default} is safe under -u.'),
        dict(title='pipefail status', cmd="bash -c 'false | true; echo \"default: $?\"; set -o pipefail; false | true; echo \"pipefail: $?\"'", why='1 only with pipefail.'),
    ]),
    ('Arguments and quoting', [
        dict(title='Count arguments', cmd="bash -c 'echo \"$# arguments\"' prog a 'b c' d", why='"b c" is one argument.'),
        dict(title='Loop over arguments safely', cmd="bash -c 'for a in \"$@\"; do echo \"<$a>\"; done' prog 'my file.csv' other.csv", why='Always "$@".'),
        dict(title='Guard: exactly one argument', cmd="bash -c '[[ $# -eq 1 ]] || { echo \"usage: prog FILE\" >&2; exit 2; }; echo ok' prog a b; echo \"exit $?\"", why='Exit 2 for usage.', expect='any'),
        dict(title='Guard: file readable', setup=SS, cmd="cd ~/ops; for f in data/orders.csv nosuch.csv; do [[ -r $f ]] && echo \"$f: readable\" || echo \"$f: missing\"; done", why='-r test.'),
    ]),
    ('Messages and exit codes', [
        dict(title='Exit code of a missing command', cmd="bash -c 'nosuchcmd' 2>/dev/null; echo \"exit $?\"", why='127.', expect='any'),
        dict(title='die() in two lines', cmd="die(){ echo \"demo: error: $*\" >&2; return 1; }; die 'disk full on /data'; echo \"status $?\"", why='return in a demo; exit in scripts.', expect='any'),
        dict(title='Only errors, no output', setup=SS, cmd="cd ~/ops; bin/report.sh nosuch.csv 2>&1 >/dev/null", why='Order matters: 2>&1 first, then stdout to null.', expect='any'),
        dict(title='Version constant', setup=SS, cmd="cd ~/ops; grep -E '^readonly' bin/report.sh", why='Constants at the top.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where script anatomy matters</h2>
''' + usecase(label_box(14, 22, 92, 46, ['cron', '2 a.m.'], 'blue', 8.6), '1. Scheduled jobs',
              'cron and systemd timers judge a job only by its exit code; a script that exits 0 after an error fails silently for weeks.', ['cron', '*exit code', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['CI', 'pipelines'], 'green', 8.6), '2. CI/CD steps',
    'GitHub Actions and Jenkins run steps as bash scripts, often with -e; a failing command must stop the deploy.', ['step', '*set -e', 'stop deploy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ops', 'runbooks'], 'amber', 8.6), '3. Team runbooks',
    'On-call engineers run scripts they did not write; -h and clear errors save minutes in an outage.', ['-h', '*usage', 'right call']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['data', 'ETL'], 'violet', 8.6), '4. Data pipelines',
    'Bash wrappers start Spark, Hive and sqoop jobs; pipefail catches a failed extract before a load step loads nothing.', ['extract', '*pipefail', 'load']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['install', 'curl | bash'], 'red', 8.6), '5. Installers',
    'Installer scripts wrap everything in main and call it last, so a half-downloaded script does nothing.', ['download', '*main last', 'safe']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful checks for any script. All really run on our build machine.', [
    dict(level='b', title='Has a shebang?', scenario='Review.', setup=SS, cmd="cd ~/ops; for f in bin/*.sh; do head -1 \"$f\" | grep -q '^#!' && echo \"$f: yes\" || echo \"$f: no\"; done", explain='First line.'),
    dict(level='b', title='Executable?', scenario='126 errors.', setup=SS, cmd="cd ~/ops; for f in bin/*.sh; do [[ -x $f ]] && echo \"$f: x\" || echo \"$f: not executable\"; done", explain='-x test.'),
    dict(level='i', title='Uses safe mode?', scenario='Review.', setup=SS, cmd="cd ~/ops; grep -L 'set -euo pipefail' bin/*.sh", explain='-L lists files without a match.', expect='any'),
    dict(level='i', title='Syntax-check all', scenario='Before commit.', setup=SS, cmd="cd ~/ops; for f in bin/*.sh; do bash -n \"$f\" && echo \"$f ok\"; done", explain='bash -n.'),
    dict(level='a', title='Exit code report', scenario='Monitoring.', setup=SS, cmd="cd ~/ops; for a in -h '' data/orders.csv nosuch; do bin/report.sh $a > /dev/null 2>&1; echo \"report.sh '$a' -> $?\"; done", explain='0, 2, 0, 1.', expect='any'),
], extra=build_up('report-v1.sh into a real script', 'Riya upgrades her one-liner, one part at a time.', SS, [
    ("cd ~/ops; printf '#!/usr/bin/env bash\\nset -euo pipefail\\n' > bin/r.sh; chmod +x bin/r.sh; head -2 bin/r.sh", '1. Shebang and safe mode.'),
    ("cd ~/ops; printf 'die() { echo \"r.sh: error: $*\" >&2; exit 1; }\\n' >> bin/r.sh; grep -c '()' bin/r.sh | sed 's/^/functions: /'", '2. A die helper.'),
    ("cd ~/ops; printf 'main() {\\n  [[ $# -eq 1 ]] || { echo \"usage: r.sh FILE\" >&2; exit 2; }\\n  [[ -r $1 ]] || die \"cannot read $1\"\\n  cut -d, -f2 \"$1\" | tail -n +2 | sort | uniq -c\\n}\\nmain \"$@\"\\n' >> bin/r.sh; bin/r.sh data/orders.csv", '3. main with guards.'),
    ("cd ~/ops; bin/r.sh; echo \"exit $?\"; bin/r.sh nope.csv; echo \"exit $?\"", '4. Test the failures.'),
], cumulative=True, expect='any')) + VAR + which('Choosing the right form.', [
    ('Interpreter', '#!/usr/bin/env bash', 'Finds bash.', 'No shebang.'),
    ('Error output', 'echo … >&2', 'Separate stream.', 'stdout.'),
    ('Usage error', 'exit 2', 'Convention.', 'exit 0.'),
    ('All arguments', '"$@"', 'Keeps words.', '$* / $@ unquoted.'),
    ('Optional variable', '${VAR:-default}', 'Safe with -u.', 'Bare $VAR.'),
    ('Allowed failure', 'cmd || true', 'Explicit.', 'set +e.'),
]) + keys('Handy forms.', [
    ('#!/usr/bin/env bash', 'line 1', 'always'),
    ('set -euo pipefail', 'safe mode', 'line 2–4'),
    ('readonly PROG=${0##*/}', 'own name', 'messages'),
    ('die() { echo "$PROG: error: $*" >&2; exit 1; }', 'errors', 'helper'),
    ('[[ $# -eq 1 ]] || { usage >&2; exit 2; }', 'guard', 'main'),
    ('main "$@"', 'last line', 'entry'),
]) + scriptit('skeleton.sh', 'The eight-part skeleton, ready to copy: every new script in this course starts from it.',
'''#!/usr/bin/env bash
# skeleton.sh - one line saying what the script does
# Usage: skeleton.sh [-h] NAME
set -euo pipefail

readonly PROG=${0##*/}

usage() { echo "Usage: $PROG [-h] NAME"; }
die()   { echo "$PROG: error: $*" >&2; exit 1; }

greet() {
  local name=$1
  echo "Hello, $name"
}

main() {
  [[ ${1:-} == -h ]] && { usage; exit 0; }
  [[ $# -eq 1 ]] || { usage >&2; exit 2; }
  greet "$1"
}

main "$@"''',
'<p>Replace greet with your work; keep the rest.</p>', expect='any') + puzzle_answer('<b>1.</b> A script’s exit code is the status of its <b>last</b> command. In <code>cut … | sort | uniq -c</code> that is <code>uniq</code>, which succeeds on empty input, so the failed <code>cut</code> is hidden and the script exits 0. <code>set -o pipefail</code> (plus <code>-e</code>) makes the pipeline, and the script, fail. <b>2.</b> <code>sh</code> on Debian and Ubuntu is <b>dash</b>, a small POSIX shell without Bash features like <code>[[ ]]</code>; the shebang <code>#!/usr/bin/env bash</code> plus running <code>./script.sh</code> (not <code>sh script.sh</code>) guarantees Bash.') + qc('Name the eight parts in order.', 'Shebang, header, safe mode, constants, usage/die, work functions, main, main "$@".') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../../linux/12-shell-environment/05-your-first-shell-script/">Linux Lesson 12.5</a> (your first script) and <a href="../../../linux/12-shell-environment/06-shell-options-set-e-u-x-and-unset/">12.6</a> (set -e -u -x).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
