import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# a C project and a data project, recreated for each example
MK = r"""rm -rf ~/mk; mkdir -p ~/mk/c ~/mk/data; cd ~/mk/c
cat > hello.c <<'EOF'
#include <stdio.h>
#include "greet.h"
int main(void){ greet("Riya"); return 0; }
EOF
cat > greet.c <<'EOF'
#include <stdio.h>
#include "greet.h"
void greet(const char *n){ printf("Hello, %s!\n", n); }
EOF
printf 'void greet(const char *n);\n' > greet.h
cat > Makefile <<'EOF'
CC = gcc
CFLAGS = -Wall -O2
OBJS = hello.o greet.o

hello: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^

%.o: %.c greet.h
	$(CC) $(CFLAGS) -c $<

clean:
	rm -f hello *.o

.PHONY: clean
EOF
cd ~/mk/data; printf 'name,city\nriya,pune\naman,delhi\nzoya,pune\n' > sales.csv
cat > Makefile <<'EOF'
report.txt: sales.csv
	tail -n +2 sales.csv | cut -d, -f2 | sort | uniq -c > report.txt

.PHONY: clean
clean:
	rm -f report.txt
EOF"""

HOOK = hook('Riya’s project has ten C files. After changing one, she runs <code>gcc *.c -o app</code>, waiting for all ten to compile again. Her data job is the same: she reruns every step of a report even when only the last input changed, and sometimes forgets a step. <b>make</b> fixes both. A <b>Makefile</b> lists <b>targets</b> (files to build), their <b>prerequisites</b> (files they depend on) and the <b>recipe</b> (commands). make compares file times and rebuilds <i>only</i> what is out of date, in the right order. It is used to build the Linux kernel, C programs, documentation sites, Docker images and data pipelines.',
    ['write a Makefile with targets, prerequisites and tab-indented recipes',
     'explain how make decides what to rebuild from timestamps, and read its messages',
     'use variables, automatic variables ($@ $< $^), pattern rules and .PHONY targets',
     'run make with -n, -B, -j, -C, -f and VAR=value, and fix “missing separator” and “No rule to make target”'])
