import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

AL = r"""rm -rf ~/al; mkdir -p ~/al/logs; cd ~/al
printf 'GET /a 200\nGET /b 500\nGET /c 200\n' > logs/web.log; touch notes.txt report.txt"""
SA = 'shopt -s expand_aliases\n'
# an interactive bash with a short prompt and a fresh history, for real screen recordings
HI = r"""rm -rf ~/hi; mkdir -p ~/hi; cd ~/hi; touch app.log notes.txt
printf '%s\n' 'PS1="riya@web01:\\w$ "' 'HISTFILE=~/hi/.hist' 'HISTSIZE=1000' 'cd ~/hi' > ~/hi/.rc"""

HOOK = hook('Riya types <code>ls -lh --color=auto</code> forty times a day, and <code>cd /var/www/html/projects/myphatshala/static</code> twenty times. Yesterday she ran a perfect 120-character <code>find … -exec</code> command; today she cannot remember it. Bash has three tools for exactly this: <b>aliases</b> (short names for long commands), <b>history</b> (every command you typed, searchable and re-runnable) and <b>keyboard shortcuts</b> (Ctrl+R, Ctrl+A, Alt+.) that make editing a command line ten times faster. They are the difference between fighting the terminal and flying through it.',
    ['create, list, use and remove aliases; make them permanent; know when an alias is the wrong tool',
     'use history: list, search with Ctrl+R and grep, re-run with !!, !n, !string, fix typos with ^old^new, and reuse arguments with !$ and Alt+.',
     'control history: HISTSIZE, HISTFILESIZE, HISTCONTROL, HISTTIMEFORMAT, HISTIGNORE, history -c, -d, -a',
     'edit command lines fast with the readline shortcuts: Ctrl+A, Ctrl+E, Ctrl+U, Ctrl+K, Ctrl+W, Ctrl+L, Ctrl+C, Ctrl+D, Tab'])
