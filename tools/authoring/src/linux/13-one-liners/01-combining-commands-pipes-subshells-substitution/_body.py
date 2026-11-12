import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

CB = r"""rm -rf ~/cb; mkdir -p ~/cb/logs ~/cb/conf; cd ~/cb
cat > logs/access.log <<'EOF'
10.0.0.5 - - [11/Nov/2026:09:01:12] "GET /index.html HTTP/1.1" 200 512
10.0.0.7 - - [11/Nov/2026:09:01:15] "GET /login HTTP/1.1" 200 230
10.0.0.5 - - [11/Nov/2026:09:02:01] "POST /login HTTP/1.1" 401 88
10.0.0.9 - - [11/Nov/2026:09:02:40] "GET /admin HTTP/1.1" 403 64
10.0.0.5 - - [11/Nov/2026:09:03:05] "GET /old-page HTTP/1.1" 404 32
10.0.0.7 - - [11/Nov/2026:09:04:11] "GET /api/orders HTTP/1.1" 500 120
10.0.0.5 - - [11/Nov/2026:09:05:30] "GET /api/orders HTTP/1.1" 200 2048
EOF
printf 'port=8080\nhost=0.0.0.0\nworkers=4\n' > conf/app.conf
printf 'port=8080\nhost=127.0.0.1\nworkers=8\n' > conf/app.conf.new"""

HOOK = hook('“How many different IP addresses got an error from our site today, and which one got the most?” Riya’s manager wants the answer in two minutes. There is no tool called <code>count-error-ips</code>. But Linux has dozens of small tools that each do one thing, and the shell has a handful of ways to <b>combine</b> them: <code>|</code> passes output along, <code>&amp;&amp;</code> and <code>||</code> decide what runs next, <code>;</code> runs things in order, <code>( )</code> and <code>{ }</code> group commands, <code>$( )</code> puts a command’s output inside another command, and <code>&lt;( )</code> lets a command read another command’s output as if it were a file. This lesson turns these into one habit: build a one-liner step by step and check each step.',
    ['combine commands with ; && || | |& and know exactly when each next command runs',
     'group commands with ( ) and { }, and know which one changes your shell',
     'use $( ), <( ) and >( ) and tee to connect commands that need arguments or files',
     'handle errors in pipelines with $?, PIPESTATUS and set -o pipefail, and build one-liners step by step'])
