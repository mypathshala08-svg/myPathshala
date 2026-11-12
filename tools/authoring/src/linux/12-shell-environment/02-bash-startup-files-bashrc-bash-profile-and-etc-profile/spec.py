import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='12-shell-environment', lesson='02-bash-startup-files-bashrc-bash-profile-and-etc-profile', n='12.2',
    module_label='Module 12 · The shell environment and shell programming',
    title='Bash startup files: .bashrc, .bash_profile, .profile, .bash_logout and /etc/profile',
    desc='Login, interactive non-login and non-interactive shells; the exact files and order bash reads: /etc/profile, /etc/profile.d, ~/.bash_profile, ~/.bash_login, ~/.profile, /etc/bash.bashrc, ~/.bashrc, ~/.bash_logout; first-file-wins; source vs running; su vs su -; /etc/skel; real recorded runs of each shell kind, animations, mistakes and a lab.',
    og_desc='Which Bash startup file runs when: .bashrc vs .bash_profile vs .profile vs .bash_logout, shown with real runs.',
    minutes=35, level='Beginner → Advanced',
    lead='Bash reads different startup files for login shells, new terminals and scripts. This lesson shows each one really being read, where to put exports and aliases, what .bash_logout does, and how to set things for all users.',
    chips=['Every file really traced', 'First file wins, animated', '.bash_logout', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Which shell kind am I?
shopt login_shell
case $- in *i*) echo interactive;; *) echo "not interactive";; esac
bash -l -c 'shopt login_shell'
# source runs a file in THIS shell
echo 'GREETING=namaste' > settings.sh
bash settings.sh; echo "after bash: [$GREETING]"
source settings.sh; echo "after source: [$GREETING]"
"""

RUN = dict(
    heading='Login shells and source',
    intro='<p>Check what kind of shell runs your code, and see the difference between running and sourcing a file.</p>',
    code=MAIN,
    anno=[('source settings.sh', 'Runs the lines in the current shell.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Is the runner a login shell?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which file does a login shell read here? Then run.',
             code="mkdir -p h; cd h\necho 'echo read .bash_profile' > .bash_profile\necho 'echo read .profile' > .profile\nHOME=$PWD bash -l -c true\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is to load aliases.sh into this shell. Fix the second line.',
             code="echo \"alias hi='echo hello'\" > aliases.sh\nbash aliases.sh\nalias hi 2>/dev/null || echo 'hi not defined'\n"),
        dict(label='4 · Your turn', hint='Remove .bash_profile and see which file is read now.',
             code="mkdir -p h2; cd h2\necho 'echo read .bash_login' > .bash_login\necho 'echo read .profile' > .profile\nHOME=$PWD bash -l -c true\n"),
        dict(label='5 · Challenge', hint='Check a startup file for syntax errors without running it.',
             code="printf 'alias ok=\"ls\"\\n' > good.rc\nbash -n good.rc && echo 'syntax ok'\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: your own startup files',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Which dotfiles do you have?', cmd='ls -A ~ | grep -E "^\\.(bash|profile)"', output='.bash_history\n.bash_logout\n.bashrc\n.profile', note='Typical Ubuntu user.'),
        dict(title='2 · Is this terminal a login shell?', cmd='shopt login_shell; ps -o args= -p $$', output='login_shell    \toff\nbash', note='Typical GNOME Terminal tab (non-login).'),
        dict(title='3 · Over SSH', cmd='ssh localhost "shopt login_shell"; ssh -t localhost "shopt login_shell"', output='login_shell    \toff\nlogin_shell    \ton', note='Typical: a command over SSH is non-login; an interactive SSH session is login.'),
        dict(title='4 · Defaults for new users', cmd='ls -A /etc/skel', output=pc('ls -A /etc/skel'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='source vs running, line by line',
    intro='<p>Step through: a settings file is run (nothing changes here) and then sourced (the variable arrives).</p>',
    code='''printf 'export APP=web\\nTEAM=data\\n' > app.env
bash app.env
echo "after bash: [$APP]"
source app.env
echo "after source: [$APP] [$TEAM]"
''',
    notes={2: 'Run :: in a child; its variables die with it.', 3: 'Still empty.', 4: 'Source :: lines run in this shell.', 5: 'Both arrived.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s alias, an admin’s system-wide PATH and a logout clean-up.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='A permanent alias (in a test home)',
         problem='<p>Add an alias to .bashrc and show that a new interactive shell has it.</p>',
         inp='a test home', approach=['Append to .bashrc.', 'Start bash -i with HOME set.'],
         code='''mkdir -p home1
echo "alias ll='ls -l'" >> home1/.bashrc
HOME=$PWD/home1 bash -i -c 'alias ll' 2>/dev/null | grep ll
''', notes={2: 'Append.', 3: 'A new interactive shell reads it.'}, tryit='Use bash -c (not interactive): is the alias there?'),
    dict(level='i', tag='Admin', title='Login file that also loads .bashrc',
         problem='<p>Make a login shell get both the exports and the aliases.</p>',
         inp='a test home', approach=['.profile sources .bashrc.'],
         code='''mkdir -p home2
echo "alias ll='ls -l'" > home2/.bashrc
printf 'export ROLE=admin\\n[ -f ~/.bashrc ] && . ~/.bashrc\\n' > home2/.profile
HOME=$PWD/home2 bash -l -i -c 'echo "ROLE=$ROLE"; alias ll' 2>/dev/null | grep -E 'ROLE|ll'
''', notes={3: 'The standard pattern.', 4: 'Login shell: both.'}, tryit='Remove the second line of .profile.'),
    dict(level='a', tag='Security', title='Clean up at logout',
         problem='<p>Delete a temp folder automatically when a login shell exits.</p>',
         inp='a test home', approach=['.bash_logout.', 'printf exit | bash -l -i.'],
         code='''mkdir -p home3/tmp; touch home3/tmp/draft.txt
echo 'rm -rf ~/tmp' > home3/.bash_logout
printf 'exit\\n' | HOME=$PWD/home3 bash -l -i > /dev/null 2>&1
ls home3/tmp 2>/dev/null || echo "tmp removed at logout"
''', notes={2: 'The logout file.', 3: 'A login shell exits.', 4: 'Cleaned.'}, tryit='Exit a non-login shell instead (bash -i).'),
]

QUIZ = mix([
    dict(q='A new terminal tab (non-login) reads…', options=['~/.profile', '~/.bashrc', '~/.bash_logout', 'nothing'], answer=1, why='Interactive non-login.'),
    dict(q='An SSH login reads…', options=['~/.bashrc only', '/etc/profile then the first of ~/.bash_profile, ~/.bash_login, ~/.profile', 'nothing', '/etc/skel'], answer=1, why='Login shell.'),
    dict(q='Which runs when a login shell exits?', options=['~/.bashrc', '~/.bash_logout', '/etc/profile', '~/.profile'], answer=1, why='Logout.'),
    dict(q='How do you apply ~/.bashrc changes to the open terminal?', options=['bash ~/.bashrc', 'source ~/.bashrc', 'chmod +x ~/.bashrc', 'logout'], answer=1, why='Same shell.'),
    dict(q='Where should a system-wide PATH addition go?', options=['/etc/profile.d/NAME.sh', '~/.bashrc', '/etc/skel', '/bin'], answer=0, why='Drop-in file.'),
    dict(q='Both ~/.bash_profile and ~/.profile exist. A login shell reads…', options=['both', 'only ~/.bash_profile', 'only ~/.profile', 'neither'], answer=1, why='First found wins.'),
    dict(q='A script (bash script.sh) reads…', options=['~/.bashrc', '~/.profile', 'no startup files', '/etc/profile'], answer=2, why='Non-interactive.'),
    dict(q='su - riya starts…', options=['a non-login shell', 'a login shell', 'no shell', 'a script'], answer=1, why='The dash.'),
])

REVISION = [
    'Login (SSH, console, su -): /etc/profile → /etc/profile.d → first of ~/.bash_profile, ~/.bash_login, ~/.profile; exit → ~/.bash_logout.',
    'Interactive non-login (new tab): /etc/bash.bashrc → ~/.bashrc. Scripts: none.',
    'Exports in ~/.profile, aliases/prompt/functions in ~/.bashrc, and the login file sources ~/.bashrc.',
    '<code>source FILE</code> / <code>. FILE</code> runs in this shell; <code>bash FILE</code> does not change it.',
    'All users: /etc/profile.d/*.sh and /etc/bash.bashrc; new users: /etc/skel.',
    'Check with <code>shopt login_shell</code> and <code>$-</code>; test with <code>bash -l</code>, <code>bash -i</code>, <code>bash -n</code>; rescue with <code>bash --norc</code>.',
]

FAQ = [
    ('What is the difference between .bashrc and .bash_profile?', '.bash_profile is read by login shells (SSH, console); .bashrc by interactive non-login shells (new terminals). Usually .bash_profile or .profile sources .bashrc.'),
    ('Where should I put export PATH?', 'In ~/.profile (or ~/.bash_profile), so it is set once at login and inherited.'),
    ('What is .bash_logout?', 'A file bash runs when a login shell exits, often used to clear the screen or clean up.'),
    ('How do I reload .bashrc?', 'source ~/.bashrc (or . ~/.bashrc), or exec bash.'),
    ('Why are my aliases missing over SSH?', 'The login file (.bash_profile or .profile) does not source ~/.bashrc, often because an extra ~/.bash_profile hides ~/.profile.'),
    ('How do I set environment variables for all users?', 'Create /etc/profile.d/NAME.sh with export lines (login shells), or /etc/environment for KEY=value pairs.'),
    ('What is /etc/skel?', 'The template folder whose files useradd -m copies into each new home directory.'),
]

PRACTICE_INTRO = 'Small startup-file tasks with a test HOME. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Login?', stmt='Show that bash -l is a login shell.', inp='nothing', code="bash -l -c 'shopt -q login_shell && echo login'\n", explain='-l.'),
    dict(level='easy', title='Not interactive', stmt='Show that a script is not interactive.', inp='nothing', code="bash -c 'case $- in *i*) echo yes;; *) echo no;; esac'\n", explain='No i.'),
    dict(level='easy', title='Source', stmt='Load X=5 from a file into this shell and print it.', inp='a file', code="echo X=5 > f.sh; . ./f.sh; echo $X\n", explain='Dot.'),
    dict(level='medium', title='First file', stmt='With .bash_login and .profile, which does a login shell read?', inp='test home', code="mkdir -p t1; echo 'echo .bash_login' > t1/.bash_login; echo 'echo .profile' > t1/.profile\nHOME=$PWD/t1 bash -l -c true\n", explain='.bash_login.'),
    dict(level='medium', title='bashrc', stmt='Show that an interactive shell reads .bashrc.', inp='test home', code="mkdir -p t2; echo 'echo bashrc read' > t2/.bashrc\nHOME=$PWD/t2 bash -i -c true 2>/dev/null | grep bashrc\n", explain='-i.'),
    dict(level='medium', title='Syntax', stmt='Detect the broken line in a startup file.', inp='a broken file', code="printf 'if true; then\\n' > bad.rc\nbash -n bad.rc 2>&1 | grep -c 'syntax error'\n", explain='bash -n.'),
    dict(level='business', title='Logout', stmt='Make a login shell write “bye” to a file at exit.', inp='test home', code="mkdir -p t3; echo 'echo bye > ~/out.txt' > t3/.bash_logout\nprintf 'exit\\n' | HOME=$PWD/t3 bash -l -i > /dev/null 2>&1; cat t3/out.txt\n", explain='.bash_logout.'),
    dict(level='business', title='Skip dotfiles', stmt='Start a shell that ignores .bashrc and print that it ran.', inp='test home', code="mkdir -p t4; echo 'echo SHOULD NOT PRINT' > t4/.bashrc\nHOME=$PWD/t4 bash --norc -i -c 'echo clean shell' 2>/dev/null | grep -v administrator | grep -v sudo_root | grep .\n", explain='--norc.'),
]

SCN_INTRO = 'Interview questions about startup files, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“.bashrc vs .bash_profile?”', 'A favourite question.', 'login vs non-login?',
        '''<ul>
          <li>.bash_profile: login shells (once per session).</li>
          <li>.bashrc: interactive non-login shells (each terminal).</li>
          <li>Usually the profile sources .bashrc.</li>
        </ul>''', 'saying “they are the same”.') +
    scn('Development team', 'Junior', 'Aliases work locally, not over SSH', 'Same user, same server.', 'first-file-wins?',
        '''<ol>
          <li><code>ls -a ~</code>: a .bash_profile exists.</li>
          <li>It does not source .bashrc (and hides .profile).</li>
          <li>Add <code>. ~/.bashrc</code> to it.</li>
        </ol>''', 'copying aliases into every file.') +
    scn('Big data platform', 'Mid-level', 'Every analyst needs SPARK_HOME', '50 users, new ones every month.', 'system-wide settings?',
        '''<ul>
          <li><code>/etc/profile.d/spark.sh</code> with the exports.</li>
          <li>Interactive helpers in /etc/bash.bashrc; defaults in /etc/skel.</li>
          <li>Services: set Environment= in their systemd units.</li>
        </ul>''', 'editing 50 home folders by hand.') +
    scn('Operations', 'Senior', 'A broken .bashrc blocks scp', 'scp fails with “protocol error”, ssh works.', 'why?',
        '''<ul>
          <li>bash reads .bashrc for ssh commands; anything printed corrupts the scp/sftp stream.</li>
          <li>Keep the “not interactive → return” guard at the top; never echo in .bashrc above it.</li>
          <li>Rescue: <code>ssh host bash --norc</code>.</li>
        </ul>''', 'reinstalling SSH.')
) + interview([
    ('Which file runs at logout?', '~/.bash_logout.'),
    ('How to reload .bashrc?', 'source ~/.bashrc.'),
    ('Login vs non-login shell?', 'Login starts a session (SSH, console, su -); non-login is another shell inside it.'),
    ('Where are default dotfiles for new users?', '/etc/skel.'),
    ('What does /etc/profile.d contain?', 'Scripts run by /etc/profile for every login shell.'),
    ('Do scripts read .bashrc?', 'No (unless BASH_ENV is set).'),
    ('su vs su -?', 'su - starts a login shell with the target user’s environment.'),
], [
    ('RHCSA (EX200)', 'Manage user environments; login shell behaviour.'),
    ('LFCS', 'Customize the shell environment.'),
    ('CompTIA Linux+', 'Shell startup files and environment.'),
]) + distro('The bash files are the same everywhere; system files differ.', [
    ('System login', '/etc/profile', '/etc/profile', '/etc/profile (zsh: /etc/zprofile)', '-'),
    ('System interactive', '/etc/bash.bashrc', '/etc/bashrc', '/etc/zshrc', '-'),
    ('User login default', '~/.profile', '~/.bash_profile', '~/.zprofile', 'PowerShell $PROFILE'),
    ('User interactive', '~/.bashrc', '~/.bashrc', '~/.zshrc', 'PowerShell $PROFILE'),
    ('Logout', '~/.bash_logout', '~/.bash_logout', '~/.zlogout', '-'),
]) + teaser('12.3', 'Riya’s .bashrc now loads. What should go inside? Aliases that save typing, a history that remembers 10,000 commands with dates, and keyboard shortcuts like Ctrl+R that find any old command in a second. Next: aliases, history and keyboard shortcuts.')

CHEATSHEET = cheatsheet('Startup files', [
    ('Login', [('/etc/profile', 'all users'), ('/etc/profile.d/*.sh', 'drop-ins'), ('~/.bash_profile', '1st choice'), ('~/.bash_login', '2nd'), ('~/.profile', '3rd (Ubuntu)')]),
    ('Interactive', [('/etc/bash.bashrc', 'all users'), ('~/.bashrc', 'you'), ('bash -i', 'test')]),
    ('Exit', [('~/.bash_logout', 'login exit'), ('exit / logout', 'triggers'), ('Ctrl+D', 'triggers')]),
    ('Tools', [('source / .', 'load now'), ('bash -n', 'syntax check'), ('bash --norc', 'rescue'), ('shopt login_shell', 'check'), ('/etc/skel', 'new users')]),
])

MINDMAP = mindmap('Startup', [
    ('Login', 'blue', ['/etc/profile', 'profile.d', '1st profile']),
    ('Each terminal', 'green', ['bash.bashrc', '~/.bashrc', 'aliases']),
    ('Logout', 'amber', ['.bash_logout', 'login only', 'clean up']),
    ('Load', 'violet', ['source', '. file', 'exec bash']),
    ('All users', 'red', ['profile.d', 'skel', 'bash.bashrc']),
    ('Check', 'acc', ['shopt', '$-', 'bash -n']),
])

LAB = lab('a permanent setup', 'Build the lab (a test home), do the four tasks, then run the checker. The checker starts shells with HOME=~/lab122/home.',
    setup='''mkdir -p ~/lab122 && cd ~/lab122 && rm -rf home && mkdir home
echo 'export JAVA_HOME=/opt/java' > home/.bash_profile
printf '[ -f ~/.bashrc ] && . ~/.bashrc\\n' > home/.profile''',
    tasks=['Add an alias <code>ll</code> for <code>ls -l</code> to <code>home/.bashrc</code>.',
           'Make login shells load .bashrc too (hint: .bash_profile exists, so .profile is ignored).',
           'Add <code>export PATH="$HOME/bin:$PATH"</code> to the file that login shells read.',
           'Make <code>home/.bash_logout</code> write the word <code>bye</code> into <code>home/logout.txt</code>.'],
    solution='''echo "alias ll='ls -l'" >> home/.bashrc
echo '[ -f ~/.bashrc ] && . ~/.bashrc' >> home/.bash_profile
echo 'export PATH="$HOME/bin:$PATH"' >> home/.bash_profile
echo 'echo bye > ~/logout.txt' > home/.bash_logout''',
    check='''cd ~/lab122; H=$PWD/home
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 alias"  'HOME=$H bash -i -c "alias ll" 2>/dev/null | grep -q "ls -l"'
ok "2 login"  'HOME=$H bash -l -i -c "alias ll" 2>/dev/null | grep -q "ls -l"'
ok "3 PATH"   '[ "$(HOME=$H bash -l -c "echo \\$PATH" 2>/dev/null | cut -d: -f1)" = "$H/bin" ]'
rm -f home/logout.txt; printf "exit\\n" | HOME=$H bash -l -i >/dev/null 2>&1
ok "4 logout" '[ "$(cat home/logout.txt 2>/dev/null)" = bye ]' ''')
