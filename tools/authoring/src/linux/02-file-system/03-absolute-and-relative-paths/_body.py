import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

cmap = concept_map(
    [('2.1', 'The Linux tree', 'one tree from /'), ('2.2', 'pwd, cd and ls', 'you are always somewhere')],
    ['absolute vs relative paths', '~, ~user, . and ..', 'Tab completion (and double Tab)', 'how the kernel walks a path', 'scripts that work from any folder'],
    [('3.1', 'Creating files and folders', 'every command takes paths'), ('3.4', 'Wildcards', 'patterns of paths'), ('12.1', 'PATH variable', 'how commands are found'), ('17.4', 'cron', 'jobs that start somewhere else')],
    'Every file name you type is a path. Get paths right and half of all “No such file or directory” errors disappear.')

# ---------------------------------------------------------------- tree helper (shared by several pictures)
NODES = {'/': (130, 18), 'home': (80, 58), 'etc': (190, 58), 'kabir': (34, 98), 'riya': (120, 98),
         'lab': (120, 138), 'reports': (70, 178), 'data': (170, 178), 'sales.csv': (170, 218)}
EDGES = [('/', 'home'), ('/', 'etc'), ('home', 'riya'), ('home', 'kabir'), ('riya', 'lab'), ('lab', 'reports'), ('lab', 'data'), ('data', 'sales.csv')]
def tree(hl=(), you=None, path=(), tone='acc'):
    o = ''
    for a, b in EDGES:
        (x1, y1), (x2, y2) = NODES[a], NODES[b]
        on = (a, b) in path or (b, a) in path
        o += f'<line x1="{x1}" y1="{y1+11}" x2="{x2}" y2="{y2-11}" style="stroke:{FILL[tone] if on else '#8A94A0'};stroke-width:{3 if on else 1.3}"/>'
    for n, (x, y) in NODES.items():
        w = 66 if n == 'sales.csv' else 56
        o += label_box(x - w / 2, y - 11, w, 22, [n if n in ('/', 'sales.csv') else n + '/'], tone if n in hl else 'card', 8.2)
    if you:
        x, y = NODES[you]
        o += t(x + 31, y + 3, '◀ you', 8, 'blue', anchor='start', bold=True)
    return o
def side(a, b, tone='acc'):
    return t(204, 108, a, 8.6, 'ink2', anchor='start') + t(204, 124, b, 8, tone, anchor='start', bold=True)

