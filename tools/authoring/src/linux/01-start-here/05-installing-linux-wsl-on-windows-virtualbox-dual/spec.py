import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', '..', '..'))
from svgkit import scn
from shlesson import pc
sys.path.insert(0, os.path.join(HERE, '..', '..'))
from linuxkit import teaser
BODY = body(HERE)

META = dict(
    module='01-start-here', lesson='05-installing-linux-wsl-on-windows-virtualbox-dual', n='1.5',
    module_label='Module 1 · Start here: what is Linux?',
    title='Installing Linux: WSL on Windows, VirtualBox, dual boot and a cloud VM',
    desc='Five ways to get Linux compared: browser runner, WSL 2 on Windows, a VirtualBox virtual machine, dual boot and a cloud VM. Step-by-step WSL installation, how WSL really works, sharing files with Windows, the invisible password, cloud VM safety, and post-install checks with real Bash.',
    og_desc='Get a real Ubuntu on your laptop safely: WSL step by step, VMs, dual boot and cloud VMs compared, with animations and checks.',
    minutes=30, level='Beginner → Advanced',
    lead='Riya cannot risk wiping her only laptop. This lesson compares the five ways to get Linux, installs Ubuntu with WSL step by step, explains what WSL builds behind the screen, and covers the classic first-day surprises: the invisible password, where your files are, and the cloud server that keeps billing.',
    chips=['Story-based', '4 animations', 'Hands-on install'],
)

MAIN = '''# Post-install checks: run these on any new Linux
echo "User      : $(whoami)"
echo "Home      : $HOME"
echo "Distro    : $(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)"
echo "Kernel    : $(uname -r)"
echo "CPU cores : $(nproc)"
echo "RAM total : $(free -h | awk '/^Mem/ {print $2}')"
echo "Disk free : $(df -h ~ | awk 'NR==2 {print $4}')"
if grep -qi microsoft /proc/version; then echo "Platform  : WSL"; else echo "Platform  : not WSL"; fi
'''

RUN = dict(
    heading='Your post-install health check',
    intro='<p>Right after installing Linux (any of the five ways), run this to see who you are, which distro and kernel you got, and how much CPU, RAM and disk you have. The output below comes from the Ubuntu 24.04 cloud VM used to build this lesson; on OneCompiler and on your laptop the numbers will be different.</p>',
    code=MAIN,
    anno=[
        ('$HOME', 'Your home folder: <code>/home/&lt;you&gt;</code>. On WSL your Linux home is not your Windows user folder.'),
        ("cut -d'\"' -f2", 'Cuts the line at double quotes and keeps the text between them.'),
        ("free -h | awk '/^Mem/ {print $2}'", 'Takes the line starting with Mem and prints column 2: total RAM.'),
        ("df -h ~ | awk 'NR==2 {print $4}'", 'Line 2 of df’s output, column 4: free space on the disk that holds your home.'),
        ('grep -qi microsoft /proc/version', 'The WSL kernel’s version string mentions Microsoft; <code>-q</code> means “just tell me yes or no”.'),
    ],
    tasks=[
        dict(label='1 · Run it', hint='Press <b>Run</b>. What does OneCompiler’s machine report? Is it WSL?', code=MAIN),
        dict(label='2 · Predict first', hint='<b>Predict first:</b> is your home folder the same as your current folder when a shell starts? Then run.',
             code='echo "HOME = $HOME"\necho "PWD  = $(pwd)"\n[ "$HOME" = "$(pwd)" ] && echo same || echo different\n'),
        dict(label='3 · Spot the error', hint='<b>Spot the error:</b> a Windows path was typed into Linux. Run it, then fix it to use the Linux style (/mnt/c/…) or a Linux folder.',
             code='cd C:\\Users\\Riya\\Documents\necho "now in: $(pwd)"\n', expect='any'),
        dict(label='4 · Your turn', hint='Create the course workspace you will use from now on: <code>~/linux-course/module1</code>, and a file <code>notes.md</code> inside it.',
             code='mkdir -p ~/linux-course/module1\ncd ~/linux-course/module1\necho "# Module 1 notes" > notes.md\npwd\nls\n'),
        dict(label='5 · Challenge', hint='Print PASS if the machine has at least 2 CPU cores, otherwise FAIL (many tools need 2+ cores).',
             code='if [ "$(nproc)" -ge 2 ]; then echo "PASS: $(nproc) cores"; else echo "FAIL: only $(nproc) core"; fi\n'),
    ],
)

