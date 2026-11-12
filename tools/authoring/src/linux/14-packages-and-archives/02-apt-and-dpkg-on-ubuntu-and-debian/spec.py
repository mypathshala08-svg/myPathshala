import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='14-packages-and-archives', lesson='02-apt-and-dpkg-on-ubuntu-and-debian', n='14.2',
    module_label='Module 14 · Software packages and archives',
    title='apt and dpkg on Ubuntu and Debian: update, upgrade, install, remove, purge, hold',
    desc='Everyday package management on Ubuntu and Debian: apt update vs upgrade, full-upgrade and “kept back”, install (also ./file.deb, versions, --no-install-recommends), search, show, policy, list --upgradable, remove vs purge vs autoremove, clean, apt-mark hold, simulate with -s; dpkg -i, -r, -P, -l status letters, --configure -a, --get-selections, conffile handling (confold/confnew); logs in /var/log/apt/history.log and dpkg.log; real outputs and simulations, 30+ examples.',
    og_desc='apt and dpkg explained with real runs and simulations: update vs upgrade, remove vs purge, hold, logs and fixing broken installs.',
    minutes=40, level='Beginner → Advanced',
    lead='The daily apt and dpkg toolkit on Ubuntu and Debian: refresh, find, install, upgrade safely, remove cleanly, freeze versions, repair, and read the logs afterwards.',
    chips=['update vs upgrade animated', 'remove vs purge', 'Simulate before acting', 'Practice lab with checker', 'Real outputs'],
)

MAIN = """# A pretend package list: name, installed, available
cat > pkgs.txt <<'EOF'
openssl 3.0.13-0ubuntu3.4 3.0.13-0ubuntu3.5
tmux 3.4-1ubuntu0.2 3.4-1ubuntu0.2
curl 8.5.0-2ubuntu10.5 8.5.0-2ubuntu10.6
EOF
echo "== like 'apt list --upgradable' =="
awk '$2 != $3 {print $1 ": " $2 " -> " $3}' pkgs.txt
echo "== count =="
awk '$2 != $3' pkgs.txt | wc -l
"""

