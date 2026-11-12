import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='14-packages-and-archives', lesson='01-packages-and-repositories-how-software', n='14.1',
    module_label='Module 14 · Software packages and archives',
    title='Packages and repositories: how software is installed on Linux',
    desc='How Linux installs software: packages (files + metadata + scripts), repositories and signed indexes, low-level (dpkg, rpm) vs high-level (apt, dnf) package managers, dependencies and version strings, deb vs rpm families and snap, flatpak, AppImage; asking the package database (dpkg -S, -L, -l, dpkg-query, apt-cache depends), inspecting and building a real .deb with dpkg-deb, installing, upgrading and removing it, a real dependency error; real outputs and 30+ examples.',
    og_desc='Packages, repositories and dependencies explained with real runs: dpkg -S, -L, building and installing a real .deb and a dependency error.',
    minutes=40, level='Beginner → Advanced',
    lead='Why sudo apt install works in two seconds: packages, repositories, dependencies and the package database, and a real .deb package you build, inspect, install and remove yourself.',
    chips=['Build your own .deb', 'Dependency error animated', 'Who owns this file?', 'Practice lab with checker', 'Real outputs'],
)

MAIN = """# Make a package folder: metadata + files in their final paths
mkdir -p hello_1.0/DEBIAN hello_1.0/usr/local/bin
cat > hello_1.0/DEBIAN/control <<'EOF'
Package: hello
Version: 1.0
Architecture: all
Maintainer: You <you@example.com>
Description: says hello
EOF
printf '#!/bin/sh\\necho hello\\n' > hello_1.0/usr/local/bin/hello
chmod 755 hello_1.0/usr/local/bin/hello
find hello_1.0 -type f | sort
grep -E '^(Package|Version)' hello_1.0/DEBIAN/control
"""

