import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)
_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index('SS = r"""') + 9
SS = _s[_i:_s.index('"""', _i)]

META = dict(
    module='01-script-craft', lesson='03-exit-codes-logging-and-stderr', n='1.3',
    module_label='Module 1 · Script craft',
    title='Exit codes, logging and messages to stderr',
    desc='Make Bash scripts observable: an exit-code contract (0, 1, 2, custom, 126, 127, 128+N), $?, if, && and ||, PIPESTATUS and pipefail, stdout vs stderr and redirection order, timestamped log lines with levels and LOG_LEVEL, a small logging library, log files, logger and journalctl, with every run real and 35+ examples.',
    og_desc='Exit codes, stderr, log levels, timestamps, log files and logger for Bash scripts, with real runs.',
    minutes=35, level='Beginner → Intermediate',
    lead='A script talks through three channels: the exit code for machines, stderr for humans and logs, stdout for the result. Keep them apart and any job is easy to monitor.',
    chips=['Three channels animated', 'The tee trap', '20-line logging library', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """log() { echo "$(date '+%F %T') [$1] demo: ${*:2}" >&2; }

job() {
  log INFO "start"
  if [[ ${1:-} == bad ]]; then log ERROR "bad input"; return 3; fi
  echo "result: 42"            # the only line on stdout
  log INFO "done"
}

job ok;  echo "exit $?"
job bad; echo "exit $?"
job ok 2>/dev/null               # messages hidden, result kept
"""

RUN = dict(
    heading='Three channels in your browser',
    intro='<p>Messages go to stderr, the result to stdout, and the status to $?.</p>',
    code=MAIN,
    anno=[('>&2', 'stderr.'), ('return 3', 'A function’s exit code.'), ('2>/dev/null', 'Only the result is left.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which lines are on stdout?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the two echo lines print?',
             code="false; echo \"a: $?\"; echo \"b: $?\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the failure of false is hidden by the pipe. Add set -o pipefail.',
             code="false | cat; echo \"status: $?\"\n"),
        dict(label='4 · Your turn', hint='Print each pipe part’s status.',
             code="true | false | true\necho \"${PIPESTATUS[@]}\"\n"),
        dict(label='5 · Challenge', hint='Turn a code into a word with case.',
             code="rc=3\ncase $rc in 0) echo ok;; 2) echo usage;; 3) echo 'bad data';; *) echo error;; esac\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC (a Linux server or VM)',
    intro='<p>The system journal is not available on our build machine; typical outputs.</p>',
    items=[
        dict(title='1 · Write to the journal', cmd="logger -t import -p user.err 'data check failed'\njournalctl -t import -n 1 --no-pager", output='Nov 12 02:00:01 web01 import[4211]: data check failed', note='Typical.'),
        dict(title='2 · Only errors today', cmd="journalctl -t import -p err --since today --no-pager", output='Nov 12 02:00:01 web01 import[4211]: data check failed', note='Typical.'),
        dict(title='3 · rsyslog file (Ubuntu)', cmd="grep import /var/log/syslog | tail -1", output='2026-11-12T02:00:01.123456+05:30 web01 import: data check failed', note='Typical.'),
        dict(title='4 · cron line with a log', cmd="crontab -l", output='0 2 * * * /home/riya/ops/bin/import.sh /data/orders.csv >> /home/riya/ops/logs/cron.log 2>&1', note='Typical.'),
    ],
)

TRACE = dict(
    heading='Saving $? in time, line by line',
    intro='<p>Watch $? change.</p>',
    code='''ls /nonexistent 2>/dev/null
rc=$?
echo "saved: $rc"
echo "now \\$? is: $?"
''',
    notes={2: 'Saved immediately: 2.', 4: 'echo succeeded, so 0.'},
)

WORKED_INTRO = 'Three jobs made observable.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Disk check with a code',
         problem='<p>Exit 0 when a folder uses less than a limit, 1 otherwise, with a log line either way.</p>',
         inp='a folder and a limit', approach=['du, compare, log, return.'],
         code='''log(){ echo "$(date -d '2026-11-12 02:00' '+%F %T') [$1] disk: ${*:2}" >&2; }
check(){ local kb; kb=$(du -sk "$1" | cut -f1)
  if (( kb < $2 )); then log INFO "$1 ok (${kb} KB)"; else log WARN "$1 too big (${kb} KB)"; return 1; fi; }
mkdir -p d; head -c 40000 /dev/zero > d/f
check d 100; echo "exit $?"; check d 10; echo "exit $?"
''', notes={3: 'WARN + non-zero.'}, tryit='Add an ERROR when the folder is missing.', expect='any'),
    dict(level='i', tag='Dev', title='A test runner summary',
         problem='<p>Run three checks, log each, exit with the number of failures.</p>',
         inp='commands', approach=['Count non-zero codes.'],
         code='''fails=0
for c in 'true' 'false' 'test -d /etc'; do
  if bash -c "$c"; then echo "PASS $c" >&2; else echo "FAIL $c" >&2; ((++fails)); fi
done
echo "failures: $fails"; ( exit $fails ); echo "exit $?"
''', notes={3: 'One line per check on stderr.', 5: 'Exit code = failure count.'}, tryit='Cap the code at 125.'),
    dict(level='a', tag='Data', title='Fail a pipeline correctly',
         problem='<p>A compressed log is processed in a pipe; the job must fail if the file is missing.</p>',
         inp='a .gz file', approach=['pipefail.'],
         code='''count(){ set -o pipefail; zcat "$1" 2>/dev/null | grep -c ERROR; }
printf 'ERROR a\\nINFO b\\nERROR c\\n' | gzip > app.log.gz
count app.log.gz; echo "exit $?"
count missing.gz; echo "exit $?"
''', notes={1: 'Without pipefail, grep’s 1 or 0 would be reported.'}, tryit='Print an ERROR line on failure.', expect='any'),
]

QUIZ = mix([
    dict(q='Which exit code means success?', options=['1', '0', '255', '-1'], answer=1, why='Only 0.'),
    dict(q='Messages for humans belong on…', options=['stdout', 'stderr', 'stdin', 'the exit code'], answer=1, why='fd 2.'),
    dict(q='In a | b, $? is the status of…', options=['a', 'b', 'both', 'the worse'], answer=1, why='The last, unless pipefail.'),
    dict(q='${PIPESTATUS[0]} after a | b is…', options=['a’s status', 'b’s status', 'the pipe count', 'the PID'], answer=0, why='Index 0 = first.'),
    dict(q='exit 256 is reported as…', options=['256', '0', '1', 'error'], answer=1, why='One byte.'),
    dict(q='A script killed by kill -TERM returns…', options=['15', '143', '1', '0'], answer=1, why='128+15.'),
    dict(q='cmd > log 2>&1 vs cmd 2>&1 > log:', options=['same', 'only the first puts both in log', 'only the second', 'both fail'], answer=1, why='Order.'),
    dict(q='Write to the system log with…', options=['syslog', 'logger', 'journal', 'echo >/var/log'], answer=1, why='logger.'),
])

REVISION = [
    'Three channels: exit code for machines, stdout for the result, stderr for messages.',
    'Codes: 0 ok, 1 error, 2 usage, 3–125 your own (documented), 126/127 shell, 128+N signals.',
    'Save $? at once; use if/&&/||; PIPESTATUS or pipefail for pipelines.',
    'Redirect: > out 2> err; >> log 2>&1 (order matters); |& in Bash 4+.',
    "Log lines: date '+%F %T' [LEVEL] prog: message; LOG_LEVEL filters DEBUG/INFO/WARN/ERROR.",
    'Files: LOG_FILE, >> 2>&1, tee -a; system: logger -t TAG -p user.err, journalctl -t TAG.',
]

FAQ = [
    ('How do I get the exit code of a command in Bash?', 'Read $? immediately after it, or use if cmd; then … fi.'),
    ('What exit code should a script return on error?', '1 for a general error, 2 for wrong usage, other documented codes for specific failures.'),
    ('How do I print to stderr in Bash?', 'echo "message" >&2.'),
    ('How do I log to a file from a shell script?', 'Append with >> file 2>&1, use tee -a, or exec >>file 2>&1 at the top.'),
    ('Why does my pipeline return 0 even though a command failed?', 'The status is the last command’s; use set -o pipefail or PIPESTATUS.'),
    ('How do I write to syslog from a script?', 'logger -t name "message", read with journalctl -t name.'),
    ('What does exit code 127 mean?', 'Command not found.'),
]

PRACTICE_INTRO = 'Small exit-code and logging tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Status', stmt='Print the status of false.', inp='nothing', code="false; echo $?\n", explain='1.'),
    dict(level='easy', title='stderr', stmt='Print WARN to stderr.', inp='nothing', code="echo WARN >&2\n", explain='>&2.'),
    dict(level='easy', title='Timestamp', stmt='Print 2026-11-12 02:00:00 with date.', inp='a fixed date', code="date -d '2026-11-12 02:00' '+%F %T'\n", explain='%F %T.'),
    dict(level='medium', title='Pipe statuses', stmt='Show both statuses of false | true.', inp='nothing', code="false | true; echo ${PIPESTATUS[*]}\n", explain='1 0.'),
    dict(level='medium', title='pipefail', stmt='Make false | true report 1.', inp='nothing', code="set -o pipefail; false | true; echo $?\n", explain='1.'),
    dict(level='medium', title='Wrap', stmt='Show the code of exit 300.', inp='nothing', code="bash -c 'exit 300'; echo $?\n", explain='44.'),
    dict(level='business', title='Level filter', stmt='Print only WARN and ERROR lines.', inp='log lines', code="printf '[INFO] a\\n[WARN] b\\n[ERROR] c\\n' | grep -E '\\[(WARN|ERROR)\\]'\n", explain='Two lines.'),
    dict(level='business', title='Code to word', stmt='Map 3 to bad data.', inp='a code', code="rc=3; case $rc in 3) echo 'bad data';; esac\n", explain='case.'),
]

