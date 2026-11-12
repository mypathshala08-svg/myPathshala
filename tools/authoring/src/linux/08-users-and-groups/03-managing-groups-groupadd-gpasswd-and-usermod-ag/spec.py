import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='08-users-and-groups', lesson='03-managing-groups-groupadd-gpasswd-and-usermod-ag', n='8.3',
    module_label='Module 8 · Users, groups and sudo',
    title='Managing groups: groupadd, gpasswd and usermod -aG',
    desc='Why groups exist; primary vs supplementary groups; groupadd (-g -r -f), groupmod (-n -g) and groupdel; adding members with usermod -aG (and why -G alone removes groups), gpasswd -a -d -M -A, /etc/gshadow, newgrp and when membership takes effect; a shared team folder, with real outputs and animations.',
    og_desc='Create groups and add or remove members safely with groupadd, usermod -aG and gpasswd, and see why usermod -G removes other groups.',
    minutes=36, level='Beginner → Advanced',
    lead='Groups give the same access to many people at once. This lesson explains groupadd, groupmod, groupdel, usermod -aG and gpasswd, the difference between adding and replacing, and how admins, DevOps, data teams and security use groups every day.',
    chips=['-G vs -aG animated', 'A shared team folder', 'Errors decoded', 'Practice lab with checker', 'Real outputs'],
)

MAIN = """# Read groups and memberships
id -Gn
getent group root sudo
awk -F: '$4!="" {print $1": "$4}' /etc/group
grep -c . /etc/group
"""

