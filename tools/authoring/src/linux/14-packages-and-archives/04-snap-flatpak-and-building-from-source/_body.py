import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

# A tiny real source package: greet-1.2 with configure, Makefile.in and C code; built for real on our machine.
SRC = r"""rm -rf ~/src ~/dl ~/.local/opt/greet ~/stage; mkdir -p ~/src/greet-1.2 ~/dl; cd ~/src/greet-1.2
cat > greet.c <<'EOF'
#include <stdio.h>
#ifndef GREETING
#define GREETING "Hello"
#endif
int main(int argc, char **argv) {
    printf("%s, %s! (greet 1.2)\n", GREETING, argc > 1 ? argv[1] : "world");
    return 0;
}
EOF
cat > configure <<'EOF'
#!/bin/sh
# minimal configure: --prefix=DIR and --greeting=TEXT
prefix=/usr/local; greeting=Hello
for a in "$@"; do
  case $a in
    --prefix=*) prefix=${a#*=} ;;
    --greeting=*) greeting=${a#*=} ;;
    --help) echo "usage: ./configure [--prefix=DIR] [--greeting=TEXT]"; exit 0 ;;
    *) echo "configure: error: unknown option $a" >&2; exit 1 ;;
  esac
done
printf 'checking for a C compiler... '
if command -v cc >/dev/null; then echo cc; else echo no; echo "configure: error: no C compiler found (install build-essential or gcc)" >&2; exit 1; fi
echo "checking install prefix... $prefix"
sed -e "s|@prefix@|$prefix|" -e "s|@greeting@|$greeting|" Makefile.in > Makefile
echo "config.status: creating Makefile"
EOF
chmod +x configure
printf 'prefix = @prefix@\nCFLAGS = -O2 -Wall -DGREETING=\\"@greeting@\\"\n\ngreet: greet.c\n\tcc $(CFLAGS) -o greet greet.c\n\ninstall: greet\n\tinstall -Dm755 greet $(DESTDIR)$(prefix)/bin/greet\n\tinstall -Dm644 README $(DESTDIR)$(prefix)/share/doc/greet/README\n\nuninstall:\n\trm -f $(DESTDIR)$(prefix)/bin/greet $(DESTDIR)$(prefix)/share/doc/greet/README\n\nclean:\n\trm -f greet\n' > Makefile.in
echo 'greet 1.2: prints a greeting. Build: ./configure && make && make install' > README
cd ~/src && tar -czf ~/dl/greet-1.2.tar.gz greet-1.2 && rm -rf ~/src/greet-1.2
cd ~/dl && sha256sum greet-1.2.tar.gz > SHA256SUMS
mkdir -p ~/typ && cd ~/typ
cat > snap-list.txt <<'EOF'
Name               Version          Rev    Tracking         Publisher     Notes
core22             20241001         1663   latest/stable    canonical**   base
firefox            132.0-1          5187   latest/stable    mozilla**     -
lxd                5.21.2-34459c8   30131  5.21/stable      canonical**   -
snapd              2.65.3           23258  latest/stable    canonical**   snapd
code               6f17636e         174    latest/stable    vscode**      classic
EOF
cat > flatpak-list.txt <<'EOF'
Name                   Application ID                  Version   Branch  Installation
GIMP                   org.gimp.GIMP                   2.10.38   stable  system
VLC                    org.videolan.VLC                3.0.21    stable  system
Freedesktop Platform   org.freedesktop.Platform        24.08.8   24.08   system
GNOME Application Pl…  org.gnome.Platform              47        47      system
EOF"""

HOOK = hook('Riya needs three tools the company laptop’s repositories do not have in the right version: VS Code, a newer GIMP, and an internal tool shipped only as <code>greet-1.2.tar.gz</code> source code. There are three answers outside apt and dnf: <b>snap</b> (Canonical’s self-contained packages), <b>flatpak</b> (sandboxed desktop apps from Flathub) and <b>building from source</b> with the classic <code>./configure &amp;&amp; make &amp;&amp; sudo make install</code>. This lesson builds a real program from source on our machine, and shows when each way is right.',
    ['install, list, update and remove snaps (channels, revisions, classic confinement) and flatpaks (remotes, runtimes, sandbox)',
     'download, verify (sha256sum) and unpack a source tarball, then configure, make and make install it',
     'install into your home or /usr/local with --prefix and DESTDIR, and uninstall cleanly',
     'choose between repository package, snap, flatpak, AppImage and source for a given situation'])