RUN = dict(
    heading='The shape of a package',
    intro='<p>Create the folder that dpkg-deb would turn into a .deb: a DEBIAN/control file and the files in their final paths. (Building and installing need dpkg, shown above with real runs.)</p>',
    code=MAIN,
    anno=[('DEBIAN/control', 'The metadata: name, version, dependencies.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Where will the program be installed?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which is newer for dpkg, 1.0~rc1 or 1.0?',
             code="printf '%s\\n' 1.0 1.0~rc1 | sort -V\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> a control file needs “Package:” with a colon. Fix it.',
             code="printf 'Package hello\\nVersion: 1.0\\n' > control\ngrep -c '^Package:' control\n", expect='any'),
        dict(label='4 · Your turn', hint='Add a dependency line to a control file and print it.',
             code="printf 'Package: report\\nVersion: 2.0\\nDepends: hello (>= 1.0)\\n' > control\ngrep Depends control\n"),
        dict(label='5 · Challenge', hint='Parse name and version from a package file name.',
             code="f=report_2.0_all.deb\nn=${f%%_*}; rest=${f#*_}; v=${rest%%_*}\necho \"name=$n version=$v\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: real apt',
    intro='<p>Our build machine has no repository indexes (no network), so these are <b>typical</b> outputs from a normal Ubuntu 24.04 machine unless marked recorded.</p>',
    items=[
        dict(title='1 · Refresh the indexes', cmd='sudo apt update', output='Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease\nGet:2 http://security.ubuntu.com/ubuntu noble-security InRelease [126 kB]\n…\nReading package lists... Done\n12 packages can be upgraded. Run \'apt list --upgradable\' to see them.', note='Typical.'),
        dict(title='2 · Install a local .deb with its dependencies', cmd='sudo apt install ./report_2.0.deb', output='Note, selecting \'report\' instead of \'./report_2.0.deb\'\nThe following NEW packages will be installed:\n  greet report', note='Typical (if greet is in a repository).'),
        dict(title='3 · Where does a package come from?', cmd='apt policy tmux', output='tmux:\n  Installed: 3.4-1ubuntu0.2\n  Candidate: 3.4-1ubuntu0.2\n  Version table:\n *** 3.4-1ubuntu0.2 500\n        500 http://archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages', note='Typical.'),
        dict(title='4 · Versions here', cmd='dpkg --version | head -1; apt --version', output=pc('dpkg --version | head -1; apt --version'), note='Recorded.'),
    ],
)

TRACE = dict(
    heading='Reading a control file, line by line',
    intro='<p>Step through: extract fields from package metadata.</p>',
    code='''ctl=$'Package: report\\nVersion: 2.0\\nDepends: greet (>= 1.0)'
name=$(echo "$ctl" | awk -F': ' '/^Package/{print $2}')
ver=$(echo "$ctl" | awk -F': ' '/^Version/{print $2}')
dep=$(echo "$ctl" | awk -F': ' '/^Depends/{print $2}')
echo "$name $ver needs: $dep"
''',
    notes={2: 'Field after "Package: ".', 4: 'The dependency with its version rule.'},
)

WORKED_INTRO = 'Three package questions from real jobs, answered with the package database.'
EXAMPLES = [
    dict(level='b', tag='Support', title='Which package does a command come from?',
         problem='<p>A user asks where <code>ls</code> and <code>tar</code> come from and which versions are installed.</p>',
         inp='command names', approach=['command -v.', 'dpkg -S on the real path.'],
         code='''for c in ls tar; do
  p=$(readlink -f "$(command -v $c)")
  echo "$c -> $p -> $(dpkg -S "$p" 2>/dev/null | cut -d: -f1)"
done
''', notes={2: 'Resolve symlinks first.'}, tryit='Add the version with dpkg-query -W.'),
    dict(level='i', tag='Ops', title='Packages taking the most disk',
         problem='<p>List the five largest installed packages in MB.</p>',
         inp='the dpkg database', approach=['Installed-Size field.', 'sort -rn.'],
         code='''dpkg-query -W -f='${Installed-Size}\\t${Package}\\n' | sort -rn | head -5 | awk '{printf "%6.0f MB  %s\\n", $1/1024, $2}'
''', notes={1: 'Installed-Size is in KB.'}, tryit='Count packages larger than 50 MB.'),
    dict(level='a', tag='Security', title='Programs not owned by any package',
         problem='<p>Find executables in /usr/local/bin and /usr/bin that no package owns (installed by hand).</p>',
         inp='bin folders', approach=['dpkg -S on each.'],
         code='''for f in /usr/local/bin/* /usr/bin/[a-c]*; do
  [ -f "$f" ] || continue
  dpkg -S "$(readlink -f "$f")" > /dev/null 2>&1 || echo "unowned: $f"
done | head -5
''', notes={3: 'No owner = installed outside the package manager.'}, tryit='Check /opt as well.'),
]

QUIZ = mix([
    dict(q='A package contains…', options=['only a program', 'files + metadata + scripts', 'a repository', 'a kernel'], answer=1, why='And dependencies in the metadata.'),
    dict(q='Which tool resolves dependencies from repositories on Ubuntu?', options=['dpkg', 'apt', 'tar', 'make'], answer=1, why='apt.'),
    dict(q='Which package owns /usr/bin/ls?', options=['dpkg -L ls', 'dpkg -S /usr/bin/ls', 'apt show ls', 'which ls'], answer=1, why='-S searches.'),
    dict(q='List the files installed by tmux:', options=['dpkg -S tmux', 'dpkg -L tmux', 'apt search tmux', 'ls tmux'], answer=1, why='-L lists.'),
    dict(q='Red Hat family package format:', options=['.deb', '.rpm', '.apk', '.msi'], answer=1, why='rpm.'),
    dict(q='Repository list on Ubuntu 24.04:', options=['/etc/yum.repos.d', '/etc/apt/sources.list.d/', '/var/lib/dpkg', '/usr/share/repos'], answer=1, why='deb822 .sources files.'),
    dict(q='dpkg status iU means…', options=['installed, OK', 'unpacked, not configured', 'removed', 'held'], answer=1, why='Usually a missing dependency.'),
    dict(q='Why is installing random .deb files risky?', options=['they are big', 'their scripts run as root', 'they are slow', 'they need Wi-Fi'], answer=1, why='Maintainer scripts.'),
])

REVISION = [
    'Package = files + metadata (name, version, depends) + scripts; repository = signed online store; package manager = installs and records.',
    'Low-level dpkg/rpm (one file, no downloads); high-level apt/dnf (repositories, dependency solving).',
    'Families: .deb (Debian, Ubuntu), .rpm (RHEL, Fedora, SUSE), plus snap, flatpak, AppImage.',
    'Ask: dpkg -S FILE, dpkg -L PKG, dpkg -l, dpkg-query -W -f, apt-cache depends/rdepends, dpkg --verify.',
    'Inspect: dpkg-deb -I / -c / -x; build: DEBIAN/control + files, dpkg-deb --build.',
    'apt update reads signed indexes into /var/lib/apt/lists; installed DB in /var/lib/dpkg/status and info/*.list.',
]

FAQ = [
    ('What is a package in Linux?', 'An archive with a program’s files plus metadata (version, dependencies) and install scripts, installed by a package manager.'),
    ('What is a repository?', 'A signed online collection of packages that apt or dnf downloads from.'),
    ('What is the difference between apt and dpkg?', 'dpkg installs a local package file; apt finds packages in repositories, resolves dependencies and calls dpkg.'),
    ('How do I find which package a file belongs to?', 'dpkg -S /path/to/file (rpm -qf on Red Hat systems).'),
    ('How do I list files in an installed package?', 'dpkg -L name (rpm -ql name).'),
    ('What is a dependency?', 'Another package a package needs to work, often a shared library.'),
    ('How do I look inside a .deb before installing?', 'dpkg-deb -I file.deb for metadata and dpkg-deb -c file.deb for files.'),
]

PRACTICE_INTRO = 'Small package-database tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Owner', stmt='Which package owns /usr/bin/tmux?', inp='a path', code="dpkg -S /usr/bin/tmux\n", explain='tmux.'),
    dict(level='easy', title='Version', stmt='Print the installed version of bash.', inp='a name', code="dpkg-query -W -f='${Version}\\n' bash\n", explain='5.2.21-2ubuntu4.'),
    dict(level='easy', title='Installed?', stmt='Print yes if tmux is installed.', inp='a name', code="dpkg -s tmux > /dev/null 2>&1 && echo yes\n", explain='yes.'),
    dict(level='medium', title='Count', stmt='How many packages are installed?', inp='nothing', code="dpkg -l | grep -c '^ii'\n", explain='1044 here.'),
    dict(level='medium', title='Files', stmt='How many paths did tmux install?', inp='a name', code="dpkg -L tmux | wc -l\n", explain='21.'),
    dict(level='medium', title='First dependency', stmt='Print the first dependency of tmux.', inp='a name', code="apt-cache depends tmux | awk '/Depends/{print $2; exit}'\n", explain='libc6.'),
    dict(level='business', title='Compare versions', stmt='Is 1.10 newer than 1.9 for dpkg?', inp='versions', code="dpkg --compare-versions 1.10 gt 1.9 && echo newer\n", explain='newer (not text order).'),
    dict(level='business', title='Sections', stmt='The most common package section.', inp='nothing', code="dpkg-query -W -f='${Section}\\n' | sort | uniq -c | sort -rn | head -1\n", explain='libs.'),
]