RUN = dict(
    heading='Your groups and the group file',
    intro='<p>Changing groups needs root, so here you read them. The real changes are in the cards above and in the lab.</p>',
    code=MAIN,
    anno=[("awk -F: '$4!=\"\" {print $1\": \"$4}' /etc/group", 'Groups that list members.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which groups have members?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> what is the GID of root’s group? Then run.', code="getent group root | cut -d: -f3\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> this should print the members field (4th) of sudo.', code="getent group sudo | cut -d: -f3\n"),
        dict(label='4 · Your turn', hint='Print the names of all groups with a GID below 100.', code="awk -F: '$3<100 {print $1}' /etc/group\n"),
        dict(label='5 · Challenge', hint='Print your primary group name, and separately your other groups.', code="echo \"primary: $(id -gn)\"\necho \"others: $(id -Gn | cut -d' ' -f2-)\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: a team group',
    intro='<p>Use test names. Outputs were <b>recorded</b> on our Ubuntu 24.04 build machine.</p>',
    items=[
        dict(title='1 · Create a group', cmd='sudo groupadd testteam && getent group testteam', output=pc('sudo groupdel testteam >/dev/null 2>&1; sudo groupadd testteam && getent group testteam'), note='Recorded (GID differs on your PC).'),
        dict(title='2 · Add yourself (keep other groups)', cmd='sudo usermod -aG testteam $USER && id -Gn $USER', output=pc('sudo usermod -aG testteam riya && id -Gn riya'), note='Recorded as riya.'),
        dict(title='3 · Use it now', cmd='newgrp testteam   # then: id -gn ; exit', output='testteam', note='Typical.'),
        dict(title='4 · Remove yourself and the group', cmd='sudo gpasswd -d $USER testteam && sudo groupdel testteam', output=pc('sudo gpasswd -d riya testteam && sudo groupdel testteam'), note='Recorded.'),
        dict(title='5 · Groups on a fresh Ubuntu desktop', cmd='id -Gn', output='vineeta adm cdrom sudo dip plugdev users lpadmin', note='Typical: the installer adds the first user to these.'),
    ],
)

TRACE = dict(
    heading='Checking membership in a script',
    intro='<p>Step through a script that checks whether users are in a group.</p>',
    code='''g=sudo
members=$(getent group "$g" | cut -d: -f4)
for u in riya aman; do
  case ",$members," in *",$u,"*) echo "$u is in $g";; *) echo "$u is not in $g";; esac
done
''',
    notes={1: 'Group.', 2: 'Members :: comma list from field 4.', 3: 'Loop.', 4: 'Match :: commas around avoid partial matches.'},
)

WORKED_INTRO = 'Three tasks from real jobs, recorded with sudo: a new team, a role change and an audit.'
EXAMPLES = [
    dict(level='b', tag='Sysadmin', title='A new team group',
         problem='<p>Create group qa with GID 2500 and add aman and riya.</p>',
         inp='nothing yet', approach=['groupadd -g.', 'gpasswd -a each.'],
         code='''sudo groupdel qa > /dev/null 2>&1
sudo groupadd -g 2500 qa
sudo gpasswd -a aman qa; sudo gpasswd -a riya qa
getent group qa
sudo groupdel qa
''', notes={2: 'Fixed GID.', 3: 'Members.', 4: 'Check.'}, tryit='Use gpasswd -M aman,riya instead.'),
    dict(level='i', tag='Help desk', title='Role change',
         problem='<p>Aman moves from finance to qa: remove one group, add the other, keep the rest.</p>',
         inp='aman in finance', approach=['gpasswd -d.', 'usermod -aG.'],
         code='''sudo groupadd -f qa
sudo gpasswd -d aman finance
sudo usermod -aG qa aman; id -Gn aman
sudo gpasswd -a aman finance > /dev/null; sudo gpasswd -d aman qa > /dev/null; sudo groupdel qa
''', notes={2: 'Out of finance.', 3: 'Into qa :: other groups kept.'}, tryit='Check with sudo -iu aman id.'),
    dict(level='a', tag='Security', title='Audit privileged groups',
         problem='<p>List members of sudo, adm, docker and wheel (if present), and flag any group that is someone’s primary group too.</p>',
         inp='/etc/group', approach=['getent per group.', 'Mark missing groups.'],
         code='''for g in sudo adm docker wheel; do
  line=$(getent group "$g") || { echo "$g: (no such group)"; continue; }
  echo "$g: ${line##*:}"
done
''', notes={1: 'Powerful groups.', 2: 'Lookup :: continue if missing.', 3: 'Members :: ${line##*:} = text after the last colon.'}, tryit='Add lxd and disk.'),
]

QUIZ = mix([
    dict(q='Which adds aman to developers without removing his other groups?', options=['usermod -G developers aman', 'usermod -aG developers aman', 'groupadd aman developers', 'gpasswd -M aman developers'], answer=1, why='-a appends.'),
    dict(q='What does usermod -G docker riya do to riya’s sudo membership?', options=['keeps it', 'removes it', 'makes it primary', 'nothing'], answer=1, why='-G replaces the list.'),
    dict(q='Cleanest way to remove one user from one group?', options=['gpasswd -d USER GROUP', 'groupdel GROUP', 'nano /etc/group', 'userdel -G'], answer=0, why='One membership only.'),
    dict(q='You were just added to a group. Your open terminal does not show it. Why?', options=['the change failed', 'groups load at login', 'needs reboot', 'needs sudo id'], answer=1, why='newgrp or log in again.'),
    dict(q='Which lets a team lead add members without sudo?', options=['gpasswd -A lead group', 'usermod -aG sudo lead', 'chmod g+w /etc/group', 'groupmod -a'], answer=0, why='Group administrator.'),
    dict(q='groupmod -n devs developers: what happens to files owned by developers?', options=['they lose their group', 'they show the new name', 'they must be chgrp’d', 'they are deleted'], answer=1, why='Same GID, new name.'),
    dict(q='Why can’t you groupdel riya?', options=['it has members', 'it is riya’s primary group', 'it is a system group', 'needs -f'], answer=1, why='Exit 8.'),
    dict(q='Which file stores group administrators?', options=['/etc/group', '/etc/gshadow', '/etc/passwd', '/etc/login.defs'], answer=1, why='Field 3 of gshadow.'),
])

REVISION = [
    'Groups give many users the same access. One primary group (passwd field 4), many supplementary (/etc/group field 4).',
    '<code>groupadd [-g GID] [-r] [-f]</code>, <code>groupmod -n NEW / -g GID</code>, <code>groupdel</code> (not a primary group).',
    '<code>usermod -aG a,b USER</code> adds; <b><code>-G</code> alone replaces</b>; <code>-g</code> changes primary.',
    '<code>gpasswd -a USER G</code>, <code>-d USER G</code>, <code>-M a,b G</code> (sets list), <code>-A LEAD G</code>.',
    'Membership applies at the next login: <code>newgrp G</code>, <code>su - $USER</code>; <code>id</code> (session) vs <code>id USER</code> (files).',
    'Edit by hand only with <code>vigr</code>/<code>vigr -s</code>. Powerful groups: sudo, wheel, docker, adm.',
]

FAQ = [
    ('How do I add a user to a group in Linux?', 'sudo usermod -aG GROUP USER (or sudo gpasswd -a USER GROUP), then the user logs in again.'),
    ('How do I remove a user from a group?', 'sudo gpasswd -d USER GROUP.'),
    ('What is the difference between usermod -G and usermod -aG?', '-G replaces all supplementary groups; -aG appends to them.'),
    ('How do I list members of a group?', 'getent group GROUP (field 4), or groupmems -g GROUP -l.'),
    ('How do I create a group with a specific GID?', 'sudo groupadd -g 2000 NAME.'),
    ('Why doesn’t my new group work?', 'Groups are loaded at login: log out and in, or run newgrp GROUP.'),
    ('How do I rename a group?', 'sudo groupmod -n NEW OLD (files keep working because the GID is the same).'),
]

PRACTICE_INTRO = 'Small group tasks (with sudo). Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='My groups', stmt='Print your group names.', inp='you', code="id -Gn\n", explain='-Gn.'),
    dict(level='easy', title='Members of finance', stmt='Print the members of finance.', inp='/etc/group', code="getent group finance | cut -d: -f4\n", explain='Field 4.'),
    dict(level='easy', title='Primary group', stmt='Print aman’s primary group name.', inp='aman', code="id -gn aman\n", explain='-g -n.'),
    dict(level='medium', title='Create and show', stmt='Create group p1 with GID 2600, show it, delete it.', inp='nothing',
         code="sudo groupdel p1 > /dev/null 2>&1; sudo groupadd -g 2600 p1\ngetent group p1\nsudo groupdel p1\n", explain='-g.'),
    dict(level='medium', title='Append', stmt='Add aman to a new group p2 and show that finance is kept.', inp='aman',
         code="sudo groupadd -f p2; sudo usermod -aG p2 aman\nid -Gn aman\nsudo gpasswd -d aman p2 > /dev/null; sudo groupdel p2\n", explain='-aG.'),
    dict(level='medium', title='Remove one', stmt='Add riya to p3, then remove her with gpasswd.', inp='riya',
         code="sudo groupadd -f p3; sudo gpasswd -a riya p3\nsudo gpasswd -d riya p3\ngetent group p3; sudo groupdel p3\n", explain='-a / -d.'),
    dict(level='business', title='Exact roster', stmt='Set p4’s members to exactly aman and riya.', inp='a roster',
         code="sudo groupadd -f p4; sudo gpasswd -M aman,riya p4\ngetent group p4 | cut -d: -f4; sudo groupdel p4\n", explain='-M.'),
    dict(level='business', title='Rename', stmt='Rename p5 to p6 and show the GID did not change.', inp='a group',
         code="for g in p5 p6; do sudo groupdel $g > /dev/null 2>&1; done; sudo groupadd -g 2700 p5\nsudo groupmod -n p6 p5; getent group p6; sudo groupdel p6\n", explain='-n.'),
]

SCN_INTRO = 'Interview questions about groups, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“Add user tom to group developers.”', 'Asked to check -a.', 'do you know -aG?',
        '''<ul>
          <li><code>sudo usermod -aG developers tom</code> (or gpasswd -a tom developers).</li>
          <li>Explain why -a matters.</li>
          <li>tom must log in again.</li>
        </ul>''', 'usermod -G developers tom.') +
    scn('Help desk', 'Junior', '“After the docker change I cannot use sudo”', 'Someone ran usermod -G docker on the user.', 'can you recover?',
        '''<ol>
          <li>Another admin (or root/recovery mode) runs <code>usermod -aG sudo,docker USER</code>.</li>
          <li>Compare with <code>/etc/group-</code> for other lost groups.</li>
          <li>Teach -aG; prefer gpasswd -a in runbooks.</li>
        </ol>''', '“reinstall sudo”.') +
    scn('Platform', 'Mid-level', 'Team folder permissions keep breaking', 'Files created by one developer cannot be edited by others.', 'do you know primary groups and SGID?',
        '''<ul>
          <li>New files get the creator’s primary group; set SGID on the folder (<code>chmod 2770</code>) so they get the team group (Lesson 9.4).</li>
          <li>umask 002 for group write (Lesson 9.3), or default ACLs (9.5).</li>
        </ul>''', 'a cron job running chmod -R 777.') +
    scn('Security team', 'Senior', 'Who can become root?', 'An audit needs every path to root.', 'do you know root-equivalent groups?',
        '''<ul>
          <li>sudo/wheel members and sudoers rules (Lesson 8.4).</li>
          <li>docker, lxd, libvirt, disk groups: root-equivalent.</li>
          <li>Review monthly; manage from a central directory.</li>
        </ul>''', 'only checking the sudo group.')
) + interview([
    ('Primary vs supplementary group?', 'Primary: one, owns new files; supplementary: extra access.'),
    ('How do you create a system group?', 'groupadd -r NAME.'),
    ('What does gpasswd -M do?', 'Sets the complete member list.'),
    ('Where are group admins stored?', '/etc/gshadow.'),
    ('How do you see members of a group?', 'getent group NAME.'),
    ('What happens to files if you delete a group?', 'They keep the bare GID.'),
    ('Why is the docker group dangerous?', 'Members can run containers that mount / as root.'),
], [
    ('RHCSA (EX200)', '“Create, delete, and modify local groups and group memberships”.'),
    ('LFCS', 'Manage groups and memberships.'),
    ('CompTIA Linux+', 'groupadd, groupmod, groupdel, gpasswd, usermod -aG.'),
]) + distro('The same tools everywhere; admin group names differ.', [
    ('Admin group', 'sudo', 'wheel', 'admin', '-'),
    ('groupadd / gpasswd', 'yes', 'yes', 'dseditgroup', '-'),
    ('First GID for teams', '1000', '1000', '501+', '-'),
    ('vigr', 'yes', 'yes', '-', '-'),
    ('Default user groups', 'adm sudo plugdev …', 'wheel (if admin)', 'staff admin', 'Windows groups'),
]) + teaser('8.4', 'Riya is in the sudo group, so she can become root. But should a junior DBA get full root just to restart PostgreSQL? Next: root, su and sudo, the sudoers file, and giving exactly one command to exactly one group.')

