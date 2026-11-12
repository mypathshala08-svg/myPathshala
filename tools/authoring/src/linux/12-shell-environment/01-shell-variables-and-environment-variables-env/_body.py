import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

SV = r"""rm -rf ~/sv; mkdir -p ~/sv/bin; cd ~/sv
printf '#!/bin/bash\necho "child sees: COURSE=[$COURSE] CITY=[$CITY]"\n' > show.sh; chmod +x show.sh
printf '#!/bin/bash\necho "backup tool v2 running"\n' > bin/backup; chmod +x bin/backup"""

HOOK = hook('Riya sets <code>DB_HOST=10.0.0.5</code> in her terminal and runs her Python app. The app says <code>DB_HOST</code> is not set. She types <code>echo $DB_HOST</code>: it is right there! On another day she copies a tool to <code>~/bin</code>, types its name, and gets “command not found”. Both problems are about <b>variables</b>: the shell keeps two kinds, <b>shell variables</b> that only the shell sees and <b>environment variables</b> that every program it starts receives. And one environment variable, <code>PATH</code>, decides where Linux looks for every command you type. Before that: which <b>shell</b> are you even talking to?',
    ['name the common Linux shells (sh, bash, dash, ksh, csh, zsh, fish), see which one you use, and change your login shell',
     'create, read, change and remove variables correctly: <code>name=value</code>, <code>$name</code>, <code>${name}</code>, <code>unset</code>, <code>readonly</code>',
     'explain shell vs environment variables, use <code>export</code>, <code>env</code>, <code>printenv</code>, <code>set</code> and <code>declare -p</code>, and pass a variable to one command only',
     'understand and safely change <code>PATH</code>, and know the important built-in variables (HOME, USER, SHELL, PWD, PS1, $?, $$, RANDOM)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the app cannot see it'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'Shells and variables', 7, 'simple meaning + 4 depths'),
    ('types', 'Kinds of shells and variables', 5, 'side by side'),
    ('commands', 'Variables by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'export to a child'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'set up an environment'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('Which shell am I using?', 'echo $0   ·   ps -p $$', '$SHELL = login shell'),
    ('Which shells are installed?', 'cat /etc/shells', 'chsh -s to change'),
    ('Make a variable', 'name=value', 'no spaces around ='),
    ('Let programs see it', 'export name=value', 'environment variable'),
    ('For one command only', 'name=value command', 'nothing left behind'),
    ('See exported variables', 'env   ·   printenv NAME', 'environment only'),
    ('See every variable', 'set   ·   declare -p NAME', 'shell + environment'),
    ('Run my own tools by name', 'export PATH="$HOME/bin:$PATH"', 'keep the old PATH!'),
])

cmap = concept_map(
    [('1.6', 'Terminal and shell', 'the prompt'), ('11.1', 'Processes', 'parent and child'), ('5.4', 'Exit status', '$?')],
    ['types of shells: sh, bash, dash, ksh, csh, zsh, fish', 'variables: name=value, $name, ${name}, unset, readonly', 'shell vs environment variables, export, env, set', 'one-command variables: VAR=x cmd', 'PATH and the important built-in variables'],
    [('12.2', 'Startup files', 'make it permanent'), ('12.4', 'Quoting', '"$var" vs \'$var\''), ('12.7', 'Script input', '$1, $#, read'), ('12.5', 'First script', 'shebang')],
    'The shell keeps variables; export copies them into the environment that every child process receives. PATH tells the shell where to find commands.')

