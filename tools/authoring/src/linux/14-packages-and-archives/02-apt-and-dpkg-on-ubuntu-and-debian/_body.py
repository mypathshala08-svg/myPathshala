import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *
import shlesson as _sh

PK = r"""export PATH=$PATH:/usr/sbin:/sbin; rm -rf ~/ap; mkdir -p ~/ap; cd ~/ap
mk(){ n=$1; v=$2; dep=$3; d=${n}_$v; mkdir -p $d/DEBIAN $d/usr/local/bin $d/etc/$n
  printf 'Package: %s\nVersion: %s\nArchitecture: all\nMaintainer: Riya <riya@example.com>\n%sDescription: %s demo\n' "$n" "$v" "${dep:+Depends: $dep
}" "$n" > $d/DEBIAN/control
  echo "/etc/$n/$n.conf" > $d/DEBIAN/conffiles; if [ "$v" = 1.0 ]; then echo "colour=blue"; else echo "colour=green"; fi > $d/etc/$n/$n.conf
  printf '#!/bin/sh\necho "%s %s"\n' "$n" "$v" > $d/usr/local/bin/$n; chmod 755 $d/usr/local/bin/$n
  dpkg-deb --build --root-owner-group $d > /dev/null; }
mk greet 1.0 tmux; mk greet 1.1 tmux
mkdir -p root/var/lib/dpkg/updates root/var/lib/dpkg/info; touch root/var/lib/dpkg/status
pdpkg(){ dpkg --force-not-root --root="$HOME/ap/root" --log="$HOME/ap/dpkg.log" "$@"; }"""

HOOK = hook('It is Patch Tuesday. Riya’s checklist for 40 Ubuntu servers: refresh the package lists, see what would be upgraded, upgrade, remove what is no longer needed, keep the database server on its current version, and write down what changed. Every step is one <code>apt</code> command. And when a vendor sends a <code>.deb</code> file, or something half-installs, she needs the lower-level tool <code>dpkg</code>. This lesson covers the daily apt and dpkg commands, what each one really does, the difference between remove and purge, upgrade and full-upgrade, and how to read the logs afterwards.',
    ['refresh, search, inspect and install packages with apt update, search, show, policy and install',
     'upgrade safely: apt list --upgradable, upgrade vs full-upgrade, simulate with -s, hold a package',
     'remove cleanly: remove vs purge vs autoremove, and clean the download cache',
     'use dpkg for local .deb files, broken installs and queries, and read /var/log/apt and dpkg logs'])
ROAD = roadmap([
    ('story', 'The story', 3, 'Patch Tuesday'),
    ('decide', 'Which command when?', 2, 'the quick chart'),
    ('definition', 'apt and dpkg', 5, 'simple meaning + 4 depths'),
    ('types', 'All the commands', 5, 'one table'),
    ('commands', 'By field', 15, 'real runs and simulations'),
    ('animation', 'See it happen', 4, 'update → upgrade'),
    ('run', 'Run on your PC', 4, 'apt needs sudo and network'),
    ('lab', 'Practice lab', 7, 'manage a package'),
], short=['story', 'decide', 'commands', 'lab'])
DECIDE = decide('Which command? (decide in 5 seconds)', [
    ('Refresh what the repositories offer', 'sudo apt update', 'always first'),
    ('What would be upgraded?', 'apt list --upgradable', 'preview'),
    ('Upgrade everything', 'sudo apt upgrade   (full-upgrade if it may remove/add)', 'patch'),
    ('Install / find / describe', 'sudo apt install X · apt search X · apt show X', 'daily'),
    ('Remove (keep configs) / everything', 'sudo apt remove X · sudo apt purge X', 'uninstall'),
    ('Clean leftovers', 'sudo apt autoremove · sudo apt clean', 'tidy'),
    ('Do not upgrade this one', 'sudo apt-mark hold X', 'pin'),
    ('A local .deb / broken install', 'sudo apt install ./f.deb · sudo apt -f install', 'dpkg cases'),
])

cmap = concept_map(
    [('14.1', 'Packages and repositories', 'the ideas'), ('8.4', 'sudo', 'root for changes'), ('6.1', 'grep', 'filtering lists')],
    ['update vs upgrade', 'install, show, search, policy', 'upgrade vs full-upgrade', 'remove vs purge vs autoremove', 'hold, simulate (-s), clean', 'dpkg -i, -l, --configure -a', 'logs: history.log, dpkg.log'],
    [('14.3', 'dnf and rpm', 'the Red Hat side'), ('19.3', 'Hardening', 'unattended-upgrades'), ('17.4', 'cron', 'scheduled updates'), ('18.1', 'Logs', 'reading them')],
    'apt talks to the repositories and plans; dpkg does the unpacking and keeps the records. Update the plan, simulate, then act.')

sc = (term(20, 14, 316, 156, ['$ sudo apt update', ('12 packages can be upgraded.', 'out'), '$ apt list --upgradable | head -2', ('openssl/noble-updates 3.0.13-0ubuntu3.5 …', 'out'), '$ sudo apt upgrade -y', ('12 upgraded, 0 newly installed …', 'acc')], title='riya@web01: ~', prompt='riya@web01:~$', size=6.6, step=17)
      + t(352, 36, 'Patch routine:', 9.4, 'acc', anchor='start', bold=True)
      + ''.join(t(352, 58 + k * 17, s, 8.8, 'ink2', anchor='start') for k, s in enumerate(['1 apt update', '2 list --upgradable', '3 upgrade', '4 autoremove', '5 check the log'])))
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Patch Tuesday</h2>
  <div class="story">
