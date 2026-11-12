import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='09-permissions', lesson='03-ownership-and-defaults-chown-chgrp-and-umask', n='9.3',
    module_label='Module 9 · Permissions and ownership',
    title='Ownership and defaults: chown, chgrp and umask',
    desc='Owner and group of a file and who may change them; chown USER, USER:GROUP, USER:, :GROUP, -R, -h, -c, --reference; chgrp; umask (022, 002, 027, 007, 077, -S, subshells) and why files start at 666 and folders at 777; files created by sudo, cp and ownership, systemd UMask=, Ubuntu’s pam_umask 0002; with real outputs and animations.',
    og_desc='Hand files to the right user with chown and chgrp, and control the permissions of new files with umask, with real outputs.',
    minutes=38, level='Beginner → Advanced',
    lead='chown and chgrp decide who owns a file; umask decides how new files start. This lesson explains both, the rules about who may change what, and how admins, DevOps, web, DBAs, data teams and security use them.',
    chips=['umask arithmetic animated', 'Hand-overs with chown -R', 'Errors decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# How do new files start?
umask
touch a.txt; mkdir dir1
umask 027; touch b.txt; mkdir dir2
umask 077; touch c.txt; mkdir dir3
stat -c '%a %U:%G %n' a.txt dir1 b.txt dir2 c.txt dir3
"""

RUN = dict(
    heading='umask decides the starting mode',
    intro='<p>Create files and folders with three umask values. chown needs root, so it is in the cards and the lab.</p>',
    code=MAIN,
    anno=[('umask 027; touch b.txt; mkdir dir2', 'File 640, folder 750.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which umask makes files private?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what mode does a new file get with umask 002? Then run.', code="umask 002; touch t\nstat -c %a t\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the goal is a private file created by this command only; the umask leaks to the rest of the script. Use a subshell.', code="umask 077; echo secret > s.txt\ntouch normal.txt\nstat -c '%a %n' s.txt normal.txt\n"),
        dict(label='4 · Your turn', hint='Show your umask as letters.', code="umask -S\n"),
        dict(label='5 · Challenge', hint='Compute the file mode for umask 037 by creating a file.', code="(umask 037; touch m; stat -c %a m)\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: owners and umask',
    intro='<p>Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine unless marked typical.</p>',
    items=[
        dict(title='1 · Your login umask', cmd='umask', output='0002', note='Typical Ubuntu login session (pam_umask, user private groups).'),
        dict(title='2 · Files in your home not owned by you', cmd='find ~ -xdev ! -user $USER 2>/dev/null | head', output='/home/vineeta/projects/build/out.log', note='Typical: often created with sudo.'),
        dict(title='3 · Give them back', cmd='sudo find ~ -xdev ! -user $USER -exec chown $USER: {} +', output='', note='Typical: no output on success.'),
        dict(title='4 · Login defaults', cmd="grep -E '^(UMASK|USERGROUPS_ENAB)' /etc/login.defs", output=pc("grep -E '^(UMASK|USERGROUPS_ENAB)' /etc/login.defs"), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='umask in a script',
    intro='<p>Step through a script that creates files with different umasks.</p>',
    code='''old=$(umask)
touch normal.txt
(umask 077; touch secret.txt)
now=$(umask)
echo "umask before $old, after $now"
stat -c '%a %n' normal.txt secret.txt
''',
    notes={1: 'Save :: 0022.', 2: 'Normal :: 644.', 3: 'Subshell :: 600, and the change ends with the brackets.', 6: 'Result.'},
)

WORKED_INTRO = 'Three tasks from real jobs, recorded with sudo: a hand-over, a sudo-created file and a team folder.'
EXAMPLES = [
    dict(level='b', tag='Help desk', title='“I cannot edit my own file”',
         problem='<p>A file created with sudo cannot be appended to. Show why and fix it.</p>',
         inp='a file made by sudo', approach=['ls -l: owner root.', 'chown back.'],
         code='''sudo touch made_with_sudo.txt
ls -l made_with_sudo.txt
sudo chown riya: made_with_sudo.txt
echo ok >> made_with_sudo.txt && ls -l made_with_sudo.txt
''', notes={2: 'Owner root.', 3: 'Fix.', 4: 'Writable now.'}, tryit='Find all such files with find ~ ! -user riya.'),
    dict(level='i', tag='Sysadmin', title='Hand over a project',
         problem='<p>Give a folder tree owned by aman to riya, and report how many entries changed.</p>',
         inp='aman’s folder', approach=['chown -R -c.', 'Count lines.'],
         code='''sudo rm -rf /tmp/ho; sudo mkdir -p /tmp/ho/a/b; sudo touch /tmp/ho/x /tmp/ho/a/y; sudo chown -R aman: /tmp/ho
sudo chown -R -c riya: /tmp/ho | wc -l
ls -ld /tmp/ho; sudo rm -rf /tmp/ho
''', notes={1: 'Setup.', 2: 'Changed :: 5 entries.', 3: 'Now riya.'}, tryit='Use --reference to copy owners.'),
    dict(level='a', tag='Data team', title='Group-owned shared folder',
         problem='<p>A folder owned by group finance where members can edit and others see nothing.</p>',
         inp='group finance', approach=['chown :finance.', 'chmod 2770 (SGID: 9.4).', 'Test as aman.'],
         code='''sudo rm -rf /tmp/fin; sudo mkdir /tmp/fin; sudo chown root:finance /tmp/fin; sudo chmod 2770 /tmp/fin
sudo -u aman sh -c 'umask 002; echo q > /tmp/fin/q4.csv'
sudo ls -l /tmp/fin; ls /tmp/fin 2>&1
sudo rm -rf /tmp/fin
''', notes={1: 'Folder.', 2: 'aman creates a file.', 3: 'Group finance :: riya (not a member) is refused.'}, tryit='Remove the 2 from 2770 and compare the group of new files.', expect='any'),
]

QUIZ = mix([
    dict(q='Who may change the owner of a file?', options=['the owner', 'root only', 'any member of the group', 'anyone with w'], answer=1, why='Prevents giving files away.'),
    dict(q='What does chown aman: f do?', options=['owner aman, group unchanged', 'owner aman, group aman’s login group', 'group aman only', 'error'], answer=1, why='Trailing colon.'),
    dict(q='With umask 022, a new file gets…', options=['755', '644', '622', '666'], answer=1, why='666 minus 022.'),
    dict(q='With umask 027, a new folder gets…', options=['750', '640', '027', '777'], answer=0, why='777 minus 027.'),
    dict(q='Why does umask never make files executable?', options=['bug', 'files start from 666', 'umask removes x', 'only root'], answer=1, why='No x to begin with.'),
    dict(q='Can riya chgrp her file to a group she is not in?', options=['yes', 'no', 'only with -R', 'only for folders'], answer=1, why='Needs membership or root.'),
    dict(q='A file created with sudo belongs to…', options=['you', 'root', 'the sudo group', 'nobody'], answer=1, why='Effective UID 0.'),
    dict(q='Which keeps a umask change to one command?', options=['umask -1', '(umask 077; cmd)', 'umask --once', 'export UMASK'], answer=1, why='Subshell.'),
])

REVISION = [
    'Owner and group live in the inode. Only root changes the owner; the owner may change the group to one they belong to.',
    '<code>chown USER</code>, <code>USER:GROUP</code>, <code>USER:</code> (login group), <code>:GROUP</code>; <code>-R -c -h --reference</code>.',
    '<code>chgrp [-R] GROUP FILE</code>.',
    'umask removes bits from 666 (files) / 777 (folders): 022→644/755, 027→640/750, 002→664/775, 077→600/700.',
    'umask is per process, inherited; set in ~/.bashrc, ~/.profile, systemd UMask=; Ubuntu logins get 0002.',
    'sudo-created files are root’s; cp makes you the owner of copies.',
]

FAQ = [
    ('How do I change the owner of a file in Linux?', 'sudo chown NEWUSER FILE (or USER:GROUP for both).'),
    ('How do I change ownership recursively?', 'sudo chown -R USER:GROUP DIR.'),
    ('What is the difference between chown and chgrp?', 'chown changes owner and/or group (owner change needs root); chgrp changes only the group.'),
    ('What is umask?', 'A mask of permission bits removed from new files (base 666) and folders (base 777).'),
    ('What does umask 022 mean?', 'New files 644, new folders 755: group and others cannot write.'),
    ('How do I make umask permanent?', 'Add umask 027 (for example) to ~/.bashrc or ~/.profile; for services use systemd UMask=.'),
    ('Why can’t I chown my own file to someone else?', 'Only root may change a file’s owner.'),
]

PRACTICE_INTRO = 'Small ownership tasks (with sudo). Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Show umask', stmt='Print your umask in letters.', inp='this shell', code="umask -S\n", explain='-S.'),
    dict(level='easy', title='Owner of a file', stmt='Print the owner and group of /etc/passwd.', inp='/etc/passwd', code="stat -c '%U:%G' /etc/passwd\n", explain='%U:%G.'),
    dict(level='easy', title='Private by default', stmt='Create a file with umask 077 and print its mode.', inp='umask', code="umask 077; touch p; stat -c %a p\n", explain='600.'),
    dict(level='medium', title='Give away', stmt='Make aman the owner of a new file and show it.', inp='a file', code="touch g.txt; sudo chown aman g.txt; stat -c %U g.txt\n", explain='sudo chown.'),
    dict(level='medium', title='Group only', stmt='Change a file’s group to sudo without changing the owner.', inp='a file', code="touch h.txt; chown :sudo h.txt; stat -c '%U:%G' h.txt\n", explain=':GROUP (riya is in sudo).'),
    dict(level='medium', title='Folder mode', stmt='What mode does mkdir give with umask 007?', inp='umask', code="umask 007; mkdir dd; stat -c %a dd\n", explain='770.'),
    dict(level='business', title='Copy owners', stmt='Give new.txt the same owner and group as ref.txt.', inp='two files', code="touch ref.txt new.txt; sudo chown aman:finance ref.txt\nsudo chown --reference=ref.txt new.txt; stat -c '%U:%G' new.txt\n", explain='--reference.'),
    dict(level='business', title='Recursive with report', stmt='Hand a small tree to aman and count changes.', inp='a tree', code="mkdir -p tr/a; touch tr/x tr/a/y\nsudo chown -R -c aman: tr | wc -l\n", explain='-c + wc.'),
]

SCN_INTRO = 'Interview questions about ownership and umask, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“chown vs chmod?”', 'A common first question.', 'do you separate who from what?',
        '''<ul>
          <li>chown: who owns it (owner, group). chmod: what each class may do.</li>
          <li>Owner change needs root.</li>
        </ul>''', 'mixing them up.') +
    scn('Web team', 'Junior', 'Uploads fail after a deploy', 'The deploy ran as root and re-created the uploads folder.', 'can you spot ownership?',
        '''<ol>
          <li><code>ls -ld uploads</code>: root:root 755.</li>
          <li><code>sudo chown www-data: uploads</code> (or the app user).</li>
          <li>Fix the deploy to set ownership, or run it as the deploy user.</li>
        </ol>''', 'chmod 777 uploads.') +
    scn('Operations', 'Mid-level', 'Logs readable by everyone', 'An app writes logs with secrets as 644.', 'do you know umask for services?',
        '''<ul>
          <li>Set <code>UMask=0027</code> in the systemd unit (or umask in the start script).</li>
          <li>chmod existing logs 640, group adm for readers.</li>
          <li>logrotate create 0640 user adm.</li>
        </ul>''', 'a cron job running chmod every minute.') +
    scn('Security team', 'Senior', 'Why can’t users chown?', 'A developer asks for chown rights “to give files to the build user”.', 'do you know the reasons?',
        '''<ul>
          <li>Users could dodge quotas, plant files that look like someone else’s, or create SUID files owned by others.</li>
          <li>Offer group-owned folders, ACLs or a sudo rule for one chown command on one path.</li>
        </ul>''', 'adding the developer to sudo.')
) + interview([
    ('What does chown :group file do?', 'Changes only the group.'),
    ('What are the default base modes?', '666 for files, 777 for folders.'),
    ('How do you see umask in symbolic form?', 'umask -S.'),
    ('Where is the system default umask set?', '/etc/login.defs (UMASK), pam_umask, /etc/profile.'),
    ('What happens to SUID/SGID when a normal user chgrps their program?', 'The kernel clears the bits.'),
    ('Who owns a file created with sudo?', 'root.'),
    ('Does umask affect existing files?', 'No, only new ones.'),
], [
    ('RHCSA (EX200)', '“Manage default file permissions” (umask) and ownership.'),
    ('LFCS', 'chown, chgrp, umask.'),
    ('CompTIA Linux+', 'Ownership commands and umask.'),
]) + distro('Same tools; defaults differ.', [
    ('Login umask', '0002 (pam_umask, private groups)', '0022 (RHEL 9: 0022; user private groups)', '0022', 'Git Bash: 0022'),
    ('chown USER: syntax', 'yes', 'yes', 'yes (BSD)', 'yes'),
    ('chown --reference', 'GNU', 'GNU', 'no', 'GNU'),
    ('Service umask', 'systemd UMask=', 'systemd UMask=', 'launchd Umask', '-'),
    ('Windows', '-', '-', '-', 'takeown, icacls /setowner'),
]) + teaser('9.4', 'Why can a normal user change their password when /etc/shadow is root-only? Why can everyone write to /tmp but not delete each other’s files? And how do new files in a team folder keep the team group? Next: SUID, SGID and the sticky bit.')

CHEATSHEET = cheatsheet('chown, chgrp, umask', [
    ('chown', [('chown u f', 'owner'), ('chown u:g f', 'both'), ('chown u: f', 'login group'), ('chown :g f', 'group'), ('-R -c -h', 'tree, report, link')]),
    ('chgrp', [('chgrp g f', 'group'), ('-R', 'tree'), ('member of g', 'or root'), ('--reference=F', 'copy'), ('stat -c %G', 'check')]),
    ('umask', [('umask', 'show'), ('umask -S', 'letters'), ('022', '644 / 755'), ('027', '640 / 750'), ('077 / 002', '600 / 664')]),
    ('Rules', [('only root', 'changes owner'), ('666 / 777', 'start modes'), ('umask removes', 'never adds'), ('sudo touch', 'root owns it'), ('UMask=', 'services')]),
])

MINDMAP = mindmap('Ownership', [
    ('chown', 'blue', ['u, u:g, u:, :g', '-R -c -h', 'root only']),
    ('chgrp', 'green', ['group only', 'owner + member', '-R']),
    ('umask', 'amber', ['666 / 777 base', 'removes bits', '022 027 077 002']),
    ('Where set', 'violet', ['.bashrc / .profile', 'login.defs, pam', 'systemd UMask=']),
    ('Gotchas', 'red', ['sudo → root files', 'cp → you own it', 'chgrp clears SUID']),
    ('Uses', 'acc', ['hand-overs', 'service files', 'team folders']),
])

LAB = lab('hand over and share', 'Build the lab, do the four tasks in your own terminal (sudo needed), then run the checker.',
    setup='''sudo rm -rf ~/lab93; mkdir -p ~/lab93/old/docs; cd ~/lab93
touch old/a.txt old/docs/b.txt; sudo touch rootfile.txt; sudo chown -R root:root old''',
    tasks=['Make yourself the owner (and your login group the group) of everything under <code>old</code>.',
           'Make <code>rootfile.txt</code> yours too.',
           'In a subshell with umask <code>077</code>, create <code>secret.txt</code> (it must be 600).',
           'Change the group of <code>old/a.txt</code> to <code>sudo</code> (a group you are in) without sudo.'],
    solution='''sudo chown -R $USER: old
sudo chown $USER: rootfile.txt
(umask 077; touch secret.txt)
chgrp sudo old/a.txt''',
    check='''cd ~/lab93
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 tree"     '[ -z "$(find old ! -user "$USER")" ]'
ok "2 rootfile" '[ "$(stat -c %U rootfile.txt)" = "$USER" ]'
ok "3 secret"   '[ "$(stat -c %a secret.txt 2>/dev/null)" = 600 ]'
ok "4 group"    '[ "$(stat -c %G old/a.txt)" = sudo ]' ''')
