import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# a fake home with every startup file announcing itself; HOME=~/sf makes bash read them
SF = r"""rm -rf ~/sf; mkdir -p ~/sf; cd ~/sf
for f in .bash_profile .bash_login .profile .bashrc .bash_logout; do echo "echo \"  read: $f\"" > "$f"; done"""
QUIET = " 2>/dev/null | grep -v -E 'administrator|sudo_root|^$'"

HOOK = hook('Riya adds <code>export PATH="$HOME/bin:$PATH"</code> and a handy alias in her terminal. Next morning: gone. She puts them in <code>~/.bashrc</code>: they work in new terminals, but not when she logs in over SSH. Her colleague puts the same lines in <code>~/.bash_profile</code>: SSH works, new terminal windows do not. Bash reads different <b>startup files</b> for different kinds of shells: <b>login</b> shells (SSH, console, <code>su -</code>) read <code>/etc/profile</code> and the first of <code>~/.bash_profile</code>, <code>~/.bash_login</code>, <code>~/.profile</code>; <b>interactive non-login</b> shells (a new terminal tab) read <code>~/.bashrc</code>; scripts read none; and <code>~/.bash_logout</code> runs when a login shell exits.',
    ['tell login, interactive non-login and non-interactive shells apart, and check which one you are in',
     'know exactly which file each one reads, and in what order: /etc/profile, /etc/profile.d, ~/.bash_profile, ~/.bash_login, ~/.profile, /etc/bash.bashrc, ~/.bashrc, ~/.bash_logout',
     'make settings permanent the right way, reload them with <code>source</code>, and use the standard “.profile sources .bashrc” pattern',
     'set system-wide settings for all users, and debug startup files that break logins'])
