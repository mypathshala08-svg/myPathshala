import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import *

# ---------------------------------------------------------------- 1. story
fam = [(26, 'Ubuntu', 'dev servers', 'acc'), (156, 'RHEL', 'bank client', 'red'), (286, 'Alpine', 'Docker images', 'blue'), (416, 'Kali', 'security team', 'violet')]
sc = ''.join(label_box(x, 20, 110, 46, [n, u], tone, 9) + arrow(x + 55, 68, x + 55, 94, 'ink3', 1.4) for x, n, u, tone in fam)
sc += label_box(26, 96, 500, 30, ['Same Linux kernel underneath'], 'blue', 9.4)
sc += t(560, 52, 'Four names.', 9, 'ink2', anchor='start') + t(560, 68, 'Which one', 9, 'ink2', anchor='start') + t(560, 84, 'to learn?', 9, 'acc', anchor='start', bold=True)
story = '''<section class="part" id="story">
  <span class="part-label"><b>1</b> The story</span>
  <h2>Four Linuxes in one office</h2>
  <div class="story">
''' + puzzle('Ubuntu, Rocky Linux and Alpine all run the same Linux kernel. So why does <code>apt install nginx</code> work on one of them and fail with “command not found” on the other two?') + '''
    <p class="narration">In her first week Riya hears four different names. The developers’ servers run <b>Ubuntu</b>. The bank the company works for insists on <b>Red Hat Enterprise Linux</b>. The Docker images use something called <b>Alpine</b>. And the security team’s laptops run <b>Kali</b>. She is worried: does she have to learn four operating systems?</p>
''' + scene('Ubuntu for development servers, RHEL for a bank client, Alpine for Docker images and Kali for the security team, all on top of the same Linux kernel.', sc,
            'Different <tspan font-weight="700" class="s-acc">distributions</tspan>, one kernel, mostly the same commands.') + '''
R> Sir, four Linuxes! Should I learn Ubuntu first, or Red Hat, or all of them?
A> Relax. They are all <b>distributions</b>: the same Linux kernel, packed with tools, a package manager and default settings by different teams. About 90% of what you learn works on all of them. The commands <code>ls</code>, <code>grep</code>, <code>cd</code> are identical.
K> Then what is different? Our DevOps lead always says “this is RHEL, use dnf, not apt”.
A> Exactly that kind of thing: how you <b>install software</b>, a few file locations, the security system, and how long each version is supported. Today you will learn the distribution <b>families</b>, what really differs, and how to choose. Then you can sit at any Linux server and know where you are within ten seconds.
  </div>
</section>
'''

# ---------------------------------------------------------------- 2. definition
lv = levels4('Distributions at four depths', [
    ('v', 'No jargon: one Android, many phones', '''      <p>You already understand distributions from your phone. Many companies make Android phones. All of them run Android underneath, but each brand adds its own look, its own apps and its own update schedule.</p>''' + '''<div class="scene"><svg viewBox="0 0 640 210" role="img" aria-label="Top row: three phone brands all built on Android. Bottom row: three Linux distributions, Ubuntu, Fedora and Debian, all built on the Linux kernel.">''' + ''.join(label_box(20 + k * 120, 14, 108, 40, [n, 'own look + apps'], 'acc', 8.8) for k, n in enumerate(['Phone brand A', 'Phone brand B', 'Phone brand C'])) + label_box(20, 62, 348, 26, ['Android underneath'], 'green', 9) + ''.join(label_box(20 + k * 120, 112, 108, 40, [n, 'own tools + installer'], 'blue', 8.8) for k, n in enumerate(['Ubuntu', 'Fedora', 'Debian'])) + label_box(20, 160, 348, 26, ['Linux kernel underneath'], 'green', 9) + t(400, 40, 'Phones: one Android, many brands.', 9.4, anchor='start', bold=True) + t(400, 60, 'Each brand adds its look, apps, updates.', 9, 'ink2', anchor='start') + t(400, 138, 'Computers: one Linux kernel,', 9.4, anchor='start', bold=True) + t(400, 154, 'many distributions.', 9.4, anchor='start', bold=True) + t(400, 174, 'Each adds its tools, installer, support.', 9, 'ink2', anchor='start') + '''<text x="632" y="204" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>''' + '''
      <ul>
        <li>A <b>distribution</b> (“distro”) is a ready-to-use Linux made by one team: Ubuntu, Fedora, Debian, Red Hat.</li>
        <li>Like phone brands, they share the same core and differ in looks, included software and how long they give updates.</li>
        <li>What you learn on one works on almost all others, just as you can use any Android phone once you know one.</li>
      </ul>'''),
    ('b', 'Same atta, different rotis', '''      <ul>
        <li>The <b>Linux kernel</b> is the atta (flour): every distribution uses it.</li>
        <li>Each <b>distribution</b> is a different recipe: phulka, paratha, naan. Same base, different extra ingredients, different cooking style.</li>
        <li>The extras are the <b>tools</b> (shell, commands), the <b>package manager</b> (the way you add new software), and the <b>default settings</b>.</li>
        <li>Most daily commands are the same everywhere. Start with <b>Ubuntu</b>: it is the most common for beginners, laptops (WSL) and cloud servers.</li>
      </ul>'''),
    ('i', 'The families and what differs between them', '''      <ul>
        <li><b>Debian family</b>: Debian, Ubuntu, Linux Mint, Kali, Raspberry Pi OS. Packages <code>.deb</code>, tools <code>apt</code>/<code>dpkg</code>.</li>
        <li><b>Red Hat family</b>: RHEL, Fedora, CentOS Stream, Rocky Linux, AlmaLinux, Oracle Linux, Amazon Linux. Packages <code>.rpm</code>, tools <code>dnf</code> (older <code>yum</code>)/<code>rpm</code>.</li>
        <li><b>SUSE</b>: SUSE Linux Enterprise, openSUSE (<code>zypper</code>). <b>Arch</b>: Arch Linux, Manjaro (<code>pacman</code>). <b>Alpine</b>: tiny, for containers (<code>apk</code>).</li>
        <li><b>Release model:</b> fixed releases with long support (Ubuntu LTS, Debian, RHEL) vs <b>rolling</b> (Arch, openSUSE Tumbleweed) where you always get the newest versions.</li>
        <li><b>Who supports it:</b> community (Debian, Fedora, Rocky, Alma) or a company with paid support (Canonical for Ubuntu, Red Hat for RHEL, SUSE).</li>
      </ul>'''),
    ('a', 'The real differences an engineer meets', '''      <ul>
        <li><b>Package names and paths</b>: the Apache web server is <code>apache2</code> on Ubuntu and <code>httpd</code> on RHEL; SSH login records go to <code>/var/log/auth.log</code> on Ubuntu and <code>/var/log/secure</code> on RHEL.</li>
        <li><b>Security layer</b>: RHEL family enables <b>SELinux</b> by default, Ubuntu uses <b>AppArmor</b> (Lesson 19.2).</li>
        <li><b>C library</b>: almost all use glibc; <b>Alpine uses musl</b>, so some pre-built programs behave differently in Alpine containers.</li>
        <li><b>Lifecycle</b>: an Ubuntu LTS gets 5 years of standard support (extendable with Ubuntu Pro); a RHEL major version is supported for 10 years. Banks and telecoms value long, predictable support and certified software.</li>
        <li><b>Identity</b>: every modern distro describes itself in <code>/etc/os-release</code>; <code>ID</code> and <code>ID_LIKE</code> tell scripts which family they are on.</li>
      </ul>'''),
])