sc = (term(20, 14, 316, 156, ['$ DB_HOST=10.0.0.5', '$ echo $DB_HOST', ('10.0.0.5', 'out'), '$ python3 app.py', ('error: DB_HOST not set', 'err'), '$ export DB_HOST', '$ python3 app.py', ('connected to 10.0.0.5', 'acc')], title='riya@web01: ~/app', prompt='riya@web01:~/app$', size=6.8, step=15)
      + t(352, 36, 'Two kinds of variable:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• shell variable:', '  only this shell', '• environment variable:', '  copied to every child', '• export = promote it'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The variable the app could not see</h2>
  <div class="story">
''' + puzzle('Riya adds this line to her terminal: <code>PATH=~/bin</code>, so that her tool <code>~/bin/backup</code> runs by name. It works: <code>backup</code> runs. But now <code>ls</code>, <code>cat</code> and <code>nano</code> all say “command not found”. What happened, how does she fix the open terminal right now, and what should she have typed?') + '''
    <p class="narration">Riya sets a variable, but her program cannot see it until she exports it.</p>
''' + scene('A terminal: a variable is set and echo shows it, but a Python app says it is not set; after export the app connects.', sc,
            '<tspan font-weight="700" class="s-acc">export</tspan> copies a variable into the environment of every program you start.') + '''
K> But echo showed it. Why could the app not see it?
A> echo is part of the shell, so it sees the shell’s own variables. <code>python3</code> is a separate <b>child process</b> (Lesson 11.1). A child gets a copy of the parent’s <b>environment</b> only, and a plain <code>DB_HOST=…</code> lives in the shell, not in the environment. <code>export</code> moves it there.
R> And PATH?
A> PATH is an environment variable that lists folders, separated by colons. When you type <code>ls</code>, the shell searches those folders in order. Today you will see exactly how, and how to change it without breaking everything.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A shell as an office desk: notes on the desk are shell variables; a folder of copies handed to every helper is the environment; export moves a note into the folder.">'
       + label_box(14, 20, 190, 110, ['shell variables', 'notes on YOUR desk', 'city=Pune', '(only you see them)'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['export', 'put a copy in the', 'folder you hand', 'to every helper'], 'amber', 8.6)
       + label_box(434, 20, 192, 110, ['environment', 'the folder: HOME,', 'PATH, USER, DB_HOST', '(children get a copy)'], 'green', 8.6)
       + t(320, 160, 'A child gets a COPY: changes in the child never come back.', 9.6, 'ink2')
       + t(320, 182, 'PATH = the list of folders searched for commands.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Shells and variables at four depths', [
    ('v', 'No jargon: notes and a folder of copies', '      <p>Your shell is a desk with notes; programs it starts get a folder of copies.</p>' + pic),
    ('b', 'What you will type every day', '''      <ul>
        <li><code>name=Riya</code> makes a variable (no spaces around <code>=</code>); <code>echo "$name"</code> reads it.</li>
        <li><code>export name</code> (or <code>export name=Riya</code>) lets programs you start see it.</li>
        <li><code>env</code> or <code>printenv</code> lists the environment; <code>echo $PATH</code> shows where commands are searched.</li>
        <li><code>unset name</code> removes a variable. <code>echo $0</code> shows which shell you are in.</li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li>Names: letters, digits, <code>_</code>; not starting with a digit; case-sensitive (<code>name</code> ≠ <code>NAME</code>). Convention: UPPERCASE for environment variables, lowercase for your own.</li>
        <li>All values are strings. <code>${name}</code> marks where the name ends: <code>"${file}_old"</code>.</li>
        <li><code>VAR=value command</code> puts VAR into the environment of that one command only.</li>
        <li>A child can never change its parent’s variables: <code>export</code> copies downwards only. To change your current shell, use <code>source</code> (Lesson 11.1).</li>
        <li><code>readonly</code> variables cannot be changed or unset until the shell exits.</li>
      </ul>'''),
    ('a', 'Behind the screen: the environment block', '''      <ul>
        <li>The environment is an array of <code>NAME=value</code> strings passed by <code>execve()</code> to every new program; read it for any process in <code>/proc/PID/environ</code>.</li>
        <li>bash keeps attributes per variable: exported (<code>-x</code>), readonly (<code>-r</code>), integer (<code>-i</code>), array (<code>-a</code>, <code>-A</code>); <code>declare -p</code> shows them.</li>
        <li>Command lookup order: alias → shell keyword → function → builtin → a hash table of remembered paths → search each <code>PATH</code> folder left to right. <code>hash -r</code> forgets remembered paths.</li>
        <li>An empty entry in PATH (<code>::</code> or a trailing <code>:</code>) means “the current folder”: a security risk.</li>
        <li><code>/bin/sh</code> on Ubuntu is <b>dash</b> (small, fast, POSIX only); on RHEL it is bash in POSIX mode. Scripts with <code>#!/bin/sh</code> must not use bash-only features.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Shells, shell variables and environment variables</h2>
''' + def_block(
    'A <b>shell</b> is a command-line interpreter: it reads commands, expands them and starts programs. A <b>shell variable</b> is a named string stored inside the running shell. An <b>environment variable</b> is a variable that has been <b>exported</b>: it is part of the environment that the shell passes to every child process it starts. <code>PATH</code> is the environment variable that lists the directories searched for commands.',
    'Shell variable = only this shell. Environment variable = this shell and every program it starts.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Shell', 'The program that reads your commands (bash).'),
    ('Login shell', 'Your default shell, from /etc/passwd ($SHELL).'),
    ('Variable', 'name=value, read with $name.'),
    ('Environment', 'Exported variables passed to children.'),
    ('export', 'Make a variable an environment variable.'),
    ('PATH', 'Folders searched for commands, : separated.'),
    ('readonly', 'A variable that cannot change.'),
    ('Special variables', '$?, $$, $0, $#, $1… set by the shell.'),
]) + '\n' + names('Where the names come from.', [
    ('sh', 'shell', 'Bourne shell, 1977.'),
    ('bash', 'Bourne-Again SHell', 'GNU, 1989.'),
    ('dash', 'Debian Almquist shell', 'Ubuntu’s /bin/sh.'),
    ('ksh', 'Korn shell', 'David Korn, 1983.'),
    ('csh', 'C shell', 'C-like syntax, 1978.'),
    ('zsh', 'Z shell', 'macOS default.'),
    ('env', 'environment', 'List or set environment.'),
    ('PS1', 'prompt string 1', 'Your prompt.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Make', '<code>name=value</code>'),
    ('Read', '<code>"$name"</code> / <code>"${name}"</code>'),
    ('Export', '<code>export name</code>'),
    ('Remove', '<code>unset name</code>'),
    ('List env', '<code>env</code> / <code>printenv</code>'),
    ('Command path', '<code>echo $PATH</code>'),
]) + '\n' + lv + didyou('<code>cd</code>, <code>export</code> and <code>read</code> must be shell builtins for the same reason: they change the shell itself. If <code>export</code> were a separate program, it would only change its own copy and then exit.') + '''
EXAM> “Difference between a shell variable and an environment variable?” → A shell variable exists only in the current shell; an environment variable (exported) is also passed to every child process.
''' + qc('After <code>x=5</code>, which shows it: <code>env</code>, <code>set</code> or both?', 'Only <code>set</code> (and declare -p x). env shows exported variables only; after export x, both.') + mistake('num= 20   ·   num = 20',
    'num=20',
    'No spaces around =. “num= 20” sets num to empty for one command and runs a command called 20 (exit 127). “num = 20” runs a command called num.') + mistake('readonly MY_VAR=10; unset MY_VAR   (to “come out of read-only mode”)',
    'There is no way back: a readonly variable lasts until the shell exits. Use readonly only for real constants.',
    'Checked on our build machine: unset prints “cannot unset: readonly variable” and exits 1; assigning prints “readonly variable”.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Kinds of shells, and kinds of variables</h2>
''' + table(['Shell', 'Path', 'Known for', 'Where you meet it'], [
    ['sh (Bourne)', '/bin/sh', 'the original 1977 shell; POSIX standard', 'portable scripts'],
    ['bash', '/bin/bash', 'sh + arrays, [[ ]], history, completion', 'default on most Linux'],
    ['dash', '/usr/bin/dash', 'tiny, fast, POSIX only', '/bin/sh on Ubuntu/Debian'],
    ['ksh (Korn)', '/bin/ksh', 'sh + C-shell ideas, fast scripts', 'AIX, Solaris, banks'],
    ['csh / tcsh', '/bin/csh', 'C-like syntax (setenv, foreach)', 'BSD, old universities'],
    ['zsh', '/bin/zsh', 'bash-like, powerful completion, themes', 'macOS default, oh-my-zsh'],
    ['fish', '/usr/bin/fish', 'friendly, not POSIX', 'desktop users'],
], minw=560) + table(['', 'Shell variable', 'Environment variable', 'Special variable'], [
    ['Created by', '<code>name=value</code>', '<code>export name=value</code>', 'the shell'],
    ['Seen by child programs', 'no', 'yes (a copy)', '—'],
    ['Listed by', '<code>set</code>, <code>declare -p</code>', '<code>env</code>, <code>printenv</code>, <code>set</code>', '<code>echo $?</code> etc.'],
    ['Examples', 'count, file, i', 'HOME, PATH, USER, LANG, JAVA_HOME', '$?, $$, $!, $0, $1, $#, $@'],
    ['Lifetime', 'until the shell exits', 'shell + its children', 'changes all the time'],
], minw=560) + table(['Variable', 'Meaning'], [
    ['<code>HOME</code>', 'your home folder'],
    ['<code>USER</code> / <code>LOGNAME</code>', 'your user name'],
    ['<code>SHELL</code>', 'your login shell (not always the current one)'],
    ['<code>PWD</code> / <code>OLDPWD</code>', 'current / previous folder'],
    ['<code>PATH</code>', 'command search folders'],
    ['<code>PS1</code>', 'the prompt'],
    ['<code>LANG</code>', 'language and character set'],
    ['<code>HOSTNAME</code>', 'machine name (bash)'],
    ['<code>RANDOM</code>', 'a random 0–32767'],
    ['<code>SECONDS</code>', 'seconds since the shell started'],
], minw=380) + qc('<code>echo $SHELL</code> says /bin/bash, but you typed <code>dash</code>. What does <code>echo $0</code> say?', '<code>dash</code>. $SHELL is your login shell from /etc/passwd; $0 (or ps -p $$) is the shell running now.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Shells and variables, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as user riya, in a folder <code>~/sv</code> with a script <code>show.sh</code> (prints COURSE and CITY as a child sees them) and a tool <code>bin/backup</code>. Only bash and dash are installed there, so outputs of other shells are marked typical.</p>
''' + cmdcard_u(['knowing which shell runs your commands', 'checking scripts for bash-only features', 'changing your login shell'],
               ['chsh to a shell that is not in /etc/shells'])(
    'shells', 'echo $0 · /etc/shells · chsh', 'which shell?',
    '<code>$0</code> (or <code>ps -p $$</code>) is the running shell; <code>$SHELL</code> is your login shell from /etc/passwd; <code>/etc/shells</code> lists allowed login shells; <code>chsh -s PATH</code> changes yours (log in again to see it).',
    'echo $0   ·   cat /etc/shells   ·   chsh -s /bin/zsh', 'change',
    [('echo $0', 'running shell', 'now'),
     ('echo $SHELL', 'login shell', 'default'),
     ('ps -p $$', 'reliable check', 'scripts'),
     ('cat /etc/shells', 'allowed shells', 'before chsh'),
     ('chsh -s SHELL', 'change login shell', 'own account'),
     ('sudo usermod -s', 'for another user', 'admin')],
    dict(cmd="echo \"running: $(ps -o comm= -p $$)   login: $SHELL\"\ngrep -v '^#' /etc/shells\nreadlink -f /bin/sh", note='/bin/sh is dash on Ubuntu. (tmux appears because it was installed as a login shell option.)'),
    [('dev', [
        dict(situation='A bash-only script run with sh goes wrong silently.', cmd="printf 'if [[ 5 -gt 3 ]]; then echo bigger; fi\\n' > t.sh\nbash t.sh\nsh t.sh; echo \"exit $?\"", expect='any',
             why='[[ ]] is bash, not POSIX, and Ubuntu’s sh is dash. dash prints “[[: not found”, treats the if as false and still exits 0: the bug is silent. Use #!/bin/bash for bash scripts and run them with bash or ./script.')]),
     ('sys', [
        dict(situation='The syllabus lab: give a user the nologin shell.', setup="sudo userdel -r user3 2>/dev/null; sudo useradd -m user3", cmd="sudo usermod -s /usr/sbin/nologin user3\ngrep '^user3:' /etc/passwd | cut -d: -f1,7\nsudo su - user3 -c whoami; echo \"exit $?\"\nsudo userdel -r user3 2>/dev/null", expect='any',
             why='nologin refuses any interactive shell: “This account is currently not available.” Used for service accounts (www-data). Lesson 8.2 covers usermod.')]),
    ],
    anat=anatomy([('chsh', 'cmd', 'change shell'), ('-s', 'opt', 'new shell'), ('/bin/zsh', 'arg', 'from /etc/shells')], 'Takes effect at the next login.')
) + cmdcard_u(['storing values in the terminal and in scripts', 'building file names', 'constants'],
               ['spaces around =', 'unquoted $var with spaces inside'])(
    'vars', 'name=value · $name · unset · readonly', 'shell variables',
    'Assign with <code>name=value</code> (no spaces; quote values with spaces). Read with <code>$name</code> or <code>${name}</code>; always put it in double quotes. <code>unset name</code> removes it; <code>readonly name=value</code> fixes it forever (for this shell).',
    'name=value   ·   echo "${name}"   ·   unset name   ·   readonly NAME=value', 'safe',
    [('name=value', 'assign', 'no spaces'),
     ('name="two words"', 'value with spaces', 'quote it'),
     ('"$name"', 'read safely', 'always quote'),
     ('"${name}_x"', 'name ends here', 'joining text'),
     ('unset name', 'remove', 'clean up'),
     ('readonly N=1', 'constant', 'cannot change')],
    dict(cmd="course=Linux; city='New Delhi'\necho \"$course in $city\"\nfile=report; echo \"${file}_2026.txt  vs  $file_2026.txt\"\nunset city; echo \"city is now [$city]\"", note='$file_2026 is read as the variable file_2026, which does not exist (empty). Braces mark the end of the name.'),
    [('qa', [
        dict(situation='Your notes’ “num= 20”: the space matters.', cmd="num= 20; echo \"exit $? num=[$num]\"\nnum = 20; echo \"exit $?\"\nnum=20; echo \"num=[$num]\"", expect='any',
             why='Only the last form assigns. The first two try to run a command (20, num).')]),
     ('sec', [
        dict(situation='readonly cannot be undone.', cmd="readonly MAX_USERS=10\nMAX_USERS=20; echo \"exit $?\"\nunset MAX_USERS; echo \"exit $?\"; echo \"still $MAX_USERS\"", expect='any',
             why='Good for constants in scripts. To get rid of it you must start a new shell.')]),
    ],
) + mistake('PATH=~/bin   ·   PATH=$HOME/bin', 'export PATH="$HOME/bin:$PATH"',
            'Without :$PATH the old folders are gone, so ls, cat and nano are “not found”. Always add to the old value.') + cmdcard_u(['letting programs see settings (DB_HOST, JAVA_HOME, EDITOR)', 'configuring tools'],
               ['exporting secrets in shared shells (other users cannot see them, but your child programs and logs can)'])(
    'export', 'export · env · printenv · set', 'environment variables',
    '<code>export NAME</code> marks a variable for the environment; <code>export NAME=value</code> does both at once; <code>export -n NAME</code> un-exports. <code>env</code> and <code>printenv</code> list the environment; <code>printenv NAME</code> prints one; <code>set</code> and <code>declare -p</code> show all variables.',
    'export NAME[=value]   ·   env   ·   printenv NAME   ·   declare -p NAME', 'safe',
    [('export N=v', 'set + export', 'one step'),
     ('export N', 'export existing', 'after testing'),
     ('export -n N', 'un-export', 'keep in shell'),
     ('env / printenv', 'list environment', 'what children get'),
     ('printenv N', 'one value', 'scripts'),
     ('declare -p N', 'value + attributes', 'debugging')],
    dict(setup=SV, cmd="cd ~/sv\nCOURSE=Linux; CITY=Pune\n./show.sh\nexport COURSE\n./show.sh\ndeclare -p COURSE CITY", note='-x in declare means exported. Only COURSE reached the child.'),
    [('dev', [
        dict(situation='Which list shows what?', cmd="mine=1; export shared=2\nenv | grep -E '^(mine|shared)='\nset | grep -E '^(mine|shared)='",
             why='env = environment only; set = every variable of the shell.')]),
     ('devops', [
        dict(situation='A child cannot change the parent.', setup=SV, cmd="cd ~/sv; export CITY=Pune\nbash -c 'CITY=Mumbai; export CITY; echo \"child: $CITY\"'\necho \"parent: $CITY\"",
             why='The child changed its own copy. To load settings into your shell, source a file (Lesson 12.2).')]),
    ]
) + cmdcard_u(['one-off settings for one command', 'testing', 'cron and CI jobs'],
               ['expecting the variable to remain afterwards'])(
    'oneshot', 'VAR=value command · env -i', 'for one command only',
    'Writing assignments before a command puts them into that command’s environment only. <code>env VAR=value cmd</code> does the same, <code>env -u VAR cmd</code> removes one, <code>env -i cmd</code> starts with an empty environment.',
    'VAR=value [VAR2=value] command   ·   env -i PATH=/usr/bin command', 'safe',
    [('LANG=C sort f', 'byte-order sort', 'predictable'),
     ('TZ=Asia/Tokyo date', 'another time zone', 'one command'),
     ('DEBUG=1 ./app', 'switch on debug', 'testing'),
     ('env -u VAR cmd', 'without VAR', 'testing'),
     ('env -i cmd', 'empty environment', 'clean runs')],
    dict(setup=SV, cmd="cd ~/sv\nCOURSE=Bash CITY=Goa ./show.sh\necho \"afterwards: COURSE=[$COURSE]\"\nTZ=Asia/Tokyo date +%H:%M | wc -c; TZ=UTC date +%Z", note='The values existed only for show.sh.'),
    [('sys', [
        dict(situation='Debug a program with a clean environment.', setup=SV, cmd="cd ~/sv; export COURSE=Linux\nenv -i PATH=/usr/bin:/bin ./show.sh\nenv -i /usr/bin/env | wc -l",
             why='env -i removes everything: many “works for me, fails in cron” bugs are environment differences (cron has a tiny environment).')]),
    ]
) + cmdcard_u(['running your own scripts and tools by name', 'choosing between two versions of a tool'],
               ['adding . or an empty entry to PATH', 'PATH=newdir without :$PATH'])(
    'path', 'PATH · type -a · hash', 'where commands are found',
    '<code>PATH</code> is a colon-separated list of folders. The shell looks in each, left to right, and runs the first match. Add a folder in front (<code>"$HOME/bin:$PATH"</code>) to prefer it, or at the end to use it last. <code>type -a cmd</code> shows every match; <code>hash -r</code> forgets remembered locations.',
    'export PATH="$HOME/bin:$PATH"   ·   type -a CMD', 'change',
    [('echo $PATH', 'show folders', 'check'),
     ('tr : \\\\n <<< $PATH', 'one per line', 'readable'),
     ('PATH="D:$PATH"', 'search D first', 'override'),
     ('PATH="$PATH:D"', 'search D last', 'add tools'),
     ('type -a CMD', 'all matches', 'which one runs'),
     ('hash -r', 'forget cached paths', 'after moving tools')],
    dict(setup=SV, cmd="cd ~/sv\necho \"$PATH\" | tr : '\\n'\nbackup; echo \"exit $?\"\nexport PATH=\"$HOME/sv/bin:$PATH\"\nbackup; type backup", expect='any', note='Not found until its folder is in PATH (exit 127); then found in ~/sv/bin.'),
    [('sec', [
        dict(situation='The puzzle: PATH without :$PATH breaks everything.', setup=SV, cmd="cd ~/sv; old=\"$PATH\"\nPATH=~/sv/bin\nbackup; ls; echo \"exit $?\"\nPATH=\"$old\"; ls | head -2", expect='any',
             why='Fix in the open terminal: restore it (here from old) or type the full path /usr/bin/ls; or simply open a new terminal.')]),
    ]
) + undo('Variables live in memory; a new terminal undoes almost everything.', [
    ('Broke PATH:', '<code>export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin</code>, or open a new terminal; then fix the line in ~/.bashrc.'),
    ('Exported something by mistake:', '<code>export -n NAME</code> or <code>unset NAME</code>.'),
    ('readonly by mistake:', 'start a new shell (exit and reopen).'),
    ('chsh to a wrong shell:', 'as root: <code>usermod -s /bin/bash USER</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='num = 20', meaning='Spaces: the shell runs a command called num.', fix='<code>num=20</code>.'),
    dict(cmd='2name=x', meaning='Names cannot start with a digit: run as a command.', fix='<code>name2=x</code>.'),
    dict(cmd='readonly R=1; R=2', meaning='Cannot change a readonly variable.', fix='Use a normal variable.'),
    dict(cmd='mytool', meaning='Not in any PATH folder (exit 127).', fix='Add its folder to PATH or run <code>./mytool</code>.'),
]) + qc('Why does <code>echo $USER</code> work in every program, but your <code>count=3</code> does not?', 'USER is in the environment (set at login and exported); count is only a shell variable until you export it.') + '''
'''

cards = cards + '</section>\n'

def fam(k):
    par = label_box(14, 20, 140, 80, ['parent shell', 'COURSE=Linux', 'CITY=Pune' + (' (exported)' if k >= 2 else ''), 'x: COURSE' if k >= 1 else ''], 'blue', 8)
    o = par
    if k >= 1:
        envv = ['COURSE=Linux'] + (['CITY=Pune'] if k >= 2 else [])
        o += arrow(154, 60, 200, 60) + label_box(200, 20, 146, 80, ['child (show.sh)', 'gets a COPY:'] + envv, 'green', 8)
    if k == 3:
        o += label_box(200, 108, 146, 34, ['child sets CITY=Goa'], 'amber', 8) + t(90, 126, 'parent still Pune', 8.4, 'red', bold=True)
    return o
see_cmds = [['$ COURSE=Linux; CITY=Pune'], ['$ export COURSE', '$ ./show.sh', ('COURSE=[Linux] CITY=[]', 'out')], ['$ export CITY', '$ ./show.sh', ('COURSE=[Linux] CITY=[Pune]', 'out')], ["$ bash -c 'CITY=Goa'", '$ echo $CITY', ('Pune', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/sv', prompt='riya@web01:~/sv$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Two shell variables.', 'Only COURSE is exported.', 'Now both.', 'Copies never flow back.'])]
behind = [fam(k) + t(180, 175, n, 8.4, 'violet', bold=True) for k, n in enumerate(['Both live only in the shell.', 'fork + exec: the environment is copied.', 'CITY joins the environment.', 'The child’s change dies with it.'])]
two = anim_two('export to a child', 'Behind the screen: what a child receives',
               'A terminal: two variables, export one, run a child, export the other, a child changes one.',
               'A parent shell box and a child box; exported variables are copied into the child; changes in the child do not reach the parent.', see, behind,
               ['Set.', 'Export one.', 'Export two.', 'One way.'],
               ['shell only', 'copied down', 'both copied', 'never up'])

def pth(k):
    dirs = ['~/sv/bin', '/usr/local/bin', '/usr/bin', '/bin']
    o = ''
    for i, d in enumerate(dirs):
        tn = 'card'
        if k == 1 and i == 0: tn = 'red'
        if k == 1 and i == 1: tn = 'red'
        if k == 1 and i == 2: tn = 'green'
        if k == 2 and i == 0: tn = 'green'
        if k == 3: tn = 'green' if i == 0 else 'card'
        lines = [d, ['', 'ls? no', 'ls? YES', ''][i] if k == 1 else ('backup? YES' if (k >= 2 and i == 0) else '')]
        o += label_box(14 + i * 86, 30, 80, 44, lines, tn, 7.4)
    return o
frames = [pth(0) + t(180, 110, 'PATH = four folders, searched left to right.', 8.6, 'violet', bold=True),
          pth(1) + t(180, 110, 'ls: not in 1, not in 2, found in /usr/bin.', 8.6, 'green', bold=True),
          pth(2) + t(180, 110, 'backup: found in the first folder.', 8.6, 'green', bold=True),
          pth(3) + t(180, 110, 'First match wins: put your folder first to override.', 8.6, 'acc', bold=True)]
s1 = anim_one('Animated example', 'How the shell finds a command in PATH',
              'Folders searched in order; the first match runs.',
              'PATH search', 'Four PATH folder boxes searched left to right: ls is found in /usr/bin, backup in the first folder.', frames,
              ['PATH.', 'ls.', 'backup.', 'First wins.'], hid='scenario-path')

dx = dissect('Layer by layer: where a variable lives',
    'Each layer has a real command and output from our build machine.', [
    dict(key='shell', name='Shell variable', sub='inside bash', why='Quick storage.', how='name=value.', impl='bash’s variable table.', used='Scripts.',
         cmd="secret=42; declare -p secret; bash -c 'echo \"child: [$secret]\"'"),
    dict(key='env', name='Environment', sub='exported', why='For children.', how='export.', impl='Passed by execve().', used='Config.',
         cmd="export APP_MODE=prod; sleep 5 & sleep 0.2; tr '\\0' '\\n' < /proc/$!/environ | grep APP_MODE; kill $!"),
    dict(key='path', name='PATH lookup', sub='finding programs', why='Run by name.', how='Left to right.', impl='Hash table cache.', used='Every command.',
         cmd="type -a ls; hash -r; ls > /dev/null; hash | tail -1"),
    dict(key='login', name='Login shell', sub='/etc/passwd', why='Which shell at login.', how='7th field.', impl='$SHELL.', used='chsh.',
         cmd="getent passwd riya | cut -d: -f1,7; echo \"$SHELL\""),
], hint='From your shell’s memory to the next login. Click a layer.')

hd = hood('Under the hood: the environment travels inside execve()', 'The real system call when bash starts a child with one extra variable: <code>MODE=test ./show.sh</code>. Look at the third argument: the environment array.',
          "bash -c 'MODE=test ./show.sh'", setup=SV + '; cd ~/sv', show='execve\\("\\./show', trace='execve')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>export to a child, and the PATH search</h2>
''' + two + s1 + dx + hd + qc('Why does a variable set in a script disappear when the script ends?', 'The script ran in a child process; its variables die with it. Use source to run it in your shell.') + '''
</section>
'''

VAR = variations('Each snippet changes one thing about the examples above, so you can see the rule from several sides. All were really run on our build machine.', [
    ('Creating and reading variables', [
        dict(title='Numbers are strings too', cmd="a=5; b=10\necho \"$a$b\"        # joined as text\necho $((a + b))    # arithmetic needs $(( ))", why='Every value is a string; arithmetic is explicit (Lesson 12.7).'),
        dict(title='Command output into a variable', cmd="today=$(date +%F)\nfiles=$(ls /etc | wc -l)\necho \"On $today, /etc has $([ \"$files\" -gt 50 ] && echo many || echo few) entries\"", why='$( ) stores the output of a command; the date changes each day.'),
        dict(title='Append to a variable', cmd="list=apples\nlist+=\",mangoes\"\nlist=\"$list,grapes\"\necho \"$list\"", why='+= appends; or rebuild it with the old value inside.'),
        dict(title='Default, alternative and length', cmd="unset city\necho \"${city:-Pune}\"     # default when empty\ncity=Delhi\necho \"${city:+set}\"      # alternative when set\necho \"${#city} letters\"", why='${v:-x}, ${v:+x} and ${#v}: three of the most used expansions.'),
    ]),
    ('Shell vs environment variables', [
        dict(title='export with and without a value', cmd="A=1; export A\nexport B=2\nbash -c 'echo \"child sees A=$A B=$B\"'", why='Both forms export; the second sets and exports in one step.'),
        dict(title='Un-export but keep the value', cmd="export C=3\nexport -n C\nbash -c 'echo \"child: [$C]\"'; echo \"parent: $C\"", why='export -n turns it back into a shell variable.'),
        dict(title='Several variables for one command', cmd="LANG=C TZ=UTC bash -c 'echo \"$LANG $TZ\"'\necho \"after: [$TZ]\"", why='Any number of NAME=value before a command, for that command only.'),
        dict(title='printenv vs echo', cmd="export SHOWN=yes; hidden=no\nprintenv SHOWN; printenv hidden || echo 'hidden is not in the environment'", why='printenv only knows the environment; echo knows all shell variables.'),
    ]),
    ('PATH variations', [
        dict(title='Prepend vs append', setup="mkdir -p ~/v1/a ~/v1/b; printf '#!/bin/sh\\necho from a\\n' > ~/v1/a/tool; printf '#!/bin/sh\\necho from b\\n' > ~/v1/b/tool; chmod +x ~/v1/a/tool ~/v1/b/tool", cmd="PATH=\"$HOME/v1/a:$HOME/v1/b:$PATH\" tool\nPATH=\"$HOME/v1/b:$HOME/v1/a:$PATH\" tool", why='The first folder in PATH wins.'),
        dict(title='Add only if missing', cmd="d=/opt/demo/bin\ncase \":$PATH:\" in *\":$d:\"*) ;; *) PATH=\"$PATH:$d\";; esac\ncase \":$PATH:\" in *\":$d:\"*) ;; *) PATH=\"$PATH:$d\";; esac\necho \"$PATH\" | tr : '\\n' | grep -c demo", why='Running the same line twice adds it once: safe in .bashrc.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Variables at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['DB_HOST', 'APP_ENV'], 'blue', 8.6), '1. App configuration',
              'Twelve-factor apps read settings (database, mode, keys) from environment variables, not config files.', ['Set', '*export', 'run']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['JAVA_HOME', 'SPARK_HOME'], 'green', 8.6), '2. Big data tools',
    'Hadoop, Spark and Kafka need JAVA_HOME and their own *_HOME plus PATH entries.', ['Install', '*export PATH', 'use']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['-e VAR', 'containers'], 'amber', 8.6), '3. Docker and Kubernetes',
    'Containers receive their configuration as environment variables (docker run -e, env: in Kubernetes).', ['Image', '*-e', 'container']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['secrets', 'CI'], 'red', 8.6), '4. CI/CD pipelines',
    'Pipelines inject tokens as masked environment variables for one job only.', ['Store', '*VAR=x cmd', 'mask']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['nologin', 'accounts'], 'violet', 8.6), '5. Service accounts',
    'Accounts like www-data and mysql get /usr/sbin/nologin so nobody can log in as them.', ['Create', '*usermod -s', 'safe']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Which shell?', scenario='Am I in bash?', cmd="ps -o comm= -p $$", explain='Reliable.'),
    dict(level='b', title='PATH one per line', scenario='Readable PATH.', cmd="echo \"$PATH\" | tr : '\\n'", explain='tr.'),
    dict(level='i', title='Is it exported?', scenario='Check a variable.', cmd="X=1; export Y=2; declare -p X Y", explain='-x = exported.'),
    dict(level='i', title='Count environment', scenario='How big is it?', cmd="env | wc -l | awk '{print ($1 > 3) ? \"several variables\" : \"few\"}'", explain='env | wc.'),
    dict(level='a', title='Another process’s environment', scenario='What did that program get?', cmd="export TOKEN_ID=abc; sleep 3 & sleep 0.1; tr '\\0' '\\n' < /proc/$!/environ | grep -c TOKEN_ID; kill $!", explain='/proc/PID/environ (only your own processes, or root).'),
], extra=build_up('a big-data tool environment', 'Riya prepares the variables a Spark-like tool needs, step by step.', SV, [
    ("export TOOL_HOME=$HOME/sv; echo \"$TOOL_HOME\"", '1. The tool’s home folder.'),
    ('export PATH="$TOOL_HOME/bin:$PATH"; type backup', '2. Its bin folder first in PATH.'),
    ('cd ~/sv; COURSE=bigdata ./show.sh', '3. A one-off setting for one run.'),
    ("declare -p TOOL_HOME | cut -c1-12", '4. Check: exported (-x).'),
], cumulative=True)) + VAR + which('Choosing the right form.', [
    ('Store a value', 'name=value', 'No spaces.', 'name = value.'),
    ('Programs must see it', 'export NAME=value', 'Environment.', 'Forgetting export.'),
    ('One command only', 'VAR=v cmd', 'Nothing left over.', 'export then forget to unset.'),
    ('Add a tool folder', 'PATH="D:$PATH"', 'Keeps old folders.', 'PATH=D.'),
    ('List what children get', 'env / printenv', 'Exact.', 'set (too much).'),
    ('Which shell now', 'ps -p $$', 'Running shell.', '$SHELL (login shell).'),
]) + keys('Handy forms.', [
    ('"${var}"', 'safe read', 'always'),
    ('export -p', 'all exported', 'audit'),
    ('printenv HOME', 'one value', 'scripts'),
    ('env -i cmd', 'empty env', 'clean test'),
    ('type -a cmd', 'all PATH matches', 'which runs'),
    ('chsh -s /bin/bash', 'login shell', 'own user'),
]) + scriptit('envcheck.sh', 'A start-up check for an application: required variables must be set and exported, and PATH must not contain an empty entry or a dot.',
'''missing=0
for v in HOME USER APP_ENV DB_HOST; do
  if ! printenv "$v" > /dev/null; then echo "MISSING: $v"; missing=1; fi
done
case ":$PATH:" in *::*|*:.:*) echo "UNSAFE PATH: contains . or empty entry";; *) echo "PATH ok";; esac
exit $missing''',
'<p>Run with only APP_ENV exported, so DB_HOST is reported.</p>', expect='any') + puzzle_answer('<code>PATH=~/bin</code> <b>replaced</b> the whole list, so the shell only looks in ~/bin: backup is found, ls is not. Fix the open terminal: <code>export PATH=/usr/local/bin:/usr/bin:/bin</code> (or open a new terminal). The right line: <code>export PATH="$HOME/bin:$PATH"</code>, saved in ~/.bashrc to keep it (Lesson 12.2).') + qc('What does <code>env -i bash</code> give you?', 'A bash with an (almost) empty environment: no HOME, PATH defaults only. Useful to test scripts the way cron runs them.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/sv ~/t.sh; sudo userdel -r user3 2>/dev/null; true', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../01-start-here/06-terminal-console-shell-and-prompt-your-first/">Lesson 1.6</a> (shell and prompt) and <a href="../../11-processes/01-what-is-a-process-pid-ppid-fork-exec/">Lesson 11.1</a> (parent and child processes).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
