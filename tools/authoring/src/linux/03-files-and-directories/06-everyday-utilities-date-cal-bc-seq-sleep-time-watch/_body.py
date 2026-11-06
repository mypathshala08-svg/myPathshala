import os, sys, calendar
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# cal is not installed on our build machine: its layout is generated here and shown as typical output.
_C = calendar.TextCalendar(6)
def CAL(m, y):
    return _C.formatmonth(y, m).rstrip('\n')
def CAL3(m, y):
    ms = [((m - 2) % 12 + 1, y - (m == 1)), (m, y), (m % 12 + 1, y + (m == 12))]
    blocks = [_C.formatmonth(yy, mm).rstrip('\n').split('\n') for mm, yy in ms]
    h = max(len(b) for b in blocks)
    return '\n'.join('  '.join(b[i].ljust(20) if i < len(b) else ' ' * 20 for b in blocks).rstrip() for i in range(h))

D = "d='2026-11-06 10:30:00'"

HOOK = hook('Every day, small questions interrupt real work: “What date is 45 days from today?” “18% GST on ₹1,250?” “I need test files numbered 001 to 100.” “Tell me when the backup file appears.” Opening a calendar, a calculator and a spreadsheet takes minutes. In the terminal each one is a single short command, and it can go straight into a script.',
    ['print and calculate dates in any format, time zone or Unix timestamp (<code>date</code>), and show calendars (<code>cal</code>)',
     'calculate with decimals, powers and number bases (<code>bc</code>), and know why scale matters for money',
     'generate number sequences for files and loops (<code>seq</code>)',
     'pause, measure and repeat commands (<code>sleep</code>, <code>time</code>, <code>watch</code>)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'six small questions'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'What the tools are', 5, 'simple meaning + 4 depths'),
    ('commands', 'Each tool, by field', 15, 'options, real runs, your field'),
    ('errors', 'Errors decoded', 3, 'what each message means'),
    ('animation', 'See it happen', 4, 'a date in four forms'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'do it yourself, auto-checked'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Today’s date in a file name', 'date +%F', '2026-11-06'),
    ('A date in the future or past', "date -d '+45 days' +%F", 'also yesterday, next monday'),
    ('Seconds since 1970 (timestamps)', 'date +%s', 'and back: date -d @1793941200'),
    ('The same time in another country', "TZ=America/New_York date", 'time zones'),
    ('A month on screen', 'cal  /  cal 3 2026  /  cal -3', 'needs the ncal package'),
    ('A sum with decimals', "echo 'scale=2; 1250*18/100' | bc", 'bash $(( )) = whole numbers only'),
    ('Numbers 1 to 100', 'seq 1 100', 'padded: seq -w, format: seq -f'),
    ('Wait before the next step', 'sleep 5', '5s, 2m, 0.5'),
    ('How long does a command take?', 'time command', 'real, user, sys'),
    ('Re-run a command every 2 s and watch', 'watch -n 2 command', 'Ctrl+C to stop'),
])

cmap = concept_map(
    [('3.1', 'Creating files', 'dated names like report_$(date +%F)'), ('3.4', 'Braces', '{01..12} vs seq'), ('3.5', 'Viewing files', 'watch tail, wc')],
    ['date: formats, past and future, time zones, Unix time, setting the clock', 'cal and ncal: calendars', 'bc: decimals, scale, powers, bases', 'seq: sequences with steps, padding and formats', 'sleep, time and watch: wait, measure, repeat'],
    [('5.4', 'Chaining and $( )', 'use their output in other commands'), ('12.5', 'Shell scripts', 'loops with seq and sleep'), ('17.4', 'cron', 'run things on a schedule'), ('18.3', 'Monitoring', 'watch, top, uptime')],
    'These small tools appear in almost every script: dated backups, waiting loops, test data and quick calculations.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 316, 156, ["$ date -d '+45 days' +%F", ('2026-12-21', 'acc'), "$ echo 'scale=2; 1250*18/100' | bc", ('225.00', 'acc'), '$ seq -w 1 100 | head -3', ('001', 'out'), ('002', 'out'), ('003', 'out')], title='riya@laptop: ~', size=7.4, step=15)
      + t(352, 36, 'Six questions, six tools:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• date: any date, any format', '• cal: the month on screen', '• bc: calculator', '• seq: numbers 1…N', '• sleep, time, watch'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Six small questions before lunch</h2>
  <div class="story">
''' + puzzle('Riya calculates ₹1,00,000 at 7% for 5 years with <code>echo "scale=2; 100000*1.07^5" | bc</code> and gets <b>140000.00</b>. A spreadsheet says 1,40,255.17. Is bc broken? Which number is right, and why?') + '''
    <p class="narration">Riya’s morning: the payment due date is 45 days from today, an invoice needs 18% GST, the testers want files numbered 001–100, and a backup should appear in a folder “some time soon”.</p>
''' + scene('A terminal: date -d +45 days prints 2026-12-21, bc calculates 225.00 GST, seq -w prints 001 002 003.', sc,
            'Small tools, used <tspan font-weight="700" class="s-acc">inside every script</tspan>.') + '''
A> Each of those is one command. <code>date</code> calculates dates, <code>bc</code> calculates with decimals, <code>seq</code> counts, <code>watch</code> repeats a command so you can see the backup arrive.
R> Can’t bash calculate by itself?
K> Only whole numbers: <code>$((1250*18/100))</code> gives 225, but <code>$((10/3))</code> gives 3. For money you need bc.
A> Today: <code>date</code>, <code>cal</code>, <code>bc</code>, <code>seq</code>, <code>sleep</code>, <code>time</code> and <code>watch</code>, each explained, then used by admins, DBAs, data engineers, developers, DevOps and testers.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="An office desk: a wall clock and calendar (date, cal), a calculator (bc), a number stamp (seq), an egg timer (sleep), a stopwatch (time) and a security camera screen refreshing (watch).">'
       + ''.join(label_box(12 + k * 105, 22, 96, 100, [a, b, c], tone, 8.8) for k, (a, b, c, tone) in enumerate([
           ('date', 'wall clock', 'any date', 'blue'), ('cal', 'wall calendar', 'months', 'green'), ('bc', 'calculator', 'decimals', 'amber'),
           ('seq', 'number stamp', '1, 2, 3 …', 'violet'), ('sleep · time', 'egg timer ·', 'stopwatch', 'card'), ('watch', 'CCTV screen', 'refreshes', 'red')]))
       + t(320, 152, 'The office tools you reach for all day,', 9.6, 'ink2')
       + t(320, 174, 'each as one command you can also put in a script.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Everyday utilities at four depths', [
    ('v', 'No jargon: the office desk', '      <p>Think of the things on an office desk.</p>' + pic + '''
      <ul>
        <li><code>date</code> is the clock, <code>cal</code> the wall calendar, <code>bc</code> the calculator.</li>
        <li><code>seq</code> stamps numbers one after another; <code>sleep</code> waits; <code>time</code> is a stopwatch.</li>
        <li><code>watch</code> is like a CCTV screen: it shows the same view again every few seconds.</li>
      </ul>'''),
    ('b', 'The commands you will type every day', '''      <ul>
        <li><code>date</code> now; <code>date +%F</code> = 2026-11-06; <code>date '+%d-%m-%Y'</code> = 06-11-2026.</li>
        <li><code>cal</code> this month, <code>cal 2026</code> the whole year.</li>
        <li><code>echo '2+3*4' | bc</code> = 14; with decimals: <code>echo 'scale=2; 10/3' | bc</code> = 3.33.</li>
        <li><code>seq 5</code> prints 1–5, one per line; <code>seq 2 2 10</code> = 2 4 6 8 10.</li>
        <li><code>sleep 5</code> waits 5 seconds; <code>time cmd</code> measures; <code>watch -n 2 ls</code> repeats ls every 2 s (Ctrl+C stops).</li>
      </ul>'''),
    ('i', 'Formats, arithmetic and the traps', '''      <ul>
        <li>Format codes: <code>%Y %m %d %H %M %S</code>, <code>%F</code> = %Y-%m-%d, <code>%T</code> = %H:%M:%S, <code>%A %B</code> names, <code>%s</code> Unix time. <b>Capital M is minutes</b>, lower m is month.</li>
        <li><code>date -d</code> understands “+45 days”, “yesterday”, “next monday”, “2026-11-06 -30 days”, “@1793941200”.</li>
        <li>bc’s <code>scale</code> = digits after the point, applied at <b>every</b> step: use a high scale for money and powers, round at the end. <code>bc -l</code> sets scale 20 and adds sqrt, sine, log.</li>
        <li><code>seq -w</code> pads to equal width, <code>-s,</code> joins with commas, <code>-f "file_%03g.txt"</code> formats each number.</li>
        <li><code>time</code> reports <b>real</b> (wall clock), <b>user</b> and <b>sys</b> (CPU time in your code / in the kernel).</li>
      </ul>'''),
    ('a', 'Behind the screen: clocks and time zones', '''      <ul>
        <li>Linux keeps time as seconds since 1 Jan 1970 00:00 UTC (the <b>Unix epoch</b>). Time zones are only applied when printing: <code>TZ=Asia/Kolkata</code> reads rules from <code>/usr/share/zoneinfo</code>.</li>
        <li>Setting the clock (<code>sudo date -s</code>) changes the system clock; servers use NTP instead (<code>timedatectl</code>, chrony, Lesson 16.7) because a wrong clock breaks logs, TLS certificates and Kerberos.</li>
        <li>32-bit signed timestamps overflow on 19 January 2038 (the “Y2038 problem”); 64-bit Linux uses 64-bit time.</li>
        <li><code>time</code> in bash is a <b>keyword</b> (it can time a whole pipeline; <code>TIMEFORMAT</code> changes its output); <code>/usr/bin/time -v</code> is a separate program that also reports memory (install the <code>time</code> package).</li>
        <li><code>sleep</code> uses the kernel’s high-resolution timers (<code>clock_nanosleep</code>), so <code>sleep 0.2</code> works.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>date, cal, bc, seq, sleep, time and watch</h2>
''' + def_block(
    '<code>date</code> prints the current or a given date and time in any format, converts between formats and time zones, and (as root) sets the system clock. <code>cal</code> displays a calendar. <code>bc</code> (basic calculator) is an arbitrary-precision calculator language. <code>seq</code> prints a sequence of numbers. <code>sleep</code> pauses for a given time. <code>time</code> reports how long a command took. <code>watch</code> runs a command repeatedly and shows its output full-screen.',
    'Clock, calendar, calculator, counter, timer, stopwatch and a screen that refreshes itself.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Format string', 'The <code>+%F %T</code> part telling date how to print.'),
    ('Unix time / epoch', f'Seconds since 1970-01-01 00:00 UTC. {gl("unix-epoch-and-timestamps", "Glossary →")}'),
    ('Time zone', 'Local offset from UTC, e.g. IST = UTC+05:30.'),
    ('scale (bc)', 'How many digits after the decimal point.'),
    ('Command substitution', f'<code>$(date +%F)</code> puts output into a command. {gl("command-substitution", "Glossary →")}'),
    ('real / user / sys', 'Wall-clock time / CPU in the program / CPU in the kernel.'),
    ('NTP', 'Network Time Protocol: keeps clocks correct.'),
    ('Exit status', f'0 = success; timeout gives 124. {gl("exit-status", "Glossary →")}'),
]) + '\n' + names('Where the names come from.', [
    ('date', 'date (and time)', 'Prints both.'),
    ('cal / ncal', 'calendar / new calendar', 'ncal prints months vertically.'),
    ('bc', 'basic calculator', 'From 1975 Unix; today GNU bc.'),
    ('seq', 'sequence', 'Counts from A to B.'),
    ('sleep', 'sleep', 'The process sleeps.'),
    ('time', 'time', 'A stopwatch for commands.'),
    ('watch', 'watch', 'Keep watching the output.'),
    ('%F / %T', 'Full date / Time', 'Two shortcuts worth remembering.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Date for file names', '<code>date +%F</code> → 2026-11-06'),
    ('Indian format', "<code>date '+%d-%m-%Y'</code> → 06-11-2026"),
    ('In 45 days', "<code>date -d '+45 days' +%F</code>"),
    ('Calculator', "<code>echo 'scale=2; 10/3' | bc</code> → 3.33"),
    ('Numbers', '<code>seq -w 1 100</code> → 001 … 100'),
    ('Repeat every 5 s', '<code>watch -n 5 df -h</code>'),
]) + '\n' + lv + didyou('India uses one time zone for the whole country, IST (UTC+05:30), a half-hour offset. In Linux it is called <code>Asia/Kolkata</code>; older systems used <code>Asia/Calcutta</code>, which still works as an alias, because time zone names follow city names, not countries.') + '''
EXAM> “How do you print the date as YYYY-MM-DD and get yesterday’s date?” → date +%F (or +%Y-%m-%d); date -d yesterday +%F; mention %M is minutes and %m is month, date -s to set the time (root), and NTP for servers.
''' + qc('What does <code>date +%Y-%M-%D</code> print, and what should it be?', 'It mixes up codes: %M is minutes and %D is mm/dd/yy (a real run printed <code>2026-30-11/06/26</code>). Use <code>+%Y-%m-%d</code> or simply <code>+%F</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The date format codes you will actually use</h2>
''' + table(['Code', 'Meaning', 'Example (2026-11-06 10:30)'], [
    ['<code>%Y</code> / <code>%y</code>', 'year, 4 / 2 digits', '2026 / 26'],
    ['<code>%m</code>', 'month 01–12', '11'],
    ['<code>%d</code>', 'day of month 01–31', '06'],
    ['<code>%H</code> / <code>%I %p</code>', 'hour 00–23 / 01–12 AM PM', '10 / 10 AM'],
    ['<code>%M</code>', '<b>minutes</b> 00–59 (not month!)', '30'],
    ['<code>%S</code>', 'seconds', '00'],
    ['<code>%F</code> · <code>%T</code>', '%Y-%m-%d · %H:%M:%S', '2026-11-06 · 10:30:00'],
    ['<code>%A %a</code> · <code>%B %b</code>', 'weekday · month name (full, short)', 'Friday Fri · November Nov'],
    ['<code>%j</code> · <code>%u</code> · <code>%U</code>', 'day of year · weekday 1–7 · week number', '310 · 5 · 44'],
    ['<code>%Z %z</code>', 'time zone name, offset', 'IST +0530'],
    ['<code>%s</code>', 'seconds since 1970 (UTC)', '1793941200'],
    ['<code>%N</code>', 'nanoseconds', 'for precise timing'],
], minw=520) + mistake("date -u +'%Y-%M-%D %H:%M:%S'", "date -u +'%Y-%m-%d %H:%M:%S'   (or date -u '+%F %T')",
                       'A common note writes %M (minutes) and %D (mm/dd/yy) where %m (month) and %d (day) are meant. The result looks like a date but is wrong.') + mistake('date +"%H:%M:%S"   described as “without the colon separator”', 'date +"%H:%M:%S"  =  date +%T   (both print 10:30:00, with colons)',
                       'The colons in the format string are printed as they are; %T is the short form of the same thing.') + qc('Which single code gives 2026-11-06?', '<code>%F</code>') + '''
</section>
'''

# ---------------------------------------------------------------- 4. commands
cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each tool explained, then used in every field</h2>
  <p id="commands">Most date examples use a fixed moment, <code>d='2026-11-06 10:30:00'</code> (IST), so the outputs stay the same whenever you read this. All outputs were recorded on Ubuntu 24.04, except <code>cal</code>, which our build machine does not have (shown as typical output).</p>
''' + cmdcard_u(['file and folder names with dates', 'log lines, reports, deadlines', 'converting time zones and Unix timestamps'],
               ['measuring how long something takes (use time)', 'setting the clock on servers (use NTP / timedatectl)'])(
    'date', 'date', 'date and time',
    'Prints the date and time now, or any date you give with <code>-d</code>, in any format after a <code>+</code>. As root it can set the clock.',
    "date [-d 'DATE'] [-u] [+FORMAT]   ·   sudo date -s 'DATE'", 'safe',
    [('+FORMAT', 'print in this format (see the table above)', 'file names, reports'),
     ("-d 'STRING'", 'use this date: “+45 days”, “yesterday”, “next monday”, “@1793941200”', 'deadlines, “30 days ago”'),
     ('-u', 'show UTC instead of local time', 'servers, logs, APIs'),
     ('-r FILE', 'the modification time of a file', 'when was it changed?'),
     ('--iso-8601=seconds / -R', 'standard formats (ISO, email)', 'APIs, emails'),
     ("TZ='Zone' date", 'the time in another time zone', 'teams abroad'),
     ("sudo date -s '2026-11-06 10:30'", 'set the system clock (root)', 'test machines only'),
     ('sudo date MMDDhhmmCCYY.ss', 'old compact way to set the clock', 'legacy scripts')],
    dict(cmd=D + "\ndate -d \"$d\"\ndate -d \"$d\" +%F\ndate -d \"$d\" '+%d-%m-%Y %H:%M'\ndate -d \"$d\" '+%A, %B %d, %Y'", note='One moment, four formats. Without <code>-d</code> you get the current time.'),
    [('sys', [
        dict(situation='Name a backup file with today’s date and time (sortable).', cmd='touch "backup_$(date +%F_%H%M).tar.gz" && ls backup_* | sed -E "s/[0-9]{4}\\.tar/HHMM.tar/"',
             why='%F_%H%M sorts correctly by name. (The time part is masked here because it changes every run.)'),
        dict(situation='What time is it on the UTC server log vs in India?', cmd=D + "\ndate -d \"$d\" '+%F %T %Z'\ndate -u -d \"$d IST\" '+%F %T %Z'",
             why='The same moment: 10:30 in India is 05:00 UTC. Note <code>$d IST</code>: without a zone, <code>date -u -d</code> would read 10:30 itself as UTC. Servers usually log in UTC; always check which one a log uses.')]),
     ('data', [
        dict(situation='The date 30 days before a report date, for a WHERE clause.', cmd="date -d '2026-11-06 -30 days' +%F",
             why='date does the calendar arithmetic (month lengths, leap years) for you.'),
        dict(situation='How many days until a deadline?', cmd="echo $(( ( $(date -d 2026-12-25 +%s) - $(date -d 2026-11-06 +%s) ) / 86400 )) days",
             why='Convert both to seconds (%s), subtract, divide by 86,400 seconds per day.')]),
     ('dev', [
        dict(situation='Convert a Unix timestamp from an API or database into a readable date.', cmd="date -d @1793941200\ndate -u -d @1793941200 --iso-8601=seconds",
             why='<code>@</code> means “seconds since 1970”. APIs often use these; ISO 8601 is the standard text form.')]),
     ('devops', [
        dict(situation='A meeting at 10:30 IST: what time is it for the team in New York and London?', cmd=D + "\nTZ=America/New_York date -d \"$d IST\" '+%F %T %Z'\nTZ=Europe/London date -d \"$d IST\" '+%F %T %Z'",
             why='TZ changes the zone just for this command. (Summer time changes these offsets; date knows the rules.)')]),
     ('dba', [
        dict(situation='When was this dump last modified?', cmd="touch -d '2026-11-05 23:00' night.sql\ndate -r night.sql '+%F %T'",
             why='<code>-r</code> reads a file’s modification time: quick check that last night’s backup really ran.')]),
     ('qa', [
        dict(situation='Validate dates in test data: is 30 February a real date?', cmd="date -d '2026-02-30' +%F 2>&1; date -d '2028-02-29' +%F",
             why='date rejects impossible dates and knows leap years (2028 is one).', expect='any')]),
    ],
    anat=anatomy([('date', 'cmd', 'command'), ("-d '+45 days'", 'opt', 'which date'), ("'+%d-%m-%Y'", 'arg', 'format (starts with +)')], 'The format must start with <code>+</code>; quote it when it contains spaces.')
) + mistake("date -d '2026-11-06 10:30:00 +45 days'", "date -d '2026-11-06 +45 days'   (or date -d '+45 days' for today)",
            'After a time, <code>+45</code> is read as a time zone offset, so a real run fails with “invalid date”. Leave out the time, or write “45 days” after it.') + cmdcard_u(['you want to see a month or a year at a glance', 'checking which weekday a date falls on', 'planning: previous, current and next month'],
               ['scripts that need dates (use date)', 'the cal command is missing (install ncal)'])(
    'cal', 'cal · ncal', 'calendar',
    'Prints a calendar for the current month, a given month, or a whole year. On Ubuntu it comes from the <code>ncal</code> package (<code>sudo apt install ncal</code>); our build machine does not have it, so outputs are typical.',
    'cal [-3 | -y] [[MONTH] YEAR]   ·   ncal', 'safe',
    [('cal', 'this month (today highlighted)', 'quick look'),
     ('cal 3 2026', 'March 2026', 'a specific month'),
     ('cal 2026 / cal -y', 'a whole year', 'planning'),
     ('cal -3', 'previous, this and next month', 'scheduling'),
     ('cal -3 3 2026', 'Feb, Mar, Apr 2026', 'around a date'),
     ('ncal', 'months shown vertically (weekdays as rows)', 'alternative layout'),
     ('ncal -w', 'with week numbers', 'sprint planning')],
    dict(cmd='cal 11 2026', rec=('Typical output (Ubuntu with ncal installed)', CAL(11, 2026)), note='November 2026 starts on a Sunday; 6 November is a Friday.'),
    [('sys', [
        dict(situation='Plan a maintenance window: see last, this and next month.', cmd='cal -3 11 2026', typical=CAL3(11, 2026),
             why='Three months side by side; weekends are easy to spot.')]),
     ('qa', [
        dict(situation='Which weekday is 31 March 2026 (end of the financial year)?', cmd='cal 3 2026', typical=CAL(3, 2026),
             why='31 March 2026 is a Tuesday. (In scripts: <code>date -d 2026-03-31 +%A</code>.)')]),
     ('devops', [
        dict(situation='The same answer inside a script, without cal.', cmd="date -d 2026-03-31 +%A",
             why='date is installed everywhere and gives text that scripts can use; cal is for people.')]),
    ]
) + cmdcard_u(['decimals: money, percentages, averages', 'powers, square roots, number bases', 'quick calculations at the terminal or in scripts'],
               ['whole numbers only (bash <code>$(( ))</code> is enough and faster)', 'big data sets (use awk, Python or a database)'])(
    'bc', 'bc', 'basic calculator',
    'A calculator language: give it an expression (usually through <code>echo … |</code>) and it prints the result. It is exact with any number of digits; <code>scale</code> sets the digits after the decimal point.',
    "echo 'EXPRESSION' | bc [-l]", 'safe',
    [('+ - * / % ^', 'add, subtract, multiply, divide, remainder, power', 'any calculation'),
     ('scale=N', 'N digits after the point (default 0)', 'money: scale=2 at the end'),
     ('-l', 'math library: scale 20, s() c() a() l() e()', 'sqrt, log, trigonometry'),
     ('sqrt(x)', 'square root', 'statistics'),
     ('obase=2 / ibase=16', 'output / input number base', 'binary, hex'),
     ('a > b', 'comparisons give 1 (true) or 0', 'decimal tests in scripts'),
     ('bc -q', 'interactive, no banner; quit to exit', 'a calculator session')],
    dict(cmd="echo '1250*18/100' | bc\necho 'scale=2; 1250*18/100' | bc\necho 'scale=2; 10/3' | bc\necho '10/3' | bc", note='Without scale bc gives whole numbers (10/3 = 3).'),
    [('data', [
        dict(situation='Average marks of a class, with two decimals.', cmd="echo 'scale=2; (91+78+85+66)/4' | bc",
             why='Integer arithmetic would give 80 and hide the .00 vs .75 difference.')]),
     ('dba', [
        dict(situation='Convert 734003200 bytes into GB for a report.', cmd="echo 'scale=2; 734003200/1024^3' | bc",
             why='1 GiB = 1024³ bytes. 0.68 GB.')]),
     ('dev', [
        dict(situation='Convert numbers between decimal, binary and hex.', cmd="echo 'obase=2; 10' | bc\necho 'ibase=16; FF' | bc\necho 'obase=16; 255' | bc",
             why='Handy for permissions, bit masks and colours. Set obase before ibase if you change both.')]),
     ('ml', [
        dict(situation='Square root for a standard deviation step.', cmd="echo 'sqrt(2)' | bc -l\necho 'scale=4; sqrt(2)' | bc -l",
             why='-l loads the math library and sets scale 20; reset scale for shorter output.')]),
     ('devops', [
        dict(situation='Alert if CPU load (a decimal) is above 1.5; bash [ ] cannot compare decimals.', cmd="load=1.82\nif [ \"$(echo \"$load > 1.5\" | bc)\" -eq 1 ]; then echo \"ALERT: load $load\"; fi",
             why='bc prints 1 for true. bash <code>[ 1.82 -gt 1.5 ]</code> would fail with “integer expression expected”.')]),
     ('qa', [
        dict(situation='Compound interest: why scale must be high during the calculation.', cmd="echo 'scale=2; 100000*1.07^5' | bc\necho 'scale=10; 100000*1.07^5' | bc",
             why='bc cuts to <code>scale</code> digits at every multiplication of the power, so scale=2 loses money. Calculate with a high scale, round only for display.')]),
    ]
) + mistake("echo 'scale=2; 100000*1.07^5' | bc     →  140000.00", "echo 'scale=10; 100000*1.07^5' | bc   →  140255.1730700000",
            'scale is applied to intermediate results too. For money: high scale while calculating, round at the end (for example with printf "%.2f").') + cmdcard_u(['numbers for loops, file names and test data', 'steps (every 5th), countdowns, decimals', 'padding and formats: 001, file_007.txt'],
               ['a fixed, small range typed by hand (braces {1..10} are simpler)', 'the end comes from a variable and you use braces ({1..$n} does not work; seq does)'])(
    'seq', 'seq', 'sequence',
    'Prints numbers from a start to an end, one per line, with an optional step. Unlike braces, the limits can come from variables.',
    'seq [OPTION]... [FIRST [STEP]] LAST', 'safe',
    [('seq 5', '1 to 5', 'simple counting'),
     ('seq 2 10', '2 to 10', 'a range'),
     ('seq 2 2 10', '2 to 10 in steps of 2', 'every n-th'),
     ('seq 10 -3 1', 'counting down', 'countdowns'),
     ('-w', 'equal width with leading zeros', '08 09 10'),
     ('-s STR', 'separator instead of newline', '1,2,3'),
     ('-f FORMAT', 'printf-style format per number', 'file_%03g.txt'),
     ('seq 0.5 0.5 2', 'decimal steps', 'thresholds')],
    dict(cmd="seq 5 | tr '\\n' ' '; echo\nseq 2 2 10 | tr '\\n' ' '; echo\nseq -w 8 12 | tr '\\n' ' '; echo\nseq -s, 1 5", note='tr turns newlines into spaces only to keep the output short here.'),
    [('qa', [
        dict(situation='Create 3 numbered test files with a format.', cmd='for f in $(seq -f "user_%03g.json" 1 3); do touch "$f"; done; ls',
             why='-f with %03g gives 001, 002, 003 inside any name.')]),
     ('devops', [
        dict(situation='Retry a command up to 3 times (the count comes from a variable).', cmd='max=3\nfor i in $(seq 1 "$max"); do echo "attempt $i"; done',
             why='{1..$max} would not work, because braces are expanded before variables. seq has no such problem.')]),
     ('data', [
        dict(situation='A test file with 100,000 rows to check a pipeline’s speed.', cmd='seq 1 100000 > ids.txt && wc -l ids.txt && tail -n 1 ids.txt',
             why='seq generates huge sequences in a fraction of a second.')]),
     ('sys', [
        dict(situation='Ping a range of server numbers (names app01–app03).', cmd='seq -w 1 3 | tr "\\n" " "; echo\nfor n in $(seq -f "app%02g" 1 3); do echo "checking $n"; done',
             why='Careful: <code>seq -w</code> pads only to the width of the largest number, so 1 to 3 stays 1 2 3. <code>-f "app%02g"</code> forces two digits: app01.')]),
    ]
) + cmdcard_u(['waiting between retries or polls in scripts', 'measuring how long a command or pipeline takes', 'watching something change on screen (disk, files, processes)'],
               ['scheduled jobs (use cron or systemd timers, Lesson 17.4)', 'precise benchmarks (use hyperfine or repeat many runs)'])(
    'sleep', 'sleep · time · watch', 'wait · measure · repeat',
    '<code>sleep</code> pauses; <code>time</code> runs a command and reports how long it took; <code>watch</code> runs a command every few seconds and redraws its output.',
    'sleep N[s|m|h|d]  ·  time COMMAND  ·  watch [-n SEC] [-d] COMMAND', 'safe',
    [('sleep 5 / 0.5 / 2m / 1h', 'wait 5 s, half a second, 2 minutes, 1 hour', 'pauses, retries'),
     ('timeout 10 cmd', 'stop cmd after 10 s (exit 124)', 'never wait forever'),
     ('time cmd', 'real, user, sys time', 'performance checks'),
     ('TIMEFORMAT=…', 'change bash time’s output', 'one-line timings'),
     ('watch cmd', 'repeat every 2 s, full screen', 'live view'),
     ('watch -n 5', 'every 5 s', 'slower changes'),
     ('watch -d', 'highlight what changed', 'spot changes'),
     ('watch -g', 'exit when the output changes', 'wait for an event')],
    dict(cmd='time sleep 0.2', note='real ≈ 0.2 s (waiting); user and sys ≈ 0, because sleeping uses no CPU.'),
    [('dev', [
        dict(situation='Which of two ways is faster?', cmd="TIMEFORMAT='%R s'\ntime (seq 1 300000 | wc -l)\ntime (for i in $(seq 1 30000); do :; done)",
             why='Time each version on the same data. (Exact numbers depend on the machine; run several times.)')]),
     ('devops', [
        dict(situation='Wait until a deploy creates a ready flag, checking every 0.2 s, but give up after 5 s.', cmd="(sleep 0.5; touch ready.flag) &\ntimeout 5 bash -c 'until [ -e ready.flag ]; do sleep 0.2; done' && echo 'service ready'",
             why='A loop with sleep polls cheaply; timeout makes sure the script never hangs forever.')]),
     ('sys', [
        dict(situation='Watch the disk fill up during a big copy.', cmd='watch -n 5 -d df -h /data',
             typical='Every 5.0s: df -h /data                    server-01: Fri Nov  6 11:20:05 2026\n\nFilesystem      Size  Used Avail Use% Mounted on\n/dev/sdb1       500G  312G  188G  63% /data',
             why='-d highlights the numbers that changed since the last refresh.')]),
     ('dba', [
        dict(situation='Watch a backup folder until the new dump appears.', cmd='watch -g ls /backups/mysql/ && echo "new file arrived"',
             typical='(the screen shows ls every 2 s …)\nnew file arrived',
             why='-g ends watch as soon as the output changes, so the next command runs.')]),
     ('data', [
        dict(situation='Respect an API limit of one call per second.', cmd='for id in 1 2 3; do echo "fetch record $id"; sleep 1; done',
             why='sleep between calls keeps you under rate limits.')]),
    ]
) + undo('These tools only read and print, with two exceptions.', [
    ('sudo date -s changed the clock:', 'on Ubuntu with time sync on, run <code>sudo timedatectl set-ntp true</code> (or restart chrony/systemd-timesyncd) to get the correct time back.'),
    ('watch or sleep is still running:', 'Ctrl+C stops it.'),
    ('bc is waiting for input:', 'you ran <code>bc</code> without echo: type <code>quit</code> or press Ctrl+D.'),
    ('A typo in a format:', 'nothing is changed; print again. Always test formats before using them in file names.'),
]) + errors('The errors students see most with these tools. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="date -d '2026-11-06 10:30:00 +45 days'", meaning='+45 after a time is read as a time zone.', fix="<code>date -d '2026-11-06 +45 days'</code>."),
    dict(cmd="date -d '2026-02-30'", meaning='30 February does not exist.', fix='Check the date; date validates it for you.'),
    dict(cmd="date +%F %T", meaning='The space split the format: %T became a second argument, which date reads as a date to set.', fix="Quote it: <code>date '+%F %T'</code>."),
    dict(cmd="[ 1.82 -gt 1.5 ] && echo high", meaning='bash test (and $(( ))) works with whole numbers only.', fix='<code>[ "$(echo "1.82 > 1.5" | bc)" -eq 1 ]</code>.'),
    dict(cmd="echo '10 / 0' | bc", meaning='Division by zero. Note that bc still exits with status 0, so a script will not notice.', fix='Check the divisor before calculating, or check bc’s output.'),
    dict(cmd='timeout 1 sleep 5', meaning='timeout stopped sleep after 1 s; exit status 124 means “timed out”.', fix='Not an error in your code: use the 124 in scripts to detect timeouts.'),
]) + stepper([
    ('1. Need a date?', '<p><code>date +%F</code>, or <code>date -d \'…\' +%F</code> for another day.</p>', 'Behind the screen: the kernel clock (seconds since 1970) + time zone rules.'),
    ('2. Put it in a name', '<p><code>backup_$(date +%F).tar.gz</code></p>', 'Behind the screen: $( ) runs date first and inserts its output.'),
    ('3. Need decimals?', '<p><code>echo \'scale=2; …\' | bc</code></p>', 'Behind the screen: bc parses the expression and calculates exactly.'),
    ('4. Need numbers?', '<p><code>seq -w 1 100</code> or <code>for i in $(seq 1 "$n")</code></p>', 'Behind the screen: seq prints; the loop reads each word.'),
    ('5. Need to wait or watch?', '<p><code>sleep</code> in loops, <code>timeout</code> as a limit, <code>watch</code> on screen.</p>', 'Behind the screen: clock_nanosleep; the process uses no CPU while waiting.'),
    ('6. Need to measure?', '<p><code>time command</code></p>', 'Behind the screen: bash reads the clocks before and after, and the CPU times from the kernel.'),
]) + qc('Write a command that prints the date 7 days ago as 30-10-2026 style.', "<code>date -d '7 days ago' '+%d-%m-%Y'</code>") + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def stamp(hl, note, tone='blue'):
    rows = [('kernel clock', '1793941200 s since 1970 (UTC)'), ('+ time zone', 'Asia/Kolkata = +05:30'), ('+ format', "'+%d-%m-%Y %H:%M'"), ('= text', '06-11-2026 10:30')]
    o = ''.join(label_box(14, 14 + k * 36, 332, 30, [f'{a}: {b}'], ('violet', 'green', 'amber', 'blue')[k] if k in hl else 'card', 8.8) for k, (a, b) in enumerate(rows))
    return o + t(180, 172, note, 8.8, tone, bold=True)
see = [term(14, 16, 332, 116, ['$ date +%s', ('1793941200', 'acc')], title='riya@laptop', size=8) + cap('Inside, time is one big number.', '', 'card', y=150, h=34),
       term(14, 16, 332, 116, ['$ date', ('Fri Nov  6 10:30:00 IST 2026', 'acc')], title='riya@laptop', size=8) + cap('Printed in Indian time (IST).', '', 'blue', y=150, h=34),
       term(14, 16, 332, 116, ['$ date -u', ('Fri Nov  6 05:00:00 UTC 2026', 'acc')], title='riya@laptop', size=8) + cap('Same moment in UTC: 5 h 30 min earlier.', '', 'blue', y=150, h=34),
       term(14, 16, 332, 116, ["$ date '+%d-%m-%Y %H:%M'", ('06-11-2026 10:30', 'acc')], title='riya@laptop', size=8) + cap('Same moment, your own format.', '', 'green', y=150, h=34),
       term(14, 16, 332, 116, ["$ date -d '+45 days' +%F", ('2026-12-21', 'acc')], title='riya@laptop', size=8) + cap('Arithmetic on the number, then printing.', '', 'green', y=150, h=34)]
behind = [stamp([0], 'The kernel counts seconds since 1 Jan 1970 UTC.', 'violet'),
          stamp([0, 1], 'date adds the time zone rules from /usr/share/zoneinfo.', 'green'),
          stamp([0], 'With -u no zone is added: UTC.', 'violet'),
          stamp([0, 1, 2, 3], 'The format decides how the result is written.', 'blue'),
          stamp([0], '+45 days = add 45 × 86,400 s (DST rules included).', 'violet')]
two = anim_two('One moment, many faces', 'How date turns a number into text',
               'A terminal: date +%s shows 1793941200, date shows IST, date -u shows UTC, a custom format shows 06-11-2026 10:30, and +45 days gives 2026-12-21.',
               'The kernel clock in seconds since 1970, plus the time zone, plus a format, gives the printed text.', see, behind,
               ['Linux stores time as seconds since 1970 (here the example moment 10:30 IST).',
                'Plain date shows it in your local zone, IST.',
                '<code>-u</code> shows UTC, five and a half hours earlier.',
                'A format string prints any layout you want.',
                '<code>-d</code> calculates other dates from it.'],
               ['One number in the kernel: the Unix time.',
                'Time zone rules turn it into local time.',
                'UTC needs no rules: that is why servers log in UTC.',
                'The format codes pick and arrange the parts.',
                'Date arithmetic is done in seconds and converted back.'])

w1 = term(14, 14, 332, 100, ['$ ls /backups/mysql', ('(empty)', 'dim'), ('# dump expected “soon”', 'dim')], title='dba@db-01', size=7.8) + cap('Riya waits for tonight’s dump.', '', 'card', y=150, h=34)
w2 = term(14, 14, 332, 100, ['$ while true; do ls; sleep 5; done', ('(scrolling list, Ctrl+C)', 'dim')], title='dba@db-01', size=7.6) + cap('A loop works, but scrolls endlessly.', '', 'amber', y=150, h=34)
w3 = term(14, 14, 332, 100, ['Every 2.0s: ls /backups/mysql', '', ('night_2026-11-06.sql.gz', 'acc')], title='watch', size=7.6) + cap('watch redraws the same screen.', '', 'blue', y=150, h=34)
w4 = term(14, 14, 332, 100, ['$ watch -g ls /backups/mysql && echo done', ('done', 'acc')], title='dba@db-01', size=7.6) + cap('-g: stop as soon as something changes.', '', 'green', y=150, h=34)
w5 = (t(180, 30, 'Waiting, three ways', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• people: watch -n 5 -d cmd', '• scripts: until …; do sleep 5; done', '• always a limit: timeout 600 …', '• schedules: cron (Lesson 17.4)'])) + cap('Never wait forever.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario', 'Waiting for the nightly dump',
              'Riya waits for a backup file to appear. Screens are typical output.',
              'sleep loops and watch', 'An empty backup folder; a while loop with sleep scrolls; watch redraws one screen; watch -g exits when the file appears.', [w1, w2, w3, w4, w5],
              ['The backup folder is still empty.',
               'A loop with sleep works but fills the screen.',
               '<code>watch</code> redraws the same view every 2 seconds.',
               '<code>watch -g</code> stops when the output changes, so the next command can run.',
               'In scripts use a sleep loop with <code>timeout</code>; for schedules use cron.'],
              hid='scenario-watch')

dx = dissect('Layer by layer: backup_$(date +%F).tar.gz',
    'How one command line builds a dated name. Each layer has a real command and output from our build machine.', [
    dict(key='clock', name='Kernel clock', sub='seconds since 1970',
         why='One simple number is easy to store and compare.',
         how='The kernel keeps UTC seconds; NTP keeps it right.',
         impl='clock_gettime(CLOCK_REALTIME).', used='Every timestamp.',
         cmd=D + '\ndate -d "$d" +%s'),
    dict(key='tz', name='Time zone', sub='Asia/Kolkata',
         why='People think in local time.',
         how='Rules from /usr/share/zoneinfo turn UTC into IST.',
         impl='TZ variable or /etc/localtime.', used='Logs, reports.',
         cmd=D + '\ndate -d "$d" "+%Z %z"'),
    dict(key='fmt', name='Format', sub='+%F',
         why='File names need a sortable, safe date.',
         how='%F = %Y-%m-%d: no spaces or slashes.',
         impl='strftime() in the C library.', used='Names, logs.',
         cmd=D + '\ndate -d "$d" +%F'),
    dict(key='sub', name='$( ) substitution', sub='insert the output',
         why='Use one command’s output inside another.',
         how='Bash runs date first and puts its output in the word.',
         impl='Command substitution (Lesson 5.4).', used='Every script.',
         cmd=D + '\necho "backup_$(date -d "$d" +%F).tar.gz"'),
    dict(key='file', name='The file', sub='sorted by name = by date',
         why='Old backups must be easy to find and delete.',
         how='YYYY-MM-DD names sort in date order.',
         impl='ls sorts names alphabetically.', used='Rotation scripts.',
         cmd='touch backup_2026-11-0{4,5,6}.tar.gz; ls backup_* | tail -n 1'),
], hint='From the clock to the file name. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A date in four forms, and waiting for a file</h2>
  <p>Left: what Riya sees (the example moment 2026-11-06 10:30 IST). Right: how date builds the text.</p>
''' + two + s1 + dx + qc('Why do many servers log in UTC instead of local time?', 'UTC has no time-zone or daylight-saving changes, so logs from servers in different countries line up and never repeat an hour.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Everyday utilities at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ tar czf', 'prompt'), ('bk_$(date +%F)', 'acc')], title='backup', size=6.4, step=12),
              '1. Dated backups and reports', 'Scripts name files with the date so every run is kept and easy to clean up.', ['Night', '*date +%F', 'history']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['bc', 'decimals'], 'amber', 8.6), '2. Thresholds and money',
    'Monitoring scripts compare decimal values (load, percentages) with bc; finance scripts calculate taxes and interest.', ['Value', '*bc', 'decision']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ until …', 'prompt'), ('sleep 5', 'acc')], title='devops', size=6.4, step=12),
    '3. Waiting for services', 'Deploy scripts wait for a port, a file or a health check with a sleep loop and a timeout.', ['Deploy', '*poll + sleep', 'ready']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['seq -f', 'test data'], 'green', 8.6), '4. Test data',
    'Testers generate numbered users, orders and files with seq for load tests.', ['Need data', '*seq', '10,000 rows']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['time', 'watch'], 'violet', 8.6), '5. Performance and monitoring',
    'Engineers time commands before and after a change, and watch disk or queue sizes during incidents.', ['Change', '*time / watch', 'evidence']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine (fixed dates keep outputs stable).', [
    dict(level='b', title='GST on an amount', scenario='18% GST on ₹1,250 and the total.',
         cmd="echo \"GST: $(echo 'scale=2; 1250*0.18' | bc)  total: $(echo 'scale=2; 1250*1.18' | bc)\"",
         explain='Two bc calls inside one echo.'),
    dict(level='b', title='Day of the week for a date', scenario='Which day is Republic Day 2027?',
         cmd="date -d 2027-01-26 +%A",
         explain='%A = full weekday name.'),
    dict(level='i', title='Last day of a month', scenario='Month-end report for February 2028 (leap year).',
         cmd="date -d '2028-03-01 -1 day' +%F",
         explain='First day of next month minus one day: works for every month.'),
    dict(level='i', title='Numbered folders for a sprint', scenario='Folders day01 … day10.',
         cmd='mkdir $(seq -f "day%02g" 1 10) && ls | head -3 && ls | wc -l',
         explain='seq -f formats each number; mkdir gets all ten names.'),
    dict(level='a', title='Age of a file in days', scenario='How old is the last backup?',
         cmd="touch -d '2026-10-30' bk.tar.gz\necho $(( ( $(date -d '2026-11-06' +%s) - $(date -r bk.tar.gz +%s) ) / 86400 )) days",
         explain='date -r gives the file time; subtract from “now” (fixed here) in seconds.'),
], extra=build_up('a dated, numbered test run', 'Riya prepares a folder for today’s test run with numbered input files and a timing.',
    '', [
    ("echo \"run_$(date -d '2026-11-06' +%F)\"", '1. The folder name (fixed date here; real: date +%F).'),
    ("d=run_$(date -d '2026-11-06' +%F); mkdir -p \"$d\" && ls", '2. Create it.'),
    ("d=run_$(date -d '2026-11-06' +%F); mkdir -p \"$d\" && for i in $(seq -w 1 12); do touch \"$d/input_$i.csv\"; done; ls \"$d\" | wc -l", '3. Twelve numbered input files.'),
    ("d=run_$(date -d '2026-11-06' +%F); mkdir -p \"$d\" && TIMEFORMAT='took %R s'; time (for i in $(seq -w 1 12); do touch \"$d/input_$i.csv\"; done)", '4. And how long it took.'),
])) + which('Choosing the right tool.', [
    ('Date in a name', 'date +%F', 'Sortable, safe.', 'date (spaces, colons).'),
    ('Another date', "date -d '+45 days'", 'Calendar-aware.', 'Counting days by hand.'),
    ('Month view', 'cal -3', 'At a glance.', 'cal in scripts.'),
    ('Decimals', "echo 'scale=2; …' | bc", 'Exact.', '$(( )) truncates.'),
    ('Powers and money', "scale=10, round later", 'No lost digits.', 'scale=2 during ^.'),
    ('Numbers from a variable', 'seq 1 "$n"', 'Works.', '{1..$n}.'),
    ('Wait in a script', 'sleep + timeout', 'Never hangs.', 'Endless loops.'),
    ('Measure', 'time cmd', 'Real vs CPU.', 'Guessing.'),
]) + keys('Shortcuts and handy forms.', [
    ('date +%F', 'the one format to remember', '2026-11-06'),
    ("date -d yesterday", 'relative dates: tomorrow, next friday, 2 weeks ago', "date -d '2 weeks ago' +%F"),
    ('bc -q', 'interactive calculator; quit to exit', 'bc -q → 2^16 → quit'),
    ('$(( ))', 'bash integer arithmetic, no bc needed', 'echo $((17 % 5))'),
    ('Ctrl + C', 'stop watch, sleep or a loop', 'watch df -h'),
    ('TIMEFORMAT', 'shorter output from time', "TIMEFORMAT='%R s'"),
]) + scriptit('wait-for-file.sh', 'A reusable “wait until a file appears” script with a timeout, a timestamped log line and the time it took.',
'''#!/bin/bash
file=${1:-ready.flag}; limit=${2:-5}
(sleep 0.6; touch "$file") &                 # demo: something creates the file
start=$(date +%s)
until [ -e "$file" ]; do
  if [ $(( $(date +%s) - start )) -ge "$limit" ]; then
    echo "gave up after ${limit}s" >&2; exit 1
  fi
  sleep 0.2
done
echo "$file appeared after about $(( $(date +%s) - start ))s"''',
'<p>The real script would also print <code>$(date \'+%F %T\')</code> in front of each message for the log.</p>') + puzzle_answer('bc is right about what it was told to do, but <b>140255.17 is the correct amount</b>. <code>scale=2</code> is applied to every intermediate result: 1.07² = 1.1449 is cut to 1.14, and so on through the power, so money is lost at each step. Calculate with a higher scale (<code>scale=10</code> gives 140255.1730700000) and round only at the end.') + qc('A script must wait at most 60 seconds for a port to open, checking every 2 seconds. Which two tools?', '<code>sleep 2</code> in a loop, and <code>timeout 60</code> (or a time check with <code>date +%s</code>) as the limit.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../05-viewing-files-cat-tac-less-more-head-tail-f-nl/">Lesson 3.5</a> and <code>$( )</code> to put output inside a command (more in Lesson 5.4).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
