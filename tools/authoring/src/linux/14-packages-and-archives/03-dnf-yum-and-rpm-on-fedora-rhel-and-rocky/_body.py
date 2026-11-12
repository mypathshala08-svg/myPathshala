import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# Saved, typical outputs from a Rocky Linux 9 server (the build machine is Ubuntu; these files are analysed for real).
RH = r"""rm -rf ~/rh; mkdir -p ~/rh/yum.repos.d; cd ~/rh
cat > os-release <<'EOF'
NAME="Rocky Linux"
VERSION="9.4 (Blue Onyx)"
ID="rocky"
ID_LIKE="rhel centos fedora"
VERSION_ID="9.4"
PLATFORM_ID="platform:el9"
EOF
cat > yum.repos.d/rocky.repo <<'EOF'
[baseos]
name=Rocky Linux $releasever - BaseOS
mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=BaseOS-$releasever
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

[appstream]
name=Rocky Linux $releasever - AppStream
mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=AppStream-$releasever
gpgcheck=1
enabled=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9

[crb]
name=Rocky Linux $releasever - CRB
mirrorlist=https://mirrors.rockylinux.org/mirrorlist?arch=$basearch&repo=CRB-$releasever
gpgcheck=1
enabled=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-Rocky-9
EOF
cat > rpm-qa.txt <<'EOF'
bash-5.1.8-9.el9.x86_64
openssl-3.0.7-27.el9.x86_64
openssl-libs-3.0.7-27.el9.x86_64
kernel-5.14.0-427.13.1.el9_4.x86_64
kernel-5.14.0-362.24.1.el9_3.x86_64
nginx-1.20.1-14.el9_2.1.x86_64
tmux-3.2a-5.el9.x86_64
python3-3.9.18-3.el9.x86_64
gpg-pubkey-350d275d-6279464b
EOF
cat > check-update.txt <<'EOF'

openssl.x86_64                 1:3.0.7-28.el9_4             baseos
openssl-libs.x86_64            1:3.0.7-28.el9_4             baseos
curl.x86_64                    7.76.1-29.el9_4.1            baseos
nginx.x86_64                   1:1.20.1-16.el9_4.1          appstream
EOF
cat > dnf-history.txt <<'EOF'
ID     | Command line              | Date and time    | Action(s)      | Altered
-------------------------------------------------------------------------------
    14 | install tmux              | 2026-11-10 09:12 | Install        |    1
    13 | upgrade                   | 2026-11-03 02:00 | Upgrade        |   42
    12 | remove httpd              | 2026-10-28 16:40 | Removed        |    5
    11 | install nginx             | 2026-10-28 16:35 | Install        |    3
EOF"""

HOOK = hook('Riya’s new job runs Rocky Linux 9 in production and Fedora on the developers’ laptops. Her fingers type <code>apt install</code> and get “command not found”. The ideas from Lessons 14.1 and 14.2 are exactly the same (packages, repositories, dependencies, a low-level and a high-level tool), only the names change: <b>.rpm</b> packages, <b>rpm</b> for single files and queries, <b>dnf</b> (formerly <b>yum</b>) for repositories, <code>/etc/yum.repos.d/</code> for the repository list and <code>dnf history</code> for the log, with a real undo button. This lesson maps every apt habit to its Red Hat twin.',
    ['use dnf for install, upgrade, remove, search, info, check-update and groups, and know yum is the same tool on older systems',
     'query packages with rpm -q, -qa, -qi, -ql, -qf, -qR and verify them with rpm -V',
     'read and change repositories in /etc/yum.repos.d/ (enabled, gpgcheck, EPEL, CRB) and use dnf history to undo',
     'translate any apt command to dnf and back, and handle RPM version strings (epoch:version-release)'])