PCRUN = dict(
    heading='Run on your PC: the install commands',
    intro='<p>Items 1–3 are Windows PowerShell commands; their outputs are <b>typical examples written for this lesson</b> (exact wording depends on your Windows version). Items 4–5 are Linux commands whose <b>outputs were recorded on a real Ubuntu 24.04 cloud VM</b>.</p>',
    items=[
        dict(title='1 · Install WSL and Ubuntu (PowerShell as administrator)', cmd='wsl --install', file='PowerShell',
             output='Installing: Virtual Machine Platform\nVirtual Machine Platform has been installed.\nInstalling: Windows Subsystem for Linux\nWindows Subsystem for Linux has been installed.\nInstalling: Ubuntu\nUbuntu has been installed.\nThe requested operation is successful. Changes will not be effective until the system is rebooted.',
             note='Typical output. Restart when asked. If you only see WSL’s help text, it is already installed: use <code>wsl --install -d Ubuntu</code>.'),
        dict(title='2 · See your distros and their WSL version', cmd='wsl -l -v', file='PowerShell',
             output='  NAME      STATE           VERSION\n* Ubuntu    Running         2',
             note='Typical output. The <code>*</code> marks the default distro. VERSION should be 2.'),
        dict(title='3 · Other distros you can install', cmd='wsl --list --online', file='PowerShell',
             output='The following is a list of valid distributions that can be installed.\nInstall using \'wsl.exe --install <Distro>\'.\n\nNAME            FRIENDLY NAME\nUbuntu          Ubuntu\nDebian          Debian GNU/Linux\n...',
             note='Typical output, shortened. The list changes over time; pick names from your own output.'),
        dict(title='4 · Update package lists and upgrade', cmd='sudo apt update && sudo apt upgrade -y', file='Ubuntu',
             output='Hit:1 http://archive.ubuntu.com/ubuntu noble InRelease\nGet:2 http://security.ubuntu.com/ubuntu noble-security InRelease [126 kB]\n...\nReading package lists... Done\nBuilding dependency tree... Done\nCalculating upgrade... Done\n0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.',
             note='Typical output (this one could not be recorded in our build environment, which has no direct access to Ubuntu’s mirrors). Your counts will differ.'),
        dict(title='5 · What kind of machine is this?', cmd='systemd-detect-virt', file='Terminal', output=pc('systemd-detect-virt'),
             note='Recorded output. Our build machine is a container, so it says <code>docker</code>; on WSL you will see <code>wsl</code>, in VirtualBox <code>oracle</code>, on real hardware <code>none</code>.'),
    ],
)

TRACE = dict(
    heading='Setting up your course workspace, line by line',
    intro='<p>You will use this folder for the rest of the course. Watch the current folder and the files change.</p>',
    code='''course=linux-course
mkdir -p $course/module1 $course/module2
cd $course/module1
echo "Lesson 1.5: installed Ubuntu" > progress.txt
cd ..
ls
ls module1
''',
    notes={2: 'Create :: Two folders at once; <code>-p</code> also creates <code>linux-course</code> itself.',
           3: 'Move :: The current folder changes to module1.',
           5: 'Up :: <code>..</code> = the parent folder, linux-course.'},
)