RUN = dict(
    heading='The idea of apt list --upgradable',
    intro='<p>The browser has no apt, so this compares installed and available versions in a small table, which is what apt does after update. Real apt runs and simulations are above.</p>',
    code=MAIN,
    anno=[("$2 != $3", 'Installed version differs from the candidate.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Which packages would be upgraded?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which version is newer? sort -V knows.',
             code="printf '%s\\n' 3.0.13-0ubuntu3.5 3.0.13-0ubuntu3.10 | sort -V | tail -1\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> text sort says 3.5 is newer than 3.10. Use sort -V.',
             code="printf '%s\\n' 3.10 3.5 | sort | tail -1\n"),
        dict(label='4 · Your turn', hint='Mark tmux as “hold” and skip held packages in the upgrade list.',
             code="printf 'openssl 1 2\\ntmux 1 2\\n' > p.txt\necho tmux > held.txt\nawk 'NR==FNR{h[$1]; next} !($1 in h) && $2!=$3 {print $1}' held.txt p.txt\n"),
        dict(label='5 · Challenge', hint='Parse history-log style lines: how many installs and upgrades?',
             code="printf '%s\\n' 'Install: jq:amd64 (1.7)' 'Upgrade: curl:amd64 (8.5.0-1, 8.5.0-2)' 'Install: tree:amd64 (2.1)' > h.log\ncut -d: -f1 h.log | sort | uniq -c\n"),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the real routine',
    intro='<p>These need sudo and network, so they are <b>typical</b> outputs from an Ubuntu 24.04 PC, except the last one.</p>',
    items=[
        dict(title='1 · Patch routine', cmd='sudo apt update\napt list --upgradable\nsudo apt upgrade', output='12 packages can be upgraded. Run \'apt list --upgradable\' to see them.\nopenssl/noble-updates,noble-security 3.0.13-0ubuntu3.5 amd64 [upgradable from: 3.0.13-0ubuntu3.4]\n…\n12 upgraded, 0 newly installed, 0 to remove and 1 not upgraded.', note='Typical.'),
        dict(title='2 · Kept back', cmd='sudo apt upgrade', output='The following packages have been kept back:\n  linux-generic linux-headers-generic linux-image-generic\n0 upgraded, 0 newly installed, 0 to remove and 3 not upgraded.', note='Typical: use sudo apt full-upgrade in a maintenance window.'),
        dict(title='3 · Hold and release', cmd='sudo apt-mark hold postgresql-16\napt-mark showhold\nsudo apt-mark unhold postgresql-16', output='postgresql-16 set on hold.\npostgresql-16\nCanceled hold on postgresql-16.', note='Typical.'),
        dict(title='4 · Simulated upgrade here', cmd='apt-get -s upgrade | tail -1', output=pc('apt-get -s upgrade 2>/dev/null | tail -1'), note='Recorded (no lists on our build machine).'),
    ],
)

TRACE = dict(
    heading='Choosing what to upgrade, line by line',
    intro='<p>Step through a tiny upgrade planner.</p>',
    code='''installed=3.0.13-0ubuntu3.4
candidate=3.0.13-0ubuntu3.5
held=no
newest=$(printf '%s\\n' "$installed" "$candidate" | sort -V | tail -1)
[ "$held" = no ] && [ "$newest" != "$installed" ] && plan=upgrade || plan=keep
echo "openssl: $plan ($installed -> $candidate)"
''',
    notes={4: 'Version-aware sort.', 5: 'Upgrade only if newer and not held.'},
)

WORKED_INTRO = 'Three apt tasks from real jobs.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Is a security fix installed?',
         problem='<p>Check whether the installed openssl version is at least the fixed version from an advisory.</p>',
         inp='two versions', approach=['dpkg --compare-versions.'],
         code='''installed=$(dpkg-query -W -f='${Version}' openssl 2>/dev/null || echo 0)
fixed=3.0.13-0ubuntu3.5
if dpkg --compare-versions "$installed" ge "$fixed"; then echo "openssl $installed: patched"; else echo "openssl $installed: VULNERABLE (need $fixed)"; fi
''', notes={3: 'Debian version rules, not text.'}, tryit='Check curl as well.'),
    dict(level='i', tag='DevOps', title='Rebuild a server’s package set',
         problem='<p>Save the manual package list of one server for another (here: show the commands and count).</p>',
         inp='apt-mark showmanual', approach=['Save the list.', 'apt install on the new server.'],
         code='''apt-mark showmanual > manual.txt
echo "packages to reinstall: $(wc -l < manual.txt)"
echo "on the new server: xargs -a manual.txt sudo apt install -y"
''', notes={1: 'Only what was installed on purpose.'}, tryit='Exclude packages starting with lib.'),
    dict(level='a', tag='SRE', title='What changed in the last patch?',
         problem='<p>From an apt history log, list packages upgraded in the last session.</p>',
         inp='history.log', approach=['awk by paragraph.', 'split the Upgrade line.'],
         code='''tail -n 30 /var/log/apt/history.log | awk -v RS= 'END{print}' | grep -E '^(Start-Date|Commandline|Install|Upgrade|Remove)' | cut -c1-90
''', notes={1: 'Last paragraph = last session.'}, tryit='Count the packages in the Install line.'),
]

