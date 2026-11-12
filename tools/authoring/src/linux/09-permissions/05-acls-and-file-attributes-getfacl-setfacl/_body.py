import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

ACLT = 'Typical output on Ubuntu with the acl package (our build machine has no getfacl/setfacl; format checked against the acl manual).'
ATT = 'sudo chattr -i -a ~/at/* > /dev/null 2>&1; sudo rm -rf ~/at; mkdir -p ~/at; echo "nameserver 10.0.0.2" > ~/at/resolv.conf; echo start > ~/at/audit.log'

HOOK = hook('Priya from internal audit needs to <b>read</b> the finance folder for two weeks. She is not in the finance group, and adding her would also give her everything else finance can reach. Opening the folder to “others” would let every user in. Three classes (owner, group, others) are simply not enough. <b>ACLs</b> (access control lists) add named entries like “user priya: read”. And when an attacker with root rewrites <code>/etc/resolv.conf</code>, or a script truncates an audit log, you want a lock that even root must remove first: <b>file attributes</b> such as immutable (<code>+i</code>) and append-only (<code>+a</code>).',
    ['explain why ACLs exist and read <code>getfacl</code> output: user, group, mask, other and named entries',
     'grant and remove access for one user or group with <code>setfacl -m</code>, <code>-x</code>, <code>-b</code>, recursively with <code>-R</code>',
     'set <b>default ACLs</b> on folders so new files inherit them, and understand the <b>mask</b>',
     'protect files with <code>chattr +i</code> (immutable) and <code>+a</code> (append-only), and check them with <code>lsattr</code>'])