ROAD = roadmap([
    ('story', 'The story', 3, 'the lost command'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'Aliases and history', 6, 'simple meaning + 4 depths'),
    ('types', 'Alias vs function vs script', 4, 'and ! forms'),
    ('commands', 'By field', 15, 'real runs and real screens'),
    ('animation', 'See it happen', 4, 'Ctrl+R search'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 6, 'a better .bashrc'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Shorten a command you type often', "alias ll='ls -lh'", 'in ~/.bashrc'),
    ('Shorten something with arguments in the middle', 'a function (12.10)', 'aliases only add at the end'),
    ('Find an old command', 'Ctrl+R, type a part', 'or history | grep'),
    ('Run the last command again', '!!', 'sudo !! = again as root'),
    ('Fix a typo in the last command', '^old^new', 'replace once'),
    ('Reuse the last argument', '!$  or  Alt+.', 'mkdir d && cd !$'),
    ('Ignore the alias once', '\\ls  or  command ls', 'run the real one'),
    ('Hide a command from history', 'start it with a space', 'with HISTCONTROL=ignorespace'),
])

cmap = concept_map(
    [('12.2', 'Startup files', '.bashrc'), ('12.1', 'Variables', 'HIST* variables'), ('1.6', 'Terminal', 'the prompt')],
    ['alias, unalias, \\cmd, command', 'history list, Ctrl+R, history | grep', '!! !n !-n !string !$ ^old^new', 'HISTSIZE, HISTCONTROL, HISTTIMEFORMAT', 'readline shortcuts: Ctrl+A E U K W L, Alt+.'],
    [('12.10', 'Functions', 'aliases with arguments'), ('12.4', 'Quoting', 'single quotes in aliases'), ('11.4', 'Jobs', 'Ctrl+Z'), ('18.1', 'Audit', 'what history is not')],
    'Aliases save typing, history saves remembering, shortcuts save editing. All three live in your interactive shell, configured in ~/.bashrc.')

sc = (term(20, 14, 316, 156, ['$ alias ll=\'ls -lh\'', '$ ll app.log', ('-rw-rw-r-- 1 riya riya 0 Nov 11 app.log', 'out'), '$ history | tail -3', ('  41  find /var/log -name "*.gz" -mtime +7', 'out'), ('  42  alias ll=\'ls -lh\'', 'out'), ('(reverse-i-search)`find\': find /var/log …', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=15)
      + t(352, 36, 'Three helpers:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• alias: short name', '• history: memory', '• Ctrl+R: search it', '• Ctrl+A/E: jump', '• !!: again'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>The lost command</h2>
  <div class="story">
''' + puzzle('Riya adds <code>alias rm=\'rm -i\'</code> to her .bashrc to protect herself. In her terminal, <code>rm notes.txt</code> asks “remove?”. Then she runs her clean-up script <code>cleanup.sh</code>, which contains <code>rm *.tmp</code>: it deletes everything without asking. Why did the alias not protect the script, and why is relying on that alias dangerous?') + '''
    <p class="narration">Riya makes a short name for a long command, and finds yesterday’s command in a second.</p>
''' + scene('A terminal: an alias ll is created and used; history shows numbered commands; reverse search finds an old find command.', sc,
            '<tspan font-weight="700" class="s-acc">Ctrl+R</tspan> + a few letters finds any command you typed before.') + '''
K> Where does history come from?
A> Bash remembers every command you type in memory and, when the shell exits, appends them to <code>~/.bash_history</code>. You can list it, search it, and re-run any entry without typing it again.
R> And aliases?
A> An alias is a text replacement: when the <b>first word</b> of a command matches, bash swaps in the longer text before running it. Simple, fast, and only in interactive shells, which is exactly the trap in the puzzle.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A phone: speed-dial numbers are aliases, the call log is history, and the search box in the call log is Ctrl+R.">'
       + label_box(14, 20, 190, 110, ['alias = speed dial', 'press 2 →', 'calls a long number', 'll → ls -lh'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['history = call log', 'every command,', 'numbered', '!42 = redial 42'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['Ctrl+R = search', 'type “find”:', 'newest match', 'Enter = run it'], 'amber', 8.6)
       + t(320, 160, 'Speed dial for what you use daily; the log for everything else.', 9.6, 'ink2')
       + t(320, 182, 'Both live in your interactive shell only.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Aliases and history at four depths', [
    ('v', 'No jargon: speed dial and call log', '      <p>Your phone already does this.</p>' + pic),
    ('b', 'What you will type every day', '''      <ul>
        <li><code>alias ll='ls -lh'</code> then <code>ll</code>. <code>alias</code> alone lists them; <code>unalias ll</code> removes one.</li>
        <li><code>history</code> lists your commands; <code>!!</code> repeats the last; <code>sudo !!</code> repeats it as root.</li>
        <li><kbd>Ctrl</kbd>+<kbd>R</kbd> then type: search backwards; <kbd>Enter</kbd> runs, <kbd>→</kbd> edits, <kbd>Ctrl</kbd>+<kbd>G</kbd> cancels.</li>
        <li><kbd>↑</kbd>/<kbd>↓</kbd> walk through history; <kbd>Tab</kbd> completes names.</li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li>Only the <b>first word</b> of a command is checked for an alias (and the word after an alias ending in a space: <code>alias sudo='sudo '</code>).</li>
        <li>Define aliases with single quotes so <code>$vars</code> are expanded when used, not when defined.</li>
        <li>Aliases are not expanded in scripts (<code>shopt expand_aliases</code> is off) and are expanded when a line is <b>read</b>, so an alias defined on a line is not usable on that same line.</li>
        <li>History expansion (<code>!</code>) happens before everything else, even inside double quotes: <code>echo "hi!"</code> can surprise you. Use single quotes or <code>set +H</code>.</li>
        <li>HISTSIZE = lines kept in memory; HISTFILESIZE = lines in ~/.bash_history; the file is written when the shell exits.</li>
      </ul>'''),
    ('a', 'Behind the screen: readline and the history list', '''      <ul>
        <li>Line editing (Ctrl+A, Ctrl+R, Tab) is the <b>GNU readline</b> library, shared with python, mysql, psql and gdb. Its settings are in <code>~/.inputrc</code> (e.g. <code>set completion-ignore-case on</code>).</li>
        <li>Default key map is Emacs style; <code>set -o vi</code> switches to vi mode (Lesson 12.6).</li>
        <li>Two terminals each keep their own in-memory list and overwrite each other’s file at exit unless <code>shopt -s histappend</code> (Ubuntu’s default .bashrc sets it). <code>PROMPT_COMMAND='history -a'</code> saves after every command.</li>
        <li>Ctrl+S (forward search) is often swallowed by terminal flow control; <code>stty -ixon</code> frees it.</li>
        <li>History is a convenience, not an audit log: users can edit or delete it. Real auditing uses auditd and system logs.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Aliases, history and keyboard shortcuts</h2>
''' + def_block(
    'An <b>alias</b> is a name that the shell replaces with a string of text when it appears as the first word of a simple command. The <b>history</b> is the list of commands the shell has read, kept in memory and saved to <code>~/.bash_history</code>; <b>history expansion</b> (<code>!!</code>, <code>!n</code>, <code>!string</code>, <code>^old^new</code>) re-uses entries. <b>Keyboard shortcuts</b> are readline key bindings for moving, editing, completing and searching the command line.',
    'Alias = short name. History = memory. Shortcuts = fast editing.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Alias', 'Short name expanded to longer text.'),
    ('unalias', 'Remove an alias.'),
    ('History list', 'Numbered commands typed so far.'),
    ('Event designator', '!!, !n, !string: which entry.'),
    ('Word designator', '!$, !^, !*: which word of it.'),
    ('Reverse search', 'Ctrl+R: find older commands.'),
    ('readline', 'The library that edits command lines.'),
    ('HISTCONTROL', 'What not to save (dups, spaces).'),
]) + '\n' + names('Where the names come from.', [
    ('alias', 'another name', 'From csh, 1978.'),
    ('!!', 'bang bang', 'Last command (csh).'),
    ('!$', 'bang dollar', 'Last word of last command.'),
    ('^old^new', 'quick substitution', 'csh.'),
    ('Ctrl+R', 'reverse', 'Search backwards.'),
    ('Ctrl+A / E', 'start / end', 'Emacs keys.'),
    ('Ctrl+U / K', 'kill', 'Cut to start / end.'),
    ('Alt+.', 'yank last arg', 'Insert last argument.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Make', "<code>alias ll='ls -lh'</code>"),
    ('List', '<code>alias</code>'),
    ('Remove', '<code>unalias ll</code>'),
    ('Search', '<kbd>Ctrl</kbd>+<kbd>R</kbd>'),
    ('Again', '<code>!!</code>'),
    ('Last arg', '<code>!$</code> / <kbd>Alt</kbd>+<kbd>.</kbd>'),
]) + '\n' + lv + didyou('<code>sudo !!</code> is probably the most-typed fix in Linux: you run a command, get “Permission denied”, and re-run exactly the same command as root without retyping it.') + '''
EXAM> “How do you make an alias permanent?” → Add the <code>alias</code> line to <code>~/.bashrc</code> and run <code>source ~/.bashrc</code>.
''' + qc('Is <code>ll</code> a command on every Linux system?', 'No. It is an alias defined in many default .bashrc files (Ubuntu: ls -alF). type ll shows what it is on your machine.') + mistake("alias rm='rm -i'   (as your only protection)",
    'Keep it if you like, but never rely on it: scripts, other users, sudo and root shells do not have it. Use rm -i explicitly and backups.',
    'Aliases expand only in your interactive shell. The day you are on another server or in a script, rm deletes without asking.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Alias vs function vs script, and the ! forms</h2>
''' + table(['', 'Alias', 'Function (12.10)', 'Script (12.5)'], [
    ['Arguments', 'only added at the end', '$1, $2 anywhere', '$1, $2 anywhere'],
    ['Logic (if, loops)', 'no', 'yes', 'yes'],
    ['Lives in', '~/.bashrc', '~/.bashrc', 'a file in PATH'],
    ['Works in scripts', 'no (by default)', 'yes, if defined there', 'yes'],
    ['Other users / sudo', 'no', 'no', 'yes (if readable/in PATH)'],
    ['Best for', 'short options shortcuts', 'small helpers', 'real tools'],
], minw=560) + table(['Form', 'Means', 'Example'], [
    ['<code>!!</code>', 'the last command', '<code>sudo !!</code>'],
    ['<code>!n</code>', 'command number n', '<code>!42</code>'],
    ['<code>!-n</code>', 'n commands back', '<code>!-2</code>'],
    ['<code>!string</code>', 'last command starting with string', '<code>!ssh</code>'],
    ['<code>!?text?</code>', 'last command containing text', '<code>!?log?</code>'],
    ['<code>!$</code>', 'last word of the last command', '<code>cd !$</code>'],
    ['<code>!^</code> / <code>!*</code>', 'first / all arguments', '<code>vim !*</code>'],
    ['<code>^old^new</code>', 'last command, replace once', '<code>^tset^test</code>'],
    ['<code>!!:p</code>', 'print, do not run', 'check first'],
], minw=440) + table(['Variable', 'Effect', 'Good value'], [
    ['<code>HISTSIZE</code>', 'lines kept in memory', '10000'],
    ['<code>HISTFILESIZE</code>', 'lines kept in the file', '20000'],
    ['<code>HISTCONTROL</code>', 'ignorespace, ignoredups, ignoreboth, erasedups', 'ignoreboth'],
    ['<code>HISTIGNORE</code>', 'patterns never saved', "'ls:ll:history'"],
    ['<code>HISTTIMEFORMAT</code>', 'show date/time in history', "'%F %T '"],
    ['<code>HISTFILE</code>', 'where it is saved', '~/.bash_history'],
], minw=440) + qc('You want <code>gco BRANCH</code> to run <code>git checkout BRANCH</code>. Alias or function?', 'An alias works (the argument goes at the end): alias gco=\'git checkout\'. For anything with the argument in the middle, use a function.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Aliases, history and shortcuts, then used in every field</h2>
  <p id="commands">Outputs were recorded on our Ubuntu 24.04 build machine as riya, in <code>~/al</code> (a small web log and two text files). Aliases are normally interactive only, so the recorded examples switch them on with <code>shopt -s expand_aliases</code>, the way a script would. History and shortcuts only exist in an interactive shell, so they are shown as <b>real terminal screens</b>: an interactive bash in a 72×12 terminal, recorded after each key.</p>
''' + cmdcard_u(['shortening long commands you type often', 'adding safe default options', 'quick navigation (cd to deep folders)'],
               ['anything with arguments in the middle (use a function)', 'changing what standard commands do on shared servers'])(
    'alias', 'alias · unalias · \\cmd · command', 'short names',
    "<code>alias name='text'</code> defines, <code>alias</code> lists all, <code>alias name</code> shows one, <code>unalias name</code> removes (<code>-a</code> all). <code>\\name</code> or <code>command name</code> runs the real command without the alias; <code>type name</code> tells you what a name is.",
    "alias NAME='TEXT'   ·   unalias NAME   ·   \\NAME", 'safe',
    [("alias ll='ls -lh'", 'define', 'daily'),
     ('alias', 'list all', 'check'),
     ('unalias ll', 'remove', 'clean up'),
     ('\\ls / command ls', 'skip the alias once', 'real command'),
     ('type ll', 'alias, builtin or file?', 'debug'),
     ("alias ..='cd ..'", 'navigation', 'speed')],
    dict(setup=AL, cmd=SA + "cd ~/al\nalias ll='ls -l'\nalias errors='grep \" 500\" logs/web.log'\nll -d logs\nerrors\ntype ll", note='The extra argument -d logs was added after the alias text. type confirms what ll is.'),
    [('dev', [
        dict(situation='Quick project navigation and a safe default.', setup=AL, cmd=SA + "alias proj='cd ~/al/logs'\nalias cp='cp -i'\nproj; pwd\nalias | grep -E \"proj|cp=\"",
             why='Navigation aliases save the most keystrokes. cp -i asks before overwriting, but only in your shell.')]),
     ('sys', [
        dict(situation='Run the real command, not the alias.', setup=AL, cmd=SA + "cd ~/al\nalias ls='ls -1 --classify'\nls logs\n\\ls -d logs\ncommand ls -d logs\nunalias ls; type ls",
             why='\\ls and command ls bypass the alias. After unalias, ls is the program again (hashed path).')]),
     ('qa', [
        dict(situation='The puzzle: scripts ignore your aliases.', setup=AL, cmd="cd ~/al; touch a.tmp b.tmp\nprintf 'alias rm=\"rm -i\"\\nrm *.tmp\\n' > cleanup.sh\nbash cleanup.sh < /dev/null; ls *.tmp 2>/dev/null || echo 'all .tmp gone: no question asked'", expect='any',
             why='Even an alias defined inside the script is not expanded (expand_aliases is off), so rm ran without -i.')]),
    ],
    anat=anatomy([('alias', 'cmd', 'define'), ('ll', 'arg', 'new name'), ("='ls -lh'", 'arg', 'text, single quotes')], 'No spaces around =; single quotes keep $vars for later.')
) + mistake("alias today=\"echo $(date +%F)\"", "alias today='echo $(date +%F)'",
            'With double quotes, $(date) runs once when the alias is DEFINED, so it prints the same date forever. Single quotes delay it until the alias is used.')

SCREENS1 = screens_block('Real terminal screens: history, !! and ^old^new', 'An interactive bash, recorded after each key: commands, the list, re-running and a typo fix.',
    HI, 'bash --rcfile ~/hi/.rc', [
    ('mkdir reports  Enter', "'mkdir reports' Enter", ' make a folder.'),
    ('cd !$  Enter', "'cd !$' Enter", ' !$ = the last argument (reports): bash prints the expanded command, then runs it.'),
    ('history 3  Enter', "'history 3' Enter", ' the numbered list.'),
    ('ls -l ../nots.txt  Enter', "'ls -l ../nots.txt' Enter", ' a typo: No such file.'),
    ('^nots^notes  Enter', "'^nots^notes' Enter", ' replace once and re-run: fixed without retyping.'),
], 72, 12, hid='screens', what='bash')

SCREENS2 = screens_block('Real terminal screens: Ctrl+R reverse search and line editing', 'Finding an old command by typing a few letters, then editing a line with Ctrl+A, Ctrl+U and Ctrl+W.',
    HI, 'bash --rcfile ~/hi/.rc', [
    ('a long find  Enter', "'find . -name \"*.log\" -size -1k' Enter", ' a long command we will need again.'),
    ('ls; date  Enter', "'ls; date +%Y' Enter", ' something else in between.'),
    ('Ctrl+R  then  find', "C-r 'find'", ' reverse search: the newest command containing “find” appears.'),
    ('Enter', 'Enter', ' runs it.'),
    ('echo one two three, then Ctrl+W', "'echo one two three' C-w", ' Ctrl+W deletes the word before the cursor.'),
    ('Ctrl+A  then  type sudo', "C-a 'sudo '", ' Ctrl+A jumps to the start of the line (Ctrl+E to the end).'),
    ('Ctrl+U', 'C-u', ' Ctrl+U deletes from the cursor back to the start of the line: the “sudo ” we just typed is gone.'),
], 72, 12, what='bash')

cards = cards + cmdcard_u(['finding and re-running old commands', 'documenting what you did', 'repeating with sudo'],
               ['re-running dangerous commands blindly (print first with :p)', 'treating history as an audit log'])(
    'history', 'history · ! expansion', 'your command memory',
    '<code>history</code> lists numbered entries (<code>history 5</code> the last five). <code>!!</code> last, <code>!n</code> number n, <code>!-n</code> n back, <code>!str</code> last starting with str, <code>!$</code> last argument, <code>^a^b</code> fix and re-run. <code>history -c</code> clears memory, <code>-d N</code> deletes one, <code>-a</code> appends to the file now.',
    'history [N]   ·   !! !n !str !$ ^old^new   ·   history -d N', 'change',
    [('history 10', 'last 10', 'look'),
     ('history | grep ssh', 'search', 'find'),
     ('!!', 'last command', 'repeat'),
     ('sudo !!', 'last, as root', 'Permission denied'),
     ('!42', 'number 42', 'from the list'),
     ('!$', 'last argument', 'cd !$'),
     ('^ls^ll', 'replace once, run', 'typos'),
     ('history -d 42', 'delete entry', 'pasted a password')],
    dict(setup=HI, cmd="cd ~/hi; printf '%s\\n' 'ls -l' 'df -h' 'ssh web02' 'tail -f app.log' > hist.txt\nhistory -r hist.txt; history", note='Here we load a sample history file into a fresh shell (history -r) to show the numbered list.'),
    [('sys', [
        dict(situation='Search the saved history for every ssh you ran.', setup=HI, cmd="cd ~/hi; printf '%s\\n' 'ls' 'ssh web02' 'df -h' 'ssh db01 uptime' 'ssh web02' > .hist\ngrep '^ssh' .hist | sort | uniq -c | sort -rn",
             why='~/.bash_history is a plain text file: grep, sort and uniq work on it (Lesson 6.2).')]),
     ('sec', [
        dict(situation='A password was pasted into the terminal by mistake.', setup=HI, cmd="cd ~/hi; printf '%s\\n' 'ls' 'mysql -u root -pSecret123' 'df -h' > hist.txt; history -r hist.txt\nhistory | grep -n pSecret | cut -d: -f1\nhistory -d 2; history",
             why='Delete the entry from memory (-d N) and from ~/.bash_history; then change the password anyway. Better: never type secrets on the command line.')]),
    ]
) + SCREENS1 + cmdcard_u(['big, timestamped, duplicate-free history', 'keeping secrets out of history'],
               ['HISTSIZE=0 (you lose the feature)', 'expecting history to survive a crash without -a'])(
    'histvars', 'HISTSIZE · HISTCONTROL · HISTTIMEFORMAT', 'tune history',
    'Set these in ~/.bashrc: <code>HISTSIZE</code> and <code>HISTFILESIZE</code> (how many), <code>HISTCONTROL=ignoreboth</code> (skip duplicates and lines starting with a space), <code>HISTIGNORE</code> (patterns), <code>HISTTIMEFORMAT=\'%F %T \'</code> (dates), <code>shopt -s histappend</code> (do not overwrite).',
    "HISTSIZE=10000 HISTFILESIZE=20000 HISTCONTROL=ignoreboth HISTTIMEFORMAT='%F %T '", 'safe',
    [('HISTSIZE=10000', 'memory', 'more recall'),
     ('HISTFILESIZE=20000', 'file', 'long memory'),
     ('HISTCONTROL=ignoreboth', 'no dups, no space-lines', 'clean'),
     ("HISTIGNORE='ls:ll'", 'never save these', 'noise'),
     ("HISTTIMEFORMAT='%F %T '", 'with date/time', 'when did I?'),
     ('shopt -s histappend', 'append, not overwrite', 'many terminals')],
    dict(cmd="grep -E '^HIST|histappend' /etc/skel/.bashrc", note='Ubuntu’s default: ignoreboth, histappend, 1000 / 2000 lines.'),
    [('devops', [
        dict(situation='Dates in history: when did I restart that service?', setup=HI, cmd="cd ~/hi; printf '%s\\n' '#1794375000' 'systemctl restart nginx' '#1794378600' 'df -h' > hist.txt\nHISTTIMEFORMAT='%F %T '; history -r hist.txt; history | sed 's/^ *//'",
             why='With HISTTIMEFORMAT set, bash stores #epoch lines in the file and shows real dates.')]),
    ]
) + SCREENS2 + undo('History and aliases are easy to reset.', [
    ('Bad alias:', '<code>unalias NAME</code>; remove the line from ~/.bashrc.'),
    ('All aliases broken:', '<code>unalias -a</code>, then <code>source ~/.bashrc</code> after fixing.'),
    ('Secret in history:', '<code>history -d N</code>, edit ~/.bash_history, change the secret.'),
    ('Pressed Ctrl+S and the terminal froze:', 'press <kbd>Ctrl</kbd>+<kbd>Q</kbd> (flow control); <code>stty -ixon</code> disables it.'),
    ('Stuck in Ctrl+R:', '<kbd>Ctrl</kbd>+<kbd>G</kbd> cancels the search.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd="alias ll = 'ls -l'", meaning='Spaces around = (alias sees three words).', fix="<code>alias ll='ls -l'</code>."),
    dict(cmd='unalias nothere', meaning='No such alias.', fix='<code>alias</code> to list them.'),
    dict(cmd='\\nosuchcmd', meaning='\\ skips aliases, but the command still must exist.', fix='Check the name.'),
    dict(cmd='history -d 9999', meaning='No entry with that number.', fix='<code>history</code> first.'),
]) + qc('What does <code>!$</code> mean in <code>mkdir -p /srv/app/logs && cd !$</code>?', 'The last word of the previous command: /srv/app/logs. (In a typed line the history list decides; Alt+. inserts it while editing.)') + '''
'''
cards = cards + '</section>\n'

see_cmds = [['$ (Ctrl+R)', "(reverse-i-search)`':"], ["(reverse-i-search)`f':", ('  find . -name "*.log"', 'acc')], ["(reverse-i-search)`fi':", ('  find . -name "*.log"', 'acc')], ['$ find . -name "*.log"', ('./app.log', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~/hi', prompt='riya@web01:~/hi$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Ctrl+R: search mode.', 'Type f…', '…more letters narrow it.', 'Enter runs it.'])]
def hl(k):
    rows = ['ls -l', 'find . -name "*.log"', 'df -h', 'date +%Y']
    o = ''
    for i, r in enumerate(rows):
        tn = 'card'
        if k in (1, 2) and i == 1: tn = 'green'
        if k == 1 and i == 3: tn = 'amber'
        if k == 3 and i == 1: tn = 'green'
        o += label_box(14, 14 + i * 32, 260, 26, [f'{i + 1:>2}  {r}'], tn, 8)
    return o
behind = [hl(k) + t(180, 160, n, 8.4, 'violet', bold=True) for k, n in enumerate(['The history list, newest at the bottom.', 'Search backwards from the newest for “f”.', 'Newest entry containing “fi”: number 2.', 'It is run and added again at the end.'])]
two = anim_two('Ctrl+R', 'Behind the screen: searching the history list',
               'A terminal in reverse-search mode: typing letters finds an older find command.',
               'A list of four history entries; the search walks upwards from the newest and stops at the first one containing the typed letters.', see, behind,
               ['Start.', 'One letter.', 'Two letters.', 'Run.'],
               ['the list', 'search up', 'first match', 'appended'])

def alexp(k):
    o = label_box(14, 26, 150, 40, ['you type:', 'll -d logs'], 'blue', 8)
    if k >= 1:
        o += arrow(164, 46, 200, 46) + label_box(200, 26, 150, 40, ['first word “ll”', 'is an alias'], 'amber', 8)
    if k >= 2:
        o += label_box(14, 90, 336, 34, ['becomes:  ls -l  -d logs'], 'green', 8)
    if k == 3:
        o += label_box(14, 136, 336, 30, ['in a script: no expansion → “ll: command not found”'], 'red', 7.6)
    return o
frames = [alexp(0) + t(180, 190, 'A command line.', 8.6, 'violet', bold=True),
          alexp(1) + t(180, 190, 'bash checks only the first word.', 8.6, 'violet', bold=True),
          alexp(2) + t(180, 190, 'Text replaced; arguments stay at the end.', 8.6, 'green', bold=True),
          alexp(3) + t(180, 190, 'Scripts skip this step.', 8.6, 'red', bold=True)]
s1 = anim_one('Animated example', 'How an alias is expanded',
              'A simple text swap of the first word.',
              'alias expansion', 'The typed line ll -d logs: the first word is found to be an alias and replaced by ls -l, the arguments stay; in scripts this does not happen.', frames,
              ['Typed.', 'Check.', 'Swap.', 'Scripts.'], hid='scenario-alias')

dx = dissect('Layer by layer: where these features live',
    'Each layer has a real command and output from our build machine.', [
    dict(key='rl', name='readline', sub='keys and editing', why='Ctrl+R, Ctrl+A.', how='Key bindings.', impl='~/.inputrc.', used='bash, python, mysql.',
         cmd="bind -P 2>/dev/null | grep -E '^(reverse-search-history|beginning-of-line|unix-line-discard|yank-last-arg) ' | sed 's/ can be found on / → /' | cut -c1-70"),
    dict(key='alias', name='Alias table', sub='in the shell', why='Short names.', how='First word swap.', impl='Interactive by default.', used='Daily.',
         cmd="bash -c 'shopt expand_aliases'; bash -i -c 'shopt expand_aliases' 2>/dev/null | tail -1"),
    dict(key='mem', name='History list', sub='in memory', why='Recall.', how='HISTSIZE lines.', impl='Per shell.', used='↑, !, Ctrl+R.',
         setup=HI, cmd="cd ~/hi; printf '%s\\n' one two three > h.txt; history -r h.txt; history | wc -l"),
    dict(key='file', name='~/.bash_history', sub='on disk', why='Survives logout.', how='Written at exit.', impl='Text file.', used='grep.',
         cmd="grep -E '^(HISTSIZE|HISTFILESIZE)' /etc/skel/.bashrc"),
], hint='From your keyboard to the history file. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Ctrl+R search, and alias expansion</h2>
''' + two + s1 + dx + qc('Two terminals are open. You close the first, then the second. Whose history is in ~/.bash_history?', 'With histappend (Ubuntu default): both, appended. Without it: only the last terminal closed, overwriting the other.') + '''
</section>
'''

VAR = variations('Variations on aliases and history. Aliases are switched on with shopt -s expand_aliases because these run as scripts.', [
    ('Alias variations', [
        dict(title='Alias with a pipe', setup="rm -rf ~/sz; mkdir -p ~/sz/logs ~/sz/data ~/sz/tmp; head -c 300000 /dev/zero > ~/sz/data/big.bin; head -c 90000 /dev/zero > ~/sz/logs/app.log; head -c 2000 /dev/zero > ~/sz/tmp/x", cmd="shopt -s expand_aliases\nalias biggest='du -s ~/sz/* | sort -rn | head -3'\nbiggest | awk '{print $2}' | sed 's|.*/||'", why='An alias can hold a whole pipeline.'),
        dict(title='Alias that chains commands', cmd="shopt -s expand_aliases\nalias mkcd_demo='mkdir -p demo && cd demo'\nmkcd_demo; pwd | sed 's|.*/||'", why='&& inside an alias; to pass the folder name as an argument, use a function (12.10).'),
        dict(title='Overriding a command safely', cmd="shopt -s expand_aliases\nalias df='df -h'\ndf / | head -1\ncommand df / | head -1", why='The alias adds -h; command df bypasses it.'),
        dict(title='Why aliases cannot take middle arguments', cmd="shopt -s expand_aliases\nalias greet='echo Hello, and welcome'\ngreet Riya\ngreetf(){ echo \"Hello $1, and welcome\"; }; greetf Riya", why='Arguments always go at the end of an alias; a function puts them anywhere.'),
    ]),
    ('History variations', [
        dict(title='Search a history file by date', cmd="printf '%s\\n' '#1794370000' 'df -h' '#1794373600' 'systemctl restart app' > h.txt\nHISTTIMEFORMAT='%F %H:%M ' ; history -r h.txt; history | grep restart | sed 's/^ *//'", why='With timestamps you can answer “when did I restart it?”.'),
        dict(title='Ignore some commands', cmd="HISTIGNORE='ls:pwd'\nprintf '%s\\n' ls pwd 'df -h' > h.txt; history -r h.txt; history | sed 's/^ *//'", why='HISTIGNORE applies to new entries you type; history -r loads all lines, so here all three appear. In your terminal ls and pwd would not be saved.'),
        dict(title='Count commands per day of work', cmd="printf '%s\\n' 'git pull' 'make' 'git push' 'make' 'make' > h.txt\nawk '{print $1}' h.txt | sort | uniq -c | sort -rn", why='Your history is data: find what to alias.'),
        dict(title='Clear and check', cmd="printf '%s\\n' a b > h.txt; history -r h.txt; history -c; history | wc -l", why='history -c empties the list in memory (the file is untouched).'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Aliases and history at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['k=kubectl', 'gs=git status'], 'blue', 8.6), '1. Developers and DevOps',
              'Teams share alias sets: k for kubectl, gs for git status, dcu for docker compose up.', ['Type less', '*alias', 'ship']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Ctrl+R', 'incidents'], 'red', 8.6), '2. On-call',
    'During an incident, Ctrl+R recovers last month’s exact fix command in seconds.', ['Alert', '*Ctrl+R', 'fix']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['HISTTIMEFORMAT', 'dates'], 'green', 8.6), '3. Change records',
    'Timestamped history helps write the change log: what was run, and when.', ['Work', '*history', 'report']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['space prefix', 'secrets'], 'amber', 8.6), '4. Security hygiene',
    'With ignorespace, commands that must contain a token are typed with a leading space so they are not saved.', ['Token', '*" cmd"', 'not saved']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['.inputrc', 'readline'], 'violet', 8.6), '5. Database consoles',
    'mysql, psql and python use the same readline keys and history: learn them once.', ['Learn', '*Ctrl+R', 'everywhere']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='What is ll?', scenario='Alias, builtin or file?', cmd=SA + "alias ll='ls -lh'\ntype ll cd ls", explain='type.'),
    dict(level='b', title='Your aliases', scenario='List them.', cmd=SA + "alias ll='ls -lh' gs='git status'\nalias", explain='alias.'),
    dict(level='i', title='Top 3 commands', scenario='What do you type most?', setup=HI, cmd="printf '%s\\n' 'ls' 'cd /tmp' 'ls' 'git status' 'ls' 'git status' > ~/hi/.hist\nawk '{print $1}' ~/hi/.hist | sort | uniq -c | sort -rn | head -3", explain='Candidates for aliases.'),
    dict(level='i', title='Date alias that works', scenario='Single quotes.', cmd=SA + "alias today='date +%F'\ntoday | grep -cE '^[0-9]{4}-'", explain='Evaluated each time.'),
    dict(level='a', title='Alias with sudo', scenario='Make aliases work after sudo.', cmd=SA + "alias ll='ls -ld'\nalias sudo='sudo '\nsudo ll /root", explain='A trailing space makes bash check the next word too.'),
], extra=build_up('a better .bashrc', 'Riya builds her personal additions in a test file and checks them in an interactive shell.', AL, [
    ("cd ~/al; printf '%s\\n' \"alias ll='ls -lh'\" \"alias ..='cd ..'\" > my.rc; cat my.rc", '1. Two aliases.'),
    ("cd ~/al; printf '%s\\n' 'HISTSIZE=10000' 'HISTCONTROL=ignoreboth' \"HISTTIMEFORMAT='%F %T '\" >> my.rc; tail -3 my.rc", '2. History settings.'),
    ("cd ~/al; bash -n my.rc && echo 'syntax ok'", '3. Check it.'),
    ("cd ~/al; bash --rcfile my.rc -i -c 'alias ll; echo $HISTCONTROL' 2>/dev/null | tail -2", '4. Load it in an interactive shell.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Repeat the last command', '!! / ↑', 'No typing.', 'Retyping it.'),
    ('Find an old command', 'Ctrl+R', 'Fast.', 'Scrolling with ↑ 200 times.'),
    ('Shortcut with arguments at the end', 'alias', 'Simple.', 'A script.'),
    ('Shortcut with logic or middle args', 'function', 'Flexible.', 'Complex alias.'),
    ('Fix a typo', '^old^new', 'One step.', 'Editing the whole line.'),
    ('Keep a secret out', ' cmd (space)', 'Not saved.', 'Typing passwords at all.'),
]) + keys('Handy shortcuts.', [
    ('Ctrl+A / Ctrl+E', 'start / end of line', 'move'),
    ('Ctrl+U / Ctrl+K', 'cut to start / end', 'delete'),
    ('Ctrl+W / Alt+D', 'cut word before / after', 'delete'),
    ('Ctrl+Y', 'paste what you cut', 'yank'),
    ('Ctrl+R / Ctrl+G', 'search / cancel', 'history'),
    ('Alt+.', 'insert last argument', 'reuse'),
    ('Ctrl+L', 'clear screen', 'tidy'),
    ('Ctrl+C / Ctrl+D', 'cancel / exit (EOF)', 'control'),
]) + scriptit('alias-report.sh', 'A small check for a .bashrc: list its aliases, warn about double-quoted ones that contain $ (evaluated too early) and about aliases that hide standard commands.',
'''f=${1:-$HOME/.bashrc}
grep -E "^alias " "$f" | while read -r line; do
  name=${line#alias }; name=${name%%=*}
  echo "alias: $name"
  case $line in *'="'*'$'*) echo "  WARNING: double quotes with \\$ (expanded once, when defined)";; esac
  [ -x "/usr/bin/$name" ] && echo "  NOTE: hides /usr/bin/$name (use \\\\$name for the real one)"
done''',
'<p>Run on riya’s default Ubuntu .bashrc.</p>', expect='any') + puzzle_answer('Aliases are expanded only in interactive shells; a script runs with <code>expand_aliases</code> off, so <code>rm *.tmp</code> inside cleanup.sh is the real rm. Relying on the alias is dangerous because the same habit (typing rm and waiting for a question) deletes files without warning on any other machine, in scripts, under sudo or as root. Use <code>rm -i</code> explicitly when you want to be asked, and keep backups.') + qc('Which key inserts the last argument of the previous command while you are typing?', '<kbd>Alt</kbd>+<kbd>.</kbd> (press again for older ones).') + '''
</section>
'''

_sh.run_sh('rm -rf ~/al ~/hi', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-bash-startup-files-bashrc-bash-profile/">Lesson 12.2</a> (where .bashrc fits).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
