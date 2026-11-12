import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', 'linux'))
from linuxkit import *
import shlesson as _sh

# Riya's data and two versions of her script: getopts (short options) and a while/case loop (long options)
SS = r"""rm -rf ~/ops; mkdir -p ~/ops/data ~/ops/bin; cd ~/ops
cat > data/orders.csv <<'EOF'
id,city,amount,status
1001,Pune,450,paid
1002,Mumbai,1200,paid
1003,Pune,300,failed
1004,Delhi,800,paid
1005,Mumbai,150,refunded
1006,Pune,999,paid
1007,Delhi,620,failed
EOF
cat > bin/orders.sh <<'EOF'
#!/usr/bin/env bash
# orders.sh - filter and total orders from a CSV
# Usage: orders.sh [-v] [-c CITY] [-s STATUS] [-n MIN] [-o FILE] CSV
set -euo pipefail
readonly PROG=${0##*/}

city="" status=paid min=0 out="" verbose=0

usage() {
  cat <<USAGE
Usage: $PROG [-v] [-c CITY] [-s STATUS] [-n MIN] [-o FILE] CSV
  -c CITY    only this city (default: all)
  -s STATUS  paid | failed | refunded | all (default: paid)
  -n MIN     only amounts >= MIN (default: 0)
  -o FILE    write the result to FILE instead of the screen
  -v         verbose: explain what is being done
  -h         this help
USAGE
}
die()  { echo "$PROG: error: $*" >&2; exit 1; }
bad()  { echo "$PROG: $*" >&2; usage >&2; exit 2; }
info() { (( verbose )) && echo "$PROG: $*" >&2 || true; }

while getopts ':c:s:n:o:vh' opt; do
  case $opt in
    c) city=$OPTARG ;;
    s) status=$OPTARG ;;
    n) min=$OPTARG ;;
    o) out=$OPTARG ;;
    v) verbose=1 ;;
    h) usage; exit 0 ;;
    :) bad "option -$OPTARG needs a value" ;;
    \?) bad "unknown option -$OPTARG" ;;
  esac
done
shift $((OPTIND - 1))

(( $# == 1 )) || bad "expected exactly one CSV file, got $#"
file=$1
[[ -r $file ]] || die "cannot read '$file'"
case $status in paid|failed|refunded|all) ;; *) bad "invalid status '$status'" ;; esac
[[ $min =~ ^[0-9]+$ ]] || bad "MIN must be a whole number, got '$min'"

info "file=$file city=${city:-all} status=$status min=$min out=${out:-screen}"
result=$(awk -F, -v c="$city" -v s="$status" -v m="$min" '
  NR > 1 && (c == "" || $2 == c) && (s == "all" || $4 == s) && $3 >= m { n++; t += $3 }
  END { printf "%d orders, total %d\n", n, t }' "$file")
if [[ -n $out ]]; then echo "$result" > "$out"; info "written to $out"; else echo "$result"; fi
EOF
chmod +x bin/orders.sh"""

