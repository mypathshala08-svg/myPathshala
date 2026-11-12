import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

FS = r"""rm -rf ~/fs; mkdir -p ~/fs/logs ~/fs/bin; cd ~/fs
printf 'GET /a 200\nGET /b 500\nGET /c 200\nGET /d 404\n' > logs/web.log"""
HELLO = r"""printf '#!/bin/bash\n# hello.sh: my first script\nname="Riya"\necho "Hello, $name!"\necho "Today is $(date +%%A) and you are in $PWD"\n' > ~/fs/hello.sh"""

HOOK = hook('Every morning Riya types the same five commands: check the disk, count today’s errors in the web log, list new uploads, back up the config, and print a summary for her team lead. It takes ten minutes and she sometimes forgets a step. A <b>shell script</b> is simply those commands saved in a file, with one special first line (<code>#!/bin/bash</code>) and an execute permission. After that, one word runs all five, in the same order, every time, even from cron at 6 a.m. This lesson takes you from an empty file to a script you can run by name, and explains every way it can go wrong on the first try.',
    ['write a script file: the shebang line <code>#!/bin/bash</code>, comments, variables and several commands',
     'run it in all four ways (<code>./script</code>, <code>bash script</code>, <code>source script</code>, by name from PATH) and know the difference',
     'make it executable with <code>chmod +x</code>, put it in <code>~/bin</code>, and return a proper exit status with <code>exit</code>',
     'decode first-script errors: Permission denied, command not found, “required file not found” from Windows line endings, wrong shebang'])
