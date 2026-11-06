import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap
BODY = body(HERE)

META = dict(
    module='02-file-system', lesson='02-moving-around-pwd-cd-and-ls', n='2.2',
    module_label='Module 2 · The Linux file system',
    title='Moving around: pwd, cd and ls',
    desc='pwd, cd and ls explained from zero: every form of cd (~, .., -, /), the ls options that matter (-l -a -h -t -r -S -d -R -F), reading ls -l column by column, why cd is a shell builtin, PWD and OLDPWD, and pwd vs pwd -P with symbolic links. Animations, real Bash and interview questions.',
    og_desc='Never get lost in the Linux tree again: pwd, cd and ls, with what happens behind the screen.',
    minutes=30, level='Beginner → Advanced',
    lead='Riya goes deep into /var/log, climbs out with ../../.., ends up at / and still cannot find the newest log. This lesson teaches the three commands you will type most in your career: where you are (pwd), how to move (cd), and how to see what is there (ls), plus every column of ls -l and what the kernel does when you cd.',
    chips=['Story-based', '4 animations', 'Layer-by-layer', 'Real Bash in your browser'],
)

MAIN = '''# Moving around a small project
mkdir -p projects/site/css && echo "hello" > projects/site/index.html
pwd
cd projects/site
pwd
ls
ls -l index.html
cd ..
pwd
cd -
cd
pwd
ls -d lab/*/
'''

