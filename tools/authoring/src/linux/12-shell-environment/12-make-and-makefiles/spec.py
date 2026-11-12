import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='12-make-and-makefiles', n='12.12',
    module_label='Module 12 · The shell environment and shell programming',
    title='make and Makefiles: targets, prerequisites, recipes, variables and pattern rules',
    desc='GNU make from zero: rules (target, prerequisites, TAB recipe), how timestamps decide what is rebuilt, variables (= := ?= +=), automatic variables $@ $< $^ $? $*, pattern rules, wildcard/patsubst/shell functions, .PHONY, ifeq, -n -B -j -C -k -s, errors like missing separator; C, Python and data-pipeline Makefiles with real outputs and 30+ examples.',
    og_desc='make and Makefiles explained with real runs: rules, timestamps, variables, pattern rules, .PHONY and parallel builds.',
    minutes=40, level='Beginner → Advanced',
    lead='make reads a Makefile of targets, prerequisites and recipes and rebuilds only what is out of date, in the right order. Used for C programs, the Linux kernel, CI task runners and data pipelines.',
    chips=['Dependency graph animated', 'C and data Makefiles', 'Timestamp traps explained', 'Practice lab with checker', 'Real outputs'],
)

MAIN = """# make's core idea in plain bash: rebuild only if the input is newer
echo 'b a c' > in.txt
build(){ if [ ! -e out.txt ] || [ in.txt -nt out.txt ]; then
           tr ' ' '\\n' < in.txt | sort > out.txt; echo "rebuilt out.txt"
         else echo "out.txt is up to date"; fi; }
build
build
sleep 1; echo 'd' >> in.txt
build
cat out.txt
"""

RUN = dict(
    heading='The idea behind make, in bash',
    intro='<p>The browser has no make, so this simulates its rule with <code>[ in -nt out ]</code> (“in is newer than out”). The real make runs are in <b>Run on your PC</b>.</p>',
    code=MAIN,
    anno=[('[ in.txt -nt out.txt ]', 'The exact test make does for every rule.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Why does the second build do nothing?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which file is newer?',
             code="touch a; sleep 1; touch b\n[ b -nt a ] && echo 'b is newer' || echo 'a is newer'\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the input changed but has an old timestamp (like cp -p). Fix it with touch in.',
             code="echo x > out; echo new > in; touch -d '1 hour ago' in\n[ in -nt out ] && echo rebuild || echo 'up to date (old timestamp!)'\n"),
        dict(label='4 · Your turn', hint='Write a TAB-indented recipe line into a Makefile and show it with cat -A.',
             code="printf 'all:\\n\\techo hi\\n' > Makefile\ncat -A Makefile\n"),
        dict(label='5 · Challenge', hint='Simulate two steps: sorted.txt from raw.txt, then top.txt from sorted.txt.',
             code="echo '3 1 2' > raw.txt\nstep(){ [ -e \"$2\" ] && [ ! \"$1\" -nt \"$2\" ] && { echo \"$2 ok\"; return; }; eval \"$3\"; echo \"made $2\"; }\nstep raw.txt sorted.txt \"tr ' ' '\\\\n' < raw.txt | sort -n > sorted.txt\"\nstep sorted.txt top.txt 'head -1 sorted.txt > top.txt'\nstep sorted.txt top.txt 'head -1 sorted.txt > top.txt'\ncat top.txt\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real make',
    intro='<p>Install with <code>sudo apt install make gcc</code> (Ubuntu) or <code>sudo dnf install make gcc</code>. Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Version', cmd='make --version | head -1', output=pc('make --version | head -1'), note='Recorded.'),
        dict(title='2 · Smallest Makefile', cmd="printf 'hi:\\n\\t@echo hello from make\\n' > Makefile && make", output=pc("cd /tmp && rm -rf pcm && mkdir pcm && cd pcm && printf 'hi:\\n\\t@echo hello from make\\n' > Makefile && make"), note='Recorded.'),
        dict(title='3 · Up to date', cmd="printf 'o: i\\n\\tcp i o\\n' > Makefile; echo x > i; make; make", output=pc("cd /tmp && rm -rf pcm && mkdir pcm && cd pcm && printf 'o: i\\n\\tcp i o\\n' > Makefile; echo x > i; make; make"), note='Recorded.'),
        dict(title='4 · Build a real project', cmd='git clone https://github.com/… && cd … && make -j$(nproc)', output='gcc -c …\n…\n(many lines)', note='Typical.'),
    ],
)