QUIZ = mix([
    dict(q='apt update…', options=['installs updates', 'refreshes package lists', 'upgrades the kernel', 'removes old packages'], answer=1, why='Lists only.'),
    dict(q='Upgrade that may remove or add packages:', options=['apt upgrade', 'apt full-upgrade', 'apt install', 'apt update'], answer=1, why='full-upgrade.'),
    dict(q='Remove a package AND its config files:', options=['apt remove', 'apt purge', 'apt clean', 'apt autoremove'], answer=1, why='purge.'),
    dict(q='Remove dependencies nobody needs:', options=['apt autoremove', 'apt clean', 'dpkg -r', 'apt purge'], answer=0, why='autoremove.'),
    dict(q='Keep a package at its version:', options=['apt-mark hold', 'apt lock', 'dpkg -h', 'apt pin'], answer=0, why='hold.'),
    dict(q='See the plan without changing anything:', options=['-y', '-s', '-q', '-f'], answer=1, why='simulate.'),
    dict(q='dpkg status rc means…', options=['running', 'removed, config remains', 'reinstall needed', 'recently changed'], answer=1, why='purge candidate.'),
    dict(q='Which log shows the apt command lines used?', options=['/var/log/syslog', '/var/log/apt/history.log', '/var/log/auth.log', '/var/log/dmesg'], answer=1, why='Commandline:.'),
])

REVISION = [
    'sudo apt update (lists) then apt list --upgradable then sudo apt upgrade; full-upgrade when “kept back”.',
    'install X / ./f.deb / X=VERSION; -y in scripts; --no-install-recommends for minimal servers.',
    'remove keeps configs (rc); purge deletes them; autoremove removes unused dependencies; clean empties the cache.',
    'apt-mark hold/unhold/showhold; apt-get -s simulates anything as a normal user.',
    'dpkg -i/-r/-P/-l/-L/-S; dpkg --configure -a and apt -f install to repair; --get-selections to save the list.',
    'Logs: /var/log/apt/history.log (sessions, command lines), term.log, /var/log/dpkg.log.',
]

FAQ = [
    ('What is the difference between apt update and apt upgrade?', 'update refreshes the package lists; upgrade installs newer versions using those lists.'),
    ('What is the difference between apt remove and apt purge?', 'remove keeps configuration files; purge deletes them too.'),
    ('What does apt autoremove do?', 'Removes packages that were installed as dependencies and are no longer needed.'),
    ('Why are packages “kept back”?', 'Their upgrade needs new packages or removals; use apt full-upgrade.'),
    ('How do I stop a package from being upgraded?', 'sudo apt-mark hold PACKAGE.'),
    ('How do I fix a broken apt install?', 'sudo dpkg --configure -a, then sudo apt -f install.'),
    ('Where can I see what apt installed?', '/var/log/apt/history.log and /var/log/dpkg.log.'),
]

PRACTICE_INTRO = 'Small apt and dpkg tasks. Expected outputs come from real runs on Ubuntu 24.04.'
PROBLEMS = [
    dict(level='easy', title='Installed?', stmt='Print the tmux line from apt list --installed.', inp='nothing', code="apt list --installed 2>/dev/null | grep '^tmux/'\n", explain='tmux/now 3.4-1ubuntu0.2 …'),
    dict(level='easy', title='Simulate', stmt='Simulate removing tmux and print the summary line.', inp='nothing', code="apt-get -s remove tmux 2>/dev/null | grep 'to remove'\n", explain='1 to remove.'),
    dict(level='easy', title='Held', stmt='How many packages are on hold?', inp='nothing', code="apt-mark showhold | wc -l\n", explain='0.'),
    dict(level='medium', title='Compare', stmt='Is 8.5.0-2ubuntu10.6 newer than 8.5.0-2ubuntu10.5?', inp='versions', code="dpkg --compare-versions 8.5.0-2ubuntu10.6 gt 8.5.0-2ubuntu10.5 && echo newer\n", explain='newer.'),
    dict(level='medium', title='Dependents', stmt='Which installed package needs libevent-core-2.1-7t64?', inp='nothing', code="apt-cache rdepends --installed libevent-core-2.1-7t64 | tail -n +3\n", explain='tmux.'),
    dict(level='medium', title='Sessions', stmt='How many apt sessions are in history.log?', inp='nothing', code="grep -c '^Start-Date' /var/log/apt/history.log\n", explain='109 here.'),
    dict(level='business', title='Selections', stmt='Count packages in “install” state.', inp='nothing', code="dpkg --get-selections | awk '$2==\"install\"' | wc -l\n", explain='1044.'),
    dict(level='business', title='Summary', stmt='One-line summary of the package called tmux.', inp='nothing', code="dpkg-query -W -f='${Package} ${Version}: ${binary:Summary}\\n' tmux\n", explain='tmux 3.4-1ubuntu0.2: terminal multiplexer.'),
]