SCN_INTRO = 'Interview questions about exit codes and logging.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is $?”', 'Common.', 'values?',
        '''<ul>
          <li>Status of the last command.</li>
          <li>0 success, non-zero failure.</li>
          <li>127 not found, 126 not executable.</li>
        </ul>''', 'saying it is the PID.') +
    scn('Service company', 'Junior', 'Cron job fails silently', 'No mail, no log.', 'fix?',
        '''<ol>
          <li>Non-zero exit on failure.</li>
          <li>>> log 2>&1 in the cron line.</li>
          <li>Timestamped log lines; MAILTO for stderr.</li>
        </ol>''', 'adding sleep.') +
    scn('Product company', 'Mid-level', 'CI step green, but tests failed', 'Uses | tee.', 'why?',
        '''<ul>
          <li>tee’s status hides the failure.</li>
          <li>set -o pipefail in the step.</li>
          <li>Or check PIPESTATUS[0].</li>
        </ul>''', 'removing logging.') +
    scn('Platform', 'Senior', 'Design logging for 50 team scripts', 'Standards.', 'proposal?',
        '''<ul>
          <li>Shared log.sh: time, level, program, stderr.</li>
          <li>Documented exit codes per script.</li>
          <li>journald/central shipping; no secrets in logs.</li>
        </ul>''', 'each team inventing its own.')
) + interview([
    ('Range of exit codes?', '0–255.'),
    ('What is 128+N?', 'Killed by signal N.'),
    ('stdout vs stderr?', 'fd 1 result, fd 2 messages.'),
    ('What does 2>&1 do?', 'Points stderr where stdout points now.'),
    ('PIPESTATUS?', 'Array of each pipe command’s status.'),
    ('How to send to syslog?', 'logger.'),
    ('Why levels?', 'Filter noise: DEBUG < INFO < WARN < ERROR.'),
], [
    ('LFCS', 'Redirection and exit statuses.'),
    ('RHCSA', 'Use exit codes in scripts; journalctl.'),
    ('CompTIA Linux+', 'Exit codes, logging.'),
]) + distro('Where logs go per distribution.', [
    ('journald', 'yes', 'yes', 'yes', 'yes'),
    ('Text syslog file', '/var/log/syslog', '/var/log/messages', '/var/log/messages', 'none by default'),
    ('logger', 'util-linux', 'util-linux', 'util-linux', 'util-linux'),
    ('Read errors', 'journalctl -p err', 'same', 'same', 'same'),
    ('macOS', '-', '-', '-', 'log show (unified log)'),
]) + teaser('1.4', 'You now have usage, options, exit codes and logging. Next: put them all into one reusable script template, and let ShellCheck find the bugs you cannot see.')