TRACE = dict(
    heading='make’s decision, line by line',
    intro='<p>Step through the timestamp test make performs for one rule.</p>',
    code='''echo data > in.txt
sleep 1
cp in.txt out.txt
if [ in.txt -nt out.txt ]; then echo rebuild; else echo up-to-date; fi
sleep 1
echo more >> in.txt
if [ in.txt -nt out.txt ]; then echo rebuild; else echo up-to-date; fi
''',
    notes={3: 'out.txt is now newer.', 4: 'Prints up-to-date.', 6: 'The input changes.', 7: 'Prints rebuild.'},
)

WORKED_INTRO = 'Three Makefiles from real jobs. The browser runs the shell parts; the make runs are shown on this page and in Run on your PC.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Generate a Makefile and check its TABs',
         problem='<p>Write a two-target Makefile with printf and confirm the recipe lines start with a TAB.</p>',
         inp='nothing', approach=['printf with \\t.', 'cat -A shows ^I.'],
         code='''printf 'all: build\\nbuild:\\n\\techo building\\n.PHONY: all build\\n' > Makefile
cat -A Makefile
grep -c $'^\\t' Makefile
''', notes={2: '^I = TAB, $ = end of line.'}, tryit='Replace \\t with four spaces and count again.'),
    dict(level='i', tag='Data', title='Which steps are stale?',
         problem='<p>Given raw → clean → report files, list which outputs are older than their input.</p>',
         inp='three files', approach=['-nt for each pair.'],
         code='''touch -d '10:00' report.txt; touch -d '11:00' raw.csv; touch -d '09:00' clean.csv
for pair in raw.csv:clean.csv clean.csv:report.txt; do
  in=${pair%%:*}; out=${pair##*:}
  [ "$in" -nt "$out" ] && echo "stale: $out (older than $in)" || echo "ok: $out"
done
''', notes={4: 'clean.csv is stale; report.txt is newer than clean.csv.'}, tryit='touch clean.csv and run the loop again.'),
    dict(level='a', tag='DevOps', title='List targets of a Makefile',
         problem='<p>Print every target with its ## help text, like a make help target.</p>',
         inp='a Makefile', approach=['grep rules with ##.', 'sed to format.'],
         code='''printf 'build: ## compile\\n\\techo b\\ntest: ## run tests\\n\\techo t\\nclean: ## remove files\\n\\techo c\\n' > Makefile
grep -E '^[a-z]+:.*##' Makefile | sed 's/:.*## / -> /'
''', notes={2: 'The same trick a help target uses.'}, tryit='Sort the targets alphabetically.'),
]

QUIZ = mix([
    dict(q='A recipe line must start with…', options=['four spaces', 'a TAB', '@', 'a colon'], answer=1, why='Otherwise: missing separator.'),
    dict(q='make rebuilds a target when…', options=['always', 'it is missing or older than a prerequisite', 'it is newer', 'once a day'], answer=1, why='Timestamps.'),
    dict(q='$@ in a recipe means…', options=['all prerequisites', 'the target', 'the first prerequisite', 'the shell PID'], answer=1, why='Target.'),
    dict(q='$< means…', options=['the first prerequisite', 'the target', 'changed files', 'all files'], answer=0, why='First input.'),
    dict(q='Why declare .PHONY: clean?', options=['to speed up', 'so a file named clean cannot block it', 'to hide output', 'required syntax'], answer=1, why='Not a file.'),
    dict(q='make -n…', options=['builds n times', 'shows commands without running', 'uses n cores', 'no output'], answer=1, why='Dry run.'),
    dict(q='Each recipe line runs…', options=['in one shell for the whole rule', 'in its own shell', 'in make itself', 'in Python'], answer=1, why='cd is forgotten.'),
    dict(q='Which runs recipes in parallel?', options=['-p', '-j', '-k', '-C'], answer=1, why='jobs.'),
])

REVISION = [
    'Rule: target: prerequisites, then TAB-indented recipe lines.',
    'Rebuild if the target is missing or older than a prerequisite; prerequisites are built first.',
    'Variables: = (lazy), := (now), ?= (default), += (append); use $(VAR); $$ for a shell $.',
    'Automatic: $@ target, $< first prerequisite, $^ all, $? newer ones, $* stem.',
    'Pattern rule %.o: %.c; functions wildcard, patsubst, shell; .PHONY for actions.',
    'Options: -n dry, -B force, -j parallel, -C dir, -f file, -k keep going, -s silent.',
]