SCN_INTRO = 'Interview questions about apt and dpkg, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you update an Ubuntu server?”', 'Very common.', 'steps?',
        '''<ul>
          <li>sudo apt update; apt list --upgradable; sudo apt upgrade.</li>
          <li>Reboot if the kernel changed (/var/run/reboot-required).</li>
          <li>sudo apt autoremove afterwards.</li>
        </ul>''', 'only apt upgrade.') +
    scn('Service company', 'Junior', '“Could not get lock /var/lib/dpkg/lock-frontend”', 'Right after boot.', 'why?',
        '''<ol>
          <li>Another apt is running (often unattended-upgrades).</li>
          <li>Wait; check with ps aux | grep -E 'apt|dpkg'.</li>
          <li>Never delete the lock while apt runs.</li>
        </ol>''', 'rm the lock files.') +
    scn('Product company', 'Mid-level', 'An upgrade broke the app', 'libfoo changed.', 'roll back?',
        '''<ul>
          <li>history.log: which version before.</li>
          <li>sudo apt install libfoo=OLDVER (from the cache or repo), then hold.</li>
          <li>Fix forward; test upgrades on staging first.</li>
        </ul>''', 'reinstalling the OS.') +
    scn('Platform', 'Senior', 'Patch 500 Ubuntu servers safely', 'Mixed roles.', 'process?',
        '''<ul>
          <li>Staged rings (canary → 10% → all) with Ansible / Landscape.</li>
          <li>unattended-upgrades for security; holds for databases.</li>
          <li>Reboot orchestration and monitoring between rings.</li>
        </ul>''', 'apt upgrade -y everywhere at once.')
) + interview([
    ('apt vs apt-get?', 'apt for people; apt-get/apt-cache stable for scripts.'),
    ('What is --no-install-recommends?', 'Skip recommended (optional) packages.'),
    ('How to install a specific version?', 'apt install PKG=VERSION.'),
    ('What does apt clean do?', 'Deletes cached .deb files.'),
    ('dpkg --configure -a?', 'Finish configuring unpacked packages.'),
    ('confold vs confnew?', 'Keep your config vs take the maintainer’s.'),
    ('How to check if a reboot is needed?', '/var/run/reboot-required exists.'),
], [
    ('LFCS', 'Manage software with apt and dpkg.'),
    ('Ubuntu / Canonical certifications', 'apt administration.'),
    ('CompTIA Linux+', 'apt, dpkg commands.'),
]) + distro('apt is the Debian family; the others use their own tools (14.3).', [
    ('Refresh', 'apt update', 'dnf makecache (automatic)', 'brew update', 'winget source update'),
    ('Upgrade all', 'apt upgrade', 'dnf upgrade', 'brew upgrade', 'winget upgrade --all'),
    ('Remove + configs', 'apt purge', 'dnf remove (configs .rpmsave)', 'brew uninstall --zap', '-'),
    ('Hold', 'apt-mark hold', 'dnf versionlock add', 'brew pin', 'winget pin'),
    ('History', '/var/log/apt/history.log', 'dnf history', 'brew log', '-'),
]) + teaser('14.3', 'Half of all enterprise servers run Red Hat Enterprise Linux or its relatives. Next: the same jobs with dnf, yum and rpm on Fedora, RHEL and Rocky, side by side with apt.')