WORKED_INTRO = 'Three real tasks: detecting where your Linux runs, checking whether a machine is big enough for the course tools, and estimating what a forgotten cloud VM costs.'
EXAMPLES = [
    dict(level='b', tag='Setup', title='Where is this Linux running?',
         problem='<p>Riya practises on three machines: WSL on her laptop, a VirtualBox VM and a cloud VM. She wants one script that tells her which one she is on.</p>',
         inp='(the machine)',
         approach=['WSL kernels mention “microsoft” in <code>/proc/version</code>.', 'Otherwise ask <code>systemd-detect-virt</code> (if it exists).', 'Print a friendly sentence.'],
         code='''if grep -qi microsoft /proc/version; then
  where="WSL on Windows"
elif command -v systemd-detect-virt >/dev/null; then
  where="$(systemd-detect-virt)"
else
  where="unknown"
fi
echo "This Linux runs on: $where"
''',
         notes={1: 'Check 1 :: <code>-q</code> quiet, <code>-i</code> ignore case. Exit status 0 means “found”.', 3: 'Check 2 :: Only call systemd-detect-virt if it is installed.'},
         tryit='Run it on OneCompiler. What does it report there?'),
    dict(level='i', tag='Capacity check', title='Is this machine big enough for Docker and Hadoop labs?',
         problem='<p>Later modules need at least 4 GB of RAM and 10 GB of free disk. Write a check that prints PASS or FAIL for each.</p>',
         inp='free -m and df -m output of the machine',
         approach=['Get total RAM in MB from <code>free -m</code> (line Mem, column 2).', 'Get free disk in MB from <code>df -m ~</code> (line 2, column 4).', 'Compare with <code>-ge</code> (greater or equal) and print the results.'],
         code='''ram=$(free -m | awk '/^Mem/ {print $2}')
disk=$(df -m ~ | awk 'NR==2 {print $4}')
[ "$ram" -ge 4096 ] && echo "RAM  PASS (${ram} MB)" || echo "RAM  FAIL (${ram} MB, need 4096)"
[ "$disk" -ge 10240 ] && echo "Disk PASS (${disk} MB free)" || echo "Disk FAIL (${disk} MB free, need 10240)"
''',
         notes={1: 'Measure :: <code>-m</code> gives whole megabytes, easy to compare.', 3: 'Compare :: <code>-ge</code> compares numbers; <code>&& … || …</code> chooses the message.'},
         tryit='Change the limits to 16384 MB RAM and see the FAIL message.'),
    dict(level='a', tag='Business problem', title='What does a forgotten cloud VM cost?',
         problem='<p>A small cloud VM costs about ₹2.50 per hour (example rate). Riya used one for 3 hours of practice a day for 20 days, but once forgot it running for a whole 30-day month. Compare the two bills and the waste.</p>',
         inp='rate = 2.50 ₹/hour · planned = 3 h × 20 days · forgotten = 24 h × 30 days',
         approach=['bash only does whole-number maths, so use <code>awk</code> for money with decimals.', 'Compute both totals and the difference.', 'Print them in rupees with two decimals.'],
         code='''rate=2.50
awk -v r="$rate" 'BEGIN {
  planned = r * 3 * 20
  forgot  = r * 24 * 30
  printf "Planned use : Rs %.2f\\n", planned
  printf "Left running: Rs %.2f\\n", forgot
  printf "Wasted      : Rs %.2f\\n", forgot - planned
}'
''',
         notes={2: 'awk :: <code>-v r=…</code> passes the shell variable into awk; BEGIN runs without any input file.'},
         tryit='Change the rate to your provider’s real price. (Rates here are examples; check your cloud’s pricing page and set a budget alert.)'),
]