CHEATSHEET = cheatsheet('Managing groups', [
    ('Groups', [('groupadd g', 'create'), ('groupadd -g 2000 g', 'fixed GID'), ('groupadd -f g', 'if missing'), ('groupmod -n new old', 'rename'), ('groupdel g', 'delete')]),
    ('Members (user side)', [('usermod -aG g u', 'add'), ('usermod -aG a,b u', 'add several'), ('usermod -G g u', 'REPLACE list'), ('usermod -g g u', 'primary'), ('id -Gn u', 'check')]),
    ('Members (group side)', [('gpasswd -a u g', 'add'), ('gpasswd -d u g', 'remove'), ('gpasswd -M a,b g', 'set list'), ('gpasswd -A lead g', 'admin'), ('getent group g', 'members')]),
    ('Apply & edit', [('newgrp g', 'use now'), ('su - $USER', 'reload'), ('sudo -iu u id', 'their view'), ('vigr / vigr -s', 'safe edit'), ('/etc/group-', 'backup')]),
])

MINDMAP = mindmap('Groups', [
    ('Why', 'blue', ['team access', 'one place to change', 'least privilege']),
    ('Kinds', 'green', ['primary (passwd)', 'supplementary', 'system (-r)']),
    ('Create', 'amber', ['groupadd -g -f', 'groupmod -n -g', 'groupdel']),
    ('Members', 'violet', ['usermod -aG', 'gpasswd -a -d', '-M sets list']),
    ('Apply', 'acc', ['login loads', 'newgrp', 'id vs id USER']),
    ('Danger', 'red', ['-G without -a', 'docker = root', 'nano /etc/group']),
])