ROAD = roadmap([
    ('story', 'The story', 3, 'a question with no command'),
    ('decide', 'Which operator when?', 2, 'the quick chart'),
    ('definition', 'What combining means', 6, 'simple meaning + 4 depths'),
    ('types', 'All the operators', 5, 'one table'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'a pipeline, stage by stage'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'answer with one-liners'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which operator? (decide in 5 seconds)', [
    ('Output of A is the input of B', 'A | B', 'pipe'),
    ('B only if A worked', 'A && B', 'AND'),
    ('B only if A failed', 'A || B', 'OR'),
    ('A, then B, no matter what', 'A ; B', 'sequence'),
    ('Output of A as an argument', 'B "$(A)"', 'command substitution'),
    ('B needs a FILE but you have a command', 'B <(A)', 'process substitution'),
    ('Save AND pass on', 'A | tee file | B', 'tee'),
    ('Try something in another folder, come back', '(cd dir && A)', 'subshell'),
])

cmap = concept_map(
    [('5.4', 'Chaining and exit codes', '&& || $?'), ('6.1', 'Text tools', 'grep cut sort uniq awk'), ('12.11', 'Expansion', '$( ) and <( )')],
    ['; && || and exit status', '| |& and tee', '( ) vs { }', '$( ) <( ) >( )', 'PIPESTATUS and pipefail', 'building one-liners step by step'],
    [('13.2', 'find + xargs', 'bulk actions'), ('13.3', 'Log one-liners', 'top IPs'), ('13.5', 'Data one-liners', 'CSV and jq'), ('13.7', '100 one-liners', 'cheat sheet')],
    'Small tools, joined by operators: | moves data, && || ; decide what runs, ( ) { } group, $( ) <( ) plug outputs into places that want arguments or files.')

sc = (term(20, 14, 316, 156, ['$ grep -E \'" [45][0-9]{2} \' access.log \\', '>   | cut -d" " -f1 | sort | uniq -c | sort -rn', ('      2 10.0.0.5', 'out'), ('      1 10.0.0.9', 'out'), ('      1 10.0.0.7', 'out'), '$ … | wc -l', ('3', 'acc')], title='riya@web01: ~/cb/logs', prompt='riya@web01:~/cb/logs$', size=6.6, step=17)
      + t(352, 36, 'Pipeline:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['grep: error lines', 'cut: the IP', 'sort | uniq -c', 'sort -rn: top', 'each tool small'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>A question with no command</h2>
  <div class="story">
''' + puzzle('Riya writes <code>grep ERROR app.log | wc -l &amp;&amp; echo "report sent"</code>. The log file does not even exist, yet “report sent” is printed. Then <code>cd /var/www &amp;&amp; rm -rf old/</code> works, but her colleague’s <code>cd /var/ww; rm -rf old/</code> (one typo) deletes the wrong folder. And <code>cat list.txt | while read f; do n=$((n+1)); done; echo $n</code> prints nothing. Why, in all three cases?') + '''
    <p class="narration">Riya answers the manager’s question by joining five small tools.</p>
''' + scene('A terminal: grep for 4xx and 5xx lines, cut the IP, sort, count with uniq -c, and sort by count; then count the distinct IPs.', sc,
            'Five tools, one line: <tspan font-weight="700" class="s-acc">each step does one thing</tspan>.') + '''
K> How did you know which tools to join?
A> I asked what each step needs to produce. Error lines → the IP of each → the same IPs next to each other → counts → biggest first. Then I ran it one stage at a time and looked at the output before adding the next.
R> And the puzzle?
A> It is all about <b>exit status</b> and <b>where commands run</b>: the status of a pipeline, what <code>;</code> does after a failure, and pipes running in subshells. Today: every way to combine commands, and how to stay safe.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A factory line: raw material goes through machines connected by conveyor belts (pipes). Traffic lights between stations decide whether the next station runs: green for && after success, red for || after failure, and a plain arrow for ; which always continues.">'
       + label_box(14, 24, 110, 70, ['grep', 'pick lines'], 'blue', 9) + arrow(124, 59, 150, 59)
       + label_box(150, 24, 110, 70, ['cut', 'take a field'], 'blue', 9) + arrow(260, 59, 286, 59)
       + label_box(286, 24, 110, 70, ['sort | uniq -c', 'count'], 'blue', 9) + arrow(396, 59, 422, 59)
       + label_box(422, 24, 110, 70, ['sort -rn', 'top first'], 'blue', 9)
       + t(560, 64, '| = belt', 10, 'blue', bold=True)
       + label_box(14, 120, 190, 54, ['A && B', 'B only after success'], 'green', 9)
       + label_box(222, 120, 190, 54, ['A || B', 'B only after failure'], 'red', 9)
       + label_box(430, 120, 190, 54, ['A ; B', 'B always'], 'amber', 9)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Combining at four depths', [
    ('v', 'No jargon: a factory line with traffic lights', '      <p>Belts carry the product; lights decide if the next station starts.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>ls | wc -l</code>: count files (output of ls goes into wc).</li>
        <li><code>mkdir backup &amp;&amp; cp *.txt backup/</code>: copy only if mkdir worked.</li>
        <li><code>ping -c1 web01 || echo "web01 is down"</code>: message only on failure.</li>
        <li><code>echo "Today is $(date +%A)"</code>: a command inside a command.</li>
      </ul>'''),
    ('i', 'Exit status decides', '''      <ul>
        <li>Every command returns an exit status: 0 = success, anything else = failure; <code>$?</code> holds the last one.</li>
        <li><code>&amp;&amp;</code> and <code>||</code> look at it; <code>;</code> ignores it.</li>
        <li><code>A &amp;&amp; B || C</code> is not if/else: C also runs when B fails.</li>
        <li>A pipeline’s status is the status of its <b>last</b> command, unless <code>set -o pipefail</code>; <code>${PIPESTATUS[@]}</code> has all of them.</li>
        <li><code>( … )</code> runs in a <b>subshell</b> (cd and variables are forgotten), <code>{ …; }</code> in the current shell.</li>
      </ul>'''),
    ('a', 'Behind the screen: pipes, forks and file descriptors', '''      <ul>
        <li>For <code>A | B</code> the shell calls <code>pipe()</code>, forks twice, connects A’s stdout (fd 1) to the write end and B’s stdin (fd 0) to the read end. Both run <b>at the same time</b>; the kernel buffers 64 KiB.</li>
        <li>Each part of a pipeline runs in its own subshell, so <code>… | while read</code> changes variables in a child (the third puzzle). <code>shopt -s lastpipe</code> or <code>while … done &lt; &lt;(cmd)</code> fixes it.</li>
        <li>If B exits early (head), A gets SIGPIPE on its next write and dies with 141 (Lesson 11.3).</li>
        <li><code>&lt;(cmd)</code> becomes a path like <code>/dev/fd/63</code>: a pipe the shell opened for you.</li>
        <li><code>|&amp;</code> is <code>2&gt;&amp;1 |</code>: stderr joins stdout into the pipe.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Pipes, lists, groups and substitutions</h2>
''' + def_block(
    'A <b>pipeline</b> (<code>A | B</code>) connects the standard output of one command to the standard input of the next. A <b>list</b> joins commands with <code>;</code>, <code>&amp;&amp;</code>, <code>||</code> or <code>&amp;</code>, which decide when the next one runs based on the previous <b>exit status</b>. <b>Grouping</b> with <code>( )</code> (a subshell) or <code>{ ;}</code> (the current shell) treats several commands as one. <b>Command substitution</b> <code>$( )</code> inserts output as text; <b>process substitution</b> <code>&lt;( )</code> provides it as a file name.',
    'Pipes move data; operators decide what runs; groups bundle; substitutions plug outputs in.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Pipeline', 'A | B | C: data flows left to right.'),
    ('Exit status', '0 success, 1–255 failure; in $?.'),
    ('List', 'Commands joined by ; && || &.'),
    ('Subshell', 'A child shell: ( … ).'),
    ('Group', '{ …; } in the current shell.'),
    ('Command substitution', '$(cmd): output as text.'),
    ('Process substitution', '<(cmd): output as a file.'),
    ('pipefail', 'Pipeline fails if any part fails.'),
]) + '\n' + names('Where the names come from.', [
    ('pipe', 'a water pipe', 'Doug McIlroy’s idea, Unix 1973.'),
    ('|', 'the pipe symbol', 'Ken Thompson added it in one night.'),
    ('tee', 'a T-shaped pipe fitting', 'Splits the flow.'),
    ('&&', 'and', 'Both must succeed.'),
    ('||', 'or', 'Either one.'),
    ('$( )', 'substitution', 'POSIX; replaces `…`.'),
    ('<( )', 'process substitution', 'ksh88, bash.'),
    ('PIPESTATUS', 'pipe statuses', 'bash array.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Last status', '<code>echo $?</code>'),
    ('All statuses', '<code>${PIPESTATUS[@]}</code>'),
    ('Strict pipes', '<code>set -o pipefail</code>'),
    ('stderr too', '<code>A |&amp; B</code>'),
    ('Save + pass', '<code>A | tee f | B</code>'),
    ('Safe cd', '<code>cd dir &amp;&amp; …</code>'),
]) + '\n' + lv + didyou('Doug McIlroy wrote in a 1964 memo: “We should have some ways of coupling programs like garden hose: screw in another segment when it becomes necessary to massage data in another way.” It took until 1973 for pipes to appear in Unix, and the “do one thing well, and work together” philosophy grew from them.') + '''
EXAM> “What is the difference between ; and &amp;&amp;?” → With ; the next command always runs; with &amp;&amp; it runs only if the previous one succeeded (exit status 0).
''' + qc('Is <code>A &amp;&amp; B || C</code> the same as if A then B else C?', 'No. C runs if A fails <i>or</i> if B fails. Use a real if when B can fail.') + mistake('cd /var/ww; rm -rf old/',
    'cd /var/www && rm -rf old/   ·   or   rm -rf /var/www/old/   (full path)',
    'With ; the rm runs even after cd failed, in whatever folder you are in. With && it never runs after a failed cd.') + mistake('grep ERROR app.log | wc -l && echo "report sent"',
    'set -o pipefail; grep ERROR app.log | wc -l && echo "report sent"',
    'The pipeline’s status is wc’s (0), even though grep failed (real run: grep 2, wc 0).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Every way to combine commands</h2>
''' + table(['Form', 'Next part runs…', 'Example', 'Use'], [
    ['<code>A ; B</code>', 'always', '<code>date; uptime</code>', 'sequence'],
    ['<code>A &amp;&amp; B</code>', 'if A succeeded', '<code>make &amp;&amp; ./app</code>', 'safe chains'],
    ['<code>A || B</code>', 'if A failed', '<code>ping -c1 h || alert</code>', 'fallbacks'],
    ['<code>A | B</code>', 'at the same time; B reads A’s output', '<code>ps aux | grep nginx</code>', 'data flow'],
    ['<code>A |&amp; B</code>', 'same, stderr included', '<code>make |&amp; tee build.log</code>', 'logs'],
    ['<code>A &amp; B</code>', 'B starts at once; A in background', '<code>sleep 5 &amp; echo hi</code>', 'parallel (11.4)'],
    ['<code>( A; B )</code>', 'in a subshell', '<code>(cd /tmp; ls)</code>', 'isolate cd / vars'],
    ['<code>{ A; B; }</code>', 'in this shell', '<code>{ date; uptime; } &gt; r.txt</code>', 'one redirect for many'],
    ['<code>"$(A)"</code>', 'A first; output becomes text', '<code>echo "$(whoami)"</code>', 'arguments'],
    ['<code>&lt;(A)</code>', 'A runs; B gets a file name', '<code>diff &lt;(ls a) &lt;(ls b)</code>', 'tools that want files'],
    ['<code>&gt;(A)</code>', 'B writes into A', '<code>tee &gt;(gzip &gt; f.gz)</code>', 'fan out'],
    ['<code>A | tee f | B</code>', 'save a copy and continue', '<code>… | tee step2.txt | wc -l</code>', 'debug pipelines'],
], minw=560) + table(['', '( … ) subshell', '{ …; } group'], [
    ['Runs in', 'a child process', 'the current shell'],
    ['cd, variables, exit', 'forgotten afterwards', 'stay'],
    ['Syntax', 'spaces optional', 'spaces after { and ; before } required'],
    ['Speed', 'forks a process', 'no fork'],
    ['Use', 'try things safely', 'redirect several commands at once'],
], minw=420) + table(['', '$( ) command substitution', '<( ) process substitution', '| pipe'], [
    ['Gives the next command', 'text (arguments)', 'a file name', 'standard input'],
    ['Good for', 'echo, variables, options', 'diff, comm, join, paste', 'filters (grep, sort…)'],
    ['Waits?', 'yes, for all output', 'no, streams', 'no, streams'],
], minw=480) + qc('Which form lets <code>diff</code> compare the outputs of two commands without temp files?', 'Process substitution: diff &lt;(cmd1) &lt;(cmd2).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Operators, groups, substitutions and safe pipelines, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/cb</code>: <code>logs/access.log</code> (7 web requests from 3 IPs, status codes 200, 401, 403, 404, 500) and <code>conf/app.conf</code> with a newer <code>app.conf.new</code>.</p>
''' + cmdcard_u(['deploy steps, backups, checks', 'anything where step 2 must not run after a failed step 1'],
               ['long chains with A && B || C as if/else', '; after cd'])(
    'lists', 'A ; B · A && B · A || B · $?', 'running commands one after another',
    '<code>;</code> runs the next command whatever happened. <code>&amp;&amp;</code> runs it only after success (status 0), <code>||</code> only after failure. Chains are read left to right: <code>A &amp;&amp; B &amp;&amp; C</code> stops at the first failure; <code>A || B || C</code> stops at the first success.',
    'A && B && C   ·   A || B   ·   A ; B', 'change',
    [('A ; B', 'always', 'sequence'),
     ('A && B', 'after success', 'safe steps'),
     ('A || B', 'after failure', 'fallback, alert'),
     ('A && B || C', 'C if A or B failed', 'careful'),
     ('! A', 'invert status', 'tests'),
     ('$?', 'last status', 'debug'),
     ('true / false', 'always 0 / 1', 'testing chains')],
    dict(setup=CB, cmd="cd ~/cb\nmkdir -p backup && cp conf/app.conf backup/ && echo 'backup ok'\ncd nosuchdir && echo 'never printed'\necho \"status of the failed cd: $?\"\nls logs/missing.log 2>/dev/null || echo 'no missing.log: using default'\ndate +%Y > /dev/null; echo 'semicolon: always runs'", expect='any', note='&& stopped after the failed cd; || gave a fallback.'),
    [('sys', [
        dict(situation='Why A && B || C is not if/else.', cmd="true && false || echo 'C ran although A succeeded (B failed)'\nif true; then false; else echo 'never'; fi; echo \"if/else: else did not run (status $?)\"", why='Use if when B can fail.')]),
     ('qa', [
        dict(situation='Stop at the first failing check.', setup=CB, cmd="cd ~/cb\n[ -f conf/app.conf ] && grep -q '^port=' conf/app.conf && [ -d logs ] && echo 'all checks passed'\n[ -f conf/app.conf ] && grep -q '^tls=' conf/app.conf && echo 'not reached' || echo 'a check failed: tls missing'", why='&& chains are the shortest way to write a checklist.')]),
    ],
    anat=anatomy([('mkdir -p backup', 'cmd', 'step 1'), ('&&', 'opt', 'only if step 1 worked'), ('cp … backup/', 'arg', 'step 2'), ('|| echo FAIL', 'opt', 'if any failed')], 'Read left to right; the operator looks at the status of everything before it.')
) + cmdcard_u(['any “filter, transform, count” question', 'logs, CSVs, command output'],
               ['parsing ls output for scripts', 'trusting a pipeline’s status without pipefail'])(
    'pipes', 'A | B · A |& B · tee · PIPESTATUS · pipefail', 'pipelines',
    'A pipe sends one command’s standard output to the next command’s standard input; all parts run at the same time. <code>|&amp;</code> also sends errors. <code>tee file</code> saves a copy in the middle. <code>${PIPESTATUS[@]}</code> holds every part’s exit status, and <code>set -o pipefail</code> makes the pipeline fail if any part fails.',
    'A | B | C   ·   A | tee f | B   ·   set -o pipefail', 'safe',
    [('A | B', 'stdout to stdin', 'filters'),
     ('A |& B', 'stdout and stderr', 'build logs'),
     ('A | tee f | B', 'save a copy', 'debugging'),
     ('A | tee -a f', 'append', 'logs'),
     ('${PIPESTATUS[@]}', 'all statuses', 'checks'),
     ('set -o pipefail', 'strict status', 'scripts'),
     ('A | head -1', 'first line only', 'stops A early')],
    dict(setup=CB, cmd="cd ~/cb/logs\ngrep -E '\" [45][0-9]{2} ' access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn\ngrep -E '\" [45][0-9]{2} ' access.log | cut -d' ' -f1 | sort -u | wc -l", note='The manager’s answer: 3 IPs got errors; 10.0.0.5 the most (2).'),
    [('qa', [
        dict(situation='The puzzle: a pipeline hides a failure.', cmd="grep ERROR /nope/app.log | wc -l && echo 'report sent'\ngrep ERROR /nope/app.log 2>/dev/null | wc -l; echo \"statuses: ${PIPESTATUS[*]}\"\nset -o pipefail\ngrep ERROR /nope/app.log 2>/dev/null | wc -l && echo 'report sent' || echo \"pipeline failed with $?\"", expect='any', why='Without pipefail only wc’s 0 counts; with it the grep failure (2) is the pipeline’s status.')]),
     ('dev', [
        dict(situation='tee to see the middle of a pipeline.', setup=CB, cmd="cd ~/cb/logs\ncut -d'\"' -f2 access.log | tee /tmp/requests.txt | awk '{print $2}' | sort | uniq -c | sort -rn | head -2\nhead -2 /tmp/requests.txt; rm /tmp/requests.txt", why='tee saved step 1 so you can check it while the pipeline carries on.')]),
    ]
) + cmdcard_u(['trying something in another folder', 'one redirect for several commands', 'a temporary variable or option'],
               ['{ } without the spaces and ;'])(
    'group', '( A; B ) · { A; B; } · bash -c', 'subshells and groups',
    '<code>( … )</code> runs the commands in a child shell: <code>cd</code>, variables, <code>set</code> options and <code>exit</code> stay inside it. <code>{ …; }</code> runs them in your shell (note the spaces and the final ;) and is the way to redirect or pipe several commands at once.',
    '(cd dir && cmd)   ·   { cmd1; cmd2; } > file', 'safe',
    [('(cd /x && cmd)', 'cd only for cmd', 'safe cd'),
     ('(export V=1; cmd)', 'temporary variable', 'isolate'),
     ('(set -e; …)', 'option only inside', 'strict block'),
     ('{ a; b; } > f', 'one redirect', 'reports'),
     ('{ a; b; } | cmd', 'pipe both', 'combine output'),
     ('cmd || { echo err; exit 1; }', 'several on failure', 'scripts')],
    dict(setup=CB, cmd="cd ~/cb\n(cd logs && wc -l < access.log); pwd | sed 's|.*/||'\n{ cd logs; pwd | sed 's|.*/||'; }; cd ~/cb\nx=1; (x=2); echo \"after ( ): x=$x\"; { x=3; }; echo \"after { }: x=$x\"\n{ echo '# report'; date +%Y; wc -l < logs/access.log; } > report.txt; cat report.txt", note='( ) forgot the cd and x=2; { } kept them; one > collected three commands.'),
    [('sys', [
        dict(situation='Fail with a message and stop.', setup=CB, cmd="cd ~/cb\ncheck(){ [ -f \"$1\" ] || { echo \"missing: $1\" >&2; return 1; }; echo \"found: $1\"; }\ncheck conf/app.conf; check conf/db.conf 2>&1; echo \"status $?\"", why='|| { …; } runs several commands only on failure.')]),
    ]
) + cmdcard_u(['values inside commands (dates, counts, names)', 'comparing two outputs', 'sending one output to two places'],
               ['$(cat bigfile) for huge files', 'unquoted $( ) with spaces'])(
    'subst', '"$(A)" · <(A) · >(A)', 'command and process substitution',
    '<code>$(A)</code> runs A and puts its output into the command line as text (quote it). <code>&lt;(A)</code> runs A and gives the command a file name to read from, so tools that only accept files (diff, comm, join, paste) can read command output. <code>&gt;(A)</code> is the opposite: a file name that feeds A.',
    'echo "$(cmd)"   ·   diff <(cmd1) <(cmd2)   ·   tee >(cmd) > file', 'safe',
    [('"$(cmd)"', 'output as text', 'arguments'),
     ('$(< file)', 'file contents', 'fast'),
     ('<(cmd)', 'output as a file', 'diff, comm'),
     ('>(cmd)', 'write into cmd', 'tee to many'),
     ('while … done < <(cmd)', 'loop without subshell', 'variables survive'),
     ('$(( ))', 'arithmetic', 'not a command')],
    dict(setup=CB, cmd="cd ~/cb\necho \"$(wc -l < logs/access.log) requests, $(cut -d' ' -f1 logs/access.log | sort -u | wc -l) visitors on $(hostname)\"\ndiff <(sort conf/app.conf) <(sort conf/app.conf.new)\ncomm -12 <(sort conf/app.conf) <(sort conf/app.conf.new)", expect='any', note='diff and comm read two command outputs as files: what changed and what stayed.'),
    [('dev', [
        dict(situation='The puzzle: a counter in a piped loop.', setup=CB, cmd="cd ~/cb\nn=0; cat logs/access.log | while read -r line; do n=$((n+1)); done; echo \"pipe: n=$n\"\nn=0; while read -r line; do n=$((n+1)); done < <(cat logs/access.log); echo \"process substitution: n=$n\"\nn=0; while read -r line; do n=$((n+1)); done < logs/access.log; echo \"plain redirect: n=$n\"", why='The piped while ran in a subshell; its n was lost.')]),
     ('data', [
        dict(situation='One output, two destinations.', setup=CB, cmd="cd ~/cb/logs\ncut -d' ' -f1 access.log | tee >(sort -u > ips.txt) | wc -l; sleep 0.2\necho \"unique IPs saved: $(wc -l < ips.txt)\"", why='tee >(…) feeds a second pipeline while the first continues.')]),
    ]
) + undo('Combining is safe; what you combine may not be.', [
    ('A chain ran too far:', 'use <code>&amp;&amp;</code> instead of <code>;</code>, and <code>set -e</code> in scripts.'),
    ('Unsure what a pipeline does:', 'run it stage by stage, or insert <code>| tee /tmp/stepN</code>.'),
    ('Deleting from a pipeline:', 'end with <code>echo</code> first (… | xargs echo rm), then remove echo.'),
    ('Variables lost in a loop:', '<code>done &lt; &lt;(cmd)</code> instead of <code>cmd | while</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='{ echo a; echo b }', meaning='The } needs a ; or newline before it.', fix='{ echo a; echo b; }'),
    dict(cmd='diff <(ls) <(ls /nope)', expect='any', meaning='One side failed; diff still compares what it got.', fix='Check both commands first.'),
    dict(cmd='cd /nope && echo ok', meaning='&& stopped after the failed cd.', fix='This is the safe behaviour.'),
]) + qc('What does <code>${PIPESTATUS[@]}</code> show after <code>false | true</code>?', '1 0: the status of each part.') + '''
'''
cards = cards + '</section>\n'

STAGES = [("grep -E '\" [45][0-9]{2} ' access.log", 'error lines'), ("… | cut -d' ' -f1", 'only the IP'), ('… | sort', 'same IPs together'), ('… | uniq -c', 'count each'), ('… | sort -rn', 'biggest first')]
OUTS = [['"POST /login" 401', '"GET /admin" 403', '"GET /api/orders" 500'], ['10.0.0.5', '10.0.0.9', '10.0.0.7'], ['10.0.0.5', '10.0.0.7', '10.0.0.9'], ['1 10.0.0.5', '1 10.0.0.7', '1 10.0.0.9'], ['1 10.0.0.5', '1 10.0.0.7', '1 10.0.0.9']]
def pipe_frame(k):
    o = ''
    for i in range(5):
        o += label_box(4 + i * 71, 14, 66, 36, [STAGES[i][1]], 'green' if i == k else ('blue' if i < k else 'card'), 6.6)
        if i < 4:
            o += arrow(70 + i * 71, 32, 75 + i * 71, 32)
    o += ''.join(t(180, 80 + j * 18, s, 8.6, 'ink2') for j, s in enumerate(OUTS[k]))
    return o
see = [term(14, 16, 332, 116, [f'$ {STAGES[k][0]}'] + [(x, 'out') for x in OUTS[k][:3]], title='riya@web01: ~/cb/logs', prompt='$', size=7.0) + cap(f'Stage {k + 1}: {STAGES[k][1]}.', '', 'card', y=150, h=34) for k in range(5)]
behind = [pipe_frame(k) + t(180, 170, f'Output of stage {k + 1}', 8.4, 'violet', bold=True) for k in range(5)]
two = anim_two('A pipeline, stage by stage', 'Behind the screen: what flows through each pipe',
               'A terminal running the error-IP pipeline one stage at a time.',
               'Five boxes connected by arrows; the current stage is highlighted and the lines leaving it are shown underneath.', see, behind,
               ['grep.', 'cut.', 'sort.', 'uniq -c.', 'sort -rn.'],
               ['grep', 'cut', 'sort', 'uniq', 'sort -rn'])

def chain(k):
    boxes = [('cd /var/ww', 'red', 'fails'), ('rm -rf old/', ['red', 'card'][k >= 2], '')]
    o = label_box(20, 30, 140, 40, ['cd /var/ww'], 'red', 9)
    op = [';', ';', '&&', '&&'][k]
    o += t(180, 54, op, 14, 'acc', bold=True)
    runs = k < 2
    o += label_box(200, 30, 140, 40, ['rm -rf old/'], 'red' if runs and k == 1 else ('card' if not runs else 'amber'), 9)
    o += t(180, 120, ['; ignores the failure…', '…rm runs in the WRONG folder!', '&& checks the status…', '…rm never runs. Safe.'][k], 9.6, 'red' if k == 1 else ('green' if k == 3 else 'violet'), bold=True)
    return o
s1 = anim_one('Animated example', '; versus && after a typo',
              'The same two commands with a different operator.',
              'cd /var/ww ; rm -rf old/', 'Two boxes: a failed cd and an rm. With ; the rm still runs; with && it does not.', [chain(k) for k in range(4)],
              [';', 'disaster', '&&', 'safe'], hid='scenario-chain')

dx = dissect('Layer by layer: what a pipeline really is',
    'Each layer has a real command and output from our build machine.', [
    dict(key='par', name='Parallel', sub='all at once', why='Streams.', how='All parts start together.', impl='fork per part.', used='Speed.',
         cmd="s=$SECONDS; sleep 1 | sleep 1 | sleep 1; echo \"three 1-second sleeps in a pipe took $((SECONDS - s)) s\""),
    dict(key='fd', name='File descriptors', sub='/proc/self/fd', why='How data moves.', how='fd 0 and 1 are pipes.', impl='pipe().', used='Debugging.',
         cmd="ls -l /proc/self/fd/0 /proc/self/fd/1 < /dev/null | cat | awk '{print $9, $10, $11}' | sed -E 's/[0-9]{3,}/N/'"),
    dict(key='sub', name='Subshells', sub='$BASHPID', why='Variables lost.', how='Each part is a child.', impl='$$ stays, BASHPID changes.', used='Puzzle 3.',
         cmd="echo \"shell $BASHPID\" | sed 's/[0-9]*$/X/'; echo x | { echo \"pipe part $BASHPID\" | sed 's/[0-9]*$/Y/'; }; [ $$ = $BASHPID ] && echo 'outside the pipe: same as $$'"),
    dict(key='pipe', name='SIGPIPE', sub='early exit', why='head stops yes.', how='Write to a closed pipe.', impl='141.', used='Big outputs.',
         cmd="yes | head -1; echo \"statuses: ${PIPESTATUS[*]} (141 = 128 + 13 PIPE)\""),
], hint='From parallel processes to SIGPIPE. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A pipeline stage by stage, and ; versus &&</h2>
''' + two + s1 + dx + qc('Why did three 1-second sleeps in a pipeline take about 1 second, not 3?', 'All parts of a pipeline run at the same time.') + '''
</section>
'''

VAR = variations('Twenty more one-liners that combine commands. All were really run on our build machine on the sample files.', [
    ('&& || ;', [
        dict(title='Create and enter a folder', cmd="mkdir -p ~/cb/new && cd ~/cb/new && pwd | sed 's|.*/cb|~/cb|'", why='Each step only after the previous one worked.'),
        dict(title='Default value on failure', setup=CB, cmd="port=$(grep -oP '^port=\\K.*' ~/cb/conf/app.conf || echo 80); echo \"port $port\"; p2=$(grep -oP '^tls=\\K.*' ~/cb/conf/app.conf || echo off); echo \"tls $p2\"", why='|| gives a fallback value.'),
        dict(title='Retry until it works (3 tries)', cmd="n=0; until [ $n -ge 3 ] || [ -e /tmp/never-$$ ]; do n=$((n+1)); echo \"try $n\"; done; [ -e /tmp/never-$$ ] || echo 'giving up after 3'", why='until with || for a retry limit.'),
        dict(title='Run a command quietly, report only the result', cmd="grep -q root /etc/passwd && echo 'root exists' || echo 'no root?'", why='-q prints nothing; only the status matters.'),
        dict(title='Invert a test', setup=CB, cmd="! grep -q '^debug=' ~/cb/conf/app.conf && echo 'debug is not set'", why='! flips the status.'),
    ]),
    ('Pipes and tee', [
        dict(title='Requests per status code', setup=CB, cmd="awk '{print $(NF-1)}' ~/cb/logs/access.log | sort | uniq -c | sort -rn", why='The field before last is the status code.'),
        dict(title='Top page', setup=CB, cmd="cut -d'\"' -f2 ~/cb/logs/access.log | awk '{print $2}' | sort | uniq -c | sort -rn | head -1", why='Request line → URL → count.'),
        dict(title='Bytes sent in total', setup=CB, cmd="awk '{s+=$NF} END{print s, \"bytes\"}' ~/cb/logs/access.log", why='Sometimes awk alone replaces a pipeline.'),
        dict(title='Errors and normal output together', cmd="ls /etc/hostname /nope |& sort", expect='any', why='|& sends stderr into the pipe too.'),
        dict(title='Save every stage', setup=CB, cmd="cd ~/cb/logs; grep ' 200 ' access.log | tee ok.txt | cut -d' ' -f1 | tee ok_ips.txt | sort -u | wc -l; wc -l ok.txt ok_ips.txt | head -2", why='tee checkpoints for debugging.'),
        dict(title='Number the output lines', cmd="ls /etc | head -3 | nl", why='nl numbers lines.'),
        dict(title='Count words across files', setup=CB, cmd="cat ~/cb/conf/*.conf* | tr '=' '\\n' | sort | uniq -c | sort -rn | head -3", why='tr splits keys and values into lines.'),
    ]),
    ('Groups and substitutions', [
        dict(title='A small report in one file', setup=CB, cmd="cd ~/cb; { echo \"== $(date +%F) ==\"; echo \"requests: $(wc -l < logs/access.log)\"; echo \"errors: $(grep -cE '\" [45][0-9]{2} ' logs/access.log)\"; } > daily.txt; cat daily.txt", why='{ } with one redirect; $( ) for the numbers.'),
        dict(title='Temporary folder in a subshell', cmd="(cd /etc && ls | wc -l); pwd | sed 's|/home/riya|~|'", why='The cd ended with the subshell.'),
        dict(title='Lines in A but not in B', setup=CB, cmd="comm -23 <(sort ~/cb/conf/app.conf) <(sort ~/cb/conf/app.conf.new)", why='comm needs sorted files: process substitution provides them.'),
        dict(title='Side by side', setup=CB, cmd="paste -d'|' <(cut -d= -f1 ~/cb/conf/app.conf) <(cut -d= -f2 ~/cb/conf/app.conf) <(cut -d= -f2 ~/cb/conf/app.conf.new)", why='Three command outputs as three columns.'),
        dict(title='Join two command outputs by key', cmd="join <(printf 'a 1\\nb 2\\n') <(printf 'a x\\nb y\\n')", why='join on the first field (Lesson 13.5).'),
        dict(title='Loop over command output safely', setup=CB, cmd="total=0; while read -r ip; do total=$((total+1)); done < <(cut -d' ' -f1 ~/cb/logs/access.log | sort -u); echo \"$total unique IPs\"", why='The variable survives.'),
        dict(title='Measure a pipeline', setup=CB, cmd="TIMEFORMAT='took %Rs'; time (sort ~/cb/logs/access.log | uniq | wc -l) 2>&1 | sed -E 's/[0-9]\\.[0-9]+s/N s/'", why='time on a ( ) group times the whole pipeline.'),
        dict(title='Build a command from parts', cmd="host=web01; svc=nginx; echo \"ssh $host 'systemctl is-active $svc && systemctl reload $svc'\"", why='Quoting so && runs on the remote side.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Combining at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['&&', 'deploys'], 'blue', 8.6), '1. Deploy scripts',
              'git pull && npm ci && npm test && systemctl restart app: nothing restarts after a failed test.', ['Pull', '*&& chain', 'safe restart']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['| uniq -c', 'logs'], 'green', 8.6), '2. Quick log answers',
    'Top IPs, failing URLs and error counts during an incident (Lesson 13.3).', ['Log', '*pipeline', 'answer']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['<( )', 'audits'], 'amber', 8.6), '3. Comparing servers and configs',
    'diff <(ssh a cat /etc/x) <(ssh b cat /etc/x) finds drift between servers.', ['Two outputs', '*diff <( )', 'drift']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['pipefail', 'CI'], 'red', 8.6), '4. CI pipelines',
    'Build scripts start with set -euo pipefail so a failing step inside a pipe fails the build.', ['Script', '*pipefail', 'honest status']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['tee', 'audit'], 'violet', 8.6), '5. Keeping a record',
    'make |& tee build.log keeps the full build output while you watch it.', ['Run', '*|& tee', 'log']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Count files in a folder', scenario='How many?', cmd="ls /etc | wc -l | sed 's/[0-9]*/N/'", explain='ls | wc -l.'),
    dict(level='b', title='Safe change of folder', scenario='Before deleting.', cmd="cd /tmp && echo \"now in $(pwd)\"", explain='&&.'),
    dict(level='i', title='Who got errors?', scenario='Incident.', setup=CB, cmd="grep -E '\" [45][0-9]{2} ' ~/cb/logs/access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn | head -1", explain='The story pipeline.'),
    dict(level='i', title='What changed in the config?', scenario='Review.', setup=CB, cmd="diff <(sort ~/cb/conf/app.conf) <(sort ~/cb/conf/app.conf.new) | grep '^[<>]'", explain='Process substitution.'),
    dict(level='a', title='Fail honestly', scenario='Scripts.', cmd="set -o pipefail; false | sort > /dev/null || echo \"pipeline status $?\"", explain='pipefail.'),
], extra=build_up('the manager’s question', 'Riya builds the one-liner from the story stage by stage, checking each output.', CB, [
    ("cd ~/cb/logs; grep -E '\" [45][0-9]{2} ' access.log", '1. Only error lines (4xx, 5xx).'),
    ("cd ~/cb/logs; grep -E '\" [45][0-9]{2} ' access.log | cut -d' ' -f1", '2. Only the IP.'),
    ("cd ~/cb/logs; grep -E '\" [45][0-9]{2} ' access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn", '3. Count and rank.'),
    ("cd ~/cb/logs; set -o pipefail; n=$(grep -E '\" [45][0-9]{2} ' access.log | cut -d' ' -f1 | sort -u | wc -l) && echo \"$n IPs got errors\" || echo 'pipeline failed'", '4. One sentence for the manager, with an honest status.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('B only after A worked', '&&', 'Safe.', ';'),
    ('Data from A into B', '|', 'Streams.', 'Temp files.'),
    ('A command wants a file', '<( )', 'No temp files.', 'Writing /tmp files and forgetting them.'),
    ('Output as an argument', '"$( )"', 'Quoted, nests.', 'Backticks.'),
    ('Variables must survive a loop', 'done < <(cmd)', 'No subshell.', 'cmd | while.'),
    ('Branching with failures', 'if … then … else', 'Clear.', 'A && B || C.'),
]) + keys('Handy forms.', [
    ('A && B || echo fail', 'chain with alert', 'scripts'),
    ('A |& tee log', 'watch and keep', 'builds'),
    ('(cd d && cmd)', 'cd only here', 'safety'),
    ('{ a; b; } > f', 'one redirect', 'reports'),
    ('diff <(a) <(b)', 'compare outputs', 'audits'),
    ('set -o pipefail', 'honest pipes', 'scripts'),
]) + scriptit('errorreport.sh', 'Answer three questions about a web log with combined commands (error count, top error IP, top failing URL), stop with a clear message if the log is missing, and give the right exit status.',
'''set -o pipefail
log=${1:-$HOME/cb/logs/access.log}
[ -r "$log" ] || { echo "cannot read $log" >&2; exit 1; }
err=$(grep -cE '" [45][0-9]{2} ' "$log") || err=0
top_ip=$(grep -E '" [45][0-9]{2} ' "$log" | cut -d' ' -f1 | sort | uniq -c | sort -rn | awk 'NR==1{print $2" ("$1")"}')
top_url=$(grep -E '" [45][0-9]{2} ' "$log" | cut -d'"' -f2 | awk '{print $2}' | sort | uniq -c | sort -rn | awk 'NR==1{print $2}')
{ echo "log:        ${log##*/}"; echo "errors:     $err"; echo "top IP:     ${top_ip:-none}"; echo "top URL:    ${top_url:-none}"; } | tee /tmp/errorreport.txt
[ "$err" -eq 0 ]''',
'<p>Run without arguments, so it reads the sample log; it exits with status 1 because there are errors.</p>', expect='any') + puzzle_answer('<b>1.</b> A pipeline’s exit status is that of its <b>last</b> command: grep failed (2), but wc succeeded (0), so <code>&amp;&amp;</code> ran. Use <code>set -o pipefail</code> or check <code>${PIPESTATUS[0]}</code>. <b>2.</b> <code>;</code> ignores the failed <code>cd</code>, so <code>rm -rf old/</code> ran in the current folder. Always <code>cd dir &amp;&amp; …</code> (or use full paths). <b>3.</b> Each part of a pipeline runs in a subshell; the loop counted in a child, and the parent’s n stayed empty. Use <code>while …; done &lt; list.txt</code> or <code>&lt; &lt;(cmd)</code>.') + qc('Which operator runs the next command only if the previous one failed?', '||.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/cb', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../05-redirection-and-pipes/03-pipes-and-tee-building-command-pipelines/">Lessons 5.3</a> and <a href="../../05-redirection-and-pipes/04-chaining-commands-exit-codes-and-xargs/">5.4</a> (pipes, tee, chaining; this lesson goes further) and <a href="../../12-shell-environment/11-metacharacters-expansion-and-directory-stacks/">Lesson 12.11</a> (expansion).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