definition = '''<section class="part" id="definition">
  <span class="part-label"><b>2</b> Definition</span>
  <h2>What is a Linux distribution?</h2>
''' + def_block(
    'A <b>Linux distribution (distro)</b> is a complete operating system built on the Linux kernel, combined with a collection of system software and libraries (usually the GNU tools), a <b>package management system</b> and software <b>repositories</b>, an installer and default configuration, and released and maintained by a community or a company on a defined <b>release and support cycle</b>.',
    'A distro is Linux “ready to use”: the kernel plus all the programs around it, a way to install more software, and a team that keeps it updated. Ubuntu, Debian, Fedora and RHEL are distros.') + '''

  <h3>Words you’ll meet in this lesson</h3>
''' + terms([
    ('Distribution', f'Kernel + tools + package manager + defaults + support. {gl("distribution-distro", "Glossary →")}'),
    ('Package', f'A ready-to-install bundle of a program: <code>.deb</code> or <code>.rpm</code>. {gl("package-deb-rpm", "Glossary →")}'),
    ('Package manager', f'The tool that installs, updates and removes packages: apt, dnf, zypper, pacman. {gl("apt-vs-dpkg", "Glossary →")}'),
    ('Repository', f'An online store of packages for your distro. {gl("repository", "Glossary →")}'),
    ('LTS', 'Long-Term Support: a release kept secure for years. Ubuntu LTS comes every two years.'),
    ('Rolling release', 'No big versions; packages are updated continuously (Arch, Tumbleweed).'),
    ('Upstream / downstream', 'Fedora → CentOS Stream → RHEL → Rocky/Alma: changes flow downstream.'),
    ('Derivative', 'A distro built from another: Ubuntu from Debian, Mint from Ubuntu.'),
    ('EOL', 'End of life: after this date the version gets no more security updates.'),
    ('/etc/os-release', 'The file where every modern distro writes its name, ID and version.'),
]) + '''

  <h3>Quick facts (as of November 2026)</h3>
''' + facts([
    ('Debian first released', '1993; current stable is Debian 13 “trixie” (August 2025)'),
    ('Ubuntu', 'Based on Debian; LTS every two years in April. Latest LTS: 26.04 (April 2026), 5 years standard support'),
    ('Red Hat Enterprise Linux', 'Commercial, 10-year lifecycle per major version; RHEL 10 released in 2025'),
    ('CentOS Linux', 'Ended: CentOS 8 in Dec 2021, CentOS 7 in June 2024. CentOS Stream continues as RHEL’s upstream'),
    ('Rocky Linux and AlmaLinux', 'Free community rebuilds compatible with RHEL'),
    ('Ubuntu version numbers', 'Year.month of release: 24.04 = April 2024'),
]) + '\n' + names('Distribution and tool names hide small stories. Knowing them helps you remember which tool belongs where.', [
    ('apt', 'Advanced Package Tool', 'Debian family’s installer.'),
    ('dpkg', 'Debian package', 'The low-level tool that unpacks .deb files.'),
    ('rpm', 'RPM Package Manager', 'Originally “Red Hat Package Manager”: the .rpm format.'),
    ('yum', 'Yellowdog Updater, Modified', 'Came from Yellow Dog Linux; dnf replaced it.'),
    ('dnf', 'Dandified YUM', 'The newer, faster yum on Fedora and RHEL.'),
    ('Debian', 'Debra + Ian', 'Named by founder Ian Murdock after his then-girlfriend Debra and himself.'),
    ('Ubuntu', '“humanity to others”', 'A Southern African (Nguni) word, chosen by founder Mark Shuttleworth.'),
    ('Rocky', 'Rocky McGaugh', 'Named after a co-founder of CentOS.'),
    ('LTS', 'Long-Term Support', 'Years of security updates for one version.'),
]) + '\n' + lv + didyou('Ubuntu code names are an adjective and an animal starting with the same letter, moving through the alphabet: 24.04 is “Noble Numbat”, 26.04 is “Resolute Raccoon”. Debian names its releases after Toy Story characters: Debian 13 is “trixie”.') + '''
EXAM> “Explain Linux distributions with examples” → definition, the components (kernel, GNU tools, package manager, repositories, installer, support), two families with examples and package tools (Debian: .deb/apt; Red Hat: .rpm/dnf), and one line on LTS vs rolling release.
''' + qc('Ubuntu and Rocky Linux: same kernel or different kernels?', 'Both use the Linux kernel (each distro ships its own build and version). What differs is everything around it: package manager, default tools and settings, support lifecycle.') + '''
</section>
'''