''' + puzzle('Riya runs <code>sudo apt upgrade</code> and gets “0 upgraded” although a security update was announced yesterday. Later, after <code>sudo apt remove nginx</code>, the folder <code>/etc/nginx</code> is still there, and when she reinstalls nginx her old broken config comes back. Finally <code>apt upgrade</code> says “The following packages have been kept back: linux-generic”. What is going on in each case?') + '''
    <p class="narration">Riya’s patch routine on a typical Ubuntu server.</p>
''' + scene('A terminal: apt update finds 12 upgradable packages, apt list --upgradable shows them, and apt upgrade installs them.', sc,
            '<tspan font-weight="700" class="s-acc">update</tspan> refreshes the list; <tspan font-weight="700" class="s-acc">upgrade</tspan> installs.') + '''
K> Why two commands, update and upgrade?
A> <code>update</code> only downloads the latest <b>lists</b> of what the repositories offer. <code>upgrade</code> compares those lists with what is installed and installs newer versions. Without update, apt does not know the new versions exist: the first puzzle.
R> And remove versus purge?
A> remove deletes the program but keeps its configuration files in /etc, in case you reinstall. purge deletes those too. Today: the whole daily toolkit, with simulations you can run without risk.
  </div>
</section>
'''

pic = ('<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="A supermarket analogy: apt update is reading this week’s catalogue, apt upgrade is replacing the items at home with newer ones from the catalogue, apt install buys something new, apt remove gives an item away but keeps its manual, apt purge also throws away the manual, apt autoremove clears accessories you no longer need.">'
       + label_box(14, 20, 196, 70, ['apt update', 'read the new catalogue'], 'blue', 9)
       + label_box(222, 20, 196, 70, ['apt upgrade', 'replace with newer items'], 'green', 9)
       + label_box(430, 20, 196, 70, ['apt install', 'buy something new'], 'green', 9)
       + label_box(14, 106, 196, 70, ['apt remove', 'give it away, keep the manual'], 'amber', 9)
       + label_box(222, 106, 196, 70, ['apt purge', 'also bin the manual (/etc)'], 'red', 9)
       + label_box(430, 106, 196, 70, ['apt autoremove', 'clear unused accessories'], 'violet', 9)
       + t(320, 196, 'Without a fresh catalogue (update), nothing new can be bought or upgraded.', 9.4, 'acc', bold=True)
       + '<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>')
lv = levels4('apt and dpkg at four depths', [
    ('v', 'No jargon: a catalogue and a shop', '      <p>Read the catalogue, then shop.</p>' + pic),
    ('b', 'What you will type', '''      <ul>
        <li><code>sudo apt update</code>, then <code>sudo apt upgrade</code>.</li>
        <li><code>sudo apt install htop</code>, <code>sudo apt remove htop</code>.</li>
        <li><code>apt search image editor</code>, <code>apt show gimp</code>.</li>
        <li><code>sudo apt autoremove</code> after removing things.</li>
      </ul>'''),
    ('i', 'Choices that matter', '''      <ul>
        <li><b>upgrade</b> never removes packages and does not add new ones; <b>full-upgrade</b> (dist-upgrade) may, which is needed for new kernels or changed dependencies (“kept back”).</li>
        <li><b>remove</b> keeps config files (status <code>rc</code>); <b>purge</b> deletes them.</li>
        <li><b>autoremove</b> removes packages that were installed only as dependencies and are no longer needed (marked “automatic”).</li>
        <li><code>apt-mark hold PKG</code> keeps a package at its version during upgrades; <code>unhold</code> releases it.</li>
        <li><code>-s</code> (simulate) shows what would happen without doing it, even as a normal user.</li>
        <li><code>apt</code> is for humans (progress bars, colours); <code>apt-get</code>/<code>apt-cache</code> have a stable output for scripts.</li>
      </ul>'''),
    ('a', 'Behind the screen: locks, phases and logs', '''      <ul>
        <li>apt takes a lock (<code>/var/lib/dpkg/lock-frontend</code>); “Could not get lock” means another apt (often unattended-upgrades) is running.</li>
        <li>An install has phases: download to <code>/var/cache/apt/archives</code>, unpack (dpkg), configure (postinst scripts, triggers like man-db and ldconfig).</li>
        <li>If configuration is interrupted, packages stay half-configured; <code>sudo dpkg --configure -a</code> resumes, <code>sudo apt -f install</code> repairs dependencies.</li>
        <li>Changed config files: on upgrade dpkg asks whether to keep yours or take the maintainer’s (<code>--force-confold</code>/<code>--force-confnew</code> in automation).</li>
        <li>Logs: <code>/var/log/apt/history.log</code> (what was installed/removed and by which command), <code>term.log</code> (the full output), <code>/var/log/dpkg.log</code> (every status change).</li>
        <li><code>unattended-upgrades</code> installs security updates automatically on Ubuntu servers (Lesson 19.3).</li>
      </ul>'''),
])
definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>apt and dpkg</h2>
''' + def_block(
    '<b>apt</b> is the high-level package manager of Debian and Ubuntu: it downloads repository indexes (<code>update</code>), resolves dependencies and installs, upgrades and removes packages from repositories. <b>dpkg</b> is the low-level tool underneath: it installs, configures and removes individual .deb files and maintains the database of installed packages. apt calls dpkg to do the actual work.',
    'apt plans and fetches; dpkg unpacks and records.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('update', 'Refresh repository lists.'),
    ('upgrade', 'Install newer versions.'),
    ('full-upgrade', 'Upgrade that may add/remove packages.'),
    ('remove / purge', 'Uninstall / also delete configs.'),
    ('autoremove', 'Remove unneeded dependencies.'),
    ('hold', 'Keep a package at its version.'),
    ('simulate (-s)', 'Show the plan, change nothing.'),
    ('conffile', 'A config file dpkg protects.'),
]) + '\n' + names('Where the names come from.', [
    ('apt', 'Advanced Package Tool', '1998.'),
    ('apt-get', 'the original front end', 'Stable for scripts.'),
    ('apt-cache', 'query the cache', 'search, policy.'),
    ('apt-mark', 'mark packages', 'hold, auto, manual.'),
    ('dist-upgrade', 'distribution upgrade', 'Now full-upgrade.'),
    ('kept back', 'held from upgrade', 'needs full-upgrade.'),
    ('rc', 'removed, config remains', 'dpkg -l status.'),
    ('unattended-upgrades', 'automatic updates', 'Ubuntu servers.'),
]) + '''

  <h3>Quick facts</h3>
''' + facts([
    ('Refresh', '<code>sudo apt update</code>'),
    ('Upgrade', '<code>sudo apt upgrade</code>'),
    ('Simulate', '<code>apt-get -s …</code>'),
    ('Remove all', '<code>sudo apt purge X</code>'),
    ('Pin', '<code>sudo apt-mark hold X</code>'),
    ('History', '<code>/var/log/apt/history.log</code>'),
]) + '\n' + lv + didyou('<code>apt moo</code> prints a cow. It is an old easter egg kept since apt-get’s early days: <code>apt-get moo</code> says “Have you mooed today?”') + '''
EXAM> “What is the difference between apt update and apt upgrade?” → update refreshes the package lists from the repositories; upgrade installs newer versions of installed packages using those lists.
''' + qc('Which command removes a package and its configuration files?', 'sudo apt purge PKG.') + mistake('apt upgrade without apt update',
    'sudo apt update && sudo apt upgrade',
    'apt only knows the versions in its last downloaded lists; without update it sees nothing new.') + mistake('apt remove when you want a clean reinstall',
    'sudo apt purge PKG && sudo apt install PKG   (back up /etc/PKG first)',
    'remove keeps /etc files, so a reinstall brings back the old (broken) config: the puzzle.') + '''
</section>
'''