# ---------------------------------------------------------------- 1. story
sc = (term(20, 14, 300, 124, ['~/lab/reports$ bash make.sh', ('report ready: 2 rows', 'out'), '~/lab/reports$ cd ~', '~$ bash lab/reports/make.sh', ('cat: ../data/sales.csv: No such', 'err'), ('file or directory', 'err')], title='riya@laptop', prompt='$', size=8.2)
      + t(350, 36, 'Same script, two results:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(350, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• inside reports/: works', '• from home: file “missing”', '• the file never moved', '• only her current folder did', '• the path was relative'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>“The file is right there!”</h2>
  <div class="story">
''' + puzzle('Riya’s script reads <code>../data/sales.csv</code>. Run from inside <code>~/lab/reports</code> it works; run from her home folder it says “No such file or directory”. The file has not moved. What exactly is <code>..</code> measured from, and how would you make the script work from anywhere?') + '''
    <p class="narration">Riya has written her first little report script. It works perfectly inside her <code>reports</code> folder. She proudly runs it again from her home folder to show Kabir, and it fails. The file is still there; she can see it with <code>ls</code>.</p>
''' + scene('A terminal: the script works inside the reports folder but fails from the home folder with No such file or directory.', sc,
            'A relative path is read <tspan font-weight="700" class="s-acc">from wherever you are standing</tspan>.') + '''
K> Classic! Your path starts with <code>..</code>, so it means “the folder above <b>wherever I am now</b>”. From home, that is <code>/home</code>, and there is no <code>/home/data</code>.
R> So the same path can point to different files depending on where I am?
A> Exactly. A path that starts with <code>/</code> is <b>absolute</b>: it is the full address, read from the top of the tree, and means the same thing from everywhere. Any other path is <b>relative</b>: directions from your current folder.
K> And use Tab. You type three letters, press Tab, and the shell finishes the name. No typos, and it shows you instantly if the path is wrong.
A> Today: both kinds of path, the shortcuts <code>~</code>, <code>.</code> and <code>..</code>, Tab completion, how the kernel walks a path one folder at a time, and how to write scripts that work from any folder.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
addr = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A full postal address works from anywhere; directions like two doors left of the tea shop only work if you start at the tea shop.">'
        + label_box(20, 20, 280, 70, ['Full postal address', '12 MG Road, Pune 411001, India', 'works from anywhere in the world'], 'green', 9.2)
        + label_box(340, 20, 280, 70, ['Directions', '“two doors left of the tea shop”', 'only works if you start at the tea shop'], 'amber', 9.2)
        + arrow(160, 96, 160, 124, 'ink3', 1.8) + arrow(480, 96, 480, 124, 'ink3', 1.8)
        + label_box(20, 128, 280, 46, ['Absolute path: /home/riya/lab/data/sales.csv', 'starts with /'], 'green', 9)
        + label_box(340, 128, 280, 46, ['Relative path: ../data/sales.csv', 'starts from the current folder'], 'amber', 9)
        + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Paths at four depths', [
    ('v', 'No jargon: an address vs directions', '''      <p>There are two ways to tell a friend where you live.</p>''' + addr + '''
      <ul>
        <li>A <b>full address</b> works from anywhere: that is an <b>absolute path</b>. On Linux it always starts with <code>/</code>.</li>
        <li><b>Directions</b> (“two doors left of the tea shop”) only work from one starting point: that is a <b>relative path</b>. It starts from the folder you are in.</li>
        <li><code>..</code> means “one step back up”; <code>.</code> means “right here”; <code>~</code> means “my home”.</li>
      </ul>'''),
    ('b', 'The rules', '''      <ul>
        <li>Starts with <code>/</code> → absolute: read from the root. <code>/etc/hostname</code> is the same file whoever types it, from wherever.</li>
        <li>Anything else → relative: read from the current folder. <code>notes.txt</code> means <code>$(pwd)/notes.txt</code>.</li>
        <li><code>..</code> is the parent folder, <code>.</code> the current folder, <code>~</code> your home (<code>/home/riya</code>), <code>~kabir</code> Kabir’s home.</li>
        <li>Folders are separated by <code>/</code>. Names are case-sensitive: <code>Data</code> and <code>data</code> are different.</li>
        <li><b>Tab</b> completes a name; pressing <b>Tab twice</b> lists all choices when there are several.</li>
      </ul>'''),
    ('i', 'Using paths well', '''      <ul>
        <li>Mix them: <code>~/lab/../lab/data</code> is valid; <code>realpath</code> cleans it up to a simple absolute path.</li>
        <li><code>dirname</code> and <code>basename</code> split a path into its folder and its last part; <code>basename file.csv .csv</code> also removes an extension.</li>
        <li>Names with spaces need quotes: <code>cd "My Documents"</code> or a backslash <code>cd My\\ Documents</code>. Tab adds the backslash for you.</li>
        <li><code>~+</code> is the current folder and <code>~-</code> the previous one (same as <code>$PWD</code> and <code>$OLDPWD</code>).</li>
        <li>To run a program in the current folder you must write <code>./run.sh</code>: the shell only searches <code>PATH</code> for names <b>without</b> a slash.</li>
      </ul>'''),
    ('a', 'Behind the screen: path resolution', '''      <ul>
        <li><code>~</code> is expanded by the <b>shell</b> before the command runs; the kernel never sees it. In quotes (<code>"~/lab"</code>) it is not expanded.</li>
        <li>The kernel resolves a path one component at a time (in the Linux source this is <code>fs/namei.c</code>, “name to inode”): start at <code>/</code> for absolute paths or at the process’s current directory for relative ones, then look each name up in the directory found so far.</li>
        <li>For every folder on the way you need <b>execute (x)</b> permission (“search”); otherwise “Permission denied”, even if the file itself is readable.</li>
        <li><code>.</code> and <code>..</code> are real entries in every directory; <code>/..</code> is <code>/</code> itself. Symbolic links met on the way are followed (up to 40 times, else “Too many levels of symbolic links”).</li>
        <li>Limits: a single name may be 255 bytes (<code>NAME_MAX</code>), a whole path 4096 bytes (<code>PATH_MAX</code>). Repeated slashes count as one: <code>/usr///bin</code> = <code>/usr/bin</code>.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Absolute and relative paths</h2>
''' + def_block(
    'A <b>path</b> is a sequence of names separated by <code>/</code> that identifies a file in the directory tree. An <b>absolute path</b> begins with <code>/</code> and is resolved from the root directory. A <b>relative path</b> does not begin with <code>/</code> and is resolved from the current working directory of the process. The entries <code>.</code> and <code>..</code> in every directory refer to the directory itself and to its parent; the shell expands <code>~</code> to the home directory.',
    'An absolute path is a full address from <code>/</code>; a relative path is directions from where you are now.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Path', f'The address of a file: names joined by /. {gl("path-absolute-and-relative", "Glossary →")}'),
    ('Absolute path', 'Starts with /; means the same from everywhere.'),
    ('Relative path', 'Does not start with /; read from the current folder.'),
    ('. and ..', f'This folder and the parent folder. {gl("and", "Glossary →")}'),
    ('~ (tilde)', f'Your home folder, expanded by the shell. {gl("home-and", "Glossary →")}'),
    ('Tab completion', f'The shell finishes a name for you. {gl("tab-completion", "Glossary →")}'),
    ('Current directory', f'Where relative paths start. {gl("current-working-directory", "Glossary →")}'),
    ('PATH', f'The folders searched for commands. {gl("path", "Glossary →")}'),
]) + '\n' + names('Small symbols, big meaning.', [
    ('/', 'slash; also the root', 'At the start: the top of the tree. Inside: separates folders.'),
    ('.', 'dot', 'This folder. ./run.sh = run.sh in this folder.'),
    ('..', 'dot dot', 'The parent folder, one level up.'),
    ('~', 'tilde', 'Home: /home/riya. ~kabir = /home/kabir.'),
    ('~+ / ~-', 'tilde plus / minus', 'Current / previous folder.'),
    ('realpath', 'real path', 'Prints the clean absolute path, links resolved.'),
    ('dirname', 'directory name', 'All but the last part: /a/b/c.txt → /a/b.'),
    ('basename', 'base name', 'Only the last part: /a/b/c.txt → c.txt.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Absolute', 'Starts with <code>/</code>: <code>/var/log/syslog</code>'),
    ('Relative', 'Anything else: <code>notes.txt</code>, <code>../data</code>, <code>./run.sh</code>'),
    ('Who expands ~', 'The shell, not the kernel (not inside quotes)'),
    ('Running a local script', '<code>./script.sh</code>: names without a slash are searched in PATH only'),
    ('Tab once / twice', 'Complete the name / list all choices'),
    ('Limits', 'Name ≤ 255 bytes, path ≤ 4096 bytes'),
]) + '\n' + lv + didyou('Tab completion is not magic built into Linux; it is a feature of the shell, and it is programmable. When you type <code>git che</code> and press Tab, bash runs a small completion function shipped with git that knows git’s sub-commands. You can see what plain file completion would offer with <code>compgen -f -- prefix</code>.') + '''
EXAM> “Differentiate between absolute and relative path names with examples” → definition of each; absolute starts with / and is independent of the current directory; relative depends on it; give the same file both ways (e.g. /home/riya/notes.txt vs notes.txt from /home/riya); mention ., .. and ~.
''' + qc('You are in <code>/home/riya/lab/reports</code>. What is the absolute path of <code>../data/sales.csv</code>?', '<code>/home/riya/lab/data/sales.csv</code>: <code>..</code> takes you from reports up to lab, then into data.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>Absolute vs relative, side by side</h2>
''' + table(['', 'Absolute path', 'Relative path'], [
    ['Starts with', '<code>/</code>', 'a name, <code>.</code>, <code>..</code> (or <code>~</code>, which the shell turns into an absolute path)'],
    ['Read from', 'the root directory', 'the current working directory'],
    ['Same meaning everywhere?', 'Yes', 'No: depends on where you are'],
    ['Length', 'often long', 'often short'],
    ['Best for', 'scripts, cron jobs, config files, documentation', 'typing interactively, moving inside a project'],
    ['Example (same file)', '<code>/home/riya/lab/data/sales.csv</code>', 'from <code>~/lab/reports</code>: <code>../data/sales.csv</code>'],
], minw=560) + '''
  <h3>The same file, many paths</h3>
''' + table(['You are in', 'A path to /home/riya/lab/data/sales.csv', 'Kind'], [
    ['anywhere', '<code>/home/riya/lab/data/sales.csv</code>', 'absolute'],
    ['anywhere (as riya)', '<code>~/lab/data/sales.csv</code>', 'home-relative (shell makes it absolute)'],
    ['<code>/home/riya/lab</code>', '<code>data/sales.csv</code> or <code>./data/sales.csv</code>', 'relative'],
    ['<code>/home/riya/lab/data</code>', '<code>sales.csv</code>', 'relative'],
    ['<code>/home/riya/lab/reports</code>', '<code>../data/sales.csv</code>', 'relative'],
    ['<code>/etc</code>', '<code>../home/riya/lab/data/sales.csv</code>', 'relative (long way round)'],
], minw=520) + '''
''' + didyou('A path can be <b>longer than needed and still correct</b>: <code>/home/riya/lab/./reports/../data/sales.csv</code> works, because the kernel simply follows each step. <code>realpath</code> shows the short form.') + qc('Which of these is an absolute path: <code>./run.sh</code>, <code>../etc/hosts</code>, <code>/etc/hosts</code>, <code>~/notes</code>?', 'Only <code>/etc/hosts</code> starts with <code>/</code>. (<code>~/notes</code> becomes absolute after the shell expands it.)') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>How <code>cat ../data/sales.csv</code> finds the file</h2>
''' + stepper([
    ('1. The shell reads your line', '<p>No <code>~</code>, no wildcards, so the shell passes <code>../data/sales.csv</code> to <code>cat</code> unchanged.</p>', 'Behind the screen: tilde and wildcard expansion happen in the shell, before any program runs.'),
    ('2. Where to start?', '<p>The path does not start with <code>/</code>, so the kernel starts at the current directory: <code>/home/riya/lab/reports</code>.</p>', 'Behind the screen: cat calls openat(AT_FDCWD, "../data/sales.csv"); AT_FDCWD means “the current directory”.'),
    ('3. Step “..”', '<p>Look up <code>..</code> in reports: it is the parent, <code>/home/riya/lab</code>.</p>', 'Behind the screen: the kernel needs x permission on reports to search it.'),
    ('4. Step “data”', '<p>Look up <code>data</code> in lab: a directory. Continue.</p>', 'Behind the screen: the name → inode lookup is usually answered from the dentry cache in RAM.'),
    ('5. Step “sales.csv”', '<p>Look up <code>sales.csv</code> in data: a regular file. Found.</p>', 'Behind the screen: now read permission on the file itself is checked.'),
    ('6. Open and read', '<p>The kernel returns a file descriptor; cat reads and prints the contents.</p>', 'Behind the screen: if any step had failed, you would see “No such file or directory” (ENOENT) or “Permission denied” (EACCES).'),
]) + qc('From <code>/home/riya</code>, the same command fails. At which step does it fail?', 'Step 3/4: <code>..</code> from /home/riya is <code>/home</code>, and <code>/home</code> has no <code>data</code> entry, so the lookup fails with “No such file or directory”.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
P_ABS = [('/', 'home'), ('home', 'riya'), ('riya', 'lab'), ('lab', 'data'), ('data', 'sales.csv')]
see = [tree(hl=('/',), you='reports') + side('Absolute path:', '/home/riya/lab/data/sales.csv', 'acc'),
       tree(hl=('/', 'home', 'riya', 'lab', 'data', 'sales.csv'), you='reports', path=P_ABS, tone='green') + side('Start at / and walk down:', 'the same from everywhere.', 'green'),
       tree(hl=('reports',), you='reports', tone='blue') + side('Relative path:', '../data/sales.csv', 'acc'),
       tree(hl=('reports', 'lab', 'data', 'sales.csv'), you='reports', path=[('lab', 'reports'), ('lab', 'data'), ('data', 'sales.csv')], tone='blue') + side('Start where you are:', '.. up to lab, then down.', 'blue'),
       tree(hl=('riya',), you='riya', tone='red') + side('From ~ the same relative path:', '.. = /home → no data/', 'red')]
def walk(rows, active, verdict, tone='blue'):
    o = t(10, 20, 'kernel path walk', 9, 'ink3', anchor='start', bold=True)
    for k, (comp, res) in enumerate(rows):
        y = 32 + k * 28
        o += label_box(10, y, 90, 24, [comp], 'acc' if k == active else 'card', 8.6)
        o += arrow(102, y + 12, 126, y + 12, 'ink3', 1.4) + t(132, y + 16, res, 8.4, 'ink2' if k != active else 'acc', anchor='start', bold=(k == active))
    return o + t(10, 230, verdict, 8.8, tone, anchor='start', bold=True)
WA = [('start: /', 'root directory (inode 2)'), ('home', 'found: directory'), ('riya', 'found: directory (x needed)'), ('lab', 'found: directory'), ('data', 'found: directory'), ('sales.csv', 'found: regular file')]
WR = [('start: cwd', '/home/riya/lab/reports'), ('..', 'the parent: /home/riya/lab'), ('data', 'found: directory'), ('sales.csv', 'found: regular file')]
WF = [('start: cwd', '/home/riya'), ('..', 'the parent: /home'), ('data', 'NOT FOUND in /home')]
behind = [walk(WA[:1], 0, 'Absolute: the walk always begins at /.'),
          walk(WA, 5, 'Each name is looked up inside the previous folder.', 'green'),
          walk(WR[:1], 0, 'Relative: the walk begins at the process’s cwd.'),
          walk(WR, 3, 'Same file, fewer steps, but only from here.', 'blue'),
          walk(WF, 2, 'ENOENT: “No such file or directory”.', 'red')]
two = anim_two('Two ways to reach one file', 'Absolute vs relative: what the kernel walks', 'The directory tree with the route of an absolute path from / and of a relative path from reports, and the failing case from home.',
               'The kernel looking up one path component at a time, with the result of each lookup.', see, behind,
               ['Riya is in <code>reports</code>. The absolute path names the file from the very top.',
                'The route goes from <code>/</code> down through home, riya, lab and data. It would be the same from any folder.',
                'The relative path <code>../data/sales.csv</code> is directions from where she stands.',
                '<code>..</code> climbs to lab, then down to data and the file. Shorter, but tied to her position.',
                'Run from home, the same directions lead to <code>/home</code>, which has no <code>data</code> folder.'],
               ['An absolute path makes the kernel start at the root directory, inode 2.',
                'Each component is looked up in the folder found so far; every folder needs x (search) permission.',
                'A relative path starts at the current directory the kernel keeps for this process.',
                '<code>..</code> is a real entry pointing to the parent. Four lookups and the file is found.',
                'One lookup fails and the whole open fails: error ENOENT, printed as “No such file or directory”.'])

# scenario 1: script that works from anywhere
a1 = term(14, 14, 332, 100, ['$ cat make.sh', ('wc -l < ../data/sales.csv', 'out'), '$ cd ~ && bash lab/reports/make.sh', ('../data/sales.csv: No such file', 'err')], title='riya@laptop', size=7.8, prompt='$') + cap('Relative to the current folder, not to the script.', '', 'red', y=150, h=34)
a2 = term(14, 14, 332, 100, ['$ cat make.sh', ('wc -l < /home/riya/lab/data/sales.csv', 'out'), ('# works, but only on Riya’s laptop', 'dim')], title='fix 1: absolute', size=7.8, prompt='$') + cap('Fix 1: absolute path. Breaks on other machines.', '', 'amber', y=150, h=34)
a3 = term(14, 14, 332, 100, ['$ cat make.sh', ('here="$(dirname "$0")"', 'out'), ('wc -l < "$here/../data/sales.csv"', 'out')], title='fix 2: relative to the script', size=7.8, prompt='$') + cap('Fix 2: start from the script’s own folder.', '', 'blue', y=150, h=34)
a4 = term(14, 14, 332, 100, ['$ cd / && bash ~/lab/reports/make.sh', ('2', 'acc'), '$ cd /tmp && bash ~/lab/reports/make.sh', ('2', 'acc')], title='riya@laptop', size=7.8, prompt='$') + cap('Now it works from any folder.', '', 'green', y=150, h=34)
a5 = (t(180, 30, 'Rules for scripts', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• never trust the caller’s current folder', '• build paths from "$(dirname "$0")"', '• or cd there first: cd "$(dirname "$0")" || exit', '• cron jobs and services start in other folders'])) + cap('A script should not care where it was started.', '', 'green', y=150, h=34))
s1 = anim_one('Real-time scenario 1', 'A script that works from any folder',
              'The most common path bug in scripts and cron jobs, and the standard fix. The output is from a real run on our build machine.',
              'Paths relative to the script', 'A script using ../data fails from home; fixed with an absolute path, then with the script’s own folder via dirname "$0".', [a1, a2, a3, a4, a5],
              ['The script uses <code>../data/sales.csv</code>. Run from home, <code>..</code> is <code>/home</code>: not found.',
               'An absolute path works, but hard-codes <code>/home/riya</code>, so it fails for Kabir or on a server.',
               '<code>$0</code> is the path used to start the script; <code>dirname</code> keeps its folder. Paths are built from there.',
               'Now the script finds its data whether it is started from <code>/</code>, <code>/tmp</code> or anywhere else.',
               'cron, systemd and CI tools all start scripts in other folders. This one habit avoids many failed jobs.'],
              hid='scenario-scriptdir')

# scenario 2: Tab completion
b1 = term(14, 14, 332, 100, ['$ cd /va', ('', 'dim')], title='riya@laptop', size=8.4, cursor=False) + cap('Type a few letters…', '', 'card', y=150, h=34)
b2 = term(14, 14, 332, 100, ['$ cd /var/', ('(Tab completed it)', 'dim')], title='riya@laptop', size=8.4) + cap('…press Tab: only one match, so it is completed.', '', 'blue', y=150, h=34)
b3 = term(14, 14, 332, 100, ['$ cd /var/l', ('lib/    local/  lock/   log/', 'acc'), '$ cd /var/l', ('(Tab Tab listed the choices)', 'dim')], title='riya@laptop', size=8.4) + cap('Several matches: Tab twice lists them.', '', 'blue', y=150, h=34)
b4 = term(14, 14, 332, 100, ['$ cd /var/lo', '$ cd /var/log/', ('(one more letter, Tab again)', 'dim')], title='riya@laptop', size=8.4) + cap('Add a letter to narrow it down, press Tab again.', '', 'blue', y=150, h=34)
b5 = term(14, 14, 332, 100, ['$ cat /var/log/nosuch', ('(Tab does nothing: no such name)', 'err')], title='riya@laptop', size=8.4) + cap('No completion? The path is probably wrong. Free check!', '', 'green', y=150, h=34)
s2 = anim_one('Real-time scenario 2', 'Tab completion: type less, make no typos',
              'Professionals almost never type a full path. They type a few letters and press Tab.',
              'Tab and Tab Tab', 'Typing /va and pressing Tab, listing choices with Tab Tab, narrowing down, and Tab refusing a wrong name.', [b1, b2, b3, b4, b5],
              ['Riya types <code>cd /va</code>…',
               '…and presses <b>Tab</b>. Only <code>/var</code> matches, so the shell completes it and adds the slash.',
               'Now <code>/var/l</code> matches four folders. A second Tab lists them (folders on this machine may differ).',
               'She types one more letter, <code>o</code>, and Tab completes <code>log/</code>.',
               'If Tab does nothing, there is no such name. That is an instant spelling check before you press Enter.'],
              hid='scenario-tab')

# scenario 3: ./ and PATH
c1 = term(14, 14, 332, 100, ['$ ls', ('deploy.sh', 'out'), '$ deploy.sh', ('deploy.sh: command not found', 'err')], title='riya@laptop', size=7.8, prompt='$') + cap('The file is here, yet “command not found”.', '', 'red', y=150, h=34)
c2 = label_box(14, 18, 332, 50, ['A name WITHOUT a slash = search the PATH folders only', '/usr/local/bin  →  /usr/bin  →  /bin'], 'card', 8.8) + cap('The current folder is not in PATH, on purpose.', '', 'card', y=150, h=34)
c3 = term(14, 14, 332, 100, ['$ ./deploy.sh', ('deploying...', 'acc')], title='riya@laptop', size=7.8, prompt='$') + cap('./deploy.sh contains a slash: run exactly this file.', '', 'green', y=150, h=34)
c4 = label_box(14, 18, 332, 60, ['Why not add . to PATH?', 'A file called “ls” left in /tmp by someone else', 'would run when you type ls inside /tmp.'], 'red', 8.8) + cap('Safety: you always know which program runs.', '', 'red', y=150, h=34)
c5 = (t(180, 30, 'Three ways to run a script', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• ./deploy.sh  (needs chmod +x)', '• /opt/tools/deploy.sh  (absolute)', '• bash deploy.sh  (bash reads the file)', '• or install it into a PATH folder (Lesson 12.1)'])) + cap('A slash in the name means “this exact file”.', '', 'green', y=150, h=34))
s3 = anim_one('Real-time scenario 3 · advanced', 'Why ./ is needed to run a script',
              'Every beginner hits this. The reason is how the shell decides what to run, and it is a security feature.',
              'Names with and without a slash', 'A script in the current folder gives command not found; the PATH search explained; ./ runs it; why . is not in PATH.', [c1, c2, c3, c4, c5],
              ['<code>deploy.sh</code> is right there, but typing its name gives “command not found”.',
               'A command name without any <code>/</code> is searched only in the PATH folders, and the current folder is not one of them.',
               '<code>./deploy.sh</code> is a relative path (it has a slash), so the shell runs exactly that file.',
               'Leaving <code>.</code> out of PATH protects you from running a fake <code>ls</code> planted in a shared folder.',
               'Any path with a slash works: relative, absolute, or ask bash to read the file.'],
              hid='scenario-dotslash')

dx = dissect('Layer by layer: dissect one path',
    'Take <code>~/lab/reports/../data/./sales.csv</code> and open each piece: who handles it, why it exists, where it really lives, and where you will use it. Each comes with a real command and its output from our build machine (Riya is in <code>~/lab</code>).', [
    dict(key='tilde', name='~', sub='home (shell)',
         why='Typing <code>/home/riya</code> again and again is slow, and differs for every user.',
         how='The <b>shell</b> replaces <code>~</code> with <code>$HOME</code> before the command runs. Inside quotes it stays a plain character.',
         impl='Tilde expansion in bash; the kernel never sees <code>~</code>.', used='Every config path: <code>~/.bashrc</code>, <code>~/.ssh/config</code>.',
         cmd="echo ~/lab \"~/lab\" '~/lab'"),
    dict(key='lab', name='lab/reports', sub='normal names',
         why='Each name is one step down the tree.',
         how='The kernel looks the name up in the directory reached so far. You need x (search) permission on each folder you pass through.',
         impl='Directory entries (name → inode); <code>fs/namei.c</code> in the kernel.', used='Every path you will ever type.',
         setup='mkdir -p reports data', cmd="stat -c '%A %n' /home/riya /home/riya/lab"),
    dict(key='dotdot', name='..', sub='parent',
         why='To go up without knowing the full address of the parent.',
         how='Every directory contains a real entry <code>..</code> pointing to its parent. <code>reports/..</code> has the same inode number as <code>.</code> (lab).',
         impl='A directory entry created with every folder; at <code>/</code>, <code>..</code> points to <code>/</code> itself.', used='<code>cd ..</code>, <code>../config</code> in projects.',
         setup='mkdir -p reports data', cmd='ls -di . reports/..'),
    dict(key='data', name='data', sub='the target folder',
         why='After climbing, we go down another branch.',
         how='A normal lookup again, now inside lab.',
         impl='The dentry cache keeps recent lookups in RAM, so repeated paths are fast.', used='Navigating across sibling folders.',
         setup='mkdir -p reports data', cmd='ls -ld data'),
    dict(key='dot', name='.', sub='this folder',
         why='Sometimes you need to say “here” explicitly: <code>./run.sh</code>, <code>cp file .</code>.',
         how='Every directory has an entry <code>.</code> pointing to itself, so <code>data/.</code> is just <code>data</code>.',
         impl='A directory entry; same inode as the folder.', used='Running local scripts, copying into the current folder.',
         setup='mkdir -p reports data', cmd='ls -di data data/.'),
    dict(key='file', name='sales.csv', sub='the last component',
         why='The thing you actually want.',
         how='The final lookup returns a regular file; now its own permissions (r, w) are checked.',
         impl='The file’s inode; <code>realpath</code> shows the clean absolute path.', used='Opening, copying, deleting: always the end of a path.',
         setup="mkdir -p reports data && echo 'id,amt' > data/sales.csv", cmd='realpath ~/lab/reports/../data/./sales.csv'),
], hint='One path, six pieces. The first is handled by the shell; the rest by the kernel. Click a piece.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Walking a path, one folder at a time</h2>
  <p>Left: the directory tree and the route each path takes. Right: the kernel looking up each component in turn.</p>
''' + two + '''
  <p>Three real-time scenarios: scripts that work from any folder, Tab completion, and why <code>./</code> is needed.</p>
''' + s1 + s2 + s3 + dx + qc('Who turns <code>~</code> into <code>/home/riya</code>: the shell or the kernel? What happens with <code>ls "~"</code>?', 'The shell. Inside quotes it is not expanded, so <code>ls "~"</code> looks for a file literally named <code>~</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Paths at work</h2>
''' + usecase(term(8, 14, 104, 62, [('0 2 * * * /opt/', 'prompt'), ('bk/run.sh', 'acc')], title='crontab', size=6.4, step=12),
              '1. Cron jobs and services: always absolute', 'Schedulers start jobs in a different folder with a minimal PATH, so crontab lines and systemd units use absolute paths for programs and files.', ['Schedule', '*absolute paths', 'job runs at 2 a.m.']) + '\n' + usecase(
    term(8, 14, 104, 62, [('import "./db"', 'prompt'), ('"../config"', 'acc')], title='project', size=6.4, step=12),
    '2. Code projects: relative inside the repo', 'Inside a project, code refers to files relatively (<code>./src</code>, <code>../config</code>), so the project works wherever it is cloned.', ['git clone', '*relative paths', 'works anywhere']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['$(dirname', '"$0")'], 'acc', 8.6), '3. Deployment scripts',
    'Install and deploy scripts find their own folder with <code>dirname "$0"</code> (or <code>realpath</code>) and build every other path from it.', ['Run from CI', '*script dir', 'right files']) + '\n' + usecase(
    term(8, 14, 104, 62, [('-v ./data:/data', 'prompt')], title='docker', size=6.4, step=12),
    '4. Containers and configs', 'Tools such as Docker Compose resolve relative paths in their files from the file’s own folder, a rule worth checking in every tool you use.', ['Config file', '*which base?', 'right mount']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Tab', 'Tab Tab'], 'green', 8.6), '5. Everyday speed',
    'Support engineers move around unfamiliar servers with Tab completion: fewer typos, and an instant signal when a path does not exist.', ['New server', '*Tab', 'fast and correct']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Path tricks you will reuse. All were really run on our Ubuntu build machine.', [
    dict(level='b', title='The clean absolute path of anything', scenario='A colleague needs the full path of a file you are looking at.',
         setup="mkdir -p reports data && echo 'id,amt' > data/sales.csv", cmd='cd reports && realpath ../data/./sales.csv', files_note='reports/ and data/sales.csv inside ~/lab.',
         explain='<code>realpath</code> removes <code>.</code>, <code>..</code> and links and prints the absolute path.'),
    dict(level='b', title='Split a path into folder, name and extension', scenario='A script receives a full file path and needs its folder and its name without .csv.',
         cmd='f=/data/in/sales_2026-11.csv; echo "$(dirname "$f") | $(basename "$f") | $(basename "$f" .csv)"',
         explain='<code>dirname</code> = folder part, <code>basename</code> = last part, with an optional suffix to remove.'),
    dict(level='i', title='How do I get from here to there?', scenario='You want the relative path from one folder to another, e.g. for a link or a config.',
         setup="mkdir -p reports data && touch data/sales.csv", cmd='realpath --relative-to=/home/riya/lab/reports /home/riya/lab/data/sales.csv', files_note='reports/ and data/sales.csv inside ~/lab.',
         explain='GNU realpath computes the relative route between two absolute paths.'),
    dict(level='a', title='See what Tab would complete', scenario='Debugging completion, or listing candidates in a script.',
         setup='mkdir -p data && touch data/sales.csv data/sales_old.csv data/stock.csv', cmd='compgen -f -- data/sa', files_note='three CSV files in data/.',
         explain='<code>compgen -f</code> prints the file names bash’s Tab completion would offer for a prefix.'),
], extra=build_up('a script’s own folder, absolute', 'A script must find files next to itself, whatever folder it is started from. Grow the expression step by step. (Here the script is <code>/home/riya/script.sh</code>, run from <code>~/lab</code>.)',
    '', [
    ('echo "$0"', 'The path that was used to start the script.'),
    ('dirname "$0"', 'Only its folder part.'),
    ('cd "$(dirname "$0")" && pwd', 'Go there and print it: an absolute folder, even if $0 was relative.'),
    ('here="$(cd "$(dirname "$0")" && pwd)"; echo "data file: $here/data/sales.csv"', 'Store it once and build every path from it. The classic first line of robust scripts.'),
])) + which('Path situations.', [
    ('Path inside a crontab or systemd unit', '/opt/app/run.sh', 'Absolute: jobs start elsewhere.', 'run.sh or ./run.sh'),
    ('Typing interactively in a project', 'cd ../config', 'Short relative paths + Tab.', 'Typing the full absolute path every time.'),
    ('Run a script in this folder', './deploy.sh', 'A slash means “this file”.', 'deploy.sh (searched in PATH only)'),
    ('A script needs files next to itself', '"$(dirname "$0")/data"', 'Independent of the caller’s folder.', '../data (depends on where it is run)'),
    ('Clean up a messy path', 'realpath path', 'Removes ., .. and links.', 'Guessing by eye.'),
    ('A folder name with spaces', 'cd "My Files"', 'Quotes keep it one argument.', 'cd My Files (two arguments)'),
    ('Use ~ inside quotes', '"$HOME/notes"', '$HOME expands inside double quotes.', '"~/notes" (not expanded)'),
    ('Unsure a path exists', 'Tab', 'No completion = no such name.', 'Pressing Enter and reading errors.'),
]) + puzzle_answer('<code>..</code> is measured from the <b>current working directory</b> of the process, not from the script’s location. From <code>~/lab/reports</code> it means <code>~/lab</code>; from home it means <code>/home</code>, where there is no <code>data</code>. To make it work from anywhere, build paths from the script’s own folder: <code>here="$(cd "$(dirname "$0")" &amp;&amp; pwd)"</code> and then read <code>"$here/../data/sales.csv"</code>, or use an absolute path from a config setting.') + qc('Why does <code>cd ~</code> work but <code>cd "~"</code> fail?', 'Tilde expansion is done by the shell and does not happen inside quotes, so <code>cd "~"</code> looks for a folder literally named <code>~</code>.') + '''
</section>
'''

body = (cmap + story.replace('  <div class="story">', before('<a href="../02-moving-around-pwd-cd-and-ls/">Lesson 2.2</a>: pwd, cd and ls, and the idea of a current working directory.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