# ---------------------------------------------------------------- 3. types
types = '''<section class="part" id="types">
  <span class="part-label"><b>3</b> Types and ways to use it</span>
  <h2>The distribution families</h2>
''' + table(['Family', 'Main members', 'Package format · tool', 'Typical use'], [
    ['Debian', 'Debian, <b>Ubuntu</b>, Linux Mint, Kali, Raspberry Pi OS', '<code>.deb</code> · <code>apt</code>, <code>dpkg</code>', 'Cloud servers, developer laptops, WSL, beginners'],
    ['Red Hat', '<b>RHEL</b>, Fedora, CentOS Stream, Rocky Linux, AlmaLinux, Oracle Linux, Amazon Linux', '<code>.rpm</code> · <code>dnf</code> (<code>yum</code>), <code>rpm</code>', 'Banks, telecom, enterprise data centres, certified software'],
    ['SUSE', 'SUSE Linux Enterprise, openSUSE Leap / Tumbleweed', '<code>.rpm</code> · <code>zypper</code>', 'Enterprise (strong in Europe), SAP systems'],
    ['Arch', 'Arch Linux, Manjaro, EndeavourOS', '<code>.pkg.tar.zst</code> · <code>pacman</code>', 'Enthusiasts, always-newest software'],
    ['Alpine', 'Alpine Linux', '<code>.apk</code> · <code>apk</code>', 'Very small container images (a few MB)'],
], minw=680) + '''

  <h3 id="anatomy">Anatomy of a distribution</h3>
  <p>Every distribution is built from the same stack of parts. The ones marked <b>differs</b> are where distributions really make different choices; the rest is shared almost everywhere.</p>
''' + '<div class="scene scene--wide"><svg viewBox="0 0 640 300" role="img" aria-label="Layers of a Linux distribution from bottom to top: hardware, boot loader, Linux kernel, init system and services, core tools and C library, package manager and repositories, desktop or server software, your applications. Package manager, defaults, desktop and release cycle differ between distributions.">' + ''.join(label_box(20, 14 + k * 34, 430, 28, [name], tone, 9) + (t(462, 32 + k * 34, note, 8.8, 'red' if note.startswith('differs') else 'ink3', anchor='start', bold=note.startswith('differs')) if note else '') for k, (name, tone, note) in enumerate([
    ('Your applications: browser, VS Code, Python, your app', 'card', ''),
    ('Desktop or server software: GNOME, KDE · nginx, PostgreSQL', 'violet', 'differs: which ones by default'),
    ('Package manager + repositories: apt · dnf · zypper · pacman · apk', 'acc', 'differs: the biggest difference'),
    ('Core tools: GNU coreutils (ls, cp), bash, C library (glibc · musl)', 'green', 'mostly shared (Alpine: musl)'),
    ('init system and services: systemd (most) · OpenRC (Alpine)', 'blue', 'mostly shared'),
    ('Linux kernel: built and patched by the distribution', 'blue', 'same kernel, different builds'),
    ('Boot loader: GRUB (or systemd-boot)', 'card', 'mostly shared'),
    ('Hardware: PC, server, cloud VM, Raspberry Pi', 'card', '')])) + t(320, 292, 'Plus a release cycle and support promise (LTS, rolling): the other big difference.', 9, 'acc', bold=True) + '<text x="632" y="296" text-anchor="end" class="s-wm">myphatshala.in</text></svg></div>' + '''
''' + didyou('The oldest distributions still maintained today date from 1993: <b>Slackware</b> (July 1993) and <b>Debian</b> (founded in August 1993). Before distributions existed, people downloaded the kernel and the GNU tools separately and put the system together by hand.') + '''
  <h3>Which one should you choose?</h3>
''' + cards([
    ('Learning Linux (this course)', 'Ubuntu LTS: huge community, default in WSL and on most clouds. Everything in this course is tested on Ubuntu.', 'start here'),
    ('Company servers', 'Ubuntu LTS or a RHEL-family distro (RHEL, Rocky, AlmaLinux). Follow what your team already runs.', 'production'),
    ('Banks, telecom, government', 'Often RHEL or SUSE with paid support and long lifecycles, because certified vendors require it.', 'enterprise'),
    ('Docker images', 'Debian “slim”, Ubuntu or Alpine for tiny images. Check musl compatibility before choosing Alpine.', 'containers'),
    ('Security testing', 'Kali Linux: Debian-based, with penetration-testing tools pre-installed. Not for daily use.', 'specialist'),
    ('Old laptop', 'Lightweight desktops such as Linux Mint Xfce or Lubuntu.', 'desktop'),
]) + '''
  <h3>Release models</h3>
''' + table(['', 'Fixed release (LTS)', 'Rolling release'], [
    ['Examples', 'Ubuntu LTS, Debian stable, RHEL, Rocky', 'Arch, openSUSE Tumbleweed'],
    ['Versions', 'Same package versions for years, only security fixes', 'Newest versions all the time'],
    ['Upgrade', 'Big upgrade every few years (22.04 → 24.04)', 'Small updates every day or week'],
    ['Good for', 'Servers: stable and predictable', 'Enthusiasts and developers who want the newest'],
], minw=560) + '''
''' + qc('Which family would you expect on a bank’s core servers, and why?', 'The Red Hat family (RHEL) or SUSE: long support lifecycles, paid support contracts and software certified by vendors.') + '''
</section>
'''