FAQ = [
    ('What is make in Linux?', 'A build tool that reads a Makefile and rebuilds only targets whose prerequisites changed.'),
    ('What does “missing separator” mean?', 'A recipe line starts with spaces instead of a TAB.'),
    ('What is a phony target?', 'A target that is an action (clean, test) rather than a file; declare it in .PHONY.'),
    ('What are $@, $< and $^?', 'The target, the first prerequisite and all prerequisites.'),
    ('How do I build faster?', 'make -j$(nproc) runs independent recipes in parallel.'),
    ('Why does cd in a recipe not work on the next line?', 'Each line runs in its own shell; join with && or use .ONESHELL.'),
    ('Is make only for C?', 'No: it is used for docs, data pipelines, Docker builds and as a task runner.'),
]

PRACTICE_INTRO = 'Small tasks that write and inspect Makefiles with the shell. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='TAB check', stmt='Write all:⏎<TAB>echo ok into Makefile and show it with cat -A.', inp='nothing', code="printf 'all:\\n\\techo ok\\n' > Makefile; cat -A Makefile\n", explain='^I is the TAB.'),
    dict(level='easy', title='Newer?', stmt='Create a, wait 1 s, create b; print which is newer.', inp='nothing', code="touch a; sleep 1; touch b; [ b -nt a ] && echo b\n", explain='-nt.'),
    dict(level='easy', title='Count rules', stmt='Count lines ending a target name with : in a sample Makefile.', inp='a Makefile', code="printf 'a: b\\n\\tx\\nb:\\n\\ty\\n' > M; grep -cE '^[a-z]+:' M\n", explain='2 rules.'),
    dict(level='medium', title='Objects list', stmt='Turn main.c util.c into main.o util.o with sed (like patsubst).', inp='names', code="echo 'main.c util.c' | sed 's/\\.c/.o/g'\n", explain='Same as $(SRC:.c=.o).'),
    dict(level='medium', title='Stale outputs', stmt='Print out if in.txt is newer than out.txt, else ok.', inp='two files', code="touch out.txt; sleep 1; touch in.txt; [ in.txt -nt out.txt ] && echo out || echo ok\n", explain='out.'),
    dict(level='medium', title='Help text', stmt='Print targets and their ## comments.', inp='a Makefile', code="printf 'build: ## compile\\ntest: ## check\\n' > M; sed -n 's/:.*## / = /p' M\n", explain='build = compile.'),
    dict(level='business', title='Pipeline order', stmt='Given report needs clean needs raw, print the build order.', inp='deps', code="printf 'clean raw\\nreport clean\\n' | tsort | tac\n", explain='tsort sorts dependencies, as make does: raw, clean, report.'),
    dict(level='business', title='Cores', stmt='Print the make -j option for this machine.', inp='nothing', code="echo \"make -j$(nproc)\" | sed 's/[0-9]*$/N/'\n", explain='nproc.'),
]

SCN_INTRO = 'Interview questions about make, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is a Makefile?”', 'Common in C and Linux rounds.', 'parts?',
        '''<ul>
          <li>A file of rules: target, prerequisites, recipe (TAB).</li>
          <li>make rebuilds only out-of-date targets, using timestamps.</li>
          <li>Example: hello: hello.o greet.o.</li>
        </ul>''', '“a script that compiles”.') +
    scn('Service company', 'Junior', '“make clean does nothing”', 'A file named clean exists.', 'fix?',
        '''<ol>
          <li>ls shows a file called clean.</li>
          <li>Add .PHONY: clean.</li>
          <li>Never redirect output into a file named like a target.</li>
        </ol>''', 'deleting the Makefile.') +
    scn('Product company', 'Mid-level', 'Random failures only with make -j8', 'Serial builds pass.', 'cause?',
        '''<ul>
          <li>A missing prerequisite: a target uses a file without listing it.</li>
          <li>With -j the order changes and the file is not ready.</li>
          <li>Add the dependency; check with make -j1 and --trace.</li>
        </ul>''', 'removing -j forever.') +
    scn('Platform', 'Senior', 'Standardise tasks across 40 repos', 'Each repo has different commands.', 'make as interface?',
        '''<ul>
          <li>Every repo exposes make build, test, lint, docker, help.</li>
          <li>CI just calls make test.</li>
          <li>Shared include file for common rules.</li>
        </ul>''', 'a wiki page nobody reads.')
) + interview([
    ('= vs := ?', 'Lazy vs immediate expansion.'),
    ('What is $?', 'Prerequisites newer than the target.'),
    ('How to pass a $ to the shell?', '$$.'),
    ('What is the default goal?', 'The first target in the Makefile.'),
    ('What does make -C do?', 'Changes to a folder before reading its Makefile.'),
    ('Why use $(MAKE)?', 'Recursive make passes options and -j correctly.'),
    ('What generates Makefiles?', 'CMake, Autotools (./configure), Meson (ninja).'),
], [
    ('RHCSA / LFCS', 'Build and install software from source (make, make install).'),
    ('Linux kernel builds', 'make menuconfig, make -j.'),
    ('DevOps interviews', 'make as a CI task runner.'),
]) + distro('GNU make is the same everywhere; only the install command differs.', [
    ('Install', 'apt install make', 'dnf install make', 'xcode-select --install', 'MSYS2 / WSL'),
    ('Version', 'GNU Make 4.3', 'GNU Make 4.3/4.4', 'GNU Make 3.81 (old)', '-'),
    ('Build essentials', 'build-essential', '"Development Tools"', 'Xcode tools', '-'),
    ('BSD make', '-', '-', 'bsdmake', 'FreeBSD default'),
]) + teaser('12.13', 'Riya keeps server names in variables called server1, server2, server3… and loops with eval. Bash has real arrays: a list in one variable, and associative arrays that map names to values. Next: arrays.')