SCN_INTRO = 'Interview questions about packages, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How is software installed on Linux?”', 'Very common.', 'explain?',
        '''<ul>
          <li>From repositories with a package manager: apt (Ubuntu) or dnf (RHEL).</li>
          <li>Packages carry metadata and dependencies.</li>
          <li>Also snap/flatpak or building from source.</li>
        </ul>''', '“download an .exe”.') +
    scn('Service company', 'Junior', '“dpkg -i fails with dependency problems”', 'A vendor .deb.', 'fix?',
        '''<ol>
          <li>sudo apt -f install, or install with sudo apt install ./file.deb.</li>
          <li>apt fetches the missing dependencies.</li>
          <li>Check the vendor supports your release.</li>
        </ol>''', 'forcing with --force-depends.') +
    scn('Security team', 'Mid-level', 'A binary in /usr/bin looks wrong', 'Possible tampering.', 'how to check?',
        '''<ul>
          <li>dpkg -S FILE: which package.</li>
          <li>dpkg --verify PKG (or debsums): checksum mismatch?</li>
          <li>Reinstall from the repository; investigate how it changed.</li>
        </ul>''', 'just deleting it.') +
    scn('Platform', 'Senior', 'Distribute an internal tool to 500 servers', 'Updates monthly.', 'how?',
        '''<ul>
          <li>Build a .deb/.rpm in CI; host a private signed repository.</li>
          <li>apt install company-tool; updates with normal upgrades.</li>
          <li>Pin versions per environment.</li>
        </ul>''', 'scp a binary to every server.')
) + interview([
    ('Where is the dpkg database?', '/var/lib/dpkg/status and info/.'),
    ('What does apt update do?', 'Downloads repository indexes.'),
    ('What is Signed-By?', 'The key that must sign a repository’s index.'),
    ('What is an epoch in a version?', 'A prefix (N:) that overrides normal version ordering.'),
    ('What is in a .deb?', 'debian-binary, control.tar, data.tar in an ar archive.'),
    ('How to list package files of a .deb?', 'dpkg-deb -c.'),
    ('rpm -qf equivalent on Ubuntu?', 'dpkg -S.'),
], [
    ('RHCSA (EX200)', 'Install and update software packages from repositories.'),
    ('LFCS', 'Manage software with package managers.'),
    ('CompTIA Linux+', 'Package management concepts.'),
]) + distro('Same ideas, different tools per family.', [
    ('Install', 'apt install', 'dnf install', 'brew install', 'winget install'),
    ('Owner of a file', 'dpkg -S', 'rpm -qf', 'pkgutil --file-info', '-'),
    ('Files of a package', 'dpkg -L', 'rpm -ql', 'brew list PKG', '-'),
    ('Repo config', '/etc/apt/sources.list.d', '/etc/yum.repos.d', 'brew tap', 'winget source'),
    ('Package file', '.deb', '.rpm', '.pkg / bottle', '.msi / .msix'),
]) + teaser('14.2', 'Riya now knows what a package is. Next: the everyday apt and dpkg commands on Ubuntu and Debian: update, upgrade, install, remove, purge, autoremove, search, show, hold and the logs that record it all.')