# ---------------------------------------------------------------- 4. steps
steps = '''<section class="part" id="steps">
  <span class="part-label"><b>4</b> Step by step</span>
  <h2>Sit at any Linux server and find out where you are</h2>
  <p>A routine every engineer follows on an unfamiliar machine. Each step takes seconds.</p>
''' + stepper([
    ('1. Which distribution and version?', '<p><code>cat /etc/os-release</code> (or <code>lsb_release -a</code> on Ubuntu).</p>', 'Behind the screen: a plain text file written by the distribution. The kernel knows nothing about it.'),
    ('2. Which family?', '<p>Look at <code>ID</code> and <code>ID_LIKE</code>: <code>ID_LIKE=debian</code> → apt; <code>ID_LIKE="rhel centos fedora"</code> → dnf.</p>', 'Behind the screen: scripts and tools such as Ansible read the same fields to decide which commands to use.'),
    ('3. Which package manager?', '<p><code>command -v apt dnf yum zypper</code> prints the ones that exist.</p>', 'Behind the screen: <code>command -v</code> searches PATH, the same way the shell finds any command.'),
    ('4. Which kernel?', '<p><code>uname -r</code>. Distros ship their own patched kernel builds, so the version tells you about patches too.</p>', 'Behind the screen: the kernel answers directly through the uname system call.'),
    ('5. Is it still supported?', '<p>Check the version against the vendor’s lifecycle page. An EOL version (for example CentOS 7) gets no security fixes.</p>', 'Behind the screen: an unsupported server is a security risk; auditors ask about this.'),
]) + '''
''' + qc('Which single file tells you the distribution and version on almost any modern Linux?', '<code>/etc/os-release</code>.') + '''
</section>
'''

# ---------------------------------------------------------------- 5. animations
def two_terms(left, right, lt='Ubuntu server', rt='Rocky Linux server'):
    return term(6, 20, 170, 110, left, title=lt, size=7.2, step=12) + term(184, 20, 170, 110, right, title=rt, size=7.2, step=12)
see = [two_terms(['$ '], ['$ ']) + t(180, 160, 'Two servers, two distributions. Task: install the nginx web server.', 8.8, 'ink2'),
       two_terms(['$ sudo apt install nginx'], ['$ sudo dnf install nginx']) + t(180, 160, 'Different install commands.', 8.8, 'ink2'),
       two_terms(['$ sudo apt install nginx', ('Unpacking nginx ...', 'dim')], ['$ sudo dnf install nginx', ('Installing : nginx', 'dim')]) + t(180, 160, 'Different messages while installing.', 8.8, 'ink2'),
       two_terms(['$ sudo systemctl start nginx', '$ curl -sI localhost | head -1', ('HTTP/1.1 200 OK', 'out')], ['$ sudo systemctl start nginx', '$ curl -sI localhost | head -1', ('HTTP/1.1 200 OK', 'out')]) + t(180, 160, 'After that: the same commands to start and test it.', 8.8, 'ink2'),
       two_terms(['$ ls -d /etc/nginx/sites-*', ('/etc/nginx/sites-available', 'out'), ('/etc/nginx/sites-enabled', 'out')], ['$ ls -d /etc/nginx/sites-*', ('ls: cannot access', 'err'), ("'/etc/nginx/sites-*'", 'err')]) + t(180, 160, 'Small differences in default config layout.', 8.8, 'acc', bold=True)]
def bstack(hl):
    o = label_box(10, 18, 160, 30, ['apt  ·  .deb'], 'acc' if 1 in hl else 'card', 8.8) + label_box(190, 18, 160, 30, ['dnf  ·  .rpm'], 'violet' if 1 in hl else 'card', 8.8)
    o += label_box(10, 56, 160, 30, ['Ubuntu repository'], 'acc' if 2 in hl else 'card', 8.6) + label_box(190, 56, 160, 30, ['Rocky repository'], 'violet' if 2 in hl else 'card', 8.6)
    o += label_box(10, 94, 340, 28, ['nginx program + systemd + bash + GNU tools'], 'green' if 3 in hl else 'card', 8.6)
    o += label_box(10, 128, 340, 26, ['Linux kernel'], 'blue' if 4 in hl else 'card', 8.8)
    return o