ROAD = roadmap([
    ('story', 'The story', 3, 'three tools, no package'),
    ('decide', 'Which way?', 2, 'the quick chart'),
    ('definition', 'snap, flatpak, source', 5, 'simple meaning + 4 depths'),
    ('types', 'Compared', 5, 'deb/rpm vs snap vs flatpak vs AppImage vs source'),
    ('commands', 'By field', 15, 'a real build from source'),
    ('animation', 'See it happen', 4, 'configure → make → install'),
    ('run', 'Run on your PC', 4, 'snap and flatpak sessions'),
    ('lab', 'Practice lab', 7, 'build it yourself'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('I need software that is… → use', [
    ('in the distro repositories', 'sudo apt / dnf install', 'first choice'),
    ('a desktop app, newer than the repos', 'flatpak install flathub ID', 'sandboxed'),
    ('published by its vendor as a snap', 'sudo snap install NAME', 'auto-updates'),
    ('a single portable file', 'AppImage: chmod +x, run', 'no install'),
    ('only source code', './configure --prefix=… && make && make install', 'you maintain it'),
    ('a developer tool for one user', 'install to ~/.local (--prefix=$HOME/.local)', 'no sudo'),
])

cmap = concept_map(
    [('14.1', 'Packages', 'why packages'), ('14.2', 'apt', 'repo packages'), ('12.1', 'PATH', 'where commands are found')],
    ['snap: channels, revisions, confinement', 'flatpak: remotes, runtimes, sandbox', 'AppImage', 'tarball → verify → unpack', './configure, make, make install', '--prefix and DESTDIR', 'uninstalling source builds'],
    [('14.5', 'tar and compression', 'tarballs in depth'), ('19.4', 'Checksums', 'sha256sum, GPG'), ('17.2', 'systemd', 'snapd is a service'), ('20.3', 'Namespaces', 'how sandboxes work')],
    'Repository first; snap or flatpak for newer apps; source when there is nothing else, installed under a prefix you control.')

sc = (term(20, 14, 316, 156, ['$ tar -xzf greet-1.2.tar.gz', '$ cd greet-1.2 && ./configure', ('config.status: creating Makefile', 'out'), '$ make && make install', ('install … bin/greet', 'out'), '$ greet Riya', ('Hello, Riya! (greet 1.2)', 'acc')], title='riya@laptop: ~/src', prompt='$', size=6.6, step=17)
      + t(352, 36, 'Three more ways:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['snap install code', 'flatpak install GIMP', 'AppImage: one file', 'source: configure,', '  make, make install'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Three tools, no package</h2>
  <div class="story">
''' + puzzle('Riya runs <code>sudo snap install code</code> and gets “error: This revision of snap "code" was published using classic confinement”. Next, she builds <code>greet</code> from source, but <code>make install</code> fails with “Permission denied” on <code>/usr/local/bin</code>. Finally she wonders: a month from now, how will she uninstall something that no package manager knows about?') + '''
    <p class="narration">On Riya’s laptop (the source build in this lesson really runs on our build machine).</p>
''' + scene('A terminal: unpack greet-1.2.tar.gz, run ./configure, make and make install, then run greet Riya, which prints Hello, Riya!', sc,
            'Source builds: <tspan font-weight="700" class="s-acc">configure → make → install</tspan>.') + '''
K> Why not always use apt?
A> Always try it first: repository packages get security updates with everything else. But the repositories freeze versions for stability, some vendors publish only snaps or flatpaks, and some software exists only as source code.
R> And snap vs flatpak?
A> Both bundle an app with its libraries and run it in a sandbox. Snap is Canonical’s (default on Ubuntu, also servers and CLI tools); flatpak is community-led and focused on desktop apps from Flathub. Today: both, plus a complete source build you can repeat.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Five ways to get software, from most to least managed: distro package, snap, flatpak, AppImage, source build; arrows show who updates each.">'
       + ''.join(label_box(14 + i * 125, 40, 115, 60, [a, b], c, 8.6) + t(71 + i * 125, 124, u, 8, 'ink2')
                 for i, (a, b, c, u) in enumerate([('deb / rpm', 'repository', 'green', 'distro updates it'), ('snap', 'Snap Store', 'amber', 'snapd auto-updates'), ('flatpak', 'Flathub', 'blue', 'flatpak update'), ('AppImage', 'one file', 'violet', 'you replace it'), ('source', 'tarball / git', 'red', 'you rebuild it')]))
       + t(320, 24, 'more managed  ←────────────→  more manual', 9, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('snap, flatpak and source at four depths', [
    ('v', 'No jargon: who keeps it up to date?', '      <p>The further right, the more work for you.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>sudo snap install firefox</code>, <code>snap list</code>, <code>sudo snap remove firefox</code>.</li>
        <li><code>flatpak install flathub org.gimp.GIMP</code>, <code>flatpak run org.gimp.GIMP</code>.</li>
        <li><code>tar -xzf app-1.0.tar.gz; cd app-1.0; ./configure; make; sudo make install</code>.</li>
      </ul>'''),
    ('i', 'The differences that matter', '''      <ul>
        <li><b>Snap channels</b>: <code>latest/stable</code>, <code>candidate</code>, <code>beta</code>, <code>edge</code>; <code>sudo snap refresh --channel=5.21/stable lxd</code>. <code>snap revert</code> goes back one revision.</li>
        <li><b>Confinement</b>: strict (sandboxed), classic (full access, like a normal program, needs <code>--classic</code>), devmode (testing).</li>
        <li><b>Flatpak runtimes</b> (org.freedesktop.Platform, org.gnome.Platform) are shared between apps; permissions are changed with Flatseal or <code>flatpak override</code>.</li>
        <li><b>Source</b>: <code>--prefix</code> chooses where files go (default /usr/local); <code>make install</code> into /usr/local needs sudo, into <code>$HOME/.local</code> does not.</li>
      </ul>'''),
    ('a', 'Behind the screen: squashfs, OSTree and Makefiles', '''      <ul>
        <li>A snap is a compressed <b>squashfs</b> image mounted read-only under <code>/snap/NAME/REV</code> (look at <code>mount | grep snap</code>); <code>snapd</code> is a systemd service; the sandbox uses AppArmor, seccomp and cgroups.</li>
        <li>Flatpak stores apps in an <b>OSTree</b> repository (Git-like, deduplicated) under <code>/var/lib/flatpak</code> and runs them through <b>bubblewrap</b> with namespaces (Lesson 20.3).</li>
        <li><code>./configure</code> (usually generated by GNU Autoconf) tests the system and writes the Makefile; CMake (<code>cmake -B build; cmake --build build</code>) and Meson are modern alternatives.</li>
        <li><code>DESTDIR=/tmp/stage make install</code> installs into a staging tree: how packagers turn source into .deb/.rpm, and how you can see exactly which files will be installed.</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>snap, flatpak and building from source</h2>
''' + def_block(
    '<b>snap</b> and <b>flatpak</b> are distribution-independent package systems: each package bundles the application with the libraries it needs and runs it in a sandbox, so the same package works on Ubuntu, Fedora or Debian. <b>Building from source</b> means downloading the program’s source code (usually a <code>.tar.gz</code> tarball), checking it, and compiling and installing it yourself, typically with <code>./configure</code>, <code>make</code> and <code>make install</code>.',
    'Bundled apps with sandboxes, or compile it yourself.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('snap / snapd', 'Canonical’s bundle format / its daemon.'),
    ('Channel', 'track/risk, e.g. latest/stable.'),
    ('Confinement', 'strict, classic, devmode.'),
    ('flatpak / Flathub', 'Bundle format / main app store.'),
    ('Runtime', 'Shared base libraries for flatpaks.'),
    ('Tarball', 'A .tar.gz of source code.'),
    ('Prefix', 'Install root: /usr/local, ~/.local.'),
    ('DESTDIR', 'Staging directory for make install.'),
]) + '\n' + names('Where the names come from.', [
    ('snap', 'a package that “snaps” in', 'Ubuntu, 2016.'),
    ('flatpak', 'from IKEA flat-pack furniture', 'Formerly xdg-app, 2015.'),
    ('AppImage', 'an app as one disk image', 'Run anywhere.'),
    ('make', 'make the target', 'Stuart Feldman, 1976.'),
    ('configure', 'configure for this system', 'Autoconf generates it.'),
    ('/usr/local', 'local, not from the distro', 'FHS rule.'),
    ('squashfs', 'squashed (compressed) file system', 'Snaps.'),
    ('bubblewrap', 'wraps an app in a sandbox', 'Flatpak.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Install a snap', '<code>sudo snap install NAME</code>'),
    ('Classic snap', '<code>--classic</code>'),
    ('Install a flatpak', '<code>flatpak install flathub ID</code>'),
    ('Build', '<code>./configure &amp;&amp; make</code>'),
    ('Install without sudo', '<code>--prefix=$HOME/.local</code>'),
    ('Check a download', '<code>sha256sum -c SHA256SUMS</code>'),
]) + '\n' + lv + didyou('Snaps update themselves automatically, by default up to four times a day. <code>sudo snap refresh --hold=24h</code> pauses updates, and <code>snap refresh --time</code> shows the schedule.') + '''
EXAM> “What does make install do, and where do files go?” → It copies the built files to the directories under the prefix chosen by ./configure (default /usr/local: bin, lib, share), which is why it usually needs sudo; no package manager records them.
''' + qc('Why install source builds under /usr/local and not /usr?', '/usr belongs to the package manager; /usr/local is reserved for locally built software, so the two never overwrite each other.') + mistake('sudo make install straight into /usr',
    './configure --prefix=/usr/local (default) or --prefix=$HOME/.local',
    'Files in /usr can overwrite or be overwritten by distro packages, and nothing records them for removal.') + mistake('building a downloaded tarball without checking it',
    'sha256sum -c SHA256SUMS (and gpg --verify if a .asc signature is published)',
    'A tampered or truncated download would be compiled and installed, often as root.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>Five ways to install software</h2>
''' + table(['', 'deb / rpm', 'snap', 'flatpak', 'AppImage', 'source'], [
    ['Comes from', 'distro repo', 'Snap Store', 'Flathub (remotes)', 'vendor website', 'tarball / git'],
    ['Works on', 'one distro family', 'most distros', 'most distros', 'most distros', 'anywhere it compiles'],
    ['Libraries', 'shared, system', 'bundled + base snap', 'bundled + runtime', 'bundled', 'system'],
    ['Sandbox', 'no', 'yes (strict)', 'yes', 'no', 'no'],
    ['Updates', 'apt/dnf upgrade', 'automatic', 'flatpak update', 'by hand', 'rebuild by hand'],
    ['Disk use', 'small', 'large', 'large (runtimes shared)', 'medium', 'small'],
    ['Root needed', 'yes', 'yes', 'no (--user)', 'no', 'only for /usr/local'],
    ['Best for', 'almost everything', 'Ubuntu, vendor apps, CLI', 'desktop apps', 'quick try-outs', 'nothing else exists'],
], minw=720) + table(['snap command', 'flatpak command', 'Does'], [
    ['<code>snap find NAME</code>', '<code>flatpak search NAME</code>', 'search'],
    ['<code>sudo snap install NAME</code>', '<code>flatpak install flathub ID</code>', 'install'],
    ['<code>snap list</code>', '<code>flatpak list --app</code>', 'installed'],
    ['<code>sudo snap refresh</code>', '<code>flatpak update</code>', 'update'],
    ['<code>sudo snap revert NAME</code>', '<code>flatpak update --commit=…</code>', 'roll back'],
    ['<code>sudo snap remove NAME</code>', '<code>flatpak uninstall ID</code>', 'remove'],
    ['<code>snap info NAME</code>', '<code>flatpak info ID</code>', 'details, channels'],
    ['<code>snap connections NAME</code>', '<code>flatpak info --show-permissions ID</code>', 'sandbox permissions'],
], minw=560) + qc('Which needs no root at all: snap, flatpak --user, or make install into /usr/local?', 'flatpak --user (and make install into $HOME/.local).') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>A real source build, then snap and flatpak</h2>
  <p id="commands">Our build machine has gcc and make, so the source build is completely real: we prepared a small program <code>greet-1.2.tar.gz</code> (C code, a configure script and a Makefile) in <code>~/dl</code>. snap and flatpak are not installed there, so their cards analyse saved typical outputs (in <code>~/typ</code>); real sessions are in Run on your PC.</p>
''' + cmdcard_u(['any download you will build or run', 'before sudo'],
               ['skipping it because “it is from GitHub”'])(
    'verify', 'sha256sum -c · tar -tzf · tar -xzf', 'verify and unpack',
    'Download the tarball and its checksum file, check it with <code>sha256sum -c</code>, list its contents with <code>tar -tzf</code> (does it unpack into one directory?), then extract with <code>tar -xzf</code>.',
    'sha256sum -c SHA256SUMS   ·   tar -tzf app.tar.gz | head   ·   tar -xzf app.tar.gz', 'safe',
    [('sha256sum -c FILE', 'verify listed files', 'every download'),
     ('gpg --verify f.asc', 'signature', 'if published'),
     ('tar -tzf', 'list', 'before extracting'),
     ('tar -xzf', 'extract .tar.gz', 'unpack'),
     ('tar -xJf', 'extract .tar.xz', 'many projects'),
     ('-C DIR', 'extract into DIR', 'tidy')],
    dict(setup=SRC, cmd="cd ~/dl\nsha256sum -c SHA256SUMS\ntar -tzf greet-1.2.tar.gz\nmkdir -p ~/src && tar -xzf greet-1.2.tar.gz -C ~/src && ls ~/src/greet-1.2", note='OK means the file matches the published checksum. Everything unpacks into greet-1.2/, as it should.'),
    [('sec', [
        dict(situation='A tampered download fails the check.', setup=SRC, cmd="cd ~/dl; cp greet-1.2.tar.gz /tmp/g.tgz; echo x >> greet-1.2.tar.gz; sha256sum -c SHA256SUMS; echo \"exit $?\"; cp /tmp/g.tgz greet-1.2.tar.gz", why='One extra byte: FAILED and exit 1. Never build it.', expect='any')]),
    ],
    anat=anatomy([('sha256sum', 'cmd', 'checksum tool'), ('-c', 'opt', 'check mode'), ('SHA256SUMS', 'arg', 'list of expected sums')], 'Compare, do not just compute.')
) + cmdcard_u(['every tarball with a configure script'],
               ['running configure as root', 'ignoring its errors'])(
    'configure', './configure --help · --prefix=DIR', 'configure',
    '<code>./configure</code> checks the system (compiler, libraries) and writes the Makefile. <code>--help</code> lists its options; <code>--prefix</code> chooses where make install will put files. If a check fails it stops with “configure: error: …”: install the missing <code>-dev</code>/<code>-devel</code> package and run it again.',
    './configure --prefix=$HOME/.local', 'safe',
    [('--help', 'options', 'always read'),
     ('--prefix=DIR', 'install root', '/usr/local default'),
     ('--enable-X / --disable-X', 'features', 'project-specific'),
     ('--with-X=DIR', 'where a library is', 'odd locations'),
     ('CC= CFLAGS=', 'compiler settings', 'tuning'),
     ('config.log', 'details of failed checks', 'debugging')],
    dict(setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src", cmd="cd ~/src/greet-1.2\n./configure --help\n./configure --prefix=$HOME/.local/opt/greet --greeting=Namaste\ngrep -E '^(prefix|CFLAGS)' Makefile", note='Our configure is a small hand-written one; real ones (from Autoconf) print dozens of checks but behave the same way.'),
    [('devops', [
        dict(situation='Unknown option: configure stops.', setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src", cmd="cd ~/src/greet-1.2; ./configure --with-ssl; echo \"exit $?\"", why='Read the error, check --help, fix, rerun.', expect='any')]),
    ]
) + cmdcard_u(['compiling after configure'],
               ['sudo make (only install needs root)'])(
    'make', 'make · make -j$(nproc) · make install · DESTDIR · make uninstall', 'build and install',
    '<code>make</code> compiles following the Makefile’s rules; <code>-j$(nproc)</code> uses all CPU cores. <code>make install</code> copies the results under the prefix. <code>DESTDIR=/tmp/stage make install</code> installs into a staging copy so you can see every file first. Many projects offer <code>make uninstall</code>; keep the source directory for it.',
    'make -j$(nproc) && make install   ·   make DESTDIR=$HOME/stage install', 'change',
    [('make', 'build default target', 'compile'),
     ('make -j N', 'parallel', 'faster'),
     ('make install', 'copy to prefix', 'install'),
     ('DESTDIR=DIR', 'staging root', 'see files first'),
     ('make uninstall', 'remove', 'if provided'),
     ('make clean', 'delete build output', 'rebuild')],
    dict(setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src && cd ~/src/greet-1.2 && ./configure --prefix=$HOME/.local/opt/greet --greeting=Namaste > /dev/null", cmd="cd ~/src/greet-1.2\nmake\nmake DESTDIR=$HOME/stage install > /dev/null && (cd ~/stage && find . -type f | sort)\nmake install\n~/.local/opt/greet/bin/greet Riya", note='The staging tree shows exactly which two files install will create; then the real install, and the program runs.'),
    [('sys', [
        dict(situation='Permission denied: installing into /usr/local as a normal user.', setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src && cd ~/src/greet-1.2 && ./configure > /dev/null && make > /dev/null", cmd="cd ~/src/greet-1.2; make install 2>&1 | tail -2", why='The puzzle: /usr/local needs sudo, or choose --prefix=$HOME/.local.', expect='any'),
        dict(situation='Uninstall cleanly.', setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src && cd ~/src/greet-1.2 && ./configure --prefix=$HOME/.local/opt/greet > /dev/null && make install > /dev/null", cmd="cd ~/src/greet-1.2; make uninstall; [ -e ~/.local/opt/greet/bin/greet ] && echo 'still there' || echo 'no greet binary left'", why='Keep the source tree (or the DESTDIR file list) to undo an install.', expect='any')]),
    ]
) + cmdcard_u(['vendor apps on Ubuntu', 'auto-updating tools'],
               ['servers where surprise updates are unwelcome (hold them)'])(
    'snap', 'snap find · install · list · refresh · revert · remove', 'snap',
    '<code>sudo snap install NAME</code> installs from the Snap Store; <code>--classic</code> for apps needing full access (editors, IDEs), <code>--channel=</code> for a version track. <code>snap list</code> shows version, revision and tracking channel; <code>snap revert</code> goes back to the previous revision.',
    'sudo snap install code --classic   ·   snap list   ·   sudo snap revert firefox', 'change',
    [('snap find X', 'search', 'discover'),
     ('install --classic', 'no sandbox', 'IDEs'),
     ('--channel=T/R', 'track/risk', 'versions'),
     ('snap list', 'installed', 'inventory'),
     ('refresh / revert', 'update / back', 'control'),
     ('refresh --hold', 'pause updates', 'servers')],
    dict(setup=SRC, cmd="cd ~/typ\nawk 'NR>1{print $1, \"rev\", $3, \"on\", $4}' snap-list.txt\nawk 'NR>1 && $NF==\"classic\"{print \"classic confinement:\", $1}' snap-list.txt", note='Saved typical snap list. The puzzle: code is a classic snap, so it needs --classic.'),
    [('sys', [
        dict(situation='Which snaps are pinned to a version track?', setup=SRC, cmd="cd ~/typ; awk 'NR>1 && $4 !~ /^latest/ {print $1, \"tracks\", $4}' snap-list.txt", why='lxd follows 5.21, an LTS track.')]),
    ]
) + cmdcard_u(['desktop apps on any distro'],
               ['servers and CLI tools'])(
    'flatpak', 'flatpak remote-add · install · run · list · update · uninstall', 'flatpak',
    'Add the Flathub remote once, then install apps by their reverse-DNS ID (<code>org.gimp.GIMP</code>). Apps share <b>runtimes</b>; <code>flatpak list --app</code> hides them. <code>--user</code> installs for you only, without root. <code>flatpak uninstall --unused</code> removes runtimes no app needs.',
    'flatpak install flathub org.gimp.GIMP   ·   flatpak run org.gimp.GIMP', 'change',
    [('remote-add --if-not-exists flathub URL', 'add store', 'once'),
     ('install flathub ID', 'install', 'apps'),
     ('--user', 'no root', 'personal'),
     ('run ID', 'start', 'launch'),
     ('list --app', 'apps only', 'inventory'),
     ('uninstall --unused', 'clean runtimes', 'disk')],
    dict(setup=SRC, cmd="cd ~/typ\nawk -F'  +' 'NR>1{print $2}' flatpak-list.txt | grep -Ev 'Platform' | sed 's/^/app: /'\nawk -F'  +' 'NR>1 && $2 ~ /Platform/ {print \"runtime:\", $2, $4}' flatpak-list.txt", note='Two apps, two shared runtimes (saved typical flatpak list).'),
    [('dev', [
        dict(situation='Reverse-DNS IDs: who publishes it?', cmd="for id in org.gimp.GIMP org.videolan.VLC com.visualstudio.code; do echo \"$id -> publisher domain: $(echo $id | awk -F. '{print $2\".\"$1}')\"; done", why='ID = reversed domain + app name.')]),
    ]
) + undo('Every way has an undo; source builds need you to plan it.', [
    ('Bad snap update:', '<code>sudo snap revert NAME</code> (previous revision is kept).'),
    ('Flatpak:', '<code>flatpak uninstall ID</code>; <code>--delete-data</code> also removes its ~/.var/app data.'),
    ('Source build:', '<code>make uninstall</code> from the same source tree, or delete the prefix directory (<code>~/.local/opt/NAME</code>) if you used one per program.'),
    ('Wrong prefix:', '<code>make clean</code>, rerun <code>./configure --prefix=…</code>, make again.'),
]) + '<h3>Errors students see most</h3><p class="muted">snap and flatpak messages are typical (not run here); the build errors below the table are real.</p>' + table(['Message', 'Meaning', 'Fix'], [
    ['<code>error: This revision of snap "code" was published using classic confinement</code>', 'needs full system access', '<code>sudo snap install code --classic</code>'],
    ['<code>error: snap "x" not found</code>', 'wrong name', '<code>snap find x</code>'],
    ['<code>error: No remote refs found for ‘flathub’</code>', 'Flathub not added', '<code>flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo</code>'],
    ['<code>configure: error: no acceptable C compiler found</code>', 'no gcc', '<code>sudo apt install build-essential</code> / <code>sudo dnf group install "Development Tools"</code>'],
    ['<code>fatal error: openssl/ssl.h: No such file or directory</code>', 'missing headers', '<code>libssl-dev</code> (Debian) / <code>openssl-devel</code> (RHEL)'],
], minw=520) + errors('Really run on our build machine:', [
    dict(setup=SRC, cmd="cd ~/dl && ./configure", meaning='No configure in this directory: you are not inside the unpacked source.', fix='cd into the extracted directory first.'),
    dict(setup=SRC, cmd="cd ~ && make", meaning='make found no Makefile here.', fix='Run ./configure first (it creates the Makefile), in the source directory.'),
]) + qc('make install says Permission denied on /usr/local/bin. Two fixes?', 'sudo make install, or reconfigure with --prefix=$HOME/.local and install without sudo.') + '''
'''
cards = cards + '</section>\n'

ST = [('tar -xzf', 'unpack source', 'blue'), ('./configure', 'check system, write Makefile', 'amber'), ('make', 'compile greet.c → greet', 'green'), ('make install', 'copy to PREFIX/bin', 'red')]
def bstep(k):
    return ''.join(label_box(14, 12 + i * 40, 330, 32, [f'{a}: {b}'], c if i <= k else 'card', 8.2) for i, (a, b, c) in enumerate(ST))
see_cmds = [['$ tar -xzf greet-1.2.tar.gz', ('greet-1.2/', 'out')], ['$ ./configure --prefix=~/.local', ('creating Makefile', 'out')], ['$ make', ('cc -O2 -o greet greet.c', 'out')], ['$ make install', ('install -Dm755 greet …/bin', 'out'), ('$ greet → Hello!', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@laptop: ~/src', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Unpack.', 'Configure.', 'Compile.', 'Install.'])]
two = anim_two('From tarball to command', 'Behind the screen: four stages',
               'A terminal: unpack the tarball, configure with a prefix, make compiles, make install copies the binary.',
               'Four stacked boxes light up: unpack, configure, make, install.', see, [bstep(k) for k in range(4)],
               ['unpack.', 'configure.', 'make.', 'install.'],
               ['tar', 'configure', 'make', 'install'])

def snapv(k):
    o = t(180, 18, 'snap revisions of firefox', 9.6, 'ink2', bold=True)
    revs = [('5100', 'old'), ('5187', 'current'), ('5210', 'refresh')]
    st = [['card', 'green', 'card'], ['card', 'card', 'green'], ['card', 'green', 'card'], ['card', 'green', 'card']][k]
    for i, (r, n) in enumerate(revs):
        o += label_box(14 + i * 115, 40, 105, 50, ['rev ' + r, n], st[i], 8)
    o += t(180, 130, ['5187 is mounted at /snap/firefox/current', 'snap refresh: 5210 becomes current', 'broken? snap revert: back to 5187', 'old revisions kept (refresh.retain=2)'][k], 9, 'violet', bold=True)
    return o
s1 = anim_one('Animated example', 'snap refresh and revert',
              'Revisions are side by side; “current” is a symlink.', 'firefox revisions', 'Three revision boxes; the green one is current.', [snapv(k) for k in range(4)],
              ['current.', 'refresh.', 'revert.', 'retain.'], hid='scenario-snap')

dx = dissect('Layer by layer: what a source build creates',
    'Each layer has a real command from our build machine.', [
    dict(key='tar', name='Tarball', sub='.tar.gz', why='The source.', how='tar + gzip.', impl='One top directory.', used='Every project.',
         setup=SRC, cmd="cd ~/dl; ls -l greet-1.2.tar.gz | awk '{print $5, \"bytes\"}'; tar -tzf greet-1.2.tar.gz | wc -l | sed 's/^/entries: /'"),
    dict(key='mk', name='Makefile', sub='rules', why='How to build.', how='target: deps, then commands.', impl='Tab-indented.', used='make.',
         setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src && cd ~/src/greet-1.2 && ./configure > /dev/null", cmd="cd ~/src/greet-1.2; grep -E '^[a-z]+:' Makefile"),
    dict(key='bin', name='Binary', sub='ELF', why='The program.', how='Compiled C.', impl='Dynamically linked to libc.', used='Runs.',
         setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src && cd ~/src/greet-1.2 && ./configure > /dev/null && make > /dev/null", cmd="cd ~/src/greet-1.2; file greet | cut -d, -f1,2; ldd greet | awk '{print $1}' | grep -c . | sed 's/^/shared libraries: /'"),
], hint='Tarball → Makefile → binary. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>A build from source, and snap revisions</h2>
''' + two + s1 + dx + qc('Why does a snap revert work instantly?', 'The previous revision is still on disk; revert only switches the “current” link back.') + '''
</section>
'''

B = SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src && cd ~/src/greet-1.2 && ./configure --prefix=$HOME/.local/opt/greet > /dev/null && make > /dev/null"
VAR = variations('Fifteen more commands around source builds and bundled apps. All were really run on our build machine.', [
    ('Build variations', [
        dict(title='Custom greeting at configure time', setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src", cmd="cd ~/src/greet-1.2; ./configure --greeting=Vanakkam > /dev/null; make > /dev/null; ./greet Chennai", why='Options become compile-time defines.'),
        dict(title='Parallel build', setup=B, cmd="cd ~/src/greet-1.2; make clean > /dev/null; make -j$(nproc) | head -1", why='-j uses every core.'),
        dict(title='make knows it is up to date', setup=B, cmd="cd ~/src/greet-1.2; make", why='Targets newer than sources are skipped.'),
        dict(title='Dry run: what would install do?', setup=B, cmd="cd ~/src/greet-1.2; make -n install", why='-n prints commands without running them.'),
        dict(title='Strip the binary', setup=B, cmd="cd ~/src/greet-1.2; a=$(stat -c %s greet); strip greet; echo \"$a -> $(stat -c %s greet) bytes\"", why='Removes symbols; packages do this.'),
    ]),
    ('Prefix and PATH', [
        dict(title='Add the prefix to PATH', setup=B + " && make install > /dev/null", cmd="export PATH=$HOME/.local/opt/greet/bin:$PATH; command -v greet; greet", why='Then it runs by name (Lesson 12.1).'),
        dict(title='Every file the install made', setup=B + " && make install > /dev/null", cmd="find ~/.local/opt/greet -type f | sed \"s|$HOME|~|\"", why='One prefix per program = easy uninstall.'),
        dict(title='Record a manifest with DESTDIR', setup=B, cmd="cd ~/src/greet-1.2; make DESTDIR=$HOME/stage install > /dev/null; (cd ~/stage && find . -type f) | sed 's|^\\.||' > ~/greet.manifest; cat ~/greet.manifest | sed \"s|$HOME|~|\"", why='A list to delete later.'),
        dict(title='Uninstall from the manifest', setup=B + " && make install > /dev/null && make DESTDIR=$HOME/stage install > /dev/null && (cd ~/stage && find . -type f | sed 's|^\\.||') > ~/greet.manifest", cmd="xargs rm -v < ~/greet.manifest | sed \"s|$HOME|~|\"", why='Works even without make uninstall.'),
    ]),
    ('Checks', [
        dict(title='Which compiler and make?', cmd="cc --version | head -1; make --version | head -1", why='What configure looks for.'),
        dict(title='Is a library’s pkg-config file present?', cmd="pkg-config --exists zlib && echo 'zlib dev files: yes' || echo 'zlib dev files: no'", why='How configure finds libraries.', expect='any'),
        dict(title='Compute and store a checksum', setup=SRC, cmd="cd ~/dl; sha256sum greet-1.2.tar.gz | cut -c1-16", why='The first 16 hex digits.'),
    ]),
    ('snap and flatpak files', [
        dict(title='Snaps by publisher', setup=SRC, cmd="cd ~/typ; awk 'NR>1{gsub(/\\*/,\"\",$5); print $5}' snap-list.txt | sort | uniq -c", why='** marks verified publishers.'),
        dict(title='Snap base and system snaps', setup=SRC, cmd="cd ~/typ; awk 'NR>1 && ($NF==\"base\" || $NF==\"snapd\"){print $1, $NF}' snap-list.txt", why='Bases are runtimes for snaps.'),
        dict(title='Flatpak IDs by domain', setup=SRC, cmd="cd ~/typ; awk -F'  +' 'NR>1{split($2,a,\".\"); print a[1]\".\"a[2]}' flatpak-list.txt | sort -u", why='org.gimp, org.videolan…'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where each way is used</h2>
''' + usecase(label_box(14, 22, 92, 46, ['snap', 'Ubuntu'], 'amber', 8.6), '1. Ubuntu desktops and LXD',
              'Firefox and LXD ship as snaps on Ubuntu; servers hold refreshes to maintenance windows.', ['Install', '*snap', 'auto-update']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['flatpak', 'desktop'], 'blue', 8.6), '2. Fedora and Steam Deck',
    'Fedora Silverblue and SteamOS install desktop apps as flatpaks on a read-only base system.', ['Read-only OS', '*flatpak', 'apps']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['source', 'HPC'], 'red', 8.6), '3. Research clusters',
    'HPC centres build scientific software from source into versioned prefixes (/opt/app/1.2), loaded with environment modules.', ['Tarball', '*prefix', 'module load']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['DESTDIR', 'packaging'], 'green', 8.6), '4. Making packages',
    'Package builders run make DESTDIR=… install and wrap the staged files into a .deb or .rpm.', ['Build', '*stage', '.deb/.rpm']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['latest', 'tools'], 'violet', 8.6), '5. Newest tool versions',
    'When a team needs a newer version than the LTS repos have, a source build into ~/.local avoids touching the system.', ['Old in repo', '*~/.local', 'new version']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Verify a download', scenario='Before building.', setup=SRC, cmd="cd ~/dl && sha256sum -c SHA256SUMS", explain='OK or FAILED.'),
    dict(level='b', title='Peek inside a tarball', scenario='What is in it?', setup=SRC, cmd="tar -tzf ~/dl/greet-1.2.tar.gz | head -3", explain='-t lists.'),
    dict(level='i', title='Build in one line', scenario='Quick build.', setup=SRC + "\nmkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src", cmd="cd ~/src/greet-1.2 && ./configure --prefix=$HOME/.local > /dev/null && make > /dev/null && echo built", explain='&& stops at the first failure.'),
    dict(level='i', title='Cores available', scenario='make -j.', cmd="nproc", explain='Use with make -j.'),
    dict(level='a', title='Classic snaps', scenario='Audit.', setup=SRC, cmd="awk 'NR>1 && $NF==\"classic\"{print $1}' ~/typ/snap-list.txt", explain='No sandbox: review them.'),
], extra=build_up('a repeatable source install', 'Riya writes down the steps so anyone can rebuild greet the same way.', SRC, [
    ("cd ~/dl && sha256sum -c SHA256SUMS", '1. Verify.'),
    ("mkdir -p ~/src && tar -xzf ~/dl/greet-1.2.tar.gz -C ~/src && ls ~/src", '2. Unpack.'),
    ("cd ~/src/greet-1.2 && ./configure --prefix=$HOME/.local/opt/greet | tail -1", '3. Configure into its own prefix.'),
    ("cd ~/src/greet-1.2 && make > /dev/null && make install > /dev/null && ~/.local/opt/greet/bin/greet team", '4. Build, install, test.'),
], cumulative=True)) + VAR + which('Choosing the right way.', [
    ('Server software', 'distro package', 'Security updates.', 'snap that auto-restarts.'),
    ('Desktop app, newer', 'flatpak', 'Sandboxed, any distro.', 'PPAs from strangers.'),
    ('Vendor ships a snap', 'snap', 'Official.', 'Unofficial repacks.'),
    ('Try once', 'AppImage', 'No install.', 'Installing system-wide.'),
    ('Only source', '--prefix build', 'Contained.', 'make install into /usr.'),
    ('Many machines', 'build your own .deb/.rpm', 'Managed.', 'Building on each.'),
]) + keys('Handy forms.', [
    ('sudo snap install X --classic', 'IDEs', 'full access'),
    ('sudo snap refresh --hold=24h', 'pause updates', 'servers'),
    ('flatpak install --user flathub ID', 'no root', 'personal'),
    ('./configure --prefix=$HOME/.local', 'no sudo', 'own builds'),
    ('make -j$(nproc)', 'fast build', 'all cores'),
    ('make DESTDIR=~/stage install', 'see files', 'manifest'),
]) + scriptit('build-from-source.sh', 'Verify, unpack, configure into a per-program prefix, build, install, and print how to uninstall: the whole safe routine for a tarball, stopping at the first failure.',
'''set -e
tarball=~/dl/greet-1.2.tar.gz
name=$(basename "$tarball" .tar.gz)
prefix=$HOME/.local/opt/$name
cd "$(dirname "$tarball")" && sha256sum -c SHA256SUMS
mkdir -p ~/src && tar -xzf "$tarball" -C ~/src
cd ~/src/"$name"
./configure --prefix="$prefix" > /dev/null
make -j"$(nproc)" > /dev/null
make install > /dev/null
echo "installed: $(find "$prefix" -type f | wc -l) files under ${prefix/#$HOME/\~}"
"$prefix"/bin/greet script
echo "uninstall: rm -r ${prefix/#$HOME/\~}"''',
'<p>Each program gets its own prefix, so uninstalling is deleting one directory.</p>', expect='any') + puzzle_answer('<b>1.</b> VS Code is a <b>classic</b> snap (it needs full access to your files and tools): <code>sudo snap install code --classic</code>. <b>2.</b> The default prefix <code>/usr/local</code> belongs to root, so <code>make install</code> as a normal user fails; use <code>sudo make install</code>, or better, <code>./configure --prefix=$HOME/.local</code> and install without sudo. <b>3.</b> Keep the source directory for <code>make uninstall</code>, install each program into its own prefix (delete the directory to remove it), or record a manifest with <code>make DESTDIR=… install</code> first.') + qc('Which command removes a source-built program installed with --prefix=$HOME/.local/opt/greet?', 'rm -r ~/.local/opt/greet (or make uninstall in its source tree).') + '''
</section>
'''

body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../02-apt-and-dpkg-on-ubuntu-and-debian/">Lesson 14.2</a> (apt) and <a href="../../12-shell-environment/01-shell-variables-and-environment-variables-env/">Lesson 12.1</a> (PATH).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
