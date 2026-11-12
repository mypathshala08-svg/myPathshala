import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='01-shell-variables-and-environment-variables-env', n='12.1',
    module_label='Module 12 · The shell environment and shell programming',
    title='Shell variables and environment variables: env, export and PATH',
    desc='Types of Linux shells (sh, bash, dash, ksh, csh, zsh, fish), $0 vs $SHELL, /etc/shells, chsh and nologin; user-defined variables (name=value, ${name}, unset, readonly, naming rules); shell vs environment variables, export, env, printenv, set, declare -p; VAR=value command and env -i; PATH and command lookup; important built-in variables; real outputs, mistakes from class notes checked, animations.',
    og_desc='Linux shells and variables: shell vs environment variables, export, env and PATH explained with real outputs and animations.',
    minutes=40, level='Beginner → Advanced',
    lead='The shell is the program that reads your commands. It keeps variables of two kinds: shell variables only it sees, and environment variables every program it starts receives. This lesson covers the types of shells, variables, export and PATH.',
    chips=['Types of shells', 'export animated', 'PATH search animated', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Shell variables vs environment variables
course=Linux
city="New Delhi"
echo "$course in $city"
bash -c 'echo "child sees: [$course]"'
export course
bash -c 'echo "child sees: [$course]"'
declare -p course city
"""

RUN = dict(
    heading='Make, read and export variables',
    intro='<p>Create two variables, see what a child process receives, then export one.</p>',
    code=MAIN,
    anno=[('export course', 'From now on every child gets a copy.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What changed after export?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does the second echo print? Then run.',
             code="file=report\necho \"${file}_2026.txt\"\necho \"$file_2026.txt\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is to set count to 5. Fix the first line.',
             code="count = 5\necho \"count is $count\"\n", expect='any'),
        dict(label='4 · Your turn', hint='Run one command with LANG=C without changing your shell.',
             code="LANG=C bash -c 'echo \"inside: $LANG\"'\necho \"outside: [$LANG]\"\n"),
        dict(label='5 · Challenge', hint='Add a folder to the FRONT of PATH and show the first entry.',
             code="mkdir -p mybin\nexport PATH=\"$PWD/mybin:$PATH\"\necho \"$PATH\" | cut -d: -f1\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your shell and environment',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Shells installed on your PC', cmd='cat /etc/shells', output='# /etc/shells: valid login shells\n/bin/sh\n/usr/bin/sh\n/bin/bash\n/usr/bin/bash\n/bin/rbash\n/usr/bin/rbash\n/usr/bin/dash', note='Typical Ubuntu desktop.'),
        dict(title='2 · Try another shell', cmd='sudo apt install zsh && zsh -c \'echo $ZSH_VERSION\'', output='5.9', note='Typical.'),
        dict(title='3 · Your PATH', cmd="echo \"$PATH\" | tr : '\\n'", output='/usr/local/sbin\n/usr/local/bin\n/usr/sbin\n/usr/bin\n/sbin\n/bin\n/usr/games\n/usr/local/games\n/snap/bin', note='Typical Ubuntu desktop.'),
        dict(title='4 · bash version', cmd='bash --version | head -1', output=pc('bash --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A variable’s life, line by line',
    intro='<p>Step through: create, change, export and remove a variable.</p>',
    code='''course=Linux
course="$course and Bash"
export course
level=beginner
unset level
echo "$course / [$level]"
''',
    notes={1: 'Create :: a shell variable.', 2: 'Change :: build on the old value.', 3: 'Export :: now in the environment.', 5: 'Remove :: level is gone.', 6: 'Read :: unset reads as empty.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s config, an admin’s PATH and a service account.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Configure an app with environment variables',
         problem='<p>A program reads APP_ENV. Show it unset, then set for one run, then exported.</p>',
         inp='a tiny program', approach=['VAR=x cmd.', 'export.'],
         code='''printf 'echo "mode=${APP_ENV:-not set}"\\n' > app.sh
bash app.sh
APP_ENV=test bash app.sh
export APP_ENV=prod; bash app.sh
''', notes={2: 'Not set.', 3: 'One run only.', 4: 'Exported.'}, tryit='Run bash app.sh once more after unset APP_ENV.'),
    dict(level='i', tag='Admin', title='Add your own bin folder to PATH safely',
         problem='<p>Make a script runnable by name without breaking other commands.</p>',
         inp='a script', approach=['~/bin first in PATH.', 'type to check.'],
         code='''mkdir -p mybin; printf '#!/bin/bash\\necho hello from mytool\\n' > mybin/mytool; chmod +x mybin/mytool
export PATH="$PWD/mybin:$PATH"
mytool; type mytool | cut -d' ' -f1-2
ls -d mybin
''', notes={2: 'Front of PATH, old list kept.', 3: 'Found.', 4: 'ls still works.'}, tryit='Try PATH=mybin and run ls (then fix it).'),
    dict(level='a', tag='Security', title='Readonly settings in a script',
         problem='<p>Protect a constant so later code cannot change it by mistake.</p>',
         inp='a script', approach=['readonly.', 'Check the exit status.'],
         code='''readonly BACKUP_DIR=/srv/backup
BACKUP_DIR=/tmp 2>/dev/null || echo "cannot change BACKUP_DIR"
echo "still $BACKUP_DIR"
''', notes={1: 'Constant.', 2: 'Refused.', 3: 'Unchanged.'}, tryit='Try unset BACKUP_DIR.'),
]

QUIZ = mix([
    dict(q='Which line assigns 5 to count?', options=['count = 5', 'count= 5', 'count=5', '$count=5'], answer=2, why='No spaces.'),
    dict(q='A child process sees…', options=['all shell variables', 'only exported (environment) variables', 'nothing', 'only PATH'], answer=1, why='export copies down.'),
    dict(q='Which lists only environment variables?', options=['set', 'env', 'declare', 'echo $*'], answer=1, why='set lists all.'),
    dict(q='Safe way to add ~/bin to PATH?', options=['PATH=~/bin', 'export PATH="$HOME/bin:$PATH"', 'PATH+bin', 'export PATH=bin:'], answer=1, why='Keep the old list.'),
    dict(q='On Ubuntu, /bin/sh is…', options=['bash', 'dash', 'zsh', 'ksh'], answer=1, why='Debian Almquist shell.'),
    dict(q='$SHELL shows…', options=['the running shell', 'your login shell', 'all shells', 'the script name'], answer=1, why='From /etc/passwd.'),
    dict(q='How do you remove a readonly variable?', options=['unset', 'unset -f', 'you cannot (until the shell exits)', 'export -n'], answer=2, why='Read-only for the shell’s life.'),
    dict(q='DEBUG=1 ./app sets DEBUG…', options=['forever', 'for that command only', 'for all users', 'in .bashrc'], answer=1, why='One-command environment.'),
])

REVISION = [
    'Shells: sh, bash (Linux default), dash (/bin/sh on Ubuntu), ksh, csh/tcsh, zsh (macOS), fish. <code>ps -p $$</code> = running; <code>$SHELL</code> = login; <code>chsh -s</code>.',
    '<code>name=value</code> with no spaces; read with <code>"$name"</code> / <code>"${name}"</code>; <code>unset</code>; <code>readonly</code> is permanent.',
    'Shell variable = this shell only; <code>export</code> makes it an environment variable that children copy. Copies never flow back.',
    '<code>env</code>/<code>printenv</code> = environment; <code>set</code>/<code>declare -p</code> = everything.',
    '<code>VAR=v cmd</code> = for one command; <code>env -i</code> = empty environment.',
    'PATH is searched left to right; add with <code>"D:$PATH"</code> never <code>PATH=D</code>.',
]

FAQ = [
    ('What are the types of shells in Linux?', 'sh (Bourne), bash, dash, ksh (Korn), csh/tcsh (C shell), zsh and fish; bash is the default on most Linux distributions.'),
    ('What is the difference between shell and environment variables?', 'Shell variables exist only in the current shell; environment variables are exported and passed to every child process.'),
    ('How do I make a variable permanent?', 'Put export NAME=value in ~/.bashrc (or ~/.profile) and reload it with source (Lesson 12.2).'),
    ('How do I add a directory to PATH?', 'export PATH="$HOME/bin:$PATH" (front) or "$PATH:$HOME/bin" (end).'),
    ('What does export do?', 'It marks a variable to be passed in the environment of commands started afterwards.'),
    ('How do I change my default shell?', 'chsh -s /path/to/shell (listed in /etc/shells); it applies at the next login.'),
    ('Why “command not found” after changing PATH?', 'The old PATH was replaced instead of extended; restore it or open a new terminal.'),
]

PRACTICE_INTRO = 'Small variable tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Greeting', stmt='Store your name in a variable and print “Hello, NAME”.', inp='nothing', code="name=Riya\necho \"Hello, $name\"\n", explain='name=value.'),
    dict(level='easy', title='Braces', stmt='Print backup_2026.tar from base=backup.', inp='nothing', code="base=backup\necho \"${base}_2026.tar\"\n", explain='${}.'),
    dict(level='easy', title='Unset', stmt='Create, unset and print a variable in brackets.', inp='nothing', code="v=1; unset v; echo \"[$v]\"\n", explain='Empty.'),
    dict(level='medium', title='Export test', stmt='Show a child sees an exported variable.', inp='nothing', code="export LEVEL=two\nbash -c 'echo \"child: $LEVEL\"'\n", explain='export.'),
    dict(level='medium', title='Not exported', stmt='Show a child does not see a plain variable.', inp='nothing', code="LEVEL=one\nbash -c 'echo \"child: [$LEVEL]\"'\n", explain='Shell only.'),
    dict(level='medium', title='Exported?', stmt='Print the declare line of an exported variable.', inp='nothing', code="export ZONE=IN; declare -p ZONE\n", explain='-x.'),
    dict(level='business', title='First PATH entry', stmt='Prepend /opt/tools/bin to PATH and print the first entry.', inp='nothing', code="export PATH=\"/opt/tools/bin:$PATH\"\necho \"$PATH\" | cut -d: -f1\n", explain='Front.'),
    dict(level='business', title='Default value', stmt='Print the value of MODE, or “dev” if it is unset.', inp='nothing', code="unset MODE; echo \"${MODE:-dev}\"; MODE=prod; echo \"${MODE:-dev}\"\n", explain='${VAR:-default}.'),
]

SCN_INTRO = 'Interview questions about shells and variables, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What types of shells are there in Linux?”', 'A common first question.', 'can you name and compare?',
        '''<ul>
          <li>sh, bash, dash, ksh, csh/tcsh, zsh, fish.</li>
          <li>bash is the default on most Linux; Ubuntu’s /bin/sh is dash; macOS uses zsh.</li>
          <li><code>cat /etc/shells</code>, <code>echo $0</code>, <code>chsh -s</code>.</li>
        </ul>''', 'saying “Linux has one shell”.') +
    scn('Product company', 'Junior', 'App cannot read DB_HOST', 'echo shows it in the terminal.', 'shell vs environment?',
        '''<ol>
          <li><code>declare -p DB_HOST</code>: no -x, not exported.</li>
          <li><code>export DB_HOST</code> and restart the app from that shell.</li>
          <li>For services, set it in the systemd unit (Environment=), not your terminal.</li>
        </ol>''', 'hard-coding the host in the code.') +
    scn('Operations', 'Mid-level', 'Script works by hand, fails in cron', 'Error: command not found.', 'environment differences?',
        '''<ul>
          <li>cron has a minimal PATH (/usr/bin:/bin) and few variables.</li>
          <li>Use full paths or set PATH at the top of the script/crontab.</li>
          <li>Reproduce with <code>env -i PATH=/usr/bin:/bin bash script.sh</code>.</li>
        </ul>''', 'adding sleep or retries.') +
    scn('Security team', 'Senior', 'PATH contains “.”', 'Found during an audit.', 'why dangerous?',
        '''<ul>
          <li>A file called <code>ls</code> in a shared folder (/tmp) would run instead of /usr/bin/ls.</li>
          <li>Empty entries (<code>::</code>, trailing <code>:</code>) also mean “.”.</li>
          <li>Remove them; use <code>./prog</code> explicitly.</li>
        </ul>''', 'thinking it is just convenience.')
) + interview([
    ('How do you see all environment variables?', 'env or printenv.'),
    ('What does export do?', 'Puts a variable into the environment passed to child processes.'),
    ('$SHELL vs $0?', 'Login shell vs the shell (or script) running now.'),
    ('How do you remove a variable?', 'unset NAME.'),
    ('What is PATH?', 'A colon-separated list of directories searched for commands.'),
    ('Can a child change the parent’s variables?', 'No; it only changes its copy.'),
    ('How to stop a user logging in?', 'Set their shell to /usr/sbin/nologin.'),
], [
    ('RHCSA (EX200)', 'Use shell variables and the environment; manage user accounts (shells).'),
    ('LFCS', 'Shell environment and variables.'),
    ('CompTIA Linux+', 'Environment variables, PATH, export, shells.'),
]) + distro('Variables work the same in POSIX shells; csh and fish differ.', [
    ('Assign', 'x=1', 'x=1', 'x=1 (zsh)', 'set x=1 (cmd) / $x=1 (PowerShell)'),
    ('Export', 'export X=1', 'export X=1', 'export X=1', 'setx / $env:X'),
    ('csh / tcsh', 'setenv X 1', 'setenv X 1', 'setenv X 1', '-'),
    ('Default shell', 'bash', 'bash', 'zsh', 'PowerShell'),
    ('/bin/sh', 'dash', 'bash', 'bash 3.2 / zsh', '-'),
]) + teaser('12.2', 'Riya’s exports disappear every time she opens a new terminal. Where do permanent settings go: .bashrc, .profile, .bash_profile or /etc/profile? Which ones run at login, which in every terminal, and what does .bash_logout do? Next: Bash startup files.')

CHEATSHEET = cheatsheet('Shells and variables', [
    ('Shells', [('ps -p $$', 'running shell'), ('$SHELL', 'login shell'), ('/etc/shells', 'allowed'), ('chsh -s', 'change'), ('nologin', 'no login')]),
    ('Variables', [('x=1', 'assign'), ('"${x}"', 'read'), ('unset x', 'remove'), ('readonly X=1', 'constant'), ('${x:-def}', 'default')]),
    ('Environment', [('export X', 'to env'), ('env / printenv', 'list'), ('set / declare -p', 'all'), ('X=1 cmd', 'one command'), ('env -i cmd', 'empty env')]),
    ('PATH', [('echo $PATH', 'show'), ('PATH="D:$PATH"', 'front'), ('PATH="$PATH:D"', 'end'), ('type -a cmd', 'which one')]),
])

MINDMAP = mindmap('Variables', [
    ('Shells', 'blue', ['bash dash sh', 'ksh csh zsh', 'chsh']),
    ('Make', 'green', ['x=1 no spaces', '"${x}"', 'unset']),
    ('Kinds', 'amber', ['shell only', 'environment', 'special $?']),
    ('Export', 'red', ['copy to child', 'never back', 'env vs set']),
    ('PATH', 'violet', ['left to right', '"D:$PATH"', 'not .']),
    ('Tricks', 'acc', ['VAR=x cmd', 'env -i', 'readonly']),
])

LAB = lab('set up an environment', 'Build the lab, do the four tasks in ONE script file <code>env.sh</code> (so the checker can source it), then run the checker.',
    setup='''mkdir -p ~/lab121/tools && cd ~/lab121 && rm -f env.sh
printf '#!/bin/bash\\necho "lab tool ok"\\n' > tools/labtool; chmod +x tools/labtool''',
    tasks=['In <code>env.sh</code>, create a variable <code>COURSE</code> with the value <code>Linux Basics</code> (with the space) and export it.',
           'Add the line that puts <code>$HOME/lab121/tools</code> at the <b>front</b> of PATH, keeping the old PATH.',
           'Create a readonly variable <code>MAX_RETRY</code> with the value 3.',
           'Create a shell variable <code>secret</code> with any value that is <b>not</b> exported.'],
    solution='''cat > env.sh <<'EOF'
export COURSE="Linux Basics"
export PATH="$HOME/lab121/tools:$PATH"
readonly MAX_RETRY=3
secret=hidden
EOF''',
    check='''cd ~/lab121
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f env.sh ] && source ./env.sh 2>/dev/null
ok "1 export"   '[ "$(bash -c "echo \\$COURSE")" = "Linux Basics" ]'
ok "2 PATH"     '[ "$(echo "$PATH" | cut -d: -f1)" = "$HOME/lab121/tools" ] && command -v ls >/dev/null && labtool >/dev/null'
ok "3 readonly" 'declare -p MAX_RETRY 2>/dev/null | grep -q "declare -r MAX_RETRY=\\"3\\""'
ok "4 secret"   '[ -n "$secret" ] && [ -z "$(bash -c "echo \\$secret")" ]' ''')