behind = [bstack([4]) + t(180, 178, 'Both servers run the Linux kernel.', 8.8, 'ink2'),
          bstack([1]) + t(180, 178, 'The package managers differ: apt vs dnf.', 8.8, 'ink2'),
          bstack([1, 2]) + t(180, 178, 'Each downloads from its own distribution’s repository.', 8.8, 'ink2'),
          bstack([3, 4]) + t(180, 178, 'The result is the same nginx program on the same kind of kernel.', 8.8, 'green', bold=True),
          bstack([2, 3]) + t(180, 178, 'Each distro packages it with its own default config files.', 8.8, 'ink2')]
two = anim_two('Install nginx on two distros', 'Same program, two distributions', 'Two terminals installing nginx: apt on Ubuntu, dnf on Rocky Linux, then the same start and test commands.',
               'Layers: different package managers and repositories, the same nginx program, systemd and Linux kernel underneath.', see, behind,
               ['Riya must install the nginx web server on an Ubuntu server and on a Rocky Linux server.',
                'On Ubuntu she uses <code>apt</code>; on Rocky Linux, <code>dnf</code>. This is the biggest daily difference between families.',
                'The progress messages look different, but both download and install packages.',
                'Starting and testing the server uses exactly the same commands on both.',
                'One detail differs: Ubuntu’s nginx package adds <code>sites-available</code> and <code>sites-enabled</code> folders; Rocky’s package puts site configs in <code>conf.d</code> only. Small differences like this are why you read the distro’s docs.'],
               ['Underneath, both are Linux kernels. Process, memory and file handling work the same.',
                'The package format and tool differ: <code>.deb</code> with apt on the Debian family, <code>.rpm</code> with dnf on the Red Hat family.',
                'Each package manager downloads from its own signed repository, maintained by the distribution.',
                'Once installed it is the same open-source nginx, started by the same systemd, using the same kernel features.',
                'Distributions choose defaults: folder layout, file names, service names. Learn the family’s conventions and you can work on all its members.'])

# scenario 1: chooser
def choose(i):
    qs = ['Learning Linux on a laptop', 'Cloud server for a startup app', 'Core banking system at a bank', 'Small Docker image for an API']
    ans = [('Ubuntu LTS (WSL or VM)', 'acc'), ('Ubuntu LTS or Rocky/Alma', 'green'), ('RHEL / SUSE with support', 'red'), ('Alpine or Debian slim', 'blue')]
    o = t(180, 22, 'Which distribution for which job?', 10, 'acc', bold=True)
    for k in range(4):
        y = 36 + k * 30
        o += t(14, y + 16, qs[k], 8.6, 'ink' if k <= i else 'ink3', anchor='start', bold=(k == i))
        if k <= i:
            o += arrow(186, y + 12, 200, y + 12, 'ink3', 1.4) + label_box(204, y, 146, 24, [ans[k][0]], ans[k][1], 8.2)
    return o
ch = [choose(0) + cap('Learning: the most common, best-documented choice.', '', 'card', y=164, h=34),
      choose(1) + cap('Startup servers: free, well supported, big community.', '', 'green', y=164, h=34),
      choose(2) + cap('Banks: long support contracts and certified software.', '', 'red', y=164, h=34),
      choose(3) + cap('Containers: smallest image that runs the app.', '', 'blue', y=164, h=34),
      choose(3) + cap('Rule: choose what your team, vendors and support need.', 'Commands you learn here work on all of them.', 'green', y=158, h=44)]
s1 = anim_one('Real-time scenario 1', 'Choosing a distribution for four real jobs',
              'There is no single “best Linux”. Watch four common situations and the usual choice for each. These are typical industry patterns, not strict rules.',
              'Right distro, right job', 'Four jobs on the left (learning, startup cloud server, bank, Docker image) matched with a usual distribution choice on the right.', ch,
              ['For learning, Ubuntu LTS is the usual choice: default in WSL, huge community, most tutorials use it.',
               'A startup’s cloud servers commonly run Ubuntu LTS or a free RHEL-compatible distro such as Rocky Linux or AlmaLinux.',
               'Banks and telecoms often choose RHEL or SUSE because software vendors certify their products on them and support contracts are available.',
               'For Docker images, smaller is better: Alpine (a few MB) or Debian “slim”. Alpine uses the musl C library, so test your app on it.',
               'The decision is driven by support, team skills and vendor requirements, not by which is “better”. Your skills transfer.'],
              hid='scenario-choose')

# scenario 2: LTS vs rolling over time
def tl(k):
    o = t(14, 26, 'Ubuntu LTS', 9, 'acc', anchor='start', bold=True) + t(14, 92, 'Arch (rolling)', 9, 'violet', anchor='start', bold=True)
    years = ['2024', '2025', '2026', '2027']
    for i, y in enumerate(years):
        x = 110 + i * 60
        o += t(x + 25, 146, y, 8, 'ink3')
        if i <= k:
            o += label_box(x, 12, 52, 26, ['24.04'], 'acc', 8.2) + t(x + 26, 50, '+ fixes', 7.4, 'green')
            o += ''.join(fill(x + j * 13, 78, 10, 24, 'violet', rx=2) for j in range(4))
    return o
