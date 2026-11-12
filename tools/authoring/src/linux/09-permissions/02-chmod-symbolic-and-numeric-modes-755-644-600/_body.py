import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

APP = r"""rm -rf ~/app; mkdir -p ~/app/src/lib ~/app/config ~/app/bin
echo 'print(1)' > ~/app/src/main.py; echo 'x=1' > ~/app/src/lib/util.py; echo 'DB_PASS=s3cret' > ~/app/config/.env
echo 'port=8080' > ~/app/config/app.ini; printf '#!/bin/sh\necho started\n' > ~/app/bin/start.sh
chmod 644 ~/app/src/main.py ~/app/src/lib/util.py ~/app/config/.env ~/app/config/app.ini ~/app/bin/start.sh; chmod 755 ~/app ~/app/src ~/app/src/lib ~/app/config ~/app/bin"""

HOOK = hook('A developer unzips a project and nothing runs: every script lost its x. A colleague “fixes” a website with <code>chmod -R 777 /var/www</code> and a week later the site is defaced. An SSH login fails with “UNPROTECTED PRIVATE KEY FILE”. All three are solved with one command, <code>chmod</code>, used precisely: the smallest change, on exactly the right files. You will learn both ways to write it, letters (<code>u+x</code>, <code>go-r</code>) and numbers (<code>755</code>, <code>644</code>, <code>600</code>), and the safe way to change a whole tree.',
    ['change permissions with symbolic modes: who (<code>u g o a</code>), how (<code>+ - =</code>), what (<code>r w x X</code>)',
     'convert between letters and octal in your head, and choose 644, 600, 755, 750 or 700 for the right job',
     'change whole trees safely with <code>-R</code>, <code>X</code> and <code>find … -exec chmod</code>, without making every file executable',
     'see what changed (<code>-v -c</code>), copy a mode (<code>--reference</code>), and know why chmod 777 is never the fix'])
