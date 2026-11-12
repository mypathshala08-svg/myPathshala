import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser, mindmap, interview, cheatsheet, lab, distro
BODY = body(HERE)

META = dict(
    module='14-packages-and-archives', lesson='03-dnf-yum-and-rpm-on-fedora-rhel-and-rocky', n='14.3',
    module_label='Module 14 · Software packages and archives',
    title='dnf, yum and rpm on Fedora, RHEL and Rocky Linux',
    desc='Package management on the Red Hat family: dnf (and yum) install, upgrade, remove, check-update and its exit code 100, search, info, provides, groups, history and undo; rpm -q, -qa, -qi, -ql, -qc, -qf, -qR, -V; repo files in /etc/yum.repos.d (enabled, gpgcheck, gpgkey), EPEL and CRB; epoch:version-release.arch; a full apt-to-dnf translation table; real analysis of saved Rocky 9 outputs and 30+ examples.',
    og_desc='dnf, yum and rpm explained with an apt-to-dnf translation table, repo files, dnf history undo and RPM versions.',
    minutes=35, level='Beginner → Advanced',
    lead='Same ideas as apt, different names: dnf for repositories, rpm for queries, .repo files, and a history you can undo. A translation table for every apt habit.',
    chips=['apt → dnf translation table', 'dnf history undo animated', 'RPM version decoded', 'Practice lab with checker', 'Real Bash in your browser'],
)

MAIN = """# Split RPM names the way rpm does: name-version-release.arch
for p in openssl-libs-3.0.7-27.el9.x86_64 nginx-1.20.1-14.el9_2.1.x86_64 tmux-3.2a-5.el9.x86_64; do
  arch=${p##*.}; rest=${p%.*}
  rel=${rest##*-}; rest=${rest%-*}
  ver=${rest##*-}; name=${rest%-*}
  printf '%-13s ver=%-7s rel=%-10s arch=%s\\n' "$name" "$ver" "$rel" "$arch"
done
"""

RUN = dict(
    heading='Reading RPM package names',
    intro='<p>The browser has no dnf or rpm; this splits real RPM names from the right, the way rpm does, because names may contain dashes.</p>',
    code=MAIN,
    anno=[('${p##*.}', 'Architecture: after the last dot.'), ('${rest%-*}', 'Peel off one -part from the right.')],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. Why split from the right?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> which release sorts last?',
             code="printf '%s\\n' 16.el9_4.1 9.el9 14.el9_2.1 | sort -V | tail -1\n"),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> cutting at the first dash breaks openssl-libs. Cut from the right.',
             code="p=openssl-libs-3.0.7-27.el9.x86_64\necho \"${p%%-*}\"\n"),
        dict(label='4 · Your turn', hint='Translate apt commands to dnf with case.',
             code="for c in install remove show; do case $c in show) echo \"apt show -> dnf info\";; *) echo \"apt $c -> dnf $c\";; esac; done\n"),
        dict(label='5 · Challenge', hint='Count enabled repos in a .repo text.',
             code="printf '[a]\\nenabled=1\\n[b]\\nenabled=0\\n[c]\\nenabled=1\\n' > r.repo\ngrep -c '^enabled=1' r.repo\n"),
    ],
)

PCRUN = dict(
    heading='Run on a Rocky or Fedora VM',
    intro='<p>Typical outputs from Rocky Linux 9 (our build machine is Ubuntu).</p>',
    items=[
        dict(title='1 · Install and query', cmd='sudo dnf install -y tmux\nrpm -qf /usr/bin/tmux', output='Installed:\n  tmux-3.2a-5.el9.x86_64\nComplete!\ntmux-3.2a-5.el9.x86_64', note='Typical.'),
        dict(title='2 · Updates waiting', cmd='dnf check-update; echo "exit $?"', output='openssl.x86_64   1:3.0.7-28.el9_4   baseos\n…\nexit 100', note='Typical.'),
        dict(title='3 · EPEL', cmd='sudo dnf install -y epel-release\nsudo dnf install -y htop', output='Installed:\n  epel-release-9-7.el9.noarch\n…\n  htop-3.3.0-1.el9.x86_64', note='Typical.'),
        dict(title='4 · Undo', cmd='dnf history\nsudo dnf history undo 14', output='ID | Command line | …\n14 | install htop | …\nRemoved:\n  htop-3.3.0-1.el9.x86_64', note='Typical.'),
    ],
)