lt = [tl(0) + cap('2024: both start fresh.', '', 'card', y=160, h=34),
      tl(1) + cap('LTS: same versions, security fixes only.', 'Rolling: new versions every week.', 'blue', y=160, h=44),
      tl(2) + cap('LTS servers stay predictable for years.', 'Rolling gets new features, and new surprises.', 'blue', y=160, h=44),
      tl(3) + cap('By 2027 the LTS still runs the 2024 versions safely.', 'The rolling system has had hundreds of updates.', 'green', y=160, h=44),
      tl(3) + cap('Servers: prefer LTS. Personal machines: either.', '', 'green', y=160, h=34)]
s2 = anim_one('Real-time scenario 2', 'Three years of updates: LTS vs rolling',
              'Each orange box is the same Ubuntu 24.04 LTS release receiving fixes; each violet bar is a batch of new versions on a rolling distro. Illustrative, not exact counts.',
              'Fixed release vs rolling release', 'Timeline from 2024 to 2027 showing an LTS release receiving fixes and a rolling distribution receiving frequent new versions.', lt,
              ['Both machines are installed in 2024.',
               'The LTS keeps the same versions of every program and only gets security and bug fixes. The rolling distro updates programs to their newest versions all the time.',
               'For a server running a payment app, “nothing changes unexpectedly” is worth a lot. For a developer laptop, new features may matter more.',
               'Three years later the LTS is still supported (standard support is 5 years). The rolling machine is up to date but has changed a lot.',
               'That is why most company servers run LTS or enterprise releases.'],
              hid='scenario-lts')

# scenario 3: CentOS migration
mg = [label_box(14, 30, 120, 44, ['40 servers', 'CentOS 7'], 'card', 9) + cap('40 servers run CentOS 7, a free RHEL rebuild.', '', 'card', y=150, h=34),
      label_box(14, 30, 120, 44, ['40 servers', 'CentOS 7'], 'red', 9) + t(250, 50, 'End of life: 30 June 2024', 9, 'red', bold=True) + t(250, 66, 'no more security fixes', 8.6, 'ink2') + cap('CentOS 7 has ended. Auditors flag the servers.', '', 'red', y=150, h=34),
      label_box(14, 30, 120, 44, ['40 servers', 'CentOS 7'], 'red', 9) + ''.join(label_box(170, 14 + k * 30, 176, 24, [o], tone, 8.2) for k, (o, tone) in enumerate([('Rocky Linux / AlmaLinux (free)', 'green'), ('RHEL (paid support)', 'red'), ('Ubuntu LTS (re-platform)', 'acc'), ('CentOS Stream (upstream)', 'violet')])) + cap('The team weighs four options.', '', 'blue', y=150, h=34),
      label_box(14, 30, 120, 44, ['test 2 servers', 'Rocky 9'], 'green', 9) + arrow(136, 52, 166, 52, 'ink3', 1.8) + label_box(170, 30, 176, 44, ['apps tested, scripts', 'kept (same dnf/rpm)'], 'green', 8.6) + cap('They test on two servers first, then migrate in waves.', 'Same family = same commands and packages.', 'green', y=150, h=44),
      (t(180, 30, 'Lessons for you', 10.5, 'acc', bold=True) + ''.join(t(26, 56 + k * 19, s, 8.6, anchor='start') for k, s in enumerate(['• Know the EOL date of every server you manage.', '• Staying inside a family keeps migrations cheap.', '• Test on a few servers before changing all of them.'])) + cap('Lifecycle planning is a real part of a Linux job.', '', 'green', y=150, h=34))]
s3 = anim_one('Real-time scenario 3 · advanced', 'When a distribution ends: the CentOS 7 migration',
              'A real industry event: CentOS Linux reached end of life. Thousands of companies had to choose a new distribution. Simplified, but the decision steps are typical.',
              'Planning a distribution migration', 'Forty CentOS 7 servers reach end of life; the team compares Rocky Linux, AlmaLinux, RHEL, Ubuntu and CentOS Stream and migrates after testing.', mg,
              ['Many companies ran CentOS Linux 7, a free rebuild of RHEL 7.',
               'CentOS Linux 7 reached end of life on 30 June 2024 (CentOS 8 had ended in December 2021). Unsupported servers get no security fixes.',
               'Options: a free RHEL-compatible rebuild (Rocky Linux, AlmaLinux), paid RHEL, moving to Ubuntu, or CentOS Stream, which now sits just ahead of RHEL.',
               'Staying in the Red Hat family keeps dnf, rpm, SELinux and most scripts the same. They test, then migrate in small waves.',
               'Knowing your distribution’s lifecycle and family is everyday knowledge for Linux admins and DevOps engineers.'],
              hid='scenario-centos')