CHEATSHEET = cheatsheet('Exit codes and logs', [
    ('Codes', [('exit 0', 'ok'), ('exit 1 / 2', 'error / usage'), ('126 / 127', 'not exec / not found'), ('128+N', 'signal')]),
    ('Status', [('rc=$?', 'save'), ('if cmd; then', 'test'), ('${PIPESTATUS[@]}', 'pipe'), ('set -o pipefail', 'worst')]),
    ('Streams', [('>&2', 'message'), ('> out 2> err', 'split'), ('>> log 2>&1', 'all'), ('|&', 'pipe both')]),
    ('Logs', [("date '+%F %T'", 'time'), ('[LEVEL]', 'severity'), ('logger -t T', 'syslog'), ('journalctl -t T', 'read')]),
])

MINDMAP = mindmap('Observable script', [
    ('Exit code', 'blue', ['0 / 1 / 2', 'custom', '128+N']),
    ('Status', 'green', ['$?', 'if && ||', 'PIPESTATUS']),
    ('Streams', 'amber', ['stdout result', 'stderr msgs', '2>&1']),
    ('Log line', 'violet', ['time', 'level', 'program']),
    ('Storage', 'red', ['file', 'tee -a', 'logger']),
    ('Rules', 'acc', ['no secrets', 'rotate', 'document']),
])