TRACE = dict(
    heading='Checking dnf’s exit code, line by line',
    intro='<p>Step through how a monitoring script reads dnf check-update.</p>',
    code='''rc=100
case $rc in
  0) state=up-to-date ;;
  100) state=updates-available ;;
  *) state=error ;;
esac
echo "dnf check-update -> $state"
''',
    notes={1: 'What dnf returns when updates exist.', 4: 'This branch.'},
)

WORKED_INTRO = 'Three tasks for mixed Ubuntu/Rocky fleets.'
EXAMPLES = [
    dict(level='b', tag='Ops', title='Which tool on this machine?',
         problem='<p>Print the package manager to use, from /etc/os-release.</p>',
         inp='os-release', approach=['ID_LIKE.'],
         code='''. /etc/os-release
case " $ID $ID_LIKE " in *" rhel "*|*" fedora "*) echo dnf;; *" debian "*) echo apt;; *) echo unknown;; esac
''', notes={2: 'Family, not exact distro.'}, tryit='Also print the version.'),
    dict(level='i', tag='Security', title='Audit repo files',
         problem='<p>List repositories with gpgcheck disabled.</p>',
         inp='.repo text', approach=['awk by section.'],
         code='''printf '[good]\\ngpgcheck=1\\n[bad]\\ngpgcheck=0\\n' > t.repo
awk -F= '/^\\[/{id=$0} /^gpgcheck=0/{print "NO SIGNATURE CHECK:", id}' t.repo
''', notes={2: 'Remember the current section.'}, tryit='Also flag enabled=1 only.'),
    dict(level='a', tag='SRE', title='Newest kernel and the rest',
         problem='<p>From an rpm -qa list, keep the newest kernel and list the others for cleanup.</p>',
         inp='kernel names', approach=['sort -V.'],
         code='''printf '%s\\n' kernel-5.14.0-427.13.1.el9_4 kernel-5.14.0-362.24.1.el9_3 kernel-5.14.0-284.11.1.el9_2 > k.txt
echo "keep: $(sort -V k.txt | tail -1)"; sort -V k.txt | head -n -1 | sed 's/^/remove: /'
''', notes={2: 'Version-aware sort.'}, tryit='Keep the newest two.'),
]

QUIZ = mix([
    dict(q='dnf equivalent of apt install:', options=['dnf add', 'dnf install', 'rpm get', 'yum put'], answer=1, why='Same verb.'),
    dict(q='Owner of an installed file:', options=['rpm -qf', 'rpm -ql', 'dnf info', 'rpm -V'], answer=0, why='-qf.'),
    dict(q='Repo files live in…', options=['/etc/apt', '/etc/yum.repos.d', '/var/lib/rpm', '/etc/dnf.repos'], answer=1, why='.repo files.'),
    dict(q='dnf check-update exit 100 means…', options=['error', 'updates available', 'no updates', 'locked'], answer=1, why='Scripts use it.'),
    dict(q='Undo transaction 13:', options=['dnf undo 13', 'dnf history undo 13', 'rpm -e 13', 'yum back 13'], answer=1, why='history undo.'),
    dict(q='Where is htop on RHEL?', options=['BaseOS', 'EPEL', 'AppStream', 'snap only'], answer=1, why='Extra Packages.'),
    dict(q='In 1:1.20.1-16.el9, “1:” is…', options=['the release', 'the epoch', 'the arch', 'a typo'], answer=1, why='Epoch.'),
    dict(q='yum on RHEL 9 is…', options=['a different tool', 'dnf under another name', 'removed', 'apt'], answer=1, why='Symlink.'),
])

REVISION = [
    'rpm = dpkg (single files, queries, database); dnf = apt (repos, solver); yum = old name for dnf.',
    'dnf install/remove/upgrade/search/info/provides/autoremove; check-update exits 100 if updates exist.',
    'rpm -q, -qa, -qi, -ql, -qc, -qf, -qR, -V; -p for a not-installed .rpm.',
    '/etc/yum.repos.d/*.repo: [id], baseurl/mirrorlist, enabled, gpgcheck, gpgkey; EPEL and CRB for extras.',
    'Every dnf run is a transaction: dnf history, history info N, history undo N / rollback N.',
    'Versions: [epoch:]version-release.dist.arch; split names from the right.',
]

FAQ = [
    ('What is the difference between yum and dnf?', 'dnf replaced yum; on RHEL 8+ the yum command runs dnf.'),
    ('What is the apt update equivalent in dnf?', 'dnf refreshes automatically; dnf makecache forces it.'),
    ('How do I find which package owns a file on RHEL?', 'rpm -qf /path, or dnf provides /path for packages not installed.'),
    ('How do I undo a dnf install or upgrade?', 'dnf history to find the ID, then sudo dnf history undo ID.'),
    ('What is EPEL?', 'Extra Packages for Enterprise Linux: a community repository of extra software for RHEL-compatible systems.'),
    ('What does the epoch in an RPM version mean?', 'A number before the colon that overrides normal version comparison.'),
    ('How do I list repositories?', 'dnf repolist (add all to see disabled ones).'),
]