types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and differences</span>
  <h2>All the everyday commands</h2>
''' + table(['Command', 'Does', 'Needs sudo', 'Script-stable twin'], [
    ['<code>apt update</code>', 'refresh lists', 'yes', '<code>apt-get update</code>'],
    ['<code>apt list --upgradable</code>', 'what can be upgraded', 'no', '<code>apt-get -s upgrade</code>'],
    ['<code>apt upgrade</code>', 'upgrade, no removals', 'yes', '<code>apt-get upgrade</code>'],
    ['<code>apt full-upgrade</code>', 'upgrade, may add/remove', 'yes', '<code>apt-get dist-upgrade</code>'],
    ['<code>apt install X</code>', 'install (or upgrade one)', 'yes', '<code>apt-get install</code>'],
    ['<code>apt install ./f.deb</code>', 'local file + deps', 'yes', '-'],
    ['<code>apt reinstall X</code>', 'reinstall', 'yes', '<code>apt-get install --reinstall</code>'],
    ['<code>apt remove X</code>', 'uninstall, keep configs', 'yes', '<code>apt-get remove</code>'],
    ['<code>apt purge X</code>', 'uninstall + configs', 'yes', '<code>apt-get purge</code>'],
    ['<code>apt autoremove</code>', 'unneeded dependencies', 'yes', '<code>apt-get autoremove</code>'],
    ['<code>apt search WORD</code>', 'find packages', 'no', '<code>apt-cache search</code>'],
    ['<code>apt show X</code>', 'details', 'no', '<code>apt-cache show</code>'],
    ['<code>apt policy X</code>', 'versions and sources', 'no', '<code>apt-cache policy</code>'],
    ['<code>apt-mark hold X</code>', 'freeze version', 'yes', '-'],
    ['<code>apt clean</code> / <code>autoclean</code>', 'empty the download cache', 'yes', '<code>apt-get clean</code>'],
], minw=560) + table(['dpkg', 'Does'], [
    ['<code>dpkg -i f.deb</code>', 'install a local file (no dependency download)'],
    ['<code>dpkg -r / -P X</code>', 'remove / purge'],
    ['<code>dpkg -l [PATTERN]</code>', 'list with status (ii, rc, iU, hi)'],
    ['<code>dpkg -L X</code> / <code>-S FILE</code>', 'files of / owner of'],
    ['<code>dpkg --configure -a</code>', 'finish interrupted configuration'],
    ['<code>dpkg --get-selections</code>', 'all packages and their selection state'],
], minw=420) + table(['', 'upgrade', 'full-upgrade'], [
    ['Installs newer versions', 'yes', 'yes'],
    ['Installs new packages (new dependencies)', 'no', 'yes'],
    ['Removes packages', 'never', 'if needed'],
    ['New kernel meta-packages', 'kept back', 'yes'],
    ['Risk', 'lowest', 'read the list first'],
], minw=420) + qc('What does “kept back” mean after apt upgrade?', 'The upgrade needs new packages or removals; upgrade refuses, full-upgrade (or apt install PKG) does it.') + '''
</section>
'''

cards = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Search, install, upgrade, remove and the logs, then used in every field</h2>
  <p id="commands">All outputs were recorded on our Ubuntu 24.04 build machine as riya. Changes need sudo and network, so we use apt’s <b>simulate</b> mode (<code>apt-get -s</code>), which prints the exact plan without changing anything, and our private dpkg folder (<code>pdpkg</code> = <code>dpkg --force-not-root --root=~/ap/root</code>) with a demo package <code>greet</code> 1.0 and 1.1 that depends on tmux and ships a config file <code>/etc/greet/greet.conf</code>. The build machine has never run apt update, so repository searches are in Run on your PC.</p>
''' + cmdcard_u(['finding and understanding packages before installing'],
               ['installing by guessing the name'])(
    'find', 'apt search · apt show · apt policy · apt list', 'find out about packages',
    '<code>apt search WORDS</code> searches names and descriptions; <code>apt show PKG</code> prints the details (version, size, depends, description); <code>apt policy PKG</code> shows installed and candidate versions and which repository they come from; <code>apt list --installed</code> / <code>--upgradable</code> list packages.',
    'apt search WORD   ·   apt show PKG   ·   apt policy PKG', 'safe',
    [('apt search', 'by words', 'discover'),
     ('apt search --names-only', 'name only', 'precise'),
     ('apt show', 'details', 'before install'),
     ('apt policy', 'versions, origin', 'which repo'),
     ('apt list --installed', 'what is here', 'inventory'),
     ('apt list --upgradable', 'updates waiting', 'patching'),
     ('apt-cache madison PKG', 'all available versions', 'downgrades')],
    dict(cmd="apt show tmux 2>/dev/null | grep -E '^(Package|Version|Installed-Size|Depends|Description):' | cut -c1-80\napt list --installed 2>/dev/null | grep '^tmux/'\napt-cache policy tmux | head -3", note='[installed,local] and no candidate source: our machine has no repository lists yet.'),
    [('sys', [
        dict(situation='Search the installed packages by description.', cmd="dpkg-query -W -f='${Package}\\t${binary:Summary}\\n' | grep -i 'terminal multiplexer'", why='Without apt update, searches only know installed packages.')]),
    ],
    anat=anatomy([('sudo', 'cmd', 'root for changes'), ('apt', 'opt', 'the tool'), ('install', 'arg', 'sub-command'), ('htop tree', 'arg', 'one or more packages')], 'apt SUBCOMMAND PACKAGES; queries need no sudo.')
) + cmdcard_u(['installing tools and services', 'vendor .deb files'],
               ['dpkg -i for files with dependencies', 'installing without reading the plan'])(
    'install', 'apt install X · apt install ./f.deb · -s · --no-install-recommends', 'install',
    '<code>sudo apt install PKG…</code> installs packages and their dependencies (and by default “recommended” packages). It prints the plan and asks Y/n. <code>./file.deb</code> installs a local file with its dependencies. <code>-s</code> prints the plan without doing it; <code>-y</code> answers yes in scripts; <code>--no-install-recommends</code> keeps servers minimal.',
    'sudo apt install PKG   ·   sudo apt install ./f.deb   ·   apt-get -s install PKG', 'change',
    [('apt install X Y', 'several', 'setup'),
     ('apt install ./f.deb', 'local file + deps', 'vendors'),
     ('apt install X=1.2-3', 'exact version', 'pinning'),
     ('-y', 'no prompt', 'scripts'),
     ('--no-install-recommends', 'minimal', 'servers, containers'),
     ('-s', 'simulate', 'preview'),
     ('apt reinstall X', 'repair files', 'broken install')],
    dict(setup=PK, cmd="cd ~/ap\napt-get -s install ./greet_1.0.deb 2>&1 | grep -E 'NEW|^  greet|^Inst|^Conf'\npdpkg -i greet_1.0.deb 2>&1 | grep -E 'depends|not installed' | head -2", expect='any', note='apt’s plan installs greet (tmux, its dependency, is already on the real system); our private dpkg root has no tmux, so dpkg alone refuses to configure it: the difference between apt and dpkg.'),
    [('devops', [
        dict(situation='Install in a script, quietly and minimally (shown).', cmd="echo 'export DEBIAN_FRONTEND=noninteractive'; echo 'sudo apt-get update -qq && sudo apt-get install -y -qq --no-install-recommends curl jq ca-certificates'", why='No questions, no extra packages, quiet output: the Dockerfile pattern.')]),
    ]
) + cmdcard_u(['monthly and security patching', 'planned upgrades'],
               ['full-upgrade on production without reading the plan', 'upgrading during peak hours'])(
    'upgrade', 'apt list --upgradable · apt upgrade · apt full-upgrade · apt-mark hold', 'upgrade safely',
    'After <code>apt update</code>, <code>apt list --upgradable</code> shows what is waiting. <code>apt upgrade</code> installs newer versions but never removes anything; <code>apt full-upgrade</code> may add or remove packages (kernels, changed dependencies). <code>apt-mark hold PKG</code> excludes a package; <code>apt-get -s upgrade</code> shows the plan.',
    'sudo apt update && apt list --upgradable && sudo apt upgrade', 'change',
    [('apt list --upgradable', 'preview', 'always'),
     ('apt upgrade', 'safe upgrade', 'routine'),
     ('apt full-upgrade', 'with adds/removals', 'kernels'),
     ('apt install --only-upgrade X', 'one package', 'urgent fix'),
     ('apt-mark hold X', 'freeze', 'databases'),
     ('apt-mark showhold', 'list held', 'audit'),
     ('-s', 'simulate', 'change review')],
    dict(setup=PK, cmd="cd ~/ap\npdpkg -i greet_1.0.deb > /dev/null 2>&1; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1\npdpkg -l greet | tail -1 | awk '{print $1, $2, $3}'\npdpkg --force-depends -i greet_1.1.deb 2>&1 | grep -E 'Unpacking|Setting'\n~/ap/root/usr/local/bin/greet\napt-get -s upgrade 2>&1 | tail -1", note='Installing a newer .deb is an upgrade (1.0 → 1.1). apt-get -s upgrade on the real system: nothing, because no lists were updated (the first puzzle).'),
    [('sys', [
        dict(situation='Hold a package (in the private root).', setup=PK, cmd="cd ~/ap; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1\necho 'greet hold' | pdpkg --set-selections; pdpkg -l greet | tail -1 | cut -c1-3\npdpkg --get-selections greet", why='hi = hold + installed. apt-mark hold does exactly this on the real system.')]),
    ]
) + cmdcard_u(['uninstalling', 'cleaning disk space', 'fresh reinstalls'],
               ['autoremove without reading the list', 'purge when you still need the config'])(
    'remove', 'apt remove · apt purge · apt autoremove · apt clean', 'remove, purge, clean up',
    '<code>remove</code> deletes the package’s files but keeps its config files (dpkg status <code>rc</code>). <code>purge</code> deletes those too. <code>autoremove</code> removes automatically installed dependencies nobody needs any more. <code>clean</code> empties the downloaded .deb cache. Always read the “will be REMOVED” list: removing a library removes everything that needs it.',
    'sudo apt remove X   ·   sudo apt purge X   ·   sudo apt autoremove', 'danger',
    [('apt remove X', 'keep configs', 'may reinstall'),
     ('apt purge X', 'delete configs', 'clean slate'),
     ('dpkg -l | grep ^rc', 'leftover configs', 'audit'),
     ('apt autoremove', 'unused dependencies', 'tidy'),
     ('apt autoremove --purge', 'and their configs', 'deep clean'),
     ('apt clean', 'empty the cache', 'disk space'),
     ('-s', 'simulate', 'always first')],
    dict(setup=PK, cmd="cd ~/ap; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1\npdpkg -r greet > /dev/null 2>&1; pdpkg -l greet | tail -1 | awk '{print $1, $2}'; ls ~/ap/root/etc/greet\npdpkg -P greet > /dev/null 2>&1; pdpkg -l greet 2>&1 | tail -1 | cut -c1-40; ls ~/ap/root/etc/greet 2>&1 | head -1", expect='any', note='The puzzle: after remove the status is rc and greet.conf is still there; purge deleted it.'),
    [('qa', [
        dict(situation='Read the plan: removing a library removes its users.', cmd="apt-get -s remove libevent-core-2.1-7t64 2>&1 | sed -n '/REMOVED/,/upgraded/p'", why='tmux needs that library, so it would go too. Always read before typing Y.')]),
     ('sys', [
        dict(situation='How big is the download cache?', cmd="du -sh /var/cache/apt/archives 2>/dev/null | cut -f1 | sed 's/^/apt cache: /'; ls /var/cache/apt/archives/*.deb 2>/dev/null | wc -l | sed 's/^/cached .deb files: /'", why='apt clean empties it on servers short of space.')]),
    ]
) + cmdcard_u(['“what changed last night?”', 'audits and rollbacks'],
               ['guessing what an upgrade did'])(
    'logs', '/var/log/apt/history.log · term.log · /var/log/dpkg.log', 'the logs',
    '<code>history.log</code> records each apt run: start time, the command line, and what was installed, upgraded or removed. <code>term.log</code> has the full screen output (root/adm only). <code>/var/log/dpkg.log</code> records every status change of every package. Rotated copies are gzip-compressed (<code>zgrep</code>).',
    'grep -A4 Start-Date /var/log/apt/history.log | tail   ·   grep " install " /var/log/dpkg.log', 'safe',
    [('history.log', 'apt sessions', 'who did what'),
     ('Commandline:', 'the exact command', 'audit'),
     ('Upgrade: / Install: / Remove:', 'what changed', 'rollbacks'),
     ('dpkg.log', 'every status change', 'detail'),
     ('zgrep … *.gz', 'older logs', 'history'),
     ('term.log', 'full output', 'errors')],
    dict(cmd="grep -c '^Start-Date' /var/log/apt/history.log | sed 's/^/apt sessions logged: /'\ngrep -E '^(Start-Date|Commandline)' /var/log/apt/history.log | tail -2 | cut -c1-80\ngrep ' install ' /var/log/dpkg.log | tail -2 | awk '{print $1, $2, $3, $4, $5}'", note='The image was built by apt-get install commands: the log shows when and how.'),
    []
) + undo('Almost everything apt does can be undone with another apt command.', [
    ('Removed the wrong package:', '<code>sudo apt install PKG</code> (configs were kept by remove).'),
    ('Purged a config you needed:', 'restore /etc from backup; reinstall gives the default config.'),
    ('An upgrade broke something:', 'find the old version in history.log; <code>sudo apt install PKG=OLDVERSION</code> and hold it.'),
    ('Interrupted install:', '<code>sudo dpkg --configure -a</code>, then <code>sudo apt -f install</code>.'),
]) + errors('Errors students see most. Each was really produced on our build machine, with its exit status.', [
    dict(cmd='apt install tree', meaning='Changes need root.', fix='sudo apt install tree.'),
    dict(cmd='apt-get -s install nosuchpkg', meaning='Unknown package (or no apt update yet).', fix='apt update; apt search WORD.'),
    dict(cmd='apt-mark hold tmux', meaning='Marking needs root.', fix='sudo apt-mark hold tmux.'),
    dict(setup=PK, cmd='cd ~/ap; pdpkg -i greet_1.0.deb', meaning='Dependency missing in this (private) system.', fix='sudo apt install ./greet_1.0.deb fetches it.'),
]) + qc('Which file tells you which command installed a package last week?', '/var/log/apt/history.log (Commandline: lines).') + '''
'''
cards = cards + '</section>\n'

