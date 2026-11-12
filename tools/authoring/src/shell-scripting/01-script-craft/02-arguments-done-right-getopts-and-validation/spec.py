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
    module='01-script-craft', lesson='02-arguments-done-right-getopts-and-validation', n='1.2',
    module_label='Module 1 · Script craft',
    title='Arguments done right: getopts, long options, defaults and validation',
    desc='Make Bash scripts take options like real Linux commands: getopts option strings, OPTARG, OPTIND and shift, silent error mode, grouped flags, long options with a while/case loop, --, defaults from variables and the environment, and validation of allowed values, numbers and files, with every run real and 35+ examples.',
    og_desc='getopts, OPTARG, OPTIND, long options with case, defaults and input validation, all with real runs.',
    minutes=35, level='Beginner → Intermediate',
    lead='One script, many uses: named options with defaults, clear errors for bad input, and long options when you need them.',
    chips=['getopts animated round by round', 'Long options loop', 'Validation before work', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """set -- -v -c Pune -n 500 orders.csv     # pretend these were typed
city="" min=0 verbose=0
while getopts ':c:n:v' opt; do
  case $opt in
    c) city=$OPTARG ;;
    n) min=$OPTARG ;;
    v) verbose=1 ;;
    :) echo "option -$OPTARG needs a value" >&2 ;;
    \\?) echo "unknown option -$OPTARG" >&2 ;;
  esac
done
shift $((OPTIND - 1))
echo "city=$city min=$min verbose=$verbose file=$1"
"""

RUN = dict(
    heading='getopts in your browser',
    intro='<p><code>set --</code> fakes the command line so you can change it and rerun.</p>',
    code=MAIN,
    anno=[(":c:n:v", 'c and n take values; leading : = silent mode.'), ('shift $((OPTIND - 1))', 'Now $1 is the file.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Then change the set -- line.', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many rounds for -vq?',
             code="set -- -vq\nwhile getopts ':vq' o; do echo \"round: $o\"; done\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> -c needs a value but the string has no colon after c.',
             code="set -- -c Pune data.csv\nwhile getopts ':cv' o; do echo \"$o=${OPTARG:-none}\"; done\n"),
        dict(label='4 · Your turn', hint='Add an -o FILE option.',
             code="out=screen\nset -- -o report.txt\nwhile getopts ':o:' o; do case $o in o) out=$OPTARG;; esac; done\necho \"output: $out\"\n"),
        dict(label='5 · Challenge', hint='Parse --city=Pune with a case.',
             code="a=--city=Pune\ncase $a in --city=*) echo \"city=${a#*=}\";; esac\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC',
    intro='<p>Save orders.sh from this lesson and try it. Outputs below are from our build machine.</p>',
    items=[
        dict(title='1 · Defaults', cmd="./orders.sh orders.csv", output='4 orders, total 3449', note='Real output.'),
        dict(title='2 · Options', cmd="./orders.sh -s failed -n 500 orders.csv", output='1 orders, total 620', note='Real output.'),
        dict(title='3 · Unknown option', cmd="./orders.sh -x orders.csv; echo $?", output='orders.sh: unknown option -x\nUsage: orders.sh [-v] [-c CITY] [-s STATUS] [-n MIN] [-o FILE] CSV\n…\n2', note='Real output (usage lines shortened).'),
        dict(title='4 · macOS getopt differs', cmd="getopt --version", output='getopt from util-linux 2.39.3   (Linux)\n--   (macOS: BSD getopt has no long options)', note='Typical; prefer getopts or a case loop.'),
    ],
)

TRACE = dict(
    heading='getopts, line by line',
    intro='<p>Watch OPTIND move.</p>',
    code='''set -- -v -c Pune data.csv
while getopts ':vc:' o; do
  echo "opt=$o OPTARG=${OPTARG:-} OPTIND=$OPTIND"
done
shift $((OPTIND - 1))
echo "file=$1"
''',
    notes={2: 'One round per option.', 5: 'OPTIND is 4: three words were options.'},
)

WORKED_INTRO = 'Three scripts that need options.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='A cleanup script with a dry run',
         problem='<p>Delete *.tmp files in a folder; -n only shows what would go.</p>',
         inp='a folder', approach=['getopts with a flag.'],
         code='''clean() {
  local OPTIND=1 dry=0 o
  while getopts ':n' o; do case $o in n) dry=1 ;; esac; done
  shift $((OPTIND - 1))
  for f in "$1"/*.tmp; do
    [[ -e $f ]] || continue
    if (( dry )); then echo "would delete $f"; else rm -- "$f"; echo "deleted $f"; fi
  done
}
mkdir -p t; touch t/a.tmp t/b.tmp t/keep.txt
clean -n t; clean t; ls t
''', notes={2: 'local OPTIND for a function.', 7: '--dry-run style preview.'}, tryit='Add -v.'),
    dict(level='i', tag='Data', title='Date range with validation',
         problem='<p>Take -s START -e END (YYYY-MM-DD); reject bad formats and END before START.</p>',
         inp='two dates', approach=['Regex, then string compare.'],
         code='''range() {
  local OPTIND=1 s="" e="" o re='^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
  while getopts ':s:e:' o; do case $o in s) s=$OPTARG;; e) e=$OPTARG;; esac; done
  [[ $s =~ $re && $e =~ $re ]] || { echo "bad date format" >&2; return 2; }
  [[ $e < $s ]] && { echo "END before START" >&2; return 2; }
  echo "range $s .. $e ok"
}
range -s 2026-11-01 -e 2026-11-07; range -s 2026-11-07 -e 2026-11-01; range -s 1/11 -e 7/11
''', notes={4: 'Format first.', 5: 'ISO dates compare as strings.'}, tryit='Add a max range of 31 days.', expect='any'),
    dict(level='a', tag='DevOps', title='Long options for a deploy',
         problem='<p>Accept --env, --version, --dry-run and reject anything else.</p>',
         inp='long options', approach=['while/case loop.'],
         code='''deploy() {
  local env="" ver="" dry=0
  while (( $# )); do
    case $1 in
      --env=*) env=${1#*=} ;; --version=*) ver=${1#*=} ;; --dry-run) dry=1 ;;
      *) echo "unknown option $1" >&2; return 2 ;;
    esac; shift
  done
  case $env in staging|prod) ;; *) echo "--env must be staging or prod" >&2; return 2 ;; esac
  echo "deploy $ver to $env (dry=$dry)"
}
deploy --env=staging --version=1.4.2 --dry-run; deploy --env=qa --version=1
''', notes={5: 'Value after =.', 9: 'Allowed list.'}, tryit='Accept --env staging (two words).', expect='any'),
]

QUIZ = mix([
    dict(q="In ':c:vh', which option takes a value?", options=['v', 'c', 'h', 'all'], answer=1, why='Colon after c.'),
    dict(q='The value of the current option is in…', options=['$1', 'OPTIND', 'OPTARG', '$opt'], answer=2, why='OPTARG.'),
    dict(q='After the loop, operands start at $1 after…', options=['shift', 'shift $OPTIND', 'shift $((OPTIND-1))', 'unset'], answer=2, why='OPTIND-1 words were options.'),
    dict(q='A leading colon in the option string…', options=['makes all options need values', 'silences getopts errors so you handle them', 'is a typo', 'adds long options'], answer=1, why='Silent mode.'),
    dict(q='./s.sh data.csv -c Pune with getopts:', options=['-c is read', '-c is ignored (after operand)', 'error always', 'reorders'], answer=1, why='Stops at first operand.'),
    dict(q='Long options like --city need…', options=['getopts', 'a while/case loop', 'OPTIND', 'set -o'], answer=1, why='getopts is short-only.'),
    dict(q='Wrong usage should exit with…', options=['0', '1', '2', '127'], answer=2, why='Convention.'),
    dict(q='A file named -x.csv is passed safely with…', options=['quotes', '--', 'sudo', 'OPTARG'], answer=1, why='End of options.'),
])

REVISION = [
    'Options are named and optional; operands are what the script works on; options come first.',
    "getopts ':c:vh' opt: letter + : needs a value; leading : = silent mode; OPTARG holds the value.",
    'Handle \\?) unknown and :) missing value with your own message, usage on stderr and exit 2.',
    'shift $((OPTIND - 1)) leaves the operands in $1…; use local OPTIND=1 inside functions.',
    'Long options: while (( $# )); case $1 in --x=*) ${1#*=};; -x|--x) $2; shift 2;; --) break;; esac.',
    'Defaults before parsing, validation after (case lists, =~ numbers and formats, -r files, $#).',
]

FAQ = [
    ('How do I parse command line options in a Bash script?', 'Use the getopts built-in in a while loop with a case statement, then shift $((OPTIND-1)).'),
    ('What is the difference between getopt and getopts?', 'getopts is a Bash/POSIX built-in for short options; getopt is an external program (util-linux) that also handles long options but differs between systems.'),
    ('How do I support --long options in Bash?', 'Loop over the arguments with while (( $# )) and match them with case, using ${1#*=} for --name=value.'),
    ('What does OPTIND mean?', 'The index of the next argument getopts will read; used to shift the options away.'),
    ('Why is my option ignored?', 'It came after a file name; getopts stops at the first operand.'),
    ('How do I make an option required?', 'Leave its variable empty by default and check it after parsing.'),
    ('How do I set a default value for an option?', 'Assign it before the getopts loop, optionally from the environment with ${VAR:-default}.'),
]

PRACTICE_INTRO = 'Small option-parsing tasks. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Flag', stmt='Set v=1 when -v is given.', inp='-v', code="v=0; set -- -v; while getopts 'v' o; do v=1; done; echo $v\n", explain='1.'),
    dict(level='easy', title='Value', stmt='Read -c Pune into city.', inp='-c Pune', code="set -- -c Pune; while getopts 'c:' o; do city=$OPTARG; done; echo $city\n", explain='Pune.'),
    dict(level='easy', title='Operand', stmt='Print the file after -v.', inp='-v a.csv', code="set -- -v a.csv; while getopts 'v' o; do :; done; shift $((OPTIND-1)); echo $1\n", explain='a.csv.'),
    dict(level='medium', title='Value after =', stmt='Get Pune from --city=Pune.', inp='a long option', code="a=--city=Pune; echo ${a#*=}\n", explain='Remove up to =.'),
    dict(level='medium', title='Unknown', stmt='Report -z as unknown in silent mode.', inp='-z', code="set -- -z; while getopts ':v' o; do [[ $o == '?' ]] && echo \"unknown -$OPTARG\"; done\n", explain='OPTARG = z.'),
    dict(level='medium', title='Number check', stmt='Check that 42 is a whole number.', inp='42', code="n=42; [[ $n =~ ^[0-9]+$ ]] && echo ok\n", explain='Regex.'),
    dict(level='business', title='Allowed list', stmt='Accept only paid|failed; test with refunded.', inp='a status', code="s=refunded; case $s in paid|failed) echo ok;; *) echo \"invalid $s\";; esac\n", explain='invalid refunded.'),
    dict(level='business', title='Collect repeats', stmt='Collect two -c values into an array.', inp='-c A -c B', code="c=(); set -- -c A -c B; while getopts 'c:' o; do c+=(\"$OPTARG\"); done; echo ${#c[@]} ${c[*]}\n", explain='2 A B.'),
]