QUIZ = mix([
    dict(q='Which way of getting Linux carries real risk to your existing files?', options=['WSL', 'A VirtualBox VM', 'Dual boot', 'The browser runner'], answer=2,
         why='Dual boot needs disk partitioning; a mistake there can erase data. The other options never touch your partitions.'),
    dict(q='Which command installs WSL with Ubuntu on Windows 11?', options=['apt install wsl', 'wsl --install (in an administrator PowerShell)', 'sudo wsl', 'install-linux.exe'], answer=1,
         why='wsl --install, run as administrator, enables the features and installs Ubuntu on WSL 2 by default. Then restart.'),
    dict(q='While typing your password for sudo, nothing appears. What does it mean?', options=['The keyboard is broken', 'Linux hides password input; keep typing and press Enter', 'You must type it in Windows', 'sudo is not installed'], answer=1,
         why='Terminals do not echo passwords at all, not even stars.'),
    dict(q='In WSL, where is your Windows C: drive?', options=['/c', '/mnt/c', '/windows', 'C:\\ inside Linux'], answer=1,
         why='Windows drives are mounted under /mnt. Linux files are reachable from Windows at \\\\wsl.localhost\\<distro>.'),
    dict(q='Why keep your coding projects in ~ rather than /mnt/c when using WSL?', options=['/mnt/c is read-only', 'Linux tools are much faster on the Linux file system', 'Windows deletes files in /mnt/c', 'It is required by law'], answer=1,
         why='Accessing /mnt/c from Linux crosses the VM boundary and is slower, especially for many small files.'),
    dict(q='WSL 2 is best described as…', options=['A Linux emulator written in JavaScript', 'A real Linux kernel running in a lightweight VM managed by Windows', 'A Linux theme for Windows', 'Dual boot without restart'], answer=1,
         why='WSL 2 uses a genuine Linux kernel (built by Microsoft) inside a Hyper-V based utility VM.'),
    dict(q='You finished practising on a cloud VM. What should you do?', options=['Leave it running for next time', 'Stop or delete it so it stops billing', 'Unplug your laptop', 'Change the root password'], answer=1,
         why='Cloud VMs bill while running. Stop or delete them and set a budget alert.'),
])

REVISION = [
    'Five ways: <b>browser runner</b>, <b>WSL 2</b>, <b>VM</b> (VirtualBox/UTM), <b>dual boot</b>, <b>cloud VM</b>. Only dual boot risks your partitions.',
    'WSL: <code>wsl --install</code> in admin PowerShell → restart → create user → <code>sudo apt update &amp;&amp; sudo apt upgrade -y</code>.',
    'Requirements: Windows 10 2004 (build 19041)+ or Windows 11. Default: Ubuntu on WSL 2.',
    'WSL 2 = real Linux kernel in a lightweight VM. Check with <code>wsl -l -v</code> (VERSION 2).',
    'Files: Windows drives at <code>/mnt/c</code>; Linux files at <code>\\\\wsl.localhost\\Ubuntu</code>. Keep projects in <code>~</code>.',
    'Passwords are not echoed. sudo asks for <b>your</b> password.',
    'VM = hypervisor + guest OS; snapshots make experiments safe. Verify ISOs with <code>sha256sum</code>.',
    'Cloud VM: SSH key, port 22 only from your IP, budget alert, stop when idle.',
]

FAQ = [
    ('What are the ways to run Linux on a Windows laptop?', 'WSL 2 (Linux inside Windows), a virtual machine with VirtualBox or VMware, dual boot (separate partition), a cloud VM reached over SSH, or a live USB. Browser-based terminals also work for basic practice.'),
    ('What is WSL? How is WSL 2 different from WSL 1?', 'WSL is a Windows feature for running Linux distributions. WSL 1 translated Linux system calls into Windows calls. WSL 2 runs a real Linux kernel inside a lightweight VM, giving full system-call compatibility and better performance for Linux file systems.'),
    ('What is a hypervisor? Type 1 vs Type 2?', 'Software that creates and runs virtual machines. Type 1 (bare-metal) runs directly on hardware: VMware ESXi, Hyper-V, KVM. Type 2 (hosted) runs as an app on a normal OS: VirtualBox, VMware Workstation.'),
    ('Dual boot or VM, which is better?', 'A VM is safer and lets you run both systems at once with snapshots, at some speed cost. Dual boot gives full hardware speed but only one OS at a time and needs careful partitioning.'),
    ('Why does Linux not show anything when I type my password?', 'For security, terminals do not echo password characters at all, so onlookers cannot even see the length. Type it fully and press Enter.'),
    ('How do you verify a downloaded ISO?', 'Compute its checksum with <code>sha256sum file.iso</code> and compare it with the SHA256SUMS published on the distribution’s official site (ideally also checking the GPG signature of that file).'),
]