def plan(k):
    rows = [('installed', 'openssl 3.0.13-0ubuntu3.4', 'card'), ('lists (after update)', 'openssl 3.0.13-0ubuntu3.5', 'blue'), ('plan', 'Upgrade: openssl, libssl3', 'amber'), ('done', 'openssl 3.0.13-0ubuntu3.5', 'green')]
    return ''.join(label_box(14, 12 + i * 40, 330, 32, [f'{a}: {b}'], c if i <= k else 'card', 8) for i, (a, b, c) in enumerate(rows))
see_cmds = [['$ apt policy openssl', ('Installed: 3.0.13-0ubuntu3.4', 'out')], ['$ sudo apt update', ('1 package can be upgraded', 'out')], ['$ apt list --upgradable', ('openssl/noble-security 3.5', 'out')], ['$ sudo apt upgrade', ('Setting up openssl (…3.5)', 'acc')]]
see = [term(14, 16, 332, 116, c, title='riya@web01: ~', prompt='$', size=7.2) + cap(n, '', 'card', y=150, h=34)
       for c, n in zip(see_cmds, ['Installed.', 'Update.', 'Preview.', 'Upgrade.'])]
behind = [plan(k) for k in range(4)]
two = anim_two('update, then upgrade', 'Behind the screen: installed vs candidate versions',
               'A terminal: policy shows the installed openssl, update finds a newer one, list --upgradable shows it, upgrade installs it.',
               'Four boxes: installed version, the newer version in the refreshed lists, the upgrade plan, and the result.', see, behind,
               ['Installed.', 'update.', 'list.', 'upgrade.'],
               ['now', 'update', 'list', 'upgrade'])

