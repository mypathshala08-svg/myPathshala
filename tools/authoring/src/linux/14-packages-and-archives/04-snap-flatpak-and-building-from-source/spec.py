import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

_s = open(os.path.join(HERE, '_body.py')).read(); _i = _s.index('SRC = r"""') + 10
SRC = _s[_i:_s.index('"""', _i)]

META = dict(
    module='14-packages-and-archives', lesson='04-snap-flatpak-and-building-from-source', n='14.4',
    module_label='Module 14 · Software packages and archives',
    title='snap, flatpak and building from source',
    desc='Installing software outside apt and dnf: snap (channels, revisions, classic confinement, refresh, revert), flatpak (Flathub, runtimes, --user, sandbox), AppImage, and a complete real build from source: sha256sum -c, tar -xzf, ./configure --prefix, make -j, make install, DESTDIR staging and make uninstall, with 30+ real examples.',
    og_desc='snap, flatpak and a real ./configure, make, make install build with --prefix, DESTDIR and clean uninstall.',
    minutes=35, level='Beginner → Advanced',
    lead='When the repository is not enough: bundled sandboxed apps with snap and flatpak, and building a program from source safely into a prefix you control.',
    chips=['Real build from source', 'snap revert animated', 'Five ways compared', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# A Makefile-like dependency check in Bash: rebuild only what is older than its source
declare -A built=( [greet.o]=100 [util.o]=300 [greet]=310 )
declare -A src=( [greet.o]=200 [util.o]=150 )
for obj in greet.o util.o; do
  if (( src[$obj] > built[$obj] )); then echo "$obj: source newer -> recompile"; built[$obj]=400
  else echo "$obj: up to date"; fi
done
(( built[greet.o] > built[greet] || built[util.o] > built[greet] )) && echo "greet: relink" || echo "greet: up to date"
"""

RUN = dict(
    heading='How make decides what to rebuild',
    intro='<p>The browser has no compiler; this simulates make’s rule: a target is rebuilt when any source is newer (numbers stand for modification times).</p>',
    code=MAIN,
    anno=[('src[$obj] > built[$obj]', 'Source newer than the object: rebuild.'), ('relink', 'The program depends on the objects.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which files are rebuilt?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which prefix wins?',
             code="prefix=/usr/local\nfor a in --prefix=$HOME/.local --greeting=Hi; do case $a in --prefix=*) prefix=${a#*=};; esac; done\necho \"$prefix\"\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> the check compares the wrong way round. Fix the operator.',
             code="src=200; obj=300\nif (( src < obj )); then echo rebuild; else echo 'up to date'; fi\n"),
        dict(label='4 · Your turn', hint='Pick a method for each need.',
             code="for need in server desktop-app source-only; do case $need in server) echo \"$need: apt/dnf\";; desktop-app) echo \"$need: flatpak\";; *) echo \"$need: ./configure --prefix\";; esac; done\n"),
        dict(label='5 · Challenge', hint='Parse snap channel track/risk.',
             code="ch=5.21/stable; echo \"track=${ch%/*} risk=${ch#*/}\"\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC (Ubuntu or Fedora)',
    intro='<p>Typical outputs; snap and flatpak are not on our build machine.</p>',
    items=[
        dict(title='1 · A classic snap', cmd='sudo snap install code --classic\nsnap list code', output='code 6f17636e from Visual Studio Code (vscode✓) installed\nName  Version   Rev  Tracking       Publisher  Notes\ncode  6f17636e  174  latest/stable  vscode✓    classic', note='Typical.'),
        dict(title='2 · Revert a snap', cmd='sudo snap revert firefox', output='firefox reverted to 131.0.3-1', note='Typical.'),
        dict(title='3 · Flatpak from Flathub', cmd='flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo\nflatpak install -y flathub org.gimp.GIMP', output='Installing app/org.gimp.GIMP/x86_64/stable\n…\nInstallation complete.', note='Typical.'),
        dict(title='4 · Build tools', cmd='sudo apt install build-essential   # Ubuntu\nsudo dnf group install "Development Tools"   # Fedora/Rocky', output='…\ngcc is already the newest version', note='Typical.'),
    ],
)

TRACE = dict(
    heading='configure’s option loop, line by line',
    intro='<p>How ./configure reads --prefix and --greeting.</p>',
    code='''prefix=/usr/local; greeting=Hello
for a in --prefix=/opt/greet --greeting=Hi; do
  case $a in
    --prefix=*) prefix=${a#*=} ;;
    --greeting=*) greeting=${a#*=} ;;
  esac
done
echo "prefix=$prefix greeting=$greeting"
''',
    notes={1: 'Defaults first.', 4: '${a#*=} drops everything up to =.'},
)

WORKED_INTRO = 'Three real tasks around source builds.'
EXAMPLES = [
    dict(level='b', tag='Dev', title='Verify before building',
         problem='<p>Check a download against its published checksum and stop if it does not match.</p>',
         inp='a file and its sum', approach=['sha256sum -c.'],
         code='''echo 'release notes' > app.txt; sha256sum app.txt > SUMS
sha256sum -c SUMS && echo 'safe to build'
echo tamper >> app.txt; sha256sum -c SUMS 2>/dev/null || echo 'STOP: checksum mismatch'
''', notes={2: 'OK.', 3: 'FAILED → stop.'}, tryit='Use sha512sum.'),
    dict(level='i', tag='Ops', title='Per-program prefixes',
         problem='<p>Install two versions side by side and switch with a symlink.</p>',
         inp='nothing', approach=['/opt/app/VERSION + current link.'],
         code='''mkdir -p opt/app/1.2/bin opt/app/1.3/bin
echo 'echo v1.2' > opt/app/1.2/bin/app; echo 'echo v1.3' > opt/app/1.3/bin/app
ln -sfn 1.3 opt/app/current; sh opt/app/current/bin/app
ln -sfn 1.2 opt/app/current; sh opt/app/current/bin/app
''', notes={3: 'Switch = move one link.'}, tryit='Remove 1.2 completely.'),
    dict(level='a', tag='Packaging', title='Manifest from a staging tree',
         problem='<p>List the files an install would create, from a DESTDIR tree.</p>',
         inp='a staging tree', approach=['find relative paths.'],
         code='''mkdir -p stage/usr/local/bin stage/usr/local/share/doc/app
touch stage/usr/local/bin/app stage/usr/local/share/doc/app/README
(cd stage && find . -type f | sed 's|^\\.||' | sort)
''', notes={3: 'Exactly what make install would write.'}, tryit='Count them.'),
]

QUIZ = mix([
    dict(q='Which installs a snap that needs full system access?', options=['snap install X --full', 'snap install X --classic', 'snap install X --root', 'snap add X'], answer=1, why='Classic confinement.'),
    dict(q='Go back to the previous snap revision:', options=['snap undo', 'snap revert X', 'snap downgrade X', 'snap back'], answer=1, why='revert.'),
    dict(q='Flatpak app IDs look like…', options=['gimp_2.10', 'org.gimp.GIMP', 'gimp-2.10.rpm', '/snap/gimp'], answer=1, why='Reverse DNS.'),
    dict(q='Install a flatpak without root:', options=['--user', '--noroot', '--home', 'sudo -u'], answer=0, why='--user.'),
    dict(q='The default ./configure prefix is…', options=['/usr', '/usr/local', '/opt', '~/.local'], answer=1, why='FHS.'),
    dict(q='DESTDIR is used to…', options=['choose the compiler', 'stage the install in another root', 'download sources', 'uninstall'], answer=1, why='Staging.'),
    dict(q='make -j$(nproc) …', options=['builds in parallel', 'installs', 'cleans', 'checks'], answer=0, why='Jobs.'),
    dict(q='Before building a tarball always…', options=['run it as root', 'verify the checksum', 'delete /usr/local', 'reboot'], answer=1, why='sha256sum -c.'),
])

REVISION = [
    'Order of preference: distro package, then flatpak or snap, then AppImage, then source.',
    'snap: install, list, refresh, revert, remove; channels track/risk; --classic for full access.',
    'flatpak: remote-add flathub, install ID, run ID, list --app, update, uninstall --unused; --user needs no root.',
    'Source: verify (sha256sum -c), unpack (tar -xzf), ./configure --prefix, make -j, make install.',
    'Use /usr/local or a prefix per program, never /usr; DESTDIR stages files; keep the tree for make uninstall.',
    'Missing headers mean a missing -dev (Debian) or -devel (RHEL) package.',
]

FAQ = [
    ('What is the difference between snap and flatpak?', 'Both bundle apps with libraries and sandbox them; snap is Canonical’s (desktop, server, CLI), flatpak is community-led and focused on desktop apps from Flathub.'),
    ('Is snap or flatpak slower?', 'First start can be slower (snaps mount a compressed image); afterwards differences are small.'),
    ('How do I install software from a .tar.gz?', 'Verify it, extract with tar -xzf, read README/INSTALL, then usually ./configure, make and sudo make install.'),
    ('How do I uninstall something installed with make install?', 'Run make uninstall in the same source tree if offered, or delete the files (or the whole prefix if you used a separate one).'),
    ('Where should source-built software go?', 'Under /usr/local (system-wide) or $HOME/.local (just you), never /usr.'),
    ('What is an AppImage?', 'A single executable file containing an app; chmod +x and run, no installation.'),
    ('Why does configure say a library is missing when it is installed?', 'The development package (headers, .pc file) is missing: install libNAME-dev or NAME-devel.'),
]

PRACTICE_INTRO = 'Small tasks around builds and bundles. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Cores', stmt='Print how many CPU cores make -j could use.', inp='nothing', code="nproc\n", explain='nproc.'),
    dict(level='easy', title='Classic', stmt='Print the snap install command for VS Code.', inp='nothing', code="echo 'sudo snap install code --classic'\n", explain='--classic.'),
    dict(level='easy', title='Prefix', stmt='Print the configure command that installs into ~/.local.', inp='nothing', code="echo './configure --prefix=$HOME/.local'\n", explain='Single quotes keep $HOME literal.'),
    dict(level='medium', title='Track and risk', stmt='Split latest/stable into its parts.', inp='a channel', code="c=latest/stable; echo ${c%/*} ${c#*/}\n", explain='latest stable.'),
    dict(level='medium', title='Tarball name', stmt='Get greet-1.2 from greet-1.2.tar.gz.', inp='a name', code="basename greet-1.2.tar.gz .tar.gz\n", explain='basename strips a suffix.'),
    dict(level='medium', title='Checksum', stmt='Verify a file you just summed.', inp='nothing', code="echo hi > f; sha256sum f > S; sha256sum -c S\n", explain='f: OK.'),
    dict(level='business', title='Version dir', stmt='Make /opt-style dirs for 1.2 and 1.3 and point current at 1.3.', inp='nothing', code="mkdir -p app/1.2 app/1.3; ln -sfn 1.3 app/current; readlink app/current\n", explain='1.3.'),
    dict(level='business', title='Flatpak publisher', stmt='Get gimp.org from org.gimp.GIMP.', inp='an ID', code="echo org.gimp.GIMP | awk -F. '{print $2\".\"$1}'\n", explain='gimp.org.'),
]

SCN_INTRO = 'Interview questions about installing software outside the repositories.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you install software from source?”', 'Classic question.', 'steps?',
        '''<ol>
          <li>Verify the checksum, extract with tar.</li>
          <li>./configure (with --prefix), make, sudo make install.</li>
          <li>Install missing -dev packages if configure fails.</li>
        </ol>''', 'skipping verification.') +
    scn('Service company', 'Junior', 'make install: Permission denied', 'Normal user.', 'fix?',
        '''<ul>
          <li>/usr/local is root’s: sudo make install, or</li>
          <li>reconfigure with --prefix=$HOME/.local.</li>
        </ul>''', 'chmod 777 /usr/local.') +
    scn('Product company', 'Mid-level', 'A snap auto-update broke a demo', 'Ubuntu laptop.', 'now?',
        '''<ul>
          <li>sudo snap revert NAME.</li>
          <li>snap refresh --hold for the demo period.</li>
          <li>Pin a channel/track for stability.</li>
        </ul>''', 'removing snapd.') +
    scn('Platform', 'Senior', 'Same tool on 200 servers, only source exists', 'Fleet.', 'how?',
        '''<ul>
          <li>Build once in CI with DESTDIR, package as .deb/.rpm (fpm, rpmbuild).</li>
          <li>Publish to an internal repository; install with apt/dnf.</li>
          <li>Never compile on each production server.</li>
        </ul>''', 'make install on every host.')
) + interview([
    ('What does ./configure do?', 'Checks the system and writes the Makefile.'),
    ('Why /usr/local?', 'Kept separate from distro files.'),
    ('What is DESTDIR?', 'Staging root for make install.'),
    ('snap confinement types?', 'strict, classic, devmode.'),
    ('Flatpak runtime?', 'Shared base libraries.'),
    ('How do snaps store apps?', 'squashfs images under /snap/NAME/REV.'),
    ('CMake equivalent of configure/make?', 'cmake -B build; cmake --build build; cmake --install build.'),
], [
    ('LFCS', 'Install software from packages and source.'),
    ('RHCSA', 'Flatpak is in the RHEL 9 objectives.'),
    ('CompTIA Linux+', 'Compiling from source, sandboxed apps.'),
]) + distro('Bundled formats per distribution.', [
    ('snap', 'default', 'available (EPEL)', 'available', 'AUR'),
    ('flatpak', 'available', 'default on Fedora', 'available', 'available'),
    ('Build tools', 'build-essential', '"Development Tools"', 'devel_basis (SUSE)', 'base-devel'),
    ('Headers package', 'libX-dev', 'X-devel', 'X-devel', 'included'),
    ('Local prefix', '/usr/local', '/usr/local', '/usr/local', '/usr/local'),
]) + teaser('14.5', 'Every tarball in this lesson was a .tar.gz. Next: tar, gzip, bzip2, xz and zip in depth: which compresses best, which is fastest, and how to back up a directory properly.')

CHEATSHEET = cheatsheet('snap / flatpak / source', [
    ('snap', [('snap install X', 'install'), ('--classic', 'full access'), ('snap refresh', 'update'), ('snap revert X', 'roll back')]),
    ('flatpak', [('flatpak install flathub ID', 'install'), ('--user', 'no root'), ('flatpak run ID', 'start'), ('uninstall --unused', 'clean')]),
    ('Source', [('sha256sum -c', 'verify'), ('tar -xzf', 'unpack'), ('./configure --prefix', 'configure'), ('make -j$(nproc)', 'build')]),
    ('Install', [('make install', 'copy'), ('DESTDIR=DIR', 'stage'), ('make uninstall', 'remove'), ('/usr/local', 'never /usr')]),
])

MINDMAP = mindmap('Beyond apt/dnf', [
    ('snap', 'amber', ['channels', 'revert', 'classic']),
    ('flatpak', 'blue', ['Flathub', 'runtimes', '--user']),
    ('AppImage', 'violet', ['one file', 'chmod +x', 'no install']),
    ('Source', 'red', ['verify', 'configure', 'make']),
    ('Install', 'green', ['prefix', 'DESTDIR', 'uninstall']),
    ('Choose', 'acc', ['repo first', 'sandbox', 'fleet: package']),
])

LAB = lab('build it yourself', 'Build the lab (it creates <code>~/dl/greet-1.2.tar.gz</code> and its checksum), write <code>~/lab144/answers.sh</code>, then run the checker.',
    setup=SRC + '''
mkdir -p ~/lab144 && cd ~/lab144 && rm -rf answers.sh *.txt inst''',
    tasks=['Verify the tarball with its SHA256SUMS file and save the output line into <code>~/lab144/verify.txt</code>.',
           'Unpack it under <code>~/lab144/</code>, configure it with prefix <code>~/lab144/inst</code> and greeting <code>Hi</code>, build and install it.',
           'Run the installed <code>greet</code> with the argument <code>lab</code> and save its output into <code>run.txt</code>.',
           'Write the number of files installed under <code>~/lab144/inst</code> into <code>count.txt</code>.'],
    solution='''cat > answers.sh <<'EOF'
cd ~/dl && sha256sum -c SHA256SUMS > ~/lab144/verify.txt
cd ~/lab144 && tar -xzf ~/dl/greet-1.2.tar.gz && cd greet-1.2
./configure --prefix=$HOME/lab144/inst --greeting=Hi > /dev/null && make > /dev/null && make install > /dev/null
~/lab144/inst/bin/greet lab > ~/lab144/run.txt
find ~/lab144/inst -type f | wc -l > ~/lab144/count.txt
EOF''',
    check='''cd ~/lab144; rm -rf verify.txt run.txt count.txt inst greet-1.2
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f answers.sh ] && bash answers.sh > /dev/null 2>&1
ok "1 verify" 'grep -q "greet-1.2.tar.gz: OK" verify.txt 2>/dev/null'
ok "2 build"  '[ -x inst/bin/greet ]'
ok "3 run"    '[ "$(cat run.txt 2>/dev/null)" = "Hi, lab! (greet 1.2)" ]'
ok "4 count"  '[ "$(cat count.txt 2>/dev/null)" = 2 ]' ''')
