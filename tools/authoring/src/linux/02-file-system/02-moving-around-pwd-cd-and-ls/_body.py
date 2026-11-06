import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

cmap = concept_map(
    [('2.1', 'The Linux tree', 'what lives where'), ('1.6', 'Command, options, arguments', 'reading a command line')],
    ['pwd: where am I?', 'cd: go anywhere (~, .., -, /)', 'ls and its 12 most useful options', 'reading ls -l column by column', 'symlinked folders: pwd vs pwd -P'],
    [('2.3', 'Paths', 'absolute vs relative'), ('2.4', 'File types', 'what ls -l’s first letter means'), ('9.1', 'Permissions', 'the rwx columns'), ('10.2', 'Links', 'what current -> app means')],
    'pwd, cd and ls are the three commands you will type most in your whole career.')

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 290, 124, ['$ cd /var/log/nginx', '$ ls', ('access.log  error.log  error.log.1', 'out'), '$ cd ../../..', '$ pwd', ('/', 'acc'), '$ # lost again...', ('', 'dim')], title='riya@app-01', prompt='riya@app-01$')
      + t(340, 36, 'Riya’s first hour:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(340, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• goes deep into folders', '• climbs back with ../../..', '• ends up at / by mistake', '• cannot find the newest log', '• types long paths again and again'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Lost in the tree</h2>
  <div class="story">
''' + puzzle('Riya runs <code>cd logs</code> inside a script, and the script’s next commands work inside <code>logs</code>. But when the script ends, her terminal is still in the old folder. Why didn’t the script move her shell? (Hint: think about who remembers the “current folder”.)') + '''
    <p class="narration">Now that Riya knows the map, she has to move around it. On app-01 she jumps into <code>/var/log/nginx</code>, climbs out with <code>../../..</code>, overshoots to <code>/</code>, and cannot tell which log file is the newest. Kabir watches for two minutes and then shows her three tricks.</p>
''' + scene('A terminal where Riya goes into /var/log/nginx, climbs too far with ../../.. and ends at /, next to her list of problems.', sc,
            'Three commands do 90% of moving around: <tspan font-weight="700" class="s-acc">pwd, cd and ls</tspan>.') + '''
K> Riya, <code>cd</code> alone takes you home. <code>cd -</code> takes you back to where you just were. And <code>ls -lt</code> puts the newest file on top.
R> That would have saved me ten minutes! But how does Linux even know “where I am”? I never saved it anywhere.
A> The kernel keeps a <b>current working directory</b> for every running program, including your shell. <code>pwd</code> asks for it, <code>cd</code> changes it, and <code>ls</code> lists what is there. Every file name you type without a <code>/</code> at the start is looked up from that folder.
K> And <code>ls -l</code> looks scary at first, but every column means something simple.
A> Today we master all three: every useful option, what <code>ls -l</code> really tells you column by column, and what happens behind the screen when you <code>cd</code>.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
mall = ('<div class="scene"><svg viewBox="0 0 640 200" role="img" aria-label="Moving around a mall: the You are here sticker is pwd, walking to another shop is cd, looking through the shop window is ls.">'
        + label_box(20, 20, 180, 64, ['“You are here” sticker', 'pwd'], 'acc', 9.6) + label_box(230, 20, 180, 64, ['Walk to another shop', 'cd'], 'blue', 9.6) + label_box(440, 20, 180, 64, ['Look through the window', 'ls'], 'green', 9.6)
        + arrow(202, 52, 228, 52, 'ink3', 1.8) + arrow(412, 52, 438, 52, 'ink3', 1.8)
        + t(110, 110, 'Where am I right now?', 9, 'ink2') + t(320, 110, 'Go there: cd shoes', 9, 'ink2') + t(530, 110, 'What is inside?', 9, 'ink2')
        + t(320, 150, 'Shortcuts: cd alone = go home · cd .. = one floor up · cd - = back to the last shop', 9.4, 'acc', bold=True)
        + '<text x="632" y="194" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Moving around at four depths', [
    ('v', 'No jargon: a mall with a map', '''      <p>Imagine walking around a big mall.</p>''' + mall + '''
      <ul>
        <li><code>pwd</code> is the “You are here” sticker on the map.</li>
        <li><code>cd</code> is walking to another shop (folder).</li>
        <li><code>ls</code> is looking through the shop window to see what is inside.</li>
        <li>You are always standing in exactly one place. Everything you ask for is found from where you stand, unless you give the full address.</li>
      </ul>'''),
    ('b', 'The everyday moves', '''      <ul>
        <li><code>pwd</code> prints the full path of the current folder: <code>/home/riya/projects</code>.</li>
        <li><code>cd folder</code> goes into a folder; <code>cd ..</code> goes up one level; <code>cd</code> or <code>cd ~</code> goes home; <code>cd /</code> goes to the top; <code>cd -</code> goes back to the previous folder.</li>
        <li><code>ls</code> lists names; <code>ls -l</code> adds details; <code>ls -a</code> includes hidden names (starting with a dot); <code>ls -h</code> shows sizes like 4.0K.</li>
        <li><code>ls folder</code> lists another folder without going there.</li>
      </ul>'''),
    ('i', 'ls like a professional', '''      <ul>
        <li>Combine options: <code>ls -lah</code> (long, all, human sizes) is the most typed form on servers.</li>
        <li>Sorting: <code>-t</code> by time (newest first), <code>-S</code> by size, <code>-r</code> reverses. <code>ls -ltr</code> puts the newest file <b>last</b>, right above your prompt, ideal for logs.</li>
        <li><code>-d</code> shows a folder itself, not its contents (<code>ls -ld /etc</code>); <code>-R</code> lists recursively; <code>-1</code> one name per line; <code>-F</code> adds markers: <code>/</code> folder, <code>@</code> link, <code>*</code> executable.</li>
        <li><code>-A</code> is like <code>-a</code> but hides <code>.</code> and <code>..</code>; <code>-i</code> shows inode numbers (Lesson 10.1).</li>
        <li>Colours (blue folders, cyan links, green executables) come from <code>--color=auto</code>, usually set as an alias in <code>~/.bashrc</code>.</li>
      </ul>'''),
    ('a', 'What really happens: chdir, PWD and symlinks', '''      <ul>
        <li>The current directory belongs to the <b>process</b> and is kept by the kernel. <code>cd</code> calls the <code>chdir()</code> system call, which is why <code>cd</code> must be a shell <b>builtin</b>: a separate program could only change its own directory.</li>
        <li>Child processes inherit the directory; a script that does <code>cd</code> changes only its own copy, not your terminal’s.</li>
        <li>bash also keeps the variables <code>PWD</code> and <code>OLDPWD</code>; <code>cd -</code> uses <code>OLDPWD</code>.</li>
        <li>Through a symbolic link, <code>pwd</code> shows the <b>logical</b> path you typed (<code>/srv/app/current</code>); <code>pwd -P</code> shows the <b>physical</b> path (<code>/srv/app/releases/2026-11-05</code>). Deployment tools rely on this.</li>
        <li><code>ls -l</code> gets each detail from the file’s <b>inode</b> through the <code>statx()</code> system call; only the name comes from the directory itself.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>pwd, cd and ls</h2>
''' + def_block(
    'Every process has a <b>current working directory</b>, maintained by the kernel, from which relative path names are resolved. <code>pwd</code> (print working directory) prints the absolute path of the shell’s current working directory. <code>cd</code> (change directory) is a shell builtin that changes it using the <code>chdir()</code> system call. <code>ls</code> (list) lists the entries of a directory and, with options such as <code>-l</code>, their attributes read from each file’s inode.',
    'You are always “in” one folder. <code>pwd</code> tells you which, <code>cd</code> moves you, <code>ls</code> shows what is there.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Current working directory', f'The folder you are in now. {gl("current-working-directory", "Glossary →")}'),
    ('Home (~)', f'Your own folder, /home/&lt;you&gt;. {gl("home-and", "Glossary →")}'),
    ('. and ..', f'This folder and the parent folder. {gl("and", "Glossary →")}'),
    ('Hidden file', f'A name starting with a dot. {gl("hidden-file-dotfile", "Glossary →")}'),
    ('ls -l columns', f'Type and permissions, links, owner, group, size, time, name. {gl("ls-l-columns", "Glossary →")}'),
    ('Builtin', f'A command inside the shell itself (cd, pwd). {gl("builtin-vs-external-command", "Glossary →")}'),
    ('Symbolic link', f'A pointer to another path, shown as name -> target. {gl("symbolic-soft-link", "Glossary →")}'),
    ('OLDPWD', 'The variable where bash remembers the previous folder, used by <code>cd -</code>.'),
]) + '\n' + names('Three tiny names you will type thousands of times.', [
    ('pwd', 'print working directory', '“Where am I working?”'),
    ('cd', 'change directory', 'Move to another folder.'),
    ('ls', 'list', 'List what is in a folder.'),
    ('-l', 'long', 'Long listing: one line of details per file.'),
    ('-a', 'all', 'Show hidden names too.'),
    ('-h', 'human-readable', 'Sizes as 4.0K, 2.3M, 1.1G.'),
    ('-t / -S / -r', 'time / Size / reverse', 'Sort by time, by size, or the other way round.'),
    ('~', 'tilde = home', 'cd ~ (or just cd) goes home.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Go home', '<code>cd</code> or <code>cd ~</code>'),
    ('Go back to the previous folder', '<code>cd -</code> (prints where you landed)'),
    ('Up one level / two levels', '<code>cd ..</code> / <code>cd ../..</code>'),
    ('Most-typed ls on servers', '<code>ls -lah</code>; for logs <code>ls -ltr</code> (newest last)'),
    ('Folder itself, not its contents', '<code>ls -ld /etc</code>'),
    ('Why cd is a builtin', 'Only the process itself can change its own current directory'),
]) + '\n' + lv + didyou('Your shell is not the only program with a current directory: <b>every</b> process has one, and you can see it. <code>ls -l /proc/$$/cwd</code> shows your shell’s, and <code>ls -l /proc/&lt;PID&gt;/cwd</code> shows any program’s, which helps when a server process writes files “somewhere” and nobody knows where.') + '''
EXAM> “Explain pwd, cd and ls with examples” → one-line definition each; cd forms (cd, cd ~, cd .., cd -, cd /path); ls options -l -a -h -t -r -S -R -d; explain the 7 columns of ls -l; state that cd is a builtin because it changes the shell’s own working directory.
''' + qc('You are in <code>/home/riya/projects/site</code>. What does <code>cd ../..</code> followed by <code>pwd</code> print?', '<code>/home/riya</code>: each <code>..</code> goes up one level (site → projects → riya).') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Every way to use cd, and the ls options worth knowing</h2>
''' + table(['cd form', 'Goes to', 'Example'], [
    ['<code>cd folder</code>', 'A folder inside the current one', '<code>cd projects</code>'],
    ['<code>cd /path</code>', 'An absolute path, from the top', '<code>cd /var/log</code>'],
    ['<code>cd</code> or <code>cd ~</code>', 'Your home folder', '<code>/home/riya</code>'],
    ['<code>cd ~user</code>', 'Another user’s home', '<code>cd ~kabir</code>'],
    ['<code>cd ..</code>', 'The parent folder', 'one level up'],
    ['<code>cd -</code>', 'The previous folder (and prints it)', 'toggle between two places'],
    ['<code>cd "my folder"</code>', 'A name with spaces', 'quotes keep it one argument'],
], minw=520) + '''
''' + table(['ls option', 'Meaning', 'Use it when'], [
    ['<code>-l</code>', 'long listing', 'you need size, owner, time, permissions'],
    ['<code>-a</code> / <code>-A</code>', 'all (also hidden) / all except . and ..', 'looking for .bashrc, .env, .git'],
    ['<code>-h</code>', 'human-readable sizes', 'with -l: 4.0K, 2.3M'],
    ['<code>-t</code>', 'sort by modification time, newest first', 'finding the latest file'],
    ['<code>-r</code>', 'reverse order', '<code>-ltr</code>: newest at the bottom'],
    ['<code>-S</code>', 'sort by size, largest first', 'what takes space?'],
    ['<code>-d</code>', 'the folder itself, not its contents', '<code>ls -ld /etc</code>'],
    ['<code>-R</code>', 'recursive (all sub-folders)', 'small trees only'],
    ['<code>-1</code>', 'one name per line', 'feeding names to other commands'],
    ['<code>-F</code>', 'markers: / folder, @ link, * executable', 'no colours available'],
    ['<code>-i</code>', 'inode numbers', 'hard links (Lesson 10.1)'],
], minw=560) + '''
''' + didyou('<code>ls -ltr</code> is a sysadmin favourite for a practical reason: on a long listing the newest file appears on the <b>last</b> line, right next to your prompt, so you do not have to scroll up.') + qc('Which ls command shows hidden files with human-readable sizes in long format?', '<code>ls -lah</code> (or <code>ls -l -a -h</code>).') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A professional’s routine on an unfamiliar server</h2>
''' + stepper([
    ('1. Where did I land?', '<p><code>pwd</code> right after logging in. Usually your home, <code>/home/&lt;you&gt;</code>.</p>', 'Behind the screen: the login process set the shell’s working directory to the home folder from /etc/passwd.'),
    ('2. What is here, including hidden files?', '<p><code>ls -la</code></p>', 'Behind the screen: ls reads the directory entries, then the inode of each name for the details.'),
    ('3. Jump to where the work is', '<p><code>cd /var/log/app</code> (use Tab to complete each part).</p>', 'Behind the screen: bash calls chdir(); the kernel checks you have execute (x) permission on every folder in the path.'),
    ('4. Find the newest file', '<p><code>ls -ltr</code>: the last line is the newest.</p>', 'Behind the screen: ls sorts by the modification time (mtime) stored in each inode.'),
    ('5. Pop back and forth', '<p><code>cd /etc/app</code> to check the config, then <code>cd -</code> to return to the logs.</p>', 'Behind the screen: bash saved the previous folder in OLDPWD.'),
    ('6. Go home when done', '<p><code>cd</code> on its own.</p>', 'Behind the screen: with no argument, cd uses the HOME variable.'),
]) + qc('After <code>cd /etc</code> and then <code>cd /var/log</code>, what does <code>cd -</code> do?', 'It returns to <code>/etc</code> (and prints <code>/etc</code>).') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
see = [term(20, 18, 320, 130, ['riya@app-01:~$ pwd', ('/home/riya', 'out')], title='riya@app-01: ~') + t(180, 172, 'Riya starts at home.', 9, 'ink2'),
       term(20, 18, 320, 130, ['riya@app-01:~$ cd /var/log/nginx', 'riya@app-01:/var/log/nginx$ '], title='riya@app-01: /var/log/nginx', cursor=True) + t(180, 172, 'cd: the prompt shows the new folder.', 9, 'ink2'),
       term(20, 18, 320, 130, ['riya@app-01:/var/log/nginx$ ls -ltr', ('-rw-r----- ... Nov  4 error.log.1', 'out'), ('-rw-r----- ... Nov  5 access.log', 'out'), ('-rw-r----- ... Nov  5 error.log', 'acc')], title='riya@app-01: /var/log/nginx') + t(180, 172, 'ls -ltr: newest file last.', 9, 'ink2'),
       term(20, 18, 320, 130, ['riya@app-01:/var/log/nginx$ cd /etc/nginx', 'riya@app-01:/etc/nginx$ cd -', ('/var/log/nginx', 'acc')], title='riya@app-01: /var/log/nginx') + t(180, 172, 'cd - jumps back and prints where.', 9, 'ink2'),
       term(20, 18, 320, 130, ['riya@app-01:/var/log/nginx$ cd', 'riya@app-01:~$ pwd', ('/home/riya', 'out')], title='riya@app-01: ~') + t(180, 172, 'cd alone: home again.', 9, 'green', bold=True)]
def cwd(path, hl, note2):
    o = label_box(10, 14, 130, 36, ['bash process', 'PID 2144'], 'acc' if 'b' in hl else 'card', 8.6)
    o += label_box(170, 14, 180, 36, ['kernel: current dir', path], 'blue' if 'k' in hl else 'card', 8.4)
    o += arrow(142, 32, 168, 32, 'ink3', 1.6)
    o += label_box(10, 64, 340, 30, ['bash variables:  ' + note2], 'card', 8.2)
    return o
behind = [cwd('/home/riya', 'k', 'PWD=/home/riya') + t(180, 128, 'The kernel stores each process’s current directory.', 8.6, 'ink2'),
          cwd('/var/log/nginx', 'bk', 'PWD=/var/log/nginx  OLDPWD=/home/riya') + t(180, 122, 'cd calls chdir("/var/log/nginx").', 8.6, 'acc', bold=True) + t(180, 138, 'The kernel checks x permission on /, var, log, nginx.', 8.6, 'ink2'),
          cwd('/var/log/nginx', 'k', 'PWD=/var/log/nginx') + t(180, 122, 'ls is a child process: it inherits this directory,', 8.6, 'ink2') + t(180, 138, 'reads entries, then each inode (statx) for details.', 8.6, 'ink2'),
          cwd('/var/log/nginx', 'bk', 'PWD=/var/log/nginx  OLDPWD=/etc/nginx') + t(180, 128, 'cd - = cd "$OLDPWD", and bash prints it.', 8.6, 'acc', bold=True),
          cwd('/home/riya', 'bk', 'PWD=/home/riya  (from HOME)') + t(180, 128, 'cd with no argument uses $HOME.', 8.6, 'green', bold=True)]
two = anim_two('cd, ls -ltr, cd -', 'Who remembers where you are?', 'A terminal: pwd at home, cd into /var/log/nginx, ls -ltr, cd to /etc/nginx and back with cd -, then cd home.',
               'The kernel’s per-process current directory and bash’s PWD and OLDPWD variables changing at each step.', see, behind,
               ['<code>pwd</code> prints <code>/home/riya</code>, where every login starts.',
                '<code>cd /var/log/nginx</code>. The prompt now shows the folder.',
                '<code>ls -ltr</code> lists the logs, oldest first, so the newest is on the last line. (Shortened.)',
                'She checks the config in <code>/etc/nginx</code>, then <code>cd -</code> brings her straight back.',
                '<code>cd</code> on its own: home.'],
               ['The kernel keeps a current directory for every process. Right now bash’s is <code>/home/riya</code>.',
                'bash’s <code>cd</code> asks the kernel to change it (<code>chdir</code>); bash also updates its PWD and OLDPWD variables.',
                '<code>ls</code> runs as a child process, starts in the same directory, and reads the directory and each file’s inode.',
                '<code>cd -</code> is short for “cd to OLDPWD”. That is why it can toggle between two places.',
                'With no argument, cd goes to <code>$HOME</code>. A script’s cd changes only the script’s own process, never your terminal’s.'])

# scenario 1: toggling with cd -
t1 = term(14, 14, 332, 100, ['~$ cd /var/log/app', '/var/log/app$ ls -ltr | tail -1', ('... 10:42 app.log', 'out')], title='riya@app-01', size=7.8) + cap('Riya reads the newest log…', '', 'card', y=150, h=34)
t2 = term(14, 14, 332, 100, ['/var/log/app$ cd /etc/app', '/etc/app$ grep timeout app.conf', ('timeout=5', 'acc')], title='riya@app-01', size=7.8) + cap('…checks a setting in the config…', '', 'blue', y=150, h=34)
t3 = term(14, 14, 332, 100, ['/etc/app$ cd -', ('/var/log/app', 'acc'), '/var/log/app$ grep -c timeout app.log', ('37', 'out')], title='riya@app-01', size=7.8) + cap('…and cd - takes her straight back to the logs.', '', 'blue', y=150, h=34)
t4 = term(14, 14, 332, 100, ['/var/log/app$ cd -', ('/etc/app', 'acc'), '/etc/app$ cd -', ('/var/log/app', 'acc')], title='riya@app-01', size=7.8) + cap('Again and again: no long paths retyped.', '', 'green', y=150, h=34)
t5 = (t(180, 30, 'Moving fast', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• cd -  toggles between two folders', '• Tab completes every part of a path', '• cd  alone goes home', '• pushd / popd keep a stack of places (help pushd)'])) + cap('Fewer keystrokes, fewer typos.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'Logs here, config there: cd - to the rescue',
              'Debugging means jumping between a log folder and a config folder dozens of times. Values are examples.',
              'Toggling with cd -', 'Riya alternates between /var/log/app and /etc/app using cd -.', [t1, t2, t3, t4, t5],
              ['In <code>/var/log/app</code> Riya looks at the newest log line.',
               'She goes to <code>/etc/app</code> to check the timeout setting.',
               '<code>cd -</code> returns her to the log folder and prints its name, so she knows where she is.',
               'Each <code>cd -</code> swaps the two places. No long paths, no mistakes.',
               'Combine with Tab completion and you rarely type a full path by hand.'],
              hid='scenario-cdminus')

# scenario 2: ls -ltr to find the newest file
l1 = term(14, 14, 332, 106, ['$ ls', ('app.log      app.log.2.gz  app.log.4.gz', 'out'), ('app.log.1    app.log.3.gz  debug.log', 'out')], title='riya@app-01', size=7.8, prompt='riya@app-01:/var/log/app$') + cap('Plain ls sorts by name: which file is newest?', '', 'card', y=150, h=34)
l2 = term(14, 14, 332, 106, ['$ ls -l', ('... Nov  1 app.log.4.gz', 'out'), ('... Nov  5 app.log', 'out'), ('... Nov  5 debug.log', 'out')], title='riya@app-01', size=7.8, prompt='riya@app-01:/var/log/app$') + cap('ls -l shows dates, but still in name order.', '', 'card', y=150, h=34)
l3 = term(14, 14, 332, 106, ['$ ls -lt | head -3', ('total 41M', 'dim'), ('... Nov  5 10:42 debug.log', 'acc'), ('... Nov  5 10:41 app.log', 'out')], title='riya@app-01', size=7.8, prompt='riya@app-01:/var/log/app$') + cap('ls -lt: newest first. debug.log is the latest.', '', 'blue', y=150, h=34)
l4 = term(14, 14, 332, 106, ['$ ls -lhS | head -2', ('total 41M', 'dim'), ('... 38M Nov  5 debug.log', 'err')], title='riya@app-01', size=7.8, prompt='riya@app-01:/var/log/app$') + cap('ls -lhS: biggest first. debug.log is also huge!', '', 'red', y=150, h=34)
l5 = (t(180, 30, 'Sorting answers questions', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• newest?  ls -lt  (or -ltr: newest last)', '• biggest? ls -lhS', '• oldest?  ls -ltr | head', '• Lesson 7.1: find for whole folder trees'])) + cap('Same listing, three different questions.', '', 'green', y=150, h=34))
s2 = anim_one('Real-time scenario 2', 'Which log is the newest, and which is the biggest?',
              'A log folder with rotated files. Plain ls cannot answer the two questions that matter; two options can. Dates and sizes are examples.',
              'Sorting a listing', 'Plain ls, ls -l, ls -lt and ls -lhS on a folder of rotated logs.', [l1, l2, l3, l4, l5],
              ['Plain <code>ls</code> sorts alphabetically, so the newest file is not obvious.',
               '<code>ls -l</code> adds dates, but the order is still by name.',
               '<code>ls -lt</code> sorts by modification time: newest first.',
               '<code>ls -lhS</code> sorts by size with human units: the debug log is 38 MB.',
               'Choose the sort for your question. For whole folder trees, Lesson 7.1 uses find.'],
              hid='scenario-sort')

# scenario 3: deployment symlink, pwd vs pwd -P
d1 = label_box(14, 20, 150, 50, ['/srv/shop/releases/', '2026-11-04 · 2026-11-05'], 'card', 8.4) + label_box(196, 20, 150, 50, ['/srv/shop/current', '→ releases/2026-11-05'], 'acc', 8.4) + cap('Many teams deploy each release to its own folder,', 'and point a link called current at the live one.', 'card', y=150, h=44)
d2 = term(14, 14, 332, 100, ['$ cd /srv/shop/current', '$ pwd', ('/srv/shop/current', 'out')], title='deploy@web-01', size=7.8, prompt='deploy@web-01$') + cap('pwd shows the logical path you typed.', '', 'blue', y=150, h=34)
d3 = term(14, 14, 332, 100, ['$ pwd -P', ('/srv/shop/releases/2026-11-05', 'acc')], title='deploy@web-01', size=7.8, prompt='deploy@web-01$') + cap('pwd -P shows the physical folder behind the link.', '', 'blue', y=150, h=34)
d4 = label_box(14, 20, 150, 50, ['bad release?', 'repoint the link'], 'red', 8.6) + label_box(196, 20, 150, 50, ['current', '→ releases/2026-11-04'], 'green', 8.6) + arrow(166, 45, 194, 45, 'acc', 2.2) + cap('Rollback = point current at the previous release.', 'One quick change; no files copied.', 'green', y=150, h=44)
d5 = (t(180, 30, 'Why this matters', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Logical vs physical paths explain “which version runs?”', '• ls -l current shows: current -> releases/…', '• Links are covered fully in Lesson 10.2'])) + cap('pwd -P tells you where you really are.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Which release is live? pwd vs pwd -P',
              'A common deployment pattern uses a symbolic link named <code>current</code>. Folder names and dates are examples.',
              'Logical and physical paths', 'Releases in dated folders, a current link, and pwd vs pwd -P inside it, then a rollback by repointing the link.', [d1, d2, d3, d4, d5],
              ['Each release goes into a dated folder; a link <code>current</code> points to the live one.',
               'Inside the link, <code>pwd</code> prints <code>/srv/shop/current</code>: the path as you typed it.',
               '<code>pwd -P</code> resolves the link: you are really in <code>releases/2026-11-05</code>.',
               'If the new release is broken, the team points <code>current</code> back to the previous folder. Instant rollback.',
               'Knowing logical vs physical paths answers “which version is actually running?” during incidents.'],
              hid='scenario-symlink')

dx = dissect('Layer by layer: dissect one line of <code>ls -l</code>',
    'Take the line <code>-rw-r--r-- 1 riya riya 13 Nov  5 18:41 notes.txt</code> and open each column: what it means, why it exists, where ls really gets it from, and where you will use it. Each comes with the real <code>stat</code> value for the same file (recorded on our build machine).', [
    dict(key='type', name='-rw-r--r--', sub='type + permissions',
         why='You must know at a glance what a name is (file, folder, link) and who may read or change it.',
         how='The first character is the type (<code>-</code> file, <code>d</code> folder, <code>l</code> link). Then three groups of rwx: owner, group, others.',
         impl='The mode field of the file’s inode.', used='Every “Permission denied” you will ever fix (Module 9).',
         setup="echo 'chai at 4:30' > notes.txt", cmd="stat -c '%A  (octal %a)' notes.txt"),
    dict(key='links', name='1', sub='hard-link count',
         why='One file can have several names; the system must know when the last name is gone.',
         how='Counts directory entries pointing to this inode. Folders show 2 or more (their own . and each child’s ..).',
         impl='The link-count field of the inode.', used='Understanding hard links and why a deleted file may still exist (Module 10).',
         setup="echo 'chai at 4:30' > notes.txt", cmd="stat -c '%h' notes.txt"),
    dict(key='owner', name='riya riya', sub='owner and group',
         why='Permissions need someone to apply to: one owner user and one group.',
         how='The inode stores numbers (UID, GID); ls turns them into names using /etc/passwd and /etc/group.',
         impl='uid and gid fields of the inode.', used='chown, chgrp, shared team folders (Modules 8 and 9).',
         setup="echo 'chai at 4:30' > notes.txt", cmd="stat -c 'user %U (UID %u), group %G (GID %g)' notes.txt"),
    dict(key='size', name='13', sub='size in bytes',
         why='To know how big a file is, and to find space hogs.',
         how='The exact byte count: “chai at 4:30” is 12 characters plus a newline. <code>-h</code> turns large numbers into K, M, G.',
         impl='The size field of the inode (for folders: the size of the directory listing itself, often 4096).', used='Disk-full investigations, checking downloads.',
         setup="echo 'chai at 4:30' > notes.txt", cmd="stat -c '%s bytes' notes.txt"),
    dict(key='time', name='Nov  5 18:41', sub='last modification',
         why='Finding the newest log, the file someone just changed, or a stale backup.',
         how='The time the content last changed (mtime). Files older than about six months show the year instead of the time.',
         impl='The mtime field of the inode; <code>stat</code> also shows access and change times (Lesson 2.4).', used='<code>ls -lt</code>, backups, “what changed last night?”.',
         setup="echo 'chai at 4:30' > notes.txt", cmd="stat -c '%y' notes.txt"),
    dict(key='name', name='notes.txt', sub='the name',
         why='Humans need names; the system works with inode numbers.',
         how='The name is stored in the <b>directory</b>, not in the inode: a directory is a list of name → inode pairs.',
         impl='A directory entry; <code>ls -i</code> shows the inode number next to the name.', used='Renaming is cheap: only the directory entry changes (Lesson 10.1).',
         setup="echo 'chai at 4:30' > notes.txt", cmd='ls -i notes.txt'),
], hint='One ls -l line, seven pieces of information. Click a column.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Moving around, and who keeps track</h2>
  <p>Left: Riya’s terminal (outputs shortened). Right: the kernel’s current directory and bash’s PWD and OLDPWD.</p>
''' + two + '''
  <p>Three real-time scenarios: toggling with cd -, sorting a listing to answer questions, and logical vs physical paths in a deployment.</p>
''' + s1 + s2 + s3 + dx + qc('In <code>ls -l</code>, where does the file’s <b>name</b> come from, and where do all the other columns come from?', 'The name comes from the directory entry; every other column comes from the file’s inode.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>pwd, cd and ls at work</h2>
''' + usecase(term(8, 14, 104, 62, [('$ ls -ltr | tail -3', 'prompt'), ('... error.log', 'acc')], title='support', size=6.4, step=12),
              '1. Support: “send me the latest log”', 'Support engineers run <code>ls -ltr</code> in a log folder to pick the newest file before reading it.', ['Ticket', '*ls -ltr', 'right log']) + '\n' + usecase(
    term(8, 14, 104, 62, [('$ ls -la', 'prompt'), ('.env  .git', 'acc')], title='dev', size=6.4, step=12),
    '2. Developers: hidden project files', 'Projects keep important hidden files (<code>.git</code>, <code>.env</code>, <code>.gitignore</code>). <code>ls -la</code> is the first thing to type in a new repository.', ['New repo', '*ls -la', 'see .env/.git']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['current →', 'release'], 'acc', 8.6), '3. Deployments with a current link',
    'Release tools deploy into dated folders and switch a <code>current</code> link; <code>pwd -P</code> and <code>ls -l</code> show what is really live.', ['Deploy', '*switch link', 'rollback ready']) + '\n' + usecase(
    term(8, 14, 104, 62, [('cd /opt/app || exit 1', 'prompt')], title='script', size=6.4, step=12),
    '4. Safe scripts', 'Scripts write <code>cd /opt/app || exit 1</code>, so that if the folder is missing the script stops instead of running commands in the wrong place.', ['Script', '*cd … || exit', 'no accidents']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['ls -lhS', 'biggest first'], 'red', 8.6), '5. Quick space checks',
    'Before deeper analysis, <code>ls -lhS</code> in a folder shows the biggest files in a second.', ['Space alert', '*ls -lhS', 'big file found']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Moving and listing, the professional way. All were really run on our Ubuntu build machine.', [
    dict(level='b', title='Where am I, and what is here (hidden too)?', scenario='First thing on any new machine or folder.',
         setup="mkdir -p proj && touch proj/app.py proj/.env proj/.gitignore", cmd='cd proj && pwd && ls -A', files_note='a project folder with hidden files.',
         explain='<code>-A</code> shows hidden names but not <code>.</code> and <code>..</code>. <code>&amp;&amp;</code> runs each step only if the previous one worked.'),
    dict(level='b', title='Only the folders, please', scenario='A folder has hundreds of files; you want just its sub-folders.',
         setup='mkdir -p data/{raw,clean,reports} && touch data/a.csv data/b.csv', cmd='ls -d data/*/', files_note='a data folder with 3 sub-folders and 2 files.',
         explain='The pattern <code>*/</code> matches only folders; <code>-d</code> lists them instead of their contents.'),
    dict(level='i', title='The newest file, by name only', scenario='A script needs the name of the latest export file.',
         setup='mkdir -p exports && for d in 01 02 03; do touch -d "2026-11-$d" exports/sales_2026-11-$d.csv; done', cmd='ls -t exports | head -1', files_note='three daily export files with different dates.',
         explain='<code>-t</code> sorts newest first; <code>head -1</code> keeps one. (Fine for simple names; Lesson 7.1 shows a safer find-based version.)'),
    dict(level='a', title='Where is this process working?', scenario='A program writes files to a mystery folder. Find its current directory without stopping it.',
         cmd='ls -l /proc/$$/cwd',
         explain='<code>$$</code> is your shell’s PID; <code>/proc/&lt;PID&gt;/cwd</code> is a link to that process’s current directory. Replace <code>$$</code> with any program’s PID.'),
], extra=build_up('the three biggest files in a folder', 'The downloads folder is huge. Grow the command step by step until it answers exactly the question.',
    'mkdir -p dl && head -c 900000 /dev/zero > dl/movie.mp4 && head -c 300000 /dev/zero > dl/setup.zip && head -c 50000 /dev/zero > dl/photo.jpg && head -c 2000 /dev/zero > dl/notes.txt', [
    ('ls dl', 'Just the names: no sizes.'),
    ('ls -l dl', 'Sizes in bytes, but in name order.'),
    ('ls -lhS dl', 'Biggest first, in human units.'),
    ('ls -lhS dl | head -4', 'The header line “total” plus the three biggest. Done.'),
])) + which('Moving and listing situations.', [
    ('Go home from anywhere', 'cd', 'No argument = $HOME.', 'Typing /home/riya every time.'),
    ('Go back to where you were', 'cd -', 'Uses OLDPWD and prints it.', 'Climbing with ../../.. and getting lost.'),
    ('See hidden files', 'ls -la', 'Shows .bashrc, .env, .git.', 'Concluding a file is missing.'),
    ('Find the newest file', 'ls -ltr', 'Newest on the last line.', 'Reading dates in name order.'),
    ('Find the biggest files', 'ls -lhS', 'Largest first, human sizes.', 'Using ls -l and comparing numbers by eye.'),
    ('Details of a folder itself', 'ls -ld /var/log', 'Shows the folder’s own line.', '<code>ls -l /var/log</code> lists its contents instead.'),
    ('Where is a link really?', 'pwd -P', 'Physical path behind symlinks.', 'Trusting pwd inside a linked folder.'),
    ('Move safely in a script', 'cd /opt/app || exit 1', 'Stops if the folder is missing.', 'Plain cd, then rm in the wrong folder.'),
]) + puzzle_answer('Because the current directory belongs to each <b>process</b>, and a script runs as a separate child process. Its <code>cd</code> changes the script’s own directory (the kernel keeps one per process); your terminal’s shell is a different process and keeps its own. That is exactly why <code>cd</code> must be built into the shell: an external <code>cd</code> program could never change your shell’s directory. To change your shell’s folder from a file, run it with <code>source file</code> instead (Lesson 12.5).') + qc('Your prompt shows <code>~/projects$</code>. What does <code>~</code> stand for, and what full path does <code>pwd</code> print for user riya?', '<code>~</code> is your home folder; pwd prints <code>/home/riya/projects</code>.') + '''
</section>
'''

body = (cmap + story.replace('  <div class="story">', before('<a href="../01-everything-is-a-file-the-linux-directory/">Lesson 2.1</a>: the Linux tree and what each top-level folder is for.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