def rm(k):
    o = label_box(14, 20, 150, 40, ['/usr/local/bin/greet'], ['green', 'card', 'card'][k], 8.4)
    o += label_box(196, 20, 150, 40, ['/etc/greet/greet.conf'], ['green', 'amber', 'card'][k], 8.4)
    o += t(180, 100, ['installed (ii)', 'apt remove → rc: config kept', 'apt purge → gone'][k], 9.6, ['green', 'amber', 'red'][k], bold=True)
    return o
s1 = anim_one('Animated example', 'remove versus purge',
              'What stays on disk after each.',
              'apt remove · apt purge', 'Program file and config file: after remove only the config remains (status rc); after purge both are gone.', [rm(k) for k in range(3)],
              ['ii.', 'rc.', 'gone.'], hid='scenario-purge')

dx = dissect('Layer by layer: what apt touches',
    'Each layer has a real command and output from our build machine.', [
    dict(key='lists', name='Lists', sub='/var/lib/apt/lists', why='What exists.', how='apt update fills it.', impl='Signed indexes.', used='upgrade, search.',
         cmd="ls /var/lib/apt/lists/ | grep -v -E '^(lock|partial|auxfiles)$' | wc -l | sed 's/^/index files here: /'"),
    dict(key='cache', name='Cache', sub='/var/cache/apt', why='Downloads.', how='.deb files.', impl='apt clean empties.', used='Offline reinstall.',
         cmd="ls /var/cache/apt/archives/ | head -3"),
    dict(key='lock', name='Locks', sub='one apt at a time', why='Safety.', how='Lock files.', impl='fcntl locks.', used='“Could not get lock”.',
         cmd="ls -l /var/lib/dpkg/lock* 2>/dev/null | awk '{print $1, $3, $NF}'"),
    dict(key='mark', name='Auto vs manual', sub='extended_states', why='autoremove.', how='Auto-Installed: 1.', impl='/var/lib/apt/extended_states.', used='Cleanup.',
         cmd="grep -c 'Auto-Installed: 1' /var/lib/apt/extended_states 2>/dev/null | sed 's/^/packages marked automatic: /' || echo 'no extended_states file'"),
], hint='From lists to locks. Click a layer.')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>update then upgrade, and remove versus purge</h2>
''' + two + s1 + dx + qc('Why is the list of index files empty on our build machine?', 'apt update has never been run there, so apt only knows the installed packages.') + '''
</section>
'''

VAR = variations('Sixteen more apt and dpkg commands. All were really run on our build machine (queries and simulations, plus our private dpkg folder).', [
    ('Queries', [
        dict(title='apt-get -s: what would upgrade?', cmd="apt-get -s upgrade 2>&1 | tail -1", why='The script-friendly preview.'),
        dict(title='Leftover configs (rc)', cmd="dpkg -l | awk '/^rc/{print $2}' | wc -l | sed 's/^/packages with leftover configs: /'", why='Purge candidates.'),
        dict(title='Held packages', cmd="apt-mark showhold | wc -l | sed 's/^/held: /'", why='Nothing held here.'),
        dict(title='Selections (backup the package list)', cmd="dpkg --get-selections | head -2; dpkg --get-selections | wc -l", why='Save this to rebuild a server with the same packages.'),
        dict(title='Installed size of one package', cmd="apt show tmux 2>/dev/null | grep Installed-Size", why='Before installing on small disks.'),
        dict(title='Description in one line', cmd="dpkg-query -W -f='${binary:Summary}\\n' tmux", why='What is this package?'),
        dict(title='Why is a package installed?', cmd="apt-cache rdepends --installed libevent-core-2.1-7t64 | tail -n +3", why='Who needs it: tmux.'),
        dict(title='Every package from one source package', cmd="dpkg-query -W -f='${source:Package} ${Package}\\n' | awk '$1==\"openssl\"' | head -3", why='One fix often updates several binary packages.'),
    ]),
    ('Simulations', [
        dict(title='Remove with purge, simulated', cmd="apt-get -s purge tmux 2>&1 | grep -E '^Purg|REMOVED' | head -2", why='Purg = purge.'),
        dict(title='Autoremove, simulated', cmd="apt-get -s autoremove 2>&1 | tail -1", why='Nothing unused here.'),
        dict(title='Install a local .deb, simulated', setup=PK, cmd="cd ~/ap; apt-get -s install ./greet_1.1.deb 2>&1 | grep -E '^(Inst|Conf)'", why='apt accepts a path starting with ./'),
    ]),
    ('Private dpkg root', [
        dict(title='Status letters', setup=PK, cmd="cd ~/ap; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1; pdpkg -l | awk 'NR<=3 || /greet/' | cut -c1-60", why='First letter: desired (i install, r remove, h hold); second: status (i installed, c config-files, U unpacked).'),
        dict(title='Changed config file is kept on upgrade', setup=PK, cmd="cd ~/ap; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1; echo 'colour=red' > ~/ap/root/etc/greet/greet.conf; pdpkg --force-depends --force-confold -i greet_1.1.deb > /dev/null 2>&1; cat ~/ap/root/etc/greet/greet.conf", why='1.1 ships a new default (colour=green), but you edited the file: --force-confold keeps yours (dpkg would ask interactively).'),
        dict(title='Take the maintainer’s version instead', setup=PK, cmd="cd ~/ap; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1; echo 'colour=red' > ~/ap/root/etc/greet/greet.conf; pdpkg --force-depends --force-confnew -i greet_1.1.deb > /dev/null 2>&1; cat ~/ap/root/etc/greet/greet.conf; ls ~/ap/root/etc/greet/", why='--force-confnew installs the maintainer’s new default and saves yours as .dpkg-old.'),
        dict(title='Finish interrupted configuration', setup=PK, cmd="cd ~/ap; pdpkg --force-depends --unpack greet_1.0.deb > /dev/null 2>&1; pdpkg -l greet | tail -1 | cut -c1-3; pdpkg --force-depends --configure -a > /dev/null 2>&1; pdpkg -l greet | tail -1 | cut -c1-3", why='iU → ii: what dpkg --configure -a does after a crash.'),
        dict(title='The private dpkg log', setup=PK, cmd="cd ~/ap; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1; grep -E ' (install|status installed) ' ~/ap/dpkg.log | awk '{print $3, $4, $5, $6}'", why='The same format as /var/log/dpkg.log.'),
    ]),
])

uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>apt at work</h2>
''' + usecase(label_box(14, 22, 92, 46, ['patching', 'monthly'], 'blue', 8.6), '1. Patch windows',
              'Ops teams run update, list --upgradable, upgrade on staging first, then production, and record history.log.', ['Staging', '*apt upgrade', 'production']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['hold', 'databases'], 'red', 8.6), '2. Protecting critical versions',
    'PostgreSQL or a kernel is held during routine patching and upgraded in a planned window.', ['hold', '*routine upgrades', 'planned upgrade']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['Dockerfile', 'images'], 'amber', 8.6), '3. Container images',
    'Dockerfiles use apt-get update && apt-get install -y --no-install-recommends … && rm -rf /var/lib/apt/lists/* to keep images small.', ['Base', '*one RUN line', 'small image']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['selections', 'rebuilds'], 'green', 8.6), '4. Rebuilding a server',
    'dpkg --get-selections on the old server, dpkg --set-selections and apt-get dselect-upgrade on the new one.', ['Old box', '*selections', 'same packages']) + '\n' + usecase(
    label_box(14, 22, 92, 46, ['unattended', 'security'], 'violet', 8.6), '5. Automatic security updates',
    'unattended-upgrades applies security fixes nightly; history.log shows what it did (Lesson 19.3).', ['Night', '*unattended-upgrades', 'patched']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Small, useful commands. All really run on our build machine.', [
    dict(level='b', title='Is it installed, which version?', scenario='Quick check.', cmd="apt list --installed 2>/dev/null | grep '^bash/'", explain='apt list.'),
    dict(level='b', title='What would an upgrade do?', scenario='Before patching.', cmd="apt-get -s upgrade 2>&1 | tail -1", explain='-s simulates.'),
    dict(level='i', title='Configs left behind', scenario='Tidy.', cmd="echo \"leftover configs: $(dpkg -l | awk '/^rc/' | wc -l)\"", explain='rc status.'),
    dict(level='i', title='Last apt command', scenario='What happened?', cmd="grep '^Commandline' /var/log/apt/history.log | tail -1 | cut -c1-60", explain='history.log.'),
    dict(level='a', title='Save the package list', scenario='Rebuild later.', cmd="dpkg --get-selections > /tmp/pkgs-$$.txt; wc -l < /tmp/pkgs-$$.txt; rm /tmp/pkgs-$$.txt", explain='--get-selections.'),
], extra=build_up('a package’s life', 'Riya walks greet through install, upgrade, remove and purge in the private root.', PK, [
    ("cd ~/ap; pdpkg --force-depends -i greet_1.0.deb > /dev/null 2>&1; pdpkg -l greet | tail -1 | awk '{print $1, $2, $3}'", '1. Install 1.0 (ii).'),
    ("cd ~/ap; pdpkg --force-depends -i greet_1.1.deb > /dev/null 2>&1; pdpkg -l greet | tail -1 | awk '{print $1, $2, $3}'", '2. Upgrade to 1.1.'),
    ("cd ~/ap; pdpkg -r greet > /dev/null 2>&1; pdpkg -l greet | tail -1 | awk '{print $1, $2}'; ls ~/ap/root/etc/greet", '3. Remove: rc, config still there.'),
    ("cd ~/ap; pdpkg -P greet > /dev/null 2>&1; ls ~/ap/root/etc/greet 2>&1 | head -1", '4. Purge: config gone.'),
], cumulative=True, expect='any')) + VAR + which('Choosing the right tool.', [
    ('Install from repos', 'apt install', 'Dependencies.', 'dpkg -i.'),
    ('Local .deb', 'apt install ./f.deb', 'Dependencies.', 'dpkg -i then guessing.'),
    ('Scripts', 'apt-get / apt-cache', 'Stable output.', 'apt (warns: unstable CLI).'),
    ('Preview anything', '-s', 'Exact plan.', 'Trying on production.'),
    ('Freeze a version', 'apt-mark hold', 'Simple.', 'Editing files by hand.'),
    ('Repair', 'dpkg --configure -a; apt -f install', 'Finishes / fixes.', 'Reinstalling the OS.'),
]) + keys('Handy forms.', [
    ('sudo apt update && sudo apt upgrade', 'patch', 'routine'),
    ('apt list --upgradable', 'preview', 'before'),
    ('sudo apt purge X', 'clean uninstall', 'reinstalls'),
    ('sudo apt autoremove', 'tidy', 'after removals'),
    ('sudo apt-mark hold X', 'freeze', 'critical'),
    ('apt-get -s …', 'simulate', 'always'),
]) + scriptit('patchreport.sh', 'A safe patch report: what is installed, what would be upgraded (simulated), held packages, leftover configs, cache size and the last three apt sessions from the log. Read-only: it changes nothing.',
'''echo "== $(hostname) $(grep -m1 PRETTY /etc/os-release | cut -d'"' -f2)"
echo "installed packages: $(dpkg -l | grep -c '^ii')"
up=$(apt-get -s upgrade 2>/dev/null | grep -c '^Inst')
echo "would upgrade now:  $up (run 'sudo apt update' first for fresh lists)"
echo "held:               $(apt-mark showhold | wc -l)"
echo "leftover configs:   $(dpkg -l | grep -c '^rc')"
echo "download cache:     $(du -sh /var/cache/apt/archives 2>/dev/null | cut -f1)"
echo "last apt sessions:"
grep -E '^(Start-Date|Commandline)' /var/log/apt/history.log 2>/dev/null | tail -6 | paste - - | cut -c13-90 | sed 's/^/  /' ''',
'<p>Read-only; safe to run anywhere.</p>', expect='any') + puzzle_answer('<b>1.</b> <code>apt upgrade</code> uses the package lists from the last <code>apt update</code>; without a fresh update apt did not know the new version existed. Always <code>sudo apt update &amp;&amp; sudo apt upgrade</code>. <b>2.</b> <code>apt remove</code> keeps configuration files (status <code>rc</code>), so the reinstall found the old config. Use <code>sudo apt purge nginx</code> (after saving what you need from /etc/nginx), then install again. <b>3.</b> “Kept back”: the new linux-generic needs new packages (a new kernel), which plain upgrade never adds. Use <code>sudo apt full-upgrade</code> (or <code>sudo apt install linux-generic</code>) in a maintenance window, then reboot.') + qc('Which apt option shows the plan without changing anything?', '-s (simulate), e.g. apt-get -s upgrade.') + '''
</section>
'''

_sh.run_sh('rm -rf ~/ap', 'any')
body = (HOOK + ROAD + cmap + story.replace('  <div class="story">', before('<a href="../01-packages-and-repositories-how-software/">Lesson 14.1</a> (packages and repositories).') + '  <div class="story">', 1)
        + '<section class="part part--decide">' + DECIDE + '</section>\n' + definition + types + cards + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