ROAD = roadmap([
    ('story', 'The story', 3, 'unzip, 777, SSH key'),
    ('decide', 'Which mode when?', 2, 'the quick chart'),
    ('definition', 'What chmod does', 5, 'simple meaning + 4 depths'),
    ('types', 'Symbolic vs numeric', 4, 'and how to convert'),
    ('commands', 'chmod by field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'bits flipping'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'fix a project'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which mode? (decide in 5 seconds)', [
    ('Normal file (docs, code, web pages)', 'chmod 644 FILE', 'rw-r--r--'),
    ('Secret (.env, private key, password file)', 'chmod 600 FILE', 'rw-------'),
    ('Script or program everyone may run', 'chmod 755 FILE  /  chmod +x', 'rwxr-xr-x'),
    ('Normal folder', 'chmod 755 DIR', 'rwxr-xr-x'),
    ('Private folder (~/.ssh)', 'chmod 700 DIR', 'rwx------'),
    ('Team folder (group may write)', 'chmod 770 DIR  (+ SGID, 9.4)', 'rwxrwx---'),
    ('Just add run permission', 'chmod u+x FILE', 'keep the rest'),
    ('Remove access for others', 'chmod o-rwx FILE', 'keep the rest'),
    ('A whole tree: folders 755, files 644', 'chmod -R a-x,u=rwX,go=rX DIR', 'X = only folders'),
])

cmap = concept_map(
    [('9.1', 'Reading permissions', 'rwx, 644, x on folders'), ('7.1', 'find', '-perm, -exec'), ('8.3', 'Groups', 'team access')],
    ['chmod with letters: u g o a, + - =, r w x X', 'chmod with numbers: 4 2 1, 644 600 755 700', 'symbolic vs numeric: when to use which', '-R, X and find -exec for trees', '-v, -c, --reference; who may chmod'],
    [('9.3', 'chown and umask', 'owners and defaults'), ('9.4', 'SUID, SGID, sticky', 'the 4th digit'), ('9.5', 'ACLs', 'per-user rules'), ('12.5', 'Shell scripts', 'chmod +x')],
    'chmod changes the nine permission bits (and the special bits). Small, precise changes keep systems both usable and safe.')

sc = (term(20, 14, 316, 156, ['$ chmod +x deploy.sh', '$ chmod 600 .env', '$ chmod -R a-x,u=rwX,go=rX site/', '$ ls -l', ('-rwxr-xr-x deploy.sh', 'out'), ('-rw------- .env', 'acc'), ('drwxr-xr-x site', 'out')], title='riya@web01: ~/app', prompt='riya@web01:~/app$', size=7.0, step=15)
      + t(352, 36, 'Two ways to say it:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• letters: u+x, go-r', '• numbers: 755, 600', '• r4 w2 x1', '• -R: whole tree', '• X: folders only'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Unzipped, broken, then “fixed” with 777</h2>
  <div class="story">
''' + puzzle('To make a project’s scripts runnable, Riya runs <code>chmod -R 755 app/</code>. Everything works. A week later the security scan reports 2,000 “executable” .py, .ini and .env files, and .env is now readable by every user. Two things went wrong with one command. Which, and what should she have typed?') + '''
    <p class="narration">A project arrives as a zip file. Riya has to make it run, safely.</p>
''' + scene('A terminal: chmod +x on a script, chmod 600 on .env, and a recursive chmod with capital X; ls -l shows the result.', sc,
            'The smallest change on <tspan font-weight="700" class="s-acc">exactly</tspan> the right files.') + '''
K> Why do people say 777?
A> Because it makes “Permission denied” disappear: everyone may read, write and run everything. It also lets the web server, every user and any attacker change the file. It hides the real problem.
R> So what do I type?
A> Ask two questions: <b>who</b> needs access, and <b>what kind</b>. Then use letters for small changes (<code>u+x</code>, <code>o-r</code>) and numbers when you want an exact result (<code>600</code>). Today: both forms, conversions, and changing a tree without ruining it.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Three rows of three switches (owner, group, others; read, write, execute). Letters flip single switches; numbers set a whole row at once: 4 for read, 2 for write, 1 for execute, added up.">'
       + label_box(14, 20, 190, 110, ['switch board', 'owner:  [r][w][x]', 'group:  [r][ ][x]', 'others: [r][ ][x]'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['letters flip', 'single switches:', 'u+x  g-w  o-r', 'a=r (set exactly)'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['numbers set rows:', 'r=4  w=2  x=1', '7=rwx 6=rw- 5=r-x', '755 = 7|5|5'], 'amber', 8.6)
       + t(320, 160, 'Letters = change some switches. Numbers = set all nine.', 9.6, 'ink2')
       + t(320, 182, 'Both write the same bits in the inode.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('chmod at four depths', [
    ('v', 'No jargon: a board of nine switches', '      <p>Each file has nine switches.</p>' + pic),
    ('b', 'The forms you will type every day', '''      <ul>
        <li><code>chmod +x deploy.sh</code>: make a script runnable.</li>
        <li><code>chmod 600 .env</code>: only me, read and write.</li>
        <li><code>chmod 644 page.html</code>: everyone reads, only I write.</li>
        <li><code>chmod 755 tools/</code>: a normal folder.</li>
        <li><code>chmod o-rwx report.xlsx</code>: take everything away from others.</li>
      </ul>'''),
    ('i', 'Symbolic syntax and octal arithmetic', '''      <ul>
        <li>Symbolic: <code>[ugoa][+-=][rwxXst]</code>, several joined by commas: <code>u=rwx,g=rx,o=</code>. <code>+</code> adds, <code>-</code> removes, <code>=</code> sets exactly (missing letters are removed).</li>
        <li>Numeric: one digit per class, each the sum of r=4, w=2, x=1: rwx=7, rw-=6, r-x=5, r--=4, ---=0. Three digits always replace all nine bits.</li>
        <li><code>X</code> (capital) adds x only to directories and to files that <b>already</b> have some x. So on a tree that was 777, first remove x: <code>chmod -R a-x,u=rwX,go=rX</code> (clauses run left to right; a-x clears the files, X puts x back on folders only).</li>
        <li>Only the file’s owner (or root) can chmod it, no matter what the mode says.</li>
      </ul>'''),
    ('a', 'Behind the screen: chmod(), umask and digits', '''      <ul>
        <li>chmod calls the <code>fchmodat()</code> system call, which rewrites the mode in the inode and updates its ctime. The file’s contents and mtime do not change.</li>
        <li>With no “who” letter (<code>chmod +x f</code>), the change is filtered by your <b>umask</b> (Lesson 9.3): with umask 022, <code>chmod +w</code> adds only u+w. Write <code>a+x</code> or <code>u+x</code> to be explicit.</li>
        <li>Fewer than three digits are padded on the <b>left</b>: <code>chmod 7 f</code> means 007, <code>chmod 64 f</code> means 064. A fourth leading digit sets SUID/SGID/sticky (4/2/1, Lesson 9.4).</li>
        <li>chmod on a symbolic link changes the <b>target</b>; with <code>-R</code>, links inside the tree are not followed.</li>
        <li>Permission checks happen at open time: a process that already has a file open keeps its access after you chmod it.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>chmod: change mode</h2>
''' + def_block(
    '<code>chmod</code> changes the permission bits (the mode) of files and directories. A mode can be given <b>symbolically</b> (who, operator, permissions: <code>u+x</code>, <code>go-w</code>, <code>a=r</code>) to change some bits, or <b>numerically</b> in octal (<code>644</code>, <code>755</code>) to set all of them. Only the owner of a file or root may change its mode.',
    'Give exactly the access each class needs: no more, no less.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Symbolic mode', 'Letters: u g o a, + - =, r w x X.'),
    ('Numeric (octal) mode', 'Digits 0–7 per class: 755.'),
    ('u / g / o / a', 'user (owner), group, others, all.'),
    ('= (equals)', 'Set exactly these bits for that class.'),
    ('X (capital)', 'x only for folders (and already-executable files).'),
    ('-R', 'Recursive: the whole tree.'),
    ('Least privilege', 'The smallest access that works.'),
    ('ctime', 'Inode change time: updated by chmod.'),
]) + '\n' + names('Where the names come from.', [
    ('chmod', 'change mode', 'Unix V1, 1971.'),
    ('u', 'user', 'The owner.'),
    ('g', 'group', 'The file’s group.'),
    ('o', 'others', 'Everyone else.'),
    ('a', 'all', 'u + g + o.'),
    ('X', 'conditional execute', 'Folders only.'),
    ('octal', 'base 8', '3 bits = one digit.'),
    ('777', 'rwxrwxrwx', 'The “please hack me” mode.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Make runnable', '<code>chmod u+x f</code>'),
    ('Secret', '<code>chmod 600 f</code>'),
    ('Web file', '<code>chmod 644 f</code>'),
    ('Folder', '<code>chmod 755 d</code>'),
    ('Tree', '<code>chmod -R a-x,u=rwX,go=rX d</code>'),
    ('See changes', '<code>chmod -c …</code>'),
]) + '\n' + lv + didyou('Octal is used because three bits make exactly one digit 0–7. That is why permissions are 3-digit numbers and why <code>chmod 999</code> is an error: 9 is not an octal digit.') + '''
EXAM> “Set report.txt so the owner can read and write, the group can read, others nothing.” → <code>chmod 640 report.txt</code> or <code>chmod u=rw,g=r,o= report.txt</code>.
''' + qc('Convert <code>rwxr-x---</code> to a number, and 644 to letters.', '750; rw-r--r--.') + mistake('chmod -R 755 app/   (to make the scripts runnable)',
    'chmod -R a-x,u=rwX,go=rX app/   then   chmod u+x app/bin/*.sh   and   chmod 600 app/config/.env',
    '-R 755 gives x to every file (data, configs, .py) and makes secrets readable by all. Capital X gives x only to folders; scripts and secrets get their own, precise command.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Symbolic vs numeric, and the conversion table</h2>
''' + table(['', 'Symbolic (u+x, go-w)', 'Numeric (755, 600)'], [
    ['Changes', 'only the bits you name', 'all nine bits at once'],
    ['Result depends on the old mode?', 'yes (adds/removes)', 'no (always the same)'],
    ['Best for', 'small fixes: add x, remove others', 'known final states: secrets, web files'],
    ['Recursive on mixed trees', 'yes, with X', 'dangerous (files get folder modes)'],
    ['Readable in scripts', 'self-explaining', 'short, needs knowing octal'],
], minw=520) + table(['Digit', 'Bits', 'Letters', 'Meaning'], [
    ['7', '4+2+1', 'rwx', 'everything'],
    ['6', '4+2', 'rw-', 'read and write'],
    ['5', '4+1', 'r-x', 'read and run / enter'],
    ['4', '4', 'r--', 'read only'],
    ['3', '2+1', '-wx', 'rare (drop box folder)'],
    ['2', '2', '-w-', 'rare'],
    ['1', '1', '--x', 'pass through a folder'],
    ['0', '0', '---', 'nothing'],
], minw=420) + table(['Symbolic', 'Effect'], [
    ['<code>u+x</code>', 'owner gains x'],
    ['<code>go-w</code>', 'group and others lose w'],
    ['<code>a+r</code>', 'everyone gains r'],
    ['<code>o=</code>', 'others: nothing at all'],
    ['<code>u=rw,g=r,o=</code>', 'exactly 640'],
    ['<code>g=u</code>', 'group gets the same as owner'],
    ['<code>+x</code> (no who)', 'a+x filtered by umask'],
], minw=360) + qc('A file is 640. What is it after <code>chmod g+w,o+r</code>?', '664 (rw-rw-r--).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>chmod explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine, in a sample project <code>~/app</code> that starts with every file 644 and every folder 755, as after an unzip.</p>
''' + cmdcard_u(['adding or removing one kind of access', 'making scripts runnable', 'taking access away from others'],
               ['when you want an exact, known final mode (use numbers)'])(
    'symbolic', 'chmod (letters)', 'change some bits',
    'Who: <code>u</code> owner, <code>g</code> group, <code>o</code> others, <code>a</code> all. Operator: <code>+</code> add, <code>-</code> remove, <code>=</code> set exactly. Permissions: <code>r w x</code>, <code>X</code> (folders only), <code>s t</code> (Lesson 9.4). Join with commas.',
    'chmod [-R] [-v|-c] WHO(+|-|=)PERMS[,…] FILE…', 'change',
    [('u+x', 'owner may run', 'scripts'),
     ('go-rwx', 'group and others: nothing', 'privacy'),
     ('o-r', 'others lose read', 'tighten'),
     ('a=r', 'everyone read only', 'published files'),
     ('u=rw,g=r,o=', 'exactly 640', 'readable spec'),
     ('g+w', 'group may change it', 'team files'),
     ('g=u', 'copy owner bits to group', 'shared work')],
    dict(setup=APP, cmd="cd ~/app\nchmod u+x bin/start.sh; chmod go-r config/.env\nstat -c '%A %a %n' bin/start.sh config/.env\n./bin/start.sh", note='Two small, exact changes: the owner may now run start.sh; .env is private.'),
    [('dev', [
        dict(situation='The unzipped script will not run.', setup=APP, cmd="cd ~/app; ./bin/start.sh; echo \"exit $?\"\nchmod u+x bin/start.sh && ./bin/start.sh", expect='any',
             why='exit 126 = found but not executable. u+x is enough for your own scripts; a+x if others run it too.')]),
     ('sec', [
        dict(situation='Take away everything from others on a sensitive folder, keep the rest.', setup=APP, cmd="cd ~/app; chmod -R o-rwx config\nls -la config",
             why='Symbolic -R is safe here: it only removes, and it removes the same thing everywhere.')]),
     ('qa', [
        dict(situation='Test how a program behaves when a config is unreadable.', setup=APP, cmd="cd ~/app; chmod a-r config/app.ini\ncat config/app.ini; echo \"exit $?\"\nchmod u+r config/app.ini; cat config/app.ini", expect='any',
             why='Remove r to simulate a broken deployment, then restore. Negative tests catch bad error messages.')]),
    ],
    anat=anatomy([('chmod', 'cmd', 'change mode'), ('u', 'opt', 'who'), ('+', 'arg', 'add'), ('x', 'opt', 'what'), ('start.sh', 'arg', 'file')], 'Several: chmod u+x,go-w file. No spaces around commas.')
) + cmdcard_u(['setting a known final state', 'secrets, web files, scripts', 'scripts and documentation (short and exact)'],
               ['-R on trees that mix files and folders', 'fewer than 3 digits by accident'])(
    'numeric', 'chmod (numbers)', 'set all nine bits',
    'One octal digit per class, owner first: each digit is r(4) + w(2) + x(1). Three digits replace the whole mode; a fourth leading digit sets SUID, SGID, sticky.',
    'chmod [-R] [-v|-c] NNN FILE…', 'change',
    [('644', 'rw-r--r--', 'normal files'),
     ('600', 'rw-------', 'secrets, SSH keys'),
     ('755', 'rwxr-xr-x', 'scripts, folders'),
     ('750', 'rwxr-x---', 'team-only programs/folders'),
     ('700', 'rwx------', 'private folders'),
     ('640', 'rw-r-----', 'logs readable by a group'),
     ('444', 'r--r--r--', 'read-only for all'),
     ('777', 'rwxrwxrwx', 'never on a server')],
    dict(setup=APP, cmd="cd ~/app\nchmod 600 config/.env; chmod 755 bin/start.sh; chmod 640 config/app.ini\nstat -c '%A %a %n' config/.env bin/start.sh config/app.ini", note='The result does not depend on the old mode: good for scripts and runbooks.'),
    [('devops', [
        dict(situation='SSH refuses a key copied from Windows.', setup="mkdir -p ~/.ssh; printf 'KEY\\n' > ~/.ssh/id_demo; chmod 644 ~/.ssh/id_demo", cmd="stat -c '%a %n' ~/.ssh/id_demo\nchmod 600 ~/.ssh/id_demo; chmod 700 ~/.ssh\nstat -c '%a %n' ~/.ssh ~/.ssh/id_demo; rm ~/.ssh/id_demo",
             why='ssh demands the private key be 600 (or 400) and ~/.ssh 700, otherwise: “UNPROTECTED PRIVATE KEY FILE” (Lesson 16.6).')]),
     ('web', [
        dict(situation='Web content: files 644, folders 755.', setup="rm -rf ~/site; mkdir -p ~/site/css; touch ~/site/index.html ~/site/css/app.css; chmod 777 ~/site ~/site/css ~/site/index.html ~/site/css/app.css", cmd="cd ~/site\nfind . -type d -exec chmod 755 {} +; find . -type f -exec chmod 644 {} +\nfind . -exec stat -c '%a %n' {} +",
             why='Two finds, one for each type: the classic way to undo a chmod -R 777.')]),
     ('dba', [
        dict(situation='Database data folders must be private.', setup='rm -rf ~/pgdata; mkdir -p ~/pgdata/base; chmod 755 ~/pgdata', cmd="chmod 700 ~/pgdata; ls -ld ~/pgdata",
             why='PostgreSQL refuses to start if its data directory is accessible by group or others (“has invalid permissions”).')]),
    ]
) + mistake('chmod -R u=rwX,go=rX site/   (to repair a tree that was chmod -R 777)', 'chmod -R a-x,u=rwX,go=rX site/',
            'X keeps x on files that already have it, so after 777 every file would stay 755. Clearing x first (a-x) makes X give x to folders only. Checked on our build machine.') + mistake('chmod 7 file   ·   chmod 64 file', 'chmod 700 file   ·   chmod 640 file',
            'Missing digits are added on the left: 7 becomes 007 (others rwx, owner nothing!) and 64 becomes 064. Always give three digits.') + cmdcard_u(['fixing a whole project or website', 'giving x to folders but not files'],
               ['-R with numbers on mixed trees', 'chmod -R on / or /etc (breaks the system)'])(
    'recursive', 'chmod -R · X · find -exec', 'change a whole tree',
    '<code>-R</code> applies the mode to a folder and everything inside. With capital <code>X</code>, x goes only to folders (and files that already had x). For different modes per type, use <code>find -type d</code> and <code>find -type f</code> with <code>-exec chmod</code>.',
    'chmod -R a-x,u=rwX,go=rX DIR   ·   find DIR -type f -exec chmod 644 {} +', 'danger',
    [('-R', 'recursive', 'trees'),
     ('X', 'x for folders only', 'with -R'),
     ('a-x,u=rwX,go=rX', 'folders 755, files 644', 'standard fix'),
     ('a-x,u=rwX,g=rX,o=', 'folders 750, files 640', 'team/private'),
     ('find -type d -exec chmod 755 {} +', 'folders only', 'precise'),
     ("find -name '*.sh' -exec chmod u+x {} +", 'only scripts', 'after unzip')],
    dict(setup=APP, cmd="cd ~/app; chmod -R 755 .\nfind . -type f -exec stat -c '%a %n' {} + | head -3\nchmod -R a-x,u=rwX,go=rX .\nfind . -exec stat -c '%a %n' {} + | sort -k2 | head -6", note='First the puzzle’s mistake: every file became 755 (executable). Then capital X: folders 755, files 644.'),
    [('sys', [
        dict(situation='After unzip: folders 755, files 644, scripts executable, secrets private.', setup=APP, cmd="cd ~/app\nchmod -R a-x,u=rwX,go=rX .\nfind . -name '*.sh' -exec chmod u+x,go+x {} +\nchmod 600 config/.env\nfind . -type f -exec stat -c '%a %n' {} + | sort -k2",
             why='Four precise steps instead of one dangerous one. This is the answer to the puzzle.')]),
     ('devops', [
        dict(situation='Git remembers only the x bit: check scripts before committing.', setup=APP, cmd="cd ~/app; find . -name '*.sh' ! -perm -u+x -print",
             why='Lists scripts that would fail in CI with exit 126. Git stores mode 100755 vs 100644 per file.')]),
    ]
) + cmdcard_u(['seeing exactly what changed (audits, scripts)', 'copying a known-good mode'],
               ['silently changing large trees'])(
    'verbose', 'chmod -v · -c · --reference', 'see and copy changes',
    '<code>-v</code> reports every file, <code>-c</code> only files that really changed, <code>--reference=FILE</code> copies FILE’s mode. Only the owner or root may chmod.',
    'chmod -c MODE FILE…   ·   chmod --reference=GOOD FILE…', 'change',
    [('-v', 'every file', 'logs'),
     ('-c', 'only changes', 'audits'),
     ('--reference=F', 'copy F’s mode', 'same'),
     ('sudo chmod', 'not your file', 'admins')],
    dict(setup=APP, cmd="cd ~/app\nchmod -c 600 config/.env config/app.ini\nchmod -c 600 config/.env\nchmod --reference=config/.env src/main.py; stat -c '%a %n' src/main.py", note='The second -c prints nothing: nothing changed. --reference copied 600.'),
    [('sec', [
        dict(situation='Only the owner or root may change a mode.', cmd="chmod 666 /etc/passwd; echo \"exit $?\"", expect='any',
             why='“Operation not permitted” (EPERM), not “Permission denied”: the mode bits of a file never give others the right to chmod it.')]),
    ]
) + undo('chmod is instant and has no undo command. Know the old mode before big changes.', [
    ('Before a big change:', "save modes: <code>find DIR -exec stat -c '%a %n' {} + &gt; modes.txt</code>; restore with <code>while read m f; do chmod \"$m\" \"$f\"; done &lt; modes.txt</code>."),
    ('Ran chmod -R 777:', 'reset with the two finds (folders 755, files 644), then re-apply secrets (600) and scripts (+x).'),
    ('Broke system files (chmod -R on /etc or /usr):', 'compare with a working server or reinstall packages (<code>dpkg --verify</code>, Lesson 14.2); often a reinstall is fastest.'),
    ('Made your own file unreadable:', 'you are still the owner: <code>chmod u+rw FILE</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='chmod 644 /etc/passwd', meaning='You are not the owner (EPERM).', fix='<code>sudo chmod …</code>, if you really should.'),
    dict(cmd='chmod 999 notes.txt', setup='touch notes.txt', meaning='9 is not an octal digit.', fix='Digits 0–7 only.'),
    dict(cmd='chmod u+z notes.txt', setup='touch notes.txt', meaning='Unknown permission letter.', fix='r w x X s t only.'),
    dict(cmd='chmod 644 missing.txt', meaning='No such file.', fix='Check the name; quote names with spaces.'),
]) + qc('Which single command makes all folders 750 and all files 640 under data/?', '<code>chmod -R a-x,u=rwX,g=rX,o= data/</code>') + '''
'''

SCREENS = screens_block('Real terminal screens: -c shows what changed', 'chmod -c reports only real changes, so you can see the effect of a recursive fix.',
    APP + "; chmod -R 777 ~/app; printf '%s\\n' 'PS1=\"riya@web01:~/app$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'cd ~/app; chmod -R -c a-x,u=rwX,go=rX config' Enter", ' after a recursive fix on config: every change is listed.'),
    ('Enter', "'chmod -R -c a-x,u=rwX,go=rX config' Enter", ' after the same command again: nothing printed, nothing to change.'),
], 74, 12, hid='screens', what='bash')

cards = cards + SCREENS + '</section>\n'

def bits(mode, hi=None):
    o = ''
    for c, cls in enumerate(['owner', 'group', 'others']):
        o += t(40, 30 + c * 30, cls, 8, 'ink2', anchor='middle')
        for b, letter in enumerate('rwx'):
            on = mode[c * 3 + b] != '-'
            tn = 'green' if on else 'card'
            if hi and (c, b) in hi:
                tn = 'amber'
            o += label_box(70 + b * 40, 16 + c * 30, 34, 24, [letter if on else '-'], tn, 8)
        val = sum(v for v, ch in zip((4, 2, 1), mode[c * 3:c * 3 + 3]) if ch != '-')
        o += t(205, 32 + c * 30, f'= {val}', 8.4, 'acc', anchor='start', bold=True)
    return o
frames_b = [('rw-r--r--', None, 'Start: 644.'), ('rwxr--r--', [(0, 2)], 'u+x: one switch, owner x.'), ('rwxr-xr-x', [(1, 2), (2, 2)], 'go+x: two more switches → 755.'), ('rw-------', [(1, 0), (1, 2), (2, 0), (2, 2), (0, 2)], 'chmod 600: all nine set at once.')]
see = [term(14, 16, 332, 116, ['$ ' + c, ('-' + m + ' file', 'out')], title='riya@web01', prompt='riya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for (m, h, n), c in zip(frames_b, ['ls -l file', 'chmod u+x file', 'chmod go+x file', 'chmod 600 file'])]
behind = [bits(m, h) + t(180, 130, n, 8.6, 'violet', bold=True) for m, h, n in frames_b]
two = anim_two('Switches and digits', 'Behind the screen: the nine bits',
               'A terminal running chmod u+x, go+x and 600 on one file.',
               'A 3 by 3 board of r w x switches for owner, group and others with the octal value of each row; letters flip single switches, a number sets all nine.', see, behind,
               ['644.', 'Letters: one change.', 'Letters: two changes.', 'Numbers: everything.'],
               ['rw-r--r-- = 644', 'u+x → 744', 'go+x → 755', '600: set exactly'])

def tree(k, note, tone):
    items = [('app/', 'd'), ('src/', 'd'), ('main.py', 'f'), ('.env', 'f')]
    modes = {0: ['755', '755', '644', '644'], 1: ['755', '755', '755', '755'], 2: ['755', '755', '644', '644'], 3: ['755', '755', '644', '600']}[k]
    o = ''
    for i, ((n, typ), m) in enumerate(zip(items, modes)):
        bad = typ == 'f' and m == '755'
        tn = 'red' if bad else ('green' if (k == 3 and n == '.env') else ('blue' if typ == 'd' else 'card'))
        o += label_box(14 + i * 84, 30, 78, 46, [n, m], tn, 8)
    return o + t(180, 120, note, 8.6, tone, bold=True)
frames = [tree(0, 'After unzip: folders 755, files 644.', 'violet'), tree(1, 'chmod -R 755: files become executable!', 'red'),
          tree(2, 'chmod -R a-x,u=rwX,go=rX: X only for folders.', 'green'), tree(3, 'Then chmod 600 .env: the secret is private.', 'green')]
s1 = anim_one('Animated example', '-R 755 vs -R with capital X',
              'The same tree, two recursive commands.',
              'recursive chmod', 'Four boxes app, src, main.py, .env with their modes: -R 755 turns files red (executable); capital X keeps files 644; .env then becomes 600.', frames,
              ['Start.', 'The puzzle’s mistake.', 'The right way.', 'Secrets last.'], hid='scenario-tree')

dx = dissect('Layer by layer: what chmod touches',
    'Each layer has a real command and output from our build machine.', [
    dict(key='cmd', name='Your command', sub='letters or digits', why='Same result, two notations.', how='chmod parses it.', impl='GNU coreutils.', used='Everywhere.',
         cmd="touch f; chmod u=rw,g=r,o= f; stat -c '%a %A' f; chmod 640 f; stat -c '%a %A' f"),
    dict(key='umask', name='umask filter', sub='only without who', why='+x / +w with no u/g/o.', how='Bits in umask are not added.', impl='Applies to “a” implied.', used='Surprises.',
         cmd="touch g; chmod 640 g; umask; chmod +x g; stat -c %a g"),
    dict(key='inode', name='Inode', sub='mode + ctime', why='Where bits live.', how='fchmodat().', impl='ctime updated, mtime not.', used='Every access check.',
         cmd="touch h; stat -c 'mtime %y | ctime %z' h | cut -c1-80; sleep 1; chmod 600 h; stat -c 'mtime %y | ctime %z' h | cut -c1-80"),
    dict(key='rule', name='Who may chmod', sub='owner or root', why='Mode bits do not grant chmod.', how='EPERM otherwise.', impl='Kernel check.', used='Security.',
         cmd="chmod 600 /etc/hosts 2>&1; echo \"exit $?\"", expect='any'),
], hint='From your command to the inode. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Switches and digits, and recursive chmod done right</h2>
''' + two + s1 + dx + qc('Why did <code>chmod +x g</code> give 751 and not 750 + something else?', 'Without “who”, +x means a+x filtered by the umask (022 does not block x), so owner, group and others all gained x: 640 → 751.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>chmod at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['chmod +x', 'deploy.sh'], 'blue', 8.6), '1. Scripts and CI',
              'Pipelines fail with exit 126 until scripts get x (and Git records 755).', ['Fail', '*chmod +x', 'commit']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['600', '.env, keys'], 'red', 8.6), '2. Secrets',
    'Keys, tokens and .env files are 600; ssh and many tools refuse anything looser.', ['Secret', '*chmod 600', 'safe']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['644 / 755', 'web root'], 'green', 8.6), '3. Websites',
    'Web files 644, folders 755, uploads folder writable only by the app user.', ['Deploy', '*find -exec', 'serve']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['700', 'data dir'], 'amber', 8.6), '4. Databases',
    'PostgreSQL and MySQL data directories must be private to the service account.', ['Init', '*chmod 700', 'start']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['find -perm', 'audit'], 'violet', 8.6), '5. Audits',
    'Security teams search for world-writable files and fix them with chmod o-w.', ['Scan', '*chmod o-w', 'clean']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Make runnable', scenario='Your own script.', cmd="printf '#!/bin/sh\\necho hi\\n' > hi.sh; chmod u+x hi.sh; ./hi.sh", explain='u+x.'),
    dict(level='b', title='Private file', scenario='Only you.', cmd="touch token.txt; chmod 600 token.txt; ls -l token.txt", explain='600.'),
    dict(level='i', title='Remove world-write', scenario='Fix risky files.', setup=APP + '; chmod 666 ~/app/config/app.ini', cmd="find ~/app -perm -o+w -exec chmod -c o-w {} +", explain='-c reports.'),
    dict(level='i', title='Scripts only', scenario='After unzip.', setup=APP, cmd="find ~/app -name '*.sh' -exec chmod -c a+x {} +", explain='find + chmod.'),
    dict(level='a', title='Save and restore modes', scenario='Before a risky change.', setup=APP, cmd="cd ~/app; find . -exec stat -c '%a %n' {} + > /tmp/modes.txt; chmod -R 777 .; while read -r m f; do chmod \"$m\" \"$f\"; done < /tmp/modes.txt; stat -c '%a %n' config/.env src/main.py", explain='A manual undo.'),
], extra=build_up('fixing a project after unzip', 'Riya applies the four-step fix from the puzzle.', APP + '; chmod -R 777 ~/app', [
    ("cd ~/app; find . -exec stat -c '%a %n' {} + | sort -k2 | head -4", '1. Start: everything 777.'),
    ('cd ~/app; chmod -R a-x,u=rwX,go=rX .', '2. Folders 755, files 644 (X).'),
    ("cd ~/app; chmod a+x bin/*.sh; chmod 600 config/.env", '3. Scripts runnable, secret private.'),
    ("cd ~/app; find . -type f -exec stat -c '%a %n' {} + | sort -k2", '4. Check every file.'),
], cumulative=True)) + which('Choosing the right form.', [
    ('Add run permission', 'chmod u+x / a+x', 'Keeps the rest.', 'chmod 777.'),
    ('Known final mode', 'chmod 600 / 644 / 755', 'Exact.', 'Many + and -.'),
    ('A tree', 'chmod -R a-x,u=rwX,go=rX', 'Folders only get x.', 'chmod -R 755.'),
    ('Different per type', 'find -type d/f -exec chmod', 'Precise.', 'One -R.'),
    ('Report changes', 'chmod -c', 'Audit trail.', 'Silence.'),
    ('Same as another', '--reference', 'Consistent.', 'Guessing.'),
]) + keys('Handy forms.', [
    ('chmod +x f', 'a+x (umask filtered)', 'scripts'),
    ('chmod u=rw,go= f', 'exactly 600', 'secrets'),
    ('chmod -R go-w d', 'remove group/other write', 'tighten'),
    ('chmod g=u f', 'group like owner', 'teams'),
    ('chmod -c', 'report changes', 'audits'),
    ("stat -c %a f", 'check', 'after'),
]) + scriptit('fix-perms.sh', 'A reusable fixer for a deployed app folder: safe defaults, executable scripts, private secrets, and a report.',
'''d=${1:-$HOME/app}
[ -d "$d" ] || { echo "no such folder: $d" >&2; exit 1; }
chmod -R a-x,u=rwX,go=rX "$d"
find "$d" -name '*.sh' -exec chmod a+x {} +
find "$d" \\( -name '.env' -o -name '*.key' -o -name '*.pem' \\) -exec chmod 600 {} +
echo "world-writable left: $(find "$d" -perm -o+w | wc -l)"
find "$d" -type f -exec stat -c '%a %n' {} + | sort -k2''',
'<p>Run on the sample project (prepared with mixed modes).</p>') + puzzle_answer('<code>chmod -R 755</code> gave x to every <b>file</b> (data and configs became “executable”) and read access to everyone, including <code>.env</code>. Better: <code>chmod -R a-x,u=rwX,go=rX app/</code> (capital X: folders only), then <code>chmod a+x app/bin/*.sh</code> and <code>chmod 600 app/config/.env</code>.') + qc('What does <code>chmod o=</code> do?', 'Removes all permissions for others (sets them to ---).') + '''
</section>
'''

_sh.run_sh('rm -rf ~/app ~/site ~/pgdata ~/hi.sh', 'any')
_SC = _sh.run_sh(APP + "; chmod -R 777 ~/app", 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-reading-permissions-rwx-for-user-group/">Lesson 9.1</a> (reading rwx and octal).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
