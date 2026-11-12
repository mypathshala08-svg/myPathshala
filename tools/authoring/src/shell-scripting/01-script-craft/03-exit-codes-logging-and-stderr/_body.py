import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# A nightly import job with a small logging library (all really run on our build machine)
SS = r"""rm -rf ~/ops; mkdir -p ~/ops/data ~/ops/bin ~/ops/logs; cd ~/ops
printf 'id,city,amount\n1,Pune,450\n2,Mumbai,1200\n3,Pune,abc\n4,Delhi,800\n' > data/orders.csv
cat > bin/log.sh <<'EOF'
# log.sh - tiny logging library: source it, then call log_info / log_warn / log_error
LOG_FILE=${LOG_FILE:-}
LOG_LEVEL=${LOG_LEVEL:-INFO}
declare -A _LV=([DEBUG]=10 [INFO]=20 [WARN]=30 [ERROR]=40)
_log() {
  local lvl=$1; shift
  (( ${_LV[$lvl]} >= ${_LV[$LOG_LEVEL]} )) || return 0
  local line
  line="$(date -d "${LOG_NOW:-now}" '+%F %T') [$lvl] ${PROG:-script}: $*"
  echo "$line" >&2
  [[ -n $LOG_FILE ]] && echo "$line" >> "$LOG_FILE"
  return 0
}
log_debug() { _log DEBUG "$@"; }
log_info()  { _log INFO  "$@"; }
log_warn()  { _log WARN  "$@"; }
log_error() { _log ERROR "$@"; }
EOF
cat > bin/import.sh <<'EOF'
#!/usr/bin/env bash
# import.sh - check and load an orders CSV; exit codes: 0 ok, 1 error, 2 usage, 3 bad data
set -euo pipefail
readonly PROG=${0##*/}
readonly E_OK=0 E_ERR=1 E_USAGE=2 E_DATA=3
source "$(dirname "$0")/log.sh"

main() {
  (( $# == 1 )) || { log_error "usage: $PROG CSV"; exit $E_USAGE; }
  local file=$1 bad
  [[ -r $file ]] || { log_error "cannot read $file"; exit $E_ERR; }
  log_info "start: $file"
  log_debug "lines: $(wc -l < "$file")"
  bad=$(awk -F, 'NR > 1 && $3 !~ /^[0-9]+$/ {print NR": "$0}' "$file")
  if [[ -n $bad ]]; then
    log_warn "rejected rows: $bad"
    log_error "data check failed"
    exit $E_DATA
  fi
  log_info "loaded $(( $(wc -l < "$file") - 1 )) rows"
  exit $E_OK
}
main "$@"
EOF
chmod +x bin/import.sh
export LOG_NOW='2026-11-12 02:00:00'"""