SCN_INTRO = 'Interview questions about script arguments.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How does a script read its arguments?”', 'Common.', 'and options?',
        '''<ul>
          <li>$1…$9, $#, "$@", shift.</li>
          <li>Options with getopts and a case statement.</li>
          <li>Check $# and print usage.</li>
        </ul>''', 'only mentioning $1.') +
    scn('Service company', 'Junior', 'Option silently ignored', 'Script called with file first.', 'why?',
        '''<ol>
          <li>getopts stops at the first operand.</li>
          <li>Options first, or a case loop.</li>
          <li>Reject extra operands with exit 2.</li>
        </ol>''', 'blaming the user.') +
    scn('Product company', 'Mid-level', 'Add --dry-run to a delete script', 'Safety review.', 'how?',
        '''<ul>
          <li>Long-option loop or -n flag.</li>
          <li>Wrap destructive commands: if dry, echo instead.</li>
          <li>Default to dry in CI until approved.</li>
        </ul>''', 'a second copy of the script.') +
    scn('Platform', 'Senior', 'Scripts behave differently on macOS laptops', 'getopt.', 'fix?',
        '''<ul>
          <li>BSD getopt lacks long options.</li>
          <li>Use getopts or a pure Bash loop.</li>
          <li>Test in CI on both.</li>
        </ul>''', 'requiring GNU tools silently.')
) + interview([
    ('What does a colon after a letter mean in getopts?', 'The option takes a value.'),
    ('What is OPTARG?', 'The current option’s value.'),
    ('Why shift $((OPTIND-1))?', 'To drop parsed options.'),
    ('getopts vs getopt?', 'Built-in short vs external long.'),
    ('How to end options?', '--.'),
    ('Silent mode?', 'Leading colon: handle ? and : yourself.'),
    ('Why local OPTIND?', 'Reset parsing in functions.'),
], [
    ('LFCS', 'Scripts with arguments.'),
    ('RHCSA', 'Process script inputs ($1, $2…).'),
    ('CompTIA Linux+', 'Script parameters.'),
]) + distro('Option parsing tools per system.', [
    ('getopts', 'bash, dash', 'bash', 'bash', 'bash, zsh'),
    ('getopt (long)', 'util-linux', 'util-linux', 'util-linux', 'macOS: BSD, short only'),
    ('Bash version', '5.x', '5.x', '5.x', 'macOS 3.2'),
    ('Long options', 'case loop', 'case loop', 'case loop', 'case loop'),
    ('Help convention', '-h/--help', 'same', 'same', 'same'),
]) + teaser('1.3', 'orders.sh can now say “error” and exit 2. Next: a full system of exit codes, log levels, timestamps, messages to stderr, and logging to a file and syslog.')