LAB = lab('make a job observable', 'Build the lab (it creates <code>~/lab13/data.txt</code>), write <code>~/lab13/job.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab13; mkdir -p ~/lab13 && cd ~/lab13
printf '10\\n20\\n30\\n' > data.txt; printf '10\\nx\\n30\\n' > bad.txt''',
    tasks=['<code>job.sh FILE</code> prints only the <b>sum</b> of the numbers on stdout and exits 0.',
           'Every message is a line on <b>stderr</b> in the form <code>YYYY-MM-DD HH:MM:SS [LEVEL] job.sh: text</code>; a run writes at least an INFO line.',
           'A line that is not a number: an ERROR line on stderr, nothing on stdout, exit <b>3</b>. A missing file: exit <b>1</b>. No argument: exit <b>2</b>.',
           'When <code>LOG_FILE</code> is set, the same log lines are also appended to that file.'],
    solution='''cat > job.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
log() { local l="$(date '+%F %T') [$1] job.sh: ${*:2}"; echo "$l" >&2; [[ -n ${LOG_FILE:-} ]] && echo "$l" >> "$LOG_FILE"; return 0; }
(( $# == 1 )) || { log ERROR "usage: job.sh FILE"; exit 2; }
[[ -r $1 ]] || { log ERROR "cannot read $1"; exit 1; }
log INFO "start $1"
if grep -qvE '^[0-9]+$' "$1"; then log ERROR "non-numeric line in $1"; exit 3; fi
awk '{s+=$1} END{print s}' "$1"
log INFO "done"
EOF
chmod +x job.sh''',
    check='''cd ~/lab13; rm -f t.log
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
re='^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} \\[(DEBUG|INFO|WARN|ERROR)\\] job\\.sh: '
ok "1 result"  '[ "$(./job.sh data.txt 2>/dev/null)" = 60 ]'
ok "2 format"  './job.sh data.txt 2>e >/dev/null; [ -s e ] && ! grep -vqE "$re" e && grep -q "\\[INFO\\]" e'
ok "3 codes"   './job.sh bad.txt 2>e >o; r1=$?; ./job.sh nosuch 2>/dev/null; r2=$?; ./job.sh 2>/dev/null; r3=$?; [ $r1 -eq 3 ] && [ ! -s o ] && grep -q "\\[ERROR\\]" e && [ $r2 -eq 1 ] && [ $r3 -eq 2 ]'
ok "4 logfile" 'LOG_FILE=t.log ./job.sh data.txt >/dev/null 2>e; [ -s t.log ] && cmp -s e t.log' ''')