ROAD = roadmap([
    ('story', 'The story', 3, 'five commands every morning'),
    ('decide', 'Which way to run?', 2, 'the quick chart'),
    ('definition', 'What a script is', 5, 'simple meaning + 4 depths'),
    ('types', 'Four ways to run', 4, 'side by side'),
    ('commands', 'Writing and running', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'what #! does'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a daily report script'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('How to run it? (decide in 5 seconds)', [
    ('Normal way, your own script', 'chmod +x s.sh; ./s.sh', 'uses the #! line'),
    ('Quick test, no chmod needed', 'bash s.sh', 'ignores the #! line'),
    ('Script must change MY shell (cd, export)', 'source s.sh', 'runs in the current shell'),
    ('Run it by name from anywhere', 'mv s.sh ~/bin/s; chmod +x', '~/bin in PATH'),
    ('Check syntax only', 'bash -n s.sh', 'nothing runs'),
    ('See each line as it runs', 'bash -x s.sh', 'debugging (12.6)'),
    ('Script made on Windows fails', 'sed -i \'s/\\r$//\' s.sh', 'remove CRLF'),
    ('A Python/other script', '#!/usr/bin/env python3', 'any interpreter'),
])

cmap = concept_map(
    [('12.1', 'Variables', 'name=value'), ('9.2', 'chmod', '+x'), ('5.4', 'Exit status', '$? and &&')],
    ['a script = commands in a file', 'the shebang #! and comments', 'chmod +x and ./script', 'four ways to run, and PATH', 'exit status and first-script errors'],
    [('12.6', 'set -e -u -x', 'safer scripts'), ('12.7', 'Script input', '$1, read'), ('12.8', 'if and case', 'decisions'), ('17.4', 'cron', 'run it every day')],
    'A script is a text file of commands. #! says which program runs it, chmod +x lets you run it, and exit tells the caller how it went.')

sc = (term(20, 14, 316, 156, ['$ cat hello.sh', ('#!/bin/bash', 'acc'), ('echo "Hello, $USER!"', 'out'), '$ ./hello.sh', ('bash: ./hello.sh: Permission denied', 'err'), '$ chmod +x hello.sh', '$ ./hello.sh', ('Hello, riya!', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=15)
      + t(352, 36, 'A script needs:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['1. commands in a file', '2. #!/bin/bash first', '3. chmod +x', '4. ./name to run', '5. exit 0 / 1'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Five commands every morning</h2>
  <div class="story">
''' + puzzle('Riya writes <code>report.sh</code> on her Windows laptop, copies it to the server, runs <code>chmod +x report.sh</code> and <code>./report.sh</code>. Answer: <code>cannot execute: required file not found</code>. The file is right there, <code>ls</code> shows it, and <code>bash report.sh</code> prints strange <code>$\'\\r\': command not found</code> errors. What is “not found”, and how does she fix it in one command?') + '''
    <p class="narration">Riya writes her first script, and the first run fails, as almost everyone’s does.</p>
''' + scene('A terminal: cat shows a two-line script with #!/bin/bash; ./hello.sh says Permission denied; after chmod +x it prints Hello.', sc,
            'A script is a <tspan font-weight="700" class="s-acc">text file</tspan> plus <tspan font-weight="700" class="s-acc">#!</tspan> plus <tspan font-weight="700" class="s-acc">x</tspan>.') + '''
K> Why Permission denied? It is my own file!
A> New files are created without execute permission (umask, Lesson 9.3). Linux will not run a file as a program until someone says it is one: <code>chmod +x</code>.
R> And what is the <code>#!</code> line for?
A> When you run <code>./hello.sh</code>, the kernel looks at the first two bytes. If they are <code>#!</code>, it runs the program named on that line and gives it your file. That is how the same mechanism runs bash, Python or Perl scripts. Today: writing, running, and every first-day error.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A recipe card: the first line says which cook should read it (shebang), the steps are the commands, and a stamp says the card may be used (execute permission).">'
       + label_box(14, 20, 190, 110, ['first line #!', '“give this card', 'to the bash cook”', '#!/bin/bash'], 'amber', 8.6)
       + label_box(224, 20, 190, 110, ['the steps', 'one command a line', '# notes for humans', 'variables, $( )'], 'blue', 8.6)
       + label_box(434, 20, 192, 110, ['the stamp', 'chmod +x', '= “this card', 'may be used”'], 'green', 8.6)
       + t(320, 160, './hello.sh = hand the card to the cook named on line 1.', 9.6, 'ink2')
       + t(320, 182, 'bash hello.sh = you choose the cook yourself.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Scripts at four depths', [
    ('v', 'No jargon: a recipe card', '      <p>A script is a recipe card for the shell.</p>' + pic),
    ('b', 'The four steps', '''      <ul>
        <li>Create the file: <code>nano hello.sh</code>.</li>
        <li>First line <code>#!/bin/bash</code>, then your commands, one per line. <code>#</code> starts a comment.</li>
        <li><code>chmod +x hello.sh</code> once.</li>
        <li>Run it: <code>./hello.sh</code> (the <code>./</code> means “in this folder”).</li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li>The shebang must be the very first line, starting at column 1: <code>#!/bin/bash</code> or <code>#!/usr/bin/env bash</code> (finds bash in PATH).</li>
        <li>The <code>.sh</code> extension is only a convention for humans; Linux ignores it. Tools in <code>~/bin</code> usually have no extension.</li>
        <li>A script runs in a <b>new</b> bash process: its <code>cd</code> and variables vanish when it ends; use <code>source</code> to run it in your shell (Lesson 11.1).</li>
        <li>The script’s exit status is that of its last command, or the number given to <code>exit</code> (0 = success, 1–255 = failure). By default a script continues after a failing command (Lesson 12.6).</li>
      </ul>'''),
    ('a', 'Behind the screen: execve and #!', '''      <ul>
        <li><code>./hello.sh</code> → the shell forks and calls <code>execve("./hello.sh")</code>. The kernel sees <code>#!</code> and turns it into <code>execve("/bin/bash", ["/bin/bash", "./hello.sh"])</code>.</li>
        <li>Only one argument is allowed after the interpreter on Linux (<code>#!/usr/bin/env bash -e</code> does not work as expected; use <code>env -S</code> or <code>set -e</code> inside).</li>
        <li>With a Windows file, the line is really <code>#!/bin/bash\\r</code>: the kernel looks for a program literally called <code>bash\\r</code>, which does not exist: “required file not found”.</li>
        <li>No shebang: the kernel refuses (ENOEXEC) and bash then runs the file itself with a new bash; other callers (cron, Python’s subprocess) may fail.</li>
        <li>bash reads a script a little at a time while running; editing a script while it runs can make it execute garbage.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>A shell script</h2>
''' + def_block(
    'A <b>shell script</b> is a text file containing shell commands that are executed in sequence by a shell interpreter. Its first line is usually a <b>shebang</b> (<code>#!</code> followed by the interpreter’s path) that tells the kernel which program should run the file. With execute permission, the script can be run like any other program, and it returns an <b>exit status</b> to its caller.',
    'Your commands in a file, with a first line saying “run me with bash”.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Script', 'A file of commands run in order.'),
    ('Shebang', 'The #! first line naming the interpreter.'),
    ('Interpreter', 'The program that reads the script (bash).'),
    ('Comment', '# … ignored by the shell.'),
    ('Execute permission', 'chmod +x: may be run as a program.'),
    ('./', 'This folder (not in PATH).'),
    ('Exit status', '0 = OK, 1–255 = problem.'),
    ('CRLF', 'Windows line ending \\r\\n.'),
]) + '\n' + names('Where the names come from.', [
    ('#!', 'shebang / hash-bang', '# (hash) + ! (bang).'),
    ('.sh', 'shell', 'Convention only.'),
    ('env', 'environment', 'Finds bash in PATH.'),
    ('./', 'current folder', 'dot = here.'),
    ('exit', 'end with a status', 'Builtin.'),
    ('~/bin', 'your bin folder', 'Added to PATH by .profile.'),
    ('CR', 'carriage return', '\\r, from typewriters.'),
    ('dos2unix', 'DOS to Unix', 'Removes \\r.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('First line', '<code>#!/bin/bash</code>'),
    ('Make runnable', '<code>chmod +x s.sh</code>'),
    ('Run', '<code>./s.sh</code>'),
    ('Without +x', '<code>bash s.sh</code>'),
    ('Status', '<code>exit 0</code> / <code>exit 1</code>'),
    ('Syntax check', '<code>bash -n s.sh</code>'),
]) + '\n' + lv + didyou('Many “commands” you use every day are shell scripts: run <code>file /usr/bin/* | grep -c "shell script"</code> on Ubuntu and you will find dozens, such as <code>ldd</code>, <code>gunzip</code> and <code>which</code>.') + '''
EXAM> “Write a script that prints Hello World, and give two ways to run it.” → <code>#!/bin/bash</code> / <code>echo "Hello World"</code>; run with <code>chmod +x hello.sh; ./hello.sh</code> or <code>bash hello.sh</code>.
''' + qc('Why must you type <code>./hello.sh</code> and not just <code>hello.sh</code>?', 'The current folder is not in PATH (for safety), so the shell would not find it. ./ gives the exact location.') + mistake('“All scripts must have the .sh extension”',
    'The extension is optional: Linux decides by the #! line and the x permission, not the name',
    'Checked: a file called hello (no extension) with #!/bin/bash and chmod +x runs fine. Tools you install in ~/bin are usually extension-free.') + mistake('#!/bin/sh at the top, then bash features ([[ ]], arrays, ((i++)))',
    '#!/bin/bash for bash scripts; #!/bin/sh only for POSIX scripts',
    'On Ubuntu /bin/sh is dash, not the Bourne shell and not bash (Lesson 12.1). bash-only lines fail or misbehave under dash.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Four ways to run a script</h2>
''' + table(['', '<code>./s.sh</code>', '<code>bash s.sh</code>', '<code>source s.sh</code> / <code>. s.sh</code>', '<code>s</code> (by name)'], [
    ['Needs chmod +x', 'yes', 'no', 'no', 'yes'],
    ['Uses the #! line', 'yes', 'no (bash chosen)', 'no (current shell)', 'yes'],
    ['New process', 'yes', 'yes', 'no', 'yes'],
    ['cd / variables survive', 'no', 'no', 'yes', 'no'],
    ['exit in the script', 'ends the script', 'ends the script', 'closes YOUR shell!', 'ends the script'],
    ['Typical use', 'normal', 'testing, no x', 'env files, functions', 'tools in ~/bin'],
], minw=600) + table(['Shebang', 'Meaning'], [
    ['<code>#!/bin/bash</code>', 'bash at a fixed path (Linux standard)'],
    ['<code>#!/usr/bin/env bash</code>', 'first bash in PATH (portable: macOS, BSD)'],
    ['<code>#!/bin/sh</code>', 'POSIX shell: dash on Ubuntu, bash on RHEL'],
    ['<code>#!/usr/bin/env python3</code>', 'a Python script'],
    ['none', 'bash runs it if you start it from bash; others may fail'],
], minw=420) + table(['File', 'Is it a script?'], [
    ['commands + #! + x', 'yes, a full program'],
    ['commands, no #!', 'works from bash, fragile elsewhere'],
    ['~/.bashrc', 'a script that is sourced, never executed'],
    ['/etc/profile.d/*.sh', 'sourced by login shells'],
], minw=360) + qc('A script ends with <code>exit 1</code>. You run it with <code>source</code>. What happens?', 'exit runs in your own shell, so your terminal closes (or your login ends). Never source scripts that call exit.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Writing and running scripts, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/fs</code> with a small web log <code>logs/web.log</code> (four requests: two 200, one 500, one 404).</p>
''' + cmdcard_u(['every script you write', 'turning daily commands into one tool'],
               ['one-off commands you will never repeat'])(
    'write', 'the script file: #! · # · commands', 'write it',
    'Line 1: the shebang. Then comments (<code>#</code>) explaining the purpose, variables at the top, then the commands in order. Write with nano or vim, or with a here-document as below.',
    '#!/bin/bash   ·   # comment   ·   commands…   ·   exit 0', 'safe',
    [('#!/bin/bash', 'interpreter', 'line 1 only'),
     ('# text', 'comment', 'explain why'),
     ('name=value', 'settings at the top', 'easy to change'),
     ('cmd; cmd', 'several on one line', 'short ones'),
     ('\\ at line end', 'continue a long line', 'readability'),
     ('exit N', 'status for the caller', '0 = OK')],
    dict(setup=FS + '; ' + HELLO, cmd="cd ~/fs\ncat -n hello.sh\nbash hello.sh | head -1", note='%A is the weekday. bash hello.sh runs it without needing chmod.'),
    [('sys', [
        dict(situation='The morning report as a script.', setup=FS, cmd="cd ~/fs; cat > report.sh <<'EOF'\n#!/bin/bash\n# report.sh: daily summary of the web log\nlog=logs/web.log\ntotal=$(wc -l < \"$log\")\nerrors=$(grep -c ' 5[0-9][0-9]$' \"$log\")\necho \"Report for $(date +%F)\"\necho \"requests: $total, server errors: $errors\"\nEOF\nchmod +x report.sh; ./report.sh | tail -1",
             why='Settings at the top, one job per line, $( ) to capture results. Lesson 17.4 runs it from cron.')]),
     ('dev', [
        dict(situation='Comments that help the next person.', setup=FS + '; ' + HELLO, cmd="cd ~/fs; grep -n '^#' hello.sh",
             why='Line 1 is the shebang (a comment for bash, an instruction for the kernel); line 2 says what the file is for.')]),
    ],
    anat=anatomy([('#!', 'cmd', 'shebang'), ('/bin/bash', 'arg', 'interpreter path')], 'Must be the first two bytes of the file.')
) + cmdcard_u(['running your scripts', 'choosing the right way'],
               ['source for normal scripts (exit closes your shell)'])(
    'run', 'chmod +x · ./ · bash · source', 'run it',
    '<code>chmod +x s.sh</code> once, then <code>./s.sh</code>. <code>bash s.sh</code> works without x and ignores the shebang. <code>source s.sh</code> runs it in your current shell. <code>bash -n</code> checks syntax without running.',
    'chmod +x s.sh && ./s.sh   ·   bash s.sh   ·   source s.sh', 'change',
    [('chmod +x', 'allow running', 'once'),
     ('./s.sh', 'run with its #!', 'normal'),
     ('bash s.sh', 'run with bash', 'no x'),
     ('source s.sh', 'in this shell', 'env files'),
     ('bash -n s.sh', 'syntax only', 'before running'),
     ('$?', 'the status', 'after it ends')],
    dict(setup=FS + '; ' + HELLO, cmd="cd ~/fs\n./hello.sh; echo \"exit $?\"\nchmod +x hello.sh\n./hello.sh | head -1; echo \"exit $?\"", expect='any', note='126 = found but not executable. After chmod +x it runs.'),
    [('devops', [
        dict(situation='Run it by name from anywhere.', setup=FS + '; ' + HELLO, cmd="cd ~/fs; cp hello.sh bin/hello; chmod +x bin/hello\nexport PATH=\"$HOME/fs/bin:$PATH\"\ncd /tmp; hello | head -1; type hello",
             why='Ubuntu’s ~/.profile adds ~/bin to PATH if it exists (Lesson 12.2); here we add ~/fs/bin by hand.')]),
     ('qa', [
        dict(situation='source vs run: who keeps the change?', setup=FS, cmd="cd ~/fs; printf 'cd /tmp\\nMODE=test\\n' > setenv.sh\nbash setenv.sh; echo \"bash:   $PWD [$MODE]\"\nsource setenv.sh; echo \"source: $PWD [$MODE]\"",
             why='Only source changed the current shell’s folder and variables.')]),
    ]
) + cmdcard_u(['telling callers (cron, CI, &&) whether the script worked', 'stopping early on a problem'],
               ['exit inside a sourced file', 'numbers above 255 (they wrap)'])(
    'exit', 'exit · $?', 'report success or failure',
    '<code>exit N</code> ends the script with status N (0 = success, 1–255 = failure). Without exit, the status is that of the last command. The caller reads it as <code>$?</code> or uses <code>&amp;&amp;</code> / <code>||</code> (Lesson 5.4).',
    'exit 0   ·   exit 1   ·   ./s.sh && echo ok || echo failed', 'safe',
    [('exit 0', 'success', 'all good'),
     ('exit 1', 'general failure', 'problem'),
     ('exit 2', 'wrong usage (convention)', 'bad arguments'),
     ('cmd || exit 1', 'stop if cmd fails', 'guard'),
     ('exit 256', 'wraps to 0!', 'avoid')],
    dict(setup=FS, cmd="cd ~/fs; printf '#!/bin/bash\\necho checking\\n[ -f logs/web.log ] || exit 1\\necho log found\\nexit 0\\n' > check.sh\nbash check.sh; echo \"status $?\"\nmv logs/web.log logs/old.log; bash check.sh; echo \"status $?\"", note='The second run stopped at the guard with status 1.'),
    [('devops', [
        dict(situation='A failing command does not stop a script by default.', cmd="printf '#!/bin/bash\\necho start\\nno_such_command\\necho \"after the error\"\\n' > e.sh\nbash e.sh; echo \"status $?\"", expect='any',
             why='Status 0, even though line 3 failed! Lesson 12.6: set -e makes the script stop at the first error.')]),
     ('qa', [
        dict(situation='Exit codes wrap at 256.', cmd="bash -c 'exit 256'; echo $?\nbash -c 'exit 300'; echo $?",
             why='Only 0–255 exist; 256 becomes 0 (success!) and 300 becomes 44. Your notes’ “255: exit status out of range” is about this.')]),
    ]
) + mistake('Write the script on Windows (Notepad), copy it, run it', 'Save with Unix (LF) line endings, or fix on Linux: sed -i \'s/\\r$//\' script.sh (or dos2unix)',
            'Every line ends with \\r\\n, so the shebang asks for “bash\\r”: “cannot execute: required file not found”. This is the puzzle.') + cmdcard_u(['first-script problems', 'scripts from Windows, the web or colleagues'],
               ['guessing: read the exact error'])(
    'errors', 'Permission denied · not found · \\r', 'first-day errors',
    'Four errors cover almost every first run: <b>Permission denied</b> (126, no x), <b>command not found</b> (127, forgot ./ or not in PATH), <b>cannot execute: required file not found</b> (127, wrong shebang path or Windows CRLF), <b>syntax error</b> (2, a typo; <code>bash -n</code> finds it).',
    'file s.sh   ·   cat -A s.sh | head -2   ·   bash -n s.sh', 'safe',
    [('file s.sh', 'shows CRLF line terminators', 'Windows files'),
     ("cat -A s.sh", '^M$ at line ends = \\r', 'see it'),
     ("sed -i 's/\\r$//'", 'remove \\r', 'fix'),
     ('head -1 s.sh', 'check the shebang', 'typos'),
     ('which bash', 'where bash really is', 'shebang path'),
     ('bash -n', 'syntax check', 'typos')],
    dict(cmd="printf '#!/bin/bash\\r\\necho hi\\r\\n' > win.sh; chmod +x win.sh\n./win.sh; echo \"exit $?\"\nfile win.sh | grep -o 'with CRLF.*'\nhead -1 win.sh | cat -A\nsed -i 's/\\r$//' win.sh; ./win.sh", expect='any', note='The \\r shows as ^M. After sed, the same file runs.'),
    [('sys', [
        dict(situation='A typo in the shebang gives the same message.', cmd="printf '#!/bin/bsh\\necho hi\\n' > typo.sh; chmod +x typo.sh\n./typo.sh; echo \"exit $?\"\nhead -1 typo.sh; command -v bash", expect='any',
             why='“not found” refers to the interpreter on line 1, not your script.')]),
    ]
) + undo('Scripts are just files; mistakes are fixed by editing and re-running.', [
    ('Edited and nothing changed:', 'check you edited the file you run: <code>type NAME</code>, <code>head -3 FILE</code>.'),
    ('Sourced a script with exit and lost the terminal:', 'open a new one; next time run it with <code>./</code>.'),
    ('Script half-ran and failed:', 'fix the cause; Lesson 12.6 shows <code>set -e</code> so it stops at the first error.'),
    ('Broke a script that worked:', 'keep scripts in Git (or at least <code>cp s.sh s.sh.bak</code> before editing).'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='./hello.sh', setup=FS + '; ' + HELLO + '; cd ~/fs', meaning='No execute permission (126).', fix='<code>chmod +x hello.sh</code> or <code>bash hello.sh</code>.'),
    dict(cmd='hello.sh', setup=FS + '; ' + HELLO + '; chmod +x ~/fs/hello.sh; cd ~/fs', meaning='The current folder is not in PATH (127).', fix='<code>./hello.sh</code>.'),
    dict(cmd='bash -n broken.sh', setup="printf 'echo \"unclosed\\n' > broken.sh", meaning='A quote is never closed (2).', fix='Close it; check again.'),
    dict(cmd='bash nofile.sh', meaning='The file name is wrong (127).', fix='<code>ls</code>; Tab-complete names.'),
]) + qc('Which status does a script return if it has no exit line?', 'The status of the last command it ran.') + '''
'''
cards = cards + '</section>\n'

def sb(k):
    o = label_box(14, 20, 150, 60, ['./hello.sh', 'line 1: #!/bin/bash', 'echo …'], 'blue', 8)
    if k >= 1:
        o += arrow(164, 50, 200, 50) + label_box(200, 20, 146, 60, ['kernel reads', 'first 2 bytes:', '“#!” → interpreter'], 'amber', 8)
    if k >= 2:
        o += label_box(14, 96, 332, 34, ['runs: /bin/bash ./hello.sh'], 'green', 8)
    if k == 3:
        o += label_box(14, 140, 332, 30, ['bash reads the file, line by line; exit status back to you'], 'violet', 7.6)
    return o
see_cmds = [['$ ./hello.sh'], ['$ ./hello.sh'], ['$ ./hello.sh'], ['$ ./hello.sh', ('Hello, Riya!', 'acc'), '$ echo $?', ('0', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/fs', prompt='riya@web01:~/fs$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['You run the file.', 'The kernel checks it…', '…starts bash with it…', '…and you get the result.'])]
behind = [sb(k) + t(180, 196, n, 8.4, 'violet', bold=True) for k, n in enumerate(['A text file with x permission.', 'Not a binary: it starts with #!.', 'The interpreter gets the file name.', 'Status 0 = success.'])]
two = anim_two('What #! does', 'Behind the screen: from file to bash',
               'A terminal running ./hello.sh and printing Hello, then $? = 0.',
               'The kernel reads the first two bytes, finds #!, starts /bin/bash with the script as its argument; bash runs the lines and returns a status.', see, behind,
               ['Run.', 'Check.', 'Start bash.', 'Result.'],
               ['execve()', '#! found', 'bash ./hello.sh', 'exit 0'])

def crlf(k):
    o = label_box(14, 22, 332, 30, ['file bytes:  # ! / b i n / b a s h \\r \\n'], 'blue', 8)
    if k >= 1:
        o += label_box(14, 64, 332, 30, ['kernel looks for program “/bin/bash\\r”'], 'amber', 8)
    if k >= 2:
        o += label_box(14, 106, 332, 30, ['no such file → “required file not found”'], 'red', 8)
    if k == 3:
        o += label_box(14, 148, 332, 30, ["sed -i 's/\\r$//' → “/bin/bash” → runs"], 'green', 8)
    return o
frames = [crlf(0) + t(180, 200, 'Saved on Windows: every line ends \\r\\n.', 8.6, 'violet', bold=True),
          crlf(1) + t(180, 200, 'The \\r becomes part of the name.', 8.6, 'violet', bold=True),
          crlf(2) + t(180, 200, 'The interpreter is “not found”.', 8.6, 'red', bold=True),
          crlf(3) + t(180, 200, 'Strip \\r: fixed.', 8.6, 'green', bold=True)]
s1 = anim_one('Animated example', 'Why a Windows script says “not found”',
              'One invisible character at the end of line 1.',
              'CRLF', 'The bytes of the first line end with \\r; the kernel looks for /bin/bash\\r, which does not exist; removing \\r fixes it.', frames,
              ['CRLF.', 'Lookup.', 'Error.', 'Fix.'], hid='scenario-crlf')

dx = dissect('Layer by layer: what makes a file runnable',
    'Each layer has a real command and output from our build machine.', [
    dict(key='text', name='Text file', sub='your commands', why='The recipe.', how='Lines.', impl='Plain text, LF.', used='Every script.',
         setup=FS + '; ' + HELLO, cmd="file ~/fs/hello.sh"),
    dict(key='mode', name='x permission', sub='chmod +x', why='May run.', how='Mode bits.', impl='Inode.', used='./script.',
         setup=FS + '; ' + HELLO, cmd="cd ~/fs; stat -c '%A %n' hello.sh; chmod +x hello.sh; stat -c '%A %n' hello.sh"),
    dict(key='shebang', name='#! line', sub='which interpreter', why='Choose the program.', how='Kernel binfmt_script.', impl='First 2 bytes.', used='bash, python.',
         setup=FS + '; ' + HELLO, cmd="head -c 11 ~/fs/hello.sh | od -c | head -1"),
    dict(key='path', name='PATH', sub='run by name', why='No ./ needed.', how='Folder list.', impl='12.1.', used='Tools.',
         cmd="echo \"$PATH\" | tr : '\\n' | head -3; grep -n 'HOME/bin' /etc/skel/.profile | head -1"),
], hint='From text to a command you can type anywhere. Click a layer.')

hd = hood('Under the hood: one execve, two programs', 'The real system call of <code>./hello.sh</code> on our build machine. The kernel starts bash for you, so you see the call for your file succeed.',
          './hello.sh', setup=FS + '; ' + HELLO + '; cd ~/fs; chmod +x hello.sh', show='execve', trace='execve')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What #! does, and the Windows line-ending trap</h2>
''' + two + s1 + dx + hd + qc('Why does <code>bash win.sh</code> (with CRLF) give <code>$\'\\r\': command not found</code> instead?', 'bash ignores the shebang, so it starts fine, but then every command ends with an invisible \\r, which becomes part of the command names and arguments.') + '''
</section>
'''

VAR = variations('More first scripts: each one adds one idea to the hello script.', [
    ('Hello, varied', [
        dict(title='Hello with the user and the time', cmd="cat > h1.sh <<'EOF'\n#!/bin/bash\necho \"Hello $USER, it is $(date +%H) o’clock on $(hostname)\"\nEOF\nbash h1.sh | sed 's/[0-9][0-9] o/HH o/'", why='Variables from the environment and command substitution.'),
        dict(title='Hello with a multi-line message', cmd="cat > h2.sh <<'EOF'\n#!/bin/bash\ncat <<MSG\nWelcome to CDAC\n  user:   $USER\n  shell:  $(basename \"$SHELL\")\nMSG\nEOF\nbash h2.sh", why='A here-document prints a block; variables still expand inside it.'),
        dict(title='Hello that refuses to run as root', cmd="cat > h3.sh <<'EOF'\n#!/bin/bash\nif [ \"$(id -u)\" -eq 0 ]; then echo 'do not run me as root' >&2; exit 1; fi\necho \"ok, running as $(whoami)\"\nEOF\nbash h3.sh; sudo bash h3.sh; echo \"status $?\"", expect='any', why='id -u is 0 for root; errors go to stderr (>&2) and exit 1.'),
    ]),
    ('Several commands in one script', [
        dict(title='A system snapshot', cmd="cat > snap.sh <<'EOF'\n#!/bin/bash\necho \"== $(date +%F) on $(hostname)\"\necho \"disk /: $(df -h / | awk 'NR==2 {print $5}') used\"\necho \"users logged in: $(who | wc -l)\"\necho \"processes: $([ \"$(ps -e --no-headers | wc -l)\" -gt 10 ] && echo 'more than 10')\"\nEOF\nbash snap.sh | sed -E 's/[0-9]+%/N%/'", why='One line per fact; awk picks the Use% column.'),
        dict(title='Create a project skeleton', cmd="cat > skel.sh <<'EOF'\n#!/bin/bash\nname=myproject\nmkdir -p \"$name\"/{src,tests,docs}\ntouch \"$name\"/README.md \"$name\"/src/main.py\necho \"created $(find \"$name\" | wc -l) items\"\nEOF\nbash skel.sh; find myproject | sort", why='Brace expansion inside a script.'),
        dict(title='Syllabus lab as a script', cmd="cat > dbda.sh <<'EOF'\n#!/bin/bash\nbase=${1:-dbda}\nmkdir -p \"$base/test\" && touch \"$base\"/test/file{1..100}\necho \"$(ls \"$base/test\" | wc -l) files in $base/test\"\nEOF\nbash dbda.sh", why='The one-line lab, made reusable with a folder argument (12.7).'),
    ]),
    ('Running variations', [
        dict(title='Same script, three ways', cmd="printf 'echo \"pid=$$ shlvl=$SHLVL\"\\n' > who.sh\nbash who.sh | sed 's/pid=[0-9]*/pid=NEW/'\nsource who.sh | sed \"s/pid=$$/pid=SAME/\"", why='bash = a new process (new PID, SHLVL+1); source = the same shell.'),
        dict(title='A Python script with a shebang', cmd="printf '#!/usr/bin/env python3\\nprint(\"hello from python\", 2 ** 10)\\n' > hi; chmod +x hi; ./hi", why='The #! line works for any interpreter.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Scripts at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['report.sh', 'daily'], 'blue', 8.6), '1. Daily reports',
              'Admins script their morning checks (disk, errors, backups) and email or post the result.', ['Write', '*cron', 'read']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['deploy.sh', 'releases'], 'green', 8.6), '2. Deployments',
    'Build, test and deploy steps live in scripts that CI runs; the exit status decides pass or fail.', ['Commit', '*./deploy.sh', 'live']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ETL', 'big data'], 'amber', 8.6), '3. Data pipelines',
    'Shell scripts glue Hive, Spark and HDFS commands together and are scheduled by cron or Airflow.', ['Extract', '*script', 'load']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['setup.sh', 'labs'], 'violet', 8.6), '4. Lab and server setup',
    'Training labs create users, folders and sample data with one script (like this course’s labs).', ['Fresh VM', '*bash setup.sh', 'ready']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['entrypoint', 'Docker'], 'red', 8.6), '5. Containers',
    'A container’s start script prepares configuration and then execs the application.', ['Start', '*entrypoint.sh', 'exec app']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Make and run', scenario='Two lines, one script.', cmd="printf '#!/bin/bash\\necho it works\\n' > s.sh && chmod +x s.sh && ./s.sh", explain='Write, chmod, run.'),
    dict(level='b', title='The syllabus lab', scenario='dbda/test with file1 … file100 in one command.', cmd="mkdir -p dbda/test && touch dbda/test/file{1..100} && ls dbda/test | wc -l && ls dbda/test | sort -V | sed -n '1p;$p'", explain='Brace expansion {1..100} (Lesson 3.4). As root: sudo mkdir -p /dbda/test && sudo touch /dbda/test/file{1..100}.'),
    dict(level='i', title='Find Windows files', scenario='Which scripts have CRLF?', cmd="printf 'a\\r\\n' > w1.sh; printf 'a\\n' > u1.sh; file *.sh | grep CRLF | cut -d: -f1", explain='file.'),
    dict(level='i', title='Scripts on the system', scenario='How many commands are scripts?', cmd="file /usr/bin/* 2>/dev/null | grep -c 'shell script' | awk '{print ($1 > 5) ? \"many\" : \"few\"}'", explain='file.'),
    dict(level='a', title='One-shot script from a here-doc', scenario='No file needed.', cmd="bash <<'EOF'\nn=$(ls /etc | wc -l)\necho \"/etc has entries: $([ $n -gt 50 ] && echo many || echo few)\"\nEOF", explain='bash reads the script from stdin.'),
], extra=build_up('the morning report', 'Riya turns her five manual commands into a script, step by step.', FS, [
    ("cd ~/fs; printf '#!/bin/bash\\n# report.sh\\nlog=logs/web.log\\n' > report.sh; cat report.sh", '1. Shebang, comment, setting.'),
    ("cd ~/fs; printf 'echo \"Report $(date +%%F)\"\\necho \"requests: $(wc -l < \"$log\")\"\\n' >> report.sh; tail -2 report.sh", '2. Add commands.'),
    ('cd ~/fs; bash -n report.sh && chmod +x report.sh && ls -l report.sh | cut -c1-10', '3. Check and make executable.'),
    ('cd ~/fs; ./report.sh | tail -1; echo "exit $?"', '4. Run it.'),
], cumulative=True)) + VAR + which('Choosing how to run.', [
    ('Your own script', './s.sh', 'Uses #!.', 'Forgetting chmod +x.'),
    ('Quick test', 'bash s.sh', 'No x needed.', 'Assuming the #! is checked.'),
    ('Load settings', 'source s.sh', 'Changes your shell.', 'exit inside it.'),
    ('A tool for daily use', '~/bin/name', 'Runs anywhere.', 'Copies everywhere.'),
    ('Script from Windows', "sed -i 's/\\r$//'", 'Fixes CRLF.', 'Retyping it.'),
    ('Check before running', 'bash -n', 'Syntax only.', 'Running unknown scripts as root.'),
]) + keys('Handy forms.', [
    ('#!/usr/bin/env bash', 'portable shebang', 'Mac + Linux'),
    ('chmod u+x s.sh', 'only you may run', 'private'),
    ('bash -n s.sh', 'syntax check', 'safety'),
    ('bash -x s.sh', 'trace lines', '12.6'),
    ('./s.sh; echo $?', 'status', 'check'),
    ('file s.sh', 'CRLF? script?', 'diagnose'),
]) + scriptit('newscript', 'A small tool that creates a new script for you: correct shebang, a header comment, Unix line endings, and execute permission. Run it with a name.',
'''name=${1:-backup-logs}   # default name if none is given
[ -e "$name" ] && { echo "$name exists, not overwriting" >&2; exit 1; }
printf '#!/bin/bash\\n# %s: describe what this script does\\n\\necho "%s is running"\\n' "$name" "$name" > "$name"
chmod +x "$name"
echo "created $name"; ./"$name"''',
'<p>Run without a name, so it uses the default backup-logs.</p>', expect='any') + puzzle_answer('The file has Windows line endings: line 1 is really <code>#!/bin/bash\\r</code>, so the kernel looks for an interpreter called <code>bash\\r</code> and reports it as not found. With <code>bash report.sh</code>, every line carries a \\r, hence the <code>$\'\\r\'</code> errors. Fix in one command: <code>sed -i \'s/\\r$//\' report.sh</code> (or <code>dos2unix report.sh</code>), and save with LF line endings in the editor next time.') + qc('What do the two characters <code>#!</code> need to be, and where?', 'The very first two bytes of the file: no space, no blank line, no BOM before them.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/fs', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../04-quoting-and-expansion-single-vs-double-quotes/">Lesson 12.4</a> (quoting) and <a href="../../09-permissions/02-chmod-symbolic-and-numeric-modes-755-644-600/">Lesson 9.2</a> (chmod).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
