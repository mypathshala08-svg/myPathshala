import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='03-files-and-directories', lesson='06-everyday-utilities-date-cal-bc-seq-sleep-time-watch', n='3.6',
    module_label='Module 3 · Working with files and directories',
    title='Everyday utilities: date, cal, bc, seq, sleep, time and watch',
    desc='date formats (%F %T %Y %m %d %H %M %S %A %B %s), date arithmetic with -d (+45 days, yesterday, @timestamps), time zones with TZ and -u, setting the clock; cal and ncal; bc with scale, powers, -l, number bases and decimal comparisons; seq with steps, -w, -s and -f; sleep, timeout, time (real/user/sys) and watch (-n, -d, -g). Each tool explained, then used by admins, DBAs, data engineers, developers, DevOps, QA and ML teams, with real outputs.',
    og_desc='Clock, calendar, calculator, counter, timer and stopwatch in the terminal: date, cal, bc, seq, sleep, time and watch with real outputs.',
    minutes=38, level='Beginner → Advanced',
    lead='A due date 45 days away, 18% GST, files numbered 001 to 100, a backup that should appear soon: each is one small command. This lesson explains date, cal, bc, seq, sleep, time and watch, and how every IT role uses them in scripts.',
    chips=['Tools by field', 'Which tool when?', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Small tools, big help (fixed date so the output is stable)
d='2026-11-06'
date -d "$d" '+%A, %d %B %Y'
date -d "$d +45 days" +%F
echo "scale=2; 1250*18/100" | bc
seq -s ' ' 1 5
seq -f 'test_%03g.csv' 1 3
time sleep 0.2
"""

RUN = dict(
    heading='Six tools in eight lines',
    intro='<p>The script formats a date, calculates a due date and GST, generates numbers and file names, and times a short sleep. Change the values and run again.</p>',
    code=MAIN,
    anno=[
        ("date -d \"$d\" '+%A, %d %B %Y'", 'A readable date: Friday, 06 November 2026.'),
        ('date -d "$d +45 days" +%F', 'The due date.'),
        ('echo "scale=2; 1250*18/100" | bc', '18% GST with two decimals.'),
        ("seq -f 'test_%03g.csv' 1 3", 'Formatted, numbered names.'),
        ('time sleep 0.2', 'real ≈ 0.2 s, CPU ≈ 0.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What is the due date?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what do the two lines print? Then run.',
             code="echo '7/2' | bc\necho 'scale=1; 7/2' | bc\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this prints minutes where the month should be. Fix the format.',
             code="date -d '2026-11-06 10:30' +%Y-%M-%d\n"),
        dict(label='4 · Your turn', hint='Print the numbers 10, 20 … 50 separated by commas.',
             code='seq -s, 10 10 50\n'),
        dict(label='5 · Challenge', hint='Print the last day of February 2028.',
             code="date -d '2028-03-01 -1 day' +%F\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: calendars, the clock and watch',
    intro='<p>cal is not installed on our build machine, and setting the clock needs root. Outputs are <b>typical</b> unless marked recorded.</p>',
    items=[
        dict(title='1 · Install and use cal', cmd='sudo apt install ncal; cal', output='   November 2026\nSu Mo Tu We Th Fr Sa\n 1  2  3  4  5  6  7\n 8  9 10 11 12 13 14\n15 16 17 18 19 20 21\n22 23 24 25 26 27 28\n29 30', note='Typical. Today is highlighted in the terminal. <code>ncal</code> prints the weekdays as rows instead.'),
        dict(title='2 · Clock and time sync status', cmd='timedatectl', output='               Local time: Fri 2026-11-06 10:30:00 IST\n           Universal time: Fri 2026-11-06 05:00:00 UTC\n                Time zone: Asia/Kolkata (IST, +0530)\nSystem clock synchronized: yes\n              NTP service: active', note='Typical on Ubuntu. Servers should show “synchronized: yes”.'),
        dict(title='3 · Set the clock by hand (test machines only)', cmd="sudo timedatectl set-ntp false; sudo date -s '2026-11-06 10:30:00'", output='Fri Nov  6 10:30:00 IST 2026', note='Typical. Turn sync back on afterwards: <code>sudo timedatectl set-ntp true</code>.'),
        dict(title='4 · Memory and time of a command', cmd='sudo apt install time; /usr/bin/time -v sort big.txt > /dev/null', output='\tCommand being timed: "sort big.txt"\n\tUser time (seconds): 0.41\n\tElapsed (wall clock) time (h:mm:ss or m:ss): 0:00.52\n\tMaximum resident set size (kbytes): 98304', note='Typical. The program /usr/bin/time (not bash’s time keyword) reports memory too.'),
        dict(title='5 · Versions on our build machine', cmd='date --version | head -1; bc --version | head -1; watch --version', output=pc('date --version | head -1; bc --version | head -1; watch --version'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Variables from the small tools',
    intro='<p>Step through a script that stores tool outputs in variables. Watch the <b>Shell</b> box fill up.</p>',
    code='''day=$(date -d '2026-11-06' +%F)
due=$(date -d "$day +45 days" +%F)
gst=$(echo "scale=2; 1250*0.18" | bc)
n=$(seq 1 5 | wc -l)
echo "invoice $day due $due gst $gst items $n"
''',
    notes={1: 'date :: The invoice date.', 2: 'Arithmetic :: 45 days later.', 3: 'bc :: Decimal tax.', 4: 'seq + wc :: Five items.', 5: 'Report :: Everything together.'},
)

WORKED_INTRO = 'Three tasks from real jobs: an accountant-style calculation, a DBA backup name with retention, and a DevOps wait loop.'
EXAMPLES = [
    dict(level='b', tag='Finance / data', title='Invoice total with GST',
         problem='<p>For an amount of ₹4,999, print the 18% GST and the total, both with two decimals.</p>',
         inp='amount = 4999',
         approach=['bc with scale=2.', 'printf for neat alignment.'],
         code='''amount=4999
gst=$(echo "scale=2; $amount*18/100" | bc)
total=$(echo "scale=2; $amount+$gst" | bc)
printf 'amount %10.2f\\ngst    %10.2f\\ntotal  %10.2f\\n' "$amount" "$gst" "$total"
''',
         notes={2: 'Tax :: 899.82.', 3: 'Total :: amount + tax.', 4: 'Layout :: printf aligns the numbers.'},
         tryit='Change the rate to 12%.'),
    dict(level='i', tag='DBA', title='Backup name and the cut-off date',
         problem='<p>Build tonight’s backup name and the date before which old backups may be deleted (keep 7 days).</p>',
         inp='today = 2026-11-06 (fixed here)',
         approach=['date +%F for the name.', 'date -d "-7 days" for the cut-off.'],
         code='''today=2026-11-06
name="mysql_$(date -d "$today" +%F).sql.gz"
cutoff=$(date -d "$today -7 days" +%F)
echo "tonight: $name"
echo "delete backups older than: $cutoff"
''',
         notes={2: 'Name :: Sortable date in the name.', 3: 'Cut-off :: Seven days earlier.'},
         tryit='Keep 30 days instead.'),
    dict(level='a', tag='DevOps', title='Retry with a growing pause',
         problem='<p>Try a flaky command up to 4 times, waiting 0.1, 0.2, 0.4 s between tries (exponential back-off). Here it succeeds on try 3.</p>',
         inp='a command that fails twice',
         approach=['seq for the tries.', 'bc for the doubling pause.'],
         code='''tries=0
flaky() { tries=$((tries+1)); [ "$tries" -ge 3 ]; }
pause=0.1
for i in $(seq 1 4); do
  if flaky; then echo "success on try $i"; break; fi
  echo "try $i failed, waiting ${pause}s"
  sleep "$pause"
  pause=$(echo "$pause*2" | bc)
done
''',
         notes={2: 'Demo :: Fails until the 3rd call.', 5: 'Try :: Stop at the first success.', 7: 'Wait :: Then double the pause with bc.'},
         tryit='Make it fail every time and see the loop end after 4 tries.'),
]

QUIZ = mix([
    dict(q='Which format prints 2026-11-06?', options=['+%Y-%M-%D', '+%F', '+%d-%m-%Y', '+%T'], answer=1,
         why='%F = %Y-%m-%d. %M is minutes.'),
    dict(q='How do you get the date 30 days ago?', options=["date -30", "date -d '30 days ago'", 'date --minus 30', 'cal -30'], answer=1,
         why='-d accepts relative dates.'),
    dict(q="echo '7/2' | bc prints…", options=['3.5', '3', '4', 'an error'], answer=1,
         why='Default scale is 0: whole numbers.'),
    dict(q='What does date +%s print?', options=['seconds of the minute', 'seconds since 1970 (UTC)', 'the time zone', 'nanoseconds'], answer=1,
         why='Unix time.'),
    dict(q='Which prints 01 02 … 10?', options=['seq 10', 'seq -w 1 10', 'seq -s 1 10', 'seq 0 10'], answer=1,
         why='-w pads to equal width.'),
    dict(q='time sleep 1 shows real 1.0, user 0.0. Why is user 0?', options=['A bug', 'Sleeping uses no CPU', 'time is wrong', 'user means kernel'], answer=1,
         why='real = wall clock; user/sys = CPU time used.'),
    dict(q='Which watch option highlights changes?', options=['-n', '-d', '-g', '-t'], answer=1,
         why='-d = differences.'),
    dict(q='Why can {1..$n} not be used for a variable range?', options=['n must be a file', 'Braces expand before variables', 'Braces need quotes', 'It works fine'], answer=1,
         why='Brace expansion happens first; use seq 1 "$n".'),
])

REVISION = [
    '<code>date +%F</code> (2026-11-06), <code>+%T</code>, <code>+%d-%m-%Y</code>; <b>%M = minutes, %m = month</b>.',
    "<code>date -d '+45 days'</code>, <code>yesterday</code>, <code>next monday</code>, <code>@1793941200</code>; <code>-u</code> UTC; <code>TZ=Zone date</code>; <code>-r file</code>.",
    'Set the clock: <code>sudo date -s</code> (tests), NTP/timedatectl (servers).',
    '<code>cal</code>, <code>cal 3 2026</code>, <code>cal -3</code>, <code>cal -y</code>, <code>ncal</code> (package ncal).',
    "bc: <code>echo 'scale=2; 10/3' | bc</code>; scale applies at every step; <code>-l</code> math; obase/ibase; comparisons 1/0.",
    '<code>seq FIRST STEP LAST</code>, <code>-w</code> pad, <code>-s,</code> join, <code>-f "x_%03g"</code> format; use with variables.',
    '<code>sleep 0.5 / 5m</code>, <code>timeout N cmd</code> (exit 124), <code>time cmd</code> real/user/sys.',
    '<code>watch -n 5 -d cmd</code>; <code>-g</code> exits on change; Ctrl+C stops.',
]

FAQ = [
    ('How do you display the date in YYYY-MM-DD format?', 'date +%F (same as date +%Y-%m-%d).'),
    ('How do you get yesterday’s date in Linux?', "date -d yesterday +%F (GNU date)."),
    ('How do you do decimal calculations in the shell?', "With bc: echo 'scale=2; 10/3' | bc. bash $(( )) only handles integers."),
    ('What is the difference between real, user and sys in time?', 'real is elapsed wall-clock time; user is CPU time in the program; sys is CPU time in the kernel for it.'),
    ('How do you run a command every few seconds?', 'watch -n SECONDS command (interactive), or a loop with sleep in scripts.'),
    ('What is seq used for?', 'Printing number sequences for loops, file names and test data, with steps, padding (-w) and formats (-f).'),
    ('How do you set the system date?', "sudo date -s 'YYYY-MM-DD HH:MM:SS' (or timedatectl set-time); on servers use NTP instead."),
]

PRACTICE_INTRO = 'Small tasks with the utilities. Expected outputs come from real runs on Ubuntu 24.04 (fixed dates).'
PROBLEMS = [
    dict(level='easy', title='Indian date format', stmt='Print 2026-11-06 as 06/11/2026.', inp='2026-11-06',
         code="date -d 2026-11-06 '+%d/%m/%Y'\n", explain='%d day, %m month, %Y year.'),
    dict(level='easy', title='Weekday', stmt='Which weekday is 15 August 2027?', inp='2027-08-15',
         code='date -d 2027-08-15 +%A\n', explain='%A full weekday name.'),
    dict(level='easy', title='Count to five', stmt='Print 1 to 5 on one line separated by spaces.', inp='—',
         code="seq -s ' ' 1 5\n", explain='-s sets the separator.'),
    dict(level='medium', title='Average', stmt='Average of 45, 67 and 89 with 2 decimals.', inp='45 67 89',
         code="echo 'scale=2; (45+67+89)/3' | bc\n", explain='Brackets first, then divide.'),
    dict(level='medium', title='90 days later', stmt='The date 90 days after 2026-11-06.', inp='2026-11-06',
         code="date -d '2026-11-06 +90 days' +%F\n", explain='Calendar arithmetic by date.'),
    dict(level='medium', title='Padded file names', stmt='Print img_001.png to img_003.png.', inp='—',
         code="seq -f 'img_%03g.png' 1 3\n", explain='%03g = 3 digits with zeros.'),
    dict(level='business', title='Days to a deadline', stmt='Days from 2026-11-06 to 2027-03-31.', inp='two dates',
         code="echo $(( ( $(date -d 2027-03-31 +%s) - $(date -d 2026-11-06 +%s) ) / 86400 ))\n", explain='Seconds difference / 86,400.'),
    dict(level='business', title='EMI-style power', stmt='₹50,000 growing 1% per month for 12 months, 2 decimals (calculate precisely).', inp='50000, 1%, 12',
         code="echo 'scale=10; x=50000*1.01^12; scale=2; x/1' | bc\n", explain='High scale while calculating, then /1 with scale=2 to round down to 2 decimals.'),
]

SCN_INTRO = 'Interview questions about these utilities, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Create a backup file with today’s date in the name.”',
        'The interviewer wants a command, not a script.',
        'do you know date formats and $( )?',
        '''<ul>
          <li><code>tar -czf "backup_$(date +%F).tar.gz" project/</code></li>
          <li>%F = YYYY-MM-DD: sortable, no spaces or slashes.</li>
          <li>For several per day: <code>+%F_%H%M</code>.</li>
        </ul>''', 'using %D (contains slashes, which are folder separators).') +
    scn('Operations · scripts', 'Junior', 'The monitoring check that never alerts',
        'A script has <code>if [ $load -gt 2 ]</code> with load = 3.45 and fails with “integer expression expected”.',
        'do you know shell arithmetic limits?',
        '''<ol>
          <li>bash tests and $(( )) are integer-only.</li>
          <li>Use bc: <code>[ "$(echo "$load > 2" | bc)" -eq 1 ]</code>, or awk.</li>
          <li>Test the alert path with a fake high value.</li>
        </ol>''', 'cutting the decimals off and hoping.') +
    scn('Global team · DevOps', 'Mid-level', 'Logs that do not line up',
        'Servers in Mumbai and Frankfurt log local time; incident timelines are confusing, and once a year an hour repeats.',
        'do you understand time zones?',
        '''<ul>
          <li>Log in UTC everywhere (<code>date -u</code>, ISO 8601 with offset), convert only for display.</li>
          <li>Europe has daylight saving: local time repeats an hour in autumn; IST does not change.</li>
          <li>Keep clocks synced with NTP (<code>timedatectl</code>, chrony).</li>
        </ul>''', '“we will add 3.5 hours by hand”.') +
    scn('Platform · reliability', 'Senior', 'The deploy that hung for six hours',
        'A pipeline waits for a health file with <code>while [ ! -e ok ]; do sleep 5; done</code>; the service never started.',
        'do you design waits with limits?',
        '''<ul>
          <li>Every wait needs a deadline: <code>timeout 300 bash -c 'until …; do sleep 5; done'</code> and handle exit 124.</li>
          <li>Back-off for retries; log timestamps; fail fast with a clear message.</li>
          <li>Measure normal start time with <code>time</code> to choose the limit.</li>
        </ul>''', 'removing the check so the pipeline “passes”.')
) + interview([
    ('Print today’s date as DD-MM-YYYY.', "date '+%d-%m-%Y'."),
    ('Difference between %m and %M?', '%m is the month (01–12); %M is minutes (00–59).'),
    ('How do you convert a Unix timestamp to a date?', 'date -d @TIMESTAMP (GNU).'),
    ('Why does echo 10/3 | bc print 3?', 'scale is 0 by default; set scale=2 for decimals.'),
    ('How do you run a command every 5 seconds and highlight changes?', 'watch -n 5 -d command.'),
    ('What do real, user and sys mean?', 'Elapsed time; CPU time in user space; CPU time in the kernel.'),
    ('How do you stop a command that runs too long?', 'timeout SECONDS command (exit status 124 when it times out).'),
], [
    ('RHCSA (EX200)', '“Configure time service clients” (chrony, timedatectl) and essential command-line tools.'),
    ('LFCS', 'Operations: maintain system time (NTP, time zones) and use shell utilities in scripts.'),
    ('CompTIA Linux+', 'Time and date management (date, timedatectl, NTP) and basic shell utilities.'),
]) + distro('date, seq and watch differ most between GNU and BSD.', [
    ("date -d '+45 days'", 'yes (GNU)', 'yes', "no: date -v+45d", 'yes'),
    ('date -d @TS', 'yes', 'yes', 'date -r TS', 'yes'),
    ('cal', 'install ncal', 'util-linux cal (installed)', 'yes', 'WSL: install ncal; Git Bash: no'),
    ('bc', 'installed', 'install bc on minimal', 'installed', 'WSL yes; Git Bash: no'),
    ('seq -w / -f', 'yes', 'yes', 'yes (macOS has seq)', 'yes'),
    ('watch', 'procps (installed)', 'installed', 'brew install watch', 'WSL yes; Git Bash: no'),
    ('timedatectl', 'yes', 'yes', 'no: systemsetup', 'WSL: only with systemd'),
]) + teaser('3.7', 'Riya has 300 photos called IMG 0001.JPEG … with spaces and capital letters. She needs img_0001.jpg … in lowercase with underscores. mv works one file at a time. Which command renames all 300 in one line, and how can she preview it first?')

CHEATSHEET = cheatsheet('everyday utilities', [
    ('date: print', [('date +%F', '2026-11-06'), ("date '+%d-%m-%Y %H:%M'", '06-11-2026 10:30'), ('date +%T / +%A', 'time / weekday'), ('date +%s', 'Unix time'), ('date -u', 'UTC')]),
    ('date: calculate', [("date -d '+45 days' +%F", 'future'), ("date -d yesterday", 'past'), ('date -d @1793941200', 'from timestamp'), ('date -r file', 'file time'), ('TZ=Europe/London date', 'other zone')]),
    ('cal · bc', [('cal / cal -3', 'month / 3 months'), ('cal 3 2026 · cal -y', 'month / year'), ("echo 'scale=2; 10/3' | bc", '3.33'), ("echo 'sqrt(2)' | bc -l", 'math lib'), ("echo 'obase=2; 10' | bc", 'binary')]),
    ('seq', [('seq 5', '1..5'), ('seq 2 2 10', 'step 2'), ('seq -w 8 12', '08..12'), ('seq -s, 1 5', '1,2,3,4,5'), ("seq -f 'f_%03g' 1 3", 'f_001…')]),
    ('sleep · time · watch', [('sleep 0.5 / 2m', 'wait'), ('timeout 10 cmd', 'limit (124)'), ('time cmd', 'real user sys'), ('watch -n 5 -d cmd', 'repeat + highlight'), ('watch -g cmd', 'exit on change')]),
])

MINDMAP = mindmap('Everyday utilities', [
    ('date', 'blue', ['+%F +%T, %m≠%M', "-d '+45 days', @ts", '-u, TZ=, -r file']),
    ('cal', 'green', ['cal, cal -3, -y', 'ncal vertical', 'package ncal']),
    ('bc', 'amber', ['scale = decimals', 'high scale for ^', '-l, obase, a>b']),
    ('seq', 'violet', ['FIRST STEP LAST', '-w -s -f', 'works with $vars']),
    ('Wait', 'red', ['sleep 0.5 / 5m', 'timeout → 124', 'until …; sleep']),
    ('Measure', 'acc', ['time: real user sys', 'watch -n -d -g', '/usr/bin/time -v']),
])

LAB = lab('prepare an invoice run', 'Build the lab, do the four tasks in your own terminal, then run the checker. Use the fixed date 2026-11-06.',
    setup='''mkdir -p ~/lab36 && cd ~/lab36 && rm -rf out
mkdir out''',
    tasks=['Write the date 45 days after 2026-11-06 (YYYY-MM-DD) into <code>out/due.txt</code>.',
           'Write 18% of 2499 with two decimals into <code>out/gst.txt</code>.',
           'Create files <code>out/inv_001.txt</code> to <code>out/inv_010.txt</code>.',
           'Write the weekday name of 2026-11-06 into <code>out/day.txt</code>.'],
    solution='''date -d '2026-11-06 +45 days' +%F > out/due.txt
echo 'scale=2; 2499*18/100' | bc > out/gst.txt
for f in $(seq -f 'out/inv_%03g.txt' 1 10); do touch "$f"; done
date -d 2026-11-06 +%A > out/day.txt''',
    check='''cd ~/lab36
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 due date"      '[ "$(cat out/due.txt 2>/dev/null)" = 2026-12-21 ]'
ok "2 GST"           '[ "$(cat out/gst.txt 2>/dev/null)" = 449.82 ]'
ok "3 ten invoices"  '[ "$(ls out/inv_0*.txt 2>/dev/null | wc -l)" -eq 10 ] && [ -e out/inv_010.txt ]'
ok "4 weekday"       '[ "$(cat out/day.txt 2>/dev/null)" = Friday ]' ''')