ROAD = roadmap([
    ('story', 'The story', 3, 'an auditor and a locked file'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'ACLs and attributes', 6, 'simple meaning + 4 depths'),
    ('types', 'Access vs default ACL; i vs a', 4, 'differences'),
    ('commands', 'Each command, by field', 15, 'getfacl, setfacl, chattr'),
    ('animation', 'See it happen', 4, 'how an ACL is checked'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'attributes, ACL commands'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('One extra user needs access', 'setfacl -m u:priya:rx DIR', 'not a group change'),
    ('One extra group needs access', 'setfacl -m g:audit:r FILE', ''),
    ('New files in a folder should get it too', 'setfacl -d -m u:priya:rX DIR', 'default ACL'),
    ('See all entries', 'getfacl FILE', '+ in ls -l means ACL'),
    ('Remove one entry / all', 'setfacl -x u:priya FILE  /  setfacl -b FILE', ''),
    ('Nobody (even root) may change a file', 'sudo chattr +i FILE', 'until chattr -i'),
    ('A log may only grow', 'sudo chattr +a FILE', 'append-only'),
    ('See attributes', 'lsattr FILE', 'i, a, e …'),
    ('Simple team access', 'a group (8.3) + SGID (9.4)', 'ACLs are for exceptions'),
])

cmap = concept_map(
    [('9.1', 'Reading permissions', 'u g o'), ('9.3', 'chgrp and umask', 'group access, defaults'), ('9.4', 'SGID', 'team folders')],
    ['why three classes are not enough', 'getfacl: entries, mask, + in ls -l', 'setfacl -m -x -b -R, and default ACLs (-d)', 'the mask and effective rights', 'chattr +i +a and lsattr'],
    [('10.1', 'Inodes', 'where ACLs and attributes live'), ('14.5', 'tar', 'keeping ACLs in backups'), ('15.2', 'File systems', 'ACL support'), ('17.2', 'systemd', 'protecting configs')],
    'ACLs add named exceptions to the owner/group/others model; attributes add locks that even root must lift first.')

sc = (term(20, 14, 316, 156, ['$ setfacl -m u:priya:rx /srv/finance', '$ ls -ld /srv/finance', ('drwxrwx---+ 2 root finance … finance', 'acc'), '$ sudo chattr +i /etc/resolv.conf', '$ sudo rm /etc/resolv.conf', ('Operation not permitted', 'err')], title='riya@web01: ~', prompt='riya@web01:~$', size=7.0, step=15)
      + t(352, 36, 'Beyond u, g, o:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['• ACL: named users/groups', '• + in ls -l', '• default ACL: inherited', '• chattr +i: locked', '• chattr +a: append only'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>One auditor, one folder, no group change</h2>
  <div class="story">
''' + puzzle('Riya gives Priya <code>setfacl -m u:priya:rwx report.xlsx</code>, then runs <code>chmod 640 report.xlsx</code> to tidy up. Priya can suddenly only read it, and <code>getfacl</code> shows <code>user:priya:rwx  #effective:r--</code>. Also, root runs <code>rm</code> on a file and gets “Operation not permitted”. What is going on in each case?') + '''
    <p class="narration">An audit week at a small company.</p>
''' + scene('A terminal: setfacl gives priya read and enter access to the finance folder, ls -ld shows a plus sign, and an immutable resolv.conf cannot be deleted even with sudo.', sc,
            'Named exceptions with <tspan font-weight="700" class="s-acc">ACLs</tspan>; locks with <tspan font-weight="700" class="s-acc">attributes</tspan>.') + '''
K> Why not just add Priya to the finance group for two weeks?
A> Because finance owns other folders too, and you would have to remember to take her out. An ACL entry names her on <b>this</b> folder only, and removing it is one command.
R> And the file root cannot delete?
A> It is <b>immutable</b>: <code>chattr +i</code>. Nothing can change, rename or delete it until someone runs <code>chattr -i</code>. Today: ACLs for exceptions, attributes for locks.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A door notice with the usual three rows plus a guest list with named people; the mask is a ceiling that limits every guest and the group; a padlock on the door (immutable) stops everyone until it is removed.">'
       + label_box(14, 20, 190, 110, ['normal notice', 'owner / group / others', '3 rows only', '(chmod)'], 'blue', 8.6)
       + label_box(224, 20, 190, 110, ['guest list (ACL)', 'priya: r-x', 'audit group: r--', 'ceiling = mask'], 'green', 8.6)
       + label_box(434, 20, 192, 110, ['padlock (chattr +i)', 'nobody changes it,', 'not even root,', 'until unlocked'], 'red', 8.6)
       + t(320, 160, 'ACLs add named people to the notice;', 9.6, 'ink2')
       + t(320, 182, 'attributes put a padlock on the file.', 9.6, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('ACLs and attributes at four depths', [
    ('v', 'No jargon: a guest list and a padlock', '      <p>Two extras on top of chmod.</p>' + pic),
    ('b', 'The commands you will type', '''      <ul>
        <li><code>getfacl report.xlsx</code>: show every entry.</li>
        <li><code>setfacl -m u:priya:r report.xlsx</code>: Priya may read.</li>
        <li><code>setfacl -x u:priya report.xlsx</code>: remove her entry; <code>setfacl -b</code>: remove all ACLs.</li>
        <li><code>sudo chattr +i file</code> / <code>-i</code>: lock / unlock. <code>lsattr file</code>: see it.</li>
      </ul>'''),
    ('i', 'Entries, the mask and default ACLs', '''      <ul>
        <li>An ACL has the three classic entries (<code>user::</code>, <code>group::</code>, <code>other::</code>) plus named <code>user:NAME:</code> and <code>group:NAME:</code> entries and a <code>mask::</code>.</li>
        <li>The <b>mask</b> is the maximum for named users, named groups and the owning group. With an ACL present, the group digit of chmod <b>is</b> the mask, so <code>chmod 640</code> sets the mask to r-- (the puzzle). <code>#effective:</code> shows the result.</li>
        <li><b>Default ACLs</b> (<code>setfacl -d -m …</code>, only on folders) are copied to new files and folders created inside, so access keeps working for new reports. They replace the umask for those files.</li>
        <li>Order of checks: owner → named user → owning group and named groups → others, each limited by the mask (except owner and others).</li>
      </ul>'''),
    ('a', 'Behind the screen: xattrs, tools and attributes', '''      <ul>
        <li>ACLs are stored as extended attributes <code>system.posix_acl_access</code> and <code>system.posix_acl_default</code> on the inode. ext4, xfs and btrfs support them by default (ext4: mount option <code>acl</code> is on).</li>
        <li><code>cp</code> keeps ACLs only with <code>-a</code> or <code>--preserve=all</code>; <code>tar</code> needs <code>--acls</code>; <code>rsync</code> needs <code>-A</code>. Backups that drop them silently open or close access after a restore.</li>
        <li>NFSv4 and Windows (SMB) have their own, richer ACL models (nfs4_setfacl, icacls).</li>
        <li>Attributes (<code>chattr</code>) are file-system flags in the inode, checked before permissions: <b>i</b> immutable (no write, rename, delete, link, chmod), <b>a</b> append-only (only <code>&gt;&gt;</code>). Setting or clearing them needs <code>CAP_LINUX_IMMUTABLE</code> (root). <b>e</b> (extents) is normal on ext4.</li>
        <li>Attackers with root can run <code>chattr -i</code> too: attributes stop accidents and scripts, not a determined root. Malware sometimes sets +i on its own files: check <code>lsattr</code> when root “cannot delete” something.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>ACLs (getfacl, setfacl) and file attributes (chattr, lsattr)</h2>
''' + def_block(
    'A POSIX <b>access control list</b> (ACL) extends a file’s permissions with entries for specific named users and groups, limited by a <b>mask</b>. <code>getfacl</code> shows them; <code>setfacl</code> adds, changes or removes them, including <b>default</b> ACLs that new files in a directory inherit. <b>File attributes</b> are file-system flags such as immutable (<code>i</code>) and append-only (<code>a</code>), set with <code>chattr</code> and shown with <code>lsattr</code>; they apply even to root.',
    'Give one extra person or group exactly the access they need, and lock files against changes or deletion.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('ACL', 'Access control list: extra named entries.'),
    ('ACL entry', 'type:name:perms, e.g. user:priya:r-x.'),
    ('Mask', 'Upper limit for named entries and the owning group.'),
    ('Effective rights', 'Entry rights after the mask.'),
    ('Default ACL', 'Inherited by new files in a folder.'),
    ('Extended attribute', 'Extra data stored with an inode (xattr).'),
    ('Immutable (+i)', 'Cannot be changed, renamed or deleted.'),
    ('Append-only (+a)', 'Can only grow at the end.'),
]) + '\n' + names('Where the names come from.', [
    ('getfacl', 'get file ACL', 'acl package.'),
    ('setfacl', 'set file ACL', 'acl package.'),
    ('-m / -x / -b', 'modify / remove / remove all', ''),
    ('-d', 'default', 'For folders.'),
    ('chattr', 'change attributes', 'e2fsprogs.'),
    ('lsattr', 'list attributes', 'e2fsprogs.'),
    ('+i', 'immutable', ''),
    ('+a', 'append', ''),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Show ACL', '<code>getfacl f</code>'),
    ('Add user', '<code>setfacl -m u:priya:r f</code>'),
    ('Default', '<code>setfacl -d -m u:priya:rX d</code>'),
    ('Remove all', '<code>setfacl -b f</code>'),
    ('Lock', '<code>sudo chattr +i f</code>'),
    ('Check', '<code>lsattr f</code>'),
]) + '\n' + lv + didyou('On Ubuntu, <code>getfacl</code> and <code>setfacl</code> come in the small <code>acl</code> package (<code>sudo apt install acl</code>); desktops have it, minimal servers and containers often do not. chattr and lsattr are always there (e2fsprogs).') + '''
EXAM> “Give user tom read and write on /data/report without changing owner, group or others.” → <code>setfacl -m u:tom:rw /data/report</code>; check with <code>getfacl /data/report</code>.
''' + qc('<code>ls -l</code> shows <code>-rw-r-----+</code>. What does the + mean, and what do you run next?', 'The file has an ACL; run getfacl to see the named entries.') + mistake('setfacl -m u:priya:r /srv/finance   (expecting Priya to read next month’s reports too)',
    'setfacl -R -m u:priya:rX /srv/finance   and   setfacl -d -m u:priya:rX /srv/finance',
    'An access ACL on a folder covers only the folder itself. Existing files need -R, future files need a default ACL (-d). Your notes’ commands -m, -x u:NAME, -x g:NAME and -b are all correct; this is the step people forget.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Groups vs ACLs, access vs default ACLs, i vs a</h2>
''' + table(['', 'Group (8.3)', 'ACL entry'], [
    ['Good for', 'a team with many shared folders', 'one exception on one file/folder'],
    ['Change who has access', 'gpasswd -a/-d (applies everywhere)', 'setfacl -m/-x on each file'],
    ['Visible in ls -l', 'yes (group column)', 'only as a +'],
    ['Survives cp/tar', 'yes (as GID)', 'only with cp -a, tar --acls, rsync -A'],
    ['Takes effect', 'next login', 'immediately'],
], minw=520) + table(['', 'Access ACL', 'Default ACL'], [
    ['Applies to', 'the file/folder itself', 'new files and folders created inside'],
    ['Set with', '<code>setfacl -m</code>', '<code>setfacl -d -m</code> (folders only)'],
    ['Shown as', '<code>user:priya:r-x</code>', '<code>default:user:priya:r-x</code>'],
    ['Effect on existing files', 'yes', 'none (use -R -m for those)'],
], minw=480) + table(['Attribute', 'Write', 'Append (>>)', 'Delete / rename', 'chmod/chown', 'Typical use'], [
    ['<code>+i</code> immutable', 'no', 'no', 'no', 'no', 'critical configs'],
    ['<code>+a</code> append-only', 'no', 'yes', 'no', 'no', 'logs, audit trails'],
    ['none', 'per permissions', 'per permissions', 'per folder w', 'owner/root', 'normal'],
], minw=560) + qc('Priya should also read every <b>future</b> report in /srv/finance. Which ACL do you need?', 'A default ACL on the folder: <code>setfacl -d -m u:priya:rX /srv/finance</code> (plus an access ACL for existing files).') + '''
</section>
'''

FIN_GET = '''# file: srv/finance/q3.xlsx
# owner: root
# group: finance
user::rw-
user:priya:r--
group::rw-
mask::rw-
other::---'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Each command explained, then used in every field</h2>
  <p id="commands">getfacl and setfacl outputs are <b>typical</b>: our build machine does not have the acl package, so we checked every format against the acl manual. Every chattr and lsattr output below was <b>recorded</b> on our Ubuntu 24.04 build machine.</p>
''' + cmdcard_u(['seeing every rule on a file with a +', 'checking effective rights after a chmod', 'backing up and restoring ACLs'],
               ['files without a + (getfacl only shows the 3 normal entries)'])(
    'getfacl', 'getfacl', 'show the ACL',
    'Prints the owner, group and every ACL entry, the mask, and (for folders) default entries. <code>#effective:</code> appears when the mask limits an entry.',
    'getfacl [-R] [-p] [--omit-header] FILE…   ·   getfacl -R DIR > acl.bak   ·   setfacl --restore=acl.bak', 'safe',
    [('getfacl f', 'all entries', 'inspect'),
     ('getfacl -R dir', 'whole tree', 'audit'),
     ('--omit-header', 'no # lines', 'scripts'),
     ('getfacl -R d > bak', 'save ACLs', 'backup'),
     ('setfacl --restore=bak', 'put them back', 'restore'),
     ('ls -l', '+ = has an ACL', 'spot it')],
    dict(cmd='getfacl /srv/finance/q3.xlsx', rec=(ACLT, FIN_GET), note='The three normal entries, plus a named entry for priya and the mask. Others have nothing.'),
    [('sec', [
        dict(situation='Audit a share: who has extra access?', cmd="getfacl -R --omit-header /srv/finance 2>/dev/null | grep -E '^(user|group):[a-z]'", rec=(ACLT, 'user:priya:r-x\ngroup:audit:r-x\nuser:priya:r--'),
             why='Lines with a name between the colons are the exceptions. Each should have a ticket and an end date.')]),
    ]
) + cmdcard_u(['one more user or group needs access', 'temporary access for auditors, contractors', 'a service account that must read one folder'],
               ['whole teams (use a group)', 'very many entries (hard to audit)'])(
    'setfacl', 'setfacl', 'add, change, remove entries',
    '<code>-m</code> adds or changes entries, <code>-x</code> removes one, <code>-b</code> removes all extended entries, <code>-R</code> recurses, <code>-d</code> works on default ACLs, <code>-k</code> removes the default ACL. Use <code>X</code> to give x to folders only.',
    'setfacl [-R] [-d] -m u:NAME:PERMS|g:NAME:PERMS|m::PERMS FILE…   ·   setfacl -x u:NAME FILE   ·   setfacl -b FILE', 'change',
    [('-m u:priya:r f', 'user priya: read', 'one person'),
     ('-m g:audit:rx d', 'group audit: read + enter', 'one group'),
     ('-R -m u:priya:rX d', 'existing tree (X: folders)', 'whole folder'),
     ('-d -m u:priya:rX d', 'default for new files', 'future files'),
     ('-x u:priya f', 'remove one entry', 'access ends'),
     ('-b f', 'remove all ACL entries', 'clean up'),
     ('-m m::r f', 'set the mask', 'cap rights')],
    dict(cmd='setfacl -m u:priya:r /srv/finance/q3.xlsx\nls -l /srv/finance/q3.xlsx\ngetfacl --omit-header /srv/finance/q3.xlsx', rec=(ACLT, '-rw-rw----+ 1 root finance 18432 Nov 11 10:02 /srv/finance/q3.xlsx\nuser::rw-\nuser:priya:r--\ngroup::rw-\nmask::rw-\nother::---'), note='The + appears; priya can read, others still cannot.'),
    [('sys', [
        dict(situation='Two weeks of read access to a folder and everything in it, including new files.', cmd='sudo setfacl -R -m u:priya:rX /srv/finance\nsudo setfacl -d -m u:priya:rX /srv/finance\ngetfacl --omit-header /srv/finance', rec=(ACLT, 'user::rwx\nuser:priya:r-x\ngroup::rwx\nmask::rwx\nother::---\ndefault:user::rwx\ndefault:user:priya:r-x\ndefault:group::rwx\ndefault:mask::rwx\ndefault:other::---'),
             why='-R for what exists, -d for what will be created. Remove later with -R -x u:priya and -k.'),
        dict(situation='End the access.', cmd='sudo setfacl -R -x u:priya /srv/finance\nsudo setfacl -k /srv/finance\nls -ld /srv/finance', rec=(ACLT, 'drwxrwx--- 2 root finance 4096 Nov 11 10:02 /srv/finance'),
             why='When no named entries are left, the + disappears.')]),
     ('web', [
        dict(situation='Let the web server read one user’s project without opening it to everyone.', cmd='setfacl -m u:www-data:x /home/riya\nsetfacl -R -m u:www-data:rX /home/riya/site', rec=(ACLT, ''),
             why='x on the home folder lets www-data pass through (not list), rX on the site lets it read. No 755 on the home needed.')]),
     ('devops', [
        dict(situation='Back up ACLs before a migration (cp and tar drop them unless told).', cmd='getfacl -R /srv/finance > /tmp/finance.acl\nsudo setfacl --restore=/tmp/finance.acl', rec=(ACLT, ''),
             why='Also: <code>cp -a</code>, <code>tar --acls</code>, <code>rsync -aA</code> keep ACLs.')]),
    ]
) + mistake('setfacl -m u:priya:rw report.xlsx, then chmod 640 report.xlsx', 'chmod 660 (or setfacl -m m::rw report.xlsx) and check getfacl',
            'With an ACL, the group digit of chmod sets the <b>mask</b>. chmod 640 made the mask r--, so priya’s rw became <code>#effective:r--</code>: the puzzle.') + cmdcard_u(['configs that must never change by accident', 'logs that may only grow', 'diagnosing “root cannot delete this”'],
               ['as a security boundary against root (root can remove it)', 'files that packages update (upgrades fail)'])(
    'chattr', 'chattr · lsattr', 'immutable and append-only',
    '<code>chattr +i</code> makes a file immutable: no change, rename, delete or link, even for root. <code>+a</code> allows only appending. <code>-i</code>/<code>-a</code> remove them. <code>lsattr</code> lists attributes (<code>e</code> = extents, normal on ext4). Changing them needs root.',
    'sudo chattr +i|-i|+a|-a FILE…   ·   lsattr [-d] [-R] FILE…', 'change',
    [('sudo chattr +i f', 'immutable', 'protect configs'),
     ('sudo chattr -i f', 'unlock', 'before editing'),
     ('sudo chattr +a f', 'append-only', 'logs'),
     ('lsattr f', 'show flags', 'diagnose'),
     ('lsattr -d dir', 'the folder itself', 'folders'),
     ('chattr +i dir', 'no files added/removed', 'freeze a folder')],
    dict(setup=ATT, cmd="cd ~/at; sudo chattr +i resolv.conf\nlsattr resolv.conf\necho 'nameserver 6.6.6.6' > resolv.conf; sudo rm -f resolv.conf; sudo chmod 777 resolv.conf\nsudo chattr -i resolv.conf; lsattr resolv.conf", expect='any', note='Even with sudo, write, delete and chmod are refused until the i flag is removed.'),
    [('sec', [
        dict(situation='An audit log that can only grow (no truncating, no editing).', setup=ATT, cmd="cd ~/at; sudo chattr +a audit.log\necho 'login riya' >> audit.log && echo appended\necho 'wiped' > audit.log; sudo truncate -s 0 audit.log\ncat audit.log; sudo chattr -a audit.log", expect='any',
             why='>> works, > and truncate fail, even as root. Attackers often try to clear logs.')]),
     ('sys', [
        dict(situation='“root cannot delete this file”: check attributes first.', setup=ATT + '; sudo chattr +i ~/at/resolv.conf', cmd="cd ~/at; sudo rm resolv.conf; echo \"exit $?\"\nlsattr resolv.conf\nsudo chattr -i resolv.conf && sudo rm resolv.conf && echo removed", expect='any',
             why='Permissions look fine, but the i flag wins. Some malware and some admins set it; lsattr reveals it.')]),
     ('devops', [
        dict(situation='Package upgrades fail on immutable files.', cmd="echo 'dpkg: error processing … unable to make backup link of ./etc/resolv.conf: Operation not permitted'", rec=('Typical error during apt upgrade when a managed file is immutable', 'dpkg: error processing archive …: unable to make backup link of \'./etc/…\' before installing new version: Operation not permitted'),
             why='Document every +i, and remove it before upgrades or config management runs.')]),
    ],
    sudo=True
) + undo('Both are reversible.', [
    ('Wrong ACL entry:', '<code>setfacl -x u:NAME FILE</code>; everything: <code>setfacl -b FILE</code>.'),
    ('Wrong default ACL:', '<code>setfacl -k DIR</code> (existing files keep theirs: <code>-R -b</code>).'),
    ('Lost ACLs after a copy:', 'restore from <code>getfacl -R</code> output with <code>setfacl --restore</code>.'),
    ('Locked file:', '<code>sudo chattr -i FILE</code> (or -a).'),
]) + errors('Errors students see most. chattr errors were really produced on our build machine, with their exit status.', [
    dict(cmd="touch f; chattr +i f", meaning='Setting attributes needs root (CAP_LINUX_IMMUTABLE).', fix='<code>sudo chattr +i f</code>.'),
    dict(cmd="touch f; sudo chattr +i f; sudo rm f; rc=$?; sudo chattr -i f; (exit $rc)", meaning='The file is immutable, so even root is refused.', fix='<code>sudo chattr -i f</code> first.'),
    dict(cmd="getfacl /etc/hosts", meaning='The acl tools are not installed on this machine.', fix='<code>sudo apt install acl</code>.'),
]) + qc('A log must keep growing but never be edited or wiped. Which command?', '<code>sudo chattr +a FILE</code>') + '''
'''

SCREENS = screens_block('Real terminal screens: an immutable file', 'Even sudo cannot delete a file with the i attribute until it is removed.',
    ATT + "; sudo chattr +i ~/at/resolv.conf; printf '%s\\n' 'PS1=\"riya@web01:~/at$ \"' > ~/.mprc", 'bash --rcfile ~/.mprc', [
    ('Enter', "'cd ~/at; ls -l resolv.conf; sudo rm resolv.conf' Enter", ' after sudo rm: refused; the normal permissions look harmless.'),
    ('Enter', "'lsattr resolv.conf' Enter", ' after lsattr: the i flag explains it.'),
], 74, 9, hid='screens', what='bash')

cards = cards + SCREENS + '</section>\n'

def acl(k, note, tone):
    rows = [('owner root', 'rw-'), ('user:priya', 'rw-'), ('mask', 'rw-' if k < 2 else 'r--'), ('other', '---')]
    o = label_box(14, 8, 110, 36, ['priya wants', 'to WRITE'], 'blue', 7.8)
    for i, (n, b) in enumerate(rows):
        tn = 'card'
        if k >= 1 and i == 1:
            tn = 'amber'
        if k >= 2 and i == 2:
            tn = 'red'
        o += label_box(140, 4 + i * 30, 120, 26, [f'{n}: {b}'], tn, 7.6)
    if k == 3:
        o += label_box(270, 40, 80, 40, ['effective', 'r-- → denied'], 'red', 7.6)
    elif k == 1:
        o += label_box(270, 40, 80, 40, ['effective', 'rw- → allowed'], 'green', 7.6)
    return o + t(180, 140, note, 8.6, tone, bold=True)
see = [term(14, 16, 332, 116, [f'$ {c}'] + ([(r, 'err' if 'denied' in r else 'out')] if r else []), title='priya@web01', prompt='priya@web01:~$', size=8) + cap(n, '', 'card', y=150, h=34)
       for c, r, n in [('echo x >> q3.xlsx', '', 'priya has an ACL entry rw-.'), ('echo x >> q3.xlsx', '(works)', 'Write works.'), ('# admin: chmod 640 q3.xlsx', '', 'Someone runs chmod 640…'), ('echo x >> q3.xlsx', 'Permission denied', '…and priya is denied.')]]
behind = [acl(0, 'Not the owner: look for a named entry.', 'violet'), acl(1, 'user:priya:rw- AND mask rw- → rw-.', 'green'),
          acl(2, 'chmod 640: the group digit 4 became the mask r--.', 'red'), acl(3, 'rw- AND r-- → r--: write denied.', 'red')]
two = anim_two('How an ACL is checked', 'Behind the screen: entry AND mask',
               'A terminal where priya appends to a file, then is denied after an admin runs chmod 640.',
               'Rows owner, named user priya, mask and other; priya’s rights are her entry combined with the mask; chmod changes the mask.', see, behind,
               ['Entry.', 'Allowed.', 'chmod.', 'Denied.'],
               ['1. named entry', '2. rw- & rw-', '3. mask r--', '4. rw- & r-- = r--'])

def inh(k, note, tone):
    o = label_box(14, 14, 140, 60, ['/srv/finance', 'default:user:priya:r-x' if k >= 1 else '(no default ACL)'], 'amber' if k >= 1 else 'card', 7.6)
    if k >= 2:
        o += arrow(156, 44, 178, 44)
        o += label_box(180, 14, 166, 60, ['new: q4.xlsx', 'user:priya:r--' if k >= 2 else ''], 'green', 7.6)
    return o + t(180, 110, note, 8.6, tone, bold=True)
frames = [inh(0, 'A folder with an access ACL only.', 'violet'), inh(1, 'setfacl -d -m u:priya:rX adds a default entry.', 'amber'),
          inh(2, 'A new file inside copies it (x dropped for files).', 'green'), inh(3, 'Future reports are readable too: no extra work.', 'green')]
s1 = anim_one('Animated example', 'Default ACLs: access for future files',
              'A default ACL is a template that new files copy.',
              'inheritance', 'A folder gets a default ACL entry for priya; a new file created inside receives priya’s entry automatically.', frames,
              ['Before.', 'Template.', 'Inherited.', 'Done.'], hid='scenario-default')

dx = dissect('Layer by layer: where the extras live',
    'Recorded on our build machine (chattr, xattrs).', [
    dict(key='mode', name='Mode bits', sub='u g o', why='The base model.', how='chmod.', impl='inode.', used='Every file.',
         cmd="touch m; stat -c '%A %a' m"),
    dict(key='xattr', name='Extended attributes', sub='system.posix_acl_*', why='Where ACLs are stored.', how='setfacl writes them.', impl='Inode xattr space.', used='ACLs, SELinux labels.',
         cmd="python3 -c \"import os; open('x','w').close(); os.setxattr('x','user.note',b'audit'); print(os.listxattr('x'), os.getxattr('x','user.note'))\""),
    dict(key='flags', name='Inode flags', sub='chattr', why='i, a and others.', how='Checked before permissions.', impl='FS_IOC_SETFLAGS.', used='Locks.',
         cmd="touch fl; sudo chattr +a fl; lsattr fl; sudo chattr -a fl"),
    dict(key='fs', name='File system', sub='ext4 / xfs', why='Must support xattrs and ACLs.', how='Mount options.', impl='ext4: on by default.', used='Shares.',
         cmd="df -T ~ | tail -1 | awk '{print $1, $2}'"),
], hint='From mode bits to the file system. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>How an ACL is checked, and default ACLs</h2>
''' + two + s1 + dx + qc('Why can root not delete an immutable file, though root bypasses permissions?', 'Attributes are checked separately from permissions; root must first remove the flag with chattr -i.') + '''
</section>
'''

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>ACLs and attributes at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['u:priya:rX', 'auditor'], 'blue', 8.6), '1. Temporary access',
              'Auditors and contractors get named, time-limited ACL entries on exactly the folders they need.', ['Request', '*setfacl', 'remove later']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['u:www-data', 'x on home'], 'green', 8.6), '2. Service access',
    'A web server or backup agent gets read access to one path without opening it to everyone.', ['Service', '*setfacl', 'least privilege']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['default ACL', 'shares'], 'amber', 8.6), '3. Shared drives',
    'Samba and project shares use default ACLs so new files keep the right access.', ['Share', '*setfacl -d', 'consistent']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['+a', 'audit.log'], 'red', 8.6), '4. Tamper-resistant logs',
    'Audit logs are append-only so a script or user cannot wipe them.', ['Log', '*chattr +a', 'evidence']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['lsattr', 'incident'], 'violet', 8.6), '5. Incident response',
    'Responders check lsattr when malware files “cannot be deleted”.', ['Stuck file', '*lsattr', 'chattr -i']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. chattr/lsattr really run on our build machine.', [
    dict(level='b', title='Attributes of a file', scenario='Anything special?', cmd='lsattr /etc/passwd', explain='Only e (extents).'),
    dict(level='b', title='Lock and unlock', scenario='Protect a file briefly.', setup=ATT, cmd="sudo chattr +i ~/at/resolv.conf; lsattr ~/at/resolv.conf; sudo chattr -i ~/at/resolv.conf", explain='+i / -i.'),
    dict(level='i', title='Find immutable files', scenario='Under a folder.', setup=ATT + '; sudo chattr +i ~/at/resolv.conf', cmd="lsattr -R ~/at 2>/dev/null | awk '$1 ~ /i/'; sudo chattr -i ~/at/resolv.conf", explain='awk on the flags column.'),
    dict(level='i', title='Files with ACLs', scenario='Spot the + in ls -l.', cmd="ls -l /etc | awk '$1 ~ /\\+$/' | head -3; echo checked", explain='No ACLs in /etc here.'),
    dict(level='a', title='Append-only check', scenario='Prove a log can only grow.', setup=ATT, cmd="cd ~/at; sudo chattr +a audit.log; echo ok >> audit.log; (echo bad > audit.log) 2>&1; wc -l < audit.log; sudo chattr -a audit.log", explain='> fails, >> works.', expect='any'),
], extra=build_up('locking down a DNS config', 'Riya stops a script from overwriting resolv.conf.', ATT, [
    ('cd ~/at; cat resolv.conf', '1. The good file.'),
    ('cd ~/at; sudo chattr +i resolv.conf; lsattr resolv.conf', '2. Make it immutable.'),
    ("cd ~/at; echo 'nameserver 6.6.6.6' | sudo tee resolv.conf; cat resolv.conf", '3. A script (even with sudo) cannot overwrite it.'),
    ('cd ~/at; sudo chattr -i resolv.conf; lsattr resolv.conf', '4. Unlock for planned changes.'),
], cumulative=True, expect='any')) + which('Choosing the right tool.', [
    ('Whole team access', 'group + SGID', 'Scales.', 'Many ACL entries.'),
    ('One person, one folder', 'setfacl -m u:', 'Precise.', 'Adding to a group.'),
    ('Future files too', 'setfacl -d', 'Inherited.', 'Fixing every week.'),
    ('Exact limit', 'mask (m::)', 'Caps entries.', 'Guessing.'),
    ('Must not change', 'chattr +i', 'Even root.', 'chmod 444 (root ignores).'),
    ('Log may only grow', 'chattr +a', 'No wipes.', 'Hoping.'),
]) + keys('Handy forms.', [
    ('setfacl -m u:N:rX', 'user, X for folders', 'access'),
    ('setfacl -d -m …', 'default', 'future files'),
    ('setfacl -x u:N', 'remove one', 'end access'),
    ('setfacl -b', 'remove all', 'reset'),
    ('chattr +i / -i', 'lock / unlock', 'configs'),
    ('lsattr -d', 'folder flags', 'check'),
]) + scriptit('attr-check.sh', 'Report files under a folder that are immutable or append-only, so nobody is surprised during maintenance.',
'''d=${1:-$HOME/at}
sudo chattr +i "$d/resolv.conf"; sudo chattr +a "$d/audit.log"   # demo flags
lsattr -R "$d" 2>/dev/null | while read -r flags f; do
  case $flags in *i*) echo "IMMUTABLE    $f";; *a*) echo "APPEND-ONLY  $f";; esac
done
sudo chattr -i "$d/resolv.conf"; sudo chattr -a "$d/audit.log"''',
'<p>Run on the sample folder.</p>') + puzzle_answer('With an ACL, the group digit of chmod changes the <b>mask</b>. <code>chmod 640</code> set the mask to r--, so priya’s rwx is cut to <code>#effective:r--</code>; fix with <code>chmod 660</code> (or <code>setfacl -m m::rw</code>). And root’s “Operation not permitted” comes from the <b>immutable</b> attribute: <code>lsattr</code> shows i; <code>sudo chattr -i</code> first.') + qc('Which removes every ACL entry from a file?', '<code>setfacl -b FILE</code>') + '''
</section>
'''

_sh.run_sh(ATT, 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../04-special-permissions-suid-sgid-and-the-sticky-bit/">Lesson 9.4</a> (SGID) and <a href="../../08-users-and-groups/03-managing-groups-groupadd-gpasswd-and-usermod-ag/">8.3</a> (groups).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
_sh.run_sh('sudo chattr -i -a ~/at/* > /dev/null 2>&1; rm -rf ~/at', 'any')
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
