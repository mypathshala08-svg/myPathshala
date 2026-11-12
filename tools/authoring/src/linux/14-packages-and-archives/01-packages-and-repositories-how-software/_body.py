import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# Build two tiny .deb packages and a private dpkg database (so riya can really install and remove).
PK = r"""export PATH=$PATH:/usr/sbin:/sbin; rm -rf ~/pk; mkdir -p ~/pk; cd ~/pk
mk(){ n=$1; v=$2; dep=$3; d=${n}_$v; mkdir -p $d/DEBIAN $d/usr/local/bin
  printf 'Package: %s\nVersion: %s\nArchitecture: all\nMaintainer: Riya <riya@example.com>\n%sDescription: %s demo tool\n' "$n" "$v" "${dep:+Depends: $dep
}" "$n" > $d/DEBIAN/control
  printf '#!/bin/sh\necho "%s %s says hello"\n' "$n" "$v" > $d/usr/local/bin/$n; chmod 755 $d/usr/local/bin/$n
  dpkg-deb --build --root-owner-group $d > /dev/null; }
mk greet 1.0 ''; mk greet 1.1 ''; mk report 2.0 'greet (>= 1.0)'
mkdir -p root/var/lib/dpkg/updates root/var/lib/dpkg/info; touch root/var/lib/dpkg/status
pdpkg(){ dpkg --force-not-root --root="$HOME/pk/root" --log="$HOME/pk/dpkg.log" "$@"; }"""

HOOK = hook('Riya needs a tool called <code>tree</code> on a new server. On Windows she would search a website, download an installer and click Next five times. On Linux she types <code>sudo apt install tree</code> and two seconds later it is there, already in the PATH, with its manual page, and it will be updated together with the rest of the system. That is the <b>package</b> idea: software is shipped as signed archives (packages) that list what they need (dependencies), from trusted online stores (repositories), installed and tracked by a <b>package manager</b>. This lesson explains the moving parts and lets you build, inspect, install and remove a real package yourself.',
    ['explain packages, repositories, package managers, dependencies and versions in plain words',
     'tell the two big families apart (.deb with dpkg/apt, .rpm with rpm/dnf) and the universal formats (snap, flatpak, AppImage)',
     'find out which package owns a file, what a package contains and what it depends on',
     'build a tiny .deb package and install, upgrade and remove it, and see a dependency error happen'])
