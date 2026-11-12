import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='04-quoting-and-expansion-single-vs-double-quotes', n='12.4',
    module_label='Module 12 · The shell environment and shell programming',
    title='Quoting and expansion: single vs double quotes and escaping',
    desc='What the shell expands before running a command; single quotes, double quotes, backslash and $\'…\' ANSI-C quoting; word splitting and IFS, globbing, quote removal; "$@" vs "$*" vs $@ checked with real runs; command substitution $( ) vs backticks; ${var:?} safety; file names with spaces and leading dashes; class-note mistakes corrected; animations.',
    og_desc='Single vs double quotes in Bash, word splitting, "$@" vs "$*" and escaping, shown with real outputs and animations.',
    minutes=35, level='Beginner → Advanced',
    lead='Before running any command the shell rewrites it: variables, command output and wildcards are expanded, then the result is split into words. Quotes decide which steps happen. This lesson makes that visible and shows how to quote correctly.',
    chips=['Word splitting animated', '"$@" vs "$*" really run', 'Safe rm and cp', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Three ways to write the same text
name="Riya"
echo 'Hello $name, today is $(date +%A)'
echo "Hello $name, today is $(date +%A)"
f="my report.txt"
printf '[%s]\\n' $f
printf '[%s]\\n' "$f"
"""

RUN = dict(
    heading='Single vs double quotes, and word splitting',
    intro='<p>Print the same text with single and double quotes, then see a file name split into two words.</p>',
    code=MAIN,
    anno=[("printf '[%s]\\n' $f", 'Unquoted: two words in brackets.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. How many bracket lines does each printf make?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> how many words does each loop see? Then run.',
             code="set -- 'a b' c\nfor x in $@; do echo \"[$x]\"; done\nfor x in \"$@\"; do echo \"<$x>\"; done\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is to print It\'s $5. Fix the quotes.',
             code="echo 'It's $5'\n", expect='any'),
        dict(label='4 · Your turn', hint='Print a tab between two words with $\'…\'.',
             code="echo $'left\\tright' | cat -A\n"),
        dict(label='5 · Challenge', hint='Make rm refuse to run when dir is empty.',
             code="dir=''\n( rm -rf -- \"${dir:?is empty}\"/nothing ) 2>&1 | sed 's/.*: dir/dir/'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: quoting traps',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · A name with a space', cmd="mkdir -p ~/qtest && cd ~/qtest && touch 'My File.txt' && f='My File.txt' && ls $f; ls \"$f\"", output="ls: cannot access 'My': No such file or directory\nls: cannot access 'File.txt': No such file or directory\n'My File.txt'", note='Typical (ls in a terminal shows the quoted name).'),
        dict(title='2 · History ! inside double quotes (interactive only)', cmd='echo "done!"', output='done!', note='Typical: an error only when something follows ! (like "done!x").'),
        dict(title='3 · Your IFS', cmd="printf '%q\\n' \"$IFS\"", output=pc("printf '%q\\n' \"$IFS\""), note='Recorded: space, tab, newline.'),
        dict(title='4 · shellcheck finds quoting bugs', cmd='sudo apt install shellcheck && shellcheck myscript.sh', output='In myscript.sh line 3:\ncp $f backup/\n   ^-- SC2086 (info): Double quote to prevent globbing and word splitting.', note='Typical.'),
    ],
)

TRACE = dict(
    heading='One value, quoted and unquoted',
    intro='<p>Step through: a value with spaces counted as words with and without quotes.</p>',
    code='''v="red green blue"
set -- $v
unquoted=$#
set -- "$v"
quoted=$#
echo "unquoted: $unquoted words, quoted: $quoted word"
''',
    notes={1: 'A value with spaces.', 2: 'Unquoted :: split into 3.', 3: 'Count.', 4: 'Quoted :: stays 1.', 6: 'Summary.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a report message, a safe copy and an awk program.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='A message with variables and literal $',
         problem='<p>Print “Riya owes $250 (due 2026)” using variables for the name and the year.</p>',
         inp='two variables', approach=['Double quotes.', '\\$ for the literal dollar.'],
         code='''who=Riya; amount=250; year=2026
echo "$who owes \\$$amount (due $year)"
''', notes={2: '\\$ then $amount.'}, tryit='Write it with single quotes around the fixed parts.'),
    dict(level='i', tag='Admin', title='Copy files with awkward names',
         problem='<p>Copy every .txt file, including names with spaces and a leading dash, into a folder.</p>',
         inp='awkward names', approach=['Glob.', '"$f".', '--.'],
         code='''mkdir -p src out; touch 'src/Q3 report.txt' src/-x.txt src/ok.txt
for f in src/*.txt; do cp -- "$f" out/; done
ls out | cat
''', notes={2: 'Every name is one word.'}, tryit='Remove the quotes around $f and see what breaks.'),
    dict(level='a', tag='Data', title='awk inside a shell script',
         problem='<p>Sum the second column of a CSV with awk, passing a shell variable safely.</p>',
         inp='a CSV', approach=['awk program in single quotes.', '-v for the shell value.'],
         code='''printf 'a,10\\nb,20\\nc,30\\n' > data.csv
min=15
awk -F, -v m="$min" '$2 > m { s += $2 } END { print "sum above", m ":", s }' data.csv
''', notes={3: 'awk sees $2; the shell value comes in through -v.'}, tryit='Try putting the awk program in double quotes.'),
]

QUIZ = mix([
    dict(q="What does echo '$HOME' print?", options=['/home/you', '$HOME', 'nothing', 'an error'], answer=1, why='Single quotes: literal.'),
    dict(q='What does echo "$HOME" print?', options=['/home/you', '$HOME', '"$HOME"', 'an error'], answer=0, why='Double quotes expand $.'),
    dict(q='Why quote "$f" in cp "$f" dest/?', options=['speed', 'to keep a name with spaces as one word', 'to make it read-only', 'it is required syntax'], answer=1, why='No word splitting.'),
    dict(q='Which passes all arguments unchanged?', options=['$*', '$@', '"$*"', '"$@"'], answer=3, why='Each kept whole.'),
    dict(q='Inside double quotes, which still expands?', options=['*', '~', '$var', 'none'], answer=2, why='$ ` \\ stay special.'),
    dict(q="How to print it's with single quotes only?", options=["'it\\'s'", "'it'\\''s'", "'it''s'", 'impossible'], answer=1, why='Close, \\\', reopen.'),
    dict(q='What does ${dir:?} do when dir is empty?', options=['uses /', 'prints an error and stops', 'uses .', 'nothing'], answer=1, why='Guard.'),
    dict(q="echo $'a\\tb' prints…", options=['a\\tb', 'a<TAB>b', '$a\\tb', 'ab'], answer=1, why='ANSI-C quoting.'),
])

REVISION = [
    "'single' = all literal; \"double\" = $ ` \\ still work, but no splitting, no wildcards, no ~.",
    'Unquoted expansions are split at IFS (space, tab, newline) and globbed: quote every "$var" and "$(cmd)".',
    '\\ protects one character; $\'…\' understands \\n \\t \\\'.',
    '"$@" = each argument whole (use it); "$*" = one string; $@/$* unquoted = split again.',
    'Quotes are removed before the program runs; for names starting with -, use -- or ./.',
    "Guard dangerous commands with ${var:?}; debug with printf '[%s]\\n' and set -x.",
]

FAQ = [
    ('What is the difference between single and double quotes in bash?', 'Single quotes keep every character literal; double quotes still expand $variables, $(commands), arithmetic and backslash escapes, but prevent word splitting and globbing.'),
    ('Why should I quote variables in bash?', 'Unquoted values are split at spaces and wildcards are expanded, which breaks file names with spaces and can widen commands like rm.'),
    ('What is the difference between $@ and $*?', '"$@" expands to each argument as a separate word; "$*" joins all arguments into one string. Unquoted, both are split again.'),
    ('How do I put a single quote inside single quotes?', "You cannot; close the quote, add \\', and reopen: 'it'\\''s', or use double quotes \"it's\"."),
    ('How do I print a literal dollar sign?', "Use \\$ inside double quotes, or single quotes: 'Cost $5'."),
    ('What does $\'...\' mean in bash?', 'ANSI-C quoting: escapes like \\n, \\t and \\\' are turned into the real characters.'),
    ('How do I handle a file name starting with a dash?', 'Use -- to end options (rm -- -file) or a path (./-file).'),
]

PRACTICE_INTRO = 'Small quoting tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Literal', stmt='Print $USER literally.', inp='nothing', code="echo '$USER'\n", explain='Single quotes.'),
    dict(level='easy', title='Expanded', stmt='Print “Hi ” followed by the value of v.', inp='a variable', code="v=Riya; echo \"Hi $v\"\n", explain='Double quotes.'),
    dict(level='easy', title='Count words', stmt='Count the words in an unquoted value with three words.', inp='a variable', code="v='a b c'; set -- $v; echo $#\n", explain='Split: 3.'),
    dict(level='medium', title='Keep one', stmt='Same value, quoted: count words.', inp='a variable', code="v='a b c'; set -- \"$v\"; echo $#\n", explain='1.'),
    dict(level='medium', title='Dollar price', stmt='Print Price: $9 with the 9 from a variable.', inp='a variable', code="p=9; echo \"Price: \\$$p\"\n", explain='\\$ then $p.'),
    dict(level='medium', title='Quote in text', stmt="Print It's done using double quotes.", inp='nothing', code="echo \"It's done\"\n", explain='Double quotes.'),
    dict(level='business', title='All args', stmt='With args "x y" and z, print each argument in brackets.', inp='set --', code="set -- 'x y' z; printf '[%s]\\n' \"$@\"\n", explain='"$@".'),
    dict(level='business', title='Join', stmt='Join the arguments a, b, c with a hyphen.', inp='set --', code="set -- a b c; ( IFS=-; echo \"$*\" )\n", explain='IFS + "$*".'),
]

SCN_INTRO = 'Interview questions about quoting, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Single vs double quotes?”', 'Asked in almost every shell interview.', 'clear rules?',
        '''<ul>
          <li>Single: everything literal.</li>
          <li>Double: $, `, \\ still work; no splitting or wildcards.</li>
          <li>Example: <code>'$HOME'</code> vs <code>"$HOME"</code>.</li>
        </ul>''', 'saying they are the same.') +
    scn('Product company', 'Junior', 'Backup fails on “Q3 report.xlsx”', 'Works for other files.', 'word splitting?',
        '''<ol>
          <li>The variable is unquoted: the name is split.</li>
          <li>Quote it: <code>"$f"</code>.</li>
          <li>Run shellcheck on all scripts (SC2086).</li>
        </ol>''', 'renaming the user’s files.') +
    scn('DevOps', 'Mid-level', 'Wrapper loses arguments with spaces', 'docker run … "hello world" arrives as two.', '"$@"?',
        '''<ul>
          <li>The entrypoint uses <code>$*</code> or unquoted <code>$@</code>.</li>
          <li>Use <code>exec "$@"</code>.</li>
          <li>Test with an argument containing spaces.</li>
        </ul>''', 'adding more quotes everywhere at random.') +
    scn('SRE', 'Senior', 'Script deleted most of a server', 'rm -rf $TARGET/ with TARGET empty.', 'prevention?',
        '''<ul>
          <li><code>set -euo pipefail</code> (Lesson 12.6), <code>"${TARGET:?}"</code>.</li>
          <li>Quote everything; shellcheck in CI; run as a limited user.</li>
          <li>Dry run (echo) before destructive commands.</li>
        </ul>''', 'blaming the junior who ran it.')
) + interview([
    ('What is word splitting?', 'Cutting the result of an unquoted expansion into words at IFS characters.'),
    ('What is IFS?', 'Internal Field Separator: space, tab and newline by default.'),
    ('$(cmd) vs backticks?', 'Same result; $( ) nests and reads better.'),
    ('How to pass all arguments to another command?', 'cmd "$@".'),
    ('Does echo "*" list files?', 'No, quotes stop globbing.'),
    ('How to print a tab?', "printf '\\t' or echo $'\\t'."),
    ('Why does [ $x = y ] fail when x is empty?', 'The empty value disappears; quote it.'),
], [
    ('RHCSA (EX200)', 'Use shell expansion and quoting in scripts.'),
    ('LFCS', 'Shell scripting: quoting and substitution.'),
    ('CompTIA Linux+', 'Quoting, escaping and command substitution.'),
]) + distro('POSIX quoting is the same everywhere; extras differ.', [
    ("' ' and \" \"", 'yes', 'yes', 'yes (zsh)', 'PowerShell: similar idea'),
    ("$' '", 'bash', 'bash', 'zsh: yes', '-'),
    ('Word splitting of $var', 'yes', 'yes', 'zsh: no by default!', '-'),
    ('dash ($\'…\')', 'no', '-', '-', '-'),
    ('Lint tool', 'shellcheck', 'shellcheck', 'shellcheck', 'PSScriptAnalyzer'),
]) + teaser('12.5', 'Riya now writes commands that survive any file name. Time to put them in a file and run it like a program: the #! line, chmod +x, ./script and comments. Next: your first shell script.')

CHEATSHEET = cheatsheet('Quoting', [
    ('Kinds', [("'…'", 'literal'), ('"…"', '$ ` \\ only'), ('\\x', 'one char'), ("$'\\t\\n'", 'C escapes')]),
    ('Always', [('"$var"', 'one word'), ('"$(cmd)"', 'output'), ('"$@"', 'all args'), ('"${v:?}"', 'not empty')]),
    ('Tricks', [("'it'\\''s'", "quote in '"), ('\\$  \\"', 'in "…"'), ('-- "$f"', 'names with -'), ('IFS=,; "$*"', 'join')]),
    ('Debug', [("printf '[%s]\\n'", 'see words'), ('set -x', 'trace'), ('shellcheck', 'lint'), ('cat -A', 'see tabs')]),
])

MINDMAP = mindmap('Quoting', [
    ('Single', 'green', ['literal', 'no $', 'no inner \'']),
    ('Double', 'blue', ['$ ` \\', 'one word', 'no glob']),
    ('None', 'red', ['split', 'glob', '~']),
    ('Escape', 'violet', ['\\x', "$'\\t'", 'line end']),
    ('Args', 'amber', ['"$@" ✓', '"$*" join', '$@ split']),
    ('Safety', 'acc', ['${v:?}', '--', 'shellcheck']),
])

LAB = lab('fix a script', 'Build the lab: <code>copy.sh</code> has four quoting bugs. Fix them (keep the file name), then run the checker.',
    setup='''mkdir -p ~/lab124 && cd ~/lab124 && rm -rf in out copy.sh
mkdir -p in; touch 'in/Q3 report.txt' in/-v.txt in/plain.txt
cat > copy.sh <<'EOF'
dest=$1
mkdir -p $dest
for f in in/*.txt; do cp $f $dest/; done
echo 'copied to $dest'
EOF''',
    tasks=['Quote the variable in the <code>mkdir</code> line.',
           'Quote both variables in the <code>cp</code> line and protect names that start with a dash.',
           'Make the last line print the real folder name (it prints <code>$dest</code> literally now).',
           'Make the script stop with an error when no destination is given (use <code>${1:?…}</code>).'],
    solution='''cat > copy.sh <<'EOF'
dest=${1:?usage: copy.sh DEST}
mkdir -p "$dest"
for f in in/*.txt; do cp -- "$f" "$dest/"; done
echo "copied to $dest"
EOF''',
    check='''cd ~/lab124; rm -rf 'my out'
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
out=$(bash copy.sh 'my out' 2>&1)
ok "1 mkdir"   '[ -d "my out" ]'
ok "2 cp"      '[ -f "my out/Q3 report.txt" ] && [ -f "my out/-v.txt" ]'
ok "3 message" '[ "$(printf "%s" "$out" | tail -1)" = "copied to my out" ]'
ok "4 guard"   '! bash copy.sh > /dev/null 2>&1 && bash copy.sh 2>&1 | grep -q usage' ''')