ROAD = roadmap([
    ('story', 'The story', 3, 'gone next morning'),
    ('decide', 'Which file when?', 2, 'the quick chart'),
    ('definition', 'Startup files', 6, 'simple meaning + 4 depths'),
    ('types', 'Login vs non-login', 5, 'the order, side by side'),
    ('commands', 'Startup files by field', 14, 'real runs'),
    ('animation', 'See it happen', 4, 'what bash reads'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a permanent setup'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which file? (decide in 5 seconds)', [
    ('Aliases, prompt, functions for you', '~/.bashrc', 'every interactive terminal'),
    ('PATH and exports for you', '~/.profile (or ~/.bash_profile)', 'login; and it sources .bashrc'),
    ('Something to run at logout', '~/.bash_logout', 'login shells only'),
    ('PATH for every user', '/etc/profile.d/myapp.sh', 'not /etc/profile itself'),
    ('Aliases for every user', '/etc/bash.bashrc', 'interactive shells'),
    ('Defaults for NEW users', '/etc/skel/', 'copied by useradd -m'),
    ('Apply changes now', 'source ~/.bashrc', 'or open a new terminal'),
    ('Settings for a service', 'systemd Environment= (17.3)', 'services read no dotfiles'),
])

cmap = concept_map(
    [('12.1', 'Variables', 'export and PATH'), ('8.2', 'useradd', '/etc/skel'), ('11.1', 'source vs run', 'same shell')],
    ['login, interactive and non-interactive shells', 'the files and their order', '~/.bash_profile → ~/.bash_login → ~/.profile', '~/.bashrc, /etc/bash.bashrc, ~/.bash_logout', 'source, /etc/profile.d and /etc/skel'],
    [('12.3', 'Aliases and history', 'what goes in .bashrc'), ('12.5', 'First script', 'scripts read no dotfiles'), ('17.4', 'cron', 'its tiny environment'), ('16.6', 'SSH', 'login shells')],
    'Put exports in the login file (.profile), interactive settings in .bashrc, and make the login file source .bashrc.')

sc = (term(20, 14, 316, 156, ['$ ssh riya@web01', ('  read: /etc/profile', 'out'), ('  read: ~/.bash_profile', 'acc'), '$ bash        # a new terminal', ('  read: ~/.bashrc', 'acc'), '$ exit; exit', ('  read: ~/.bash_logout', 'out')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Which file runs?', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• login (SSH, su -):', '  profile files', '• new terminal:', '  .bashrc', '• script: none'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Gone next morning</h2>
  <div class="story">
''' + puzzle('Riya’s server has both <code>~/.bash_profile</code> (made by an old tool, it only sets JAVA_HOME) and <code>~/.profile</code> (Ubuntu’s default, which loads her .bashrc). She adds her aliases to <code>~/.bashrc</code>. In a terminal tab they work. Over SSH they are missing, and so is the colourful prompt. Why, and what is the one-line fix?') + '''
    <p class="narration">Riya makes every startup file print its name, to see who reads what.</p>
''' + scene('A terminal: an SSH login reads /etc/profile and ~/.bash_profile; a new bash reads ~/.bashrc; logging out runs ~/.bash_logout.', sc,
            'Different kinds of shell read <tspan font-weight="700" class="s-acc">different files</tspan>.') + '''
K> Why not one file for everything?
A> History. A <b>login</b> shell starts your whole session once (SSH, console, <code>su -</code>): it is the place for environment variables that every program inherits. An <b>interactive non-login</b> shell is every extra terminal you open: it needs aliases, prompt and functions, which are <b>not</b> inherited. Scripts need neither and must stay predictable.
R> So where do I put things?
A> Exports in <code>~/.profile</code> (login), interactive things in <code>~/.bashrc</code>, and make the login file <b>source</b> .bashrc so login shells get both. Ubuntu’s default .profile already does. Today you will watch bash read each file.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="An office: arriving at the building (login) you pass reception and get your badge (profile files, exports); every time you sit at a desk (new terminal) you arrange your desk (bashrc: aliases, prompt); leaving (logout) you clear the desk (bash_logout).">'
       + label_box(14, 20, 190, 110, ['arrive (login)', 'reception: badge', '/etc/profile', '~/.profile: exports'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['sit at a desk', '(new terminal)', '~/.bashrc:', 'aliases, prompt'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['leave (logout)', '~/.bash_logout:', 'clear screen,', 'clean up'], 'amber', 8.6)
       + t(320, 160, 'Badge once per visit; desk set-up every time you sit down.', 9.6, 'ink2')
       + t(320, 182, 'Scripts are robots: no reception, no desk.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Startup files at four depths', [
    ('v', 'No jargon: arrive, sit, leave', '      <p>Three moments, three kinds of files.</p>' + pic),
    ('b', 'What you will do every day', '''      <ul>
        <li>Add aliases and your prompt to <code>~/.bashrc</code>.</li>
        <li>Add <code>export</code> lines (PATH, JAVA_HOME) to <code>~/.profile</code> (or ~/.bash_profile).</li>
        <li>After editing: <code>source ~/.bashrc</code> (or open a new terminal).</li>
        <li>Never delete these files blindly; copy fresh ones from <code>/etc/skel</code>.</li>
      </ul>'''),
    ('i', 'The rules', '''      <ul>
        <li><b>Login shell</b>: <code>/etc/profile</code> (which runs <code>/etc/profile.d/*.sh</code>), then the <b>first one that exists</b> of <code>~/.bash_profile</code>, <code>~/.bash_login</code>, <code>~/.profile</code>. On exit: <code>~/.bash_logout</code>.</li>
        <li><b>Interactive non-login</b>: <code>/etc/bash.bashrc</code> (Debian/Ubuntu; <code>/etc/bashrc</code> on RHEL), then <code>~/.bashrc</code>.</li>
        <li><b>Non-interactive</b> (scripts, <code>bash -c</code>, cron): none, except the file named in <code>$BASH_ENV</code>.</li>
        <li>Check: <code>shopt -q login_shell && echo login</code>; <code>[[ $- == *i* ]] && echo interactive</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: how bash decides', '''      <ul>
        <li>bash is a login shell if <code>argv[0]</code> starts with <code>-</code> (that is how login, sshd and <code>su -</code> start it: <code>ps</code> shows <code>-bash</code>) or with <code>--login</code>/<code>-l</code>.</li>
        <li>Interactive = stdin and stderr are terminals and no <code>-c</code>, or <code>-i</code> given. <code>$-</code> then contains <code>i</code>.</li>
        <li>GUI terminals (GNOME Terminal) start non-login shells; your desktop session’s login read ~/.profile once.</li>
        <li>SSH with a command (<code>ssh host cmd</code>) is non-login and non-interactive, yet bash still reads ~/.bashrc because it detects sshd. That is why the Ubuntu .bashrc starts with “If not running interactively, don’t do anything”.</li>
        <li><code>sh</code>/dash login shells read only /etc/profile and ~/.profile, not the bash files; that is why exports belong in ~/.profile.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Bash startup files</h2>
''' + def_block(
    '<b>Startup files</b> are shell scripts that bash runs automatically. A <b>login shell</b> runs <code>/etc/profile</code> and the first readable file among <code>~/.bash_profile</code>, <code>~/.bash_login</code> and <code>~/.profile</code>, and runs <code>~/.bash_logout</code> when it exits. An <b>interactive non-login shell</b> runs <code>/etc/bash.bashrc</code> and <code>~/.bashrc</code>. Non-interactive shells run none of them.',
    'Login = profile files once per session; every terminal = .bashrc; logout = .bash_logout.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Login shell', 'The first shell of a session (SSH, console, su -).'),
    ('Interactive shell', 'One you type into.'),
    ('Non-interactive shell', 'A script or bash -c.'),
    ('Dotfile', 'A hidden config file in your home (.bashrc).'),
    ('source / .', 'Run a file in the current shell.'),
    ('/etc/profile.d', 'Drop-in files for all users.'),
    ('/etc/skel', 'Template files for new users.'),
    ('$-', 'Current shell options (i = interactive).'),
]) + '\n' + names('Where the names come from.', [
    ('.bashrc', 'bash run commands', 'rc = run commands (1965).'),
    ('.profile', 'profile', 'Bourne shell, 1979.'),
    ('.bash_profile', 'bash’s own profile', 'Read before .profile.'),
    ('.bash_login', 'csh-style name', '.login in csh.'),
    ('.bash_logout', 'at logout', 'Login shells only.'),
    ('skel', 'skeleton', 'Template home folder.'),
    ('source', 'read and run', 'Same as the dot command.'),
    ('-bash', 'login marker', 'Leading dash in ps.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Aliases', '<code>~/.bashrc</code>'),
    ('Exports', '<code>~/.profile</code>'),
    ('Logout', '<code>~/.bash_logout</code>'),
    ('All users', '<code>/etc/profile.d/*.sh</code>'),
    ('Reload', '<code>source ~/.bashrc</code>'),
    ('Login shell?', '<code>shopt login_shell</code>'),
]) + '\n' + lv + didyou('Only the <b>first</b> of ~/.bash_profile, ~/.bash_login and ~/.profile is read. Creating an empty ~/.bash_profile silently switches off your Ubuntu ~/.profile, and with it the line that loads ~/.bashrc in login shells.') + '''
EXAM> “Which file is executed when a user logs out?” → <code>~/.bash_logout</code> (for login shells).
''' + qc('You open a new terminal tab in Ubuntu’s desktop. Which of your files runs?', '~/.bashrc (it is an interactive non-login shell), after /etc/bash.bashrc.') + mistake('Put export PATH=… in ~/.bashrc only',
    'Exports in ~/.profile; aliases/prompt/functions in ~/.bashrc; and ~/.profile sources ~/.bashrc',
    'Programs started from your desktop or by a login (not from a terminal) never read .bashrc, so they miss the PATH. Exports are inherited, so setting them once at login is enough.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Login vs non-login, and the reading order</h2>
''' + table(['Shell kind', 'Started by', 'Files read (in order)'], [
    ['Interactive login', 'console login, SSH, <code>su -</code>, <code>bash -l</code>', '/etc/profile → /etc/profile.d/*.sh → first of ~/.bash_profile, ~/.bash_login, ~/.profile'],
    ['… at exit', '<code>exit</code>, <code>logout</code>, Ctrl+D', '~/.bash_logout'],
    ['Interactive non-login', 'new terminal tab, <code>bash</code>, <code>su</code> (no dash)', '/etc/bash.bashrc → ~/.bashrc'],
    ['Non-interactive', 'scripts, <code>bash -c</code>, cron', 'none (only $BASH_ENV)'],
    ['sh / dash login', '<code>sh -l</code>, dash as login shell', '/etc/profile → ~/.profile'],
], minw=560) + table(['File', 'Who', 'Put here'], [
    ['/etc/profile', 'all users, login', 'nothing (edit profile.d instead)'],
    ['/etc/profile.d/*.sh', 'all users, login', 'system-wide PATH, JAVA_HOME'],
    ['/etc/bash.bashrc', 'all users, interactive', 'system-wide aliases, prompt'],
    ['~/.bash_profile', 'you, login (if it exists)', 'exports; then source ~/.bashrc'],
    ['~/.profile', 'you, login (if no .bash_profile)', 'exports; sources ~/.bashrc (Ubuntu default)'],
    ['~/.bashrc', 'you, every terminal', 'aliases, functions, prompt, history settings'],
    ['~/.bash_logout', 'you, login exit', 'clear screen, clean temp files'],
    ['/etc/skel/', 'new users', 'default dotfiles copied by useradd -m'],
], minw=520) + table(['', 'su USER', 'su - USER'], [
    ['Shell kind', 'non-login', 'login'],
    ['Reads', '~/.bashrc of USER', 'profile files of USER'],
    ['Environment', 'keeps yours (mostly)', 'clean, USER’s own'],
    ['Folder', 'stays where you were', 'USER’s home'],
], minw=380) + qc('Ubuntu has no ~/.bash_profile by default. Which file does an SSH login read?', '~/.profile (after /etc/profile), which in turn sources ~/.bashrc.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Startup files explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine. To see which files bash reads without touching the real ones, we made a test home <code>~/sf</code> where each of .bash_profile, .bash_login, .profile, .bashrc and .bash_logout only prints its own name, and ran bash with <code>HOME=~/sf</code>. (The two-line “To run a command as administrator…” message printed by Ubuntu’s /etc/bash.bashrc is filtered out.)</p>
''' + cmdcard_u(['knowing which files your shell read', 'debugging “works in terminal, not over SSH”'],
               ['assuming every shell reads .bashrc'])(
    'kinds', 'bash -l · bash -i · $- · shopt', 'which kind of shell?',
    '<code>bash -l</code> (--login) starts a login shell, <code>bash -i</code> an interactive one. Inside, <code>shopt login_shell</code> says on/off, <code>$-</code> contains <code>i</code> when interactive, and <code>ps</code> shows a login shell as <code>-bash</code>.',
    'bash [-l] [-i] [-c CMD]   ·   shopt login_shell   ·   echo $-', 'safe',
    [('bash -l', 'login shell', 'test profile files'),
     ('bash -i', 'interactive', 'test .bashrc'),
     ('bash -c', 'non-interactive', 'like a script'),
     ('shopt login_shell', 'on / off', 'check'),
     ('echo $-', 'i = interactive', 'check'),
     ('ps -o args= -p $$', '-bash = login', 'check')],
    dict(setup=SF, cmd="cd ~/sf\necho '--- login + interactive:'; HOME=~/sf bash -l -i -c 'echo running'" + QUIET + "\necho '--- interactive only:'; HOME=~/sf bash -i -c 'echo running'" + QUIET + "\necho '--- script (bash -c):'; HOME=~/sf bash -c 'echo running'", note='Login read .bash_profile (only the first found); a plain interactive shell read .bashrc; a script read nothing.'),
    [('sys', [
        dict(situation='Only the first profile file is used.', setup=SF, cmd="cd ~/sf; rm .bash_profile\nHOME=~/sf bash -l -c 'echo running'\nrm .bash_login\nHOME=~/sf bash -l -c 'echo running'",
             why='Order: .bash_profile, else .bash_login, else .profile. The others are ignored completely.')]),
     ('qa', [
        dict(situation='Am I a login shell? Am I interactive?', cmd="bash -l -c 'shopt login_shell'\nbash -c 'shopt login_shell; echo \"options: $-\"'",
             why='Scripts are neither login nor interactive ($- has no i).')]),
    ],
    anat=anatomy([('HOME=~/sf', 'arg', 'test home'), ('bash', 'cmd', 'shell'), ('-l', 'opt', 'login'), ('-i', 'opt', 'interactive')], 'A safe way to test startup files without changing yours.')
) + cmdcard_u(['making exports and aliases permanent', 'loading changes without logging out'],
               ['running the file instead of sourcing it (bash ~/.bashrc does nothing for you)'])(
    'source', 'editing dotfiles · source · .', 'make it permanent, load it now',
    'Append to the right file (<code>&gt;&gt;</code>, or edit with nano/vim), then load it into the <b>current</b> shell with <code>source FILE</code> or <code>. FILE</code>. Running it (<code>bash ~/.bashrc</code>) changes only a child process.',
    "echo 'export X=1' >> ~/.profile   ·   source ~/.bashrc", 'change',
    [('>> ~/.bashrc', 'append a line', 'aliases'),
     ('>> ~/.profile', 'append an export', 'PATH'),
     ('source FILE', 'run in this shell', 'reload'),
     ('. FILE', 'same (POSIX)', 'sh scripts'),
     ('exec bash', 'replace with a fresh shell', 'full reload'),
     ('bash FILE', 'runs in a child', 'does NOT reload')],
    dict(setup=SF, cmd="cd ~/sf; echo 'export EDITOR=nano' >> .profile\nbash .profile > /dev/null; echo \"after bash: [$EDITOR]\"\nsource .profile > /dev/null; echo \"after source: [$EDITOR]\"", note='Only source changed the current shell.'),
    [('devops', [
        dict(situation='Check for syntax errors before reloading.', setup=SF, cmd="cd ~/sf; echo 'alias ll=\"ls -l' >> .bashrc\nbash -n .bashrc; echo \"syntax check exit $?\"", expect='any',
             why='bash -n parses without running. A broken .bashrc spoils every new terminal; test it first.')]),
    ]
) + mistake('touch ~/.bash_profile   (or a tool creates one) on Ubuntu', 'Delete it, or make it source ~/.profile:  [ -f ~/.profile ] && . ~/.profile',
            'Once ~/.bash_profile exists, ~/.profile is ignored in login shells, and with it the lines that load ~/.bashrc and add ~/bin to PATH. This is the puzzle.') + cmdcard_u(['clean-up at logout', 'clearing the screen on shared consoles'],
               ['expecting it to run for terminal tabs or when the window is closed by force'])(
    'logout', '~/.bash_logout', 'runs at logout',
    'When a <b>login</b> shell exits normally (<code>exit</code>, <code>logout</code>, Ctrl+D), bash runs <code>~/.bash_logout</code>. Ubuntu’s default clears the console. Use it to clear the screen, remove temporary files or write a log line.',
    '~/.bash_logout   ·   logout', 'change',
    [('exit / logout', 'leave login shell', 'runs it'),
     ('Ctrl+D', 'end of input', 'runs it'),
     ('clear', 'wipe the screen', 'privacy'),
     ('rm -f ~/tmp/*', 'clean up', 'housekeeping'),
     ('non-login shells', 'never run it', 'tabs, scripts')],
    dict(setup=SF, cmd="cd ~/sf\necho '--- login shell, then exit:'; printf 'exit\\n' | HOME=~/sf bash -l -i" + QUIET + "\necho '--- non-login shell, then exit:'; printf 'exit\\n' | HOME=~/sf bash -i" + QUIET, note='Only the login shell ran .bash_logout.'),
    [('sec', [
        dict(situation='A logout record for a shared account.', setup=SF + "; printf 'echo \"$(date +%%F) logout $USER\" >> ~/logins.log\\n' > ~/sf/.bash_logout", cmd="cd ~/sf; printf 'exit\\n' | HOME=~/sf bash -l -i > /dev/null 2>&1\ncut -d' ' -f2- logins.log",
             why='Simple auditing; real audit trails use last and the system logs (Lesson 18.1).')]),
     ('sys', [
        dict(situation='Ubuntu’s default .bash_logout.', cmd="grep -v '^#' /etc/skel/.bash_logout | grep -v '^$'",
             why='At the last console logout (SHLVL 1) it clears the screen so the next person cannot read your work.')]),
    ]
) + cmdcard_u(['settings for every user', 'defaults for new accounts'],
               ['editing /etc/profile directly (package updates overwrite it)'])(
    'system', '/etc/profile.d · /etc/bash.bashrc · /etc/skel', 'all users',
    'For every user’s login shells, add a small file <code>/etc/profile.d/NAME.sh</code>; for every interactive shell, <code>/etc/bash.bashrc</code>. <code>/etc/skel</code> holds the dotfiles that <code>useradd -m</code> copies into each new home (Lesson 8.2).',
    'sudo tee /etc/profile.d/app.sh   ·   ls -a /etc/skel', 'danger',
    [('/etc/profile.d/x.sh', 'all logins', 'PATH, JAVA_HOME'),
     ('/etc/bash.bashrc', 'all terminals', 'aliases'),
     ('/etc/skel/', 'new users', 'defaults'),
     ('/etc/environment', 'KEY=value, no shell', 'PAM, all sessions')],
    dict(cmd="ls -A /etc/skel\nsed -n '/include .bashrc/,/fi$/p' /etc/skel/.profile | head -5", note='Ubuntu’s default .profile loads .bashrc for login shells.'),
    [('devops', [
        dict(situation='A system-wide PATH for a big-data tool.', setup="sudo rm -f /etc/profile.d/spark-demo.sh", cmd="echo 'export SPARK_HOME=/opt/spark; export PATH=\"$PATH:$SPARK_HOME/bin\"' | sudo tee /etc/profile.d/spark-demo.sh > /dev/null\nbash -l -c 'echo \"$SPARK_HOME\"; echo \"$PATH\" | tr : \"\\n\" | tail -1'\nsudo rm /etc/profile.d/spark-demo.sh",
             why='Every user’s next login gets it; nothing else to edit. Lesson 8.2: useradd copies /etc/skel.')]),
    ], sudo=True
) + undo('Startup files are plain text; a broken one can lock you out of comfortable logins, rarely more.', [
    ('Broke ~/.bashrc:', 'open a shell that skips it: <code>bash --norc</code> (or <code>bash --noprofile --norc</code>), fix the file, <code>bash -n</code> to check.'),
    ('Lost the defaults:', '<code>cp /etc/skel/.bashrc ~/</code> (and .profile).'),
    ('A .bash_profile hides .profile:', 'remove it or add <code>. ~/.profile</code> inside.'),
    ('A command in .bashrc hangs logins:', '<code>ssh host bash --norc</code> or <code>ssh -t host bash --noprofile</code>, then fix.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='source ~/nofile', meaning='The file does not exist.', fix='Check the name: ~/.bashrc has a dot.'),
    dict(cmd='bash -n broken.sh', setup="printf 'alias x=\"ls\\n' > broken.sh", meaning='A missing quote in a startup file.', fix='Close the quote; check again with bash -n.'),
    dict(cmd='logout', meaning='logout works only in a login shell.', fix='Use <code>exit</code>.'),
    dict(cmd='echo "export X=1" > /etc/profile.d/x.sh', meaning='Only root may write there.', fix='<code>echo … | sudo tee …</code>.'),
]) + qc('You changed ~/.bashrc. Name two ways to apply it to the open terminal.', '<code>source ~/.bashrc</code> (or <code>. ~/.bashrc</code>), or <code>exec bash</code>.') + '''
'''
_sh.run_sh('sudo rm -f /etc/profile.d/spark-demo.sh', 'any')
cards = cards + '</section>\n'

def flow(k):
    boxes = [('/etc/profile', 'blue'), ('~/.bash_profile', 'green'), ('~/.bashrc', 'amber'), ('~/.bash_logout', 'violet')]
    lit = [[0, 1], [2], [], [3]][k]
    o = ''
    for i, (n, tn) in enumerate(boxes):
        o += label_box(14 + i * 86, 40, 80, 40, [n, 'read' if i in lit else '—'], tn if i in lit else 'card', 7.4)
    return o
see_cmds = [['$ ssh riya@web01', ('Welcome to Ubuntu', 'out')], ['$ bash', ('(a new interactive shell)', 'out')], ['$ ./script.sh', ('script output', 'out')], ['$ exit', ('logout', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['A login.', 'A new terminal.', 'A script.', 'Leaving.'])]
behind = [flow(k) + t(180, 110, n, 8.6, 'violet', bold=True) for k, n in enumerate(['Login: /etc/profile, then the first profile file.', 'Non-login: ~/.bashrc only.', 'Script: no startup file at all.', 'Login shell exit: ~/.bash_logout.'])]
two = anim_two('What bash reads', 'Behind the screen: one file per moment',
               'A terminal: SSH login, then a new bash, then a script, then exit.',
               'Four file boxes: /etc/profile and ~/.bash_profile light up at login, ~/.bashrc for a new shell, none for a script, ~/.bash_logout at exit.', see, behind,
               ['Login.', 'New shell.', 'Script.', 'Logout.'],
               ['profile files', '.bashrc', 'nothing', '.bash_logout'])

def first(k):
    files = ['~/.bash_profile', '~/.bash_login', '~/.profile']
    exists = [[1, 1, 1], [0, 1, 1], [0, 0, 1], [1, 0, 1]][k]
    chosen = exists.index(1)
    o = ''
    for i, f in enumerate(files):
        tn = 'green' if i == chosen else ('card' if exists[i] else 'red')
        o += label_box(14 + i * 112, 40, 104, 40, [f, 'READ' if i == chosen else ('ignored' if exists[i] else 'missing')], tn, 7.6)
    return o
frames = [first(0) + t(180, 110, 'All three exist: only .bash_profile is read.', 8.6, 'violet', bold=True),
          first(1) + t(180, 110, 'No .bash_profile: .bash_login is read.', 8.6, 'violet', bold=True),
          first(2) + t(180, 110, 'Only .profile: Ubuntu’s default.', 8.6, 'green', bold=True),
          first(3) + t(180, 110, 'The puzzle: an extra .bash_profile hides .profile!', 8.6, 'red', bold=True)]
s1 = anim_one('Animated example', 'The first profile file wins',
              'bash reads exactly one of three files at login.',
              'first file wins', 'Three file boxes: the first existing one is read and the rest ignored; an extra .bash_profile hides .profile.', frames,
              ['All three.', 'No profile.', 'Only .profile.', 'The trap.'], hid='scenario-first')

dx = dissect('Layer by layer: from login to your prompt',
    'Each layer has a real command and output from our build machine.', [
    dict(key='sys', name='/etc/profile', sub='all users, login', why='System defaults.', how='Runs profile.d.', impl='Shell script.', used='Every login.',
         cmd="grep -n 'profile.d' /etc/profile | head -2"),
    dict(key='user', name='~/.profile', sub='your login', why='Your exports.', how='First found wins.', impl='From /etc/skel.', used='PATH.',
         cmd="grep -n -E 'bin|bashrc' /etc/skel/.profile | head -4"),
    dict(key='rc', name='~/.bashrc', sub='every terminal', why='Aliases, prompt.', how='Interactive only.', impl='Starts with a guard.', used='Daily.',
         cmd="sed -n '/If not running interactively/,/esac/p' /etc/skel/.bashrc"),
    dict(key='kind', name='Shell kind', sub='login? interactive?', why='Decides files.', how='argv[0] -bash, $-.', impl='shopt login_shell.', used='Debugging.',
         cmd="bash -l -c 'shopt -q login_shell && echo login'; bash -i -c 'echo \"options: $-\"' 2>/dev/null | tail -1"),
], hint='From the system file to the shell’s own flags. Click a layer.')

hd = hood('Under the hood: bash opens the files in order', 'The real file opens of a login shell started with <code>HOME=~/sf bash -l -c true</code> on our build machine.',
          "env HOME=/home/riya/sf bash -l -c true", setup=SF, show='profile|bash_|bashrc', trace='openat')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>What bash reads, and the first-file-wins rule</h2>
''' + two + s1 + dx + hd + qc('Why does the Ubuntu .bashrc stop early when “not running interactively”?', 'Some non-interactive shells (ssh host cmd) still read .bashrc; the guard keeps aliases and output out of scripts and scp.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Startup files at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['profile.d', 'JAVA_HOME'], 'blue', 8.6), '1. Big data clusters',
              'Admins drop hadoop.sh or spark.sh into /etc/profile.d so every user gets the same HOME and PATH.', ['Install', '*profile.d', 'login']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['dotfiles', 'Git repo'], 'green', 8.6), '2. Developers',
    'Many developers keep their .bashrc in a Git “dotfiles” repository and link it on every machine.', ['Clone', '*ln -s', 'same shell']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['/etc/skel', 'new users'], 'amber', 8.6), '3. Onboarding',
    'Training labs put a prepared .bashrc (prompt, aliases, welcome) into /etc/skel before creating student accounts.', ['Prepare', '*skel', 'useradd']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['.bash_logout', 'clear'], 'violet', 8.6), '4. Shared consoles',
    'Kiosks and lab machines clear the screen and remove temp files at logout.', ['Work', '*logout', 'clean']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['no dotfiles', 'services'], 'red', 8.6), '5. Services and cron',
    'Daemons and cron jobs read no startup files: their settings go in systemd units or the crontab.', ['Service', '*Environment=', 'run']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Login shell?', scenario='Check quickly.', cmd="shopt login_shell", expect='any', explain='on/off (exit 1 when off).'),
    dict(level='b', title='Your dotfiles', scenario='What exists?', cmd="ls -A /etc/skel", explain='Defaults.'),
    dict(level='i', title='Interactive?', scenario='Inside a script.', cmd="case $- in *i*) echo interactive;; *) echo 'not interactive';; esac", explain='$-.'),
    dict(level='i', title='Syntax check', scenario='Before reloading.', cmd="bash -n /etc/skel/.bashrc && echo 'syntax ok'", explain='bash -n.'),
    dict(level='a', title='Clean test shell', scenario='Ignore all startup files.', cmd="bash --noprofile --norc -c 'echo \"PS1 in a script: [$PS1]\"'", explain='Skip dotfiles.'),
], extra=build_up('a permanent setup', 'Riya makes her PATH and alias permanent in the test home and checks each shell kind.', SF + "; cd ~/sf; printf '[ -f ~/.bashrc ] && . ~/.bashrc\\n' > .profile; rm .bash_profile .bash_login; echo 'alias ll=\"ls -l\"' >> .bashrc", [
    ("cd ~/sf; echo 'export PATH=\"$HOME/bin:$PATH\"' >> .profile; tail -1 .profile", '1. The export goes into .profile.'),
    ("cd ~/sf; HOME=~/sf bash -l -i -c 'alias ll; echo \"$PATH\" | cut -d: -f1'" + QUIET, '2. Login shell: alias and PATH.'),
    ("cd ~/sf; HOME=~/sf bash -i -c 'alias ll'" + QUIET, '3. New terminal: alias (PATH is inherited).'),
], cumulative=True)) + which('Choosing the right file.', [
    ('Alias, prompt, function', '~/.bashrc', 'Every terminal.', '.bash_profile only.'),
    ('PATH, exports', '~/.profile', 'Once per login; inherited.', '.bashrc only.'),
    ('Clean-up', '~/.bash_logout', 'Login exit.', 'Expecting it on tab close.'),
    ('All users', '/etc/profile.d/x.sh', 'Survives updates.', 'Editing /etc/profile.'),
    ('New accounts', '/etc/skel', 'Copied at creation.', 'Copying by hand.'),
    ('Apply now', 'source FILE', 'Same shell.', 'bash FILE.'),
]) + keys('Handy forms.', [
    ('source ~/.bashrc', 'reload', 'after edits'),
    ('bash -n FILE', 'syntax check', 'before reload'),
    ('bash --norc', 'skip .bashrc', 'rescue'),
    ('bash -l', 'login shell', 'test profile'),
    ('shopt login_shell', 'login?', 'check'),
    ('cp /etc/skel/.bashrc ~', 'restore default', 'repair'),
]) + scriptit('whichfiles.sh', 'Report which of your startup files exist, which one a login shell will actually read, and whether it loads .bashrc.',
'''cd "${1:-$HOME}"
for f in .bash_profile .bash_login .profile .bashrc .bash_logout; do
  [ -f "$f" ] && echo "exists: $f"
done
for f in .bash_profile .bash_login .profile; do
  if [ -f "$f" ]; then echo "login reads: $f"; grep -q bashrc "$f" && echo "  and it loads .bashrc" || echo "  WARNING: it does not load .bashrc"; break; fi
done''',
'<p>Run on the test home after adding an empty .bash_profile (the puzzle).</p>', expect='any') + puzzle_answer('Because <code>~/.bash_profile</code> exists, a login shell (SSH) reads it and <b>ignores ~/.profile</b>, which is where Ubuntu loads ~/.bashrc. So aliases and the prompt are missing over SSH. Fix: add <code>[ -f ~/.profile ] &amp;&amp; . ~/.profile</code> (or <code>. ~/.bashrc</code>) to ~/.bash_profile, or move its JAVA_HOME line into ~/.profile and delete it.') + qc('Does <code>su riya</code> (without the dash) read riya’s .profile?', 'No: it starts a non-login shell, which reads ~/.bashrc. su - riya starts a login shell.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/sf ~/broken.sh', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-shell-variables-and-environment-variables-env-export-and-path/">Lesson 12.1</a> (variables, export and PATH).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
