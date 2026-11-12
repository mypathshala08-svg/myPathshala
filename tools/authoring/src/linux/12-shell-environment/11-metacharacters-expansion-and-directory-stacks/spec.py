import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='11-metacharacters-expansion-and-directory-stacks', n='12.11',
    module_label='Module 12 · The shell environment and shell programming',
    title='Metacharacters, command-line expansion order and directory stacks (pushd, popd, dirs)',
    desc='Shell metacharacters (; & && || | < > ( ) { } $ ` \\ " \' * ? [ ] ~ # !) and how to protect them; the expansion order: brace, tilde, parameter/arithmetic/command/process substitution, word splitting, globbing, quote removal; brace ranges, steps and padding; $( ) vs backticks, $(<file), <( ) and >( ); eval, ${!name} and command arrays; pushd, popd, dirs -v, cd -; real outputs, animations and 30+ examples.',
    og_desc='Bash metacharacters, the order of expansions, eval and pushd/popd directory stacks, with real outputs and 30+ examples.',
    minutes=40, level='Beginner → Advanced',
    lead='bash rewrites every command line in a fixed order before running it: braces, tilde, variables and commands, splitting, wildcards, quotes. This lesson shows each step, the metacharacters that trigger them, eval and its dangers, and the pushd/popd directory stack.',
    chips=['Expansion order animated', 'Brace tricks', 'eval vs arrays', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Watch expansions happen
mkdir -p proj/{src,docs}
touch proj/src/{main,util}.py proj/docs/readme.md
echo proj/{src,docs}/*
echo ~ "~" $((6 * 7)) "$(date +%Y)"
pushd proj/src > /dev/null
pwd
popd > /dev/null
pwd
"""

RUN = dict(
    heading='Braces, globs, substitutions and pushd',
    intro='<p>Build a tree with braces, list it with a glob, see tilde and substitutions, and visit a folder with pushd/popd.</p>',
    code=MAIN,
    anno=[('echo proj/{src,docs}/*', 'Braces first, then the glob finds files.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which ~ was expanded?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does each echo print? Then run.',
             code="n=3\necho {1..3}\necho {1..$n}\necho $(seq 1 $n)\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the pipe should work. Use an array or run it directly.',
             code="cmd='ls / | wc -l'\n$cmd 2>&1 | head -1\n", expect='any'),
        dict(label='4 · Your turn', hint='Make a backup copy of notes.txt with one brace.',
             code="echo hi > notes.txt\ncp notes.txt{,.bak}\nls notes*\n"),
        dict(label='5 · Challenge', hint='Compare two command outputs without temp files.',
             code="diff <(printf 'a\\nb\\n') <(printf 'a\\nc\\n')\necho \"diff status $?\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own stack',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · A working stack', cmd='pushd /var/log; pushd /etc; dirs -v', output='/var/log ~\n/etc /var/log ~\n 0  /etc\n 1  /var/log\n 2  ~', note='Typical (pushd prints the stack each time).'),
        dict(title='2 · Jump with ~N', cmd='ls ~1 | head -3', output='alternatives.log\napt\nauth.log', note='Typical: ~1 = entry 1 of the stack.'),
        dict(title='3 · Expansion trace', cmd='set -x; ls ~/{Documents,Downloads} > /dev/null; set +x', output='+ ls /home/vineeta/Documents /home/vineeta/Downloads', note='Typical.'),
        dict(title='4 · bash version', cmd='bash --version | head -1', output=pc('bash --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Expansions, line by line',
    intro='<p>Step through: braces, tilde, arithmetic and command substitution in variables.</p>',
    code='''names=$(echo {a,b,c})
home=~
n=$(( 2 ** 5 ))
year=$(date +%Y)
echo "$names | $home | $n | ${#year} digits"
''',
    notes={1: 'Braces inside $( ).', 2: 'Tilde in an assignment.', 3: 'Arithmetic :: 32.', 4: 'Command substitution.', 5: 'All together.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a project tree, a safe command list and a build loop with the stack.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='A project tree in one command',
         problem='<p>Create app/{src,tests}/{unit,integration} and count the folders.</p>',
         inp='nothing', approach=['Nested braces.', 'find -type d.'],
         code='''mkdir -p app/{src,tests}/{unit,integration}
find app -type d | sort
''', notes={1: '2 × 2 leaf folders.'}, tryit='Add a docs folder at the top level.'),
    dict(level='i', tag='Security', title='Commands in an array instead of eval',
         problem='<p>Build a grep command with a pattern containing spaces and run it safely.</p>',
         inp='a file', approach=['Array of arguments.', '"${cmd[@]}".'],
         code='''printf 'disk full\\ndisk ok\\n' > log.txt
pattern='disk full'
cmd=(grep -n "$pattern" log.txt)
"${cmd[@]}"
''', notes={4: 'One argument per item.'}, tryit='Try the same with a plain string and $cmd.'),
    dict(level='a', tag='DevOps', title='Build every module and come back',
         problem='<p>For each module folder, enter it, “build” (count files), and return, using pushd/popd.</p>',
         inp='module folders', approach=['for + pushd/popd.'],
         code='''mkdir -p mods/{auth,billing,reports}; touch mods/auth/{a,b} mods/billing/c
for m in mods/*/; do
  pushd "$m" > /dev/null
  echo "$(basename "$m"): $(ls | wc -l) files"
  popd > /dev/null
done
pwd | sed 's|.*/||'
''', notes={3: 'Enter.', 5: 'Return.', 7: 'Still in the start folder.'}, tryit='Replace pushd/popd with ( cd "$m"; … ).'),
]

QUIZ = mix([
    dict(q='Which expansion happens first?', options=['globbing', 'brace expansion', 'command substitution', 'word splitting'], answer=1, why='Step 1.'),
    dict(q='echo {x,y}.txt when the files do not exist prints…', options=['nothing', 'x.txt y.txt', '{x,y}.txt', 'an error'], answer=1, why='Braces do not check files.'),
    dict(q='cp f{,.bak} runs…', options=['cp f .bak', 'cp f f.bak', 'cp f{,.bak}', 'error'], answer=1, why='Empty item + .bak.'),
    dict(q='Why does cmd="ls | wc -l"; $cmd fail?', options=['ls is broken', 'the pipe is parsed before expansion', 'quotes', 'wc missing'], answer=1, why='Tokens first.'),
    dict(q='Safer than eval for a command with arguments?', options=['backticks', 'an array', 'alias', 'export'], answer=1, why='"${cmd[@]}".'),
    dict(q='popd does…', options=['adds a folder', 'returns to the top folder of the stack and removes it', 'lists the stack', 'deletes a folder'], answer=1, why='Pop.'),
    dict(q='cd - goes…', options=['home', 'to the previous folder', 'up one level', 'to /'], answer=1, why='OLDPWD.'),
    dict(q='<(cmd) gives…', options=['the output text', 'a file name to read the output', 'a pipe symbol', 'a subshell PID'], answer=1, why='/dev/fd/N.'),
])

REVISION = [
    'Metacharacters: ; & && || | < > ( ) { } $ ` \\ " \' * ? [ ] ~ # ! — quote them to use them literally.',
    'Order: tokens/operators → brace → tilde → $var $(( )) $( ) <( ) (left to right) → word splitting → globbing → quote removal.',
    'Braces generate names (no files needed, no variables inside); globs match existing files.',
    '$( ) nests and replaces backticks; $(<file) reads a file; <( ) and >( ) turn commands into files.',
    'eval re-parses text (double expansion, injection risk); prefer arrays, functions, ${!name}.',
    'pushd DIR / popd / dirs -v / pushd +N / cd -.',
]

FAQ = [
    ('What are shell metacharacters?', 'Characters with special meaning to the shell, such as ; & | < > ( ) $ ` \\ " \' * ? [ ] ~ { } and #.'),
    ('In what order does bash expand a command line?', 'Brace, tilde, parameter/arithmetic/command/process substitution, word splitting, pathname expansion, then quote removal.'),
    ('What is brace expansion?', 'Generating words from {a,b,c} or {1..10}, e.g. mkdir -p dir/{a,b}.'),
    ('What does eval do and why is it dangerous?', 'It re-parses its arguments as a command line; with untrusted input it can run arbitrary commands.'),
    ('How do pushd and popd work?', 'pushd changes to a folder and saves the previous one on a stack; popd returns to the folder on top of the stack.'),
    ('What is process substitution?', '<(cmd) provides cmd’s output as a file name, so diff <(cmd1) <(cmd2) compares outputs.'),
    ('Why does {1..$n} not work?', 'Brace expansion happens before variable expansion.'),
]

PRACTICE_INTRO = 'Small expansion tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Brace list', stmt='Print red-1 red-2 blue-1 blue-2 with one echo.', inp='nothing', code="echo {red,blue}-{1,2}\n", explain='Combinations.'),
    dict(level='easy', title='Range', stmt='Print a to f.', inp='nothing', code="echo {a..f}\n", explain='Letter range.'),
    dict(level='easy', title='Home', stmt='Print your home with tilde.', inp='nothing', code="echo ~\n", explain='/home/riya.'),
    dict(level='medium', title='Padded', stmt='Print file01 to file05.', inp='nothing', code="echo file{01..05}\n", explain='Padding.'),
    dict(level='medium', title='Step', stmt='Print 0 to 100 in steps of 25.', inp='nothing', code="echo {0..100..25}\n", explain='Step.'),
    dict(level='medium', title='Indirect', stmt='With v=PATH_NAME and PATH_NAME=demo, print demo without eval.', inp='variables', code="PATH_NAME=demo; v=PATH_NAME; echo \"${!v}\"\n", explain='${!v}.'),
    dict(level='business', title='Stack', stmt='pushd /tmp then /etc; print the stack size, then popd twice and print the folder name.', inp='nothing', code="cd /var; pushd /tmp >/dev/null; pushd /etc >/dev/null; dirs -p | wc -l; popd >/dev/null; popd >/dev/null; pwd\n", explain='3 entries, back to /var.'),
    dict(level='business', title='Process substitution', stmt='Count lines common to two lists with comm and <( ).', inp='two lists', code="comm -12 <(printf 'a\\nb\\nc\\n') <(printf 'b\\nc\\nd\\n') | wc -l\n", explain='2.'),
]

SCN_INTRO = 'Interview questions about expansion, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Create folders jan to dec in one command”', 'Shows brace knowledge.', 'braces?',
        '''<ul>
          <li><code>mkdir {jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec}</code></li>
          <li>Numbers: <code>mkdir month{01..12}</code>.</li>
          <li>Braces do not need existing files.</li>
        </ul>''', '12 separate mkdir commands.') +
    scn('Service company', 'Junior', '“What happens when you type ls *.txt?”', 'Tests understanding of globbing.', 'who expands?',
        '''<ol>
          <li>bash expands *.txt to matching names before ls runs.</li>
          <li>ls receives the list; it never sees *.</li>
          <li>No match: the pattern stays as text (or nullglob).</li>
        </ol>''', '“ls searches for the pattern”.') +
    scn('DevOps', 'Mid-level', 'A script uses eval on a config value', 'Security review flagged it.', 'risk and fix?',
        '''<ul>
          <li>Config text with ; or $( ) would run as code.</li>
          <li>Replace with arrays, case on allowed values, or source a validated file.</li>
          <li>shellcheck SC2294 warns about eval.</li>
        </ul>''', 'escaping by hand.') +
    scn('Platform', 'Senior', 'Compare package lists on 2 servers quickly', 'No temp files allowed on prod.', 'process substitution?',
        '''<ul>
          <li><code>diff &lt;(ssh a rpm -qa | sort) &lt;(ssh b rpm -qa | sort)</code></li>
          <li>Or comm -3 for one-side-only lists.</li>
          <li>Explain /dev/fd and that it needs bash.</li>
        </ul>''', 'copying files around with scp.')
) + interview([
    ('$( ) vs backticks?', 'Same; $( ) nests and is clearer.'),
    ('What is ~+ ?', 'The current folder ($PWD).'),
    ('How to undo a cd?', 'cd -.'),
    ('What does dirs -v show?', 'The numbered directory stack.'),
    ('Which expansions work inside double quotes?', '$var, $( ), $(( )), and backticks.'),
    ('What is word splitting?', 'Splitting unquoted results at IFS characters.'),
    ('Why avoid eval?', 'Double expansion and code injection.'),
], [
    ('RHCSA (EX200)', 'Use shell expansion and command substitution.'),
    ('LFCS', 'Shell expansions and command substitution.'),
    ('CompTIA Linux+', 'Brace expansion, globbing, command substitution.'),
]) + distro('Brace expansion and pushd are bash/zsh features.', [
    ('{a,b} {1..5}', 'bash', 'bash', 'bash/zsh', 'Git Bash'),
    ('~ $( ) $(( ))', 'yes', 'yes', 'yes', '-'),
    ('<( ) >( )', 'bash', 'bash', 'bash/zsh', '-'),
    ('pushd / popd', 'bash', 'bash', 'zsh too', 'PowerShell: Push-Location'),
    ('dash (/bin/sh)', 'no braces, no pushd', '-', '-', '-'),
]) + teaser('12.12', 'Riya rebuilds reports, compresses logs and runs tests by hand, often forgetting a step or redoing work that was already up to date. make reads a Makefile of targets and dependencies and rebuilds only what changed. Next: make and Makefiles.')

CHEATSHEET = cheatsheet('Expansion and stack', [
    ('Braces', [('{a,b}', 'list'), ('{1..9}', 'range'), ('{01..10}', 'padded'), ('{0..20..5}', 'step'), ('f{,.bak}', 'backup')]),
    ('Tilde / subst', [('~ ~user', 'homes'), ('cd -', 'previous'), ('"$(cmd)"', 'output'), ('$(<file)', 'read file'), ('<(cmd)', 'as a file')]),
    ('Order', [('1 brace 2 tilde', 'first'), ('3 $ $( ) $(( ))', 'values'), ('4 split 5 glob', 'words'), ('6 quotes off', 'last')]),
    ('Stack / eval', [('pushd D', 'go + save'), ('popd', 'back'), ('dirs -v', 'show'), ('${!name}', 'indirect'), ('cmd=( … )', 'not eval')]),
])

MINDMAP = mindmap('Expansion', [
    ('Meta', 'red', ['; & | < >', '( ) { }', '$ ` \\ " \'']),
    ('Braces', 'blue', ['{a,b}', '{1..10}', 'no vars']),
    ('Values', 'amber', ['~', '$v $( )', '$(( )) <( )']),
    ('Words', 'green', ['split IFS', 'glob * ?', 'quotes off']),
    ('eval', 'violet', ['re-parse', 'injection', 'use arrays']),
    ('Stack', 'acc', ['pushd', 'popd', 'dirs cd -']),
])

LAB = lab('predict the shell', 'Build the lab, do the four tasks in <code>~/lab1211/tasks.sh</code>, then run the checker.',
    setup='''mkdir -p ~/lab1211 && cd ~/lab1211 && rm -rf tasks.sh site out.txt start.txt''',
    tasks=['With ONE mkdir command, create <code>site/{css,js,img}</code> and <code>site/pages/{home,about,contact}</code>.',
           'Write the words <code>web-dev web-prod db-dev db-prod</code> into <code>out.txt</code> using one brace expression.',
           'Append a line <code>year: YYYY</code> (the real current year) to <code>out.txt</code> using command substitution.',
           'Use pushd to go into <code>site/pages</code>, write <code>$(ls | wc -l)</code> into <code>../../start.txt</code>, then popd back.'],
    solution='''cat > tasks.sh <<'EOF'
mkdir -p site/{css,js,img} site/pages/{home,about,contact}
echo {web,db}-{dev,prod} > out.txt
echo "year: $(date +%Y)" >> out.txt
pushd site/pages > /dev/null
ls | wc -l > ../../start.txt
popd > /dev/null
EOF''',
    check='''cd ~/lab1211; rm -rf site out.txt start.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f tasks.sh ] && bash tasks.sh
ok "1 tree"   '[ -d site/css ] && [ -d site/img ] && [ -d site/pages/contact ] && [ "$(find site -type d | wc -l)" = 8 ]'
ok "2 braces" '[ "$(head -1 out.txt 2>/dev/null)" = "web-dev web-prod db-dev db-prod" ]'
ok "3 year"   'grep -qx "year: $(date +%Y)" out.txt 2>/dev/null'
ok "4 stack"  '[ "$(cat start.txt 2>/dev/null)" = 3 ] && grep -q pushd tasks.sh && grep -q popd tasks.sh' ''')