CHEATSHEET = cheatsheet('Packages', [
    ('Concepts', [('package', 'files + metadata'), ('repository', 'signed store'), ('dependency', 'needed package'), ('dpkg / apt', 'low / high level')]),
    ('Ask', [('dpkg -S FILE', 'owner'), ('dpkg -L PKG', 'files'), ('dpkg -l PKG', 'status'), ('apt-cache depends', 'needs')]),
    ('.deb files', [('dpkg-deb -I', 'metadata'), ('dpkg-deb -c', 'contents'), ('dpkg-deb -x', 'extract'), ('dpkg-deb --build', 'make')]),
    ('Install / remove', [('apt install ./f.deb', 'with deps'), ('dpkg -i', 'one file'), ('dpkg -r / -P', 'remove / purge'), ('apt -f install', 'fix')]),
])

MINDMAP = mindmap('Packages', [
    ('Package', 'blue', ['files', 'metadata', 'scripts']),
    ('Repository', 'green', ['signed index', 'mirrors', 'components']),
    ('Tools', 'amber', ['dpkg rpm', 'apt dnf', 'snap flatpak']),
    ('Deps', 'red', ['libraries', 'versions', 'iU errors']),
    ('Ask', 'violet', ['dpkg -S', 'dpkg -L', 'depends']),
    ('Build', 'acc', ['DEBIAN/control', 'dpkg-deb', 'install']),
])

LAB = lab('build a package', 'Build the lab, write <code>~/lab141/build.sh</code> for the four tasks, then run the checker.',
    setup='''mkdir -p ~/lab141 && cd ~/lab141 && rm -rf build.sh *.deb clock_1.0 owner.txt''',
    tasks=['Create the folder <code>clock_1.0</code> with a program <code>usr/local/bin/clock</code> (executable) that prints the time with <code>date +%T</code>.',
           'Write <code>clock_1.0/DEBIAN/control</code> with Package clock, Version 1.0, Architecture all, a Maintainer and a Description.',
           'Build <code>clock_1.0.deb</code> with dpkg-deb (use --root-owner-group).',
           'Write the name of the package that owns <code>/usr/bin/tar</code> on this system into <code>owner.txt</code>.'],
    solution='''cat > build.sh <<'EOF'
cd ~/lab141
mkdir -p clock_1.0/DEBIAN clock_1.0/usr/local/bin
printf '#!/bin/sh\\ndate +%%T\\n' > clock_1.0/usr/local/bin/clock; chmod 755 clock_1.0/usr/local/bin/clock
printf 'Package: clock\\nVersion: 1.0\\nArchitecture: all\\nMaintainer: Me <me@example.com>\\nDescription: prints the time\\n' > clock_1.0/DEBIAN/control
dpkg-deb --build --root-owner-group clock_1.0 > /dev/null
dpkg -S /usr/bin/tar | cut -d: -f1 > owner.txt
EOF''',
    check='''cd ~/lab141; rm -rf clock_1.0 clock_1.0.deb owner.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f build.sh ] && bash build.sh 2>/dev/null
ok "1 program" '[ -x clock_1.0/usr/local/bin/clock ] && clock_1.0/usr/local/bin/clock | grep -qE "^[0-9]{2}:[0-9]{2}:[0-9]{2}$"'
ok "2 control" 'grep -qx "Package: clock" clock_1.0/DEBIAN/control 2>/dev/null && grep -qx "Version: 1.0" clock_1.0/DEBIAN/control'
ok "3 deb"     '[ -f clock_1.0.deb ] && dpkg-deb -c clock_1.0.deb | grep -q "usr/local/bin/clock" && dpkg-deb -f clock_1.0.deb Package | grep -qx clock'
ok "4 owner"   '[ "$(cat owner.txt 2>/dev/null)" = tar ]' ''')
