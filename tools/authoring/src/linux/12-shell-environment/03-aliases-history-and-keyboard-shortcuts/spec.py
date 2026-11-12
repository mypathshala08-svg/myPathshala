import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='03-aliases-history-and-keyboard-shortcuts', n='12.3',
    module_label='Module 12 · The shell environment and shell programming',
    title='Aliases, history and keyboard shortcuts',
    desc='alias, unalias, type, \\cmd and command; why aliases do not work in scripts; history, !!, !n, !-n, !string, !$, ^old^new, sudo !!, history -c/-d/-r/-a; HISTSIZE, HISTFILESIZE, HISTCONTROL, HISTIGNORE, HISTTIMEFORMAT, histappend; Ctrl+R reverse search and readline shortcuts (Ctrl+A E U K W Y L, Alt+.) shown as real recorded terminal screens.',
    og_desc='Bash aliases, history (!!, !$, ^old^new, Ctrl+R) and keyboard shortcuts with real terminal screens.',
    minutes=35, level='Beginner → Advanced',
    lead='Aliases shorten long commands, history remembers everything you typed and keyboard shortcuts make editing fast. This lesson covers all three with real terminal screens, and explains why aliases never protect your scripts.',
    chips=['Real Ctrl+R screens', '!! !$ ^old^new', 'Alias traps', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Aliases (scripts need this switch; your terminal has it on)
shopt -s expand_aliases
alias ll='ls -ld'
alias today='date +%F'
ll /tmp
type ll
unalias ll
type ll 2>&1 | head -1
"""

RUN = dict(
    heading='Make, use and remove an alias',
    intro='<p>Define two aliases, use one, check what it is with type, then remove it.</p>',
    code=MAIN,
    anno=[("alias ll='ls -ld'", 'Single quotes: the text is used as it is.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What does type say after unalias?', code=MAIN, expect='any'),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which echo prints the time when it is USED? Then run.',
             code="shopt -s expand_aliases\nalias a1=\"echo $SECONDS\"\nalias a2='echo $SECONDS'\nsleep 1\na1; a2\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is an alias gs for git status. Fix the definition.',
             code="shopt -s expand_aliases\nalias gs = 'git status'\nalias gs 2>&1 | tail -1\n", expect='any'),
        dict(label='4 · Your turn', hint='Make an alias that counts files in the current folder.',
             code="shopt -s expand_aliases\nalias count='ls -1 | wc -l'\ntouch a b c\ncount\n"),
        dict(label='5 · Challenge', hint='Run the real ls even though ls has an alias.',
             code="shopt -s expand_aliases\nalias ls='echo NOT THE REAL LS'\nls\n\\ls -d .\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your history and aliases',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Your aliases', cmd='alias', output="alias alert='notify-send --urgency=low …'\nalias egrep='egrep --color=auto'\nalias fgrep='fgrep --color=auto'\nalias grep='grep --color=auto'\nalias l='ls -CF'\nalias la='ls -A'\nalias ll='ls -alF'\nalias ls='ls --color=auto'", note='Typical Ubuntu default .bashrc.'),
        dict(title='2 · Your 5 most-used commands', cmd="history | awk '{print $2}' | sort | uniq -c | sort -rn | head -5", output='    212 ls\n    140 cd\n     88 git\n     51 sudo\n     33 python3', note='Typical.'),
        dict(title='3 · Turn on dates', cmd="echo \"HISTTIMEFORMAT='%F %T '\" >> ~/.bashrc && source ~/.bashrc && history 3", output="  998  2026-11-11 10:12:01 ls\n  999  2026-11-11 10:12:05 source ~/.bashrc\n 1000  2026-11-11 10:12:07 history 3", note='Typical.'),
        dict(title='4 · Readline version', cmd="bind -v | head -3", output="set bind-tty-special-chars on\nset blink-matching-paren off\nset byte-oriented off", note='Typical (needs an interactive shell).'),
    ],
)

TRACE = dict(
    heading='An alias appears and disappears',
    intro='<p>Step through a script that switches aliases on, defines one, uses it and removes it.</p>',
    code='''shopt -s expand_aliases
alias greet='echo Namaste'
greet Riya
unalias greet
type greet 2>/dev/null || echo "greet is gone"
''',
    notes={1: 'Switch on :: scripts need this.', 2: 'Define.', 3: 'Use :: Riya is appended.', 4: 'Remove.', 5: 'Gone.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s shortcuts, an admin’s history search and a security check.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Git shortcuts',
         problem='<p>Define gs and gl aliases and show what they are.</p>',
         inp='nothing', approach=['alias.', 'alias NAME.'],
         code='''shopt -s expand_aliases
alias gs='git status -sb'
alias gl='git log --oneline -5'
alias gs gl
''', notes={4: 'Shows the definitions.'}, tryit='Add one for git diff --stat.'),
    dict(level='i', tag='Admin', title='Most-used commands from a history file',
         problem='<p>From a saved history, find the three most frequent commands.</p>',
         inp='a history file', approach=['awk first word.', 'uniq -c.'],
         code='''printf '%s\\n' 'ls' 'cd /var/log' 'ls' 'tail -f syslog' 'ls' 'cd ~' > hist.txt
awk '{print $1}' hist.txt | sort | uniq -c | sort -rn | head -3
''', notes={2: 'Count.'}, tryit='Count whole lines instead of first words.'),
    dict(level='a', tag='Security', title='Find secrets in history',
         problem='<p>Scan a history file for lines that look like passwords on the command line.</p>',
         inp='a history file', approach=['grep -nE.'],
         code='''printf '%s\\n' 'ls' 'mysql -u app -pS3cret' 'export TOKEN=abc123' 'df -h' > hist.txt
grep -nE -- '-p[^ ]+|TOKEN=|PASSWORD=' hist.txt | cut -d: -f1 | tr '\\n' ' '; echo
''', notes={2: 'Line numbers of risky entries.'}, tryit='Delete them with sed -i and check again.'),
]

QUIZ = mix([
    dict(q='Which defines an alias correctly?', options=["alias ll = 'ls -l'", "alias ll='ls -l'", "alias 'll'=ls -l", 'set ll=ls -l'], answer=1, why='No spaces around =.'),
    dict(q='Why does an alias in .bashrc not work in your script?', options=['scripts are slow', 'aliases are not expanded in non-interactive shells', 'aliases need root', 'scripts read .profile'], answer=1, why='expand_aliases is off.'),
    dict(q='What does !! do?', options=['clears history', 'repeats the last command', 'negates', 'runs as root'], answer=1, why='sudo !! adds root.'),
    dict(q='What does ^tst^test do?', options=['replaces tst with test in the last command and runs it', 'searches history', 'nothing', 'deletes history'], answer=0, why='Quick substitution.'),
    dict(q='Which key searches history backwards?', options=['Ctrl+S', 'Ctrl+R', 'Ctrl+H', 'Ctrl+F'], answer=1, why='Reverse search.'),
    dict(q='Which jumps to the start of the line?', options=['Ctrl+E', 'Ctrl+A', 'Ctrl+U', 'Ctrl+W'], answer=1, why='E = end.'),
    dict(q='HISTCONTROL=ignoreboth means…', options=['no history', 'skip duplicates and lines starting with a space', 'save twice', 'save to two files'], answer=1, why='ignoredups + ignorespace.'),
    dict(q='How do you run the real ls if ls is an alias?', options=['\\ls', 'ls!', 'real ls', 'ls --real'], answer=0, why='Or command ls.'),
])

REVISION = [
    "<code>alias n='text'</code>, <code>alias</code>, <code>unalias n</code>, <code>type n</code>, <code>\\cmd</code>/<code>command cmd</code>; single quotes; permanent in ~/.bashrc.",
    'Aliases: first word only, interactive shells only (not scripts), arguments go at the end; use functions for more.',
    '<code>history</code>, <code>!!</code>, <code>!n</code>, <code>!str</code>, <code>!$</code>, <code>^old^new</code>, <code>sudo !!</code>, <code>history -d N</code>.',
    'HISTSIZE/HISTFILESIZE, HISTCONTROL=ignoreboth, HISTTIMEFORMAT, histappend.',
    'Keys: Ctrl+R/Ctrl+G, Ctrl+A/E, Ctrl+U/K/W/Y, Alt+., Ctrl+L, Ctrl+C, Ctrl+D, Tab.',
    'History is convenience, not an audit; never type secrets on the command line.',
]

FAQ = [
    ('How do I create a permanent alias in Linux?', "Add alias name='command' to ~/.bashrc and run source ~/.bashrc."),
    ('How do I remove an alias?', 'unalias name (and remove it from ~/.bashrc).'),
    ('Why does my alias not work in a shell script?', 'Non-interactive shells do not expand aliases; use a function or the full command (or shopt -s expand_aliases).'),
    ('How do I search command history?', 'Press Ctrl+R and type part of the command, or history | grep TEXT.'),
    ('How do I see timestamps in history?', "Set HISTTIMEFORMAT='%F %T ' in ~/.bashrc."),
    ('How do I clear bash history?', 'history -c (memory) and truncate ~/.bash_history; history -d N removes one entry.'),
    ('What does sudo !! do?', 'Runs the previous command again with sudo.'),
]

PRACTICE_INTRO = 'Small alias and history tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Define and use', stmt='Make an alias hi that prints Namaste and use it.', inp='nothing', code="shopt -s expand_aliases\nalias hi='echo Namaste'\nhi\n", explain='alias.'),
    dict(level='easy', title='Show one', stmt='Print the definition of the alias hi.', inp='nothing', code="alias hi='echo Namaste'\nalias hi\n", explain='alias NAME.'),
    dict(level='easy', title='What is it?', stmt='Use type to show that cd is a builtin.', inp='nothing', code="type cd\n", explain='type.'),
    dict(level='medium', title='Argument at the end', stmt='Alias lsd=\'ls -d\' and use it on /tmp.', inp='nothing', code="shopt -s expand_aliases\nalias lsd='ls -d'\nlsd /tmp\n", explain='Appended.'),
    dict(level='medium', title='Bypass', stmt='Alias echo to print X, then run the real echo with a backslash.', inp='nothing', code="shopt -s expand_aliases\nalias echo='printf X\\\\n #'\necho real\n\\echo real\n", explain='\\ skips.'),
    dict(level='medium', title='Read a history file', stmt='Load a history file and print how many entries there are.', inp='a file', code="printf '%s\\n' a b c > h.txt\nhistory -r h.txt; history | wc -l\n", explain='history -r.'),
    dict(level='business', title='Unique commands', stmt='Count distinct first words in a history file.', inp='a file', code="printf '%s\\n' 'ls -l' 'cd /' 'ls' 'df -h' > h.txt\nawk '{print $1}' h.txt | sort -u | wc -l\n", explain='3.'),
    dict(level='business', title='Remove all aliases', stmt='Define two aliases, remove all, show none remain.', inp='nothing', code="alias a1=ls a2=pwd\nunalias -a\nalias | wc -l\n", explain='unalias -a.'),
]

SCN_INTRO = 'Interview questions about aliases and history, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What is an alias? How to make it permanent?”', 'Common in Linux rounds.', 'basics?',
        '''<ul>
          <li>A short name for a command: <code>alias ll='ls -l'</code>.</li>
          <li>Permanent: put it in ~/.bashrc, then <code>source ~/.bashrc</code>.</li>
          <li>Remove: <code>unalias ll</code>.</li>
        </ul>''', 'not knowing where to save it.') +
    scn('Support team', 'Junior', '“How do you re-run a command as root without retyping?”', 'A quick practical check.', 'history expansion?',
        '''<ol>
          <li><code>sudo !!</code>.</li>
          <li>Or ↑, Ctrl+A, type sudo.</li>
          <li>Ctrl+R to find older ones.</li>
        </ol>''', 'retyping long commands.') +
    scn('DevOps', 'Mid-level', 'A teammate’s script uses his aliases and fails in CI', 'Error: ll: command not found.', 'aliases in scripts?',
        '''<ul>
          <li>Non-interactive shells do not expand aliases and CI has no .bashrc.</li>
          <li>Use full commands or functions defined in the script.</li>
          <li>Never depend on personal dotfiles in shared code.</li>
        </ul>''', 'adding source ~/.bashrc to the CI job.') +
    scn('Security', 'Senior', 'Secrets found in ~/.bash_history', 'An audit found database passwords in history files.', 'prevention?',
        '''<ul>
          <li>Rotate the secrets; remove the entries.</li>
          <li>Use prompts (<code>mysql -p</code> without value), config files with 600 permissions, or a secret manager.</li>
          <li>HISTCONTROL=ignorespace for unavoidable cases; real auditing with auditd, not history.</li>
        </ul>''', 'just deleting the history file.')
) + interview([
    ('Where is history stored?', '~/.bash_history (HISTFILE), written when the shell exits.'),
    ('How do you see the last 10 commands?', 'history 10.'),
    ('What is !$?', 'The last argument of the previous command.'),
    ('How to bypass an alias?', '\\cmd or command cmd.'),
    ('Alias vs function?', 'A function can take arguments anywhere and contain logic.'),
    ('What does Ctrl+U do?', 'Deletes from the cursor to the start of the line.'),
    ('How to keep history from two terminals?', 'shopt -s histappend (and history -a).'),
], [
    ('RHCSA (EX200)', 'Use the shell effectively: history, aliases, editing.'),
    ('LFCS', 'Use shell features: history and aliases.'),
    ('CompTIA Linux+', 'alias, history, shell shortcuts.'),
]) + distro('Same in all bash/zsh shells; small differences.', [
    ('alias syntax', 'yes', 'yes', 'zsh: same', 'PowerShell: Set-Alias (no arguments)'),
    ('Default ll', 'ls -alF', 'ls -l --color', 'none', '-'),
    ('History file', '~/.bash_history', '~/.bash_history', '~/.zsh_history', 'PSReadLine history'),
    ('Ctrl+R', 'yes', 'yes', 'yes', 'yes (PSReadLine)'),
    ('histappend default', 'on', 'on', 'zsh: setopt', '-'),
]) + teaser('12.4', 'Riya’s alias failed because of the quotes: double quotes ran $(date) too early. Quotes decide what the shell expands and what it leaves alone. Single, double, backslash, $( ): next, quoting and expansion.')

CHEATSHEET = cheatsheet('Aliases and history', [
    ('Alias', [("alias n='cmd'", 'define'), ('alias', 'list'), ('unalias n', 'remove'), ('\\cmd', 'bypass'), ('type n', 'what is it')]),
    ('History', [('history N', 'last N'), ('!!', 'last'), ('!n / !-n', 'by number'), ('!str', 'by prefix'), ('!$', 'last arg'), ('^a^b', 'fix, rerun')]),
    ('Settings', [('HISTSIZE', 'memory'), ('HISTFILESIZE', 'file'), ('HISTCONTROL', 'ignoreboth'), ('HISTTIMEFORMAT', 'dates')]),
    ('Keys', [('Ctrl+R', 'search'), ('Ctrl+A / E', 'start / end'), ('Ctrl+U / K / W', 'cut'), ('Alt+.', 'last arg'), ('Ctrl+L', 'clear')]),
])

MINDMAP = mindmap('Shell speed', [
    ('Alias', 'blue', ["'single'", 'first word', 'not scripts']),
    ('History', 'green', ['history', '~/.bash_history', '-d -c']),
    ('Bang', 'amber', ['!! !n', '!$ !str', '^a^b']),
    ('Search', 'red', ['Ctrl+R', 'Ctrl+G', 'grep']),
    ('Settings', 'violet', ['HISTSIZE', 'ignoreboth', 'timestamps']),
    ('Keys', 'acc', ['Ctrl+A E', 'Ctrl+U K W', 'Alt+.']),
])

LAB = lab('a better .bashrc', 'Build the lab, write the four settings into <code>~/lab123/my.bashrc</code>, then run the checker (it loads the file in an interactive shell).',
    setup='''mkdir -p ~/lab123 && cd ~/lab123 && rm -f my.bashrc && mkdir -p logs && echo 'GET / 200' > logs/web.log''',
    tasks=['An alias <code>ll</code> for <code>ls -lh</code>.',
           'An alias <code>weblog</code> that runs <code>tail -n 20 ~/lab123/logs/web.log</code>.',
           'History settings: <code>HISTSIZE=10000</code> and <code>HISTCONTROL=ignoreboth</code>.',
           "Timestamps in history: <code>HISTTIMEFORMAT='%F %T '</code>."],
    solution='''cat > my.bashrc <<'EOF'
alias ll='ls -lh'
alias weblog='tail -n 20 ~/lab123/logs/web.log'
HISTSIZE=10000
HISTCONTROL=ignoreboth
HISTTIMEFORMAT='%F %T '
EOF''',
    check='''cd ~/lab123
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
run(){ bash --rcfile ./my.bashrc -i -c "$1" 2>/dev/null; }
[ -f my.bashrc ] || touch my.bashrc
ok "1 ll"       'run "alias ll" | grep -q "ls -lh"'
ok "2 weblog"   'run "weblog" | grep -q "GET / 200"'
ok "3 history"  '[ "$(run "echo \\$HISTSIZE-\\$HISTCONTROL" | tail -1)" = "10000-ignoreboth" ]'
ok "4 time"     '[ "$(run "echo \\"\\$HISTTIMEFORMAT\\"" | tail -1)" = "%F %T " ]' ''')