animation = '''<section class="part" id="animation">
  <span class="part-label"><b>5</b> See it happen</span>
  <h2>Same task on two distributions</h2>
  <p>Left: what Riya types on an Ubuntu server and on a Rocky Linux server. Right: which layers actually differ.</p>
''' + two + '''
  <p>Three real-time scenarios: choosing a distro for a job, LTS vs rolling over three years, and a real end-of-life migration.</p>
''' + s1 + s2 + s3 + '''
''' + dissect('Layer by layer: dissect <code>sudo apt install nginx</code>',
    'Installing software is where distributions differ most. Open each layer to see what really happens on an Ubuntu machine, where each part lives on disk, and run the real commands that show it (on the machine used to build this lesson).', [
    dict(key='you', name='You + sudo', sub='ask, with admin rights',
         why='Installing software changes system folders, so only an administrator may do it.',
         how='<code>sudo</code> checks you are allowed, asks your password and runs apt as root.',
         impl='<code>/usr/bin/sudo</code> and the rules in <code>/etc/sudoers</code> (Lesson 8.4).',
         used='Every software installation on a server, usually in scripts or automation tools.'),
    dict(key='apt', name='apt', sub='the planner',
         why='Programs need other programs (dependencies). Working them out by hand is painful.',
         how='apt reads the package lists, finds nginx and everything it depends on, and makes a plan: what to download, in which order.',
         impl='<code>/usr/bin/apt</code>; its sources are listed in <code>/etc/apt/sources.list.d/</code>.',
         used='All Debian-family systems. The Red Hat family uses <b>dnf</b> in the same role.',
         cmd='apt-cache depends bash | head -4'),
    dict(key='repo', name='Repository', sub='the online store',
         why='Software must come from a trusted, signed source that also delivers security updates.',
         how='<code>apt update</code> downloads the index of available packages; <code>apt install</code> downloads the .deb files and checks their signatures.',
         impl='Index files in <code>/var/lib/apt/lists/</code>; downloaded packages in <code>/var/cache/apt/archives/</code>.',
         used='Companies often run their own mirror so servers install the same, approved versions.',
         cmd='apt-cache policy bash | head -3'),
    dict(key='dpkg', name='dpkg', sub='the unpacker',
         why='Someone must actually put each file in place and remember which package owns it, for clean upgrades and removal.',
         how='dpkg unpacks the .deb archive, copies files into place, runs install scripts and records everything in its database.',
         impl='<code>/usr/bin/dpkg</code>; database in <code>/var/lib/dpkg/</code>. On RHEL the same job is done by <b>rpm</b>.',
         used='“Which package owns this file?” is a daily support question.',
         cmd='dpkg -S /usr/bin/ls'),
    dict(key='systemd', name='systemd', sub='starts the service',
         why='A web server must start at boot, restart if it crashes and keep logs.',
         how='The nginx package installs a unit file; systemd reads it and starts nginx as a background service.',
         impl='Unit files in <code>/usr/lib/systemd/system/</code>; controlled with <code>systemctl</code> (Lesson 17.2).',
         used='Every service on a modern Linux server: web servers, databases, Docker.',
         cmd='ls /usr/lib/systemd/system | grep -c service'),
    dict(key='kernel', name='Kernel', sub='the same on every distro',
         why='Whatever the distribution, programs still need CPU, memory, files and the network.',
         how='nginx runs as an ordinary process; the kernel gives it CPU time and memory, and delivers network connections to it.',
         impl='The distribution’s build of the Linux kernel in <code>/boot</code>.',
         used='This layer is why your skills carry across distributions.',
         cmd='uname -sr'),
]) + qc('When apt installs nginx on Ubuntu, which program actually unpacks and records the files?', '<code>dpkg</code>. apt plans and downloads; dpkg installs. On Rocky Linux the pair is dnf and rpm.') + '''
</section>
'''