CHEATSHEET = cheatsheet('apt / dpkg', [
    ('Refresh / find', [('apt update', 'lists'), ('apt search W', 'find'), ('apt show P', 'details'), ('apt policy P', 'versions')]),
    ('Install / upgrade', [('apt install P', 'install'), ('apt install ./f.deb', 'local'), ('apt upgrade', 'safe'), ('apt full-upgrade', 'kernels')]),
    ('Remove / tidy', [('apt remove P', 'keep conf'), ('apt purge P', 'all'), ('apt autoremove', 'unused'), ('apt clean', 'cache')]),
    ('Control / repair', [('apt-mark hold P', 'freeze'), ('apt-get -s …', 'simulate'), ('dpkg --configure -a', 'resume'), ('apt -f install', 'fix')]),
])

MINDMAP = mindmap('apt / dpkg', [
    ('Refresh', 'blue', ['update', 'lists', 'signed']),
    ('Install', 'green', ['install', './f.deb', 'versions']),
    ('Upgrade', 'amber', ['upgrade', 'full-upgrade', 'kept back']),
    ('Remove', 'red', ['remove', 'purge', 'autoremove']),
    ('Control', 'violet', ['hold', '-s', 'clean']),
    ('dpkg', 'acc', ['-i -r -P', '-l status', 'logs']),
])

LAB = lab('manage a package', 'Build the lab (it makes a demo package and a private dpkg folder), do the four tasks, then run the checker. Use <code>d</code> for dpkg in that folder: <code>d(){ dpkg --force-not-root --root=$HOME/lab142/root --log=$HOME/lab142/dpkg.log "$@"; }</code>.',
    setup='''export PATH=$PATH:/usr/sbin:/sbin; mkdir -p ~/lab142 && cd ~/lab142 && rm -rf root note_* *.txt
for v in 1.0 2.0; do d=note_$v; mkdir -p $d/DEBIAN $d/usr/local/bin $d/etc/note
printf 'Package: note\\nVersion: %s\\nArchitecture: all\\nMaintainer: Lab <lab@example.com>\\nDescription: note demo\\n' $v > $d/DEBIAN/control
echo /etc/note/note.conf > $d/DEBIAN/conffiles; echo "v=$v" > $d/etc/note/note.conf
printf '#!/bin/sh\\necho note %s\\n' $v > $d/usr/local/bin/note; chmod 755 $d/usr/local/bin/note
dpkg-deb --build --root-owner-group $d > /dev/null; done
mkdir -p root/var/lib/dpkg/updates root/var/lib/dpkg/info; touch root/var/lib/dpkg/status''',
    tasks=['Install <code>note_1.0.deb</code> into the private root, then upgrade it with <code>note_2.0.deb</code>.',
           'Write the installed version (from the private database, via dpkg-query or dpkg -l) into <code>version.txt</code>.',
           'Put <code>note</code> on hold in the private root (dpkg --set-selections).',
           'Write the real system’s simulated summary line for removing <code>tmux</code> (the line with “to remove”, from apt-get -s) into <code>sim.txt</code>.'],
    solution='''export PATH=$PATH:/usr/sbin:/sbin; cd ~/lab142
d(){ dpkg --force-not-root --root=$HOME/lab142/root --log=$HOME/lab142/dpkg.log "$@"; }
d -i note_1.0.deb > /dev/null; d -i note_2.0.deb > /dev/null
d -l note | awk '/^ii/{print $3}' > version.txt
echo 'note hold' | d --set-selections
apt-get -s remove tmux 2>/dev/null | grep 'to remove' > sim.txt''',
    check='''export PATH=$PATH:/usr/sbin:/sbin; cd ~/lab142
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
d(){ dpkg --force-not-root --root=$HOME/lab142/root --log=$HOME/lab142/dpkg.log "$@"; }
ok "1 upgraded" '[ "$(root/usr/local/bin/note 2>/dev/null)" = "note 2.0" ]'
ok "2 version"  '[ "$(cat version.txt 2>/dev/null)" = 2.0 ]'
ok "3 hold"     'd --get-selections note 2>/dev/null | grep -q hold'
ok "4 sim"      'grep -q "1 to remove" sim.txt 2>/dev/null' ''')