CHEATSHEET = cheatsheet('make', [
    ('Rule', [('target: prereqs', 'header'), ('<TAB>cmd', 'recipe'), ('@cmd', 'quiet'), ('-cmd', 'ignore error')]),
    ('Variables', [('A = v', 'lazy'), ('A := v', 'now'), ('A ?= v', 'default'), ('$@ $< $^ $?', 'automatic'), ('$$', 'shell $')]),
    ('Patterns', [('%.o: %.c', 'pattern rule'), ('$(wildcard *.c)', 'list'), ('$(SRC:.c=.o)', 'rename'), ('.PHONY: clean', 'actions')]),
    ('Run', [('make -n', 'dry'), ('make -B', 'force'), ('make -j4', 'parallel'), ('make -C d', 'folder'), ('make V=x', 'override')]),
])

MINDMAP = mindmap('make', [
    ('Rules', 'blue', ['target', 'prerequisites', 'TAB recipe']),
    ('Decide', 'amber', ['timestamps', 'missing → build', 'graph order']),
    ('Variables', 'green', ['= := ?=', '$@ $< $^', '$$']),
    ('Patterns', 'violet', ['%.o: %.c', 'wildcard', 'patsubst']),
    ('Phony', 'red', ['clean', 'test all', '.PHONY']),
    ('Options', 'acc', ['-n -B', '-j -C', '-k -s']),
])

LAB = lab('a data Makefile', 'Build the lab, write <code>~/lab1212/Makefile</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab1212 && cd ~/lab1212 && rm -f Makefile *.txt clean
printf 'city,amount\\npune,100\\ndelhi,250\\npune,50\\n' > sales.csv''',
    tasks=['A target <code>totals.txt</code> that depends on <code>sales.csv</code> and writes the total per city, sorted (e.g. <code>delhi 250</code>, <code>pune 150</code>), using awk.',
           'A target <code>top.txt</code> that depends on <code>totals.txt</code> and writes the city with the largest total.',
           'An <code>all</code> target listed first that builds <code>top.txt</code>.',
           'A phony <code>clean</code> that removes both .txt files.'],
    solution='''cat > Makefile <<'EOF'
all: top.txt

totals.txt: sales.csv
	awk -F, 'NR>1{s[$$1]+=$$2} END{for(c in s) print c, s[c]}' sales.csv | sort > $@

top.txt: totals.txt
	sort -k2,2nr totals.txt | head -1 | cut -d' ' -f1 > $@

.PHONY: all clean
clean:
	rm -f totals.txt top.txt
EOF''',
    check='''cd ~/lab1212
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f Makefile ] && make -s clean >/dev/null 2>&1; [ -f Makefile ] && make -s >/dev/null 2>&1
ok "1 totals"  '[ "$(cat totals.txt 2>/dev/null)" = "$(printf "delhi 250\\npune 150")" ]'
ok "2 top"     '[ "$(cat top.txt 2>/dev/null)" = delhi ]'
ok "3 all"     '[ "$(grep -m1 -oE "^[a-z.]+:" Makefile 2>/dev/null)" = "all:" ]'
ok "4 clean"   'grep -q "^.PHONY:.*clean" Makefile 2>/dev/null && touch clean && make -s clean >/dev/null 2>&1 && [ ! -e totals.txt ] && rm -f clean' ''')