CHEATSHEET = cheatsheet('Arguments', [
    ('getopts', [("':c:vh'", 'string'), ('$OPTARG', 'value'), ('$OPTIND', 'next'), ('shift $((OPTIND-1))', 'operands')]),
    ('Errors', [('\\?)', 'unknown'), (':)', 'no value'), ('usage >&2', 'help'), ('exit 2', 'usage error')]),
    ('Long', [('while (( $# ))', 'loop'), ('--x=*) ${1#*=}', 'with ='), ('-x|--x) $2; shift 2', 'two words'), ('--) break', 'end')]),
    ('Validate', [('x=default', 'before'), ('case allowed', 'words'), ('=~ ^[0-9]+$', 'number'), ('[[ -r $f ]]', 'file')]),
])

MINDMAP = mindmap('Arguments', [
    ('Kinds', 'blue', ['flag', 'value', 'operand']),
    ('getopts', 'green', ['option string', 'OPTARG', 'OPTIND']),
    ('Errors', 'red', ['silent :', '? and :', 'exit 2']),
    ('Long', 'violet', ['case loop', '--x=', '--']),
    ('Defaults', 'amber', ['before loop', 'env', 'required']),
    ('Validate', 'acc', ['lists', 'numbers', 'files']),
])

LAB = lab('add options to a script', 'Build the lab (it creates <code>~/lab12/sales.csv</code>), write <code>~/lab12/total.sh</code>, then run the checker.',
    setup='''rm -rf ~/lab12; mkdir -p ~/lab12 && cd ~/lab12
printf 'id,city,amount\\n1,Pune,450\\n2,Mumbai,1200\\n3,Pune,300\\n4,Delhi,800\\n' > sales.csv''',
    tasks=['<code>total.sh [-c CITY] [-n MIN] FILE</code> prints the sum of <code>amount</code> for matching rows (defaults: all cities, MIN 0). Use getopts.',
           '<code>./total.sh -c Pune sales.csv</code> must print <code>750</code>; <code>./total.sh -n 500 sales.csv</code> must print <code>2000</code>.',
           'An unknown option (<code>-x</code>) or <code>-c</code> without a value must print a message to stderr and exit <b>2</b>.',
           'A non-numeric MIN (<code>-n abc</code>) must exit <b>2</b>; no FILE must exit <b>2</b>.'],
    solution='''cat > total.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
city="" min=0
bad() { echo "total.sh: $*" >&2; exit 2; }
while getopts ':c:n:' o; do
  case $o in
    c) city=$OPTARG ;; n) min=$OPTARG ;;
    :) bad "-$OPTARG needs a value" ;; \\?) bad "unknown option -$OPTARG" ;;
  esac
done
shift $((OPTIND - 1))
(( $# == 1 )) || bad "expected one FILE"
[[ $min =~ ^[0-9]+$ ]] || bad "MIN must be a number"
awk -F, -v c="$city" -v m="$min" 'NR>1 && (c=="" || $2==c) && $3>=m {s+=$3} END{print s+0}' "$1"
EOF
chmod +x total.sh''',
    check='''cd ~/lab12
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 getopts"  'grep -q getopts total.sh && [ -x total.sh ] && [ "$(./total.sh sales.csv 2>/dev/null)" = 2750 ]'
ok "2 options"  '[ "$(./total.sh -c Pune sales.csv 2>/dev/null)" = 750 ] && [ "$(./total.sh -n 500 sales.csv 2>/dev/null)" = 2000 ]'
ok "3 errors"   './total.sh -x sales.csv 2>e >o; r1=$?; ./total.sh -c 2>/dev/null; r2=$?; [ $r1 -eq 2 ] && [ $r2 -eq 2 ] && [ -s e ] && [ ! -s o ]'
ok "4 validate" './total.sh -n abc sales.csv 2>/dev/null; r1=$?; ./total.sh 2>/dev/null; r2=$?; [ $r1 -eq 2 ] && [ $r2 -eq 2 ]' ''')