PRACTICE_INTRO = 'Small checks you will run on every new Linux machine. Expected outputs are from real runs on the Ubuntu 24.04 build VM.'
PROBLEMS = [
    dict(level='easy', title='Greet the new user', stmt='Print “Welcome, &lt;user&gt;! Your home is &lt;home&gt;”.', inp='(the machine)',
         code='echo "Welcome, $(whoami)! Your home is $HOME"\n', explain='<code>$HOME</code> is set by the system at login; <code>whoami</code> asks the system for your user name.'),
    dict(level='easy', title='Make your course folders', stmt='Create <code>linux-course</code> with sub-folders <code>module1</code> to <code>module3</code> in one command and list them.', inp='(nothing)',
         code='mkdir -p linux-course/module{1..3}\nls linux-course\n', explain='<code>{1..3}</code> expands to 1 2 3, so three folders are created in one mkdir.'),
    dict(level='easy', title='Distro version only', stmt='Print only the VERSION_ID of the distribution, without quotes.', inp='/etc/os-release',
         code="grep '^VERSION_ID' /etc/os-release | cut -d'\"' -f2\n", explain='The value sits between double quotes; cut with <code>-d\'"\'</code> picks it out.'),
    dict(level='medium', title='RAM in GB, rounded', stmt='Print total RAM in whole GB, using <code>free -g</code>.', inp='free -g',
         code="echo \"RAM: $(free -g | awk '/^Mem/ {print $2}') GB\"\n", explain='<code>-g</code> shows gibibytes, rounded down. A 7.8 GiB machine shows 7.'),
    dict(level='medium', title='Disk usage percentage', stmt='Print how full the disk holding your home is, e.g. “Disk is 29% full”.', inp='df -h ~',
         code="echo \"Disk is $(df -h ~ | awk 'NR==2 {print $5}') full\"\n", explain='Column 5 of df’s second line is Use%.'),
    dict(level='medium', title='Translate a Windows path', stmt='Turn <code>C:\\Users\\Riya\\Documents</code> into the WSL path <code>/mnt/c/Users/Riya/Documents</code>.', inp='C:\\Users\\Riya\\Documents',
         code="win='C:\\Users\\Riya\\Documents'\necho \"$win\" | sed -e 's#\\\\#/#g' -e 's#^\\([A-Za-z]\\):#/mnt/\\L\\1#'\n",
         explain='First every backslash becomes a slash; then the drive letter becomes <code>/mnt/</code> plus the letter in lower case (<code>\\L</code> is a GNU sed feature). WSL also ships a tool for this: <code>wslpath</code>.'),
    dict(level='business', title='Lab readiness report', stmt='For a training lab, print one line: cores, RAM in MB, free disk in GB, and READY if cores ≥ 2 and RAM ≥ 4096 MB, else NOT READY.', inp='(the machine)',
         code="c=$(nproc); r=$(free -m | awk '/^Mem/ {print $2}'); d=$(df -BG ~ | awk 'NR==2 {print $4}')\nif [ $c -ge 2 ] && [ $r -ge 4096 ]; then s=READY; else s=\"NOT READY\"; fi\necho \"cores=$c ram=${r}MB disk_free=$d -> $s\"\n",
         explain='<code>df -BG</code> reports sizes in whole gigabytes. Two tests joined with <code>&amp;&amp;</code> must both pass.'),
    dict(level='business', title='Cloud practice budget', stmt='With an example rate of ₹2.50 per hour and a budget of ₹500, how many hours of VM practice can a student afford? Print whole hours.', inp='rate=2.50, budget=500',
         code="awk 'BEGIN { rate=2.50; budget=500; printf \"Affordable hours: %d\\n\", budget/rate }'\n", explain='awk handles decimals; <code>%d</code> prints the whole number part. Rates are examples only.'),
]

