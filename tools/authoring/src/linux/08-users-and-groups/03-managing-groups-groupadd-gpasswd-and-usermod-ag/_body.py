import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

GCLEAN = 'for g in labteam labold developers dbteam devs qa p1 p2 p3 p4 p5 p6; do sudo groupdel "$g" > /dev/null 2>&1; done; sudo usermod -g aman -G finance aman; sudo rm -rf /srv/projects'

import subprocess
subprocess.run(['bash', '-c', GCLEAN.replace('sudo ', '')])

HOOK = hook('Friday 6 p.m.: a developer asks to be added to the <code>docker</code> group. The admin types <code>sudo usermod -G docker riya</code>, leaves for the weekend, and on Monday Riya cannot use sudo, cannot read the shared folder and cannot deploy. One missing letter, <code>-a</code>, removed every other group. Groups are how Linux gives the same access to many people at once; managing them is simple, but you must know which commands <b>add</b>, which <b>replace</b> and when the change takes effect.',
    ['explain why groups exist, and the difference between primary and supplementary groups',
     'create, rename, renumber and delete groups with <code>groupadd</code>, <code>groupmod</code> and <code>groupdel</code>',
     'add and remove members safely with <code>usermod -aG</code>, <code>gpasswd -a/-d/-M</code> and group admins (<code>gpasswd -A</code>)',
     'build a shared project folder for a team, and make new group membership take effect (<code>newgrp</code>, re-login)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'one missing letter'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'What groups are', 5, 'simple meaning + 4 depths'),
    ('types', 'Add vs replace', 3, 'the safe and unsafe forms'),
    ('commands', 'Each command, by field', 15, 'options, real runs'),
    ('animation', 'See it happen', 4, '-G vs -aG animated'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'a team folder'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('Create a group', 'sudo groupadd NAME', '-g GID for a fixed number'),
    ('Add one user to a group (keep others)', 'sudo usermod -aG GROUP USER', 'or gpasswd -a USER GROUP'),
    ('Remove one user from a group', 'sudo gpasswd -d USER GROUP', 'cleanest way'),
    ('Set the exact member list', 'sudo gpasswd -M a,b,c GROUP', 'replaces members'),
    ('Let a team lead manage members', 'sudo gpasswd -A LEAD GROUP', 'no sudo for them'),
    ('Rename or renumber a group', 'sudo groupmod -n NEW / -g GID', 'files follow the GID'),
    ('Delete a group', 'sudo groupdel NAME', 'not a primary group'),
    ('Use a new group now', 'newgrp GROUP  /  log in again', 'groups load at login'),
    ('Who is in it?', 'getent group GROUP', 'members list'),
])

cmap = concept_map(
    [('8.1', 'Users and groups', '/etc/group, id'), ('8.2', 'Managing users', 'usermod'), ('3.1', 'Creating folders', 'mkdir')],
    ['why groups: same access for many people', 'groupadd, groupmod, groupdel', 'usermod -aG vs -G', 'gpasswd -a -d -M -A', 'newgrp and when membership applies'],
    [('8.4', 'sudo', 'the sudo group'), ('9.2', 'chmod', 'g+rw for a team'), ('9.3', 'chgrp', 'group owner'), ('9.4', 'SGID', 'team folders keep the group')],
    'A group is a named list of users. Give access to the group once, then manage people by adding or removing them.')

sc = (term(20, 14, 316, 156, ['$ sudo usermod -G docker riya', '$ id riya', ('groups=1000(riya),996(docker)', 'err'), ('(sudo is gone!)', 'err'), '$ sudo usermod -aG docker riya', ('groups=…,27(sudo),996(docker)', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'One letter matters:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• -G: replace the list', '• -aG: add to the list', '• gpasswd -a: add', '• gpasswd -d: remove', '• newgrp: use it now'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>One missing letter, a lost weekend</h2>
  <div class="story">
''' + puzzle('Riya runs <code>sudo usermod -aG developers riya</code>, then immediately <code>id</code>, and <code>developers</code> is not there. She runs <code>id riya</code> and it is there. Did the command work? And why does a note say “remove a user from a group: <code>sudo nano /etc/group</code>”: is that a good idea?') + '''
    <p class="narration">A team of three needs a shared folder. Riya is setting it up.</p>
''' + scene('A terminal: usermod -G docker removes the sudo group; usermod -aG docker keeps it.', sc,
            '<tspan font-weight="700" class="s-acc">-a</tspan> means append.') + '''
K> Why not give everyone access with chmod 777?
A> Because then everyone on the server has it, including the web server account. Make a group <code>developers</code>, give the folder to that group, and add exactly the people who need it.
R> And when someone moves teams?
A> <code>gpasswd -d</code> them from the group: one command, and every folder that group owns is closed to them. Today: create groups, add and remove members safely, and see why -G alone is dangerous.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A building where doors are labelled with team names; staff carry team badges; adding a badge to someone opens all that team’s doors, and the badge list for a team is the group.">'
       + label_box(14, 20, 190, 110, ['door: /srv/projects', 'opens for badge', '“developers”', '(group owner)'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['badge list', 'developers:', 'aman, neha', '(/etc/group)'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['add a badge', 'gpasswd -a riya', 'take it back', 'gpasswd -d riya'], 'amber', 8.6)
       + t(320, 160, 'Doors check badges, not names. Change the badge list,', 9.6, 'ink2')
       + t(320, 182, 'and every door of that team follows.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Groups at four depths', [
    ('v', 'No jargon: team badges', '      <p>A group is a team badge.</p>' + pic),
    ('b', 'The commands you will type', '''      <ul>
        <li><code>sudo groupadd developers</code>: a new team.</li>
        <li><code>sudo usermod -aG developers aman</code>: give Aman the badge (keep his others).</li>
        <li><code>sudo gpasswd -d aman developers</code>: take it back.</li>
        <li><code>getent group developers</code>: who has it.</li>
      </ul>'''),
    ('i', 'Primary vs supplementary, and when changes apply', '''      <ul>
        <li>Primary group (passwd field 4): one per user, becomes the group of new files. Change with <code>usermod -g</code>.</li>
        <li>Supplementary groups (members in /etc/group): extra access. <code>-G</code> sets the whole list, <code>-aG</code> adds to it.</li>
        <li><code>gpasswd</code> edits one membership at a time: <code>-a</code> add, <code>-d</code> delete, <code>-M</code> set all members, <code>-A</code> set group administrators who can then add/remove members without sudo.</li>
        <li>A running session keeps the groups it logged in with. New membership: log out and in, <code>newgrp GROUP</code> (a new shell with that group), or <code>su - $USER</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: GIDs, gshadow and limits', '''      <ul>
        <li>Files store only the GID. <code>groupmod -n</code> (rename) changes nothing on disk; <code>groupmod -g</code> (renumber) leaves existing files with the old number: fix them with <code>find / -gid OLD -exec chgrp NEW {} +</code>.</li>
        <li><code>/etc/gshadow</code> holds group administrators and (rarely used) group passwords: <code>name:password:admins:members</code>.</li>
        <li>groupdel refuses to delete any user’s primary group. Files owned by a deleted group keep the bare GID.</li>
        <li>The kernel keeps a process’s supplementary groups (up to 65536) in its credentials; NFSv3 with AUTH_SYS sends at most 16, a classic cause of “works locally, denied on NFS”.</li>
        <li>Some groups are powerful: <code>sudo</code>/<code>wheel</code> (root via sudo), <code>docker</code> and <code>lxd</code> (root-equivalent), <code>adm</code> (read logs), <code>disk</code> (raw disks). Audit them.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>groupadd, groupmod, groupdel, gpasswd and usermod -aG</h2>
''' + def_block(
    'A <b>group</b> is a named set of users with a GID, used to give several users the same access. <code>groupadd</code> creates a group, <code>groupmod</code> renames or renumbers it, and <code>groupdel</code> deletes it. Membership is changed with <code>usermod -aG</code> (append groups to a user) or <code>gpasswd</code> (add, remove or set members of a group). All need root, except gpasswd for a group’s administrators.',
    'Give access to a team once, then manage people by changing who is in the group.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Group', 'A named list of users with a GID.'),
    ('Member', 'A user listed in the group’s line of /etc/group.'),
    ('Primary group', 'The group in passwd field 4; owns new files.'),
    ('Supplementary group', 'Any extra group a user belongs to.'),
    ('Append (-a)', 'Add to the existing list instead of replacing it.'),
    ('Group admin', 'A user allowed to add/remove members (gpasswd -A).'),
    ('newgrp', 'Start a shell with a group you just joined.'),
    ('Shared folder', 'A folder owned by a group, writable by its members.'),
]) + '\n' + names('Where the names come from.', [
    ('groupadd', 'group add', 'Create.'),
    ('groupmod', 'group modify', 'Rename / renumber.'),
    ('groupdel', 'group delete', 'Remove.'),
    ('gpasswd', 'group password', 'Named for passwords, used for members.'),
    ('usermod -aG', 'append Groups', 'Add groups to a user.'),
    ('newgrp', 'new group', 'Switch active group.'),
    ('groupmems', 'group members', 'List/add members (shadow tools).'),
    ('wheel', 'big wheel', 'Old slang for an important person: admin group.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Create', '<code>sudo groupadd developers</code>'),
    ('Add member', '<code>sudo usermod -aG developers aman</code>'),
    ('Remove member', '<code>sudo gpasswd -d aman developers</code>'),
    ('Members', '<code>getent group developers</code>'),
    ('Delete', '<code>sudo groupdel developers</code>'),
    ('Apply now', '<code>newgrp developers</code>'),
]) + '\n' + lv + didyou('The name <code>wheel</code> for the admin group comes from 1970s slang “big wheel” (an important person). Fedora and RHEL still use it; Ubuntu calls it <code>sudo</code>.') + '''
EXAM> “Add user tom to the group wheel without removing his other groups.” → <code>usermod -aG wheel tom</code> (or <code>gpasswd -a tom wheel</code>). Check with <code>id tom</code>.
''' + qc('Why give a folder to a group instead of to each user?', 'You change access in one place (the member list) instead of on every folder, and nobody else gets access.') + mistake('“To remove a user from a group: sudo nano /etc/group”',
    'Use <code>sudo gpasswd -d USER GROUP</code>. If you must edit, use <code>sudo vigr</code> (and <code>sudo vigr -s</code> for gshadow), which locks the file and checks it.',
    'nano does not lock the file and does not update /etc/gshadow; a typo can break every group lookup. gpasswd -d is the recommended way, as the notes also say.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Commands that add, and commands that replace</h2>
''' + table(['Command', 'What it changes', 'Other groups/members', 'Safe for adding one person?'], [
    ['<code>usermod -aG g user</code>', 'adds g to user', 'kept', 'yes'],
    ['<code>usermod -G g user</code>', 'sets user’s whole list to g', '<b>removed</b>', 'no'],
    ['<code>gpasswd -a user g</code>', 'adds user to g', 'kept', 'yes'],
    ['<code>gpasswd -d user g</code>', 'removes user from g', 'kept', 'yes (removing)'],
    ['<code>gpasswd -M a,b g</code>', 'sets g’s whole member list', '<b>others removed</b>', 'no (sets the list)'],
    ['<code>usermod -g g user</code>', 'changes the primary group', 'supplementary kept', 'different purpose'],
], minw=600) + table(['', 'usermod -aG', 'gpasswd -a / -d'], [
    ['Point of view', 'the user (“give riya these groups”)', 'the group (“add riya to this group”)'],
    ['Several groups at once', 'yes: <code>-aG a,b,c</code>', 'one group per command'],
    ['Remove', 'no (only by resetting with -G)', 'yes: <code>-d</code>'],
    ['Without sudo', 'no', 'yes, for group admins (<code>-A</code>)'],
], minw=520) + qc('Which command could silently remove a user from sudo?', '<code>usermod -G something user</code> without <code>-a</code>, or <code>gpasswd -M</code> on the sudo group with a list that leaves them out.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine (users riya and aman). Each example starts from a clean state.</p>
''' + cmdcard_u(['a new team, project or role', 'a fixed GID that must match on every server', 'scripts that create a group only if missing'],
               ['one group per person for shared access (use one team group)'])(
    'groupadd', 'groupadd · groupmod · groupdel', 'create, change, delete groups',
    '<code>groupadd</code> adds a line to /etc/group and /etc/gshadow. <code>groupmod</code> renames (<code>-n</code>) or renumbers (<code>-g</code>) it. <code>groupdel</code> removes it, unless it is someone’s primary group.',
    'sudo groupadd [-g GID] [-r] [-f] NAME   ·   sudo groupmod [-n NEW] [-g GID] NAME   ·   sudo groupdel NAME', 'change',
    [('groupadd NAME', 'next free GID ≥ 1000', 'teams'),
     ('-g 2000', 'fixed GID', 'same on all servers / NFS'),
     ('-r', 'system group (GID < 1000)', 'services'),
     ('-f', 'no error if it exists', 'scripts'),
     ('groupmod -n new old', 'rename (files keep working)', 'team renamed'),
     ('groupmod -g 2100 g', 'renumber (old files keep old GID!)', 'rare'),
     ('groupdel g', 'delete', 'cleanup')],
    dict(setup=GCLEAN, cmd='sudo groupadd developers\nsudo groupadd -g 2000 dbteam\ngetent group developers dbteam', note='developers got the next free GID; dbteam got 2000 because we asked.'),
    [('sys', [
        dict(situation='Create only if missing (safe to run twice).', setup=GCLEAN, cmd='sudo groupadd developers\nsudo groupadd developers; echo "exit $?"\nsudo groupadd -f developers; echo "with -f: exit $?"', expect='any',
             why='-f makes the script idempotent: the same result however many times it runs.'),
        dict(situation='The team was renamed: rename the group, files follow.', setup=GCLEAN + '; sudo groupadd developers; sudo mkdir -p /srv/projects; sudo chgrp developers /srv/projects', cmd='sudo groupmod -n devs developers\nls -ld /srv/projects\ngetent group devs',
             why='Files store the GID, which did not change, so ls now prints the new name.')]),
     ('devops', [
        dict(situation='Renumbering leaves old files behind.', setup=GCLEAN + '; sudo groupadd -g 2000 dbteam; sudo mkdir -p /srv/projects; sudo chgrp dbteam /srv/projects', cmd='sudo groupmod -g 2100 dbteam\nls -ld /srv/projects\nsudo find /srv -gid 2000 -exec chgrp dbteam {} +\nls -ld /srv/projects',
             why='After -g the folder shows the bare number 2000 until you chgrp the files. Plan GIDs before creating data.')]),
     ('sec', [
        dict(situation='A user’s primary group cannot be deleted.', cmd='sudo groupdel aman; echo "exit $?"', expect='any',
             why='Delete or change the user first (Lesson 8.2).')]),
    ],
    sudo=True
) + cmdcard_u(['giving a user one or more extra groups', 'onboarding: “add Neha to docker and developers”'],
               ['-G without -a', 'removing a single group (use gpasswd -d)'])(
    'usermod-ag', 'usermod -aG · usermod -g', 'add groups to a user',
    '<code>-aG</code> appends groups to the user’s supplementary list. <code>-G</code> alone <b>replaces</b> the list. <code>-g</code> changes the primary group.',
    'sudo usermod -aG G1[,G2…] USER   ·   sudo usermod -g GROUP USER', 'change',
    [('-aG developers aman', 'add one group', 'access'),
     ('-aG a,b,c user', 'add several', 'onboarding'),
     ('-G a user', 'replace list with a only', 'rarely what you want'),
     ('-G "" user', 'remove all supplementary groups', 'offboarding'),
     ('-g finance aman', 'primary group = finance', 'new files get finance')],
    dict(setup=GCLEAN + '; sudo groupadd developers', cmd='id aman\nsudo usermod -aG developers aman\nid aman\nsudo usermod -G developers aman\nid aman', note='With -aG Aman kept finance. With -G alone finance disappeared: the opening story.'),
    [('dev', [
        dict(situation='Several groups in one command.', setup=GCLEAN + '; sudo groupadd developers; sudo groupadd qa', cmd='sudo usermod -aG developers,qa aman\nid -Gn aman',
             why='Comma separated, no spaces.')]),
     ('data', [
        dict(situation='New files should belong to the team, not the person.', setup=GCLEAN, cmd='sudo usermod -g finance aman\nsudo -u aman touch /tmp/q3.csv; ls -l /tmp/q3.csv\nsudo rm /tmp/q3.csv; sudo usermod -g aman -G finance aman',
             why='The primary group owns new files. For a shared folder, SGID is usually better (Lesson 9.4).')]),
    ],
    sudo=True
) + mistake('sudo usermod -G docker riya', 'sudo usermod -aG docker riya',
            'Without -a the user loses every other supplementary group, including sudo. If it happened to you, ask another admin, or use recovery mode, and re-add with -aG.') + cmdcard_u(['removing one user from one group', 'setting a group’s exact members', 'letting a team lead manage membership'],
               ['-M when you meant to add one person'])(
    'gpasswd', 'gpasswd', 'manage members of a group',
    'Works from the group’s point of view: <code>-a</code> adds a user, <code>-d</code> removes one, <code>-M</code> sets the full member list, <code>-A</code> sets group administrators, who may then run <code>gpasswd -a/-d</code> on that group without sudo.',
    'sudo gpasswd -a USER GROUP   ·   -d USER GROUP   ·   -M U1,U2 GROUP   ·   -A ADMIN GROUP', 'change',
    [('-a riya developers', 'add', 'one person'),
     ('-d riya developers', 'remove', 'moved teams'),
     ('-M aman,riya developers', 'set exact members', 'from an HR list'),
     ('-A aman developers', 'aman becomes group admin', 'delegate'),
     ('groupmems -g G -l', 'list members', 'alternative')],
    dict(setup=GCLEAN + '; sudo groupadd developers', cmd='sudo gpasswd -a riya developers\nsudo gpasswd -a aman developers\ngetent group developers\nsudo gpasswd -d riya developers\ngetent group developers', note='gpasswd announces each change; only the named user is affected.'),
    [('sys', [
        dict(situation='Set the member list from the team roster.', setup=GCLEAN + '; sudo groupadd developers; sudo gpasswd -a riya developers > /dev/null', cmd='sudo gpasswd -M aman developers\ngetent group developers',
             why='-M replaces: riya is gone because she is not on the roster. Exactly right for syncing, wrong for adding one person.')]),
     ('devops', [
        dict(situation='The team lead manages the group without sudo.', setup=GCLEAN + '; sudo groupadd developers; sudo gpasswd -a aman developers > /dev/null', cmd='sudo gpasswd -A aman developers\nsudo grep "^developers:" /etc/gshadow\nsudo -u aman gpasswd -a riya developers\ngetent group developers',
             why='The admin list is in /etc/gshadow (field 3). Aman added riya without root rights.')]),
     ('sec', [
        dict(situation='Remove a leaver from every powerful group.', setup=GCLEAN + '; sudo groupadd developers; sudo usermod -aG developers aman', cmd="for g in $(id -Gn aman); do [ \"$g\" = aman ] || sudo gpasswd -d aman \"$g\"; done\nid aman",
             why='Leaves only the private group. (Lesson 8.2: also lock and expire the account.)')]),
    ],
    sudo=True
) + cmdcard_u(['using a group you were just added to, without logging out', 'checking a membership change'],
               ['scripts (newgrp starts an interactive shell)'])(
    'newgrp', 'newgrp · id · su -', 'make a new group take effect',
    'Groups are loaded when a session starts. <code>newgrp GROUP</code> starts a new shell whose primary group is GROUP (only if you are a member). <code>su - $USER</code> or logging in again loads the full new list.',
    'newgrp GROUP   ·   id   ·   id USER   ·   su - USER', 'safe',
    [('id', 'groups of this shell', 'what you have now'),
     ('id USER', 'groups from the files', 'what you will have'),
     ('newgrp developers', 'shell with that group', 'use it now'),
     ('exit', 'leave the newgrp shell', 'back'),
     ('sudo -iu USER id', 'fresh login view', 'check for someone else')],
    dict(setup=GCLEAN + '; sudo groupadd developers', cmd='sudo usermod -aG developers riya\nid -Gn         # this running shell\nid -Gn riya    # the account files\nsudo gpasswd -d riya developers > /dev/null', note='The shell that is already running does not see the new group; the files do. That is the puzzle.'),
    [('qa', [
        dict(situation='Check a user’s groups as they will be at their next login.', setup=GCLEAN + '; sudo groupadd developers; sudo usermod -aG developers aman', cmd='sudo -iu aman id -Gn',
             why='sudo -i simulates a full login, so it loads the current groups.')]),
    ]
) + undo('Group changes are reversible, except deleting data or renumbering carelessly.', [
    ('Lost groups with usermod -G:', 'add them back with <code>usermod -aG a,b,c</code>; old list in <code>/etc/group-</code> (backup).'),
    ('Removed the wrong member:', '<code>gpasswd -a USER GROUP</code>.'),
    ('Deleted a group by mistake:', 'recreate it with the <b>same GID</b> (<code>groupadd -g N</code>): files come back to it.'),
    ('Renumbered a group:', '<code>find / -xdev -gid OLD -exec chgrp NEW {} +</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='sudo groupadd finance', meaning='The group already exists (exit 9).', fix='Use it, or <code>groupadd -f</code> in scripts.'),
    dict(cmd='sudo gpasswd -a aman nosuchgroup', meaning='No such group (exit 3).', fix='Create it with groupadd first.'),
    dict(cmd='sudo usermod -aG nosuchgroup aman', meaning='-G names a missing group (exit 6).', fix='Check with <code>getent group NAME</code>.'),
    dict(cmd='sudo groupdel riya', meaning='It is a user’s primary group (exit 8).', fix='Change the user’s primary group, or delete the user.'),
]) + qc('You need to add Neha to docker and developers in one command. Which?', '<code>sudo usermod -aG docker,developers neha</code>') + '''
'''

SCREENS = screens_block('Real terminal screens: newgrp', 'After joining a group, newgrp starts a new shell that has it. exit returns to the old one.',
    GCLEAN + "; sudo groupadd developers; sudo usermod -aG developers riya; printf '%s\\n' 'PS1=\"riya@web01:~$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'id -gn; id -Gn' Enter", ' after <code>id -gn; id -Gn</code>: the old session has no developers.'),
    ('Enter', "'newgrp developers' Enter 'id -gn' Enter", ' after <code>newgrp developers</code> and <code>id -gn</code>: the new shell’s primary group.'),
], 72, 9, hid='screens', what='bash')

cards = cards + SCREENS + '</section>\n'

def grp(k, mode, note, tone):
    before = ['riya', 'sudo', 'finance']
    if k == 0:
        cur = before
    elif mode == 'G':
        cur = ['riya', 'docker']
    else:
        cur = before + ['docker']
    o = label_box(14, 14, 150, 30, [f'usermod -{"G" if mode == "G" else "aG"} docker'], 'red' if mode == 'G' else 'green', 8)
    for i, g in enumerate(cur):
        tn = 'acc' if g == 'docker' else ('blue' if g == 'riya' else 'card')
        o += label_box(14 + i * 82, 60, 74, 30, [g], tn, 8)
    if k and mode == 'G':
        o += t(180, 112, 'sudo and finance removed', 8.4, 'red', bold=True)
    return o + t(180, 140, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, [f'$ sudo usermod {m} docker riya', '$ id -Gn riya'] + ([(r, 'out')] if r else []), title='riya@web01', prompt='riya@web01:~$', size=8) + cap(c, '', 'card', y=150, h=34)
       for m, r, c in [('-G', '', 'Before.'), ('-G', 'riya docker', 'With -G: only docker left!'), ('-aG', '', 'Try again with -aG…'), ('-aG', 'riya sudo finance docker', '…docker added, nothing lost.')]]
behind = [grp(0, 'G', 'Current list: riya, sudo, finance.', 'violet'), grp(1, 'G', '-G writes a NEW list.', 'red'),
          grp(0, 'aG', 'Start again from the same list.', 'violet'), grp(1, 'aG', '-a appends to the existing list.', 'green')]
two = anim_two('-G versus -aG', 'Behind the screen: replace or append',
               'A terminal running usermod with -G and then with -aG.',
               'Boxes showing riya’s group list: with -G it becomes riya and docker only; with -aG docker is added and the rest stay.', see, behind,
               ['Before.', 'Replace.', 'Again.', 'Append.'],
               ['1. old list', '2. -G: list replaced', '3. old list', '4. -aG: list + docker'])

def apply(k, note, tone):
    o = label_box(14, 14, 150, 50, ['/etc/group', 'developers:…:riya' if k >= 1 else 'developers:…:'], 'green' if k >= 1 else 'card', 8)
    o += label_box(196, 14, 150, 50, ['running shell', 'groups: riya sudo' + (' developers' if k >= 3 else '')], 'green' if k >= 3 else ('amber' if k >= 2 else 'card'), 8)
    if k >= 2:
        o += arrow(166, 40, 192, 40)
    return o + t(180, 110, note, 8.6, tone, bold=True)
frames = [apply(0, 'riya is logged in. Groups were loaded at login.', 'violet'), apply(1, 'usermod -aG writes riya into /etc/group.', 'green'),
          apply(2, 'The running shell still has its old list.', 'amber'), apply(3, 'newgrp / new login reads the files again.', 'green')]
s1 = anim_one('Animated example', 'When does a new group start working?',
              'The files change immediately; your session does not.',
              'session vs files', 'Two boxes: /etc/group gets the new member at once, the running shell only after newgrp or a new login.', frames,
              ['Login loads groups.', 'Files updated.', 'Old session unchanged.', 'New session has it.'], hid='scenario-apply')

dx = dissect('Layer by layer: where a membership lives',
    'Each layer has a real command and output from our build machine.', [
    dict(key='group', name='/etc/group', sub='members', why='Who is in each group.', how='4th field, comma list.', impl='groupadd, gpasswd, usermod.', used='Every login.',
         cmd="grep -E '^(sudo|finance):' /etc/group"),
    dict(key='gshadow', name='/etc/gshadow', sub='admins', why='Group admins, passwords.', how='root only.', impl='gpasswd -A.', used='Delegation.',
         cmd="sudo grep -E '^(sudo|finance):' /etc/gshadow"),
    dict(key='passwd', name='/etc/passwd', sub='primary group', why='One group per user.', how='Field 4 GID.', impl='usermod -g.', used='New files.',
         cmd="getent passwd aman | cut -d: -f1,4"),
    dict(key='proc', name='Process', sub='/proc/self/status', why='What the kernel checks.', how='Set at login.', impl='setgroups().', used='Permission checks.',
         cmd="grep '^Groups' /proc/self/status"),
], hint='From files to a running process. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Replace vs append, and when membership applies</h2>
''' + two + s1 + dx + qc('A user was added to developers an hour ago and still gets “Permission denied” in the folder. First thing to try?', 'Log out and back in (or newgrp developers); check with <code>id</code> in that session.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Groups at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['/srv/projects', 'developers'], 'blue', 8.6), '1. Team folders',
              'One group per team owns its shared folders; people join and leave the group.', ['New team', '*groupadd', 'folder']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['sudo / wheel', 'docker'], 'red', 8.6), '2. Privileged groups',
    'Admin rights come from membership in sudo, wheel or docker; audits review those lists.', ['Audit', '*getent group', 'trim']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['adm', 'logs'], 'green', 8.6), '3. Read-only access',
    'Support staff join adm to read /var/log without becoming admins.', ['Support', '*-aG adm', 'read logs']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['GID 2000', 'NFS'], 'amber', 8.6), '4. Shared storage',
    'Fixed GIDs keep group ownership correct across servers and NFS.', ['Plan', '*groupadd -g', 'consistent']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['gpasswd -A', 'lead'], 'violet', 8.6), '5. Delegation',
    'Team leads manage their own group without root rights.', ['Lead', '*gpasswd -a', 'no ticket']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='My groups', scenario='Names only.', cmd='id -Gn', explain='-G -n.'),
    dict(level='b', title='Members of sudo', scenario='Who is an admin?', cmd='getent group sudo | cut -d: -f4', explain='Field 4.'),
    dict(level='i', title='Groups with members', scenario='Only groups that list someone.', cmd="awk -F: '$4!=\"\" {print $1\": \"$4}' /etc/group", explain='awk on field 4.'),
    dict(level='i', title='Is aman in finance?', scenario='Exact match for a script.', cmd="id -Gn aman | tr ' ' '\\n' | grep -qx finance && echo yes || echo no", explain='grep -x.'),
    dict(level='a', title='Users per group, most first', scenario='Team sizes.', cmd="awk -F: '$4!=\"\" {print gsub(/,/,\",\",$4)+1, $1}' /etc/group | sort -rn", explain='Count commas + 1.'),
], extra=build_up('a shared team folder', 'Riya creates a developers group and a folder that only members can use.', GCLEAN, [
    ('sudo groupadd developers', '1. The team group.'),
    ('sudo gpasswd -a aman developers', '2. Aman joins.'),
    ('sudo mkdir -p /srv/projects && sudo chgrp developers /srv/projects && sudo chmod 2770 /srv/projects', '3. Folder owned by the group (2770: Lesson 9.4).'),
    ('ls -ld /srv/projects; sudo -u aman touch /srv/projects/plan.md && sudo ls -l /srv/projects; ls /srv/projects 2>&1', '4. Aman can write; riya (not a member) cannot even list it.'),
], cumulative=True, expect='any')) + which('Choosing the right command.', [
    ('Add one person', 'usermod -aG / gpasswd -a', 'Keeps others.', 'usermod -G.'),
    ('Remove one person', 'gpasswd -d', 'One membership.', 'nano /etc/group.'),
    ('Sync from a roster', 'gpasswd -M', 'Exact list.', 'Many -a/-d.'),
    ('Delegate', 'gpasswd -A', 'Lead manages.', 'Giving sudo.'),
    ('Rename team', 'groupmod -n', 'Files follow.', 'New group + chgrp.'),
    ('Use it now', 'newgrp / re-login', 'Loads groups.', 'Rebooting.'),
    ('Edit by hand', 'vigr / vigr -s', 'Locked + checked.', 'Plain editors.'),
]) + keys('Handy forms.', [
    ('usermod -aG a,b u', 'several groups', 'onboarding'),
    ('gpasswd -d u g', 'remove', 'offboarding'),
    ('getent group g', 'members', 'check'),
    ('groupadd -f g', 'create if missing', 'scripts'),
    ('id u vs id', 'files vs session', 'debug'),
    ('newgrp g', 'shell with g', 'right now'),
]) + scriptit('team-sync.sh', 'Keep a group’s members equal to a roster file: report who will be added and removed, then apply with gpasswd -M.',
'''sudo groupadd -f developers
printf 'aman\\nriya\\n' > roster.txt
current=$(getent group developers | cut -d: -f4 | tr ',' '\\n' | grep . | sort)
echo "remove: $(comm -23 <(echo "$current") <(sort roster.txt) | tr '\\n' ' ')"
echo "add:    $(comm -13 <(echo "$current") <(sort roster.txt) | tr '\\n' ' ')"
sudo gpasswd -M "$(paste -sd, roster.txt)" developers
getent group developers
sudo groupdel developers''',
'<p>comm compares the two sorted lists (Lesson 6.3); paste -sd, joins the roster with commas.</p>') + puzzle_answer('Yes, it worked: <code>id riya</code> reads /etc/group, which already lists her. Plain <code>id</code> shows the groups of the <b>running</b> shell, loaded at login. Log in again or run <code>newgrp developers</code>. And editing /etc/group with nano is risky (no lock, no check, gshadow not updated): use <code>gpasswd -d</code>, or <code>vigr</code> if you must edit.') + qc('What does <code>gpasswd -M aman developers</code> do to the other members?', 'Removes them: -M sets the complete member list.') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-managing-users-useradd-usermod-userdel-passwd/">Lesson 8.2</a> (usermod).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
