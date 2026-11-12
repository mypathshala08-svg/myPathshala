import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='06-shell-options-set-e-u-x-and-unset', n='12.6',
    module_label='Module 12 · The shell environment and shell programming',
    title='Shell options for safer scripts: set -e, set -u, set -x, set -o vi and unset',
    desc='set -e (errexit) and its exceptions (if, &&, ||, !, pipes), the ((count++)) trap; set -u (nounset) with ${VAR:-default} and ${VAR:?}; set -o pipefail and PIPESTATUS; set -x / bash -x and PS4 line numbers; bash -n; set -o, set +o, $-, SHELLOPTS; noclobber and >|; set -o vi shown on real screens; set --; unset and unset -f; strict mode template; animations.',
    og_desc='Make Bash scripts safe and debuggable: set -euo pipefail, set -x, bash -n, noclobber, set -o vi and unset, with real outputs.',
    minutes=35, level='Beginner → Advanced',
    lead='Bash is forgiving by default: scripts continue after errors, unknown variables are empty and pipes hide failures. This lesson switches on strict mode, shows each option’s traps, and debugs scripts with set -x.',
    chips=['set -e stops the line', 'pipefail animated', 'The ((x++)) trap', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Default vs strict
printf 'echo start\\nfalse\\necho "after false"\\n' > lax.sh
bash lax.sh; echo "lax status: $?"
printf 'set -e\\necho start\\nfalse\\necho "after false"\\n' > strict.sh
bash strict.sh; echo "strict status: $?"
bash -x strict.sh 2>&1 | head -3
"""

RUN = dict(
    heading='Default vs set -e, and a trace',
    intro='<p>Run the same three lines without and with set -e, then trace the strict one.</p>',
    code=MAIN,
    anno=[('bash -x strict.sh', 'Each command printed with + before it runs.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which script printed “after false”?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does each echo print? Then run.',
             code="false | true; echo \"default $?\"\nset -o pipefail\nfalse | true; echo \"pipefail $?\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the counter should reach 2 under set -e. Fix the increment.',
             code="bash -c 'set -e; n=0; ((n++)); ((n++)); echo \"n=$n\"'; echo \"status $?\"\n"),
        dict(label='4 · Your turn', hint='Give MODE a default so set -u does not stop the script.',
             code="bash -c 'set -u; echo \"mode=${MODE:-dev}\"'\n"),
        dict(label='5 · Challenge', hint='Protect a file from > with noclobber, then force it.',
             code="set -o noclobber\necho one > k.txt\necho two > k.txt 2>/dev/null || echo 'refused'\necho three >| k.txt; cat k.txt\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: options in your terminal',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Options of your terminal', cmd='echo $-', output='himBHs', note='Typical interactive bash: h hash, i interactive, m job control, B braces, H history, s stdin.'),
        dict(title='2 · Try vi keys', cmd='set -o vi    # Esc, then b w dw 0 $ … ; set -o emacs to go back', output='', note='Typical: no output; the keys change.'),
        dict(title='3 · Lint for safety', cmd='shellcheck deploy.sh', output='In deploy.sh line 3:\ncd /srv/app\n^---------^ SC2164 (warning): Use \'cd ... || exit\' in case cd fails.', note='Typical (sudo apt install shellcheck).'),
        dict(title='4 · bash version (pipefail needs ≥ 3)', cmd='bash --version | head -1', output=pc('bash --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A pipeline’s statuses',
    intro='<p>Step through: one pipeline, its overall status, and each part’s status.</p>',
    code='''printf 'b\\na\\n' > in.txt
sort in.txt | grep z | wc -l
s=$?
set -o pipefail
sort in.txt | grep z | wc -l
p=$?
echo "default $s, pipefail $p"
''',
    notes={2: 'grep finds nothing (1), wc prints 0.', 3: 'Default :: wc’s 0.', 4: 'Switch on.', 6: 'pipefail :: grep’s 1.', 7: 'Summary.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a strict backup, a debug trace and an expected failure.'
EXAMPLES = [
    dict(level='b', tag='Admin', title='A backup that refuses an empty target',
         problem='<p>Copy a file to BACKUP_DIR, but stop with a clear message if BACKUP_DIR is not set.</p>',
         inp='a file', approach=['set -u.', '${VAR:?}.'],
         code='''echo data > app.conf
cat > backup.sh <<'EOF'
set -euo pipefail
dest=${BACKUP_DIR:?set BACKUP_DIR first}
mkdir -p "$dest"; cp app.conf "$dest/"; echo "backed up to $dest"
EOF
bash backup.sh 2>&1 | sed 's/.*: BACKUP_DIR/BACKUP_DIR/'
BACKUP_DIR=bk bash backup.sh
''', notes={7: 'Refused.', 8: 'Works.'}, tryit='Remove the :? and run without BACKUP_DIR under set -u.'),
    dict(level='i', tag='Developer', title='Find the bad line with a numbered trace',
         problem='<p>A script prints a wrong total. Trace it with line numbers.</p>',
         inp='a script', approach=['PS4 with $LINENO.', 'bash -x.'],
         code='''printf 'a=5\\nb=7\\ntotal=$((a+a))\\necho "total $total"\\n' > sum.sh
PS4='+ line $LINENO: ' bash -x sum.sh 2>&1 | grep 'line 3'
''', notes={2: 'Line 3 adds a twice.'}, tryit='Fix line 3 and trace again.'),
    dict(level='a', tag='DevOps', title='Allowed failures in strict mode',
         problem='<p>Under set -euo pipefail, count error lines, where finding none is fine.</p>',
         inp='a log', approach=['grep -c … || true.'],
         code='''printf 'ok\\nok\\n' > app.log
bash -c 'set -euo pipefail
n=$(grep -c ERROR app.log || true)
echo "errors: $n"'
''', notes={2: 'grep -c prints 0 and exits 1; || true allows it.'}, tryit='Remove || true.'),
]

QUIZ = mix([
    dict(q='set -e makes a script…', options=['run faster', 'exit at the first failing command', 'print each line', 'ignore errors'], answer=1, why='errexit.'),
    dict(q='set -u stops when…', options=['a command fails', 'an unset variable is used', 'a pipe fails', 'a file exists'], answer=1, why='nounset.'),
    dict(q='Status of false | true with pipefail?', options=['0', '1', '2', '141'], answer=1, why='Last non-zero.'),
    dict(q='How to debug a script line by line?', options=['bash -n', 'bash -x', 'bash -e', 'bash -u'], answer=1, why='xtrace.'),
    dict(q='Under set -e, which does NOT stop the script when cmd fails?', options=['cmd', 'cmd || true', 'x=$(cmd)', 'cmd; echo'], answer=1, why='Checked by ||.'),
    dict(q='With set -e and n=0, ((n++)) …', options=['works', 'exits the script', 'sets n to 2', 'prints 0'], answer=1, why='Old value 0 = false.'),
    dict(q='Which turns xtrace OFF?', options=['set -x', 'set +x', 'unset x', 'set -o x'], answer=1, why='+ = off.'),
    dict(q='How to remove a function f?', options=['unset f', 'unset -f f', 'rm f', 'delete f'], answer=1, why='-f.'),
])

REVISION = [
    '<code>set -euo pipefail</code> on line 2 of every script (not in the shebang).',
    '-e exits on failure except in if/while conditions, before && / ||, after !, non-final pipe parts; beware ((x++)) at 0.',
    '-u: unset variable = error; use ${V:-default} for optional and ${V:?msg} for required.',
    'pipefail: any failing part fails the pipe; ${PIPESTATUS[@]} shows each.',
    'bash -x / set -x … set +x, PS4 with $LINENO; bash -n for syntax; never trace secrets.',
    'set -o lists; - on, + off; noclobber and >|; set -o vi; set --; unset / unset -f.',
]

FAQ = [
    ('What does set -e do in bash?', 'It makes the script exit immediately when a command fails (non-zero status), except in conditions and && / || lists.'),
    ('What is set -euo pipefail?', 'Bash “strict mode”: exit on errors (-e), on unset variables (-u), and on failures anywhere in a pipeline (pipefail).'),
    ('How do I debug a bash script?', 'Run bash -x script.sh (or set -x inside it) to print each command as it is executed; bash -n checks syntax.'),
    ('How do I show line numbers in bash -x?', "Set PS4='+ $LINENO: ' before running with -x."),
    ('Why does my script exit at ((i++))?', 'Under set -e, ((i++)) returns status 1 when i was 0. Use i=$((i+1)) or ((++i)).'),
    ('What does set -o noclobber do?', 'It prevents > from overwriting existing files; >| forces the overwrite.'),
    ('How do I unset a function?', 'unset -f NAME.'),
]

PRACTICE_INTRO = 'Small option tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Stop on error', stmt='Show that set -e stops before the second echo (print the status).', inp='nothing', code="bash -c 'set -e; echo one; false; echo two'; echo \"status $?\"\n", explain='one, then 1.'),
    dict(level='easy', title='Unset', stmt='Remove a variable and print it in brackets.', inp='nothing', code="x=9; unset x; echo \"[$x]\"\n", explain='[].'),
    dict(level='easy', title='Trace', stmt='Trace one assignment with bash -x.', inp='nothing', code="bash -xc 'y=4' 2>&1\n", explain='+ y=4.'),
    dict(level='medium', title='Default under -u', stmt='Print ${CITY:-Pune} under set -u with CITY unset.', inp='nothing', code="bash -uc 'echo \"${CITY:-Pune}\"'\n", explain='Default.'),
    dict(level='medium', title='Pipefail', stmt='Show the status of a pipe whose first part fails, with pipefail.', inp='nothing', code="bash -c 'set -o pipefail; false | cat; echo $?'\n", explain='1.'),
    dict(level='medium', title='PIPESTATUS', stmt='Print each status of true | false | true.', inp='nothing', code="true | false | true; echo \"${PIPESTATUS[*]}\"\n", explain='0 1 0.'),
    dict(level='business', title='Counter', stmt='Count to 3 under set -e safely.', inp='nothing', code="bash -c 'set -e; c=0; for i in 1 2 3; do c=$((c+1)); done; echo $c'\n", explain='$(( )).'),
    dict(level='business', title='Allowed failure', stmt='Under set -e, try to remove a missing file and continue.', inp='nothing', code="bash -c 'set -e; rm nofile 2>/dev/null || true; echo continued'\n", explain='|| true.'),
]

SCN_INTRO = 'Interview questions about shell options, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you debug a shell script?”', 'Classic question.', 'tools?',
        '''<ul>
          <li><code>bash -x script.sh</code> or <code>set -x</code>.</li>
          <li><code>bash -n</code> for syntax.</li>
          <li>echo/printf of values; shellcheck.</li>
        </ul>''', 'only “I add echo statements”.') +
    scn('DevOps', 'Junior', 'CI is green but the deploy failed', 'Logs show an error mid-script.', 'exit status?',
        '''<ol>
          <li>The script continued after the error; the last command succeeded.</li>
          <li>Add <code>set -euo pipefail</code> on line 2.</li>
          <li>Handle expected failures with if / ||.</li>
        </ol>''', 'parsing logs for the word “error”.') +
    scn('SRE', 'Mid-level', 'Script with set -e exits silently in a loop', 'No message, status 1.', 'traps of -e?',
        '''<ul>
          <li><code>bash -x</code> shows the last line: <code>((count++))</code> with count=0.</li>
          <li>Use <code>count=$((count+1))</code>.</li>
          <li>Other traps: grep with no match, $(false), functions in conditions.</li>
        </ul>''', 'removing set -e.') +
    scn('Platform', 'Senior', 'Choose error handling for 200 team scripts', 'Inconsistent styles.', 'standard?',
        '''<ul>
          <li>Template: <code>set -euo pipefail</code>, <code>trap … ERR EXIT</code> for messages and clean-up (12.10).</li>
          <li>shellcheck in CI; bash -n pre-commit hook.</li>
          <li>Explicit checks for important steps.</li>
        </ul>''', 'one big wrapper that hides errors.')
) + interview([
    ('What does set -x do?', 'Prints each command (after expansion) before running it.'),
    ('set -e vs set -u?', 'Exit on failing command vs exit on unset variable.'),
    ('What is pipefail?', 'Pipeline fails if any command in it fails.'),
    ('How to turn an option off?', 'set +x (plus instead of minus).'),
    ('How to check syntax only?', 'bash -n.'),
    ('What is PIPESTATUS?', 'Array of the statuses of the last pipeline.'),
    ('What does set -- do?', 'Sets the positional parameters.'),
], [
    ('RHCSA (EX200)', 'Write and debug shell scripts.'),
    ('LFCS', 'Shell scripting: debugging and error handling.'),
    ('CompTIA Linux+', 'set options, debugging scripts.'),
]) + distro('The core options are POSIX; pipefail is newer.', [
    ('set -e -u -x', 'yes', 'yes', 'yes', 'Git Bash'),
    ('pipefail', 'bash/dash 0.5.12+', 'yes', 'bash 3.2 yes', '-'),
    ('PIPESTATUS', 'bash', 'bash', 'zsh: pipestatus', '-'),
    ('set -o vi', 'yes', 'yes', 'yes (zsh: bindkey -v)', 'PSReadLine vi mode'),
    ('noclobber', 'yes', 'yes', 'yes', '-'),
]) + teaser('12.7', 'Riya’s script is strict now, but it always does the same thing. Real tools take input: a file name as $1, how many arguments ($#), a question answered with read, and some arithmetic with expr and $(( )). Next: script input and arithmetic.')

CHEATSHEET = cheatsheet('Shell options', [
    ('Strict', [('set -e', 'stop on error'), ('set -u', 'unset = error'), ('set -o pipefail', 'honest pipes'), ('set -euo pipefail', 'all three')]),
    ('Debug', [('bash -x s.sh', 'trace'), ('set -x / +x', 'part'), ("PS4='+ $LINENO: '", 'line nos'), ('bash -n s.sh', 'syntax')]),
    ('Exceptions', [('cmd || true', 'allowed'), ('if cmd', 'checked'), ('${V:-}', 'optional'), ('((++n))', 'not n++')]),
    ('More', [('set -o', 'list'), ('set -C / >|', 'noclobber'), ('set -o vi', 'vi keys'), ('set -- a b', '$1 $2'), ('unset -f f', 'function')]),
])

MINDMAP = mindmap('set', [
    ('-e', 'red', ['stop on error', 'if/&&/|| exempt', '((n++)) trap']),
    ('-u', 'amber', ['unset = error', '${V:-def}', '${V:?msg}']),
    ('pipefail', 'violet', ['any part fails', 'PIPESTATUS', 'grep no match']),
    ('-x', 'green', ['trace', 'PS4', 'secrets!']),
    ('More', 'blue', ['-n syntax', '-C noclobber', '-o vi']),
    ('unset', 'acc', ['variables', '-f functions', 'set --']),
])

LAB = lab('harden a script', 'Build the lab: <code>job.sh</code> has four weaknesses. Fix them, then run the checker.',
    setup='''mkdir -p ~/lab126 && cd ~/lab126 && rm -rf job.sh out
printf 'ok\\nok\\n' > input.log
cat > job.sh <<'EOF'
#!/bin/bash
out_dir=$OUT
mkdir -p "$out_dir"
count=0
((count++))
grep ERROR input.log | wc -l > "$out_dir/errors.txt"
echo "done $count"
EOF''',
    tasks=['Add strict mode (<code>set -euo pipefail</code>) as line 2.',
           'Make <code>out_dir</code> default to <code>out</code> when OUT is not set.',
           'Make the counter safe under set -e (it must reach 1).',
           'Allow the grep to find nothing: the script must still write <code>0</code> and finish.'],
    solution='''cat > job.sh <<'EOF'
#!/bin/bash
set -euo pipefail
out_dir=${OUT:-out}
mkdir -p "$out_dir"
count=0
count=$((count + 1))
{ grep ERROR input.log || true; } | wc -l > "$out_dir/errors.txt"
echo "done $count"
EOF''',
    check='''cd ~/lab126; rm -rf out
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
res=$(env -u OUT bash job.sh 2>/dev/null); st=$?
ok "1 strict"  '[ "$(sed -n 2p job.sh)" = "set -euo pipefail" ]'
ok "2 default" '[ -d out ]'
ok "3 counter" '[ "$res" = "done 1" ] && [ $st = 0 ]'
ok "4 grep"    '[ "$(cat out/errors.txt 2>/dev/null)" = 0 ]' ''')