HOOK = hook('Riya’s <code>report.sh</code> from Lesson 1.1 takes exactly one file. Now three teams want different reports from it: sales wants only Pune, finance wants failed orders above ₹500, and the night job wants the result in a file, quietly. Copying the script three times is the wrong answer. The right answer is <b>options</b>: <code>-c Pune</code>, <code>-s failed -n 500</code>, <code>-o out.txt</code>, exactly like real Linux commands. Bash has a built-in parser for them, <code>getopts</code>, and this lesson builds a script with it, adds long options like <code>--city=Pune</code>, sets defaults, and rejects bad input before it can do damage.',
    ['parse short options with getopts: flags (-v), options with values (-c CITY), OPTARG, OPTIND and shift',
     'report unknown options and missing values with the leading-colon (silent) mode',
     'support long options (--city Pune, --city=Pune) with a while/case loop',
     'give every option a default and validate values (allowed list, numbers, files) before doing any work'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three teams, one script'),
    ('decide', 'Which parser?', 2, 'the quick chart'),
    ('definition', 'Options and getopts', 5, 'simple meaning + 4 depths'),
    ('types', 'Kinds of arguments', 4, 'flags, values, operands'),
    ('commands', 'Step by step', 15, 'getopts, long options, validation'),
    ('animation', 'See it happen', 4, 'getopts walks the arguments'),
    ('run', 'Run on your PC', 3, 'your terminal'),
    ('lab', 'Practice lab', 8, 'add options to a script'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('I need… → use', [
    ('one or two fixed arguments', '$1 $2 with a $# check', 'Lesson 1.1'),
    ('short options -v -c CITY', 'getopts', 'built into bash'),
    ('long options --city=Pune too', 'while (( $# )); case $1 in …; shift', 'hand-written loop'),
    ('a default value', 'set it before parsing', 'status=paid'),
    ('an option from the environment', '${CITY:-} as the default', 'CITY=Pune ./orders.sh'),
    ('to stop option parsing', '--', 'files that start with -'),
])

cmap = concept_map(
    [('1.1', 'Anatomy of a real script', 'usage, die, exit 2'), ('L:12.7', 'Positional parameters', '$1, $#, shift'), ('L:12.8', 'case', 'patterns')],
    ['flags, options with values, operands', 'getopts and its option string', 'OPTARG, OPTIND, shift', 'silent error mode (leading :)', 'long options with while/case', 'defaults and validation', '-- and file names starting with -'],
    [('1.3', 'Exit codes and logging', 'verbose messages'), ('1.4', 'Template + ShellCheck', 'reuse it'), ('4.1', 'Backup tool', 'many options'), ('3.3', 'Testing scripts', 'test every option')],
    'Your script now takes options like any Linux command, with help, defaults and clear errors.')

sc = (term(20, 14, 316, 156, ['$ ./orders.sh data/orders.csv', ('4 orders, total 3449', 'out'), '$ ./orders.sh -c Pune data/orders.csv', ('2 orders, total 1449', 'out'), '$ ./orders.sh -s failed -n 500 data/orders.csv', ('1 orders, total 620', 'acc'), '$ ./orders.sh -x data/orders.csv', ('orders.sh: unknown option -x', 'err')], title='riya@laptop: ~/ops', prompt='$', size=6.4, step=17)
      + t(352, 36, 'One script, many uses:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['-c CITY', '-s STATUS', '-n MIN', '-o FILE', '-v  -h'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three teams, one script</h2>
  <div class="story">
''' + puzzle('Riya’s first attempt reads options by position: <code>./orders.sh Pune failed 500 data/orders.csv</code>. It works until someone wants all cities with a minimum: <code>./orders.sh failed 500 data/orders.csv</code>, and now “failed” is read as the city. Next she tries getopts, but <code>./orders.sh data/orders.csv -c Pune</code> ignores <code>-c Pune</code> completely. And <code>./orders.sh -c</code> with no city prints a confusing Bash message instead of her own. Three bugs; what is the rule behind each?') + '''
    <p class="narration">In Riya’s <code>~/ops</code> folder (every run in this lesson is real).</p>
''' + scene('A terminal: orders.sh with no options gives paid totals; -c Pune limits to Pune; -s failed -n 500 shows failed orders over 500; -x is rejected as an unknown option.', sc,
            'Options make one script serve <tspan font-weight="700" class="s-acc">every team</tspan>.') + '''
K> Why not just keep adding $2, $3, $4?
A> Positions only work when every argument is always given, in order. Options have names, so they can be left out (defaults), given in any order, and checked. Every command you know works this way: <code>ls -l -a</code>, <code>tar -czf name dir</code>, <code>grep -i -c word file</code>.
R> And the file name at the end?
A> That is an <b>operand</b>: what the command works on. Options first, then operands; getopts stops at the first word that is not an option, and you <code>shift</code> the parsed options away so <code>$1</code> is the file.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 200" role="img" aria-label="The command line ./orders.sh -v -c Pune -n 500 data/orders.csv split into a flag, two options with values and one operand.">'
       + ''.join(label_box(14 + x, 40, w, 46, [a, b], c, 8.6) for x, w, a, b, c in [(0, 90, './orders.sh', '$0', 'card'), (96, 60, '-v', 'flag', 'green'), (162, 110, '-c Pune', 'option + value', 'blue'), (278, 110, '-n 500', 'option + value', 'blue'), (394, 216, 'data/orders.csv', 'operand ($1 after shift)', 'amber')])
       + t(320, 120, 'getopts reads the blue part · shift $((OPTIND-1)) · then $1 is the file', 9, 'acc', bold=True)
       + '<text x="632" y="194" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Options and getopts at four depths', [
    ('v', 'No jargon: a food order', '      <p>“One masala dosa, extra chutney, no onion, to take away.” The dish is the operand; the rest are options, in any order, each optional.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li>Option string <code>':c:s:n:o:vh'</code>: a letter followed by <code>:</code> needs a value.</li>
        <li><code>while getopts ':c:vh' opt; do case $opt in c) city=$OPTARG ;; v) verbose=1 ;; esac; done</code></li>
        <li><code>shift $((OPTIND - 1))</code>, then <code>$1</code> is the first operand.</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li>A leading <code>:</code> in the option string switches on <b>silent mode</b>: getopts prints nothing and gives you <code>?</code> (unknown option) or <code>:</code> (missing value) with the letter in <code>OPTARG</code>, so your own message and exit code 2 are used.</li>
        <li>getopts handles grouped flags (<code>-vh</code>) and attached values (<code>-cPune</code>) for free.</li>
        <li>getopts stops at the first operand: options must come <b>before</b> the file. <code>--</code> ends options explicitly.</li>
        <li>Long options are not supported by getopts; use a <code>while (( $# ))</code> loop with <code>case "$1"</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: OPTIND and the external getopt', '''      <ul>
        <li><code>OPTIND</code> is the index of the next argument to look at (starts at 1). Each call to getopts reads one option and moves OPTIND on; when it meets an operand or <code>--</code> it returns non-zero and the loop ends.</li>
        <li>OPTIND is a global variable: in a function that parses options, set <code>local OPTIND=1</code> or a second call parses nothing.</li>
        <li>The separate <b>getopt</b> program (util-linux, one word, no s) does support long options and reordering, but it differs between Linux and macOS; <code>getopts</code> is POSIX and works everywhere Bash and sh do.</li>
        <li>GNU convention (followed by most Linux tools): <code>-h/--help</code> exits 0, <code>--version</code> prints a version, errors exit 2 and print usage to stderr.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Options, operands and getopts</h2>
''' + def_block(
    'Command-line <b>options</b> are named arguments, usually a dash and a letter (<code>-c</code>) or two dashes and a word (<code>--city</code>), that change how a program behaves; some take a value. <b>Operands</b> are the remaining arguments, the things the program works on. <b>getopts</b> is a Bash built-in that reads short options one by one according to an option string, putting the letter in a variable and any value in <code>OPTARG</code>.',
    'Named, optional, any order, checked: options. What you work on: operands.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Flag', 'Option without a value: -v.'),
    ('Option with value', '-c Pune.'),
    ('Operand', 'The file etc. after options.'),
    ('Option string', '\':c:vh\' for getopts.'),
    ('OPTARG', 'The option’s value.'),
    ('OPTIND', 'Index of the next argument.'),
    ('Silent mode', 'Leading : in the option string.'),
    ('--', 'End of options.'),
]) + '\n' + names('Where the names come from.', [
    ('getopts', 'get options (plural)', 'Shell built-in, POSIX.'),
    ('getopt', 'the older external program', 'util-linux.'),
    ('OPTARG', 'option argument', 'Same as C’s optarg.'),
    ('OPTIND', 'option index', 'Same as C’s optind.'),
    ('flag', 'a switch, on or off', 'Like a flag raised.'),
    ('operand', 'what is operated on', 'POSIX term.'),
    ('--', 'end of options', 'POSIX guideline 10.'),
    ('-h', 'help', 'Convention.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Value needed', '<code>c:</code> in the option string'),
    ('Own errors', 'leading <code>:</code>'),
    ('After the loop', '<code>shift $((OPTIND-1))</code>'),
    ('Unknown option', '<code>\\?)</code> case'),
    ('Missing value', '<code>:)</code> case'),
    ('Long options', 'while/case loop'),
]) + '\n' + lv + didyou('POSIX’s “Utility Syntax Guidelines” are why almost every Unix tool feels the same: single-letter options with one dash, groupable (<code>-la</code>), options before operands, and <code>--</code> to end options. getopts implements exactly these rules.') + '''
EXAM> “What do OPTARG and OPTIND hold?” → OPTARG holds the value of the option just read (or the bad letter in silent mode); OPTIND is the index of the next argument to process, used with shift $((OPTIND-1)) to reach the operands.
''' + qc('In the option string \':c:vh\', which options need a value?', 'Only c (it is followed by a colon); v and h are flags. The first colon switches on silent mode.') + mistake('city=$2 status=$3 min=$4   (positions for optional settings)',
    'while getopts \':c:s:n:\' o; do … done; shift $((OPTIND-1))',
    'Leaving one out shifts all the others into the wrong variables, silently.') + mistake('./orders.sh data/orders.csv -c Pune',
    './orders.sh -c Pune data/orders.csv',
    'getopts stops at the first operand: options after the file are not read at all.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Kinds of arguments, and three ways to parse them</h2>
''' + table(['Kind', 'Example', 'In the option string', 'Variable'], [
    ['Flag', '<code>-v</code>', '<code>v</code>', '<code>verbose=1</code>'],
    ['Option with value', '<code>-c Pune</code> or <code>-cPune</code>', '<code>c:</code>', '<code>$OPTARG</code>'],
    ['Grouped flags', '<code>-vh</code>', '<code>vh</code>', 'two loop rounds'],
    ['Long option', '<code>--city=Pune</code>', '(not getopts)', '<code>${1#*=}</code>'],
    ['Operand', '<code>data/orders.csv</code>', '—', '<code>$1</code> after shift'],
    ['End of options', '<code>--</code>', 'built in', 'next words are operands'],
], minw=560) + table(['', '$1 $2 positions', 'getopts', 'while/case loop', 'external getopt'], [
    ['Short options', 'no', 'yes', 'yes', 'yes'],
    ['Long options', 'no', 'no', 'yes', 'yes (GNU)'],
    ['Grouped -vh', 'no', 'yes', 'extra code', 'yes'],
    ['Options after operands', '—', 'no', 'yes', 'yes (reorders)'],
    ['Portable', 'yes', 'yes (POSIX)', 'yes', 'differs on macOS'],
    ['Best for', '1–2 fixed args', 'most scripts', 'GNU-style tools', 'rarely needed'],
], minw=620) + qc('You need --dry-run and -n MIN. Which parser?', 'A while/case loop (getopts cannot do --dry-run).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>getopts, long options and validation</h2>
  <p id="commands">Every card runs on our build machine in <code>~/ops</code>: <code>data/orders.csv</code> (7 orders) and Riya’s finished <code>bin/orders.sh</code>, which you can read in full in the last card.</p>
''' + cmdcard_u(['every script with optional settings'], ['scripts with one fixed argument'])(
    'getopts', "while getopts ':c:s:n:o:vh' opt · OPTARG · shift", 'parse short options',
    'getopts reads one option per loop round. The letter goes into the variable you name (<code>opt</code>), a value into <code>OPTARG</code>. After the loop, <code>shift $((OPTIND - 1))</code> removes the options so the operands start at <code>$1</code>.',
    "while getopts ':c:vh' opt; do case $opt in …; esac; done; shift $((OPTIND-1))", 'safe',
    [('c:', 'needs a value', 'OPTARG'),
     ('v', 'flag', 'on/off'),
     ('leading :', 'silent mode', 'own errors'),
     ('OPTARG', 'the value', 'per round'),
     ('OPTIND', 'next index', 'for shift'),
     ('shift $((OPTIND-1))', 'drop options', 'operands at $1')],
    dict(setup=SS, cmd="cd ~/ops\nbin/orders.sh data/orders.csv\nbin/orders.sh -c Pune data/orders.csv\nbin/orders.sh -s failed -n 500 data/orders.csv\nbin/orders.sh -s all -c Delhi data/orders.csv", note='Defaults: all cities, status paid, minimum 0. Options can come in any order.'),
    [('dev', [
        dict(situation='Watch getopts work: one round per option.', cmd="set -- -v -c Pune -n500 data.csv\nwhile getopts ':c:n:v' o; do echo \"round: opt=$o OPTARG=${OPTARG:-} OPTIND=$OPTIND\"; done\nshift $((OPTIND-1)); echo \"operands left: $*\"", why='-n500 (value attached) works too.')]),
    ],
    anat=anatomy([('getopts', 'cmd', 'built-in'), (":c:s:n:o:vh", 'opt', 'option string'), ('opt', 'arg', 'variable for the letter')], 'A colon after a letter = that option takes a value.')
) + cmdcard_u(['any script others will call'], ['Bash’s own cryptic messages'])(
    'errors', "\\?) unknown · :) missing value · exit 2", 'silent mode and errors',
    'With a leading colon getopts stays quiet. An unknown option gives <code>?</code> with the letter in OPTARG; an option missing its value gives <code>:</code>. Your <code>case</code> turns both into a clear message, the usage text and exit code 2.',
    "\\?) bad \"unknown option -$OPTARG\" ;;   :) bad \"option -$OPTARG needs a value\" ;;", 'safe',
    [("':…'", 'silent mode', 'recommended'),
     ('\\?)', 'unknown letter', 'OPTARG = letter'),
     (':)', 'missing value', 'OPTARG = letter'),
     ('exit 2', 'usage error', 'convention'),
     ('usage >&2', 'help on errors', 'stderr'),
     ('-h', 'help, exit 0', 'stdout')],
    dict(setup=SS, cmd="cd ~/ops\nbin/orders.sh -x data/orders.csv 2>&1 | head -2; echo \"exit ${PIPESTATUS[0]}\"\nbin/orders.sh -c 2>&1 | head -1\nbin/orders.sh -c Pune 2>&1 | head -1", note='Unknown option, missing value, missing file argument: three clear messages, exit 2.', expect='any'),
    [('dev', [
        dict(situation='Without the leading colon: Bash’s own message.', cmd="set -- -x; while getopts 'c:' o; do echo \"opt=$o\"; done", why='getopts prints “illegal option” itself and sets opt to ?. Silent mode lets you control the wording.', expect='any')]),
    ]
) + cmdcard_u(['GNU-style tools', '--dry-run, --help'], ['when short options are enough'])(
    'long', 'while (( $# )); case $1 in --city=*) … ; shift', 'long options',
    'getopts cannot read <code>--city</code>. A <code>while (( $# &gt; 0 ))</code> loop looks at <code>$1</code>, matches it with <code>case</code>, takes the value from <code>$2</code> (then <code>shift 2</code>) or from <code>${1#*=}</code> for the <code>--city=Pune</code> form, and stops at <code>--</code> or the first operand.',
    "case $1 in -c|--city) city=$2; shift 2 ;; --city=*) city=${1#*=}; shift ;; --) shift; break ;; esac", 'safe',
    [('-c|--city)', 'both spellings', 'friendly'),
     ('--city=*)', 'with =', 'GNU style'),
     ('${1#*=}', 'value after =', 'parameter expansion'),
     ('shift 2', 'option + value', 'next'),
     ('--) shift; break', 'end of options', 'safe'),
     ('-*) unknown', 'catch the rest', 'exit 2')],
    dict(cmd="parse() {\n  local city=\"\" dry=0 files=()\n  while (( $# > 0 )); do\n    case $1 in\n      -c|--city) city=$2; shift 2 ;;\n      --city=*) city=${1#*=}; shift ;;\n      --dry-run) dry=1; shift ;;\n      --) shift; files+=(\"$@\"); break ;;\n      -*) echo \"unknown option $1\" >&2; return 2 ;;\n      *) files+=(\"$1\"); shift ;;\n    esac\n  done\n  echo \"city=${city:-all} dry=$dry files=${files[*]}\"\n}\nparse --city=Pune --dry-run a.csv\nparse a.csv -c Mumbai b.csv\nparse -- -odd-name.csv", note='Unlike getopts, this loop also accepts options after operands.'),
    [('devops', [
        dict(situation='An unknown long option.', cmd="case --colour in -c|--city) echo city;; --dry-run) echo dry;; -*) echo \"unknown option --colour\" >&2; echo 'exit 2';; esac", why='Same rule as short options: message, usage, exit 2.')]),
    ]
) + cmdcard_u(['every value that comes from a user'], ['trusting input'])(
    'validate', 'defaults · allowed lists · numbers · files', 'defaults and validation',
    'Set every default <b>before</b> parsing (<code>status=paid min=0</code>). After parsing, check everything before doing any work: allowed words with <code>case</code>, numbers with <code>[[ $min =~ ^[0-9]+$ ]]</code>, files with <code>-r</code>, and the operand count with <code>$#</code>.',
    "case $status in paid|failed|refunded|all) ;; *) bad \"invalid status\" ;; esac", 'safe',
    [('x=default', 'before the loop', 'defaults'),
     ('${CITY:-}', 'default from env', 'CI, cron'),
     ('case allowed', 'whitelist', 'words'),
     ('=~ ^[0-9]+$', 'whole number', 'numbers'),
     ('[[ -r $f ]]', 'readable file', 'files'),
     ('(( $# == 1 ))', 'operand count', 'operands')],
    dict(setup=SS, cmd="cd ~/ops\nbin/orders.sh -s cancelled data/orders.csv 2>&1 | head -1\nbin/orders.sh -n 5OO data/orders.csv 2>&1 | head -1\nbin/orders.sh nosuch.csv; echo \"exit $?\"", note='5OO has the letter O, not zero: caught before awk silently treats it as 5.', expect='any'),
    [('sec', [
        dict(situation='Why validate: an unchecked value reaches awk.', cmd="awk -v m='5OO' 'BEGIN{ print \"awk reads 5OO as\", m + 0 }'", why='Without the check the report would quietly use 5 as the minimum.')]),
    ]
) + cmdcard_u(['scheduled jobs', 'quiet vs chatty runs'], ['mixing info messages into results'])(
    'flags', '-v verbose · -o FILE · -h help', 'flags that change behaviour',
    'A flag just sets a variable (<code>verbose=1</code>). Verbose messages go to stderr so the result stays clean; <code>-o FILE</code> redirects only the result. <code>-h</code> prints usage to stdout and exits 0.',
    'orders.sh -v -o out.txt data/orders.csv', 'safe',
    [('-v', 'explain steps', 'debugging'),
     ('info() → stderr', 'messages', 'clean output'),
     ('-o FILE', 'write result', 'cron'),
     ('-h', 'usage, exit 0', 'help'),
     ('-q', 'quiet', 'opposite of -v'),
     ('-n / --dry-run', 'show, do not do', 'safety')],
    dict(setup=SS, cmd="cd ~/ops\nbin/orders.sh -v -c Mumbai -o mumbai.txt data/orders.csv\ncat mumbai.txt\nbin/orders.sh -h | head -3", note='The two orders.sh: lines are verbose messages on stderr; the result went to the file.'),
    [('sys', [
        dict(situation='Read the whole finished script.', setup=SS, cmd="cd ~/ops; sed -n '24,38p' bin/orders.sh", why='The getopts loop and shift.')]),
    ]
) + undo('Option parsing mistakes are fixed by rerunning; prevent the expensive ones:', [
    ('Option after the file ignored:', 'put options first, or switch to a while/case loop.'),
    ('Destructive script got a wrong value:', 'validate first, act second; add <code>-n/--dry-run</code> to preview.'),
    ('File name starting with -:', '<code>./script.sh -- -file.csv</code> or <code>./-file.csv</code>.'),
    ('getopts in a function parses nothing the 2nd time:', '<code>local OPTIND=1</code> at the start of the function.'),
]) + errors('Errors students see most (really run on our build machine).', [
    dict(cmd="set -- -c; while getopts 'c:' o; do :; done", meaning='No leading colon: Bash prints its own “option requires an argument”.', fix="Use ':c:' and handle :) yourself."),
    dict(setup=SS, cmd="cd ~/ops && bin/orders.sh data/orders.csv -c Pune", meaning='“expected exactly one CSV file, got 3”: getopts stopped at the file, so -c Pune became extra operands.', fix='Options before operands.'),
    dict(cmd="f(){ while getopts 'v' o; do echo \"got -$o\"; done; }; f -v; f -v; echo '(second call printed nothing)'", meaning='OPTIND kept its value from the first call.', fix='local OPTIND=1 inside the function.'),
]) + qc('After getopts, why shift $((OPTIND - 1)) and not shift $OPTIND?', 'OPTIND points at the next unread argument; OPTIND-1 arguments were options.') + '''
'''
cards = cards + '</section>\n'

ARGS = ['-v', '-c', 'Pune', '-n', '500', 'data.csv']
def gstep(k):
    o = t(180, 18, './orders.sh -v -c Pune -n 500 data.csv', 9.2, 'ink2', bold=True)
    idx = [1, 2, 4, 6][k]
    col = {0: ['green'], 1: ['green', 'blue', 'blue'], 2: ['green', 'blue', 'blue', 'amber', 'amber'], 3: ['green', 'blue', 'blue', 'amber', 'amber', 'violet']}[k]
    for i, a in enumerate(ARGS):
        o += label_box(10 + i * 58, 32, 54, 34, [a], col[i] if i < len(col) else 'card', 8.4)
    o += t(180, 90, ['round 1: opt=v (flag)', 'round 2: opt=c OPTARG=Pune', 'round 3: opt=n OPTARG=500', 'data.csv is not an option: loop ends'][k], 9.2, 'violet', bold=True)
    o += t(180, 112, f'OPTIND = {[2, 4, 6, 6][k]}', 9, 'acc', bold=True)
    return o
see_cmds = [['$ ./orders.sh -v …', ('verbose=1', 'out')], ['getopts → c', ('city=Pune', 'out')], ['getopts → n', ('min=500', 'out')], ['shift $((OPTIND-1))', ('$1 = data.csv', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@laptop: ~/ops', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['-v.', '-c.', '-n.', 'shift.'])]
two = anim_two('getopts, round by round', 'Behind the screen: OPTIND moves',
               'A terminal: getopts sets verbose, city and min one round at a time, then shift leaves data.csv as $1.',
               'Six argument boxes light up as getopts reads them; OPTIND counts up to 6.', see, [gstep(k) for k in range(4)],
               ['-v.', '-c.', '-n.', 'end.'], ['v', 'c', 'n', 'end'])

def lng(k):
    o = t(180, 18, '--city=Pune --dry-run a.csv', 9.4, 'ink2', bold=True)
    rows = [('$1 = --city=Pune', 'case --city=*) → city=${1#*=}', 'blue'), ('$1 = --dry-run', 'case --dry-run) → dry=1', 'green'), ('$1 = a.csv', 'case *) → files+=(a.csv)', 'amber'), ('$# = 0', 'loop ends', 'violet')]
    for i in range(k + 1):
        a, b, c = rows[i]
        o += label_box(14, 30 + i * 28, 330, 24, [f'{a}: {b}'], c, 8)
    return o
s1 = anim_one('Animated example', 'A long-option loop',
              'case on $1, then shift.', 'while (( $# ))', 'Rows show each case branch as the loop shifts.', [lng(k) for k in range(4)],
              ['--city=.', '--dry-run.', 'operand.', 'done.'], hid='scenario-long')

dx = dissect('Layer by layer: from command line to variables',
    'Each layer has a real command from our build machine.', [
    dict(key='argv', name='Words', sub='"$@"', why='What the shell passes.', how='Split by the shell.', impl='argv.', used='$#.',
         cmd="show(){ echo \"$# words:\"; printf '  [%s]\\n' \"$@\"; }; show -c 'New Delhi' -vh data.csv"),
    dict(key='getopts', name='getopts', sub='rounds', why='Name → value.', how='Option string.', impl='Built-in.', used='Short options.',
         cmd="set -- -vh -c'New Delhi' x; while getopts ':vhc:' o; do printf '%s=%s ' \"$o\" \"${OPTARG:-}\"; done; echo"),
    dict(key='check', name='Validation', sub='before work', why='Safety.', how='case, =~, -r.', impl='Exit 2.', used='Every script.',
         setup=SS, cmd="cd ~/ops; for s in paid PAID all x; do case $s in paid|failed|refunded|all) echo \"$s: ok\";; *) echo \"$s: rejected\";; esac; done"),
], hint='Words → getopts → checks. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>getopts round by round, and a long-option loop</h2>
''' + two + s1 + dx + qc('What does -vh become in getopts?', 'Two rounds: opt=v, then opt=h.') + '''
</section>
'''

VAR = variations('Sixteen more option-parsing patterns. All were really run on our build machine.', [
    ('getopts forms', [
        dict(title='Attached value', cmd="set -- -cPune; while getopts ':c:' o; do echo \"$o=$OPTARG\"; done", why='-cPune = -c Pune.'),
        dict(title='Grouped flags', cmd="set -- -qvx; while getopts ':qvx' o; do printf '%s ' $o; done; echo", why='Three rounds.'),
        dict(title='Value with spaces', cmd="set -- -c 'New Delhi'; while getopts ':c:' o; do echo \"city=[$OPTARG]\"; done", why='Quotes keep it one word.'),
        dict(title='Repeated option collects a list', cmd="cities=(); set -- -c Pune -c Delhi; while getopts ':c:' o; do cities+=(\"$OPTARG\"); done; echo \"${cities[*]}\"", why='Array for -c used twice.'),
        dict(title='Counting -v for verbosity levels', cmd="v=0; set -- -vvv; while getopts ':v' o; do ((v++)); done; echo \"verbosity $v\"", why='-vvv = level 3.'),
        dict(title='-- ends options', cmd="set -- -v -- -c; while getopts ':vc:' o; do echo \"opt $o\"; done; shift $((OPTIND-1)); echo \"operand: $1\"", why='-c after -- is an operand.'),
        dict(title='local OPTIND in a function', cmd="f(){ local OPTIND=1 o; while getopts 'v' o; do echo \"got -$o\"; done; }; f -v; f -v", why='Works on every call.'),
    ]),
    ('Running orders.sh', [
        dict(title='Minimum only', setup=SS, cmd="cd ~/ops; bin/orders.sh -n 900 data/orders.csv", why='Paid orders ≥ 900.'),
        dict(title='All statuses for one city', setup=SS, cmd="cd ~/ops; bin/orders.sh -s all -c Pune data/orders.csv", why='-s all.'),
        dict(title='Refunded', setup=SS, cmd="cd ~/ops; bin/orders.sh -s refunded data/orders.csv", why='Allowed list.'),
        dict(title='Grouped -vh', setup=SS, cmd="cd ~/ops; bin/orders.sh -vh | head -1", why='h exits first.'),
        dict(title='Too many files', setup=SS, cmd="cd ~/ops; bin/orders.sh data/orders.csv data/orders.csv 2>&1 | head -1", why='Operand count check.', expect='any'),
    ]),
    ('Defaults and environment', [
        dict(title='Default from the environment', cmd="city=${CITY:-all}; echo \"city=$city\"; CITY=Pune bash -c 'echo \"city=${CITY:-all}\"'", why='Options override env, env overrides built-in default.'),
        dict(title='Required option', cmd="out=''; [[ -n $out ]] || { echo 'error: -o FILE is required' >&2; echo 'exit 2'; }", why='Check after parsing.'),
        dict(title='Number range', cmd="for n in 5 0 101; do (( n >= 1 && n <= 100 )) && echo \"$n ok\" || echo \"$n out of range\"; done", why='(( )) for ranges.'),
        dict(title='Date format check', cmd="for d in 2026-11-12 12/11/2026; do [[ $d =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] && echo \"$d ok\" || echo \"$d bad\"; done", why='Regex for formats.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Options in real scripts</h2>
''' + usecase(label_box(14, 22, 92, 46, ['backup', '-d -k'], 'blue', 8.6), '1. Backup scripts',
              'backup.sh -d /data -k 7 -n: source, keep days, dry run, so the same script runs on every server.', ['options', '*getopts', 'one script']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['CI', '--env'], 'green', 8.6), '2. Deploy scripts in CI',
    'deploy.sh --env staging --version 1.4.2 --dry-run; CI passes different options per branch.', ['branch', '*--env', 'deploy']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['data', 'dates'], 'amber', 8.6), '3. Data jobs',
    'extract.sh -s 2026-11-01 -e 2026-11-07 -t orders: validated date ranges before a long Spark or Hive job starts.', ['dates', '*validate', 'job']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ops', '-h'], 'violet', 8.6), '4. On-call tools',
    'At 3 a.m. -h is the documentation; clear errors with exit 2 prevent half-runs.', ['-h', '*usage', 'right call']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['cron', '-q -o'], 'red', 8.6), '5. Scheduled reports',
    'Cron runs report.sh -q -o /reports/daily.txt; humans run it with -v.', ['cron', '*-q -o', 'file']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful option tricks. All really run on our build machine.', [
    dict(level='b', title='Help', scenario='How do I call it?', setup=SS, cmd="cd ~/ops; bin/orders.sh -h | head -2", explain='-h exits 0.'),
    dict(level='b', title='One city', scenario='Sales.', setup=SS, cmd="cd ~/ops; bin/orders.sh -c Delhi data/orders.csv", explain='-c.'),
    dict(level='i', title='Failed above 500', scenario='Finance.', setup=SS, cmd="cd ~/ops; bin/orders.sh -s failed -n 500 data/orders.csv", explain='Two options.'),
    dict(level='i', title='Quietly to a file', scenario='Night job.', setup=SS, cmd="cd ~/ops; bin/orders.sh -o night.txt data/orders.csv && cat night.txt", explain='-o.'),
    dict(level='a', title='Every city in a loop', scenario='Report per city.', setup=SS, cmd="cd ~/ops; for c in $(cut -d, -f2 data/orders.csv | tail -n +2 | sort -u); do printf '%-7s ' $c; bin/orders.sh -c $c data/orders.csv; done", explain='Script reused as a building block.'),
], extra=build_up('positional script → options', 'Riya rebuilds her parser step by step.', SS, [
    ("cd ~/ops; city='' status=paid; set -- -c Pune data/orders.csv; while getopts ':c:s:' o; do case $o in c) city=$OPTARG;; s) status=$OPTARG;; esac; done; echo \"city=$city status=$status OPTIND=$OPTIND\"", '1. A getopts loop with defaults.'),
    ("cd ~/ops; set -- -c Pune data/orders.csv; OPTIND=1; while getopts ':c:' o; do :; done; shift $((OPTIND-1)); echo \"file=$1\"", '2. shift to the operand.'),
    ("cd ~/ops; set -- -z; OPTIND=1; while getopts ':c:' o; do case $o in \\?) echo \"unknown option -$OPTARG\";; esac; done", '3. Silent-mode error.'),
    ("cd ~/ops; bin/orders.sh -c Pune data/orders.csv", '4. The finished script.'),
], cumulative=False)) + VAR + which('Choosing the right form.', [
    ('Short options', 'getopts', 'Built-in, POSIX.', 'Positions.'),
    ('Long options', 'while/case loop', 'GNU style.', 'getopt differences.'),
    ('Own error text', "leading ':'", 'Control.', "Bash's message."),
    ('Optional setting', 'default + option', 'Clear.', 'Required positions.'),
    ('Dangerous action', '-n / --dry-run', 'Preview.', 'No preview.'),
    ('Odd file names', '--', 'Safe.', 'Hoping.'),
]) + keys('Handy forms.', [
    ("while getopts ':c:vh' o; do", 'loop', 'start'),
    ('c) city=$OPTARG ;;', 'value', 'case'),
    (':) bad "-$OPTARG needs a value" ;;', 'missing', 'error'),
    ('\\?) bad "unknown -$OPTARG" ;;', 'unknown', 'error'),
    ('shift $((OPTIND - 1))', 'to operands', 'after'),
    ('--city=*) city=${1#*=} ;;', 'long =', 'loop'),
]) + scriptit('opts-skeleton.sh', 'The getopts block from this lesson, ready to paste into the Lesson 1.1 skeleton.',
'''#!/usr/bin/env bash
set -euo pipefail
readonly PROG=${0##*/}
name=world loud=0
usage() { echo "Usage: $PROG [-l] [-n NAME] [-h]"; }
bad()   { echo "$PROG: $*" >&2; usage >&2; exit 2; }

while getopts ':n:lh' opt; do
  case $opt in
    n) name=$OPTARG ;;
    l) loud=1 ;;
    h) usage; exit 0 ;;
    :) bad "option -$OPTARG needs a value" ;;
    \\?) bad "unknown option -$OPTARG" ;;
  esac
done
shift $((OPTIND - 1))
(( $# == 0 )) || bad "unexpected argument '$1'"

msg="Hello, $name"
(( loud )) && msg=${msg^^}
echo "$msg"''',
'<p>Run with no options it prints Hello, world.</p>', expect='any') + puzzle_answer('<b>1.</b> Positions break as soon as an argument is optional: leaving the city out shifts “failed” into <code>$1</code>. Named options with defaults fix it. <b>2.</b> getopts stops at the <b>first operand</b>; <code>data/orders.csv -c Pune</code> leaves <code>-c Pune</code> unread (orders.sh then complains about 3 operands). Put options first, or use a while/case loop that accepts both orders. <b>3.</b> Without a leading colon in the option string, Bash prints its own “option requires an argument -- c”. With <code>\':c:…\'</code> getopts is silent and gives you <code>:</code> with the letter in OPTARG, so you print your own message, the usage and exit 2.') + qc('Which variable holds the value of -c inside the loop?', 'OPTARG.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-anatomy-of-a-real-script/">Lesson 1.1</a> (usage, die, exit 2) and <a href="../../../linux/12-shell-environment/07-script-input-positional-parameters-read-and-arithmetic/">Linux Lesson 12.7</a> ($1, $#, shift).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