LAB = lab('set up a team', 'Build the lab, do the four tasks in your own terminal (sudo needed), then run the checker.',
    setup='''sudo groupdel labteam > /dev/null 2>&1; sudo groupdel labold > /dev/null 2>&1
sudo groupadd labold; sudo usermod -aG labold $USER''',
    tasks=['Create the group <code>labteam</code> with GID <code>2900</code>.',
           'Add yourself and the user <code>root</code> to labteam without removing any of your other groups.',
           'Remove yourself from <code>labold</code>.',
           'Make root an administrator of labteam.'],
    solution='''sudo groupadd -g 2900 labteam
sudo usermod -aG labteam $USER; sudo gpasswd -a root labteam
sudo gpasswd -d $USER labold
sudo gpasswd -A root labteam''',
    check='''ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
ok "1 group"    '[ "$(getent group labteam | cut -d: -f3)" = 2900 ]'
ok "2 members"  'getent group labteam | cut -d: -f4 | tr , "\\n" | grep -qx "$USER" && getent group labteam | grep -q root && id -Gn "$USER" | grep -qw sudo'
ok "3 removed"  '! getent group labold | cut -d: -f4 | tr , "\\n" | grep -qx "$USER"'
ok "4 admin"    '[ "$(sudo grep "^labteam:" /etc/gshadow | cut -d: -f3)" = root ]' ''')