PRACTICE_INTRO = 'Small tasks on RPM names and repo text. Expected outputs come from real runs on our build machine.'
PROBLEMS = [
    dict(level='easy', title='Arch', stmt='Print the arch of tmux-3.2a-5.el9.x86_64.', inp='a name', code="p=tmux-3.2a-5.el9.x86_64; echo ${p##*.}\n", explain='x86_64.'),
    dict(level='easy', title='Translate', stmt='Print the dnf command for “apt show nginx”.', inp='nothing', code="echo 'dnf info nginx'\n", explain='info.'),
    dict(level='easy', title='Family', stmt='Print ID_LIKE of this machine.', inp='nothing', code=". /etc/os-release; echo $ID_LIKE\n", explain='debian.'),
    dict(level='medium', title='Name', stmt='Print the name part of openssl-libs-3.0.7-27.el9.x86_64.', inp='a name', code="p=openssl-libs-3.0.7-27.el9.x86_64; r=${p%.*}; r=${r%-*}; echo ${r%-*}\n", explain='openssl-libs.'),
    dict(level='medium', title='Epoch', stmt='Print the epoch of 1:3.0.7-28.el9_4.', inp='a version', code="v=1:3.0.7-28.el9_4; echo ${v%%:*}\n", explain='1.'),
    dict(level='medium', title='Newest', stmt='Newest of 9.el9, 14.el9_2.1, 16.el9_4.1.', inp='releases', code="printf '%s\\n' 9.el9 14.el9_2.1 16.el9_4.1 | sort -V | tail -1\n", explain='16.el9_4.1.'),
    dict(level='business', title='Enabled', stmt='Print enabled repo ids from a small .repo text.', inp='repo text', code="printf '[a]\\nenabled=1\\n[b]\\nenabled=0\\n' | awk -F= '/^\\[/{id=$0} /^enabled=1/{print id}'\n", explain='[a].'),
    dict(level='business', title='Exit code', stmt='Map dnf exit 100 to a word.', inp='a code', code="rc=100; [ $rc -eq 100 ] && echo updates\n", explain='updates.'),
]

SCN_INTRO = 'Interview questions about dnf and rpm, from fresher to senior rounds.'
SCENARIOS = (
    scn('Any company · basics', 'Fresher', '“How do you install a package on RHEL?”', 'Very common.', 'and query it?',
        '''<ul>
          <li>sudo dnf install PKG (yum on old systems).</li>
          <li>rpm -q PKG; rpm -ql PKG; rpm -qf FILE.</li>
          <li>dnf info PKG for details.</li>
        </ul>''', 'apt install.') +
    scn('Service company', 'Junior', '“No match for argument: htop”', 'Rocky 9.', 'fix?',
        '''<ol>
          <li>htop is in EPEL.</li>
          <li>sudo dnf install epel-release (and enable crb).</li>
          <li>dnf install htop.</li>
        </ol>''', 'downloading a random .rpm.') +
    scn('Product company', 'Mid-level', 'A patch broke production', 'dnf upgrade last night.', 'rollback?',
        '''<ul>
          <li>dnf history; dnf history info N.</li>
          <li>sudo dnf history undo N.</li>
          <li>versionlock the package; test on staging.</li>
        </ul>''', 'restoring a full backup first.') +
    scn('Platform', 'Senior', 'Mixed Ubuntu and RHEL fleet', 'One runbook.', 'how?',
        '''<ul>
          <li>Ansible package module, or scripts detecting os-release.</li>
          <li>Map commands in one table; same patch process.</li>
          <li>Separate repos/mirrors per family.</li>
        </ul>''', 'two separate teams.')
) + interview([
    ('rpm -ivh vs dnf install?', 'rpm has no dependency resolution.'),
    ('What is rpm -Va?', 'Verify all packages’ files.'),
    ('.rpmnew vs .rpmsave?', 'New default config vs your saved one.'),
    ('dnf provides?', 'Which package provides a file or capability.'),
    ('What is CRB?', 'CodeReady Builder: extra build dependencies.'),
    ('What is installonly_limit?', 'How many kernels dnf keeps.'),
    ('dnf group install?', 'Install a set like "Development Tools".'),
], [
    ('RHCSA (EX200)', 'Install, update and remove software with dnf; configure repositories.'),
    ('RHCE', 'Automate package management.'),
    ('CompTIA Linux+', 'rpm and yum/dnf.'),
]) + distro('The Red Hat family and its relatives.', [
    ('Install', 'apt install', 'dnf install', 'zypper install (SUSE)', 'pacman -S (Arch)'),
    ('Owner of file', 'dpkg -S', 'rpm -qf', 'rpm -qf', 'pacman -Qo'),
    ('Repo config', 'sources.list.d', 'yum.repos.d', 'zypp/repos.d', 'pacman.conf'),
    ('Undo', '-', 'dnf history undo', 'snapper rollback', '-'),
    ('Old tool', 'apt-get', 'yum', '-', '-'),
]) + teaser('14.4', 'Some software is not in any repository, or is too old there. Next: snap, flatpak and building from source with ./configure, make and make install.')