HOOK = hook('Every night at 2 a.m. Riya’s <code>import.sh</code> loads the day’s orders. One morning the dashboard is empty, cron says nothing, and the script’s only trace is a line “done” in a file nobody reads. Did it fail? Why? When? A script talks to the world in exactly three ways: its <b>exit code</b> (did it work?), its <b>standard output</b> (the result) and its <b>standard error</b> (messages for humans and logs). This lesson gives Riya’s job a clear exit-code contract, log lines with time and level, a log file, and the system log, all with real runs.',
    ['design exit codes for a script (0, 1, 2 and your own) and check them with $?, &&, ||, if and PIPESTATUS',
     'keep results on stdout and every message on stderr, and redirect each where it belongs',
     'write timestamped, levelled log lines (DEBUG, INFO, WARN, ERROR) with a small reusable library',
     'log to a file and to the system log with logger, and read them back'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the silent 2 a.m. failure'),
    ('decide', 'Where does it go?', 2, 'the quick chart'),
    ('definition', 'Exit codes and logs', 5, 'simple meaning + 4 depths'),
    ('types', 'Codes and levels', 4, 'tables'),
    ('commands', 'Step by step', 15, 'codes, stderr, log lines, files, syslog'),
    ('animation', 'See it happen', 4, 'three channels'),
    ('run', 'Run on your PC', 3, 'journalctl'),
    ('lab', 'Practice lab', 8, 'make a job observable'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('This message… → goes to', [
    ('the result (numbers, report)', 'stdout', 'echo'),
    ('progress, warnings, errors', 'stderr', 'echo … >&2'),
    ('did it work? (for programs)', 'exit code', 'exit N'),
    ('history for later', 'a log file', '>> logs/job.log'),
    ('central/system history', 'syslog / journal', 'logger -t job'),
    ('only when debugging', 'DEBUG level', 'LOG_LEVEL=DEBUG'),
])

cmap = concept_map(
    [('1.1', 'Anatomy of a script', 'die, exit 2'), ('1.2', 'Options', '-v verbose'), ('L:5.1', 'Streams', 'stdin, stdout, stderr')],
    ['exit code contract (0, 1, 2, custom)', '$?, &&, ||, if, PIPESTATUS', 'stdout vs stderr', 'log lines: time, level, program', 'log levels and LOG_LEVEL', 'log files and tee', 'logger and journalctl'],
    [('1.4', 'Template + ShellCheck', 'all together'), ('3.1', 'Error handling', 'ERR trap'), ('4.2', 'Log monitor', 'read logs'), ('L:18.1', 'System logs', 'journal')],
    'A job that says clearly whether it worked, what it did, and why it failed.')

sc = (term(20, 14, 316, 156, ['$ ./import.sh data/orders.csv', ('2026-11-12 02:00:00 [INFO] start', 'out'), ('[WARN] rejected rows: 4: 3,Pune,abc', 'err'), ('[ERROR] data check failed', 'err'), '$ echo $?', ('3', 'acc')], title='riya@server: ~/ops', prompt='$', size=6.6, step=18)
      + t(352, 36, 'Three channels:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['exit code: did it work?', 'stdout: the result', 'stderr: messages', '+ log file, syslog'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The silent 2 a.m. failure</h2>
  <div class="story">
''' + puzzle('Riya’s old job ended with <code>echo done</code>, so it always exited 0. Her fix, <code>./import.sh orders.csv | tee run.log</code>, still reports 0 in cron even when import.sh exits 3. Then she moves her error messages to stderr and they vanish from <code>run.log</code> altogether. And her colleague asks: “why does your script use exit 3, I thought only 0 and 1 exist?” Three puzzles about the three channels.') + '''
    <p class="narration">On the server, in <code>~/ops</code> (every run in this lesson is real; the clock is fixed to 02:00 so the times repeat).</p>
''' + scene('A terminal: import.sh logs a start line, a warning about a bad row and an error, then echo $? shows exit code 3.', sc,
            'Now the failure has a <tspan font-weight="700" class="s-acc">code, a time and a reason</tspan>.') + '''
K> Isn't printing “ERROR” enough?
A> For a human reading the screen, maybe. But cron, systemd, CI and other scripts never read your text; they read the exit code. And the human reads the log hours later, so every line needs a time and a level.
R> So: code for machines, log lines for humans, stdout only for the actual result.
A> Exactly. Keep those three apart and any job becomes easy to monitor.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A script with three outputs: stdout carries the result to a file or pipe, stderr carries log messages to the screen or a log file, and the exit code goes to the caller such as cron or CI.">'
       + label_box(250, 70, 140, 60, ['import.sh', 'your script'], 'blue', 9.4)
       + arrow(390, 82, 470, 40) + label_box(476, 20, 150, 40, ['stdout (1): result'], 'green', 8.6)
       + arrow(390, 100, 470, 100) + label_box(476, 80, 150, 40, ['stderr (2): messages'], 'amber', 8.6)
       + arrow(390, 118, 470, 160) + label_box(476, 140, 150, 40, ['exit code: 0–255'], 'red', 8.6)
       + label_box(20, 70, 170, 60, ['cron · CI · systemd', 'read only the code'], 'card', 8.4) + arrow(250, 100, 192, 100)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Exit codes and logging at four depths', [
    ('v', 'No jargon: a courier delivery', '      <p>The parcel is the result (stdout). The tracking messages are the log (stderr). “Delivered” or “Failed: address not found” is the exit code: the one thing the sender’s system checks.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>exit 0</code> success, <code>exit 1</code> error, <code>exit 2</code> wrong usage.</li>
        <li><code>echo "…" &gt;&amp;2</code> for every message.</li>
        <li><code>echo "$(date '+%F %T') [INFO] started" &gt;&amp;2</code>.</li>
        <li><code>./job.sh &gt;&gt; job.log 2&gt;&amp;1</code> in cron.</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li><code>$?</code> is overwritten by the very next command: save it at once (<code>rc=$?</code>).</li>
        <li>In a pipeline, <code>$?</code> is the <b>last</b> command’s status; <code>${PIPESTATUS[@]}</code> holds each one, and <code>set -o pipefail</code> uses the worst.</li>
        <li>Levels: DEBUG &lt; INFO &lt; WARN &lt; ERROR; a <code>LOG_LEVEL</code> variable decides what is printed.</li>
        <li><code>logger -t name "msg"</code> writes to syslog/journald; read with <code>journalctl -t name</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: 8 bits and file descriptors', '''      <ul>
        <li>An exit status is <b>one byte</b>: <code>exit 256</code> becomes 0, <code>exit -1</code> becomes 255. Codes above 125 are reserved by the shell (126 not executable, 127 not found, 128+N killed by signal N).</li>
        <li>stdout is file descriptor 1 and stderr 2; both point at the terminal by default. <code>2&gt;&amp;1</code> copies fd 1 into fd 2 <i>at that moment</i>, which is why order matters.</li>
        <li>stdout to a file or pipe is block-buffered, stderr is unbuffered, so in a shared log file their lines can appear out of order.</li>
        <li><code>logger</code> sends to <code>/dev/log</code>; journald stores it with time, host, PID and priority; <code>-p user.err</code> sets the priority.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Exit codes, stderr and log lines</h2>
''' + def_block(
    'An <b>exit code</b> (exit status) is the number from 0 to 255 a program returns when it ends: 0 means success, anything else a kind of failure. <b>Standard error</b> (stderr, file descriptor 2) is the output stream for diagnostics, kept separate from standard output (the result). A <b>log line</b> is a diagnostic message with at least a timestamp, a severity level and the program name, written to stderr, a file or the system log.',
    'Code for machines, log lines for humans, stdout for the result.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Exit status', '0–255; 0 = success.'),
    ('$?', 'Status of the last command.'),
    ('PIPESTATUS', 'Statuses of each pipe part.'),
    ('stderr', 'fd 2, for messages.'),
    ('Log level', 'DEBUG, INFO, WARN, ERROR.'),
    ('Timestamp', 'When it happened: %F %T.'),
    ('logger', 'Writes to the system log.'),
    ('journalctl', 'Reads the systemd journal.'),
]) + '\n' + names('Where the names come from.', [
    ('exit status', 'C’s exit(int)', 'Unix, 1971.'),
    ('$?', '“what happened?”', 'Bourne shell.'),
    ('stderr', 'standard error', 'Unix V6, 1975.'),
    ('syslog', 'system log', 'Eric Allman, sendmail, 1980s.'),
    ('logger', 'command-line syslog client', 'BSD.'),
    ('journald', 'systemd’s journal', '2011.'),
    ('%F %T', 'full date, time', 'strftime.'),
    ('sysexits.h', 'BSD exit-code list', 'EX_USAGE=64 …'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Success', '<code>exit 0</code>'),
    ('Last status', '<code>rc=$?</code>'),
    ('Pipe statuses', '<code>${PIPESTATUS[@]}</code>'),
    ('Message', '<code>echo "…" &gt;&amp;2</code>'),
    ('Timestamp', "<code>date '+%F %T'</code>"),
    ('System log', '<code>logger -t job "msg"</code>'),
]) + '\n' + lv + didyou('grep uses three exit codes on purpose: 0 = found, 1 = not found, 2 = error (such as a missing file). That is why <code>grep -q pattern file</code> works perfectly in <code>if</code>, and why a script should also give different failures different codes.') + '''
EXAM> “How do you get the exit status of each command in a pipeline?” → ${PIPESTATUS[@]} right after the pipeline, or set -o pipefail to make $? the last non-zero status.
''' + qc('Why must rc=$? come immediately after the command?', 'Every command, even echo or [[, replaces $?.') + mistake('job.sh | tee job.log   in cron',
    'set -o pipefail; job.sh 2>&1 | tee -a job.log   (or job.sh >> job.log 2>&1)',
    'The pipeline’s status is tee’s (0), so cron never sees the failure, and stderr is not in the log.') + mistake('echo "ERROR: disk full"',
    'log_error "disk full"; exit 1   (time, level, stderr, a code)',
    'A message on stdout pollutes the result, has no time, and the exit code still says success.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Exit codes and log levels</h2>
''' + table(['Code', 'Meaning', 'Who uses it'], [
    ['0', 'success', 'everyone'],
    ['1', 'general error', 'most scripts'],
    ['2', 'wrong usage / misuse of shell builtins', 'getopts errors, bash'],
    ['3–125', 'your own meanings (document them!)', 'import.sh: 3 = bad data'],
    ['126', 'found, not executable', 'shell'],
    ['127', 'command not found', 'shell'],
    ['128+N', 'killed by signal N (130 Ctrl+C, 137 KILL, 143 TERM)', 'shell'],
    ['64–78', 'sysexits.h (EX_USAGE 64, EX_DATAERR 65 …)', 'some tools, mail'],
], minw=520) + table(['Level', 'Use for', 'Example'], [
    ['DEBUG', 'details only while debugging', 'lines: 5'],
    ['INFO', 'normal progress', 'start, loaded 4 rows'],
    ['WARN', 'something odd, job continues', 'rejected row 4'],
    ['ERROR', 'the job failed (then exit non-zero)', 'data check failed'],
], minw=420) + qc('Your script is killed with kill -TERM. What exit code does the caller see?', '143 (128 + 15).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Codes, streams, log lines, files and syslog</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops</code>: <code>data/orders.csv</code> (row 4 has a bad amount <code>abc</code>), the logging library <code>bin/log.sh</code> and the job <code>bin/import.sh</code>. <code>LOG_NOW</code> fixes the clock at 02:00 so the times repeat.</p>
''' + cmdcard_u(['every script', 'every check of another command'], ['ignoring $?'])(
    'codes', 'exit N · $? · && || · if · PIPESTATUS', 'exit codes',
    'A script returns <code>exit N</code> (or the status of its last command). The caller reads it with <code>$?</code>, chains with <code>&amp;&amp;</code>/<code>||</code>, or tests it with <code>if cmd; then</code>. Document your own codes at the top of the script.',
    'rc=$?; case $rc in 0) … ;; 3) … ;; esac', 'safe',
    [('exit 0', 'success', 'end'),
     ('exit 1 / 2', 'error / usage', 'conventions'),
     ('exit 3+', 'own meanings', 'documented'),
     ('rc=$?', 'save at once', 'before anything'),
     ('if cmd; then', 'test success', 'clean'),
     ('${PIPESTATUS[@]}', 'each pipe part', 'pipelines')],
    dict(setup=SS, cmd="cd ~/ops\nbin/import.sh 2>/dev/null; echo \"no file: $?\"\nbin/import.sh nosuch.csv 2>/dev/null; echo \"missing: $?\"\nbin/import.sh data/orders.csv 2>/dev/null; echo \"bad data: $?\"\nsed -i '/abc/d' data/orders.csv; bin/import.sh data/orders.csv 2>/dev/null; echo \"clean data: $?\"", note='Four situations, four different codes the caller can act on.', expect='any'),
    [('sys', [
        dict(situation='React to each code in a wrapper.', setup=SS, cmd="cd ~/ops; bin/import.sh data/orders.csv 2>/dev/null; rc=$?\ncase $rc in 0) echo 'OK';; 2) echo 'fix the cron line';; 3) echo 'ask the data team';; *) echo \"failed ($rc)\";; esac", why='Different failures, different people.', expect='any')]),
     ('devops', [
        dict(situation='The pipeline trap (the puzzle).', setup=SS, cmd="cd ~/ops; bin/import.sh data/orders.csv 2>&1 | tee run.log > /dev/null; echo \"\\$?=$?  PIPESTATUS=${PIPESTATUS[*]}\"\nset -o pipefail; bin/import.sh data/orders.csv 2>&1 | tee run.log > /dev/null; echo \"with pipefail: $?\"", why='tee succeeded, so $? was 0; PIPESTATUS and pipefail show the 3.', expect='any')]),
    ],
    anat=anatomy([('exit', 'cmd', 'end the script'), ('3', 'arg', '0–255, documented')], 'Only 0 means success.')
) + cmdcard_u(['all messages'], ['messages on stdout'])(
    'stderr', '>&2 · 2> · 2>&1 · 2>/dev/null', 'stdout vs stderr',
    'Results go to stdout, messages to stderr (<code>&gt;&amp;2</code>). The caller can then separate them: <code>&gt; result.txt 2&gt; errors.log</code>, or join them for a log: <code>&gt;&gt; job.log 2&gt;&amp;1</code> (order matters).',
    './job.sh > result.txt 2> messages.log', 'safe',
    [('>&2', 'message to stderr', 'inside scripts'),
     ('2> file', 'save messages', 'caller'),
     ('2>&1', 'join with stdout', 'after > file'),
     ('2>/dev/null', 'hide messages', 'careful'),
     ('|&', 'pipe both', 'bash 4+'),
     ('exec 2>>log', 'whole script', 'top of script')],
    dict(setup=SS, cmd="cd ~/ops\nsed -i '/abc/d' data/orders.csv\nbin/import.sh data/orders.csv > out.txt 2> msg.log\necho \"stdout: $(wc -c < out.txt) bytes\"; echo 'stderr:'; cat msg.log", note='import.sh prints no result, only messages, so stdout is empty: nothing would corrupt a pipe.'),
    [('dev', [
        dict(situation='Order of redirections matters.', setup=SS, cmd="cd ~/ops; bin/import.sh x 2>&1 > /dev/null | wc -l; bin/import.sh x > /dev/null 2>&1 | wc -l", why='2>&1 first: messages go to the pipe (1 line). After > /dev/null: both discarded (0).', expect='any')]),
    ]
) + cmdcard_u(['any script that runs unattended'], ['plain echo for diagnostics'])(
    'loglines', "log_info · log_warn · log_error · date '+%F %T'", 'log lines with time and level',
    'A log line has a <b>time</b>, a <b>level</b>, the <b>program</b> and the message. A tiny library (<code>bin/log.sh</code>, 20 lines) gives you <code>log_info</code>, <code>log_warn</code>, <code>log_error</code> and <code>log_debug</code>; <code>LOG_LEVEL</code> chooses what is shown.',
    "source bin/log.sh; log_info \"loaded $n rows\"", 'safe',
    [("date '+%F %T'", '2026-11-12 02:00:00', 'sortable'),
     ('[LEVEL]', 'severity', 'filter'),
     ('PROG:', 'which script', 'shared logs'),
     ('LOG_LEVEL=DEBUG', 'show more', 'debugging'),
     ('LOG_LEVEL=WARN', 'show less', 'cron'),
     ("date -u / %z", 'UTC or offset', 'servers')],
    dict(setup=SS, cmd="cd ~/ops\nbin/import.sh data/orders.csv; echo \"exit $?\"\necho '--- with LOG_LEVEL=DEBUG:'\nLOG_LEVEL=DEBUG bin/import.sh data/orders.csv 2>&1 | head -2", note='DEBUG adds the line count; the default INFO hides it.', expect='any'),
    [('sys', [
        dict(situation='Read the library.', setup=SS, cmd="cd ~/ops; sed -n '5,13p' bin/log.sh", why='One function, four levels, stderr and an optional file.')]),
    ]
) + cmdcard_u(['history of every run'], ['logs that grow forever (rotate them: Linux Lesson 18.2)'])(
    'logfile', 'LOG_FILE · >> · tee -a · exec', 'log to a file',
    'Set <code>LOG_FILE</code> and every log line is also appended to it. For a cron job, <code>&gt;&gt; logs/import.log 2&gt;&amp;1</code> captures everything; <code>tee -a</code> shows and saves at once; <code>exec &gt;&gt;file 2&gt;&amp;1</code> at the top of a script redirects the rest of it.',
    'LOG_FILE=logs/import.log ./import.sh data.csv', 'change',
    [('LOG_FILE=path', 'library writes there', 'per job'),
     ('>> log 2>&1', 'cron capture', 'everything'),
     ('tee -a log', 'screen + file', 'manual runs'),
     ('exec >>log 2>&1', 'rest of script', 'top'),
     ('grep ERROR log', 'find failures', 'reading'),
     ('tail -f log', 'follow live', 'watching')],
    dict(setup=SS, cmd="cd ~/ops\nfor d in 10 11 12; do LOG_NOW=\"2026-11-$d 02:00\" LOG_FILE=logs/import.log bin/import.sh data/orders.csv 2>/dev/null; done\nwc -l < logs/import.log\ngrep ERROR logs/import.log\ngrep -c 'start:' logs/import.log", note='Three nights, three runs, one file: grep answers “when did it fail?”', expect='any'),
    [('sys', [
        dict(situation='Failures per day from the log.', setup=SS, cmd="cd ~/ops; for d in 10 11 12; do LOG_NOW=\"2026-11-$d 02:00\" LOG_FILE=logs/import.log bin/import.sh data/orders.csv 2>/dev/null; done; grep ERROR logs/import.log | cut -d' ' -f1 | uniq -c", why='Timestamps make logs searchable.', expect='any')]),
    ]
) + cmdcard_u(['servers with central logging'], ['debug spam in syslog'])(
    'syslog', 'logger -t TAG -p PRIO · journalctl -t TAG', 'the system log',
    '<code>logger</code> writes a message to the system log (journald/rsyslog), where admins and monitoring tools already look. <code>-t</code> sets a tag, <code>-p user.err</code> the priority; read it with <code>journalctl -t TAG</code> or in <code>/var/log/syslog</code>.',
    'logger -t import -p user.err "data check failed"', 'safe',
    [('-t TAG', 'name', 'filter'),
     ('-p user.err', 'priority', 'alerts'),
     ('-s', 'also to stderr', 'both'),
     ('journalctl -t TAG', 'read', 'systemd'),
     ('-p err', 'only errors', 'triage'),
     ('/var/log/syslog', 'rsyslog file', 'Debian')],
    dict(cmd="logger --version | head -1\nlogger -t import -p user.err 'data check failed'; echo \"logger exit: $?\"", note='logger accepted the message (exit 0). Our build machine has no journal to read it back from; on a real server it lands in the journal and syslog (see Run on your PC). A script should never stop just because logging failed.', expect='any'),
    [('sys', [
        dict(situation='Priorities are numbers too.', cmd="for p in emerg alert crit err warning notice info debug; do printf '%s ' $p; done; echo; echo 'err = 3, info = 6 (lower = more severe)'", why='journalctl -p err shows 0–3.')]),
    ]
) + undo('Logging mistakes are cheap to fix; lost information is not.', [
    ('Lost a failure in a pipe:', 'add <code>set -o pipefail</code> or check <code>${PIPESTATUS[0]}</code>.'),
    ('Messages missing from the log:', 'you captured stdout only: add <code>2&gt;&amp;1</code> after the file.'),
    ('Log file filled the disk:', 'truncate it (<code>: &gt; job.log</code>) and add logrotate (Linux 18.2).'),
    ('Secrets in logs:', 'never log passwords or tokens; mask them (<code>${TOKEN:0:4}****</code>).'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(cmd="bash -c 'exit 256'; echo \"reported as $?\"", meaning='Codes wrap around at 256: this is reported as 0, a “success”.', fix='Use 0–125 for your own codes.'),
    dict(cmd="false; echo \"checked\"; echo \"rc=$?\"", meaning='$? now belongs to the first echo, so it says 0.', fix='rc=$? immediately after the command.'),
    dict(setup=SS, cmd="cd ~/ops && bash -c 'source bin/log.sh; LOG_LEVEL=TRACE; log_info hi'", meaning='Unknown level: the associative-array lookup gives an empty value and the (( )) test breaks.', fix='Validate LOG_LEVEL against DEBUG|INFO|WARN|ERROR.'),
]) + qc('cron runs job.sh | tee job.log and the job fails with 3. What does cron see?', '0 (tee’s status), unless pipefail is set.') + '''
'''
cards = cards + '</section>\n'

def ch(k):
    o = t(180, 18, './import.sh orders.csv', 9.6, 'ink2', bold=True)
    rows = [('stderr', '[INFO] start: orders.csv', 'amber'), ('stderr', '[WARN] rejected rows: 4', 'amber'), ('stderr', '[ERROR] data check failed', 'red'), ('exit code', '3 → cron, CI, wrapper', 'blue')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 32 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
see_cmds = [['$ ./import.sh orders.csv', ('[INFO] start', 'out')], ['awk checks amounts', ('[WARN] row 4: abc', 'err')], ['bad rows found', ('[ERROR] data check failed', 'err')], ['$ echo $?', ('3', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@server: ~/ops', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Start.', 'Warn.', 'Error.', 'Exit.'])]
two = anim_two('One run, three channels', 'Behind the screen: what goes where',
               'A terminal: import.sh logs start, a warning and an error, then exits 3.',
               'Rows fill in: three log lines on stderr, then the exit code to the caller.', see, [ch(k) for k in range(4)],
               ['start.', 'warn.', 'error.', 'exit 3.'], ['info', 'warn', 'error', 'exit'])

def ps(k):
    o = t(180, 18, 'import.sh | tee run.log', 9.6, 'ink2', bold=True)
    o += label_box(14, 36, 160, 46, ['import.sh', 'exit 3'], 'red', 8.6) + label_box(186, 36, 160, 46, ['tee', 'exit 0'], 'green', 8.6)
    o += t(180, 112, ['each part has its own status', '$? = 0 (last part): failure hidden', 'PIPESTATUS = (3 0)', 'pipefail: $? = 3'][k], 9.2, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'The tee trap',
              'Logging with a pipe can hide the failure.', 'PIPESTATUS', 'Two boxes: import.sh exit 3, tee exit 0.', [ps(k) for k in range(4)],
              ['parts.', '$?.', 'PIPESTATUS.', 'pipefail.'], hid='scenario-tee')

dx = dissect('Layer by layer: where a log line goes',
    'Each layer has a real command from our build machine.', [
    dict(key='fd', name='File descriptors', sub='1 and 2', why='Separate streams.', how='Per process.', impl='/proc/self/fd.', used='Redirection.',
         cmd="ls -l /proc/self/fd/ > out.txt 2> err.txt; awk 'NR>1 && $9 <= 2 {print $9, \"->\", $NF}' out.txt | sed \"s|$HOME|~|\""),
    dict(key='line', name='Log line', sub='time level prog msg', why='Readable later.', how='date + printf.', impl='log.sh.', used='grep, monitors.',
         setup=SS, cmd="cd ~/ops; bash -c 'PROG=demo; source bin/log.sh; log_warn \"disk 91%\"' 2>&1"),
    dict(key='code', name='Exit status', sub='one byte', why='Machines decide.', how='exit N.', impl='wait() status.', used='cron, CI.',
         cmd="for n in 0 3 255 256 300; do bash -c \"exit $n\"; echo \"exit $n -> $?\"; done"),
], hint='Descriptors → line → status. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Three channels, and the tee trap</h2>
''' + two + s1 + dx + qc('exit 300 is reported as?', '44 (300 mod 256).') + '''
</section>
'''

VAR = variations('Sixteen more exit-code and logging patterns. All were really run on our build machine.', [
    ('Exit codes', [
        dict(title='grep’s three codes', cmd="echo abc > f; grep -q b f; echo \"found: $?\"; grep -q z f; echo \"not found: $?\"; grep -q z nofile 2>/dev/null; echo \"error: $?\"", why='0, 1, 2.', expect='any'),
        dict(title='Signal exit codes', cmd="bash -c 'kill -TERM $$'; echo \"TERM: $?\"; bash -c 'kill -KILL $$'; echo \"KILL: $?\"", why='128+15, 128+9.', expect='any'),
        dict(title='! inverts a status', cmd="! grep -q root /etc/hostname && echo 'no root in hostname'", why='Useful in if.'),
        dict(title='Function return vs exit', cmd="f(){ return 4; }; f; echo \"function returned $?\"; ( exit 5 ); echo \"subshell exited $?\"", why='return for functions, exit for scripts.', expect='any'),
        dict(title='Every pipe status', cmd="true | false | true; echo \"${PIPESTATUS[*]}\"", why='Read it right away.'),
    ]),
    ('stdout and stderr', [
        dict(title='Only stderr to a file', cmd="{ echo result; echo problem >&2; } 2> err.txt; echo \"err.txt: $(cat err.txt)\"", why='Result still on screen.'),
        dict(title='Both into one pipe', cmd="{ echo result; echo problem >&2; } 2>&1 | wc -l", why='2>&1 before the pipe.'),
        dict(title='|& shortcut', cmd="{ echo result; echo problem >&2; } |& wc -l", why='Bash 4+: same as 2>&1 |.'),
        dict(title='Swap stdout and stderr', cmd="{ echo result; echo problem >&2; } 3>&1 1>&2 2>&3 | tr a-z A-Z", why='Only the message reaches the pipe.'),
    ]),
    ('Log lines', [
        dict(title='UTC timestamp', cmd="TZ=UTC date -d '2026-11-12 02:00 +0530' '+%FT%TZ'", why='ISO 8601 for servers.'),
        dict(title='Milliseconds', cmd="date -d '2026-11-12 02:00:00.123' '+%T.%3N'", why='%3N.'),
        dict(title='Only warnings and errors', setup=SS, cmd="cd ~/ops; LOG_LEVEL=WARN bin/import.sh data/orders.csv; echo \"exit $?\"", why='INFO hidden.', expect='any'),
        dict(title='Duration of a job', cmd="start=$(date -d '02:00:00' +%s); end=$(date -d '02:03:25' +%s); echo \"took $(( end - start )) s\"", why='Log how long it ran.'),
        dict(title='Mask a secret before logging', cmd="TOKEN=ghp_abcdefghij1234; echo \"using token ${TOKEN:0:4}****\"", why='Never log secrets.'),
    ]),
    ('Reading logs', [
        dict(title='Count by level', setup=SS, cmd="cd ~/ops; for d in 10 11; do LOG_NOW=\"2026-11-$d 02:00\" LOG_FILE=logs/j.log bin/import.sh data/orders.csv 2>/dev/null; done; grep -o '\\[[A-Z]*\\]' logs/j.log | sort | uniq -c", why='Quick health check.', expect='any'),
        dict(title='Last run only', setup=SS, cmd="cd ~/ops; for d in 10 11; do LOG_NOW=\"2026-11-$d 02:00\" LOG_FILE=logs/j.log bin/import.sh data/orders.csv 2>/dev/null; done; tac logs/j.log | sed '/start:/q' | tac", why='From the last start line to the end.', expect='any'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Exit codes and logs at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['cron', 'MAILTO'], 'blue', 8.6), '1. Cron jobs',
              'cron mails stderr to MAILTO and monitoring checks the exit code; a script with clear codes pages the right person.', ['job', '*exit code', 'alert']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['CI', 'steps'], 'green', 8.6), '2. CI pipelines',
    'Any non-zero exit fails the step; good log lines make the failed build readable.', ['step', '*non-zero', 'red build']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['systemd', 'journal'], 'amber', 8.6), '3. systemd services and timers',
    'stderr of a service goes straight into the journal; journalctl -u job -p err shows only failures.', ['service', '*stderr', 'journal']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ETL', 'codes'], 'violet', 8.6), '4. Data pipelines',
    'Airflow’s BashOperator fails a task on non-zero; a separate code for “bad data” lets the DAG retry only real outages.', ['task', '*exit 3', 'no retry']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ELK', 'grep'], 'red', 8.6), '5. Central logging',
    'Timestamped, levelled lines ship to Elasticsearch/Loki and become searchable dashboards.', ['line', '*fields', 'dashboard']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful patterns. All really run on our build machine.', [
    dict(level='b', title='Save and show $?', scenario='Debugging.', cmd="ls /nonexistent 2>/dev/null; rc=$?; echo \"rc=$rc\"", explain='Save first.', expect='any'),
    dict(level='b', title='Timestamped echo', scenario='Quick log.', cmd="echo \"$(date -d '2026-11-12 02:00' '+%F %T') [INFO] backup started\" >&2", explain='%F %T.'),
    dict(level='i', title='Run and report', scenario='Wrapper.', setup=SS, cmd="cd ~/ops; if bin/import.sh data/orders.csv 2>/dev/null; then echo OK; else echo \"FAILED ($?)\"; fi", explain='if on the command.', expect='any'),
    dict(level='i', title='All output to a log', scenario='Cron line.', setup=SS, cmd="cd ~/ops; bin/import.sh data/orders.csv >> logs/cron.log 2>&1; echo \"exit $?, log lines: $(wc -l < logs/cron.log)\"", explain='>> then 2>&1.', expect='any'),
    dict(level='a', title='Errors in the last log', scenario='Morning check.', setup=SS, cmd="cd ~/ops; LOG_FILE=logs/i.log bin/import.sh data/orders.csv 2>/dev/null; grep -E '\\[(WARN|ERROR)\\]' logs/i.log | cut -c1-70", explain='Filter levels.', expect='any'),
], extra=build_up('echo done → observable job', 'Riya rebuilds the job’s reporting step by step.', SS, [
    ("cd ~/ops; bash -c 'echo done' ; echo \"old job exit: $?\"", '1. The old way: always 0.'),
    ("cd ~/ops; bin/import.sh data/orders.csv 2>/dev/null; echo \"new job exit: $?\"", '2. A real exit code.'),
    ("cd ~/ops; bin/import.sh data/orders.csv 2>&1 | cut -c1-60", '3. Log lines with time and level.'),
    ("cd ~/ops; LOG_FILE=logs/import.log bin/import.sh data/orders.csv 2>/dev/null; tail -1 logs/import.log", '4. Saved to a file.'),
], cumulative=False, expect='any')) + VAR + which('Choosing the right channel.', [
    ('Result', 'stdout', 'Pipes, files.', 'stderr.'),
    ('Messages', 'stderr', 'Separate.', 'stdout.'),
    ('Success/failure', 'exit code', 'Machines read it.', 'Text.'),
    ('History', 'log file / journal', 'Searchable.', 'Screen only.'),
    ('Pipeline status', 'pipefail / PIPESTATUS', 'Correct.', '$? alone.'),
    ('Debug detail', 'LOG_LEVEL=DEBUG', 'On demand.', 'Always on.'),
]) + keys('Handy forms.', [
    ('exit 0 / 1 / 2 / 3', 'contract', 'documented'),
    ('rc=$?', 'save status', 'immediately'),
    ('echo "msg" >&2', 'message', 'stderr'),
    ("date '+%F %T'", 'timestamp', 'sortable'),
    ('job >> job.log 2>&1', 'capture all', 'cron'),
    ('logger -t job -p user.err "msg"', 'syslog', 'servers'),
]) + scriptit('run-and-log.sh', 'A wrapper that runs any command, logs start, end, duration and exit code, and passes the code on, so any job becomes observable without changing it.',
'''#!/usr/bin/env bash
set -uo pipefail
log() { echo "$(date -d "${LOG_NOW:-now}" '+%F %T') [$1] run: ${*:2}" >&2; }

run() {
  local start rc
  start=$(date +%s)
  log INFO "start: $*"
  "$@"; rc=$?
  if (( rc == 0 )); then log INFO "ok in $(( $(date +%s) - start ))s"
  else log ERROR "failed with exit $rc: $*"; fi
  return $rc
}

LOG_NOW='2026-11-12 02:00'
run ls /etc/hostname
run ls /nonexistent
echo "wrapper passed on: $?"''',
'<p>No set -e here: the wrapper must survive the failure to log it.</p>', expect='any') + puzzle_answer('<b>1.</b> In <code>import.sh | tee run.log</code>, <code>$?</code> is <code>tee</code>’s status (0). Use <code>set -o pipefail</code>, check <code>${PIPESTATUS[0]}</code>, or avoid the pipe: <code>import.sh &gt;&gt; run.log 2&gt;&amp;1</code>. <b>2.</b> The pipe carries only <b>stdout</b>; messages on stderr went straight to the screen (or cron’s mail). Add <code>2&gt;&amp;1</code> before the pipe. <b>3.</b> Any number from 0 to 255 is allowed; 0 is success, 1 and 2 are conventions, and your own codes such as 3 = “bad data” tell the caller <i>which</i> failure happened. Document them at the top of the script.') + qc('Where should a script’s warnings go?', 'stderr (and a log file / syslog), never stdout.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-arguments-done-right-getopts-and-validation/">Lesson 1.2</a> (exit 2 for usage) and <a href="../../../linux/05-redirection-and-pipes/01-standard-streams-stdin-stdout-stderr-and-file/">Linux Lesson 5.1</a> (streams).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
