import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='09-permissions', lesson='02-chmod-symbolic-and-numeric-modes-755-644-600', n='9.2',
    module_label='Module 9 · Permissions and ownership',
    title='chmod: symbolic and numeric modes (755, 644, 600)',
    desc='chmod with symbolic modes (u g o a, + - =, r w x X, commas) and octal modes (4 2 1; 644, 600, 755, 750, 700, 640); converting between them; recursive changes done safely with -R and capital X or find -exec; -v, -c, --reference; who may chmod; umask filtering of +x; why chmod -R 755 and 777 are mistakes, with real outputs and animations.',
    og_desc='Change Linux permissions precisely with chmod letters (u+x, go-r) and numbers (755, 644, 600), and fix whole trees safely.',
    minutes=40, level='Beginner → Advanced',
    lead='chmod changes who may read, write and run a file. This lesson explains letters and numbers, how to convert between them, how to change whole trees without ruining them, and how developers, admins, web, DBAs, DevOps and security use chmod.',
    chips=['Letters and numbers', '-R with capital X', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Letters and numbers
touch notes.txt; printf '#!/bin/sh\\necho hi\\n' > run.sh; echo key > secret.key
chmod u+x run.sh
chmod 600 secret.key
chmod u=rw,g=r,o= notes.txt
stat -c '%A %a %n' notes.txt run.sh secret.key
./run.sh
"""

RUN = dict(
    heading='Change modes with letters and numbers',
    intro='<p>Make a script runnable, a key private and a note 640, then check all three.</p>',
    code=MAIN,
    anno=[('chmod u=rw,g=r,o= notes.txt', 'Exactly 640, written in letters.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which file is 600?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> start at 644; what is the mode after go-r and u+x? Then run.',
             code="touch p; chmod 644 p; chmod go-r,u+x p\nstat -c '%a %A' p\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is owner rwx only (700). Fix the number.',
             code="touch q; chmod 7 q\nstat -c '%a %A' q\n"),
        dict(label='4 · Your turn', hint='Make folders 755 and files 644 in a tree with one chmod.',
             code="mkdir -p t/a; touch t/x t/a/y; chmod -R 777 t\nchmod -R a-x,u=rwX,go=rX t\nfind t -exec stat -c '%a %n' {} +\n"),
        dict(label='5 · Challenge', hint='Make only the .sh files executable, nothing else.',
             code="mkdir -p s; touch s/a.sh s/b.sh s/c.txt\nfind s -name '*.sh' -exec chmod a+x {} +\nstat -c '%a %n' s/*\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: fix real files',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Your SSH folder', cmd='chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_* && chmod 644 ~/.ssh/*.pub && ls -la ~/.ssh', output='drwx------ 2 vineeta vineeta 4096 Oct  2 10:00 .\n-rw------- 1 vineeta vineeta  411 Oct  2 10:00 id_ed25519\n-rw-r--r-- 1 vineeta vineeta  101 Oct  2 10:00 id_ed25519.pub', note='Typical.'),
        dict(title='2 · See what a fix would change', cmd="mkdir -p ~/t/x; touch ~/t/a; chmod -R 777 ~/t; chmod -R -c a-x,u=rwX,go=rX ~/t", output=pc("mkdir -p ~/t/x; touch ~/t/a; chmod -R 777 ~/t; chmod -R -c a-x,u=rwX,go=rX ~/t"), note='Recorded.'),
        dict(title='3 · Find world-writable files in your home', cmd='find ~ -xdev -type f -perm -o+w 2>/dev/null | head', output='', note='Typical: should print nothing.'),
        dict(title='4 · chmod version', cmd='chmod --version | head -1', output=pc('chmod --version | head -1'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='A mode changing step by step',
    intro='<p>Step through letters and numbers on one file and watch the octal value.</p>',
    code='''touch f; chmod 644 f
a=$(stat -c %a f)
chmod u+x f; b=$(stat -c %a f)
chmod go-r f; c=$(stat -c %a f)
chmod 640 f; d=$(stat -c %a f)
echo "$a -> $b -> $c -> $d"
''',
    notes={1: 'Start :: 644.', 2: 'Save.', 3: 'u+x :: 744.', 4: 'go-r :: 700.', 6: 'Summary :: line 5 set 640 exactly.'},
)

WORKED_INTRO = 'Three tasks from real jobs: a developer’s scripts, a web root and a secrets audit.'
EXAMPLES = [
    dict(level='b', tag='Developer', title='Make a script runnable',
         problem='<p>A new script gives Permission denied. Fix it with the smallest change.</p>',
         inp='a 644 script', approach=['u+x.', 'Run again.'],
         code='''printf '#!/bin/sh\\necho build ok\\n' > build.sh
./build.sh 2>/dev/null || echo "denied (exit $?)"
chmod u+x build.sh; ./build.sh
stat -c '%A %n' build.sh
''', notes={2: 'Denied :: 126.', 3: 'Fixed.', 4: 'Only owner x.'}, tryit='Use a+x so others can run it too.'),
    dict(level='i', tag='Web', title='Reset a 777 web root',
         problem='<p>Someone ran chmod -R 777 on a site. Restore 755 folders and 644 files.</p>',
         inp='a site tree', approach=['find -type d / -type f.', 'Count world-writable before and after.'],
         code='''mkdir -p www/img; touch www/index.html www/img/logo.png; chmod -R 777 www
echo "world-writable: $(find www -perm -o+w | wc -l)"
find www -type d -exec chmod 755 {} +; find www -type f -exec chmod 644 {} +
echo "world-writable: $(find www -perm -o+w | wc -l)"
''', notes={2: 'Before :: 4.', 3: 'Fix.', 4: 'After :: 0.'}, tryit='Do it with one chmod -R and X.'),
    dict(level='a', tag='Security', title='Private secrets everywhere',
         problem='<p>Find every .env, .key and .pem file that group or others can read, and make it 600.</p>',
         inp='a project', approach=['find with -o.', '-perm /go+r.', 'chmod -c.'],
         code='''mkdir -p p/a p/b; touch p/a/.env p/b/tls.key p/b/notes.txt; chmod 644 p/a/.env p/b/tls.key p/b/notes.txt
find p -type f \\( -name '.env' -o -name '*.key' -o -name '*.pem' \\) -perm /go+r -exec chmod -c 600 {} +
stat -c '%a %n' p/a/.env p/b/tls.key p/b/notes.txt
''', notes={1: 'Setup.', 2: 'Fix :: -c reports each change.', 3: 'notes.txt untouched.'}, tryit='Run the find again: nothing to change.'),
]

QUIZ = mix([
    dict(q='Which makes a script executable by its owner only, keeping other bits?', options=['chmod 700', 'chmod u+x', 'chmod a=x', 'chmod 1'], answer=1, why='Symbolic adds one bit.'),
    dict(q='What is 640 in letters?', options=['rw-r-----', 'rwxr-----', 'rw-rw----', 'r--r-----'], answer=0, why='6 rw-, 4 r--, 0 ---.'),
    dict(q='What does chmod 7 file set?', options=['700', '007', '777', 'error'], answer=1, why='Padded on the left.'),
    dict(q='What does capital X do with -R?', options=['x for everything', 'x only for folders (and already-executable files)', 'removes x', 'sticky bit'], answer=1, why='Conditional execute.'),
    dict(q='Best mode for an SSH private key?', options=['644', '600', '755', '666'], answer=1, why='ssh demands it.'),
    dict(q='Who may change a file’s mode?', options=['anyone with w', 'the owner or root', 'the group', 'anyone with x'], answer=1, why='Mode bits do not grant chmod.'),
    dict(q='chmod u=rw,g=r,o= equals…', options=['640', '644', '600', '660'], answer=0, why='rw- r-- ---.'),
    dict(q='Why is chmod -R 755 on a project a mistake?', options=['it is too slow', 'every file becomes executable and readable by all', 'folders lose x', 'it removes owner write'], answer=1, why='Use a-x,u=rwX,go=rX.'),
])

REVISION = [
    'Letters: <code>[ugoa][+-=][rwxX]</code>, e.g. <code>u+x</code>, <code>go-w</code>, <code>u=rw,g=r,o=</code>.',
    'Numbers: r4 w2 x1 per class; three digits set all nine bits. 644 files, 600 secrets, 755 scripts/folders, 700 private, 750/640 team.',
    'Always three digits (7 = 007). 777 is never the fix.',
    'Trees: <code>chmod -R a-x,u=rwX,go=rX DIR</code>; per type: <code>find -type d/f -exec chmod … {} +</code>.',
    '<code>-c</code> shows changes, <code>-v</code> everything, <code>--reference=F</code> copies a mode.',
    'Only the owner or root can chmod (EPERM otherwise). <code>+x</code> without “who” is filtered by the umask.',
]

FAQ = [
    ('What does chmod 755 mean?', 'Owner read, write, execute; group and others read and execute (rwxr-xr-x).'),
    ('What is the difference between chmod 644 and 755?', '644 = rw-r--r-- (normal files); 755 adds x for everyone (scripts and folders).'),
    ('How do I make a file executable?', 'chmod u+x FILE (or chmod +x / a+x for everyone).'),
    ('How do I set folders to 755 and files to 644?', 'chmod -R a-x,u=rwX,go=rX DIR, or two find commands with -type d and -type f.'),
    ('Why is chmod 777 bad?', 'Every user and process can change or replace the file; it hides the real problem and fails audits.'),
    ('How do I copy permissions from one file to another?', 'chmod --reference=SOURCE TARGET.'),
    ('Why “Operation not permitted” with chmod?', 'You are not the owner; use sudo if appropriate.'),
]

PRACTICE_INTRO = 'Small chmod tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Secret', stmt='Make key.pem 600 and print its mode.', inp='a file', code="touch key.pem; chmod 600 key.pem; stat -c %a key.pem\n", explain='600.'),
    dict(level='easy', title='Runnable', stmt='Add x for the owner and print the letters.', inp='a file', code="touch r.sh; chmod 644 r.sh; chmod u+x r.sh; stat -c %A r.sh\n", explain='u+x.'),
    dict(level='easy', title='Letters to number', stmt='Set rwxr-x--- with letters and print the number.', inp='a file', code="touch s; chmod u=rwx,g=rx,o= s; stat -c %a s\n", explain='750.'),
    dict(level='medium', title='Remove from others', stmt='From 666, remove all rights from others.', inp='a file', code="touch o; chmod 666 o; chmod o= o; stat -c '%a %A' o\n", explain='o=.'),
    dict(level='medium', title='Group like owner', stmt='Give the group the same rights as the owner on a 640 file.', inp='a file', code="touch g; chmod 640 g; chmod g=u g; stat -c %a g\n", explain='g=u → 660.'),
    dict(level='medium', title='Tree', stmt='Folders 750, files 640 in one command.', inp='a tree', code="mkdir -p d/e; touch d/f d/e/h; chmod -R 777 d\nchmod -R a-x,u=rwX,g=rX,o= d\nfind d -exec stat -c '%a %n' {} + | sort -k2\n", explain='X.'),
    dict(level='business', title='Report changes', stmt='Make three files 644 and report only those that changed.', inp='mixed', code="touch a b c; chmod 644 a; chmod 600 b; chmod 666 c\nchmod -c 644 a b c\n", explain='-c.'),
    dict(level='business', title='Copy a mode', stmt='Give new.conf the same mode as good.conf.', inp='two files', code="touch good.conf new.conf; chmod 640 good.conf\nchmod --reference=good.conf new.conf; stat -c %a new.conf\n", explain='--reference.'),
]

SCN_INTRO = 'Interview questions about chmod, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“What does chmod 755 do?”', 'Asked in almost every Linux interview.', 'can you convert?',
        '''<ul>
          <li>7 = rwx owner, 5 = r-x group, 5 = r-x others.</li>
          <li>For scripts and folders.</li>
          <li>Symbolic: <code>u=rwx,go=rx</code>.</li>
        </ul>''', 'not knowing r=4 w=2 x=1.') +
    scn('Developer team', 'Junior', '“Permission denied” running ./deploy.sh in CI', 'It works on the developer’s laptop.', 'do you know Git keeps the x bit?',
        '''<ol>
          <li><code>git ls-files -s deploy.sh</code>: 100644 means no x in the repository.</li>
          <li><code>git update-index --chmod=+x deploy.sh</code> (or chmod +x and commit).</li>
          <li>Or call it with <code>bash deploy.sh</code>.</li>
        </ol>''', 'adding chmod 777 to the pipeline.') +
    scn('Web team', 'Mid-level', 'A site was hacked after chmod -R 777', 'Uploaded PHP files appeared everywhere.', 'can you restore and prevent it?',
        '''<ul>
          <li>Restore: folders 755, files 644 (two finds), owner = deploy user, not www-data.</li>
          <li>Only the uploads folder writable by www-data, with PHP execution disabled there.</li>
          <li>Monitor with <code>find -perm -o+w</code>.</li>
        </ul>''', 'restoring from backup and keeping 777.') +
    scn('Platform', 'Senior', 'Mode drift across 500 servers', 'Some hosts have world-readable keys.', 'automation and policy?',
        '''<ul>
          <li>Configuration management sets mode on every managed file (mode: "0600").</li>
          <li>Compliance scans (find, OpenSCAP) report drift; alert, then fix.</li>
          <li>umask and ACL defaults to prevent new drift (9.3, 9.5).</li>
        </ul>''', 'a monthly manual chmod.')
) + interview([
    ('What does chmod u+x do?', 'Adds execute for the owner only.'),
    ('chmod 644 vs chmod 600?', '644 others can read; 600 only owner.'),
    ('How do you change permissions recursively?', 'chmod -R, preferably with X or find -exec per type.'),
    ('What does chmod = mean?', 'Set exactly, removing unlisted bits for that class.'),
    ('Can a user chmod a file they can write but do not own?', 'No; only the owner or root.'),
    ('What does the 4th digit in chmod 4755 mean?', 'Special bits: 4 SUID, 2 SGID, 1 sticky (Lesson 9.4).'),
    ('How do you see what chmod changed?', 'chmod -c (or -v).'),
], [
    ('RHCSA (EX200)', '“List, set, and change standard ugo/rwx permissions”.'),
    ('LFCS', 'Manage file permissions with chmod.'),
    ('CompTIA Linux+', 'chmod symbolic and octal modes.'),
]) + distro('chmod is the same everywhere; small option differences.', [
    ('Symbolic and octal', 'yes', 'yes', 'yes', 'Git Bash: limited (NTFS)'),
    ('-c / --reference', 'GNU', 'GNU', 'no (BSD chmod has -v only)', 'GNU'),
    ('Capital X', 'yes', 'yes', 'yes', 'yes'),
    ('chmod +a (ACL)', '-', '-', 'macOS ACLs', '-'),
    ('Windows names', '-', '-', '-', 'icacls'),
]) + teaser('9.3', 'Riya fixed the modes, but every new file her team creates is still 644 owned by its creator, so colleagues cannot edit it. Who owns a file, how do you hand it to someone else, and what decides the mode of a new file? Next: chown, chgrp and umask.')

CHEATSHEET = cheatsheet('chmod', [
    ('Letters', [('u+x', 'owner run'), ('go-w', 'no write for g, o'), ('a=r', 'all read only'), ('u=rw,g=r,o=', '640'), ('g=u', 'group like owner')]),
    ('Numbers', [('644', 'files'), ('600', 'secrets'), ('755', 'scripts, folders'), ('700', 'private'), ('750 / 640', 'team')]),
    ('Trees', [('-R a-x,u=rwX,go=rX', '755/644'), ('-R a-x,u=rwX,g=rX,o=', '750/640'), ('find -type d …755', 'folders'), ('find -type f …644', 'files'), ("find -name '*.sh' …+x", 'scripts')]),
    ('Options', [('-c', 'report changes'), ('-v', 'report all'), ('--reference=F', 'copy mode'), ('sudo chmod', 'not owner'), ('stat -c %a', 'check')]),
])

MINDMAP = mindmap('chmod', [
    ('Letters', 'blue', ['u g o a', '+ - =', 'r w x X']),
    ('Numbers', 'green', ['r4 w2 x1', '644 600 755', '3 digits!']),
    ('Trees', 'amber', ['-R + X', 'find -exec', 'never -R 777']),
    ('Options', 'violet', ['-c -v', '--reference', 'sudo']),
    ('Rules', 'acc', ['owner or root', 'umask on +x', 'ctime changes']),
    ('Uses', 'red', ['scripts +x', 'secrets 600', 'web 644/755']),
])

LAB = lab('fix a project', 'Build the lab, do the four tasks in your own terminal, then run the checker.',
    setup='''mkdir -p ~/lab92 && cd ~/lab92 && rm -rf proj
mkdir -p proj/bin proj/conf proj/docs; touch proj/bin/run.sh proj/conf/.env proj/conf/app.ini proj/docs/readme.md
chmod -R 777 proj''',
    tasks=['Make every folder 755 and every file 644 under <code>proj</code>.',
           'Make <code>proj/bin/run.sh</code> executable for everyone.',
           'Make <code>proj/conf/.env</code> readable and writable by the owner only.',
           'Make <code>proj/conf</code> (the folder) accessible to the owner only.'],
    solution='''chmod -R a-x,u=rwX,go=rX proj
chmod a+x proj/bin/run.sh
chmod 600 proj/conf/.env
chmod 700 proj/conf''',
    check='''cd ~/lab92
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 tree"    '[ "$(stat -c %a proj proj/bin proj/docs proj/docs/readme.md proj/conf/app.ini | tr "\\n" " ")" = "755 755 755 644 644 " ]'
ok "2 script"  '[ "$(stat -c %a proj/bin/run.sh)" = 755 ]'
ok "3 secret"  '[ "$(stat -c %a proj/conf/.env)" = 600 ]'
ok "4 folder"  '[ "$(stat -c %a proj/conf)" = 700 ]' ''')