CHEATSHEET = cheatsheet('dnf / rpm', [
    ('dnf', [('dnf install X', 'install'), ('dnf upgrade', 'patch'), ('dnf remove X', 'remove'), ('dnf check-update', 'exit 100')]),
    ('Find', [('dnf search W', 'search'), ('dnf info X', 'details'), ('dnf provides F', 'which pkg'), ('dnf repolist', 'repos')]),
    ('rpm', [('rpm -qa', 'all'), ('rpm -qf F', 'owner'), ('rpm -ql X', 'files'), ('rpm -V X', 'verify')]),
    ('History / repos', [('dnf history', 'list'), ('history undo N', 'reverse'), ('epel-release', 'extras'), ('/etc/yum.repos.d', 'config')]),
])

MINDMAP = mindmap('dnf / rpm', [
    ('dnf', 'blue', ['install', 'upgrade', 'remove']),
    ('rpm', 'green', ['-qa -qf', '-ql -qi', '-V']),
    ('Repos', 'amber', ['.repo files', 'EPEL', 'gpgcheck']),
    ('History', 'red', ['transactions', 'undo', 'rollback']),
    ('Versions', 'violet', ['epoch', 'release', 'arch']),
    ('Map', 'acc', ['apt → dnf', 'dpkg → rpm', 'detect']),
])

LAB = lab('translate and analyse', 'Build the lab (it saves typical Rocky outputs), write <code>~/lab143/answers.sh</code>, then run the checker.',
    setup='''mkdir -p ~/lab143 && cd ~/lab143 && rm -f answers.sh *.txt
printf '%s\\n' bash-5.1.8-9.el9.x86_64 kernel-5.14.0-427.13.1.el9_4.x86_64 kernel-5.14.0-362.24.1.el9_3.x86_64 python3-libs-3.9.18-3.el9.x86_64 > qa.out
printf '[baseos]\\nenabled=1\\ngpgcheck=1\\n[epel]\\nenabled=1\\ngpgcheck=0\\n[crb]\\nenabled=0\\ngpgcheck=1\\n' > lab.repo''',
    tasks=['Write the number of installed kernels (from qa.out) into <code>kernels.txt</code>.',
           'Write the name part of the python3-libs line (exactly <code>python3-libs</code>) into <code>name.txt</code>, computed, not typed.',
           'Write the id of the enabled repository that has gpgcheck=0 (just the id, no brackets) into <code>unsafe.txt</code>.',
           'Write the dnf command equivalent to <code>apt list --upgradable</code> into <code>cmd.txt</code>.'],
    solution='''cat > answers.sh <<'EOF'
cd ~/lab143
grep -c '^kernel-' qa.out > kernels.txt
p=$(grep '^python3-libs' qa.out); r=${p%.*}; r=${r%-*}; echo "${r%-*}" > name.txt
awk -F= '/^\\[/{id=$0; gsub(/[][]/,"",id)} /^enabled=1/{en[id]=1} /^gpgcheck=0/{if(en[id]) print id}' lab.repo > unsafe.txt
echo 'dnf check-update' > cmd.txt
EOF''',
    check='''cd ~/lab143; rm -f kernels.txt name.txt unsafe.txt cmd.txt
ok(){ if eval "$2"; then echo "PASS  $1"; else echo "FAIL  $1"; fi; }
[ -f answers.sh ] && bash answers.sh 2>/dev/null
ok "1 kernels" '[ "$(cat kernels.txt 2>/dev/null)" = 2 ]'
ok "2 name"    '[ "$(cat name.txt 2>/dev/null)" = python3-libs ]'
ok "3 unsafe"  '[ "$(cat unsafe.txt 2>/dev/null)" = epel ]'
ok "4 cmd"     '[ "$(cat cmd.txt 2>/dev/null)" = "dnf check-update" ]' ''')