RUN = dict(
    heading='Move around and look',
    intro='<p>The script builds a tiny project, walks into it, looks, climbs out, jumps back with <code>cd -</code> and goes home. The output below was recorded on our Ubuntu build machine as user <code>riya</code>.</p>',
    code=MAIN,
    anno=[
        ('mkdir -p projects/site/css && echo "hello" > projects/site/index.html', 'Builds the folders and one file. <code>-p</code> creates parent folders as needed.'),
        ('cd projects/site', 'A relative path: looked up from the current folder.'),
        ('ls -l index.html', 'One long line: type and permissions, links, owner, group, size, time, name.'),
        ('cd ..', 'Up one level, to <code>projects</code>.'),
        ('cd -', 'Back to the previous folder; bash prints where you landed.'),
        ('cd', 'No argument: straight home.'),
        ('ls -d lab/*/', 'Only the folders inside lab; <code>-d</code> lists them, not their contents.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Follow every <code>pwd</code>: which folder is printed each time?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what does the final <code>pwd</code> print? Then run.',
             code='mkdir -p a/b/c\ncd a/b/c\ncd ../..\npwd\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the folder name has a space. Fix the cd line with quotes.',
             code='mkdir "my notes"\ncd my notes\npwd\n', expect='any'),
        dict(label='4 · Your turn', hint='Create three files, then list them newest first in long format with human sizes.',
             code='for f in one two three; do echo $f > $f.txt; sleep 1; done\nls -lht\n'),
        dict(label='5 · Challenge', hint='Prove that a script’s <code>cd</code> does not move the calling shell: run a child bash that cds to /tmp, then print pwd.',
             code='pwd\nbash -c \'cd /tmp; echo "child is in: $(pwd)"\'\necho "parent still in: $(pwd)"\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: move and list on your own Linux',
    intro='<p>Try these on your own Linux. <b>Outputs were recorded on our Ubuntu 24.04 build machine</b> unless marked typical.</p>',
    items=[
        dict(title='1 · cd and pwd are builtins', cmd='type pwd cd ls', output=pc('type pwd cd ls'),
             note='<code>ls</code> is a real program (on a laptop it is usually an alias with <code>--color=auto</code>); <code>cd</code> and <code>pwd</code> live inside bash.'),
        dict(title='2 · A folder’s own line', cmd='ls -ld /etc /tmp', output=pc('ls -ld /etc /tmp'),
             note='Notice <code>t</code> at the end of /tmp’s permissions: the sticky bit (Lesson 9.4).'),
        dict(title='3 · Your shell’s current directory, as the kernel sees it', cmd='cd /var/log; ls -l /proc/$$/cwd', output=pc('cd /var/log; ls -l /proc/$$/cwd'),
             note='<code>$$</code> is your shell’s PID. Every process has a cwd link in /proc.'),
        dict(title='4 · Coloured listing on a desktop', cmd='alias ls; ls --color=auto -F /', output="alias ls='ls --color=auto'\nbin@   dev/  home/  lib64@  mnt/  proc/  run/   srv/  tmp/  var/\nboot/  etc/  lib@   media/  opt/  root/  sbin@  sys/  usr/",
             note='Typical output on Ubuntu desktop: blue folders, cyan links. <code>-F</code> adds <code>/</code> and <code>@</code> markers, which help when colours are not shown.'),
    ],
)

TRACE = dict(
    heading='Following cd, line by line',
    intro='<p>Watch the <b>Shell</b> box: after each <code>cd</code> the variables <code>PWD</code> and <code>OLDPWD</code> change.</p>',
    code='''mkdir -p shop/logs shop/conf
cd shop/logs
echo "in: $PWD"
cd ../conf
echo "in: $PWD, before: $OLDPWD"
cd - > /dev/null
echo "back in: $PWD"
cd
echo "home: $PWD"
''',
    notes={2: 'Down :: Two levels down with one relative path.', 4: 'Sideways :: <code>..</code> up to shop, then into conf.',
           6: 'Back :: <code>cd -</code> = cd to OLDPWD. The printed path is hidden with <code>&gt; /dev/null</code>.', 8: 'Home :: No argument: cd uses $HOME.'},
)

WORKED_INTRO = 'Three real tasks: a safe directory change in a script, a quick folder report, and finding files changed today.'
EXAMPLES = [
    dict(level='b', tag='Scripts', title='Change folder safely before working',
         problem='<p>A cleanup script must work inside <code>reports</code>. If that folder is missing it must stop, not run in the wrong place.</p>',
         inp='a reports folder with two files (then a missing folder)',
         approach=['Use <code>cd folder || exit</code>: the right side runs only if cd fails.', 'Print where we are before doing anything.'],
         code='''mkdir reports && touch reports/jan.csv reports/feb.csv
cd reports || { echo "reports missing, stopping"; exit 1; }
echo "working in $(pwd)"
ls
cd /no/such/folder 2>/dev/null || echo "second cd failed safely"
''',
         notes={2: 'Guard :: <code>||</code> runs the block only when cd fails.', 5: 'Fail test :: The error is hidden; our message prints instead.'},
         tryit='Delete the first line and run: the script now stops with the message.'),
    dict(level='i', tag='Reporting', title='A one-screen folder report',
         problem='<p>Show, for a project folder: how many files, how many folders, how many hidden entries, and the biggest file.</p>',
         inp='app/ with code files, a hidden .env and two sub-folders',
         approach=['<code>ls -A</code> lists everything except . and ..', '<code>ls -p</code> marks folders with <code>/</code>, so grep can count them.', '<code>ls -S | head -1</code> gives the biggest.'],
         code='''mkdir -p app/src app/tests && echo "KEY=1" > app/.env
head -c 5000 /dev/zero > app/main.py; head -c 300 /dev/zero > app/util.py
cd app
echo "folders: $(ls -p | grep -c /)"
echo "files  : $(ls -Ap | grep -vc /)"
echo "hidden : $(ls -A | grep -c '^\\.')"
echo "biggest: $(ls -S | head -1)"
''',
         notes={4: 'Folders :: <code>-p</code> appends / to folder names.', 5: 'Files :: <code>-v</code> inverts: lines without a slash. Includes the hidden .env.', 6: 'Hidden :: Names starting with a dot.'},
         tryit='Add a hidden folder <code>.git</code>. Which counts change?'),
    dict(level='a', tag='Business problem', title='What changed most recently in a release folder?',
         problem='<p>After a failed deploy, the team wants the three most recently changed files in a release, with full time stamps, newest first.</p>',
         inp='release/ with four files changed at different times',
         approach=['<code>touch -d</code> sets sample times.', '<code>ls -lt --time-style=long-iso</code> sorts by time and shows exact dates.'],
         code='''mkdir release && cd release
touch -d "2026-11-05 09:00" app.jar
touch -d "2026-11-05 09:30" config.yml
touch -d "2026-11-04 18:00" README.md
touch -d "2026-11-05 09:45" start.sh
ls -lt --time-style=long-iso | head -4 | awk '{print $6, $7, $8}'
''',
         notes={6: 'Rank :: newest first; head keeps the header plus 3 files; awk prints date, time, name.'},
         tryit='Add <code>-r</code> to see the oldest first.'),
]

QUIZ = mix([
    dict(q='What does cd with no argument do?', options=['Nothing', 'Goes to /', 'Goes to your home folder', 'Prints the current folder'], answer=2,
         why='With no argument cd uses $HOME.'),
    dict(q='What does cd - do?', options=['Goes up one level', 'Goes to the previous folder', 'Goes to /', 'Deletes the folder'], answer=1,
         why='It goes to $OLDPWD and prints it.'),
    dict(q='Which command lists files with the newest last?', options=['ls -lt', 'ls -ltr', 'ls -lS', 'ls -la'], answer=1,
         why='-t sorts newest first; -r reverses, so the newest is on the last line.'),
    dict(q='Why is cd a shell builtin and not a separate program?', options=['It is faster', 'A separate program could only change its own directory, not the shell’s', 'For security only', 'Historical accident'], answer=1,
         why='The current directory belongs to each process; only the shell itself can change its own.'),
    dict(q='How do you see a folder’s own permissions instead of its contents?', options=['ls -l folder', 'ls -ld folder', 'ls -a folder', 'pwd folder'], answer=1,
         why='-d lists the directory itself.'),
    dict(q='In ls -l, which column is NOT read from the inode?', options=['Size', 'Owner', 'Name', 'Modification time'], answer=2,
         why='The name is stored in the directory entry; everything else comes from the inode.'),
    dict(q='Inside a symlinked folder, which command shows the real physical path?', options=['pwd', 'pwd -P', 'ls -P', 'cd -P only'], answer=1,
         why='pwd -P resolves symbolic links; plain pwd shows the logical path.'),
])

REVISION = [
    '<code>pwd</code> = where am I · <code>cd</code> = move · <code>ls</code> = what is here.',
    'cd forms: <code>cd</code>/<code>cd ~</code> home · <code>cd ..</code> up · <code>cd -</code> previous · <code>cd /path</code> absolute · quote names with spaces.',
    'ls options: <code>-l</code> long · <code>-a</code>/<code>-A</code> hidden · <code>-h</code> human · <code>-t</code> time · <code>-S</code> size · <code>-r</code> reverse · <code>-d</code> folder itself · <code>-R</code> recursive · <code>-F</code> markers.',
    'Favourites: <code>ls -lah</code>, <code>ls -ltr</code> (newest last), <code>ls -lhS</code> (biggest first).',
    'ls -l columns: type+perms, links, owner, group, size, mtime, name. All from the inode except the name (directory entry).',
    'The current directory is kept by the kernel per process; <code>cd</code> calls <code>chdir()</code>, so it must be a builtin.',
    'bash keeps <code>PWD</code> and <code>OLDPWD</code>; a script’s cd never moves your terminal.',
    '<code>pwd</code> logical vs <code>pwd -P</code> physical (through symlinks). Scripts: <code>cd dir || exit 1</code>.',
]

FAQ = [
    ('What is the difference between cd .. and cd -?', 'cd .. goes to the parent folder (one level up). cd - goes back to the previous folder you were in, wherever that was, using $OLDPWD.'),
    ('What is the difference between ls -a and ls -A?', 'Both show hidden entries. -a also shows . and .. ; -A (almost all) leaves those two out.'),
    ('Explain the output of ls -l.', 'File type and permissions, number of hard links, owner, group, size in bytes, last modification time, and name. Example: -rw-r--r-- 1 riya riya 13 Nov 5 18:41 notes.txt.'),
    ('Why is cd a built-in command?', 'The working directory is a property of each process. An external program would change only its own directory and exit; the shell must call chdir() itself.'),
    ('What is the difference between pwd and pwd -P?', 'pwd prints the logical path, including symbolic links you followed. pwd -P prints the physical path with all links resolved.'),
    ('How do you list only directories?', 'ls -d */ (the pattern matches folders only), or ls -l | grep ^d, or find . -maxdepth 1 -type d.'),
]

PRACTICE_INTRO = 'Tasks that use only pwd, cd and ls. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Where am I after this?', stmt='Create <code>x/y/z</code>, go into <code>z</code>, go up two levels and print the folder name only.', inp='x/y/z',
         code='mkdir -p x/y/z\ncd x/y/z\ncd ../..\nbasename "$(pwd)"\n', explain='z → y → x. <code>basename</code> keeps the last part of the path.'),
    dict(level='easy', title='Show hidden files', stmt='Create <code>.config</code> and <code>notes.txt</code>, then list everything except . and ..', inp='.config, notes.txt',
         code='touch .config notes.txt\nls -A\n', explain='-A shows hidden names without . and ..'),
    dict(level='easy', title='Toggle with cd -', stmt='Go to <code>/tmp</code>, then <code>/etc</code>, then use cd - and print where you are.', inp='/tmp, /etc',
         code='cd /tmp\ncd /etc\ncd - > /dev/null\npwd\n', explain='cd - returns to the previous folder, /tmp.'),
    dict(level='medium', title='Biggest file first', stmt='Create three files of 100, 2000 and 50 bytes and print just their names, biggest first.', inp='s.txt (100), m.txt (2000), t.txt (50)',
         code='head -c 100 /dev/zero > s.txt; head -c 2000 /dev/zero > m.txt; head -c 50 /dev/zero > t.txt\nls -S\n', explain='-S sorts by size, largest first.'),
    dict(level='medium', title='Only the folders', stmt='In a folder with two sub-folders and two files, list only the folders.', inp='docs/, img/, a.txt, b.txt',
         code='mkdir docs img; touch a.txt b.txt\nls -d */\n', explain='<code>*/</code> matches folders only.'),
    dict(level='medium', title='Logical vs physical', stmt='Create <code>releases/v2</code> and a link <code>current</code> pointing to it. Go into current and print both paths.', inp='current -> releases/v2',
         code='mkdir -p releases/v2\nln -s releases/v2 current\ncd current\npwd\npwd -P\n', explain='pwd shows .../current; pwd -P resolves the link to .../releases/v2.'),
    dict(level='business', title='Newest export for the dashboard', stmt='A dashboard must load the newest daily export. Given three dated files, print only the newest name.', inp='sales_01.csv, sales_02.csv, sales_03.csv with dates 1, 2, 3 Nov',
         code='mkdir exports\nfor d in 01 02 03; do touch -d "2026-11-$d" exports/sales_$d.csv; done\nls -t exports | head -1\n', explain='ls -t sorts newest first; head -1 keeps the top line.'),
    dict(level='business', title='Safe move into a work folder', stmt='A job must enter <code>/data/incoming</code>; if it is missing, print “no incoming folder” and stop with status 1. Show the status.', inp='/data/incoming (missing here)',
         code='bash -c \'cd /data/incoming 2>/dev/null || { echo "no incoming folder"; exit 1; }\'\necho "job status: $?"\n', explain='The guard stops the job; status 1 tells the scheduler it failed.'),
]