ROAD = roadmap([
    ('story', 'The story', 3, 'two seconds to install'),
    ('decide', 'Which tool when?', 2, 'the quick chart'),
    ('definition', 'Packages and repositories', 6, 'simple meaning + 4 depths'),
    ('types', 'Formats and families', 5, 'deb, rpm, snap, flatpak'),
    ('commands', 'By field', 15, 'real runs'),
    ('animation', 'See it happen', 4, 'from repository to /usr/bin'),
    ('run', 'Run the code', 4, 'try it in the browser'),
    ('lab', 'Practice lab', 7, 'build a package'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which tool? (decide in 5 seconds)', [
    ('Install software on Ubuntu/Debian', 'sudo apt install NAME', 'apt (14.2)'),
    ('Install on Fedora/RHEL/Rocky', 'sudo dnf install NAME', 'dnf (14.3)'),
    ('Which package owns this file?', 'dpkg -S /usr/bin/ls   ·   rpm -qf FILE', 'owner'),
    ('What does a package contain?', 'dpkg -L NAME   ·   rpm -ql NAME', 'files'),
    ('What does it need?', 'apt-cache depends NAME   ·   dnf deplist NAME', 'dependencies'),
    ('Look inside a .deb file', 'dpkg-deb -I f.deb   ·   dpkg-deb -c f.deb', 'inspect'),
    ('Newest version / desktop app', 'snap / flatpak', '14.4'),
    ('Not packaged at all', 'build from source', '14.4'),
])

cmap = concept_map(
    [('1.3', 'Distributions', 'Ubuntu, RHEL, Fedora'), ('2.1', 'File system layout', '/usr/bin, /etc'), ('9.1', 'Permissions', 'why sudo')],
    ['package = files + metadata + scripts', 'repository = signed online store', 'package manager = installs and tracks', 'dependencies and versions', 'deb vs rpm, snap, flatpak', 'build and install a real .deb'],
    [('14.2', 'apt and dpkg', 'daily use'), ('14.3', 'dnf and rpm', 'Red Hat family'), ('14.4', 'snap, flatpak, source', 'other ways'), ('19.3', 'Updates', 'security patches')],
    'A package is a labelled box of files; a repository is a trusted shop of boxes; the package manager is the shopkeeper who also remembers what you bought.')

sc = (term(20, 14, 316, 156, ['$ dpkg -S /usr/bin/ls', ('coreutils: /usr/bin/ls', 'out'), '$ dpkg-query -W tmux', ('tmux    3.4-1ubuntu0.2', 'out'), '$ apt-cache depends tmux | head -3', ('tmux', 'out'), ('  Depends: libc6', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.8, step=16)
      + t(352, 36, 'Every file has', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['an owner package,', 'a version,', 'dependencies,', 'and a source', 'repository'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Two seconds to install</h2>
  <div class="story">
''' + puzzle('Riya downloads <code>report_2.0.deb</code> from a colleague and runs <code>sudo dpkg -i report_2.0.deb</code>. It answers “dependency problems - leaving unconfigured: report depends on greet (&gt;= 1.0); however: Package greet is not installed.” Her colleague says “just use apt instead of dpkg”. Another colleague says “never install .deb files from chat messages”. Who is right, and what is a dependency anyway?') + '''
    <p class="narration">Riya asks her server who owns <code>ls</code> and what tmux needs.</p>
''' + scene('A terminal: dpkg -S shows that /usr/bin/ls belongs to the coreutils package; dpkg-query shows the installed tmux version; apt-cache depends lists the libraries tmux needs.', sc,
            'The package manager <tspan font-weight="700" class="s-acc">remembers</tspan> every file it installed.') + '''
K> Why does tmux need libc6?
A> Programs share code in <b>libraries</b>. tmux does not carry its own copy of the C library; it says “I need libc6” (a <b>dependency</b>), and the package manager makes sure libc6 is installed first. One copy, shared by everyone, updated once.
R> And the puzzle?
A> <code>dpkg</code> installs one file you give it and does not fetch anything; <code>apt</code> also downloads the missing dependencies from the repository. Both colleagues have a point. Today: packages, repositories, dependencies, and a package we build ourselves.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A shop analogy: the repository is a shop with labelled boxes on shelves, each box has a label (name, version, needs) and contents (files). The package manager is the shopkeeper who fetches the box and every box it needs, unpacks them into the right rooms of the house (/usr/bin, /etc), and writes everything into a notebook (the package database).">'
       + label_box(14, 24, 180, 116, ['REPOSITORY (shop)', 'boxes on shelves', 'signed by the', 'distribution'], 'blue', 9)
       + label_box(230, 24, 180, 116, ['PACKAGE (box)', 'label: name, version,', 'needs (depends)', 'contents: files'], 'amber', 9)
       + label_box(446, 24, 180, 116, ['PACKAGE MANAGER', 'fetches box + needs,', 'unpacks to /usr/bin…', 'writes the notebook'], 'green', 9)
       + arrow(194, 82, 230, 82) + arrow(410, 82, 446, 82)
       + t(320, 166, 'One command: find, check, download, unpack, configure, record.', 10, 'acc', bold=True)
       + t(320, 188, 'Removing later is just as clean, because the notebook lists every file.', 9.2, 'ink2')
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('Packages at four depths', [
    ('v', 'No jargon: a shop, a box and a shopkeeper', '      <p>You ask for a box; the shopkeeper brings it and everything it needs.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>sudo apt install tree</code>: install (Ubuntu/Debian).</li>
        <li><code>sudo dnf install tree</code>: install (Fedora/RHEL).</li>
        <li><code>dpkg -S /usr/bin/ls</code>: which package owns a file.</li>
        <li><code>apt show tree</code>: what a package is.</li>
      </ul>'''),
    ('i', 'The parts', '''      <ul>
        <li>A <b>package</b> (.deb or .rpm) is an archive of files plus <b>metadata</b> (name, version, architecture, dependencies, description) and optional <b>maintainer scripts</b> (run before/after install or removal).</li>
        <li>A <b>repository</b> is a web server with many packages and a signed <b>index</b>; your system lists repositories in <code>/etc/apt/sources.list.d/</code> or <code>/etc/yum.repos.d/</code>.</li>
        <li>The <b>low-level</b> tool (dpkg, rpm) installs one package file and keeps the database; the <b>high-level</b> tool (apt, dnf) reads repositories, solves dependencies and calls the low-level tool.</li>
        <li>Versions like <code>3.4-1ubuntu0.2</code> are “upstream version 3.4, Debian revision 1, Ubuntu’s 0.2 update”.</li>
      </ul>'''),
    ('a', 'Behind the screen: indexes, signatures and the database', '''      <ul>
        <li><code>apt update</code> downloads each repository’s <code>InRelease</code> file (signed with GPG) and <code>Packages</code> indexes into <code>/var/lib/apt/lists/</code>; the signature is checked against keys in <code>/usr/share/keyrings/</code>. A package whose checksum does not match the signed index is refused.</li>
        <li>The installed-package database is <code>/var/lib/dpkg/status</code> plus per-package file lists <code>/var/lib/dpkg/info/NAME.list</code> (rpm: an SQLite database in <code>/var/lib/rpm</code>).</li>
        <li>Dependency solving is a real constraint problem (versions, conflicts, “provides”); apt and dnf use solvers to choose a consistent set.</li>
        <li>Downloaded package files are cached in <code>/var/cache/apt/archives/</code> until <code>apt clean</code>.</li>
        <li>A .deb is an <code>ar</code> archive with <code>control.tar</code> (metadata, scripts) and <code>data.tar</code> (the files); an .rpm is a header plus a cpio archive.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>Packages, repositories and package managers</h2>
''' + def_block(
    'A <b>package</b> is an archive containing a program’s files together with metadata (name, version, architecture, description, <b>dependencies</b> on other packages) and install scripts. A <b>repository</b> is a signed collection of packages served over the network. A <b>package manager</b> installs, upgrades and removes packages, resolves dependencies and keeps a database of every installed file. Debian and Ubuntu use .deb packages with <code>dpkg</code> and <code>apt</code>; Red Hat, Fedora and Rocky use .rpm with <code>rpm</code> and <code>dnf</code>.',
    'Signed boxes of software from trusted shops, installed and remembered by one tool.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Package', 'Files + metadata + scripts in one archive.'),
    ('Repository (repo)', 'A signed online store of packages.'),
    ('Package manager', 'apt, dnf: install, upgrade, remove.'),
    ('Dependency', 'Another package this one needs.'),
    ('Library', 'Shared code used by many programs.'),
    ('Metadata', 'Name, version, depends, description.'),
    ('Maintainer script', 'Runs at install/remove (postinst…).'),
    ('Upstream', 'The original authors of the software.'),
]) + '\n' + names('Where the names come from.', [
    ('dpkg', 'Debian package', '1994.'),
    ('apt', 'Advanced Package Tool', '1998.'),
    ('rpm', 'Red Hat Package Manager', '1997.'),
    ('yum / dnf', 'Yellowdog Updater, Modified / Dandified yum', '2003 / 2015.'),
    ('.deb', 'Debian', 'ar archive.'),
    ('noble', 'Ubuntu 24.04 code name', 'Noble Numbat.'),
    ('main / universe', 'Ubuntu repo components', 'supported / community.'),
    ('PPA', 'Personal Package Archive', 'Launchpad.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Install', '<code>sudo apt install X</code>'),
    ('Owner of a file', '<code>dpkg -S FILE</code>'),
    ('Files of a package', '<code>dpkg -L X</code>'),
    ('Needs', '<code>apt-cache depends X</code>'),
    ('Repos list', '<code>/etc/apt/sources.list.d/</code>'),
    ('Installed DB', '<code>/var/lib/dpkg/status</code>'),
]) + '\n' + lv + didyou('Debian’s package archive has more than 60,000 source packages, maintained by about a thousand volunteers. Ubuntu builds on it, and many other distributions (Mint, Pop!_OS, Kali) build on Ubuntu or Debian: the same .deb format everywhere.') + '''
EXAM> “What is the difference between dpkg and apt?” → dpkg installs a single local .deb and does not resolve dependencies; apt uses repositories, downloads packages and resolves dependencies (and calls dpkg).
''' + qc('Which file lists the repositories on Ubuntu 24.04?', '/etc/apt/sources.list.d/ubuntu.sources (older systems: /etc/apt/sources.list).') + mistake('installing random .deb/.rpm files from the internet or chat',
    'use the distribution’s repositories, the vendor’s official repository, or snap/flatpak; check the source and the signature',
    'A package runs install scripts as root: a malicious one can do anything to the machine.') + mistake('sudo dpkg -i app.deb and stopping at the dependency error',
    'sudo apt install ./app.deb   (apt resolves and downloads the dependencies)',
    'dpkg does not fetch anything: “dependency problems - leaving unconfigured” (real run, puzzle).') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Package formats and families</h2>
''' + table(['Family', 'Distributions', 'Format', 'Low-level', 'High-level', 'Repo config'], [
    ['Debian', 'Debian, Ubuntu, Mint, Kali', '.deb', 'dpkg', 'apt, apt-get', '/etc/apt/sources.list.d/'],
    ['Red Hat', 'RHEL, Fedora, Rocky, Alma, CentOS Stream', '.rpm', 'rpm', 'dnf (yum)', '/etc/yum.repos.d/'],
    ['SUSE', 'openSUSE, SLES', '.rpm', 'rpm', 'zypper', '/etc/zypp/repos.d/'],
    ['Arch', 'Arch, Manjaro', '.pkg.tar.zst', 'pacman', 'pacman', '/etc/pacman.conf'],
    ['Alpine', 'Alpine (containers)', '.apk', 'apk', 'apk', '/etc/apk/repositories'],
], minw=560) + table(['', 'Distribution packages', 'snap', 'flatpak', 'AppImage', 'From source'], [
    ['Who builds', 'the distribution', 'the vendor (Canonical store)', 'the vendor (Flathub)', 'the vendor', 'you'],
    ['Dependencies', 'shared libraries', 'bundled', 'shared runtimes', 'bundled in one file', 'you install them'],
    ['Updates', 'with the system', 'automatic', 'flatpak update', 'manual', 'manual'],
    ['Isolation', 'none', 'confined', 'sandboxed', 'none', 'none'],
    ['Best for', 'servers, almost everything', 'desktop apps, some tools', 'desktop apps', 'try an app', 'not packaged / newest'],
], minw=560) + table(['Version string', 'Means'], [
    ['<code>3.4-1ubuntu0.2</code>', 'upstream 3.4, Debian revision 1, Ubuntu update 0.2'],
    ['<code>2:8.2.3995-1</code>', 'epoch 2 (overrides version ordering), version, revision'],
    ['<code>1.0~rc1</code>', '~ sorts before: 1.0~rc1 &lt; 1.0'],
    ['<code>5.14.0-427.el9</code>', 'RPM: version 5.14.0, release 427 for EL 9'],
], minw=420) + qc('Which tool installs a single .deb file without fetching its dependencies?', 'dpkg (apt install ./file.deb fetches them).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Ask the system, inspect, build and install a package, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya. Queries about installed packages run on the real system. To install and remove without sudo, we built two tiny packages (<code>greet</code> 1.0 and 1.1, and <code>report</code> 2.0 which depends on greet) and used dpkg’s own option to install into a private folder: <code>pdpkg</code> below means <code>dpkg --force-not-root --root=~/pk/root</code>. On your PC you would use <code>sudo dpkg</code> or <code>sudo apt</code>.</p>
''' + cmdcard_u(['“where does this file come from?”', 'auditing what is installed'],
               ['guessing package names'])(
    'ask', 'dpkg -S · dpkg -L · dpkg-query -W · apt-cache depends/rdepends', 'asking the package database',
    '<code>dpkg -S FILE</code> names the package that installed a file. <code>dpkg -L PKG</code> lists its files. <code>dpkg-query -W -f=…</code> prints chosen fields for installed packages. <code>apt-cache depends</code> and <code>rdepends --installed</code> show what a package needs and what needs it.',
    'dpkg -S /usr/bin/ls   ·   dpkg -L tmux   ·   apt-cache depends tmux', 'safe',
    [('dpkg -S FILE', 'owner package', 'where from'),
     ('dpkg -L PKG', 'files of a package', 'what it installed'),
     ('dpkg -l | grep PKG', 'installed? version?', 'check'),
     ('dpkg-query -W -f', 'custom fields', 'reports'),
     ('apt-cache depends', 'needs', 'before removing'),
     ('apt-cache rdepends --installed', 'needed by', 'impact'),
     ('apt show PKG', 'description', 'what is it')],
    dict(cmd="dpkg -S /usr/bin/ls /usr/bin/awk 2>&1 | head -2\ndpkg -L tmux | grep -E 'bin/|man1' \ndpkg-query -W -f='${Package} ${Version} ${Installed-Size}KB\\n' bash tmux\napt-cache depends tmux | grep Depends | head -3", note='awk belongs to no package directly: /usr/bin/awk is a symlink managed by the alternatives system.'),
    [('sys', [
        dict(situation='How many packages, and the biggest ones?', cmd="dpkg -l | grep -c '^ii'\ndpkg-query -W -f='${Installed-Size}\\t${Package}\\n' | sort -rn | head -3 | awk '{printf \"%6.0f MB  %s\\n\", $1/1024, $2}'", why='Disk-space audits often start here.')]),
     ('sec', [
        dict(situation='Has a system file been changed since install?', cmd="dpkg --verify coreutils | grep -v -E '/usr/share/(doc|man|info)' | wc -l | sed 's/^/changed or missing program files: /'\ndpkg --verify coreutils | grep -c '/usr/share/doc' | sed 's/^/missing doc files: /'", why='--verify compares installed files with the package’s MD5 sums. Our build image deletes documentation to save space, so docs show as missing; the programs themselves all match.')]),
    ],
    anat=anatomy([('dpkg', 'cmd', 'low-level tool'), ('-S', 'opt', 'search: who owns'), ('/usr/bin/ls', 'arg', 'a file')], 'dpkg -S / -L / -l / -s / -i / -r.')
) + cmdcard_u(['looking inside a package before installing', 'understanding the format'],
               ['installing packages you have not looked at'])(
    'inspect', 'dpkg-deb -I · dpkg-deb -c · ar t', 'inside a .deb',
    'A .deb is an <code>ar</code> archive with three members: <code>debian-binary</code>, <code>control.tar.*</code> (metadata and scripts) and <code>data.tar.*</code> (the files). <code>dpkg-deb -I</code> shows the control fields, <code>-c</code> the file list, <code>-x</code> extracts the files without installing.',
    'dpkg-deb -I f.deb   ·   dpkg-deb -c f.deb   ·   dpkg-deb -x f.deb dir', 'safe',
    [('dpkg-deb -I', 'metadata', 'what is it'),
     ('dpkg-deb -c', 'file list', 'where it goes'),
     ('dpkg-deb -x f.deb d/', 'extract only', 'look closer'),
     ('dpkg-deb -e f.deb d/', 'control files and scripts', 'audit scripts'),
     ('ar t f.deb', 'raw members', 'format'),
     ('dpkg-deb --build DIR', 'make a .deb', 'packaging')],
    dict(setup=PK, cmd="cd ~/pk\nls *.deb\nar t report_2.0.deb\ndpkg-deb -I report_2.0.deb | sed -n '/Package/,$p'\ndpkg-deb -c report_2.0.deb | awk '{print $1, $NF}' | tail -1", note='report needs greet (>= 1.0); its only file goes to /usr/local/bin.'),
    [('dev', [
        dict(situation='Build a package from a folder.', setup=PK, cmd="cd ~/pk; mkdir -p hi_0.1/DEBIAN hi_0.1/usr/local/bin\nprintf 'Package: hi\\nVersion: 0.1\\nArchitecture: all\\nMaintainer: Riya <riya@example.com>\\nDescription: says hi\\n' > hi_0.1/DEBIAN/control\nprintf '#!/bin/sh\\necho hi\\n' > hi_0.1/usr/local/bin/hi; chmod 755 hi_0.1/usr/local/bin/hi\ndpkg-deb --build --root-owner-group hi_0.1 && ls -l hi_0.1.deb | awk '{print $5, $NF}'", why='DEBIAN/control + files in their final paths: that is all a basic .deb needs.')]),
    ]
) + cmdcard_u(['installing, upgrading and removing', 'understanding dependency errors'],
               ['dpkg -i for packages with missing dependencies (use apt install ./file.deb)'])(
    'install', 'dpkg -i · dpkg -r / -P · dependency errors · upgrade by a newer .deb', 'install, upgrade, remove',
    '<code>dpkg -i FILE.deb</code> unpacks and configures a package and records it; installing a newer version upgrades it. If a dependency is missing, dpkg stops with “dependency problems”; apt would fetch it. <code>dpkg -r</code> removes a package (keeps config files), <code>-P</code> purges everything.',
    'sudo dpkg -i f.deb   ·   sudo dpkg -r NAME   ·   sudo apt install ./f.deb', 'change',
    [('dpkg -i f.deb', 'install / upgrade', 'local file'),
     ('dpkg -r NAME', 'remove (keep config)', 'uninstall'),
     ('dpkg -P NAME', 'purge', 'clean'),
     ('dpkg -l NAME', 'status (ii, rc, iU)', 'check'),
     ('apt install ./f.deb', 'with dependencies', 'normal way'),
     ('apt -f install', 'fix broken deps', 'after dpkg errors')],
    dict(setup=PK, cmd="cd ~/pk\npdpkg -i report_2.0.deb 2>&1 | grep -E 'depends|not installed' | head -2\npdpkg -l report 2>/dev/null | tail -1 | cut -c1-40\npdpkg -i greet_1.0.deb > /dev/null; pdpkg --configure -a > /dev/null 2>&1\npdpkg -l | awk '/^ii/{print $2, $3}'", expect='any', note='The puzzle: report could not be configured until greet was installed (iU = unpacked, not configured).'),
    [('sys', [
        dict(situation='Upgrade and remove.', setup=PK, cmd="cd ~/pk; pdpkg -i greet_1.0.deb > /dev/null\npdpkg -i greet_1.1.deb 2>&1 | grep -E 'Unpacking|Setting up'\n~/pk/root/usr/local/bin/greet\npdpkg -r greet > /dev/null; pdpkg -l greet 2>&1 | tail -1 | cut -c1-40; ls ~/pk/root/usr/local/bin 2>/dev/null | wc -l", expect='any', why='A newer .deb replaced 1.0; remove deleted its file (and the now-empty folders); dpkg no longer knows the package.')]),
     ('qa', [
        dict(situation='Removing something others depend on.', setup=PK, cmd="cd ~/pk; pdpkg -i greet_1.0.deb report_2.0.deb > /dev/null 2>&1\npdpkg -r greet 2>&1 | grep -E 'depends|dependency' | head -2", expect='any', why='dpkg refuses to break report; apt would offer to remove both.')]),
    ]
) + cmdcard_u(['understanding where packages come from', 'adding a vendor repository'],
               ['adding repositories from blogs without checking keys'])(
    'repos', '/etc/apt/sources.list.d/*.sources · apt update · keyrings', 'repositories',
    'Ubuntu 24.04 describes repositories in “deb822” files: <code>Types</code>, <code>URIs</code>, <code>Suites</code> (release and updates), <code>Components</code> (main, universe, restricted, multiverse) and <code>Signed-By</code> (the key that must have signed the index). <code>apt update</code> refreshes the indexes; only then does <code>apt install</code> know what exists.',
    'cat /etc/apt/sources.list.d/ubuntu.sources   ·   sudo apt update', 'safe',
    [('Types: deb', 'binary packages', 'deb-src for sources'),
     ('URIs', 'the mirror', 'archive.ubuntu.com'),
     ('Suites', 'noble, noble-updates, noble-security', 'release + updates'),
     ('Components', 'main universe …', 'which sections'),
     ('Signed-By', 'trusted key', 'security'),
     ('apt update', 'download indexes', 'before install'),
     ('apt policy PKG', 'which repo, which version', 'pinning')],
    dict(cmd="grep -v '^#' /etc/apt/sources.list.d/ubuntu.sources | grep -v '^$' | head -5\ngrep VERSION_CODENAME /etc/os-release\nls /var/lib/apt/lists/ | grep -c Packages | sed 's/^/downloaded package indexes: /'\napt-cache policy tmux | head -3", expect='any', note='Our build machine has never run apt update (0 indexes), so it only knows installed packages; on your PC apt update fills /var/lib/apt/lists.'),
    []
) + undo('Package managers are designed to undo: remove, purge, reinstall.', [
    ('Installed the wrong package:', '<code>sudo apt remove NAME</code> (or purge); <code>apt autoremove</code> for leftovers.'),
    ('Broke dependencies with dpkg -i:', '<code>sudo apt -f install</code> fixes or removes the half-installed package.'),
    ('Changed a packaged config file badly:', '<code>sudo apt install --reinstall -o Dpkg::Options::=--force-confask PKG</code>, or restore from /etc backup.'),
    ('Added a bad repository:', 'delete its file in /etc/apt/sources.list.d/ and its key, then apt update.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='dpkg -S /usr/bin/nosuchprog', meaning='No package owns that path.', fix='Check the path; it may come from pip, snap or a manual install.'),
    dict(cmd='dpkg -L nosuchpkg', meaning='Not installed.', fix='apt search NAME to find the right name.'),
    dict(cmd='dpkg -i /tmp/x.deb', meaning='Installing needs root.', fix='sudo dpkg -i, or better sudo apt install ./x.deb.'),
    dict(cmd='apt-get -s install tree', meaning='Unknown package: the indexes are empty (no apt update yet) or the name is wrong.', fix='sudo apt update, then try again.'),
]) + qc('What does the status <code>iU</code> in dpkg -l mean?', 'Install requested, Unpacked but not configured (usually a missing dependency).') + '''
'''
cards = cards + '</section>\n'

STEP = [('Repository', 'signed index + .deb files', 'blue'), ('apt: solve', 'report needs greet', 'amber'), ('download', '/var/cache/apt/archives', 'amber'), ('dpkg: unpack', 'files to /usr/local/bin', 'green'), ('dpkg: configure', 'run postinst, record', 'green')]
def flow(k):
    return ''.join(label_box(14, 8 + i * 34, 330, 28, [f'{a}: {b}'], c if i <= k else 'card', 7.8) for i, (a, b, c) in enumerate(STEP))
see_cmds = [['$ sudo apt install report'], ['Reading package lists...', 'The following NEW packages:', ('  greet report', 'out')], ['Get:1 … greet 1.0', 'Get:2 … report 2.0'], ['Unpacking greet (1.0) ...', 'Unpacking report (2.0) ...'], ['Setting up greet (1.0) ...', ('Setting up report (2.0) ...', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Ask.', 'Solve.', 'Download.', 'Unpack.', 'Configure.'])]
behind = [flow(k) for k in range(5)]
two = anim_two('From repository to /usr/local/bin', 'Behind the screen: apt and dpkg working together',
               'A terminal running apt install report: apt adds greet as a dependency, downloads both, unpacks and sets them up.',
               'Five boxes: repository, apt solving dependencies, download into the cache, dpkg unpacking files, dpkg configuring and recording.', see, behind,
               ['Ask.', 'Solve.', 'Get.', 'Unpack.', 'Set up.'],
               ['ask', 'solve', 'get', 'unpack', 'setup'])

def deps(k):
    o = label_box(130, 14, 100, 30, ['report 2.0'], 'blue', 8.6)
    o += label_box(130, 84, 100, 30, ['greet ≥ 1.0'], ['red', 'red', 'green'][k], 8.6) + arrow(180, 44, 180, 84)
    o += t(180, 150, ['dpkg -i report: greet missing', '→ unpacked, not configured (iU)', 'install greet → both configured (ii)'][k], 8.8, ['red', 'amber', 'green'][k], bold=True)
    return o
s1 = anim_one('Animated example', 'A dependency, missing and then satisfied',
              'What dpkg does when a needed package is not there.',
              'dpkg -i report_2.0.deb', 'report depends on greet; when greet is missing report stays unconfigured; after installing greet both are configured.', [deps(k) for k in range(3)],
              ['Missing.', 'iU.', 'Fixed.'], hid='scenario-deps')

dx = dissect('Layer by layer: what a package system keeps',
    'Each layer has a real command and output from our build machine.', [
    dict(key='status', name='The status file', sub='/var/lib/dpkg/status', why='What is installed.', how='One stanza per package.', impl='Plain text.', used='dpkg -l reads it.',
         cmd="awk -v RS= '/^Package: tmux\\n/' /var/lib/dpkg/status | grep -E '^(Package|Status|Version|Depends):' | cut -c1-70"),
    dict(key='list', name='File lists', sub='info/NAME.list', why='Clean removal.', how='Every path installed.', impl='One per package.', used='dpkg -L.',
         cmd="wc -l < /var/lib/dpkg/info/tmux.list | sed 's/^/tmux installed this many paths: /'; head -3 /var/lib/dpkg/info/tmux.list"),
    dict(key='md5', name='Checksums', sub='info/NAME.md5sums', why='Detect changes.', how='MD5 per file.', impl='dpkg --verify.', used='Security.',
         cmd="head -1 /var/lib/dpkg/info/tmux.md5sums | cut -c1-12,33-; (cd / && md5sum usr/bin/tmux | cut -c1-12)"),
    dict(key='ar', name='The .deb format', sub='ar archive', why='Simple, standard.', how='3 members.', impl='ar + tar.', used='Packaging.',
         setup=PK, cmd="cd ~/pk; ar t greet_1.0.deb; ar p greet_1.0.deb control.tar.zst 2>/dev/null | head -c 0; ar p greet_1.0.deb debian-binary"),
], hint='From the database to the file format. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>From repository to disk, and a dependency</h2>
''' + two + s1 + dx + qc('Where does dpkg remember which files a package installed?', '/var/lib/dpkg/info/NAME.list.') + '''
</section>
'''

VAR = variations('Sixteen more package questions answered on the real system and with our demo packages. All were really run on our build machine.', [
    ('Asking the system', [
        dict(title='Is a package installed?', cmd="for p in tmux nginx; do dpkg -s $p > /dev/null 2>&1 && echo \"$p: installed\" || echo \"$p: not installed\"; done", why='dpkg -s exits 0 only if installed.'),
        dict(title='Version only', cmd="dpkg-query -W -f='${Version}\\n' bash", why='Scripts and reports.'),
        dict(title='Which package gives the man page of ls?', cmd="dpkg -S /usr/share/man/man1/ls.1.gz", why='Docs belong to packages too.'),
        dict(title='Config files of a package', cmd="dpkg-query -W -f='${Conffiles}\\n' tmux | head -3; dpkg -L bash | grep '^/etc' | head -3", why='Files under /etc are kept on remove (purge deletes them).'),
        dict(title='Installed in the last days', cmd="ls -t /var/lib/dpkg/info/*.list | head -3 | xargs -n1 basename | sed 's/.list$//'", why='Newest file lists = most recent installs.'),
        dict(title='Packages by section', cmd="dpkg-query -W -f='${Section}\\n' | sort | uniq -c | sort -rn | head -3", why='libs, utils, python…'),
        dict(title='What needs libc6 (count)', cmd="apt-cache rdepends --installed libc6 | tail -n +3 | wc -l", why='Almost everything: the base library.'),
        dict(title='Manually installed vs automatic', cmd="echo \"manual: $(apt-mark showmanual | wc -l), automatic: $(apt-mark showauto | wc -l)\"", why='Automatic ones came in as dependencies (autoremove candidates later).'),
    ]),
    ('Our demo packages', [
        dict(title='Install both in the right order', setup=PK, cmd="cd ~/pk; pdpkg -i greet_1.0.deb report_2.0.deb 2>&1 | grep -c 'Setting up'; ~/pk/root/usr/local/bin/report", why='Given both files, dpkg orders them itself.'),
        dict(title='Who owns the installed file?', setup=PK, cmd="cd ~/pk; pdpkg -i greet_1.0.deb > /dev/null; pdpkg -S /usr/local/bin/greet", why='The private database answers like the real one.'),
        dict(title='Compare versions the dpkg way', cmd="for p in '1.0 1.1' '1.0~rc1 1.0' '2:1.0 3.0'; do set -- $p; dpkg --compare-versions $1 lt $2 && echo \"$1 < $2\" || echo \"$1 >= $2\"; done", why='~ sorts first; an epoch (2:) beats everything without one.'),
        dict(title='Downgrade needs a deliberate step', setup=PK, cmd="cd ~/pk; pdpkg -i greet_1.1.deb > /dev/null; pdpkg -i greet_1.0.deb 2>&1 | grep -i -E 'downgrad' | head -1; ~/pk/root/usr/local/bin/greet", why='dpkg warns but allows it; apt needs an explicit version.'),
        dict(title='Purge vs remove', setup=PK, cmd="cd ~/pk; pdpkg -i greet_1.0.deb > /dev/null; pdpkg -r greet > /dev/null; pdpkg -l greet 2>/dev/null | tail -1 | cut -c1-3; pdpkg -P greet > /dev/null; pdpkg -l greet 2>&1 | tail -1 | cut -c1-40", expect='any', why='greet has no config files, so -r already removed it completely and -P has nothing left to do. Packages with config files in /etc stay as rc after -r until you purge.'),
        dict(title='Extract without installing', setup=PK, cmd="cd ~/pk; mkdir -p peek; dpkg-deb -x report_2.0.deb peek; find peek -type f | sed 's|^peek||'", why='See exactly what would be written.'),
    ]),
    ('Repositories', [
        dict(title='Suites and components', cmd="awk '/^Suites:/{print \"suites:\", $2, $3, $4} /^Components:/{print \"components:\", $2, $3, $4, $5}' /etc/apt/sources.list.d/ubuntu.sources | sort -u", why='Release, updates, backports; supported and community sections.'),
        dict(title='Trusted keyrings', cmd="ls /usr/share/keyrings/ | grep -c gpg | sed 's/^/keyring files: /'; ls /usr/share/keyrings/ | grep ubuntu | head -2", why='Signed-By points to one of these.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Packages at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['apt install', 'servers'], 'blue', 8.6), '1. Building servers',
              'Every server build (by hand, Ansible or a Dockerfile) is mostly “install these packages, change these configs”.', ['Base image', '*apt/dnf install', 'ready']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['updates', 'security'], 'red', 8.6), '2. Security updates',
    'A vulnerability in OpenSSL is fixed once in the libssl package; every program using it is fixed by one upgrade (Lesson 19.3).', ['CVE', '*apt upgrade', 'patched']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['.deb', 'vendors'], 'amber', 8.6), '3. Vendor software',
    'Docker, PostgreSQL, Grafana and Microsoft ship their own signed repositories so updates come through apt/dnf too.', ['Add repo', '*key + list', 'apt install']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['dpkg -S', 'support'], 'green', 8.6), '4. Troubleshooting',
    '“Which package broke this file?” dpkg -S and dpkg --verify answer it; reinstalling the package repairs it.', ['Broken file', '*dpkg -S', 'reinstall']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['build', 'internal'], 'violet', 8.6), '5. Internal packages',
    'Companies package their own tools as .deb/.rpm and host a private repository, so deployment is apt install company-tool.', ['Code', '*dpkg-deb / rpmbuild', 'private repo']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Who owns this file?', scenario='Where from?', cmd="dpkg -S /usr/bin/tmux", explain='dpkg -S.'),
    dict(level='b', title='Installed version', scenario='Bug reports.', cmd="dpkg-query -W tmux", explain='dpkg-query -W.'),
    dict(level='i', title='Biggest package', scenario='Disk.', cmd="dpkg-query -W -f='${Installed-Size} ${Package}\\n' | sort -rn | head -1 | awk '{printf \"%.0f MB %s\\n\", $1/1024, $2}'", explain='Installed-Size in KB.'),
    dict(level='i', title='Count installed packages', scenario='Inventory.', cmd="dpkg -l | grep -c '^ii'", explain='ii = installed.'),
    dict(level='a', title='Verify a package’s program files', scenario='Integrity.', cmd="dpkg --verify tmux | grep -v -E '/usr/share/(doc|man)' | grep -q . && echo 'tmux changed!' || echo 'tmux program files OK'", explain='Checksums from the package (docs ignored here).'),
], extra=build_up('a package from nothing', 'Riya packages a one-line tool and installs it, step by step.', PK, [
    ("cd ~/pk; mkdir -p uptime-mp_1.0/usr/local/bin; printf '#!/bin/sh\\nuptime -p\\n' > uptime-mp_1.0/usr/local/bin/uptime-mp; chmod 755 uptime-mp_1.0/usr/local/bin/uptime-mp; find uptime-mp_1.0 -type f", '1. The files, in their final paths.'),
    ("cd ~/pk; mkdir -p uptime-mp_1.0/DEBIAN; printf 'Package: uptime-mp\\nVersion: 1.0\\nArchitecture: all\\nMaintainer: Riya <riya@example.com>\\nDescription: friendly uptime\\n' > uptime-mp_1.0/DEBIAN/control; cat uptime-mp_1.0/DEBIAN/control | head -2", '2. The control file (metadata).'),
    ("cd ~/pk; dpkg-deb --build --root-owner-group uptime-mp_1.0 > /dev/null && dpkg-deb -I uptime-mp_1.0.deb | grep -E 'Package|Version'", '3. Build and inspect.'),
    ("cd ~/pk; pdpkg -i uptime-mp_1.0.deb > /dev/null && pdpkg -l uptime-mp | tail -1 | awk '{print $1, $2, $3}'; ~/pk/root/usr/local/bin/uptime-mp | sed -E 's/[0-9]+/N/g'", '4. Install and run.'),
], cumulative=True)) + VAR + which('Choosing the right tool.', [
    ('Install from repositories', 'apt / dnf', 'Dependencies, updates.', 'Downloading installers by hand.'),
    ('A local .deb with dependencies', 'apt install ./f.deb', 'Fetches what is missing.', 'dpkg -i alone.'),
    ('Inspect before installing', 'dpkg-deb -I / -c', 'See scripts and files.', 'Installing blind.'),
    ('Find the owner of a file', 'dpkg -S / rpm -qf', 'Exact.', 'Guessing.'),
    ('Newest desktop app', 'flatpak / snap', 'Vendor builds.', 'Random PPAs.'),
    ('Your own tool for many servers', 'build a .deb + private repo', 'Clean installs, updates.', 'scp + chmod on each server.'),
]) + keys('Handy forms.', [
    ('dpkg -S FILE', 'owner', 'where from'),
    ('dpkg -L PKG', 'files', 'what'),
    ('dpkg -l | grep PKG', 'status', 'installed?'),
    ('apt-cache depends PKG', 'needs', 'deps'),
    ('dpkg-deb -I / -c', 'inspect .deb', 'before install'),
    ('apt install ./f.deb', 'local + deps', 'normal'),
]) + scriptit('whatpkg.sh', 'Explain where commands come from: for each command name, find its real path, the package that owns it, the package version and how many other installed packages depend on that package.',
'''[ $# -eq 0 ] && set -- ls tmux awk python3
for c in "$@"; do
  p=$(command -v "$c") || { printf '%-8s not found\\n' "$c"; continue; }
  real=$(readlink -f "$p")
  owner=$(dpkg -S "$real" 2>/dev/null | head -1 | cut -d: -f1)
  if [ -n "$owner" ]; then
    v=$(dpkg-query -W -f='${Version}' "$owner")
    n=$(apt-cache rdepends --installed "$owner" 2>/dev/null | tail -n +3 | wc -l)
    printf '%-8s %-28s %-14s %-18s needed by %s\\n' "$c" "$real" "$owner" "$v" "$n"
  else
    printf '%-8s %-28s (not from a package)\\n' "$c" "$real"
  fi
done''',
'<p>Run without arguments, so it explains ls, tmux, awk and python3.</p>', expect='any') + puzzle_answer('<b>Both colleagues are right.</b> A dependency is another package this one needs; <code>report</code> needs <code>greet</code> (version 1.0 or newer). <code>dpkg -i</code> only installs the file you give it, so report stayed “unpacked, not configured”. <code>sudo apt install ./report_2.0.deb</code> would read the repositories and install greet first (here greet is our own demo package, so it would have to be in a repository). And a .deb from a chat message runs its install scripts as root: install only from trusted repositories or sources, and inspect unknown packages with <code>dpkg-deb -I</code> and <code>-c</code> first.') + qc('Which command shows the files a .deb would install, without installing it?', 'dpkg-deb -c FILE.deb.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/pk', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../../01-start-here/">Module 1</a> (distributions) and <a href="../../09-permissions/">Module 9</a> (why installing needs sudo).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