ROAD = roadmap([
    ('story', 'The story', 3, 'apt: command not found'),
    ('decide', 'apt → dnf chart', 2, 'the quick chart'),
    ('definition', 'rpm and dnf', 5, 'simple meaning + 4 depths'),
    ('types', 'apt vs dnf vs rpm', 5, 'the translation table'),
    ('commands', 'By field', 15, 'real analysis of RHEL outputs'),
    ('animation', 'See it happen', 4, 'dnf history undo'),
    ('run', 'Run on your PC', 4, 'on a Rocky/Fedora VM'),
    ('lab', 'Practice lab', 7, 'translate and analyse'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('apt habit → Red Hat command', [
    ('apt update', '(automatic) · sudo dnf makecache', 'refresh'),
    ('apt list --upgradable', 'dnf check-update', 'preview'),
    ('apt upgrade', 'sudo dnf upgrade', 'patch'),
    ('apt install X / ./f.deb', 'sudo dnf install X / ./f.rpm', 'install'),
    ('apt remove / purge X', 'sudo dnf remove X', 'uninstall'),
    ('apt search / show X', 'dnf search X / dnf info X', 'find'),
    ('dpkg -S FILE / -L X', 'rpm -qf FILE / rpm -ql X', 'query'),
    ('history.log', 'dnf history · sudo dnf history undo N', 'log + undo'),
])

cmap = concept_map(
    [('14.1', 'Packages', 'the ideas'), ('14.2', 'apt and dpkg', 'the Debian side'), ('1.3', 'Distributions', 'RHEL family')],
    ['rpm: single files and queries', 'dnf (yum): repositories, dependencies', 'repo files in /etc/yum.repos.d', 'dnf history and undo', 'groups and modules', 'EPEL and CRB', 'epoch:version-release'],
    [('14.4', 'snap, flatpak, source', 'other ways'), ('19.2', 'SELinux', 'RHEL’s security layer'), ('19.3', 'Hardening', 'dnf-automatic'), ('17.2', 'systemd', 'same on both')],
    'Same ideas, different names: rpm is dpkg, dnf is apt, yum.repos.d is sources.list.d, and dnf history can undo.')

sc = (term(20, 14, 316, 156, ['$ sudo dnf install tmux', ('Installed: tmux-3.2a-5.el9.x86_64', 'out'), '$ rpm -qf /usr/bin/tmux', ('tmux-3.2a-5.el9.x86_64', 'out'), '$ dnf history | head -3', ('14 | install tmux | … | Install', 'acc')], title='riya@rocky9: ~', prompt='[riya@rocky9 ~]$', size=6.6, step=17)
      + t(352, 36, 'Red Hat twins:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['apt → dnf', 'dpkg → rpm', 'sources → .repo', 'history → dnf history', '+ history undo'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>apt: command not found</h2>
  <div class="story">
''' + puzzle('On Rocky 9 Riya runs <code>sudo dnf install htop</code> and gets “No match for argument: htop”, although her colleague installed it yesterday. <code>rpm -q nginx</code> prints <code>nginx-1.20.1-14.el9_2.1.x86_64</code>, but <code>dnf check-update</code> lists <code>nginx 1:1.20.1-16.el9_4.1</code>: what is the <code>1:</code>? And after a bad <code>sudo dnf upgrade</code> her senior says “just undo transaction 13”. Undo an upgrade?') + '''
    <p class="narration">On the Rocky server (outputs shown are typical; our build machine is Ubuntu).</p>
''' + scene('A Rocky Linux terminal: dnf installs tmux, rpm -qf shows which package owns /usr/bin/tmux, and dnf history lists the install as transaction 14.', sc,
            'Same ideas as apt; <tspan font-weight="700" class="s-acc">dnf history</tspan> even has undo.') + '''
K> So I just replace apt with dnf?
A> For most commands, yes: <code>dnf install</code>, <code>dnf remove</code>, <code>dnf upgrade</code>, <code>dnf search</code>, <code>dnf info</code>. Two differences you notice first: dnf refreshes its metadata automatically (no separate update step), and every change is a numbered <b>transaction</b> you can inspect and undo.
R> And htop?
A> htop is not in Rocky’s own repositories; it is in <b>EPEL</b> (Extra Packages for Enterprise Linux), which her colleague had enabled. Today: dnf, rpm, repositories, history, and a translation table you will use for years.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Two parallel columns: Debian family (apt over dpkg, sources.list.d, .deb) and Red Hat family (dnf over rpm, yum.repos.d, .rpm), with arrows showing each pair is the same role.">'
       + label_box(20, 20, 260, 34, ['Debian / Ubuntu'], 'blue', 9.4) + label_box(360, 20, 260, 34, ['RHEL / Rocky / Fedora'], 'red', 9.4)
       + ''.join(label_box(20, 64 + i * 32, 260, 26, [a], 'card', 8.4) + label_box(360, 64 + i * 32, 260, 26, [b], 'card', 8.4) + t(320, 82 + i * 32, '=', 11, 'acc', bold=True)
                 for i, (a, b) in enumerate([('apt (repositories, dependencies)', 'dnf / yum'), ('dpkg (one file, database)', 'rpm'), ('/etc/apt/sources.list.d/', '/etc/yum.repos.d/*.repo'), ('.deb', '.rpm')]))
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('dnf and rpm at four depths', [
    ('v', 'No jargon: two families, same jobs', '      <p>Every tool has a twin.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>sudo dnf install nginx</code>, <code>sudo dnf remove nginx</code>.</li>
        <li><code>sudo dnf upgrade</code> (yum update on CentOS 7).</li>
        <li><code>dnf search editor</code>, <code>dnf info nginx</code>.</li>
        <li><code>rpm -qa | grep nginx</code>: is it installed?</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li>No separate “update” step: dnf refreshes metadata when it is older than the cache expiry (<code>dnf makecache</code> forces it).</li>
        <li><code>dnf remove</code> also removes now-unneeded dependencies (clean_requirements_on_remove); there is no purge: changed config files are saved as <code>.rpmsave</code>.</li>
        <li>Every change is a numbered <b>transaction</b>: <code>dnf history</code>, <code>dnf history info N</code>, <code>sudo dnf history undo N</code>.</li>
        <li>Groups install sets of packages: <code>dnf group install "Development Tools"</code>.</li>
        <li>Extra repositories: <b>EPEL</b> (community extras), <b>CRB</b> (CodeReady Builder, build dependencies), enabled with <code>dnf config-manager --set-enabled crb</code>.</li>
      </ul>'''),
    ('a', 'Behind the screen: RPM database, versions and modules', '''      <ul>
        <li>The RPM database lives in <code>/var/lib/rpm</code> (SQLite since RHEL 9). <code>rpm -V</code> checks size, mode, checksum, owner of every file: <code>S.5....T. c /etc/nginx/nginx.conf</code> means size, MD5 and time changed, and it is a config file.</li>
        <li>Version strings are <code>[epoch:]version-release.dist.arch</code>; the epoch (<code>1:</code>) forces ordering when upstream numbering went backwards.</li>
        <li>dnf is written in Python on libsolv (the same solver family as openSUSE’s zypper); dnf5 (C++) replaces it in newer Fedora.</li>
        <li>yum on RHEL 8/9 is a symlink to dnf; real yum (Python 2) only on CentOS 7 and older.</li>
        <li>AppStream “modules” (RHEL 8) offered several versions of one package (e.g. nodejs:18, nodejs:20) via <code>dnf module enable</code>; RHEL 9 uses mostly normal packages again.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>rpm, dnf and yum</h2>
''' + def_block(
    '<b>rpm</b> is the low-level package tool of the Red Hat family: it installs, removes, queries and verifies individual <code>.rpm</code> files and keeps the RPM database. <b>dnf</b> (Dandified YUM) is the high-level package manager on Fedora, RHEL 8+ and its rebuilds (Rocky, AlmaLinux): it reads repositories from <code>/etc/yum.repos.d/</code>, resolves dependencies, and records every change as an undoable transaction. <b>yum</b> is its predecessor; on current systems the yum command runs dnf.',
    'rpm is dpkg, dnf is apt, yum is the old name of dnf.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('RPM', 'Package format and low-level tool.'),
    ('dnf / yum', 'High-level package manager.'),
    ('Repo file', '/etc/yum.repos.d/NAME.repo.'),
    ('Transaction', 'One numbered dnf change.'),
    ('EPEL', 'Extra Packages for Enterprise Linux.'),
    ('CRB', 'CodeReady Builder repository.'),
    ('Epoch', 'The N: before a version.'),
    ('el9', 'Built for Enterprise Linux 9.'),
]) + '\n' + names('Where the names come from.', [
    ('rpm', 'Red Hat Package Manager', '1997.'),
    ('yum', 'Yellowdog Updater, Modified', 'From Yellow Dog Linux, 2003.'),
    ('dnf', 'Dandified YUM', 'Fedora 22, 2015.'),
    ('RHEL', 'Red Hat Enterprise Linux', 'Paid, supported.'),
    ('Rocky / Alma', 'free RHEL rebuilds', 'After CentOS 8 ended.'),
    ('Fedora', 'upstream, fast-moving', 'Sponsored by Red Hat.'),
    ('BaseOS / AppStream', 'core OS / applications', 'RHEL 8+ repos.'),
    ('.rpmnew / .rpmsave', 'new default / your saved config', 'Upgrades, removals.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Install', '<code>sudo dnf install X</code>'),
    ('Owner of a file', '<code>rpm -qf FILE</code>'),
    ('Files of a package', '<code>rpm -ql X</code>'),
    ('Updates waiting', '<code>dnf check-update</code>'),
    ('Undo', '<code>sudo dnf history undo N</code>'),
    ('Repos', '<code>/etc/yum.repos.d/</code>'),
]) + '\n' + lv + didyou('<code>dnf check-update</code> returns exit code <b>100</b> when updates are available, 0 when there are none and 1 on error: made for scripts and monitoring checks.') + '''
EXAM> “What is the difference between rpm and dnf?” → rpm installs and queries single package files without resolving dependencies; dnf uses repositories, resolves dependencies, and keeps an undoable transaction history.
''' + qc('Where would you look to see which repositories a Rocky server uses?', '/etc/yum.repos.d/*.repo, or dnf repolist.') + mistake('sudo rpm -ivh package.rpm for a package with dependencies',
    'sudo dnf install ./package.rpm   (dnf fetches the dependencies)',
    'rpm fails with “Failed dependencies: … is needed by …”, the same problem as dpkg -i.') + mistake('turning gpgcheck=0 to make an install “work”',
    'import the vendor’s key (rpm --import KEY) or fix the repo’s gpgkey= line',
    'Without signature checks a tampered package would install silently.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>The translation table</h2>
''' + table(['Job', 'Debian / Ubuntu', 'RHEL / Rocky / Fedora', 'Notes'], [
    ['Refresh metadata', '<code>apt update</code>', '<code>dnf makecache</code>', 'dnf does it automatically'],
    ['Updates waiting', '<code>apt list --upgradable</code>', '<code>dnf check-update</code>', 'exit 100 if any'],
    ['Upgrade all', '<code>apt upgrade</code>', '<code>dnf upgrade</code>', '<code>yum update</code> on old systems'],
    ['Security only', '(unattended-upgrades)', '<code>dnf upgrade --security</code>', 'needs advisories metadata'],
    ['Install', '<code>apt install X</code>', '<code>dnf install X</code>', ''],
    ['Local file', '<code>apt install ./f.deb</code>', '<code>dnf install ./f.rpm</code>', 'with dependencies'],
    ['Remove', '<code>apt remove / purge</code>', '<code>dnf remove</code>', 'configs → .rpmsave'],
    ['Unused deps', '<code>apt autoremove</code>', '<code>dnf autoremove</code>', ''],
    ['Search / info', '<code>apt search / show</code>', '<code>dnf search / info</code>', ''],
    ['Who provides a file?', '<code>apt-file search</code>', '<code>dnf provides /usr/bin/x</code>', 'works for uninstalled'],
    ['Owner of installed file', '<code>dpkg -S</code>', '<code>rpm -qf</code>', ''],
    ['Files of a package', '<code>dpkg -L</code>', '<code>rpm -ql</code>', ''],
    ['Dependencies', '<code>apt-cache depends</code>', '<code>rpm -qR</code> / <code>dnf deplist</code>', ''],
    ['Verify files', '<code>dpkg --verify</code>', '<code>rpm -V</code>', ''],
    ['Hold', '<code>apt-mark hold</code>', '<code>dnf versionlock add</code>', 'plugin'],
    ['History / undo', '<code>history.log</code>', '<code>dnf history</code> / <code>undo N</code>', ''],
    ['Groups', 'tasksel / metapackages', '<code>dnf group install</code>', ''],
    ['Clean cache', '<code>apt clean</code>', '<code>dnf clean all</code>', ''],
], minw=600) + table(['rpm query', 'Shows'], [
    ['<code>rpm -q X</code>', 'installed version or “not installed”'],
    ['<code>rpm -qa</code>', 'all installed packages'],
    ['<code>rpm -qi X</code>', 'information'],
    ['<code>rpm -ql X</code>', 'files'],
    ['<code>rpm -qc X</code>', 'config files only'],
    ['<code>rpm -qf FILE</code>', 'owner package'],
    ['<code>rpm -qR X</code>', 'requirements'],
    ['<code>rpm -q --changelog X</code>', 'package changelog (CVE fixes)'],
    ['<code>rpm -qpl f.rpm</code>', 'files in a not-installed .rpm (-p)'],
], minw=420) + qc('What is the dnf equivalent of dpkg -S?', 'rpm -qf for installed files; dnf provides for any package in the repositories.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>dnf, rpm, repositories and history, then used in every field</h2>
  <p id="commands">Our build machine runs Ubuntu, so dnf and rpm themselves cannot run here. We saved <b>typical outputs from a Rocky Linux 9 server</b> (its os-release, repo file, <code>rpm -qa</code>, <code>dnf check-update</code> and <code>dnf history</code>) into <code>~/rh</code>; every shell command below really runs on those files on our build machine. The command that produced each file on Rocky is shown in the card. Real dnf sessions are in Run on your PC.</p>
''' + cmdcard_u(['every Red Hat-family server', 'scripts that must work on both families'],
               ['assuming apt exists everywhere'])(
    'family', 'cat /etc/os-release · ID / ID_LIKE · command -v dnf', 'which family am I on?',
    '<code>/etc/os-release</code> names the distribution; <code>ID_LIKE</code> says which family it behaves like (rhel centos fedora, or debian ubuntu). Scripts check this, or simply whether <code>dnf</code> or <code>apt-get</code> exists, before installing anything.',
    '. /etc/os-release; echo $ID $ID_LIKE   ·   command -v dnf || command -v apt-get', 'safe',
    [('ID', 'rocky, rhel, fedora, ubuntu', 'exact'),
     ('ID_LIKE', 'family', 'portable scripts'),
     ('VERSION_ID', '9.4, 24.04', 'version'),
     ('PLATFORM_ID', 'platform:el9', 'RHEL builds'),
     ('command -v dnf', 'tool exists?', 'detection'),
     ('rpm -E %rhel', 'major version', 'Red Hat only')],
    dict(setup=RH, cmd="cd ~/rh\n( . ./os-release; echo \"Rocky file: ID=$ID like=[$ID_LIKE] version=$VERSION_ID\" )\n( . /etc/os-release; echo \"this machine: ID=$ID like=[$ID_LIKE] version=$VERSION_ID\" )\nfor t in dnf yum rpm apt-get dpkg; do command -v $t > /dev/null && echo \"$t: present\" || echo \"$t: absent\"; done", note='Subshells keep the variables apart. Our machine is Debian-family, so dnf and rpm are absent.'),
    [('devops', [
        dict(situation='One install function for both families.', cmd="pkg_install(){ if command -v dnf > /dev/null; then echo sudo dnf install -y \"$@\"; elif command -v apt-get > /dev/null; then echo sudo apt-get install -y \"$@\"; else echo 'no known package manager' >&2; return 1; fi; }\npkg_install tmux jq", why='echo shows the command it would run; remove echo to use it.')]),
    ],
    anat=anatomy([('sudo', 'cmd', 'root'), ('dnf', 'opt', 'high-level tool'), ('install', 'arg', 'sub-command'), ('nginx', 'arg', 'package')], 'Same shape as apt.')
) + cmdcard_u(['inventory, audits, “is it installed?”'],
               ['parsing rpm -qa by position without knowing the format'])(
    'rpmq', 'rpm -q · -qa · -qi · -ql · -qf · -qR · -V', 'rpm queries',
    'rpm’s query mode answers questions about installed packages: <code>-q NAME</code> (version), <code>-qa</code> (all), <code>-qi</code> (info), <code>-ql</code> (files), <code>-qc</code> (config files), <code>-qf FILE</code> (owner), <code>-qR</code> (requirements), <code>-V</code> (verify). Names print as <code>name-version-release.arch</code>.',
    'rpm -qa | sort   ·   rpm -qf /usr/bin/tmux   ·   rpm -V nginx', 'safe',
    [('rpm -q X', 'installed?', 'check'),
     ('rpm -qa', 'everything', 'inventory'),
     ('rpm -qa --last', 'newest first', 'what changed'),
     ('rpm -qi X', 'info', 'details'),
     ('rpm -ql / -qc X', 'files / configs', 'where'),
     ('rpm -qf FILE', 'owner', 'where from'),
     ('rpm -V X', 'changed files?', 'integrity')],
    dict(setup=RH, cmd="cd ~/rh\nwc -l < rpm-qa.txt | sed 's/^/packages in the saved rpm -qa: /'\ngrep -c '^kernel-' rpm-qa.txt | sed 's/^/installed kernels: /'\nsed -E 's/^(.+)-([^-]+)-([^-]+)\\.([^.]+)$/\\1  version=\\2  release=\\3  arch=\\4/' rpm-qa.txt | grep -E '^(nginx|tmux) '", note='name-version-release.arch: split from the right, because names can contain dashes (openssl-libs).'),
    [('sec', [
        dict(situation='Read an rpm -V line (typical output saved).', cmd="line='S.5....T.  c /etc/nginx/nginx.conf'\nflags=${line%% *}; echo \"file: ${line##* }\"\nfor i in 1 2 3 4 5 6 7 8 9; do c=${flags:i-1:1}; [ \"$c\" != . ] && case $c in S) echo ' size changed';; 5) echo ' checksum changed';; T) echo ' time changed';; M) echo ' mode changed';; U) echo ' owner changed';; esac; done; echo ' (c = config file: expected after editing)'", why='Each position is one test; . means unchanged.')]),
     ('sys', [
        dict(situation='Old kernels to clean up.', setup=RH, cmd="cd ~/rh; grep '^kernel-' rpm-qa.txt | sort -V | head -n -1 | sed 's/^/remove candidate: /'", why='Keep the newest; on Rocky dnf keeps 3 by default (installonly_limit).')]),
    ]
) + cmdcard_u(['understanding where packages come from', 'enabling EPEL or CRB'],
               ['gpgcheck=0', 'copying .repo files from random blogs'])(
    'repos', '/etc/yum.repos.d/*.repo · dnf repolist · config-manager · EPEL', 'repositories',
    'Each <code>[section]</code> in a .repo file is one repository: <code>name</code>, <code>baseurl</code> or <code>mirrorlist</code>, <code>enabled</code>, <code>gpgcheck</code> and <code>gpgkey</code>. <code>dnf repolist</code> lists enabled ones; <code>dnf config-manager --set-enabled crb</code> turns one on; <code>dnf install epel-release</code> adds EPEL.',
    'dnf repolist   ·   sudo dnf config-manager --set-enabled crb   ·   sudo dnf install epel-release', 'change',
    [('[id]', 'repo id', 'dnf --repo=id'),
     ('baseurl / mirrorlist', 'where', 'mirrors'),
     ('enabled=1', 'on', 'switch'),
     ('gpgcheck=1', 'verify signatures', 'always'),
     ('gpgkey=', 'trusted key', 'security'),
     ('$releasever $basearch', 'filled in by dnf', '9, x86_64'),
     ('dnf repolist all', 'also disabled', 'audit')],
    dict(setup=RH, cmd="cd ~/rh\nawk -F= '/^\\[/{id=$0} /^enabled/{print id, \"enabled=\" $2}' yum.repos.d/rocky.repo\ngrep -c '^gpgcheck=1' yum.repos.d/rocky.repo | sed 's/^/repos with gpgcheck on: /'\nsed -E 's/\\$releasever/9/; s/\\$basearch/x86_64/' yum.repos.d/rocky.repo | grep -m1 mirrorlist", note='The puzzle: htop lives in EPEL, which is not in this file; crb is present but disabled.'),
    [('devops', [
        dict(situation='Enable a repo by editing the file (what config-manager does).', setup=RH, cmd="cd ~/rh; sed -i '/^\\[crb\\]/,/^\\[/ s/^enabled=0/enabled=1/' yum.repos.d/rocky.repo; awk -F= '/^\\[/{id=$0} /^enabled/{print id, $2}' yum.repos.d/rocky.repo | grep crb", why='A range address limits the change to the [crb] section.')]),
    ]
) + cmdcard_u(['patching Red Hat servers', 'rolling back a bad change'],
               ['dnf upgrade on production without check-update and history'])(
    'dnf', 'dnf check-update · upgrade · install · remove · history · undo', 'dnf in daily use',
    '<code>dnf check-update</code> lists available updates (exit 100 if any). <code>sudo dnf upgrade</code> installs them; <code>--security</code> only security fixes. <code>dnf install/remove</code> work like apt. Every run becomes a transaction: <code>dnf history</code>, <code>dnf history info N</code>, <code>sudo dnf history undo N</code> or <code>rollback N</code>.',
    'dnf check-update   ·   sudo dnf upgrade   ·   sudo dnf history undo 13', 'change',
    [('dnf check-update', 'preview, exit 100', 'monitoring'),
     ('dnf upgrade', 'patch all', 'routine'),
     ('dnf upgrade --security', 'security only', 'urgent'),
     ('dnf install X', 'install', 'daily'),
     ('dnf remove X', 'uninstall + unused deps', 'cleanup'),
     ('dnf history', 'transactions', 'audit'),
     ('dnf history undo N', 'reverse one', 'rollback')],
    dict(setup=RH, cmd="cd ~/rh\ngrep -cE '^[a-z]' check-update.txt | sed 's/^/updates waiting: /'\nawk 'NF==3 {split($1,a,\".\"); print a[1], \"->\", $2, \"from\", $3}' check-update.txt\nawk -F'|' 'NR>2 && $4 ~ /Upgrade/ {gsub(/ /,\"\",$1); print \"last upgrade: transaction\", $1, \"on\", $3, \"(\" $5+0 \" packages)\"}' dnf-history.txt", note='The puzzle: 1: is the epoch of nginx’s version; transaction 13 was the 42-package upgrade that `dnf history undo 13` would reverse.'),
    [('sys', [
        dict(situation='Exit code 100 in a monitoring check.', setup=RH, cmd="cd ~/rh; check(){ grep -qE '^[a-z]' check-update.txt && return 100 || return 0; }; check; rc=$?; case $rc in 100) echo \"WARNING: updates available (exit $rc)\";; 0) echo OK;; *) echo ERROR;; esac", why='dnf check-update uses exactly these codes.')]),
    ]
) + undo('dnf is the friendliest here: almost every change has an undo.', [
    ('Bad upgrade:', '<code>sudo dnf history undo N</code> (or <code>rollback N</code> to go back to that point).'),
    ('Removed something needed:', '<code>sudo dnf history undo LAST</code>, or install it again.'),
    ('Edited config replaced:', 'your version is saved as <code>.rpmsave</code>; a new default as <code>.rpmnew</code>.'),
    ('Repo breaks dnf:', 'disable it: <code>sudo dnf config-manager --set-disabled ID</code> or <code>--disablerepo=ID</code>.'),
]) + '<h3>Errors students see most on Rocky 9</h3><p class="muted">Typical messages from a Rocky Linux 9 server (not run here: our build machine is Ubuntu).</p>' + table(['Message', 'Meaning', 'Fix'], [
    ['<code>Error: Unable to find a match: htop</code>', 'not in the enabled repositories', 'enable EPEL: <code>sudo dnf install epel-release</code>'],
    ['<code>error: Failed dependencies: libfoo.so.1 is needed by app</code>', 'rpm -i does not fetch dependencies', '<code>sudo dnf install ./app.rpm</code>'],
    ['<code>Error: This command has to be run with superuser privileges</code>', 'changes need root', '<code>sudo dnf …</code>'],
    ['<code>Signature … key ID 350d275d: NOKEY</code>', 'signing key not imported', '<code>sudo rpm --import KEYFILE</code>'],
    ['<code>Error: Failed to download metadata for repo</code>', 'mirror unreachable or wrong URL', 'check network/proxy; <code>--disablerepo=ID</code>'],
], minw=520) + errors('And the mirror image on our Ubuntu build machine, really run:', [
    dict(cmd="dnf --version", meaning='dnf does not exist on Ubuntu, just as apt does not exist on Rocky.', fix='Use the family’s own tool (detect with /etc/os-release).'),
    dict(cmd="rpm -qa", meaning='No rpm tool on Debian-family systems.', fix='dpkg -l.'),
]) + qc('What does exit code 100 from dnf check-update mean?', 'Updates are available.') + '''
'''
cards = cards + '</section>\n'

TX = [('11', 'install nginx', 'green'), ('12', 'remove httpd', 'amber'), ('13', 'upgrade (42)', 'red'), ('undo 13', 'reverse the 42 upgrades', 'blue')]
def hist(k):
    return ''.join(label_box(14, 12 + i * 40, 330, 32, [f'transaction {a}: {b}'], c if i <= k else 'card', 8.2) for i, (a, b, c) in enumerate(TX))
see_cmds = [['$ sudo dnf install nginx', ('Complete!', 'out')], ['$ sudo dnf remove httpd', ('Complete!', 'out')], ['$ sudo dnf upgrade', ('Upgraded: 42 packages', 'out'), ('(the app breaks)', 'acc')], ['$ sudo dnf history undo 13', ('Downgraded: 42 packages', 'out')]]
see = [term(14, 16, 332, 116, c, title='riya@rocky9: ~', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['11.', '12.', '13.', 'Undo.'])]
behind = [hist(k) for k in range(4)]
two = anim_two('dnf history and undo', 'Behind the screen: numbered transactions',
               'A Rocky terminal: install, remove and a 42-package upgrade become transactions 11 to 13; dnf history undo 13 downgrades them again.',
               'Four stacked boxes: transactions 11, 12, 13 and the undo of 13.', see, behind,
               ['11.', '12.', '13.', 'undo.'],
               ['11', '12', '13', 'undo'])

def ver(k):
    parts = [('epoch', '1:', 'red'), ('version', '1.20.1', 'blue'), ('release', '16.el9_4.1', 'green'), ('arch', 'x86_64', 'violet')]
    o = t(180, 20, 'nginx-1:1.20.1-16.el9_4.1.x86_64', 9.6, 'ink2', bold=True)
    for i in range(k + 1):
        a, b, c = parts[i]
        o += label_box(14 + i * 86, 40, 80, 50, [a, b], c, 8)
    o += t(180, 130, ['epoch beats everything else', 'upstream version', 'distro build + target (el9_4)', 'CPU architecture'][k], 9, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'Reading an RPM version',
              'epoch:version-release.arch, piece by piece.',
              '1:1.20.1-16.el9_4.1.x86_64', 'An RPM version split into epoch, version, release and architecture boxes.', [ver(k) for k in range(4)],
              ['epoch.', 'version.', 'release.', 'arch.'], hid='scenario-version')

dx = dissect('Layer by layer: the Red Hat package stack',
    'Each layer has a real command (on the saved Rocky files) from our build machine.', [
    dict(key='repo', name='Repos', sub='.repo files', why='Where from.', how='INI sections.', impl='/etc/yum.repos.d.', used='dnf repolist.',
         setup=RH, cmd="cd ~/rh; grep -c '^\\[' yum.repos.d/rocky.repo | sed 's/^/repositories defined: /'; grep '^\\[' yum.repos.d/rocky.repo | tr -d '[]' | paste -sd' '"),
    dict(key='db', name='RPM database', sub='/var/lib/rpm', why='What is installed.', how='SQLite (RHEL 9).', impl='rpmdb.sqlite.', used='rpm -q.',
         setup=RH, cmd="cd ~/rh; grep -v '^gpg-pubkey' rpm-qa.txt | wc -l | sed 's/^/real packages: /'; grep -c '^gpg-pubkey' rpm-qa.txt | sed 's/^/imported signing keys (pseudo-packages): /'"),
    dict(key='hist', name='History', sub='transactions', why='Undo.', how='dnf history DB.', impl='/var/lib/dnf/history.sqlite.', used='Rollbacks.',
         setup=RH, cmd="cd ~/rh; awk -F'|' 'NR>2{gsub(/ +/,\" \"); print \"#\"$1\"|\"$2\"|\"$4}' dnf-history.txt | sed 's/  */ /g'"),
    dict(key='cmp', name='Version order', sub='rpm vs text', why='Upgrades.', how='Segment by segment.', impl='rpmvercmp.', used='Which is newer.',
         cmd="printf '%s\\n' 1.20.1-16.el9_4.1 1.20.1-14.el9_2.1 1.20.1-9.el9 | sort -V"),
], hint='From repo files to version order. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Transactions and undo, and an RPM version</h2>
''' + two + s1 + dx + qc('Why do imported GPG keys appear in rpm -qa?', 'rpm stores them as pseudo-packages named gpg-pubkey-KEYID-DATE.') + '''
</section>
'''

VAR = variations('Sixteen more one-liners on the saved Rocky outputs and for translating between families. All were really run on our build machine.', [
    ('Translating', [
        dict(title='apt → dnf translator', cmd="tr(){ case \"$1\" in update) echo 'dnf makecache';; upgrade) echo 'dnf upgrade';; install) echo 'dnf install';; remove|purge) echo 'dnf remove';; autoremove) echo 'dnf autoremove';; search) echo 'dnf search';; show) echo 'dnf info';; *) echo '?';; esac; }; for c in update upgrade purge show; do printf 'apt %-8s -> %s\\n' $c \"$(tr $c)\"; done", why='Muscle memory, mapped.'),
        dict(title='dpkg → rpm translator', cmd="for p in '-S:-qf' '-L:-ql' '-l:-qa' '-s:-qi' '--verify:-V'; do printf 'dpkg %-9s = rpm %s\\n' \"${p%%:*}\" \"${p#*:}\"; done", why='Query twins.'),
        dict(title='Package file names', cmd="for f in nginx_1.24.0-2ubuntu7_amd64.deb nginx-1.20.1-16.el9_4.1.x86_64.rpm; do case $f in *.deb) echo \"$f: Debian (name_version_arch)\";; *.rpm) echo \"$f: RPM (name-version-release.arch)\";; esac; done", why='Separators differ: _ for deb, - and . for rpm.'),
    ]),
    ('rpm -qa analysis', [
        dict(title='Only names', setup=RH, cmd="cd ~/rh; sed -E 's/-[^-]+-[^-]+$//' rpm-qa.txt | grep -v gpg-pubkey | paste -sd' '", why='Strip version-release.arch from the right.'),
        dict(title='Packages built for el9_4', setup=RH, cmd="cd ~/rh; grep -c 'el9_4' rpm-qa.txt", why='The dist tag shows the minor release of the build.'),
        dict(title='Is nginx installed? (like rpm -q)', setup=RH, cmd="cd ~/rh; grep -E '^nginx-[0-9]' rpm-qa.txt || echo 'package nginx is not installed'", why='The rpm -q answer.'),
        dict(title='Newest kernel', setup=RH, cmd="cd ~/rh; grep '^kernel-' rpm-qa.txt | sort -V | tail -1", why='sort -V understands versions.'),
        dict(title='Architectures present', setup=RH, cmd="cd ~/rh; grep -v gpg-pubkey rpm-qa.txt | awk -F. '{print $NF}' | sort | uniq -c", why='x86_64, noarch, i686 on mixed systems.'),
    ]),
    ('check-update and history', [
        dict(title='Updates by repository', setup=RH, cmd="cd ~/rh; awk 'NF==3{print $3}' check-update.txt | sort | uniq -c", why='baseos vs appstream.'),
        dict(title='Updates with an epoch', setup=RH, cmd="cd ~/rh; awk 'NF==3 && $2 ~ /^[0-9]+:/ {print $1, $2}' check-update.txt", why='The 1: from the puzzle.'),
        dict(title='Security-relevant names', setup=RH, cmd="cd ~/rh; grep -E '^(openssl|curl|kernel)' check-update.txt | awk '{print $1}'", why='Patch these first.'),
        dict(title='Transactions per action', setup=RH, cmd="cd ~/rh; awk -F'|' 'NR>2{gsub(/ /,\"\",$4); print $4}' dnf-history.txt | sort | uniq -c", why='dnf history summary.'),
        dict(title='What would undo 12 do?', setup=RH, cmd="cd ~/rh; awk -F'|' 'NR>2 && $1+0==12 {print \"undo 12 would reinstall what was removed by:\", $2}' dnf-history.txt | sed 's/  */ /g'", why='Undo reverses the action: removed → installed again.'),
        dict(title='Changes in the last week', setup=RH, cmd="cd ~/rh; awk -F'|' 'NR>2 && $3 >= \" 2026-11-05\"' dnf-history.txt | wc -l", why='Text dates compare correctly in ISO format.'),
    ]),
    ('Repo files', [
        dict(title='All repo ids and URLs', setup=RH, cmd="cd ~/rh; awk -F= '/^\\[/{id=$0} /^mirrorlist/{print id, substr($2,1,45)\"…\"}' yum.repos.d/rocky.repo", why='Quick audit.'),
        dict(title='Repos without gpgcheck (should be none)', setup=RH, cmd="cd ~/rh; awk -F= '/^\\[/{id=$0} /^gpgcheck=0/{print id}' yum.repos.d/*.repo | wc -l", why='A security check for audits.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>dnf and rpm at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['RHEL', 'enterprise'], 'red', 8.6), '1. Enterprise servers',
              'Banks, telecoms and governments run RHEL or Rocky for long support (10 years); patching is dnf upgrade in windows, tracked in dnf history.', ['Window', '*dnf upgrade', 'history']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['undo', 'rollback'], 'green', 8.6), '2. Fast rollbacks',
    'dnf history undo turns a bad patch night into a five-minute rollback.', ['Bad patch', '*history undo', 'back']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['EPEL', 'tools'], 'amber', 8.6), '3. Extra tools',
    'htop, ncdu, jq on RHEL usually come from EPEL; CRB provides -devel packages for building software.', ['Need htop', '*EPEL', 'installed']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['both', 'scripts'], 'blue', 8.6), '4. Cross-distro automation',
    'Ansible’s package module and shell scripts check os-release and call apt or dnf as needed.', ['os-release', '*detect', 'apt or dnf']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['rpm -V', 'audit'], 'violet', 8.6), '5. Compliance audits',
    'rpm -Va lists every changed packaged file; auditors review unexpected changes outside /etc.', ['rpm -Va', '*review', 'report']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine on the saved Rocky outputs.', [
    dict(level='b', title='Which family?', scenario='New server.', cmd="( . /etc/os-release; echo \"$ID ($ID_LIKE)\" )", explain='os-release.'),
    dict(level='b', title='Count packages', scenario='Inventory.', setup=RH, cmd="grep -vc gpg-pubkey ~/rh/rpm-qa.txt", explain='rpm -qa | wc -l.'),
    dict(level='i', title='Updates waiting', scenario='Patch check.', setup=RH, cmd="grep -cE '^[a-z]' ~/rh/check-update.txt", explain='dnf check-update.'),
    dict(level='i', title='Enabled repos', scenario='Audit.', setup=RH, cmd="awk -F= '/^\\[/{id=$0} /^enabled=1/{print id}' ~/rh/yum.repos.d/rocky.repo | tr -d '[]' | paste -sd' '", explain='enabled=1.'),
    dict(level='a', title='Last transaction', scenario='Rollback.', setup=RH, cmd="awk -F'|' 'NR==3{gsub(/  +/,\" \"); print \"#\"$1, $2}' ~/rh/dnf-history.txt", explain='dnf history | head.'),
], extra=build_up('a patch report for Rocky', 'Riya turns the saved dnf outputs into a one-paragraph report.', RH, [
    ("cd ~/rh; n=$(grep -cE '^[a-z]' check-update.txt); echo \"$n updates waiting\"", '1. How many updates?'),
    ("cd ~/rh; grep -E '^(openssl|curl|kernel)' check-update.txt | awk '{print $1}' | paste -sd' ' | sed 's/^/security-relevant: /'", '2. Which matter most?'),
    ("cd ~/rh; awk -F'|' 'NR>2 && $4 ~ /Upgrade/ {gsub(/ /,\"\",$1); print \"previous upgrade: #\"$1\" on\"$3; exit}' dnf-history.txt", '3. When was the last upgrade?'),
    ("cd ~/rh; echo \"plan: sudo dnf upgrade --security; if it breaks: sudo dnf history undo $(( $(awk -F'|' 'NR==3{print $1+0}' dnf-history.txt) + 1 ))\"", '4. The plan, with its undo.'),
], cumulative=False)) + VAR + which('Choosing the right tool.', [
    ('Install with dependencies', 'dnf install', 'Repos, solver.', 'rpm -ivh.'),
    ('Query installed', 'rpm -q…', 'Fast, offline.', 'dnf list installed for one file.'),
    ('Who provides a missing file?', 'dnf provides', 'Searches repos.', 'Googling.'),
    ('Roll back', 'dnf history undo', 'Exact.', 'Manual downgrades.'),
    ('Extra packages', 'EPEL', 'Maintained.', 'Random .rpm downloads.'),
    ('Both families', 'detect via os-release', 'Portable.', 'Hard-coded apt.'),
]) + keys('Handy forms (Rocky / RHEL).', [
    ('dnf check-update', 'preview', 'exit 100'),
    ('sudo dnf upgrade --security', 'security', 'urgent'),
    ('rpm -qf FILE', 'owner', 'where from'),
    ('dnf provides */htop', 'find a file', 'missing tools'),
    ('dnf history info N', 'details', 'audit'),
    ('sudo dnf history undo N', 'reverse', 'rollback'),
]) + scriptit('pkgfamily.sh', 'Detect the package family of the machine and print the right commands for refresh, upgrade, install, owner-of-file and history, so the same runbook works on Ubuntu and Rocky.',
'''. /etc/os-release
case " $ID $ID_LIKE " in
  *" debian "*|*" ubuntu "*) fam=debian ;;
  *" rhel "*|*" fedora "*|*" centos "*) fam=redhat ;;
  *) fam=unknown ;;
esac
echo "machine: $PRETTY_NAME -> family: $fam"
case $fam in
  debian) printf '%s\\n' 'refresh:  sudo apt update' 'upgrade:  sudo apt upgrade' 'install:  sudo apt install PKG' 'owner:    dpkg -S FILE' 'history:  less /var/log/apt/history.log' ;;
  redhat) printf '%s\\n' 'refresh:  sudo dnf makecache' 'upgrade:  sudo dnf upgrade' 'install:  sudo dnf install PKG' 'owner:    rpm -qf FILE' 'history:  dnf history' ;;
  *) echo "unknown family"; exit 1 ;;
esac''',
'<p>On our Ubuntu build machine it prints the Debian commands.</p>', expect='any') + puzzle_answer('<b>1.</b> htop is not in Rocky’s BaseOS/AppStream; it is in <b>EPEL</b>. Enable it with <code>sudo dnf install epel-release</code> (and usually <code>sudo dnf config-manager --set-enabled crb</code>), then <code>sudo dnf install htop</code>. <b>2.</b> <code>1:</code> is the <b>epoch</b>: it comes first in comparisons and is added when upstream version numbering would otherwise sort wrongly; rpm -q hides an epoch unless you ask (<code>rpm -q --qf "%{EPOCH}:%{VERSION}-%{RELEASE}\\n" nginx</code>). <b>3.</b> Yes: every dnf run is a numbered transaction; <code>sudo dnf history undo 13</code> downgrades the 42 packages that transaction 13 upgraded (if the old versions are still available in the repositories or cache).') + qc('Which dnf command reverses transaction 13?', 'sudo dnf history undo 13.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/rh', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-apt-and-dpkg-on-ubuntu-and-debian/">Lesson 14.2</a> (apt and dpkg): this lesson maps each command to its Red Hat twin.') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