SCN_INTRO = 'Questions interviewers ask to see whether you can set up and use Linux environments sensibly.'
SCENARIOS = (
    scn('Any company · onboarding', 'Fresher', '“Set up your laptop for our Linux project”',
        'Your new company gives you a Windows laptop. The project runs on Ubuntu servers. How will you set up your environment?',
        'do you choose a safe, standard setup and know the basics?',
        '''<ul>
          <li>Install WSL 2 with Ubuntu (matching the server’s version if possible), update it, and install the project’s tools inside WSL.</li>
          <li>Keep the code in the Linux home (<code>~/projects</code>), use VS Code’s WSL integration, and configure Git with LF line endings.</li>
          <li>If I need a full desktop or risky experiments, add a VirtualBox VM with snapshots. Follow the company’s security policy for any of this.</li>
        </ul>''', 'proposing to wipe the company laptop and dual boot.') +
    scn('Product company · concepts', 'Fresher', '“VM or container or WSL?”',
        'The interviewer asks you to explain the difference between a virtual machine, a container and WSL 2.',
        'do you understand isolation levels?',
        '''<ul>
          <li><b>VM</b>: a full emulated computer with its own kernel, managed by a hypervisor. Strong isolation, heavier.</li>
          <li><b>Container</b>: isolated processes sharing the host’s Linux kernel (namespaces + cgroups). Very light and fast to start.</li>
          <li><b>WSL 2</b>: Microsoft’s lightweight VM running a real Linux kernel, tightly integrated with Windows; Docker Desktop on Windows itself uses it.</li>
        </ul>''', 'saying a container is a small VM.') +
    scn('Cloud team · operations', 'Junior', 'An unexpected cloud bill',
        'Your manager notices a training account spent much more than planned last month. Three VMs created for a workshop were never stopped.',
        'do you handle cost and hygiene responsibly?',
        '''<ol>
          <li>Stop or delete the idle VMs immediately (after checking nobody needs data on them; take snapshots if unsure).</li>
          <li>Set budget alerts and tags such as owner and expiry date on every resource.</li>
          <li>For workshops, use a script to create and destroy VMs together, or schedules that stop them at night.</li>
        </ol>''', 'only apologising, without preventing it next time.') +
    scn('Support · troubleshooting', 'Fresher', '“WSL is very slow”',
        'A colleague says <code>npm install</code> or <code>git status</code> in WSL takes minutes. You notice the project is in <code>/mnt/c/Users/…</code>.',
        'do you know the WSL file-system boundary?',
        '''<ul>
          <li>Linux tools accessing files on the Windows drive go through a translation layer, which is slow for many small files.</li>
          <li>Move the project into the Linux home (<code>~/projects</code>), and open it from VS Code with the WSL extension or <code>code .</code>.</li>
          <li>Check <code>wsl -l -v</code> shows VERSION 2.</li>
        </ul>''', '“WSL is just slow, use Windows instead.”')
) + teaser('1.6', 'Riya starts <code>ping google.com</code> and it never stops. Closing the window feels wrong. Which two keys stop it, and what do they really send to the program?')

from linuxkit import mindmap
MINDMAP = mindmap('Getting Linux', [
    ('Five ways', 'acc', ['browser runner', 'WSL 2, VirtualBox VM', 'dual boot, cloud VM']),
    ('WSL steps', 'green', ['wsl --install (admin)', 'restart, create user', 'apt update && upgrade']),
    ('How WSL 2 works', 'blue', ['lightweight Hyper-V VM', 'Microsoft Linux kernel', 'files in ext4.vhdx']),
    ('VirtualBox', 'violet', ['ISO + checksum', '4 GB RAM, 25 GB disk', 'Guest Additions, snapshots']),
    ('Files', 'amber', ['/mnt/c from Linux', '\\\\wsl.localhost from Windows', 'projects in ~']),
    ('Safety', 'red', ['dual boot: back up first', 'password not echoed', 'stop cloud VMs']),
])