SCN_INTRO = 'Interview questions about moving around and listing, as asked for support, DevOps and developer roles.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Explain ls -l output.”',
        'The interviewer writes <code>drwxr-x--- 2 app app 4096 Nov 5 10:02 data</code> on the board and asks you to read it.',
        'can you read each column calmly?',
        '''<ul>
          <li><code>d</code>: a directory. <code>rwx</code> owner can read, write, enter; <code>r-x</code> group can read and enter; <code>---</code> others nothing.</li>
          <li><code>2</code>: hard-link count (a folder: itself and its own <code>.</code>). <code>app app</code>: owner and group.</li>
          <li><code>4096</code>: size of the directory listing itself, not its contents. Then the last modification time and the name.</li>
        </ul>''', 'saying 4096 is the size of everything inside the folder.') +
    scn('Operations · support', 'Junior', 'Find the latest log fast',
        'A service just crashed. You are in your home folder on the server. Show the last lines of the newest log in /var/log/app.',
        'do you combine cd, ls and a reading tool efficiently?',
        '''<ol>
          <li><code>cd /var/log/app &amp;&amp; ls -ltr | tail -3</code>: the newest files are at the bottom.</li>
          <li><code>tail -50 "$(ls -t | head -1)"</code>, or simply the name you saw.</li>
          <li>After checking the config (<code>cd /etc/app</code>), return with <code>cd -</code>.</li>
        </ol>''', 'opening every file with cat until one looks recent.') +
    scn('Platform team · concepts', 'Mid-level', '“My script runs cd, but my terminal didn’t move.”',
        'A teammate reports a bug: <code>./goto-project.sh</code> contains <code>cd ~/project</code> but after running it they are still in the old folder.',
        'do you understand processes and the working directory?',
        '''<ul>
          <li>The script runs in a child process; the kernel keeps a separate working directory per process. Its cd changes only itself.</li>
          <li>Fix: run it in the current shell with <code>source goto-project.sh</code> (or <code>. goto-project.sh</code>), or make it a function or alias in <code>~/.bashrc</code>.</li>
          <li>Same reason cd must be a builtin.</li>
        </ul>''', '“add sudo”.') +
    scn('DevOps · deployments', 'Mid-level', 'Which release is live?',
        'Production runs from <code>/srv/shop/current</code>. A colleague asks which release is actually running.',
        'do you understand symbolic links and logical vs physical paths?',
        '''<ul>
          <li><code>ls -l /srv/shop/current</code> shows <code>current -&gt; releases/2026-11-05</code>, or <code>readlink -f</code>.</li>
          <li>Inside it, <code>pwd -P</code> prints the physical path; plain <code>pwd</code> prints <code>.../current</code>.</li>
          <li>Rollback = repoint the link to the previous release, then restart or reload the service.</li>
        </ul>''', 'copying release folders over each other.')
) + teaser('2.3', 'Riya’s script works when she runs it from inside her project folder, but fails with “No such file or directory” when she runs it from anywhere else. Same file, same command. What changed?')

MINDMAP = mindmap('pwd, cd and ls', [
    ('pwd', 'acc', ['where am I?', 'pwd -P = physical', 'prompt shows it too']),
    ('cd moves', 'blue', ['cd = home (~)', 'cd .. = up', 'cd - = previous']),
    ('ls lists', 'green', ['-l long, -a hidden', '-h human sizes', '-d the folder itself']),
    ('Sorting', 'amber', ['-t newest first', '-S biggest first', '-r reverse (-ltr)']),
    ('ls -l columns', 'violet', ['type + perms, links', 'owner, group, size', 'mtime, name']),
    ('Behind the screen', 'red', ['kernel cwd per process', 'chdir() → builtin', 'PWD and OLDPWD']),
])