ROAD = roadmap([
    ('story', 'The story', 3, 'rebuild only what changed'),
    ('decide', 'Which form when?', 2, 'the quick chart'),
    ('definition', 'What make is', 6, 'simple meaning + 4 depths'),
    ('types', 'Parts of a Makefile', 5, 'rules, variables, patterns'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'the dependency graph'),
    ('run', 'Run on your PC', 4, 'make is not in the browser'),
    ('lab', 'Practice lab', 7, 'a data Makefile'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which form? (decide in 5 seconds)', [
    ('Build everything that is out of date', 'make', 'first target'),
    ('Build one target', 'make report.txt', 'named target'),
    ('See what would run, without running', 'make -n', 'dry run'),
    ('Force a full rebuild', 'make -B   or   make clean && make', 'always'),
    ('Use all CPU cores', 'make -j$(nproc)', 'parallel'),
    ('Makefile in another folder', 'make -C src', 'change dir'),
    ('Override a variable', 'make CFLAGS=-g', 'command line'),
    ('A target that is not a file', '.PHONY: clean test', 'phony'),
])

cmap = concept_map(
    [('12.5', 'Shell scripts', 'commands in a file'), ('12.11', 'Expansion', '$ and wildcards'), ('3.6', 'Timestamps', 'ls -l, touch')],
    ['targets, prerequisites, recipes', 'timestamps decide what is rebuilt', 'variables and $@ $< $^', 'pattern rules %.o: %.c', '.PHONY, -n, -B, -j, -C'],
    [('14.4', 'Building from source', './configure && make && sudo make install'), ('17.3', 'systemd timers', 'run make on a schedule'), ('20.4', 'DevOps', 'make in CI pipelines')],
    'A Makefile is a recipe book with a memory: make rebuilds only the dishes whose ingredients changed.')

sc = (term(20, 14, 316, 156, ['$ make', ('gcc -Wall -O2 -c hello.c', 'out'), ('gcc -Wall -O2 -c greet.c', 'out'), ('gcc -Wall -O2 -o hello hello.o greet.o', 'out'), '$ make', ("make: 'hello' is up to date.", 'acc')], title='riya@web01: ~/mk/c', prompt='riya@web01:~/mk/c$', size=6.8, step=17)
      + t(352, 36, 'Second run:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['nothing changed', '→ nothing to do', 'edit greet.c', '→ only greet.o', '   and hello rebuilt'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Rebuild only what changed</h2>
  <div class="story">
''' + puzzle('Riya writes a Makefile in an editor that turns tabs into four spaces. make answers <code>Makefile:2: *** missing separator.  Stop.</code> She fixes it. Later she restores yesterday’s <code>sales.csv</code> from a backup with <code>cp -p</code>, and make says “up to date” even though the data changed. Then she makes a target named <code>clean</code>, and one day it stops working: <code>make: \'clean\' is up to date.</code> What is going on in each case?') + '''
    <p class="narration">Riya runs make twice. The first time it compiles; the second time it does nothing.</p>
''' + scene('A terminal: the first make compiles two files and links them; the second make says hello is up to date.', sc,
            'make compares <tspan font-weight="700" class="s-acc">file times</tspan> and skips work that is already done.') + '''
K> How does it know nothing changed?
A> Every target has prerequisites. If the target file is <b>newer</b> than all of them, it is up to date. If any prerequisite is newer, or the target is missing, make runs the recipe.
R> So if I edit only greet.c…
A> …make recompiles greet.o and relinks hello, and leaves hello.o alone. On a project with 30,000 files, like the Linux kernel, that is the difference between hours and seconds. Today: Makefile syntax, variables, patterns, phony targets and the options you will use.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A recipe card: the dish (target), the ingredients (prerequisites) and the steps (recipe). The cook makes the dish again only if an ingredient is fresher than the dish.">'
       + label_box(20, 24, 180, 120, ['DISH (target)', 'report.txt', '', 'made at 10:05'], 'green', 9)
       + label_box(230, 24, 180, 120, ['INGREDIENTS', '(prerequisites)', 'sales.csv', 'changed 10:20'], 'amber', 9)
       + label_box(440, 24, 180, 120, ['STEPS (recipe)', '<TAB> cut | sort', '<TAB> uniq -c', '> report.txt'], 'blue', 9)
       + t(320, 172, 'Ingredient newer than the dish → cook again.', 10, 'acc', bold=True)
       + t(320, 194, 'Dish newer than every ingredient → nothing to do.', 9.6, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('make at four depths', [
    ('v', 'No jargon: a recipe card with a memory', '      <p>Each card says what to make, from what, and how.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>make</code>: build the first target in ./Makefile.</li>
        <li><code>make clean</code>: run the clean target.</li>
        <li><code>make -n</code>: show the commands without running them.</li>
        <li>A rule: <code>target: prerequisites</code>, then recipe lines that start with a <b>TAB</b>.</li>
      </ul>'''),
    ('i', 'Variables and patterns', '''      <ul>
        <li><code>CC = gcc</code>, used as <code>$(CC)</code>.</li>
        <li><code>$@</code> the target, <code>$&lt;</code> the first prerequisite, <code>$^</code> all prerequisites.</li>
        <li>Pattern rule <code>%.o: %.c</code>: how to make any .o from its .c.</li>
        <li><code>.PHONY: clean</code>: clean is a name, not a file.</li>
        <li>Each recipe line runs in its <b>own shell</b>: <code>cd dir</code> on one line is forgotten on the next.</li>
      </ul>'''),
    ('a', 'Behind the screen: the dependency graph', '''      <ul>
        <li>make reads the whole Makefile, builds a <b>graph</b> of targets and prerequisites, then walks it depth-first from the goal.</li>
        <li>For each node it compares modification times (mtime, from stat). Missing target or newer prerequisite → rebuild. File systems store times to the nanosecond, but GNU make 4 compares them to the nanosecond, so “newer” means newer, not “different”: an <i>older</i> file restored with cp -p, tar or rsync does not trigger a rebuild.</li>
        <li>Recipes run with <code>/bin/sh -c</code> (dash on Ubuntu) unless <code>SHELL := /bin/bash</code>; <code>$</code> must be written <code>$$</code> to reach the shell.</li>
        <li>If a recipe line fails (non-zero exit), make stops and may delete a half-built target (<code>.DELETE_ON_ERROR</code>).</li>
        <li><code>-j N</code> runs independent branches of the graph at the same time; missing prerequisites then show up as random build failures.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>make and the Makefile</h2>
''' + def_block(
    '<b>make</b> is a build automation tool. It reads a <b>Makefile</b> made of <b>rules</b>: a <b>target</b>, its <b>prerequisites</b> and a <b>recipe</b> of shell commands. make rebuilds a target only when it is missing or older than one of its prerequisites, and builds prerequisites first.',
    'Write down what depends on what once; make works out what to redo.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Target', 'What a rule makes (usually a file).'),
    ('Prerequisite', 'A file the target depends on.'),
    ('Recipe', 'TAB-indented commands that make the target.'),
    ('Rule', 'target: prerequisites + recipe.'),
    ('Phony target', 'A name for an action, not a file (clean).'),
    ('Pattern rule', '%.o: %.c, a rule for many files.'),
    ('Automatic variable', '$@ $< $^, filled in per rule.'),
    ('Default goal', 'The first target in the file.'),
]) + '\n' + names('Where the names come from.', [
    ('make', 'make (the file)', 'Stuart Feldman, Bell Labs, 1976.'),
    ('Makefile', 'the file make reads', 'Also makefile, GNUmakefile.'),
    ('GNU make', 'the Linux version', 'Most common today.'),
    ('$@', 'at = the target', '“at” the goal.'),
    ('$<', 'the first input', 'arrow in.'),
    ('$^', 'all inputs', 'roof over all.'),
    ('.PHONY', 'fake (target)', 'Not a real file.'),
    ('-j', 'jobs', 'parallel recipes.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Build', '<code>make</code>'),
    ('Dry run', '<code>make -n</code>'),
    ('Force', '<code>make -B</code>'),
    ('Parallel', '<code>make -j4</code>'),
    ('Other folder', '<code>make -C dir</code>'),
    ('Install', '<code>sudo apt install make</code>'),
]) + '\n' + lv + didyou('Stuart Feldman wrote make in 1976 after a colleague lost a morning debugging a program that was fine; he had just forgotten to recompile one file. Feldman later said that the TAB rule was a mistake he kept because a dozen people already used it.') + '''
EXAM> “What is the use of make?” → To automate building: it rebuilds only targets whose prerequisites changed, in dependency order, using rules in a Makefile.
''' + qc('Why does make say “up to date” on the second run?', 'Every target is newer than all its prerequisites, so no recipe needs to run.') + mistake('a recipe indented with spaces',
    'indent every recipe line with one TAB character (cat -A shows ^I)',
    'make answers “missing separator. Stop.” (real run). Set your editor to keep tabs in Makefiles.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The parts of a Makefile</h2>
''' + table(['Part', 'Looks like', 'Meaning'], [
    ['Explicit rule', '<code>hello: hello.o greet.o</code>', 'how to make one target'],
    ['Recipe line', '<code>&lt;TAB&gt;gcc -o $@ $^</code>', 'shell command, own shell each line'],
    ['Pattern rule', '<code>%.o: %.c</code>', 'any .o from its .c'],
    ['Phony target', '<code>.PHONY: clean test</code>', 'always runs; not a file'],
    ['Variable', '<code>CFLAGS = -Wall</code> → <code>$(CFLAGS)</code>', 'reuse values'],
    ['Comment', '<code># note</code>', 'ignored'],
    ['Include', '<code>include config.mk</code>', 'read another file'],
    ['Conditional', '<code>ifeq ($(MODE),debug)</code>', 'choose settings'],
    ['Function', '<code>$(wildcard *.c)</code> <code>$(patsubst %.c,%.o,…)</code>', 'compute lists'],
], minw=520) + table(['Variable', 'Means', 'In <code>hello: hello.o greet.o</code>'], [
    ['<code>$@</code>', 'the target', 'hello'],
    ['<code>$&lt;</code>', 'first prerequisite', 'hello.o'],
    ['<code>$^</code>', 'all prerequisites (no duplicates)', 'hello.o greet.o'],
    ['<code>$?</code>', 'prerequisites newer than the target', 'only the changed ones'],
    ['<code>$*</code>', 'the % stem in a pattern rule', 'greet (for greet.o)'],
], minw=480) + table(['Assignment', 'When the value is computed', 'Use'], [
    ['<code>=</code>', 'every time it is used (recursive)', 'default'],
    ['<code>:=</code>', 'once, now (simple)', 'shell calls, speed'],
    ['<code>?=</code>', 'only if not already set', 'defaults users can override'],
    ['<code>+=</code>', 'append', 'CFLAGS += -g'],
], minw=420) + table(['', 'make', 'a shell script'], [
    ['Skips work already done', 'yes, by timestamps', 'no, runs everything'],
    ['Order', 'from the dependency graph', 'top to bottom'],
    ['Parallel', 'make -j', 'by hand (&, wait)'],
    ['Each line', 'its own shell', 'one shell'],
], minw=420) + qc('In <code>%.o: %.c</code> compiling greet.c, what are $@ and $&lt;?', '$@ is greet.o, $&lt; is greet.c.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Rules, timestamps, variables and options, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine (GNU Make 4.3, gcc 13) as riya. <code>~/mk/c</code> has hello.c, greet.c, greet.h and the C Makefile; <code>~/mk/data</code> has sales.csv and a report Makefile. We add <code>sleep 1</code> before edits so the new file time is clearly later.</p>
''' + cmdcard_u(['any repeated build: programs, reports, docs, images', 'steps that depend on other steps'],
               ['one-off commands (a script or alias is simpler)'])(
    'rule', 'target: prerequisites  ⏎  <TAB>recipe', 'a rule and how make decides',
    'make starts at the first target (or the one you name), checks its prerequisites first, then runs the recipe if the target is missing or older than any prerequisite. It prints each command before running it (prefix a line with <code>@</code> to hide it).',
    'make   ·   make TARGET   ·   make -f FILE', 'change',
    [('make', 'build the default goal', 'daily'),
     ('make report.txt', 'one target', 'targeted'),
     ('@cmd', 'do not echo the line', 'clean output'),
     ('-cmd', 'ignore its error', 'cleanup'),
     ('make -f build.mk', 'another file name', 'several Makefiles'),
     ('make -C dir', 'run in dir', 'sub-projects')],
    dict(setup=MK, cmd="cd ~/mk/data\nmake\ncat report.txt\nmake\nsleep 1; echo 'neha,delhi' >> sales.csv\nmake\ncat report.txt", note='Second run: nothing to do. After sales.csv changed, the report was rebuilt.'),
    [('data', [
        dict(situation='The restored-file trap from the puzzle.', setup=MK, cmd="cd ~/mk/data\nmake > /dev/null\nprintf 'name,city\\nold,goa\\n' > sales.csv; touch -d '1 day ago' sales.csv\nmake\ncat report.txt\ntouch sales.csv; make", why='The new data has an OLD timestamp (like cp -p or tar restore), so make thinks the report is fresh and leaves stale numbers. touch gives it the current time and make rebuilds. When in doubt: make -B.')]),
     ('dev', [
        dict(situation='Hide commands with @ and keep going after - errors.', setup=MK, cmd="cd ~/mk; cat > Makefile <<'EOF'\nhi:\n\t@echo \"building as $$USER\"\n\t-rm nothing.tmp\n\t@echo done\nEOF\nmake 2>&1", expect='any', why='@ hides the command line; - lets make continue after rm fails; $$ passes a single $ to the shell.')]),
    ],
    anat=anatomy([('report.txt', 'cmd', 'target'), (':', 'opt', 'separator'), ('sales.csv', 'arg', 'prerequisite'), ('⏎ TAB cmd', 'arg', 'recipe')], 'One rule: target, colon, prerequisites, then TAB-indented recipe lines.')
) + cmdcard_u(['C/C++ projects', 'any rule repeated for many files'],
               ['writing the same rule ten times'])(
    'vars', 'CC = gcc · $(CC) · $@ $< $^ · %.o: %.c', 'variables, automatic variables and pattern rules',
    'Variables keep settings in one place (<code>CC</code>, <code>CFLAGS</code>, <code>OBJS</code>). Automatic variables fill in the current target and prerequisites. A pattern rule <code>%.o: %.c</code> teaches make to build any .o from the .c with the same stem, so adding a file needs no new rule.',
    'NAME = value   ·   $(NAME)   ·   %.out: %.in', 'change',
    [('VAR = v', 'define', 'settings'),
     ('$(VAR)', 'use', 'everywhere'),
     ('$@ $< $^', 'target / first / all', 'recipes'),
     ('%.o: %.c', 'pattern rule', 'many files'),
     ('$(wildcard *.c)', 'list files', 'auto lists'),
     ('$(patsubst %.c,%.o,$(SRC))', 'rename list', 'objects'),
     ('make VAR=x', 'override', 'one run')],
    dict(setup=MK, cmd="cd ~/mk/c\nmake\n./hello\nmake\nsleep 1; touch greet.c\nmake", note='After touching greet.c only greet.o was recompiled, then hello was relinked. hello.o was not touched.'),
    [('dev', [
        dict(situation='Override variables from the command line.', setup=MK, cmd="cd ~/mk/c\nmake -B CFLAGS='-g -O0' | head -1\nmake -B CC=cc | tail -1", why='Command-line values win over the Makefile; -B forces the rebuild so you can see the new flags.')]),
     ('qa', [
        dict(situation='Lists with functions: no hand-written OBJS.', setup=MK, cmd="cd ~/mk/c; cat > list.mk <<'EOF'\nSRC := $(wildcard *.c)\nOBJ := $(patsubst %.c,%.o,$(SRC))\nshow:\n\t@echo \"sources: $(SRC)\"\n\t@echo \"objects: $(OBJ)\"\nEOF\nmake -f list.mk", why='wildcard and patsubst compute the lists, so a new .c file is picked up automatically.')]),
    ]
) + cmdcard_u(['clean, test, install, all, help', 'targets that are actions, not files'],
               ['forgetting .PHONY (a file named clean breaks it)'])(
    'phony', '.PHONY: all clean test install', 'phony targets',
    'A <b>phony</b> target is a name for an action. Declaring it in <code>.PHONY</code> tells make never to look for a file with that name, so the recipe always runs. Without it, a file called <code>clean</code> makes the target “up to date” forever (the puzzle). A phony <code>all</code> listed first lets <code>make</code> build several things.',
    '.PHONY: clean   ·   all: prog docs   ·   make clean', 'change',
    [('.PHONY: clean', 'not a file', 'always'),
     ('all: a b', 'build several', 'default goal'),
     ('clean', 'remove built files', 'reset'),
     ('test', 'run tests', 'CI'),
     ('install', 'copy into place', 'sudo make install'),
     ('help', 'list targets', 'friendly')],
    dict(setup=MK, cmd="cd ~/mk/c; make > /dev/null\nmake clean\nls\ntouch clean\nsed -i '/^.PHONY/d' Makefile\nmake clean\nprintf '.PHONY: clean\\n' >> Makefile; make clean", note='Without .PHONY, the file named clean made the target “up to date”. With .PHONY it runs again.'),
    [('sys', [
        dict(situation='A help target that lists the others.', setup=MK, cmd="cd ~/mk; cat > Makefile <<'EOF'\n.PHONY: help build test\nhelp:   ## show this help\n\t@grep -E '^[a-z]+:.*##' Makefile | sed 's/:.*## /\\t/'\nbuild:  ## compile everything\n\t@echo building\ntest:   ## run the tests\n\t@echo testing\nEOF\nmake", why='A common team convention: the first target prints help from ## comments.')]),
    ]
) + cmdcard_u(['checking a Makefile before running it', 'big builds on many cores', 'projects with sub-folders'],
               ['-j on a Makefile with missing prerequisites'])(
    'opts', 'make -n · -B · -j N · -C dir · -k · -s', 'useful options',
    '<code>-n</code> prints what would run; <code>-B</code> rebuilds everything; <code>-j N</code> runs N recipes at once; <code>-C dir</code> changes into dir first; <code>-k</code> keeps going after an error to show all failures; <code>-s</code> is silent; <code>-p</code> prints make’s whole database.',
    'make -n   ·   make -j$(nproc)   ·   make -C sub target', 'change',
    [('-n', 'dry run', 'preview'),
     ('-B', 'force all', 'rebuild'),
     ('-j N', 'parallel', 'speed'),
     ('-C dir', 'other folder', 'sub-projects'),
     ('-k', 'keep going', 'see all errors'),
     ('-s', 'silent', 'quiet logs'),
     ('-f file', 'other Makefile', 'variants')],
    dict(setup=MK, cmd="cd ~/mk\nmake -n -C c\nmake -s -C c && ls c/hello\nmake -C c -B -j2 2>&1 | grep -c gcc", note='-n printed the three commands without building; -j2 compiled the two .o files at the same time.'),
    [('sys', [
        dict(situation='How many cores for -j?', cmd="echo \"this machine has $(nproc) CPU(s): use make -j$(nproc)\"", why='nproc counts CPUs; -j more than that rarely helps.')]),
    ]
) + undo('make only runs what you wrote; the risky parts are clean targets and install.', [
    ('Not sure what make will do:', 'run <code>make -n</code> first.'),
    ('clean removed too much:', 'restore from git; keep clean to built files only (no <code>rm -rf *</code>).'),
    ('Build is stale or confused:', '<code>make clean &amp;&amp; make</code> or <code>make -B</code>.'),
    ('sudo make install put files everywhere:', 'try <code>sudo make uninstall</code>; next time use a package or <code>checkinstall</code> (Lesson 14.4).'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(setup="cd ~; rm -rf mkx; mkdir mkx; cd mkx; printf 'x:\\n    echo hi\\n' > Makefile", cmd='cd ~/mkx; make', meaning='Recipe indented with spaces.', fix='Use a TAB.'),
    dict(setup="cd ~; rm -rf mkx; mkdir mkx; cd mkx; printf 'all:\\n\\techo ok\\n' > Makefile", cmd='cd ~/mkx; make nope', meaning='No such target.', fix='Check spelling; make help.'),
    dict(setup="cd ~; rm -rf mkx; mkdir mkx", cmd='cd ~/mkx; make', meaning='No Makefile here.', fix='cd to the project, or make -C / -f.'),
    dict(setup="cd ~; rm -rf mkx; mkdir mkx; cd mkx; printf 'out: in.txt\\n\\tcp in.txt out\\n' > Makefile", cmd='cd ~/mkx; make', meaning='A prerequisite file is missing and no rule makes it.', fix='Create it or add a rule.'),
    dict(setup="cd ~; rm -rf mkx; mkdir mkx; cd mkx; printf 'all:\\n\\tfalse\\n\\techo never\\n' > Makefile", cmd='cd ~/mkx; make', meaning='A recipe command failed, so make stopped.', fix='Fix the command; - prefix to ignore.'),
]) + qc('What does <code>make -n</code> do?', 'Prints the commands that would run, without running them.') + '''
'''
cards = cards + '</section>\n'

# animation: dependency graph, rebuild after editing greet.c
def graph(k):
    col = [['card'] * 5, ['green'] * 5, ['green', 'green', 'red', 'green', 'red'], ['green'] * 5][k]
    o = (label_box(140, 14, 80, 30, ['hello'], col[0], 8.4)
         + label_box(40, 74, 90, 30, ['hello.o'], col[1], 8.4) + label_box(230, 74, 90, 30, ['greet.o'], col[4], 8.4)
         + label_box(10, 134, 70, 28, ['hello.c'], col[1], 8) + label_box(150, 134, 70, 28, ['greet.h'], col[3], 8)
         + label_box(260, 134, 80, 28, ['greet.c'], col[2], 8)
         + arrow(85, 74, 165, 44) + arrow(275, 74, 200, 44) + arrow(45, 134, 75, 104) + arrow(185, 134, 100, 104) + arrow(185, 134, 260, 104) + arrow(300, 134, 285, 104))
    return o
see_cmds = [['$ make', ('gcc -c hello.c', 'out'), ('gcc -c greet.c', 'out'), ('gcc -o hello …', 'out')],
            ['$ make', ("'hello' is up to date.", 'acc')],
            ['$ vim greet.c   # edit', '$ make'],
            ['$ make', ('gcc -c greet.c', 'out'), ('gcc -o hello …', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/mk/c', prompt='riya@web01:~/mk/c$', size=7.4) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['First build.', 'Nothing changed.', 'Edit one file.', 'Only what depends on it.'])]
behind = [graph(k) + t(180, 190, n, 8.4, 'violet', bold=True) for k, n in enumerate(['Nothing built yet.', 'All targets newer than inputs.', 'greet.c newer than greet.o → red.', 'greet.o, then hello rebuilt.'])]
two = anim_two('make after one edit', 'Behind the screen: the dependency graph and timestamps',
               'A terminal: first make compiles, second does nothing, then after editing greet.c only greet.o and hello are rebuilt.',
               'A graph: hello depends on hello.o and greet.o, which depend on the .c files and greet.h. Edited greet.c turns its branch red until rebuilt.', see, behind,
               ['Build.', 'Up to date.', 'Edit.', 'Rebuild part.'],
               ['first', 'again', 'edit', 'partial'])

def jobs(k):
    o = ''
    lanes = [[('hello.o', 0)], [('hello.o', 0), ('greet.o', 1)], [('hello', 0)]]
    if k == 0:
        o += label_box(20, 30, 140, 30, ['-j1: hello.o'], 'blue', 8) + label_box(20, 70, 140, 30, ['then greet.o'], 'card', 8) + label_box(20, 110, 140, 30, ['then hello'], 'card', 8)
    elif k == 1:
        o += label_box(20, 30, 140, 30, ['-j2: hello.o'], 'blue', 8) + label_box(190, 30, 140, 30, ['greet.o (same time)'], 'blue', 8)
    else:
        o += label_box(100, 70, 160, 30, ['link hello (needs both)'], 'green', 8)
    return o
frames = [jobs(0) + t(180, 180, 'One job at a time.', 8.6, 'violet', bold=True),
          jobs(1) + t(180, 180, '-j2: independent targets together.', 8.6, 'violet', bold=True),
          jobs(2) + t(180, 180, 'hello waits for both prerequisites.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'Parallel builds with -j',
              'make runs targets that do not depend on each other at the same time.',
              'make -j2', 'Three boxes: with -j1 targets run one after another; with -j2 hello.o and greet.o run together; hello is linked after both.', frames,
              ['-j1.', '-j2.', 'link.'], hid='scenario-jobs')

dx = dissect('Layer by layer: what make does on each run',
    'Each layer has a real command and output from our build machine.', [
    dict(key='read', name='Read rules', sub='parse', why='Learn the graph.', how='Variables expanded.', impl='make -p shows it.', used='Every run.',
         setup=MK, cmd="cd ~/mk/c; make -p -n 2>/dev/null | grep -E '^(hello|greet.o|clean):' | sort -u"),
    dict(key='time', name='Compare times', sub='stat', why='Decide.', how='mtime.', impl='Nanoseconds.', used='Up to date?',
         setup=MK, cmd="cd ~/mk/c; make -s; sleep 1; touch greet.c; for f in greet.c greet.o hello; do stat -c '%n %Y' $f; done"),
    dict(key='why', name='Explain', sub='--debug', why='Why rebuild?', how='-d / --trace.', impl='GNU make 4.', used='Debugging.',
         setup=MK, cmd="cd ~/mk/c; make -s; sleep 1; touch greet.c; make --trace 2>&1 | grep -o 'update target.*' "),
    dict(key='shell', name='Run recipes', sub='/bin/sh', why='Do the work.', how='One shell per line.', impl='dash on Ubuntu.', used='cd trap.',
         setup="cd ~; rm -rf mky; mkdir -p mky/sub; cd mky; printf 'a:\\n\\tcd sub\\n\\tpwd | sed \"s|.*/||\"\\nb:\\n\\tcd sub && pwd | sed \"s|.*/||\"\\n' > Makefile", cmd="cd ~/mky; make -s a; make -s b"),
], hint='From reading rules to running recipes. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>The dependency graph and parallel jobs</h2>
''' + two + s1 + dx + qc('Why did <code>cd sub</code> on one recipe line not affect the next line?', 'Each recipe line runs in a new shell; join them with &amp;&amp; on one line (or use .ONESHELL).') + '''
</section>
'''

VAR = variations('Fifteen more Makefiles and runs, from tiny to realistic. All were really run on our build machine.', [
    ('Rules and variables', [
        dict(title='Smallest Makefile', setup="cd ~; rm -rf v1; mkdir v1; cd v1; printf 'hello:\\n\\t@echo Hello from make\\n' > Makefile", cmd="cd ~/v1; make", why='One target, one recipe, no prerequisites: it always runs (there is no file named hello).'),
        dict(title='A chain of steps', setup="cd ~; rm -rf v2; mkdir v2; cd v2; printf '3 1 2\\n' > raw.txt; printf 'top.txt: sorted.txt\\n\\thead -1 sorted.txt > top.txt\\nsorted.txt: raw.txt\\n\\ttr \" \" \"\\\\n\" < raw.txt | sort -n > sorted.txt\\n' > Makefile", cmd="cd ~/v2; make; cat top.txt", why='make built sorted.txt first because top.txt needs it.'),
        dict(title='= vs :=', setup="cd ~; rm -rf v3; mkdir v3; cd v3; printf 'A = $(B)\\nC := $(B)\\nB = later\\nshow:\\n\\t@echo \"A=$(A) C=$(C)\"\\n' > Makefile", cmd="cd ~/v3; make", why='= is expanded when used (sees later); := was expanded when defined (B was empty).'),
        dict(title='?= default the user can override', setup="cd ~; rm -rf v4; mkdir v4; cd v4; printf 'ENV ?= dev\\nshow:\\n\\t@echo deploying to $(ENV)\\n' > Makefile", cmd="cd ~/v4; make; make ENV=prod; ENV=test make", why='?= sets a value only if nothing else did: command line or environment win.'),
        dict(title='$$ for shell variables', setup="cd ~; rm -rf v5; mkdir v5; cd v5; printf 'who:\\n\\t@echo \"make var: $(USER)  shell var: $$USER  pid: $$$$\" | sed \"s/pid: [0-9]*/pid: N/\"\\n' > Makefile", cmd="cd ~/v5; make", why='$(USER) is make’s copy of the environment; $$ passes $ to the shell.'),
    ]),
    ('Patterns and functions', [
        dict(title='Convert many files with one pattern rule', setup="cd ~; rm -rf v6; mkdir v6; cd v6; for n in a b c; do echo \"hello $n\" > $n.txt; done; printf 'UP := $(patsubst %%.txt,%%.up,$(wildcard *.txt))\\nall: $(UP)\\n%%.up: %%.txt\\n\\ttr a-z A-Z < $< > $@\\n' > Makefile", cmd="cd ~/v6; make; cat b.up", why='One rule handles every .txt; $< is the input, $@ the output.'),
        dict(title='$? shows only the changed inputs', setup="cd ~; rm -rf v7; mkdir v7; cd v7; touch x y z; printf 'stamp: x y z\\n\\t@echo changed: $?\\n\\t@touch stamp\\n' > Makefile", cmd="cd ~/v7; make; sleep 1; touch y; make", why='First run: all three; then only y.'),
        dict(title='$(shell …) and text functions', setup="cd ~; rm -rf v8; mkdir v8; cd v8; printf 'TODAY := $(shell date +%%Y)\\nFILES := one.c two.c\\nshow:\\n\\t@echo year $(TODAY), $(words $(FILES)) files: $(FILES:.c=.o), upper $(shell echo riya | tr a-z A-Z)\\n' > Makefile", cmd="cd ~/v8; make", why='$(shell) runs a command; $(words) counts; $(VAR:.c=.o) is a substitution reference.'),
        dict(title='ifeq for debug and release builds', setup="cd ~; rm -rf v9; mkdir v9; cd v9; printf 'MODE ?= release\\nifeq ($(MODE),debug)\\nCFLAGS = -g -O0\\nelse\\nCFLAGS = -O2\\nendif\\nshow:\\n\\t@echo $(MODE): $(CFLAGS)\\n' > Makefile", cmd="cd ~/v9; make; make MODE=debug", why='Conditionals choose settings when the Makefile is read.'),
    ]),
    ('Real projects', [
        dict(title='C program end to end', setup=MK, cmd="cd ~/mk/c; make -s && ./hello && make -s clean && ls", why='Build, run, clean: the everyday cycle.'),
        dict(title='Python project tasks', setup="cd ~; rm -rf v11; mkdir v11; cd v11; printf 'def add(a,b): return a+b\\n' > calc.py; printf 'from calc import add\\nassert add(2,3)==5\\nprint(\"1 test passed\")\\n' > test_calc.py; printf '.PHONY: test lint\\ntest:\\n\\t@python3 test_calc.py\\nlint:\\n\\t@python3 -m py_compile calc.py && echo syntax ok\\n' > Makefile", cmd="cd ~/v11; make test lint", why='make as a task runner: several targets in one call.'),
        dict(title='Data pipeline: download → clean → report', setup="cd ~; rm -rf v12; mkdir v12; cd v12; printf 'id,amt\\n1,100\\n2,\\n3,250\\n' > raw.csv; printf 'report.txt: clean.csv\\n\\tawk -F, \"NR>1{s+=\\\\$$2} END{print \\\\\"total\\\\\", s}\" clean.csv > $@\\nclean.csv: raw.csv\\n\\tgrep -v \",\\\\$$\" raw.csv > $@\\n' > Makefile", cmd="cd ~/v12; make && cat report.txt", why='The empty-amount row is dropped, then totals computed; rerun only redoes changed steps.'),
        dict(title='Sub-folders with -C', setup="cd ~; rm -rf v13; mkdir -p v13/api v13/web; for d in api web; do printf 'all:\\n\\t@echo built %s\\n' $d > v13/$d/Makefile; done; printf 'all:\\n\\t$(MAKE) -s -C api\\n\\t$(MAKE) -s -C web\\n' > v13/Makefile", cmd="cd ~/v13; make -s", why='A top Makefile drives sub-projects; use $(MAKE) so options pass down.'),
        dict(title='A timing proof: partial rebuild', setup=MK, cmd="cd ~/mk/c; make -s; sleep 1; touch hello.c; make | sed 's/ -Wall -O2//'", why='Only hello.o and the link ran; greet.o stayed.'),
        dict(title='.DELETE_ON_ERROR keeps no half files', setup="cd ~; rm -rf v15; mkdir v15; cd v15; printf '.DELETE_ON_ERROR:\\nout.txt:\\n\\techo partial > $@; false\\n' > Makefile", cmd="cd ~/v15; make 2>&1 | tail -2; ls out.txt 2>&1", expect='any', why='The recipe failed, so make deleted out.txt instead of leaving a broken file that looks up to date.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>make at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['kernel', 'make -j'], 'blue', 8.6), '1. Building the Linux kernel and C software',
              'make menuconfig, make -j$(nproc), sudo make modules_install install. Every open-source C project ships a Makefile.', ['Source', '*make', 'binary']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['./configure', 'install'], 'green', 8.6), '2. Installing from source',
    './configure && make && sudo make install (Lesson 14.4).', ['Download', '*make', 'install']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['make test', 'CI'], 'amber', 8.6), '3. CI pipelines and task runners',
    'GitHub Actions or Jenkins call make test, make lint, make docker so every developer runs the same steps.', ['Push', '*make test', 'green build']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['data', 'reports'], 'violet', 8.6), '4. Data pipelines',
    'Analysts chain download → clean → model → report; make reruns only steps whose inputs changed.', ['Raw', '*make', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['docs', 'sites'], 'red', 8.6), '5. Docs and websites',
    'Sphinx docs (make html) and static sites build with make.', ['Markdown', '*make html', 'site']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Build and run', scenario='Daily.', setup=MK, cmd="cd ~/mk/c; make -s && ./hello", explain='-s keeps it quiet.'),
    dict(level='b', title='Preview', scenario='Before running someone’s Makefile.', setup=MK, cmd="cd ~/mk/data; make -n", explain='Dry run.'),
    dict(level='i', title='Rebuild everything', scenario='Odd results.', setup=MK, cmd="cd ~/mk/c; make -s; make -B | wc -l", explain='-B forces all recipes.'),
    dict(level='i', title='Show targets', scenario='New project.', setup=MK, cmd="cd ~/mk/c; grep -E '^[a-zA-Z%.]+:' Makefile", explain='Lines ending in : are rules.'),
    dict(level='a', title='Why is it rebuilding?', scenario='Debug.', setup=MK, cmd="cd ~/mk/c; make -s; sleep 1; touch greet.h; make --trace 2>&1 | grep -o 'update target.*'", explain='greet.h is a prerequisite of both .o files.'),
], extra=build_up('a report Makefile', 'Riya grows a data Makefile step by step.', "cd ~; rm -rf bu; mkdir bu; cd bu; printf 'name,city\\nriya,pune\\naman,delhi\\nzoya,pune\\n' > sales.csv", [
    ("cd ~/bu; printf 'report.txt: sales.csv\\n\\tcut -d, -f2 sales.csv | tail -n +2 | sort | uniq -c > $@\\n' > Makefile; make; cat report.txt", '1. One rule.'),
    ("cd ~/bu; make", '2. Run again: up to date.'),
    ("cd ~/bu; printf '.PHONY: clean\\nclean:\\n\\trm -f report.txt\\n' >> Makefile; make clean", '3. Add a phony clean.'),
    ("cd ~/bu; sed -i '1i all: report.txt' Makefile; make && sleep 1 && echo 'neha,pune' >> sales.csv && make && cat report.txt", '4. all first; new data, automatic rebuild.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Build with dependencies', 'make', 'Skips done work.', 'A script that recompiles all.'),
    ('One-off command', 'alias / script', 'Simpler.', 'A Makefile for one line.'),
    ('Large C/C++ projects', 'CMake or Meson → make/ninja', 'Generate Makefiles.', 'Hand-writing 500 rules.'),
    ('Task runner', 'make (phony)', 'Everywhere installed.', 'Tool-specific runners for tiny jobs.'),
    ('Scheduled rebuild', 'cron/timer + make', 'Only changed steps.', 'Rerunning everything nightly.'),
]) + keys('Handy forms.', [
    ('make -n', 'dry run', 'preview'),
    ('make -B', 'force', 'rebuild'),
    ('make -j$(nproc)', 'parallel', 'speed'),
    ('make -C dir', 'folder', 'sub-projects'),
    ('make V=1 / VAR=x', 'override', 'variables'),
    ('cat -A Makefile', 'see TABs (^I)', 'separator errors'),
]) + scriptit('newmake.sh', 'Create a starter Makefile for a C program (with variables, a pattern rule, all, clean and help), then build and run it.',
'''dir=${1:-starter}
mkdir -p "$dir" && cd "$dir" || exit 1
printf '#include <stdio.h>\\nint main(void){ puts("built by make"); return 0; }\\n' > main.c
printf '%s\\n' 'CC ?= gcc' 'CFLAGS ?= -Wall -O2' 'SRC := $(wildcard *.c)' 'OBJ := $(SRC:.c=.o)' '' \\
  '.PHONY: all clean' 'all: app' 'app: $(OBJ)' '	$(CC) $(CFLAGS) -o $@ $^' '%.o: %.c' '	$(CC) $(CFLAGS) -c $<' 'clean:' '	rm -f app $(OBJ)' > Makefile
make -s && ./app
make
make -s clean && ls''',
'<p>Run without a name, so it uses the starter folder.</p>', expect='any') + puzzle_answer('<b>1.</b> Recipe lines must start with a TAB; spaces give “missing separator”. <b>2.</b> make only asks “is a prerequisite <i>newer</i> than the target?”. <code>cp -p</code> kept the backup’s old timestamp, so sales.csv looked older than report.txt. Run <code>touch sales.csv</code> or <code>make -B</code>. <b>3.</b> A file named <code>clean</code> appeared in the folder (for example from <code>make clean &gt; clean</code>). With no prerequisites, that file is always “up to date”. Declare <code>.PHONY: clean</code> so make never treats it as a file.') + qc('Which automatic variable holds all the prerequisites?', '$^.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/mk ~/mkx ~/mky ~/v* ~/bu', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../05-your-first-shell-script/">Lesson 12.5</a> (scripts) and <a href="../11-metacharacters-expansion-and-directory-stacks/">Lesson 12.11</a> ($ and wildcards).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