# ---------------------------------------------------------------- 6. real world
uc = '''<section class="part" id="real-world">
  <span class="part-label"><b>6</b> Real-world use</span>
  <h2>Where each distribution shows up at work</h2>
''' + usecase(''.join(server(10 + k * 36, 16, 30, 50, None, 'acc', leds=3) for k in range(3)), '1. Cloud servers',
              'On AWS, Azure and Google Cloud, Ubuntu LTS is one of the most common server images, alongside Amazon Linux, Debian and RHEL-family images.',
              ['Choose image', '*Ubuntu / Amazon Linux / RHEL', 'Your VM']) + '\n' + usecase(
    label_box(14, 24, 92, 42, ['RHEL', '10-year support'], 'red', 8.6), '2. Banks, telecom and enterprise data centres',
    'Large regulated companies often standardise on RHEL or SUSE so that their database and middleware vendors certify and support the setup.',
    ['Vendor software', '*RHEL / SUSE', 'Support contract']) + '\n' + usecase(
    label_box(14, 24, 92, 42, ['FROM alpine', '≈ 5 MB'], 'blue', 8.6), '3. Container images',
    'Dockerfiles start with a base image: <code>FROM ubuntu</code>, <code>FROM debian:stable-slim</code> or <code>FROM alpine</code>. Smaller images download and start faster.',
    ['Dockerfile', '*base distro image', 'Container']) + '\n' + usecase(
    '<rect x="20" y="18" width="80" height="54" rx="6" class="s-board"/>' + t(60, 50, 'WSL: Ubuntu', 8.4, 'chalk', bold=True),
    '4. Developer laptops',
    'Many developers on Windows run Ubuntu inside WSL; others use Fedora or Ubuntu desktops directly. Same commands as the servers they deploy to.',
    ['Laptop', '*Ubuntu in WSL', 'Same as server']) + '\n' + usecase(
    label_box(14, 24, 92, 42, ['Kali', 'security tools'], 'violet', 8.6), '5. Security testing',
    'Ethical hackers and security teams use Kali Linux, a Debian-based distro packed with testing tools, for authorised penetration tests.',
    ['Authorised test', '*Kali tools', 'Report']) + '''
  <p class="muted">Examples are simplified and generic. They describe common patterns, not the internal systems of any particular company.</p>
''' + oneliners('Ways to identify a Linux system in one line. Each was really run on Ubuntu 24.04; other distros print their own values.', [
    dict(level='b', title='Which distro is this?', scenario='You have just logged in to an unknown server.',
         cmd="grep PRETTY_NAME /etc/os-release",
         explain='<code>grep</code> prints the line containing PRETTY_NAME: the human-readable name and version.'),
    dict(level='b', title='Which package manager do I use here?', scenario='You want to install a tool but do not know whether this machine uses apt or dnf.',
         cmd='for pm in apt dnf yum zypper pacman apk; do command -v $pm; done', expect='any',
         explain='<code>command -v</code> prints the path of each command that exists and nothing for those that do not. Here only apt exists, so this is the Debian family.'),
    dict(level='i', title='Family, ID and version for a script', scenario='Your install script must choose apt or dnf automatically.',
         cmd='(. /etc/os-release && echo "id=$ID like=$ID_LIKE version=$VERSION_ID")',
         explain='<code>/etc/os-release</code> is written as shell variables, so <code>.</code> (source) loads them. The <code>( )</code> keeps those variables from leaking into your shell.'),
    dict(level='a', title='Pick the install command automatically', scenario='One script must install <code>curl</code> on both Ubuntu and Rocky servers. (The command is printed, not run.)',
         cmd='(. /etc/os-release; case " $ID $ID_LIKE " in *" debian "*) echo "sudo apt install -y curl";; *" rhel "*|*" fedora "*) echo "sudo dnf install -y curl";; *) echo "unknown distro: $ID";; esac)',
         explain='<code>case</code> matches the ID words; the spaces around the pattern prevent partial matches. Real automation tools (Ansible) use exactly these os-release facts.'),
], extra=build_up('how many packages are installed, and which are the biggest?', 'Before cleaning up a server image, the team wants to know how many packages it has and which ones use the most space.', '', [
    ('dpkg -l | head -7', 'Look first: dpkg lists every package it knows. Installed ones start with <code>ii</code>.'),
    ("dpkg -l | grep -c '^ii'", 'Count only the installed ones.'),
    ("dpkg-query -W -f='${Installed-Size}\t${Package}\n' | sort -n | tail -3", 'Ask dpkg for size (in KB) and name of each package, sort numerically and keep the three biggest.'),
    ("echo \"Installed: $(dpkg -l | grep -c '^ii') packages; biggest: $(dpkg-query -W -f='${Installed-Size}\t${Package}\n' | sort -n | tail -1 | cut -f2)\"", 'Combine into one report line.'),
], level='a')) + which('Common distribution questions and the right command for each family.', [
    ('Find the distro and version', 'cat /etc/os-release', 'Works on every modern distro.', 'Relying on <code>lsb_release</code>, which is often missing on RHEL and containers.'),
    ('Install a package on Ubuntu/Debian', 'sudo apt install nginx', 'apt resolves dependencies from the repository.', 'Using <code>dnf</code> or <code>yum</code> here: “command not found”.'),
    ('Install a package on RHEL/Rocky/Fedora', 'sudo dnf install nginx', 'dnf is the current tool (yum is an alias on new versions).', 'Using <code>apt</code> because a tutorial said so.'),
    ('Update the package list (Debian family)', 'sudo apt update', 'Downloads the latest package lists.', 'Thinking it upgrades software; that is <code>apt upgrade</code>.'),
    ('Check SSH login records', 'sudo less /var/log/auth.log', 'Ubuntu/Debian path. On RHEL: <code>/var/log/secure</code>.', 'Searching for auth.log on RHEL.'),
    ('Know the kernel version', 'uname -r', 'Kernel, not distro.', 'Reporting the kernel version as the “Linux version” in a ticket.'),
]) + '''
''' + puzzle_answer('The package manager is <b>not part of the kernel</b>; it is part of each distribution’s own set of tools. Ubuntu ships <code>apt</code>, Rocky Linux ships <code>dnf</code>, Alpine ships <code>apk</code>. Same kernel, different toolboxes, so <code>apt</code> simply does not exist on the other two. That is exactly what “distribution” means.') + qc('Your Dockerfile switched to <code>FROM alpine</code> and a compiled Python package now breaks. What is the most likely reason?', 'Alpine uses the musl C library instead of glibc; programs built for glibc may not run or must be compiled again.') + '''
</section>
'''

cmap = concept_map(
    [('1.2', 'Kernel and shell', 'Linux is the kernel')],
    ['what a distribution adds', 'Debian, Red Hat, SUSE, Arch, Alpine families', 'apt vs dnf', 'LTS vs rolling, lifecycles', 'identify any system'],
    [('1.4', 'Linux vs other systems', 'where distros fit among OSes'), ('1.5', 'Install Ubuntu', 'pick and install one'), ('14.2', 'apt and dpkg', 'Debian family in depth'), ('14.3', 'dnf and rpm', 'Red Hat family in depth')],
    'Distribution differences come back whenever you install software (Module 14), read logs (18) or set up security (19).')
body = cmap + (story.replace('  <div class="story">', before('<a href="../02-what-is-an-operating-system-kernel-shell/">Lesson 1.2</a>: you should know that Linux is a kernel and that a full OS adds tools around it.') + '  <div class="story">', 1)
        + definition + types + steps + animation + uc)
open(os.path.join(HERE, 'body.html'), 'w', encoding='utf-8').write(body)
print('body.html', len(body) // 1024, 'KB')
